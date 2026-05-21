---
series: type-hints-python-101
episode: 7
title: "Type Hints in Python 101 (7/10): Understanding Generics"
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
  - Generic
  - TypeVar
  - Type Parameters
  - Generic Programming
seo_description: Write reusable, type-safe code with TypeVar and Generic for functions and classes that work across multiple types.
last_reviewed: '2026-05-15'
---

# Type Hints in Python 101 (7/10): Understanding Generics

Reusable Python code often fails at exactly one point: you can make it accept many types, but you accidentally erase the relationship between the input type and the output type. `Any` makes the code flexible but blind.

This is post 7 in the Type Hints in Python 101 series. In this article, we will use `TypeVar` and `Generic` to preserve those type relationships, then look at where Generics help in real service code and where they become unnecessary abstraction.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Understanding Generics?
- Which signal should the example or diagram make visible for Understanding Generics?
- What failure should be prevented first when Understanding Generics reaches a real system?

## Big Picture

![Type Hints in Python 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/type-hints-python-101/07/07-01-concept-at-a-glance.en.png)

*Type Hints in Python 101 chapter 7 flow overview*

This picture places Understanding Generics inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## What You Will Learn

- TypeVar definition and usage
- Generic class construction
- Bounds and constraints for limiting type variables
- Python 3.12 type parameter syntax

## Why It Matters

Libraries and utility functions often need to work with multiple types. `Any` disables type checking entirely, and Union broadens the return type. Generic preserves the exact type relationship: "if you put in X, you get out X." This is how FastAPI's `Response[T]`, SQLAlchemy's `Mapped[T]`, and standard library containers like `list[T]` maintain type safety.

> Generic = parameterize types so the type checker can track them.

The same concept exists in Java, TypeScript, Rust, and Go.

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
# example: Python 3.12+ type parameter syntax
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

## Real Migration Pattern: Wrapper Types First

The biggest payoff from Generics in a real repository usually comes from wrapper types, not toy helper functions. Pagination responses, cache entries, `Repository[T]`, and `Result[T]` all repeat the same structure while varying only in the payload type.

The key question is simple: does the payload type flow through the API unchanged? If yes, Generic is usually the right fit. If the return type no longer depends on the input type, a concrete return type or a Protocol is often clearer.

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Page(Generic[T]):
    def __init__(self, items: list[T], total: int) -> None:
        self.items = items
        self.total = total

def first_item(page: Page[T]) -> T:
    return page.items[0]
```

With this contract, `Page[int]` produces `int`, and `Page[str]` produces `str`. That is the signal that the abstraction is earning its keep.

## First Checks When Inference Looks Wrong

- Confirm that one `TypeVar` is not trying to represent two unrelated roles in the same function.
- Remember that mutable containers like `list[T]` are invariant. `list[Child]` is not assignable to `list[Parent]`.
- If type parameters keep multiplying, split the API before you end up with `T`, `U`, `V`, and `W` everywhere.
- Do not use Generic as a prettier `Any`. If no relationship is preserved, a concrete type is often better.

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

## Answering the Opening Questions

- **What boundary should you inspect first when applying Understanding Generics?**
  - The article treats Understanding Generics as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Understanding Generics?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Understanding Generics reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Type Hints in Python 101 (1/10): What Are Python Type Hints?](./01-what-is-type-hint.md)
- [Type Hints in Python 101 (2/10): Basic Types and Collection Types](./02-basic-and-collection-types.md)
- [Type Hints in Python 101 (3/10): Optional and Union](./03-optional-and-union.md)
- [Type Hints in Python 101 (4/10): Function Type Hints](./04-function-type-hints.md)
- [Type Hints in Python 101 (5/10): TypedDict and dataclass](./05-typeddict-and-dataclass.md)
- [Type Hints in Python 101 (6/10): Protocol and Structural Typing](./06-protocol-and-structural-typing.md)
- **Understanding Generics (current)**
- Using mypy and pyright (upcoming)
- Pydantic and Type Hints (upcoming)
- Type Hint Best Practices (upcoming)

<!-- toc:end -->

## References

- [Python docs — typing.TypeVar](https://docs.python.org/3/library/typing.html#typing.TypeVar)
- [Python docs — typing.Generic](https://docs.python.org/3/library/typing.html#typing.Generic)
- [Python typing specification — Generics](https://typing.python.org/en/latest/spec/generics.html)
- [PEP 695 — Type Parameter Syntax](https://peps.python.org/pep-0695/)
- [mypy docs — Variance of generic types](https://mypy.readthedocs.io/en/stable/generics.html#variance-of-generic-types)
- [mypy docs — Generics](https://mypy.readthedocs.io/en/stable/generics.html)

Tags: Python, Type Hints, Generic, TypeVar, Type Parameters, Generic Programming
