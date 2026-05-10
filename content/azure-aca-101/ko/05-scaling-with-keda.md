---
title: 스케일링 — KEDA scaler와 0-to-N
series: azure-aca-101
episode: 5
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Azure
- Container Apps
- KEDA
- Autoscaling
- Scale-to-Zero
- Serverless
last_reviewed: '2026-04-29'
seo_description: 스케일링은 세 단계의 선언적 흐름으로 보면 단순해집니다.
---

# 스케일링 — KEDA scaler와 0-to-N

> Azure Container Apps 101 시리즈 (5/7)

## 이 글에서 답할 질문

- ACA는 어떤 신호를 보고 replica 수를 결정하며, 그 결정은 어디에서 일어나는가?
- 내장 HTTP·TCP scale rule과 KEDA custom scaler는 언제 어느 쪽을 골라야 하는가?
- `min-replicas 0`(scale-to-zero)은 어떤 워크로드에서 안전하고, 어떤 경우에 위험한가?
- Service Bus queue worker는 왜 HTTP rule이 아니라 KEDA scaler로 묶어야 하는가?
- cold start trade-off는 SLO 관점에서 어떻게 측정하고 절충해야 하는가?

## 이 글에서 다룰 문제

ACA의 핵심 가치 제안은 "Kubernetes의 무게 없이 컨테이너를 운영한다"입니다.
그 약속이 가장 분명하게 드러나는 지점이 스케일링입니다.
직접 HPA(Horizontal Pod Autoscaler)나 KEDA를 설치하지 않아도, 동일한 KEDA scaler가 ACA의 control plane 안에서 동작합니다.

스케일링을 이해하지 못하면 두 가지 비용이 발생합니다.
첫째는 **돈**입니다. `min-replicas`를 1 이상으로 잡고 잊으면 idle 상태에서도 replica가 계속 청구됩니다.
둘째는 **신뢰성**입니다. queue 길이 기반으로 스케일해야 할 worker를 HTTP 규칙으로 묶어두면 메시지가 쌓여도 replica가 늘지 않습니다.
스케일링 규칙은 비용 정책이면서 동시에 SLO 정책입니다.

## Mental Model

스케일링은 세 단계의 선언적 흐름으로 보면 단순해집니다.

1. **신호(Signal)** — 무엇을 보고 판단할지: HTTP 동시 요청 수, TCP 연결 수, Service Bus queue 깊이, CPU 사용률 등.
2. **규칙(Rule)** — 신호를 어떤 임계값과 어떤 scaler 타입으로 해석할지: `--scale-rule-type http`, `azure-servicebus`, `cpu` 등.
3. **범위(Bounds)** — `--min-replicas`와 `--max-replicas` 사이에서 KEDA가 replica 수를 결정.

신호 → 규칙 → 범위. 이 세 가지만 정해지면 ACA가 나머지를 처리합니다.
직접 작성하는 것은 YAML이나 imperative scaling 코드가 아니라, "어떤 신호가 들어오면 몇 개까지 늘려라"라는 한 줄짜리 선언입니다.

![스케일 신호가 replica 수를 바꾸는 흐름](../../../assets/azure-aca-101/05/05-01-the-scaling-path.ko.png)

*스케일 신호가 replica 수를 바꾸는 흐름*

## 핵심 개념

### 1. 세 가지 규칙 카테고리

| 카테고리 | 트리거 | scale-to-zero | 대표 사용처 |
| --- | --- | --- | --- |
| HTTP 규칙 | 동시 HTTP 요청 수 | 가능 | Web API, REST 서비스 |
| TCP 규칙 | 동시 TCP 연결 수 | 가능 | gRPC, custom TCP 서버 |
| Custom KEDA 규칙 | Service Bus, Event Hubs, Kafka, Redis, CPU, memory 등 | scaler에 따라 다름 | Queue worker, batch processor |

HTTP·TCP는 ACA가 ingress 계층에서 직접 측정하기 때문에 별도 인증이 필요 없습니다.
Custom 규칙은 외부 리소스(예: Service Bus namespace)에 접근해야 하므로 `--scale-rule-auth`로 secret을 연결합니다.

### 2. scale-to-zero의 의미

`--min-replicas 0`은 "트래픽이 없으면 replica를 0개로 내려라"는 뜻입니다.
다음 요청이 들어오면 ACA가 cold start로 새 replica를 띄웁니다.
HTTP 규칙과 대부분의 event-driven KEDA scaler(Service Bus, Event Hubs, Kafka 등)는 0까지 내려갈 수 있습니다.
**CPU와 memory scaler는 custom 카테고리에 속하지만 scale-to-zero를 지원하지 않습니다.** 측정할 replica가 있어야 CPU·memory를 잴 수 있기 때문입니다.

### 3. Cold start trade-off

scale-to-zero는 비용을 거의 0으로 만들지만, 첫 요청은 컨테이너가 시작될 때까지 기다려야 합니다.
Python/FastAPI 기준 보통 1~3초, 무거운 모델 로딩이 있으면 10초 이상까지 갑니다.
사용자가 직접 보는 경로(synchronous API)에는 `min-replicas 1`을 권장하고, 비동기 worker나 nightly batch에는 `min-replicas 0`이 적합합니다.

## Before-After

### Before (스케일 규칙 없음)

```bash
az containerapp create \
  --name my-api --resource-group $RG --environment $ACA_ENV \
  --image $IMAGE --ingress external --target-port 8000
```

명시적 규칙이 없으면 ACA는 기본 HTTP scale rule(동시 요청 10)을 적용합니다.
`min-replicas`도 기본값 0이라, idle 상태는 비용이 0이지만 첫 요청 시 cold start가 발생합니다.
부하가 몰리면 100개의 replica까지 늘어날 수 있어 예상치 못한 비용이 발생할 수 있습니다.

### After (명시적 HTTP 규칙)

```bash
az containerapp create \
  --name my-api --resource-group $RG --environment $ACA_ENV \
  --image $IMAGE --ingress external --target-port 8000 \
  --min-replicas 1 --max-replicas 10 \
  --scale-rule-name http-rule \
  --scale-rule-type http \
  --scale-rule-http-concurrency 50
```

`min-replicas 1`로 cold start를 제거했고, `max-replicas 10`으로 비용 상한을 두었습니다.
동시 요청 50을 기준으로 replica를 늘리므로 traffic spike에도 latency가 안정적으로 유지됩니다.

## 단계별 실습

### Step 1: HTTP API에 scaling 적용

FastAPI 앱이 이미 ACR에 푸시되어 있다고 가정합니다.

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

### Step 2: Service Bus queue worker 만들기

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

`messageCount=5`는 "queue에 메시지 5개당 replica 1개"라는 뜻입니다.
queue가 비면 0으로 내려가고, 50개가 쌓이면 10개까지 늘어납니다(max 한도).

### Step 3: 동작 확인

```bash
az containerapp replica list --name queue-worker --resource-group $RG -o table
```

queue에 메시지를 넣은 뒤 30~60초 안에 replica 수가 변하는지 확인합니다.

## 자주 하는 실수

- **`min-replicas 0`을 latency-sensitive API에 적용** — 첫 요청에서 cold start가 발생합니다. user-facing API는 최소 1을 권장합니다.
- **`max-replicas`를 설정하지 않음** — traffic spike나 잘못된 scale rule이 비용 폭탄으로 이어집니다.
- **Queue worker에 HTTP 규칙을 사용** — 메시지가 쌓여도 replica가 늘지 않습니다. 반드시 event-driven scaler를 써야 합니다.
- **Secret 없이 Service Bus scaler 구성** — `--scale-rule-auth`가 없으면 KEDA가 queue를 polling하지 못해 스케일이 동작하지 않습니다.
- **CPU scaler에 `min-replicas 0` 기대** — CPU·memory scaler는 측정 대상이 필요하므로 0으로 내려가지 않습니다.

## 실무에서

실무 시나리오별 권장 설정:

- **공개 REST API** — `min=1, max=10`, HTTP rule, concurrency 50~100. cold start 제거 우선.
- **Internal admin API** — `min=0, max=3`, HTTP rule. 비용 절감 우선.
- **Order processing worker** — `min=0, max=20`, Service Bus rule, `messageCount=10`. burst 처리 우선.
- **Real-time inference API** — `min=2, max=20`, HTTP rule, concurrency 20. latency SLO 중요.
- **Nightly batch** — `min=0, max=5`, scheduled trigger 또는 manual trigger.

KEDA scaler 종류는 [공식 문서](https://keda.sh/docs/scalers/)에서 확인할 수 있고, ACA가 지원하는 scaler 목록은 Microsoft Learn에서 별도 명시됩니다.

## 실무에서는 이렇게 생각한다

scale-to-zero는 비용 절감의 꽃처럼 보이지만, 콜드 스타트 지연이 사용자 경험에 직접 영향을 줍니다. 내부 배치 워커라면 0으로 내려도 문제가 없지만, 사용자 요청을 직접 받는 API라면 최소 replica를 1로 유지하는 편이 현실적입니다. 비용과 응답 시간 사이의 트레이드오프를 팀이 명시적으로 합의해두지 않으면, 장애 리뷰 때 "왜 0이었느냐"는 질문이 반드시 나옵니다.

KEDA scaler를 고를 때 가장 흔한 실수는 HTTP 트리거만 보는 것입니다. 큐 기반 워크로드는 큐 길이 scaler가 훨씬 정확하고, 크론 scaler는 예측 가능한 트래픽 패턴에 적합합니다. 실무에서는 두세 가지 scaler를 조합하는 경우가 많습니다. 예를 들어 HTTP 트리거로 기본 스케일링을 걸고, 크론 scaler로 피크 시간대에 미리 워밍업하는 방식입니다.

스케일링 설정을 코드 리뷰 대상에 포함시키는 팀이 생각보다 적습니다. `maxReplicas`를 100으로 두고 잊어버리면 예상치 못한 비용 폭탄이 됩니다. scaling 규칙은 인프라 설정이 아니라 비즈니스 결정이므로, PR 단위로 변경 이력을 남기는 습관이 필요합니다.

## 체크리스트

- [ ] 트리거 카테고리(HTTP / TCP / custom)를 워크로드 특성에 맞게 골랐는가?
- [ ] `min-replicas`가 cold start 허용 범위와 일치하는가?
- [ ] `max-replicas`로 비용 상한을 설정했는가?
- [ ] Custom scaler에 필요한 `--scale-rule-auth`와 secret을 연결했는가?
- [ ] queue worker는 event-driven scaler를 사용하는가?
- [ ] Application Insights나 Log Analytics에서 replica 수 변화를 모니터링하고 있는가?

## 정리·다음 글

이번 글의 핵심:

- ACA 스케일링은 신호 → 규칙 → 범위의 선언적 흐름입니다.
- HTTP·TCP는 내장 규칙, 그 외 KEDA scaler는 custom 규칙으로 분류됩니다.
- scale-to-zero는 비용을 거의 0으로 만들지만 cold start를 동반합니다.
- `min-replicas`와 `max-replicas`는 비용 정책이자 SLO 정책입니다.

다음 글에서는 **Dapr 통합**을 다룹니다.
service invocation, pub/sub, state store 같은 분산 시스템 building block을 sidecar로 얻는 방법을 보여드립니다.

---

<!-- toc:begin -->
## 시리즈 목차

- [Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기](./01-what-is-aca.md)
- [Environment·Container App·Revision — 세 단어로 보는 ACA](./02-environment-app-revision.md)
- [첫 앱 배포하기 — Python/FastAPI](./03-first-deploy.md)
- [Ingress와 트래픽 분할 — Revision 기반 배포 전략](./04-ingress-and-traffic-split.md)
- **스케일링 — KEDA scaler와 0-to-N (현재 글)**
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
