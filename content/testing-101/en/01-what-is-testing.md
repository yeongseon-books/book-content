---
series: testing-101
episode: 1
title: "Testing 101 (1/10): What Is Testing?"
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
  - Quality
  - Software
  - Basics
  - Engineering
seo_description: A starting point for the Testing 101 series — what tests are, what kinds exist, and why automated tests beat manual checks.
last_reviewed: '2026-05-04'
---

# Testing 101 (1/10): What Is Testing?

At first, testing often looks like a manual ritual: start the server, open the browser, click through signup and login, and decide that things seem fine. That works once or twice. It breaks down the moment the codebase, the team, or the release frequency grows.

Manual confirmation also has a short memory. It tells you what happened this afternoon, but it does not protect the same path tomorrow, next week, or after another engineer refactors the code.

This is the first post in the Testing 101 series. Here we define what a test is, why automated checks matter, and where unit, integration, and end-to-end tests fit in the larger picture.

> A test is executable memory for a codebase. It keeps the team from re-learning the same failure by hand.


![testing 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/testing-101/01/01-01-concept-at-a-glance.en.png)
*testing 101 chapter 1 flow overview*
> Without tests, every change carries hidden risk — testing is how a team avoids repeating the same failure.

## Questions to Keep in Mind

- What boundary should you inspect first when applying What Is Testing??
- Which signal should the example or diagram make visible for What Is Testing??
- What failure should be prevented first when What Is Testing? reaches a real system?

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
Testing is a decision-making process: choosing what to verify, when to verify it, and which layers handle which kinds of failures. Manual tests answer individual questions once; automated tests answer the same questions repeatedly, forever.
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

Restore `add` and run `pytest` again — *all green*. This single cycle — break, read the failure, fix, see green — is the fastest way to internalize why tests have value.

In practice, the two most common moments people first write tests are: (1) after fixing a bug, to guarantee it never recurs, and (2) before a refactor, to preserve existing behavior. In both cases, without tests the only option is to verify by eye, and that cost grows exponentially as the codebase grows.

## What to Notice in This Code

- A test is *small code*. It does *not need to be complex*.
- The flow of *broken → green again* is what *builds trust* in tests.
- Tests are also *documentation*: they show *example usage* of a function.

## The Three Levels of Testing

Automated tests split into three levels by verification scope. Later posts cover each in depth, but the big picture here makes each post's position clear.

```text
                ┌───────────┐
               /  E2E Test   \         ← Few, slow, expensive
              /───────────────\
             / Integration Test\       ← Middle ground
            /───────────────────\
           /     Unit Test       \     ← Many, fast, cheap
          └─────────────────────────┘
```

| Level | Scope | Speed | Primary Verification Target |
|---|---|---|---|
| Unit | One function, one class | Milliseconds | Logic correctness |
| Integration | Module boundaries (DB, API, queue) | Seconds | Contract compliance |
| E2E | Full user scenario | Minutes | Business flow completeness |

The ratio is not fixed. Depending on the project, integration may be thicker or E2E may be the core. What matters is that each level catches a **different kind of risk**.

## Properties of Good Tests

Not every test is valuable. If maintenance cost exceeds value, a test becomes a burden. Good tests share four properties:

1. **Fast.** Slow tests get skipped. Unit test suites should finish in seconds.
2. **Deterministic.** Same code must produce the same result every time. Dependence on time, network, or randomness creates flaky tests.
3. **Independent.** Test A's result must not affect Test B. Order-dependent results make debugging extremely difficult.
4. **Clear failure messages.** On failure, the message should show what expectation broke in one line.

```python
# Bad: failure shows only "AssertionError"
def test_bad():
    assert process(data)

# Good: failure shows expected and actual values
def test_good():
    result = process(data)
    assert result.status == "completed", f"Expected completed, got {result.status}"
```

## Practical Advice for Introducing Tests

If you are adding tests to a project that already runs without them, do not try to cover everything at once. This order is realistic:

1. **Start with new code.** Leave existing code untouched for now.
2. **Every time a bug appears,** write a test that reproduces it before fixing.
3. **Before refactoring,** add tests that verify current behavior.
4. **Wire tests into CI.** Running only locally means forgetting. Auto-run on every PR reduces omissions.

Perfect coverage is not the goal. The first goal is the team having the *habit* of running tests.

## Applying the Test Pyramid to a Real Repository

After understanding the concept, the first practical question is "what ratio of tests should our repo have?" Answering abstractly does not help. Translate it into a directory-level plan.

```text
project/
├─ src/
│  ├─ domain/
│  ├─ service/
│  └─ api/
├─ tests/
│  ├─ unit/         # Fast feedback, majority of cases
│  ├─ integration/  # DB, message broker, external API boundaries
│  └─ e2e/          # Critical user journeys only
└─ pyproject.toml
```

In practice, teams typically start with unit tests at 70-85%, integration at 10-20%, and E2E at 5-10% by test count. The absolute ratio varies by project character, but the principle "thick fast tests, thin slow tests" does not change.

```python
# tests/unit/test_tax.py
def test_calculate_vat_for_standard_rate():
    assert calculate_vat(10000, 0.1) == 1000

# tests/integration/test_order_repository.py
def test_save_order_persists_to_db(db_session):
    repo = OrderRepository(db_session)
    order = Order(id='o-1', total=15000)
    repo.save(order)
    assert repo.get('o-1').total == 15000

# tests/e2e/test_checkout_flow.py
def test_checkout_flow(page):
    page.goto('http://localhost:8000')
    page.get_by_role('button', name='Add to Cart').click()
    page.get_by_role('button', name='Checkout').click()
    expect(page.get_by_text('Payment Complete')).to_be_visible()
```

Showing examples at each layer in the same repo lets a new developer quickly understand which kind of risk each layer catches. Test strategy communicates better through file structure than through sentences.

## Fixture Patterns — Start Separating Early

In early projects, preparing test data directly inside each function causes no immediate pain. But once tests exceed 200, setup duplication grows fast, and changing data shapes causes an explosion of edits. Establishing `pytest` fixture patterns from day one is far cheaper long-term.

```python
import pytest

@pytest.fixture
def user_factory():
    def _build(**overrides):
        data = {
            'id': 'u-100',
            'email': 'test@example.com',
            'role': 'member',
            'active': True,
        }
        data.update(overrides)
        return User(**data)
    return _build

def test_admin_permission(user_factory):
    admin = user_factory(role='admin')
    assert can_publish(admin) is True
```

A factory fixture shares default data while allowing per-test variations concisely. Adopting this pattern keeps tests short and reduces edit points when business rules change.

## Coverage Reports as a Compass

Coverage is not a quality scorecard — it is a tool for prioritizing where to invest next. Reading the report like this lets a team agree on "which file to protect first next week."

```bash
pytest --cov=src --cov-report=term-missing
```

```text
Name                       Stmts   Miss  Cover   Missing
---------------------------------------------------------
src/domain/pricing.py         82     19    77%   45-52, 71-79
src/service/order.py         104      6    94%   88-90, 131-133
src/utils/time.py             24      1    96%   18
---------------------------------------------------------
TOTAL                        210     26    88%
```

If `pricing.py` is core domain, the priority is clear: reinforce missing branches in pricing before simple utilities. The point is not the coverage number itself but "which risk did we close first."

## Minimum CI Setup

Tests running only locally rely on human willpower. To solidify them as team quality standards, they must auto-run on every PR. The simplest starting point:

```yaml
name: test
on:
  pull_request:
  push:
    branches: [main]

jobs:
  pytest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements-dev.txt
      - run: pytest -q --maxfail=1
```

Rather than starting with a complex matrix, automate the agreement "unit tests must run on every PR" first. As the project grows, add integration test parallelization, caching, and coverage upload incrementally.

## Operational Perspective on Tests

In production teams, tests are not just verification tools — they are devices that lower the cost of change. To deploy frequently, automatic verification must come before human memory and manual checklists.

Strong teams ask one question first on every PR: not "what did you change?" but "what did you verify?" Without tests, reviewers struggle to understand intent and failure conditions, and post-merge risk rises sharply.

```python
from unittest.mock import patch

def test_payment_service_retries_once_on_timeout():
    service = PaymentService()
    with patch('src.payment.client.charge') as charge:
        charge.side_effect = [TimeoutError(), {'status': 'ok'}]
        result = service.pay(user_id='u-1', amount=10000)

    assert result['status'] == 'ok'
    assert charge.call_count == 2
```

```bash
pytest -q --maxfail=1 --disable-warnings
pytest --cov=src --cov-report=term-missing
```

Fixtures are design tools, not convenience functions. Defining clearly in the fixture layer which objects have which default state and which variations are allowed makes test intent clean. Especially when domain objects are complex, fixture design quality determines test maintenance cost.

To reduce regression bugs, every closed bug ticket should leave a reproduction test behind. Merging only the fix means the same root cause can resurface through a different path. A reproduction test turns team knowledge into an executable asset.

## Five Common Mistakes

1. **Saving tests for *later*.** "Later" becomes *never*.
2. **Cramming *several assertions* into one test, so you cannot tell *what* broke.**
3. **Tests too *slow* to run.** Tests that you do not run are *no tests*.
4. **Test code *more complex than production*.** That itself is a bug.
5. **Treating green `pytest` as *proof of correctness*.** Tests cover *only the cases you wrote*.

## Verification Points

1. Change `add` to `return a - b` and run `pytest -v` again. If nothing fails, the test is not actually guarding the behavior you care about.
2. Read only the test names and check whether you can infer the contract of `add`. If you cannot, the test is also failing as documentation.
3. Record how long `pytest -q` takes. If the very first tests already feel slow, the team will stop running them habitually once the suite grows.

**Expected output:** the intentionally broken version should fail immediately, and the restored implementation should return to a fully green run.

## Failure Signals and First Checks

- If tests stay green after a deliberate bug, your assertions are probably too weak or too narrow.
- If failure messages say only `test_case_1`, rename the tests before the suite grows any further.
- If a beginner example already runs slowly, check for hidden file I/O, network calls, or shared global state.

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

## Answering the Opening Questions

- **What exactly does a test verify?**
  A test records expected behavior in executable form. Unlike manual checks, once written it can be reused continuously—raising both team velocity and confidence in changes simultaneously.
- **How does manual verification differ from automated testing?**
  Manual verification is valid only at that moment; automated tests run again next week, even when someone else touches the code, applying the same criteria. This difference grows more critical as teams scale.
- **How do unit, integration, and E2E tests differ?**
  The three test types differ in verification scope and speed. Fast unit tests solidify core logic, integration tests confirm component connections, and E2E tests validate user flows.

<!-- toc:begin -->
## In this series

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

### Official Docs
- [pytest documentation](https://docs.pytest.org/)
- [Python `unittest` documentation](https://docs.python.org/3/library/unittest.html)

### Practical Reading
- [Martin Fowler — The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Google Testing Blog](https://testing.googleblog.com/)

Tags: Testing, Quality, Software, Basics, Engineering
