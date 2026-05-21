---
series: software-engineering-101
episode: 3
title: "Software Engineering 101 (3/10): Design vs Implementation"
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
  - Design
  - Architecture
  - Implementation
  - Tradeoff
seo_description: A short, code-first take on design vs implementation, capturing decisions in ADRs, and avoiding over-engineering.
last_reviewed: '2026-05-15'
---

# Software Engineering 101 (3/10): Design vs Implementation

Sometimes you review a change and think, "The code is clean, but the structure still feels fragile." Other times the code itself is ordinary, yet the boundaries are so clear that the system looks like it will survive years of change. That difference usually comes from design quality more than implementation polish.

Treat design and implementation as the same activity, and the important decisions disappear into the code. Responsibility boundaries, reversibility, failure handling, and trade-offs stop being explicit choices and start becoming accidental side effects. That is how teams end up with a lot of code and very little shared reasoning.

This is post 3 in the Software Engineering 101 series. In this chapter, we separate the questions design answers from the questions implementation answers, then use ADRs and small examples to show how to keep that boundary visible.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Design vs Implementation?
- Which signal should the example or diagram make visible for Design vs Implementation?
- What failure should be prevented first when Design vs Implementation reaches a real system?

## Big Picture

![software engineering 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/software-engineering-101/03/03-01-concept-at-a-glance.en.png)

*software engineering 101 chapter 3 flow overview*

This picture places Design vs Implementation inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## What You Will Learn

- Definitions of design and implementation
- ADR (Architecture Decision Record)
- How to capture trade-offs in writing
- Five signs of good design
- How to avoid over-engineering

## Why It Matters

Design decisions outlive code. Bad design cannot be hidden under good code.

> Code can be rewritten; the trace of decisions follows you forever.

Design sets the ceiling for implementation.

## Key Terms

- **Design**: deciding components, responsibilities, boundaries, and interfaces.
- **Implementation**: realizing those decisions in code.
- **ADR**: a short document of one decision and its reasoning.
- **Trade-off**: what you gain and what you give up.
- **YAGNI**: do not build what you do not need today.

## Before/After

**Before — Designing inside the code**

```text
"Just code it and refactor later" -> decisions hide in the code
```

**After — ADR makes it explicit**

```text
Options A/B/C, choice + reason, reversibility -> simpler code
```

When design is visible, code becomes simpler.

## Hands-on Step by Step

### Step 1 — Interface First

```python
# 1_iface.py
from typing import Protocol

class Notifier(Protocol):
    def send(self, user_id: str, body: str) -> None: ...
```

Interface before implementation.

### Step 2 — Two Implementations

```python
# 2_impls.py
class EmailNotifier:
    def send(self, user_id, body): ...
class SMSNotifier:
    def send(self, user_id, body): ...
```

Polymorphism makes implementations swappable.

### Step 3 — Write the ADR

```text
# 3_adr.md
# ADR 0007: Notification channel abstraction
- Context: email/SMS/push are added often
- Decision: abstract via Notifier protocol
- Alternatives: direct if/elif, external SaaS integration
- Consequences: easy unit testing, negligible perf cost
```

The reasoning fits on one page.

### Step 4 — Apply YAGNI (Subtract)

```python
# 4_remove.py
# class NotifierFactory: ...        # not needed for one channel
# class NotifierRegistry: ...       # current simplicity beats future freedom
```

Today's simplicity over tomorrow's optionality.

### Step 5 — Observability (At Implementation Time)

```python
# 5_obs.py
import logging
log = logging.getLogger(__name__)

class EmailNotifier:
    def send(self, user_id, body):
        log.info("notify", extra={"user": user_id, "channel": "email"})
        # ...
```

Design must intend for observability.

## A small design stress test

Good design shows up when you try to change the system, not when you stare at the current diagram. Use a small change request to see whether your interfaces and ADRs actually reduce blast radius.

### Verification steps

1. Assume you need to add one more notifier channel to the example.
2. Count how many files and tests would need to change.
3. Explain the reason for the abstraction in one short ADR paragraph.

**Expected output:**

- New behavior can be added without rewriting every caller.
- The ADR makes the trade-off legible to someone who did not make the original choice.
- Observability needs remain visible instead of getting glued on at the end.

### Failure modes to watch

- One new implementation forces broad edits across unrelated callers.
- The abstraction exists, but no one can still explain why it exists.
- Future-proofing added factories and registries long before any real pressure appeared.

## What to Notice in This Code

- The interface defines responsibility.
- Polymorphism prices the cost of future change.
- ADRs preserve the justification for changes.
- Observability is a design-time decision.

## Five Common Mistakes

1. **Burying design in code.** Reasons disappear.
2. **Over-design (future assumptions).** Unused abstraction is debt.
3. **Sharing implementations without an interface.** Leaks into other callers.
4. **Missing ADRs.** "Why this way?" repeats forever after an incident.
5. **Avoiding redesign.** Reinforcing a wrong decision with more code.

## How This Shows Up in Production

Large organizations keep ADRs in git and change them via PR. System diagrams (C4 model) live in the README. New features always go "design -> review -> implementation".

## How a Senior Engineer Thinks

- ADR before code.
- Make responsibility boundaries explicit through interfaces.
- Today's simplicity over tomorrow's optionality.
- Observability is part of the design.
- Decisions are kept reversible.

## Checklist

- [ ] Do major decisions have ADRs?
- [ ] Are interfaces explicit?
- [ ] Has YAGNI been applied to subtract abstraction?
- [ ] Is observability part of the design?
- [ ] Is the decision reversible?

## Practice Problems

1. Write an ADR for one big decision in your project.
2. Find two unused abstractions and outline how to remove them.
3. Pick a module without observability and list the additions you would make.

## Wrap-up and Next Steps

Design and implementation are different jobs done with different tools. Next we look at the last quality gate before merge — code review.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Design vs Implementation?**
  - The article treats Design vs Implementation as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Design vs Implementation?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Design vs Implementation reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Software Engineering 101 (1/10): What Is Software Engineering?](./01-what-is-software-engineering.md)
- [Software Engineering 101 (2/10): Understanding Requirements](./02-understanding-requirements.md)
- **Design vs Implementation (current)**
- Code Review (upcoming)
- Testing Strategy (upcoming)
- Version Control and Release (upcoming)
- Documentation (upcoming)
- Collaboration Process (upcoming)
- Maintenance and Tech Debt (upcoming)
- What Makes Good Software (upcoming)

<!-- toc:end -->

## References

- [Michael Nygard — Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- [C4 Model — Simon Brown](https://c4model.com/)
- [ThoughtWorks — Architecture Decision Records](https://www.thoughtworks.com/radar/techniques/lightweight-architecture-decision-records)
- [Designing Data-Intensive Applications — Martin Kleppmann](https://dataintensive.net/)

Tags: Computer Science, SoftwareEngineering, Design, Architecture, Implementation, Tradeoff
