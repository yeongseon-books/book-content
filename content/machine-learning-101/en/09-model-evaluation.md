---
series: machine-learning-101
episode: 9
title: "Machine Learning 101 (9/10): Model Evaluation"
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
  - Evaluation
  - Metrics
  - ROC
  - scikit-learn
seo_description: How to choose the right metric for classification and regression, read confusion matrices, and compare ROC and PR curves with scikit-learn
last_reviewed: '2026-05-15'
---

# Machine Learning 101 (9/10): Model Evaluation

“Which model is better?” is an incomplete question until someone adds a metric and a business cost. Without that context, evaluation becomes theater: numbers move, dashboards look scientific, and the organization still cannot decide which errors it is willing to pay for.

This is post 9 in the Machine Learning 101 series. Here we will connect confusion matrices, ROC and PR curves, regression metrics, and threshold choices back to the more important decision: what kind of failure matters most in the real system.


![machine learning 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/09/09-01-concept-at-a-glance.en.png)
*machine learning 101 chapter 9 flow overview*

## Questions to Keep in Mind

- Which metrics belong to classification versus regression?
- What does each cell of the confusion matrix tell you operationally?
- When should PR outrank ROC in your analysis?

## Why It Matters

Wrong metric, wrong decision. When business cost and metric drift apart, the model only looks good on paper.

## Key Terms

- **TP / FP / FN / TN**: the four quadrants of the confusion matrix.
- **Accuracy**: fraction of correct predictions.
- **Precision**: fraction of predicted positives that are right.
- **Recall**: fraction of actual positives caught.
- **AUC**: average performance across thresholds.

## Before/After

**Before**: A single accuracy number in the report.

**After**: Metric table, confusion matrix, and PR or ROC curves together.

## Hands-on: 5 Steps of Evaluation

### Step 1 — Data

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
X, y = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
```

### Step 2 — Model

```python
from sklearn.linear_model import LogisticRegression
m = LogisticRegression(max_iter=2000).fit(Xtr, ytr)
prob = m.predict_proba(Xte)[:, 1]
pred = (prob >= 0.5).astype(int)
```

### Step 3 — Confusion matrix

```python
from sklearn.metrics import confusion_matrix
print(confusion_matrix(yte, pred))
```

### Step 4 — Classification metrics

```python
from sklearn.metrics import classification_report, roc_auc_score, average_precision_score
print(classification_report(yte, pred))
print("ROC-AUC:", roc_auc_score(yte, prob))
print("PR-AUC :", average_precision_score(yte, prob))
```

### Step 5 — Regression metrics

```python
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
yt, yp = np.array([3.0, 5.0, 2.5]), np.array([2.8, 5.4, 2.1])
print("MAE:", mean_absolute_error(yt, yp))
print("RMSE:", mean_squared_error(yt, yp) ** 0.5)
print("R^2:", r2_score(yt, yp))
```

**Expected output:** the confusion matrix should expose the actual error mix, while ROC-AUC and PR-AUC summarize ranking quality across thresholds. In the regression toy example, MAE and RMSE stay close only because the errors are small and fairly even.

## What to Notice in This Code

- AUC is independent of the threshold.
- PR-AUC is more informative on imbalanced data.
- RMSE and MAE differ in their sensitivity to outliers.

## Read the first failure signal this way

- If metric debates drag on, translate the disagreement into the cost of false positives versus false negatives.
- If the dataset is imbalanced, do not stop at ROC-AUC before checking PR behavior and threshold sensitivity.
- If a model looks good by one metric and bad by another, that is not a contradiction; it is a prompt to clarify which failure matters.

## Five Common Mistakes

1. Reporting accuracy on imbalanced data.
2. Trusting ROC-AUC on heavy class imbalance.
3. Ignoring threshold tuning while optimizing F1.
4. Reporting only one of MAE or RMSE for regression.
5. Repeated evaluation on the same test set leaks information.

## How This Shows Up in Production

A/B testing, model gates, and MLOps monitoring all rest on the metric definition. The metric is the language of organizational agreement.

## How a Senior Engineer Thinks

- Order: business cost, then metric, then threshold.
- The PR curve is the truth on imbalance.
- Maximize recall when missing positives is catastrophic.
- Calibration is part of evaluation, not optional.
- One metric is rarely enough.

## Checklist

- [ ] I always print a confusion matrix.
- [ ] I look at ROC and PR together.
- [ ] I report MAE and RMSE for regression.
- [ ] I touch the test set exactly once at the end.

## Practice Problems

1. Compare accuracy and F1 on imbalanced data.
2. Plot ROC and PR curves side by side.
3. Construct a dataset where MAE and RMSE strongly disagree.

## Wrap-up and Next Steps

Evaluation is the language of model selection. Next, we close the series with the end-to-end ML project workflow.

## Answering the Opening Questions

- **Which metrics belong to classification versus regression?**
  - The article treats Model Evaluation as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **What does each cell of the confusion matrix tell you operationally?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **When should PR outrank ROC in your analysis?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Machine Learning 101 (1/10): What Is Machine Learning?](./01-what-is-machine-learning.md)
- [Machine Learning 101 (2/10): Supervised and Unsupervised Learning](./02-supervised-and-unsupervised.md)
- [Machine Learning 101 (3/10): Train/Test Split](./03-train-test-split.md)
- [Machine Learning 101 (4/10): Linear Regression](./04-linear-regression.md)
- [Machine Learning 101 (5/10): Logistic Regression](./05-logistic-regression.md)
- [Machine Learning 101 (6/10): Decision Tree and Random Forest](./06-decision-tree-and-random-forest.md)
- [Machine Learning 101 (7/10): Clustering](./07-clustering.md)
- [Machine Learning 101 (8/10): Overfitting and Regularization](./08-overfitting-and-regularization.md)
- **Model Evaluation (current)**
- The ML Project Workflow (upcoming)

<!-- toc:end -->

## References

- [scikit-learn — Model evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [scikit-learn — ROC and PR curves](https://scikit-learn.org/stable/auto_examples/model_selection/plot_precision_recall.html)
- [Google — Classification metrics](https://developers.google.com/machine-learning/crash-course/classification/precision-and-recall)
- [Wikipedia — Confusion matrix](https://en.wikipedia.org/wiki/Confusion_matrix)

Tags: MachineLearning, Evaluation, Metrics, ROC, scikit-learn
