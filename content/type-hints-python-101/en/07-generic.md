---
series: type-hints-python-101
episode: 7
title: Understanding Generics
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
  - Type Hints
  - Generic
  - TypeVar
  - Type Parameters
  - Generic Programming
seo_description: Write reusable, type-safe code with TypeVar and Generic for functions and classes that work across multiple types.
last_reviewed: '2026-05-04'
---

# Understanding Generics

> Type Hints in Python 101 Series (7/10)

<!-- a-grade-intro:begin -->

**Key Question**: Can a function accept multiple types while preserving the relationship between input and output types?

> Consider a function that returns the first element of a list. If you pass `list[int]`, you want `int` back. If you pass `list[str]`, you want `str` back. Using `Any` erases type information. Writing separate functions duplicates code. Generics solve this by letting you parameterize types — "the return type is the same as the element type of the input." This article covers TypeVar, Generic classes, bounds, constraints, and the Python 3.12 syntax.

<!-- a-grade-intro:end -->

## What You Will Learn

- TypeVar definition and usage
- Generic class construction
- Bounds and constraints for limiting type variables
- Python 3.12 type parameter syntax

## Why It Matters

Libraries and utility functions often need to work with multiple types. `Any` disables type checking entirely, and Union broadens the return type. Generic preserves the exact type relationship: "if you put in X, you get out X." This is how FastAPI's `Response[T]`, SQLAlchemy's `Mapped[T]`, and standard library containers like `list[T]` maintain type safety.

> Generic = parameterize types so the type checker can track them.

The same concept exists in Java, TypeScript, Rust, and Go.

## Concept at a Glance

> Generic declares a type variable and uses it in function or class signatures. The concrete type is determined at the call site.

```text
TypeVar("T") ──> function signature uses T
                     │
              call: f([1, 2, 3])
                     │
              T = int (resolved)
                     │
              return type = int
```

## Key Concepts

| Term | Description |
| --- | --- |
| TypeVar | Declares a type variable for generic functions and classes |
| Generic | Base class for classes parameterized by type variables |
| bound | Upper bound — TypeVar must be a subtype of the bound |
| constraint | TypeVar must be exactly one of the listed types |
| ParamSpec | Captures an entire function signature as a type variable |

## Before / After

**Before — Using Any:**

```python
from typing import Any


def first(items: list[Any]) -> Any:
    return items[0]


value = first([1, 2, 3])
# value: Any — type information lost
```

**After — Using Generic:**

```python
from typing import TypeVar

T = TypeVar("T")


def first(items: list[T]) -> T:
    return items[0]


value = first([1, 2, 3])
# value: int — exact type preserved
```

## Hands-On Steps

### Step 1: TypeVar Basics

```python
from typing import TypeVar

T = TypeVar("T")


def identity(value: T) -> T:
    """Returns the value unchanged."""
    return value


text = identity("hello")   # str
number = identity(42)       # int
```

The string argument to `TypeVar` must match the variable name: `T = TypeVar("T")`.

### Step 2: Generic Classes

```python
from typing import Generic, TypeVar

T = TypeVar("T")


class Stack(Generic[T]):
    """A type-safe stack data structure."""

    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

    def is_empty(self) -> bool:
        return len(self._items) == 0


int_stack: Stack[int] = Stack()
int_stack.push(1)
int_stack.push(2)
value = int_stack.pop()  # int
```

### Step 3: Bounds

```python
from typing import TypeVar


class Comparable:
    def __lt__(self, other: object) -> bool:
        return NotImplemented


C = TypeVar("C", bound=Comparable)


def find_min(items: list[C]) -> C:
    """Only accepts types that are subtypes of Comparable."""
    result = items[0]
    for item in items[1:]:
        if item < result:
            result = item
    return result
```

`bound=Comparable` means `C` must be a subtype of `Comparable`.

### Step 4: Constraints

```python
from typing import TypeVar

Number = TypeVar("Number", int, float)


def add(a: Number, b: Number) -> Number:
    """Only accepts int or float."""
    return a + b


add(1, 2)       # OK — int
add(1.0, 2.5)   # OK — float
# add("a", "b") # Error — str not allowed
```

Constraints list the exact allowed types. Unlike bounds, subtype relationships do not apply.

### Step 5: Python 3.12 Type Parameter Syntax

```python
# Python 3.12+
def first[T](items: list[T]) -> T:
    return items[0]


class Stack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()
```

Python 3.12 eliminates the need to declare `TypeVar` explicitly. The `[T]` syntax declares the type parameter inline.

## What to Notice in This Code

- TypeVar resolves to the same concrete type within a single function call
- Generic classes are parameterized at instantiation: `Stack[int]`
- Bounds use inheritance relationships; constraints use exact type matching
- Python 3.12 syntax removes the need for explicit TypeVar declarations

## 5 Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| TypeVar name mismatch | `T = TypeVar("U")` causes confusion | Match the variable name and string |
| Declaring TypeVar inside functions | Creates a new TypeVar per call | Declare at module level |
| Confusing bound and constraint | Different semantics — inheritance vs. exact match | bound = upper limit, constraint = allowed list |
| Not inheriting from Generic | Type parameters are ignored | Use `class MyClass(Generic[T]):` |
| Overusing Generics | Unnecessary complexity | Use Generics only when input-output type relationships exist |

## Real-World Applications

- FastAPI `Response[T]`: type-safe API response wrappers
- SQLAlchemy `Mapped[T]`: ORM column types expressed as Generics
- Pydantic Generic subclasses: pagination wrappers like `Page[T]`
- Cache decorators using `ParamSpec` to preserve wrapped function signatures
- Repository pattern: `Repository[T]` for type-safe CRUD across entities

## How Senior Engineers Think About This

Senior engineers use Generics where there is a clear type relationship between inputs and outputs. Not every function needs a TypeVar — only those where "the return type depends on the input type." Utility functions, container classes, and wrapper patterns are the sweet spot.

They avoid over-abstraction. A `Repository[T]` is useful. A `GenericProcessor[T, U, V, W]` with four type parameters probably needs a simpler design. Generics should make code clearer, not more obscure. If adding a TypeVar does not help the type checker catch real errors, it is not worth the complexity.

## Checklist

- [ ] Declared TypeVar at module level with matching name
- [ ] Inherited from `Generic[T]` for generic classes
- [ ] Used bound for subtype constraints, constraint for exact type lists
- [ ] Considered Python 3.12 syntax for new projects
- [ ] Avoided unnecessary Generics on simple functions

## Exercises

1. Write a `Pair[K, V]` class using `TypeVar` and `Generic` with `first: K` and `second: V` properties.

2. Create a `longest(a: T, b: T) -> T` function with `bound=Sized` that returns the longer of two objects.

3. Rewrite a Generic Queue class using Python 3.12 `[T]` syntax with `enqueue`, `dequeue`, and `peek` methods.

## Summary and Next Steps

Generics parameterize types so a single function or class works across multiple types while preserving type relationships. TypeVar declares type variables, Generic provides the base class, and bounds/constraints limit the allowed types. Python 3.12 simplifies the syntax further.

In the next article, we will cover mypy and pyright — the tools that actually verify all these type hints.

<!-- toc:begin -->
- [What Are Python Type Hints?](./01-what-is-type-hint.md)
- [Basic Types and Collection Types](./02-basic-and-collection-types.md)
- [Optional and Union](./03-optional-and-union.md)
- [Function Type Hints](./04-function-type-hints.md)
- [TypedDict and dataclass](./05-typeddict-and-dataclass.md)
- [Protocol and Structural Typing](./06-protocol-and-structural-typing.md)
- **Understanding Generics (current)**
- [Using mypy and pyright](./08-mypy-and-pyright.md)
- [Pydantic and Type Hints](./09-pydantic-and-type-hints.md)
- [Type Hint Best Practices](./10-type-hints-best-practices.md)
<!-- toc:end -->

## References

- [Python docs — typing.TypeVar](https://docs.python.org/3/library/typing.html#typing.TypeVar)
- [Python docs — typing.Generic](https://docs.python.org/3/library/typing.html#typing.Generic)
- [PEP 695 — Type Parameter Syntax](https://peps.python.org/pep-0695/)
- [mypy docs — Generics](https://mypy.readthedocs.io/en/stable/generics.html)

Tags: Python, Type Hints, Generic, TypeVar, Type Parameters, Generic Programming
