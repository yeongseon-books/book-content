---
series: mlops-101
episode: 4
title: "MLOps 101 (4/10): Model Training Pipeline"
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
  - Pipeline
  - Airflow
  - DAG
  - DataScience
seo_description: Break ML training into explicit ingest, preprocess, train, evaluate, and register stages so re-runs, retries, and recovery become manageable.
last_reviewed: '2026-05-15'
---

# MLOps 101 (4/10): Model Training Pipeline

Scheduling one `train.py` file does not automatically give you an operable training system. When ingest, preprocessing, training, evaluation, and registration are fused into one script, failures are hard to localize and partial re-runs become expensive.

The more the training process depends on manual steps, the faster reproducibility and recovery speed fall apart. In MLOps, a pipeline is not a convenience feature. It is the structure that turns training into explicit, repeatable stages.

This is post 4 in the MLOps 101 series.

Here, we will distinguish a training pipeline from simple script automation and show why stage boundaries and a DAG matter.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Model Training Pipeline?
- Which signal should the example or diagram make visible for Model Training Pipeline?
- What failure should be prevented first when Model Training Pipeline reaches a real system?

## Big Picture

![mlops 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/mlops-101/04/04-01-see-the-flow-first.en.png)

*mlops 101 chapter 4 flow overview*

This picture places Model Training Pipeline inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> A training pipeline is not a large script with a scheduler attached. It is a DAG of small stages with clear inputs and outputs, designed so failed stages do not force the whole run to restart.

## Questions this article answers

- Why split a single training script into multiple pipeline stages?
- How is a DAG different from a plain execution order?
- Where do Airflow, Prefect, and Kubeflow fit into the picture?
- Why do retries and caching matter so much in training pipelines?
- Which design mistakes force the whole pipeline to re-run unnecessarily?

> Mental model: a training pipeline is not a large script with a scheduler attached. It is a DAG of small stages with clear inputs and outputs, designed to shrink the re-run scope.

## Why It Matters

Manual training is slow, hard to reproduce, and difficult to debug. When a nightly training job fails and the whole process has to restart from the beginning, the operating cost rises quickly.

When stages are split cleanly, the team can narrow the failure immediately and rerun only the part whose inputs changed. A pipeline is the mechanism that raises both observability and recoverability for training.

## See the Flow First

The most important part of this diagram is not the stage names, but the boundaries between them. Ingest, preprocess, train, evaluate, and register have to be separate if the team wants partial re-runs and faster root-cause analysis.

The goal of a training pipeline is not fancy scheduling. It is clear stage boundaries.

## Key Terms

- **Stage**: a unit of inputs, command, and outputs.
- **DAG**: a directed acyclic graph encoding dependencies.
- **Idempotent**: same input always produces same output.
- **Caching**: only changed stages re-run.
- **Backfill**: re-running historical dates.

## Before/After

**Before**: `train.py` triggered by cron and crossed fingers.

**After**: a DAG with retries, alerts, and caching.

## Hands-on: 5 Steps Through a Mini Pipeline

### Step 1 — Stage functions

```python
import pandas as pd

def ingest():
    df = pd.DataFrame({"x": range(50), "y": [i % 2 for i in range(50)]})
    df.to_csv("/tmp/raw.csv", index=False)
    return "/tmp/raw.csv"
```

### Step 2 — Preprocess

```python
def preprocess(path):
    df = pd.read_csv(path)
    df["x"] = (df["x"] - df["x"].mean()) / df["x"].std()
    out = "/tmp/clean.csv"
    df.to_csv(out, index=False)
    return out
```

### Step 3 — Train

```python
import pickle
from sklearn.linear_model import LogisticRegression

def train(path):
    df = pd.read_csv(path)
    m = LogisticRegression().fit(df[["x"]], df["y"])
    with open("/tmp/model.pkl", "wb") as f:
        pickle.dump(m, f)
    return "/tmp/model.pkl"
```

### Step 4 — Evaluate

```python
def evaluate(path, model_path):
    df = pd.read_csv(path)
    with open(model_path, "rb") as f:
        m = pickle.load(f)
    return float(m.score(df[["x"]], df["y"]))
```

### Step 5 — Orchestrate

```python
def run():
    raw = ingest()
    clean = preprocess(raw)
    model = train(clean)
    metric = evaluate(clean, model)
    print({"metric": metric, "model": model})

run()
```

## What to Notice in This Code

- Each stage is a function plus file I/O.
- The orchestrator only enforces order.
- Airflow wraps these functions as Operators.

## Five Common Mistakes

1. Stages are too large, so a failure forces re-running everything.
2. Stages are not idempotent because random seeds are unset.
3. Output paths are fixed and parallel runs collide.
4. No retry policy.
5. No alerts, leading to silent failures.

## How This Shows Up in Production

A nightly Airflow DAG runs data, train, register. The weekly report is just the last stage of the same DAG.

## How a Senior Engineer Thinks

- Small stages make debugging easy.
- Fixed seeds make stages idempotent.
- Output paths include date or run id.
- Retries and alerts are defaults, not extras.
- The DAG diagram is the documentation.

## Checklist

- [ ] Stages are small and focused.
- [ ] Each stage declares inputs and outputs.
- [ ] Retries and alerts are configured.
- [ ] A DAG diagram exists.

## Practice Problems

1. Convert the example pipeline into an Airflow DAG (pseudocode).
2. Cache only the preprocess stage.
3. Add Slack alerts on failure (pseudocode).

## Wrap-up and Next Steps

Pipelines provide repeatability. Next, model deployment turns trained artifacts into live services.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Model Training Pipeline?**
  - The article treats Model Training Pipeline as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Model Training Pipeline?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Model Training Pipeline reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [MLOps 101 (1/10): What Is MLOps?](./01-what-is-mlops.md)
- [MLOps 101 (2/10): Experiment Tracking](./02-experiment-tracking.md)
- [MLOps 101 (3/10): Data Versioning](./03-data-versioning.md)
- **Model Training Pipeline (current)**
- Model Deployment (upcoming)
- Model Monitoring (upcoming)
- Data Drift and Model Drift (upcoming)
- Retraining (upcoming)
- Feature Store (upcoming)
- Building a Production ML System (upcoming)

<!-- toc:end -->

## References

- [Apache Airflow](https://airflow.apache.org/docs/)
- [Prefect](https://docs.prefect.io/)
- [Kubeflow Pipelines](https://www.kubeflow.org/docs/components/pipelines/)
- [Google — TFX](https://www.tensorflow.org/tfx)

Tags: MLOps, Pipeline, Airflow, DAG, DataScience
