
# Sets and Set Operations

> Data Structures with Python 101 Series (9/10)

<!-- a-grade-intro:begin -->

**Key Question**: What data structure gives you O(1) deduplication and membership testing?

> Python's set is backed by a hash table, so adding, removing, and checking membership are all O(1). It also provides mathematical set operations — union, intersection, difference, and symmetric difference — out of the box. This article covers set internals and practical usage patterns.

<!-- a-grade-intro:end -->

## What You Will Learn

- Set internals and performance characteristics
- Union, intersection, difference, and symmetric difference
- frozenset use cases
- Practical patterns using sets

## Why It Matters

Deduplication, membership checks, and comparing two collections are extremely common in data processing. With a list, these operations are O(n). With a set, they are O(1). The larger the data, the more decisive this difference becomes.

> A set is essentially a dict without values. It is a hash table that stores only keys.

Set operations are used heavily in data analysis, permission management, and tag systems.

## Concept Overview

> set = a collection of unique elements, backed by a hash table

```
A = {1, 2, 3, 4}      B = {3, 4, 5, 6}

union        A | B  = {1, 2, 3, 4, 5, 6}
intersection A & B  = {3, 4}
difference   A - B  = {1, 2}
sym. diff.   A ^ B  = {1, 2, 5, 6}
```

## Key Concepts

| Term | Description |
|------|------------|
| set | A hash-based collection that does not allow duplicates |
| frozenset | An immutable set that can be used as a dict key or set element |
| union | All elements from both sets combined |
| intersection | Elements common to both sets |
| difference | Elements in one set but not the other |

## Before / After

Compare deduplication and finding common elements with a list versus a set.

```python
# before: deduplication and intersection with list — O(n^2)
list_a = [1, 2, 3, 4, 2, 3]
unique = []
for x in list_a:
    if x not in unique:
        unique.append(x)
common = [x for x in list_a if x in [3, 4, 5, 6]]
```

```python
# after: deduplication and intersection with set — O(n)
set_a = {1, 2, 3, 4, 2, 3}   # automatic dedup → {1, 2, 3, 4}
common = set_a & {3, 4, 5, 6}  # O(min(m, n)) intersection
```

## Hands-On Steps

### Step 1: Basic set operations

```python
# Creation
fruits = {"apple", "banana", "cherry"}
numbers = set([1, 2, 3, 2, 1])  # {1, 2, 3}

# Add — O(1)
fruits.add("date")

# Remove — O(1)
fruits.discard("banana")  # no error if missing
# fruits.remove("banana")  # raises KeyError if missing

# Membership test — O(1)
print("apple" in fruits)  # True

# Size
print(len(fruits))  # 3
```

### Step 2: Set operations

```python
a = {1, 2, 3, 4, 5}
b = {4, 5, 6, 7, 8}

# Union
print(a | b)          # {1, 2, 3, 4, 5, 6, 7, 8}
print(a.union(b))     # same result

# Intersection
print(a & b)              # {4, 5}
print(a.intersection(b))  # same result

# Difference
print(a - b)            # {1, 2, 3}
print(a.difference(b))  # same result

# Symmetric difference (elements in only one set)
print(a ^ b)                      # {1, 2, 3, 6, 7, 8}
print(a.symmetric_difference(b))  # same result
```

### Step 3: Subsets and supersets

```python
a = {1, 2, 3}
b = {1, 2, 3, 4, 5}

print(a <= b)          # True — a is a subset of b
print(a.issubset(b))   # True

print(b >= a)            # True — b is a superset of a
print(b.issuperset(a))   # True

print(a.isdisjoint({6, 7}))  # True — no common elements
```

### Step 4: frozenset usage

```python
# frozenset: immutable set — can be used as a dict key
permissions = frozenset(["read", "write"])
other = frozenset(["read", "write"])

# Use as dict key
role_map = {
    frozenset(["read"]): "viewer",
    frozenset(["read", "write"]): "editor",
    frozenset(["read", "write", "admin"]): "admin",
}
print(role_map[permissions])  # "editor"

# Use as set element
set_of_sets = {frozenset([1, 2]), frozenset([3, 4])}
print(frozenset([1, 2]) in set_of_sets)  # True
```

### Step 5: Practical pattern — tag filtering

```python
articles = [
    {"title": "Python Intro", "tags": {"python", "beginner"}},
    {"title": "Django REST", "tags": {"python", "django", "api"}},
    {"title": "React Hooks", "tags": {"javascript", "react"}},
    {"title": "Flask API", "tags": {"python", "flask", "api"}},
]

# Articles with BOTH python AND api tags
required = {"python", "api"}
matches = [a for a in articles if required <= a["tags"]]
for m in matches:
    print(m["title"])
# Django REST
# Flask API

# Articles with python OR javascript tags
any_of = {"python", "javascript"}
matches = [a for a in articles if a["tags"] & any_of]
print([m["title"] for m in matches])
# ['Python Intro', 'Django REST', 'React Hooks', 'Flask API']
```

## What to Notice in This Code

- set's `in` operator is O(1), making it ideal for large-scale data lookups
- `|`, `&`, `-`, `^` operators express set operations concisely
- The `<=` operator checks subset relationships
- frozenset is immutable, so it can serve as a dict key or element of another set

## 5 Common Mistakes

| Mistake | Why It Is a Problem | Fix |
|---------|-------------------|-----|
| Creating an empty set with `{}` | `{}` creates an empty dict | Use `set()` to create an empty set |
| Using a list as a set element | Lists are unhashable — causes TypeError | Convert to tuple first |
| Relying on set ordering | Sets do not guarantee order | Use sorted() when order matters |
| Using remove() for a missing element | Raises KeyError | Use discard() to silently ignore missing elements |
| Expecting duplicates in set comprehensions | Duplicates are automatically removed | Verify this is the intended behavior |

## Real-World Applications

- User permissions are managed as sets, with intersection checks for access control
- Duplicate data is removed instantly with set conversion
- Differences between two data sources are computed with set difference
- Tag-based filtering leverages set operations
- Already-processed items are tracked in a set to prevent reprocessing

## How Senior Engineers Think About This

Sets are underappreciated. Many developers default to lists, but using sets for search and deduplication makes code both cleaner and faster.

When the question is "are there duplicates?" or "do these two collections share elements?", set should be the first thing that comes to mind.

## Checklist

- [ ] Can use basic set operations (add, discard, in)
- [ ] Can explain union, intersection, difference, and symmetric difference
- [ ] Can explain the purpose of frozenset
- [ ] Can perform O(1) deduplication and membership checks with set
- [ ] Can check subset and superset relationships

## Exercises

1. Write a function that finds common elements of two lists using set operations and returns them in the original order.
2. Manage course enrollments for multiple students as sets and find courses taken by every student.
3. Extract words from two text files and find words unique to each file using symmetric difference.

## Summary and Next Steps

Sets are hash-table-backed collections that provide O(1) lookups and rich set operations. They excel at deduplication, membership testing, and data comparison. The next article wraps up the series with a comprehensive guide for choosing the right data structure.

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
## References

- [Python Docs — Set Types](https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset)
- [Real Python — Sets in Python](https://realpython.com/python-sets/)
- [Python TimeComplexity — Set](https://wiki.python.org/moin/TimeComplexity)
- [GeeksforGeeks — Python Set](https://www.geeksforgeeks.org/python-set/)

Tags: Python, Data Structures, set, Set Operations, frozenset

---

© 2026 YeongseonBooks. All rights reserved.
