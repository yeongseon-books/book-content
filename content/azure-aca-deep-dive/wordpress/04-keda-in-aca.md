---
title: "바이브코딩을 위한 Azure Container Apps 심화 (4/6): ACA 안의 KEDA"
series: azure-aca-deep-dive
episode: 4
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureContainerApps심화
- KEDA
- 스케일링
- AI코딩
seo_description: "바이브코딩을 위한 Azure Container Apps 심화 4편: ACA 안의 KEDA. Scale Rule이 KEDA형 제어 루프로 어떻게 번역되고 scale과 traffic이 왜 다른 제어 루프인지 이해합니다."
---

# 바이브코딩을 위한 Azure Container Apps 심화 (4/6): ACA 안의 KEDA

이 글은 바이브코딩을 위한 Azure Container Apps 심화 시리즈의 4번째 글입니다.

Azure Container Apps의 스케일링 표면은 놀랄 만큼 짧습니다. minReplicas, maxReplicas, 그리고 HTTP·TCP·custom rule 몇 개만 설정하면 플랫폼이 나머지를 처리합니다. Microsoft 문서가 ACA scaling을 "KEDA-powered"라고 명시하는 이유가 여기에 있습니다. 사용자가 직접 ScaledObject나 HPA를 만들지는 않지만, 하위 제어 루프를 설명할 때는 KEDA가 가장 정확한 기준점이 되기 때문입니다. ACA 스케일링의 핵심은 이것입니다. scale rule은 scaler 그 자체가 아니라, 플랫폼이 KEDA형 autoscaling 동작으로 번역해야 하는 제품 설정입니다. 트래픽 분할과 스케일링은 자주 같은 이야기처럼 섞이지만 실제로는 완전히 다른 제어 루프입니다. 트래픽은 Ingress가 어디로 보낼지를 결정하고, 스케일은 선택된 Revision 뒤에 몇 개 replica를 둘지를 결정합니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 스케일링 설정 코드를 요청할 때 scale rule의 revision 범위와 cooldown을 명시하지 않으면, 트래픽 분할과 스케일링을 혼동하는 설계나 scale-to-zero cold start를 고려하지 않는 코드가 생성되기 때문입니다.

> ACA 안의 KEDA의 핵심은 scale rule이 revision-scope 설정이고, 트래픽 분할과 스케일링이 서로 다른 제어 루프임을 이해하는 데 있습니다.

---

## 이 글에서 다룰 문제

- ACA의 scale rule은 KEDA에서 어떤 형태의 제어 루프로 읽는 편이 가장 정확할까요?
- scale rule이 app-scope가 아니라 revision-scope에 속하는 이유는 무엇일까요?
- minReplicas 0이 가능하다는 사실은 스케일 모델을 어떻게 바꿀까요?
- scale-to-zero cold start는 어떤 경로로 발생할까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

ACA 안의 KEDA를 이해하면 AI에게 "HTTP API Revision에 concurrent 10 기준 HTTP scaler, min 1 max 10, Service Bus worker Revision에 queueLength 5 기준 azure-servicebus scaler, min 0 max 5를 각각 설정하고 scale 이벤트를 Log Analytics에서 확인하는 KQL 쿼리"를 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "ACA 스케일링 설정해줘"
→ 모든 앱에 동일한 HTTP rule 적용
→ cooldown 기본값 사용
→ traffic split과 scale 혼용
→ scale-to-zero cold start 미고려
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "ACA KEDA 스케일링을 워크로드별로 설정해줘.
    HTTP API: http scaler, concurrent 10, min 1(cold start 방지), max 10
    Service Bus worker: azure-servicebus scaler, queueLength 5,
    min 0(scale-to-zero 허용), max 5
    두 앱의 scale 이벤트를 Log Analytics에서 확인하는 KQL도 포함.
    트래픽 분할(Ingress 가중치)과 스케일(replica 수)은 별개임을 명시"
→ 워크로드별 신호 선택
→ scale과 traffic을 별개 제어 루프로 명확히 분리
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| traffic split과 scale을 같은 설정으로 혼동 | 서로 다른 제어 루프인데 함께 조정 시도 | Ingress 가중치와 KEDA scale rule을 분리해서 설정 |
| scale rule을 app 전체에 적용한다고 가정 | scale rule은 revision 범위에 속함 | 새 Revision 배포 시 scale rule을 다시 명시 |
| 사용자 대면 API에 min 0 설정 | scale-to-zero cold start 1~5초 지연 | 사용자 대면 API는 min 1 이상 |
| cooldown을 너무 짧게 설정 | replica 수 flapping, 비용 불안정 | scale out cooldown 5분, scale in cooldown 더 길게 |
| 외부 지표 scaler 즉시 반응 기대 | KEDA polling interval 존재, 즉시 반응 안 됨 | polling interval과 burst 대응 gap 계획 필요 |

## AI 협업 팁

ACA 안의 KEDA 관련 효과적인 AI 프롬프트 패턴:

1. **HTTP scaler 설정 요청**: "ACA HTTP API에 concurrent 10 기준 HTTP scaler, min 1 max 10으로 설정하는 Bicep 코드 작성해줘"
2. **Service Bus scaler 요청**: "ACA worker에 Service Bus 큐 길이 5 기준 KEDA azure-servicebus scaler, min 0 max 5 설정하는 az CLI 명령 작성해줘"
3. **scale 이벤트 모니터링 요청**: "Log Analytics에서 ACA replica 수 변화를 시간 순으로 조회하는 KQL 쿼리 작성해줘"

예시 프롬프트:
> "ACA 스케일링 설정과 모니터링을 작성해줘. orders-api: HTTP scaler min 1 max 10 concurrent 10. order-worker: azure-servicebus scaler min 0 max 5 queueLength 5. Log Analytics에서 두 앱의 replica 수 변화 KQL 포함. scale과 traffic split이 별개 제어 루프임을 코드 주석으로 명시."

## 운영 체크리스트

- [ ] scale rule과 traffic split을 별개 제어 루프로 인식하고 있는가?
- [ ] scale rule이 revision 범위임을 이해하고 새 Revision 배포 시 재명시하는가?
- [ ] 사용자 대면 API의 min-replicas가 1 이상인가?
- [ ] scale 이벤트를 Log Analytics에서 모니터링하는가?
- [ ] 다음 글에서 Dapr 사이드카 내부를 이해할 준비가 됐는가?

## 처음 질문으로 돌아가기

ACA 안의 KEDA를 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. scale rule의 revision 범위와 traffic split과의 분리를 명시한 사람과 그렇지 않은 사람이 AI에게 받는 스케일링 설정 코드의 완성도는 크게 다릅니다.

## 정리

ACA 안의 KEDA 편은 바이브코딩을 위한 Azure Container Apps 심화에서 스케일링 제어 루프를 이해하는 핵심 단계입니다. scale rule이 revision-scope 설정이고, 트래픽 분할과 스케일링이 서로 다른 제어 루프임을 이해했습니다. 다음 글에서는 Dapr 사이드카 내부 동작을 다룹니다.

## 참고 자료

- [Scale in Azure Container Apps](https://docs.microsoft.com/azure/container-apps/scale-app)
- [KEDA scalers overview](https://keda.sh/docs/scalers/)
- [Azure Service Bus KEDA scaler](https://keda.sh/docs/scalers/azure-service-bus/)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aca-deep-dive/ko/04-keda-in-aca)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure Container Apps 심화 (1/6): ACA 아키텍처
- 바이브코딩을 위한 Azure Container Apps 심화 (2/6): Environment 내부
- 바이브코딩을 위한 Azure Container Apps 심화 (3/6): Revision과 트래픽 분할
- **바이브코딩을 위한 Azure Container Apps 심화 (4/6): ACA 안의 KEDA (현재 글)**
- 바이브코딩을 위한 Azure Container Apps 심화 (5/6): Dapr 사이드카 내부
- 바이브코딩을 위한 Azure Container Apps 심화 (6/6): Envoy Ingress 경로
<!-- toc:end -->

Tags: 바이브코딩, AzureContainerApps심화, KEDA, AI코딩
