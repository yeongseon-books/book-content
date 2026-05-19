---
series: oop-101
episode: 7
title: Composition vs Inheritance
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
  - Composition
  - Inheritance
  - Design Patterns
seo_description: Compare composition and inheritance, learn when to use each, and apply delegation and dependency injection patterns.
last_reviewed: '2026-05-15'
---

# Composition vs Inheritance

This is post 7 in the Object-Oriented Programming 101 series.

> Object-Oriented Programming 101 Series (7/10)

<!-- a-grade-intro:begin -->

**Key Question**: When extending a class, should you choose inheritance or composition?

> "Favor composition over inheritance" is a core principle from the GoF Design Patterns. Inheritance suits is-a relationships; composition suits has-a relationships. This article examines the structural differences and practical selection criteria.

<!-- a-grade-intro:end -->

## What You Will Learn

- The structural difference between inheritance (is-a) and composition (has-a)
- Why composition is more flexible than inheritance
- The delegation pattern
- Practical criteria for choosing between inheritance and composition

## Why It Matters

Inheritance creates tight coupling with the parent class. When the parent's internal implementation changes, child classes can break. Composition "contains" objects, so it does not depend on internal implementations and allows runtime replacement.

> Inheritance = compile-time coupling, Composition = runtime flexibility

Misused inheritance is a leading cause of increasing complexity during modifications. Always ask: "Is this relationship really is-a?"

## Concept Overview

> Inheritance vs Composition

```text
Inheritance (is-a)                Composition (has-a)
┌─────────────┐               ┌─────────────┐
│ Parent class │               │ Car         │
└──────┬──────┘               │  ├─ Engine  │
       │                      │  ├─ Wheel   │
┌──────┴──────┐               │  └─ GPS     │
│ Child class  │               └─────────────┘
└─────────────┘
Tight coupling                 Loose coupling
```

![Concept Overview](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/07/07-01-concept-overview.en.png)
*The composition-versus-inheritance decision starts with substitutability and change radius, not with how much code you can reuse.*

## Key Concepts

| Term | Description |
|------|-------------|
| Composition | An object contains other objects as attributes |
| Delegation | A pattern that forwards requests to an internal object |
| is-a relationship | "The child is a kind of parent" — suits inheritance |
| has-a relationship | "This object has that object" — suits composition |
| Dependency injection (DI) | A composition pattern where dependencies are passed from outside |

## Before / After

Comparing approaches to adding logging functionality.

```python
# before: logging via inheritance — multiple inheritance needed
class Logger:
    def log(self, msg: str) -> None:
        print(f"[LOG] {msg}")

class UserService(Logger):  # UserService is-a Logger? No.
    def create_user(self, name: str) -> None:
        self.log(f"Creating user: {name}")
```

```python
# after: logging via composition — natural has-a relationship
class Logger:
    def log(self, msg: str) -> None:
        print(f"[LOG] {msg}")

class UserService:
    def __init__(self, logger: Logger) -> None:
        self._logger = logger  # has-a relationship

    def create_user(self, name: str) -> None:
        self._logger.log(f"Creating user: {name}")
```

## Hands-On Steps

### Step 1: Composition Basics — Assembling a Car

```python
class Engine:
    def __init__(self, horsepower: int) -> None:
        self.horsepower = horsepower
        self.running = False

    def start(self) -> str:
        self.running = True
        return f"{self.horsepower}hp engine started"

    def stop(self) -> str:
        self.running = False
        return "Engine stopped"


class GPS:
    def navigate(self, destination: str) -> str:
        return f"Navigating to {destination}"


class Car:
    def __init__(self, engine: Engine, gps: GPS) -> None:
        self._engine = engine
        self._gps = gps

    def drive(self, destination: str) -> None:
        print(self._engine.start())
        print(self._gps.navigate(destination))

    def park(self) -> None:
        print(self._engine.stop())


car = Car(Engine(200), GPS())
car.drive("downtown")
# 200hp engine started
# Navigating to downtown
car.park()
# Engine stopped
```

### Step 2: Delegation Pattern

```python
class Printer:
    def print_document(self, content: str) -> None:
        print(f"Printing: {content}")

class Scanner:
    def scan(self) -> str:
        return "Scan complete"

class Fax:
    def send_fax(self, number: str, content: str) -> None:
        print(f"Faxing to {number}: {content}")


class MultiFunctionDevice:
    """Composition + delegation: each function delegated to an internal object"""

    def __init__(self) -> None:
        self._printer = Printer()
        self._scanner = Scanner()
        self._fax = Fax()

    def print_document(self, content: str) -> None:
        self._printer.print_document(content)

    def scan(self) -> str:
        return self._scanner.scan()

    def send_fax(self, number: str, content: str) -> None:
        self._fax.send_fax(number, content)


mfd = MultiFunctionDevice()
mfd.print_document("Report")       # Printing: Report
print(mfd.scan())                   # Scan complete
mfd.send_fax("02-1234", "Contract")  # Faxing to 02-1234: Contract
```

### Step 3: Strategy Pattern — Runtime Replacement

```python
from typing import Protocol


class SortStrategy(Protocol):
    def sort(self, data: list[int]) -> list[int]: ...


class BubbleSort:
    def sort(self, data: list[int]) -> list[int]:
        arr = data[:]
        for i in range(len(arr)):
            for j in range(len(arr) - 1 - i):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr


class QuickSort:
    def sort(self, data: list[int]) -> list[int]:
        return sorted(data)


class Sorter:
    def __init__(self, strategy: SortStrategy) -> None:
        self._strategy = strategy

    def set_strategy(self, strategy: SortStrategy) -> None:
        self._strategy = strategy

    def execute(self, data: list[int]) -> list[int]:
        return self._strategy.sort(data)


data = [5, 3, 8, 1, 9]
sorter = Sorter(BubbleSort())
print(sorter.execute(data))  # [1, 3, 5, 8, 9]

sorter.set_strategy(QuickSort())  # runtime replacement
print(sorter.execute(data))  # [1, 3, 5, 8, 9]
```

### Step 4: Dependency Injection

```python
from typing import Protocol


class Database(Protocol):
    def save(self, data: dict) -> None: ...
    def find(self, key: str) -> dict | None: ...


class InMemoryDB:
    def __init__(self) -> None:
        self._store: dict[str, dict] = {}

    def save(self, data: dict) -> None:
        self._store[data["id"]] = data

    def find(self, key: str) -> dict | None:
        return self._store.get(key)


class UserRepository:
    def __init__(self, db: Database) -> None:
        self._db = db  # injected from outside

    def create(self, user_id: str, name: str) -> None:
        self._db.save({"id": user_id, "name": name})

    def get(self, user_id: str) -> dict | None:
        return self._db.find(user_id)


db = InMemoryDB()
repo = UserRepository(db)
repo.create("u1", "Kim")
print(repo.get("u1"))  # {'id': 'u1', 'name': 'Kim'}
```

### Step 5: When Inheritance Is Appropriate

```python
class HttpError(Exception):
    """HTTP error base class — inheritance is appropriate for is-a relationships"""

    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code

class NotFoundError(HttpError):
    def __init__(self, resource: str) -> None:
        super().__init__(404, f"{resource} not found")

class UnauthorizedError(HttpError):
    def __init__(self) -> None:
        super().__init__(401, "Authentication required")


try:
    raise NotFoundError("User")
except HttpError as e:
    print(f"[{e.status_code}] {e}")
# [404] User not found
```

## What to Notice in This Code

- Composition allows replacing internal objects, providing high runtime flexibility
- Dependency injection makes it easy to substitute mock objects during testing
- The strategy pattern is a classic use of composition for runtime algorithm replacement
- The Exception hierarchy is a good example of inheritance where is-a is clear

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|---------------------|-----|
| Using inheritance for has-a relationships | "Car is-a Engine" does not hold | Switch to composition |
| Inheriting only for code reuse | Creates meaningless hierarchies | Use composition or utility functions |
| Exposing composed objects directly | Breaks encapsulation | Wrap with delegation methods |
| Creating dependencies internally | Hard to test and replace | Inject via constructor |
| Converting all inheritance to composition | Some cases like Exception suit inheritance | Use inheritance when is-a is clear |

## Real-World Applications

- FastAPI's `Depends()` is a composition pattern based on dependency injection
- Django's CBVs combine functionality through mixin-based composition
- Logging, caching, and auth are separated as cross-cutting concerns via composition
- Tests inject InMemoryDB instead of real databases
- Microservices inject HTTP clients via composition

## How Senior Engineers Think About This

"Favor composition over inheritance" does not mean "never use inheritance." Exception hierarchies, Enum extensions, and ABC implementations are natural places for inheritance where is-a is clear.

The decision rule is simple: "Can a child object be used wherever a parent type is expected?" (Liskov Substitution Principle). If yes, use inheritance. If no, use composition.

## Failure Modes That Push Teams Back to Composition

| Failure mode | First symptom you notice | Refactoring direction |
|--------------|--------------------------|-----------------------|
| Editing the parent breaks multiple children at once | One "small" shared change causes unrelated test failures | Keep only the common contract and move variable behavior into strategies |
| One child accumulates exception rules | Overrides fill up with `if` branches and special cases | Extract that responsibility into an internal collaborator |
| Behavior must change at runtime | Config-driven branching grows faster than the hierarchy | Switch to constructor injection plus a strategy object |
| Parent initialization is too heavy for tests | Every child test must construct the whole parent dependency graph | Move assembly into a separate layer and inject only what is needed |

## Checklist

- [ ] I can distinguish is-a relationships from has-a relationships
- [ ] I can implement composition and the delegation pattern
- [ ] I can implement runtime behavior replacement with the strategy pattern
- [ ] I understand the purpose and implementation of dependency injection
- [ ] I can judge when inheritance is appropriate and when composition is better

## Exercises

1. Design a `NotificationService` using composition so that `EmailSender` and `SmsSender` are interchangeable.
2. Refactor an inheritance-based `AdminUser(User)` to use composition instead.
3. Build a `Compressor` class using the strategy pattern to swap between gzip, bzip2, and lzma algorithms.

## Summary and Next Steps

Composition provides loose coupling and runtime flexibility, making it more suitable than inheritance in most situations. Inheritance should be reserved for clear is-a relationships. In the next article, we explore SOLID principles — the fundamental guidelines for object-oriented design.

<!-- toc:begin -->
- [What Is Object-Oriented Programming?](./01-what-is-oop.md)
- [Classes and Instances](./02-classes-and-instances.md)
- [Encapsulation](./03-encapsulation.md)
- [Inheritance](./04-inheritance.md)
- [Polymorphism](./05-polymorphism.md)
- [Abstraction](./06-abstraction.md)
- **Composition vs Inheritance (current)**
- [SOLID Principles Basics](./08-solid-principles.md)
- [OOP Design Example](./09-oop-design-example.md)
- [When to Avoid OOP](./10-when-to-avoid-oop.md)
<!-- toc:end -->

## References

- [Design Patterns — GoF (Gang of Four)](https://www.oreilly.com/library/view/design-patterns-elements/0201633612/)
- [Real Python — Inheritance and Composition](https://realpython.com/inheritance-composition-python/)
- [Effective Python — Item 41: Consider Composing Functionality with Mix-in Classes](https://effectivepython.com/)
- [Clean Architecture — Robert C. Martin](https://www.oreilly.com/library/view/clean-architecture/9780134494272/)

Tags: Python, OOP, Composition, Inheritance, Design Patterns
