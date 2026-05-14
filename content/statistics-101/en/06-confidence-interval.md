---
series: statistics-101
episode: 6
title: Confidence Interval
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Statistics
  - ConfidenceInterval
  - Inference
  - Uncertainty
  - Beginner
seo_description: What a 95 percent confidence interval really means, common misconceptions to avoid, and a step-by-step procedure to build one from a sample
last_reviewed: '2026-05-04'
---

# Confidence Interval

This is post 6 in the Statistics 101 series.

> Statistics 101 series (6/10)

<!-- a-grade-intro:begin -->

**Core question**: What does a *95% confidence interval* actually mean? Does it mean *the population mean has a 95% chance* of being inside?

> *Confidence is in the procedure, not in the value.*

<!-- a-grade-intro:end -->

## What You Will Learn

- The *true meaning* of a *95% CI*
- The *t-distribution* and *small samples*
- *Asymmetric CIs* via the *bootstrap*
- A 5-step CI exercise
- Five common mistakes

## Why It Matters

Confidence intervals are the *most common tool* for showing uncertainty — and the *most commonly misread*. Knowing the *exact meaning* is what produces *exact decisions*.

> *A 95% CI is the *hit rate of the method*, not the probability of *this* particular interval.*

## Concept at a Glance

```mermaid
flowchart LR
    Sample["Sample"] --> SE["Standard Error"]
    SE --> Critical["t / z critical value"]
    Critical --> CI["Confidence Interval"]
```

## Key Terms

- **Confidence Interval**: an interval such that, if the *procedure* were repeated infinitely, *95% of intervals* would contain the parameter.
- **Confidence Level**: 95%, 99%, etc. — the *hit rate*.
- **Margin of Error**: the *±* part.
- **t-distribution**: a *slightly heavier-tailed* alternative to the normal, used for small samples.
- **Bootstrap**: a *non-parametric* method that *re-samples* data to build *asymmetric CIs*.

## Before / After

**Before**: *“There is a 95% probability the mean is between 95 and 105.”* — Common misreading.

**After**: *“Repeat the procedure 100 times and about 95 of those intervals will contain the true mean.”*

## Hands-on: 5-step CI

### Step 1 — Sample

```python
import numpy as np
sample = np.random.normal(100, 20, size=64)
```

### Step 2 — t critical value

```python
from scipy import stats
df = len(sample) - 1
t_crit = stats.t.ppf(0.975, df)
print("t*:", t_crit)
```

### Step 3 — SE and margin of error

```python
se = sample.std(ddof=1) / np.sqrt(len(sample))
moe = t_crit * se
```

### Step 4 — The interval

```python
mean = sample.mean()
print(f"95% CI: [{mean - moe:.2f}, {mean + moe:.2f}]")
```

### Step 5 — Bootstrap

```python
from numpy.random import default_rng
rng = default_rng(0)
boots = [rng.choice(sample, len(sample), replace=True).mean() for _ in range(2000)]
print("Bootstrap CI:", np.percentile(boots, [2.5, 97.5]))
```

## What to Notice in This Code

- For *small samples*, use the *t-distribution*.
- *Bootstrap* works *without distributional assumptions*.
- When the two intervals *agree*, the assumptions were *appropriate*.

## Five Common Mistakes

1. **Believing *this particular interval* has *95% probability*.**
2. **Using *z = 1.96* on *N=10*. The *t* is required.**
3. **Confusing *confidence level* with *significance level*.**
4. **Using a normal CI on a *skewed* distribution without bootstrap.**
5. **Concluding *no effect* whenever the CI *contains 0*.**

## How This Shows Up in Production

A/B test results, regression coefficients, effect sizes — every *inference report* lists a *CI* alongside the estimate. *Dashboard error bars* are visualizations of confidence intervals.

## How a Senior Engineer Thinks

- Knows the *exact meaning* — the *hit rate of the method*.
- Uses the *t-distribution* and *bootstrap* on small samples.
- Reads *CI width* alongside *effect size*.
- Picks *confidence level* by context (medicine = 99%, marketing = 90%).
- Knows that *containing 0 ≠ no effect*.

## Checklist

- [ ] I know the *exact meaning* of a CI.
- [ ] I can use the *t-distribution*.
- [ ] I know the *bootstrap*.
- [ ] I pick the *confidence level* by context.

## Practice Problems

1. Simulate the *width difference* between a *95% CI* and a *99% CI*.
2. Describe a situation where the *bootstrap CI* beats the *normal CI*.
3. Explain why *“the mean is in X with 95% probability”* is *wrong*.

## Wrap-up and Next Steps

Confidence intervals are the tool for *visualizing uncertainty*. The next episode covers *hypothesis testing* — asking *whether a difference exists*.

<!-- toc:begin -->
- [What Is Statistics?](./01-what-is-statistics.md)
- [Mean, Median, and Variance](./02-mean-median-variance.md)
- [Distributions](./03-distributions.md)
- [Sample and Population](./04-sample-and-population.md)
- [Estimation](./05-estimation.md)
- **Confidence Interval (current)**
- Hypothesis Testing (upcoming)
- Correlation and Regression (upcoming)
- Understanding p-value (upcoming)
- Statistical Thinking (upcoming)
<!-- toc:end -->

## References

- [scipy.stats — t and bootstrap](https://docs.scipy.org/doc/scipy/reference/stats.html)
- [BMJ — Common Misconceptions of Confidence Intervals](https://www.bmj.com/content/322/7280/226)
- [Khan Academy — Confidence Intervals](https://www.khanacademy.org/math/statistics-probability/confidence-intervals-one-sample)
- [Wikipedia — Bootstrap](https://en.wikipedia.org/wiki/Bootstrapping_%28statistics%29)

Tags: Statistics, ConfidenceInterval, Inference, Uncertainty, Beginner
