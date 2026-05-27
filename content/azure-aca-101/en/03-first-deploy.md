---
title: "Azure Container Apps 101 (3/7): Your first deploy — Python/FastAPI"
series: azure-aca-101
episode: 3
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
- FastAPI
- ACR
- Dockerfile
- az containerapp
last_reviewed: '2026-05-03'
seo_description: A first deploy on ACA is like calling a taxi — you need an origin
  before the taxi can leave.
---

# Azure Container Apps 101 (3/7): Your first deploy — Python/FastAPI

A first deploy is where ACA stops being a diagram and starts becoming an operating model. You only really see the service boundaries after you push an image, wire the dependencies, and watch a Revision come alive.

This is the 3rd post in the Azure Container Apps 101 series. Here, we'll walk a Python/FastAPI app through that full path.

![azure container apps 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-101/03/03-01-the-end-to-end-path.en.png)
*azure container apps 101 chapter 3 flow overview*

## Questions to Keep in Mind

- The full path from local FastAPI code to a live ACA Revision?
- That ACA does not build images for you — and what that means for division of responsibility?
- The four-step dependency chain: ACR → ACA Environment → Container App → Revision?

## Why this matters

A single "hello world" deploy is the line between understanding ACA in your head and understanding it in your hands. After one real deploy, you have your own answers to questions like:

- Where does ACA's responsibility start and end? (It does not own image build.)
- Why is a registry like ACR mandatory? (ACA only consumes image references.)
- When does cost actually start? (At Environment creation and Revision running.)
- What signal proves the deploy succeeded? (FQDN response and Revision health.)

This post walks the path end to end.

## Mental Model

> A first deploy on ACA is like calling a taxi — you need an origin before the taxi can leave.

The taxi (ACA) takes the passenger (your image) anywhere, but if there is no passenger waiting it cannot leave. The passenger has to be standing somewhere (a registry), and you have to give the address (image reference) to the taxi.

So a first deploy flows in this order: image build → registry push → ACA creates a Revision pointing at that image. Skip any step and the next one will not happen.

## See the path first

Seeing the route makes the deploy feel much simpler.

Critical dependencies:

1. **Resource group** — container for all Azure resources
2. **ACR** — where images live (or another OCI registry)
3. **ACA Environment** — the boundary where Revisions actually run
4. **Container App + Revision** — image reference + config = running instance

## Core concept — what ACA does NOT do

| Responsibility | Owner |
|---|---|
| Source code → image build | **Developer / CI** (not ACA) |
| Image storage | **ACR or external registry** (not ACA) |
| Image pull credentials | ACA (via managed identity) |
| Container execution and restart | ACA |
| Ingress, TLS termination | ACA |
| 0-to-N scaling | ACA |
| Log shipping | ACA (to Log Analytics) |

Memorize this table once and 90% of "why is it not working?" disappears. ACA does not build images for you.

## Before / After

**Before — assuming ACA will build for you**

```bash
# Pointing at code does not work in general - ACA does not do source builds
az containerapp create \
  --name myapi \
  --source ./my-fastapi-folder   # ← only works in some scenarios via containerapp up + Buildpacks
```

`az containerapp up` does call buildpacks under the hood, but in production CI/CD the explicit build → push → deploy split is standard.

**After — explicit build, push, then deploy**

```bash
az acr build --registry $ACR_NAME --image fastapi-hello:v1 .
az containerapp create --name myapi --image $ACR_NAME.azurecr.io/fastapi-hello:v1 ...
```

The latter makes the image tag the identity of "what was deployed," so tracing, rollback, and audit are all clean.

## Hands-on

### Step 0. Variables and CLI prep

```bash
az extension add --name containerapp --upgrade
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.OperationalInsights

RG="rg-aca-101-demo"
LOCATION="eastus"
ACA_ENV="aca-env-101-demo"
ACR_NAME="aca101demo$RANDOM"
APP_NAME="fastapi-aca-demo"
IMAGE="$ACR_NAME.azurecr.io/fastapi-hello:v1"
```

### Step 1. FastAPI app and Dockerfile

```python
# app/main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "hello from azure container apps"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}
```

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`requirements.txt` needs at minimum `fastapi` and `uvicorn[standard]`.

### Step 2. Resource group and ACR

```bash
az group create --name $RG --location $LOCATION
az acr create --name $ACR_NAME --resource-group $RG --location $LOCATION --sku Basic
```

### Step 3. Image build & push (single command)

```bash
az acr build --registry $ACR_NAME --image fastapi-hello:v1 .
```

`az acr build` ships your source to ACR, builds in the cloud, and pushes — no local Docker daemon required.

### Step 4. Create the ACA Environment

```bash
az containerapp env create \
  --name $ACA_ENV \
  --resource-group $RG \
  --location $LOCATION
```

The Environment is a boundary that shares network, log destination, and optional integrations (e.g., Dapr). This command takes 2-3 minutes.

### Step 5. Create the first Container App + Revision

```bash
az containerapp create \
  --name $APP_NAME \
  --resource-group $RG \
  --environment $ACA_ENV \
  --image $IMAGE \
  --ingress external \
  --target-port 8000 \
  --cpu 0.5 \
  --memory 1.0Gi \
  --min-replicas 0 \
  --max-replicas 3
```

This single command (1) creates the Container App, (2) creates the first Revision, (3) wires up ingress + TLS automatically, and (4) enables scale-to-zero.

### Step 6. Verify the deploy from CLI

```bash
# Get the FQDN
FQDN=$(az containerapp show --name $APP_NAME --resource-group $RG \
  --query properties.configuration.ingress.fqdn --output tsv)
echo "https://$FQDN"

# Hit it
curl https://$FQDN/
curl https://$FQDN/healthz

# Check Revision status
az containerapp revision list --name $APP_NAME --resource-group $RG \
  --query "[].{name:name, active:properties.active, healthState:properties.healthState}" \
  --output table
```

`healthState: Healthy` means success.

## Common mistakes

### Mistake 1. `target-port` does not match what the container actually listens on

ACA's `--target-port` must be the port the container is actively listening on. If Dockerfile runs on `8000` but you pass `--target-port 80`, ingress will never get a response.

### Mistake 2. Running `az containerapp create` before the image is in ACR

Order matters. Step 3 (image push) must finish before Step 5 (app create) can pull the image. Otherwise the Revision fails to start, similar to `ImagePullBackOff`.

### Mistake 3. Not setting up ACR pull permission

Within the same subscription, `az containerapp create` usually creates a system-assigned managed identity and assigns `AcrPull` automatically. Otherwise (cross-subscription, external registry), you must specify `--registry-server`, `--registry-username`, `--registry-password`, or a managed identity manually.

### Mistake 4. `min-replicas 0` plus an infrequent health probe

Scale-to-zero causes a cold start on the first request. If `/healthz` is heavy or startup is slow, ingress can time out. For first-deploy verification, briefly setting `--min-replicas 1` is fine.

### Mistake 5. Stopping at "Provisioning succeeded" in the portal

Provisioning success is a control-plane response — it does not mean the application is healthy. Always check Revision `healthState` and a real endpoint response.

## How seasoned teams think about it

A production first-deploy checklist:

- **Is the image tag immutable?** No `:latest`. Use `:v1`, `:sha-abc123`, or similar explicit tags.
- **Is the build environment reproducible?** `az acr build` spins up an ephemeral build agent in ACR — good for reproducibility.
- **Are env vars and secrets separated?** Secrets via `--secrets`, plain config via `--env-vars`.
- **Is first-deploy cost visible?** Log Analytics cost starts the moment you create an Environment.
- **Is the rollback path obvious?** Re-running Step 5 with a different image tag creates a new Revision; in Multiple mode you can split weights.

## Checklist

- [ ] I can explain the responsibility split for image build → push → deploy
- [ ] I know how `--target-port` must align with Dockerfile EXPOSE/CMD
- [ ] I retrieved the FQDN from CLI and got a real response
- [ ] I know how to check Revision `healthState` from CLI
- [ ] I can explain why image tags must be managed immutably

## Exercises

1. Follow Steps 1-6 verbatim and deploy. Then change the response message in `app/main.py`, build/push as image tag `:v2`, update the app, and use `az containerapp revision list` to confirm a new Revision was created.
2. With `--min-replicas 0`, leave the app idle for five minutes and measure the latency of the first request. Then update to `--min-replicas 1` and repeat the measurement to see the cold-start difference.

## Summary

- ACA does not own image build — that belongs to the developer/CI.
- The first-deploy flow is RG → ACR → image build/push → Environment → Container App + Revision.
- A single `az containerapp create` enables (1) the App, (2) the first Revision, (3) ingress + TLS, and (4) scaling.
- Verify from **Revision healthState + FQDN response**, not the portal's "Provisioning succeeded."
- Image tags must be immutable (`:v1`, `:sha-abc123`) to enable tracking and rollback.

## Next up

The next post goes deep on ingress and traffic splitting. We create two Revisions, run a 90/10 canary, and practice the instant flip back to 100/0 when something goes wrong.

## Answering the Opening Questions

- **The full path from local FastAPI code to a live ACA Revision?**
  - The article treats Your first deploy — Python/FastAPI as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **That ACA does not build images for you — and what that means for division of responsibility?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **The four-step dependency chain: ACR → ACA Environment → Container App → Revision?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Azure Container Apps 101 (1/7): What is Azure Container Apps? — running containers without Kubernetes](./01-what-is-aca.md)
- [Azure Container Apps 101 (2/7): Environment, Container App, Revision — ACA in three words](./02-environment-app-revision.md)
- **Azure Container Apps 101 (3/7): Your first deploy — Python/FastAPI (current)**
- Azure Container Apps 101 (4/7): Ingress and traffic splitting — revision-based deployment strategies (upcoming)
- Azure Container Apps 101 (5/7): Scaling — KEDA scalers and zero-to-N (upcoming)
- Azure Container Apps 101 (6/7): Dapr integration — what you get from a sidecar (upcoming)
- Azure Container Apps 101 (7/7): Monitoring and ops — Log Analytics and Application Insights (upcoming)

<!-- toc:end -->

---

## References

### Official Docs
- [Quickstart: Deploy your first container app with containerapp up — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/get-started)
- [az containerapp create — Microsoft Learn](https://learn.microsoft.com/en-us/cli/azure/containerapp#az-containerapp-create)
- [Azure Container Apps environments — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/environment)
- [Run containers from any registry — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/containers)

### Related Series
- [Azure App Service 101](../../azure-app-service-101/en/01-what-is-app-service.md)
- [Azure AKS 101](../../azure-aks-101/en/01-what-is-aks.md)
- [Azure Functions 101](../../azure-functions-101/en/01-what-is-azure-functions.md)

Tags: Azure, Container Apps, Serverless, Containers
