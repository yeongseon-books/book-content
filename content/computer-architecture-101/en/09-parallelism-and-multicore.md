---
series: computer-architecture-101
episode: 9
title: Parallelism and Multicore
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
  - Computer Architecture
  - Parallelism
  - Multicore
  - Concurrency
  - Synchronization
seo_description: Why eight cores rarely give 8x speedup, the difference between concurrency and parallelism, the cost of synchronization, and Amdahl's law.
last_reviewed: '2026-05-04'
---

# Parallelism and Multicore

> Computer Architecture 101 series (9/10)

<!-- a-grade-intro:begin -->

**Core question**: With eight cores, will a program run exactly 8x faster? If not, what sets the limit?

> Clock speed stopped climbing around 2005, and every gain in performance since has come from adding cores and exploiting parallelism. But adding cores does not automatically make code faster. Some work is inherently sequential, and communication between cores is never free. This article lays out the mental model for using multicore well: concurrency vs parallelism, the cost of synchronization, and Amdahl's law.

<!-- a-grade-intro:end -->

## What You Will Learn

- The difference between concurrency and parallelism
- Multicore hardware models (SMP, NUMA, cache coherence)
- The cost of synchronization primitives (lock, atomic, barrier)
- Amdahl's law and the ceilings on scalability

## Why It Matters

Every server, laptop, and phone is multicore today. Single-core clocks are no longer rising, so squeezing out performance means dividing work across cores. Done badly, this makes things slower. Lock contention, cache ping-pong, and false sharing wait at every corner.

> Parallelism is not free. Always start by asking "is this work worth parallelizing?"

## Concept at a Glance

> Concurrency is the structural ability to deal with many tasks. Parallelism is physically running tasks at the same time. Multicore enables parallelism, but data movement between cores has a cost. Cache coherence keeps data consistent automatically, but contention on the same line crashes performance. Amdahl's law says "if 5% is sequential, no number of cores breaks past 20x speedup."

```text
   concurrency                          parallelism
   --------------------                 ---------------------
   structural ability to                physical ability to
   deal with many tasks                 run them simultaneously
                                        (multicore required)

   single-core OK                       multicore required
   async/await, generators              threads, processes, SIMD
```

## Key Terms

| Term | Description |
| --- | --- |
| Concurrency | Structuring multiple tasks to interleave |
| Parallelism | Physically running tasks at the same time |
| SMP | Symmetric multi-processing, equal cores |
| NUMA | Non-uniform memory access by core |
| Cache coherence | Keeping per-core caches consistent |
| Amdahl's law | Sequential fraction caps speedup |

## Before / After

**Before — use all cores without thinking:**

```python
# "8 cores so it must be 8x faster"
from multiprocessing import Pool

def task(x):
    return x * 2

with Pool(8) as p:
    result = p.map(task, range(100))   # tasks too small, overhead dominates
```

**After — consider task size and communication cost:**

```python
from multiprocessing import Pool

def heavy_task(n):
    return sum(i * i for i in range(n))

with Pool(8) as p:
    result = p.map(heavy_task, [10_000_000] * 8)   # enough work per core
```

Same tool, opposite outcomes. When tasks are too small, inter-process communication costs more than the computation.

## Hands-on: Step by Step

### Step 1: Check core count and trivial parallelism

```python
import os, time
from multiprocessing import Pool

def work(n):
    return sum(i * i for i in range(n))

if __name__ == "__main__":
    print(f"logical cores: {os.cpu_count()}")

    N = 5_000_000
    tasks = [N] * 8

    start = time.time()
    [work(n) for n in tasks]
    print(f"sequential: {time.time() - start:.2f}s")

    with Pool(processes=os.cpu_count()) as p:
        start = time.time()
        p.map(work, tasks)
        print(f"parallel:   {time.time() - start:.2f}s")
```

Typical speedup is 4–6x. The reason 8 cores rarely give 8x is the topic of the next step.

### Step 2: Compute Amdahl's law

```python
def amdahl_speedup(p, n):
    """p: parallelizable fraction, n: cores"""
    return 1 / ((1 - p) + p / n)

for serial in [0.05, 0.10, 0.20, 0.50]:
    p = 1 - serial
    print(f"serial {serial*100:.0f}%: cores 8 -> {amdahl_speedup(p, 8):.2f}x,"
          f"  cores inf -> {1/serial:.1f}x")
```

Even 5% serial work caps speedup at 20x with infinite cores. That ceiling lives over every distributed system.

### Step 3: Measure lock contention

```python
import threading, time

counter = 0
lock = threading.Lock()

def with_lock(iters):
    global counter
    for _ in range(iters):
        with lock:
            counter += 1

ITERS = 1_000_000
counter = 0
threads = [threading.Thread(target=with_lock, args=(ITERS,)) for _ in range(4)]
start = time.time()
for t in threads: t.start()
for t in threads: t.join()
print(f"with lock: {time.time()-start:.2f}s, counter={counter}")
```

Past a certain point, more threads do not speed things up — lock contention slows them down.

### Step 4: See false sharing

```python
import threading, time

# Adjacent indices updated by different threads share a cache line
shared = [0] * 4

def bump(idx, iters):
    for _ in range(iters):
        shared[idx] += 1

# Adjacent (false sharing)
threads = [threading.Thread(target=bump, args=(i, 5_000_000)) for i in range(4)]
start = time.time()
for t in threads: t.start()
for t in threads: t.join()
print(f"adjacent: {time.time()-start:.2f}s")

# Spaced apart (false sharing reduced)
shared = [0] * 256
threads = [threading.Thread(target=bump, args=(i*64, 5_000_000)) for i in range(4)]
start = time.time()
for t in threads: t.start()
for t in threads: t.join()
print(f"spaced:   {time.time()-start:.2f}s")
```

Same workload, different cache line layout, different time. Python's GIL hides much of the effect, but in C, Rust, or Go this is routinely 2–3x.

### Step 5: Concurrency vs parallelism for I/O

```python
import asyncio, time

async def io_task(i):
    await asyncio.sleep(0.1)
    return i

async def main():
    start = time.time()
    await asyncio.gather(*(io_task(i) for i in range(100)))
    print(f"asyncio (concurrency, 1 core): {time.time()-start:.2f}s")

asyncio.run(main())
```

100 I/O tasks finish in roughly 0.1 seconds, not 10. A single core handles it through concurrency. Parallelism only helps when work is CPU-bound.

## What to Notice in This Code

- Adding cores alone has limits
- Amdahl's law shows the sequential fraction sets the ceiling
- Lock contention and false sharing are commonly missed performance traps
- For I/O-bound work, concurrency beats parallelism

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Parallelizing tiny tasks | Communication overhead dominates | Make tasks bigger |
| Threading for CPU-bound work in Python | GIL keeps it single-core | multiprocessing or C extension |
| Lock scope too wide | Effective serialization returns | Minimize scope, split locks |
| Ignoring false sharing | Cache ping-pong tanks performance | Pad and align data |
| Parallelizing everything | Some work is inherently sequential | Use Amdahl to estimate first |

## How This Shows Up in Production

- Data processing: SIMD in pandas/numpy, distributed parallelism in Spark
- Web servers: multi-process workers combined with async I/O
- Game engines: rendering, physics, audio pinned to separate cores
- ML training: GPUs use thousands of SIMD lanes
- Databases: parallel queries and partitioning

## How a Senior Engineer Thinks

A senior engineer who hears "let's parallelize" asks two questions first. One: is this work actually CPU-bound? Two: what fraction is parallelizable? Most backend work is I/O-bound, and the answer there is concurrency, not parallelism.

A senior also measures the cost of parallelism. Task distribution, result collection, synchronization, cache coherence traffic — if those costs exceed the parallel gain, you build systems that get slower as you add cores. The proven approach: measure small, scale cores incrementally, plot the curve.

## Checklist

- [ ] You can explain concurrency and parallelism to someone else
- [ ] You can estimate ceilings with Amdahl's law
- [ ] You can identify lock contention and false sharing
- [ ] You can tell CPU-bound from I/O-bound
- [ ] You can decide whether a task is large enough to parallelize

## Practice Problems

1. Tabulate `amdahl_speedup` for serial fractions 1%, 5%, 10% across 16, 64, 256 cores. Find where diminishing returns start.

2. With `multiprocessing.Pool`, vary task size (10k, 100k, 1M, 10M) and measure 4-core speedup. Find the threshold where parallelism is worth it.

3. Compare `threading` and `asyncio` on 100 HTTP GET requests. Tabulate CPU usage, memory, and time.

## Wrap-up and Next Steps

Parallelism is the heart of the multicore era, but it is not automatic. Distinguish it from concurrency, estimate ceilings with Amdahl, and avoid the traps of lock contention and false sharing. A senior looks at the parallelizable fraction before the core count.

Next is the final article in this series — measuring and analyzing performance. We pull together everything from CPU to memory to I/O to parallelism into a thinking tool that explains why a system is as fast or slow as it is.

<!-- toc:begin -->
- [What Is Computer Architecture?](./01-what-is-computer-architecture.md)
- [Data Representation — Bit, Byte, Integer, Floating Point](./02-data-representation.md)
- [CPU and Instructions](./03-cpu-and-instructions.md)
- [Registers and the ALU](./04-registers-and-alu.md)
- [Memory Organization](./05-memory-organization.md)
- [Cache and Locality](./06-cache-and-locality.md)
- [Pipelining](./07-pipelining.md)
- [I/O and Devices](./08-io-and-devices.md)
- **Parallelism and Multicore (current)**
- Understanding Performance (upcoming)
<!-- toc:end -->

## References

- [Wikipedia — Amdahl's law](https://en.wikipedia.org/wiki/Amdahl%27s_law)
- [Wikipedia — Cache coherence](https://en.wikipedia.org/wiki/Cache_coherence)
- [Wikipedia — False sharing](https://en.wikipedia.org/wiki/False_sharing)
- [The Free Lunch Is Over (Herb Sutter, 2005)](http://www.gotw.ca/publications/concurrency-ddj.htm)

Tags: Computer Science, Computer Architecture, Parallelism, Multicore, Concurrency, Synchronization
