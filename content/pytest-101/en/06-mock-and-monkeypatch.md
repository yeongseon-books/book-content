---
series: pytest-101
episode: 6
title: "pytest 101 (6/10): Mock and Monkeypatch"
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
  - mock
  - monkeypatch
  - Test Doubles
seo_description: Isolate dependencies with mock and monkeypatch in pytest. Master function replacement, exception simulation, and call verification with assert.
last_reviewed: '2026-05-04'
---

# pytest 101 (6/10): Mock and Monkeypatch

This is post 6 in the pytest 101 series.

> pytest 101 series (6/10)

**Key Question**: How do you test a function without actually calling the database or an external API?

> A mock replaces real dependencies with fake objects to isolate the code under test. Monkeypatch temporarily swaps functions, attributes, and environment variables within the test scope. This article covers the differences between the two tools and their usage patterns.


![pytest 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/pytest-101/06/06-01-big-picture.en.png)
*pytest 101 chapter 6 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Mock and Monkeypatch?
- Which signal should the example or diagram make visible for Mock and Monkeypatch?
- What failure should be prevented first when Mock and Monkeypatch reaches a real system?

## What You Will Learn

- When to choose mock versus monkeypatch
- Replacing functions with `unittest.mock.patch`
- Swapping attributes with `monkeypatch.setattr`
- Verifying calls with `assert_called_with` patterns

## Why It Matters

A unit test should verify one function in isolation. When that function depends on databases, external APIs, or the file system, tests become slow, flaky, and environment-dependent. Mocking removes those dependencies, producing fast and stable tests.

> A mock verifies "how does this function interact with the outside world?" — without making a real call. You confirm that the right parameters were passed, without waiting for a network round-trip.

In production, mocks prevent test failures caused by external service outages.

## Mental Model

> mock = swap the real thing with a fake to isolate the test

```text
[Production]                    [Test]
function → DB query → result    function → Mock(DB) → fake result
function → HTTP call → response function → Mock(HTTP) → fake response
```

## Core Concepts

| Term | Description |
|------|-------------|
| mock | A fake object that replaces the real one |
| patch | Swaps an object at a given import path with a mock |
| monkeypatch | Built-in pytest fixture that temporarily changes attributes and env vars |
| MagicMock | A mock that records all attribute accesses and method calls |
| side_effect | Specifies a function to run or an exception to raise when the mock is called |

## Before / After

Compare a test calling the real API with one isolated by a mock.

```python
# before: real HTTP call — slow and externally dependent
import requests

def get_user_name(user_id):
    response = requests.get(f"https://api.example.com/users/{user_id}")
    return response.json()["name"]

def test_get_user_name():
    # real API call — requires network, slow, flaky
    name = get_user_name(1)
    assert name == "Alice"
```

```python
# after: mock replaces the HTTP call
from unittest.mock import patch, MagicMock

def test_get_user_name():
    mock_response = MagicMock()
    mock_response.json.return_value = {"name": "Alice"}

    with patch("requests.get", return_value=mock_response):
        name = get_user_name(1)
    assert name == "Alice"
```

## Step-by-Step Practice

### Step 1: Basic Mock Usage

```python
# weather.py
import requests

def get_temperature(city: str) -> float:
    response = requests.get(
        f"https://api.weather.com/v1/current?city={city}"
    )
    data = response.json()
    return data["temperature"]
```

```python
# test_weather.py
from unittest.mock import patch, MagicMock
from weather import get_temperature

def test_get_temperature():
    mock_response = MagicMock()
    mock_response.json.return_value = {"temperature": 22.5}

    with patch("weather.requests.get", return_value=mock_response) as mock_get:
        result = get_temperature("Seoul")

    assert result == 22.5
    mock_get.assert_called_once_with(
        "https://api.weather.com/v1/current?city=Seoul"
    )
```

### Step 2: Replacing a Function with monkeypatch

```python
# notification.py
import smtplib

def send_email(to: str, subject: str, body: str) -> bool:
    server = smtplib.SMTP("smtp.example.com")
    server.sendmail("noreply@example.com", to, f"Subject: {subject}\n\n{body}")
    server.quit()
    return True
```

```python
# test_notification.py
from notification import send_email

def test_send_email(monkeypatch):
    sent_emails = []

    class FakeSMTP:
        def __init__(self, host):
            self.host = host

        def sendmail(self, from_addr, to_addr, msg):
            sent_emails.append({"to": to_addr, "msg": msg})

        def quit(self):
            pass

    monkeypatch.setattr("notification.smtplib.SMTP", FakeSMTP)

    result = send_email("user@test.com", "Hello", "Test body")

    assert result is True
    assert len(sent_emails) == 1
    assert sent_emails[0]["to"] == "user@test.com"
```

### Step 3: Simulating Exceptions with side_effect

```python
# test_error_handling.py
from unittest.mock import patch, MagicMock
import requests
from weather import get_temperature

def test_network_error():
    with patch("weather.requests.get", side_effect=requests.ConnectionError):
        try:
            get_temperature("Seoul")
            assert False, "Expected an exception"
        except requests.ConnectionError:
            pass  # expected

def test_invalid_json():
    mock_response = MagicMock()
    mock_response.json.side_effect = ValueError("Invalid JSON")

    with patch("weather.requests.get", return_value=mock_response):
        try:
            get_temperature("Seoul")
            assert False, "Expected an exception"
        except ValueError:
            pass
```

### Step 4: Setting Environment Variables with monkeypatch

```python
# config.py
import os

def get_database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL is not set")
    return url
```

```python
# test_config.py
import pytest
from config import get_database_url

def test_database_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
    assert get_database_url() == "sqlite:///test.db"

def test_missing_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValueError, match="DATABASE_URL"):
        get_database_url()
```

### Step 5: Call Verification Patterns

```python
# test_call_verification.py
from unittest.mock import MagicMock, call

def process_items(items, handler):
    for item in items:
        handler(item)

def test_handler_called_for_each_item():
    mock_handler = MagicMock()

    process_items(["a", "b", "c"], mock_handler)

    assert mock_handler.call_count == 3
    mock_handler.assert_has_calls([
        call("a"),
        call("b"),
        call("c"),
    ])
```

## What to Notice in This Code

- The first argument to `patch` is the import path where the target is *used* — not where it's defined
- `monkeypatch` is a fixture, so it automatically restores original values after the test
- `side_effect` raises exceptions to test error handling paths
- `assert_called_once_with` verifies the exact parameters passed to a mock

## Common Mistakes

| Mistake | Why It's a Problem | Fix |
|---------|-------------------|-----|
| Patching the definition path | The mock doesn't apply because the import path differs | Patch where the target is imported, not defined |
| Overusing mocks | Tests couple to implementation details, making refactoring painful | Verify results, not internal calls |
| Confusing return_value and side_effect | Fixed return vs. dynamic behavior serve different purposes | Use return_value for constants, side_effect for functions or exceptions |
| Manual setattr without monkeypatch | Forgetting to restore the original value leaks state | Always use the monkeypatch fixture |
| Accessing typo'd attributes on MagicMock | MagicMock auto-creates any attribute, hiding typos | Use `spec=True` to enforce the real interface |

## Practical Applications

- Mock external API calls so CI tests run without network access
- Isolate environment variables per test with monkeypatch
- Safely test side-effect-heavy code like payment modules
- Sync mock interfaces with real objects using `spec=True`
- Simulate timeouts and network errors via side_effect

## How Practitioners Think About This

Mocks are powerful, but overuse leads to "tests that test the implementation." If you need more than 5 mocks, it's a signal that the code has too many dependencies.

Monkeypatch fits simple substitutions like environment variables and config values. `unittest.mock` excels at complex call verification. Pick the right tool for the situation.

## Checklist

- [ ] Used `unittest.mock.patch` to mock an external dependency
- [ ] Replaced a function with `monkeypatch.setattr`
- [ ] Set an environment variable with `monkeypatch.setenv`
- [ ] Simulated an exception with `side_effect`
- [ ] Verified a call with `assert_called_once_with`

## Exercises

1. Mock `requests.get` to test both HTTP 200 and 404 responses separately.
2. Use monkeypatch to replace `datetime.now()` with a fixed time and write a test.
3. Use `spec=True` to confirm that calling a non-existent method on a mock raises an error.

## Summary and Next

Mock and monkeypatch remove external dependencies to make tests fast and stable. Next, we'll explore concrete patterns for testing files, environment variables, and time-dependent code.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Mock and Monkeypatch?**
  - The article treats Mock and Monkeypatch as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Mock and Monkeypatch?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Mock and Monkeypatch reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [pytest 101 (1/10): Why Write Tests?](./01-why-write-tests.md)
- [pytest 101 (2/10): Writing Your First pytest Test](./02-first-pytest-test.md)
- [pytest 101 (3/10): Assert and Exception Testing](./03-assert-and-exceptions.md)
- [pytest 101 (4/10): Understanding Fixtures](./04-fixtures.md)
- [pytest 101 (5/10): Parametrization](./05-parametrization.md)
- **Mock and Monkeypatch (current)**
- Testing Files, Environment Variables, and Time (upcoming)
- Coverage and Test Quality (upcoming)
- Test Automation with GitHub Actions (upcoming)
- Writing Testable Code (upcoming)

<!-- toc:end -->

## References

- [pytest — monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)
- [unittest.mock — Python Docs](https://docs.python.org/3/library/unittest.mock.html)
- [Real Python — Understanding the Python Mock Object Library](https://realpython.com/python-mock-library/)
- [pytest-mock — Plugin Documentation](https://pytest-mock.readthedocs.io/)

Tags: Python, pytest, mock, monkeypatch, Test Doubles
