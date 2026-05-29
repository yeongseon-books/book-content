---
series: clean-code-101
episode: 2
title: "Clean Code 101 (2/10): Naming"
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
  - Naming
  - Readability
  - Refactoring
  - SoftwareEngineering
seo_description: Six signals of a good name, naming variables vs functions vs classes, and the most common naming mistakes.
last_reviewed: '2026-05-15'
---

# Clean Code 101 (2/10): Naming

Bad names waste time before any logic is understood. A reviewer pauses at `data`, guesses what it means, and rereads the same block twice.

This is the 2nd post in the Clean Code 101 series.

Here we will look at the signals of a strong name, how variable, function, and class names play different roles, and how domain language lowers search and review cost.


![clean code 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/clean-code-101/02/02-01-concept-at-a-glance.en.png)
*clean code 101 chapter 2 flow overview*
> Good names eliminate the need for explanation and make search, review, and documentation easier at the same time.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Naming?
- Which signal should the example or diagram make visible for Naming?
- What failure should be prevented first when Naming reaches a real system?

## Questions this article answers

- What signals tell you a name is actually a good one?
- How should variable, function, and class names differ in the role they play?
- How do you bring domain language into code without making it sound forced?
- What naming mistakes show up again and again in real codebases?
- What is the safest order for a rename?

> Good names do not make code shorter. They make intent visible sooner.

## Why It Matters

Names are the most-read element of code. Pick a wrong one and you keep saying it forever.

> A searchable name is the start of maintainability.

The name lifts intent into view.

## Key Terms

- **Intention-revealing**: Says what and why.
- **Searchable**: Found by grep in one shot.
- **Pronounceable**: A name you can say in a meeting.
- **Domain term**: Use the business word as-is.
- **Length budget**: Shorter is not better; accuracy first.

## Before/After

**Before**

```python
d = 86400  # ?
```

**After**

```python
SECONDS_PER_DAY = 86400
```

The constant carries meaning.

## Hands-on: Six Naming Principles

### Step 1 — Reveal intent

```python
# 1_intent.py
def f(x): return x[0]            # of what?
def first_completed_order(orders): return orders[0]
```

The name explains the call site.

### Step 2 — Searchable

```python
# 2_search.py
TAX = 0.08                       # used where? unclear
DEFAULT_SALES_TAX_RATE = 0.08
```

Caught by a single grep.

### Step 3 — Domain terms

```python
# 3_domain.py
def calc(items): ...             # domain lost
def calculate_invoice_subtotal(line_items): ...
```

Code and business speak the same word.

### Step 4 — Avoid negatives

```python
# 4_negative.py
if not is_not_empty(x): ...      # double negative
if is_empty(x): ...
```

Affirmatives use less brain.

### Step 5 — Balance brevity and accuracy

```python
# 5_balance.py
i, j, k                          # short loops are fine
customer_balance_cents           # domain names can be long
```

Narrow scope: short. Wide scope: precise.

## How to Verify This in a Real Codebase

```bash
ruff check app/ --select N
python -m pytest -q tests/test_naming_examples.py
```

**Expected output**

- Inconsistent naming patterns and weak abbreviations surface first.
- After a rename, tests should stay green without behavior drift.

## Failure Modes to Watch

- Renaming only types while leaving domain language muddy.
- Verifying the declaration but missing the full set of call sites.

## What to Notice in This Code

- The name creates meaning at the call site.
- Searchability enables future analysis.
- Domain terms bridge users and developers.

## Five Common Mistakes

1. **`data`, `info`, `obj`.** Zero information.
2. **Heavy abbreviations.** Names like `usrCtxMgr`.
3. **Numeric suffixes.** `process2`, `process3` carry no meaning.
4. **Type in the name.** Use `user`, not `user_dict`.
5. **Lying names.** `getXxx` that mutates.

## How This Shows Up in Production

Mature teams keep a domain glossary in the repo and enforce consistency in PRs. Lints forbid one-letter variables outside loops and require an abbreviation allow-list.

## How a Senior Engineer Thinks

- Names are half the documentation.
- Accuracy beats brevity.
- Searchability decides future cost.
- Bring domain terms straight into code.
- A lying name is fraud.

## Checklist

- [ ] Does the name reveal intent?
- [ ] Is it grep-searchable?
- [ ] Does it use a domain term?
- [ ] Did you avoid negatives?
- [ ] Is length appropriate to scope?

## Practice Problems

1. Find five `data`/`info`/`obj` and rename them.
2. Expand five abbreviations.
3. Build a one-page domain glossary.

## Wrap-up and Next Steps

Naming is the single highest-leverage readability tool. Next we shrink the unit those names point at — small functions.

## Answering the Opening Questions

- **What signals identify a good name?**
  - Intention-revealing, searchable, pronounceable, and domain-aligned. Names like `SECONDS_PER_DAY`, `DEFAULT_SALES_TAX_RATE`, `calculate_invoice_subtotal` satisfy meaning and searchability simultaneously.
- **How do variable, function, and class naming differ?**
  - Variables reveal value meaning and unit (`invoice_total_cents`); functions carry verb + purpose (`calculate_order_total`); classes are role-centered nouns (`InvoiceRepository`). The standard shifts based on what the name promises to callers—not one rule for all.
- **How do you bring domain terms naturally into code?**
  - Map user expressions to code terms 1:1 (as the domain-term table showed) and use the same words in tests and API schemas: `order_total_cents`, `payment_confirmed`, `discount_coupon`. Alignment cuts translation cost in meetings, PRs, and incident response, and makes rename scope obvious.

## Applying Variable, Function, and Class Naming in Practice

A name is not a style choice — it is a contract. The moment a caller reads the name, expectations lock in. The table below captures the rules used most often in production code.

| Target | Good Pattern | Anti-pattern | Example |
| --- | --- | --- | --- |
| Variable | Reveal value meaning | `data`, `tmp`, `obj` | `invoice_total_cents` |
| Boolean | Question/state prefix | Double negatives | `is_active`, `has_permission` |
| Function | Verb + domain purpose | `do_stuff`, `handle_data` | `calculate_invoice_total` |
| Class | Role-centered noun | Leaking implementation detail | `InvoiceRepository` |
| Collection | Plural + element meaning | Singular form confusion | `active_users`, `line_items` |
| Constant | UPPER_CASE with unit | Magic numbers without units | `DEFAULT_TIMEOUT_SECONDS` |

The key is consistency. If the same domain concept gets different names in different files, searchability and collaboration speed collapse. Agree on a glossary first; then execute renames broadly in one pass.

## Full Before/After: When Names Change Intent

```python
# before

def p(u, o, c):
    if u and o:
        t = 0
        for i in o:
            t += i["p"] * i["q"]
        if c:
            t -= 1000
        return t
    return None

# after
from typing import Iterable

def calculate_order_total(user_id: str, line_items: Iterable[dict], has_coupon: bool) -> int | None:
    if not user_id or not line_items:
        return None

    subtotal_cents = 0
    for line_item in line_items:
        subtotal_cents += line_item["unit_price_cents"] * line_item["quantity"]

    if has_coupon:
        subtotal_cents -= 1000

    return subtotal_cents
```

The logic is nearly identical, but the second version tells the caller what units to expect, what inputs mean, and under what conditions `None` returns. That difference shows up directly in debugging time and review speed.

## Safe Rename Procedure

A rename looks small but its blast radius is wide. Follow this sequence to reduce risk:

1. Define the domain meaning of the candidate name first.
2. Run a reference search to identify all affected files.
3. Distinguish public API from internal implementation.
4. Lock tests green before touching names.
5. Rename one concept at a time and re-verify immediately.

```python
def normalize_variable_name(raw_name: str) -> str:
    cleaned = raw_name.strip().lower().replace(" ", "_")
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned
```

Tooling like this normalizer keeps large-scale renames consistent. Ultimately, name quality depends less on personal taste and more on team agreement and automation level.

## Naming Standards: Locking Team Agreement Into Code

Naming is a shared contract, not personal preference. Place this standard in your repo root doc and PR template so review criteria stabilize quickly.

| Category | Recommended | Forbidden | Example |
| --- | --- | --- | --- |
| Boolean | `is_`, `has_`, `can_` prefix | `flag`, `status` alone | `has_payment_method` |
| Numeric with units | Suffix the unit | Unitless number names | `retry_interval_seconds` |
| Collection | Plural + element meaning | `list`, `arr`, `data` | `overdue_invoices` |
| Derived value | Suffix showing computation | Reuse original name | `normalized_email` |
| Temporary | Block-scoped purpose | `tmp`, `x`, `v2` | `next_status` |

## Function Extraction + Rename Demo

```python
# before
def run(a, b, c):
    if a and b and c > 0:
        return b * c * 0.9
    return 0

# after
def calculate_discounted_total(has_membership: bool, item_price_cents: int, quantity: int) -> int:
    if not is_discount_eligible(has_membership, item_price_cents, quantity):
        return 0
    return int(item_price_cents * quantity * 0.9)

def is_discount_eligible(has_membership: bool, item_price_cents: int, quantity: int) -> bool:
    return has_membership and item_price_cents > 0 and quantity > 0
```

The key insight is not the extraction itself but the contract the names create. Callers understand inputs without reading the body, and change impact is traceable.

## Domain Term Table

| User expression | Code term | Avoid |
| --- | --- | --- |
| Order total | `order_total_cents` | `sum`, `total_value` |
| Payment complete | `payment_confirmed` | `done`, `ok` |
| Ready to ship | `ready_for_shipment` | `prepared`, `state3` |
| Discount coupon | `discount_coupon` | `dc`, `ticket` |

Rather than keeping the glossary separate from code, put the same terms in tests and API schemas. When terms align across layers, incident reports get shorter too.

## Enforcing Naming Rules With a Linter

```toml
# pyproject.toml
[tool.ruff.lint]
select = ["E", "F", "N", "B"]

[tool.ruff.lint.pep8-naming]
ignore-names = ["setUp", "tearDown"]
```

Once naming rules live in the linter, reviewers stop repeating "please rename" and focus on design decisions and risk assessment instead.

## Rename Migration Plan for Large Codebases

In a large repo, name improvements cannot finish in one shot. Prioritize by area and proceed incrementally.

| Priority | Target | Criterion | Done when |
| --- | --- | --- | --- |
| 1 | Public API | External callers depend on it | Changelog + compat verified |
| 2 | Core domain | Changes frequently | Glossary matches code |
| 3 | Internal utils | Limited blast radius | Tests pass |

```python
RENAME_MAP = {
    "calc": "calculate_invoice_total",
    "usr": "user",
    "amt": "amount_cents",
    "dt": "created_at",
}

def suggest_renamed_identifier(identifier: str) -> str:
    return RENAME_MAP.get(identifier, identifier)
```

Such a mapping doubles as input to automated substitution tools. But always follow automated renames with a semantic review — string replacement does not understand context.

## Review Comment Style for Naming Issues

- **Observation**: `result` is reused with three different meanings across stages.
- **Risk**: Debugging becomes harder when value tracking is ambiguous.
- **Suggestion**: Split into `validated_payload`, `persisted_order`, `response_body` to separate stage-level semantics.

This approach avoids aggressive phrasing while making the reason for change clear. Review language is part of code quality.

## Change Impact Scoring

Before renaming, estimate propagation risk:

- Count callers of the target function.
- Separate whether input/output contracts change.
- Record whether exception types or log event names shift.
- Verify test cases cover both input boundaries and failure boundaries.

```python
def change_impact_score(callers: int, contract_changed: bool, exception_changed: bool) -> int:
    score = callers * 2
    if contract_changed:
        score += 5
    if exception_changed:
        score += 3
    return score
```

| Score range | Recommended strategy |
| --- | --- |
| 0–5 | Single PR |
| 6–12 | Separate refactoring PR from feature PR |
| 13+ | Staged deployment with rollback plan |

Putting a number on impact moves review conversations from gut feeling to evidence.

<!-- toc:begin -->
## In this series

- [Clean Code 101 (1/10): What Is Clean Code?](./01-what-is-clean-code.md)
- **Naming (current)**
- Small Functions (upcoming)
- Simplifying Conditionals (upcoming)
- Removing Duplication (upcoming)
- Error Handling (upcoming)
- Comments and Documentation (upcoming)
- Testable Code (upcoming)
- Refactoring Basics (upcoming)
- Good Code Review Standards (upcoming)

<!-- toc:end -->

## References

- [Clean Code (Ch. 2 Meaningful Names)](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)
- [Domain-Driven Design — Eric Evans](https://www.oreilly.com/library/view/domain-driven-design-tackling/0321125215/)
- [Google Style Guide — Naming](https://google.github.io/styleguide/pyguide.html#316-naming)
- [PEP 8 — Naming Conventions](https://peps.python.org/pep-0008/#naming-conventions)
- [Ruff pep8-naming rules](https://docs.astral.sh/ruff/rules/#pep8-naming-n)
- [PEP 8 naming conventions](https://peps.python.org/pep-0008/#naming-conventions)
Tags: Computer Science, CleanCode, Naming, Readability, Refactoring, SoftwareEngineering
