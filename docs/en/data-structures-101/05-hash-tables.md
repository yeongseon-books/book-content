---
series: data-structures-101
episode: 5
title: Hash Tables
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
  - Data Structures
  - Hash Table
  - Hash Function
  - Collision Resolution
  - Python dict
seo_description: How a hash table delivers average O(1) lookup, with collision handling and rehashing implemented from scratch alongside Python's dict.
last_reviewed: '2026-05-04'
---

# Hash Tables

> Data Structures 101 series (5/10)

<!-- a-grade-intro:begin -->

**Core question**: Would you believe a structure that finds one entry among a trillion in roughly one operation?

> A hash table converts a key to an integer index using a hash function, and then jumps straight into an array. Average time complexity is O(1) — astonishing performance — but you must handle collisions, rehashing, and hash quality carefully. This article walks through how a hash table works, two collision strategies (chaining and open addressing), and the design ideas inside Python's dict.

<!-- a-grade-intro:end -->

## What You Will Learn

- The role of a hash function and what makes one good
- Why collisions happen and how to resolve them
- The relationship between load factor and rehashing
- How Python's dict and set work internally

## Why It Matters

Hash tables sit in the standard library of nearly every language: Python's dict and set, Java's HashMap, JavaScript's Object and Map. Database indexes, caches, and compiler symbol tables all use hash tables. The single fact that average lookup is O(1) makes a great deal of computer science possible.

> Without dict, half of the algorithm problems become hard.

## Concept at a Glance

> A hash table runs a two-step transform: "key → hash value → index" — landing on a specific slot in an array. When two keys map to the same slot, you resolve the collision with chaining (a linked list) or open addressing (probe for the next empty slot).

```text
"apple" → hash() → 17234... → % 8 → 2
"banana" → hash() → 89123... → % 8 → 7

index: 0  1  2  3  4  5  6  7
array:[ ][ ][ap][ ][ ][ ][ ][ba]

When a collision occurs (chaining)
index 2: ["apple", 1] → ["apricot", 5]
```

## Key Terms

| Term | Meaning |
| --- | --- |
| Hash function | A function mapping keys to integers |
| Bucket | One slot of the underlying array |
| Collision | When two keys map to the same index |
| Load factor | (entries stored) / (array size) |
| Rehashing | Moving everything to a larger array when the load factor grows |

## Before / After

**Before — searching keys with a list:**

```python
users = [(1, "Alice"), (2, "Bob"), (3, "Carol"), ...]   # one million entries

def find(uid):
    for k, v in users:
        if k == uid:
            return v
    return None
# average O(n)
```

**After — searching keys with a dict:**

```python
users = {1: "Alice", 2: "Bob", 3: "Carol", ...}

def find(uid):
    return users.get(uid)
# average O(1)
```

## Hands-On: Step by Step

### Step 1: A Minimal Hash Table (Chaining)

```python
class HashTable:
    def __init__(self, capacity=8):
        self._capacity = capacity
        self._size = 0
        self._buckets = [[] for _ in range(capacity)]

    def _index(self, key):
        return hash(key) % self._capacity

    def put(self, key, value):
        bucket = self._buckets[self._index(key)]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self._size += 1

    def get(self, key):
        for k, v in self._buckets[self._index(key)]:
            if k == key:
                return v
        raise KeyError(key)


h = HashTable()
h.put("apple", 1); h.put("banana", 2)
print(h.get("apple"))   # 1
```

Each bucket is a list of key-value pairs. On a collision, you append to the same bucket.

### Step 2: Load Factor and Rehashing

```python
class HashTable2(HashTable):
    LOAD_FACTOR_LIMIT = 0.75

    def put(self, key, value):
        if (self._size + 1) / self._capacity > self.LOAD_FACTOR_LIMIT:
            self._rehash(self._capacity * 2)
        super().put(key, value)

    def _rehash(self, new_capacity):
        old = [(k, v) for bucket in self._buckets for k, v in bucket]
        self._capacity = new_capacity
        self._buckets = [[] for _ in range(new_capacity)]
        self._size = 0
        for k, v in old:
            super().put(k, v)


h = HashTable2(capacity=4)
for i in range(10):
    h.put(f"key{i}", i)
    print(f"size={h._size}, capacity={h._capacity}")
```

When the load factor exceeds 0.75, the array doubles and every key is rehashed. It is expensive but rare, so amortized cost stays at O(1).

### Step 3: Open Addressing (Linear Probing)

```python
class OpenAddressTable:
    _EMPTY = object()
    _DELETED = object()

    def __init__(self, capacity=8):
        self._capacity = capacity
        self._slots = [self._EMPTY] * capacity
        self._size = 0

    def _probe(self, key):
        idx = hash(key) % self._capacity
        for _ in range(self._capacity):
            slot = self._slots[idx]
            if slot is self._EMPTY or (slot is not self._DELETED and slot[0] == key):
                return idx
            idx = (idx + 1) % self._capacity
        raise RuntimeError("table full")

    def put(self, key, value):
        idx = self._probe(key)
        if self._slots[idx] is self._EMPTY:
            self._size += 1
        self._slots[idx] = (key, value)


t = OpenAddressTable()
t.put("a", 1); t.put("b", 2)
```

Instead of chaining, you walk forward to the next empty slot on a collision. Cache friendliness improves, but deletion is tricky (you need a `_DELETED` marker).

### Step 4: The Impact of a Good Hash Function

```python
# Bad hash function: always returns the same value
class BadHash:
    def __init__(self, val):
        self.val = val
    def __hash__(self):
        return 0
    def __eq__(self, other):
        return self.val == other.val


import time

bad_set = set()
start = time.perf_counter()
for i in range(5000):
    bad_set.add(BadHash(i))
print(f"bad hash: {(time.perf_counter() - start) * 1000:.0f} ms")

good_set = set()
start = time.perf_counter()
for i in range(5000):
    good_set.add(i)
print(f"good hash: {(time.perf_counter() - start) * 1000:.0f} ms")
```

If every key lands in the same bucket, the hash table degenerates into a linked list. O(1) collapses to O(n).

### Step 5: Mutable Objects Cannot Be Keys

```python
# What happens if you use a mutable object as a dict key?
key = [1, 2, 3]
try:
    {key: "value"}    # TypeError: unhashable type: 'list'
except TypeError as e:
    print(f"error: {e}")

# A tuple is immutable, so it works as a key
print({(1, 2, 3): "value"})

# A frozenset works too
print({frozenset({1, 2}): "value"})
```

A hash table assumes keys' hashes do not change. If you mutate the key, you can never find it again.

## Notable Points

- The "average O(1)" rests on a good hash function and a sensible load factor
- Collisions are unavoidable; how you handle them defines the structure's character
- Rehashing is expensive but amortized, so the average stays at O(1)
- Open addressing wins on cache friendliness; chaining handles higher load factors gracefully

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Using a mutable object as a key | TypeError or lost keys | Use tuple or frozenset |
| Defining only `__hash__` | Collisions break without `__eq__` | Define both together |
| Ignoring collision risk | Worst case O(n) ignored | Verify hash quality |
| Depending on order | Treating dict order as key order | Sort explicitly |
| Ignoring load factor | Wasted memory or slowdown | Stay near 0.5–0.75 |

## How This Is Used in Practice

- Database hash indexes serve equality lookups in O(1)
- Caches like Redis and Memcached are key-value stores built on hash tables
- Compiler and interpreter symbol tables are hash tables
- Deduplication, frequency counting (`Counter`), and grouping are all dict-based
- Distributed systems use consistent hashing to spread keys across nodes

## How a Senior Engineer Thinks

A senior engineer reaches for dict like a free resource — except in security-sensitive contexts. They know hash flooding can take down a service, so they avoid using untrusted input directly as a hash key, or they switch to a key-aware function like SipHash.

A senior engineer also knows that Python 3.7+ guarantees dict insertion order, but they do not build business logic that depends on it. When explicit order matters, they use `OrderedDict` or a sorted collection. Relying on incidental properties of a structure makes future-you suffer.

## Checklist

- [ ] I can explain what a hash function does and why it is needed
- [ ] I know two strategies for resolving collisions and when each fits
- [ ] I understand the relationship between load factor and rehashing
- [ ] I know why mutable objects cannot be keys
- [ ] I distinguish average O(1) from worst-case O(n)

## Practice Problems

1. Add a `delete(key)` method to the `HashTable` above. It is straightforward with chaining — what makes it tricky with open addressing?

2. Write two versions that count word frequencies — one with a dict, one with a list — and compare their times on a million-word input.

3. To use your own class as a dict key, which methods must you implement? What kinds of bugs appear if you implement them incorrectly?

## Wrap-Up and Next Steps

A hash table converts a key to an integer index and jumps into an array, delivering an overwhelming average O(1) lookup. The trick is a good hash function, careful load-factor management, and a collision strategy. The downsides: weak support for ordered traversal and range queries, and the worst case can degrade to O(n).

Next we look at the structure that naturally expresses hierarchy — the tree. File systems, the DOM, organization charts: nearly every hierarchical dataset shares the same skeleton.

<!-- toc:begin -->
- [What Are Data Structures?](./01-what-are-data-structures.md)
- [Arrays and Dynamic Arrays](./02-arrays-and-dynamic-arrays.md)
- [Linked Lists](./03-linked-lists.md)
- [Stacks and Queues](./04-stacks-and-queues.md)
- **Hash Tables (current)**
- Trees (upcoming)
- Binary Search Trees (upcoming)
- Heaps (upcoming)
- Graphs (upcoming)
- Choosing Data Structures (upcoming)
<!-- toc:end -->

## References

- [Open Data Structures — Hash Tables](https://opendatastructures.org/ods-python/5_Hash_Tables.html)
- [CPython dictobject.c source](https://github.com/python/cpython/blob/main/Objects/dictobject.c)
- [Wikipedia — Hash Table](https://en.wikipedia.org/wiki/Hash_table)
- [Raymond Hettinger — Modern Python Dictionaries (PyCon 2017)](https://www.youtube.com/watch?v=npw4s1QTmPg)
