---
series: data-structures-python-101
episode: 9
title: Sets and Set Operations
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
  - set
  - Set Operations
  - frozenset
seo_description: Explore Python set internals and practice union, intersection, difference, and symmetric difference operations.
last_reviewed: '2026-05-17'
---

# Sets and Set Operations

This is the ninth post in the Data Structures with Python 101 series.

## What This Article Answers

- Why is `set` so strong at deduplication and membership testing?
- What do collisions and hashability mean for a set, not just for a dict?
- Why can `frozenset` be a set element or dict key while plain `set` cannot?
- How do union, intersection, and difference connect back to the storage model?

> Mental model: a Python `set` is a hash table that stores keys only. By giving up duplicates and positional order, it gains fast membership testing and efficient set algebra.

## Why It Matters

Deduplication, membership checks, and collection comparison show up everywhere: permissions, tags, already-processed items, feature flags, and data cleaning. If you model those problems with lists, the code still works, but the cost grows much faster than it needs to.

> `set` belongs to the same hash-table family as `dict`; it simply stores keys without associated values.

That is why the right way to learn sets is not only through operators like `|` and `&`, but also through hashability, collision handling, and uniqueness semantics.

## Concept Overview

> `set` = a hash-table-backed collection of unique keys

```text
A = {1, 2, 3, 4}      B = {3, 4, 5, 6}

union        A | B  = {1, 2, 3, 4, 5, 6}
intersection A & B  = {3, 4}
difference   A - B  = {1, 2}
sym. diff.   A ^ B  = {1, 2, 5, 6}
```

## Set Storage and Dedup

![Set Storage and Dedup](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-python-101/09/09-01-set-storage-and-dedup.en.png)

*How a set stores only unique keys in a hash table, making deduplication and set algebra consequences of the same storage model*

## Key Concepts

| Term | Description |
|------|------------|
| set | A hash-based collection that stores unique keys only |
| Hashability | The requirement that elements have stable hashing and equality semantics |
| Collision | Different values competing for the same lookup/probe path |
| `frozenset` | An immutable set that can itself be hashed |
| Set Algebra | Operations such as union, intersection, difference, and symmetric difference |

## Before / After

Compare list-based deduplication with set-based deduplication.

```python
# before: deduplication and membership with list — O(n^2)
values = [1, 2, 3, 4, 2, 3]
unique = []
for value in values:
    if value not in unique:
        unique.append(value)
```

```python
# after: deduplication with set — average O(n)
values = [1, 2, 3, 4, 2, 3]
unique = set(values)
print(unique)  # {1, 2, 3, 4}
```

The gain is not just speed. `set` also states your intent clearly: duplicates do not matter here, only membership does.

## Hands-On Steps

### Step 1: Verify the basic operations

```python
fruits = {"apple", "banana", "cherry"}

fruits.add("date")
fruits.discard("banana")

print("apple" in fruits)  # True
print(len(fruits))         # 3
```

### Step 2: Force collisions and prove dedup still works

```python
class Tag:
    def __init__(self, name: str):
        self.name = name

    def __hash__(self) -> int:
        return 7

    def __eq__(self, other) -> bool:
        return isinstance(other, Tag) and self.name == other.name

    def __repr__(self) -> str:
        return f"Tag({self.name!r})"


seen = {Tag("python"), Tag("api"), Tag("python")}

print(seen)
print(Tag("python") in seen)  # True
print(len(seen))               # 2
```

Example output:

```text
{Tag('api'), Tag('python')}
True
2
```

#### How to read this result

- All three objects use the same hash value, so collisions are guaranteed.
- The set still keeps only two logical elements because equality says the two `Tag("python")` objects represent the same key.
- Speed comes from hash-table lookup, but correctness depends on stable hashing and meaningful equality.

### Step 3: Go beyond "list is unhashable" and prove why `frozenset` works

```python
try:
    invalid = {{1, 2}}
except TypeError as error:
    print(type(error).__name__, error)

allowed = {frozenset({"read", "write"}), frozenset({"read"})}
print(frozenset({"read", "write"}) in allowed)  # True

role_map = {frozenset({"read", "write"}): "editor"}
print(role_map[frozenset({"write", "read"})])   # editor
```

Example output:

```text
TypeError unhashable type: 'set'
True
editor
```

#### How to read this result

Plain `set` cannot be nested because it is mutable and therefore unhashable. `frozenset` works because its contents cannot change after creation, so Python can safely derive a stable hash and use it as another set element or as a dict key.

### Step 4: Connect set algebra back to storage behavior

```python
a = {1, 2, 3, 4, 5}
b = {4, 5, 6, 7, 8}

print(a | b)  # union
print(a & b)  # intersection
print(a - b)  # difference
print(a ^ b)  # symmetric difference
```

These operators are compact because the underlying structure already thinks in terms of unique keys and membership.

### Step 5: Keep practical filtering as an application, not the proof

```python
articles = [
    {"title": "Python Intro", "tags": {"python", "beginner"}},
    {"title": "Django REST", "tags": {"python", "django", "api"}},
    {"title": "React Hooks", "tags": {"javascript", "react"}},
    {"title": "Flask API", "tags": {"python", "flask", "api"}},
]

required = {"python", "api"}
matches = [article for article in articles if required <= article["tags"]]
print([article["title"] for article in matches])
```

Tag filtering is a great use case, but it matters more once you already trust the internals that make membership and subset checks efficient.

## What to Notice in This Code

- `set` is best understood as a key-only hash table.
- Collisions still happen in sets; they just do not break uniqueness or membership semantics.
- Deduplication works because hashing narrows the search and equality confirms identity.
- `frozenset` is not a convenience alias; it is the immutable version that can itself be hashed.
- Set algebra feels natural because the structure is already optimized for unique-key membership.

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|-------------------|-----|
| Creating an empty set with `{}` | `{}` creates an empty dict | Use `set()` |
| Treating collisions as impossible | Collisions are normal in hash tables | Design stable `__hash__` and `__eq__` |
| Using mutable values as set elements | Mutable values are unhashable or unsafe | Use immutable values such as `tuple` or `frozenset` |
| Assuming set order is meaningful | Set iteration order is not a stable semantic contract | Sort explicitly when presentation order matters |
| Thinking `frozenset` is only for style | It solves the hashability boundary for nested sets and dict keys | Use it when the element itself must be a set |

## Real-World Applications

- Permissions are modeled as sets and compared with intersection/subset logic.
- Deduplication pipelines often turn raw values into sets first.
- Processed IDs are tracked in a set to prevent repeated work.
- Feature flags and tags are naturally modeled as membership sets.
- Differences between two datasets are often clearer as set difference than as loops.

## How Senior Engineers Think About This

Senior engineers reach for `set` when order is not the product requirement but membership is. That single decision often shortens the code and removes accidental O(n²) behavior.

They also know correctness depends on element semantics. If equality or hashing is unstable, the set can no longer give reliable uniqueness or membership answers.

## Checklist

- [ ] Can explain why `set` belongs to the same hash-table family as `dict`
- [ ] Can explain how collisions and equality still produce correct deduplication
- [ ] Can describe the hashability boundary between `set` and `frozenset`
- [ ] Can use union, intersection, difference, and symmetric difference appropriately
- [ ] Can choose `set` when membership matters more than order

## Exercises

1. Extend the `Tag` example so five different objects share one hash value, then verify membership still works correctly.
2. Build a `set` of `frozenset` permission bundles and look up which bundles grant both `read` and `write`.
3. Compare a list-based deduplication loop with `set(values)` on a large input and explain the runtime difference using the storage model.

## Summary and Next Steps

Python `set` is a key-only hash table. That explains its fast membership checks, automatic deduplication, and expressive set algebra. Once you understand that correctness still depends on stable hashing and equality, `set` stops being a convenient trick and becomes a reliable design tool. The next article closes the series by showing how to choose the right data structure for a given workload.

<!-- toc:begin -->
- [What Are Data Structures?](./01-what-are-data-structures.md)
- [Arrays and Lists](./02-arrays-and-lists.md)
- [Stacks and Queues](./03-stacks-and-queues.md)
- [Hash Tables and dict](./04-hash-tables-and-dict.md)
- [Linked Lists](./05-linked-lists.md)
- [Trees and Binary Trees](./06-trees-and-binary-trees.md)
- [Heaps and Priority Queues](./07-heaps-and-priority-queues.md)
- [Graph Representations](./08-graph-representations.md)
- **Sets and Set Operations (current)**
- Choosing the Right Data Structure (upcoming)
<!-- toc:end -->

## References

- [Python Docs — Set Types](https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset)
- [CPython set implementation (GitHub)](https://github.com/python/cpython/blob/main/Objects/setobject.c)
- [Python Data Model — `__hash__` and `__eq__`](https://docs.python.org/3/reference/datamodel.html#object.__hash__)
- [Real Python — Sets in Python](https://realpython.com/python-sets/)
- [Python TimeComplexity — Set](https://wiki.python.org/moin/TimeComplexity)

Tags: Python, Data Structures, set, Set Operations, frozenset
