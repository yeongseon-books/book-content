---
series: software-engineering-101
episode: 10
title: "Software Engineering 101 (10/10): What Makes Good Software"
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
  - Quality
  - SOLID
  - Simplicity
  - Engineering
seo_description: Quality attributes, SOLID, simplicity, sustainability, and the external signals senior engineers actually look at.
last_reviewed: '2026-05-15'
---

# Software Engineering 101 (10/10): What Makes Good Software

A working feature and good software are not the same thing. Shipping the feature is only the opening move. The harder question is whether the system still behaves well when requirements change, teammates rotate, traffic grows, and incidents force trade-offs under pressure.

Teams often judge quality first by style or abstraction. Those signals matter, but the stronger truth usually appears outside the code: lead time, recovery speed, onboarding friction, user trust, and the ease of safe change. Quality lives at the intersection of internal structure and external behavior.

This is the final post in the Software Engineering 101 series. In this chapter, we tie the series together by looking at quality attributes, practical readings of SOLID, and the operational signals senior engineers use when they say a system is healthy.


![software engineering 101 chapter 10 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/software-engineering-101/10/10-01-concept-at-a-glance.en.png)
*software engineering 101 chapter 10 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying What Makes Good Software?
- Which signal should the example or diagram make visible for What Makes Good Software?
- What failure should be prevented first when What Makes Good Software reaches a real system?

## What You Will Learn

- Quality attributes (a short take on ISO/IEC 25010)
- The one-line meaning of each SOLID principle
- The link between simplicity and sustainability
- Four external signals of a healthy system
- The single thing senior engineers look at last

## Why It Matters

A working feature is the start, not the end. Good software endures over time and grows the people who work on it.

> What is simple lasts.

Quality is not one axis but a balance across many.

## Key Terms

- **Functional suitability**: Meets the requirement correctly.
- **Reliability**: Predictable failure rate.
- **Maintainability**: Cost of change.
- **Performance efficiency**: Throughput per resource.
- **SOLID**: Five principles of OO design.

## Before/After

**Before — feature-only**

```text
"It works" is the only metric -> change cost explodes in 6 months
```

**After — measure quality attributes**

```text
lead time, incident rate, MTTR, maintainability score -> decisions become possible
```

You only improve what you measure.

## Hands-on: A Small Quality Kit

### Step 1 — SRP check (the S in SOLID)

```python
# 1_srp.py
class Invoice:           # responsibility 1: data
    ...
class InvoicePrinter:    # responsibility 2: rendering
    ...
```

One class, one reason to change.

### Step 2 — DIP check (the D in SOLID)

```python
# 2_dip.py
class OrderService:
    def __init__(self, repo: "Repo"):  # depends on the interface
        self.repo = repo
```

Depend on abstractions, not on concretions.

### Step 3 — Measure simplicity

```bash
# 3_complexity.sh
radon cc app/ -a -nb
```

If complexity passes a threshold, decompose.

### Step 4 — Measure lead time

```bash
# 4_lead_time.sh
git log --pretty='%H %as' -- app/ | head
```

Track time from code to deploy.

### Step 5 — Four external signals

```text
# 5_signals.md
- Time to a new hire's first PR
- MTTR on incidents
- Average lead time for new features
- User satisfaction (NPS, CSAT)
```

External signals tell more truth than internal code metrics.

## A quality-signal check

The fastest way to make quality actionable is to convert it from taste into signals. Pick one weak quality attribute in your current system and pair it with one internal metric and one external outcome.

### Verification steps

1. Choose the weakest current axis such as reliability or maintainability.
2. Name one internal signal and one external signal that expose that weakness.
3. Define a baseline and one quarter-scale improvement target.

**Expected output:**

- Quality discussions shift from preference to evidence.
- Complexity, lead time, MTTR, and onboarding speed start to connect to each other.
- SOLID principles become tools for reducing change cost instead of slogans.

### Failure modes to watch

- The team measures feature output only.
- Internal code style stands in for user and operational reality.
- Metrics exist, but no review cadence turns them into decisions.

## What to Notice in This Code

- One class, one reason to change.
- Depending on abstractions decides change cost.
- Complexity is measurable.
- External signals carry the truth about quality.

## Five Common Mistakes

1. **Measuring features only.** Change cost explodes soon.
2. **Treating SOLID as dogma.** Principles are tools, not faith.
3. **Too much abstraction.** Simplicity dies.
4. **Ignoring external signals.** User trust is the real metric.
5. **Quality at the end.** Measure from day one.

## How This Shows Up in Production

Strong teams track DORA's four metrics (deploy frequency, lead time, change failure rate, MTTR) and review them quarterly. New features call out their quality-attribute impact (reliability/security) explicitly.

## How a Senior Engineer Thinks

- What is simple lasts.
- SOLID is a tool, not a religion.
- External signals are closer to truth.
- Quality is measured from day one.
- Good software grows the people who work on it.

## Checklist

- [ ] Do you know the six quality attributes?
- [ ] Do you measure DORA's four metrics?
- [ ] Are complexity and lead time on a dashboard?
- [ ] Do you treat SOLID as a tool, not a creed?
- [ ] Do you review external signals each quarter?

## Practice Problems

1. Estimate the current values of DORA's four metrics for your project.
2. Find one SOLID violation and rewrite it through an SRP or DIP lens.
3. Define four external signals for your own system.

## Wrap-up and Next Steps

Good software is simple, measurable, and grows the people who maintain it. This series ends here, but the principles from these ten essays deepen further in the next series — Clean Code, Design Patterns, API Design, and beyond.

## Answering the Opening Questions

- **Why aren't "good code" and "good software" the same thing?**
  Good code means readable, well-separated responsibility at the class/function level. Good software means that code translates over time into low lead time, short MTTR, and fast onboarding. That's why this article emphasized looking at external signals—complexity, deployment lead time, new-hire first-PR time—beyond `It works`.
- **Along which axes do quality attributes split, and why does balance matter?**
  The article separated functional suitability, reliability, maintainability, and performance efficiency, while the quality criteria table also bundled changeability, operational stability, collaboration transparency, and learnability. Pushing one axis collapses another, so managing different quality targets simultaneously (availability 99.9%, p95 300ms, MTTR under 30 minutes) maintains balance.
- **How should SOLID principles be read in practice?**
  The SRP and DIP examples showed SOLID should be read as judgment tools for reducing change cost, not memorization subjects. The moment multiple change reasons pile into one class or it directly couples to concrete implementations, maintainability drops—principles serve as criteria for reading which boundaries are change-prone.

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
- [Software Engineering 101 (9/10): Maintenance and Tech Debt](./09-maintenance-and-tech-debt.md)
- **What Makes Good Software (current)**

<!-- toc:end -->

## References

- [ISO/IEC 25010 — Product Quality Model](https://iso25000.com/index.php/en/iso-25000-standards/iso-25010)
- [Robert C. Martin — SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [DORA — State of DevOps](https://dora.dev/)
- [A Philosophy of Software Design — John Ousterhout](https://web.stanford.edu/~ouster/cgi-bin/aposd.php)

Tags: Computer Science, SoftwareEngineering, Quality, SOLID, Simplicity, Engineering
