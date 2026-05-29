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

## Practical Extension: Test Strategy Table and Integration Test Scenarios

The most frequently underestimated task in schedule management is testing. When a team plans only implementation time and fails to reserve testing time separately, defects pile up in the final week and the entire plan crumbles. Therefore a test strategy must be explicitly included in the schedule document.

### Test Strategy Table

| Test Level | Purpose | Owner | Timing | Pass Criteria |
| --- | --- | --- | --- | --- |
| Unit tests | Verify core function logic | Backend / frontend devs | Immediately after feature dev | 90%+ pass rate on core functions |
| Integration tests | Verify cross-component connections | QA + developers | Weekly | 100% pass on critical flows |
| Regression tests | Confirm existing features unaffected | QA | Before deployment | 0 failures on key scenarios |
| Demo rehearsal tests | Validate presentation environment | Entire team | Twice in the week before presentation | 60-second demo succeeds 3 consecutive times |

### Integration Test Scenario Examples

| Scenario ID | Input | Expected Result | Failure Response |
| --- | --- | --- | --- |
| IT-01 | Valid timetable input | "No conflict" message displayed | Check input parser logs |
| IT-02 | Conflicting timetable input | Conflicting courses and time slots shown | Debug calculation module |
| IT-03 | Empty input submitted | User-friendly error message | Add frontend validation |
| IT-04 | Malformed CSV | Format error notice with re-upload prompt | Strengthen exception handling |
| IT-05 | 20 repeated requests | Average response time meets threshold | Cache/computation optimization |

### Schedule-Test Linkage Rules

- Attach a separate test-pass criterion to each milestone.
- Update related regression tests immediately when a new feature is added.
- Prioritize blocker issues over feature issues.
- During presentation week, share test failure count trends daily.
- If the test pass rate drops below target, halt feature additions.

### Weekly Test Report Format

```text
Week: 4
Tests executed: 28
Passed: 24
Failed: 4
Primary failure cause: missing input-format exception handling
Next action: reinforce parser validation logic, add 3 regression cases
```

This report enables early schedule-risk detection without complex quality tools. In a capstone, the simpler the quality indicator, the faster the team shares it and converts it into action.

### Pre-Presentation Stabilization Check

- Fix the 5 core scenarios to demo.
- Test in the same environment as the demo venue.
- Prepare fallback demo material (video/screenshots) for network instability.
- Separate defect priority into P1/P2 and triage accordingly.
- Link the final rehearsal log to the retrospective document.

The purpose of schedule management is not filling dates but surfacing failures early. Integrating the test strategy into the schedule document makes plan-vs-reality gaps visible faster and prevents the late-semester schedule collapse.

## Practical Anchor: Gantt Chart Operation and Weekly Check Rules

Schedule management is not about making a pretty timeline—it is about detecting deviation early. In a capstone, a one-week delay directly degrades presentation quality, so weekly reviews must follow a consistent format.

### 8-Week Gantt Chart Example

```text
Week               1 2 3 4 5 6 7 8
Problem/Requirements █ █
MVP Implementation       █ █ █
Integration Testing            █ █
Presentation Prep                █ █
Rehearsal & Fixes                  █ █
```

### Weekly Check Board Template

| Item | Planned | Actual | Deviation | Action |
| --- | --- | --- | --- | --- |
| Implementation completion | 60% | 45% | -15% | Reduce scope |
| Test pass rate | 90% | 82% | -8% | Add regression tests |
| Rehearsal count | 2 | 1 | -1 | Reschedule time slot |

When recording deviations, actions matter more than excuses. Write "why it was late" in one sentence, then decide "what to cut" immediately—that is what stabilizes the next week. The schedule is not a prediction tool; it is a priority-adjustment tool, and maintaining that mindset is essential.

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

- **Why do seemingly perfect plans actually break down frequently?**
  - This article unpacks schedule management not as a simple definition but through concrete situations and decision processes encountered in practice. Follow the examples and checklists in each section to apply them to your own situation.
- **How should milestones and weekly plans be distinguished and used?**
  - Referring to the example code and matrices presented in this article, you can concretely feel what good judgment criteria look like. Understanding "in what situation do you set such criteria" matters more than the numbers themselves.
- **Why should daily standups be short and repeatable?**
  - The core message of this article is that regardless of what evaluation criteria you use, it never ends with a single judgment. Recording criteria in documents early on, so the same mistakes aren't repeated when looking back later—that process itself leads a project to success.
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
