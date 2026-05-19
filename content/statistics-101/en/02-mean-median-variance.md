---
series: statistics-101
episode: 2
title: Mean, Median, and Variance
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
  - DescriptiveStats
  - Mean
  - Variance
  - Beginner
seo_description: A practical comparison of mean, median, and variance, with rules for picking the right summary statistic when distributions are skewed
last_reviewed: '2026-05-04'
---

# Mean, Median, and Variance

The moment you compress a dataset into one or two numbers, you are already shaping the story the report will tell. Whether you write down only the mean, add the median, or explain spread with variance and standard deviation changes the reader's interpretation.

That choice becomes especially important when the data has outliers or a long tail. In those cases, the mean can move far away from what most observations actually look like.

This is post 2 in the Statistics 101 series. Here we will compare mean, median, and variance, and clarify why the right summary statistic depends on the shape of the data.

## Questions this post answers

- When should we use the mean, and when should we use the median?
- What do variance and standard deviation tell us that the mean cannot?
- What happens to summary statistics when one extreme outlier appears?
- When is IQR the safer measure of spread?

> A good summary statistic is not a pretty compression of the data. It is the number that fits the question.

## Why It Matters

Data has *thousands of rows*, but humans decide with *one or two numbers*. *Which number you pick* determines the *quality of the decision*.

> *One wrong mean writes one wrong decision.*

## Concept at a Glance

![Concept at a Glance](https://yeongseon-books.github.io/book-public-assets/assets/statistics-101/02/02-01-concept-at-a-glance.en.png)

*A useful summary needs both a center metric and a spread metric, not just one representative number.*
## Key Terms

- **Mean**: sum / count. *Sensitive to outliers*.
- **Median**: middle value after sorting. *Robust to outliers*.
- **Mode**: the *most frequent* value.
- **Variance**: average of *squared distances* from the mean.
- **Standard Deviation**: square root of variance. Same units as the data.
- **IQR (Interquartile Range)**: *Q3 − Q1*. The width of the middle 50%.

## Before / After

**Before**: *“Our average user spend is $50.”* — But what if one user spent $5,000?

**After**: *“Median $12, mean $50 (heavily skewed) — spend follows a long-tail distribution.”*

## Hands-on: 5-step Summary Statistics

### Step 1 — Prepare data

```python
import numpy as np
x = np.array([10, 12, 11, 13, 12, 14, 11, 12, 5_000_000])
```

### Step 2 — Mean and median

```python
print("mean:", np.mean(x))
print("median:", np.median(x))
```

### Step 3 — Variance and standard deviation

```python
print("var:", np.var(x))
print("std:", np.std(x))
```

### Step 4 — IQR

```python
q1, q3 = np.percentile(x, [25, 75])
print("IQR:", q3 - q1)
```

### Step 5 — Summary sentence

```text
Median 12, IQR 1.5 — most users sit near 12.
Mean 555,557 (skewed by one outlier).
Decision: report the median, not the mean.
```

## What to Notice in This Code

- With outliers present, *mean ≠ median*.
- Variance is in *squared units*; standard deviation is in *original units*.
- IQR is a *spread* measure that is *robust to outliers*.

## Five Common Mistakes

1. **Deciding from the *mean alone*.** Missing the *shape* of the distribution.
2. **Confusing *standard deviation* with *variance*.** Different units.
3. **Reporting the *mean* on a *skewed* distribution.**
4. **Trusting the *variance* of *N=10*.** The sample is too small.
5. **Reporting *unitless numbers*.** Always include dollars, %, seconds.

## How This Shows Up in Production

Revenue, response time, ad cost — all of these tend to be *long-tail*, so *median / p95 / p99* are reported more often than *mean*. Dashboards usually show *three or four statistics* together.

## How a Senior Engineer Thinks

- *Plot the distribution* first.
- Look at *median / p95* alongside the *mean*.
- *Investigate the source* of outliers.
- *Always* write the units.
- Pick the *summary statistic that matches the question*.

## Checklist

- [ ] I know the difference between *mean* and *median*.
- [ ] I know *variance / standard deviation / IQR*.
- [ ] I use the *median* on *skewed* distributions.
- [ ] I include units in my report.

## Practice Problems

1. Compute the mean and median of your *daily study time over the last 30 days*.
2. Explain in one sentence why the *mean is dangerous* on a *long-tail* distribution.
3. Compare *IQR* and *standard deviation* — how are they different?

## Wrap-up and Next Steps

Summary statistics is a tool for *briefly conveying the shape* of data. The next episode goes one level deeper into the *shape itself* — *distributions*.

<!-- toc:begin -->
- [What Is Statistics?](./01-what-is-statistics.md)
- **Mean, Median, and Variance (current)**
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

- [NIST/SEMATECH e-Handbook of Statistical Methods](https://www.itl.nist.gov/div898/handbook/)
- [pandas — describe()](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.describe.html)
- [Wikipedia — Robust Statistics](https://en.wikipedia.org/wiki/Robust_statistics)
- [Khan Academy — Summary Statistics](https://www.khanacademy.org/math/statistics-probability/summarizing-quantitative-data)

Tags: Statistics, DescriptiveStats, Mean, Variance, Beginner
