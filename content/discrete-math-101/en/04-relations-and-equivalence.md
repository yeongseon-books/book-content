---
series: discrete-math-101
episode: 4
title: "Discrete Math 101 (4/10): Relations and Equivalence"
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
  - Discrete Math
  - Relations
  - Equivalence Classes
  - Partial Order
  - Data Modeling
seo_description: Binary relations, the reflexive, symmetric, and transitive properties, equivalence partitions, and partial orders with topological sort.
last_reviewed: '2026-05-04'
---

# Discrete Math 101 (4/10): Relations and Equivalence

This is post 4 in the Discrete Math 101 series.

> Discrete Math 101 series (4/10)

**Core question**: A database "relation," the `==` operator, the topological sort of a dependency graph — what is the shared mathematical structure?

> A relation is a subset of a Cartesian product expressing "some connection" between two elements. Combinations of properties (reflexive, symmetric, transitive) define equivalence relations and partial orders, which underpin partitions, ordering, and hierarchies. This article covers relations, their properties, equivalence classes, and topological sort.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Relations and Equivalence?
- Which signal should the example or diagram make visible for Relations and Equivalence?
- What failure should be prevented first when Relations and Equivalence reaches a real system?

## Big Picture

![discrete math 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/discrete-math-101/04/04-01-big-picture.en.png)

*discrete math 101 chapter 4 flow overview*

This picture places Relations and Equivalence inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## What You Will Learn

- The definition and representation of binary relations
- Reflexive, symmetric, transitive, and antisymmetric properties
- Equivalence relations, equivalence classes, and the partition theorem
- Partial orders and topological sort

## Why It Matters

The relational database model came directly from relation theory. Git's commit graph, npm dependency resolution, and build tool task scheduling are all topological sorts on partial orders. The `==` and `is` operators along with caching strategies are applications of equivalence relations.

> A relation is the most basic tool for expressing structure between data.

> A relation is a set of pairs (a, b). Depending on which properties hold, it is classified as an equivalence relation, a partial order, etc.

```text
   Relation R ⊆ A × A
        │
   ┌────┴────┬──────────┐
 Reflexive   Symmetric  Transitive
   │         │          │
   └────┬────┘          │
   Equivalence ↔ Partition
                         │
   Refl ∧ Antisym ∧ Trans = Partial order → Topological sort
```

## Key Terms

| Term | Meaning |
| --- | --- |
| Binary relation | A subset of A × A |
| Reflexive | (a, a) ∈ R for every a |
| Symmetric | (a, b) ∈ R ⇒ (b, a) ∈ R |
| Transitive | (a, b), (b, c) ∈ R ⇒ (a, c) ∈ R |
| Equivalence | Reflexive + Symmetric + Transitive |

## Before / After

**Before — no relational thinking:**

```python
# Ad-hoc comparison: "are these two objects the same?"
def same_user(a, b):
    return a.id == b.id and a.email == b.email
```

**After — explicit equivalence relation:**

```python
# Group items into equivalence classes — usable as cache keys
def equivalence_class(item, items, eq):
    return {x for x in items if eq(item, x)}
```

## Hands-On: Step by Step

### Step 1: Representing a Relation

```python
# A relation is a set of (a, b) pairs
people = {"alice", "bob", "carol"}
friends = {("alice", "bob"), ("bob", "alice"), ("bob", "carol"), ("carol", "bob")}

print(f"alice's friends: {[b for (a, b) in friends if a == 'alice']}")

# Matrix representation
import numpy as np

names = sorted(people)
n = len(names)
M = np.zeros((n, n), dtype=int)
for a, b in friends:
    M[names.index(a)][names.index(b)] = 1

print(f"Adjacency matrix:\n{M}")
```

A relation can be a set of pairs, an adjacency matrix, or an adjacency list. We meet these forms again with graphs in Chapter 8.

### Step 2: The Core Properties

```python
def is_reflexive(R: set, A: set) -> bool:
    return all((a, a) in R for a in A)

def is_symmetric(R: set) -> bool:
    return all((b, a) in R for (a, b) in R)

def is_transitive(R: set) -> bool:
    return all(
        (a, c) in R
        for (a, b) in R
        for (b2, c) in R
        if b == b2
    )

def is_antisymmetric(R: set) -> bool:
    return all(
        a == b for (a, b) in R if (b, a) in R
    )

A = {1, 2, 3}
R_eq = {(1, 1), (2, 2), (3, 3), (1, 2), (2, 1)}
print(f"Reflexive: {is_reflexive(R_eq, A)}")
print(f"Symmetric: {is_symmetric(R_eq)}")
print(f"Transitive: {is_transitive(R_eq)}")
```

### Step 3: Equivalence Relations and Classes

```python
# Equivalence: reflexive + symmetric + transitive
# Example: integers modulo 3
def mod_equivalent(a: int, b: int, n: int = 3) -> bool:
    return (a - b) % n == 0

numbers = list(range(10))

def equivalence_class(x: int, domain: list, eq) -> set:
    return {y for y in domain if eq(x, y)}

for i in range(3):
    cls = equivalence_class(i, numbers, mod_equivalent)
    print(f"[{i}] = {sorted(cls)}")

# Equivalence classes partition the domain
all_classes = {frozenset(equivalence_class(x, numbers, mod_equivalent)) for x in numbers}
print(f"Partition: {[sorted(c) for c in all_classes]}")
```

Equivalence relations always induce partitions and vice versa — the two notions are in bijection. Cache invalidation, deduplication, and clustering all reduce to defining the right equivalence.

### Step 4: Partial Orders and Hasse Diagrams

```python
# Partial order: reflexive + antisymmetric + transitive
# Example: subset relation ⊆
A = [{1}, {2}, {1, 2}, {1, 2, 3}]

def is_subset_of(x: set, y: set) -> bool:
    return x <= y

# Cover relation: x ⊂ y with no element strictly in between
def covers(x, y, items):
    if x == y or not is_subset_of(x, y):
        return False
    return not any(
        is_subset_of(x, z) and is_subset_of(z, y) and z != x and z != y
        for z in items
    )

for x in A:
    for y in A:
        if covers(x, y, A):
            print(f"{x} ⋖ {y}")
```

In a partial order, not every pair must be comparable — that's how it differs from a total order. Directory trees, class inheritance, and Git commit DAGs are all partial orders.

### Step 5: Topological Sort

```python
from collections import defaultdict, deque

def topological_sort(nodes: list, edges: list[tuple]) -> list:
    """Return a linear order respecting the partial order."""
    graph = defaultdict(list)
    indegree = {n: 0 for n in nodes}
    for a, b in edges:
        graph[a].append(b)
        indegree[b] += 1

    queue = deque([n for n in nodes if indegree[n] == 0])
    result = []
    while queue:
        node = queue.popleft()
        result.append(node)
        for nxt in graph[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    return result if len(result) == len(nodes) else []

tasks = ["wake_up", "shower", "breakfast", "work"]
deps = [("wake_up", "shower"), ("shower", "breakfast"), ("breakfast", "work")]
print(f"Execution order: {topological_sort(tasks, deps)}")
```

Topological sort produces a linear ordering that satisfies every constraint of a partial order. Build tools (make, gradle), package managers, and task schedulers all use it.

## Notable Points

- Relations are subsets of Cartesian products — simple definition, rich structure
- Equivalence relation ↔ partition is a one-to-one correspondence
- Partial orders are weaker than total orders but more general
- Topological sort exists only when there are no cycles

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Skip an equivalence property | Reflexivity or transitivity check missed | Verify all three explicitly |
| Confuse partial and total order | Cannot handle incomparable pairs | Partial order compares only some pairs |
| Topological sort with cycles | Infinite loop or empty result | Check for cycles first |
| Treat classes and partitions separately | Reimplement the same idea twice | Define one, derive the other |
| Confuse symmetry and antisymmetry | Both can hold on empty relations | Use definitions strictly |

## How This Is Used in Practice

- Database normalization rests on functional dependencies (a partial order)
- npm/pip dependency resolution is topological sort
- Git's ancestor relation is a partial order
- Cache key design is the same as defining an equivalence relation
- An ORM's `equals()` must satisfy the equivalence laws

## How a Senior Engineer Thinks

When defining "equality," senior engineers always check the three equivalence properties. Java's `equals()` contract and Python's `__eq__` rely on them — break them and collections break too. When designing task scheduling, the first question is "is this dependency a partial order with no cycles?"

## Checklist

- [ ] I can define the four relation properties
- [ ] I remember the three equivalence laws
- [ ] I see the bijection between equivalence and partition
- [ ] I distinguish partial vs total order
- [ ] I know topological sort requires no cycles

## Practice Problems

1. Decide whether "same sign" is an equivalence relation on the integers and list its equivalence classes.

2. Express your directory layout as a partial order and write one valid topological order.

3. Construct a broken `__eq__` in Python that violates transitivity and explain what goes wrong.

## Wrap-Up and Next Steps

A relation is a subset of a Cartesian product, and combinations of properties produce equivalences and partial orders. Equivalences yield partitions; partial orders yield topological sorts. These structures are the math behind data modeling and task scheduling.

Next, we examine how to "rigorously prove" claims like these — direct, contradiction, and induction proofs.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Relations and Equivalence?**
  - The article treats Relations and Equivalence as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Relations and Equivalence?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Relations and Equivalence reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Discrete Math 101 (1/10): What Is Discrete Mathematics?](./01-what-is-discrete-math.md)
- [Discrete Math 101 (2/10): Propositions and Logic](./02-propositions-and-logic.md)
- [Discrete Math 101 (3/10): Sets and Functions](./03-sets-and-functions.md)
- **Relations and Equivalence (current)**
- Proof Techniques (upcoming)
- Sequences and Recurrence (upcoming)
- Combinatorics (upcoming)
- Graph Theory Basics (upcoming)
- Trees and Graph Traversal (upcoming)
- Discrete Mathematics and Algorithms (upcoming)

<!-- toc:end -->

## References

- [Discrete Mathematics and Its Applications — Kenneth Rosen, Chapter 9](https://www.mheducation.com/highered/product/discrete-mathematics-its-applications-rosen/M9781259676512.html)
- [Wikipedia — Equivalence Relation](https://en.wikipedia.org/wiki/Equivalence_relation)
- [Wikipedia — Partially Ordered Set](https://en.wikipedia.org/wiki/Partially_ordered_set)
- [Wikipedia — Topological Sorting](https://en.wikipedia.org/wiki/Topological_sorting)

Tags: Computer Science, Discrete Math, Relations, Equivalence Classes, Partial Order, Data Modeling
