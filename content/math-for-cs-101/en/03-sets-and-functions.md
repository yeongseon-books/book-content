---
series: math-for-cs-101
episode: 3
title: "Math for CS 101 (3/10): Sets and Functions"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Math
  - Sets
  - Functions
  - Foundations
  - Beginner
seo_description: A beginner-friendly guide to sets and functions covering union, intersection, difference, injective, surjective, bijective, and composition
last_reviewed: '2026-05-04'
---

# Math for CS 101 (3/10): Sets and Functions

When you learn data structures, you usually start with lists, dictionaries, mapping, and filtering. Step back a little, though, and two simpler ideas sit underneath all of them: sets tell you what belongs, and functions tell you how one value becomes another.

In real systems these two ideas rarely stay separate. Deduplication, permission checks, feature preprocessing, key mapping, and serialization pipelines all become easier to reason about once you can describe them as set boundaries plus transformation rules.

This is the 3rd post in the Math for CS 101 series.

Here we use sets and functions as the foundation for data modeling and transformation, not just as definitions to memorize.


![math for cs 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/math-for-cs-101/03/03-01-concept-at-a-glance.en.png)
*math for cs 101 chapter 3 flow overview*
> Sets and functions are not abstract concepts; they are the mathematical foundations of type systems and data transformations in code.

## Questions to Keep in Mind

- Why are sets such a useful foundation for data structures and validation?
- How do union, intersection, and difference show up in ordinary code?
- What separates a function from a more general relation?

## Why It Matters

Python's `set`, `dict`, `map`, and `filter` already carry the mental model of sets and functions. Deduplication is a set operation. Data transformation is often a chain of functions. Permission checks usually become set membership or set intersection once you make the model explicit.

That clarity pays off when business rules get complicated. If you blur together the data boundary and the transformation rule, exceptions spread everywhere. When you separate them, you can explain what is allowed and how it is transformed as two different decisions.

Sets define *membership* and *boundaries*; functions map *inputs to outputs* systematically. Together they form the vocabulary of types and data transformations.

## Before/After

**Before**: Think of functions as "just code that does something."

**After**: See functions as *precise mappings* with defined domains and codomains.

## Key Terms

- **set**: a collection of *distinct* elements.
- **union**: all elements.
- **intersection**: *shared* elements.
- **function**: one *output* per *input*.
- **bijection**: *injective* and *surjective*.

## Before/After

**Before**: handle everything with *lists*.

**After**: handle it with *sets* and *functions*, more clearly.

## Hands-on: Five Steps with Sets and Functions

### Step 1 — Sets

```python
A, B = {1, 2, 3}, {2, 3, 4}
```

The core property of a set is membership, not order. Duplicates collapse to a single element—this is the first point where sets differ from lists. Whenever your data model treats duplicates as meaningless, set thinking is the more natural fit.

### Step 2 — Union, intersection, difference

```python
def ops(A, B):
    return A | B, A & B, A - B
```

A single operator expresses union, intersection, or difference. The code looks simple, yet it handles inclusion relationships in extremely compressed grammar. Permission intersections, allow-list minus block-list—production scenarios follow the same structure.

### Step 3 — A function

```python
def square(x):
    return x * x
```

A function maps each input to exactly one output. The guarantee that the same input always yields the same result directly connects to testability, cacheability, and reasoning ability.

### Step 4 — Injective check

```python
def is_injective(f, domain):
    return len({f(x) for x in domain}) == len(list(domain))
```

Injectivity means distinct inputs always produce distinct outputs. If two different inputs can map to the same output, you lose the ability to reverse the mapping—a concern that shows up in hashing, encoding, and database key design.

### Step 5 — Composition

```python
def compose(f, g):
    return lambda x: f(g(x))
```

Composition chains two functions so the output of one feeds into the other. This is the algebraic version of piping—same idea as Unix pipes or middleware stacks, but with a precise rule about application order.

## What to Notice in This Code

- The *operations* are *one operator* each.
- *Injective* is a *length* comparison.
- *Composition* is a *lambda*.

## Using Python Set Operations as a Modeling Language

Set operations are not just syntax convenience—they define policies and data boundaries. For example, in access control you can check whether a user's scope set is a superset of the required scope set.

```python
def can_access(user_scopes: set[str], required_scopes: set[str]) -> bool:
    return required_scopes.issubset(user_scopes)

user = {'read:post', 'read:comment', 'write:comment'}
required = {'read:post'}
```

The advantage: even as conditions grow, the core meaning stays intact. A list-based comparison introduces ordering and duplication issues. A set-based approach keeps the requirement expressed as a mathematical condition.

## Operation Selection Table

| Situation | Set Operation | Code | Checkpoint |
| --- | --- | --- | --- |
| Merging allow rules | Union | `A \| B` | Deduplicate meaning |
| Simultaneous-satisfaction rules | Intersection | `A & B` | Handle empty intersection |
| Exclusion rules | Difference | `A - B` | Block-list freshness |
| Exact-match drift detection | Symmetric difference | `A ^ B` | Missing/extra items |

Symmetric difference (`A ^ B`) is particularly useful in operations for detecting "policy drift"—it immediately reveals where the expected state and the actual state diverge.

## Designing Data Pipelines with Function Composition

Composing small transformation functions produces testable pipelines.

```python
def trim(s: str) -> str:
    return s.strip()

def lower(s: str) -> str:
    return s.lower()

def remove_space(s: str) -> str:
    return s.replace(' ', '')

def compose(*funcs):
    def wrapped(x):
        for f in funcs:
            x = f(x)
        return x
    return wrapped

normalize = compose(trim, lower, remove_space)
```

Composition separates each step's responsibility, making failure root-cause analysis straightforward. You can maintain per-step unit tests while adding an end-to-end pipeline test for regression safety.

## Understanding Injective, Surjective, and Bijective Through Practical Mappings

- **Injective**: distinct inputs always produce distinct outputs. Example: unique user ID generators.
- **Surjective**: every value in the codomain is reached by at least one input. Example: a status-code mapping that covers all possible statuses.
- **Bijective**: both injective and surjective—reversible mapping. Example: a 1:1 table between abbreviation codes and full text.

```python
def is_injective_map(mapping: dict[str, str]) -> bool:
    return len(set(mapping.values())) == len(mapping)
```

If you miss the injectivity requirement during mapping design, collisions make reverse lookup impossible. This problem appears frequently in log key standardization, cache key generation, and URL slug creation.

## Why Separate Functions from Relations

A relation allows one input to map to multiple outputs; a function does not. This distinction directly affects API contracts. "One default shipping address per user" is a function model; "multiple bookmarks per user" is a relation model. Confusing the two at design time leads to unnecessarily complex schemas and interfaces.

## Boundary Case Checklist

1. Does the operation produce expected results on empty-set input?
2. Is information loss acceptable when converting a duplicate-containing source to a set?
3. Does swapping the order of composed functions change the meaning?
4. Does the codomain definition match between documentation and implementation?

Sets and functions are foundational concepts, but they keep getting reused all the way up to advanced design because they clarify boundaries and contracts.

## Lowering Set/Function Models into API Contracts

When you use set and function perspectives directly in API design docs, misunderstandings between implementation teams decrease. For example, `GET /users/{id}` is an `id -> user` function model, while `GET /users?team=x` is a subset query on the team set. Making this explicit naturally separates responsibilities for empty results, duplicates, and ordering across layers.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class User:
    user_id: str
    team: str

def team_members(users: set[User], team: str) -> set[User]:
    return {u for u in users if u.team == team}
```

The key is writing what mathematical contract an API guarantees before describing how it enumerates values.

## Resolving Permissions with Set Operations

Set operations express data-boundary validation directly. Given an allowed set, a requested set, and a blocked set, computing the final approved set becomes a single expression.

```python
def resolve_permissions(allowed: set[str], requested: set[str], blocked: set[str]) -> set[str]:
    return (allowed & requested) - blocked

allowed = {"read", "write", "delete", "audit"}
requested = {"read", "delete"}
blocked = {"delete"}
print(resolve_permissions(allowed, requested, blocked))  # {'read'}
```

The advantage: policy intent is visible at the operator level. A list-based filter chain shows procedure but can obscure the policy boundary.

## Typed Function Composition

Function composition is the core pattern for assembling small transformations into a larger pipeline.

```python
from typing import Callable

def compose(f: Callable, g: Callable):
    return lambda x: f(g(x))

def strip_text(x: str) -> str:
    return x.strip()

def normalize_space(x: str) -> str:
    return " ".join(x.split())

def to_lower(x: str) -> str:
    return x.lower()

pipeline = compose(to_lower, compose(normalize_space, strip_text))
print(pipeline("  Hello   CS Math  "))
```

The habit of reading composition order precisely matters for bug tracking. Especially in serialization/deserialization and validation/normalization chains, swapping one step changes the entire meaning.

## Injective and Surjective Comparison

| Property | Definition | Development Context | Watch Out |
| --- | --- | --- | --- |
| Injective | Distinct inputs map to distinct outputs | ID mapping, key generation | Collision means injectivity failure |
| Surjective | Every codomain element is hit at least once | Classification labels covering all cases | Data bias can break surjectivity |
| Bijective | Injective + surjective | Reversible transforms, lossless encoding | Incorrect codomain definition causes misjudgment |

### Checking Injectivity and Surjectivity in Code

```python
def is_injective(mapping: dict) -> bool:
    return len(set(mapping.values())) == len(mapping)

def is_surjective(mapping: dict, codomain: set) -> bool:
    return set(mapping.values()) == codomain

m = {"a": 1, "b": 2, "c": 3}
print(is_injective(m), is_surjective(m, {1, 2, 3}))
```

In practice, if you do not explicitly state the codomain, a surjectivity judgment is meaningless. Making the codomain explicit in function contracts is a necessary habit.

## Set Operation Symbol Reference

| Symbol | Name | Python | Meaning |
| --- | --- | --- | --- |
| A ∪ B | Union | `a \| b` | Elements in either set |
| A ∩ B | Intersection | `a & b` | Elements in both sets |
| A ∖ B | Difference | `a - b` | Elements in A but not B |
| A ⊕ B | Symmetric difference | `a ^ b` | Elements in exactly one set |
| A ⊆ B | Subset | `a <= b` | All elements of A are in B |
| A ⊂ B | Proper subset | `a < b` | A ⊆ B and A ≠ B |
| x ∈ A | Membership | `x in a` | x belongs to A |
| \|A\| | Cardinality | `len(a)` | Number of elements in A |
| ∅ | Empty set | `set()` | A set with no elements |
| P(A) | Power set | See code below | Set of all subsets of A |

## Power Set and Cardinality

The power set P(A) is the set of all subsets of A. If |A| = n, then |P(A)| = 2ⁿ. This concept connects directly to combinatorics and appears whenever you need to calculate possible configuration combinations in a system.

```python
from itertools import combinations

def power_set(s: set) -> list:
    items = list(s)
    result = []
    for r in range(len(items) + 1):
        for combo in combinations(items, r):
            result.append(set(combo))
    return result

features = {"cache", "retry", "logging"}
all_configs = power_set(features)
print(f"feature flags: {len(features)} -> configurations: {len(all_configs)}")  # 3 -> 8
```

With 3 feature flags you get 8 combinations; with 10 you get 1,024. Understanding power-set cardinality growth lets you quantitatively explain how feature-flag explosion increases testing cost.

## Building a Data Validation Pipeline with Set Operations

Set operations show their greatest value in data validation scenarios.

```python
def validate_schema(required: set, optional: set, actual: set) -> dict:
    missing = required - actual
    unexpected = actual - (required | optional)
    recognized = actual & (required | optional)
    return {
        "valid": len(missing) == 0 and len(unexpected) == 0,
        "missing": missing,
        "unexpected": unexpected,
        "recognized": recognized,
    }

required_fields = {"id", "name", "email"}
optional_fields = {"phone", "address"}
actual_fields = {"id", "name", "email", "nickname"}

result = validate_schema(required_fields, optional_fields, actual_fields)
print(result)
# {'valid': False, 'missing': set(), 'unexpected': {'nickname'}, 'recognized': {'id', 'name', 'email'}}
```

This pattern is reusable across API request validation, CSV column checking, and environment variable verification. Compared to list-based validation, the intent is clearer and performance benefits from O(1) lookups.

## Five Common Mistakes

1. **Confusing *list* and *set*.**
2. **Confusing *function* with *relation*.**
3. **Mixing up *injective* and *surjective*.**
4. **Misordering in *composition*.**
5. **Missing the *empty set* case.**

## How This Shows Up in Production

*Permission checks* are *set intersections*, *data mapping* is *function composition*, and *deduplication* is a *set conversion*.

## How a Senior Engineer Thinks

- *Sets* are *clear*.
- *Functions* are *deterministic*.
- *Bijections* are *invertible*.
- *Composition* is a *pipe*.
- The *empty set* is the *base case*.

## Checklist

- [ ] Translate *operations* to *code*.
- [ ] Specify *domain* and *codomain*.
- [ ] Decide *injective/surjective*.
- [ ] Check *composability*.

## Practice Problems

1. Define *injective* in one line.
2. Define *surjective* in one line.
3. Define *composition* in one line.

## Wrap-up and Next Steps

Sets clarify the shape of data, and functions clarify the shape of change. Together they provide a compact vocabulary for boundary checks, deterministic transformations, and reversible mappings.

Next, we broaden that structural view into graphs, where relationships between objects become the main story.

## Answering the Opening Questions

- **Why are sets called the foundation of data structures and data models?**
  - Sets directly express boundaries—what's allowed and what's excluded—making them the floor of data models. The `can_access(user_scopes, required_scopes)`, `validate_schema(required, optional, actual)`, and `power_set(features)` examples show that permissions, schemas, and configuration combinations can all be described in the language of membership.
- **How do union, intersection, and difference look in code?**
  - The article mapped them directly: `A | B`, `A & B`, `A - B`. In `resolve_permissions(allowed, requested, blocked)`, the final approved set was `(allowed & requested) - blocked`. In `validate_schema`, missing fields were `required - actual` and unexpected fields were `actual - (required | optional)`—set operations as validation rules.
- **What distinguishes functions from relations?**
  - A function maps each input to exactly one output deterministically, so it supports pipelines like `compose(trim, lower, remove_space)`. A relation—where one input yields multiple results, like a user having many bookmarks or `team_members(users, team)`—requires different contracts and test strategies.
<!-- toc:begin -->
## In this series

- [Math for CS 101 (1/10): Why Math for CS](./01-why-math-for-cs.md)
- [Math for CS 101 (2/10): Logic and Proofs](./02-logic-and-proofs.md)
- **Sets and Functions (current)**
- Graphs (upcoming)
- Combinatorics (upcoming)
- Probability (upcoming)
- Linear Algebra (upcoming)
- Calculus (upcoming)
- Information Theory (upcoming)
- Algorithms and Math (upcoming)

<!-- toc:end -->

## References

- [Sets - Wolfram MathWorld](https://mathworld.wolfram.com/Set.html)
- [Functions - Khan Academy](https://www.khanacademy.org/math/algebra/x2f8bb11595b61c86:functions)
- [Discrete Math - Rosen](https://en.wikipedia.org/wiki/Discrete_Mathematics_and_Its_Applications)
- [Python Set Operations](https://docs.python.org/3/tutorial/datastructures.html#sets)
- [SymPy GitHub repository](https://github.com/sympy/sympy)

Tags: Math, Sets, Functions, Foundations, Beginner
