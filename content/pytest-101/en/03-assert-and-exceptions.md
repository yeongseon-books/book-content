---
series: pytest-101
episode: 3
title: "pytest 101 (3/10): Assert and Exception Testing"
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
  - assert
  - Exception Testing
  - pytest.raises
seo_description: Master pytest assertion introspection, floating-point comparison with pytest.approx, and exception testing using pytest.raises with matching.
last_reviewed: '2026-05-04'
---

# pytest 101 (3/10): Assert and Exception Testing

This is the 3rd post in the pytest 101 series.

> pytest 101 series (3/10)

**Key Question**: How is pytest's `assert` different from Python's built-in `assert`?

> pytest rewrites `assert` statements internally, showing the left-hand and right-hand values in detail when a test fails. This article covers various assert patterns and exception testing with `pytest.raises`.


![pytest 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/pytest-101/03/03-01-big-picture.en.png)
*pytest 101 chapter 3 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Assert and Exception Testing?
- Which signal should the example or diagram make visible for Assert and Exception Testing?
- What failure should be prevented first when Assert and Exception Testing reaches a real system?

## What You Will Learn

- How pytest's assertion introspection mechanism works
- Patterns for comparing collections, strings, and floating-point numbers
- Verifying exception types and messages with `pytest.raises`
- Safe floating-point comparison with `pytest.approx`

## Why It Matters

When a test fails, quickly understanding *why* it failed is critical. pytest's assertion introspection shows the failure cause immediately, dramatically reducing debugging time.

> unittest's `self.assertEqual(a, b)` is harder to read than `assert a == b`, yet pytest's failure messages are actually *more* detailed.

Exception handling is core to production code. Without testing that exceptions fire correctly, broken error handling goes undetected.

## Mental Model

> assertion introspection = pytest analyzes assert statements to provide detailed information on failure

```text
assert result == expected
       │          │
       │          └─ Expected value: displayed
       └─ Actual value: displayed

On failure:
  AssertionError: assert 3 == 5
    where 3 = add(1, 2)
```

## Core Concepts

| Term | Description |
|------|-------------|
| Assertion rewriting | pytest transforms assert at the AST level to generate detailed messages |
| pytest.raises | Context manager that verifies a specific exception is raised |
| pytest.approx | Allows tolerance in floating-point comparisons |
| match parameter | Validates exception messages using regex patterns |
| ExceptionInfo | Exception information object returned by pytest.raises |

## Before / After

Compare unittest-style and pytest-style assertions.

```python
# before: unittest style — must memorize method names
import unittest

class TestMath(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(1, 2), 3)
        self.assertIn("hello", result)
        self.assertAlmostEqual(0.1 + 0.2, 0.3, places=1)
        self.assertRaises(ValueError, divide, 1, 0)
```

```python
# after: pytest style — unified with assert
import pytest

def test_add():
    assert add(1, 2) == 3
    assert "hello" in result
    assert 0.1 + 0.2 == pytest.approx(0.3)
    with pytest.raises(ValueError):
        divide(1, 0)
```

## Step-by-Step Practice

### Step 1: Basic Assert Patterns

```python
# test_assert_patterns.py

def test_equality():
    assert 1 + 1 == 2

def test_inequality():
    assert 1 + 1 != 3

def test_truthiness():
    assert [1, 2, 3]    # non-empty list is truthy
    assert not []        # empty list is falsy

def test_membership():
    fruits = ["apple", "banana", "cherry"]
    assert "banana" in fruits
    assert "mango" not in fruits

def test_identity():
    a = None
    assert a is None
```

### Step 2: Collection Comparison

```python
# test_collections.py

def test_list_comparison():
    expected = [1, 2, 3, 4, 5]
    result = list(range(1, 6))
    assert result == expected

def test_dict_comparison():
    expected = {"name": "Alice", "age": 30}
    result = {"name": "Alice", "age": 25}
    assert result == expected  # shows differing key-values on failure

def test_set_comparison():
    expected = {1, 2, 3}
    result = {1, 2, 4}
    assert result == expected  # shows set difference on failure
```

### Step 3: Floating-Point Comparison

```python
# test_float.py
import pytest

def test_float_naive():
    # This test would fail:
    # assert 0.1 + 0.2 == 0.3

    # Safe comparison with pytest.approx
    assert 0.1 + 0.2 == pytest.approx(0.3)

def test_approx_with_tolerance():
    assert 2.0 == pytest.approx(2.02, abs=0.05)
    assert 100.0 == pytest.approx(101.0, rel=0.02)

def test_approx_list():
    result = [0.1 + 0.2, 0.2 + 0.3]
    assert result == pytest.approx([0.3, 0.5])
```

### Step 4: Exception Testing

```python
# test_exceptions.py
import pytest

def divide(a, b):
    if b == 0:
        raise ValueError(f"Cannot divide {a} by zero")
    return a / b

def test_raises_basic():
    with pytest.raises(ValueError):
        divide(10, 0)

def test_raises_with_match():
    with pytest.raises(ValueError, match="by zero"):
        divide(10, 0)

def test_raises_inspect_exception():
    with pytest.raises(ValueError) as exc_info:
        divide(10, 0)
    assert "by zero" in str(exc_info.value)
    assert exc_info.type is ValueError

def test_raises_wrong_exception():
    # This test fails because ValueError is raised, not TypeError
    with pytest.raises(TypeError):
        divide(10, 0)
```

### Step 5: Custom Error Messages

```python
# test_custom_message.py

def test_with_message():
    value = compute_score()
    assert value >= 0, f"Score cannot be negative. Got: {value}"

def test_complex_assertion():
    users = fetch_active_users()
    assert len(users) > 0, "No active users found"
```

## What to Notice in This Code

- Dict comparison failures show exactly which keys and values differ
- `pytest.approx` works with lists and dict values too
- The `match` parameter supports regex for flexible message verification
- `exc_info.value` gives direct access to the exception object for attribute inspection

## Common Mistakes

| Mistake | Why It's a Problem | Fix |
|---------|-------------------|-----|
| `assert 0.1 + 0.2 == 0.3` | Always fails due to floating-point imprecision | Use `pytest.approx(0.3)` |
| Asserting inside `pytest.raises` block | Code after the exception won't execute | Inspect `exc_info` outside the block |
| Testing with overly broad exception types | Catching `Exception` hides other bugs | Specify the exact exception type |
| Forgetting to escape special characters in `match` | Interpreted as regex, causing unexpected matches | Use `re.escape()` |
| Calling functions without asserting | Only verifies no error is raised, not the result | Always assert the return value |

## Practical Applications

- Assert API response status codes and body simultaneously
- Use `pytest.approx` for financial calculations with decimal tolerance
- Test all error cases of input validation with `pytest.raises`
- Verify custom exception class attributes (error_code, detail) via `exc_info.value`
- Add context to failure messages for faster root cause analysis in CI logs

## How Practitioners Think About This

A good test reveals its failure cause from the failure message alone. When `assert result == expected` fails, pytest shows both values — no print debugging needed.

When writing exception tests, think from the perspective: "This function *must* fail for this input." If the exception doesn't fire, the test fails, preventing accidental removal of error handling.

## Checklist

- [ ] Observed pytest's assertion introspection output
- [ ] Compared floating-point values with `pytest.approx`
- [ ] Verified exception types with `pytest.raises`
- [ ] Validated exception messages with the `match` parameter
- [ ] Inspected exception object attributes via `exc_info`

## Exercises

1. Write a test comparing two dicts that differ, and observe pytest's diff output.
2. Test a `sqrt(n)` function that raises `ValueError` on negative input, and verify the error message.
3. Experiment with the `rel` and `abs` parameters of `pytest.approx` and document the difference.

## Summary and Next

pytest's assert is readable and provides detailed failure information. `pytest.raises` and `pytest.approx` are essential tools for exception and floating-point testing. Next, we'll learn about fixtures for managing test data.

## Making Failure Messages an Asset: How to Write assert Statements

An `assert` determines team productivity not when it passes, but when it fails. Writing assertions so that failure messages are immediately actionable is what matters.

```python
# tax.py

def calc_tax(amount: int, rate: float) -> int:
    if amount < 0:
        raise ValueError("amount must be >= 0")
    if not 0 <= rate <= 1:
        raise ValueError("rate must be between 0 and 1")
    return int(amount * rate)
```

```python
# test_tax.py
import pytest
from tax import calc_tax

@pytest.mark.parametrize(
    "amount,rate,expected",
    [
        (10000, 0.1, 1000),
        (0, 0.2, 0),
        (5500, 0.08, 440),
    ],
)
def test_calc_tax(amount, rate, expected):
    assert calc_tax(amount, rate) == expected

def test_calc_tax_rejects_negative_amount():
    with pytest.raises(ValueError, match=r"amount must be >= 0"):
        calc_tax(-1, 0.1)

def test_calc_tax_rejects_bad_rate():
    with pytest.raises(ValueError, match="between 0 and 1"):
        calc_tax(1000, 1.5)
```

## Reading Causes from pytest Output

```bash
pytest test_tax.py -v
```

```text
test_tax.py::test_calc_tax[10000-0.1-1000] PASSED
...
========================= 5 passed =========================
```

Intentionally introduce a failure to see how the output differs.

```python
def test_calc_tax():
    assert calc_tax(10000, 0.1) == 1200
```

```text
E       assert 1000 == 1200
E        +  where 1000 = calc_tax(10000, 0.1)
```

## Frequently Missed Points in Exception Testing

| Item | Bad Example | Good Example |
|---|---|---|
| Type verification | `with pytest.raises(Exception)` | `with pytest.raises(ValueError)` |
| Message verification | Only check exception type | `match="between 0 and 1"` |
| Scope | Block is too large | Place only the exception-raising line in the block |

```python
# Bad: block too large, other errors get mixed in
with pytest.raises(ValueError):
    x = calc_tax(1000, 0.1)
    y = x / 0
```

```python
# Good
with pytest.raises(ValueError, match="between 0 and 1"):
    calc_tax(1000, 1.5)
```

## Floating-Point Comparison Patterns in Practice

```python
import pytest

def test_discount_ratio():
    ratio = 1 - (90 / 100)
    assert ratio == pytest.approx(0.1)

def test_vector_ratios():
    values = [1 / 3, 2 / 3]
    assert values == pytest.approx([0.333333, 0.666667], rel=1e-5)
```

## Before and After: Strengthening assert Messages

```python
# before
assert total > 0
```

```python
# after
assert total > 0, f"total must be positive, got={total}, items={items}"
```

The latter's failure message reduces reproduction time.

## Patterns for Expressive Assertions

### String Comparison

```python

def render_title(name: str) -> str:
    return f"[USER] {name.strip()}"

def test_render_title():
    assert render_title(" Alice ") == "[USER] Alice"
```

### Collection Comparison

```python

def ids(users):
    return [u["id"] for u in users]

def test_ids():
    data = [{"id": 1}, {"id": 2}]
    assert ids(data) == [1, 2]
```

### Exception and Message Verification

```python
import pytest

def parse_qty(value: str) -> int:
    qty = int(value)
    if qty <= 0:
        raise ValueError("qty must be positive")
    return qty

def test_parse_qty_error_message():
    with pytest.raises(ValueError, match="positive"):
        parse_qty("0")
```

## Red/Green Output Example

```bash
pytest -v test_parse_qty.py
```

```text
test_parse_qty.py::test_parse_qty_error_message PASSED
```

If the expected message is wrong, the test fails immediately.

```text
E   AssertionError: Regex pattern did not match.
```

## Before and After: Removing try/except

```python
# before
try:
    parse_qty("0")
    assert False
except ValueError:
    pass
```

```python
# after
with pytest.raises(ValueError, match="positive"):
    parse_qty("0")
```

## Practical Check Items

- Did you verify the error type specifically?
- Did you verify the message to lock in intent?
- Did you use `pytest.approx` for floating-point comparisons?
- Does the assert failure message preserve the inputs needed for reproduction?

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

## Case Study: Common Improvement Points in PR Reviews

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
- Are exception types specific?
- Can you identify the cause from the failure message?
- Is the structure extensible by adding data alone, without copying functions?

## Mini Checklist

- Maintain at least 3 failure cases.
- Include boundary values (min/max/empty).
- Confirm failure messages are meaningful.
- Verify the same command reproduces in CI.

## Quick Verification

```bash
pytest -q
```

```text
PASS
```

Tests must leave execution results and preserve failure inputs in reproducible form so the same problem never resurfaces in production.

## Answering the Opening Questions

- **Why does pytest's `assert` provide more readable failure messages?**
  - pytest internally rewrites `assert` to show actual and expected values together, so when `assert calc_tax(10000, 0.1) == 1200` fails, `1000 == 1200` and the call expression appear immediately. This makes tracking which calculation went wrong easy from CI logs alone, without adding `print()` statements.
- **How should collections, strings, and floating-point values be verified?**
  - Dicts and sets compared directly with `assert` have pytest show key and element differences in detail; strings are best fixed directly like `render_title(" Alice ") == "[USER] Alice"`. Floating-point requires explicit tolerance—`0.1 + 0.2 == pytest.approx(0.3)` or `pytest.approx([0.3, 0.5], rel=1e-5)`—for stable tests.
- **How do you verify exception type and message with `pytest.raises`?**
  - `with pytest.raises(ValueError, match="between 0 and 1"):` verifies both type and message together, locking not just that it failed but that it failed for the right reason. For more detailed checks, `exc_info.value` and `exc_info.type` let you directly inspect whether `divide(10, 0)` or `parse_qty("0")` produced the expected exception object.
<!-- toc:begin -->
## In this series

- [pytest 101 (1/10): Why Write Tests?](./01-why-write-tests.md)
- [pytest 101 (2/10): Writing Your First pytest Test](./02-first-pytest-test.md)
- **Assert and Exception Testing (current)**
- Understanding Fixtures (upcoming)
- Parametrization (upcoming)
- Mock and Monkeypatch (upcoming)
- Testing Files, Environment Variables, and Time (upcoming)
- Coverage and Test Quality (upcoming)
- Test Automation with GitHub Actions (upcoming)
- Writing Testable Code (upcoming)

<!-- toc:end -->

## References

- [pytest — Assertions](https://docs.pytest.org/en/stable/how-to/assert.html)
- [pytest — pytest.raises](https://docs.pytest.org/en/stable/reference/reference.html#pytest-raises)
- [pytest — pytest.approx](https://docs.pytest.org/en/stable/reference/reference.html#pytest-approx)
- [Real Python — Testing Exceptions](https://realpython.com/pytest-python-testing/#testing-for-exceptions)

Tags: Python, pytest, assert, Exception Testing, pytest.raises
