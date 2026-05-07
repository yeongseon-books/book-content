---
series: software-design-101
episode: 3
title: Modules and Boundaries
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
  - SoftwareDesign
  - Modules
  - Boundaries
  - Encapsulation
  - PackageDesign
seo_description: Define a module, design small public APIs, hide volatile decisions, and build deep modules with clear boundaries.
last_reviewed: '2026-05-04'
---

# Modules and Boundaries

> Software Design 101 series (3/10)

<!-- a-grade-intro:begin -->

**Core question**: What makes a module boundary good?

> A small surface area and the absence of leaks from internal changes to external callers.

<!-- a-grade-intro:end -->

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

```mermaid
flowchart LR
    P["Public API"] -. small .-> M["Module"]
    M -. deep .-> I["Internal"]
    I --> R["Rich behavior"]
```

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

<!-- toc:begin -->
- [What Is Software Design?](./01-what-is-software-design.md)
- [Separation of Concerns](./02-separation-of-concerns.md)
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

Tags: Computer Science, SoftwareDesign, Modules, Boundaries, Encapsulation, PackageDesign
