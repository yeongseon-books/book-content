---
series: containers-101
episode: 4
title: Dockerfile
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
- Dockerfile
- Build
- DevOps
seo_description: Dockerfile rules, cache-friendly ordering, multi-stage builds, and
  security defaults — taught with a runnable Python app example.
last_reviewed: '2026-05-15'
---

# Dockerfile

A Dockerfile is not just a text file that happens to build an image. Instruction order changes cache hit rate, base-image choice changes image size and CVE count, and one user directive can change the security posture of the runtime.

This is post 4 in the Containers 101 series.

In this chapter, we focus on cache-friendly instruction order, multi-stage builds, non-root defaults, and secret handling so the resulting image is faster, smaller, and safer to ship.

> Dockerfile quality is really cache quality, image quality, and runtime safety compressed into one file.

## Questions this chapter answers

- The role and order of instructions
- Cache-friendly authoring
- Multi-stage builds
- Security defaults
- Five common pitfalls

## Why It Matters

A Dockerfile directly drives team productivity and security. Get it right once and it pays back for years.

## Concept at a Glance

![Builder stage separated from the runtime stage](../../../assets/containers-101/04/04-01-concept-at-a-glance.en.png)

*Builder stage separated from the runtime stage*
## Key Terms

- **FROM**: the base image.
- **WORKDIR**: the working directory.
- **COPY/ADD**: copy files in.
- **RUN**: command at build time.
- **CMD/ENTRYPOINT**: the default command at run time.

## Before/After

**Before**: a single-stage build produces a 900MB image.

**After**: multi-stage plus a slim base lands at about 80MB.

## Hands-on: A Python App Dockerfile (illustrative)

### Step 1 — Base

```python
def base_stage():
    return [
        "FROM python:3.12-slim AS builder",
        "WORKDIR /app",
    ]
```

### Step 2 — Dependencies first

```python
def deps_stage():
    return [
        "COPY requirements.txt .",
        "RUN pip install --user -r requirements.txt",
    ]
```

### Step 3 — Code

```python
def code_stage():
    return [
        "COPY . .",
    ]
```

### Step 4 — Runtime stage

```python
def runtime_stage():
    return [
        "FROM python:3.12-slim",
        "WORKDIR /app",
        "COPY --from=builder /root/.local /root/.local",
        "COPY --from=builder /app .",
        "ENV PATH=/root/.local/bin:$PATH",
    ]
```

### Step 5 — Non-root and run

```python
def finalize():
    return [
        "RUN useradd -m app && chown -R app:app /app",
        "USER app",
        "CMD [\"python\", \"main.py\"]",
    ]
```

## What to Notice in This Code

- `requirements.txt` is copied *before* code so the layer caches.
- `--from=builder` brings results from the previous stage.
- `USER app` avoids root.

## Quick verification and failure signals

```bash
docker build -t demo-app:dev .
docker image inspect demo-app:dev --format "user={{.Config.User}} size={{.Size}}"
```

**Expected output:**
- The dependency layer sits early enough to be cached between source-only rebuilds.
- `Config.User` is not empty and points to a non-root runtime user.

**Check first if it fails:**
- If dependencies reinstall every time, inspect where `COPY requirements.txt` sits.
- If the app still runs as root, confirm `USER` exists in the final stage.
- If the image is too large, check whether build tools leaked into runtime.

## Five Common Mistakes

1. **`COPY .` first — kills the cache.**
2. **`apt update` standalone — leaves stale cache.**
3. **Running as root.**
4. **Storing secrets in `ENV`.**
5. **Using `latest` for the base image.**

## How This Shows Up in Production

Multi-stage separates build tools. `.dockerignore` shrinks the build context. Digest pins guarantee reproducibility. The container runs as a non-root user.

## How a Senior Engineer Thinks

- A Dockerfile deserves the same review as application code.
- Cache-friendly order *is* productivity.
- Secrets belong in build args or BuildKit secrets, not ENV.
- The base image is small and verified.
- Image scans are part of CI.

## Checklist

- [ ] Multi-stage in use.
- [ ] `.dockerignore` written.
- [ ] Non-root user.
- [ ] Digest pin in production.

## Practice Problems

1. Why must `COPY requirements` come before `COPY .`? Answer in one line.
2. Name one signature benefit of multi-stage builds.
3. Recommend one safe way to handle secrets in a Dockerfile.

## Wrap-up and Next Steps

Once images exist, the next question is *where to put state*. The next post covers Volume.

<!-- toc:begin -->
## In this series

- [What is a Container?](./01-what-is-a-container.md)
- [Image and Layer](./02-image-and-layer.md)
- [Runtime](./03-runtime.md)
- **Dockerfile (current)**
- Volume (upcoming)
- Network (upcoming)
- Registry (upcoming)
- Container Security (upcoming)
- Containers vs VMs (upcoming)
- Build a Container App (upcoming)

<!-- toc:end -->

## References

- [Dockerfile reference](https://docs.docker.com/engine/reference/builder/)
- [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [Dockerfile best practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [BuildKit secrets](https://docs.docker.com/build/building/secrets/)

Tags: Containers, Docker, Kubernetes, DevOps
