---
series: docker-101
episode: 5
title: "Docker 101 (5/10): Docker Compose"
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
  - Compose
  - YAML
  - MultiContainer
  - Dev
seo_description: Define and run multi-container environments from a single YAML file with Docker Compose, including healthchecks and profiles.
last_reviewed: '2026-05-15'
---

# Docker 101 (5/10): Docker Compose

A few `docker run` commands are manageable when you have only one service. The moment you need a web app, a database, a cache, and maybe a worker, that command-line memory game stops scaling. Teams start depending on tribal knowledge instead of a reproducible environment definition.

Compose matters because it turns that memory into a checked-in declaration. Services, ports, volumes, healthchecks, and optional profiles become reviewable configuration instead of setup folklore.

This is post 5 in the Docker 101 series. It shows how to express a multi-container environment in Compose, what `depends_on` can and cannot guarantee, and which verification steps tell you the stack is actually ready.

## Questions to Keep in Mind

- Defining *services / networks / volumes?
- depends_on* and healthchecks?
- profiles* for *selective execution?

## Big Picture

![docker 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/05/05-01-concept-at-a-glance.en.png)

*docker 101 chapter 5 flow overview*

This picture places Docker Compose inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## Why It Matters

New-hire setup finishes in *under five minutes*. The *README setup section* simply disappears.

> *Compose is the shortest path to *environment-as-code*.*

## Key Terms

- **Service**: a *group of containers* from one image.
- **Project**: the *logical unit* Compose manages.
- **Profile**: a *bundle of services* that runs only in a specific scenario.
- **Healthcheck**: the criterion for *readiness*.
- **depends_on**: start *order* and *waiting*.

## Before/After

**Before**: five `docker run` commands wrapped in a *shell script*. Options are *remembered, not written down*.

**After**: `docker compose up`. Every option is *explicit in YAML*.

## Hands-on: Compose in 5 Steps

### Step 1 — `compose.yaml`

```yaml
services:
  web:
    build: .
    ports: ["8000:8000"]
    environment:
      DB_HOST: db
    depends_on:
      db:
        condition: service_healthy
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: dev
    volumes: ["pgdata:/var/lib/postgresql/data"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5
volumes:
  pgdata:
```

### Step 2 — Bring it up

```bash
docker compose up -d
docker compose ps
docker compose logs -f web
```

### Step 3 — Variables (`.env`)

```bash
# .env
DB_PASSWORD=dev
APP_PORT=8000
```

```yaml
environment:
  POSTGRES_PASSWORD: ${DB_PASSWORD}
ports: ["${APP_PORT}:8000"]
```

### Step 4 — Profile

```yaml
services:
  worker:
    image: myapp:1.0
    profiles: ["worker"]
```

```bash
docker compose --profile worker up -d
```

### Step 5 — Tear down

```bash
docker compose down            # remove containers
docker compose down -v         # also remove volumes
```

### Verify right after you run it

- In `docker compose ps`, the database should become `healthy` before the web service settles into its running state.
- `docker compose logs -f web` should show the application starting without immediate database connection errors.

### If it does not work, check this first

- If the web container exits too early, verify that `depends_on` uses `condition: service_healthy` rather than plain start order.
- If test data vanished after `down -v`, that is expected; make sure disposable and persistent data do not share the same volume strategy.

## What to Notice in This Code

- *healthcheck + condition: service_healthy* waits for *real readiness*.
- `depends_on` alone only ensures *start order*, not readiness.
- *profiles* is the standard for *optional services*.

## Five Common Mistakes

1. **Trusting `depends_on` and *connecting before DB is ready*.** Healthcheck is required.
2. **Always running `up`, *never* `down -v`.** Data sits *contaminated*.
3. **Committing `.env`.** Secrets leak.
4. **Running *all services always* without profiles.** Resource waste.
5. **Multiple projects on the *same port*.** Conflicts.

## How This Shows Up in Production

Most companies' *local dev environments* run on Compose. CI also uses it for *integration test bootstrapping*.

## How a Senior Engineer Thinks

- *Setup must be *one command*.
- `depends_on` without a healthcheck is *a lie*.
- Keep `.env` and `.env.example` *separate*.
- *Profiles* split *complexity*.
- Use `down -v` only when you can *recover*.

## Checklist

- [ ] All services live in *one compose.yaml*.
- [ ] Dependent services have a *healthcheck*.
- [ ] *.env / .env.example* are split.
- [ ] Optional services use *profiles*.

## Practice Problems

1. Bring up *web + db + redis* via Compose.
2. Add a *healthcheck* on db so web starts *after readiness*.
3. Move ports into *.env* and reference them.

## Wrap-up and Next Steps

Compose is your team's *first piece of infrastructure as code*. Next, the patterns of *environment variables and configuration*.

## Answering the Opening Questions

- **Defining *services / networks / volumes?**
  - The article treats Docker Compose as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **depends_on* and healthchecks?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **profiles* for *selective execution?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Docker 101 (1/10): What Is Docker?](./01-what-is-docker.md)
- [Docker 101 (2/10): Images and Containers](./02-image-and-container.md)
- [Docker 101 (3/10): Writing a Dockerfile](./03-dockerfile.md)
- [Docker 101 (4/10): Volumes and Networks](./04-volume-and-network.md)
- **Docker Compose (current)**
- Environment Variables and Configuration (upcoming)
- Containerizing a Python App (upcoming)
- Running with a Database (upcoming)
- Image Optimization (upcoming)
- Production-Ready Docker (upcoming)

<!-- toc:end -->

## References

### Official docs

- [Compose specification](https://docs.docker.com/compose/compose-file/)
- [Overview of Compose](https://docs.docker.com/compose/)
- [Compose profiles](https://docs.docker.com/compose/profiles/)
- [Healthcheck in Compose](https://docs.docker.com/compose/compose-file/05-services/#healthcheck)

### Verification and troubleshooting

- [Compose startup order and dependency conditions](https://docs.docker.com/compose/how-tos/startup-order/)

Tags: Docker, Compose, YAML, MultiContainer, Dev
