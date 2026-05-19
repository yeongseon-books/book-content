---
series: kubernetes-101
episode: 10
title: Kubernetes in Operation
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
  - SRE
  - Observability
  - GitOps
  - DevOps
seo_description: A beginner-friendly tour of operating Kubernetes covering probes, RBAC, network policies, observability, capacity planning, GitOps, and runbooks.
last_reviewed: '2026-05-15'
---

# Kubernetes in Operation

A running cluster is not the same thing as an operable one. You can have healthy-looking Pods and still lack safe traffic gates, clear permissions, useful telemetry, and a repeatable incident path when something breaks at night.

This is the final post in the Kubernetes 101 series.

Here, we will connect probes, RBAC, network boundaries, observability, GitOps, and runbooks into one operating model instead of treating them as unrelated checkboxes.

> Kubernetes operations become reliable only when traffic rules, permissions, telemetry, and change procedures reinforce each other.

## Questions this chapter answers

- *liveness/readiness/startup* probes
- *RBAC* and *NetworkPolicy*
- *metrics/logs/traces*
- *capacity planning* and *GitOps*
- the shape of a *runbook*

## Why It Matters

*Functionally working* and *staying up overnight without issues* are different. *Operability* is *service trust*.

## Concept at a Glance

![Concept at a Glance](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/10/10-01-concept-at-a-glance.en.png)
*Operations become repeatable only when probes, telemetry, runbooks, and GitOps all feed the same response system.*


## Key Terms

- **liveness probe**: signals when to *restart*.
- **readiness probe**: signals when to *receive traffic*.
- **RBAC**: *role-based access control*.
- **NetworkPolicy**: limits *Pod-to-Pod* communication.
- **GitOps**: *declarative ops* with *Git* as the *source of truth*.

## Before/After

**Before**: *manual kubectl*, *log grepping*, *guess-driven debugging*.

**After**: *probes* + *dashboards* + *runbooks* enable *repeatable response*.

## Hands-on: Operations Basics

### Step 1 — Add probes

```python
"""
livenessProbe:
  httpGet: {path: /healthz, port: 8080}
readinessProbe:
  httpGet: {path: /ready, port: 8080}
"""
```

### Step 2 — RBAC

```python
"""
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata: {name: reader, namespace: web}
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list"]
"""
```

### Step 3 — NetworkPolicy

```python
"""
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: {name: web-only, namespace: web}
spec:
  podSelector: {matchLabels: {app: web}}
  ingress:
  - from:
    - podSelector: {matchLabels: {role: lb}}
"""
```

### Step 4 — Collect observability data

```python
import subprocess

def top_pods(ns):
    res = subprocess.run(
        ["kubectl", "top", "pods", "-n", ns],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

### Step 5 — Runbook snippet

```python
def runbook_step(name):
    return {
        "name": name,
        "preconditions": ["alert fired", "owner paged"],
        "actions": ["check probe", "rollout status", "rollback if needed"],
    }
```

## Verification workflow

```bash
kubectl describe pod web-xxxxx
kubectl auth can-i get pods --as system:serviceaccount:web:default -n web
kubectl get networkpolicy -n web
```

**Expected output:** `describe pod` should let you separate readiness failures from restart signals, `auth can-i` should confirm the service account permissions you intended, and the NetworkPolicy list should show that communication boundaries exist as declared objects rather than assumptions.

**Failure modes to check first:**

- A running Pod with failed readiness is an operations contract failure even when the process itself is alive.
- RBAC that looks correct in YAML may still fail if the actual service-account binding is missing.
- An empty NetworkPolicy list usually means the security problem is the absence of a boundary, not one broken rule.

## What to Notice in This Code

- When *readiness* is *0/1*, *traffic is blocked*.
- *RBAC* should start from *least privilege*.
- *NetworkPolicy* is safest with a *default deny*.

## Five Common Mistakes

1. **Setting *liveness* but skipping *readiness*.**
2. **Granting *all permissions* by *default*.**
3. **Skipping *NetworkPolicy*, allowing *lateral movement*.**
4. **Watching only *logs*, ignoring *metrics*.**
5. **Responding to incidents without a *runbook*.**

## How This Shows Up in Production

*GitOps* tools like *Argo CD* converge the *cluster* to the *Git* state, while *dashboards* and *runbooks* make *night-time response* feasible.

## How a Senior Engineer Thinks

- *Probes* are *contracts*.
- *Permissions* start *small*.
- *Observability* stands on *three legs* (metrics, logs, traces).
- When *Git* is the *source*, *drift disappears*.
- *Runbooks* improve through *training*.

## Checklist

- [ ] All three *probe* types reviewed.
- [ ] *RBAC* at *least privilege*.
- [ ] *NetworkPolicy* default *deny*.
- [ ] *Dashboards + alerts*.
- [ ] *Runbook* exists.

## Practice Problems

1. In one line, the *difference* between *liveness* and *readiness*.
2. In one line, the *core benefit* of *GitOps*.
3. In one line, the *effect* of a *default-deny NetworkPolicy*.

## Wrap-up and Next Steps

That wraps the *Kubernetes 101* series. Next, the *Serverless* and *SRE* series go deeper into *operability*.

<!-- toc:begin -->
- [What is Kubernetes?](./01-what-is-kubernetes.md)
- [Pod](./02-pod.md)
- [Deployment](./03-deployment.md)
- [Service](./04-service.md)
- [Ingress](./05-ingress.md)
- [ConfigMap and Secret](./06-configmap-and-secret.md)
- [Volume](./07-volume.md)
- [HPA](./08-hpa.md)
- [Helm](./09-helm.md)
- **Kubernetes in Operation (current)**
<!-- toc:end -->

## References

- [Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [NetworkPolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Argo CD](https://argo-cd.readthedocs.io/)
- [kubectl auth can-i](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_auth/kubectl_auth_can-i/)

Tags: Kubernetes, SRE, Observability, GitOps, DevOps
