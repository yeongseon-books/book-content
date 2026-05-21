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

This is post 2 in the Capstone Project 101 series. It explains how to compare candidate topics and how to shrink an attractive idea into a semester-sized project.


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

A shared comparison method makes those conversations faster. Instead of arguing from preference, the team can discuss impact, feasibility, risk, and demo clarity using the same rubric.

## The flow at a glance

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

- **idea**: a *candidate*.
- **filter**: rejection *criteria*.
- **matrix**: comparison *table*.
- **score**: a *number*.
- **pick**: *final selection*.

## Before/After

**Before**: You only chase *cool topics*.

**After**: You pick a *topic that fits your team*.

## Hands-on: Topic Comparison Matrix

### Step 1 — Candidates

```python
ideas = ["schedule_checker", "mood_diary", "campus_map"]
```

### Step 2 — Score axes

```python
axes = ["impact", "feasibility", "interest"]
```

### Step 3 — Score table

```python
score = {"schedule_checker": [4, 5, 4], "mood_diary": [3, 4, 5], "campus_map": [4, 3, 3]}
```

### Step 4 — Totals

```python
total = {k: sum(v) for k, v in score.items()}
```

### Step 5 — Pick

```python
pick = max(total, key=total.get)
```

## What to Notice in This Code

- *Comparison* makes the *decision* easy.
- *Axes* are the *criteria*.
- Look at *balance* too, not only *totals*.

## Five Common Mistakes

1. **Chasing *trends* only.**
2. **Overestimating *team capacity*.**
3. **Picking by *gut* with no *score table*.**
4. ***Mixing* axis definitions.**
5. **Not *keeping alternatives*.**

## How This Shows Up in Production

Product *priority meetings* use *similar matrices*.

## How a Senior Engineer Thinks

- Stay *small*.
- *Compare*.
- *Document*.
- Keep *alternatives*.
- Allow *revisits*.

## Checklist

- [ ] *Three or more candidates*.
- [ ] *Three axes*.
- [ ] *Score table*.
- [ ] *Reason for pick*.

## Practice Problems

1. Define *impact* in one line.
2. Define *feasibility* in one line.
3. State the meaning of *topic selection* in one line.

## Wrap-up and Next Steps

Topic selection is a delivery decision, not a popularity contest. When you score candidates by shared criteria and choose the option with the fastest demo payoff, later scoping becomes much easier. The next post turns that topic into a sharp problem statement.

## Answering the Opening Questions

- **What qualities make a topic strong enough for a capstone?**
  - The article treats Choosing a Topic as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **How do you separate a trendy idea from a deliverable one?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Which shared criteria should the team use when comparing options?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

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
