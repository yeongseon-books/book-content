---
series: kubernetes-101
episode: 8
title: HPA
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Kubernetes
  - HPA
  - Autoscaling
  - Metrics
  - DevOps
seo_description: A beginner tour of Kubernetes HPA covering CPU and memory targets, metrics-server, custom metrics, and pairing with Cluster Autoscaler.
last_reviewed: '2026-05-04'
---

# HPA

> Kubernetes 101 series (8/10)

<!-- a-grade-intro:begin -->

**Core question**: should a *human* resize *Pod count* every time *traffic* shifts?

> *HorizontalPodAutoscaler* watches *metrics* and scales *Pods* in and out *automatically*.

<!-- a-grade-intro:end -->

This is post 8 in the Kubernetes 101 series.

## What You Will Learn

- where *HPA* fits
- why *metrics-server* matters
- *CPU/memory* targets
- *custom metrics*
- relationship with *VPA / Cluster Autoscaler*

## Why It Matters

*Manual scaling* causes *lag* and *over-provisioning*. *Autoscaling* protects both *cost* and *availability*.

## Concept at a Glance

```mermaid
flowchart LR
    Metrics["metrics-server"] --> HPA["hpa"]
    HPA --> Dep["deployment"]
    Dep --> Pods["pods"]
```

## Key Terms

- **HPA**: scales *Pod count* *automatically*.
- **metrics-server**: collector for *built-in metrics*.
- **target utilization**: target *CPU/Mem ratio*.
- **custom metric**: *external signals* like *queue length*.
- **VPA**: tunes *Pod-level resources* instead of count.

## Before/After

**Before**: *waste* at *night*, *503s* at *peak*.

**After**: *HPA* sizes *Pods* to current *demand*.

## Hands-on: CPU-based HPA

### Step 1 — Resource requests on the Deployment

```python
"""
spec:
  template:
    spec:
      containers:
      - name: app
        image: myorg/app:1.0
        resources:
          requests: {cpu: 200m, memory: 256Mi}
"""
```

### Step 2 — HPA manifest

```python
"""
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata: {name: web}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target: {type: Utilization, averageUtilization: 60}
"""
```

### Step 3 — apply

```python
import subprocess

def apply(path):
    subprocess.run(["kubectl", "apply", "-f", path], check=True)
```

### Step 4 — generate load

```python
def load(target):
    subprocess.run([
        "kubectl", "run", "load", "--rm", "-i", "--restart=Never",
        "--image=busybox", "--", "sh", "-c",
        f"while true; do wget -q -O- {target}; done",
    ], check=False)
```

### Step 5 — inspect HPA state

```python
def hpa_status(name):
    res = subprocess.run(
        ["kubectl", "get", "hpa", name, "-o", "wide"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

## What to Notice in This Code

- *HPA* does *nothing* without *resource requests*.
- *minReplicas >= 2* is the start of *high availability*.
- *averageUtilization* is a ratio against *requests*.

## Five Common Mistakes

1. **Missing *requests*, so metrics show *0%*.**
2. ***maxReplicas* too low to absorb the *peak*.**
3. **Jumping straight to *custom metrics*.**
4. **Ignoring *node limits* so scaling *cannot proceed*.**
5. **Skipping *cooldowns* and getting *flapping*.**

## How This Shows Up in Production

The common pairing is *HPA + Cluster Autoscaler* so that *Pod growth* drives *node growth* in two coordinated layers.

## How a Senior Engineer Thinks

- *Requests* are the *foundation* of all autoscaling.
- *Metric trust* equals *autoscaler trust*.
- *Custom metrics* come *after measurement*.
- *Flapping* shows up as *cost*.
- Always pair with *node-level automation*.

## Checklist

- [ ] *Requests* set.
- [ ] *minReplicas >= 2*.
- [ ] *Cluster Autoscaler* considered.
- [ ] *Flapping* monitored.

## Practice Problems

1. In one line, why does *HPA* fail without *requests*?
2. In one line, the *difference* between *VPA* and *HPA*.
3. In one line, the *role* of *Cluster Autoscaler*.

## Wrap-up and Next Steps

With autoscaling in place, you need a *repeatable deploy unit*. The next post is *Helm*.

<!-- toc:begin -->
- [What is Kubernetes?](./01-what-is-kubernetes.md)
- [Pod](./02-pod.md)
- [Deployment](./03-deployment.md)
- [Service](./04-service.md)
- [Ingress](./05-ingress.md)
- [ConfigMap and Secret](./06-configmap-and-secret.md)
- [Volume](./07-volume.md)
- **HPA (current)**
- Helm (upcoming)
- Kubernetes in Operation (upcoming)
<!-- toc:end -->

## References

- [HorizontalPodAutoscaler](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [metrics-server](https://github.com/kubernetes-sigs/metrics-server)
- [Cluster Autoscaler](https://github.com/kubernetes/autoscaler/tree/master/cluster-autoscaler)
- [VPA](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler)

Tags: Kubernetes, HPA, Autoscaling, Metrics, DevOps
