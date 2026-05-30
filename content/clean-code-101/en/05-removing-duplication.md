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

## Duplication Removal Techniques by Stage

Removing duplication is not "abstract big all at once." Proceed in small steps while checking change reasons. The table below lists representative techniques and when to apply them.

| Technique | When to Apply | Expected Benefit | Failure Signal |
|---|---|---|---|
| Extract Function | Logic identical and context similar | Reuse, simpler tests | Argument explosion |
| Parameterize | Difference reducible to a few values | Fewer branches | Meaningless flag proliferation |
| Template Method | Algorithm skeleton same, only certain steps differ | Fixed common flow | Inheritance hierarchy bloat |
| Strategy | Policy swaps needed frequently | Easy extension | Excessive object count |
| Data Table | Rules are effectively data | Lower change risk | Key consistency management failure |

The core question in duplication removal is always the same: "Do these two really change for the same reason?"

## Table-Driven Deduplication in Python

```python
from dataclasses import dataclass

@dataclass
class PricingRule:
    name: str
    multiplier: float

PRICING_RULES = {
    "kr": PricingRule(name="kr", multiplier=1.10),
    "jp": PricingRule(name="jp", multiplier=1.08),
    "us": PricingRule(name="us", multiplier=1.07),
}

def apply_tax(base_price: int, country_code: str) -> int:
    rule = PRICING_RULES[country_code]
    return int(base_price * rule.multiplier)
```

When three country-specific functions collapse into a single table, the modification point becomes singular. Testing also simplifies: per-country tests just vary input data against the same function.

## Distinguishing Accidental Similarity from Essential Duplication

Four criteria to evaluate:

1. Do change issues always open together?
2. Is the domain terminology identical?
3. Is the failure impact scope the same?
4. Does deploy timing move together?

```python
def is_essential_duplication(
    same_change_issue: bool,
    same_domain_term: bool,
    same_failure_impact: bool,
    same_release_timing: bool,
) -> bool:
    score = sum([same_change_issue, same_domain_term, same_failure_impact, same_release_timing])
    return score >= 3
```

Defining a simple evaluation function like this as a team convention allows fast decisions on whether to deduplicate.

## When to Undo a Wrong Abstraction

Abstractions are easy to think of as permanent, but inlining is also an important refactoring. Consider rolling back when:

- The shared function's argument count has grown to 5+
- Most callers pass dummy values
- Branch-handling code exceeds the shared logic
- Every new requirement adds another exception flag

Rolling back a wrong abstraction may temporarily look like duplication, but separating change reasons reduces long-term cost.

## Duplication Type Classification

The biggest mistake in deduplication is abstracting prematurely because shapes look similar. Classify whether duplication is semantic or coincidental first.

| Type | Observation Point | Recommended Response | Caution |
|---|---|---|---|
| Text duplication | Identical code blocks copied | Extract function | Watch for argument explosion |
| Algorithm duplication | Identical computation procedure | Common policy function | Preserve domain context |
| Data duplication | Constants/mapping tables repeated | Move to config file | Check default value consistency |
| Process duplication | Same deploy/verification steps repeated | Scriptify | Never skip steps |

## Before/After Demo: Consolidating Duplicate Tax Logic

```python
# before
def order_tax(amount_cents: int) -> int:
    return int(amount_cents * 0.1)

def refund_tax(amount_cents: int) -> int:
    return int(amount_cents * 0.1)

# after
TAX_RATE = 0.1

def calculate_tax(amount_cents: int, rate: float = TAX_RATE) -> int:
    return int(amount_cents * rate)

def order_tax(amount_cents: int) -> int:
    return calculate_tax(amount_cents)

def refund_tax(amount_cents: int) -> int:
    return calculate_tax(amount_cents)
```

## Undoing a Wrong Abstraction Demo

```python
# Over-abstracted
def process(user, a, b, c, d, e):
    ...

# After inlining back
def process_order_payment(user, order_total_cents, coupon_code):
    ...

def process_subscription_payment(user, plan_id, billing_cycle):
    ...
```

The goal of deduplication is not unification itself but reducing change cost. If argument count grows abnormally or call sites become more complex after merging, inlining back is the better choice.

## Linter as an Early Warning System

```toml
[tool.ruff.lint]
select = ["E", "F", "B", "SIM", "PLR"]

[tool.ruff.lint.pylint]
max-args = 5
```

An argument-count limit serves as early warning against over-abstraction. The moment a function tries to absorb every case, the linter fires and forces a structural re-evaluation.

## Change Impact Score

Before refactoring shared code, estimate propagation risk with a simple scoring model.

```python
def change_impact_score(callers: int, contract_changed: bool, exception_changed: bool) -> int:
    score = callers * 2
    if contract_changed:
        score += 5
    if exception_changed:
        score += 3
    return score
```

| Score Range | Recommended Strategy |
|---|---|
| 0-5 | Proceed in a single PR |
| 6-12 | Separate refactoring PR from feature PR |
| 13+ | Staged deploy with rollback plan |

Putting a number on impact moves review conversations from gut feeling to evidence.

## Deduplication Sprint Planning

Deduplication succeeds more often when it is an explicit sprint goal rather than something squeezed between feature work. Do not eliminate all duplication at once; prioritize flows with frequent changes.

| Sprint Item | Selection Criteria | Measurement |
|---|---|---|
| Payment calculation duplication | Top modified in last 4 weeks | PR conflict count reduction |
| Validation logic duplication | Same root cause repeated in incident reports | Defect recurrence rate reduction |
| API response format duplication | Response structure inconsistency | Consumer error rate reduction |

```python
def build_error_response(code: str, message: str) -> dict:
    return {
        "ok": False,
        "error": {
            "code": code,
            "message": message,
        },
    }
```

Judge deduplication success by operational metric improvement, not abstraction elegance. If conflicts decrease and review time drops, the direction is correct.

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

- **What does DRY actually mean?**
  - Not "reduce line count" but "keep each piece of knowledge in a single source." When policies like `PRICING_RULES`, `PLANS`, `calculate_tax` live in one place, changes don't create divergent truths.
- **How do you distinguish accidental resemblance from essential duplication?**
  - Essential duplication shares the same change trigger, domain term, failure impact, and deploy timing—as the `is_essential_duplication` example codified. Merging code that merely looks similar leads to bloated parameters and exception flags—failed abstractions.
- **In what order should extraction and parameterization be applied?**
  - Wait until the third repetition; extract common logic first; parameterize only when the difference truly reduces to a single value. `with_tax(price, rate)` and `greet(name, lang)` show parameters that keep call sites simple—avoiding mini-framework over-abstraction.

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

Tags: Computer Science, CleanCode, DRY, Duplication, Refactoring, Abstraction
