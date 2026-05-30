---
series: clean-code-101
episode: 7
title: "Clean Code 101 (7/10): Comments and Documentation"
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
  - Comments
  - Documentation
  - Docstring
  - Readability
seo_description: Learn when not to comment, how to write intent comments and docstrings, and how to manage TODO discipline well.
last_reviewed: '2026-05-15'
---

# Clean Code 101 (7/10): Comments and Documentation

Comments feel helpful precisely when the code is hardest to read. That is why comments become risky so quickly: they often preserve a bad structure instead of forcing it to improve.

This is the 7th post in the Clean Code 101 series.

Here we will separate the explanations that belong in naming and structure from the few that belong in intent comments, warnings, docstrings, and contributor-facing docs.


![clean code 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/clean-code-101/07/07-01-concept-at-a-glance.en.png)
*clean code 101 chapter 7 flow overview*
> If you need explanation, try fixing code first. Only then add comments.

## Questions to Keep in Mind

- When is it better not to write a comment at all?
- How do intent comments and warning comments differ?
- What rules should Python docstrings follow?

## Why It Matters

Comments tend to lie. Code changes; comments rarely follow. When something feels like it needs explaining, the first question should be whether better names and structure can eliminate the need for explanation altogether.

That said, documentation is not useless. Public API contracts, quirky external-system behavior, and caller-safety warnings often cannot be expressed through code alone. The key is keeping comments narrow and purposeful.

## Key Terms

- **Self-documenting code**: Names and structure expose intent.
- **Intent comment**: Explains why a piece of code exists.
- **Docstring**: Usage information attached to a function or class.
- **TODO/FIXME**: Markers for future work; must be traceable.
- **API doc**: The contract of a public interface.

## Comment vs Self-Documenting Code: When to Choose Which

Good comments are few and precise. Better code needs almost none. The table below clarifies when to comment and when to improve code instead.

| Situation | Improve Code First | Comment First | Reasoning |
| --- | --- | --- | --- |
| Ambiguous variable/function name | O | X | Renaming is the permanent fix |
| Working around a complex external contract | X | O | "Why" is hard to express in code alone |
| Performance optimization trick | X | O | Intent and constraints must be recorded for safety |
| TODO/FIXME item | X | O | Needs a traceable work memo |
| Public API input/return contract | X | O (docstring) | Caller contract requires documentation |

If a comment merely restates what the code does, it is a deletion candidate. If it conveys an external constraint, historical context, or danger warning, it is worth keeping.

## Before/After

**Before**

```python
# increment i by one
i = i + 1

# user list
def gu(): ...
```

**After**

```python
def get_active_users(): ...
```

The name replaces the comment.

## Good Comments vs Bad Comments

```python
# Bad comment: repeats what the code already says.

def add_one(value: int) -> int:
    # add 1 to value
    return value + 1
```

```python
# Good comment: explains WHY this implementation was chosen.

def parse_gateway_status(response: dict) -> str:
    # The payment gateway returns HTTP 200 even on failure.
    # We ignore the status code and check the body value instead.
    if response.get("error_code"):
        return "FAILED"
    return "PAID"
```

The difference shows up in maintenance. Bad comments age into lies; good comments preserve decision context.

## Hands-on: Five Steps to Useful Documentation

### Step 1 — Intent comment

```python
# 1_intent.py
# The payment gateway sometimes returns 200 with an error in the body,
# so we read body.status instead of the HTTP status code.
def is_paid(resp):
    return resp.json().get("status") == "PAID"
```

Capture context that the code cannot show.

### Step 2 — Warning comment

```python
# 2_warning.py
# WARNING: this function performs IO. Do not call inside a transaction.
def upload_invoice(path): ...
```

Place warnings where the caller can be hurt.

### Step 3 — Docstring

```python
# 3_doc.py
def discount(price: int, rate: float) -> int:
    """Return the price after applying a discount.

    Args:
        price: Integer price in cents.
        rate: Discount rate in [0, 1].

    Returns:
        Rounded integer price.

    Raises:
        ValueError: When rate is out of range.
    """
    if not 0 <= rate <= 1:
        raise ValueError("rate out of range")
    return int(price * (1 - rate))
```

Public functions deserve a docstring.

### Step 4 — README header

```markdown
<!-- 4_readme.md -->
# checkout-service

Payment domain service that responds within 5 seconds.

- Run: `make run`
- Test: `make test`
- Env vars: `GATEWAY_URL`, `SECRET_KEY`
```

A new contributor should onboard in 30 seconds.

### Step 5 — TODO with an owner

```python
# 5_todo.py
# TODO(yeongseon, 2026-06-01): replace simple retry with exponential backoff.
def retry_simple(): ...
```

Every TODO needs a person and a date.

## Python Docstring Practical Rules

```python
def calculate_refund_amount(total_cents: int, cancel_fee_rate: float) -> int:
    """Calculate the refund amount in cents.

    Args:
        total_cents: Original payment amount in cents.
        cancel_fee_rate: Cancellation fee rate in [0, 1].

    Returns:
        Refund amount after deducting the fee, in cents.

    Raises:
        ValueError: When fee rate is out of range.
    """
    if not 0 <= cancel_fee_rate <= 1:
        raise ValueError("cancel_fee_rate must be in [0, 1]")

    refund_cents = int(total_cents * (1 - cancel_fee_rate))
    return max(refund_cents, 0)
```

A docstring is a contract document, not an implementation description. Record "what goes in, what comes out, what can break" — not "how it works internally."

## Documentation Quality Check Routine

1. Can you state the function's purpose within 10 seconds of reading the code alone?
2. Does the comment explain "why"?
3. Does the TODO have an owner, a deadline, and an issue link?
4. Does the public API's docstring contract match its tests?

```python
def should_keep_comment(comment_text: str, explains_why: bool, duplicates_code: bool) -> bool:
    if duplicates_code:
        return False
    return explains_why and len(comment_text.strip()) > 0
```

Adding this check to your code review template reduces noise comments and raises documentation quality.

## Comment Quality Decision Table

Comments add value when they record decisions that code cannot express — not when they restate what code already says.

| Comment Type | Good Example | Bad Example |
| --- | --- | --- |
| Intent explanation | Why a specific constraint led to this implementation | Restating the code in prose |
| Warning | Explicit transaction/performance/security risk | Vague "be careful" note |
| TODO | Includes owner, deadline, and follow-up condition | Ownerless TODO accumulating silently |
| Documentation link | Connects to ADR or issue number | Unsourced claim |

## Before/After Demo: Names and Structure Over Comments

```python
# before
def p(a, b):
    # user can purchase
    if a and b > 0:
        return True
    return False

# after
def can_purchase(is_active_user: bool, stock_quantity: int) -> bool:
    return is_active_user and stock_quantity > 0
```

When names carry intent, comments become unnecessary. Comments should be the last resort.

## Documentation Routine Example

1. Use a fixed What/Why/How/Risk template in every PR description.
2. When changing a public API, update the README and usage examples in the same PR.
3. Include an ADR link for any change with operational impact.

```markdown
## Change Summary
- What: Restructure order cancellation policy to state-based
- Why: Eliminate branch duplication and prevent policy misinterpretation
- How: Introduce strategy object; keep existing API signature
- Risk: Legacy callers may have status-string typos
```

## Linter Example: Minimum Docstring Standards

```toml
[tool.ruff.lint]
select = ["D", "E", "F", "B"]
ignore = ["D203", "D213"]
```

Automating docstring rules catches missing function-level documentation early and keeps quality uniform across the team.

## How to Verify This in a Real Codebase

```bash
ruff check app/
python -m pytest -q tests/test_public_api_docs.py
```

**Expected output**

- Names and structure should carry the main explanation without comment noise.
- Public API contracts should match both tests and docs.

## Failure Modes to Watch

- Comments merely restate the code.
- TODOs have no owner or tracking link and turn into permanent debt.

## What to Notice in This Code

- Code expresses "what"; comments express "why".
- Docstrings make the usage contract explicit.
- TODOs are traceable.

## Five Common Mistakes

1. **Comments that restate the code.** Pure noise.
2. **Stale comments.** They become lies.
3. **Anonymous TODOs.** They live forever.
4. **Boilerplate docstrings on every function.** Zero information.
5. **Secrets or local paths in comments.** Bad for security and portability.

## How This Shows Up in Production

Strong teams require docstrings on public APIs and allow only intent comments internally. Every TODO carries an issue link.

## How a Senior Engineer Thinks

- Improves names and structure before adding a comment.
- Writes only "why" comments.
- States contracts on public APIs.
- Tags TODOs with an owner and a date.
- Updates stale comments together with the code change.

## Checklist

- [ ] Is the code self-explanatory?
- [ ] Does the comment explain "why"?
- [ ] Do public functions have a docstring?
- [ ] Do TODOs have an owner and date?
- [ ] Are old comments still accurate?

## Practice Problems

1. Delete three noise comments and improve names instead.
2. Add a docstring to one public function.
3. Attach an issue link and date to one TODO.

## Wrap-up and Next Steps

Good comments are few and accurate. Next we tackle what truly decides a codebase's fate: testable code.

## Answering the Opening Questions

- **When is it better *not* to write a comment?**
  - When names and structure alone convey intent. Instead of `# increment i by 1`, rename to `get_active_users()` or `can_purchase(is_active_user, stock_quantity)` so the code reads on its own—and outlasts comments that drift.
- **How do intent comments and warning comments differ?**
  - Intent comments explain *why* an implementation was chosen (e.g., payment gateway returns 200 but body status must still be checked). Warning comments alert callers to danger ("Do not call inside a transaction"). Neither repeats what the code does—both communicate background or risk that code alone can't convey.
- **What rules should Python docstrings follow?**
  - Treat docstrings as contract documents, not implementation descriptions. Specify `Args`, `Returns`, `Raises` with input units and exception conditions. The `discount` and `calculate_refund_amount` examples let callers know what to pass and what to expect—aligning tests and docs on the same contract.

<!-- toc:begin -->
## In this series

- [Clean Code 101 (1/10): What Is Clean Code?](./01-what-is-clean-code.md)
- [Clean Code 101 (2/10): Naming](./02-naming.md)
- [Clean Code 101 (3/10): Small Functions](./03-small-functions.md)
- [Clean Code 101 (4/10): Simplifying Conditionals](./04-simplifying-conditionals.md)
- [Clean Code 101 (5/10): Removing Duplication](./05-removing-duplication.md)
- [Clean Code 101 (6/10): Error Handling](./06-error-handling.md)
- **Comments and Documentation (current)**
- Testable Code (upcoming)
- Refactoring Basics (upcoming)
- Good Code Review Standards (upcoming)

<!-- toc:end -->

## References

- [Clean Code (Ch. 4 Comments)](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)
- [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/)
- [Google Python Style Guide — Comments](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [Write the Docs — Documentation Guide](https://www.writethedocs.org/guide/)
Tags: Computer Science, CleanCode, Comments, Documentation, Docstring, Readability
