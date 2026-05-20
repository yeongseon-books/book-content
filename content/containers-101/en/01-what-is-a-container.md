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

## Questions to Keep in Mind

- The definition of a container?
- What gets shared with the host?
- The decisive difference from a VM?

## Big Picture

![containers 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/containers-101/01/01-01-concept-at-a-glance.en.png)

*containers 101 chapter 1 flow overview*

This picture places What is a Container? inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of What is a Container? is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Why It Matters

Since 2013, the container has been the default unit of deployment. Without it, modern DevOps is closed off to you.

## Concept at a Glance

## Key Terms

- **Container**: an isolated bundle of processes.
- **Image**: the static template a container starts from.
- **Namespace**: isolates process, network, and filesystem views.
- **cgroups**: caps CPU and memory.
- **Runtime**: the engine that actually runs containers.

## Before/After

**Before**: install directly on a server, then watch it break in production due to environment drift.

**After**: one image runs the same way on any machine.

## Hands-on: Run Your First Container

### Step 1 — Version check

```python
import subprocess

def docker_version():
    res = subprocess.run(["docker", "--version"], capture_output=True, text=True)
    return res.stdout.strip()
```

### Step 2 — Pull image

```python
def pull(image):
    subprocess.run(["docker", "pull", image], check=True)
```

### Step 3 — Run container

```python
def run_nginx():
    subprocess.run(
        ["docker", "run", "-d", "-p", "8080:80", "--name", "web", "nginx:latest"],
        check=True,
    )
```

### Step 4 — Inspect

```python
def ps():
    res = subprocess.run(["docker", "ps"], capture_output=True, text=True)
    return res.stdout
```

### Step 5 — Clean up

```python
def cleanup(name):
    subprocess.run(["docker", "rm", "-f", name], check=True)
```

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

Developers build the same image on Docker Desktop. CI pushes that image to a registry. Production runs the same image under Kubernetes.

## How a Senior Engineer Thinks

- A container is a process, not a VM.
- Images are *immutable*.
- State lives on volumes, not inside containers.
- Default to non-root.
- Reproducibility is the whole point.

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

## Answering the Opening Questions

- **The definition of a container?**
  - The article treats What is a Container? as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **What gets shared with the host?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **The decisive difference from a VM?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

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
