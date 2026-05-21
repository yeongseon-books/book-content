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

This is post 2 in the Object-Oriented Programming 101 series.

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

## Answering the Opening Questions

- **What boundary should you inspect first when applying Classes and Instances?**
  - The article treats Classes and Instances as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Classes and Instances?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Classes and Instances reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

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
