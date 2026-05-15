---
series: data-structures-python-101
episode: 7
title: Heaps and Priority Queues
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
  - Heap
  - Priority Queue
  - heapq
seo_description: Implement heaps and priority queues in Python using the heapq module and learn practical usage patterns.
last_reviewed: '2026-05-04'
---

# Heaps and Priority Queues

> Data Structures with Python 101 Series (7/10)

<!-- a-grade-intro:begin -->

**Key Question**: What data structure lets you always retrieve the smallest (or largest) value quickly?

> A heap retrieves the minimum or maximum in O(1) and inserts or removes in O(log n). Python's heapq module makes heaps easy to use. This article covers heap internals, heapq usage, and priority queue patterns.

<!-- a-grade-intro:end -->

This is post 7 in the Data Structures with Python 101 series.

## What You Will Learn

- Heap structure and the heap property
- Using Python's heapq module
- Implementing a max-heap
- Practical priority queue patterns

## Why It Matters

Requirements like "process the most urgent task first" or "visit the nearest node first" appear everywhere. Sorting every time costs O(n log n), but a heap handles it in O(log n).

> A heap is a complete binary tree where the parent node is always smaller (min-heap) or larger (max-heap) than its children.

Core algorithms like Dijkstra's shortest path, job schedulers, and event simulations are all built on heaps.

## Concept Overview

> Heap = a complete binary tree where the parent is always smaller than its children (min-heap)

```
[Min-Heap]               [Array Representation]
      1                   index: 0  1  2  3  4  5
    /   \                  value: [1, 3, 5, 7, 4, 8]
   3     5
  / \   /                Parent i's children: 2i+1, 2i+2
 7   4 8                 Child i's parent: (i-1)//2
```

## Key Concepts

| Term | Description |
|------|------------|
| min-heap | A complete binary tree where the parent is always smaller than its children |
| max-heap | A complete binary tree where the parent is always larger than its children |
| heapify | An operation that converts an array into heap order in O(n) |
| priority queue | An abstract data type that dequeues the highest-priority element first |
| complete binary tree | A tree where every level except the last is completely filled |

## Before / After

Compare repeatedly extracting the smallest value by sorting versus using a heap.

```python
# before: sort to extract minimum — O(n log n) per extraction
tasks = [5, 3, 8, 1, 4]
tasks.sort()
smallest = tasks.pop(0)  # sort then pop — inefficient
```

```python
# after: heapq for minimum extraction — O(log n) per extraction
import heapq
tasks = [5, 3, 8, 1, 4]
heapq.heapify(tasks)           # O(n) to build the heap
smallest = heapq.heappop(tasks) # O(log n) to extract minimum
```

## Hands-On Steps

### Step 1: Basic heapq usage

```python
import heapq

data = [5, 3, 8, 1, 4, 2]

# Convert list to heap — O(n)
heapq.heapify(data)
print(data)  # [1, 3, 2, 5, 4, 8] — heap order

# Peek at minimum — O(1)
print(data[0])  # 1

# Extract minimum — O(log n)
print(heapq.heappop(data))  # 1
print(heapq.heappop(data))  # 2

# Insert value — O(log n)
heapq.heappush(data, 0)
print(data[0])  # 0
```

### Step 2: Implement a max-heap (negate values)

```python
import heapq

# Python heapq only supports min-heaps
# Implement max-heap by negating values
max_heap = []
for val in [5, 3, 8, 1, 4]:
    heapq.heappush(max_heap, -val)

# Extract maximum
print(-heapq.heappop(max_heap))  # 8
print(-heapq.heappop(max_heap))  # 5
print(-heapq.heappop(max_heap))  # 4
```

### Step 3: Solve Top-K problems

```python
import heapq

scores = [85, 92, 78, 95, 88, 76, 91, 83, 97, 80]

# Top 3 — O(n log k)
top3 = heapq.nlargest(3, scores)
print(f"top 3: {top3}")  # [97, 95, 92]

# Bottom 3
bottom3 = heapq.nsmallest(3, scores)
print(f"bottom 3: {bottom3}")  # [76, 78, 80]
```

### Step 4: Implement a priority queue

```python
import heapq

class PriorityQueue:
    def __init__(self):
        self._heap = []
        self._counter = 0  # maintains insertion order for equal priorities

    def push(self, priority: int, item):
        heapq.heappush(self._heap, (priority, self._counter, item))
        self._counter += 1

    def pop(self):
        if not self._heap:
            raise IndexError("pop from empty queue")
        priority, _, item = heapq.heappop(self._heap)
        return item

    def peek(self):
        if not self._heap:
            raise IndexError("peek at empty queue")
        return self._heap[0][2]

    def __len__(self):
        return len(self._heap)

pq = PriorityQueue()
pq.push(3, "low priority task")
pq.push(1, "urgent task")
pq.push(2, "normal task")

print(pq.pop())  # "urgent task"
print(pq.pop())  # "normal task"
print(pq.pop())  # "low priority task"
```

### Step 5: Merge sorted lists

```python
import heapq

list1 = [1, 4, 7, 10]
list2 = [2, 5, 8, 11]
list3 = [3, 6, 9, 12]

# Merge multiple sorted iterables into one — O(n log k)
merged = list(heapq.merge(list1, list2, list3))
print(merged)  # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
```

## What to Notice in This Code

- heapq only supports min-heaps, so max-heaps use value negation
- heapify is O(n), but n individual heappush calls are O(n log n)
- Use a counter in priority queues to avoid comparison errors on equal priorities
- nlargest/nsmallest are more efficient than sorted() when k is small

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|-------------------|-----|
| Using append then heapify instead of heappush | Each call becomes O(n) | Use heappush for O(log n) insertion |
| Trying to delete arbitrary elements | heapq does not support arbitrary deletion | Use the lazy deletion pattern |
| Using custom comparators for max-heap | Python heaps do not accept comparison functions | Use value negation or a wrapper class |
| Checking heap[-1] for the maximum | heap[-1] is not guaranteed to be the maximum | Only heap[0] is guaranteed to be the minimum |
| Pushing uncomparable objects into the heap | Causes TypeError | Use (priority, counter, item) tuples |

## Real-World Applications

- Job schedulers process the highest-priority tasks first
- Dijkstra's shortest path algorithm selects the nearest node
- Event simulations process the earliest event first
- Log merging combines multiple sorted log files in time order
- Real-time median calculation uses both a max-heap and a min-heap

## How Senior Engineers Think About This

You will use queue.PriorityQueue (thread-safe) or asyncio.PriorityQueue more often than heapq directly. But both are built on heapq internally, so understanding heapq is fundamental.

Top-K problems appear frequently in interviews. Solving them with "heap in O(n log k)" instead of "sort then slice" makes a strong impression on interviewers.

## Checklist

- [ ] Can explain the heap structure and heap property
- [ ] Can use heapify, heappush, and heappop from heapq
- [ ] Can implement a max-heap using value negation
- [ ] Can implement a priority queue with heapq
- [ ] Can solve Top-K problems with nlargest/nsmallest

## Exercises

1. Write a class that computes the real-time median from a stream of integers. (Hint: max-heap + min-heap)
2. Write a function that merges K sorted lists without using heapq.merge.
3. Implement a priority queue that processes tasks based on both priority and deadline.

## Summary and Next Steps

Heaps efficiently manage minimum and maximum values, and Python's heapq module makes them easy to use. The next article covers graphs — data structures that represent relationships with nodes and edges.

<!-- toc:begin -->
- [What Are Data Structures?](./01-what-are-data-structures.md)
- [Arrays and Lists](./02-arrays-and-lists.md)
- [Stacks and Queues](./03-stacks-and-queues.md)
- [Hash Tables and dict](./04-hash-tables-and-dict.md)
- [Linked Lists](./05-linked-lists.md)
- [Trees and Binary Trees](./06-trees-and-binary-trees.md)
- **Heaps and Priority Queues (current)**
- Graph Representations (upcoming)
- Sets and Set Operations (upcoming)
- Choosing the Right Data Structure (upcoming)
<!-- toc:end -->

## References

- [Python Docs — heapq](https://docs.python.org/3/library/heapq.html)
- [Real Python — The Python heapq Module](https://realpython.com/python-heapq-module/)
- [GeeksforGeeks — Heap Data Structure](https://www.geeksforgeeks.org/heap-data-structure/)
- [Visualgo — Heap Visualization](https://visualgo.net/en/heap)

Tags: Python, Data Structures, Heap, Priority Queue, heapq
