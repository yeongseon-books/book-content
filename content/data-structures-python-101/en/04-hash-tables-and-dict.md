---
series: data-structures-python-101
episode: 4
title: "Data Structures with Python 101 (4/10): Hash Tables and dict"
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
  - Data Structures
  - dict
  - Hash Table
  - Time Complexity
seo_description: Understand how Python dict implements a hash table internally, and learn its performance characteristics and collision handling.
last_reviewed: '2026-05-17'
---

# Data Structures with Python 101 (4/10): Hash Tables and dict

This is the fourth post in the Data Structures with Python 101 series.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Hash Tables and dict?
- Which signal should the example or diagram make visible for Hash Tables and dict?
- What failure should be prevented first when Hash Tables and dict reaches a real system?

## Big Picture

![Data Structures with Python 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-python-101/04/04-01-dict-probe-and-resize.en.png)

*Data Structures with Python 101 chapter 4 flow overview*

This picture places Hash Tables and dict inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Hash Tables and dict is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## What This Article Answers

- How can `dict` find a value among huge numbers of keys so quickly?
- What roles do hashing, collisions, probing, and resizing play?
- Why can some objects be dict keys while others cannot?
- What does insertion order mean in a hash-table-backed mapping?

> Mental model: Python's `dict` is not a bag of key-value pairs with magic lookup. It is a hash table that turns a key into a probe path inside a sparse array, then resizes before the table gets too crowded.

## Why It Matters

`dict` sits at the center of Python. JSON parsing, caching, grouping, configuration loading, and metadata handling all rely on it. If you only memorize "dict lookup is O(1)," you miss the engineering reality that makes that performance possible.

> Fast lookup comes from predictable hashing plus a table layout that stays sparse enough for short probe paths.

That is why collisions, resizing, and hashability matter. They are not side topics. They are the actual reason `dict` stays both correct and fast.

## Concept Overview

> Hash table = a structure that turns a key into a slot candidate, then probes until it finds the right entry or an empty place

```text
key "alice"   -> hash("alice")   -> slot 5
slot 5 occupied? yes  -> probe next slot
slot 6 occupied? yes  -> probe next slot
slot 7 empty?    yes  -> store there
```

## Dict Probe and Resize

## Key Concepts

| Term | Description |
|------|------------|
| Hash Function | Converts a key into an integer used to begin lookup |
| Collision | Different keys compete for the same slot or probe path |
| Probe Path | The sequence of candidate slots checked during lookup or insertion |
| Sparse Table | A table with enough empty space that lookups usually stop quickly |
| Hashable | An object with stable hashing/equality semantics that can safely be used as a key |

## Before / After

Compare a linear scan through tuples with direct lookup.

```python
# before: linear search in a list — O(n)
users = [("alice", 95), ("bob", 82), ("charlie", 90)]
for name, score in users:
    if name == "charlie":
        print(score)
        break
```

```python
# after: instant lookup with dict — average O(1)
users = {"alice": 95, "bob": 82, "charlie": 90}
print(users["charlie"])  # 90
```

This speed is not mystical. `dict` can usually jump straight to a short probe path because the key's hash tells the table where to start.

## Hands-On Steps

### Step 1: Verify the baseline operations

```python
scores = {}

scores["alice"] = 95
scores["bob"] = 82
scores["charlie"] = 90

print(scores["alice"])         # 95
print(scores.get("diana", 0))  # 0

del scores["bob"]
print(scores)                   # {'alice': 95, 'charlie': 90}

print("alice" in scores)       # True
```

### Step 2: Force collisions on purpose

```python
class CollidingKey:
    def __init__(self, label: str):
        self.label = label

    def __hash__(self) -> int:
        return 42

    def __eq__(self, other) -> bool:
        return isinstance(other, CollidingKey) and self.label == other.label

    def __repr__(self) -> str:
        return f"CollidingKey({self.label!r})"

keys = [CollidingKey("alpha"), CollidingKey("beta"), CollidingKey("gamma")]
table = {key: index for index, key in enumerate(keys, start=1)}

print(table)
print(table[CollidingKey("beta")])   # 2
print(CollidingKey("beta") in table) # True
print(len(table))                     # 3
```

Example output:

```text
{CollidingKey('alpha'): 1, CollidingKey('beta'): 2, CollidingKey('gamma'): 3}
2
True
3
```

#### How to read this result

- We deliberately forced every key to produce the same hash value.
- `dict` still stores and retrieves all three keys correctly because equality distinguishes them after the collision.
- The lesson is not that collisions never happen. The lesson is that Python `dict` stays correct and usually fast because collisions are resolved inside the table, and the table resizes before high crowding turns lookups into long searches.

### Step 3: Observe insertion order, deletion, and reinsertion

```python
events = {"queued": 1, "running": 2, "done": 3}
print(list(events))

del events["running"]
events["running"] = 22

print(list(events))
print(events)
```

Example output:

```text
['queued', 'running', 'done']
['queued', 'done', 'running']
{'queued': 1, 'done': 3, 'running': 22}
```

#### How to read this result

Python preserves the insertion order of keys that currently exist in the dictionary. But if you delete a key and add it again, that key returns as a new insertion and appears at the end. Order is preserved for the live dictionary state, not for the full historical timeline of a key.

### Step 4: Check the hashable / unhashable boundary

```python
print(hash("hello"))    # varies by session
print(hash((1, 2, 3)))   # tuples are hashable

try:
    hash([1, 2, 3])
except TypeError as error:
    print(f"error: {error}")
```

Mutable containers like `list`, `dict`, and `set` cannot be dict keys because their contents can change, which would break stable hashing.

### Step 5: Use higher-level dict tools after the internals are clear

```python
from collections import Counter, defaultdict

word_count = defaultdict(int)
for word in "the cat sat on the mat".split():
    word_count[word] += 1

print(dict(word_count))

counter = Counter("the cat sat on the mat".split())
print(counter.most_common(2))
```

`defaultdict` and `Counter` are still worth learning, but they make more sense once the base dict mental model is solid.

## What to Notice in This Code

- `dict` lookup, insert, and delete are average-case O(1), not guaranteed worst-case O(1).
- A collision means "multiple keys start from the same place," not "the dictionary breaks."
- CPython `dict` is best pictured as a sparse open-addressed table, not as a chain of linked buckets.
- Insertion order is preserved, but delete-and-reinsert moves a key to the end.
- Correct keys need stable hashing and meaningful equality.

Many textbooks teach hash tables with separate chaining because it is easy to draw. That model is useful for general computer science intuition, but it should not be your main mental picture for Python `dict`.

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|-------------------|-----|
| Accessing a missing key with `d[key]` | Raises `KeyError` | Use `d.get(key, default)` or check membership first |
| Using a mutable object as a dict key | Mutable objects are unhashable or unsafe as keys | Use immutable values such as `str`, `int`, `tuple`, or `frozenset` |
| Assuming collisions mean wrong results | Collisions are normal; wrong equality semantics are the real danger | Make `__hash__` and `__eq__` consistent |
| Assuming dict order means sorting | `dict` preserves insertion order, not sorted order | Use `sorted()` when sorted output matters |
| Deleting and reinserting while expecting the old position | Reinsertion creates a new order position | Rebuild order explicitly if stable placement matters |

## Real-World Applications

- JSON objects arrive as dicts and are traversed by key.
- Caches and memoization layers depend on fast key lookup.
- Frequency counting often starts with `dict` and graduates to `Counter`.
- API metadata, headers, and config blobs are modeled as key-value mappings.
- Grouping and indexing tasks often build dicts keyed by IDs, slugs, or composite tuples.

## How Senior Engineers Think About This

Senior engineers treat `dict` as infrastructure, not just syntax. The design question is whether the key has stable identity and whether order matters for downstream behavior.

They also know that average-case O(1) depends on maintaining a healthy table shape. That is why key design, load, and accidental mutation matter more than memorizing the word "hash table."

## Checklist

- [ ] Can explain why `dict` uses hashing to begin lookup
- [ ] Can explain what a collision is without implying incorrect results
- [ ] Can describe how delete-and-reinsert affects key order
- [ ] Can distinguish hashable from unhashable objects
- [ ] Can explain why Python `dict` should be pictured as a sparse probing table

## Exercises

1. Extend `CollidingKey` so that ten distinct keys all share one hash value, then verify every key still round-trips correctly.
2. Build a dict, delete one key, reinsert it, and explain why the new order is still consistent with insertion-order preservation.
3. Write a grouping function keyed by `frozenset` and explain why plain `set` cannot be used as the key.

## Summary and Next Steps

Python `dict` is a hash-table-backed mapping whose performance depends on three ideas working together: stable hashing, short probe paths, and periodic resizing. Once that model is clear, collisions and preserved insertion order stop feeling contradictory. The next article shifts to linked lists, which store data in a completely different way from arrays and hash tables.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Hash Tables and dict?**
  - The article treats Hash Tables and dict as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Hash Tables and dict?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Hash Tables and dict reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Data Structures with Python 101 (1/10): What Are Data Structures?](./01-what-are-data-structures.md)
- [Data Structures with Python 101 (2/10): Arrays and Lists](./02-arrays-and-lists.md)
- [Data Structures with Python 101 (3/10): Stacks and Queues](./03-stacks-and-queues.md)
- **Hash Tables and dict (current)**
- Linked Lists (upcoming)
- Trees and Binary Trees (upcoming)
- Heaps and Priority Queues (upcoming)
- Graph Representations (upcoming)
- Sets and Set Operations (upcoming)
- Choosing the Right Data Structure (upcoming)

<!-- toc:end -->

## References

- [Python Official Docs — Mapping Types (`dict`)](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict)
- [CPython dict implementation (GitHub)](https://github.com/python/cpython/blob/main/Objects/dictobject.c)
- [Python Data Model — `__hash__` and `__eq__`](https://docs.python.org/3/reference/datamodel.html#object.__hash__)
- [Real Python — Dictionaries in Python](https://realpython.com/python-dicts/)
- [Hash Table — Wikipedia](https://en.wikipedia.org/wiki/Hash_table)

Tags: Python, Data Structures, dict, Hash Table, Time Complexity
