# Dapr integration — what you get from a sidecar

> Azure Container Apps 101 series (6/7)

This post shows where the Dapr sidecar sits and what it simplifies.
Service invocation.
Pub/Sub.
State.
And secrets are the key themes.

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

## Component example

```yaml
componentType: pubsub.azure.servicebus.queue
version: v1
metadata:
  - name: namespaceName
    value: mybus.servicebus.windows.net
scopes:
  - publisher-app
  - subscriber-app
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
