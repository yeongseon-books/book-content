---
title: 'Hosting Models: 어떤 플랜을 선택해야 할까?'
series: azure-app-service-101
episode: 3
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Azure
- App Service
- Cloud
- Web Apps
last_reviewed: '2026-05-12'
seo_description: App Service의 OS, 배포 모델, 티어를 어떤 기준과 순서로 골라야 하는지 실무 관점으로 정리합니다.
---

# Hosting Models: 어떤 플랜을 선택해야 할까?

App Service를 처음 만들 때 가장 먼저 부딪히는 질문은 “어떤 플랜을 골라야 하지?”입니다. Free, Basic, Standard, Premium에 Linux와 Windows, Code와 Container까지 한 번에 나오면 선택지가 많아 보여도 기준은 잘 보이지 않습니다.

이 글은 Azure App Service 101 시리즈의 3번째 글입니다.

여기서는 App Service 옵션 목록을 외우는 대신, OS, 배포 모델, 가격 티어를 어떤 순서와 기준으로 고르면 되는지 실무 의사결정 프레임으로 정리하겠습니다.

---

## 이 글에서 다룰 문제

- 같은 App Service에서도 코드 배포, 기본 제공 컨테이너(built-in container), 커스텀 컨테이너(custom container)는 무엇이 다를까요?
- Linux App Service에서 Docker 이미지를 실행할 때 startup command는 어떤 순서로 결정될까요?
- Windows 컨테이너는 왜 특정 SKU에서만 실행될까요?
- ZIP 배포와 컨테이너 배포는 롤백 전략이 어떻게 달라질까요?
- 같은 앱을 여러 호스팅 모델로 함께 운영하는 것이 실제로 가치 있는 시점은 언제일까요?

## Decision Flowchart

App Service 호스팅 전략을 고르는 흐름은 아래와 같습니다.

```text
1. Choose OS (Linux / Windows)
 ↓
2. Choose Deployment Model (Code / Container)
 ↓
3. Choose Plan Tier (Dev → Production)
```

![Plan choice after OS and deployment](../../../assets/azure-app-service-101/03/01-decision-flow.ko.png)

*OS와 배포 모델을 거친 뒤의 플랜 선택 흐름*

> 티어를 먼저 고르기보다, OS와 배포 모델을 먼저 고르면 실제 제약이 보입니다. App Service 선택은 기능 표 읽기가 아니라 제약을 먼저 고르는 일에 가깝습니다.

---

## What is an App Service Plan?

App Service Plan은 앱이 실행되는 **컴퓨팅 리소스 풀**입니다.

### What the Plan Defines

| Item | Description |
|------|-------------|
| CPU/Memory | 인스턴스당 사용할 수 있는 리소스 |
| Max Instance Count | scale out 한도 |
| Feature Set | Autoscale, Slots, VNet 등 |
| Pricing & SLA | 비용과 가용성 보장 |

### Key Point: One Plan = Multiple Apps

여러 앱을 같은 Plan에 배포하면 **같은 컴퓨팅 리소스**를 공유합니다.

```text
[App Service Plan: Standard S1]
├── Web App A
├── Web App B 
└── API App C ← All share the same VM pool
```

즉 App Service Plan은 “앱 하나의 가격표”가 아니라 “앱 여러 개가 올라가는 리소스 묶음”으로 보는 편이 맞습니다.

---

## Plan Tier Comparison

### Features by Tier

| Tier | Use Case | Key Limitations |
|------|----------|-----------------|
| **Free/Shared** | 학습, 실험 | 공유 리소스, 제한된 기능 |
| **Basic** | 낮은 트래픽 | 운영 기능 제한 |
| **Standard** | 기본 프로덕션 | 중간 수준의 scale 한계 |
| **Premium** | 고성능, 네트워킹 | 더 높은 비용 |
| **Isolated** | 규정 준수, 네트워크 격리 | 최고 비용, 높은 복잡성 |

### Feature Requirements by Tier

| Feature | Minimum Tier |
|---------|-------------|
| Custom Domain | Shared |
| SSL Certificate | Basic |
| Deployment Slots | Standard |
| Autoscale | Standard |
| VNet Integration | Standard |
| Private Endpoint | Premium |
| Zone Redundancy | Premium |

### Practical Advice

> 프로덕션은 최소 Standard부터 시작하는 편이 안전합니다. Autoscale과 Deployment Slot 없이 운영하면 결국 사람이 직접 사고를 막아야 합니다.

---

## OS Selection: Linux vs Windows

### Which OS to Choose?

| Consideration | Description |
|---------------|-------------|
| Existing standards | 팀이 익숙한 환경 |
| Dependency compatibility | 특정 라이브러리 요구사항 |
| Compliance | 엔터프라이즈 보안 정책 |
| Tooling/Observability | 디버깅 워크플로 |

### Practical Differences

| Aspect | Linux | Windows |
|--------|-------|---------|
| Startup speed | 대체로 더 빠름 | 약간 더 느림 |
| Container support | Native | 제한적 |
| Kudu/SCM | 기능이 제한적 | 기능이 더 풍부함 |
| Cost | 티어별 동일 | 동일 |

**권장:** 특별한 이유가 없다면 **Linux**를 먼저 검토합니다. 현대적인 스택과 더 잘 맞기 때문입니다.

```bash
# Create Linux Plan
az appservice plan create \
 --resource-group $RG \
 --name $PLAN_NAME \
 --location koreacentral \
 --sku S1 \
 --is-linux
```

---

## Deployment Model: Code vs Container

### Code-based Deployment

플랫폼이 런타임을 제공하고, 여러분은 코드만 배포합니다.

**Pros:**
- 빠른 온보딩
- container 관리 오버헤드 감소
- 강한 플랫폼 통합

**Cons:**
- base image 제어 범위가 제한됨
- 런타임 업데이트가 플랫폼 정책을 따름

```bash
# Create code-based web app
az webapp create \
 --resource-group $RG \
 --plan $PLAN_NAME \
 --name $APP_NAME \
 --runtime "PYTHON|3.11"
```

### Container-based Deployment

직접 만든 OCI 이미지를 빌드하고 배포합니다.

**Pros:**
- 런타임 스택 전체 제어 가능
- 로컬과 클라우드 환경 일관성
- OS 레벨 의존성 자유도

**Cons:**
- 패치 주기를 직접 관리해야 함
- 레지스트리 거버넌스 필요
- 이미지 품질이 startup 성능에 직접 영향

```bash
# Create container-based web app
az webapp create \
 --resource-group $RG \
 --plan $PLAN_NAME \
 --name $APP_NAME \
 --deployment-container-image-name myregistry.azurecr.io/myapp:latest
```

---

## Shared Plan vs Dedicated Plan

![Shared and dedicated resource tradeoffs](../../../assets/azure-app-service-101/03/03-shared-vs-dedicated.ko.png)

*공유 Plan과 전용 Plan의 트레이드오프*

### Shared Plan Strategy

여러 앱을 하나의 Plan에 올리는 방식입니다.

**Pros:**
- 비용 효율적임
- 트래픽 패턴이 다른 앱끼리 상호 보완 가능

**Cons:**
- 앱 사이 리소스 경쟁 발생(Noisy Neighbor)
- 한 앱의 문제가 다른 앱에 영향

### Dedicated Plan Strategy

중요한 앱마다 별도 Plan을 두는 방식입니다.

**Pros:**
- 리소스 격리
- 용량 예측이 쉬움
- blast radius 제한

**Cons:**
- 비용 증가

### Recommended Approach

```text
Business-critical apps → Dedicated Plan
Internal tools, low traffic apps → Shared Plan
```

운영에서는 “같은 Plan에 묶어도 되는가”가 비용과 안정성을 함께 가르는 질문이 됩니다.

---

## Feature Mapping

어떤 기능이 Plan에 의존하고, 어떤 기능이 배포 모델에 의존하는지 정리하면 아래와 같습니다.

![Feature availability across plan tiers](../../../assets/azure-app-service-101/03/02-tier-feature-matrix.ko.png)

*플랜 티어별 기능 가용성*

| Feature | Plan Dependent | Deployment Model Dependent |
|---------|----------------|---------------------------|
| Autoscale | Yes | No |
| Deployment Slots | Yes | No |
| Private Endpoint | Yes | No |
| VNet Integration | Yes | No |
| Custom Startup Image | No | Yes (Container) |
| Platform Build | No | Yes (Code) |

---

## Cost and Capacity Planning

### Capacity Planning Considerations

| Item | Question |
|------|----------|
| Traffic | Peak vs average request rate? |
| Resources | CPU-intensive vs IO-intensive? |
| Memory | Memory per request, background workers? |
| Startup time | Cold start frequency? |

### Practical Patterns

```
1. Start with production-ready tier (Standard or higher)
2. Load test with actual traffic patterns
3. Configure Autoscale thresholds and cooldowns
4. Re-evaluate Plan size monthly
```

### Check Plan Info with CLI

```bash
az appservice plan show \
 --resource-group $RG \
 --name $PLAN_NAME \
 --query "{sku:sku, workers:numberOfWorkers, reserved:reserved}" \
 --output json
```

**예시 출력:**
```json
{
 "sku": {
 "name": "S1",
 "tier": "Standard",
 "capacity": 2
 },
 "workers": 2,
 "reserved": true
}
```

---

## Right-Sizing Checklist

Plan을 고르기 전에 아래를 점검합니다.

| Question | Check |
|----------|-------|
| Does it support required networking features? | |
| Does it support required deployment patterns? (Slots) | |
| Will Autoscale react before saturation? | |
| Is memory per instance sufficient at peak? | |
| Can dependent services handle increased load? | |

---

## 운영 체크리스트

- [ ] 선택한 hosting model을 왜 골랐는지 기록했다
- [ ] startup command와 env var의 단일 출처(IaC)를 정했다
- [ ] Managed Identity로 registry 인증을 구성했다
- [ ] hosting model별 rollback 절차를 문서화하고 연습했다
- [ ] hosting model이 바뀔 때 어떤 모니터링 필드가 달라지는지 정리했다

---

## 정리

Hosting Model 선택에서 기억할 핵심은 네 가지입니다.

- **OS**: 특별한 이유가 없으면 Linux를 먼저 봅니다.
- **Deployment Model**: 기본은 Code로 시작하고, 제어가 더 필요할 때 Container로 갑니다.
- **Tier**: 프로덕션은 Standard 이상이 현실적인 출발점입니다.
- **Plan Strategy**: 핵심 앱은 Dedicated, 나머지는 Shared가 일반적인 패턴입니다.

결국 App Service 선택은 옵션을 많이 아는 것보다, 어떤 제약을 받아들이고 어떤 운영 비용을 줄일지 먼저 정하는 일이 더 중요합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure App Service란? - 플랫폼 아키텍처 이해하기](./01-what-is-app-service.md)
- [Request Lifecycle: 3am에 터진 502를 어디서부터 봐야 할까](./02-request-lifecycle.md)
- **Hosting Models: 어떤 플랜을 선택해야 할까? (현재 글)**
- 첫 번째 배포: 로컬에서 Azure까지 (Python/Flask) (예정)
- Configuration 마스터하기: App Settings & 환경변수 (예정)
- 로그와 모니터링 기초: “앱이 느려요”에 답할 수 있는 상태 만들기 (예정)
- Scaling 101: 언제 Scale Up vs Scale Out? (예정)

<!-- toc:end -->

---

## 참고 자료

### 공식 문서
- [App Service plan overview (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/overview-hosting-plans)
- [Custom container in App Service (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/tutorial-custom-container)
- [App Service pricing (Azure)](https://azure.microsoft.com/pricing/details/app-service/)

### 관련 시리즈
- [Azure Functions 101](../../azure-functions-101/ko/)

---

Tags: Azure, App Service, Cloud, Web Apps
