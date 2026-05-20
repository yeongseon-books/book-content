---
series: algorithms-101
episode: 1
title: "Algorithms 101 (1/10): What Is an Algorithm?"
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
  - Foundations
  - Problem Solving
  - Pseudocode
  - Correctness
seo_description: What an algorithm is, how it differs from a program, and how correctness, finiteness, and efficiency together define a usable algorithm.
last_reviewed: '2026-05-04'
---

# Algorithms 101 (1/10): What Is an Algorithm?

**Core question**: Why does a "good algorithm" matter so much when modern hardware is fast enough to run almost anything?

An algorithm is a finite sequence of clear, unambiguous steps that takes a well-defined input and produces a correct output. Three properties separate an algorithm from "any code that happens to work": correctness on every valid input, finiteness in time and space, and efficiency that scales with input growth. Hardware does not save us from a quadratic algorithm running on millions of records.

This is the first post in the Algorithms 101 series. Here we define what an algorithm is, how it differs from a program, and which core terms the rest of the series will build on.

## Questions to Keep in Mind

- What boundary should you inspect first when applying What Is an Algorithm??
- Which signal should the example or diagram make visible for What Is an Algorithm??
- What failure should be prevented first when What Is an Algorithm? reaches a real system?

## Big Picture

![algorithms 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-101/01/01-01-big-picture.en.png)

*algorithms 101 chapter 1 flow overview*

This picture places What Is an Algorithm? inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of What Is an Algorithm? is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## What You Will Learn

- The three properties an algorithm must satisfy
- How algorithms differ from programs
- Why pseudocode is the working language of algorithm design
- A high-level map of the nine remaining episodes

## Why It Matters

Most production incidents that look like "the system is slow" are really "the algorithm does not scale." A linear scan over 10 million rows is fine in a test fixture but lethal in production. Knowing the vocabulary of algorithms is the first step toward predicting whether a system will hold under realistic load.

> An algorithm is the contract between a problem and its solution.

## Concept at a Glance

> An algorithm has three obligations. It must produce the correct output for every valid input (correctness). It must terminate in finite time using finite memory (finiteness). It must do so within an efficiency envelope appropriate to the input size. Programs add concrete syntax, environment, and side effects, but the algorithm is the abstract recipe behind them.

```text
Problem  →  Algorithm  →  Program  →  Execution
                  (correctness, finiteness, efficiency)
```

## Key Terms

| Term | Description |
| --- | --- |
| Algorithm | Finite sequence of unambiguous steps from input to output |
| Correctness | Right output for every valid input |
| Finiteness | Terminates in finite time and memory |
| Pseudocode | Language-agnostic notation for algorithm design |
| Efficiency | Cost growth with respect to input size |

## Before / After

**Before — code that "works on my machine":**

```python
def find(arr, x):
    for v in arr:
        if v == x:
            return True
    return False
# Fine on 100 items, terrible on 10^8
```

**After — algorithm chosen for the input size:**

```python
def find(sorted_arr, x):
    import bisect
    i = bisect.bisect_left(sorted_arr, x)
    return i < len(sorted_arr) and sorted_arr[i] == x
# O(log n) once the array is sorted
```

## Hands-On: Step by Step

### Step 1: Verify finiteness

```python
def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

print(gcd(48, 36))   # 12
```

The Euclidean algorithm terminates because `b` strictly decreases on every step. Finiteness is not an accident — it is something you should be able to prove in a single sentence.

### Step 2: Verify correctness on edge cases

```python
assert gcd(0, 5) == 5
assert gcd(5, 0) == 5
assert gcd(7, 7) == 7
```

Correctness is checked against representative classes of input: empty values, equal values, extreme values. "All my tests passed" is meaningful only when the tests cover the right classes.

### Step 3: Estimate efficiency before coding

```text
n = 10^6, time budget = 1 second
→ O(n^2) is impossible
→ O(n log n) or O(n) is required
```

Input size narrows the algorithm before you write any code. This single habit prevents most performance disasters.

### Step 4: Write pseudocode first

```text
Algorithm: find smallest in array
1. min ← arr[0]
2. for i in 1..len(arr)-1:
3.     if arr[i] < min: min ← arr[i]
4. return min
```

Pseudocode keeps the focus on logic. Translation into Python or any other language becomes mechanical once the steps are clear.

### Step 5: Compare two algorithms for the same problem

```python
import time
n = 1_000_000
arr = list(range(n))

t = time.perf_counter()
arr.index(n - 1)                                # O(n)
print(f"linear : {time.perf_counter() - t:.4f}s")

import bisect
t = time.perf_counter()
bisect.bisect_left(arr, n - 1)                  # O(log n)
print(f"binary : {time.perf_counter() - t:.4f}s")
```

The point is not the absolute number but the order of difference. The same task takes very different times depending on the algorithm, even on identical hardware.

## Notable Points

- The same problem can have many algorithms with very different costs
- Pseudocode separates "what to do" from "how to write it"
- Correctness must be argued, not just tested
- Finiteness is a property to verify, not assume

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Coding before estimating cost | Time-out in production | Estimate complexity from input size first |
| "It works in tests" without edge cases | Failures on rare inputs | Cover empty, single, extreme, duplicate cases |
| Using a fast language as a substitute for a good algorithm | Quadratic still loses | Algorithm choice dominates language choice |
| Copy-pasting code without reading the algorithm | Hidden assumptions | Write pseudocode first |
| Confusing correctness with success on one input | Latent bugs | Verify against representative classes |

## How This Is Used in Practice

- API performance reviews always begin with the algorithm, not the language
- Database query plans are algorithms (sort, hash join, index scan)
- Compiler optimization is rewriting one algorithm into a faster equivalent
- Machine learning training is dominated by the cost of the underlying algorithm
- Debugging slow systems usually means replacing one algorithm with another

## How a Senior Engineer Thinks

A senior engineer asks "what is the algorithm here?" before "what is the bug?" When something is slow, the first question is whether the underlying approach is the right one for the input size, not whether the implementation can be tweaked.

A senior engineer also writes pseudocode for hard pieces before code. The five minutes spent clarifying the steps usually saves an hour of debugging. Code is the cheap part; the algorithm is where the real design happens.

## Checklist

- [ ] Can you state the algorithm's correctness condition in one sentence?
- [ ] Can you prove its finiteness in one sentence?
- [ ] Did you estimate complexity before coding?
- [ ] Can you compare two algorithms for the same problem on the same input?
- [ ] Can you write pseudocode without any specific language in mind?

## Practice Problems

1. Write the Euclidean algorithm in pseudocode and prove finiteness in one sentence. Then translate the pseudocode into Python and verify with three edge cases.

2. Two algorithms find the maximum in an array: linear scan and a divide-and-conquer recursion. Implement both, measure on inputs of size 10^4, 10^5, 10^6, and explain why their times differ even though both are O(n).

3. Pick a small task you wrote recently and rewrite it as pseudocode without using any specific language constructs. Note any assumption you had to make explicit during the rewrite.

## Wrap-Up and Next Steps

An algorithm is defined by correctness, finiteness, and efficiency. It is the abstract recipe behind every program, and it is what determines whether a system holds under load. Pseudocode is the design language; specific code is the implementation detail.

The next article introduces time and space complexity, the formal vocabulary used to compare algorithms. Big-O, Big-Omega, and Big-Theta will give us shared terms for the rest of the series.

## Answering the Opening Questions

- **What boundary should you inspect first when applying What Is an Algorithm??**
  - The article treats What Is an Algorithm? as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for What Is an Algorithm??**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when What Is an Algorithm? reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- **What Is an Algorithm? (current)**
- Time and Space Complexity (upcoming)
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

- [Wikipedia — Algorithm](https://en.wikipedia.org/wiki/Algorithm)
- [Donald Knuth — The Art of Computer Programming](https://www-cs-faculty.stanford.edu/~knuth/taocp.html)
- [CLRS — Introduction to Algorithms](https://mitpress.mit.edu/books/introduction-algorithms-third-edition)
- [Sedgewick & Wayne — Algorithms 4ed](https://algs4.cs.princeton.edu/home/)

Tags: Computer Science, Algorithms, Foundations, Problem Solving, Pseudocode, Correctness
