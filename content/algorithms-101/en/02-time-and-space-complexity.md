---
series: algorithms-101
episode: 2
title: "Algorithms 101 (2/10): Time and Space Complexity"
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
  - Big-O
  - Complexity
  - Performance
  - Asymptotic Analysis
seo_description: Big-O, Big-Omega, and Big-Theta as the shared vocabulary for comparing algorithms, plus how to estimate complexity from input size.
last_reviewed: '2026-05-04'
---

# Algorithms 101 (2/10): Time and Space Complexity

**Core question**: How can we predict whether an algorithm will be fast enough before writing the code?

Time and space complexity describe how an algorithm's cost grows with input size. They abstract away hardware, language, and constants so we can compare algorithms on equal footing. Once you can read the asymptotic class of an algorithm at a glance, you can decide whether it scales before writing it.

This is post 2 in the Algorithms 101 series. Here we cover Big-O and related notation, plus the cost model you need to compare algorithms before you benchmark them.


![algorithms 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-101/02/02-01-big-picture.en.png)
*algorithms 101 chapter 2 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Time and Space Complexity?
- Which signal should the example or diagram make visible for Time and Space Complexity?
- What failure should be prevented first when Time and Space Complexity reaches a real system?

## What You Will Learn

- The meaning of Big-O, Big-Omega, and Big-Theta
- How to estimate complexity from a code snippet
- The cost classes you must recognise immediately (constant, log, linear, n log n, quadratic, exponential)
- How input size narrows the algorithm choice

## Why It Matters

Asymptotic analysis is the shared vocabulary engineers use to discuss performance. Without it, "is this fast enough" becomes guesswork. With it, you can compare two algorithms before running either, and you can estimate whether code will hold at 100x its current load.

> Big-O is the language in which performance arguments are made.

> Complexity describes growth, not absolute time. An O(n) algorithm may be slower than an O(n log n) one for small inputs but always wins for large ones. The constant factors disappear in asymptotic notation, which is what allows fair comparison across machines and languages.

```text
Cost classes (low to high)
    O(1)       constant
    O(log n)   logarithmic
    O(n)       linear
    O(n log n) linearithmic
    O(n^2)     quadratic
    O(2^n)     exponential
```

## Key Terms

| Term | Description |
| --- | --- |
| Big-O | Asymptotic upper bound (worst case) |
| Big-Omega | Asymptotic lower bound (best case) |
| Big-Theta | Tight asymptotic bound |
| Worst case | Maximum cost over all inputs of size n |
| Amortized | Average over a long sequence of operations |

## Before / After

**Before — guessing if code is fast enough:**

```python
# "It runs in a second on my laptop, ship it."
# Production data is 1000x larger.
```

**After — estimating from input size:**

```text
n = 10^6, time budget = 1s
→ O(n^2) = 10^12 ops, impossible
→ O(n log n) ≈ 2 × 10^7 ops, feasible
→ Pick an O(n log n) algorithm
```

## Hands-On: Step by Step

### Step 1: Recognise common patterns

```python
def constant(arr):
    return arr[0]                 # O(1)

def linear(arr):
    return sum(arr)               # O(n)

def quadratic(arr):
    out = 0
    for x in arr:
        for y in arr:             # nested loop over n
            out += x * y
    return out                    # O(n^2)
```

The shape of the loops, not the language, drives the cost class.

### Step 2: Logarithmic patterns

```python
def binary_search(arr, x):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == x:
            return mid
        if arr[mid] < x:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1                     # O(log n) — halves each step
```

Halving the search space each step yields O(log n). The same pattern appears in tree heights, exponentiation, and some divide-and-conquer recursions.

### Step 3: Linearithmic patterns

```python
def mergesort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = mergesort(arr[:mid])
    right = mergesort(arr[mid:])
    return merge(left, right)     # O(n log n)
```

Divide into halves (log n levels) and do O(n) work per level. The product is O(n log n) — the typical cost of efficient sorting.

### Step 4: Estimate from input size

```text
n = 10              → almost anything (even O(n!))
n = 10^3            → O(n^2) okay
n = 10^5            → O(n log n) required
n = 10^7            → O(n) required
n = 10^9            → O(log n) or streaming
```

Memorising this table is one of the highest-leverage things you can do. It instantly narrows the algorithm before any code.

### Step 5: Worst case vs amortized

```python
arr = []
for i in range(10**6):
    arr.append(i)                 # average O(1), worst O(n) on resize
```

Python's list `append` is amortized O(1) — most calls are O(1) but occasional resizes copy the whole array. Amortized analysis matters when worst-case spikes are tolerable.

## Notable Points

- Big-O hides constants but constants matter for small n
- The worst case is usually what production sees over time
- Space complexity is independent of time complexity
- Logarithms ignore the base — O(log n) and O(log_2 n) are the same class

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Comparing algorithms by raw time on small inputs | Wrong winner at scale | Look at the cost class, not the milliseconds |
| Counting only the outer loop | Missed nested cost | Multiply nested loops |
| Ignoring constants completely | Tight code surprisingly slow | Reduce both class and constant for hot paths |
| Confusing average with worst case | Production spikes | Plan for worst case in latency-sensitive systems |
| Treating O(log n) as "essentially constant" | Underestimates large n | log(10^9) ≈ 30 — small but not free |

## How This Is Used in Practice

- Code reviews flag O(n^2) loops over potentially large inputs
- Database query plans are evaluated by the same asymptotic vocabulary
- Capacity planning estimates load growth against algorithm class
- Hot-path optimisation focuses on lowering both class and constants
- Algorithmic interviews are essentially asymptotic-analysis interviews

## How a Senior Engineer Thinks

A senior engineer reads complexity from code at a glance. Nested loops over the same input scream O(n^2); divide-and-conquer with linear merge says O(n log n). This pattern recognition is built by exposure, not memorisation.

A senior engineer also separates cost class from constant factors. For small inputs, a "worse" class with smaller constants can win. For large inputs, the class dominates. Knowing where your input lives on that curve is half of performance engineering.

## Checklist

- [ ] Can you read the cost class of a function in 30 seconds?
- [ ] Do you estimate complexity before coding?
- [ ] Can you distinguish worst case, average, and amortized?
- [ ] Do you know the input-size table by heart?
- [ ] Can you explain why O(log n) is dramatically smaller than O(n)?

## Practice Problems

1. For each of the following, give the time complexity in Big-O: triple nested loop, recursion T(n)=2T(n/2)+O(n), recursion T(n)=T(n/2)+O(1). Justify each in one sentence.

2. Implement a function that finds the two indices in a sorted array whose values sum to a target. First write an O(n^2) brute-force version, then improve it to O(n) using two pointers, and explain the gain.

3. Pick a real function from your code and write down its time and space complexity. Then identify a single change that would reduce one of them by at least one cost class.

## Wrap-Up and Next Steps

Asymptotic analysis is the language we use to argue about performance. Big-O for upper bound, Omega for lower, Theta for tight. Recognise the common cost classes and combine them with input size to predict whether code will scale.

The next article applies this vocabulary to search algorithms, where the difference between O(n) and O(log n) is the difference between scanning a million items and looking at twenty.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Time and Space Complexity?**
  - The article treats Time and Space Complexity as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Time and Space Complexity?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Time and Space Complexity reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Algorithms 101 (1/10): What Is an Algorithm?](./01-what-is-an-algorithm.md)
- **Time and Space Complexity (current)**
- Search Algorithms (upcoming)
- Sorting Algorithms (upcoming)
- Recursion and Divide and Conquer (upcoming)
- Dynamic Programming (upcoming)
- Greedy Algorithms (upcoming)
- Graph Algorithms (upcoming)
- String Algorithm Basics (upcoming)
- Algorithm Problem-Solving Strategies (upcoming)

<!-- toc:end -->

## References

- [Wikipedia — Big O notation](https://en.wikipedia.org/wiki/Big_O_notation)
- [CLRS — Introduction to Algorithms, Chapter 3](https://mitpress.mit.edu/books/introduction-algorithms-third-edition)
- [Open Data Structures — Asymptotic Notation](https://opendatastructures.org/)
- [Big-O Cheat Sheet](https://www.bigocheatsheet.com/)

Tags: Computer Science, Algorithms, Big-O, Complexity, Performance, Asymptotic Analysis
