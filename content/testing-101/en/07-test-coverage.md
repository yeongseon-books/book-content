---
series: testing-101
episode: 7
title: Test Coverage
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Testing
  - Coverage
  - pytest-cov
  - Quality
  - Metrics
seo_description: Line, branch, and function coverage explained, how to measure with pytest-cov, and why 100% coverage can be dangerous.
last_reviewed: '2026-05-04'
---

# Test Coverage

> Testing 101 series (7/10)

<!-- a-grade-intro:begin -->

**Core question**: *How much* did you test? Is 100% *enough*?

> Coverage is a *measurement tool*. The moment it becomes *a target* it loses meaning.

<!-- a-grade-intro:end -->

## What You Will Learn

- The difference between *line/branch/function* coverage
- How to *measure* with `pytest-cov`
- A workflow to find *uncovered code*
- *Why 100% coverage* can be dangerous
- How to set a sensible target

## Why It Matters

If you do not know *where tests reach*, incidents happen in the *blind spots*. At the same time, tests written *just to raise the number* create *false safety*.

> Coverage is a *compass*, not a *map*.

## Concept at a Glance

```mermaid
flowchart LR
    Code["Production code"] --> Cov["Coverage tool"]
    Cov --> Report["Line/branch report"]
    Report --> Action["Add tests for gaps"]
```

## Key Terms

- **Line coverage**: ratio of *executed lines / total lines*.
- **Branch coverage**: whether *both sides* of branches like if/else were executed.
- **Function coverage**: ratio of *called functions*.
- **Uncovered**: code that tests *never* executed.
- **Coverage gate**: CI fails if coverage falls below *the minimum*.

## Before/After

**Before (no coverage)**

```text
- All you know is "we have many tests"
- No idea which lines were *never executed*
```

**After (coverage report)**

```text
src/payment.py: 78% (line 42, 57 uncovered)
src/auth.py: 92% (line 11 uncovered)
TOTAL: 84%
```

## Hands-on: pytest-cov in Five Steps

### Step 1 — Install

```bash
pip install pytest-cov
```

### Step 2 — Measure

```bash
pytest --cov=src --cov-report=term-missing
```

```text
src/calc.py    24    2    92%   18-19
src/auth.py    50   10    80%   34, 41-49
TOTAL         200   18    91%
```

### Step 3 — HTML report

```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

The red lines are *the untested ones*.

### Step 4 — Branch coverage

```bash
pytest --cov=src --cov-branch --cov-report=term-missing
```

This shows whether *both True and False* of `if x > 0:` were covered.

### Step 5 — Gate (enforce in CI)

```toml
# pyproject.toml
[tool.coverage.report]
fail_under = 80
```

```bash
pytest --cov=src
# Coverage failure: total of 78 is less than fail_under=80
```

## What to Notice in This Code

- Line coverage only looks at *execution* (value verification is separate).
- *Branch coverage* is a more honest signal.
- The HTML report shows *the gaps* at a glance.

## Five Common Mistakes

1. **Setting *100%* as a KPI.** It floods you with *meaningless tests*.
2. **Inflating coverage with *no assertions*.** Code is *executed* but not *verified*.
3. **Including *generated/migration/experimental code* in measurement.** Just noise.
4. **Ignoring *branch coverage*.** Testing only one side of an if-else still gives *100% line*.
5. **Holding *new code and legacy code* to the *same gate*.** Improvement becomes hard.

## How This Shows Up in Production

Most teams aim for *70\~85% on production code*. Core domain stays *high*; adapters and UI sit *lower*. Many add a separate gate on *patch coverage* (coverage of changed lines).

## How a Senior Engineer Thinks

- Treats coverage as *a diagnostic, not an outcome metric*.
- Looks at *the gaps* and asks *why* they are gaps.
- Keeps *new code coverage high* while *legacy improves gradually*.
- *Prioritizes* branches and exception paths.
- Accepts that 100% can have *low ROI*.

## Checklist

- [ ] You looked at a `pytest --cov` report once.
- [ ] You inspected *red lines* in the HTML report.
- [ ] You enabled *branch coverage*.
- [ ] CI has a *minimum coverage* gate.

## Practice Problems

1. Find the *file with the lowest coverage* in your project.
2. Write *why it is low* in one line and propose *three tests* to add.
3. Compare the *numerical gap* between line and branch coverage.

## Wrap-up and Next Steps

Coverage is a *health signal*, not *health itself*. The next post covers *regression tests* — making sure the same bug *does not come back*.

<!-- toc:begin -->
- [What Is Testing?](./01-what-is-testing.md)
- [Unit Test](./02-unit-test.md)
- [Integration Test](./03-integration-test.md)
- [E2E Test](./04-e2e-test.md)
- [Test Double](./05-test-double.md)
- [Mock and Stub](./06-mock-and-stub.md)
- **Test Coverage (current)**
- Regression Test (upcoming)
- Running Tests in CI (upcoming)
- Building a Test Strategy (upcoming)
<!-- toc:end -->

## References

- [pytest-cov docs](https://pytest-cov.readthedocs.io/)
- [coverage.py docs](https://coverage.readthedocs.io/)
- [Martin Fowler — Test Coverage](https://martinfowler.com/bliki/TestCoverage.html)
- [Google Testing Blog — Code Coverage Best Practices](https://testing.googleblog.com/2020/08/code-coverage-best-practices.html)

Tags: Testing, Coverage, pytest-cov, Quality, Metrics
