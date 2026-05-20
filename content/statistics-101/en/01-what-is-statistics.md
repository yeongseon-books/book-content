---
series: statistics-101
episode: 1
title: "Statistics 101 (1/10): What Is Statistics?"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Statistics
  - Fundamentals
  - DataAnalysis
  - Beginner
  - Concept
seo_description: An introduction to descriptive and inferential statistics and the thinking flow that turns data into business decisions, with a 5-step exercise
last_reviewed: '2026-05-04'
---

# Statistics 101 (1/10): What Is Statistics?

As data accumulates, so do numbers. But more numbers do not automatically produce better judgment. Monthly revenue is up, conversion changed, survey satisfaction looks high—those statements all contain numbers, but they do not say whether the conclusion is stable enough to trust.

Statistics is the tool that closes that gap. It is not just a way to format numbers neatly. It is a way to move from observation to a decision while keeping uncertainty visible.

This is the first post in the Statistics 101 series. Here we will split statistics into its two major branches—descriptive and inferential statistics—and build the basic flow that connects data to a decision.

## Questions to Keep in Mind

- What does statistics actually study?
- How are descriptive statistics and inferential statistics different?
- How does statistics connect numbers to decision-making?

## Big Picture

![statistics 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/statistics-101/01/01-01-concept-at-a-glance.en.png)

*statistics 101 chapter 1 flow overview*

This picture places What Is Statistics? inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of What Is Statistics? is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Why It Matters

As data piles up, the question *“is this really true?”* shows up more and more often. Statistics is the tool that *links hypothesis to evidence in numbers* — making *uncertain decisions less uncertain*.

> *Good statistical thinking produces decisions, not numbers.*

## Concept at a Glance

## Key Terms

- **Descriptive Statistics**: statistics that *summarize* data (mean, variance, etc.).
- **Inferential Statistics**: statistics that *infer the population* from a *sample*.
- **Population vs Sample**: *all* vs *part*.
- **Estimate**: the *guess* about the *true value* in the population.
- **Uncertainty**: the error that *always* accompanies an estimate.

## Before / After

**Before**: *“Revenue went up this month!”* — By how much? Is it statistically meaningful?

**After**: *“Monthly revenue is up by 6.2% on average (95% CI ±1.5%, n=30 days) — statistically significant vs last month.”*

## Hands-on: 5-step Statistical Thinking

### Step 1 — Define the question

```text
Q: "Did this month's marketing campaign improve click-through rate?"
```

### Step 2 — Collect data

```python
import pandas as pd
df = pd.read_csv("clicks.csv")
print(df.shape, df.columns.tolist())
```

**Expected output:** something like `(2000, ['group', 'ctr'])`, which confirms the row count and the columns you expect to analyze.

### Step 3 — Summarize (descriptive)

```python
print(df.groupby("group")["ctr"].agg(["mean", "std", "count"]))
```

**Expected output:** a small table with one row per group and columns for mean CTR, standard deviation, and sample count.

### Step 4 — Infer

```python
from scipy.stats import ttest_ind
a, b = df.loc[df.group == "control", "ctr"], df.loc[df.group == "test", "ctr"]
print(ttest_ind(a, b, equal_var=False))
```

**Expected output:** a `TtestResult(statistic=..., pvalue=...)` object. The p-value is the first signal for whether the observed gap is plausibly just noise.

### Step 5 — Decide

```text
Decision: p < 0.01 & lift +0.4pp → roll out the campaign to all users
```

## What to Notice in This Code

- The *3-tier structure* — *describe → infer → decide*.
- *Group comparison* starts with a *t-test*.
- A *decision sentence* is what *closes* the analysis.

## Five Common Mistakes

1. **Looking only at the *mean*.** You also need *variance* and the *distribution*.
2. **Treating the *sample* like the *population*.** Forgetting *uncertainty*.
3. **Confusing *p-value* with *effect size*.**
4. **Reading statistics *without visualization*.** Distorted distributions slip by.
5. **Ending the report *without a decision*.** The point of the analysis is lost.

## How This Shows Up in Production

A/B testing, revenue forecasting, anomaly detection, quality control — *every data-driven decision* sits on a base of statistics. Even *one cell on a dashboard* is an *estimate*; reporting it *with its uncertainty* is what builds *trust*.

## How a Senior Engineer Thinks

- Read the *distribution* before the *mean*.
- *Always* attach *uncertainty* to an estimate.
- Shorten the *question → data → decision* loop.
- Use *visualization* and *statistics* together.
- Remember statistics is the *language of decisions*.

## Checklist

- [ ] I can write the *question* in one line.
- [ ] I can *summarize* data with descriptive statistics.
- [ ] I can read *uncertainty* through inference.
- [ ] I close with a *decision sentence*.

## Practice Problems

1. Compute the mean and variance of *some everyday data* (e.g., daily study time).
2. Explain the difference between *population* and *sample* in *one sentence*.
3. Recall *one statistical report* that ended with a clear decision and write its structure down.

## Wrap-up and Next Steps

Statistics is the tool that moves *uncertainty* into *decisions*. The next episode dives into the most basic summary tools — *mean, median, and variance*.

## Answering the Opening Questions

- **What does statistics actually study?**
  - The article treats What Is Statistics? as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **How are descriptive statistics and inferential statistics different?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **How does statistics connect numbers to decision-making?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- **What Is Statistics? (current)**
- Mean, Median, and Variance (upcoming)
- Distributions (upcoming)
- Sample and Population (upcoming)
- Estimation (upcoming)
- Confidence Interval (upcoming)
- Hypothesis Testing (upcoming)
- Correlation and Regression (upcoming)
- Understanding p-value (upcoming)
- Statistical Thinking (upcoming)

<!-- toc:end -->

## References

- [Khan Academy — Statistics and Probability](https://www.khanacademy.org/math/statistics-probability)
- [OpenIntro Statistics](https://www.openintro.org/book/os/)
- [scipy.stats — Statistical Functions](https://docs.scipy.org/doc/scipy/reference/stats.html)
- [Seeing Theory — Visual Introduction](https://seeing-theory.brown.edu/)

Tags: Statistics, Fundamentals, DataAnalysis, Beginner, Concept
