---
series: statistics-101
episode: 9
title: Understanding p-value
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
  - PValue
  - Inference
  - Misconceptions
  - Beginner
seo_description: A clear definition of the p-value, the five most common misreadings, and practical rules to avoid p-hacking when reporting test results
last_reviewed: '2026-05-04'
---

# Understanding p-value

> Statistics 101 series (9/10)

<!-- a-grade-intro:begin -->

**Core question**: What does *p < 0.05* really mean? *Why* is it *misread so often*?

> *A p-value is not the probability that a hypothesis is true. It is only how surprising the data is.*

<!-- a-grade-intro:end -->

## What You Will Learn

- The *precise definition* of a p-value
- *Five common misreadings*
- *p-hacking* and *pre-registration*
- A 5-step p-value exercise
- The core of the *ASA 2016 statement*

## Why It Matters

Most papers and reports collapse a *conclusion* into one line: *p < 0.05*. Yet *most readers misread that line*. *A misread p-value leads to wrong decisions*.

> *A p-value is not an answer; it is the *start of a question*.*

## Concept at a Glance

```mermaid
flowchart LR
    H0["H0 (null)"] --> Sample["Observed sample"]
    Sample --> Stat["Test statistic"]
    Stat --> P["p = P(stat >= obs | H0)"]
    P --> Decide["Compare with alpha"]
```

## Key Terms

- **p-value**: under the *assumption that H0 is true*, the probability of seeing a *result at least as extreme* as the observed one.
- **Significance level α**: a pre-chosen *rejection threshold* (often 0.05).
- **Type I error**: rejecting *H0 when it is true* (probability = α).
- **p-hacking**: rerunning analyses *until the desired p* appears.
- **Pre-registration**: publishing the hypothesis and procedure *before* analysis.

## Before / After

**Before**: *“p = 0.03, so H0 is true with *3%* probability.”* — *Wrong reading*.

**After**: *“If H0 is true, the chance of seeing data *as extreme as ours* is 3%.”*

## Hands-on: 5-step p-value

### Step 1 — Set the hypothesis

```python
# H0: mean = 100, H1: mean != 100
mu0 = 100
```

### Step 2 — Data

```python
import numpy as np
rng = np.random.default_rng(0)
sample = rng.normal(102, 15, size=40)
```

### Step 3 — Run the test

```python
from scipy import stats
t, p = stats.ttest_1samp(sample, mu0)
print("t:", t, "p:", p)
```

### Step 4 — Effect size

```python
import numpy as np
effect = (sample.mean() - mu0) / sample.std(ddof=1)
print("Cohen's d:", effect)
```

### Step 5 — Simulate p-hacking

```python
import numpy as np
from scipy import stats
hits = 0
for _ in range(20):
    x = np.random.default_rng().normal(100, 15, size=40)
    if stats.ttest_1samp(x, 100).pvalue < 0.05:
        hits += 1
print("False alarms in 20 looks:", hits)
```

## What to Notice in This Code

- A *p-value is a function of the data*; it is *not* the probability of a *hypothesis*.
- *p* shrinks with sample size *even when the effect is small*.
- Re-analyzing the *same data many times* compounds *spurious significance*.

## Five Common Mistakes

1. ***p = P(H0 is true)*** *(wrong)*.
2. ***p = effect size*** *(wrong)*.
3. ***p > 0.05* means *no effect*** *(absence of evidence is not evidence of absence)*.
4. **Running *many tests* with *no correction*.**
5. **Reshaping a hypothesis *to fit the data after the fact*.**

## How This Shows Up in Production

A/B tests, clinical trials, quality control — production reports always pair *p-values* with *effect sizes* and *confidence intervals*. *Multiple-testing corrections* such as *Bonferroni* or *FDR* are standard.

## How a Senior Engineer Thinks

- *Always* reads *p* with the *effect size*.
- Knows *significant ≠ meaningful*.
- Uses *pre-registration* to block *p-hacking*.
- Knows the core of the *ASA statement*.
- Never decides on *p alone*.

## Checklist

- [ ] I can define a *p-value* precisely.
- [ ] I separate *significance level* from *Type I error*.
- [ ] I recognize *p-hacking*.
- [ ] I report *effect size* alongside *p*.

## Practice Problems

1. Explain the *practical difference* between *p = 0.04* and *p = 0.06*.
2. Compute the *false-positive* probability of testing the *same data 5 times*.
3. Describe what it *means* when the *effect size is tiny* but *p is small*.

## Wrap-up and Next Steps

A p-value is *not proof*; it is a *measure of surprise*. The next episode wraps everything together as a *statistical mindset*.

<!-- toc:begin -->
- [What Is Statistics?](./01-what-is-statistics.md)
- [Mean, Median, and Variance](./02-mean-median-variance.md)
- [Distributions](./03-distributions.md)
- [Sample and Population](./04-sample-and-population.md)
- [Estimation](./05-estimation.md)
- [Confidence Interval](./06-confidence-interval.md)
- [Hypothesis Testing](./07-hypothesis-testing.md)
- [Correlation and Regression](./08-correlation-and-regression.md)
- **Understanding p-value (current)**
- Statistical Thinking (upcoming)
<!-- toc:end -->

## References

- [ASA Statement on p-Values (2016)](https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf)
- [Nature — Scientists rise up against statistical significance](https://www.nature.com/articles/d41586-019-00857-9)
- [scipy.stats — ttest_1samp](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_1samp.html)
- [Wikipedia — Misuse of p-values](https://en.wikipedia.org/wiki/Misuse_of_p-values)
