---
title: What is Azure Container Apps? — running containers without Kubernetes
series: azure-aca-101
episode: 1
language: en
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
- Serverless
- KEDA
- Dapr
- Containers
last_reviewed: '2026-05-03'
seo_description: Azure Container Apps (ACA) is a managed serverless platform that simplifies container deployment by abstracting Kubernetes cluster management.
---

# What is Azure Container Apps? — running containers without Kubernetes

At first glance, Azure Container Apps looks like the missing middle ground between App Service and AKS. To use it well, you need a clear mental model of what the platform abstracts away and what still belongs to you.

This is the first post in the Azure Container Apps 101 series. Here, we'll place ACA on the Azure container map and define the workloads it fits best.

---

## What you will learn

- How Azure Container Apps (ACA) differs from the other Azure container services (App Service, AKS, Functions)
- The role of ACA's three core building blocks: Environment, Container App, and Revision
- Which workloads belong on ACA, and which workloads belong somewhere else
- How the seven episodes of this series will progressively zoom into each part of ACA

## Why this matters

Anyone can build a container. It runs fine on a laptop. The hard part is everything that comes after.

> Where do you run it. Who terminates HTTPS. How do you stop paying when traffic is zero. Who scales it. Where do logs and traces land.

Every one of those answers is bound to a platform decision. AKS gives you total freedom but you operate the cluster yourself. App Service is convenient but sidecars and KEDA-style scaling are awkward. Functions is optimized for short event handlers, not long-running containers.

ACA aims at exactly the empty space between them: **bring your own container, but let Microsoft run the cluster**.

## Mental Model

> ACA is "App Service for containers."

App Service takes your code (or a zip) and turns it into a web app with ingress, scaling, and slots wired up for you. ACA does the same trick, but the input is a container image and the scaler is KEDA, which means it can scale all the way down to zero.

> Another analogy: if AKS is "driving your own car," ACA is "calling a taxi." You pick the destination (image) and a few preferences (scale rules, ingress); the cluster stays out of sight.

## The big picture — one ACA environment at a glance

This diagram is the map for the whole series. Later posts zoom into each box.

- Clients and ingress: episode 4
- Environment, Container App, Revision: episode 2
- First deployment: episode 3
- KEDA scaling: episode 5
- Dapr: episode 6
- Observability: episode 7

![Ingress and app layout in one ACA environment](../../../assets/azure-aca-101/01/01-01-the-big-picture-one-aca-environment-at-a.en.png)

*Ingress and app layout in one ACA environment*

## Core concept 1 — a one-sentence definition

ACA is a **managed serverless container platform**. It runs on a Microsoft-operated Kubernetes foundation with KEDA-backed scaling, optional Dapr integration, and managed ingress baked in — but you never see or control the cluster itself.

- The container image is the deployment unit.
- Replicas shrink while idle and can scale to zero when conditions allow.
- Ingress, Revision, and observability ship inside the product.

## Core concept 2 — Azure container service comparison

| Service | Abstraction level | Best for | Trade-off |
|---|---|---|---|
| **AKS** | Low (raw Kubernetes) | Complex multi-tenant systems, fine-grained control | You operate the cluster |
| **ACA** | Medium (managed K8s) | HTTP APIs, workers, microservices | Only part of the K8s API is exposed |
| **App Service** | High (PaaS) | Classic web apps | Few non-container options |
| **Functions** | Highest (FaaS) | Event-driven, short functions | Not for long-running workloads |

ACA sits in the spot that says "not as free as AKS, but far more container-native than App Service."

## Before / After

**Before (you only know AKS)**

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

The difference is one command versus several tools. When a small API does not need K8s complexity, ACA shines.

## Hands-on — create your first ACA environment

Real deployments are covered in episode 3. Here we just build the environment.

### Step 1. Prepare the CLI

```bash
az login
az extension add --name containerapp --upgrade
az provider register --namespace Microsoft.App
```

### Step 2. Create a resource group and an environment

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

### Step 3. Deploy a hello-world image

```bash
az containerapp up \
  --name hello-aca \
  --resource-group $RG \
  --environment $ENV \
  --image mcr.microsoft.com/azuredocs/containerapps-helloworld:latest \
  --ingress external \
  --target-port 80
```

The final output prints a `https://hello-aca.<unique>.azurecontainerapps.io` URL. The HTTPS certificate, ingress, and scale-to-zero are all wired up for you.

## The path of one request

Walking through the simplest HTTP request makes the platform's responsibilities concrete.

![Client request flow to an active revision](../../../assets/azure-aca-101/01/01-02-the-path-of-one-request.en.png)

*Client request flow to an active revision*

What you decide:

- build the image
- pick the port and health probe path
- define scale rules
- choose a traffic strategy (Revision split)
- decide where logs and traces go

What ACA handles for you: TLS termination, request routing, replica autoscaling, container restart, log shipping.

## Common mistakes

### Mistake 1. Treating ACA as an "AKS replacement"

ACA is a simplification of K8s, not a full exposure of every feature. If you need CRDs, custom controllers, DaemonSets, StatefulSets, or GPU scheduling, AKS is the right answer.

### Mistake 2. Always turning on scale-to-zero

Cold starts of 1-5 seconds happen, so the first request to a user-facing API will be slow. For tight SLAs, set `--min-replicas 1` and reserve scale-to-zero for batch and worker workloads.

### Mistake 3. Creating one Environment per service

The Environment is the boundary that shares VNet and log destinations. Microservices owned by the same team should sit in a single Environment so cost and operations stay manageable.

### Mistake 4. Enabling Dapr from day one

Dapr is powerful but has a learning curve. Plain HTTP APIs should start without Dapr; introduce it once pub/sub or state stores are genuinely needed (episode 6).

### Mistake 5. Putting external ingress on a worker

Workers (message consumers, batch jobs) have no external traffic, so use `--ingress disabled` or `internal`. Turning on external ingress only exposes a useless endpoint.

## How seasoned teams think about it

In production, picking ACA usually comes down to a small set of questions.

- **Do we have people to run K8s ourselves?** If not, ACA is almost certainly correct.
- **Is the workload an HTTP API + worker mix?** That is ACA's sweet spot.
- **Are idle periods long?** Scale-to-zero can cut cost dramatically.
- **Do we need K8s-native features (Operators, GPU, custom schedulers)?** Then it is AKS.
- **Is zip/code deployment more convenient than containers?** Then App Service is simpler.

If the first three answers are yes and the last two are no, ACA is the most natural fit.

## Where ACA fits

- FastAPI-based APIs
- Workers with bursty traffic
- Microservice combinations
- Services that need canary or blue-green

## Checklist

- [ ] I can describe in one paragraph how ACA differs from AKS, App Service, and Functions
- [ ] I can draw the relationship between Environment, Container App, and Revision
- [ ] I know when to enable scale-to-zero and when not to
- [ ] I can decide whether our workload fits ACA using the five questions above

## Exercises

1. For each workload below, pick AKS / ACA / App Service / Functions and write a one-line reason.
   - "A function that receives GitHub webhooks and posts to Slack"
   - "A FastAPI REST API serving roughly 100 req/s on average"
   - "A GPU-based model training pipeline"
   - "A system of 30 microservices wired together with a service mesh"
2. Follow Steps 1-3 above, build your first ACA environment, and hit the hello-world URL. Compare the latency of the first request and the second to feel the cold-start effect first hand.

## Summary

- ACA is a managed serverless container platform — "bring your own container, leave the cluster to us."
- The Environment is the shared boundary; the App and the Revision are the day-to-day operational units.
- It is not as free as AKS, but KEDA-based scale-to-zero and revision-based traffic split ship by default.
- When the workload is an HTTP API + worker mix with variable traffic, ACA is the most natural choice.
- Hiding the cluster does not hide the decisions about ingress, scaling, rollout, and observability — those remain yours.

## Next up

The next post zooms into ACA's operational model through three words: Environment, Container App, and Revision.

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
