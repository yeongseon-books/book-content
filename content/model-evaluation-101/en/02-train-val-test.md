---
series: model-evaluation-101
episode: 2
title: "Model Evaluation 101 (2/10): Train, Validation, and Test"
status: publish-ready
targets:
  tistory: false
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
last_reviewed: '2026-05-15'
---

# Model Evaluation 101 (2/10): Train, Validation, and Test

Model quality is often decided long before you compute the first metric. If the split is wrong, every number that follows can still look polished while being untrustworthy. Leakage from preprocessing, random splits on time-series data, or the same user showing up in multiple splits can all inflate performance fast.

That is why train, validation, and test are not textbook ceremony. They are a discipline for separating learning, selection, and final verification. Once those roles blur together, evaluation stops being evidence and starts becoming wishful thinking.

This is the 2nd post in the Model Evaluation 101 series. In this post, we define what each split is allowed to do and where leakage usually sneaks in.


![model evaluation 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/02/02-01-concept-at-a-glance.en.png)
*model evaluation 101 chapter 2 flow overview*

> Train / validation / test are three different jobs (learning, selection, final verification) — once those roles blur, every downstream number looks polished while being untrustworthy.

## Questions to Keep in Mind

- The role of each dataset?
- Different forms of data leakage?
- Principles for splitting time-series data?

## Why It Matters

A wrong split invalidates every measurement that follows. Model comparisons become misleading.

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

**Expected output:** You should see that fitting transforms on the full dataset quietly leaks statistics, while time-aware and group-aware splits preserve the boundary between what the model is allowed to know and what it must still prove.

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

## Answering the Opening Questions

- **What role should train, validation, and test each serve?**
  - Train is the segment where `LogisticRegression` learns parameters, validation is where you pick hyperparameters and thresholds, and test is where you confirm performance exactly once at the end. The article created `Xtr`, `Xva`, `Xte` separately because mixing each set's responsibility destroys score interpretation.
- **Why shouldn't you use validation and test for the same purpose?**
  - If you repeatedly peek at test to select models, that set is no longer final verification but tuning data. The article explains that you should finish selection with validation and lock test away, so the final score remains generalization performance on never-before-seen data.
- **Through what paths does data leakage most commonly enter?**
  - In the examples, fitting preprocessing on the full dataset like `StandardScaler().fit(X)` was the classic leakage case, along with random splits on time series and duplicate appearances of the same user group. That's why choosing a split method matching the data structure first—like `TimeSeriesSplit` or `GroupKFold`—is the key.
<!-- toc:begin -->
## In this series

- [Model Evaluation 101 (1/10): Why Model Evaluation Is Hard](./01-why-evaluation-is-hard.md)
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
