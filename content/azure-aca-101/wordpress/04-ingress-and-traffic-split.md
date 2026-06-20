---
title: "바이브코딩을 위한 Azure Container Apps (4/7): Ingress와 트래픽 분할"
series: azure-aca-101
episode: 4
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureContainerApps
- Ingress
- 카나리배포
- AI코딩
seo_description: "바이브코딩을 위한 Azure Container Apps 4편: Ingress와 트래픽 분할. external/internal/disabled ingress 모드와 revision 기반 canary/blue-green 배포 전략을 이해합니다."
---

# 바이브코딩을 위한 Azure Container Apps (4/7): Ingress와 트래픽 분할

이 글은 바이브코딩을 위한 Azure Container Apps 시리즈의 4번째 글입니다.

Ingress와 트래픽 분할은 ACA에서 가장 중요한 운영 레버 두 개입니다. 설정 한 줄만 바뀌어도 외부 노출 방식과 배포 안전성이 함께 달라집니다. Ingress는 ACA의 "정문"이고, 트래픽 가중치는 "엘리베이터 배차 비율"입니다. 정문(Ingress)은 외부 방문자를 받을지(external), 같은 건물 사람만 받을지(internal), 아예 닫아 둘지(disabled)를 결정합니다. 정문을 통과한 뒤에는 엘리베이터(traffic split rule)가 설정된 비율에 따라 각 방문자를 어느 사무실(Revision)로 보낼지 결정합니다. ACA 관리형 ingress는 TLS 종료, external/internal 노출, Revision 라우팅을 담당하지만, 앱 수준 인증이나 WAF는 담당하지 않습니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 canary 배포 코드를 요청할 때 ingress mode와 revision mode를 명시하지 않으면, Single mode에서 canary를 시도해 트래픽이 100% 새 버전으로 한 번에 전환되는 코드가 생성되기 때문입니다.

> Ingress와 트래픽 분할의 핵심은 외부 노출 방식(ingress mode)과 버전 분배(traffic weight)가 독립적으로 운영된다는 사실을 이해하는 데 있습니다.

---

## 이 글에서 다룰 문제

- ACA 관리형 Ingress는 무엇을 책임지고 무엇은 책임지지 않을까요?
- external, internal, disabled ingress mode의 차이는 무엇일까요?
- Single mode와 Multiple mode는 트래픽 분배를 어떻게 다르게 동작시킬까요?
- revision 기반 canary와 blue-green 배포는 어떻게 구현할까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

Ingress와 트래픽 분할을 이해하면 AI에게 "Multiple mode에서 v2=90% v3=10% canary 설정 후 오류율 확인하고 100% 전환 또는 즉시 가중치 복귀하는 스크립트"를 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "ACA에서 canary 배포 구현해줘"
→ Single mode에서 새 Revision 배포
→ 트래픽 100% 즉시 전환
→ ingress mode 구분 없음
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "ACA Ingress와 트래픽 분할로 canary 배포를 구현해줘.
    1) --revisions-mode multiple 설정 확인
    2) external ingress, target-port 8000
    3) v3 배포 후 v2=90% v3=10% 가중치
    4) 10분 관찰 후 정상이면 v3=100%,
       문제면 v2=100% 즉시 복귀(az containerapp ingress traffic set)"
→ Single mode 함정 없는 안전한 canary
→ rollback은 가중치 조정으로 수 초 완료
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| external ingress 켰는데 접속 불가 | target-port가 컨테이너 실제 포트와 다름 | FastAPI는 --target-port 8000 명시 |
| Single mode에서 canary 시도 | 새 Revision 즉시 100% 트래픽 수신 | --revisions-mode multiple로 전환 |
| worker에 external ingress 설정 | 외부에 불필요한 엔드포인트 노출 | worker는 --ingress disabled 또는 internal |
| internal ingress 앱에 외부 접근 시도 | 같은 Environment 내부에서만 접근 가능 | 외부 노출 필요 시 external 설정 |
| rollback을 재배포로 구현 | 새 Revision 추가 생성 + 빌드 시간 낭비 | 이전 Revision에 가중치 100% 즉시 복귀 |

## AI 협업 팁

Ingress와 트래픽 분할 관련 효과적인 AI 프롬프트 패턴:

1. **ingress 설정 요청**: "FastAPI ACA 앱을 external ingress, target-port 8000, transport auto로 설정하는 az CLI 명령 작성해줘"
2. **canary 배포 요청**: "ACA Multiple mode에서 v3를 10%로 시작해 단계적으로 100%까지 올리는 트래픽 가중치 스크립트 작성해줘"
3. **blue-green 배포 요청**: "ACA에서 blue(v2)와 green(v3)을 동시에 active로 두고 synthetic 테스트 통과 후 100% 전환하는 스크립트 작성해줘"

예시 프롬프트:
> "ACA revision 기반 배포 전략을 구현해줘. Multiple mode 설정 → v3 배포(v2=90%, v3=10%) → 10분 관찰 → Log Analytics에서 5xx 확인 → 정상이면 v3=100%, 오류면 v2=100% 즉시 복귀."

## 운영 체크리스트

- [ ] worker와 internal 서비스에 external ingress가 잘못 붙어 있지 않은가?
- [ ] canary 배포 전에 Multiple revision mode를 확인했는가?
- [ ] rollback이 가중치 조정으로 구현됐는가 (재배포가 아닌가)?
- [ ] target-port가 컨테이너 실제 포트와 일치하는가?
- [ ] 다음 글에서 KEDA 스케일링을 이해할 준비가 됐는가?

## 처음 질문으로 돌아가기

Ingress와 트래픽 분할을 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. ingress mode와 revision mode를 명시한 사람과 그렇지 않은 사람이 AI에게 받는 canary 배포 코드의 안전성은 크게 다릅니다.

## 정리

Ingress와 트래픽 분할 편은 바이브코딩을 위한 Azure Container Apps에서 외부 노출 방식과 버전 분배 전략을 이해하는 핵심 단계입니다. external/internal/disabled ingress 모드의 차이와 revision 기반 canary/blue-green 배포를 이해했습니다. 다음 글에서는 KEDA scaler와 zero-to-N 스케일링을 다룹니다.

## 참고 자료

- [Ingress in Azure Container Apps](https://docs.microsoft.com/azure/container-apps/ingress-overview)
- [Traffic splitting in Azure Container Apps](https://docs.microsoft.com/azure/container-apps/traffic-splitting)
- [Blue-green deployment in Container Apps](https://docs.microsoft.com/azure/container-apps/blue-green-deployment)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aca-101/ko/04-ingress-and-traffic-split)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure Container Apps (1/7): Azure Container Apps란?
- 바이브코딩을 위한 Azure Container Apps (2/7): Environment, Container App, Revision
- 바이브코딩을 위한 Azure Container Apps (3/7): 첫 배포하기
- **바이브코딩을 위한 Azure Container Apps (4/7): Ingress와 트래픽 분할 (현재 글)**
- 바이브코딩을 위한 Azure Container Apps (5/7): 스케일링과 KEDA
- 바이브코딩을 위한 Azure Container Apps (6/7): Dapr 통합
- 바이브코딩을 위한 Azure Container Apps (7/7): 모니터링과 운영
<!-- toc:end -->

Tags: 바이브코딩, AzureContainerApps, Ingress, AI코딩
