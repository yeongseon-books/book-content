---
series: software-engineering-101
episode: 9
title: "Software Engineering 101 (9/10): Maintenance and Tech Debt"
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
  - Maintenance
  - TechDebt
  - Refactoring
  - Legacy
seo_description: The four types of tech debt, how to prioritize repayment, safe refactoring, and a phased deprecation procedure you can copy.
last_reviewed: '2026-05-15'
---

# Software Engineering 101 (9/10): Maintenance and Tech Debt

Every codebase gets awkward over time. A quick branch added under pressure, a duplicated workflow, an interface nobody wants to touch, a module that resists testing. Teams often respond with a vague promise to "clean it up later." Usually that later never arrives until a deadline slips or an incident forces the issue.

Tech debt is not automatically a failure. Sometimes it is a conscious trade: speed now, cleanup later. The dangerous version is debt without explicit ownership, measurement, or repayment intent. That kind of debt quietly taxes reliability, lead time, and team confidence all at once.

This is post 9 in the Software Engineering 101 series. In this chapter, we classify debt, prioritize repayment, and use phased replacement and deprecation patterns to keep maintenance work recoverable.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Maintenance and Tech Debt?
- Which signal should the example or diagram make visible for Maintenance and Tech Debt?
- What failure should be prevented first when Maintenance and Tech Debt reaches a real system?

## Big Picture

![software engineering 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/software-engineering-101/09/09-01-concept-at-a-glance.en.png)

*software engineering 101 chapter 9 flow overview*

This picture places Maintenance and Tech Debt inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## What You Will Learn

- The four types of tech debt (Martin Fowler's quadrant)
- How to prioritize debt repayment
- A safe refactoring procedure
- Phased deprecation
- Treating debt as a measurable signal

## Why It Matters

There is no codebase without debt. The question is whether you are aware of it, measuring it, and paying it down.

> Debt is not the problem. Unconscious debt is.

Debt is a cycle, not an event.

## Key Terms

- **Deliberate-Prudent**: Conscious decision with a plan to pay it off.
- **Deliberate-Reckless**: Knowingly irresponsible.
- **Inadvertent-Prudent**: Debt from inexperience, paid off by learning.
- **Inadvertent-Reckless**: Unaware and irresponsible — the most dangerous.
- **Deprecation**: Phased retirement of an interface.

## Before/After

**Before — "all at once later"**

```text
big-bang refactor at month 12 -> incidents + schedule blow-up
```

**After — 5% per quarter**

```text
5% of each sprint, measured, prioritized -> incremental improvement
```

Small and frequent is safe.

## Hands-on: Treat Debt as Code

### Step 1 — Debt label

```python
# 1_label.py
# DEBT(billing): tax computation leaks into PaymentService
# Due: 2026 Q3, owner: @alice
def charge(amount): ...
```

Debt needs a due date and an owner.

### Step 2 — Debt index

```markdown
# 2_index.md
| ID | Area | Severity | Owner | Due |
|----|------|----------|-------|-----|
| D-12 | billing | high | alice | 2026 Q3 |
| D-13 | auth | mid | bob | 2026 Q4 |
```

Only searchable debt is payable debt.

### Step 3 — Strangler Fig pattern

```python
# 3_strangler.py
def charge(amount):
    if feature("new_billing"):
        return new_billing.charge(amount)
    return legacy.charge(amount)
```

Replace incrementally with a feature flag.

### Step 4 — Deprecation phases

```python
# 4_deprecate.py
import warnings
def old_api(*a, **kw):
    warnings.warn("old_api is deprecated; use new_api", DeprecationWarning, stacklevel=2)
    return new_api(*a, **kw)
```

Warn -> trace callers -> remove (one phase per quarter).

### Step 5 — Debt metrics dashboard

```text
# 5_metrics.md
- Average cyclomatic complexity
- Test coverage delta
- Debt items closed per sprint
- Mean time to recovery (MTTR) on incidents
```

What you do not measure, you do not pay.

## A debt-management check

Debt becomes manageable when it is specific enough to own, time-box, and replace safely. Pick one risky module and describe its debt in a way that could survive beyond the current conversation.

### Verification steps

1. Choose one module tied to a recent incident or slow change.
2. Add the debt item to an index with owner, severity, and due window.
3. Write the first incremental replacement step using a feature-flag or strangler pattern.

**Expected output:**

- The debt item becomes a prioritizable object instead of background frustration.
- The safe first step is smaller than the emotional desire for a total rewrite.
- Deprecation starts looking like a staged operational process, not a one-shot deletion.

### Failure modes to watch

- The only record is a vague TODO with no owner or due date.
- The team cannot connect debt to incidents, lead time, or recovery cost.
- "We will clean it all up later" is the only plan on the table.

## What to Notice in This Code

- Debt has a due date and an owner.
- The Strangler Fig pattern is recoverable replacement.
- Deprecation is phased and measurable.
- Without metrics, debt is forgotten.

## Five Common Mistakes

1. **Big-bang refactor.** A leading cause of incidents.
2. **No debt label.** Unsearchable, unpayable.
3. **Removing a deprecated API immediately.** Callers break.
4. **Blaming people for debt.** Debt is a system outcome.
5. **No debt metric.** Unmeasured, unprioritized.

## How This Shows Up in Production

Mature teams allocate 10~20% of sprint capacity to debt repayment. Strangler Fig + feature flags enable zero-downtime replacement. The debt index is reviewed each quarter.

## How a Senior Engineer Thinks

- Debt is a cycle, not an event.
- Deliberate debt is a tool, unconscious debt is an incident.
- Debt without a due date becomes permanent.
- Incremental beats big-bang almost every time.
- Only what you measure gets paid.

## Checklist

- [ ] Is there a debt index?
- [ ] Does each debt item have an owner and a due date?
- [ ] Is sprint capacity allocated to debt?
- [ ] Are deprecation phases defined?
- [ ] Do debt metrics live on a dashboard?

## Practice Problems

1. Label five debt items in your repo.
2. Decompose your most dangerous debt item using Strangler Fig.
3. Define five debt-metric items for a dashboard.

## Wrap-up and Next Steps

Debt is a cycle. Be aware, measure, pay down each quarter. The final episode ties it all together — what makes good software.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Maintenance and Tech Debt?**
  - The article treats Maintenance and Tech Debt as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Maintenance and Tech Debt?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Maintenance and Tech Debt reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Software Engineering 101 (1/10): What Is Software Engineering?](./01-what-is-software-engineering.md)
- [Software Engineering 101 (2/10): Understanding Requirements](./02-understanding-requirements.md)
- [Software Engineering 101 (3/10): Design vs Implementation](./03-design-vs-implementation.md)
- [Software Engineering 101 (4/10): Code Review](./04-code-review.md)
- [Software Engineering 101 (5/10): Testing Strategy](./05-testing-strategy.md)
- [Software Engineering 101 (6/10): Version Control and Release](./06-version-control-and-release.md)
- [Software Engineering 101 (7/10): Documentation](./07-documentation.md)
- [Software Engineering 101 (8/10): Collaboration Process](./08-collaboration-process.md)
- **Maintenance and Tech Debt (current)**
- What Makes Good Software (upcoming)

<!-- toc:end -->

## References

- [Martin Fowler — Technical Debt Quadrant](https://martinfowler.com/bliki/TechnicalDebtQuadrant.html)
- [Martin Fowler — StranglerFigApplication](https://martinfowler.com/bliki/StranglerFigApplication.html)
- [Refactoring — Martin Fowler](https://martinfowler.com/books/refactoring.html)
- [Working Effectively with Legacy Code — Michael Feathers](https://www.oreilly.com/library/view/working-effectively-with/0131177052/)

Tags: Computer Science, SoftwareEngineering, Maintenance, TechDebt, Refactoring, Legacy
