---
series: containers-101
episode: 8
title: "Containers 101 (8/10): Container Security"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
- Containers
- Security
- seccomp
- Cosign
- DevOps
seo_description: A beginner guide to container security covering non-root users, capabilities,
  seccomp, image scanning, and proper secret handling with examples
last_reviewed: '2026-05-15'
---

# Containers 101 (8/10): Container Security

Isolation does not make a container automatically safe. Default settings can still leave you with a root process, excess capabilities, weak secret handling, and unsigned artifacts moving through production.

This is the 8th post in the Containers 101 series.

In this chapter, we build a practical baseline around non-root users, capability reduction, seccomp, read-only filesystems, image scanning, and signature-aware delivery.

> Container security improves when defaults get narrower: fewer privileges, fewer writable paths, fewer blind spots.


![containers 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/containers-101/08/08-01-concept-at-a-glance.en.png)
*containers 101 chapter 8 flow overview*
> Container security is not one choice but layers: no root, minimal privileges, image scanning, runtime policies, and host isolation — break any layer and risk grows.

## Questions to Keep in Mind

- What *non-root* means?
- Capabilities* and *seccomp?
- Image scanning?

## Why It Matters

A default container runs as *root* with *too many privileges* and easily becomes the *starting point* of a security incident.

Never run containers as root unless forced to. Use non-root users in Dockerfile. Scan images for known CVEs. Apply runtime policies (seccomp, SELinux, AppArmor) to restrict syscalls. Remember: containers share the host kernel, so kernel bugs can leak between containers.

## Key Terms

- **non-root**: running as a *normal user* such as UID 1000.
- **capability**: a *fragment* of root privilege.
- **seccomp**: a *syscall whitelist*.
- **image scanning**: checking *known CVEs*.
- **secret**: stored in a *dedicated system*, not env vars.

## Before / After

**Before**: running as *root* with *every privilege*.

**After**: *non-root + minimal capabilities + seccomp* shrinks the *attack surface*.

## Hands-on: Run a Container Safely

### Step 1 — Scan the image

```python
import subprocess

def scan(image):
    res = subprocess.run(
        ["trivy", "image", "--severity", "HIGH,CRITICAL", image],
        capture_output=True, text=True,
    )
    return res.returncode == 0
```

### Step 2 — Force non-root

```python
def run_nonroot(image):
    subprocess.run([
        "docker", "run", "--rm", "-d",
        "--user", "1000:1000", image,
    ], check=True)
```

### Step 3 — Drop capabilities

```python
def run_min_caps(image):
    subprocess.run([
        "docker", "run", "--rm", "-d",
        "--cap-drop=ALL", "--cap-add=NET_BIND_SERVICE", image,
    ], check=True)
```

### Step 4 — Read-only filesystem

```python
def run_readonly(image):
    subprocess.run([
        "docker", "run", "--rm", "-d",
        "--read-only", "--tmpfs", "/tmp", image,
    ], check=True)
```

### Step 5 — Mount a secret

```python
def run_with_secret(image, secret_path):
    subprocess.run([
        "docker", "run", "--rm", "-d",
        "-v", f"{secret_path}:/run/secrets/db_pw:ro", image,
    ], check=True)
```

## What to Notice in This Code

- *--user* avoids running as root.
- After *--cap-drop=ALL* we add only what is needed.
- *Secrets* are mounted as volumes.

## Quick verification and failure signals

```bash
trivy image --severity HIGH,CRITICAL python:3.12-slim
docker run --rm --user 1000:1000 python:3.12-slim id
docker run --rm --cap-drop=ALL --cap-add=NET_BIND_SERVICE nginx:1.27-alpine nginx -t
docker run --rm --read-only --tmpfs /tmp python:3.12-slim python -c "print("ok")"
```

**Expected output:**
- `id` shows a non-root UID and GID.
- The process still works with only the minimum extra capability added back.
- The container can run read-only as long as writable scratch paths are explicit.

**Check first if it fails:**
- If non-root fails, inspect writable paths and ownership before broadening permissions.
- If read-only mode fails, trace which directory the app expects to write to.
- If scan results are noisy, start with base-image choice and package removal.

## Five Common Mistakes

1. **Running as *root* and trusting the inside.**
2. **Exposing *secrets* as *env vars*.**
3. **Shipping to production *without scanning*.**
4. **Overusing *privileged* containers.**
5. **Skipping *signature verification*, opening replacement attacks.**

## How This Shows Up in Production

*Kubernetes Pod Security* and *admission controllers* enforce *non-root, no privileged, signed only* policies at *runtime*.

## How a Senior Engineer Thinks

- *Defaults* are *dangerous*.
- *Capabilities* are *added explicitly* only.
- *Secrets* belong to a *dedicated system*.
- *Scanning* is part of the *CI gate*.
- *Signing* starts *supply-chain trust*.

## Checklist

- [ ] *Non-root* user.
- [ ] *cap-drop=ALL* with minimal additions.
- [ ] *Read-only* filesystem.
- [ ] *Secrets* via volumes or a secret manager.

## Practice Problems

1. Explain in one line *why capabilities exist*.
2. Describe the role of *seccomp* in one line.
3. Name one *attack* signed images prevent.

## Wrap-up and Next Steps

With security principles in place, the next topic is the *fundamental difference* between *containers and VMs*. The next post covers *containers vs VMs*.

## Answering the Opening Questions

- **What *non-root* means?**
  - The article treats Container Security as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Capabilities* and *seccomp?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Image scanning?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Containers 101 (1/10): What is a Container?](./01-what-is-a-container.md)
- [Containers 101 (2/10): Image and Layer](./02-image-and-layer.md)
- [Containers 101 (3/10): Runtime](./03-runtime.md)
- [Containers 101 (4/10): Dockerfile](./04-dockerfile.md)
- [Containers 101 (5/10): Volume](./05-volume.md)
- [Containers 101 (6/10): Network](./06-network.md)
- [Containers 101 (7/10): Registry](./07-registry.md)
- **Container Security (current)**
- Containers vs VMs (upcoming)
- Build a Container App (upcoming)

<!-- toc:end -->

## References

- [Docker security](https://docs.docker.com/engine/security/)
- [Kubernetes Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Trivy](https://aquasecurity.github.io/trivy/)
- [seccomp profiles](https://docs.docker.com/engine/security/seccomp/)

Tags: Containers, Docker, Kubernetes, DevOps
