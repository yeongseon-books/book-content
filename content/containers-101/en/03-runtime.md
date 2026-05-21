---
series: containers-101
episode: 3
title: "Containers 101 (3/10): Runtime"
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
- Runtime
- containerd
- runc
- DevOps
seo_description: Docker, containerd, runc, and CRI — the layered structure of the
  container runtime stack, explained with hands-on ctr examples for beginners.
last_reviewed: '2026-05-15'
---

# Containers 101 (3/10): Runtime

When a container fails, many beginners assume the Docker CLI is always the first place to look. In real clusters, that mental model breaks quickly because Docker, containerd, runc, and CRI sit at different layers with different responsibilities.

This is post 3 in the Containers 101 series.

In this chapter, we separate the user-facing layer, lifecycle daemon, low-level executor, and Kubernetes runtime interface so you know which layer is actually failing when the node misbehaves.

> Runtime trouble gets easier to debug once you know which layer owns UX, lifecycle, and process execution.


![containers 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/containers-101/03/03-01-concept-at-a-glance.en.png)
*containers 101 chapter 3 flow overview*
> The runtime is really three layers: high-level (Docker, containerd) for image and storage; low-level (runc) for process spawning; and orchestration glue (CRI) for Kubernetes.

## Questions to Keep in Mind

- High-level vs low-level runtimes?
- The Docker → containerd → runc flow?
- The role of CRI?

## Why It Matters

Since Kubernetes 1.24 removed `dockershim`, you cannot debug effectively without knowing the runtime layers.

Docker and containerd are daemons that manage images and storage. runc is the actual process executor. When Kubernetes 1.24 removed dockershim, it meant most clusters switch directly to containerd or another CRI-compatible runtime.

## Key Terms

- **Docker**: a high-level user CLI plus daemon.
- **containerd**: a daemon that manages container lifecycle.
- **runc**: the OCI low-level executor.
- **CRI**: the interface Kubernetes uses to talk to runtimes.
- **OCI**: the Open Container Initiative standards.

## Before/After

**Before**: assume Docker is all there is.

**After**: clearly separate the roles of containerd, runc, and CRI.

## Hands-on: containerd Directly

### Step 1 — Client (illustrative)

```python
import subprocess

def ctr_version():
    res = subprocess.run(["ctr", "version"], capture_output=True, text=True)
    return res.stdout
```

### Step 2 — Pull

```python
def ctr_pull(image):
    subprocess.run(["ctr", "image", "pull", image], check=True)
```

### Step 3 — Run

```python
def ctr_run(image, name):
    subprocess.run(
        ["ctr", "run", "-d", image, name],
        check=True,
    )
```

### Step 4 — List

```python
def ctr_list():
    res = subprocess.run(["ctr", "containers", "ls"], capture_output=True, text=True)
    return res.stdout
```

### Step 5 — Cleanup

```python
def ctr_kill(name):
    subprocess.run(["ctr", "task", "kill", name])
    subprocess.run(["ctr", "container", "rm", name])
```

## What to Notice in This Code

- `ctr` is containerd's debugging CLI.
- `task` and `container` are separate concepts.
- Kubernetes uses `crictl` instead.

## Quick verification and failure signals

```bash
ctr version
ctr image pull docker.io/library/nginx:1.27-alpine
ctr images ls | grep nginx
crictl info
```

**Expected output:**
- `ctr version` reports both client and server versions.
- `ctr images ls` shows the pulled image under containerd.
- On a Kubernetes node, `crictl info` reveals the CRI endpoint and runtime data.

**Check first if it fails:**
- If `ctr` is missing, confirm whether you are on a real containerd host.
- If `crictl info` fails, inspect the CRI socket path first.
- If the pull fails, check registry reachability, proxy policy, and node credentials.

## Five Common Mistakes

1. **Learning Docker but ignoring containerd entirely.**
2. **Trying to debug a Kubernetes node with the `docker` CLI.**
3. **Mismatching runtime versions across hosts.**
4. **Skipping the rootless runtime option.**
5. **Ignoring `runc`'s default seccomp profile.**

## How This Shows Up in Production

Kubernetes nodes run containerd. Operators reach for `crictl`. Local development still leans on Docker Desktop. Embedded systems often use `podman`.

## How a Senior Engineer Thinks

- Knowing the runtime layers handles half of all incidents.
- Docker is a user tool; containerd is an operations tool.
- OCI is the secret sauce of compatibility.
- Default to rootless when you can.
- Runtime upgrades affect the whole cluster.

## Checklist

- [ ] Can explain containerd vs runc.
- [ ] Understand what CRI does.
- [ ] Aware of `crictl` for debugging.
- [ ] Aware of OCI as a standard.

## Practice Problems

1. Difference in responsibility between runc and containerd, in one line.
2. Give one reason Kubernetes removed `dockershim`.
3. State when you should reach for `crictl`, in one line.

## Wrap-up and Next Steps

To run an image, you must build one. The next post covers Dockerfile.

## Answering the Opening Questions

- **High-level vs low-level runtimes?**
  - The article treats Runtime as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **The Docker → containerd → runc flow?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **The role of CRI?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Containers 101 (1/10): What is a Container?](./01-what-is-a-container.md)
- [Containers 101 (2/10): Image and Layer](./02-image-and-layer.md)
- **Runtime (current)**
- Dockerfile (upcoming)
- Volume (upcoming)
- Network (upcoming)
- Registry (upcoming)
- Container Security (upcoming)
- Containers vs VMs (upcoming)
- Build a Container App (upcoming)

<!-- toc:end -->

## References

- [containerd docs](https://containerd.io/docs/)
- [runc repo](https://github.com/opencontainers/runc)
- [Kubernetes CRI](https://kubernetes.io/docs/concepts/architecture/cri/)
- [OCI standards](https://opencontainers.org/)

Tags: Containers, Docker, Kubernetes, DevOps
