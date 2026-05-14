---
series: testing-101
episode: 10
title: Building a Test Strategy
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
  - Strategy
  - Quality
  - Capstone
  - Engineering
seo_description: How to build a test strategy that fits your team using the test pyramid and ROI thinking.
last_reviewed: '2026-05-04'
---

# Building a Test Strategy

A team can accumulate a large number of tests and still operate poorly. If every screen gets an E2E scenario, every helper gets a unit test, and CI stretches to half an hour, the suite starts protecting itself more than it protects the product. At that point, the missing piece is not effort. It is strategy.

Strategy is how a team decides where to spend testing cost: which flows deserve E2E coverage, which contracts belong in integration tests, and which logic should be guarded by fast unit tests that run on every change.

This is the final post in the Testing 101 series. Here we connect the earlier layers into one operating model and focus on how to keep test investment aligned with risk, team speed, and maintenance reality.

> Test strategy is not about proving you test a lot. It is about proving you spend testing effort where failure would hurt most.

## What You Will Learn

- The meaning and distribution of the *test pyramid*
- *ROI* per layer and *investment priorities*
- The *team rituals* that keep tests alive
- *Contract tests* at system boundaries
- Five common pitfalls

## Why It Matters

Tests are *not free*. They cost time to write, to run, and to fix. A strategy-less suite becomes a *slow, brittle net*.

> A good strategy *catches bugs while protecting development speed*.

## Concept at a Glance

![Concept at a Glance](../../../assets/testing-101/10/10-01-concept-at-a-glance.en.png)

*Concept at a Glance*
## Key Terms

- **Test pyramid**: a distribution model with *many unit / fewer integration / even fewer E2E* tests.
- **ROI**: the *cost vs. bugs caught* per test.
- **Critical path**: the *money-flow paths* (payment, login, etc.).
- **Contract test**: validates *input/output shape* at *system boundaries*.
- **Flaky budget**: the *acceptable instability ratio* (e.g., 0.5%).

## Before/After

**Before (no strategy)**

```text
- *Unit tests* on every function
- *E2E tests* on every scenario
- 30-minute CI, team PR velocity stalls
```

**After (strategy applied)**

```text
- *2,000 unit tests* on the core domain
- *200 integration tests* (DB and external APIs)
- *20 E2E tests* on critical paths (payment, login, etc.)
- CI under 5 minutes
```

## Hands-on: Five Steps to a Strategy

### Step 1 - Measure the current distribution

```bash
pytest --collect-only -q | wc -l    # total test count
ls tests/unit | wc -l
ls tests/integration | wc -l
ls tests/e2e | wc -l
```

### Step 2 - Define the critical paths

```text
- Login
- Payment
- Sign-up
- Password reset
```

These flows *must be protected by E2E*.

### Step 3 - Add contract tests at the boundary

```python
# tests/contracts/test_payment_api.py
def test_payment_response_schema():
    res = payment_client.charge(amount=100)
    assert set(res.keys()) >= {"id", "status", "amount"}
```

### Step 4 - Establish team rituals

```text
- PR template: "Did you add a regression test? [ ]"
- Weekly 30 minutes: review *flaky tests*
- Monthly: check coverage *trend* (trend, not absolute)
```

### Step 5 - Quarterly pruning

```bash
# E2E that has not failed for six months is a candidate for review
# Tests that fail repeatedly in the same area are *a refactoring signal*
```

## What to Notice in This Code

- A strategy survives as *rituals*, not as *documents*.
- *Distribution* is unknowable without measurement.
- If *critical paths* are not defined, *everything* becomes critical.

## Five Common Mistakes

1. **The same test intensity *for all code*.** Invest in proportion to *risk*.
2. **Treating E2E as the *primary tier*.** It is slow and brittle and *kills team speed*.
3. **Watching only the *coverage target*.** What you *cover* matters more than the number.
4. **No contract tests.** External API changes get caught *in production*.
5. **Setting the strategy *once and forgetting it*.** Revisit *quarterly*.

## Verification Points

1. Write down the current counts and runtime for unit, integration, and E2E tests. A strategy cannot improve a distribution you have never measured.
2. Pick three business-critical flows—such as login, payment, and password reset—and mark which layer protects each one today.
3. Review the last quarter’s flaky tests and CI duration together to decide whether any layer is overgrown or misplaced.

**Expected output:** the strategy discussion should produce explicit investment priorities, not a generic desire to increase tests everywhere.

## Failure Signals and First Checks

- If all code gets the same test intensity, teams eventually work around the cost instead of benefiting from the protection.
- If E2E count keeps rising without reducing major incidents, the layer placement is probably wrong.
- If flaky rate and CI duration are not measured, there is no feedback loop to tell you whether the strategy is improving.

## How This Shows Up in Production

Mature teams record their *target distribution* and *flaky budget* in an *Engineering Excellence* document. Every new service follows that baseline, and *quarterly OKRs* include *CI duration* and *flaky ratio*.

## How a Senior Engineer Thinks

- Test on a *risk basis*. Do not distribute evenly.
- *Fast feedback* is the basis of *every decision*.
- *Contract tests* at the boundary reduce *cross-team cost*.
- A *flaky test* is a *broken window*. Fix it immediately.
- A strategy is a *living document*.

## Checklist

- [ ] You know your team's *test distribution*.
- [ ] *Critical paths* are *documented*.
- [ ] The *PR template* includes a regression test item.
- [ ] You *measure* the *flaky ratio*.

## Practice Problems

1. Measure your project's *test distribution* and verify it forms a *pyramid*.
2. Define three *critical paths* and confirm E2E covers them.
3. Propose one *weekly ritual* to introduce to your team.

## Wrap-up and Next Steps

Test strategy is not *technique* but *decision-making*. With this we close out Testing 101 — next, in *DevOps 101* and *Observability 101*, we extend quality work into *post-deployment*.

<!-- toc:begin -->
- [What is testing?](./01-what-is-testing.md)
- [Unit Test](./02-unit-test.md)
- [Integration Test](./03-integration-test.md)
- [E2E Test](./04-e2e-test.md)
- [Test Doubles](./05-test-double.md)
- [Mock and Stub](./06-mock-and-stub.md)
- [Test Coverage](./07-test-coverage.md)
- [Regression Test](./08-regression-test.md)
- [Running Tests in CI](./09-tests-in-ci.md)
- **Building a Test Strategy (current)**
<!-- toc:end -->

## References

### Official Docs
- [GitHub documentation for pull request templates](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-issue-and-pull-request-templates)
- [Pact contract testing guides](https://docs.pact.io/)

### Practical Reading
- [Martin Fowler — The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Accelerate (Forsgren, Humble, Kim)](https://itrevolution.com/product/accelerate/)
- [ThoughtWorks — Test Strategy](https://www.thoughtworks.com/insights/blog/testing-strategy)

Tags: Testing, Strategy, Quality, Capstone, Engineering
