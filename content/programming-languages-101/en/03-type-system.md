---
series: programming-languages-101
episode: 3
title: "Programming Languages 101 (3/10): Type Systems"
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
  - Programming Languages
  - TypeSystem
  - Static
  - Dynamic
  - Inference
seo_description: A type system is not just data tagging. It is a proof tool that rejects nonsense programs before they run. Walk through the core ideas and tradeoffs.
last_reviewed: '2026-05-15'
---

# Programming Languages 101 (3/10): Type Systems

Dynamic languages run perfectly well for a long time. Then the project grows, the team grows, and people start adding type hints, CI checks, and tighter interfaces again. That repeated move is a clue: types solve a practical problem that only becomes more obvious at scale.

This is post 3 in the Programming Languages 101 series.

In this post, we will treat a type system not as simple data labeling but as a way to reject nonsensical combinations before they run. We will compare static and dynamic typing, strong and weak typing, and then look at why inference and generics raise productivity instead of just adding ceremony.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Type Systems?
- Which signal should the example or diagram make visible for Type Systems?
- What failure should be prevented first when Type Systems reaches a real system?

## Big Picture

![programming languages 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/programming-languages-101/03/03-01-concept-at-a-glance.en.png)

*programming languages 101 chapter 3 flow overview*

This picture places Type Systems inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Type Systems is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Questions this article answers

- What role does a type actually play?
- What do static types and dynamic types check, and when do they check it?
- Why are strong vs weak typing and static vs dynamic typing different axes?
- Why do type inference and generics improve productivity?

## Why It Matters

Most modern languages have some kind of type system, and even Python, JavaScript, and Ruby grew gradual type systems (type hints, TypeScript). To use autocompletion, refactoring tools, and build-stage error messages well, you need to understand types. The later episodes — scope and closures — also operate on top of types.

> A type narrows down, in advance, which inputs are even legal.

## Concept at a Glance

The type checker rules out impossible calls before runtime. Simultaneously, it gives the IDE the basis for autocompletion and safe refactoring.

## Key Terms

- **Static typing**: Types checked at compile / pre-run time.
- **Dynamic typing**: Types checked while the program runs.
- **Strong typing**: Implicit conversions are rare.
- **Weak typing**: Implicit conversions are common (think JavaScript's `+`).
- **Type inference**: The compiler figures out the type without an annotation.
- **Generics**: Parameterizing code so it works for many types safely.

## Before/After

**Before — a function with no types**

```python
def discount(price, rate):
    return price - price * rate

# Someone calls it like this
discount("1000", 0.1)  # TypeError at runtime
```

The signature alone does not tell callers what to pass, and bugs only show at runtime.

**After — annotated**

```python
def discount(price: int, rate: float) -> float:
    return price - price * rate

discount("1000", 0.1)  # mypy rejects this at the call site
```

A static checker like `mypy` catches it before runtime, and the signature itself becomes a small piece of documentation.

## Hands-on: Introduce Types Step by Step

### Step 1 — Add type hints

```python
# 1_hints.py
def to_kebab(s: str) -> str:
    return s.strip().lower().replace(" ", "-")

print(to_kebab("Hello World"))
```

The behavior is the same with or without `-> str`, but callers now have a contract.

### Step 2 — Run mypy

```bash
pip install mypy
mypy 1_hints.py    # Success: no issues
```

A new habit: check at build time.

### Step 3 — Generic function

```python
# 3_generic.py
from typing import TypeVar, Iterable

T = TypeVar("T")

def first(xs: Iterable[T]) -> T:
    for x in xs:
        return x
    raise ValueError("empty")

reveal_type(first([1, 2, 3]))   # Revealed type is "int"
reveal_type(first(["a", "b"]))  # Revealed type is "str"
```

The same function preserves an exact return type for many input types. Tooling gets stronger.

### Step 4 — Union types and narrowing

```python
# 4_union.py
def length(x: str | list) -> int:
    if isinstance(x, str):
        return len(x)
    return sum(len(item) for item in x)
```

After the `isinstance` check, the type checker narrows the type inside each branch.

### Step 5 — A real bug found by adding types

```python
# 5_real_bug.py
def total_price(items: list[dict]) -> int:
    return sum(item["price"] for item in items)  # mypy points out the dict value type is unclear
```

Trying to write the type accurately tends to expose ambiguity in the data model itself. That ambiguity is usually where the real bug lives.

### Step 6 — Validate at the boundary, then narrow to a precise type

```python
# 6_boundary.py
from typing import TypedDict

class LineItem(TypedDict):
    price: int
    quantity: int

def parse_line_item(raw: dict[str, object]) -> LineItem:
    price = raw.get("price")
    quantity = raw.get("quantity")
    if not isinstance(price, int) or not isinstance(quantity, int):
        raise ValueError("price and quantity must be integers")
    return {"price": price, "quantity": quantity}

def subtotal(item: LineItem) -> int:
    return item["price"] * item["quantity"]

payload = {"price": 1200, "quantity": 3}
item = parse_line_item(payload)
print(subtotal(item))  # 3600
```

This is the practical boundary pattern. Runtime validation narrows a JSON-like payload first, then the rest of the program benefits from precise types, safer refactoring, and better autocomplete.

## What to Notice in This Code

- A type is checking, documentation, and tool input all at once.
- A static check does not catch every bug, but it catches the cheapest, most common ones cheapest.
- Generics are the safe form of "write once, use for many types."
- Union types plus `isinstance` narrowing carry your dynamic-language intuition straight into the static checker.

## Five Common Mistakes

1. **Sprinkling `Any` everywhere.** The checker stays quiet, but you lost the safety.
2. **Adding types everywhere at once.** Start at boundaries — public functions, module interfaces — and grow inward.
3. **Confusing types with runtime validation.** `mypy` does not check the shape of external inputs at runtime. Validate those separately.
4. **Chasing overly precise types.** A simple type that catches 90% of cases tends to be more valuable than a baroque one that catches 100%.
5. **Treating dynamic vs static as a status battle.** It is a tradeoff that depends on team size and domain.

## How This Shows Up in Production

Large Python codebases run mypy or pyright in CI and require types on public functions. The JavaScript world has settled on TypeScript as the de facto default. Types at library boundaries are the first documentation users see and the basis of autocompletion.

Types are a refactoring safety net. When changing the order of a function's arguments lights up every call site at compile time, you can do that change confidently.

## How a Senior Engineer Thinks

- Adds types to module boundaries and public APIs first; helpers later.
- When they spot an `Any`, they look for one step of narrowing.
- Always validates external input separately (types ≠ runtime validation).
- Treats static vs dynamic as a tradeoff driven by team size and change frequency, not faith.
- Sees IDE support (autocomplete, refactoring) as the type system's main payoff, not a side benefit.

## Checklist

- [ ] Can you tell static vs dynamic and strong vs weak typing apart in one line?
- [ ] Do you know where to add types first when adopting them gradually?
- [ ] Do you have a strategy for narrowing an `Any`?
- [ ] Do you know the difference between types and runtime validation?
- [ ] Can you explain why generics are stronger than ad-hoc parameterization?

## Practice Problems

1. Take the `total_price` example and introduce a `TypedDict` describing the exact shape of `item`.
2. Pick a function in your favorite dynamic language and write down its input and output types in prose. If anything is ambiguous, describe what that ambiguity actually means.
3. Recall a real bug that was only caught after types were added. Explain why the dynamic check found it late.

## Wrap-up and Next Steps

A type system gives you safety, documentation, and tooling at the same time. Not every language needs every level of typing, but for large systems with many boundaries it is almost always a win. Next we look at another universal pillar — scope and binding.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Type Systems?**
  - The article treats Type Systems as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Type Systems?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Type Systems reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Programming Languages 101 (1/10): What Is a Programming Language?](./01-what-is-a-programming-language.md)
- [Programming Languages 101 (2/10): Syntax and Semantics](./02-syntax-and-semantics.md)
- **Type Systems (current)**
- Scope and Binding (upcoming)
- Functions and Closures (upcoming)
- Objects and Prototypes (upcoming)
- Memory Management (upcoming)
- Interpreters and Compilers (upcoming)
- Static vs Dynamic Languages (upcoming)
- What Makes a Good Language Design? (upcoming)

<!-- toc:end -->

## References

- [Types and Programming Languages (Pierce)](https://www.cis.upenn.edu/~bcpierce/tapl/)
- [Python typing documentation](https://docs.python.org/3/library/typing.html)
- [mypy documentation](https://mypy.readthedocs.io/)
- [PEP 589 — TypedDict](https://peps.python.org/pep-0589/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/)
- [PEP 484 — Type Hints](https://peps.python.org/pep-0484/)

Tags: Computer Science, Programming Languages, TypeSystem, Static, Dynamic, Inference
