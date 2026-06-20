---
title: "바이브코딩을 위한 Azure Container Apps 심화 (1/6): ACA 아키텍처"
series: azure-aca-deep-dive
episode: 1
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureContainerApps심화
- ACA아키텍처
- Kubernetes
- AI코딩
seo_description: "바이브코딩을 위한 Azure Container Apps 심화 1편: ACA 아키텍처. ACA를 숨은 Kubernetes 위의 관리형 제품 표면으로 읽고 Environment, Revision, KEDA, Dapr, Envoy 경계를 이해합니다."
---

# 바이브코딩을 위한 Azure Container Apps 심화 (1/6): ACA 아키텍처

이 글은 바이브코딩을 위한 Azure Container Apps 심화 시리즈의 첫 번째 글입니다.

Azure Container Apps를 처음 보면 설명이 꽤 단순합니다. 컨테이너 이미지를 올리고, Ingress를 켜고, 필요하면 Dapr와 스케일 규칙을 붙이면 플랫폼 운영은 Microsoft가 맡는다는 이야기입니다. 하지만 운영에서 부딪히는 문제는 대부분 추상화 아래층에서 발생합니다. ACA는 Kubernetes를 지운 서비스가 아니라, Kubernetes 위에 관리형 제품 표면을 올린 서비스입니다. Environment·Revision·KEDA·Dapr·Envoy가 각각 어느 층에서 어떤 역할을 맡는지 이해해야 "새 Revision은 떴는데 왜 트래픽을 못 받는지", "스케일 규칙은 있는데 왜 Replica가 0에 머무는지", "Dapr를 켰는데 왜 localhost 호출만 성공하는지" 같은 질문을 빠르게 해결할 수 있습니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 ACA 운영 코드를 요청할 때 계층 구조를 명시하지 않으면, 포털 표면만 다루는 코드가 생성되어 실제 운영 문제를 진단하지 못하기 때문입니다.

> ACA 아키텍처의 핵심은 기능 이름이 아니라, Environment·Revision·KEDA·Dapr·Envoy가 어느 층에서 어떤 역할을 맡는지 이해하는 데 있습니다.

---

## 이 글에서 다룰 문제

- ACA는 정확히 어떤 추상화 위에 어떤 추상화를 올린 서비스일까요?
- AKS와 비교할 때 Microsoft가 대신 떠안는 운영 책임과 사용자가 여전히 이해해야 할 책임은 무엇일까요?
- Environment는 왜 단순한 상위 리소스가 아니라 실제 격리 경계일까요?
- 계층별 실패 신호는 어떻게 다를까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

ACA 아키텍처를 이해하면 AI에게 "ACA 5xx 장애 진단 시 Ingress 계층, Revision 상태, KEDA replica 수, Dapr sidecar 로그를 각각 확인하는 순서와 명령"을 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "ACA 앱이 5xx 에러 날 때 원인 찾는 방법?"
→ 앱 코드부터 의심하는 조언
→ 계층별 진단 순서 없음
→ KEDA, Dapr, Envoy 계층 구분 없음
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "ACA 5xx 장애 진단 순서를 계층별로 알려줘.
    1) Ingress 계층: FQDN 직접 curl 응답 코드 확인
    2) Revision 상태: az containerapp revision list로 active/inactive 확인
    3) KEDA 스케일: Log Analytics에서 replica 수 변화 확인
    4) Dapr sidecar: ContainerAppSystemLogs_CL에서 sidecar 에러 확인
    각 계층별 확인 명령을 순서대로 작성해줘"
→ 계층별 체계적 진단
→ 앱 코드가 아닌 플랫폼 계층부터 확인
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| ACA 문제를 항상 앱 코드 버그로 가정 | 계층별 실패 신호를 놓침 | Ingress → Revision → KEDA → Dapr 순서로 진단 |
| ACA를 AKS 대체재로 보고 kubectl 기대 | ACA는 K8s API를 직접 노출하지 않음 | az containerapp 명령과 Log Analytics로 진단 |
| Environment를 단순 그룹핑 상자로 이해 | 네트워크, 로그, Dapr 범위 공유 설계 오류 | Environment를 격리 경계로 이해하고 분리 기준 수립 |
| Dapr 장애를 앱 코드 문제로만 봄 | sidecar 프로세스 자체가 실패할 수 있음 | sidecar 로그를 앱 로그와 별개로 확인 |
| scale 결과와 traffic split 혼동 | 서로 다른 제어 루프인데 같이 디버깅 시도 | 트래픽은 Ingress, 스케일은 KEDA 계층으로 분리 |

## AI 협업 팁

ACA 아키텍처 관련 효과적인 AI 프롬프트 패턴:

1. **계층별 진단 요청**: "ACA 5xx 장애를 Ingress, Revision, KEDA, Dapr sidecar 계층별로 진단하는 명령 시퀀스 작성해줘"
2. **책임 경계 확인 요청**: "ACA에서 Microsoft가 관리하는 부분과 사용자가 설정해야 하는 부분의 경계를 표로 정리해줘"
3. **계층 지도 요청**: "ACA의 Environment, Container App, Revision, KEDA, Dapr, Envoy가 각각 어느 층에 속하는지 계층 구조도와 설명 작성해줘"

예시 프롬프트:
> "ACA 운영 장애 진단 플레이북을 작성해줘. Ingress 계층(FQDN curl), Revision 계층(az revision list), 스케일 계층(Log Analytics replica count), sidecar 계층(Dapr 로그) 순서로 각 계층의 진단 명령과 정상/비정상 판별 기준 포함."

## 운영 체크리스트

- [ ] ACA가 Kubernetes 위의 관리형 제품 표면임을 이해했는가?
- [ ] 계층별 실패 신호(Ingress vs Revision vs KEDA vs Dapr)를 구분할 수 있는가?
- [ ] Environment를 격리 경계로 이해하고 분리 기준을 수립했는가?
- [ ] kubectl 없이 az containerapp과 Log Analytics로 진단하는 방법을 알고 있는가?
- [ ] 다음 글에서 Environment 내부 구조를 이해할 준비가 됐는가?

## 처음 질문으로 돌아가기

ACA 아키텍처를 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. 계층별 진단 순서를 명시한 사람과 그렇지 않은 사람이 AI에게 받는 장애 대응 코드의 완성도는 크게 다릅니다.

## 정리

ACA 아키텍처는 바이브코딩을 위한 Azure Container Apps 심화 시리즈의 출발점입니다. ACA를 숨은 Kubernetes 위의 관리형 제품 표면으로 읽고, Environment·Revision·KEDA·Dapr·Envoy가 각각 다른 층에서 다른 역할을 맡는다는 계층 모델을 이해했습니다. 다음 글에서는 Environment 내부의 네트워크, 로그, Dapr 스코프 경계를 다룹니다.

## 참고 자료

- [Azure Container Apps overview](https://docs.microsoft.com/azure/container-apps/overview)
- [Container Apps internals](https://docs.microsoft.com/azure/container-apps/environment)
- [KEDA in Container Apps](https://docs.microsoft.com/azure/container-apps/scale-app)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aca-deep-dive/ko/01-aca-architecture)

---

<!-- toc:begin -->
## 시리즈 목차

- **바이브코딩을 위한 Azure Container Apps 심화 (1/6): ACA 아키텍처 (현재 글)**
- 바이브코딩을 위한 Azure Container Apps 심화 (2/6): Environment 내부
- 바이브코딩을 위한 Azure Container Apps 심화 (3/6): Revision과 트래픽 분할
- 바이브코딩을 위한 Azure Container Apps 심화 (4/6): ACA 안의 KEDA
- 바이브코딩을 위한 Azure Container Apps 심화 (5/6): Dapr 사이드카 내부
- 바이브코딩을 위한 Azure Container Apps 심화 (6/6): Envoy Ingress 경로
<!-- toc:end -->

Tags: 바이브코딩, AzureContainerApps심화, ACA아키텍처, AI코딩
