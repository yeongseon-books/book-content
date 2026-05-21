---
series: algorithms-python-101
episode: 2
title: "Algorithms with Python 101 (2/10): Time Complexity and Big-O"
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
  - Time Complexity
  - Big-O
  - Performance
seo_description: Understand time complexity and Big-O notation to analyze and compare algorithm performance with Python examples.
last_reviewed: '2026-05-04'
---

# Algorithms with Python 101 (2/10): Time Complexity and Big-O

Wall-clock time on your laptop is not a reliable way to judge an algorithm. Hardware, runtime, and test data all change, but the growth pattern of the algorithm stays the same.

Big-O gives you a practical language for comparing that growth before the code ever reaches production or an interview whiteboard.

This is post 2 in the Algorithms with Python 101 series. Here, we'll build an intuition for time complexity and use Big-O notation to compare algorithms more rigorously.


![Algorithms with Python 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-python-101/02/02-01-big-picture.en.png)
*Algorithms with Python 101 chapter 2 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Time Complexity and Big-O?
- Which signal should the example or diagram make visible for Time Complexity and Big-O?
- What failure should be prevented first when Time Complexity and Big-O reaches a real system?

## What You Will Learn

- What time complexity means and why wall-clock time is insufficient
- How to read and write Big-O notation
- Common complexity classes from O(1) to O(n!)
- How to analyze the time complexity of Python code

## Why It Matters

Saying "this code is slow" is vague. Big-O provides a precise, hardware-independent way to measure an algorithm's scalability. An O(n) algorithm handles 10 million items comfortably; an O(n^2) algorithm chokes at 100,000.

> Big-O notation expresses an algorithm's worst-case growth rate as input size approaches infinity, ignoring constants and lower-order terms.

Understanding time complexity is the foundation for every algorithm discussion in interviews, code reviews, and system design.

## Concept Overview

> Big-O = upper bound on the growth rate of an algorithm's running time

```text
Input Size vs Operations (approximate):
n=1,000  | O(1): 1       | O(log n): 10    | O(n): 1,000
         | O(n log n): 10,000 | O(n^2): 1,000,000 | O(2^n): ∞
```

## Key Concepts

| Term | Description |
|------|-------------|
| Time complexity | A measure of how running time grows with input size |
| Big-O notation | An upper-bound expression for worst-case growth rate |
| O(1) — constant | Running time does not depend on input size |
| O(n) — linear | Running time grows proportionally to input size |
| O(n^2) — quadratic | Running time grows with the square of input size |

## Before / After

Two ways to check for a value in a collection.

```python
# before: linear search in a list — O(n)
def contains(data: list, target) -> bool:
    for item in data:
        if item == target:
            return True
    return False
```

```python
# after: lookup in a set — O(1) average
def contains(data: set, target) -> bool:
    return target in data
```

## Hands-On Steps

### Step 1: O(1) — Constant Time

```python
def get_first(data: list) -> int:
    """Access the first element — O(1)."""
    return data[0]

def get_by_key(data: dict, key: str):
    """Dictionary lookup — O(1) average."""
    return data.get(key)

numbers = list(range(1_000_000))
print(get_first(numbers))  # 0

lookup = {"name": "Alice", "age": 30}
print(get_by_key(lookup, "name"))  # Alice
```

### Step 2: O(n) — Linear Time

```python
def linear_sum(data: list[int]) -> int:
    """Sum all elements — O(n)."""
    total = 0
    for x in data:
        total += x
    return total

def find_value(data: list[int], target: int) -> int:
    """Linear search — O(n)."""
    for i, val in enumerate(data):
        if val == target:
            return i
    return -1

data = list(range(100))
print(linear_sum(data))       # 4950
print(find_value(data, 42))   # 42
```

### Step 3: O(n^2) — Quadratic Time

```python
def bubble_sort(data: list[int]) -> list[int]:
    """Bubble sort — O(n^2)."""
    arr = data[:]
    n = len(arr)
    for i in range(n):
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def all_pairs(data: list) -> int:
    """Count all pairs — O(n^2)."""
    count = 0
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            count += 1
    return count

print(bubble_sort([5, 3, 8, 1, 2]))  # [1, 2, 3, 5, 8]
print(all_pairs(list(range(100))))    # 4950
```

### Step 4: O(log n) and O(n log n)

```python
def binary_search(sorted_data: list[int], target: int) -> int:
    """Binary search — O(log n)."""
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

data = list(range(1_000_000))
print(binary_search(data, 999_999))  # 999999

# Python's built-in sort is O(n log n) — Timsort
import random
random_data = [random.randint(0, 1000) for _ in range(1000)]
sorted_data = sorted(random_data)  # O(n log n)
print(sorted_data[:5])
```

### Step 5: Empirical Measurement

```python
import time

def measure(func, *args) -> float:
    start = time.perf_counter()
    func(*args)
    return time.perf_counter() - start

sizes = [1_000, 5_000, 10_000]
for n in sizes:
    data = list(range(n))
    t_linear = measure(linear_sum, data)
    t_quadratic = measure(all_pairs, data)
    ratio = t_quadratic / t_linear if t_linear > 0 else 0
    print(f"n={n:>6}: linear={t_linear:.5f}s  quadratic={t_quadratic:.5f}s  ratio={ratio:.0f}x")
```

## What to Notice in This Code

- O(1) operations like dictionary lookup stay constant regardless of data size
- O(n) and O(n^2) differ dramatically — at n=10,000, quadratic is roughly 10,000x slower than linear
- Binary search demonstrates O(log n): searching 1 million items takes about 20 comparisons
- Python's built-in `sorted()` uses Timsort, an O(n log n) hybrid algorithm

## 5 Common Mistakes

| Mistake | Why It's a Problem | How to Fix It |
|---------|-------------------|---------------|
| Confusing O(n) with O(1) | Lists and sets have different lookup costs | Know which operations are O(1) for each data structure |
| Ignoring nested loops | An inner loop makes the total O(n^2) | Count the nesting depth |
| Forgetting hidden costs | `in` on a list is O(n), not O(1) | Check the data structure's complexity table |
| Optimizing prematurely | Micro-optimizing O(n) code while ignoring O(n^2) elsewhere | Profile first, optimize the biggest bottleneck |
| Confusing best, average, and worst case | Big-O is worst case by convention | Be explicit about which case you are analyzing |

## Real-World Applications

- Database query planners choose indexes based on time complexity analysis
- Search engines use O(1) hash lookups for inverted indexes
- Video streaming uses O(n log n) sorting for recommendation ranking
- Network routers use O(log n) lookups for packet forwarding tables
- Machine learning training time depends on algorithm complexity

## How Senior Engineers Think About This

You do not need to memorize every complexity class. What matters is building intuition: "If I double the input, does the runtime double (linear), quadruple (quadratic), or barely change (logarithmic)?"

In code reviews, a senior engineer spots nested loops over large data and immediately asks about the complexity. This single habit prevents most performance problems before they reach production.

## Quick complexity triage in production

- If latency jumps only after a dataset crosses a threshold, suspect an O(n²) path that stayed hidden on smaller fixtures.
- If a request handler repeatedly scans the same collection, look for a data-structure change before reaching for lower-level optimization.
- If performance work stalls, count the dominant operations first. Complexity mistakes usually outweigh constant-factor wins.

## Checklist

- [ ] Explain what Big-O notation represents
- [ ] Identify the time complexity of simple Python code
- [ ] Rank common complexity classes from fastest to slowest
- [ ] Distinguish O(n) from O(n^2) in nested loops
- [ ] Measure and compare algorithm performance empirically

## Exercises

1. Analyze the time complexity of Python's `list.index()` and `dict.__getitem__()`.
2. Write an O(n) algorithm to find duplicates in a list (hint: use a set).
3. Predict how long an O(n^2) algorithm takes for n=100,000 if it takes 1 second for n=10,000.

## Summary and Next Steps

Time complexity and Big-O notation give you a precise way to compare algorithm performance. The most important classes to remember are O(1), O(log n), O(n), O(n log n), and O(n^2). In the next article, we implement and compare two fundamental search algorithms: linear search and binary search.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Time Complexity and Big-O?**
  - The article treats Time Complexity and Big-O as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Time Complexity and Big-O?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Time Complexity and Big-O reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Algorithms with Python 101 (1/10): What Are Algorithms?](./01-what-are-algorithms.md)
- **Time Complexity and Big-O (current)**
- Linear Search and Binary Search (upcoming)
- Sorting Algorithms (upcoming)
- Recursion and Divide and Conquer (upcoming)
- Dynamic Programming Basics (upcoming)
- Graph Traversal — BFS and DFS (upcoming)
- Shortest Path Basics (upcoming)
- Greedy Algorithms (upcoming)
- Coding Test Problem-Solving Strategies (upcoming)

<!-- toc:end -->

## References

- [Big-O Cheat Sheet](https://www.bigocheatsheet.com/)
- [Python Time Complexity — Python Wiki](https://wiki.python.org/moin/TimeComplexity)
- [Real Python — Big O Notation and Algorithm Analysis](https://realpython.com/python-big-o-notation/)
- [Khan Academy — Asymptotic Notation](https://www.khanacademy.org/computing/computer-science/algorithms/asymptotic-notation/a/big-o-notation)

Tags: Python, Algorithms, Time Complexity, Big-O, Performance
