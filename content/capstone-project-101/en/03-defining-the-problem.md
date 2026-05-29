---
series: capstone-project-101
episode: 3
title: "Capstone Project 101 (3/10): Defining the Problem"
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
  - Problem
  - Definition
  - Scope
  - Beginner
seo_description: A beginner-friendly tour of defining a capstone problem covering statements, users, value, assumptions, and metrics.
last_reviewed: '2026-05-14'
---

# Capstone Project 101 (3/10): Defining the Problem

When the problem statement is weak, the team keeps changing solutions without knowing what it is optimizing for. Features multiply while the explanation gets thinner.

A good problem statement becomes the project's anchor. Requirements, MVP scope, demo emphasis, and success metrics all need to trace back to it.

This is the 3rd post in the Capstone Project 101 series. It separates feature talk from problem definition and shows how to build a problem card with users, assumptions, and metrics.


![capstone project 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/capstone-project-101/03/03-01-the-flow-at-a-glance.en.png)
*capstone project 101 chapter 3 flow overview*
> A problem statement earns its clarity by testing against real usage patterns. Good problems narrow toward specific users and specific pain.

## Questions to Keep in Mind

- Why does an unclear problem statement destabilize the solution?
- How is a problem definition different from feature description?
- How much detail do users and assumptions need?

## What You Will Learn

- Writing a problem *statement*
- *User* hypothesis
- *Value* specification
- *Metric* baseline
- Problem *restatement*

## Why It Matters

A clear statement lets the team ask the same question whenever a new feature appears: does this directly help solve the stated problem? Without that filter, every idea starts to look equally important.

Writing assumptions and metrics next to the problem also strengthens the eventual demo and retrospective. The team can compare what it believed at kickoff with what it later observed.

## Practical artifact: a problem card

A short problem card can dramatically improve solution discussions. The fields below are the minimum useful set.

```text
Observation: students spend too much time manually checking course schedule conflicts right before registration
Primary users: freshmen and double-major students
Problem statement: users cannot confirm schedule conflicts within 30 seconds before course registration
Core assumption: timetable data can be entered through text or CSV without special setup
Success metric: a first-time user confirms conflicts within 30 seconds
```

## What to validate first

- Make sure the statement does not begin as a solution pitch.
- Narrow the primary user group instead of writing everyone.
- Pull hidden assumptions into the document before implementation starts.
- Prefer measurable values such as time, accuracy, or completion rate.

## Key Terms

- **statement**: the problem sentence that anchors the project.
- **persona**: a concrete user profile the team designs for.
- **value**: the benefit the user receives when the problem is solved.
- **assumption**: a premise the team believes but has not yet verified.
- **metric**: a measurable indicator of success.

## Before/After

**Before**: A *feature* equals the *problem*.

**After**: The *problem* justifies the *feature*.

## Hands-on: Problem Card

### Step 1 — Observation

Start with a concrete observation, such as schedule conflicts during course registration.

An observation is not an opinion. It describes a real behavior you have witnessed or can verify: "students open three browser tabs to cross-check class times manually."

### Step 2 — User

Name the primary users explicitly: freshmen and double-major students.

Resisting the temptation to write "all students" is half the battle. The narrower the user definition, the sharper the solution becomes.

### Step 3 — Value

Describe the value in outcome language: help users spot conflicts quickly.

Value should be written from the user's point of view, not the developer's. "Reduce manual checking time" is better than "build a smarter algorithm."

### Step 4 — Assumption

Pull the key assumption into the open: users can paste timetables as text.

If the assumption turns out to be wrong, the entire solution path changes. Surfacing assumptions early converts invisible risk into a testable hypothesis.

### Step 5 — Metric

Tie the goal to a measurable threshold: a conflict should be found within 30 seconds.

A good metric has a number, a unit, and a boundary. "Fast" is not a metric. "First conflict identified within 30 seconds on first use" is.

## What to Notice in This Code

- *Observation* comes before *statement* — facts before interpretation.
- *Assumptions* are *explicit* — hidden premises kill projects.
- The *metric* defines the *solution boundary* — without it, you never know when to stop.

## Five Common Mistakes

1. **Writing the solution as the problem.** "We need a conflict-detection algorithm" is a solution, not a problem.
2. **Writing everyone as the user.** Designing for everyone means designing for no one.
3. **Hiding assumptions.** Unwritten assumptions become invisible risks that surface at the worst time.
4. **Vague metrics.** "Better user experience" cannot be measured or demonstrated.
5. **Fearing restatement.** Rewriting the problem after learning is healthy, not wasteful.

## How This Shows Up in Production

The first section of a product requirements document (PRD) is always the problem statement. Product managers and senior engineers refuse to discuss solutions until the problem statement survives scrutiny. The capstone problem card is the same exercise at a smaller scale.

## How a Senior Engineer Thinks

- Keep the problem short — if you cannot read it in 10 seconds, it is too broad.
- Make assumptions explicit — then test the riskiest one first.
- Metrics are numbers — if you cannot put a number on it, you cannot demo it.
- Restatement is healthy — the first version is never the last.
- Users are concrete — "someone who does X at time Y" beats "users."

## Checklist

- [ ] Problem statement fits in one paragraph.
- [ ] Primary user group named explicitly.
- [ ] At least two assumptions documented.
- [ ] Success metric includes a number and a unit.

## Practice Problems

1. Define *problem statement* in one line.
2. Define *assumption* in one line.
3. State the meaning of *metric* in one line.

## Deep Dive: MVP Scope Checklist and Feature Priority Matrix

Having a problem definition does not automatically organize the scope. In fact, this is the moment when the team starts receiving a stream of "we also need this" proposals. You need operational tools that cut MVP scope against the problem statement. The checklist and matrix below are gates the team must pass before writing any implementation code.

### MVP Scope Checklist

| Check Item | Yes/No | Evidence |
| --- | --- | --- |
| Primary user defined in one sentence |  |  |
| Core flow explained in 3–5 steps |  |  |
| Demo-reproducible input data available |  |  |
| Success metric expressed as a number (time, completion rate, etc.) |  |  |
| Fallback path exists if external dependency fails |  |  |
| Out-of-scope items documented |  |  |
| Must features are fewer than half of all candidates |  |  |
| Core flow demonstrable within 5 minutes during rehearsal |  |  |

The checklist is not a scoring sheet — it is an alarm system. If three or more items read "No," stop implementation and re-cut scope. In capstones, fast scope alignment beats fast coding every time.

### Feature Priority Matrix

| Feature | User Value | Impl. Difficulty | Failure Risk | Demo Contribution | Classification |
| --- | --- | --- | --- | --- | --- |
| Timetable input | High | Medium | Medium | High | Must |
| Conflict calculation | Very high | Medium | High | Very high | Must |
| Result visualization | High | Medium | Low | High | Must |
| Social sharing | Medium | Low | Low | Medium | Should |
| Notification feature | Medium | Medium | Medium | Low | Could |
| Advanced recommendation algorithm | Low | High | High | Low | Won't |

Classification rules should be simple. `Must` — features that make the core flow work. `Should` — features that raise quality. `Could` — features addable if time allows. `Won't` — explicitly excluded this semester. Pin these rules at the top of the document to minimize interpretation drift within the team.

### Scope-Cut Decision Log Example

```text
2026-05-20
- Decision: Move advanced recommendation algorithm to Won't
- Reason: learning cost too high relative to demo contribution
- Impact: simplifies data pipeline, reduces test surface
- Alternative: mention expansion plan during Q&A only
```

Recording the decision log means you can instantly answer "why did we drop this feature?" later. This is especially powerful evidence in presentation materials and retrospective documents.

### Suggested Application Order

1. Pin the problem statement at the top of the document.
2. List all candidate features.
3. Run a first-pass classification using the priority matrix.
4. Remove items that fail the MVP checklist.
5. Record the decision log and convert survivors into implementation issues.

The point is not "pack in as many features as possible" but "complete the core flow end-to-end." When this principle holds during problem definition, schedule management and presentation prep stabilize dramatically downstream.

## Practical Anchor: Code Review Checklist and Minimal CI Pipeline

A problem definition that stays as a document loses execution power. To connect the problem statement to the development flow, design a code review standard and an automated verification pipeline together. Fixing quality rules at this stage keeps judgments consistent even when scope shifts later.

### Code Review Checklist (Problem-Definition-Linked)

- Verify that the change directly connects to the problem statement.
- Confirm the new feature falls within `MVP scope`.
- Check that input/output examples match the demo scenario.
- Ensure at least one failure-case test is included.
- Confirm documentation (README / decision log) is updated alongside code.

### GitHub Actions CI Example

```yaml
name: capstone-ci
on:
  pull_request:
    branches: [main]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest -q
      - run: python scripts/check_problem_scope.py
```

The point of this pipeline is not complex deployment automation. It is about making problem-definition and scope verification pass automatically at the PR stage. As team size grows, automated rules keep project quality stable far better than human memory.

## Wrap-up and Next Steps

Problem definition is the decision anchor for the whole project. Once users, assumptions, and metrics are written down together, later requirement and MVP cuts become much easier to justify. The next post turns that anchor into an actual requirements document.

## Answering the Opening Questions

- **Why does a fuzzy problem statement make the solution unstable too?**
  - This article unpacks problem definition not as a simple definition but through concrete situations and decision processes encountered in practice. Follow the examples and checklists in each section to apply them to your own situation.
- **How does a feature description differ from a problem definition?**
  - Referring to the example code and matrices presented in this article, you can concretely feel what good judgment criteria look like. Understanding "in what situation do you set such criteria" matters more than the numbers themselves.
- **What should you write to fit user, value, assumptions, and measurement criteria on a single page?**
  - The core message of this article is that regardless of what evaluation criteria you use, it never ends with a single judgment. Recording criteria in documents early on, so the same mistakes aren't repeated when looking back later—that process itself leads a project to success.
<!-- toc:begin -->
## In this series

- [Capstone Project 101 (1/10): What is a Capstone Project](./01-what-is-capstone.md)
- [Capstone Project 101 (2/10): Choosing a Topic](./02-choosing-a-topic.md)
- **Defining the Problem (current)**
- Organizing Requirements (upcoming)
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
- [Working Backwards](https://www.workingbackwards.com/)
- [The Mom Test](http://momtestbook.com/)
- [Inspired — Marty Cagan](https://svpg.com/inspired-how-to-create-products-customers-love/)

Tags: Capstone, Problem, Definition, Scope, Beginner
