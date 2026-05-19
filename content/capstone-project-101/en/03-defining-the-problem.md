---
series: capstone-project-101
episode: 3
title: Defining the Problem
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

# Defining the Problem

When the problem statement is weak, the team keeps changing solutions without knowing what it is optimizing for. Features multiply while the explanation gets thinner.

A good problem statement becomes the project's anchor. Requirements, MVP scope, demo emphasis, and success metrics all need to trace back to it.

This is post 3 in the Capstone Project 101 series. It separates feature talk from problem definition and shows how to build a problem card with users, assumptions, and metrics.

## Questions this chapter answers

- Why does an unclear problem statement destabilize the solution?
- How is a problem definition different from feature description?
- How much detail do users and assumptions need?
- Why should metrics appear from the start?
- When does rewriting the problem signal learning rather than failure?

> The problem statement is not the first line of a feature list. It is the sentence that holds later requirements and priorities together.


## What You Will Learn

- Writing a problem *statement*
- *User* hypothesis
- *Value* specification
- *Metric* baseline
- Problem *restatement*

## Why It Matters

A clear statement lets the team ask the same question whenever a new feature appears: does this directly help solve the stated problem? Without that filter, every idea starts to look equally important.

Writing assumptions and metrics next to the problem also strengthens the eventual demo and retrospective. The team can compare what it believed at kickoff with what it later observed.

## The flow at a glance

![The flow at a glance](https://yeongseon-books.github.io/book-public-assets/assets/capstone-project-101/03/03-01-the-flow-at-a-glance.en.png)
*Connecting the problem statement to users, assumptions, and metrics*

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

- **statement**: *problem* sentence.
- **persona**: *user* profile.
- **value**: *benefit* of solving.
- **assumption**: a *premise*.
- **metric**: *measurement*.

## Before/After

**Before**: A *feature* equals the *problem*.

**After**: The *problem* justifies the *feature*.

## Hands-on: Problem Card

### Step 1 — Observation

```python
obs = "schedule conflicts during course registration"
```

### Step 2 — User

```python
user = "freshmen plus double-major students"
```

### Step 3 — Value

```python
value = "spot conflicts fast"
```

### Step 4 — Assumption

```python
assume = "users can paste timetables as text"
```

### Step 5 — Metric

```python
metric = "conflict found within 30s"
```

## What to Notice in This Code

- *Observation* comes before *statement*.
- *Assumptions* are *explicit*.
- The *metric* defines the *solution*.

## Five Common Mistakes

1. **Writing the *solution* as the *problem*.**
2. **Writing *everyone* as the *user*.**
3. **Hiding *assumptions*.**
4. **Vague *metrics*.**
5. **Fearing *restatement*.**

## How This Shows Up in Production

The *first section* of a PRD is the *problem statement*.

## How a Senior Engineer Thinks

- Keep the *problem short*.
- Make *assumptions explicit*.
- *Metrics* are *numbers*.
- *Restatement* is *healthy*.
- *Users* are *concrete*.

## Checklist

- [ ] *Statement* in one paragraph.
- [ ] *User* named.
- [ ] *Assumption* table.
- [ ] *Metric* number.

## Practice Problems

1. Define *problem statement* in one line.
2. Define *assumption* in one line.
3. State the meaning of *metric* in one line.

## Wrap-up and Next Steps

Problem definition is the decision anchor for the whole project. Once users, assumptions, and metrics are written down together, later requirement and MVP cuts become much easier to justify. The next post turns that anchor into an actual requirements document.

<!-- toc:begin -->
- [What is a Capstone Project](./01-what-is-capstone.md)
- [Choosing a Topic](./02-choosing-a-topic.md)
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
