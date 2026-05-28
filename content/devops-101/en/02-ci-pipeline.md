---
series: devops-101
episode: 2
title: "DevOps 101 (2/10): CI Pipeline"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - DevOps
  - CI
  - GitHub Actions
  - Automation
  - Pipeline
seo_description: How to design and build a CI pipeline that automates build, test, lint, and security checks for every pull request.
last_reviewed: '2026-05-15'
---

# DevOps 101 (2/10): CI Pipeline

A pull request without a reliable CI pipeline is still a guess. Reviewers can catch logic issues, but they should not be the only layer standing between a typo, a broken import, or a vulnerable dependency and your main branch.

A strong CI pipeline turns quality rules into an executable contract. Every PR sees the same checks in the same order, so the team argues less about process and spends more time fixing real failures.

This is the 2nd post in the DevOps 101 series. Here we focus on the first hard feedback gate in the DevOps loop: how to design CI so it fails fast, explains itself clearly, and earns the team's trust.


![devops 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/devops-101/02/02-01-concept-at-a-glance.en.png)
*devops 101 chapter 2 flow overview*
> A CI pipeline decides *what to verify*, *when*, and *how long to wait*—so quality depends on *system defaults*, not reviewer diligence.

## Questions to Keep in Mind

- What boundary should you inspect first when applying CI Pipeline?
- Which signal should the example or diagram make visible for CI Pipeline?
- What failure should be prevented first when CI Pipeline reaches a real system?

## Questions this article answers

- How is a *CI pipeline* different from simple *test automation*?
- Why should *build*, *test*, *lint*, and *scan* be combined into one *flow*?
- In what order should you design a pipeline to deliver *fast feedback*?
- What does it take for a *failed build* to send a clear signal to the whole team?
- What are the common ways *CI* still breaks down in day-to-day work even after adoption?

## Why It Matters

Tests alone are not enough. *Lint, type checks, and security scans* must be bundled into *one flow* so *opinions* do not creep in.

> A PR without CI is *wishful thinking*.

A CI pipeline is an automated sequence of checks that run every time code is pushed. It should be *fast* (fail early), *clear* (report exactly what broke), and *consistent* (same rules apply to everyone).

## Key Terms

- **Pipeline**: an *ordered sequence of stages*.
- **Stage**: a *logical unit* inside the pipeline (build, test, etc.).
- **Job**: an actual *execution unit*. May run in parallel.
- **Artifact**: a *file passed between stages*.
- **Status check**: the *signal that decides* whether a PR can be merged.

## Before/After

**Before (manual checks)**

```text
- Reviewers *check out and build manually*
- If anyone forgets, *red code* lands on main
```

**After (CI pipeline)**

```yaml
on: [pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ruff check .
  test:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pytest
```

## Hands-on: Five Pipeline Stages

### Step 1 - Lint (fastest, runs first)

```yaml
- run: ruff check .
- run: ruff format --check .
```

### Step 2 - Type check

```yaml
- run: mypy src/
```

### Step 3 - Build

```yaml
- run: python -m build
- uses: actions/upload-artifact@v4
  with: { name: dist, path: dist/ }
```

### Step 4 - Test (parallel)

```yaml
strategy:
  matrix:
    shard: [1, 2, 3, 4]
steps:
  - run: pytest --shard ${{ matrix.shard }}/4
```

### Step 5 - Security scan

```yaml
- uses: aquasecurity/trivy-action@master
  with: { scan-type: fs, severity: HIGH,CRITICAL }
```

## What to Notice in This Code

- *Faster stages* must come *first* to enable *fast failure*.
- *Artifacts* between stages reduce *rebuild cost*.
- Security scans belong *as the final gate*.

## Five Common Mistakes

1. **All stages running *serially*.** Parallelization can cut time by *50%*.
2. **Putting lint *last*.** A 30-minute build flagged red because of *one blank line*.
3. **An environment that *only works in CI*.** No local repro means *debugging hell*.
4. **No required checks.** Red PRs get *merged anyway*.
5. **Logs *too verbose* to find the cause.** Add a *summary step*.

## How This Shows Up in Production

Large monorepos apply *impact analysis* to build and test only the *changed packages*. Bazel, Nx, and Turbo are common choices.

## How a Senior Engineer Thinks

- *The 5-minute rule* — PR feedback must arrive within five minutes.
- On failure, *skip the next stage*.
- *Reproducibility* — CI must be *deterministic*.
- *Secrets* are split *per environment*.
- *The pipeline itself* is subject to *code review*.

## Checklist

- [ ] *Lint, type, test, and scan* all exist.
- [ ] *Required checks* are configured.
- [ ] *Feedback under 5 minutes*.
- [ ] Stages are connected by *artifacts*.

## Practice Problems

1. Split your project's CI into *four or more stages*.
2. *Measure and compare* the runtime after parallelizing.
3. Add *required checks* to your PR merge conditions.

## Wrap-up and Next Steps

A CI pipeline is *the encoded passing line*. In the next post we cover how to *deploy* the *passed code* *safely*.

## Answering the Opening Questions

- **How does a CI pipeline differ from simple test automation?**
  - The CI in this article is not just running tests—it is a flow that bundles lint, mypy, pytest, and Trivy into a single merge gate. Including status checks and artifact concepts means the system consistently determines whether a PR meets team standards.
- **Why must build, test, lint, and scan stages be unified into one flow?**
  - As shown in the examples, lint must pass before test, and test before build—catching problems at the cheapest possible moment. This way required checks and stage dependencies (not reviewer memory) guard main branch quality.
- **What order should a fast-feedback pipeline follow?**
  - The article places the fastest checks (lint and format) first, then type checking and build, and finally slow parallel tests and security scans last. Combined with `matrix`, shard, and cache examples, fast failure and short wait time are the design criteria for good CI.
<!-- toc:begin -->
## In this series

- [DevOps 101 (1/10): What Is DevOps?](./01-what-is-devops.md)
- **CI Pipeline (current)**
- CD and Deployment Strategies (upcoming)
- Environments and Configuration (upcoming)
- Infrastructure as Code (upcoming)
- Containers and Build (upcoming)
- Monitoring and Alerting (upcoming)
- Logging and Analysis (upcoming)
- Incident Response and On-Call (upcoming)
- An Operable DevOps Flow (upcoming)

<!-- toc:end -->

## References

- [GitHub Actions docs](https://docs.github.com/en/actions)
- [Martin Fowler — Continuous Integration](https://martinfowler.com/articles/continuousIntegration.html)
- [Trivy](https://trivy.dev/)
- [Bazel](https://bazel.build/)

Tags: DevOps, CI, GitHub Actions, Automation, Pipeline
