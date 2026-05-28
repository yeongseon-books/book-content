---
series: kubernetes-101
episode: 4
title: "Kubernetes 101 (4/10): Service"
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
  - Service
  - Networking
  - DNS
  - DevOps
seo_description: A beginner guide to Kubernetes Services — ClusterIP, NodePort, LoadBalancer, selectors, and how cluster DNS keeps Pods reachable
last_reviewed: '2026-05-15'
---

# Kubernetes 101 (4/10): Service

Once several Pods are running, their IP addresses stop being a stable integration surface. Pods restart, move, and get recreated, but callers still need one name and one contract that keeps working.

This is the 4th post in the Kubernetes 101 series.

Here, we will look at Service as the networking contract that hides changing Pod membership behind a stable virtual IP and DNS name for both internal and external traffic patterns.

> A Service is the answer to “how do I keep calling this workload after the Pods behind it change?”


![kubernetes 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/04/04-01-concept-at-a-glance.en.png)
*kubernetes 101 chapter 4 flow overview*

## Questions to Keep in Mind

- The problem a *Service* solves?
- ClusterIP / NodePort / LoadBalancer?
- How *selectors* match?

## Why It Matters

For *microservices* to call each other by *name*, a *Service* is mandatory.

## Key Terms

- **ClusterIP**: an internal *virtual IP* (default).
- **NodePort**: exposes a *port on every node*.
- **LoadBalancer**: provisions a *cloud LB*.
- **selector**: matches *Pods by labels*.
- **DNS name**: `svc.namespace.svc.cluster.local`.

## Before / After

**Before**: calling a *Pod IP* directly breaks on *restart*.

**After**: calling the *Service name* through *DNS* is *stable*.

## Hands-on: Expose a Service

### Step 1 — Service manifest

```python
"""
apiVersion: v1
kind: Service
metadata: {name: web}
spec:
  selector: {app: web}
  ports:
  - port: 80
    targetPort: 80
"""
```

### Step 2 — Apply and read

```python
import subprocess

def apply_and_get(path):
    subprocess.run(["kubectl", "apply", "-f", path], check=True)
    return subprocess.run(
        ["kubectl", "get", "svc", "web"],
        capture_output=True, text=True, check=True,
    ).stdout
```

### Step 3 — DNS check

```python
def dns_check(target):
    res = subprocess.run([
        "kubectl", "run", "tmp", "--rm", "-i", "--restart=Never",
        "--image=busybox", "--", "nslookup", target,
    ], capture_output=True, text=True, check=True)
    return res.stdout
```

### Step 4 — Switch to NodePort

```python
def to_nodeport(svc):
    subprocess.run([
        "kubectl", "patch", "svc", svc, "-p",
        '{"spec": {"type": "NodePort"}}',
    ], check=True)
```

### Step 5 — Cleanup

```python
def delete(svc):
    subprocess.run(["kubectl", "delete", "svc", svc], check=True)
```

## Verification workflow

```bash
kubectl get svc web
kubectl get endpoints web
kubectl run dnscheck --rm -i --restart=Never --image=busybox -- nslookup web.default.svc.cluster.local
```

**Expected output:** the Service should have a ClusterIP, the Endpoints object should list one or more Pod IPs, and DNS lookup should resolve the service name from inside the cluster. Those three checks tell you whether naming, backend selection, and internal discovery all line up.

**Failure modes to check first:**

- A Service with empty Endpoints almost always means selector/label mismatch.
- DNS success with request failure usually means `targetPort` and the container listen port disagree.
- Calls from another namespace often fail because the caller dropped the namespace part of the service name.

## What to Notice in This Code

- The *selector* must match *Deployment labels*.
- *targetPort* is the *container port*.
- The *DNS name* standardizes calls.

## Five Common Mistakes

1. **Mismatched *selector* and *labels* break routing.**
2. **Using *NodePort* as the *production entry point*.**
3. **Calling a *Pod IP* directly.**
4. **Using *Headless Service* for the *common case*.**
5. **Dropping the *namespace* from the *DNS name*.**

## How This Shows Up in Production

*ClusterIP* handles *internal* traffic, *LoadBalancer* the *external entry*, and *Ingress* the *L7 routing*.

## How a Senior Engineer Thinks

- The *Service name* is an *API contract*.
- *Internal* traffic uses *ClusterIP*.
- *External* uses *LoadBalancer + Ingress*.
- *Headless* is for *stateful* workloads.
- *DNS TTL* is also a *variable*.

## Checklist

- [ ] *Selector* match verified.
- [ ] *type* explicit.
- [ ] Calls go through the *DNS name*.
- [ ] *External exposure* via *Ingress* first.

## Practice Problems

1. State the *difference* between ClusterIP and LoadBalancer in one line.
2. Explain in one line *why* the selector is critical.
3. Name *one typical use* of a Headless Service.

## Wrap-up and Next Steps

Internal traffic is solved. The next post covers *Ingress*, which splits *external HTTP* by *path*.

## Answering the Opening Questions

- **What problem does a Service solve?**
  - Pod IPs change on every restart or reschedule. A Service places a stable virtual IP and DNS name in front of a selector-matched Pod set, so callers never need to know which specific Pod is handling traffic at any moment.
- **When do ClusterIP, NodePort, and LoadBalancer diverge?**
  - ClusterIP is for intra-cluster-only access; NodePort opens a specific port on every node for external reach; LoadBalancer integrates with a cloud LB for public traffic. The deciding question is *where the traffic originates*.
- **Why must selector and labels match exactly?**
  - A Service finds Pods via its selector and bundles the results into Endpoints for routing. A single-character mismatch empties the Endpoints, creating a black hole where traffic reaches nothing—hence the operational habit of checking `kubectl get endpoints`.

<!-- toc:begin -->
## In this series

- [Kubernetes 101 (1/10): What is Kubernetes?](./01-what-is-kubernetes.md)
- [Kubernetes 101 (2/10): Pod](./02-pod.md)
- [Kubernetes 101 (3/10): Deployment](./03-deployment.md)
- **Service (current)**
- Ingress (upcoming)
- ConfigMap and Secret (upcoming)
- Volume (upcoming)
- HPA (upcoming)
- Helm (upcoming)
- Kubernetes in Operation (upcoming)

<!-- toc:end -->

## References

- [Service (Kubernetes)](https://kubernetes.io/docs/concepts/services-networking/service/)
- [DNS for Services and Pods](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/)
- [Service types](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types)
- [Headless Services](https://kubernetes.io/docs/concepts/services-networking/service/#headless-services)
- [Debug Services](https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/)

Tags: Kubernetes, Service, Networking, DNS, DevOps
