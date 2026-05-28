---
series: docker-101
episode: 1
title: "Docker 101 (1/10): What Is Docker?"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Docker
  - Container
  - DevOps
  - Linux
  - Virtualization
seo_description: Containers vs virtual machines and what Docker actually does, in a five-minute introduction with a runnable first container.
last_reviewed: '2026-05-15'
---

# Docker 101 (1/10): What Is Docker?

Docker usually gets introduced as a convenience tool for developers. That framing is not wrong, but it is too small. What teams actually buy with Docker is reproducibility: the ability to move one runnable artifact across a laptop, CI, staging, and production without rewriting the environment story each time.

When that reproducibility is missing, debugging turns vague very quickly. You stop asking whether the code is wrong and start asking whether Python, OpenSSL, libc, or a forgotten package version changed under your feet. Docker is valuable because it makes that ambiguity much smaller.

This is the first post in the Docker 101 series. It sets the mental model for the rest of the series by clarifying what Docker is, how containers differ from virtual machines, and what you should verify when you run your first container.


![docker 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/01/01-01-concept-at-a-glance.en.png)
*docker 101 chapter 1 flow overview*

## Questions to Keep in Mind

- The difference between *containers* and *virtual machines?
- The *environment-drift* problem Docker solves?
- The big picture of *image / container / registry?

## Why It Matters

*Environment differences* are the most demoralizing thing for newcomers. *One Docker line* gives the *whole team the same environment*, cutting half of the debugging time.

> *Environment problems are not a *skill issue*; they are a *design issue*.*

## Key Terms

- **Image**: an *executable package* (code + libraries + OS layers).
- **Container**: a *running instance* of an image.
- **Registry**: an image storage backend (Docker Hub, GHCR).
- **Daemon**: the background process that *creates and manages* containers.
- **Layer**: the *unit of change* inside an image.

## Before/After

**Before**: "It runs on my laptop." New-hire setup takes *half a day*.

**After**: `docker run myapp`. *Same environment in five minutes*.

## Hands-on: Your First Container in 5 Steps

### Step 1 — Verify install

```bash
docker --version
# Docker version 25.x.x
docker run hello-world
```

### Step 2 — Run an official image

```bash
docker run -it --rm python:3.12-slim python -c "print('hi')"
```

### Step 3 — Run in the background

```bash
docker run -d --name web -p 8080:80 nginx
curl http://localhost:8080
```

### Step 4 — Inspect

```bash
docker ps              # running
docker logs web        # logs
docker stop web && docker rm web
```

### Step 5 — Search and pull images

```bash
docker pull redis:7-alpine
docker images
```

### Verify right after you run it

- After `docker run hello-world`, Docker should print the standard success message explaining that it pulled the image and ran the test container.
- `curl http://localhost:8080` should return the default nginx page. If the connection is refused, start with the port mapping.

### If it does not work, check this first

- Confirm that Docker Desktop or the Docker daemon is actually running; installation alone is not enough.
- If the container is running but unreachable, verify that `-p 8080:80` maps host port to container port in the intended order.

## What to Notice in This Code

- An *image* is a *snapshot just before run*; a *container* is a *live process*.
- *`-p 8080:80`* maps *host:container* ports.
- *`--rm`* cleans up after exit.

## Five Common Mistakes

1. **Treating Docker like a VM.** Containers *share the host kernel*.
2. **Using the `latest` tag in *production*.** It will *break silently* one day.
3. **Letting containers pile up without `docker rm`.** Your disk *fills up*.
4. **Forgetting `-p` and being puzzled it is "down".** Port mapping is required.
5. **Running as root, then promoting to *production*.** A security incident waiting to happen.

## How This Shows Up in Production

Most organizations operate on the assumption that *a service equals a container*. Local dev, CI, staging, and production all run the *same image*.

## How a Senior Engineer Thinks

- *Environments are code*, not wiki pages.
- *Images are *immutable*; containers are *disposable*.
- *latest* is for demos; production uses *pinned tags*.
- *A container is a process*; mind PID 1.
- *Sharing the host kernel* is where security starts.

## Checklist

- [ ] `docker run hello-world` works.
- [ ] You can explain *image* vs *container*.
- [ ] You understand *port mapping*.
- [ ] You can *clean up* containers.

## Practice Problems

1. Run `nginx` and access it on *host port 8080*.
2. Open an *interactive shell* with `python:3.12-slim`.
3. Inspect a running container's *logs* and *status*.

## Wrap-up and Next Steps

Docker is the fastest way to kill *environment drift*. Next we look deeper into *images and containers*.

## Answering the Opening Questions

- **What exactly does Docker do for you?**
  - Docker packages an application and its runtime environment into a single image, reducing the "works on my machine" problem. Because build, deploy, and run all use the same unit (image/container), debugging costs from environment differences drop significantly.
- **How does a container differ from a virtual machine?**
  - As the comparison diagram showed, VMs virtualize an entire OS kernel — heavy and slow to start — while containers share the host kernel and add only process isolation. The result is tens of MB instead of hundreds, and millisecond startup instead of seconds. A trade-off of isolation strength for density and speed.
- **How should you understand the relationship between image, container, and registry?**
  - An image is a built static snapshot, a container is a running instance of that image, and a registry stores and distributes images. The flow `docker build` → registry `push` → `pull` elsewhere → `run` is exactly how these three objects collaborate.

<!-- toc:begin -->
## In this series

- **What Is Docker? (current)**
- Images and Containers (upcoming)
- Writing a Dockerfile (upcoming)
- Volumes and Networks (upcoming)
- Docker Compose (upcoming)
- Environment Variables and Configuration (upcoming)
- Containerizing a Python App (upcoming)
- Running with a Database (upcoming)
- Image Optimization (upcoming)
- Production-Ready Docker (upcoming)

<!-- toc:end -->

## References

### Official docs

- [Docker overview](https://docs.docker.com/get-started/overview/)
- [Get Docker](https://docs.docker.com/get-docker/)
- [Docker Hub](https://hub.docker.com/)
- [What is a container?](https://www.docker.com/resources/what-container/)

### Verification and troubleshooting

- [docker run reference](https://docs.docker.com/engine/reference/run/)

Tags: Docker, Container, DevOps, Linux, Virtualization
