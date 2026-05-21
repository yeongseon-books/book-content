---
series: docker-101
episode: 4
title: "Docker 101 (4/10): Volumes and Networks"
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
  - Volume
  - Network
  - BindMount
  - Bridge
seo_description: How volumes, bind mounts, and networks let containers persist data and talk to each other safely with named DNS.
last_reviewed: '2026-05-15'
---

# Docker 101 (4/10): Volumes and Networks

Running one container is the easy part. The real operational questions begin as soon as you need data to survive a restart and one container to reach another container without guessing IP addresses. Those two requirements show up almost immediately in real applications.

Docker gives you separate tools for the two problems on purpose. Volumes control data lifetime. Networks control communication paths. Keeping those concerns separate is what prevents “the database disappeared” and “the app cannot find the database” from becoming routine incidents.

This is post 4 in the Docker 101 series. It focuses on when to use named volumes, bind mounts, and user-defined bridge networks, plus the concrete checks you should run before you trust persistence or name-based communication.

## Questions to Keep in Mind

- The difference between *volume / bind mount / tmpfs?
- Bridge / host / none* network modes?
- Communicating *by container name?

## Big Picture

![docker 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/04/04-01-concept-at-a-glance.en.png)

*docker 101 chapter 4 flow overview*

This picture places Volumes and Networks inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## Why It Matters

*Data loss* and *broken communication* are the *most common incidents* in container ops. The right *volume/network model* prevents both.

> *The moment *state leaks* into a stateless container, an incident begins.*

## Key Terms

- **Volume**: a *persistent store* managed by Docker.
- **Bind mount**: a *host path* mounted directly.
- **tmpfs**: memory-backed *ephemeral* storage.
- **Bridge network**: the default *virtual network* on one host.
- **Service discovery**: *DNS resolution* by container name.

## Before/After

**Before**: DB data *disappears* on restart. Containers cannot reach each other on `localhost`.

**After**: *named volumes* persist data. *User-defined bridges* let containers talk *by name*.

## Hands-on: Volumes and Networks in 5 Steps

### Step 1 — Named volume

```bash
docker volume create app-data
docker run -d --name api -v app-data:/var/lib/data myapp
docker volume inspect app-data
```

### Step 2 — Bind mount (for dev)

```bash
docker run --rm -v "$PWD":/app -w /app python:3.12-slim python app.py
```

### Step 3 — User-defined bridge

```bash
docker network create app-net
docker run -d --network app-net --name db postgres:16
docker run -d --network app-net --name api -e DB_HOST=db myapp
# api can reach the host 'db'
```

### Step 4 — Verify communication

```bash
docker exec api ping -c 1 db
docker exec api curl http://db:5432
```

### Step 5 — Back up a volume

```bash
docker run --rm \
  -v app-data:/data \
  -v "$PWD":/backup \
  alpine tar czf /backup/data.tgz -C /data .
```

### Verify right after you run it

- `docker volume inspect app-data` should show a named volume that exists independently of any one container, and `docker exec api ping -c 1 db` should prove name-based resolution on the bridge network.
- If you ran the backup step, confirm that `data.tgz` was actually created in the working directory.

### If it does not work, check this first

- If the app still tries to reach the database on `localhost`, inspect the injected `DB_HOST` value before troubleshooting Docker networking.
- Permission failures on a bind mount usually come from a mismatch between host ownership and the UID inside the container.

## What to Notice in This Code

- A *named volume* lives *independent of containers*.
- *User-defined bridges* provide *DNS* automatically.
- *Bind mounts* often have *permission issues*.

## Five Common Mistakes

1. **Saving directly to *paths inside* the container.** Lost on restart.
2. **Using the *default bridge*.** *No name resolution*.
3. **Bind mount owned by *root only*.** Cannot edit from the host.
4. **Volumes that are *never backed up*.** Unrecoverable on incident.
5. **Abusing `--network host`.** Security and port-conflict risks.

## How This Shows Up in Production

Orchestrators (e.g., Kubernetes) extend the same ideas with *PersistentVolume* and *Service DNS*. Learning them here makes the transition natural.

## How a Senior Engineer Thinks

- *State is a volume; communication is a network*.
- *User-defined bridges* are the *default*.
- *A volume without a backup is one incident away*.
- *Bind mounts* are for dev; production uses *named volumes*.
- *Expose ports minimally*.

## Checklist

- [ ] Data persists in a *named volume*.
- [ ] Containers run on a *user-defined bridge*.
- [ ] They communicate *by name*.
- [ ] A *backup procedure* exists.

## Practice Problems

1. Persist PostgreSQL data with a *named volume*.
2. Make two containers talk by *name* on a *user-defined bridge*.
3. Back up a volume's contents with *tar*.

## Wrap-up and Next Steps

Data and networking are the *pillars* of container ops. Next, *Docker Compose* runs many containers *at once*.

## Answering the Opening Questions

- **The difference between *volume / bind mount / tmpfs?**
  - The article treats Volumes and Networks as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Bridge / host / none* network modes?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Communicating *by container name?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Docker 101 (1/10): What Is Docker?](./01-what-is-docker.md)
- [Docker 101 (2/10): Images and Containers](./02-image-and-container.md)
- [Docker 101 (3/10): Writing a Dockerfile](./03-dockerfile.md)
- **Volumes and Networks (current)**
- Docker Compose (upcoming)
- Environment Variables and Configuration (upcoming)
- Containerizing a Python App (upcoming)
- Running with a Database (upcoming)
- Image Optimization (upcoming)
- Production-Ready Docker (upcoming)

<!-- toc:end -->

## References

### Official docs

- [Volumes](https://docs.docker.com/storage/volumes/)
- [Bind mounts](https://docs.docker.com/storage/bind-mounts/)
- [Networking overview](https://docs.docker.com/network/)
- [Use bridge networks](https://docs.docker.com/network/bridge/)

### Verification and troubleshooting

- [docker volume inspect reference](https://docs.docker.com/reference/cli/docker/volume/inspect/)

Tags: Docker, Volume, Network, BindMount, Bridge
