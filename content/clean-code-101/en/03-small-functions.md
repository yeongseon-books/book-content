---
series: clean-code-101
episode: 3
title: Small Functions
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
  - CleanCode
  - Functions
  - SRP
  - Refactoring
  - Readability
seo_description: Why small functions help, doing one thing only, the extract function procedure, and how to remove side effects.
last_reviewed: '2026-05-04'
---

# Small Functions

> Clean Code 101 series (3/10)

<!-- a-grade-intro:begin -->

**Core question**: How small is small enough?

> Small enough that "does one thing" is visible. The name carries that one thing.

This is post 3 in the Clean Code 101 series.

<!-- a-grade-intro:end -->

## What You Will Learn

- Four effects of small functions
- The Extract Function procedure
- Patterns that remove side effects
- Command-Query Separation
- Parameter objects to simplify signatures

## Why It Matters

A small function explains itself by name. A large function asks for comments, and comments turn into lies.

> When functions shrink, names do the work.

## Concept at a Glance

```mermaid
flowchart LR
    B["Giant function"] --> E["Extract"]
    E --> S["Does one thing"]
    S --> N["Good name"]
    N --> R["Reuse and test"]
```

Extraction enables names; names enable reuse.

## Key Terms

- **SRP (Single Responsibility)**: One reason to change.
- **Extract Function**: Pull a block out into a function.
- **Command-Query Separation**: Functions either do or answer, not both.
- **Pure function**: Same input -> same output, no side effects.
- **Parameter Object**: Group arguments into an object.

## Before/After

**Before**

```python
def checkout(cart, user, addr, coupon):
    # 60 lines: validate + price + tax + ship + log + email + save
    ...
```

**After**

```python
def checkout(cart, user, addr, coupon):
    items = validate_cart(cart, user)
    total = price_with_tax(items, addr)
    order = save_order(user, items, total, coupon)
    notify_user(user, order)
    return order
```

The body becomes a table of contents.

## Hands-on: Extract Safely

### Step 1 — Partial extraction

```python
# 1_extract.py
def total(items):
    s = 0
    for it in items:
        s += it.price * it.qty
    return s
```

Loops are good extraction candidates.

### Step 2 — Intent name

```python
# 2_intent.py
def line_total(item): return item.price * item.qty
def total(items): return sum(line_total(it) for it in items)
```

The name reduces the code.

### Step 3 — Command/Query split

```python
# 3_cqs.py
class Account:
    def withdraw(self, amount):  # command
        self.balance -= amount
    def is_overdrawn(self):      # query
        return self.balance < 0
```

Queries must not mutate.

### Step 4 — Parameter object

```python
# 4_param_obj.py
from dataclasses import dataclass
@dataclass
class Range: lo: int; hi: int
def in_range(value, r: Range): return r.lo <= value <= r.hi
```

More than three args is a candidate for an object.

### Step 5 — Make it pure

```python
# 5_pure.py
def discount(price: int, rate: float) -> int:
    return int(price * (1 - rate))
```

Pure functions are one-line tests.

## What to Notice in This Code

- The body reads like a table of contents.
- Names replace comments.
- Command/Query split reduces debugging time.

## Five Common Mistakes

1. **Cleaning a giant function with variables only.** No new names appear.
2. **Argument explosion after extraction.** Group into objects.
3. **Queries that mutate.** A leading source of bugs.
4. **Extracting without tests.** Regression risk.
5. **Over-shredding.** A hundred one-line functions kills readability.

## How This Shows Up in Production

Strong teams gate function length, arg count, and cyclomatic complexity via lint. Large functions get auto-flagged with extraction suggestions on PRs.

## How a Senior Engineer Thinks

- Make the body read like a table of contents.
- Names replace comments.
- Queries never mutate.
- More than three args is a smell.
- Pure functions are friends of tests.

## Checklist

- [ ] Does the function do exactly one thing?
- [ ] Does the body read like a table of contents?
- [ ] Args ≤ 3?
- [ ] Are queries side-effect free?
- [ ] Are there tests around the extraction?

## Practice Problems

1. Rewrite one function so its body reads as a table of contents.
2. Group a 4+ arg function into an object.
3. Fix one CQS violation.

## Wrap-up and Next Steps

Small functions enable names and tests. Next, the chief reason for big functions — conditionals.

<!-- toc:begin -->
- [What Is Clean Code?](./01-what-is-clean-code.md)
- [Naming](./02-naming.md)
- **Small Functions (current)**
- Simplifying Conditionals (upcoming)
- Removing Duplication (upcoming)
- Error Handling (upcoming)
- Comments and Documentation (upcoming)
- Testable Code (upcoming)
- Refactoring Basics (upcoming)
- Good Code Review Standards (upcoming)
<!-- toc:end -->

## References

- [Clean Code (Ch. 3 Functions)](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)
- [Refactoring — Extract Function](https://refactoring.com/catalog/extractFunction.html)
- [Martin Fowler — Command Query Separation](https://martinfowler.com/bliki/CommandQuerySeparation.html)
- [Refactoring — Introduce Parameter Object](https://refactoring.com/catalog/introduceParameterObject.html)

Tags: Computer Science, CleanCode, Functions, SRP, Refactoring, Readability
