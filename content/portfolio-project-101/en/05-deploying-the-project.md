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

This is post 5 in the Portfolio Project 101 series. Here we will treat deployment not as a giant infrastructure project, but as the discipline of creating a public URL, separating secrets, keeping a repeatable release path, and exposing a basic health check.

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

```python
env = {"DATABASE_URL": "...", "SECRET_KEY": "..."}
```

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

## Answering the Opening Questions

- **Why is a public URL close to mandatory for a portfolio project?**
  - The article treats Deploying the Project as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **What should you optimize for when choosing a hosting platform?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Why should secrets and environment configuration live outside the codebase?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

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
