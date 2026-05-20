---
title: "Azure Kubernetes Service Deep Dive (3/6): CNI and Azure CNI Overlay — where Pod IPs come from"
series: azure-aks-deep-dive
episode: 3
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- AKS
- Kubernetes
- Distributed Systems
- Containers
last_reviewed: '2026-05-15'
seo_description: Compare Azure CNI Pod Subnet, Node Subnet, and Overlay in AKS by Pod IP source, VNet pressure, SNAT path, and first-response diagnostics.
---

# Azure Kubernetes Service Deep Dive (3/6): CNI and Azure CNI Overlay — where Pod IPs come from

AKS networking gets confusing fast if every design is still called simply “Azure CNI.” The real operational questions are more specific: which address space gives the Pod its IP, what consumes scarce VNet space, and what path outbound traffic takes after the Pod comes up.

This is the third post in the Azure Kubernetes Service Deep Dive series. Here, I separate Azure CNI Pod Subnet, Node Subnet, and Overlay so the source of Pod IPs becomes concrete.

The goal is not to re-list networking product names. It is to give you a cleaner operator map: where the Pod IP is allocated, what burns scarce VNet space, what an external firewall actually sees, and which symptom usually appears first when the address plan starts to hurt.

## Source Version

This post uses the following upstream versions as external reference points:
- Kubernetes: v1.30.x (https://github.com/kubernetes/kubernetes)
- containerd: v1.7.x (https://github.com/containerd/containerd)
- KEDA: v2.13.x (https://github.com/kedacore/keda)

AKS control plane is managed by Microsoft, so the upstream code here is a behavioral comparison baseline, not a statement about the exact binaries running in the service.

> Azure Kubernetes Service Deep Dive series (3/6)

Pod IPs come from different address models depending on the networking mode.
In current AKS you should separate three cases instead of calling everything simply "Azure CNI."
Azure CNI Pod Subnet is the current flat-networking path for new clusters,
Azure CNI Node Subnet is the older flat model,
and Azure CNI Overlay keeps Pod IPs on a separate overlay CIDR while the VNet mostly sees node IPs.

## Questions to Keep in Mind

- How do kubenet, Azure CNI, and Azure CNI Overlay differ in IP consumption and routing?
- What operational limits emerge when Pod IPs consume real VNet IPs directly?
- In Overlay mode, what is the SNAT path for outbound traffic?

## Big Picture

![azure kubernetes service deep dive chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-deep-dive/03/03-01-put-both-models-side-by-side.en.png)

*azure kubernetes service deep dive chapter 3 flow overview*

This picture places CNI and Azure CNI Overlay — where Pod IPs come from inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of CNI and Azure CNI Overlay — where Pod IPs come from is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Why this matters in real AKS operations

AKS networking is not a one-time cluster-creation checkbox. The chosen model keeps shaping later decisions about new node pools, peering, firewall rules, NAT, private endpoints, and how many Pods the cluster can add before address pressure becomes a production issue.

That is why teams often get surprised twice. First, they treat all Azure CNI modes as the same design and underestimate how differently they consume IP space. Second, they debug outbound failures, IP exhaustion, or policy mismatches as if they were generic Kubernetes problems when the root cause is actually the network model chosen on day one.

The practical payoff of this chapter is simple. Once you can answer “where did this Pod IP come from?” and “what source IP does the outside world see?”, most AKS networking incidents narrow down much faster.

## Put the three models side by side

---

## What CNI does

CNI is the contract that attaches networking to the Pod sandbox.
It creates interfaces,
assigns IPs,
and installs routes and rules.
That means part 2's `RunPodSandbox` path and part 3's Pod IP story are tightly connected.

For operators, that also means Pod startup and Pod networking should not be debugged as unrelated phases. A sandbox that never receives a usable interface can surface as a startup failure, even when the container image and process entrypoint are completely fine.

---

## Azure CNI Pod Subnet, Node Subnet, and Overlay

For 2026 AKS operations, the practical comparison is this:

- **Azure CNI Pod Subnet**: Pods receive VNet-routable IPs from a dedicated pod subnet while nodes stay on a separate node subnet. This is the cleaner flat-network design because node and pod address planning scale independently.
- **Azure CNI Node Subnet (legacy)**: Pods and nodes both consume addresses from the node subnet. The routing model is simple, but this is the version that creates IP exhaustion pressure fastest.
- **Azure CNI Overlay**: Pods receive IPs from an overlay CIDR such as the default `10.244.0.0/16`, nodes stay on the regular VNet subnet, and traffic leaving the cluster is SNATed through the node IP.

Pod Subnet and Node Subnet both preserve direct pod reachability from connected networks because Pod IPs still live in VNet space. Overlay conserves VNet IPs best, but direct inter-cluster pod-to-pod routing through native pod IPs is not the model there.

The design trade-off becomes clearer if you phrase it operationally:

- **Pod Subnet** keeps flat networking while separating node growth from Pod growth.
- **Node Subnet** is easiest to picture, but it is also the quickest path to subnet exhaustion.
- **Overlay** preserves VNet IP space best, but you must reason about egress and external policy through node-facing addresses rather than native Pod-IP reachability.

![IP path differences across three AKS network models](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-deep-dive/03/03-02-azure-cni-versus-overlay.en.png)

*IP path differences across three AKS network models*
---

## Where kubenet stands now

AKS documentation now carries a kubenet retirement timeline.
That means kubenet is no longer a safe long-term default for new designs.
The official networking direction in AKS is moving toward Azure CNI Overlay.

That does not mean every existing kubenet cluster is wrong. It means new designs should treat kubenet as a constrained legacy path, not the default mental model for future AKS networking decisions.

## What tends to fail first in each model

The first visible symptom is not identical across the three models.

- **Pod Subnet** usually fails as pod-subnet sizing pressure, route-policy mismatches, or surprise reachability assumptions between connected networks.
- **Node Subnet** often shows pain earliest as subnet exhaustion because node count and Pod density burn the same address pool together.
- **Overlay** more often shifts the first debugging step toward outbound SNAT, firewall expectations, or external systems assuming Pod IPs are directly routable.

This is why “the Pod cannot reach X” is not a diagnosis yet. You need to know whether you are investigating address allocation, node-based SNAT, or external routing assumptions.

---

## The point of this episode

> AKS networking now needs a three-way distinction. Azure CNI Pod Subnet is the current flat-networking design, where pods use a dedicated pod subnet separate from the node subnet. Azure CNI Node Subnet is the older flat model, where pods and nodes burn the same subnet together. Azure CNI Overlay puts pods on a separate overlay CIDR and preserves VNet IP space best, at the cost of giving up direct native pod-IP routing between clusters.

---

## Where this fits in the series

This is part 3 of the Azure Kubernetes Service Deep Dive series.
Part 2 followed the node-local execution path; this part explains how CNI attaches Pod networking beside that path. The key diagnostic gain is that node execution and Pod addressing no longer blur into the same failure domain.

---

## Call Path Summary

- kubelet `RunPodSandbox` → CNI plugin invocation
- CNI plugin → interface creation, IPAM allocation, routes/rules programming
- Pod sandbox becomes network-ready with Pod IP attached
- Pod traffic exits either through VNet-routable pod subnets or through overlay-to-node SNAT depending on the mode

### Inspect CNI mode and Pod CIDR

```bash
az aks show -n my-cluster -g my-rg \
  --query "{network:networkProfile.networkPlugin, mode:networkProfile.networkPluginMode, pod:networkProfile.podCidr, service:networkProfile.serviceCidr}"

kubectl get nodes -o wide
kubectl get pods -A -o wide | head -20
```

### Check IP pressure and outbound path before changing the cluster

```bash
az network vnet subnet show -g my-network-rg \
  --vnet-name my-vnet \
  --name my-node-subnet \
  --query "{prefix:addressPrefix, available:ipConfigurations}" -o json

kubectl describe pod my-pod -n my-ns | tail -40
kubectl get events -A --sort-by=.lastTimestamp | tail -30
```

Use the Azure-side subnet view to verify address-planning assumptions, then use Pod events to confirm whether the symptom is allocation failure, sandbox setup failure, or a later connectivity problem.

## Failure signatures worth recognizing early

- A Pod that stays in `ContainerCreating` while sandbox setup or CNI attachment keeps retrying points you toward node-local networking setup, not application code.
- Repeated Pending or creation failures during scale events can be the first practical sign that the subnet math was too tight for the expected Pod and node growth.
- Overlay clusters that work internally but fail against external systems often expose policy or firewall assumptions about source IP visibility rather than a generic Kubernetes networking bug.
- Outbound instability under burst traffic can reflect SNAT pressure even when Pod-to-Service communication inside the cluster looks healthy.

## Common points of confusion

- **Azure CNI is not one single design.** Pod Subnet, Node Subnet, and Overlay differ in address source and what the outside world sees.
- **Overlay does not mean “less real” Kubernetes networking.** It means Pod IPs come from a different address space and egress is interpreted differently outside the cluster.
- **CNI is not a decorative add-on after the container starts.** It is part of making the Pod sandbox usable in the first place.
- **Native Pod-IP reachability is an architectural choice, not a guaranteed property of every AKS networking mode.**
- **Address planning is an operations policy decision, not only a cluster-bootstrap step.**

## Operational checklist

- [ ] Computed subnet sizing and service-CIDR headroom against the projected Pod count
- [ ] Validated Overlay choice against external systems (firewalls, peering)
- [ ] Decided on default-deny NetworkPolicy adoption with a staged rollout plan
- [ ] Monitor SNAT-port exhaustion and decided whether to use NAT Gateway
- [ ] Reviewed DNS traffic path (CoreDNS, upstream) and caching policy

## Answering the Opening Questions

- **How do kubenet, Azure CNI, and Azure CNI Overlay differ in IP consumption and routing?**
  - The article treats CNI and Azure CNI Overlay — where Pod IPs come from as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **What operational limits emerge when Pod IPs consume real VNet IPs directly?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **In Overlay mode, what is the SNAT path for outbound traffic?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Azure Kubernetes Service Deep Dive (1/6): Control plane anatomy — what AKS hides from you](./01-control-plane-anatomy.md)
- [Azure Kubernetes Service Deep Dive (2/6): kubelet and containerd — how a container actually starts on a node](./02-kubelet-and-containerd.md)
- **Azure Kubernetes Service Deep Dive (3/6): CNI and Azure CNI Overlay — where Pod IPs come from (current)**
- Azure Kubernetes Service Deep Dive (4/6): Scheduler and Pod placement — who decides which node (upcoming)
- Azure Kubernetes Service Deep Dive (5/6): HPA and Cluster Autoscaler internals — two control loops (upcoming)
- Azure Kubernetes Service Deep Dive (6/6): KEDA internals — how a ScaledObject builds an HPA (upcoming)

<!-- toc:end -->

---

## References

### Primary sources
- [CRI network status fields — `api.proto` @ `v1.30.0`](https://github.com/kubernetes/kubernetes/blob/v1.30.0/staging/src/k8s.io/cri-api/pkg/apis/runtime/v1/api.proto)
- [`kuberuntime_sandbox.go` @ `v1.30.0`](https://github.com/kubernetes/kubernetes/blob/v1.30.0/pkg/kubelet/kuberuntime/kuberuntime_sandbox.go)

### Secondary sources
- [Azure CNI Pod Subnet](https://learn.microsoft.com/en-us/azure/aks/concepts-network-azure-cni-pod-subnet)
- [Azure CNI Overlay](https://learn.microsoft.com/en-us/azure/aks/azure-cni-overlay)
- [Concepts - CNI Networking in AKS](https://learn.microsoft.com/en-us/azure/aks/concepts-network-cni-overview)
- [Configure kubenet networking in AKS](https://learn.microsoft.com/en-us/azure/aks/configure-kubenet)
- [Update Azure CNI IPAM mode and data plane technology](https://learn.microsoft.com/en-us/azure/aks/update-azure-cni)

### Related Series
- [Azure AKS 101](../../azure-aks-101/en/)
- [Azure Functions Deep Dive part 1 — start with the big picture](../../azure-functions-deep-dive/en/01-host-bootstrap.md)

Tags: AKS, Kubernetes, Distributed Systems, Containers
