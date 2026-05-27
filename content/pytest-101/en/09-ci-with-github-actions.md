---
series: pytest-101
episode: 9
title: "pytest 101 (9/10): Test Automation with GitHub Actions"
status: content-ready
targets:
  tistory: false
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
seo_description: Build a GitHub Actions workflow that verifies pytest, coverage, and a Python version matrix on every push and pull request.
last_reviewed: '2026-05-17'
---

# pytest 101 (9/10): Test Automation with GitHub Actions

This is the 9th post in the pytest 101 series.

Local green tests are not enough when pull requests can still ship unverified combinations of Python versions, dependencies, and coverage regressions. In this article, we'll turn pytest into an operational gate by wiring one coherent GitHub Actions workflow to every push and pull request.


![pytest 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/pytest-101/09/09-01-github-actions-workflow-overview.en.png)
*pytest 101 chapter 9 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Test Automation with GitHub Actions?
- Which signal should the example or diagram make visible for Test Automation with GitHub Actions?
- What failure should be prevented first when Test Automation with GitHub Actions reaches a real system?

## What This Article Covers

- How to stop relying on developers to remember manual test runs before opening a PR
- How to assemble one final GitHub Actions workflow instead of mentally merging partial YAML snippets
- How to verify Python 3.10, 3.11, and 3.12 in parallel without slowing feedback too much
- How to keep an HTML coverage artifact available for reviewers after each CI run

## Why It Matters

Without CI, testing remains a habit. Habits fail under pressure. A team only gets consistent quality when test execution is enforced by repository rules instead of personal memory.

> The real value of CI is not "it can run tests". It is "you cannot forget to run them anymore."

Python projects are especially prone to environment drift. A change that passes on one laptop can still fail on another version of Python or with a slightly different dependency cache. That is why the PR signal, not the local shell, should be the team's source of truth.

## Mental Model

> Think of GitHub Actions as a router: one push or pull request event fans out into multiple Python-version jobs, and one designated job also keeps the coverage artifact for review.

```text
push or pull_request
  -> workflow starts
  -> matrix jobs for Python 3.10 / 3.11 / 3.12
  -> each job installs package + test dependencies
  -> each job runs pytest with coverage threshold
  -> Python 3.12 job uploads HTML coverage artifact
  -> PR shows pass/fail signal for merge decision
```

## Core Concepts

| Term | Description |
| --- | --- |
| workflow | The automation definition stored in `.github/workflows/` |
| trigger | The event condition that starts a workflow |
| job | An independently executed task on a GitHub Actions runner |
| matrix | A strategy that expands one job definition across multiple environments |
| artifact | A stored file bundle generated during workflow execution |

## Before / After

**Before — test execution depends on human memory:**

```bash
git push origin feature/cart-discount
# Open PR
# Reviewer: "Did you check 3.10 too?"
# Author: "I only ran it on 3.12..."
```

**After — push and PR events enforce the same rule:**

```yaml
# .github/workflows/test.yml
name: test

on:
  push:
    branches: [master]
  pull_request:
    branches: [master]

jobs:
  pytest:
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -e ".[test]"
      - run: pytest --cov=src --cov-fail-under=80
```

Even this short version already communicates the operational rule: when it runs, which versions it checks, and what failure threshold blocks the change.

## Step-by-Step Practice

### Step 1: Start with the final workflow, not fragments

Instead of scattering the explanation across partial YAML blocks, anchor the article on one runnable file and explain each decision from there.

```yaml
# .github/workflows/test.yml
name: test

on:
  push:
    branches: [master]
  pull_request:
    branches: [master]

jobs:
  pytest:
    name: pytest (Python ${{ matrix.python-version }})
    runs-on: ubuntu-latest

    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip
          cache-dependency-path: pyproject.toml

      - name: Install package and test dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[test]"

      - name: Run pytest with coverage gate
        id: pytest
        run: |
          set +e
          pytest -q --maxfail=1 \
            --cov=src \
            --cov-report=term-missing \
            --cov-report=xml \
            --cov-fail-under=80
          status=$?
          echo "exit_code=$status" >> "$GITHUB_OUTPUT"
          exit 0

      - name: Build HTML coverage report
        if: ${{ always() && matrix.python-version == '3.12' }}
        run: coverage html

      - name: Upload HTML coverage artifact
        if: ${{ always() && matrix.python-version == '3.12' }}
        uses: actions/upload-artifact@v4
        with:
          name: coverage-html
          path: htmlcov/
          if-no-files-found: error

      - name: Fail job when pytest failed
        if: ${{ steps.pytest.outputs.exit_code != '0' }}
        run: exit 1
```

This one file is the reference point for everything else in the article. Readers never have to reconstruct the workflow in their heads.

### Step 2: Trigger on both push and pull request

```yaml
on:
  push:
    branches: [master]
  pull_request:
    branches: [master]
```

If you only listen to `push`, you lose the clarity of seeing the rule enforced directly on the PR. If you only listen to `pull_request`, branch pushes become a slower feedback loop. In practice, teams usually want both.

This also matches how branch protection is commonly configured: the workflow becomes a required status check, which means "no green CI, no merge."

### Step 3: Use a matrix to surface compatibility problems earlier

```yaml
strategy:
  fail-fast: false
  matrix:
    python-version: ["3.10", "3.11", "3.12"]
```

The matrix expands one job definition across multiple Python versions. `fail-fast: false` is useful because one failure should not hide the rest of the compatibility picture. If 3.10 fails but 3.11 and 3.12 pass, that already tells you something precise about the bug.

Quote version strings. YAML should treat them as strings, not numbers such as `3.1`.

### Step 4: Install the project the way the project actually runs

```yaml
- name: Install package and test dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -e ".[test]"
```

`pip install -r requirements.txt` is often not enough, especially for projects using a `src/` layout. CI should install the package itself plus its test extras so imports behave the same way they do in real development.

That workflow stays cleaner when `pyproject.toml` already describes the test environment.

```toml
[project.optional-dependencies]
test = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = "-ra --tb=short"

[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
show_missing = true
fail_under = 80
```

### Step 5: Prefer setup-python caching before hand-rolled cache steps

```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: ${{ matrix.python-version }}
    cache: pip
    cache-dependency-path: pyproject.toml
```

Older examples often build dependency caching with `actions/cache` directly. That still works, but `actions/setup-python` already supports a pip cache and is simpler to maintain. The dependency file drives cache invalidation, and the workflow stays readable.

The goal of CI optimization is not to create the cleverest cache key. It is to keep feedback fast without making the workflow mysterious.

### Step 6: Standardize on one canonical pytest command

```yaml
- name: Run pytest with coverage gate
  run: |
    pytest -q --maxfail=1 \
      --cov=src \
      --cov-report=term-missing \
      --cov-report=xml \
      --cov-fail-under=80
```

Teams get confused when the README says `pytest`, CI says `pytest --cov`, and local developer docs say something else again. Try to make the CI command the repository's canonical verification command.

This one step does four jobs:

- verifies test pass/fail status
- shows missing coverage lines in the log
- emits an XML report for later tooling
- fails the run when coverage drops below the agreed floor

### Step 7: Keep the artifact even when tests fail, while still failing the job

```yaml
- name: Run pytest with coverage gate
  id: pytest
  run: |
    set +e
    pytest -q --maxfail=1 \
      --cov=src \
      --cov-report=term-missing \
      --cov-report=xml \
      --cov-fail-under=80
    status=$?
    echo "exit_code=$status" >> "$GITHUB_OUTPUT"
    exit 0

- name: Build HTML coverage report
  if: ${{ always() && matrix.python-version == '3.12' }}
  run: coverage html

- name: Upload HTML coverage artifact
  if: ${{ always() && matrix.python-version == '3.12' }}
  uses: actions/upload-artifact@v4
  with:
    name: coverage-html
    path: htmlcov/
    if-no-files-found: error

- name: Fail job when pytest failed
  if: ${{ steps.pytest.outputs.exit_code != '0' }}
  run: exit 1
```

GitHub Actions skips later steps after a failed step unless you explicitly use a status function. That means a plain failing `pytest` step usually prevents HTML coverage generation and artifact upload, which breaks the common review workflow of downloading artifacts from a red PR. The pattern above captures the pytest exit code, runs report generation and upload with `always()`, and then fails the job at the end so you get both diagnostics and a red status.

Uploading HTML coverage from every matrix job usually creates more noise than value. One representative Python version is enough for most teams, and here Python 3.12 plays that role.

For reviewers, this matters because they can download `htmlcov/index.html` straight from the workflow run and inspect missed branches without rerunning the project locally.

## How to Verify the Workflow After You Push

Do not stop at "the YAML is written." CI becomes operational only after you verify the run path.

1. In the **Actions** tab, confirm the workflow run is attached to the correct branch push or pull request event.
2. Check that the **three matrix jobs** appear separately as Python 3.10, 3.11, and 3.12 runs.
3. Open a job log and confirm the expected order: checkout -> install -> pytest -> coverage.
4. In the Python 3.12 run, confirm the **Artifacts** section contains `coverage-html`.
5. If this repository uses branch protection, wire this workflow into the **required status checks** list.

Knowing what success looks like is part of the implementation. Otherwise the workflow exists, but the operational guarantee is still vague.

## What to Notice in This Code

- A single final `test.yml` is easier to reason about than four disconnected snippets.
- `fail-fast: false` preserves the full compatibility picture across Python versions.
- `actions/setup-python` caching is often enough without a separate cache action.
- A single artifact-producing job gives reviewers useful coverage context without tripling artifact noise.

## Common Mistakes

| Mistake | Why It's a Problem | Fix |
| --- | --- | --- |
| Configuring only `push` or only `pull_request` | The feedback path stays incomplete | Use both and connect the workflow to branch protection |
| Leaving Python versions unquoted | YAML may interpret `3.10` as `3.1` | Write `"3.10"` |
| Installing requirements without the project package | `src`-layout imports may fail in CI | Use `pip install -e ".[test]"` |
| Uploading HTML coverage from every matrix job | Logs and artifacts get noisy fast | Upload from one representative version |
| Letting CI and local docs use different pytest commands | Reproduction becomes inconsistent | Make the CI command the canonical one |

## Practical Applications

- Add `ruff` or `mypy` jobs alongside the test job for a broader quality gate.
- Split slow integration tests from fast unit tests when feedback time starts growing.
- Enforce green CI in repository settings instead of relying on PR template reminders.
- Keep nightly or scheduled workflows separate from the fast PR workflow.

## How Practitioners Think About This

Good CI is less about having many features and more about having one rule the team trusts. Once logs become noisy or the workflow feels inconsistent, people stop treating red builds as urgent signals.

So the first win is not sophistication. It is a stable baseline: every push and PR runs the same pytest command, the result is visible on the PR, and failing CI blocks merge.

## Checklist

- [ ] Added both push and pull request triggers to `.github/workflows/test.yml`
- [ ] Configured a matrix for Python 3.10, 3.11, and 3.12
- [ ] Installed the package and test dependencies with `pip install -e ".[test]"`
- [ ] Chosen one canonical `pytest --cov` command as the CI verification rule
- [ ] Uploaded an HTML coverage artifact from one representative Python version

## Exercises

1. Add a `ruff check .` job and run it in parallel with the test job.
2. Raise the coverage floor from 80 to 85 and inspect which files cause the failure.
3. Add this workflow to your repository's required status checks.

## Summary and Next

GitHub Actions is not just a way to run tests automatically. It is how a repository turns testing into an enforced merge rule. Once you anchor the workflow around one final file with clear triggers, matrix coverage, caching, and an artifact path, CI stops being a side feature and becomes the repository's default safety gate. Next, we'll look at how to write code that needs fewer mocks in the first place.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Test Automation with GitHub Actions?**
  - The article treats Test Automation with GitHub Actions as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Test Automation with GitHub Actions?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Test Automation with GitHub Actions reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [pytest 101 (1/10): Why Write Tests?](./01-why-write-tests.md)
- [pytest 101 (2/10): Writing Your First pytest Test](./02-first-pytest-test.md)
- [pytest 101 (3/10): Assert and Exception Testing](./03-assert-and-exceptions.md)
- [pytest 101 (4/10): Understanding Fixtures](./04-fixtures.md)
- [pytest 101 (5/10): Parametrization](./05-parametrization.md)
- [pytest 101 (6/10): Mock and Monkeypatch](./06-mock-and-monkeypatch.md)
- [pytest 101 (7/10): Testing Files, Environment Variables, and Time](./07-testing-files-env-time.md)
- [pytest 101 (8/10): Coverage and Test Quality](./08-coverage.md)
- **Test Automation with GitHub Actions (current)**
- Writing Testable Code (upcoming)

<!-- toc:end -->

## References

- [GitHub Actions workflow syntax](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions)
- [Running variations of jobs in a workflow with a matrix](https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs)
- [Caching dependencies to speed up workflows](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)
- [actions/setup-python](https://github.com/actions/setup-python)
- [Store and share data with workflow artifacts](https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts)

Tags: Python, pytest, GitHub Actions, CI/CD, Test Automation
