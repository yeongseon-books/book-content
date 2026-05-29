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

- Why is Ruff useful for consolidating multiple tools into one?
- At what point should Mypy be moved to strict mode?
- Why must pre-commit be paired with CI?

## Why It Matters

Lint and types are the first things reviewers catch. But these checks are exactly what machines do faster and more consistently. Automating the quality gate lets reviewers spend time on architecture, exception flows, performance, and operational impact — the expensive judgments.

Another critical point is team-wide consistency. When code passes locally but fails in CI, developers start treating automation as an annoying barrier. Running the same commands locally and in CI creates a structure that lasts.

## Quality Gate at a Glance

The structure is clear: code comes in, machines check style and static types first, and those results feed the CI gate. Human review comes after.

## Key Terms

| Term | Meaning | Practical Point |
| --- | --- | --- |
| Linter | Catches style and pattern violations | Reduces repetitive review comments |
| Formatter | Auto-aligns and formats code | Eliminates style debates within the team |
| Type checker | Finds static type errors before runtime | Reduces boundary errors before execution |
| pre-commit | Hook that runs before commit | Fast feedback before CI |
| Quality gate | Rule that blocks merge on failure | Makes standards enforceable, not just documented |

Ruff is particularly compelling because it consolidates multiple tools. Eliminating the complexity of managing flake8, isort, and black separately reduces total team maintenance cost.

## Before and After

Without a quality gate, reviewers repeat the same feedback: import order, unused variables, line length, missing types. This wears people down, and standards drift as the team grows.

When PRs automatically show `Lint passed` and `Type-check passed`, the focus of review conversations shifts. The question becomes "is this design right?" and "is this error handling sufficient?" rather than "is the formatting correct?" That is where the real value of a quality gate lies.

## Quality Gate in 5 Steps

### Step 1 — Ruff for Basic Rules

```yaml
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
  with:
    python-version: "3.11"
- run: pip install ruff
- run: ruff check .
- run: ruff format --check .
```

This setup alone catches a majority of style issues automatically. Adding format checking eliminates "isn't this just taste?" debates.

### Step 2 — Add Mypy

```yaml
- run: pip install mypy
- run: mypy src/
```

Static type checking surfaces errors before runtime. The effect grows as function boundaries and data structures multiply.

### Step 3 — Centralize Config (pyproject.toml)

```toml
[tool.ruff]
line-length = 100
[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP"]

[tool.mypy]
strict = true
```

When config is scattered across multiple files, which value is authoritative becomes unclear. Centralizing in `pyproject.toml` is the approach that scales.

### Step 4 — Integrate pre-commit

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks: [{id: ruff}, {id: ruff-format}]
```

Errors caught locally save CI time too. When teammates run the same rules before commit, failures seen in PRs naturally decrease.

### Step 5 — Lint Diffs Only (optional)

```yaml
- run: |
    git fetch origin ${{ github.base_ref }}
    ruff check $(git diff --name-only origin/${{ github.base_ref }} | grep '\.py$') || true
```

Useful for legacy projects where enforcing strict rules on the entire repo at once is impractical. Make sure the team agrees whether this is a temporary or long-term strategy.

## What to Notice in This Code

- Ruff alone can simplify multiple quality tools into one.
- Mypy is cheaper to enforce early — the migration cost only grows.
- pre-commit acts as a fast breakwater before CI.

Adding more tools is not the point. Making standards clear is far more important. Clear standards mean failures feel less arbitrary and fixes come faster.

## Five Common Mistakes

1. **Only running CI; not installing locally.** Every PR breaks at CI.
2. **Loosening rules until they are meaningless.** Short-term comfort, long-term trust erosion.
3. **Applying Mypy partially.** `Any` leaks across boundaries undetected.
4. **Auto-committing `ruff format` per PR.** Merge conflicts multiply.
5. **Scattering config across files.** No single source of truth.

Mistake 2 deserves emphasis. Lowering standards instead of reducing violations feels easy now but eventually makes the quality gate itself untrustworthy.

## How Mature Teams Operate

Mature teams bundle Ruff, Mypy, and pre-commit into a standard template. Rather than ad-hoc rules per repository, a template repo or shared config keeps team standards consistent — far easier to maintain.

Auto-fix and auto-commit need careful separation too. Auto-fix locally is fine, but CI auto-committing into PRs can complicate review and conflict management. The pattern that survives: local auto-fix, CI verification only.

## Checklist

- [ ] `ruff check` and `ruff format --check` run in CI.
- [ ] `mypy strict` is on.
- [ ] The team has pre-commit installed.
- [ ] All config lives in `pyproject.toml`.

## Practice Problems

1. Add a Ruff + Mypy workflow.
2. Start pre-commit with three or more hooks.
3. Categorize the errors that appear once you enable strict Mypy.

## Production-Level Ruff Configuration

Ruff combines Python linting and formatting into one tool. It runs rules from Flake8, isort, pycodestyle, pyflakes, and more in a single Rust binary — CI setup simplifies and execution speed improves dramatically.

### pyproject.toml Configuration

```toml
[tool.ruff]
target-version = "py311"
line-length = 88

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "S",    # flake8-bandit (security)
    "A",    # flake8-builtins
    "C4",   # flake8-comprehensions
    "SIM",  # flake8-simplify
    "TCH",  # flake8-type-checking
    "RUF",  # ruff-specific rules
]
ignore = [
    "E501",   # line-length (formatter handles this)
    "S101",   # assert usage (needed in tests)
]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101", "S106"]  # allow assert and hardcoded passwords in tests

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

Design intent of this configuration:

- `select` explicitly lists rule groups so activated checks are visible at a glance.
- `per-file-ignores` disables irrelevant rules in test code.
- `line-length` is delegated to the formatter and ignored by the linter.

### CI Workflow Configuration

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - name: Ruff lint
        uses: astral-sh/ruff-action@v3
        with:
          args: "check --output-format github"

      - name: Ruff format check
        uses: astral-sh/ruff-action@v3
        with:
          args: "format --check --diff"
```

`--output-format github` displays lint errors as inline annotations on the PR diff. Developers see exactly where to fix without digging through logs.

`format --check --diff` shows formatting discrepancies as a diff without modifying files. CI only verifies; actual fixes happen in the developer's local `ruff format` or pre-commit.

---

## Introducing Mypy Gradually

The biggest mistake when first introducing Mypy is enabling `--strict` immediately. Without existing type annotations, hundreds of errors appear and team morale drops.

### Gradual Introduction Strategy

```toml
# pyproject.toml - Phase 1: basic checks only
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true

# New modules are strict
[[tool.mypy.overrides]]
module = "src.new_module.*"
strict = true

# Legacy modules are lenient
[[tool.mypy.overrides]]
module = "src.legacy.*"
ignore_errors = true
```

The key is applying strict standards to new code while migrating legacy code gradually.

### Running Mypy in CI

```yaml
jobs:
  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
          cache: "pip"
      - run: pip install -e ".[dev]"

      - name: Mypy type check
        run: mypy src --output-format=github-actions
```

`--output-format=github-actions` displays inline annotations on PR diffs, similar to Ruff. Available from Mypy 0.900+.

### Leveraging Mypy Cache

```yaml
      - name: Restore Mypy cache
        uses: actions/cache@v4
        with:
          path: .mypy_cache
          key: mypy-${{ hashFiles('pyproject.toml') }}-${{ hashFiles('src/**/*.py') }}
          restore-keys: |
            mypy-${{ hashFiles('pyproject.toml') }}-
            mypy-

      - run: mypy src
```

Mypy supports incremental checking, so caching dramatically reduces execution time. Including source file hashes in the cache key ensures the cache refreshes only when code changes.

---

## pre-commit and CI: The Relationship

pre-commit runs checks at local commit time. You might think "if we already check locally, why bother in CI?" Two reasons make CI essential:

1. **Local hooks can be bypassed.** `git commit --no-verify` skips hooks, and some developers may not install pre-commit at all.
2. **CI is the enforcement gate.** PR checks must fail to block merge. Local hooks provide "fast feedback"; CI provides "mandatory enforcement."

### .pre-commit-config.yaml

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.14.1
    hooks:
      - id: mypy
        additional_dependencies:
          - types-requests
          - types-pyyaml
```

### Running pre-commit in CI

```yaml
jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"

      - uses: pre-commit/action@v3.0.1
```

`pre-commit/action` runs hooks only on changed files, making it faster than a full check. Caching is handled automatically.

---

## Job Structure: Combining Lint, Types, and Tests

How to combine lint and type checks with other verification is the practical core.

```yaml
name: quality-gate

on:
  pull_request:
    paths: ["src/**", "tests/**", "pyproject.toml"]

concurrency:
  group: quality-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: astral-sh/ruff-action@v3
        with:
          args: "check --output-format github"
      - uses: astral-sh/ruff-action@v3
        with:
          args: "format --check"

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
          cache: "pip"
      - run: pip install -e ".[dev]"
      - run: mypy src

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
          cache: "pip"
      - run: pip install -e ".[dev]"
      - run: pytest -q

  build:
    needs: [lint, typecheck, test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: python -m build
```

Three verification jobs run in parallel; all must pass before build starts. Lint finishes fastest (usually under 10 seconds), type checking takes 30-60 seconds, and tests take the longest. In this structure, a lint failure returns immediate feedback without waiting for other jobs to complete.

---

## Progressive Strictness Strategy

The most realistic approach when introducing lint and type checks to a team is progressive strictness.

| Phase | Lint | Type Check | Timeline |
| --- | --- | --- | --- |
| Phase 1 | Basic rules only (E, F) | ignore_missing_imports | 2 weeks |
| Phase 2 | Extended rules (B, UP, SIM) | New modules strict | 1 month |
| Phase 3 | Security rules included (S) | Full strict | Gradual |

Move to the next phase when CI failures reach zero at the current level. Fix existing code issues in bulk PRs, and apply strict standards to new code first — this approach is easiest to get team buy-in for.

`ruff check --statistics` helps determine which rules to enable first:

```bash
$ ruff check --statistics src/
  128  F841  local variable is assigned but never used
   45  E501  line too long
   23  B006  mutable argument default
```

Starting with the highest-count violations gives the most visible improvement.

---

## Balancing Auto-fix and Manual Verification

The `--fix` option is convenient, but applying auto-fixes in CI and committing them can introduce unintended changes into PRs. The practical principle:

- **Local**: Apply auto-fix with `ruff check --fix` and `ruff format`
- **CI**: Verify only with `ruff check` (no fix) and `ruff format --check`

If you want CI to auto-fix and commit, this pattern works:

```yaml
jobs:
  auto-fix:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v6
        with:
          ref: ${{ github.head_ref }}
          token: ${{ secrets.GITHUB_TOKEN }}

      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"

      - run: pip install ruff
      - run: ruff check --fix .
      - run: ruff format .

      - name: Commit changes
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git diff --quiet || (git add -A && git commit -m "style: auto-fix lint issues")
          git push
```

This pattern is convenient but has a caveat: auto-commits can re-trigger workflows, creating infinite loops. Commits made with `github-actions[bot]`'s token do not trigger workflows by default, so this is usually safe — but be careful if using a PAT.

---

## Security Lint (Bandit / Ruff S Rules)

Code security checks can be handled as part of linting. Ruff's `S` rule group includes flake8-bandit rules.

```toml
[tool.ruff.lint]
select = ["S"]  # Enable security rules
```

Common security issues caught:

| Rule | Issue | Example |
| --- | --- | --- |
| S101 | assert usage | Can be removed with -O flag in production |
| S104 | Binding to 0.0.0.0 | Unintended external exposure |
| S105 | Hardcoded password | Variable name contains "password" |
| S108 | /tmp usage | Symlink attack possible |
| S301 | pickle usage | Deserialization attack possible |
| S603 | subprocess call | Command injection risk |

Security lint does not catch everything, but it automatically prevents the most common mistakes. It is the first step in reducing the security team's code review burden.

---

## Using Type Checks for Refactoring

Mypy serves as more than a checker — it acts as a refactoring safety net.

```python
# Before: bugs hidden behind Any type
def process_data(data):  # type: ignore
    return data["key"]["nested"]  # KeyError risk

# After: contract made explicit with types
from typing import TypedDict

class NestedData(TypedDict):
    nested: str

class InputData(TypedDict):
    key: NestedData

def process_data(data: InputData) -> str:
    return data["key"]["nested"]  # Mypy validates structure
```

Adding type annotations lets Mypy catch type mismatches at call sites. This statically blocks bugs that are difficult to discover through tests alone.

### Mypy Strictness Report

To understand current type coverage:

```bash
$ mypy src --txt-report mypy-report
$ cat mypy-report/index.txt
Module              Stmts   Miss  Cover
--------------------------------------
src.api.routes        45      3    93%
src.core.models       80      0   100%
src.legacy.utils     120     95    21%
```

Saving this report as a CI artifact lets you track type coverage trends over time.

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
