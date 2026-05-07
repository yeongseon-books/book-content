---
series: capstone-project-101
episode: 8
title: Schedule Management
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Capstone
  - Schedule
  - Planning
  - Project
  - Beginner
seo_description: A beginner-friendly tour of capstone schedule management with milestones, weekly plans, and a risk buffer.
last_reviewed: '2026-05-04'
---

# Schedule Management

> Capstone Project 101 series (8/10)

<!-- a-grade-intro:begin -->

**Core question**: *Why* does the *perfect plan* fall apart?

> *Reality* is *slower* and *more uncertain* than *estimates*.

<!-- a-grade-intro:end -->

## What You Will Learn

- Defining *milestones*
- A *weekly plan*
- A *daily standup*
- A *risk buffer*
- Measuring *progress*

## Why It Matters

A *clear schedule* enables *focus*.

## Concept at a Glance

```mermaid
flowchart LR
    M[Milestones] --> W[Weekly Plan]
    W --> S[Standup]
    S --> R[Risk Buffer]
    R --> P[Progress]
```

## Key Terms

- **milestone**: a *major step*.
- **weekly plan**: a *7-day plan*.
- **standup**: a *short sync*.
- **buffer**: *spare time*.
- **progress**: *measured advance*.

## Before/After

**Before**: Only a *deadline* is written.

**After**: *Milestones + weekly + buffer* exist.

## Hands-on: Schedule Table

### Step 1 — Milestones

```python
milestones = ["MVP", "Demo", "Final"]
```

### Step 2 — Weekly plan

```python
weeks = {1: "setup", 2: "core", 3: "polish"}
```

### Step 3 — Standup format

```python
standup = ["yesterday", "today", "blockers"]
```

### Step 4 — Risk buffer

```python
buffer_days = 0.2 * 21
```

### Step 5 — Progress snapshot

```python
progress = {"done": 12, "todo": 8, "blocked": 2}
```

## What to Notice in This Code

- *Milestones* are *three to five*.
- The *weekly plan* is *one line*.
- The *buffer* is *twenty percent*.

## Five Common Mistakes

1. **No *buffer*.**
2. ***Standups* run *long*.**
3. **Measuring *progress* by *feel*.**
4. **The *weekly plan* is *fixed*.**
5. **Hiding *blockers*.**

## How This Shows Up in Production

Company teams use *two-week sprints* and *burndown* charts.

## How a Senior Engineer Thinks

- *Milestones* are *outcomes*.
- *Plans* are *adjustable*.
- *Buffer* is *standard*.
- *Blockers* are *visible*.
- *Progress* is *measured*.

## Checklist

- [ ] *Milestones* table.
- [ ] *Weekly* plan.
- [ ] *Daily* standup.
- [ ] *Twenty percent* buffer.

## Practice Problems

1. Define *milestone* in one line.
2. State the purpose of *buffer* in one line.
3. State the *three* standup items in one line.

## Wrap-up and Next Steps

Next post: *Building Presentation Materials*.

<!-- toc:begin -->
- [What is a Capstone Project](./01-what-is-capstone.md)
- [Choosing a Topic](./02-choosing-a-topic.md)
- [Defining the Problem](./03-defining-the-problem.md)
- [Organizing Requirements](./04-organizing-requirements.md)
- [Splitting Team Roles](./05-splitting-team-roles.md)
- [Designing the MVP](./06-designing-the-mvp.md)
- [Choosing the Tech Stack](./07-choosing-the-tech-stack.md)
- **Schedule Management (current)**
- Building Presentation Materials (upcoming)
- Project Retrospective (upcoming)
<!-- toc:end -->

## References

- [Scrum Guide](https://scrumguides.org/)
- [Critical Path Method](https://en.wikipedia.org/wiki/Critical_path_method)
- [Burndown Chart - Atlassian](https://www.atlassian.com/agile/tutorials/burndown-charts)
- [Estimation - Steve McConnell](https://stevemcconnell.com/sea/)

Tags: Capstone, Schedule, Planning, Project, Beginner
