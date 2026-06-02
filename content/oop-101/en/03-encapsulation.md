---
series: oop-101
episode: 3
title: "Object-Oriented Programming 101 (3/10): Encapsulation"
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
  - Encapsulation
  - Property
  - Information Hiding
seo_description: Learn how Python implements encapsulation through naming conventions and the property decorator for controlled attribute access.
last_reviewed: '2026-05-04'
---

# Object-Oriented Programming 101 (3/10): Encapsulation

This is the 3rd post in the Object-Oriented Programming 101 series.

> Object-Oriented Programming 101 Series (3/10)

**Key Question**: Why and how should you protect an object's internal data?

> Encapsulation shields an object's internal state from direct external modification, exposing it only through a controlled interface. Python has no enforced access control, but naming conventions and the property decorator provide effective encapsulation.


![Object-Oriented Programming 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/03/03-01-big-picture.en.png)
*Object-Oriented Programming 101 chapter 3 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Encapsulation?
- Which signal should the example or diagram make visible for Encapsulation?
- What failure should be prevented first when Encapsulation reaches a real system?

## What You Will Learn

- The purpose and benefits of encapsulation
- Python naming conventions: public, _protected, __private
- Implementing getters and setters with the property decorator
- Integrating validation into properties

## Why It Matters

When external code can freely modify an object's internals, the object can enter an invalid state and the cause is nearly impossible to trace. Encapsulation creates a contract: "modify this data only through these methods" — reducing bugs.

> Encapsulation = hide implementation details + provide a safe interface

Python does not have `private` keywords like Java. Instead, it uses underscore (`_`) conventions and the `property` decorator. Understanding these conventions lets you read Python ecosystem code naturally.

## Concept Overview

> Python access control conventions

```text
Naming Pattern           Access Level
─────────────────────────────────────
name                    public — accessible by anyone
_name                   protected — internal / subclass use (convention)
__name                  private — name mangling applied (_Class__name)
__name__                dunder — Python internal protocol
```

## Key Concepts

| Term | Description |
|------|-------------|
| Encapsulation | Bundling data and methods together while hiding internal implementation |
| Information hiding | Preventing direct access to internal state from outside |
| Property | Python built-in decorator that controls attribute access via methods |
| Name mangling | Transforms `__name` into `_ClassName__name` |
| Getter/Setter | Methods called when reading or setting an attribute value |

## Before / After

Comparing bank account balance management.

```python
# before: direct access — invalid state possible
class BankAccount:
    def __init__(self, balance):
        self.balance = balance

account = BankAccount(1000)
account.balance = -500  # negative balance allowed — bug
```

```python
# after: property protection — validation guaranteed
class BankAccount:
    def __init__(self, balance: int) -> None:
        self._balance = balance  # protected

    @property
    def balance(self) -> int:
        return self._balance

    def deposit(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self._balance += amount

    def withdraw(self, amount: int) -> None:
        if amount > self._balance:
            raise ValueError("Insufficient balance")
        self._balance -= amount

account = BankAccount(1000)
account.deposit(500)    # 1500
account.withdraw(200)   # 1300
# account.balance = -500  # AttributeError — no setter defined
```

## Hands-On Steps

### Step 1: Understanding Underscore Conventions

```python
class Employee:
    def __init__(self, name: str, salary: int) -> None:
        self.name = name           # public
        self._department = "Unassigned"  # protected (convention)
        self.__salary = salary      # private (name mangling)

    def get_salary(self) -> int:
        return self.__salary

emp = Employee("Kim", 5000)
print(emp.name)            # Kim
print(emp._department)     # Unassigned (accessible but discouraged)
# print(emp.__salary)      # AttributeError
print(emp._Employee__salary)  # 5000 — mangled name access (not recommended)
print(emp.get_salary())    # 5000
```

### Step 2: Property Basics

```python
class Circle:
    def __init__(self, radius: float) -> None:
        self._radius = radius

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        if value <= 0:
            raise ValueError(f"Radius must be positive: {value}")
        self._radius = value

    @property
    def area(self) -> float:
        """Read-only computed property"""
        import math
        return math.pi * self._radius ** 2

c = Circle(5)
print(c.radius)   # 5
print(c.area)     # 78.539...

c.radius = 10
print(c.area)     # 314.159...

# c.radius = -1   # ValueError
# c.area = 100    # AttributeError — no setter
```

### Step 3: Chained Validation

```python
class User:
    def __init__(self, name: str, age: int, email: str) -> None:
        self.name = name    # triggers setter validation
        self.age = age
        self.email = email

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not value.strip():
            raise ValueError("Name cannot be empty")
        self._name = value.strip()

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int) -> None:
        if not 0 <= value <= 150:
            raise ValueError(f"Invalid age: {value}")
        self._age = value

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        if "@" not in value:
            raise ValueError(f"Invalid email: {value}")
        self._email = value

user = User("Alice", 30, "alice@example.com")
print(user.name)   # Alice
user.age = 31      # OK
# user.age = -1    # ValueError
```

### Step 4: Read-Only Attributes

```python
class ImmutablePoint:
    def __init__(self, x: float, y: float) -> None:
        self._x = x
        self._y = y

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    def __repr__(self) -> str:
        return f"ImmutablePoint({self._x}, {self._y})"

p = ImmutablePoint(3, 4)
print(p.x, p.y)  # 3 4
# p.x = 10       # AttributeError — read-only
```

### Step 5: Encapsulation and Interface Separation

```python
class TemperatureSensor:
    """Hides internal implementation and exposes only converted values"""

    def __init__(self) -> None:
        self._raw_readings: list[float] = []

    def add_reading(self, celsius: float) -> None:
        self._raw_readings.append(celsius)

    @property
    def average_celsius(self) -> float:
        if not self._raw_readings:
            return 0.0
        return sum(self._raw_readings) / len(self._raw_readings)

    @property
    def average_fahrenheit(self) -> float:
        return self.average_celsius * 9 / 5 + 32

    @property
    def reading_count(self) -> int:
        return len(self._raw_readings)

sensor = TemperatureSensor()
sensor.add_reading(20.0)
sensor.add_reading(25.0)
sensor.add_reading(22.5)
print(f"{sensor.average_celsius:.1f}°C")     # 22.5°C
print(f"{sensor.average_fahrenheit:.1f}°F")   # 72.5°F
print(f"Readings: {sensor.reading_count}")     # Readings: 3
```

## What to Notice in This Code

- `@property` lets you access methods like attributes, keeping the interface clean
- Assigning `self.name = value` in `__init__` triggers the setter for validation
- Omitting the setter makes a property read-only
- Name mangling (`__`) prevents accidental access, not security

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|---------------------|-----|
| Making every attribute `__` private | Subclasses cannot access them | `_` convention is sufficient |
| Expensive computation in property | Every attribute access incurs cost | Move heavy computation into a method |
| Bypassing setter in `__init__` | Skips validation | Use `self.attr = value` to trigger setter in `__init__` |
| Treating name mangling as security | `_Class__name` is still accessible | It is a convention, not enforcement |
| Getter/setter with no logic | Java-style boilerplate | If no validation or computation, use a public attribute |

## Real-World Applications

- Pydantic's `@validator` provides field-level validation similar to property
- SQLAlchemy's `hybrid_property` works on both Python and SQL sides
- Django models use `@property` for computed fields
- Config classes expose environment variables as read-only properties
- API response objects hide internal structure and expose values via properties

## How Senior Engineers Think About This

In Python, encapsulation is a "contract," not "enforcement." Ignoring underscore conventions still works, but code that depends on internals breaks when libraries update.

The most common pattern in practice is "start with public attributes, convert to property when validation is needed." Python's property decorator makes this transition transparent to callers.

## Checklist

- [ ] I can explain the difference between `_` and `__` conventions
- [ ] I can implement getters and setters with `@property`
- [ ] I can create read-only attributes
- [ ] I can apply the setter-through-`__init__` validation pattern
- [ ] I can judge when encapsulation is needed and when it is overkill

## Exercises

1. Create a `Password` class that validates minimum 8 characters and at least one digit on set.
2. Build a `Rectangle` class with `width` and `height` as validated properties and `area` as a read-only computed property.
3. Implement a `Config` class with a freeze pattern: once set, values cannot be changed.

## Summary and Next Steps

Encapsulation protects an object's internal state and provides a safe interface. Python achieves this through underscore conventions and the property decorator. In the next article, we explore inheritance — extending existing classes with new functionality.

## Design Principle Violation Cases

| Violation | Symptom | Fix |
|---|---|---|
| Modifying `_balance` directly from outside | Negative balance, limit bypass | Read-only exposure + method control |
| Validation logic duplicated per controller | Missed policy changes | Unify into object methods |
| Using auto-generated getter/setter only | Equivalent to exposing fields without encapsulation | Express intent through domain behavior methods |

## Comparison: Public Fields vs Encapsulated Objects

| Aspect | Public Field-Centric | Encapsulated Object |
|---|---|---|
| Policy change response | Must modify call sites simultaneously | Converges to internal object modification |
| Regression risk | Many missed points | Change points limited |
| Debugging | Hard to grasp context from values alone | Traceable through method paths |

## Refactoring Procedure

1. Search all write paths and consolidate to a single point.
2. Hide field writes as private and replace with method calls.
3. Move validation rules inside methods.
4. Update existing call-site tests to behavior-based tests.

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

## Additional Comparison: Design Decision Matrix

| Situation | Recommended Structure | Choice to Avoid |
|---|---|---|
| Rules change frequently | Separate policy objects + injection | Accumulating hard-coded branches |
| State transitions are core | Method-based transition model | External direct field modification |
| Frequent external integrations | Port/adapter separation | Direct SDK calls from domain |
| Team onboarding needed | Maintain UML text and term glossary | Relying on implicit rules |

This matrix is not meant to fix "the right design." Its purpose is to unify judgment language within a team to reduce code review time.

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

## Additional Code Example: Isolating Rule Changes in Methods

```python
class Membership:
    def __init__(self, level: str) -> None:
        self.level = level

    def discount_rate(self) -> int:
        if self.level == 'gold':
            return 20
        if self.level == 'silver':
            return 10
        return 0


class PriceCalculator:
    def __init__(self, membership: Membership) -> None:
        self.membership = membership

    def final_price(self, amount: int) -> int:
        rate = self.membership.discount_rate()
        return int(amount * (100 - rate) / 100)
```

In this structure, when membership policy changes, only the `Membership` implementation needs modification.


## Answering the Opening Questions

- **How should you interpret Python's public, `_protected`, and `__private` conventions?**
  - In the `Employee` example, `name` is a public attribute, `_department` signals internal implementation, and `__salary` uses name mangling to make accidental access harder. Python's access control is closer to a contract marker than a security barrier—the article even showed that `_Employee__salary` remains accessible.
- **What design advantage does `property` provide beyond simple getter/setter syntax?**
  - `Circle.radius` reads and writes like an attribute but internally enforces positive-value validation and `area` recalculation rules, while `TemperatureSensor` hides a raw measurement array and exposes only average Celsius and Fahrenheit. So `property` is a means to separate internal representation from external interface without proliferating method names—that is the core takeaway of this article.
- **Why does embedding validation in attribute access make object state management easier?**
  - In `User`, every path that assigns `name`, `age`, or `email` passes through setters, so blank names, negative ages, and malformed emails never persist inside the object. `BankAccount` also opens `balance` as read-only and concentrates limit and balance checks in `deposit()` and `withdraw()`, practically demonstrating that fewer state-change paths mean easier bug tracking.
<!-- toc:begin -->
## In this series

- [Object-Oriented Programming 101 (1/10): What Is Object-Oriented Programming?](./01-what-is-oop.md)
- [Object-Oriented Programming 101 (2/10): Classes and Instances](./02-classes-and-instances.md)
- **Encapsulation (current)**
- Inheritance (upcoming)
- Polymorphism (upcoming)
- Abstraction (upcoming)
- Composition vs Inheritance (upcoming)
- SOLID Principles Basics (upcoming)
- OOP Design Example (upcoming)
- When to Avoid OOP (upcoming)

<!-- toc:end -->

## References

- [Python Official Docs — Property](https://docs.python.org/3/library/functions.html#property)
- [Real Python — Python Property](https://realpython.com/python-property/)
- [Fluent Python — Chapter 11: A Pythonic Object](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)
- [Effective Python — Item 44: Use Plain Attributes Instead of Setter and Getter Methods](https://effectivepython.com/)

Tags: Python, OOP, Encapsulation, Property, Information Hiding
