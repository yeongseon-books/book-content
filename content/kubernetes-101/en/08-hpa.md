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

Manual scaling causes lag and over-provisioning. A human watching dashboards reacts in minutes, not seconds—and is absent on nights and weekends. Autoscaling closes that gap, but only when the inputs are trustworthy: resource requests define the denominator HPA uses to compute utilization, and cluster capacity determines whether new replicas can actually land. Without both, autoscaling is a promise the cluster cannot keep.

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

Resource requests are the foundation. HPA computes utilization as `current usage ÷ requests`. Without requests, the denominator is zero and utilization is incalculable—HPA will never fire. Set requests to reflect steady-state usage, not peak.

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

A 60% CPU target keeps headroom for traffic bursts before new replicas finish starting. `minReplicas: 2` ensures availability even during quiet periods. `maxReplicas` is your cost ceiling—set it based on cluster node capacity and budget, not infinity.

### Step 3 — apply

```python
import subprocess

def apply(path):
    subprocess.run(["kubectl", "apply", "-f", path], check=True)
```

The HPA object existing does not mean it is working. Metrics-server must be healthy and reporting actual CPU/memory numbers. If `kubectl top pods` returns an error, fix metrics-server before tuning HPA thresholds.

### Step 4 — generate load

```python
def load(target):
    subprocess.run([
        "kubectl", "run", "load", "--rm", "-i", "--restart=Never",
        "--image=busybox", "--", "sh", "-c",
        f"while true; do wget -q -O- {target}; done",
    ], check=False)
```

Synthetic load validates your thresholds in a safe environment. If HPA does not scale under artificial pressure, it will not scale under real traffic. Watch whether new replicas actually become Ready—if they stay Pending, the bottleneck is node capacity, not HPA configuration.

### Step 5 — inspect HPA state

```python
def hpa_status(name):
    res = subprocess.run(
        ["kubectl", "get", "hpa", name, "-o", "wide"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

The key columns in `get hpa -o wide` are TARGETS (current/target), MINPODS, MAXPODS, and REPLICAS. When current exceeds target but replicas stay flat, check events with `describe hpa` for capacity errors or stabilization-window cooldowns.

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

- **Why is manual Pod scaling slow and expensive?**
  - A human watching dashboards and running `kubectl scale` reacts in minutes, not seconds—and is absent on nights and weekends. The article showed how a 5-minute traffic spike degrades responses while no one is watching, or idle hours waste money on unnecessary replicas.
- **What metrics does HPA use for scale-out and scale-in?**
  - By default, CPU/memory utilization from metrics-server calculated as current usage ÷ requests. The article showed extending to RPS or queue length via `Resource`, `Pods`, `Object`, and `External` metric types. When the desired/current gap exceeds a threshold, replicas adjust; `behavior` settings add cooldown to prevent oscillation.
- **Why does HPA fail without resource requests?**
  - HPA computes utilization as "current usage ÷ requests." Without requests, the denominator is zero—target utilization becomes incalculable. Metrics show 0% or N/A, scaling never fires, and node resource reservation fails so scale-out itself breaks.

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
