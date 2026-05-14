---
series: containers-101
episode: 2
title: Image and Layer
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Containers
  - Docker
  - Image
  - Layer
  - DevOps
seo_description: How container images split into layers, how OverlayFS stacks them, and how layer caching speeds up builds — with docker history examples.
last_reviewed: '2026-05-04'
---

# Image and Layer

> Containers 101 series (2/10)

<!-- a-grade-intro:begin -->

**Core question**: Why are images split into *layers* in the first place?

> *Layered images give you reuse, caching, and small transfers all at once — they are the central design of containers.*

<!-- a-grade-intro:end -->

This is post 2 in the Containers 101 series.

## What You Will Learn

- The physical structure of an image
- The job of a layer
- How OverlayFS stacks them
- Layer caching for fast builds
- Five common pitfalls

## Why It Matters

Without layers, you cannot really optimize a Dockerfile. The difference between a 1-minute and a 30-second build comes from understanding this.

## Concept at a Glance

```mermaid
flowchart LR
    Base["base layer (os)"] --> Lib["lib layer"]
    Lib --> Code["app code"]
    Code --> Container["container (rw layer)"]
```

## Key Terms

- **Layer**: a read-only bundle of changes.
- **Base image**: the OS or runtime layer at the bottom.
- **OverlayFS**: a filesystem that stacks layers visually.
- **Manifest**: the index metadata of an image.
- **Digest**: the content hash of an image.

## Before/After

**Before**: a single source change rebuilds the whole image.

**After**: only the upper layers rebuild — seconds, not minutes.

## Hands-on: Look Inside an Image

### Step 1 — Pull and inspect

```python
import subprocess, json

def inspect(image):
    res = subprocess.run(
        ["docker", "image", "inspect", image],
        capture_output=True, text=True, check=True,
    )
    return json.loads(res.stdout)
```

### Step 2 — History

```python
def history(image):
    res = subprocess.run(
        ["docker", "history", "--no-trunc", image],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

### Step 3 — Layer hashes

```python
def layer_sizes(image):
    data = inspect(image)
    return [layer for layer in data[0]["RootFS"]["Layers"]]
```

### Step 4 — Digest

```python
def digest(image):
    return inspect(image)[0]["Id"]
```

### Step 5 — Compare two builds

```python
def diff(a, b):
    return set(layer_sizes(a)) ^ set(layer_sizes(b))
```

## What to Notice in This Code

- `RootFS.Layers` are the actual layer hashes.
- `history` traces the command behind each layer.
- The digest guarantees content equality.

## Five Common Mistakes

1. **Splitting commands across many RUN statements — layer explosion.**
2. **`COPY .` pulling in junk you did not mean to ship.**
3. **Splitting `apt update` from `apt install` — cache invalidates.**
4. **Shipping huge build artifacts in the final image.**
5. **Tagging `latest` and losing reproducibility.**

## How This Shows Up in Production

Multi-stage builds split build tools from runtime. `.dockerignore` keeps the build context tiny. Digest pins guarantee reproducibility.

## How a Senior Engineer Thinks

- Stable instructions go on top, volatile ones at the bottom.
- Multi-stage is the default pattern.
- `latest` is a landmine.
- `.dockerignore` matters as much as the Dockerfile.
- Image size equals attack surface.

## Checklist

- [ ] Multi-stage build in use.
- [ ] `.dockerignore` present.
- [ ] Digest pins in production.
- [ ] Image scanning enabled.

## Practice Problems

1. Name the most common reason layer caching breaks, in one line.
2. Give one scenario where multi-stage builds clearly win.
3. Explain the difference between an image digest and a tag in one line.

## Wrap-up and Next Steps

You can see how an image is built. Next, look at what runs it. The next post covers Runtime.

<!-- toc:begin -->
- [What is a Container?](./01-what-is-a-container.md)
- **Image and Layer (current)**
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

- [Docker — about storage drivers](https://docs.docker.com/storage/storagedriver/)
- [OverlayFS](https://docs.kernel.org/filesystems/overlayfs.html)
- [OCI Image Spec — manifest](https://github.com/opencontainers/image-spec/blob/main/manifest.md)
- [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)

Tags: Containers, Docker, Image, Layer, DevOps
