---
series: algorithms-python-101
episode: 5
title: Recursion and Divide and Conquer
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
  - Algorithms
  - Recursion
  - Divide and Conquer
  - Tower of Hanoi
seo_description: Understand recursion and the divide-and-conquer strategy in Python with practical examples including fast exponentiation and Tower of Hanoi.
last_reviewed: '2026-05-04'
---

# Recursion and Divide and Conquer

Recursion is one of those ideas that looks simple on the surface and confusing in practice. Once it clicks, though, a lot of algorithm patterns start to feel much more consistent.

Divide and conquer is one of the most important of those patterns. It shows up in binary search, merge sort, quick sort, and many problems that become manageable only after you split them into smaller parts.

This is post 5 in the Algorithms with Python 101 series. Here, we'll make recursion concrete first, then use it to build an intuition for divide-and-conquer problem solving.

## What You Will Learn

- How recursive functions work and what the call stack looks like
- Why the base case is critical
- The three stages of divide and conquer: divide, conquer, combine
- How to convert recursion to iteration and why memoization matters

## Why It Matters

Recursion is the foundation of tree traversal, graph traversal, sorting, and dynamic programming. Without understanding recursion, the rest of the algorithm curriculum becomes impenetrable.

> Divide and conquer splits a problem into smaller parts (Divide), solves each part (Conquer), and combines the results (Combine).

Divide and conquer is the common pattern behind merge sort, quick sort, and binary search. Recognizing this pattern lets you tackle new problems systematically.

## Concept Overview

> Recursion = a function that calls itself to perform repetitive work

```text
factorial(4) call trace:
factorial(4) → 4 × factorial(3)
               → 3 × factorial(2)
                    → 2 × factorial(1)
                         → 1 (base case)
                    ← 2 × 1 = 2
               ← 3 × 2 = 6
          ← 4 × 6 = 24
```

## Key Concepts

| Term | Description |
|------|-------------|
| Recursion | A programming technique where a function calls itself |
| Base case | The termination condition that stops recursive calls |
| Call stack | The stack of execution contexts created by recursive calls |
| Divide and conquer | A strategy that divides, conquers, and combines |
| Tail recursion | A form where the recursive call is the last operation |

## Before / After

Two ways to sum a list.

```python
# before: iterative
def sum_list(data):
    total = 0
    for x in data:
        total += x
    return total
```

```python
# after: recursive
def sum_list(data):
    if not data:
        return 0
    return data[0] + sum_list(data[1:])
```

## Hands-On Steps

### Step 1: Basic Recursion — Factorial and Fibonacci

```python
def factorial(n: int) -> int:
    """Factorial — O(n)."""
    if n <= 1:  # base case
        return 1
    return n * factorial(n - 1)

print(factorial(5))   # 120
print(factorial(10))  # 3628800


def fibonacci(n: int) -> int:
    """Fibonacci — O(2^n), inefficient."""
    if n <= 1:  # base case
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(fibonacci(10))  # 55
```

### Step 2: Visualizing the Call Stack

```python
def factorial_trace(n: int, depth: int = 0) -> int:
    """Factorial with call stack visualization."""
    indent = "  " * depth
    print(f"{indent}factorial({n}) called")

    if n <= 1:
        print(f"{indent}base case: return 1")
        return 1

    result = n * factorial_trace(n - 1, depth + 1)
    print(f"{indent}factorial({n}) = {result}")
    return result

factorial_trace(4)
# factorial(4) called
#   factorial(3) called
#     factorial(2) called
#       factorial(1) called
#       base case: return 1
#     factorial(2) = 2
#   factorial(3) = 6
# factorial(4) = 24
```

### Step 3: Divide and Conquer — Fast Exponentiation

```python
def power(base: int, exp: int) -> int:
    """Divide-and-conquer exponentiation — O(log n)."""
    if exp == 0:
        return 1
    if exp % 2 == 0:
        half = power(base, exp // 2)
        return half * half
    return base * power(base, exp - 1)

print(power(2, 10))   # 1024
print(power(3, 5))    # 243

# Comparison: naive approach is O(n), D&C is O(log n)
# Computing 2^1000 takes ~1000 vs ~10 multiplications
```

### Step 4: Divide and Conquer — Find Max and Tower of Hanoi

```python
def find_max(data: list[int], left: int, right: int) -> int:
    """Find maximum using divide and conquer."""
    if left == right:
        return data[left]
    mid = (left + right) // 2
    left_max = find_max(data, left, mid)
    right_max = find_max(data, mid + 1, right)
    return max(left_max, right_max)

data = [3, 7, 2, 9, 1, 8, 4]
print(find_max(data, 0, len(data) - 1))  # 9


def hanoi(n: int, source: str, target: str, auxiliary: str):
    """Tower of Hanoi — O(2^n)."""
    if n == 1:
        print(f"Disk 1: {source} -> {target}")
        return
    hanoi(n - 1, source, auxiliary, target)
    print(f"Disk {n}: {source} -> {target}")
    hanoi(n - 1, auxiliary, target, source)

hanoi(3, "A", "C", "B")
# Disk 1: A -> C
# Disk 2: A -> B
# Disk 1: C -> B
# Disk 3: A -> C
# Disk 1: B -> A
# Disk 2: B -> C
# Disk 1: A -> C
```

### Step 5: Converting Recursion to Iteration

```python
# Recursive factorial → iterative factorial
def factorial_iter(n: int) -> int:
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

print(factorial_iter(10))  # 3628800


# Recursive fibonacci → memoized fibonacci
from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci_memo(n: int) -> int:
    """Memoized Fibonacci — O(n)."""
    if n <= 1:
        return n
    return fibonacci_memo(n - 1) + fibonacci_memo(n - 2)

print(fibonacci_memo(50))  # 12586269025

# Python recursion depth limit
import sys
print(f"Max recursion depth: {sys.getrecursionlimit()}")  # default 1000
```

## What to Notice in This Code

- A recursive function without a base case causes a RecursionError. Always write the base case first
- Divide-and-conquer exponentiation reduces multiplications from O(n) to O(log n)
- Naive recursive Fibonacci is O(2^n), but adding memoization makes it O(n)
- Python's default recursion limit is 1000. For deep recursion, convert to iteration

## 5 Common Mistakes

| Mistake | Why It's a Problem | How to Fix It |
|---------|-------------------|---------------|
| Missing base case | Infinite recursion causes RecursionError | Always write the base case first |
| Exceeding recursion depth | Python's default limit is 1000 | Convert to iteration or adjust sys.setrecursionlimit |
| Redundant computation | Same values computed repeatedly, exponential time | Use memoization or DP |
| Creating new lists via slicing | Wastes memory and time | Pass indices instead |
| Forgetting the combine step | Sub-results are not merged into the final answer | Verify all three stages: divide, conquer, combine |

## Real-World Applications

- File system explorers recursively traverse directory trees
- Parsers recursively process nested structures like JSON and XML
- MapReduce uses divide and conquer to process large datasets in parallel
- Compilers recursively evaluate abstract syntax trees (ASTs)
- Fractal graphics are generated from recursive patterns

## How Senior Engineers Think About This

Recursion makes code concise, but you must watch for performance and stack depth. For inherently recursive structures like trees, recursion is natural. For simple iteration, a for loop is better.

The real value is learning to recognize the divide-and-conquer pattern. Habitually asking "Can I split this problem in half?" leads to efficient solutions faster.

## Checklist

- [ ] Explain the role of the base case in a recursive function
- [ ] Trace a call stack diagram for a simple recursive function
- [ ] Identify the three stages of divide and conquer
- [ ] Compare the pros and cons of recursion vs iteration
- [ ] Eliminate redundant computation with memoization

## Exercises

1. Write a function that reverses a list recursively.
2. Write a function that computes the sum of a list using divide and conquer.
3. Print the minimum number of moves and the full sequence for the Tower of Hanoi with 4 disks.

## Summary and Next Steps

Recursion is a technique where a function calls itself; divide and conquer is a strategy that uses recursion to systematically break down problems. In the next article, we tackle the redundant computation problem with dynamic programming.

<!-- toc:begin -->
- [What Are Algorithms?](./01-what-are-algorithms.md)
- [Time Complexity and Big-O](./02-time-complexity-and-big-o.md)
- [Linear Search and Binary Search](./03-linear-and-binary-search.md)
- [Sorting Algorithms](./04-sorting-algorithms.md)
- **Recursion and Divide and Conquer (current)**
- Dynamic Programming Basics (upcoming)
- Graph Traversal — BFS and DFS (upcoming)
- Shortest Path Basics (upcoming)
- Greedy Algorithms (upcoming)
- Coding Test Problem-Solving Strategies (upcoming)
<!-- toc:end -->

## References

- [Python Documentation — functools.lru_cache](https://docs.python.org/3/library/functools.html#functools.lru_cache)
- [Wikipedia — Divide-and-Conquer Algorithm](https://en.wikipedia.org/wiki/Divide-and-conquer_algorithm)
- [Real Python — Thinking Recursively in Python](https://realpython.com/python-thinking-recursively/)
- [GeeksforGeeks — Divide and Conquer](https://www.geeksforgeeks.org/divide-and-conquer/)

Tags: Python, Algorithms, Recursion, Divide and Conquer, Tower of Hanoi
