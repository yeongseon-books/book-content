---
series: oop-101
episode: 3
title: Encapsulation
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
  - Encapsulation
  - Property
  - Information Hiding
seo_description: Learn how Python implements encapsulation through naming conventions and the property decorator for controlled attribute access.
last_reviewed: '2026-05-04'
---

# Encapsulation

> Object-Oriented Programming 101 Series (3/10)

<!-- a-grade-intro:begin -->

**Key Question**: Why and how should you protect an object's internal data?

> Encapsulation shields an object's internal state from direct external modification, exposing it only through a controlled interface. Python has no enforced access control, but naming conventions and the property decorator provide effective encapsulation.

<!-- a-grade-intro:end -->

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

```
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

<!-- toc:begin -->
- [What Is Object-Oriented Programming?](./01-what-is-oop.md)
- [Classes and Instances](./02-classes-and-instances.md)
- **Encapsulation (current)**
- [Inheritance](./04-inheritance.md)
- [Polymorphism](./05-polymorphism.md)
- [Abstraction](./06-abstraction.md)
- [Composition vs Inheritance](./07-composition-vs-inheritance.md)
- [SOLID Principles Basics](./08-solid-principles.md)
- [OOP Design Example](./09-oop-design-example.md)
- [When to Avoid OOP](./10-when-to-avoid-oop.md)
<!-- toc:end -->

## References

- [Python Official Docs — Property](https://docs.python.org/3/library/functions.html#property)
- [Real Python — Python Property](https://realpython.com/python-property/)
- [Fluent Python — Chapter 11: A Pythonic Object](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)
- [Effective Python — Item 44: Use Plain Attributes Instead of Setter and Getter Methods](https://effectivepython.com/)
