---
series: kubernetes-101
episode: 6
title: ConfigMap and Secret
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
  - ConfigMap
  - Secret
  - Configuration
  - DevOps
seo_description: A beginner guide to Kubernetes ConfigMap and Secret — splitting config from secrets and injecting them via env vars or file mounts
last_reviewed: '2026-05-15'
---

# ConfigMap and Secret

It is easy to hardcode configuration and passwords when an application has only one environment. That shortcut becomes expensive as soon as you want the same image to move through dev, staging, and production without carrying secrets inside the artifact.

This is post 6 in the Kubernetes 101 series.

Here, we will use ConfigMap and Secret to split environment-specific values from the image and connect that split to injection methods, restart behavior, and external secret managers.

> Configuration becomes operationally useful only when the image can stay the same while the environment-specific values change outside it.

## Questions this chapter answers

- Splitting *ConfigMap* and *Secret*
- *Env vars* vs *file mounts*
- The *base64* fact and the *encryption gap*
- Integrating an *external secret manager*
- *Restart on change*

## Why It Matters

Pulling *environment differences* out of the image is what makes things *reproducible*. *Secrets* must be tracked *separately*.

## Concept at a Glance

![Concept at a Glance](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/06/06-01-concept-at-a-glance.en.png)
*ConfigMap and Secret can both enter the same Pod, but they intentionally represent different operational and security boundaries.*


## Key Terms

- **ConfigMap**: a bundle of *non-secret key/value*.
- **Secret**: a bundle of *secret key/value* (base64).
- **envFrom**: bulk-injects keys as *env vars*.
- **volume mount**: mounts data as *files*.
- **External Secrets**: syncs from an *external manager*.

## Before / After

**Before**: *baking the DB password* into the image.

**After**: *injecting via Secret*; the *image is environment-agnostic*.

## Hands-on: Split Config and Secrets

### Step 1 — ConfigMap

```python
"""
apiVersion: v1
kind: ConfigMap
metadata: {name: app-config}
data:
  LOG_LEVEL: "info"
  FEATURE_FLAG: "true"
"""
```

### Step 2 — Secret

```python
"""
apiVersion: v1
kind: Secret
metadata: {name: app-secret}
type: Opaque
stringData:
  DB_PASSWORD: "s3cret"
"""
```

### Step 3 — Inject into a Pod

```python
"""
spec:
  containers:
  - name: app
    image: myorg/app:1.0
    envFrom:
    - configMapRef: {name: app-config}
    - secretRef: {name: app-secret}
"""
```

### Step 4 — Mount as files

```python
"""
volumes:
- name: cfg
  configMap: {name: app-config}
volumeMounts:
- name: cfg
  mountPath: /etc/app
"""
```

### Step 5 — Restart after change

```python
import subprocess

def restart(dep):
    subprocess.run(
        ["kubectl", "rollout", "restart", f"deployment/{dep}"],
        check=True,
    )
```

## Verification workflow

```bash
kubectl get configmap app-config -o yaml
kubectl get secret app-secret -o yaml
kubectl exec deploy/web -- env | grep 'LOG_LEVEL\|DB_PASSWORD'
```

**Expected output:** ConfigMap data should remain readable, Secret data should appear base64-encoded, and the `exec` check should confirm that the injected values reached the running process environment inside the container.

**Failure modes to check first:**

- If Secret data looks plain, revisit `stringData` vs `data` and how the manifest was rendered.
- If the object changed but the app still sees the old value, check whether a rollout restart was skipped.
- If the app expects files rather than env vars, the mount path matters more than `envFrom`.

## What to Notice in This Code

- *stringData* handles *base64 encoding for you*.
- *envFrom* injects the *whole bundle*.
- A *change* requires an *explicit restart*.

## Five Common Mistakes

1. **Equating *Secret* with *encryption*.**
2. **Storing *Secret values* in *Git in the clear*.**
3. **Expecting *ConfigMap* changes to *auto-reload*.**
4. **Cramming *long config* into *env vars only*.**
5. **Skipping *Secret RBAC*.**

## How This Shows Up in Production

The *External Secrets Operator* keeps *Vault / AWS Secrets Manager* as the *source of truth* and *syncs cluster Secrets* automatically.

## How a Senior Engineer Thinks

- *Secrets* are *base64*, not *encryption*.
- The *external manager* is the *source of truth*.
- *RBAC* is the *last line of defense*.
- *Change means restart*.
- *Per-environment ConfigMap* gives *reproducibility*.

## Checklist

- [ ] No *plain Secrets* in *Git*.
- [ ] *RBAC* applied.
- [ ] *rollout restart* after a change.
- [ ] *External manager* considered first.

## Practice Problems

1. State the *difference* between ConfigMap and Secret in one line.
2. Explain in one line *what* "Secret is not encryption" means.
3. Name *one benefit* of External Secrets.

## Wrap-up and Next Steps

Config is solved. The next post covers persisting *state data* with *Volumes*.

<!-- toc:begin -->
- [What is Kubernetes?](./01-what-is-kubernetes.md)
- [Pod](./02-pod.md)
- [Deployment](./03-deployment.md)
- [Service](./04-service.md)
- [Ingress](./05-ingress.md)
- **ConfigMap and Secret (current)**
- Volume (upcoming)
- HPA (upcoming)
- Helm (upcoming)
- Kubernetes in Operation (upcoming)
<!-- toc:end -->

## References

- [ConfigMap](https://kubernetes.io/docs/concepts/configuration/configmap/)
- [Secret](https://kubernetes.io/docs/concepts/configuration/secret/)
- [External Secrets Operator](https://external-secrets.io/)
- [RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [Distribute credentials securely using Secrets](https://kubernetes.io/docs/tasks/inject-data-application/distribute-credentials-secure/)

Tags: Kubernetes, ConfigMap, Secret, Configuration, DevOps
