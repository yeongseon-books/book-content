---
series: type-hints-python-101
episode: 6
title: "Type Hints in Python 101 (6/10): Protocol and Structural Typing"
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
  - Type Hints
  - Protocol
  - Structural Typing
  - Duck Typing
  - Interface
seo_description: Define interfaces without inheritance using Protocol and structural typing for flexible, duck-typing-friendly code.
last_reviewed: '2026-05-15'
---

# Type Hints in Python 101 (6/10): Protocol and Structural Typing

Python has always leaned on duck typing. If an object has `close()`, we close it. If it has `render()`, we render it. The friction starts when you want that flexibility to survive code review and CI, not just runtime.

This is post 6 in the Type Hints in Python 101 series. In this article, we will look at how `Protocol` captures “this shape is enough” without forcing inheritance, and how that changes interface design in real Python code.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Protocol and Structural Typing?
- Which signal should the example or diagram make visible for Protocol and Structural Typing?
- What failure should be prevented first when Protocol and Structural Typing reaches a real system?

## Big Picture

![Type Hints in Python 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/type-hints-python-101/06/06-01-concept-at-a-glance.en.png)

*Type Hints in Python 101 chapter 6 flow overview*

This picture places Protocol and Structural Typing inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Protocol and Structural Typing is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## What You Will Learn

- Protocol definition and structural typing principles
- Difference between ABC (nominal typing) and Protocol (structural typing)
- `@runtime_checkable` for runtime Protocol verification
- Practical Protocol design patterns

## Why It Matters

ABCs force inheritance, which creates tight coupling. If a function requires `Iterable`, every class must explicitly inherit from `Iterable` — even if it already has `__iter__`. Protocol eliminates this requirement. If the methods exist, the type is compatible. This mirrors how Python actually works at runtime and aligns static typing with the language's duck typing philosophy.

> Protocol = static duck typing.

Like Go interfaces and TypeScript structural types.

## Concept at a Glance

> Protocol defines a set of methods/attributes. Any class that has those methods is compatible — no inheritance required. This is structural typing.

```text
class Closeable(Protocol):     class FileHandler:
    def close(self) -> None:       def close(self) -> None:
        ...                            self.file.close()

        │                                    │
        └──── structural match ──────────────┘
              (no inheritance needed)
```

## Key Concepts

| Term | Description |
| --- | --- |
| Protocol | A class that defines required methods/attributes without requiring inheritance |
| Structural typing | Compatibility based on structure (methods/attributes), not inheritance |
| Nominal typing | Compatibility based on explicit class hierarchy (inheritance) |
| @runtime_checkable | Enables `isinstance()` checks against a Protocol |
| ABC | Abstract Base Class — nominal typing with required method overrides |

## Before / After

**Before — ABC requires inheritance:**

```python
from abc import ABC, abstractmethod

class Closeable(ABC):
    @abstractmethod
    def close(self) -> None: ...

class FileHandler(Closeable):  # Must inherit
    def close(self) -> None:
        print("closed")

def cleanup(resource: Closeable) -> None:
    resource.close()
```

**After — Protocol requires no inheritance:**

```python
from typing import Protocol

class Closeable(Protocol):
    def close(self) -> None: ...

class FileHandler:  # No inheritance needed
    def close(self) -> None:
        print("closed")

def cleanup(resource: Closeable) -> None:
    resource.close()

cleanup(FileHandler())  # OK — structural match
```

## Hands-On Steps

### Step 1: Define a Basic Protocol

```python
from typing import Protocol

class Renderable(Protocol):
    def render(self) -> str: ...

class HtmlWidget:
    def render(self) -> str:
        return "<div>Hello</div>"

class JsonResponse:
    def render(self) -> str:
        return '{"message": "hello"}'

def display(item: Renderable) -> None:
    print(item.render())

display(HtmlWidget())     # OK
display(JsonResponse())   # OK — both have render() -> str
```

Neither `HtmlWidget` nor `JsonResponse` inherits from `Renderable`. They are compatible because they have a matching `render` method.

### Step 2: Protocol with Attributes

```python
from typing import Protocol

class Named(Protocol):
    name: str

class User:
    def __init__(self, name: str) -> None:
        self.name = name

class Product:
    def __init__(self, name: str, price: int) -> None:
        self.name = name
        self.price = price

def greet(entity: Named) -> str:
    return f"Hello, {entity.name}!"

greet(User("Alice"))             # OK
greet(Product("Book", 25))       # OK — has name: str
```

### Step 3: @runtime_checkable

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Sizeable(Protocol):
    def __len__(self) -> int: ...

print(isinstance([1, 2, 3], Sizeable))   # True
print(isinstance("hello", Sizeable))     # True
print(isinstance(42, Sizeable))          # False
```

`@runtime_checkable` enables `isinstance()` checks. Note: it only checks method existence, not signatures.

### Step 4: Protocol Inheritance

```python
from typing import Protocol

class Readable(Protocol):
    def read(self) -> str: ...

class Writable(Protocol):
    def write(self, data: str) -> None: ...

class ReadWritable(Readable, Writable, Protocol):
    ...

class FileHandler:
    def read(self) -> str:
        return "data"

    def write(self, data: str) -> None:
        print(f"Writing: {data}")

def process(stream: ReadWritable) -> None:
    content = stream.read()
    stream.write(content.upper())

process(FileHandler())  # OK — has both read and write
```

### Step 5: Protocol vs. ABC Decision

```python
from abc import ABC, abstractmethod
from typing import Protocol

# Use ABC when: you own all implementing classes and want to enforce a contract
class BasePlugin(ABC):
    @abstractmethod
    def execute(self) -> None: ...

    def log(self) -> None:  # Shared implementation
        print(f"Running {self.__class__.__name__}")

# Use Protocol when: you want structural compatibility with external classes
class Executable(Protocol):
    def execute(self) -> None: ...
```

Use ABC when you provide shared implementation. Use Protocol when you define an interface for code you do not control.

## Migration Pattern for a Real Codebase

In a real repository, you usually do not start with a clean `Protocol` design. You inherit code that already has `S3Storage`, `LocalStorage`, `FakeStorage`, and a service layer that refers to those concrete classes directly. The safest first move is not to force everything under a new base class. It is to extract the smallest interface the service already depends on.

For example, if the upload flow only needs `save()` and `open()`, define a `StorageBackend` Protocol with just those methods and change the service signature first. Then run mypy or pyright to confirm that the existing implementations satisfy the contract without any inheritance changes.

```python
from typing import Protocol

class StorageBackend(Protocol):
    def save(self, path: str, data: bytes) -> None: ...
    def open(self, path: str) -> bytes: ...

def publish_report(storage: StorageBackend, path: str, data: bytes) -> bytes:
    storage.save(path, data)
    return storage.open(path)
```

This keeps the migration reviewable. Call sites move to the new contract first, while implementations only need to match the shape. If you start by designing one giant Protocol for every future use case, the contract becomes noisy and most implementations satisfy only part of it.

## First Checks When Compatibility Fails

- Verify that attribute types are not narrower than what the Protocol requires.
- Check return types, not just method names. Structural typing still fails on a mismatched signature.
- Do not confuse `@runtime_checkable` with full type validation. `isinstance()` only checks member presence.
- If one Protocol keeps growing, split it into smaller read-only and write-only contracts so implementations can satisfy exactly what they need.

## What to Notice in This Code

- Protocol classes define method signatures but no implementations
- Any class with matching methods is compatible — no inheritance required
- `@runtime_checkable` enables isinstance checks but only verifies method existence
- Protocol inheritance combines multiple Protocols into one

## 5 Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Adding implementation to Protocol | Protocol methods should be abstract | Use `...` (Ellipsis) as the body |
| Forgetting `Protocol` in multi-inheritance | Class becomes a regular class | Include `Protocol` in the bases |
| Relying on runtime_checkable for signatures | Only checks method names, not types | Use static type checking for full verification |
| Using Protocol where ABC fits better | No shared implementation possible | Use ABC when you need default methods |
| Over-fragmenting Protocols | Too many tiny Protocols | Group related methods into one Protocol |

## Real-World Applications

- Plugin systems that accept any object with an `execute()` method
- Testing with mock objects that structurally match the Protocol
- Adapter patterns where third-party classes satisfy your Protocol without modification
- Framework hooks that accept any callable with the right signature
- Repository patterns where different storage backends match the same Protocol

## How Senior Engineers Think About This

Senior engineers default to Protocol over ABC for public interfaces. Protocol is more flexible because it does not require the implementing class to know about the interface. This is especially valuable when working with third-party libraries — you can define a Protocol that their classes already satisfy without any modification.

They use ABC only when shared default implementations are needed. If the base class provides utility methods that subclasses inherit, ABC is the right tool. Otherwise, Protocol gives you the same static type safety with less coupling.

## Checklist

- [ ] Used Protocol for interfaces that external classes should satisfy
- [ ] Used ABC only when shared implementation is needed
- [ ] Applied `@runtime_checkable` only when isinstance checks are necessary
- [ ] Kept Protocol definitions focused on essential methods
- [ ] Verified Protocol compatibility with mypy

## Exercises

1. Define a `Serializable` Protocol with `to_json() -> str` and `from_json(data: str) -> Self` methods. Create two classes that satisfy it without inheritance.

2. Create a `Repository` Protocol with `get(id: int)`, `save(entity)`, and `delete(id: int)` methods. Write a service function that accepts any Repository.

3. Compare ABC and Protocol by implementing the same interface both ways. Test with mypy and note the differences in error messages and flexibility.

## Summary and Next Steps

Protocol enables structural typing in Python's static type system. Classes satisfy a Protocol by having the right methods — no inheritance required. This aligns with Python's duck typing philosophy while providing full static type checking. Use Protocol for flexible interfaces and ABC when shared implementation is needed.

In the next article, we will explore Generics — parameterizing types with type variables for reusable, type-safe code.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Protocol and Structural Typing?**
  - The article treats Protocol and Structural Typing as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Protocol and Structural Typing?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Protocol and Structural Typing reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Type Hints in Python 101 (1/10): What Are Python Type Hints?](./01-what-is-type-hint.md)
- [Type Hints in Python 101 (2/10): Basic Types and Collection Types](./02-basic-and-collection-types.md)
- [Type Hints in Python 101 (3/10): Optional and Union](./03-optional-and-union.md)
- [Type Hints in Python 101 (4/10): Function Type Hints](./04-function-type-hints.md)
- [Type Hints in Python 101 (5/10): TypedDict and dataclass](./05-typeddict-and-dataclass.md)
- **Protocol and Structural Typing (current)**
- Understanding Generics (upcoming)
- Using mypy and pyright (upcoming)
- Pydantic and Type Hints (upcoming)
- Type Hint Best Practices (upcoming)

<!-- toc:end -->

## References

- [Python docs — typing.Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol)
- [Python typing specification — Protocols](https://typing.python.org/en/latest/spec/protocol.html)
- [PEP 544 — Protocols: Structural subtyping](https://peps.python.org/pep-0544/)
- [Python docs — abc](https://docs.python.org/3/library/abc.html)
- [mypy docs — Protocols and structural subtyping](https://mypy.readthedocs.io/en/stable/protocols.html)
- [Real Python — Structural Typing](https://realpython.com/python-protocol/)

Tags: Python, Type Hints, Protocol, Structural Typing, Duck Typing, Interface
