---
series: devops-101
episode: 6
title: "DevOps 101 (6/10): Containers and Build"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - DevOps
  - Docker
  - Container
  - Build
  - Image
seo_description: Write Dockerfiles, use multi-stage builds, and optimize images for lightweight, secure containers.
last_reviewed: '2026-05-15'
---

# DevOps 101 (6/10): Containers and Build

"It works on my laptop" is usually an environment problem wearing an application mask. If the runtime libraries, OS packages, and process entrypoints differ between local and production, deployment quality depends on luck more than engineering.

Containers reduce that gap by freezing the runtime environment into an image. Once the image becomes the deployable unit, teams can reason about versioning, rollback, and promotion much more cleanly.

This is the 6th post in the DevOps 101 series. Here we focus on how Dockerfiles, layer caching, multi-stage builds, and non-root execution turn containerization into a real operational advantage.


![devops 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/devops-101/06/06-01-concept-at-a-glance.en.png)
*devops 101 chapter 6 flow overview*
> Containers solve *"it works on my laptop"* by making the deployment unit *consistent* across every machine.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Containers and Build?
- Which signal should the example or diagram make visible for Containers and Build?
- What failure should be prevented first when Containers and Build reaches a real system?

## Questions this article answers

- How are *containers* different from *VMs*, and why do they improve deployment repeatability?
- Which basic *Dockerfile* instructions do you need to understand first?
- How do *multi-stage builds* change image size and security?
- Why does a *Dockerfile* that uses *layer caching* well also speed up development?
- What traps commonly appear when *container images* move into production?

## Why It Matters

The same build artifact must *behave the same* in *every environment*. Containers bundle *OS libraries, dependencies, and code* into *a single unit*.

> Containers realize *Build once, run anywhere*.

Containers package code and its *exact runtime* into one deployable unit. Build automation runs the same steps every time, so *"works on my laptop"* becomes impossible.

## Key Terms

- **Image**: an *immutable executable package*.
- **Container**: a running *instance of an image*.
- **Dockerfile**: an image *build recipe*.
- **Layer**: a *read-only stratum* per command.
- **Registry**: an image store (Docker Hub, ECR, etc.).

## Before/After

**Before (host-dependent)**

```bash
# Install directly on the server
apt install python3.12 postgresql-client
pip install -r requirements.txt
# On another server, *versions differ*
```

**After (Dockerfile)**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

## Hands-on: Five Dockerfile Steps

### Step 1 - Basic build

```bash
docker build -t myapp:1.0 .
docker run -p 8000:8000 myapp:1.0
```

### Step 2 - Optimize the layer cache

```dockerfile
COPY requirements.txt .          # rare changes -> cache reuse
RUN pip install -r requirements.txt
COPY . .                          # only the code changes often
```

### Step 3 - Shrink with multi-stage

```dockerfile
FROM python:3.12 AS builder
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.12-slim
COPY --from=builder /root/.local /root/.local
COPY . /app
WORKDIR /app
CMD ["python", "main.py"]
```

### Step 4 - Non-root user

```dockerfile
RUN useradd --create-home appuser
USER appuser
```

### Step 5 - Healthcheck

```dockerfile
HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1
```

## What to Notice in This Code

- Put commands with *low change frequency* *higher up*.
- Reduce the *attack surface* with *slim/distroless* images.
- *Non-root* is the *default*.

## Five Common Mistakes

1. **Using the `latest` tag.** *Not reproducible*. Always *pin a version*.
2. **`COPY . .` *at the start*.** Cache invalidation means *every build starts over*.
3. **Baking secrets *into the image*.** `docker history` *extracts* them.
4. **Running as root.** Container escape *risks the host*.
5. **Images over *1GB*.** *push/pull* gets slow and *cold starts* lengthen.

## How This Shows Up in Production

Mature teams wire *distroless* + *SBOM generation* + *image signing (cosign)* + *vulnerability scans (Trivy)* into the *CI pipeline*.

## How a Senior Engineer Thinks

- *Images are immutable*. Change = *new image*.
- *Smaller is safer*. Prefer distroless.
- *.dockerignore* matters as much as *.gitignore*.
- *Build speed* is *development speed*. Defend the cache.
- *Image signing* protects the *supply chain*.

## Checklist

- [ ] The *Dockerfile* ends as *non-root*.
- [ ] *Multi-stage* keeps the *final image* small.
- [ ] *.dockerignore* excludes *.git, tests, docs*.
- [ ] *Vulnerability scanning* is in CI.

## Practice Problems

1. Reduce your app's *final image size* to *under 200MB*.
2. Compare *build times* before and after applying *multi-stage*.
3. Audit *HIGH/CRITICAL* vulnerabilities with *Trivy*.

## Wrap-up and Next Steps

A container is *a frozen environment*. In the next post we cover how to *monitor* containers in production.

## Answering the Opening Questions

- **How do containers differ from VMs, and why are they advantageous for deployment reproducibility?**
  - In this article, containers bundle application and dependencies into an image more lightly than VMs (which require a full OS). Since the execution environment itself is captured as code starting from `FROM python:3.12-slim`, the reproducibility problems caused by differing server installation states are greatly reduced.
- **What basic Dockerfile commands must you understand?**
  - The article covers `FROM`, `WORKDIR`, `COPY`, `RUN`, `CMD` as the basic axis, adding `USER` and `HEALTHCHECK` for production quality. Particularly, the order of COPYing `requirements.txt` first and switching to a non-root user are key points affecting both build cache and security simultaneously.
- **What difference does multi-stage build make for image size and security?**
  - Installing dependencies in a builder stage and copying only execution results (like `/root/.local`) to the runtime stage removes unnecessary build tools from the final image. As shown in the comparison table, image size drops 50–70% easily, and the accompanying packages and attack surface shrink too, producing cleaner security scan results.
<!-- toc:begin -->
## In this series

- [DevOps 101 (1/10): What Is DevOps?](./01-what-is-devops.md)
- [DevOps 101 (2/10): CI Pipeline](./02-ci-pipeline.md)
- [DevOps 101 (3/10): CD and Deployment Strategies](./03-cd-and-deployment.md)
- [DevOps 101 (4/10): Environments and Configuration](./04-environments-and-config.md)
- [DevOps 101 (5/10): Infrastructure as Code](./05-infrastructure-as-code.md)
- **Containers and Build (current)**
- Monitoring and Alerting (upcoming)
- Logging and Analysis (upcoming)
- Incident Response and On-Call (upcoming)
- An Operable DevOps Flow (upcoming)

<!-- toc:end -->

## References

- [Docker docs](https://docs.docker.com/)
- [Distroless images](https://github.com/GoogleContainerTools/distroless)
- [Trivy](https://trivy.dev/)
- [Sigstore Cosign](https://docs.sigstore.dev/cosign/overview/)

Tags: DevOps, Docker, Container, Build, Image
