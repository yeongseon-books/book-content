---
series: oop-101
episode: 6
title: Abstraction
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
  - Abstraction
  - ABC
  - Interface
seo_description: Learn how to design abstract classes with Python ABC and define enforced interfaces using abstractmethod.
last_reviewed: '2026-05-04'
---

# Abstraction

This is post 6 in the Object-Oriented Programming 101 series.

> Object-Oriented Programming 101 Series (6/10)

<!-- a-grade-intro:begin -->

**Key Question**: How do you define a common interface that cannot be instantiated directly?

> Abstraction exposes only essential interfaces while hiding implementation details. Python's `abc` module lets you define abstract classes and abstract methods that force subclasses to provide implementations.

<!-- a-grade-intro:end -->

## What You Will Learn

- The purpose of abstraction and the role of abstract classes
- Using Python `abc.ABC` and `@abstractmethod`
- Abstract properties and abstract class methods
- Choosing between abstract classes and Protocol

## Why It Matters

When multiple developers build classes for different data sources (files, databases, APIs) without a shared interface, method names and signatures diverge. Abstract classes enforce a contract — "you must implement these methods" — at instantiation time.

> Abstract class = cannot instantiate + forces method implementation on subclasses

Protocol says "structurally matching is OK," while ABC says "you must explicitly inherit." For larger teams or framework design, ABC's explicitness reduces mistakes.

## Concept Overview

> Abstract class structure

```text
ABC (Abstract Base Class)
├── @abstractmethod read()     -> must implement
├── @abstractmethod write()    -> must implement
├── close()                    -> shared implementation (optional override)
│
├── FileStorage(ABC)
│   ├── read()  implemented
│   └── write() implemented
│
└── MemoryStorage(ABC)
    ├── read()  implemented
    └── write() implemented
```

## Key Concepts

| Term | Description |
|------|-------------|
| Abstract class | A class that cannot be instantiated and forces subclasses to implement methods |
| `@abstractmethod` | Marks a method that must be overridden in subclasses |
| ABC (Abstract Base Class) | The base class provided by Python's `abc` module |
| Concrete class | A class that implements all abstract methods and can be instantiated |
| Template method pattern | Defines the algorithm skeleton and delegates specific steps to subclasses |

## Before / After

Comparing data source interfaces.

```python
# before: no interface enforcement — method name mismatch risk
class FileStorage:
    def read_file(self, path):
        pass

class DbStorage:
    def fetch_data(self, query):  # different method name
        pass
```

```python
# after: ABC enforces the interface
from abc import ABC, abstractmethod

class Storage(ABC):
    @abstractmethod
    def read(self, key: str) -> str: ...

    @abstractmethod
    def write(self, key: str, data: str) -> None: ...

class FileStorage(Storage):
    def read(self, key: str) -> str:
        return f"Reading {key} from file"

    def write(self, key: str, data: str) -> None:
        print(f"Writing {key} to file: {data}")
```

## Hands-On Steps

### Step 1: Basic Abstract Class

```python
from abc import ABC, abstractmethod


class Animal(ABC):
    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def speak(self) -> str:
        """Return the animal's sound"""
        ...

    def describe(self) -> str:
        """Shared implementation — optional override"""
        return f"{self.name}: {self.speak()}"


class Dog(Animal):
    def speak(self) -> str:
        return "woof"

class Cat(Animal):
    def speak(self) -> str:
        return "meow"

dog = Dog("Buddy")
print(dog.describe())  # Buddy: woof

# animal = Animal("animal")  # TypeError: Can't instantiate abstract class
```

### Step 2: Abstract Properties

```python
from abc import ABC, abstractmethod


class Vehicle(ABC):
    @property
    @abstractmethod
    def fuel_type(self) -> str: ...

    @property
    @abstractmethod
    def max_speed(self) -> int: ...

    def specs(self) -> str:
        return f"Fuel: {self.fuel_type}, Max speed: {self.max_speed}km/h"


class ElectricCar(Vehicle):
    @property
    def fuel_type(self) -> str:
        return "electric"

    @property
    def max_speed(self) -> int:
        return 250


class GasCar(Vehicle):
    @property
    def fuel_type(self) -> str:
        return "gasoline"

    @property
    def max_speed(self) -> int:
        return 220


ev = ElectricCar()
gas = GasCar()
print(ev.specs())   # Fuel: electric, Max speed: 250km/h
print(gas.specs())  # Fuel: gasoline, Max speed: 220km/h
```

### Step 3: Template Method Pattern

```python
from abc import ABC, abstractmethod


class DataPipeline(ABC):
    """Data processing pipeline — skeleton fixed, steps delegated to subclasses"""

    def run(self) -> list[str]:
        raw = self.extract()
        cleaned = self.transform(raw)
        self.load(cleaned)
        return cleaned

    @abstractmethod
    def extract(self) -> list[str]: ...

    @abstractmethod
    def transform(self, data: list[str]) -> list[str]: ...

    @abstractmethod
    def load(self, data: list[str]) -> None: ...


class CsvPipeline(DataPipeline):
    def extract(self) -> list[str]:
        return ["  Alice,30  ", "  Bob,25  ", "  Charlie,35  "]

    def transform(self, data: list[str]) -> list[str]:
        return [row.strip() for row in data]

    def load(self, data: list[str]) -> None:
        for row in data:
            print(f"Saving: {row}")


pipeline = CsvPipeline()
result = pipeline.run()
# Saving: Alice,30
# Saving: Bob,25
# Saving: Charlie,35
print(result)  # ['Alice,30', 'Bob,25', 'Charlie,35']
```

### Step 4: ABC's register()

```python
from abc import ABC, abstractmethod


class Drawable(ABC):
    @abstractmethod
    def draw(self) -> str: ...


class ThirdPartyWidget:
    """External library class — cannot modify"""
    def draw(self) -> str:
        return "Widget rendered"


Drawable.register(ThirdPartyWidget)

widget = ThirdPartyWidget()
print(isinstance(widget, Drawable))  # True
print(widget.draw())                 # Widget rendered
```

### Step 5: ABC vs Protocol — When to Choose Which

```python
from abc import ABC, abstractmethod
from typing import Protocol


# ABC: explicit inheritance required — good for frameworks, team contracts
class Serializer(ABC):
    @abstractmethod
    def serialize(self, data: dict) -> str: ...

class JsonSerializer(Serializer):
    def serialize(self, data: dict) -> str:
        import json
        return json.dumps(data)


# Protocol: no inheritance needed — good for cross-library compatibility
class SerializerProto(Protocol):
    def serialize(self, data: dict) -> str: ...

class YamlSerializer:  # does not inherit Protocol
    def serialize(self, data: dict) -> str:
        return "\n".join(f"{k}: {v}" for k, v in data.items())


def save(serializer: SerializerProto, data: dict) -> None:
    print(serializer.serialize(data))

save(JsonSerializer(), {"name": "Kim"})  # {"name": "Kim"}
save(YamlSerializer(), {"name": "Kim"})  # name: Kim
```

## What to Notice in This Code

- Failing to implement an abstract method raises `TypeError` at instantiation
- The template method pattern places the algorithm skeleton in the parent and delegates steps to children
- `register()` adds an existing class to an ABC without modifying it
- ABC provides explicit contracts; Protocol provides structural compatibility — choose based on context

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|---------------------|-----|
| Leaving any abstract method unimplemented | TypeError at instantiation | IDEs highlight unimplemented methods |
| Putting too much implementation in ABC | Increases inheritance coupling | Include only shared utilities |
| Defining every interface as ABC | Forces unnecessary inheritance | Protocol is better for external compatibility |
| Using ABC without any `@abstractmethod` | Class can be instantiated, defeating the purpose | Define at least one abstract method |
| Using abstract classes for data storage | Abstract classes are for interface definition | Use dataclass or regular classes for data |

## Real-World Applications

- Python's `collections.abc` (Iterable, Sequence, Mapping) are ABCs
- Django's `View` class uses the template method pattern
- Plugin architectures define plugin interfaces with ABC
- Tests create mock classes inheriting ABC to guarantee implementation
- Data processing pipelines abstract Extract/Transform/Load steps with ABC

## How Senior Engineers Think About This

Abstract classes become more valuable as team size grows. For small projects, duck typing is sufficient. But when multiple developers each build their own implementations, ABC provides a clear contract: "you must implement this."

The Python ecosystem mixes ABC and Protocol based on context. Internal team code uses ABC; compatibility with external libraries favors Protocol.

## Checklist

- [ ] I can define abstract classes with ABC and `@abstractmethod`
- [ ] I can define abstract properties
- [ ] I can implement the template method pattern
- [ ] I can explain the difference between ABC and Protocol
- [ ] I can register existing classes with an ABC using `register()`

## Exercises

1. Define a `NotificationSender` ABC and implement `EmailSender`, `SmsSender`, and `SlackSender`.
2. Apply the template method pattern to a `ReportGenerator` ABC and create `HtmlReport` and `PdfReport`.
3. Inherit from `collections.abc.Sequence` to implement a custom sequence class.

## Summary and Next Steps

Abstraction manages complexity and enforces consistent interfaces. Using ABC and Protocol appropriately enables extensible and safe designs. In the next article, we compare composition and inheritance and explore when each approach is appropriate.

<!-- toc:begin -->
- [What Is Object-Oriented Programming?](./01-what-is-oop.md)
- [Classes and Instances](./02-classes-and-instances.md)
- [Encapsulation](./03-encapsulation.md)
- [Inheritance](./04-inheritance.md)
- [Polymorphism](./05-polymorphism.md)
- **Abstraction (current)**
- [Composition vs Inheritance](./07-composition-vs-inheritance.md)
- [SOLID Principles Basics](./08-solid-principles.md)
- [OOP Design Example](./09-oop-design-example.md)
- [When to Avoid OOP](./10-when-to-avoid-oop.md)
<!-- toc:end -->

## References

- [Python Official Docs — abc module](https://docs.python.org/3/library/abc.html)
- [Real Python — Abstract Base Classes](https://realpython.com/python-interface/)
- [Python collections.abc Docs](https://docs.python.org/3/library/collections.abc.html)
- [Fluent Python — Chapter 13: Interfaces, Protocols, and ABCs](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)

Tags: Python, OOP, Abstraction, ABC, Interface
