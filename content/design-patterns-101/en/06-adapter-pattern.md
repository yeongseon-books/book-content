---
series: design-patterns-101
episode: 6
title: "Design Patterns 101 (6/10): The Adapter Pattern"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - DesignPatterns
  - Adapter
  - Structural
  - Compatibility
  - Wrapper
seo_description: How the Adapter pattern protects domain boundaries by translating external interfaces into contracts the application can own.
last_reviewed: '2026-05-23'
---

# Design Patterns 101 (6/10): The Adapter Pattern

The day comes when a payment SDK has to be replaced. I have been through this three times. The first was swapping Stripe for Toss Payments. The second was moving email delivery from SES to SendGrid. The third was when an internal auth server migrated to the OAuth2 standard. All three left the same lesson: when an external SDK's signatures are scattered across domain code, replacing the SDK is not "swap one library" but "refactor the entire service."

This is the 6th post in the Design Patterns 101 series. Article 3 introduced Adapter at overview level, so here we dig into the boundaries Adapter creates in production and the costs those boundaries carry.

![Design Patterns 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/06/06-01-concept-at-a-glance.en.png)
*How an external SDK call passes through the Adapter boundary to reach the domain*
> The Adapter pattern keeps you from rewriting either side of a mismatched interface; it slips a thin translator between two contracts that almost — but not quite — agree.

## Questions to Keep in Mind

- What dependency, exactly, does an Adapter cut?
- Are Anti-Corruption Layer and Adapter the same thing or different things?
- What costs accumulate when Adapters multiply?

## Wrapping an External SDK into the Shape the Domain Wants

The core of Adapter fits in one sentence: **prevent the domain from learning the external SDK's language.** The domain only knows the Protocol it defined; the SDK's method names, exception types, and response structures stay locked inside the Adapter.

Here is an example wrapping the Stripe SDK.

```python
from dataclasses import dataclass
from typing import Protocol


class PaymentGateway(Protocol):
    """Contract the domain defines for payments."""

    def charge(self, customer_id: str, amount_krw: int) -> str:
        """Execute a charge and return a transaction ID."""
        ...

    def refund(self, transaction_id: str) -> None: ...


@dataclass
class StripeAdapter:
    """Translates the Stripe SDK into the PaymentGateway contract."""

    api_key: str

    def charge(self, customer_id: str, amount_krw: int) -> str:
        import stripe

        stripe.api_key = self.api_key
        intent = stripe.PaymentIntent.create(
            amount=amount_krw,
            currency="krw",
            customer=customer_id,
            confirm=True,
        )
        return intent.id

    def refund(self, transaction_id: str) -> None:
        import stripe

        stripe.api_key = self.api_key
        stripe.Refund.create(payment_intent=transaction_id)
```

The domain service sees only `PaymentGateway`.

```python
def process_order(gateway: PaymentGateway, customer_id: str, total: int) -> str:
    tx_id = gateway.charge(customer_id, total)
    # update order status, emit events, etc.
    return tx_id
```

When Stripe is replaced by Toss Payments, `process_order` does not change by a single character. Create a new `TossAdapter`, inject it, done. That is the most practical value Adapter delivers.

## The Dependency That Gets Cut

Without an Adapter the dependency graph looks like this:

```text
[OrderService] -> [stripe package]
[RefundService] -> [stripe package]
[WebhookHandler] -> [stripe package]
```

Three modules all import `stripe` directly. When Stripe ships a major version bump, all three must be patched simultaneously.

With an Adapter the graph changes:

```text
[OrderService] -> [PaymentGateway (Protocol)]
[RefundService] -> [PaymentGateway (Protocol)]
[WebhookHandler] -> [PaymentGateway (Protocol)]
                         ^
                   [StripeAdapter] -> [stripe package]
```

Only one module depends on the `stripe` package now. The blast radius of any change converges to a single Adapter file. Testing becomes natural too. There is no reason for an `OrderService` unit test to hit Stripe's servers; plug in an in-memory implementation instead.

```python
@dataclass
class FakePaymentGateway:
    charged: list[tuple[str, int]] = None

    def __post_init__(self) -> None:
        self.charged = self.charged or []

    def charge(self, customer_id: str, amount_krw: int) -> str:
        tx_id = f"fake-{len(self.charged)}"
        self.charged.append((customer_id, amount_krw))
        return tx_id

    def refund(self, transaction_id: str) -> None:
        pass
```

## Adapter as Anti-Corruption Layer

In Domain-Driven Design the Anti-Corruption Layer (ACL) is a translation tier that prevents an external bounded context's model from polluting the internal domain. Adapter is the most common vehicle for implementing an ACL.

Suppose an external payment API returns this response:

```python
# External API response (structure we do not control)
external_response = {
    "txn_ref": "TXN-9912",
    "amt": 50000,
    "ccy": "KRW",
    "sts": "OK",
    "ts": "2026-05-23T10:00:00Z",
}
```

If domain code parses this structure directly in multiple places, the moment the external API renames a field the entire domain shakes. An ACL Adapter handles the translation in one place.

```python
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PaymentResult:
    """Payment result the domain understands."""

    transaction_id: str
    amount: int
    currency: str
    success: bool
    completed_at: datetime


class ExternalPaymentAdapter:
    """Translates external payment API responses into domain models."""

    def translate(self, raw: dict) -> PaymentResult:
        return PaymentResult(
            transaction_id=raw["txn_ref"],
            amount=raw["amt"],
            currency=raw["ccy"],
            success=raw["sts"] == "OK",
            completed_at=datetime.fromisoformat(raw["ts"]),
        )
```

The difference between ACL and a plain Adapter lies in intent. A plain Adapter focuses on matching signatures. An ACL prevents **the external model's concepts themselves** from leaking inward. Reinterpreting `sts` as `success: bool` is the essence of ACL.

## Adapter vs Facade vs Wrapper

These three terms are frequently conflated. Here is the difference in code.

**Adapter**: translates one interface into another. A contract the caller expects already exists, and the external implementation does not match it.

```python
class NotificationSender(Protocol):
    def send(self, recipient: str, body: str) -> None: ...

class SlackWebhookAdapter:
    """Translates the Slack webhook API into the NotificationSender contract."""

    def __init__(self, webhook_url: str) -> None:
        self._url = webhook_url

    def send(self, recipient: str, body: str) -> None:
        import httpx

        httpx.post(self._url, json={"channel": recipient, "text": body})
```

**Facade**: hides multiple subsystems behind a single simplified entry point. No pre-existing contract; the goal is to simplify a complex combination.

```python
class DeployFacade:
    """Single entry point that runs build + test + deploy."""

    def __init__(self, builder, tester, deployer) -> None:
        self._builder = builder
        self._tester = tester
        self._deployer = deployer

    def release(self, version: str) -> None:
        artifact = self._builder.build(version)
        self._tester.run_all(artifact)
        self._deployer.push(artifact)
```

**Wrapper**: not a pattern name but a general term. Adapter is a Wrapper; Decorator is also a Wrapper. It describes the act of wrapping without distinguishing structural intent.

Summary:

| Term | Purpose | Target |
| --- | --- | --- |
| Adapter | Translate to match an existing contract | One interface |
| Facade | Simplify complex subsystems | Multiple subsystems |
| Wrapper | General term (the act of wrapping) | No specific structure |

## Why Class Adapter via Multiple Inheritance Is Wrong in Python

The GoF book splits Adapter into two variants: Object Adapter (composition) and Class Adapter (multiple inheritance). In C++ the Class Adapter was a natural choice, but in Python the Object Adapter wins almost every time.

Forcing a Class Adapter in Python looks like this:

```python
class LegacyPrinter:
    def print_old(self, text: str) -> None:
        print(f"[LEGACY] {text}")


class Printer(Protocol):
    def print_text(self, text: str) -> None: ...


class PrinterClassAdapter(LegacyPrinter):
    """Adapts LegacyPrinter to the Printer contract via inheritance."""

    def print_text(self, text: str) -> None:
        self.print_old(text)
```

Three problems arise:

1. **Every public method of LegacyPrinter is exposed.** External code can call `print_old` directly, breaking encapsulation.
2. **Changes to LegacyPrinter break the Adapter.** Inheritance couples to the parent's internal implementation.
3. **Multiple inheritance triggers MRO conflicts.** Inheriting from two or more Adaptees simultaneously makes debugging extremely painful.

Object Adapter avoids all of these:

```python
@dataclass
class PrinterObjectAdapter:
    """Wraps LegacyPrinter via composition."""

    _legacy: LegacyPrinter

    def print_text(self, text: str) -> None:
        self._legacy.print_old(text)
```

`_legacy` is private; there is no path for external code to call `print_old` directly. I have never chosen Class Adapter in a Python project. Composition is always safer and more flexible.

## API Version Migration

When migrating from API v1 to v2, flipping all clients at once is unrealistic. Adapter serves as a compatibility layer that preserves the v1 interface while internally calling v2.

```python
from dataclasses import dataclass


@dataclass
class UserV1:
    """User model the v1 API returned."""

    id: int
    name: str
    email: str


@dataclass
class UserV2:
    """v2 user model with split fields."""

    user_id: str  # changed to UUID
    display_name: str
    contact: dict  # {"email": ..., "phone": ...}


class UserServiceV1Protocol(Protocol):
    def get_user(self, user_id: int) -> UserV1: ...


class V1ToV2Adapter:
    """Maintains the v1 contract while internally calling the v2 service."""

    def __init__(self, v2_client) -> None:
        self._v2 = v2_client

    def get_user(self, user_id: int) -> UserV1:
        v2_user: UserV2 = self._v2.get_user_by_legacy_id(user_id)
        return UserV1(
            id=user_id,
            name=v2_user.display_name,
            email=v2_user.contact["email"],
        )
```

v1 clients keep calling the old interface without knowing anything changed. Internally the v2 service is already running. Once every client has migrated to v2, remove the Adapter. Adapter is not necessarily a permanent structure; it can serve as a **temporary translation layer that exists only during migration**.

## Adapter at the Test Boundary

The boundary Adapter creates has a direct impact on test strategy. I split tests into three tiers:

1. **Domain unit tests**: inject a Fake Adapter. No network calls, runs in milliseconds.
2. **Adapter integration tests**: hit the real external service (or its sandbox). Slow, but verifies the translation logic is correct.
3. **E2E tests**: cut through the entire system.

This separation is possible because Adapter provides a clear seam. Without it, domain code calls the SDK directly and unit tests must rely on heavy mocking. Mocks replicate the external API's internal implementation inside test code, so when the API changes the mocks break too. With an Adapter the mock target becomes "a Protocol we defined," making tests stable regardless of external changes.

```python
def test_order_charges_correct_amount() -> None:
    gateway = FakePaymentGateway()
    tx_id = process_order(gateway, customer_id="cust-1", total=30000)

    assert tx_id == "fake-0"
    assert gateway.charged == [("cust-1", 30000)]
```

This test does not break whether Stripe ships v3 or the team switches to Toss.

## Two-Way Adapter

Most Adapters are unidirectional: external-to-internal or internal-to-external. During migration periods where a legacy system and a new system coexist, bidirectional translation may be necessary.

```python
from dataclasses import dataclass


@dataclass
class LegacyEvent:
    event_type: str  # "ORDER_CREATED"
    payload: str  # JSON string


@dataclass
class DomainEvent:
    name: str  # "order.created"
    data: dict


class BidirectionalEventAdapter:
    """Translates legacy events <-> domain events in both directions."""

    def to_domain(self, legacy: LegacyEvent) -> DomainEvent:
        import json

        return DomainEvent(
            name=legacy.event_type.lower().replace("_", "."),
            data=json.loads(legacy.payload),
        )

    def to_legacy(self, domain: DomainEvent) -> LegacyEvent:
        import json

        return LegacyEvent(
            event_type=domain.name.upper().replace(".", "_"),
            payload=json.dumps(domain.data),
        )
```

A bidirectional Adapter is convenient but dangerous. Translation rules must be consistent in both directions, and if one side cannot represent a concept the other can, information is lost. Whenever I use a bidirectional Adapter I always write a roundtrip test.

```python
def test_roundtrip() -> None:
    adapter = BidirectionalEventAdapter()
    original = DomainEvent(name="order.created", data={"id": 1})

    legacy = adapter.to_legacy(original)
    restored = adapter.to_domain(legacy)

    assert restored == original
```

A failing roundtrip test signals that information is being lost during translation.

## The Cost of Too Many Adapters

Adapters are not free. As they accumulate in a project the following costs pile up.

**Call paths get longer.** Domain -> Protocol -> Adapter -> SDK. When debugging, the stack trace has one more layer to unwind. During incidents, distinguishing "did this error come from the Adapter or the SDK?" takes time.

**Protocol mismatches can be hidden.** If the external SDK is async but the domain Protocol is defined as sync, the Adapter ends up calling `asyncio.run()` internally to paper over the mismatch. Such an Adapter works but becomes a performance bottleneck.

**Adapters themselves bloat.** If the external SDK exposes 20 methods but the domain uses 3, the Adapter should translate only 3. Wrapping all 20 "just in case" turns the Adapter into a mirror of the SDK. At that point any SDK change forces a full Adapter rewrite, and the boundary loses its meaning.

I manage Adapter cost with these heuristics:

- If a single Adapter translates more than 5 methods, I question whether the domain Protocol is too wide.
- If conditional branches appear inside an Adapter, business logic has leaked in and should be pulled back into the domain.
- If an Adapter calls another Adapter, boundaries are nesting and should be collapsed into one.

## Exception Translation Is the Adapter's Job

Letting an external SDK's exceptions bubble into the domain forces domain code to know the SDK's exception hierarchy. The Adapter must translate these into domain exceptions.

```python
class PaymentError(Exception):
    """Domain payment exception."""

    def __init__(self, message: str, retriable: bool = False) -> None:
        super().__init__(message)
        self.retriable = retriable


@dataclass
class StripeAdapterWithErrorTranslation:
    api_key: str

    def charge(self, customer_id: str, amount_krw: int) -> str:
        import stripe

        stripe.api_key = self.api_key
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount_krw,
                currency="krw",
                customer=customer_id,
                confirm=True,
            )
            return intent.id
        except stripe.error.CardError as e:
            raise PaymentError(str(e), retriable=False) from e
        except stripe.error.RateLimitError as e:
            raise PaymentError(str(e), retriable=True) from e
        except stripe.error.StripeError as e:
            raise PaymentError(f"Stripe internal error: {e}", retriable=True) from e
```

The domain only needs to know `PaymentError`. It checks the `retriable` flag to decide whether to retry, and Stripe's proprietary exception hierarchy never leaks past the Adapter.

## Answering the Opening Questions

- **What dependency, exactly, does an Adapter cut?**
  The direct import dependency from domain modules to the external SDK package. As the dependency graph in this article showed, before the Adapter three modules all depended on `stripe`; after, only the Adapter file does. The blast radius converges and a seam appears for injecting Fakes in tests.

- **Are Anti-Corruption Layer and Adapter the same thing or different things?**
  ACL is a strategic DDD concept; Adapter is a tactical means of implementing it. A plain Adapter matches signatures. An ACL Adapter prevents the external model's concepts from penetrating inward. The `ExternalPaymentAdapter` reinterpreting `sts` as `success: bool` illustrates the difference.

- **What costs accumulate when Adapters multiply?**
  Call paths lengthen and debugging time grows. Protocol mismatches can be hidden. Adapters bloat into SDK mirrors, erasing the boundary's value. I treat more than 5 translated methods, internal branching, and Adapter-to-Adapter calls as warning signals.

<!-- toc:begin -->
## Series Table of Contents

- [Design Patterns 101 (1/10): What Are Design Patterns?](./01-what-are-design-patterns.md)
- [Design Patterns 101 (2/10): Creational Patterns](./02-creational-patterns.md)
- [Design Patterns 101 (3/10): Structural Patterns](./03-structural-patterns.md)
- [Design Patterns 101 (4/10): Behavioral Patterns](./04-behavioral-patterns.md)
- [Design Patterns 101 (5/10): The Strategy Pattern](./05-strategy-pattern.md)
- **The Adapter Pattern (current)**
- The Observer Pattern (upcoming)
- Factory and Dependency Injection (upcoming)
- When Not to Use Patterns (upcoming)
- Patterns That Fit Python (upcoming)

<!-- toc:end -->

## References

### Core References

- [Adapter Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/adapter)
- [Hexagonal Architecture (Alistair Cockburn)](https://alistair.cockburn.us/hexagonal-architecture/)
- [Anti-Corruption Layer (Martin Fowler)](https://docs.microsoft.com/en-us/azure/architecture/patterns/anti-corruption-layer)

### Practical Extensions

- [PEP 544 — Protocols](https://peps.python.org/pep-0544/)
- [Domain-Driven Design (Eric Evans) — Chapter 14: Maintaining Model Integrity](https://www.domainlanguage.com/ddd/)
- [Example code for this series (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/en)

Tags: Computer Science, DesignPatterns, Adapter, Structural, Compatibility, Wrapper
