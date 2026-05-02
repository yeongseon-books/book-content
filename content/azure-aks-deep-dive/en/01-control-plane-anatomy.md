---
title: Control plane anatomy — what AKS hides from you
series: azure-aks-deep-dive
episode: 1
language: en
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AKS
- Kubernetes
- Distributed Systems
- Containers
last_reviewed: '2026-04-29'
---

# Control plane anatomy — what AKS hides from you

## Source Version

This post uses the following upstream versions as external reference points:
- Kubernetes: v1.30.x (https://github.com/kubernetes/kubernetes)
- containerd: v1.7.x (https://github.com/containerd/containerd)
- KEDA: v2.13.x (https://github.com/kedacore/keda)

AKS control plane is managed by Microsoft, so the upstream code here is a behavioral comparison baseline, not a statement about the exact binaries running in the service.

> Azure Kubernetes Service Deep Dive series (1/6)

The AKS 101 series calls AKS a managed Kubernetes service.
That statement is correct.
It is also too coarse for real operations.
You need to know where Microsoft's boundary ends,
where your responsibility begins,
and why one `kubectl get pods` call crosses a chain of components you never log into.

This deep-dive series reopens that hidden layer with code and architecture.
Part 1 draws the map.
It defines what the AKS control plane really is,
where the data plane starts,
and why the only control-plane surface most users ever see is the API server endpoint.

---

## The big picture — AKS control vs data plane

This diagram is the map for the whole series.
Later parts zoom into one box at a time.
Get the boundaries straight now and kubelet, CNI, scheduler, and autoscaling all line up cleanly.

![Managed control plane and node data plane](../../../assets/azure-aks-deep-dive/01/01-01-the-big-picture-aks-control-vs-data-plan.en.png)
The `kube-apiserver`, `etcd`, `kube-controller-manager`, and `kube-scheduler` boxes belong to this episode,
node-side `kubelet + containerd` belong to part 2,
`CNI` to part 3,
`scheduler` internals to part 4,
autoscaling control loops to part 5,
and KEDA's event-to-HPA bridge to part 6.

---

## Why the control plane is invisible in AKS

In self-managed Kubernetes,
you own the control-plane nodes.
You touch `kube-apiserver` flags,
`etcd` backup strategy,
certificate rotation,
and failure recovery yourself.

AKS pushes that heavy layer into a Microsoft-managed boundary.
Users do not normally SSH into control-plane hosts.
They do not usually see a control-plane resource group.
What they see is a managed API endpoint and the node pools attached to it.

That design brings clear advantages.
Control-plane patching,
high availability,
and lifecycle management of the core components move into the service.
It also creates a different debugging model.
When something goes wrong,
you do not log into the process and inspect it directly.
You infer through API behavior,
object status,
Azure diagnostics,
and the surfaces AKS chooses to expose.

---

## Read the SLA carefully

AKS documentation states that the Standard and Premium tiers include Uptime SLA by default,
and that with availability zones the Kubernetes API server is covered at 99.95% availability.
That sentence matters for more than pricing.

The SLA surface is the API server.
That means the component users actually touch is the API endpoint.
How `etcd` is arranged internally,
how many scheduler instances exist,
or where controller-manager runs is generally service internals.
From the operator's point of view,
API success rate and latency become the practical health signal of the control plane.

That is why the first question in an AKS outage is usually the same.
Is the API server down,
slow,
or healthy while some downstream loop like scheduling or reconciliation is lagging.
That split narrows the search space fast.

---

## The path of one request

![API request path to node execution](../../../assets/azure-aks-deep-dive/01/01-02-the-path-of-one-request.en.png)
The API server is the coordinator.
It is not the executor.
Actual container startup happens later on the node through kubelet and the runtime.
That split between recording intent and executing work is the most important model in the entire series.

---

## `kube-apiserver`, `etcd`, `controller-manager`, `scheduler`

The API server is the only control-plane component every AKS user always touches.
`etcd` is the durable state store behind it.
The controller manager runs convergence loops that keep actual state moving toward desired state.
The scheduler chooses a node for Pods that do not have one yet and records the result as a Binding.

You may not manage those binaries directly in AKS,
but you still need the model.
Without it,
control-plane latency,
reconciliation lag,
and scheduling failures all blur together.

---

## The point of this episode

- AKS control plane is Microsoft-managed.
- users practically meet it through the API server surface.
- `etcd`, scheduler, and controller loops still shape the behavior you observe.
- actual execution belongs to the node-side data plane.
- separating control-plane failures from data-plane failures is the first useful diagnostic move.

---

## Where this fits in the series

This is part 1 of the Azure Kubernetes Service Deep Dive series.
If AKS 101 explained the split between the control plane and node pools for first-time readers, this series re-reads the same system through upstream code paths and managed-service boundaries. In the same way that Azure Functions Deep Dive part 1 fixed the Host-versus-Worker map first, this episode fixes the AKS control-plane-versus-data-plane map before the narrower internals.

---

## Call Path Summary

- `kubectl` / client → `kube-apiserver`
- `kube-apiserver` → `etcd` read/write
- controller loops in `kube-controller-manager` reconcile desired vs actual state
- `kube-scheduler` writes a `Pod → Node` binding
- kubelet and node-side runtime execute the work on the chosen node

<!-- toc:begin -->
## In this series

- **Control plane anatomy — what AKS hides from you (current)**
- kubelet and containerd — how a container actually starts on a node (upcoming)
- CNI and Azure CNI Overlay — where Pod IPs come from (upcoming)
- Scheduler and Pod placement — who decides which node (upcoming)
- HPA and Cluster Autoscaler internals — two control loops (upcoming)
- KEDA internals — how a ScaledObject builds an HPA (upcoming)

<!-- toc:end -->

---

## References

### Primary sources
- [`schedule_one.go` @ `v1.30.0`](https://github.com/kubernetes/kubernetes/blob/v1.30.0/pkg/scheduler/schedule_one.go)
- [`default_plugins.go` @ `v1.30.0`](https://github.com/kubernetes/kubernetes/blob/v1.30.0/pkg/scheduler/apis/config/v1/default_plugins.go)
- [`api.proto` @ `v1.30.0`](https://github.com/kubernetes/kubernetes/blob/v1.30.0/staging/src/k8s.io/cri-api/pkg/apis/runtime/v1/api.proto)

### Secondary sources
- [AKS core concepts](https://learn.microsoft.com/en-us/azure/aks/core-aks-concepts)
- [AKS pricing tiers and Uptime SLA](https://learn.microsoft.com/en-us/azure/aks/free-standard-pricing-tiers)
- [Kubernetes components overview](https://kubernetes.io/docs/concepts/overview/components/)

### Related Series
- [Azure AKS 101](../../azure-aks-101/en/)
- [Azure Functions Deep Dive part 1 — host bootstrap and the big picture](../../azure-functions-deep-dive/en/01-host-bootstrap.md)

Tags: AKS, Kubernetes, Distributed Systems, Containers
