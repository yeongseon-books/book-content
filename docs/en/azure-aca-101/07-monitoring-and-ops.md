---
title: Monitoring and ops — Log Analytics and Application Insights
series: azure-aca-101
episode: 7
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
- Log Analytics
- Application Insights
- Observability
- Monitoring
last_reviewed: '2026-04-29'
seo_description: 'ACA observability splits into three independent layers:'
---

# Monitoring and ops — Log Analytics and Application Insights

> Azure Container Apps 101 series (7/7)

## What you'll learn

- The layered structure of ACA observability.
- How `ContainerAppConsoleLogs_CL` differs from `ContainerAppSystemLogs_CL`.
- How to write KQL queries that group logs by Revision in Log Analytics.
- How to wire Application Insights into a FastAPI app via OpenTelemetry.

## Questions this chapter answers

- What three layers does ACA observability split into, and what does each layer own?
- What events does `ContainerAppConsoleLogs_CL` capture compared to `ContainerAppSystemLogs_CL`?
- How do you write a KQL query that groups logs by Revision in Log Analytics?
- What is the shortest path to wire Application Insights into a FastAPI app via OpenTelemetry?
- Where is the boundary between observability ACA gives you for free and what you must instrument yourself?

## Why this matters

Imagine your production ACA app starts emitting 5xx errors.
First question: "Which revision?" — `RevisionName_s` in Log Analytics answers it.
Second: "Which dependency stalled?" — Application Insights distributed traces answer it.
Third: "How many replicas spun up?" — Azure Monitor metrics answer it.

**ACA gives you the first answer for free.** The second and third require app instrumentation or explicit Diagnostic Settings.
Miss this boundary and you spend an hour during an incident asking "why don't I see traces?"

## Mental Model

ACA observability splits into three independent layers:

1. **Platform layer (Log Analytics)** — emitted automatically by ACA. Container stdout/stderr and system events.
2. **Application layer (Application Insights)** — your code emits these via SDK or OpenTelemetry. Distributed traces, custom metrics, dependency map.
3. **Sidecar layer (Dapr telemetry)** — only meaningful if you use Dapr. `--dapr-connection-string` belongs to this layer, not to general app tracing.

The three layers can land in the same Application Insights instance or stay separate.
The discipline is to always know "which layer does this signal come from?"

![Where logs and traces converge](../../assets/azure-aca-101/07/07-01-the-observability-map.en.png)

*Where logs and traces converge*

## Core concepts

### 1. Two platform log tables

| Table | Contents | Primary use |
| --- | --- | --- |
| `ContainerAppConsoleLogs_CL` | Container stdout/stderr | App behavior, business log tracing |
| `ContainerAppSystemLogs_CL` | ACA platform events (scaling, revision change, probe failure, etc.) | Platform decision tracing |

The `_CL` suffix means "Custom Log." Both tables live in your Log Analytics workspace and are queried with KQL.

### 2. Revision is the strongest grouping key

ACA fills `RevisionName_s` on every log row.
The first query during an incident is almost always "which revision saw the error spike?"

### 3. Two paths to Application Insights

- **App-level instrumentation** — pass the connection string via `APPLICATIONINSIGHTS_CONNECTION_STRING` and export with the OpenTelemetry SDK.
- **Dapr telemetry** — set `az containerapp env update --dapr-instrumentation-key` so the sidecar emits its own telemetry. Independent from app code traces.

## Before-After

### Before (no observability)

```bash
az containerapp create \
  --name fastapi-aca-demo --resource-group $RG --environment $ACA_ENV \
  --image $IMAGE --ingress external --target-port 8000
```

During an incident:
- "Where do the 5xxs come from?" → no SSH, no debugging.
- Container restart wipes stdout history.

### After (Log Analytics + App Insights wired up)

```bash
# 1. Connect a Log Analytics workspace when creating the Environment
az containerapp env create \
  --name $ACA_ENV --resource-group $RG --location koreacentral \
  --logs-workspace-id $LOG_WORKSPACE_ID \
  --logs-workspace-key $LOG_WORKSPACE_KEY

# 2. Inject the App Insights connection string
az containerapp create \
  --name fastapi-aca-demo --resource-group $RG --environment $ACA_ENV \
  --image $IMAGE --ingress external --target-port 8000 \
  --env-vars "APPLICATIONINSIGHTS_CONNECTION_STRING=$AI_CONN"
```

During an incident:
- One KQL line gives you per-revision error counts.
- App Insights captures traces, dependencies, and exceptions automatically.

## Step-by-step

### Step 1: Create a Log Analytics workspace

```bash
RG=rg-aca-demo
LOG_WS=aca-logs

az monitor log-analytics workspace create \
  --resource-group $RG --workspace-name $LOG_WS

LOG_WORKSPACE_ID=$(az monitor log-analytics workspace show \
  --resource-group $RG --workspace-name $LOG_WS \
  --query customerId -o tsv)

LOG_WORKSPACE_KEY=$(az monitor log-analytics workspace get-shared-keys \
  --resource-group $RG --workspace-name $LOG_WS \
  --query primarySharedKey -o tsv)
```

### Step 2: Wire it into the ACA Environment

```bash
az containerapp env create \
  --name aca-env-demo --resource-group $RG --location koreacentral \
  --logs-workspace-id $LOG_WORKSPACE_ID \
  --logs-workspace-key $LOG_WORKSPACE_KEY
```

### Step 3: Query with KQL

In Azure Portal → Log Analytics workspace → Logs:

```kusto
// Most recent 100 console logs
ContainerAppConsoleLogs_CL
| where ContainerAppName_s == "fastapi-aca-demo"
| project Time=TimeGenerated, Revision=RevisionName_s, Message=Log_s
| top 100 by Time desc

// Errors per revision
ContainerAppConsoleLogs_CL
| where ContainerAppName_s == "fastapi-aca-demo"
| where Log_s contains "ERROR"
| summarize ErrorCount=count() by RevisionName_s
| order by ErrorCount desc

// Scaling events
ContainerAppSystemLogs_CL
| where ContainerAppName_s == "fastapi-aca-demo"
| where Log_s contains "Scal"
| project Time=TimeGenerated, Message=Log_s
| top 50 by Time desc
```

### Step 4: Connect Application Insights (FastAPI)

```bash
AI_NAME=aca-appinsights
az monitor app-insights component create \
  --app $AI_NAME --location koreacentral --resource-group $RG \
  --workspace $LOG_WORKSPACE_ID

AI_CONN=$(az monitor app-insights component show \
  --app $AI_NAME --resource-group $RG --query connectionString -o tsv)

az containerapp update \
  --name fastapi-aca-demo --resource-group $RG \
  --set-env-vars "APPLICATIONINSIGHTS_CONNECTION_STRING=$AI_CONN"
```

FastAPI app code:

```python
from azure.monitor.opentelemetry import configure_azure_monitor
from fastapi import FastAPI

configure_azure_monitor()  # Auto-detects APPLICATIONINSIGHTS_CONNECTION_STRING
app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}
```

Add `azure-monitor-opentelemetry` to `requirements.txt` and traces, requests, and dependencies are collected automatically.

## Common pitfalls

- **Forgetting Log Analytics on the Environment** — logs only show up in the ACA portal blade, not in KQL.
- **Storing the App Insights connection string as a plain env-var** — protect it with `--secrets` in production.
- **Assuming App Insights auto-collects traces** — injecting the connection string is not enough. The app must export with an OpenTelemetry SDK.
- **Confusing Dapr telemetry with app telemetry** — `--dapr-instrumentation-key` is sidecar-only.
- **Leaving log retention at the default** — Log Analytics defaults to 30 days. Compliance may require more.

## In production

Production checklist:

- **Enable Diagnostic Settings** — connect both Log Analytics and a Storage Account (long-term retention).
- **Configure alert rules** — KQL-based alerts like "5xx ratio > 5% on a specific revision."
- **Build a Workbook** — per-revision latency, error rate, and replica count on one screen.
- **Manage cost** — App Insights bills on ingestion volume. Tune sampling rate.
- **Standardize on OpenTelemetry** — OTel SDK + Azure Monitor exporter beats vendor-specific SDK for portability.

## Checklist

- [ ] Is the ACA Environment connected to a Log Analytics workspace?
- [ ] Are both `ContainerAppConsoleLogs_CL` and `ContainerAppSystemLogs_CL` receiving data?
- [ ] Is the App Insights connection string managed as a secret?
- [ ] Does the FastAPI app export traces via OpenTelemetry?
- [ ] Is there a KQL alert grouping errors by revision?
- [ ] Does log retention match compliance requirements?

## Exercises

1. Right after deploying a new revision, 5xx ratios spike. Write a KQL query comparing error rates between the previous and current revision.
2. What is the difference between exposing the App Insights connection string as a plain env-var vs injecting it as a secret?
3. Should a plain FastAPI app (no Dapr) ever set `--dapr-instrumentation-key`? Why or why not?

## Wrap-up and next post

Key takeaways:

- ACA observability splits into platform / application / sidecar layers.
- Log Analytics captures console and system logs into `_CL` tables automatically.
- Application Insights only gains meaning when the app exports via OpenTelemetry.
- Revision is the strongest grouping key for incident triage.

This concludes the **Azure Container Apps 101 series — all 7 episodes**.
We covered the concept (Ep 1), structure (Ep 2), first deploy (Ep 3), traffic splitting (Ep 4), scaling (Ep 5), Dapr integration (Ep 6), and now observability.

Natural next steps: compare the same approach across **Azure App Service 101**, **Azure AKS 101**, and **Azure Functions 101** to understand the trade-offs of serverless container platforms.
---

## References

### Official Docs
- [Monitor logs in Azure Container Apps with Log Analytics — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/log-monitoring)
- [Observability in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/observability)
- [Azure Monitor Application Insights overview — Microsoft Learn](https://learn.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview)
- [Azure Container Apps environments — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/environment)
- [Azure Monitor OpenTelemetry distro for Python](https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-enable?tabs=python)

### Related Series
- [Azure App Service 101](../azure-app-service-101/01-what-is-app-service.md)
- [Azure AKS 101](../azure-aks-101/01-what-is-aks.md)
- [Azure Functions 101](../azure-functions-101/01-what-is-azure-functions.md)
