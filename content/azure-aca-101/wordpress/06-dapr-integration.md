---
title: "바이브코딩을 위한 Azure Container Apps (6/7): Dapr 통합"
series: azure-aca-101
episode: 6
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureContainerApps
- Dapr
- 사이드카
- AI코딩
seo_description: "바이브코딩을 위한 Azure Container Apps 6편: Dapr 통합. App 수준 설정과 Environment 수준 컴포넌트를 분리해서 이해하면 Dapr가 단순해집니다."
---

# 바이브코딩을 위한 Azure Container Apps (6/7): Dapr 통합

이 글은 바이브코딩을 위한 Azure Container Apps 시리즈의 6번째 글입니다.

Dapr는 마이크로서비스에서 반복되는 배관 작업을 많이 줄여 주지만, 아키텍처의 트레이드오프 자체를 지워 주지는 않습니다. Dapr를 이해하는 핵심은 App 수준 설정과 Environment 수준 컴포넌트를 분리해서 보는 데 있습니다. 앱은 `localhost:3500`의 Dapr 사이드카에 말하고, 사이드카가 실제 백엔드(Service Bus, Redis, Key Vault 등)와 통신합니다. ACA에서 Dapr가 특히 매력적인 이유는 런타임 설치 비용이 0이기 때문입니다. AKS에서는 Helm chart를 설치하고 Dapr control plane을 직접 운영해야 합니다. ACA에서는 그 control plane을 플랫폼이 관리합니다. 앱에 `--enable-dapr true`만 주면 사이드카가 자동으로 주입됩니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 Dapr 설정 코드를 요청할 때 App 수준과 Environment 수준을 구분하지 않으면, component를 앱 설정에 하드코딩하거나 pub/sub 연결이 되지 않는 코드가 생성되기 때문입니다.

> Dapr 통합의 핵심은 App 수준(--enable-dapr, --dapr-app-id, --dapr-app-port)과 Environment 수준(component 등록)의 역할 분리를 이해하는 데 있습니다.

---

## 이 글에서 다룰 문제

- Dapr 사이드카는 ACA 컨테이너 안의 어디에 붙고, 앱은 어떤 엔드포인트를 호출할까요?
- App 수준 설정과 Environment 수준 component는 왜 분리될까요?
- Service invocation, Pub/Sub, State store, Secret store는 각각 어떤 문제를 해결할까요?
- "첫날부터 Dapr를 켜는 것"이 왜 자주 안티패턴으로 언급될까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

Dapr 통합을 이해하면 AI에게 "orders-api에 Dapr 활성화(app-id orders-api, app-port 8000), Environment에 Service Bus pub/sub component 등록, orders-api에서 dapr publish로 메시지 발행하는 코드"를 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "ACA에서 두 서비스가 통신하게 해줘"
→ Service Bus SDK 직접 구현
→ Dapr component 등록 없음
→ App 수준과 Environment 수준 설정 혼재
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "ACA Dapr pub/sub을 설정해줘.
    1) Environment에 Service Bus pub/sub component 등록
       (--dapr-component-type pubsub.azure.servicebus)
    2) orders-api: --enable-dapr true, --dapr-app-id orders-api, --dapr-app-port 8000
    3) order-worker: --enable-dapr true, --dapr-app-id order-worker
    4) orders-api에서 dapr HTTP로 메시지 발행하는 FastAPI 코드
    5) order-worker에서 구독 처리하는 FastAPI 엔드포인트"
→ App 수준과 Environment 수준 분리 설정
→ SDK 없이 Dapr API로 브로커 추상화
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 첫날부터 Dapr 전체 기능 도입 | 학습 곡선 + 불필요한 복잡도 추가 | 단순 HTTP 통신에는 Dapr 없이 시작 |
| component를 앱 설정에 직접 하드코딩 | Environment 수준 공유 불가 | az containerapp env dapr-component set으로 Environment에 등록 |
| dapr-app-port 누락 | Dapr가 앱으로 콜백할 포트를 모름 | --dapr-app-port를 앱 실제 포트로 명시 |
| Secret store 없이 component 자격증명 하드코딩 | 보안 위험 | Dapr Secret store로 자격증명 참조 |
| service invocation에 직접 HTTP URL 사용 | Dapr가 제공하는 재시도, 트레이스 누락 | localhost:3500/v1.0/invoke/{appId}/method/{methodName} 사용 |

## AI 협업 팁

Dapr 통합 관련 효과적인 AI 프롬프트 패턴:

1. **App Dapr 활성화 요청**: "ACA 앱에 Dapr를 활성화하고 app-id와 app-port를 설정하는 az CLI 명령 작성해줘"
2. **pub/sub component 등록 요청**: "ACA Environment에 Service Bus pub/sub component를 등록하는 az containerapp env dapr-component set 명령 작성해줘"
3. **service invocation 코드 요청**: "FastAPI에서 Dapr service invocation으로 다른 ACA 앱을 호출하는 코드를 localhost:3500 Dapr API로 작성해줘"

예시 프롬프트:
> "ACA Dapr pub/sub 설정을 처음부터 작성해줘. Environment에 servicebus component 등록 → orders-api에 Dapr 활성화 → FastAPI에서 POST /orders 수신 시 Dapr publish로 order-created 토픽에 발행하는 코드 포함."

## 운영 체크리스트

- [ ] Dapr component를 Environment 수준에 등록했는가?
- [ ] 각 앱에 --dapr-app-id와 --dapr-app-port를 명시했는가?
- [ ] component 자격증명을 Secret store로 참조하는가?
- [ ] 단순 HTTP 통신에만 service invocation을 쓰고 불필요하게 확장하지 않았는가?
- [ ] 다음 글에서 모니터링과 운영을 이해할 준비가 됐는가?

## 처음 질문으로 돌아가기

Dapr 통합을 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. App 수준과 Environment 수준 설정을 분리해 명시한 사람과 그렇지 않은 사람이 AI에게 받는 Dapr 설정 코드의 완성도는 크게 다릅니다.

## 정리

Dapr 통합 편은 바이브코딩을 위한 Azure Container Apps에서 마이크로서비스 배관 작업을 플랫폼에 위임하는 방법을 이해하는 핵심 단계입니다. App 수준 설정과 Environment 수준 component의 역할 분리, 네 가지 핵심 구성요소(service invocation, pub/sub, state store, secret store)를 이해했습니다. 다음 글에서는 모니터링과 운영을 다룹니다.

## 참고 자료

- [Dapr integration in Azure Container Apps](https://docs.microsoft.com/azure/container-apps/dapr-overview)
- [Dapr components in Container Apps](https://docs.microsoft.com/azure/container-apps/dapr-component-connection)
- [Dapr service invocation](https://docs.dapr.io/developing-applications/building-blocks/service-invocation/)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aca-101/ko/06-dapr-integration)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure Container Apps (1/7): Azure Container Apps란?
- 바이브코딩을 위한 Azure Container Apps (2/7): Environment, Container App, Revision
- 바이브코딩을 위한 Azure Container Apps (3/7): 첫 배포하기
- 바이브코딩을 위한 Azure Container Apps (4/7): Ingress와 트래픽 분할
- 바이브코딩을 위한 Azure Container Apps (5/7): 스케일링과 KEDA
- **바이브코딩을 위한 Azure Container Apps (6/7): Dapr 통합 (현재 글)**
- 바이브코딩을 위한 Azure Container Apps (7/7): 모니터링과 운영
<!-- toc:end -->

Tags: 바이브코딩, AzureContainerApps, Dapr, AI코딩
