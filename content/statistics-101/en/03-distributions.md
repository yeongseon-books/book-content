---
series: statistics-101
episode: 3
title: "Statistics 101 (3/10): Distributions"
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
  - Distribution
  - Normal
  - Skew
  - Beginner
seo_description: A walkthrough of normal, uniform, exponential, and power-law shapes plus a 5-step procedure for reading the distribution behind any dataset
last_reviewed: '2026-05-04'
---

# Statistics 101 (3/10): Distributions

Two datasets can share the same mean and still behave in completely different ways. One may stay tightly clustered around the center, while the other may have a long tail or a few values far away from the rest. Matching one summary number does not mean the data has the same character.

In statistics, the distribution is the shape of the data. If you misread that shape, later decisions about averages, confidence intervals, tests, or SLAs start to drift.

This is the 3rd post in the Statistics 101 series. Here we will build intuition for reading data shape and explain why assuming normality too quickly causes real problems.


![statistics 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/statistics-101/03/03-01-concept-at-a-glance.en.png)
*statistics 101 chapter 3 flow overview*
> Understanding the *shape* of your data unlocks why the *same mean* can hide *different realities*.

## Questions to Keep in Mind

- Why does the shape of a distribution matter?
- How do normal, uniform, exponential, and power-law distributions differ?
- What do skewness and kurtosis tell us numerically?

## Why It Matters

*Most* summary statistics and tests stand on *distribution assumptions*. If the *shape is assumed wrong*, the *conclusion as a whole* shakes.

> *Pick the tool by the shape.*

## Concept at a Glance
Visualizing distributions reveals patterns that summaries alone cannot capture. A distribution tells you not just where data *lives*, but how *wide* the variation is and whether there are *outliers* or *gaps*.
## Key Terms

- **Normal**: a *symmetric bell* shape; common in nature and measurement noise.
- **Uniform**: every value has the *same frequency*.
- **Exponential**: time between events, waiting times.
- **Power-law**: *long-tail*. Revenue, page views.
- **Skewness**: degree of *asymmetry*.
- **Kurtosis**: thickness of the *tails*.

## Before / After

**Before**: *“Average response time is 200 ms.”* — assumed bell-shaped, SLA built on the mean.

**After**: *“p50=120 ms, p95=900 ms, long-tail — the SLA must be defined on p95 to be safe.”*

## Hands-on: 5-step Distribution Diagnosis

### Step 1 — Histogram

```python
import matplotlib.pyplot as plt
plt.hist(latency, bins=50); plt.show()
```

### Step 2 — Summary statistics

```python
import numpy as np
print(np.mean(latency), np.median(latency), np.std(latency))
```

### Step 3 — Quantiles

```python
for q in [50, 90, 95, 99]:
    print(f"p{q}:", np.percentile(latency, q))
```

### Step 4 — Skewness and kurtosis

```python
from scipy.stats import skew, kurtosis
print("skew:", skew(latency), "kurt:", kurtosis(latency))
```

### Step 5 — Decide

```text
skew=+2.3, kurt=+8 → long-tail. SLA = p95 = 900ms.
```

## What to Notice in This Code

- The *histogram* is the *start of every diagnosis*.
- *Quantiles* catch the *long-tail*.
- *Skewness and kurtosis* express the shape *as numbers*.

## Five Common Mistakes

1. **Applying tests after *assuming normality*.**
2. **Letting *outliers* blend into the *distribution*.**
3. **Looking at long-tail without a *log scale*.**
4. **Replacing *p99* with the *mean*.**
5. **Reading statistics *without visualization*.**

## How This Shows Up in Production

Response-time SLAs, revenue, click-through, defect frequency — most operational metrics are long-tail. Tools like Datadog, Grafana, Sentry default to showing p50 / p95 / p99.

### Distribution Diagnosis Sequence

1. Histogram → rough shape (symmetric? skewed? bimodal?)
2. Box plot → outliers and quartiles
3. Log-scale histogram → tail structure
4. Q-Q plot → normality approximation check
5. Shapiro / D'Agostino test → numeric confirmation

```python
import numpy as np
from scipy import stats

rng = np.random.default_rng(0)
x = np.r_[rng.lognormal(4.2, 0.6, 1800), rng.lognormal(6.0, 0.4, 200)]

# Log transform improves normality
k2, p = stats.normaltest(np.log(x))
print(f'normality test p-value (log-transformed): {p:.4f}')
print(f'skewness (raw): {stats.skew(x):.2f}')
print(f'skewness (log): {stats.skew(np.log(x)):.2f}')
```

If log-transform makes the data approximately normal, mean-based estimation and linear models become more stable. Always show before/after side by side for team consensus.

### When to Apply Which Distribution Model

| Data type | Typical distribution | Key indicator |
| --- | --- | --- |
| Response time | Log-normal / Pareto | Long right tail, floor at 0 |
| Count data (bugs, clicks) | Poisson / Negative binomial | Integer, floor at 0 |
| Time between events | Exponential | Memoryless, single rate |
| Proportions (CTR) | Beta / Binomial | Bounded [0, 1] |
| Symmetric measurement error | Normal | Bell-shaped, thin tails |

## How a Senior Engineer Thinks

- *Plot the distribution* first — never assume normality casually.
- For long-tails, read *quantiles* (p50, p95, p99) rather than trusting the mean.
- Use *log scale* aggressively to expose tail structure.
- Make *shape vocabulary* (skewed, bimodal, heavy-tailed) part of team discussions.
- Choose SLA thresholds on percentiles, not averages — p95 SLA protects real users.

## Checklist

- [ ] I draw a *histogram*.
- [ ] I read *p50 / p95 / p99*.
- [ ] I know *skewness and kurtosis*.
- [ ] I use a *p95 SLA* on long-tail data.

## Practice Problems

1. Plot a histogram of *response times* for a service you know.
2. Explain in one sentence the *shape difference* between *normal* and *exponential*.
3. Write down why *p99* is more useful than the *mean* on a long-tail.

## Wrap-up and Next Steps

A distribution is the *personality of the data*. The next episode opens up *uncertainty* through *sample and population*.

## Answering the Opening Questions

- **Why does the shape of a data distribution matter?**
  Histograms, boxplots, and QQ plots reveal the data's shape from multiple angles—without knowing the shape, you can't choose appropriate summary statistics or tests.
- **How do normal, uniform, exponential, and power-law distributions differ?**
  Knowing the distribution explains why different behaviors emerge from the same mean—exponential has rare extreme events while normal clusters around center.
- **What do skewness and kurtosis tell us numerically?**
  Unusual distributions can signal data collection errors, making them automatic alert criteria in operations. Skewness measures asymmetry; kurtosis measures tail heaviness.

<!-- toc:begin -->
## In this series

- [Statistics 101 (1/10): What Is Statistics?](./01-what-is-statistics.md)
- [Statistics 101 (2/10): Mean, Median, and Variance](./02-mean-median-variance.md)
- **Distributions (current)**
- Sample and Population (upcoming)
- Estimation (upcoming)
- Confidence Interval (upcoming)
- Hypothesis Testing (upcoming)
- Correlation and Regression (upcoming)
- Understanding p-value (upcoming)
- Statistical Thinking (upcoming)

<!-- toc:end -->

## References

- [SciPy — Statistical Distributions](https://docs.scipy.org/doc/scipy/reference/stats.html)
- [Khan Academy — Distributions](https://www.khanacademy.org/math/statistics-probability/random-variables-stats-library)
- [Wikipedia — Power Law](https://en.wikipedia.org/wiki/Power_law)
- [Brendan Gregg — Latency Distributions](https://www.brendangregg.com/blog/2014-06-23/latency-heat-maps.html)

Tags: Statistics, Distribution, Normal, Skew, Beginner
