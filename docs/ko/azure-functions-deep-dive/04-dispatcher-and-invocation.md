---
title: Dispatcher와 Invocation — 함수 호출이 워커에 도달하기까지
series: azure-functions-deep-dive
episode: 4
language: ko
status: publish-ready
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
seo_description: 이 글의 모든 코드 인용은 Azure/azure-functions-host @ 5e59423 기준입니다.
---

# Dispatcher와 Invocation — 함수 호출이 워커에 도달하기까지

> Azure Functions Deep Dive 시리즈 (4/6)

## Source Version

이 글의 모든 코드 인용은 [`Azure/azure-functions-host @ 5e59423`](https://github.com/Azure/azure-functions-host/tree/5e59423ba45491041d18224c3e72c168a4a5b7f7) 기준입니다.

3화에서 호스트와 워커가 단 하나의 양방향 gRPC 스트림(`EventStream`)으로 `StreamingMessage`를 주고받는다는 것까지 봤습니다. 이제 그 위에서 일어나는 가장 중요한 메시지 종류 — **`InvocationRequest` / `InvocationResponse`** — 의 흐름을 따라갑니다.

질문은 단순합니다.

> 큐에 메시지가 하나 들어오면, 또는 HTTP 요청이 들어오면, 그게 어떻게 워커 프로세스에 있는 사용자 함수까지 닿고, 결과는 어떻게 돌아오는가?

답에는 두 가지 객체가 핵심으로 등장합니다. `IFunctionInvocationDispatcher`와 `WorkerFunctionInvoker`. 이 글은 두 객체의 역할과 그 사이에서 만들어지는 `InvocationRequest`의 일생을 다룹니다.

> 모든 코드 인용은 [`Azure/azure-functions-host` @ `5e59423`](https://github.com/Azure/azure-functions-host/tree/5e59423ba45491041d18224c3e72c168a4a5b7f7) 기준입니다.

---

## 큰 그림 — 트리거에서 워커까지

먼저 한 호출의 전체 경로를 한 화면에 그리고 시작하겠습니다.

![트리거 호출이 워커에 닿는 경로](../../assets/azure-functions-deep-dive/04/04-01-the-big-picture-from-trigger-to-worker.ko.png)

*트리거 호출이 워커에 닿는 경로*
이 그림이 4화의 전부입니다. 이제 각 단계를 코드로 봅니다.

---

## 1단계 — 트리거가 발화하면 SDK가 Invoker를 호출한다

Azure Functions 호스트는 **WebJobs SDK 위에 얹혀** 있습니다 (1화에서 본 그대로). 큐에 메시지가 도착하면, HTTP 요청이 들어오면, 타이머가 만료되면 — 모두 WebJobs SDK 안의 트리거 리스너가 감지하고, 그것을 함수 호출로 변환합니다.

WebJobs SDK는 함수마다 **`IFunctionInvoker` 구현체**를 하나씩 갖습니다. 이 인터페이스는 단순합니다. "binding 데이터를 받아서 함수를 한 번 실행하라."

호스트가 워커 프로세스에서 함수를 실행할 때 사용하는 구현체가 [`WorkerFunctionInvoker`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/WorkerFunctionInvoker.cs)입니다. 이 객체의 역할을 한 줄로 줄이면 다음과 같습니다.

> **사용자 코드를 직접 호출하는 대신, `IFunctionInvocationDispatcher`에게 호출을 위임한다.**

즉 in-process 모델(C# in-process)에서는 Invoker가 직접 사용자 메서드를 호출하지만, **out-of-proc 워커 모델**(Node, Python, Java, isolated .NET 등)에서는 Invoker가 호출을 gRPC 너머의 워커에게 던지는 게 일입니다. 그 위임 대상이 Dispatcher입니다.

---

## 2단계 — `IFunctionInvocationDispatcher`라는 추상화

[`IFunctionInvocationDispatcher.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/IFunctionInvocationDispatcher.cs) 인터페이스는 호스트가 "함수 호출을 어딘가에 보내는" 능력을 추상화한 진입점입니다.

같은 디렉토리에는 두 개의 구현체가 있습니다.

| 구현체 | 무엇 |
|---|---|
| **`RpcFunctionInvocationDispatcher`** (별도 파일에 위치) | 기본 경로입니다. 워커와의 호출 운반은 gRPC 채널을 사용합니다. |
| [`HttpFunctionInvocationDispatcher.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/HttpFunctionInvocationDispatcher.cs) | `httpWorkerOptions.Value.Description`이 있을 때 선택되는 HTTP worker/custom handler 전용 경로입니다. |

[`FunctionInvocationDispatcherFactory.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/FunctionInvocationDispatcherFactory.cs)는 분기 조건을 아주 단순하게 둡니다. `httpWorkerOptions.Value.Description != null`이면 `HttpFunctionInvocationDispatcher`를 만들고, 아니면 `RpcFunctionInvocationDispatcher`를 만듭니다. 즉 선택 기준은 트리거 종류가 아니라 **HTTP worker/custom handler 구성이 존재하는가**입니다.

핵심 사실 두 가지:

1. **모든 트리거가 같은 `InvocationRequest` 메시지로 평준화됩니다.** 큐 메시지든, 타이머 펄스든, Blob 이벤트든, Dispatcher 입장에서는 똑같이 "한 번 호출하라"는 명령입니다.
2. **HTTP 관련 경로는 두 층으로 나뉩니다.** 첫째, 방금 본 `HttpFunctionInvocationDispatcher`는 factory 단계에서 아예 선택되는 별도 dispatcher입니다. 이건 HTTP worker/custom handler가 구성됐을 때의 경로입니다.

둘째, gRPC 워커가 광고하는 "HTTP proxying" capability는 다른 이야기입니다. 이 경우 dispatcher 자체는 여전히 `RpcFunctionInvocationDispatcher`이고, 워커 채널도 그대로 살아 있습니다. 다만 HTTP 트리거 호출에서 본문 전달만 worker가 연 HTTP 엔드포인트로 우회해 큰 HTTP payload를 protobuf `TypedData.http`에 그대로 싣지 않게 만드는 것입니다. 이름은 비슷하지만, **dispatcher 선택**과 **gRPC 워커의 HTTP 본문 프록시**는 같은 메커니즘이 아닙니다.

---

## 3단계 — `ScriptInvocationContext`를 만들고 Dispatcher에 던진다

`WorkerFunctionInvoker`가 Dispatcher에 호출을 넘길 때 들고 가는 객체가 **`ScriptInvocationContext`**입니다. `5e59423` 기준 실제 필드는 다음 축으로 정리할 수 있습니다.

- 함수 메타데이터 (`FunctionMetadata`)
- 실행 컨텍스트 (`ExecutionContext`)
- 입력 데이터 (`Inputs`)와 바인딩 데이터 (`BindingData`)
- 추적 컨텍스트 (`Traceparent`, `Tracestate`, `Attributes`)
- 취소와 로깅 관련 정보 (`CancellationToken`, `Logger`, `AsyncExecutionContext`, `Properties`)
- 결과를 받을 `TaskCompletionSource<ScriptInvocationResult>` (`ResultSource`)

여기서 중요한 점은 `RetryContext`가 `ScriptInvocationContext`의 직접 필드는 아니라는 것입니다. 재시도 정보는 이후 `ToRpcInvocationRequest()` 변환 과정에서 `InvocationRequest.RetryContext`로 채워집니다. 마지막 항목인 `ResultSource`가 특히 결정적입니다. **Dispatcher는 동기 응답을 기대하지 않습니다.** 호출을 던진 직후 곧바로 `Task`를 반환하고, 워커가 응답을 보내면 그때 비로소 그 `Task`가 완료됩니다. 한 워커에 여러 개의 in-flight 호출이 동시에 있을 수 있고, 그것들은 `invocation_id`로 구별됩니다.

---

## 4단계 — `InvocationRequest` 만들기

3화에서 본 [`FunctionRpc.proto`](https://github.com/Azure/azure-functions-language-worker-protobuf/blob/3757ce8/src/proto/FunctionRpc.proto)의 `InvocationRequest`를 다시 봅니다.

```protobuf
message InvocationRequest {
  string invocation_id = 1;
  string function_id = 2;
  repeated ParameterBinding input_data = 3;
  map<string, TypedData> trigger_metadata = 4;
  RpcTraceContext trace_context = 5;
  RetryContext retry_context = 6;
}
```

`ScriptInvocationContext`의 필드를 protobuf 메시지로 변환하는 게 이 단계의 일입니다. 두 가지 비자명한 사실:

**a) 입력 데이터는 `ParameterBinding`의 배열입니다.**

```protobuf
message ParameterBinding {
  string name = 1;
  oneof rpc_data {
    TypedData data = 2;
    RpcSharedMemory rpc_shared_memory = 3;
  }
}
```

각 입력은 이름 + 데이터로 표현되고, 데이터는 직접 `TypedData`(string/json/bytes/http/...)로 들어가거나, 또는 **공유 메모리 영역의 메타데이터**(`RpcSharedMemory`)로만 들어갈 수 있습니다. 후자가 capability 협상의 결과입니다 — "shared memory data transfer"를 양쪽 다 지원하면, 큰 페이로드는 gRPC 메시지에 직접 싣지 않고 공유 메모리에 둔 뒤 그 위치만 알려줍니다. (3화에서 본 capability 교환의 실제 활용)

**b) 트레이스 컨텍스트는 W3C 표준을 그대로 옮깁니다.**

```protobuf
message RpcTraceContext {
  string trace_parent = 1;
  string trace_state = 2;
  map<string, string> attributes = 3;
}
```

호스트의 `Activity.Current?.Id`가 `trace_parent`로, `Activity.Current?.TraceStateString`이 `trace_state`로 들어갑니다. 워커 측 라이브러리(예: Application Insights SDK)는 이걸 받아 자기 컨텍스트를 호스트의 트레이스에 이어 붙입니다. 즉 **분산 트레이싱이 호스트-워커 경계에서 끊어지지 않습니다.**

---

## 5단계 — `GrpcWorkerChannel.SendInvocationRequest`

3화에서 본 [`GrpcWorkerChannel`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Channel/GrpcWorkerChannel.cs)이 다시 등장합니다. 이번엔 송신 측 역할입니다.

`GrpcWorkerChannel`은 워커 1대를 대표하는 객체입니다. Dispatcher가 "이 워커에 이 호출을 보내라"고 하면, `GrpcWorkerChannel`은 다음 일을 합니다.

1. `ScriptInvocationContext`를 `InvocationRequest`로 변환
2. 그 호출의 `TaskCompletionSource`를 **invocation_id 기반 인메모리 사전**에 등록 — 응답이 올 때 짝지을 수 있도록
3. `new StreamingMessage { InvocationRequest = invocationRequest }`를 만들어 `_outbound` writer 쪽으로 보낸다
4. [`FunctionRpcService`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Server/FunctionRpcService.cs)가 `TryGetGrpcChannels(workerId, out var inbound, out var outbound)`로 같은 워커의 채널 쌍을 잡아 두고, 그중 `outbound.Reader`를 읽어 실제 gRPC 스트림에 쓴다

여기서 중요한 점은 `SendInvocationRequest`가 **새 `request_id` GUID를 만들어 correlation key로 쓰는 경로가 아니라는 것**입니다. 이 메서드는 `InvocationRequest` payload를 그대로 `StreamingMessage`에 넣어 보냅니다. 응답 매칭의 핵심 키는 `InvocationRequest`에 이미 들어 있던 `invocation_id`입니다.

또 한 가지 중요한 점은 "공용 이벤트 버스"보다 **워커별 채널 쌍**이 실제 운반 경로라는 것입니다. `WorkerChannel` 생성자에서 워커 ID로 `TryGetGrpcChannels`를 호출해 inbound/outbound 채널을 받아 두고, `SendStreamingMessageAsync`는 `_outbound` writer에 직접 적습니다.

3번의 `invocation_id` ↔ `TaskCompletionSource` 사전은 비동기 응답 매칭의 핵심입니다. 응답이 순서 없이 돌아와도 같은 `invocation_id`로 정확히 짝을 맞출 수 있습니다.

---

## 6단계 — 워커 측에서의 일

워커는 자신의 gRPC 클라이언트로 `EventStream`을 듣고 있다가, `StreamingMessage`의 `oneof content == invocation_request`인 메시지를 발견하면 다음 일을 합니다.

1. `function_id`로 어느 함수인지 식별 (이미 `FunctionLoadRequest`로 로드해 둔 함수)
2. `input_data`를 언어 객체로 변환 (예: Node에서 `TypedData.json` → JS object, `TypedData.bytes` → Buffer)
3. `trigger_metadata`를 사용자 함수의 `context` 객체에 채움
4. 사용자 함수를 호출
5. 반환값을 `TypedData`로 직렬화해 `InvocationResponse.return_value`에 넣음
6. output binding 결과를 `output_data`에 넣음
7. `result.status = Success/Failure/Cancelled` + 예외가 있으면 `result.exception`에 채움
8. `StreamingMessage(invocation_response)`를 호스트로 회신

언어별 워커 구현은 다르지만(Node는 npm `@azure/functions`, Python은 `azure-functions-worker`, Java는 `azure-functions-java-worker` 등), 위의 8단계 자체는 모두 같습니다. **그게 단일 프로토콜의 의미입니다.**

이 글은 호스트 관점이라 워커 측 코드는 짚지 않습니다. 다만 워커 코드도 모두 `Azure/azure-functions-{nodejs|python|java|...}-worker`라는 이름으로 공개돼 있으니, 특정 언어 동작이 궁금하면 해당 저장소를 보면 됩니다.

---

## 7단계 — 응답을 받아 `TaskCompletionSource`를 완료

워커가 보낸 응답은 다음 경로를 거칩니다.

```
gRPC stream
  → FunctionRpcService.EventStream (호스트 측 핸들러)
  → workerId별 inbound Channel<InboundGrpcEvent>에 write
  → GrpcWorkerChannel / WorkerChannel의 inbound.Reader가 읽음
  → invocation_id로 TaskCompletionSource 조회
  → tcs.SetResult(ScriptInvocationResult)
  → Dispatcher가 await하던 Task가 깨어남
  → WorkerFunctionInvoker가 결과를 SDK에 반환
  → SDK가 트리거 처리 완료 (큐 메시지 삭제, HTTP 응답 송신 등)
```

이게 한 호출의 전체 일생입니다.

---

## 동시 호출 — 한 워커가 여러 개를 동시에 처리한다

여기서 중요한 사실 하나. **한 워커 프로세스는 동시에 여러 개의 invocation을 처리할 수 있습니다.**

위의 5단계에서 본 `invocation_id ↔ TaskCompletionSource` 사전이 그걸 가능하게 합니다. 호스트는 워커가 준비한 버퍼와 현재 워커 수를 바탕으로 호출을 흘려보내며, 인스턴스 내부에서 워커를 더 붙일지의 임계치는 `WorkerConcurrencyOptions` 같은 실제 옵션으로 제어됩니다.

하지만 **응답 메시지가 어떤 순서로 돌아올지는 보장되지 않습니다.** 호출 A를 먼저 보내고 B를 나중에 보냈더라도, B가 더 빨리 끝나면 응답 B가 먼저 옵니다. 그건 사전 매칭으로 자연스럽게 처리됩니다.

다만 **logging이나 같은 함수에 대한 일부 메시지 순서**는 지켜져야 할 때가 있습니다. 그래서 [`Channel/OrderedInvocationMessageDispatcher.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Channel/OrderedInvocationMessageDispatcher.cs)가 존재합니다 — invocation 단위로 메시지 순서를 보장하면서도 invocation 사이의 병렬성은 유지합니다.

![한 워커의 동시 호출 처리 구조](../../assets/azure-functions-deep-dive/04/04-02-concurrent-invocations-one-worker-handle.ko.png)

*한 워커의 동시 호출 처리 구조*
같은 `invocation_id`의 메시지들은 도착 순서대로 처리되지만, 서로 다른 `invocation_id`들은 병렬로 처리됩니다.

---

## 워커 동시성 — 호스트가 워커를 얼마나 바쁘게 만들지

[`WorkerConcurrencyManager.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/WorkerConcurrencyManager.cs)는 단순 invocation 개수 임계치가 아니라 `WorkerStatus.LatencyHistory`를 기반으로 overload를 판단하고, 필요하면 **워커 추가 생성**을 요청합니다. 즉 같은 함수 앱 안에서도 워커가 여러 개 떠 있을 수 있습니다 — 같은 인스턴스 안에 여러 개의 워커 프로세스가 존재할 수 있다는 뜻입니다.

[`WorkerChannelThrottleProvider.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/WorkerChannelThrottleProvider.cs)는 그 반대 방향 — 워커가 너무 바쁘면 호스트 측에서 추가 호출을 throttling합니다. 이 두 객체가 **인스턴스 내부의 호출 처리 능력**을 동적으로 조정합니다.

여기서 중요한 구분: **이건 인스턴스 내부의 워커 프로세스 수 조정**이지, **인스턴스 자체를 늘리는 것**(스케일아웃)이 아닙니다. 후자는 5화에서 다룹니다.

---

## HTTP 프록시 — gRPC를 우회하는 길

앞에서 구분한 두 메커니즘을 여기서 다시 정리하겠습니다. [`HttpFunctionInvocationDispatcher.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/HttpFunctionInvocationDispatcher.cs)는 factory가 선택하는 **HTTP worker/custom handler 경로**입니다. 반면 gRPC 워커의 HTTP proxying은 `WorkerChannel.SendInvocationRequest` 안에서 `IsHttpProxyingWorker && context.FunctionMetadata.IsHttpTriggerFunction()` 조건이 맞을 때 `_httpProxyService.StartForwarding(...)`를 호출하는 방식으로 붙습니다.

즉 HTTP 트리거라고 해서 자동으로 `HttpFunctionInvocationDispatcher`로 가는 것은 아닙니다. 일반적인 언어 워커의 HTTP 트리거는 여전히 `RpcFunctionInvocationDispatcher` 경로를 타되, 워커 capability가 있으면 HTTP 본문 전달만 우회합니다. 이때 흐름은 대략 다음과 같습니다.

1. 워커가 자기 프로세스 안에 HTTP 서버를 추가로 띄움
2. 호스트는 워커가 알려준 HTTP 엔드포인트로 **원본 HTTP 요청을 거의 그대로 프록시**
3. 워커는 사용자 함수에 HTTP 요청을 그대로 넘기고, 응답을 호스트에 HTTP 응답으로 돌려보냄

장점은 **큰 HTTP 본문(파일 업로드 등)을 protobuf로 직렬화하지 않는다**는 것입니다. 다만 제어 평면 자체가 완전히 바뀌는 것은 아닙니다. 호출 등록, invocation ID 관리, 최종 응답 매칭은 계속 같은 워커 채널과 dispatcher 흐름 안에서 움직입니다.

---

## 한 호출의 모든 것을 한 표에

| 단계 | 객체 | 역할 |
|---|---|---|
| 1 | WebJobs SDK 트리거 리스너 | 트리거 발화 감지 |
| 2 | `WorkerFunctionInvoker` | SDK가 사용자 코드를 호출하려 할 때 위임받음 |
| 3 | `IFunctionInvocationDispatcher` 구현체 | 호출을 받아 실제 운반 |
| 4 | `InvocationRequest` 빌더 | `ScriptInvocationContext`를 protobuf로 변환 |
| 5 | `GrpcWorkerChannel` | 워커 1대에 보냄, 응답 매칭용 사전 등록 |
| 6 | `FunctionRpcService` (gRPC) | 워커별 outbound 채널을 읽어 실제 스트림에 쓴다 |
| 7 | Worker process | 사용자 함수 실행, `InvocationResponse` 회신 |
| 8 | `FunctionRpcService` (gRPC) | 인바운드 메시지를 워커별 inbound 채널에 쓴다 |
| 9 | `OrderedInvocationMessageDispatcher` | invocation별 메시지 순서 보장 |
| 10 | `GrpcWorkerChannel` | invocation_id로 TCS 매칭, 결과 완료 |
| 11 | Dispatcher → Invoker → SDK | 결과 전파 |

---

## 이 글이 고정해 주는 것

이번 글까지 읽으면, 한 호출이 호스트를 통해 워커에 도달하고 응답이 돌아오는 전체 경로가 명확해졌을 겁니다. 여기서 붙잡아 둘 핵심은 transport가 달라져도, 호스트가 호출을 다루는 기본 골격은 dispatcher 추상화·`ScriptInvocationContext`·워커 채널의 correlation 경로로 일관된다는 점입니다.

---

이 글은 Azure Functions Deep Dive 시리즈 4화입니다. 1~3화에서 호스트 부팅, 워커 프로세스, gRPC 스트림의 뼈대를 세웠다면, 이번 화는 그 위를 실제 호출이 어떻게 지나가는지 따라가며 워커 채널 기반 상관관계 경로를 고정했습니다.

---

## Call Path Summary

- `WorkerFunctionInvoker.InvokeCore()` → `IFunctionInvocationDispatcher.InvokeAsync()` → `RpcFunctionInvocationDispatcher.InvokeAsync()` → `GrpcWorkerChannel.SendInvocationRequest()`
- `ScriptInvocationContext.ToRpcInvocationRequest()` → `new StreamingMessage { InvocationRequest = invocationRequest }` → worker-specific outbound channel → `FunctionRpcService.EventStream()`
- worker `InvocationResponse` → worker-specific inbound channel → invocation ID lookup in `WorkerChannel` → `TaskCompletionSource<ScriptInvocationResult>` 완료

---

## 운영 체크리스트

- [ ] 함수별 maxConcurrentRequests / batchSize 값을 워크로드에 맞춰 튜닝했다
- [ ] invocation timeout과 외부 호출 timeout의 관계를 정렬했다
- [ ] retry 정책과 poison queue 경로를 trigger 별로 정리했다
- [ ] invocation 실패 분류(transient vs permanent)에 대한 알림 정책을 정했다
- [ ] long-running invocation을 Durable Functions로 옮길 후보를 식별했다

<!-- toc:begin -->
## 시리즈 목차

- [호스트 부팅 — `WebJobsScriptHostService`부터 따라가기](./01-host-bootstrap.md)
- [Worker 프로세스 — 한 호스트에서 여러 언어 런타임이 같이 사는 법](./02-worker-process.md)
- [gRPC 이벤트 스트림 — 호스트와 워커는 무엇을 주고받는가](./03-grpc-event-stream.md)
- **Dispatcher와 Invocation — 함수 호출이 워커에 도달하기까지 (현재 글)**
- 스케일링 내부 동작 — Scale Controller, ScaleMonitor, 그리고 플랜별 차이 (예정)
- 콜드 스타트와 Placeholder Mode — 새 인스턴스가 만들어질 때 (예정)

<!-- toc:end -->

---

## 참고 자료

**호스트 코드 (commit `5e59423`)**
- [`IFunctionInvocationDispatcher.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/IFunctionInvocationDispatcher.cs)
- [`IFunctionInvocationDispatcherFactory.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/IFunctionInvocationDispatcherFactory.cs)
- [`FunctionInvocationDispatcherFactory.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/FunctionInvocationDispatcherFactory.cs)
- [`HttpFunctionInvocationDispatcher.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/HttpFunctionInvocationDispatcher.cs)
- [`WorkerFunctionInvoker.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/WorkerFunctionInvoker.cs)
- [`WorkerConcurrencyManager.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/WorkerConcurrencyManager.cs)
- [`WorkerChannelThrottleProvider.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/WorkerChannelThrottleProvider.cs)
- [`Channel/GrpcWorkerChannel.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Channel/GrpcWorkerChannel.cs)
- [`Channel/WorkerChannel.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Channel/WorkerChannel.cs)
- [`Channel/OrderedInvocationMessageDispatcher.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Channel/OrderedInvocationMessageDispatcher.cs)
- [`Server/FunctionRpcService.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Server/FunctionRpcService.cs)

**프로토콜**
- [`FunctionRpc.proto`](https://github.com/Azure/azure-functions-language-worker-protobuf/blob/3757ce8/src/proto/FunctionRpc.proto) — `InvocationRequest`, `InvocationResponse`, `ParameterBinding`, `RpcTraceContext`
