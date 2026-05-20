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

## Questions to Keep in Mind

- What boundary should you inspect first when applying What Is Object-Oriented Programming??
- Which signal should the example or diagram make visible for What Is Object-Oriented Programming??
- What failure should be prevented first when What Is Object-Oriented Programming? reaches a real system?

## Big Picture

![Object-Oriented Programming 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/01/01-01-big-picture.en.png)

*Object-Oriented Programming 101 chapter 1 flow overview*

This picture places What Is Object-Oriented Programming? inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of What Is Object-Oriented Programming? is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

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

## Answering the Opening Questions

- **What boundary should you inspect first when applying What Is Object-Oriented Programming??**
  - The article treats What Is Object-Oriented Programming? as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for What Is Object-Oriented Programming??**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when What Is Object-Oriented Programming? reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

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
