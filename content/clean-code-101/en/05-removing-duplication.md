---
series: clean-code-101
episode: 5
title: "Clean Code 101 (5/10): Removing Duplication"
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
  - DRY
  - Duplication
  - Refactoring
  - Abstraction
seo_description: Apply DRY, extract function, parameterize, and table-driven techniques to remove duplication without creating wrong abstractions.
last_reviewed: '2026-05-15'
---

# Clean Code 101 (5/10): Removing Duplication

Duplication is expensive, but wrong abstractions are expensive in a different way. The hard part is not spotting repetition. It is proving that the same knowledge really changes together.

This is the 5th post in the Clean Code 101 series.

Here we will separate shared change reasons from accidental similarity, then verify when extraction, parameterization, or a data table actually reduces future maintenance cost.


![clean code 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/clean-code-101/05/05-01-concept-at-a-glance.en.png)
*clean code 101 chapter 5 flow overview*
> Extract only duplication that changes for the same reason.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Removing Duplication?
- Which signal should the example or diagram make visible for Removing Duplication?
- What failure should be prevented first when Removing Duplication reaches a real system?

## Questions this article answers

- What does DRY actually mean?
- How do you tell accidental similarity from essential duplication?
- In what order should you apply extraction and parameterization?
- How can you move data duplication into tables?
- Why does premature abstraction create a more expensive form of coupling?

> Once the same knowledge starts living in two places, it eventually drifts apart.

## Why It Matters

Duplication multiplies bugs. Fix one site and you forget the other.

> When the same knowledge lives in two places, they will diverge.

Extract only when the change reason is shared.

## Key Terms

- **DRY**: Don't Repeat Yourself. Single source of knowledge.
- **Coincidental duplication**: Code that just happens to look alike.
- **Extract Function/Class**: Lift the shared part into a function or class.
- **Parameterize**: Express the differing part as an argument.
- **Premature abstraction**: Coupling created by extracting too early.

## Before/After

**Before**

```python
def email_admin(msg):
    print(f"[admin] {msg}")
def email_user(msg):
    print(f"[user] {msg}")
def email_guest(msg):
    print(f"[guest] {msg}")
```

**After**

```python
def email(role, msg):
    print(f"[{role}] {msg}")
```

The differing part (role) becomes an argument.

## Hands-on: Removing Duplication Safely

### Step 1 — Wait for the third occurrence

```python
# 1_rule_of_three.py
# Extract only after the same pattern shows up three times.
def calc_a(x): return x * 1.1
def calc_b(x): return x * 1.2
# When the third arrives, decide whether to unify.
```

Premature extraction creates expensive coupling.

### Step 2 — Extract function

```python
# 2_extract.py
def with_tax(price, rate): return int(price * (1 + rate))
def krw(price): return with_tax(price, 0.1)
def jpy(price): return with_tax(price, 0.08)
```

Only the rate (the differing part) is an argument.

### Step 3 — Parameterize

```python
# 3_param.py
def greet(name, lang="en"):
    msgs = {"en": "Hello", "ko": "안녕하세요"}
    return f"{msgs[lang]}, {name}"
```

Lookup replaces branching.

### Step 4 — Remove data duplication

```python
# 4_data.py
PLANS = {
    "free": {"price": 0,  "limit": 100},
    "pro":  {"price": 10, "limit": 1000},
    "team": {"price": 30, "limit": 10000},
}
def quota(plan): return PLANS[plan]["limit"]
```

Three branching functions become one data structure.

### Step 5 — Undo a wrong extraction

```python
# 5_unfold.py
# A function shared by only two callers but with six arguments
# is usually better inlined back into two simple functions
# (Inline Function).
```

Roll back when abstraction adds more burden than benefit.

## How to Verify This in a Real Codebase

```bash
python -m pytest -q tests/test_pricing_rules.py
ruff check app/
```

**Expected output**

- Behavior stays stable before and after extraction.
- Table-driven rules should make new cases cheaper to add.

## Failure Modes to Watch

- The shared helper turns into a six-argument mini framework.
- Coincidental similarity gets merged and couples unrelated change reasons.

## What to Notice in This Code

- Only the changing parts become arguments.
- Data structures absorb the branching.
- Abstractions appear only when their value is clear.

## Five Common Mistakes

1. **Extracting on the first duplicate.** Likely coincidental.
2. **Merging code that looks alike but means different things.** Coupling grows.
3. **Extractions with more than five arguments.** A failed abstraction signal.
4. **Extracting without tests.** Regression risk.
5. **Ignoring data duplication.** It is more dangerous than code duplication.

## How This Shows Up in Production

Most policy branches — API routes, form validation, pricing tiers — can move into data. Adding a new policy becomes a code-free PR.

## How a Senior Engineer Thinks

- Looks for shared change reasons, not shared shapes.
- Waits for the third occurrence.
- Acknowledges the cost (coupling) of abstraction.
- Removes data duplication first.
- Rolls back wrong extractions without ego.

## Checklist

- [ ] Does the duplicate code change for the same reason?
- [ ] Is the differing part clear?
- [ ] Is the argument count reasonable?
- [ ] Can it be expressed as data?
- [ ] Does merging simplify the call sites?

## Practice Problems

1. Find one piece of coincidental duplication in your code and write down why you keep it as is.
2. Extract one piece of essential duplication into a function.
3. Move one if/elif policy chain into a data structure.

## Wrap-up and Next Steps

DRY is about a single source of change. Next, we tidy up another rotting place: error handling.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Removing Duplication?**
  - The article treats Removing Duplication as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Removing Duplication?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Removing Duplication reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Clean Code 101 (1/10): What Is Clean Code?](./01-what-is-clean-code.md)
- [Clean Code 101 (2/10): Naming](./02-naming.md)
- [Clean Code 101 (3/10): Small Functions](./03-small-functions.md)
- [Clean Code 101 (4/10): Simplifying Conditionals](./04-simplifying-conditionals.md)
- **Removing Duplication (current)**
- Error Handling (upcoming)
- Comments and Documentation (upcoming)
- Testable Code (upcoming)
- Refactoring Basics (upcoming)
- Good Code Review Standards (upcoming)

<!-- toc:end -->

## References

- [The Pragmatic Programmer — DRY](https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/)
- [Sandi Metz — The Wrong Abstraction](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction)
- [Refactoring — Extract Function](https://refactoring.com/catalog/extractFunction.html)
- [Refactoring — Inline Function](https://refactoring.com/catalog/inlineFunction.html)
- [The wrong abstraction](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction)
Tags: Computer Science, CleanCode, DRY, Duplication, Refactoring, Abstraction
