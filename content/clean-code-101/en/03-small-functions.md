---
series: clean-code-101
episode: 3
title: "Clean Code 101 (3/10): Small Functions"
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
  - CleanCode
  - Functions
  - SRP
  - Refactoring
  - Readability
seo_description: Why small functions help, doing one thing only, the extract function procedure, and how to remove side effects.
last_reviewed: '2026-05-15'
---

# Clean Code 101 (3/10): Small Functions

Large functions rarely fail because of one dramatic bug. They fail because reading them feels like switching tasks every three lines.

This is post 3 in the Clean Code 101 series.

Here we will define what “small enough” really means, walk through a safe extraction sequence, and show how side effects and argument growth tell you when to stop.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Small Functions?
- Which signal should the example or diagram make visible for Small Functions?
- What failure should be prevented first when Small Functions reaches a real system?

## Big Picture

![clean code 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/clean-code-101/03/03-01-concept-at-a-glance.en.png)

*clean code 101 chapter 3 flow overview*

This picture places Small Functions inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Small Functions is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Questions this article answers

- What do you gain when functions stay small?
- In what order should you apply Extract Function to keep the refactor safe?
- What common patterns help reduce side effects?
- Why does Command-Query Separation cut debugging time?
- When is it worth introducing a parameter object?

> As functions get smaller, names do more of the work than comments, and tests become much easier to write.

## Why It Matters

A small function explains itself by name. A large function asks for comments, and comments turn into lies.

> When functions shrink, names do the work.

## Concept at a Glance

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

## How to Verify This in a Real Codebase

```bash
radon cc app/ -a -s
python -m pytest -q tests/test_checkout.py
```

**Expected output**

- You can compare complexity before and after extraction while keeping tests stable.
- The function body should read like a table of contents.

## Failure Modes to Watch

- Argument count explodes after extraction.
- Query-style functions still mutate hidden state.

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

## Answering the Opening Questions

- **What boundary should you inspect first when applying Small Functions?**
  - The article treats Small Functions as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Small Functions?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Small Functions reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Clean Code 101 (1/10): What Is Clean Code?](./01-what-is-clean-code.md)
- [Clean Code 101 (2/10): Naming](./02-naming.md)
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
- [Python dataclasses documentation](https://docs.python.org/3/library/dataclasses.html)
Tags: Computer Science, CleanCode, Functions, SRP, Refactoring, Readability
