---
series: algorithms-101
episode: 6
title: Dynamic Programming
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - Algorithms
  - Dynamic Programming
  - Memoization
  - Tabulation
  - Optimal Substructure
seo_description: The two conditions for dynamic programming, memoization vs tabulation, and classic DP problems for state-design intuition.
last_reviewed: '2026-05-04'
---

# Dynamic Programming

> Algorithms 101 series (6/10)

<!-- a-grade-intro:begin -->

**Core question**: Why do we keep recomputing the same subproblems, and how can we recognise that pattern in the wild?

> Dynamic programming (DP) applies when (1) the same subproblems repeat and (2) the optimal solutions of subproblems compose into the optimal solution of the whole. The work is to define the state, write a recurrence, and solve it either top-down with memoization or bottom-up with tabulation. DP feels hard not because of the algorithm but because state design is a skill — one that grows by writing classic problems with your own hands.

<!-- a-grade-intro:end -->

## What You Will Learn

- The two conditions DP needs: overlapping subproblems and optimal substructure
- The difference between memoization (top-down) and tabulation (bottom-up)
- How to define a state and write a recurrence
- Classic DP problems: Fibonacci, 0/1 knapsack, longest common subsequence

## Why It Matters

DP is the backbone of algorithm interviews and shows up in production for optimisation, scheduling, and string comparison. The same way of thinking extends to value functions in reinforcement learning, dynamic-programming-based control, and decoders in sequence-to-sequence models.

> DP starts from one principle: never solve the same subproblem twice.

## Concept at a Glance

> DP defines a recurrence over a state space and solves it. Memoization is recursion plus a cache and feels intuitive. Tabulation fills small states first and tends to be faster and lighter on memory. The hard part — and the one worth practising — is choosing what the state means. That choice is 90% of the solution.

```text
DP applicability signals
    1) The same subproblem appears many times (overlapping subproblems)
    2) Optimal subproblem solutions compose into optimal whole (optimal substructure)

Two implementations
    Top-down  (memoization) : recursion + cache, computes only needed states
    Bottom-up (tabulation)  : iteration,         fills every state in order
```

## Key Terms

| Term | Description |
| --- | --- |
| State | A single cell of the DP table — what subproblem it represents |
| Recurrence | The relation between states |
| Overlapping subproblems | The same subproblem appears repeatedly |
| Optimal substructure | The optimum of parts forms the optimum of the whole |
| Memoization | Caching results to remove duplicate work |

## Before / After

**Before — Fibonacci with no memo, O(2^n):**

```python
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
# fib(40) and beyond becomes painfully slow
```

**After — memoization, O(n):**

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
```

## Hands-On: Step by Step

### Step 1: See the overlapping subproblems

```python
calls = 0
def fib_naive(n):
    global calls
    calls += 1
    if n <= 1:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)

fib_naive(20)
print(calls)   # 13529 — explosive in n
```

You can watch the same `fib(k)` getting recomputed many times. That repetition is the starting point for DP.

### Step 2: Top-down (memoization)

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(100))   # 354224848179261915075
```

The recursive structure stays exactly the same; one decorator adds the cache. It is intuitive and easy to extend.

### Step 3: Bottom-up (tabulation)

```python
def fib_tab(n):
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]

print(fib_tab(100))
```

We fill from small states up. There is no recursion depth to worry about, and we can collapse the array down to two rolling variables for even less memory.

### Step 4: 0/1 knapsack — practising state definition

```python
def knapsack(weights, values, W):
    n = len(weights)
    dp = [[0] * (W + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        w, v = weights[i - 1], values[i - 1]
        for cap in range(W + 1):
            dp[i][cap] = dp[i - 1][cap]
            if w <= cap:
                dp[i][cap] = max(dp[i][cap], dp[i - 1][cap - w] + v)
    return dp[n][W]

print(knapsack([2, 3, 4, 5], [3, 4, 5, 6], 5))   # 7
```

State: `dp[i][cap]` is the best value using the first `i` items with capacity `cap`. Once the state is clearly written, the recurrence almost writes itself.

### Step 5: Longest common subsequence (LCS) — DP across two sequences

```python
def lcs(a, b):
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[n][m]

print(lcs("ABCBDAB", "BDCABC"))   # 4
```

We fill a table indexed by all pairs of prefixes. This is the algorithm under diff tools, DNA alignment, and document comparison.

## Notable Points

- State definition is 90% of the solution
- Top-down feels natural; bottom-up is usually faster and lighter on memory
- For 2D DP, one row is often enough — rolling array
- The same problem can have very different costs depending on how the state is defined

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Coding before defining the state | Confused recurrence | Write a one-line meaning of `dp[...]` first |
| Missing base case | Wrong answer | Initialise `dp[0]`, `dp[i][0]` explicitly |
| Mutable cache keys | Cache misses | Convert to tuple |
| Applying DP without overlap | Plain divide and conquer fits better | Verify subproblems actually repeat |
| Memory blow-up | OOM for large inputs | Use a rolling array to drop a dimension |

## How This Is Used in Practice

- diff/patch algorithms (an LCS application)
- String similarity (edit distance)
- Dynamic time warping in speech recognition
- Join-order selection in database query optimisers
- Value-function updates in reinforcement learning (Bellman equations)

## How a Senior Engineer Thinks

A senior engineer first asks "do the same subproblems show up here?" If yes, they define the state and write the recurrence. They typically solve it top-down for clarity, then convert to bottom-up if performance demands it, and only then squeeze memory.

A senior engineer also thinks of DP as "divide and conquer that remembers." If recursion plus a cache feels natural, that is already DP. It is more efficient to learn DP by writing the recursion first, adding memoization, and only then translating to a table — not by drawing tables from scratch.

## Checklist

- [ ] Can you check the two conditions for DP?
- [ ] Can you state the meaning of a state and recurrence in one sentence?
- [ ] Can you write both top-down and bottom-up versions?
- [ ] Have you reduced memory with a rolling array?
- [ ] Can you spot the applicability signals?

## Practice Problems

1. Given coin denominations and a target amount, write a function that returns the minimum number of coins. Define the state and recurrence in words first, then translate to code.

2. Compute the edit distance (Levenshtein) between two strings, treating insertion, deletion, and substitution as cost 1 each.

3. In a graph with positive weights, design a DP that counts paths between two nodes whose total length is at most 5. The state holds the current node and the remaining length.

## Wrap-Up and Next Steps

DP starts from "do not solve the same subproblem twice." It applies whenever the same subproblems repeat and parts compose into a whole. State definition is almost the entire solution, and starting top-down then refining to bottom-up is usually the smoothest path to learn it.

The next article covers greedy algorithms — when greedy actually works (exchange arguments, matroid intuition), classic problems, and cases where what looks greedy actually requires DP.

<!-- toc:begin -->
- [What Is an Algorithm?](./01-what-is-an-algorithm.md)
- [Time and Space Complexity](./02-time-and-space-complexity.md)
- [Search Algorithms](./03-search-algorithms.md)
- [Sorting Algorithms](./04-sorting-algorithms.md)
- [Recursion and Divide and Conquer](./05-recursion-and-divide-and-conquer.md)
- **Dynamic Programming (current)**
- Greedy Algorithms (upcoming)
- Graph Algorithms (upcoming)
- String Algorithm Basics (upcoming)
- Algorithm Problem-Solving Strategies (upcoming)
<!-- toc:end -->

## References

- [Python `functools.lru_cache`](https://docs.python.org/3/library/functools.html#functools.lru_cache)
- [Wikipedia — Dynamic programming](https://en.wikipedia.org/wiki/Dynamic_programming)
- [CLRS — Introduction to Algorithms, Chapter 15](https://mitpress.mit.edu/books/introduction-algorithms-third-edition)
- [Competitive Programmer's Handbook — Chapter 7](https://cses.fi/book/book.pdf)

Tags: Computer Science, Algorithms, Dynamic Programming, Memoization, Tabulation, Optimal Substructure
