---
series: capstone-project-101
episode: 8
title: "Capstone Project 101 (8/10): Schedule Management"
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
  - Schedule
  - Planning
  - Project
  - Beginner
seo_description: A beginner-friendly tour of capstone schedule management with milestones, weekly plans, and a risk buffer.
last_reviewed: '2026-05-14'
---

# Capstone Project 101 (8/10): Schedule Management

Most capstone schedules do not collapse in the final week without warning. They drift gradually, and the team notices too late because nothing made the gap visible early enough.

A good schedule is not a beautiful timeline. It is a system that repeatedly exposes the difference between plan and reality through milestones, weekly commitments, blockers, and explicit buffer.

This is the 8th post in the Capstone Project 101 series. It explains how to combine milestones, weekly planning, standups, and risk buffer into a realistic execution rhythm.


![capstone project 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/capstone-project-101/08/08-01-the-flow-at-a-glance.en.png)
*capstone project 101 chapter 8 flow overview*
> The real skill in Schedule Management is knowing which decision points matter most for your team and how to recognize them in real projects.

## Questions to Keep in Mind

- Why do polished-looking plans still fail in practice?
- How do milestones differ from weekly plans?
- Why should blockers be exposed as early as possible?

## What You Will Learn

- Defining *milestones*
- A *weekly plan*
- A *daily standup*
- A *risk buffer*
- Measuring *progress*

## Why It Matters

Milestones without weekly plans stay abstract, while weekly plans without milestones easily turn into busy work with no visible destination.

Buffer matters because student projects absorb many external shocks at once: exams, conflicting calendars, and surprise bugs. Without spare capacity, small slips turn into schedule-wide failure very quickly.

## Practical artifact: a weekly execution board

A board like this often shows reality faster than a polished Gantt chart.

```text
Week | Goal | Done condition | Blocker | Buffer used
Week 1 | freeze requirements | Must stories approved | none | 0 days
Week 2 | implement core flow | input and result view connected | CSV cleanup delay | 1 day
Week 3 | rehearse demo | 60-second run succeeds | login bug reproduced | 2 days
Week 4 | finalize deck | Q&A ready | none | 0.5 day
```

## What to validate first

- Keep each weekly goal readable in one line.
- Define done conditions as outcomes, not activities.
- Record blockers explicitly instead of hiding them in chat.
- Track buffer consumption separately so schedule health stays visible.

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

Lock the milestones around visible outcomes such as `MVP`, `Demo`, and `Final`.

### Step 2 — Weekly plan

Write the weekly plan as a one-line summary, for example `week 1=setup`, `week 2=core`, and `week 3=polish`.

### Step 3 — Standup format

The standup format only needs these three repeated prompts:

- `yesterday`
- `today`
- `blockers`

### Step 4 — Risk buffer

Calculate the risk buffer in advance, for example as 20% of a 21-day schedule.

### Step 5 — Progress snapshot

Capture progress in numbers such as `done=12`, `todo=8`, and `blocked=2` so blocked work is immediately visible.

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

Schedule management is about surfacing drift, not documenting busyness. When milestones, weekly plans, blockers, and buffer are managed together, late-semester uncertainty becomes far easier to absorb. The next post shows how to turn that work into presentation materials.

## Answering the Opening Questions

- **Why do polished-looking plans still fail in practice?**
  - The article treats Schedule Management as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **How do milestones differ from weekly plans?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Why should blockers be exposed as early as possible?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Capstone Project 101 (1/10): What is a Capstone Project](./01-what-is-capstone.md)
- [Capstone Project 101 (2/10): Choosing a Topic](./02-choosing-a-topic.md)
- [Capstone Project 101 (3/10): Defining the Problem](./03-defining-the-problem.md)
- [Capstone Project 101 (4/10): Organizing Requirements](./04-organizing-requirements.md)
- [Capstone Project 101 (5/10): Splitting Team Roles](./05-splitting-team-roles.md)
- [Capstone Project 101 (6/10): Designing the MVP](./06-designing-the-mvp.md)
- [Capstone Project 101 (7/10): Choosing the Tech Stack](./07-choosing-the-tech-stack.md)
- **Schedule Management (current)**
- Building Presentation Materials (upcoming)
- Project Retrospective (upcoming)

<!-- toc:end -->

## References

### Official docs and practical guides

- [Scrum Guide](https://scrumguides.org/scrum-guide.html)
- [Burndown chart tutorial](https://www.atlassian.com/agile/tutorials/burndown-charts)
- [Critical Path Method](https://en.wikipedia.org/wiki/Critical_path_method)
- [Software Estimation resources — Steve McConnell](https://stevemcconnell.com/sea/)

Tags: Capstone, Schedule, Planning, Project, Beginner
