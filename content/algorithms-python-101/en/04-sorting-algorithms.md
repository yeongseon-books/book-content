---
series: algorithms-python-101
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
  - Python
  - Algorithms
  - Sorting
  - Bubble Sort
  - Quick Sort
seo_description: Implement bubble, selection, insertion, merge, and quick sort in Python and compare their performance characteristics.
last_reviewed: '2026-05-04'
---

# Sorting Algorithms

Sorting sits underneath far more problems than most beginners expect. Binary search, ranking, grouping, and deduplication all become easier once data is in order.

Even if you use Python's built-in `sorted()` in practice, understanding the trade-offs behind classic sorting algorithms helps you reason about performance, stability, and data shape.

This is post 4 in the Algorithms with Python 101 series. Here, we'll implement several classic sorting algorithms in Python and compare how their strategies affect performance.

## What You Will Learn

- The principles and implementations of three O(n^2) sorting algorithms
- The divide-and-conquer strategies behind merge sort and quick sort
- How Python's built-in sort works and how to use the key function
- What sorting stability means and when it matters

## Why It Matters

Sorting is one of the most fundamental operations in computing. Binary search, deduplication, and ranking all assume sorted data. Beyond 10,000 items, the difference between O(n^2) and O(n log n) exceeds 100x.

> Sorting arranges data in a specific order. The choice of algorithm determines whether the job finishes in milliseconds or minutes.

In practice, you use sorted() almost everywhere. But understanding the principles helps you design key functions, reason about stability, and diagnose performance bottlenecks.

## Concept Overview

> Comparison-based sorting determines order by comparing pairs of elements

```text
Bubble sort:    compare and swap adjacent elements → O(n^2)
Selection sort: find the minimum and move it to front → O(n^2)
Insertion sort: insert each element at its correct position → O(n^2), fast on nearly sorted data
Merge sort:     split in half, sort, merge → O(n log n), stable
Quick sort:     partition around a pivot → average O(n log n)
```

## Key Concepts

| Term | Description |
|------|-------------|
| Stable sort | Preserves the original order of equal elements |
| In-place sort | Uses only O(1) extra memory |
| Comparison sort | Determines order by comparing elements; lower bound is O(n log n) |
| Pivot | The element used as the partition boundary in quick sort |
| Divide and conquer | Split the problem, solve each part, combine the results |

## Before / After

Two approaches to sorting a list.

```python
# before: bubble sort — O(n^2)
def sort_data(data):
    n = len(data)
    for i in range(n):
        for j in range(n - 1 - i):
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]
    return data
```

```python
# after: built-in sort — O(n log n), Timsort
def sort_data(data):
    return sorted(data)
```

## Hands-On Steps

### Step 1: Bubble Sort

```python
def bubble_sort(data: list[int]) -> list[int]:
    """Bubble sort — O(n^2), stable, in-place."""
    arr = data[:]
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr

print(bubble_sort([5, 3, 8, 1, 2]))  # [1, 2, 3, 5, 8]
```

### Step 2: Selection Sort and Insertion Sort

```python
def selection_sort(data: list[int]) -> list[int]:
    """Selection sort — O(n^2), unstable, in-place."""
    arr = data[:]
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr


def insertion_sort(data: list[int]) -> list[int]:
    """Insertion sort — O(n^2), stable, fast on nearly sorted data."""
    arr = data[:]
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr

data = [64, 25, 12, 22, 11]
print(selection_sort(data))   # [11, 12, 22, 25, 64]
print(insertion_sort(data))   # [11, 12, 22, 25, 64]
```

### Step 3: Merge Sort

```python
def merge_sort(data: list[int]) -> list[int]:
    """Merge sort — O(n log n), stable, O(n) extra space."""
    if len(data) <= 1:
        return data[:]
    mid = len(data) // 2
    left = merge_sort(data[:mid])
    right = merge_sort(data[mid:])
    return _merge(left, right)


def _merge(left: list[int], right: list[int]) -> list[int]:
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:  # <= ensures stability
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

print(merge_sort([38, 27, 43, 3, 9, 82, 10]))
# [3, 9, 10, 27, 38, 43, 82]
```

### Step 4: Quick Sort

```python
def quick_sort(data: list[int]) -> list[int]:
    """Quick sort — average O(n log n), worst O(n^2)."""
    if len(data) <= 1:
        return data[:]
    pivot = data[len(data) // 2]
    left = [x for x in data if x < pivot]
    middle = [x for x in data if x == pivot]
    right = [x for x in data if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

print(quick_sort([3, 6, 8, 10, 1, 2, 1]))
# [1, 1, 2, 3, 6, 8, 10]
```

### Step 5: Built-in Sort and Benchmarks

```python
import time


def benchmark_sort(n: int):
    import random
    data = [random.randint(0, n) for _ in range(n)]

    algorithms = [
        ("Bubble", bubble_sort),
        ("Selection", selection_sort),
        ("Insertion", insertion_sort),
        ("Merge", merge_sort),
        ("Quick", quick_sort),
        ("Built-in", sorted),
    ]

    for name, func in algorithms:
        arr = data[:]
        start = time.perf_counter()
        func(arr)
        elapsed = time.perf_counter() - start
        print(f"  {name}: {elapsed:.4f}s")


for n in [1_000, 5_000]:
    print(f"n={n:,}")
    benchmark_sort(n)
```

## What to Notice in This Code

- Bubble sort's early termination (swapped flag) gives O(n) on already-sorted data
- The `<=` comparison in merge sort guarantees stability
- Quick sort's pivot selection determines performance; choosing the middle value reduces worst-case risk
- Python's sorted() uses Timsort, a hybrid of insertion sort and merge sort

## 5 Common Mistakes

| Mistake | Why It's a Problem | How to Fix It |
|---------|-------------------|---------------|
| Mutating the original list | Caller sees unexpected changes | Work on a copy or use sorted() |
| Choosing the first element as pivot | O(n^2) on already-sorted data | Use the middle element or random pivot |
| Using an unstable sort where stability is needed | Equal elements lose their original order | Use sorted() or merge sort |
| Wrong sort key | Results do not match the intended order | Specify the key function explicitly |
| Using O(n^2) sorts on large data | Takes seconds on tens of thousands of items | Use an O(n log n) algorithm or built-in sort |

## Real-World Applications

- Database ORDER BY clauses use sorting algorithms internally
- Log analysis sorts events by timestamp
- Search engines sort results by relevance score
- pandas sort_values() uses Timsort under the hood
- Leaderboards and ranking systems depend on real-time sorting

## How Senior Engineers Think About This

In practice, you almost never implement a sorting algorithm yourself. sorted() and list.sort() cover virtually every case. The real skill is designing the key function correctly.

Still, knowing the principles matters. Understanding "why this sort is slow" or "why stability matters here" helps you choose the right tool.

## Checklist

- [ ] Explain the differences among the three O(n^2) sorts
- [ ] Describe the divide-and-conquer process for merge sort and quick sort
- [ ] Explain stable vs unstable sorting
- [ ] Use sorted() with a custom key function
- [ ] Choose an appropriate sorting strategy for a given scenario

## Exercises

1. Write a function that sorts a list of dictionaries by multiple keys (e.g., age then name).
2. Modify quick sort to use a random pivot.
3. Benchmark insertion sort on nearly-sorted data vs random data and explain the result.

## Summary and Next Steps

O(n^2) sorts are easy to understand but impractical for large datasets. O(n log n) sorts — merge sort and quick sort — use divide and conquer. In the next article, we explore the divide-and-conquer pattern and recursion in depth.

<!-- toc:begin -->
- [What Are Algorithms?](./01-what-are-algorithms.md)
- [Time Complexity and Big-O](./02-time-complexity-and-big-o.md)
- [Linear Search and Binary Search](./03-linear-and-binary-search.md)
- **Sorting Algorithms (current)**
- Recursion and Divide and Conquer (upcoming)
- Dynamic Programming Basics (upcoming)
- Graph Traversal — BFS and DFS (upcoming)
- Shortest Path Basics (upcoming)
- Greedy Algorithms (upcoming)
- Coding Test Problem-Solving Strategies (upcoming)
<!-- toc:end -->

## References

- [Python Documentation — Sorting HOW TO](https://docs.python.org/3/howto/sorting.html)
- [Wikipedia — Sorting Algorithm](https://en.wikipedia.org/wiki/Sorting_algorithm)
- [Visualgo — Sorting Visualization](https://visualgo.net/en/sorting)
- [Real Python — How to Use sorted() and sort()](https://realpython.com/python-sort/)

Tags: Python, Algorithms, Sorting, Bubble Sort, Quick Sort
