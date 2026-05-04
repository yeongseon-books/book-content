---
series: pytest-101
episode: 9
title: Test Automation with GitHub Actions
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Python
  - pytest
  - GitHub Actions
  - CI/CD
  - Test Automation
seo_description: Build a CI pipeline that runs pytest automatically with GitHub Actions.
last_reviewed: '2026-05-04'
---

# Test Automation with GitHub Actions

> pytest 101 series (9/10)

<!-- a-grade-intro:begin -->

**Key Question**: Do you have to run tests manually every time you open a PR?

> GitHub Actions triggers test runs automatically on push and PR events. This article covers setting up pytest with coverage in GitHub Actions, matrix builds across Python versions, and caching for faster runs.

<!-- a-grade-intro:end -->

## What You Will Learn

- The structure and syntax of a GitHub Actions workflow file
- Running pytest with coverage in CI
- Matrix builds to test across multiple Python versions
- Caching dependencies to speed up CI runs

## Why It Matters

Tests pass locally but may fail in a different environment. CI runs all tests in a consistent environment automatically, catching problems before code is merged.

> "Works on my machine" is solved by CI. If it passes in CI, it works for everyone on the team.

No matter how well-written your tests are, they're useless if nobody runs them. CI automates execution so "forgot to run tests" never happens.

## Mental Model

> CI = push/PR event → automatic test run → results displayed on PR

```
Developer pushes → GitHub Actions triggered
  → Install Python
  → Install dependencies
  → Run pytest
  → Coverage report
  → Result: Pass / Fail
```

## Core Concepts

| Term | Description |
|------|-------------|
| workflow | An automation pipeline defined in `.github/workflows/` |
| job | An execution unit within a workflow |
| step | An individual command within a job |
| matrix | Tests multiple environment combinations simultaneously |
| artifact | Files generated during CI that can be stored and downloaded |

## Before / After

Compare manual testing with CI automation.

```bash
# before: manual — developer runs tests themselves
git push origin feature-branch
# PR created... forgot to run tests
# reviewer: "Did you run the tests?" → "Uh... no"
```

```yaml
# after: automatic — runs on every push
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e ".[test]"
      - run: pytest --cov
```

## Step-by-Step Practice

### Step 1: Write the Basic Workflow

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[test]"

      - name: Run tests
        run: pytest -v --tb=short

      - name: Run tests with coverage
        run: pytest --cov=src --cov-report=term-missing --cov-fail-under=80
```

### Step 2: Matrix Build

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[test]"

      - name: Run tests
        run: pytest -v --cov=src --cov-report=term-missing
```

### Step 3: Dependency Caching

```yaml
      - name: Cache pip packages
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('pyproject.toml') }}
          restore-keys: |
            ${{ runner.os }}-pip-
```

### Step 4: Upload Coverage Artifact

```yaml
      - name: Generate HTML coverage report
        run: pytest --cov=src --cov-report=html
        if: matrix.python-version == '3.12'

      - name: Upload coverage report
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: htmlcov/
        if: matrix.python-version == '3.12'
```

### Step 5: Configure Test Dependencies in pyproject.toml

```toml
# pyproject.toml
[project.optional-dependencies]
test = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "freezegun>=1.2",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = "-v --tb=short"

[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
show_missing = true
fail_under = 80
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.",
]
```

## What to Notice in This Code

- `on: [push, pull_request]` triggers on both event types
- Matrix builds test 3 Python versions simultaneously
- Caching saves `pip install` time on subsequent runs
- Coverage reports stored as artifacts for later download

## Common Mistakes

| Mistake | Why It's a Problem | Fix |
|---------|-------------------|-----|
| Only `pip install -r requirements.txt` | Package itself isn't installed, causing import errors | Use `pip install -e ".[test]"` |
| Python version without quotes | `3.10` is parsed as `3.1` in YAML | Quote it: `"3.10"` |
| Cache key without lock file | Cache isn't invalidated when dependencies change | Use `hashFiles('pyproject.toml')` |
| No coverage threshold | CI passes even when coverage drops | Add `--cov-fail-under=80` |
| Only testing on main branch | PR changes aren't tested before merge | Include `pull_request` event |

## Practical Applications

- Enforce branch protection so PRs can't merge until CI passes
- Test across Python 3.10, 3.11, and 3.12 with matrix builds
- Auto-post coverage reports as PR comments
- Split slow tests into a separate job for faster feedback
- Add a workflow status badge to README

## How Practitioners Think About This

CI compensates for the human limitation of "forgetting to run tests." Once configured, every push runs tests automatically — you never have to consciously remember.

In practice, teams enforce a rule that PRs cannot merge without passing CI. This single rule dramatically improves code quality.

## Checklist

- [ ] Created `.github/workflows/test.yml`
- [ ] Configured triggers for both push and pull_request events
- [ ] Set up a matrix build for multiple Python versions
- [ ] Added dependency caching
- [ ] Set a coverage threshold and uploaded artifacts

## Exercises

1. Add a lint job (flake8 or ruff) to the workflow and run it in parallel with the test job.
2. Set `fail-fast: false` so the remaining Python versions continue even if one fails.
3. Add a workflow status badge to your README.md.

## Summary and Next

GitHub Actions automates test execution so every code change is verified. Matrix builds, caching, and coverage reports make CI effective. Next, we'll learn design principles for writing testable code.

<!-- toc:begin -->
- [Why Write Tests?](./01-why-write-tests.md)
- [Writing Your First pytest Test](./02-first-pytest-test.md)
- [Assert and Exception Testing](./03-assert-and-exceptions.md)
- [Understanding Fixtures](./04-fixtures.md)
- [Parametrization](./05-parametrization.md)
- [Mock and Monkeypatch](./06-mock-and-monkeypatch.md)
- [Testing Files, Environment Variables, and Time](./07-testing-files-env-time.md)
- [Coverage and Test Quality](./08-coverage.md)
- **Test Automation with GitHub Actions (current)**
- Writing Testable Code (upcoming)
<!-- toc:end -->

## References

- [GitHub Actions — Documentation](https://docs.github.com/en/actions)
- [actions/setup-python](https://github.com/actions/setup-python)
- [pytest-cov — CI Configuration](https://pytest-cov.readthedocs.io/en/latest/config.html)
- [Real Python — CI/CD with GitHub Actions](https://realpython.com/python-continuous-integration/)

Tags: Python, pytest, GitHub Actions, CI/CD, Test Automation
