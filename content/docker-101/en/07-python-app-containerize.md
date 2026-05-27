---
series: docker-101
episode: 7
title: "Docker 101 (7/10): Containerizing a Python App"
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
  - Python
  - FastAPI
  - Uvicorn
  - PID1
seo_description: Containerize a FastAPI app to production grade with Dockerfile, healthcheck, non-root user, and proper PID 1 signal handling.
last_reviewed: '2026-05-15'
---

# Docker 101 (7/10): Containerizing a Python App

A Python app running inside a container is not the same thing as a production-ready Python container. The difference shows up when the process receives SIGTERM during deployment, when healthchecks ask whether the app is really ready, and when a compromised process should not be running as root.

Those details are easy to skip because the app still starts without them. They only become visible when a deployment drains live traffic, a container hangs on shutdown, or an orchestrator keeps restarting something that looked healthy on a laptop.

This is the 7th post in the Docker 101 series. It turns a simple FastAPI example into an operationally credible container by focusing on PID 1, signals, healthchecks, and least-privilege execution.


![docker 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/07/07-01-concept-at-a-glance.en.png)
*docker 101 chapter 7 flow overview*

## Questions to Keep in Mind

- Containerizing *FastAPI + uvicorn?
- Signal handling at PID 1* (SIGTERM)?
- Adding a *healthcheck?

## Why It Matters

*Python in a container* often *fails to receive SIGTERM*, breaking *graceful shutdown*. This is a common cause of *deploy incidents*.

> *PID 1 in a container needs to be a *small init* or a process with *correct signal handling*.*

## Key Terms

- **PID 1**: the *first process* in a container.
- **SIGTERM**: the *graceful* termination signal.
- **Graceful shutdown**: finishing *in-flight requests* before exit.
- **Healthcheck**: container reports its *health*.
- **Tini**: a *tiny init* process.

## Before/After

**Before**: `python app.py` runs directly. SIGTERM is ignored, then the process is *killed*.

**After**: `uvicorn` + `tini` deliver *graceful shutdown*. The healthcheck reports *readiness*.

## Hands-on: Python Container in 5 Steps

### Step 1 — App code (`app.py`)

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/")
def root() -> dict[str, str]:
    return {"hello": "world"}
```

### Step 2 — Dockerfile

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# deps layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# app layer
COPY . .

RUN useradd -m -u 1000 appuser
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz').read()" || exit 1

# tini at PID 1 forwards SIGTERM
ENTRYPOINT ["tini", "--"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 3 — `requirements.txt`

```text
fastapi==0.115.*
uvicorn[standard]==0.30.*
```

### Step 4 — Build and run

```bash
docker build -t myapi:1.0 .
docker run -d --name api -p 8000:8000 myapi:1.0
curl http://localhost:8000/healthz
```

### Step 5 — Verify graceful shutdown

```bash
docker stop api    # sends SIGTERM, uvicorn drains in-flight requests
docker logs api | tail
```

### Verify right after you run it

- `curl http://localhost:8000/healthz` should return `{"status":"ok"}`, and `docker stop api` should produce graceful shutdown logs rather than a forced termination pattern.
- It is also worth checking `docker exec api id` once to confirm the process is not running as root.

### If it does not work, check this first

- If the container exits immediately, confirm that `tini` is actually installed in the image and not just referenced in `ENTRYPOINT`.
- If the healthcheck keeps failing, verify that uvicorn is bound to `0.0.0.0:8000` and that `/healthz` exists exactly as declared.

## What to Notice in This Code

- *Deps -> code* ordering for *cache efficiency*.
- *tini* forwards *signals correctly*.
- The *healthcheck* cooperates with the orchestrator.

## Five Common Mistakes

1. **Running `python app.py` *directly*.** SIGTERM is *ignored*.
2. **Setting `workers` to *4x cores*.** *Memory blow-up*.
3. **`pip install` running *on every code change*.** Minutes of build cost.
4. **Running as *root*.** Security incident.
5. **Healthcheck *also probes the DB*.** *False negatives* skyrocket.

## How This Shows Up in Production

In real deployments, *Gunicorn + Uvicorn worker*, *prometheus-fastapi-instrumentator* for metrics, and *OpenTelemetry* for traces are standard.

## How a Senior Engineer Thinks

- *Be aware of PID 1*.
- *Graceful shutdown* is *user trust*.
- *Healthcheck must be light*; check dependencies on *another endpoint*.
- *Non-root* is the *default*.
- Pick *worker count* after *measuring load*.

## Checklist

- [ ] *tini* or equivalent init is used.
- [ ] *Healthcheck* is light and accurate.
- [ ] Container runs as *non-root*.
- [ ] *Graceful shutdown* verified.

## Practice Problems

1. Containerize a FastAPI app and verify `/healthz`.
2. Confirm `docker stop` lets *in-flight requests* complete *before exit*.
3. Add `USER` to run as *non-root*.

## Wrap-up and Next Steps

The real difficulty of Python containers is *signals and healthcheck*. Next, we run *with a database*.

## Answering the Opening Questions

- **Containerizing *FastAPI + uvicorn?**
  - The article treats Containerizing a Python App as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Signal handling at PID 1* (SIGTERM)?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Adding a *healthcheck?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Docker 101 (1/10): What Is Docker?](./01-what-is-docker.md)
- [Docker 101 (2/10): Images and Containers](./02-image-and-container.md)
- [Docker 101 (3/10): Writing a Dockerfile](./03-dockerfile.md)
- [Docker 101 (4/10): Volumes and Networks](./04-volume-and-network.md)
- [Docker 101 (5/10): Docker Compose](./05-docker-compose.md)
- [Docker 101 (6/10): Environment Variables and Configuration](./06-env-and-config.md)
- **Containerizing a Python App (current)**
- Running with a Database (upcoming)
- Image Optimization (upcoming)
- Production-Ready Docker (upcoming)

<!-- toc:end -->

## References

### Official docs

- [FastAPI in containers](https://fastapi.tiangolo.com/deployment/docker/)
- [Uvicorn deployment](https://www.uvicorn.org/deployment/)
- [tini - a tiny init for containers](https://github.com/krallin/tini)
- [Dockerfile HEALTHCHECK](https://docs.docker.com/engine/reference/builder/#healthcheck)

### Verification and troubleshooting

- [Docker stop signal behavior](https://docs.docker.com/reference/cli/docker/container/stop/)

Tags: Docker, Python, FastAPI, Uvicorn, PID1
