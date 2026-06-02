---
title: "AI Web Development 101 (6/7): Deploying an AI web app — shipping to Vercel and Azure"
series: ai-web-dev-101
episode: 6
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI
- LLM
- Web Development
- Python
- Tutorial
last_reviewed: '2026-05-14'
seo_description: Deploy a local AI app to Vercel and Azure App Service while handling startup commands, environment variables, logs, and cost guardrails.
---

> **Deprecation notice**: This series is superseded by [`llm-app-foundations-101`](../../llm-app-foundations-101/en/) and [`ai-app-patterns-101`](../../ai-app-patterns-101/en/). New readers are encouraged to start with the successor series.

# AI Web Development 101 (6/7): Deploying an AI web app — shipping to Vercel and Azure

An AI app that only works on your laptop is still a local experiment. Once other people need to access it, deployment turns secrets, startup commands, logging, and budget control into real operational concerns.

This is the 6th post in the AI Web Development 101 series.

Here, we will walk through the first deployment path for a frontend-heavy app on Vercel and a Python backend on Azure App Service.


![AI Web Development 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/06/local-to-live-deployment.en.png)
*AI Web Development 101 chapter 6 flow overview*

> Deploying an AI app is the moment secrets, startup commands, logs, and cost ceilings stop being local concerns — the platform you pick (Vercel for frontend, Azure for Python backend) decides which of those concerns is hardest.

## Questions to Keep in Mind

- Why is deployment more than uploading source code?
- When does Vercel fit better, and when does Azure App Service fit better?
- What should you verify first in Vercel?

## What to prepare before deployment

Before you deploy, verify four things:

- dependency files actually describe the runtime you need
- secrets are injected through environment variables, not source code
- the application entry point is explicit
- the app can bind to the platform-provided port

## Picking a platform

| Option | Vercel | Azure App Service |
| --- | --- | --- |
| Best fit | frontend-heavy Next.js apps | Python or mixed backend workloads |
| Setup style | minimal | more explicit runtime configuration |
| Typical beginner benefit | fastest first deployment | better control over backend runtime |

A common combination is simple: frontend on Vercel, Python API on Azure.

![Comparing the Vercel and Azure hosting structure](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/06/vercel-azure-hosting-overview.en.png)

*Comparing the Vercel and Azure hosting structure*

## Deploying to Vercel

### Step 1: push the repository

```bash
GIT_MASTER=1 git add .
GIT_MASTER=1 git commit -m "feat: initial AI chatbot"
GIT_MASTER=1 git push origin main
```

### Step 2: import the project

1. Sign in to [Vercel](https://vercel.com).
2. Choose **Add New > Project**.
3. Import your GitHub repository.

### Step 3: set environment variables

Add `OPENAI_API_KEY` through the Vercel project settings. Do not commit the real value.

### Step 4: verify the deployment

After deployment, inspect the build log first. Missing dependencies, missing environment variables, and type errors usually show up there before you ever open the app URL.

![The runtime path from deployed app to model call](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/06/production-request-path.en.png)

*The runtime path from deployed app to model call*

## Deploying a Python app to Azure App Service

For Flask or FastAPI, App Service is a good beginner option, but it expects you to be more explicit about startup behavior.

### Step 1: log in with the Azure CLI

```bash
az login
az account list --output table
```

### Step 2: make sure the Python dependencies are present

```text
fastapi
uvicorn[standard]
gunicorn
openai
```

### Step 3: use `az webapp up` for the first deployment

```bash
az webapp up --sku F1 --name my-ai-chatbot-app --location koreacentral
```

This is a good first path because it creates the resource group, plan, and app together.

### Step 4: make the startup command explicit

```bash
az webapp config set   --resource-group myResourceGroup   --name my-ai-chatbot-app   --startup-file "gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app"
```

Without this, a deployment can appear successful while the app still fails to boot correctly.

### Step 5: inject the API key

```bash
az webapp config appsettings set   --name my-ai-chatbot-app   --resource-group myResourceGroup   --settings OPENAI_API_KEY="$OPENAI_API_KEY"
```

### Step 6: read live logs first

```bash
az webapp log tail --name my-ai-chatbot-app --resource-group myResourceGroup
```

This is usually where missing environment variables, package-install failures, or startup-command mistakes become obvious.

## Secret handling is part of deployment design

The most common beginner mistake is committing an API key directly into source code. In AI apps, that can turn into a billing incident immediately.

```text
# .gitignore
.env
__pycache__/
node_modules/
.venv/
.DS_Store
```

Only commit an example file such as `.env.example`. Keep the real values in local environments and deployment platform settings.

![Environment-variable boundaries versus hardcoded secret exposure](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/06/secret-key-boundary.en.png)

*Environment-variable boundaries versus hardcoded secret exposure*

## Cost and monitoring basics

Even if hosting starts on a free tier, model calls can still create ongoing cost. The operational goal is to catch unexpected spend and quiet failures early.

- set an OpenAI budget or usage threshold
- create Azure budget alerts if you use App Service
- inspect deployment logs immediately after each rollout
- watch cold-start behavior and 500-level errors on the live URL

![Operational checks from budget guardrails to error visibility](https://yeongseon-books.github.io/book-public-assets/assets/ai-web-dev-101/06/cost-guardrails-flow.en.png)

*Operational checks from budget guardrails to error visibility*

## Checklist

- [ ] Dependency files and startup commands match the deployment runtime.
- [ ] Secrets are injected only through environment variables.
- [ ] I know where to read logs right after deployment.
- [ ] I configured budget or usage alerts before opening the app widely.

## First 24-Hour Post-Deployment Verification Scenario

The most common oversight in initial deployment is checking only the "success screen" without verifying the actual usage flow end-to-end. The first 24 hours after deployment are safer spent focusing on operational signal verification rather than feature checks.

### 1) User-path verification

- Send prompts of different lengths (first request, second request, long request) and verify response time distribution.
- Separate normal questions, edge-case questions, and failure-inducing questions to verify HTTP status codes and error message consistency.
- If frontend and backend are separated, verify that CORS, timeout, and retry policies actually work.

### 2) Log quality verification

- Verify that request IDs pass through from frontend logs to backend logs.
- Verify that on model call failure, users receive a safe message while internal logs record the cause code.
- Reproduce operational errors (missing key, permission error, quota exceeded) and verify the alert path end-to-end.

### 3) Cost safeguard verification

- Estimate the slope of token usage growth as daily request count increases.
- If per-model pricing differs, verify via sample logs that routing rules apply as intended.
- Mock-test that budget threshold alerts actually reach the contact channel (email, messenger).

This verification is not a process that slows development — it is a pre-investment that reduces future incident response time. AI apps in particular create incidents from data, model, and cost factors interleaving rather than pure code bugs, so establishing operational observation lines early is crucial.

## Fixing the Pre-Deployment Checklist Alongside Code

To repeat deployments reliably, store the checklist in the repository instead of relying on personal memory. AI apps have higher environment variable dependency than typical web apps — a single missing value can show users nothing but "no response."

```bash
# Common pre-deployment checks
python3 -m pytest tests
npm run lint
npm run build
python3 scripts/check_env_required.py --env-file .env.production.example
```

If verification scripts are not connected to the deployment pipeline, the process eventually reverts to manual checks and incident probability rises.

## Vercel Frontend Deployment Configuration

For Next.js-based chatbot frontends, deploying to Vercel first has the lowest barrier to entry. However, the frontend-backend URL contract must be clear to prevent cross-environment confusion.

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "env": {
    "NEXT_PUBLIC_API_BASE_URL": "https://api.example.com",
    "AI_MODEL": "gpt-4o-mini"
  }
}
```

Environment variable names must match the constant names in code exactly. Even small discrepancies often cause silent runtime failures.

## Azure App Service Backend Deployment Example

When deploying a Python API server to Azure App Service, fix the startup command and health check path first.

```yaml
# startup command example
gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000 --timeout 120
```

```bash
az webapp config appsettings set \
  --resource-group rg-ai-web-dev \
  --name ai-web-dev-api \
  --settings OPENAI_API_KEY="***" AI_MODEL="gpt-4o-mini" LOG_LEVEL="INFO"
```

The health check path (`/healthz`) should not include model calls — it should only quickly verify process and dependency connection state.

## Operational Settings: Timeout, Retry, Circuit Breaker

AI APIs are affected by network and provider state, so deployment environments must explicitly declare time limits and retry policies.

```python
CALL_TIMEOUT_SEC = 20
MAX_RETRY = 2
RETRY_BACKOFF_SEC = [0.5, 1.0]
```

Additionally, when failures accumulate beyond a threshold, the circuit breaker pattern temporarily stops calls and returns an outage notice to users — a pattern commonly used in practice.

## Post-Deployment Verification Scenarios

Ending at the deployment success message almost guarantees missed problems. Automate at minimum these scenarios.

1. Normal query: response code 200, JSON schema passes
2. Invalid input: 4xx and error message convention check
3. Model failure simulation: 5xx response message check
4. Timeout simulation: retry count and final error check
5. Excessive token input: length limit behavior check

## Dashboard Baseline Items for Evaluation Metrics

During the first week after deployment, keep the dashboard simple.

- Request count, error rate, p95 latency
- Average prompt_tokens, completion_tokens
- User feedback (helpful/not helpful)
- Cost estimate per route
- Performance comparison by deployment version

These five items alone enable early detection of "performance degradation," "cost spikes," and "specific version regression."

## Security Baseline: Key Management and Access Control

The most dangerous mistake at the deployment stage is exposing API keys in code repositories or client bundles. Production keys must go in the platform secret store, with permission scope minimized.

- Separate production keys from development keys.
- Set key rotation cycle at monthly intervals.
- Document a procedure for immediate revocation when anomalous traffic is detected.

Additionally, admin pages and internal diagnostic APIs need IP restrictions or authentication gates to reduce unnecessary exposure.

## Production Deployment Pipeline Example

Deployments are more stable with declarative pipelines than manual clicks. Structuring like below clearly separates failure points.

```yaml
name: deploy-ai-web-app
on:
  push:
    branches: [main]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm run build
      - run: python3 -m pip install -r requirements.txt
      - run: python3 -m pytest -q

  deploy:
    needs: verify
    runs-on: ubuntu-latest
    steps:
      - run: ./scripts/deploy_vercel.sh
      - run: ./scripts/deploy_azure_api.sh
```

Separating verification and deployment stages lets you quickly pinpoint the cause when problems occur.

## Documenting Rollback Criteria in Advance

Deciding rollback criteria ad-hoc when failure happens is too late. Agree on these thresholds beforehand.

- 5-minute average error rate exceeds 5%
- p95 latency increases 2x or more vs. baseline
- Authentication errors occur consecutively

With explicit criteria, even when responsibility transfers between team members the same judgment can be reproduced.

## Automated Post-Deployment Health Check Commands

Fixing health check commands as scripts to run within 10 minutes of deployment makes overnight incident response much easier.

```bash
curl -fsS https://api.example.com/healthz
curl -fsS https://api.example.com/api/ask -H 'content-type: application/json' -d '{"question":"health check","user_id":"monitor"}'
```

The purpose of these commands is not full functional verification but quickly confirming "the service is available right now."

## Cost Cap Guard

AI apps can see cost spikes even during normal operation, so daily caps and alert thresholds are necessary.

- Daily cost cap: $100
- Alert when 1-hour moving average rises 2x vs. baseline
- Auto-enable sampling logs when tokens spike on a specific endpoint

This guard prevents quality issues from escalating into cost incidents.

### Post-Deployment 24-Hour Observation

During the first 24 hours, prioritize observation over feature additions. Verify that error rate, latency, and token usage enter a stable range before planning the next release — this is safer long-term.


## Summary

Deployment is not the final coding step. It is the first real operating step.

- Vercel is a strong starting point for frontend-heavy AI apps.
- Azure App Service is flexible for Python backends, but it rewards explicit runtime configuration.
- Secret handling belongs inside the deployment design, not outside it.
- Logs and budget alerts should be in place before real user traffic arrives.

The final chapter focuses on what happens after deployment: how to measure response quality, catch regressions, and improve an AI app over time.

## Answering the Opening Questions

- **What does deployment actually prepare, beyond a simple upload?**
  - Deployment is not uploading code files; it is locking `requirements.txt` and `package.json`, start commands, ports, environment variables, and verification scenarios against the execution environment. The article placed `python3 -m pytest tests`, `npm run lint`, `npm run build`, and `python3 scripts/check_env_required.py --env-file .env.production.example` as pre-deploy common checks. What matters more than uploading is deciding "what the server runs and how" in advance.
- **Which platform should you deploy a Next.js app and a Python backend to first?**
  - A UI-centric Next.js app fits Vercel naturally, while a Python API requiring runtime control (`gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000 --timeout 120`) fits Azure App Service. That is why `NEXT_PUBLIC_API_BASE_URL` and `AI_MODEL` appeared in the Vercel example while `OPENAI_API_KEY`, `LOG_LEVEL`, and the startup command appeared in the Azure example. Using both reflects the different operational characteristics of frontend and backend.
- **What should you verify first on Vercel?**
  - First verify that environment variables like `OPENAI_API_KEY` actually reached the deployment environment and that the build log shows no dependency or type errors. After deploy, go beyond checking that `[project].vercel.app` loads—confirm `Functions > app/api/chat/route.ts > maxDuration=30`, run `vercel env add OPENAI_API_KEY production`, and test the first request, a long request, and a failure request on the real user path. The 24-hour post-deploy checklist existed to lock that verification sequence.
<!-- toc:begin -->
## In this series

- [AI Web Development 101 (1/7): AI API first steps — sending your first request with the OpenAI API](./01-hello-ai-api.md)
- [AI Web Development 101 (2/7): Prompt engineering basics — getting the answer you actually want](./02-prompt-engineering.md)
- [AI Web Development 101 (3/7): Building an AI chatbot — real-time chat with Next.js and the Vercel AI SDK](./03-ai-chatbot.md)
- [AI Web Development 101 (4/7): RAG introduction — answering with your own data](./04-rag-intro.md)
- [AI Web Development 101 (5/7): First steps with AI agents — making the model use tools](./05-ai-agent.md)
- **Deploying an AI web app — shipping to Vercel and Azure (current)**
- Evaluating and improving an AI app — measuring quality over time (upcoming)

<!-- toc:end -->

## References

- [Vercel documentation](https://vercel.com/docs)
- [Azure App Service Python quickstart](https://learn.microsoft.com/azure/app-service/quickstart-python)
- [OpenAI production best practices](https://platform.openai.com/docs/guides/production-best-practices)
- [Azure Cost Management documentation](https://learn.microsoft.com/azure/cost-management-billing/)

Tags: AI, LLM, Web Development, Python, Tutorial
