---
series: capstone-project-101
episode: 7
title: "Capstone Project 101 (7/10): Choosing the Tech Stack"
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
  - TechStack
  - Decision
  - Architecture
  - Beginner
seo_description: A beginner-friendly tour of choosing a capstone tech stack by weighing familiarity, learning cost, and ops burden.
last_reviewed: '2026-05-14'
---

# Capstone Project 101 (7/10): Choosing the Tech Stack

Tech-stack decisions in capstones usually mix two different desires: the urge to try something new and the obligation to finish the semester with a stable demo.

Those goals often pull in opposite directions. The right stack is therefore not the most impressive one, but the one your team can operate without burning the schedule on tooling friction.

This is post 7 in the Capstone Project 101 series. It defines a practical stack-selection rubric built on familiarity, learning cost, operational burden, and documentation strength.


![capstone project 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/capstone-project-101/07/07-01-the-flow-at-a-glance.en.png)
*capstone project 101 chapter 7 flow overview*
> Stack choices matter less than knowing why you picked each piece and how to explain it in a demo.

## Questions to Keep in Mind

- Why is the newest technology not automatically the best choice?
- How does familiarity map directly to schedule risk?
- How should teams separate learning cost from operational burden?

## What You Will Learn

- Assessing *familiarity*
- Comparing *learning curves*
- Checking the *ecosystem*
- Estimating *ops cost*
- Comparing *alternatives*

## Why It Matters

Trying new technology is not inherently bad. The risk appears when the team treats learning time as if it were outside the project schedule. Unfamiliar frameworks increase debugging, deployment, and documentation-reading time together.

Operational burden matters separately too. A tool that feels simple on a laptop may become fragile in a demo environment. Deployment steps, configuration drift, and error handling all belong in the decision.

## The flow at a glance

## Practical artifact: a lightweight ADR

Stack decisions get revisited constantly when they only exist in conversation. A short ADR like the one below preserves the context.

```text
Title: choose Flask as the backend framework
Context: three of four teammates have Flask experience and the demo must ship in six weeks
Alternatives: FastAPI, Django
Decision: Flask has the lowest learning cost, the simplest deployment path, and sufficient documentation
Known downside: weaker built-in structure and API documentation than FastAPI
Review trigger: reconsider if authentication, async APIs, or admin features expand significantly
```

## What to validate first

- Write familiarity separately from learning cost.
- Include deployment and failure handling in operational burden.
- Keep alternatives to two or three realistic options.
- Add review triggers so the team knows when a new decision is justified.

## Key Terms

- **familiarity**: prior *experience*.
- **learning curve**: *learning cost*.
- **ecosystem**: libraries and *community*.
- **ops**: *deploy* and *run*.
- **alternative**: a *backup choice*.

## Before/After

**Before**: Always use the *newest* stack.

**After**: Choose by *familiarity + cost*.

## Hands-on: Decision Table

### Step 1 — List candidates

```python
candidates = ["FastAPI", "Flask", "Django"]
```

### Step 2 — Score familiarity

```python
familiar = {"FastAPI": 4, "Flask": 5, "Django": 2}
```

### Step 3 — Estimate learning cost

```python
learning_cost = {"FastAPI": 2, "Flask": 1, "Django": 4}
```

### Step 4 — Estimate ops burden

```python
ops = {"FastAPI": 2, "Flask": 1, "Django": 3}
```

### Step 5 — Compute scores

```python
score = {k: familiar[k] - learning_cost[k] - ops[k] for k in candidates}
```

## What to Notice in This Code

- *Score* is *familiarity minus cost*.
- *Alternatives* are *three or fewer*.
- The *decision* is *documented*.

## Five Common Mistakes

1. **Choosing by *popularity* only.**
2. **Ignoring *familiarity*.**
3. **Forgetting *ops cost*.**
4. **Not recording the *decision*.**
5. **No *alternative* comparison.**

## How This Shows Up in Production

Companies record decisions in *ADRs*.

## How a Senior Engineer Thinks

- *Familiarity* is *speed*.
- *Learning* is a *cost*.
- *Ops* is *ongoing*.
- *Alternatives* are *written*.
- *Decisions* are *reversible*.

## Checklist

- [ ] *Three* candidates.
- [ ] *Familiarity* score.
- [ ] *Learning cost*.
- [ ] *Decision* record.

## Practice Problems

1. State the meaning of *ADR* in one line.
2. State why *familiarity* matters in one line.
3. Define *ops burden* in one line.

## Wrap-up and Next Steps

Tech-stack selection is risk shaping, not taste ranking. When familiarity, learning cost, operational burden, and written rationale stay together, the stack starts serving the project instead of dominating it. The next post turns those decisions into an executable schedule.

## Answering the Opening Questions

- **Why is the newest technology not automatically the best choice?**
  - The article treats Choosing the Tech Stack as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **How does familiarity map directly to schedule risk?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **How should teams separate learning cost from operational burden?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Capstone Project 101 (1/10): What is a Capstone Project](./01-what-is-capstone.md)
- [Capstone Project 101 (2/10): Choosing a Topic](./02-choosing-a-topic.md)
- [Capstone Project 101 (3/10): Defining the Problem](./03-defining-the-problem.md)
- [Capstone Project 101 (4/10): Organizing Requirements](./04-organizing-requirements.md)
- [Capstone Project 101 (5/10): Splitting Team Roles](./05-splitting-team-roles.md)
- [Capstone Project 101 (6/10): Designing the MVP](./06-designing-the-mvp.md)
- **Choosing the Tech Stack (current)**
- Schedule Management (upcoming)
- Building Presentation Materials (upcoming)
- Project Retrospective (upcoming)

<!-- toc:end -->

## References

### Official docs and practical guides

- [Architecture Decision Records](https://adr.github.io/)
- [Choose Boring Technology](https://boringtechnology.club/)
- [The Twelve-Factor App](https://12factor.net/)
- [Thoughtworks Technology Radar](https://www.thoughtworks.com/radar)

Tags: Capstone, TechStack, Decision, Architecture, Beginner
