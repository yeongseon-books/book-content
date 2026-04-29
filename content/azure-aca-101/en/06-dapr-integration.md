---
title: Dapr integration — what you get from a sidecar
series: azure-aca-101
episode: 6
language: en
status: ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Azure
- Container Apps
- Serverless
- Containers
last_reviewed: '2026-04-29'
---

# Dapr integration — what you get from a sidecar

> Azure Container Apps 101 series (6/7)

This post shows where the Dapr sidecar sits and what it simplifies. Service invocation, pub/sub, state, and secret access are the four recurring themes, but the main operational lesson is scope: some settings live on the app, while components and secret wiring live at the environment boundary.

---

## Where Dapr sits

The sidecar sits next to the app.
It mediates access to Environment-level components and external services.

![Where Dapr sits](../../../assets/azure-aca-101/06/06-01-where-dapr-sits.en.png)
---

## Enable commands

```bash
az containerapp create   --name api-app   --resource-group $RG   --environment $ACA_ENV   --image $IMAGE   --ingress external   --target-port 8000   --enable-dapr true   --dapr-app-id api-app   --dapr-app-port 8000

az containerapp dapr enable   --name api-app   --resource-group $RG   --dapr-app-id api-app   --dapr-app-port 8000
```

---

## App scope and Environment scope

- App level — enablement, app ID, app port
- Environment level — component definitions and scopes

---

## Key building blocks

- Service invocation
- Pub/Sub
- State store
- Secret store

---

## Component sketch: enough to read, not a copy-paste file

```yaml
componentType: pubsub.azure.servicebus.queue
version: v1
metadata:
  - name: namespaceName
    value: mybus.servicebus.windows.net
  - name: queueName
    value: orders
  - name: connectionString
    secretRef: servicebus-connection-string
scopes:
  - publisher-app
  - subscriber-app
```

Treat this as a schematic, not as a ready-to-apply manifest. A runnable ACA Dapr component also needs the secret value to exist at the environment level, and the exact auth path depends on whether you use connection strings, managed identity, or another supported component auth pattern.

---

## What matters operationally

- Dapr enablement on the app and component definition in the environment are different decisions.
- Component YAML without auth wiring is only a diagram, not a deployment plan.
- Dapr reduces plumbing code, but it does not remove the need to choose scopes, retry behavior, and failure handling deliberately.

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
