---
title: Scheduler and Pod placement — who decides which node
series: azure-aks-deep-dive
episode: 4
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
seo_description: Learn how the Kubernetes scheduler filters, scores, and binds Pods in AKS so you can diagnose Pending Pods by placement failure instead of guesswork.
---

# Scheduler and Pod placement — who decides which node

When a Pod stays Pending, it is tempting to jump straight to node health or runtime logs. Very often the earlier decision point matters more: scheduler has to evaluate constraints, narrow the candidate set, and commit a Binding before node-side execution can even begin.

This is the fourth post in the Azure Kubernetes Service Deep Dive series. Here, I walk through how kube-scheduler filters, scores, and finally records placement decisions.

The useful shift is from “Pending means something is wrong on the node” to “Pending can be a placement story long before kubelet ever sees the Pod.” That single distinction saves a surprising amount of wasted debugging time.

## Source Version

This post uses the following upstream versions as external reference points:
- Kubernetes: v1.30.x (https://github.com/kubernetes/kubernetes)
- containerd: v1.7.x (https://github.com/containerd/containerd)
- KEDA: v2.13.x (https://github.com/kedacore/keda)

AKS control plane is managed by Microsoft, so the upstream code here is a behavioral comparison baseline, not a statement about the exact binaries running in the service.

> Azure Kubernetes Service Deep Dive series (4/6)

Scheduling is not a free-CPU calculator.
Affinity,
taints,
ports,
volumes,
and topology constraints all participate.
The upstream scheduler code makes the structure clear.
It filters impossible nodes,
scores feasible ones,
and records a Binding.

---

## Questions this chapter answers

- Through which stages does kube-scheduler narrow down nodes for a single Pod?
- What intent originally drove nodeSelector, affinity, taints/tolerations, and topologySpreadConstraints?
- PriorityClass and preemption protect the SLO — who pays the side-effect bill?
- When a Pod is unschedulable, what are the first three debugging steps?
- How should placement policies differ between stateful and stateless workloads?

## Why this matters in real AKS operations

Scheduler behavior is where abstract policy becomes an operational consequence. Zone-spread rules, taints, affinity, PVC topology, spot-node usage, and preemption all meet at the same decision point. If this layer is fuzzy, teams end up paying for it as Pending Pods, uneven failure domains, or high-priority workloads displacing the wrong tenants.

This is also the chapter that makes autoscaling behavior easier to read. HPA can request more replicas, but if scheduler cannot find feasible nodes, the next thing you see is not more Ready Pods. It is a set of Pending Pods that Cluster Autoscaler may or may not be able to help later.

## The three steps

![Scheduling stages from pending Pod to Binding](../../../assets/azure-aks-deep-dive/04/04-01-the-three-steps.en.png)

*Scheduling stages from pending Pod to Binding*
---

## Filter and Score

`ScheduleOne()` separates the scheduling cycle from the binding cycle.
Filter removes nodes where the Pod cannot run.
Score ranks the nodes that remain.
The default plugin set includes `NodeResourcesFit`, `NodeAffinity`, `PodTopologySpread`, and `InterPodAffinity`.

Operationally, Filter and Score answer two different questions:

- **Filter** asks: “Can this Pod run here at all?”
- **Score** asks: “If several nodes work, which one is the better placement?”

Confusing those two questions is one reason placement policies become hard to explain during incidents.

![Node filtering and scoring in placement](../../../assets/azure-aks-deep-dive/04/04-02-filter-and-score.en.png)

*Node filtering and scoring in placement*
---

## What Binding means

The binding cycle writes the selected node back through the API server.
Only then can kubelet pick up the Pod and start the execution path from part 2.
The scheduler's output is therefore not a running Pod.
It is a `Pod -> Node` decision.

That is the key split to keep in your head during incidents. “No node was selected” and “a node was selected but startup later failed” are not neighboring nuances of the same problem. They are different branches of the system.

## Placement policy is broader than free CPU

Teams often talk about scheduling as if it were just a leftover-capacity calculator. Real production placement is wider than that.

- `nodeSelector` and affinity encode intent about where workloads belong.
- taints and tolerations encode which workloads are allowed into special-purpose nodes.
- topology spread and anti-affinity encode blast-radius policy.
- PVC and zone constraints encode where stateful workloads are even allowed to land.

Seen this way, scheduler is not just a resource balancer. It is one of the main policy enforcement loops in the cluster.

## Failure signatures to recognize early

- `0/N nodes are available` usually means Filter already rejected every candidate before node-local startup was even relevant.
- A Pod that has feasible nodes but still struggles later may point to binding-time conflicts, preemption side effects, or downstream node execution problems rather than core placement rules.
- Stateful workloads that look underutilized can still remain Pending because storage topology and zone alignment are tighter constraints than CPU or memory.
- Repeated preemption events often mean the PriorityClass policy is compensating for a capacity or tenancy design problem rather than solving it.

## Diagnose placement before you read runtime logs

The first-pass workflow should stay close to scheduler signals:

1. Check whether the Pod is still Pending and whether `nodeName` is empty.
2. Read the most recent scheduler-facing events from `kubectl describe pod`.
3. Compare those messages against node labels, taints, zones, and agent pools.

That sequence usually tells you whether the problem is impossible placement, poor candidate quality, or something that only started after Binding.

---

## The point of this episode

> kube-scheduler does not execute Pods. It first removes impossible nodes through Filter plugins, then ranks the feasible candidates through Score plugins, and finally records the decision as a Binding in the API server. The key diagnostic split for a Pending Pod is whether it has no feasible nodes at all because Filter rejected every candidate, or whether feasible nodes existed but binding still failed later because of preemption, reservation conflicts, or another rare post-score issue.

---

## Where this fits in the series

This is part 4 of the Azure Kubernetes Service Deep Dive series.
Parts 2 and 3 covered node execution and networking; this part explains the earlier placement decision. The diagnostic value is that Pending Pods can now be split cleanly into placement failures, binding-time failures, and node-side execution delays.

---

## Call Path Summary

- Pod without `nodeName` → scheduler queue
- Filter plugins remove impossible nodes
- Score plugins rank feasible nodes
- scheduler writes Binding through the API server
- kubelet on the chosen node starts the node-local execution path

### Diagnose placement failures of a pending Pod

```bash
kubectl get pods -A --field-selector status.phase=Pending
kubectl describe pod my-pod -n my-ns | tail -30
kubectl get events --sort-by=.lastTimestamp -n my-ns | tail -20
kubectl get nodes -L topology.kubernetes.io/zone,agentpool
```

### Inspect the policy surface that the scheduler is actually reading

```bash
kubectl get pod my-pod -n my-ns -o yaml | grep -E "nodeSelector|tolerations|affinity|priorityClassName"
kubectl describe node my-node | tail -40
kubectl get pvc -n my-ns
```

These checks make the placement contract visible: Pod-side constraints, node-side taints and labels, and storage objects that may lock stateful workloads to a narrower zone set than expected.

## Common points of confusion

- **Scheduler does not run containers.** It records a placement decision.
- **Pending does not automatically mean kubelet trouble.** The Pod may have failed long before node execution began.
- **Filter failure and Score preference are not the same kind of result.** One removes candidates; the other ranks survivors.
- **PriorityClass is not a free performance knob.** Its cost is often paid by other workloads through preemption.
- **Stateful placement is constrained by storage topology as much as by compute capacity.**

## Operational checklist

- [ ] Specified affinity/anti-affinity and zone spread for key workloads
- [ ] Classified workloads by PriorityClass policy and preemption tolerance
- [ ] Assigned an owner to every node taint and toleration
- [ ] Prepared alerts and an auto-diagnostic script for Pending Pods
- [ ] Aligned PVC zone-affinity with node zones for stateful workloads

<!-- toc:begin -->
## In this series

- [Control plane anatomy — what AKS hides from you](./01-control-plane-anatomy.md)
- [kubelet and containerd — how a container actually starts on a node](./02-kubelet-and-containerd.md)
- [CNI and Azure CNI Overlay — where Pod IPs come from](./03-cni-and-azure-cni-overlay.md)
- **Scheduler and Pod placement — who decides which node (current)**
- HPA and Cluster Autoscaler internals — two control loops (upcoming)
- KEDA internals — how a ScaledObject builds an HPA (upcoming)

<!-- toc:end -->

---

## References

### Primary sources
- [`schedule_one.go` @ `v1.30.0`](https://github.com/kubernetes/kubernetes/blob/v1.30.0/pkg/scheduler/schedule_one.go)
- [`default_plugins.go` @ `v1.30.0`](https://github.com/kubernetes/kubernetes/blob/v1.30.0/pkg/scheduler/apis/config/v1/default_plugins.go)

### Secondary sources
- [Kubernetes scheduler](https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/)
- [Assigning Pods to Nodes](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/)

### Related Series
- [Azure AKS 101](../../azure-aks-101/en/)
- [Azure Functions Deep Dive part 4 — dispatcher and invocation](../../azure-functions-deep-dive/en/04-dispatcher-and-invocation.md)

Tags: AKS, Kubernetes, Distributed Systems, Containers
