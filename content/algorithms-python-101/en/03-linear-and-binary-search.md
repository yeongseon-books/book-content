---
series: algorithms-python-101
episode: 3
title: Linear Search and Binary Search
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Python
  - Algorithms
  - Linear Search
  - Binary Search
  - bisect
seo_description: Implement linear search and binary search in Python, compare their performance, and learn to use the bisect module.
last_reviewed: '2026-05-04'
---

# Linear Search and Binary Search

Searching is one of the most common operations in programming. On a small list, a linear scan is fine. On a large sorted list, cutting the search space in half each step changes the problem completely.

That is why binary search shows up far beyond textbook examples. The same pattern appears whenever you need the first value that satisfies a condition, not just an exact match.

This is post 3 in the Algorithms with Python 101 series. Here, we'll implement linear search and binary search side by side and compare when each approach makes sense.

## What You Will Learn

- How linear search works and its limitations
- The principle and implementation of binary search
- How to use Python's bisect module
- Performance comparison between the two approaches

## Why It Matters

Searching is the most common operation in programming. With 100 items, linear search is fine. With one million items, binary search needs at most 20 comparisons while linear search may need all one million.

> Binary search eliminates half the remaining data at each step, achieving O(log n) on sorted data.

Beyond simple lookups, binary search extends to "find the first/last value satisfying a condition" — a pattern that appears frequently in coding interviews.

## Concept Overview

> Search = the process of finding a target value in a collection of data

```text
Linear search: [1, 3, 5, 7, 9, 11, 13] — find 9
→ 1, 3, 5, 7, 9 (5 comparisons)

Binary search: [1, 3, 5, 7, 9, 11, 13] — find 9
→ 7 (middle), 11 (right half middle), 9 (3 comparisons)
```

## Key Concepts

| Term | Description |
|------|-------------|
| Linear search | Check elements one by one from start to end — O(n) |
| Binary search | Halve the search space using the middle element — O(log n) on sorted data |
| bisect | Python standard library module for binary search |
| Upper/lower bound | Variants that find the first position above or at a given value |
| Parametric search | Applying binary search to "find the boundary of a condition" |

## Before / After

Two ways to find a value in a sorted list.

```python
# before: linear search — O(n)
def search(data, target):
    for i, val in enumerate(data):
        if val == target:
            return i
    return -1
```

```python
# after: binary search — O(log n)
def search(data, target):
    left, right = 0, len(data) - 1
    while left <= right:
        mid = (left + right) // 2
        if data[mid] == target:
            return mid
        elif data[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

## Hands-On Steps

### Step 1: Implement Linear Search

```python
def linear_search(data: list, target) -> int:
    """Linear search — O(n)."""
    for i, value in enumerate(data):
        if value == target:
            return i
    return -1

data = [4, 2, 7, 1, 9, 3, 8]
print(linear_search(data, 9))   # 4
print(linear_search(data, 5))   # -1

# No sorting required — works on any list
```

### Step 2: Implement Binary Search

```python
def binary_search(sorted_data: list[int], target: int) -> int:
    """Binary search — O(log n), requires sorted data."""
    left, right = 0, len(sorted_data) - 1
    while left <= right:
        mid = (left + right) // 2
        if sorted_data[mid] == target:
            return mid
        elif sorted_data[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

data = [1, 3, 5, 7, 9, 11, 13, 15]
print(binary_search(data, 9))    # 4
print(binary_search(data, 10))   # -1
```

### Step 3: Use the bisect Module

```python
import bisect

data = [1, 3, 5, 7, 9, 11, 13, 15]

# Find insertion point (maintains sorted order)
pos = bisect.bisect_left(data, 9)
print(f"Position of 9: {pos}")  # 4

# Check whether a value exists
def bisect_search(sorted_data: list[int], target: int) -> int:
    pos = bisect.bisect_left(sorted_data, target)
    if pos < len(sorted_data) and sorted_data[pos] == target:
        return pos
    return -1

print(bisect_search(data, 9))    # 4
print(bisect_search(data, 10))   # -1

# Insert into a sorted list
scores = [70, 80, 90]
bisect.insort(scores, 85)
print(scores)  # [70, 80, 85, 90]
```

### Step 4: Lower Bound and Upper Bound

```python
import bisect

data = [1, 3, 5, 5, 5, 7, 9]

# bisect_left: position of the first occurrence
print(bisect.bisect_left(data, 5))   # 2

# bisect_right: position after the last occurrence
print(bisect.bisect_right(data, 5))  # 5

# Count occurrences of 5
count = bisect.bisect_right(data, 5) - bisect.bisect_left(data, 5)
print(f"Count of 5: {count}")  # 3

# First index >= 5
lower = bisect.bisect_left(data, 5)
print(f"First position >= 5: {lower}")  # 2

# First index > 5
upper = bisect.bisect_right(data, 5)
print(f"First position > 5: {upper}")   # 5
```

### Step 5: Performance Comparison

```python
import time
import bisect


def benchmark_search(n: int):
    data = list(range(n))
    target = n - 1  # worst case

    # Linear search
    start = time.perf_counter()
    linear_search(data, target)
    t_linear = time.perf_counter() - start

    # Binary search
    start = time.perf_counter()
    binary_search(data, target)
    t_binary = time.perf_counter() - start

    # bisect
    start = time.perf_counter()
    bisect.bisect_left(data, target)
    t_bisect = time.perf_counter() - start

    print(f"n={n:>10,}: linear={t_linear:.6f}s  binary={t_binary:.6f}s  bisect={t_bisect:.6f}s")

for n in [10_000, 100_000, 1_000_000]:
    benchmark_search(n)
```

## What to Notice in This Code

- Linear search works on unsorted data; binary search requires sorted data
- Binary search handles one million items in at most 20 comparisons
- The bisect module is implemented in C and is faster than a hand-written binary search
- Understanding the difference between bisect_left and bisect_right unlocks many problem variations

## 5 Common Mistakes

| Mistake | Why It's a Problem | How to Fix It |
|---------|-------------------|---------------|
| Using binary search on unsorted data | Returns wrong results | Sort the data first or verify it is sorted |
| Integer overflow in mid calculation | `(left + right)` can overflow in some languages | Use `left + (right - left) // 2` |
| Using `<` instead of `<=` | Misses the case where one element remains | Use `<=` in the while condition |
| Infinite loop | Wrong update of left/right causes no convergence | Always use `mid + 1` and `mid - 1` |
| Using bisect result as direct index | bisect returns an insertion point even when the value is absent | Check whether the value at the returned position matches |

## Real-World Applications

- Database B-Tree indexes use binary search principles to locate records
- Log analysis tools find entries in a time range using binary search
- Version control systems locate the commit that introduced a bug (git bisect)
- Game matchmaking finds opponents of similar skill with binary search
- A/B testing determines optimal thresholds using binary search

## How Senior Engineers Think About This

You rarely implement binary search from scratch. The bisect module or database indexes handle most cases. But understanding binary search enables a powerful pattern called parametric search.

"Find the first/last value satisfying a condition in sorted data" is the core application of binary search and a staple of coding interviews.

## Checklist

- [ ] Compare the time complexity of linear search and binary search
- [ ] Implement binary search with a while loop
- [ ] Explain the difference between bisect_left and bisect_right
- [ ] Explain the precondition of binary search (sorted data)
- [ ] Describe real-world applications of binary search

## Exercises

1. Write a function that counts values greater than or equal to a target in a sorted list in O(log n).
2. Implement binary search recursively.
3. Find the square root of an integer N using binary search (to 6 decimal places).

## Summary and Next Steps

Linear search is O(n); binary search is O(log n). Binary search only works on sorted data, but the performance gap is dramatic as data grows. In the next article, we cover the core algorithms that sort data.

<!-- toc:begin -->
- [What Are Algorithms?](./01-what-are-algorithms.md)
- [Time Complexity and Big-O](./02-time-complexity-and-big-o.md)
- **Linear Search and Binary Search (current)**
- Sorting Algorithms (upcoming)
- Recursion and Divide and Conquer (upcoming)
- Dynamic Programming Basics (upcoming)
- Graph Traversal — BFS and DFS (upcoming)
- Shortest Path Basics (upcoming)
- Greedy Algorithms (upcoming)
- Coding Test Problem-Solving Strategies (upcoming)
<!-- toc:end -->

## References

- [Python Documentation — bisect](https://docs.python.org/3/library/bisect.html)
- [Real Python — Binary Search in Python](https://realpython.com/binary-search-python/)
- [GeeksforGeeks — Binary Search](https://www.geeksforgeeks.org/binary-search/)
- [LeetCode — Binary Search Problems](https://leetcode.com/tag/binary-search/)

Tags: Python, Algorithms, Linear Search, Binary Search, bisect
