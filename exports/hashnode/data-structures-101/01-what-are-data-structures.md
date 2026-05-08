
# What Are Data Structures?

> Data Structures 101 series (1/10)

<!-- a-grade-intro:begin -->

**Core question**: The same data, the same task — yet one program finishes in one second and another takes an hour. What makes the difference?

> A data structure defines how data is laid out in memory and which operations it can support efficiently. The task "find a user among 10 million" needs five million comparisons on average if you scan an array, but only one if you use a hash table. This article defines data structures, contrasts them with abstract data types (ADTs), and maps out the entire series.

<!-- a-grade-intro:end -->

## What You Will Learn

- The relationship between a data structure and an abstract data type (ADT)
- How structure choice impacts performance
- A high-level map of the nine data structures covered in this series
- The criteria you use to compare data structures

## Why It Matters

Writing good code ultimately means making good decisions about how to represent data. Algorithms run on top of data structures. Pick the wrong structure and even the best algorithm becomes slow.

> Algorithms + Data Structures = Programs — Niklaus Wirth

This series walks through nine core data structures: how they work, their time and space complexity, and when to reach for each one.

## Concept at a Glance

> A data structure has two layers: the logical structure of the data and its physical layout in memory. An ADT defines what you can do; a data structure decides how to do it.

```text
            ADT (Abstract Data Type)
              "what can be done"
                    |
        ┌───────────┼───────────┐
        |           |           |
      List         Set         Map
        |           |           |
   ┌────┴────┐  ┌───┴───┐  ┌───┴───┐
  array  linked  hash  tree  hash  tree
        |
   (concrete data structure: memory layout)
```

## Key Terms

| Term | Meaning |
| --- | --- |
| Data structure | A concrete way to store and manipulate data in memory |
| Abstract Data Type (ADT) | A definition of data and operations at the interface level |
| Time complexity | Growth rate of operation time as input size grows |
| Space complexity | Growth rate of memory usage as input size grows |
| Amortized cost | The average cost of an operation across many invocations |

## Before / After

**Before — without thinking about data structures:**

```python
# Find a specific ID among 10 million users
users = [{"id": i, "name": f"user{i}"} for i in range(10_000_000)]


def find_user(target_id: int):
    for user in users:
        if user["id"] == target_id:
            return user
    return None


# 5 million comparisons on average, 10 million in the worst case
```

**After — with a data structure in mind:**

```python
# Index the same data with a hash table
users = {i: {"id": i, "name": f"user{i}"} for i in range(10_000_000)}


def find_user(target_id: int):
    return users.get(target_id)


# One comparison on average
```

## Hands-On: Step by Step

### Step 1: Same Data, Different Structures

```python
import time

N = 1_000_000

list_data = list(range(N))
set_data = set(list_data)


def measure(label, fn):
    start = time.perf_counter()
    fn()
    elapsed = (time.perf_counter() - start) * 1000
    print(f"{label}: {elapsed:.2f} ms")


measure("list lookup", lambda: (N - 1) in list_data)
measure("set lookup", lambda: (N - 1) in set_data)
```

A list scans from start to end; a set jumps straight to the bucket via a hash. The gap widens as the data grows.

### Step 2: Separate ADT from Implementation

```python
from abc import ABC, abstractmethod


class Stack(ABC):
    """ADT: pop returns whatever was pushed last."""

    @abstractmethod
    def push(self, value): ...

    @abstractmethod
    def pop(self): ...


class ListStack(Stack):
    def __init__(self):
        self._data = []

    def push(self, value):
        self._data.append(value)

    def pop(self):
        return self._data.pop()


class LinkedStack(Stack):
    def __init__(self):
        self._head = None

    def push(self, value):
        self._head = (value, self._head)

    def pop(self):
        value, self._head = self._head
        return value
```

The `Stack` ADT is identical, but the implementation differs. Callers only care about the interface.

### Step 3: Time Complexity Comparison Table

```python
operations = {
    "Array":             {"search": "O(n)",     "insert": "O(n)",  "delete": "O(n)"},
    "Dynamic Array":     {"search": "O(n)",     "insert": "O(1)*", "delete": "O(n)"},
    "Linked List":       {"search": "O(n)",     "insert": "O(1)",  "delete": "O(1)"},
    "Hash Table":        {"search": "O(1)",     "insert": "O(1)",  "delete": "O(1)"},
    "Balanced BST":      {"search": "O(log n)", "insert": "O(log n)", "delete": "O(log n)"},
    "Heap":              {"search": "O(n)",     "insert": "O(log n)", "min": "O(1)"},
}

for ds, ops in operations.items():
    print(f"{ds:<20} {ops}")
```

`*` marks an amortized cost. A dynamic array occasionally pays a costly resize, but on average the insert is O(1).

### Step 4: The Cost of Choosing Wrong

```python
# Scenario: process events arriving every second by priority
import heapq

events = []
# Wrong choice: sort on every insert
def add_wrong(priority, event):
    events.append((priority, event))
    events.sort()

# Right choice: a heap
heap = []
def add_right(priority, event):
    heapq.heappush(heap, (priority, event))


# add_wrong is O(n log n) per insert
# add_right is O(log n) per insert
# At 1 million events per day, that is a 1000x difference
```

### Step 5: The Series Roadmap

```python
roadmap = [
    (1, "What Are Data Structures?", "the big picture"),
    (2, "Arrays and Dynamic Arrays", "fixed/variable contiguous memory"),
    (3, "Linked Lists", "nodes connected by pointers"),
    (4, "Stacks and Queues", "LIFO and FIFO"),
    (5, "Hash Tables", "instant access by key"),
    (6, "Trees", "expressing hierarchy"),
    (7, "Binary Search Trees", "fast search in a sorted tree"),
    (8, "Heaps", "implementing priority queues"),
    (9, "Graphs", "modeling arbitrary relationships"),
    (10, "Choosing Data Structures", "when to use which"),
]

for num, title, keywords in roadmap:
    print(f"  {num:02d}. {title} — {keywords}")
```

## Notable Points

- The same ADT can have wildly different performance depending on the implementation
- Time complexity describes the growth rate at large input — small inputs may favor constant-time differences
- Amortized analysis is needed for structures like dynamic arrays and hash tables that occasionally do expensive work
- Picking the right data structure is as critical to performance as picking the right algorithm

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Conflating ADT and implementation | "A stack is an array" | Treat the ADT as interface; implementations vary |
| Judging by small inputs | "List is faster, see?" | Look at the growth rate as input scales |
| Reading only Big-O | Ignoring constants | Account for cache friendliness and benchmarks |
| Using one structure for everything | Dict for every problem | Match the structure to the access pattern |
| Ignoring space complexity | Out-of-memory crashes | Analyze space alongside time |

## How This Is Used in Practice

- Database indexes are implemented as B-Trees (a kind of tree) for fast lookup
- Operating system process schedulers use a priority queue (heap) to decide what runs next
- A web browser's back button is backed by a stack
- Routing tables, dependency graphs, and social networks are all modeled as graphs
- In-memory caches like Redis and Memcached are built on hash tables

## How a Senior Engineer Thinks

A senior engineer asks "which operations dominate?" before asking "which data structure?" Is it search-heavy, insert-heavy, or does it require ordered traversal? Once the workload is named, the structure almost picks itself.

Senior engineers also start with primitives plus dict and list. They do not reach for trees and heaps up front. They measure first and only swap in something fancier when a real bottleneck appears. Premature optimization is just as dangerous in data structures as anywhere else.

## Checklist

- [ ] I can explain the difference between a data structure and an ADT
- [ ] I understand that one ADT can have many implementations
- [ ] I know that time complexity describes growth as input scales
- [ ] I know what amortized cost means and when it applies
- [ ] I have reviewed the roadmap for the rest of the series

## Practice Problems

1. Pick a real-world system (a queue at a store, a bookshelf, a phone book) and analyze which data structure it resembles. Which operations are fast, and which are slow?

2. Run the Step 1 measurement code for N = 100k, 1M, 10M. How does the gap between list and set widen? Plot it if you can.

3. Pick a recent piece of code you wrote. List every data structure it uses. For each, ask whether a different choice would have been clearer or faster.

## Wrap-Up and Next Steps

A data structure decides how data sits in memory and which operations it can run efficiently. The same data with the wrong structure can be tens to thousands of times slower. The ADT names the interface; the data structure names the implementation. Keeping them separate sharpens your design.

Next we look at the most basic structure — the array. We compare fixed-size and dynamic arrays and trace what Python's `list` actually does under the hood.

- **What Are Data Structures? (current)**
- Arrays and Dynamic Arrays (upcoming)
- Linked Lists (upcoming)
- Stacks and Queues (upcoming)
- Hash Tables (upcoming)
- Trees (upcoming)
- Binary Search Trees (upcoming)
- Heaps (upcoming)
- Graphs (upcoming)
- Choosing Data Structures (upcoming)
## References

- [Introduction to Algorithms (CLRS) — Cormen et al.](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)
- [Open Data Structures — Pat Morin](https://opendatastructures.org/)
- [Wikipedia — Data Structure](https://en.wikipedia.org/wiki/Data_structure)
- [Python Time Complexity Wiki](https://wiki.python.org/moin/TimeComplexity)

Tags: Computer Science, Data Structures, Abstract Data Type, Algorithms, Time Complexity, Foundations

---

© 2026 YeongseonBooks. All rights reserved.
