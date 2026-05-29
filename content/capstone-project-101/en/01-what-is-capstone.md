---
series: capstone-project-101
episode: 1
title: "Capstone Project 101 (1/10): What is a Capstone Project"
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
  - Project
  - Graduation
  - Career
  - Beginner
seo_description: A beginner-friendly tour of the capstone project covering goals, evaluation, and how it differs from regular coursework.
last_reviewed: '2026-05-14'
---

# Capstone Project 101 (1/10): What is a Capstone Project

Many teams introduce a capstone project as "the big final team assignment." That description is not wrong, but it does not explain why some teams finish with a coherent demo while others spend the semester chasing loosely connected features.

A capstone is better understood as a small product-delivery exercise. The team defines a problem, narrows scope, ships a demoable flow, and explains what it learned. Without that frame, the project keeps changing its own success criteria.

This is the first post in the Capstone Project 101 series. It defines what separates a capstone from ordinary coursework and establishes the delivery flow used throughout the series.

> Mental model: a capstone is not a course where you build many big features — it is a small product development exercise connecting problem definition through demo and retrospective in one practical flow.

![capstone project 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/capstone-project-101/01/01-01-the-flow-at-a-glance.en.png)
*capstone project 101 chapter 1 flow overview*
> The real distinction in a capstone is that you control the entire flow: problem choice, scope, demo shape, and retrospective. That control is the main learning.

## Questions to Keep in Mind

- How is a capstone project different from a regular class assignment?
- Why do some teams build features but still finish with a weak project story?
- What should you evaluate besides feature count?

## What You Will Learn

- Definition of *capstone*
- *Goals* and *evaluation*
- Difference from *assignments*
- *Team* roles
- Series *flow*

## Why It Matters

A capstone is the last bridge between school and industry. Regular assignments come with clear answers and rubrics, but a capstone forces you to decide what problem to solve, who the user is, where to stop building, and what to demo. The judgment process itself becomes the training target.

The same structure appears in real jobs. You explain the problem, organize user value, and produce a convincing result within a deadline. Teams that understand this frame grab the problem and demo before the feature list.

## Practical artifact: a one-page project brief

One simple way to separate a capstone from a generic assignment is to ask whether the team can produce a short brief like the one below before building features.

```text
Project title: Course schedule conflict checker
Primary users: freshmen and double-major students
Problem statement: students spend too long manually checking schedule conflicts before registration
Core value: confirm conflicts within 30 seconds
Demo bar: enter a sample timetable, show conflicts, and suggest alternatives
Success signal: a first-time user completes the main flow without explanation
```

## What to validate first

- Check whether the problem statement describes a user situation rather than a feature list.
- Confirm that the value is expressed as a measurable change such as time, confidence, or effort.
- Make sure the demo bar is realistic enough to reproduce during presentation week.
- Prefer observable success signals over vague team confidence.

## Key Terms

- **capstone**: a comprehensive project performed right before graduation.
- **stakeholder**: interested parties who have a stake in the outcome.
- **MVP**: the smallest verifiable product.
- **demo**: a live demonstration of the core flow.
- **retro**: a review that captures lessons from the project.

## Before/After

**Before**: You see it as a *big assignment*.

**After**: You see it as a *small product delivery exercise*.

## Hands-on: Capstone Definition Card

### Step 1 — One-line title

Write the title as one clear line, such as *course schedule conflict checker*.

A project title is not better when fancier — it is better when immediately understandable. A sharp one-line title makes team conversations sharper.

### Step 2 — Users

List the first user candidates briefly, such as `student` and `advisor`, so the scope stays visible.

Narrowing users narrows requirements. Conversely, targeting everyone inflates the project quickly.

### Step 3 — Value

Describe the value as a user-visible change: *cuts the time spent on registration*.

Value should describe a change, not a feature. Write what becomes easier, not what was built.

### Step 4 — Metric

Make the metric measurable: *users confirm conflicts within 30 seconds*.

A metric makes the success criteria explicit. "It feels convenient" is weaker than "they finish in 30 seconds."

### Step 5 — Demo

Decide on the demo package early, even if it is as simple as `demo.mp4` plus `README.md`.

Fixing the demo format early reveals which flows must be finished. Teams that scramble at the last minute tend to miss the core flow.

## What to Notice in This Code

- The *title* is one line.
- *Users* and *value* move as a pair.
- The goal is *measurable*.
- Fixing the *demo format* clarifies priorities.

## Five Common Mistakes

1. Picking a topic too big.
2. Vague user definition.
3. No measurement criteria — only impressionistic descriptions.
4. Building the demo last.
5. Treating the retrospective as a formality.

## How This Shows Up in Production

New-hire onboarding projects and internal pilots follow nearly the same structure. Define the problem in one sentence, pick a user, build a small demo, and use feedback to decide the next step. Someone who has truly experienced a capstone can explain *why* they built something, not just *what*.

## How a Senior Engineer Thinks

- Problem first.
- Start small.
- Make success measurable.
- Imagine the demo from day one.
- Turn the retro into an asset for the next project.

## Checklist

- [ ] I can explain the project in one line.
- [ ] The first user group is defined.
- [ ] The value is written as a change.
- [ ] The success criteria include numbers.
- [ ] The demo format is decided.

## Practice Problems

1. Define *capstone* in one line.
2. Define *MVP* in one line.
3. State the meaning of *measurement* in one line.

## Deep Dive: Topic Selection Matrix and Good vs. Bad Topics

The starting point of a capstone is topic selection. The reason this article is chapter 1 is that only teams who understand the capstone's essence can pick a topic realistically. A topic is not a noun you choose once — it is a criterion sentence that filters every decision throughout the semester. You must build a comparison framework first, then validate candidates through it.

### Topic Selection Evaluation Matrix

| Criterion | Question | 1-point | 3-point | 5-point | Weight |
| --- | --- | --- | --- | --- | --- |
| User problem clarity | Is who suffers what clearly defined? | User unclear | User group exists but situation vague | User and situation clear in one sentence | 0.25 |
| Verifiability | Can a demo and feedback happen within one semester? | No demo criteria | Demo possible but measurement weak | Demo and success metrics both clear | 0.20 |
| Feasibility | Can the team's skills actually build this? | Key tech completely unknown | Partial experience | Majority experienced in core tech | 0.20 |
| Data/resource access | Can you obtain the necessary data and environment? | No access path | Partial access | Available at project start | 0.15 |
| Presentation clarity | Can you explain problem → solution → result briefly? | Abstract explanation | Explainable but weak core | Persuasive within 3 minutes | 0.10 |
| Extensibility | Does an extension path exist beyond MVP? | No clear extension | Limited extension possible | 2+ clear extension hypotheses | 0.10 |

The total score is `sum of (item score × weight)`. But per-item variance matters more than the total. For example, a high total with low Verifiability creates risk during the late-semester demo prep. Conversely, a slightly lower total with high problem clarity and demo feasibility is a safer capstone pick.

### Good Topics vs. Bad Topics

| Dimension | Good example | Bad example | Key difference |
| --- | --- | --- | --- |
| Problem definition | Registration schedule conflict checking is slow | Innovate campus life with AI | Good topics have observable problems |
| User scope | Freshmen and double-major students | All students, faculty, external users | Good topics narrow the first user |
| Demo feasibility | 60-second demo with sample data | Requires large-scale real-time data integration | Good topics are reproducible on demo day |
| Technical complexity | Buildable with an existing framework | Multi-model, real-time streaming, recommendation engine simultaneously | Good topics limit core risks |
| Success criteria | First user confirms conflicts within 30 seconds | Improve user satisfaction | Good topics have clear measurement |

### Evaluation Procedure

1. Prepare at least 3 candidate topics.
2. Each team member scores independently first.
3. Discuss only items where scores diverge significantly.
4. Finalize second-round scores after discussion.
5. Record the final selection and rejection reasons in 3 sentences.

The purpose is not to eliminate disagreement but to make disagreement documentable. Different scores are natural. What matters is recording *why* views differed and preventing the same conflict from repeating.

### Validation Questions to Reduce Failure

- Can you describe this topic in one sentence starting with the user problem, not a feature name?
- Can you build the first demo within 2 weeks?
- Is there a fallback data path if the primary source is blocked?
- Can the core flow survive if one team member drops out?
- Can you demo on presentation day even with unstable internet?

If two or more answers are "no," shrink the topic. A capstone's goal is not the biggest product but the most convincingly completed one. Choose validation structure over ambition early — once that foundation is set, requirements, MVP, schedule, and presentation materials align naturally.

## Decision Documentation Patterns

The purpose of capstone documentation is not word count but leaving traces of judgment. Teams that record decision rationale learn at a fundamentally different density than those that don't. The patterns below apply across any chapter as minimum documentation rules.

### Decision Card Template

| Field | Guideline | Example |
| --- | --- | --- |
| Decision title | Short, verb-form | Fix input format to CSV |
| Background | Describe problem and constraints in ≤3 sentences | Need implementation stability 2 weeks before demo |
| Options | Compare at least 2 | CSV vs. direct Excel upload |
| Evaluation criteria | State time, risk, implementation difficulty | Learning cost, error probability |
| Final decision | One sentence | Adopt CSV input for MVP scope |
| Follow-up action | Convert to executable action | Add 5 parser validation tests |

### Risk Register Example

| Risk ID | Description | Likelihood | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- | --- |
| RK-01 | External data access delay | Medium | High | Prepare sample data fallback | Data lead |
| RK-02 | Demo environment network instability | Medium | High | Prepare offline video backup | Presenter |
| RK-03 | Integration test gaps | High | Medium | Fix weekly regression test slot | QA lead |
| RK-04 | Frequent requirement changes | Medium | Medium | Define change approval rules | Team lead |

A risk register is not a document for recording anxiety — it is a document for deciding priority. Viewing likelihood and impact together makes it clear which risks to reduce first.

### Weekly Review Questions

- Which of this week's decisions should be revisited next week?
- Was the schedule deviation caused by a technical issue or a decision delay?
- When a scope expansion request arrives, is the rejection criteria documented?
- Are test failures concentrated in a specific area?
- Is there sufficient documented rationale to explain decisions on presentation day?

### Recording Principles for Quality

First, write sentences short and verifiable. Second, whenever numbers are available, record numbers. Third, never separate decisions from actions. Fourth, update documents within 24 hours of a meeting. Fifth, never omit the reason for a change. Following these five principles transforms capstone documents from mere submissions into operational manuals for the next project.

## Practical Anchor: Project Proposal Draft and Branch Strategy

The first document to create after defining the capstone is a proposal draft. A proposal is not a long document — it is a document confirming the team agreed on the same problem in the same words. The template below fits on one page.

### One-Page Project Proposal Template

```text
Project name:
Problem summary (3 sentences):
Primary users:
Core scenario (≤5 steps):
MVP scope (included):
MVP non-scope (excluded):
Success metrics (2 numbers):
Demo method (live/recorded/hybrid):
Key risks and mitigation:
```

The strength of this template is fast consensus. Even when team members have different writing styles, fixed fields prevent arguments from scattering. Explicitly listing *MVP non-scope* helps control scope creep mid-semester.

### Git Branch Strategy: Minimum Rules

Once document consensus is done, define repository rules immediately. A simple branch strategy is the most stable approach early on.

| Item | Rule | Reason |
| --- | --- | --- |
| Default branch | Protect `main` | Block direct pushes to maintain quality |
| Work branches | `feat/*`, `fix/*`, `docs/*` | Identify change purpose from the name |
| Merge method | PR + 1 approval | Prevent omissions from solo judgment |
| Merge condition | Tests pass, no conflicts | Prevent regression failures before demo |

```bash
git checkout -b feat/problem-card
git add .
git commit -m "add initial problem card and scope"
git push -u origin feat/problem-card
```

Branch strategy is about consistency, not advanced features. The biggest loss in capstone teams is not a wrong tech choice but losing change history. Even small changes should go through a PR to leave a record.

## Wrap-up and Next Steps

A capstone starts with a delivery frame, not a feature list. When problem definition, requirements, MVP, demo, and retrospective stay connected, the rest of the project becomes easier to steer. The next post focuses on choosing a topic that can survive that full flow.

## Answering the Opening Questions

- **How does a capstone project differ from a regular assignment?**
  - Regular assignments have predetermined answers and grading criteria, but a capstone requires you to define your own standards from problem definition through to demo. The article uses a one-page project brief, evaluation matrix, and branch rules to show that the judgment process — not just the artifact — is the training target.
- **Why do some teams build features but still finish with a weak project story?**
  - Because they never established a delivery frame. Without a problem statement that describes a user situation, a measurable success signal, and a demo bar fixed early, feature work accumulates without converging toward a convincing narrative.
- **What should you evaluate besides feature count?**
  - How clearly the problem was defined, how persuasively the demo was built, and how well the team's decision process was documented. The topic selection matrix and decision card template in this article give concrete evaluation criteria that survive contact with a review panel.
<!-- toc:begin -->
## In this series

- **What is a Capstone Project (current)**
- Choosing a Topic (upcoming)
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

- [Atlassian Project Management Guide](https://www.atlassian.com/agile/project-management)
- [Scrum Guide](https://scrumguides.org/scrum-guide.html)
- [The Lean Startup](http://theleanstartup.com/)
- [Inspired — Marty Cagan](https://svpg.com/inspired-how-to-create-products-customers-love/)

Tags: Capstone, Project, Graduation, Career, Beginner
