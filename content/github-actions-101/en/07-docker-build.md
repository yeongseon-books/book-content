---
series: github-actions-101
episode: 7
title: Docker Build
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - GitHubActions
  - Docker
  - Buildx
  - GHCR
  - CICD
seo_description: Buildx, cache, multi-platform, and GHCR push. Build Docker images the standard way in CI without paying for slow rebuilds.
last_reviewed: '2026-05-04'
---

# Docker Build

> GitHub Actions 101 series (7/10)

<!-- a-grade-intro:begin -->

**Core question**: How do you build a *Docker image per PR* *fast and safely* and push it to a *registry*?

> *Docker builds* are *all about cache design*.

<!-- a-grade-intro:end -->

## What You Will Learn

- Enabling *Buildx* via *docker/setup-buildx-action*
- Cutting build time with the *gha cache*
- Logging in and pushing to *GHCR*
- *Multi-platform* (linux/amd64+arm64) builds
- Five common pitfalls

## Why It Matters

The *slowest CI step* is usually the *Docker build*. Done right (cache + multi-stage + Buildx), *minutes* become *seconds*.

> *Container standards* drive *deployment standards*.

## Concept at a Glance

```mermaid
flowchart LR
    Dockerfile["Dockerfile"] --> Buildx["docker/build-push-action"]
    Buildx --> Cache["gha cache"]
    Buildx --> GHCR["ghcr.io"]
```

## Key Terms

- **Buildx**: Docker's *advanced builder*.
- **gha cache**: GitHub Actions *cache backend*.
- **GHCR**: *GitHub Container Registry*.
- **Multi-platform**: building for *multiple CPU architectures*.
- **OCI image**: the *standard container image* format.

## Before/After

**Before**: every run *rebuilds all layers* — *4 minutes per PR*.

**After**: *gha cache + multi-stage* finishes in *30 seconds*.

## Hands-on: Docker Build in 5 Steps

### Step 1 — Set up Buildx

```yaml
- uses: docker/setup-qemu-action@v3
- uses: docker/setup-buildx-action@v3
```

### Step 2 — Log in to GHCR

```yaml
- uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

### Step 3 — Build and push with build-push-action

```yaml
- uses: docker/build-push-action@v6
  with:
    context: .
    push: true
    tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

### Step 4 — Multi-platform

```yaml
- uses: docker/build-push-action@v6
  with:
    platforms: linux/amd64,linux/arm64
    push: true
    tags: ghcr.io/${{ github.repository }}:latest
```

### Step 5 — Permissions (top-level)

```yaml
permissions:
  contents: read
  packages: write
```

## What to Notice in This Code

- *cache-to: gha, mode=max* maximizes *layer cache* reuse.
- *Multi-platform* roughly *doubles cost*.
- *GITHUB_TOKEN* needs *packages: write* permission.

## Five Common Mistakes

1. **No Buildx.** No *gha cache* available.
2. **Missing `permissions: packages: write`.** *push 401*.
3. **Pushing only *latest*.** No rollback.
4. **Building *multi-platform* on every PR.** Cost explodes.
5. **Single-stage Dockerfile.** Image grows to *hundreds of MB*.

## How This Shows Up in Production

Mature teams build *amd64 + cache only* on *PRs* and produce *signed (cosign) multi-platform* images on *main push*.

## How a Senior Engineer Thinks

- *Docker build time* equals *team patience*.
- *Cache strategy* drives *Dockerfile design*.
- *latest* is convenience; *pinned tags* are truth.
- Grant *permissions* minimally.
- *Sign* artifacts for *supply-chain security*.

## Checklist

- [ ] *Buildx + gha cache* are enabled.
- [ ] Both *pinned (sha)* and *latest* tags are pushed.
- [ ] *permissions: packages: write* is set.
- [ ] *Multi-platform* runs only on *needed triggers*.

## Practice Problems

1. Build *amd64 only* on PRs.
2. Push *multi-platform + latest* on *main push*.
3. Refactor your *Dockerfile* to *multi-stage* to cut image size in *half*.

## Wrap-up and Next Steps

Automating Docker builds is the *gateway to deployment automation*. Next: *Deployment automation*.

<!-- toc:begin -->
- [What Is GitHub Actions?](./01-what-is-github-actions.md)
- [Workflows and Jobs](./02-workflow-and-job.md)
- [Understanding Triggers](./03-triggers.md)
- [Python Test Automation](./04-python-test-automation.md)
- [Lint and Type Check](./05-lint-and-typecheck.md)
- [Build Artifacts](./06-build-artifact.md)
- **Docker Build (current)**
- Deployment Automation (upcoming)
- Secret Management (upcoming)
- A Real-World CI/CD Pipeline (upcoming)
<!-- toc:end -->

## References

- [docker/build-push-action](https://github.com/docker/build-push-action)
- [docker/setup-buildx-action](https://github.com/docker/setup-buildx-action)
- [GHCR documentation](https://docs.github.com/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Buildx GitHub Actions cache](https://docs.docker.com/build/ci/github-actions/cache/)

Tags: GitHubActions, Docker, Buildx, GHCR, CICD
