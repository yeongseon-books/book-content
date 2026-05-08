
# SOLID Principles Basics

> Object-Oriented Programming 101 Series (8/10)

<!-- a-grade-intro:begin -->

**Key Question**: What principles should you follow to design classes that are resilient to change and flexible for extension?

> SOLID is a set of five core principles for object-oriented design. This article walks through Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion — each with Python code examples.

<!-- a-grade-intro:end -->

## What You Will Learn

- The definition and purpose of all five SOLID principles
- Violation examples and improved code for each principle
- Practical approaches to applying SOLID in Python
- Relationships and trade-offs between the principles

## Why It Matters

You spend far more time maintaining code than writing it. SOLID principles guide you toward "code that is easy to change." The goal: modifying one place does not break another, and adding features requires minimal changes to existing code.

> SOLID = five principles for designs that are resilient to change and flexible for extension

You do not need to apply every principle perfectly from the start. Apply them when problems emerge as the code grows.

## Concept Overview

> SOLID five principles summary

```
S — Single Responsibility    One class changes for only one reason
O — Open/Closed             Open for extension, closed for modification
L — Liskov Substitution     Children must be substitutable for parents
I — Interface Segregation   Many small interfaces over one large interface
D — Dependency Inversion    Depend on abstractions, not concretions
```

## Key Concepts

| Term | Description |
|------|-------------|
| Single Responsibility (SRP) | A class should have only one responsibility |
| Open/Closed (OCP) | Extend functionality without modifying existing code |
| Liskov Substitution (LSP) | Child classes must be substitutable for parent classes |
| Interface Segregation (ISP) | Do not depend on methods you do not use |
| Dependency Inversion (DIP) | High-level modules should depend on abstractions, not low-level modules |

## Before / After

Comparing SRP violation and improvement.

```python
# before: SRP violation — one class with multiple responsibilities
class UserManager:
    def create_user(self, name: str) -> dict:
        user = {"name": name}
        # DB save logic
        # email send logic
        # log recording logic
        return user
```

```python
# after: SRP applied — each class has one responsibility
class UserRepository:
    def save(self, user: dict) -> None:
        print(f"DB save: {user}")

class EmailService:
    def send_welcome(self, name: str) -> None:
        print(f"Welcome email sent: {name}")

class UserService:
    def __init__(self, repo: UserRepository, email: EmailService) -> None:
        self._repo = repo
        self._email = email

    def create_user(self, name: str) -> dict:
        user = {"name": name}
        self._repo.save(user)
        self._email.send_welcome(name)
        return user
```

## Hands-On Steps

### Step 1: S — Single Responsibility Principle (SRP)

```python
# Violation: Report class handles both data processing and output
class Report:
    def __init__(self, data: list[dict]) -> None:
        self.data = data

    def calculate_total(self) -> int:
        return sum(item["amount"] for item in self.data)

    def to_html(self) -> str:  # output format change -> Report must change
        total = self.calculate_total()
        return f"<h1>Total: {total}</h1>"


# Improved: separate data processing from output
class SalesReport:
    def __init__(self, data: list[dict]) -> None:
        self.data = data

    def calculate_total(self) -> int:
        return sum(item["amount"] for item in self.data)


class ReportFormatter:
    def to_html(self, report: SalesReport) -> str:
        return f"<h1>Total: {report.calculate_total()}</h1>"

    def to_text(self, report: SalesReport) -> str:
        return f"Total: {report.calculate_total()}"


data = [{"amount": 100}, {"amount": 200}]
report = SalesReport(data)
formatter = ReportFormatter()
print(formatter.to_html(report))  # <h1>Total: 300</h1>
print(formatter.to_text(report))  # Total: 300
```

### Step 2: O — Open/Closed Principle (OCP)

```python
from typing import Protocol


class Discount(Protocol):
    def apply(self, price: int) -> int: ...


class NoDiscount:
    def apply(self, price: int) -> int:
        return price

class PercentDiscount:
    def __init__(self, percent: int) -> None:
        self.percent = percent

    def apply(self, price: int) -> int:
        return price - (price * self.percent // 100)

class FixedDiscount:
    def __init__(self, amount: int) -> None:
        self.amount = amount

    def apply(self, price: int) -> int:
        return max(0, price - self.amount)


def calculate_price(price: int, discount: Discount) -> int:
    """Adding new discount types requires no changes to this function"""
    return discount.apply(price)


print(calculate_price(10000, NoDiscount()))           # 10000
print(calculate_price(10000, PercentDiscount(20)))     # 8000
print(calculate_price(10000, FixedDiscount(3000)))     # 7000
```

### Step 3: L — Liskov Substitution Principle (LSP)

```python
class Bird:
    def move(self) -> str:
        return "moving"

class FlyingBird(Bird):
    def move(self) -> str:
        return "flying"

class Penguin(Bird):
    def move(self) -> str:
        return "walking"


def make_bird_move(bird: Bird) -> None:
    print(bird.move())

# All subclasses can substitute for the parent
make_bird_move(FlyingBird())  # flying
make_bird_move(Penguin())     # walking
```

### Step 4: I — Interface Segregation Principle (ISP)

```python
from typing import Protocol


# Violation: all capabilities in one interface
# class Worker(Protocol):
#     def code(self) -> str: ...
#     def test(self) -> str: ...
#     def design(self) -> str: ...  # unnecessary for developers


# Improved: separated by role
class Coder(Protocol):
    def code(self) -> str: ...

class Tester(Protocol):
    def test(self) -> str: ...

class Designer(Protocol):
    def design(self) -> str: ...


class Developer:
    def code(self) -> str:
        return "Writing code"

    def test(self) -> str:
        return "Writing tests"


class UxDesigner:
    def design(self) -> str:
        return "Designing UI"


def assign_coding(worker: Coder) -> None:
    print(worker.code())

def assign_design(worker: Designer) -> None:
    print(worker.design())

assign_coding(Developer())    # Writing code
assign_design(UxDesigner())   # Designing UI
```

### Step 5: D — Dependency Inversion Principle (DIP)

```python
from typing import Protocol


class MessageSender(Protocol):
    def send(self, to: str, body: str) -> None: ...


class EmailSender:
    def send(self, to: str, body: str) -> None:
        print(f"Email -> {to}: {body}")

class SlackSender:
    def send(self, to: str, body: str) -> None:
        print(f"Slack -> {to}: {body}")


class NotificationService:
    """High-level module: depends on abstraction (Protocol), not concretions"""

    def __init__(self, sender: MessageSender) -> None:
        self._sender = sender

    def notify(self, user: str, message: str) -> None:
        self._sender.send(user, message)


# Notify via email
service = NotificationService(EmailSender())
service.notify("kim@example.com", "Deploy complete")

# Switch to Slack — no changes to NotificationService
service = NotificationService(SlackSender())
service.notify("#deploy", "Deploy complete")
```

## What to Notice in This Code

- SRP keeps classes small by limiting each to a single reason for change
- OCP lets you add new features without modifying existing code
- LSP ensures children safely substitute for parents in inheritance hierarchies
- DIP is naturally implemented through Protocol and dependency injection

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|---------------------|-----|
| Applying all principles from the start | Over-abstraction adds complexity | Apply incrementally as needed |
| Extreme SRP — too many tiny classes | Classes become too granular | Judge by "reason for change" |
| LSP violation — child throws exceptions | Cannot use as parent type | Consider composition instead |
| Ignoring ISP — monolithic interfaces | Forces unnecessary method implementations | Split Protocols by role |
| Ignoring DIP — depending on concrete classes | Hard to replace and test | Depend on abstractions and inject |

## Real-World Applications

- FastAPI's `Depends()` supports DIP at the framework level
- Django's settings module separates configuration following SRP
- Plugin systems extend functionality based on OCP
- REST API serialization/deserialization separates interfaces via ISP
- Test mocks replace concrete dependencies thanks to DIP

## How Senior Engineers Think About This

SOLID is a "guideline," not a "rule." You do not need to apply it to every piece of code. Apply it at the points where change becomes difficult as the code grows. The most practical principles are SRP and DIP.

For small projects, you do not need to think about SOLID. But when team projects exceed tens of thousands of lines, the quality gap between developers who understand SOLID and those who do not becomes strikingly clear.

## Checklist

- [ ] I can explain each of the five SOLID principles
- [ ] I can identify and improve SRP violations
- [ ] I can implement OCP using Protocol or ABC
- [ ] I can identify LSP violation cases
- [ ] I can apply DIP through dependency injection

## Exercises

1. Split an SRP-violating `OrderProcessor` class (order processing + payment + email) into three classes.
2. Apply OCP to design a `FileExporter` that supports new file formats (CSV, JSON, XML) without modifying existing code.
3. Apply DIP so that a `WeatherApp` can swap between different weather APIs (OpenWeather, WeatherAPI).

## Summary and Next Steps

SOLID principles are guidelines for designs that are resilient to change and flexible for extension. Rather than applying them perfectly from the start, it is more practical to apply them when needed as the code grows. In the next article, we apply SOLID and other OOP principles to a real-world design example.

- [What Is Object-Oriented Programming?](./01-what-is-oop.md)
- [Classes and Instances](./02-classes-and-instances.md)
- [Encapsulation](./03-encapsulation.md)
- [Inheritance](./04-inheritance.md)
- [Polymorphism](./05-polymorphism.md)
- [Abstraction](./06-abstraction.md)
- [Composition vs Inheritance](./07-composition-vs-inheritance.md)
- **SOLID Principles Basics (current)**
- [OOP Design Example](./09-oop-design-example.md)
- [When to Avoid OOP](./10-when-to-avoid-oop.md)
## References

- [Clean Architecture — Robert C. Martin](https://www.oreilly.com/library/view/clean-architecture/9780134494272/)
- [Real Python — SOLID Principles in Python](https://realpython.com/solid-principles-python/)
- [Agile Software Development — Robert C. Martin](https://www.oreilly.com/library/view/agile-software-development/0135974445/)
- [PEP 544 — Protocols: Structural subtyping](https://peps.python.org/pep-0544/)

Tags: Python, OOP, SOLID, Design Principles, Clean Code

---

© 2026 YeongseonBooks. All rights reserved.
