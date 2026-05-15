---
series: docker-101
episode: 6
title: Environment Variables and Configuration
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Docker
  - Config
  - EnvVar
  - Secret
  - 12Factor
seo_description: Inject environment variables, separate config files, and externalize secrets following the twelve-factor configuration principle.
last_reviewed: '2026-05-04'
---

# Environment Variables and Configuration

This is post 6 in the Docker 101 series.

> Docker 101 series (6/10)

<!-- a-grade-intro:begin -->

**Core question**: With *one image*, how do you inject *different settings per environment*?

> *Configuration belongs *outside the code*; secrets belong *outside the image*. The most important *twelve-factor* principle.*

<!-- a-grade-intro:end -->

## What You Will Learn

- The difference between *ENV* and *ARG*
- Splitting *env vars / config files / secrets*
- Wiring *Compose* to *external secret tools*
- Patterns for *defaults and validation*
- Five common pitfalls

## Why It Matters

The *same image* must flow from *dev to staging to prod* unchanged for *reproducibility*. If per-environment config sneaks into code, that trust is gone.

> *Images are build artifacts; environments are *runtime context*.*

## Concept at a Glance

```mermaid
flowchart LR
    Image["app:1.0 (immutable)"] --> Dev["dev env vars"]
    Image --> Stg["staging env vars"]
    Image --> Prd["prod env vars"]
```

## Key Terms

- **ENV**: a *default env var* in the Dockerfile.
- **ARG**: a *build-time* variable.
- **`-e` / `--env-file`**: runtime injection.
- **Config volume**: mount a *config file* in.
- **Secret store**: external secrets via *Vault / Doppler*.

## Before/After

**Before**: separate images for prod and dev, *each built independently*.

**After**: *one image*. Behavior changes by *flipping env vars*.

## Hands-on: Env Vars in 5 Steps

### Step 1 — ENV/ARG in the Dockerfile

```dockerfile
ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION} \
    LOG_LEVEL=INFO
```

### Step 2 — Runtime injection

```bash
docker run --rm \
  -e LOG_LEVEL=DEBUG \
  -e DB_URL=postgres://user:pass@db:5432/app \
  myapp:1.0
```

### Step 3 — `--env-file`

```bash
# .env.staging
LOG_LEVEL=INFO
DB_URL=postgres://user:pass@stg-db:5432/app

docker run --rm --env-file .env.staging myapp:1.0
```

### Step 4 — Variables in Compose

```yaml
services:
  web:
    image: myapp:1.0
    env_file: .env.${ENV:-dev}
    environment:
      LOG_LEVEL: ${LOG_LEVEL:-INFO}
```

### Step 5 — Externalize secrets

```bash
# Doppler
doppler run -- docker compose up -d
# Vault (envconsul)
envconsul -secret secret/app -- docker compose up -d
```

## What to Notice in This Code

- *Defaults* (`${VAR:-default}`) protect against *missing values*.
- Splitting *.env.dev* and *.env.staging* makes the environment *explicit*.
- *Secrets* never sit *inside Compose*.

## Five Common Mistakes

1. **Hardcoding a secret in *Dockerfile ENV*.** Forever embedded in the image.
2. **Committing `.env` to *Git*.** Leak.
3. **Building a *separate image per environment*.** Reproducibility gone.
4. **Letting missing vars *quietly default to empty*.** Runtime incident.
5. **Logging an *env var dump*.** Secret exposure.

## How This Shows Up in Production

Mature teams let *Vault / Doppler / 1Password* be the *runtime secret provider* and the codebase keeps *only variable names*.

## How a Senior Engineer Thinks

- *Image is environment-agnostic*; *environment lives in variables*.
- *A secret in an image has already leaked*.
- *Validate variables at startup* and *fail fast*.
- *Defaults* lean to the *safe side*.
- Always commit a *.env.example*.

## Checklist

- [ ] The image is *environment-agnostic*.
- [ ] Secrets live in an *external store*.
- [ ] A *.env.example* exists.
- [ ] Startup performs *variable validation*.

## Practice Problems

1. Run the *same image* in *dev* and *staging*.
2. Split per-environment configuration via `--env-file`.
3. Add code that *fails to start* when a required variable is missing.

## Wrap-up and Next Steps

Configuration discipline is half of *production stability*. Next, we turn a *Python app* into a *complete container*.

<!-- toc:begin -->
- [What Is Docker?](./01-what-is-docker.md)
- [Images and Containers](./02-image-and-container.md)
- [Writing a Dockerfile](./03-dockerfile.md)
- [Volumes and Networks](./04-volume-and-network.md)
- [Docker Compose](./05-docker-compose.md)
- **Environment Variables and Configuration (current)**
- Containerizing a Python App (upcoming)
- Running with a Database (upcoming)
- Image Optimization (upcoming)
- Production-Ready Docker (upcoming)
<!-- toc:end -->

## References

- [The Twelve-Factor App - Config](https://12factor.net/config)
- [Set environment variables in containers](https://docs.docker.com/engine/reference/commandline/run/#env)
- [Compose - environment variables](https://docs.docker.com/compose/environment-variables/)
- [Manage secrets with Docker](https://docs.docker.com/engine/swarm/secrets/)

Tags: Docker, Config, EnvVar, Secret, 12Factor
