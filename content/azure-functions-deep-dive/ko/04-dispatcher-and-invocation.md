---
title: "Azure Functions Deep Dive (4/6): Dispatcher와 Invocation — 함수 호출이 워커에 도달하기까지"
series: azure-functions-deep-dive
episode: 4
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

# Azure Functions Deep Dive (4/6): Dispatcher와 Invocation — 함수 호출이 워커에 도달하기까지

gRPC 채널이 준비되었다고 해서 설명이 끝난 것은 아닙니다. 운영자와 애플리케이션 개발자가 결국 궁금해하는 지점은 따로 있습니다. 큐 메시지 하나, HTTP 요청 하나, 타이머 신호 하나가 어떻게 실제 사용자 함수 한 번의 실행으로 바뀌고, 그 결과는 어떤 상관관계 경로를 따라 다시 호스트로 돌아오는가입니다.

이 질문은 시스템 경계를 추상적으로 이해하는 수준을 넘어섭니다. 어느 객체가 invocation context를 만들고, 누가 그것을 워커 쪽 메시지로 바꾸며, 응답은 어떤 키로 다시 매칭되는지를 알아야 timeout, retry, long-running invocation, HTTP proxying 같은 운영 문제도 올바르게 읽을 수 있습니다.

이번 글은 [`Azure/azure-functions-host @ 5e59423`](https://github.com/Azure/azure-functions-host/tree/5e59423ba45491041d18224c3e72c168a4a5b7f7) 기준으로 `WorkerFunctionInvoker`, `IFunctionInvocationDispatcher`, `GrpcWorkerChannel`을 따라 한 번의 invocation 경로를 끝까지 추적합니다. 앞선 3화가 wire protocol 경계를 고정했다면, 이번 화는 그 위를 실제 호출이 어떻게 흐르는지 보여 줍니다.

이 글은 Azure Functions Deep Dive 시리즈의 네 번째 글입니다.

이제 트리거 이벤트가 워커 안의 사용자 함수 실행으로 바뀌는 구체적인 경로를 고정하겠습니다.

![Azure Functions Deep Dive 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-deep-dive/04/04-01-the-big-picture-from-trigger-to-worker.ko.png)
*Azure Functions Deep Dive 4장 흐름 개요*
> Dispatcher와 Invocation — 함수 호출이 워커에 도달하기까지의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- dispatcher는 한 번의 invocation을 어떤 단계로 나눠 처리할까요?
- invocation context는 어디서 만들어지고 누가 해제할까요?
- `maxConcurrentRequests`, `batchSize` 같은 동시성 제어는 어디에서 실제로 영향을 줄까요?

## 왜 이 글이 중요한가

Azure Functions는 다양한 트리거를 지원하지만, 워커로 넘어가는 순간에는 모두 같은 invocation 파이프라인으로 정규화됩니다. 이 사실을 모르면 큐 트리거와 HTTP 트리거가 전혀 다른 런타임처럼 보이지만, 실제로는 `WorkerFunctionInvoker`와 dispatcher 추상화 위에서 동일한 경로를 공유합니다. 차이는 trigger가 이벤트를 발생시키는 앞단에 있고, invocation 경로 자체는 훨씬 더 공통적입니다.

또한 한 번의 invocation은 동기 호출이 아닙니다. 호스트는 호출을 보낸 뒤 곧바로 `Task`를 들고 기다리고, 워커가 나중에 `InvocationResponse`를 돌려주면 그때 결과가 완성됩니다. 따라서 응답 상관관계 키가 무엇인지, 동시에 여러 invocation이 날아갈 때 순서 보장이 어디까지 되는지를 알아야 실제 지연과 오류를 분석할 수 있습니다.

마지막으로, 이번 글은 스케일링과 콜드 스타트 글을 읽기 위한 마지막 내부 경로입니다. 워커 수를 늘릴 때 실제로 무엇이 병렬화되는지, HTTP proxying이 gRPC를 완전히 대체하는지, 장시간 실행 함수를 Durable Functions로 분리해야 하는 이유가 모두 invocation 경로를 이해한 뒤에야 선명해집니다.

## 핵심 관점

Azure Functions invocation은 “트리거가 함수를 호출한다”는 한 문장보다 더 구체적인 경로를 가집니다. WebJobs SDK가 트리거 이벤트를 감지하면 `IFunctionInvoker` 구현이 실행되고, out-of-proc 경로에서는 `WorkerFunctionInvoker`가 직접 사용자 코드를 호출하는 대신 `IFunctionInvocationDispatcher`에 위임합니다. 이때 실제 운반체가 되는 것이 `ScriptInvocationContext`입니다.

이 context는 다시 protobuf `InvocationRequest`로 변환되어 특정 워커의 outbound 채널로 밀려나고, 응답은 `invocation_id`를 키로 같은 워커의 inbound 경로를 통해 되돌아옵니다. 즉 이번 글에서 봐야 할 것은 함수 호출 자체보다 **호스트가 호출을 표현하고 상관관계 짓는 방식**입니다.

> 이번 글의 핵심은 모든 트리거가 결국 같은 `InvocationRequest` 경로로 정규화되고, 그 왕복 상관관계가 워커별 채널과 `invocation_id` 위에서 유지된다는 사실입니다.

## 핵심 개념

### 먼저 전체 경로를 한 화면에 올려놓아야 합니다

이번 글이 다루는 경로는 아래 그림 하나로 요약할 수 있습니다.

트리거가 발화하면 WebJobs SDK가 그것을 함수 invocation으로 바꾸고, `WorkerFunctionInvoker`는 dispatcher에 위임합니다. dispatcher는 context를 protobuf 메시지로 만들어 워커 채널로 보내고, 워커 응답이 돌아오면 다시 원래 `Task`를 깨워 SDK가 후속 처리를 끝냅니다.

### 1단계: WebJobs SDK가 `IFunctionInvoker`를 호출합니다

Azure Functions 호스트는 WebJobs SDK 위에 올라가 있습니다. 큐 메시지 도착, HTTP 요청 유입, 타이머 만료 같은 사건은 모두 SDK의 trigger listener가 감지하고 함수 호출로 정규화합니다. 함수마다 `IFunctionInvoker` 구현이 하나씩 있으며, out-of-proc 모델에서 그 구현은 `WorkerFunctionInvoker`입니다.

이 객체의 역할은 분명합니다. 사용자 메서드를 직접 호출하는 대신, **`IFunctionInvocationDispatcher`에 실행을 위임**합니다. C# in-process와 달리 Node, Python, Java, isolated .NET 같은 경로에서는 실제 실행 주체가 워커 프로세스이기 때문입니다.

### 2단계: `IFunctionInvocationDispatcher`는 “호출을 어딘가로 보내는 능력”을 추상화합니다

`IFunctionInvocationDispatcher`는 호스트가 함수를 외부 실행 경계로 보내는 능력을 감싼 추상화입니다. 기본 경로는 `RpcFunctionInvocationDispatcher`이고, `httpWorkerOptions.Value.Description != null`일 때만 `HttpFunctionInvocationDispatcher`가 선택됩니다. 즉 분기 기준은 trigger 종류가 아니라 **HTTP worker / custom handler 모드가 설정되어 있는지 여부**입니다.

이 점은 자주 오해됩니다. HTTP trigger라고 해서 자동으로 `HttpFunctionInvocationDispatcher`가 되는 것이 아닙니다. 일반적인 language worker 경로에서는 여전히 `RpcFunctionInvocationDispatcher`가 사용되고, HTTP body 운반 방식만 별도로 proxying 될 수 있습니다.

### 3단계: `WorkerFunctionInvoker`는 `ScriptInvocationContext`를 만들어 dispatcher에 넘깁니다

dispatcher에 건네지는 실제 운반체는 `ScriptInvocationContext`입니다. `5e59423` 기준으로 이 객체에는 `FunctionMetadata`, `ExecutionContext`, 입력과 바인딩 데이터, trace context, 취소 토큰, 로거, 속성들, 그리고 가장 중요한 `TaskCompletionSource<ScriptInvocationResult>`가 들어 있습니다.

여기서 핵심은 마지막 필드입니다. dispatcher는 동기 응답을 기다리는 것이 아니라, 호출을 밀어 넣은 뒤 나중에 워커가 응답하면 완료될 `TaskCompletionSource`를 함께 등록합니다. 즉 한 워커 안에 여러 invocation이 동시에 in-flight 상태로 존재할 수 있고, 그것들을 구분하는 키가 `invocation_id`입니다.

정확성을 위해 하나 더 짚으면 `RetryContext`는 `ScriptInvocationContext`의 직접 필드가 아닙니다. 나중에 `ToRpcInvocationRequest()`가 protobuf 메시지를 만들 때 추가됩니다. 이런 세부 차이를 알아야 source-level 분석이 뭉개지지 않습니다.

### 4단계: `InvocationRequest`는 이 context를 protobuf로 굳힌 형태입니다

`InvocationRequest` 정의를 다시 보면 실제 wire payload가 무엇인지 바로 보입니다.

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

이 단계의 의미는 `ScriptInvocationContext`를 전송 가능한 protobuf 구조로 바꾸는 것입니다. 여기서 두 가지가 특히 중요합니다. 첫째, 입력은 `ParameterBinding` 배열로 직렬화됩니다.

```protobuf
message ParameterBinding {
  string name = 1;
  oneof rpc_data {
    TypedData data = 2;
    RpcSharedMemory rpc_shared_memory = 3;
  }
}
```

각 입력은 이름과 데이터 쌍이고, 데이터는 `TypedData`로 inline 직렬화되거나 `RpcSharedMemory`를 통해 shared memory 위치만 전달될 수 있습니다. 이것이 3화에서 본 capability negotiation이 실제 성능 최적화로 연결되는 지점입니다.

둘째, trace context는 W3C 형식으로 그대로 복사됩니다.

```protobuf
message RpcTraceContext {
  string trace_parent = 1;
  string trace_state = 2;
  map<string, string> attributes = 3;
}
```

호스트의 `Activity.Current?.Id`는 `trace_parent`가 되고, `TraceStateString`은 `trace_state`가 됩니다. 덕분에 worker-side telemetry도 같은 분산 추적 체인 위에 붙을 수 있습니다. 즉 host/worker 경계가 tracing 경계를 끊지 않습니다.

### 5단계: `GrpcWorkerChannel.SendInvocationRequest`가 워커별 outbound 채널로 보냅니다

실제 전송 시점에는 `GrpcWorkerChannel`이 다시 등장합니다. dispatcher가 “이 호출을 이 워커로 보내라”고 하면, 채널 객체는 `ScriptInvocationContext`를 `InvocationRequest`로 바꾸고, `invocation_id`를 키로 `TaskCompletionSource`를 메모리 딕셔너리에 등록한 뒤, `new StreamingMessage { InvocationRequest = invocationRequest }`를 해당 워커의 `_outbound` writer로 씁니다.

중요한 보정 하나가 있습니다. 상관관계 키는 새로 만든 `request_id`가 아닙니다. 실제 왕복 correlation은 이미 `InvocationRequest` 안에 들어 있는 `invocation_id`로 이뤄집니다. 이 점을 놓치면 응답 매칭 경로를 잘못 이해하게 됩니다.

`FunctionRpcService.EventStream()`는 같은 워커의 outbound 채널을 읽어 실제 gRPC 스트림으로 배출합니다. 따라서 transport는 generic bus가 아니라 **워커별 채널 쌍**입니다.

### 6단계: 워커는 언어별 구현으로 호출을 실행하지만 프로토콜 단계는 동일합니다

워커는 `oneof content == invocation_request`인 `StreamingMessage`를 받으면 `function_id`로 대상 함수를 찾고, `input_data`를 언어 네이티브 객체로 바꾸고, `trigger_metadata`로 context를 채운 뒤 사용자 함수를 호출합니다. 반환값은 `InvocationResponse.return_value`의 `TypedData`로 직렬화되고, output binding 결과는 `output_data`에 담기며, 성공/실패/취소 여부는 `result.status`에 들어갑니다.

언어별 구현체는 다르지만, 이 여덟 단계 자체는 공통입니다. 이것이 “프로토콜은 하나이고 워커 구현만 다르다”는 말의 실제 의미입니다.

### 7단계: 응답은 `invocation_id`로 매칭되어 원래 `Task`를 깨웁니다

워커 응답의 복귀 경로는 아래 텍스트 그대로 이해해도 됩니다.

```text
gRPC stream
  → FunctionRpcService.EventStream (host-side handler)
  → write to the worker-specific inbound Channel<InboundGrpcEvent>
  → GrpcWorkerChannel / WorkerChannel reads from inbound.Reader
  → look up the TaskCompletionSource by invocation_id
  → tcs.SetResult(ScriptInvocationResult)
  → the Task the dispatcher was awaiting wakes up
  → WorkerFunctionInvoker returns the result to the SDK
  → the SDK finishes trigger handling (delete the queue message, send the HTTP response, etc.)
```

즉 dispatcher가 기다리던 것은 네트워크 응답이 아니라 `TaskCompletionSource` 완결입니다. 워커에서 응답이 들어오면 `invocation_id`로 매칭해 그 `Task`를 완료시키고, 그제야 SDK가 큐 메시지 삭제나 HTTP 응답 마무리 같은 후속 처리를 끝냅니다.

### 한 워커는 여러 invocation을 동시에 처리할 수 있습니다

중요한 사실 하나는 **워커 하나가 동시에 여러 invocation을 처리할 수 있다**는 점입니다. `invocation_id ↔ TaskCompletionSource` 딕셔너리가 있기 때문에 호스트는 여러 호출을 동시에 날릴 수 있고, 응답은 순서대로 오지 않아도 됩니다. A를 먼저 보냈더라도 B가 빨리 끝나면 B 응답이 먼저 돌아올 수 있습니다.

![Concurrent invocation handling in one worker](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-deep-dive/04/04-02-concurrent-invocations-one-worker-handle.ko.png)

*Concurrent invocation handling in one worker*

다만 같은 invocation 내부의 메시지 순서는 필요합니다. 그래서 `OrderedInvocationMessageDispatcher.cs`가 존재합니다. 동일 `invocation_id` 안의 메시지는 도착 순서를 지키고, 다른 invocation끼리는 병렬성을 유지하는 구조입니다.

### worker concurrency와 HTTP proxying은 invocation 파이프라인을 완전히 바꾸지 않습니다

`WorkerConcurrencyManager`는 queue depth가 아니라 `WorkerStatus.LatencyHistory`를 보고 워커가 과부하인지 판단하고, 필요하면 **같은 인스턴스 안에 워커를 더 띄웁니다**. 이것은 외부 scale-out이 아니라 인스턴스 내부 병렬성 조절입니다. 반대로 `WorkerChannelThrottleProvider`는 워커가 너무 바쁠 때 호스트 쪽에서 추가 invocation을 조절합니다.

HTTP proxying도 같은 맥락에서 봐야 합니다. `HttpFunctionInvocationDispatcher`는 별도 dispatcher 경로이지만, 일반 gRPC worker 경로에서 HTTP proxying capability가 켜지면 dispatcher는 여전히 `RpcFunctionInvocationDispatcher`입니다. 바뀌는 것은 HTTP body 운반 방식뿐입니다. control plane과 invocation 등록, response completion은 여전히 같은 worker-channel 경로에 남아 있습니다.

### invocation 코드 경로를 파일 단위로 보면 디버깅 속도가 올라갑니다

호출 실패를 분석할 때 클래스 이름만 기억하면 헷갈립니다. 아래처럼 파일 단위로 책임을 고정하면 로그 한 줄을 즉시 코드 경로에 대응시킬 수 있습니다.

- `src/WebJobs.Script.Grpc/WorkerFunctionInvoker.cs`: `ScriptInvocationContext` 생성과 dispatcher 위임
- `src/WebJobs.Script.Grpc/IFunctionInvocationDispatcher.cs`: invocation 전송 추상화 계약
- `src/WebJobs.Script.Grpc/RpcFunctionInvocationDispatcher.cs`: 기본 gRPC worker 경로
- `src/WebJobs.Script.Grpc/Channel/GrpcWorkerChannel.cs`: `InvocationRequest` 작성, outbound 송신, 응답 매칭
- `src/WebJobs.Script.Grpc/Channel/WorkerChannel.cs`: 채널 공통 상태와 수명주기
- `src/WebJobs.Script.Grpc/Channel/OrderedInvocationMessageDispatcher.cs`: invocation 내 메시지 순서 보장

운영 문서에는 이 경로를 그대로 넣어 두는 것이 좋습니다. 그래야 온콜 엔지니어가 재현 시점에 "어느 레이어에서 멈췄는지"를 즉시 분기할 수 있습니다.

### invocation 단계별 프로파일링 출력 예시

한 번의 함수 호출 지연을 분해하려면 end-to-end 시간만 보면 부족합니다. 아래처럼 단계별 시간을 남기면 병목을 정확히 분리할 수 있습니다.

```text
[InvocationProfile]
InvocationId=72e5f8f7-...
CreateScriptInvocationContextMs=3
SerializeInvocationRequestMs=7
OutboundQueueWaitMs=21
WorkerExecutionMs=388
InboundDispatchMs=5
CompleteTaskCompletionSourceMs=1
TotalMs=425
```

이 예시에서 병목은 `WorkerExecutionMs`입니다. 반대로 `OutboundQueueWaitMs`가 길면 워커 포화 또는 throttle이 먼저 의심됩니다. 이런 숫자를 팀 공용 대시보드로 올려 두면 "플랫폼이 느린가, 함수 코드가 느린가" 논쟁을 데이터로 정리할 수 있습니다.

### timeout과 cancellation은 invocation 경계에서 명시적으로 보입니다

장시간 실행 호출에서 흔한 오해는 timeout이 "호스트 내부에서 조용히 처리된다"는 생각입니다. 실제로는 timeout/취소가 발생하면 `InvocationCancel` 메시지와 cancellation token 경로가 명시적으로 작동합니다. 즉 취소는 숨은 부작용이 아니라 프로토콜 이벤트입니다.

이 특성 때문에 함수 코드는 cancellation을 무시하면 안 됩니다. 워커가 취소 신호를 받았는데 사용자 코드가 계속 외부 API를 호출하면, 호출자에게는 실패가 반환됐는데 실제 부작용은 뒤늦게 발생하는 일관성 문제가 생길 수 있습니다.

### 동시성 제어 설정이 어디에 걸리는지 구체적으로 구분해야 합니다

`maxConcurrentRequests`, `batchSize`, 워커 수, channel throttle은 모두 "동시성"처럼 보이지만 작동 지점이 다릅니다.

| 설정/메커니즘 | 적용 지점 | 체감 효과 |
|---|---|---|
| `batchSize` | 트리거 listener가 이벤트를 읽어오는 앞단 | 한 번에 가져오는 작업량 조절 |
| `maxConcurrentRequests` | HTTP 요청 처리 동시성 | 동시 HTTP invocation 상한 |
| `FUNCTIONS_WORKER_PROCESS_COUNT` | 인스턴스 내부 워커 프로세스 수 | 병렬 실행 슬롯 증가 |
| `WorkerChannelThrottleProvider` | 워커 채널 송신 직전 | 과포화 시 추가 invocation 지연 |

이 구분이 없으면 잘못된 튜닝을 하게 됩니다. 예를 들어 큐 처리량 문제를 HTTP 동시성 설정으로 해결하려 하면 아무 변화가 없습니다. 설정은 "같은 단어"가 아니라 "같은 계층"에서 비교해야 합니다.

## 흔히 헷갈리는 지점

- **모든 trigger가 다른 invocation 메커니즘을 갖는 것은 아닙니다.** trigger는 앞단이 다를 뿐, 워커로 넘어갈 때는 공통 `InvocationRequest` 경로로 정규화됩니다.
- **`HttpFunctionInvocationDispatcher`는 HTTP trigger 일반 경로가 아닙니다.** HTTP worker / custom handler 설정이 있을 때만 선택됩니다.
- **응답 상관관계 키는 `request_id`가 아니라 `invocation_id`입니다.** 실제 round-trip 매칭은 `InvocationRequest`에 들어 있는 ID로 이뤄집니다.
- **워커 응답 순서는 보장되지 않습니다.** 여러 invocation이 동시에 in-flight일 수 있으므로 빠른 호출이 먼저 돌아올 수 있습니다.
- **worker concurrency는 외부 scale-out이 아닙니다.** 같은 인스턴스 안에서 워커 프로세스 수를 늘리는 메커니즘입니다.

## 운영 체크리스트

- [ ] 워크로드에 맞춰 함수별 `maxConcurrentRequests`와 `batchSize`를 점검했습니다.
- [ ] invocation timeout과 외부 의존성 timeout을 함께 맞췄습니다.
- [ ] trigger별 retry 정책과 poison-path를 문서화했습니다.
- [ ] invocation 실패를 일시 오류와 영구 오류로 분류하는 알림 정책을 정했습니다.
- [ ] 장시간 실행 호출을 Durable Functions 후보로 분류했습니다.

## 정리

이번 글은 트리거 이벤트가 실제 워커 호출로 변환되는 경로를 고정했습니다. WebJobs SDK가 `IFunctionInvoker`를 호출하면, out-of-proc 모델에서는 `WorkerFunctionInvoker`가 `ScriptInvocationContext`를 만들고 dispatcher에 넘깁니다. dispatcher는 그것을 `InvocationRequest`로 바꿔 워커별 채널에 밀어 넣고, 응답은 `invocation_id`를 키로 다시 원래 `Task`에 매칭됩니다.

이 경로를 알면 Azure Functions invocation이 동기 함수 호출이 아니라 비동기 메시지 왕복이라는 사실이 명확해집니다. timeout, retry, long-running invocation, concurrent invocations를 이해할 때도 “한 번의 함수 호출”이 아니라 “한 번의 요청-응답 상관관계”로 생각해야 정확합니다.

다음 글에서는 이제 인스턴스 하나 바깥으로 올라갑니다. 같은 invocation 파이프라인이 한 인스턴스 안에서 아무리 잘 돌아가도, 어느 시점에는 인스턴스 자체를 더 늘려야 합니다. 다음 편에서는 그 스케일아웃 결정을 누가 내리고, 호스트는 어떤 신호만 제공하는지, 그리고 인스턴스 내부 워커 동시성과 외부 scale controller를 어떻게 구분해야 하는지를 보겠습니다.

## 처음 질문으로 돌아가기

- **dispatcher는 한 번의 invocation을 어떤 단계로 나눠 처리할까요?**
  - 한 번의 invocation은 트리거 감지 뒤 `WorkerFunctionInvoker`가 `ScriptInvocationContext`를 만들고, dispatcher가 그것을 `InvocationRequest`로 직렬화해 워커별 outbound 채널로 보내는 단계로 나뉩니다. 이후 워커 응답은 inbound 채널로 돌아와 `invocation_id`로 원래 `TaskCompletionSource`를 깨우고, 마지막에 SDK가 큐 삭제나 HTTP 응답 같은 후속 처리를 마칩니다.
- **invocation context는 어디서 만들어지고 누가 해제할까요?**
  - invocation context는 out-of-proc 경로에서 `WorkerFunctionInvoker`가 만들고, 그 안에 함수 메타데이터, 입력 데이터, trace context, 취소 토큰, 결과를 기다릴 `TaskCompletionSource`까지 담깁니다. 해제도 별도 마법이 아니라 워커 응답이 `invocation_id`로 매칭되어 해당 `TaskCompletionSource`가 완료될 때 자연스럽게 호출 수명주기가 닫히는 방식입니다.
- **`maxConcurrentRequests`, `batchSize` 같은 동시성 제어는 어디에서 실제로 영향을 줄까요?**
  - `batchSize`는 트리거 listener 앞단에서 한 번에 읽어오는 작업량을 바꾸고, `maxConcurrentRequests`는 HTTP 요청 동시 처리 상한에 걸립니다. 반면 워커 수와 `WorkerChannelThrottleProvider`는 invocation이 워커 채널로 밀려나기 직전 병렬성을 조절하므로, 같은 동시성 설정처럼 보여도 실제 영향을 주는 계층이 서로 다릅니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure Functions Deep Dive (1/6): 호스트 부팅 — `WebJobsScriptHostService`부터 따라가기](./01-host-bootstrap.md)
- [Azure Functions Deep Dive (2/6): Worker 프로세스 — 한 호스트에서 여러 언어 런타임이 같이 사는 법](./02-worker-process.md)
- [Azure Functions Deep Dive (3/6): gRPC 이벤트 스트림 — 호스트와 워커는 무엇을 주고받는가](./03-grpc-event-stream.md)
- **Azure Functions Deep Dive (4/6): Dispatcher와 Invocation — 함수 호출이 워커에 도달하기까지 (현재 글)**
- Azure Functions Deep Dive (5/6): 스케일링 내부 동작 — Scale Controller, ScaleMonitor, 그리고 플랜별 차이 (예정)
- Azure Functions Deep Dive (6/6): 콜드 스타트와 Placeholder Mode — 새 인스턴스가 만들어질 때 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [`Azure/azure-functions-host @ 5e59423`](https://github.com/Azure/azure-functions-host/tree/5e59423ba45491041d18224c3e72c168a4a5b7f7)
- [`IFunctionInvocationDispatcher.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/IFunctionInvocationDispatcher.cs)
- [`FunctionInvocationDispatcherFactory.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/FunctionInvocationDispatcherFactory.cs)
- [`HttpFunctionInvocationDispatcher.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/HttpFunctionInvocationDispatcher.cs)
- [`WorkerFunctionInvoker.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/WorkerFunctionInvoker.cs)
- [`WorkerConcurrencyManager.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/WorkerConcurrencyManager.cs)
- [`WorkerChannelThrottleProvider.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/WorkerChannelThrottleProvider.cs)
- [`Channel/GrpcWorkerChannel.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Channel/GrpcWorkerChannel.cs)
- [`Channel/WorkerChannel.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Channel/WorkerChannel.cs)
- [`Channel/OrderedInvocationMessageDispatcher.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Channel/OrderedInvocationMessageDispatcher.cs)
- [`Server/FunctionRpcService.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/Server/FunctionRpcService.cs)
- [FunctionRpc.proto](https://github.com/Azure/azure-functions-language-worker-protobuf/blob/3757ce8/src/proto/FunctionRpc.proto)

### 관련 시리즈
- [Azure Functions 101 — Host와 Worker](../../azure-functions-101/ko/03-host-and-worker.md)
- [Azure Functions 101 — 스케일링과 콜드 스타트](../../azure-functions-101/ko/06-scaling-and-cold-start.md)
- [Azure App Service Deep Dive — App Service 플랫폼 아키텍처](../../azure-app-service-deep-dive/ko/01-platform-architecture.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-functions-deep-dive/ko/04-dispatcher-and-invocation)

Tags: Azure Functions, Serverless, Distributed Systems, gRPC
