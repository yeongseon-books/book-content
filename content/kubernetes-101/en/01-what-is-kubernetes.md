---
series: kubernetes-101
episode: 1
title: "Kubernetes 101 (1/10): What is Kubernetes?"
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
  - Orchestration
  - Containers
  - DevOps
  - SRE
seo_description: A beginner-friendly overview of Kubernetes — container orchestration, control plane vs worker nodes, and the desired state model
last_reviewed: '2026-05-15'
---

# Kubernetes 101 (1/10): What is Kubernetes?

A few `docker run` commands feel manageable when the system is small. The moment the service grows into dozens of containers across several nodes, that confidence usually breaks first. Someone has to decide placement, recover failures, and keep versions aligned while the system keeps moving.

This is the first post in the Kubernetes 101 series.

Here, we will frame Kubernetes as an orchestrator that continuously pushes the cluster toward the state you declared, not as a command launcher that starts containers one by one.

> Kubernetes is most useful when you stop thinking in terms of "start this container now" and start thinking in terms of "keep the cluster in this desired state over time."


![kubernetes 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/01/01-01-concept-at-a-glance.en.png)
*kubernetes 101 chapter 1 flow overview*

## Questions to Keep in Mind

- What does orchestration actually replace in day-to-day operations?
- How do the control plane and worker nodes divide responsibility?
- Why is the desired state model the core philosophy of Kubernetes?

## Why It Matters

A handful of containers fits on Compose. Once you pass dozens, an orchestrator becomes a survival requirement—not because of scale alone, but because the coordination decisions (placement, restart, version swap, resource limits) exceed what a human can reliably track by hand.

Many beginners treat Kubernetes as "a container platform," but it is closer to a system that converts human operational decisions into declarative rules. Grasping this perspective first makes Pod, Deployment, and Service feel like natural extensions rather than isolated features.

## Key Terms

- **cluster**: The complete execution environment—a control plane plus worker nodes.
- **control plane**: API server, etcd, scheduler, controller-manager—the components that make placement and convergence decisions.
- **node**: A machine (physical or virtual) where containers actually run.
- **desired state**: The target state declared in YAML that controllers work to maintain.
- **kubectl**: The CLI that communicates with the cluster API server.

## Before / After

**Before**: each server runs manual `docker run` commands. Dead containers require human intervention. Reproducing the same setup on another server is error-prone.

**After**: one YAML declaration yields the same result anywhere. The system continuously reconciles current state toward the declared target, providing self-healing and reproducibility as default behaviors.

## Hands-on: Tour Your First Cluster

### Step 1 — Show context

```python
import subprocess

def current_context():
    res = subprocess.run(
        ["kubectl", "config", "current-context"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout.strip()
```

The first thing to check is your current context. `kubectl` is not a single-cluster tool—confirming which cluster you are talking to prevents accidental changes to production.

### Step 2 — List nodes

```python
def get_nodes():
    res = subprocess.run(
        ["kubectl", "get", "nodes", "-o", "wide"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

The node list shows what execution resources the cluster actually has. Even though Kubernetes feels like a logical control system, workloads ultimately run on worker nodes.

### Step 3 — List namespaces

```python
def list_namespaces():
    res = subprocess.run(
        ["kubectl", "get", "ns"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

Namespaces are the most basic isolation unit in Kubernetes. Instead of dumping everything into one bucket, you separate workloads by environment or team from the start.

### Step 4 — System pods

```python
def system_pods():
    res = subprocess.run(
        ["kubectl", "-n", "kube-system", "get", "pods"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

Looking at `kube-system` reveals what the cluster runs to operate itself. Kubernetes is not a single binary—it is a system of cooperating components.

### Step 5 — Cluster health

```python
def cluster_info():
    res = subprocess.run(
        ["kubectl", "cluster-info"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

`cluster-info` is a quick reachability check. In production, it is often the first command when investigating API server connectivity issues.

## Verification workflow

```bash
kubectl config current-context
kubectl get nodes -o wide
kubectl cluster-info
```

**Expected output:** you should first see the active context name, then at least one `Ready` node, and finally a reachable API server endpoint.

**Failure modes to check first:**

- If `current-context` is wrong, stop—the rest of your commands are reading the wrong cluster.
- If `get nodes` times out, check API reachability and credentials before assuming a Kubernetes concept issue.
- If `cluster-info` works but nodes are `NotReady`, the problem is cluster health, not your mental model.

## Manifest-Based Operations

Kubernetes's strength lies in declarative manifests, not imperative commands. The example below separates Deployment, Service, and Ingress to keep responsibility boundaries clear.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  labels:
    app: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: ghcr.io/example/api:1.2.0
          ports:
            - containerPort: 8000
          readinessProbe:
            httpGet:
              path: /healthz
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
          resources:
            requests:
              cpu: "200m"
              memory: "256Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: api
spec:
  selector:
    app: api
  ports:
    - port: 80
      targetPort: 8000
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api
spec:
  ingressClassName: nginx
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: api
                port:
                  number: 80
```

Defining readiness probes and resource requests/limits together prevents the "deployed but crashes under traffic" failure mode. Embedding operational stability in the declarative file matters more than adding it after the fact.

## kubectl Operational Commands

After applying manifests, cycle through status observation commands quickly. This set covers the most common failure analysis needs:

```bash
kubectl apply -f k8s/
kubectl get deploy,rs,pod -n prod -o wide
kubectl rollout status deploy/api -n prod
kubectl describe pod -n prod -l app=api
kubectl logs -n prod deploy/api --tail=200
kubectl get events -n prod --sort-by=.metadata.creationTimestamp
```

Checking `rollout status` and `describe` first lets you distinguish image pull failures, probe failures, and scheduling failures quickly. Looking at logs alone often misattributes infrastructure problems as application bugs.

## Architecture Boundaries

- **API Server boundary**: All declarative changes flow through the API server. SSH-ing into a node and fixing state by hand creates drift.
- **Scheduler boundary**: Pod placement is the result of resource requests, taints/tolerations, and affinity rules. Separate node-selection issues from application bugs.
- **Controller boundary**: The Deployment Controller handles replica convergence and rolling updates. Watch the desired/current gap as a habit.
- **Network boundary**: Service (L4) and Ingress (L7) have different responsibilities. Separating internal routing failures from external ingress failures speeds diagnosis.

Decomposing failures along these boundaries replaces the vague "cluster problem" conclusion with a precise "which layer broke which signal" record.

## Deployment Stability Checklist

1. Set readiness/liveness probes on every workload.
2. Use pinned version tags instead of `latest` to preserve rollback targets.
3. Run `kubectl diff -f` before every apply to catch unintended field deletions.
4. Apply ResourceQuota and LimitRange in production namespaces to limit blast radius.
5. Check `kubectl rollout history` after deploy to document the recovery path.

## Troubleshooting Workflow: Decompose Signals by Layer

The most common production question—"the service is slow"—is dangerously vague. Decompose it by layer before jumping to application code:

1. **Ingress layer**: Ingress Controller logs, 4xx/5xx ratio.
2. **Service layer**: Are healthy Pods listed in Endpoints?
3. **Workload layer**: Pod restart count, probe failures, OOMKilled.
4. **Cluster layer**: Node pressure (memory/disk), evictions.

```bash
kubectl get endpoints api -n prod -o yaml
kubectl describe deploy api -n prod
kubectl get pod -n prod -l app=api -o wide
kubectl top pod -n prod
kubectl top node
```

Document this order in your runbook. On-call handoff quality improves dramatically when the diagnostic sequence is fixed rather than ad-hoc.

## What to Notice in This Code

- `kubectl` talks only to the API server—it never directly starts containers.
- You never touch etcd directly in normal operations.
- Namespaces are the default isolation unit—build this habit early.

These three points prevent the misconception that Kubernetes is "a tool where you issue a command and a container starts immediately." What you do is declare; what adjusts is the control plane.

## Five Common Mistakes

1. **Treating Kubernetes as a synonym for containers.** It is an orchestrator, not a runtime.
2. **Believing more nodes alone solve problems.** Node count without proper resource requests just spreads chaos wider.
3. **Trying to manage etcd directly.** Treat it as an internal implementation detail.
4. **Mixing up kubectl contexts.** One wrong context and you apply to production by accident.
5. **Adopting Kubernetes for tiny workloads.** If Compose handles it, Kubernetes adds complexity without proportional benefit.

## How This Shows Up in Production

Most teams choose managed Kubernetes (EKS, GKE, AKS) as the default because they want to operate applications, not control planes. Senior engineers look at Kubernetes through the lens of its mental model first: Is it a desired-state declaration tool? Is it a control system that converges toward that state? How much of the control loop does the team need to own directly?

This perspective makes Deployment and HPA feel like natural extensions of the same idea rather than separate features to memorize.

## How a Senior Engineer Thinks

- Desired state is the philosophy—everything else follows.
- Control plane is the brain, nodes are the limbs.
- Kubernetes is overkill for tiny teams with simple workloads.
- Managed is the default choice unless you have a specific reason to self-host.
- `kubectl` is a thin client—the real work happens in controllers.

## Checklist

- [ ] Verified the current context before applying any change.
- [ ] Planned namespace separation for workloads.
- [ ] Committed desired state as YAML in version control.
- [ ] Evaluated managed Kubernetes before considering self-hosted.

## Practice Problems

1. Describe the role of the control plane in one line.
2. Explain in one line why the desired state model matters.
3. Name one situation where you should delay adopting Kubernetes.

## Wrap-up and Next Steps

The big picture of orchestration is in place: Kubernetes is a desired-state reconciliation system, not a container launcher. The control plane decides, worker nodes execute, and `kubectl` is just the thin client that submits declarations.

The next post covers the smallest deployable unit: the Pod. Most Kubernetes abstractions are built around it.

## Answering the Opening Questions

- **What does orchestration actually replace?**
  - It replaces the manual cycle of running `docker run` on each server, restarting dead containers by hand, and coordinating version swaps across hosts. These placement/restart/upgrade decisions move into system-level rules expressed as YAML.
- **How do the control plane and worker nodes divide responsibility?**
  - The control plane (API server, etcd, scheduler, controller-manager) decides where and what to run. Worker nodes execute those decisions by actually running containers. `kubectl` never launches a container directly—it only tells the API server the desired state.
- **Why is the desired state model the core philosophy?**
  - Users declare a goal state and controllers continuously converge current state toward it. This makes self-healing and reproducibility default behaviors rather than bolt-on features. Watching the desired-vs-current gap becomes the starting point of all operations.

<!-- toc:begin -->
## In this series

- **What is Kubernetes? (current)**
- Pod (upcoming)
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

- [Kubernetes Overview](https://kubernetes.io/docs/concepts/overview/)
- [Kubernetes components](https://kubernetes.io/docs/concepts/overview/components/)
- [kubectl reference](https://kubernetes.io/docs/reference/kubectl/)
- [CNCF landscape](https://landscape.cncf.io/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)

Tags: Kubernetes, Orchestration, Containers, DevOps, SRE
