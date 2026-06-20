---
title: "바이브코딩을 위한 Azure Functions 심화 (4/6): 디스패처와 호출"
series: azure-functions-deep-dive
episode: 4
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureFunctions심화
- Serverless
- AI코딩
seo_description: "바이브코딩을 위한 Azure Functions 심화 4편: 디스패처와 호출. WorkerFunctionInvoker → ScriptInvocationContext → InvocationRequest → invocation_id 상관관계 → TaskCompletionSource 응답 매칭 구조를 이해합니다."
---

# 바이브코딩을 위한 Azure Functions 심화 (4/6): 디스패처와 호출

이 글은 바이브코딩을 위한 Azure Functions 심화 시리즈의 네 번째 글입니다.

gRPC 스트림을 통해 InvocationRequest가 도착하면 어떤 일이 일어날까요? 함수 코드가 즉시 실행되는 것이 아니라, 여러 객체를 거쳐 실행 결과가 비동기적으로 돌아오는 과정이 진행됩니다. WorkerFunctionInvoker가 IFunctionInvocationDispatcher(기본 구현은 RpcFunctionInvocationDispatcher)에 위임합니다. Dispatcher는 ScriptInvocationContext를 만들고 그 안에 TaskCompletionSource를 포함시킵니다. InvocationRequest는 invocation_id를 가지고 gRPC를 통해 Worker로 전송됩니다. Worker에서 실행이 끝나면 InvocationResponse가 같은 invocation_id를 담아 돌아옵니다. Host는 이 invocation_id로 대기 중인 TaskCompletionSource를 찾아 TCS.SetResult()를 호출합니다. 이렇게 동시에 여러 호출이 in-flight 상태로 처리됩니다. HTTP 트리거가 HttpFunctionInvocationDispatcher를 자동으로 사용한다는 것은 오해이며, HttpFunctionInvocationDispatcher는 커스텀 핸들러 모드에서만 사용됩니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 Functions 호출 추적 코드를 요청할 때 invocation_id 상관관계 구조를 명시하지 않으면, 여러 동시 호출을 개별로 추적하지 못하는 불완전한 관측 설정이 생성되기 때문입니다.

> 디스패처와 호출의 핵심은 WorkerFunctionInvoker → ScriptInvocationContext(TaskCompletionSource 포함) → InvocationRequest(invocation_id) → gRPC → Worker 실행 → InvocationResponse(동일 invocation_id) → TCS.SetResult() 흐름을 이해하고, invocation_id가 동시 호출 추적의 키임을 아는 데 있습니다.

---

## 이 글에서 다룰 문제

- WorkerFunctionInvoker와 RpcFunctionInvocationDispatcher는 각각 어떤 역할을 할까요?
- ScriptInvocationContext와 TaskCompletionSource는 왜 함께 존재할까요?
- invocation_id는 어떻게 생성되고 어떻게 응답 매칭에 사용될까요?
- 동시에 여러 호출이 in-flight 상태일 때 응답 순서가 뒤바뀌어도 괜찮은 이유는 무엇일까요?
- HTTP 트리거가 HttpFunctionInvocationDispatcher를 사용하지 않는다면 언제 사용될까요?

디스패처와 호출 구조를 이해하면 AI에게 "Application Insights에서 invocation_id를 기반으로 함수 호출의 Host 디스패치 단계부터 Worker 실행 완료까지 전체 흐름을 추적하는 KQL 분산 추적 쿼리"를 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "Functions 함수 호출 추적 코드 작성해줘"
→ 함수명 기반 추적만 설정
→ invocation_id 상관관계 활용 없음
→ 동시 호출 구분 불가
→ HTTP 트리거에 커스텀 핸들러 디스패처 가정
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "Functions 함수 호출을 invocation_id 기반으로 추적해줘.
    1) Application Insights에서 invocation_id를 operation_Id로
       매핑해 분산 추적 활성화
    2) 동시 in-flight 호출 수 모니터링 KQL
    3) InvocationRequest 발송부터 InvocationResponse 수신까지
       구간별 지연 측정
    invocation_id = operation_Id 매핑 활용"
→ 동시 호출 개별 추적
→ 구간별 지연 진단 가능
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| HTTP 트리거 = HttpFunctionInvocationDispatcher 사용으로 가정 | HttpFunctionInvocationDispatcher는 커스텀 핸들러 모드 전용 | 일반 HTTP 트리거는 RpcFunctionInvocationDispatcher 사용 확인 |
| invocation_id를 단순 로그 레이블로만 활용 | invocation_id는 동시 호출의 응답 매칭 키, 분산 추적 상관관계 키 | Application Insights operation_Id와 invocation_id 매핑 활용 |
| 동시 호출을 순서대로 처리된다고 가정 | TCS 기반 비동기 매칭으로 응답 순서와 요청 순서가 다를 수 있음 | invocation_id로 요청-응답 쌍을 명시적으로 매칭 |
| 호출 실패를 Worker 오류로만 가정 | Dispatcher 단계 실패(ScriptInvocationContext 생성 실패)도 가능 | Host 디스패치 로그와 Worker 실행 로그를 분리해서 확인 |
| 함수 실행 시간 = 전체 지연으로 측정 | Host 디스패치 → gRPC 전송 → Worker 실행 → 응답 수신까지 각 구간이 있음 | Application Insights에서 구간별 duration 분리 측정 |

## AI 협업 팁

디스패처와 호출 관련 효과적인 AI 프롬프트 패턴:

1. **invocation_id 분산 추적 요청**: "Azure Functions Application Insights에서 invocation_id를 operation_Id로 활용해 함수 호출 전체 흐름을 추적하는 KQL 쿼리 작성해줘"
2. **동시 호출 모니터링 요청**: "Application Insights에서 Azure Functions의 동시 in-flight 호출 수를 1분 단위로 집계하는 KQL 쿼리 작성해줘"
3. **호출 구간 지연 진단 요청**: "Azure Functions 호출의 Host 디스패치 지연과 Worker 실행 지연을 Application Insights에서 분리해서 측정하는 KQL 쿼리 작성해줘"

예시 프롬프트:
> "Azure Functions 호출 추적 설정 작성해줘. 1) invocation_id를 Application Insights operation_Id로 연결하는 설정 2) 동시 in-flight 호출 수 모니터링 KQL 3) Host 디스패치 → Worker 실행 → 응답 수신 구간별 P95 지연 측정 KQL."

## 운영 체크리스트

- [ ] invocation_id를 Application Insights 분산 추적의 상관관계 키로 활용하는가?
- [ ] 동시 in-flight 호출 수를 모니터링하고 상한을 설정했는가?
- [ ] 호출 실패를 Host 디스패치 단계와 Worker 실행 단계로 구분해서 진단하는가?
- [ ] HTTP 트리거가 RpcFunctionInvocationDispatcher를 사용함을 이해하고 있는가?
- [ ] 다음 글에서 Scale Controller와 WorkerConcurrencyManager가 어떻게 인스턴스 수를 결정하는지 이해할 준비가 됐는가?

## 처음 질문으로 돌아가기

디스패처와 호출 구조를 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. invocation_id 상관관계를 이해한 사람과 그렇지 않은 사람이 AI에게 받는 호출 추적 코드의 완성도는 크게 다릅니다.

## 정리

디스패처와 호출 편은 바이브코딩을 위한 Azure Functions 심화에서 함수 실행의 실제 경로를 이해하는 핵심 단계입니다. WorkerFunctionInvoker → RpcFunctionInvocationDispatcher → ScriptInvocationContext(TCS) → InvocationRequest(invocation_id) → 응답 매칭 → TCS.SetResult() 흐름, invocation_id 기반 동시 호출 추적, HTTP 트리거와 커스텀 핸들러 모드의 디스패처 차이를 이해했습니다. 다음 글에서는 Scale Controller와 WorkerConcurrencyManager가 인스턴스 수를 결정하는 내부 구조를 다룹니다.

## 참고 자료

- [WorkerFunctionInvoker source (GitHub)](https://github.com/Azure/azure-functions-host/blob/dev/src/WebJobs.Script/Workers/Rpc/RpcFunctionInvocationDispatcher.cs)
- [Distributed tracing in Azure Functions](https://learn.microsoft.com/azure/azure-functions/functions-monitoring#distributed-tracing)
- [Azure Functions custom handlers](https://learn.microsoft.com/azure/azure-functions/functions-custom-handlers)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-functions-deep-dive/ko/04-dispatcher-and-invocation)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure Functions 심화 (1/6): 호스트 부팅
- 바이브코딩을 위한 Azure Functions 심화 (2/6): Worker 프로세스
- 바이브코딩을 위한 Azure Functions 심화 (3/6): gRPC 이벤트 스트림
- **바이브코딩을 위한 Azure Functions 심화 (4/6): 디스패처와 호출 (현재 글)**
- 바이브코딩을 위한 Azure Functions 심화 (5/6): 스케일링 내부 구조
- 바이브코딩을 위한 Azure Functions 심화 (6/6): 콜드 스타트와 플레이스홀더 모드
<!-- toc:end -->

Tags: 바이브코딩, AzureFunctions심화, Serverless, AI코딩
