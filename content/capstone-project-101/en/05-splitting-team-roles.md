---
series: capstone-project-101
episode: 5
title: "Capstone Project 101 (5/10): Splitting Team Roles"
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
  - Team
  - Roles
  - Collaboration
  - Beginner
seo_description: A beginner-friendly tour of splitting capstone team roles, mapping primary owners, backups, and decision rights.
last_reviewed: '2026-05-14'
---

# Capstone Project 101 (5/10): Splitting Team Roles

Teams with fuzzy roles often look busy while moving slowly. Work circulates because nobody is sure who owns the final decision or who can safely take over when someone gets blocked.

In a capstone, role splitting is not about drawing boxes around people. It is about preventing decision bottlenecks and making sure the project can keep moving under schedule pressure.

This is the 5th post in the Capstone Project 101 series. It outlines a simple role model that uses primary owners, backups, and explicit decision rights to keep collaboration moving.


![capstone project 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/capstone-project-101/05/05-01-the-flow-at-a-glance.en.png)
*capstone project 101 chapter 5 flow overview*
> Role clarity matters most when communication breaks down. Each role owns specific outcomes and handoff points.

## Questions to Keep in Mind

- Why do overlapping roles slow decisions down?
- How should teams assign primary owners and backups?
- How is a lead different from a code owner?

## What You Will Learn

- Five core *roles*
- A *responsibility matrix*
- *Code ownership*
- *Decision* flow
- *Backups*

## Why It Matters

Clear primary ownership speeds up decisions because the team knows exactly where questions and approvals should go.

Backup ownership matters just as much. Student teams are vulnerable to exams, interviews, and conflicting schedules, so a single absent owner can quickly turn into a project-wide slowdown.

## Practical artifact: a responsibility matrix

Even a small team benefits from writing responsibility lines like these before implementation starts.

```text
Workstream | Primary owner | Backup | Decision right
Requirement changes | Team lead | Frontend owner | Lead approval
API design | Backend owner | Data owner | Backend proposes, lead approves
Demo scenario | QA owner | Team lead | QA proposes, team agrees
Deployment check | Backend owner | Frontend owner | Must follow deployment checklist
```

## What to validate first

- Check that each workstream has one clear primary owner.
- Look for critical areas with no backup owner.
- Mark ambiguous decision rights early instead of discovering them mid-sprint.
- Leave room to record when and why role assignments change.

## Key Terms

- **lead**: the overall coordinator who owns schedule alignment and final approval on scope changes.
- **backend**: the server and API owner responsible for data flow and integration.
- **frontend**: the UI owner responsible for user-facing screens and interactions.
- **data**: the DB and analysis owner who manages data pipelines and sample data.
- **QA**: the quality verifier who defines test criteria and confirms acceptance.

## Before/After

**Before**: *Everyone* watches *everything*.

**After**: A *primary* and a *backup* are set.

## Hands-on: Role Table

### Step 1 — List members

List the team members clearly first, such as `A`, `B`, `C`, and `D`, so you can judge role overlap realistically.

Assigning roles before listing people leads to fantasy org charts. Start from actual headcount and skill distribution.

### Step 2 — Map primary roles

Map the primary roles explicitly, for example `A=lead`, `B=backend`, `C=frontend`, and `D=data`.

Each person should have exactly one primary role. Dual-primary assignments create the very ambiguity this exercise aims to eliminate.

### Step 3 — Map backups

Define the backup mapping early too, such as `backend=C`, `frontend=B`, and `data=A`.

Backup does not mean "does double work." It means "can unblock the team within 24 hours if the primary is unavailable."

### Step 4 — Responsibility table

For the responsibility table, concise pairings such as `deploy=(A, B)` and `test=(D, C)` are usually enough.

The table answers one question: "When X is stuck, who decides?" If the table cannot answer that question for every workstream, it has gaps.

### Step 5 — Review cadence

Set the review cadence explicitly; a weekly role review is usually enough to catch drift early.

Roles evolve as the project moves through phases. A role that makes sense during requirements may need adjustment during integration. Reviewing weekly keeps assignments honest.

## What to Notice in This Code

- A *primary* is *one person* — shared ownership is no ownership.
- A *backup* is *always* defined — single points of failure kill capstones.
- *RACI* is *concise* — four columns maximum.

## Five Common Mistakes

1. **Marking everyone as co-owner.** Shared responsibility becomes no responsibility.
2. **No backup.** One sick team member stalls the entire project.
3. **The lead decides everything.** Bottleneck by design.
4. **Assigning QA at the end.** Quality criteria should exist before code is written.
5. **Not recording role changes.** The team forgets who currently owns what.

## How This Shows Up in Production

Company teams use RACI matrices to clarify decision rights every sprint. The format is identical to what you build in a capstone — Responsible, Accountable, Consulted, Informed. Practicing it now means less ramp-up time in your first job.

## How a Senior Engineer Thinks

- Roles are written down — verbal agreements vanish under pressure.
- Backups are required — no single point of failure tolerated.
- Decision rights are explicit — who proposes, who approves, who is informed.
- Overlap is minimal — two owners means zero owners.
- Changes are announced — silent role drift causes confusion.

## Checklist

- [ ] Primary owner mapped for every workstream.
- [ ] Backup defined for every primary owner.
- [ ] RACI table completed and shared with the team.
- [ ] Weekly review cadence scheduled.

## Practice Problems

1. State what *RACI* means in one line.
2. State the purpose of a *backup* in one line.
3. State the *lead* responsibility in one line.

## Deep Dive: Schedule Planning Table and Milestone Setup

Once roles are set, the next challenge is placing them on a timeline. Many teams manage the role table and the schedule separately, which creates time slots that nobody actually owns. The role-assignment document should therefore include schedule planning and milestone criteria together.

### 6-Week Schedule Planning Table

| Week | Goal | Primary Role | Completion Criterion | Risk Signal |
| --- | --- | --- | --- | --- |
| Week 1 | Lock problem definition and requirements | Team lead | Must stories approved | 3+ requirement changes |
| Week 2 | Secure core data / input path | Backend, Data | Sample input processed successfully | External data access delay |
| Week 3 | Implement core flow | Frontend, Backend | Input → calculation → result connected | Repeated integration failure |
| Week 4 | Test and fix defects | QA | Must test pass rate ≥ 90 % | Regression bug increase |
| Week 5 | Demo rehearsal | Entire team | 60 s demo succeeds 3 times consecutively | 2+ demo failures |
| Week 6 | Finalize presentation / retrospective | Team lead, QA | Slides and retro action log complete | Document gaps |

### Milestone Definition Example

| Milestone | Definition | Evidence Deliverable | Pass Condition |
| --- | --- | --- | --- |
| M1 Requirements Lock | Must scope confirmed | Requirements sheet v1 | Change-request hold rule agreed |
| M2 MVP Connected | Core flow working | Demo video draft | 1 successful demonstration |
| M3 Quality Stabilized | Defect risk reduced | Test report | Major defects = 0 |
| M4 Presentation Ready | Delivery quality verified | Slides, demo script | Rehearsal time met |

Milestones are not tools for recording "we were busy this week" — they are tools for judging "what is finished." If completion criteria are vague, even clear roles cannot prevent schedule blur.

### Role-Schedule Sync Rules

- The primary owner declares the weekly goal as a sentence.
- The backup proposes an alternative plan within 24 hours when a blocker appears.
- The team lead records the schedule-deviation cause in the weekly retro.
- QA announces test criteria per milestone in advance.
- No new features are added during the presentation week.

### Schedule Adjustment Decision Frame

```text
Question 1: Does this change strengthen the core flow?
Question 2: Does this change raise demo success probability?
Question 3: Does this change increase Must test coverage?
Question 4: Can the current team handle the increased scope?
Conclusion: If 2+ answers are "No," defer to next week.
```

The quality of role assignment is ultimately measured by the team's ability to absorb schedule shocks. Operating the tables and rules above together lets the team speak the same language about "who finishes what by when" — and that shared language itself accelerates collaboration.

## Practical Anchor: Role Assignment Standard and Branch Strategy

Team roles are not about dividing people — they are about creating responsibility boundaries. When roles are ambiguous, nobody can confirm a decision when the schedule slips. The standard below is a minimal configuration directly applicable to small capstone teams.

### RACI-Based Role Assignment Example

| Task | Responsible (R) | Accountable (A) | Consulted (C) | Informed (I) |
| --- | --- | --- | --- | --- |
| Lock problem definition | PM | Team lead | Everyone | Advisor |
| MVP implementation | Dev owner | Team lead | QA owner | Everyone |
| Test / verification | QA owner | Team lead | Dev owner | Everyone |
| Presentation materials | Presenter | PM | Everyone | Advisor |

### Branch Collaboration Rules

- Create a `feat/<owner>/<topic>` branch per feature unit.
- Push to remote at least once per day to keep change history public.
- Pin three items in every PR body: "Purpose / Changes / Verification."
- Do not merge until the review checklist passes.

```text
PR Template
- Purpose: what problem does this change solve
- Changes: top 3 modifications
- Verification: tests run and their results
```

Fixing roles and branch rules together reduces meeting time and speeds up decisions. Especially in the week before the presentation, confusion about who is finishing what drops significantly.

## Wrap-up and Next Steps

Role splitting is a bottleneck-reduction design, not an org-chart exercise. Primary ownership, backup coverage, and explicit decision rights make the team far more resilient under capstone pressure. The next post shows how that structure supports MVP scoping.

## Answering the Opening Questions

- **Why do overlapping roles slow down decisions?**
  - This article unpacks splitting team roles not as a simple definition but through concrete situations and decision processes encountered in practice. Follow the examples and checklists in each section to apply them to your own situation.
- **What are the core roles commonly used in teams?**
  - Referring to the example code and matrices presented in this article, you can concretely feel what good judgment criteria look like. Understanding "in what situation do you set such criteria" matters more than the numbers themselves.
- **How should you designate a primary owner and backup?**
  - The core message of this article is that regardless of what evaluation criteria you use, it never ends with a single judgment. Recording criteria in documents early on, so the same mistakes aren't repeated when looking back later—that process itself leads a project to success.
<!-- toc:begin -->
## In this series

- [Capstone Project 101 (1/10): What is a Capstone Project](./01-what-is-capstone.md)
- [Capstone Project 101 (2/10): Choosing a Topic](./02-choosing-a-topic.md)
- [Capstone Project 101 (3/10): Defining the Problem](./03-defining-the-problem.md)
- [Capstone Project 101 (4/10): Organizing Requirements](./04-organizing-requirements.md)
- **Splitting Team Roles (current)**
- Designing the MVP (upcoming)
- Choosing the Tech Stack (upcoming)
- Schedule Management (upcoming)
- Building Presentation Materials (upcoming)
- Project Retrospective (upcoming)

<!-- toc:end -->

## References

### Official docs and practical guides

- [RACI Matrix — PMI](https://www.pmi.org/learning/library/raci-responsibility-matrix-9410)
- [Team Topologies](https://teamtopologies.com/)
- [Code Ownership — Martin Fowler](https://martinfowler.com/bliki/CodeOwnership.html)
- [The Mythical Man-Month](https://en.wikipedia.org/wiki/The_Mythical_Man-Month)

Tags: Capstone, Team, Roles, Collaboration, Beginner
