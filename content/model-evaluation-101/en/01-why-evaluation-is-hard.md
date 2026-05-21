---
series: model-evaluation-101
episode: 1
title: "Model Evaluation 101 (1/10): Why Model Evaluation Is Hard"
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
  - Metrics
  - MachineLearning
  - Foundations
  - Beginner
seo_description: Why a single accuracy number is the wrong evaluation, and how data distribution, business cost, and thresholds change the answer
last_reviewed: '2026-05-15'
---

# Model Evaluation 101 (1/10): Why Model Evaluation Is Hard

Model evaluation tends to feel easier in a notebook than it does in production. A single score can look clean, yet the decision behind it is rarely clean. The same 95% accuracy means very different things depending on the data distribution, the cost of mistakes, and the threshold that turns scores into action.

When evaluation gets shaky, model selection gets shaky with it. The real danger is not one bad number, but a whole team optimizing toward the wrong number. That is why evaluation is less about metric calculation and more about decision design.

This is the first post in the Model Evaluation 101 series. In this post, we build the mental model you need before train/validation/test splits, class-specific metrics, and reporting start to matter.


![model evaluation 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/01/01-01-concept-at-a-glance.en.png)
*model evaluation 101 chapter 1 flow overview*

## Questions to Keep in Mind

- Four reasons evaluation is hard?
- Why metrics are not business value?
- The threat of distribution drift?

## Why It Matters

Evaluation is the language of model selection. When the language is wrong, the entire team aims at the wrong target.

## Key Terms

- **Metric**: a numerical summary of performance.
- **Base rate**: class proportion in the data.
- **Threshold**: probability cut-off for class assignment.
- **Drift**: change in distribution over time.
- **Cost matrix**: distinct costs for different errors.

## Before/After

**Before**: One accuracy number drives the decision.

**After**: Metrics, confusion matrix, cost, and drift are reviewed together.

## Hands-on: 5 Steps Through Evaluation Pitfalls

### Step 1 — Imbalanced data

```python
import numpy as np
y = np.array([0]*95 + [1]*5)
pred_dummy = np.zeros_like(y)
print("acc:", (pred_dummy == y).mean())
```

### Step 2 — The accuracy trap

```python
print("recall (1):", ((pred_dummy == 1) & (y == 1)).sum() / (y == 1).sum())
```

### Step 3 — Confusion matrix

```python
from sklearn.metrics import confusion_matrix
print(confusion_matrix(y, pred_dummy))
```

### Step 4 — Threshold sensitivity

```python
import numpy as np
prob = np.linspace(0, 1, 100)
yt = (prob > 0.5).astype(int)
for t in [0.3, 0.5, 0.7]:
    pred = (prob >= t).astype(int)
    print(t, (pred == yt).mean())
```

### Step 5 — Cost weighting

```python
def cost(tp, fp, fn, c_fp=1, c_fn=10):
    return c_fp * fp + c_fn * fn
print("cost:", cost(tp=5, fp=10, fn=2))
```

**Expected output:** You should see that the dummy model can look strong on accuracy while still collapsing on recall, and that the "best" threshold changes once you price false positives and false negatives differently.

## What to Notice in This Code

- 95% accuracy can be completely useless.
- The threshold moves every metric.
- The cost matrix represents the real decision.

## Five Common Mistakes

1. Selecting models based on a single metric.
2. Ignoring base rates.
3. Re-evaluating on the test set.
4. Locking the threshold to 0.5.
5. Skipping business cost considerations.

## How This Shows Up in Production

A/B experiments, MLOps gates, and compliance reviews all hinge on the evaluation definition. It is the contract among teams.

## How a Senior Engineer Thinks

- Order: business cost, then metric, then threshold.
- One metric is rarely enough.
- Touch the test set exactly once.
- Drift always happens.
- Treat evaluation as code worth reviewing.

## Checklist

- [ ] At least two metrics in addition to accuracy.
- [ ] Always include the confusion matrix.
- [ ] Document the business cost.
- [ ] Justify the threshold with reasoning.

## Practice Problems

1. Build a dummy model that scores 99% accuracy on a 1% base-rate dataset.
2. Sweep thresholds from 0.1 to 0.9 and compare precision and recall.
3. Define a cost matrix and minimize total cost over thresholds.

## Wrap-up and Next Steps

Evaluation is the language of model selection. Next, we cover the roles of train, validation, and test sets.

## Answering the Opening Questions

- **Four reasons evaluation is hard?**
  - The article treats Why Model Evaluation Is Hard as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Why metrics are not business value?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **The threat of distribution drift?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- **Why Model Evaluation Is Hard (current)**
- Train, Validation, and Test (upcoming)
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

- [scikit-learn — Model evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [Google — Rules of ML](https://developers.google.com/machine-learning/guides/rules-of-ml)
- [Wikipedia — Confusion matrix](https://en.wikipedia.org/wiki/Confusion_matrix)
- [Pattern Recognition and Machine Learning — Bishop](https://www.microsoft.com/en-us/research/people/cmbishop/prml-book/)

Tags: ModelEvaluation, Metrics, MachineLearning, Foundations, Beginner
