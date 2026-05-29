---
series: kubernetes-101
episode: 10
title: "Kubernetes 101 (10/10): Kubernetes in Operation"
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

# Kubernetes 101 (10/10): Kubernetes in Operation

A running cluster is not the same thing as an operable one. You can have healthy-looking Pods and still lack safe traffic gates, clear permissions, useful telemetry, and a repeatable incident path when something breaks at night.

This is the final post in the Kubernetes 101 series.

Here, we will connect probes, RBAC, network boundaries, observability, GitOps, and runbooks into one operating model instead of treating them as unrelated checkboxes.

> Kubernetes operations become reliable only when traffic rules, permissions, telemetry, and change procedures reinforce each other.


![kubernetes 101 chapter 10 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/10/10-01-concept-at-a-glance.en.png)
*kubernetes 101 chapter 10 flow overview*

## Questions to Keep in Mind

- liveness/readiness/startup* probes?
- RBAC* and *NetworkPolicy?
- metrics/logs/traces?

## Why It Matters

Functionally working and staying up overnight without paging are different things. A deployment can pass all health checks and still lack the operational scaffolding to detect degradation, limit blast radius, and recover without guesswork. Operability means probes define traffic contracts, RBAC limits who can break what, network policies contain lateral movement, telemetry catches problems before users do, and runbooks turn incident response from heroics into procedure.

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

Liveness and readiness serve different contracts. Liveness failing triggers a restart—use it for deadlock detection, not slow queries. Readiness failing removes the Pod from Service endpoints—use it for warm-up and dependency checks. Mixing them causes either unnecessary restarts or premature traffic during boot.

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

Start with the narrowest permissions that let the workload function. A service account that can `get pods` and `pods/log` covers most debugging needs without granting destructive access. Widen only when a specific automation requires it, and audit bindings quarterly.

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

Without a NetworkPolicy, every Pod can reach every other Pod—convenient for development, dangerous in production. A compromised container gains free lateral movement across the entire namespace. Default-deny plus explicit allow-lists limits blast radius to the declared communication paths.

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

Metrics are the fastest signal ("something is wrong"), but logs and traces are needed for root cause ("this specific request failed at this span"). Collecting all three on the same timeline—correlated by trace ID—turns a vague "cluster is slow" into an actionable "Service X, endpoint Y, database call Z took 3s."

### Step 5 — Runbook snippet

```python
def runbook_step(name):
    return {
        "name": name,
        "preconditions": ["alert fired", "owner paged"],
        "actions": ["check probe", "rollout status", "rollback if needed"],
    }
```

A runbook standardizes incident response: what to check first, when to escalate, when to rollback. Without one, night-time responders improvise under pressure—increasing time-to-resolution and the chance of making things worse. Write the runbook before the first incident, then refine it after each postmortem.

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

## Answering the Opening Questions

- **Liveness, readiness, startup probe — how do they split responsibilities?**
  - Liveness asks "should this container be killed and restarted?"; readiness asks "can it receive traffic now?"; startup asks "has initial boot finished?" Using the same endpoint for all three causes slow-starting apps to be killed repeatedly or to receive traffic before warm-up completes.
- **Why are RBAC and NetworkPolicy fundamental operational boundaries?**
  - RBAC limits who can touch which API objects; NetworkPolicy limits which Pods can send traffic to which other Pods. Both default to "allow," so without explicit narrowing a single mistake can propagate cluster-wide. The operational baseline is "deny by default, permit only what's needed."
- **Why must metrics, logs, and traces be viewed together?**
  - Metrics show *what* is degraded and *how much*; logs show *what messages* appeared; traces show *which service span* is consuming time. Without correlating all three on the same timeline, a post-deploy 5xx spike leaves you stuck at "the cluster is slow" rather than isolating the exact service and call path responsible.

<!-- toc:begin -->
## In this series

- [Kubernetes 101 (1/10): What is Kubernetes?](./01-what-is-kubernetes.md)
- [Kubernetes 101 (2/10): Pod](./02-pod.md)
- [Kubernetes 101 (3/10): Deployment](./03-deployment.md)
- [Kubernetes 101 (4/10): Service](./04-service.md)
- [Kubernetes 101 (5/10): Ingress](./05-ingress.md)
- [Kubernetes 101 (6/10): ConfigMap and Secret](./06-configmap-and-secret.md)
- [Kubernetes 101 (7/10): Volume](./07-volume.md)
- [Kubernetes 101 (8/10): HPA](./08-hpa.md)
- [Kubernetes 101 (9/10): Helm](./09-helm.md)
- **Kubernetes in Operation (current)**

<!-- toc:end -->

## References

- [Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [NetworkPolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Argo CD](https://argo-cd.readthedocs.io/)
- [kubectl auth can-i](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_auth/kubectl_auth_can-i/)

Tags: Kubernetes, SRE, Observability, GitOps, DevOps
