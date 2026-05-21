---
title: "Azure Kubernetes Service 101 (5/7): Networking and Ingress — the path in and out of the cluster"
series: azure-aks-101
episode: 5
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
seo_description: Understand AKS networking models (CNI vs. Overlay), Ingress controllers, and how traffic flows into your Kubernetes cluster.
---

# Azure Kubernetes Service 101 (5/7): Networking and Ingress — the path in and out of the cluster

> Azure Kubernetes Service 101 series (5/7)

Networking is where AKS often stops feeling simple. Pods can talk to each other, but external requests fail. A Service exists, but domain-based routing does not. The subnet looked large enough, until node growth or IP planning says otherwise. At first, these all blur together.

They get easier once you separate two layers: how pod IPs are assigned, and how external HTTP traffic gets from the edge into Services inside the cluster. This post is about keeping those layers straight.

This is the fifth post in the Azure Kubernetes Service 101 series. Here, we connect the workload model to AKS networking by separating pod IP design from Ingress and external traffic flow.

## Questions to Keep in Mind

- How does pod IP assignment differ from external HTTP routing, and why keep them separate?
- When does kubenet beat Azure CNI, and when does Azure CNI Overlay sidestep both tradeoffs?
- What does an Ingress controller add that a plain Service cannot?

## Big Picture

![azure kubernetes service 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-101/05/05-01-start-with-the-request-path.en.png)

*azure kubernetes service 101 chapter 5 flow overview*

This picture places Networking and Ingress — the path in and out of the cluster inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## Start with the request path

From the outside, this is the shape that matters. The Service is the stable in-cluster endpoint. The Ingress layer is the HTTP router in front of it.

Pod IP allocation, subnet sizing, and CNI choice sit further down the stack. Related problems, yes. The same problem, no.

---

## The first networking decision in AKS

Early cluster design usually forces a few questions.

- How should pods get IP addresses?
- Should pods be directly addressed in the VNet?
- Do external systems need direct pod-IP visibility?
- How much growth do we expect in nodes and clusters?

For most new AKS clusters today, **Azure CNI Overlay** is the first option worth evaluating.

---

## kubenet vs Azure CNI vs Azure CNI Overlay

### 1) kubenet

kubenet was the long-standing lightweight option.

- nodes get IPs from the VNet subnet
- pods use a separate logical address space
- routing and NAT are involved
- IP conservation is a major benefit

But kubenet is now a retirement path, not a forward-looking default. AKS documentation states kubenet support ends on **March 31, 2028**.

### 2) Azure CNI

In the flat Azure CNI model, pods get IPs from the VNet-side address space.

- direct network reachability is strong
- IP planning pressure is higher
- large contiguous subnet planning can become painful

### 3) Azure CNI Overlay

Azure CNI Overlay is the most broadly recommended modern choice for new clusters.

- pod IPs come from a separate logical CIDR
- VNet IP conservation is much better
- management is simpler than flat-IP planning in many environments
- scale characteristics are strong

In plain terms, Azure CNI Overlay keeps Azure integration while dramatically reducing the pain of pod IP consumption.

---

## Three models on one diagram

![Comparison of three AKS network models](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-101/05/05-02-three-models-on-one-diagram.en.png)

*Comparison of three AKS network models*
At a glance, kubenet and Overlay can look similar because both separate node IPs from pod IPs. The important difference is support direction and operating model. For new AKS clusters, the modern recommendation is not “pick any overlay.” It is “start from Azure CNI Overlay unless you have a reason not to.”

---

## A practical recommendation for new clusters

For most greenfield AKS environments:

- start by evaluating **Azure CNI Overlay**
- use flat networking only when direct pod-level network visibility is a real requirement
- treat kubenet as a legacy or migration topic rather than a new default

That decision should be made with both platform and network stakeholders involved. IPAM choices are the sort of decision teams dislike revisiting later.

---

## Service is L4, Ingress is L7

This boundary is worth being strict about.

### Service

- stable virtual IP and DNS name
- load distribution across pods
- LoadBalancer type can expose traffic externally

### Ingress

- HTTP/HTTPS-aware routing
- host-based and path-based rules
- TLS termination
- one entry point for multiple backend services

If you only need to expose one service quickly, a LoadBalancer Service may be enough. Once you have multiple services or richer routing requirements, you usually want an Ingress layer.

---

## Why an Ingress controller exists at all

The Kubernetes Ingress resource is just a declaration. Something still has to read that declaration and program the actual data path.

In AKS, three options come up most often.

### NGINX Ingress Controller

- the most familiar pattern
- broad ecosystem documentation
- great for learning and common deployments

### Application Gateway Ingress Controller (AGIC)

- uses Azure Application Gateway as the L7 front door
- strong Azure network and security integration story
- useful when Application Gateway is already part of the platform design

### Application Routing add-on

- managed NGINX path recommended by Microsoft for easy setup
- good integration with Azure DNS and Key Vault
- lower operational overhead than self-managing the controller

The 101-level summary is enough here: NGINX is the common in-cluster route, AGIC uses Application Gateway, and Application Routing is the managed NGINX flavor in AKS.

For 2026 planning, add one more layer to that summary. Upstream `kubernetes/ingress-nginx` is now in retirement/archived maintenance, so it is no longer the forward-looking place to invest for net-new designs. AKS Application Routing with managed NGINX is still actively supported by Microsoft and remains a valid choice for many new clusters, especially when you want the simplest managed Ingress path today. But the longer-term direction is **Gateway API** through `gateway.networking.k8s.io`, and AKS now supports that direction through the application routing Gateway API implementation. For existing ingress-nginx workloads, moving to App Routing is a practical near-term migration. For brand-new ingress designs in 2026+, Gateway API is usually the better long-term bet.

---

## A simple Ingress example

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: fastapi-hello
spec:
  ingressClassName: webapprouting.kubernetes.azure.com
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: fastapi-hello
                port:
                  number: 80
```

This example uses the Application Routing add-on ingress class. The behavior is straightforward: requests for `api.example.com/` go to the `fastapi-hello` Service.

Ingress usually targets **Services**, not pods directly.

---

## NGINX and AGIC feel different because they live in different places

![Placement difference between NGINX and AGIC](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-101/05/05-03-nginx-and-agic-feel-different-because-th.en.png)

*Placement difference between NGINX and AGIC*
NGINX feels like an in-cluster reverse proxy. AGIC feels like an Azure-native L7 gateway in front of the cluster. Neither is inherently “the right one” in all cases. The right answer depends on existing Azure networking standards, WAF needs, and who owns edge traffic.

---

## Where TLS termination happens

The usual options are:

- at the Ingress controller
- at an external gateway such as Application Gateway

For a 101-level mental model, the key point is simply that TLS handling belongs at the traffic-entry layer, not at the Service abstraction itself.

---

## Three early mistakes teams make

### Treating kubenet like a forward-looking default

It is not. The support direction for new clusters points toward Azure CNI Overlay.

### Deferring IP planning too long

Networking mode is one of the decisions teams least enjoy revisiting. Cluster count, node count, peering, and on-prem connectivity all affect it.

### Using LoadBalancer Services for every externally reachable workload

That works for one or two services. It gets clumsy once the number of public entry points grows.

---

## Re-reading the FastAPI example through this lens

In part 3, the FastAPI app was exposed with a `LoadBalancer` Service. The next step in a more realistic design would be:

1. change the Service to `ClusterIP`
2. place an Ingress in front of it
3. route multiple backend services by host or path

That gives you a cleaner external surface and more consistent TLS and DNS management.

---

## What the next post adds

Once traffic starts rising, the next questions are unavoidable.

- Do we need more pods?
- Do we need more nodes?
- Can event-driven workers scale differently from HTTP APIs?

That is the handoff to part 6: HPA, Cluster Autoscaler, and KEDA.

---

This is part 5 of the Azure Kubernetes Service 101 series. The previous post focused on the internal workload primitives; this one connected those primitives to cluster networking and external traffic. Part 6 picks up from here and explains how AKS reacts when that traffic and workload demand change over time.

---

## Operational checklist

- [ ] Chose kubenet vs. Azure CNI deliberately, not by default
- [ ] Documented why you picked your ingress controller (NGINX, AGIC, etc.)
- [ ] Defined the TLS issuance/renewal path (cert-manager, Key Vault)
- [ ] Restricted pod-to-pod traffic with NetworkPolicy as intended
- [ ] Managed the external LoadBalancer's static IP/DNS through IaC

## Answering the Opening Questions

- **How does pod IP assignment differ from external HTTP routing, and why keep them separate?**
  - The article treats Networking and Ingress — the path in and out of the cluster as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **When does kubenet beat Azure CNI, and when does Azure CNI Overlay sidestep both tradeoffs?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What does an Ingress controller add that a plain Service cannot?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Azure Kubernetes Service 101 (1/7): What is Azure Kubernetes Service? — what managed Kubernetes actually gives you](./01-what-is-aks.md)
- [Azure Kubernetes Service 101 (2/7): Cluster architecture — control plane and node pools](./02-cluster-architecture.md)
- [Azure Kubernetes Service 101 (3/7): Your first cluster, your first deploy — Python/FastAPI](./03-first-cluster-and-deploy.md)
- [Azure Kubernetes Service 101 (4/7): Pod, Deployment, Service — the three ways you express a workload](./04-pod-deployment-service.md)
- **Azure Kubernetes Service 101 (5/7): Networking and Ingress — the path in and out of the cluster (current)**
- Azure Kubernetes Service 101 (6/7): Scaling — HPA, Cluster Autoscaler, KEDA (upcoming)
- Azure Kubernetes Service 101 (7/7): Monitoring and ops — Container Insights, logs, alerts (upcoming)

<!-- toc:end -->

---

## References

### Official Docs
- [Concepts - CNI Networking in AKS](https://learn.microsoft.com/en-us/azure/aks/concepts-network-cni-overview)
- [Configure kubenet networking in AKS](https://learn.microsoft.com/en-us/azure/aks/configure-kubenet)
- [Concepts - Ingress Networking in AKS](https://learn.microsoft.com/en-us/azure/aks/concepts-network-ingress)
- [AKS managed NGINX ingress with the application routing add-on](https://learn.microsoft.com/en-us/azure/aks/app-routing)
- [What is Application Gateway Ingress Controller?](https://learn.microsoft.com/en-us/azure/application-gateway/ingress-controller-overview)

### Related Series
- [Azure App Service 101](../../azure-app-service-101/en/02-request-lifecycle.md) — useful when comparing cluster ingress paths with a simpler platform request path
- [Azure Functions 101](../../azure-functions-101/en/01-what-is-azure-functions.md) — useful when comparing HTTP exposure on a more abstract execution model

Tags: Azure, AKS, Kubernetes, Cloud
