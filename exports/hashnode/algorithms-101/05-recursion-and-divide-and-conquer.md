
# Recursion and Divide and Conquer

> Algorithms 101 series (5/10)

<!-- a-grade-intro:begin -->

**Core question**: Why does recursion feel hard, and why are divide-and-conquer algorithms like mergesort fast for the right reason?

> Recursion expresses a problem in terms of smaller versions of itself. Three rules make it work: a base case that is reachable, strict progress toward that base case, and no shared mutable state. Divide and conquer is the most useful pattern built on recursion — divide, conquer, combine. Cost is analysed via recurrences. When the same subproblems repeat, we cache their results, which is exactly the door to dynamic programming.

<!-- a-grade-intro:end -->

## What You Will Learn

- The three rules for correct recursion
- The call stack and what causes RecursionError
- Divide-and-conquer recurrences and master-theorem intuition
- When repeated subproblems mean memoization is needed

## Why It Matters

Without comfortable recursion, trees, graphs, divide and conquer, dynamic programming, and backtracking all feel harder than they are. With it, complex problems decompose naturally into smaller versions of themselves.

> Recursion is the second native language of algorithms.

## Concept at a Glance

> A recursive function has a base case, a progress step, and a self-call. Divide and conquer breaks input into a parts of size n/b and combines results in f(n) work. The cost satisfies T(n) = a · T(n/b) + f(n); the master theorem gives the closed form. Mergesort yields O(n log n); binary search yields O(log n).

```text
Recursive shape
    if base case: return
    self-call(smaller input)
    combine results

Divide-and-conquer recurrence
    T(n) = a · T(n/b) + f(n)
    e.g. mergesort     T(n) = 2T(n/2) + O(n) = O(n log n)
         binary search T(n) = T(n/2)   + O(1) = O(log n)
```

## Key Terms

| Term | Description |
| --- | --- |
| Base case | Termination condition without further recursion |
| Call stack | Storage of nested call contexts |
| Divide and conquer | Divide → conquer → combine pattern |
| Recurrence | Equation describing recursive cost |
| Memoization | Caching results of repeated subproblems |

## Before / After

**Before — missing base case:**

```python
def factorial(n):
    return n * factorial(n - 1)        # no termination → RecursionError
```

**After — explicit base case:**

```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

## Hands-On: Step by Step

### Step 1: The three rules

```python
def power(base, exp):
    if exp == 0:                           # (1) base case
        return 1
    return base * power(base, exp - 1)     # (2) smaller input (3) self-call

print(power(2, 10))   # 1024
```

The base case must be reachable, and every call must move strictly closer to it.

### Step 2: Call stack and RecursionError

```python
import sys
print(sys.getrecursionlimit())     # 1000 by default

def deep(n):
    if n == 0:
        return 0
    return 1 + deep(n - 1)

try:
    deep(2000)
except RecursionError as e:
    print("RecursionError:", e)

sys.setrecursionlimit(10_000)
print(deep(2000))
```

CPython has no tail-call optimisation. Deep recursion either needs a higher limit or must be rewritten as iteration.

### Step 3: Divide and conquer for exponentiation, O(n) → O(log n)

```python
def fast_power(base, exp):
    if exp == 0:
        return 1
    half = fast_power(base, exp // 2)
    if exp % 2 == 0:
        return half * half
    return half * half * base

print(fast_power(2, 30))   # 1073741824
```

Halving the exponent gives O(log n) calls. The same trick appears in modular exponentiation used in cryptography.

### Step 4: Mergesort — feel a recurrence

```python
def mergesort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = mergesort(arr[:mid])
    right = mergesort(arr[mid:])
    return merge(left, right)

def merge(a, b):
    out, i, j = [], 0, 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    out.extend(a[i:]); out.extend(b[j:])
    return out

print(mergesort([3, 1, 4, 1, 5, 9, 2, 6]))
```

T(n) = 2T(n/2) + O(n) → O(n log n). The friendliest example of the recurrence in action.

### Step 5: Repeated subproblems → memoization

```python
def fib_naive(n):
    if n <= 1:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)
# Same subproblems repeated exponentially, very slow

from functools import lru_cache

@lru_cache(maxsize=None)
def fib_memo(n):
    if n <= 1:
        return n
    return fib_memo(n - 1) + fib_memo(n - 2)

print(fib_memo(100))
```

Caching collapses O(2^n) to O(n). This is the entry point to dynamic programming, covered in the next article.

## Notable Points

- Always check that the base case is genuinely reachable
- The combine cost f(n) can dominate the total complexity
- Spotting repeated subproblems unlocks dramatic speed-ups
- Deep recursion in Python is iteration in disguise — convert when needed

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Missing or unreachable base case | Infinite recursion | Verify monotone progress |
| Sharing mutable arguments across calls | Unintended accumulation | Copy or pass an index |
| Deep recursion in Python | RecursionError | Iterate or raise limit |
| Ignoring the divide ratio b | Wrong complexity | Apply master theorem |
| Missing repeated subproblems | Exponential time | Add `lru_cache` memoization |

## How This Is Used in Practice

- File-system traversal (recursive directory walking)
- Compiler AST traversal and transformation
- Distributed reduce stages (k-way merging)
- Graphics quadtrees and octrees
- ML decision-tree learning (recursive splits)

## How a Senior Engineer Thinks

A senior engineer chooses recursion when it expresses the problem naturally — trees almost always, deep linear chains rarely. For performance-critical paths, an explicit stack iteration is preferable to deep recursion.

A senior engineer also draws the recurrence in their head when they see divide and conquer. Memorising T(n) = 2T(n/2) + O(n) → O(n log n) and T(n) = T(n/2) + O(1) → O(log n) covers most analyses you will ever do.

## Checklist

- [ ] Can you check the three rules of recursion?
- [ ] Do you understand what RecursionError signals?
- [ ] Can you write a recurrence for a divide-and-conquer routine?
- [ ] Can you spot repeated subproblems?
- [ ] Can you convert deep recursion to iteration?

## Practice Problems

1. Sum an integer array via divide and conquer and compare with simple iteration. Write the recurrence and complexity.

2. Compute the intersection of two sorted lists recursively, then improve it with binary search when the two sizes are very different.

3. Solve Towers of Hanoi recursively and prove the call count is 2^n − 1 from the recurrence.

## Wrap-Up and Next Steps

Recursion expresses a problem as smaller versions of itself. Divide and conquer is its most useful pattern, analysed via recurrences. When subproblems repeat, memoization closes the gap between recursion and dynamic programming.

The next article introduces dynamic programming proper — memoization vs tabulation, the art of state design, and classic problems like 0/1 knapsack and longest common subsequence.

- [What Is an Algorithm?](./01-what-is-an-algorithm.md)
- [Time and Space Complexity](./02-time-and-space-complexity.md)
- [Search Algorithms](./03-search-algorithms.md)
- [Sorting Algorithms](./04-sorting-algorithms.md)
- **Recursion and Divide and Conquer (current)**
- Dynamic Programming (upcoming)
- Greedy Algorithms (upcoming)
- Graph Algorithms (upcoming)
- String Algorithm Basics (upcoming)
- Algorithm Problem-Solving Strategies (upcoming)
## References

- [Python `functools.lru_cache`](https://docs.python.org/3/library/functools.html#functools.lru_cache)
- [Python `sys.setrecursionlimit`](https://docs.python.org/3/library/sys.html#sys.setrecursionlimit)
- [Wikipedia — Master theorem](https://en.wikipedia.org/wiki/Master_theorem)
- [CLRS — Introduction to Algorithms, Chapter 4](https://mitpress.mit.edu/books/introduction-algorithms-third-edition)

Tags: Computer Science, Algorithms, Recursion, Divide and Conquer, Call Stack, Memoization

---

© 2026 YeongseonBooks. All rights reserved.
