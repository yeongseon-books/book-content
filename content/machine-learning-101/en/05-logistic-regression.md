---
series: machine-learning-101
episode: 5
title: "Machine Learning 101 (5/10): Logistic Regression"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - MachineLearning
  - LogisticRegression
  - Classification
  - scikit-learn
  - Beginner
seo_description: How logistic regression turns linear scores into probabilities, why thresholds matter, and how precision and recall guide classification decisions
last_reviewed: '2026-05-15'
---

# Machine Learning 101 (5/10): Logistic Regression

Beginner confusion around logistic regression is healthy because the name really is misleading at first glance. It predicts classes in practice, but it does that by assigning probabilities first. The probability layer is where the useful operational decisions live.

This is the 5th post in the Machine Learning 101 series. Here we will treat logistic regression as a probability engine, then connect thresholds, precision, recall, and class imbalance back to the decisions a production system has to make.


![machine learning 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/05/05-01-concept-at-a-glance.en.png)
*machine learning 101 chapter 5 flow overview*
> Logistic regression is linear regression that squashes its score into a probability, then lets you choose where to draw the line between two classes.

## Questions to Keep in Mind

- If the output is 0 or 1, why is the model called regression?
- How does the sigmoid turn a linear score into a probability?
- Why is `0.5` only a default threshold, not a law?

## Why It Matters

Logistic regression is the standard classification baseline. It is interpretable, fast, and stays competitive on imbalanced data when you tune the threshold.

## Key Terms

- **Sigmoid**: maps any real number to (0, 1).
- **Probability**: the model's belief in class 1.
- **Threshold**: turns probability into a class label.
- **Precision**: fraction of predicted positives that are actually positive.
- **Recall**: fraction of actual positives that the model caught.

## Before/After

**Before**: "95% accuracy" — meaningless on imbalanced data.

**After**: Report precision, recall, F1, and AUC together.

## Hands-on: 5 Steps of Classification

### Step 1 — Data

```python
from sklearn.datasets import load_breast_cancer
X, y = load_breast_cancer(return_X_y=True)
```

### Step 2 — Split and scale

```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
sc = StandardScaler().fit(Xtr)
Xtr, Xte = sc.transform(Xtr), sc.transform(Xte)
```

### Step 3 — Fit

```python
from sklearn.linear_model import LogisticRegression
model = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
```

### Step 4 — Evaluate

```python
from sklearn.metrics import classification_report
print(classification_report(yte, model.predict(Xte)))
```

### Step 5 — Tune the threshold

```python
prob = model.predict_proba(Xte)[:, 1]
for t in [0.3, 0.5, 0.7]:
    pred = (prob >= t).astype(int)
    print(t, (pred == yte).mean())
```

**Expected output:** `classification_report` prints class-wise precision and recall, while the threshold loop shows that a different cutoff changes the downstream behavior even when the model weights stay the same. That is the core lesson: thresholding is part of modeling, not a display choice.

## What to Notice in This Code

- `predict_proba` returns probabilities, not just labels.
- The threshold is a precision-recall trade-off knob.
- `StandardScaler` helps the optimizer converge.

## Read the first failure signal this way

- If accuracy looks high but the expensive positive cases are still missed, inspect recall and the threshold before changing models.
- If probabilities look overconfident, test calibration instead of assuming `predict_proba` is production-ready.
- If coefficients drift wildly, verify scaling and class balance before arguing about solver choice.

## Five Common Mistakes

1. Treating raw probabilities as calibrated.
2. Always using 0.5 as the threshold.
3. Reporting accuracy on imbalanced data.
4. Forgetting to scale features.
5. Using defaults on multiclass instead of explicit multinomial.

## How This Shows Up in Production

Spam filtering, fraud detection, and churn modeling all rely on probability outputs because downstream systems need to weigh costs.

## How a Senior Engineer Thinks

- Business cost determines the threshold.
- Always plot the precision-recall curve.
- Use class weights for imbalance.
- Treat interpretability as leverage.
- Validate calibration explicitly.

## Checklist

- [ ] I use `predict_proba` for downstream decisions.
- [ ] I report precision and recall together.
- [ ] I select thresholds based on cost.
- [ ] I always scale features.

## Practice Problems

1. Sweep thresholds from 0.1 to 0.9 and plot precision and recall.
2. Compare results with `class_weight="balanced"`.
3. Apply `multi_class="multinomial"` to a multiclass dataset.

## Wrap-up and Next Steps

Logistic regression is the foundation of classification. Next, we cover decision trees and random forests for nonlinear modeling.

## Answering the Opening Questions

- **The output is 0 or 1, so why is it called "regression"?**
  - Logistic regression first computes a linear score before assigning class labels, then converts that score to a probability using a continuous function. The final purpose is classification, but internally it handles linear combination and probability estimation—hence "regression" remains in the name.
- **How does the sigmoid turn a linear score into a probability?**
  - The formula `σ(z) = 1 / (1 + e^{-z})` compresses any real number `z` to between 0 and 1. `predict_proba(Xte)` shows the model's linear score converted to class-1 probability, with predictions splitting around 0.5 near `z=0`.
- **Why should 0.5 never be treated as the universal correct threshold?**
  - As the threshold loop shows, the same probabilities yield different precision and recall depending on whether you cut at 0.3, 0.5, or 0.7. For fraud detection where misses are costly, a threshold below 0.5 may be more appropriate—the cutoff must be determined alongside domain costs.
<!-- toc:begin -->
## In this series

- [Machine Learning 101 (1/10): What Is Machine Learning?](./01-what-is-machine-learning.md)
- [Machine Learning 101 (2/10): Supervised and Unsupervised Learning](./02-supervised-and-unsupervised.md)
- [Machine Learning 101 (3/10): Train/Test Split](./03-train-test-split.md)
- [Machine Learning 101 (4/10): Linear Regression](./04-linear-regression.md)
- **Logistic Regression (current)**
- Decision Tree and Random Forest (upcoming)
- Clustering (upcoming)
- Overfitting and Regularization (upcoming)
- Model Evaluation (upcoming)
- The ML Project Workflow (upcoming)

<!-- toc:end -->

## References

- [scikit-learn — Logistic Regression](https://scikit-learn.org/stable/modules/linear_model.html#logistic-regression)
- [scikit-learn — Classification metrics](https://scikit-learn.org/stable/modules/model_evaluation.html#classification-metrics)
- [Google — Classification thresholds](https://developers.google.com/machine-learning/crash-course/classification/thresholding)
- [StatQuest — Logistic Regression](https://www.youtube.com/watch?v=yIYKR4sgzI8)

Tags: MachineLearning, LogisticRegression, Classification, scikit-learn, Beginner
