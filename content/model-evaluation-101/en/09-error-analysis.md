---
series: model-evaluation-101
episode: 9
title: Error Analysis
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - ModelEvaluation
  - ErrorAnalysis
  - Slicing
  - Debugging
  - scikit-learn
seo_description: Error analysis breaks accuracy into slices, error types, and confidence buckets to expose model weaknesses, with runnable code examples
last_reviewed: '2026-05-04'
---

# Error Analysis

> Model Evaluation 101 series (9/10)

<!-- a-grade-intro:begin -->

**Core question**: Two models with the same overall score — how do you find where they fail differently?

> *Error analysis breaks the aggregate average into subgroups to reveal patterns of weakness.*

<!-- a-grade-intro:end -->

This is post 9 in the Model Evaluation 101 series.

## What You Will Learn

- Decomposing performance by slice
- Classifying error types (FP, FN, class confusion)
- Analyzing accuracy by confidence
- Telling data problems from model problems
- Five common pitfalls

## Why It Matters

92% accuracy overall can hide 60% accuracy on a specific user segment, which is a fairness issue.

## Concept at a Glance

```mermaid
flowchart LR
    All["all errors"] --> Slice["slice by feature"]
    All --> Conf["slice by confidence"]
    All --> Conf2["confusion pairs"]
    Slice --> Weak["weakest segment"]
    Conf --> Calib["calibration gap"]
```

## Key Terms

- **Slice**: a subset of the data defined by some condition.
- **Confusion pair**: classes that are frequently swapped.
- **Confidence histogram**: distribution of predicted probabilities.
- **Hard example**: a sample that is repeatedly misclassified.
- **Label noise**: cases where the ground truth itself is wrong.

## Before/After

**Before**: "92% accuracy, looks good."

**After**: a per-segment table, the weakest slice identified, and either data or modeling fixes scheduled.

## Hands-on: 5 Steps of Error Analysis

### Step 1 — Data and model

```python
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
X, y = make_classification(n_samples=3000, n_features=8, weights=[0.7, 0.3], random_state=0)
Xtr, Xte, ytr, yte = train_test_split(X, y, stratify=y, random_state=42)
m = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
proba = m.predict_proba(Xte)[:, 1]
pred = (proba >= 0.5).astype(int)
```

### Step 2 — Slice scores

```python
from sklearn.metrics import f1_score
slice_mask = Xte[:, 0] > 0
print("slice + :", f1_score(yte[slice_mask], pred[slice_mask]))
print("slice - :", f1_score(yte[~slice_mask], pred[~slice_mask]))
```

### Step 3 — Error types

```python
fp = (pred == 1) & (yte == 0)
fn = (pred == 0) & (yte == 1)
print("FP:", fp.sum(), "FN:", fn.sum())
```

### Step 4 — Error rate per confidence bucket

```python
bins = np.linspace(0, 1, 6)
for lo, hi in zip(bins[:-1], bins[1:]):
    m_ = (proba >= lo) & (proba < hi)
    if m_.sum():
        err = (pred[m_] != yte[m_]).mean()
        print(round(lo, 1), round(hi, 1), "err:", round(err, 3))
```

### Step 5 — Most ambiguous samples

```python
order = np.argsort(np.abs(proba - 0.5))[:10]
print("ambiguous indices:", order.tolist())
```

## What to Notice in This Code

- Slice scores are the starting point of fairness work.
- Splitting FP and FN guides threshold tuning.
- Ambiguous samples are prime candidates for label review.

## Five Common Mistakes

1. Trusting the overall score and ignoring segments.
2. Lumping FP and FN together.
3. Blaming the model for label noise.
4. Tuning the threshold without confidence-bucket analysis.
5. Defining slices after seeing the result (cherry-picking).

## How This Shows Up in Production

Reliability and fairness audits sometimes require per-segment reports by law.

## How a Senior Engineer Thinks

- The weakest slice is more dangerous than the overall number.
- Different error types deserve different fixes.
- Label quality caps model quality.
- Pre-define slices.
- Look at the correlation between confidence and error rate.

## Checklist

- [ ] I report on at least two slices.
- [ ] I split FP and FN.
- [ ] I review error rate by confidence bucket.
- [ ] I audit labels of ambiguous samples.

## Practice Problems

1. Bucket a continuous feature into three ranges and compare slice scores.
2. Tabulate how threshold changes shift the FP-to-FN ratio.
3. Manually inspect labels for the top 10 ambiguous samples.

## Wrap-up and Next Steps

Error analysis answers "why does it fail?" Next, the evaluation report ties everything into one document.

<!-- toc:begin -->
- [Why Model Evaluation Is Hard](./01-why-evaluation-is-hard.md)
- [Train, Validation, and Test](./02-train-val-test.md)
- [The Limits of Accuracy](./03-limits-of-accuracy.md)
- [Precision and Recall](./04-precision-and-recall.md)
- [F1 Score](./05-f1-score.md)
- [ROC and AUC](./06-roc-and-auc.md)
- [Calibration](./07-calibration.md)
- [Cross Validation](./08-cross-validation.md)
- **Error Analysis (current)**
- Building an Evaluation Report (upcoming)
<!-- toc:end -->

## References

- [scikit-learn — Model evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [Google — Model debugging](https://developers.google.com/machine-learning/testing-debugging)
- [Kaggle — Intermediate ML](https://www.kaggle.com/learn/intermediate-machine-learning)
- [Andrew Ng — Error analysis](https://www.deeplearning.ai/the-batch/issue-115/)

Tags: ModelEvaluation, ErrorAnalysis, Slicing, Debugging, scikit-learn
