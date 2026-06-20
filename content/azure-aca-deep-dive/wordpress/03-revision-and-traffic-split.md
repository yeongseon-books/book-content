---
title: "바이브코딩을 위한 Azure Container Apps 심화 (3/6): Revision과 트래픽 분할"
series: azure-aca-deep-dive
episode: 3
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureContainerApps심화
- Revision
- 트래픽분할
- AI코딩
seo_description: "바이브코딩을 위한 Azure Container Apps 심화 3편: Revision과 트래픽 분할. Revision이 불변 런타임 스냅샷이고 트래픽 분할이 Ingress 라우팅 정책임을 이해합니다."
---

# 바이브코딩을 위한 Azure Container Apps 심화 (3/6): Revision과 트래픽 분할

이 글은 바이브코딩을 위한 Azure Container Apps 심화 시리즈의 3번째 글입니다.

ACA의 배포 경험은 생각보다 부드럽습니다. 이미지를 바꾸면 새 Revision이 생기고, 필요하면 일부 트래픽만 새 버전으로 보낼 수 있으며, 문제가 있으면 다시 비율을 되돌리면 됩니다. 그 뒤에는 불변 스냅샷 생성, 활성 Revision 판정, Ingress 라우팅 상태 갱신이 이어집니다. ACA Revision 모델의 핵심은 이것입니다. Revision은 불변 런타임 스냅샷이고, 트래픽 분할은 앱 범위의 Ingress 라우팅 정책입니다. 즉 배포 단위와 노출 정책이 분리되어 있습니다. rollback은 재배포가 아니라 이전 Revision의 트래픽 가중치를 100%로 올리는 일입니다. 이 사실을 이해해야 canary와 blue-green이 "포털 마법"이 아니라 불변 Revision을 여러 개 살려 두고 Ingress가 가중치를 조절하는 구조로 보입니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 rollout 코드를 요청할 때 Revision 불변성과 label 라우팅의 차이를 명시하지 않으면, 테스트용 label URL과 main URL의 차이를 구분하지 못하는 코드가 생성되기 때문입니다.

> Revision과 트래픽 분할의 핵심은 Revision이 불변 스냅샷이고, rollback이 재배포가 아닌 가중치 이동임을 이해하는 데 있습니다.

---

## 이 글에서 다룰 문제

- 어떤 변경은 새 Revision을 만들고, 어떤 변경은 만들지 않을까요?
- Single revision mode와 Multiple revision mode는 운영상 무엇을 바꿀까요?
- label과 traffic weight는 각각 어떤 다른 라우팅 문제를 풀까요?
- rollback이 재배포가 아닌 이유는 무엇일까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

Revision과 트래픽 분할을 이해하면 AI에게 "Multiple mode에서 v3를 label URL로 먼저 테스트하고 확인 후 main URL traffic weight를 10% → 50% → 100%로 단계적으로 올리는 배포 스크립트"를 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "ACA 배포 rollback 어떻게 해?"
→ 이전 이미지로 재배포 시도
→ 새 Revision 추가 생성
→ 빌드 + 배포 시간 낭비
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "ACA Revision 기반 rollback을 구현해줘.
    현재 배포: v2=0%, v3=100%
    문제 발생 시 트래픽 가중치만 조정:
    v2=100%, v3=0% (재배포 없이 수 초 완료)
    label URL로 v3를 계속 접근 가능하게 유지"
→ 재배포 없이 Revision 가중치 이동
→ label URL로 v3 별도 테스트 가능
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| rollback을 이전 이미지 재배포로 구현 | 빌드 시간 + 새 Revision 추가 생성 | 이전 Revision 가중치 100% 복귀 |
| Single mode에서 canary 시도 | 새 Revision 생성 즉시 100% 전환 | Multiple mode로 전환 후 가중치 조정 |
| label URL과 main URL을 혼동 | label URL은 특정 Revision 고정, main URL은 가중치 분배 | 테스트는 label URL, 출시는 traffic weight |
| 환경 변수 변경을 무중단으로 가정 | 환경 변수도 새 Revision을 만듦 | health probe 설정으로 전환 시 지연 최소화 |
| inactive Revision 무한 누적 | 포털/CLI 목록 오염 | 최근 N개 유지 정책 수립 |

## AI 협업 팁

Revision과 트래픽 분할 관련 효과적인 AI 프롬프트 패턴:

1. **단계적 rollout 요청**: "ACA Multiple mode에서 v3를 label URL로 먼저 테스트 후 10%→50%→100%로 단계적 traffic weight 조정하는 스크립트 작성해줘"
2. **rollback 요청**: "v2 Revision을 100% 복귀시키는 az containerapp ingress traffic set 명령 작성해줘 (재배포 없음)"
3. **Revision 정리 요청**: "ACA 앱의 inactive Revision 목록을 조회하고 최근 3개를 제외한 나머지를 비활성화하는 스크립트 작성해줘"

예시 프롬프트:
> "ACA v3 배포 전략 스크립트를 작성해줘. 1) v3 Revision 배포(label=v3-test, traffic=0%) 2) label URL로 smoke test 3) 통과 시 10%→100% 단계적 전환 4) 실패 시 v2=100% 즉시 복귀(재배포 없음)."

## 운영 체크리스트

- [ ] canary/blue-green 배포 전에 Multiple revision mode를 확인했는가?
- [ ] rollback이 가중치 이동으로 구현됐는가 (재배포가 아닌가)?
- [ ] label URL로 특정 Revision을 테스트할 수 있는가?
- [ ] inactive Revision 정리 정책을 수립했는가?
- [ ] 다음 글에서 ACA 안의 KEDA 제어 루프를 이해할 준비가 됐는가?

## 처음 질문으로 돌아가기

Revision과 트래픽 분할을 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. Revision 불변성과 label/weight 차이를 명시한 사람과 그렇지 않은 사람이 AI에게 받는 rollout 스크립트의 완성도는 크게 다릅니다.

## 정리

Revision과 트래픽 분할 편은 바이브코딩을 위한 Azure Container Apps 심화에서 배포 단위와 노출 정책의 분리를 이해하는 핵심 단계입니다. Revision 불변성, label vs traffic weight 역할 차이, rollback이 재배포가 아닌 가중치 이동임을 이해했습니다. 다음 글에서는 ACA 안의 KEDA 스케일링 제어 루프를 다룹니다.

## 참고 자료

- [Revisions in Azure Container Apps](https://docs.microsoft.com/azure/container-apps/revisions)
- [Traffic splitting in Azure Container Apps](https://docs.microsoft.com/azure/container-apps/traffic-splitting)
- [Revision labels](https://docs.microsoft.com/azure/container-apps/revisions-manage)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aca-deep-dive/ko/03-revision-and-traffic-split)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure Container Apps 심화 (1/6): ACA 아키텍처
- 바이브코딩을 위한 Azure Container Apps 심화 (2/6): Environment 내부
- **바이브코딩을 위한 Azure Container Apps 심화 (3/6): Revision과 트래픽 분할 (현재 글)**
- 바이브코딩을 위한 Azure Container Apps 심화 (4/6): ACA 안의 KEDA
- 바이브코딩을 위한 Azure Container Apps 심화 (5/6): Dapr 사이드카 내부
- 바이브코딩을 위한 Azure Container Apps 심화 (6/6): Envoy Ingress 경로
<!-- toc:end -->

Tags: 바이브코딩, AzureContainerApps심화, Revision, AI코딩
