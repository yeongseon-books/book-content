---
series: testing-101
episode: 8
title: Regression Test
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
  - Regression
  - Bugfix
  - Quality
  - pytest
seo_description: How to write and operate regression tests so the same bug never returns to production.
last_reviewed: '2026-05-04'
---

# Regression Test

A bug is rarely expensive only once. The real cost comes when the same failure returns months later, after the original context has faded and a different engineer has to reconstruct why the system was fragile in the first place. Software does not remember fixes unless you encode the lesson.

Regression tests are that encoded lesson. They turn a bug report into a failing example, then keep the example around so the same path cannot silently break again.

This is post 8 in the Testing 101 series. Here we walk through the bug → repro test → fix workflow and show how to keep regression tests small, traceable, and cheap enough to live close to the code they protect.

> A regression test is a bug report that learned how to execute itself.

## What You Will Learn

- The definition and purpose of *regression tests*
- The *bug -> test -> fix* workflow
- *Repro tests* and *minimum reproduction cases*
- How to manage the *maintenance cost* of regression tests
- Five common pitfalls

## Why It Matters

Software has *no memory*. A bug fixed once can be *reintroduced by the next contributor*. Regression tests are *the team's memory*.

> A team without regression tests fixes *the same bug forever*.

## Concept at a Glance

![Concept at a Glance](https://yeongseon-books.github.io/book-public-assets/assets/testing-101/08/08-01-concept-at-a-glance.en.png)

*Concept at a Glance*
## Key Terms

- **Regression**: a *previously fixed behavior* that *breaks again*.
- **Repro test**: the *minimum test* that *reproduces* the bug.
- **Bug ID**: the *unique identifier* in your issue tracker (e.g., PROJ-1234).
- **Golden file**: a file that *freezes the expected output* for comparison.
- **Snapshot test**: a test that compares the *entire output snapshot*.

## Before/After

**Before (verbal promise)**

```text
- "I fixed that bug" -> merged
- Six months later the *same bug* shows up again
```

**After (regression test added)**

```python
def test_regression_PROJ_1234_negative_total():
    cart = Cart(); cart.add(Item(price=-1))
    with pytest.raises(ValueError):
        cart.total()
```

## Hands-on: Five Steps to a Regression Test

### Step 1 - Reproduce the bug

```python
# tests/test_regression.py
def test_repro_negative_price_breaks_total():
    cart = Cart(); cart.add(Item(price=-1))
    assert cart.total() >= 0   # currently *fails*
```

### Step 2 - See the red bar

```bash
pytest tests/test_regression.py -v
# FAILED ... assert -1 >= 0
```

### Step 3 - Fix it

```python
class Cart:
    def add(self, item):
        if item.price < 0:
            raise ValueError("price must be >= 0")
        self._items.append(item)
```

### Step 4 - Update the test (capture the intent)

```python
def test_regression_PROJ_1234_negative_price_rejected():
    """Adding an item with a negative price raises ValueError. (PROJ-1234)"""
    cart = Cart()
    with pytest.raises(ValueError):
        cart.add(Item(price=-1))
```

### Step 5 - Lock it into CI

```bash
git add tests/test_regression.py src/cart.py
git commit -m "fix(cart): reject negative price (PROJ-1234)"
```

## What to Notice in This Code

- The test *name* embeds the *bug ID* so it stays *traceable*.
- Regression tests are *small and clear*. Focus on *one reproduction* only.
- You add them *based on recurrence risk*, not as a blanket rule.

## Five Common Mistakes

1. **Fixing the bug but *not writing the test*.** This is *how regressions begin*.
2. **A repro test that is *too large*.** Shrink it to the *minimum* case.
3. **Regression tests that *only accumulate* and are never pruned.** Maintenance cost explodes.
4. **Refreshing snapshots *without thinking*.** If you do not check *why it changed*, the snapshot is *meaningless paperwork*.
5. **Pushing regression tests into *slow E2E suites*.** Keep them at the *lowest layer* possible.

## Verification Points

1. Run the reproduction test against the pre-fix code first and confirm that it really goes red. Without that step, the “regression test” may be decorative.
2. Keep the bug ID in the test name or docstring so later readers can trace why the case exists.
3. Compare whether the regression belongs best as a unit test, integration test, or E2E scenario. The lowest effective layer is usually the cheapest long-term home.

**Expected output:** the pre-fix version should fail deterministically, and the fixed version should make the same test pass without broadening the scenario unnecessarily.

## Failure Signals and First Checks

- Adding only a green test after the fix leaves the real regression risk unproven.
- If the repro is too large, unrelated moving parts will blur the failure cause.
- Blind snapshot refreshes turn regression tests into paperwork.

## How This Shows Up in Production

Most teams enforce the *issue -> repro test -> fix* flow through their *default PR template*. When the *same module produces repeated regressions*, they treat it as a *signal of a design problem*.

## How a Senior Engineer Thinks

- Every *bug-fix PR* must include a *regression test*.
- Keep regression tests as *unit tests* whenever possible.
- *Repeated regressions* mean *refactoring is overdue*.
- Snapshots are refreshed *only after the reason is documented*.
- A *bug ID* is a *note left in the code*.

## Checklist

- [ ] My recent bug fixes have *regression tests*.
- [ ] Test names include the *issue ID and reason*.
- [ ] Repro tests are *small and deterministic*.
- [ ] Regression tests live at the *lowest possible level*.

## Practice Problems

1. Pick *one bug* you fixed recently and add a regression test.
2. Run that test against the *pre-fix code* and confirm it *fails*.
3. If the same module has *three or more past regressions*, write down what *refactoring* it deserves.

## Wrap-up and Next Steps

Regression tests are *the team's memory*. In the next post we move all of these tests onto *CI that runs them automatically*.

<!-- toc:begin -->
- [What is testing?](./01-what-is-testing.md)
- [Unit Test](./02-unit-test.md)
- [Integration Test](./03-integration-test.md)
- [E2E Test](./04-e2e-test.md)
- [Test Doubles](./05-test-double.md)
- [Mock and Stub](./06-mock-and-stub.md)
- [Test Coverage](./07-test-coverage.md)
- **Regression Test (current)**
- Running Tests in CI (upcoming)
- Building a Test Strategy (upcoming)
<!-- toc:end -->

## References

### Official Docs
- [pytest documentation](https://docs.pytest.org/)
- [GitHub Issues documentation](https://docs.github.com/en/issues)

### Practical Reading
- [Martin Fowler — The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [The Pragmatic Programmer — Bug fixing chapter](https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/)

Tags: Testing, Regression, Bugfix, Quality, pytest
