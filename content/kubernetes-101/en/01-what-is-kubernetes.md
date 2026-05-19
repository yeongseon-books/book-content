---
series: kubernetes-101
episode: 1
title: What is Kubernetes?
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

# What is Kubernetes?

A few `docker run` commands feel manageable when the system is small. The moment the service grows into dozens of containers across several nodes, that confidence usually breaks first. Someone has to decide placement, recover failures, and keep versions aligned while the system keeps moving.

This is the first post in the Kubernetes 101 series.

Here, we will frame Kubernetes as an orchestrator that continuously pushes the cluster toward the state you declared, not as a command launcher that starts containers one by one.

> Kubernetes is most useful when you stop thinking in terms of “start this container now” and start thinking in terms of “keep the cluster in this desired state over time.”

## Questions this chapter answers

- The meaning of *orchestration*
- *Control plane* vs *worker nodes*
- The *desired state* model
- Where *kubectl* fits
- *When* to adopt it

## Why It Matters

A handful of containers fits on *Compose*. From *dozens* upward, an *orchestrator* is a *survival requirement*.

## Concept at a Glance

![Concept at a Glance](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/01/01-01-concept-at-a-glance.en.png)
*This control-flow view shows how `kubectl` talks to the API server and lets the control plane drive scheduling toward the desired state.*


## Key Terms

- **cluster**: a *control plane + worker nodes* bundle.
- **control plane**: *api-server, etcd, scheduler, controller-manager*.
- **node**: a machine where *containers actually run*.
- **desired state**: the *target state* declared in *YAML*.
- **kubectl**: the *CLI* that talks to the cluster.

## Before / After

**Before**: each server runs *manual docker run* — *not reproducible*.

**After**: one *YAML* yields the same result *anywhere*.

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

### Step 2 — List nodes

```python
def get_nodes():
    res = subprocess.run(
        ["kubectl", "get", "nodes", "-o", "wide"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

### Step 3 — List namespaces

```python
def list_namespaces():
    res = subprocess.run(
        ["kubectl", "get", "ns"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

### Step 4 — System pods

```python
def system_pods():
    res = subprocess.run(
        ["kubectl", "-n", "kube-system", "get", "pods"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

### Step 5 — Cluster health

```python
def cluster_info():
    res = subprocess.run(
        ["kubectl", "cluster-info"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

## Verification workflow

```bash
kubectl config current-context
kubectl get nodes -o wide
kubectl cluster-info
```

**Expected output:** you should first see the active context name, then at least one `Ready` node, and finally a reachable API server endpoint. This is the fastest way to confirm that the cluster model in the article matches a live control plane you can actually talk to.

**Failure modes to check first:**

- If `current-context` is wrong, stop before deeper debugging because the rest of the commands are reading the wrong cluster.
- If `get nodes` times out, check API reachability and credentials before assuming a Kubernetes concept issue.
- If `cluster-info` works but nodes are `NotReady`, the problem is cluster health, not your mental model of orchestration.

## What to Notice in This Code

- *kubectl* talks only to the *api-server*.
- You *never touch etcd directly*.
- *Namespaces* are the *default isolation unit*.

## Five Common Mistakes

1. **Treating *Kubernetes* as a synonym for *containers*.**
2. **Believing more *nodes* alone *solve* problems.**
3. **Trying to *manage etcd directly*.**
4. **Mixing up *kubectl* contexts and applying to *production*.**
5. **Adopting Kubernetes for *tiny* workloads.**

## How This Shows Up in Production

*EKS / GKE / AKS* — *managed Kubernetes* — operates the *control plane for you*, leaving the team to focus on *workload YAML*.

## How a Senior Engineer Thinks

- *Desired state* is the *philosophy*.
- *Control plane* is the *brain*, *nodes* are the *limbs*.
- *Kubernetes* is *overkill* for tiny teams.
- *Managed* is the default choice.
- *kubectl* is a *thin client*.

## Checklist

- [ ] Switch *contexts explicitly*.
- [ ] Split into *namespaces*.
- [ ] Keep *desired state* in *YAML*.
- [ ] Prefer *managed* first.

## Practice Problems

1. Describe the *role of the control plane* in one line.
2. Explain in one line *why desired state matters*.
3. Name *one situation* where you should delay Kubernetes.

## Wrap-up and Next Steps

The *big picture* of orchestration is in place. The next post covers the *smallest unit*: the *Pod*.

<!-- toc:begin -->
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
