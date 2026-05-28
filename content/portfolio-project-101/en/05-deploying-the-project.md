---
series: portfolio-project-101
episode: 5
title: "Portfolio Project 101 (5/10): Deploying the Project"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Portfolio
  - Deploy
  - DevOps
  - Hosting
  - Beginner
seo_description: How to deploy a portfolio project so other people can verify it through a stable URL, a health check, and a repeatable release path.
last_reviewed: '2026-05-15'
---

# Portfolio Project 101 (5/10): Deploying the Project

A portfolio project is only halfway finished if it runs on localhost and nowhere else. There is a big difference between saying the project works and giving another person a URL where they can verify it. Without that public path, the project still depends on explanation.

This is the 5th post in the Portfolio Project 101 series. Here we will treat deployment not as a giant infrastructure project, but as the discipline of creating a public URL, separating secrets, keeping a repeatable release path, and exposing a basic health check.

---

> Deployment is not about getting the app up once. It is about making the app reachable, repeatable, and inspectable.


![portfolio project 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/portfolio-project-101/05/05-01-concept-at-a-glance.en.png)
*portfolio project 101 chapter 5 flow overview*
> Code that only runs locally is not evidence. When deployed so anyone can access it, then and only then does it read like an intentionally completed project.

## Questions to Keep in Mind

- Why is a public URL close to mandatory for a portfolio project?
- What should you optimize for when choosing a hosting platform?
- Why should secrets and environment configuration live outside the codebase?

## Why It Matters

Deployment connects your work to the outside world. Hiring reviewers do not evaluate a portfolio by imagining your laptop environment. They click, inspect, and decide whether the project feels real.

A deployment setup also reveals operational judgment. Even a small project looks stronger when secrets are separated, redeploys follow the same path, and there is an obvious way to confirm service health.

## Mental Model

You do not need a complicated model: code is pushed, built, deployed, checked, and then made available through a public URL.

This flow is also what helps you debug. Was the build broken? Did deployment finish but the app fail to start? Is the URL reachable while internal state is unhealthy? Reviewers will not ask those questions explicitly, but your project feels more mature when the deployment story can answer them.

## Key Terms

- **Hosting**: the service that runs the application.
- **Official URL**: the public address you want people to use and remember.
- **Environment variables**: deployment-time configuration and secrets.
- **Continuous delivery**: a repeatable path from code change to deployment.
- **Health check**: a small route that tells you whether the app is alive enough to serve traffic.

## Before and After

**Before**: only localhost works, and no one else can verify the result.

**After**: the project has a public URL, secrets live outside the code, and the app can be redeployed through a known path.

The second project reads like an operating service instead of a local exercise.

## Step by Step

### Step 1 — Choose simple hosting first

You do not need a complex platform to make a portfolio project credible.

Pick one understandable platform first—Fly.io, Render, or Railway are all reasonable beginner choices.

The best beginner choice is usually the platform you can understand, redeploy, and afford to keep alive.

### Step 2 — Separate environment variables

Public repositories should never carry real secrets.

For example, values such as `DATABASE_URL` and `SECRET_KEY` should live in deployment environment variables rather than in code.

This separation is both a security baseline and an operational baseline. It lets you distinguish local, test, and production settings cleanly.

### Step 3 — Keep the build path explicit

Deployment should be a repeatable process, not a manual ritual.

```bash
docker build -t app .
```

A container image is often the easiest way to reduce machine-specific surprises and make the run environment legible.

### Step 4 — Make the actual deploy repeatable

One successful push is not enough if you cannot do it again reliably.

```bash
fly deploy
```

Repeatability matters because portfolio demos age quickly. If updating the demo is painful, the project goes stale fast.

### Step 5 — Add a health check

Deployment is not complete until you have a quick signal for service state.

That signal can be as simple as a health-check URL such as `https://app.fly.dev/healthz`.

That small route gives you a first check when something looks wrong, and it makes operations feel less guess-driven.

## What to Notice in the Code

- Hosting should optimize for simplicity and maintainability before sophistication.
- Environment variables are the basic safety layer for public work.
- Health checks and repeatable deploys are visible signs of operational awareness.

## Common Mistakes

1. Leaving secrets in code or in README examples.
2. Having multiple URLs with no clear “official” one.
3. Shipping no health route, so a broken demo is harder to diagnose.
4. Ignoring monthly cost until the demo quietly disappears.
5. Relying on a manual redeploy path that discourages updates.

These are not just infrastructure mistakes. They shorten the life of the demo itself.

## How This Reads in Practice

Small startups and solo products often begin on platforms such as Render, Fly.io, Railway, or Vercel because they reduce operational friction. The same logic applies to a portfolio.

What matters most is not how ambitious the infrastructure sounds. It is whether the public URL stays usable and the project can be updated without drama.

## Checklist

- [ ] I picked one hosting platform on purpose.
- [ ] The official public URL is documented clearly.
- [ ] Database credentials and secrets live in environment variables.
- [ ] There is at least one health-check route.

## Practice Problems

1. Pick one hosting option for your project and write down why it fits.
2. Name three values that should move from code into environment variables.
3. Decide what route you would check first if the demo stopped working.

## Wrap-up and Next Steps

Portfolio deployment does not require giant infrastructure. A public URL, separated secrets, a repeatable deployment path, and a basic health check already go a long way. Once those exist, even a small project starts to read like something another person can trust.

Next, we will turn that trust into explicit proof through tests, documentation, and automated verification.

### CI/CD Pipeline YAML Example

To raise deployment quality, you need "verified then deployed on every code change" rather than "deployed once successfully." The example below is a minimal CI/CD pipeline structure suitable for portfolio projects.

```yaml
name: ci-cd
on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: pytest -q

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t app:${{ github.sha }} .

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - run: ./scripts/deploy.sh
```

The key is ordering. Tests gate the build, and builds gate the deploy. This alone dramatically reduces demo outages.

### Test Strategy Table

Writing many tests matters less than deciding which failures get caught where.

| Test Type | Purpose | Example | When |
| --- | --- | --- | --- |
| Unit test | Catch logic errors early | Date normalization function | Every PR |
| Integration test | Verify API-DB boundary | `/healthz`, `/schedule` responses | Every PR |
| Smoke test | Confirm survival post-deploy | Main page and health check | Right after deploy |
| Regression check | Preserve critical flows | Login-query-share scenario | Before release |

Including this table in README or `docs/testing.md` signals that verification is designed, not accidental.

### Deploy Failure Runbook (Minimal Version)

A short runbook prevents panic when deploys fail. Even basic step-by-step checkpoints speed up problem classification.

```markdown
## Deploy Failure Runbook
1. Check if CI test job failed
2. Review Docker build logs for dependency/network errors
3. Verify no environment variables are missing on the platform
4. Check `/healthz` status code and response body
5. Roll back to last known-good version
```

A runbook in a portfolio project is not overkill. It is strong evidence of operational thinking. Even a small project looks notably more complete when it has failure-handling standards.

### Environment Variable Management Guide

Environment variables are not just configuration. They are the boundary between security and operational quality.

| Category | Example | Storage | Note |
| --- | --- | --- | --- |
| Secrets | SECRET_KEY, DB_PASSWORD | Platform secrets | Never commit to repo |
| Per-environment | APP_ENV, LOG_LEVEL | Separate dev/prod | Specify defaults |
| Public values | FEATURE_FLAG | Config file/docs | Explain purpose |

```markdown
.env.example principles
- Use placeholders instead of real passwords
- Separate required vs optional variables
- Describe expected format and type
```

This organization alone dramatically speeds up migration to new environments and simplifies failure root-cause analysis.

### Full GitHub Actions Deploy Pipeline

A complete CI/CD setup for a FastAPI app deployed to Render:

```yaml
# .github/workflows/deploy.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: '3.11'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Lint
        run: ruff check .

      - name: Type check
        run: mypy src/

      - name: Test
        run: pytest --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: |
          docker build -t ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} .
          docker tag ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} \
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Render
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}

      - name: Wait for deploy
        run: sleep 30

      - name: Health check
        run: |
          STATUS=$(curl -s -o /dev/null -w "%{http_code}" ${{ secrets.APP_URL }}/healthz)
          if [ "$STATUS" != "200" ]; then
            echo "Deploy failed! Health check returned $STATUS"
            exit 1
          fi
```

The pipeline separates into three stages: test → build → deploy. If an earlier stage fails, later stages do not run. PRs run only tests; build/deploy trigger only on main push.

### Dockerfile Basics

A deployable project needs a Dockerfile. Below is a baseline for a FastAPI project.

```dockerfile
# Dockerfile
FROM python:3.11-slim AS base

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY scripts/seed_demo_data.py ./scripts/

# Generate demo seed data
RUN python scripts/seed_demo_data.py

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Key points:

1. **Slim image**: Smaller image means faster deploys.
2. **Copy requirements.txt first**: Layer caching shortens build time.
3. **Include seed data**: Prevents an empty screen in the demo environment.
4. **Explicit port**: Documents which port the app uses.

### Health Check Endpoint

A health check endpoint is simple but high-impact:

```python
# src/health.py
from fastapi import APIRouter

router = APIRouter()


@router.get("/healthz")
def health_check():
    return {"status": "ok", "version": "1.0.0"}
```

With this endpoint, CI/CD can automatically determine deploy success, and monitoring tools can detect downtime.

### Hosting Cost Comparison

Portfolio projects need to stay alive long-term, so cost matters. Most portfolio projects fit within free tiers.

| Platform | Free Tier | Limitations | Best For |
| --- | --- | --- | --- |
| Vercel | Unlimited deploys | Serverless/static only | Frontend, Next.js |
| Render | 750 hrs/month | Sleeps after 15 min inactivity | API servers |
| Railway | $5 credit/month | Stops when exhausted | Full-stack |
| Fly.io | 3 VMs | 256 MB RAM | Container-based |
| GitHub Pages | Unlimited | Static sites only | Portfolio website |

Recommended strategy: Vercel for frontend, Render or Railway for API, GitHub Pages for portfolio website. This runs at $0/month. Migrate when you actually hit limits.

### Post-Deploy Checklist

After deploy completes, verify in this order:

```text
[ ] Public URL loads first screen
[ ] Health check endpoint returns 200
[ ] No missing environment variables (check error logs)
[ ] HTTPS applied (browser lock icon visible)
[ ] Seed data displays correctly
[ ] README demo URL matches deployed URL
[ ] Mobile layout renders properly
```

Passing this checklist means the project meets minimum requirements as a deployed artifact. Recording this in the README shows reviewers your operational perspective.

### Docker Compose for Local/Production Parity

"Works on my machine" problems almost always come from environment differences. Docker Compose minimizes the gap between local and production.

```yaml
# docker-compose.yml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/portfolio
      - APP_ENV=development
      - SECRET_KEY=${SECRET_KEY:-dev-secret-key}
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: portfolio
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 5s
      retries: 3
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

Add this to your README and anyone can reproduce the same environment:

```bash
# Local run (3 steps)
git clone https://github.com/username/task-tracker.git
cd task-tracker
docker compose up --build
# Verify at http://localhost:8000
```

The advantage is that dependency versions, OS, and runtime differences are all isolated in containers. It eliminates "works on my machine" conversations entirely.

## Answering the Opening Questions

- **Why is a public URL nearly essential for a portfolio project?**
  - Code that only works locally is not evidence. A public URL lets reviewers verify directly, and only then does it read as a completed project.
- **What criteria should guide hosting platform choice over flashiness?**
  - Repeatability, low cost, and operational simplicity are the criteria. Whether you can redeploy with the same procedure matters more than fancy infrastructure.
- **Why should secrets and environment variables be managed in the deployment environment, not in code?**
  - Putting secrets in code exposes them when the repository goes public. Separating them into environment variables in the deployment environment secures both security and operational flexibility.
<!-- toc:begin -->
## In this series

- [Portfolio Project 101 (1/10): What is a Portfolio Project](./01-what-is-a-portfolio-project.md)
- [Portfolio Project 101 (2/10): Traits of a Good Project](./02-traits-of-a-good-project.md)
- [Portfolio Project 101 (3/10): Writing the README](./03-writing-the-readme.md)
- [Portfolio Project 101 (4/10): Building the Demo](./04-building-the-demo.md)
- **Deploying the Project (current)**
- Tests and Documentation (upcoming)
- Recording Tech Decisions (upcoming)
- Summarizing as Blog Posts (upcoming)
- Explaining in Interviews (upcoming)
- Portfolio Improvement Checklist (upcoming)

<!-- toc:end -->

## References

- [The Twelve-Factor App](https://12factor.net/)
- [Deploying Containers on Render](https://render.com/docs/deploy-an-image)
- [Fly.io Docs](https://fly.io/docs/)
- [GitHub Actions documentation](https://docs.github.com/en/actions)

Tags: Portfolio, Deploy, DevOps, Hosting, Beginner
