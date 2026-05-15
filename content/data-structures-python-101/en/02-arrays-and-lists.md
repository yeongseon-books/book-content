---
series: data-structures-python-101
episode: 2
title: Arrays and Lists
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
  - Data Structures
  - list
  - array
  - Time Complexity
seo_description: Understand how Python list works internally as a dynamic array, and learn the time complexity of common list operations.
last_reviewed: '2026-05-04'
---

# Arrays and Lists

> Data Structures with Python 101 Series (2/10)

<!-- a-grade-intro:begin -->

**Key Question**: Is Python's list an array or a linked list?

> Python's list is implemented internally as a dynamic array. Index access is O(1), but insertion or deletion in the middle is O(n). This article covers the difference between arrays and lists, how Python list works under the hood, and its performance characteristics.

<!-- a-grade-intro:end -->

This is post 2 in the Data Structures with Python 101 series.

## What You Will Learn

- The difference between static arrays and dynamic arrays
- How Python list is implemented internally
- Time complexity of common list operations
- The difference between the array module and list

## Why It Matters

list is the most commonly used data structure in Python. Without understanding how it works internally, it is easy to write inefficient code. For example, if you do not know why inserting at the front of a list is slow, finding the root cause of a performance issue becomes difficult.

> Understanding list deeply means understanding the foundation of stacks, queues, heaps, and other data structures.

list is also the building block for other data structures. Stacks use append/pop, heaps use heapq on top of list. Deep knowledge of list makes learning the rest much easier.

## Concept Overview

> Dynamic array = an array that grows automatically as elements are added

```
[static array]     fixed size, determined at declaration
  +---+---+---+---+
  | 1 | 2 | 3 | 4 |  <- 4 slots, fixed
  +---+---+---+---+

[dynamic array]    doubles when capacity is exceeded
  +---+---+---+---+---+---+---+---+
  | 1 | 2 | 3 | 4 |   |   |   |   |  <- extra capacity reserved
  +---+---+---+---+---+---+---+---+
```

## Key Concepts

| Term | Description |
|------|------------|
| Static Array | A fixed-size array, like `int arr[10]` in C |
| Dynamic Array | An array that automatically grows when elements are added |
| Index Access | Retrieving an element by position in O(1) |
| Slicing | Creating a sub-list with `list[start:end]` |
| Amortized O(1) | append occasionally triggers array expansion, but averages to O(1) |

## Before / After

Compare an inefficient and efficient way to insert at the front of a list.

```python
# before: insert at front of list — O(n), shifts all elements
data = [1, 2, 3, 4, 5]
data.insert(0, 0)  # every element shifts one position to the right
```

```python
# after: insert at front with deque — O(1)
from collections import deque
data = deque([1, 2, 3, 4, 5])
data.appendleft(0)  # O(1) insertion at the front
```

## Hands-On Steps

### Step 1: Verify basic list operations and their time complexity

```python
numbers = [10, 20, 30, 40, 50]

# index access — O(1)
print(numbers[2])     # 30

# append — amortized O(1)
numbers.append(60)
print(numbers)        # [10, 20, 30, 40, 50, 60]

# pop from end — O(1)
last = numbers.pop()
print(last)           # 60
```

### Step 2: Measure the cost of mid-list insertion and deletion

```python
import time

size = 100_000
data = list(range(size))

# insert at front — O(n)
start = time.perf_counter()
data.insert(0, -1)
insert_front = time.perf_counter() - start

# insert at end — O(1)
start = time.perf_counter()
data.append(-1)
insert_end = time.perf_counter() - start

print(f"front insert: {insert_front:.6f}s")
print(f"end   insert: {insert_end:.6f}s")
print(f"front insert is {insert_front / max(insert_end, 1e-9):.0f}x slower")
```

### Step 3: Use slicing

```python
data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

print(data[2:5])    # [2, 3, 4]
print(data[::2])    # [0, 2, 4, 6, 8] — even indices
print(data[::-1])   # [9, 8, 7, 6, 5, 4, 3, 2, 1, 0] — reversed
```

### Step 4: Transform with list comprehension

```python
# list of squares
squares = [x ** 2 for x in range(10)]
print(squares)  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# filter with condition
evens = [x for x in range(20) if x % 2 == 0]
print(evens)    # [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
```

### Step 5: Compare the array module with list

```python
from array import array

# array: type-fixed array — memory efficient
int_array = array('i', [1, 2, 3, 4, 5])  # 'i' = signed int
print(int_array[0])  # 1

# list can mix types
mixed = [1, "hello", 3.14, True]
print(mixed)
```

## What to Notice in This Code

- Index access and append on a list are O(1), but insert(0, x) is O(n)
- Slicing creates a new list and costs O(k) time and space (k = slice length)
- List comprehensions are faster and more readable than for loops
- The array module stores only one type to save memory, but list is the default choice

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|-------------------|-----|
| Calling list.insert(0, x) in a loop | Becomes O(n squared), extremely slow on large data | Use deque.appendleft() |
| Copying a list with `b = a` | Both reference the same object; changes to one affect the other | Use `b = a[:]` or `b = a.copy()` |
| Initializing nested lists with `[[] * 3]` | All inner lists reference the same object | Use `[[] for _ in range(3)]` |
| Modifying a list while iterating | Indices shift and produce unexpected results | Create a new list or iterate in reverse |
| Assuming len() is O(n) | Leads to unnecessary caching of the length | Python's len() is O(1) — call it directly |

## Real-World Applications

- API responses arrive as JSON arrays and are processed as lists
- Log data is collected in a list and batch-processed
- List comprehensions build data transformation pipelines
- Slicing implements pagination (items[offset:offset+limit])
- Large numerical data uses NumPy arrays instead of the array module

## How Senior Engineers Think About This

In most situations Python list is fast enough. Performance optimization comes after profiling reveals a bottleneck. But knowing that "inserting at the front of a list is slow" lets you pick the right data structure from the start.

When using list in production, the first question is: "What operations will I run on this list most often?" If you only add and remove from the end, list is ideal. If you need both ends, use deque. If lookups dominate, use set or dict.

## Checklist

- [ ] Can explain that Python list is implemented as a dynamic array
- [ ] Can state the time complexity of major list operations
- [ ] Can explain why insert(0, x) is slower than append(x)
- [ ] Can use slicing and list comprehensions effectively
- [ ] Can describe the difference between the array module and list

## Exercises

1. Measure the time to call insert(0, x) 1,000 times on a 100,000-element list versus deque.appendleft(x) 1,000 times.
2. Initialize a 5x5 2D list correctly and verify that setting a value at (2,3) does not affect other rows.
3. Use a list comprehension to create a list of numbers from 1 to 100 that are multiples of 3 but not multiples of 5.

## Summary and Next Steps

Python list is implemented as a dynamic array: index access is O(1), append/pop from the end is amortized O(1), and mid-list insertion/deletion is O(n). The next article covers stacks and queues built on top of list.

<!-- toc:begin -->
- [What Are Data Structures?](./01-what-are-data-structures.md)
- **Arrays and Lists (current)**
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

- [Python Official Docs — Lists](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists)
- [Python TimeComplexity — Python Wiki](https://wiki.python.org/moin/TimeComplexity)
- [CPython list implementation (GitHub)](https://github.com/python/cpython/blob/main/Objects/listobject.c)
- [Real Python — Python Lists and Tuples](https://realpython.com/python-lists-tuples/)

Tags: Python, Data Structures, list, array, Time Complexity
