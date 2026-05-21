---
series: model-evaluation-101
episode: 7
title: "Model Evaluation 101 (7/10): Calibration"
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
  - Calibration
  - BrierScore
  - Reliability
  - scikit-learn
seo_description: How to make model probabilities trustworthy with reliability diagrams, Brier score, and Platt or isotonic calibration in code
last_reviewed: '2026-05-15'
---

# Model Evaluation 101 (7/10): Calibration

When a model predicts 0.8, most teams instinctively read that as "about an 80% chance." That interpretation only holds if the model is calibrated. Without that check, the score may still be useful for ranking while being misleading as a probability.

This matters most when probabilities flow directly into pricing, prioritization, or expected-value calculations. A model can have strong AUC and still overstate or understate risk badly enough to damage downstream decisions.

This is post 7 in the Model Evaluation 101 series. In this post, we separate ranking quality from probability quality and walk through reliability curves, Brier score, and post-fit calibration.

## Questions to Keep in Mind

- The definition and purpose of calibration?
- How to read a reliability diagram?
- The meaning of Brier score?

## Big Picture

![model evaluation 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/07/07-01-concept-at-a-glance.en.png)

*model evaluation 101 chapter 7 flow overview*

This picture places Calibration inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## Why It Matters

Systems that multiply probabilities by costs to make decisions need calibration more than AUC.

## Key Terms

- **Calibration**: predicted probability equals observed frequency.
- **Reliability diagram**: predicted vs observed frequency per bin.
- **Brier score**: mean of `(p - y)^2`. Lower is better.
- **Platt scaling**: a sigmoid post-fit.
- **Isotonic regression**: a non-parametric monotonic fit.

## Before/After

**Before**: "proba is 0.9, very confident."

**After**: check the reliability curve, compare Brier scores, switch to isotonic if needed.

## Hands-on: 5 Steps Through Calibration

### Step 1 — Data and model

```python
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
X, y = make_classification(n_samples=3000, weights=[0.7, 0.3], random_state=0)
Xtr, Xte, ytr, yte = train_test_split(X, y, stratify=y, random_state=42)
rf = RandomForestClassifier(n_estimators=100, random_state=0).fit(Xtr, ytr)
proba = rf.predict_proba(Xte)[:, 1]
```

### Step 2 — Reliability curve

```python
from sklearn.calibration import calibration_curve
frac_pos, mean_pred = calibration_curve(yte, proba, n_bins=10)
for mp, fp in zip(mean_pred, frac_pos):
    print(round(mp, 2), round(fp, 2))
```

### Step 3 — Brier score

```python
from sklearn.metrics import brier_score_loss
print("brier:", brier_score_loss(yte, proba))
```

### Step 4 — Platt scaling

```python
from sklearn.calibration import CalibratedClassifierCV
platt = CalibratedClassifierCV(rf, method="sigmoid", cv=5).fit(Xtr, ytr)
print("brier (platt):", brier_score_loss(yte, platt.predict_proba(Xte)[:, 1]))
```

### Step 5 — Isotonic calibration

```python
iso = CalibratedClassifierCV(rf, method="isotonic", cv=5).fit(Xtr, ytr)
print("brier (isotonic):", brier_score_loss(yte, iso.predict_proba(Xte)[:, 1]))
```

**Expected output:** You should see raw probabilities drift away from observed frequencies, then compare whether sigmoid or isotonic calibration improves the Brier score without changing the ranking story very much.

## What to Notice in This Code

- Raw RF probabilities tend to be over- or under-confident.
- Platt scaling is stable on small data.
- Isotonic regression is flexible when data is plentiful.

## Five Common Mistakes

1. Assuming great AUC implies trustworthy probabilities.
2. Fitting calibration on training data.
3. Picking too few or too many bins for the reliability curve.
4. Overfitting isotonic on small samples.
5. Reusing the old threshold after recalibration.

## How This Shows Up in Production

Expected-value bidding (ads, insurance) ties calibrated probabilities directly to revenue.

## How a Senior Engineer Thinks

- AUC and calibration are independent qualities.
- Use a held-out calibration set.
- Brier rolls AUC and calibration into one number.
- Re-tune the threshold after recalibration.
- Recalibrate on drift.

## Checklist

- [ ] I read the reliability diagram.
- [ ] I compare Brier scores.
- [ ] My calibration set is held out.
- [ ] I scheduled recalibration.

## Practice Problems

1. Compare reliability curves of logistic regression and random forest.
2. Compare Brier scores between sigmoid and isotonic calibration.
3. Check whether AUC changes meaningfully after calibration.

## Wrap-up and Next Steps

Calibration is the truth of the probability itself. Next, cross validation tackles the variance of evaluation.

## Answering the Opening Questions

- **The definition and purpose of calibration?**
  - The article treats Calibration as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **How to read a reliability diagram?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **The meaning of Brier score?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Model Evaluation 101 (1/10): Why Model Evaluation Is Hard](./01-why-evaluation-is-hard.md)
- [Model Evaluation 101 (2/10): Train, Validation, and Test](./02-train-val-test.md)
- [Model Evaluation 101 (3/10): The Limits of Accuracy](./03-limits-of-accuracy.md)
- [Model Evaluation 101 (4/10): Precision and Recall](./04-precision-and-recall.md)
- [Model Evaluation 101 (5/10): F1 Score](./05-f1-score.md)
- [Model Evaluation 101 (6/10): ROC and AUC](./06-roc-and-auc.md)
- **Calibration (current)**
- Cross Validation (upcoming)
- Error Analysis (upcoming)
- Building an Evaluation Report (upcoming)

<!-- toc:end -->

## References

- [scikit-learn — Calibration](https://scikit-learn.org/stable/modules/calibration.html)
- [scikit-learn — calibration_curve](https://scikit-learn.org/stable/modules/generated/sklearn.calibration.calibration_curve.html)
- [Wikipedia — Brier score](https://en.wikipedia.org/wiki/Brier_score)
- [Niculescu-Mizil & Caruana 2005](https://www.cs.cornell.edu/~alexn/papers/calibration.icml05.crc.rev3.pdf)

Tags: ModelEvaluation, Calibration, BrierScore, Reliability, scikit-learn
