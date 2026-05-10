---
title: Dapr 통합 — 사이드카로 얻는 것
series: azure-aca-101
episode: 6
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
- Dapr
- Sidecar
- Pub-Sub
- Service Invocation
last_reviewed: '2026-04-29'
seo_description: Dapr를 두 개의 "수준"으로 보면 단순해집니다.
---

# Dapr 통합 — 사이드카로 얻는 것

> Azure Container Apps 101 시리즈 (6/7)

## 이 글에서 배울 것

- Dapr가 무엇이고 ACA의 어느 위치에 사이드카로 붙는지 이해합니다.
- App 수준 설정과 Environment 수준 component의 분리를 구분할 수 있습니다.
- Service invocation, Pub/Sub, State store, Secret store 네 가지 building block의 역할을 설명할 수 있습니다.
- `--enable-dapr` 플래그와 component YAML로 실제 Dapr 통합을 구성할 수 있습니다.

<!-- a-grade-intro:begin -->
## 핵심 질문

Dapr 사이드카를 도입하면 무엇이 쉬워지고 무엇을 새로 책임져야 할까요?

이 글은 그 질문에 답하기 위해 Dapr 통합의 핵심 결정과 운영 함정을 살펴봅니다.

<!-- a-grade-intro:end -->

## 이 글에서 답할 질문

- Dapr 사이드카는 ACA pod 안 어디에 붙고, 앱은 어떤 endpoint로 호출하는가?
- App-level `--enable-dapr` 설정과 Environment-level component는 왜 분리되어 있는가?
- Service invocation, Pub/Sub, State store, Secret store는 각각 어떤 문제를 해결하는가?
- AKS에서 Dapr를 운영하는 것과 ACA에서 쓰는 것의 결정적 차이는 무엇인가?
- Dapr를 "처음부터 켜는 것"이 왜 안티패턴으로 자주 지적되는가?

## 왜 중요한가

마이크로서비스를 만들면 똑같은 문제가 반복됩니다.
서비스 A가 서비스 B를 호출하려면 service discovery가 필요하고, 둘 사이에 메시지를 주고받으려면 메시지 브로커 SDK를 골라야 하고, 상태를 저장하려면 Redis나 Cosmos DB SDK를 직접 다뤄야 합니다.
**Dapr는 이 네 가지 문제를 표준 HTTP/gRPC API로 추상화합니다.** 앱은 `localhost:3500`의 Dapr 사이드카에 요청을 보내고, 사이드카가 실제 backend(Service Bus, Redis, Key Vault 등)와 통신합니다.

ACA에서 Dapr가 특히 매력적인 이유는 **runtime 설치가 0**이기 때문입니다.
Kubernetes에서 Dapr를 쓰려면 Helm chart를 설치하고 control plane을 운영해야 하지만, ACA는 control plane을 플랫폼이 직접 관리합니다.
앱에서 `--enable-dapr true` 한 줄이면 사이드카가 자동으로 주입됩니다.

## Mental Model

Dapr를 두 개의 "수준"으로 보면 단순해집니다.

1. **App 수준** — 이 앱이 Dapr를 쓰는가? `app-id`는 무엇인가? 앱이 듣는 포트는?
2. **Environment 수준** — 이 ACA Environment가 어떤 component를 제공하는가? Service Bus를 pubsub으로 쓸 것인가, Redis를 state store로 쓸 것인가?

App 수준은 **개별 앱의 옵트인**, Environment 수준은 **공유 인프라 카탈로그**입니다.
component 하나를 Environment에 등록하면, 같은 Environment의 여러 앱이 scope 설정으로 그 component를 공유합니다.

![앱 옆 Dapr 사이드카와 외부 서비스 연결 구조](../../../assets/azure-aca-101/06/06-01-where-dapr-sits.ko.png)

*앱 옆 Dapr 사이드카와 외부 서비스 연결 구조*

## 핵심 개념

### 1. 사이드카 모델

`--enable-dapr true`를 주면 ACA가 앱 컨테이너 옆에 `daprd` 사이드카를 함께 띄웁니다.
앱은 자기 비즈니스 로직만 작성하고, 외부 시스템과의 통신은 사이드카에 위임합니다.

```
┌─────────────────────────────────────┐
│  Container App: api-app             │
│  ┌──────────────┐  ┌─────────────┐  │
│  │ Your code    │  │ Dapr        │  │
│  │ FastAPI      │◄─┤ sidecar     │──┼──► Service Bus
│  │ :8000        │  │ :3500       │  │    Redis
│  └──────────────┘  └─────────────┘  │    Key Vault
└─────────────────────────────────────┘
```

### 2. 네 가지 핵심 building block

| Building block | 역할 | ACA 대표 backend |
| --- | --- | --- |
| **Service invocation** | 앱 간 호출 (service discovery + retry + mTLS) | 다른 Container App (`app-id` 기반) |
| **Pub/Sub** | 메시지 발행·구독 | Azure Service Bus, Event Hubs, Kafka |
| **State store** | key-value 상태 저장 | Cosmos DB, Redis, PostgreSQL |
| **Secret store** | secret 조회 추상화 | Azure Key Vault, ACA secrets |

### 3. Component와 scope

Component YAML은 "이 backend를 어떤 이름으로 사용할지" 정의합니다.
`scopes:` 필드로 어떤 `app-id`가 그 component에 접근할지 명시적으로 제한합니다.
scope를 비우면 같은 Environment의 모든 앱이 사용 가능합니다 — 운영에서는 항상 명시하는 편이 안전합니다.

## Before-After

### Before (Dapr 없이 직접 SDK 사용)

```python
# Service Bus SDK 직접 사용
from azure.servicebus import ServiceBusClient, ServiceBusMessage

connection_str = os.environ["SERVICE_BUS_CONNECTION_STRING"]
with ServiceBusClient.from_connection_string(connection_str) as client:
    sender = client.get_queue_sender(queue_name="orders")
    sender.send_messages(ServiceBusMessage("order-123"))
```

backend가 바뀌면(Service Bus → Kafka) SDK, 의존성, 코드를 모두 교체해야 합니다.

### After (Dapr Pub/Sub API)

```python
import requests

requests.post(
    "http://localhost:3500/v1.0/publish/orderpubsub/orders",
    json={"orderId": "order-123"}
)
```

backend가 바뀌어도 코드는 그대로입니다. component YAML만 교체하면 됩니다.

## 단계별 실습

### Step 1: 앱에 Dapr 활성화

```bash
RG=rg-aca-demo
ACA_ENV=aca-env-demo
IMAGE=myacr.azurecr.io/api-app:latest

az containerapp create \
  --name api-app --resource-group $RG --environment $ACA_ENV \
  --image $IMAGE --ingress external --target-port 8000 \
  --enable-dapr true \
  --dapr-app-id api-app \
  --dapr-app-port 8000
```

이미 만든 앱이라면:

```bash
az containerapp dapr enable \
  --name api-app --resource-group $RG \
  --dapr-app-id api-app --dapr-app-port 8000
```

### Step 2: Pub/Sub component 등록 (Service Bus)

`pubsub.yaml`:

```yaml
componentType: pubsub.azure.servicebus.queues
version: v1
metadata:
  - name: namespaceName
    value: mybus.servicebus.windows.net
  - name: connectionString
    secretRef: servicebus-connection-string
secrets:
  - name: servicebus-connection-string
    value: "<SERVICE_BUS_CONNECTION_STRING>"
scopes:
  - api-app
  - worker-app
```

```bash
az containerapp env dapr-component set \
  --name $ACA_ENV --resource-group $RG \
  --dapr-component-name orderpubsub \
  --yaml pubsub.yaml
```

### Step 3: 앱에서 호출

```python
import requests

# 발행
requests.post(
    "http://localhost:3500/v1.0/publish/orderpubsub/orders",
    json={"orderId": "order-123"}
)

# 다른 앱 호출 (service invocation)
requests.post(
    "http://localhost:3500/v1.0/invoke/worker-app/method/process",
    json={"orderId": "order-123"}
)
```

## 자주 하는 실수

- **App 수준 enable과 Environment 수준 component를 혼동** — 앱에서 `--enable-dapr`만 켜고 component를 등록하지 않으면 사이드카는 떠도 publish가 실패합니다.
- **Scope 미지정** — 모든 앱이 모든 component에 접근 가능해져 보안 경계가 무너집니다.
- **Secret을 inline value로 작성** — component YAML에 connection string을 평문으로 넣지 말고 `secretRef`와 `secrets:` 블록 또는 Key Vault secret store를 사용해야 합니다.
- **`dapr-app-port` 누락** — service invocation이 들어와도 사이드카가 어느 포트로 forwarding할지 몰라 502가 발생합니다.
- **HTTP API와 gRPC API 혼용 후 디버깅 혼선** — Dapr는 둘 다 지원하지만, 한 앱에서는 한 가지를 선택하는 편이 트러블슈팅에 유리합니다.

## 실무에서

언제 Dapr를 쓰고, 언제 쓰지 말까:

- **쓸 만한 경우**: 마이크로서비스 3개 이상, pub/sub과 service invocation을 모두 사용, backend를 추후 교체할 가능성이 있는 경우.
- **굳이 쓰지 않아도 되는 경우**: 단일 모놀리식 API + DB 한 개. SDK 호출이 한두 줄이면 추상화 레이어가 오히려 복잡도를 더합니다.
- **production checklist**: managed identity 기반 인증으로 전환, scope 명시, retry policy 설정, Application Insights에 Dapr telemetry 연동.

ACA의 Dapr 버전은 플랫폼이 관리하므로, breaking change가 있는 major upgrade는 release notes를 확인해야 합니다.

## 실무에서는 이렇게 생각한다

Dapr를 도입할지 말지는 "마이크로서비스가 몇 개냐"로 판단하는 것이 가장 빠릅니다. 앱이 2–3개이고 통신 패턴이 단순 HTTP라면, Dapr 사이드카가 추가하는 복잡도가 이점보다 큽니다. 반면 앱이 5개 이상이고 pub/sub, state store, secret 관리가 모두 필요한 환경이라면, 각 앱에서 별도 SDK를 붙이는 것보다 Dapr building block으로 통일하는 편이 운영 부담을 줄입니다.

Dapr component YAML은 ACA Environment 단위로 관리되므로, 여러 앱이 같은 state store를 공유할 때 편리합니다. 하지만 이것이 양날의 검이 될 수 있습니다. 한 팀이 component YAML을 변경하면 같은 Environment의 모든 앱에 영향을 줍니다. Environment를 팀 또는 도메인 단위로 분리할지, 하나로 묶을지는 초기에 결정해두는 것이 좋습니다.

마이그레이션 관점에서 Dapr는 "점진적 도입"이 가능합니다. 모든 앱을 한꺿번에 Dapr로 전환할 필요 없이, 새로 추가하는 앱부터 Dapr를 켜고 기존 앱은 그대로 둘 수 있습니다. 다만 하이브리드 구성에서는 Dapr 앱과 비-Dapr 앱 간 통신 방식이 달라지므로, 호출 경로를 문서화해두지 않으면 혼란이 옵니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **Dapr은 인터페이스 통일이 본질** — 메시징·상태·시크릿을 추상화해 벤더 종속을 줄입니다.
- **컴포넌트 설정을 IaC로 관리한다** — 런타임 변경은 추적이 어려우므로 코드로 둡니다.
- **관측은 분산 트레이싱 기본으로 연결한다** — 사이드카 추가로 호출 경로가 늘어나므로 trace가 필수입니다.
- **재시도·타임아웃은 클라이언트와 일치시킨다** — Dapr이 자동 재시도를 추가하므로 의도치 않은 중복 호출을 막습니다.
- **불필요한 곳에는 도입하지 않는다** — 단순 HTTP 호출만 있는 앱에 Dapr을 강제하면 복잡성만 늘어납니다.

## 체크리스트

- [ ] `--enable-dapr true`와 `--dapr-app-id`, `--dapr-app-port`를 모두 설정했는가?
- [ ] component YAML이 Environment에 등록되었는가?
- [ ] `scopes:`로 접근 가능한 app-id를 명시했는가?
- [ ] Secret이 inline value가 아니라 `secretRef` 또는 Key Vault로 관리되는가?
- [ ] Service invocation과 Pub/Sub 호출 경로가 Application Insights에서 추적 가능한가?
- [ ] 단일 앱 시나리오라면 Dapr가 정말 필요한지 재검토했는가?

## 연습 문제

1. 같은 Environment에 두 개의 앱(`api-app`, `worker-app`)이 있고, `api-app`만 Service Bus pubsub component를 사용해야 합니다. component YAML의 `scopes:`를 어떻게 작성하시겠습니까?
2. Dapr service invocation과 직접 HTTP 호출(앱 FQDN으로 호출)의 차이점 세 가지를 나열하세요.
3. State store backend를 Redis에서 Cosmos DB로 바꾸려고 합니다. 앱 코드는 얼마나 바뀌어야 하나요? 이유는?

## 정리·다음 글

이번 글의 핵심:

- Dapr는 사이드카로 동작하며, 분산 시스템 building block을 표준 API로 추상화합니다.
- App 수준 설정(enable, app-id)과 Environment 수준 component 정의는 다른 결정입니다.
- 네 가지 핵심 building block: Service invocation, Pub/Sub, State store, Secret store.
- Scope, secret 관리, retry policy는 Dapr가 자동으로 정해 주지 않으므로 명시적으로 설계해야 합니다.

다음 글에서는 시리즈 마지막 주제 **모니터링과 운영**을 다룹니다.
Log Analytics와 Application Insights를 ACA에 연결해 로그·메트릭·trace를 수집하고, 운영 알림을 구성하는 방법을 보여드립니다.

---

<!-- toc:begin -->
## 시리즈 목차

- [Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기](./01-what-is-aca.md)
- [Environment·Container App·Revision — 세 단어로 보는 ACA](./02-environment-app-revision.md)
- [첫 앱 배포하기 — Python/FastAPI](./03-first-deploy.md)
- [Ingress와 트래픽 분할 — Revision 기반 배포 전략](./04-ingress-and-traffic-split.md)
- [스케일링 — KEDA scaler와 0-to-N](./05-scaling-with-keda.md)
- **Dapr 통합 — 사이드카로 얻는 것 (현재 글)**
- 모니터링과 운영 — Log Analytics와 Application Insights (예정)

<!-- toc:end -->

---

## 참고 자료

### 공식 문서
- [Configure Dapr on an Existing Container App — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/enable-dapr)
- [Microservice APIs powered by Dapr — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/dapr-overview)
- [Dapr Components in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/dapr-components)
- [Dapr overview](https://docs.dapr.io/concepts/overview/)

### 관련 시리즈
- [Azure App Service 101](../../azure-app-service-101/ko/01-what-is-app-service.md)
- [Azure AKS 101](../../azure-aks-101/ko/01-what-is-aks.md)
- [Azure Functions 101](../../azure-functions-101/ko/01-what-is-azure-functions.md)

Tags: Azure, Container Apps, Serverless, Containers
