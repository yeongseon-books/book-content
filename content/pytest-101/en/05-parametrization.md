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

This is the 5th post in the pytest 101 series.

> pytest 101 series (5/10)

**Key Question**: When testing the same logic with different inputs, do you have to copy the function?

> `@pytest.mark.parametrize` lets a single test function verify multiple input-output combinations. This article covers basic syntax, multi-parameter usage, and ID customization.


![pytest 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/pytest-101/05/05-01-big-picture.en.png)
*pytest 101 chapter 5 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Parametrization?
- Which signal should the example or diagram make visible for Parametrization?
- What failure should be prevented first when Parametrization reaches a real system?

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

## Parameter Design Deep Dive: Change Data, Keep Verification Logic

The advantage of parametrize is expanding the input space without increasing the number of test functions.

```python
# validator.py

def validate_username(name: str) -> bool:
    if not 3 <= len(name) <= 20:
        return False
    return name.replace("_", "").isalnum()
```

```python
# test_validator.py
import pytest
from validator import validate_username

@pytest.mark.parametrize(
    "name,expected",
    [
        pytest.param("abc", True, id="min-length"),
        pytest.param("ab", False, id="too-short"),
        pytest.param("user_name", True, id="underscore"),
        pytest.param("bad name", False, id="space"),
        pytest.param("x" * 21, False, id="too-long"),
    ],
)
def test_validate_username(name, expected):
    assert validate_username(name) is expected
```

## CLI Output Verification

```bash
pytest test_validator.py -v
```

```text
test_validator.py::test_validate_username[min-length] PASSED
test_validator.py::test_validate_username[too-short] PASSED
...
========================= 5 passed =========================
```

## Handling Happy and Error Cases in a Single Function

```python
# parser.py

def parse_port(value: str) -> int:
    port = int(value)
    if not 1 <= port <= 65535:
        raise ValueError("port out of range")
    return port
```

```python
# test_parser.py
import pytest
from parser import parse_port

@pytest.mark.parametrize("value,expected", [("80", 80), ("443", 443)])
def test_parse_port_ok(value, expected):
    assert parse_port(value) == expected

@pytest.mark.parametrize("value", ["0", "70000", "-1"])
def test_parse_port_fail(value):
    with pytest.raises(ValueError, match="out of range"):
        parse_port(value)
```

## Controlling Combinatorial Explosion

Nested parametrize is powerful but combinations grow fast.

| Methods | Statuses | Generated Tests |
|---|---|---|
| 3 | 3 | 9 |
| 5 | 6 | 30 |
| 8 | 10 | 80 |

Extract only the necessary boundaries to keep test execution time manageable.

## Before and After: Refactoring

```python
# before

def test_price_case1():
    assert discount(10000, "VIP") == 9000

def test_price_case2():
    assert discount(10000, "NEW") == 9500

def test_price_case3():
    assert discount(10000, "NONE") == 10000
```

```python
# after
import pytest

@pytest.mark.parametrize(
    "price,tier,expected",
    [
        (10000, "VIP", 9000),
        (10000, "NEW", 9500),
        (10000, "NONE", 10000),
    ],
)
def test_discount(price, tier, expected):
    assert discount(price, tier) == expected
```

Adding tests becomes adding a data row, not copying functions.

## Dataset Management Patterns

When parameter lists grow long, test file readability suffers. Group by category.

```python
VALID_CASES = [
    ("alice", True),
    ("bob_01", True),
]

INVALID_CASES = [
    ("ab", False),
    ("bad name", False),
    ("x" * 30, False),
]
```

```python
import pytest
from validator import validate_username

@pytest.mark.parametrize("name,expected", VALID_CASES, ids=["alice", "bob_01"])
def test_username_valid(name, expected):
    assert validate_username(name) is expected

@pytest.mark.parametrize("name,expected", INVALID_CASES, ids=["short", "space", "long"])
def test_username_invalid(name, expected):
    assert validate_username(name) is expected
```

## Interpreting Failure Output

```text
FAILED test_username_invalid[space] - assert True is False
```

With IDs, you can immediately read which case failed.

## Combining parametrize with raises

```python
import pytest

def to_int(v: str) -> int:
    if not v.strip().isdigit():
        raise ValueError("not integer")
    return int(v)

@pytest.mark.parametrize("bad", ["", "a1", "-1", "1.2"])
def test_to_int_invalid(bad):
    with pytest.raises(ValueError):
        to_int(bad)
```

## Refactoring Checklist

- When you start copying test functions, consider switching to parametrize
- Assign IDs to each case
- Separate happy and error cases
- Sample by category when combinations explode

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

## Answering the Opening Questions

- **How do you verify the same logic with multiple inputs without copying functions?**
  - Instead of multiplying functions like `test_is_palindrome_radar` and `test_is_palindrome_hello`, add inputs and expectations as data to `@pytest.mark.parametrize`. As the `validate_username`, `discount`, and `parse_port` examples show, keeping verification logic as one function while expanding only cases makes tests shorter and more consistent.
- **How should you read `@pytest.mark.parametrize`'s basic syntax?**
  - `@pytest.mark.parametrize("a,b,expected", [(1, 2, 3), (0, 0, 0)])` means running one test function independently for each tuple. Separating normal cases from error cases with `pytest.raises(ValueError, match="out of range")` in a separate function makes it clear in output which combination validates which contract.
- **How do you give each test case a readable name?**
  - Using `pytest.param(..., id="min-length")` or `ids=["alice", "bob_01"]` makes failure logs print meaningful names instead of data blobs. So `FAILED test_username_invalid[space]` immediately shows which input was problematic, and adding regression inputs to the list remains easy to track.
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
