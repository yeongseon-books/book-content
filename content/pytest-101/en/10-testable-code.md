---
episode: 10
language: en
last_reviewed: '2026-05-17'
seo_description: Reduce mock-heavy tests by separating pure logic from side effects and injecting boundaries explicitly in Python code.
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
  tistory: false
title: "pytest 101 (10/10): Writing Testable Code"
---

# pytest 101 (10/10): Writing Testable Code

This is the final post in the pytest 101 series.

When testing feels painful, the problem is often not pytest. It is that one function is trying to calculate totals, call a payment API, write to storage, stamp the current time, and notify a user all at once. In this article, we'll make that pain concrete and then show how to redraw the boundary so the important rules become easy to verify.


![pytest 101 chapter 10 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/pytest-101/10/10-01-testable-code-boundary.en.png)
*pytest 101 chapter 10 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Writing Testable Code?
- Which signal should the example or diagram make visible for Writing Testable Code?
- What failure should be prevented first when Writing Testable Code reaches a real system?

## What This Article Covers

- Why some tests need a wall of patches before they can even reach the assertion
- Where dependency injection actually pays off in real Python code
- How pure functions, Protocols, and Fakes each reduce testing friction
- How to refactor legacy code toward fewer mocks and clearer business rules

## Why It Matters

"Hard to test" usually means "the boundaries are blurry." If one function reads from storage, calls an external API, checks the current time, and sends email, then of course the test needs a miniature universe of substitutes.

> More mocks do not automatically mean a more sophisticated test. Often they mean the code is tangled too tightly with the outside world.

Testable structure is not only about making tests pleasant. It also narrows failure causes, makes business rules easier to read, and reduces the blast radius of future changes.

## Mental Model

> Testable code has a pure core on the inside and replaceable side-effect boundaries on the outside.

```text
[Pure core]
  price calculation
  validation rules
  status transitions

[Boundary adapters]
  payment gateway
  repository
  notification sender
  clock / id factory
```

## Core Concepts

| Term | Description |
| --- | --- |
| Pure function | Returns the same result for the same input and has no hidden side effects |
| Dependency injection | Receives external collaborators from the outside so they can be swapped |
| Protocol | A type-level interface that describes the methods a collaborator must provide |
| Fake | A lightweight test implementation that stands in for a real dependency |
| Boundary | The place where business rules meet the outside world |

## Before / After

**Before — time, payment, persistence, and notification are fused together:**

```python
import requests
from datetime import datetime, timezone

def create_order(user: dict, items: list[dict]) -> dict:
    subtotal = sum(item["unit_price"] * item["quantity"] for item in items)
    payload = {
        "customer_id": user["payment_customer_id"],
        "amount": subtotal,
        "currency": "KRW",
        "requested_at": datetime.now(timezone.utc).isoformat(),
        "line_items": [
            {
                "sku": item["sku"],
                "quantity": item["quantity"],
                "unit_price": item["unit_price"],
            }
            for item in items
        ],
    }
    response = requests.post(
        "https://pay.example.com/v1/charges",
        json=payload,
        timeout=5,
    )
    response.raise_for_status()
    charge = response.json()
    save_order_to_db(user["id"], subtotal, charge["id"])
    send_email(user["email"], f"Order {charge['id']} completed.")
    return {
        "order_id": charge["id"],
        "status": charge["status"],
        "charged_amount": charge["amount"],
    }
```

**After — pure calculation and external collaboration are separated:**

```python
def build_charge_request(user: dict, items: list[dict], requested_at: str) -> dict:
    subtotal = sum(item["unit_price"] * item["quantity"] for item in items)
    return {
        "customer_id": user["payment_customer_id"],
        "amount": subtotal,
        "currency": "KRW",
        "requested_at": requested_at,
        "line_items": [
            {
                "sku": item["sku"],
                "quantity": item["quantity"],
                "unit_price": item["unit_price"],
            }
            for item in items
        ],
    }

def finalize_order(charge: dict) -> dict:
    return {
        "order_id": charge["id"],
        "status": charge["status"],
        "charged_amount": charge["amount"],
    }
```

The key change is not style. It is that the code now separates "what data should be produced" from "which external service receives it."

## Step-by-Step Practice

### Step 1: Pull pure logic into the center first

```python
# pricing.py
def calculate_subtotal(items: list[dict]) -> int:
    return sum(item["unit_price"] * item["quantity"] for item in items)

def membership_discount_rate(membership: str) -> float:
    rates = {"gold": 0.15, "silver": 0.10, "bronze": 0.05}
    return rates.get(membership, 0.0)

def calculate_discount(subtotal: int, membership: str) -> int:
    return int(subtotal * membership_discount_rate(membership))

def calculate_shipping(amount_after_discount: int, country: str) -> int:
    if country == "KR":
        return 0 if amount_after_discount >= 50000 else 3000
    return 15000

def calculate_order_totals(items: list[dict], membership: str, country: str) -> dict:
    subtotal = calculate_subtotal(items)
    discount = calculate_discount(subtotal, membership)
    shipping = calculate_shipping(subtotal - discount, country)
    total = subtotal - discount + shipping
    return {
        "subtotal": subtotal,
        "discount": discount,
        "shipping": shipping,
        "total": total,
    }
```

```python
# test_pricing.py
from pricing import calculate_order_totals, calculate_shipping, calculate_discount

def test_gold_discount():
    assert calculate_discount(100000, "gold") == 15000

def test_shipping_for_small_domestic_order():
    assert calculate_shipping(42000, "KR") == 3000

def test_order_totals_for_silver_member():
    items = [
        {"sku": "keyboard", "unit_price": 30000, "quantity": 1},
        {"sku": "switch-pack", "unit_price": 5000, "quantity": 2},
    ]
    result = calculate_order_totals(items, membership="silver", country="KR")

    assert result == {
        "subtotal": 40000,
        "discount": 4000,
        "shipping": 3000,
        "total": 39000,
    }
```

There is no network, no database, and no current time here. That is why the tests stay short and the failures stay obvious.

### Step 2: Split external collaborators behind Protocols and Fakes

```python
# order_service.py
from typing import Protocol

class PaymentGateway(Protocol):
    def charge(self, payload: dict) -> dict:
        pass

class OrderRepository(Protocol):
    def save(self, order: dict) -> dict:
        pass

class Notifier(Protocol):
    def send(self, email: str, message: str) -> None:
        pass

class OrderService:
    def __init__(
        self,
        gateway: PaymentGateway,
        repository: OrderRepository,
        notifier: Notifier,
    ):
        self.gateway = gateway
        self.repository = repository
        self.notifier = notifier

    def create(self, user: dict, payload: dict) -> dict:
        charge = self.gateway.charge(payload)
        order = {
            "user_id": user["id"],
            "email": user["email"],
            "charge_id": charge["id"],
            "status": charge["status"],
            "charged_amount": charge["amount"],
        }
        saved = self.repository.save(order)
        self.notifier.send(user["email"], f"Order {saved['charge_id']} completed.")
        return saved
```

```python
# test_order_service.py
from order_service import OrderService

class FakeGateway:
    def __init__(self):
        self.payloads = []

    def charge(self, payload: dict) -> dict:
        self.payloads.append(payload)
        return {
            "id": "ch_1001",
            "status": "paid",
            "amount": payload["amount"],
        }

class FakeRepository:
    def __init__(self):
        self.saved_orders = []

    def save(self, order: dict) -> dict:
        persisted = {**order, "id": 101}
        self.saved_orders.append(persisted)
        return persisted

class FakeNotifier:
    def __init__(self):
        self.messages = []

    def send(self, email: str, message: str) -> None:
        self.messages.append((email, message))

def test_create_order_with_fakes():
    service = OrderService(FakeGateway(), FakeRepository(), FakeNotifier())
    user = {"id": 7, "email": "buyer@example.com"}
    payload = {
        "customer_id": "cus_777",
        "amount": 39000,
        "currency": "KRW",
        "requested_at": "2026-05-17T09:00:00+00:00",
        "line_items": [
            {"sku": "keyboard", "quantity": 1, "unit_price": 30000},
            {"sku": "switch-pack", "quantity": 2, "unit_price": 5000},
        ],
    }

    result = service.create(user, payload)

    assert result["id"] == 101
    assert result["charge_id"] == "ch_1001"
    assert result["charged_amount"] == 39000
```

The Protocol shows the contract. The Fake shows how the contract behaves in tests. Together they let you verify collaboration without a mocking framework wall.

### Step 3: Make request assembly explicit and testable

```python
# checkout.py
def build_charge_request(user: dict, items: list[dict], requested_at: str) -> dict:
    subtotal = sum(item["unit_price"] * item["quantity"] for item in items)
    return {
        "customer_id": user["payment_customer_id"],
        "amount": subtotal,
        "currency": "KRW",
        "requested_at": requested_at,
        "line_items": [
            {
                "sku": item["sku"],
                "quantity": item["quantity"],
                "unit_price": item["unit_price"],
            }
            for item in items
        ],
    }

def present_checkout_result(charge: dict) -> dict:
    return {
        "order_id": charge["id"],
        "status": charge["status"],
        "charged_amount": charge["amount"],
    }
```

```python
# test_checkout.py
from checkout import build_charge_request, present_checkout_result

def test_build_charge_request_uses_explicit_fields():
    payload = build_charge_request(
        user={"payment_customer_id": "cus_777"},
        items=[
            {"sku": "keyboard", "unit_price": 30000, "quantity": 1},
            {"sku": "switch-pack", "unit_price": 5000, "quantity": 2},
        ],
        requested_at="2026-05-17T09:00:00+00:00",
    )

    assert payload == {
        "customer_id": "cus_777",
        "amount": 40000,
        "currency": "KRW",
        "requested_at": "2026-05-17T09:00:00+00:00",
        "line_items": [
            {"sku": "keyboard", "quantity": 1, "unit_price": 30000},
            {"sku": "switch-pack", "quantity": 2, "unit_price": 5000},
        ],
    }

def test_present_checkout_result():
    charge = {"id": "ch_1001", "status": "paid", "amount": 40000}
    assert present_checkout_result(charge) == {
        "order_id": "ch_1001",
        "status": "paid",
        "charged_amount": 40000,
    }
```

Once the payload is its own function, your docs and tests stop hiding behind placeholders like `json={...}`. The exact fields become visible and verifiable.

### Step 4: Move time and ID generation outside the function

```python
from collections.abc import Callable

from pricing import calculate_order_totals

def create_checkout_payload(
    user: dict,
    items: list[dict],
    now_iso: str,
    order_id_factory: Callable[[], str],
) -> dict:
    totals = calculate_order_totals(items, membership=user["membership"], country=user["country"])
    return {
        "order_id": order_id_factory(),
        "customer_id": user["payment_customer_id"],
        "requested_at": now_iso,
        "amount": totals["total"],
        "currency": "KRW",
        "line_items": items,
    }
```

```python
from checkout import create_checkout_payload

def test_create_checkout_payload_with_fixed_clock_and_id():
    user = {
        "membership": "gold",
        "country": "KR",
        "payment_customer_id": "cus_777",
    }
    items = [{"sku": "keyboard", "unit_price": 30000, "quantity": 2}]

    payload = create_checkout_payload(
        user=user,
        items=items,
        now_iso="2026-05-17T09:00:00+00:00",
        order_id_factory=lambda: "order_9001",
    )

    assert payload["order_id"] == "order_9001"
    assert payload["requested_at"] == "2026-05-17T09:00:00+00:00"
    assert payload["amount"] == 51000
```

Direct `datetime.now()` and `uuid4()` calls make tests depend on moving time and randomness. Passing time and ID generation in from the outside makes the test deterministic immediately.

### Step 5: Compare the patch wall with the refactored version

First, here is a realistic pre-refactor function and test.

```python
# before_checkout.py
import requests
from datetime import datetime, timezone

from mailer import send_email
from repository import save_order_to_db

def checkout(user: dict, items: list[dict]) -> dict:
    subtotal = sum(item["unit_price"] * item["quantity"] for item in items)
    response = requests.post(
        "https://pay.example.com/v1/charges",
        json={
            "customer_id": user["payment_customer_id"],
            "amount": subtotal,
            "currency": "KRW",
            "requested_at": datetime.now(timezone.utc).isoformat(),
        },
        timeout=5,
    )
    response.raise_for_status()
    charge = response.json()
    save_order_to_db(user["id"], subtotal, charge["id"])
    send_email(user["email"], f"Order {charge['id']} completed.")
    return {"order_id": charge["id"], "status": charge["status"]}
```

```python
# test_before_checkout.py
from datetime import datetime, timezone
from unittest.mock import patch

from before_checkout import checkout

@patch("before_checkout.send_email")
@patch("before_checkout.save_order_to_db")
@patch("before_checkout.requests.post")
@patch("before_checkout.datetime")
def test_checkout_before(mock_datetime, mock_post, mock_save, mock_email):
    mock_datetime.now.return_value = datetime(2026, 5, 17, 9, 0, tzinfo=timezone.utc)
    mock_post.return_value.raise_for_status.return_value = None
    mock_post.return_value.json.return_value = {
        "id": "ch_1001",
        "status": "paid",
        "amount": 40000,
    }

    result = checkout(
        user={"id": 7, "email": "buyer@example.com", "payment_customer_id": "cus_777"},
        items=[
            {"sku": "keyboard", "unit_price": 30000, "quantity": 1},
            {"sku": "switch-pack", "unit_price": 5000, "quantity": 2},
        ],
    )

    assert result == {"order_id": "ch_1001", "status": "paid"}
    mock_save.assert_called_once()
    mock_email.assert_called_once()
```

Most of that test is setup for the environment, not verification of business rules.

Now compare it to a refactored version that keeps the core logic pure.

```python
# after_checkout.py
from collections.abc import Callable

from checkout import create_checkout_payload

def plan_checkout(user: dict, items: list[dict], now_iso: str, order_id_factory: Callable[[], str]) -> dict:
    payload = create_checkout_payload(user, items, now_iso=now_iso, order_id_factory=order_id_factory)
    return {
        "order_id": payload["order_id"],
        "charge_request": payload,
        "email": user["email"],
    }

def complete_checkout(plan: dict, charge: dict) -> dict:
    return {
        "order_id": plan["order_id"],
        "status": charge["status"],
        "charged_amount": charge["amount"],
        "email": plan["email"],
    }
```

```python
# test_after_checkout.py
from after_checkout import complete_checkout, plan_checkout

def test_checkout_after_refactoring():
    user = {
        "email": "buyer@example.com",
        "membership": "silver",
        "country": "KR",
        "payment_customer_id": "cus_777",
    }
    items = [
        {"sku": "keyboard", "unit_price": 30000, "quantity": 1},
        {"sku": "switch-pack", "unit_price": 5000, "quantity": 2},
    ]

    plan = plan_checkout(
        user=user,
        items=items,
        now_iso="2026-05-17T09:00:00+00:00",
        order_id_factory=lambda: "order_9001",
    )
    result = complete_checkout(
        plan,
        charge={"id": "ch_1001", "status": "paid", "amount": 39000},
    )

    assert plan["charge_request"]["amount"] == 39000
    assert result == {
        "order_id": "order_9001",
        "status": "paid",
        "charged_amount": 39000,
        "email": "buyer@example.com",
    }
```

No network patching. No database patching. No time patching. The business rule is finally the main character of the test.

## What to Notice in This Code

- Pure calculation functions make intent visible because the tests only talk about inputs and outputs.
- Protocols plus Fakes shift collaborator tests away from patch mechanics and toward behavior.
- Explicit payload-building functions document external API contracts in both code and tests.
- Injected time and ID generation make the workflow deterministic and reproducible.

## Common Mistakes

| Mistake | Why It's a Problem | Fix |
| --- | --- | --- |
| Mixing business rules and external calls in one function | Tests become tied to network, storage, and time at once | Split calculation from I/O boundaries first |
| Leaving Protocol examples as `...` placeholders | Readers cannot copy and run the example immediately | Use concrete method names and at least `pass` bodies |
| Hiding payload examples behind `json={...}` | The important verification surface stays vague | Show the exact fields explicitly |
| Only trying to reduce patch count without moving logic inward | The design problem remains | Move more rules into the pure core |
| Turning every boundary into a class automatically | Unnecessary state can reintroduce complexity | Keep functions when state is not needed |

## Practical Applications

- Keep service-layer business rules pure in FastAPI applications and inject sessions or clients at the boundary.
- Wrap payment, email, and queue integrations in adapters so unit tests can use Fakes.
- Treat legacy refactoring as a boundary-redrawing exercise, not just a coverage exercise.
- Use integration tests for the outer adapters and fast unit tests for the inner rules.

## How Practitioners Think About This

Experienced developers usually do not respond to painful tests by looking for more pytest tricks first. They ask whether the function is doing too many jobs. The test pain is often a design signal.

Good refactoring does more than reduce mock counts. It leaves business rules at the center and makes the external edges replaceable.

## Checklist

- [ ] Separated pure calculation from external collaboration
- [ ] Exposed collaborator contracts with Protocols or equivalent interfaces
- [ ] Wrote a core service test with Fakes instead of a patch wall
- [ ] Made time, IDs, and API payloads deterministic to verify
- [ ] Replaced a pre-refactor mock-heavy test with a rule-focused refactored test

## Exercises

1. Wrap a direct `requests.post()` call in a `PaymentGateway` adapter and test it with a `FakeGateway`.
2. Pick an existing function that calls `datetime.now()` directly and refactor it to accept time as an argument.
3. Find one test in your codebase that needs 3 or more patches and write down which boundary you would separate first.

## Summary and Series Wrap-Up

Using pytest well and writing testable code are not separate skills. Once you move pure rules inward and push external dependencies to the boundary, tests become shorter and design becomes clearer at the same time. That is the closing idea of this series: good tests do not just verify good code — they also keep pushing the code toward better structure.

## Answering the Opening Questions

- **Why do some functions need multiple patches and mocks for a single test?**
  - When one function like `before_checkout.checkout()` calls `requests.post`, `datetime.now()`, `save_order_to_db`, and `send_email` all at once, the test must prepare that many patches. The four-patch example in the article signals not a testing-skill deficit but a design where business rules and side-effect boundaries are lumped together.
- **At which points should dependency injection be applied to actually simplify tests?**
  - Boundaries where time is `now_iso`, IDs come from `order_id_factory`, and external integrations are `gateway`, `repository`, `notifier`—injecting via arguments or constructors at these points shortens tests. So `create_checkout_payload()` and `plan_checkout()` need only verify pure dict inputs and outputs, locking core rules without time patches or network mocks.
- **What roles should pure functions, Protocols, and Fake objects each take?**
  - Pure functions handle computation and assembly rules like `calculate_order_totals`, `build_charge_request`, and `present_checkout_result`. Protocols expose collaborator contracts like `PaymentGateway`, `OrderRepository`, and `Notifier`. FakeGateway, FakeRepository, and FakeNotifier lightly mimic those contracts within tests, focusing on stored state and result values rather than mock call verification.
<!-- toc:begin -->
## In this series

- [pytest 101 (1/10): Why Write Tests?](./01-why-write-tests.md)
- [pytest 101 (2/10): Writing Your First pytest Test](./02-first-pytest-test.md)
- [pytest 101 (3/10): Assert and Exception Testing](./03-assert-and-exceptions.md)
- [pytest 101 (4/10): Understanding Fixtures](./04-fixtures.md)
- [pytest 101 (5/10): Parametrization](./05-parametrization.md)
- [pytest 101 (6/10): Mock and Monkeypatch](./06-mock-and-monkeypatch.md)
- [pytest 101 (7/10): Testing Files, Environment Variables, and Time](./07-testing-files-env-time.md)
- [pytest 101 (8/10): Coverage and Test Quality](./08-coverage.md)
- [pytest 101 (9/10): Test Automation with GitHub Actions](./09-ci-with-github-actions.md)
- **Writing Testable Code (current)**

<!-- toc:end -->

## References

- [pytest Good Integration Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html)
- [pytest How to use fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [unittest.mock — mock object library](https://docs.python.org/3/library/unittest.mock.html)
- [Martin Fowler — Dependency Injection](https://martinfowler.com/articles/injection.html)
- [Brian Okken — pytest for maintainable tests](https://pythontest.com/pytest-book/)

Tags: Python, pytest, Testable Code, Dependency Injection, Software Design
