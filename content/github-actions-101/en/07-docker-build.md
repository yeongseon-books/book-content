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

That is why container automation is not just "run `docker build` in CI." It is a design problem that combines Buildx, cache layout, registry authentication, and branch-specific push policy.

This is the 7th post in the GitHub Actions 101 series. In this post, we will build a practical Docker workflow around Buildx, GitHub Actions cache, GHCR authentication, multi-platform builds, and tagging strategy.

![github actions 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/07/07-01-concept-at-a-glance.en.png)
*github actions 101 chapter 7 flow overview*

## Questions to Keep in Mind

- Why is Buildx used more often than the regular builder?
- How does GitHub Actions cache affect Docker layer build time?
- What permissions are needed when pushing to GHCR?

## Why It Matters

Container images are the deployment boundary. Regardless of what application code looks like, deployment often happens at the image level. If builds are slow or hard to reproduce, deployments become unstable.

Docker builds also directly affect CI costs. A pipeline that rebuilds all layers every time quickly becomes slow, and developers stop wanting to wait for check results. The core of Docker build automation is not "make it fast" but "make it predictable." Cache and tag strategies create that predictability.

## Docker Build Flow at a Glance

At the center of this structure is `docker/build-push-action`. It takes a Dockerfile as input, builds it, leverages cache, and pushes the result to a registry — all in one step.

## Key Terms

| Term | Meaning | Practical Point |
| --- | --- | --- |
| Buildx | Docker's extended builder | Central to cache, multi-platform, and advanced build features |
| gha cache | GitHub Actions cache backend | Reduces build time through layer reuse |
| GHCR | GitHub Container Registry | Natural image distribution within the GitHub ecosystem |
| Multi-platform | Building images for multiple CPU architectures | Expands compatibility but increases cost |
| OCI image | Standard container image format | Compatible across various runtimes and registries |

## Before and After

A build without cache rebuilds every layer on each PR. Dependency installation, system packages, application copy — all repeated from scratch, easily consuming 4-5 minutes. This kind of pipeline scales poorly; even modest repository growth multiplies team wait time.

With Buildx and `type=gha` cache, unchanged layers are reused as-is. When the Dockerfile is structured with multi-stage builds, build time drops significantly and image size shrinks too. I always look at these two things together in Docker build automation.

## Docker Build in 5 Steps

### Step 1 — Set Up Buildx

```yaml
- uses: docker/setup-qemu-action@v3
- uses: docker/setup-buildx-action@v3
```

This step lays the foundation for advanced build features. If multi-platform is on the roadmap, QEMU and Buildx setup is the starting point.

### Step 2 — Log In to GHCR

```yaml
- uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

Pushing images requires authentication. When using the GitHub repository and registry together, the `GITHUB_TOKEN` combination is the default starting point.

### Step 3 — Build and Push with Cache

```yaml
- uses: docker/build-push-action@v6
  with:
    context: .
    push: true
    tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

The key here is designing tags and cache together. The `github.sha` tag provides traceability; `cache-from` and `cache-to` reduce build time.

### Step 4 — Multi-Platform Images

```yaml
- uses: docker/build-push-action@v6
  with:
    platforms: linux/amd64,linux/arm64
    push: true
    tags: ghcr.io/${{ github.repository }}:latest
```

Multi-platform is convenient but not free. Running it on every PR is generally avoided — it belongs on main push or release tag triggers.

### Step 5 — Declare Permissions

```yaml
permissions:
  contents: read
  packages: write
```

Pushing images requires package write permission. Without this setting, the build succeeds but the final push fails with 401 — a frustrating pattern to encounter.

## What Success Looks Like

```text
#17 [linux/amd64] exporting to image
#17 exporting manifest sha256:8f4c...
#17 naming to ghcr.io/acme/demo:4d2e9f1
#17 DONE 2.1s
```

If you see a digest plus the expected tag, the minimum contract is working. In PR validation runs, even when `push: false`, the logs should still tell you whether cache hit, which layers rebuilt, and how expensive the workflow will be once the repository gets busier.

## If the Build Fails, Check These First

- **401 or permission denied**: Confirm `permissions: packages: write` is present and the repository is allowed to publish to the target GHCR package.
- **Cache never hits**: Check whether frequently changing files are copied too early in the Dockerfile. Layer order usually explains the miss.
- **Only multi-platform builds are slow or flaky**: Keep PR runs to amd64 only, then reserve arm64 for `main` or release tags.

## Use a Different Branch Policy from Your Release Policy

On pull requests, I usually build with `push: false` so the job validates the Dockerfile and cache path without publishing images for every review iteration. On `main`, I push a pinned `sha` tag and, if the repository really needs it, a convenience `latest` tag. On release tags, I expand to multi-platform output and signing. That split keeps feedback fast without giving up rollback discipline.

## What to Notice in This Code

- `cache-to: type=gha,mode=max` maximizes layer cache reuse.
- Multi-platform builds roughly double the cost.
- `GITHUB_TOKEN` needs `packages: write` permission.

In other words, Docker build automation is not just a Dockerfile problem — it is a design problem where permissions, cache, and tag policy are intertwined.

## Five Common Mistakes

1. **No Buildx.** No gha cache available.
2. **Missing `permissions: packages: write`.** Push fails with 401.
3. **Pushing only `latest`.** No rollback reference.
4. **Building multi-platform on every PR.** Cost explodes.
5. **Single-stage Dockerfile.** Image grows to hundreds of MB.

Mistake 3 especially hurts post-incident traceability. A pinned tag identifying the exact commit must always accompany the image.

## How Mature Teams Operate

Mature teams run amd64 + cache-only fast validation on PRs, and produce signed multi-platform images on main push or tag. Not every situation warrants the same weight of container build.

The `latest` tag is a convenience label, not a source of truth. Actual deployment tracking and rollback should rely on fixed identifiers like SHA or version tags.

## Checklist

- [ ] Buildx and gha cache are enabled.
- [ ] Both pinned (sha) and `latest` tags are managed.
- [ ] `permissions: packages: write` is set.
- [ ] Multi-platform runs only on needed triggers.

## Practice Problems

1. Build amd64 only on PRs.
2. Push multi-platform + `latest` on main push.
3. Refactor your Dockerfile to multi-stage to cut image size in half.

## Dockerfile Optimization and CI Build Time

To reduce Docker build time in CI, the Dockerfile itself must be CI-friendly. For layer cache to work effectively, layers that change infrequently belong at the top and frequently-changing layers at the bottom.

### Cache-Efficient Dockerfile Pattern

```dockerfile
# Stage 1: Dependencies (changes infrequently)
FROM python:3.12-slim AS deps
WORKDIR /app
COPY requirements.lock ./
RUN pip install --no-cache-dir -r requirements.lock

# Stage 2: Application copy (changes frequently)
FROM deps AS app
COPY src/ ./src/
COPY pyproject.toml ./

# Stage 3: Final image (minimized)
FROM python:3.12-slim AS runtime
WORKDIR /app
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=app /app/src ./src
USER 1000:1000
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Design points of this multi-stage build:

- **Dependency layer separation**: When `requirements.lock` does not change, the pip install layer is cached. If only source code changes, this layer is reused, dramatically cutting build time.
- **Multi-stage**: Build tools and dev dependencies are excluded from the final image, reducing size.
- **Non-root user**: Runs as non-root for security.

---

## Buildx Cache Strategy Deep Dive

There are several ways to leverage Docker layer cache in GitHub Actions. Comparing the trade-offs:

### GitHub Actions Cache (gha) Backend

```yaml
- uses: docker/build-push-action@v6
  with:
    context: .
    push: true
    tags: ghcr.io/${{ github.repository }}:latest
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

`mode=max` caches layers from all build stages. The default `mode=min` caches only final image layers, so for multi-stage builds, `max` provides higher cache hit rates.

### Registry Cache

```yaml
- uses: docker/build-push-action@v6
  with:
    context: .
    push: true
    tags: ghcr.io/${{ github.repository }}:latest
    cache-from: type=registry,ref=ghcr.io/${{ github.repository }}:cache
    cache-to: type=registry,ref=ghcr.io/${{ github.repository }}:cache,mode=max
```

Registry cache is not subject to GitHub Actions Cache's 10GB limit and is accessible from other CI systems. However, since cache travels over the network, the first build may be slower than gha.

### Cache Strategy Comparison

| Strategy | Speed | Size Limit | Sharing Scope |
| --- | --- | --- | --- |
| gha (GitHub Actions) | Fast | 10 GB | Same repository |
| registry | Medium | Registry limits | Entire organization |
| local | Fastest | Runner disk | Not possible (runner is ephemeral) |

Most projects should start with `gha` and switch to registry when cache size becomes insufficient.

---

## Tag Strategy and Image Traceability

Docker image tags are central to tracking "which code is in this image."

```yaml
- uses: docker/metadata-action@v5
  id: meta
  with:
    images: ghcr.io/${{ github.repository }}
    tags: |
      type=ref,event=branch
      type=ref,event=pr
      type=semver,pattern={{version}}
      type=semver,pattern={{major}}.{{minor}}
      type=sha,prefix=,format=short

- uses: docker/build-push-action@v6
  with:
    context: .
    push: ${{ github.event_name != 'pull_request' }}
    tags: ${{ steps.meta.outputs.tags }}
    labels: ${{ steps.meta.outputs.labels }}
```

`docker/metadata-action` automatically generates appropriate tags based on event type:

| Event | Generated Tags Example |
| --- | --- |
| main push | `main`, `sha-a1b2c3d` |
| PR #42 | `pr-42` |
| v1.2.3 tag | `1.2.3`, `1.2`, `sha-a1b2c3d` |

On PRs, `push: false` builds the image without pushing to the registry. Only build success is verified.

---

## GHCR Permission Setup

Pushing images to GitHub Container Registry requires proper permission configuration.

```yaml
jobs:
  docker:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v6

      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - uses: docker/setup-buildx-action@v3

      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
```

Key points:

- `permissions: packages: write` is required. If default permission is `read`, push fails.
- `GITHUB_TOKEN` is automatically provided — no separate PAT needed.
- Image names must be lowercase. If the repository name contains uppercase letters, convert `${{ github.repository }}` to lowercase.

```yaml
- name: Convert repo name to lowercase
  id: repo
  run: echo "name=$(echo ${{ github.repository }} | tr '[:upper:]' '[:lower:]')" >> "$GITHUB_OUTPUT"
```

---

## Image Security Scanning

Checking built images for known vulnerabilities is an important CI responsibility.

```yaml
- name: Build image
  uses: docker/build-push-action@v6
  with:
    context: .
    load: true
    tags: app:scan

- name: Security scan
  uses: aquasecurity/trivy-action@0.28.0
  with:
    image-ref: app:scan
    format: sarif
    output: trivy-results.sarif
    severity: CRITICAL,HIGH

- name: Upload scan results
  uses: github/codeql-action/upload-sarif@v3
  if: always()
  with:
    sarif_file: trivy-results.sarif
```

`load: true` loads the image into the local Docker daemon (without pushing). The structure pushes only after scanning confirms no issues.

Uploading Trivy's SARIF output to GitHub Code Scanning makes vulnerabilities visible in the PR's Security tab. Limiting severity to `CRITICAL,HIGH` filters to issues requiring immediate action.

---

## Multi-Platform Builds

To produce images that work on ARM servers or Apple Silicon Macs, multi-platform builds are needed.

```yaml
- uses: docker/setup-qemu-action@v3

- uses: docker/setup-buildx-action@v3

- uses: docker/build-push-action@v6
  with:
    context: .
    platforms: linux/amd64,linux/arm64
    push: true
    tags: ghcr.io/${{ github.repository }}:latest
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

QEMU emulation is 2-5x slower than native builds. When build time matters, use ARM native runners or build per-platform in separate jobs and merge with a manifest:

```yaml
jobs:
  build-amd64:
    runs-on: ubuntu-latest
    steps:
      - uses: docker/build-push-action@v6
        with:
          platforms: linux/amd64
          ...

  build-arm64:
    runs-on: ubuntu-24.04-arm
    steps:
      - uses: docker/build-push-action@v6
        with:
          platforms: linux/arm64
          ...

  manifest:
    needs: [build-amd64, build-arm64]
    runs-on: ubuntu-latest
    steps:
      - run: |
          docker manifest create ghcr.io/org/app:latest \
            ghcr.io/org/app:amd64 \
            ghcr.io/org/app:arm64
          docker manifest push ghcr.io/org/app:latest
```

---

## Docker Compose Integration Tests

A pattern for running integration tests alongside Docker builds. Spin up the application and dependencies (DB, Redis) together for tests close to the real environment.

```yaml
jobs:
  integration-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - name: Start services
        run: docker compose -f docker-compose.test.yml up -d

      - name: Wait for readiness
        run: |
          timeout 60 bash -c 'until curl -s http://localhost:8000/health; do sleep 2; done'

      - name: Run integration tests
        run: |
          docker compose -f docker-compose.test.yml exec -T app pytest tests/integration -q

      - name: Collect logs
        if: failure()
        run: docker compose -f docker-compose.test.yml logs > docker-logs.txt

      - uses: actions/upload-artifact@v7
        if: failure()
        with:
          name: docker-logs
          path: docker-logs.txt
          retention-days: 3

      - name: Cleanup
        if: always()
        run: docker compose -f docker-compose.test.yml down -v
```

`if: failure()` collects logs only on failure and saves them as artifacts. On success, no unnecessary files are created, saving storage.

---

## Image Size Monitoring

Growing image sizes affect deployment time and storage costs. Monitoring in CI:

```yaml
- name: Check image size
  run: |
    SIZE=$(docker image inspect app:latest --format='{{.Size}}')
    SIZE_MB=$((SIZE / 1024 / 1024))
    echo "Image size: ${SIZE_MB} MB"

    # Warn on threshold
    if [ "$SIZE_MB" -gt 500 ]; then
      echo "::warning::Image size exceeds 500MB (${SIZE_MB}MB)"
    fi

    # Fail on hard limit
    if [ "$SIZE_MB" -gt 1000 ]; then
      echo "::error::Image size exceeds 1GB limit (${SIZE_MB}MB)"
      exit 1
    fi
```

`::warning::` and `::error::` are GitHub Actions workflow commands that display warnings and errors in PR checks. They catch gradual image growth early.

Common image size reduction techniques:

| Technique | Effect |
| --- | --- |
| slim/alpine base image | 50-80% reduction |
| Multi-stage build | Excludes build tools |
| .dockerignore | Excludes unnecessary files |
| pip --no-cache-dir | Excludes pip cache |
| Layer merging (RUN chaining) | Removes intermediate files |

---

## Docker Security Best Practices in CI

```yaml
jobs:
  docker-security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - name: Dockerfile lint
        uses: hadolint/hadolint-action@v3.1.0
        with:
          dockerfile: Dockerfile

      - name: Build
        uses: docker/build-push-action@v6
        with:
          context: .
          load: true
          tags: app:security-check

      - name: Vulnerability scan
        uses: aquasecurity/trivy-action@0.28.0
        with:
          image-ref: app:security-check
          severity: CRITICAL,HIGH
          exit-code: 1

      - name: Generate SBOM
        uses: anchore/sbom-action@v0
        with:
          image: app:security-check
          output-file: sbom.spdx.json
```

This workflow performs three layers of security verification:

1. **Hadolint**: Checks Dockerfile best-practice violations (root usage, latest tags, unnecessary packages).
2. **Trivy**: Finds known vulnerabilities in OS packages and language dependencies of the built image.
3. **SBOM**: Generates a software bill of materials to support supply-chain security.

Setting `exit-code: 1` fails the job when CRITICAL/HIGH vulnerabilities are found, preventing vulnerable images from reaching deployment.

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
- [Trivy](https://github.com/aquasecurity/trivy)

Tags: GitHubActions, Docker, Buildx, GHCR, CICD
