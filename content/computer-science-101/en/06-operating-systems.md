---
series: computer-science-101
episode: 6
title: "Computer Science 101 (6/10): Operating Systems"
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
  - Operating Systems
  - Processes
  - Threads
  - Virtual Memory
  - Concurrency
seo_description: How an operating system manages processes, threads, memory, and system calls — and why your concurrency choices depend on it.
last_reviewed: '2026-05-15'
---

# Computer Science 101 (6/10): Operating Systems

The moment one machine seems to run many programs at once, you are already living inside an operating-system abstraction. The same perspective explains why a web server stalls, why a memory leak becomes visible, and why threads do not always make Python faster.

This is post 6 in the Computer Science 101 series.

In this article, we'll turn processes, threads, virtual memory, system calls, and concurrency into a practical model you can use while debugging and designing software.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Operating Systems?
- Which signal should the example or diagram make visible for Operating Systems?
- What failure should be prevented first when Operating Systems reaches a real system?

## Big Picture

![Computer Science 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-101/06/06-01-concept-at-a-glance.en.png)

*Computer Science 101 chapter 6 flow overview*

This picture places Operating Systems inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Operating Systems is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Questions This Article Answers

- Why does one machine appear to run many programs at once?
- How do processes and threads differ in memory sharing and isolation?
- Why is virtual memory such a useful abstraction?
- What cost appears at the user/kernel boundary when a system call happens?
- Why do CPU-bound and I/O-bound tasks need different concurrency strategies?

## What You Will Learn

- The difference between processes and threads
- Virtual memory and address spaces
- System calls and the user/kernel mode boundary
- Concurrency vs parallelism, and what the GIL means

## Why It Matters

Why a web server stalls, how a memory leak shows up to the OS, why multithreading is not always faster — all of these need OS-level reasoning to answer.

> An OS = resource manager + abstraction layer.

Without understanding OS abstractions, debugging starts to feel like magic.

## Concept at a Glance

> A process is an isolated execution unit. A thread is a flow of execution that shares memory with other threads inside the same process.

## Key Terms

| Term | Description |
| --- | --- |
| Process | An execution unit with its own memory space |
| Thread | An execution flow sharing memory inside the same process |
| Context switch | The OS swapping the running process or thread on the CPU |
| Virtual memory | The abstraction that gives each process its own contiguous address space |
| System call | The interface a user program uses to request a kernel service |
| Scheduler | The OS component deciding which process/thread gets the CPU |

## Before / After

**Before — code that ignores the OS:**

```python
# Fetch 100 URLs sequentially — most of the time is spent waiting
import urllib.request

urls = [f"https://httpbin.org/delay/1?n={i}" for i in range(100)]
results = [urllib.request.urlopen(u).read() for u in urls]
# About 100 seconds — the CPU is idle, just waiting on I/O
```

**After — using the OS's async I/O:**

```python
# Same work, done concurrently — overlap the I/O wait
from concurrent.futures import ThreadPoolExecutor
import urllib.request

def fetch(url: str) -> bytes:
    return urllib.request.urlopen(url).read()

with ThreadPoolExecutor(max_workers=20) as pool:
    results = list(pool.map(fetch, urls))
# About 5-10 seconds — other requests progress while one waits
```

## Hands-On: Step by Step

### Step 1: Create a process and a thread

```python
import os
import threading
import multiprocessing

def show_id(label: str) -> None:
    print(f"{label}: pid={os.getpid()}, tid={threading.get_ident()}")

print("[main]")
show_id("main")

print("\n[thread]")
t = threading.Thread(target=show_id, args=("thread",))
t.start()
t.join()

print("\n[process]")
p = multiprocessing.Process(target=show_id, args=("process",))
p.start()
p.join()
```

### Step 2: The GIL and the limits of multithreading

```python
# CPU-bound work does not get faster with threads (CPython GIL)
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def cpu_heavy(n: int) -> int:
    total = 0
    for i in range(n):
        total += i * i
    return total

N = 10_000_000
work = [N] * 4

start = time.perf_counter()
[cpu_heavy(n) for n in work]
print(f"sequential : {time.perf_counter() - start:.2f}s")

start = time.perf_counter()
with ThreadPoolExecutor(max_workers=4) as pool:
    list(pool.map(cpu_heavy, work))
print(f"threads x4 : {time.perf_counter() - start:.2f}s")  # roughly the same

start = time.perf_counter()
with ProcessPoolExecutor(max_workers=4) as pool:
    list(pool.map(cpu_heavy, work))
print(f"processes x4: {time.perf_counter() - start:.2f}s")  # about 4x faster
```

**Expected output:** for CPU-bound work, `threads x4` should stay close to `sequential`, while `processes x4` should finish noticeably faster.

### Step 3: Look inside a system call

```python
# Python's open() ultimately calls the OS open(2) system call
import os

fd = os.open("/tmp/oscourse_demo.txt", os.O_CREAT | os.O_WRONLY, 0o644)
os.write(fd, b"Hello from a system call\n")
os.close(fd)

print(open("/tmp/oscourse_demo.txt").read())
os.remove("/tmp/oscourse_demo.txt")
```

### Step 4: Observe virtual memory

```python
# Inspect process memory usage (Linux/macOS)
import os
import resource

print(f"PID            : {os.getpid()}")
usage = resource.getrusage(resource.RUSAGE_SELF)
print(f"max RSS (KB)   : {usage.ru_maxrss}")    # peak resident set size
print(f"page faults    : {usage.ru_minflt}")    # page-fault count
```

### Step 5: Concurrency vs parallelism

```python
# Concurrency = multiple tasks in progress (time-sliced)
# Parallelism = multiple tasks running at the same instant (multi-core)

import asyncio
import time

async def task(name: str, sec: float) -> None:
    print(f"{name} starting")
    await asyncio.sleep(sec)        # simulate I/O wait
    print(f"{name} done")

async def main() -> None:
    start = time.perf_counter()
    await asyncio.gather(task("A", 1), task("B", 1), task("C", 1))
    print(f"total elapsed: {time.perf_counter() - start:.2f}s")  # about 1s

asyncio.run(main())
```

## Notable Points in This Code

- Processes do not share memory; threads do.
- CPython's GIL makes processes preferable to threads for CPU-bound work.
- I/O-bound work scales well with threads or async.
- A system call switches from user mode to kernel mode and that switch has a cost.

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Using threads for CPU-bound work | Ineffective due to the GIL | Use `multiprocessing` or `ProcessPoolExecutor` |
| Calling system calls one line at a time | Context-switch overhead | Buffer or batch operations |
| Ending child processes without `join` | Zombie processes, resource leaks | Use `with` or explicit `join`/`wait` |
| Sharing variables between threads without protection | Race conditions | `threading.Lock` or queue-based patterns |
| Judging memory only by RSS | You ignore virtual and shared memory | Use tools like `pmap` or `smem` to break it down |

## How This Is Used in Practice

- Worker processes plus an async event loop in web servers (Gunicorn + Uvicorn).
- Container (cgroup) resource isolation and OOM Killer behavior.
- Choosing multiprocessing vs distributed processing in data pipelines.
- Debugging tools (`strace`, `dtruss`, `perf`) for analyzing system calls and scheduling.
- Memory-leak analysis tracking RSS, swap, and page-fault trends.

## How a Senior Engineer Thinks

A senior engineer asks first: "Is the bottleneck CPU or I/O?" If CPU, they think algorithms and parallelism. If I/O, they think async and concurrency. Even with multithreading, they choose with full awareness of the runtime's concurrency model (GIL, async, actor).

They also know OS abstractions are *leaky abstractions*. Virtual memory looks unbounded, but real RAM and swap have limits. The file system looks like a tree, but inodes and mount points exist. Bugs grow at the edges of abstractions.

## Checklist

- [ ] I can explain processes vs threads from a memory perspective
- [ ] I know what the CPython GIL is and what work it affects
- [ ] I understand virtual memory, pages, and swap
- [ ] I am aware that system calls have a cost
- [ ] I can distinguish concurrency from parallelism in my designs

## Practice Problems

1. Run a CPU-bound and an I/O-bound function with four threads each and four processes each, and compare the times.

2. Use `os.fork()` (or `multiprocessing.Process`) and confirm that the parent and child see the same variable differently.

3. Increment a counter from 100 threads with and without `threading.Lock`, and observe the difference in the result.

## Wrap-Up and Next Steps

The OS abstracts hardware so that many programs can coexist safely. Processes, threads, virtual memory, and system calls are the stage on which all of our code runs. The right concurrency model depends on whether the work is CPU- or I/O-bound.

The next article moves beyond a single machine to how computers exchange data — networks.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Operating Systems?**
  - The article treats Operating Systems as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Operating Systems?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Operating Systems reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Computer Science 101 (1/10): What Is Computer Science?](./01-what-is-computer-science.md)
- [Computer Science 101 (2/10): Computation and Programs](./02-computation-and-programs.md)
- [Computer Science 101 (3/10): Data Representation](./03-data-representation.md)
- [Computer Science 101 (4/10): Algorithms and Complexity](./04-algorithms-and-complexity.md)
- [Computer Science 101 (5/10): Computer Architecture](./05-computer-architecture.md)
- **Operating Systems (current)**
- Networks (upcoming)
- Databases (upcoming)
- Software Engineering (upcoming)
- From CS to AI and Data Science (upcoming)

<!-- toc:end -->

## References

- [Operating Systems: Three Easy Pieces (free)](https://pages.cs.wisc.edu/~remzi/OSTEP/)
- [Python — concurrent.futures docs](https://docs.python.org/3/library/concurrent.futures.html)
- [Linux man-pages — system calls](https://man7.org/linux/man-pages/dir_section_2.html)
- [Andrew Tanenbaum — Modern Operating Systems](https://www.pearson.com/en-us/subject-catalog/p/modern-operating-systems/P200000003311)

Tags: Computer Science, Operating Systems, Processes, Threads, Virtual Memory, Concurrency
