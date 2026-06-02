---
series: oop-101
episode: 5
title: "Object-Oriented Programming 101 (5/10): Polymorphism"
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
  - OOP
  - Polymorphism
  - Duck Typing
  - Protocol
seo_description: Learn how Python implements polymorphism through inheritance, duck typing, and the Protocol class for structural subtyping.
last_reviewed: '2026-05-04'
---

# Object-Oriented Programming 101 (5/10): Polymorphism

This is the 5th post in the Object-Oriented Programming 101 series.

> Object-Oriented Programming 101 Series (5/10)

**Key Question**: How do you handle objects of different types through a single interface?

> Polymorphism means that a method with the same name behaves differently depending on the object's type. Python's duck typing enables polymorphism without inheritance. This article covers inheritance-based polymorphism, duck typing, and Python 3.8+ Protocol.


![Object-Oriented Programming 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/05/05-01-big-picture.en.png)
*Object-Oriented Programming 101 chapter 5 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Polymorphism?
- Which signal should the example or diagram make visible for Polymorphism?
- What failure should be prevented first when Polymorphism reaches a real system?

## What You Will Learn

- The concept of polymorphism and three implementation approaches
- Duck typing principles and usage
- Structural subtyping with Python `Protocol`
- Practical polymorphic code patterns

## Why It Matters

Imagine a payment system handling credit cards, bank transfers, and e-wallets. Each payment method has different internal logic, but the caller wants a single `pay(amount)` interface. Polymorphism solves this problem.

> Polymorphism = same interface, different implementations

Without polymorphism, `if isinstance(payment, CreditCard): ...` branches multiply every time a new payment method is added. With polymorphism, adding a new payment method requires no changes to existing code.

## Concept Overview

> Three approaches to polymorphism in Python

```text
1. Inheritance-based polymorphism
   Animal -> Dog.speak(), Cat.speak()

2. Duck Typing
   "If it has a quack() method, it's a duck"
   No inheritance needed — just matching methods

3. Protocol — Python 3.8+
   Structural subtyping: type hints verify duck typing
```

## Key Concepts

| Term | Description |
|------|-------------|
| Polymorphism | A single interface behaving differently based on the object's type |
| Duck typing | Judging an object by its methods, not its type |
| Protocol | A `typing` module class that supports structural subtyping |
| Dispatch | The mechanism that selects the actual type's method at call time |
| Interface | The set of methods an object must provide |

## Before / After

Comparing payment processing approaches.

```python
# before: type-based branching — requires modification for each new payment method
def process_payment(payment, amount):
    if payment["type"] == "credit_card":
        print(f"Credit card payment: ${amount}")
    elif payment["type"] == "bank_transfer":
        print(f"Bank transfer: ${amount}")
    # new payment method -> add elif
```

```python
# after: polymorphism — no modification needed for new payment methods
class CreditCard:
    def pay(self, amount: int) -> str:
        return f"Credit card payment: ${amount}"

class BankTransfer:
    def pay(self, amount: int) -> str:
        return f"Bank transfer: ${amount}"

def process_payment(payment, amount: int) -> None:
    print(payment.pay(amount))  # any type with pay() works
```

## Hands-On Steps

### Step 1: Inheritance-Based Polymorphism

```python
class Shape:
    def area(self) -> float:
        raise NotImplementedError

    def describe(self) -> str:
        return f"{type(self).__name__}: area = {self.area():.2f}"

class Circle(Shape):
    def __init__(self, radius: float) -> None:
        self.radius = radius

    def area(self) -> float:
        import math
        return math.pi * self.radius ** 2

class Rectangle(Shape):
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

class Triangle(Shape):
    def __init__(self, base: float, height: float) -> None:
        self.base = base
        self.height = height

    def area(self) -> float:
        return 0.5 * self.base * self.height

shapes: list[Shape] = [Circle(5), Rectangle(4, 6), Triangle(3, 8)]
for shape in shapes:
    print(shape.describe())
# Circle: area = 78.54
# Rectangle: area = 24.00
# Triangle: area = 12.00
```

### Step 2: Duck Typing

```python
class FileWriter:
    def write(self, data: str) -> None:
        print(f"Writing to file: {data}")

class DatabaseWriter:
    def write(self, data: str) -> None:
        print(f"Saving to DB: {data}")

class ApiWriter:
    def write(self, data: str) -> None:
        print(f"Sending to API: {data}")

def save_data(writer, data: str) -> None:
    """The type of writer does not matter — only the write() method"""
    writer.write(data)

save_data(FileWriter(), "hello")       # Writing to file: hello
save_data(DatabaseWriter(), "hello")   # Saving to DB: hello
save_data(ApiWriter(), "hello")        # Sending to API: hello
```

### Step 3: Structural Subtyping with Protocol

```python
from typing import Protocol

class Writable(Protocol):
    def write(self, data: str) -> None: ...

class ConsoleWriter:
    def write(self, data: str) -> None:
        print(f"Console output: {data}")

class NetworkWriter:
    def write(self, data: str) -> None:
        print(f"Network send: {data}")

def save_all(writers: list[Writable], data: str) -> None:
    for writer in writers:
        writer.write(data)

writers: list[Writable] = [ConsoleWriter(), NetworkWriter()]
save_all(writers, "important data")
# Console output: important data
# Network send: important data
```

### Step 4: Built-in Polymorphism via Dunder Methods

```python
class Team:
    def __init__(self, name: str, members: list[str]) -> None:
        self.name = name
        self.members = members

    def __len__(self) -> int:
        return len(self.members)

    def __contains__(self, member: str) -> bool:
        return member in self.members

    def __iter__(self):
        return iter(self.members)

team = Team("Backend", ["Kim", "Lee", "Park"])
print(len(team))          # 3
print("Kim" in team)      # True
print(list(team))         # ['Kim', 'Lee', 'Park']

for member in team:
    print(member)
```

### Step 5: functools.singledispatch

```python
from functools import singledispatch

@singledispatch
def format_value(value) -> str:
    return str(value)

@format_value.register(int)
def _(value: int) -> str:
    return f"{value:,}"

@format_value.register(float)
def _(value: float) -> str:
    return f"{value:.2f}"

@format_value.register(list)
def _(value: list) -> str:
    return f"[{len(value)} items]"

print(format_value(1000000))       # 1,000,000
print(format_value(3.14159))       # 3.14
print(format_value([1, 2, 3]))     # [3 items]
print(format_value("hello"))       # hello
```

## What to Notice in This Code

- Python's duck typing enables polymorphism without inheritance
- `Protocol` lets type checkers verify duck typing at analysis time
- Dunder methods like `__len__`, `__contains__`, `__iter__` integrate with Python's built-in syntax
- `singledispatch` provides function-level polymorphism based on argument type

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|---------------------|-----|
| Excessive `isinstance()` branching | Defeats the purpose of polymorphism | Unify through a common interface |
| Mismatched method names in duck typing | `AttributeError` at runtime | Add type hints with `Protocol` |
| Solving everything with inheritance | Creates unnecessary hierarchies | Consider duck typing or Protocol first |
| Missing `NotImplementedError` in base class | Parent's default implementation runs unexpectedly | Use ABC for abstract methods |
| Writing implementation code in Protocol | Protocol is for interface definition only | Method bodies should be `...` only |

## Real-World Applications

- Plugin systems use a common interface to integrate extension modules
- Test mocks implement the same interface to replace real dependencies
- Serialization libraries (JSON, YAML, pickle) share a `dump`/`load` interface
- Web framework middleware processes requests/responses through a common interface
- Database drivers unify around DB-API 2.0 for interchangeable backends

## How Senior Engineers Think About This

In Python, polymorphism "emerges naturally" rather than being "designed intentionally." Thanks to duck typing, objects with matching methods are interchangeable without inheritance.

For projects where type safety matters, use `Protocol` extensively. It has zero runtime impact but lets type checkers (mypy) catch interface violations.

## Checklist

- [ ] I can implement inheritance-based polymorphism
- [ ] I understand duck typing principles and can apply them
- [ ] I can define structural subtyping with `Protocol`
- [ ] I can integrate with Python's built-in syntax via dunder methods
- [ ] I can replace `isinstance()` branching with polymorphism

## Exercises

1. Define an `Exportable` Protocol and implement `CsvExporter`, `JsonExporter`, and `XmlExporter`.
2. Implement a `Matrix` class with `__add__` and `__mul__` dunder methods.
3. Use `singledispatch` to create a function that formats various data types into log output.

## Practical Pattern: Verifying SOLID Boundaries in Code

A common failure in OOP design is treating "more classes" as the goal. In reality, the goal is separating responsibilities and change directions. The example below organizes a payment domain respecting SRP and OCP, showing how composition replaces forced inheritance.

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class PaymentRequest:
    order_id: str
    amount: int


class PaymentGateway(Protocol):
    def pay(self, req: PaymentRequest) -> str:
        ...


class CardGateway:
    def pay(self, req: PaymentRequest) -> str:
        return f"card:{req.order_id}:{req.amount}"


class BankGateway:
    def pay(self, req: PaymentRequest) -> str:
        return f"bank:{req.order_id}:{req.amount}"


class PaymentService:
    def __init__(self, gateway: PaymentGateway) -> None:
        self.gateway = gateway

    def process(self, order_id: str, amount: int) -> str:
        if amount <= 0:
            raise ValueError("amount must be positive")
        return self.gateway.pay(PaymentRequest(order_id=order_id, amount=amount))
```

Adding a new payment method requires no changes to `PaymentService`—just one more class implementing the `PaymentGateway` contract. This is OCP in action. By using Protocol + composition instead of forced inheritance, runtime swapping and test double injection become trivial. The purpose of OOP is not deepening hierarchies but reducing change propagation.

## The Core of Polymorphism Is Collaboration Contracts, Not if/elif Elimination

Polymorphism is not a technique for removing branching—it is a design where callers collaborate through a shared contract without knowing concrete types.

```text
[CheckoutService] --> [PaymentMethod]
PaymentMethod (interface)
  + pay(amount)
      ^            ^            ^
      |            |            |
 [CardPay]     [BankPay]    [PointPay]
```

## Before and After: From Type Branching to Polymorphism

```python
# before

def pay(method: str, amount: int) -> str:
    if method == 'card':
        return f'card:{amount}'
    if method == 'bank':
        return f'bank:{amount}'
    if method == 'point':
        return f'point:{amount}'
    raise ValueError('unsupported method')
```

```python
# after
from typing import Protocol

class PaymentMethod(Protocol):
    def pay(self, amount: int) -> str:
        ...

class CardPay:
    def pay(self, amount: int) -> str:
        return f'card:{amount}'

class BankPay:
    def pay(self, amount: int) -> str:
        return f'bank:{amount}'

class PointPay:
    def pay(self, amount: int) -> str:
        return f'point:{amount}'

class CheckoutService:
    def __init__(self, method: PaymentMethod) -> None:
        self.method = method

    def checkout(self, amount: int) -> str:
        if amount <= 0:
            raise ValueError('amount must be positive')
        return self.method.pay(amount)
```

## Principle Violations and Corrections

| Violation | Consequence | Fix |
|---|---|---|
| `if method == ...` branches duplicated across modules | Multiple edits when adding a payment method | Contract interface + implementation classes |
| Implementation class reads caller's internal state directly | Coupling increases | Pass only necessary data as parameters |
| No common exception handling | Failure format varies per implementation | Separate common exception policy layer |

## Comparison: Inheritance-Based Polymorphism vs Duck Typing Protocol

| Criterion | Inheritance-Based | Protocol-Based |
|---|---|---|
| Applying to existing code | Requires base class modification | Just match methods on existing classes |
| Framework dependency | Relatively high | Low |
| Writing test doubles | Requires subclassing | A simple stub object suffices |

## Refactoring Checklist

- First check whether branch conditions use type-name strings.
- Reduce the caller's concern to a single contract like `pay(amount)`.
- Verify that adding a new type requires zero modifications to existing callers.

## Real-World Scenario: Building a Structure That Survives Requirement Changes

In production, rule changes happen more often than feature additions. When evaluating class structures, "how many files must change for the next requirement" is a safer criterion than "does it work now."

```python
from dataclasses import dataclass
from typing import Protocol


@dataclass
class LineItem:
    name: str
    quantity: int
    unit_price: int

    def subtotal(self) -> int:
        return self.quantity * self.unit_price


class DiscountPolicy(Protocol):
    def apply(self, amount: int) -> int:
        ...


class NoDiscount:
    def apply(self, amount: int) -> int:
        return amount


class PercentDiscount:
    def __init__(self, percent: int) -> None:
        if not 0 <= percent <= 100:
            raise ValueError('percent must be 0..100')
        self.percent = percent

    def apply(self, amount: int) -> int:
        return int(amount * (100 - self.percent) / 100)


class Invoice:
    def __init__(self, items: list[LineItem], policy: DiscountPolicy) -> None:
        self.items = items
        self.policy = policy

    def total(self) -> int:
        base = sum(i.subtotal() for i in self.items)
        return self.policy.apply(base)
```

When the discount rule changes, `Invoice.total()` needs no modification. Extension stays closed through implementation class additions, while the core flow remains stable.

## UML-Style Collaboration View

```text
[Invoice]
  - items: list[LineItem]
  - policy: DiscountPolicy
  + total()

[LineItem]
  + subtotal()

[DiscountPolicy] <<interface>>
  + apply(amount)
      ^
      +-- [NoDiscount]
      +-- [PercentDiscount]
```

Writing collaboration structures as text UML lets code reviews quickly align on "which axis is the policy axis and which is the domain axis."

## Anti-Patterns and Correction Procedures

| Anti-Pattern | Detection Signal | Correction Sequence |
|---|---|---|
| God Object | 20+ methods, scattered change history | Decompose by responsibility axis → derive collaboration interfaces |
| Data-only empty class | Only getters/setters, no methods | Move rule methods in, or simplify to dataclass |
| Inheritance tree bypass branching | Type-check branches on subclass types | Redefine polymorphic contract |
| Infrastructure type leakage | Domain layer depends on SDK response objects | Add DTO conversion layer |

## Before and After: Test Maintenance Cost

| Item | Before Refactoring | After Refactoring |
|---|---|---|
| Test setup | Global state initialization required | Per-object state creation |
| Failure root-cause tracing | Trace entire function chain | Per-method tracing |
| Regression scope | Broad and unpredictable | Narrow and predictable |

## Team Adoption Checklist

- Verify that domain terms and class names match.
- Confirm invariants are fully established at instance creation time.
- Check that policy changes are possible through implementation additions, not existing code modifications.
- In code reviews, agree on collaboration structure with 10-line UML text first.
- Ensure test names describe business rules rather than method names.

## Mini Case Study: Validating with One Rule Addition

The example below is the minimal unit that adds a policy extension without modifying existing code.

```python
class WeekendPolicy:
    def apply(self, amount: int, is_weekend: bool) -> int:
        if is_weekend:
            return int(amount * 0.95)
        return amount


def estimate(amount: int, is_weekend: bool) -> int:
    policy = WeekendPolicy()
    return policy.apply(amount, is_weekend)
```

The key point is that new policies enter without breaking call paths. Keeping change history confined to the policy class reduces regression risk.

| Verification Question | Pass Criterion |
|---|---|
| Does adding a new policy require modifying existing functions? | No |
| Does the exception policy share the same contract? | Yes |
| Are tests separated per policy? | Yes |

## Refactoring Retrospective: Measuring Change Cost Numerically

- If modified file count exceeds 5 per feature, review boundary design.
- If type-branching if/elif accumulates 3+, migrate to polymorphism or strategy objects.
- If regression test writing time exceeds implementation time, revisit responsibility placement.

```python
def complexity_signal(changed_files: int, branch_count: int) -> str:
    if changed_files >= 5 or branch_count >= 3:
        return 'refactor-needed'
    return 'acceptable'
```

This is not a rigorous metric, but it helps teams discuss with criteria rather than gut feeling.

## Design Quality Verification Questions

These questions are used repeatedly during post-implementation reviews.

- Does the exception type and message match the caller's contract when this method fails?
- Is the same rule duplicated in other classes or functions?
- Does state mutation happen through exactly one method path?
- Can the unit be tested without external dependencies?

```python
def review_signal(duplicate_rules: int, mutable_paths: int) -> str:
    if duplicate_rules > 0:
        return 'duplicate rule removal needed'
    if mutable_paths > 1:
        return 'consolidate state mutation paths'
    return 'structure stable'
```

Applying these checks even to article-level examples helps readers understand OOP as a maintenance strategy rather than mere syntax.

## Change Request Response Time Comparison

| Change Request | Weak Boundaries | Clear Boundaries |
|---|---|---|
| Add discount rule | Search branches then multi-edit | Add policy implementation |
| Modify state transition | Simultaneous edits across functions | Modify domain method |
| Strengthen tests | Integration-test-centric | Unit-test-first |

This comparison matters from the perspective of reducing maintenance lead time, not performance numbers.

## Supplementary Note

Design choices are not about finding the "right answer"—they are decisions that lower change cost. Defining boundaries first simplifies both reviews and tests, even for the same functionality.

## Quick Reminder

When applying OOP, evaluate quality by "how many files must change for the next requirement" rather than "how many classes did I create."

## Final Verification Statement

Every example in this article is structured around boundary design that reduces change propagation.

Maintaining design intent and test contracts together is the core principle.
## Summary and Next Steps

Polymorphism increases code flexibility by calling different implementations through a single interface. Python supports polymorphism through duck typing, inheritance, and Protocol. In the next article, we explore abstraction — enforcing common interfaces through abstract base classes.

## Answering the Opening Questions

- **Why is polymorphism the most powerful tool for eliminating type-based branching?**
  - The article started with a payment function that grew `if` branches for each `payment["type"]`, then replaced it with a single `payment.pay(amount)` call—eliminating caller modifications when new payment methods are added. The same flow repeated with `Shape.area()` and `describe()`, and with `CheckoutService` knowing only the `PaymentMethod` contract, concretely showing that polymorphism lowers extension cost far more than branching.
- **What is the difference between inheritance-based polymorphism and duck typing?**
  - `Circle`, `Rectangle`, and `Triangle` share the same `area()` contract by inheriting from `Shape`—a classic example of inheritance-based polymorphism. In contrast, `FileWriter`, `DatabaseWriter`, and `ApiWriter` fit into `save_data()` simply by matching `write()` with no common parent, confirming that duck typing in Python is looser and easier to layer onto existing code.
- **How does `Protocol` reinforce duck typing at the static analysis level?**
  - With a `Writable` Protocol, objects like `ConsoleWriter` and `NetworkWriter`—without any inheritance relationship—pass the type checker as long as they match the `write(self, data: str)` contract. In other words, `Protocol`'s practical value is maintaining runtime flexibility while catching method name mismatches or wrong signatures before deployment.
<!-- toc:begin -->
## In this series

- [Object-Oriented Programming 101 (1/10): What Is Object-Oriented Programming?](./01-what-is-oop.md)
- [Object-Oriented Programming 101 (2/10): Classes and Instances](./02-classes-and-instances.md)
- [Object-Oriented Programming 101 (3/10): Encapsulation](./03-encapsulation.md)
- [Object-Oriented Programming 101 (4/10): Inheritance](./04-inheritance.md)
- **Polymorphism (current)**
- Abstraction (upcoming)
- Composition vs Inheritance (upcoming)
- SOLID Principles Basics (upcoming)
- OOP Design Example (upcoming)
- When to Avoid OOP (upcoming)

<!-- toc:end -->

## References

- [Python Official Docs — typing.Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol)
- [Real Python — Duck Typing in Python](https://realpython.com/duck-typing-python/)
- [PEP 544 — Protocols: Structural subtyping](https://peps.python.org/pep-0544/)
- [Fluent Python — Chapter 13: Interfaces, Protocols, and ABCs](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)

Tags: Python, OOP, Polymorphism, Duck Typing, Protocol
