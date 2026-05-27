---
title: "Azure Container Apps 101 (4/7): Ingress and traffic splitting — revision-based deployment strategies"
series: azure-aca-101
episode: 4
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
- Ingress
- Canary
- Blue-Green
- Traffic Split
last_reviewed: '2026-05-03'
seo_description: Ingress is ACA's "front door"; traffic weight is the "elevator dispatch
  ratio."
---

# Azure Container Apps 101 (4/7): Ingress and traffic splitting — revision-based deployment strategies

Ingress and traffic splitting are two of the most important operational levers in ACA. A small configuration change can alter both exposure and rollout safety, so they make more sense together than apart.

This is the 4th post in the Azure Container Apps 101 series. Here, we'll connect ingress design to revision-based deployment strategy.

![azure container apps 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-101/04/04-01-the-request-path.en.png)
*azure container apps 101 chapter 4 flow overview*

## Questions to Keep in Mind

- What ACA's managed Ingress owns (TLS, external/internal exposure, Revision routing) and what it does not?
- The exact difference between `external`, `internal`, and `disabled` ingress modes?
- How Single mode and Multiple mode change traffic distribution behavior?

## Why this matters

One of ACA's most powerful production features is revision-based traffic split. Using it correctly first requires getting ingress right.

Common incidents:

- "External ingress is on but I cannot reach it from the internet" → `target-port` mismatch
- "I tried to send 10% to canary but 100% went to the new version" → was on Single mode
- "I heard rollback takes minutes like a redeploy" → it is a weight change, completes in seconds
- "I built it with internal ingress but the internet can reach it" → ingress mode misread

This post ties ingress and traffic split into one flow and removes the root causes of those incidents.

## Mental Model

> Ingress is ACA's "front door"; traffic weight is the "elevator dispatch ratio."

The front door (Ingress) decides whether external visitors get in (`external`), only same-building people get in (`internal`), or it stays closed (`disabled`). Once past the door, the elevator (traffic split rule) decides which office (Revision) each visitor reaches based on the configured ratio.

These two stages are separate, so you can manage "external exposure" and "version distribution" independently.

## The request path

ACA's managed Ingress layer plays the front door, then dispatches traffic to active Revisions according to weights.

Key steps:

1. Client hits `https://<app>.<env-id>.<region>.azurecontainerapps.io`
2. ACA's managed envoy proxy terminates TLS
3. The weight table for the Container App's Revisions is consulted
4. Traffic is routed to one replica of one Revision based on the ratio
5. The replica responds; logs flow to Log Analytics

## Core concept 1 — three ingress modes

| Mode | Exposure | URL | Best for |
|---|---|---|---|
| `external` | Public internet | `https://<app>.<env-id>.<region>.azurecontainerapps.io` | Public APIs, web frontends |
| `internal` | Same Environment only | `https://<app>.internal.<env-id>.<region>.azurecontainerapps.io` | Microservice-to-microservice calls |
| `disabled` | Not exposed | (none) | Workers, batch jobs, message consumers |

CLI example:

```bash
az containerapp ingress enable \
  --name myapi --resource-group $RG \
  --type external --target-port 8000 --transport auto
```

`--transport` is one of `auto` (recommended), `http`, `http2`, `tcp`.

## Core concept 2 — Single vs Multiple revision mode

| Aspect | Single mode | Multiple mode |
|---|---|---|
| Active Revisions | Always 1 | N concurrently active |
| New Revision deploy | 100% traffic flips immediately | Weights stay as configured |
| Canary | Not possible | Possible |
| Blue-Green | Not possible | Possible |
| Best for | Simple services, dev | Production APIs |

The default is Single. **Production should be Multiple.**

```bash
az containerapp revision set-mode \
  --name $APP_NAME --resource-group $RG \
  --mode multiple
```

## Before / After

**Before — trying canary in Single mode**

```bash
# Single mode is the default
az containerapp update --name myapi --image myregistry.azurecr.io/myapi:v2
# → New Revision is created and 100% of traffic moves to v2 instantly
# The exact opposite of "send only some users."
```

**After — Multiple mode + weight split**

```bash
# 1. Switch to Multiple mode
az containerapp revision set-mode --name myapi --resource-group $RG --mode multiple

# 2. Deploy the new Revision (traffic still 0%)
az containerapp update --name myapi --image myregistry.azurecr.io/myapi:v2 --revision-suffix v2

# 3. Adjust weights gradually
az containerapp ingress traffic set --name myapi --resource-group $RG \
  --revision-weight myapi--v1=90 myapi--v2=10
```

The difference is whether you can flow traffic at the **ratio you actually intended**.

## Hands-on — 90/10 canary and instant rollback

### Step 1. Switch to Multiple mode

```bash
RG=rg-aca-demo
APP=myapi

az containerapp revision set-mode --name $APP --resource-group $RG --mode multiple
```

### Step 2. Deploy v1 (a single Revision at 100%)

```bash
az containerapp update --name $APP --resource-group $RG \
  --image myregistry.azurecr.io/myapi:v1 --revision-suffix v1
```

### Step 3. Deploy v2 starting at 0% traffic

```bash
az containerapp update --name $APP --resource-group $RG \
  --image myregistry.azurecr.io/myapi:v2 --revision-suffix v2

# Pin v1=100, v2=0 first
az containerapp ingress traffic set --name $APP --resource-group $RG \
  --revision-weight $APP--v1=100 $APP--v2=0
```

### Step 4. Start the 90/10 canary

```bash
az containerapp ingress traffic set --name $APP --resource-group $RG \
  --revision-weight $APP--v1=90 $APP--v2=10
```

Now compare error rate and latency in Log Analytics by `RevisionName`.

### Step 5a. If healthy, proceed 50/50 → 0/100

```bash
az containerapp ingress traffic set --name $APP --resource-group $RG \
  --revision-weight $APP--v1=50 $APP--v2=50
# After more monitoring
az containerapp ingress traffic set --name $APP --resource-group $RG \
  --revision-weight $APP--v1=0 $APP--v2=100
```

### Step 5b. If problems appear, roll back instantly

```bash
az containerapp ingress traffic set --name $APP --resource-group $RG \
  --revision-weight $APP--v1=100 $APP--v2=0
```

v2 traffic is at zero within seconds.

## Common mistakes

### Mistake 1. Confusing `target-port` with the ingress port

`--target-port` is the **container's** listening port. The externally exposed port is always 443 (HTTPS); ACA handles the mapping.

### Mistake 2. Assuming `internal` is safe because of NSGs

`internal` only routes within the same Environment. If the Environment was created without VNet integration, internal endpoints can only be called by other Container Apps in the same ACA region. To call from on-prem or another VNet, you need a VNet-integrated Environment.

### Mistake 3. Starting canary with v2's `min-replicas` at 0

Even at 10% traffic, the first hit on v2 will pay a cold start cost. Set v2's `--min-replicas 1` during canary so latency measurements stay clean.

### Mistake 4. Looking at metrics immediately after weight changes

Ingress weight changes apply instantly, but Log Analytics queries lag by 1-3 minutes. Wait 5-10 minutes before drawing conclusions.

### Mistake 5. Expecting label-based routing (header, cookie)

ACA traffic split is **percentage-based**. Routing like "only this user-agent to v2" is not supported. For that, put Application Gateway or Front Door in front.

## How seasoned teams think about it

Production canary playbook:

- **Start weight 1-10%** — too small loses statistical signal, too large widens blast radius
- **Wait at least 10-15 minutes between steps** — accommodates log delay and traffic variety
- **Pre-agree rollback triggers** — for example 5xx > 1%, p95 latency +20%
- **Equal `min-replicas` on both Revisions** — avoids cold-start measurement bias
- **Use meaningful Revision suffixes** — prefer `v2-fix-bug-1234` over plain `v2`

## Checklist

- [ ] I can describe the difference between external/internal/disabled ingress modes
- [ ] I know how Single vs Multiple mode affects whether canary is possible
- [ ] I have memorized the CLI command to set traffic weights
- [ ] I confirmed that rollback completes within seconds via weight change
- [ ] I know that header/cookie-based routing is not part of ACA traffic split

## Exercises

1. Follow Steps 1-5a to drive v1 → v2 100% via 90/10 → 50/50 → 0/100. At each step, query Log Analytics for request count by `RevisionName` and compare intended vs actual ratio.
2. Inject an intentional 500 error in v2, start a 90/10 canary, then run the rollback command and measure how long until v2 traffic reaches zero.

## Summary

- ACA Ingress owns TLS, external/internal exposure, and Revision routing.
- Picking among `external` / `internal` / `disabled` is the first decision.
- Production should be in Multiple revision mode to enable canary and instant rollback.
- Traffic split is percentage-based — header/cookie routing is not supported.
- Rollback is a weight change, not a new deploy — it completes in seconds.

## Next up

The next post covers KEDA-based scaling. We will configure 0-to-N scaling driven not just by HTTP traffic but also by queue length, CPU, and custom metrics.

## Answering the Opening Questions

- **What ACA's managed Ingress owns (TLS, external/internal exposure, Revision routing) and what it does not?**
  - The article treats Ingress and traffic splitting — revision-based deployment strategies as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **The exact difference between `external`, `internal`, and `disabled` ingress modes?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **How Single mode and Multiple mode change traffic distribution behavior?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Azure Container Apps 101 (1/7): What is Azure Container Apps? — running containers without Kubernetes](./01-what-is-aca.md)
- [Azure Container Apps 101 (2/7): Environment, Container App, Revision — ACA in three words](./02-environment-app-revision.md)
- [Azure Container Apps 101 (3/7): Your first deploy — Python/FastAPI](./03-first-deploy.md)
- **Azure Container Apps 101 (4/7): Ingress and traffic splitting — revision-based deployment strategies (current)**
- Azure Container Apps 101 (5/7): Scaling — KEDA scalers and zero-to-N (upcoming)
- Azure Container Apps 101 (6/7): Dapr integration — what you get from a sidecar (upcoming)
- Azure Container Apps 101 (7/7): Monitoring and ops — Log Analytics and Application Insights (upcoming)

<!-- toc:end -->

---

## References

### Official Docs
- [Ingress in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/ingress-overview)
- [Configure ingress for your app in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/ingress-how-to)
- [Traffic splitting in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/traffic-splitting)
- [Update and deploy changes in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/revisions)

### Related Series
- [Azure App Service 101](../../azure-app-service-101/en/01-what-is-app-service.md)
- [Azure AKS 101](../../azure-aks-101/en/01-what-is-aks.md)
- [Azure Functions 101](../../azure-functions-101/en/01-what-is-azure-functions.md)

Tags: Azure, Container Apps, Serverless, Containers
