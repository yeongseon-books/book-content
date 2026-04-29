---
title: Worker Processes — How One Host Hosts Many Languages
series: azure-functions-deep-dive
episode: 2
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

# Worker Processes — How One Host Hosts Many Languages

> Azure Functions Deep Dive series (2/6)

## Source Version

All code citations in this post are based on [`Azure/azure-functions-host @ 5e59423`](https://github.com/Azure/azure-functions-host/tree/5e59423ba45491041d18224c3e72c168a4a5b7f7).

At the end of part 1 I left a question hanging: *what exactly happens inside the “Worker channel preparation” box of `InitializeAsync`?* That is the topic for this installment. How does the Functions Host — written in .NET — launch and connect to Worker processes for Node.js, Python, Java, and PowerShell? We follow the trail **all the way down to the moment the OS-level `Process.Start` is called**.

The reference commit is the same as in part 1: `5e59423`.

---

## Starting point — `worker.config.json`

The answer is straightforward. The Host does not hard-code how to launch each language runtime. It reads **a `worker.config.json` file that ships with each language worker package** and follows that description. Adding a new language is therefore closer to adding a worker package than patching the Host.

The Node.js worker’s configuration, for example, looks like this:

```json
{
  "description": {
    "language": "node",
    "extensions": [".js", ".mjs", ".cjs"],
    "defaultExecutablePath": "node",
    "defaultWorkerPath": "dist/src/nodejsWorker.js"
  }
}
```

> Source: [Node.js worker repo `worker.config.json`](https://github.com/Azure/azure-functions-nodejs-worker/blob/v3.x/worker.config.json)

The Java worker’s configuration follows the same shape, in its own file:

> Source: [Java worker repo `worker.config.json`](https://github.com/Azure/azure-functions-java-worker/blob/dev/worker.config.json)

These files tell the Host three things:

- **Which executable to launch** (`node`, `java -jar ...`, `python`, etc.)
- **Which entry-point script to hand it** (`nodejsWorker.js`, `azure-functions-java-worker.jar`, etc.)
- **Which file extensions it owns** (`.js`, `.py`, `.java`, ...)

---

## One level up — `WorkerConfigurationResolver`

When the Host boots, the object at the center of worker-config aggregation is `WorkerConfigurationResolver`. It does not scan everything by itself. Instead, multiple providers populate a `Dictionary<string, RpcWorkerConfig>`, and `WorkerConfigurationResolver.GetWorkerConfigs()` aggregates their results in priority order.

At `5e59423`, those providers are `DefaultWorkerConfigurationProvider`, `DynamicWorkerConfigurationProvider`, and `ExplicitWorkerConfigurationProvider`, all sharing `WorkerConfigurationProviderBase`. The default provider scans the host's built-in `workers/` directory, the dynamic provider resolves versioned workers from probing paths, and the explicit provider applies app-setting overrides for a specific worker directory.

![One level up — the worker configuration resolver/provider split](../../../assets/azure-functions-deep-dive/02/02-01-one-level-up-workerconfigfactory.en.png)
That is why language workers plug in cleanly. **The Host does not carry language-specific launch logic for each runtime; it reads a config description and builds from there.**

---

## Launching the Worker process — `RpcWorkerProcess`

Once the configs are gathered, the next step is to launch an actual OS process. The class responsible is `RpcWorkerProcess`. But `RpcWorkerProcess` does not directly instantiate the child process on its own. Its `CreateWorkerProcess()` method builds a `RpcWorkerContext` and delegates to the injected `_processFactory.CreateWorkerProcess(workerContext)`.

> Source: [`RpcWorkerProcess.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script.Grpc/Rpc/RpcWorkerProcess.cs)

The actual start happens in `WorkerProcess.StartProcessAsync()`. Three things happen there:

1. Spin up an OS process via `System.Diagnostics.Process`
2. **Intercept stdout/stderr and wire them into the Host’s logging pipeline**
3. Register a callback for when the process dies (the `Exited` event)

> Source: [`WorkerProcess.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script.Grpc/ProcessManagement/WorkerProcess.cs)

That stdout/stderr wiring matters operationally. **Every line a worker writes to standard output flows through the Host’s logging system into Application Insights.** A large fraction of the rows you see in the `traces` table — the one we toured in part 7 of the introductory series — are, in fact, lines the worker wrote to stdout. That is the answer to “how does a single `console.log` end up in cloud logs.”

---

## Worker lifecycle within a single instance

A running OS process does not mean the Worker is “ready.” Process boot and the gRPC handshake are separate stages. The sequence below is the full path a single Worker takes to reach the “ready” state inside one instance.

![Worker lifecycle within a single instance](../../../assets/azure-functions-deep-dive/02/02-02-worker-lifecycle-within-a-single-instanc.en.png)
The `GrpcWorkerChannel` that appears here is “the Host-side handle that corresponds to one worker process.” When the worker dies, the channel is torn down with it, and the Host spins up a new worker along with a new channel.

> Source: [`GrpcWorkerChannel.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script.Grpc/Channel/GrpcWorkerChannel.cs)

---

## `FUNCTIONS_WORKER_PROCESS_COUNT` — multiple workers per instance

The default is 1. That is, a single Function App instance hosts a single Worker. But if you set the environment variable `FUNCTIONS_WORKER_PROCESS_COUNT` to N, that same instance will run N worker processes side by side.

This is meaningful in two cases:

- **Single-threaded, event-loop languages like Node.js / Python** — when a single worker is blocked on CPU work, no other invocation can squeeze in. Running multiple workers parallelizes execution at the OS multi-process level.
- **Multi-threaded languages like Java / .NET** — there is little reason to need extra workers, but you can still use the option when you want memory isolation or separate GCs.

Two different knobs get conflated here, and the host code keeps them separate.

- **`FUNCTIONS_WORKER_PROCESS_COUNT` / `WorkerProcessCountOptions`** sets the **static number of worker processes per instance**.
- **`WorkerConcurrencyOptions` / `WorkerConcurrencyManager`** governs **dynamic worker concurrency**: the runtime watches latency history and may add more workers at runtime.

So `FUNCTIONS_WORKER_PROCESS_COUNT=4` means “start four workers for this instance.” `WorkerConcurrencyOptions` means “watch live worker latency and decide whether to add another one.” Dynamic concurrency is limited to a subset of runtimes such as Node.js, Python, and PowerShell, and it is skipped when `FUNCTIONS_WORKER_PROCESS_COUNT` is explicitly set.

![`FUNCTIONS_WORKER_PROCESS_COUNT` — multiple workers per instance](../../../assets/azure-functions-deep-dive/02/02-03-functions-worker-process-count-multiple.en.png)
---

## What happens when a worker dies

A worker process runs arbitrary user code. Which means it can always die: infinite loops, runaway memory, unhandled exceptions, the occasional unexplained OOM. The Host’s recovery strategy looks like this:

1. Detect the death via `WorkerProcess`’s `Exited` event
2. Tear down the corresponding worker channel (`GrpcWorkerChannel.Dispose`)
3. Launch a fresh worker process
4. Mark any in-flight `InvocationRequest`s as failed

Operationally, this isolation is the reason “a function may fail occasionally while the Host itself stays perfectly healthy.” The Host is designed around detecting and recovering from the death of **a child process** — not its own.

![What happens when a worker dies](../../../assets/azure-functions-deep-dive/02/02-04-what-happens-when-a-worker-dies.en.png)
---

## Wrapping up part 2

If I had to compress this part into a single paragraph, it would be this:

> Each language's worker package drops a `worker.config.json` on disk. At boot, the Host gathers those configs through `WorkerConfigurationResolver` and its providers into a `RpcWorkerConfig` catalogue. When it is time to launch a worker, `RpcWorkerProcess.CreateWorkerProcess()` builds a `RpcWorkerContext` and delegates to `_processFactory.CreateWorkerProcess(...)`, then `WorkerProcess.StartProcessAsync()` makes the final OS-level `Process.Start()` call. stdout/stderr are wired into the Host's logging pipeline.

By this point the worker is **running, connected to the Host, and ready to receive function metadata**. The useful mental model is that worker startup is not a monolith. Configuration discovery, OS process creation, stdout/stderr wiring, and channel readiness are separate stages with different failure modes.

---

## Where this fits in the series

This is part 2 of the Azure Functions Deep Dive series. Part 1 covered host bootstrap; this part stays beside that host and follows the worker process from configuration to `Process.Start`, isolating the handoff between host-managed runtime selection and worker-managed execution.

---

## Call Path Summary

- `WorkerConfigurationResolver.GetWorkerConfigs()` → `DynamicWorkerConfigurationProvider` / `DefaultWorkerConfigurationProvider` / `ExplicitWorkerConfigurationProvider` → `RpcWorkerConfig`
- `GrpcWorkerChannel.StartWorkerProcessAsync()` → `IWorkerProcess.StartProcessAsync()` → `RpcWorkerProcess.CreateWorkerProcess()` → `_processFactory.CreateWorkerProcess(workerContext)` → `Process.Start()`

---

<!-- toc:begin -->
## In this series

- [Host Bootstrap — Following `WebJobsScriptHostService`](./01-host-bootstrap.md)
- **Worker Processes — How One Host Hosts Many Languages (current)**
- The gRPC Event Stream — What Do the Host and Worker Actually Exchange? (upcoming)
- Dispatcher and Invocation — How a Function Call Reaches the Worker (upcoming)
- Scaling Internals — Scale Controller, ScaleMonitor, and What Differs Across Plans (upcoming)
- Cold Start and Placeholder Mode — What Happens When a New Instance Is Born (upcoming)

<!-- toc:end -->

---

## References

**Source code (commit `5e59423`)**
- [`RpcWorkerProcess.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script.Grpc/Rpc/RpcWorkerProcess.cs)
- [`WorkerProcess.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script.Grpc/ProcessManagement/WorkerProcess.cs)
- [`GrpcWorkerChannel.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script.Grpc/Channel/GrpcWorkerChannel.cs)
- [PR #4210 — `FUNCTIONS_WORKER_PROCESS_COUNT`](https://github.com/Azure/azure-functions-host/pull/4210)
- [`WorkerProcessCountOptions.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script/Workers/WorkerProcessCountOptions.cs)
- [`WorkerConcurrencyOptions.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script/Config/WorkerConcurrencyOptions.cs)
- [`WorkerConcurrencyManager.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script.Grpc/WorkerConcurrencyManager.cs)

**Related worker repos**
- [`Azure/azure-functions-nodejs-worker` `worker.config.json`](https://github.com/Azure/azure-functions-nodejs-worker/blob/v3.x/worker.config.json)
- [`Azure/azure-functions-python-worker`](https://github.com/Azure/azure-functions-python-worker)
- [`Azure/azure-functions-java-worker` `worker.config.json`](https://github.com/Azure/azure-functions-java-worker/blob/dev/worker.config.json)

Tags: Azure Functions, Serverless, Distributed Systems, gRPC
