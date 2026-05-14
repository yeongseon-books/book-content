---
series: computer-science-101
episode: 5
title: Computer Architecture
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
  - CPU
  - Memory
  - Cache
  - Performance
seo_description: How CPUs, memory, and the cache hierarchy work, and how they shape the real performance of your code.
last_reviewed: '2026-05-04'
---

# Computer Architecture

> Computer Science 101 series (5/10)

<!-- a-grade-intro:begin -->

**Key question**: Two pieces of code share the same Big-O. Why is one ten times slower than the other in practice?

> Even with the same algorithm, performance depends heavily on how the code uses hardware. The CPU does not touch memory directly — it goes through a cache. Cache-friendly code can be tens of times faster than code that misses the cache constantly. This article covers the von Neumann model, the CPU and memory and cache hierarchy, and how all of it shows up in your code.

<!-- a-grade-intro:end -->

This is post 5 in the Computer Science 101 series.

## What You Will Learn

- The core components of the von Neumann architecture
- The stages a CPU goes through to execute an instruction
- The memory hierarchy (registers -> cache -> RAM -> disk)
- Locality and cache-friendly code

## Why It Matters

There is always a performance gap that algorithms alone cannot explain. Why one O(n) implementation is twice as fast, why a 10x gap appears depending on how you walk a matrix — all of it traces back to the memory hierarchy.

> The CPU is fast and memory is slow. The cache exists to close that gap.

An algorithm written without hardware awareness is fast only on paper.

## Concept at a Glance

> Higher in the hierarchy means faster, more expensive, and smaller. Lower means slower, cheaper, and bigger.

```text
Tier            Approx. access time   Size
────────────────────────────────────────────
Register        < 1 ns                tens of bytes
L1 cache        ~1 ns                 32-64 KB
L2 cache        ~4 ns                 hundreds of KB
L3 cache        ~10 ns                tens of MB
Main memory     ~100 ns               tens of GB
SSD             ~100 µs               hundreds of GB - TB
HDD             ~10 ms                TB
Network         ~ms - seconds         —
```

## Key Terms

| Term | Description |
| --- | --- |
| CPU | The unit that decodes instructions and performs operations |
| Register | The fastest storage, inside the CPU |
| Cache | A fast intermediate store between CPU and memory (L1/L2/L3) |
| RAM | The main memory used while a program runs |
| Bus | The data path between CPU, memory, and devices |
| Clock | The CPU operating speed (Hz, cycles per second) |

## Before / After

**Before — cache-unfriendly code:**

```python
# Walk a 2D list column-major — frequent cache misses
N = 2000
matrix = [[0] * N for _ in range(N)]

for j in range(N):           # outer loop is the column
    for i in range(N):       # inner loop is the row
        matrix[i][j] += 1    # jump to a different row on every access
```

**After — cache-friendly code:**

```python
# Walk row-major — sequential access in adjacent memory
for i in range(N):           # outer loop is the row
    for j in range(N):       # inner loop is the column
        matrix[i][j] += 1    # adjacent memory access within the same row
```

Both are O(n^2), but the second uses cache lines efficiently and runs faster.

## Hands-On: Step by Step

### Step 1: Memory access patterns make a real difference

```python
import time

N = 2000
matrix = [[0] * N for _ in range(N)]

start = time.perf_counter()
for i in range(N):
    for j in range(N):
        matrix[i][j] += 1
print(f"row-major   : {time.perf_counter() - start:.3f}s")

start = time.perf_counter()
for j in range(N):
    for i in range(N):
        matrix[i][j] += 1
print(f"column-major: {time.perf_counter() - start:.3f}s")
```

### Step 2: Inspect memory layout with NumPy

```python
import numpy as np

a = np.arange(12).reshape(3, 4)        # default is C-order (row-major)
print(a.flags["C_CONTIGUOUS"])         # True
print(a.flags["F_CONTIGUOUS"])         # False

b = np.asfortranarray(a)               # Fortran-order (column-major)
print(b.flags["F_CONTIGUOUS"])         # True

# Same data, different memory layout -> different traversal speed
```

### Step 3: Feel the speed gap of the memory hierarchy

```python
# Sum data of growing size — the cache tiers become visible
import time

for power in [10, 14, 18, 22, 24]:
    n = 1 << power                      # 2^power
    data = [1] * n
    start = time.perf_counter()
    total = 0
    for x in data:
        total += x
    print(f"n=2^{power:>2}  size~{n * 28 // 1024:>10} KB  time={time.perf_counter() - start:.3f}s")
```

### Step 4: What the CPU does in one cycle

```python
# A 3 GHz clock = 3 billion cycles per second
# A simple add = ~1 cycle
# Main memory access = ~300 cycles (about 100x an L1 hit)

# Pseudocode of the instruction stages (Fetch-Decode-Execute)
def cpu_cycle(instruction: str) -> None:
    """1. Fetch  — read the instruction from memory.
       2. Decode — interpret the instruction.
       3. Execute — perform the operation in the ALU.
       4. Write back — store the result in a register or memory."""
    fetch = f"read: {instruction}"
    decode = "decoding"
    execute = "executing"
    write_back = "storing result"
    print(fetch, decode, execute, write_back, sep=" -> ")


cpu_cycle("ADD R1, R2, R3")
```

### Step 5: Pack data for locality

```python
# A list of objects (scattered memory) vs a per-field array (contiguous memory)
import array
import time

N = 1_000_000

class Point:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


points = [Point(i, i) for i in range(N)]
xs = array.array("d", [float(i) for i in range(N)])

start = time.perf_counter()
total = sum(p.x for p in points)
print(f"object list : {time.perf_counter() - start:.3f}s")

start = time.perf_counter()
total = sum(xs)
print(f"flat array  : {time.perf_counter() - start:.3f}s")
```

## Notable Points in This Code

- The same algorithm performs differently depending on memory access order.
- Sequential access of adjacent memory exploits cache lines (spatial locality).
- Reusing the same data soon after keeps it in cache (temporal locality).
- A Python list of objects is an array of pointers, so cache friendliness is poor.

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Column-major traversal of a 2D array | Cache misses explode | Walk in the same order as the memory layout |
| Processing a large object graph as-is | Pointer chasing kills cache use | Use NumPy arrays or `__slots__` dataclasses |
| Doing disk I/O one line at a time | Syscall overhead dominates | Buffer or read in chunks |
| Relying on virtual memory under pressure | Swap is 10,000x slower | Check data size against memory limits first |
| Assuming Python `list` is an array | It is an array of pointers; arithmetic is slow | Use `array` or `numpy` for numeric work |

## How This Is Used in Practice

- Vectorizing data pipelines with NumPy/Pandas to maximize cache use.
- Improving locality in games and graphics with ECS (Entity-Component-System).
- Column-store DB engines (Parquet, ClickHouse) that favor analytics queries.
- Avoiding false sharing (cache-line contention) in concurrent code.
- Respecting CPU/memory limits and NUMA-aware scheduling in containers.

## How a Senior Engineer Thinks

Senior engineers first lower the algorithmic order, then suspect the memory access pattern. They know an O(n^2) algorithm can be fast enough if cache-friendly, while an O(n log n) algorithm can drag if its memory accesses are scattered.

They also know not every line of code needs cache optimization. Identify the hot path with a profiler and tune it precisely; for everything else, prioritize readability. The principle: "Fix what the profiler points at."

## Checklist

- [ ] I can roughly state the speed gap between CPU, memory, and cache
- [ ] I can explain spatial vs temporal locality
- [ ] I know why 2D arrays should be walked row-major
- [ ] I understand a Python `list` is not a true array
- [ ] I have intuition for how expensive disk I/O is compared to memory

## Practice Problems

1. Sum a 1000x1000 matrix row-major and column-major, and measure the speed ratio.

2. Store one million integers in `list`, `array.array("i", ...)`, and `numpy.ndarray`, and compare summation time.

3. Compute the sum of squares with (a) a `for` loop, (b) a list comprehension, and (c) NumPy vectorization, and analyze the gap.

## Wrap-Up and Next Steps

The CPU is fast and memory is slow. The cache fills the gap, and code that uses it well is tens of times faster on the same algorithm. Good engineers lower the algorithmic order first, then verify the memory access pattern.

The next article covers how multiple programs coexist and share resources on this hardware — the operating system.

<!-- toc:begin -->
- [What Is Computer Science?](./01-what-is-computer-science.md)
- [Computation and Programs](./02-computation-and-programs.md)
- [Data Representation](./03-data-representation.md)
- [Algorithms and Complexity](./04-algorithms-and-complexity.md)
- **Computer Architecture (current)**
- [Operating Systems](./06-operating-systems.md)
- [Networks](./07-networks.md)
- [Databases](./08-databases.md)
- [Software Engineering](./09-software-engineering.md)
- [From CS to AI and Data Science](./10-ai-and-data-science.md)
<!-- toc:end -->

## References

- [Computer Organization and Design (Patterson & Hennessy)](https://www.elsevier.com/books/computer-organization-and-design-mips-edition/patterson/978-0-12-820109-1)
- [Latency Numbers Every Programmer Should Know](https://gist.github.com/jboner/2841832)
- [Ulrich Drepper — What Every Programmer Should Know About Memory](https://people.freebsd.org/~lstewart/articles/cpumemory.pdf)
- [Agner Fog — Optimization Manuals](https://www.agner.org/optimize/)

Tags: Computer Science, Computer Architecture, CPU, Memory, Cache, Performance
