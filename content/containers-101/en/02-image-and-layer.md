---
series: containers-101
episode: 2
title: "Containers 101 (2/10): Image and Layer"
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
- Image
- Layer
- DevOps
seo_description: How container images split into layers, how OverlayFS stacks them,
  and how layer caching speeds up builds — with docker history examples.
last_reviewed: '2026-05-15'
---

# Containers 101 (2/10): Image and Layer

An image can look like one opaque artifact until build time starts to hurt. Then layer order, cache reuse, transfer size, and vulnerability surface suddenly become operational concerns instead of implementation detail.

This is the 2nd post in the Containers 101 series.

In this chapter, we unpack why images are split into layers, how OverlayFS makes the stack look like one filesystem, and why Dockerfile optimization and digest-based reproducibility both depend on that structure.

> Layers are the reason images can be reused, cached, and transferred efficiently at the same time.


![containers 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/containers-101/02/02-01-concept-at-a-glance.en.png)
*containers 101 chapter 2 flow overview*
> An image is not a single file; it is a stack of immutable layer snapshots. Each layer can be reused, cached, and transferred independently — that is why images are efficient.

## Questions to Keep in Mind

- The physical structure of an image?
- The job of a layer?
- How OverlayFS stacks them?

## Why It Matters

Without layers, you cannot optimize a Dockerfile. The difference between a 1-minute and a 30-second build comes from understanding how layers cache, share, and transfer independently. More importantly, layers determine your image's attack surface: each unnecessary layer adds files that may contain vulnerabilities, grow pull time, and increase registry costs.

Layers are read-only change sets. The bottom layers hold the base OS or runtime; upper layers add application dependencies. At runtime, an additional writable container layer is added on top so the base layers stay clean.

Layers are read-only change sets. The bottom layers hold the base OS or runtime; upper layers add application dependencies. At runtime, an additional writable container layer is added on top so the base layers stay clean.

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

`docker image inspect` reveals the full metadata including the ordered layer stack. Each layer hash in `RootFS.Layers` corresponds to one Dockerfile instruction that produced file changes.

### Step 2 — History

```python
def history(image):
    res = subprocess.run(
        ["docker", "history", "--no-trunc", image],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

`docker history` traces the command behind each layer and its size contribution. This is how you identify which instruction bloated the image or broke the cache.

### Step 3 — Layer hashes

```python
def layer_sizes(image):
    data = inspect(image)
    return [layer for layer in data[0]["RootFS"]["Layers"]]
```

The layer hash list is what Docker uses to decide cache hits. Two images sharing the same lower layers only transfer the differing upper layers during pull—the deduplication that makes container registries efficient.

### Step 4 — Digest

```python
def digest(image):
    return inspect(image)[0]["Id"]
```

The digest (`sha256:...`) is the content-addressable identity. Unlike mutable tags (`latest`, `v1.0`), a digest guarantees byte-for-byte equality. Use digests in production deployments to prevent silent image mutation.

### Step 5 — Compare two builds

```python
def diff(a, b):
    return set(layer_sizes(a)) ^ set(layer_sizes(b))
```

Comparing layer sets between two builds instantly shows which instruction changed. If only the top layer differs, your cache strategy is working. If many layers differ, the Dockerfile ordering needs review.

## What to Notice in This Code

- `RootFS.Layers` are the actual layer hashes.
- `history` traces the command behind each layer.
- The digest guarantees content equality.

## Quick verification and failure signals

```bash
docker pull python:3.12-slim
docker image inspect python:3.12-slim --format "{{json .RootFS.Layers}}"
docker history python:3.12-slim
docker inspect --format "{{index .RepoDigests 0}}" python:3.12-slim
```

**Expected output:**
- `RootFS.Layers` prints an ordered array of layer hashes.
- `docker history` shows the commands and sizes behind the layers.
- `RepoDigests` gives you the immutable identity after push.

**Check first if it fails:**
- If layer count grows too quickly, review how the Dockerfile splits `RUN`.
- If the digest is empty, confirm you are inspecting a pushed image.
- If the image is too large, inspect build context size and multi-stage usage first.

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

## Answering the Opening Questions

- **What exactly does a single layer do?**
  - Each Dockerfile instruction (`RUN`, `COPY`, `ADD`) creates one read-only change layer. It only contains files that differ from the previous layer, so there is no data duplication. You can verify each layer's source instruction and size with `docker history`.
- **How can you tell why the cache broke?**
  - Docker compares whether each layer's input (instruction + context files) matches the previous build. If `COPY . .` sits above app code, a one-line code change forces every layer below it to re-execute. That's why the article emphasized placing less-frequently-changing items lower and frequently-changing items higher.
- **How does OverlayFS make these layers appear merged?**
  - OverlayFS combines lowerdir (the read-only layer stack) and upperdir (the container's writable layer) into a single visible filesystem. Reads search top-down, writes always go to upperdir. Deletes are marked with whiteout files, so the actual layer originals remain unchanged.
<!-- toc:begin -->
## In this series

- [Containers 101 (1/10): What is a Container?](./01-what-is-a-container.md)
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

Tags: Containers, Docker, Kubernetes, DevOps
