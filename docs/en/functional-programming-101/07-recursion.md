---
series: functional-programming-101
episode: 7
title: Recursion and Tail Calls
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
  - Functional Programming
  - Recursion
  - Tail Calls
  - Stack
seo_description: Learn recursive function principles, stack overflow prevention, and practical recursion patterns in Python.
last_reviewed: '2026-05-04'
---

# Recursion and Tail Calls

> Functional Programming 101 Series (7/10)

<!-- a-grade-intro:begin -->

**Key Question**: Can you solve problems by having a function call itself, without using loops?

> Recursion is a technique where a function calls itself to break a problem into smaller subproblems. In functional programming, it is the core tool for expressing repetition without state changes. This article covers recursion principles, tail call optimization, and practical Python usage.

<!-- a-grade-intro:end -->

## What You Will Learn

- The basic structure and mechanics of recursion
- The importance of base cases and preventing stack overflow
- Tail recursion and Python's limitations
- Patterns for converting recursion to iteration

## Why It Matters

Tree traversal, divide and conquer, and mathematical definitions are naturally expressed as recursion. Understanding recursion lets you implement algorithms for complex structures intuitively.

> Recursion = decomposing a problem into smaller versions of itself

Python does not support tail call optimization, so in practice you must be aware of recursion depth and convert to iteration when needed.

## Concept Overview

> Flow of a Recursive Call

```
factorial(4)
  -> 4 * factorial(3)
       -> 3 * factorial(2)
            -> 2 * factorial(1)
                 -> 1  (base case)
            <- 2 * 1 = 2
       <- 3 * 2 = 6
  <- 4 * 6 = 24
```

## Key Concepts

| Term | Description |
|------|-------------|
| Recursion | A technique where a function calls itself |
| Base case | The condition that stops the recursion |
| Tail recursion | A form where the recursive call is the last operation in the function |
| Stack overflow | An error that occurs when recursion depth exceeds the limit |
| Divide and conquer | A strategy of splitting a problem into smaller subproblems |

## Before / After

Express a loop as recursion.

```python
# before: iterative sum
def sum_iterative(numbers: list[int]) -> int:
    total = 0
    for n in numbers:
        total += n
    return total

print(sum_iterative([1, 2, 3, 4, 5]))  # 15
```

```python
# after: recursive sum
def sum_recursive(numbers: list[int]) -> int:
    if not numbers:  # base case
        return 0
    return numbers[0] + sum_recursive(numbers[1:])

print(sum_recursive([1, 2, 3, 4, 5]))  # 15
```

## Hands-On Steps

### Step 1: Basic Recursion — Factorial

```python
def factorial(n: int) -> int:
    """n! = n * (n-1) * ... * 1"""
    if n <= 1:  # base case
        return 1
    return n * factorial(n - 1)


print(factorial(5))   # 120
print(factorial(10))  # 3628800

# visualize the call stack
def factorial_verbose(n: int, depth: int = 0) -> int:
    indent = "  " * depth
    print(f"{indent}factorial({n})")
    if n <= 1:
        print(f"{indent}-> 1")
        return 1
    result = n * factorial_verbose(n - 1, depth + 1)
    print(f"{indent}-> {result}")
    return result

factorial_verbose(4)
# factorial(4)
#   factorial(3)
#     factorial(2)
#       factorial(1)
#       -> 1
#     -> 2
#   -> 6
# -> 24
```

### Step 2: Fibonacci and Memoization

```python
from functools import lru_cache


# naive recursion: O(2^n) — very slow
def fib_naive(n: int) -> int:
    if n <= 1:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


# memoization: O(n) — eliminates duplicate computation
@lru_cache(maxsize=None)
def fib_memo(n: int) -> int:
    if n <= 1:
        return n
    return fib_memo(n - 1) + fib_memo(n - 2)


print(fib_naive(10))  # 55 (slow)
print(fib_memo(100))  # 354224848179261915075 (fast)

# check cache statistics
print(fib_memo.cache_info())
# CacheInfo(hits=98, misses=101, maxsize=None, currsize=101)
```

### Step 3: Tail Recursion and Python's Limitations

```python
import sys

# normal recursion — stack frames accumulate
def factorial_normal(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial_normal(n - 1)  # multiplication is pending

# tail recursion — result passed as argument
def factorial_tail(n: int, acc: int = 1) -> int:
    if n <= 1:
        return acc
    return factorial_tail(n - 1, n * acc)  # last operation is the recursive call


# Python does NOT support tail call optimization (TCO)
print(sys.getrecursionlimit())  # default 1000
print(factorial_tail(900))  # works but...
# factorial_tail(1500)  # RecursionError!

# solution: convert to iteration
def factorial_iterative(n: int) -> int:
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

print(factorial_iterative(10000))  # no problem
```

### Step 4: Tree Traversal — A Natural Fit for Recursion

```python
from typing import Any


# traverse nested dicts (tree structure)
def flatten_dict(
    d: dict,
    parent_key: str = "",
    sep: str = ".",
) -> dict[str, Any]:
    """Flattens a nested dictionary."""
    items: list[tuple[str, Any]] = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


config = {
    "database": {
        "host": "localhost",
        "port": 5432,
        "credentials": {
            "user": "admin",
            "password": "secret",
        },
    },
    "debug": True,
}

flat = flatten_dict(config)
for k, v in flat.items():
    print(f"  {k}: {v}")
# database.host: localhost
# database.port: 5432
# database.credentials.user: admin
# database.credentials.password: secret
# debug: True
```

### Step 5: Converting Recursion to Iteration

```python
# recursive version: total size of a simulated file tree
def total_size_recursive(tree: dict) -> int:
    """Total size of a file tree represented as nested dicts."""
    total = 0
    for name, value in tree.items():
        if isinstance(value, dict):
            total += total_size_recursive(value)
        else:
            total += value
    return total


# iterative version: explicit stack management
def total_size_iterative(tree: dict) -> int:
    total = 0
    stack = [tree]
    while stack:
        current = stack.pop()
        for name, value in current.items():
            if isinstance(value, dict):
                stack.append(value)
            else:
                total += value
    return total


file_tree = {
    "src": {
        "main.py": 1200,
        "utils": {
            "helpers.py": 800,
            "config.py": 400,
        },
    },
    "README.md": 300,
    "tests": {
        "test_main.py": 600,
    },
}

print(total_size_recursive(file_tree))  # 3300
print(total_size_iterative(file_tree))  # 3300
```

## What to Notice in This Code

- Every recursion requires a base case
- `@lru_cache` eliminates duplicate calls and dramatically improves recursive performance
- Python lacks tail call optimization, so deep recursion should be converted to iteration
- Tree structure traversal is the most natural use case for recursion

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|---------------------|-----|
| Missing base case | Infinite recursion leads to stack overflow | Write the base case first |
| Deep recursion | Python's default limit is 1000 | Convert to iteration for deep cases |
| Missing memoization | Exponential time complexity | Apply `@lru_cache` |
| Slicing lists every call | O(n) copy at every invocation | Pass an index as an argument instead |
| Relying on tail recursion | Python does not optimize it | Use a loop instead |

## Real-World Applications

- Traverse nested structures in parsed JSON with recursion
- Use recursion for file system tree traversal
- Apply divide and conquer algorithms (quicksort, mergesort)
- AST (abstract syntax tree) processing requires recursive patterns
- Convert to explicit stacks when depth is bounded

## How Senior Engineers Think About This

Recursion is the most natural tool for trees, graphs, and nested structures. However, in Python you must always be aware of the recursion limit (default 1000). In practice, recursion with uncertain depth should be converted to iteration for safety.

"Recursion vs iteration" is a trade-off between readability and safety. Use recursion for shallow depths (tens of levels) where the structure is inherently recursive; use iteration when depth is deep or uncertain.

## Checklist

- [ ] I can set correct base cases for recursive functions
- [ ] I understand how stack frames accumulate during recursive calls
- [ ] I can improve recursive performance with `@lru_cache`
- [ ] I can convert recursion to iteration using an explicit stack
- [ ] I can explain the criteria for choosing between recursion and iteration

## Exercises

1. Implement binary search in both recursive and iterative versions.
2. Write a recursive function to flatten a nested list `[1, [2, [3, 4], 5], 6]`.
3. Implement memoization manually with a dictionary instead of `@lru_cache`.

## Summary and Next Steps

Recursion decomposes a problem into smaller versions of itself. Python lacks tail call optimization, so you must be aware of depth limits and convert to iteration when needed. The next article covers computing values only when needed: **lazy evaluation and generators**.

<!-- toc:begin -->
- [What Is Functional Programming?](./01-what-is-fp.md)
- [Pure Functions and Side Effects](./02-pure-functions.md)
- [Immutable Data](./03-immutable-data.md)
- [Higher-Order Functions](./04-higher-order-functions.md)
- [map, filter, reduce](./05-map-filter-reduce.md)
- [Closures and Partial Application](./06-closure-and-partial.md)
- **Recursion and Tail Calls (current)**
- [Lazy Evaluation and Generators](./08-lazy-evaluation.md)
- [Function Composition and Pipelines](./09-function-composition.md)
- [Balancing OOP and Functional Programming](./10-oop-and-fp-balance.md)
<!-- toc:end -->

## References

- [Python Official Docs — sys.setrecursionlimit](https://docs.python.org/3/library/sys.html#sys.setrecursionlimit)
- [Real Python — Recursion in Python](https://realpython.com/python-recursion/)
- [Python Official Docs — functools.lru_cache](https://docs.python.org/3/library/functools.html#functools.lru_cache)
- [The Little Schemer — Daniel P. Friedman](https://mitpress.mit.edu/9780262560993/the-little-schemer/)
