---
series: functional-programming-101
episode: 8
title: Lazy Evaluation and Generators
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Python
  - Functional Programming
  - Generators
  - Lazy Evaluation
  - itertools
seo_description: Build memory-efficient data processing pipelines using generators and lazy evaluation in Python.
last_reviewed: '2026-05-04'
---

# Lazy Evaluation and Generators

> Functional Programming 101 Series (8/10)

<!-- a-grade-intro:begin -->

**Key Question**: Can you process data without loading everything into memory at once?

> Lazy evaluation is a strategy that defers computation until the moment a value is actually needed. Python's generators are the primary tool for lazy evaluation, enabling memory-efficient data processing. This article covers how generators work and how to build lazy pipelines with itertools.

<!-- a-grade-intro:end -->

## What You Will Learn

- The difference between eager evaluation and lazy evaluation
- Generator functions and generator expressions
- Memory-efficient processing with itertools
- Working with infinite sequences

## Why It Matters

When analyzing a 10 GB log file, you cannot load it all into memory. Lazy evaluation processes data one line at a time, keeping memory usage constant regardless of input size.

> Lazy evaluation = compute only as much as you need

Python's `range()`, `map()`, `filter()`, and file objects all use lazy evaluation under the hood. Understanding generators unlocks the principles behind all of these built-in tools.

## Concept Overview

> Eager vs Lazy Evaluation

```
Eager Evaluation               Lazy Evaluation
─────────────────             ─────────────────
[1, 4, 9, 16, 25]            (waiting to compute...)
Everything in memory          Produces one value at a time
list()                        generator / iterator
```

## Key Concepts

| Term | Description |
|------|-------------|
| Lazy evaluation | A strategy that computes values only when they are needed |
| Generator | A function that produces values one at a time using `yield` |
| Iterator | An object that returns values sequentially via `__next__()` |
| Generator expression | A lazy expression in the form `(expr for x in iterable)` |
| itertools | A standard library providing efficient iterator combinators |

## Before / After

Replace a full list construction with a generator.

```python
# before: build the entire list in memory
def get_squares(n: int) -> list[int]:
    return [i ** 2 for i in range(n)]

squares = get_squares(1_000_000)  # millions of items stored at once
```

```python
# after: yield one value at a time
def get_squares(n: int):
    for i in range(n):
        yield i ** 2

squares = get_squares(1_000_000)  # almost no memory used
```

## Hands-On Steps

### Step 1: Generator Function Basics

```python
def countdown(n: int):
    """Counts down from n to 1."""
    while n > 0:
        yield n
        n -= 1


# create a generator object
gen = countdown(5)
print(type(gen))  # <class 'generator'>

# pull values one at a time with next()
print(next(gen))  # 5
print(next(gen))  # 4

# iterate over the rest with a for loop
for n in gen:
    print(n, end=" ")
# 3 2 1

# the generator is now exhausted
# next(gen)  # StopIteration
```

### Step 2: Generator Expressions

```python
# list comprehension — eager evaluation
squares_list = [x ** 2 for x in range(10)]
print(type(squares_list))  # <class 'list'>

# generator expression — lazy evaluation
squares_gen = (x ** 2 for x in range(10))
print(type(squares_gen))  # <class 'generator'>


# memory comparison
import sys

big_list = [x ** 2 for x in range(1_000_000)]
big_gen = (x ** 2 for x in range(1_000_000))

print(f"List: {sys.getsizeof(big_list):,} bytes")       # ~8,000,000 bytes
print(f"Generator: {sys.getsizeof(big_gen):,} bytes")    # ~200 bytes

# pass a generator expression directly to sum()
total = sum(x ** 2 for x in range(1_000_000))
print(f"Total: {total:,}")
```

### Step 3: Infinite Sequences

```python
from itertools import count, islice


# infinite generator
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


# take only what you need with islice
fib_10 = list(islice(fibonacci(), 10))
print(fib_10)  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


# infinite counter
def natural_numbers():
    n = 1
    while True:
        yield n
        n += 1

# first 5 perfect squares
squares = list(islice(
    (n ** 2 for n in natural_numbers()),
    5,
))
print(squares)  # [1, 4, 9, 16, 25]
```

### Step 4: Working with itertools

```python
from itertools import chain, takewhile, dropwhile, accumulate, groupby


# chain: concatenate multiple iterables
combined = list(chain([1, 2], [3, 4], [5, 6]))
print(combined)  # [1, 2, 3, 4, 5, 6]

# takewhile / dropwhile: condition-based selection
numbers = [2, 4, 6, 1, 3, 5, 8]
taken = list(takewhile(lambda x: x % 2 == 0, numbers))
dropped = list(dropwhile(lambda x: x % 2 == 0, numbers))
print(taken)    # [2, 4, 6]
print(dropped)  # [1, 3, 5, 8]

# accumulate: running totals
running_total = list(accumulate([1, 2, 3, 4, 5]))
print(running_total)  # [1, 3, 6, 10, 15]

# groupby: group consecutive elements by key
data = sorted(["a", "b", "a", "c", "b", "a"])
for key, group in groupby(data):
    print(f"  {key}: {list(group)}")
# a: ['a', 'a', 'a']
# b: ['b', 'b']
# c: ['c']
```

### Step 5: Building a Lazy Pipeline

```python
from typing import Iterator


def read_lines(text: str) -> Iterator[str]:
    """Yields lines from a text block."""
    for line in text.strip().split("\n"):
        yield line.strip()

def parse_csv(lines: Iterator[str]) -> Iterator[dict]:
    """Converts CSV lines into dictionaries."""
    headers = next(lines).split(",")
    for line in lines:
        values = line.split(",")
        yield dict(zip(headers, values))

def filter_by_score(records: Iterator[dict], min_score: int) -> Iterator[dict]:
    """Yields only records above the minimum score."""
    for record in records:
        if int(record["score"]) >= min_score:
            yield record

def format_output(records: Iterator[dict]) -> Iterator[str]:
    """Formats records for display."""
    for r in records:
        yield f"{r['name']}: {r['score']} points"


# run the pipeline — every stage is lazy
csv_text = """name,score
Alice,85
Bob,92
Charlie,78
Diana,95
Eve,60"""

pipeline = format_output(
    filter_by_score(
        parse_csv(read_lines(csv_text)),
        min_score=80,
    )
)

# consume results one at a time
for line in pipeline:
    print(line)
# Alice: 85 points
# Bob: 92 points
# Diana: 95 points
```

## What to Notice in This Code

- Generators produce values one at a time, saving memory
- Generator expressions can be passed directly to `sum()`, `max()`, and `min()`
- Infinite sequences are made finite with `islice()` or `takewhile()`
- In a lazy pipeline, each stage is a generator so data flows one record at a time

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|---------------------|-----|
| Iterating a generator twice | Once exhausted, it produces nothing | Convert to `list()` or recreate the generator |
| Calling `list()` on an infinite generator | Memory runs out | Use `islice()` to limit |
| Calling `len()` on a generator | Raises TypeError | Convert to a list first if you need length |
| Ignoring exceptions inside generators | Data loss occurs silently | Handle or propagate exceptions properly |
| Unnecessary `list()` conversion | Loses the benefits of laziness | Keep generators until final consumption |

## Real-World Applications

- Process large log files line by line
- Abstract API pagination results as a generator
- Build ETL pipelines by chaining generators
- Transform streaming data in real time
- Use `itertools` for efficient combinations, permutations, and grouping

## How Senior Engineers Think About This

Python's generators are a practical implementation of functional programming's lazy evaluation. The question "Do I really need all this data in memory?" is the trigger — if the answer is no, use a generator.

In production, the effective pattern is to compose each pipeline stage as a generator and let the final consumer (a for loop, `sum()`, a file write) drive the actual computation. This follows the same philosophy as UNIX pipes (`|`).

## Checklist

- [ ] I can explain the difference between a generator function and a regular function
- [ ] I can write generator expressions
- [ ] I can use key functions from `itertools`
- [ ] I can safely work with infinite sequences
- [ ] I can build lazy pipelines to process large datasets

## Exercises

1. Write a generator that yields prime numbers infinitely, and use `islice` to print the first 20.
2. Build a lazy pipeline that reads a large CSV file line by line and computes the average of a specific column.
3. Use `itertools.chain` and `groupby` to group log entries from multiple files by date.

## Summary and Next Steps

Lazy evaluation defers computation to the moment values are needed, keeping memory usage constant. Python's generators and `itertools` are the core tools for building lazy pipelines. The next article covers combining small functions into complex transformations: **function composition and pipelines**.

<!-- toc:begin -->
- [What Is Functional Programming?](./01-what-is-fp.md)
- [Pure Functions and Side Effects](./02-pure-functions.md)
- [Immutable Data](./03-immutable-data.md)
- [Higher-Order Functions](./04-higher-order-functions.md)
- [map, filter, reduce](./05-map-filter-reduce.md)
- [Closures and Partial Application](./06-closure-and-partial.md)
- [Recursion and Tail Calls](./07-recursion.md)
- **Lazy Evaluation and Generators (current)**
- [Function Composition and Pipelines](./09-function-composition.md)
- [Balancing OOP and Functional Programming](./10-oop-and-fp-balance.md)
<!-- toc:end -->

## References

- [Python Official Docs — Generators](https://docs.python.org/3/howto/functional.html#generators)
- [Python Official Docs — itertools](https://docs.python.org/3/library/itertools.html)
- [Real Python — Introduction to Python Generators](https://realpython.com/introduction-to-python-generators/)
- [David Beazley — Generator Tricks for Systems Programmers](http://www.dabeaz.com/generators/)
