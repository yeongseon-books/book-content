---
series: statistics-101
episode: 4
title: "Statistics 101 (4/10): Sample and Population"
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
  - Sampling
  - Population
  - Bias
  - Beginner
seo_description: How a sample becomes representative of a population, focusing on random sampling and the most common sources of sampling bias to avoid
last_reviewed: '2026-05-04'
---

# Statistics 101 (4/10): Sample and Population

Statistics usually begins without complete information. We cannot survey every customer, destructively test every manufactured item, or run every user through the same experiment. So we look at a part and try to say something about the whole.

The hard part is representativeness. If the sample does not resemble the population closely enough, even a careful analysis starts from the wrong place.

This is the 4th post in the Statistics 101 series. Here we will clarify the relationship between population, sample, parameter, and statistic, then explain why random sampling and sampling bias sit at the foundation of statistical work.


![statistics 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/statistics-101/04/04-01-concept-at-a-glance.en.png)
*statistics 101 chapter 4 flow overview*
> You can *never* measure the entire population — so statistics teaches you how to *measure the sample* and *speak confidently* about the whole.

## Questions to Keep in Mind

- How do population and sample differ?
- What makes a sample representative enough to trust?
- Why does random sampling appear so often in statistics?

## Why It Matters

*Every statistical conclusion* starts from a *sample*. With a *bad sample*, even a *perfect analysis* gives a *wrong conclusion*.

> *Garbage sample → Garbage decision.*

## Concept at a Glance
Every statistic you compute comes from a *sample*—a *part* of the population you actually care about. The quality of your inference depends on whether that sample is *representative* and *large enough*.
## Key Terms

- **Population**: the *whole group* we want to learn about.
- **Sample**: the *subset* we pulled from the population.
- **Parameter**: the *true value* in the population (μ, σ).
- **Statistic**: a value computed from the sample (x̄, s).
- **Sampling Bias**: when the sample *fails to represent* the population.

## Before / After

**Before**: *“Average website satisfaction is 4.5/5.”* — Only respondents were analyzed.

**After**: *“200 respondents / 10,000 visitors — 2% response rate, possibly skewed toward satisfied users → interpret cautiously.”*

## Hands-on: 5-step Sample Design

### Step 1 — Define the population

```text
Population: "active users on our website over the last 30 days"
```

### Step 2 — Sampling frame

```python
import pandas as pd
users = pd.read_csv("active_users.csv")  # population list
print(len(users))
```

### Step 3 — Random sampling

```python
sample = users.sample(n=500, random_state=42)
```

### Step 4 — Collect responses

```python
responses = collect_survey(sample.user_id)
print("response rate:", len(responses) / len(sample))
```

### Step 5 — Check for bias

```python
print("plan dist (sample):", sample.plan.value_counts(normalize=True))
print("plan dist (pop):",    users.plan.value_counts(normalize=True))
```

## What to Notice in This Code

- *Defining the population* is the *start* of the sample.
- *random_state* guarantees *reproducibility*.
- *Response rate* and *segment distribution* expose *bias*.

## Five Common Mistakes

1. **Treating a *convenience sample* as if it were representative.**
2. **Analyzing *only respondents*.** Non-respondents differ.
3. **Blindly trusting *N=30*.**
4. **Skipping the *population definition*.**
5. **Slicing by *time order* instead of *randomly*.**

## How This Shows Up in Production

A/B testing, surveys, quality inspections, pre-launch beta tests — in all of these, *sample design* determines *result quality*. Techniques like *stratified sampling* and *cluster sampling* show up often.

## How a Senior Engineer Thinks

- Write the *population* in a sentence.
- *Pin* the *random_state*.
- *Report* response rate and segments.
- *Name biases openly* instead of hiding them.
- Set sample size *statistically*, not by feel.

## Checklist

- [ ] I write the *population* in one line.
- [ ] I do *random sampling*.
- [ ] I report the *response rate*.
- [ ] I compare *segment distributions*.

## Practice Problems

1. Define the *population, sample, and statistics* for *members of your club*.
2. Explain the difference between a *convenience sample* and a *random sample* in one sentence.
3. Write how you would *interpret a survey* with a *30% response rate*.

## Wrap-up and Next Steps

Sample design is the *foundation of statistics*. The next episode enters the world of *estimation*, where we use samples to *guess at population parameters*.

## Answering the Opening Questions

- **How do population and sample differ?**
  - The article treats Sample and Population as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **What makes a sample representative enough to trust?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Why does random sampling appear so often in statistics?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Statistics 101 (1/10): What Is Statistics?](./01-what-is-statistics.md)
- [Statistics 101 (2/10): Mean, Median, and Variance](./02-mean-median-variance.md)
- [Statistics 101 (3/10): Distributions](./03-distributions.md)
- **Sample and Population (current)**
- Estimation (upcoming)
- Confidence Interval (upcoming)
- Hypothesis Testing (upcoming)
- Correlation and Regression (upcoming)
- Understanding p-value (upcoming)
- Statistical Thinking (upcoming)

<!-- toc:end -->

## References

- [Pew Research — Sampling Methodology](https://www.pewresearch.org/our-methods/u-s-surveys/)
- [scikit-learn — Stratified Sampling](https://scikit-learn.org/stable/modules/cross_validation.html)
- [OpenIntro — Sampling Principles](https://www.openintro.org/book/os/)
- [Wikipedia — Selection Bias](https://en.wikipedia.org/wiki/Selection_bias)

Tags: Statistics, Sampling, Population, Bias, Beginner
