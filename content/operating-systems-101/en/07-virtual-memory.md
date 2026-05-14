---
series: operating-systems-101
episode: 7
title: Virtual Memory
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
  - Virtual Memory
  - Paging
  - TLB
  - Swap
seo_description: Pages, page tables, the TLB, swap, and page faults — how the OS makes limited RAM look infinite, and what it really costs.
last_reviewed: '2026-05-04'
---

# Virtual Memory

This is post 7 in the Operating Systems 101 series.

> Operating Systems 101 series (7/10)

<!-- a-grade-intro:begin -->

**Core question**: Every process appears to own its own enormous memory, yet the machine has only a few GB of RAM — how does the OS construct that illusion?

> Virtual memory is the biggest illusion the OS produces. It promises every process its own 4GB while the machine has only 8 or 16. Pages, page tables, the TLB, and page faults hold up that illusion. Once you understand the mechanism, you can see why "the process looks fine but the system freezes" actually happens.

<!-- a-grade-intro:end -->

## What You Will Learn

- The split between virtual addresses and physical addresses
- The roles of pages, page tables, and the TLB
- The cost that page faults and swap impose
- How memory-mapped files (mmap) and copy-on-write are used in practice

## Why It Matters

Without virtual memory you cannot diagnose "RSS is small but the system is slow" or "swap fills up and response times collapse." Powerful features like mmap, fork, and copy-on-write all live on top of virtual memory. It is where the OS handles resources most elegantly, and also where the most expensive mistakes happen.

> Virtual memory is not free. The illusion bills you precisely through page faults.

## Concept at a Glance

> Each process has its own virtual address space. Virtual addresses are split into pages (typically 4KB) and translated to physical addresses through a page table. The CPU caches recent translations in a TLB. When a translation is missing or the page is on disk, a page fault triggers and the OS handles it.

```text
virtual addr  →  [TLB hit]  →  physical addr  →  RAM
                   ↓ miss
              page table walk
                   ↓ not present
              page fault → OS handles (read from disk / allocate new page)
```

## Key Terms

| Term | Description |
| --- | --- |
| Page | The unit virtual/physical memory is divided into (typically 4KB) |
| Page table | Map from virtual page → physical frame |
| TLB | CPU-internal cache of recent page-table lookups |
| Page fault | Mapping is missing or the page is not in RAM; the OS must intervene |
| Swap | Pages evicted to disk and brought back when RAM is tight |

## Before / After

**Before — "RSS tells the whole story":**

```bash
ps -o pid,rss,cmd -p $$
# Not enough. Two processes with the same RSS can have very different speeds
```

**After — "watch page faults and TLB misses too":**

```bash
# major fault = went to disk (slow)
ps -o pid,min_flt,maj_flt,rss,cmd -p $$
# Rising major faults suggests swap-in
```

Same RSS but different fault patterns produce very different perceived speed.

## Hands-on: Step by Step

### Step 1: Read page-fault counters

```bash
python3 -c "
import resource
r = resource.getrusage(resource.RUSAGE_SELF)
print('minor faults', r.ru_minflt)
print('major faults', r.ru_majflt)
"
```

A minor fault is the cost of grabbing a fresh page in RAM; a major fault is the cost of pulling it from disk. Climbing major faults suggests swap activity.

### Step 2: mmap a large file

```python
import mmap, os

with open('big.bin', 'wb') as f:
    f.write(b'A' * (10 * 1024 * 1024))     # 10MB

with open('big.bin', 'rb') as f:
    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
        print(mm[0:10])                     # only touched pages get loaded
```

mmap maps a file directly into the virtual address space. Only the pages you actually touch end up in RAM, so you can treat very large files like memory.

### Step 3: Observe copy-on-write (fork)

```python
import os, time

big = bytearray(100 * 1024 * 1024)          # 100MB
pid = os.fork()
if pid == 0:                                 # child
    # Initially shares pages with the parent (CoW)
    big[0] = 1                               # write triggers a page copy
    time.sleep(2)
    os._exit(0)
else:
    os.waitpid(pid, 0)
```

`fork` does not copy pages immediately; copy happens only on write. This is the core trick that makes spawning a child process cheap.

### Step 4: Look at swap usage

```bash
free -h
swapon --show
# or
cat /proc/swaps
```

If swap is in use and response times are collapsing, RAM is short or the working set has exceeded RAM.

### Step 5: Access pattern and the TLB

```python
import time
N = 5000
m = [[0]*N for _ in range(N)]

t = time.time()
for i in range(N):
    for j in range(N):
        m[i][j] = 1                          # row-major — good page locality
print('row-major', time.time() - t)

t = time.time()
for j in range(N):
    for i in range(N):
        m[i][j] = 1                          # column-major — TLB/cache misses explode
print('col-major', time.time() - t)
```

Same data, same number of writes, different access pattern — the timing differs by several times. Virtual-memory cost is decided by access pattern.

## What to Notice in This Code

- mmap turns file I/O into memory access — a natural abstraction for large data
- Copy-on-write is the trick that makes fork cheap
- When swap shows up, response time has already collapsed
- Same RSS plus different locality produces very different perceived speed

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Judging memory only by RSS | Misses swap and faults | Monitor major faults and swap usage too |
| Reading the entire large file | OOM or swap | Use mmap or chunk streaming |
| Mutating big data right after fork | Defeats CoW, memory explodes | Minimize writes between fork and exec |
| Ignoring access locality | TLB-miss storm | Co-design data structures and loop order |
| "Swap on means safe" | Response collapses anyway | Disable or minimize swap on production systems |

## How This Shows Up in Production

- Databases: mmap for index and page cache
- Containers: cgroup memory and swap settings shape OOM behavior
- ML training: memory-mapped numpy arrays relieve RAM pressure
- Backends: fork-based worker models (gunicorn, uwsgi) leverage CoW
- Performance tuning: perf and friends measure TLB miss and page faults

## How a Senior Engineer Thinks

When a senior engineer hears "we are out of memory," they do not stop at RSS. They first check page-fault rates, swap usage, and whether the working set has exceeded RAM. Virtual memory is an illusion, but unless you can name the moment the illusion breaks (major fault, swap-in), diagnosis goes nowhere.

A senior also designs the access pattern alongside the data structure. Memory is not a flat 1D space but a hierarchy with pages and cache lines, and that fact alone makes the same algorithm several times faster or slower.

## Checklist

- [ ] I can describe virtual vs physical addresses
- [ ] I can describe the cost difference between minor and major faults
- [ ] I know when mmap is useful
- [ ] I can explain what copy-on-write means
- [ ] I treat visible swap as a danger signal

## Practice Problems

1. Time row-major vs column-major fills of the same 2D array. Explain in one paragraph why the times differ.

2. Process a 1GB file with read() vs mmap. Compare RSS and time.

3. Run the same memory load with swap on and with swap off. Observe the response-time difference.

## Wrap-up and Next Steps

Virtual memory is an illusion, but the OS bills you precisely for it through page faults and swap. Techniques like mmap and copy-on-write apply that illusion to handle big data gracefully. Understand virtual memory and you can name the moment the system freezes.

The next article moves on to a resource the OS handles almost as often as memory — the file system.

<!-- toc:begin -->
- [What is an Operating System?](./01-what-is-an-operating-system.md)
- [Processes and Threads](./02-processes-and-threads.md)
- [Scheduling](./03-scheduling.md)
- [Concurrency and Race Conditions](./04-concurrency-and-race-conditions.md)
- [Locks, Mutexes, and Semaphores](./05-locks-mutex-semaphore.md)
- [Memory Management](./06-memory-management.md)
- **Virtual Memory (current)**
- File Systems (upcoming)
- System Calls (upcoming)
- Containers and the Operating System (upcoming)
<!-- toc:end -->

## References

- [Tanenbaum & Bos — Modern Operating Systems](https://www.pearson.com/store/p/modern-operating-systems/P100000869539)
- [What Every Programmer Should Know About Memory — Ulrich Drepper](https://people.freebsd.org/~lstewart/articles/cpumemory.pdf)
- [Linux mmap(2) man page](https://man7.org/linux/man-pages/man2/mmap.2.html)
- [Python mmap](https://docs.python.org/3/library/mmap.html)

Tags: Computer Science, Operating Systems, Virtual Memory, Paging, TLB, Swap
