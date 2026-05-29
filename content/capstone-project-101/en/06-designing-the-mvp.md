---
series: capstone-project-101
episode: 6
title: "Capstone Project 101 (6/10): Designing the MVP"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Capstone
  - MVP
  - Scope
  - Product
  - Beginner
seo_description: A beginner-friendly tour of designing a capstone MVP by picking one happy path and cutting non essential scope.
last_reviewed: '2026-05-14'
---

# Capstone Project 101 (6/10): Designing the MVP

Many teams describe an MVP as building fewer features. That usually leads to half-finished surfaces everywhere and no fully working core flow.

An MVP is better understood as the cheapest meaningful test of the project's main hypothesis. That means the cut list is often more important than the feature list.

This is the 6th post in the Capstone Project 101 series. It designs the MVP as a package of one core flow, an explicit out-of-scope list, a demo bar, and a feedback loop.


![capstone project 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/capstone-project-101/06/06-01-the-flow-at-a-glance.en.png)
*capstone project 101 chapter 6 flow overview*
> An MVP is not a small feature set; it is a single user flow that creates enough confidence to proceed. A good MVP fits one scenario completely.

## Questions to Keep in Mind

- Why is an MVP closer to a learning tool than a small product?
- What does picking one core flow force the team to remove?
- Why must the out-of-scope list be documented?

## What You Will Learn

- *MVP* definition
- One *core flow*
- *Out-of-scope* decisions
- A *demo scenario*
- Collecting *feedback*

## Why It Matters

An MVP with one complete flow is also stronger on demo day. A user who can sign in, act, and see a result tells a much better story than a project that exposes many shallow screens.

The out-of-scope list protects that flow. Naming postponed items such as payments, admin tools, or internationalization keeps the team from quietly rebuilding the project every week.

## Practical artifact: an MVP contract

One of the best tools for protecting scope is a short MVP contract that states the current boundary in plain language.

```text
Core flow: sign in → enter timetable → calculate conflicts → view results
Out of scope: payments, admin dashboard, internationalization, advanced recommendation logic
Demo bar: show the full flow with sample data in under 60 seconds
Success signal: at least 2 of 3 first-time users reach the result screen without explanation
Feedback prompts: was the flow clear, was it fast enough, would you use it in real life
```

## What to validate first

- Confirm that the core flow fits into one readable sentence.
- Check whether the out-of-scope list is aggressive enough to protect the flow.
- Make sure the demo bar is realistic in the actual presentation environment.
- Use feedback questions that can influence the next iteration.

## Key Terms

- **MVP**: Minimum Viable Product — the smallest working version that tests your hypothesis.
- **happy path**: the normal, expected user flow with no errors or edge cases.
- **out of scope**: items explicitly deferred — documented so they do not creep back.
- **demo**: a live walkthrough of the core flow in front of an audience.
- **feedback**: structured responses collected from testers to guide the next iteration.

## Before/After

**Before**: Build *every feature*.

**After**: *Finish one flow*.

## Hands-on: MVP Table

### Step 1 — Pick the core flow

Reduce the core flow to one readable sentence, for example: register, upload, then share.

If the sentence has more than three verbs, the scope is probably too wide. A single verb chain — "enter → process → display" — is the ideal granularity for a capstone MVP.

### Step 2 — Out of scope list

Write the out-of-scope items down explicitly:

- `payment` — revenue is not the semester goal
- `i18n` — Korean-only is sufficient for the demo
- `admin` — no admin panel needed for 3 test users

Each item should have a one-line justification so the team does not revisit the same debate later.

### Step 3 — Demo scenario

Write the demo sequence in the same order you will show it, such as `login_demo_user`, `upload_sample`, and `show_share_link`.

The demo scenario doubles as a manual test script. If you can demo it, you can test it. If you cannot demo it, it is not in MVP scope.

### Step 4 — Success criteria

Make the success criteria immediately checkable, such as `happy_path <= 60s` and `errors = 0`.

Criteria should be observable during the presentation itself. A criterion you can only verify offline is a weak criterion.

### Step 5 — Feedback form

Keep the feedback prompts short and repeatable, such as `clarity`, `speed`, and `value`.

Three questions are enough. More than five and testers disengage. Fewer than two and you learn nothing actionable.

## What to Notice in This Code

- The *flow* is one *sentence* — simplicity forces focus.
- *Out of scope* is *explicit* — invisible cuts come back as invisible scope creep.
- *Criteria* are *numbers* — "works well" is not a criterion.

## Five Common Mistakes

1. **Measuring progress by feature count.** Counting features instead of verifying the flow produces false confidence.
2. **Trying to handle every exception.** Edge-case completeness belongs after the happy path works.
3. **No demo scenario.** Without a scripted demo, presentation day becomes improvisation.
4. **No feedback form.** Unstructured impressions are hard to act on.
5. **Adding external dependencies that grow risk.** Each new API or service multiplies failure modes.

## How This Shows Up in Production

Startups also start with a one-line happy path. The Y Combinator motto "do things that don't scale" is essentially an MVP contract — pick one flow, prove it works for one user, then expand. The discipline you build here transfers directly.

## How a Senior Engineer Thinks

- An MVP is a learning tool — not a shrunken product.
- The flow is single — one scenario, proven end-to-end.
- Cutting scope is bold — saying "no" is the hardest and most valuable skill.
- The demo is scripted — no improvisation during presentations.
- Feedback is structured — specific questions yield specific improvements.

## Checklist

- [ ] Core flow defined in one sentence.
- [ ] Out-of-scope list with at least 3 items documented.
- [ ] Demo scenario scripted step by step.
- [ ] Feedback form with 3 questions prepared.

## Practice Problems

1. State what *MVP* means in one line.
2. Define *happy path* in one line.
3. State the meaning of *out of scope* in one line.

## Deep Dive: Technical Design Document Structure and ADR Example

After locking MVP scope, leave a minimal technical design document before coding starts. Teams without a design doc repeat the same debates, and when standards shift mid-implementation the schedule destabilizes. Teams that maintain short design docs and ADRs preserve decision context, so they adjust faster when changes arrive.

### Technical Design Document Structure

| Section | What to Include | Length Guide |
| --- | --- | --- |
| Background and goal | What problem are we solving? What is MVP scope? | 5–8 sentences |
| Core scenario | User's happy path and failure path | 1 diagram + explanation |
| System composition | Frontend / backend / data / deployment layout | 1 component table |
| Data model | Input/output schemas, required fields | 1–2 tables |
| API contract | Endpoints, request/response, error codes | Table or OpenAPI draft |
| Quality criteria | Performance, error handling, test standards | Checklist |
| Risks and alternatives | Expected risks, mitigations, alternative comparison | 5–10 sentences |

### Component Responsibility Boundary Example

| Component | Responsible For | NOT Responsible For |
| --- | --- | --- |
| Web UI | Input collection, result display | Data persistence logic |
| API server | Validation, conflict calculation, response generation | Screen state management |
| Data layer | Timetable data storage/retrieval | Business rule decisions |
| Test module | Core scenario automated verification | Production monitoring |

Clear boundaries reduce "whose job is this?" questions between team members. Boundaries blur easily during the MVP stage, which makes documentation even more important.

### ADR Example

```text
ADR-003: Run conflict calculation engine on the server side

Status: Accepted
Date: 2026-05-21

Context:
- Placing calculation logic in both frontend and backend increases inconsistency risk.
- Consistency of calculation results is critical during the demo presentation.

Decision:
- Conflict calculation runs in a single server-side module.
- Frontend handles input validation and result display only.

Alternatives:
1) Client-side calculation: faster to implement but consistency management burden grows
2) Server-side calculation: requires network round-trip but centralizes rules

Consequences:
- Test criteria can focus on server-side tests.
- API latency monitoring criteria become additionally necessary.
```

### Design Review Questions

- Does this design directly support the MVP core flow?
- Is there a simpler alternative for the most complex part?
- Are boundaries separated into testable units?
- Are failure symptoms visible to the user defined?
- Is this a design decision that can be demonstrated during the presentation?

### Document Operation Principles

A design document is not a document that must be perfect — it is a living reference. Rather than rewriting the whole thing every time a change occurs, accumulating decisions as ADRs is more efficient. During the MVP stage, recording "why we made this decision" matters especially. That record becomes the shared evidence base for schedule management, presentation Q&A, and the final retrospective.

## Practical Anchor: MVP Acceptance Criteria Table and CI/CD Pipeline

The core of MVP design is not feature count — it is "done criteria." Without done criteria, you cannot judge whether implementation is finished, and rehearsals become an endless edit loop.

### MVP Acceptance Criteria Table

| Feature | Done Condition | Failure Condition | Verification Method |
| --- | --- | --- | --- |
| Input processing | 5 sample inputs processed without error | Malfunction when required field missing | Unit test + manual demo |
| Core calculation | Conflict detection accuracy 100 % | 1+ conflict missed | Test dataset verification |
| Result screen | Key info visible within one scroll | Key info missing | Checklist review |

### Minimal CI/CD Pipeline for Capstone

```yaml
stages:
  - test
  - build
  - deploy

test:
  script:
    - pytest -q
build:
  script:
    - docker build -t capstone-app .
deploy:
  script:
    - ./scripts/deploy_staging.sh
```

This configuration is not complex, but its effect is large. Because builds cannot proceed without passing tests, quality drops are caught early. Fixing a staging deployment also keeps the demo rehearsal environment stable.

## Wrap-up and Next Steps

An MVP is a small experiment, not a small product. When the core flow, cut list, demo bar, and feedback prompts live together, the team can protect what matters even when the semester gets noisy. The next post chooses a tech stack that fits that MVP.

## Answering the Opening Questions

- **Why is an MVP closer to a learning tool than a small finished product?**
  - This article unpacks MVP design not as a simple definition but through concrete situations and decision processes encountered in practice. Follow the examples and checklists in each section to apply them to your own situation.
- **What does "pick one core flow" mean in terms of what to keep and what to cut?**
  - Referring to the example code and matrices presented in this article, you can concretely feel what good judgment criteria look like. Understanding "in what situation do you set such criteria" matters more than the numbers themselves.
- **Why is documenting out-of-scope items important?**
  - The core message of this article is that regardless of what evaluation criteria you use, it never ends with a single judgment. Recording criteria in documents early on, so the same mistakes aren't repeated when looking back later—that process itself leads a project to success.
<!-- toc:begin -->
## In this series

- [Capstone Project 101 (1/10): What is a Capstone Project](./01-what-is-capstone.md)
- [Capstone Project 101 (2/10): Choosing a Topic](./02-choosing-a-topic.md)
- [Capstone Project 101 (3/10): Defining the Problem](./03-defining-the-problem.md)
- [Capstone Project 101 (4/10): Organizing Requirements](./04-organizing-requirements.md)
- [Capstone Project 101 (5/10): Splitting Team Roles](./05-splitting-team-roles.md)
- **Designing the MVP (current)**
- Choosing the Tech Stack (upcoming)
- Schedule Management (upcoming)
- Building Presentation Materials (upcoming)
- Project Retrospective (upcoming)

<!-- toc:end -->

## References

### Official docs and practical guides

- [Minimum Viable Product guide](https://www.atlassian.com/agile/product-management/minimum-viable-product)
- [The Lean Startup](http://theleanstartup.com/)
- [Continuous Discovery Habits](https://www.producttalk.org/continuous-discovery/)
- [Inspired — Marty Cagan](https://svpg.com/inspired-how-to-create-products-customers-love/)

Tags: Capstone, MVP, Scope, Product, Beginner
