---
series: computer-science-101
episode: 1
title: "Computer Science 101 (1/10): What Is Computer Science?"
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

# Computer Science 101 (1/10): What Is Computer Science?

When people first encounter computer science, it is easy to mistake it for “being good at programming languages.” In practice, the engineers who keep growing are usually the ones who can model computation, reason about abstraction, and explain where a system's limits come from.

This is the first post in the Computer Science 101 series.

In this article, we'll define what computer science actually studies, why abstraction is the field's shared tool, and how the rest of the series connects into one map.


![Computer Science 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-101/01/01-01-concept-at-a-glance.en.png)
*Computer Science 101 chapter 1 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying What Is Computer Science??
- Which signal should the example or diagram make visible for What Is Computer Science??
- What failure should be prevented first when What Is Computer Science? reaches a real system?

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

> Computer science has three pillars: theory, systems, and applications. Every subject is connected through one shared tool — abstraction.

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

## Tracing Abstraction Layers in a Real System

We said abstraction is CS's core tool. Let us trace it through a real system. From the moment you click a button in a web browser to the moment that event reaches a server, the journey passes through the following layers.

| Layer | Responsibility | Service received from layer below |
| --- | --- | --- |
| Application | Handle user input, update UI | HTTP request/response |
| Framework | Routing, state management, rendering | DOM API, fetch API |
| Runtime | Execute JavaScript, event loop | OS system calls |
| Operating System | Process management, socket communication | Hardware drivers |
| Network Stack | TCP/IP packet transmission | NIC (network interface card) |
| Hardware | Electrical signal delivery | Physical medium (copper, fiber) |

Each layer is unaware of the details below it. JavaScript code does not need to know how packets are transmitted; the OS does not care what business logic the application runs. This separation allows each layer to be improved or replaced independently.

### When Abstraction Breaks

Abstraction is not infallible. Joel Spolsky's "Leaky Abstractions" — the moment an abstraction starts to leak — is something you will inevitably encounter in production. Here is a representative example.

```python
# Leaky abstraction example: the hidden cost behind an ORM query
# A simple-looking query in Django ORM can generate
# a three-way JOIN under the hood

import sqlite3

conn = sqlite3.connect(":memory:")
cur = conn.cursor()
cur.execute("CREATE TABLE posts (id INTEGER PRIMARY KEY, author_id INTEGER, title TEXT)")
cur.execute("CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT)")
cur.execute("CREATE TABLE followers (id INTEGER PRIMARY KEY, target_id INTEGER)")

# A join without indexes causes a full scan
for row in cur.execute(
    "EXPLAIN QUERY PLAN SELECT p.title FROM posts p JOIN authors a ON p.author_id = a.id"
):
    print(row)
# Trust the abstraction, but verify with EXPLAIN
```

The lesson is clear. The ORM abstracts SQL away, but the execution cost beneath the abstraction still exists. Use abstractions, but be ready to look one layer down when performance issues arise.

### Training Yourself to Move Between Abstraction Levels

People who are good at CS do not stay in one layer. When a problem appears, they descend to a lower layer to find the cause, fix it, then return to the upper layer to clean up the interface. The best way to develop this ability is to express the same problem at multiple levels of abstraction.

```python
# The same "sort" task expressed at three abstraction levels

# Level 1: Highest abstraction — one line
data = [5, 2, 8, 1, 9, 3]
result = sorted(data)
print(f"Level 1 (built-in): {result}")

# Level 2: Algorithm level — insertion sort implemented manually
def insertion_sort(arr: list[int]) -> list[int]:
    arr = arr[:]
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr

print(f"Level 2 (algorithm):  {insertion_sort(data)}")

# Level 3: Comparison-operation level — counting comparisons while sorting
def counted_sort(arr: list[int]) -> tuple[list[int], int]:
    arr = arr[:]
    comparisons = 0
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0:
            comparisons += 1
            if arr[j] > key:
                arr[j + 1] = arr[j]
                j -= 1
            else:
                break
        arr[j + 1] = key
    return arr, comparisons

sorted_data, count = counted_sort(data)
print(f"Level 3 (comparison tracking): {sorted_data}, {count} comparisons")
```

Level 1 says only "what" to do. Level 2 shows "how" it is done. Level 3 measures "how expensive" it is. CS coursework develops the ability to move freely among these three levels.

## The Essence of Computation Through Base Conversion

We said computer science studies "computation." Base conversion is the most fundamental example. The process is simple, yet it captures the essence of computation — transforming input to output according to rules.

```python
# A general-purpose function to convert a decimal integer to any base
def convert_base(n: int, base: int) -> str:
    if n == 0:
        return "0"
    digits = "0123456789ABCDEF"
    result = []
    while n > 0:
        result.append(digits[n % base])
        n //= base
    return "".join(reversed(result))

# Conversion examples table
print(f"{'Decimal':>8} {'Binary':>12} {'Octal':>8} {'Hex':>6}")
print("-" * 40)
for num in [0, 7, 10, 15, 16, 42, 127, 255, 256, 1024]:
    print(f"{num:>8} {convert_base(num, 2):>12} {convert_base(num, 8):>8} {convert_base(num, 16):>6}")
```

This function is only ten lines, yet it contains several core CS ideas.

| Observation | CS Concept |
| --- | --- |
| `n % base` gets the remainder | Division algorithm — foundation of all base conversions |
| `while n > 0` loop | A finite loop with a guaranteed termination condition — definition of algorithm |
| `reversed(result)` | Stack structure — last in, first out |
| `digits` table lookup | Lookup table — branching via data instead of conditionals |

### Hexadecimal in Practice

Hexadecimal appears constantly in programming: color codes (`#FF5733`), memory addresses (`0x7fff5fbff8ac`), MAC addresses (`AA:BB:CC:DD:EE:FF`), UUIDs — all use hex.

```python
# Hex in real-world use
color = 0xFF5733
r = (color >> 16) & 0xFF   # upper 8 bits
g = (color >> 8) & 0xFF    # middle 8 bits
b = color & 0xFF           # lower 8 bits
print(f"RGB({r}, {g}, {b})")  # RGB(255, 87, 51)

# Print a memory address
data = [1, 2, 3]
print(f"List object id: {hex(id(data))}")

# Display bytes as hex
message = "Hello".encode("utf-8")
hex_dump = " ".join(f"{byte:02X}" for byte in message)
print(f"Hex dump of 'Hello': {hex_dump}")
```

## CS Subject Dependencies in Detail

We said the subjects in this series are not standalone but interdependent. Here is a more concrete view of those dependencies.

| Prerequisite | Successor | Connection |
| --- | --- | --- |
| Data Representation | Algorithms | Integer/float representation underlies sorting and comparison operations |
| Data Representation | Networks | Byte order (endianness), serialization formats |
| Algorithms | Databases | B-Tree indexes, hash joins, sort-merge |
| Algorithms | Operating Systems | Scheduling algorithms, page replacement policies |
| Computer Architecture | Operating Systems | Interrupts, virtual memory, cache coherence |
| Operating Systems | Networks | Socket API, file descriptors, epoll |
| Networks | Databases | Client-server protocols, replication |
| Databases | Software Engineering | Migrations, schema design, testing |
| Software Engineering | AI/DS | MLOps, experiment reproducibility, code quality |

The key takeaway from this table is simple: **skip any one subject and you will inevitably circle back to it later.** Understanding networks requires OS sockets; understanding sockets requires file descriptors. Understanding database indexes requires B-Tree data structures.

## Learning Roadmap: Connecting This Article to the Curriculum

Rather than rushing through an intro to computer science, building interconnected concepts gradually produces better long-term learning efficiency. The core concepts in this article are not standalone knowledge — they are prerequisites that lead into operating systems, networks, databases, and software engineering. Use this article as a weekly anchor and perform the following connection exercises.

| Learning Axis | Checkpoint in This Article | Connection to Later Subjects |
| --- | --- | --- |
| Computation Model | Clearly define input-state-output relationships | Algorithm design, distributed system modeling |
| Abstraction | Distinguish interfaces from hidden implementations | API design, module boundary design |
| Resource Constraints | Consider time, memory, and I/O costs simultaneously | Performance tuning, infrastructure cost optimization |
| Verifiability | Judge by measurement and counterexamples, not claims | Test strategy, experiment design |

When doing connection learning, repeat the structure "define concept once + apply to two cases + check one counterexample." For example, after learning time complexity, do not merely memorize Big-O notation — record actual execution-time graphs as input size changes. When the graph differs from expectation, hypothesize the cause and explain the effects of cache locality or constant factors. This practice transforms textbook knowledge into real-world decision-making criteria.

Unifying vocabulary across subjects is also important. The same phenomenon might be called scheduling in OS, queueing in networking, and transaction waiting in databases. The names differ, but the essence — "allocating resources under contention" — is identical. Maintaining a terminology glossary with concept-equivalence mappings in your study notes makes it easier to reuse existing understanding when learning a new field.

Finally, structure weekly reviews around questions rather than summaries. Answering "Why is this abstraction needed?", "Under what conditions does it break?", and "What is the cost of the alternative?" in one sentence each accelerates learning depth. The accumulated question-answer sets become thinking frameworks directly usable in interviews, design reviews, and code reviews.

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

## Answering the Opening Questions

- **How does computer science differ from programming, and what exactly does it study?**
  - Programming is the skill of using tools; computer science studies the principles by which those tools work. CS covers "the principles, limits, and applications of computation"—including what is computable (theory), how to compute efficiently (algorithms), and what structures execution runs on (systems).
- **Why does abstraction repeatedly appear as CS's most important tool?**
  - Understanding complex systems all at once is impossible. Abstraction lets each layer hide lower-layer details and expose only an interface, enabling humans with finite cognitive capacity to design and operate massive systems. Just as the Stack example hid the internal list, OS abstracts hardware, frameworks abstract OS, and applications abstract frameworks.
- **What layered relationship connects algorithms, systems, and application courses?**
  - Theory (algorithms, complexity) provides foundations; systems (hardware, OS, networks, DB) create the execution environment; applications (AI, web, mobile) deliver value to users. Understanding lower-layer constraints makes upper-layer design realistic.
<!-- toc:begin -->
## In this series

- **What Is Computer Science? (current)**
- Computation and Programs (upcoming)
- Data Representation (upcoming)
- Algorithms and Complexity (upcoming)
- Computer Architecture (upcoming)
- Operating Systems (upcoming)
- Networks (upcoming)
- Databases (upcoming)
- Software Engineering (upcoming)
- From CS to AI and Data Science (upcoming)

<!-- toc:end -->

## References

- [CS50 — Introduction to Computer Science (Harvard)](https://cs50.harvard.edu/)
- [ACM/IEEE-CS/AAAI — Computing Curricula 2020](https://www.acm.org/binaries/content/assets/education/curricula-recommendations/cc2020.pdf)
- [Structure and Interpretation of Computer Programs (MIT)](https://mitpress.mit.edu/sites/default/files/sicp/full-text/book/book.html)
- [Computer Science Distilled — Wladston Ferreira Filho](https://code.energy/computer-science-distilled/)

Tags: Computer Science, CS Fundamentals, Abstraction, Computation Theory, Curriculum Overview, Learning Roadmap
