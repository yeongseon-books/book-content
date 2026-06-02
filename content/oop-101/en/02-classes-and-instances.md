---
series: oop-101
episode: 2
title: "Object-Oriented Programming 101 (2/10): Classes and Instances"
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
  - Classes
  - Instances
  - Constructors
seo_description: Master Python class constructors, instance methods, class methods, static methods, and dunder methods with practical examples.
last_reviewed: '2026-05-04'
---

# Object-Oriented Programming 101 (2/10): Classes and Instances

This is the 2nd post in the Object-Oriented Programming 101 series.

> Object-Oriented Programming 101 Series (2/10)

**Key Question**: How should you design classes and work with instances effectively?

> A class is the blueprint; an instance is the actual object built from it. This article covers constructors, instance methods, class methods, static methods, and Python's special dunder methods — the building blocks of any class.


![Object-Oriented Programming 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/02/02-01-big-picture.en.png)
*Object-Oriented Programming 101 chapter 2 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Classes and Instances?
- Which signal should the example or diagram make visible for Classes and Instances?
- What failure should be prevented first when Classes and Instances reaches a real system?

## What You Will Learn

- Constructor (`__init__`) and instance initialization patterns
- Differences between instance methods, class methods, and static methods
- Dunder methods: `__repr__`, `__str__`, `__eq__`, and more
- Class design patterns used frequently in production code

## Why It Matters

Creating a class is not hard. The hard part is deciding which data becomes attributes and which operations become methods. Good class design improves both reusability and readability.

> Good class = clear responsibility + proper interface + hidden internals

Python's dunder methods let you integrate custom classes seamlessly with built-in syntax. `print()`, `==`, `len()`, and `for` loops all work naturally with user-defined objects when the right dunders are in place.

## Concept Overview

> Anatomy of a class

```text
Class
├── class variable
├── __init__()       → instance initialization
├── instance method  → self as first arg
├── @classmethod     → cls as first arg
├── @staticmethod    → no self/cls
└── dunder methods   → __repr__, __str__, __eq__, ...
```

## Key Concepts

| Term | Description |
|------|-------------|
| Constructor (`__init__`) | Initializer called automatically when an instance is created |
| Instance method | Takes `self` as first parameter to access instance data |
| Class method (`@classmethod`) | Takes `cls` as first parameter and operates at the class level |
| Static method (`@staticmethod`) | A utility function that does not depend on instance or class state |
| Dunder method | Methods starting and ending with `__` that implement Python protocols |

## Before / After

Improving object comparison and display.

```python
# before: no dunder methods — unhelpful output and comparison
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

p1 = Point(1, 2)
p2 = Point(1, 2)
print(p1)        # <__main__.Point object at 0x...>
print(p1 == p2)  # False — same coordinates but considered different
```

```python
# after: dunder methods — intuitive output and comparison
class Point:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y

p1 = Point(1, 2)
p2 = Point(1, 2)
print(p1)        # Point(1, 2)
print(p1 == p2)  # True
```

## Hands-On Steps

### Step 1: Constructor Patterns

```python
class Product:
    """Product class — validation in the constructor"""

    def __init__(self, name: str, price: int, quantity: int = 0) -> None:
        if price < 0:
            raise ValueError(f"Price cannot be negative: {price}")
        self.name = name
        self.price = price
        self.quantity = quantity

    def total_value(self) -> int:
        return self.price * self.quantity

    def __repr__(self) -> str:
        return f"Product({self.name!r}, {self.price}, {self.quantity})"

p = Product("Keyboard", 50000, 3)
print(p.total_value())  # 150000
print(p)                # Product('Keyboard', 50000, 3)
```

### Step 2: Alternative Constructors with @classmethod

```python
class Date:
    def __init__(self, year: int, month: int, day: int) -> None:
        self.year = year
        self.month = month
        self.day = day

    @classmethod
    def from_string(cls, date_str: str) -> "Date":
        """Create Date from 'YYYY-MM-DD' string"""
        year, month, day = map(int, date_str.split("-"))
        return cls(year, month, day)

    @classmethod
    def today(cls) -> "Date":
        """Create Date from today's date"""
        from datetime import date
        d = date.today()
        return cls(d.year, d.month, d.day)

    def __repr__(self) -> str:
        return f"Date({self.year}, {self.month}, {self.day})"

d1 = Date(2026, 5, 4)
d2 = Date.from_string("2026-05-04")
print(d1)  # Date(2026, 5, 4)
print(d2)  # Date(2026, 5, 4)
```

### Step 3: Static Methods

```python
class MathUtils:
    @staticmethod
    def is_even(n: int) -> bool:
        return n % 2 == 0

    @staticmethod
    def factorial(n: int) -> int:
        if n < 0:
            raise ValueError("Factorial is not defined for negative numbers")
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result

print(MathUtils.is_even(4))     # True
print(MathUtils.factorial(5))   # 120
```

### Step 4: Operator Overloading with Dunders

```python
class Vector:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar: float) -> "Vector":
        return Vector(self.x * scalar, self.y * scalar)

    def __abs__(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def __repr__(self) -> str:
        return f"Vector({self.x}, {self.y})"

v1 = Vector(3, 4)
v2 = Vector(1, 2)
print(v1 + v2)    # Vector(4, 6)
print(v1 * 2)     # Vector(6, 8)
print(abs(v1))    # 5.0
```

### Step 5: Memory Optimization with __slots__

```python
class RegularPoint:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

class OptimizedPoint:
    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

import sys

rp = RegularPoint(1, 2)
op = OptimizedPoint(1, 2)
print(sys.getsizeof(rp.__dict__))  # size of regular instance __dict__
# OptimizedPoint has no __dict__ → saves memory
```

## What to Notice in This Code

- `@classmethod` is mainly used for alternative constructors (factory methods)
- `@staticmethod` is for utilities logically related to the class but needing no instance data
- The `isinstance` check and `NotImplemented` return in `__eq__` are the standard pattern for type-safe comparison
- `__slots__` saves memory when creating millions of instances

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|---------------------|-----|
| Returning a value from `__init__` | `__init__` must return `None` | Only write initialization logic; omit `return` |
| Confusing `@classmethod` and `@staticmethod` | They differ in access to class data | Use `@classmethod` when `cls` is needed, `@staticmethod` otherwise |
| Defining `__eq__` without `__hash__` | Cannot use as dict key or set member | Define `__hash__` whenever you define `__eq__` |
| Making every method `@staticmethod` | No reason to use a class at all | Use instance methods when instance data is involved |
| Mutable default argument | All calls share the same object | Use `None` as default and create inside the function |

## Real-World Applications

- Django ORM's `Model.objects.create()` is a classmethod-based factory
- dataclasses and Pydantic auto-generate `__init__`, `__repr__`, `__eq__`
- `__slots__` saves memory in high-volume data objects (millions of records)
- FastAPI uses classes as callables for dependency injection
- Tests use `__eq__` for `assert actual == expected` comparisons

## How Senior Engineers Think About This

The most important principle when designing classes is "one class, one responsibility." A class that does too much is hard to test and fragile against changes.

Since Python 3.7, consider `dataclasses` first. They reduce boilerplate while still letting you add custom methods — suitable for most data-centric classes.

## Checklist

- [ ] I can perform validation in the constructor
- [ ] I can create alternative constructors with `@classmethod`
- [ ] I can judge when `@staticmethod` is appropriate
- [ ] I can implement `__repr__`, `__eq__`, and other dunder methods
- [ ] I understand the purpose and constraints of `__slots__`

## Exercises

1. Create a `Money` class implementing `__add__`, `__sub__`, `__repr__`, and `__eq__`.
2. Create a `Temperature` class with a `from_fahrenheit()` classmethod.
3. Create a `Pixel` class using `__slots__`, generate one million instances, and compare memory usage with a regular class.

## Summary and Next Steps

A class is composed of constructors, instance methods, class methods, static methods, and dunder methods. Understanding each component lets you design clean, Pythonic classes. In the next article, we explore encapsulation — protecting a class's internal state.

## What to Look at First in Class Design: State Consistency

When distinguishing classes and instances, the criterion more important than syntax is state consistency. What invariants the constructor guarantees and what rules the object state observes after method calls determine design quality.

```text
[InventoryItem]
  - sku: str
  - quantity: int
  - unit_price: int
  + increase(qty)
  + decrease(qty)
  + valuation()

Relationship
InventoryService --> InventoryItem (uses)
```

## Before and After: From Free-Input Constructor to Validation-Centric Object

```python
# before
class InventoryItem:
    def __init__(self, sku, quantity, unit_price):
        self.sku = sku
        self.quantity = quantity
        self.unit_price = unit_price
```

```python
# after
class InventoryItem:
    def __init__(self, sku: str, quantity: int, unit_price: int) -> None:
        if not sku:
            raise ValueError('sku is required')
        if quantity < 0:
            raise ValueError('quantity must be >= 0')
        if unit_price <= 0:
            raise ValueError('unit_price must be > 0')

        self.sku = sku
        self._quantity = quantity
        self.unit_price = unit_price

    @property
    def quantity(self) -> int:
        return self._quantity

    def increase(self, qty: int) -> None:
        if qty <= 0:
            raise ValueError('qty must be positive')
        self._quantity += qty

    def decrease(self, qty: int) -> None:
        if qty <= 0:
            raise ValueError('qty must be positive')
        if self._quantity - qty < 0:
            raise ValueError('stock cannot be negative')
        self._quantity -= qty

    def valuation(self) -> int:
        return self._quantity * self.unit_price
```

The key is restricting manipulation paths so that an instance maintains a valid state even after creation.

## Class Variable Misuse and Correction

| Violation Code | Problem | Fix |
|---|---|---|
| `items = []` declared as class variable | All instances share the same list | Declare `self.items = []` in `__init__` |
| Using class variable for settings that differ per instance | Unexpected global side effects | Immutable settings as class variables, mutable state as instance variables |

## Instance Lifecycle Table

| Stage | Question | Recommended Design |
|---|---|---|
| Creation | What inputs should be rejected? | Validate immediately in constructor |
| Usage | What state transitions are allowed? | Express transition intent through method names |
| Query | What should be exposed externally? | Read-only property first |
| Disposal | Is external resource cleanup needed? | Context manager or explicit close |

## Classes and Instances from a Testing Perspective

```python
import pytest


def test_inventory_item_invariants() -> None:
    item = InventoryItem('A-100', 10, 3000)
    item.decrease(4)
    assert item.quantity == 6

    with pytest.raises(ValueError):
        item.decrease(7)
```

This test verifies not just numeric results but the contract that instance invariants remain unbroken.

## Real Scenario: Restructuring to Withstand Requirement Changes

In production, rule changes happen more often than feature additions. Therefore, when evaluating class structure, it's safer to ask "how far must the next change reach?" rather than "does it work now?"

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

This code requires no modification to `Invoice.total()` when discount rules change. Extension closes through adding implementation classes, while the core flow remains stable.

## Collaboration in UML Style

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

Writing collaboration structure in text like this lets you quickly align on "where is the policy axis and where is the domain axis" during code review.

## Anti-Patterns and Correction Procedures

| Anti-Pattern | Detection Signal | Correction Steps |
|---|---|---|
| God Object | 20+ methods, scattered change history | Decompose by responsibility axis → derive collaboration interfaces |
| Data-only empty class | Only getters/setters, no methods | Move rule methods or simplify to dataclass |
| Inheritance tree bypass branching | Type-check branching on subclasses | Redefine polymorphic contract |
| Infrastructure type leakage | Domain layer depends on SDK response objects | Add DTO conversion layer |

## Before and After: Test Maintenance Cost

| Item | Before Refactoring | After Refactoring |
|---|---|---|
| Test setup | Global state initialization needed | Per-object state creation |
| Failure root-cause tracing | Backtrack entire function chain | Trace per class method |
| Regression scope | Broad and unclear | Narrow and predictable |

## Team Application Checklist

- Confirm domain terms and class names match.
- Confirm invariants are complete at instance creation time.
- Check whether policy changes are possible via implementation addition rather than existing code modification.
- Agree on collaboration structure via 10-line UML text before code review.
- Confirm test names describe business rules rather than method names.

## Mini Case Study: Verifying with a Single Rule Addition

The example below is the minimum unit for extending a policy without modifying existing code.

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

The key is that the new policy enters without breaking call paths. Keeping change history confined to policy classes reduces regression risk.

| Verification Question | Pass Criteria |
|---|---|
| Does adding a new policy require modifying existing functions? | No |
| Does the exception policy match the existing contract? | Yes |
| Are tests separated per policy? | Yes |

## Refactoring Retrospective: Viewing Change Cost as Numbers

- If modified file count exceeds 5 per feature, review boundary redesign.
- If type-branch if/elif accumulates 3 or more, move to polymorphism or strategy objects.
- If regression test writing time exceeds implementation time, review responsibility placement.

```python
def complexity_signal(changed_files: int, branch_count: int) -> str:
    if changed_files >= 5 or branch_count >= 3:
        return 'refactor-needed'
    return 'acceptable'
```

This approach is not a rigorous metric, but it's useful for making teams discuss based on criteria rather than intuition.

## Verification Note: Questions for Checking Object Design Quality

These questions are criteria used repeatedly in post-implementation reviews.

- Does the exception type and message match the caller's contract when this method fails?
- Is the same rule not duplicated in other classes or functions?
- Does state mutation occur through only one method path?
- Is unit testing possible without external dependencies?

```python
def review_signal(duplicate_rules: int, mutable_paths: int) -> str:
    if duplicate_rules > 0:
        return 'duplicate rule removal needed'
    if mutable_paths > 1:
        return 'state mutation path consolidation needed'
    return 'structure stable'
```

Applying these checks even to article-level examples helps understand OOP as a maintenance strategy rather than syntax.

## Additional Comparison: Response Time to Change Requests

| Change Request | Code with Weak Boundaries | Code with Clear Boundaries |
|---|---|---|
| Add discount rule | Search branches then multi-modify | Add policy implementation |
| Modify state transition | Modify multiple functions simultaneously | Modify domain method |
| Strengthen tests | Integration-test-centric | Unit-test-first |

This comparison matters not for performance numbers but for reducing maintenance lead time.


## Answering the Opening Questions

- **How much should the constructor (`__init__`) be responsible for, and where does it become too much?**
  - `Product` validates negative prices immediately, and `InventoryItem` locks `sku`, `quantity`, and `unit_price` invariants at creation time. However, once you start putting DB queries or external API calls—things beyond the object's core state—into the constructor, it becomes excessive. The article showed `Date.from_string()` class methods as an alternative constructor pattern for such cases.
- **What criteria distinguish instance methods, class methods, and static methods?**
  - `InventoryItem.increase()` and `decrease()` modify instance state, so they are instance methods. `Date.from_string()` and `today()` create the same type through different input paths, making them class methods. `MathUtils.factorial()`, which needs neither `self` nor `cls`, naturally fits as a static method. The article noted that when this distinction blurs, classes become heavy namespaces.
- **Why are Python's dunder methods important for debugging and comparison operations?**
  - The `Point` example showed that without `__repr__`, you only see `<__main__.Point object ...>` during debugging, and without `__eq__`, two points with identical coordinates compare as `False`. `Vector`'s `__add__`, `__mul__`, and `__abs__` demonstrated how objects integrate naturally with Python syntax, revealing that dunder methods are not mere decoration but directly affect usability and test accuracy.
<!-- toc:begin -->
## In this series

- [Object-Oriented Programming 101 (1/10): What Is Object-Oriented Programming?](./01-what-is-oop.md)
- **Classes and Instances (current)**
- Encapsulation (upcoming)
- Inheritance (upcoming)
- Polymorphism (upcoming)
- Abstraction (upcoming)
- Composition vs Inheritance (upcoming)
- SOLID Principles Basics (upcoming)
- OOP Design Example (upcoming)
- When to Avoid OOP (upcoming)

<!-- toc:end -->

## References

- [Python Official Docs — Data Model](https://docs.python.org/3/reference/datamodel.html)
- [Real Python — Python Classes](https://realpython.com/python3-object-oriented-programming/)
- [Fluent Python — Luciano Ramalho](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)
- [Python dataclasses Official Docs](https://docs.python.org/3/library/dataclasses.html)

Tags: Python, OOP, Classes, Instances, Constructors
