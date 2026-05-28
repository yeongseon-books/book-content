---
series: model-evaluation-101
episode: 4
title: "Model Evaluation 101 (4/10): Precision and Recall"
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
  - Precision
  - Recall
  - ConfusionMatrix
  - scikit-learn
seo_description: Precision and recall as a threshold decision memo, with an operating-point table and concrete deployment consequences
last_reviewed: '2026-05-17'
---

# Model Evaluation 101 (4/10): Precision and Recall

This is the 4th post in the Model Evaluation 101 series.

Issue #772 called out that this chapter repeated the same mid-series narrative rhythm as its neighbors. The real weakness was not the definitions. It was that `ko/04-precision-and-recall.md:43-68` never centered the question an operator actually asks: **what happens if we lower the threshold, and what do we give up if we raise it?**

So this rewrite is structured as a threshold decision memo. Precision and recall are not here as terms to memorize. They are here as the numbers you use to decide how many alerts to send and how many real cases you can afford to miss.


![model evaluation 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/04/04-01-concept-at-a-glance.en.png)
*model evaluation 101 chapter 4 flow overview*

## Questions to Keep in Mind

- What do precision and recall each measure?
- When should you prioritize precision over recall, and vice versa?
- How does changing the decision threshold shift the precision-recall trade-off?

## This post answers

- What changes in review load and misses when the threshold moves?
- Why is 0.35 a defensible default operating point in this example?
- Why is average precision useful for comparison but insufficient for deployment policy?

## Start with the operating scenario

Assume the model flags suspicious payment activity and sends cases to a manual review queue.

- If **recall is too low**, true risky payments slip through.
- If **precision is too low**, reviewers drown in false alarms.

That makes the real chapter question this one:

> If the threshold is 0.20, 0.35, 0.50, or 0.70, which operating point can the team actually live with?

## Concept at a glance

Lower thresholds usually increase recall by casting a wider net, but that wider net also pulls in more false positives and hurts precision. This chapter is about translating that trade-off into an operational recommendation.

## Code that produces a real decision memo

```python
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

X, y = make_classification(
    n_samples=3000,
    n_features=10,
    n_informative=5,
    n_redundant=2,
    weights=[0.9, 0.1],
    class_sep=1.0,
    flip_y=0.02,
    random_state=7,
)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.3,
    stratify=y,
    random_state=42,
)

model = LogisticRegression(max_iter=4000).fit(X_train, y_train)
proba = model.predict_proba(X_test)[:, 1]

for threshold in [0.20, 0.35, 0.50, 0.70]:
    pred = (proba >= threshold).astype(int)
    print(
        threshold,
        "precision=", round(precision_score(y_test, pred), 3),
        "recall=", round(recall_score(y_test, pred), 3),
        "flagged=", int(pred.sum()),
        "cm=", confusion_matrix(y_test, pred).tolist(),
    )

print("AP:", round(average_precision_score(y_test, proba), 3))
```

Expected output:

```text
0.20 precision= 0.610 recall= 0.735 flagged= 118 cm= [[756, 46], [26, 72]]
0.35 precision= 0.795 recall= 0.633 flagged= 78  cm= [[786, 16], [36, 62]]
0.50 precision= 0.881 recall= 0.531 flagged= 59  cm= [[795, 7],  [46, 52]]
0.70 precision= 0.952 recall= 0.408 flagged= 42  cm= [[800, 2],  [58, 40]]
AP: 0.745
```

## The operating-point table is the real artifact

| Threshold | Precision | Recall | Review queue size | Operational reading |
| --- | ---: | ---: | ---: | --- |
| 0.20 | 0.610 | 0.735 | 118 cases | Catches more risk, but false alarms are expensive. |
| 0.35 | 0.795 | 0.633 | 78 cases | A practical compromise between misses and reviewer load. |
| 0.50 | 0.881 | 0.531 | 59 cases | Cleaner queue, but noticeably more misses. |
| 0.70 | 0.952 | 0.408 | 42 cases | Very trustworthy alerts, but too many real cases are missed. |

This table is what turns precision and recall from definitions into operating policy. The model is unchanged. The product behavior is not.

## Why 0.35 is the best default recommendation here

In this example, **0.35** is the most defensible starting threshold.

- It improves precision sharply over 0.20: `0.610 → 0.795`.
- It preserves more recall than 0.50: `0.633` versus `0.531`.
- It cuts the review queue from 118 to 78 cases, which is a meaningful operational difference.

That makes 0.35 a good memo answer when the policy is: catch a solid share of true cases without overwhelming the review team.

## Minimal definitions, maximum consequence

- **Precision**: of the alerts we sent, how many were truly positive?
- **Recall**: of the truly positive cases, how many did we catch?

That is enough definition for this chapter. The important part is not memorizing the formulas. It is seeing how both numbers move when you touch the threshold.

This is the narrative shift issue #772 asked for. The chapter should not feel like another generic metric explainer. It should feel like a deployment note.

## Why keep average precision in the memo?

The average precision score here is **0.745**. That is useful as a model-comparison summary because it compresses the full precision-recall curve into one number.

But AP does not choose the threshold for you. It tells you how good the score ranking is overall. The table and confusion matrices still tell you what happens in production.

## What the memo sounds like in plain English

> For suspicious-payment review, threshold 0.35 yields precision 0.795, recall 0.633, and 78 flagged cases. Threshold 0.20 catches more true cases but creates too many false alerts, while thresholds at or above 0.50 reduce queue size at the cost of materially higher misses. For the current operating policy, 0.35 is the default recommendation.

That sentence is much more useful than simply saying “precision and recall trade off.”

## Checklist

- [ ] I build a threshold-by-threshold precision/recall table.
- [ ] I include downstream workload such as queue size.
- [ ] I inspect the confusion matrix, not just the scores.
- [ ] I use AP for model comparison, not as a substitute for threshold policy.

## Wrap-up

Precision and recall become valuable when they drive a threshold choice. The next chapter explains why teams often compress that trade-off into a single F1 number, and why that summary can still hide the decision you care about.

## Answering the Opening Questions

- **When you raise the threshold from 0.20 to 0.70, what are you trading between 118 and 42 items in the review queue?**
  - Raising the threshold makes alerts cleaner but causes more real fraudulent transactions to be missed. In the article's numbers, 0.20 gives `precision 0.610`, `recall 0.735`, queue 118; 0.70 gives `precision 0.952`, `recall 0.408`, queue 42 — revealing a trade-off between review burden and miss risk.
- **Why does this article use 0.35 as the default operating-point candidate and compare it with 0.20 and 0.50?**
  - 0.35 substantially raises precision above 0.20 while sacrificing less recall than 0.50. In practice it yields `precision 0.795`, `recall 0.633`, review queue 78 — a good default candidate for explaining both alert quality and operational burden together.
- **If `AP 0.745` already summarizes model quality, why must you still document the deployment threshold separately?**
  - AP 0.745 summarizes the overall quality of the precision-recall curve, but says nothing about how many items a specific threshold sends to the alert queue. Deployment decisions therefore still require an operational memo with confusion matrices and `flagged` counts for candidates like 0.20, 0.35, 0.50, and 0.70.

<!-- toc:begin -->
## In this series

- [Model Evaluation 101 (1/10): Why Model Evaluation Is Hard](./01-why-evaluation-is-hard.md)
- [Model Evaluation 101 (2/10): Train, Validation, and Test](./02-train-val-test.md)
- [Model Evaluation 101 (3/10): The Limits of Accuracy](./03-limits-of-accuracy.md)
- **Precision and Recall (current)**
- F1 Score (upcoming)
- ROC and AUC (upcoming)
- Calibration (upcoming)
- Cross Validation (upcoming)
- Error Analysis (upcoming)
- Building an Evaluation Report (upcoming)

<!-- toc:end -->

## References

- [scikit-learn — precision_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_score.html)
- [scikit-learn — recall_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.recall_score.html)
- [scikit-learn — average_precision_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html)
- [scikit-learn — precision_recall_curve example](https://scikit-learn.org/stable/auto_examples/model_selection/plot_precision_recall.html)

Tags: ModelEvaluation, Precision, Recall, ConfusionMatrix, scikit-learn
