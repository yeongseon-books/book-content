---
series: statistics-101
episode: 7
title: "Statistics 101 (7/10): Hypothesis Testing"
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
  - HypothesisTesting
  - Inference
  - ABTest
  - Beginner
seo_description: A walkthrough of null and alternative hypotheses, the t-test for group differences, plus type I and II errors and statistical power explained
last_reviewed: '2026-05-04'
---

# Statistics 101 (7/10): Hypothesis Testing

In statistical work, we constantly run into questions about differences. Did the new button lift conversion? Is the new treatment better than the old one? Is the model improvement real, or just noise in the sample?

Hypothesis testing exists because visible differences are not automatically meaningful differences. Samples always wobble. Without a formal procedure, it is easy to mistake random fluctuation for evidence.

This is the 7th post in the Statistics 101 series. Here we will define the null and alternative hypotheses, walk through the basic t-test flow, and explain why Type I error, Type II error, and statistical power matter in real decision-making.


![statistics 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/statistics-101/07/07-01-concept-at-a-glance.en.png)
*statistics 101 chapter 7 flow overview*
> Hypothesis testing answers: *Is this difference real or just noise?* It does not prove truth—it *measures evidence*.

## Questions to Keep in Mind

- How far can data support the claim that a difference exists?
- What do H0 and H1 actually mean?
- Why is p-value alone not enough?

## Why It Matters

*A/B testing, campaign effects, model comparisons* — *half* of all *decisions* run on hypothesis testing. Asking *correctly* avoids both *overclaiming* and *underclaiming*.

> *Asking the right question matters more than the answer.*

## Concept at a Glance
A hypothesis test starts with a claim (the *null hypothesis*), then checks whether your data is *consistent* with that claim. If your data is *too unusual* under that assumption, you reject the claim.
## Key Terms

- **H0 (Null Hypothesis)**: *no difference*.
- **H1 (Alternative)**: *there is a difference*.
- **Significance Level (α)**: tolerated *Type I error* probability (usually 0.05).
- **Power (1-β)**: probability of *catching a real effect*.
- **Type I Error**: *rejecting* H0 when it is *true*.
- **Type II Error**: *failing to reject* H0 when it is *false*.

## Before / After

**Before**: *“Group B's mean is higher. The treatment works!”* — Could be chance.

**After**: *“B mean +0.4pp (t=3.2, p=0.001) — significant at α=0.05, the treatment shows an effect.”*

## Hands-on: 5-step Hypothesis Test

### Step 1 — State the hypotheses

```text
H0: μ_A = μ_B
H1: μ_A ≠ μ_B
α = 0.05
```

### Step 2 — Sample

```python
import numpy as np
a = np.random.normal(3.2, 1, 1000)
b = np.random.normal(3.6, 1, 1000)
```

### Step 3 — Test statistic

```python
from scipy.stats import ttest_ind
stat, p = ttest_ind(a, b, equal_var=False)
print("t:", stat, "p:", p)
```

**Expected output:** a line like `t: ... p: ...`, which gives the first formal signal for whether the gap is plausibly just chance.

### Step 4 — Decide

```python
print("Reject H0" if p < 0.05 else "Fail to reject H0")
```

**Expected output:** in this example you will usually see `Reject H0`.

### Step 5 — Effect size

```python
diff = b.mean() - a.mean()
pooled = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
print("Cohen's d:", diff / pooled)
```

**Expected output:** a Cohen's d value often around `0.3` to `0.5` for this synthetic setup, giving you magnitude rather than only significance.

## What to Notice in This Code

- *Never decide from the p-value alone*.
- Read *Cohen's d* alongside it for *effect size*.
- *equal_var=False* selects *Welch's t-test*.

## Five Common Mistakes

1. **Concluding *“there is an effect”* from *p < 0.05* alone.**
2. **Running multiple tests *without correcting for multiplicity*.**
3. **Choosing sample size *without a power analysis*.**
4. **Picking *one-sided / two-sided* without context.**
5. **Changing H0 / H1 *after looking at results* (HARKing).**

## How This Shows Up in Production

A/B test result pages, *model performance comparisons*, *clinical trials* — the standard procedure for any *comparison decision*. *Bonferroni* and *FDR* corrections are common companions.

## How a Senior Engineer Thinks

- Writes the *hypothesis* down *before* seeing the data.
- Reads *p-value* and *effect size* together.
- Computes *power* up front.
- *Corrects* for multiple comparisons.
- Distinguishes *“fail to reject”* from *“H0 is true”*.

## Checklist

- [ ] I write *H0 / H1* clearly.
- [ ] I decide *α* and *power*.
- [ ] I report *effect size*.
- [ ] I know *multiple comparisons* corrections.

## Practice Problems

1. Simulate the *p-value* difference between *N=30* and *N=3000*.
2. Explain *Type I* vs *Type II* error with an example.
3. Write how you would *correct p < 0.05* across *three campaigns* tested at once.

## Wrap-up and Next Steps

Hypothesis testing is the *standard language of decisions*. The next episode looks at the *relationship between variables* — *correlation and regression*.

## Answering the Opening Questions

- **How far can data support the claim that "a difference exists"?**
  The null hypothesis states "no change." We look for evidence that the data is incompatible with this null—strong evidence lets us reject it, but absence of evidence isn't evidence of absence.
- **What do H0 (null hypothesis) and H1 (alternative hypothesis) mean?**
  H0 is the default assumption (no effect); H1 is what we suspect (there is an effect). A small p-value means the observation would be rare under H0, giving grounds to reject it.
- **Why is p-value alone insufficient for decisions?**
  In operations, you must also examine effect size and business impact alongside test results. A statistically significant but tiny effect may not justify action; a large effect with borderline p-value might.

<!-- toc:begin -->
## In this series

- [Statistics 101 (1/10): What Is Statistics?](./01-what-is-statistics.md)
- [Statistics 101 (2/10): Mean, Median, and Variance](./02-mean-median-variance.md)
- [Statistics 101 (3/10): Distributions](./03-distributions.md)
- [Statistics 101 (4/10): Sample and Population](./04-sample-and-population.md)
- [Statistics 101 (5/10): Estimation](./05-estimation.md)
- [Statistics 101 (6/10): Confidence Interval](./06-confidence-interval.md)
- **Hypothesis Testing (current)**
- Correlation and Regression (upcoming)
- Understanding p-value (upcoming)
- Statistical Thinking (upcoming)

<!-- toc:end -->

## References

- [scipy.stats — Hypothesis Tests](https://docs.scipy.org/doc/scipy/reference/stats.html)
- [Khan Academy — Hypothesis Testing](https://www.khanacademy.org/math/statistics-probability/significance-tests-one-sample)
- [Wikipedia — Multiple Comparisons Problem](https://en.wikipedia.org/wiki/Multiple_comparisons_problem)
- [Statistics Done Wrong (Reinhart)](https://www.statisticsdonewrong.com/)

Tags: Statistics, HypothesisTesting, Inference, ABTest, Beginner
