---
series: functional-programming-101
episode: 4
title: "Functional Programming 101 (4/10): Higher-Order Functions"
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
  - Functional Programming
  - Higher-Order Functions
  - Callbacks
  - Decorators
seo_description: Understand higher-order functions that accept or return functions, with practical Python patterns.
last_reviewed: '2026-05-04'
---

# Functional Programming 101 (4/10): Higher-Order Functions

This is the 4th post in the Functional Programming 101 series.

> Functional Programming 101 Series (4/10)

**Key Question**: Why is it powerful to pass a function as an argument to another function, or to return a function?

> A higher-order function accepts a function as an argument or returns a function as its result. This pattern abstracts behavior, removes duplication, and enables flexible code. This article covers the principles of higher-order functions and their practical use in Python.


![Functional Programming 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/functional-programming-101/04/04-01-big-picture.en.png)
*Functional Programming 101 chapter 4 flow overview*

## Questions to Keep in Mind

- What is a higher-order function?
- Why does passing behavior as an argument simplify code?
- How do `map`, `filter`, and `sorted` with `key=` demonstrate higher-order functions?

## Why It Matters

When extracting repeated patterns into functions, sometimes the "behavior itself" varies. Higher-order functions pass behavior as an argument, eliminating duplication and implementing the strategy pattern without classes.

> Higher-order functions = tools for treating behavior like data

Python's `sorted(key=...)`, `map(func, ...)`, and decorators are all higher-order functions. You already use them — understanding the principle makes them more powerful.

## Concept Overview

> Two Forms of Higher-Order Functions

```text
Form 1: Accept a function          Form 2: Return a function
─────────────────────              ─────────────────
sorted(data, key=func)             def make_adder(n):
map(func, data)                        return lambda x: x + n
filter(func, data)                 adder = make_adder(5)
```

## Key Concepts

| Term | Description |
|------|-------------|
| Higher-order function | A function that accepts a function as an argument or returns a function |
| Callback | A function passed as an argument to another function |
| First-class object | An object that can be assigned to variables, passed as arguments, and returned |
| Factory function | A function that creates and returns a new function or object |
| Decorator | A higher-order function that accepts a function and returns a new function with added behavior |

## Before / After

Remove duplicate code with a higher-order function.

```python
# before: three functions with nearly identical logic
def get_adults(people: list[dict]) -> list[dict]:
    result = []
    for p in people:
        if p["age"] >= 18:
            result.append(p)
    return result

def get_seniors(people: list[dict]) -> list[dict]:
    result = []
    for p in people:
        if p["age"] >= 65:
            result.append(p)
    return result
```

```python
# after: higher-order function with condition as argument
from collections.abc import Callable

def filter_people(
    people: list[dict],
    predicate: Callable[[dict], bool],
) -> list[dict]:
    return [p for p in people if predicate(p)]

adults = filter_people(people, lambda p: p["age"] >= 18)
seniors = filter_people(people, lambda p: p["age"] >= 65)
```

## Hands-On Steps

### Step 1: Passing Functions as Arguments

```python
from collections.abc import Callable

def apply_operation(
    values: list[int],
    operation: Callable[[int], int],
) -> list[int]:
    return [operation(v) for v in values]

numbers = [1, 2, 3, 4, 5]

doubled = apply_operation(numbers, lambda x: x * 2)
print(doubled)  # [2, 4, 6, 8, 10]

squared = apply_operation(numbers, lambda x: x ** 2)
print(squared)  # [1, 4, 9, 16, 25]

def negate(x: int) -> int:
    return -x

negated = apply_operation(numbers, negate)
print(negated)  # [-1, -2, -3, -4, -5]
```

### Step 2: The key Parameter in sorted

```python
from dataclasses import dataclass

@dataclass
class Student:
    name: str
    score: int
    grade: int

students = [
    Student("Alice", 85, 3),
    Student("Bob", 92, 2),
    Student("Charlie", 78, 3),
    Student("Diana", 95, 1),
]

# sort by score
by_score = sorted(students, key=lambda s: s.score, reverse=True)
for s in by_score:
    print(f"{s.name}: {s.score}")
# Diana: 95
# Bob: 92
# Alice: 85
# Charlie: 78

# multi-key sort: grade then score
by_grade_score = sorted(students, key=lambda s: (s.grade, -s.score))
for s in by_grade_score:
    print(f"  Grade {s.grade} {s.name}: {s.score}")
#   Grade 1 Diana: 95
#   Grade 2 Bob: 92
#   Grade 3 Alice: 85
#   Grade 3 Charlie: 78
```

### Step 3: Factory Functions that Return Functions

```python
from collections.abc import Callable

def make_multiplier(factor: int) -> Callable[[int], int]:
    """Creates a multiplier function."""
    def multiplier(x: int) -> int:
        return x * factor
    return multiplier

def make_validator(min_val: float, max_val: float) -> Callable[[float], bool]:
    """Creates a range validation function."""
    def validate(value: float) -> bool:
        return min_val <= value <= max_val
    return validate

double = make_multiplier(2)
triple = make_multiplier(3)
print(double(5))  # 10
print(triple(5))  # 15

is_valid_score = make_validator(0, 100)
is_valid_rate = make_validator(0.0, 1.0)
print(is_valid_score(85))   # True
print(is_valid_score(150))  # False
print(is_valid_rate(0.75))  # True
```

### Step 4: Decorators — Syntactic Sugar for Higher-Order Functions

```python
import time
from collections.abc import Callable
from typing import Any
from functools import wraps

def timer(func: Callable) -> Callable:
    """A decorator that measures execution time."""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__}: {elapsed:.4f}s")
        return result
    return wrapper

def retry(max_attempts: int) -> Callable:
    """Creates a retry decorator."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise
                    print(f"  Attempt {attempt} failed: {e}")
            return None
        return wrapper
    return decorator

@timer
def slow_sum(n: int) -> int:
    return sum(range(n))

@retry(max_attempts=3)
def unstable_operation() -> str:
    import random
    if random.random() < 0.7:
        raise ValueError("transient error")
    return "success"

result = slow_sum(1_000_000)
print(f"Result: {result}")
# slow_sum: 0.0234s
# Result: 499999500000
```

### Step 5: Building a Pipeline with Higher-Order Functions

```python
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")

def compose(*funcs: Callable) -> Callable:
    """Composes functions from right to left."""
    def composed(value):
        result = value
        for func in reversed(funcs):
            result = func(result)
        return result
    return composed

def strip_whitespace(text: str) -> str:
    return text.strip()

def to_lower(text: str) -> str:
    return text.lower()

def replace_spaces(text: str) -> str:
    return text.replace(" ", "-")

def truncate_20(text: str) -> str:
    return text[:20]

slugify = compose(truncate_20, replace_spaces, to_lower, strip_whitespace)

print(slugify("  Hello World Python  "))  # hello-world-python
print(slugify("  Functional Programming Guide  "))  # functional-programmi
```

## What to Notice in This Code

- Higher-order functions pass behavior as an argument to eliminate duplication
- Factory functions dynamically create multiple functions with different configurations
- Decorators are syntactic sugar for higher-order functions, and `@wraps` preserves metadata
- Function composition combines small functions into complex transformations

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|---------------------|-----|
| Complex lambda expressions | Debugging becomes difficult | Define a named function instead |
| Omitting `@wraps` | Function name and docstring are lost | Always add `@wraps` to decorators |
| Excessive nesting of higher-order functions | Readability degrades | Use intermediate variables beyond two levels |
| Missing type hints | The Callable signature is unclear | Specify `Callable[[int], str]` explicitly |
| Callbacks with side effects | Execution order sensitivity increases | Write callbacks as pure functions when possible |

## Real-World Applications

- FastAPI's `Depends()` implements dependency injection as a higher-order function
- `sorted(key=...)`, `min(key=...)`, `max(key=...)` are all higher-order functions
- Logging, authentication, and caching decorators are implemented as higher-order functions
- Event handler registration uses the callback pattern
- Test fixtures are generated with factory functions

## How Senior Engineers Think About This

Higher-order functions are "tools for abstraction." Extracting the "part that varies" from a repeated pattern into a function eliminates duplication. In Python, decorators, `sorted(key=...)`, and callback patterns already use higher-order functions pervasively.

However, excessive abstraction actually harms readability. Always ask "does this need to accept a function as an argument?" — in simple cases, writing the code directly may be better.

## Checklist

- [ ] I can explain the two forms of higher-order functions
- [ ] I can pass an appropriate function to `sorted(key=...)`
- [ ] I can write a factory function that dynamically creates functions
- [ ] I understand that decorators are higher-order functions and can write simple decorators
- [ ] I can use higher-order functions to eliminate code duplication

## Exercises

1. Write `make_formatter(format_str)` that dynamically creates number formatting functions.
2. Write a `@trace` decorator that logs execution time, call count, and result.
3. Implement a data processing pipeline by combining `filter_by(predicate)`, `sort_by(key)`, and `transform(func)`.

## Summary and Next Steps

Higher-order functions abstract behavior by accepting or returning functions. Factory patterns and decorators are their most common applications. The next article covers the most widely used higher-order functions: **map, filter, and reduce**.

## Answering the Opening Questions

- **What is a higher-order function?**
  - Higher-order functions appear in two forms: accepting a function as an argument, or returning a function. `apply_operation()` and `filter_people()` receive behavior as arguments, while `make_multiplier()` and `make_validator()` return new functions with baked-in configuration — demonstrating both forms precisely.
- **Why does passing behavior as an argument simplify code?**
  - All three let the library handle the iteration structure while we supply only the sorting criterion or transformation rule as a function. Like `sorted(students, key=lambda s: s.score)`, exposing only *what to look at* makes intent immediately readable without rewriting loops.
- **How do `map`, `filter`, and `sorted` with `key=` demonstrate higher-order functions?**
  - Factory functions are especially powerful when the same computation template varies only by configuration. With `make_multiplier(2)`, `make_validator(0, 100)`, and `retry(max_attempts=3)`, rules defined once and wrapped in a function can be reused at call sites without reassembling conditions each time.

<!-- toc:begin -->
## In this series

- [Functional Programming 101 (1/10): What Is Functional Programming?](./01-what-is-fp.md)
- [Functional Programming 101 (2/10): Pure Functions and Side Effects](./02-pure-functions.md)
- [Functional Programming 101 (3/10): Immutable Data](./03-immutable-data.md)
- **Higher-Order Functions (current)**
- map, filter, reduce (upcoming)
- Closures and Partial Application (upcoming)
- Recursion and Tail Calls (upcoming)
- Lazy Evaluation and Generators (upcoming)
- Function Composition and Pipelines (upcoming)
- Balancing OOP and Functional Programming (upcoming)

<!-- toc:end -->

## References

- [Python Official Docs — Functional Programming HOWTO](https://docs.python.org/3/howto/functional.html)
- [Real Python — Primer on Python Decorators](https://realpython.com/primer-on-python-decorators/)
- [Fluent Python — Chapter 7: Functions as First-Class Objects](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)
- [Python Official Docs — functools](https://docs.python.org/3/library/functools.html)

Tags: Python, Functional Programming, Higher-Order Functions, Callbacks, Decorators
