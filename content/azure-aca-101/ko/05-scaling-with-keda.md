---
title: 스케일링 — KEDA scaler와 zero-to-N
series: azure-aca-101
episode: 5
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Azure
- Container Apps
- KEDA
- Autoscaling
- Scale-to-Zero
- Serverless
last_reviewed: '2026-05-15'
seo_description: 스케일링은 신호, 규칙, 범위라는 세 단계 선언형 흐름으로 이해하면 단순해집니다.
---

# 스케일링 — KEDA scaler와 zero-to-N

ACA의 스케일링은 단순히 replica 수를 늘리는 기능이 아닙니다. 어떤 신호를 중요하게 볼지, 그리고 0까지 내려갈 수 있게 할지를 정하는 순간 비용 정책과 지연 시간 정책도 함께 정해집니다.

이 글은 Azure Container Apps 101 시리즈의 5번째 글입니다. 여기서는 KEDA scaler와 zero-to-N 모델을 운영 관점에서 풀어 보겠습니다.

## 이 글에서 다룰 문제

- Azure Container Apps는 선언형 스케일링 신호를 바탕으로 replica 수를 어떻게 결정할까요?
- 내장 HTTP/TCP 규칙과 사용자 정의 KEDA scaler의 차이는 무엇일까요?
- `min-replicas 0`(scale-to-zero)는 언제 안전하고, 언제 위험할까요?
- `az containerapp` 명령으로 HTTP API와 Service Bus 큐 worker를 각각 어떻게 구성할까요?

## 이 글이 답할 질문

- Azure Container Apps는 어떤 신호를 보고 replica 수를 결정하며, 그 판단은 어디에서 이루어질까요?
- 내장 HTTP/TCP 규칙과 사용자 정의 KEDA scaler 중 언제 무엇을 써야 할까요?
- `min-replicas 0`(scale-to-zero)는 언제 안전하고, 언제 위험할까요?
- Service Bus 큐 worker는 왜 HTTP 규칙이 아니라 KEDA scaler로 스케일해야 할까요?
- cold start와 SLO 사이의 트레이드오프는 어떻게 측정하고 받아들여야 할까요?

## 왜 이 글이 중요한가

ACA의 핵심 가치 제안은 "Kubernetes의 무게 없이 컨테이너를 운영한다"입니다. 그 약속이 가장 선명하게 보이는 지점이 스케일링입니다.

여기서는 HPA(Horizontal Pod Autoscaler)나 KEDA를 직접 설치하지 않습니다. 같은 KEDA scaler가 ACA control plane 안에서 동작합니다.

스케일링을 오해하면 두 방향에서 비용을 치르게 됩니다. 첫째는 돈입니다. `min-replicas`를 0보다 크게 둔 채 잊어버리면 유휴 replica 비용을 계속 냅니다. 둘째는 신뢰성입니다. 큐 worker를 HTTP 규칙에 묶어 두면 메시지가 쌓여도 replica는 늘지 않습니다. 스케일 규칙은 비용 정책이면서 동시에 SLO 정책입니다.

## 멘탈 모델

스케일링은 세 단계 선언형 파이프라인으로 보면 단순해집니다.

1. **Signal** — 무엇을 볼지: HTTP 동시 요청 수, TCP 연결 수, Service Bus 큐 길이, CPU 사용률 등
2. **Rule** — 그 신호를 어떻게 해석할지: `--scale-rule-type http`, `azure-servicebus`, `cpu` 등
3. **Bounds** — `--min-replicas`와 `--max-replicas` 사이에서 KEDA가 replica 수를 고릅니다

Signal → Rule → Bounds. 이 세 가지가 정해지면 나머지는 ACA가 처리합니다.
YAML이나 명령형 스케일링 코드를 쓰는 것이 아니라, "이 신호가 오면 N까지 늘려라"라고 선언하는 구조입니다.

> 스케일링은 무엇을 볼지, 어떻게 해석할지, 어디까지 허용할지를 먼저 선언하고, 런타임이 그 범위 안에서 replica 수를 움직이게 하는 모델입니다.

![Scale signals changing replica counts](../../../assets/azure-aca-101/05/05-01-the-scaling-path.ko.png)

*Scale signals changing replica counts*

## 핵심 개념

### 1. 세 가지 규칙 범주

| Category | Trigger | Scale-to-zero | 흔한 용도 |
| --- | --- | --- | --- |
| HTTP rule | Concurrent HTTP requests | Yes | Web API, REST 서비스 |
| TCP rule | Concurrent TCP connections | Yes | gRPC, 사용자 정의 TCP 서버 |
| Custom KEDA rules | Service Bus, Event Hubs, Kafka, Redis, CPU, memory 등 | scaler에 따라 다름 | 큐 worker, 배치 프로세서 |

HTTP와 TCP는 ACA ingress 레이어가 직접 측정하므로 추가 인증이 필요 없습니다.
반면 custom rule은 외부 리소스(Service Bus namespace 등)에 접근하므로 `--scale-rule-auth`로 secret을 연결해야 합니다.

### 2. scale-to-zero가 실제로 뜻하는 것

`--min-replicas 0`는 "트래픽이 없으면 replica를 0까지 내린다"는 뜻입니다.
다음 요청이 들어오면 ACA가 새 replica를 띄우면서 cold start가 발생합니다.
HTTP 규칙과 대부분의 이벤트 기반 KEDA scaler(Service Bus, Event Hubs, Kafka 등)는 0까지 내려갈 수 있습니다.
**CPU와 memory scaler는 custom 범주에 속하지만 scale-to-zero는 되지 않습니다.** CPU나 memory를 측정하려면 최소 하나의 replica가 있어야 하기 때문입니다.

### 3. cold start 트레이드오프

Scale-to-zero는 유휴 비용을 거의 0으로 밀어 내지만, 첫 요청은 컨테이너가 뜰 때까지 기다려야 합니다.
Python/FastAPI는 보통 1–3초 정도 걸리고, 무거운 모델 로딩은 10초 이상까지 늘 수 있습니다.
사용자 대면 동기 API는 `min-replicas 1`이 낫고, 비동기 worker나 야간 배치는 `min-replicas 0`이 적절합니다.

## Before / After

### Before (명시적인 스케일 규칙이 없는 경우)

```bash
az containerapp create \
  --name my-api --resource-group $RG --environment $ACA_ENV \
  --image $IMAGE --ingress external --target-port 8000
```

명시적인 규칙이 없으면 ACA는 기본 HTTP 스케일 규칙(concurrency 10)과 함께 `min-replicas 0`, `max-replicas 10`을 적용합니다.
덕분에 유휴 비용은 없지만 첫 요청은 cold start를 맞습니다.
ACA는 더 높은 replica 상한으로 구성할 수 있지만, 별도 설정이 없다면 기본 스케일 범위는 0~10 replica입니다.

### After (명시적인 HTTP 규칙을 둔 경우)

```bash
az containerapp create \
  --name my-api --resource-group $RG --environment $ACA_ENV \
  --image $IMAGE --ingress external --target-port 8000 \
  --min-replicas 1 --max-replicas 10 \
  --scale-rule-name http-rule \
  --scale-rule-type http \
  --scale-rule-http-concurrency 50
```

`min-replicas 1`은 cold start를 없앱니다. `max-replicas 10`은 비용 상한을 잡아 줍니다.
동시 요청 50개를 기준으로 replica가 늘어나므로, 트래픽 스파이크 동안 지연 시간을 더 안정적으로 유지할 수 있습니다.

## 단계별 실습

### Step 1: HTTP API에 스케일 규칙 적용하기

FastAPI 앱이 이미 ACR에 올라가 있다고 가정합니다.

```bash
RG=rg-aca-demo
ACA_ENV=aca-env-demo
IMAGE=myacr.azurecr.io/my-api:latest

az containerapp create \
  --name my-api --resource-group $RG --environment $ACA_ENV \
  --image $IMAGE --ingress external --target-port 8000 \
  --min-replicas 0 --max-replicas 5 \
  --scale-rule-name http-rule \
  --scale-rule-type http \
  --scale-rule-http-concurrency 100
```

### Step 2: Service Bus 큐 worker 만들기

```bash
az containerapp create \
  --name queue-worker --resource-group $RG --environment $ACA_ENV \
  --image $IMAGE \
  --min-replicas 0 --max-replicas 10 \
  --secrets "sb-connection=<SERVICE_BUS_CONNECTION_STRING>" \
  --scale-rule-name servicebus-rule \
  --scale-rule-type azure-servicebus \
  --scale-rule-metadata \
      "queueName=orders" \
      "namespace=mybus.servicebus.windows.net" \
      "messageCount=5" \
  --scale-rule-auth "connection=sb-connection"
```

`messageCount=5`는 "대기 메시지 5개마다 replica 하나"를 뜻합니다.
큐가 비면 0으로 내려가고, 50개가 쌓이면 10 replica(최대값)까지 올라갑니다.

### Step 3: 동작 검증하기

```bash
az containerapp replica list --name queue-worker --resource-group $RG -o table
```

메시지를 넣은 뒤 30–60초 안에 replica 수가 바뀌어야 정상입니다.

## 자주 하는 실수

- 지연 시간에 민감한 API에 `min-replicas 0`을 쓰는 것 — 매번 cold path가 cold start 비용을 냅니다. 사용자 대면 API는 최소 1로 고정하는 편이 안전합니다.
- `max-replicas`를 지정하지 않는 것 — 트래픽 급증이나 잘못된 규칙 하나가 곧 비용 사고가 됩니다.
- 큐 worker에 HTTP 규칙을 다는 것 — 메시지는 쌓이는데 replica는 늘지 않습니다. 이벤트 기반 scaler를 써야 합니다.
- 인증 없이 Service Bus scaler를 구성하는 것 — `--scale-rule-auth`가 없으면 KEDA가 큐를 polling할 수 없어 스케일링이 일어나지 않습니다.
- CPU scaler에 `min-replicas 0`을 기대하는 것 — CPU와 memory scaler는 측정할 replica가 필요하므로 0까지 내려가지 않습니다.

## 프로덕션에서는 이렇게 둔다

시나리오별 권장값은 보통 아래와 같습니다.

- 공개 REST API — `min=1, max=10`, HTTP rule, concurrency 50–100. cold start 제거를 우선합니다.
- 내부 admin API — `min=0, max=3`, HTTP rule. 비용을 우선합니다.
- 주문 처리 worker — `min=0, max=20`, Service Bus rule, `messageCount=10`. 버스트 처리량을 우선합니다.
- 실시간 추론 API — `min=2, max=20`, HTTP rule, concurrency 20. 지연 시간 SLO가 가장 중요합니다.
- 야간 배치 — `min=0, max=5`, 스케줄 기반 또는 수동 트리거.

KEDA scaler 종류는 [공식 문서](https://keda.sh/docs/scalers/)에 정리돼 있고, Microsoft Learn에는 ACA가 지원하는 scaler 목록이 나옵니다.

## 체크리스트

- [ ] 내 워크로드에 맞는 트리거 범주(HTTP / TCP / custom)를 골랐습니까?
- [ ] `min-replicas`가 우리 서비스의 cold-start 허용치와 맞습니까?
- [ ] `max-replicas`로 비용 상한을 설정했습니까?
- [ ] custom scaler라면 `--scale-rule-auth`와 secret을 연결했습니까?
- [ ] 큐 worker가 이벤트 기반 scaler를 사용하고 있습니까?
- [ ] Application Insights 또는 Log Analytics에서 replica 수를 모니터링하고 있습니까?

## 연습 문제

1. 평균 동시성 30, 피크 200인 REST API가 있다면 `min`, `max`, `http-concurrency`를 어떻게 잡겠습니까? 각각 이유를 써 보세요.
2. Service Bus 큐에 메시지 1000개가 쌓였는데 worker replica는 10개뿐입니다. 그럴듯한 원인 세 가지를 적어 보세요.
3. CPU 기반 scaler에 `min-replicas 0`을 주면 무슨 일이 생길까요? 왜 그럴까요?

## 정리

- ACA 스케일링은 선언형 Signal → Rule → Bounds 파이프라인으로 이해하면 됩니다.
- HTTP와 TCP는 내장 규칙이고, 나머지는 custom KEDA scaler입니다.
- Scale-to-zero는 유휴 비용을 거의 0으로 만들지만 cold start를 가져옵니다.
- `min-replicas`와 `max-replicas`는 동시에 비용 정책이자 SLO 정책입니다.

다음 글에서는 **Dapr 통합**을 다룹니다. 사이드카를 붙이면 service invocation, pub/sub, state store 같은 분산 시스템 구성요소를 라이브러리 종속성 없이 어떻게 가져올 수 있는지 보겠습니다.

---

<!-- toc:begin -->
## 시리즈 목차

- [Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기](./01-what-is-aca.md)
- [Environment, Container App, Revision — ACA in three words](./02-environment-app-revision.md)
- [첫 배포하기 — Python/FastAPI](./03-first-deploy.md)
- [Ingress와 트래픽 분할 — revision 기반 배포 전략](./04-ingress-and-traffic-split.md)
- **스케일링 — KEDA scaler와 zero-to-N (현재 글)**
- Dapr 통합 — 사이드카로 얻는 것 (예정)
- 모니터링과 운영 — Log Analytics와 Application Insights (예정)

<!-- toc:end -->

---

## 참고 자료

### 공식 문서

- [Scaling in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/scale-app)
- [Azure Container Apps overview — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/overview)
- [KEDA scalers documentation](https://keda.sh/docs/scalers/)
- [Azure Service Bus scaler — KEDA](https://keda.sh/docs/scalers/azure-service-bus/)

### 관련 시리즈

- [Azure App Service 101](../../azure-app-service-101/ko/01-what-is-app-service.md)
- [Azure AKS 101](../../azure-aks-101/ko/01-what-is-aks.md)
- [Azure Functions 101](../../azure-functions-101/ko/01-what-is-azure-functions.md)

Tags: Azure, Container Apps, Serverless, Containers
