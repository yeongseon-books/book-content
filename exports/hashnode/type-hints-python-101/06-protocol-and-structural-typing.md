
# Protocol and Structural Typing

> Type Hints in Python 101 Series (6/10)

<!-- a-grade-intro:begin -->

**Key Question**: Can you define "this object must have these methods" without requiring inheritance?

> Python's duck typing says "if it walks like a duck and quacks like a duck, it is a duck." But traditional Abstract Base Classes (ABCs) require explicit inheritance, which breaks when you cannot modify the class — like third-party library classes. `Protocol` brings duck typing into the static type system. If a class has the right methods, it satisfies the Protocol — no inheritance needed. This article covers Protocol, its relationship to structural typing, and practical patterns.

<!-- a-grade-intro:end -->

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

- [What Are Python Type Hints?](./01-what-is-type-hint.md)
- [Basic Types and Collection Types](./02-basic-and-collection-types.md)
- [Optional and Union](./03-optional-and-union.md)
- [Function Type Hints](./04-function-type-hints.md)
- [TypedDict and dataclass](./05-typeddict-and-dataclass.md)
- **Protocol and Structural Typing (current)**
- [Understanding Generics](./07-generic.md)
- [Using mypy and pyright](./08-mypy-and-pyright.md)
- [Pydantic and Type Hints](./09-pydantic-and-type-hints.md)
- [Type Hint Best Practices](./10-type-hints-best-practices.md)
## References

- [Python docs — typing.Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol)
- [PEP 544 — Protocols: Structural subtyping](https://peps.python.org/pep-0544/)
- [mypy docs — Protocols and structural subtyping](https://mypy.readthedocs.io/en/stable/protocols.html)
- [Real Python — Structural Typing](https://realpython.com/python-protocol/)

Tags: Python, Type Hints, Protocol, Structural Typing, Duck Typing, Interface

---

© 2026 YeongseonBooks. All rights reserved.
