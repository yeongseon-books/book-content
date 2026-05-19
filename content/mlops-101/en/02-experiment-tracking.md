---
series: mlops-101
episode: 2
title: Experiment Tracking
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - MLOps
  - ExperimentTracking
  - MLflow
  - Reproducibility
  - DataScience
seo_description: Record runs, parameters, metrics, and artifacts so ML experiments become reproducible team memory instead of scattered notebook history.
last_reviewed: '2026-05-15'
---

# Experiment Tracking

Once a team trains a model a few times, memory usually fails before compute does. File names alone do not explain which parameter set won last week, which data version produced the result, or why today's score moved.

The problem gets worse when multiple people are involved. One person leaves metrics in Slack, another stores only the best model, and someone else never records failed runs at all. At that point, reconstructing the past becomes harder than improving the model.

This is post 2 in the MLOps 101 series.

Here, we will treat experiment tracking as the team's short-term memory and focus on what must be recorded so results can be reproduced and compared.

## Questions this article answers

- Why does the same model become hard to reproduce without run tracking?
- Which pieces of metadata must always be captured: params, metrics, artifacts, environment, or data version?
- How should you think about experiments and runs in MLflow?
- Why should failed runs stay visible instead of being discarded?
- What does a team have to standardize before run comparison becomes useful?

> Mental model: an experiment tracker is not a pretty dashboard. It is the shared memory system that stores each training run in one comparable format.

## Why It Matters

Without experiment tracking, training continues but knowledge does not accumulate. When a new score appears, the team cannot tell whether the gain came from the data change, the parameter change, or pure luck.

When every run is recorded, the process becomes an asset in its own right. Failed runs prevent repeated mistakes, and successful runs become promotion candidates that can be defended with evidence.

## See the Flow First

![See the Flow First](https://yeongseon-books.github.io/book-public-assets/assets/mlops-101/02/02-01-see-the-flow-first.en.png)

*See the Flow First*
This is the essence of experiment tracking. Code, parameters, and data version become one run; that run emits metrics, artifacts, and tags; and the team can compare many runs on the same axis.

The key point is not storage by itself, but comparability. The run table matters only when different runs can be read side by side with consistent names and metadata.

## Key Terms

- **Experiment**: a named container for related runs.
- **Run**: a single training execution.
- **Param**: a fixed input value.
- **Metric**: a measured outcome.
- **Artifact**: a file such as a model, plot, or log.

## Before/After

**Before**: chaos under filenames like `v3_final2.pkl`.

**After**: a runs table and an MLflow UI for comparison.

## Hands-on: 5 Steps Through MLflow

### Step 1 — Bootstrap the tracker

```python
# pip install mlflow
import mlflow
mlflow.set_tracking_uri("file:./mlruns")
mlflow.set_experiment("demo")
```

### Step 2 — Record a run

```python
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
X, y = make_classification(n_samples=500, random_state=0)

with mlflow.start_run():
    C = 1.0
    mlflow.log_param("C", C)
    m = LogisticRegression(C=C, max_iter=1000).fit(X, y)
    mlflow.log_metric("acc", m.score(X, y))
```

### Step 3 — Log the model artifact

```python
import pickle, os
os.makedirs("art", exist_ok=True)
with mlflow.start_run():
    m = LogisticRegression().fit(X, y)
    with open("art/model.pkl", "wb") as f:
        pickle.dump(m, f)
    mlflow.log_artifact("art/model.pkl")
```

### Step 4 — Sweep parameters

```python
for C in [0.1, 1.0, 10.0]:
    with mlflow.start_run():
        mlflow.log_param("C", C)
        m = LogisticRegression(C=C, max_iter=1000).fit(X, y)
        mlflow.log_metric("acc", m.score(X, y))
```

### Step 5 — Compare via the API

```python
client = mlflow.tracking.MlflowClient()
exp = client.get_experiment_by_name("demo")
runs = client.search_runs(exp.experiment_id, order_by=["metrics.acc DESC"])
for r in runs[:3]:
    print(r.data.params, r.data.metrics)
```

## What to Notice in This Code

- A `with` block is the run boundary.
- Params and metrics are key-value pairs.
- Artifacts are stored as files as is.

## Five Common Mistakes

1. Recording only successful runs.
2. Forgetting the data version.
3. Inconsistent param and metric names.
4. Using only local mlruns and losing shareability.
5. Choosing the winner manually instead of by comparison.

## How This Shows Up in Production

Hyperparameter sweeps and weekly reviews use MLflow or W&B as shared memory.

## How a Senior Engineer Thinks

- Record every run, including failures.
- Treat data version as a param.
- Standardize metric keys across the team.
- Default to a remote tracking server.
- Run metadata is the entry point of debugging.

## Checklist

- [ ] All training is captured as runs.
- [ ] Data and code versions are included.
- [ ] A shared tracking server is used.
- [ ] Decisions come from the comparison view.

## Practice Problems

1. Sweep three parameter combinations and print the top run.
2. Add the data hash as a param.
3. Use run tags to mark experiment intent.

## Wrap-up and Next Steps

Experiment tracking is the team's short-term memory. Next, data versioning provides the long-term memory.

<!-- toc:begin -->
- [What Is MLOps?](./01-what-is-mlops.md)
- **Experiment Tracking (current)**
- Data Versioning (upcoming)
- Model Training Pipeline (upcoming)
- Model Deployment (upcoming)
- Model Monitoring (upcoming)
- Data Drift and Model Drift (upcoming)
- Retraining (upcoming)
- Feature Store (upcoming)
- Building a Production ML System (upcoming)
<!-- toc:end -->

## References

- [MLflow — Tracking](https://mlflow.org/docs/latest/tracking.html)
- [Weights & Biases](https://docs.wandb.ai/)
- [Neptune.ai — Comparison](https://neptune.ai/blog/best-ml-experiment-tracking-tools)
- [Google — Reproducible ML](https://cloud.google.com/architecture/ml-on-gcp-best-practices)

Tags: MLOps, ExperimentTracking, MLflow, Reproducibility, DataScience
