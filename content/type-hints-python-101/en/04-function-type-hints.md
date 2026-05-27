---
series: type-hints-python-101
episode: 4
title: "Type Hints in Python 101 (4/10): Function Type Hints"
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
  - Callable
  - Overload
  - Decorator
  - Function Signature
seo_description: Learn how to annotate functions as values with Callable, type *args/**kwargs, and use @overload for precise signatures.
last_reviewed: '2026-05-04'
---

# Type Hints in Python 101 (4/10): Function Type Hints

This is the 4th post in the Type Hints in Python 101 series.

> Type Hints in Python 101 Series (4/10)

**Key Question**: How do you annotate a parameter that accepts a function, or describe a decorator's type signature?

> Python treats functions as first-class objects. You can pass them as arguments, return them from other functions, and store them in variables. But how do you tell the type checker what kind of function is expected? `Callable` describes function signatures as types, `@overload` handles functions with multiple valid signatures, and `ParamSpec` preserves decorator signatures. This article covers these advanced function-level type hints.


![Type Hints in Python 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/type-hints-python-101/04/04-01-big-picture.en.png)
*Type Hints in Python 101 chapter 4 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Function Type Hints?
- Which signal should the example or diagram make visible for Function Type Hints?
- What failure should be prevented first when Function Type Hints reaches a real system?

## What You Will Learn

- `Callable[[ArgTypes], ReturnType]` for function-typed parameters
- Typing `*args` and `**kwargs`
- `@overload` for functions with multiple signatures
- `ParamSpec` and `Concatenate` for decorators

## Why It Matters

Higher-order functions — functions that take or return other functions — are fundamental to Python. Callbacks, decorators, event handlers, and strategy patterns all pass functions as values. Without `Callable`, the type checker cannot verify that the right kind of function is being passed, and decorator return types become `Any`.

> Callable = describing "what shape of function" a parameter expects.

This is especially critical for decorators, which are used everywhere in frameworks like FastAPI and Flask.

> Callable describes function types. @overload describes multiple valid call signatures. ParamSpec preserves the original function's signature through decorators.

```text
Callable[[int, str], bool]
    │       │   │      │
    │    arg types   return type
    │
    "A function that takes (int, str) and returns bool"

@overload
def parse(raw: str) -> dict: ...
def parse(raw: bytes) -> dict: ...
```

## Key Concepts

| Term | Description |
| --- | --- |
| Callable | Type hint for function-typed values: `Callable[[Args], Return]` |
| @overload | Decorator to define multiple valid signatures for one function |
| ParamSpec | Captures the full parameter list of a function for decorators |
| Concatenate | Adds parameters to a ParamSpec for decorator wrappers |
| TypeGuard | A return type that tells the type checker a boolean function narrows types |

## Before / After

**Before — Untyped callback:**

```python
def retry(func, attempts):
    for i in range(attempts):
        try:
            return func()
        except Exception:
            if i == attempts - 1:
                raise
```

**After — Typed callback:**

```python
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")

def retry(func: Callable[[], T], attempts: int) -> T:
    for i in range(attempts):
        try:
            return func()
        except Exception:
            if i == attempts - 1:
                raise
    raise RuntimeError("unreachable")
```

## Hands-On Steps

### Step 1: Callable for Function Parameters

```python
from collections.abc import Callable

def apply_operation(values: list[int], op: Callable[[int], int]) -> list[int]:
    return [op(v) for v in values]

def double(x: int) -> int:
    return x * 2

result = apply_operation([1, 2, 3], double)  # [2, 4, 6]
result = apply_operation([1, 2, 3], lambda x: x + 1)  # [2, 3, 4]
```

`Callable[[int], int]` means "a function that takes one `int` parameter and returns `int`."

### Step 2: Typing *args and **kwargs

```python
def log_call(*args: str, **kwargs: int) -> None:
    for arg in args:
        print(arg)        # arg: str
    for key, value in kwargs.items():
        print(f"{key}={value}")  # value: int

log_call("hello", "world", retries=3, timeout=30)
```

When you annotate `*args: str`, each individual argument is `str`. Similarly, `**kwargs: int` means each keyword argument value is `int`.

### Step 3: @overload for Multiple Signatures

```python
from typing import overload

@overload
def parse_value(raw: str) -> dict[str, str]: ...

@overload
def parse_value(raw: bytes) -> dict[str, bytes]: ...

def parse_value(raw: str | bytes) -> dict[str, str] | dict[str, bytes]:
    if isinstance(raw, str):
        return {"data": raw}
    return {b"data": raw}

text_result = parse_value("hello")    # dict[str, str]
bytes_result = parse_value(b"hello")  # dict[str, bytes]
```

`@overload` decorators define the possible call signatures. The implementation (without `@overload`) handles all cases. Only the overloaded signatures are visible to callers.

### Step 4: ParamSpec for Decorators

```python
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")

def log_calls(func: Callable[P, T]) -> Callable[P, T]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_calls
def add(a: int, b: int) -> int:
    return a + b

result = add(1, 2)  # Type checker knows: (int, int) -> int
```

`ParamSpec` captures the full parameter list. Without it, the decorator would erase the original function's type information.

### Step 5: Callable with No Arguments or Any Arguments

```python
from collections.abc import Callable
from typing import Any

# No arguments, returns str
factory: Callable[[], str] = lambda: "hello"

# Any arguments (use ... for untyped)
handler: Callable[..., None] = lambda *args, **kwargs: None
```

`Callable[[], str]` takes no arguments. `Callable[..., None]` accepts any arguments — use this sparingly, as it disables argument type checking.

## What to Notice in This Code

- `Callable` uses a list for argument types: `Callable[[int, str], bool]`
- `@overload` signatures must be followed by one non-overloaded implementation
- `ParamSpec` preserves the original function's parameter types through decorators
- `*args` and `**kwargs` annotations apply to each individual argument, not the tuple/dict

## 5 Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Using `Callable` without argument types | `Callable[..., int]` loses parameter safety | Specify argument types: `Callable[[str], int]` |
| Missing implementation after `@overload` | Type checker cannot find the real function | Add the undecorated implementation last |
| Decorator returns `Any` | Decorated function loses its type info | Use `ParamSpec` to preserve the signature |
| Annotating `*args: tuple[str, ...]` | Wrong — `*args: str` means each arg is str | Use the element type, not the container type |
| Overload with identical signatures | Redundant and confusing | Each overload must have a distinct input type |

## Real-World Applications

- FastAPI route decorators use `ParamSpec` to preserve endpoint signatures
- Event systems type callbacks as `Callable[[Event], None]` for type-safe subscriptions
- Retry decorators use `Callable[P, T]` to maintain the wrapped function's contract
- Strategy pattern implementations accept `Callable[[Data], Result]` for pluggable algorithms
- Middleware chains type each layer as `Callable[[Request], Response]`

## How Senior Engineers Think About This

Senior engineers invest in typing decorators correctly because decorators are used everywhere. A poorly typed decorator silently erases type information for every function it wraps, creating a cascade of `Any` types through the codebase. `ParamSpec` is not optional — it is the baseline for any decorator in a typed codebase.

They use `@overload` judiciously. It is powerful for functions that genuinely return different types based on input types, but overusing it makes code harder to read. If a function needs more than three overloads, the design likely needs simplification.

## Checklist

- [ ] Used `Callable[[ArgTypes], ReturnType]` for function-typed parameters
- [ ] Annotated `*args` and `**kwargs` with element types
- [ ] Applied `@overload` for functions with distinct input-output type relationships
- [ ] Used `ParamSpec` to preserve signatures in decorators
- [ ] Avoided `Callable[..., T]` when argument types are known

## Exercises

1. Write a `map_values(data: dict[str, int], transform: Callable[[int], float]) -> dict[str, float]` function. Test it with `lambda x: x * 1.1`.

2. Create a timing decorator using `ParamSpec` that prints execution time while preserving the decorated function's type signature. Verify with mypy.

3. Write an overloaded `serialize` function: `serialize(data: dict) -> str` and `serialize(data: list) -> str` with different formatting for each.

## Summary and Next Steps

`Callable` types function-valued parameters, `@overload` handles functions with multiple valid signatures, and `ParamSpec` preserves decorator type information. These tools are essential for typing higher-order functions, callbacks, and decorators — patterns that appear in virtually every Python framework.

In the next article, we will explore `TypedDict` and `dataclass` for typing structured data with named fields.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Function Type Hints?**
  - The article treats Function Type Hints as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Function Type Hints?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Function Type Hints reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Type Hints in Python 101 (1/10): What Are Python Type Hints?](./01-what-is-type-hint.md)
- [Type Hints in Python 101 (2/10): Basic Types and Collection Types](./02-basic-and-collection-types.md)
- [Type Hints in Python 101 (3/10): Optional and Union](./03-optional-and-union.md)
- **Function Type Hints (current)**
- TypedDict and dataclass (upcoming)
- Protocol and Structural Typing (upcoming)
- Understanding Generics (upcoming)
- Using mypy and pyright (upcoming)
- Pydantic and Type Hints (upcoming)
- Type Hint Best Practices (upcoming)

<!-- toc:end -->

## References

- [Python docs — typing.Callable](https://docs.python.org/3/library/typing.html#typing.Callable)
- [Python docs — typing.overload](https://docs.python.org/3/library/typing.html#typing.overload)
- [PEP 612 — Parameter Specification Variables](https://peps.python.org/pep-0612/)
- [mypy docs — Callable types](https://mypy.readthedocs.io/en/stable/kinds_of_types.html#callable-types-and-lambdas)

Tags: Python, Type Hints, Callable, Overload, Decorator, Function Signature
