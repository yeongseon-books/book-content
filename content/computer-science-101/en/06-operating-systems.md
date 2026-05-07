---
series: computer-science-101
episode: 6
title: Operating Systems
status: content-ready
targets:
  tistory: true
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
last_reviewed: '2026-05-04'
---

# Operating Systems

> Computer Science 101 series (6/10)

<!-- a-grade-intro:begin -->

**Key question**: Why does it look like hundreds of programs run at the same time on a single machine?

> The operating system sits between hardware and applications. It hands CPU and memory out to many programs and gives them a uniform way to reach files, networks, and other resources. Every line of code we write eventually relies on the OS. This article covers processes, threads, virtual memory, system calls, and the basics of concurrency.

<!-- a-grade-intro:end -->

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

```text
Process A                       Process B
┌───────────────────┐           ┌───────────────────┐
│ Virtual address   │           │ Virtual address   │
│  ┌─────────────┐  │           │  ┌─────────────┐  │
│  │ Thread 1    │  │           │  │ Thread 1    │  │
│  │ Thread 2    │  │           │  │             │  │
│  └─────────────┘  │           │  └─────────────┘  │
└─────────┬─────────┘           └─────────┬─────────┘
          │                               │
          └───── Operating system ────────┘
                       │
                  Hardware (CPU, RAM, disk)
```

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

<!-- toc:begin -->
- [What Is Computer Science?](./01-what-is-computer-science.md)
- [Computation and Programs](./02-computation-and-programs.md)
- [Data Representation](./03-data-representation.md)
- [Algorithms and Complexity](./04-algorithms-and-complexity.md)
- [Computer Architecture](./05-computer-architecture.md)
- **Operating Systems (current)**
- [Networks](./07-networks.md)
- [Databases](./08-databases.md)
- [Software Engineering](./09-software-engineering.md)
- [From CS to AI and Data Science](./10-ai-and-data-science.md)
<!-- toc:end -->

## References

- [Operating Systems: Three Easy Pieces (free)](https://pages.cs.wisc.edu/~remzi/OSTEP/)
- [Python — concurrent.futures docs](https://docs.python.org/3/library/concurrent.futures.html)
- [Linux man-pages — system calls](https://man7.org/linux/man-pages/dir_section_2.html)
- [Andrew Tanenbaum — Modern Operating Systems](https://www.pearson.com/en-us/subject-catalog/p/modern-operating-systems/P200000003311)

Tags: Computer Science, Operating Systems, Processes, Threads, Virtual Memory, Concurrency
