---
series: pytest-101
episode: 5
title: "pytest 101 (5/10): Parametrization"
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
  - parametrize
  - Test Cases
  - Data-Driven Testing
seo_description: Learn to use @pytest.mark.parametrize for data-driven tests. Master syntax, multi-parameter usage, custom test IDs, and Cartesian products.
last_reviewed: '2026-05-04'
---

# pytest 101 (5/10): Parametrization

This is post 5 in the pytest 101 series.

> pytest 101 series (5/10)

**Key Question**: When testing the same logic with different inputs, do you have to copy the function?

> `@pytest.mark.parametrize` lets a single test function verify multiple input-output combinations. This article covers basic syntax, multi-parameter usage, and ID customization.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Parametrization?
- Which signal should the example or diagram make visible for Parametrization?
- What failure should be prevented first when Parametrization reaches a real system?

## Big Picture

![pytest 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/pytest-101/05/05-01-big-picture.en.png)

*pytest 101 chapter 5 flow overview*

This picture places Parametrization inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## What You Will Learn

- Basic syntax of `@pytest.mark.parametrize`
- Passing multiple parameters simultaneously
- Customizing test IDs for readability
- Combining parametrize with fixtures

## Why It Matters

When you need to test a function with many inputs, duplicating the function for each input causes code to explode. Parametrize lets you list input-output data and pytest runs each as an independent test.

> Instead of copy-pasting 5 tests, add 5 lines of data. Same logic, different data.

Boundary values, empty inputs, and special characters need comprehensive coverage — parametrize makes this practical.

## Mental Model

> parametrize = one test function + multiple data sets → N independent tests

```text
@pytest.mark.parametrize("input,expected", [
    ("hello", 5),      ← test 1
    ("", 0),            ← test 2
    ("hi", 2),          ← test 3
])
def test_length(input, expected):
    assert len(input) == expected
```

## Core Concepts

| Term | Description |
|------|-------------|
| parametrize | Decorator that injects test parameters |
| Test ID | Unique identifier assigned to each parameter combination |
| pytest.param | Assigns IDs or marks to individual test cases |
| indirect | Passes parametrize values to fixtures |
| Cartesian product | Stacking multiple parametrize decorators multiplies combinations |

## Before / After

Compare copy-paste tests with parametrize.

```python
# before: duplicate function per input
def test_is_palindrome_radar():
    assert is_palindrome("radar") is True

def test_is_palindrome_hello():
    assert is_palindrome("hello") is False

def test_is_palindrome_empty():
    assert is_palindrome("") is True

def test_is_palindrome_single():
    assert is_palindrome("a") is True
```

```python
# after: just list the data
import pytest

@pytest.mark.parametrize("word,expected", [
    ("radar", True),
    ("hello", False),
    ("", True),
    ("a", True),
])
def test_is_palindrome(word, expected):
    assert is_palindrome(word) is expected
```

## Step-by-Step Practice

### Step 1: Basic Parametrize

```python
# test_math.py
import pytest

def add(a, b):
    return a + b

@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
    (-5, -3, -8),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

### Step 2: String Parameters

```python
# test_string.py
import pytest

def slugify(text: str) -> str:
    return text.lower().strip().replace(" ", "-")

@pytest.mark.parametrize("input_text,expected", [
    ("Hello World", "hello-world"),
    ("  spaces  ", "spaces"),
    ("UPPER CASE", "upper-case"),
    ("already-slug", "already-slug"),
    ("multiple   spaces", "multiple---spaces"),
])
def test_slugify(input_text, expected):
    assert slugify(input_text) == expected
```

### Step 3: Exception Case Parametrize

```python
# test_validation.py
import pytest

def parse_age(value: str) -> int:
    age = int(value)
    if age < 0 or age > 150:
        raise ValueError(f"Invalid age: {age}")
    return age

@pytest.mark.parametrize("value,expected", [
    ("25", 25),
    ("0", 0),
    ("150", 150),
])
def test_parse_age_valid(value, expected):
    assert parse_age(value) == expected

@pytest.mark.parametrize("value", ["-1", "151", "999"])
def test_parse_age_invalid(value):
    with pytest.raises(ValueError):
        parse_age(value)
```

### Step 4: Custom IDs

```python
# test_with_ids.py
import pytest

@pytest.mark.parametrize("email,valid", [
    pytest.param("user@example.com", True, id="normal-email"),
    pytest.param("@example.com", False, id="missing-local"),
    pytest.param("user@", False, id="missing-domain"),
    pytest.param("", False, id="empty-string"),
    pytest.param("user@exam ple.com", False, id="space-in-domain"),
])
def test_validate_email(email, valid):
    result = "@" in email and len(email.split("@")) == 2
    has_domain = result and len(email.split("@")[1]) > 0
    has_local = result and len(email.split("@")[0]) > 0
    has_no_space = " " not in email
    assert (has_domain and has_local and has_no_space) == valid
```

### Step 5: Cartesian Product (Stacked Parametrize)

```python
# test_cartesian.py
import pytest

@pytest.mark.parametrize("method", ["GET", "POST", "PUT"])
@pytest.mark.parametrize("status", [200, 404, 500])
def test_http_response(method, status):
    """3 methods x 3 statuses = 9 tests generated."""
    response = {"method": method, "status": status}
    assert response["method"] in ["GET", "POST", "PUT", "DELETE"]
    assert isinstance(response["status"], int)
```

## What to Notice in This Code

- Each parameter combination runs as an independent test — one failure doesn't block the rest
- `pytest.param`'s `id` provides meaningful names in test output
- Stacking parametrize decorators creates a Cartesian product
- Separating valid and exception cases into different parametrize blocks improves readability

## Common Mistakes

| Mistake | Why It's a Problem | Fix |
|---------|-------------------|-----|
| Spaces in parameter names | `"a, b"` with spaces causes parsing errors | Use `"a,b"` or a list `["a", "b"]` |
| Parameter count mismatch | Tuple element count doesn't match parameter count | Ensure all tuples have the same length |
| Too many cases in one parametrize | Beyond 50 cases, readability drops | Split by category into separate parametrize blocks |
| Mutable objects as parameters | Lists or dicts may be shared across tests | Copy inside the test or use tuples |
| Complex parameters without IDs | Failures show cryptic `test[param0-param1]` | Use `pytest.param(..., id="description")` |

## Practical Applications

- Batch-test boundary values (empty strings, max lengths, special characters) in validation functions
- Verify various HTTP status code responses with parametrize
- Cover multiple languages in internationalization (i18n) tests
- Test diverse filter combinations in database queries using Cartesian products
- Load parameter data from JSON/YAML files to separate test data from code

## How Practitioners Think About This

Parametrize is the perfect solution for the "same verification logic, different data" pattern. Add 50 test cases without writing a single new line of logic.

In practice, when a bug report arrives, the failing input gets added to a parametrize block as a regression test. If the same bug reappears, it's caught immediately.

## Checklist

- [ ] Wrote a test using `@pytest.mark.parametrize`
- [ ] Separated valid and exception cases
- [ ] Customized test IDs with `pytest.param`
- [ ] Created a Cartesian product with stacked parametrize
- [ ] Verified individual test cases with the `-v` option

## Exercises

1. Write a `fizzbuzz(n)` function and parametrize test cases for inputs 1 through 15.
2. Write a password validation function and parametrize tests for minimum length, uppercase, and digit requirements.
3. Create a Cartesian product of HTTP methods and Content-Types, and count how many tests are generated.

## Summary and Next

Parametrize is the core tool for data-driven testing. A single test function covers diverse inputs, eliminating code duplication. Next, we'll learn mock and monkeypatch for replacing external dependencies.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Parametrization?**
  - The article treats Parametrization as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Parametrization?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Parametrization reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [pytest 101 (1/10): Why Write Tests?](./01-why-write-tests.md)
- [pytest 101 (2/10): Writing Your First pytest Test](./02-first-pytest-test.md)
- [pytest 101 (3/10): Assert and Exception Testing](./03-assert-and-exceptions.md)
- [pytest 101 (4/10): Understanding Fixtures](./04-fixtures.md)
- **Parametrization (current)**
- Mock and Monkeypatch (upcoming)
- Testing Files, Environment Variables, and Time (upcoming)
- Coverage and Test Quality (upcoming)
- Test Automation with GitHub Actions (upcoming)
- Writing Testable Code (upcoming)

<!-- toc:end -->

## References

- [pytest — Parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html)
- [pytest — pytest.param](https://docs.pytest.org/en/stable/reference/reference.html#pytest-param)
- [Real Python — Parametrize Tests](https://realpython.com/pytest-python-testing/#parametrize)
- [Effective Python Testing with pytest — Parametrize](https://testdriven.io/blog/testing-python/)

Tags: Python, pytest, parametrize, Test Cases, Data-Driven Testing
