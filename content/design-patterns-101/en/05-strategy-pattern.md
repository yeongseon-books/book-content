---
series: design-patterns-101
episode: 5
title: The Strategy Pattern
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - DesignPatterns
  - Strategy
  - Polymorphism
  - Behavioral
  - OCP
seo_description: How the Strategy pattern turns branching algorithms into swappable units and how to keep the Python version lightweight.
last_reviewed: '2026-05-15'
---

# The Strategy Pattern

Code tilts toward conditionals when the same job can be done in several ways. It starts with one `if kind == ...`, then grows as options multiply and policy diverges. After a while, every new case means reopening existing code and retesting the whole branch tree.

This is post 5 in the Design Patterns 101 series.

In this post, we'll look at Strategy as a way to turn algorithms into swappable units that a context can receive from the outside. In Python, that often means using a function before reaching for a class hierarchy.

## Questions this chapter answers

- The problem Strategy solves (branch explosion)
- Strategy and the Open/Closed Principle
- Class Strategy vs function Strategy
- Runtime swapping and testing
- When Strategy is overkill

## Why It Matters

Branching algorithms with if/elif means editing existing code every time a new option appears. Strategy turns those branches into *swappable objects* — open for extension, closed for modification (OCP).

> Strategy is OCP made visible in code.

## Concept at a Glance

![Concept at a Glance](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/05/05-01-concept-at-a-glance.en.png)
*Strategy works when the context stays ignorant of algorithm internals and concrete behavior can swap in at the edge.*

## Key Terms

- **Context**: the object that uses a Strategy.
- **Strategy interface**: the algorithm contract.
- **Concrete Strategy**: an algorithm implementing the contract.
- **Injection point**: where Strategy is supplied (constructor, method arg).
- **Default strategy**: the sensible default behavior.

## Before/After

**Before**

```python
def price(kind, base):
    if kind == "vip":
        return base * 0.7
    elif kind == "member":
        return base * 0.9
    elif kind == "guest":
        return base
    raise ValueError(kind)
```

**After**

```python
class Pricing:
    def apply(self, base): return base

class Vip(Pricing):
    def apply(self, base): return base * 0.7

class Member(Pricing):
    def apply(self, base): return base * 0.9
```

`price` no longer knows the algorithm.

## Hands-on: Five Steps to Practice Strategy

### Step 1 — Define the interface

```python
# 1_iface.py
from typing import Protocol

class ShipCost(Protocol):
    def for_weight(self, kg: float) -> int: ...
```

Python often uses `Protocol` for *structural* interfaces instead of ABCs.

### Step 2 — Concrete strategies

```python
# 2_strategies.py
class StandardShip:
    def for_weight(self, kg): return int(3000 + 500 * kg)

class ExpressShip:
    def for_weight(self, kg): return int(6000 + 800 * kg)
```

Without inheritance, both satisfy the Protocol (duck typing).

### Step 3 — Inject

```python
# 3_inject.py
class Order:
    def __init__(self, ship: ShipCost): self.ship = ship
    def total(self, items, kg):
        return sum(items) + self.ship.for_weight(kg)
```

Constructor injection is the most common form.

### Step 4 — Function Strategy

```python
# 4_func.py
def standard(kg): return int(3000 + 500 * kg)
def express(kg):  return int(6000 + 800 * kg)

class Order2:
    def __init__(self, ship): self.ship = ship
    def total(self, items, kg): return sum(items) + self.ship(kg)

o = Order2(standard)
```

In Python, a function is the most natural Strategy.

### Step 5 — Runtime swap and testing

```python
# 5_runtime.py
order = Order2(standard)
print(order.total([10000], 2))
order.ship = express
print(order.total([10000], 2))
```

In tests, inject deterministic strategies to cut external dependencies.

## What to Notice in This Code

- The Context does not know Strategy *internals*.
- Adding a new algorithm is an *addition*, not a *modification*.
- Tests get easier — inject a fake Strategy and you're done.

## Five Common Mistakes

1. **Strategy for a trivial two-liner.** Over-generalization.
2. **Strategy mutating Context state directly.** Leaky responsibility.
3. **Class explosion.** A function would have been enough.
4. **Missing default Strategy.** Callers must always decide.
5. **Strategies coupling to each other's internals.** Strategy-to-Strategy coupling.

## How This Shows Up in Production

The `key` argument of `sorted`, the `func` of `pandas.apply`, payment-gateway adapter selection, notification-channel selection (email/SMS/Slack) — all Strategy in shape.

## Quick verification

Use these checks to confirm that a Strategy refactor is justified.

- Count how often the algorithm branch changes or receives new variants.
- Replace one concrete strategy with a fake implementation in a test and confirm the context stays untouched.
- Verify whether a plain function already expresses the strategy clearly enough.

**Expected outcome:** new variants become additive, and the context no longer owns the branching logic that selects the algorithm.

## How a Senior Engineer Thinks

- When you feel "another branch coming", suspect Strategy.
- Try a function first; reach for a class only if needed.
- Provide a default to keep simple callers simple.
- Strategy is best when it has *little state*.
- Name by *role*, not behavior — prefer `LoyaltyDiscount` over `Vip`.

## Checklist

- [ ] Does the Context stay ignorant of algorithm internals?
- [ ] Does adding an algorithm only add code?
- [ ] Does the Strategy avoid mutating Context state?
- [ ] Is the default Strategy reasonable?
- [ ] Did you avoid a class where a function would suffice?

## Practice Problems

1. Refactor a payment-method branch (card/transfer/points) into Strategy.
2. Express a sort comparator as a function Strategy.
3. Implement notification-channel selection with Strategy plus a default.

## Wrap-up and Next Steps

Strategy is OCP made visible. The next post zooms in on the structural pattern for compatibility — Adapter.

<!-- toc:begin -->
- [What Are Design Patterns?](./01-what-are-design-patterns.md)
- [Creational Patterns](./02-creational-patterns.md)
- [Structural Patterns](./03-structural-patterns.md)
- [Behavioral Patterns](./04-behavioral-patterns.md)
- **The Strategy Pattern (current)**
- Adapter Pattern (upcoming)
- Observer Pattern (upcoming)
- Factory and Dependency Injection (upcoming)
- Avoiding Pattern Overuse (upcoming)
- Pythonic Patterns (upcoming)
<!-- toc:end -->

## References

### Core references

- [Strategy Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/strategy)
- [Open/Closed Principle (Wikipedia)](https://en.wikipedia.org/wiki/Open%E2%80%93closed_principle)
- [PEP 544 — Protocols](https://peps.python.org/pep-0544/)

### Practical follow-up

- [sorted(key=...) (Python docs)](https://docs.python.org/3/howto/sorting.html)
- [functools — Higher-order functions and operations on callables (Python docs)](https://docs.python.org/3/library/functools.html)

Tags: Computer Science, DesignPatterns, Strategy, Polymorphism, Behavioral, OCP
