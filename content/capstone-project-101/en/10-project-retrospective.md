---
series: capstone-project-101
episode: 10
title: "Capstone Project 101 (10/10): Project Retrospective"
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
  - Retrospective
  - Learning
  - Reflection
  - Beginner
seo_description: A beginner-friendly tour of capstone retrospectives using KPT, data, five whys, and concrete next actions.
last_reviewed: '2026-05-14'
---

# Capstone Project 101 (10/10): Project Retrospective

When the project ends, relief arrives before reflection. If the team disperses at that moment, most of the semester's learning stays trapped in individual memory.

A retrospective is valuable because it converts feelings into facts, causes, and next actions. That conversion is what allows the next project to start from a higher baseline.

This is the final post in the Capstone Project 101 series. It shows how to combine KPT, data, cause analysis, and next actions into a retrospective that the next project can actually use.


![capstone project 101 chapter 10 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/capstone-project-101/10/10-01-the-flow-at-a-glance.en.png)
*capstone project 101 chapter 10 flow overview*
> A retrospective done well becomes a bridge to the next project. Bad retros feel like filing a report; good ones feel like unpacking lessons.

## Questions to Keep in Mind

- What keeps a retrospective from turning into blame allocation?
- Why does the KPT format work well for beginner teams?
- How does data make retrospective discussion more stable?

## What You Will Learn

- The *KPT* format
- *Data-driven* retrospectives
- *Five Whys* root cause
- *Next actions*
- *Learning* summary

## Why It Matters

A simple format such as KPT keeps the conversation grounded. Separating what to keep, what was problematic, and what to try next lowers the chance that the meeting dissolves into vague frustration.

Data and next actions strengthen the discussion further. Metrics such as bug counts, review latency, or rehearsal attempts make the team's pain points concrete, while owned actions turn insight into change.

## Practical artifact: a retrospective action log

Retrospectives lead to change only when next actions are small and explicit enough to survive after the meeting.

```text
Type | Item | Owner | Due date
Keep | preserve a written log of requirement changes | team lead | before next project kickoff
Problem | the team found demo-breaking bugs too late because rehearsal was weak | team | recorded during retro
Try | reserve a 20-minute rehearsal slot every Friday | QA owner | week 1 of the next project
Action | add a deployment checklist template to the repository | backend owner | week 1 of the next project
```

## What to validate first

- Separate keeps, problems, and tries instead of mixing them.
- Gather evidence for claims that currently rely on memory alone.
- Attach an owner and due date to each next action.
- Store the retro where the next project can reopen it easily.

## Key Terms

- **KPT**: *Keep / Problem / Try*.
- **5 Whys**: a *root-cause* method.
- **action**: a *next step*.
- **data**: *numerical* evidence.
- **learning**: *captured* lesson.

## Before/After

**Before**: Only *feelings* are aired.

**After**: *Facts and actions* are recorded.

## Hands-on: Retro Table

### Step 1 — KPT

The KPT template only needs three columns: `keep`, `problem`, and `try`.

### Step 2 — Data

Record retrospective metrics in numbers, such as `velocity=12`, `bugs=5`, and `review_time=1.5`, so the discussion stays tied to facts.

### Step 3 — Five Whys

Cause tracing becomes easier to read when you write it as a chain such as `bug_at_demo -> missed_test -> no_ci -> no_template -> first_time`.

### Step 4 — Next actions

Write each next action on one line with an owner, an action, and a deadline, such as `who=A`, `what=add_ci`, and `by=next_sprint`.

### Step 5 — Learning summary

Summarize the learning as short reusable lines such as `scope_first`, `ci_early`, and `demo_dryrun`.

## What to Notice in This Code

- *KPT* has *three* columns.
- *Data* is *numeric*.
- *Actions* have an *owner* and *deadline*.

## Five Common Mistakes

1. **Asking *who* is at fault.**
2. **Recording only *feelings*.**
3. **No *actions*.**
4. **No *data*.**
5. **Not *linking* to the *next project*.**

## How This Shows Up in Production

Companies run *sprint retrospectives* and *postmortems*.

## Practical Extension: KPT Framework and Personal Growth Record

For a retrospective document to become a team learning asset, separating team retrospective from individual retrospective is effective. The team retro focuses on system and process improvements; the individual retro focuses on skill growth and next learning plans. Mixing the two often creates blame dynamics or dilutes action items.

### Expanded KPT Framework

| Category | Question | Example Entry | Next Action Link |
| --- | --- | --- | --- |
| Keep | What worked well? | Requirement change log reduced schedule shock | Reuse same template |
| Problem | What recurred? | Integration test failures clustered before demo | Move test cycle earlier |
| Try | What experiment to run next? | Fix a weekly rehearsal slot | Calendar pre-emption |
| Learn | What new principle was gained? | Scope-exclusion documentation raised quality | Reflect in MVP doc standard |
| Stop | What habit to drop? | Verbal-only agreements in meetings | Mandate decision log |

When expanding KPT, strengthening the link to action items matters more than adding categories. If an item has no "next action" attached, the retro ends as mere record.

### Personal Growth Record Template

```text
[Basic Info]
Name:
Role:
Period:

[Achievements]
Top 2 contributions this project:

[Technical Growth]
New skills/tools learned:
How learned (docs, implementation, review, etc.):
Items to reuse in the next project:

[Collaboration Growth]
Communication strengths:
Lessons from conflict situations:
Collaboration habits to improve next time:

[Failures and Lessons]
Biggest mistake (1):
Cause:
Prevention action:

[Next 4-Week Plan]
Learning goal 1:
Execution plan:
Measurement criteria:
```

### Team-Individual Retro Connection Rules

- Cross-check team Problem items against individual failure entries.
- Clearly assign ownership of personal actions from team Try items.
- Verify that individual learning plans connect to the next project's preparation.
- Version the retro document in the repository for future reference.
- At the next project kickoff, read the top 5 sentences from the previous retro first.

### Action Item Quality Criteria

| Criterion | Bad Example | Good Example |
| --- | --- | --- |
| Specificity | "Test harder" | "Run 10 integration test cases every Tuesday" |
| Accountability | "Team will check" | "QA owner reports results as an issue" |
| Deadline | "Reflect next time" | "Apply by week 2 of next project" |
| Measurability | "Improve quality" | "Keep defect reopen rate under 20%" |

### The 48-Hour Rule

If action items are not transferred to actual task-tracking tools within 48 hours after the retro, execution probability drops sharply. Therefore the following three steps are recommended immediately after the retro meeting ends:

1. Register action items as issues.
2. Confirm assignees and deadlines.
3. Pre-empt the next review date on the calendar.

The quality of a project retrospective is judged not by the eloquence of its sentences but by the execution rate of its next actions. Operating KPT alongside personal growth records converts the capstone from a one-off assignment into a long-term growth asset.

## Practical Anchor: Retrospective Checklist and Handoff Document

Retrospective quality is determined not by how long the reflection essay is, but by how many reusable rules it leaves for the next project. Therefore the retro document should not end with "went well / was tough" but must be converted into executable items.

### Retrospective Checklist

- Separate verified assumptions from failed assumptions in the original proposal.
- Classify schedule delays into technical issues vs. decision-making delays.
- Verify via git log whether the branch strategy was actually followed.
- Record root causes for repeatedly failing CI/CD pipeline stages.
- Reflect presentation slide and demo script improvement points in the next template.

### Next-Project Handoff Document Template

| Item | This Project Lesson | Next Project Rule |
| --- | --- | --- |
| Problem definition | Broad user scope caused early instability | Document excluded users by end of week 1 |
| Schedule management | Insufficient test buffer | Fix 0.5 days/week for regression testing |
| Collaboration method | Inconsistent PR review standards | Lock code-review checklist |
| Presentation prep | Too few rehearsals | 2 rehearsals/week starting 2 weeks before |

When the retrospective document reaches this level, the capstone transforms from a one-time assignment into the team's operational asset. That is the result this final chapter must secure.

## How a Senior Engineer Thinks

- Start from *facts*.
- *Causes* are *systemic*.
- *Actions* are *small*.
- *Responsibility* is *shared*.
- *Learning* is *documented*.

## Checklist

- [ ] *KPT* table.
- [ ] *Data* gathered.
- [ ] *Five Whys*.
- [ ] *Three* next actions.

## Practice Problems

1. State the meaning of *KPT* in one line.
2. State what *Five Whys* is in one line.
3. State the *next-action* format in one line.

## Wrap-up and Next Steps

A retrospective is both the final document of this project and the first document of the next one. When KPT, data, cause analysis, and next actions are captured together, the semester's failures and wins become durable project memory. This concludes the Capstone Project 101 series.

## Answering the Opening Questions

- **What does it take to prevent a retrospective from devolving into blame games?**
  - This article unpacks project retrospectives not as a simple definition but through concrete situations and decision processes encountered in practice. Follow the examples and checklists in each section to apply them to your own situation.
- **Why is the KPT format especially useful for beginner teams?**
  - Referring to the example code and matrices presented in this article, you can concretely feel what good judgment criteria look like. Understanding "in what situation do you set such criteria" matters more than the numbers themselves.
- **What part of a retrospective does data make more solid?**
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
- [Capstone Project 101 (8/10): Schedule Management](./08-schedule-management.md)
- [Capstone Project 101 (9/10): Building Presentation Materials](./09-presentation-materials.md)
- **Project Retrospective (current)**

<!-- toc:end -->

## References

### Official docs and practical guides

- [Agile Retrospectives](https://pragprog.com/titles/dlret/agile-retrospectives/)
- [The Five Whys](https://en.wikipedia.org/wiki/Five_whys)
- [Google SRE — Postmortem Culture](https://sre.google/sre-book/postmortem-culture/)
- [Project Retrospectives](https://retrospectives.com/)

Tags: Capstone, Retrospective, Learning, Reflection, Beginner
