---
series: computer-science-major-101
episode: 4
title: "Computer Science Major 101 (4/10): Understanding Systems Subjects"
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
  - Systems
  - OS
  - Architecture
  - Beginner
seo_description: A beginner-friendly tour of systems courses covering OS, computer architecture, compilers, and systems programming.
code_required: false
last_reviewed: '2026-05-14'
---

# Computer Science Major 101 (4/10): Understanding Systems Subjects

> Computer Science Major 101 series (4/10)

**Core question**: Do *systems* courses really explain *why* a single line of code *behaves* the way it does?

> Yes. *OS*, *architecture*, and *compilers* are the *stage* on which your code runs.

This is post 4 in the Computer Science Major 101 series.


![computer science major 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-major-101/04/04-01-systems-stack-map.en.png)
*computer science major 101 chapter 4 flow overview*
> Systems courses are not just theory—they bridge the gap between what you code and how the hardware actually runs it. That gap is where debugging happens.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Understanding Systems Subjects?
- Which signal should the example or diagram make visible for Understanding Systems Subjects?
- What failure should be prevented first when Understanding Systems Subjects reaches a real system?

## What You Will Learn

- Meaning of the *operating system*
- *Computer architecture*
- Role of the *compiler*
- *Systems programming*
- Better debugging ability

## Why It Matters

*Performance* and *incident analysis* are only possible on top of *systems knowledge*.

## Concept at a Glance
Processes, memory hierarchies, caching, and instruction pipelines are not abstractions—they explain why your code runs at the speed it does.
## Key Terms

- **OS**: *resource manager*.
- **process**: unit of *execution*.
- **thread**: *lightweight* execution.
- **register**: *fastest* memory.
- **compiler**: *translator*.

## Before/After

**Before**: Code *just* runs.

**After**: You see *CPU*, *memory*, and *OS* underneath.

## Hands-on: Build Systems Sense

### Step 1 — Process ID

```python
import os
print(os.getpid())
```

### Step 2 — Environment variable

```python
print(os.environ.get("PATH", ""))
```

### Step 3 — File descriptor

```python
with open("/etc/hostname") as f:
    print(f.fileno())
```

### Step 4 — Time measurement

```python
import time
t = time.perf_counter()
sum(range(10_000_000))
print(time.perf_counter() - t)
```

### Step 5 — Memory sense

```python
import sys
print(sys.getsizeof([0] * 1000))
```

## What to Notice in This Code

- *Processes* have unique IDs.
- *Environment* is per-process.
- *Time* requires syscalls.

## Five Common Mistakes

1. **Treating *memory addresses* as values.**
2. **Confusing *process* and *thread*.**
3. **Confusing *stack* and *heap*.**
4. **Forgetting *buffering*.**
5. **Ignoring *syscall* costs.**

## How This Shows Up in Production

Root cause in incident reports is *usually* an *OS resource* limit.

## How a Senior Engineer Thinks

- Code runs on *machines*.
- *Cost* is *CPU* and *memory*.
- *Concurrency* is decided by the *OS*.
- *Compiler* sets the shape.
- *Syscalls* are *expensive*.

## Checklist

- [ ] *Process/thread* clear.
- [ ] *Memory regions* understood.
- [ ] *Syscall* cost noted.
- [ ] *Timing* measurable.

## Practice Problems

1. Define *operating system* in one line.
2. Define *compiler* in one line.
3. State the meaning of *process* in one line.

## Wrap-up and Next Steps

Next post: *Database and Network*.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Understanding Systems Subjects?**
  - The article treats Understanding Systems Subjects as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Understanding Systems Subjects?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Understanding Systems Subjects reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Computer Science Major 101 (1/10): What Computer Science Majors Learn](./01-what-cs-majors-learn.md)
- [Computer Science Major 101 (2/10): Understanding First Year Subjects](./02-first-year-subjects.md)
- [Computer Science Major 101 (3/10): Data Structures and Algorithms](./03-data-structures-and-algorithms.md)
- **Understanding Systems Subjects (current)**
- Database and Network (upcoming)
- AI and Data Science (upcoming)
- Project Subjects (upcoming)
- How to Study Computer Science (upcoming)
- Build Your Portfolio (upcoming)
- Skills to Have Before Graduation (upcoming)

<!-- toc:end -->

## References

- [Operating Systems: Three Easy Pieces](https://pages.cs.wisc.edu/~remzi/OSTEP/)
- [Computer Systems: A Programmer's Perspective](https://csapp.cs.cmu.edu/)
- [Crafting Interpreters](https://craftinginterpreters.com/)
- [The Linux Programming Interface](https://man7.org/tlpi/)

Tags: CS, Systems, OS, Architecture, Beginner
