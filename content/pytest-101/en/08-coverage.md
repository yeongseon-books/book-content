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
  tistory: false
title: "pytest 101 (8/10): Coverage and Test Quality"
---

# pytest 101 (8/10): Coverage and Test Quality

This is the 8th post in the pytest 101 series.

> pytest 101 series (8/10)

**Key Question**: What percentage of your code do your tests actually execute?

> Code coverage measures the proportion of lines your tests run. With pytest-cov, you can measure coverage, find untested lines, and fill the gaps. This article covers setup, interpretation, and CI enforcement.


![pytest 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/pytest-101/08/08-01-big-picture.en.png)
*pytest 101 chapter 8 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Coverage and Test Quality?
- Which signal should the example or diagram make visible for Coverage and Test Quality?
- What failure should be prevented first when Coverage and Test Quality reaches a real system?

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

## Coverage Baseline Configuration Example

```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = "--cov=src/myapp --cov-report=term-missing --cov-fail-under=85"
```

This configuration blocks PRs that fall below the threshold immediately.

## Line Coverage vs Branch Coverage

| Aspect | Line Coverage | Branch Coverage |
|---|---|---|
| Meaning | Whether a code line was executed | Whether each conditional branch was executed |
| Easily missed issue | Unexecuted `else` of an `if` | Relatively fewer |
| Recommended use | Basic measurement | Apply alongside for core modules |

## Common Misconceptions

- Even at 100% coverage, quality can be low if assertions are weak.
- Even at 70% coverage, practical value can be high if key boundaries are well-captured.
- The nature of missing lines matters more than the number itself.

## Before and After: Coverage-Driven Refactoring

```python
# before: single block with many branches

def shipping_label(country: str, express: bool) -> str:
    if country == "KR":
        if express:
            return "KR-EXP"
        return "KR-STD"
    if country == "US":
        if express:
            return "US-EXP"
        return "US-STD"
    return "INTL"
```

After locking branches with tests, you can simplify to a data map.

```python
# after
MAP = {
    ("KR", True): "KR-EXP",
    ("KR", False): "KR-STD",
    ("US", True): "US-EXP",
    ("US", False): "US-STD",
}

def shipping_label(country: str, express: bool) -> str:
    return MAP.get((country, express), "INTL")
```

This preserves behavior while improving both readability and test visibility.

## Reading Coverage Reports: Priority Order

1. Check `Missing` lines before looking at the TOTAL number.
2. Distinguish whether missing lines are core logic or simple boilerplate.
3. If core logic is missing, add tests first.
4. For functions with many branches, review with `--cov-branch`.

## Using HTML Reports

```bash
pytest --cov=src/myapp --cov-report=html
```

After running, open `htmlcov/index.html` and prioritize red lines (unexecuted).

## Enforcing Failure Thresholds

```bash
pytest --cov=src/myapp --cov-fail-under=90
```

```text
ERROR: Coverage failure: total of 84 is less than fail-under=90
```

This failure acts as a safety net preventing test quality regression.

## Minimize Exclusion Rules

```ini
# .coveragerc
[run]
source = src/myapp

[report]
omit =
    */__init__.py
```

Indiscriminate `omit` settings only make numbers look good while hiding real risks.

## Operational Threshold Examples

| Item | Threshold |
|---|---|
| New modules | 90%+ |
| Core domain modules | 95%+ with branch |
| Legacy modules | Gradual improvement |
| PR quality gate | Apply fail-under |

## Conclusion Pattern

Coverage is not a pass/fail number — it's a missing-segment detection tool. Quality improves when you iterate the loop of filling missing lines with tests.

## Terminal Option Combinations

| Command | Purpose |
|---|---|
| `pytest -q` | Quick pass/fail confirmation |
| `pytest -v` | Per-case pass/fail detail |
| `pytest -x` | Stop immediately on first failure |
| `pytest -k "keyword"` | Run only matching subset |
| `pytest --maxfail=3` | Limit maximum failure count |

## Regression Test Template

```python
import pytest

BUG_CASES = [
    ("", ValueError),
    ("   ", ValueError),
    (None, TypeError),
]

@pytest.mark.parametrize("raw,exc", BUG_CASES)
def test_regression_cases(raw, exc):
    with pytest.raises(exc):
        require_non_empty(raw)
```

This template is the simplest way to permanently preserve bug issues as test code.

## Quality Check Questions

- Can you infer the cause from the failure message alone?
- Does the test depend on execution order?
- Are boundary-value inputs included?
- Are both happy and error paths verified?
- Can you extend coverage by adding data rather than copying functions?

## Case Study: Common Review Points in PRs

### Code Example

```python
# app/discount.py

def discount_price(price: int, rate: float) -> int:
    if price < 0:
        raise ValueError("price must be >= 0")
    if not 0 <= rate <= 1:
        raise ValueError("rate must be between 0 and 1")
    return int(price * (1 - rate))
```

```python
# tests/test_discount.py
import pytest
from app.discount import discount_price

@pytest.mark.parametrize(
    "price,rate,expected",
    [
        (10000, 0.0, 10000),
        (10000, 0.1, 9000),
        (10000, 1.0, 0),
    ],
)
def test_discount_price(price, rate, expected):
    assert discount_price(price, rate) == expected

@pytest.mark.parametrize("price,rate", [(-1, 0.1), (1000, -0.1), (1000, 1.1)])
def test_discount_price_invalid(price, rate):
    with pytest.raises(ValueError):
        discount_price(price, rate)
```

### Output Example

```bash
pytest tests/test_discount.py -v
```

```text
tests/test_discount.py::test_discount_price[10000-0.0-10000] PASSED
tests/test_discount.py::test_discount_price[10000-0.1-9000] PASSED
tests/test_discount.py::test_discount_price[10000-1.0-0] PASSED
tests/test_discount.py::test_discount_price_invalid[-1-0.1] PASSED
tests/test_discount.py::test_discount_price_invalid[1000--0.1] PASSED
tests/test_discount.py::test_discount_price_invalid[1000-1.1] PASSED
========================= 6 passed =========================
```

### Review Points

- Are boundary values (`0`, `1.0`) included?
- Is the exception type specific?
- Can you identify the cause from the failure message?
- Is the structure extensible by adding data alone?

## Mini Checklist

- Maintain at least 3 failure cases.
- Include boundary values (min/max/empty).
- Verify that failure messages are meaningful.
- Confirm reproducibility with the same command in CI.


## Answering the Opening Questions

- **What does code coverage measure exactly?**
  - Coverage shows the ratio of lines tests actually executed to total lines. As the `validator.py` and `score.py` examples showed, its greatest value lies not in the number itself but in revealing which conditional branches and exception paths were never executed.
- **How do line coverage and branch coverage differ?**
  - Line coverage checks whether a code line was traversed at least once; branch coverage checks whether each `if/else` arm was actually taken. So for functions like `grade(score)` where A/B/C/D/F and range errors diverge, branch coverage must be checked alongside line coverage to not miss empty branches.
- **How do you identify missing lines with `pytest-cov`?**
  - Running `pytest --cov=src/myapp --cov-report=term-missing --cov-branch` shows `Missing` lines and branch gaps directly in the terminal. Adding `coverage html` and `--cov-fail-under=80` lets you view gaps in a browser and connect to PR quality gates in the same flow.
<!-- toc:begin -->
## In this series

- [pytest 101 (1/10): Why Write Tests?](./01-why-write-tests.md)
- [pytest 101 (2/10): Writing Your First pytest Test](./02-first-pytest-test.md)
- [pytest 101 (3/10): Assert and Exception Testing](./03-assert-and-exceptions.md)
- [pytest 101 (4/10): Understanding Fixtures](./04-fixtures.md)
- [pytest 101 (5/10): Parametrization](./05-parametrization.md)
- [pytest 101 (6/10): Mock and Monkeypatch](./06-mock-and-monkeypatch.md)
- [pytest 101 (7/10): Testing Files, Environment Variables, and Time](./07-testing-files-env-time.md)
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
