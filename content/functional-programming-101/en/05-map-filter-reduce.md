---
series: functional-programming-101
episode: 5
title: "Functional Programming 101 (5/10): map, filter, reduce"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Python
  - Functional Programming
  - map
  - filter
  - reduce
seo_description: Learn the principles of map, filter, and reduce, and how they compare to list comprehensions.
last_reviewed: '2026-05-04'
---

# Functional Programming 101 (5/10): map, filter, reduce

This is the 5th post in the Functional Programming 101 series.

> Functional Programming 101 Series (5/10)

**Key Question**: How do you transform, filter, and aggregate collections without writing explicit loops?

> `map`, `filter`, and `reduce` are the three core operations of functional programming. They hide loop details and enable declarative data processing that focuses on "what" rather than "how." This article covers each function's mechanics, Python usage, and comparison with list comprehensions.


![Functional Programming 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/functional-programming-101/05/05-01-big-picture.en.png)
*Functional Programming 101 chapter 5 flow overview*

## Questions to Keep in Mind

- How do map, filter, and reduce divide their responsibilities?
- When should you choose a list comprehension over map/filter?
- What mental model makes reduce easy to reason about?

## Why It Matters

Most data processing falls into three patterns: "transform (map)", "select (filter)", and "aggregate (reduce)." Mastering these three lets you express most iteration logic concisely.

> map + filter + reduce = the fundamental data processing toolkit

In Python, list comprehensions often replace map/filter, but understanding the principles helps you choose the right tool for each situation.

## Concept Overview

> The Role of Each Operation

```text
Input list    [1, 2, 3, 4, 5]
              |
map(f)        [f(1), f(2), f(3), f(4), f(5)]    -> transform
filter(p)     [x for x if p(x)]                  -> select
reduce(g)     g(g(g(g(x1, x2), x3), x4), x5)    -> aggregate
```

## Key Concepts

| Term | Description |
|------|-------------|
| map | Applies a function to each element, producing a new sequence |
| filter | Selects only elements that satisfy a condition |
| reduce | Aggregates a sequence into a single value |
| List comprehension | Python's declarative list creation syntax |
| Lazy evaluation | map/filter return iterators that compute values only when needed |

## Before / After

Convert imperative iteration to declarative style.

```python
# before: imperative loop
prices = [1200, 3400, 5600, 7800, 2300]
discounted = []
for p in prices:
    if p >= 3000:
        discounted.append(int(p * 0.9))
print(discounted)  # [3060, 5040, 7020]
```

```python
# after: map + filter composition
prices = [1200, 3400, 5600, 7800, 2300]
discounted = list(map(
    lambda p: int(p * 0.9),
    filter(lambda p: p >= 3000, prices),
))
print(discounted)  # [3060, 5040, 7020]
```

## Hands-On Steps

### Step 1: map — Transform

```python
# basic usage
numbers = [1, 2, 3, 4, 5]
squares = list(map(lambda x: x ** 2, numbers))
print(squares)  # [1, 4, 9, 16, 25]

# with a named function
def celsius_to_fahrenheit(c: float) -> float:
    return c * 9 / 5 + 32

temps_c = [0, 20, 37, 100]
temps_f = list(map(celsius_to_fahrenheit, temps_c))
print(temps_f)  # [32.0, 68.0, 98.6, 212.0]

# applying to multiple sequences simultaneously
a = [1, 2, 3]
b = [10, 20, 30]
sums = list(map(lambda x, y: x + y, a, b))
print(sums)  # [11, 22, 33]

# list comprehension alternative
squares_comp = [x ** 2 for x in numbers]
print(squares_comp)  # [1, 4, 9, 16, 25]
```

### Step 2: filter — Select

```python
# basic usage
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)  # [2, 4, 6, 8, 10]

# with a named function
def is_positive(x: float) -> bool:
    return x > 0

values = [-3, -1, 0, 2, 5, -4, 8]
positives = list(filter(is_positive, values))
print(positives)  # [2, 5, 8]

# None removes falsy values
mixed = [0, "", "hello", None, 42, [], "world"]
truthy = list(filter(None, mixed))
print(truthy)  # ['hello', 42, 'world']

# list comprehension alternative
evens_comp = [x for x in numbers if x % 2 == 0]
print(evens_comp)  # [2, 4, 6, 8, 10]
```

### Step 3: reduce — Aggregate

```python
from functools import reduce

# sum
numbers = [1, 2, 3, 4, 5]
total = reduce(lambda acc, x: acc + x, numbers)
print(total)  # 15

# with initial value
total_with_init = reduce(lambda acc, x: acc + x, numbers, 100)
print(total_with_init)  # 115

# maximum (reduce approach)
maximum = reduce(lambda a, b: a if a > b else b, numbers)
print(maximum)  # 5

# flatten nested lists
nested = [[1, 2], [3, 4], [5, 6]]
flat = reduce(lambda acc, lst: acc + lst, nested, [])
print(flat)  # [1, 2, 3, 4, 5, 6]

# word frequency count
words = ["apple", "banana", "apple", "cherry", "banana", "apple"]
freq = reduce(
    lambda acc, w: {**acc, w: acc.get(w, 0) + 1},
    words,
    {},
)
print(freq)  # {'apple': 3, 'banana': 2, 'cherry': 1}
```

### Step 4: Comprehensions vs map/filter

```python
# simple case: comprehensions are more Pythonic
numbers = [1, 2, 3, 4, 5]

# map + filter
result1 = list(map(lambda x: x ** 2, filter(lambda x: x % 2 == 0, numbers)))

# comprehension — more readable
result2 = [x ** 2 for x in numbers if x % 2 == 0]

print(result1)  # [4, 16]
print(result2)  # [4, 16]

# when map is better: applying an existing function
names = ["alice", "bob", "charlie"]

# map + existing method
upper1 = list(map(str.upper, names))

# comprehension
upper2 = [n.upper() for n in names]

print(upper1)  # ['ALICE', 'BOB', 'CHARLIE']
print(upper2)  # ['ALICE', 'BOB', 'CHARLIE']
# map is slightly more concise
```

### Step 5: Combined Usage — Real-World Data Processing

```python
from functools import reduce

# order data processing
orders = [
    {"product": "Coffee", "quantity": 2, "price": 4500},
    {"product": "Cake", "quantity": 1, "price": 6000},
    {"product": "Juice", "quantity": 3, "price": 3000},
    {"product": "Cookie", "quantity": 5, "price": 1500},
    {"product": "Sandwich", "quantity": 1, "price": 5500},
]

# 1. calculate totals (map)
with_total = list(map(
    lambda o: {**o, "total": o["quantity"] * o["price"]},
    orders,
))

# 2. filter orders >= $50 (filter)
expensive = list(filter(lambda o: o["total"] >= 5000, with_total))

# 3. calculate grand total (reduce)
grand_total = reduce(lambda acc, o: acc + o["total"], expensive, 0)

for o in expensive:
    print(f"  {o['product']}: ${o['total']:,}")
print(f"Grand total: ${grand_total:,}")
# Coffee: $9,000
# Cake: $6,000
# Juice: $9,000
# Cookie: $7,500
# Sandwich: $5,500
# Grand total: $37,000
```

## What to Notice in This Code

- `map` and `filter` return iterators, so they are lazily evaluated
- For simple cases, list comprehensions are more Pythonic than map/filter
- Always provide an initial value to `reduce` for safety
- Combining the three operations expresses complex data processing declaratively

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|---------------------|-----|
| Omitting the initial value in reduce | TypeError on empty sequences | Always provide an initial value |
| Iterating over a map result multiple times | An iterator can only be consumed once | Convert to `list()` or recreate |
| Nesting map/filter deeply | Readability drops sharply | Use comprehensions or intermediate variables |
| Using reduce for everything | Complex reduce is hard to understand | Use built-in functions like `sum()`, `max()` |
| Lambda with side effects in map/filter | Functions in map/filter should be pure | Handle side effects in a for loop |

## Real-World Applications

- Transform schemas with map in data pipelines
- Filter out failed validation items with filter
- Generate summary reports with reduce
- pandas `apply()` and `query()` follow the same concepts
- Process large data lazily with generator expressions

## How Senior Engineers Think About This

In Python, list comprehensions are more idiomatic than map/filter. But knowing the concepts of map/filter/reduce is crucial because pandas, PySpark, and SQL all follow the same patterns.

`reduce` was moved to `functools` precisely because it is easy to overuse. If a built-in function like `sum()`, `max()`, `min()`, `any()`, or `all()` exists for the job, using it is clearer.

## Checklist

- [ ] I can demonstrate the difference between map, filter, and reduce with code
- [ ] I know when to choose list comprehensions over map/filter
- [ ] I can use reduce safely with an initial value
- [ ] I can compose the three operations into a data pipeline
- [ ] I understand that map/filter return iterators

## Exercises

1. From a list of student dicts, use map to extract names and filter for scores above 90.
2. Use reduce to join a list of strings into a single CSV string.
3. Implement the same task both ways — map/filter/reduce and list comprehensions — and compare.

## Summary and Next Steps

map, filter, and reduce are the fundamental tools of functional data processing. In Python, list comprehensions replace many cases, but understanding the principles enables broader tool selection. The next article covers **closures and partial application** — functions that remember external variables.

## Answering the Opening Questions

- **How do map, filter, and reduce divide their responsibilities?**
  - `map` transforms every element to a different value, `filter` keeps only elements matching a condition, and `reduce` collapses multiple values into one. The Celsius-to-Fahrenheit `map`, even-number `filter`, and order-total and word-frequency `reduce` examples show each role in isolation.
- **When should you choose a list comprehension over map/filter?**
  - Simple transformations with conditions read more naturally as `[x ** 2 for x in numbers if x % 2 == 0]`. Conversely, when applying an existing function directly like `str.upper`, or when you want to maintain a lazy iterator flow, `map` and `filter` are more concise.
- **What mental model makes reduce easy to reason about?**
  - First separate which steps are selection, transformation, or aggregation, then assemble them in order. The example filtering prices with `filter(lambda p: p >= 3000)` then discounting with `map(lambda p: int(p * 0.9))`, and the order-data pipeline `with_total → expensive → grand_total`, are exactly that structure.

<!-- toc:begin -->
## In this series

- [Functional Programming 101 (1/10): What Is Functional Programming?](./01-what-is-fp.md)
- [Functional Programming 101 (2/10): Pure Functions and Side Effects](./02-pure-functions.md)
- [Functional Programming 101 (3/10): Immutable Data](./03-immutable-data.md)
- [Functional Programming 101 (4/10): Higher-Order Functions](./04-higher-order-functions.md)
- **map, filter, reduce (current)**
- Closures and Partial Application (upcoming)
- Recursion and Tail Calls (upcoming)
- Lazy Evaluation and Generators (upcoming)
- Function Composition and Pipelines (upcoming)
- Balancing OOP and Functional Programming (upcoming)

<!-- toc:end -->

## References

- [Python Official Docs — Built-in Functions (map, filter)](https://docs.python.org/3/library/functions.html)
- [Python Official Docs — functools.reduce](https://docs.python.org/3/library/functools.html#functools.reduce)
- [Real Python — map, filter, reduce](https://realpython.com/python-map-function/)
- [Fluent Python — Chapter 7: Functions as First-Class Objects](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)

Tags: Python, Functional Programming, map, filter, reduce
