---
series: model-evaluation-101
episode: 6
title: "Model Evaluation 101 (6/10): ROC and AUC"
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
  - ROC
  - AUC
  - PRCurve
  - scikit-learn
seo_description: ROC-AUC as a ranking summary, extended all the way to threshold choice, confusion matrix, precision/recall, and simple cost-based deployment judgment
last_reviewed: '2026-05-17'
---

# Model Evaluation 101 (6/10): ROC and AUC

This is the 6th post in the Model Evaluation 101 series.

ROC curves and AUC are useful when you want to compare candidate models before committing to one production threshold. But issue #772 correctly pointed out that the earlier version stopped at `ko/06-roc-and-auc.md:84-115`: it showed `thr[:3]`, AUC, PR-AUC, and one `FPR<=0.05` lookup, then never landed on an actual operating decision.

This rewrite finishes that story. We will use ROC-AUC as a ranking-quality summary, compare it with PR-AUC on the same imbalanced dataset, then turn an `FPR <= 0.05` policy into a concrete threshold, confusion matrix, precision/recall pair, and simple decision cost.


![model evaluation 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/06/06-01-concept-at-a-glance.en.png)
*model evaluation 101 chapter 6 flow overview*

## Questions to Keep in Mind

- What does the ROC curve show?
- What does AUC measure and why is it useful?
- When is AUC misleading?

## This post answers

- Why can ROC-AUC and PR-AUC feel very different on the same dataset?
- How do you turn an `FPR <= 0.05` policy into a threshold and confusion matrix?
- When does a decent AUC still lead to a “not ready to launch” conclusion?

## The final question of this chapter

The real question is not “what is the AUC?” It is this one.

> If AUC looks decent, what do we actually pay at the threshold we are allowed to deploy?

Without that question, ROC-AUC stays a nice-looking summary. With it, the whole 03–06 metrics arc lands in an operational judgment.

## Concept at a glance

ROC and PR both start from score ranking. Deployment does not. Deployment happens at one threshold, so the curve analysis has to come back down to one confusion matrix.

## Code that goes from curve summary to deployment choice

```python
import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split

X, y = make_classification(
    n_samples=5000,
    n_features=12,
    n_informative=5,
    n_redundant=3,
    weights=[0.96, 0.04],
    class_sep=1.2,
    flip_y=0.02,
    random_state=31,
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

fpr, tpr, thresholds = roc_curve(y_test, proba)
print("ROC-AUC:", round(roc_auc_score(y_test, proba), 3))
print("PR-AUC:", round(average_precision_score(y_test, proba), 3))

target_fpr = 0.05
idx = max(i for i, value in enumerate(fpr) if value <= target_fpr)
threshold = thresholds[idx]
pred = (proba >= threshold).astype(int)

cm = confusion_matrix(y_test, pred)
tn, fp, fn, tp = cm.ravel()
precision = precision_score(y_test, pred, zero_division=0)
recall = recall_score(y_test, pred, zero_division=0)
decision_cost = fp * 1 + fn * 10

print("chosen threshold:", round(float(threshold), 3))
print("FPR:", round(fp / (fp + tn), 3))
print("precision:", round(precision, 3))
print("recall:", round(recall, 3))
print("confusion matrix:", cm.tolist())
print("cost (FP=1, FN=10):", decision_cost)
```

Expected output:

```text
ROC-AUC: 0.819
PR-AUC: 0.463
chosen threshold: 0.141
FPR: 0.049
precision: 0.352
recall: 0.507
confusion matrix: [[1355, 70], [37, 38]]
cost (FP=1, FN=10): 440
```

## First conclusion: ROC-AUC and PR-AUC are not telling the same story

The ROC-AUC is **0.819**, which sounds fairly solid. The PR-AUC is only **0.463**. On low-base-rate problems, that difference matters. ROC-AUC summarizes ranking separation between positives and negatives. PR-AUC is far more sensitive to whether the model surfaces positive cases with usable precision.

So “AUC looks good” is still too vague. PR-AUC adds the missing warning that positive-case quality may be weaker than the ROC summary suggests.

## What happens under an explicit FPR budget?

Suppose the operating policy says `FPR <= 0.05`. Under that constraint, the chosen threshold in this example is **0.141**.

At that point, the model produces:

- precision **0.352**
- recall **0.507**
- confusion matrix `[[1355, 70], [37, 38]]`

That means the false-positive budget is respected, but only about half of the true positives are caught. This is the step the previous version was missing: the curve point is now translated into operational impact.

## Compare the threshold candidates side by side

| Threshold | FPR | Precision | Recall | Operational reading |
| --- | ---: | ---: | ---: | --- |
| 0.10 | 0.081 | 0.275 | 0.587 | Better recall, but it violates the 5% FPR policy. |
| 0.141 | 0.049 | 0.352 | 0.507 | Highest recall that still fits the FPR budget. |
| 0.20 | 0.023 | 0.500 | 0.440 | Safer on false positives, but misses more real positives. |

This is the table that turns “the curve looks good” into “these are the actual choices.”

## Add a simple cost frame and the trade-off becomes concrete

The code above uses a deliberately simple cost function: `FP=1`, `FN=10`. At threshold 0.141, the total cost is **440**.

- 70 false positives × 1 = 70
- 37 false negatives × 10 = 370
- total = 440

An interesting detail is that threshold 0.10 can look cheaper overall at **426**, but it fails the policy because `FPR=0.081`. That is the point: **cost minimization and policy compliance are not the same thing**. Production usually needs both.

## So is the model deployable?

Now we can ask the final question.

> Under `FPR <= 0.05`, is recall 0.507 good enough?

If the team requirement is “catch at least 60% of positives,” then the answer is no. The model is not ready under the current policy budget because the best compliant operating point still reaches only about 50.7% recall.

That leads to a much stronger recommendation than “ROC-AUC is 0.819.”

> The model has decent ranking quality, but under the current `FPR <= 0.05` deployment policy it reaches only 0.507 recall. If the recall target is stricter, the team should improve the model or revisit the operating policy before launch.

That is the missing last mile from curve summary to deployment decision.

## Checklist

- [ ] I report ROC-AUC and PR-AUC together.
- [ ] I write down the operating constraint first.
- [ ] I show the confusion matrix at the chosen threshold.
- [ ] I report precision and recall in the same paragraph.
- [ ] I use a simple cost frame when it helps explain the policy trade-off.

## Wrap-up

ROC and AUC are useful because they summarize ranking quality before you lock a threshold. But deployment still happens at one threshold, with one confusion matrix, under one set of constraints. That closes the metrics arc from baselines in episode 03, to threshold trade-offs in episode 04, to F1 summary limits in episode 05, and finally to operating-point selection here.

## Answering the Opening Questions

- **When `ROC-AUC 0.819` and `PR-AUC 0.463` appear together, what should you read differently?**
  - ROC-AUC 0.819 means the model ranks positives above negatives reasonably well, but PR-AUC 0.463 signals that its ability to reliably surface positives in a low base-rate setting is weaker. This is why the article reads beyond the ROC curve impression and moves down to actual threshold selection after examining PR-AUC.
- **Under an `FPR ≤ 0.05` constraint, what happens to the confusion matrix and cost when you pick threshold 0.141?**
  - In the article's example, choosing 0.141 gives `FPR 0.049`, `precision 0.352`, `recall 0.507`, confusion matrix `[[1355, 70], [37, 38]]`. With cost assumptions `FP=1`, `FN=10`, the 70 false positives and 37 false negatives translate to a total cost of 440.
- **Cost alone might favor threshold 0.10, so why must you revisit the policy choice around 0.141?**
  - Threshold 0.10 shows a lower total cost of 426, but its `FPR 0.081` violates the `FPR ≤ 0.05` policy. The article's key point is that cost minimization and policy constraints must be satisfied simultaneously — and if the recall target is 60%, even 0.141 falls short, requiring model improvement or policy redesign.

<!-- toc:begin -->
## In this series

- [Model Evaluation 101 (1/10): Why Model Evaluation Is Hard](./01-why-evaluation-is-hard.md)
- [Model Evaluation 101 (2/10): Train, Validation, and Test](./02-train-val-test.md)
- [Model Evaluation 101 (3/10): The Limits of Accuracy](./03-limits-of-accuracy.md)
- [Model Evaluation 101 (4/10): Precision and Recall](./04-precision-and-recall.md)
- [Model Evaluation 101 (5/10): F1 Score](./05-f1-score.md)
- **ROC and AUC (current)**
- Calibration (upcoming)
- Cross Validation (upcoming)
- Error Analysis (upcoming)
- Building an Evaluation Report (upcoming)

<!-- toc:end -->

## References

- [scikit-learn — roc_curve](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_curve.html)
- [scikit-learn — roc_auc_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html)
- [scikit-learn — average_precision_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html)
- [Wikipedia — ROC curve](https://en.wikipedia.org/wiki/Receiver_operating_characteristic)

Tags: ModelEvaluation, ROC, AUC, PRCurve, scikit-learn
