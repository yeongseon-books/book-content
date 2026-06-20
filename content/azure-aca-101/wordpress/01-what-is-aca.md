---
title: "바이브코딩을 위한 Azure Container Apps (1/7): Azure Container Apps란?"
series: azure-aca-101
episode: 1
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureContainerApps
- KEDA
- 컨테이너
- AI코딩
seo_description: "바이브코딩을 위한 Azure Container Apps 1편: Azure Container Apps란? ACA가 App Service, AKS, Functions 사이 어디에 위치하는지, 어떤 워크로드에 맞는지 이해합니다."
---

# 바이브코딩을 위한 Azure Container Apps (1/7): Azure Container Apps란?

이 글은 바이브코딩을 위한 Azure Container Apps 시리즈의 첫 번째 글입니다.

Azure Container Apps를 처음 보면 App Service와 AKS 사이 어딘가를 메우는 서비스처럼 보입니다. 이 서비스를 정확히 이해하려면 플랫폼이 무엇을 추상화하고, 무엇은 여전히 사용자 책임으로 남기는지부터 잡아야 합니다. ACA는 "컨테이너용 App Service"라는 비유로 가장 빠르게 이해할 수 있습니다. App Service가 코드나 zip을 받아 ingress, scaling, slot이 연결된 웹 앱으로 바꿔 주듯, ACA는 컨테이너 이미지를 받아 비슷한 일을 해 줍니다. 차이는 입력이 컨테이너 이미지라는 점이고, 스케일러가 KEDA라서 0까지 내려갈 수 있다는 사실입니다. AKS가 "직접 운전하는 차"라면 ACA는 "택시를 부르는 것"에 가깝습니다. 목적지(이미지)와 몇 가지 선호사항(스케일 규칙, ingress)만 정하면 클러스터는 시야 밖에 머뭅니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 ACA 설정 코드를 요청할 때 워크로드 특성과 서비스 위치를 명시하지 않으면, AKS 수준의 복잡한 설정이나 App Service 패턴을 그대로 가져오는 코드가 생성되기 때문입니다.

> Azure Container Apps의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 추상화하고 어떤 신호를 남길지 정하는 데 있습니다.

---

## 이 글에서 다룰 문제

- Azure Container Apps(ACA)는 App Service, AKS, Functions와 무엇이 다를까요?
- ACA의 핵심 구성 요소인 Environment, Container App, Revision은 각각 어떤 역할을 할까요?
- 어떤 워크로드는 ACA에 잘 맞고, 어떤 워크로드는 다른 서비스에 두는 편이 나을까요?
- scale-to-zero는 언제 켜야 하고 언제 꺼야 할까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

ACA의 위치와 적합 워크로드를 이해하면 AI에게 "HTTP API와 큐 worker 조합에서 ACA Environment 하나에 두 Container App을 만들고 worker는 ingress disabled, API만 external ingress로 설정하는 Bicep 코드"를 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "컨테이너 앱을 Azure에 배포해줘"
→ AKS 클러스터 생성 + kubectl apply 흐름
→ Ingress Controller, cert-manager 직접 설치
→ ACA 없이 K8s 전체 운영 부담
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "FastAPI 컨테이너를 ACA에 배포해줘.
    Environment 하나에 API와 worker를 같이 두고
    API는 external ingress(port 8000),
    worker는 ingress disabled,
    min-replicas 1로 설정하는 az CLI 명령 작성해줘"
→ ACA 단일 명령으로 HTTPS + 스케일링 자동 구성
→ 클러스터 운영 부담 없음
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| ACA를 AKS 대체재로 보고 CRD, DaemonSet 요구 | ACA는 K8s 일부만 노출하는 서비스 | K8s 네이티브 기능 필요 시 AKS 선택 |
| scale-to-zero를 사용자 대면 API에 적용 | cold start 1~5초로 첫 요청 지연 | 사용자 대면 API는 min-replicas 1 이상 |
| 서비스마다 Environment를 하나씩 만들기 | VNet, 로그, Dapr 설정 중복으로 비용 폭증 | 팀 × 스테이지 기준으로 Environment 분리 |
| worker에 external ingress 설정 | 외부에 불필요한 엔드포인트 노출 | worker는 ingress disabled 또는 internal |
| 첫날부터 Dapr 활성화 | 학습 곡선 + 불필요한 복잡도 | pub/sub, state store 필요 시점에 도입 |

## AI 협업 팁

ACA 기본 설정 관련 효과적인 AI 프롬프트 패턴:

1. **Environment + App 생성 요청**: "ACA Environment를 만들고 FastAPI 컨테이너를 external ingress(port 8000), min-replicas 1, max-replicas 5로 배포하는 az CLI 명령 작성해줘"
2. **워크로드 배치 요청**: "API와 큐 worker를 같은 ACA Environment에 넣되, API는 external ingress, worker는 ingress disabled로 설정하는 Bicep 작성해줘"
3. **플랫폼 선택 판단 요청**: "K8s 운영 인력이 없고 HTTP API + 큐 worker 구성인데 ACA vs AKS 선택 기준을 설명해줘"

예시 프롬프트:
> "ACA에 최소 프로덕션 구성을 만들어줘. Log Analytics 연결된 Environment, FastAPI API(external ingress, min 1 replica), Service Bus consumer worker(ingress disabled, scale-to-zero 허용)를 Bicep으로 작성해줘."

## 운영 체크리스트

- [ ] ACA가 App Service, AKS, Functions 중 어느 위치인지 이해했는가?
- [ ] Environment를 팀 × 스테이지 기준으로 나눴는가?
- [ ] 사용자 대면 API에 min-replicas 1 이상을 설정했는가?
- [ ] worker에 external ingress가 잘못 붙어 있지 않은가?
- [ ] scale-to-zero를 쓰는 서비스의 cold start 영향을 고려했는가?

## 처음 질문으로 돌아가기

ACA의 위치와 적합 워크로드를 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. 워크로드 특성과 Environment 구조를 명시한 사람과 그렇지 않은 사람이 AI에게 받는 컨테이너 배포 코드의 완성도는 크게 다릅니다.

## 정리

Azure Container Apps란? 편은 바이브코딩을 위한 Azure Container Apps 시리즈의 시작 단계입니다. ACA가 App Service와 AKS 사이 어디에 있는지, Environment/Container App/Revision의 역할 분리, 워크로드 적합성을 이해했습니다. 다음 글에서는 Environment, Container App, Revision 세 구성 요소를 더 깊이 다룹니다.

## 참고 자료

- [Azure Container Apps overview](https://docs.microsoft.com/azure/container-apps/overview)
- [Compare container options in Azure](https://docs.microsoft.com/azure/container-apps/compare-options)
- [az containerapp CLI reference](https://docs.microsoft.com/cli/azure/containerapp)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aca-101/ko/01-what-is-aca)

---

<!-- toc:begin -->
## 시리즈 목차

- **바이브코딩을 위한 Azure Container Apps (1/7): Azure Container Apps란? (현재 글)**
- 바이브코딩을 위한 Azure Container Apps (2/7): Environment, Container App, Revision
- 바이브코딩을 위한 Azure Container Apps (3/7): 첫 배포하기
- 바이브코딩을 위한 Azure Container Apps (4/7): Ingress와 트래픽 분할
- 바이브코딩을 위한 Azure Container Apps (5/7): 스케일링과 KEDA
- 바이브코딩을 위한 Azure Container Apps (6/7): Dapr 통합
- 바이브코딩을 위한 Azure Container Apps (7/7): 모니터링과 운영
<!-- toc:end -->

Tags: 바이브코딩, AzureContainerApps, KEDA, AI코딩
