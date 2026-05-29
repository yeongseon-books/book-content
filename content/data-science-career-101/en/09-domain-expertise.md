---
series: data-science-career-101
episode: 9
title: "Data Science Career 101 (9/10): Building Domain Expertise"
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
  - Domain
  - Expertise
  - BusinessSense
  - Beginner
seo_description: Strengthen your impact as a data professional by building domain expertise and connecting technical analysis to business value and strategic goals.
last_reviewed: '2026-05-14'
---

# Data Science Career 101 (9/10): Building Domain Expertise

At some point in a data career, technical competence stops being the main differentiator. Two people can write the same query or build the same dashboard, but one of them will ask a much better follow-up question because they understand the business language, the decision context, and the operational reality behind the metric.

That is domain expertise. It is easy to postpone because there is always another technical topic to study, but even a modest amount of domain understanding can dramatically improve the quality of your questions, your prioritization, and your interpretation of the same numbers.

This is the 9th post in the Data Science Career 101 series.


![data science career 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-science-career-101/09/09-01-concept-at-a-glance.en.png)
*data science career 101 chapter 9 flow overview*
> In domain knowledge, what matters most is not knowing every tool or concept, but asking the right questions at each stage and knowing when you have a good answer.

## Questions to Keep in Mind

- Why does domain expertise change the quality of data work so much?
- How should you start learning the vocabulary and KPI structure of an industry?
- Why does field observation improve metric interpretation?

## What You Will Learn

- The definition of *domain*
- Learning the *glossary*
- Understanding key *metrics*
- *Field* observation
- A *continuous* loop

## Why It Matters

Technical patterns are often portable. Domain judgment is what makes the same pattern useful in the right place.

You cannot reliably interpret retention, fraud, churn, utilization, or margin if you do not understand the business model and the operating constraints behind those words. Domain expertise is what separates a person who knows how to run a query from a person who knows what question to ask.

## IC Staff vs Manager: Two Growth Paths

Before diving into how to build domain expertise, it helps to understand which path you are building it for. Senior individual contributors and managers both need domain knowledge, but they apply it differently.

| Dimension | IC Staff | Manager |
| --- | --- | --- |
| Mission | Solve the hardest technical problems in the domain | Enable the team to solve problems at scale |
| Influence method | Technical depth and written artifacts | People development and process design |
| Key deliverables | Architecture docs, models, reference implementations | Hiring plans, team roadmaps, stakeholder alignment |
| Success metric | Quality and reuse of solutions | Team velocity and retention |
| Daily work | Deep focus, code/analysis, design reviews | 1:1s, cross-team meetings, prioritization |
| Primary risk | Isolation from business context | Distance from technical reality |

Neither path is superior. The choice depends on what energizes you over a multi-year horizon.

### IC vs Manager Self-Check

| Question | IC Signal | Manager Signal |
| --- | --- | --- |
| What energizes me at the end of a long day? | Solving a hard technical puzzle | Watching someone on my team grow |
| Where do I want influence to come from? | Depth of expertise and artifacts | People and process design |
| What am I willing to sacrifice? | Broad organizational control | Hands-on technical depth |

If your answers lean one way consistently, that is the path worth investing in. Domain expertise compounds on both paths, but the application differs.

## Key Terms

- **domain**: An industry or business area with its own vocabulary, KPIs, regulations, and decision patterns.
- **glossary**: A curated list of defined terms that prevents miscommunication across teams.
- **KPI**: Key performance indicator—the metric a team uses to judge success.
- **playbook**: An operational response guide that codifies domain-specific best practices.
- **shadowing**: Spending time observing how another role (sales, ops, support) actually works day-to-day.

## Before/After

**Before**: "I tweak dashboards without knowing why the business cares about this number."

**After**: "I converse using KPIs and domain vocabulary, and my analysis connects to real decisions."

## Hands-on: Four-Week Domain Learning Project

Rather than vaguely "studying the industry," structure domain learning as a time-boxed project with deliverables.

| Week | Focus | Deliverable |
| --- | --- | --- |
| 1 | Vocabulary and glossary | 30-term glossary with definitions and examples |
| 2 | KPI structure and metric formulas | 5-KPI reference sheet with owners and consumers |
| 3 | Field observation and stakeholder interviews | Shadow notes + 3 questions surfaced |
| 4 | Synthesis and presentation | One-page domain brief shared with team |

### Step 1 — Build a Glossary

```text
- 30 words
- definition + example + common misuse
```

Start with the terms your team uses in Slack and meetings that you cannot define precisely. Precision here prevents weeks of misalignment later.

### Step 2 — Five Key Metrics

```text
- definition
- formula (numerator / denominator)
- consuming team
- decision it drives
```

For each metric, ask: "If this number moves 10%, what action does the team take?" If nobody can answer, the metric may be vanity.

### Step 3 — Field Shadowing

```text
- spend a day with sales or operations
- notes: what surprised you
- questions: what do they wish data could answer
```

Field observation reveals what dashboards hide. The gap between "what we measure" and "what actually happens" is where the best analysis questions live.

### Step 4 — External Study

```text
- one industry conference or report per quarter
- industry news RSS (2-3 sources)
- one competitive teardown per half
```

### Step 5 — Quarterly Retro

```text
- ten new words mastered
- three new metrics understood
- one domain insight applied to analysis
```

## Domain Expertise by Industry

Domain knowledge is not generic. What matters varies sharply by sector.

| Industry | Key Metrics | Common Misconception | Learning Method |
| --- | --- | --- | --- |
| E-commerce | GMV, conversion rate, return rate, LTV | "Revenue = success" (ignoring returns and CAC) | Shadow CS/ops, read refund logs, map the order lifecycle |
| Fintech | AUM, default rate, compliance score, NIM | "More users = more revenue" (ignoring risk exposure) | Study regulatory filings, attend compliance reviews |
| SaaS | MRR, churn, NRR, activation rate | "Low churn = healthy" (ignoring expansion revenue) | Join customer success calls, read cancellation surveys |

The fastest way to build credibility in any domain: learn what veterans *assume everyone already knows*, and close that gap explicitly.

## Expert Communication Template

When presenting analysis to domain experts, structure your message to show you understand their world:

```text
1) Observation: "We see [metric] moving [direction] over [period]."
2) Interpretation: "In the context of [domain factor], this likely means [hypothesis]."
3) Limitations: "This does not account for [known gap or confound]."
4) Proposal: "I recommend [action] and suggest we validate by [method]."
```

This four-line pattern signals domain awareness. It separates your analysis from generic dashboard commentary.

## What to Notice in This Code

- Vocabulary is the entry point to domain fluency.
- Metrics give direction only when you understand what decisions they drive.
- Field observation reveals the gap between measurement and operational reality.

## Five Common Mistakes

1. **Going deep on tech only.** Technical skill without domain context produces impressive work that misses the point.
2. **No vocabulary investment.** You cannot ask good questions in a language you do not speak.
3. **Vague metric definitions.** If two people define the same KPI differently, every analysis built on it is suspect.
4. **Never visiting the field.** Dashboards flatten reality. Observation restores the dimensions.
5. **Skipping external study.** Your company's view of the market is one perspective. External sources provide the others.

## How This Shows Up in Production

In domain-heavy industries such as fintech, healthcare, and gaming, the same metric can imply completely different actions depending on regulation, user behavior, and operating model.

That is why senior data people are often the ones who can translate between numbers and business reality without reducing either side to vague summaries. They have earned the vocabulary and context to make precise claims.

## How a Senior Engineer Thinks

- Vocabulary first—you cannot reason about what you cannot name.
- Define metrics until the formula is unambiguous and the consumer is clear.
- Observe the field regularly—operational reality shifts faster than dashboards update.
- Study externally to calibrate your company's assumptions against the market.
- Sustain the loop: glossary → metrics → observation → synthesis → repeat.

## Checklist

- [ ] Compiled a 30-term domain glossary with definitions and examples.
- [ ] Documented five KPIs with formulas, owners, and the decisions they drive.
- [ ] Completed at least one shadow day with a non-data team (sales, ops, support).
- [ ] Scheduled a quarterly domain retro to measure vocabulary and metric growth.

## Practice Problems

1. Pick one KPI your team uses. Write its exact formula, name who consumes it, and state what action a 10% change triggers.
2. Name one domain term you have been using loosely. Define it precisely in one sentence.
3. Describe one insight you could only get from field observation, not from a dashboard.

## Wrap-up and Next Steps

Domain expertise grows slowly, but it compounds hard. A stronger glossary leads to better questions, better questions lead to better metrics, and better metrics lead to more credible analysis. The investment pays off most visibly when your proposals stop needing translation—because you already speak the business language.

The next post closes the series by looking at what changes as you grow from junior execution toward senior impact.

## Answering the Opening Questions

- **Why does domain expertise change the quality of data work so much?**
  - Because the same technical skill applied to the wrong question produces zero value. Domain knowledge tells you which questions matter, which metrics drive decisions, and which interpretations are plausible given business constraints.
- **How should you start learning the vocabulary and KPI structure of an industry?**
  - Structure it as a four-week project: glossary first, then metric formulas with owners, then field observation, then a synthesis document. External study each quarter keeps the loop alive.
- **Why does field observation improve metric interpretation?**
  - Dashboards compress reality into numbers. Observation reveals the operational context—workarounds, edge cases, human decisions—that explains why a metric moves the way it does.

<!-- toc:begin -->
## In this series

- [Data Science Career 101 (1/10): What Is a Data Career](./01-what-is-data-career.md)
- [Data Science Career 101 (2/10): Analyst vs Scientist vs Engineer](./02-analyst-scientist-engineer.md)
- [Data Science Career 101 (3/10): Designing the Learning Path](./03-learning-path.md)
- [Data Science Career 101 (4/10): The Data Portfolio](./04-data-portfolio.md)
- [Data Science Career 101 (5/10): SQL and Analytics Interviews](./05-sql-and-analytics-interview.md)
- [Data Science Career 101 (6/10): The ML Interview](./06-ml-interview.md)
- [Data Science Career 101 (7/10): The Case Interview](./07-case-interview.md)
- [Data Science Career 101 (8/10): Settling into the First Data Job](./08-first-job.md)
- **Building Domain Expertise (current)**
- The Path to Senior in Data (upcoming)

<!-- toc:end -->

## References

- [Eric Evans - Domain-Driven Design](https://www.domainlanguage.com/ddd/)
- [Alistair Croll and Benjamin Yoskovitz - Lean Analytics](https://leananalyticsbook.com/)
- [Klipfolio - KPI Examples and Templates](https://www.klipfolio.com/resources/kpi-examples)
- [Josh Kaufman - The Personal MBA](https://personalmba.com/)

Tags: DataCareer, Domain, Expertise, BusinessSense, Beginner
