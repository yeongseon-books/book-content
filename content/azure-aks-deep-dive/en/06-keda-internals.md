---
title: "Azure Kubernetes Service Deep Dive (6/6): KEDA internals — how a ScaledObject builds an HPA"
series: azure-aks-deep-dive
episode: 6
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
seo_description: See how KEDA turns ScaledObjects into generated HPAs, feeds external metrics, and directly owns the 0-to-1 scale boundary in AKS.
---

# Azure Kubernetes Service Deep Dive (6/6): KEDA internals — how a ScaledObject builds an HPA

Event-driven autoscaling can make KEDA look like a full replacement for HPA. Internally, the model is more precise than that: KEDA layers on top of HPA, feeds the external-metrics path, and takes special responsibility at the scale-to-zero boundary.

This is the final post in the Azure Kubernetes Service Deep Dive series. Here, I trace how a ScaledObject becomes a generated HPA, where the adapter fits, and why KEDA directly owns the 0-to-1 edge.

## Source Version

This post uses the following upstream versions as external reference points:
- Kubernetes: v1.30.x (https://github.com/kubernetes/kubernetes)
- containerd: v1.7.x (https://github.com/containerd/containerd)
- KEDA: v2.14.0 (https://github.com/kedacore/keda/tree/v2.14.0)

AKS control plane is managed by Microsoft, so the upstream code here is a behavioral comparison baseline, not a statement about the exact binaries running in the service.

> Azure Kubernetes Service Deep Dive series (6/6)

KEDA does not replace HPA.
It watches ScaledObjects,
creates HPAs,
feeds the external metrics path,
and directly handles the scale-to-zero boundary by writing replica counts itself.
KEDA installs two main components: the **operator**, which watches `ScaledObject` and `ScaledJob` CRDs, creates the HPA, and reconciles activation and deactivation; and the **metrics adapter**, which implements the Kubernetes external-metrics API so HPA can pull scaler values. A **scaler** is the Go interface each event source implements for activity detection and metric production.

![azure kubernetes service deep dive chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-deep-dive/06/06-01-the-keda-structure.en.png)
*azure kubernetes service deep dive chapter 6 flow overview*

## Questions to Keep in Mind

- How does KEDA synthesize HPA external metrics, and where does the adapter's responsibility end?
- What is the decisive difference between triggers that scale to zero and those that cannot?
- How do ScaledObject and ScaledJob differ in intent, and who picks which?

## The KEDA structure

---

## ScaledObjectReconciler and the generated HPA

`scaledobject_controller.go` checks that the target exposes `/scale`,
ensures the right label exists,
and creates or updates the HPA.
A ScaledObject is the declaration.
The concrete autoscaling artifact inside Kubernetes remains an HPA.

At the scaler layer, upstream `pkg/scalers/scaler.go` defines the interface each event source implements. In current KEDA that means the scaler answers three questions in practice: is this source active, what metric specs should HPA use, and what metric values should the adapter return.

---

## The external metrics path

`api_service.yaml` registers `v1beta1.external.metrics.k8s.io`.
`provider.go` shows the adapter reading the `scaledobject.keda.sh/name` selector and querying the metrics service over gRPC.

![External metrics path into HPA decisions](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-deep-dive/06/06-02-the-external-metrics-path.en.png)

*External metrics path into HPA decisions*
---

## The scale-to-zero boundary

`scale_scaledobjects.go` has separate `scaleToZeroOrIdle()` and `scaleFromZeroOrIdle()` paths.
That exists because HPA does not naturally control the below-`minReplicas` boundary.
KEDA directly updates `/scale` for the 0↔1 region,
while the generated HPA controls the 1↔N region.

![Scale-to-zero boundary between KEDA and HPA](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-deep-dive/06/06-03-the-scale-to-zero-boundary.en.png)

*Scale-to-zero boundary between KEDA and HPA*
---

## The point of this episode

> KEDA does not replace HPA. The operator watches ScaledObjects and ScaledJobs, creates HPAs, and reconciles activation state. The metrics adapter provides `external.metrics.k8s.io`, and each scaler implements the Go-side metric and activity interface for an event source such as Service Bus or Kafka. HPA uses those metrics for autoscaling above one replica, while the scale-to-zero boundary is handled directly by KEDA.

---

## Where this fits in the series

This is the final part of the Azure Kubernetes Service Deep Dive series.
Because part 5 separated HPA from Cluster Autoscaler first, this episode can place KEDA more precisely: above HPA, not instead of it.

---

## Call Path Summary

- `ScaledObject` / `ScaledJob` → KEDA operator reconcile
- operator → generated HPA
- HPA → external metrics query
- KEDA metrics adapter → scaler implementation
- scaler returns activity + metric values
- KEDA directly manages the `0 ↔ 1` boundary through `/scale`

### Debug KEDA state and ScaledObjects

```bash
kubectl get scaledobjects -A
kubectl describe scaledobject my-app -n my-ns | tail -40

kubectl -n kube-system logs -l app=keda-operator --tail=80
kubectl get hpa -n my-ns | grep keda
```

## Operational checklist

- [ ] Tuned per-trigger polling interval and cooldown to workload spike shape
- [ ] Defined fallback behaviour and alerts for KEDA operator failure
- [ ] Wrote a guide for choosing between ScaledJob and ScaledObject
- [ ] Set policy for external-scaler auth (managed identity, secrets)
- [ ] Enabled monitoring on consistency between KEDA metrics and actual replica counts

## Answering the Opening Questions

- **How does KEDA convert a ScaledObject into a generated HPA, and what does it guarantee in the process?**
  - The operator shown in this article, at the `scaledobject_controller.go` path, verifies the target exposes a `/scale` subresource, matches required labels, then creates or updates the generated HPA. So ScaledObject is the declaration, and the actual autoscaling artifact inside Kubernetes is the generated HPA. What operators should verify here is: "if the declaration is valid, does an HPA get created as a concrete artifact connected to the target workload?"
- **What does the metrics adapter take responsibility for in the external metrics path?**
  - The metrics adapter opens the `v1beta1.external.metrics.k8s.io` API surface, reads the `scaledobject.keda.sh/name` selector, queries the metrics service via gRPC, and returns values for the HPA to consume. Its core responsibility is translating external metrics into a Kubernetes API path consumable by HPA. It doesn't directly perform replica changes on the target workload—that step passes to the generated HPA and KEDA's `0 ↔ 1` control boundary.
- **What questions does the scaler interface ask of the event source?**
  - As summarized in this article, the scaler interface asks three things of the event source: whether this source is currently active, what metric spec to pass to the HPA, and what actual metric value the adapter should return. So the scaler isn't a simple number collector but a layer that handles both activation decisions and metric translation together.

<!-- toc:begin -->
## In this series

- [Azure Kubernetes Service Deep Dive (1/6): Control plane anatomy — what AKS hides from you](./01-control-plane-anatomy.md)
- [Azure Kubernetes Service Deep Dive (2/6): kubelet and containerd — how a container actually starts on a node](./02-kubelet-and-containerd.md)
- [Azure Kubernetes Service Deep Dive (3/6): CNI and Azure CNI Overlay — where Pod IPs come from](./03-cni-and-azure-cni-overlay.md)
- [Azure Kubernetes Service Deep Dive (4/6): Scheduler and Pod placement — who decides which node](./04-scheduler-and-pod-placement.md)
- [Azure Kubernetes Service Deep Dive (5/6): HPA and Cluster Autoscaler internals — two control loops](./05-hpa-and-cluster-autoscaler-internals.md)
- **Azure Kubernetes Service Deep Dive (6/6): KEDA internals — how a ScaledObject builds an HPA (current)**

<!-- toc:end -->

---

## References

### Primary sources
- [`scaledobject_controller.go` @ `v2.14.0`](https://github.com/kedacore/keda/blob/v2.14.0/controllers/keda/scaledobject_controller.go)
- [`scaler.go` @ `v2.14.0`](https://github.com/kedacore/keda/blob/v2.14.0/pkg/scalers/scaler.go)
- [`provider.go` @ `v2.14.0`](https://github.com/kedacore/keda/blob/v2.14.0/pkg/provider/provider.go)
- [`scale_scaledobjects.go` @ `v2.14.0`](https://github.com/kedacore/keda/blob/v2.14.0/pkg/scaling/executor/scale_scaledobjects.go)
- [`api_service.yaml` @ `v2.14.0`](https://github.com/kedacore/keda/blob/v2.14.0/config/metrics-server/api_service.yaml)

### Secondary sources
- [KEDA scaling deployments and custom resources](https://keda.sh/docs/2.14/concepts/scaling-deployments/)
- [Horizontal Pod Autoscaling](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)

### Related Series
- [Azure AKS 101](../../azure-aks-101/en/)
- [Azure Functions Deep Dive part 5 — reading control loops](../../azure-functions-deep-dive/en/05-scaling-internals.md)

Tags: AKS, Kubernetes, Distributed Systems, Containers
