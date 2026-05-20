---
series: data-structures-101
episode: 4
title: "Data Structures 101 (4/10): Stacks and Queues"
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
  - Stack
  - Queue
  - LIFO
  - FIFO
seo_description: How stacks (LIFO) and queues (FIFO) work, how to implement them, and where they show up across real-world software.
last_reviewed: '2026-05-04'
---

# Data Structures 101 (4/10): Stacks and Queues

> Data Structures 101 series (4/10)

**Core question**: What data structure underlies a function call? Why do message queues, work queues, and printer queues all share the word "queue"?

> A stack is last-in-first-out (LIFO); a queue is first-in-first-out (FIFO). The two ADTs are simple, but they sit at the heart of nearly every system: function calls, tree traversal, task scheduling, message passing. This article walks through both by implementing them and then shows how they appear in production software.

This is post 4 in the Data Structures 101 series.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Stacks and Queues?
- Which signal should the example or diagram make visible for Stacks and Queues?
- What failure should be prevented first when Stacks and Queues reaches a real system?

## Big Picture

![data structures 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-101/04/04-01-big-picture.en.png)

*data structures 101 chapter 4 flow overview*

This picture places Stacks and Queues inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Stacks and Queues is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## What You Will Learn

- The ADT definitions of a stack and a queue and their core operations
- How to implement both using arrays and linked lists
- How a function call stack and a BFS traversal queue work
- Which Python data structure to reach for in each case

## Why It Matters

Stacks and queues appear in language execution models, OS scheduling, and inter-service messaging in distributed systems. The ADTs are simple, but without a deep grasp you cannot reason about recursion, DFS, BFS, or event loops.

> Without stacks, you cannot debug recursion. Without queues, you cannot design async systems.

## Concept at a Glance

> A stack is the "push on top, pop from top" model. A queue is the "join the back, leave from the front" model. Both ADTs only operate on the ends, so both can be O(1) with arrays or linked lists.

```text
Stack (LIFO)              Queue (FIFO)
        push                  enqueue       dequeue
          ↓                      ↓             ↑
       ┌─────┐              ┌─────────────────┐
       │  C  │ ← top         │ A → B → C → D │
       │  B  │                └─────────────────┘
       │  A  │              front           back
       └─────┘
          ↑
         pop
```

## Key Terms

| Term | Meaning |
| --- | --- |
| Stack | Last-In-First-Out ADT |
| Queue | First-In-First-Out ADT |
| push / pop | Stack insert / remove |
| enqueue / dequeue | Queue insert / remove |
| Deque | A generalization that pushes and pops at both ends |

## Before / After

**Before — using a list as a queue directly:**

```python
queue = []
queue.append("A")
queue.append("B")
front = queue.pop(0)   # O(n) — every element shifts one slot
```

**After — using deque as a queue:**

```python
from collections import deque

queue = deque()
queue.append("A")
queue.append("B")
front = queue.popleft()   # O(1)
```

The behavior is identical, but the gap widens dramatically as the queue grows.

## Hands-On: Step by Step

### Step 1: Implement a Stack Yourself

```python
class Stack:
    def __init__(self):
        self._data = []

    def push(self, value):
        self._data.append(value)

    def pop(self):
        if not self._data:
            raise IndexError("pop from empty stack")
        return self._data.pop()

    def peek(self):
        if not self._data:
            raise IndexError("peek from empty stack")
        return self._data[-1]

    def __len__(self):
        return len(self._data)

s = Stack()
for v in [1, 2, 3]:
    s.push(v)
print(s.pop(), s.pop(), s.pop())   # 3 2 1
```

When you only operate on one end of an array, every operation is O(1), so a plain list is already a stack.

### Step 2: Implement a Queue Yourself

```python
from collections import deque

class Queue:
    def __init__(self):
        self._data = deque()

    def enqueue(self, value):
        self._data.append(value)

    def dequeue(self):
        if not self._data:
            raise IndexError("dequeue from empty queue")
        return self._data.popleft()

    def __len__(self):
        return len(self._data)

q = Queue()
for v in ["A", "B", "C"]:
    q.enqueue(v)
print(q.dequeue(), q.dequeue(), q.dequeue())   # A B C
```

A deque is O(1) at both ends, which makes it the ideal queue backing.

### Step 3: Bracket Balancing — A Classic Use of a Stack

```python
def is_balanced(expr: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    opens = set("([{")
    stack = []

    for ch in expr:
        if ch in opens:
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack

print(is_balanced("({[]})"))   # True
print(is_balanced("({[})"))    # False
print(is_balanced("(("))       # False
```

Push on opens, pop on closes, and check the match. Compiler parsing works on the same principle.

### Step 4: BFS — A Classic Use of a Queue

```python
from collections import deque

def bfs(graph: dict, start: str) -> list:
    visited = {start}
    queue = deque([start])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order

graph = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A", "D"],
    "D": ["B", "C", "E"],
    "E": ["D"],
}

print(bfs(graph, "A"))   # ['A', 'B', 'C', 'D', 'E']
```

The queue ensures you visit nearby nodes first. Swap the queue for a stack and the same code becomes DFS.

### Step 5: A Deque Does Both

```python
from collections import deque

dq = deque()
# As a stack
dq.append(1); dq.append(2); dq.append(3)
print(dq.pop())    # 3 (LIFO)

# As a queue
dq.append(1); dq.append(2); dq.append(3)
print(dq.popleft()) # 1 (FIFO)
```

A deque is O(1) at both ends, so it is the generalized structure that can express both a stack and a queue.

## Notable Points

- A list as a stack and a deque as a queue both stay O(1)
- `list.pop(0)` for a queue is O(n) — never use it
- The only difference between a stack and a queue is "which end do you remove from"
- DFS and BFS are the same code with the data structure swapped

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Using `list.pop(0)` as a queue | O(n) per operation | Use `collections.deque` |
| Popping from an empty container | IndexError | Guard with `if stack` or try/except |
| Ignoring recursion depth limits | RecursionError | Convert to an explicit stack |
| Missing visited in BFS | Infinite traversal | Mark visited at the moment of push |
| Treating a priority queue as a normal queue | Wrong order | Use a heap separately |

## How This Is Used in Practice

- Function calls run on a stack (the call stack, stack traces)
- A web browser's back button uses a stack; the forward button uses another stack
- Message queues like RabbitMQ and Kafka are the backbone of inter-service async communication
- OS schedulers compose multiple queues (FIFO, priority)
- In graph traversal, BFS uses a queue and DFS uses a stack (or recursion)

## How a Senior Engineer Thinks

A senior engineer mentally draws the stack whenever they see a recursive function. They know deep recursion can be dangerous, so they always have a sense of the call-depth ceiling. When needed, they convert recursion into an explicit stack-based iteration.

A senior engineer also names "work queues" carefully. A simple FIFO queue, a priority queue, a delay queue, and a queue with backpressure produce completely different system behavior. They never assume two queues behave the same just because the ADT name is the same.

## Checklist

- [ ] I can explain the meaning of LIFO and FIFO
- [ ] I know why you must not use a list as a queue in Python
- [ ] I recognize problem patterns where a stack is natural (like bracket balancing)
- [ ] I understand that BFS vs DFS is a choice of data structure
- [ ] I know that a deque supports both stacks and queues

## Practice Problems

1. Implement a queue using two stacks. `enqueue` pushes onto stack one; `dequeue` pops from stack two, refilling stack two from stack one when empty. What is the amortized cost?

2. Implement a postfix calculator with a stack. Example: `"3 4 + 2 *"` → 14.

3. Replace the deque in the BFS code above with a stack (a list). Confirm it becomes DFS. How does the visit order change?

## Wrap-Up and Next Steps

Stacks and queues are the simplest ADTs and the ones you encounter most often. A stack is LIFO and powers function calls, parsing, and DFS. A queue is FIFO and powers BFS, scheduling, and messaging. In Python, a list is the standard stack and `collections.deque` is the standard queue. The only difference is "which end do you pop from," but that one choice changes how a system behaves.

Next we look at the magic of finding a value by key instantly — the hash table. We see how average O(1) search works and how collisions are resolved.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Stacks and Queues?**
  - The article treats Stacks and Queues as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Stacks and Queues?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Stacks and Queues reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Data Structures 101 (1/10): What Are Data Structures?](./01-what-are-data-structures.md)
- [Data Structures 101 (2/10): Arrays and Dynamic Arrays](./02-arrays-and-dynamic-arrays.md)
- [Data Structures 101 (3/10): Linked Lists](./03-linked-lists.md)
- **Stacks and Queues (current)**
- Hash Tables (upcoming)
- Trees (upcoming)
- Binary Search Trees (upcoming)
- Heaps (upcoming)
- Graphs (upcoming)
- Choosing Data Structures (upcoming)

<!-- toc:end -->

## References

- [Open Data Structures — Stacks and Queues](https://opendatastructures.org/ods-python/3_3_SEList_Space_Efficient_.html)
- [Python `collections.deque` docs](https://docs.python.org/3/library/collections.html#collections.deque)
- [Wikipedia — Stack (abstract data type)](https://en.wikipedia.org/wiki/Stack_(abstract_data_type))
- [Wikipedia — Queue (abstract data type)](https://en.wikipedia.org/wiki/Queue_(abstract_data_type))

Tags: Computer Science, Data Structures, Stack, Queue, LIFO, FIFO
