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

- How exactly does a Pod differ from a container?
- Why does Kubernetes use Pods rather than bare containers as the base unit?
- When is the sidecar pattern needed, and what is the coupling cost?

## Why It Matters

Every workload eventually runs on a Pod. Higher-level objects (Deployment, Job, DaemonSet) all manage Pods underneath. Understanding the Pod model—shared networking, volume mounts, lifecycle phases—is prerequisite knowledge for everything that follows.

## Key Terms

- **pod**: A shared bundle of one or more containers that share a network namespace and storage volumes.
- **sidecar**: A helper container placed next to the main container inside the same Pod.
- **init container**: A container that runs once to completion before the main containers start.
- **lifecycle**: The sequence Pending → Running → Succeeded/Failed that every Pod traverses.
- **ephemeral**: A Pod does not come back after it dies. Resurrection is the job of a controller.

## Before / After

**Before**: Lone containers cannot easily share localhost networking or storage without manual orchestration.

**After**: A Pod shares network and volumes naturally. Containers inside the same Pod talk over `localhost` and mount the same volumes without extra configuration.

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

**Expected output:** `get pod` should show a Pod that is `Running` or still becoming ready, `describe` should list scheduling and container-start events in order, and `logs` should surface the first app messages from standard output.

**Failure modes to check first:**

- A long `Pending` state usually means scheduling or resource issues before it means application failure.
- `ImagePullBackOff` points to image tag or registry access before it points to Pod YAML shape.
- Empty logs often mean the process exited immediately or the app is still writing only to files inside the container.

## Reading a Pod Spec from an Operational Perspective

A Pod is not just an execution unit—it is an operational contract. The fields `securityContext`, `resources`, `probe`, and `terminationGracePeriodSeconds` determine how the Pod behaves under failure. Making failure predictable matters more than making deployment fast.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: api-pod
  labels:
    app: api
spec:
  terminationGracePeriodSeconds: 30
  containers:
    - name: api
      image: ghcr.io/example/api:1.3.1
      ports:
        - containerPort: 8000
      resources:
        requests:
          cpu: "200m"
          memory: "256Mi"
        limits:
          cpu: "500m"
          memory: "512Mi"
      livenessProbe:
        httpGet:
          path: /livez
          port: 8000
      readinessProbe:
        httpGet:
          path: /readyz
          port: 8000
```

Key fields to always specify: `resources` (scheduling promise and burst ceiling), both probes (traffic routing and restart trigger), and `terminationGracePeriodSeconds` (graceful shutdown window during rolling updates).

## Debugging Workflow: Pending, CrashLoopBackOff, OOMKilled

Pod failures are diagnosable from the status string alone as a first pass:

| Status | First Thing to Check | Typical Root Cause |
| --- | --- | --- |
| Pending | Scheduling constraints | Insufficient node resources, taint mismatch, unbound PVC |
| CrashLoopBackOff | Start command and dependencies | Missing env var, bad entrypoint, dependency not ready |
| OOMKilled | Memory limit | Limit set too low, memory leak, large batch load |

```bash
kubectl get pod api-pod -n prod -o wide
kubectl describe pod api-pod -n prod
kubectl logs api-pod -n prod --previous
kubectl top pod api-pod -n prod
```

The Events section in `describe` separates causes quickly: image pull failure, node resource pressure, or probe failure. Read events before reading logs—infrastructure causes masquerading as app bugs waste hours.

## Pod-Level Operational Rules

1. Never use a bare Pod as a long-running production unit. Wrap it in a Deployment or StatefulSet so a controller handles restarts and rollouts.
2. Ban the `latest` tag. Pin image versions so rollback has a concrete target.
3. Set `terminationGracePeriodSeconds` and a preStop hook to avoid connection drops during rolling updates.
4. Treat `kubectl exec` as a temporary diagnostic tool. Fix the root cause in the manifest, not inside the running container.

Designing Pods well up front dramatically reduces the cost of adding Deployment, HPA, and PodDisruptionBudget later.

## What to Notice in This Code

- The Pod name must be unique within a namespace.
- `containers` is an array—more than one is allowed, which is the whole point of the Pod abstraction.
- Creating a bare Pod is for learning and debugging only. Production workloads belong behind a controller.

## Five Common Mistakes

1. **Assuming Pod = one container.** It is a multi-container boundary by design.
2. **Creating a bare Pod and expecting automatic restarts.** Without a controller, a dead Pod stays dead.
3. **Assuming the Pod IP is stable.** It changes on every reschedule. Use a Service for stable addressing.
4. **Splitting containers that need shared resources.** You lose localhost networking and volume sharing.
5. **Reading logs only from files inside the container.** Standard output is the Kubernetes-native log path.

## How This Shows Up in Production

Sidecars such as log collectors (Fluent Bit), Envoy proxies, and secret syncers (Vault Agent) sit next to the main container in the same Pod. The Pod is the coupling boundary that determines what shares a lifecycle.

Senior engineers ask "what must live and die together?" first. They also recognize that sidecars are both a convenience and a coupling cost—putting too much into one Pod ties deployment and scaling units together unnecessarily.

## How a Senior Engineer Thinks

- Pods are ephemeral. Never try to resurrect a specific Pod instance.
- Restarts and replica count are the job of higher-level controllers, not the Pod itself.
- Sidecars are powerful but carry coupling cost—every container in a Pod scales and deploys together.
- Pod IPs are temporary. Always front Pods with a Service.
- Outside of learning exercises, never create bare Pods for production traffic.

## Checklist

- [ ] Bare-Pod creation limited to debugging and learning scenarios only.
- [ ] Sidecar containers have a clearly documented role and lifecycle justification.
- [ ] Application logs go to stdout/stderr (not internal files).
- [ ] Both liveness and readiness probes are defined with appropriate paths.
- [ ] Resource requests and limits are specified for every container.

## Practice Problems

1. State the difference between a Pod and a container in one sentence.
2. Name a real-world sidecar example and explain why it must share a Pod with the main container.
3. Explain in one line why bare Pods should not be used as a production default.

## Wrap-up and Next Steps

A Pod is the smallest deployable unit in Kubernetes—a bundle where containers share network and storage and live the same lifecycle. Understanding it at the operational level (probes, resources, debugging states) makes everything built on top of it predictable.

The next post covers the Deployment, which owns restart logic, replica count, and rolling updates—the controller that makes Pods production-ready.

## Answering the Opening Questions

- **How exactly does a Pod differ from a container?**
  - A container is an isolated process. A Pod is a group of one or more containers sharing the same network namespace and volumes, starting and stopping together. The YAML spec where `containers` is defined as an array illustrates this directly.
- **Why does Kubernetes use Pods instead of bare containers?**
  - Because auxiliary processes (log collectors, proxies, secret syncers) need the same lifecycle as the main process. Without the Pod boundary, you would have to manually design coupling and shared resources every time.
- **When is the sidecar pattern needed, and what is the coupling cost?**
  - When an auxiliary role must start and stop at the same moment as the main container. The cost: every container in the Pod shares the same deploy and scaling unit, so an update to the sidecar forces a rollout of the entire Pod.

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
