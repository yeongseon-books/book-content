---
series: software-engineering-101
episode: 5
title: "Software Engineering 101 (5/10): Testing Strategy"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - SoftwareEngineering
  - Testing
  - TestPyramid
  - CI
  - Quality
seo_description: The roles of unit, integration, and E2E tests, the test pyramid, the coverage trap, and how to keep CI fast.
last_reviewed: '2026-05-15'
---

# Software Engineering 101 (5/10): Testing Strategy

Most teams agree that tests matter. Disagreement starts immediately after that. Should you invest harder in unit tests, rely on integration tests, or trust end-to-end coverage because it looks closest to production? Without a strategy, test suites grow in the most expensive direction: slower feedback, shakier trust, and harder debugging.

The real problem is not test quantity. It is test placement. A healthy test system tells you where to look when something breaks, keeps PR feedback short enough to preserve flow, and treats flaky tests as defects in the delivery system rather than background noise.

This is post 5 in the Software Engineering 101 series. In this chapter, we use the test pyramid as a decision tool, then connect it to verification speed, expected output, and the failure modes that make CI untrustworthy.


![software engineering 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/software-engineering-101/05/05-01-concept-at-a-glance.en.png)
*software engineering 101 chapter 5 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Testing Strategy?
- Which signal should the example or diagram make visible for Testing Strategy?
- What failure should be prevented first when Testing Strategy reaches a real system?

## What You Will Learn

- The role of unit, integration, and E2E tests
- The test pyramid and its inverse, the ice cream cone
- When coverage lies
- How to keep tests fast in CI
- How to fix flaky tests instead of muting them

## Why It Matters

Tests determine the cost of change. Good tests let you refactor without fear; bad tests make every PR a hesitation.

> Code without tests is, in practice, frozen code.

The pyramid balances cost against speed.

## Key Terms

- **Unit test**: Function or class scope, no external dependency.
- **Integration test**: Multiple components working together.
- **E2E test**: Real user scenario, slowest layer.
- **Flaky test**: Same code, sometimes red, sometimes green.
- **Coverage**: Percentage of code executed by tests, not a quality metric.

## Before/After

**Before — ice cream cone**

```text
E2E 80%, integration 15%, unit 5%
-> slow CI, flaky tests, debugging hell
```

**After — pyramid**

```text
unit 70%, integration 25%, E2E 5%
-> fast CI, clear failure location
```

Change the ratio and the team speeds up.

## Hands-on: Build a Small Pyramid

### Step 1 — Unit test

```python
# 1_unit.py
def add(a: int, b: int) -> int:
    return a + b

def test_add():
    assert add(2, 3) == 5
```

Fastest layer, the most of them.

### Step 2 — Integration with a fake

```python
# 2_integration.py
class FakeRepo:
    def __init__(self): self.items = []
    def save(self, x): self.items.append(x)

def test_service_uses_repo():
    repo = FakeRepo()
    service = OrderService(repo)
    service.create({"id": 1})
    assert repo.items == [{"id": 1}]
```

Fakes break less than mocks.

### Step 3 — E2E for scenarios only

```python
# 3_e2e.py
def test_checkout_flow(client):
    client.post("/cart", json={"sku": "A"})
    r = client.post("/checkout")
    assert r.status_code == 200
```

Critical user journeys only, kept few.

### Step 4 — Split CI for speed

```yaml
# 4_ci.yml
jobs:
  unit:
    steps: [{ run: pytest tests/unit -q }]
  integration:
    steps: [{ run: pytest tests/integration -q }]
  e2e:
    if: github.ref == 'refs/heads/main'
    steps: [{ run: pytest tests/e2e -q }]
```

Some teams gate E2E only on main.

### Step 5 — Quarantine flaky tests

```python
# 5_flaky.py
import pytest
@pytest.mark.flaky(reruns=2)
def test_uses_external_clock(): ...
```

Quarantine, then fix next sprint. Do not mute.

## A confidence-oriented test check

Test strategy is easier to judge from feedback speed and diagnosability than from raw counts. Take one recent CI failure and see how quickly the suite told you where to look.

### Verification steps

1. Pick one recent failing build and note whether it failed in unit, integration, or E2E.
2. Measure how long it took to identify the real cause.
3. Ask whether the same behavior could have been asserted at a lower layer.

**Expected output:**

- A healthy pyramid narrows the search space immediately.
- Too much E2E weight translates into long debugging loops.
- Flaky tests stand out as delivery-system defects, not mere annoyances.

### Failure modes to watch

- Coverage is high, but no one can explain where to start debugging.
- PR feedback time is long enough to change merge behavior.
- Red builds are ignored because the team expects to hit rerun anyway.

## What to Notice in This Code

- Unit tests are most numerous and fastest.
- Fakes are more stable than mocks.
- E2E is scenario-driven and small in count.
- Splitting CI shortens feedback time.

## Five Common Mistakes

1. **Coverage as a goal.** Coverage is an outcome, not a target.
2. **Mocking everything.** A leading cause of flaky tests.
3. **Doing unit work via E2E.** Slow and hard to debug.
4. **Ignoring flakies.** Trust collapses, everyone hits rerun.
5. **Deleting tests to merge.** Defects do not vanish, only the metric does.

## How This Shows Up in Production

Fast teams gate every PR on unit and integration tests, run E2E on main merge or nightly. They set an SLO for test runtime (for example PR < 5 min) and split or parallelize when it slips.

## How a Senior Engineer Thinks

- Tests are both spec and safety net.
- Fast units mean fast change.
- Fakes teach you the code.
- A flaky test is fixed, not muted.
- Change safety beats coverage numbers.

## Checklist

- [ ] Do you know your pyramid ratio?
- [ ] Is PR test time under 5 minutes?
- [ ] Is there a flaky-test tracking board?
- [ ] Do you prefer fakes over mocks?
- [ ] Can you measure change safety?

## Practice Problems

1. Find a function whose external dependency can be replaced by a fake.
2. Take your slowest E2E test and split it into unit and integration tests.
3. Run a 5-Whys on the most recent flaky test.

## Wrap-up and Next Steps

Tests determine the cost of change. Next we look at how to ship tested code safely to users — version control and release.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Testing Strategy?**
  - The article treats Testing Strategy as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Testing Strategy?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Testing Strategy reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Software Engineering 101 (1/10): What Is Software Engineering?](./01-what-is-software-engineering.md)
- [Software Engineering 101 (2/10): Understanding Requirements](./02-understanding-requirements.md)
- [Software Engineering 101 (3/10): Design vs Implementation](./03-design-vs-implementation.md)
- [Software Engineering 101 (4/10): Code Review](./04-code-review.md)
- **Testing Strategy (current)**
- Version Control and Release (upcoming)
- Documentation (upcoming)
- Collaboration Process (upcoming)
- Maintenance and Tech Debt (upcoming)
- What Makes Good Software (upcoming)

<!-- toc:end -->

## References

- [Martin Fowler — Test Pyramid](https://martinfowler.com/bliki/TestPyramid.html)
- [Google Testing Blog — Just Say No to More End-to-End Tests](https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html)
- [Pytest Docs](https://docs.pytest.org/)
- [Working Effectively with Legacy Code — Michael Feathers](https://www.oreilly.com/library/view/working-effectively-with/0131177052/)

Tags: Computer Science, SoftwareEngineering, Testing, TestPyramid, CI, Quality
