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
