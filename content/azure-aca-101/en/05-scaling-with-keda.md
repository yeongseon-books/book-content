---
title: Scaling — KEDA scalers and zero-to-N
series: azure-aca-101
episode: 5
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

# Scaling — KEDA scalers and zero-to-N

> Azure Container Apps 101 series (5/7)

This post explains the KEDA-based scaling path.
It separates built-in HTTP and TCP rules.
And custom KEDA rules such as Service Bus, CPU, and memory.

---

## The scaling path

Scaling remains declarative.
You choose the signal and the replica bounds.

![Scale signals changing replica counts](../../../assets/azure-aca-101/05/05-01-the-scaling-path.en.png)
---

## Three rule categories

- **HTTP scale rule** — the built-in rule used for ingress-enabled HTTP apps, based on concurrent requests.
- **TCP scale rule** — the built-in rule used for TCP apps, based on concurrent connections.
- **Custom scale rules** — any KEDA scaler you attach, including Service Bus, Event Hubs, Kafka, Redis, and resource-based scalers such as CPU and memory.

---

## Scale-to-zero

HTTP and TCP rules can scale to zero.
Many custom event-driven KEDA rules can also scale to zero.
CPU and memory live under the custom-rule bucket, but they still do not scale to zero according to Microsoft Learn.

---

## HTTP example

```bash
az containerapp create   --name $APP_NAME   --resource-group $RG   --environment $ACA_ENV   --image $IMAGE   --ingress external   --target-port 8000   --min-replicas 0   --max-replicas 5   --scale-rule-name http-rule   --scale-rule-type http   --scale-rule-http-concurrency 100
```

---

## Service Bus example

```bash
az containerapp create   --name queue-worker   --resource-group $RG   --environment $ACA_ENV   --image $IMAGE   --min-replicas 0   --max-replicas 10   --secrets "sb-connection=<SERVICE_BUS_CONNECTION_STRING>"   --scale-rule-name servicebus-rule   --scale-rule-type azure-servicebus   --scale-rule-metadata "queueName=orders" "namespace=mybus.servicebus.windows.net" "messageCount=5"   --scale-rule-auth "connection=sb-connection"
```

---

## What matters operationally

- Pick the trigger family first: HTTP, TCP, or custom.
- Treat min replicas as an availability and latency decision, not just a cost knob.
- Read every scaling discussion together with the workload's queue depth, request shape, and cold-start tolerance.

---

<!-- toc:begin -->
## In this series

- [What is Azure Container Apps? — running containers without Kubernetes](./01-what-is-aca.md)
- [Environment, Container App, Revision — ACA in three words](./02-environment-app-revision.md)
- [Your first deploy — Python/FastAPI](./03-first-deploy.md)
- [Ingress and traffic splitting — revision-based deployment strategies](./04-ingress-and-traffic-split.md)
- **Scaling — KEDA scalers and zero-to-N (current)**
- Dapr integration — what you get from a sidecar (upcoming)
- Monitoring and ops — Log Analytics and Application Insights (upcoming)

<!-- toc:end -->

---

## References

### Official Docs
- [Scaling in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/scale-app)
- [Azure Container Apps overview — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/overview)
- [KEDA scalers documentation](https://keda.sh/docs/scalers/)

### Related Series
- [Azure App Service 101](../../azure-app-service-101/en/01-what-is-app-service.md)
- [Azure AKS 101](../../azure-aks-101/en/01-what-is-aks.md)
- [Azure Functions 101](../../azure-functions-101/en/01-what-is-azure-functions.md)

Tags: Azure, Container Apps, Serverless, Containers
