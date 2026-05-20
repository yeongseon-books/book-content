---
series: data-science-101
episode: 2
title: "Data Science 101 (2/10): Turning a Problem into a Data Problem"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - DataScience
  - ProblemFraming
  - Metrics
  - Workflow
  - Beginner
seo_description: A 5-step framing technique for turning vague business questions into measurable data questions, with the falsifiability traps to watch
last_reviewed: '2026-05-15'
---

# Data Science 101 (2/10): Turning a Problem into a Data Problem

Most analytics requests arrive as loose complaints, not well-formed questions. “Revenue feels down.” “Churn seems worse.” “Did that campaign work?” The problem is not that these questions are unimportant. The problem is that data cannot answer them until someone pins down the metric, the time window, and the population.

Strong data work starts before SQL, notebooks, or models. It starts when the team rewrites a vague request into a sentence that could be proven wrong. That single rewrite usually decides whether the rest of the project is fast and reliable or slow and argumentative.

This is post 2 in the Data Science 101 series. In this chapter, we turn problem framing into an explicit workflow you can reuse before any collection, EDA, or modeling begins.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Turning a Problem into a Data Problem?
- Which signal should the example or diagram make visible for Turning a Problem into a Data Problem?
- What failure should be prevented first when Turning a Problem into a Data Problem reaches a real system?

## Big Picture

![data science 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-science-101/02/02-01-concept-at-a-glance.en.png)

*data science 101 chapter 2 flow overview*

This picture places Turning a Problem into a Data Problem inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Turning a Problem into a Data Problem is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Questions This Post Answers

- Why are business questions usually too vague for data to answer directly?
- How do metric, time window, and population narrow the scope of analysis?
- What makes a data question falsifiable instead of merely interesting?
- How does stronger framing shorten the rest of the project?

> A data question becomes tractable only after you lock the metric, the time window, the population, and the testable claim.

## What You Will Learn

- A 5-step framing for *business question → data question*
- How to pick a *measurable metric*
- How to write a *falsifiable hypothesis*
- A *5-step* framing exercise
- Five common traps

## Why It Matters

A *fuzzy question* gives you *no way to choose* the right data. *Framing* is *half of the analysis*.

> *One precise sentence saves *three weeks* of analysis.*

## Concept at a Glance

## Key Terms

- **Metric**: a *number* you can measure (DAU, conversion rate, revenue).
- **Window**: the *time range* of analysis (last 30 days).
- **Population**: the *group* you analyze (paid subscribers).
- **Hypothesis**: a statement that *could be wrong*.
- **Counterfactual**: the *“what if” scenario* — what would have happened without the change.

## Before / After

**Before**: *“Why did revenue drop?”* → no idea where to start.

**After**: *“Did paid-subscriber MRR drop more than 5% in the last 30 days vs the previous 30 days?”* → one query.

## Hands-on: 5-step Framing

### Step 1 — Write the vague question

```text
"Revenue feels like it's dropping"
```

### Step 2 — Pick a metric

```text
metric = monthly_revenue
```

### Step 3 — Pick a window

```text
window = last 30 days vs previous 30 days
```

### Step 4 — Narrow the population

```text
population = paid subscribers (excluding trials)
```

### Step 5 — Rewrite as falsifiable

```text
"Paid-subscriber monthly revenue dropped more than 5% in the last 30 days versus the prior 30 days."
```

**Expected output:** one falsifiable question that explicitly names the metric, time window, and target population.

## What to Notice in This Code

- The *metric* is the spine of the analysis.
- *Window* and *population* keep the comparison *fair*.
- A hypothesis must be *falsifiable* before the data can answer.

## Five Common Mistakes

1. **Choosing the *metric last*.** The analysis loses direction.
2. **Using *different windows* across teams.** Comparisons become *unfair*.
3. **Letting the *population shift*.** Trends get *contaminated*.
4. **Writing *unfalsifiable* hypotheses.** *“We are growing”* can never be proven or disproven.
5. **Asking *several questions at once*.** Answers blur together.

## How This Shows Up in Production

When PMs send a *fuzzy request*, the data team *rewrites* it through the 5-step frame and replies with a *clear question*. Many teams treat this as a *question review* — same rigor as a code review.

## How a Senior Engineer Thinks

- Pick the *metric first*.
- Document *window and population* explicitly.
- Always check *falsifiability*.
- Treat *question review* as seriously as *code review*.
- *If you can't answer it*, rewrite the question.

## Checklist

- [ ] I can write *metric, window, population* clearly.
- [ ] I can write a *falsifiable hypothesis*.
- [ ] I understand *counterfactual*.
- [ ] I can rewrite a *vague request* as a clean question.

## Practice Problems

1. Frame *“churn is up”* using the 5-step process.
2. Write 3 *unfalsifiable* hypotheses, then rewrite each to be *falsifiable*.
3. Pick one metric and show how *different windows* change the conclusion.

## Wrap-up and Next Steps

Only *answerable questions* are the start of analysis. Next, we will look at *how to collect* the data behind those questions.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Turning a Problem into a Data Problem?**
  - The article treats Turning a Problem into a Data Problem as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Turning a Problem into a Data Problem?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Turning a Problem into a Data Problem reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Data Science 101 (1/10): What Is Data Science?](./01-what-is-data-science.md)
- **Turning a Problem into a Data Problem (current)**
- Data Collection (upcoming)
- Data Cleaning (upcoming)
- Exploratory Data Analysis (upcoming)
- Visualization (upcoming)
- Modeling (upcoming)
- Evaluation (upcoming)
- Result Interpretation (upcoming)
- End-to-End Data Project Flow (upcoming)

<!-- toc:end -->

## References

- [Google — Rules of Machine Learning (Rule #1)](https://developers.google.com/machine-learning/guides/rules-of-ml)
- [Cassie Kozyrkov — How to Ask Smart Questions](https://kozyrkov.medium.com/)
- [Stitch Fix — A/B Testing Lessons](https://multithreaded.stitchfix.com/)
- [Andrew Gelman — Statistical Modeling Blog](https://statmodeling.stat.columbia.edu/)

Tags: DataScience, ProblemFraming, Metrics, Workflow, Beginner
