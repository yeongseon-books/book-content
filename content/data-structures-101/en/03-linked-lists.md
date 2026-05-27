---
series: data-structures-101
episode: 3
title: "Data Structures 101 (3/10): Linked Lists"
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
  - Data Structures
  - Linked List
  - Pointers
  - Nodes
  - Memory
seo_description: How singly and doubly linked lists are built, how they compare with arrays, and when a linked list is the right choice in production code.
last_reviewed: '2026-05-04'
---

# Data Structures 101 (3/10): Linked Lists

> Data Structures 101 series (3/10)

**Core question**: Inserting a value in the middle of an array shifts every element by one slot. Is there a structure that avoids that?

> A linked list stores each value in a node that holds a pointer to the next node. Even when scattered across memory, you can visit values in order by following the pointers. Inserting or removing a node only updates the two pointers around it — that is O(1). On the other hand, indexing must follow pointers from the head and is O(n). This article walks through singly and doubly linked lists and the trade-offs between them.

This is the 3rd post in the Data Structures 101 series.


![data structures 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-101/03/03-01-big-picture.en.png)
*data structures 101 chapter 3 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Linked Lists?
- Which signal should the example or diagram make visible for Linked Lists?
- What failure should be prevented first when Linked Lists reaches a real system?

## What You Will Learn

- The structural difference between singly and doubly linked lists
- The time and space comparisons between linked lists and arrays
- How to manipulate pointers by implementing linked lists yourself
- When linked lists fit a real-world workload and when they do not

## Why It Matters

Linked lists are at the heart of system software — operating-system kernels, LRU caches, free-memory lists. They also form the foundation of more complex structures like trees and graphs. Pointer manipulation is awkward at first, but once you understand it, a far wider library of structures opens up.

> An array groups data by position. A linked list groups data by relationship.

> A singly linked list stores only a "next" pointer per node — small memory footprint, but reverse traversal is hard. A doubly linked list keeps both directions, so both ends are fast, at the cost of an extra pointer per node.

```text
Singly linked list
[10 | →] → [20 | →] → [30 | →] → [40 | None]
  ↑
 head

Doubly linked list
None ← [10 | ↔] ↔ [20 | ↔] ↔ [30 | ↔] ↔ [40] → None
         ↑                              ↑
        head                          tail
```

## Key Terms

| Term | Meaning |
| --- | --- |
| Node | A unit holding a value and pointers |
| Pointer | The memory address of another node |
| Head | A reference to the first node |
| Tail | A reference to the last node (often kept in doubly linked) |
| Sentinel | A dummy node that simplifies edge handling |

## Before / After

**Before — prepend on an array:**

```python
data = list(range(1_000_000))
data.insert(0, -1)         # all 1,000,000 elements shift one slot: O(n)
```

**After — prepend on a linked list:**

```python
class Node:
    __slots__ = ("value", "next")
    def __init__(self, value, next=None):
        self.value, self.next = value, next

head = None
for v in range(1_000_000):
    head = Node(v, head)   # O(1) insert each time
```

## Hands-On: Step by Step

### Step 1: Implement a Singly Linked List

```python
class Node:
    __slots__ = ("value", "next")
    def __init__(self, value, next=None):
        self.value = value
        self.next = next

class SinglyLinkedList:
    def __init__(self):
        self.head = None
        self._size = 0

    def push_front(self, value):
        self.head = Node(value, self.head)
        self._size += 1

    def pop_front(self):
        if self.head is None:
            raise IndexError("empty list")
        value = self.head.value
        self.head = self.head.next
        self._size -= 1
        return value

    def __len__(self):
        return self._size

    def __iter__(self):
        cur = self.head
        while cur is not None:
            yield cur.value
            cur = cur.next

lst = SinglyLinkedList()
for v in [3, 2, 1]:
    lst.push_front(v)
print(list(lst))   # [1, 2, 3]
```

`push_front` and `pop_front` only touch the head pointer, so both are O(1).

### Step 2: Remove a Node in the Middle

```python
def remove_value(self, target):
    """Remove the first node whose value equals target."""
    prev, cur = None, self.head
    while cur is not None:
        if cur.value == target:
            if prev is None:
                self.head = cur.next
            else:
                prev.next = cur.next
            self._size -= 1
            return True
        prev, cur = cur, cur.next
    return False

SinglyLinkedList.remove_value = remove_value

lst = SinglyLinkedList()
for v in [3, 2, 1]:
    lst.push_front(v)
lst.remove_value(2)
print(list(lst))   # [1, 3]
```

The deletion itself touches only two pointers (O(1)), but the search for the target node is O(n).

### Step 3: Doubly Linked List with Sentinels

```python
class DNode:
    __slots__ = ("value", "prev", "next")
    def __init__(self, value):
        self.value = value
        self.prev = None
        self.next = None

class DoublyLinkedList:
    def __init__(self):
        self._head = DNode(None)        # sentinel head
        self._tail = DNode(None)        # sentinel tail
        self._head.next = self._tail
        self._tail.prev = self._head
        self._size = 0

    def push_back(self, value):
        node = DNode(value)
        last = self._tail.prev
        last.next = node
        node.prev = last
        node.next = self._tail
        self._tail.prev = node
        self._size += 1

    def remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev
        self._size -= 1

    def __iter__(self):
        cur = self._head.next
        while cur is not self._tail:
            yield cur.value
            cur = cur.next
```

Sentinels remove the special cases for an empty list, the front, and the back. The code shrinks and bug counts drop.

### Step 4: Array vs Linked-List Performance

```python
import time
from collections import deque

N = 100_000

# 1. Prepend
data = []
start = time.perf_counter()
for i in range(N):
    data.insert(0, i)
print(f"list.insert(0): {(time.perf_counter() - start) * 1000:.0f} ms")

dq = deque()
start = time.perf_counter()
for i in range(N):
    dq.appendleft(i)
print(f"deque.appendleft: {(time.perf_counter() - start) * 1000:.0f} ms")
```

A deque is a (block-based) doubly linked list, so both-end inserts are O(1). When prepending dominates, reach for a deque.

### Step 5: The Limit of Index Access

```python
import time
from collections import deque

N = 100_000

lst = list(range(N))
dq = deque(range(N))

start = time.perf_counter()
for _ in range(1000):
    _ = lst[N // 2]
print(f"list[mid]: {(time.perf_counter() - start) * 1e6:.0f} us")

start = time.perf_counter()
for _ in range(1000):
    _ = dq[N // 2]
print(f"deque[mid]: {(time.perf_counter() - start) * 1e6:.0f} us")
```

A list indexes in O(1); a deque is closer to O(n). Choose based on whether end operations or random access dominate your workload.

## Notable Points

- Nodes scatter across memory, so cache friendliness is worse than for arrays
- Each node carries one or two extra pointers in memory
- End operations are O(1), but random access is O(n)
- Sentinels reduce branches and prevent bugs

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Imitating an array with index access | O(n) traversal each time | Use an array if random access dominates |
| Losing the head pointer | The whole list is gone | Manage head updates explicitly |
| Forgetting to update prev on delete | Doubly linked list breaks | Always update both directions together |
| Missing the empty-list branch | NoneType errors | Use sentinels to remove the empty case |
| Assuming memory leaks | Python's GC handles this | In C/C++ you must `free` explicitly |

## How This Is Used in Practice

- The Linux kernel ties together almost every structure with `list_head`, a doubly linked list
- LRU caches combine a hash table and a doubly linked list to update in O(1)
- Memory allocators manage free blocks as a linked list
- Music players' next/previous track navigation maps neatly onto a doubly linked list
- Text editor line structures often use a linked-list variant called a rope

## How a Senior Engineer Thinks

A senior engineer rarely uses the textbook singly linked list. For most real workloads, arrays and deques outperform it because of cache friendliness. Linked lists shine when (1) you only operate on the ends or (2) another structure already holds direct node references so deletion can happen in O(1).

A senior engineer also draws pointer manipulation on paper before coding it. Tracking pointers in your head almost always leads to mistakes. Sketching nodes and arrows step by step is the most effective way to prevent bugs.

## Checklist

- [ ] I can explain the structural difference between singly and doubly linked lists
- [ ] I understand why end inserts are O(1) and random access is O(n)
- [ ] I know the value of a sentinel node
- [ ] I can identify workloads where a linked list beats an array
- [ ] I know what kind of structure Python's deque is closer to

## Practice Problems

1. Add a `reverse()` method to the `SinglyLinkedList` above. Do not allocate a new list; only flip pointers.

2. Implement an algorithm that detects whether a singly linked list contains a cycle. Hint: use a fast and slow pointer (Floyd's Tortoise and Hare).

3. Write a function that merges two sorted singly linked lists into one sorted list. Do not create new nodes — reuse the existing ones.

## Wrap-Up and Next Steps

A linked list joins nodes through pointers, giving O(1) insertion and deletion at the ends or at known positions. In exchange, random access is O(n) and cache friendliness lags arrays. The choice between singly and doubly linked is a trade-off between the cost of an extra pointer and the ability to traverse both ways.

Next we look at two ADTs built on top of arrays or linked lists — stacks and queues. We see how the simple rules LIFO and FIFO become powerful abstractions.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Linked Lists?**
  - The article treats Linked Lists as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Linked Lists?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Linked Lists reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Data Structures 101 (1/10): What Are Data Structures?](./01-what-are-data-structures.md)
- [Data Structures 101 (2/10): Arrays and Dynamic Arrays](./02-arrays-and-dynamic-arrays.md)
- **Linked Lists (current)**
- Stacks and Queues (upcoming)
- Hash Tables (upcoming)
- Trees (upcoming)
- Binary Search Trees (upcoming)
- Heaps (upcoming)
- Graphs (upcoming)
- Choosing Data Structures (upcoming)

<!-- toc:end -->

## References

- [Open Data Structures — Chapter 3 Linked Lists](https://opendatastructures.org/ods-python/3_Linked_Lists.html)
- [Linux Kernel `list.h`](https://github.com/torvalds/linux/blob/master/include/linux/list.h)
- [Wikipedia — Linked List](https://en.wikipedia.org/wiki/Linked_list)
- [Python collections.deque docs](https://docs.python.org/3/library/collections.html#collections.deque)

Tags: Computer Science, Data Structures, Linked List, Pointers, Nodes, Memory
