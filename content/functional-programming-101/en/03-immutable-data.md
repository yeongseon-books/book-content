---
series: functional-programming-101
episode: 3
title: "Functional Programming 101 (3/10): Immutable Data"
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
  - Immutability
  - tuple
  - frozenset
seo_description: Use immutable data in Python to write safe, predictable code with tuples, frozensets, and frozen dataclasses.
last_reviewed: '2026-05-04'
---

# Functional Programming 101 (3/10): Immutable Data

This is the 3rd post in the Functional Programming 101 series.

> Functional Programming 101 Series (3/10)

**Key Question**: Can you write programs without ever changing existing data?

> Immutable data cannot be modified after creation. When you need a new value, you create new data based on the original. This article covers Python's immutable types and patterns for writing safe, predictable code.


![Functional Programming 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/functional-programming-101/03/03-01-big-picture.en.png)
*Functional Programming 101 chapter 3 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Immutable Data?
- Which signal should the example or diagram make visible for Immutable Data?
- What failure should be prevented first when Immutable Data reaches a real system?

## What You Will Learn

- The distinction between mutable and immutable types in Python
- Practical use of tuple, frozenset, and NamedTuple
- Building immutable objects with frozen dataclasses
- Why immutability simplifies debugging and parallel processing

## Why It Matters

Mutable data makes it hard to track "who changed what and when." If you pass a list to a function and that function modifies the original, hunting down the bug becomes extremely difficult.

> Immutable data = elimination of unpredictable changes

Defaulting to immutable data eliminates an entire class of state-related bugs and makes code easier to reason about.

## Concept Overview

> Mutable vs Immutable Types in Python

```text
Immutable                       Mutable
─────────────────               ─────────────────
int, float, bool                list
str                             dict
tuple                           set
frozenset                       bytearray
bytes                           user-defined classes (default)
```

## Key Concepts

| Term | Description |
|------|-------------|
| Immutable | An object whose internal state cannot be changed after creation |
| Mutable | An object whose internal state can be changed after creation |
| Structural sharing | Reusing unchanged parts when creating a modified copy of immutable data |
| Frozen dataclass | A dataclass created with `frozen=True` that prevents attribute assignment |
| Defensive copy | Copying data at function boundaries to prevent modification of the original |

## Before / After

Convert a mutable list operation to an immutable pattern.

```python
# before: mutating the original list
def add_tag(tags: list[str], tag: str) -> list[str]:
    tags.append(tag)
    return tags

original = ["python", "fp"]
result = add_tag(original, "immutable")
print(original)  # ['python', 'fp', 'immutable'] — original changed!
```

```python
# after: creating a new list
def add_tag(tags: list[str], tag: str) -> list[str]:
    return [*tags, tag]

original = ["python", "fp"]
result = add_tag(original, "immutable")
print(original)  # ['python', 'fp'] — original preserved
print(result)    # ['python', 'fp', 'immutable']
```

## Hands-On Steps

### Step 1: Built-in Immutable Types

```python
# tuple — immutable sequence
point = (3, 4)
# point[0] = 5  # TypeError: 'tuple' does not support item assignment

# frozenset — immutable set
allowed = frozenset({"read", "write", "execute"})
# allowed.add("delete")  # AttributeError: 'frozenset' has no attribute 'add'

# str — immutable string
name = "hello"
upper_name = name.upper()  # creates a new string
print(name)        # hello — original preserved
print(upper_name)  # HELLO

# tuples are hashable and can serve as dict keys
grid: dict[tuple[int, int], str] = {
    (0, 0): "start",
    (1, 2): "goal",
}
print(grid[(0, 0)])  # start
```

### Step 2: Meaningful Immutable Records with NamedTuple

```python
from typing import NamedTuple

class Point(NamedTuple):
    x: float
    y: float

class Color(NamedTuple):
    r: int
    g: int
    b: int

p = Point(3.0, 4.0)
print(p.x, p.y)  # 3.0 4.0
# p.x = 5.0  # AttributeError — immutable

# create a modified copy with _replace
p2 = p._replace(x=5.0)
print(p)   # Point(x=3.0, y=4.0) — original preserved
print(p2)  # Point(x=5.0, y=4.0)

red = Color(255, 0, 0)
print(red)  # Color(r=255, g=0, b=0)
```

### Step 3: Frozen Dataclasses

```python
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class User:
    name: str
    email: str
    role: str = "viewer"

user = User(name="Alice", email="alice@example.com")
# user.name = "Bob"  # FrozenInstanceError — cannot modify

# create a new instance
admin = replace(user, role="admin")
print(user)   # User(name='Alice', email='alice@example.com', role='viewer')
print(admin)  # User(name='Alice', email='alice@example.com', role='admin')

# frozen dataclasses are hashable — usable as dict keys and set elements
users = {user, admin}
print(len(users))  # 2
```

### Step 4: Immutable Dictionary Patterns

```python
from types import MappingProxyType

# MappingProxyType — read-only dictionary view
config = {"host": "localhost", "port": 8080, "debug": True}
readonly_config = MappingProxyType(config)

print(readonly_config["host"])  # localhost
# readonly_config["host"] = "0.0.0.0"  # TypeError — cannot modify

# dictionary update — create a new dictionary
def update_config(config: dict, **updates) -> dict:
    return {**config, **updates}

original = {"host": "localhost", "port": 8080}
updated = update_config(original, port=9090, debug=False)

print(original)  # {'host': 'localhost', 'port': 8080} — original preserved
print(updated)   # {'host': 'localhost', 'port': 9090, 'debug': False}
```

### Step 5: State History with Immutable Data

```python
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class AppState:
    count: int
    message: str

def increment(state: AppState) -> AppState:
    return replace(state, count=state.count + 1)

def set_message(state: AppState, msg: str) -> AppState:
    return replace(state, message=msg)

# state history — every change is tracked
history: list[AppState] = []

state = AppState(count=0, message="start")
history.append(state)

state = increment(state)
history.append(state)

state = increment(state)
history.append(state)

state = set_message(state, "done")
history.append(state)

for i, s in enumerate(history):
    print(f"Step {i}: count={s.count}, message='{s.message}'")
# Step 0: count=0, message='start'
# Step 1: count=1, message='start'
# Step 2: count=2, message='start'
# Step 3: count=2, message='done'
```

## What to Notice in This Code

- Python's tuple, frozenset, and str are built-in immutable types
- `NamedTuple._replace()` and `dataclasses.replace()` are the core immutable update patterns
- Frozen dataclasses are hashable, so they can be used as dict keys and set elements
- Immutable data makes state history (undo/redo) a natural implementation

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|---------------------|-----|
| Putting mutable objects inside a tuple | The tuple is immutable but inner lists can still change | Use immutable types for inner elements too |
| Mutating a dict received as a function argument | The caller's data changes unexpectedly | Create a new dict with `{**d, key: value}` |
| Using mutable default arguments | State is shared across calls | Use `None` as the default |
| Copying everything every time | Performance suffers with large data | Use structural sharing or copy only what changes |
| Force-modifying frozen objects | Using `object.__setattr__` violates the contract | Respect the intent of frozen |

## Real-World Applications

- Define configuration objects as frozen dataclasses to prevent runtime changes
- Use immutable state updates in Redux-style state management
- Model API responses with NamedTuple or frozen dataclass
- Use tuples or frozensets as cache keys
- Manage history with immutable event objects in event sourcing

## How Senior Engineers Think About This

"Make everything immutable" is not the goal. The key is to default to immutable and use mutable only where performance or convenience requires it. In Python, `frozen=True` and `NamedTuple` make immutability easy to achieve.

For large-scale data processing, copying everything every time can be inefficient. Use generators or structural sharing to avoid unnecessary copies while preserving the benefits of immutability.

## Checklist

- [ ] I can distinguish mutable and immutable types in Python
- [ ] I can use tuple and frozenset appropriately
- [ ] I can define a frozen dataclass and update it with `replace()`
- [ ] I can apply immutable patterns that avoid mutating function arguments
- [ ] I can explain the trade-offs of immutable data

## Exercises

1. Refactor a configuration manager that uses a mutable `dict` into a frozen dataclass.
2. Implement a simple text editor with undo support using immutable patterns.
3. Define a 2D vector with `NamedTuple` and write add, subtract, and scalar multiply functions.

## Summary and Next Steps

Immutable data eliminates unpredictable changes and increases code stability. Python provides tuple, frozenset, NamedTuple, and frozen dataclass for implementing immutability. The next article covers **higher-order functions** — functions that accept and return other functions.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Immutable Data?**
  - The article treats Immutable Data as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Immutable Data?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Immutable Data reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Functional Programming 101 (1/10): What Is Functional Programming?](./01-what-is-fp.md)
- [Functional Programming 101 (2/10): Pure Functions and Side Effects](./02-pure-functions.md)
- **Immutable Data (current)**
- Higher-Order Functions (upcoming)
- map, filter, reduce (upcoming)
- Closures and Partial Application (upcoming)
- Recursion and Tail Calls (upcoming)
- Lazy Evaluation and Generators (upcoming)
- Function Composition and Pipelines (upcoming)
- Balancing OOP and Functional Programming (upcoming)

<!-- toc:end -->

## References

- [Python Official Docs — Data Model (Immutable Types)](https://docs.python.org/3/reference/datamodel.html)
- [Real Python — Immutability in Python](https://realpython.com/python-mutable-vs-immutable-types/)
- [Fluent Python — Chapter 8: Object References, Mutability, and Recycling](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)
- [Python Official Docs — dataclasses (frozen)](https://docs.python.org/3/library/dataclasses.html)

Tags: Python, Functional Programming, Immutability, tuple, frozenset
