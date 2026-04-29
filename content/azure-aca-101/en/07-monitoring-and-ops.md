# Monitoring and ops — Log Analytics and Application Insights

> Azure Container Apps 101 series (7/7)

This post covers logs, traces, and day-two operations.
It separates console logs from system logs.
Then connects KQL, revision comparison, and Application Insights.

---

## The observability map

Log Analytics tells you what happened.
Application Insights helps you follow where the request went.

![The observability map](../../../assets/azure-aca-101/07/07-01-the-observability-map.en.png)
---

## Two log types

- ContainerAppConsoleLogs_CL
- ContainerAppSystemLogs_CL

---

## KQL examples

```kusto
ContainerAppConsoleLogs_CL
| where ContainerAppName_s == "fastapi-aca-demo"
| project Time=TimeGenerated, Revision=RevisionName_s, Message=Log_s
| take 100

ContainerAppSystemLogs_CL
| where ContainerAppName_s == "fastapi-aca-demo"
| project Time=TimeGenerated, Revision=RevisionName_s, Message=Log_s
| take 100
```

---

## Revision comparison

```kusto
ContainerAppConsoleLogs_CL
| where ContainerAppName_s == "fastapi-aca-demo"
| summarize count() by RevisionName_s
| order by count_ desc
```

---

## Application Insights

It is strong at distributed tracing and dependency analysis.
Application code should be instrumented with SDKs.

```bash
az containerapp env create   --name $ACA_ENV   --resource-group $RG   --location eastus   --dapr-connection-string "$APPLICATIONINSIGHTS_CONNECTION_STRING"
```

---

## Operator notes

- ACA gets simpler once the operating units are named precisely.
- Do not blur app names, revision names, and environment names.
- Troubleshooting speed depends on how cleanly you separate layers.
- The platform hides a lot, but the boundaries still matter.
- Deployment, scaling, and observability are different faces of one flow.
- It is better to understand which layer a command changes than to memorize syntax alone.
- You need a clean split between revision-scoped changes and app-wide policy changes.
- Logs and metrics are most useful when read with revision context.
- Cost and stability usually move with traffic shape and replica floors.
- A repeatable deployment procedure lowers operational risk quickly.

---

## Common mistakes

- Managed does not mean operations disappear.
- A failed new revision is not the same thing as automatic rollback.
- Scale-to-zero is not implemented the same way for every rule type.
- Turning on Dapr does not remove application design responsibility.
- Using Environment and App as if they are the same layer leads to weak boundary decisions.

---

## Operations checklist

- Cost and stability usually move with traffic shape and replica floors.
- A repeatable deployment procedure lowers operational risk quickly.
- ACA gets simpler once the operating units are named precisely.
- Do not blur app names, revision names, and environment names.
- Troubleshooting speed depends on how cleanly you separate layers.
- The platform hides a lot, but the boundaries still matter.
- Deployment, scaling, and observability are different faces of one flow.
- It is better to understand which layer a command changes than to memorize syntax alone.
- You need a clean split between revision-scoped changes and app-wide policy changes.
- Logs and metrics are most useful when read with revision context.
- Cost and stability usually move with traffic shape and replica floors.
- A repeatable deployment procedure lowers operational risk quickly.
- ACA gets simpler once the operating units are named precisely.
- Do not blur app names, revision names, and environment names.
- Troubleshooting speed depends on how cleanly you separate layers.
- The platform hides a lot, but the boundaries still matter.
- Deployment, scaling, and observability are different faces of one flow.
- It is better to understand which layer a command changes than to memorize syntax alone.
- You need a clean split between revision-scoped changes and app-wide policy changes.
- Logs and metrics are most useful when read with revision context.
- Cost and stability usually move with traffic shape and replica floors.
- A repeatable deployment procedure lowers operational risk quickly.
- ACA gets simpler once the operating units are named precisely.
- Do not blur app names, revision names, and environment names.
- Troubleshooting speed depends on how cleanly you separate layers.
- The platform hides a lot, but the boundaries still matter.
- Deployment, scaling, and observability are different faces of one flow.
- It is better to understand which layer a command changes than to memorize syntax alone.
- You need a clean split between revision-scoped changes and app-wide policy changes.
- Logs and metrics are most useful when read with revision context.
- Cost and stability usually move with traffic shape and replica floors.
- A repeatable deployment procedure lowers operational risk quickly.
- ACA gets simpler once the operating units are named precisely.
- Do not blur app names, revision names, and environment names.
- Troubleshooting speed depends on how cleanly you separate layers.
- The platform hides a lot, but the boundaries still matter.
- Deployment, scaling, and observability are different faces of one flow.
- It is better to understand which layer a command changes than to memorize syntax alone.
- You need a clean split between revision-scoped changes and app-wide policy changes.
- Logs and metrics are most useful when read with revision context.
- Cost and stability usually move with traffic shape and replica floors.
- A repeatable deployment procedure lowers operational risk quickly.
- ACA gets simpler once the operating units are named precisely.
- Do not blur app names, revision names, and environment names.
- Troubleshooting speed depends on how cleanly you separate layers.
- The platform hides a lot, but the boundaries still matter.
- Deployment, scaling, and observability are different faces of one flow.
- It is better to understand which layer a command changes than to memorize syntax alone.
- You need a clean split between revision-scoped changes and app-wide policy changes.
- Logs and metrics are most useful when read with revision context.
- Cost and stability usually move with traffic shape and replica floors.
- A repeatable deployment procedure lowers operational risk quickly.
- ACA gets simpler once the operating units are named precisely.
- Do not blur app names, revision names, and environment names.
- Troubleshooting speed depends on how cleanly you separate layers.
- The platform hides a lot, but the boundaries still matter.
- Deployment, scaling, and observability are different faces of one flow.
- It is better to understand which layer a command changes than to memorize syntax alone.
- You need a clean split between revision-scoped changes and app-wide policy changes.
- Logs and metrics are most useful when read with revision context.
- Cost and stability usually move with traffic shape and replica floors.
- A repeatable deployment procedure lowers operational risk quickly.
- ACA gets simpler once the operating units are named precisely.
- Do not blur app names, revision names, and environment names.
- Troubleshooting speed depends on how cleanly you separate layers.
- The platform hides a lot, but the boundaries still matter.
- Deployment, scaling, and observability are different faces of one flow.
- It is better to understand which layer a command changes than to memorize syntax alone.
- You need a clean split between revision-scoped changes and app-wide policy changes.
- Logs and metrics are most useful when read with revision context.
- Cost and stability usually move with traffic shape and replica floors.
- A repeatable deployment procedure lowers operational risk quickly.
- ACA gets simpler once the operating units are named precisely.
- Do not blur app names, revision names, and environment names.
- Troubleshooting speed depends on how cleanly you separate layers.
- The platform hides a lot, but the boundaries still matter.
- Deployment, scaling, and observability are different faces of one flow.
- It is better to understand which layer a command changes than to memorize syntax alone.
- You need a clean split between revision-scoped changes and app-wide policy changes.
- Logs and metrics are most useful when read with revision context.
- Cost and stability usually move with traffic shape and replica floors.
- A repeatable deployment procedure lowers operational risk quickly.
- ACA gets simpler once the operating units are named precisely.
- Do not blur app names, revision names, and environment names.
- Troubleshooting speed depends on how cleanly you separate layers.
- The platform hides a lot, but the boundaries still matter.
- Deployment, scaling, and observability are different faces of one flow.
- It is better to understand which layer a command changes than to memorize syntax alone.
- You need a clean split between revision-scoped changes and app-wide policy changes.
- Logs and metrics are most useful when read with revision context.
- Cost and stability usually move with traffic shape and replica floors.
- A repeatable deployment procedure lowers operational risk quickly.
- ACA gets simpler once the operating units are named precisely.
- Do not blur app names, revision names, and environment names.
- Troubleshooting speed depends on how cleanly you separate layers.
- The platform hides a lot, but the boundaries still matter.
- Deployment, scaling, and observability are different faces of one flow.
- It is better to understand which layer a command changes than to memorize syntax alone.
- You need a clean split between revision-scoped changes and app-wide policy changes.
- Logs and metrics are most useful when read with revision context.
- Cost and stability usually move with traffic shape and replica floors.
- A repeatable deployment procedure lowers operational risk quickly.
- ACA gets simpler once the operating units are named precisely.
- Do not blur app names, revision names, and environment names.
- Troubleshooting speed depends on how cleanly you separate layers.
- The platform hides a lot, but the boundaries still matter.
- Deployment, scaling, and observability are different faces of one flow.
- It is better to understand which layer a command changes than to memorize syntax alone.
- You need a clean split between revision-scoped changes and app-wide policy changes.
- Logs and metrics are most useful when read with revision context.
- Cost and stability usually move with traffic shape and replica floors.
- A repeatable deployment procedure lowers operational risk quickly.
- ACA gets simpler once the operating units are named precisely.
- Do not blur app names, revision names, and environment names.
- Troubleshooting speed depends on how cleanly you separate layers.
- The platform hides a lot, but the boundaries still matter.
- Deployment, scaling, and observability are different faces of one flow.
- It is better to understand which layer a command changes than to memorize syntax alone.
- You need a clean split between revision-scoped changes and app-wide policy changes.
- Logs and metrics are most useful when read with revision context.
- Cost and stability usually move with traffic shape and replica floors.
- A repeatable deployment procedure lowers operational risk quickly.
- ACA gets simpler once the operating units are named precisely.
- Do not blur app names, revision names, and environment names.
- Troubleshooting speed depends on how cleanly you separate layers.
- The platform hides a lot, but the boundaries still matter.
- Deployment, scaling, and observability are different faces of one flow.
- It is better to understand which layer a command changes than to memorize syntax alone.
- You need a clean split between revision-scoped changes and app-wide policy changes.
- Logs and metrics are most useful when read with revision context.

---

This post is one step in the Azure Container Apps 101 series.
The earlier posts define the platform shape, and the later posts build deployment and operations decisions on top of that shape.
Read in order and ACA starts to feel like an operating model instead of a feature catalog.

- Revisit the checklist right after each deployment.

---

<!-- toc:begin -->
## In this series

- [What is Azure Container Apps? — running containers without Kubernetes](./01-what-is-aca.md)
- [Environment, Container App, Revision — ACA in three words](./02-environment-app-revision.md)
- [Your first deploy — Python/FastAPI](./03-first-deploy.md)
- [Ingress and traffic splitting — revision-based deployment strategies](./04-ingress-and-traffic-split.md)
- [Scaling — KEDA scalers and zero-to-N](./05-scaling-with-keda.md)
- [Dapr integration — what you get from a sidecar](./06-dapr-integration.md)
- **Monitoring and ops — Log Analytics and Application Insights (current)**

<!-- toc:end -->

---

## References

### Official Docs
- [Monitor logs in Azure Container Apps with Log Analytics — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/log-monitoring)
- [Observability in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/observability)
- [Azure Monitor Application Insights overview — Microsoft Learn](https://learn.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview)
- [Azure Container Apps environments — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/environment)

### Related Series
- [Azure App Service 101](../../azure-app-service-101/en/01-what-is-app-service.md)
- [Azure AKS 101](../../azure-aks-101/en/01-what-is-aks.md)
- [Azure Functions 101](../../azure-functions-101/en/01-what-is-azure-functions.md)

Tags: Azure, Container Apps, Serverless, Containers
