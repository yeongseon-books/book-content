---
series: software-engineering-101
episode: 2
title: "Software Engineering 101 (2/10): Understanding Requirements"
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
  - Requirements
  - ProductManagement
  - UserStory
  - Process
seo_description: A short, code-first guide to requirements — what makes one good, user stories, and the INVEST principle that keeps stories shippable.
last_reviewed: '2026-05-15'
---

# Software Engineering 101 (2/10): Understanding Requirements

Requirements often sound obvious at first. "Add search." "Improve response time." "Let users reset passwords." The danger is that everyone hears familiar words and imagines a different finish line. Product, design, engineering, and operations can all agree with the same sentence while still carrying different assumptions about scope, risk, and success.

That is why requirement mistakes are so expensive. A bug found during implementation can usually be fixed. A misunderstood requirement can force you to rewrite the code, the tests, the rollout plan, and the user expectation all at once. The cost is not just rework. It is false progress.

This is post 2 in the Software Engineering 101 series. In this chapter, we turn vague requests into testable statements by connecting user stories, acceptance criteria, non-functional requirements, and the question patterns that expose ambiguity early.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Understanding Requirements?
- Which signal should the example or diagram make visible for Understanding Requirements?
- What failure should be prevented first when Understanding Requirements reaches a real system?

## Big Picture

![software engineering 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/software-engineering-101/02/02-01-concept-at-a-glance.en.png)

*software engineering 101 chapter 2 flow overview*

This picture places Understanding Requirements inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Understanding Requirements is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## What You Will Learn

- What makes a requirement good
- User stories and acceptance criteria
- Functional vs non-functional requirements
- Question patterns that remove ambiguity
- Why requirements live in writing

## Why It Matters

Over half of code defects originate at the requirements stage. The later you find them, the cost grows exponentially.

> The most expensive code is code you rewrite.

## Concept at a Glance

Requirements only become real when they map to tests.

## Key Terms

- **Functional requirement**: what the system does.
- **Non-functional requirement**: how well it must do it (performance, security, availability).
- **User story**: "As a role, I want X so that Y" — one line.
- **Acceptance Criteria (AC)**: the conditions that mark "done".
- **INVEST**: the six attributes of a good story.

## Before/After

**Before — Vague**

```text
"Build a search feature"
```

**After — Measurable**

```text
A user (role) searches the product catalog (scope) by keyword (input)
and gets results sorted by relevance (sort) within 500ms (performance).
```

One sentence sets the quality of the outcome.

## Hands-on Step by Step

### Step 1 — Write a User Story

```text
# 1_story.txt
As a registered user, I want a password-reset link via email so that
I can quickly recover account access.
```

Role - action - value.

### Step 2 — Acceptance Criteria

```text
# 2_ac.txt
- Email arrives within 60 seconds for a registered address
- Link expires after 30 minutes
- Token is invalidated immediately after use
- Identical response for unregistered emails (avoid leaking)
```

Phrased so they can be tested.

### Step 3 — Non-functional Requirements

```text
# 3_nfr.txt
- Availability: 99.9% monthly
- Security: single-use token
- Observability: send/use counters streamed to SIEM
```

NFRs decide operational cost.

### Step 4 — Ambiguity-Hunting Questions

```text
# 4_questions.txt
- Who uses this?
- How often?
- What happens on failure?
- Where do we measure?
- What is "done"?
```

Append 5W1H to expose vagueness.

### Step 5 — Capture in the Wiki/Ticket

```text
# 5_doc.md
- Context
- User story
- Acceptance criteria
- Non-functional requirements
- Decision log (options and reason chosen)
```

A spoken agreement does not exist.

## A practical ambiguity check

When a requirement arrives, resist the urge to design immediately. First convert the sentence into something a tester, reviewer, and operator can all inspect. That small pause is where most requirement quality is won.

### Verification steps

1. Copy a real feature request into a scratch note.
2. Rewrite it in terms of role, input, success condition, and failure behavior.
3. Add at least two non-functional constraints such as latency, security, or observability.

**Expected output:**

- The original sentence becomes testable instead of merely familiar.
- Missing edge cases show up before they turn into implementation drift.
- The acceptance criteria start looking like the future PR checklist.

### Failure modes to watch

- The requirement still depends on words like "fast" or "properly" with no threshold.
- Unregistered users, failed requests, or measurement points are undefined.
- The agreement lives only in meeting memory instead of a ticket, RFC, or PRD.

## What to Notice in This Code

- "Verifiable" is the start of a good requirement.
- Acceptance criteria become PR-merge gates.
- Pinning NFRs early is always cheaper.
- A decision log shrinks future debugging time.

## Five Common Mistakes

1. **Designing the moment you hear the requirement.** Vagueness hardens into code.
2. **Accepting "something like X".** Not measurable.
3. **Ignoring NFRs.** They explode in production.
4. **Merging PRs without ACs.** No definition of done.
5. **No change history.** "Why is it this way?" repeats forever.

## How This Shows Up in Production

PM, designers, and engineers run a discovery meeting and capture requirements in an RFC or PRD. Jira/Linear tickets carry ACs as checkboxes that map directly into the PR description.

## How a Senior Engineer Thinks

- Cannot state the "why" in one line? Do not start.
- Pin NFRs before writing code.
- Automate ACs as tests.
- Capture decisions in RFCs/ADRs.
- Resolve ambiguity in conversation, not in code.

## Checklist

- [ ] Does the story have role, action, and value?
- [ ] Are the acceptance criteria measurable?
- [ ] Are non-functional requirements stated?
- [ ] Is there a decision log?
- [ ] Does the PR description map to the ACs?

## Practice Problems

1. Rewrite one feature in your project as a user story.
2. Pick a story without ACs and write five.
3. Name two NFRs that would cause incidents if ignored.

## Wrap-up and Next Steps

Good requirements are measurable. Next we look at the step before code — design vs implementation.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Understanding Requirements?**
  - The article treats Understanding Requirements as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Understanding Requirements?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Understanding Requirements reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Software Engineering 101 (1/10): What Is Software Engineering?](./01-what-is-software-engineering.md)
- **Understanding Requirements (current)**
- Design vs Implementation (upcoming)
- Code Review (upcoming)
- Testing Strategy (upcoming)
- Version Control and Release (upcoming)
- Documentation (upcoming)
- Collaboration Process (upcoming)
- Maintenance and Tech Debt (upcoming)
- What Makes Good Software (upcoming)

<!-- toc:end -->

## References

- [Mike Cohn — User Stories Applied](https://www.mountaingoatsoftware.com/books/user-stories-applied)
- [Atlassian — INVEST in Good Stories](https://www.atlassian.com/agile/project-management/user-stories)
- [Joel Spolsky — Painless Functional Specifications](https://www.joelonsoftware.com/2000/10/02/painless-functional-specifications-part-1-why-bother/)
- [ISO/IEC/IEEE 29148 — Requirements Engineering](https://www.iso.org/standard/72089.html)

Tags: Computer Science, SoftwareEngineering, Requirements, ProductManagement, UserStory, Process
