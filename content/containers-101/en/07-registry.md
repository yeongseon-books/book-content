---
series: containers-101
episode: 7
title: "Containers 101 (7/10): Registry"
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
- Registry
- ECR
- DevOps
seo_description: A beginner guide to container registries (Docker Hub, ECR, GHCR),
  push and pull flow, tagging strategy, and signed images with Cosign
last_reviewed: '2026-05-15'
---

# Containers 101 (7/10): Registry

A well-built image is still useless if no one can pull the exact same artifact back later. Teams usually feel this when tags drift, push permissions are too broad, or deployment history can no longer prove what actually ran.

This is post 7 in the Containers 101 series.

In this chapter, we treat the registry as the center of deployment identity, covering push and pull flow, digest pinning, permission separation, and the first steps toward image signing.

> A registry is not just storage. It is the identity system for what actually gets deployed.


![containers 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/containers-101/07/07-01-concept-at-a-glance.en.png)
*containers 101 chapter 7 flow overview*
> A registry is not a backup folder; it is the distribution contract that binds tags, digests, manifests, and policy into one reproducible handoff.

## Questions to Keep in Mind

- The role of a *registry?
- The *push / pull* flow?
- Tagging* strategy?

## Why It Matters

A reproducible image is useless if there is *no place to fetch it from*. *Deployment starts at the registry.*

Tags are human-friendly labels; digests are content-based hashes. The same tag can point to different digests over time, but a digest always refers to the exact same bytes. Private registries add authentication and network isolation; public ones rely on image content and scanning.

## Key Terms

- **registry**: an *image storage server*.
- **repository**: a unit that holds *one image name*.
- **tag**: a *human label* for a version.
- **digest**: an *immutable* SHA identifier.
- **signed image**: an image *signed by Cosign* or similar.

## Before / After

**Before**: shipping images by *USB or scp* leads to *drift*.

**After**: a *registry* with *digests* guarantees *identity*.

## Hands-on: Automate an Image Push

### Step 1 — Login

```python
import subprocess

def login(registry, user, password):
    subprocess.run(
        ["docker", "login", registry, "-u", user, "--password-stdin"],
        input=password.encode(), check=True,
    )
```

### Step 2 — Tag

```python
def tag(local, remote):
    subprocess.run(["docker", "tag", local, remote], check=True)
```

### Step 3 — Push

```python
def push(remote):
    subprocess.run(["docker", "push", remote], check=True)
```

### Step 4 — Read the digest

```python
def digest(remote):
    res = subprocess.run(
        ["docker", "inspect", "--format={{index .RepoDigests 0}}", remote],
        capture_output=True, text=True, check=True,
    )
    return res.stdout.strip()
```

### Step 5 — Verify with pull

```python
def verify_pull(remote_digest):
    subprocess.run(["docker", "pull", remote_digest], check=True)
```

## What to Notice in This Code

- We pin by *digest*, not tag.
- *password-stdin* avoids leaking secrets.
- Push happens *after role separation* only.

## Quick verification and failure signals

```bash
docker login ghcr.io -u "$GITHUB_USER" --password-stdin
docker tag myapp:dev ghcr.io/example/myapp:1.0.0
docker push ghcr.io/example/myapp:1.0.0
docker inspect --format "{{index .RepoDigests 0}}" ghcr.io/example/myapp:1.0.0
```

**Expected output:**
- After push, `RepoDigests` exposes an immutable `@sha256:` reference.
- Pulling by digest later resolves the exact same content in every environment.

**Check first if it fails:**
- If auth fails, inspect token scope or registry-specific permissions.
- If the digest is unexpected, verify the tag points at the intended image.
- Never leave production with only a mutable tag and no recorded digest.

## Five Common Mistakes

1. **Using *latest* in production.**
2. **Re-deploying without *digest pinning*.**
3. **Pushing *private* images to a *public* repo.**
4. **Overwriting tags and losing *history*.**
5. **Skipping *signature verification*.**

## How This Shows Up in Production

*GitHub Actions* builds and pushes to GHCR; *Argo CD* watches *digest changes* and rolls out automatically.

## How a Senior Engineer Thinks

- The *digest* is the truth.
- A *tag* is only a name.
- The *registry* needs backups too.
- *Signing* protects the supply chain.
- *Permission separation* is the start of security.

## Checklist

- [ ] Production pinned by *digest*.
- [ ] *Push* permission limited to *CI*.
- [ ] *Signing* policy applied.
- [ ] *Retention* policy configured.

## Practice Problems

1. State the *difference* between tag and digest in one line.
2. Name *one strength* of GHCR.
3. Explain in one line *why* signature verification matters.

## Wrap-up and Next Steps

Once you know *where* to fetch images, the next question is *how to run them safely*. The next post covers *container security*.

## Answering the Opening Questions

- **The role of a *registry?**
  - The article treats Registry as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **The *push / pull* flow?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Tagging* strategy?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Containers 101 (1/10): What is a Container?](./01-what-is-a-container.md)
- [Containers 101 (2/10): Image and Layer](./02-image-and-layer.md)
- [Containers 101 (3/10): Runtime](./03-runtime.md)
- [Containers 101 (4/10): Dockerfile](./04-dockerfile.md)
- [Containers 101 (5/10): Volume](./05-volume.md)
- [Containers 101 (6/10): Network](./06-network.md)
- **Registry (current)**
- Container Security (upcoming)
- Containers vs VMs (upcoming)
- Build a Container App (upcoming)

<!-- toc:end -->

## References

- [Docker Hub](https://hub.docker.com/)
- [Amazon ECR](https://docs.aws.amazon.com/AmazonECR/latest/userguide/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Cosign](https://docs.sigstore.dev/cosign/overview/)

Tags: Containers, Docker, Kubernetes, DevOps
