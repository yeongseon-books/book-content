---
series: data-structures-python-101
episode: 4
title: Hash Tables and dict
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
  - Data Structures
  - dict
  - Hash Table
  - Time Complexity
seo_description: Understand how Python dict implements a hash table internally, and learn its performance characteristics and collision handling.
last_reviewed: '2026-05-04'
---

# Hash Tables and dict

> Data Structures with Python 101 Series (4/10)

<!-- a-grade-intro:begin -->

**Key Question**: How does dict instantly find a value among millions of keys?

> dict is implemented internally as a hash table. It converts a key to an integer via a hash function, computes an array index, and stores the value at that location. This article covers hash table internals, dict behavior, and hash collision handling.

<!-- a-grade-intro:end -->

This is post 4 in the Data Structures with Python 101 series.

## What You Will Learn

- How hash tables work
- Internal implementation of Python dict
- Hash collisions and resolution strategies
- Time complexity of dict operations

## Why It Matters

dict is the second most used data structure in Python. JSON parsing, configuration management, caching, data grouping — dict is everywhere. Understanding hash table internals helps you use dict more effectively.

> A hash table maps "key to value" in O(1). This performance is constant regardless of data size.

"Why is dict O(1)?" is a common interview question. You need to understand hash functions, hash collisions, and resizing to answer accurately.

## Concept Overview

> Hash table = a data structure that maps keys to array indices via a hash function

```
key "alice"   -> hash("alice")  -> index 3
key "bob"     -> hash("bob")    -> index 7
key "charlie" -> hash("charlie")-> index 1

array:  [   |charlie|   |alice|   |   |   |bob|   ]
index:    0     1     2    3    4   5   6   7   8
```

## Key Concepts

| Term | Description |
|------|------------|
| Hash Function | Converts arbitrary-sized data to a fixed-size integer |
| Hash Collision | Occurs when different keys map to the same index |
| Load Factor | The ratio of stored elements to array size; higher values increase collisions |
| Resizing | Expanding the array when the load factor exceeds a threshold |
| Hashable | An immutable object that implements __hash__() and can be used as a dict key |

## Before / After

Compare linear search through a list of tuples with instant dict lookup.

```python
# before: linear search in a list — O(n)
users = [("alice", 95), ("bob", 82), ("charlie", 90)]
for name, score in users:
    if name == "charlie":
        print(score)
        break
```

```python
# after: instant lookup with dict — O(1)
users = {"alice": 95, "bob": 82, "charlie": 90}
print(users["charlie"])  # 90
```

## Hands-On Steps

### Step 1: Basic dict operations

```python
scores = {}

# insert — O(1)
scores["alice"] = 95
scores["bob"] = 82
scores["charlie"] = 90

# lookup — O(1)
print(scores["alice"])      # 95
print(scores.get("diana", 0))  # 0 — default when key is missing

# delete — O(1)
del scores["bob"]
print(scores)  # {'alice': 95, 'charlie': 90}

# membership check — O(1)
print("alice" in scores)    # True
```

### Step 2: Inspect the hash() function

```python
# immutable objects are hashable
print(hash("hello"))    # a fixed integer (varies per session)
print(hash(42))         # 42
print(hash((1, 2, 3)))  # tuples are hashable

# mutable objects are not hashable
try:
    hash([1, 2, 3])
except TypeError as e:
    print(f"error: {e}")  # unhashable type: 'list'
```

### Step 3: Build a simple hash table from scratch

```python
class SimpleHashTable:
    def __init__(self, size: int = 10):
        self._size = size
        self._buckets = [[] for _ in range(size)]

    def _hash(self, key: str) -> int:
        return hash(key) % self._size

    def put(self, key: str, value):
        idx = self._hash(key)
        for i, (k, v) in enumerate(self._buckets[idx]):
            if k == key:
                self._buckets[idx][i] = (key, value)
                return
        self._buckets[idx].append((key, value))

    def get(self, key: str, default=None):
        idx = self._hash(key)
        for k, v in self._buckets[idx]:
            if k == key:
                return v
        return default

ht = SimpleHashTable()
ht.put("name", "Alice")
ht.put("age", 30)
print(ht.get("name"))   # Alice
print(ht.get("email"))  # None
```

### Step 4: Use defaultdict and Counter

```python
from collections import defaultdict, Counter

# defaultdict: auto-creates default values for missing keys
word_count = defaultdict(int)
for word in "the cat sat on the mat".split():
    word_count[word] += 1
print(dict(word_count))
# {'the': 2, 'cat': 1, 'sat': 1, 'on': 1, 'mat': 1}

# Counter: built for frequency counting
counter = Counter("the cat sat on the mat".split())
print(counter.most_common(2))  # [('the', 2), ('cat', 1)]
```

### Step 5: dict comprehension and sorting

```python
scores = {"alice": 95, "bob": 82, "charlie": 90, "diana": 88}

# dict comprehension
high_scores = {k: v for k, v in scores.items() if v >= 90}
print(high_scores)  # {'alice': 95, 'charlie': 90}

# sort by value
sorted_scores = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
print(sorted_scores)
# {'alice': 95, 'charlie': 90, 'diana': 88, 'bob': 82}
```

## What to Notice in This Code

- dict lookup, insert, and delete are O(1) on average but O(n) in the worst case
- hash() results differ across Python sessions (hash randomization for security)
- Mutable objects (list, dict, set) cannot be hashed and cannot be used as dict keys
- Since Python 3.7, dict preserves insertion order

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|-------------------|-----|
| Accessing a missing key with `d[key]` | Raises KeyError | Use `d.get(key, default)` or check `key in d` first |
| Using a list as a dict key | TypeError — lists are unhashable | Convert to tuple first |
| Adding/deleting keys while iterating over dict | Raises RuntimeError | Iterate over `list(d.keys())` instead |
| Assuming dict comparison depends on order | dict comparison is order-independent, but this can cause confusion | Use `==` operator, which ignores order |
| Missing default values in nested dicts | Raises KeyError | Use defaultdict(dict) or setdefault() |

## Real-World Applications

- JSON responses are parsed into dicts for data extraction
- Environment variables and configuration are managed in dicts
- Caches are implemented with dicts to avoid redundant computation
- Log data is aggregated with Counter
- API parameters are passed as dicts

## How Senior Engineers Think About This

dict is at the core of Python. Module, class, and instance attributes are all managed by dicts. Understanding dict performance means understanding Python itself at a deeper level.

In practice, dataclasses and Pydantic models are increasingly used for structured data. But they all rely on dict internally, so understanding how dict works is essential.

## Checklist

- [ ] Can explain how a hash table works
- [ ] Can state the time complexity of dict lookup, insert, and delete
- [ ] Can distinguish hashable from unhashable objects
- [ ] Can use defaultdict and Counter
- [ ] Can transform data with dict comprehensions

## Exercises

1. Write a function that counts the frequency of each string in a list using a plain dict. (No Counter.)
2. Write a function that checks whether two dicts have exactly the same keys.
3. Write a function that retrieves a value from a nested dict `{"a": {"b": {"c": 1}}}` using dot notation like `"a.b.c"`.

## Summary and Next Steps

dict is implemented as a hash table and provides O(1) lookups. Understanding hash functions, collisions, and hashable objects helps you use dict more effectively. The next article covers linked lists, a data structure that connects data in a fundamentally different way from arrays.

<!-- toc:begin -->
- [What Are Data Structures?](./01-what-are-data-structures.md)
- [Arrays and Lists](./02-arrays-and-lists.md)
- [Stacks and Queues](./03-stacks-and-queues.md)
- **Hash Tables and dict (current)**
- Linked Lists (upcoming)
- Trees and Binary Trees (upcoming)
- Heaps and Priority Queues (upcoming)
- Graph Representations (upcoming)
- Sets and Set Operations (upcoming)
- Choosing the Right Data Structure (upcoming)
<!-- toc:end -->

## References

- [Python Official Docs — Mapping Types (dict)](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict)
- [CPython dict implementation (GitHub)](https://github.com/python/cpython/blob/main/Objects/dictobject.c)
- [Real Python — Dictionaries in Python](https://realpython.com/python-dicts/)
- [Hash Table — Wikipedia](https://en.wikipedia.org/wiki/Hash_table)

Tags: Python, Data Structures, dict, Hash Table, Time Complexity
