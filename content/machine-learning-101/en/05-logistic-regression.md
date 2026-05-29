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
seo_description: How logistic regression turns a linear score into a probability, threshold tuning, precision, recall, and why 0.5 is not always the right cutoff
last_reviewed: '2026-05-15'
---

# Machine Learning 101 (5/10): Logistic Regression

Predicting 0 or 1 — yet the name says "regression." This is one of the most common beginner confusions, and it is natural. Logistic regression looks like it directly outputs a class, but internally it first computes a continuous probability and then applies a threshold to produce a label. So it handles classification problems, but its internal mechanics are those of a probability model.

This is the 5th post in the Machine Learning 101 series. Here we cover the sigmoid function, thresholds, and precision/recall/F1 — together positioning logistic regression as the most fundamental classification baseline.

![machine learning 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/05/05-01-concept-at-a-glance.en.png)
*machine learning 101 chapter 5 flow overview*
> Logistic regression squeezes a linear score through a sigmoid to get a probability, then draws a boundary line between two classes based on a chosen threshold.

## Questions to Keep in Mind

- If it predicts 0 or 1, why is it called regression?
- How does the sigmoid turn a linear score into a probability?
- Why should 0.5 not always be used as the threshold?

## Sigmoid Function Intuition

The core of logistic regression is the **sigmoid function**. It maps any real number into the range (0, 1).

$$
\sigma(z) = \frac{1}{1 + e^{-z}}
$$

### Why sigmoid?

1. Linear regression `y_hat = Xw + b` can output anything from `-∞` to `+∞`.
2. For classification we want a probability between 0 and 1.
3. Sigmoid compresses any real number into `(0, 1)`, serving exactly this role.

### Sigmoid characteristics

- At `z = 0`, `σ(0) = 0.5`.
- As `z` grows large, `σ(z) → 1`.
- As `z` grows very negative, `σ(z) → 0`.
- Smooth S-shaped curve.

Logistic regression first computes a linear score, then wraps it in a sigmoid to produce a probability.

## Python Example: Checking Probabilities with predict_proba

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

X, y = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
sc = StandardScaler().fit(Xtr)
Xtr, Xte = sc.transform(Xtr), sc.transform(Xte)

model = LogisticRegression(max_iter=1000).fit(Xtr, ytr)

# Check probabilities
proba = model.predict_proba(Xte)[:5]
print("Class 0 | Class 1")
for p0, p1 in proba:
    print(f"{p0:.3f}   | {p1:.3f}")

# Predicted labels
print("Predicted:", model.predict(Xte)[:5])
```

`.predict()` returns 1 when probability exceeds 0.5, otherwise 0. `.predict_proba()` reveals the model's confidence level.

## Logistic vs Linear Regression

| Aspect | Logistic Regression | Linear Regression |
|---|---|---|
| Output | Probability between 0 and 1 | Continuous value |
| Loss function | Log Loss (Cross-Entropy) | MSE |
| Use case | Classification | Regression |

The name is confusing because logistic regression outputs a probability. The final classification is determined only after applying a threshold.

## Why It Matters

Logistic regression is the standard classification baseline. It is interpretable, fast, and — when you tune the threshold — surprisingly competitive even on imbalanced data.

## Key Terms

- **Sigmoid**: Maps any real value into `(0, 1)`.
- **Probability**: The model's belief that the sample belongs to class 1.
- **Threshold**: The cutoff that converts probability into a class label.
- **Precision**: Of predictions called positive, how many actually are.
- **Recall**: Of actual positives, how many the model caught.

## Before/After

**Before**: "95% accuracy" sounds great. On imbalanced data it is nearly meaningless.

**After**: Report precision, recall, F1, and AUC together, and tune the threshold.

## Hands-on: 5-Step Classification

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

### Step 5 — Threshold tuning

```python
prob = model.predict_proba(Xte)[:, 1]
for t in [0.3, 0.5, 0.7]:
    pred = (prob >= t).astype(int)
    print(t, (pred == yte).mean())
```

**Expected output:** `classification_report` shows per-class precision and recall. The threshold loop demonstrates that the same model produces different outcomes at different cutoffs — threshold selection is a **modeling decision**, not a display option.

## What to Notice in This Code

- `predict_proba` returns probabilities, not labels.
- The threshold is the knob that controls the precision-recall tradeoff.
- `StandardScaler` helps the optimizer converge.

## Reading the First Failure Signals

- If accuracy is high but important positives are missed, check **recall** and **threshold** before the model.
- If probabilities look overly confident, verify **calibration** rather than trusting `predict_proba` at face value.
- If coefficients are unstable, investigate **scaling** and **class imbalance** before blaming the solver.

## Five Common Mistakes

1. **Assuming raw probabilities are already calibrated.**
2. **Always using 0.5 as the threshold.**
3. **Reporting only accuracy on imbalanced data.**
4. **Forgetting feature scaling.**
5. **Using default settings for multiclass without explicit multinomial configuration.**

## How This Shows Up in Production

Spam filtering, fraud detection, churn prediction — wherever downstream systems need to **weigh costs**, probability output is essential. Logistic regression is not just a classifier; it becomes an input signal for operational decision-making.

## How a Senior Engineer Thinks

- The threshold is decided by **business cost**.
- Always plot the precision-recall curve.
- For imbalance, consider `class_weight`.
- Interpretability is a valuable lever.
- Probability calibration is verified separately.

## Checklist

- [ ] I use `predict_proba` for downstream decisions.
- [ ] I report precision and recall together.
- [ ] I set the threshold based on cost.
- [ ] I always scale features.

## Practice Problems

1. Sweep the threshold from 0.1 to 0.9 and plot precision and recall.
2. Compare F1 scores with `class_weight="balanced"` vs default.
3. Use `CalibratedClassifierCV` and compare reliability diagrams before and after.

## Summary

Logistic regression is a probability model disguised as a classifier. The sigmoid converts a linear score into a probability; the threshold converts probability into a label. Controlling that threshold — guided by business cost — is where most operational value lives.

Next post: we move to decision trees and random forests, where nonlinearity comes from recursive feature-space splits.

## Answering the Opening Questions

- **If it predicts 0 or 1, why is it called regression?**
  - Internally it regresses onto a continuous probability via the sigmoid. The final class label is only produced after applying a threshold, which is a separate step from the model's core computation.
- **How does the sigmoid turn a linear score into a probability?**
  - It compresses any value from `(-∞, +∞)` into `(0, 1)` via `1/(1+e^{-z})`. At `z=0` the output is 0.5; larger z → closer to 1, smaller z → closer to 0.
- **Why should 0.5 not always be used as the threshold?**
  - Because the optimal cutoff depends on the cost asymmetry of the problem. If missing a positive (FN) is far more expensive than a false alarm (FP), you lower the threshold. The threshold is a business decision, not a mathematical constant.

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

- [scikit-learn — LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html)
- [Stanford CS229 — Logistic Regression](https://cs229.stanford.edu/notes2022fall/main_notes.pdf)
- [Google — ML Crash Course: Classification](https://developers.google.com/machine-learning/crash-course/classification)
- [Hands-On Machine Learning — Aurélien Géron, Ch. 4](https://www.oreilly.com/library/view/hands-on-machine-learning/9781098125967/)

Tags: MachineLearning, LogisticRegression, Classification, scikit-learn, Beginner
