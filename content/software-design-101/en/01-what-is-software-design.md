---
series: software-design-101
episode: 1
title: "Software Design 101 (1/10): What Is Software Design?"
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
  - SoftwareDesign
  - Architecture
  - Modularity
  - DesignPrinciples
  - Maintainability
seo_description: Define software design, distinguish it from clean coding, and learn signals of good and failing design across a code base.
last_reviewed: '2026-05-15'
---

# Software Design 101 (1/10): What Is Software Design?

Changing one line is easy. Changing a feature without dragging half the code base with it is where software design starts to matter.

This is the first post in the Software Design 101 series.

In this post, we treat software design not as code prettiness but as a bundle of decisions that determines the cost of the next change. The working question is simple: what signals tell you that a structure will stay changeable six months from now?

> Good code makes one line easier to read; good design makes the whole code base easier to change.

## Questions to Keep in Mind

- What boundary should you inspect first when applying What Is Software Design??
- Which signal should the example or diagram make visible for What Is Software Design??
- What failure should be prevented first when What Is Software Design? reaches a real system?

## Big Picture

![software design 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/software-design-101/01/01-01-concept-at-a-glance.en.png)

*software design 101 chapter 1 flow overview*

This picture places What Is Software Design? inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## What You Will Learn

- A working definition of software design
- Signals that distinguish good design
- The relationship between design and code quality
- Symptoms of design failure
- The time horizon of design

## Why It Matters

Design is invisible. But it shows itself every time the next change is more expensive than expected.

> Design debt always charges interest.

Design determines change cost.

## Key Terms

- **Software design**: A set of decisions about modules, responsibilities, and dependencies.
- **Architecture**: Design decisions at the largest unit.
- **Coupling**: Degree of interdependence between modules.
- **Cohesion**: Degree of relatedness within a module.
- **Change cost**: Time and risk required for the next change.

## Before/After

**Before**

```text
"It just needs to work."
→ Quick first release; painful changes six months later.
```

**After**

```text
"It must remain changeable in six months."
→ Slightly slower first release; smaller cumulative cost.
```

Design is a cumulative cost game.

## Hands-on: Five Signals of Good Design

### Step 1 — Change simulation

```python
# 1_change_sim.py
# "Add a payment method" — how many files would you touch?
files_touched = ["payment.py"]  # one file is a strong signal
```

Smaller change footprint, better design.

### Step 2 — Dependency graph

```python
# 2_deps.py
# A -> B -> C (one direction) is fine.
# A <-> B (cycle) is a design smell.
```

Dependency cycles are nearly always a red flag.

### Step 3 — Module responsibility

```python
# 3_responsibility.py
# If you cannot describe a module in one sentence, its responsibility is fuzzy.
PAYMENT = "Payment domain — calls external gateway and applies domain rules"
```

The name and the one-sentence description must match.

### Step 4 — Testability

```python
# 4_testable.py
# Can the domain module be tested alone, without IO?
def can_test_alone(module):
    return module.no_io and module.no_globals
```

The most honest measure of design quality.

### Step 5 — Onboarding curve

```text
# 5_onboard.txt
Can a new teammate understand a module in 30 minutes?
```

Design is, in the end, a human task.

## Quick Verification

The fastest way to evaluate design is to replay a real change against the code base. Pick a frequent request and write down the actual change footprint, dependency shape, and test scope.

```text
Change scenario: add a payment method
Files touched: 1 / 4 / 9
Dependency cycle: no / yes
Test scope: domain only / domain+DB / full regression
```

**Expected output:** the healthier design touches fewer files, avoids cycles, and keeps the verification scope narrow.

That simple exercise moves the conversation away from “is the code clean?” and toward “how expensive is the next change?”

## Failure Signals and First Checks

| Failure signal | First check |
| --- | --- |
| One feature request forces you through many folders | Find the module boundary where the change leaks |
| A tiny change still demands full regression | Check whether domain rules are glued to IO |
| A new teammate cannot explain the structure quickly | Ask for a one-sentence responsibility per module |

Once you learn to read these early signals, design stops being an abstract aesthetic debate and becomes a cost-control tool.

## What to Notice in This Code

- Change footprint, dependencies, responsibility, and testability viewed together.
- The onboarding curve is the strongest signal.

## Five Common Mistakes

1. **One huge upfront design.** Decisions made without information are usually wrong.
2. **Not measuring change cost.** Design debt becomes invisible.
3. **Tolerating cycles.** They harden over time.
4. **Module responsibility takes more than one sentence.** Cohesion is low.
5. **No record of design decisions.** Same debate repeats forever.

## How This Shows Up in Production

Strong teams keep ADRs (Architecture Decision Records). Decisions and their reasoning are preserved together so new teammates do not relitigate.

## How a Senior Engineer Thinks

- Design is a cumulative cost game.
- Start small and evolve often.
- Validate design with change simulations.
- Record decisions in writing.
- Treat the onboarding curve as a design signal.

## Checklist

- [ ] Can each module be described in one sentence?
- [ ] Are there no dependency cycles?
- [ ] Are change footprints small?
- [ ] Can domain modules be tested in isolation?
- [ ] Are decisions captured as ADRs?

## Practice Problems

1. Draw the module dependency graph of your project.
2. Pick the most frequent change and count the files it touches.
3. Write your last big decision as a one-page ADR.

## Wrap-up and Next Steps

Design decides the cost of the next change. Next we start with the most fundamental tool: separation of concerns.

## Answering the Opening Questions

- **What boundary should you inspect first when applying What Is Software Design??**
  - The article treats What Is Software Design? as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for What Is Software Design??**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when What Is Software Design? reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- **What Is Software Design? (current)**
- Separation of Concerns (upcoming)
- Modules and Boundaries (upcoming)
- Dependency Direction (upcoming)
- Interfaces and Abstraction (upcoming)
- Layered Architecture (upcoming)
- Data Flow Design (upcoming)
- Reducing Change Impact (upcoming)
- Design Principles (upcoming)
- Practicing Design with a Small Project (upcoming)

<!-- toc:end -->

## References

- [A Philosophy of Software Design (J. Ousterhout)](https://web.stanford.edu/~ouster/cgi-bin/aposd.php)
- [Software Architecture Guide (Martin Fowler)](https://martinfowler.com/architecture/)
- [Architecture Decision Records (ADR)](https://adr.github.io/)
- [Designing Data-Intensive Applications](https://dataintensive.net/)

### Practical Docs

- [The Python Tutorial — Modules](https://docs.python.org/3/tutorial/modules.html)
- [unittest.mock — mock object library](https://docs.python.org/3/library/unittest.mock.html)

Tags: Computer Science, SoftwareDesign, Architecture, Modularity, DesignPrinciples, Maintainability
