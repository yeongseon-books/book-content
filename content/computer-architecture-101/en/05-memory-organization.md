---
series: computer-architecture-101
episode: 5
title: "Computer Architecture 101 (5/10): Memory Organization"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - Computer Architecture
  - Memory
  - Virtual Memory
  - Address Space
  - Stack and Heap
seo_description: How RAM is addressed, what virtual memory is, where the stack and heap live, and how a process actually sees its own memory.
last_reviewed: '2026-05-04'
---

# Computer Architecture 101 (5/10): Memory Organization

> Computer Architecture 101 series (5/10)

**Core question**: Two processes can hold different values at the same address `0x400000`, and both run correctly. How is that possible?

> Memory looks like a giant array of addressed bytes, but the memory a process sees is not real RAM. It is a virtual address space that the operating system and the CPU's MMU build together. On top of that space, code, data, stack, and heap each take their assigned region, and every variable lives somewhere inside it. This article draws that map.

This is post 5 in the Computer Architecture 101 series.


![computer architecture 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/computer-architecture-101/05/05-01-big-picture.en.png)
*computer architecture 101 chapter 5 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Memory Organization?
- Which signal should the example or diagram make visible for Memory Organization?
- What failure should be prevented first when Memory Organization reaches a real system?

## What You Will Learn

- The address model of RAM and word alignment
- Virtual memory and the page concept
- A process's memory layout (text, data, heap, stack)
- The difference between stack and heap, and the memory model behind function calls

## Why It Matters

Without a memory model in your head, you keep meeting the same bugs: stack overflow, memory leaks, dangling pointers, alignment faults. They all come from missing one piece of memory organization. Virtual memory is also one of the single largest performance factors in any system — a page fault can make code 10,000 times slower in a single instruction.

> "Where does this variable live?" is the starting question for both memory safety and performance.

> Each process gets its own virtual address space, and the MMU maps virtual addresses to physical RAM. Inside one process, the layout has fixed regions: text (code), initialized data, BSS (zero-initialized data), heap (grows up), and stack (grows down).

```text
   +------------------+  high addresses
   |     STACK        |  <- function calls, locals
   |        |         |
   |        v         |
   |                  |
   |        ^         |
   |        |         |
   |     HEAP         |  <- malloc, new, dynamic allocation
   +------------------+
   |     BSS          |  <- uninitialized globals
   +------------------+
   |     DATA         |  <- initialized globals
   +------------------+
   |     TEXT         |  <- executable code
   +------------------+  low addresses
```

## Key Terms

| Term | Description |
| --- | --- |
| Address space | The memory range a process can see |
| Virtual address | The address the process uses |
| Physical address | The actual address in RAM |
| MMU | Hardware that translates virtual to physical |
| Page | The smallest mapping unit (typically 4KB) |
| Alignment | Placing data at addresses matching its type size |

## Before / After

**Before — "memory is a flat byte array":**

```python
data = [0] * 1_000_000
data[12345] = 42
# "It just goes into slot 12345"
```

**After — "that address is virtual, and it goes through pages":**

```text
Process virtual address: 0x7f8a4c001000 + 12345*8
                         |
                         v  (MMU + page table)
                         |
Physical RAM address:    0x00000000abcd1000
                         |
                         v  (cache -> DRAM cell)
```

The same index access actually traverses virtual address, physical address, cache, and DRAM in turn.

## Hands-on: Step by Step

### Step 1: Inspect a variable's actual address

```python
import ctypes

x = ctypes.c_int(42)
y = ctypes.c_int(99)
print(hex(ctypes.addressof(x)))
print(hex(ctypes.addressof(y)))
print(f"distance: {ctypes.addressof(y) - ctypes.addressof(x)} bytes")
```

C-compatible types have real addresses. The distance between two variables gives you intuition for how memory gets laid out.

### Step 2: Observe alignment

```python
import ctypes

class Misaligned(ctypes.Structure):
    _fields_ = [("a", ctypes.c_char), ("b", ctypes.c_int), ("c", ctypes.c_char)]

class Aligned(ctypes.Structure):
    _fields_ = [("b", ctypes.c_int), ("a", ctypes.c_char), ("c", ctypes.c_char)]

print(ctypes.sizeof(Misaligned))   # usually 12 (with padding)
print(ctypes.sizeof(Aligned))       # usually 8
```

Same fields, different order, different padding, different size. Memory alignment is the invisible cost in struct design.

### Step 3: Compare stack and heap addresses

```python
import ctypes

def stack_var():
    x = ctypes.c_int(1)
    return ctypes.addressof(x)

heap_var = ctypes.c_int(2)
print("global address:", hex(ctypes.addressof(heap_var)))
print("stack address: ", hex(stack_var()))
```

A stack variable has a different (and usually higher) address per call, while globals and dynamic allocations sit at stable addresses. The exact ranges differ per system.

### Step 4: Check the page size

```python
import resource

print("page size:", resource.getpagesize(), "bytes")  # usually 4096
print("RSS (KB):", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
```

The OS deals with memory in pages (4KB). Touching one variable brings an entire page into RAM. This connects directly to the cache friendliness story in the next article.

### Step 5: Hit the stack-depth limit

```python
import sys

def recurse(n):
    return n if n == 0 else recurse(n - 1) + 1

print(sys.getrecursionlimit())
try:
    recurse(2000)
except RecursionError as e:
    print("stack limit hit:", e)
```

The stack is a fixed-size region reserved up front, and deep recursion hits that limit as a stack overflow. The heap can grow dynamically; the stack cannot.

## What to Notice in This Code

- Every variable has a virtual address; the MMU translates it to physical
- Field order in a struct affects padding and total size
- The stack is small and fast; the heap is large and slower
- Memory is managed in page units (4KB)

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Deep recursion | Stack overflow | Use iteration or an explicit stack |
| Large objects on the stack | Stack size exceeded | Allocate on the heap (malloc, new) |
| Ignoring field alignment | Wasted memory | Order fields large to small |
| Treating virtual as physical | Bad address comparisons, bad caching | Keep virtual and physical distinct |
| Ignoring page faults | Sudden 10,000x slowdown | mlock, prefetch, shrink working set |

## How This Shows Up in Production

- Database engines: page-sized I/O and buffer pool management
- Game engines: cache-friendly struct layouts (SoA vs AoS)
- Embedded systems: explicit split of stack and heap regions in fixed RAM
- Security: ASLR and NX-bit protection of the address space
- Systems programming: mmap to map files directly into memory

## How a Senior Engineer Thinks

A senior engineer monitors process memory in RSS (Resident Set Size) terms. The goal is not "use less memory" in the abstract but "shrink the working set" — the set of pages you touch frequently. That single idea shrinks both page faults and cache misses.

A senior is also aware of struct memory layout. The same data as Array of Structs and Struct of Arrays produce completely different cache behavior, and the right choice depends on the access pattern. Memory layout is the hidden dimension of data structure choice.

## Checklist

- [ ] You can state the difference between virtual and physical addresses
- [ ] You know that page size is typically 4KB
- [ ] You can describe the stack-vs-heap difference in one sentence
- [ ] You understand how field order affects struct size
- [ ] You can explain why deep recursion is dangerous

## Practice Problems

1. With `ctypes.Structure`, define two structs with the same fields (char, int, char, double) — one ordered largest-first, one smallest-first — and compare `sizeof`.

2. Try allocating a 1MB array (a) on the stack and (b) on the heap. (In Python use `numpy.zeros` and `ctypes.c_int * N`.) Observe which is more likely to fail.

3. On your OS, check the stack size with `ulimit -s` (macOS/Linux) or `sys.getrecursionlimit()`. Measure what recursion depth that translates to.

## Wrap-up and Next Steps

Memory looks like a flat byte array, but that flatness is an illusion built by virtual memory. In reality it is mapped in pages, divided into text/data/heap/stack regions, and shaped by alignment and padding. Once that model is in your head, the next chapter — caches — falls into place naturally.

Next we look at the cache that sits between memory and the CPU, why it exists, what locality is, and how cache-aware code differs from cache-blind code.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Memory Organization?**
  - The article treats Memory Organization as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Memory Organization?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Memory Organization reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Computer Architecture 101 (1/10): What Is Computer Architecture?](./01-what-is-computer-architecture.md)
- [Computer Architecture 101 (2/10): Data Representation — Bit, Byte, Integer, Floating Point](./02-data-representation.md)
- [Computer Architecture 101 (3/10): CPU and Instructions](./03-cpu-and-instructions.md)
- [Computer Architecture 101 (4/10): Registers and the ALU](./04-registers-and-alu.md)
- **Memory Organization (current)**
- Cache and Locality (upcoming)
- Pipelining (upcoming)
- I/O and Devices (upcoming)
- Parallelism and Multicore (upcoming)
- Understanding Performance (upcoming)

<!-- toc:end -->

## References

- [Wikipedia — Virtual memory](https://en.wikipedia.org/wiki/Virtual_memory)
- [What Every Programmer Should Know About Memory (Ulrich Drepper)](https://www.akkadia.org/drepper/cpumemory.pdf)
- [Wikipedia — Data structure alignment](https://en.wikipedia.org/wiki/Data_structure_alignment)
- [Linux Memory Management Documentation](https://www.kernel.org/doc/html/latest/admin-guide/mm/index.html)

Tags: Computer Science, Computer Architecture, Memory, Virtual Memory, Address Space, Stack and Heap
