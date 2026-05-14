---
series: computer-architecture-101
episode: 6
title: Cache and Locality
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
  - Cache
  - Locality
  - Performance
  - Memory Hierarchy
seo_description: How CPU caches work, why temporal and spatial locality matter, and how to write cache-friendly code that runs an order of magnitude faster.
last_reviewed: '2026-05-04'
---

# Cache and Locality

> Computer Architecture 101 series (6/10)

<!-- a-grade-intro:begin -->

**Core question**: Two pieces of code read the same data the same number of times. One takes 1 second, the other takes 30. What makes that difference?

> The speed gap between the CPU and main memory is more than 100x. Caches close that gap, but caches only help if your code respects temporal and spatial locality. This article covers how caches work, the two kinds of locality, and the difference between cache-friendly and cache-hostile code.

<!-- a-grade-intro:end -->

This is post 6 in the Computer Architecture 101 series.

## What You Will Learn

- What a cache is and where it sits in the memory hierarchy
- Temporal and spatial locality
- The cache line and the costs it imposes
- Patterns for writing cache-friendly code

## Why It Matters

On a modern CPU, the biggest single performance variable is not clock speed — it is cache miss rate. One main-memory access burns 100–300 cycles; an L1 hit takes around 4. The same algorithm can run 10x faster or slower depending on memory access patterns. Cache awareness is the highest-ROI optimization technique you can learn.

> If the algorithm is fixed, the next question is "is this code cache-friendly?"

## Concept at a Glance

> A cache is a small, fast store that keeps recently and frequently used data close to the CPU. The CPU does not fetch a single byte from main memory — it fetches a 64-byte block called a cache line. Other data in the same line becomes nearly free to read on the next access.

```text
   CPU
    |  (one cycle)
    v
   L1 cache  (32-64KB, ~4 cycles)
    |
    v
   L2 cache  (256KB-1MB, ~12 cycles)
    |
    v
   L3 cache  (several MB, ~40 cycles)
    |
    v
   Main RAM  (several GB, ~200 cycles)
    |
    v
   SSD/HDD  (several TB, tens of thousands of cycles)
```

## Key Terms

| Term | Description |
| --- | --- |
| Cache line | The smallest unit of cache (typically 64 bytes) |
| Temporal locality | Recently touched data is touched again soon |
| Spatial locality | Nearby addresses are touched soon after |
| Cache miss | The needed data is not in cache |
| Working set | The set of data currently accessed often |

## Before / After

**Before — cache-hostile code:**

```python
# Column-major traversal of a 2D array
def col_major(matrix, n):
    total = 0
    for j in range(n):
        for i in range(n):
            total += matrix[i][j]
    return total
```

**After — cache-friendly code:**

```python
def row_major(matrix, n):
    total = 0
    for i in range(n):
        for j in range(n):
            total += matrix[i][j]
    return total
```

Both compute the same sum, but row-major traversal reads adjacent elements that share a cache line, so it runs much faster.

## Hands-on: Step by Step

### Step 1: Time row-major vs column-major traversal

```python
import time, numpy as np

N = 4096
m = np.random.randint(0, 100, (N, N), dtype=np.int32)

start = time.perf_counter()
total = 0
for i in range(N):
    for j in range(N):
        total += m[i, j]
print(f"row-major:   {time.perf_counter() - start:.2f} s")

start = time.perf_counter()
total = 0
for j in range(N):
    for i in range(N):
        total += m[i, j]
print(f"col-major:   {time.perf_counter() - start:.2f} s")
```

Same data, same number of accesses, different order. Row-major is typically 5–10x faster. The gap comes from cache miss rate.

### Step 2: See the cache line in action

```python
import time, numpy as np

CACHE_LINE = 64
INT_SIZE = 8     # numpy int64
stride_ints = CACHE_LINE // INT_SIZE   # 8

N = 100_000_000
arr = np.zeros(N, dtype=np.int64)

start = time.perf_counter()
for i in range(0, N, 1):
    arr[i] += 1
print(f"stride 1:  {time.perf_counter() - start:.2f} s")

start = time.perf_counter()
for i in range(0, N, stride_ints):
    arr[i] += 1
print(f"stride 8:  {time.perf_counter() - start:.2f} s")
```

Stride 1 uses all 8 elements within a cache line; stride 8 uses only one element per line. Memory bandwidth is wasted by a single-digit factor.

### Step 3: Use temporal locality through caching

```python
from functools import lru_cache

def fib_no_cache(n):
    if n < 2: return n
    return fib_no_cache(n - 1) + fib_no_cache(n - 2)

@lru_cache(maxsize=None)
def fib_cached(n):
    if n < 2: return n
    return fib_cached(n - 1) + fib_cached(n - 2)

import time
start = time.perf_counter(); fib_no_cache(30)
print(f"no cache: {time.perf_counter() - start:.3f} s")

start = time.perf_counter(); fib_cached(30)
print(f"cached:   {time.perf_counter() - start:.6f} s")
```

When the same input is asked again, caching the result is the most direct exploitation of temporal locality.

### Step 4: Layout matters — AoS vs SoA

```python
import numpy as np, time

N = 1_000_000

class Particle:
    __slots__ = ("x", "y", "z", "vx", "vy", "vz")
    def __init__(self):
        self.x = self.y = self.z = 0.0
        self.vx = self.vy = self.vz = 0.0

aos = [Particle() for _ in range(N // 100)]   # smaller for memory
soa_x = np.zeros(N); soa_y = np.zeros(N); soa_z = np.zeros(N)

start = time.perf_counter()
for p in aos:
    p.x += 1.0
print(f"AoS x++: {time.perf_counter() - start:.4f} s")

start = time.perf_counter()
soa_x += 1.0
print(f"SoA x++: {time.perf_counter() - start:.4f} s")
```

When you only update x, SoA traverses a contiguous array of just x values, putting the cache to far better use. This is why game engines and GPU code prefer SoA.

### Step 5: Matrix multiplication and blocking

```python
import numpy as np, time

N = 512
a = np.random.rand(N, N); b = np.random.rand(N, N)

start = time.perf_counter()
c = a @ b   # numpy (BLAS) uses cache blocking internally
print(f"numpy matmul: {time.perf_counter() - start:.3f} s")

start = time.perf_counter()
c2 = np.zeros((N, N))
for i in range(N):
    for j in range(N):
        for k in range(N):
            c2[i, j] += a[i, k] * b[k, j]
# only meaningful for smaller N because of speed
```

Numpy's `@` calls into BLAS, which splits matrices into cache-sized blocks. The same algorithm with cache awareness runs more than 100x faster.

## What to Notice in This Code

- For the same algorithm and data, access order determines performance
- A cache line must be used in full for it to be efficient
- Temporal locality is exploited through result caching; spatial through adjacent access
- Data layout (AoS vs SoA) is directly tied to cache behavior

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Column-first traversal | Cache miss explosion | Match traversal to layout |
| Many small scattered objects | Pointer-chasing cost | Pack into contiguous arrays |
| Large stride access | Wasted cache lines | Prefer adjacent indices |
| Recomputing results | Ignored temporal locality | Memoize, lru_cache |
| Tiny hot field in a big struct | Cache line pollution | Split hot fields into a separate SoA |

## How This Shows Up in Production

- Databases: column-store layouts speed up analytical queries
- Machine learning: keeping GPU tensors contiguous in memory
- Game engines: ECS (Entity Component System) enforces SoA layout
- Compilers: loop tiling and loop interchange auto-block code
- Operating systems: the page cache turns disk I/O into memory access

## How a Senior Engineer Thinks

A senior engineer asks of a hot piece of code, "where does this working set fit — L1, L2, or L3?" Past L1 (typically 32KB) costs start to climb; past L3 you hit main memory. Knowing roughly which cache level absorbs the data is the basis for interpreting any measurement.

A senior also keeps the rule "an unmeasured cache optimization is folklore." Cache behavior is non-linear in CPU and data size, so the model in your head must always be checked with tools like `perf stat`, `valgrind --tool=cachegrind`, or simple timing.

## Checklist

- [ ] You know the cache line size is typically 64 bytes
- [ ] You know the order-of-magnitude cost of L1, L2, L3, and RAM
- [ ] You can distinguish temporal and spatial locality
- [ ] You know the AoS vs SoA tradeoff
- [ ] You have measured the row-vs-column traversal difference

## Practice Problems

1. Sum a 1024x1024 numpy array in row-major and column-major order. Measure the ratio and check how it relates to cache line size.

2. Compare a function with `lru_cache` and without it for temporal locality. Call with the same input 1000 times and compare averages.

3. Update the position of 10,000 particles in AoS (Python class) and SoA (numpy array) styles. Measure both.

## Wrap-up and Next Steps

The cache is the largest device that closes the speed gap between CPU and memory, and its effect depends on whether your code follows locality. The same algorithm can show 10x differences from access pattern alone, and that difference is something you can both measure and design for.

Next we look at another device that speeds up the CPU itself — the pipeline. We will cover how a CPU appears to finish one instruction per cycle, and why branch prediction was invented.

<!-- toc:begin -->
- [What Is Computer Architecture?](./01-what-is-computer-architecture.md)
- [Data Representation — Bit, Byte, Integer, Floating Point](./02-data-representation.md)
- [CPU and Instructions](./03-cpu-and-instructions.md)
- [Registers and the ALU](./04-registers-and-alu.md)
- [Memory Organization](./05-memory-organization.md)
- **Cache and Locality (current)**
- Pipelining (upcoming)
- I/O and Devices (upcoming)
- Parallelism and Multicore (upcoming)
- Understanding Performance (upcoming)
<!-- toc:end -->

## References

- [What Every Programmer Should Know About Memory (Ulrich Drepper)](https://www.akkadia.org/drepper/cpumemory.pdf)
- [Wikipedia — CPU cache](https://en.wikipedia.org/wiki/CPU_cache)
- [Wikipedia — Locality of reference](https://en.wikipedia.org/wiki/Locality_of_reference)
- [Mike Acton — Data-Oriented Design and C++ (CppCon 2014)](https://www.youtube.com/watch?v=rX0ItVEVjHc)

Tags: Computer Science, Computer Architecture, Cache, Locality, Performance, Memory Hierarchy
