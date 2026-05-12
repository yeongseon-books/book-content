---
title: Dapr integration — what you get from a sidecar
series: azure-aca-101
episode: 6
language: en
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
seo_description: 'Think of Dapr at two levels:'
---

# Dapr integration — what you get from a sidecar

Dapr removes a lot of repeated plumbing in microservices, but it does not erase architectural trade-offs. You need to keep App-level settings separate from Environment-level components to see where the platform ends and your design begins.

This is post 6 in the Azure Container Apps 101 series. Here, we'll examine what the sidecar gives you on ACA and what it asks you to own.

## What you'll learn

- What Dapr is and where its sidecar attaches inside ACA.
- How to separate App-level configuration from Environment-level components.
- The role of the four core building blocks: Service invocation, Pub/Sub, State store, Secret store.
- How to configure a real Dapr integration with `--enable-dapr` and component YAML.

## Questions this chapter answers

- Where exactly does the Dapr sidecar attach inside an ACA pod, and what endpoint does the app call?
- Why are App-level `--enable-dapr` settings separated from Environment-level components?
- What problems do Service invocation, Pub/Sub, State store, and Secret store each solve?
- What is the decisive difference between running Dapr on AKS versus on ACA?
- Why is "enabling Dapr from day one" often cited as an anti-pattern?

## Why this matters

Microservices keep posing the same problems.
Service A calling Service B needs service discovery; sending messages between them needs a broker SDK; storing state needs a Redis or Cosmos DB SDK.
**Dapr abstracts all four behind a standard HTTP/gRPC API.** Your app talks to the Dapr sidecar at `localhost:3500`, and the sidecar talks to the actual backend (Service Bus, Redis, Key Vault, etc.).

Dapr is especially compelling on ACA because **runtime install is zero**.
On Kubernetes you install a Helm chart and operate the Dapr control plane yourself. On ACA, the platform manages the control plane.
Adding `--enable-dapr true` to your app injects the sidecar automatically.

## Mental Model

Think of Dapr at two levels:

1. **App level** — does this app use Dapr? What is its `app-id`? What port does the app listen on?
2. **Environment level** — what components does this ACA Environment provide? Service Bus as pubsub? Redis as state store?

App level is **per-app opt-in**. Environment level is a **shared infrastructure catalog**.
Register one component on the Environment, and many apps in the same Environment can share it through scope settings.

![Dapr sidecar next to the app and connections to external services](../../../assets/azure-aca-101/06/06-01-where-dapr-sits.en.png)

*Dapr sidecar next to the app and connections to external services*

## Core concepts

### 1. The sidecar model

`--enable-dapr true` makes ACA spin up a `daprd` sidecar next to your app container.
Your code holds business logic; communication with external systems is delegated to the sidecar.

```text
┌─────────────────────────────────────┐
│  Container App: api-app             │
│  ┌──────────────┐  ┌─────────────┐  │
│  │ Your code    │  │ Dapr        │  │
│  │ FastAPI      │◄─┤ sidecar     │──┼──► Service Bus
│  │ :8000        │  │ :3500       │  │    Redis
│  └──────────────┘  └─────────────┘  │    Key Vault
└─────────────────────────────────────┘
```

### 2. Four core building blocks

| Building block | Role | Common ACA backend |
| --- | --- | --- |
| **Service invocation** | App-to-app calls (service discovery + retry + mTLS) | Another Container App (by `app-id`) |
| **Pub/Sub** | Publish/subscribe messaging | Azure Service Bus, Event Hubs, Kafka |
| **State store** | Key-value state storage | Cosmos DB, Redis, PostgreSQL |
| **Secret store** | Secret lookup abstraction | Azure Key Vault, ACA secrets |

### 3. Components and scope

A component YAML defines "use this backend under this name."
The `scopes:` field explicitly limits which `app-id`s can access it.
Empty scope means every app in the Environment can use it — in production, always set it explicitly.

## Before-After

### Before (calling SDKs directly)

```python
# Service Bus SDK directly
from azure.servicebus import ServiceBusClient, ServiceBusMessage

connection_str = os.environ["SERVICE_BUS_CONNECTION_STRING"]
with ServiceBusClient.from_connection_string(connection_str) as client:
    sender = client.get_queue_sender(queue_name="orders")
    sender.send_messages(ServiceBusMessage("order-123"))
```

Switch backends (Service Bus → Kafka) and you replace the SDK, dependencies, and code.

### After (Dapr Pub/Sub API)

```python
import requests

requests.post(
    "http://localhost:3500/v1.0/publish/orderpubsub/orders",
    json={"orderId": "order-123"}
)
```

Backend swap touches only the component YAML — your code stays untouched.

## Step-by-step

### Step 1: Enable Dapr on the app

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

For an existing app:

```bash
az containerapp dapr enable \
  --name api-app --resource-group $RG \
  --dapr-app-id api-app --dapr-app-port 8000
```

### Step 2: Register a Pub/Sub component (Service Bus)

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

### Step 3: Call from your app

```python
import requests

# Publish
requests.post(
    "http://localhost:3500/v1.0/publish/orderpubsub/orders",
    json={"orderId": "order-123"}
)

# Invoke another app (service invocation)
requests.post(
    "http://localhost:3500/v1.0/invoke/worker-app/method/process",
    json={"orderId": "order-123"}
)
```

## Common pitfalls

- **Confusing app-level enable with environment-level components** — flipping `--enable-dapr` without registering a component starts the sidecar but every publish fails.
- **No scope set** — every app gains access to every component, eroding security boundaries.
- **Inline secret values** — never put a connection string in a component YAML as plain text. Use `secretRef` with a `secrets:` block, or a Key Vault secret store.
- **Missing `dapr-app-port`** — incoming service invocation has nowhere to forward, so you get 502s.
- **Mixing HTTP and gRPC APIs in one app** — Dapr supports both, but mixing them complicates troubleshooting.

## In production

When to use Dapr and when to skip it:

- **Worth it**: 3+ microservices, both pub/sub and service invocation, plausible backend swap in the future.
- **Skip it**: a single monolithic API plus one DB. If your SDK call is one or two lines, the abstraction adds more complexity than it removes.
- **Production checklist**: switch to managed identity auth, set explicit scopes, configure retry policy, wire Dapr telemetry into Application Insights.

ACA manages the Dapr version for you — check release notes for breaking changes on major upgrades.

## Checklist

- [ ] Did I set `--enable-dapr true`, `--dapr-app-id`, and `--dapr-app-port`?
- [ ] Are component YAMLs registered on the Environment?
- [ ] Did I list explicit `scopes:` for each component?
- [ ] Are secrets managed via `secretRef` or Key Vault, not inline values?
- [ ] Are Service invocation and Pub/Sub paths visible in Application Insights?
- [ ] If this is a single-app scenario, did I reconsider whether Dapr is really needed?

## Exercises

1. The same Environment hosts `api-app` and `worker-app`, but only `api-app` should use a Service Bus pubsub component. How would you write the `scopes:` field?
2. List three differences between Dapr service invocation and a direct HTTP call to the app FQDN.
3. You want to switch a state store backend from Redis to Cosmos DB. How much app code changes? Why?

## Wrap-up and next post

Key takeaways:

- Dapr runs as a sidecar and abstracts distributed-system building blocks behind standard APIs.
- App-level config (enable, app-id) and Environment-level components are independent decisions.
- Four core building blocks: Service invocation, Pub/Sub, State store, Secret store.
- Scope, secret management, and retry policy are still your responsibility — Dapr does not pick them for you.

Next post wraps up the series with **Monitoring and ops** — connecting Log Analytics and Application Insights to ACA, collecting logs/metrics/traces, and configuring operational alerts.

---

<!-- toc:begin -->
## In this series

- [What is Azure Container Apps? — running containers without Kubernetes](./01-what-is-aca.md)
- [Environment, Container App, Revision — ACA in three words](./02-environment-app-revision.md)
- [Your first deploy — Python/FastAPI](./03-first-deploy.md)
- [Ingress and traffic splitting — revision-based deployment strategies](./04-ingress-and-traffic-split.md)
- [Scaling — KEDA scalers and zero-to-N](./05-scaling-with-keda.md)
- **Dapr integration — what you get from a sidecar (current)**
- Monitoring and ops — Log Analytics and Application Insights (upcoming)

<!-- toc:end -->

---

## References

### Official Docs
- [Configure Dapr on an Existing Container App — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/enable-dapr)
- [Microservice APIs powered by Dapr — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/dapr-overview)
- [Dapr Components in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/dapr-components)
- [Dapr overview](https://docs.dapr.io/concepts/overview/)

### Related Series
- [Azure App Service 101](../../azure-app-service-101/en/01-what-is-app-service.md)
- [Azure AKS 101](../../azure-aks-101/en/01-what-is-aks.md)
- [Azure Functions 101](../../azure-functions-101/en/01-what-is-azure-functions.md)

Tags: Azure, Container Apps, Serverless, Containers
