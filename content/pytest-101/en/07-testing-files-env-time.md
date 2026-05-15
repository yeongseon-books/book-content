---
series: pytest-101
episode: 7
title: Testing Files, Environment Variables, and Time
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
  - tmp_path
  - freezegun
  - System Resource Testing
seo_description: Test file I/O with tmp_path, environment variables with monkeypatch, and time-dependent logic with freezegun for stable and reproducible tests.
last_reviewed: '2026-05-04'
---

# Testing Files, Environment Variables, and Time

This is post 7 in the pytest 101 series.

> pytest 101 series (7/10)

<!-- a-grade-intro:begin -->

**Key Question**: How do you reliably test code that reads files or depends on the current time?

> pytest's `tmp_path` fixture manages temporary files, `monkeypatch` isolates environment variables, and `freezegun` freezes the clock. This article covers patterns for testing code that depends on system resources.

<!-- a-grade-intro:end -->

## What You Will Learn

- Managing temporary files with `tmp_path` and `tmp_path_factory`
- Isolating environment variables per test with `monkeypatch.setenv`
- Freezing time with `freezegun` to test time-dependent logic
- Safe patterns for file system tests

## Why It Matters

File I/O, environment variables, and the current time are the trickiest external dependencies in testing. Testing files without temporary directories causes collisions between tests, and time-dependent tests fail at midnight or month-end.

> Tests that depend on system resources are the primary source of "passes today, fails tomorrow" flaky tests.

Master these three patterns and you can isolate most system dependencies.

## Mental Model

> system resource isolation = controlling files, env vars, and time within the test scope

```text
[Before Isolation]                [After Isolation]
files → real path collisions      tmp_path → auto-cleanup
env vars → global pollution       monkeypatch → restored after test
time → varies per execution       freezegun → fixed time
```

## Core Concepts

| Term | Description |
|------|-------------|
| tmp_path | Built-in pytest fixture providing a per-test temporary directory |
| tmp_path_factory | Session-scoped fixture for shared temporary directories |
| monkeypatch.setenv | Sets an environment variable within the test scope |
| freezegun | Library that replaces `datetime.now()` with a fixed time |
| flaky test | A test that intermittently fails on identical code |

## Before / After

Compare a test using real file paths with one isolated by tmp_path.

```python
# before: real paths — risk of collisions between tests
import os

def test_write_file():
    with open("/tmp/test_output.txt", "w") as f:
        f.write("hello")
    with open("/tmp/test_output.txt") as f:
        assert f.read() == "hello"
    os.remove("/tmp/test_output.txt")  # leaked if forgotten
```

```python
# after: tmp_path — automatic isolation and cleanup
def test_write_file(tmp_path):
    filepath = tmp_path / "test_output.txt"
    filepath.write_text("hello")
    assert filepath.read_text() == "hello"
    # no cleanup needed — pytest handles it
```

## Step-by-Step Practice

### Step 1: File Testing with tmp_path

```python
# file_processor.py
from pathlib import Path
import json

def save_config(config: dict, filepath: Path) -> None:
    filepath.write_text(json.dumps(config, indent=2))

def load_config(filepath: Path) -> dict:
    if not filepath.exists():
        raise FileNotFoundError(f"{filepath} does not exist")
    return json.loads(filepath.read_text())
```

```python
# test_file_processor.py
import pytest
from pathlib import Path
from file_processor import save_config, load_config

def test_save_and_load(tmp_path):
    config = {"host": "localhost", "port": 8080}
    filepath = tmp_path / "config.json"

    save_config(config, filepath)
    loaded = load_config(filepath)

    assert loaded == config

def test_load_missing_file(tmp_path):
    filepath = tmp_path / "missing.json"
    with pytest.raises(FileNotFoundError):
        load_config(filepath)

def test_nested_directory(tmp_path):
    nested = tmp_path / "a" / "b" / "c"
    nested.mkdir(parents=True)
    filepath = nested / "deep.txt"
    filepath.write_text("deep content")
    assert filepath.read_text() == "deep content"
```

### Step 2: Multi-File Processing Test

```python
# csv_processor.py
from pathlib import Path
import csv

def merge_csv_files(input_dir: Path, output_file: Path) -> int:
    rows = []
    for csv_file in sorted(input_dir.glob("*.csv")):
        with open(csv_file) as f:
            reader = csv.DictReader(f)
            rows.extend(reader)

    if not rows:
        return 0

    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)
```

```python
# test_csv_processor.py
from csv_processor import merge_csv_files

def test_merge_csv(tmp_path):
    (tmp_path / "a.csv").write_text("name,age\nAlice,30\n")
    (tmp_path / "b.csv").write_text("name,age\nBob,25\n")

    output = tmp_path / "merged.csv"
    count = merge_csv_files(tmp_path, output)

    assert count == 2
    lines = output.read_text().strip().split("\n")
    assert len(lines) == 3  # header + 2 rows

def test_merge_empty_dir(tmp_path):
    output = tmp_path / "merged.csv"
    count = merge_csv_files(tmp_path, output)
    assert count == 0
```

### Step 3: Environment Variable Testing

```python
# app_config.py
import os

def get_config() -> dict:
    return {
        "debug": os.environ.get("DEBUG", "false").lower() == "true",
        "db_url": os.environ.get("DATABASE_URL", "sqlite:///default.db"),
        "log_level": os.environ.get("LOG_LEVEL", "INFO"),
    }
```

```python
# test_app_config.py
from app_config import get_config

def test_default_config(monkeypatch):
    monkeypatch.delenv("DEBUG", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    config = get_config()
    assert config["debug"] is False
    assert config["db_url"] == "sqlite:///default.db"
    assert config["log_level"] == "INFO"

def test_production_config(monkeypatch):
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("DATABASE_URL", "postgresql://prod:5432/app")
    monkeypatch.setenv("LOG_LEVEL", "WARNING")

    config = get_config()
    assert config["debug"] is False
    assert "postgresql" in config["db_url"]
    assert config["log_level"] == "WARNING"

def test_debug_mode(monkeypatch):
    monkeypatch.setenv("DEBUG", "True")
    config = get_config()
    assert config["debug"] is True
```

### Step 4: Freezing Time

```python
# billing.py
from datetime import datetime

def is_billing_day() -> bool:
    return datetime.now().day == 1

def days_until_expiry(expiry_date: datetime) -> int:
    delta = expiry_date - datetime.now()
    return max(0, delta.days)

def format_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
```

```python
# test_billing.py
from datetime import datetime
from unittest.mock import patch
from billing import is_billing_day, days_until_expiry, format_timestamp

def test_is_billing_day_true():
    fixed_time = datetime(2025, 1, 1, 12, 0, 0)
    with patch("billing.datetime") as mock_dt:
        mock_dt.now.return_value = fixed_time
        assert is_billing_day() is True

def test_is_billing_day_false():
    fixed_time = datetime(2025, 1, 15, 12, 0, 0)
    with patch("billing.datetime") as mock_dt:
        mock_dt.now.return_value = fixed_time
        assert is_billing_day() is False

def test_days_until_expiry():
    now = datetime(2025, 1, 1, 12, 0, 0)
    expiry = datetime(2025, 1, 11, 12, 0, 0)
    with patch("billing.datetime") as mock_dt:
        mock_dt.now.return_value = now
        assert days_until_expiry(expiry) == 10
```

### Step 5: Using freezegun

```bash
pip install freezegun
```

```python
# test_billing_freezegun.py
from freezegun import freeze_time
from billing import is_billing_day, format_timestamp

@freeze_time("2025-01-01 12:00:00")
def test_billing_day_with_freezegun():
    assert is_billing_day() is True

@freeze_time("2025-03-15 14:30:00")
def test_format_with_freezegun():
    assert format_timestamp() == "2025-03-15 14:30:00"

@freeze_time("2025-01-15")
def test_not_billing_day():
    assert is_billing_day() is False
```

## What to Notice in This Code

- `tmp_path` returns a `pathlib.Path` object, so you build paths with the `/` operator
- `monkeypatch.delenv` explicitly tests the "variable not set" scenario
- `freeze_time` is a single decorator that's more concise than manual mock patching
- Each test runs independently with no environment contamination

## Common Mistakes

| Mistake | Why It's a Problem | Fix |
|---------|-------------------|-----|
| Creating files at absolute paths | Fails on different systems, collides between tests | Always use `tmp_path` |
| Setting env vars directly on `os.environ` | Leaks state to other tests if not restored | Use `monkeypatch.setenv` |
| Comparing `datetime.now()` directly | Results vary by execution time | Inject time or use freezegun |
| Manually cleaning up tmp_path contents | Unnecessary since pytest auto-cleans | Remove cleanup code |
| Ignoring timezones | UTC vs. local time differences cause failures | Always specify UTC or use timezone-aware datetimes |

## Practical Applications

- Create log files in `tmp_path` and verify log formats
- Batch-test environment variable combinations with parametrize and monkeypatch
- Test expiration logic at past, present, and future times with freezegun
- Use `tmp_path` in CI to avoid file permission differences across environments
- Test batch job scheduling logic with frozen time

## How Practitioners Think About This

Files, environment variables, and time are "the world outside your code." If you don't control that world in tests, your results are determined by the environment, not the code.

`tmp_path` is one of pytest's most useful built-in fixtures. Make it your starting point for every file I/O test.

## Checklist

- [ ] Created temporary files with `tmp_path` and used them in tests
- [ ] Isolated environment variables with `monkeypatch.setenv/delenv`
- [ ] Froze time with `unittest.mock.patch` or `freezegun`
- [ ] Tested error handling for missing files
- [ ] Confirmed no state contamination between tests

## Exercises

1. Create a YAML config file in `tmp_path` and write a test that parses it.
2. Test a function that outputs JSON or text logs depending on a `LOG_FORMAT` environment variable.
3. Combine `freeze_time` with parametrize to test the 1st, 15th, and last day of a month.

## Summary and Next

With tmp_path, monkeypatch, and freezegun, you can isolate system resources for stable, reproducible tests. Next, we'll learn how to measure coverage and evaluate test quality.

<!-- toc:begin -->
- [Why Write Tests?](./01-why-write-tests.md)
- [Writing Your First pytest Test](./02-first-pytest-test.md)
- [Assert and Exception Testing](./03-assert-and-exceptions.md)
- [Understanding Fixtures](./04-fixtures.md)
- [Parametrization](./05-parametrization.md)
- [Mock and Monkeypatch](./06-mock-and-monkeypatch.md)
- **Testing Files, Environment Variables, and Time (current)**
- Coverage and Test Quality (upcoming)
- Test Automation with GitHub Actions (upcoming)
- Writing Testable Code (upcoming)
<!-- toc:end -->

## References

- [pytest — tmp_path](https://docs.pytest.org/en/stable/how-to/tmp_path.html)
- [pytest — monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)
- [freezegun — GitHub](https://github.com/spulec/freezegun)
- [Real Python — Testing with tmp_path](https://realpython.com/pytest-python-testing/#tmp-path)

Tags: Python, pytest, tmp_path, freezegun, System Resource Testing
