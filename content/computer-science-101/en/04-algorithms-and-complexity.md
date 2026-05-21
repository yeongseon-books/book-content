---
series: computer-science-101
episode: 4
title: "Computer Science 101 (4/10): Algorithms and Complexity"
status: publish-ready
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
  - Complexity
  - Big-O
  - Data Structures
  - Performance
seo_description: An introductory tour of algorithms, time and space complexity, and Big-O notation for engineers picking data structures.
last_reviewed: '2026-05-15'
---

# Computer Science 101 (4/10): Algorithms and Complexity

Code that feels fine on 100 records can collapse in production once the data grows by three orders of magnitude. At that point, the first explanation is rarely “the machine is slow.” It is usually that the algorithmic cost was hidden while the input stayed small.

This is post 4 in the Computer Science 101 series.

In this article, we'll define algorithms, read time and space complexity, and show how data-structure choice changes performance long before micro-optimization matters.


![Computer Science 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-101/04/04-01-concept-at-a-glance.en.png)
*Computer Science 101 chapter 4 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Algorithms and Complexity?
- Which signal should the example or diagram make visible for Algorithms and Complexity?
- What failure should be prevented first when Algorithms and Complexity reaches a real system?

## Questions This Article Answers

- How can you compare two solutions before you benchmark them?
- What do time complexity and space complexity each measure?
- Why does Big-O help you predict behavior as input grows?
- How can `list`, `set`, and `dict` choices change the order of the whole solution?
- Why does code that looks acceptable on small inputs fail at scale?

## What You Will Learn

- The definition of an algorithm and what makes one good
- Time complexity and space complexity
- Comparing performance with Big-O notation
- How data-structure choice changes complexity

## Why It Matters

Code that runs fine on 100 items may stall on 1,000,000. If you cannot predict how performance scales with data size, you will hit incidents in production. Big-O lets you reason about performance limits without even running the code.

> Algorithm = the procedure to solve a problem. Complexity = the cost of that procedure.

Reading complexity is one of the clearest dividing lines between senior and junior engineers.

> Two algorithms that produce the same result can diverge by thousands of times once the input grows.

## Key Terms

| Term | Description |
| --- | --- |
| Algorithm | A finite, well-defined procedure that maps input to output |
| Time complexity | Growth rate of operations as input size grows |
| Space complexity | Growth rate of memory use as input size grows |
| Big-O | Upper bound on growth rate as input grows without bound |
| Data structure | A way of storing and accessing data (list, dict, set, ...) |

## Before / After

**Before — without complexity awareness:**

```python
# Find common elements between two lists — O(n^2)
def common_slow(a: list[int], b: list[int]) -> list[int]:
    result = []
    for x in a:
        if x in b:        # `in` on a list is O(n)
            result.append(x)
    return result

# At n=10,000 that is roughly 100 million comparisons — several seconds
```

**After — with complexity awareness:**

```python
# Same problem — O(n)
def common_fast(a: list[int], b: list[int]) -> list[int]:
    b_set = set(b)        # one-time O(n)
    return [x for x in a if x in b_set]   # `in` on a set is O(1)

# At n=10,000 that is roughly 20,000 comparisons — milliseconds
```

## Hands-On: Step by Step

### Step 1: Linear search and binary search

```python
def linear_search(arr: list[int], target: int) -> int:
    """Search an unsorted list for target — O(n)."""
    for i, value in enumerate(arr):
        if value == target:
            return i
    return -1

def binary_search(arr: list[int], target: int) -> int:
    """Search a sorted list for target — O(log n)."""
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

data = sorted(range(1_000_000))
print(linear_search(data, 999_999))   # 999999 — about 1,000,000 comparisons
print(binary_search(data, 999_999))   # 999999 — about 20 comparisons
```

### Step 2: Compare wall-clock time

```python
import time

big = sorted(range(1_000_000))
target = 999_999

start = time.perf_counter()
linear_search(big, target)
print(f"linear : {time.perf_counter() - start:.4f}s")

start = time.perf_counter()
binary_search(big, target)
print(f"binary : {time.perf_counter() - start:.6f}s")
```

**Expected output:** on sorted input, `binary` should be much faster than `linear`, and the comparison gap becomes dramatic at large sizes.

### Step 3: Data-structure choice changes complexity

```python
# list: `in` is O(n)
nums_list = list(range(1_000_000))

# set: `in` is O(1) on average
nums_set = set(nums_list)

start = time.perf_counter()
print(999_999 in nums_list)
print(f"list   : {time.perf_counter() - start:.4f}s")

start = time.perf_counter()
print(999_999 in nums_set)
print(f"set    : {time.perf_counter() - start:.6f}s")
```

### Step 4: Compare sorting algorithms

```python
import random

def bubble_sort(arr: list[int]) -> list[int]:
    """O(n^2) — educational only. Do not use this in real code."""
    arr = arr[:]
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

small = [random.randint(0, 100) for _ in range(2000)]

start = time.perf_counter()
bubble_sort(small)
print(f"bubble (n=2000)  : {time.perf_counter() - start:.4f}s")

start = time.perf_counter()
sorted(small)             # Python's sorted is Timsort — O(n log n)
print(f"sorted (n=2000)  : {time.perf_counter() - start:.6f}s")
```

### Step 5: Build complexity intuition

```python
def complexity_table(sizes: list[int]) -> None:
    print(f"{'n':>10} {'O(log n)':>12} {'O(n)':>12} {'O(n log n)':>14} {'O(n^2)':>16}")
    for n in sizes:
        import math
        log_n = math.log2(n)
        print(f"{n:>10} {log_n:>12.1f} {n:>12} {n * log_n:>14.0f} {n * n:>16,}")

complexity_table([10, 100, 1_000, 10_000, 100_000])
```

## Notable Points in This Code

- The same problem can have different complexities depending on the data structure you pick.
- `in` on a `list` is O(n); `in` on a `set` or `dict` is O(1) on average.
- Use the standard library for sorting (`sorted`, `list.sort`) — Timsort guarantees O(n log n).
- Binary search only applies when the input is sorted.

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Measuring on small data and feeling safe | Performance explodes as n grows | Measure with 10x and 100x larger inputs |
| Repeated `in` checks against a `list` | Cumulative O(n^2) | Convert lookup targets to a `set` or `dict` |
| Obsessing over micro-optimization | You shave constants while the order stays the same | First lower the algorithmic order |
| Trying to make every line O(1) | Lower readability and ballooning memory | Optimize only the bottleneck |
| Confusing average and worst-case complexity | Assuming dict is always O(1) | Hash collisions push the worst case to O(n) |

## How This Is Used in Practice

- Tracking API response time regression as data grows.
- Reading database EXPLAIN output and seeing how indexes change complexity.
- Picking the right cache structure (LRU with `OrderedDict`, fast membership with `set`).
- Reducing space complexity in large log processing with streaming algorithms.
- Trading off complexity in search and recommender index structures (B-Tree, Trie, HNSW).

## How a Senior Engineer Thinks

A senior engineer computes complexity in their head while reading code. When they see nested loops, the first question is "What happens when n grows?" On small n you cannot tell which is faster, but on large n the algorithm with the lower order always wins.

They also know that theoretical Big-O and real performance can diverge. Cache friendliness, branch prediction, and allocation costs dominate the constant factor. So they follow the principle: "An optimization you have not measured is a guess."

## Checklist

- [ ] I can state the order of an algorithm in Big-O
- [ ] I have memorized the complexities of the main `list`, `set`, and `dict` operations
- [ ] I can tell when to use linear vs binary search
- [ ] I can explain why we use the standard library for sorting
- [ ] I do not judge performance only on small inputs

## Practice Problems

1. Write two implementations that detect duplicates in a list of length n — one O(n^2), one O(n) — and compare their wall-clock time.

2. Merge two sorted lists into one sorted list in O(n) time. (Do not use `sorted(a + b)` since that is O(n log n).)

3. Find the missing integer in 1..n in O(n) time and O(1) space.

## Wrap-Up and Next Steps

An algorithm is a procedure for solving a problem. Complexity is its cost. Big-O describes the upper bound on growth as input grows. Data-structure choice drives complexity, so you must know the operation costs of `list`, `set`, and `dict`. Senior engineers do not optimize without measuring.

The next article opens up the machine that actually runs these algorithms — CPU, memory, and the cache hierarchy.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Algorithms and Complexity?**
  - The article treats Algorithms and Complexity as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Algorithms and Complexity?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Algorithms and Complexity reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Computer Science 101 (1/10): What Is Computer Science?](./01-what-is-computer-science.md)
- [Computer Science 101 (2/10): Computation and Programs](./02-computation-and-programs.md)
- [Computer Science 101 (3/10): Data Representation](./03-data-representation.md)
- **Algorithms and Complexity (current)**
- Computer Architecture (upcoming)
- Operating Systems (upcoming)
- Networks (upcoming)
- Databases (upcoming)
- Software Engineering (upcoming)
- From CS to AI and Data Science (upcoming)

<!-- toc:end -->

## References

- [Big-O Cheat Sheet](https://www.bigocheatsheet.com/)
- [Python TimeComplexity Wiki](https://wiki.python.org/moin/TimeComplexity)
- [Introduction to Algorithms (CLRS)](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)
- [Donald Knuth — The Art of Computer Programming](https://www-cs-faculty.stanford.edu/~knuth/taocp.html)

Tags: Computer Science, Algorithms, Complexity, Big-O, Data Structures, Performance
