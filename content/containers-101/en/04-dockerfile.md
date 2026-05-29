---
series: containers-101
episode: 4
title: "Containers 101 (4/10): Dockerfile"
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

# Containers 101 (4/10): Dockerfile

A Dockerfile is not just a text file that happens to build an image. Instruction order changes cache hit rate, base-image choice changes image size and CVE count, and one user directive can change the security posture of the runtime.

This is the 4th post in the Containers 101 series.

In this chapter, we focus on cache-friendly instruction order, multi-stage builds, non-root defaults, and secret handling so the resulting image is faster, smaller, and safer to ship.

> Dockerfile quality is really cache quality, image quality, and runtime safety compressed into one file.


![containers 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/containers-101/04/04-01-concept-at-a-glance.en.png)
*containers 101 chapter 4 flow overview*
> The quality of a Dockerfile lives or dies by cache efficiency. Change a layer deep in the file, and you rebuild everything below it.

## Questions to Keep in Mind

- The role and order of instructions?
- Cache-friendly authoring?
- Multi-stage builds?

## Why It Matters

A Dockerfile directly drives team productivity and security. A poorly ordered Dockerfile means every code change triggers a full dependency reinstall (minutes wasted per build, multiplied by every developer and CI run). A missing `USER` directive means every container runs as root—one exploit away from host compromise. Get it right once and it pays back for years.

Each Dockerfile instruction creates one layer. Layers below are cached if their inputs match; changes above invalidate everything below. Multi-stage builds let you discard build artifacts before the final layer.

Each Dockerfile instruction creates one layer. Layers below are cached if their inputs match; changes above invalidate everything below. Multi-stage builds let you discard build artifacts before the final layer.

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

The `FROM` instruction sets the base image and names the build stage. Choosing `python:3.12-slim` over the full image saves ~600MB and reduces CVE surface. The stage name (`AS builder`) enables multi-stage referencing later.

### Step 2 — Dependencies first

```python
def deps_stage():
    return [
        "COPY requirements.txt .",
        "RUN pip install --user -r requirements.txt",
    ]
```

Copying `requirements.txt` before the application code is the single most impactful cache optimization. Since dependencies change rarely, this layer stays cached across most builds—only a requirements change triggers a reinstall.

### Step 3 — Code

```python
def code_stage():
    return [
        "COPY . .",
    ]
```

`COPY . .` brings in the actual application code. Because it sits after the dependency layer, a code-only change rebuilds only this layer and below—not the expensive `pip install` step.

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

The runtime stage starts from a fresh slim image. `COPY --from=builder` pulls only the installed packages and app code, leaving behind compilers, headers, and build cache. This is what drops image size from 900MB to ~80MB.

### Step 5 — Non-root and run

```python
def finalize():
    return [
        "RUN useradd -m app && chown -R app:app /app",
        "USER app",
        "CMD [\"python\", \"main.py\"]",
    ]
```

Creating a non-root user and switching to it with `USER app` means the container process cannot write to system paths even if compromised. This one line eliminates an entire class of container-escape vulnerabilities.

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

## Answering the Opening Questions

- **Why does Dockerfile instruction order matter so much?**
  - Docker creates each instruction as a layer, and if earlier layers cache-hit, subsequent instructions can be skipped entirely. Conversely, if one earlier instruction's input changes, every layer after it must be rebuilt. Therefore placing low-change-frequency instructions (base image, dependency install) above and frequently-changing instructions (source code copy) below is the core principle for reducing build time.
- **How does a cache-friendly writing style change build time?**
  - Copy source code last and install dependencies first. With this pattern, builds that only modify code can reuse the entire dependency layer, commonly reducing CI build time from 5 minutes to 30 seconds. In large monorepos, this difference accumulates across dozens of daily builds.
- **What problem does multi-stage build solve?**
  - It extracts only the final artifacts from a large build image containing build tools (gcc, npm, pytest, etc.) and moves them to a small runtime image. When a 900MB image shrinks to 80MB, transfer time, storage cost, and vulnerability surface area all improve.
<!-- toc:begin -->
## In this series

- [Containers 101 (1/10): What is a Container?](./01-what-is-a-container.md)
- [Containers 101 (2/10): Image and Layer](./02-image-and-layer.md)
- [Containers 101 (3/10): Runtime](./03-runtime.md)
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
