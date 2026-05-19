---
series: computer-science-101
episode: 1
title: What Is Computer Science?
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - CS Fundamentals
  - Abstraction
  - Computation Theory
  - Curriculum Overview
  - Learning Roadmap
seo_description: A map of what computer science actually studies, why abstraction is its central tool, and how the core subjects connect.
last_reviewed: '2026-05-15'
---

# What Is Computer Science?

When people first encounter computer science, it is easy to mistake it for “being good at programming languages.” In practice, the engineers who keep growing are usually the ones who can model computation, reason about abstraction, and explain where a system's limits come from.

This is the first post in the Computer Science 101 series.

In this article, we'll define what computer science actually studies, why abstraction is the field's shared tool, and how the rest of the series connects into one map.

## Questions This Article Answers

- How is computer science different from programming, and what does it actually study?
- Why does abstraction keep showing up as the field's central tool?
- How do algorithms, systems, and applications connect as layers?
- Why can the same problem produce very different solutions when viewed through a CS lens?
- How should you read this series so that the full picture becomes clearer over time?

## What You Will Learn

- The definition of computer science and its central research questions
- Why abstraction is the field's most important tool
- How the major subjects relate to each other
- A roadmap for learning the rest of this series

## Why It Matters

Learning a programming language and learning computer science are not the same. Programming is the skill of using a tool. Computer science is the study of why those tools work. When you understand the principles, you pick up new tools quickly and you solve problems at the root.

> CS = the study of the principles, limits, and applications of computation.

This series walks through the major subjects of a CS curriculum, one at a time, to draw the whole picture.

## Concept at a Glance

> Computer science has three pillars: theory, systems, and applications. Every subject is connected through one shared tool — abstraction.

![Concept at a Glance](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-101/01/01-01-concept-at-a-glance.en.png)
*The main CS layers, moving from theory into systems and applications*

## Key Terms

| Term | Description |
| --- | --- |
| Computation | Producing output from input by following rules |
| Abstraction | Hiding details so only the essential interface remains |
| Algorithm | A step-by-step procedure for solving a problem |
| Complexity | The time and space an algorithm consumes |
| Turing machine | A theoretical model of what is computable |

## Before / After

**Before — without CS thinking:**

```python
# Compare every pair to find duplicates — O(n^2)
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return duplicates
```

**After — with CS thinking:**

```python
# Use a set for an O(n) solution
def find_duplicates(items):
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return list(duplicates)
```

## Hands-On: Step by Step

### Step 1: What is computation?

```python
# The simplest computation: input -> process -> output
def is_even(n: int) -> bool:
    """Return True if n is even."""
    return n % 2 == 0


print(is_even(4))   # True
print(is_even(7))   # False
```

The essence of computation is "take input, apply rules, produce output." Every program follows this shape.

### Step 2: The power of abstraction

```python
# Hide implementation details, expose only the interface
class Stack:
    """An abstract stack — internals stay hidden."""

    def __init__(self) -> None:
        self._items: list[int] = []

    def push(self, item: int) -> None:
        self._items.append(item)

    def pop(self) -> int:
        return self._items.pop()

    def is_empty(self) -> bool:
        return len(self._items) == 0


# Users do not need to know there is a list inside
stack = Stack()
stack.push(1)
stack.push(2)
print(stack.pop())  # 2
```

Abstraction is the field's most important tool. Operating systems abstract hardware, programming languages abstract machine code, and functions abstract implementation details.

### Step 3: Algorithms and efficiency

```python
import time


def linear_search(items: list[int], target: int) -> int:
    """Sequential search — O(n)."""
    for i, item in enumerate(items):
        if item == target:
            return i
    return -1


def binary_search(items: list[int], target: int) -> int:
    """Binary search — O(log n), requires sorted input."""
    low, high = 0, len(items) - 1
    while low <= high:
        mid = (low + high) // 2
        if items[mid] == target:
            return mid
        elif items[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1


data = list(range(1_000_000))

start = time.time()
linear_search(data, 999_999)
print(f"Linear search: {time.time() - start:.4f}s")

start = time.time()
binary_search(data, 999_999)
print(f"Binary search: {time.time() - start:.6f}s")
```

**Expected output:** `Linear search` should take much longer than `Binary search`, and the gap grows quickly as the input size increases.

The performance gap between two algorithms that solve the same problem widens dramatically as the input grows.

### Step 4: CS as a layered structure

```python
# Express the layered relationship of CS subjects as a dictionary
cs_layers = {
    "Applications": ["AI", "Data science", "Web", "Mobile"],
    "Software": ["Software engineering", "Programming languages"],
    "Systems": ["Operating systems", "Networks", "Databases"],
    "Hardware": ["Computer architecture", "Digital logic"],
    "Theory": ["Algorithms", "Complexity theory", "Computation theory"],
}

for layer, subjects in cs_layers.items():
    print(f"[{layer}] {', '.join(subjects)}")
```

CS stacks up as theory -> hardware -> systems -> software -> applications. Each layer rests on the one below it.

### Step 5: This series at a glance

```python
roadmap = [
    (1, "What Is Computer Science?", "the whole picture"),
    (2, "Computation and Programs", "models of computation, paradigms"),
    (3, "Data Representation", "binary, encoding, types"),
    (4, "Algorithms and Complexity", "Big-O, sorting, searching"),
    (5, "Computer Architecture", "CPU, memory, instructions"),
    (6, "Operating Systems", "processes, memory, file systems"),
    (7, "Networks", "TCP/IP, HTTP, the internet"),
    (8, "Databases", "relational model, SQL, transactions"),
    (9, "Software Engineering", "design, testing, collaboration"),
    (10, "From CS to AI and Data Science", "ML, statistics, applications"),
]

for num, title, keywords in roadmap:
    print(f"  {num:02d}. {title} — {keywords}")
```

## Notable Points in This Code

- The essence of computation is the simple shape: input -> process -> output.
- Abstraction lets us split complex systems into manageable units.
- The choice of algorithm changes the performance of the same problem dramatically.
- Every subject in CS is connected through a layered structure.

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Treating CS as "programming" | You confuse using a tool with understanding it | CS studies the principles of computation |
| Skipping theory subjects | You hit walls in applied work | Algorithms and data structures underpin every other subject |
| Drilling into one subject only | You miss the whole picture | Survey the field first, then go deep where needed |
| Avoiding math entirely | Your theoretical understanding caps out | Discrete math and probability are core CS tools |
| Studying theory without practice | Understanding stays superficial | Implement concepts in code to confirm them |

## How This Is Used in Practice

- CS fundamentals are the core evaluation criteria in system-design interviews.
- Algorithm complexity analysis decides performance in large-scale data processing.
- Operating-system concepts underpin containers (Docker) and cloud infrastructure.
- Network knowledge is essential for distributed systems and microservice design.
- Database theory drives schema design and query optimization.

## How a Senior Engineer Thinks

A senior engineer is not rattled by new technology. The technology changes, but the underlying CS principles do not. Containers are an application of OS concepts, NoSQL is a variation of database theory, and serverless is a new abstraction over distributed systems.

Engineers with strong CS foundations understand problems at the root and design solutions at the right level of abstraction. They can give a principled answer to "Why did you pick this technology?"

## Checklist

- [ ] I can describe computer science in my own words
- [ ] I understand why abstraction matters in CS
- [ ] I can explain how the major CS subjects relate
- [ ] I see why algorithm efficiency matters in practice
- [ ] I have reviewed the full roadmap of this series

## Practice Problems

1. Find three real-world examples of "algorithms" in daily life. Write down the input, the processing steps, and the output for each.

2. List the CS fields that show up inside a single smartphone. (For example: operating system -> iOS/Android.)

3. Run `linear_search` and `binary_search` yourself, and measure the runtime gap as you grow the input by 10x each time.

## Wrap-Up and Next Steps

Computer science is the study of the principles, limits, and applications of computation. Its central tool is abstraction, and its subjects connect in a layered structure from theory up to applications. Programming is a tool of CS, not CS itself.

The next article digs into the most basic CS question — "What is computation?" — and traces the evolution of programming paradigms.

<!-- toc:begin -->
- **What Is Computer Science? (current)**
- [Computation and Programs](./02-computation-and-programs.md)
- [Data Representation](./03-data-representation.md)
- [Algorithms and Complexity](./04-algorithms-and-complexity.md)
- [Computer Architecture](./05-computer-architecture.md)
- [Operating Systems](./06-operating-systems.md)
- [Networks](./07-networks.md)
- [Databases](./08-databases.md)
- [Software Engineering](./09-software-engineering.md)
- [From CS to AI and Data Science](./10-ai-and-data-science.md)
<!-- toc:end -->

## References

- [CS50 — Introduction to Computer Science (Harvard)](https://cs50.harvard.edu/)
- [ACM/IEEE-CS/AAAI — Computing Curricula 2020](https://www.acm.org/binaries/content/assets/education/curricula-recommendations/cc2020.pdf)
- [Structure and Interpretation of Computer Programs (MIT)](https://mitpress.mit.edu/sites/default/files/sicp/full-text/book/book.html)
- [Computer Science Distilled — Wladston Ferreira Filho](https://code.energy/computer-science-distilled/)

Tags: Computer Science, CS Fundamentals, Abstraction, Computation Theory, Curriculum Overview, Learning Roadmap
