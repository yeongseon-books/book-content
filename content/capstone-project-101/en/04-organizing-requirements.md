---
series: capstone-project-101
episode: 4
title: "Capstone Project 101 (4/10): Organizing Requirements"
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
  - Requirements
  - Spec
  - Scope
  - Beginner
seo_description: A beginner-friendly tour of organizing capstone requirements through user stories, non functional needs, and priorities.
last_reviewed: '2026-05-14'
---

# Capstone Project 101 (4/10): Organizing Requirements

A feature list alone does not help when the schedule slips. It does not tell the team what can be cut first or what done actually means.

A useful requirements document behaves more like a compact delivery contract. It links user stories, acceptance criteria, non-functional constraints, and priority labels in one place.

This is the 4th post in the Capstone Project 101 series. It turns the problem statement into implementable requirements and explicit verification criteria.


![capstone project 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/capstone-project-101/04/04-01-the-flow-at-a-glance.en.png)
*capstone project 101 chapter 4 flow overview*
> Strong requirements emerge from the gap between what users need and what's buildable. Documentation captures that tension so priorities stay visible.

## Questions to Keep in Mind

- Why is a feature list alone not enough?
- How should user stories pair with acceptance criteria?
- Why should non-functional constraints live in a separate table?

## What You Will Learn

- *User stories*
- *Non-functional* needs
- Setting *priority*
- *Acceptance* criteria
- Requirement *traceability*

## Why It Matters

Without acceptance criteria, teams can finish implementation and still disagree about whether the requirement is actually done. Once criteria and priority live together, scope cuts become far less emotional.

Non-functional constraints deserve their own space too. Requirements such as mobile usability, no-sign-up flow, or response-time targets disappear quickly when they are buried inside generic feature bullets.

## Practical artifact: a requirements sheet

Adding IDs like the sheet below makes it much easier to connect implementation tasks and later test checks.

```text
ID: ST-1
User story: as a student, I want to confirm schedule conflicts immediately
Acceptance criteria: input within 5 seconds, results within 1 second, clear error messages
Non-functional needs: mobile-first, usable without sign-up, Korean-first copy
Priority: Must
Linked features: F-1 timetable input, F-2 conflict engine, F-3 results view
```

## What to validate first

- Make acceptance criteria observable rather than subjective.
- Separate non-functional needs from the user story itself.
- Check that not every line has been promoted to Must.
- Ensure the requirement ID can later map to features or tests.

## Key Terms

- **user story**: *user-perspective* request.
- **acceptance**: *accept* criteria.
- **non-functional**: *non functional* need.
- **MoSCoW**: *priority* labels.
- **traceability**: *trace links*.

## Before/After

**Before**: A *list of features*.

**After**: *Stories + criteria + priority*.

## Hands-on: Requirements Table

### Step 1 — User story

Write the story in plain user language: as a student, I want instant conflict detection.

### Step 2 — Acceptance criteria

Summarize the acceptance criteria as a short checklist:

- `input 5s`
- `result 1s`
- `error clear`

### Step 3 — Non-functional

Keep the non-functional constraints separate as well:

- `mobile`
- `no_signup`
- `korean_first`

### Step 4 — Priority

Record priority in one consistent format, for example `core=Must`, `share=Should`, and `ai=Could`.

### Step 5 — Trace

Write trace links directly, such as `ST-1 -> F-1, F-2`, so requirement IDs connect to implementation items.

## What to Notice in This Code

- *Stories* start with *verbs*.
- *Criteria* combine *numbers* and *readability*.
- *Trace* uses *IDs*.

## Five Common Mistakes

1. **The *story* drifts into *feature description*.**
2. **Forgetting *non-functional* needs.**
3. ***Everything Must*.**
4. **Subjective *criteria*.**
5. **No *traceability*.**

## How This Shows Up in Production

Startup PMs use *Must/Should/Could* labels every week.

## How a Senior Engineer Thinks

- *Stories* stay *short*.
- *Criteria* are *measurable*.
- *Priority* is *three or four buckets*.
- *Non-functional* is *separate*.
- *Trace* is *documented*.

## Checklist

- [ ] *Five+ stories*.
- [ ] *Acceptance criteria*.
- [ ] *Non-functional* table.
- [ ] *Priority* labels.

## Practice Problems

1. Define *user story* in one line.
2. Define *acceptance criteria* in one line.
3. State the meaning of *MoSCoW* in one line.

## Wrap-up and Next Steps

Requirement organization is about traceable scope, not prettier feature bullets. Once stories, criteria, non-functional needs, and priority labels live together, design and schedule decisions get much faster. The next post shows how that work should be split across the team.

## Answering the Opening Questions

- **Why is a feature list alone insufficient for requirements?**
  - This article unpacks requirements organization not as a simple definition but through concrete situations and decision processes encountered in practice. Follow the examples and checklists in each section to apply them to your own situation.
- **How does a user story differ from a feature description?**
  - Referring to the example code and matrices presented in this article, you can concretely feel what good judgment criteria look like. Understanding "in what situation do you set such criteria" matters more than the numbers themselves.
- **How specific should acceptance criteria be?**
  - The core message of this article is that regardless of what evaluation criteria you use, it never ends with a single judgment. Recording criteria in documents early on, so the same mistakes aren't repeated when looking back later—that process itself leads a project to success.
<!-- toc:begin -->
## In this series

- [Capstone Project 101 (1/10): What is a Capstone Project](./01-what-is-capstone.md)
- [Capstone Project 101 (2/10): Choosing a Topic](./02-choosing-a-topic.md)
- [Capstone Project 101 (3/10): Defining the Problem](./03-defining-the-problem.md)
- **Organizing Requirements (current)**
- Splitting Team Roles (upcoming)
- Designing the MVP (upcoming)
- Choosing the Tech Stack (upcoming)
- Schedule Management (upcoming)
- Building Presentation Materials (upcoming)
- Project Retrospective (upcoming)

<!-- toc:end -->

## References

### Official docs and practical guides

- [Atlassian requirements guide](https://www.atlassian.com/agile/product-management/requirements)
- [User Stories Applied](https://www.mountaingoatsoftware.com/books/user-stories-applied)
- [Specification by Example](https://gojko.net/books/specification-by-example/)
- [INVEST in Good Stories](https://www.agilealliance.org/glossary/invest/)

Tags: Capstone, Requirements, Spec, Scope, Beginner
