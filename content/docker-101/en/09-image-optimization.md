---
series: docker-101
episode: 9
title: "Docker 101 (9/10): Image Optimization"
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
  - Multistage
  - BuildKit
  - Alpine
  - Distroless
seo_description: Multi-stage builds, BuildKit cache mounts, and slim or distroless bases that cut image size and build time in half.
last_reviewed: '2026-05-15'
---

# Docker 101 (9/10): Image Optimization

Image optimization is often presented as an aesthetic preference for smaller numbers. In practice, image size changes deploy time, registry traffic, cache hit rates, and the number of unnecessary packages that become part of your attack surface.

The important point is that optimization is rarely one trick. Base image choice, multi-stage separation, and BuildKit cache reuse work together. If you optimize only one of them, the result is usually smaller than it should be.

This is the 9th post in the Docker 101 series. It walks through multi-stage builds, cache mounts, and base-image trade-offs so you can reason about build speed, runtime simplicity, and debugging cost at the same time.


![docker 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/09/09-01-concept-at-a-glance.en.png)
*docker 101 chapter 9 flow overview*

## Questions to Keep in Mind

- Multi-stage builds* to split *build vs runtime?
- BuildKit cache mounts* to *speed rebuilds?
- Comparing *slim / alpine / distroless?

## Why It Matters

Smaller images shorten *pull time = deploy time*. Cleaner images also reduce the *attack surface*.

> *A 1 GB image costs *one minute per deploy* and *100 points of security score*.*

## Key Terms

- **Multistage**: multiple *FROM* statements with only the *final image* shipped.
- **Cache mount**: a BuildKit *cache directory* mounted at build time.
- **Distroless**: a minimal image *without a shell*.
- **Layer squash**: merge layers into *one*.
- **`.dockerignore`**: shrink the *build context*.

## Before/After

**Before**: 1.2 GB image. 6-min build. 30-sec pull.

**After**: 80 MB image. 40-sec build (5 sec on cache hit). 3-sec pull.

## Hands-on: Optimization in 5 Steps

### Step 1 — Multistage Dockerfile

```dockerfile
# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip wheel --wheel-dir /wheels -r requirements.txt

FROM python:3.12-slim AS runtime
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links=/wheels /wheels/*.whl && rm -rf /wheels
COPY . .
RUN useradd -m -u 1000 appuser
USER appuser
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 2 — Enable BuildKit

```bash
DOCKER_BUILDKIT=1 docker build -t myapp:opt .
docker images myapp
```

### Step 3 — Compare bases

```text
python:3.12          ~1.0 GB
python:3.12-slim     ~150 MB
python:3.12-alpine   ~50 MB   (watch for musl compat)
gcr.io/distroless/python3-debian12  ~50 MB (no shell)
```

### Step 4 — Combine into one RUN

```dockerfile
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*
```

### Step 5 — Squash and dive

```bash
docker history myapp:opt
# Use 'dive' to analyze per-layer size
# https://github.com/wagoodman/dive
```

### Verify right after you run it

- Run the BuildKit build twice. The second build should show a clear cache advantage on dependency-related steps.
- Compare `docker images myapp` with `docker history myapp:opt` to confirm that builder-only tools stayed out of the runtime image.

### If it does not work, check this first

- If Alpine or distroless causes runtime issues, investigate compatibility and debugging constraints before chasing smaller size numbers.
- If the image barely shrinks, inspect `.dockerignore` and the copy boundary between builder and runtime stages.

## What to Notice in This Code

- A *wheels stage* keeps only the *compiled artifacts* in runtime.
- *Cache mount* reuses the pip cache.
- *Distroless* has *no shell*, so debugging is harder (trade-off).

## Five Common Mistakes

1. **Reaching for alpine *unconditionally*.** *musl* incompatibility causes *runtime errors*.
2. **Forgetting `--no-install-recommends`.** Image bloats by *tens of MB*.
3. **No cache cleanup after `apt-get install`.** Same problem.
4. **Build tools (`gcc`) left in *runtime*.** Larger attack surface.
5. **`COPY .` pulling in *gigabytes of context*.** Missing `.dockerignore`.

## How This Shows Up in Production

Build systems combine *BuildKit* with *registry caches* (e.g., GHA cache) to keep *PR builds under 30 seconds*. Security teams recommend *distroless / Chainguard*.

## How a Senior Engineer Thinks

- *Small images are not a virtue; they are a KPI*.
- *Multistage is the default*; single-stage is for demos.
- *Base image* is a *team-level decision*.
- *Unknown layers* are *attack surface*.
- *Audit periodically with dive*.

## Checklist

- [ ] *Multistage* splits build vs runtime.
- [ ] *BuildKit cache mounts* are used.
- [ ] Image < 200 MB.
- [ ] *.dockerignore* shrinks the build context.

## Practice Problems

1. Convert a Dockerfile to *multistage* and *halve* the image size.
2. Use a *cache mount* to drop build time to *one-fifth*.
3. Try a *distroless* base.

## Wrap-up and Next Steps

Small images lift *team velocity* and *security* at once. Next, the full *production deploy* configuration.

## Answering the Opening Questions

- **Why does a multi-stage build separate build from runtime?**
  - The first stage (`AS builder`) holds compilers, dev packages, and source code for building, then the second stage copies only the artifacts (binaries, wheels, dist folder) onto a lighter base via `COPY --from=builder`. Build tools never reach the final image — saving hundreds of MB and narrowing the attack surface significantly.
- **How does BuildKit cache mount speed up rebuilds?**
  - `RUN --mount=type=cache,target=/root/.cache/pip pip install ...` mounts the cache directory outside the layer, so even when layer cache breaks, pip/apt/go-mod download results are reused. The image stays clean while builds get faster — that's the point.
- **What are the trade-offs between slim, alpine, and distroless?**
  - `python:slim` uses glibc for maximum compatibility. `alpine` uses musl libc and apk for the smallest size but has some wheel compatibility issues. `distroless` removes even the shell and package manager for maximum security but makes debugging harder. It's a choice between "size reduction vs compatibility vs debugging convenience."

<!-- toc:begin -->
## In this series

- [Docker 101 (1/10): What Is Docker?](./01-what-is-docker.md)
- [Docker 101 (2/10): Images and Containers](./02-image-and-container.md)
- [Docker 101 (3/10): Writing a Dockerfile](./03-dockerfile.md)
- [Docker 101 (4/10): Volumes and Networks](./04-volume-and-network.md)
- [Docker 101 (5/10): Docker Compose](./05-docker-compose.md)
- [Docker 101 (6/10): Environment Variables and Configuration](./06-env-and-config.md)
- [Docker 101 (7/10): Containerizing a Python App](./07-python-app-containerize.md)
- [Docker 101 (8/10): Running with a Database](./08-database-with-app.md)
- **Image Optimization (current)**
- Production-Ready Docker (upcoming)

<!-- toc:end -->

## References

### Official docs

- [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [BuildKit cache mounts](https://docs.docker.com/build/cache/optimize/)
- [Distroless images](https://github.com/GoogleContainerTools/distroless)
- [dive - layer analysis](https://github.com/wagoodman/dive)

### Verification and troubleshooting

- [Optimize cache usage in builds](https://docs.docker.com/build/cache/optimize/)

Tags: Docker, Multistage, BuildKit, Alpine, Distroless
