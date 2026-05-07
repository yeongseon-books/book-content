---
series: algorithms-101
episode: 4
title: Sorting Algorithms
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
  - Sorting
  - Quicksort
  - Mergesort
  - Timsort
seo_description: Why comparison sorting is bounded by O(n log n), the trade-offs among mergesort, quicksort, and heapsort, and what Timsort does differently.
last_reviewed: '2026-05-04'
---

# Sorting Algorithms

> Algorithms 101 series (4/10)

<!-- a-grade-intro:begin -->

**Core question**: Why is Python's `sorted` so consistently fast, and what does it do that a textbook quicksort does not?

> Sorting is the preprocessing step of almost every other algorithm. Comparison-based sorts have an information-theoretic lower bound of O(n log n). Within that envelope, mergesort, quicksort, and heapsort differ in stability, memory, and cache behaviour. Python's standard library uses Timsort, which adapts to the partial order found in real data. Picking a sort means weighing data shape, memory, and external constraints together.

<!-- a-grade-intro:end -->

## What You Will Learn

- Why comparison sorting cannot beat O(n log n)
- Trade-offs among mergesort, quicksort, and heapsort
- Stable vs unstable sorting and why it matters
- Why Timsort wins on real-world data

## Why It Matters

Sorting underpins index construction, batch processing, joins, window aggregations, and ML preprocessing. The cost of every downstream algorithm depends on which sort precedes it. Without a clear sense of trade-offs, you cannot estimate the cost of the rest of the pipeline.

> Understanding sorting is the first vocabulary of algorithm design.

## Concept at a Glance

> The decision tree of comparison sorts has depth log(n!) ≈ n log n, so O(n log n) is the lower bound. Mergesort is stable, uses O(n) extra memory, and guarantees O(n log n). Quicksort is in-place, averages O(n log n), but degrades to O(n²) on bad pivots. Heapsort is in-place and guaranteed O(n log n) but unstable. Timsort layers run detection on top of mergesort.

```text
Lower bound for comparison sorting: O(n log n)

mergesort   stable,   O(n) extra memory,  guaranteed O(n log n)
quicksort   unstable, in-place,           average O(n log n) / worst O(n^2)
heapsort    unstable, in-place,           guaranteed O(n log n)
Timsort     stable,   adaptive,           best O(n) / worst O(n log n)
```

## Key Terms

| Term | Description |
| --- | --- |
| Comparison sort | Orders by comparing elements |
| Stable sort | Preserves relative order of equal keys |
| In-place | Uses O(1) extra memory |
| Adaptive sort | Faster on partially sorted input |
| Timsort | Mergesort + run detection |

## Before / After

**Before — hand-rolled quicksort, weak on bad input:**

```python
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[0]
    left = [x for x in arr[1:] if x < pivot]
    right = [x for x in arr[1:] if x >= pivot]
    return quicksort(left) + [pivot] + quicksort(right)
# O(n^2) on already-sorted input
```

**After — use the standard library:**

```python
sorted_arr = sorted(arr)        # Timsort, stable, adaptive
arr.sort()                      # in-place variant
```

## Hands-On: Step by Step

### Step 1: Mergesort

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

The textbook divide and conquer. Stable and guaranteed O(n log n), at the cost of O(n) extra memory.

### Step 2: Quicksort with a randomised pivot

```python
import random

def quicksort_inplace(arr, lo=0, hi=None):
    if hi is None:
        hi = len(arr) - 1
    if lo >= hi:
        return
    pivot_idx = random.randint(lo, hi)
    arr[pivot_idx], arr[hi] = arr[hi], arr[pivot_idx]
    pivot = arr[hi]
    i = lo
    for j in range(lo, hi):
        if arr[j] < pivot:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
    arr[i], arr[hi] = arr[hi], arr[i]
    quicksort_inplace(arr, lo, i - 1)
    quicksort_inplace(arr, i + 1, hi)

a = [3, 1, 4, 1, 5, 9, 2, 6]
quicksort_inplace(a)
print(a)
```

Choosing the first element as the pivot collapses to O(n²) on sorted input. Random pivot or median-of-three is the standard defence.

### Step 3: Heapsort

```python
import heapq

def heapsort(arr):
    h = list(arr)
    heapq.heapify(h)
    return [heapq.heappop(h) for _ in range(len(h))]

print(heapsort([3, 1, 4, 1, 5, 9, 2, 6]))
```

Unstable but guaranteed O(n log n), with smaller extra memory than mergesort.

### Step 4: Observe Timsort's adaptiveness

```python
import random, time

def measure(arr):
    t = time.perf_counter()
    sorted(arr)
    return time.perf_counter() - t

n = 1_000_000
random_arr = [random.random() for _ in range(n)]
sorted_arr = sorted(random_arr)
nearly_sorted = sorted_arr[:]
for _ in range(100):
    i = random.randrange(n); j = random.randrange(n)
    nearly_sorted[i], nearly_sorted[j] = nearly_sorted[j], nearly_sorted[i]

print(f"random        : {measure(random_arr):.3f}s")
print(f"already sorted: {measure(sorted_arr):.3f}s")
print(f"nearly sorted : {measure(nearly_sorted):.3f}s")
```

Timsort detects pre-existing runs and merges them cheaply. Real-world data is almost never uniformly random, which is exactly where Timsort wins.

### Step 5: Multi-key sorting via stability

```python
people = [
    ("Alice", 30), ("Bob", 25), ("Carol", 30), ("Dan", 25),
]
people.sort(key=lambda p: p[0])     # secondary
people.sort(key=lambda p: p[1])     # primary
print(people)
```

Stable sort lets you sort by secondary then primary key to express multi-key ordering concisely. Timsort being stable makes this idiom safe.

## Notable Points

- Mergesort is stable and guaranteed but pays in memory
- Quicksort is fast on average but needs pivot defence
- Heapsort gives worst-case guarantees with low memory
- Timsort combines stability with real-world adaptiveness

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Maintaining a parallel index manually | Sync bugs | Use `sorted(..., key=..., reverse=...)` |
| Quicksort with first-element pivot | O(n^2) on sorted input | Random or median-of-three |
| Multi-key sort without stability assumption | Non-deterministic results | Use Timsort/`sort()` (stable) |
| Sorting huge data in memory | Out of memory | External merge sort, chunking |
| Comparator with side effects | Inconsistent comparisons | Extract via key function |

## How This Is Used in Practice

- Database `ORDER BY` and index construction internally sort
- Log pipelines do k-way merge of time-ordered streams
- Search engines sort candidates by score
- Recommender systems rank candidates
- ML pipelines sort before stratified sampling

## How a Senior Engineer Thinks

A senior engineer first asks "do I really need a full sort, or just the top k?" Top k can be O(n log k) via a heap; partition statistics can be done in O(n) via quickselect.

A senior engineer also checks "does it fit in memory?" External mergesort or distributed shuffle costs become the dominant concern as soon as data leaves RAM.

## Checklist

- [ ] Can you state the O(n log n) lower bound?
- [ ] Can you list the trade-offs of mergesort, quicksort, and heapsort?
- [ ] Do you understand stability and where it matters?
- [ ] Can you explain why Timsort is fast on real data?
- [ ] Do you ask "do I really need a full sort?" first?

## Practice Problems

1. Sort a list of words by length ascending, breaking ties by lexical order. Use Timsort's stability so the call fits in one line.

2. Implement `heapq.nlargest` yourself: given a list and k, return the top k in O(n log k) and explain why it beats a full sort.

3. Sketch external mergesort for 10^8 integers that do not fit in memory. Estimate the disk I/O passes required.

## Wrap-Up and Next Steps

Within the same asymptotic envelope, sorts differ by stability, memory, and adaptiveness. Default to `sorted` (Timsort) and switch only when a trade-off is clear.

The next article covers recursion and divide and conquer — call stacks, recurrences, and the path from divide and conquer toward dynamic programming.

<!-- toc:begin -->
- [What Is an Algorithm?](./01-what-is-an-algorithm.md)
- [Time and Space Complexity](./02-time-and-space-complexity.md)
- [Search Algorithms](./03-search-algorithms.md)
- **Sorting Algorithms (current)**
- Recursion and Divide and Conquer (upcoming)
- Dynamic Programming (upcoming)
- Greedy Algorithms (upcoming)
- Graph Algorithms (upcoming)
- String Algorithm Basics (upcoming)
- Algorithm Problem-Solving Strategies (upcoming)
<!-- toc:end -->

## References

- [Python `sorted` documentation](https://docs.python.org/3/library/functions.html#sorted)
- [Python sort how-to](https://docs.python.org/3/howto/sorting.html)
- [Tim Peters — Timsort listsort.txt](https://github.com/python/cpython/blob/main/Objects/listsort.txt)
- [Sedgewick & Wayne — Algorithms 4ed, Chapter 2](https://algs4.cs.princeton.edu/20sorting/)

Tags: Computer Science, Algorithms, Sorting, Quicksort, Mergesort, Timsort
