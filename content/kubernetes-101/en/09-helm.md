---
series: kubernetes-101
episode: 9
title: "Kubernetes 101 (9/10): Helm"
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
  - Helm
  - Chart
  - PackageManager
  - DevOps
seo_description: A beginner-friendly tour of Helm covering chart layout, values, install/upgrade/rollback, repos, and dependency management for Kubernetes deployments.
last_reviewed: '2026-05-15'
---

# Kubernetes 101 (9/10): Helm

Kubernetes YAML usually starts tidy and then multiplies across environments. Before long, the real problem is no longer writing manifests but keeping the right differences in the right places without copying entire files forever.

This is the 9th post in the Kubernetes 101 series.

Here, we will frame Helm as a repeatable deployment unit that separates shared structure from environment-specific values and gives you install, upgrade, and rollback workflows that are easier to reason about.

> Helm becomes valuable when the chart expresses the common contract and the values file is the only place where environments diverge.


![kubernetes 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/09/09-01-concept-at-a-glance.en.png)
*kubernetes 101 chapter 9 flow overview*

## Questions to Keep in Mind

- the layout of a *Chart?
- how *values.yaml* works?
- install / upgrade / rollback?

## Why It Matters

Per-environment YAML copies create drift silently. A patch applied to `prod/` is forgotten in `staging/`; a direct edit in one directory diverges from the others within days. Helm forces differences into a single axis—values files—while the chart itself is the shared contract. This separation makes environment promotion a values swap rather than a directory diff.

## Key Terms

- **Chart**: the *package unit* of *Helm*.
- **values.yaml**: the *default values* file.
- **release**: an *installed instance* of a *chart*.
- **repository**: the *distribution channel* for *charts*.
- **dependency**: a *subchart* relation.

## Before/After

**Before**: three *YAML copies* for *dev/stage/prod*.

**After**: one *Chart* with *per-environment values*.

## Hands-on: a Tiny Chart

### Step 1 — Create the Chart

```python
import subprocess

def create(name):
    subprocess.run(["helm", "create", name], check=True)
```

`helm create` scaffolds a chart with sane defaults, but the real work is deciding what goes into templates versus values. Anything that changes per environment (replica count, image tag, domain) belongs in `values.yaml`; structural decisions (which Kubernetes objects, resource relationships) stay in templates.

### Step 2 — values.yaml

```python
"""
replicaCount: 2
image:
  repository: myorg/app
  tag: "1.0"
service:
  type: ClusterIP
  port: 80
"""
```

Values hold environment-varying data; the chart structure stays constant. When you promote from dev to prod, only the `-f values-prod.yaml` flag changes—the chart itself is identical, eliminating an entire class of "works in dev, broken in prod" issues.

### Step 3 — install

```python
def install(release, chart, values):
    subprocess.run(
        ["helm", "install", release, chart, "-f", values],
        check=True,
    )
```

A release is an installed instance of a chart—a name, a namespace, and a revision history. This makes Helm a deploy-management tool, not just a template engine: you can query what was deployed, when, and roll back to any previous state.

### Step 4 — upgrade

```python
def upgrade(release, chart, values):
    subprocess.run(
        ["helm", "upgrade", release, chart, "-f", values, "--atomic"],
        check=True,
    )
```

`--atomic` automatically rolls back if any resource in the upgrade fails to become healthy within the timeout. Without it, a broken upgrade leaves the release in a partial state that requires manual intervention—dangerous for unattended or night deploys.

### Step 5 — rollback

```python
def rollback(release, revision):
    subprocess.run(
        ["helm", "rollback", release, str(revision)],
        check=True,
    )
```

Rollback needs practice before incidents. Know your previous good revision number (`helm history`), test the rollback path in staging, and verify that dependent resources (ConfigMaps, Secrets, PVCs) remain compatible with the older chart revision.

## Verification workflow

```bash
helm template web ./chart -f values.yaml
helm lint ./chart
helm history web
```

**Expected output:** `helm template` should show the exact manifests you are about to apply, `helm lint` should catch structural issues in the chart early, and `helm history` should prove that a release has revision history available for rollback.

**Failure modes to check first:**

- If the rendered YAML is already wrong, the problem is chart/value separation rather than the cluster.
- A chart that lints clean can still be operationally unsafe if secrets remain as plain values.
- If rollback is missing, inspect release-history behavior in the install/upgrade workflow before the next incident.

## What to Notice in This Code

- *--atomic* triggers an *automatic rollback* on failure.
- *helm template* lets you *inspect rendered output* before applying.
- *Values* differ per environment; the *Chart* is shared.

## Five Common Mistakes

1. **Mixing *values* and *Chart* into the *same file*.**
2. **Storing *secrets* as *plain text* in *values*.**
3. **Using *latest* without a *version pin*.**
4. **Not knowing the *rollback* procedure.**
5. **Forgetting to *update dependencies*.**

## How This Shows Up in Production

Combined with *GitOps*, a *values change* alone drives *PR-based* deploys.

## How a Senior Engineer Thinks

- *Chart* is a *shared contract*.
- *Values* should hold only *environment differences*.
- *--atomic* is the *seatbelt* for *night deploys*.
- *Rollback* needs *practice*.
- Delegate *Secret* handling to an *external manager*.

## Checklist

- [ ] *Chart* and *values* separated.
- [ ] *Version pinned*.
- [ ] *--atomic* used.
- [ ] *Secrets* externalized.

## Practice Problems

1. In one line, the *purpose* of *helm template*.
2. In one line, the *responsibility difference* between *values* and *Chart*.
3. In one line, why *--atomic* is *safer*.

## Wrap-up and Next Steps

With a deploy unit in hand, the final piece is the *operations view*. Next post is *Kubernetes in Operation*.

## Answering the Opening Questions

- **Why does copying YAML per environment create drift?**
  - Separate `dev/`, `staging/`, `prod/` directories with near-identical manifests inevitably diverge: a patch applied to one misses another, and direct edits become untrackable. Over time "same code behaves differently across environments" accumulates silently.
- **What responsibilities do Chart and `values.yaml` split?**
  - The Chart defines templates and structure (which objects, in what shape); `values.yaml` isolates environment-variable values (image tag, replica count, domain). This separation enables the pattern of keeping one Chart and swapping `-f values-prod.yaml` per environment.
- **How do `install`, `upgrade`, and `rollback` flow together?**
  - `install` creates a new release with its objects; `upgrade` adds a new revision to an existing release; `rollback` reverts to a previous revision in that history. A Helm release is not a single snapshot but a versioned change log—enabling fast recovery during incidents.

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
- **Helm (current)**
- Kubernetes in Operation (upcoming)

<!-- toc:end -->

## References

- [Helm official docs](https://helm.sh/docs/)
- [Chart structure](https://helm.sh/docs/topics/charts/)
- [Helm best practices](https://helm.sh/docs/chart_best_practices/)
- [Artifact Hub](https://artifacthub.io/)
- [helm lint](https://helm.sh/docs/helm/helm_lint/)

Tags: Kubernetes, Helm, Chart, PackageManager, DevOps
