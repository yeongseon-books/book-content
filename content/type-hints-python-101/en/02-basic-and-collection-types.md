---
series: type-hints-python-101
episode: 2
title: "Type Hints in Python 101 (2/10): Basic Types and Collection Types"
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
  - Basic Types
  - Collection Types
  - list
  - dict
seo_description: Master Python type hints for basic types (int, str, bool, float) and collections (list, dict, tuple, set) with examples.
last_reviewed: '2026-05-04'
---

# Type Hints in Python 101 (2/10): Basic Types and Collection Types

This is post 2 in the Type Hints in Python 101 series.

> Type Hints in Python 101 Series (2/10)

**Key Question**: How do you annotate containers like lists and dictionaries so the type checker knows what is inside them?

> Annotating a function parameter as `list` tells the type checker it is a list — but not what the list contains. A `list[int]` is fundamentally different from a `list[str]` when it comes to the operations you can perform on its elements. This article covers Python's basic scalar types and how to parameterize collection types for precise type checking.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Basic Types and Collection Types?
- Which signal should the example or diagram make visible for Basic Types and Collection Types?
- What failure should be prevented first when Basic Types and Collection Types reaches a real system?

## Big Picture

![Type Hints in Python 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/type-hints-python-101/02/02-01-big-picture.en.png)

*Type Hints in Python 101 chapter 2 flow overview*

This picture places Basic Types and Collection Types inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## What You Will Learn

- Basic scalar types: `int`, `str`, `float`, `bool`, `bytes`, `None`
- Parameterized collection types: `list[T]`, `dict[K, V]`, `tuple[T, ...]`, `set[T]`
- The difference between homogeneous and heterogeneous tuples
- Nested type annotations for complex data structures

## Why It Matters

Most real-world Python code works with collections. API responses are dictionaries, database queries return lists of rows, and configuration is nested dicts. Without parameterized type annotations, the type checker treats every element as `object` and cannot catch errors like calling `.upper()` on an integer inside a list.

> Parameterized types = telling the type checker what is *inside* the container.

This is where type hints start paying real dividends in large codebases.

> Basic types annotate single values. Collection types wrap basic types to describe containers and their contents.

```text
Scalar:     int    str    float    bool    None
               \    |     /         |
Collection: list[int]  dict[str, float]  tuple[str, int]
               \           |                /
Nested:     dict[str, list[int]]
```

## Key Concepts

| Term | Description |
| --- | --- |
| Scalar type | A single value type like `int`, `str`, `float`, `bool` |
| Parameterized type | A generic type with type arguments like `list[int]` |
| Homogeneous tuple | A tuple with variable length and uniform type: `tuple[int, ...]` |
| Heterogeneous tuple | A tuple with fixed length and per-position types: `tuple[str, int]` |
| Type alias | A name assigned to a complex type for readability |

## Before / After

**Before — Unparameterized collections:**

```python
def get_prices(items: list) -> dict:
    result = {}
    for item in items:
        result[item.name] = item.price  # type checker: Unknown attributes
    return result
```

**After — Parameterized collections:**

```python
def get_prices(items: list[Product]) -> dict[str, int]:
    result: dict[str, int] = {}
    for item in items:
        result[item.name] = item.price  # type checker: OK
    return result
```

## Hands-On Steps

### Step 1: Basic Scalar Types

```python
name: str = "Alice"
age: int = 30
height: float = 5.7
is_active: bool = True
data: bytes = b"hello"
nothing: None = None
```

These are the building blocks. Every more complex type is ultimately composed of these scalars.

### Step 2: list and set

```python
names: list[str] = ["Alice", "Bob", "Charlie"]
unique_ids: set[int] = {1, 2, 3}

# Nested list
matrix: list[list[int]] = [
    [1, 2, 3],
    [4, 5, 6],
]

def get_active_users(users: list[str]) -> set[str]:
    return set(users)
```

`list[str]` means every element is a `str`. The type checker will flag `names.append(42)` as an error.

### Step 3: dict

```python
scores: dict[str, int] = {"Alice": 95, "Bob": 87}
config: dict[str, str | int | bool] = {
    "host": "localhost",
    "port": 8080,
    "debug": True,
}

def get_headers() -> dict[str, str]:
    return {"Content-Type": "application/json"}
```

`dict[str, int]` means string keys and integer values. For mixed-value dicts, use Union types.

### Step 4: tuple — Homogeneous vs. Heterogeneous

```python
# Heterogeneous: fixed length, per-position types
coordinate: tuple[float, float] = (37.5, 127.0)
record: tuple[str, int, bool] = ("Alice", 30, True)

# Homogeneous: variable length, uniform type
numbers: tuple[int, ...] = (1, 2, 3, 4, 5)
empty: tuple[()] = ()
```

The `...` (Ellipsis) in `tuple[int, ...]` means "zero or more ints." Without it, each position has its own type.

### Step 5: Type Aliases for Complex Types

```python
# Type alias for readability
UserScores = dict[str, list[int]]
Config = dict[str, str | int | bool | list[str]]

def aggregate_scores(data: UserScores) -> dict[str, float]:
    return {name: sum(scores) / len(scores) for name, scores in data.items()}

scores: UserScores = {
    "Alice": [95, 87, 92],
    "Bob": [78, 85, 90],
}
```

Type aliases reduce repetition and make signatures readable. In Python 3.12+, use the `type` statement: `type UserScores = dict[str, list[int]]`.

## What to Notice in This Code

- Collection types require type parameters to be useful for static analysis
- `tuple` has two forms: heterogeneous (fixed positions) and homogeneous (variable length with `...`)
- Nested types like `dict[str, list[int]]` are fully supported
- Type aliases improve readability for complex nested types

## 5 Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Using bare `list` or `dict` | Type checker cannot verify element types | Always parameterize: `list[int]`, `dict[str, str]` |
| Confusing `tuple[int, int]` with `tuple[int, ...]` | Fixed-length vs. variable-length semantics | Use `...` only for homogeneous variable-length tuples |
| Using `typing.List` on Python 3.9+ | Unnecessary import from typing | Use `list[str]` directly |
| Overly broad `dict[str, Any]` | Loses type safety for values | Use specific value types or TypedDict |
| Forgetting `frozenset` for immutable sets | Mutability mismatch | Use `frozenset[int]` when immutability is required |

## Real-World Applications

- API response models use `dict[str, list[dict[str, str]]]` for nested JSON structures
- Database query functions return `list[tuple[int, str, float]]` for typed row results
- Configuration loaders use `dict[str, str | int | bool]` for settings
- Data pipelines annotate `list[dict[str, float]]` for tabular data
- Cache implementations parameterize `dict[str, T]` with generics for type-safe storage

## How Senior Engineers Think About This

Senior engineers parameterize every collection type without exception. The five seconds it takes to write `list[int]` instead of `list` saves hours of debugging when someone passes the wrong type three layers deep in a call chain.

They also prefer narrow types over broad ones. `dict[str, Any]` is almost never the right answer — if you know the shape of your data, use TypedDict (covered in episode 5). The more precise the type, the more the type checker can help you.

## Checklist

- [ ] Parameterized all collection types with element types
- [ ] Used heterogeneous tuples for fixed-structure data
- [ ] Created type aliases for complex nested types
- [ ] Avoided bare `list`, `dict`, `tuple` without type parameters
- [ ] Used built-in types instead of `typing` imports (Python 3.9+)

## Exercises

1. Write a function `flatten(matrix: list[list[int]]) -> list[int]` that takes a 2D list and returns a 1D list. Verify with mypy.

2. Create a type alias `StudentRecord = tuple[str, int, list[float]]` (name, age, grades) and write a function that calculates the average grade from a list of student records.

3. Annotate a nested configuration structure: `dict[str, dict[str, str | int | list[str]]]`. Write a function that extracts a specific value and verify the types with mypy.

## Summary and Next Steps

Basic types (`int`, `str`, `float`, `bool`) and parameterized collections (`list[T]`, `dict[K, V]`, `tuple[T, ...]`, `set[T]`) form the foundation of Python type annotations. Always parameterize collections to give the type checker visibility into element types. Use type aliases for complex nested structures.

In the next article, we will explore `Optional` and `Union` types for handling values that might be missing or could be one of several types.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Basic Types and Collection Types?**
  - The article treats Basic Types and Collection Types as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Basic Types and Collection Types?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Basic Types and Collection Types reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Type Hints in Python 101 (1/10): What Are Python Type Hints?](./01-what-is-type-hint.md)
- **Basic Types and Collection Types (current)**
- Optional and Union (upcoming)
- Function Type Hints (upcoming)
- TypedDict and dataclass (upcoming)
- Protocol and Structural Typing (upcoming)
- Understanding Generics (upcoming)
- Using mypy and pyright (upcoming)
- Pydantic and Type Hints (upcoming)
- Type Hint Best Practices (upcoming)

<!-- toc:end -->

## References

- [Python docs — typing module](https://docs.python.org/3/library/typing.html)
- [PEP 585 — Type Hinting Generics In Standard Collections](https://peps.python.org/pep-0585/)
- [mypy docs — Built-in types](https://mypy.readthedocs.io/en/stable/builtin_types.html)
- [Real Python — Python Type Checking](https://realpython.com/python-type-checking/)

Tags: Python, Type Hints, Basic Types, Collection Types, list, dict
