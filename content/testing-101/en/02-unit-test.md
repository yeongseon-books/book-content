---
series: testing-101
episode: 2
title: "Testing 101 (2/10): Unit Test"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Testing
  - Unit Test
  - pytest
  - Python
  - Quality
seo_description: Definition of a unit test, the AAA pattern, pytest fixtures and parametrize, edge cases, and the five conditions of a good unit test.
last_reviewed: '2026-05-04'
---

# Testing 101 (2/10): Unit Test

When people first hear “unit test,” they often agree on the word *test* but not on the word *unit*. Is the unit a function, a method, a class, or a whole module? If that boundary stays fuzzy, tests quickly become too large, too slow, and too vague to diagnose.

Unit testing is mostly an exercise in shrinking the problem. Remove external dependencies, isolate one behavior, and get feedback in seconds instead of minutes.

This is post 2 in the Testing 101 series. Here we define the scope of a unit test, walk through the AAA pattern and core `pytest` features, and show what makes a unit test genuinely useful in a growing codebase.

> A strong unit test is small enough to fail loudly and fast, but precise enough to explain exactly what contract broke.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Unit Test?
- Which signal should the example or diagram make visible for Unit Test?
- What failure should be prevented first when Unit Test reaches a real system?

## Big Picture

![testing 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/testing-101/02/02-01-concept-at-a-glance.en.png)

*testing 101 chapter 2 flow overview*

This picture places Unit Test inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> A good unit test fails loudly when the contract breaks, and passes silently when it holds.

## What You Will Learn

- The definition and *scope* of a unit test
- The *AAA pattern* (Arrange/Act/Assert)
- pytest basics, fixtures, and parametrize
- *Edge cases* and *exception cases*
- The *five conditions* of a good unit test

## Why It Matters

Unit tests are *the base of the pyramid*. Because they are fast, *thousands* of them run in *seconds*. Strong unit tests *let upper layers (integration/E2E) stay small*.

> Many fast unit tests are the *foundation of the whole strategy*.

## Concept at a Glance
A unit test verifies one behavior by isolating a single function or method from its external dependencies, running it in milliseconds, and confirming its output or state change without touching real databases, APIs, or clocks.
## Key Terms

- **Unit**: a *minimal piece* such as a single function, method, or class.
- **AAA pattern**: *Arrange* → *Act* → *Assert*.
- **Fixture**: *prepared data/objects* shared between tests.
- **Parametrize**: collapsing tests *that differ only by input* into *one function*.
- **Edge case**: *boundary values* (0, negative, empty string, None, ...).

## Before/After

**Before (one big test)**

```python
def test_user_flow():
    u = create_user("a")
    u.activate()
    u.upgrade()
    assert u.plan == "pro"
```

**After (split into small units)**

```python
def test_create_user_starts_inactive(): ...
def test_activate_sets_active(): ...
def test_upgrade_sets_pro(): ...
```

## Hands-on: pytest in Five Steps

### Step 1 — The function under test

```python
# src/discount.py
def apply_discount(price: int, percent: int) -> int:
    if not 0 <= percent <= 100:
        raise ValueError("percent must be 0..100")
    return price - price * percent // 100
```

### Step 2 — Basic test (AAA)

```python
# tests/test_discount.py
from src.discount import apply_discount

def test_apply_10_percent_discount():
    # Arrange
    price, percent = 1000, 10
    # Act
    result = apply_discount(price, percent)
    # Assert
    assert result == 900
```

### Step 3 — Group with parametrize

```python
import pytest

@pytest.mark.parametrize("price,percent,expected", [
    (1000, 0, 1000),
    (1000, 50, 500),
    (1000, 100, 0),
])
def test_apply_discount_table(price, percent, expected):
    assert apply_discount(price, percent) == expected
```

### Step 4 — Exception cases

```python
def test_apply_discount_invalid_percent_raises():
    with pytest.raises(ValueError):
        apply_discount(1000, 150)
```

### Step 5 — Fixture

```python
@pytest.fixture
def base_price() -> int:
    return 10_000

def test_with_fixture(base_price: int):
    assert apply_discount(base_price, 10) == 9_000
```

## What to Notice in This Code

- Each test asserts *one thing*.
- Same-shaped tests are *parametrized* to *cut duplication*.
- Exception cases live in *their own test*.

## Five Common Mistakes

1. **Calling the *real* database.** That is an *integration test*.
2. **Tests depending on *each other's state*.** Reordering *breaks* them.
3. **Waiting via `time.sleep`.** Unit tests *do not wait*.
4. **Meaningless `assert True`.** It only adds noise.
5. **Test names like *test_1, test_2*.** The name is *the documentation*.

## Verification Points

1. Run the boundary cases `apply_discount(1000, 0)` and `apply_discount(1000, 100)` and confirm both still match the contract.
2. Try `apply_discount(1000, 150)` and make sure the exception path is explicit and easy to read in the test output.
3. Check that no real DB, network, filesystem, or clock dependency has slipped into the test file. The moment that happens, you are paying integration-test cost for unit-test feedback.

**Expected output:** normal cases should stay green in milliseconds, and invalid percentages should fail with a clear `ValueError` contract.

## Failure Signals and First Checks

- If exception cases are not wrapped in `pytest.raises(...)`, the failure story is usually incomplete.
- If fixtures share mutable state, the suite may only fail when test order changes.
- If one unit test needs too many setup steps, it is often exposing a design problem rather than a testing problem.

## How This Shows Up in Production

Core domain logic (pricing, authorization, state machines) is *always* covered by thick unit tests. The more incident-prone the code, the *higher the ROI of unit tests*.

## How a Senior Engineer Thinks

- Grows *small, fast unit tests* first.
- Names tests with *one line of behavior*.
- *Always* covers boundary values for the same function.
- Uses *parametrize* to express *repetition*.
- Keeps *all* unit tests under *five seconds*.

## Checklist

- [ ] You wrote *three or more* tests for one function.
- [ ] You covered *boundary* and *exception* cases.
- [ ] You followed AAA structure.
- [ ] You used parametrize *once*.

## Practice Problems

1. Build `is_palindrome(s)` and write a parametrized test with *five* inputs.
2. Cover *boundary cases* like empty string, single char, and whitespace.
3. Introduce a bug intentionally and note *which test catches it*.

## Wrap-up and Next Steps

Unit tests are *small, fast, and free of external dependencies*. The next post climbs one step up to *integration tests*, which verify several modules together.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Unit Test?**
  - The article treats Unit Test as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Unit Test?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Unit Test reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Testing 101 (1/10): What Is Testing?](./01-what-is-testing.md)
- **Unit Test (current)**
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

- [pytest — parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html)
- [pytest — fixtures](https://docs.pytest.org/en/stable/explanation/fixtures.html)
- [Martin Fowler — Unit Test](https://martinfowler.com/bliki/UnitTest.html)
- [Google Testing Blog](https://testing.googleblog.com/)

Tags: Testing, Unit Test, pytest, Python, Quality
