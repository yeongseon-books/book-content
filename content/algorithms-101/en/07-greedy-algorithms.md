---
series: algorithms-101
episode: 7
title: "Algorithms 101 (7/10): Greedy Algorithms"
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
  - Algorithms
  - Greedy
  - Exchange Argument
  - Optimisation
  - Activity Selection
seo_description: When greedy algorithms are correct, exchange-argument proofs, classic problems, and greedy-looking problems that actually need DP.
last_reviewed: '2026-05-04'
---

# Algorithms 101 (7/10): Greedy Algorithms

**Core question**: If we always pick what looks best right now, does that really lead to the global optimum? And why does it work on some problems and quietly fail on others?

A greedy algorithm makes the locally best choice at every step and never reconsiders it. To be correct, two properties must hold: the greedy-choice property and optimal substructure. The standard tool for proving both is the exchange argument.

This is the 7th post in the Algorithms 101 series. Here we cover when greedy algorithms are correct, how to justify them, and where greedy-looking problems quietly turn into DP.


![algorithms 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-101/07/07-01-big-picture.en.png)
*algorithms 101 chapter 7 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Greedy Algorithms?
- Which signal should the example or diagram make visible for Greedy Algorithms?
- What failure should be prevented first when Greedy Algorithms reaches a real system?

## What You Will Learn

- The two conditions a greedy algorithm needs to be correct
- How to justify a greedy choice with an exchange argument
- Classic greedy problems: activity selection, coin change, Huffman coding
- The trap of greedy-looking problems that actually need DP

## Why It Matters

Greedy algorithms are among the simplest and fastest. When they apply they are easy to write and operate, often O(n log n) or better. The downside is that without a justification step you can ship wrong answers and not notice. Mastering greedy means knowing exactly when it applies.

> Greedy is the algorithm of simplicity, but it carries a heavier burden of correctness.

> The greedy-choice property says "there exists an optimal solution that contains the local greedy choice." Optimal substructure says "after that choice, the rest is solved by the same greedy rule." Both must hold. The usual proof technique is the exchange argument.

```text
Conditions for greedy to be correct
    1) Greedy-choice property : an optimal solution containing the greedy first choice exists
    2) Optimal substructure   : the remaining subproblem is also solved greedily

Exchange argument
    Take any optimal OPT, swap its first choice for the greedy choice;
    show the result is still optimal.
```

## Key Terms

| Term | Description |
| --- | --- |
| Greedy choice | The locally best choice at each step |
| Greedy-choice property | An optimal solution containing the greedy choice exists |
| Optimal substructure | The subproblem is also optimally solved by the same greedy rule |
| Exchange argument | Replace one choice in OPT with the greedy choice and prove equivalence |
| Huffman code | Frequency-based lossless compression — the canonical greedy example |

## Before / After

**Before — wrong greedy on coin change:**

```python
# Make change for 6 with coins [1, 3, 4]
def greedy_change(coins, amount):
    coins = sorted(coins, reverse=True)
    n = 0
    for c in coins:
        n += amount // c
        amount %= c
    return n

print(greedy_change([1, 3, 4], 6))   # 3 (4+1+1) — optimum is 2 (3+3)
```

**After — when greedy fails, fall back to DP:**

```python
def min_coins(coins, amount):
    INF = float('inf')
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return dp[amount] if dp[amount] != INF else -1

print(min_coins([1, 3, 4], 6))   # 2
```

## Hands-On: Step by Step

### Step 1: Activity selection — pick the earliest finish time

```python
def activity_selection(intervals):
    """[(start, end), ...] -> the largest set of non-overlapping intervals"""
    intervals = sorted(intervals, key=lambda x: x[1])
    chosen, last_end = 0, -1
    for s, e in intervals:
        if s >= last_end:
            chosen += 1
            last_end = e
    return chosen

print(activity_selection([(1, 4), (3, 5), (0, 6), (5, 7), (8, 9), (5, 9)]))   # 4
```

Always choosing the activity that finishes earliest is optimal. The exchange argument formalises why.

### Step 2: Meeting rooms — sort by end time, not start time

```python
meetings = [(1, 5), (2, 3), (3, 4), (4, 6), (6, 8)]
print(activity_selection(meetings))   # 3 — e.g. (2,3), (3,4), (4,6)
```

The same algorithm covers meeting-room and classroom scheduling. A single line — the sort key — decides correctness.

### Step 3: Coin change — when greedy actually works

```python
def coin_change_greedy(coins, amount):
    coins = sorted(coins, reverse=True)
    used = []
    for c in coins:
        while amount >= c:
            amount -= c
            used.append(c)
    return used if amount == 0 else None

# Korean and US coin systems are canonical, so greedy is optimal
print(coin_change_greedy([500, 100, 50, 10], 1260))
```

If a coin system is "canonical," greedy is optimal. For arbitrary coin sets there is no guarantee, and DP is the safe choice.

### Step 4: Huffman code — greedy on a priority queue

```python
import heapq

def huffman(freq):
    h = [[w, c] for c, w in freq.items()]
    heapq.heapify(h)
    while len(h) > 1:
        a = heapq.heappop(h)
        b = heapq.heappop(h)
        heapq.heappush(h, [a[0] + b[0], (a, b)])
    return h[0]

print(huffman({"a": 5, "b": 9, "c": 12, "d": 13, "e": 16, "f": 45}))
```

Repeatedly merge the two least-frequent nodes. The result is an optimal prefix code for lossless compression.

### Step 5: Fractional knapsack — fractional vs 0/1

```python
def fractional_knapsack(weights, values, W):
    items = sorted(zip(weights, values), key=lambda x: -x[1] / x[0])
    total = 0.0
    for w, v in items:
        if W >= w:
            W -= w; total += v
        else:
            total += v * (W / w); break
    return total

print(fractional_knapsack([10, 20, 30], [60, 100, 120], 50))   # 240.0
```

Fractional knapsack is solved optimally by greedy, but 0/1 knapsack is not — that requires DP. Whether items are divisible decides whether greedy applies.

## Notable Points

- A single sort key carries almost the entire correctness argument
- Divisibility separates fractional from 0/1 problems
- Priority queues are the workhorse data structure for greedy
- Don't trust intuition alone — reach for the exchange argument

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Greedy without a justification | Subtly wrong answers | Verify with an exchange argument |
| Greedy-looking problem that is actually DP | Wrong answer | Hand-craft a small counterexample |
| Wrong sort key | Off-by-one or close-to-optimal | Compare candidates: start, end, ratio |
| Missing priority queue | O(n^2) | Use a heap to get O(n log n) |
| Backtracking on a partial solution | Violates greedy itself | Greedy never undoes — switch to DP if needed |

## How This Is Used in Practice

- Job scheduling (CPU/GPU work queues)
- Fast heuristics for network routing
- Data compression (Huffman, LZ77 variants)
- Real-time decisions in ad-bidding systems
- Immediate action selection in game AI

## How a Senior Engineer Thinks

A senior engineer writes the one-line "why this is correct" before writing the algorithm. If a clean exchange argument does not come naturally, they suspect DP. They also actively craft small counterexamples — a hand-drawn case is the fastest correctness check available.

A senior engineer also documents the input conditions under which the greedy algorithm is valid. Writing "this only works when the coin system is canonical" protects future-you and your colleagues from quietly using it on the wrong inputs.

## Checklist

- [ ] Can you check the greedy-choice property and optimal substructure?
- [ ] Can you state the exchange argument in one sentence?
- [ ] Do you understand how the sort key drives correctness?
- [ ] Can you spot DP problems that look greedy?
- [ ] Are you comfortable with priority queues?

## Practice Problems

1. Schedule as many meetings as possible in a single room. Then construct a counterexample showing why sorting by start time instead of end time breaks optimality.

2. For jobs with positive weights, find a schedule that minimises mean completion time using a greedy strategy, and justify it with an exchange argument.

3. With coins [1, 5, 6, 9] and target 11, print both the greedy and the DP answer, and explain why they differ.

## Wrap-Up and Next Steps

Greedy is the algorithm of simplicity and speed, but it carries a heavier burden of correctness. Building the habit of checking the greedy-choice property and optimal substructure with an exchange argument prevents wrong answers slipping through.

The next article covers graph algorithms: the difference between BFS and DFS, Dijkstra's shortest paths, and minimum spanning trees. Graphs are where greedy and DP meet most frequently.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Greedy Algorithms?**
  - The article treats Greedy Algorithms as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Greedy Algorithms?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Greedy Algorithms reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Algorithms 101 (1/10): What Is an Algorithm?](./01-what-is-an-algorithm.md)
- [Algorithms 101 (2/10): Time and Space Complexity](./02-time-and-space-complexity.md)
- [Algorithms 101 (3/10): Search Algorithms](./03-search-algorithms.md)
- [Algorithms 101 (4/10): Sorting Algorithms](./04-sorting-algorithms.md)
- [Algorithms 101 (5/10): Recursion and Divide and Conquer](./05-recursion-and-divide-and-conquer.md)
- [Algorithms 101 (6/10): Dynamic Programming](./06-dynamic-programming.md)
- **Greedy Algorithms (current)**
- Graph Algorithms (upcoming)
- String Algorithm Basics (upcoming)
- Algorithm Problem-Solving Strategies (upcoming)

<!-- toc:end -->

## References

- [CLRS — Introduction to Algorithms, Chapter 16](https://mitpress.mit.edu/books/introduction-algorithms-third-edition)
- [Wikipedia — Greedy algorithm](https://en.wikipedia.org/wiki/Greedy_algorithm)
- [Python `heapq` documentation](https://docs.python.org/3/library/heapq.html)
- [Competitive Programmer's Handbook — Chapter 6](https://cses.fi/book/book.pdf)

Tags: Computer Science, Algorithms, Greedy, Exchange Argument, Optimisation, Activity Selection
