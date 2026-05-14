---
episode: 8
language: en
last_reviewed: '2026-05-04'
seo_description: Measure code coverage with pytest-cov, interpret line and branch
  metrics, and use coverage gaps to find untested edge cases in production code.
series: pytest-101
status: content-ready
tags:
- Python
- pytest
- coverage
- pytest-cov
- Code Coverage
targets:
  ebook: true
  hashnode: true
  medium: true
  mkdocs: true
  tistory: true
title: Coverage and Test Quality
---

# Coverage and Test Quality

This is post 8 in the pytest 101 series.

> pytest 101 series (8/10)

<!-- a-grade-intro:begin -->

**Key Question**: What percentage of your code do your tests actually execute?

> Code coverage measures the proportion of lines your tests run. With pytest-cov, you can measure coverage, find untested lines, and fill the gaps. This article covers setup, interpretation, and CI enforcement.

<!-- a-grade-intro:end -->

## What You Will Learn

- Installing pytest-cov and measuring coverage
- The difference between line coverage and branch coverage
- Visually inspecting missing lines with HTML reports
- Enforcing coverage thresholds in CI

## Why It Matters

Having tests doesn't mean having enough tests. If core logic isn't covered, you end up with "tests pass but bugs ship." Coverage provides an objective measure of test scope.

> 100% coverage doesn't mean zero bugs. But 30% coverage is definitely risky. Coverage guarantees "at least this code was exercised."

Setting a team-wide coverage threshold prevents new code from merging without tests.

## Mental Model

> coverage = lines executed by tests / total lines of code

```text
def process(x):        ← executed
    if x > 0:          ← executed
        return x * 2   ← executed
    else:               ← not executed
        return 0        ← not executed

test: process(5) → line coverage 60% (3/5)
```

## Core Concepts

| Term | Description |
|------|-------------|
| Line coverage | Percentage of code lines that were executed |
| Branch coverage | Percentage of conditional branches that were taken |
| pytest-cov | Plugin that runs coverage.py within pytest |
| .coveragerc | Configuration file for exclusions and source paths |
| Missing lines | Line numbers that tests never executed |

## Before / After

Compare running tests without and with coverage measurement.

```bash
# before: no coverage measurement
pytest
# result: 4 passed — but no idea which code is untested
```

```bash
# after: coverage included
pytest --cov=src --cov-report=term-missing
# result: 4 passed, coverage 78% — missing line numbers shown
```

## Step-by-Step Practice

### Step 1: Install pytest-cov

```bash
pip install pytest-cov
```

### Step 2: Prepare the Code Under Test

```python
# src/myapp/validator.py
def validate_email(email: str) -> bool:
    if not email:
        return False
    if "@" not in email:
        return False
    local, domain = email.split("@", 1)
    if not local or not domain:
        return False
    if "." not in domain:
        return False
    return True

def validate_age(age: int) -> bool:
    if not isinstance(age, int):
        raise TypeError("Age must be an integer")
    if age < 0:
        return False
    if age > 150:
        return False
    return True
```

### Step 3: Write Partial Tests

```python
# tests/test_validator.py
from myapp.validator import validate_email, validate_age

def test_valid_email():
    assert validate_email("user@example.com") is True

def test_empty_email():
    assert validate_email("") is False

def test_valid_age():
    assert validate_age(25) is True
```

### Step 4: Measure Coverage

```bash
pytest --cov=src/myapp --cov-report=term-missing

# Example output:
# Name                        Stmts   Miss  Cover   Missing
# ---------------------------------------------------------
# src/myapp/validator.py         16      6    63%   8-10, 20-22
# ---------------------------------------------------------
# TOTAL                          16      6    63%
```

### Step 5: Fill the Gaps

```python
# tests/test_validator.py — additional tests
import pytest
from myapp.validator import validate_email, validate_age

def test_valid_email():
    assert validate_email("user@example.com") is True

def test_empty_email():
    assert validate_email("") is False

def test_no_at_sign():
    assert validate_email("userexample.com") is False

def test_no_local_part():
    assert validate_email("@example.com") is False

def test_no_domain_dot():
    assert validate_email("user@localhost") is False

def test_valid_age():
    assert validate_age(25) is True

def test_negative_age():
    assert validate_age(-1) is False

def test_too_old():
    assert validate_age(200) is False

def test_age_type_error():
    with pytest.raises(TypeError):
        validate_age("twenty")
```

```bash
pytest --cov=src/myapp --cov-report=term-missing
# result: coverage 100%
```

## What to Notice in This Code

- `--cov=src/myapp` targets the specific directory for measurement
- `term-missing` shows missing line numbers directly in the terminal
- Missing lines guide you to write tests covering those branches
- Even at 100% coverage, not every edge case is necessarily covered

## Common Mistakes

| Mistake | Why It's a Problem | Fix |
|---------|-------------------|-----|
| Aiming for 100% coverage | Adds unnecessary tests and maintenance burden | Target 80%+ on core business logic |
| Ignoring branch coverage | Line coverage can be 100% while missing else branches | Add `--cov-branch` |
| Measuring test code coverage | Test code itself shouldn't be a coverage target | Use `--cov=src` to measure source only |
| Not reading the report | Looking at the number without checking which lines are missing | Generate HTML reports for visual inspection |
| Overusing `# pragma: no cover` | Excluded code hides potential bugs | Only exclude with documented justification |

## Practical Applications

- Fail CI builds with `--cov-fail-under=80` when coverage drops
- Integrate coverage bots that comment coverage changes on PRs
- Store HTML reports as CI artifacts for team browsing
- Share coverage settings in `pyproject.toml` across the team
- Track coverage for new code separately to measure improvement over legacy

## How Practitioners Think About This

Coverage is a tool for finding "where tests are missing," not for proving "where tests are sufficient." High coverage with weak assertions is meaningless.

In practice, keeping new code coverage higher than existing code is an effective strategy. Raising legacy code to 100% at once is unrealistic — start by adding tests to code that changes.

## Checklist

- [ ] Installed pytest-cov and measured coverage
- [ ] Identified missing lines with `term-missing`
- [ ] Generated an HTML report for visual inspection
- [ ] Set a minimum threshold with `--cov-fail-under`
- [ ] Added coverage settings to `pyproject.toml`

## Exercises

1. Run `--cov-branch` on `validate_email` and compare branch coverage with line coverage.
2. Add coverage settings to `pyproject.toml` and set `--cov-fail-under=90` to see a threshold failure.
3. Generate an HTML report and open it in a browser to visually inspect missing lines.

## Summary and Next

Coverage objectively measures the scope of your tests. Measure with pytest-cov, fill missing lines, and enforce thresholds in CI to maintain test quality. Next, we'll automate test execution with GitHub Actions.

<!-- toc:begin -->
- [Why Write Tests?](./01-why-write-tests.md)
- [Writing Your First pytest Test](./02-first-pytest-test.md)
- [Assert and Exception Testing](./03-assert-and-exceptions.md)
- [Understanding Fixtures](./04-fixtures.md)
- [Parametrization](./05-parametrization.md)
- [Mock and Monkeypatch](./06-mock-and-monkeypatch.md)
- [Testing Files, Environment Variables, and Time](./07-testing-files-env-time.md)
- **Coverage and Test Quality (current)**
- Test Automation with GitHub Actions (upcoming)
- Writing Testable Code (upcoming)
<!-- toc:end -->

## References

- [pytest-cov — Documentation](https://pytest-cov.readthedocs.io/)
- [coverage.py — Documentation](https://coverage.readthedocs.io/)
- [Real Python — Python Code Coverage](https://realpython.com/python-testing/#testing-for-code-coverage)
- [Martin Fowler — Test Coverage](https://martinfowler.com/bliki/TestCoverage.html)

Tags: Python, pytest, coverage, pytest-cov, Code Coverage