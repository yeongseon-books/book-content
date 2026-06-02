---
series: pytest-101
episode: 1
title: "pytest 101 (1/10): Why Write Tests?"
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
  - Testing
  - Software Quality
  - Test Automation
seo_description: Testing with pytest enhances productivity and provides a safety net for refactoring. Learn with practical Python examples and the test pyramid.
last_reviewed: '2026-05-04'
---

# pytest 101 (1/10): Why Write Tests?

This is the first post in the pytest 101 series.

> pytest 101 series (1/10)

**Key Question**: Does writing tests slow down development?

> Tests don't slow you down — they remove the fear of change and ultimately speed you up. This article explains why tests matter, what kinds exist, and why pytest is the go-to tool for Python testing.


![pytest 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/pytest-101/01/01-01-big-picture.en.png)
*pytest 101 chapter 1 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Why Write Tests??
- Which signal should the example or diagram make visible for Why Write Tests??
- What failure should be prevented first when Why Write Tests? reaches a real system?

## What You Will Learn

- The concrete impact of tests on development productivity
- The test pyramid and differences between test types
- Manual testing versus automated testing
- Why pytest is the preferred Python testing tool

## Why It Matters

You've probably felt that anxiety when modifying code: "Will this break something else?" Without tests, every change is a gamble. With tests, you confirm existing behavior works in seconds after any change.

> Tests are a safety net for your future self. Ten minutes today saves three hours of debugging tomorrow.

In production environments, deploying without tests means incident root-cause analysis takes 3–5x longer on average. Tests tell you exactly which input fails and where.

## Mental Model

> Test = code that automatically verifies your code behaves as expected

```text
[Manual Testing]           [Automated Testing]
  Human runs code            Code runs code
  Repetition cost ↑          Repetition cost ≈ 0
  Error-prone                Consistent results
  Coverage unclear           Coverage measurable
```

## Core Concepts

| Term | Description |
|------|-------------|
| Unit test | Verifies a single function in isolation |
| Integration test | Verifies interaction between multiple components |
| E2E test | Verifies the entire flow from a user's perspective |
| Test pyramid | Strategy of writing more unit tests than integration or E2E tests |
| Regression test | Confirms existing features still work after changes |

## Before / After

Compare manual verification with pytest automation.

```python
# before: manually call functions and visually inspect output
def add(a, b):
    return a + b

print(add(1, 2))   # check if 3 appears
print(add(-1, 1))   # check if 0 appears
```

```python
# after: automated verification with pytest
def add(a, b):
    return a + b

def test_add_positive():
    assert add(1, 2) == 3

def test_add_negative():
    assert add(-1, 1) == 0
```

## Step-by-Step Practice

### Step 1: Check Python Environment

```bash
python3 --version
# Python 3.10 or higher is fine
```

### Step 2: Install pytest

```bash
pip install pytest
pytest --version
```

### Step 3: Write the Function Under Test

Create `calculator.py`:

```python
# calculator.py
def add(a: int, b: int) -> int:
    return a + b

def divide(a: int, b: int) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

### Step 4: Write the Test File

Create `test_calculator.py`:

```python
# test_calculator.py
import pytest
from calculator import add, divide

def test_add():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, 1) == 0

def test_divide():
    assert divide(10, 2) == 5.0

def test_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(1, 0)
```

### Step 5: Run the Tests

```bash
pytest test_calculator.py -v
```

Output:

```text
test_calculator.py::test_add PASSED
test_calculator.py::test_add_negative PASSED
test_calculator.py::test_divide PASSED
test_calculator.py::test_divide_by_zero PASSED
========================= 4 passed =========================
```

## What to Notice in This Code

- Functions starting with `test_` are automatically discovered by pytest
- A single `assert` statement verifies the expected value — more concise than unittest's `assertEqual`
- `pytest.raises` verifies that an exception is raised
- The `-v` flag shows individual test pass/fail status

## Common Mistakes

| Mistake | Why It's a Problem | Fix |
|---------|-------------------|-----|
| Test filename doesn't start with `test_` | pytest won't discover the test file | Follow the `test_*.py` or `*_test.py` naming convention |
| Test function doesn't start with `test_` | The function won't be recognized as a test | Prefix function names with `test_` |
| Using `print()` to verify results | Can't be automated and won't catch regressions | Use `assert` to state expected values explicitly |
| Too many asserts in one test | Remaining assertions are skipped after the first failure | Verify one behavior per test |
| Tests depend on execution order | Tests fail when run independently | Design each test to be self-contained |

## Practical Applications

- Run `pytest` in CI/CD pipelines to automatically verify before merge
- Write tests before refactoring to establish a safety net
- When receiving a bug report, write a reproduction test first, then fix
- Use test coverage as a metric during code review
- Run tests during onboarding to quickly understand project behavior

## How Practitioners Think About This

Some view test writing as "extra work," but experienced developers see tests as "part of development." Writing code without tests is like deploying without compiling.

In practice, teams invest 20–30% of total development time in writing tests. This investment pays back through reduced debugging time, safer refactoring, and faster code reviews.

## Checklist

- [ ] Installed pytest and verified with `pytest --version`
- [ ] Understood the `test_` prefix convention
- [ ] Wrote a test that verifies expected values with `assert`
- [ ] Wrote an exception test with `pytest.raises`
- [ ] Ran `pytest -v` and reviewed the results

## Exercises

1. Write a `multiply(a, b)` function and create three tests for positive, negative, and zero inputs.
2. Write an `is_even(n)` function and test it with even, odd, and negative numbers.
3. Write a `parse_int(s)` function that raises `ValueError` on invalid string input, and test it.

## Summary and Next

Tests are a safety net for code changes. pytest lets you write tests with a single `assert` statement. In the next article, we'll walk through writing your first pytest test from scratch.

## Real-World Scenario: The Moment Tests Save Money

Here is a cart discount calculation that transitions from manual verification to automated testing.

```python
# pricing.py
from dataclasses import dataclass

@dataclass
class CartItem:
    name: str
    price: int
    qty: int

def calc_total(items: list[CartItem], coupon_rate: float = 0.0) -> int:
    if not 0.0 <= coupon_rate <= 1.0:
        raise ValueError("coupon_rate must be between 0 and 1")
    subtotal = sum(i.price * i.qty for i in items)
    discounted = int(subtotal * (1 - coupon_rate))
    return max(0, discounted)
```

```python
# test_pricing.py
import pytest
from pricing import CartItem, calc_total

def test_calc_total_without_coupon():
    items = [CartItem("book", 10000, 2), CartItem("pen", 1000, 3)]
    assert calc_total(items) == 23000

def test_calc_total_with_coupon():
    items = [CartItem("book", 10000, 2), CartItem("pen", 1000, 3)]
    assert calc_total(items, 0.1) == 20700

@pytest.mark.parametrize("bad_rate", [-0.1, 1.1])
def test_calc_total_rejects_bad_coupon_rate(bad_rate):
    with pytest.raises(ValueError, match="between 0 and 1"):
        calc_total([], bad_rate)
```

```bash
pytest test_pricing.py -v
```

```text
test_pricing.py::test_calc_total_without_coupon PASSED
test_pricing.py::test_calc_total_with_coupon PASSED
test_pricing.py::test_calc_total_rejects_bad_coupon_rate[-0.1] PASSED
test_pricing.py::test_calc_total_rejects_bad_coupon_rate[1.1] PASSED
========================= 4 passed =========================
```

Intentionally introduce a bug to see how tests catch it immediately.

```python
# Bug: wrong operator
# discounted = int(subtotal * (1 + coupon_rate))
```

```bash
pytest test_pricing.py -v
```

```text
test_pricing.py::test_calc_total_without_coupon PASSED
test_pricing.py::test_calc_total_with_coupon FAILED
E       assert 25300 == 20700
```

That single failure line is the signal that prevents a production incident.

## How to Prioritize What to Test

When you don't know where to start writing tests, this priority table is practical.

| Priority | Area | Reason | Example |
|---|---|---|---|
| 1 | Money, permissions, inventory | Failure cost is high | Payment total, admin access |
| 2 | External integration boundaries | Failure propagates widely | API response mapping, DB writes |
| 3 | Pure calculation functions | Fast, broad coverage possible | Parsing, formatting, validation |
| 4 | Simple getters/setters | ROI may be low | Thin wrapper functions |

The key is to automate critical boundaries first. Trying to test all code at the same density drives up maintenance costs before delivering value.

## Common Objections and Responses

| Objection | Real Problem | Response |
|---|---|---|
| "No time to write tests" | Debugging time grows larger | Start with bug-reproduction tests |
| "UI changes too often" | Misunderstanding unit test scope | Separate domain logic and test that |
| "We already have manual QA" | Slow regression detection | Add automated tests at PR stage |
| "Coverage is too low to matter" | No measurement baseline exists | Set a baseline on core modules first |

## Before and After Refactoring: Code Without Tests vs. Code With Tests

```python
# before_refactor.py
def shipping_fee(country: str, total: int) -> int:
    if country == "KR":
        if total >= 50000:
            return 0
        return 3000
    if country == "US":
        if total >= 100:
            return 0
        return 10
    return 999999
```

```python
# test_shipping_fee.py
import pytest
from before_refactor import shipping_fee

@pytest.mark.parametrize(
    "country,total,expected",
    [
        ("KR", 10000, 3000),
        ("KR", 50000, 0),
        ("US", 50, 10),
        ("US", 100, 0),
        ("JP", 1, 999999),
    ],
)
def test_shipping_fee(country, total, expected):
    assert shipping_fee(country, total) == expected
```

Lock the tests first, then safely restructure the function internals.

```python
# after_refactor.py
FEES = {
    "KR": {"free_over": 50000, "fee": 3000},
    "US": {"free_over": 100, "fee": 10},
}

def shipping_fee(country: str, total: int) -> int:
    policy = FEES.get(country)
    if policy is None:
        return 999999
    return 0 if total >= policy["free_over"] else policy["fee"]
```

Run the same tests—all pass—confirming the behavioral contract is preserved while the structure improves.

## Team Adoption Roadmap: How to Actually Start a Testing Culture

Even when a team agrees tests are necessary, execution stalls without a clear starting point. This sequence works for small teams.

### Step 1: Bug-Reproduction Tests First

Start by adding reproduction tests for any code that has caused a production incident.

```python
# bugfix_test_example.py

def normalize_phone(raw: str) -> str:
    digits = "".join(ch for ch in raw if ch.isdigit())
    if len(digits) not in (10, 11):
        raise ValueError("invalid phone length")
    return digits
```

```python
import pytest
from bugfix_test_example import normalize_phone

@pytest.mark.parametrize("bad", ["123", "abc", "010-1234-12345"])
def test_normalize_phone_rejects_invalid_input(bad):
    with pytest.raises(ValueError):
        normalize_phone(bad)
```

### Step 2: Automate Critical Boundaries

Add tests to input validation, payment amounts, and permission checks—boundaries where failure cost is highest.

### Step 3: PR Ground Rules

- Feature code changes must include at least one related test
- Bug fixes must start with a reproduction test
- CI blocks merge when `pytest -q` fails

## Manual QA vs. Automated Tests: Role Separation

| Aspect | Automated Tests | Manual QA |
|---|---|---|
| Purpose | Fast regression detection | User-perspective verification |
| Frequency | Every PR | Before/after release |
| Speed | Seconds to minutes | Minutes to hours |
| Reproducibility | High | Relatively low |

The two approaches are complementary, not interchangeable.

## Turning Failure Output into Operational Knowledge

Test failures are not individual developer events—they are team knowledge accumulation events.

- Keep failed input values in parametrize lists permanently.
- Make error messages specific to reduce reproduction time.
- Link retrospective documents as comments in test code.

```python
# regression_cases.py
import pytest

def parse_currency(value: str) -> int:
    cleaned = value.replace(",", "").strip()
    if not cleaned.isdigit():
        raise ValueError("invalid currency string")
    return int(cleaned)

@pytest.mark.parametrize(
    "raw",
    ["1,2,3", "12a00", "-100", ""],
)
def test_parse_currency_regressions(raw):
    with pytest.raises(ValueError):
        parse_currency(raw)
```

## Minimum Operational Metrics

Once you start testing, track these monthly to clarify improvement direction.

| Metric | Meaning | Target |
|---|---|---|
| Time to recovery after failure | Time to identify and fix test failure cause | Decreasing trend |
| Regression bug count | Same-type recurrence count | Decrease per quarter |
| PR test execution rate | Percentage of PRs that include tests | 90%+ |
| Test execution time | Feedback delay | Maintain team-agreed threshold |

## Terminal Option Combinations

| Command | Purpose |
|---|---|
| `pytest -q` | Quick pass/fail summary |
| `pytest -v` | Per-case pass/fail detail |
| `pytest -x` | Stop immediately on first failure |
| `pytest -k "keyword"` | Run only matching subset |
| `pytest --maxfail=3` | Limit maximum failure count |

## Operational Regression Test Template

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

This template is the simplest form of permanently preserving bug tickets as test code.

## Quality Check Questions

- Can you infer the failure cause from the failure message alone?
- Do tests depend on execution order?
- Are boundary-value inputs included?
- Are both happy and error paths verified?
- Does adding a test case require only adding data, not copying functions?

## Answering the Opening Questions

- **Are tests work that slows development, or an investment that speeds it up?**
  - As the article's examples show, once you lock core logic like `add`, `divide`, and `calc_total` with tests, regressions like incorrect discount calculations or division by zero get caught immediately after a fix. The `pytest -v` output showing `test_calc_total_with_coupon` failing instantly demonstrates that tests reduce debugging time and ultimately speed up development.
- **What distinguishes unit tests, integration tests, and E2E tests?**
  - Unit tests verify a single function's rules at the level of `add(2, 3) == 5` or `shipping_fee("KR", 50000) == 0`. Integration and E2E tests bundle multiple components or entire user flows, but as the test pyramid emphasizes, the thickest layer should be fast, frequently-run unit tests.
- **What difference do manual and automated tests make?**
  - Manual tests require humans to check results visually with `print(add(1, 2))`, incurring repeated cost. Automated tests preserve failure conditions in code—like `pytest.raises(ValueError, match="Cannot divide by zero")` or `@pytest.mark.parametrize("bad", [-1, 24, 100])`—automatically re-checking the same problems on every change.
<!-- toc:begin -->
## In this series

- **Why Write Tests? (current)**
- Writing Your First pytest Test (upcoming)
- Assert and Exception Testing (upcoming)
- Understanding Fixtures (upcoming)
- Parametrization (upcoming)
- Mock and Monkeypatch (upcoming)
- Testing Files, Environment Variables, and Time (upcoming)
- Coverage and Test Quality (upcoming)
- Test Automation with GitHub Actions (upcoming)
- Writing Testable Code (upcoming)

<!-- toc:end -->

## References

- [pytest official documentation](https://docs.pytest.org/)
- [Python Testing with pytest (Brian Okken)](https://pragprog.com/titles/bopytest2/python-testing-with-pytest-second-edition/)
- [Test Pyramid — Martin Fowler](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Real Python — Getting Started With Testing in Python](https://realpython.com/python-testing/)

Tags: Python, pytest, Testing, Software Quality, Test Automation
