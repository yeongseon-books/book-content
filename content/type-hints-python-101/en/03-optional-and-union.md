---
series: type-hints-python-101
episode: 3
title: Optional and Union
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
  - Optional
  - Union
  - None Handling
  - Type Narrowing
seo_description: Learn how to use Optional and Union type hints in Python to handle nullable values and multi-type parameters safely.
last_reviewed: '2026-05-04'
---

# Optional and Union

This is post 3 in the Type Hints in Python 101 series.

> Type Hints in Python 101 Series (3/10)

<!-- a-grade-intro:begin -->

**Key Question**: How do you tell the type checker that a value might be `None` or could be one of several different types?

> In real-world code, functions often return `None` to signal "not found," and parameters accept multiple types for flexibility. Without explicit annotations, these patterns become invisible traps — a `None` return value that crashes three function calls later, or a parameter that silently accepts the wrong type. `Optional` and `Union` make these contracts explicit so the type checker can enforce them.

<!-- a-grade-intro:end -->

## What You Will Learn

- `Optional[T]` for values that might be `None`
- `Union[T1, T2]` for values that could be one of several types
- Python 3.10+ `X | Y` pipe syntax
- Type narrowing with `isinstance` and `is None` checks

## Why It Matters

`None`-related errors are among the most common runtime bugs in Python. A function returns `None` when no result is found, but the caller assumes it always returns a valid object and calls a method on it — `AttributeError`. Optional makes this possibility visible. Union handles the equally common case where a parameter legitimately accepts multiple types.

> Optional = "this might be None." Union = "this might be one of several types."

Both force the caller to handle all possibilities.

## Concept at a Glance

> Optional[T] is shorthand for Union[T, None]. Union[T1, T2] means the value is either T1 or T2. Type narrowing confirms which type it actually is.

```text
Optional[str]  =  str | None
                    │
            if value is not None:
                    │
            value: str  (narrowed)

Union[int, str]  =  int | str
                      │
            if isinstance(value, int):
                      │
            value: int  (narrowed)
```

## Key Concepts

| Term | Description |
| --- | --- |
| Optional[T] | Equivalent to `T \| None` — the value is either T or None |
| Union[T1, T2] | The value is one of the listed types |
| Pipe syntax | Python 3.10+ shorthand: `int \| str` instead of `Union[int, str]` |
| Type narrowing | Using checks like `isinstance` to confirm a specific type within a Union |
| Type guard | A function that tells the type checker a value is a specific type |

## Before / After

**Before — Hidden None danger:**

```python
def find_user(user_id: int) -> dict:
    if user_id == 0:
        return None  # type says dict, but returns None
    return {"id": user_id, "name": "Alice"}


user = find_user(0)
print(user["name"])  # Runtime: TypeError
```

**After — Explicit Optional:**

```python
def find_user(user_id: int) -> dict[str, str | int] | None:
    if user_id == 0:
        return None
    return {"id": user_id, "name": "Alice"}


user = find_user(0)
if user is not None:
    print(user["name"])  # Safe: type checker verified the None check
```

## Hands-On Steps

### Step 1: Optional for Nullable Returns

```python
from typing import Optional


def find_by_name(name: str) -> Optional[str]:
    """Returns the email if found, None otherwise."""
    users = {"Alice": "alice@example.com", "Bob": "bob@example.com"}
    return users.get(name)


email = find_by_name("Alice")
# email: Optional[str] — must check before using
if email is not None:
    print(email.upper())  # Safe
```

`Optional[str]` is exactly `str | None`. The type checker forces you to handle the `None` case.

### Step 2: Python 3.10+ Pipe Syntax

```python
# Python 3.10+: use | instead of Union/Optional
def find_by_name(name: str) -> str | None:
    users = {"Alice": "alice@example.com"}
    return users.get(name)


def process(value: int | str) -> str:
    return str(value)
```

The pipe syntax is cleaner and does not require imports from `typing`.

### Step 3: Union for Multi-Type Parameters

```python
def format_id(value: int | str) -> str:
    """Accepts both integer IDs and string UUIDs."""
    if isinstance(value, int):
        return f"ID-{value:06d}"
    return f"UUID-{value}"


print(format_id(42))          # ID-000042
print(format_id("abc-123"))   # UUID-abc-123
```

The `isinstance` check narrows the type. Inside the `if` block, the type checker knows `value` is `int`.

### Step 4: Type Narrowing Patterns

```python
def process(value: str | int | None) -> str:
    # Pattern 1: None check
    if value is None:
        return "default"

    # Pattern 2: isinstance check
    if isinstance(value, int):
        return str(value)

    # Pattern 3: After eliminating other types, only str remains
    return value.upper()


def safe_len(text: str | None) -> int:
    # Pattern 4: Early return for None
    if text is None:
        return 0
    return len(text)
```

### Step 5: Default Values with Optional

```python
def greet(name: str, title: str | None = None) -> str:
    """Title is optional with a default of None."""
    if title is not None:
        return f"Hello, {title} {name}!"
    return f"Hello, {name}!"


print(greet("Alice"))              # Hello, Alice!
print(greet("Alice", "Dr."))      # Hello, Dr. Alice!
```

When a parameter has a default of `None`, annotate it as `T | None` (or `Optional[T]`). This signals that callers can omit it.

## What to Notice in This Code

- `Optional[T]` is strictly equivalent to `T | None` — use whichever your team prefers
- Every `Optional` return value requires a `None` check before use
- `isinstance` and `is None` are the primary type narrowing mechanisms
- The pipe syntax (`|`) is available from Python 3.10+ and requires no imports

## 5 Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Not checking Optional before use | `AttributeError: NoneType has no attribute` | Always check `is not None` before accessing |
| Using `Optional` for required params | Misleading — suggests the param is optional | `Optional` means nullable, not "param is optional" |
| Broad `Union[int, str, float, bool, list]` | Too many types to handle | Simplify the API or use a common base |
| Forgetting narrowing in branches | Type checker reports errors inside branches | Add `isinstance` or `is None` checks |
| Nested `Optional[Optional[str]]` | Redundant — collapses to `str \| None` | Use `str \| None` directly |

## Real-World Applications

- Database query functions return `Optional[Model]` — not found means `None`
- Configuration lookups use `Optional[str]` with fallback defaults
- API clients return `Union[SuccessResponse, ErrorResponse]` for typed error handling
- Form parsing accepts `str | int` for fields that might be numeric strings
- Cache lookups return `T | None` to distinguish "not cached" from "cached as empty"

## How Senior Engineers Think About This

Senior engineers prefer `Optional` over sentinel values. Instead of returning `-1` or `""` to mean "not found," they return `None` with an explicit `Optional` annotation. This makes the absence of a value impossible to miss — the type checker will not let you use it without checking.

They also keep Union types narrow. A function that accepts `int | str | float | list | dict | None` is a design smell — it means the interface is poorly defined. If a function needs to accept many types, it often needs to be split into multiple functions with clear contracts.

## Checklist

- [ ] Used `Optional[T]` or `T | None` for nullable values
- [ ] Checked for `None` before using Optional values
- [ ] Used `isinstance` for type narrowing in Union branches
- [ ] Kept Union types to 2-3 types maximum
- [ ] Used Python 3.10+ pipe syntax where available

## Exercises

1. Write a function `safe_divide(a: float, b: float) -> float | None` that returns `None` when dividing by zero. Write a caller that handles both cases.

2. Create a `format_value(value: int | float | str) -> str` function that formats each type differently (integers with commas, floats with 2 decimals, strings in quotes). Use type narrowing.

3. Refactor a function that uses sentinel values (e.g., returning `""` for "not found") to use `Optional[str]` instead. Run mypy on both versions and compare the safety guarantees.

## Summary and Next Steps

`Optional[T]` annotates values that might be `None`, and `Union[T1, T2]` annotates values that could be one of several types. Type narrowing with `isinstance` and `is None` lets the type checker verify that you handle all cases. The Python 3.10+ pipe syntax (`X | Y`) provides a cleaner alternative to `Union` and `Optional` imports.

In the next article, we will explore function type hints in depth — including `Callable`, `*args`, `**kwargs`, and overload patterns.

<!-- toc:begin -->
- [What Are Python Type Hints?](./01-what-is-type-hint.md)
- [Basic Types and Collection Types](./02-basic-and-collection-types.md)
- **Optional and Union (current)**
- [Function Type Hints](./04-function-type-hints.md)
- [TypedDict and dataclass](./05-typeddict-and-dataclass.md)
- [Protocol and Structural Typing](./06-protocol-and-structural-typing.md)
- [Understanding Generics](./07-generic.md)
- [Using mypy and pyright](./08-mypy-and-pyright.md)
- [Pydantic and Type Hints](./09-pydantic-and-type-hints.md)
- [Type Hint Best Practices](./10-type-hints-best-practices.md)
<!-- toc:end -->

## References

- [Python docs — typing.Optional](https://docs.python.org/3/library/typing.html#typing.Optional)
- [Python docs — typing.Union](https://docs.python.org/3/library/typing.html#typing.Union)
- [PEP 604 — Allow writing union types as X | Y](https://peps.python.org/pep-0604/)
- [mypy docs — Optional types and None](https://mypy.readthedocs.io/en/stable/kinds_of_types.html#optional-types-and-the-none-type)

Tags: Python, Type Hints, Optional, Union, None Handling, Type Narrowing
