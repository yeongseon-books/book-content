---
title: "Azure Container Apps 101 (1/7): Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기"
series: azure-aca-101
episode: 1
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
- Serverless
- KEDA
- Dapr
- Containers
last_reviewed: '2026-05-12'
seo_description: ACA는 "컨테이너용 App Service"라는 비유로 가장 빠르게 이해할 수 있습니다.
---

# Azure Container Apps 101 (1/7): Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기

처음 Azure Container Apps를 보면 App Service와 AKS 사이 어딘가를 메우는 서비스처럼 보입니다. 이 서비스를 제대로 쓰려면 플랫폼이 무엇을 추상화하고, 무엇은 여전히 사용자의 책임으로 남기는지부터 명확히 잡아야 합니다.

이 글은 Azure Container Apps 101 시리즈의 첫 번째 글입니다. 여기서는 ACA를 Azure 컨테이너 서비스 지도 위에 올려놓고, 어떤 워크로드에 가장 잘 맞는지부터 정리합니다.

## 먼저 던지는 질문

- Azure Container Apps(ACA)는 다른 Azure 컨테이너 서비스(App Service, AKS, Functions)와 무엇이 다를까요?
- ACA의 세 가지 핵심 구성 요소인 Environment, Container App, Revision은 각각 어떤 역할을 할까요?
- 어떤 워크로드는 ACA에 잘 맞고, 어떤 워크로드는 다른 서비스에 두는 편이 나을까요?

## 큰 그림

![Azure Container Apps 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-101/01/01-01-the-big-picture-one-aca-environment-at-a.ko.png)

*Azure Container Apps 101 1장 흐름 개요*

이 그림에서는 Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 이 글이 중요한가

컨테이너 하나 만드는 일은 누구나 할 수 있습니다. 노트북에서도 잘 뜹니다. 어려운 지점은 그다음부터입니다.

> 어디에서 실행할지. HTTPS는 누가 끝낼지. 트래픽이 0일 때 비용을 어떻게 멈출지. 누가 스케일할지. 로그와 트레이스는 어디에 쌓일지.

이 질문의 답은 모두 플랫폼 선택에 묶여 있습니다. AKS는 완전한 자유를 주지만 클러스터를 직접 운영해야 합니다. App Service는 편리하지만 사이드카나 KEDA 스타일 스케일링은 어색합니다. Functions는 짧은 이벤트 핸들러에 최적화되어 있어서 장시간 실행되는 컨테이너에는 맞지 않습니다.

ACA는 정확히 그 사이의 빈 공간을 노립니다. 컨테이너는 직접 가져오되, 클러스터 운영은 Microsoft에 맡기는 모델입니다.

## 멘탈 모델

> ACA는 "컨테이너용 App Service"입니다.

App Service가 코드나 zip을 받아 ingress, scaling, slot이 연결된 웹 앱으로 바꿔 주듯, ACA는 컨테이너 이미지를 받아 비슷한 일을 해 줍니다. 차이는 입력이 컨테이너 이미지라는 점이고, 스케일러가 KEDA라서 0까지 내려갈 수 있다는 점입니다.

> 다른 비유로 보면, AKS가 "직접 운전하는 차"라면 ACA는 "택시를 부르는 것"에 가깝습니다. 목적지(이미지)와 몇 가지 선호사항(스케일 규칙, ingress)만 정하면 클러스터는 시야 밖에 머뭅니다.

## 하나의 ACA 환경부터 보기

이 그림이 시리즈 전체의 지도입니다. 뒤의 글들은 각 상자를 하나씩 확대합니다.

- 클라이언트와 ingress: 4화
- Environment, Container App, Revision: 2화
- 첫 배포: 3화
- KEDA 스케일링: 5화
- Dapr: 6화
- 관측성: 7화

## 핵심 개념 1 — 한 문장 정의

ACA는 관리형 서버리스 컨테이너 플랫폼입니다. Microsoft가 운영하는 Kubernetes 기반 위에 KEDA 기반 스케일링, 선택적 Dapr 통합, 관리형 ingress를 얹어 제공하지만, 사용자는 클러스터 자체를 보거나 제어하지 않습니다.

- 컨테이너 이미지가 배포 단위입니다.
- 유휴 상태에서는 replica 수가 줄고, 조건이 맞으면 0까지 내려갈 수 있습니다.
- Ingress, Revision, 관측성이 제품 안에 기본으로 들어 있습니다.

## 핵심 개념 2 — Azure 컨테이너 서비스 비교

| 서비스 | 추상화 수준 | 잘 맞는 워크로드 | 트레이드오프 |
|---|---|---|---|
| **AKS** | 낮음 (raw Kubernetes) | 복잡한 멀티 테넌트 시스템, 세밀한 제어 | 클러스터를 직접 운영해야 합니다 |
| **ACA** | 중간 (managed K8s) | HTTP API, worker, 마이크로서비스 | K8s API의 일부만 노출됩니다 |
| **App Service** | 높음 (PaaS) | 전형적인 웹 앱 | 비컨테이너 옵션은 많지 않습니다 |
| **Functions** | 가장 높음 (FaaS) | 이벤트 기반, 짧은 함수 | 장시간 실행 워크로드에는 맞지 않습니다 |

ACA는 "AKS만큼 자유롭지는 않지만, App Service보다 훨씬 더 컨테이너 네이티브하다"는 자리에 놓입니다.

## Before / After

**Before (AKS만 알고 있을 때)**

```bash
# Just to put one small API on AKS:
az aks create ...                  # cluster creation (tens of minutes)
kubectl apply -f deployment.yaml   # write Deployment, Service, Ingress yourself
helm install ingress-nginx ...     # install your own ingress controller
helm install cert-manager ...      # configure TLS yourself
# + node maintenance, K8s upgrades, RBAC
```

**After (ACA)**

```bash
az containerapp up \
  --name myapi \
  --resource-group rg-demo \
  --image myregistry.azurecr.io/myapi:v1 \
  --ingress external \
  --target-port 8000
# → environment created, ingress + HTTPS + scaling 0..N configured automatically
```

차이는 명령 하나와 여러 도구의 차이입니다. 작은 API에 K8s 복잡도가 필요하지 않을 때 ACA가 빛납니다.

## 실습 — 첫 ACA 환경 만들기

본격적인 배포는 3화에서 다룹니다. 여기서는 환경만 만듭니다.

### Step 1. CLI 준비

```bash
az login
az extension add --name containerapp --upgrade
az provider register --namespace Microsoft.App
```

### Step 2. 리소스 그룹과 Environment 만들기

```bash
RG=rg-aca-demo
LOC=koreacentral
ENV=aca-env-demo

az group create --name $RG --location $LOC
az containerapp env create \
  --name $ENV \
  --resource-group $RG \
  --location $LOC
```

### Step 3. hello-world 이미지 배포하기

```bash
az containerapp up \
  --name hello-aca \
  --resource-group $RG \
  --environment $ENV \
  --image mcr.microsoft.com/azuredocs/containerapps-helloworld:latest \
  --ingress external \
  --target-port 80
```

마지막 출력에는 `https://hello-aca.<unique>.azurecontainerapps.io` URL이 찍힙니다. HTTPS 인증서, ingress, scale-to-zero가 모두 자동으로 연결됩니다.

## 요청 하나가 지나가는 경로

가장 단순한 HTTP 요청을 따라가 보면 플랫폼이 맡는 책임이 더 구체적으로 보입니다.

![Client request flow to an active revision](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-101/01/01-02-the-path-of-one-request.ko.png)

*Client request flow to an active revision*

여러분이 결정하는 것:

- 이미지를 빌드하는 일
- 포트와 health probe 경로 선택
- 스케일 규칙 정의
- 트래픽 전략 선택(Revision split)
- 로그와 트레이스의 목적지 결정

ACA가 대신 처리하는 것: TLS 종료, 요청 라우팅, replica 오토스케일링, 컨테이너 재시작, 로그 수집입니다.

## 자주 하는 실수

### 실수 1. ACA를 "AKS 대체재"로만 보는 것

ACA는 K8s를 단순화한 서비스이지, 모든 기능을 노출하는 서비스가 아닙니다. CRD, custom controller, DaemonSet, StatefulSet, GPU 스케줄링이 필요하다면 AKS가 정답입니다.

### 실수 2. scale-to-zero를 항상 켜 두는 것

1–5초 수준의 cold start가 생기므로 사용자 대면 API의 첫 요청은 느려집니다. SLA가 엄격하다면 `--min-replicas 1`로 두고, scale-to-zero는 batch나 worker에 남겨 두는 편이 낫습니다.

### 실수 3. 서비스마다 Environment를 하나씩 만드는 것

Environment는 VNet과 로그 목적지를 공유하는 경계입니다. 같은 팀의 마이크로서비스는 하나의 Environment 안에 두는 편이 비용과 운영을 모두 관리하기 쉽습니다.

### 실수 4. 첫날부터 Dapr를 켜는 것

Dapr는 강력하지만 학습 곡선이 있습니다. 평범한 HTTP API라면 Dapr 없이 시작하고, pub/sub이나 state store가 실제로 필요해졌을 때 도입하는 편이 좋습니다(6화).

### 실수 5. worker에 external ingress를 붙이는 것

Worker(메시지 소비자, 배치 작업)는 외부 트래픽을 받지 않으므로 `--ingress disabled` 또는 `internal`을 사용해야 합니다. external ingress를 켜면 쓸모없는 엔드포인트만 외부에 노출됩니다.

## 실무에서는 이렇게 생각한다

프로덕션에서 ACA를 고를 때는 대개 몇 가지 질문으로 판단합니다.

- 우리가 K8s를 직접 운영할 인력이 있는가? 없다면 ACA가 거의 확실하게 더 맞습니다.
- 워크로드가 HTTP API + worker 조합인가? 그렇다면 ACA의 스위트 스팟에 가깝습니다.
- 유휴 시간이 긴가? 그렇다면 scale-to-zero로 비용을 크게 줄일 수 있습니다.
- K8s 네이티브 기능(Operator, GPU, custom scheduler)이 필요한가? 그렇다면 AKS로 가야 합니다.
- 컨테이너보다 zip/code 배포가 더 편한가? 그렇다면 App Service가 더 단순합니다.

앞의 세 질문에는 예, 마지막 두 질문에는 아니오라면 ACA가 가장 자연스러운 선택입니다.

## ACA가 잘 맞는 시나리오

- FastAPI 기반 API
- 트래픽이 몰렸다 줄어드는 worker
- 마이크로서비스 조합
- canary나 blue-green이 필요한 서비스

## 체크리스트

- [ ] ACA가 AKS, App Service, Functions와 어떻게 다른지 한 문단으로 설명할 수 있습니다
- [ ] Environment, Container App, Revision의 관계를 직접 그릴 수 있습니다
- [ ] scale-to-zero를 켜야 할 때와 꺼야 할 때를 구분할 수 있습니다
- [ ] 위의 다섯 질문으로 우리 워크로드가 ACA에 맞는지 판단할 수 있습니다

## 연습 문제

1. 아래 워크로드마다 AKS / ACA / App Service / Functions 중 하나를 고르고, 한 줄 이유를 써 보세요.
   - "GitHub webhook을 받아 Slack에 보내는 함수"
   - "평균 초당 약 100 req/s를 처리하는 FastAPI REST API"
   - "GPU 기반 모델 학습 파이프라인"
   - "서비스 메시로 연결된 30개 마이크로서비스 시스템"
2. 위 Step 1-3을 따라 첫 ACA 환경을 만들고 hello-world URL을 호출해 보세요. 첫 번째 요청과 두 번째 요청의 지연 시간을 비교해 cold start를 직접 체감해 보세요.

## 정리

- ACA는 관리형 서버리스 컨테이너 플랫폼입니다. 다시 말해 "컨테이너는 직접 가져오되, 클러스터는 플랫폼에 맡기는" 모델입니다.
- Environment는 공용 경계이고, App과 Revision은 일상적인 운영 단위입니다.
- AKS만큼 자유롭지는 않지만, KEDA 기반 scale-to-zero와 revision 기반 트래픽 분할이 기본으로 들어 있습니다.
- 워크로드가 HTTP API + worker 조합이고 트래픽 변동이 크다면 ACA가 가장 자연스럽습니다.
- 클러스터를 숨긴다고 해서 ingress, scaling, rollout, observability 결정까지 사라지는 것은 아닙니다. 그 판단은 여전히 사용자 몫입니다.

다음 글에서는 이 모델을 Environment, Container App, Revision이라는 세 단어로 더 정밀하게 확대해 봅니다.

## 처음 질문으로 돌아가기

- **Azure Container Apps(ACA)는 다른 Azure 컨테이너 서비스(App Service, AKS, Functions)와 무엇이 다를까요?**
  - 본문의 기준은 Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **ACA의 세 가지 핵심 구성 요소인 Environment, Container App, Revision은 각각 어떤 역할을 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **어떤 워크로드는 ACA에 잘 맞고, 어떤 워크로드는 다른 서비스에 두는 편이 나을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **Azure Container Apps 101 (1/7): Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기 (현재 글)**
- Azure Container Apps 101 (2/7): Environment, Container App, Revision — ACA in three words (예정)
- Azure Container Apps 101 (3/7): 첫 배포하기 — Python/FastAPI (예정)
- Azure Container Apps 101 (4/7): Ingress와 트래픽 분할 — revision 기반 배포 전략 (예정)
- Azure Container Apps 101 (5/7): 스케일링 — KEDA scaler와 zero-to-N (예정)
- Azure Container Apps 101 (6/7): Dapr 통합 — 사이드카로 얻는 것 (예정)
- Azure Container Apps 101 (7/7): 모니터링과 운영 — Log Analytics와 Application Insights (예정)

<!-- toc:end -->

---

## 참고 자료

### 공식 문서

- [Azure Container Apps overview — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/overview)
- [Azure Container Apps environments — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/environment)
- [Update and deploy changes in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/revisions)
- [Ingress in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/ingress-overview)

### 관련 시리즈

- [Azure App Service 101](../../azure-app-service-101/ko/01-what-is-app-service.md)
- [Azure AKS 101](../../azure-aks-101/ko/01-what-is-aks.md)

Tags: Azure, Container Apps, Serverless, Containers
