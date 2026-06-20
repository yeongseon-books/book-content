---
title: "바이브코딩을 위한 Azure Container Apps (5/7): 스케일링과 KEDA"
series: azure-aca-101
episode: 5
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureContainerApps
- KEDA
- ScaleToZero
- AI코딩
seo_description: "바이브코딩을 위한 Azure Container Apps 5편: 스케일링과 KEDA. 신호-규칙-범위 세 단계 선언형 흐름으로 KEDA scaler와 zero-to-N 스케일링을 이해합니다."
---

# 바이브코딩을 위한 Azure Container Apps (5/7): 스케일링과 KEDA

이 글은 바이브코딩을 위한 Azure Container Apps 시리즈의 5번째 글입니다.

ACA의 스케일링은 단순히 replica 수를 늘리는 기능이 아닙니다. 어떤 신호를 볼지, 그리고 0까지 내려갈 수 있게 할지를 정하는 순간 비용 정책과 지연 시간 정책도 함께 정해집니다. 스케일링은 세 단계 선언형 파이프라인으로 보면 단순해집니다. Signal(무엇을 볼지: HTTP 동시 요청 수, 큐 길이, CPU 사용률), Rule(그 신호를 어떻게 해석할지: scale-rule-type http, azure-servicebus, cpu), Bounds(min-replicas와 max-replicas 범위). 이 세 가지가 정해지면 나머지는 ACA가 처리합니다. ACA에는 AKS처럼 HPA를 직접 설치하지 않습니다. 같은 KEDA scaler가 ACA control plane 안에서 동작합니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 스케일링 설정 코드를 요청할 때 신호 종류와 min-replicas를 명시하지 않으면, 큐 worker를 HTTP 규칙에 묶어 메시지가 쌓여도 replica가 늘지 않는 코드가 생성되기 때문입니다.

> 스케일링의 핵심은 어떤 신호를 볼지(Signal), 어떻게 해석할지(Rule), 어디까지 허용할지(Bounds)를 선언하는 세 단계 구조를 이해하는 데 있습니다.

---

## 이 글에서 다룰 문제

- ACA는 어떤 신호를 보고 replica 수를 결정할까요?
- 내장 HTTP/TCP 규칙과 사용자 정의 KEDA scaler의 차이는 무엇일까요?
- min-replicas 0(scale-to-zero)는 언제 안전하고 언제 위험할까요?
- 큐 worker는 왜 HTTP 규칙이 아니라 KEDA scaler로 스케일해야 할까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

KEDA 스케일링을 이해하면 AI에게 "HTTP API는 동시 요청 10개 기준 HTTP 규칙으로 min 1 max 10, Service Bus worker는 메시지 큐 길이 기준 azure-servicebus scaler로 min 0 max 5로 설정하는 Bicep 코드"를 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "ACA 앱 자동 스케일링 설정해줘"
→ HTTP 규칙으로 모든 앱에 동일 설정
→ 큐 worker도 HTTP 규칙 적용
→ min-replicas 기본값으로 cold start 미고려
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "ACA 스케일링을 워크로드별로 설정해줘.
    1) HTTP API: --scale-rule-type http, 동시 요청 10개 기준, min 1 max 10
       (사용자 대면이라 min 1로 cold start 방지)
    2) Service Bus worker: --scale-rule-type azure-servicebus,
       큐 길이 5 기준, min 0 max 5
       (유휴 시 scale-to-zero로 비용 절약)"
→ 워크로드 특성에 맞는 신호 선택
→ cold start와 비용 트레이드오프 명시
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 큐 worker를 HTTP 규칙으로 스케일 | 큐 길이 증가해도 HTTP 신호 없어 replica 안 늘어남 | azure-servicebus 또는 kafka KEDA scaler 사용 |
| 사용자 대면 API에 min-replicas 0 | 첫 요청 cold start 1~5초 지연 | 사용자 대면 API는 min-replicas 1 이상 |
| max-replicas 미설정 | 트래픽 급증 시 무제한 scale out으로 비용 폭증 | max-replicas 명시 필수 |
| CPU 규칙 단독 사용 | 메트릭 수집 지연으로 반응 늦음 | HTTP/큐 규칙을 주 신호로, CPU는 보조 |
| scale-to-zero 후 cold start 미모니터링 | SLO 위반 파악 불가 | Log Analytics에서 replica=0 구간 확인 |

## AI 협업 팁

KEDA 스케일링 관련 효과적인 AI 프롬프트 패턴:

1. **HTTP 스케일 규칙 요청**: "ACA HTTP API에 동시 요청 10개 기준 scale 규칙, min 1 max 10으로 설정하는 az CLI 명령 작성해줘"
2. **Service Bus scaler 요청**: "Service Bus 큐 길이 5개 기준으로 worker를 scale하는 KEDA azure-servicebus 규칙 설정 명령 작성해줘"
3. **cost vs latency 분석 요청**: "min-replicas 0과 1의 비용 차이와 cold start 영향을 서비스 유형별로 비교해줘"

예시 프롬프트:
> "ACA 두 앱의 스케일링을 설정해줘. orders-api: HTTP scaler, concurrent 10, min 1 max 10. order-worker: azure-servicebus scaler, queueLength 5, min 0 max 5, connection string은 secret으로 참조."

## 운영 체크리스트

- [ ] 큐 worker에 적절한 KEDA scaler(azure-servicebus, kafka 등)를 설정했는가?
- [ ] 사용자 대면 API의 min-replicas가 1 이상인가?
- [ ] max-replicas를 명시해 비용 상한을 설정했는가?
- [ ] scale-to-zero 서비스의 cold start 영향을 모니터링하는가?
- [ ] 다음 글에서 Dapr 통합을 이해할 준비가 됐는가?

## 처음 질문으로 돌아가기

KEDA 스케일링을 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. 워크로드별 신호 종류와 min-replicas를 명시한 사람과 그렇지 않은 사람이 AI에게 받는 스케일링 설정 코드의 완성도는 크게 다릅니다.

## 정리

스케일링과 KEDA 편은 바이브코딩을 위한 Azure Container Apps에서 선언형 스케일링 모델을 이해하는 핵심 단계입니다. Signal-Rule-Bounds 세 단계 구조, HTTP와 KEDA scaler의 적합 워크로드 차이, scale-to-zero 트레이드오프를 이해했습니다. 다음 글에서는 Dapr 통합을 다룹니다.

## 참고 자료

- [Scale in Azure Container Apps](https://docs.microsoft.com/azure/container-apps/scale-app)
- [KEDA scalers in Container Apps](https://docs.microsoft.com/azure/container-apps/custom-scaling)
- [Azure Service Bus scaler](https://keda.sh/docs/scalers/azure-service-bus/)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aca-101/ko/05-scaling-with-keda)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure Container Apps (1/7): Azure Container Apps란?
- 바이브코딩을 위한 Azure Container Apps (2/7): Environment, Container App, Revision
- 바이브코딩을 위한 Azure Container Apps (3/7): 첫 배포하기
- 바이브코딩을 위한 Azure Container Apps (4/7): Ingress와 트래픽 분할
- **바이브코딩을 위한 Azure Container Apps (5/7): 스케일링과 KEDA (현재 글)**
- 바이브코딩을 위한 Azure Container Apps (6/7): Dapr 통합
- 바이브코딩을 위한 Azure Container Apps (7/7): 모니터링과 운영
<!-- toc:end -->

Tags: 바이브코딩, AzureContainerApps, KEDA, AI코딩
