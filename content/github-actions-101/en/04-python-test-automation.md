---
series: github-actions-101
episode: 4
title: "GitHub Actions 101 (4/10): Python Test Automation"
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
  - Python
  - Pytest
  - Testing
  - CICD
seo_description: pytest, coverage, and matrix in one workflow. Run your Python tests automatically on every PR with confidence.
last_reviewed: '2026-05-15'
---

# GitHub Actions 101 (4/10): Python Test Automation

Teams that run `pytest` only on local machines keep hitting the same failures. One developer passes on 3.12, another breaks on 3.10, someone skips the test suite under deadline pressure, and the problem surfaces only after merge when the cost of recovery is already higher.

The important line is not “tests exist.” It is “the repository runs the same tests in the same environment every time.” That shift is what turns test code into an actual safety mechanism for the team.

This is the 4th post in the GitHub Actions 101 series. In this post, we will build a practical Python test workflow around `setup-python`, caching, reports, coverage, and version matrices.


![github actions 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/04/04-01-concept-at-a-glance.en.png)
*github actions 101 chapter 4 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Python Test Automation?
- Which signal should the example or diagram make visible for Python Test Automation?
- What failure should be prevented first when Python Test Automation reaches a real system?

## What You Will Learn

- Fast setup with *setup-python* + *pip cache*
- Surfacing *pytest results* as PR checks
- Measuring *coverage* and uploading to *Codecov*
- Multiple *Python versions* via *matrix*
- Five common pitfalls

## Why It Matters

Manual tests get *forgotten*. Only automation guarantees *the same trust* on every PR.

> *Slow CI* becomes *skipped CI*.

## Key Terms

- **setup-python**: installs *Python on the runner*.
- **pip cache**: caches *dependencies* for speed.
- **pytest**: the Python *test runner*.
- **coverage**: measures *test coverage*.
- **Codecov**: a coverage *reporting service*.

## Before/After

**Before**: `pytest` runs *only locally* and breakage shows up *after merge*.

**After**: a *Tests passed* check appears on every PR and *3.10/3.11/3.12* must all pass before merge.

## Hands-on: Test Automation in 5 Steps

### Step 1 — Python + cache

```yaml
- uses: actions/setup-python@v6
  with:
    python-version: "3.11"
    cache: "pip"
- run: pip install -r requirements.txt
```

### Step 2 — Run pytest and report

```yaml
- run: pytest -q --junitxml=report.xml
- uses: actions/upload-artifact@v7
  if: always()
  with:
    name: pytest-report
    path: report.xml
```

### Step 3 — Measure coverage

```yaml
- run: pytest --cov=src --cov-report=xml
- uses: codecov/codecov-action@v4
  with:
    files: coverage.xml
```

### Step 4 — Multi-version matrix

```yaml
strategy:
  matrix:
    python: ["3.10", "3.11", "3.12"]
steps:
  - uses: actions/setup-python@v6
    with:
      python-version: ${{ matrix.python }}
```

### Step 5 — Capture on failure

```yaml
- name: dump logs on failure
  if: failure()
  run: |
    cat pytest.log || true
```

## What to Notice in This Code

- One line of *cache: "pip"* trims *tens of seconds* of install time.
- *junit XML* integrates with *Test Reporter* tools.
- *if: always()* uploads artifacts even when steps fail.

## Five Common Mistakes

1. **`pip install` reinstalls everything every time.** Cache is missing.
2. **Using `pytest -v` in *production CI*.** Log output explodes.
3. **Tests depending on the *external network*.** Source of *flakiness*.
4. **No `junitxml`.** PR can't show *detailed* results.
5. **Coverage measured *with no goal*.** Numbers grow but quality doesn't.

## How This Shows Up in Production

Mature teams *parallelize with pytest-xdist*, manage *flaky tests* with *re-run* policy, and gate PRs on a *coverage threshold*.

## How a Senior Engineer Thinks

- *Slow tests* block *new code*.
- *Flaky tests* must be *quarantined*.
- *Coverage* is a *signal*, not a goal.
- *Matrix* must justify its *cost*.
- *Artifacts* preserve *debugging trails*.

## Checklist

- [ ] *pip cache* is enabled.
- [ ] *junit XML* is uploaded.
- [ ] *Coverage* is measured.
- [ ] *Matrix* is sized to need.

## Practice Problems

1. Add a *pytest workflow* to your project.
2. Enable a *3.11/3.12* matrix.
3. Fail PRs when *coverage drops below 80%*.

## Wrap-up and Next Steps

Test automation is the *heart of CI*. The next post covers *Lint and Type Check*.

## Answering the Opening Questions

- **Why must `setup-python` and pip cache be configured together?**
  - `setup-python`'s `cache: "pip"` option preserves pip download cache between runs, reducing dependency install time by 50-80%. Linking the cache key to dependency file hashes via `cache-dependency-path` means fresh downloads only when dependencies change. This single setting's impact on total workflow time is large enough to always configure together.
- **What's needed to surface `pytest` results as PR checks and reports?**
  - Output results as XML with `--junitxml=report.xml`, then display on PR checks with actions like `mikepenz/action-junit-report`. The key is `if: always()` — without it, the report step is skipped on failure, losing information exactly when you need it most. Don't forget `permissions: checks: write` either.
- **Why are trends and thresholds more important than the coverage number itself?**
  - 80% means different things per project. What matters is "did this PR lower coverage" (diff coverage) and "which direction is coverage moving over time" (trend). Set a floor with `fail_under`, provide per-PR feedback with Codecov's diff coverage, and the team naturally maintains the habit of writing tests.
<!-- toc:begin -->
## In this series

- [GitHub Actions 101 (1/10): What Is GitHub Actions?](./01-what-is-github-actions.md)
- [GitHub Actions 101 (2/10): Workflows and Jobs](./02-workflow-and-job.md)
- [GitHub Actions 101 (3/10): Understanding Triggers](./03-triggers.md)
- **Python Test Automation (current)**
- Lint and Type Check (upcoming)
- Build Artifacts (upcoming)
- Docker Build (upcoming)
- Deployment Automation (upcoming)
- Secret Management (upcoming)
- A Real-World CI/CD Pipeline (upcoming)

<!-- toc:end -->

## References

- [actions/setup-python](https://github.com/actions/setup-python)
- [pytest documentation](https://docs.pytest.org/)
- [coverage.py](https://coverage.readthedocs.io/)
- [Codecov GitHub Action](https://github.com/codecov/codecov-action)

Tags: GitHubActions, Python, Pytest, Testing, CICD
