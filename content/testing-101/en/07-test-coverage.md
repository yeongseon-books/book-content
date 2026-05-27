---
series: testing-101
episode: 7
title: "Testing 101 (7/10): Test Coverage"
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
  - Coverage
  - pytest-cov
  - Quality
  - Metrics
seo_description: Line, branch, and function coverage explained, how to measure with pytest-cov, and why 100% coverage can be dangerous.
last_reviewed: '2026-05-04'
---

# Testing 101 (7/10): Test Coverage

Ask a team how much they tested, and someone will usually answer with a percentage. That number is useful—but only up to the point where people start mistaking execution for verification. A line can run without the test proving anything meaningful about it.

Coverage helps when it reveals blind spots. It hurts when it becomes a vanity metric that rewards shallow tests and distracts from risky branches or exception paths.

This is the 7th post in the Testing 101 series. Here we separate line, branch, and function coverage, run `pytest-cov`, and focus on how to turn a report into better decisions rather than prettier dashboards.

> Coverage is a dashboard light. It tells you where to inspect, not what conclusion to declare.


![testing 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/testing-101/07/07-01-concept-at-a-glance.en.png)
*testing 101 chapter 7 flow overview*
> Coverage is a diagnostic tool that reveals blind spots — not a scorecard that proves correctness.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Test Coverage?
- Which signal should the example or diagram make visible for Test Coverage?
- What failure should be prevented first when Test Coverage reaches a real system?

## What You Will Learn

- The difference between *line/branch/function* coverage
- How to *measure* with `pytest-cov`
- A workflow to find *uncovered code*
- *Why 100% coverage* can be dangerous
- How to set a sensible target

## Why It Matters

If you do not know *where tests reach*, incidents happen in the *blind spots*. At the same time, tests written *just to raise the number* create *false safety*.

> Coverage is a *compass*, not a *map*.

## Concept at a Glance
Coverage measures which lines, branches, and functions tests execute, using tools like pytest-cov, and reveals untested code paths—branches, exception handlers, edge cases—that manual inspection might miss, though high percentage coverage can hide shallow tests.
## Key Terms

- **Line coverage**: ratio of *executed lines / total lines*.
- **Branch coverage**: whether *both sides* of branches like if/else were executed.
- **Function coverage**: ratio of *called functions*.
- **Uncovered**: code that tests *never* executed.
- **Coverage gate**: CI fails if coverage falls below *the minimum*.

## Before/After

**Before (no coverage)**

```text
- All you know is "we have many tests"
- No idea which lines were *never executed*
```

**After (coverage report)**

```text
src/payment.py: 78% (line 42, 57 uncovered)
src/auth.py: 92% (line 11 uncovered)
TOTAL: 84%
```

## Hands-on: pytest-cov in Five Steps

### Step 1 — Install

```bash
pip install pytest-cov
```

### Step 2 — Measure

```bash
pytest --cov=src --cov-report=term-missing
```

```text
src/calc.py    24    2    92%   18-19
src/auth.py    50   10    80%   34, 41-49
TOTAL         200   18    91%
```

### Step 3 — HTML report

```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

The red lines are *the untested ones*.

### Step 4 — Branch coverage

```bash
pytest --cov=src --cov-branch --cov-report=term-missing
```

This shows whether *both True and False* of `if x > 0:` were covered.

### Step 5 — Gate (enforce in CI)

```toml
# pyproject.toml
[tool.coverage.report]
fail_under = 80
```

```bash
pytest --cov=src
# Coverage failure: total of 78 is less than fail_under=80
```

## What to Notice in This Code

- Line coverage only looks at *execution* (value verification is separate).
- *Branch coverage* is a more honest signal.
- The HTML report shows *the gaps* at a glance.

## Five Common Mistakes

1. **Setting *100%* as a KPI.** It floods you with *meaningless tests*.
2. **Inflating coverage with *no assertions*.** Code is *executed* but not *verified*.
3. **Including *generated/migration/experimental code* in measurement.** Just noise.
4. **Ignoring *branch coverage*.** Testing only one side of an if-else still gives *100% line*.
5. **Holding *new code and legacy code* to the *same gate*.** Improvement becomes hard.

## Verification Points

1. Run `pytest --cov=src --cov-report=term-missing` and inspect two or three uncovered lines in the source itself. The point is to read the gap, not just the percentage.
2. Re-run the same suite with `--cov-branch` and compare the numbers. The distance between line and branch coverage usually teaches more than the headline percentage.
3. Add a small new exception path and confirm that the coverage report notices it. That is how you verify the CI gate is watching real change.

**Expected output:** the report should make missing branches and exception paths more visible than the total percentage alone.

## Failure Signals and First Checks

- High line coverage with recurring incidents often means weak assertions or missing branch checks.
- Measuring generated files or migrations together with core logic inflates the number and lowers the signal.
- If one hard gate blocks both new and legacy code indiscriminately, teams often start gaming the metric instead of improving it.

## How This Shows Up in Production

Most teams aim for *70\~85% on production code*. Core domain stays *high*; adapters and UI sit *lower*. Many add a separate gate on *patch coverage* (coverage of changed lines).

## How a Senior Engineer Thinks

- Treats coverage as *a diagnostic, not an outcome metric*.
- Looks at *the gaps* and asks *why* they are gaps.
- Keeps *new code coverage high* while *legacy improves gradually*.
- *Prioritizes* branches and exception paths.
- Accepts that 100% can have *low ROI*.

## Checklist

- [ ] You looked at a `pytest --cov` report once.
- [ ] You inspected *red lines* in the HTML report.
- [ ] You enabled *branch coverage*.
- [ ] CI has a *minimum coverage* gate.

## Practice Problems

1. Find the *file with the lowest coverage* in your project.
2. Write *why it is low* in one line and propose *three tests* to add.
3. Compare the *numerical gap* between line and branch coverage.

## Wrap-up and Next Steps

Coverage is a *health signal*, not *health itself*. The next post covers *regression tests* — making sure the same bug *does not come back*.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Test Coverage?**
  - The article treats Test Coverage as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Test Coverage?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Test Coverage reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Testing 101 (1/10): What Is Testing?](./01-what-is-testing.md)
- [Testing 101 (2/10): Unit Test](./02-unit-test.md)
- [Testing 101 (3/10): Integration Test](./03-integration-test.md)
- [Testing 101 (4/10): E2E Test](./04-e2e-test.md)
- [Testing 101 (5/10): Test Double](./05-test-double.md)
- [Testing 101 (6/10): Mock and Stub](./06-mock-and-stub.md)
- **Test Coverage (current)**
- Regression Test (upcoming)
- Running Tests in CI (upcoming)
- Building a Test Strategy (upcoming)

<!-- toc:end -->

## References

- [pytest-cov docs](https://pytest-cov.readthedocs.io/)
- [coverage.py docs](https://coverage.readthedocs.io/)
- [Martin Fowler — Test Coverage](https://martinfowler.com/bliki/TestCoverage.html)
- [Google Testing Blog — Code Coverage Best Practices](https://testing.googleblog.com/2020/08/code-coverage-best-practices.html)

Tags: Testing, Coverage, pytest-cov, Quality, Metrics
