---
series: software-design-101
episode: 3
title: "Software Design 101 (3/10): Modules and Boundaries"
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
  - SoftwareDesign
  - Modules
  - Boundaries
  - Encapsulation
  - PackageDesign
seo_description: Define a module, design small public APIs, hide volatile decisions, and build deep modules with clear boundaries.
last_reviewed: '2026-05-15'
---

# Software Design 101 (3/10): Modules and Boundaries

A code base can have many files and still have weak module boundaries. If callers must understand the internals to use a module safely, the boundary is mostly theater.

This is post 3 in the Software Design 101 series.

In this post, we focus on deep modules, small public surfaces, and information hiding. The practical question is how to keep internal changes inside the module instead of leaking them into every caller.

> A strong boundary lets the caller know less while still getting more useful work done.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Modules and Boundaries?
- Which signal should the example or diagram make visible for Modules and Boundaries?
- What failure should be prevented first when Modules and Boundaries reaches a real system?

## Big Picture

![software design 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/software-design-101/03/03-01-concept-at-a-glance.en.png)

*software design 101 chapter 3 flow overview*

This picture places Modules and Boundaries inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Modules and Boundaries is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## What You Will Learn

- A definition of a module
- Deep vs shallow modules
- Public API design principles
- Encapsulation and information hiding
- Signals from package structure

## Why It Matters

Module boundaries are walls that contain change. Good walls keep changes on one side from leaking to the other.

> A good boundary permits ignorance.

## Concept at a Glance

Small surface, deep interior.

## Key Terms

- **Module**: A unit of code grouped by responsibility.
- **Public API**: The promise a module makes to the outside.
- **Deep module**: Small surface, rich interior.
- **Encapsulation**: Hide internals; communicate only via the interface.
- **Information hiding (Parnas)**: Hide volatile decisions inside the module.

## Before/After

**Before**

```python
# Shallow module: each function exposed
def open_file(p): ...
def read_chunk(f, n): ...
def close_file(f): ...
```

**After**

```python
# Deep module: one surface, full responsibility
def read_file(path) -> bytes: ...
```

Callers do not need to know the internals.

## Hands-on: Five Steps to Good Boundaries

### Step 1 — Shrink the surface

```python
# 1_surface.py
# Ten public symbols expose ten dependencies.
# Export only what truly needs to be exported.
__all__ = ["read_file"]
```

Use `__all__` / `index.ts` to control the surface.

### Step 2 — Make the interior deep

```python
# 2_deep.py
def read_file(path):
    f = _open(path)
    try: return _read_all(f)
    finally: _close(f)
```

Callers can finish in one line.

### Step 3 — Isolate volatile decisions

```python
# 3_hide.py
class CacheBackend:  # outside knows only the interface
    def get(self, k): ...
    def set(self, k, v): ...
```

Redis vs in-memory is an internal decision.

### Step 4 — Limit data exposure

```python
# 4_dto.py
# Do not expose internal models directly; use DTOs.
def public_user(u): return {"id": u.id, "name": u.name}
```

Internal changes do not break the external contract.

### Step 5 — One-way dependencies

```python
# 5_one_way.py
# Domain must not know about infra.
# Infra imports the domain.
```

Direction reinforces the boundary.

## Quick Verification

Pick one module and write down its public symbols separately from its internal helpers. That single inventory usually exposes whether the boundary is doing any real work.

```python
__all__ = [
    "read_file",
    "read_chunk",
    "open_file",
    "close_file",
]
```

**Expected output:** if callers truly need only one or two entry points, the rest are candidates to hide behind the boundary.

Then inspect data exposure as well. More leaks come from returning internal structures directly than from having one extra function.

## Failure Signals and First Checks

| Failure signal | First check |
| --- | --- |
| Internal refactors force caller changes | Check whether the public API exposes too much procedure |
| External code knows your internal dict layout | Check whether internal models escaped without DTOs |
| There are many modules but little abstraction value | Check whether you created only shallow modules |

The best boundaries let callers know little and still get meaningful work done.

## What to Notice in This Code

- The surface is small and intentional.
- Internal changes do not leak.
- Callers know little but accomplish much.

## Five Common Mistakes

1. **Everything public.** No real boundary.
2. **Returning internal data structures.** External code couples to internals.
3. **Too many tiny modules.** Dependency graph explodes.
4. **Only shallow modules.** Abstraction adds no value.
5. **Exposing volatile decisions.** Zero design freedom left.

## How This Shows Up in Production

Great libraries (e.g., `requests`) have a tiny surface and a deep interior. Easy to use, free to evolve.

## How a Senior Engineer Thinks

- Modules should be deep.
- The surface conveys intent.
- Volatile decisions stay inside.
- Protect internal models with DTOs.
- Direction strengthens the boundary.

## Checklist

- [ ] Is the module surface small?
- [ ] Is the interior rich?
- [ ] Are external contracts protected by DTOs?
- [ ] Are volatile decisions hidden inside?
- [ ] Are dependencies one-way?

## Practice Problems

1. Halve the public surface of one of your modules.
2. Wrap an exposed data structure in a DTO.
3. Identify one volatile decision inside a module.

## Wrap-up and Next Steps

Good boundaries contain change. Next we look at another weapon a boundary carries: dependency direction.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Modules and Boundaries?**
  - The article treats Modules and Boundaries as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Modules and Boundaries?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Modules and Boundaries reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Software Design 101 (1/10): What Is Software Design?](./01-what-is-software-design.md)
- [Software Design 101 (2/10): Separation of Concerns](./02-separation-of-concerns.md)
- **Modules and Boundaries (current)**
- Dependency Direction (upcoming)
- Interfaces and Abstraction (upcoming)
- Layered Architecture (upcoming)
- Data Flow Design (upcoming)
- Reducing Change Impact (upcoming)
- Design Principles (upcoming)
- Practicing Design with a Small Project (upcoming)

<!-- toc:end -->

## References

- [Parnas — On the Criteria To Be Used in Decomposing Systems into Modules](https://www.win.tue.nl/~wstomv/edu/2ip30/references/criteria_for_modularization.pdf)
- [A Philosophy of Software Design — Deep Modules](https://web.stanford.edu/~ouster/cgi-bin/aposd.php)
- [Effective Java — API Design](https://www.oracle.com/technical-resources/articles/java/bloch-effective-08-qa.html)
- [Domain-Driven Design — Bounded Context](https://martinfowler.com/bliki/BoundedContext.html)

### Practical Docs

- [The Python Tutorial — Modules](https://docs.python.org/3/tutorial/modules.html)
- [Python Reference — import statement](https://docs.python.org/3/reference/simple_stmts.html#import)

Tags: Computer Science, SoftwareDesign, Modules, Boundaries, Encapsulation, PackageDesign
