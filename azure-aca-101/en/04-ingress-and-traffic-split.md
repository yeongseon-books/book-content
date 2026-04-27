# Ingress and traffic splitting — revision-based deployment strategies

> Azure Container Apps 101 series (4/7)

This post connects ingress with revision-based rollout control.
It focuses on TLS termination.
Single versus multiple mode.
And weighted traffic movement.

---

## The request path

Envoy acts as the front door and routes to active revisions.

![The request path](../../assets/azure-aca-101/04/04-01-the-request-path.en.png)
---

## What ingress owns

- TLS termination
- external or internal exposure
- traffic distribution across revisions

---

## Single and multiple mode

Single deactivates the previous revision after the new one is ready.
Multiple keeps more than one revision active.

---

## Traffic commands

```bash
az containerapp revision set-mode   --name $APP_NAME   --resource-group $RG   --mode multiple

az containerapp ingress traffic set   --name $APP_NAME   --resource-group $RG   --revision-weight myapp--rev-a=80 myapp--rev-b=20
```

---

## Canary and blue-green

- start with a small percentage
- compare logs and latency
- move traffic back if needed

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
- **Ingress and traffic splitting — revision-based deployment strategies (current)**
- Scaling — KEDA scalers and zero-to-N (upcoming)
- Dapr integration — what you get from a sidecar (upcoming)
- Monitoring and ops — Log Analytics and Application Insights (upcoming)

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
