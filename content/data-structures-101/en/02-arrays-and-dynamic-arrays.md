---
series: data-structures-101
episode: 2
title: "Data Structures 101 (2/10): Arrays and Dynamic Arrays"
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
  - Data Structures
  - Array
  - Dynamic Array
  - Memory
  - Python List
seo_description: How fixed and dynamic arrays differ, what Python's list does internally, and what amortized O(1) really means for append.
last_reviewed: '2026-05-04'
---

# Data Structures 101 (2/10): Arrays and Dynamic Arrays

> Data Structures 101 series (2/10)

**Core question**: Why does calling `append` on a Python list a million times stay fast? Surely it must reallocate memory each time?

> An array stores elements of the same type contiguously in memory. Indexing is instant, but the size is fixed. A dynamic array breaks that limit by allocating a larger block and copying existing elements when capacity runs out. This article walks through both structures, their time complexity, and how Python's list is actually implemented.

This is post 2 in the Data Structures 101 series.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Arrays and Dynamic Arrays?
- Which signal should the example or diagram make visible for Arrays and Dynamic Arrays?
- What failure should be prevented first when Arrays and Dynamic Arrays reaches a real system?

## Big Picture

![data structures 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-101/02/02-01-big-picture.en.png)

*data structures 101 chapter 2 flow overview*

This picture places Arrays and Dynamic Arrays inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Arrays and Dynamic Arrays is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## What You Will Learn

- How a fixed-size array is laid out and why indexing is O(1)
- How a dynamic array grows and what its amortized cost is
- How Python's list works internally
- When to choose an array and when to avoid one

## Why It Matters

Arrays are among the most basic and the fastest data structures. They mesh perfectly with the CPU cache, indexing is O(1), and they form the foundation of nearly every advanced structure. Hash tables, dynamic arrays, and heaps all use arrays underneath.

> Without understanding arrays, you cannot deeply understand any other data structure.

This article goes beyond "a collection of values" and looks at memory layout, reallocation, and cache friendliness.

## Concept at a Glance

> An array is a contiguous block of memory. `arr[i]` is computed as start address + `i × element size`, so it is O(1). When a dynamic array runs out of capacity, it usually allocates a block twice as large and copies the old elements over.

```text
Fixed array (size = 5)
addr: 100 104 108 112 116
val:  [10][20][30][40][50]
       ↑
  arr[2] = 100 + 2*4 = 108

Dynamic array (size = 3, capacity = 4)
val:  [10][20][30][ - ]   one slot free
append(40) → [10][20][30][40]   capacity full
append(50) → new block (capacity 8) → [10][20][30][40][50][ ][ ][ ]
```

## Key Terms

| Term | Meaning |
| --- | --- |
| Static array | An array whose size is fixed at creation |
| Dynamic array | An array that can grow on demand |
| Capacity | The largest size currently allocated to a dynamic array |
| Reallocation | Allocating a larger block and copying elements over |
| Amortized cost | The average cost across many operations |

## Before / After

**Before — building a list with `+`:**

```python
result = []
for i in range(1_000_000):
    result = result + [i]   # O(n) copy each time → O(n^2) overall
```

**After — using append:**

```python
result = []
for i in range(1_000_000):
    result.append(i)        # amortized O(1) → O(n) overall
```

The two look similar, but the time difference is over 1000x.

## Hands-On: Step by Step

### Step 1: Is Indexing Truly O(1)?

```python
import time

data = list(range(10_000_000))

start = time.perf_counter()
_ = data[0]
print(f"data[0]:        {(time.perf_counter() - start) * 1e6:.2f} us")

start = time.perf_counter()
_ = data[5_000_000]
print(f"data[5_000_000]: {(time.perf_counter() - start) * 1e6:.2f} us")

start = time.perf_counter()
_ = data[9_999_999]
print(f"data[-1]:        {(time.perf_counter() - start) * 1e6:.2f} us")
```

All three accesses take roughly the same time. There is multiplication and addition only — no scanning of the data.

### Step 2: Implement Dynamic Array Growth Yourself

```python
class DynamicArray:
    def __init__(self):
        self._capacity = 1
        self._size = 0
        self._data = [None] * self._capacity

    def append(self, value):
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        self._data[self._size] = value
        self._size += 1

    def _resize(self, new_cap):
        new_data = [None] * new_cap
        for i in range(self._size):
            new_data[i] = self._data[i]
        self._data = new_data
        self._capacity = new_cap

    def __getitem__(self, i):
        if not 0 <= i < self._size:
            raise IndexError(i)
        return self._data[i]

    def __len__(self):
        return self._size

arr = DynamicArray()
for i in range(10):
    arr.append(i)
    print(f"size={len(arr)}, capacity={arr._capacity}")
```

You will see the capacity climb 1, 2, 4, 8, 16... — doubling each time. The doubling strategy is the key to amortized O(1).

### Step 3: Understand Amortized Cost

```python
# Count the total copies during n appends
copies = 0
size = 0
capacity = 1

for _ in range(1024):
    if size == capacity:
        copies += size       # copy old elements to the new block
        capacity *= 2
    size += 1

print(f"total appends: {size}, total copies: {copies}")
print(f"average: {copies / size:.2f}")
```

The average copy count is below 1. Most appends just write a value into a slot — only the occasional resize is expensive.

### Step 4: Inserting in the Middle Is Costly

```python
import time

data = list(range(100_000))

start = time.perf_counter()
data.append(-1)              # append at the end: O(1)
print(f"append: {(time.perf_counter() - start) * 1e6:.2f} us")

data = list(range(100_000))
start = time.perf_counter()
data.insert(0, -1)           # insert at the front: O(n)
print(f"insert(0): {(time.perf_counter() - start) * 1e6:.2f} us")
```

Inserting at the front shifts every element back by one slot. If your workload does this often, consider a linked list or a deque.

### Step 5: Cache Friendliness

```python
import time

# Sum the same one million integers
list_data = list(range(1_000_000))

start = time.perf_counter()
total = 0
for x in list_data:
    total += x
print(f"list iteration: {(time.perf_counter() - start) * 1000:.2f} ms")

# Compare with a dict — slower
dict_data = {i: i for i in range(1_000_000)}

start = time.perf_counter()
total = 0
for v in dict_data.values():
    total += v
print(f"dict iteration: {(time.perf_counter() - start) * 1000:.2f} ms")
```

Contiguous memory is loaded into a CPU cache line in one shot. That is why a list iterates faster than a dict for the same number of elements.

## Notable Points

- Indexing is just address arithmetic, so it is O(1) regardless of position
- The doubling strategy keeps append's amortized cost at O(1)
- Insertion in the middle or front is O(n) — an inherent limit of dynamic arrays
- Contiguous memory is cache-friendly and benchmarks well

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Building a list with `+` | O(n^2) copy explosion | Use `append` or a list comprehension |
| Frequent inserts at the front | O(n) shift each time | Use `collections.deque` |
| Confusing capacity with size | Wrong memory estimates | size = used, capacity = allocated |
| Slicing huge lists repeatedly | Wasted memory and time | Use indices instead of slices when possible |
| Linear search on sorted data | O(n) when O(log n) is possible | Use the `bisect` module |

## How This Is Used in Practice

- NumPy's ndarray treats fixed-size arrays at the C level to accelerate numeric work
- Pandas DataFrame columns are stored internally as contiguous arrays
- File I/O buffers, network packets, and image pixel data are all arrays
- Game engine entity-component systems (ECS) use arrays for cache friendliness
- Database column stores compress sorted columns and scan them array-style for speed

## How a Senior Engineer Thinks

A senior engineer distinguishes "list" from "array." Python's list is a kind of dynamic array, but other languages do not all share that convention. Java's `ArrayList`, C++'s `std::vector`, and Rust's `Vec` are all dynamic-array families, while Java's `LinkedList` is a different beast entirely.

A senior engineer also pre-allocates capacity. If you know the final size, allocating once with `[None] * n` removes every reallocation cost. It is a small detail, but on a hot path it makes a noticeable difference.

## Checklist

- [ ] I can explain why array indexing is O(1) using the memory layout
- [ ] I understand the link between doubling and amortized cost
- [ ] I can distinguish capacity from size
- [ ] I know why inserting at the front is expensive
- [ ] I understand why cache friendliness affects performance

## Practice Problems

1. Add `pop()` and `__delitem__()` to the `DynamicArray` above. Then add a shrink strategy that halves capacity once the size falls below a quarter.

2. Compare filling a list with one million `append`s versus pre-allocating `[None] * 1_000_000` and writing by index. How big is the difference?

3. What is the time complexity of `bisect.insort` on a sorted list? Search is O(log n) — why is insert not?

## Wrap-Up and Next Steps

An array places same-sized elements contiguously in memory; indexing is O(1) and the layout is cache-friendly. A dynamic array doubles capacity when it runs out, keeping the amortized cost of end-insertion at O(1). Insertions in the middle or front are still O(n), and if that pattern dominates your workload, the linked list in the next article may serve you better.

Next we look at linked lists — nodes joined by pointers. We compare how they solve the "expensive middle insert" problem of arrays, and what they give up in exchange.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Arrays and Dynamic Arrays?**
  - The article treats Arrays and Dynamic Arrays as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Arrays and Dynamic Arrays?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Arrays and Dynamic Arrays reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Data Structures 101 (1/10): What Are Data Structures?](./01-what-are-data-structures.md)
- **Arrays and Dynamic Arrays (current)**
- Linked Lists (upcoming)
- Stacks and Queues (upcoming)
- Hash Tables (upcoming)
- Trees (upcoming)
- Binary Search Trees (upcoming)
- Heaps (upcoming)
- Graphs (upcoming)
- Choosing Data Structures (upcoming)

<!-- toc:end -->

## References

- [Open Data Structures — Chapter 2 Array-Based Lists](https://opendatastructures.org/ods-python/2_Array_Based_Lists.html)
- [CPython listobject.c source](https://github.com/python/cpython/blob/main/Objects/listobject.c)
- [Wikipedia — Dynamic Array](https://en.wikipedia.org/wiki/Dynamic_array)
- [Python collections.deque docs](https://docs.python.org/3/library/collections.html#collections.deque)

Tags: Computer Science, Data Structures, Array, Dynamic Array, Memory, Python List
