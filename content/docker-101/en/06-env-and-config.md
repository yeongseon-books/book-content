---
series: docker-101
episode: 6
title: "Docker 101 (6/10): Environment Variables and Configuration"
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
  - Config
  - EnvVar
  - Secret
  - 12Factor
seo_description: Inject environment variables, separate config files, and externalize secrets following the twelve-factor configuration principle.
last_reviewed: '2026-05-15'
---

# Docker 101 (6/10): Environment Variables and Configuration

Configuration is where reproducibility quietly breaks. If a team builds one image for development, another for staging, and yet another for production, it no longer has one deployable artifact. It has several environment-specific snowflakes that only look similar.

The better model is simpler: keep the image immutable and move environment-specific behavior to runtime configuration. That is also where secret handling becomes a security decision instead of a convenience shortcut.

This is post 6 in the Docker 101 series. It covers the contract between image and environment, including `ENV` vs `ARG`, runtime injection patterns, secret externalization, and the startup checks that keep missing variables from becoming late incidents.

## Questions to Keep in Mind

- The difference between *ENV* and *ARG?
- Splitting *env vars / config files / secrets?
- Wiring *Compose* to *external secret tools?

## Big Picture

![docker 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/06/06-01-concept-at-a-glance.en.png)

*docker 101 chapter 6 flow overview*

This picture places Environment Variables and Configuration inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## Why It Matters

The *same image* must flow from *dev to staging to prod* unchanged for *reproducibility*. If per-environment config sneaks into code, that trust is gone.

> *Images are build artifacts; environments are *runtime context*.*

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

### Verify right after you run it

- Run the image with `--env-file` and confirm that the expected values actually appear in app diagnostics or logs, especially `LOG_LEVEL` and database settings.
- Remove a required variable once and confirm that the application fails fast instead of continuing with a silent empty default.

### If it does not work, check this first

- When a variable resolves to an empty string, inspect the `.env` file path and shell export state before blaming Docker interpolation.
- If you suspect a secret leaked into the image, review both `docker history` and every Dockerfile `ENV` instruction first.

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

## Answering the Opening Questions

- **The difference between *ENV* and *ARG?**
  - The article treats Environment Variables and Configuration as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Splitting *env vars / config files / secrets?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Wiring *Compose* to *external secret tools?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Docker 101 (1/10): What Is Docker?](./01-what-is-docker.md)
- [Docker 101 (2/10): Images and Containers](./02-image-and-container.md)
- [Docker 101 (3/10): Writing a Dockerfile](./03-dockerfile.md)
- [Docker 101 (4/10): Volumes and Networks](./04-volume-and-network.md)
- [Docker 101 (5/10): Docker Compose](./05-docker-compose.md)
- **Environment Variables and Configuration (current)**
- Containerizing a Python App (upcoming)
- Running with a Database (upcoming)
- Image Optimization (upcoming)
- Production-Ready Docker (upcoming)

<!-- toc:end -->

## References

### Official docs

- [The Twelve-Factor App - Config](https://12factor.net/config)
- [Set environment variables in containers](https://docs.docker.com/engine/reference/commandline/run/#env)
- [Compose - environment variables](https://docs.docker.com/compose/environment-variables/)
- [Manage secrets with Docker](https://docs.docker.com/engine/swarm/secrets/)

### Verification and troubleshooting

- [Environment variables in Compose](https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/)

Tags: Docker, Config, EnvVar, Secret, 12Factor
