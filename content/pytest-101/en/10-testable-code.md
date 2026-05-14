---
episode: 10
language: en
last_reviewed: '2026-05-04'
seo_description: Design testable code with dependency injection, pure functions, and
  clear seams so pytest can verify behavior without fragile setup.
series: pytest-101
status: content-ready
tags:
- Python
- pytest
- Testable Code
- Dependency Injection
- Software Design
targets:
  ebook: true
  hashnode: true
  medium: true
  mkdocs: true
  tistory: true
title: Writing Testable Code
---

# Writing Testable Code

This is the final post in the pytest 101 series.

> pytest 101 series (10/10)

<!-- a-grade-intro:begin -->

**Key Question**: Why is some code easy to test while other code needs 10 mocks?

> Hard-to-test code is almost always a design problem. Applying dependency injection, pure functions, and separation of concerns produces code you can test without mocks. This article covers design principles that improve testability.

<!-- a-grade-intro:end -->

## What You Will Learn

- Common patterns of hard-to-test code
- Separating external dependencies with dependency injection
- Isolating business logic with pure functions
- Narrowing test scope with separation of concerns

## Why It Matters

If a test needs more than 5 mocks, the problem isn't the test — it's the code. When a single function queries a database, calls an API, and sends an email, of course it's hard to test.

> "Hard to test" is feedback that says "improve the design." Tests drive design.

Code with high testability is flexible to change, easy to reuse, and fast to debug.

## Mental Model

> testable code = clear inputs + predictable outputs

```
[Hard to Test]                   [Easy to Test]
  DB call inside the function     DB passed as parameter
  Depends on global variables     Values passed as arguments
  Side effects hidden inside      Side effects separated out
  datetime.now() called directly  Time passed as parameter
```

## Core Concepts

| Term | Description |
|------|-------------|
| Dependency injection | Passing dependencies from outside so they can be swapped |
| Pure function | Always returns the same output for the same input, no side effects |
| Separation of concerns | Splitting business logic from infrastructure code |
| Testability | The degree to which code can be tested in isolation |
| Ports and adapters | Pattern separating business logic (ports) from external systems (adapters) |

## Before / After

Compare code with hard-coded dependencies versus injected dependencies.

```python
# before: dependencies hard-coded — untestable without mocks
import requests
from datetime import datetime

def create_order(user_id, items):
    user = db.query(f"SELECT * FROM users WHERE id = {user_id}")
    order_date = datetime.now()
    payment = requests.post("https://pay.api/charge", json={...})
    send_email(user["email"], "Order confirmed")
    return {"order_id": 1, "status": "completed"}
```

```python
# after: dependencies injected — testable without mocks
def create_order(user, items, now, charge_fn, notify_fn):
    total = sum(item["price"] * item["qty"] for item in items)
    payment = charge_fn(user["id"], total)
    if payment["status"] != "success":
        return {"status": "payment_failed"}
    notify_fn(user["email"], "Order confirmed")
    return {
        "order_id": payment["order_id"],
        "total": total,
        "date": now,
        "status": "completed",
    }
```

## Step-by-Step Practice

### Step 1: Isolate Business Logic with Pure Functions

```python
# pricing.py — pure functions: input → output, no side effects
def calculate_discount(total: float, membership: str) -> float:
    rates = {"gold": 0.15, "silver": 0.10, "bronze": 0.05}
    rate = rates.get(membership, 0.0)
    return round(total * rate, 2)

def calculate_shipping(total: float, country: str) -> float:
    if country == "KR":
        return 0.0 if total >= 50000 else 3000.0
    return 15000.0

def calculate_total(
    items: list[dict],
    membership: str,
    country: str,
) -> dict:
    subtotal = sum(item["price"] * item["qty"] for item in items)
    discount = calculate_discount(subtotal, membership)
    shipping = calculate_shipping(subtotal - discount, country)
    return {
        "subtotal": subtotal,
        "discount": discount,
        "shipping": shipping,
        "total": subtotal - discount + shipping,
    }
```

```python
# test_pricing.py — no mocks needed
from pricing import calculate_discount, calculate_shipping, calculate_total

def test_gold_discount():
    assert calculate_discount(100000, "gold") == 15000.0

def test_no_discount():
    assert calculate_discount(100000, "none") == 0.0

def test_free_shipping_kr():
    assert calculate_shipping(60000, "KR") == 0.0

def test_paid_shipping_kr():
    assert calculate_shipping(30000, "KR") == 3000.0

def test_total_calculation():
    items = [{"price": 10000, "qty": 3}, {"price": 5000, "qty": 2}]
    result = calculate_total(items, "silver", "KR")
    assert result["subtotal"] == 40000
    assert result["discount"] == 4000.0
    assert result["shipping"] == 3000.0
    assert result["total"] == 39000.0
```

### Step 2: Dependency Injection Pattern

```python
# user_service.py
from typing import Protocol

class UserRepository(Protocol):
    def find_by_id(self, user_id: int) -> dict | None: ...
    def save(self, user: dict) -> None: ...

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def get_user(self, user_id: int) -> dict:
        user = self.repo.find_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        return user

    def update_name(self, user_id: int, new_name: str) -> dict:
        user = self.get_user(user_id)
        user["name"] = new_name
        self.repo.save(user)
        return user
```

```python
# test_user_service.py
import pytest
from user_service import UserService

class FakeUserRepo:
    def __init__(self):
        self.users = {}
        self.saved = []

    def find_by_id(self, user_id):
        return self.users.get(user_id)

    def save(self, user):
        self.saved.append(user)

def test_get_user():
    repo = FakeUserRepo()
    repo.users[1] = {"id": 1, "name": "Alice"}
    service = UserService(repo)

    user = service.get_user(1)
    assert user["name"] == "Alice"

def test_get_missing_user():
    repo = FakeUserRepo()
    service = UserService(repo)

    with pytest.raises(ValueError, match="not found"):
        service.get_user(999)

def test_update_name():
    repo = FakeUserRepo()
    repo.users[1] = {"id": 1, "name": "Alice"}
    service = UserService(repo)

    updated = service.update_name(1, "Bob")
    assert updated["name"] == "Bob"
    assert len(repo.saved) == 1
```

### Step 3: Separation of Concerns

```python
# report.py — separate data processing from output
def aggregate_sales(transactions: list[dict]) -> dict:
    """Pure function: handles data aggregation only."""
    total = sum(t["amount"] for t in transactions)
    count = len(transactions)
    avg = total / count if count > 0 else 0
    return {"total": total, "count": count, "average": round(avg, 2)}

def format_report(stats: dict) -> str:
    """Pure function: handles formatting only."""
    return (
        f"Sales Report\n"
        f"Total Sales: ${stats['total']:,.0f}\n"
        f"Transactions: {stats['count']}\n"
        f"Average: ${stats['average']:,.0f}"
    )

def save_report(content: str, filepath: str) -> None:
    """Infrastructure function: handles file I/O only."""
    with open(filepath, "w") as f:
        f.write(content)
```

```python
# test_report.py — test each concern independently
from report import aggregate_sales, format_report

def test_aggregate_sales():
    transactions = [
        {"amount": 10000},
        {"amount": 20000},
        {"amount": 30000},
    ]
    result = aggregate_sales(transactions)
    assert result == {"total": 60000, "count": 3, "average": 20000.0}

def test_aggregate_empty():
    result = aggregate_sales([])
    assert result == {"total": 0, "count": 0, "average": 0}

def test_format_report():
    stats = {"total": 60000, "count": 3, "average": 20000.0}
    report = format_report(stats)
    assert "$60,000" in report
    assert "3" in report
```

### Step 4: Separating Side Effects via Function Parameters

```python
# notification.py
from typing import Callable

def process_order(
    order: dict,
    save_fn: Callable[[dict], None],
    notify_fn: Callable[[str, str], None],
) -> dict:
    """Business logic only. Injected functions handle side effects."""
    if order["total"] <= 0:
        raise ValueError("Order total must be greater than 0")

    order["status"] = "confirmed"
    save_fn(order)
    notify_fn(order["email"], f"Order {order['id']} confirmed")
    return order
```

```python
# test_notification.py
import pytest
from notification import process_order

def test_process_order():
    saved = []
    notifications = []

    result = process_order(
        order={"id": 1, "total": 10000, "email": "a@test.com"},
        save_fn=lambda o: saved.append(o),
        notify_fn=lambda email, msg: notifications.append((email, msg)),
    )

    assert result["status"] == "confirmed"
    assert len(saved) == 1
    assert len(notifications) == 1
    assert notifications[0][0] == "a@test.com"

def test_invalid_order():
    with pytest.raises(ValueError, match="greater than 0"):
        process_order(
            order={"id": 1, "total": 0, "email": "a@test.com"},
            save_fn=lambda o: None,
            notify_fn=lambda e, m: None,
        )
```

### Step 5: Before and After Refactoring

```python
# before refactoring: needs 5 mocks
# def test_create_order():
#     with patch("module.db") as mock_db, \
#          patch("module.requests") as mock_req, \
#          patch("module.send_email") as mock_email, \
#          patch("module.datetime") as mock_dt, \
#          patch("module.logger") as mock_log:
#         ...  # 30 lines of setup

# after refactoring: zero mocks
def test_calculate_order_total():
    items = [{"price": 10000, "qty": 2}]
    total = calculate_total(items, "gold", "KR")
    assert total["total"] == 17000.0  # 20000 - 3000(15%) + 0(shipping)
```

## What to Notice in This Code

- Pure functions only need input/output verification, keeping tests concise
- Protocol-based dependency injection makes Fake implementations easy to build
- Separation of concerns lets you test data processing, formatting, and I/O independently
- Injecting side effects as function parameters enables testing with simple lambdas

## Common Mistakes

| Mistake | Why It's a Problem | Fix |
|---------|-------------------|-----|
| Mixing business logic and I/O in one function | Can't test without mocks | Separate logic from I/O |
| Depending directly on global objects | State leaks between tests | Inject dependencies as parameters |
| Overusing mocks | Tests couple to implementation details | Improve design to reduce mock needs |
| Refusing to change code for testability | Testability is a sign of good design | Let tests drive the design |
| Making everything a class | Unnecessary state complicates tests | Prefer pure functions when possible |

## Practical Applications

- Write business logic as pure functions for fast domain tests
- Use the Repository pattern to isolate DB access with Fake implementations
- Leverage FastAPI's Depends for injection, overriding in tests
- Separate event handlers so publishing and processing are tested independently
- When refactoring legacy code, aim for "testable structure" as the goal

## How Practitioners Think About This

When facing hard-to-test code, experienced developers ask "how do I change the design?" not "how do I mock this?" Mocking is a temporary workaround; good design is the permanent fix.

The real value of TDD isn't "writing tests first" — it's "forcing testable design."

## Checklist

- [ ] Separated business logic into pure functions
- [ ] Made external dependencies swappable with dependency injection
- [ ] Defined interfaces with Protocol and created Fakes
- [ ] Tested each layer independently through separation of concerns
- [ ] Tested core business logic without any mocks

## Exercises

1. Refactor a function that directly queries a DB into a Repository pattern and test it with a Fake Repository.
2. Change a function that calls `datetime.now()` to accept a time parameter and test it with a fixed time.
3. Split a read-file → process-data → write-file function into 3 pure functions and test each independently.

## Summary and Series Wrap-Up

This series covered pytest from the basics to testable design. Tests aren't just "tools for verifying code works" — they're a "feedback loop that drives good design." Think about testing first, and good code follows naturally.

<!-- toc:begin -->
- [Why Write Tests?](./01-why-write-tests.md)
- [Writing Your First pytest Test](./02-first-pytest-test.md)
- [Assert and Exception Testing](./03-assert-and-exceptions.md)
- [Understanding Fixtures](./04-fixtures.md)
- [Parametrization](./05-parametrization.md)
- [Mock and Monkeypatch](./06-mock-and-monkeypatch.md)
- [Testing Files, Environment Variables, and Time](./07-testing-files-env-time.md)
- [Coverage and Test Quality](./08-coverage.md)
- [Test Automation with GitHub Actions](./09-ci-with-github-actions.md)
- **Writing Testable Code (current)**
<!-- toc:end -->

## References

- [Clean Architecture — Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [pytest — Documentation](https://docs.pytest.org/)
- [Cosmic Python — Architecture Patterns with Python](https://www.cosmicpython.com/)
- [Martin Fowler — Dependency Injection](https://martinfowler.com/articles/injection.html)

Tags: Python, pytest, Testable Code, Dependency Injection, Software Design