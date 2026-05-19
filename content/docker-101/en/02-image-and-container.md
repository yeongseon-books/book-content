---
series: docker-101
episode: 2
title: Images and Containers
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
  - Image
  - Container
  - Layer
  - Lifecycle
seo_description: Image and container lifecycle, layer model, and the ten commands you actually use day to day, with hands-on inspection.
last_reviewed: '2026-05-15'
---

# Images and Containers

The first serious confusion in Docker usually appears between images and containers. Teams pull an image, change files inside a running container, restart it, and then wonder why the change disappeared. The failure is not mysterious; it comes from mixing up a deployable artifact with a disposable runtime instance.

Once that distinction is clear, a lot of troubleshooting gets easier. You can separate image build issues from runtime state issues, and you can explain why some changes belong in a Dockerfile while others belong in a volume or an environment variable.

This is post 2 in the Docker 101 series. Here we use layers, copy-on-write, and lifecycle commands to build a durable mental model for image state, container state, and what actually survives a restart.
## What you will learn

- The *lifecycle* of *images* and *containers*
- *Layers* and *copy-on-write*
- The *ten commands* you actually use
- How to *look inside* a container
- Five common pitfalls

## Why It Matters

If you do not understand how containers behave, *debugging becomes luck*. Knowing layers and lifecycle makes *80% of issues* *predictable*.

> *Half of "non-reproducible" bugs come from *misunderstanding container state*.*

## Concept at a Glance

![Immutable image flowing into a mutable container lifecycle from run to stop to removal](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/02/02-01-concept-at-a-glance.en.png)

*An immutable image becomes a mutable container instance that can be created, run, stopped, and removed without changing the source artifact*

## Key Terms

- **Layer**: a *read-only filesystem slice* inside an image.
- **Writable layer**: the *top read-write layer* a container owns.
- **Lifecycle**: created -> running -> stopped -> removed.
- **Tag**: an image version label (`nginx:1.27`).
- **Digest**: the *immutable SHA256* identifier of an image.

## Before/After

**Before**: you `apt install` inside a container, then panic when it *vanishes on restart*.

**After**: changes are *codified in a Dockerfile*; containers can be *thrown away anytime*.

## Hands-on: Images and Containers in 5 Steps

### Step 1 — Inspect an image

```bash
docker pull nginx:1.27
docker image inspect nginx:1.27 | jq '.[0].RootFS.Layers'
docker history nginx:1.27
```

### Step 2 — Create and start a container

```bash
docker create --name web nginx:1.27   # create only
docker start web                       # then start
docker ps
```

### Step 3 — Step inside

```bash
docker exec -it web bash
# inside the container
ls /etc/nginx
exit
```

### Step 4 — Changes are *ephemeral*

```bash
docker exec web touch /tmp/hello
docker stop web && docker rm web
docker run --name web2 nginx:1.27
docker exec web2 ls /tmp/hello   # No such file
```

### Step 5 — Clean up images

```bash
docker image prune -f          # remove dangling
docker image rm nginx:1.27
```

### Verify right after you run it

- `docker history nginx:1.27` should show a list of image layers, and `docker exec web2 ls /tmp/hello` should fail because the file lived only in the first container instance.
- Those two observations together confirm the difference between image state and container state.

### If it does not work, check this first

- If `docker exec -it web bash` fails, the image may not include `bash`; retry with `sh`.
- If image cleanup fails, check `docker ps -a` first and make sure no running container still references the image.

## What to Notice in This Code

- `docker history` shows the *commands behind each layer*.
- Container changes are lost *unless you commit*.
- A *digest* is *much more trustworthy* than a tag.

## Five Common Mistakes

1. **Storing files *permanently inside the container*.** Lost on restart.
2. **Building images via `docker commit`.** *Not reproducible*.
3. **Letting stopped containers *pile up*.** `docker ps -a` becomes *hundreds of lines*.
4. **Using only `latest`.** Compatibility breaks one morning.
5. **Images with *too many layers*.** Build and pull get slow.

## How This Shows Up in Production

CI systems build with *digest pins* for reproducibility, and operations correlate *image-level change history* with Datadog/Grafana to *track change-related incidents*.

## How a Senior Engineer Thinks

- *Images are built; containers are run*.
- *Change is code*; `commit` is the *last resort*.
- *Digest pins* are the *production default*.
- *Layer caching* drives *build speed*.
- *Design containers to be discarded at any time*.

## Checklist

- [ ] You can explain *image vs container*.
- [ ] You know container changes are *ephemeral*.
- [ ] You use *layers / digests*.
- [ ] You *clean up* stopped containers.

## Practice Problems

1. Find the *number of layers* in `nginx:1.27`.
2. Create a file inside a container, restart it, confirm it is gone.
3. Run `docker image prune` to clear *unused images*.

## Wrap-up and Next Steps

Separating images and containers is the *fundamentals* of Docker. Next we *build images with Dockerfile*.

<!-- toc:begin -->
- [What Is Docker?](./01-what-is-docker.md)
- **Images and Containers (current)**
- Writing a Dockerfile (upcoming)
- Volumes and Networks (upcoming)
- Docker Compose (upcoming)
- Environment Variables and Configuration (upcoming)
- Containerizing a Python App (upcoming)
- Running with a Database (upcoming)
- Image Optimization (upcoming)
- Production-Ready Docker (upcoming)
<!-- toc:end -->

## References

### Official docs

- [Docker images](https://docs.docker.com/engine/reference/commandline/image/)
- [Docker container lifecycle](https://docs.docker.com/engine/reference/commandline/container/)
- [Storage drivers and layers](https://docs.docker.com/storage/storagedriver/)
- [Image digests](https://docs.docker.com/engine/reference/commandline/pull/#pull-an-image-by-digest-immutable-identifier)

### Verification and troubleshooting

- [docker exec reference](https://docs.docker.com/engine/reference/commandline/exec/)

Tags: Docker, Image, Container, Layer, Lifecycle
