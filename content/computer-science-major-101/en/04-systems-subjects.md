---
series: computer-science-major-101
episode: 4
title: Understanding Systems Subjects
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

# Understanding Systems Subjects

> Computer Science Major 101 series (4/10)

<!-- a-grade-intro:begin -->

**Core question**: Do *systems* courses really explain *why* a single line of code *behaves* the way it does?

> Yes. *OS*, *architecture*, and *compilers* are the *stage* on which your code runs.

<!-- a-grade-intro:end -->

This is post 4 in the Computer Science Major 101 series.

## What You Will Learn

- Meaning of the *operating system*
- *Computer architecture*
- Role of the *compiler*
- *Systems programming*
- Better debugging ability

## Why It Matters

*Performance* and *incident analysis* are only possible on top of *systems knowledge*.

## Concept at a Glance

![Systems stack map](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-major-101/04/04-01-systems-stack-map.en.png)

*How hardware, OS, compilers, and programs connect*

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

<!-- toc:begin -->
- [What Computer Science Majors Learn](./01-what-cs-majors-learn.md)
- [Understanding First Year Subjects](./02-first-year-subjects.md)
- [Data Structures and Algorithms](./03-data-structures-and-algorithms.md)
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
