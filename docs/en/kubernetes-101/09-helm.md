---
series: kubernetes-101
episode: 9
title: Helm
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
  - Helm
  - Chart
  - PackageManager
  - DevOps
seo_description: A beginner-friendly tour of Helm covering chart layout, values, install/upgrade/rollback, repos, and dependency management for Kubernetes deployments.
last_reviewed: '2026-05-04'
---

# Helm

> Kubernetes 101 series (9/10)

<!-- a-grade-intro:begin -->

**Core question**: should you *copy/paste* dozens of *manifests* across *environments*?

> *Helm* separates *templates* from *values* through a unit called a *chart*.

<!-- a-grade-intro:end -->

## What You Will Learn

- the layout of a *Chart*
- how *values.yaml* works
- *install / upgrade / rollback*
- *repositories* and *dependencies*
- the role of *helm template*

## Why It Matters

*Per-environment copies* create *drift*. *Helm* lets you reuse the *same template* and only swap *values*.

## Concept at a Glance

```mermaid
flowchart LR
    Values["values.yaml"] --> Tmpl["templates/*.yaml"]
    Tmpl --> Render["rendered manifests"]
    Render --> API["kubernetes api"]
```

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

### Step 3 — install

```python
def install(release, chart, values):
    subprocess.run(
        ["helm", "install", release, chart, "-f", values],
        check=True,
    )
```

### Step 4 — upgrade

```python
def upgrade(release, chart, values):
    subprocess.run(
        ["helm", "upgrade", release, chart, "-f", values, "--atomic"],
        check=True,
    )
```

### Step 5 — rollback

```python
def rollback(release, revision):
    subprocess.run(
        ["helm", "rollback", release, str(revision)],
        check=True,
    )
```

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

<!-- toc:begin -->
- [What is Kubernetes?](./01-what-is-kubernetes.md)
- [Pod](./02-pod.md)
- [Deployment](./03-deployment.md)
- [Service](./04-service.md)
- [Ingress](./05-ingress.md)
- [ConfigMap and Secret](./06-configmap-and-secret.md)
- [Volume](./07-volume.md)
- [HPA](./08-hpa.md)
- **Helm (current)**
- Kubernetes in Operation (upcoming)
<!-- toc:end -->

## References

- [Helm official docs](https://helm.sh/docs/)
- [Chart structure](https://helm.sh/docs/topics/charts/)
- [Helm best practices](https://helm.sh/docs/chart_best_practices/)
- [Artifact Hub](https://artifacthub.io/)
