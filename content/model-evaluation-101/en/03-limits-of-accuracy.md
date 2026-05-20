---
series: model-evaluation-101
episode: 3
title: "Model Evaluation 101 (3/10): The Limits of Accuracy"
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
  - Accuracy
  - ImbalancedData
  - BaselineModel
  - scikit-learn
seo_description: How to read accuracy only after checking base rate, dummy baseline, minority recall, and balanced accuracy on imbalanced classification problems
last_reviewed: '2026-05-17'
---

# Model Evaluation 101 (3/10): The Limits of Accuracy

This is post 3 in the Model Evaluation 101 series.

Accuracy is easy to compute and easy to explain, which is exactly why teams trust it too early. Issue #772 called out that this chapter explained the limitation of accuracy but did not walk the reader through the real operator sequence: base rate → dummy baseline → minority recall → balanced accuracy → final review.

That is the structure of this rewrite. We will treat accuracy as the **last summary number**, not the first verdict. In other words, we are fixing the weakness identified in `ko/03-limits-of-accuracy.md:64-69,115-131`: the article now moves in the order a reviewer would actually use when deciding whether accuracy is still safe to report.

## Questions to Keep in Mind

- What boundary should you inspect first when applying The Limits of Accuracy?
- Which signal should the example or diagram make visible for The Limits of Accuracy?
- What failure should be prevented first when The Limits of Accuracy reaches a real system?

## Big Picture

![model evaluation 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/03/03-01-concept-at-a-glance.en.png)

*model evaluation 101 chapter 3 flow overview*

This picture places The Limits of Accuracy inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of The Limits of Accuracy is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## This post answers

- When is a small accuracy lift over a dummy baseline still operationally weak?
- How do minority recall and balanced accuracy overturn the headline number?
- How do you decide whether accuracy deserves a place in the final memo at all?

## The review order for accuracy

When class imbalance is present, accuracy should be read in this order.

1. **Check the base rate**: how rare is the positive class?
2. **Compare to a dummy baseline**: how high can accuracy get without learning anything?
3. **Inspect minority recall**: how many important positives are still being missed?
4. **Add balanced accuracy**: what happens when each class gets an equal vote?
5. **Decide whether accuracy is reportable**: only now is accuracy allowed back into the summary.

If you reverse that order, `acc 96%` sounds impressive. If you keep the order, you can distinguish a real lift from majority-class comfort.

## Concept at a glance

The point is not that accuracy is useless. The point is that imbalanced data changes the conditions under which accuracy is honest.

## One diagnostic script instead of five disconnected snippets

The following script runs the full review sequence in one place.

```python
from sklearn.datasets import make_classification
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    recall_score,
)
from sklearn.model_selection import train_test_split

X, y = make_classification(
    n_samples=5000,
    n_features=20,
    n_informative=5,
    n_redundant=2,
    weights=[0.96, 0.04],
    class_sep=1.1,
    flip_y=0.015,
    random_state=42,
)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    stratify=y,
    random_state=42,
)

dummy = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
model = LogisticRegression(max_iter=4000).fit(X_train, y_train)
pred = model.predict(X_test)

print("base rate:", round(y.mean(), 4))
print("dummy accuracy:", round(dummy.score(X_test, y_test), 4))
print("model accuracy:", round(accuracy_score(y_test, pred), 4))
print("minority recall:", round(recall_score(y_test, pred), 4))
print("balanced accuracy:", round(balanced_accuracy_score(y_test, pred), 4))
print("confusion matrix:\n", confusion_matrix(y_test, pred))
print(classification_report(y_test, pred, digits=4))
```

Expected interpretation:

```text
base rate: 0.0468
dummy accuracy: 0.9536
model accuracy: 0.9608
minority recall: 0.1897
balanced accuracy: 0.5940
confusion matrix:
[[1190    2]
 [  47   11]]
```

Accuracy alone looks strong at 96.08%. The moment you line it up next to the dummy baseline at 95.36%, the story changes. The model gained only **0.72 percentage points of accuracy**, while still missing 47 of 58 positive cases.

## Step 1 — Base rate changes the burden of proof

The positive class appears only 4.68% of the time. That means accuracy is heavily subsidized by the majority class before the model does anything smart.

This is why base rate belongs at the top of the review. Once you know the problem is not 50:50, a high accuracy number stops being self-explanatory.

## Step 2 — The dummy baseline reveals how cheap high accuracy can be

`DummyClassifier(strategy="most_frequent")` predicts the majority class every time. On this dataset it already reaches **95.36% accuracy**. That one number keeps the team from celebrating the wrong thing.

- Bad reading: `96% accuracy, looks production-ready.`
- Better reading: `The baseline is already 95.36%, so the accuracy gain is small. Show me what happened to the minority class.`

Accuracy without a dummy comparison is rarely interpretable on skewed data.

## Step 3 — Minority recall is the operational core

The minority recall is **0.1897**. In plain terms, the model catches fewer than 19% of the positives. That means about 81 out of every 100 important cases are still missed.

This is the failure mode accuracy hides. The confusion matrix makes it explicit: 11 true positives, 47 false negatives. If the application is fraud, medical screening, or outage detection, that row matters more than the headline accuracy.

## Step 4 — Balanced accuracy gives each class an equal vote

Balanced accuracy is **0.5940**, which is dramatically lower than the raw accuracy of 0.9608. That gap is the point. The majority class is handled well, the minority class is handled poorly, and balanced accuracy refuses to let one class hide the other.

This is the missing decision order flagged in issue #772. You do not accept accuracy at face value until minority recall and balanced accuracy have had a chance to challenge it.

## Step 5 — Is accuracy still reportable?

Only now can you ask the final review question.

> Is this a real performance lift, or just majority-class comfort?

For this example, the answer is closer to the second one. Accuracy is not useless, but it must be reported with conditions.

- Show the improvement over the dummy baseline.
- Put minority recall in the same paragraph.
- Add balanced accuracy next to raw accuracy.
- If misses are expensive, do not use accuracy as the lead metric.

In this setting, `minority recall=0.1897` and `balanced accuracy=0.5940` deserve more attention than `accuracy=0.9608`.

## A production-style review sentence

This is the kind of sentence you want in an evaluation memo.

> On a problem with a 4.68% positive rate, the model reached 96.08% accuracy versus a 95.36% dummy baseline. However, minority recall was only 18.97% and balanced accuracy was 59.40%, so the result is better described as a small baseline lift with a serious positive-case miss problem.

That is a much safer conclusion than simply reporting `96% accuracy`.

## Checklist

- [ ] I check the base rate first.
- [ ] I compare accuracy to a dummy baseline.
- [ ] I report minority recall separately.
- [ ] I add balanced accuracy.
- [ ] I decide whether accuracy deserves a headline role only after those checks.

## Wrap-up

Accuracy is not a bad metric. It is a metric with an order of operations. On imbalanced data, base rate, dummy baseline, minority recall, and balanced accuracy have to speak first. Next, we continue that review flow by turning precision and recall into an explicit threshold decision memo.

## Answering the Opening Questions

- **What boundary should you inspect first when applying The Limits of Accuracy?**
  - The article treats The Limits of Accuracy as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for The Limits of Accuracy?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when The Limits of Accuracy reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Model Evaluation 101 (1/10): Why Model Evaluation Is Hard](./01-why-evaluation-is-hard.md)
- [Model Evaluation 101 (2/10): Train, Validation, and Test](./02-train-val-test.md)
- **The Limits of Accuracy (current)**
- Precision and Recall (upcoming)
- F1 Score (upcoming)
- ROC and AUC (upcoming)
- Calibration (upcoming)
- Cross Validation (upcoming)
- Error Analysis (upcoming)
- Building an Evaluation Report (upcoming)

<!-- toc:end -->

## References

- [scikit-learn — DummyClassifier](https://scikit-learn.org/stable/modules/generated/sklearn.dummy.DummyClassifier.html)
- [scikit-learn — accuracy_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.accuracy_score.html)
- [scikit-learn — balanced_accuracy_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.balanced_accuracy_score.html)
- [Wikipedia — Accuracy paradox](https://en.wikipedia.org/wiki/Accuracy_paradox)

Tags: ModelEvaluation, Accuracy, ImbalancedData, BaselineModel, scikit-learn
