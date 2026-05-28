---
series: data-science-101
episode: 9
title: "Data Science 101 (9/10): Result Interpretation"
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
  - Interpretation
  - Storytelling
  - Decision
  - Beginner
seo_description: A 5-step interpretation framework for turning model output and analysis results into business decisions, plus five common cognitive traps to avoid
last_reviewed: '2026-05-15'
---

# Data Science 101 (9/10): Result Interpretation

The model score is not the finish line. Someone still has to explain what changed, how certain that change is, who it applies to, and what action the team should take next. That translation step is where strong technical work often becomes weak communication.

Interpretation is not about making numbers sound impressive. It is about adding context, uncertainty, and practical significance until the result is honest enough to trust and clear enough to act on.

This is the 9th post in the Data Science 101 series. Here we turn raw analytical results into decision-ready language without overstating what the data can support.


![data science 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-science-101/09/09-01-concept-at-a-glance.en.png)
*data science 101 chapter 9 flow overview*
> At its core, Result Interpretation is about deciding what enters a system, where validation happens, and which signals stay for the next cycle—not about feature names.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Result Interpretation?
- Which signal should the example or diagram make visible for Result Interpretation?
- What failure should be prevented first when Result Interpretation reaches a real system?

## Questions This Post Answers

- How do you move from a metric change to a decision sentence?
- Why must uncertainty travel with the result instead of appearing in a footnote?
- Which interpretation traps make teams overclaim or underclaim?
- How do context and segmentation keep a result from being overgeneralized?

> Interpretation is the act of carrying numbers, context, and uncertainty together into one actionable statement.

## What You Will Learn

- A *result → decision* 5-step flow
- How to report *uncertainty* alongside numbers
- Five *cognitive biases* that distort interpretation
- A 5-step interpretation exercise
- Five common mistakes

## Why It Matters

When interpretation is *exaggerated*, it leads to *bad decisions*; when it is *understated*, opportunities are missed. Reporting *uncertainty alongside numbers* is the first step toward *trust*.

> *A good interpretation does not overclaim, yet it still enables a decision.*

The key boundary in this episode is between the concept itself and how it operates in a real system. You need to know where the data comes in, where the decision happens, and what signal must be recorded.

## Key Terms

- **Confidence Interval**: an *uncertainty range* around an estimate.
- **Effect Size**: the *magnitude of a difference* (more important than mere significance).
- **Practical Significance**: a difference that is *meaningful for the business*.
- **Cherry-picking**: the trap of *reporting only favorable* results.
- **Survivorship Bias**: looking *only at survivors* and missing the failures.

## Before / After

**Before**: *“Accuracy went up by 5%!”* — Where? For whom? How often?

**After**: *“On paid users (60K), the 7-day average accuracy moved from 89% to 91% (95% CI ±0.8%, n=14).”*

## Hands-on: 5-step Interpretation

### Step 1 — Write the numbers precisely

```text
A/B test result: conversion 3.2% (control) vs 3.6% (variant)
n = 50,000 per arm
```

### Step 2 — Report a confidence interval

```text
delta = +0.4pp (95% CI: +0.2pp ~ +0.6pp)
```

### Step 3 — Evaluate effect size

```text
relative lift = +12.5%
```

### Step 4 — Add context

```text
campaign window: 2 weeks; segment: paid users; device: desktop only
```

### Step 5 — Close with a decision

```text
Decision: roll out to 100% paid desktop users; monitor for 2 more weeks.
```

**Expected output:** a decision-ready paragraph that includes the result, the confidence interval, the affected segment, and the next action.

## What to Notice in This Code

- *Numbers* and *context* always travel as a *pair*.
- The *confidence interval* turns *decision risk* into a *number*.
- A *decision sentence* is what *closes* the report.

## Five Common Mistakes

1. **Looking at *p-values* only.** *Effect size* may still be tiny.
2. **Generalizing a *single segment* to *everyone*.** Variance gets hidden.
3. **Reporting *only positive* findings.** That is cherry-picking.
4. **Hiding *uncertainty*.** Decisions become overconfident.
5. **Ending the report *without a decision*.** No action follows.

## How This Shows Up in Production

Data team weekly reviews follow a *number → context → confidence interval → decision* template. *Pre-registration* of hypotheses (writing them down before the analysis) protects against *cherry-picking*.

## How a Senior Engineer Thinks

- Do not be *embarrassed* by uncertainty.
- *Always* close with a decision.
- Watch *effect size* more than *p-value*.
- *Split by segment* to expose variance.
- Make the *review template* a *team asset*.

## Checklist

- [ ] I can write a *confidence interval*.
- [ ] I can read *effect size*.
- [ ] I can *split by segment*.
- [ ] I can write a *decision sentence*.

## Practice Problems

1. Take *one past analysis* and *re-interpret* it through the *5-step flow*.
2. Write how you would report a result with *p=0.04 but only a 0.1% effect*.
3. List *three team rules* that would prevent *cherry-picking*.

## Wrap-up and Next Steps

Interpretation is the *final bridge* that carries *analysis into decisions*. The next episode follows a single *data project end to end*, pulling everything in this series together.

## Answering the Opening Questions

- **How can you turn numerical results into decision sentences?**
  - Follow this article's 5-step approach: bundle the raw figure, confidence interval, segment context, and action recommendation into one sentence. For example, writing `conversion 3.2% vs 3.6%`, `delta = +0.4pp`, `paid users`, `roll out` in one paragraph is the moment a number becomes a decision sentence.
- **Why must numbers and context always be written together?**
  - The same 2pp increase is easy to over-generalize without knowing who, when, and under what conditions it was measured. That's why the article specified writing `campaign window: 2 weeks; segment: paid users; device: desktop only` alongside numbers.
- **Why must effect size and uncertainty be reported simultaneously?**
  - `relative lift = +12.5%` alone can look large, but you need `95% CI: +0.2pp ~ +0.6pp` alongside to know how stable that difference is. Effect size shows the magnitude of action value; the confidence interval shows the risk of that judgment — with only one, decisions become either exaggerated or overly conservative.
<!-- toc:begin -->
## In this series

- [Data Science 101 (1/10): What Is Data Science?](./01-what-is-data-science.md)
- [Data Science 101 (2/10): Turning a Problem into a Data Problem](./02-problem-to-data-problem.md)
- [Data Science 101 (3/10): Data Collection](./03-data-collection.md)
- [Data Science 101 (4/10): Data Cleaning](./04-data-cleaning.md)
- [Data Science 101 (5/10): Exploratory Data Analysis](./05-exploratory-data-analysis.md)
- [Data Science 101 (6/10): Visualization](./06-visualization.md)
- [Data Science 101 (7/10): Modeling](./07-modeling.md)
- [Data Science 101 (8/10): Evaluation](./08-evaluation.md)
- **Result Interpretation (current)**
- End-to-End Data Project Flow (upcoming)

<!-- toc:end -->

## References

- [Andrew Gelman — Statistical Modeling Blog](https://statmodeling.stat.columbia.edu/)
- [Kahneman — Thinking, Fast and Slow](https://us.macmillan.com/books/9780374533557/thinkingfastandslow)
- [Stitch Fix — A/B Testing Lessons](https://multithreaded.stitchfix.com/)
- [Microsoft — Trustworthy Online Experiments](https://exp-platform.com/)

Tags: DataScience, Interpretation, Storytelling, Decision, Beginner
