---
series: backend-development-101
episode: 9
title: Deploying the Backend
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Backend
  - Deployment
  - Docker
  - DevOps
  - Python
seo_description: Use Docker, environment variables, healthchecks, and rolling updates to ship a Python backend safely to production.
last_reviewed: '2026-05-04'
---

# Deploying the Backend

> Backend Development 101 series (9/10)

<!-- a-grade-intro:begin -->

**Core question**: Why does "it works on my laptop" so often *break* in production?

> Production has different OS, dependencies, secrets, and networks. Deployment is the work of *freezing* those differences in code.

<!-- a-grade-intro:end -->

## What You Will Learn

- The pieces that make up a deployment environment
- How a Dockerfile creates a *reproducible environment*
- How to manage env vars and secrets
- What healthchecks and readiness probes do
- The basic idea behind zero-downtime deployment

## Why It Matters

When deploys become *scary*, release frequency drops, and rare deploys carry *more change* and *more risk*. Making deploys boring is one of the most senior things you can do.

> A great deploy has *no drama*.

## Concept at a Glance

```mermaid
flowchart LR
    Code["Source"] --> Build["Build"]
    Build --> Image["Container image"]
    Image --> Reg["Registry"]
    Reg --> Run["Runner"]
    Run --> LB["Load balancer"]
    LB --> Users["Users"]
```

Code becomes an *image*; the image runs the same way *everywhere*.

## Key Terms

- **Container**: a unit that runs *with its dependencies inside it*.
- **Image**: the blueprint of a container.
- **Registry**: the storage for images.
- **Healthcheck**: an endpoint that tells the runner whether the container is *alive*.
- **Rolling update**: replacing the old version *gradually* with the new one.

## Before/After

**Before (manual deploy)**

```bash
ssh server
git pull
pip install -r requirements.txt
systemctl restart app
```

**After (Dockerized — same image runs everywhere)**

```bash
docker build -t myapp:1.2.3 .
docker push registry/myapp:1.2.3
# Production pulls the same image and runs it
```

## Hands-on: Five Steps to a Deploy

### Step 1 — Dockerfile

```dockerfile
# Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 2 — Build and run

```bash
docker build -t myapp:0.1 .
docker run -p 8000:8000 myapp:0.1
```

### Step 3 — Environment variables

```python
# main.py
import os
DB_URL = os.environ["DATABASE_URL"]
JWT_SECRET = os.environ["JWT_SECRET"]
```

```bash
docker run -e DATABASE_URL=postgres://... -e JWT_SECRET=... myapp:0.1
```

### Step 4 — Healthcheck endpoint

```python
# health.py
@app.get("/healthz")
def healthz():
    return {"status": "ok"}
```

In `docker-compose.yml`:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/healthz"]
  interval: 10s
  retries: 3
```

### Step 5 — Rolling update

```bash
# Kubernetes, ECS, Docker Swarm — same idea
# 1) deploy the new image
# 2) wait for healthcheck to pass
# 3) shift traffic gradually
# 4) remove the old version
```

The key is to *prove the new version is healthy* before traffic moves.

## What to Notice in This Code

- Secrets *do not* go inside the image.
- Options like `--no-cache-dir` keep the image lean.
- The application provides its own healthcheck.

## Five Common Mistakes

1. **Deploying the `latest` tag in production.** You cannot tell *which version* is live.
2. **Baking secrets into the image.** A leaked image leaks the secrets.
3. **Skipping healthchecks behind a load balancer.** Traffic flows to dead instances.
4. **Running migrations *manually* in production.** Deploy automation loses its point.
5. **Not preparing a rollback procedure.** Incident response becomes *unrehearsed*.

## How This Shows Up in Production

Most teams use *Docker + GitHub Actions + an orchestrator (Kubernetes/ECS)*. A merged PR triggers CI: build the image, push it, deploy. Operators stop *running commands* and start *watching the system*.

## How a Senior Engineer Thinks

- Every deploy must be *reversible*.
- Secrets live only in a *secret manager*.
- Smaller images mean faster builds and deploys.
- Migrations are designed to be *backward compatible*.
- A deploy that pages someone is, by definition, a *bad deploy*.

## Checklist

- [ ] You can write a Dockerfile and build the image.
- [ ] You can split config out into environment variables.
- [ ] You can add a `/healthz` endpoint.
- [ ] You can keep secrets out of the image.
- [ ] You can describe the rolling update flow.

## Practice Problems

1. Dockerize your FastAPI app and run it locally.
2. Use a `.env` file with `docker run --env-file` to externalize config.
3. Break the healthcheck on purpose and observe the container status.

## Wrap-up and Next Steps

Deployment is a *reproducibility* problem. In the final chapter, we tie all the layers together into a *production-ready backend structure*.

<!-- toc:begin -->
- [What Is Backend Development?](./01-what-is-backend-development.md)
- [Building an HTTP Server](./02-building-an-http-server.md)
- [Routing and Controllers](./03-routing-and-controllers.md)
- [The Service Layer](./04-service-layer.md)
- [The Database Layer](./05-database-layer.md)
- [Authentication and Authorization](./06-auth-and-authorization.md)
- [Logging and Error Handling](./07-logging-and-error-handling.md)
- [Testing the Backend](./08-testing-the-backend.md)
- **Deploying the Backend (current)**
- A Production-Ready Backend Structure (upcoming)
<!-- toc:end -->

## References

- [Docker get-started](https://docs.docker.com/get-started/)
- [The Twelve-Factor App](https://12factor.net/)
- [Kubernetes probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [GitHub Actions for Python](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python)
