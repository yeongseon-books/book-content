---
series: software-design-101
episode: 8
title: "Software Design 101 (8/10): Reducing Change Impact"
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
  - ChangeImpact
  - OpenClosed
  - FeatureFlags
  - Refactoring
seo_description: Design that keeps a single change from shaking the whole system, with the open/closed principle and the expand-contract pattern.
last_reviewed: '2026-05-15'
---

# Software Design 101 (8/10): Reducing Change Impact

A change feels scary when one new branch, one schema update, or one pricing tweak can rattle the whole system. Good design does not stop change. It narrows the blast radius.

This is post 8 in the Software Design 101 series.

In this post, we connect the open/closed principle with expand-contract and feature flags. The aim is to make live changes observable, reversible, and small enough to ship without turning every deployment into a cliff edge.

> The safest evolution path is usually: expand, compare, migrate, and only then clean up.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Reducing Change Impact?
- Which signal should the example or diagram make visible for Reducing Change Impact?
- What failure should be prevented first when Reducing Change Impact reaches a real system?

## Big Picture

![software design 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/software-design-101/08/08-01-concept-at-a-glance.en.png)

*software design 101 chapter 8 flow overview*

This picture places Reducing Change Impact inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## What You Will Learn

- The blast radius of a change
- The Open / Closed Principle (OCP)
- The expand-contract migration pattern
- Decoupling change with feature flags
- Signals that you have a real safety net

## Why It Matters

Most systems are not built well from the start. They are built to change well. The smaller the impact of each change, the more often and more safely they can evolve.

> Code is good when it is good at being changed.

Expand → switch → contract.

## Key Terms

- **Blast radius**: How far a single change can spread.
- **OCP**: Open for extension, closed for modification.
- **Expand-contract**: Run old and new paths together, migrate gradually.
- **Feature flag**: A switch that separates code deploy from feature activation.
- **Strangler fig**: Pattern of wrapping legacy code and replacing it gradually.

## Before / After

**Before**

```python
def price(item, kind):
    if kind == "book": return item.cost * 0.9
    elif kind == "food": return item.cost * 0.95
    elif kind == "lux": return item.cost * 1.1
    # adding a new category = editing this function
```

**After**

```python
class PricingRule:
    def apply(self, item) -> float: ...

PRICING: dict[str, PricingRule] = {}

def price(item, kind):
    return PRICING[kind].apply(item)
```

A new category just registers itself in PRICING.

## Hands-on: Five Steps to Shrink Change Impact

### Step 1 — Measure the blast radius

```bash
# 1_blast.sh
git grep -n "kind ==" | wc -l
# Has one variable's comparison spread across the system?
```

See the current radius first.

### Step 2 — Expand

```python
# 2_expand.py
# Add the new path only; leave the old one intact.
def price_v2(item, kind): ...
```

Old callers see no impact.

### Step 3 — Migrate gradually

```python
# 3_migrate.py
def price(item, kind):
    if FF.use_v2: return price_v2(item, kind)
    return price_v1(item, kind)
```

A feature flag flips users in stages.

### Step 4 — Compare in parallel

```python
# 4_compare.py
def price(item, kind):
    a, b = price_v1(item, kind), price_v2(item, kind)
    if a != b: log.warn("price drift", a, b)
    return a if not FF.use_v2 else b
```

Side-by-side comparison catches regressions.

### Step 5 — Contract

```python
# 5_contract.py
# Once everyone is on v2, remove v1 and the flag.
```

Cleanup is part of the change.

## Quick Verification

For live code, define the comparison before you write the new path. Spell out what the old and new behavior will be compared on.

```text
Comparison target: pricing result
Comparison point: right after request handling
Tolerance: 0
Switch-over rule: zero drift logs and regression suite pass
```

**Expected output:** before enabling the new implementation, you can explain exactly which signals qualify it as safe.

With that in place, the feature flag stops being a mere switch and becomes part of a verification plan.

## Failure Signals and First Checks

| Failure signal | First check |
| --- | --- |
| The new path ships before anyone compares outputs | Check whether side-by-side drift logging existed |
| A feature flag lives for months | Check whether it had an expiration date and cleanup plan |
| Even tiny changes trigger expand-contract | Re-evaluate whether the operational risk justifies the ceremony |

Reducing change impact is not about using more patterns. It is about slicing the risky changes into safe, observable steps.

## What to Notice in This Code

- Adding a new path does not touch the old one.
- The change is expressed as data (config, flags), not branching.
- Regression checks come naturally with the pattern.

## Five Common Mistakes

1. **Editing the existing path in place.** Branching multiplies forever.
2. **Expanding but never contracting.** Dead code and flags pile up.
3. **Keeping a flag forever.** It becomes operational debt.
4. **Switching with no comparison.** Latent regressions ship.
5. **Forcing expand-contract on every change.** Overkill for a one-liner.

## How This Shows Up in Production

Schema migrations, API v1→v2 swaps, rewriting pricing or discount logic, replacing a third-party SaaS — these are the practical tools for evolving live systems safely.

## How a Senior Engineer Thinks

- They estimate blast radius first.
- They prefer data-driven dispatch over more branches.
- They run old and new in parallel to verify.
- They give feature flags an expiration date.
- The last step of any change is always cleanup.

## Checklist

- [ ] Did you estimate the blast radius?
- [ ] Can the new path live next to the old?
- [ ] Is there a way to verify regressions?
- [ ] Do flags have an expiration date?
- [ ] Is post-migration cleanup planned?

## Practice Problems

1. Find the function with the most branches in your code and turn it into a data-driven dispatch.
2. Pick one API and write a plan to expand-contract it to v2.
3. List your live feature flags that have no expiration date and assign them one.

## Wrap-up and Next Steps

Good design makes change unscary. Next up we look at the principles that compress this thinking — a tour of design principles.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Reducing Change Impact?**
  - The article treats Reducing Change Impact as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Reducing Change Impact?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Reducing Change Impact reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Software Design 101 (1/10): What Is Software Design?](./01-what-is-software-design.md)
- [Software Design 101 (2/10): Separation of Concerns](./02-separation-of-concerns.md)
- [Software Design 101 (3/10): Modules and Boundaries](./03-modules-and-boundaries.md)
- [Software Design 101 (4/10): Dependency Direction](./04-dependency-direction.md)
- [Software Design 101 (5/10): Interfaces and Abstraction](./05-interfaces-and-abstraction.md)
- [Software Design 101 (6/10): Layered Architecture](./06-layered-architecture.md)
- [Software Design 101 (7/10): Data Flow Design](./07-data-flow-design.md)
- **Reducing Change Impact (current)**
- Design Principles (upcoming)
- Practicing Design with a Small Project (upcoming)

<!-- toc:end -->

## References

- [Open/Closed Principle (Robert C. Martin)](https://web.archive.org/web/20060822033314/http://www.objectmentor.com/resources/articles/ocp.pdf)
- [ParallelChange (Expand-Contract) — Danilo Sato](https://martinfowler.com/bliki/ParallelChange.html)
- [Feature Toggles — Pete Hodgson](https://martinfowler.com/articles/feature-toggles.html)
- [Strangler Fig Application — Martin Fowler](https://martinfowler.com/bliki/StranglerFigApplication.html)

### Practical Docs

- [logging — Logging facility for Python](https://docs.python.org/3/library/logging.html)
- [enum — Support for enumerations](https://docs.python.org/3/library/enum.html)

Tags: Computer Science, SoftwareDesign, ChangeImpact, OpenClosed, FeatureFlags, Refactoring
