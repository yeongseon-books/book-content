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

Start with a concrete observation, such as schedule conflicts during course registration.

### Step 2 — User

Name the primary users explicitly: freshmen and double-major students.

### Step 3 — Value

Describe the value in outcome language: help users spot conflicts quickly.

### Step 4 — Assumption

Pull the key assumption into the open: users can paste timetables as text.

### Step 5 — Metric

Tie the goal to a measurable threshold: a conflict should be found within 30 seconds.

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
