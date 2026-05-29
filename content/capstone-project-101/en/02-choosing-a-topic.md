---
series: capstone-project-101
episode: 2
title: "Capstone Project 101 (2/10): Choosing a Topic"
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
  - Topic
  - Ideation
  - Scope
  - Beginner
seo_description: A beginner-friendly tour of choosing a capstone topic covering criteria, candidate matrix, scoring, and final pick.
last_reviewed: '2026-05-14'
---

# Capstone Project 101 (2/10): Choosing a Topic

It is easy to generate impressive ideas. It is much harder to find an idea a student team can actually carry through one semester with a convincing demo.

A good capstone topic is not the flashiest topic. It is the one your team can explain, scope, build, and present without collapsing under delivery risk.

This is the 2nd post in the Capstone Project 101 series. It explains how to compare candidate topics and how to shrink an attractive idea into a semester-sized project.


![capstone project 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/capstone-project-101/02/02-01-the-flow-at-a-glance.en.png)
*capstone project 101 chapter 2 flow overview*
> Choosing well means balancing fresh ideas against the time constraint. The best topic is one where a demoable result appears within weeks, not months.

## Questions to Keep in Mind

- What qualities make a topic strong enough for a capstone?
- How do you separate a trendy idea from a deliverable one?
- Which shared criteria should the team use when comparing options?

## What You Will Learn

- *Criteria* for a good topic
- Building a *candidate list*
- *Comparison matrix*
- *Scope* tuning
- *Final* pick

## Why It Matters

When the topic is fuzzy, later requirements and scheduling become unstable too. Oversized ideas keep producing scope fights because nobody agreed on the real delivery boundary.

A team that picks well looks ahead at completion probability, not novelty. A capstone is not an idea contest — it is the exercise of building a small but convincing deliverable within a strict time box.

A shared comparison method makes those conversations faster. Instead of arguing from preference, the team can discuss impact, feasibility, risk, and demo clarity using the same rubric.

## Practical artifact: a topic comparison matrix

Keeping at least three candidates and scoring them on the same axes quickly reveals whether the team has a decision or just a favorite idea.

```text
Candidate | User pain | Impact | Feasibility | Data access | Demo clarity
Schedule conflict checker | High | 5 | 5 | 4 | 5
Mood diary recommender | Medium | 3 | 4 | 3 | 3
Campus navigation app | Medium | 4 | 2 | 2 | 4

Conclusion: the schedule conflict checker is the smallest option with the clearest demo payoff.
```

## What to validate first

- Check that the scoring axes are not duplicates in disguise.
- Keep late-breaking risks such as data access or integration friction as separate axes.
- Write one or two sentences next to the final pick so the score table does not become context-free.
- Preserve rejected candidates as fallback options for later scope changes.

## Key Terms

- **idea**: a topic candidate worth reviewing.
- **filter**: a criterion for early elimination.
- **matrix**: a table that lines candidates up side by side.
- **score**: a numeric rating on each axis.
- **pick**: the final selection.

## Before/After

**Before**: You only chase *cool topics*.

**After**: You pick a *topic that fits your team*.

## Hands-on: Topic Comparison Matrix

### Step 1 — Candidates

Start the comparison with at least three candidates such as `schedule_checker`, `mood_diary`, and `campus_map`.

Having at least three is important. With only two, the discussion becomes a for-or-against debate. With three or more, genuine comparison begins.

### Step 2 — Score axes

Split the score axes into distinct criteria such as `impact`, `feasibility`, and `interest`.

The axes reveal the team's values. Mixing user value, implementation feasibility, and team interest gives a balanced view across dimensions that naturally compete.

### Step 3 — Score table

For example, you might score `schedule_checker` as `(4, 5, 4)`, `mood_diary` as `(3, 4, 5)`, and `campus_map` as `(4, 3, 3)` so the reasoning stays visible.

Numbers are not written because they are perfect — they are written to expose the reasoning. The moment someone explains why they gave feasibility a 5, the team's hidden assumptions surface.

### Step 4 — Totals

Summarize the totals by adding each candidate's scores, but keep in mind that totals are only a quick comparison aid.

Totals are useful for a fast glance, but they are never absolute. Look at the balance of scores across axes too — a candidate that scores 5/5/1 is riskier than one scoring 4/4/3.

### Step 5 — Pick

You can describe the final pick as the candidate with the highest total, but also leave one or two sentences explaining why it won.

The final selection is not something the numbers do for you. It is the step where you close the team conversation using numbers as evidence. Recording why you chose a candidate makes later scope adjustments far easier.

## What to Notice in This Code

- A comparison structure lets the team argue from criteria, not emotion.
- Axes *are* the team's judgment criteria.
- Look at *balance* too, not only *totals*.
- Recording the reason for the pick lets you revisit the decision later.

## Five Common Mistakes

1. **Chasing trends only.** The latest buzzword does not guarantee a deliverable result.
2. **Overestimating team capacity.** First-time teams routinely oversize scope by 2–3×.
3. **Picking by gut with no score table.** Without a written rubric, the loudest voice wins.
4. **Mixing axis definitions.** If two axes overlap, scores lose discriminating power.
5. **Not keeping alternatives.** Dropping rejected candidates means starting from zero if scope changes.

## How This Shows Up in Production

Product priority meetings follow the same core pattern. Collect candidates, compare them by user value and implementation cost, and pick the one to push right now. Practicing a topic comparison matrix in a capstone is a small-scale rehearsal for real product judgment calls.

## How a Senior Engineer Thinks

- Start small — prove value before expanding scope.
- Put comparable criteria on the table — never compare apples to oranges.
- Document the selection rationale — future-you will thank present-you.
- Keep alternatives alive — conditions change.
- Allow revisits — a good process includes checkpoints.

## Checklist

- [ ] Three or more candidates listed.
- [ ] Three distinct scoring axes defined.
- [ ] Score table filled in with reasoning notes.
- [ ] Final selection reason documented in one or two sentences.

## Practice Problems

1. Define *impact* in one line.
2. Define *feasibility* in one line.
3. State the meaning of *topic selection* in one line.

## Deep Dive: Problem Definition Template and Requirements Spec

Once you pick a topic, resist jumping straight into implementation. Fix a problem definition document first. The most common error right after topic selection is the illusion that "everyone already understands the same problem." In practice, each team member imagines a different user and a different success criterion. The template below is a minimal document that surfaces those gaps quickly.

### Problem Definition Template

```text
[Problem Name]
One-line summary:

[Users]
Primary user 1:
Primary user 2:
Excluded users:

[Observations]
Current pain point:
When the pain occurs:
Evidence for the pain:

[Problem Statement]
Who struggles with what, when, and why:

[Success Criteria]
Quantitative metric 1:
Quantitative metric 2:
Qualitative metric 1:

[Key Assumptions]
Assumption A:
Assumption B:

[Out of Scope]
What we will NOT do this semester:
```

The real value of this template is not writing difficulty — it lowers review difficulty. When fields are fixed, teammates with different assumptions can immediately see where they conflict.

### Requirements Spec Example

| ID | Type | Requirement | Acceptance Criteria | Priority |
| --- | --- | --- | --- | --- |
| RQ-01 | Functional | Users can enter their timetable as text | 3 sample inputs saved without error | Must |
| RQ-02 | Functional | System identifies conflicting courses | 10 out of 10 conflict cases detected | Must |
| RQ-03 | Functional | Result screen highlights conflict zones visually | Key info visible within one scroll | Should |
| RQ-04 | Non-functional | Result computation returns within 1 second | Average response time ≤ 1 s | Must |
| RQ-05 | Non-functional | Usable on mobile screens | No layout breakage at 390 px width | Should |

### Template Application Checkpoints

- Verify that each problem statement maps 1:1 to a requirement.
- Check that every requirement has an acceptance criterion.
- If "Must" items exceed 60 % of total, suspect scope overload.
- Separate non-functional requirements from functional ones.
- Mark which items will appear in the presentation demo.

### Team Review Process

Keep document reviews under 20 minutes. The first 5 minutes: the author explains. The next 10 minutes: questions only. The last 5 minutes: finalize action items. Replace "good/bad" impressions with "which field is empty?" — that single shift raises document quality fast. Building this habit during topic selection accelerates every decision in later chapters.

## Practical Anchor: Topic Proposal Comparison and Gantt Chart

At the topic-selection stage, comparing written proposals matters more than open-ended brainstorming. Produce at least three proposals of similar length and evaluate them on identical criteria — this separates team preference from project risk.

### Topic Proposal Comparison Template

| Item | Candidate A | Candidate B | Candidate C |
| --- | --- | --- | --- |
| User problem clarity |  |  |  |
| Demo-ready within 2 weeks |  |  |  |
| Data accessibility |  |  |  |
| Team skill fit |  |  |  |
| Presentation impact |  |  |  |
| Summary (2 sentences) |  |  |  |

When filling the table, replace "I think it will work" with evidence. For example, if you score data accessibility low, specify whether the bottleneck is an API permission issue or a privacy regulation — the mitigation strategy differs.

### 4-Week Pre-Validation Gantt Chart

```text
Week             1    2    3    4
Problem definition ████
Data check            ████
Core feature spike         ████
Demo draft                      ████
Feedback loop                      ████
```

A Gantt chart at this stage is not about precision — it is about exposing dependencies. Drawing even this rough sketch right after topic selection clarifies "what must be ready by when." When the schedule slips later, it also makes obvious which item to cut first.

## Wrap-up and Next Steps

Topic selection is a delivery decision, not a popularity contest. When you score candidates by shared criteria and choose the option with the fastest demo payoff, later scoping becomes much easier. The next post turns that topic into a sharp problem statement.

## Answering the Opening Questions

- **What conditions should a good capstone topic meet?**
  - This article unpacks topic selection not as a simple definition but through concrete situations and decision processes encountered in practice. Follow the examples and checklists in each section to apply them to your own situation.
- **How do you distinguish an interesting idea from one you can actually execute?**
  - Referring to the example code and matrices presented in this article, you can concretely feel what good judgment criteria look like. Understanding "in what situation do you set such criteria" matters more than the numbers themselves.
- **What criteria should the team collectively reference when comparing candidates?**
  - The core message of this article is that regardless of what evaluation criteria you use, it never ends with a single judgment. Recording criteria in documents early on, so the same mistakes aren't repeated when looking back later—that process itself leads a project to success.
<!-- toc:begin -->
## In this series

- [Capstone Project 101 (1/10): What is a Capstone Project](./01-what-is-capstone.md)
- **Choosing a Topic (current)**
- Defining the Problem (upcoming)
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

- [Atlassian Decision Matrix](https://www.atlassian.com/work-management/project-management/decision-matrix)
- [The Mom Test](http://momtestbook.com/)
- [Jobs to Be Done overview](https://strategyn.com/jobs-to-be-done/)
- [How to Get Startup Ideas — Paul Graham](http://paulgraham.com/startupideas.html)

Tags: Capstone, Topic, Ideation, Scope, Beginner
