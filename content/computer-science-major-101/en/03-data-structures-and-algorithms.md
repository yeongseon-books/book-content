---
series: computer-science-major-101
episode: 3
title: "Computer Science Major 101 (3/10): Data Structures and Algorithms"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - CS
  - DataStructures
  - Algorithms
  - Complexity
  - Beginner
seo_description: A beginner-friendly tour of data structures and algorithms covering complexity, study order, and interview preparation.
code_required: false
last_reviewed: '2026-05-14'
---

# Computer Science Major 101 (3/10): Data Structures and Algorithms

> Computer Science Major 101 series (3/10)

**Core question**: Why are *data structures* and *algorithms* the *core* course for *every* CS major?

> Because they are the *common language* of *problem solving*.

This is post 3 in the Computer Science Major 101 series.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Data Structures and Algorithms?
- Which signal should the example or diagram make visible for Data Structures and Algorithms?
- What failure should be prevented first when Data Structures and Algorithms reaches a real system?

## Big Picture

![computer science major 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-major-101/03/03-01-dsa-problem-solving-map.en.png)

*computer science major 101 chapter 3 flow overview*

This picture places Data Structures and Algorithms inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Data Structures and Algorithms is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## What You Will Learn

- Meaning of *data structures*
- Meaning of *algorithms*
- *Time and space complexity*
- Study *order*
- Link to coding *interviews*

## Why It Matters

*Complexity* thinking is the first *standard* of *code quality*.

## Concept at a Glance

## Key Terms

- **array**: *contiguous* memory.
- **list**: *linked* structure.
- **tree**: *hierarchical* structure.
- **graph**: *relations*.
- **complexity**: *growth rate*.

## Before/After

**Before**: You only write *for loops*.

**After**: You think in *complexity*.

## Hands-on: Mini DSA Kit

### Step 1 — Array sum

```python
def total(xs):
    return sum(xs)
```

### Step 2 — Linear search

```python
def find(xs, t):
    return any(x == t for x in xs)
```

### Step 3 — Binary search

```python
def bsearch(xs, t):
    lo, hi = 0, len(xs) - 1
    while lo <= hi:
        m = (lo + hi) // 2
        if xs[m] == t:
            return m
        if xs[m] < t:
            lo = m + 1
        else:
            hi = m - 1
    return -1
```

### Step 4 — Stack

```python
stack = []
stack.append(1)
stack.pop()
```

### Step 5 — Graph BFS

```python
from collections import deque
def bfs(g, s):
    seen, q = {s}, deque([s])
    while q:
        u = q.popleft()
        for v in g[u]:
            if v not in seen:
                seen.add(v); q.append(v)
    return seen
```

## What to Notice in This Code

- *Linear* and *log* differ.
- *Stack/queue* are *simple* but *fundamental*.
- *BFS* shines on *shortest path*.

## Five Common Mistakes

1. **Never *measuring* complexity.**
2. **Forgetting *recursion stack* limits.**
3. **Using *hash* everywhere.**
4. **Mixing *graph representations*.**
5. **Underestimating *input size*.**

## How This Shows Up in Production

Most API *latency* problems start at *data structure choice*.

## How a Senior Engineer Thinks

- *Complexity* is intuition.
- *Data shape* drives the algorithm.
- Look at *worst* and *best*.
- Write *invariants*.
- *Tests* are evidence.

## Checklist

- [ ] *Complexity* labeled.
- [ ] *Input limit* known.
- [ ] *Invariant* stated.
- [ ] *Tests* pass.

## Practice Problems

1. Define *hash table* in one line.
2. Define *graph* in one line.
3. State the meaning of *Big O* in one line.

## Wrap-up and Next Steps

Next post: *Understanding Systems Subjects*.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Data Structures and Algorithms?**
  - The article treats Data Structures and Algorithms as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Data Structures and Algorithms?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Data Structures and Algorithms reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Computer Science Major 101 (1/10): What Computer Science Majors Learn](./01-what-cs-majors-learn.md)
- [Computer Science Major 101 (2/10): Understanding First Year Subjects](./02-first-year-subjects.md)
- **Data Structures and Algorithms (current)**
- Understanding Systems Subjects (upcoming)
- Database and Network (upcoming)
- AI and Data Science (upcoming)
- Project Subjects (upcoming)
- How to Study Computer Science (upcoming)
- Build Your Portfolio (upcoming)
- Skills to Have Before Graduation (upcoming)

<!-- toc:end -->

## References

- [CLRS Introduction to Algorithms](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)
- [Open Data Structures](https://opendatastructures.org/)
- [Visualgo - Algorithm Visualization](https://visualgo.net/en)
- [LeetCode Patterns](https://seanprashad.com/leetcode-patterns/)

Tags: CS, DataStructures, Algorithms, Complexity, Beginner
