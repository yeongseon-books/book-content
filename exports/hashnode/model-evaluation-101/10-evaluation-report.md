
# Building an Evaluation Report

> Model Evaluation 101 series (10/10)

<!-- a-grade-intro:begin -->

**Core question**: When you ship a model, what belongs in a one-page evaluation report?

> *A good report gathers the five elements — data, metrics, threshold, slices, and reproducibility — in a single place.*

<!-- a-grade-intro:end -->

## What You Will Learn

- The five sections of an evaluation report
- How it differs from a Model Card
- Reproducibility metadata
- Patterns for automatic generation
- Five common pitfalls

## Why It Matters

Reviews, audits, and post-incident analyses all read the same report. A consistent format speeds up the team.

## Concept at a Glance

```mermaid
flowchart LR
    Data["data section"] --> Report
    Metric["metrics + threshold"] --> Report
    Slice["slice scores"] --> Report
    Repro["reproducibility"] --> Report
    Risk["known risks"] --> Report
```

## Key Terms

- **Model Card**: a document describing a model's intent and limits.
- **Datasheet**: a description of a dataset's origin and bias.
- **Operating threshold**: the production decision boundary.
- **Reproducibility hash**: identifiers for code and data versions.
- **Risk register**: known failure modes.

## Before/After

**Before**: a single Slack message — "acc 0.92, ship."

**After**: a five-section structured report, generated automatically.

## Hands-on: 5 Steps to Build a Report

### Step 1 — Collect metrics

```python
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, roc_auc_score, brier_score_loss
X, y = make_classification(n_samples=3000, weights=[0.7, 0.3], random_state=0)
Xtr, Xte, ytr, yte = train_test_split(X, y, stratify=y, random_state=42)
m = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
proba = m.predict_proba(Xte)[:, 1]
pred = (proba >= 0.5).astype(int)
metrics = {
    "f1_macro": f1_score(yte, pred, average="macro"),
    "auc_roc": roc_auc_score(yte, proba),
    "brier": brier_score_loss(yte, proba),
}
```

### Step 2 — Slice scores

```python
slice_mask = Xte[:, 0] > 0
slices = {
    "slice_pos": f1_score(yte[slice_mask], pred[slice_mask]),
    "slice_neg": f1_score(yte[~slice_mask], pred[~slice_mask]),
}
```

### Step 3 — Metadata

```python
import hashlib, sys, sklearn
meta = {
    "python": sys.version.split()[0],
    "sklearn": sklearn.__version__,
    "data_hash": hashlib.sha1(X.tobytes()).hexdigest()[:10],
    "threshold": 0.5,
}
```

### Step 4 — Serialize the report

```python
import json
report = {"metrics": metrics, "slices": slices, "meta": meta,
          "risks": ["minor calibration drift", "slice_neg lower F1"]}
print(json.dumps(report, indent=2))
```

### Step 5 — Render to Markdown

```python
def to_md(rep):
    lines = ["# Evaluation Report", "## Metrics"]
    for k, v in rep["metrics"].items():
        lines.append(f"- {k}: {round(v, 3)}")
    lines.append("## Slices")
    for k, v in rep["slices"].items():
        lines.append(f"- {k}: {round(v, 3)}")
    lines.append("## Meta")
    for k, v in rep["meta"].items():
        lines.append(f"- {k}: {v}")
    return "\n".join(lines)

print(to_md(report))
```

## What to Notice in This Code

- Generate JSON first, render Markdown second.
- The data hash is the backbone of reproducibility.
- A documented threshold prevents interpretation drift.

## Five Common Mistakes

1. Forgetting to record the threshold.
2. Skipping slice scores.
3. Omitting version info.
4. Leaving the risk section blank.
5. Writing the report by hand, killing reproducibility.

## How This Shows Up in Production

ML release gates and monitoring alerts use the evaluation report as the canonical reference.

## How a Senior Engineer Thinks

- A report is a build artifact.
- Model Card and report are separate documents.
- Every number cites its data and threshold.
- The risk section matters most.
- Regenerate periodically to track drift.

## Checklist

- [ ] Metrics are reported with their threshold.
- [ ] Slice scores are included.
- [ ] Version and hash metadata is recorded.
- [ ] Known risks are listed.

## Practice Problems

1. Fill the template with your team's most recent model.
2. Produce two reports for the same model at two different thresholds.
3. Wire the report generator into your CI pipeline.

## Wrap-up and Next Steps

Across ten episodes you have a vocabulary for evaluation and the realistic traps. From here, MLOps and deeper error analysis are the natural next series.

- [Why Model Evaluation Is Hard](./01-why-evaluation-is-hard.md)
- [Train, Validation, and Test](./02-train-val-test.md)
- [The Limits of Accuracy](./03-limits-of-accuracy.md)
- [Precision and Recall](./04-precision-and-recall.md)
- [F1 Score](./05-f1-score.md)
- [ROC and AUC](./06-roc-and-auc.md)
- [Calibration](./07-calibration.md)
- [Cross Validation](./08-cross-validation.md)
- [Error Analysis](./09-error-analysis.md)
- **Building an Evaluation Report (current)**
## References

- [Google — Model Cards](https://modelcards.withgoogle.com/about)
- [Datasheets for Datasets](https://arxiv.org/abs/1803.09010)
- [scikit-learn — Model evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [MLOps — Production ML guide](https://ml-ops.org/)

Tags: ModelEvaluation, Reporting, ModelCard, Reproducibility, scikit-learn

---

© 2026 YeongseonBooks. All rights reserved.
