---
series: pytest-101
episode: 1
title: Why Write Tests?
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
  - Testing
  - Software Quality
  - Test Automation
seo_description: Learn how testing improves development productivity and code quality with pytest.
last_reviewed: '2026-05-04'
---

# Why Write Tests?

> pytest 101 series (1/10)

<!-- a-grade-intro:begin -->

**Key Question**: Does writing tests slow down development?

> Tests don't slow you down — they remove the fear of change and ultimately speed you up. This article explains why tests matter, what kinds exist, and why pytest is the go-to tool for Python testing.

<!-- a-grade-intro:end -->

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

```
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

```
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

<!-- toc:begin -->
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
