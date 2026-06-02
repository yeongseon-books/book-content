---
series: oop-101
episode: 1
title: "Object-Oriented Programming 101 (1/10): What Is Object-Oriented Programming?"
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
  - Object-Oriented
  - Programming Paradigm
  - Classes
seo_description: Understand the core idea of object-oriented programming and how it differs from procedural code with practical Python examples.
last_reviewed: '2026-05-15'
---

# Object-Oriented Programming 101 (1/10): What Is Object-Oriented Programming?

This is the first post in the Object-Oriented Programming 101 series.

> Object-Oriented Programming 101 Series (1/10)

**Key Question**: Why does organizing programs around "objects" make code easier to maintain?

> Programming paradigms define how we structure code. Procedural programming centers on functions; object-oriented programming bundles data and behavior into objects. This article explains what OOP is, why it emerged, and when it is the right choice.


![Object-Oriented Programming 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/01/01-01-big-picture.en.png)
*Object-Oriented Programming 101 chapter 1 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying What Is Object-Oriented Programming??
- Which signal should the example or diagram make visible for What Is Object-Oriented Programming??
- What failure should be prevented first when What Is Object-Oriented Programming? reaches a real system?

## What You Will Learn

- Types of programming paradigms and how they compare
- The core idea of OOP: binding data and behavior
- Structural differences between procedural and OOP code
- How OOP is used in Python

## Why It Matters

Small scripts run fine with functions alone. But when code grows beyond a few thousand lines, related data and logic scatter across many functions, and every change forces you to modify multiple places at once. OOP groups related data and behavior into a single unit to solve this problem.

> OOP = a programming style that bundles data and behavior into objects

Most modern languages — Python, Java, C++, C# — support OOP. Frameworks and libraries are built on OOP design, so without understanding the concept, even reading code becomes difficult.

## Concept Overview

> Procedural vs Object-Oriented

```text
Procedural                     Object-Oriented
┌────────────────────┐        ┌────────────────────┐
│ Function A         │        │ Object A           │
│ Function B         │        │  ├─ Data           │
│ Function C         │        │  └─ Methods        │
│                    │        ├────────────────────┤
│ Global Data        │        │ Object B           │
│  ├─ var 1          │        │  ├─ Data           │
│  └─ var 2          │        │  └─ Methods        │
└────────────────────┘        └────────────────────┘
```

## Key Concepts

| Term | Description |
|------|-------------|
| Class | A template (blueprint) for creating objects |
| Instance | An actual object created from a class |
| Attribute | Data held by an object |
| Method | A function that belongs to an object |
| Encapsulation | Bundling data and methods together while restricting external access |

## Before / After

Comparing user management logic.

```python
# before: procedural — data and functions are separate
users = []

def create_user(name, email):
    user = {"name": name, "email": email, "active": True}
    users.append(user)
    return user

def deactivate_user(user):
    user["active"] = False

def get_user_display(user):
    status = "active" if user["active"] else "inactive"
    return f"{user['name']} ({status})"
```

```python
# after: OOP — data and behavior live in one class
class User:
    def __init__(self, name: str, email: str) -> None:
        self.name = name
        self.email = email
        self.active = True

    def deactivate(self) -> None:
        self.active = False

    def display(self) -> str:
        status = "active" if self.active else "inactive"
        return f"{self.name} ({status})"
```

## Hands-On Steps

### Step 1: Creating Your First Class

```python
class Dog:
    """A simple Dog class"""

    def __init__(self, name: str, breed: str) -> None:
        self.name = name
        self.breed = breed

    def bark(self) -> str:
        return f"{self.name} says woof!"

    def __repr__(self) -> str:
        return f"Dog(name={self.name!r}, breed={self.breed!r})"

my_dog = Dog("Buddy", "Golden Retriever")
print(my_dog.bark())  # Buddy says woof!
print(my_dog)          # Dog(name='Buddy', breed='Golden Retriever')
```

### Step 2: Creating Multiple Instances

```python
dog1 = Dog("Buddy", "Golden Retriever")
dog2 = Dog("Charlie", "Poodle")
dog3 = Dog("Max", "Labrador")

dogs = [dog1, dog2, dog3]
for dog in dogs:
    print(f"{dog.name} ({dog.breed}): {dog.bark()}")
# Buddy (Golden Retriever): Buddy says woof!
# Charlie (Poodle): Charlie says woof!
# Max (Labrador): Max says woof!

print(dog1 is dog2)  # False — different instances
```

### Step 3: Procedural to OOP Refactoring

```python
# procedural version
def create_rect(width, height):
    return {"width": width, "height": height}

def area(rect):
    return rect["width"] * rect["height"]

def perimeter(rect):
    return 2 * (rect["width"] + rect["height"])

r = create_rect(5, 3)
print(area(r))       # 15
print(perimeter(r))  # 16
```

```python
# OOP version
class Rectangle:
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)

    def __repr__(self) -> str:
        return f"Rectangle({self.width}, {self.height})"

r = Rectangle(5, 3)
print(r.area())       # 15
print(r.perimeter())  # 16
```

### Step 4: Understanding self

```python
class Counter:
    def __init__(self) -> None:
        self.count = 0

    def increment(self) -> None:
        self.count += 1

    def reset(self) -> None:
        self.count = 0

    def value(self) -> int:
        return self.count

c1 = Counter()
c2 = Counter()
c1.increment()
c1.increment()
c2.increment()
print(c1.value())  # 2
print(c2.value())  # 1 — each instance is independent
```

### Step 5: Class Variables vs Instance Variables

```python
class Student:
    school = "Python Academy"  # class variable: shared by all instances

    def __init__(self, name: str, grade: int) -> None:
        self.name = name    # instance variable: unique per instance
        self.grade = grade

    def introduce(self) -> str:
        return f"{self.name} at {self.school}, grade {self.grade}"

s1 = Student("Alice", 3)
s2 = Student("Bob", 2)
print(s1.introduce())  # Alice at Python Academy, grade 3
print(s2.introduce())  # Bob at Python Academy, grade 2

Student.school = "Code Academy"  # changing class variable affects all instances
print(s1.introduce())  # Alice at Code Academy, grade 3
```

## What to Notice in This Code

- `__init__` is the initializer method called automatically when an instance is created
- `self` refers to the current instance and is the first parameter of every instance method
- Class variables are shared across all instances; instance variables are unique to each
- Defining `__repr__` makes objects display useful information during debugging

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|---------------------|-----|
| Forgetting self in `__init__` | Creates a local variable instead of an instance attribute | Always use `self.attr = value` |
| Mutable class variable | All instances share the same list or dict | Declare mutable objects as instance variables in `__init__` |
| Confusing class and instance | `Dog.bark()` raises TypeError | Always create an instance before calling methods |
| Wrapping everything in classes | Adds unnecessary complexity | Simple logic is fine as plain functions |
| Not defining `__repr__` | Prints `<__main__.Dog object>` during debugging | Define `__repr__` to show useful info |

## Real-World Applications

- Web frameworks like Django and Flask use class-based models
- REST APIs represent request/response data as classes
- Game development models characters and items as objects
- Data pipelines abstract each processing step as a class
- Test frameworks (pytest, unittest) support class-based tests

## How Senior Engineers Think About This

OOP is not a silver bullet. Introducing classes into small scripts often makes them harder to read. But as code grows and multiple functions share the same data, OOP becomes a natural solution.

In practice, the question "Should this be a class?" comes up often. The answer usually is: "Do the data and behavior change together?" If yes, bundling them in a class makes maintenance easier.

## Checklist

- [ ] I can explain the difference between procedural and OOP
- [ ] I understand the relationship between classes and instances
- [ ] I can explain the roles of `__init__` and `self`
- [ ] I can distinguish class variables from instance variables
- [ ] I can design and implement a simple class

## Exercises

1. Create a `BankAccount` class with deposit, withdraw, and balance methods.
2. Create a `Book` class, store multiple instances in a list, and write a function that searches by title.
3. Refactor a procedural calculator into an OOP version.

## Summary and Next Steps

OOP bundles data and behavior into a single unit to make code structure clear. In the next article, we will explore classes and instances in greater depth.

## Drawing Design Boundaries with Text UML

In OOP, the sense you need to develop before class syntax is boundaries. When boundaries are clear, you can track which data changes where, and predict the scope of modifications when requirements change.

```text
[OrderService]
  - place_order(cart, payment)
  - cancel_order(order_id)
        |
        | uses
        v
[Order]
  - id: str
  - lines: list[OrderLine]
  - status: OrderStatus
  - total_amount()
        |
        | has many
        v
[OrderLine]
  - product_id: str
  - quantity: int
  - unit_price: int
```

The key here is that `OrderService` coordinates flow while `Order` owns domain rules. If the service holds all calculations, rules scatter; if the entity knows external infrastructure, boundaries collapse.

## Refactoring from Procedural to Object Boundaries

The code below is easy to write quickly at first. The problem is that order amount calculation, coupon application, and state transition rules are mixed in one function.

```python
# before

def checkout(order_dict: dict, coupon: dict | None) -> dict:
    if order_dict['status'] != 'draft':
        raise ValueError('invalid status')

    total = 0
    for line in order_dict['lines']:
        total += line['quantity'] * line['unit_price']

    if coupon and coupon['type'] == 'percent':
        total = int(total * (100 - coupon['value']) / 100)

    order_dict['total'] = total
    order_dict['status'] = 'placed'
    return order_dict
```

```python
# after
from dataclasses import dataclass
from enum import Enum


class OrderStatus(str, Enum):
    DRAFT = 'draft'
    PLACED = 'placed'


@dataclass(frozen=True)
class OrderLine:
    product_id: str
    quantity: int
    unit_price: int

    def amount(self) -> int:
        return self.quantity * self.unit_price


class Order:
    def __init__(self, lines: list[OrderLine]) -> None:
        self.lines = lines
        self.status = OrderStatus.DRAFT
        self._discount_rate = 0

    def apply_percent_coupon(self, value: int) -> None:
        if not 0 <= value <= 100:
            raise ValueError('coupon percent must be 0..100')
        self._discount_rate = value

    def total_amount(self) -> int:
        subtotal = sum(line.amount() for line in self.lines)
        return int(subtotal * (100 - self._discount_rate) / 100)

    def place(self) -> None:
        if self.status != OrderStatus.DRAFT:
            raise ValueError('only draft can be placed')
        self.status = OrderStatus.PLACED
```

The biggest difference when moving from procedural to object-oriented code is not the calculation formulas but the location of rules. Coupon validation, state transition, and amount calculation gather inside `Order`, making the test unit clear.

## Violation Signals and Correction Methods

| Violation Signal | What Problem Arises | Correction Direction |
|---|---|---|
| Service function bloats beyond 200 lines | Must read entire function for policy changes | Move rules into domain classes |
| Same key strings (`'status'`, `'total'`) duplicated across files | Typos hide until runtime | Replace with typed attributes |
| Validation logic exists separately in API, service, and batch | Rule inconsistency causes incidents | Define single rule in object method |
| Tests focus on assembling input dictionaries | Verify shape rather than meaning | Switch to method tests that verify behavior |

## Comparison: Maintenance Cost of Function-Centric vs Object-Centric

| Perspective | Function-Centric Code | Object-Centric Code |
|---|---|---|
| Rule discovery | Must trace multiple functions and global constants | Focused inspection within class methods |
| Change impact | Must follow call graph broadly | Narrows to the object and its collaborators |
| Type safety | Dictionary key typos discovered late | Revealed early through attribute/method contracts |
| Onboarding | Understanding varies by file order | Learnable in domain-term units |

## Practical Check: When to Introduce Objects

- When the same data bundle changes together in three or more places, grouping into a class is advantageous.
- When state transitions matter, making rules explicit with enum + methods is safer.
- Separating I/O schema from domain rules reduces API changes propagating across the entire domain.
- Separating reasons for change takes priority over increasing class count.

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

- **How does OOP differ from procedural programming, and why did it emerge?**
  - This article first showed how data and functions scattered across a `users` list and standalone `create_user()`, `deactivate_user()` functions come together inside a `User` class. Then by refactoring `Order` to handle coupon application, state transitions, and total calculation through internal methods, we confirmed that OOP emerged not as syntactic decoration but as a way to gather change rules within a single boundary.
- **How should you understand the relationship between classes, instances, attributes, and methods?**
  - The `Dog("Buddy", "Golden Retriever")`, `Rectangle(5, 3)`, and `Counter()` examples help you understand a class as a blueprint and an instance as an individual object built from that blueprint. Attributes like `name`, `breed`, and `count` represent the state an object holds, while methods like `bark()`, `area()`, and `increment()` are operations that read or modify that state—a correspondence repeated throughout the article.
- **When do objects feel more natural than plain functions in a small script?**
  - For simple calculations like `area(rect)`, functions are sufficient. But the moment state transitions from `draft` to `placed` and coupon validation tags along—as with `Order`—objects become more natural. The `PaymentService` and `Invoice` examples later in the article also show that when related data and policies change together, drawing object boundaries makes testing and extension easier.
<!-- toc:begin -->
## In this series

- **What Is Object-Oriented Programming? (current)**
- Classes and Instances (upcoming)
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

- [Python Official Docs — Classes](https://docs.python.org/3/tutorial/classes.html)
- [Real Python — Object-Oriented Programming in Python](https://realpython.com/python3-object-oriented-programming/)
- [Clean Code — Robert C. Martin](https://www.oreilly.com/library/view/clean-code/9780136083238/)
- [Python Crash Course — Eric Matthes](https://nostarch.com/python-crash-course-3rd-edition)

Tags: Python, OOP, Object-Oriented, Programming Paradigm, Classes
