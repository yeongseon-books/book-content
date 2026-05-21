---
series: machine-learning-101
episode: 10
title: "Machine Learning 101 (10/10): The ML Project Workflow"
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
  - MLWorkflow
  - Pipeline
  - MLOps
  - Beginner
seo_description: From problem framing to data, modeling, evaluation, deployment, and monitoring, the full ML project workflow with sklearn Pipeline in code
last_reviewed: '2026-05-15'
---

# Machine Learning 101 (10/10): The ML Project Workflow

Many ML projects die after the notebook victory lap. The score looked good, the demo worked, and then the real system exposed everything the notebook had hidden: missing reproducibility, scattered preprocessing, undefined monitoring, and no clear path from experiment to deployment.

This is the final post in the Machine Learning 101 series. Here we will connect problem framing, data preparation, modeling, evaluation, deployment, and monitoring into one workflow so the model score becomes only one checkpoint in a larger loop.

## Questions to Keep in Mind

- Why do so many ML projects fail even after promising offline scores?
- Why should problem definition, data, modeling, deployment, and monitoring be treated as one loop?
- How does `Pipeline` protect you from preprocessing leakage?

## Big Picture

![machine learning 101 chapter 10 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/machine-learning-101/10/10-01-concept-at-a-glance.en.png)

*machine learning 101 chapter 10 flow overview*

This picture places The ML Project Workflow inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## Why It Matters

A 0.95 score in a notebook is worth zero if the model never reaches users. Owning the full loop is what creates impact.

## Key Terms

- **Pipeline**: a single object combining preprocessing and model.
- **Reproducibility**: pinned seeds, versions, and data snapshots.
- **Model Card**: official documentation of model metadata.
- **Drift**: shift in input or target distribution.
- **Shadow deploy**: log predictions without acting on them.

## Before/After

**Before**: "Train the model, print the score, done."

**After**: A loop of problem, data, model, evaluation, deployment, and monitoring.

## Hands-on: 5-Step Mini Workflow

### Step 1 — Problem and data

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
X, y = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
```

### Step 2 — Pipeline

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", LogisticRegression(max_iter=2000)),
])
```

### Step 3 — Train and evaluate

```python
pipe.fit(Xtr, ytr)
print("test:", pipe.score(Xte, yte))
```

### Step 4 — Save (reproducibility)

```python
import joblib
joblib.dump(pipe, "model.joblib")
loaded = joblib.load("model.joblib")
print("loaded:", loaded.score(Xte, yte))
```

### Step 5 — Simulate monitoring

```python
import numpy as np
fresh = Xte + np.random.normal(0, 0.1, Xte.shape)
print("drifted:", loaded.score(fresh, yte))
```

**Expected output:** the saved pipeline should reload and reproduce the same test score, while the drifted input score should usually fall. That gap is a simple but useful reminder that deployment success depends on watching the input distribution, not just archiving the model artifact.

## What to Notice in This Code

- `Pipeline` blocks preprocessing leakage at the source.
- `joblib` enables reproducible deployment.
- Even small input noise drops the score, illustrating drift.

## Read the first failure signal this way

- If the production score drops right after deployment, compare live preprocessing with the training pipeline before blaming the model weights.
- If nobody can reproduce the shipped result from a clean environment, the workflow is broken even if the notebook was convincing.
- If monitoring only tracks latency and uptime, you still do not know whether the model is healthy.

## Five Common Mistakes

1. Spreading preprocessing across notebook cells.
2. Skipping seeds and version pinning, killing reproducibility.
3. Deploying without monitoring.
4. Sharing models without a model card.
5. Evaluating on stale data that no longer reflects reality.

## How This Shows Up in Production

Recommendation, fraud detection, and search teams compete on how well they automate the full ML loop, not on a single notebook.

## How a Senior Engineer Thinks

- Problem framing is 60% of the value.
- `Pipeline` decides maintainability.
- Monitoring is the real beginning, not the end.
- Drift always happens.
- Model cards become organizational assets.

## Checklist

- [ ] Wrap everything inside a `Pipeline`.
- [ ] Save and load with `joblib`.
- [ ] Pin seeds and versions.
- [ ] Plan a drift monitoring strategy.

## Practice Problems

1. Add `PCA` to the pipeline and compare scores.
2. Load the saved model from a separate script and re-evaluate.
3. Plot the score curve as input noise increases.

## Wrap-up and Next Steps

Congratulations — you finished Machine Learning 101. Continue with Model Evaluation 101 and MLOps 101 for deeper material.

## Answering the Opening Questions

- **Why do so many ML projects fail even after promising offline scores?**
  - The article treats The ML Project Workflow as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Why should problem definition, data, modeling, deployment, and monitoring be treated as one loop?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **How does `Pipeline` protect you from preprocessing leakage?**
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
- [Machine Learning 101 (9/10): Model Evaluation](./09-model-evaluation.md)
- **The ML Project Workflow (current)**

<!-- toc:end -->

## References

- [scikit-learn — Pipelines](https://scikit-learn.org/stable/modules/compose.html)
- [Google — Rules of ML](https://developers.google.com/machine-learning/guides/rules-of-ml)
- [Model Cards — Mitchell et al. (2019)](https://arxiv.org/abs/1810.03993)
- [Hidden Technical Debt in ML — Sculley et al.](https://papers.nips.cc/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html)

Tags: MachineLearning, MLWorkflow, Pipeline, MLOps, Beginner
