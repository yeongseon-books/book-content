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
- **Prediction drift**: a change in the output distribution P(ŷ), which may signal either input or model issues.
- **PSI**: Population Stability Index. Below 0.1 is considered safe.
- **KS**: Kolmogorov–Smirnov test for distribution distance.
- **MMD**: Maximum Mean Discrepancy — a kernel-based test for multivariate drift.
- **Baseline**: the reference distribution, usually training data.

## Drift Type Comparison and Response Priority

Drift looks like a single phenomenon, but in practice the response differs by type.

| Type | What Changed | Fast Detection Signal | First Response |
|---|---|---|---|
| Data drift | Input distribution X | PSI, KS, missing-value rate | Check collection/preprocessing path |
| Concept drift | Relationship between X and Y | Delayed-label performance drop | Generate retraining candidate |
| Prediction drift | Output distribution P(ŷ) | Class ratio shift, score distribution | Check serving version and input distribution together |

In production, treating data drift as the early warning and concept drift as the impact-confirmation signal works well together.

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

This example assumes the baseline and current distributions are slightly misaligned. In a real service, training data and recent production inputs fill these roles.

### Step 2 — Bin edges

```python
def bin_edges(x, n=10):
    return np.quantile(x, np.linspace(0, 1, n + 1))
```

PSI compares distributions by splitting them into bins, so edge selection matters. Using baseline quantiles locks the comparison frame so that the current distribution is always measured against a fixed reference.

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

The `+ 1e-6` correction deserves attention. In real production data, certain bin counts can hit zero, and dividing by zero breaks the entire calculation.

### Step 4 — KS test

```python
from scipy.stats import ks_2samp
stat, p = ks_2samp(base, live)
print(round(stat, 3), round(p, 4))
```

The KS test reduces the gap between two distributions to a single statistic. Using PSI and KS together lets you read both bin-level proportional changes and the overall distributional distance.

### Step 5 — Threshold policy

```python
def status(p_value, psi_value):
    if psi_value > 0.2 or p_value < 0.01:
        return "drift"
    if psi_value > 0.1:
        return "watch"
    return "ok"
```

A raw statistic alone does not end the operational decision. Ultimately the team must agree on when to investigate and when to queue retraining.

## KS Test Production Code

The basic `ks_2samp` call above is fine for exploration, but production needs a structured return value:

```python
import numpy as np
from scipy.stats import ks_2samp

def ks_drift(reference: np.ndarray, current: np.ndarray, alpha: float = 0.01) -> dict:
    stat, p = ks_2samp(reference, current)
    return {
        "ks_stat": float(stat),
        "p_value": float(p),
        "drift": bool(p < alpha),
    }

ref = np.random.normal(loc=0.0, scale=1.0, size=3000)
cur = np.random.normal(loc=0.25, scale=1.0, size=3000)
print(ks_drift(ref, cur))
```

KS works well for continuous features. For categorical features, consider chi-squared tests or Jensen-Shannon divergence instead.

## Per-Feature Drift Report

```python
import pandas as pd

def drift_report(df_ref: pd.DataFrame, df_cur: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    rows = []
    for c in cols:
        out = ks_drift(df_ref[c].to_numpy(), df_cur[c].to_numpy())
        rows.append({"feature": c, **out})
    return pd.DataFrame(rows).sort_values("p_value")
```

A per-feature report lets you quickly narrow down which input path shifted first.

## Drift Response Runbook

1. When a drift alert fires, compare the baseline and current bin distributions first.
2. Check data-path issues: collection gaps, schema changes, missing-value spikes.
3. Cross-reference model prediction distribution and business metrics.
4. If impact is significant, trigger a challenger retraining pipeline.
5. Document comparison results between the challenger and current champion before promotion.

Drift detection creates value only when it connects to an operational flow — not when it stays as a standalone statistic.

## KS Batch Job

In production, a batch-job form is more practical than a one-off function call. This example reads reference and current windows, then emits a single JSON line per feature for log collectors:

```python
from __future__ import annotations

import json
import numpy as np
from scipy.stats import ks_2samp

def evaluate_ks(reference: np.ndarray, current: np.ndarray, alpha: float = 0.01) -> dict:
    stat, p_value = ks_2samp(reference, current)
    return {
        "ks_stat": float(stat),
        "p_value": float(p_value),
        "alpha": alpha,
        "drift": bool(p_value < alpha),
    }

def run_batch(reference: np.ndarray, current: np.ndarray, feature_name: str) -> None:
    result = evaluate_ks(reference, current)
    payload = {
        "feature": feature_name,
        "sample_ref": int(reference.size),
        "sample_cur": int(current.size),
        **result,
    }
    print(json.dumps(payload, ensure_ascii=False))

if __name__ == "__main__":
    ref = np.random.normal(0.0, 1.0, 5000)
    cur = np.random.normal(0.35, 1.0, 5000)
    run_batch(ref, cur, "risk_score")
```

Including `sample_ref` and `sample_cur` in the output helps quickly distinguish false positives caused by insufficient sample size.

## Drift Type Response Strategy

| Drift Signal | First Check | Second Action | Retrain? |
|---|---|---|---|
| PSI spike + KS significant | Collection path / schema change | Rollback preprocessing or patch missing values | Conditional |
| Prediction score distribution shift | Input distribution + serving version | Fix serving config / feature-loading delay | Conditional |
| Delayed-label performance drop | Label quality / label delay | Train challenger + offline re-evaluation | High priority |
| Single segment degradation | Per-segment sample count | Redesign segment-specific thresholds | Selective |

Operations teams should standardize "what to do first after an alert" rather than debating the statistic itself. Separating first-check from second-action (as above) improves both response speed and consistency when the same alert recurs.

## Multivariate Drift Detection

Univariate tests (KS, PSI) compare one feature at a time, so they miss cases where inter-feature correlations change. Multivariate drift detection captures distributional shifts across the entire feature space.

```python
from alibi_detect.cd import MMDDrift
import numpy as np

# Reference data: feature distribution at training time
reference_data = np.load("reference_features.npy")  # shape: (N, D)

# Initialize MMD-based drift detector
drift_detector = MMDDrift(
    reference_data,
    backend="pytorch",
    p_val=0.05,
    n_permutations=100,
)

def check_multivariate_drift(new_batch: np.ndarray) -> dict:
    """Test a new batch for multivariate drift."""
    result = drift_detector.predict(new_batch)
    return {
        "is_drift": bool(result["data"]["is_drift"]),
        "p_value": float(result["data"]["p_val"]),
        "threshold": 0.05,
        "distance": float(result["data"]["distance"]),
    }
```

MMD (Maximum Mean Discrepancy) compares two distributions in kernel space. Unlike univariate tests, it also catches interaction changes — for example, a shift in the age-income correlation even when each feature individually looks stable.

## Automated Daily Drift Pipeline

Running drift detection manually invites gaps. Integrating it into a scheduled pipeline is the reliable approach:

```python
from datetime import datetime
import json

def daily_drift_report(
    reference_path: str,
    today_data_path: str,
    output_path: str,
):
    """Generate a daily drift report combining multivariate and univariate tests."""
    reference = np.load(reference_path)
    today = np.load(today_data_path)

    # Multivariate test
    multi_result = check_multivariate_drift(today)

    # Univariate test (per feature)
    from scipy.stats import ks_2samp

    univariate_results = []
    for col_idx in range(reference.shape[1]):
        stat, p_val = ks_2samp(reference[:, col_idx], today[:, col_idx])
        univariate_results.append({
            "feature_index": col_idx,
            "ks_statistic": float(stat),
            "p_value": float(p_val),
            "is_drift": p_val < 0.05,
        })

    report = {
        "date": datetime.now().isoformat(),
        "multivariate": multi_result,
        "univariate": univariate_results,
        "drifted_features": [
            r["feature_index"]
            for r in univariate_results
            if r["is_drift"]
        ],
        "recommendation": (
            "retrain" if multi_result["is_drift"] else "monitor"
        ),
    }

    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    return report
```

When `recommendation` is `"retrain"`, this report can trigger a retraining pipeline automatically. The next post (Retraining) covers that connection in detail.

## Retraining Trigger

Detecting drift does not mean unconditional retraining. You must confirm that the drift actually degrades performance:

```python
def should_retrain(psi: float, recent_accuracy: float, baseline_accuracy: float):
    if psi > 0.2 and recent_accuracy < baseline_accuracy - 0.05:
        return True
    if psi > 0.3:
        return True
    return False
```

This function checks two conditions. First, if PSI exceeds 0.2 and accuracy has dropped by more than 5 percentage points, retrain. Second, if PSI exceeds 0.3, retrain regardless of accuracy. The exact thresholds should be tuned per team, but the key principle is looking at drift and performance together.

## Drift Detection Tests

Drift detection code needs tests too. You need to verify that PSI calculations are correct and that threshold logic behaves as expected:

```python
import pytest
import numpy as np

def test_psi_same_distribution():
    base = np.random.normal(0, 1, 1000)
    live = np.random.normal(0, 1, 1000)
    assert psi(base, live) < 0.1

def test_psi_shifted_distribution():
    base = np.random.normal(0, 1, 1000)
    live = np.random.normal(1, 1, 1000)
    assert psi(base, live) > 0.2

def test_status_logic():
    assert status(0.001, 0.05) == "ok"
    assert status(0.001, 0.15) == "watch"
    assert status(0.001, 0.25) == "drift"
```

These tests confirm that PSI is low for identical distributions and high for shifted ones. They also verify that the status function applies thresholds correctly. Since drift detection is production code, test coverage matters.

## Optimizing Drift Detection at Scale

When data volume grows, computing PSI across all features becomes expensive. Prioritize:

1. **Top features**: Monitor the 5–10 features with the highest model-performance impact first.
2. **Sampling**: Compute PSI on a representative sample rather than the full dataset.
3. **Cadence adjustment**: Check daily or weekly instead of hourly.
4. **Incremental computation**: Instead of re-reading all data, compute PSI on new arrivals and merge with prior results.

Efficiency matters at scale, but for features where sensitivity outweighs efficiency, skip sampling and check the full population.

## What to Notice in This Code

- The `+ 1e-6` term prevents division by zero.
- KS reduces a distribution gap to a single number.
- The threshold is a team agreement, not a universal constant.
- The baseline and threshold together form the team's operating contract.

Good drift detection depends more on operational wiring than on statistical technique. If an alert fires but nobody knows the next step, the numbers just accumulate.

## Five Common Mistakes

1. **Setting the baseline to "the last few days" — drift becomes invisible.**
   The distribution drifts together, so changes cancel out.
2. **Trying to detect concept drift without labels.**
   You end up conflating input changes with performance degradation.
3. **Looking only at single features and ignoring multivariate shift.**
   Real problems can emerge from feature combinations.
4. **Applying KS to bounded categorical features as-is.**
   Feature characteristics demand matching metric choices.
5. **Alerting only — no automated retraining trigger.**
   The warning exists but the operational loop never closes.

## How This Shows Up in Production

A risk-scoring model computes PSI nightly. If it crosses 0.2, the model is automatically queued for retraining and a ticket is filed. The key principle: never leave drift detection to human eyes alone.

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
- [ ] Per-feature drift report exists for triage.
- [ ] Multivariate drift detection covers feature interactions.

## Practice Problems

1. Write a PSI function for *categorical* features.
2. How would you measure concept drift when labels arrive late?
3. PSI is 0.18 — alert or ignore? Justify your rule.

## Wrap-up and Next Steps

Drift detection is the mechanism that surfaces a model's quiet aging before it becomes a visible business problem. Separating input distribution change from actual performance degradation makes the response more precise.

The single takeaway: **data drift is the signal that arrives first; model drift is the consequence that signal produces.** The next post covers *retraining automation* — what to do once the signal fires.

## Answering the Opening Questions

- **How do data drift and model drift differ?**
  - Data drift is when input X's distribution changes between `base` and `live`; model drift is the resulting degradation in actual performance and prediction distribution. The article treated data drift as an early warning and model drift as the impact-confirmation signal — separately.
- **Why does choosing the wrong baseline make drift invisible?**
  - PSI and KS ultimately depend on what you compare current distributions against. If the baseline is recent days that drift together, changes cancel out. That's why the article insisted on fixing the training-time distribution or a validated reference period as the anchor.
- **When are PSI and KS tests useful?**
  - PSI is useful for seeing how much bin-level proportions have shifted; KS is strong for summarizing two continuous-feature distributions' difference as `stat` and `p_value`. Using both together (as in the article) makes it easy to connect them to `status()` or retraining conditions — turning simple statistics into operational alerts.
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
- [alibi-detect — MMDDrift](https://docs.seldon.io/projects/alibi-detect/en/stable/cd/methods/mmddrift.html)

Tags: MLOps, Drift, Monitoring, DataScience, Statistics
