---
series: testing-101
episode: 1
title: What Is Testing?
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Testing
  - Quality
  - Software
  - Basics
  - Engineering
seo_description: A starting point for the Testing 101 series — what tests are, what kinds exist, and why automated tests beat manual checks.
last_reviewed: '2026-05-04'
---

# What Is Testing?

> Testing 101 series (1/10)

<!-- a-grade-intro:begin -->

**Core question**: *Why* do we write tests? Is one click in the browser not *enough*?

> A test is code that automatically checks whether *your code behaves as intended*. A human hand forgets in *three days*; an automated test still runs *three years from now*.

<!-- a-grade-intro:end -->

## What You Will Learn

- The *definition* and purpose of a test
- The difference between *manual and automated* testing
- The *main kinds* of tests (unit, integration, E2E)
- What happens *when tests are missing*
- Where the *unit test* of the next post fits

## Why It Matters

Without tests, *every change is a gamble*. You fix signup and *payments* break; you fix payments and *login* breaks. Tests are the *safety net for change*.

> Tests turn *slow hands* into *fast code*.

## Concept at a Glance

```mermaid
flowchart LR
    Code["Production code"] --> Test["Test code"]
    Test --> Run["Test runner"]
    Run --> Result["Pass / Fail + error location"]
```

## Key Terms

- **Test**: a check that expresses *expected behavior* in *code*.
- **Assertion**: a function that *asserts a value matches the expectation*.
- **Test runner**: a tool that *collects and runs* tests.
- **Fixture**: *prepared data/state* that a test uses.
- **Coverage**: the *fraction of production code* that tests execute.

## Before/After

**Before (manual testing)**

```text
1. Start the server locally
2. In the browser: signup → login → click pay
3. Say "it works!" and merge the PR
4. *Three days later* it breaks from someone else's change
```

**After (automated testing)**

```bash
$ pytest
collected 142 items
.................................... 142 passed in 3.4s
```

## Hands-on: Your First Automated Test in Five Steps

### Step 1 — The function under test

```python
# src/calc.py
def add(a: int, b: int) -> int:
    return a + b
```

### Step 2 — The test file

```python
# tests/test_calc.py
from src.calc import add

def test_add_positive_numbers():
    assert add(2, 3) == 5

def test_add_with_zero():
    assert add(0, 7) == 7
```

### Step 3 — Run it

```bash
pip install pytest
pytest -v
```

### Step 4 — Break it on purpose

```python
def add(a: int, b: int) -> int:
    return a - b   # bug
```

```bash
pytest -v
# FAILED tests/test_calc.py::test_add_positive_numbers - assert -1 == 5
```

### Step 5 — Fix it again

Restore `add` and run `pytest` again — *all green*.

## What to Notice in This Code

- A test is *small code*. It does *not need to be complex*.
- The flow of *broken → green again* is what *builds trust* in tests.
- Tests are also *documentation*: they show *example usage* of a function.

## Five Common Mistakes

1. **Saving tests for *later*.** "Later" becomes *never*.
2. **Cramming *several assertions* into one test, so you cannot tell *what* broke.**
3. **Tests too *slow* to run.** Tests that you do not run are *no tests*.
4. **Test code *more complex than production*.** That itself is a bug.
5. **Treating green `pytest` as *proof of correctness*.** Tests cover *only the cases you wrote*.

## How This Shows Up in Production

Most teams run tests *automatically on every PR* (CI). When a test fails, *the merge is blocked*. That pressure makes teams *write smaller PRs* and *add tests alongside changes*.

## How a Senior Engineer Thinks

- Treats a PR without tests as *temporary*.
- *Fixes a broken test immediately* — or deletes it immediately.
- Treats tests as *the spec* of the code.
- Knows that *fast tests build culture*.
- Decides *what* to verify before *how*.

## Checklist

- [ ] You installed `pytest` and ran it once.
- [ ] You broke the code on purpose and read the *failure message*.
- [ ] You wrote *small tests* with one or two assertions each.
- [ ] You confirmed tests finish in *under three seconds*.

## Practice Problems

1. Write a `subtract(a, b)` function and *three tests* for it.
2. Intentionally introduce a bug and capture the *failure message*.
3. Explain *why we need tests* to a peer in one paragraph.

## Wrap-up and Next Steps

Tests turn *fear of change* into *confidence in change*. The next post starts at the smallest unit — the *unit test*.

<!-- toc:begin -->
- **What Is Testing? (current)**
- Unit Test (upcoming)
- Integration Test (upcoming)
- E2E Test (upcoming)
- Test Double (upcoming)
- Mock and Stub (upcoming)
- Test Coverage (upcoming)
- Regression Test (upcoming)
- Running Tests in CI (upcoming)
- Building a Test Strategy (upcoming)
<!-- toc:end -->

## References

- [pytest docs](https://docs.pytest.org/)
- [Martin Fowler — Testing Strategies](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Google Testing Blog](https://testing.googleblog.com/)
- [The Practical Test Pyramid (article)](https://martinfowler.com/articles/practical-test-pyramid.html)
