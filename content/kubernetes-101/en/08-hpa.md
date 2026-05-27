---
series: kubernetes-101
episode: 8
title: "Kubernetes 101 (8/10): HPA"
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
  - HPA
  - Autoscaling
  - Metrics
  - DevOps
seo_description: A beginner tour of Kubernetes HPA covering CPU and memory targets, metrics-server, custom metrics, and pairing with Cluster Autoscaler.
last_reviewed: '2026-05-15'
---

# Kubernetes 101 (8/10): HPA

Traffic rarely stays flat. If humans resize replicas by hand, they react too late during spikes and waste money during quiet periods. Autoscaling helps, but only if the metrics and resource requests underneath it are trustworthy.

This is the 8th post in the Kubernetes 101 series.

Here, we will treat HPA as a control loop that adjusts Deployment replica count from metrics, then connect that loop to requests, metrics-server, and node-level capacity limits.

> HPA is only as good as the metrics it can trust and the cluster capacity that can satisfy the scaling decision.


![kubernetes 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/08/08-01-concept-at-a-glance.en.png)
*kubernetes 101 chapter 8 flow overview*

## Questions to Keep in Mind

- where *HPA* fits?
- why *metrics-server* matters?
- CPU/memory* targets?

## Why It Matters

*Manual scaling* causes *lag* and *over-provisioning*. *Autoscaling* protects both *cost* and *availability*.

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

## Verification workflow

```bash
kubectl top pods
kubectl get hpa web -w
kubectl describe hpa web
```

**Expected output:** `kubectl top pods` must return CPU and memory numbers, `get hpa -w` should show current/target metrics and replica changes under load, and `describe hpa` should reveal recent scaling events and controller conditions.

**Failure modes to check first:**

- If `top pods` fails, fix metrics-server before tuning the HPA manifest.
- If HPA wants more replicas but Pods do not appear, the bottleneck is often node capacity rather than HPA logic.
- If scaling thrashes, revisit requests sizing and traffic shape before only changing the target percentage.

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

## Answering the Opening Questions

- **where *HPA* fits?**
  - The article treats HPA as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **why *metrics-server* matters?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **CPU/memory* targets?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Kubernetes 101 (1/10): What is Kubernetes?](./01-what-is-kubernetes.md)
- [Kubernetes 101 (2/10): Pod](./02-pod.md)
- [Kubernetes 101 (3/10): Deployment](./03-deployment.md)
- [Kubernetes 101 (4/10): Service](./04-service.md)
- [Kubernetes 101 (5/10): Ingress](./05-ingress.md)
- [Kubernetes 101 (6/10): ConfigMap and Secret](./06-configmap-and-secret.md)
- [Kubernetes 101 (7/10): Volume](./07-volume.md)
- **HPA (current)**
- Helm (upcoming)
- Kubernetes in Operation (upcoming)

<!-- toc:end -->

## References

- [HorizontalPodAutoscaler](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [metrics-server](https://github.com/kubernetes-sigs/metrics-server)
- [Cluster Autoscaler](https://github.com/kubernetes/autoscaler/tree/master/cluster-autoscaler)
- [VPA](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler)
- [Horizontal Pod Autoscaler walkthrough](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/)

Tags: Kubernetes, HPA, Autoscaling, Metrics, DevOps
