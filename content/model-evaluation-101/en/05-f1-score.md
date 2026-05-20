---
series: model-evaluation-101
episode: 5
title: "Model Evaluation 101 (5/10): F1 Score"
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
  - F1Score
  - Fbeta
  - ImbalancedData
  - scikit-learn
seo_description: "How F1 changes across averaging modes, and how to pick thresholds with proper train/validation/test separation"
last_reviewed: '2026-05-17'
---

# Model Evaluation 101 (5/10): F1 Score

This is post 5 in the Model Evaluation 101 series.

Once precision and recall are framed as a threshold memo, teams immediately ask for one compact number. F1 is usually the answer. The problem is that the earlier version of this chapter used `ko/05-f1-score.md:109-118` to sweep thresholds on the same binary data that was used for training, which teaches exactly the optimistic tuning pattern the series should avoid.

This rewrite fixes that defect directly. F1 is still useful, but threshold selection now follows the correct **train → validation → test** flow. At the same time, macro, micro, and weighted F1 are connected back to the review question they actually answer.

## Questions to Keep in Mind

- What boundary should you inspect first when applying F1 Score?
- Which signal should the example or diagram make visible for F1 Score?
- What failure should be prevented first when F1 Score reaches a real system?

## Big Picture

![model evaluation 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/05/05-01-concept-at-a-glance.en.png)

*model evaluation 101 chapter 5 flow overview*

This picture places F1 Score inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of F1 Score is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## This post answers

- What review question do macro, micro, and weighted F1 each answer?
- Why is threshold tuning on the training data itself optimistic?
- Why might the best validation F1 threshold still be the wrong production threshold?

## What F1 can summarize and what it cannot

F1 is the harmonic mean of precision and recall, so it drops whenever either side collapses. That is useful. But F1 is still a summary.

- It can hide which averaging mode was used.
- It can hide which class is weak.
- It can hide which threshold produced the number.
- It can hide whether the threshold was tuned on the wrong split.

So the right question is not “what is the F1?” but “which F1, chosen how, and for what decision?”

## Concept at a glance

This chapter has two branching points: which averaging mode you use in multiclass evaluation, and which threshold you lock in for the binary operating policy.

## Part 1 — The same predictions produce different F1 summaries

```python
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, fbeta_score
from sklearn.model_selection import train_test_split

X, y = make_classification(
    n_samples=3200,
    n_features=12,
    n_informative=6,
    n_redundant=2,
    n_classes=3,
    n_clusters_per_class=1,
    weights=[0.65, 0.25, 0.10],
    class_sep=1.1,
    flip_y=0.02,
    random_state=11,
)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    stratify=y,
    random_state=42,
)

model = LogisticRegression(max_iter=4000).fit(X_train, y_train)
pred = model.predict(X_test)

print("micro:", round(f1_score(y_test, pred, average="micro"), 3))
print("macro:", round(f1_score(y_test, pred, average="macro"), 3))
print("weighted:", round(f1_score(y_test, pred, average="weighted"), 3))
print("per class:", [round(x, 3) for x in f1_score(y_test, pred, average=None)])
print("F2 macro:", round(fbeta_score(y_test, pred, beta=2, average="macro"), 3))
print("F0.5 macro:", round(fbeta_score(y_test, pred, beta=0.5, average="macro"), 3))
```

Expected output:

```text
micro: 0.927
macro: 0.881
weighted: 0.925
per class: [0.952, 0.923, 0.768]
F2 macro: 0.866
F0.5 macro: 0.900
```

Those numbers answer different questions.

- **Micro F1 = 0.927**: dominated by total volume, so the majority class matters most.
- **Macro F1 = 0.881**: every class gets an equal vote.
- **Weighted F1 = 0.925**: tracks the original class distribution.
- **Per-class F1 = [0.952, 0.923, 0.768]**: the third class is the real weakness.

That is why `F1=0.92` is incomplete unless you name the averaging mode.

## Part 2 — Threshold selection must use train, validation, and test separately

Now we fix the exact issue #772 defect. The binary example below does **not** train and tune on the same data.

```python
import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

X, y = make_classification(
    n_samples=4000,
    n_features=10,
    n_informative=5,
    n_redundant=2,
    weights=[0.88, 0.12],
    class_sep=1.0,
    flip_y=0.02,
    random_state=19,
)

X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.4,
    stratify=y,
    random_state=42,
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp,
    y_temp,
    test_size=0.5,
    stratify=y_temp,
    random_state=42,
)

model = LogisticRegression(max_iter=4000).fit(X_train, y_train)
val_proba = model.predict_proba(X_val)[:, 1]
test_proba = model.predict_proba(X_test)[:, 1]

thresholds = np.arange(0.10, 0.91, 0.05)
rows = []
for threshold in thresholds:
    val_pred = (val_proba >= threshold).astype(int)
    rows.append(
        (
            round(float(threshold), 2),
            f1_score(y_val, val_pred),
            precision_score(y_val, val_pred, zero_division=0),
            recall_score(y_val, val_pred, zero_division=0),
        )
    )

best_threshold, best_val_f1, _, _ = max(rows, key=lambda row: row[1])
print("validation sweep:")
for threshold, f1, precision, recall in rows:
    if threshold in {0.20, 0.30, 0.50, 0.70}:
        print(threshold, round(f1, 3), round(precision, 3), round(recall, 3))

print("best validation threshold:", best_threshold, round(best_val_f1, 3))

locked_test_pred = (test_proba >= best_threshold).astype(int)
print(
    "locked test:",
    round(f1_score(y_test, locked_test_pred), 3),
    round(precision_score(y_test, locked_test_pred), 3),
    round(recall_score(y_test, locked_test_pred), 3),
)

business_pred = (test_proba >= 0.50).astype(int)
print(
    "business threshold 0.50:",
    round(f1_score(y_test, business_pred), 3),
    round(precision_score(y_test, business_pred), 3),
    round(recall_score(y_test, business_pred), 3),
)
```

Expected output:

```text
validation sweep:
0.20 0.596 0.485 0.775
0.30 0.585 0.564 0.608
0.50 0.503 0.776 0.373
0.70 0.354 0.821 0.225
best validation threshold: 0.2 0.596
locked test: 0.627 0.527 0.775
business threshold 0.50: 0.490 0.717 0.373
```

## Why this procedure matters

On the validation split, the best F1 threshold is **0.20**. Once that threshold is chosen, it is locked and carried unchanged to the test split, where it produces `F1=0.627`, `precision=0.527`, and `recall=0.775`.

That is the correct question: does the policy selected on validation survive on held-out data?

If you train and tune on the same data, you allow threshold choice to absorb chance patterns from the training sample. That is the optimistic workflow issue #772 explicitly asked us to remove.

## The best F1 threshold may still be the wrong business threshold

Not every team should ship the threshold that maximizes validation F1.

In this example, 0.20 wins on F1, but on the test split it also creates many false alarms. Threshold **0.50** has a lower F1, yet precision climbs to **0.717**. If reviewer fatigue is the dominant cost, 0.50 may still be the better operating choice.

That leads to the real review question.

- Is the goal to miss fewer positives? Then 0.20 is attractive.
- Is the goal to protect a limited false-positive budget? Then 0.50 may be safer.

F1 tells you about balance. It does not, by itself, encode policy.

## F-beta is how you stop hiding the cost preference

In the multiclass example, `F2 macro=0.866` and `F0.5 macro=0.900` differ because the metric itself changes what it values.

- **F2** weights recall more heavily.
- **F0.5** weights precision more heavily.

So beta should come from cost structure, not personal taste. If misses are more expensive, a recall-heavy beta makes sense. If false alarms are more expensive, a precision-heavy beta makes sense.

## What a solid review sentence sounds like

> Macro F1 is 0.881, but the minority class remains weaker at 0.768 per-class F1. For the binary operating policy, threshold 0.20 maximized validation F1 and delivered test F1 0.627 with precision 0.527 and recall 0.775. However, if the review team cannot absorb that false-positive rate, a stricter threshold such as 0.50 should be considered despite its lower F1.

That sentence keeps the convenience of F1 without hiding the averaging mode, threshold procedure, or operating trade-off.

## Checklist

- [ ] I name the F1 averaging mode.
- [ ] I inspect per-class F1, not just the aggregate.
- [ ] I separate train, validation, and test for threshold choice.
- [ ] I lock the chosen validation threshold before evaluating on test.
- [ ] I state whether the highest-F1 threshold is also the preferred business threshold.

## Wrap-up

F1 is still a useful summary, but only after you make its hidden choices explicit. The next chapter zooms out to ROC and AUC for threshold-free ranking quality, then brings the conversation back down to the operating threshold you still have to choose in the end.

## Answering the Opening Questions

- **What boundary should you inspect first when applying F1 Score?**
  - The article treats F1 Score as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for F1 Score?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when F1 Score reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Model Evaluation 101 (1/10): Why Model Evaluation Is Hard](./01-why-evaluation-is-hard.md)
- [Model Evaluation 101 (2/10): Train, Validation, and Test](./02-train-val-test.md)
- [Model Evaluation 101 (3/10): The Limits of Accuracy](./03-limits-of-accuracy.md)
- [Model Evaluation 101 (4/10): Precision and Recall](./04-precision-and-recall.md)
- **F1 Score (current)**
- ROC and AUC (upcoming)
- Calibration (upcoming)
- Cross Validation (upcoming)
- Error Analysis (upcoming)
- Building an Evaluation Report (upcoming)

<!-- toc:end -->

## References

- [scikit-learn — f1_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html)
- [scikit-learn — fbeta_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.fbeta_score.html)
- [scikit-learn — precision_recall_fscore_support](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_fscore_support.html)
- [Wikipedia — F-score](https://en.wikipedia.org/wiki/F-score)

Tags: ModelEvaluation, F1Score, Fbeta, ImbalancedData, scikit-learn
