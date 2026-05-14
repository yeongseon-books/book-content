---
series: oop-101
episode: 5
title: Polymorphism
status: content-ready
targets:
  tistory: true
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

# Polymorphism

This is post 5 in the Object-Oriented Programming 101 series.

> Object-Oriented Programming 101 Series (5/10)

<!-- a-grade-intro:begin -->

**Key Question**: How do you handle objects of different types through a single interface?

> Polymorphism means that a method with the same name behaves differently depending on the object's type. Python's duck typing enables polymorphism without inheritance. This article covers inheritance-based polymorphism, duck typing, and Python 3.8+ Protocol.

<!-- a-grade-intro:end -->

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

```
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

## Summary and Next Steps

Polymorphism increases code flexibility by calling different implementations through a single interface. Python supports polymorphism through duck typing, inheritance, and Protocol. In the next article, we explore abstraction — enforcing common interfaces through abstract base classes.

<!-- toc:begin -->
- [What Is Object-Oriented Programming?](./01-what-is-oop.md)
- [Classes and Instances](./02-classes-and-instances.md)
- [Encapsulation](./03-encapsulation.md)
- [Inheritance](./04-inheritance.md)
- **Polymorphism (current)**
- [Abstraction](./06-abstraction.md)
- [Composition vs Inheritance](./07-composition-vs-inheritance.md)
- [SOLID Principles Basics](./08-solid-principles.md)
- [OOP Design Example](./09-oop-design-example.md)
- [When to Avoid OOP](./10-when-to-avoid-oop.md)
<!-- toc:end -->

## References

- [Python Official Docs — typing.Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol)
- [Real Python — Duck Typing in Python](https://realpython.com/duck-typing-python/)
- [PEP 544 — Protocols: Structural subtyping](https://peps.python.org/pep-0544/)
- [Fluent Python — Chapter 13: Interfaces, Protocols, and ABCs](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)

Tags: Python, OOP, Polymorphism, Duck Typing, Protocol
