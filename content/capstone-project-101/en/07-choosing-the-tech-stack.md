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

This is the 7th post in the Capstone Project 101 series. It defines a practical stack-selection rubric built on familiarity, learning cost, operational burden, and documentation strength.


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

Keep the candidates to a comparable shortlist such as `FastAPI`, `Flask`, and `Django`.

### Step 2 — Score familiarity

Score familiarity in numbers, for example `FastAPI=4`, `Flask=5`, and `Django=2`, so the speed difference stays visible.

### Step 3 — Estimate learning cost

Use the same scale for learning cost, such as `FastAPI=2`, `Flask=1`, and `Django=4`.

### Step 4 — Estimate ops burden

Estimate ops burden in the same way, for example `FastAPI=2`, `Flask=1`, and `Django=3`, including deploy and incident response costs.

### Step 5 — Compute scores

For a simple comparison, it is enough to subtract learning cost and ops burden from familiarity.

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

- **Why isn't the newest stack always the right answer?**
  - This article unpacks tech stack selection not as a simple definition but through concrete situations and decision processes encountered in practice. Follow the examples and checklists in each section to apply them to your own situation.
- **Why does team familiarity directly connect to schedule?**
  - Referring to the example code and matrices presented in this article, you can concretely feel what good judgment criteria look like. Understanding "in what situation do you set such criteria" matters more than the numbers themselves.
- **How should you weigh learning cost versus operational burden?**
  - The core message of this article is that regardless of what evaluation criteria you use, it never ends with a single judgment. Recording criteria in documents early on, so the same mistakes aren't repeated when looking back later—that process itself leads a project to success.
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
