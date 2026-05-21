---
series: kubernetes-101
episode: 5
title: "Kubernetes 101 (5/10): Ingress"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Kubernetes
  - Ingress
  - HTTP
  - TLS
  - DevOps
seo_description: A beginner guide to Kubernetes Ingress — host and path routing, TLS termination, and how to choose an Ingress Controller
last_reviewed: '2026-05-15'
---

# Kubernetes 101 (5/10): Ingress

Exposing one service to the outside world is simple enough. Exposing several services, under one domain, with TLS and path-based routing is where copy-paste load balancers start turning into cost and operational drift.

This is post 5 in the Kubernetes 101 series.

Here, we will separate the declarative Ingress rule from the controller that enforces it, then use that split to reason about host routing, path routing, and TLS termination.

> Ingress is the routing rule. The Ingress controller is the runtime that makes the rule real.


![kubernetes 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/05/05-01-concept-at-a-glance.en.png)
*kubernetes 101 chapter 5 flow overview*

## Questions to Keep in Mind

- Splitting *Ingress* and *IngressController?
- Host / path* routing?
- TLS termination?

## Why It Matters

A *LoadBalancer Service per app* explodes *cost*. *Ingress* collapses everything into a *single entry*.

## Key Terms

- **Ingress**: an *L7 routing rule* object.
- **IngressController**: the *proxy that enforces the rules* (nginx, Envoy).
- **host**: a *domain name*.
- **path**: a *URL path*.
- **TLS termination**: *decryption at the Ingress*.

## Before / After

**Before**: an *LB per service* — *cost* and *ops burden*.

**After**: one *Ingress* and one *Controller* split traffic *by path*.

## Hands-on: Host and Path Routing

### Step 1 — Ingress manifest

```python
"""
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata: {name: web}
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service: {name: api, port: {number: 80}}
      - path: /
        pathType: Prefix
        backend:
          service: {name: web, port: {number: 80}}
"""
```

### Step 2 — Apply

```python
import subprocess

def apply(path):
    subprocess.run(["kubectl", "apply", "-f", path], check=True)
```

### Step 3 — Create a TLS secret

```python
def tls_secret(name, cert, key):
    subprocess.run([
        "kubectl", "create", "secret", "tls", name,
        "--cert", cert, "--key", key,
    ], check=True)
```

### Step 4 — Apply TLS

```python
"""
spec:
  tls:
  - hosts: [example.com]
    secretName: example-tls
"""
```

### Step 5 — Verify

```python
def curl(host, path):
    res = subprocess.run(
        ["curl", "-sk", f"https://{host}{path}"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

## Verification workflow

```bash
kubectl get ingress web
kubectl describe ingress web
curl -sk -H 'Host: example.com' https://<ingress-address>/api
```

**Expected output:** `get ingress` should show an address or controller-managed endpoint, `describe ingress` should list the expected host/path/backend mapping, and the `curl` response should prove that `/api` reaches a different backend than the site root.

**Failure modes to check first:**

- An address-less Ingress usually means the controller path is broken, not the rule object itself.
- TLS handshake failures often come from the secret namespace or secret name before they come from certificate content.
- If `/` works and `/api` does not, inspect path precedence and `pathType` interpretation first.

## What to Notice in This Code

- *Ingress* is the *rule*; the *Controller* is the *executor*.
- *pathType: Prefix* is the *common default*.
- *TLS* terminates at the *Ingress*.

## Five Common Mistakes

1. **Expecting traffic without an *IngressController*.**
2. **Skipping *pathType* and hitting compatibility issues.**
3. **Putting the *TLS secret* in the *wrong namespace*.**
4. **Failing to fix *LB cost explosion* with Ingress.**
5. **Misreading *path priority*.**

## How This Shows Up in Production

*nginx-ingress* or the *AWS ALB Controller* reflects *Ingress objects* into the *external LB*, while *cert-manager* issues *TLS* automatically.

## How a Senior Engineer Thinks

- *Ingress* is a *routing rule*.
- *Controller* features *vary widely*.
- *TLS* is delegated to *cert-manager*.
- *Gateway API* is the *next standard*.
- *Entry points* are kept *minimal*.

## Checklist

- [ ] *Controller* installed.
- [ ] *pathType* explicit.
- [ ] *TLS* automated.
- [ ] *Entry points* consolidated.

## Practice Problems

1. State the *difference* between Ingress and IngressController in one line.
2. Name *one reason* TLS termination at the Ingress is good.
3. Describe in one line *what limit* the Gateway API addresses.

## Wrap-up and Next Steps

With routing in place, the next step is *separating config and secrets*. The next post covers *ConfigMap and Secret*.

## Answering the Opening Questions

- **Splitting *Ingress* and *IngressController?**
  - The article treats Ingress as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Host / path* routing?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **TLS termination?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Kubernetes 101 (1/10): What is Kubernetes?](./01-what-is-kubernetes.md)
- [Kubernetes 101 (2/10): Pod](./02-pod.md)
- [Kubernetes 101 (3/10): Deployment](./03-deployment.md)
- [Kubernetes 101 (4/10): Service](./04-service.md)
- **Ingress (current)**
- ConfigMap and Secret (upcoming)
- Volume (upcoming)
- HPA (upcoming)
- Helm (upcoming)
- Kubernetes in Operation (upcoming)

<!-- toc:end -->

## References

- [Ingress (Kubernetes)](https://kubernetes.io/docs/concepts/services-networking/ingress/)
- [Ingress Controllers](https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/)
- [cert-manager](https://cert-manager.io/docs/)
- [Gateway API](https://gateway-api.sigs.k8s.io/)
- [Set up Ingress on Minikube](https://kubernetes.io/docs/tasks/access-application-cluster/ingress-minikube/)

Tags: Kubernetes, Ingress, HTTP, TLS, DevOps
