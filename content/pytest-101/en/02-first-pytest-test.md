---
series: pytest-101
episode: 2
title: "pytest 101 (2/10): Writing Your First pytest Test"
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
  - Test Writing
  - Test Discovery
  - Project Structure
seo_description: Learn pytest discovery rules, project layout with the src directory, and how to execute specific tests using node IDs and keyword filtering.
last_reviewed: '2026-05-04'
---

# pytest 101 (2/10): Writing Your First pytest Test

This is post 2 in the pytest 101 series.

> pytest 101 series (2/10)

**Key Question**: How does pytest automatically find test files and functions?

> pytest uses the `test_` prefix convention to auto-discover files and functions. This article covers project layout, writing tests, and using various execution options.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Writing Your First pytest Test?
- Which signal should the example or diagram make visible for Writing Your First pytest Test?
- What failure should be prevented first when Writing Your First pytest Test reaches a real system?

## Big Picture

![pytest 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/pytest-101/02/02-01-big-picture.en.png)

*pytest 101 chapter 2 flow overview*

This picture places Writing Your First pytest Test inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## What You Will Learn

- pytest's test discovery rules
- Separating production and test code directories
- pytest execution options and output interpretation
- The role and placement of conftest.py

## Why It Matters

No matter how well-written your tests are, they won't run if pytest can't find them. Getting the project structure and naming conventions right from the start makes test management effortless.

> The location and name of your test code are the rules. Follow them and pytest handles everything automatically with zero configuration.

When test structure is consistent across a team project, new members know where tests live before they even open the code.

## Mental Model

> test discovery = the mechanism by which pytest automatically locates test files and functions

```text
project/
├── src/
│   └── myapp/
│       ├── __init__.py
│       └── calculator.py    ← production code
└── tests/
    ├── conftest.py          ← shared fixtures
    ├── test_calculator.py   ← test code
    └── test_utils.py        ← test code
```

## Core Concepts

| Term | Description |
|------|-------------|
| Test discovery | Automatically locates tests by file, class, and function naming rules |
| conftest.py | Configuration file for sharing fixtures across test files |
| Test node ID | Identifies individual tests in `file::class::function` format |
| Test marker | Classifies tests with `@pytest.mark` for selective execution |
| Exit code | 0 means all passed, 1 means some failed, 2 means user interrupt |

## Before / After

Compare a project with no test structure to one with organized tests.

```python
# before: production code and test logic mixed together
# main.py
def greet(name):
    return f"Hello, {name}"

if __name__ == "__main__":
    print(greet("World"))  # manual verification
```

```python
# after: separated structure
# src/myapp/greeting.py
def greet(name: str) -> str:
    if not name:
        raise ValueError("Name cannot be empty")
    return f"Hello, {name}"

# tests/test_greeting.py
import pytest
from myapp.greeting import greet

def test_greet():
    assert greet("World") == "Hello, World"

def test_greet_empty_name():
    with pytest.raises(ValueError):
        greet("")
```

## Step-by-Step Practice

### Step 1: Create Project Structure

```bash
mkdir -p src/myapp tests
touch src/myapp/__init__.py
```

### Step 2: Write Production Code

```python
# src/myapp/string_utils.py
def reverse_string(s: str) -> str:
    """Reverses a string."""
    if not isinstance(s, str):
        raise TypeError("Input must be a string")
    return s[::-1]

def count_vowels(s: str) -> int:
    """Counts the number of vowels."""
    return sum(1 for c in s.lower() if c in "aeiou")

def truncate(s: str, max_length: int = 10) -> str:
    """Truncates a string to the specified maximum length."""
    if len(s) <= max_length:
        return s
    return s[:max_length] + "..."
```

### Step 3: Write Tests

```python
# tests/test_string_utils.py
import pytest
from myapp.string_utils import reverse_string, count_vowels, truncate

class TestReverseString:
    def test_basic(self):
        assert reverse_string("hello") == "olleh"

    def test_empty(self):
        assert reverse_string("") == ""

    def test_palindrome(self):
        assert reverse_string("radar") == "radar"

    def test_type_error(self):
        with pytest.raises(TypeError):
            reverse_string(123)

class TestCountVowels:
    def test_basic(self):
        assert count_vowels("hello") == 2

    def test_no_vowels(self):
        assert count_vowels("xyz") == 0

    def test_all_vowels(self):
        assert count_vowels("aeiou") == 5

class TestTruncate:
    def test_short_string(self):
        assert truncate("hi", 10) == "hi"

    def test_long_string(self):
        assert truncate("hello world", 5) == "hello..."

    def test_exact_length(self):
        assert truncate("hello", 5) == "hello"
```

### Step 4: Configure pyproject.toml

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

### Step 5: Run Tests in Various Ways

```bash
# run all tests
pytest

# verbose output
pytest -v

# specific file
pytest tests/test_string_utils.py

# specific class
pytest tests/test_string_utils.py::TestReverseString

# specific test
pytest tests/test_string_utils.py::TestReverseString::test_basic

# filter by keyword
pytest -k "vowel"

# stop on first failure
pytest -x
```

## What to Notice in This Code

- `class Test*` groups related tests for better readability
- `pyproject.toml`'s `pythonpath` tells pytest where to find the `src` directory
- The `-k` option filters tests by partial name match
- Node IDs (`file::class::function`) target exactly one test

## Common Mistakes

| Mistake | Why It's a Problem | Fix |
|---------|-------------------|-----|
| Not adding `src/` to `pythonpath` | Causes `ModuleNotFoundError` | Add `pythonpath = ["src"]` in `pyproject.toml` |
| Missing `__init__.py` | Directory not recognized as a package | Create `__init__.py` in every package directory |
| Defining `__init__` in test classes | pytest won't recognize the class as a test class | Never define `__init__` in test classes |
| Trying to import conftest.py | conftest.py is loaded automatically by pytest | Don't write `import conftest` |
| Using hyphens in test filenames | Python can't import modules with hyphens | Use underscores instead of hyphens |

## Practical Applications

- Separate `tests/` from `src/` so tests aren't included in the distribution package
- Define common fixtures like database connections and HTTP clients in `conftest.py`
- Use `-x` flag in CI to fail fast on first error
- Share identical settings across the team via `pytest.ini` or `pyproject.toml`
- Use `-k` to quickly run only tests related to a specific feature

## How Practitioners Think About This

Setting up test structure early pays dividends as the codebase grows. "I'll add tests later" almost always means "I'll never add tests."

In practice, the `src/` layout is used to clearly separate production code from tests. This ensures test code isn't included when running `pip install .`.

## Checklist

- [ ] Organized the project with `src/` layout
- [ ] Configured `testpaths` and `pythonpath` in `pyproject.toml`
- [ ] Ran all tests with `pytest -v`
- [ ] Executed a specific test using its node ID
- [ ] Used the `-k` option for keyword filtering

## Exercises

1. Write a `capitalize_words(s)` function and group tests for empty string, single word, and multiple words into a test class.
2. Run `pytest` without `pyproject.toml`, observe the error, then fix it by adding the configuration.
3. Use `-k` to run only tests containing "reverse" and verify the results.

## Summary and Next

You've learned pytest's test discovery rules and project structure. The `test_` prefix and `src/` layout are the foundation. Next, we'll dive deep into `assert` patterns and exception testing.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Writing Your First pytest Test?**
  - The article treats Writing Your First pytest Test as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Writing Your First pytest Test?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Writing Your First pytest Test reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [pytest 101 (1/10): Why Write Tests?](./01-why-write-tests.md)
- **Writing Your First pytest Test (current)**
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

- [pytest — Test Discovery](https://docs.pytest.org/en/stable/goodpractices.html#test-discovery)
- [pytest — Configuration](https://docs.pytest.org/en/stable/reference/customize.html)
- [src layout vs flat layout — Python Packaging Guide](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
- [Real Python — Effective Python Testing With Pytest](https://realpython.com/pytest-python-testing/)

Tags: Python, pytest, Test Writing, Test Discovery, Project Structure
