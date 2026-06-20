---
title: "바이브코딩을 위한 Azure Container Apps (2/7): Environment, Container App, Revision"
series: azure-aca-101
episode: 2
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureContainerApps
- Revision
- 트래픽분할
- AI코딩
seo_description: "바이브코딩을 위한 Azure Container Apps 2편: Environment는 건물, Container App은 사무실, Revision은 자리 배치입니다. 세 단위의 역할 차이와 rollback 원리를 이해합니다."
---

# 바이브코딩을 위한 Azure Container Apps (2/7): Environment, Container App, Revision

이 글은 바이브코딩을 위한 Azure Container Apps 시리즈의 2번째 글입니다.

ACA에서는 Environment, Container App, Revision이라는 세 단어를 계속 만나게 됩니다. 이름은 비슷하게 들리지만 수명과 책임은 전혀 다르고, 그 차이가 배포 방식과 운영 습관을 결정합니다. Environment는 "건물", Container App은 "사무실", Revision은 "그날의 자리 배치"입니다. 건물(Environment)은 한 번 지으면 오래 갑니다. 공유 인프라, 예를 들면 VNet, 로그 목적지, Dapr 공통 설정은 이 수준에 놓입니다. 사무실(Container App)은 서비스 정체성을 가지며 시간이 흘러도 같은 이름과 엔드포인트를 유지합니다. 자리 배치(Revision)는 그 사무실의 특정 시점 스냅샷입니다. ACA의 rollback은 이전 이미지를 재배포하는 것이 아니라 이전 Revision의 트래픽 가중치를 100%로 올리는 일입니다. 수 초 안에 끝납니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 canary 배포나 rollback 코드를 요청할 때 Single mode와 Multiple mode의 차이를 명시하지 않으면, Single mode에서 트래픽이 100% 새 버전으로 한 번에 전환되는 코드가 생성되기 때문입니다.

> Environment, Container App, Revision의 핵심은 어떤 변경이 새 Revision을 만드는지, rollback이 재배포가 아닌 가중치 조정임을 이해하는 데 있습니다.

---

## 이 글에서 다룰 문제

- Environment, Container App, Revision은 각각 어떤 책임을 가질까요?
- 어떤 변경은 새 Revision을 만들고, 어떤 변경은 만들지 않을까요?
- Single Revision mode와 Multiple Revision mode는 무엇이 다를까요?
- ACA rollback은 어떻게 동작하고 왜 빠를까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

이 세 단위의 역할을 이해하면 AI에게 "Multiple revision mode에서 v2 90%, v3 10%로 canary 배포 후 오류 없으면 100% 전환, 문제 시 v2로 즉시 가중치 복귀하는 배포 스크립트"를 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "ACA canary 배포 구현해줘"
→ Single mode 상태에서 canary 시도
→ 새 Revision에 트래픽 100% 즉시 전환
→ rollback 시 새 이미지 재배포 시도
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "ACA Multiple revision mode에서 canary 배포해줘.
    1) revisions-mode multiple로 앱 설정
    2) v3 배포 후 v2=90%, v3=10%로 가중치 설정
    3) 10분 관찰 후 v3=100% 전환
    4) 문제 시 v2=100%로 가중치 즉시 복귀(재배포 없음)"
→ 점진 배포와 즉시 rollback 구현
→ 재배포 없이 수 초 안에 복구 가능
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| Single mode에서 canary 시도 | 새 Revision 생성 즉시 트래픽 100% 전환 | 처음부터 --revisions-mode multiple 설정 |
| rollback을 이전 이미지 재배포로 이해 | 재배포 시간 + 새 Revision 추가 생성 | 이전 Revision 가중치를 100%로 올리는 것 |
| 환경 변수 수정이 무중단이라고 가정 | 환경 변수 변경도 새 Revision을 만듦 | health probe 설정으로 전환 시 지연 최소화 |
| 서비스마다 Environment를 따로 만들기 | 비용과 Dapr component 중복 등록 | 팀 × 스테이지 기준으로 Environment 분리 |
| inactive Revision을 무한 누적 | 포털과 CLI 목록 오염 | 최근 N개 유지 정책 설정 |

## AI 협업 팁

Revision 기반 배포 관련 효과적인 AI 프롬프트 패턴:

1. **Multiple mode 설정 요청**: "ACA 앱을 Multiple revision mode로 설정하는 az CLI 명령 작성해줘"
2. **canary 배포 요청**: "v2 90%, v3 10% 트래픽 가중치로 canary 배포 후 단계적으로 100% 전환하는 스크립트 작성해줘"
3. **rollback 요청**: "v2 Revision으로 즉시 트래픽 100% 복귀하는 az containerapp ingress traffic set 명령 작성해줘"

예시 프롬프트:
> "ACA Multiple revision mode canary 배포 스크립트를 작성해줘. v3 배포 → v2=90% v3=10% 설정 → 10분 관찰 → 정상 시 v3=100%, 오류 시 v2=100% 즉시 복귀. revision-weight 명령 포함."

## 운영 체크리스트

- [ ] 앱이 Multiple revision mode로 설정됐는가?
- [ ] rollback이 가중치 조정임을 이해하고 있는가?
- [ ] 환경 변수 변경도 새 Revision을 만든다는 것을 알고 있는가?
- [ ] Environment를 팀 × 스테이지 기준으로 분리했는가?
- [ ] 오래된 inactive Revision을 정기적으로 정리하는가?

## 처음 질문으로 돌아가기

Environment, Container App, Revision을 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. revision mode와 rollback 원리를 명시한 사람과 그렇지 않은 사람이 AI에게 받는 배포 스크립트의 안전성은 크게 다릅니다.

## 정리

Environment, Container App, Revision 편은 바이브코딩을 위한 Azure Container Apps에서 세 운영 단위의 역할 분리를 이해하는 핵심 단계입니다. 건물/사무실/자리 배치 비유로 수명과 책임을 구분했고, rollback이 재배포가 아닌 가중치 조정임을 이해했습니다. 다음 글에서는 실제 첫 배포 경로를 다룹니다.

## 참고 자료

- [Revisions in Azure Container Apps](https://docs.microsoft.com/azure/container-apps/revisions)
- [Traffic splitting in Azure Container Apps](https://docs.microsoft.com/azure/container-apps/traffic-splitting)
- [Managed environments overview](https://docs.microsoft.com/azure/container-apps/environment)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aca-101/ko/02-environment-app-revision)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure Container Apps (1/7): Azure Container Apps란?
- **바이브코딩을 위한 Azure Container Apps (2/7): Environment, Container App, Revision (현재 글)**
- 바이브코딩을 위한 Azure Container Apps (3/7): 첫 배포하기
- 바이브코딩을 위한 Azure Container Apps (4/7): Ingress와 트래픽 분할
- 바이브코딩을 위한 Azure Container Apps (5/7): 스케일링과 KEDA
- 바이브코딩을 위한 Azure Container Apps (6/7): Dapr 통합
- 바이브코딩을 위한 Azure Container Apps (7/7): 모니터링과 운영
<!-- toc:end -->

Tags: 바이브코딩, AzureContainerApps, Revision, AI코딩
