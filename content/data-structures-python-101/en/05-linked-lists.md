---
series: data-structures-python-101
episode: 5
title: "Data Structures with Python 101 (5/10): Linked Lists"
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
  - Linked List
  - Node
  - Pointers
seo_description: Implement singly and doubly linked lists in Python and compare their performance characteristics with arrays.
last_reviewed: '2026-05-15'
---

# Data Structures with Python 101 (5/10): Linked Lists

> Data Structures with Python 101 Series (5/10)

**Key Question**: Python already has list — why learn linked lists?

> Python list is array-based, so mid-list insertion and deletion are O(n). Linked lists connect nodes with pointers, achieving O(1) insertion and deletion. This article implements singly and doubly linked lists in Python and compares them with arrays.

This is post 5 in the Data Structures with Python 101 series.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Linked Lists?
- Which signal should the example or diagram make visible for Linked Lists?
- What failure should be prevented first when Linked Lists reaches a real system?

## Big Picture

![Data Structures with Python 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-python-101/05/05-01-linked-structure-at-a-glance.en.png)

*Data Structures with Python 101 chapter 5 flow overview*

This picture places Linked Lists inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## What You Will Learn

- The structure and behavior of linked lists
- Implementing a singly linked list
- Implementing a doubly linked list
- Performance comparison between arrays and linked lists

## Why It Matters

Linked lists are the most fundamental building block in data structures. Trees, graphs, and hash table chaining all build on top of linked lists. Implementing a linked list from scratch solidifies your understanding of pointers (references).

> A linked list is a data structure where each node holds data and a reference to the next node.

Linked list problems are among the most frequently tested in coding interviews. Reversal, cycle detection, and merge problems come in many variations.

## Concept Overview

> Linked list = a linear data structure where nodes are connected by pointers

```text
[Singly Linked List]
  head -> [A|->] -> [B|->] -> [C|->] -> None

[Doubly Linked List]
  None <- [<-|A|->] <-> [<-|B|->] <-> [<-|C|->] -> None
```

## Linked Structure at a Glance

## Key Concepts

| Term | Description |
|------|------------|
| Node | A unit that holds data and a reference to the next node |
| head | Points to the first node of the linked list |
| tail | Points to the last node of the linked list |
| Singly Linked List | Each node references only the next node |
| Doubly Linked List | Each node references both the previous and the next node |

## Before / After

Compare mid-list deletion in an array versus a linked list.

```python
# before: delete from middle of list — O(n), shifts all subsequent elements
data = [10, 20, 30, 40, 50]
data.pop(2)  # removes 30 — 40 and 50 shift left
```

```python
# after: delete from middle of linked list — O(1), change pointers only
# node_b.next = node_b.next.next
# skip node 30 and connect 20 -> 40
```

## Hands-On Steps

### Step 1: Define the Node class

```python
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

    def __repr__(self):
        return f"Node({self.data})"
```

### Step 2: Implement a singly linked list

```python
class SinglyLinkedList:
    def __init__(self):
        self.head = None
        self._size = 0

    def append(self, data):
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self._size += 1

    def prepend(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        self._size += 1

    def delete(self, data):
        if self.head is None:
            return
        if self.head.data == data:
            self.head = self.head.next
            self._size -= 1
            return
        current = self.head
        while current.next:
            if current.next.data == data:
                current.next = current.next.next
                self._size -= 1
                return
            current = current.next

    def __len__(self):
        return self._size

    def __str__(self):
        parts = []
        current = self.head
        while current:
            parts.append(str(current.data))
            current = current.next
        return " -> ".join(parts)

sll = SinglyLinkedList()
sll.append("A")
sll.append("B")
sll.append("C")
print(sll)          # A -> B -> C
sll.prepend("Z")
print(sll)          # Z -> A -> B -> C
sll.delete("B")
print(sll)          # Z -> A -> C
print(len(sll))     # 3
```

### Step 3: Reverse a linked list

```python
def reverse_linked_list(head: Node) -> Node:
    prev = None
    current = head
    while current:
        next_node = current.next
        current.next = prev
        prev = current
        current = next_node
    return prev

sll = SinglyLinkedList()
for item in ["A", "B", "C", "D"]:
    sll.append(item)
print(f"original: {sll}")  # A -> B -> C -> D
sll.head = reverse_linked_list(sll.head)
print(f"reversed: {sll}")  # D -> C -> B -> A
```

### Step 4: Implement a doubly linked list

```python
class DNode:
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None

class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self._size = 0

    def append(self, data):
        new_node = DNode(data)
        if self.tail is None:
            self.head = self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self._size += 1

    def prepend(self, data):
        new_node = DNode(data)
        if self.head is None:
            self.head = self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        self._size += 1

    def __str__(self):
        parts = []
        current = self.head
        while current:
            parts.append(str(current.data))
            current = current.next
        return " <-> ".join(parts)

dll = DoublyLinkedList()
dll.append("A")
dll.append("B")
dll.append("C")
dll.prepend("Z")
print(dll)  # Z <-> A <-> B <-> C
```

### Step 5: Cycle detection (Floyd's algorithm)

```python
def has_cycle(head: Node) -> bool:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False

# no cycle
a, b, c = Node("A"), Node("B"), Node("C")
a.next, b.next = b, c
print(has_cycle(a))  # False

# cycle present
c.next = a  # C -> A creates a cycle
print(has_cycle(a))  # True
```

## What to Notice in This Code

- Linked list prepend is O(1), but list.insert(0, x) is O(n)
- Linked lists have O(n) index access, making them unsuitable for random access
- Reversal and cycle detection are classic interview problems
- Python's collections.deque is implemented internally as a doubly linked list

The practical trade-off is that linked lists win on pointer updates, not on total throughput. Python lists keep elements in contiguous memory, which is friendly to CPU caches and fast for iteration. Linked lists spread nodes across separate objects, so following pointers can cost more than their O(1) insertion story suggests.

You also need to separate "finding the node" from "rewiring the node." Deleting a node is O(1) only after you already have a reference to the previous node. If every operation starts with a linear scan, the overall workload may still be O(n). That is why production Python code usually reaches for deque, OrderedDict, or library implementations instead of a custom linked list.

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|-------------------|-----|
| Wrong order of next-pointer updates | Nodes are lost and the list breaks | Save the next node in a temp variable before changing pointers |
| Not handling the case when head is None | Causes NoneType errors | Always check head is None first |
| Forgetting to update size after deletion | len() returns wrong values | Always decrement _size on successful delete |
| Not setting prev in a doubly linked list | Reverse traversal becomes impossible | Update both prev and next on every insert/delete |
| Infinite loop from circular references | while current never terminates | Use Floyd's algorithm to detect cycles |

## Real-World Applications

- LRU caches are implemented with a doubly linked list plus a dict
- Text editors manage undo history with linked lists
- Memory allocators track free blocks with linked lists
- Hash table chaining uses linked lists
- Browser history is implemented as a doubly linked list

## How Senior Engineers Think About This

In Python, you rarely need to implement a linked list from scratch. list and deque cover most situations. But understanding the linked list concept lets you reason about how deque, LRU caches, and graphs work internally.

For interview preparation, linked lists are essential. They are the best data structure for practicing pointer manipulation, edge-case handling, and recursive thinking.

## Checklist

- [ ] Can implement append, prepend, and delete on a singly linked list
- [ ] Can write an algorithm to reverse a linked list
- [ ] Can explain the advantages of a doubly linked list
- [ ] Can explain Floyd's cycle detection algorithm
- [ ] Can compare the performance differences between arrays and linked lists

## Exercises

1. Write a function that finds the middle node of a singly linked list in a single pass. (Hint: slow/fast pointers)
2. Write a function that merges two sorted linked lists into one sorted linked list.
3. Write a function that deletes the Nth node from the end of a linked list.

## Summary and Next Steps

Linked lists connect nodes with pointers to achieve O(1) insertion and deletion. Unlike arrays, they do not require contiguous memory, but index access is O(n). The next article covers trees and binary trees for representing hierarchical structures.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Linked Lists?**
  - The article treats Linked Lists as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Linked Lists?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Linked Lists reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Data Structures with Python 101 (1/10): What Are Data Structures?](./01-what-are-data-structures.md)
- [Data Structures with Python 101 (2/10): Arrays and Lists](./02-arrays-and-lists.md)
- [Data Structures with Python 101 (3/10): Stacks and Queues](./03-stacks-and-queues.md)
- [Data Structures with Python 101 (4/10): Hash Tables and dict](./04-hash-tables-and-dict.md)
- **Linked Lists (current)**
- Trees and Binary Trees (upcoming)
- Heaps and Priority Queues (upcoming)
- Graph Representations (upcoming)
- Sets and Set Operations (upcoming)
- Choosing the Right Data Structure (upcoming)

<!-- toc:end -->

## References

- [Python Docs — collections.deque](https://docs.python.org/3/library/collections.html#collections.deque)
- [CPython Source — collections module implementation](https://github.com/python/cpython/blob/main/Modules/_collectionsmodule.c)
- [Real Python — Linked Lists in Python](https://realpython.com/linked-lists-python/)
- [Runestone Academy — Linked Lists](https://runestone.academy/ns/books/published/pythonds3/BasicDS/ImplementinganUnorderedListLinkedLists.html)

Tags: Python, Data Structures, Linked List, Node, Pointers
