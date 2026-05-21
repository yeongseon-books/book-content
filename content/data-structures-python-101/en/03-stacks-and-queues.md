---
series: data-structures-python-101
episode: 3
title: "Data Structures with Python 101 (3/10): Stacks and Queues"
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
  - Stack
  - Queue
  - deque
seo_description: Implement stacks and queues in Python using list and deque, and learn practical patterns for both data structures.
last_reviewed: '2026-05-04'
---

# Data Structures with Python 101 (3/10): Stacks and Queues

> Data Structures with Python 101 Series (3/10)

**Key Question**: Why is list alone not enough for both stacks and queues?

> list implements stacks efficiently, but using list as a queue means popping from the front is O(n). This article covers the concepts of stack (LIFO) and queue (FIFO), Python implementations, and efficient queue implementation with deque.

This is post 3 in the Data Structures with Python 101 series.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Stacks and Queues?
- Which signal should the example or diagram make visible for Stacks and Queues?
- What failure should be prevented first when Stacks and Queues reaches a real system?

## Big Picture

![Data Structures with Python 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-python-101/03/03-01-big-picture.en.png)

*Data Structures with Python 101 chapter 3 flow overview*

This picture places Stacks and Queues inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## What You Will Learn

- How stacks (LIFO) and queues (FIFO) work
- Implementing a stack with Python list
- Implementing a queue with collections.deque
- Real-world patterns where stacks and queues are used

## Why It Matters

Stacks and queues are the most fundamental abstract data types. Function call stacks, browser back buttons, task queues, and BFS traversal all rely on them. Understanding these two gives you the foundation for more complex algorithms.

> A stack is "last in, first out." A queue is "first in, first out."

Web server request handling, message brokers, and undo functionality are all built on stack and queue patterns.

## Concept Overview

> Stack = LIFO (Last In, First Out), Queue = FIFO (First In, First Out)

```text
[Stack — LIFO]            [Queue — FIFO]
  push -> | C |           enqueue -> | A | B | C | -> dequeue
          | B |                     ^               ^
          | A |                   rear            front
          +---+
  pop  <- | C | (last)    dequeue <- | A | (first)
```

## Key Concepts

| Term | Description |
|------|------------|
| Stack | A data structure that operates on the LIFO principle |
| Queue | A data structure that operates on the FIFO principle |
| push / pop | Operations to add and remove elements from a stack |
| enqueue / dequeue | Operations to add and remove elements from a queue |
| deque | A data structure with O(1) insert/delete at both ends |

## Before / After

Compare an inefficient queue using list and an efficient queue using deque.

```python
# before: queue with list — pop(0) is O(n)
queue = [1, 2, 3]
queue.append(4)       # enqueue
first = queue.pop(0)  # dequeue — O(n), shifts all elements
```

```python
# after: queue with deque — popleft() is O(1)
from collections import deque
queue = deque([1, 2, 3])
queue.append(4)           # enqueue — O(1)
first = queue.popleft()   # dequeue — O(1)
```

## Hands-On Steps

### Step 1: Implement a stack with list

```python
class Stack:
    def __init__(self):
        self._data = []

    def push(self, item):
        self._data.append(item)

    def pop(self):
        if self.is_empty():
            raise IndexError("cannot pop from an empty stack")
        return self._data.pop()

    def peek(self):
        if self.is_empty():
            raise IndexError("cannot peek an empty stack")
        return self._data[-1]

    def is_empty(self):
        return len(self._data) == 0

    def __len__(self):
        return len(self._data)

stack = Stack()
stack.push("a")
stack.push("b")
stack.push("c")
print(stack.pop())   # "c"
print(stack.peek())  # "b"
print(len(stack))    # 2
```

### Step 2: Implement a queue with deque

```python
from collections import deque

class Queue:
    def __init__(self):
        self._data = deque()

    def enqueue(self, item):
        self._data.append(item)

    def dequeue(self):
        if self.is_empty():
            raise IndexError("cannot dequeue from an empty queue")
        return self._data.popleft()

    def peek(self):
        if self.is_empty():
            raise IndexError("cannot peek an empty queue")
        return self._data[0]

    def is_empty(self):
        return len(self._data) == 0

    def __len__(self):
        return len(self._data)

queue = Queue()
queue.enqueue("task1")
queue.enqueue("task2")
queue.enqueue("task3")
print(queue.dequeue())  # "task1"
print(queue.peek())     # "task2"
```

### Step 3: Balanced parentheses check — stack in action

```python
def is_balanced(text: str) -> bool:
    pairs = {"(": ")", "[": "]", "{": "}"}
    stack = []
    for char in text:
        if char in pairs:
            stack.append(char)
        elif char in pairs.values():
            if not stack or pairs[stack.pop()] != char:
                return False
    return len(stack) == 0

print(is_balanced("({[]})"))   # True
print(is_balanced("({[})"))    # False
print(is_balanced("((()"))     # False
```

### Step 4: BFS with a queue

```python
from collections import deque

def bfs(graph: dict, start: str) -> list:
    visited = []
    queue = deque([start])
    seen = {start}
    while queue:
        node = queue.popleft()
        visited.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return visited

graph = {
    "A": ["B", "C"],
    "B": ["D"],
    "C": ["D", "E"],
    "D": [],
    "E": [],
}
print(bfs(graph, "A"))  # ['A', 'B', 'C', 'D', 'E']
```

### Step 5: Performance comparison — list.pop(0) vs deque.popleft()

```python
import time
from collections import deque

n = 100_000

# list.pop(0) — O(n) per operation
data_list = list(range(n))
start = time.perf_counter()
while data_list:
    data_list.pop(0)
list_time = time.perf_counter() - start

# deque.popleft() — O(1) per operation
data_deque = deque(range(n))
start = time.perf_counter()
while data_deque:
    data_deque.popleft()
deque_time = time.perf_counter() - start

print(f"list.pop(0):      {list_time:.4f}s")
print(f"deque.popleft():  {deque_time:.4f}s")
print(f"deque is {list_time / deque_time:.0f}x faster")
```

## What to Notice in This Code

- list's append/pop are O(1), making it a natural fit for stacks
- deque's appendleft/popleft are also O(1), making it ideal for queues
- Popping from an empty stack or queue raises an error, so guard clauses are essential
- BFS uses a queue, DFS uses a stack (or recursion)

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|-------------------|-----|
| Using list.pop(0) for a queue | O(n) per call, slow on large data | Use deque.popleft() |
| Calling pop on an empty stack/queue | Raises IndexError | Check is_empty() before popping |
| Confusing stack and queue | Data is processed in the wrong order | Distinguish LIFO from FIFO clearly |
| Overusing index access on deque | Middle-index access is O(n) | Use only end operations; use list for random access |
| Using an unbounded queue without maxlen | Memory grows indefinitely | Use deque(maxlen=N) to cap the size |

## Real-World Applications

- Browser back/forward navigation uses two stacks
- Undo functionality is implemented with a stack
- Task queues process requests in FIFO order
- BFS traversal manages nodes to visit with a queue
- Rate limiters track the last N requests with deque(maxlen=N)

## How Senior Engineers Think About This

In practice, developers rarely create Stack or Queue classes. They use list and deque directly, signaling intent through comments or type hints like "this variable is used as a stack."

At scale, in-memory queues give way to Redis, RabbitMQ, or Kafka. But the fundamental principles are identical. Understanding queue behavior through deque makes message queue systems easy to reason about.

## Checklist

- [ ] Can explain the difference between stack (LIFO) and queue (FIFO)
- [ ] Can implement a stack with list
- [ ] Can implement a queue with deque
- [ ] Can solve a balanced-parentheses problem with a stack
- [ ] Can explain why list.pop(0) is slower than deque.popleft()

## Exercises

1. Implement a queue using two stacks. (Include enqueue, dequeue, and peek methods.)
2. Write a function that reverses a string using a stack.
3. Create a `deque(maxlen=5)` and add 10 elements. Observe what happens.

## Summary and Next Steps

Stacks operate on LIFO, queues on FIFO. In Python, stacks use list and queues use deque by convention. The next article explores hash tables and dict, which enable O(1) lookups.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Stacks and Queues?**
  - The article treats Stacks and Queues as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Stacks and Queues?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Stacks and Queues reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Data Structures with Python 101 (1/10): What Are Data Structures?](./01-what-are-data-structures.md)
- [Data Structures with Python 101 (2/10): Arrays and Lists](./02-arrays-and-lists.md)
- **Stacks and Queues (current)**
- Hash Tables and dict (upcoming)
- Linked Lists (upcoming)
- Trees and Binary Trees (upcoming)
- Heaps and Priority Queues (upcoming)
- Graph Representations (upcoming)
- Sets and Set Operations (upcoming)
- Choosing the Right Data Structure (upcoming)

<!-- toc:end -->

## References

- [Python Official Docs — collections.deque](https://docs.python.org/3/library/collections.html#collections.deque)
- [Real Python — Stacks and Queues in Python](https://realpython.com/queue-in-python/)
- [GeeksforGeeks — Stack Data Structure](https://www.geeksforgeeks.org/stack-data-structure/)
- [Visualgo — Stack and Queue Visualization](https://visualgo.net/en/list)

Tags: Python, Data Structures, Stack, Queue, deque
