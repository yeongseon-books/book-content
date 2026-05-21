---
series: algorithms-python-101
episode: 6
title: "Algorithms with Python 101 (6/10): Dynamic Programming Basics"
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
  - Dynamic Programming
  - DP
  - Memoization
seo_description: Learn top-down and bottom-up dynamic programming in Python with Fibonacci, stair climbing, coin change, and knapsack examples.
last_reviewed: '2026-05-04'
---

# Algorithms with Python 101 (6/10): Dynamic Programming Basics

Some problems stay hopelessly slow if you solve the same subproblem again and again. Dynamic programming matters because it turns that waste into reusable work.

This topic also shows up constantly in interviews and competitive programming, but the real value is learning to recognize overlapping subproblems and reusable state.

This is post 6 in the Algorithms with Python 101 series. Here, we'll introduce dynamic programming through memoization, tabulation, and a set of classic Python examples.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Dynamic Programming Basics?
- Which signal should the example or diagram make visible for Dynamic Programming Basics?
- What failure should be prevented first when Dynamic Programming Basics reaches a real system?

## Big Picture

![Algorithms with Python 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-python-101/06/06-01-concept-overview.en.png)

*Algorithms with Python 101 chapter 6 flow overview*

This picture places Dynamic Programming Basics inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## What You Will Learn

- The two conditions for DP: optimal substructure and overlapping sub-problems
- Top-down implementation with memoization
- Bottom-up implementation with tabulation
- Classic DP problems: Fibonacci, stair climbing, coin change, knapsack

## Why It Matters

Recursion alone can lead to exponential time. DP reduces that to polynomial time by caching sub-problem results. Naive recursive Fibonacci is O(2^n); with DP, it becomes O(n).

> DP stores sub-problem results to avoid redundant computation — turning exponential problems into polynomial ones.

DP is the most frequently tested category in coding interviews. Learning the patterns gives you a systematic approach to optimization problems.

## Concept Overview

> DP applies when a problem has optimal substructure AND overlapping sub-problems

```text
Fibonacci fib(5) — redundant computation in naive recursion:
fib(5) → fib(4) + fib(3)
          fib(4) → fib(3) + fib(2)   ← fib(3) repeated
                    fib(3) → fib(2) + fib(1)  ← fib(2) repeated

After DP: each fib(n) computed only once
fib(1)=1 → fib(2)=1 → fib(3)=2 → fib(4)=3 → fib(5)=5
```

## Key Concepts

| Term | Description |
|------|-------------|
| Optimal substructure | The optimal solution is composed of optimal solutions to sub-problems |
| Overlapping sub-problems | The same sub-problems are computed repeatedly |
| Memoization | Top-down approach that caches results of recursive calls |
| Tabulation | Bottom-up approach that fills a table from the smallest sub-problem |
| State transition | The recurrence relation that computes the current state from previous states |

## Before / After

Two ways to compute the Fibonacci sequence.

```python
# before: naive recursion — O(2^n)
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

```python
# after: DP bottom-up — O(n)
def fibonacci(n):
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]
```

## Hands-On Steps

### Step 1: Top-Down — Memoization

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib_top_down(n: int) -> int:
    """Top-down Fibonacci — O(n)."""
    if n <= 1:
        return n
    return fib_top_down(n - 1) + fib_top_down(n - 2)

print(fib_top_down(50))  # 12586269025

# Manual memoization
def fib_memo(n: int, memo: dict | None = None) -> int:
    if memo is None:
        memo = {}
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fib_memo(n - 1, memo) + fib_memo(n - 2, memo)
    return memo[n]

print(fib_memo(50))  # 12586269025
```

### Step 2: Bottom-Up — Tabulation

```python
def fib_bottom_up(n: int) -> int:
    """Bottom-up Fibonacci — O(n), O(n) space."""
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]

print(fib_bottom_up(50))  # 12586269025

def fib_optimized(n: int) -> int:
    """Space-optimized Fibonacci — O(n), O(1) space."""
    if n <= 1:
        return n
    prev2, prev1 = 0, 1
    for _ in range(2, n + 1):
        prev2, prev1 = prev1, prev2 + prev1
    return prev1

print(fib_optimized(50))  # 12586269025
```

### Step 3: Stair Climbing Problem

```python
def climb_stairs(n: int) -> int:
    """Number of ways to climb n stairs taking 1 or 2 steps at a time."""
    if n <= 2:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    dp[2] = 2
    for i in range(3, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]

# Recurrence: dp[i] = dp[i-1] + dp[i-2]
for n in range(1, 8):
    print(f"Stairs {n}: {climb_stairs(n)} ways")
# Stairs 1: 1 ways
# Stairs 2: 2 ways
# Stairs 3: 3 ways
# Stairs 4: 5 ways
# Stairs 5: 8 ways
# Stairs 6: 13 ways
# Stairs 7: 21 ways
```

### Step 4: Minimum Coin Change

```python
def coin_change(coins: list[int], amount: int) -> int:
    """Minimum coins to make amount — O(amount * len(coins))."""
    dp = [float("inf")] * (amount + 1)
    dp[0] = 0

    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i and dp[i - coin] + 1 < dp[i]:
                dp[i] = dp[i - coin] + 1

    return dp[amount] if dp[amount] != float("inf") else -1

print(coin_change([1, 5, 10], 13))   # 4 (10+1+1+1)
print(coin_change([1, 5, 10], 30))   # 3 (10+10+10)
print(coin_change([3, 7], 5))        # -1 (impossible)
```

### Step 5: 0-1 Knapsack

```python
def knapsack(weights: list[int], values: list[int], capacity: int) -> int:
    """0-1 Knapsack — O(n * capacity)."""
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        w, v = weights[i - 1], values[i - 1]
        for c in range(capacity + 1):
            dp[i][c] = dp[i - 1][c]  # skip current item
            if w <= c:
                dp[i][c] = max(dp[i][c], dp[i - 1][c - w] + v)

    return dp[n][capacity]

weights = [2, 3, 4, 5]
values = [3, 4, 5, 6]
capacity = 8
print(knapsack(weights, values, capacity))  # 10
```

## What to Notice in This Code

- Top-down computes only the sub-problems that are needed; bottom-up computes all of them in order
- Space optimization replaces an array with two variables when only the previous values are needed
- Defining the recurrence relation is the core of DP — think about "the last choice"
- The knapsack's 2D table records all combinations of "items x capacity"

## 5 Common Mistakes

| Mistake | Why It's a Problem | How to Fix It |
|---------|-------------------|---------------|
| Coding before defining the recurrence | Logic errors without a clear structure | Write the recurrence formula first |
| Missing base case | Wrong results when dp[0] is uninitialized | Define the smallest sub-problem first |
| Wrong table size | IndexError from out-of-range access | Allocate size n+1 |
| Exceeding recursion depth in top-down | RecursionError for large n | Switch to bottom-up |
| Unnecessary 2D table | Wasted memory | Optimize to 1D when only the previous row is needed |

## Real-World Applications

- Route optimization computes minimum-cost paths with DP
- Edit distance (Levenshtein) powers spell-checkers and diff tools
- The Viterbi algorithm in NLP uses DP for sequence decoding
- Portfolio optimization in finance can be formulated as a DP problem
- Game AI explores optimal strategies with DP-based search

## How Senior Engineers Think About This

You rarely implement DP from scratch in production, but DP thinking is invaluable. "Can I cache this computation?" and "Does this problem have optimal substructure?" are questions that drive performance optimization.

In coding interviews, when you see a DP problem, define the recurrence first and implement bottom-up. Top-down is more intuitive but risks stack overflow.

## How to decide whether a problem is really DP

- If the same computation repeats across requests, records, or subtrees, caching or a DP formulation is worth testing first.
- If the current answer depends on a small, well-defined set of previous states, you can often convert the problem into a table or rolling-state update.
- If the state space explodes or inputs change continuously in real time, a greedy heuristic or approximation may be cheaper to operate than a full DP table.
- Before coding, write down the state, recurrence, and base cases in plain language. That usually exposes bugs earlier than the implementation does.

## Checklist

- [ ] Explain the two conditions for applying DP
- [ ] Compare top-down and bottom-up approaches
- [ ] Define a recurrence relation and fill a DP table
- [ ] Apply space optimization to a DP solution
- [ ] Solve stair climbing and coin change problems

## Exercises

1. Compute the number of ways to tile a 2xn rectangle with 1x2 tiles.
2. Find the length of the Longest Increasing Subsequence (LIS) using DP.
3. Extend the coin change solution to also print the actual coins used.

## Summary and Next Steps

Dynamic programming eliminates redundant computation, turning exponential problems into polynomial ones. The key is defining the recurrence relation. In the next article, we explore graph traversal with BFS and DFS.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Dynamic Programming Basics?**
  - The article treats Dynamic Programming Basics as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Dynamic Programming Basics?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Dynamic Programming Basics reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Algorithms with Python 101 (1/10): What Are Algorithms?](./01-what-are-algorithms.md)
- [Algorithms with Python 101 (2/10): Time Complexity and Big-O](./02-time-complexity-and-big-o.md)
- [Algorithms with Python 101 (3/10): Linear Search and Binary Search](./03-linear-and-binary-search.md)
- [Algorithms with Python 101 (4/10): Sorting Algorithms](./04-sorting-algorithms.md)
- [Algorithms with Python 101 (5/10): Recursion and Divide and Conquer](./05-recursion-and-divide-and-conquer.md)
- **Dynamic Programming Basics (current)**
- Graph Traversal — BFS and DFS (upcoming)
- Shortest Path Basics (upcoming)
- Greedy Algorithms (upcoming)
- Coding Test Problem-Solving Strategies (upcoming)

<!-- toc:end -->

## References

- [Wikipedia — Dynamic Programming](https://en.wikipedia.org/wiki/Dynamic_programming)
- [Real Python — Memoization with Python](https://realpython.com/lru-cache-python/)
- [GeeksforGeeks — Dynamic Programming](https://www.geeksforgeeks.org/dynamic-programming/)
- [LeetCode — Dynamic Programming Problems](https://leetcode.com/tag/dynamic-programming/)

Tags: Python, Algorithms, Dynamic Programming, DP, Memoization
