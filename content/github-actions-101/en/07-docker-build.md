---
series: github-actions-101
episode: 7
title: "GitHub Actions 101 (7/10): Docker Build"
status: content-ready
targets:
  tistory: false
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
last_reviewed: '2026-05-15'
---

# GitHub Actions 101 (7/10): Docker Build

Docker build is usually the slowest and most failure-prone stage in a GitHub Actions pipeline. Without cache, every PR rebuilds layers from scratch. Without a tag policy, you lose traceability. Without the right permissions, the build succeeds only to fail at the final push with a 401.

That is why container automation is not just “run `docker build` in CI.” It is a design problem that combines Buildx, cache layout, registry authentication, and branch-specific push policy.

This is the 7th post in the GitHub Actions 101 series. In this post, we will build a practical Docker workflow around Buildx, GitHub Actions cache, GHCR authentication, multi-platform builds, and tagging strategy.


![github actions 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/07/07-01-concept-at-a-glance.en.png)
*github actions 101 chapter 7 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Docker Build?
- Which signal should the example or diagram make visible for Docker Build?
- What failure should be prevented first when Docker Build reaches a real system?

## What You Will Learn

- Enabling *Buildx* via *docker/setup-buildx-action*
- Cutting build time with the *gha cache*
- Logging in and pushing to *GHCR*
- *Multi-platform* (linux/amd64+arm64) builds
- Five common pitfalls

## Why It Matters

The *slowest CI step* is usually the *Docker build*. Done right (cache + multi-stage + Buildx), *minutes* become *seconds*.

> *Container standards* drive *deployment standards*.

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

## What success looks like at this point

```text
#17 [linux/amd64] exporting to image
#17 exporting manifest sha256:8f4c...
#17 naming to ghcr.io/acme/demo:4d2e9f1
#17 DONE 2.1s
```

If you see a digest plus the expected tag, the minimum contract is working. In PR validation runs, even when `push: false`, the logs should still tell you whether cache hit, which layers rebuilt, and how expensive the workflow will be once the repository gets busier.

## If the build fails, check these first

- **401 or permission denied**: confirm `permissions: packages: write` is present and the repository is allowed to publish to the target GHCR package.
- **Cache never hits**: check whether frequently changing files are copied too early in the Dockerfile. Layer order usually explains the miss.
- **Only multi-platform builds are slow or flaky**: keep PR runs to amd64 only, then reserve arm64 for `main` or release tags.

## Use a different branch policy from your release policy

On pull requests, I usually build with `push: false` so the job validates the Dockerfile and cache path without publishing images for every review iteration. On `main`, I push a pinned `sha` tag and, if the repository really needs it, a convenience `latest` tag. On release tags, I expand to multi-platform output and signing. That split keeps feedback fast without giving up rollback discipline.

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

## Answering the Opening Questions

- **Why is Buildx used more often than the regular builder?**
  - Buildx supports multi-platform builds, advanced cache backends (gha, registry), and parallel build stage execution. Regular `docker build` suffices for local builds, but when CI needs cache optimization and multi-architecture support, Buildx becomes essential. One line with `docker/setup-buildx-action` sets it up.
- **How does GitHub Actions cache affect Docker layer build time?**
  - Setting `cache-from: type=gha` reuses previous build layers, skipping unchanged layer rebuilds. When the dependency install layer is cached, build time drops from minutes to seconds. `mode=max` caches all stages for maximum effect in multi-stage builds.
- **What permissions are needed when pushing to GHCR?**
  - Set `permissions: packages: write` at job level and login via `docker/login-action` with `GITHUB_TOKEN`. Works without separate PATs; image names must be lowercase. On PRs, the typical pattern is build verification only without pushing.
<!-- toc:begin -->
## In this series

- [GitHub Actions 101 (1/10): What Is GitHub Actions?](./01-what-is-github-actions.md)
- [GitHub Actions 101 (2/10): Workflows and Jobs](./02-workflow-and-job.md)
- [GitHub Actions 101 (3/10): Understanding Triggers](./03-triggers.md)
- [GitHub Actions 101 (4/10): Python Test Automation](./04-python-test-automation.md)
- [GitHub Actions 101 (5/10): Lint and Type Check](./05-lint-and-typecheck.md)
- [GitHub Actions 101 (6/10): Build Artifacts](./06-build-artifact.md)
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
