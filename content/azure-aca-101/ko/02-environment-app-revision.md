---
title: "Azure Container Apps 101 (2/7): Environment, Container App, Revision — ACA in three words"
series: azure-aca-101
episode: 2
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
- Azure
- Container Apps
- Revision
- Environment
- Blue-Green
- Canary
last_reviewed: '2026-05-12'
seo_description: Environment는 "건물", Container App은 "사무실", Revision은 "그날의 자리 배치"입니다.
---

# Azure Container Apps 101 (2/7): Environment, Container App, Revision — ACA in three words

ACA에서는 Environment, Container App, Revision이라는 세 단어를 계속 만나게 됩니다. 이름은 비슷하게 들리지만 수명과 책임은 전혀 다르고, 그 차이가 배포 방식과 운영 습관을 결정합니다.

이 글은 Azure Container Apps 101 시리즈의 2번째 글입니다. 여기서는 운영자 관점에서 이 세 단어를 분명히 갈라 보겠습니다.

## 먼저 던지는 질문

- ACA의 세 가지 운영 단위인 Environment, Container App, Revision은 정확히 어떤 책임을 가질까요?
- 어떤 변경은 새 Revision을 만들고, 어떤 변경은 만들지 않을까요?
- Single Revision mode와 Multiple Revision mode는 무엇이 다르고, 각각 언제 맞을까요?

## 큰 그림

![Azure Container Apps 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-101/02/02-01-start-with-the-hierarchy.ko.png)

*Azure Container Apps 101 2장 흐름 개요*

이 그림에서는 Environment, Container App, Revision — ACA in three words를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> Environment, Container App, Revision — ACA in three words의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 이 글이 중요한가

ACA를 처음 만지면 포털과 CLI에 같은 세 단어가 반복해서 등장합니다. Environment, Container App, Revision. 이름은 비슷해 보여도 실제로는 수명, 가변성, 소유 범위가 모두 다릅니다.

이 셋을 헷갈리면 익숙한 사고가 바로 따라옵니다.

- 팀과 서비스마다 Environment를 따로 만들어 비용과 운영 부담이 폭증합니다
- "환경 변수만 바꿨는데요" 했지만 새 Revision이 생기고 트래픽이 잠깐 흔들립니다
- "롤백했습니다"라고 말했지만 실제로는 또 다른 새 Revision이 생겨 있습니다
- Single mode에서 canary를 시도했다가 새 버전에 트래픽 100%가 한 번에 넘어갑니다

이 글은 운영 관점에서 그 세 단어를 분리해 줍니다.

## 멘탈 모델

> Environment는 "건물", Container App은 "사무실", Revision은 "그날의 자리 배치"입니다.

건물(Environment)은 한 번 지으면 오래 갑니다. 공유 인프라, 예를 들면 VNet, 로그 목적지, Dapr 공통 설정은 이 수준에 놓입니다.

사무실(Container App)은 건물 안의 한 회사입니다. "orders API"나 "payments worker" 같은 서비스 정체성을 가지며, 시간이 흘러도 같은 이름과 엔드포인트를 유지합니다.

자리 배치(Revision)는 그 사무실의 특정 시점 스냅샷입니다. 의자 하나만 옮겨도 새 배치가 됩니다. 마음에 들지 않으면 어제 배치로 되돌아가면 됩니다.

## 계층부터 먼저 보기

Environment는 경계입니다. Container App은 논리적인 서비스입니다. Revision은 이미지와 설정의 불변 스냅샷입니다.

개수 관계는 다음과 같습니다.

- 하나의 Environment 안에 여러 Container App이 들어갈 수 있습니다.
- 하나의 Container App은 시간에 따라 여러 Revision을 가질 수 있습니다.
- 하나의 Revision은 정확히 하나의 이미지와 하나의 설정 집합에 묶입니다.

## 핵심 개념 1 — Environment

Environment는 ACA의 공유 경계입니다. 하나의 Environment 안에 있는 모든 앱은 아래를 공유합니다.

- 같은 VNet(네트워크 경계, 내부 통신 가능)
- 같은 Log Analytics workspace(로그 목적지)
- 같은 Dapr component 정의
- 같은 리전(리전마다 별도의 Environment가 필요합니다)

> Environment는 자주 만드는 리소스가 아닙니다. 팀, 환경(dev/staging/prod), 규제 경계 기준으로 묶어야 비용, 운영, 관측성을 모두 관리하기 쉽습니다.

## 핵심 개념 2 — Container App

Container App은 시간의 흐름을 가로질러 유지되는 서비스 정체성입니다. URL 엔드포인트, 이름, ingress 설정, secret은 이 수준에 있습니다.

Container App은 아래 요소를 소유합니다.

- 이미지 참조
- 환경 변수와 secret 참조
- Ingress(external / internal / disabled)
- CPU/메모리 리소스 제한
- 스케일 규칙(min/max replica, KEDA scaler)

이 속성 중 일부를 바꾸면 변경을 반영하기 위해 Container App이 자동으로 새 Revision을 만듭니다. 바로 다음 섹션에서 어떤 변경이 여기에 해당하는지 정리합니다.

## 핵심 개념 3 — Revision

Revision은 이미지 + 설정의 불변 스냅샷입니다. 한번 만들어진 Revision은 수정되지 않습니다. 변경을 적용하려면 새 Revision을 만들고, 그쪽으로 트래픽을 옮겨야 합니다.

- 0%–100% 사이의 트래픽 가중치를 받을 수 있습니다
- active/inactive 상태를 가집니다
- 트래픽을 이전 Revision으로 즉시 되돌릴 수 있는데, 이것이 rollback입니다
- "rollback"은 새 Revision을 만드는 작업이 아니라 기존 Revision 사이의 가중치를 조정하는 작업입니다

## Before / After

**Before — (team × service × stage)마다 Environment 하나**

```bash
az containerapp env create --name env-orders-dev ...
az containerapp env create --name env-orders-staging ...
az containerapp env create --name env-orders-prod ...
az containerapp env create --name env-payments-dev ...
# ... Environment count explodes
# Cost: separate Log Analytics workspace, separate VNet
# Ops: register Dapr components in each environment
```

**After — (team × stage)마다 Environment 하나**

```bash
az containerapp env create --name env-team-a-dev ...
az containerapp env create --name env-team-a-prod ...
# Place orders, payments, notifications inside one environment
az containerapp create --name orders --environment env-team-a-prod ...
az containerapp create --name payments --environment env-team-a-prod ...
az containerapp create --name notifications --environment env-team-a-prod ...
```

차이는 꽤 구체적입니다. 두 번째 구조에서는 같은 VNet 안에서 내부 호출이 자유롭고, 로그는 하나의 workspace로 모이며, Dapr component도 한 번만 등록하면 됩니다.

## 실습 — Revision이 실제로 어떻게 움직이는지 보기

### Step 1. Multiple revision mode로 Container App 만들기

```bash
RG=rg-aca-demo
ENV=aca-env-demo

az containerapp create \
  --name myapi \
  --resource-group $RG \
  --environment $ENV \
  --image mcr.microsoft.com/azuredocs/containerapps-helloworld:latest \
  --ingress external \
  --target-port 80 \
  --revisions-mode multiple
```

### Step 2. 새 이미지로 두 번째 Revision 만들기

```bash
az containerapp update \
  --name myapi \
  --resource-group $RG \
  --image myregistry.azurecr.io/myapi:v2 \
  --revision-suffix v2
```

### Step 3. 두 Revision 사이에 트래픽 나누기(canary)

```bash
az containerapp ingress traffic set \
  --name myapi \
  --resource-group $RG \
  --revision-weight myapi--<v1-suffix>=90 myapi--<v2-suffix>=10
```

### Step 4. 문제가 생기면 즉시 rollback 하기

```bash
az containerapp ingress traffic set \
  --name myapi \
  --resource-group $RG \
  --revision-weight myapi--<v1-suffix>=100 myapi--<v2-suffix>=0
```

핵심은 이것입니다. **rollback은 새 배포가 아니라 가중치 조정**입니다. 수 초 안에 끝납니다.

## 자주 하는 실수

### 실수 1. 서비스마다 Environment를 하나씩 만드는 것

위 Before 예시처럼 개수가 폭증합니다. 기본값은 팀 × 스테이지 기준으로 Environment를 나누는 것입니다.

### 실수 2. Single mode에서 canary를 하려는 것

Single revision mode에서는 새 Revision이 생기는 순간 트래픽 100%가 자동으로 넘어갑니다. Canary나 blue-green을 하려면 처음부터 `--revisions-mode multiple`이어야 합니다.

### 실수 3. rollback을 이전 이미지 재배포라고 생각하는 것

ACA에서 rollback은 이전 Revision의 가중치를 다시 100%로 올리는 일입니다. 새 배포도, 재빌드도, 이미지 푸시도 필요 없습니다. 같은 이유로 최근 Revision은 한동안 남겨 두는 편이 좋습니다.

### 실수 4. 환경 변수 수정은 무중단일 거라고 가정하는 것

환경 변수, 이미지 태그, 스케일 규칙 변경은 새 Revision을 만들고 그쪽으로 트래픽을 보냅니다. ingress가 라우팅을 갱신하는 동안 짧은 시작 지연이 생길 수 있습니다. 확실한 무중단을 원한다면 health probe와 startup probe를 따로 구성해야 합니다.

### 실수 5. inactive Revision을 너무 많이 남겨 두는 것

Inactive Revision 자체가 비싸지는 않지만, 포털과 CLI 목록이 금방 지저분해집니다. "최근 N개 유지" 같은 정책을 정하고 오래된 것은 주기적으로 비활성화하는 편이 좋습니다.

## 실무에서는 이렇게 생각한다

프로덕션에서 이 세 단어를 분리하는 일은 결국 변경의 blast radius를 분리하는 일입니다.

- **Environment 변경**은 드물어야 합니다. 일어나면 VNet, 리전, 로그 workspace 같은 큰 인프라 결정입니다.
- **Container App 변경**은 신중해야 합니다. 이름 변경이나 ingress 변경은 외부 URL을 바꿀 수 있습니다.
- **Revision 변경**은 자주 일어납니다. 배포마다 새 Revision이 생기는 것이 정상입니다.

건강한 ACA 운영은 이 비대칭을 지킵니다. Environment는 드물게, Container App은 가끔, Revision은 거의 매일 바뀝니다.

## 어떤 변경이 새 Revision을 만들까

다음 변경은 새 Revision을 만듭니다.

- 컨테이너 이미지 변경
- 환경 변수 추가, 수정, 삭제
- Secret 변경
- CPU/메모리 제한 변경
- 스케일 규칙 변경(min/max, KEDA scaler)
- Dapr 설정 변경

다음 변경은 새 Revision을 만들지 않습니다.

- 트래픽 가중치 조정(rollback이 여기에 해당합니다)
- Revision active/inactive 전환
- Container App 수준의 태그 변경

## 체크리스트

- [ ] Environment, Container App, Revision 사이의 1:N:N 관계를 직접 그릴 수 있습니다
- [ ] 새 Revision을 만드는 변경을 다섯 가지 이상 말할 수 있습니다
- [ ] 우리 서비스에 Single mode와 Multiple mode 중 무엇이 맞는지 고를 수 있습니다
- [ ] rollback이 재배포가 아니라 가중치 조정이라는 점을 알고 있습니다
- [ ] 서비스마다 Environment를 만들면 왜 안 되는지 설명할 수 있습니다

## 연습 문제

1. 아래 시나리오마다 변경 수준이 Environment, Container App, Revision 중 어디인지 구분해 보세요.
   - "orders API 이미지 태그를 v1.2.3에서 v1.2.4로 올린다"
   - "payments 서비스의 ingress를 internal에서 external로 바꾼다"
   - "팀이 staging 전체를 다른 리전으로 옮기기로 했다"
   - "프로덕션 트래픽의 5%를 새 버전으로 보낸다"
2. 위 Step 1-4를 따라 두 개의 Revision을 만들고 가중치를 50/50으로 나눠 보세요. 그런 다음 각 엔드포인트를 100번씩 호출해서 실제 분포를 측정해 보세요.

## 정리

- Environment는 공유 인프라이며, 드물게 만들어야 합니다.
- Container App은 시간을 가로질러 유지되는 서비스 정체성입니다.
- Revision은 이미지와 설정의 불변 스냅샷이며, 실제 배포 단위입니다.
- Single mode는 단순한 서비스에 맞고, canary나 blue-green에는 Multiple mode가 필요합니다.
- ACA에서 rollback은 가중치 조정이지 새 배포가 아닙니다. 수 초 안에 끝납니다.

다음 글에서는 이 모델을 손으로 다뤄 봅니다. Python/FastAPI 앱을 처음으로 ACA에 배포하고, Container App과 Revision이 실제로 만들어지는 과정을 단계별로 보겠습니다.

## 처음 질문으로 돌아가기

- **ACA의 세 가지 운영 단위인 Environment, Container App, Revision은 정확히 어떤 책임을 가질까요?**
  - 본문의 기준은 Environment, Container App, Revision — ACA in three words를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **어떤 변경은 새 Revision을 만들고, 어떤 변경은 만들지 않을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Single Revision mode와 Multiple Revision mode는 무엇이 다르고, 각각 언제 맞을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure Container Apps 101 (1/7): Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기](./01-what-is-aca.md)
- **Azure Container Apps 101 (2/7): Environment, Container App, Revision — ACA in three words (현재 글)**
- Azure Container Apps 101 (3/7): 첫 배포하기 — Python/FastAPI (예정)
- Azure Container Apps 101 (4/7): Ingress와 트래픽 분할 — revision 기반 배포 전략 (예정)
- Azure Container Apps 101 (5/7): 스케일링 — KEDA scaler와 zero-to-N (예정)
- Azure Container Apps 101 (6/7): Dapr 통합 — 사이드카로 얻는 것 (예정)
- Azure Container Apps 101 (7/7): 모니터링과 운영 — Log Analytics와 Application Insights (예정)

<!-- toc:end -->

---

## 참고 자료

### 공식 문서

- [Azure Container Apps environments — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/environment)
- [Update and deploy changes in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/revisions)
- [Manage revisions in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/revisions-manage)
- [Azure Container Apps overview — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/overview)

### 관련 시리즈

- [Azure App Service 101](../../azure-app-service-101/ko/01-what-is-app-service.md)
- [Azure AKS 101](../../azure-aks-101/ko/01-what-is-aks.md)
- [Azure Functions 101](../../azure-functions-101/ko/01-what-is-azure-functions.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aca-101/ko/02-environment-app-revision)

Tags: Azure, Container Apps, Serverless, Containers
