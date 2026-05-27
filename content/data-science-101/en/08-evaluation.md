---
series: data-science-101
episode: 8
title: "Data Science 101 (8/10): Evaluation"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - DataScience
  - Evaluation
  - Metrics
  - ScikitLearn
  - Beginner
seo_description: Why accuracy can lie, plus a practical tour of precision, recall, F1, ROC AUC, MAE, RMSE, and how to encode business cost into the metric
last_reviewed: '2026-05-15'
---

# Data Science 101 (8/10): Evaluation

Evaluation is where teams discover whether a model is useful for the problem they actually have, not the benchmark they wish they had. Accuracy feels satisfying because it is easy to explain, but in imbalanced or asymmetric problems it can reward exactly the wrong behavior.

Good evaluation therefore starts with the cost of being wrong. If missing a positive case is expensive, the metric has to show that. If a false alarm is the real operational pain, the metric has to show that instead.

This is the 8th post in the Data Science 101 series. In this chapter, we connect classification and regression metrics back to business cost so that model scores line up with real decisions.


![data science 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/data-science-101/08/08-01-concept-at-a-glance.en.png)
*data science 101 chapter 8 flow overview*
> At its core, Evaluation is about deciding what enters a system, where validation happens, and which signals stay for the next cycle—not about feature names.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Evaluation?
- Which signal should the example or diagram make visible for Evaluation?
- What failure should be prevented first when Evaluation reaches a real system?

## Questions This Post Answers

- When does accuracy become the wrong summary of model quality?
- How do precision, recall, F1, and ROC AUC support different operational trade-offs?
- Which regression metric matches which error tolerance?
- How do you encode business cost so the model score matches the real decision?

> Metric choice is really cost choice: it tells the team which failure mode matters most.

## What You Will Learn

- How *accuracy can mislead*
- Classification: *precision / recall / F1 / ROC AUC*
- Regression: *MAE / RMSE / R²*
- A 5-step evaluation exercise
- Five common pitfalls

## Why It Matters

If the metric *misaligns with the problem*, the model learns the *wrong direction*. Encoding *business cost* into the metric makes *decisions land*.

> *Metrics are *what you optimize* — choose them carefully.*

The key boundary in this episode is between the concept itself and how it operates in a real system. You need to know where the data comes in, where the decision happens, and what signal must be recorded.

## Key Terms

- **Confusion matrix**: TP / FP / FN / TN table.
- **Precision**: of *predicted positives*, how many are right.
- **Recall**: of *actual positives*, how many we caught.
- **F1**: *harmonic mean* of P and R.
- **ROC AUC**: threshold-independent *separability*.

## Before / After

**Before**: fraud model hits *99% accuracy*, but *recall is 5%* — most fraud is missed.

**After**: *recall* is the primary metric, with *F1 / cost* as secondary.

## Hands-on: 5-step Evaluation

### Step 1 — Confusion matrix

```python
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_test, y_pred)
print(cm)
```

### Step 2 — Precision / Recall / F1

```python
from sklearn.metrics import precision_score, recall_score, f1_score
print(precision_score(y_test, y_pred))
print(recall_score(y_test, y_pred))
print(f1_score(y_test, y_pred))
```

### Step 3 — ROC AUC

```python
from sklearn.metrics import roc_auc_score
proba = model.predict_proba(X_test)[:, 1]
print(roc_auc_score(y_test, proba))
```

### Step 4 — Regression metrics

```python
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

print("MAE :", mean_absolute_error(y_test, y_pred))
print("RMSE:", np.sqrt(mean_squared_error(y_test, y_pred)))
print("R^2 :", r2_score(y_test, y_pred))
```

### Step 5 — Encode business cost

```python
# A false negative costs 5x a false positive
cost = 5 * cm[1, 0] + 1 * cm[0, 1]
print("expected cost:", cost)
```

**Expected output:** one evaluation table that puts the confusion matrix, P/R/F1, ROC AUC, and business-cost score side by side.

## What to Notice in This Code

- The *confusion matrix* is the *root* of every classification metric.
- *Probability-based* metrics like ROC AUC are *threshold-independent*.
- *Business cost* should be computed *directly* and treated as a metric.

## Five Common Mistakes

1. **Watching only *accuracy*.** Misleading on imbalanced data.
2. **Looking at only *one threshold*.** Always pair with *ROC*.
3. **Watching only *RMSE*.** It's *too sensitive* to outliers.
4. **Tuning the *threshold on the test set*.** That's *data leakage*.
5. **Ignoring *business cost*.** Decisions and metrics drift apart.

## How This Shows Up in Production

Teams pair a *primary metric* with *guardrail metrics*. Example: primary = *recall*, guardrail = *precision >= 0.7*.

## How a Senior Engineer Thinks

- Pick the *metric with the problem*.
- Document the *cost matrix* in writing.
- Separate *primary* from *guardrails*.
- Tune *thresholds on validation*, never on test.
- Treat *metric changes* as *PR-worthy*.

## Checklist

- [ ] I know the difference between *Precision / Recall / F1*.
- [ ] I understand *ROC AUC*.
- [ ] I know the difference between *MAE / RMSE / R²*.
- [ ] I can build a *cost matrix*.

## Practice Problems

1. On *imbalanced data*, build a case where *accuracy and recall disagree*.
2. Plot a *ROC curve* and observe the *threshold trade-off*.
3. Define a *cost-based metric* and pick the *optimal threshold*.

## Wrap-up and Next Steps

Evaluation is the *conversation* between problem and model. Next we look at how to *interpret* the results into a *decision*.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Evaluation?**
  - The article treats Evaluation as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Evaluation?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Evaluation reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Data Science 101 (1/10): What Is Data Science?](./01-what-is-data-science.md)
- [Data Science 101 (2/10): Turning a Problem into a Data Problem](./02-problem-to-data-problem.md)
- [Data Science 101 (3/10): Data Collection](./03-data-collection.md)
- [Data Science 101 (4/10): Data Cleaning](./04-data-cleaning.md)
- [Data Science 101 (5/10): Exploratory Data Analysis](./05-exploratory-data-analysis.md)
- [Data Science 101 (6/10): Visualization](./06-visualization.md)
- [Data Science 101 (7/10): Modeling](./07-modeling.md)
- **Evaluation (current)**
- Result Interpretation (upcoming)
- End-to-End Data Project Flow (upcoming)

<!-- toc:end -->

## References

- [scikit-learn — Model Evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [Google — Classification Metrics](https://developers.google.com/machine-learning/crash-course/classification)
- [Wikipedia — Receiver Operating Characteristic](https://en.wikipedia.org/wiki/Receiver_operating_characteristic)
- [Aurelien Geron — Hands-On ML](https://github.com/ageron/handson-ml3)

Tags: DataScience, Evaluation, Metrics, ScikitLearn, Beginner
