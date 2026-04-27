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

```mermaid
flowchart LR
    C1[Browser / Mobile / API Client]
    C2[Internal services]
    subgraph ENV[ACA Environment]
        I[Ingress\nEnvoy]
        subgraph APP1[Container App: web-api]
            R1[Revision A\nFastAPI + Dapr]
            R2[Revision B\nFastAPI + Dapr]
        end
        subgraph APP2[Container App: worker]
            R3[Revision A\nWorker + Dapr]
        end
        K[KEDA scaler]
    end
    ACR[Container Registry]
    LA[Log Analytics]
    AI[Application Insights]
    C1 --> I
    C2 --> I
    I --> R1
    I --> R2
    I --> R3
    K -. scale rules .-> R1
    K -. scale rules .-> R2
    K -. scale rules .-> R3
    ACR --> R1
    ACR --> R2
    ACR --> R3
    R1 --> LA
    R2 --> LA
    R3 --> LA
    R1 --> AI
    R2 --> AI
    R3 --> AI
```

---

## A one-sentence definition

ACA is a managed serverless platform for running containerized applications.
It uses a Microsoft-managed Kubernetes layer plus components such as KEDA, Dapr, and Envoy, but the cluster is not exposed to the user.

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

```mermaid
sequenceDiagram
    autonumber
    participant Client as Client
    participant Ingress as Envoy ingress
    participant Rev as ACA revision
    participant App as FastAPI app
    participant Log as Log Analytics
    Client->>Ingress: HTTPS request
    Ingress->>Rev: Route to active revision
    Rev->>App: Forward request to port 8000
    App-->>Rev: Response
    Rev-->>Ingress: 200 OK
    Ingress-->>Client: HTTPS response
    App->>Log: stdout / stderr logs
```

---

## Workloads that fit well

- FastAPI APIs
- bursty workers
- microservice groups
- services that need canary or blue-green

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
