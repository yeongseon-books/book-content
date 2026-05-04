---
title: Environment·Container App·Revision — 세 단어로 보는 ACA
series: azure-aca-101
episode: 2
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
- Azure
- Container Apps
- Revision
- Environment
- Blue-Green
- Canary
last_reviewed: '2026-05-03'
---

# Environment·Container App·Revision — 세 단어로 보는 ACA

> Azure Container Apps 101 시리즈 (2/7)

---

## 이 글에서 배울 것

- ACA의 세 가지 운영 단위 — Environment, Container App, Revision의 정확한 책임 분담
- 어떤 변경이 새 Revision을 만들고, 어떤 변경은 같은 Revision 안에서 끝나는지
- Single Revision mode와 Multiple Revision mode의 차이와 각각의 적합한 상황
- Canary, Blue-Green, 즉시 rollback을 Revision 단위로 어떻게 운영하는지

## 이 글에서 답할 질문

- Environment, Container App, Revision은 각각 어떤 수명을 가지고 어떤 변경에 반응하는가?
- 어떤 변경이 새 Revision을 만들고, 어떤 변경은 기존 Revision 안에서 반영되는가?
- Single Revision mode와 Multiple Revision mode는 트래픽 처리가 어떻게 달라지는가?
- 한 Environment에 여러 Container App을 묶어야 할까, 서비스마다 따로 만들어야 할까?
- Revision 기반 rollback은 일반적인 Kubernetes rollback과 무엇이 다른가?

## 왜 중요한가

ACA를 처음 만지면 portal과 CLI에 같은 단어가 반복해서 등장합니다. Environment, Container App, Revision. 이름만 보면 비슷해 보이지만 실제로 셋은 **수명, 가변성, 책임**이 모두 다릅니다.

이 셋을 헷갈린 채로 운영을 시작하면 다음과 같은 사고가 자주 납니다.

- 한 팀의 service마다 Environment를 따로 만들어 비용·운영 부담이 폭증
- 환경변수만 바꿨는데 Revision이 새로 생겨 트래픽이 끊어짐
- "rollback 했다"고 말하지만 실제로는 새 Revision을 또 하나 더 만든 상태
- Single mode에서 canary 배포를 시도하다가 100% 트래픽이 새 버전으로 한 번에 넘어가는 경험

이 글은 그 헷갈림의 뿌리인 세 단어를 운영 관점으로 분해합니다.

## Mental Model

> Environment는 "건물", Container App은 "사무실", Revision은 "그날의 자리 배치"입니다.

건물(Environment)은 한 번 짓고 오래 씁니다. VNet, log destination, Dapr 공통 설정 같은 공용 인프라가 여기에 묶입니다.

사무실(Container App)은 건물 안의 한 회사입니다. "주문 API", "결제 worker" 같은 서비스 정체성을 가지며 시간이 흘러도 같은 이름과 endpoint를 유지합니다.

자리 배치(Revision)는 그 사무실의 특정 시점 스냅샷입니다. 의자 하나만 옮겨도 새 배치가 만들어지고, 마음에 안 들면 어제 배치로 돌아갈 수 있습니다.

## 계층 먼저 보기

Environment는 경계입니다. Container App은 논리 서비스입니다. Revision은 이미지와 설정의 불변 스냅샷입니다.

![Environment와 Container App와 Revision의 계층 관계](../../../assets/azure-aca-101/02/02-01-start-with-the-hierarchy.ko.png)

세 단어 사이의 cardinality는 다음과 같습니다.

- 한 Environment는 여러 Container App을 가질 수 있습니다.
- 한 Container App은 여러 Revision을 가질 수 있습니다.
- 한 Revision은 정확히 하나의 image, 하나의 설정 묶음에 묶입니다.

## 핵심 개념 1 — Environment

Environment는 ACA의 **공용 boundary**입니다. 한 Environment에 묶인 모든 app이 다음을 공유합니다.

- 같은 VNet (네트워크 boundary, internal traffic 가능)
- 같은 Log Analytics workspace (로그 destination)
- 같은 Dapr 공용 component 정의
- 같은 region (region별로 별도 Environment 필요)

> Environment는 자주 만들 대상이 아닙니다. **팀 단위**, **환경(dev/staging/prod) 단위**, 혹은 **regulatory boundary 단위**로 묶어야 비용·관리·observability 모두 쉽습니다.

## 핵심 개념 2 — Container App

Container App은 시간이 흘러도 살아남는 **서비스 정체성**입니다. URL endpoint, 이름, ingress 설정, secrets는 Container App 수준에 매여 있습니다.

Container App이 가지는 속성들:

- image reference
- 환경변수와 secret reference
- ingress (external / internal / disabled)
- CPU/memory 리소스 한도
- 스케일 규칙 (min/max replicas, KEDA scaler)

이 중 일부 속성을 바꾸면 Container App은 자동으로 **새 Revision**을 만들어 변경을 적용합니다. 다음 절에서 어떤 변경이 그렇게 동작하는지 정리합니다.

## 핵심 개념 3 — Revision

Revision은 **image + 설정의 불변 스냅샷**입니다. 한 번 생성된 Revision은 절대 수정되지 않습니다. 변경을 적용하려면 새 Revision을 만들고 트래픽을 옮기는 방식입니다.

- 트래픽 weight 대상이 될 수 있음 (0%~100%)
- 활성/비활성 상태를 가짐
- 이전 Revision으로 트래픽을 즉시 되돌릴 수 있음 → 그게 곧 rollback
- "rollback"이 새 Revision을 만들지 않음 → 기존 Revision의 weight만 조정

## Before / After

**Before — 환경별 Environment를 따로 만든 경우**

```bash
az containerapp env create --name env-orders-dev ...
az containerapp env create --name env-orders-staging ...
az containerapp env create --name env-orders-prod ...
az containerapp env create --name env-payments-dev ...
# ... 팀당 service당 환경당 분리 → Environment가 폭증
# 비용: Log Analytics workspace 분리, VNet 분리
# 관리: Dapr component를 각 환경마다 등록
```

**After — 환경 단위로만 묶은 경우**

```bash
az containerapp env create --name env-team-a-dev ...
az containerapp env create --name env-team-a-prod ...
# 한 환경 안에 orders, payments, notifications 모두 배치
az containerapp create --name orders --environment env-team-a-prod ...
az containerapp create --name payments --environment env-team-a-prod ...
az containerapp create --name notifications --environment env-team-a-prod ...
```

차이는 분명합니다. 후자는 같은 VNet 안에서 internal call이 자유롭고, 로그가 한 workspace에 모이며, Dapr component를 한 번만 등록합니다.

## 단계별 실습 — Revision의 동작 직접 확인하기

### Step 1. Container App을 Multiple revision mode로 생성

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

### Step 2. 새 image로 두 번째 Revision 생성

```bash
az containerapp update \
  --name myapi \
  --resource-group $RG \
  --image myregistry.azurecr.io/myapi:v2 \
  --revision-suffix v2
```

### Step 3. 두 Revision 사이에 트래픽 분할 (canary)

```bash
az containerapp ingress traffic set \
  --name myapi \
  --resource-group $RG \
  --revision-weight myapi--<v1-suffix>=90 myapi--<v2-suffix>=10
```

### Step 4. 문제가 생기면 즉시 rollback

```bash
az containerapp ingress traffic set \
  --name myapi \
  --resource-group $RG \
  --revision-weight myapi--<v1-suffix>=100 myapi--<v2-suffix>=0
```

여기서 핵심은 **rollback이 새 deploy가 아니라 weight 조정**이라는 점입니다. 수 초 안에 끝납니다.

## 자주 하는 실수

### 실수 1. service당 Environment를 만든다

위 Before 예시처럼 환경이 폭발합니다. Environment는 **팀과 환경(dev/staging/prod)을 곱한 만큼**만 만드는 것이 기본입니다.

### 실수 2. Single mode에서 canary를 시도한다

Single revision mode는 새 Revision이 생기는 순간 100% 트래픽이 자동으로 그곳으로 옮겨집니다. canary나 Blue-Green이 필요하면 반드시 `--revisions-mode multiple`로 시작해야 합니다.

### 실수 3. "rollback = 이전 image 다시 배포"라고 생각한다

ACA에서 rollback은 **이전 Revision의 weight를 100%로 올리는 것**입니다. 새 deployment를 돌리지 않고, build도 image push도 필요 없습니다. 같은 이유로 이전 Revision은 한동안 보존해두는 편이 좋습니다.

### 실수 4. 환경변수를 바꿨는데 무중단인 줄 안다

환경변수, image tag, scale 규칙 같은 변경은 새 Revision을 만들고 트래픽이 옮겨집니다. ingress가 routing을 바꾸는 동안 짧은 startup 지연이 발생할 수 있습니다. 무중단을 보장하려면 health probe와 startup probe를 분리해 설정합니다.

### 실수 5. 너무 많은 inactive Revision을 방치한다

Inactive Revision은 비용이 크지 않지만 portal/CLI list가 지저분해집니다. 운영 정책으로 "최근 N개만 보존"을 정해 정기적으로 deactivate합니다.

## 실무에서는 이렇게 생각한다

production 운영 관점에서 셋의 책임 분리는 곧 **변경 영향 범위**의 분리입니다.

- **Environment 변경**은 거의 없어야 합니다. 있으면 인프라 큰 의사결정 (VNet, region, Log workspace).
- **Container App 변경**은 신중히 합니다. 이름·ingress 변경은 외부 URL이 바뀔 수 있습니다.
- **Revision 변경**은 자주 합니다. 매 배포마다 새 Revision이 만들어지고, 그게 정상입니다.

좋은 ACA 운영은 "Environment는 거의 안 건드리고, Container App은 가끔, Revision은 매일"이라는 비대칭을 유지합니다.

## 어떤 변경이 새 Revision을 만드는가

다음 변경은 **새 Revision을 만듭니다**:

- Container image 변경
- 환경변수 추가/수정/삭제
- secret 변경
- CPU/memory 리소스 한도 변경
- scale 규칙 변경 (min/max, KEDA scaler)
- Dapr 설정 변경

다음 변경은 **새 Revision을 만들지 않습니다**:

- 트래픽 weight 조정 (rollback이 여기 해당)
- Revision 활성/비활성 토글
- Container App 수준의 tag 변경

## 체크리스트

- [ ] Environment, Container App, Revision의 cardinality (1:N:N)를 그릴 수 있다
- [ ] 어떤 변경이 새 Revision을 만드는지 5개 이상 나열할 수 있다
- [ ] Single mode와 Multiple mode 중 우리 service에 맞는 것을 고를 수 있다
- [ ] rollback이 image 재배포가 아닌 weight 조정임을 안다
- [ ] Environment를 service당 만들지 않는 이유를 설명할 수 있다

## 연습 문제

1. 다음 시나리오에서 Environment, Container App, Revision 중 어디 수준의 변경이 일어나는지 답해보세요.
   - "주문 API의 image tag를 v1.2.3에서 v1.2.4로 올림"
   - "결제 service의 ingress를 internal에서 external로 바꿈"
   - "팀이 staging 환경 전체를 다른 region으로 옮기기로 결정"
   - "프로덕션 트래픽의 5%를 새 버전으로 흘려보내기"
2. 본문 Step 1-4를 따라 직접 두 Revision을 만들고 weight를 50/50으로 분할해보세요. 그 다음 두 endpoint를 100번씩 호출해 실제 분포가 어떻게 나오는지 측정해봅니다.

## 정리

- Environment는 공용 인프라 boundary, 자주 만들지 않습니다.
- Container App은 시간을 가로지르는 service 정체성입니다.
- Revision은 image + 설정의 불변 스냅샷이고, 배포의 실제 단위입니다.
- Single mode는 단순한 service에, Multiple mode는 canary/Blue-Green이 필요한 service에 씁니다.
- ACA에서 rollback은 새 deployment가 아니라 **weight 조정**입니다 — 수 초 안에 끝납니다.

## 다음 글

다음 글에서는 이 모델을 직접 손에 익힙니다. Python/FastAPI app을 ACA에 처음으로 배포하면서 Container App과 Revision이 만들어지는 과정을 단계별로 따라갑니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기](./01-what-is-aca.md)
- **Environment·Container App·Revision — 세 단어로 보는 ACA (현재 글)**
- 첫 앱 배포하기 — Python/FastAPI (예정)
- Ingress와 트래픽 분할 — Revision 기반 배포 전략 (예정)
- 스케일링 — KEDA scaler와 0-to-N (예정)
- Dapr 통합 — 사이드카로 얻는 것 (예정)
- 모니터링과 운영 — Log Analytics와 Application Insights (예정)

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

Tags: Azure, Container Apps, Serverless, Containers
