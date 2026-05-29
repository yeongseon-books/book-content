---
series: data-science-career-101
episode: 7
title: "Data Science Career 101 (7/10): The Case Interview"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - DataCareer
  - CaseInterview
  - ProductSense
  - Metrics
  - Beginner
seo_description: Master structured problem-solving for data case interviews — clarification, metric design, hypothesis generation, and decision proposals.
last_reviewed: '2026-05-14'
---

# Data Science Career 101 (7/10): The Case Interview

Case interviews often feel abstract because they do not offer the comforting shape of a coding problem. There is no obvious schema, no single query to write, and no algorithm name to anchor on. That makes many candidates answer too quickly and confuse brainstorming with structured reasoning.

What interviewers usually want instead is a visible thinking process. Can you clarify the problem, choose the metric that matters, generate competing hypotheses, propose a concrete data plan, and still close with a decision rather than an endless list of possibilities?

This is the 7th post in the Data Science Career 101 series.


![data science career 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-science-career-101/07/07-01-concept-at-a-glance.en.png)
*data science career 101 chapter 7 flow overview*
> In case interviews, what matters most is not knowing every tool or concept, but asking the right questions at each stage and knowing when you have a good answer.

## Questions to Keep in Mind

- What does a case interview actually test in a data candidate?
- Why should clarification come before analysis?
- How do you choose a north star metric and supporting metrics?

## Why It Matters

Technical skill alone does not solve ambiguous product problems.

As data roles become more embedded in product and business teams, the ability to structure a fuzzy situation becomes as important as the ability to query or model the underlying data.

A case interview feels open-ended because it is. You need to structure the ambiguity yourself: ask clarifying questions, propose a frame, estimate numbers, and explain your reasoning at each step.

## Key Terms

- **product sense**: The ability to read how features and metrics affect user experience.
- **north star metric**: The single top-level metric representing a product's core value.
- **hypothesis**: A testable explanation for an observed change.
- **A/B test**: A controlled experiment comparing two conditions.
- **trade-off**: A situation where gaining one thing requires losing another.

## Before/After

**Before**: "I just throw out numbers."

**After**: "I follow Problem to Metric to Hypothesis to Data to Decision."

## Hands-on: Five-Step Frame

These five steps form an answer template you can use for any case question. If you skip the first step, the metric and data plan that follow will often aim at the wrong target.

### Step 1 — Clarify

```text
"DAU dropped" = which segment, what period?
```

Clarification is not a stalling tactic. It prevents you from solving the wrong problem. Always confirm the segment, time window, and any recent changes before proceeding.

### Step 2 — Metric

```text
- north star metric
- two supporting metrics
```

One north star metric plus two supporting metrics gives the answer a center of gravity. Without a defined metric, the conversation drifts into abstraction quickly.

### Step 3 — Hypothesis

```text
- product change
- external event
- data pipeline
```

Never settle on a single hypothesis. Propose at least three that differ in nature—product change, external event, and data/pipeline issue—so your exploration stays balanced.

### Step 4 — Data

```text
- which query, which comparison
- A/B feasibility
```

"I would look at the data" is too vague. Specify which comparison you would run, which logs you need, and whether an experiment is feasible. This makes your plan sound executable.

### Step 5 — Decision

```text
- recommended action
- risks
- follow-up measurement
```

A case answer must end with a conclusion. State the recommended action, acknowledge the risks, and describe how you would measure whether the decision worked.

## Data Team Structures and Collaboration Patterns

Case interviews do not only test individual reasoning—they also assess whether you can solve problems within a team context. Understanding how data teams are organized helps you give more realistic answers, especially when the interviewer asks "who would you work with?" or "how would you get buy-in?"

| Team Structure | Characteristics | Strengths | Risks | Best Fit |
| --- | --- | --- | --- | --- |
| Centralized | Data org provides shared services | Standardization, quality control | Slow response to product needs | Large enterprises needing governance |
| Embedded | Data people sit inside product teams | Fast context, quick iteration | Inconsistent standards across teams | Experiment-heavy product organizations |
| Hybrid | Central platform + embedded analysts | Balance of standards and agility | Role boundary confusion | Mid-to-large growing organizations |

When you mention collaboration in a case answer, avoid the generic "I communicate well." Instead, anchor on the structure: "Since the metric definition might differ between the central team and the product team, I would first align on a metric spec before running the analysis."

## Collaboration Frame for Case Answers

| Stage | Key Question | Deliverable |
| --- | --- | --- |
| Problem alignment | Who is the final decision-maker? | Responsibility/decision-path table |
| Metric agreement | What does success/failure look like? | KPI definition document |
| Execution split | Who handles analysis, implementation, validation? | Role assignment matrix |
| Result sharing | At what cadence do we share findings? | Weekly report/review note |

## Real Job Postings as Case Practice

Case interviews become more concrete when you convert actual job posting language into practice questions:

| Job Posting Phrase | Mock Case Question | Required Answer Elements |
| --- | --- | --- |
| "Retention improvement through data analysis" | "Monthly retention dropped—what do you check first?" | Segment decomposition, cohort criteria, event definition |
| "New feature performance measurement" | "How do you judge success two weeks after launch?" | North star + guardrail metrics + time window |
| "Marketing efficiency optimization" | "CAC is rising—what hypotheses do you form?" | Channel-level hypotheses, experiment feasibility, decision criteria |

Practice each question with a 3-minute answer, 2-minute challenge response, and 1-minute summary. This structure reduces the habit of improvising and builds reliable problem-solving presentation.

## Case Interview Script: Question → Structure → Estimate → Decide

Case interviews test structured decomposition more than fast arithmetic. Internalize this script to stay stable even in unfamiliar domains:

```text
1) Restate the question: agree on success metric and time horizon.
2) Decompose: split along 3-4 axes (user, funnel, price, channel).
3) State assumptions: declare needed numbers explicitly.
4) Calculate: verify intermediate results step by step.
5) Conclude: propose 2 executable actions and 1 risk.
```

Interviewers watch assumption management as much as calculation accuracy. Stating assumptions out loud dramatically increases logical credibility.

## What to Notice in This Code

- Clarifying buys time and quality.
- The metric anchors the conversation.
- Always reach a decision.

Many candidates treat case interviews like brainstorming sessions and stop before reaching a conclusion. Interviewers want to see structured thinking that closes with a recommendation, not an open-ended list of possibilities.

## Five Common Mistakes

1. **Answering immediately.**
2. **No metric defined.**
3. **Single hypothesis.**
4. **Vague data proposal.**
5. **Ending without a decision.**

## How This Shows Up in Production

Case-style questioning is common because real product and analytics work rarely arrives as a cleanly defined ticket.

The day-to-day version of this interview looks like a metric drop, a launch question, a retention problem, or a growth trade-off where the first useful step is not code but clarification.

## How a Senior Engineer Thinks

- Clarify first.
- Pick a north star.
- Three hypotheses.
- Concrete data plan.
- Close with a decision.

## Checklist

- [ ] Three clarifying questions.
- [ ] One metric plus supports.
- [ ] Three hypotheses.
- [ ] One decision.

## Practice Problems

1. A subscription service sees increased churn at month two—diagnose the cause and propose a priority response.
2. Ad budget drops 20% but signup targets remain—propose a plan to maintain goals.
3. After a price increase, revenue rose but repurchase rate fell—explain why.

## Wrap-up and Next Steps

Strong case answers move in a reliable sequence: clarify the scope, anchor on a metric, generate multiple hypotheses, ask for the right data, and then make a recommendation with risks and follow-up measurement attached.

The next post turns from interviews to the first 90 days after you land the job.

## Answering the Opening Questions

- **What do case interviews actually evaluate?**
  - They test your ability to structure ambiguous problems: clarifying scope, choosing metrics, generating competing hypotheses, proposing a data plan, and closing with a decision—not the volume of ideas you can brainstorm.
- **Why must you ask clarifying questions first when you hear the problem?**
  - Without clarification, you risk solving the wrong problem. Confirming the segment, time window, and recent changes prevents the entire analysis from aiming at the wrong target.
- **How should you choose a north star metric and supporting metrics?**
  - The north star represents the product's core value (e.g., weekly active usage for engagement products). Supporting metrics act as guardrails that catch unintended side effects of optimizing the north star.
<!-- toc:begin -->
## In this series

- [Data Science Career 101 (1/10): What Is a Data Career](./01-what-is-data-career.md)
- [Data Science Career 101 (2/10): Analyst vs Scientist vs Engineer](./02-analyst-scientist-engineer.md)
- [Data Science Career 101 (3/10): Designing the Learning Path](./03-learning-path.md)
- [Data Science Career 101 (4/10): The Data Portfolio](./04-data-portfolio.md)
- [Data Science Career 101 (5/10): SQL and Analytics Interviews](./05-sql-and-analytics-interview.md)
- [Data Science Career 101 (6/10): The ML Interview](./06-ml-interview.md)
- **The Case Interview (current)**
- Settling into the First Data Job (upcoming)
- Building Domain Expertise (upcoming)
- The Path to Senior in Data (upcoming)

<!-- toc:end -->

## References

- [Lewis C. Lin - Decode and Conquer](https://www.lewis-lin.com/decode-and-conquer)
- [Cracking the PM Interview](https://www.crackingthepminterview.com/)
- [Ben Thompson - Stratechery](https://stratechery.com/)
- [Ron Kohavi et al. - Trustworthy Online Controlled Experiments](https://experimentguide.com/)

Tags: DataCareer, CaseInterview, ProductSense, Metrics, Beginner
