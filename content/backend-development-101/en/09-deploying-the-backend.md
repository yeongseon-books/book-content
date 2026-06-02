---
series: backend-development-101
episode: 9
title: "Backend Development 101 (9/10): Deploying the Backend"
status: publish-ready
targets:
  tistory: false
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
last_reviewed: '2026-05-15'
---

# Backend Development 101 (9/10): Deploying the Backend

The reason code works on your laptop and fails in production is usually not the code alone. It is the difference in operating system, dependencies, secrets, networking, and startup assumptions that never got frozen into something reproducible.

This is the 9th post in the Backend Development 101 series. Here, we treat deployment as a reproducibility problem and use Docker, environment variables, healthchecks, and rolling updates to make backend delivery predictable.


![backend development 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/backend-development-101/09/09-01-concept-at-a-glance.en.png)
*backend development 101 chapter 9 flow overview*

## Questions to Keep in Mind

- The pieces that make up a deployment environment?
- How a Dockerfile creates a *reproducible environment?
- How to manage env vars and secrets?

## Why It Matters

When deploys become *scary*, release frequency drops, and rare deploys carry *more change* and *more risk*. Making deploys boring is one of the most senior things you can do.

> A great deploy has *no drama*.

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

## Verification points

**Expected output:** `docker build` should produce the same runnable image from the same Dockerfile, `/healthz` should return `{"status": "ok"}`, and traffic should move only after the new version passes its healthcheck.

### First failure modes to check

- If the container exits immediately, inspect the `CMD` path and port binding first.
- If behavior changes across environments, secrets or config may still be baked into the image.
- If errors spike during rollout, confirm traffic is not shifting before healthchecks succeed.

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

Most teams use Docker + GitHub Actions + an orchestrator (Kubernetes/ECS). A merged PR triggers CI: build → test → push image → deploy. Operators stop running commands and start watching the system.

### Deploy Flow (Universal Pattern)

```text
1. main merge
2. CI tests pass
3. Image build + SHA tag
4. Staging deploy
5. Readiness/error-rate verification
6. Production rolling update
7. Post-deploy 10-min observation
8. Auto or manual rollback if thresholds exceeded
```

### Post-Deploy 10-Minute Routine

| Window | Metric | Decision criteria |
| --- | --- | --- |
| 0–2 min | Readiness pass rate | 100% per instance |
| 2–5 min | 5xx rate, p95 latency | No spike vs previous deploy |
| 5–10 min | DB connections, queue depth, retry rate | No background load increase |

Watch *rate of change*, not averages. Normal avg latency + spiking p95 = bottleneck on a specific path.

### Deploy Checklist Table

| Item | Verification question | Risk if skipped |
| --- | --- | --- |
| Env vars | All required keys injected? | Boot failure or runtime exception |
| Secrets | Nothing in image/logs? | Security incident, costly key rotation |
| Migration | Schema matches this release? | Partial feature failure |
| Health | liveness + readiness both pass? | Zero-downtime deploy fails |
| Rollback | Can revert to last stable in < 2 min? | Extended outage |
| Monitoring | Error/latency/resource alerts active? | Delayed detection |

### Migration + Rollback Strategy (Expand-Deploy-Contract)

1. **Expand**: add nullable columns, new indexes—backwards-compatible with current code
2. **Deploy**: new code handles both old and new schema
3. **Contract**: after observation, drop unused columns/paths

This ensures app rollback doesn't conflict with data layer changes. Destructive migration bundled with code deploy = recovery time explosion.

### Four Failure Patterns

| Scenario | Symptom | Root cause | Fix |
| --- | --- | --- | --- |
| Works locally, fails in prod | `KeyError: DB_HOST` on boot | Missing env var | Startup config validation, fail-fast |
| Deploy succeeds, container crashes | CrashLoopBackOff | Port mismatch (CMD/EXPOSE/service) | Unify port definition to single source |
| Can't rollback | No previous image to revert to | Only `latest` tag used | Publish `service:semver` + `service:git-sha` |
| DB migration skipped | Specific endpoints return 500 | Code/schema version mismatch | Migration step mandatory in pipeline, abort on failure |

## How a Senior Engineer Thinks

- **Every deploy must be reversible.** If you can't `helm rollback` or redeploy the previous SHA within 2 minutes, the deploy process is incomplete.
- **Secrets live only in a secret manager.** Not in `.env` committed to Git, not baked into images. Rotation must be possible without redeployment.
- **Smaller images mean faster builds and deploys.** Multi-stage builds, `.dockerignore`, minimal base images. Every MB in the image is seconds in CI and cold-start.
- **Migrations are backward-compatible by design.** Never drop a column in the same release that stops using it. Expand first, deploy, observe, then contract.
- **A deploy that pages someone is a bad deploy.** Post-deploy observation is part of the deploy, not a separate concern. The engineer who deploys owns the next 10 minutes.
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

## Answering the Opening Questions

- **What elements compose a deployment environment?**
  - A deployment environment combines code repository, container image, env vars and secrets, orchestrator, reverse proxy, and observability tooling into an execution system. Correct code can still fail if any layer's contract mismatches—all must align for production reproducibility.
- **Why is the Dockerfile the key to a reproducible execution environment?**
  - It pins runtime version, dependency install order, and entrypoint to produce identical images repeatedly. Designing multi-stage builds, layer caching, and `.dockerignore` together improves speed, stability, and security simultaneously.
- **How should env vars and secrets be separated?**
  - Config injects environment-specific behavior values; secrets come from a dedicated vault at runtime only. Validating required values at startup with `pydantic-settings` catches omissions early and stops deployment failures before traffic arrives.

<!-- toc:begin -->
## In this series

- [Backend Development 101 (1/10): What Is Backend Development?](./01-what-is-backend-development.md)
- [Backend Development 101 (2/10): Building an HTTP Server](./02-building-an-http-server.md)
- [Backend Development 101 (3/10): Routing and Controllers](./03-routing-and-controllers.md)
- [Backend Development 101 (4/10): The Service Layer](./04-service-layer.md)
- [Backend Development 101 (5/10): The Database Layer](./05-database-layer.md)
- [Backend Development 101 (6/10): Authentication and Authorization](./06-auth-and-authorization.md)
- [Backend Development 101 (7/10): Logging and Error Handling](./07-logging-and-error-handling.md)
- [Backend Development 101 (8/10): Testing the Backend](./08-testing-the-backend.md)
- **Deploying the Backend (current)**
- A Production-Ready Backend Structure (upcoming)

<!-- toc:end -->

## References

### Official Docs

- [Docker get-started](https://docs.docker.com/get-started/)
- [Kubernetes probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [GitHub Actions for Python](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python)

### Further Reading

- [The Twelve-Factor App](https://12factor.net/)

Tags: Backend, Deployment, Docker, DevOps, Python
