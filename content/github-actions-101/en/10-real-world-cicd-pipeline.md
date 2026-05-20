---
series: github-actions-101
episode: 10
title: "GitHub Actions 101 (10/10): A Real-World CI/CD Pipeline"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - GitHubActions
  - Pipeline
  - CICD
  - Capstone
  - ReusableWorkflow
seo_description: A capstone that ties episodes 1-9 into one pipeline split by PR, main, and tag, standardized with reusable workflows for the whole team.
last_reviewed: '2026-05-15'
---

# GitHub Actions 101 (10/10): A Real-World CI/CD Pipeline

The pieces we covered one by one are all useful, but real systems do not run them in isolation. Triggers, tests, lint, artifacts, Docker, deployment, and secret handling eventually meet in one delivery path, and the quality of that composition determines whether the pipeline scales or collapses under its own weight.

The practical question is not “how many checks can we add?” It is “how clearly can we separate responsibility?” Pull requests need fast feedback. Main needs integration and staging confidence. Tags need traceable release and production promotion. Once those roles are clear, the YAML gets simpler instead of larger.

This is the final post in the GitHub Actions 101 series. In this post, we will combine the earlier topics into a reusable CI/CD shape that separates PR, `main`, and tag responsibilities without losing traceability.

## Questions to Keep in Mind

- What boundary should you inspect first when applying A Real-World CI/CD Pipeline?
- Which signal should the example or diagram make visible for A Real-World CI/CD Pipeline?
- What failure should be prevented first when A Real-World CI/CD Pipeline reaches a real system?

## Big Picture

![github actions 101 chapter 10 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/10/10-01-concept-at-a-glance.en.png)

*github actions 101 chapter 10 flow overview*

This picture places A Real-World CI/CD Pipeline inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of A Real-World CI/CD Pipeline is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## What You Will Learn

- *Responsibility split* across *PR, main, and tag*
- *Reusable workflows* (`workflow_call`) to *eliminate duplication*
- *Composite actions* for grouping steps
- The *team-template repo* pattern
- Five common pitfalls

## Why It Matters

The parts you have learned only improve *DORA* (deploy frequency, lead time, change-failure rate, MTTR) when they sit *together* in one place.

> *The pieces make you *fast*. The composition keeps you *fast*.*

## Concept at a Glance

## Key Terms

- **Reusable workflow**: a *shared workflow* invoked via `workflow_call`.
- **Composite action**: several steps wrapped as one *reusable step*.
- **Template repo**: a repository teams use as a *starting point*.
- **DORA metrics**: the four delivery performance metrics.
- **Promotion**: moving from staging to production.

## Before/After

**Before**: every repo has a *similar but slightly different* workflow. Fix one and the *others drift*.

**After**: a single *shared reusable workflow*. Each repo holds only a *thin caller*. *One change rolls out org-wide*.

## Hands-on: A Real Pipeline in 5 Steps

### Step 1 — Define a reusable workflow

```yaml
# .github/workflows/_ci.yml in org/template-repo
on:
  workflow_call:
    inputs:
      python-version:
        type: string
        default: "3.12"
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: ${{ inputs.python-version }}
      - run: pip install -e ".[dev]"
      - run: ruff check . && mypy . && pytest -q
```

### Step 2 — PR stage (lint + test)

```yaml
# .github/workflows/pr.yml
on:
  pull_request:
jobs:
  ci:
    uses: org/template-repo/.github/workflows/_ci.yml@v1
    with:
      python-version: "3.12"
```

### Step 3 — main stage (build + docker + staging)

```yaml
on:
  push:
    branches: [main]
jobs:
  ci:
    uses: org/template-repo/.github/workflows/_ci.yml@v1
  docker:
    needs: ci
    uses: org/template-repo/.github/workflows/_docker.yml@v1
  deploy-staging:
    needs: docker
    environment: staging
    runs-on: ubuntu-latest
    steps:
      - run: kubectl apply -f k8s/staging/
```

### Step 4 — tag stage (release + production)

```yaml
on:
  push:
    tags: ["v*"]
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: softprops/action-gh-release@v2
  deploy-prod:
    needs: release
    environment: production  # required reviewers ON
    runs-on: ubuntu-latest
    steps:
      - run: kubectl apply -f k8s/production/
```

### Step 5 — Wrap steps with a composite action

```yaml
# .github/actions/setup-app/action.yml
runs:
  using: composite
  steps:
    - uses: actions/setup-python@v6
      with: { python-version: "3.12" }
    - run: pip install -e ".[dev]"
      shell: bash
```

## What success looks like at this point

| Trigger | Expected run shape | What you validate |
| --- | --- | --- |
| Pull request | lint, test, typecheck | feedback stays fast and blocks bad merges |
| `main` push | build, docker, staging | the validated artifact reaches staging unchanged |
| Tag push | release, production | the approved version is traceable all the way to prod |

If your real Actions history matches that table, the responsibility split is doing its job. If pull requests are still running every heavy deployment check, or production can be triggered from an unversioned main build, the pipeline has not been separated enough yet.

## When the pipeline misbehaves, narrow it in this order

1. **PR feedback is too slow**: trim the reusable workflow to the checks reviewers truly need on every change, and watch for oversized matrices.
2. **`main` is unstable**: verify that build outputs, image tags, and staging deployment all refer to the same validated artifact.
3. **Production is risky**: confirm tag-based release, required reviewers, and rollback workflow all still exist as live controls rather than documentation promises.

## Branch protection and promotion policy are half the design

In practice, the workflow file is only half the story. Branch protection rules should require status checks before merge. `main` should not accept casual direct pushes. Production environments should keep reviewers and environment-scoped secrets separate from staging. If those repository-level policies are missing, even a clean YAML design will drift into unsafe operations.

## What to Notice in This Code

- *PR* is for *feedback*, *main* is for *deployment*, *tag* is for *release*.
- *Reusable workflows* are *version-pinned* (`@v1`) so upstream changes do not break you.
- The *production environment* is the *final gate*.

## Five Common Mistakes

1. **Running *full e2e* on every PR.** Feedback now takes 30 minutes.
2. **Deploying *straight to production* from main.** Skipping canary and staging.
3. **Calling reusable workflows with `@main`.** One day it *breaks silently*.
4. **Deploying to *production* without a tag.** No way to trace what shipped.
5. **Composite actions with *no input validation*.** Bad values pass through quietly.

## How This Shows Up in Production

A platform team owns an *org-wide template repo* so every service shares the same *CI/CD skeleton*, while *DORA metrics* are collected automatically by *Sleuth/LinearB*.

## How a Senior Engineer Thinks

- *The trigger decides the responsibility*.
- *Common goes into reusable; differences stay in the caller*.
- *Never give up the production gate*.
- *Templates are code, not wiki pages*.
- *Optimize for what makes DORA improve*.

## Checklist

- [ ] *PR, main, and tag* stages are separated.
- [ ] Common steps are extracted into *reusable workflows*.
- [ ] *production* has *required reviewers*.
- [ ] Reusable workflows are called with a *pinned version*.

## Practice Problems

1. Write a *PR-stage* workflow that runs only *lint, test, typecheck*.
2. Create a *reusable workflow* and call it from two repos with the same CI.
3. Build a workflow where a *tag push* triggers *production deploy* behind an *approval gate*.

## Wrap-up and Next Steps

If you followed along, you can handle *95% of real-world CI/CD*. From here, deepen *runtime* and *operations* with *Docker 101*, *Kubernetes 101*, and *SRE 101*.

## Answering the Opening Questions

- **What boundary should you inspect first when applying A Real-World CI/CD Pipeline?**
  - The article treats A Real-World CI/CD Pipeline as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for A Real-World CI/CD Pipeline?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when A Real-World CI/CD Pipeline reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [GitHub Actions 101 (1/10): What Is GitHub Actions?](./01-what-is-github-actions.md)
- [GitHub Actions 101 (2/10): Workflows and Jobs](./02-workflow-and-job.md)
- [GitHub Actions 101 (3/10): Understanding Triggers](./03-triggers.md)
- [GitHub Actions 101 (4/10): Python Test Automation](./04-python-test-automation.md)
- [GitHub Actions 101 (5/10): Lint and Type Check](./05-lint-and-typecheck.md)
- [GitHub Actions 101 (6/10): Build Artifacts](./06-build-artifact.md)
- [GitHub Actions 101 (7/10): Docker Build](./07-docker-build.md)
- [GitHub Actions 101 (8/10): Deployment Automation](./08-deploy-automation.md)
- [GitHub Actions 101 (9/10): Secret Management](./09-secret-management.md)
- **A Real-World CI/CD Pipeline (current)**

<!-- toc:end -->

## References

- [Reusing workflows](https://docs.github.com/actions/using-workflows/reusing-workflows)
- [Creating a composite action](https://docs.github.com/actions/creating-actions/creating-a-composite-action)
- [DORA - Accelerate State of DevOps](https://dora.dev/)
- [Creating a template repository](https://docs.github.com/repositories/creating-and-managing-repositories/creating-a-template-repository)

Tags: GitHubActions, Pipeline, CICD, Capstone, ReusableWorkflow
