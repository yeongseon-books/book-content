---
series: containers-101
episode: 1
title: "Containers 101 (1/10): What is a Container?"
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
- Docker
- Linux
- DevOps
- Architecture
seo_description: A beginner-friendly definition of containers — how they share the
  host kernel, how they differ from VMs, with a runnable docker example.
last_reviewed: '2026-05-15'
---

# Containers 101 (1/10): What is a Container?

Containers are often introduced as tiny VMs, but that shortcut hides the exact boundary that matters in operations. The real question is which parts are shared, which parts are isolated, and what that means for reproducibility and security.

This is the first post in the Containers 101 series.

In this chapter, we define a container as an isolated process tree sharing the host kernel, compare that model with a VM, and walk through what `docker run` actually creates when your first container starts.

> A container is not a tiny VM. It is an isolated process tree sharing the host kernel.


![containers 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/containers-101/01/01-01-concept-at-a-glance.en.png)
*containers 101 chapter 1 flow overview*
> The real question is: which parts are shared with the host kernel, which parts are isolated, and what happens when that isolation breaks.

## Questions to Keep in Mind

- The definition of a container?
- What gets shared with the host?
- The decisive difference from a VM?

## Why It Matters

Since 2013, the container has been the default unit of deployment. Without understanding it, modern DevOps, CI/CD, and Kubernetes remain opaque. Many beginners remember containers as "lightweight VMs"—not entirely wrong, but operationally misleading. A container does not boot a guest OS. It shares the host kernel and isolates application processes via namespaces and cgroups. That is why startup is fast, density is high, and the same image reproduces the same behavior everywhere.

A container is a process tree isolated by namespaces (PID, network, filesystem, IPC) and constrained by cgroups. They share the host kernel but not the OS image or process visibility.


## Key Terms

- **Container**: an isolated bundle of processes.
- **Image**: the static template a container starts from.
- **Namespace**: isolates process, network, and filesystem views.
- **cgroups**: caps CPU and memory.
- **Runtime**: the engine that actually runs containers.

## Before/After

**Before**: you install the application directly on each server. Python 3.9 on your laptop, Python 3.7 in production. A system library present locally is missing on the staging box. Each environment fails differently.

```text
Dev A local:   Ubuntu 22.04, Python 3.11, libpq 15
Dev B local:   macOS 14, Python 3.10, libpq 14
CI server:     Amazon Linux 2, Python 3.9, libpq 13
Production:    Debian 11, Python 3.9, libpq 13
→ Each environment can fail in a different way
```

**After**: one image bundles the Python version, system libraries, and application code. Every environment runs the identical bytes.

```text
Image: python:3.11-slim + requirements.txt + app code
Dev A local:   docker run → same image
Dev B local:   docker run → same image
CI server:     docker run → same image
Production:    docker run → same image
→ Identical behavior everywhere
```

The real value of containers is reproducibility, not speed. Eliminating "works on my laptop" is the problem containers solve.
## Hands-on: Run Your First Container

### Step 1 — Version check

```python
import subprocess

def docker_version():
    res = subprocess.run(["docker", "--version"], capture_output=True, text=True)
    return res.stdout.strip()
```

First verify Docker CLI is installed. In production, confirming tool version before debugging anything else is a habit that saves time.

### Step 2 — Pull image

```python
def pull(image):
    subprocess.run(["docker", "pull", image], check=True)
```

The image you pull (`nginx:latest`) is not the container itself—it is a static, read-only template. Remembering this distinction (template vs running instance) prevents confusion in every subsequent chapter.

### Step 3 — Run container

```python
def run_nginx():
    subprocess.run(
        ["docker", "run", "-d", "-p", "8080:80", "--name", "web", "nginx:latest"],
        check=True,
    )
```

This is where a container is actually created: the image is the blueprint, the container is the running instance. Think class vs object.

### Step 4 — Inspect

```python
def ps():
    res = subprocess.run(["docker", "ps"], capture_output=True, text=True)
    return res.stdout
```

The output of `docker ps` looks like a simple list, but in operations it is the primary observation point: port mappings, names, status, and uptime are all here.

### Step 5 — Clean up

```python
def cleanup(name):
    subprocess.run(["docker", "rm", "-f", name], check=True)
```

Cleanup completes the exercise. The fact that containers can be created and destroyed in seconds is the core operational property—disposability enables reproducibility.

## What to Notice in This Code

- `-d` runs in the background.
- `-p 8080:80` maps host:container ports.
- `--name` gives you a stable handle.

## Quick verification and failure signals

```bash
docker --version
docker run -d --name web -p 8080:80 nginx:1.27-alpine
curl -I http://127.0.0.1:8080
docker ps --filter name=web
```

**Expected output:**
- `docker --version` returns a valid engine version.
- `curl -I` shows `HTTP/1.1 200 OK`.
- `docker ps` shows `web` with `0.0.0.0:8080->80/tcp`.

**Check first if it fails:**
- If `docker run` fails, confirm local port `8080` is free.
- If `curl` fails, inspect `docker logs web` before changing the image.
- If you swap the image, verify the service still listens on port 80.

## Five Common Mistakes

1. **Forgetting port mapping — the container is unreachable.**
2. **Confusing containers with images.**
3. **Skipping cleanup until disk is full.**
4. **Running containers as root.**
5. **Believing the "works on my laptop" myth.**

## How This Shows Up in Production

Developers build the same image on Docker Desktop. CI pushes that image to a registry. Production runs the same image under Kubernetes. Every stage shares one artifact.

```text
Developer local  →  git push  →  CI (docker build + test)  →  Registry push
                                                            ↓
Production       ←  Kubernetes pull  ←  Registry (immutable tag)
```

The key insight: once an image is built, it passes through every environment without modification. The image your laptop produced and the image production runs are byte-for-byte identical, so you validate the image itself rather than debugging per-environment drift.

A container is not a development convenience—it is a deployment contract. Without this perspective, containers remain a local experimentation toy.

## How a Senior Engineer Thinks

- A container is a process, not a VM.
- Images are *immutable* artifacts.
- State lives on volumes or external stores, never inside containers.
- Default to non-root execution.
- Reproducibility is the whole point.

Senior engineers evaluate containers by "can I destroy this and spin up an identical replacement?" rather than "does it start correctly once?" What matters in production is repeatable deployment, not first-run success.

Before writing a Dockerfile, a senior engineer answers three questions: Where does this service's state live? Can I discard this container and recreate it during an incident? If I pin the image tag, will I get the same result six months later? Without answers to these three, containerization itself becomes technical debt.

## Checklist

- [ ] Docker installed and verified.
- [ ] Can explain image vs container.
- [ ] Understand port mapping.
- [ ] Know the cleanup commands.

## Practice Problems

1. State the decisive difference between containers and VMs in one line.
2. Describe what happens when `docker run` is invoked without `-d`.
3. Use the class/instance analogy to explain images vs containers.

## Wrap-up and Next Steps

If an image is a template, you have to understand its internals. The next post covers Image and Layer.

## Deep Dive: Containers vs VMs — The Operational Comparison

"Containers are lighter" is true but operationally useless. The real question is which isolation boundary to trust.

| Dimension | Container | VM |
| --- | --- | --- |
| Isolation basis | Namespaces + cgroups | Hypervisor + guest OS |
| Kernel | Shared | Independent |
| Startup | ms to seconds | Seconds to minutes |
| Density | High | Low |
| Security boundary | Logical (kernel shared) | Strong (kernel separated) |
| Best for | Microservices, CI, batch | Strong tenant isolation, custom OS |

Architecture decisions follow boundary requirements, not tool preference.

## Namespaces and Cgroups: The Two Isolation Axes

**Namespaces** partition what a process *sees*: pid, net, mnt, uts, ipc, user. **Cgroups** limit what it *consumes*: cpu.max, memory.max, pids.max, io.max. Neither works without the other—a process with its own network namespace can still eat 100% CPU without cgroup limits.

```bash
docker run --rm -d --name cpu-test --cpus="0.5" alpine sh -c "while true; do :; done"
docker inspect cpu-test --format '{{json .HostConfig.NanoCpus}}'
# Verify: container is real process set with enforced constraints
```

## Operational Scenarios

| Scenario | Choose | Why |
| --- | --- | --- |
| 40 internal services, fast iteration | Containers | Reproducibility, rolling updates, density |
| Multi-tenant SaaS, strong isolation | VM / microVM | Kernel independence required |
| CI build/test environments | Containers | Fast startup, easy cleanup |
| Kernel-module-dependent workloads | VM | Host kernel sharing is a constraint |

## Day-One Documentation Checklist

Define these before the first production container ships:

- Default resource limits (CPU, memory, pids).
- Root prohibition policy.
- Log collection path (stdout/stderr).
- State externalization rule (volumes, DB, object storage).
- Image tag and digest pinning policy.

Without these, each team develops different habits and recovery speed drops during incidents.

## Observing Isolation in Practice

```bash
# Namespace verification
docker run --rm -d --name ns-demo nginx:1.27
docker inspect -f '{{.State.Pid}}' ns-demo
ls -l /proc/<PID>/ns  # different inodes = different views

# Cgroup verification
docker run --rm -d --name cg-demo --cpus 0.5 --memory 256m nginx:1.27
docker stats --no-stream cg-demo
```

Declaring limits in Compose files rather than `docker run` flags makes isolation reviewable:

```yaml
services:
  web:
    image: nginx:1.27
    cpus: 0.50
    mem_limit: 256m
    pids_limit: 256
```

## Answering the Opening Questions

- **How can you precisely define a container in one sentence?**
  - A container is an isolated bundle of processes sharing the host kernel. Unlike a VM with a completely independent OS, it shares the kernel but isolates processes via filesystem, network, and PID namespaces.
- **What does a container share with the host, and what does it isolate?**
  - It shares the kernel and system call interface. What gets isolated: PID space, filesystem root, network interfaces, and user ID mappings. The hands-on exercise checking `/proc/<PID>/ns` in the article directly showed this boundary.
- **Where does the decisive difference from VMs arise?**
  - The kernel boundary. VMs boot a separate guest kernel, resulting in high boot time and overhead but stronger isolation. Containers share the host kernel, starting in milliseconds with high density, but a kernel vulnerability becomes every container's vulnerability. In operational design, this tradeoff must be matched to workload characteristics.
<!-- toc:begin -->
## In this series

- **What is a Container? (current)**
- Image and Layer (upcoming)
- Runtime (upcoming)
- Dockerfile (upcoming)
- Volume (upcoming)
- Network (upcoming)
- Registry (upcoming)
- Container Security (upcoming)
- Containers vs VMs (upcoming)
- Build a Container App (upcoming)

<!-- toc:end -->

## References

- [Docker official docs](https://docs.docker.com/)
- [OCI Image Spec](https://github.com/opencontainers/image-spec)
- [Linux namespaces](https://man7.org/linux/man-pages/man7/namespaces.7.html)
- [cgroups v2](https://www.kernel.org/doc/Documentation/admin-guide/cgroup-v2.rst)

Tags: Containers, Docker, Kubernetes, DevOps
