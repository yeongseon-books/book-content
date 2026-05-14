---
series: data-structures-python-101
episode: 1
title: What Are Data Structures?
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
  - Data Structures
  - Algorithms
  - Programming Basics
  - Time Complexity
seo_description: Learn what data structures are, why they matter in Python, and get a roadmap for the core structures every developer should know.
last_reviewed: '2026-05-04'
---

# What Are Data Structures?

> Data Structures with Python 101 Series (1/10)

<!-- a-grade-intro:begin -->

**Key Question**: If you can store data in a variable, why bother learning data structures?

> When data grows, a single variable is not enough. The structure you choose determines whether a search takes 0.001 seconds or 10 seconds. This article explains what data structures are, why they matter, and which ones Python provides out of the box.

<!-- a-grade-intro:end -->

This is the first post in the Data Structures with Python 101 series.

## What You Will Learn

- The definition and role of data structures
- How data structure choices affect performance
- Built-in data structures in Python and their characteristics
- A roadmap of data structures covered in this series

## Why It Matters

A program takes data in, processes it, and produces output. How you store that data determines whether a task finishes in milliseconds or seconds. Data structures are the key to that difference.

> A data structure is a way to organize data for efficient access and modification. Choosing the right one makes code simpler and faster.

Data structure questions are a staple of coding interviews for good reason. Understanding data structures broadens how you see problems and helps you design optimal solutions.

## Concept Overview

> Data Structure = a method for organizing data so it can be accessed and modified efficiently

```text
[single variable]    →  stores 1 value
[list]               →  stores N values in order
[dict]               →  stores N key-value pairs (O(1) lookup)
[tree]               →  represents hierarchies (O(log n) search)
[graph]              →  represents networks of relationships
```

## Key Concepts

| Term | Description |
|------|------------|
| Data Structure | A way of organizing data that determines the efficiency of insert, delete, and search operations |
| Time Complexity | Describes how long an operation takes relative to the size of the data |
| Space Complexity | Describes how much memory a data structure uses |
| Abstract Data Type (ADT) | Defines only the operations, hiding the implementation details |
| Built-in Data Structures | Structures Python provides by default: list, dict, set, tuple, etc. |

## Before / After

Compare the difference between not knowing and knowing data structures.

```python
# before: searching in a list — O(n)
users = ["alice", "bob", "charlie", "diana"]
if "charlie" in users:
    print("found")
```

```python
# after: searching in a set — O(1)
users = {"alice", "bob", "charlie", "diana"}
if "charlie" in users:
    print("found")
```

## Hands-On Steps

### Step 1: Compare search speed between list and set

```python
import time

data_list = list(range(1_000_000))
data_set = set(range(1_000_000))

target = 999_999

start = time.perf_counter()
_ = target in data_list
list_time = time.perf_counter() - start

start = time.perf_counter()
_ = target in data_set
set_time = time.perf_counter() - start

print(f"list search: {list_time:.6f}s")
print(f"set  search: {set_time:.6f}s")
print(f"set is {list_time / set_time:.0f}x faster")
```

### Step 2: Verify O(1) key-value lookup with dict

```python
scores = {"alice": 95, "bob": 82, "charlie": 90}
print(scores["bob"])          # 82 — O(1) access
print(scores.get("diana", 0)) # 0 — default when key is missing
```

### Step 3: Represent immutable data with tuple

```python
point = (3, 4)
# point[0] = 5  # TypeError — tuples are immutable
print(f"x={point[0]}, y={point[1]}")
```

### Step 4: Use a list as a stack

```python
stack = []
stack.append("a")
stack.append("b")
stack.append("c")
print(stack.pop())  # "c" — last in, first out
print(stack.pop())  # "b"
```

### Step 5: Explore the collections module

```python
from collections import deque, Counter, defaultdict

# deque: O(1) insert/delete at both ends
dq = deque([1, 2, 3])
dq.appendleft(0)
print(list(dq))  # [0, 1, 2, 3]

# Counter: frequency counting
counter = Counter("abracadabra")
print(counter.most_common(3))  # [('a', 5), ('b', 2), ('r', 2)]

# defaultdict: dict with default values
dd = defaultdict(list)
dd["fruits"].append("apple")
print(dd)  # defaultdict(<class 'list'>, {'fruits': ['apple']})
```

## What to Notice in This Code

- The `in` operator on a list is O(n), but on a set it is O(1)
- dict retrieves values by key in O(1), making it ideal for frequent lookups
- Tuples are immutable and can be used as dict keys or set elements
- The collections module provides specialized data structures for common patterns

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|-------------------|-----|
| Using list everywhere | Search is O(n), slow on large data | Use set or dict when lookups are frequent |
| Using a list as a dict key | Lists are mutable and unhashable | Convert to tuple first |
| Ignoring data structure size | Can cause memory exhaustion | Choose a structure that fits the data scale |
| Relying on insertion order with set | Sets do not guarantee order | Use list or OrderedDict when order matters |
| Ignoring time complexity during implementation | Works on small data but fails at scale | Check operation complexity before choosing a structure |

## Real-World Applications

- Cache systems use dict for O(1) lookups
- Deduplication uses set to keep only unique values
- Task queues use deque for FIFO processing
- Configuration values are stored in tuples to prevent accidental modification
- Log analysis uses Counter for frequency aggregation

## How Senior Engineers Think About This

Experienced engineers ask "what structure should hold this data?" before writing code. The data structure choice determines the performance and readability of the entire architecture.

In practice, Python's built-in data structures handle most problems. The key is understanding the characteristics of list, dict, set, and tuple, and choosing the right one for the situation.

## Checklist

- [ ] Can explain the definition and role of data structures
- [ ] Can describe the differences between list, dict, set, and tuple
- [ ] Can explain why set is faster than list for lookups
- [ ] Can use deque, Counter, and defaultdict from the collections module
- [ ] Understands time complexity and can apply it to data structure selection

## Exercises

1. Write code that searches for a value in a list of 1 million integers and in a set. Compare the execution times.
2. Write a function that removes duplicates from a list of strings while preserving the original order. (Hint: use dict.fromkeys)
3. Store student name-score data in a dict and print it sorted by score in descending order.

## Summary and Next Steps

Data structures are a fundamental concept for storing and accessing data efficiently. Python provides powerful built-in structures like list, dict, set, and tuple. The next article takes a deep dive into the most basic of these: arrays and lists.

<!-- toc:begin -->
- **What Are Data Structures? (current)**
- Arrays and Lists (upcoming)
- Stacks and Queues (upcoming)
- Hash Tables and dict (upcoming)
- Linked Lists (upcoming)
- Trees and Binary Trees (upcoming)
- Heaps and Priority Queues (upcoming)
- Graph Representations (upcoming)
- Sets and Set Operations (upcoming)
- Choosing the Right Data Structure (upcoming)
<!-- toc:end -->

## References

- [Python Official Docs — Data Structures](https://docs.python.org/3/tutorial/datastructures.html)
- [Problem Solving with Algorithms and Data Structures using Python](https://runestone.academy/ns/books/published/pythonds3/index.html)
- [Real Python — Common Python Data Structures](https://realpython.com/python-data-structures/)
- [Big-O Cheat Sheet](https://www.bigocheatsheet.com/)

Tags: Python, Data Structures, Algorithms, Programming Basics, Time Complexity
