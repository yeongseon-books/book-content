---
series: oop-101
episode: 4
title: "Object-Oriented Programming 101 (4/10): Inheritance"
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
  - Inheritance
  - Method Overriding
  - super
seo_description: Learn Python inheritance basics including method overriding, super(), isinstance(), and multiple inheritance with MRO.
last_reviewed: '2026-05-15'
---

# Object-Oriented Programming 101 (4/10): Inheritance

This is the 4th post in the Object-Oriented Programming 101 series.

> Object-Oriented Programming 101 Series (4/10)

**Key Question**: How do you reuse an existing class's functionality while adding new capabilities?

> Inheritance lets a new class (child) receive attributes and methods from an existing class (parent). It reduces code duplication and expresses hierarchical relationships. This article covers single inheritance, method overriding, `super()`, and multiple inheritance with MRO.


![Object-Oriented Programming 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/04/04-01-concept-overview.en.png)
*Object-Oriented Programming 101 chapter 4 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Inheritance?
- Which signal should the example or diagram make visible for Inheritance?
- What failure should be prevented first when Inheritance reaches a real system?

## What You Will Learn

- Basic structure and usage of single inheritance
- Method overriding and `super()` calls
- Using `isinstance()` and `issubclass()`
- Multiple inheritance and MRO (Method Resolution Order)

## Why It Matters

When building several classes with similar functionality, you repeat the same code without inheritance. Inheritance lets you write common logic once in a parent class and implement only the differences in child classes.

> Inheritance = "is-a" relationship: a child class is a kind of parent class

That said, inheritance creates tight coupling. Changes to a parent class affect all child classes. Knowing when inheritance is appropriate — and when it is not — is critical.

## Concept Overview

> Inheritance hierarchy

```text
Animal (parent class)
├── name, sound
├── speak()
├── __repr__()
│
├── Dog (child class)
│   └── speak() overridden
│   └── fetch() added
│
└── Cat (child class)
    └── speak() overridden
    └── purr() added
```

## Key Concepts

| Term | Description |
|------|-------------|
| Parent class (base) | The existing class that provides attributes and methods |
| Child class (derived) | A new class that inherits from and extends the parent |
| Overriding | Redefining a parent's method in the child class |
| `super()` | Built-in function that calls the parent class's method |
| MRO (Method Resolution Order) | The order in which methods are looked up in multiple inheritance |

## Before / After

Removing code duplication from shape classes.

```python
# before: no inheritance — duplicated code
class Circle:
    def __init__(self, name, color, radius):
        self.name = name
        self.color = color
        self.radius = radius

    def describe(self):
        return f"{self.color} {self.name}"

class Square:
    def __init__(self, name, color, side):
        self.name = name      # duplicated
        self.color = color    # duplicated
        self.side = side

    def describe(self):       # duplicated
        return f"{self.color} {self.name}"
```

```python
# after: inheritance consolidates common logic
class Shape:
    def __init__(self, name: str, color: str) -> None:
        self.name = name
        self.color = color

    def describe(self) -> str:
        return f"{self.color} {self.name}"

class Circle(Shape):
    def __init__(self, color: str, radius: float) -> None:
        super().__init__("circle", color)
        self.radius = radius

class Square(Shape):
    def __init__(self, color: str, side: float) -> None:
        super().__init__("square", color)
        self.side = side
```

## Hands-On Steps

### Step 1: Basic Inheritance

```python
class Animal:
    def __init__(self, name: str, sound: str) -> None:
        self.name = name
        self.sound = sound

    def speak(self) -> str:
        return f"{self.name}: {self.sound}"

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.name!r})"

class Dog(Animal):
    def __init__(self, name: str) -> None:
        super().__init__(name, "woof")

    def fetch(self, item: str) -> str:
        return f"{self.name} fetches the {item}"

class Cat(Animal):
    def __init__(self, name: str) -> None:
        super().__init__(name, "meow")

    def purr(self) -> str:
        return f"{self.name} is purring"

dog = Dog("Buddy")
cat = Cat("Whiskers")
print(dog.speak())   # Buddy: woof
print(cat.speak())   # Whiskers: meow
print(dog.fetch("ball"))  # Buddy fetches the ball
```

### Step 2: Method Overriding

```python
class Logger:
    def log(self, message: str) -> None:
        print(f"[LOG] {message}")

    def error(self, message: str) -> None:
        print(f"[ERROR] {message}")

class TimestampLogger(Logger):
    def log(self, message: str) -> None:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    def error(self, message: str) -> None:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] ERROR: {message}")

logger = TimestampLogger()
logger.log("Server started")    # [2026-05-04 12:00:00] Server started
logger.error("Connection failed")  # [2026-05-04 12:00:00] ERROR: Connection failed
```

### Step 3: Extending Parent Behavior with super()

```python
class Vehicle:
    def __init__(self, make: str, model: str, year: int) -> None:
        self.make = make
        self.model = model
        self.year = year

    def info(self) -> str:
        return f"{self.year} {self.make} {self.model}"

class ElectricVehicle(Vehicle):
    def __init__(self, make: str, model: str, year: int, battery_kwh: float) -> None:
        super().__init__(make, model, year)
        self.battery_kwh = battery_kwh

    def info(self) -> str:
        base = super().info()
        return f"{base} (Battery: {self.battery_kwh}kWh)"

ev = ElectricVehicle("Tesla", "Model 3", 2026, 75.0)
print(ev.info())  # 2026 Tesla Model 3 (Battery: 75.0kWh)
```

### Step 4: isinstance and issubclass

```python
dog = Dog("Buddy")
cat = Cat("Whiskers")

print(isinstance(dog, Dog))     # True
print(isinstance(dog, Animal))  # True — Dog is a kind of Animal
print(isinstance(dog, Cat))     # False

print(issubclass(Dog, Animal))  # True
print(issubclass(Cat, Animal))  # True
print(issubclass(Dog, Cat))     # False

animals: list[Animal] = [Dog("Buddy"), Cat("Whiskers"), Dog("Max")]
for animal in animals:
    print(animal.speak())
# Buddy: woof
# Whiskers: meow
# Max: woof
```

### Step 5: Multiple Inheritance and MRO

```python
class Flyable:
    def fly(self) -> str:
        return f"{self.name} is flying"

class Swimmable:
    def swim(self) -> str:
        return f"{self.name} is swimming"

class Duck(Animal, Flyable, Swimmable):
    def __init__(self, name: str) -> None:
        super().__init__(name, "quack")

duck = Duck("Donald")
print(duck.speak())  # Donald: quack
print(duck.fly())    # Donald is flying
print(duck.swim())   # Donald is swimming

# Check MRO
print(Duck.__mro__)
# (Duck, Animal, Flyable, Swimmable, object)
```

## What to Notice in This Code

- `super().__init__()` calls the parent class's initializer to set up attributes
- When overriding, `super().method()` preserves and extends the parent's original behavior
- `isinstance()` checks the entire inheritance hierarchy, supporting polymorphic code
- MRO is determined by the C3 linearization algorithm and can be inspected via `__mro__`

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|---------------------|-----|
| Forgetting `super().__init__()` | Parent attributes are not initialized | Always call it in the child's `__init__` |
| Inheritance depth beyond 4 levels | Hard to debug and understand | Limit to 2-3 levels; consider composition |
| Using inheritance for "has-a" relationships | A car is not a kind of engine | Use composition instead |
| Overusing multiple inheritance | MRO becomes complex; diamond problem emerges | Limit to mixin patterns |
| Depending on parent's internal implementation | Child breaks when parent changes | Use only the parent's public interface |

## Real-World Applications

- Django's `View` → `ListView` → `DetailView` hierarchy for web views
- Python's `Exception` hierarchy for defining custom errors
- unittest's `TestCase` for writing test classes via inheritance
- Custom logging handlers extending the built-in logging hierarchy
- ABC (Abstract Base Class) inheritance for defining interfaces

## How Senior Engineers Think About This

Inheritance is powerful but the most overused OOP feature. If you are not confident that the relationship is truly "is-a," choosing composition is the safer bet.

In practice, the trend favors composition over inheritance. Inheritance is mainly used at framework-provided extension points (Django views, exceptions), while business logic relies on composition and interfaces.

## Signals That Tell You to Reconsider Inheritance

| Signal | What usually breaks first | Refactoring move to try first |
|--------|---------------------------|-------------------------------|
| Each child overrides most of the parent method | The base class is no longer truly shared | Keep only the common interface and move variable behavior into composition or strategies |
| The parent keeps gaining option flags | The base class turns into `if self.kind == ...` logic | Thin the parent and extract changing behavior into separate collaborators |
| One child needs special initialization order | `super()` rules become fragile and hard to debug | Move creation concerns into a factory or assembly layer |
| Callers accept the parent type but still need child-specific checks | LSP is already failing in practice | Split the hierarchy or redefine the contract as smaller interfaces |

## Checklist

- [ ] I can extend a parent class using single inheritance
- [ ] I can call parent methods using `super()`
- [ ] I understand how method overriding works
- [ ] I can use `isinstance()` and `issubclass()`
- [ ] I can inspect and understand MRO in multiple inheritance

## Exercises

1. Create a `Shape` → `Rectangle` → `Square` hierarchy and implement an area method.
2. Build a `LogHandler` parent class with `FileHandler` and `ConsoleHandler` child classes.
3. Create `Serializable` and `Printable` mixins and use multiple inheritance in a `Document` class.

## Summary and Next Steps

Inheritance is useful for code reuse and expressing hierarchical relationships, but overuse increases complexity. In the next article, we explore polymorphism — implementing different behaviors through a single interface.

## LSP Violation Example and Correction

```python
class Bird:
    def fly(self) -> str:
        return 'flying'

class Penguin(Bird):
    def fly(self) -> str:
        raise RuntimeError('cannot fly')
```

This structure violates LSP because the subtype breaks the supertype's contract.

```python
from typing import Protocol

class Swimmable(Protocol):
    def swim(self) -> str:
        ...

class Flyable(Protocol):
    def fly(self) -> str:
        ...
```

Separating into capability-based interfaces avoids forced inheritance.

## Comparison: Inheritance vs Composition

| Criterion | Inheritance | Composition |
|---|---|---|
| Runtime replacement | Difficult | Easy |
| Coupling | Large hierarchy coupling | Interface coupling |
| Change impact | Large parent-change propagation | Localized to composed objects |
| Test substitution | Must prepare inheritance tree | Simple mock injection |

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

- **Inheritance can reduce code duplication, but why does it simultaneously create tight coupling?**
  - Lifting `name` and `color` into `Shape` clearly reduced duplication in `Circle` and `Square`, but children become bound to the parent's initialization approach and public interface. The `Penguin(Bird)` example and `ReportDeliveryService` refactoring later in the article showed that choosing inheritance based solely on shared code quickly leads back to LSP violations or mixed responsibilities.
- **How should overriding and `super()` be used together safely?**
  - `ElectricVehicle.info()` calls the parent's `info()` via `super()` first and then appends battery information—a safe pattern that maintains the existing contract while extending it. Conversely, if a child bypasses parent initialization or default behavior entirely, issues like missing `super().__init__()`, duplicate overrides, and initialization order confusion arise. The article recommended reusing parent functionality and adding only additional responsibilities.
- **Why are `isinstance()` and `issubclass()` important when reading inheritance relationships?**
  - The example where `Dog` receives a `speak()` call from within an `Animal` list demonstrates why `isinstance()` is needed to verify at runtime whether an object satisfies the parent contract. Additionally, checking `issubclass(Dog, Animal)` and `Duck.__mro__` instills the practical sense of verifying type relationships and method resolution order in code rather than just trusting the hierarchy.
<!-- toc:begin -->
## In this series

- [Object-Oriented Programming 101 (1/10): What Is Object-Oriented Programming?](./01-what-is-oop.md)
- [Object-Oriented Programming 101 (2/10): Classes and Instances](./02-classes-and-instances.md)
- [Object-Oriented Programming 101 (3/10): Encapsulation](./03-encapsulation.md)
- **Inheritance (current)**
- Polymorphism (upcoming)
- Abstraction (upcoming)
- Composition vs Inheritance (upcoming)
- SOLID Principles Basics (upcoming)
- OOP Design Example (upcoming)
- When to Avoid OOP (upcoming)

<!-- toc:end -->

## References

- [Python Official Docs — Inheritance](https://docs.python.org/3/tutorial/classes.html#inheritance)
- [Real Python — Inheritance and Composition](https://realpython.com/inheritance-composition-python/)
- [Python MRO Official Docs](https://docs.python.org/3/library/stdtypes.html#class.__mro__)
- [Effective Python — Item 40: Initialize Parent Classes with super](https://effectivepython.com/)

Tags: Python, OOP, Inheritance, Method Overriding, super
