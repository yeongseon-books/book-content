# Hosting Models: Which Plan Should You Choose?

> Azure App Service 101 Series (3/7)

When starting with App Service, the first question you face: **"Which plan should I choose?"**

Free? Basic? Standard? Premium? And Windows vs Linux? Code vs Container?

In this post, we'll cover the **key criteria for choosing your Hosting Model**.

---

## Decision Flowchart

The flow for deciding your App Service hosting strategy:

```
1. Choose OS (Linux / Windows)
   ↓
2. Choose Deployment Model (Code / Container)
   ↓
3. Choose Plan Tier (Dev → Production)
```

![IMAGE: Hosting Model decision flowchart]
`📸 Screenshot: Decision flowchart (draw.io)`

---

## What is an App Service Plan?

An App Service Plan is the **compute resource pool** where your app runs.

### What the Plan Defines

| Item | Description |
|------|-------------|
| CPU/Memory | Resources available per instance |
| Max Instance Count | Scale out limit |
| Feature Set | Autoscale, Slots, VNet, etc. |
| Pricing & SLA | Cost and availability guarantees |

### Key Point: One Plan = Multiple Apps

Deploying multiple apps to the same Plan means they **share compute resources**.

```
[App Service Plan: Standard S1]
├── Web App A
├── Web App B  
└── API App C   ← All share the same VM pool
```

![IMAGE: App Service Plan overview]
`📸 Screenshot: Azure Portal → App Service Plans → Select a Plan → Overview`

---

## Plan Tier Comparison

### Features by Tier

| Tier | Use Case | Key Limitations |
|------|----------|-----------------|
| **Free/Shared** | Learning, experiments | Shared resources, limited features |
| **Basic** | Low traffic | No advanced features |
| **Standard** | Basic production | Medium scale limits |
| **Premium** | High performance, networking | Higher cost |
| **Isolated** | Compliance, network isolation | Highest cost, complexity |

### Feature Requirements by Tier

| Feature | Minimum Tier |
|---------|-------------|
| Custom Domain | Shared |
| SSL Certificate | Basic |
| Deployment Slots | Standard |
| Autoscale | Standard |
| VNet Integration | Standard |
| Private Endpoint | Premium |
| Zone Redundancy | Premium |

### 💡 Practical Advice

> "Start with Standard minimum for production. Operating without Autoscale and Deployment Slots is asking for trouble."

![IMAGE: App Service Plan pricing comparison]
`📸 Screenshot: Azure Portal → App Service Plan → Scale up (App Service plan)`

---

## OS Selection: Linux vs Windows

### Which OS to Choose?

| Consideration | Description |
|---------------|-------------|
| Existing standards | Environment your team knows |
| Dependency compatibility | Specific library requirements |
| Compliance | Enterprise security policies |
| Tooling/Observability | Debugging workflows |

### Practical Differences

| Aspect | Linux | Windows |
|--------|-------|---------|
| Startup speed | Generally faster | Slightly slower |
| Container support | Native | Limited |
| Kudu/SCM | Limited features | Rich features |
| Cost | Same per tier | Same |

**Recommendation:** Choose **Linux** unless you have specific reasons otherwise (better for modern stacks)

```bash
# Create Linux Plan
az appservice plan create \
    --resource-group $RG \
    --name $PLAN_NAME \
    --location koreacentral \
    --sku S1 \
    --is-linux
```

![IMAGE: OS selection when creating App Service Plan]
`📸 Screenshot: Azure Portal → Create App Service Plan → Operating System selection`

---

## Deployment Model: Code vs Container

### Code-based Deployment

Platform provides the runtime; you just deploy code.

**Pros:**
- ✅ Fast onboarding
- ✅ No container management overhead
- ✅ Strong platform integration

**Cons:**
- ❌ No control over base image
- ❌ Runtime updates follow platform policy

```bash
# Create code-based web app
az webapp create \
    --resource-group $RG \
    --plan $PLAN_NAME \
    --name $APP_NAME \
    --runtime "PYTHON|3.11"
```

### Container-based Deployment

Build and deploy your own OCI images.

**Pros:**
- ✅ Full control over runtime stack
- ✅ Local-cloud environment consistency
- ✅ OS-level dependency freedom

**Cons:**
- ❌ Manage patching cycles yourself
- ❌ Registry governance required
- ❌ Image quality directly impacts startup performance

```bash
# Create container-based web app
az webapp create \
    --resource-group $RG \
    --plan $PLAN_NAME \
    --name $APP_NAME \
    --deployment-container-image-name myregistry.azurecr.io/myapp:latest
```

![IMAGE: Publish option when creating Web App]
`📸 Screenshot: Azure Portal → Create Web App → Publish: Code vs Docker Container`

---

## Shared Plan vs Dedicated Plan

### Shared Plan Strategy

Place multiple apps on one Plan:

**Pros:**
- Cost efficient
- Apps with different traffic patterns complement each other

**Cons:**
- Resource competition between apps (Noisy Neighbor)
- One app's issues affect others

### Dedicated Plan Strategy

Separate Plan for each critical app:

**Pros:**
- Resource isolation
- Easier capacity prediction
- Limited blast radius

**Cons:**
- Increased cost

### 💡 Recommended Approach

```
Business-critical apps → Dedicated Plan
Internal tools, low traffic apps → Shared Plan
```

![IMAGE: Multiple apps in same Plan]
`📸 Screenshot: Azure Portal → App Service Plan → Apps tab`

---

## Feature Mapping

Which features depend on Plan vs Deployment Model:

| Feature | Plan Dependent | Deployment Model Dependent |
|---------|----------------|---------------------------|
| Autoscale | ✅ | ❌ |
| Deployment Slots | ✅ | ❌ |
| Private Endpoint | ✅ | ❌ |
| VNet Integration | ✅ | ❌ |
| Custom Startup Image | ❌ | ✅ (Container) |
| Platform Build | ❌ | ✅ (Code) |

---

## Cost and Capacity Planning

### Capacity Planning Considerations

| Item | Question |
|------|----------|
| Traffic | Peak vs average request rate? |
| Resources | CPU-intensive vs IO-intensive? |
| Memory | Memory per request, background workers? |
| Startup time | Cold start frequency? |

### Practical Patterns

```
1. Start with production-ready tier (Standard or higher)
2. Load test with actual traffic patterns
3. Configure Autoscale thresholds and cooldowns
4. Re-evaluate Plan size monthly
```

### Check Plan Info with CLI

```bash
az appservice plan show \
    --resource-group $RG \
    --name $PLAN_NAME \
    --query "{sku:sku, workers:numberOfWorkers, reserved:reserved}" \
    --output json
```

**Example output:**
```json
{
  "sku": {
    "name": "S1",
    "tier": "Standard",
    "capacity": 2
  },
  "workers": 2,
  "reserved": true
}
```

![IMAGE: Scale up screen for App Service Plan]
`📸 Screenshot: Azure Portal → App Service Plan → Scale up (App Service plan)`

---

## Bicep Example: Reproducible Infrastructure

```bicep
param location string = resourceGroup().location
param planName string
param appName string

// App Service Plan
resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: planName
  location: location
  sku: {
    name: 'S1'
    tier: 'Standard'
    capacity: 1
  }
  properties: {
    reserved: true  // Linux
  }
}

// Web App
resource app 'Microsoft.Web/sites@2023-12-01' = {
  name: appName
  location: location
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
  }
}
```

![IMAGE: Bicep deployment result]
`📸 Screenshot: Azure Portal → Resource Group → Deployed resources`

---

## Right-Sizing Checklist

Verify before choosing a Plan:

| Question | Check |
|----------|-------|
| Does it support required networking features? | ☐ |
| Does it support required deployment patterns? (Slots) | ☐ |
| Will Autoscale react before saturation? | ☐ |
| Is memory per instance sufficient at peak? | ☐ |
| Can dependent services handle increased load? | ☐ |

---

## Summary

Key points for Hosting Model selection:

- **OS**: Linux unless you have specific reasons
- **Deployment Model**: Start with Code, Container when control is needed
- **Tier**: Standard or higher for production
- **Plan Strategy**: Dedicated for critical apps, shared for the rest

In the next post, we'll walk through **deploying a Python Flask app to Azure** step by step.

---

## Series Index

1. What is Azure App Service? - Understanding the Platform Architecture
2. Request Lifecycle: How Requests Reach Your App
3. **[Current] Hosting Models: Which Plan Should You Choose?**
4. First Deployment: From Local to Azure (Python/Flask)
5. Mastering Configuration: App Settings & Environment Variables
6. Logging and Monitoring Basics
7. Scaling 101: When to Scale Up vs Scale Out?

---

## References

- [App Service plan overview (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/overview-hosting-plans)
- [Custom container in App Service (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/tutorial-custom-container)
- [App Service pricing (Azure)](https://azure.microsoft.com/pricing/details/app-service/)

---

**Tags:** `Azure` `App Service` `Cloud` `Pricing` `DevOps`
