---
title: "Azure Functions Deep Dive (3/6): gRPC 이벤트 스트림 — 호스트와 워커는 무엇을 주고받는가"
series: azure-functions-deep-dive
episode: 3
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Azure Functions
- Serverless
- Distributed Systems
- gRPC
last_reviewed: '2026-05-12'
seo_description: 이 글의 모든 코드 인용은 Azure/azure-functions-host @ 5e59423 기준입니다.
---

# Azure Functions Deep Dive (3/6): gRPC 이벤트 스트림 — 호스트와 워커는 무엇을 주고받는가

워커 프로세스를 띄웠다고 해서 Functions가 곧바로 동작하는 것은 아닙니다. 실제 시스템 경계는 호스트와 워커가 생명주기 메시지, 함수 메타데이터, invocation, 로그, 상태 신호를 어떤 전송 경로로 주고받는지에서 드러납니다. 이 경로를 모르면 out-of-proc 모델은 “프로세스가 따로 있다”는 설명 이상으로 내려가지 못합니다.

이 글의 범위는 하나입니다. `Process.Start()` 이후, 워커가 호스트와 처음 말을 트는 순간부터 시작해 실제 invocation이 오갈 준비가 될 때까지의 프로토콜 경계를 코드로 따라갑니다. 기준은 호스트 저장소 [`Azure/azure-functions-host @ 5e59423`](https://github.com/Azure/azure-functions-host/tree/5e59423ba45491041d18224c3e72c168a4a5b7f7)와 프로토콜 저장소 [`Azure/azure-functions-language-worker-protobuf`](https://github.com/Azure/azure-functions-language-worker-protobuf)입니다.

특히 이번 글은 “gRPC를 쓴다”는 일반론이 아니라, 실제로 서비스가 하나이고 RPC도 하나이며 그 위에 dozens of message types가 `oneof`로 다중화된다는 사실을 구조적으로 정리합니다. 그리고 호스트 내부에서는 이 스트림이 일반 이벤트 버스보다 **워커별 채널 쌍 + gRPC 펌프**에 더 가깝게 구현되어 있다는 점을 보겠습니다.

이 글은 Azure Functions Deep Dive 시리즈의 세 번째 글입니다.

이제 워커가 연결된 뒤 호스트와 워커 사이에 놓이는 실제 wire protocol 경계를 선명하게 보겠습니다.

## 먼저 던지는 질문

- 호스트-워커 gRPC 스트림에는 어떤 메시지가 어떤 방식으로 실릴까요?
- 스트림이 끊기면 호스트와 워커는 각각 무엇을 가정할까요?
- 큰 페이로드는 이 스트림 위를 어떻게 지나가며, 어디에서 한계가 드러날까요?

## 큰 그림

![Azure Functions Deep Dive 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-deep-dive/03/03-01-all-on-one-screen.ko.png)

*Azure Functions Deep Dive 3장 흐름 개요*

이 그림에서는 gRPC 이벤트 스트림 — 호스트와 워커는 무엇을 주고받는가를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> gRPC 이벤트 스트림 — 호스트와 워커는 무엇을 주고받는가의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 이 글이 중요한가

운영에서 “워커와 통신이 안 된다”는 말은 매우 자주 쓰이지만, 실제로는 여러 다른 층이 섞여 있습니다. 프로세스가 안 떴을 수도 있고, gRPC 클라이언트가 호스트에 붙지 못했을 수도 있고, 붙었지만 capability handshake가 끝나지 않았을 수도 있고, 함수 로드 메시지까지는 갔지만 invocation 경로가 준비되지 않았을 수도 있습니다. 프로토콜 경계를 알아야 이 문제들을 분리할 수 있습니다.

또한 Azure Functions의 out-of-proc 모델은 언어마다 구현체가 달라도 프로토콜은 동일하다는 점이 핵심입니다. Node, Python, Java 워커 코드가 달라도 `StartStream`, `WorkerInitRequest`, `FunctionLoadRequest`, `InvocationRequest`라는 공통 메시지 집합을 공유합니다. 이 사실을 이해하면 언어별 구현 차이와 플랫폼 공통 경계를 구분해서 볼 수 있습니다.

마지막으로, 이 글은 다음 화의 invocation 경로를 위한 전제 조건입니다. 한 번의 함수 호출이 워커에 도달하려면 먼저 워커별 채널과 응답 상관관계 구조가 이미 준비되어 있어야 합니다. 따라서 gRPC 스트림 구조를 이해하지 않고 dispatcher와 invocation을 보면 메시지 흐름이 지나치게 추상적으로 남습니다.

## 핵심 관점

Azure Functions 호스트-워커 통신은 서비스 하나와 RPC 하나로 압축됩니다. 중요한 것은 RPC가 많지 않다는 사실이 아니라, **하나의 양방향 스트림 위에 거의 모든 프로토콜 메시지가 `oneof`로 다중화되어 있다는 점**입니다. 생명주기, 함수 로드, invocation, 로그, 상태 점검이 모두 같은 운반체 위를 지나갑니다.

호스트 내부 구현도 이 관점을 뒷받침합니다. 겉으로는 gRPC 서버와 클라이언트처럼 보이지만, 실제 소스에 가까이 붙어 보면 각 워커마다 inbound/outbound `Channel<T>`가 따로 있고, `FunctionRpcService`가 그 채널들과 실제 gRPC 스트림 사이를 연결하는 펌프 역할을 합니다. 즉 “generic event bus”보다는 “워커별 큐와 스트림 연결기”에 더 가깝습니다.

> 이 글에서 잡아야 할 핵심은 단순히 gRPC를 쓴다는 사실이 아니라, 워커 하나가 워커별 채널 쌍과 하나의 `EventStream`에 매핑된다는 구체적인 통신 모델입니다.

## 핵심 개념

### 출발점은 정말로 RPC 하나뿐입니다

호스트와 워커 사이의 통신 정의는 아래 한 줄로 요약됩니다.

```protobuf
service FunctionRpc {
  rpc EventStream (stream StreamingMessage) returns (stream StreamingMessage) {}
}
```

`EventStream` 하나, 양방향 스트림 하나입니다. 요청-응답 RPC 여러 개가 있는 구조가 아닙니다. 따라서 이 채널 위에서 무엇이 오갈 수 있는지 이해하려면 `StreamingMessage`가 실을 수 있는 payload 집합을 보는 것이 핵심입니다.

### `StreamingMessage`는 `oneof`로 다중화된 만능 메시지입니다

`FunctionRpc.proto`의 `StreamingMessage`는 아래처럼 정의되어 있습니다.

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

여기서 중요한 것은 두 가지입니다. `request_id`는 비동기 응답 상관관계에 쓰이고, `oneof content`는 한 번에 하나의 payload만 실을 수 있게 하면서도 수십 가지 메시지 타입을 같은 채널에 다중화합니다. 결국 Functions 프로토콜은 이 `oneof` 안에 들어가는 메시지 집합이라고 봐도 됩니다.

### 메시지 집합은 다섯 부류로 나눠 보면 이해가 쉬워집니다

프로토콜을 화면 하나에 올려놓으면 다음 다섯 부류로 볼 수 있습니다.

| 그룹 | 메시지 | 방향 |
|---|---|---|
| **Lifecycle** | StartStream, WorkerInitRequest/Response, WorkerTerminate | `StartStream` is worker → host, `WorkerInitRequest` is host → worker, `WorkerInitResponse` is worker → host, `WorkerTerminate` is host → worker |
| **Health checks** | WorkerStatusRequest/Response | Host → Worker |
| **Function loading** | FunctionLoadRequest/Response, FunctionsMetadataRequest, FunctionMetadataResponse | Host ↔ Worker |
| **Invocation** | InvocationRequest/Response, InvocationCancel | Host → Worker (response goes the other way) |
| **Operations** | RpcLog, FileChangeEventRequest, FunctionEnvironmentReloadRequest/Response, WorkerWarmupRequest/Response | Mixed |

이 표를 머리에 넣으면 이후 세부 단계가 훨씬 단순해집니다. 같은 스트림을 쓰더라도 지금 오가는 메시지가 생명주기인지, 함수 로드인지, 호출인지 구분할 수 있기 때문입니다.

### 첫 핸드셰이크를 이해하면 나머지가 따라옵니다

실제 시작 순서는 네 단계로 요약할 수 있습니다. 먼저 워커가 `StartStream`으로 자신을 소개합니다.

```protobuf
message StartStream {
  // id of the worker
  string worker_id = 2;
}
```

이 `worker_id`는 호스트가 2화에서 워커를 띄울 때 환경변수나 명령줄 인자로 넘겨준 값입니다. 즉 워커는 호스트가 준 식별자를 다시 되돌려 주며, 호스트는 “방금 붙은 gRPC 클라이언트가 내가 띄운 그 워커가 맞다”고 확인합니다.

그 다음 호스트는 `WorkerInitRequest`를 보냅니다.

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

여기서 핵심은 `capabilities`입니다. 호스트가 자신이 지원하는 기능을 광고하고, 워커는 그 정보를 읽어 “이 호스트와는 shared memory data transfer를 쓸 수 있나, HTTP body를 어떤 방식으로 받을 수 있나”를 결정합니다.

이어서 워커는 `WorkerInitResponse`로 자기 capability를 돌려줍니다.

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

호스트는 `WorkerChannel.ApplyCapabilities()`를 통해 이 값을 병합하고, 그 결과로 shared memory 전송이나 HTTP proxying 같은 기능을 활성화할지 판단합니다. `WorkerMetadata`에는 런타임 종류, 버전, bitness 같은 telemetry 정보도 함께 실립니다.

마지막으로 호스트는 함수별 `FunctionLoadRequest` 또는 일괄 `FunctionLoadRequestCollection`을 보내 워커에게 실제 함수 목록을 알려 줍니다.

```protobuf
message FunctionLoadRequest {
  string function_id = 1;
  RpcFunctionMetadata metadata = 2;
  bool managed_dependency_enabled = 3;
}
```

이 네 단계가 끝나야 워커는 invocation을 받을 준비를 갖춥니다.

### 호스트 쪽 gRPC 서버는 `FunctionRpcService`입니다

워커는 gRPC 클라이언트이고, 호스트는 서버입니다. 호스트 쪽 `EventStream` 구현은 `src/WebJobs.Script.Grpc/Server/FunctionRpcService.cs`에 있습니다. 이 클래스는 `FunctionRpc.FunctionRpcBase`를 상속하고 `EventStream` 메서드를 override합니다.

주변 파일도 함께 보면 구조가 더 분명해집니다. `AspNetCoreGrpcServer.cs`는 Kestrel + ASP.NET Core gRPC 서버를 호스트 내부에 띄우는 진입점이고, `AspNetCoreGrpcHostBuilder.cs`는 그 gRPC 서버용 `IHost`를 만들며, `Startup.cs`는 `endpoints.MapGrpcService<FunctionRpc.FunctionRpcBase>()`로 엔드포인트를 등록합니다. 즉 **Functions Host 내부에 localhost gRPC 서버가 하나 돌고 있고, 각 워커가 그 서버에 클라이언트로 붙는 구조**입니다.

### 호스트 내부에서는 워커별 채널 쌍과 gRPC 펌프로 보는 편이 정확합니다

이 부분은 소스에 가까이 붙어 읽는 것이 중요합니다. 실제 invocation 경로는 넓은 pub-sub 버스라기보다 워커별 inbound/outbound 채널 쌍으로 구현됩니다. `GrpcEventExtensions.AddGrpcChannels(workerId)`가 워커 ID별로 두 개의 채널을 만듭니다.

- inbound: worker → host 방향의 `InboundGrpcEvent`
- outbound: host → worker 방향의 `OutboundGrpcEvent`

`FunctionRpcService.EventStream()`는 먼저 `StartStream`으로 워커 ID를 확인한 뒤 `TryGetGrpcChannels(workerId, out inbound, out outbound)`를 호출합니다. 그 다음은 기계적입니다. gRPC에서 읽은 `StreamingMessage`를 inbound 채널에 쓰고, outbound 채널에서 꺼낸 메시지를 다시 gRPC 응답 스트림으로 밀어 넣습니다.

![Per-worker channel pairs and gRPC pump](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-deep-dive/03/03-02-the-channel-layout-closer-to-per-worker.ko.png)

따라서 `FunctionRpcService`는 실제 gRPC 스트림과 호스트 내부 워커별 큐 사이의 펌프입니다. `IScriptEventManager`가 있기는 하지만, 적어도 함수 호출 트래픽을 이해하는 데는 “워커별 큐 + gRPC 펌프”라는 멘탈 모델이 소스와 가장 잘 맞습니다.

### 결국 한 invocation이 타는 통신 인프라는 이렇게 요약됩니다

한 문장으로 압축하면 이렇습니다. `FunctionRpcService`가 워커에서 온 `StreamingMessage`를 읽어 그 워커의 inbound 채널에 넣고, outbound 채널의 메시지를 다시 gRPC 스트림으로 배출합니다. 그리고 `GrpcWorkerChannel`은 그 채널 쌍 위에 올라가 요청과 응답을 워커 단위로 맞춰 주는 호스트 측 제어 객체입니다.

이 그림이 잡히면 이후 dispatcher와 invocation 경로가 “generic event bus를 떠다니는 메시지”가 아니라, **워커 하나에 귀속된 실체적인 송수신 경로**로 보이기 시작합니다.

## 흔히 헷갈리는 지점

- **호스트-워커 통신은 RPC 여러 개가 아니라 `EventStream` 하나입니다.** 수십 가지 메시지 타입이 `StreamingMessage.oneof`로 다중화됩니다.
- **워커가 먼저 `StartStream`으로 자신을 소개합니다.** 호스트가 일방적으로 초기화만 하는 구조가 아닙니다.
- **capability negotiation은 일회성 “공통집합 계산”으로 끝나지 않습니다.** 호스트는 워커 capability를 병합한 뒤 그 상태로 기능을 파생합니다.
- **호스트 내부 경로는 generic event bus보다 워커별 채널 쌍에 가깝습니다.** invocation 트래픽은 worker-specific inbound/outbound 큐 위에서 움직입니다.
- **프로토콜이 공통이라는 말은 언어별 구현이 같다는 뜻이 아닙니다.** 구현은 달라도 같은 메시지 집합과 같은 핸드셰이크 순서를 공유한다는 뜻입니다.

## 운영 체크리스트

- [ ] 큰 페이로드 함수에 대해 chunking 또는 shared-memory 전송 정책을 정했습니다.
- [ ] worker disconnect와 자동 복구 알림을 대시보드에 올렸습니다.
- [ ] gRPC 채널 지연과 오류 지표를 관측 가능한 형태로 정리했습니다.
- [ ] 스트림 드롭 시 외부 의존성에 대한 idempotency 보장을 점검했습니다.
- [ ] 추적 가능한 디버깅을 위해 correlation ID 전파 정책을 정의했습니다.

## 정리

이번 글은 Azure Functions out-of-proc 모델의 실제 프로토콜 경계를 고정했습니다. 워커는 하나의 양방향 `EventStream`으로 호스트와 대화하고, 그 위에서 생명주기·함수 로드·호출·로그·상태 메시지가 모두 `StreamingMessage` 형태로 다중화됩니다. 즉 gRPC는 단순 운반체가 아니라 전체 호스트-워커 계약의 표면입니다.

동시에 호스트 내부 구현도 함께 분해했습니다. `FunctionRpcService`는 호스트 내부 localhost gRPC 서버의 핸들러이며, 실제 동작은 워커별 inbound/outbound 채널과 gRPC 스트림을 이어 주는 펌프에 가깝습니다. 이 구조를 이해하면 “통신이 안 된다”는 증상을 훨씬 더 구체적인 단계 문제로 쪼갤 수 있습니다.

이제 다음 글에서는 이 스트림 위를 오가는 메시지 중 가장 중요한 `InvocationRequest`와 `InvocationResponse`에 집중합니다. 트리거가 발화했을 때 그 사건이 어떻게 워커 안의 사용자 함수 호출이 되고, 결과가 어떤 상관관계 경로를 따라 호스트로 되돌아오는지 보겠습니다.

## 처음 질문으로 돌아가기

- **호스트-워커 gRPC 스트림에는 어떤 메시지가 어떤 방식으로 실릴까요?**
  - 본문의 기준은 gRPC 이벤트 스트림 — 호스트와 워커는 무엇을 주고받는가를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **스트림이 끊기면 호스트와 워커는 각각 무엇을 가정할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **큰 페이로드는 이 스트림 위를 어떻게 지나가며, 어디에서 한계가 드러날까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure Functions Deep Dive (1/6): 호스트 부팅 — `WebJobsScriptHostService`부터 따라가기](./01-host-bootstrap.md)
- [Azure Functions Deep Dive (2/6): Worker 프로세스 — 한 호스트에서 여러 언어 런타임이 같이 사는 법](./02-worker-process.md)
- **Azure Functions Deep Dive (3/6): gRPC 이벤트 스트림 — 호스트와 워커는 무엇을 주고받는가 (현재 글)**
- Azure Functions Deep Dive (4/6): Dispatcher와 Invocation — 함수 호출이 워커에 도달하기까지 (예정)
- Azure Functions Deep Dive (5/6): 스케일링 내부 동작 — Scale Controller, ScaleMonitor, 그리고 플랜별 차이 (예정)
- Azure Functions Deep Dive (6/6): 콜드 스타트와 Placeholder Mode — 새 인스턴스가 만들어질 때 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [`Azure/azure-functions-host @ 5e59423`](https://github.com/Azure/azure-functions-host/tree/5e59423ba45491041d18224c3e72c168a4a5b7f7)
- [`Azure/azure-functions-language-worker-protobuf`](https://github.com/Azure/azure-functions-language-worker-protobuf)
- [FunctionRpc.proto](https://github.com/Azure/azure-functions-language-worker-protobuf/blob/3757ce8/src/proto/FunctionRpc.proto)
- [`Server/FunctionRpcService.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Server/FunctionRpcService.cs)
- [`Server/AspNetCoreGrpcServer.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Server/AspNetCoreGrpcServer.cs)
- [`Channel/GrpcWorkerChannel.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Channel/GrpcWorkerChannel.cs)
- [`Channel/GrpcCapabilities.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Channel/GrpcCapabilities.cs)
- [`Eventing/GrpcEventExtensions.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Eventing/GrpcEventExtensions.cs)
- [`Channel/OrderedInvocationMessageDispatcher.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Channel/OrderedInvocationMessageDispatcher.cs)

### 관련 시리즈
- [Azure Functions 101 — Host와 Worker](../../azure-functions-101/ko/03-host-and-worker.md)
- [Azure Functions 101 — 스케일링과 콜드 스타트](../../azure-functions-101/ko/06-scaling-and-cold-start.md)
- [Azure App Service Deep Dive — App Service 플랫폼 아키텍처](../../azure-app-service-deep-dive/ko/01-platform-architecture.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-functions-deep-dive/ko/03-grpc-event-stream)

Tags: Azure Functions, Serverless, Distributed Systems, gRPC
