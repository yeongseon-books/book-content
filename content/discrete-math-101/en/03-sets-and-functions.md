---
series: discrete-math-101
episode: 3
title: Sets and Functions
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
  - Set Theory
  - Functions
  - Databases
  - Data Structures
seo_description: Set operations, function domain and range, injective and bijective functions, and how they form the math behind data structures.
last_reviewed: '2026-05-04'
---

# Sets and Functions

This is post 3 in the Discrete Math 101 series.

> Discrete Math 101 series (3/10)

<!-- a-grade-intro:begin -->

**Core question**: Python's `set`, database tables, hash maps — what is the shared mathematical foundation behind these tools?

> A set is a collection of distinct elements, and a function is a well-defined correspondence from one set to another. Data structures (`set`, `dict`), database relational algebra, and the `map` of functional programming are all direct applications. This article covers set operations, Cartesian products, function classification, and composition with inverses.

<!-- a-grade-intro:end -->

## What You Will Learn

- Set notation and definitions
- Union, intersection, difference, and Cartesian product
- Function domain, codomain, and range
- Injective, surjective, and bijective functions

## Why It Matters

A row in a database is an element of a Cartesian product, and JOIN evaluates a predicate over that product. A hash map is a partial function from keys to values. The functional `map` is function application across sets. Without sets and functions, you cannot understand the essence of these tools.

> A data structure is the efficient implementation of a set or a function.

## Concept at a Glance

> Sets are collections of elements; functions are correspondences between sets. Together they describe every data structure.

```text
   Set A           Function f: A → B           Set B
  ┌─────┐                                    ┌─────┐
  │ a₁  │ ─────────── f(a₁) ─────────────── │ b₁  │
  │ a₂  │ ─────────── f(a₂) ─────────────── │ b₂  │
  │ a₃  │ ─────────── f(a₃) ─────────────── │ b₃  │
  └─────┘                                    └─────┘
   domain                                    codomain
                                              range
                                              ⊆ codomain
```

## Key Terms

| Term | Symbol | Meaning |
| --- | --- | --- |
| Element | a ∈ A | a belongs to set A |
| Subset | A ⊆ B | every element of A is in B |
| Cartesian product | A × B | set of pairs (a, b) |
| Function | f: A → B | maps each element of A to one in B |
| Injective | one-to-one | distinct inputs → distinct outputs |

## Before / After

**Before — without set thinking:**

```python
# Manually deduplicate
result = []
for item in items:
    if item not in result:
        result.append(item)
```

**After — using sets:**

```python
# Leverage the set's intrinsic property
result = list(set(items))
```

## Hands-On: Step by Step

### Step 1: Set Notation

```python
# Roster notation: list elements
A = {1, 2, 3, 4, 5}

# Set-builder notation: state a condition
B = {x for x in range(1, 11) if x % 2 == 0}

# Power set: the set of all subsets
from itertools import chain, combinations


def power_set(s: set) -> list[set]:
    items = list(s)
    return [
        set(combo)
        for r in range(len(items) + 1)
        for combo in combinations(items, r)
    ]


print(f"A = {A}")
print(f"B = {B}")
print(f"|A| = {len(A)}, |P(A)| = {2 ** len(A)}")
print(f"P({{1,2}}) = {power_set({1, 2})}")
```

If |A| = n, then |P(A)| = 2ⁿ. Subsets grow exponentially — this is one root cause of algorithmic complexity.

### Step 2: Set Operations

```python
A = {1, 2, 3, 4, 5}
B = {4, 5, 6, 7, 8}
U = set(range(1, 11))  # universal set

print(f"A ∪ B = {A | B}")        # union
print(f"A ∩ B = {A & B}")        # intersection
print(f"A - B = {A - B}")        # difference
print(f"A △ B = {A ^ B}")        # symmetric difference
print(f"A^c (∈ U) = {U - A}")     # complement
print(f"|A ∪ B| = |A| + |B| - |A ∩ B| = {len(A) + len(B) - len(A & B)}")
```

The last identity is the simplest case of inclusion–exclusion, expanded in Chapter 7.

### Step 3: Cartesian Product and Relations

```python
from itertools import product

A = {1, 2, 3}
B = {"x", "y"}

# A × B = {(a, b) | a ∈ A, b ∈ B}
cartesian = set(product(A, B))
print(f"A × B = {cartesian}")
print(f"|A × B| = |A| × |B| = {len(cartesian)}")

# A database row is an element of a Cartesian product
users = {"alice", "bob"}
roles = {"admin", "user"}
permissions = set(product(users, roles))
print(f"Possible (user, role) pairs: {permissions}")
```

A database table schema is itself a Cartesian product. `CROSS JOIN` literally computes it.

### Step 4: Kinds of Functions

```python
def is_injective(f: dict) -> bool:
    """Injective: distinct inputs map to distinct outputs"""
    return len(set(f.values())) == len(f)


def is_surjective(f: dict, codomain: set) -> bool:
    """Surjective: every codomain element is hit"""
    return set(f.values()) == codomain


def is_bijective(f: dict, codomain: set) -> bool:
    """Bijective: both injective and surjective"""
    return is_injective(f) and is_surjective(f, codomain)


f1 = {1: "a", 2: "b", 3: "c"}     # injective; surjectivity depends on codomain
f2 = {1: "a", 2: "a", 3: "b"}     # not injective
codomain = {"a", "b", "c"}

print(f"f1 injective: {is_injective(f1)}")
print(f"f1 surjective onto {codomain}: {is_surjective(f1, codomain)}")
print(f"f1 bijective: {is_bijective(f1, codomain)}")
print(f"f2 injective: {is_injective(f2)}")
```

A hash collision means the hash function failed injectivity. A good hash function is "almost" injective by design.

### Step 5: Composition and Inverses

```python
def compose(g, f):
    """(g ∘ f)(x) = g(f(x))"""
    return lambda x: g(f(x))


def inverse(f: dict) -> dict:
    """Inverse exists only when f is injective"""
    if not is_injective(f):
        raise ValueError("non-injective functions have no inverse")
    return {v: k for k, v in f.items()}


f = lambda x: x + 1
g = lambda x: x * 2

h = compose(g, f)  # h(x) = 2(x + 1)
print(f"h(3) = {h(3)}")  # 8

mapping = {1: "a", 2: "b", 3: "c"}
inv = inverse(mapping)
print(f"Inverse: {inv}")
```

Function composition is at the heart of functional programming, and inverses are essential in cryptography and data transformations.

## Notable Points

- A power set has size 2ⁿ — exhaustive subset search is exponential
- Cartesian products are the math behind database tables
- Injectivity and surjectivity drive hash and crypto design
- Composition and inverses are fundamental tools in transformation pipelines

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Confuse sets with lists | Order/duplication assumptions break | Sets are unordered, no duplicates |
| Confuse codomain with range | Surjectivity check fails | Codomain is declared; range is actual outputs |
| Mix partial and total functions | KeyError on missing inputs | Handle `dict` access carefully |
| Reverse composition order | (g ∘ f)(x) ≠ (f ∘ g)(x) | Apply right-to-left |
| Assume an inverse exists | Non-injective ⇒ no inverse | Verify injectivity first |

## How This Is Used in Practice

- Python `set`/`dict` are direct implementations of sets and functions
- SQL JOIN is filtering over a Cartesian product with a predicate
- Hash maps are partial functions from keys to values
- Data migrations are functions between schemas
- ORMs are functions from object domains to relational domains

## How a Senior Engineer Thinks

When choosing a data structure, senior engineers ask "is this a set, a multiset, ordered, or what?" They check whether a function is injective and whether an inverse can be constructed. When designing a data pipeline, they verify that each step is well-defined as a function — same input always produces same output — which is the basis of idempotency.

## Checklist

- [ ] I can explain how sets differ from lists
- [ ] I know the formula |P(A)| = 2ⁿ
- [ ] I can distinguish injective, surjective, and bijective
- [ ] I understand the order of function composition
- [ ] I know when an inverse exists

## Practice Problems

1. Enumerate the power set of {a, b, c} and confirm it has 2³ = 8 elements.

2. Show that f(x) = x² is not injective on ℝ but is injective on [0, ∞).

3. Pick a database table from a project of yours and describe which Cartesian product it is a subset of.

## Wrap-Up and Next Steps

A set is a collection of data; a function is a well-defined correspondence between sets. Together they form the mathematical basis of data structures and databases. Power sets, Cartesian products, composition, and inverses describe every transformation we can perform.

Next, we look at the most important structure built on top of sets — relations and equivalence.

<!-- toc:begin -->
- [What Is Discrete Mathematics?](./01-what-is-discrete-math.md)
- [Propositions and Logic](./02-propositions-and-logic.md)
- **Sets and Functions (current)**
- Relations and Equivalence (upcoming)
- Proof Techniques (upcoming)
- Sequences and Recurrence (upcoming)
- Combinatorics (upcoming)
- Graph Theory Basics (upcoming)
- Trees and Graph Traversal (upcoming)
- Discrete Mathematics and Algorithms (upcoming)
<!-- toc:end -->

## References

- [Discrete Mathematics and Its Applications — Kenneth Rosen, Chapter 2](https://www.mheducation.com/highered/product/discrete-mathematics-its-applications-rosen/M9781259676512.html)
- [Wikipedia — Set Theory](https://en.wikipedia.org/wiki/Set_theory)
- [Wikipedia — Function (mathematics)](https://en.wikipedia.org/wiki/Function_(mathematics))
- [Python Documentation — set, dict](https://docs.python.org/3/tutorial/datastructures.html#sets)

Tags: Computer Science, Discrete Math, Set Theory, Functions, Databases, Data Structures
