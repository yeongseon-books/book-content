---
series: clean-code-101
episode: 6
title: "Clean Code 101 (6/10): Error Handling"
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
  - ErrorHandling
  - Exceptions
  - Robustness
  - Reliability
seo_description: Choose between exceptions and return values, fail fast, use errors as values, and apply retry with backoff safely.
last_reviewed: '2026-05-15'
---

# Clean Code 101 (6/10): Error Handling

Error handling becomes dangerous when it is everywhere and nowhere at the same time. The code catches broadly, logs vaguely, and leaves the caller guessing which failures still matter.

This is post 6 in the Clean Code 101 series.

Here we will set boundaries for validation, typed exceptions, return-value failures, and retries so that robustness increases without letting the happy path disappear.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Error Handling?
- Which signal should the example or diagram make visible for Error Handling?
- What failure should be prevented first when Error Handling reaches a real system?

## Big Picture

![clean code 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/clean-code-101/06/06-01-concept-at-a-glance.en.png)

*clean code 101 chapter 6 flow overview*

This picture places Error Handling inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> Validate input first, then use exceptions only when flow is lost.

## Questions this article answers

- How do you decide between raising an exception and returning a value?
- When is Fail Fast especially important?
- When is the "errors as values" pattern the better fit?
- Under what conditions is retry with exponential backoff actually safe?
- What try/except anti-patterns show up most often?

> If the caller can make a reasonable local decision, return a value. If not, raise a meaningful exception.

## Why It Matters

When error handling code outweighs business logic, the code stops being readable.

> Error handling is a first-class citizen, but never the lead role.

Validate up front; raise only when control is lost.

## Key Terms

- **Fail Fast**: Surface invalid state immediately.
- **Result/Either**: Encode success/failure as a value.
- **Exception**: Situation the caller cannot recover from locally.
- **Retry**: Repeat a transient failure.
- **Backoff**: Increase the delay between retries.

## Before/After

**Before**

```python
def fetch(url):
    try:
        ...
    except Exception:
        return None  # swallows everything
```

**After**

```python
class FetchError(Exception): ...

def fetch(url):
    try:
        return _http_get(url)
    except TimeoutError as e:
        raise FetchError(f"timeout: {url}") from e
```

Errors travel upward with meaning intact.

## Hands-on: Five Steps to Robust Error Handling

### Step 1 — Fail fast

```python
# 1_fail_fast.py
def transfer(amount):
    if amount <= 0:
        raise ValueError("amount must be positive")
    ...
```

Reject bad input immediately.

### Step 2 — Errors as values

```python
# 2_result.py
from dataclasses import dataclass
@dataclass
class Result:
    ok: bool
    value: object = None
    error: str = ""

def parse_int(s):
    try: return Result(True, int(s))
    except ValueError as e: return Result(False, error=str(e))
```

When the caller will branch, return a value.

### Step 3 — Exception chaining

```python
# 3_chain.py
class ConfigError(Exception): ...

def load_config(path):
    try:
        with open(path) as f: return f.read()
    except FileNotFoundError as e:
        raise ConfigError(f"missing config: {path}") from e
```

`from e` preserves the cause.

### Step 4 — Retry + backoff

```python
# 4_retry.py
import time, random
def with_retry(fn, attempts=3):
    for i in range(attempts):
        try: return fn()
        except TimeoutError:
            if i == attempts - 1: raise
            time.sleep((2 ** i) + random.random())
```

Exponential backoff with jitter.

### Step 5 — Catch only at boundaries

```python
# 5_boundary.py
def handle_request(req):
    try:
        return business_logic(req)
    except ValueError as e:
        return {"status": 400, "error": str(e)}
    except Exception:
        return {"status": 500, "error": "internal"}
```

Use broad catches only at outer boundaries.

## How to Verify This in a Real Codebase

```bash
python -m pytest -q tests/test_error_handling.py
python -m pytest -q tests/test_retry_idempotency.py
```

**Expected output**

- Typed exceptions and boundary mappings stay locked in by tests.
- Retry logic should pass only for idempotent operations.

## Failure Modes to Watch

- Broad catches still sit deep inside business logic.
- Retry is added to operations that can duplicate side effects such as billing.

## What to Notice in This Code

- Validation and handling are separated.
- Domain exception classes carry meaning.
- Retries are safe only when operations are idempotent.

## Five Common Mistakes

1. **Empty except blocks.** All information is lost.
2. **Catching `Exception` indiscriminately.** Debugging becomes impossible.
3. **Logging and continuing anyway.** Bad state accumulates.
4. **Infinite retry loops.** They take systems down.
5. **Using exceptions for control flow.** Expensive and hard to read.

## How This Shows Up in Production

In an API server the handler is the boundary. Domain logic raises typed exceptions; the handler maps them to HTTP responses. Only idempotent operations are auto-retried.

## How a Senior Engineer Thinks

- Validates at the entry point and never again.
- Defines domain exception types.
- Distinguishes recoverable from unrecoverable.
- Pairs idempotency with retry.
- Restricts broad catches to boundaries.

## Checklist

- [ ] Is input validation at the top of the function?
- [ ] Are there domain exception types?
- [ ] Is the except clause narrow enough?
- [ ] Did you preserve the cause with `from e`?
- [ ] Is retry limited to idempotent operations?

## Practice Problems

1. Replace one empty except in your code with meaningful handling.
2. Refactor one parse-style function to the Result pattern.
3. Add backoff retry to one external call.

## Wrap-up and Next Steps

Treat errors as first-class but never as the lead role. Next: an often misused tool — comments and documentation.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Error Handling?**
  - The article treats Error Handling as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Error Handling?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Error Handling reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Clean Code 101 (1/10): What Is Clean Code?](./01-what-is-clean-code.md)
- [Clean Code 101 (2/10): Naming](./02-naming.md)
- [Clean Code 101 (3/10): Small Functions](./03-small-functions.md)
- [Clean Code 101 (4/10): Simplifying Conditionals](./04-simplifying-conditionals.md)
- [Clean Code 101 (5/10): Removing Duplication](./05-removing-duplication.md)
- **Error Handling (current)**
- Comments and Documentation (upcoming)
- Testable Code (upcoming)
- Refactoring Basics (upcoming)
- Good Code Review Standards (upcoming)

<!-- toc:end -->

## References

- [Clean Code (Ch. 7 Error Handling)](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)
- [Joel Spolsky — Exceptions](https://www.joelonsoftware.com/2003/10/13/13/)
- [Google SRE — Handling Overload](https://sre.google/sre-book/handling-overload/)
- [AWS — Exponential Backoff and Jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
- [Python exception hierarchy](https://docs.python.org/3/library/exceptions.html)
- [AWS Builders Library — timeouts, retries, and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
Tags: Computer Science, CleanCode, ErrorHandling, Exceptions, Robustness, Reliability
