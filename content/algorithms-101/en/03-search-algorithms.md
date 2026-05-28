---
series: algorithms-101
episode: 3
title: "Algorithms 101 (3/10): Search Algorithms"
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
  - Search
  - Binary Search
  - Linear Search
  - bisect
seo_description: Linear vs binary search, the leverage of sorted data, and practical use of Python bisect, including parametric search as an extension.
last_reviewed: '2026-05-04'
---

# Algorithms 101 (3/10): Search Algorithms

**Core question**: Given a million sorted integers, is there anything better than scanning from the start to find a target?

Search algorithms locate a value inside a collection. With unsorted data, linear scan at O(n) is the only option. With sorted data, binary search discards half the candidates each step, reaching the answer in O(log n). One precondition — sortedness — changes the algorithmic class.

This is the 3rd post in the Algorithms 101 series. Here we cover linear search, binary search, Python's `bisect`, and the broader idea of parametric search.


![algorithms 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-101/03/03-01-big-picture.en.png)
*algorithms 101 chapter 3 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Search Algorithms?
- Which signal should the example or diagram make visible for Search Algorithms?
- What failure should be prevented first when Search Algorithms reaches a real system?

## What You Will Learn

- The cost difference between linear and binary search
- Why sortedness changes the algorithmic class
- Variants of binary search (lower bound, upper bound)
- The `bisect` module and how to use it correctly

## Why It Matters

Search is the basic operation of almost every system. Database lookups, log queries, recommendation candidate retrieval, and game matchmaking all reduce to search. The wrong choice slows the entire system. Binary search also unlocks the broader pattern of parametric search, used widely in competitive programming.

> Without binary search, you have read only half of the algorithms book.

> Linear search compares from the first element, O(n). Binary search uses sorted order to halve the search space, O(log n). For one million items, linear takes a million comparisons; binary takes about twenty. The leverage comes entirely from the precondition that the input is sorted.

```text
Linear  [3, 1, 4, 1, 5, 9, 2, 6]   target=9
            8 comparisons → O(n)

Binary  [1, 1, 2, 3, 4, 5, 6, 9]   target=5
            4 < 5 < 6 → right half
            5 == 5 → found
            ≈ log(8) = 3 comparisons → O(log n)
```

## Key Terms

| Term | Description |
| --- | --- |
| Linear search | Compare from the first element |
| Binary search | Halve the candidates each step on sorted data |
| Lower bound | First position where target ≥ |
| Upper bound | First position where target > |
| Parametric search | Binary search over the answer itself |

## Before / After

**Before — linear search on sorted data:**

```python
def contains(sorted_arr, x):
    for v in sorted_arr:
        if v == x:
            return True
    return False
# O(n) — wastes the sortedness
```

**After — binary search via bisect:**

```python
import bisect
def contains(sorted_arr, x):
    i = bisect.bisect_left(sorted_arr, x)
    return i < len(sorted_arr) and sorted_arr[i] == x
# O(log n)
```

## Hands-On: Step by Step

### Step 1: Implement linear search

```python
def linear_search(arr, target):
    for i, v in enumerate(arr):
        if v == target:
            return i
    return -1

print(linear_search([3, 1, 4, 1, 5, 9, 2, 6], 5))   # 4
print(linear_search([3, 1, 4, 1, 5, 9, 2, 6], 7))   # -1
```

Works regardless of order but always pays O(n).

### Step 2: Implement binary search

```python
def binary_search(arr, target):
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

arr = sorted([3, 1, 4, 1, 5, 9, 2, 6])
print(binary_search(arr, 5))
```

The pivot is `mid = (lo + hi) // 2`. Termination depends on `lo <= hi` and proper updates of `lo` and `hi` — one off-by-one becomes an infinite loop.

### Step 3: Lower and upper bound variants

```python
def lower_bound(arr, target):
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo

def upper_bound(arr, target):
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo

arr = [1, 2, 2, 2, 3, 4, 5]
print(lower_bound(arr, 2))                                  # 1
print(upper_bound(arr, 2))                                  # 4
print(upper_bound(arr, 2) - lower_bound(arr, 2))            # 3
```

These two variants solve "count in range," "insertion position," and "first occurrence" with one tool.

### Step 4: Use `bisect`

```python
import bisect

arr = [1, 2, 4, 4, 4, 6, 8]
print(bisect.bisect_left(arr, 4))    # 2
print(bisect.bisect_right(arr, 4))   # 5

bisect.insort(arr, 5)
print(arr)
```

The standard library gives you a verified implementation. Prefer it over rolling your own except as an exercise.

### Step 5: Parametric search

```python
# Cut n logs into m equal pieces. Find the maximum length per piece.
def can_make(logs, length, m):
    return sum(log // length for log in logs) >= m

def max_cut_length(logs, m):
    lo, hi = 1, max(logs)
    while lo <= hi:
        mid = (lo + hi) // 2
        if can_make(logs, mid, m):
            lo = mid + 1
        else:
            hi = mid - 1
    return hi

print(max_cut_length([802, 743, 457, 539], 11))   # 200
```

When the answer is monotone (short → feasible, long → infeasible), binary-search the answer itself. This pattern collapses many "find the maximum X such that..." problems into O(log) time.

## Notable Points

- Linear search on sorted data is a wasted opportunity
- Binary search bugs hide in `mid` updates and termination
- Lower/upper bound variants cover most real questions
- `bisect` is faster and safer than ad-hoc implementations

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Binary search on unsorted data | Wrong result | Document the sortedness precondition |
| `(lo + hi) / 2` integer overflow | Negative index in C/C++ | Use `lo + (hi - lo) // 2` (Python is safe) |
| Off-by-one in bound updates | Infinite loop | Memorise lower/upper-bound templates |
| Reimplementing instead of using bisect | Subtle bugs | Reach for the standard library first |
| Assuming items are comparable | TypeError | Provide a key function |

## How This Is Used in Practice

- Database index lookups (B-tree generalises binary search)
- Time-series queries: binary-search a timestamp in sorted logs
- Game matchmaking: find a peer with similar score in sorted ranks
- ML inference: nearest-neighbour over sorted embeddings
- OS memory allocators: variants of binary search over free blocks

## How a Senior Engineer Thinks

A senior engineer reaches for binary search the moment they see "sorted." They also weigh "sort once + binary search many times" against repeated linear scans — pre-sorting almost always wins when queries are repeated.

A senior engineer also recognises monotone answers. When a problem asks for "the largest X such that ..." and the predicate is monotone in X, that is parametric search calling. Recognising the pattern is the entire trick.

## Checklist

- [ ] Do you have an intuition for the cost gap between linear and binary?
- [ ] Can you write the binary-search termination conditions correctly?
- [ ] Do you understand lower vs upper bound?
- [ ] Are you comfortable with `bisect`?
- [ ] Can you spot when parametric search applies?

## Practice Problems

1. Write a function that returns the first and last positions of a target in a sorted array. Use `lower_bound` and `upper_bound`.

2. Implement search in a rotated sorted array such as `[4,5,6,7,0,1,2]` in O(log n). It is a binary-search variant.

3. Given two sorted arrays of size n and m, find the k-th smallest element in their union in O(log(n+m)). It is a classic application of binary search.

## Wrap-Up and Next Steps

Search cost depends on whether the data has structure. With sortedness, binary search reduces O(n) to O(log n), and the same idea generalises to parametric search. Memorise the lower/upper bound templates and prefer `bisect` for routine work.

The next article covers sorting algorithms — the trade-offs of mergesort, quicksort, and heapsort, and why Python's `sorted` uses Timsort.

## Answering the Opening Questions

- **How large is the cost gap between linear and binary search?**
  - `linear_search()` over `[3, 1, 4, 1, 5, 9, 2, 6]` is O(n)—up to 8 comparisons. `binary_search()` on a sorted array halves candidates each step for O(log n)—about 3 comparisons. The 8-element example made that gap visible.
- **Why does sorting alone change the algorithm tier?**
  - With sorted data, a single `arr[mid] < target` check discards half the array. Without sorting, that reasoning vanishes and even `contains(sorted_arr, x)` falls back to O(n).
- **Where are lower bound and upper bound each used?**
  - `lower_bound(arr, 2)` finds the first position ≥ target; `upper_bound(arr, 2)` finds the first position > target. Subtracting the two counts duplicates, and `bisect_left`/`bisect_right` directly give insertion positions.

<!-- toc:begin -->
## In this series

- [Algorithms 101 (1/10): What Is an Algorithm?](./01-what-is-an-algorithm.md)
- [Algorithms 101 (2/10): Time and Space Complexity](./02-time-and-space-complexity.md)
- **Search Algorithms (current)**
- Sorting Algorithms (upcoming)
- Recursion and Divide and Conquer (upcoming)
- Dynamic Programming (upcoming)
- Greedy Algorithms (upcoming)
- Graph Algorithms (upcoming)
- String Algorithm Basics (upcoming)
- Algorithm Problem-Solving Strategies (upcoming)

<!-- toc:end -->

## References

- [Python `bisect` documentation](https://docs.python.org/3/library/bisect.html)
- [Wikipedia — Binary Search Algorithm](https://en.wikipedia.org/wiki/Binary_search_algorithm)
- [Open Data Structures — Searching](https://opendatastructures.org/)
- [Sedgewick & Wayne — Algorithms 4ed, Chapter 3](https://algs4.cs.princeton.edu/30searching/)

Tags: Computer Science, Algorithms, Search, Binary Search, Linear Search, bisect
