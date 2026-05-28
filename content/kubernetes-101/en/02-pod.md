---
series: kubernetes-101
episode: 2
title: "Kubernetes 101 (2/10): Pod"
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
  - Pod
  - Containers
  - YAML
  - DevOps
seo_description: A beginner guide to Kubernetes Pods — what they are, how they relate to containers, the sidecar pattern, and the pod lifecycle in YAML
last_reviewed: '2026-05-15'
---

# Kubernetes 101 (2/10): Pod

The first thing that confuses many Docker users is that Kubernetes does not treat the container itself as the base unit. That design choice looks odd until you hit the real operational problems: shared networking, helper processes, startup ordering, and the fact that several containers sometimes have to live and die together.

This is the 2nd post in the Kubernetes 101 series.

Here, we will define a Pod as the smallest deployable execution bundle in Kubernetes and connect that idea to sidecars, shared storage, and the Pod lifecycle you debug in production.

> A Pod is not a prettier name for one container. It is the boundary Kubernetes uses when scheduling, networking, and replacing a unit of work.


![kubernetes 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/02/02-01-concept-at-a-glance.en.png)
*kubernetes 101 chapter 2 flow overview*

## Questions to Keep in Mind

- The definition of a *Pod?
- How it differs from a *container?
- The *sidecar* pattern?

## Why It Matters

*Every workload* eventually runs *on a Pod*. You must understand the *Pod model* before higher-level objects make sense.

## Key Terms

- **pod**: a *shared bundle* of *one or more containers*.
- **sidecar**: a helper container *next to* the main one.
- **init container**: a container that runs *once before start*.
- **lifecycle**: *Pending → Running → Succeeded/Failed*.
- **ephemeral**: a Pod *does not come back* after it dies.

## Before / After

**Before**: lone *containers* struggle to share resources.

**After**: a *Pod* shares *network and volumes* naturally.

## Hands-on: Work with Pod YAML

### Step 1 — Pod manifest

```python
"""
apiVersion: v1
kind: Pod
metadata:
  name: web
spec:
  containers:
  - name: app
    image: nginx:1.25
    ports: [{containerPort: 80}]
"""
```

### Step 2 — Apply

```python
import subprocess

def apply(path):
    subprocess.run(["kubectl", "apply", "-f", path], check=True)
```

### Step 3 — Describe

```python
def describe(name):
    res = subprocess.run(
        ["kubectl", "describe", "pod", name],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

### Step 4 — Logs

```python
def logs(name):
    res = subprocess.run(
        ["kubectl", "logs", name],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

### Step 5 — Delete

```python
def delete(name):
    subprocess.run(["kubectl", "delete", "pod", name], check=True)
```

## Verification workflow

```bash
kubectl get pod web -o wide
kubectl describe pod web
kubectl logs web
```

**Expected output:** `get pod` should show a Pod that is `Running` or still becoming ready, `describe` should list scheduling and container-start events in order, and `logs` should surface the first app messages from standard output. Together they show state, reason, and app-level evidence instead of only a green/red summary.

**Failure modes to check first:**

- A long `Pending` state usually means scheduling or resource issues before it means application failure.
- `ImagePullBackOff` points to image tag or registry access before it points to Pod YAML shape.
- Empty logs often mean the process exited immediately or the app is still writing only to files inside the container.

## What to Notice in This Code

- The *Pod name* must be *unique*.
- *containers* is an *array* — more than one is allowed.
- Creating a *bare Pod* is *for learning only*.

## Five Common Mistakes

1. **Assuming *Pod = one container*.**
2. **Creating a *bare Pod* and expecting *restarts*.**
3. **Assuming the *IP is stable*.**
4. **Losing *shared-volume* gains by splitting containers.**
5. **Reading *logs* only from inside the container.**

## How This Shows Up in Production

*Sidecars* such as *log collectors*, *Envoy proxies*, and *secret syncers* sit *next to* the main container.

## How a Senior Engineer Thinks

- *Pods are ephemeral.* Do not resurrect them.
- *Restarts* are the job of *higher objects*.
- *Sidecars* are both a *coupling tool* and a *coupling cost*.
- *Pod IPs* are *temporary*.
- Outside of learning, do not create *bare Pods*.

## Checklist

- [ ] Bare-Pod creation only for *debugging*.
- [ ] *Sidecar* role clearly defined.
- [ ] *Logs* go to *stdout*.
- [ ] *Pod lifecycle* monitored.

## Practice Problems

1. State the *difference* between Pod and container in one line.
2. Name a *real example* of a sidecar.
3. Explain in one line *why* you should not create bare Pods.

## Wrap-up and Next Steps

With *Pods* understood, the next step is the *Deployment*, which owns *restarts and rolling updates*.

## Answering the Opening Questions

- **Pod vs container — how do they differ?**
  - A container is an isolated process, while a Pod is a group of one or more containers sharing the same network namespace and volumes, starting and stopping together. The YAML spec where `containers` is an array illustrates this directly.
- **Why does Kubernetes use Pods instead of bare containers?**
  - Log collectors, proxies, and secret-sync agents need the same lifecycle as the main process. Without a Pod boundary, you'd have to manually design the coupling and shared resources every time.
- **When is the sidecar pattern needed?**
  - When an auxiliary role (log collection, proxy, file sync) must start and stop at the same moment as the main container. The article also noted the coupling cost: putting both in one Pod ties their deploy and scaling unit together.

<!-- toc:begin -->
## In this series

- [Kubernetes 101 (1/10): What is Kubernetes?](./01-what-is-kubernetes.md)
- **Pod (current)**
- Deployment (upcoming)
- Service (upcoming)
- Ingress (upcoming)
- ConfigMap and Secret (upcoming)
- Volume (upcoming)
- HPA (upcoming)
- Helm (upcoming)
- Kubernetes in Operation (upcoming)

<!-- toc:end -->

## References

- [Pods (Kubernetes)](https://kubernetes.io/docs/concepts/workloads/pods/)
- [Pod lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [Init containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/)
- [Sidecar containers](https://kubernetes.io/blog/2023/08/25/native-sidecar-containers/)
- [Debug Pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/)

Tags: Kubernetes, Pod, Containers, YAML, DevOps
