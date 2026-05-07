---
series: model-evaluation-101
episode: 2
title: Train, Validation, and Test
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - ModelEvaluation
  - TrainValTest
  - DataLeakage
  - CrossValidation
  - scikit-learn
seo_description: How to separate train, validation, and test sets, prevent leakage and group spillover, and split time-series data correctly with scikit-learn
last_reviewed: '2026-05-04'
---

# Train, Validation, and Test

> Model Evaluation 101 series (2/10)

<!-- a-grade-intro:begin -->

**Core question**: Why must validation and test be separate?

> *Train fits, validation tunes, and test is touched exactly once. The discipline of three roles is the foundation of all evaluation.*

<!-- a-grade-intro:end -->

## What You Will Learn

- The role of each dataset
- Different forms of data leakage
- Principles for splitting time-series data
- Group-aware splitting to prevent group leakage
- Five common pitfalls

## Why It Matters

A wrong split invalidates every measurement that follows. Model comparisons become misleading.

## Concept at a Glance

```mermaid
flowchart LR
    All["all data"] --> Tr["train (fit)"]
    All --> Va["valid (tune)"]
    All --> Te["test (final)"]
```

## Key Terms

- **Train**: data used for fitting.
- **Validation**: tuning hyperparameters and model selection.
- **Test**: the final, single look at the truth.
- **Leakage**: any path that lets the answer slip in.
- **Group split**: prevents the same entity from appearing in two splits.

## Before/After

**Before**: Fit on everything, score on a slice.

**After**: Three distinct splits with preprocessing applied after splitting.

## Hands-on: 5 Splitting Patterns

### Step 1 — Basic split

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
X, y = load_iris(return_X_y=True)
Xtrv, Xte, ytrv, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
Xtr, Xva, ytr, yva = train_test_split(Xtrv, ytrv, test_size=0.25, stratify=ytrv, random_state=42)
print(Xtr.shape, Xva.shape, Xte.shape)
```

### Step 2 — Demonstrate leakage

```python
from sklearn.preprocessing import StandardScaler
sc_bad = StandardScaler().fit(X)
sc_ok = StandardScaler().fit(Xtr)
```

### Step 3 — Time-series split

```python
from sklearn.model_selection import TimeSeriesSplit
import numpy as np
ts = np.arange(20).reshape(-1, 1)
for tr, te in TimeSeriesSplit(n_splits=3).split(ts):
    print(tr[-1], te[0])
```

### Step 4 — Group split

```python
from sklearn.model_selection import GroupKFold
groups = np.array([1,1,1,2,2,3,3,3,4,4])
X = np.arange(10).reshape(-1, 1); y = np.arange(10)
for tr, te in GroupKFold(n_splits=2).split(X, y, groups):
    print(set(groups[te]))
```

### Step 5 — Train after splitting

```python
from sklearn.linear_model import LogisticRegression
sc = StandardScaler().fit(Xtr)
m = LogisticRegression(max_iter=1000).fit(sc.transform(Xtr), ytr)
print("valid:", m.score(sc.transform(Xva), yva))
```

## What to Notice in This Code

- Fitting on the full dataset leaks statistics.
- Time-series splits preserve order.
- Group splits separate identical IDs.

## Five Common Mistakes

1. Tuning on the test set.
2. Random splits on time-series data.
3. Letting group leakage slide.
4. Fitting a scaler on the entire dataset.
5. Repeated comparison on test without a validation set.

## How This Shows Up in Production

Recommendation, healthcare, and finance all rely on group-aware or time-aware splits. The strategy contributes most of real-world performance.

## How a Senior Engineer Thinks

- EDA before splitting is fine; fitting is not.
- Walk-forward for time series.
- Always suspect group or time leakage.
- Protect the scarcity of the test set.
- Document the role of each split.

## Checklist

- [ ] I use three splits.
- [ ] I fit preprocessing after splitting.
- [ ] I split time-series chronologically.
- [ ] I declare groups explicitly.

## Practice Problems

1. Compare test scores when fitting on the full dataset versus on train only.
2. Print 5-fold splits with `TimeSeriesSplit`.
3. Build a `GroupKFold` split that prevents group leakage.

## Wrap-up and Next Steps

The split strategy is the prerequisite for every measurement. Next, we examine the limits of accuracy.

<!-- toc:begin -->
- [Why Model Evaluation Is Hard](./01-why-evaluation-is-hard.md)
- **Train, Validation, and Test (current)**
- The Limits of Accuracy (upcoming)
- Precision and Recall (upcoming)
- F1 Score (upcoming)
- ROC and AUC (upcoming)
- Calibration (upcoming)
- Cross Validation (upcoming)
- Error Analysis (upcoming)
- Building an Evaluation Report (upcoming)
<!-- toc:end -->

## References

- [scikit-learn — Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html)
- [scikit-learn — TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html)
- [Forecasting: Principles and Practice — Hyndman](https://otexts.com/fpp3/)
- [Google — Rules of ML](https://developers.google.com/machine-learning/guides/rules-of-ml)

Tags: ModelEvaluation, TrainValTest, DataLeakage, CrossValidation, scikit-learn
