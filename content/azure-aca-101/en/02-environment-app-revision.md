---
title: "Azure Container Apps 101 (2/7): Environment, Container App, Revision — ACA in three words"
series: azure-aca-101
episode: 2
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
- Azure
- Container Apps
- Revision
- Environment
- Blue-Green
- Canary
last_reviewed: '2026-05-03'
seo_description: Environment is "the building," Container App is "the office," Revision
  is "today's seating arrangement."
---

# Azure Container Apps 101 (2/7): Environment, Container App, Revision — ACA in three words

Environment, Container App, and Revision show up everywhere in ACA. The names sound close, but they carry different lifetimes and responsibilities, and that distinction drives how you deploy and operate the platform.

This is post 2 in the Azure Container Apps 101 series. Here, we'll separate those three terms from an operator's point of view.

## Questions to Keep in Mind

- The exact responsibilities of ACA's three operational units — Environment, Container App, and Revision?
- Which changes create a new Revision and which do not?
- The difference between Single Revision mode and Multiple Revision mode, and when each fits?

## Big Picture

![azure container apps 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-101/02/02-01-start-with-the-hierarchy.en.png)

*azure container apps 101 chapter 2 flow overview*

This picture places Environment, Container App, Revision — ACA in three words inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Environment, Container App, Revision — ACA in three words is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Why this matters

The first time you touch ACA, the same three words show up everywhere in the portal and CLI: Environment, Container App, Revision. They sound similar but they have very different **lifetimes, mutability, and ownership**.

Confusing them tends to produce a familiar set of incidents:

- A separate Environment per service per team — costs and operational load explode
- "I only changed an env var" but a new Revision was created and traffic skipped a beat
- "I rolled back" but the system actually has yet another new Revision sitting around
- Trying canary deploys on Single mode and discovering 100% of traffic flipped to the new version at once

This post breaks those three words apart from an operational point of view.

## Mental Model

> Environment is "the building," Container App is "the office," Revision is "today's seating arrangement."

The building (Environment) is built once and lasts. Shared infrastructure — VNet, log destination, Dapr common configuration — lives at this level.

The office (Container App) is one company inside the building. It has a service identity such as "orders API" or "payments worker," and it keeps the same name and endpoint over time.

The seating (Revision) is a snapshot of the office at one point in time. Move a single chair and you have a new arrangement; if you do not like it, go back to yesterday's layout.

## Start with the hierarchy

Environment is a boundary. Container App is a logical service. Revision is an immutable snapshot of image and configuration.

The cardinality is:

- One Environment can hold many Container Apps.
- One Container App can have many Revisions over time.
- One Revision is bound to exactly one image and one configuration set.

## Core concept 1 — Environment

The Environment is the **shared boundary** in ACA. Every app inside one Environment shares:

- The same VNet (network boundary, internal traffic possible)
- The same Log Analytics workspace (log destination)
- The same Dapr component definitions
- The same region (you need a separate Environment per region)

> Environments are not something you create often. Group them by **team**, by **environment (dev/staging/prod)**, or by **regulatory boundary** so that cost, ops, and observability all stay manageable.

## Core concept 2 — Container App

The Container App is the **service identity** that survives over time. URL endpoint, name, ingress configuration, and secrets all live at this level.

A Container App owns:

- An image reference
- Environment variables and secret references
- Ingress (external / internal / disabled)
- CPU/memory resource limits
- Scale rules (min/max replicas, KEDA scalers)

Changing some of these properties causes the Container App to automatically create a **new Revision** to apply the change. The next section lists which.

## Core concept 3 — Revision

A Revision is an **immutable snapshot of image plus configuration**. Once created, a Revision is never modified. To apply a change you create a new Revision and shift traffic to it.

- Can receive a traffic weight (0%–100%)
- Has an active/inactive state
- Traffic can be flipped back to a previous Revision instantly — that is your rollback
- "Rollback" does not create a new Revision — it only adjusts weights on existing ones

## Before / After

**Before — one Environment per (team × service × stage)**

```bash
az containerapp env create --name env-orders-dev ...
az containerapp env create --name env-orders-staging ...
az containerapp env create --name env-orders-prod ...
az containerapp env create --name env-payments-dev ...
# ... Environment count explodes
# Cost: separate Log Analytics workspace, separate VNet
# Ops: register Dapr components in each environment
```

**After — one Environment per (team × stage)**

```bash
az containerapp env create --name env-team-a-dev ...
az containerapp env create --name env-team-a-prod ...
# Place orders, payments, notifications inside one environment
az containerapp create --name orders --environment env-team-a-prod ...
az containerapp create --name payments --environment env-team-a-prod ...
az containerapp create --name notifications --environment env-team-a-prod ...
```

The difference is concrete. The second layout allows free internal calls inside one VNet, sends logs to one workspace, and registers Dapr components only once.

## Hands-on — observe Revisions in action

### Step 1. Create a Container App in Multiple revision mode

```bash
RG=rg-aca-demo
ENV=aca-env-demo

az containerapp create \
  --name myapi \
  --resource-group $RG \
  --environment $ENV \
  --image mcr.microsoft.com/azuredocs/containerapps-helloworld:latest \
  --ingress external \
  --target-port 80 \
  --revisions-mode multiple
```

### Step 2. Create a second Revision with a new image

```bash
az containerapp update \
  --name myapi \
  --resource-group $RG \
  --image myregistry.azurecr.io/myapi:v2 \
  --revision-suffix v2
```

### Step 3. Split traffic between the two Revisions (canary)

```bash
az containerapp ingress traffic set \
  --name myapi \
  --resource-group $RG \
  --revision-weight myapi--<v1-suffix>=90 myapi--<v2-suffix>=10
```

### Step 4. Roll back instantly when something breaks

```bash
az containerapp ingress traffic set \
  --name myapi \
  --resource-group $RG \
  --revision-weight myapi--<v1-suffix>=100 myapi--<v2-suffix>=0
```

The point: **rollback is a weight adjustment, not a new deploy**. It completes within seconds.

## Common mistakes

### Mistake 1. One Environment per service

As in the Before example, the count explodes. Create Environments only by **team × stage** as a baseline.

### Mistake 2. Canary on Single mode

Single revision mode automatically flips 100% of traffic to a new Revision the moment it appears. Canary or Blue-Green requires `--revisions-mode multiple` from the start.

### Mistake 3. Treating "rollback" as redeploying the previous image

In ACA, rollback is **bumping the previous Revision's weight back to 100%**. No new deployment, no rebuild, no image push. For the same reason, it is wise to keep recent Revisions around for a while.

### Mistake 4. Assuming env var edits are zero-downtime

Changes to env vars, image tag, or scale rules create a new Revision and route traffic to it. While ingress is updating routing, a brief startup delay can occur. To guarantee zero downtime, configure separate health and startup probes.

### Mistake 5. Leaving too many inactive Revisions around

Inactive Revisions are not expensive, but they clutter the portal and CLI list. Decide a policy such as "keep the last N" and deactivate older ones regularly.

## How seasoned teams think about it

In production, separating these three is really about separating **the blast radius of changes**.

- **Environment changes** should be rare. When they happen, they are big infrastructure decisions (VNet, region, Log workspace).
- **Container App changes** are made carefully. Renaming or changing ingress can change the external URL.
- **Revision changes** happen frequently. A new Revision per deploy is normal and expected.

Healthy ACA operations preserve that asymmetry: Environment rarely, Container App occasionally, Revision daily.

## Which changes create a new Revision

The following changes **create a new Revision**:

- Container image change
- Adding, modifying, or removing environment variables
- Secret change
- CPU/memory limit change
- Scale rule change (min/max, KEDA scalers)
- Dapr configuration change

The following changes **do not create a new Revision**:

- Traffic weight adjustment (rollback fits here)
- Toggling a Revision active/inactive
- Container App-level tag change

## Checklist

- [ ] I can draw the cardinality (1:N:N) between Environment, Container App, and Revision
- [ ] I can list at least five changes that create a new Revision
- [ ] I can pick between Single mode and Multiple mode for our service
- [ ] I know that rollback is a weight adjustment, not a redeploy
- [ ] I can explain why we should not create one Environment per service

## Exercises

1. For each scenario, identify whether the change is at the Environment, Container App, or Revision level.
   - "Bump the orders API image tag from v1.2.3 to v1.2.4"
   - "Switch the payments service ingress from internal to external"
   - "The team decides to move all of staging to a different region"
   - "Send 5% of production traffic to the new version"
2. Follow Steps 1-4 above to create two Revisions and split weight 50/50. Then call each endpoint 100 times and measure the actual distribution.

## Summary

- The Environment is shared infrastructure — created rarely.
- The Container App is the service identity that crosses time.
- The Revision is an immutable snapshot of image plus config and is the actual deployment unit.
- Single mode fits simple services; Multiple mode is required for canary or Blue-Green.
- In ACA, rollback is **weight adjustment**, not a new deploy — it completes within seconds.

## Next up

The next post puts this model into your hands. We deploy a Python/FastAPI app to ACA for the first time and watch a Container App and its Revision get created step by step.

## Answering the Opening Questions

- **The exact responsibilities of ACA's three operational units — Environment, Container App, and Revision?**
  - The article treats Environment, Container App, Revision — ACA in three words as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which changes create a new Revision and which do not?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **The difference between Single Revision mode and Multiple Revision mode, and when each fits?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Azure Container Apps 101 (1/7): What is Azure Container Apps? — running containers without Kubernetes](./01-what-is-aca.md)
- **Azure Container Apps 101 (2/7): Environment, Container App, Revision — ACA in three words (current)**
- Azure Container Apps 101 (3/7): Your first deploy — Python/FastAPI (upcoming)
- Azure Container Apps 101 (4/7): Ingress and traffic splitting — revision-based deployment strategies (upcoming)
- Azure Container Apps 101 (5/7): Scaling — KEDA scalers and zero-to-N (upcoming)
- Azure Container Apps 101 (6/7): Dapr integration — what you get from a sidecar (upcoming)
- Azure Container Apps 101 (7/7): Monitoring and ops — Log Analytics and Application Insights (upcoming)

<!-- toc:end -->

---

## References

### Official Docs
- [Azure Container Apps environments — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/environment)
- [Update and deploy changes in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/revisions)
- [Manage revisions in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/revisions-manage)
- [Azure Container Apps overview — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/overview)

### Related Series
- [Azure App Service 101](../../azure-app-service-101/en/01-what-is-app-service.md)
- [Azure AKS 101](../../azure-aks-101/en/01-what-is-aks.md)
- [Azure Functions 101](../../azure-functions-101/en/01-what-is-azure-functions.md)

Tags: Azure, Container Apps, Serverless, Containers
