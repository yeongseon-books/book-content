---
series: containers-101
episode: 10
title: "Containers 101 (10/10): Build a Container App"
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
- Compose
- FastAPI
- DevOps
seo_description: A hands-on guide to shipping a FastAPI app with Dockerfile, Compose,
  healthcheck, secrets, and logs as one runnable stack
last_reviewed: '2026-05-15'
---

# Containers 101 (10/10): Build a Container App

The earlier chapters only become operationally useful when they collapse into one reproducible application workflow. A single command that brings up the stack, verifies health, and tears it down cleanly is where container basics stop being vocabulary and start being practice.

This is the final post in the Containers 101 series.

In this chapter, we assemble a FastAPI app and Postgres into one stack with Dockerfile, Compose, health checks, secret boundaries, and log inspection as one repeatable flow.

> A one-command stack is where container theory becomes an operational habit you can repeat.

## Questions to Keep in Mind

- A *Dockerfile* for a *FastAPI* app?
- Compose* with a *DB* connection?
- Defining a *healthcheck?

## Big Picture

![containers 101 chapter 10 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/containers-101/10/10-01-concept-at-a-glance.en.png)

*containers 101 chapter 10 flow overview*

This picture places Build a Container App inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> Building a container app means weaving together development, testing, registry push, orchestration, and observability into one reproducible pipeline.

## Why It Matters

Every concept above only sticks once you *integrate* it into *one running result*. That is the meaning of this *final post*.

A container app lives in three places: source code + Dockerfile in version control; built image in a registry (tagged for traceability); running instance in an orchestrator (with volumes, network policy, and logging attached). Each stage moves the same artifact forward.

## Key Terms

- **Dockerfile**: a *recipe* for building an image.
- **Compose**: a tool that ties *multiple containers* together via *YAML*.
- **healthcheck**: a *liveness signal*.
- **restart policy**: an *auto-restart rule on failure*.
- **logs driver**: a *log collection backend*.

## Before / After

**Before**: many *manual docker run* lines that no one can reproduce.

**After**: `docker compose up` runs the *whole stack* in *one line*.

## Hands-on: A FastAPI + Postgres Stack

### Step 1 — app/main.py

```python
from fastapi import FastAPI
import os, psycopg

app = FastAPI()

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/users")
def users():
    with psycopg.connect(os.environ["DB_URL"]) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM users")
            return {"count": cur.fetchone()[0]}
```

### Step 2 — Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
USER 1000
EXPOSE 8080
HEALTHCHECK CMD curl -f http://localhost:8080/health || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Step 3 — docker-compose.yml

```yaml
services:
  app:
    build: .
    ports: ["8080:8080"]
    environment:
      DB_URL: postgresql://app:secret@db:5432/app
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: app
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 5s
      timeout: 3s
      retries: 10
```

### Step 4 — Automate startup

```python
import subprocess

def up():
    subprocess.run(["docker", "compose", "up", "-d", "--build"], check=True)

def logs():
    subprocess.run(["docker", "compose", "logs", "--tail=100"], check=False)
```

### Step 5 — Tear down

```python
def down():
    subprocess.run(["docker", "compose", "down", "-v"], check=True)
```

## What to Notice in This Code

- *USER 1000* enforces *non-root*.
- The *healthcheck* drives *Compose* dependency ordering.
- *depends_on + service_healthy* is a paired pattern.

## Quick verification and failure signals

```bash
docker compose up -d --build
docker compose ps
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/users
docker compose logs --tail=100
```

**Expected output:**
- `docker compose ps` shows both app and db as running.
- `/health` returns `{"ok": true}`.
- `/users` proves the app can reach Postgres through the service name.

**Check first if it fails:**
- If the app crashes early, inspect `depends_on` and health-check logic together.
- If DB access fails, verify the Compose network still resolves `db` by name.
- If secrets are still plain text, split them out before calling the stack production-ready.

## Five Common Mistakes

1. **Storing the *DB password* as plain text in *Compose* forever.**
2. **Using *depends_on* without a *healthcheck*.**
3. **Forgetting a *restart policy* and propagating failures.**
4. **Missing *volumes* and losing data.**
5. **Writing *logs* only inside the container.**

## How This Shows Up in Production

*Local development* runs on *Compose*; *production* runs on *Kubernetes*; the *same image* is operated by *different orchestrators*.

## How a Senior Engineer Thinks

- A *one-line bring-up* defines *onboarding cost*.
- The *healthcheck* is the *signal for orchestration*.
- *Env vars* should be the *only difference* across environments.
- *Logs* go to *stdout*.
- Even *teardown* is automated.

## Checklist

- [ ] *Non-root* at runtime.
- [ ] *Healthcheck* defined.
- [ ] *Secrets* split out.
- [ ] *Teardown* command documented.

## Practice Problems

1. Explain in one line *why* the Dockerfile *USER* matters.
2. Explain in one line why *depends_on alone* is insufficient.
3. Name *one thing* Compose and Kubernetes share.

## Wrap-up and Next Steps

This is the *finale* of *Containers 101*. The next step is *Kubernetes 101*, where you enter the world of *orchestration*.

## Answering the Opening Questions

- **A *Dockerfile* for a *FastAPI* app?**
  - The article treats Build a Container App as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Compose* with a *DB* connection?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Defining a *healthcheck?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Containers 101 (1/10): What is a Container?](./01-what-is-a-container.md)
- [Containers 101 (2/10): Image and Layer](./02-image-and-layer.md)
- [Containers 101 (3/10): Runtime](./03-runtime.md)
- [Containers 101 (4/10): Dockerfile](./04-dockerfile.md)
- [Containers 101 (5/10): Volume](./05-volume.md)
- [Containers 101 (6/10): Network](./06-network.md)
- [Containers 101 (7/10): Registry](./07-registry.md)
- [Containers 101 (8/10): Container Security](./08-container-security.md)
- [Containers 101 (9/10): Containers vs VMs](./09-container-vs-vm.md)
- **Build a Container App (current)**

<!-- toc:end -->

## References

- [Docker Compose](https://docs.docker.com/compose/)
- [FastAPI in containers](https://fastapi.tiangolo.com/deployment/docker/)
- [Dockerfile best practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [HEALTHCHECK reference](https://docs.docker.com/engine/reference/builder/#healthcheck)

Tags: Containers, Docker, Kubernetes, DevOps
