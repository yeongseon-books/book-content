---
series: github-actions-101
episode: 2
title: "GitHub Actions 101 (2/10): Workflows and Jobs"
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
  - Workflow
  - Job
  - Matrix
  - CICD
seo_description: Workflow, Job, and Step structure with dependencies. Master parallelism and ordering in your CI graph.
last_reviewed: '2026-05-15'
---

# GitHub Actions 101 (2/10): Workflows and Jobs

Once you start using GitHub Actions, the next question is rarely about YAML syntax. It is about structure. Should lint and test live in one job? Should deploy wait for build only, or for every earlier check? When does a single workflow become harder to reason about than several smaller ones?

Those questions are really about pipeline design. A workflow file is only the container. The actual pipeline is the graph of jobs inside it, and the quality of that graph determines both feedback speed and operational safety.

This is post 2 in the GitHub Actions 101 series. In this post, we will map the relationship between workflows, jobs, and steps, then use `needs`, `matrix`, and `outputs` to design a graph that is fast without becoming fragile.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Workflows and Jobs?
- Which signal should the example or diagram make visible for Workflows and Jobs?
- What failure should be prevented first when Workflows and Jobs reaches a real system?

## Big Picture

![github actions 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/02/02-01-concept-at-a-glance.en.png)

*github actions 101 chapter 2 flow overview*

This picture places Workflows and Jobs inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## What You Will Learn

- The exact relationship between *Workflow / Job / Step*
- Expressing dependencies with *jobs.<id>.needs*
- Running *many environments* with *matrix*
- Passing values between jobs with *outputs*
- Five common mistakes

## Why It Matters

A fully *serial* CI is slow; a fully *parallel* one *breaks ordering*. Drawing the *job graph* correctly is what makes a pipeline *fast and safe*.

> *Parallel for speed, dependencies for safety*.

## Key Terms

- **Workflow**: one *YAML file* equals one workflow.
- **Job**: a *unit of execution* in a workflow; jobs run *in parallel* by default.
- **Step**: a *command* or *Action call* inside a Job.
- **needs**: declares *dependencies* between Jobs.
- **matrix**: *replicates* a Job across *combinations of variables*.
- **outputs**: values a Job *passes* to the next Job.

## Before/After

**Before**: every step crammed into *one Job* — a *six-minute serial* pipeline.

**After**: split into *three parallel jobs* (lint / test / build) with *deploy needs build* — a *two-minute graph* pipeline.

## Hands-on: Job Graph in 5 Steps

### Step 1 — Split into jobs

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: ruff check .

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: pytest -q
```

### Step 2 — Order with needs

```yaml
  build:
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps:
      - uses: actions/checkout@v6
      - run: python -m build
```

### Step 3 — Multiple environments via matrix

```yaml
  test:
    strategy:
      matrix:
        python: ["3.10", "3.11", "3.12"]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: ${{ matrix.python }}
      - run: pytest -q
```

### Step 4 — Pass values via outputs

```yaml
  build:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.v.outputs.version }}
    steps:
      - id: v
        run: echo "version=1.2.3" >> "$GITHUB_OUTPUT"

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: echo "deploy ${{ needs.build.outputs.version }}"
```

### Step 5 — Failure policy: continue-on-error

```yaml
  flaky:
    continue-on-error: true
    runs-on: ubuntu-latest
    steps:
      - run: pytest tests/flaky.py
```

## What to Notice in This Code

- *needs* is a *DAG*.
- *matrix* watch for *combinatorial explosion*.
- *outputs* carries *strings only*.

## Five Common Mistakes

1. **All steps in *one Job*.** Lost parallelism.
2. **Missing `needs`.** Dependencies become *implicit*.
3. **A *huge matrix*.** Build cost explodes.
4. **Complex *objects in outputs*.** Serialization breaks.
5. **No `if:` conditions.** Unnecessary jobs run *every time*.

## How This Shows Up in Production

Mature teams run *fast lint+test only* on *PRs* and a *full matrix + build* on *main push* — a *two-tier graph*.

## How a Senior Engineer Thinks

- *Job decomposition* drives *feedback time*.
- Add *matrix only when needed*.
- *needs* expresses *business intent*.
- *outputs* is for *simple values* only.
- Use *if* to remove *unnecessary runs*.

## Checklist

- [ ] *lint / test / build* are separated.
- [ ] *needs* makes dependencies explicit.
- [ ] *matrix* is sized for cost.
- [ ] *outputs* carry only *strings*.

## Practice Problems

1. Build a *3-job graph* (lint, test, build).
2. Add a *Python 3.11/3.12* matrix to test.
3. Have *deploy* consume the *version output* from build.

## Wrap-up and Next Steps

The job graph is the *spine of your pipeline*. The next post covers *when it runs (Trigger)*.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Workflows and Jobs?**
  - The article treats Workflows and Jobs as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Workflows and Jobs?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Workflows and Jobs reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [GitHub Actions 101 (1/10): What Is GitHub Actions?](./01-what-is-github-actions.md)
- **Workflows and Jobs (current)**
- Understanding Triggers (upcoming)
- Python Test Automation (upcoming)
- Lint and Type Check (upcoming)
- Build Artifacts (upcoming)
- Docker Build (upcoming)
- Deployment Automation (upcoming)
- Secret Management (upcoming)
- A Real-World CI/CD Pipeline (upcoming)

<!-- toc:end -->

## References

- [Workflow syntax](https://docs.github.com/actions/using-workflows/workflow-syntax-for-github-actions)
- [Using jobs in a workflow](https://docs.github.com/actions/using-jobs/using-jobs-in-a-workflow)
- [Using a matrix for jobs](https://docs.github.com/actions/using-jobs/using-a-matrix-for-your-jobs)
- [Defining outputs for jobs](https://docs.github.com/actions/using-jobs/defining-outputs-for-jobs)

Tags: GitHubActions, Workflow, Job, Matrix, CICD
