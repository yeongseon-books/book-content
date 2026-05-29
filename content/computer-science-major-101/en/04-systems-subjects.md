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

This is the 4th post in the Computer Science Major 101 series.


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


## Connecting Systems Courses Through the Execution Path

Systems courses look broad, but the core question is singular: "What path does my code take through the CPU and what resources does it consume?" Whether you study OS, architecture, systems programming, or compilers separately, this question unifies the knowledge. For instance, you should be able to trace — in words — the sequence of process scheduling, context switch, memory allocation, syscall, network I/O, and file access when a single web request arrives.

The table below maps OS core concepts to production debugging signals.

| OS concept | Classroom content | Production signal | Check command / metric |
| --- | --- | --- | --- |
| Process / Thread | Scheduling, execution unit | CPU spike, response delay | `top`, `ps`, run-queue length |
| Memory virtualization | Pages, cache, swap | OOM, GC stall, page fault | RSS, page-fault rate |
| File system | inodes, buffer cache | Disk I/O bottleneck | iowait, latency |
| Syscall | user / kernel boundary | Syscall storm, context-switch surge | strace, perf |
| Synchronization | Locks, semaphores | Deadlock, throughput drop | lock-wait time |

With this table, the symptom "it's slow" becomes more specific. Distinguishing CPU-bound from I/O-bound first changes the fix direction entirely.

## Building Cost Intuition Through Syscall Examples

Even a single line of high-level code can trigger many syscalls internally. File reads, socket sends, and process creation all cross the user–kernel boundary — functionally necessary but not free. Unnecessary file open/close in tight loops, frequent small network sends, and excessive process spawning hit performance immediately.

Recommended observation points during lab exercises:

- Compare batch I/O vs single-call I/O execution time for the same function
- Confirm whether syscall frequency rather than string processing is the bottleneck
- Before introducing threads, check lock-contention potential first
- No optimization without measurement: record metrics before and after changes

These four principles alone let systems-course concepts flow naturally into performance-improvement work.

## Systems Learning Roadmap (Undergraduate)

1. Explain process / thread / memory basics with diagrams.
2. Run a simple server and trace the request-handling path.
3. Create an I/O-bottleneck example and practice measurement tools.
4. Connect compile / link steps to binary execution flow.
5. In a project, reproduce at least one performance issue and record the improvement.

At this point, systems courses transform from abstract memorization into "the skill of narrowing problems."

## Systems Debugging Checklist

When a systems issue is suspected, fix the observation order before modifying code: 1) confirm reproduction conditions, 2) classify bottleneck axis among CPU / memory / I/O, 3) align log timeline, 4) check syscall / network boundaries, 5) compare measurements before and after the change. Following this order reduces intuition-based guessing and narrows causes faster.

## Connecting Systems Knowledge to Team Projects

Systems courses lose most of their value if they end as exam subjects. They must connect to reading operational logs and measurement results.

| Observed signal | Possible cause | Verification metric | Next action |
| --- | --- | --- | --- |
| Response latency spike | CPU contention, I/O wait | CPU usage, iowait | Decompose bottleneck segment, reproduce in experiment |
| Memory growth | Leak, excessive cache | RSS, GC metrics | Inspect object lifecycle |
| Intermittent timeout | Lock contention, network delay | p95/p99, lock wait | Separate retry policy from critical section |

Using this table as a postmortem template in semester projects converts systems-course knowledge into documented assets.
## Practice Problems

1. Define *operating system* in one line.
2. Define *compiler* in one line.
3. State the meaning of *process* in one line.

## Wrap-up and Next Steps

Next post: *Database and Network*.

## Answering the Opening Questions

- **How far can systems courses explain what happens when a single line of code runs?**
  - Operating systems explain how hardware and applications are mediated through resource management, computer architecture shows how CPUs execute instructions, and compilers reveal how high-level languages transform into machine code.
- **Why should operating systems, computer architecture, and compilers be learned together?**
  - Concepts like the difference between processes and threads, memory hierarchy (cache, RAM, disk), and pipeline hazards are not abstract ideas — they describe how actual hardware operates.
- **Why are concepts like processes, memory, files, and time crucial for debugging and performance analysis?**
  - Understanding system depth changes how you reason when debugging "why is this code slow" or "why does this bug occur." This is one of the biggest differences between junior and experienced engineers.
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
