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
