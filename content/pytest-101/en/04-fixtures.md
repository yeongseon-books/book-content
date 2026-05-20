---
series: pytest-101
episode: 4
title: "pytest 101 (4/10): Understanding Fixtures"
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
  - Fixtures
  - conftest
  - Test Data
seo_description: Master pytest fixtures to manage test data efficiently. Learn about fixture injection, scopes, yield teardown, and sharing with conftest.py.
last_reviewed: '2026-05-04'
---

# pytest 101 (4/10): Understanding Fixtures

This is post 4 in the pytest 101 series.

> pytest 101 series (4/10)

**Key Question**: How do you avoid duplicating setup code across multiple tests?

> pytest fixtures define test data and state as functions, injecting them automatically by parameter name. This article covers fixture creation, scope management, and yield-based teardown.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Understanding Fixtures?
- Which signal should the example or diagram make visible for Understanding Fixtures?
- What failure should be prevented first when Understanding Fixtures reaches a real system?

## Big Picture

![pytest 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/pytest-101/04/04-01-big-picture.en.png)

*pytest 101 chapter 4 flow overview*

This picture places Understanding Fixtures inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Understanding Fixtures is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## What You Will Learn

- Defining fixtures and injecting them into tests
- The difference between fixture scopes (function, class, module, session)
- Separating setup and teardown with yield fixtures
- Sharing fixtures across files with conftest.py

## Why It Matters

When every test repeats the same object creation code, test files become bloated and hard to maintain. Fixtures eliminate that repetition, letting tests focus on *what* they verify.

> Fixtures are the "Given" in Given-When-Then. Pull Given into a fixture, and the test body is just When and Then.

Resources like database connections, API clients, and temporary files need fixtures to be created and cleaned up safely.

## Mental Model

> fixture = a reusable component that prepares state before a test and cleans up after

```text
@pytest.fixture
def user():            ← fixture definition
    return User("Alice")

def test_greet(user):  ← auto-injected by parameter name
    assert user.name == "Alice"
```

## Core Concepts

| Term | Description |
|------|-------------|
| Fixture | A function that provides test data or state |
| Scope | Controls the fixture's lifetime (function, class, module, session) |
| Yield fixture | Code before yield is setup; code after is teardown |
| conftest.py | Configuration file for sharing fixtures across test files |
| autouse | Fixture applied automatically without explicit request |

## Before / After

Compare unittest-style setUp/tearDown with pytest fixtures.

```python
# before: unittest style — setUp/tearDown methods
import unittest
import tempfile
import os

class TestFileProcessor(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.filepath = os.path.join(self.tmpdir, "test.txt")
        with open(self.filepath, "w") as f:
            f.write("hello")

    def tearDown(self):
        os.remove(self.filepath)
        os.rmdir(self.tmpdir)

    def test_read(self):
        with open(self.filepath) as f:
            assert f.read() == "hello"
```

```python
# after: pytest fixture — declarative and reusable
import pytest

@pytest.fixture
def text_file(tmp_path):
    filepath = tmp_path / "test.txt"
    filepath.write_text("hello")
    return filepath

def test_read(text_file):
    assert text_file.read_text() == "hello"
# no teardown needed — tmp_path auto-cleans
```

## Step-by-Step Practice

### Step 1: Define Basic Fixtures

```python
# conftest.py
import pytest

@pytest.fixture
def sample_user():
    return {"name": "Alice", "age": 30, "role": "developer"}

@pytest.fixture
def sample_users():
    return [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
        {"name": "Charlie", "age": 35},
    ]
```

### Step 2: Use Fixtures

```python
# test_user.py

def test_user_name(sample_user):
    assert sample_user["name"] == "Alice"

def test_user_count(sample_users):
    assert len(sample_users) == 3

def test_youngest_user(sample_users):
    youngest = min(sample_users, key=lambda u: u["age"])
    assert youngest["name"] == "Bob"
```

### Step 3: Yield Fixtures for Resource Management

```python
# conftest.py
import pytest
import sqlite3

@pytest.fixture
def db_connection():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute("INSERT INTO users (name) VALUES ('Alice')")
    conn.commit()
    yield conn  # provide conn to the test
    conn.close()  # cleanup after test

# test_db.py
def test_query_user(db_connection):
    cursor = db_connection.execute("SELECT name FROM users")
    row = cursor.fetchone()
    assert row[0] == "Alice"
```

### Step 4: Fixture Scopes

```python
# conftest.py
import pytest

@pytest.fixture(scope="module")
def expensive_resource():
    """Shared across all tests in the module."""
    print("Creating resource (runs once)")
    resource = {"data": list(range(10000))}
    yield resource
    print("Cleaning up resource (runs once at module end)")

# test_scope.py
def test_first(expensive_resource):
    assert len(expensive_resource["data"]) == 10000

def test_second(expensive_resource):
    # reuses the same resource
    assert expensive_resource["data"][0] == 0
```

### Step 5: Fixture Composition

```python
# conftest.py
import pytest

@pytest.fixture
def base_url():
    return "https://api.example.com"

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}

@pytest.fixture
def api_client(base_url, auth_headers):
    """Composes other fixtures."""
    return {
        "base_url": base_url,
        "headers": auth_headers,
    }

# test_api.py
def test_api_client_has_auth(api_client):
    assert "Authorization" in api_client["headers"]

def test_api_client_url(api_client):
    assert api_client["base_url"].startswith("https://")
```

## What to Notice in This Code

- The fixture name *is* the parameter name — no explicit calls needed
- Code before `yield` is setup; code after is teardown
- `scope="module"` reduces the number of times expensive resources are created
- Fixtures compose by listing other fixtures as parameters

## Common Mistakes

| Mistake | Why It's a Problem | Fix |
|---------|-------------------|-----|
| Asserting inside fixtures | Fixtures provide data, they don't verify | Keep asserts in test functions only |
| Using function-scope fixture in module-scope | Scope mismatch causes errors | Match dependent fixture scopes |
| Opening resources without yield | Files or connections never close | Add yield with cleanup code |
| Importing conftest.py | pytest loads it automatically | Use fixture names without import |
| Overusing autouse | Unnecessary fixtures applied to all tests | Reserve autouse for cross-cutting concerns like logging |

## Practical Applications

- Manage database connections with session-scope fixtures for faster test suites
- Use the built-in `tmp_path` fixture for temporary files with automatic cleanup
- Provide authentication tokens via fixtures in API tests
- Place conftest.py files at different directory levels for hierarchical fixture scoping
- Use factory fixtures to generate diverse test data variations

## How Practitioners Think About This

Fixtures determine the readability and maintainability of your tests. Well-designed fixtures make test code read like scenario descriptions.

Scope selection follows the rule: "Is it safe for tests to share this data?" Immutable data gets module or session scope; mutable data stays at function scope.

## Checklist

- [ ] Defined a fixture with `@pytest.fixture` and injected it into a test
- [ ] Separated setup/teardown with a yield fixture
- [ ] Understood scope differences and chose appropriately
- [ ] Placed shared fixtures in conftest.py
- [ ] Composed complex test data from multiple fixtures

## Exercises

1. Create a fixture providing an SQLite in-memory database, and write tests that verify INSERT and SELECT operations.
2. Use the `tmp_path` built-in fixture to create and read a temporary JSON file.
3. Compare execution counts of `scope="session"` and `scope="function"` fixtures using the `-s` flag.

## Summary and Next

Fixtures are pytest's core mechanism for managing test data. Understanding scope and yield lets you manage resources safely and efficiently. Next, we'll learn how parametrization lets a single test function verify multiple inputs.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Understanding Fixtures?**
  - The article treats Understanding Fixtures as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Understanding Fixtures?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Understanding Fixtures reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [pytest 101 (1/10): Why Write Tests?](./01-why-write-tests.md)
- [pytest 101 (2/10): Writing Your First pytest Test](./02-first-pytest-test.md)
- [pytest 101 (3/10): Assert and Exception Testing](./03-assert-and-exceptions.md)
- **Understanding Fixtures (current)**
- Parametrization (upcoming)
- Mock and Monkeypatch (upcoming)
- Testing Files, Environment Variables, and Time (upcoming)
- Coverage and Test Quality (upcoming)
- Test Automation with GitHub Actions (upcoming)
- Writing Testable Code (upcoming)

<!-- toc:end -->

## References

- [pytest — Fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [pytest — conftest.py](https://docs.pytest.org/en/stable/how-to/fixtures.html#conftest-py-sharing-fixtures-across-files)
- [pytest — Built-in Fixtures](https://docs.pytest.org/en/stable/reference/fixtures.html)
- [Real Python — pytest Fixtures](https://realpython.com/pytest-python-testing/#fixtures-managing-state-and-dependencies)

Tags: Python, pytest, Fixtures, conftest, Test Data
