---
series: algorithms-python-101
episode: 4
title: "Algorithms with Python 101 (4/10): Sorting Algorithms"
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
  - Sorting
  - Bubble Sort
  - Quick Sort
seo_description: Implement bubble, selection, insertion, merge, and quick sort in Python and compare their performance characteristics.
last_reviewed: '2026-05-04'
---

# Algorithms with Python 101 (4/10): Sorting Algorithms

This is the 4th post in the Algorithms with Python 101 series. Sorting sits underneath far more problems than most beginners expect, and binary search, ranking, grouping, and deduplication all become easier once data is in order.

This chapter uses one practical question as its spine: why is Python's built-in `sorted()` usually the default in real work? We will still implement classic algorithms, but as contrast material that helps explain performance, stability, and `key` design rather than as the main payoff.


![Algorithms with Python 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-python-101/04/04-01-big-picture.en.png)
*Algorithms with Python 101 chapter 4 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Sorting Algorithms?
- Which signal should the example or diagram make visible for Sorting Algorithms?
- What failure should be prevented first when Sorting Algorithms reaches a real system?

## What You Will Learn

- Why `sorted()` should usually be your production default
- The principles behind three O(n^2) sorting algorithms and where they stay educational
- The divide-and-conquer strategies behind merge sort and quick sort
- How Python's built-in sort, `key`, and stability pay off on real data

## Why It Matters

Sorting is one of the most fundamental operations in computing. Binary search, deduplication, and ranking all assume sorted data. Beyond 10,000 items, the gap between O(n^2) and O(n log n) becomes large enough to feel immediately.

> Sorting is not only about rearranging values. In practice, it is often about expressing the right ordering rule and verifying that equal values keep the order your system expects.

In practice, you use `sorted()` almost everywhere. But understanding the principles still matters because it lets you design better `key` functions, reason about stability, and tell whether a bottleneck comes from algorithm choice or from sorting the wrong shape of data.

## Concept Overview

> In comparison-based sorting, the real decision is not only how you compare elements, but also whether equal values keep their original order.

| Option | Core idea | Time complexity | Best use |
|------|-----------|-----------------|----------|
| `sorted(data, key=...)` | Pass an explicit ordering rule to a battle-tested built-in sort | `O(n log n)` | Production default |
| Bubble / Selection / Insertion | Rebuild comparison and movement logic by hand | `O(n^2)` | Learning and tiny inputs |
| Merge sort | Split, sort, and merge | `O(n log n)` | Divide-and-conquer + stable behavior |
| Quick sort | Partition around a pivot | average `O(n log n)` | Explaining average-case speed and pivot strategy |

## Key Concepts

| Term | Description |
|------|-------------|
| Stable sort | Preserves the original order of equal elements |
| In-place sort | Uses only O(1) extra memory |
| Comparison sort | Determines order by comparing elements; lower bound is O(n log n) |
| Pivot | The element used as the partition boundary in quick sort |
| Divide and conquer | Split the problem, solve each part, combine the results |

## Before / After

The same "sort employee records by department and join time" task leads to very different decisions.

```python
# before: starting with manual reimplementation spends effort on mechanics first
def sort_people(records):
    data = records[:]
    n = len(data)
    for i in range(n):
        for j in range(n - 1 - i):
            if (data[j]["department"], data[j]["joined_at"]) > (
                data[j + 1]["department"],
                data[j + 1]["joined_at"],
            ):
                data[j], data[j + 1] = data[j + 1], data[j]
    return data
```

```python
# after: production code usually means built-in sort + explicit key
def sort_people(records):
    return sorted(records, key=lambda record: (record["department"], record["joined_at"]))
```

## Hands-On Steps

### Step 1: Start with the production default — `sorted(..., key=...)`

```python
records = [
    {"name": "Mina", "score": 90, "submitted_at": 3},
    {"name": "Joon", "score": 75, "submitted_at": 1},
    {"name": "Sora", "score": 90, "submitted_at": 2},
    {"name": "Luca", "score": 75, "submitted_at": 4},
]

sorted_records = sorted(records, key=lambda record: record["score"])
print([(record["name"], record["score"]) for record in sorted_records])
# [('Joon', 75), ('Luca', 75), ('Mina', 90), ('Sora', 90)]

score_75_order = [record["name"] for record in sorted_records if record["score"] == 75]
score_90_order = [record["name"] for record in sorted_records if record["score"] == 90]

assert score_75_order == ["Joon", "Luca"]
assert score_90_order == ["Mina", "Sora"]

sorted_by_two_keys = sorted(
    records,
    key=lambda record: (-record["score"], record["submitted_at"]),
)
print([
    (record["name"], record["score"], record["submitted_at"])
    for record in sorted_by_two_keys
])
# [('Sora', 90, 2), ('Mina', 90, 3), ('Joon', 75, 1), ('Luca', 75, 4)]
```

The practical lesson is twofold. First, the high-value skill in production is usually designing the right `key`, not rewriting a sorting algorithm. Second, Python's built-in sort is stable, so equal-score groups keep their original order.

These checks are deliberate.

- The 75-point group should stay in `Joon → Luca` order.
- The 90-point group should stay in `Mina → Sora` order.
- If either group changes unexpectedly, first verify that you are using a stable sorting tool before you blame the `key` logic.

### Step 2: Use classic O(n²) sorts as contrast material

```python
def verify_sort(name: str, func, cases: dict[str, list[int]]) -> None:
    for case_name, values in cases.items():
        expected = sorted(values)
        actual = func(values)
        print(f"{name:>10} | {case_name:>14} | expected={expected} | actual={actual}")
        assert actual == expected, f"{name} failed on {case_name}"

test_cases = {
    "random": [5, 3, 8, 1, 2],
    "sorted": [1, 2, 3, 4, 5],
    "reversed": [5, 4, 3, 2, 1],
    "duplicates": [4, 2, 4, 1, 2, 1],
}

def bubble_sort(data: list[int]) -> list[int]:
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

def selection_sort(data: list[int]) -> list[int]:
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
    arr = data[:]
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr

verify_sort("bubble", bubble_sort, test_cases)
verify_sort("selection", selection_sort, test_cases)
verify_sort("insertion", insertion_sort, test_cases)
```

The point of splitting verification into four cases is to shorten debugging loops.

- If bubble sort fails on an already-sorted list, inspect the inner loop bound `n - 1 - i` first.
- If insertion sort fails on duplicate-heavy input, inspect `while j >= 0 and arr[j] > key:` first. Changing `>` to `>=` can break the stable behavior you expect.
- If selection sort produces the right values but equal-value order changes, that is not a bug in your printout. It is the definition of an unstable sort.

### Step 3: Merge sort shows where stability comes from

```python
def merge_sort(data: list[int]) -> list[int]:
    if len(data) <= 1:
        return data[:]
    mid = len(data) // 2
    left = merge_sort(data[:mid])
    right = merge_sort(data[mid:])
    return _merge(left, right)

def _merge(left: list[int], right: list[int]) -> list[int]:
    result: list[int] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

verify_sort("merge", merge_sort, test_cases)

def merge_sort_records(records: list[dict[str, int | str]]) -> list[dict[str, int | str]]:
    if len(records) <= 1:
        return records[:]
    mid = len(records) // 2
    left = merge_sort_records(records[:mid])
    right = merge_sort_records(records[mid:])
    return merge_records(left, right)

def merge_records(left, right):
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i]["score"] <= right[j]["score"]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged

stable_records = merge_sort_records(records)
assert [record["name"] for record in stable_records if record["score"] == 75] == ["Joon", "Luca"]
assert [record["name"] for record in stable_records if record["score"] == 90] == ["Mina", "Sora"]
```

Merge sort is a classic divide-and-conquer example: split, sort each half, and merge. The important practical detail is that equal-score order survives because of the `<=` comparison inside the merge step.

If numeric output is correct but equal-score order changes, inspect `merge_records()` first and verify that `<=` did not become `<`.

### Step 4: Quick sort is fast on average, but verify it the same way

```python
def quick_sort(data: list[int]) -> list[int]:
    if len(data) <= 1:
        return data[:]
    pivot = data[len(data) // 2]
    left = [x for x in data if x < pivot]
    middle = [x for x in data if x == pivot]
    right = [x for x in data if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

verify_sort("quick", quick_sort, test_cases)
```

Quick sort partitions around a pivot. It is often fast, but poor pivot choice can still push it toward O(n^2). If reverse-sorted data behaves suspiciously, inspect the pivot rule and partition conditions before anything else.

### Step 5: Benchmark growth trends, not one noisy number

```python
import random
import time

def benchmark_sort(n: int) -> list[tuple[str, float, bool]]:
    data = [random.randint(0, n) for _ in range(n)]

    algorithms = [
        ("Bubble", bubble_sort),
        ("Selection", selection_sort),
        ("Insertion", insertion_sort),
        ("Merge", merge_sort),
        ("Quick", quick_sort),
        ("Built-in", sorted),
    ]

    results = []
    for name, func in algorithms:
        start = time.perf_counter()
        actual = func(data[:])
        elapsed = time.perf_counter() - start
        is_correct = actual == sorted(data)
        results.append((name, elapsed, is_correct))
    return results

for n in [1_000, 5_000]:
    print(f"n={n:,}")
    for name, elapsed, is_correct in benchmark_sort(n):
        print(f"  {name:>8}: {elapsed:.4f}s | correct={is_correct}")
        assert is_correct, f"{name} produced a wrong result for n={n}"
```

The goal of this benchmark is not to memorize which line is smaller on one run. The real signal is the growth trend as input size increases.

If bubble sort looks less terrible on a tiny sample than you expected, do not over-read that number. Compare the curve as `n` grows rather than single-run noise.

## What to Notice in This Code

- The production default is not algorithm reimplementation. It is `sorted(..., key=...)`.
- Bubble sort's early termination (`swapped`) can reduce best-case work on already-sorted input.
- The `<=` comparison in merge sort preserves the order of equal values.
- Quick sort's pivot choice strongly affects performance.
- Verification loops should separate random, already-sorted, reverse-sorted, and duplicate-heavy inputs so failures are easier to diagnose.

## 5 Common Mistakes

| Mistake | Why It's a Problem | How to Fix It |
|---------|-------------------|---------------|
| Mutating the original list | Caller sees unexpected changes | Work on a copy or use `sorted()` |
| Choosing the first element as pivot | O(n^2) on already-sorted data | Use the middle element or a random pivot |
| Treating an unstable study implementation as production-safe | Equal elements lose their original order | Use `sorted()` or merge sort and explicitly verify equal-key order |
| Wrong sort key | Results do not match the intended order | Specify the key function explicitly |
| Using O(n^2) sorts on large data | Takes seconds on tens of thousands of items | Use an O(n log n) algorithm or built-in sort |

## Real-World Applications

- Database `ORDER BY` clauses use sorting internally.
- Log analysis sorts events by timestamp.
- Search engines sort results by relevance score.
- pandas `sort_values()` relies on sorting internally.
- Leaderboards and ranking systems depend on real-time ordering.

## How Senior Engineers Think About This

In practice, you almost never implement a sorting algorithm yourself. `sorted()` and `list.sort()` cover virtually every case. The real skill is designing the key function correctly and verifying that equal-key groups keep the order your system expects.

Still, knowing the principles matters. Understanding "why this sort is slow," "why stability matters here," or "why the values are right but the order still looks wrong" helps you choose the right tool.

## Checklist

- [ ] Explain the differences among the three O(n^2) sorts
- [ ] Describe the divide-and-conquer process for merge sort and quick sort
- [ ] Explain stable vs unstable sorting
- [ ] Use `sorted()` with a custom key function and verify equal-key order
- [ ] Choose an appropriate sorting strategy for a given scenario

## Exercises

1. Write a function that sorts a list of dictionaries by multiple keys, such as age and then name.
2. Modify quick sort to use a random pivot.
3. Benchmark insertion sort on nearly-sorted data vs random data and explain the result.

## Summary and Next Steps

The point of learning sorting is not memorizing every algorithm equally. It is understanding that the production default is usually `sorted(..., key=...)`, while classic algorithms give you the contrast needed to reason about complexity, stability, and debugging. O(n^2) sorts are easy to understand but impractical for large datasets, and O(n log n) sorts such as merge sort and quick sort show the divide-and-conquer pattern that we explore more deeply in the next article.

## Answering the Opening Questions

- **Why should you prefer `sorted()` over implementing a sorting algorithm directly in practice?**
  - The article's conclusion is that the practical default is `sorted(..., key=...)`, not re-implementing sorting algorithms. The `records` example—sorting by score and submission time, then verifying order within same-score groups—showed that sort criteria and stability matter more than implementation.
- **How do the three `O(n²)` sorting algorithms work, and where do they belong as learning material?**
  - Bubble sort sends large values to the back, selection sort brings the minimum forward, and insertion sort places each element in its correct position. All three are good for learning comparison and movement principles, but as the benchmark showed, `O(n²)` cost makes them study-versus-contrast material once input grows.
- **How do merge sort and quicksort leverage divide and conquer?**
  - Merge sort splits the list in half then merges the two sorted halves; quicksort separates values into less-than, equal, and greater-than the pivot and recurses. The `<=` in the merge step preserves stability, and quicksort's average `O(n log n)` versus worst-case `O(n²)` depends on pivot selection—both confirmed through code.
<!-- toc:begin -->
## In this series

- [Algorithms with Python 101 (1/10): What Are Algorithms?](./01-what-are-algorithms.md)
- [Algorithms with Python 101 (2/10): Time Complexity and Big-O](./02-time-complexity-and-big-o.md)
- [Algorithms with Python 101 (3/10): Linear Search and Binary Search](./03-linear-and-binary-search.md)
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
