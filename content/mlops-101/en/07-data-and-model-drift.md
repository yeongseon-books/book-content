---
series: mlops-101
episode: 7
title: "MLOps 101 (7/10): Data Drift and Model Drift"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - MLOps
  - Drift
  - Monitoring
  - DataScience
  - Statistics
seo_description: Separate input-distribution drift from model-quality drift with PSI, KS, and an explicit policy for investigation and retraining.
last_reviewed: '2026-05-15'
---

# MLOps 101 (7/10): Data Drift and Model Drift

When a live model stops feeling as reliable as it used to, the cause is rarely one thing. The input distribution may have changed, or the inputs may look similar while the relationship between input and label has shifted underneath the model.

Teams often notice the problem only after a business metric drops. In practice, the input distribution usually changes first, and only later do the performance and business losses become obvious.

This is the 7th post in the MLOps 101 series.

Here, we will separate data drift from model drift and connect statistical signals such as PSI and KS to concrete operating thresholds.


![mlops 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/mlops-101/07/07-01-see-the-flow-first.en.png)
*mlops 101 chapter 7 flow overview*
> Drift detection is not a single metric threshold. It is an early warning system that catches data and model changes before they cascade into visible business failure.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Data Drift and Model Drift?
- Which signal should the example or diagram make visible for Data Drift and Model Drift?
- What failure should be prevented first when Data Drift and Model Drift reaches a real system?

## Questions this article answers

- What is the difference between data drift and model drift in practice?
- Why does a weak baseline make drift hard to see?
- When are PSI and the KS test useful?
- Why should thresholds be treated as team policy rather than a magic formula?
- How do you connect drift detection to a retraining trigger?

> Mental model: data drift is a change in the input distribution. Model drift is the business or prediction impact that follows. The first is an early warning; the second is the confirmed consequence.

## Why It Matters

The world does not freeze after training. User behavior changes, seasonality changes, policy changes, and collection pipelines change. The moment a team assumes that the training distribution will stay stable forever, the model starts aging.

Without drift detection, the loss accumulates quietly. Only later do accuracy or business alarms make the problem visible. That is why drift detection has to exist as an early warning system.

## See the Flow First

This diagram captures the core workflow. A training-time distribution becomes the baseline, live inputs are compared against it with statistical tests, and the system emits a warning when the difference crosses the operating threshold.

The most important design choice is the baseline. If the baseline moves carelessly, drift itself becomes difficult to detect.

## Key Terms

- **Data drift**: a change in the distribution of input X.
- **Concept drift**: a change in the relationship between X and Y.
- **PSI**: Population Stability Index. Below 0.1 is considered safe.
- **KS**: Kolmogorov–Smirnov test for distribution distance.
- **Baseline**: the reference distribution, usually training data.

## Before/After

**Before**: you notice accuracy dropped *after* the loss is real.

**After**: PSI > 0.2 fires, and someone is investigating.

## Hands-on: Detect Data Drift with PSI

### Step 1 — Baseline and live data

```python
import numpy as np

base = np.random.normal(0, 1, 1000)
live = np.random.normal(0.5, 1, 1000)
```

### Step 2 — Bin edges

```python
def bin_edges(x, n=10):
    return np.quantile(x, np.linspace(0, 1, n + 1))
```

### Step 3 — PSI calculation

```python
def psi(base, live, n=10):
    edges = bin_edges(base, n)
    edges[0], edges[-1] = -np.inf, np.inf
    b, _ = np.histogram(base, edges)
    l, _ = np.histogram(live, edges)
    bp = b / b.sum() + 1e-6
    lp = l / l.sum() + 1e-6
    return float(np.sum((lp - bp) * np.log(lp / bp)))

print(round(psi(base, live), 3))
```

### Step 4 — KS test

```python
from scipy.stats import ks_2samp
stat, p = ks_2samp(base, live)
print(round(stat, 3), round(p, 4))
```

### Step 5 — Threshold policy

```python
def status(p_value, psi_value):
    if psi_value > 0.2 or p_value < 0.01:
        return "drift"
    if psi_value > 0.1:
        return "watch"
    return "ok"
```

## What to Notice in This Code

- The `+ 1e-6` term prevents division by zero.
- KS reduces a distribution gap to a single number.
- The threshold is a team agreement, not a universal constant.

## Five Common Mistakes

1. **Setting the baseline to "the last few days" — drift becomes invisible.**
2. **Trying to detect concept drift without labels.**
3. **Looking only at single features and ignoring multivariate shift.**
4. **Applying KS to bounded categorical features as-is.**
5. **Alerting only — no automated retraining trigger.**

## How This Shows Up in Production

A risk-scoring model computes PSI nightly. If it crosses 0.2, the model is automatically queued for retraining and a ticket is filed.

## How a Senior Engineer Thinks

- Data drift is the early warning.
- Model drift confirms the impact via metrics.
- Pin the baseline, refresh on a known cadence.
- Use PSI for categorical, KS for continuous features.
- Wire drift alerts to retraining workflows.

## Checklist

- [ ] A baseline distribution is defined.
- [ ] PSI/KS run on a regular schedule.
- [ ] Thresholds are documented.
- [ ] A retraining trigger is connected to the alert.

## Practice Problems

1. Write a PSI function for *categorical* features.
2. How would you measure concept drift when labels arrive late?
3. PSI is 0.18 — alert or ignore? Justify your rule.

## Wrap-up and Next Steps

Once you see drift, the next question is what to do. The next post covers *retraining automation*.

## Answering the Opening Questions

- **How do data drift and model drift differ?**
  - Data drift is when input X's distribution changes between `base` and `live`; model drift is the resulting degradation in actual performance and prediction distribution. The article treated data drift as an early warning and model drift as the impact-confirmation signal—separately.
- **Why does choosing the wrong baseline make drift invisible?**
  - PSI and KS ultimately depend on what you compare current distributions against. If the baseline is recent days that drift together, changes cancel out. That's why the article insisted on fixing the training-time distribution or a validated reference period as the anchor.
- **When are PSI and KS tests useful?**
  - PSI is useful for seeing how much bin-level proportions have shifted; KS is strong for summarizing two continuous-feature distributions' difference as `stat` and `p_value`. Using both together (as in the article) makes it easy to connect them to `status()` or retraining conditions—turning simple statistics into operational alerts.
<!-- toc:begin -->
## In this series

- [MLOps 101 (1/10): What Is MLOps?](./01-what-is-mlops.md)
- [MLOps 101 (2/10): Experiment Tracking](./02-experiment-tracking.md)
- [MLOps 101 (3/10): Data Versioning](./03-data-versioning.md)
- [MLOps 101 (4/10): Model Training Pipeline](./04-training-pipeline.md)
- [MLOps 101 (5/10): Model Deployment](./05-model-deployment.md)
- [MLOps 101 (6/10): Model Monitoring](./06-model-monitoring.md)
- **Data Drift and Model Drift (current)**
- Retraining (upcoming)
- Feature Store (upcoming)
- Building a Production ML System (upcoming)

<!-- toc:end -->

## References

- [Evidently AI — drift detection](https://docs.evidentlyai.com/)
- [SciPy — `ks_2samp`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ks_2samp.html)
- [Population Stability Index explained](https://www.listendata.com/2015/05/population-stability-index.html)
- [Google — Rules of ML](https://developers.google.com/machine-learning/guides/rules-of-ml)

Tags: MLOps, Drift, Monitoring, DataScience, Statistics
