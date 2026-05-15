---
series: oop-101
episode: 4
title: Inheritance
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
  - Inheritance
  - Method Overriding
  - super
seo_description: Learn Python inheritance basics including method overriding, super(), isinstance(), and multiple inheritance with MRO.
last_reviewed: '2026-05-04'
---

# Inheritance

This is post 4 in the Object-Oriented Programming 101 series.

> Object-Oriented Programming 101 Series (4/10)

<!-- a-grade-intro:begin -->

**Key Question**: How do you reuse an existing class's functionality while adding new capabilities?

> Inheritance lets a new class (child) receive attributes and methods from an existing class (parent). It reduces code duplication and expresses hierarchical relationships. This article covers single inheritance, method overriding, `super()`, and multiple inheritance with MRO.

<!-- a-grade-intro:end -->

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

<!-- toc:begin -->
- [What Is Object-Oriented Programming?](./01-what-is-oop.md)
- [Classes and Instances](./02-classes-and-instances.md)
- [Encapsulation](./03-encapsulation.md)
- **Inheritance (current)**
- [Polymorphism](./05-polymorphism.md)
- [Abstraction](./06-abstraction.md)
- [Composition vs Inheritance](./07-composition-vs-inheritance.md)
- [SOLID Principles Basics](./08-solid-principles.md)
- [OOP Design Example](./09-oop-design-example.md)
- [When to Avoid OOP](./10-when-to-avoid-oop.md)
<!-- toc:end -->

## References

- [Python Official Docs — Inheritance](https://docs.python.org/3/tutorial/classes.html#inheritance)
- [Real Python — Inheritance and Composition](https://realpython.com/inheritance-composition-python/)
- [Python MRO Official Docs](https://docs.python.org/3/library/stdtypes.html#class.__mro__)
- [Effective Python — Item 40: Initialize Parent Classes with super](https://effectivepython.com/)

Tags: Python, OOP, Inheritance, Method Overriding, super
