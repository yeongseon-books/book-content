---
title: The gRPC Event Stream — What Do the Host and Worker Actually Exchange?
series: azure-functions-deep-dive
episode: 3
language: en
status: ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Azure Functions
- Serverless
- Distributed Systems
- gRPC
last_reviewed: '2026-04-29'
---

# The gRPC Event Stream — What Do the Host and Worker Actually Exchange?

> Azure Functions Deep Dive series (3/6)

<!-- ebook-only:start -->
## Where this chapter fits

This is chapter 3 of 6 in the series.
The previous chapter covered **Worker Processes — How One Host Hosts Many Languages**.
After this chapter, the next one moves on to **Dispatcher and Invocation — How a Function Call Reaches the Worker**.
<!-- ebook-only:end -->

## Source Version

All code citations in this post are based on [`Azure/azure-functions-host @ 5e59423`](https://github.com/Azure/azure-functions-host/tree/5e59423ba45491041d18224c3e72c168a4a5b7f7).

In Part 2, we watched the worker process get spawned. When `WorkerProcess.StartProcessAsync()` ultimately calls `Process.Start()`, an external process like Node, Python, or Java starts running. But on its own, that does nothing. **The host and the worker need a channel to talk over.**

That channel is a single **bidirectional gRPC stream**. In this post, we'll walk through what the stream looks like, what messages travel across it, and how the host receives and routes them — all in code.

> All code citations in this post are based on these two repositories:
> - Host: [`Azure/azure-functions-host` @ `5e59423`](https://github.com/Azure/azure-functions-host/tree/5e59423ba45491041d18224c3e72c168a4a5b7f7)
> - Protocol: [`Azure/azure-functions-language-worker-protobuf`](https://github.com/Azure/azure-functions-language-worker-protobuf) — the protocol lives in a separate repo.

---

## The big picture — one single stream

Let's start with the punchline. Host-worker communication in Azure Functions is **one gRPC service, one RPC**.

```protobuf
service FunctionRpc {
  rpc EventStream (stream StreamingMessage) returns (stream StreamingMessage) {}
}
```

One line. A single `EventStream`. Streaming on both sides. In other words, the host and worker **exchange messages freely over the same channel**. This is not a request-response RPC.

That single line carries a lot of weight. **Everything that can go inside `StreamingMessage`** is essentially the entire Functions protocol.

---

## `StreamingMessage` — the all-purpose message multiplexed via `oneof`

[`StreamingMessage` in `FunctionRpc.proto`](https://github.com/Azure/azure-functions-language-worker-protobuf/blob/3757ce8/src/proto/FunctionRpc.proto) looks like this:

```protobuf
message StreamingMessage {
  // Used to identify message between host and worker
  string request_id = 1;

  // Payload of the message
  oneof content {
    StartStream start_stream = 20;

    WorkerInitRequest worker_init_request = 17;
    WorkerInitResponse worker_init_response = 16;

    WorkerTerminate worker_terminate = 14;

    WorkerStatusRequest worker_status_request = 12;
    WorkerStatusResponse worker_status_response = 13;

    FileChangeEventRequest file_change_event_request = 6;
    WorkerActionResponse worker_action_response = 7;

    FunctionLoadRequest function_load_request = 8;
    FunctionLoadResponse function_load_response = 9;

    InvocationRequest invocation_request = 4;
    InvocationResponse invocation_response = 5;
    InvocationCancel invocation_cancel = 21;

    RpcLog rpc_log = 2;

    FunctionEnvironmentReloadRequest function_environment_reload_request = 25;
    FunctionEnvironmentReloadResponse function_environment_reload_response = 26;

    CloseSharedMemoryResourcesRequest close_shared_memory_resources_request = 27;
    CloseSharedMemoryResourcesResponse close_shared_memory_resources_response = 28;

    FunctionsMetadataRequest functions_metadata_request = 29;
    FunctionMetadataResponse function_metadata_response = 30;

    FunctionLoadRequestCollection function_load_request_collection = 31;
    FunctionLoadResponseCollection function_load_response_collection = 32;

    WorkerWarmupRequest worker_warmup_request = 33;
    WorkerWarmupResponse worker_warmup_response = 34;
  }
}
```

Two things matter here:

1. `request_id` — the ID the host and worker use to pair messages. It's critical for correlating asynchronous responses.
2. `oneof content` — only one payload is set at a time. In other words, **dozens of message types are multiplexed** over the same channel.

If we group them, the messages fall into roughly five categories:

| Group | Messages | Direction |
|---|---|---|
| **Lifecycle** | StartStream, WorkerInitRequest/Response, WorkerTerminate | `StartStream` is worker → host, `WorkerInitRequest` is host → worker, `WorkerInitResponse` is worker → host, `WorkerTerminate` is host → worker |
| **Health checks** | WorkerStatusRequest/Response | Host → Worker |
| **Function loading** | FunctionLoadRequest/Response, FunctionsMetadataRequest, FunctionMetadataResponse | Host ↔ Worker |
| **Invocation** | InvocationRequest/Response, InvocationCancel | Host → Worker (response goes the other way) |
| **Operations** | RpcLog, FileChangeEventRequest, FunctionEnvironmentReloadRequest/Response, WorkerWarmupRequest/Response | Mixed |

This table is the entire Functions protocol in one view.

---

## The handshake — the moment a worker first speaks to the host

All of these messages matter, but if you understand **the very first handshake**, the rest follows naturally.

### Step 1 — the worker sends `StartStream`

Once the worker process finishes booting, it introduces itself to the host first.

```protobuf
message StartStream {
  // id of the worker
  string worker_id = 2;
}
```

The worker sends `StartStream` with its own `worker_id` to the host. This ID is the same one the host passed to the worker as an environment variable or command-line argument when it built the `RpcWorkerConfig` we saw in Part 2. In other words, **the worker is echoing back the ID the host previously handed it**. With that, the host confirms: "the gRPC client that just connected is indeed the worker I spawned."

### Step 2 — the host sends `WorkerInitRequest`

Once the worker's identity is confirmed, the host "initializes" the worker.

```protobuf
message WorkerInitRequest {
  // version of the host sending init request
  string host_version = 1;

  // A map of host supported features/capabilities
  map<string, string> capabilities = 2;

  // inform worker of supported categories and their levels
  map<string, RpcLog.Level> log_categories = 3;

  // Full path of worker.config.json location
  string worker_directory = 4;

  // base directory for function app
  string function_app_directory = 5;
}
```

The most important field here is `capabilities`. **The host advertises the features it supports** (e.g. shared memory data transfer, RPC HTTP body, raw HTTP body bytes, etc.). The worker reads it and learns: "here's what I can do with this particular host."

### Step 3 — the worker replies with `WorkerInitResponse`

```protobuf
message WorkerInitResponse {
  // A map of worker supported features/capabilities
  map<string, string> capabilities = 2;

  // Status of the response
  StatusResult result = 3;

  // Worker metadata captured for telemetry purposes
  WorkerMetadata worker_metadata = 4;
}
```

This time, **the worker advertises its own capabilities**. The host updates its capability state through `WorkerChannel.ApplyCapabilities()`, whose default strategy is merge. So the runtime behavior is not “calculate one static common set once,” but rather **update the host-side capability set and derive features like shared memory transfer or HTTP proxying from that merged view**. `WorkerMetadata` also rides along, carrying telemetry such as the runtime type, version, and bitness.

### Step 4 — the host loads functions via `FunctionLoadRequest`

Once the handshake is done, the host starts telling the worker about each function.

```protobuf
message FunctionLoadRequest {
  string function_id = 1;
  RpcFunctionMetadata metadata = 2;
  bool managed_dependency_enabled = 3;
}
```

The host sends one of these per function, or batches them in a single `FunctionLoadRequestCollection`. The worker replies to each with a `FunctionLoadResponse` reporting success or failure.

### All on one screen

![Common worker protocol lifecycle flow](../../../assets/azure-functions-deep-dive/03/03-01-all-on-one-screen.en.png)
This sequence is **the life of every worker**. The Node worker, the Python worker, the Java worker — all the same. The implementation details on the worker side differ per language, but **the protocol is uniform**.

---

## The host side — `FunctionRpcService` accepts the EventStream

The worker is the client; the host is the server. On the host side, the `EventStream` RPC is implemented in [`src/WebJobs.Script.Grpc/Server/FunctionRpcService.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Server/FunctionRpcService.cs).

As the name suggests, it inherits from `FunctionRpc.FunctionRpcBase` (the base class auto-generated by `protoc` from `service FunctionRpc`) and overrides the `EventStream` method.

The `Server/` directory also contains the following files:

- [`AspNetCoreGrpcServer.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Server/AspNetCoreGrpcServer.cs) — the entry point that brings up Kestrel + ASP.NET Core gRPC as a server inside the host
- [`AspNetCoreGrpcHostBuilder.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Server/AspNetCoreGrpcHostBuilder.cs) — builds the IHost for the gRPC server
- [`Startup.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Server/Startup.cs) — gRPC endpoint registration via `endpoints.MapGrpcService<FunctionRpc.FunctionRpcBase>()`

In other words, **an ASP.NET Core gRPC server is running inside the Functions host**, and worker processes connect to it as gRPC clients to call `EventStream`. It's localhost gRPC.

The address (endpoint and port) the server listens on is decided by the host and communicated to the worker via the environment variables/command-line arguments we saw in Part 2. That's why, if you read the worker code in any language, the very first entry point follows the same pattern: "create a gRPC client targeting the address the host gave us."

---

## `GrpcWorkerChannel` — the host's handle on a worker

Messages received by the server eventually need someone to **read and route** them. That "someone" on the host side is the worker handle object: **`GrpcWorkerChannel`**.

[`src/WebJobs.Script.Grpc/Channel/GrpcWorkerChannel.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Channel/GrpcWorkerChannel.cs) is the object the host holds **one-per-worker-process**. Looking at the surrounding files in the same directory makes its role obvious:

| File | Role |
|---|---|
| `GrpcWorkerChannel.cs` | The handle that represents one worker. The concrete flow is split between `StartWorkerProcessAsync()`, `SendWorkerInitRequest`, `SendInvocationRequest`, and `StopWorkerProcess()` across this class and the base `WorkerChannel`. |
| [`WorkerChannel.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Channel/WorkerChannel.cs) | The shared base layered on top of gRPC |
| [`GrpcWorkerChannelFactory.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Channel/GrpcWorkerChannelFactory.cs) | The factory that produces `GrpcWorkerChannel` instances |
| [`GrpcCapabilities.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Channel/GrpcCapabilities.cs) | Constants for capability keys |
| [`OrderedInvocationMessageDispatcher.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Channel/OrderedInvocationMessageDispatcher.cs) | Preserves ordering for messages that belong to the same `invocation_id` |

For the purpose of this post, the important point is simply that **this object handles the EventStream in both directions**.

---

## The channel layout — closer to per-worker `Channel<T>` pairs than a generic event bus

This part is easier to reason about if you stay close to the code. The main invocation path is not a broad pub-sub event bus. It is **a pair of inbound/outbound `Channel<T>` instances created per worker**.

`GrpcEventExtensions.AddGrpcChannels(workerId)` allocates two channels for each worker ID:

- inbound: `InboundGrpcEvent` flowing from worker to host
- outbound: `OutboundGrpcEvent` flowing from host to worker

`FunctionRpcService.EventStream()` confirms the worker identity from `StartStream`, then calls `TryGetGrpcChannels(workerId, out inbound, out outbound)`. After that, the server-side loop is mechanical:

- read `StreamingMessage` from gRPC and write it to the inbound channel
- read outbound messages from the outbound channel and write them to the gRPC response stream

That makes `FunctionRpcService` the pump between the real gRPC stream and the host-side per-worker queues.

![Per-worker channel pairs and gRPC pump](../../../assets/azure-functions-deep-dive/03/03-02-the-channel-layout-closer-to-per-worker.en.png)
`IScriptEventManager` still exists here, but mainly as keyed storage for those channels. `InboundGrpcEvent` and `OutboundGrpcEvent` are real wrapper types, and other components can observe them around the edges. But for function invocation traffic, the mental model that matches the source is **per-worker queues plus a gRPC pump**, not “everything goes through one generic in-process event bus.”

---

## So what path does a single invocation take?

If we boil everything down to one sentence:

> Inside the host, `FunctionRpcService` reads `StreamingMessage` frames from a worker and writes them into that worker's inbound channel, then drains the outbound channel back onto the gRPC stream. `GrpcWorkerChannel` sits on top of that channel pair and matches requests with responses for its worker.

That's the communication infrastructure. Once you keep the per-worker channel pair and the gRPC pump in mind, the rest of the host's invocation machinery stops looking like a generic event bus and starts looking like a concrete request/response transport.

---

## What this post establishes

At this point, the protocol boundary is explicit: one worker connects over one bidirectional gRPC stream, the host maps that worker to a pair of in-memory channels, and `GrpcWorkerChannel` lives on top as the worker-specific control object.

---

## Where this fits in the series

This is part 3 of the Azure Functions Deep Dive series. Part 2 stopped at process startup; this part covers the wire protocol that takes over once the worker connects, making the host-side transport boundary concrete.

---

## Call Path Summary

- Worker bootstrap → `StartStream(worker_id)` → `FunctionRpcService.EventStream(...)` → `TryGetGrpcChannels(workerId, out inbound, out outbound)`
- `WorkerChannel.SendWorkerInitRequest()` → `WorkerInitResponse` → `ApplyCapabilities(...)`
- `WorkerChannel.SendFunctionLoadRequest()` / `SendFunctionLoadRequestCollection()` → worker load ack → per-worker invocation path becomes ready

---

<!-- blog-only:start -->
Next: [Dispatcher and Invocation — How a Function Call Reaches the Worker](./04-dispatcher-and-invocation.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## In this series

- [Host Bootstrap — Following `WebJobsScriptHostService`](./01-host-bootstrap.md)
- [Worker Processes — How One Host Hosts Many Languages](./02-worker-process.md)
- **The gRPC Event Stream — What Do the Host and Worker Actually Exchange? (current)**
- Dispatcher and Invocation — How a Function Call Reaches the Worker (upcoming)
- Scaling Internals — Scale Controller, ScaleMonitor, and What Differs Across Plans (upcoming)
- Cold Start and Placeholder Mode — What Happens When a New Instance Is Born (upcoming)

<!-- toc:end -->

---

## References

**Protocol (separate repo)**
- [FunctionRpc.proto](https://github.com/Azure/azure-functions-language-worker-protobuf/blob/3757ce8/src/proto/FunctionRpc.proto) — `service FunctionRpc`, `StreamingMessage`, all message types

**Host code (commit `5e59423`)**
- [`Server/FunctionRpcService.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Server/FunctionRpcService.cs)
- [`Server/AspNetCoreGrpcServer.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Server/AspNetCoreGrpcServer.cs)
- [`Channel/GrpcWorkerChannel.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Channel/GrpcWorkerChannel.cs)
- [`Channel/GrpcCapabilities.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Channel/GrpcCapabilities.cs)
- [`Eventing/GrpcEventExtensions.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Eventing/GrpcEventExtensions.cs)
- [`Channel/OrderedInvocationMessageDispatcher.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Channel/OrderedInvocationMessageDispatcher.cs)

**Related introductory series**
- [Host and Worker — who actually runs your functions (101 series, Part 3)](../../azure-functions-101/en/03-host-and-worker.md)

Tags: Azure Functions, Serverless, Distributed Systems, gRPC
