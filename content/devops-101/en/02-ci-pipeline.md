---
series: devops-101
episode: 2
title: CI Pipeline
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

# CI Pipeline

A pull request without a reliable CI pipeline is still a guess. Reviewers can catch logic issues, but they should not be the only layer standing between a typo, a broken import, or a vulnerable dependency and your main branch.

A strong CI pipeline turns quality rules into an executable contract. Every PR sees the same checks in the same order, so the team argues less about process and spends more time fixing real failures.

This is post 2 in the DevOps 101 series. Here we focus on the first hard feedback gate in the DevOps loop: how to design CI so it fails fast, explains itself clearly, and earns the team's trust.

## Questions this article answers

- How is a *CI pipeline* different from simple *test automation*?
- Why should *build*, *test*, *lint*, and *scan* be combined into one *flow*?
- In what order should you design a pipeline to deliver *fast feedback*?
- What does it take for a *failed build* to send a clear signal to the whole team?
- What are the common ways *CI* still breaks down in day-to-day work even after adoption?

## Why It Matters

Tests alone are not enough. *Lint, type checks, and security scans* must be bundled into *one flow* so *opinions* do not creep in.

> A PR without CI is *wishful thinking*.

## Concept at a Glance

![Concept at a Glance](https://yeongseon-books.github.io/book-public-assets/assets/devops-101/02/02-01-concept-at-a-glance.en.png)

*Concept at a Glance*

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

<!-- toc:begin -->
- [What Is DevOps?](./01-what-is-devops.md)
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
