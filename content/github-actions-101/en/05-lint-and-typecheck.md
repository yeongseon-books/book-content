---
series: github-actions-101
episode: 5
title: "GitHub Actions 101 (5/10): Lint and Type Check"
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
  - Lint
  - Ruff
  - Mypy
  - QualityGate
seo_description: Automate code-quality gates with ruff, mypy, and pre-commit so PR review focuses on logic, not style.
last_reviewed: '2026-05-15'
---

# GitHub Actions 101 (5/10): Lint and Type Check

If code review keeps starting with import order, line length, and obvious type errors, the team is spending expensive human attention on work a machine can do faster and more consistently. That is usually a sign that the quality gate is either missing or too soft to be trusted.

The goal of lint and type checks is not to slow developers down. It is to remove low-value review noise so humans can focus on design, failure modes, and the operational consequences of a change.

This is the 5th post in the GitHub Actions 101 series. In this post, we will use Ruff, Mypy, and pre-commit to turn style and type rules into an explicit CI gate instead of an informal team habit.


![github actions 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/05/05-01-concept-at-a-glance.en.png)
*github actions 101 chapter 5 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Lint and Type Check?
- Which signal should the example or diagram make visible for Lint and Type Check?
- What failure should be prevented first when Lint and Type Check reaches a real system?

## What You Will Learn

- Combined *style + lint* with *Ruff*
- *Static type checks* with *Mypy*
- *Local + CI* parity via *pre-commit*
- Linting *PR diffs* only
- Five common pitfalls

## Why It Matters

*Lint and types* are the *first things reviewers catch*. Automating them frees *review* to focus on *design*.

> *Format gating* cuts *review time* in half.

## Key Terms

- **Linter**: catches *style/pattern violations* (ruff).
- **Formatter**: an *auto formatter* (ruff format).
- **Type checker**: a *static type* checker (mypy).
- **pre-commit**: a *commit-time* check hook.
- **Quality gate**: blocks merge on *failed quality*.

## Before/After

**Before**: reviewers nit *semicolons, line length, types* line by line.

**After**: PRs show *Lint passed* and *Type-check passed* automatically; review focuses on *logic*.

## Hands-on: Quality Gate in 5 Steps

### Step 1 — Ruff workflow

```yaml
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
  with:
    python-version: "3.11"
- run: pip install ruff
- run: ruff check .
- run: ruff format --check .
```

### Step 2 — Add Mypy

```yaml
- run: pip install mypy
- run: mypy src/
```

### Step 3 — Centralize config (pyproject.toml)

```toml
[tool.ruff]
line-length = 100
[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP"]

[tool.mypy]
strict = true
```

### Step 4 — Integrate pre-commit

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks: [{id: ruff}, {id: ruff-format}]
```

### Step 5 — Lint diffs only (optional)

```yaml
- run: |
    git fetch origin ${{ github.base_ref }}
    ruff check $(git diff --name-only origin/${{ github.base_ref }} | grep '\.py$') || true
```

## What to Notice in This Code

- *ruff* alone replaces *flake8 + isort + black*.
- Enable *strict* mypy *from day one* — the migration cost only grows.
- *pre-commit* catches issues *before CI does*.

## Five Common Mistakes

1. **Only running CI; not installing locally.** Every PR breaks at CI.
2. **Loosening rules until they're meaningless.**
3. **Applying `mypy` *partially*.** *any* leaks across boundaries.
4. **Auto-committing `ruff format` per PR.** Merge conflicts.
5. **Scattering `pyproject.toml` config.** No source of truth.

## How This Shows Up in Production

Mature teams standardize *ruff + mypy + pre-commit* via a *template repo* and run identical checks in *pre-commit.ci* or *GitHub Actions*.

## How a Senior Engineer Thinks

- *Lint reduces debate*.
- *Types are documentation*.
- *Strict* by default; document any exception.
- *Local and CI* run *the same command*.
- *Auto-fix* is *feedback*, not *commits*.

## Checklist

- [ ] *ruff check + format* run in CI.
- [ ] *mypy strict* is on.
- [ ] The team has *pre-commit installed*.
- [ ] All config lives in *pyproject.toml*.

## Practice Problems

1. Add a *ruff + mypy* workflow.
2. Start *pre-commit* with *three hooks*.
3. Categorize the errors that appear once you enable *strict mypy*.

## Wrap-up and Next Steps

Quality gates *lighten the review load*. Next: *Build artifacts*.

## Answering the Opening Questions

- **Why is Ruff useful for consolidating multiple tools into one?**
  - Ruff runs rules from 10+ tools (Flake8, isort, pycodestyle, pyflakes, flake8-bugbear, etc.) in a single Rust binary. CI config simplifies to `ruff check` and `ruff format`, running 10-100× faster than traditional tools. With `--output-format github`, inline annotations appear on PR diffs without separate reporter tools.
- **At what point should Mypy be moved to strict mode?**
  - Start new modules strict from the beginning; start legacy modules with `ignore_errors = true` and gradually add types. Applying strict immediately to an entire project creates hundreds of errors and team demotivation simultaneously. Use `per-file-ignores` and module overrides for the realistic strategy: "new code strict, legacy gradual."
- **Why must pre-commit be paired with CI?**
  - pre-commit gives fast local feedback; CI is the enforcement gate. Local hooks can be skipped with `--no-verify`, and some developers may not install them, so CI must run the same checks again to ensure "cannot merge without passing" is truly enforced.
<!-- toc:begin -->
## In this series

- [GitHub Actions 101 (1/10): What Is GitHub Actions?](./01-what-is-github-actions.md)
- [GitHub Actions 101 (2/10): Workflows and Jobs](./02-workflow-and-job.md)
- [GitHub Actions 101 (3/10): Understanding Triggers](./03-triggers.md)
- [GitHub Actions 101 (4/10): Python Test Automation](./04-python-test-automation.md)
- **Lint and Type Check (current)**
- Build Artifacts (upcoming)
- Docker Build (upcoming)
- Deployment Automation (upcoming)
- Secret Management (upcoming)
- A Real-World CI/CD Pipeline (upcoming)

<!-- toc:end -->

## References

- [Ruff documentation](https://docs.astral.sh/ruff/)
- [Mypy documentation](https://mypy.readthedocs.io/)
- [pre-commit](https://pre-commit.com/)
- [astral-sh/ruff-pre-commit](https://github.com/astral-sh/ruff-pre-commit)

Tags: GitHubActions, Lint, Ruff, Mypy, QualityGate
