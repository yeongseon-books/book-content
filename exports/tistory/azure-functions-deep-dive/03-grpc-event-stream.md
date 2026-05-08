
# gRPC 이벤트 스트림 — 호스트와 워커는 무엇을 주고받는가

> Azure Functions Deep Dive 시리즈 (3/6)

## Source Version

이 글의 모든 코드 인용은 [`Azure/azure-functions-host @ 5e59423`](https://github.com/Azure/azure-functions-host/tree/5e59423ba45491041d18224c3e72c168a4a5b7f7) 기준입니다.

2화에서 워커 프로세스가 떠지는 것까지 봤습니다. `WorkerProcess.StartProcessAsync()`가 최종적으로 `Process.Start()`를 호출하면, Node/Python/Java 같은 외부 프로세스가 실행됩니다. 그러나 그것만으로는 아무 일도 일어나지 않습니다. **호스트와 워커가 서로 말을 걸 채널이 필요**합니다.

그 채널은 단 하나의 **양방향 gRPC 스트림**입니다. 이 글에서는 그 스트림이 어떻게 생겼는지, 어떤 메시지가 오가는지, 그리고 호스트 측에서 그것을 어떻게 받고 라우팅하는지를 코드로 따라갑니다.

> 이 글의 모든 코드 인용은 다음 두 저장소를 기준으로 합니다.
> - 호스트: [`Azure/azure-functions-host` @ `5e59423`](https://github.com/Azure/azure-functions-host/tree/5e59423ba45491041d18224c3e72c168a4a5b7f7)
> - 프로토콜: [`Azure/azure-functions-language-worker-protobuf`](https://github.com/Azure/azure-functions-language-worker-protobuf) — 프로토콜은 호스트와 분리된 별도 저장소에 정의되어 있습니다.

---

<!-- a-grade-intro:begin -->
## 핵심 질문

Host와 Worker의 gRPC 이벤트 스트림을 이해하면 어떤 통신 사고를 진단할 수 있을까요?

이 글은 그 질문에 답하기 위해 gRPC 이벤트 스트림의 핵심 결정과 운영 함정을 살펴봅니다.

<!-- a-grade-intro:end -->

## 이 글에서 답할 질문

- Host와 Worker 사이의 gRPC stream은 어떤 종류의 메시지를 어떻게 주고받는가?
- 이 stream이 끊기면 호스트는 무엇을 가정하고, Worker는 무엇을 가정하는가?
- 큰 payload는 stream 위에서 어떻게 흘러가는가, 한계는 어디인가?
- gRPC 흐름의 backpressure는 어디에서 가시화되는가?
- 이 채널은 디버깅 가능한 채널인가, 아니면 블랙박스인가?

## 큰 그림 — 단 하나의 스트림

먼저 결론. Azure Functions의 호스트-워커 통신은 **gRPC 서비스 하나, RPC 하나**로 구성됩니다.

```protobuf
service FunctionRpc {
  rpc EventStream (stream StreamingMessage) returns (stream StreamingMessage) {}
}
```

한 줄입니다. `EventStream` 하나. 양쪽 모두 stream. 즉 호스트와 워커는 **같은 채널을 통해 자유롭게 메시지를 주고받습니다**. 요청-응답 RPC가 아닙니다.

이 한 줄이 갖는 의미는 큽니다. **`StreamingMessage`에 들어갈 수 있는 모든 종류의 메시지**가 곧 Functions 프로토콜의 전부입니다.

---

## `StreamingMessage` — `oneof`로 다중화된 만능 메시지

[`FunctionRpc.proto`의 `StreamingMessage`](https://github.com/Azure/azure-functions-language-worker-protobuf/blob/3757ce8/src/proto/FunctionRpc.proto)는 이렇게 생겼습니다.

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

두 가지를 눈여겨봐야 합니다.

1. `request_id` — 호스트와 워커가 메시지를 짝짓는 데 쓰는 ID. 비동기 응답을 짝지을 때 결정적입니다.
2. `oneof content` — 한 번에 하나의 페이로드만 들어갑니다. 즉 같은 채널에 **수십 종의 메시지가 다중화**됩니다.

이걸 분류해 보면 메시지는 크게 다섯 그룹으로 나뉩니다.

| 그룹 | 메시지 | 누가 보내는가 |
|---|---|---|
| **수명주기** | StartStream, WorkerInitRequest/Response, WorkerTerminate | StartStream은 워커 → 호스트, WorkerInitRequest는 호스트 → 워커, WorkerInitResponse는 워커 → 호스트, WorkerTerminate는 호스트 → 워커 |
| **상태 점검** | WorkerStatusRequest/Response | 호스트 → 워커 |
| **함수 로드** | FunctionLoadRequest/Response, FunctionsMetadataRequest, FunctionMetadataResponse | 호스트 ↔ 워커 |
| **호출** | InvocationRequest/Response, InvocationCancel | 호스트 → 워커 (응답 역방향) |
| **운영** | RpcLog, FileChangeEventRequest, FunctionEnvironmentReloadRequest/Response, WorkerWarmupRequest/Response | 다양 |

이 표가 곧 Functions 프로토콜의 전체 그림입니다.

---

## 핸드셰이크 — 워커가 떠서 호스트와 처음 말을 트는 순간

이 모든 메시지가 다 중요하지만, **가장 처음 일어나는 핸드셰이크**를 이해하면 나머지는 자연스럽게 따라옵니다.

### 1단계 — 워커가 `StartStream`을 보낸다

워커 프로세스가 부팅을 마치면, 먼저 호스트에게 자기소개를 합니다.

```protobuf
message StartStream {
  // id of the worker
  string worker_id = 2;
}
```

워커는 자신의 `worker_id`를 담아 `StartStream`을 호스트로 보냅니다. 이 ID는 2화에서 본 `RpcWorkerConfig` 생성 시 호스트가 워커에게 환경 변수나 명령행 인자로 전달한 것과 동일합니다. 즉 **호스트가 미리 알려준 ID를 워커가 그대로 되돌려주는** 인사입니다. 호스트는 이걸로 "방금 연결한 이 gRPC 클라이언트가 내가 띄운 그 워커"임을 확인합니다.

### 2단계 — 호스트가 `WorkerInitRequest`를 보낸다

워커의 신원이 확인되면, 호스트는 워커를 "초기화"합니다.

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

여기서 가장 중요한 필드는 `capabilities`입니다. **호스트가 자기가 지원하는 기능을 광고**합니다. (예: shared memory data transfer, RPC HTTP body, raw HTTP body bytes 등) 워커는 이걸 보고 "이 호스트랑은 이런 기능까지 쓸 수 있네"를 학습합니다.

### 3단계 — 워커가 `WorkerInitResponse`로 답한다

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

이번엔 반대로 **워커가 자기 capabilities를 광고**합니다. 호스트는 `WorkerChannel.ApplyCapabilities()`로 기존 capability 상태를 갱신하며, 기본 전략은 merge입니다. 즉 “양쪽 capability의 단순 교집합을 한 번 계산한다”기보다, **호스트가 알고 있는 capability 집합을 업데이트하고 그 결과로 shared memory·HTTP proxying 같은 동작을 켜거나 끄는 모델**에 가깝습니다. 또한 `WorkerMetadata`로 런타임 종류, 버전, 비트성 같은 텔레메트리용 메타데이터가 함께 옵니다.

### 4단계 — 호스트가 `FunctionLoadRequest`로 함수를 로드시킨다

핸드셰이크가 끝나면 호스트는 본격적으로 함수를 워커에게 알려줍니다.

```protobuf
message FunctionLoadRequest {
  string function_id = 1;
  RpcFunctionMetadata metadata = 2;
  bool managed_dependency_enabled = 3;
}
```

각 함수마다 하나씩 보내거나, 또는 `FunctionLoadRequestCollection`으로 한 번에 묶어서 보냅니다. 워커는 각각에 대해 `FunctionLoadResponse`로 "성공/실패"를 알려줍니다.

### 한 화면으로

![워커 생애주기의 공통 프로토콜 흐름](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-deep-dive/03/03-01-all-on-one-screen.ko.png)

*워커 생애주기의 공통 프로토콜 흐름*
이 시퀀스가 **모든 워커의 일생**입니다. Node 워커도, Python 워커도, Java 워커도 똑같습니다. 언어별로 다른 건 워커 측의 구현 상세이고, **프로토콜은 단일**입니다.

---

## 호스트 측 — `FunctionRpcService`가 EventStream을 받는다

워커는 클라이언트, 호스트는 서버입니다. 호스트 측에서 `EventStream` RPC를 구현하는 건 [`src/WebJobs.Script.Grpc/Server/FunctionRpcService.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Server/FunctionRpcService.cs)입니다.

이름에서 짐작되듯, `FunctionRpc.FunctionRpcBase`(protoc가 `service FunctionRpc`에서 자동 생성한 base 클래스)를 상속해 `EventStream` 메서드를 override합니다.

`Server/` 디렉토리에는 이 외에도 다음 파일이 있습니다.

- [`AspNetCoreGrpcServer.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Server/AspNetCoreGrpcServer.cs) — Kestrel + ASP.NET Core gRPC를 호스트 안에 서버로 띄우는 진입점
- [`AspNetCoreGrpcHostBuilder.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Server/AspNetCoreGrpcHostBuilder.cs) — gRPC 서버용 IHost를 빌드
- [`Startup.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Server/Startup.cs) — `endpoints.MapGrpcService<FunctionRpc.FunctionRpcBase>()`로 gRPC 엔드포인트 매핑

즉, **함수 호스트 안에서 ASP.NET Core gRPC 서버가 함께 떠 있고**, 워커 프로세스들은 그 서버에 gRPC 클라이언트로 접속해 `EventStream`을 부릅니다. localhost gRPC 통신입니다.

서버가 듣는 주소(엔드포인트와 포트)는 호스트가 결정하고, 2화에서 본 환경 변수/명령행 인자를 통해 워커에게 알려줍니다. 그래서 워커 측 코드를 보면 거의 모든 언어 워커가 첫 진입점에서 "호스트가 알려준 주소로 gRPC 클라이언트를 만든다"는 동일한 패턴을 보입니다.

---

## `GrpcWorkerChannel` — 호스트가 워커를 다루는 손잡이

서버가 받은 메시지는 결국 누군가가 **읽고 라우팅**해야 합니다. 그 "누군가"가 호스트 측의 워커 핸들 객체, **`GrpcWorkerChannel`**입니다.

[`src/WebJobs.Script.Grpc/Channel/GrpcWorkerChannel.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Channel/GrpcWorkerChannel.cs)는 호스트가 **하나의 워커 프로세스 = 하나의 인스턴스** 비율로 갖고 있는 객체입니다. 같은 디렉토리의 다른 파일들을 곁에 두고 보면 역할이 분명해집니다.

| 파일 | 역할 |
|---|---|
| `GrpcWorkerChannel.cs` | 워커 1대를 대표하는 손잡이. `StartWorkerProcessAsync()`, `SendWorkerInitRequest`, `SendInvocationRequest`, `StopWorkerProcess()` 같은 흐름이 여기와 베이스 `WorkerChannel`에 걸쳐 있습니다. |
| [`WorkerChannel.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Channel/WorkerChannel.cs) | gRPC 위에 있는 공통 베이스 |
| [`GrpcWorkerChannelFactory.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Channel/GrpcWorkerChannelFactory.cs) | `GrpcWorkerChannel`을 만드는 팩토리 |
| [`GrpcCapabilities.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Channel/GrpcCapabilities.cs) | capability 키 상수 모음 |
| [`OrderedInvocationMessageDispatcher.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Channel/OrderedInvocationMessageDispatcher.cs) | 같은 `invocation_id`에 속한 메시지를 순서대로 처리 |

이번 글에서 붙잡아 둘 핵심은 하나입니다. **이 객체가 EventStream을 양쪽 방향에서 다룬다**는 사실입니다.

---

## 채널 구조 — 범용 이벤트 버스보다 워커별 `Channel<T>` 쌍에 가깝다

이 부분은 그림을 과장 없이 보는 편이 좋습니다. 호출 메시지의 주 경로는 “광범위한 in-process 이벤트 버스”가 아니라, **워커 하나마다 만들어지는 inbound/outbound `Channel<T>` 쌍**입니다.

`GrpcEventExtensions.AddGrpcChannels(workerId)`는 워커 ID별로 다음 두 채널을 만듭니다.

- inbound: 워커 → 호스트로 들어오는 `InboundGrpcEvent`
- outbound: 호스트 → 워커로 나가는 `OutboundGrpcEvent`

`FunctionRpcService.EventStream()`은 `StartStream`으로 워커 ID를 확인한 뒤 `TryGetGrpcChannels(workerId, out inbound, out outbound)`를 호출합니다. 그 다음 동작은 단순합니다.

- gRPC에서 읽은 `StreamingMessage`를 inbound 채널에 씁니다.
- outbound 채널에서 읽은 메시지를 gRPC 응답 스트림으로 씁니다.

즉 `FunctionRpcService`는 호스트 쪽 gRPC 서버이면서, 동시에 **워커별 채널과 실제 gRPC 스트림 사이를 펌프하는 중계기**입니다.

![워커별 채널 쌍과 gRPC 펌프 구조](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-deep-dive/03/03-02-the-channel-layout-closer-to-per-worker.ko.png)

*워커별 채널 쌍과 gRPC 펌프 구조*
`IScriptEventManager`는 이 채널들을 워커 ID로 보관하고 찾는 상태 저장소로 쓰입니다. `InboundGrpcEvent`와 `OutboundGrpcEvent` 같은 래퍼 타입도 실제로 존재합니다. 다만 함수 호출 메시지의 핵심 경로를 설명할 때는, 그것들을 범용 pub-sub 버스라고 이해하기보다 **워커별 큐와 펌프 구조**로 보는 쪽이 코드와 더 가깝습니다.

---

## 그래서 한 호출은 어떤 길을 가는가

지금까지의 모든 걸 한 줄로 줄이면 다음과 같습니다.

> 호스트 안의 `FunctionRpcService`는 워커가 보낸 `StreamingMessage`를 받아 해당 워커의 inbound 채널에 넣고, outbound 채널에서 꺼낸 메시지를 다시 gRPC 스트림으로 씁니다. `GrpcWorkerChannel`은 자기 워커에 연결된 그 채널 쌍을 통해 요청과 응답을 처리합니다.

여기까지가 "통신 인프라"입니다. 워커별 채널 쌍과 gRPC 펌프 구조를 머릿속에 넣고 나면, 이후의 호출 경로도 범용 이벤트 버스가 아니라 구체적인 요청/응답 전송으로 읽히기 시작합니다.

---

## 이 글이 고정해 주는 것

여기까지 오면 프로토콜 경계가 선명해집니다. 워커 하나가 양방향 gRPC 스트림 하나로 호스트에 붙고, 호스트는 그 워커를 채널 쌍으로 매핑하며, `GrpcWorkerChannel`이 그 위에서 워커별 제어 객체 역할을 맡습니다.

---

## 시리즈 안에서의 위치

이 글은 Azure Functions Deep Dive 시리즈 3화입니다. 2화가 워커 프로세스를 띄우는 문제였다면, 이번 화는 그 워커가 호스트와 어떤 전송 경계로 붙는지 분해해 보여 줍니다.

---

## Call Path Summary

- Worker bootstrap → `StartStream(worker_id)` → `FunctionRpcService.EventStream(...)` → `TryGetGrpcChannels(workerId, out inbound, out outbound)`
- `WorkerChannel.SendWorkerInitRequest()` → `WorkerInitResponse` → `ApplyCapabilities(...)`
- `WorkerChannel.SendFunctionLoadRequest()` / `SendFunctionLoadRequestCollection()` → worker load ack → per-worker invocation path becomes ready

---

## 시니어 엔지니어는 이렇게 생각합니다

- **StreamingMessage가 통신의 단위** — 요청·응답·로그가 모두 같은 스트림을 탑니다.
- **스트림 단절은 워커 사망 신호** — 재연결 패턴을 메트릭으로 추적합니다.
- **InvocationRequest·Response가 핵심** — 함수 호출의 양방향이 명확히 구조화되어 있습니다.
- **페이로드 크기 한계를 의식** — 대용량 입출력은 외부 스토리지를 경유해야 합니다.
- **로그도 같은 채널로 흐른다** — 워커 로그 누락은 채널 단절의 단서입니다.

## 운영 체크리스트

- [ ] 큰 payload 함수의 분할/스트리밍 정책을 정했다
- [ ] Worker disconnect 알림과 자동 복구 동작을 검증했다
- [ ] gRPC 채널 메트릭(latency, error)을 대시보드에 노출했다
- [ ] stream 끊김 시 외부 의존성에 대한 idempotency 보장을 검토했다
- [ ] 디버깅을 위한 trace correlation ID 전파 정책을 정했다

## 시리즈 목차

- [호스트 부팅 — `WebJobsScriptHostService`부터 따라가기](./01-host-bootstrap.md)
- [Worker 프로세스 — 한 호스트에서 여러 언어 런타임이 같이 사는 법](./02-worker-process.md)
- **gRPC 이벤트 스트림 — 호스트와 워커는 무엇을 주고받는가 (현재 글)**
- Dispatcher와 Invocation — 함수 호출이 워커에 도달하기까지 (예정)
- 스케일링 내부 동작 — Scale Controller, ScaleMonitor, 그리고 플랜별 차이 (예정)
- 콜드 스타트와 Placeholder Mode — 새 인스턴스가 만들어질 때 (예정)

---

## 참고 자료

**프로토콜 (별도 저장소)**
- [FunctionRpc.proto](https://github.com/Azure/azure-functions-language-worker-protobuf/blob/3757ce8/src/proto/FunctionRpc.proto) — `service FunctionRpc`, `StreamingMessage`, 모든 메시지 타입

**호스트 코드 (commit `5e59423`)**
- [`Server/FunctionRpcService.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Server/FunctionRpcService.cs)
- [`Server/AspNetCoreGrpcServer.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Server/AspNetCoreGrpcServer.cs)
- [`Channel/GrpcWorkerChannel.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Channel/GrpcWorkerChannel.cs)
- [`Channel/GrpcCapabilities.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Channel/GrpcCapabilities.cs)
- [`Eventing/GrpcEventExtensions.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Eventing/GrpcEventExtensions.cs)
- [`Channel/OrderedInvocationMessageDispatcher.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Channel/OrderedInvocationMessageDispatcher.cs)

**관련 입문편**
- [Host와 Worker — 함수는 누가 실행하는가 (입문편 3화)](../../azure-functions-101/ko/03-host-and-worker.md)

Tags: Azure Functions, Serverless, Distributed Systems, gRPC

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
