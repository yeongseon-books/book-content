---
title: "Azure Kubernetes Service 101 (2/7): Cluster architecture — control plane and node pools"
series: azure-aks-101
episode: 2
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
seo_description: Explore Azure Kubernetes Service (AKS) architecture, including the managed control plane, system vs. user node pools, and Spot capacity strategy.
---

# Azure Kubernetes Service 101 (2/7): Cluster architecture — control plane and node pools

> Azure Kubernetes Service 101 series (2/7)

The first structural split to get right in AKS is the split between the cluster's brain and the place where containers actually run. If you blur those together, cost, upgrades, failure handling, and scaling all become harder to reason about. AKS draws that boundary pretty clearly for you.

This post is about reading that boundary. We'll look at what the control plane does, why system and user node pools exist, and where Spot capacity fits into the picture.

This is the second post in the Azure Kubernetes Service 101 series. Here, we turn the managed-Kubernetes boundary into a concrete cluster shape by looking at the control plane, node pools, and their operational roles.

![azure kubernetes service 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-101/02/02-01-cut-the-cluster-in-half.en.png)
*azure kubernetes service 101 chapter 2 flow overview*

## Questions to Keep in Mind

- What does each control-plane component (API server, scheduler, controller manager, etcd) actually do?
- How does the kubelet, kube-proxy, and container runtime path on a node fit together?
- Where do AKS managed identity and RBAC plug into the authn/authz flow?

## Cut the cluster in half

The left side is the Azure-managed layer. The right side is the layer you shape more directly. That single picture explains a lot: why the control plane is not billed separately, why node count is your decision, and why pod scaling and node scaling are different conversations.

---

## What the control plane actually does

The control plane is the cluster's decision-making layer.

- **API server**: the entry point for every declaration and query.
- **etcd**: the persistence layer for cluster state.
- **Scheduler**: decides where new pods should run.
- **Controller loops**: keep deployments, endpoints, and other resources converging toward desired state.

In AKS, Azure runs this layer for you. You still use the API constantly, but you are not typically building, placing, and maintaining API server nodes yourself.

That is the concrete meaning of managed Kubernetes. It does not remove Kubernetes. It removes a large chunk of the mechanics around operating Kubernetes.

---

## What a node pool is

A node pool is a group of VMs with the same configuration.

- same VM size
- same OS SKU
- same scaling envelope
- same pool mode

Every pod eventually lands on a node in one of these pools. That makes node pools the place where abstract Kubernetes intent turns into real capacity decisions.

Most practical questions become node-pool questions pretty quickly.

- Which VM size should this workload use?
- Should system components be isolated from application pods?
- Should we use Spot capacity?
- What should the autoscaler bounds be?

Pods are the logical unit. Node pools are the capacity and cost unit.

---

## System node pool vs user node pool

This is the first node-pool distinction to learn in AKS.

![Role split between system and user pools](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-101/02/02-02-system-node-pool-vs-user-node-pool.en.png)

*Role split between system and user pools*
### System node pool

System pools are where critical cluster components are expected to run.

- CoreDNS
- metrics-server
- cluster add-ons

AKS recommends keeping system components there and running your application on user pools instead. In a tiny learning cluster with only one pool, app pods may run on the system pool. In production, separation is the better default.

### User node pool

User pools are for your workload.

- web APIs
- background workers
- batch jobs
- scheduled jobs

That separation reduces the odds that a badly behaved application workload interferes with core cluster services.

---

## Why the split matters

The benefit is not philosophical. It is operational.

1. System pods and app pods do not compete for the same space by default.
2. User capacity can scale independently.
3. Spot capacity can be attached where it makes sense.
4. Mixed pool strategies become easier, including Windows user pools alongside Linux system pools.

The shortest useful summary is this:

> The system pool keeps the cluster alive. The user pool runs the business workload.

---

## How many node pools should you have?

Do not over-segment too early. A common starting point is simple.

### Small, sane starting shape

- one system pool
- one user pool

That is enough for most introductory clusters.

### When clusters get larger

You may split user pools by workload shape.

- latency-sensitive API pool
- batch or worker pool
- Spot-only pool
- GPU or memory-optimized pool

Node pools are usually better organized around **workload characteristics** than around team boundaries.

---

## Regular pools vs Spot pools

Once cost enters the conversation, Spot capacity shows up quickly.

### Regular node pools

Use regular pools when stability is the primary concern.

- baseline capacity
- critical APIs
- workloads where interruption is expensive

### Spot node pools

Spot pools use discounted Azure capacity that can be evicted.

- lower cost
- lower stability
- best for interruption-tolerant workloads

Good examples include queue consumers, batch processing, and retry-friendly background work. A business-critical API with no non-Spot fallback is usually the wrong place for Spot.

---

## How scheduling relates to node pools

Kubernetes does not schedule “to a node pool” directly. It schedules to nodes. In AKS, the node pool identity is expressed through labels, taints, and pool configuration.

The useful hierarchy is:

- node pool: management unit
- node: actual scheduling target
- pod: placed through selectors, taints, affinity, and resource requirements

That is why pool design and placement policy are tightly connected. A tainted system pool plus explicit selectors on user workloads is not ceremony. It is how you encode intent. In practice, many teams use the AKS-recommended `CriticalAddonsOnly=true:NoSchedule` taint on the system pool so ordinary application pods stay on user pools unless you opt in explicitly.

---

## Upgrades make the boundary even clearer

When teams say “we upgraded the cluster,” that can mean a few different things.

- control plane version upgrade
- node pool Kubernetes version upgrade
- node image upgrade

Those are related, but not identical. The control plane can move first, with node pools following. So “the cluster version changed” is often an incomplete operational statement. You also want to know **which pools have caught up**.

---

## Constraints worth remembering early

AKS documentation repeats a few practical rules often enough that they are worth anchoring now.

- A cluster must always have at least one system node pool.
- System node pools must be Linux.
- User node pools can be Linux or Windows.
- Spot capacity belongs on user pools.
- For production, system pools should be sized with fault tolerance in mind.

For a beginner-friendly mental model, this is enough: the initial pool is a system pool, and your applications should graduate into user pools.

---

## The five fastest architecture questions

When someone hands you an AKS cluster, these questions reveal a lot quickly.

1. Are system and user pools separated?
2. How many user pools exist, and what is each one for?
3. Is Spot being used anywhere?
4. What are the autoscaler bounds per pool?
5. Are workloads actually landing on the intended pools?

Those questions are more useful than a generic architecture diagram because they connect directly to cost and failure behavior.

---

This is part 2 of the Azure Kubernetes Service 101 series. Part 1 defined the managed-Kubernetes boundary; this post turned that boundary into a concrete cluster shape. The next step is to turn that shape into a running cluster and a small FastAPI deployment.

---

## Quick check

```bash
kubectl get nodes -o wide
kubectl get pods -n kube-system
```

To connect the Azure-resource view with the Kubernetes view, add these as a pair.

```bash
az aks nodepool list \
  --resource-group $RG \
  --cluster-name $CLUSTER \
  --query "[].{name:name, mode:mode, count:count, vmSize:vmSize, osType:osType}"

kubectl get nodes -L kubernetes.azure.com/agentpool,kubernetes.azure.com/mode
```

The first command shows the pool definitions as Azure resources. The second shows which nodes actually belong to which pool and mode from the Kubernetes side. Reading them together is how node-pool design stops being abstract.

## A practical first-pass troubleshooting order

Architecture becomes real when it shortens the first five minutes of debugging.

### 1. Decide whether the problem starts at the API layer

If `kubectl get nodes` is unexpectedly slow or fails outright, start with the control-plane boundary and credentials before diving into workload YAML. That is usually a faster cut than inspecting application pods immediately.

### 2. If pods do not start, inspect pool capacity and scheduling signals

When pods stay `Pending`, the question is often not “is Kubernetes broken?” but “what prevented this pod from landing on a node?”

```bash
kubectl describe pod <pod-name>
kubectl top nodes
```

`describe` exposes selector mismatches, taints, and insufficient CPU or memory. `kubectl top nodes` gives you a quick read on which pool is actually under pressure.

### 3. If system workloads wobble, treat the blast radius as larger

There is a meaningful difference between an app Deployment being unhealthy and `kube-system` components such as CoreDNS or metrics-server wobbling. The latter usually means you are no longer looking at one workload problem. You are looking at cluster-operability risk.

That is why the control-plane vs node-pool model matters operationally. It is not only an architecture diagram. It is the fastest way to decide whether you should inspect the API boundary, system pools, or user-pool capacity first.

## Operational checklist

- [ ] Can articulate the role of each control-plane component
- [ ] Mapped the kubelet/kube-proxy/runtime path on a node
- [ ] Marked where managed identity and RBAC sit in authn/authz
- [ ] Inventoried what AKS creates in the managed `MC_` resource group
- [ ] Estimated blast radius of node and control-plane upgrades

## Answering the Opening Questions

- **What does each control-plane component (API server, scheduler, controller manager, etcd) actually do?**
  - The article treats Cluster architecture — control plane and node pools as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **How does the kubelet, kube-proxy, and container runtime path on a node fit together?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Where do AKS managed identity and RBAC plug into the authn/authz flow?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Azure Kubernetes Service 101 (1/7): What is Azure Kubernetes Service? — what managed Kubernetes actually gives you](./01-what-is-aks.md)
- **Azure Kubernetes Service 101 (2/7): Cluster architecture — control plane and node pools (current)**
- Azure Kubernetes Service 101 (3/7): Your first cluster, your first deploy — Python/FastAPI (upcoming)
- Azure Kubernetes Service 101 (4/7): Pod, Deployment, Service — the three ways you express a workload (upcoming)
- Azure Kubernetes Service 101 (5/7): Networking and Ingress — the path in and out of the cluster (upcoming)
- Azure Kubernetes Service 101 (6/7): Scaling — HPA, Cluster Autoscaler, KEDA (upcoming)
- Azure Kubernetes Service 101 (7/7): Monitoring and ops — Container Insights, logs, alerts (upcoming)

<!-- toc:end -->

---

## References

### Official Docs
- [What is Azure Kubernetes Service (AKS)?](https://learn.microsoft.com/en-us/azure/aks/what-is-aks)
- [Use system node pools in Azure Kubernetes Service (AKS)](https://learn.microsoft.com/en-us/azure/aks/use-system-pools)
- [Create node pools in Azure Kubernetes Service (AKS)](https://learn.microsoft.com/en-us/azure/aks/create-node-pools)
- [Deploy an Azure Kubernetes Service (AKS) Cluster Using Azure CLI](https://learn.microsoft.com/en-us/azure/aks/learn/quick-kubernetes-deploy-cli)

### Related Series
- [Azure App Service 101](../../azure-app-service-101/en/) — useful when contrasting AKS with a platform that has no node concept at all
- [Azure Functions 101](../../azure-functions-101/en/) — useful when comparing orchestration with event-driven execution

Tags: Azure, AKS, Kubernetes, Cloud
