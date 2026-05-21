---
title: "Azure Kubernetes Service 101 (3/7): Your first cluster, your first deploy — Python/FastAPI"
series: azure-aks-101
episode: 3
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- Azure
- AKS
- Kubernetes
- Cloud
last_reviewed: '2026-04-29'
seo_description: Build your first Azure Kubernetes Service (AKS) cluster and deploy a Python/FastAPI app using Azure CLI and kubectl.
---

# Azure Kubernetes Service 101 (3/7): Your first cluster, your first deploy — Python/FastAPI

> Azure Kubernetes Service 101 series (3/7)

Kubernetes stays abstract for too long if you only study the nouns. The model gets much easier once you build a small cluster, push a tiny app into it, and watch the pieces line up. After that, networking and autoscaling stop feeling theoretical.

This post creates a small AKS cluster, adds a user node pool, and deploys a minimal FastAPI application with a Deployment and a Service. The example stays intentionally small, but the shape matches the way real AKS environments are organized.

This is the third post in the Azure Kubernetes Service 101 series. Here, we take the cluster model from the earlier posts and turn it into a working AKS deployment with a small FastAPI app.

## Questions to Keep in Mind

- What parameters absolutely must be decided when creating a minimal AKS cluster?
- Should you reach for `az aks create` or Bicep/Terraform for your first cluster?
- What permission model wires ACR (Azure Container Registry) to AKS?

## Big Picture

![azure kubernetes service 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-101/03/03-01-today-s-flow.en.png)

*azure kubernetes service 101 chapter 3 flow overview*

This picture places Your first cluster, your first deploy — Python/FastAPI inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## Today's flow

The split matters. `az` creates and configures Azure resources. `kubectl` talks to the Kubernetes API once the cluster exists.

---

## 0. What you need

- Azure CLI
- `kubectl`
- an Azure subscription
- a container registry for the image

The focus here is the AKS flow, not registry setup. Azure Container Registry is the natural Azure-native choice, but Docker Hub works for a simple lab too.

---

## 1. Create a resource group

Start with the Azure resource group.

```bash
export RESOURCE_GROUP="rg-aks-101"
export LOCATION="koreacentral"
export CLUSTER_NAME="aks-101-cluster"
export USER_POOL="userpool1"

az group create --name $RESOURCE_GROUP --location $LOCATION
```

This step is not Kubernetes-specific, but it reinforces a useful point: AKS is still an Azure resource managed through Azure Resource Manager.

---

## 2. Create a small AKS cluster

The smallest clean starting command looks like this.

```bash
az aks create \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --node-count 1 \
  --generate-ssh-keys
```

Four things matter here.

- `az aks create` creates the AKS cluster.
- `--node-count 1` is just a lab choice to keep cost down.
- The current Learn quickstart path uses a system-assigned managed identity by default.
- `--generate-ssh-keys` creates keys if you do not already have them.

In production, you would design VM size, networking mode, monitoring, and upgrade strategy up front. For a first deployment exercise, the point is to get a real cluster and put Kubernetes objects on it.

---

## 3. Add a user node pool

AKS guidance is clear: application workloads should run on a user node pool, not the default system pool. Even in a small lab, it is worth following that pattern once.

```bash
az aks nodepool add \
  --resource-group $RESOURCE_GROUP \
  --cluster-name $CLUSTER_NAME \
  --name $USER_POOL \
  --node-count 1 \
  --mode User
```

Now the cluster has a default system pool and an explicit user pool.

You can confirm that with:

```bash
az aks nodepool list \
  --resource-group $RESOURCE_GROUP \
  --cluster-name $CLUSTER_NAME \
  --query "[].{Name:name, Mode:mode, Count:count}"
```

Seeing `System` and `User` in the output is the architecture from part 2 turned into a real cluster.

---

## 4. Give kubectl access to the cluster

Creating the Azure resource is not the same thing as configuring your local Kubernetes client.

```bash
az aks get-credentials --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME
```

Then verify the connection.

```bash
kubectl get nodes
```

If you see two nodes, that usually means one node in the system pool and one in the user pool.

From this point on, most of the workflow moves to `kubectl`.

---

## 5. Build a tiny FastAPI app

Keep the application code minimal.

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "hello from aks"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}
```

Containerize it with a small `Dockerfile`.

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

And keep `requirements.txt` small.

```text
fastapi==0.115.0
uvicorn[standard]==0.30.6
```

Build the image and push it to your registry of choice. The Deployment will reference that image.

---

## 6. Write the Deployment and Service

For this post, the smallest useful pair is enough.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-hello
spec:
  replicas: 2
  selector:
    matchLabels:
      app: fastapi-hello
  template:
    metadata:
      labels:
        app: fastapi-hello
    spec:
      nodeSelector:
        kubernetes.azure.com/mode: user
      containers:
        - name: app
          image: <your-registry>/fastapi-hello:latest
          ports:
            - containerPort: 8000
          startupProbe:
            httpGet:
              path: /healthz
              port: 8000
            periodSeconds: 5
            failureThreshold: 12
          readinessProbe:
            httpGet:
              path: /healthz
              port: 8000
            initialDelaySeconds: 3
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8000
            initialDelaySeconds: 15
            periodSeconds: 10
            failureThreshold: 3
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 300m
              memory: 256Mi
---
apiVersion: v1
kind: Service
metadata:
  name: fastapi-hello
spec:
  selector:
    app: fastapi-hello
  ports:
    - port: 80
      targetPort: 8000
  type: LoadBalancer
```

For a first deploy, four lines matter most.

- `replicas: 2` means “keep two copies of this pod shape.”
- `nodeSelector` expresses intent to run on the user pool.
- `startupProbe` gives the container time to boot before liveness checks can kill it.
- `type: LoadBalancer` asks for an Azure load balancer-backed external entry point.

Using the same probe for every lifecycle stage is fine for a toy demo, but it becomes noisy fast in a real cluster. A short readiness probe tells Kubernetes when the pod can receive traffic, while a slower liveness probe avoids restart loops during cold starts, dependency warm-up, or image pulls.

---

## 7. Apply the manifest

Save the manifest as `fastapi-hello.yaml` and apply it.

```bash
kubectl apply -f fastapi-hello.yaml
```

Then inspect what happened.

```bash
kubectl get deployments
kubectl get pods -o wide
kubectl get services
```

The `-o wide` output is especially useful because it shows where the pods actually landed. If they land on the user pool nodes, the placement intent is working.

---

## 8. The request path

![External request path to Service and pods](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-101/03/03-02-8-the-request-path.en.png)

*External request path to Service and pods*
This is the pre-Ingress version of exposure. The Service is carrying both the stable service identity and the external publication path. In the next networking post, an Ingress layer will sit in front of ClusterIP services instead.

---

## 9. Test the service

Wait for the external IP to show up.

```bash
kubectl get service fastapi-hello
```

Once `EXTERNAL-IP` is assigned, test it.

```bash
curl http://<external-ip>/
```

Expected response:

```json
{"message":"hello from aks"}
```

That confirms three things at once.

- the container started correctly
- the Deployment is maintaining the replica set
- the Service is routing traffic to healthy pods

---

## 10. Three common early failures

### Image pull failure

Usually an image name or registry-auth problem.

```bash
kubectl describe pod <pod-name>
```

### External IP takes time

The Azure load balancer resource may still be provisioning.

```bash
kubectl describe service fastapi-hello
```

### Pod runs but never becomes Ready

Check the `/healthz` path and port first. Readiness is about whether the pod can safely receive traffic, not just whether the process exists.

---

## 11. What should stick from this post

The point is not YAML memorization. The point is the flow.

1. Create Azure resources with `az aks create`.
2. Connect your local client with `az aks get-credentials`.
3. Declare desired state with `kubectl apply -f`.
4. Let Deployment and Service turn that declaration into running pods and a reachable endpoint.

Once that loop is familiar, later features like Ingress, HPA, and KEDA are extensions of the same model.

---

## Wrap-up

The example is small, but the main AKS layers are already in play.

- Azure CLI for cluster and node-pool lifecycle
- `kubectl` for Kubernetes resources
- user node pool placement
- Service-based exposure

The three workload primitives you just used—Pod, Deployment, and Service—are also the place where most first-cluster misunderstandings show up.

---

This is part 3 of the Azure Kubernetes Service 101 series. The first two posts set the platform boundary and the cluster shape; this one turned that model into a real deployment with a small FastAPI app. The next step is to unpack the exact role of Pod, Deployment, and Service in the manifest you just applied.

---

## Operational checklist

- [ ] Pinned region, node SKU, and Kubernetes version up front
- [ ] Connected ACR to AKS via managed identity
- [ ] Verified cluster access with `kubectl get nodes`
- [ ] Set readiness and liveness probes on the first Deployment
- [ ] Picked the right Service exposure (ClusterIP/LoadBalancer) for intent

## Answering the Opening Questions

- **What parameters absolutely must be decided when creating a minimal AKS cluster?**
  - The article treats Your first cluster, your first deploy — Python/FastAPI as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Should you reach for `az aks create` or Bicep/Terraform for your first cluster?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What permission model wires ACR (Azure Container Registry) to AKS?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Azure Kubernetes Service 101 (1/7): What is Azure Kubernetes Service? — what managed Kubernetes actually gives you](./01-what-is-aks.md)
- [Azure Kubernetes Service 101 (2/7): Cluster architecture — control plane and node pools](./02-cluster-architecture.md)
- **Azure Kubernetes Service 101 (3/7): Your first cluster, your first deploy — Python/FastAPI (current)**
- Azure Kubernetes Service 101 (4/7): Pod, Deployment, Service — the three ways you express a workload (upcoming)
- Azure Kubernetes Service 101 (5/7): Networking and Ingress — the path in and out of the cluster (upcoming)
- Azure Kubernetes Service 101 (6/7): Scaling — HPA, Cluster Autoscaler, KEDA (upcoming)
- Azure Kubernetes Service 101 (7/7): Monitoring and ops — Container Insights, logs, alerts (upcoming)

<!-- toc:end -->

---

## References

### Official Docs
- [Deploy an Azure Kubernetes Service (AKS) Cluster Using Azure CLI](https://learn.microsoft.com/en-us/azure/aks/learn/quick-kubernetes-deploy-cli)
- [Create node pools in Azure Kubernetes Service (AKS)](https://learn.microsoft.com/en-us/azure/aks/create-node-pools)
- [Use system node pools in Azure Kubernetes Service (AKS)](https://learn.microsoft.com/en-us/azure/aks/use-system-pools)
- [az aks create](https://learn.microsoft.com/en-us/cli/azure/aks#az-aks-create)
- [az aks get-credentials](https://learn.microsoft.com/en-us/cli/azure/aks#az-aks-get-credentials)

### Related Series
- [Azure App Service 101](../../azure-app-service-101/en/04-first-deploy.md) — useful when comparing the same FastAPI app on a higher-level PaaS
- [Azure Functions 101](../../azure-functions-101/en/) — useful when comparing container deployment with function deployment

Tags: Azure, AKS, Kubernetes, Cloud
