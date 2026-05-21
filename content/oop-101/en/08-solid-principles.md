---
series: oop-101
episode: 8
title: "Object-Oriented Programming 101 (8/10): SOLID Principles Basics"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Python
  - OOP
  - SOLID
  - Design Principles
  - Clean Code
seo_description: Learn the five SOLID principles with Python examples and practical guidance for applying them in real projects.
last_reviewed: '2026-05-17'
---

# Object-Oriented Programming 101 (8/10): SOLID Principles Basics

This is post 8 in the Object-Oriented Programming 101 series.

SOLID starts making sense when one service keeps growing until every new requirement shakes unrelated code.

Rather than treating SOLID as five isolated slogans, we will use one checkout workflow and refactor it step by step. Each principle will answer a concrete design smell, not just define a rule.

## Questions to Keep in Mind

- What boundary should you inspect first when applying SOLID Principles Basics?
- Which signal should the example or diagram make visible for SOLID Principles Basics?
- What failure should be prevented first when SOLID Principles Basics reaches a real system?

## Big Picture

![Object-Oriented Programming 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/08/08-01-concept-overview.en.png)

*Object-Oriented Programming 101 chapter 8 flow overview*

This picture places SOLID Principles Basics inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## Questions This Article Answers

- Which SOLID principle matches the failure shape I am seeing right now?
- How do I refactor one workflow without turning the lesson into five disconnected toy snippets?
- What should keep working after each refactor step so I know the design is improving rather than drifting?

## What This Article Tries to Solve

> SOLID is most useful when you can point to one brittle workflow and ask, "what is the smallest design move that stops this code from breaking the same way again?"

- How do you recognize which principle matches the failure you are seeing?
- What changes after SRP, and what should stay stable?
- How do OCP, LSP, ISP, and DIP build on top of one another instead of competing?
- When does applying SOLID too early become over-design?

## Concept Overview

The key is not memorizing the acronym. The key is mapping one visible failure mode to one design correction. If the service has too many reasons to change, start with SRP. If every new rule edits old branching code, reach for OCP. If the system cannot swap dependencies cleanly, DIP is the more urgent fix.

## Key Concepts

| Term | Description |
|------|-------------|
| SRP | A class should change for one reason at a time |
| OCP | New behavior should arrive mainly by extension, not by editing stable flow |
| LSP | A subtype must honor the behavioral expectations of its parent contract |
| ISP | Clients should depend only on the methods they actually need |
| DIP | High-level policies should depend on abstractions instead of concrete tools |

## Before / After

The chapter starts with one overloaded checkout service and ends with a thinner workflow coordinator.

```python
# before: one class owns validation, pricing, persistence, and notification
class OrderService:
    def checkout(self, order: dict) -> int:
        if not order["items"]:
            raise ValueError("order must contain items")
        total = sum(item["price"] for item in order["items"])
        if order["customer_tier"] == "vip":
            total = int(total * 0.8)
        print(f"saving order for {order['customer_email']}")
        print(f"emailing receipt for {total}")
        return total
```

```python
# after: the checkout flow depends on smaller collaborators and abstractions
class CheckoutService:
    def __init__(self, validator, pricer, repository, notifier) -> None:
        self.validator = validator
        self.pricer = pricer
        self.repository = repository
        self.notifier = notifier
```

## One Workflow: Refactoring a Checkout Service with SOLID

### Step 1: SRP — Split Distinct Reasons to Change

Here is the brittle starting point.

```python
class OrderService:
    def checkout(self, order: dict) -> int:
        if not order["items"]:
            raise ValueError("order must contain items")

        total = sum(item["price"] for item in order["items"])

        if order["customer_tier"] == "vip":
            total = int(total * 0.8)

        print(f"saving order for {order['customer_email']}")
        print(f"emailing receipt for {total}")
        return total
```

This service changes when validation rules change, discount policy changes, persistence changes, or message delivery changes. That is four reasons to change packed into one class.

Refactor first by separating responsibilities.

```python
class OrderValidator:
    def validate(self, order: dict) -> None:
        if not order["items"]:
            raise ValueError("order must contain items")

class OrderPricer:
    def calculate_total(self, order: dict) -> int:
        return sum(item["price"] for item in order["items"])

class OrderRepository:
    def save(self, order: dict, total: int) -> None:
        print(f"saving order for {order['customer_email']} -> {total}")

class ReceiptNotifier:
    def send(self, email: str, total: int) -> None:
        print(f"emailing receipt to {email} for {total}")

class CheckoutService:
    def __init__(self) -> None:
        self.validator = OrderValidator()
        self.pricer = OrderPricer()
        self.repository = OrderRepository()
        self.notifier = ReceiptNotifier()

    def checkout(self, order: dict) -> int:
        self.validator.validate(order)
        total = self.pricer.calculate_total(order)
        self.repository.save(order, total)
        self.notifier.send(order["customer_email"], total)
        return total
```

#### Verify

```python
order = {
    "customer_email": "kim@example.com",
    "customer_tier": "regular",
    "items": [{"price": 12000}, {"price": 8000}],
}

print(CheckoutService().checkout(order))
```

Expected output:

```text
saving order for kim@example.com -> 20000
emailing receipt to kim@example.com for 20000
20000
```

What changed: responsibilities are now split. What stayed stable: `checkout()` still returns the total.

#### Failure Signal Before the Refactor

If the team asks for Slack notifications as well as email, the original class must be edited even though pricing rules did not change. That is the signal that SRP was already under strain.

### Step 2: OCP — Move Discount Rules Behind an Extension Point

The checkout flow is still brittle because every new discount edits the pricing logic.

```python
from typing import Protocol

class DiscountPolicy(Protocol):
    def apply(self, subtotal: int, order: dict) -> int: ...

class NoDiscount:
    def apply(self, subtotal: int, order: dict) -> int:
        return subtotal

class VipDiscount:
    def apply(self, subtotal: int, order: dict) -> int:
        return int(subtotal * 0.8) if order["customer_tier"] == "vip" else subtotal

class ThresholdDiscount:
    def __init__(self, minimum: int, amount: int) -> None:
        self.minimum = minimum
        self.amount = amount

    def apply(self, subtotal: int, order: dict) -> int:
        return subtotal - self.amount if subtotal >= self.minimum else subtotal

class OrderPricer:
    def __init__(self, discount: DiscountPolicy) -> None:
        self.discount = discount

    def calculate_total(self, order: dict) -> int:
        subtotal = sum(item["price"] for item in order["items"])
        return self.discount.apply(subtotal, order)
```

#### Verify

```python
order = {
    "customer_email": "kim@example.com",
    "customer_tier": "vip",
    "items": [{"price": 12000}, {"price": 8000}],
}

print(OrderPricer(NoDiscount()).calculate_total(order))
print(OrderPricer(VipDiscount()).calculate_total(order))
print(OrderPricer(ThresholdDiscount(minimum=15000, amount=3000)).calculate_total(order))
```

Expected output:

```text
20000
16000
17000
```

What changed: the pricing rule became pluggable. What stayed stable: callers still ask the pricer for one total.

#### Failure Signal Before the Refactor

If every promotional rule adds another `if` branch to one method, OCP is the next principle to apply.

### Step 3: LSP — Keep the Contract Honest

An extension point is only useful if each subtype honors the same promise. Here is a broken subtype.

```python
class PickupOnlyDiscount:
    def apply(self, subtotal: int, order: dict) -> int:
        if order["delivery"] != "pickup":
            raise ValueError("pickup-only discount cannot handle delivery orders")
        return subtotal - 2000
```

This technically matches the method signature, but it does not behave like a safe `DiscountPolicy` for the checkout flow. The caller expects any discount policy to produce a total for any valid order.

Refactor by moving the special condition into composition instead of hiding it inside a subtype that surprises the caller.

```python
class EligibilityRule(Protocol):
    def allows(self, order: dict) -> bool: ...

class PickupEligibility:
    def allows(self, order: dict) -> bool:
        return order["delivery"] == "pickup"

class FixedAmountDiscount:
    def __init__(self, amount: int) -> None:
        self.amount = amount

    def apply(self, subtotal: int, order: dict) -> int:
        return max(0, subtotal - self.amount)

class ConditionalDiscount:
    def __init__(self, rule: EligibilityRule, inner: DiscountPolicy) -> None:
        self.rule = rule
        self.inner = inner

    def apply(self, subtotal: int, order: dict) -> int:
        if not self.rule.allows(order):
            return subtotal
        return self.inner.apply(subtotal, order)
```

#### Verify

```python
pickup_order = {"delivery": "pickup", "items": [{"price": 10000}], "customer_tier": "regular"}
delivery_order = {"delivery": "courier", "items": [{"price": 10000}], "customer_tier": "regular"}

policy = ConditionalDiscount(PickupEligibility(), FixedAmountDiscount(2000))
print(policy.apply(10000, pickup_order))
print(policy.apply(10000, delivery_order))
```

Expected output:

```text
8000
10000
```

What changed: non-eligible orders now remain valid instead of exploding. What stayed stable: the pricing contract always returns a total.

#### Failure Signal Before the Refactor

If one child implementation needs special-case exceptions for ordinary parent use, the hierarchy is lying. That is an LSP problem.

### Step 4: ISP — Narrow the Interfaces Each Client Depends On

The checkout workflow still does not need every operation some backend tool might expose.

```python
from typing import Protocol

class OrderGateway(Protocol):
    def save(self, order: dict, total: int) -> None: ...
    def send_receipt(self, email: str, total: int) -> None: ...
    def export_daily_report(self) -> str: ...
```

This interface is too broad for `CheckoutService`. The checkout flow does not need reporting.

```python
class OrderWriter(Protocol):
    def save(self, order: dict, total: int) -> None: ...

class ReceiptSender(Protocol):
    def send_receipt(self, email: str, total: int) -> None: ...

class OrderRepository:
    def save(self, order: dict, total: int) -> None:
        print(f"saving order for {order['customer_email']} -> {total}")

class EmailNotifier:
    def send_receipt(self, email: str, total: int) -> None:
        print(f"emailing receipt to {email} for {total}")

class CheckoutService:
    def __init__(self, writer: OrderWriter, sender: ReceiptSender, pricer: OrderPricer, validator: OrderValidator) -> None:
        self.writer = writer
        self.sender = sender
        self.pricer = pricer
        self.validator = validator
```

#### Verify

What changed: checkout no longer depends on export/reporting methods it never calls. What stayed stable: the service still needs only persistence plus receipt sending.

#### Failure Signal Before the Refactor

If a fake dependency in tests must implement unrelated methods just to satisfy the type, the interface is already too wide.

### Step 5: DIP — Inject Abstractions, Not Concrete Tools

The last step is to remove direct dependency on concrete infrastructure so the high-level checkout policy stays easy to test.

```python
from typing import Protocol

class OrderWriter(Protocol):
    def save(self, order: dict, total: int) -> None: ...

class ReceiptSender(Protocol):
    def send_receipt(self, email: str, total: int) -> None: ...

class CheckoutService:
    def __init__(self, validator: OrderValidator, pricer: OrderPricer, writer: OrderWriter, sender: ReceiptSender) -> None:
        self.validator = validator
        self.pricer = pricer
        self.writer = writer
        self.sender = sender

    def checkout(self, order: dict) -> int:
        self.validator.validate(order)
        total = self.pricer.calculate_total(order)
        self.writer.save(order, total)
        self.sender.send_receipt(order["customer_email"], total)
        return total

class FakeWriter:
    def __init__(self) -> None:
        self.saved: list[tuple[str, int]] = []

    def save(self, order: dict, total: int) -> None:
        self.saved.append((order["customer_email"], total))

class FakeSender:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def send_receipt(self, email: str, total: int) -> None:
        self.messages.append(f"{email}:{total}")

writer = FakeWriter()
sender = FakeSender()
service = CheckoutService(
    validator=OrderValidator(),
    pricer=OrderPricer(VipDiscount()),
    writer=writer,
    sender=sender,
)

order = {
    "customer_email": "kim@example.com",
    "customer_tier": "vip",
    "delivery": "courier",
    "items": [{"price": 12000}, {"price": 8000}],
}

total = service.checkout(order)
print(total)
print(writer.saved)
print(sender.messages)
```

#### Verify

Expected output:

```text
16000
[('kim@example.com', 16000)]
['kim@example.com:16000']
```

What changed: the high-level workflow can be tested without a database or email system. What stayed stable: the service still coordinates the same checkout policy.

#### Failure Signal Before the Refactor

If you cannot test the policy without booting real infrastructure, DIP is the missing piece.

## Run and Verify the Final Workflow

Save the final Step 5 code as `solid_checkout.py` and run:

```bash
python solid_checkout.py
```

Final verification checklist:

1. Validation still blocks an empty order.
2. The discount policy can change without editing `CheckoutService`.
3. A non-eligible order no longer crashes a subtype unexpectedly.
4. Test doubles can replace persistence and notification infrastructure.

## How the Principles Connect

| Principle | Smell we saw | Refactor move |
|-----------|---------------|---------------|
| SRP | One class changed for validation, pricing, persistence, and notification | Split collaborators by reason to change |
| OCP | Every new discount edited pricing code | Introduce `DiscountPolicy` |
| LSP | One subtype crashed on otherwise valid orders | Replace brittle inheritance assumptions with composition |
| ISP | Checkout depended on methods it never used | Split large gateway interfaces |
| DIP | Policy code depended on concrete tools | Inject abstractions and fakes |

## 5 Common Mistakes

| Mistake | Why It Hurts | Better Move |
|---------|--------------|-------------|
| Applying all five principles before any pain appears | The design becomes abstract without a clear payoff | Start from the visible failure shape |
| Treating OCP as "never edit code again" | Indirection grows faster than value | Extract only the rules that actually vary |
| Mistaking signature compatibility for LSP | Subtypes still break callers at runtime | Verify behavioral expectations, not just method names |
| Using one giant interface for convenience | Clients must fake unrelated methods | Split interfaces by caller need |
| Calling something DIP while constructing concretes internally | Tests and replacements remain expensive | Inject abstractions from the outside |

## Real-World Uses

- Payment, shipping, and notification rules often become OCP extension points.
- Service-layer tests become dramatically easier once DIP allows fakes.
- Framework integration points are healthier when wide infrastructure interfaces are split by ISP.
- SRP usually arrives first because change pressure shows up there earliest.

## How Senior Engineers Think About This

Senior engineers rarely ask, "did we apply all five SOLID principles?" They ask, "what failure keeps repeating, and which principle gives the smallest fix?" The value of SOLID is not ceremony. The value is sharper reasoning about change.

That is why a practical refactor often starts with SRP or DIP, then adds OCP only where variation is real. LSP and ISP act as guardrails that keep those abstractions honest and narrow.

## Checklist

- [ ] I can connect each SOLID principle to a visible design smell
- [ ] I can split a large service by reason to change
- [ ] I can introduce an extension point without rewriting the stable workflow
- [ ] I can recognize when a subtype violates behavioral expectations
- [ ] I can test a high-level workflow by injecting fakes through abstractions

## Summary and Next Steps

SOLID becomes practical when you apply it to one brittle workflow instead of memorizing five slogans in isolation. In this checkout example, SRP split responsibilities, OCP made discount rules extensible, LSP kept the contract honest, ISP narrowed dependencies, and DIP made the policy testable. In the next article, we apply these ideas together in a fuller OOP design example.

## Answering the Opening Questions

- **What boundary should you inspect first when applying SOLID Principles Basics?**
  - The article treats SOLID Principles Basics as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for SOLID Principles Basics?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when SOLID Principles Basics reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Object-Oriented Programming 101 (1/10): What Is Object-Oriented Programming?](./01-what-is-oop.md)
- [Object-Oriented Programming 101 (2/10): Classes and Instances](./02-classes-and-instances.md)
- [Object-Oriented Programming 101 (3/10): Encapsulation](./03-encapsulation.md)
- [Object-Oriented Programming 101 (4/10): Inheritance](./04-inheritance.md)
- [Object-Oriented Programming 101 (5/10): Polymorphism](./05-polymorphism.md)
- [Object-Oriented Programming 101 (6/10): Abstraction](./06-abstraction.md)
- [Object-Oriented Programming 101 (7/10): Composition vs Inheritance](./07-composition-vs-inheritance.md)
- **SOLID Principles Basics (current)**
- OOP Design Example (upcoming)
- When to Avoid OOP (upcoming)

<!-- toc:end -->

## References

- [PEP 544 — Protocols: Structural Subtyping](https://peps.python.org/pep-0544/)
- [Python Official Docs — abc](https://docs.python.org/3/library/abc.html)
- [Real Python — SOLID Principles in Python](https://realpython.com/solid-principles-python/)
- [Agile Software Development, Principles, Patterns, and Practices in C# — Robert C. Martin](https://www.oreilly.com/library/view/agile-software-development/0135974445/)

Tags: Python, OOP, SOLID, Design Principles, Clean Code
