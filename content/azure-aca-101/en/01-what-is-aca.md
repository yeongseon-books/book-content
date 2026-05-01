---
title: What is Azure Container Apps? — running containers without Kubernetes
series: azure-aca-101
episode: 1
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

# What is Azure Container Apps? — running containers without Kubernetes

> Azure Container Apps 101 series (1/7)

Teams can usually build an image and run it locally.
The confusion starts one step later.
Where does it run.
Who handles HTTPS.
What is the deployment unit.
Where do logs and traces go.
Azure Container Apps fits that gap.
It keeps the container workflow while hiding direct Kubernetes cluster operations from the user.

---

## The big picture — one ACA environment at a glance

This diagram is the map for the whole series.
Later posts zoom into each box.
Clients and ingress return in part 4.
Environment, Container App, and Revision are part 2.
First deployment is part 3.
KEDA is part 5.
Dapr is part 6.
Observability is part 7.

![Ingress and app layout in one ACA environment](../../../assets/azure-aca-101/01/01-01-the-big-picture-one-aca-environment-at-a.en.png)
---

## A one-sentence definition

ACA is a managed serverless platform for running containerized applications.
It uses a Microsoft-managed Kubernetes foundation plus built-in capabilities such as KEDA-backed scaling, optional Dapr integration, and managed ingress, but the cluster itself is not exposed to the user.

- Container images remain the deployment unit.
- Replicas can shrink aggressively, often to zero.
- Ingress, revisioning, and observability are built into the product.

---

## Why teams reach for ACA

- APIs and workers on one platform
- lower idle cost
- revision-based canary and blue-green
- optional Dapr integration

---

## The path of one request

A single HTTP request is enough to make the boundary responsibilities visible.

- build the image correctly
- listen on the right port
- define health paths and config safely
- choose scale and rollout rules
- emit logs and traces deliberately

![Client request flow to an active revision](../../../assets/azure-aca-101/01/01-02-the-path-of-one-request.en.png)
---

## Workloads that fit well

- FastAPI APIs
- bursty workers
- microservice groups
- services that need canary or blue-green

---

## What should stick from the overview

- The environment is the shared boundary; apps and revisions are the units you will operate day to day.
- ACA hides the cluster, not the need to make explicit decisions about ingress, scaling, rollout, and telemetry.
- If those boundaries feel clear, the rest of the series becomes much easier to read.

---

<!-- blog-only:start -->
Next: [Environment, Container App, Revision — ACA in three words](./02-environment-app-revision.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## In this series

- **What is Azure Container Apps? — running containers without Kubernetes (current)**
- Environment, Container App, Revision — ACA in three words (upcoming)
- Your first deploy — Python/FastAPI (upcoming)
- Ingress and traffic splitting — revision-based deployment strategies (upcoming)
- Scaling — KEDA scalers and zero-to-N (upcoming)
- Dapr integration — what you get from a sidecar (upcoming)
- Monitoring and ops — Log Analytics and Application Insights (upcoming)

<!-- toc:end -->

---

## References

### Official Docs
- [Azure Container Apps overview — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/overview)
- [Azure Container Apps environments — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/environment)
- [Update and deploy changes in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/revisions)
- [Ingress in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/ingress-overview)

### Related Series
- [Azure App Service 101](../../azure-app-service-101/en/01-what-is-app-service.md)
- [Azure AKS 101](../../azure-aks-101/en/01-what-is-aks.md)
- [Azure Functions 101](../../azure-functions-101/en/01-what-is-azure-functions.md)

Tags: Azure, Container Apps, Serverless, Containers
