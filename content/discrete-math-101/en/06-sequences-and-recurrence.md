---
series: discrete-math-101
episode: 6
title: Sequences and Recurrence
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - Discrete Math
  - Sequences
  - Recurrence
  - Master Theorem
  - Algorithm Analysis
seo_description: Sequences, recurrence relations, and the Master Theorem — the tools to derive exact time complexity for recursive algorithms.
last_reviewed: '2026-05-04'
---

# Sequences and Recurrence

This is post 6 in the Discrete Math 101 series.

> Discrete Math 101 series (6/10)

<!-- a-grade-intro:begin -->

**Core question**: How do we prove that merge sort is O(n log n)? How do we count the exact number of recursive calls a function makes?

> A sequence is an ordered list of numbers, and a recurrence is an equation that defines each term using earlier terms. The running time of a recursive function is itself a recurrence, and techniques like substitution, recursion trees, and the Master Theorem turn that recurrence into a closed form. This article covers the definitions, the solving methods, and how they apply directly to algorithm analysis.

<!-- a-grade-intro:end -->

## What You Will Learn

- Definition of sequences and closed forms
- Mathematical notation for recurrences
- Substitution and recursion-tree methods
- The Master Theorem

## Why It Matters

`mergesort(n) = 2·mergesort(n/2) + O(n)` — that is a recurrence. Solving it gives O(n log n). Every divide-and-conquer algorithm, every dynamic programming problem, every recursive function is analyzed by solving a recurrence. Without recurrences you can write recursive code, but you cannot analyze it.

> A recurrence is the mathematical mirror of a recursive algorithm.

## Concept at a Glance

> The recurrence T(n) = aT(n/b) + f(n) is the canonical divide-and-conquer form. The Master Theorem reads off the closed form instantly.

```text
   recursive algorithm
            │
            ↓
     recurrence form
            │
   ┌────────┼────────────┐
   ↓        ↓            ↓
substitution recursion  Master
            tree       Theorem
   │        │            │
   └────────┴──────┬─────┘
                   ↓
            closed form (Big-O)
```

## Key Terms

| Term | Description |
| --- | --- |
| Sequence | a₁, a₂, a₃, ... |
| Closed form | Expression that computes aₙ directly from n |
| Recurrence | aₙ = f(aₙ₋₁, ...) form |
| Master Theorem | Solution formula for T(n) = aT(n/b) + f(n) |
| Geometric sequence | aₙ = a₁·rⁿ⁻¹ |

## Before / After

**Before — without analysis:**

```python
# "Recursion is slow" — no exact complexity known
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)
```

**After — analyzed via recurrence:**

```python
# T(n) = T(n-1) + T(n-2) + O(1)
# Solution: T(n) = O(φⁿ) ≈ O(1.618ⁿ) — exponential
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)


# Memoized: T(n) = T(n-1) + O(1) → O(n)
from functools import lru_cache


@lru_cache(maxsize=None)
def fib_fast(n):
    return n if n < 2 else fib_fast(n - 1) + fib_fast(n - 2)
```

## Hands-On: Step by Step

### Step 1: Representing sequences

```python
# Arithmetic: aₙ = a₁ + (n-1)d
def arithmetic(a1: float, d: float, n: int) -> list:
    return [a1 + (i - 1) * d for i in range(1, n + 1)]


# Geometric: aₙ = a₁ · rⁿ⁻¹
def geometric(a1: float, r: float, n: int) -> list:
    return [a1 * (r ** (i - 1)) for i in range(1, n + 1)]


print(f"arithmetic (a=2, d=3, n=5): {arithmetic(2, 3, 5)}")
print(f"geometric  (a=1, r=2, n=8): {geometric(1, 2, 8)}")
```

Arithmetic and geometric sequences have crisp closed forms. The strategy for harder recurrences is to reduce them to these familiar shapes.

### Step 2: Computing a recurrence directly

```python
# Recurrence: T(n) = T(n-1) + n, T(0) = 0
# Meaning: do n units of work at each level
def T(n: int) -> int:
    if n == 0:
        return 0
    return T(n - 1) + n


# Closed form: T(n) = n(n+1)/2
def T_closed(n: int) -> int:
    return n * (n + 1) // 2


for n in [1, 5, 10, 100]:
    assert T(n) == T_closed(n)
    print(f"T({n}) = {T(n)} (closed: {T_closed(n)})")
```

### Step 3: Solving by substitution

```python
# Recurrence: T(n) = 2T(n/2) + n, T(1) = 1
# Substitute repeatedly:
# T(n) = 2T(n/2) + n
#      = 2[2T(n/4) + n/2] + n = 4T(n/4) + 2n
#      = 4[2T(n/8) + n/4] + 2n = 8T(n/8) + 3n
#      ...
#      = 2^k T(n/2^k) + kn
# n/2^k = 1 → k = log n
# T(n) = n·T(1) + n log n = O(n log n)


def merge_sort_count(arr: list) -> tuple:
    """Merge sort that also returns the comparison count."""
    if len(arr) <= 1:
        return arr, 0
    mid = len(arr) // 2
    left, lc = merge_sort_count(arr[:mid])
    right, rc = merge_sort_count(arr[mid:])
    merged, mc = merge_count(left, right)
    return merged, lc + rc + mc


def merge_count(a: list, b: list) -> tuple:
    result = []
    i = j = c = 0
    while i < len(a) and j < len(b):
        c += 1
        if a[i] <= b[j]:
            result.append(a[i]); i += 1
        else:
            result.append(b[j]); j += 1
    result.extend(a[i:]); result.extend(b[j:])
    return result, c


import math

for n in [16, 64, 256]:
    arr = list(range(n, 0, -1))
    _, count = merge_sort_count(arr)
    print(f"n={n}: {count} comparisons, n log n = {n * int(math.log2(n))}")
```

### Step 4: The Master Theorem

```python
# Master Theorem: T(n) = aT(n/b) + f(n)
# Compare n^(log_b a) and f(n) — three cases:
# 1. f(n) = O(n^(log_b a - ε))           → T(n) = Θ(n^(log_b a))
# 2. f(n) = Θ(n^(log_b a))                → T(n) = Θ(n^(log_b a) · log n)
# 3. f(n) = Ω(n^(log_b a + ε)) (regular)  → T(n) = Θ(f(n))

import math


def master_theorem(a: int, b: int, f_exponent: float) -> str:
    """Estimate the closed form of T(n) = aT(n/b) + n^f_exponent."""
    critical = math.log(a, b)
    if f_exponent < critical:
        return f"Θ(n^{critical:.2f})"
    elif abs(f_exponent - critical) < 1e-9:
        return f"Θ(n^{critical:.2f} · log n)"
    else:
        return f"Θ(n^{f_exponent})"


# Merge sort: T(n) = 2T(n/2) + n  → a=2, b=2, f(n)=n¹
print(f"merge sort:        {master_theorem(2, 2, 1)}")
# Binary search: T(n) = T(n/2) + 1
print(f"binary search:     {master_theorem(1, 2, 0)}")
# Strassen: T(n) = 7T(n/2) + n²
print(f"Strassen multiply: {master_theorem(7, 2, 2)}")
```

### Step 5: Closed form for Fibonacci

```python
# Fibonacci: F(n) = F(n-1) + F(n-2), F(0)=0, F(1)=1
# Characteristic equation: x² = x + 1 → x = (1±√5)/2 = φ, ψ
# Closed form: F(n) = (φⁿ - ψⁿ) / √5

import math

PHI = (1 + math.sqrt(5)) / 2
PSI = (1 - math.sqrt(5)) / 2


def fib_closed(n: int) -> int:
    return round((PHI ** n - PSI ** n) / math.sqrt(5))


def fib_iter(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


for n in [10, 20, 30]:
    assert fib_closed(n) == fib_iter(n)
    print(f"F({n}) = {fib_closed(n)} (closed = iter)")
```

Linear recurrences yield closed forms via the characteristic equation. The appearance of the golden ratio in Fibonacci is exactly this technique at work.

## Notable Points

- A recurrence captures the time complexity of a recursive algorithm.
- The Master Theorem is the standard tool for divide-and-conquer.
- Once you have a closed form, you can compute the cost for any n instantly.
- Memoization eliminates duplicate subproblems and turns exponential into polynomial.

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Ignoring Master Theorem conditions | Skipping the regularity check (case 3) | Verify all three cases explicitly |
| Missing the base case | Defining only the recurrence, omitting T(1) | Always specify the starting term |
| Confusing log bases | log₂ vs log₁₀ differ numerically | Big-O hides constants but track the base for exact counts |
| Non-uniform splits | Applying Master Theorem to T(n)=T(n-1)+T(n-2) | Master Theorem requires uniform division |
| Forgetting memoization | Writing accidentally exponential code | Always memoize when subproblems overlap |

## How This Is Used in Practice

- Time-complexity analysis in interviews (merge sort, quicksort, binary search)
- Deriving recurrences for DP problems (knapsack, LIS, edit distance)
- Search depth analysis for database indexes (B-trees)
- Estimating message complexity in distributed systems
- Designing cache invalidation frequencies and retry-backoff schedules

## How a Senior Engineer Thinks

A senior engineer sees a new algorithm and immediately sketches its recurrence: "How many times does this function call itself, and at what size?" They reach for the Master Theorem on reflex. The same recurrence-thinking applies to non-algorithmic design too — "What sequence should the n-th retry interval follow?" or "How fast does cache pressure grow?"

## Checklist

- [ ] Can you recall the closed forms for arithmetic and geometric sequences?
- [ ] Can you recognize the T(n) = aT(n/b) + f(n) shape?
- [ ] Can you distinguish all three Master Theorem cases?
- [ ] Can you derive O(n log n) for merge sort from its recurrence?
- [ ] Do you understand why memoization lowers complexity?

## Practice Problems

1. Use the Master Theorem to find the closed form of T(n) = 3T(n/2) + n².

2. Measure the runtime of iterative Fibonacci (O(n)) and naive recursive Fibonacci (O(φⁿ)) for n = 30, 35, 40 and compare.

3. Pick a recursive function you have written, express it as a recurrence, and derive its time complexity.

## Wrap-Up and Next Steps

Sequences are ordered lists of numbers; recurrences define them recursively. Substitution, recursion trees, and the Master Theorem give us closed forms — and therefore exact complexity bounds — for divide-and-conquer and dynamic programming.

The next article looks at the math of counting: combinatorics.

<!-- toc:begin -->
- [What Is Discrete Mathematics?](./01-what-is-discrete-math.md)
- [Propositions and Logic](./02-propositions-and-logic.md)
- [Sets and Functions](./03-sets-and-functions.md)
- [Relations and Equivalence](./04-relations-and-equivalence.md)
- [Proof Techniques](./05-proof-techniques.md)
- **Sequences and Recurrence (current)**
- Combinatorics (upcoming)
- Graph Theory Basics (upcoming)
- Trees and Graph Traversal (upcoming)
- Discrete Mathematics and Algorithms (upcoming)
<!-- toc:end -->

## References

- [Introduction to Algorithms — CLRS, Chapter 4 (Master Theorem)](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)
- [Wikipedia — Master Theorem](https://en.wikipedia.org/wiki/Master_theorem_(analysis_of_algorithms))
- [Wikipedia — Recurrence Relation](https://en.wikipedia.org/wiki/Recurrence_relation)
- [MIT OCW — Mathematics for Computer Science, Lectures 19-21](https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/)

Tags: Computer Science, Discrete Math, Sequences, Recurrence, Master Theorem, Algorithm Analysis
