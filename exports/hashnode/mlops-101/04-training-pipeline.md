
# Model Training Pipeline

> MLOps 101 series (4/10)

<!-- a-grade-intro:begin -->

**Core question**: How do you turn a training script that "behaves differently every run" into a reliable, staged pipeline?

> *A training pipeline splits ingest, preprocess, train, evaluate, and register into explicit stages, so re-runs and caching become possible.*

<!-- a-grade-intro:end -->

## What You Will Learn

- The five stages of a training pipeline
- The meaning of a DAG
- How Airflow, Prefect, and Kubeflow differ
- Retries and caching
- Five common pitfalls

## Why It Matters

Manual training is unreproducible, slow, and a team bottleneck. Pipelines are automatic and auditable.

## Concept at a Glance

```mermaid
flowchart LR
    Ingest["ingest"] --> Prep["preprocess"]
    Prep --> Train["train"]
    Train --> Eval["evaluate"]
    Eval --> Reg["register"]
    Reg --> Deploy["deploy"]
```

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

- [What Is MLOps?](./01-what-is-mlops.md)
- [Experiment Tracking](./02-experiment-tracking.md)
- [Data Versioning](./03-data-versioning.md)
- **Model Training Pipeline (current)**
- Model Deployment (upcoming)
- Model Monitoring (upcoming)
- Data Drift and Model Drift (upcoming)
- Retraining (upcoming)
- Feature Store (upcoming)
- Building a Production ML System (upcoming)
## References

- [Apache Airflow](https://airflow.apache.org/docs/)
- [Prefect](https://docs.prefect.io/)
- [Kubeflow Pipelines](https://www.kubeflow.org/docs/components/pipelines/)
- [Google — TFX](https://www.tensorflow.org/tfx)

Tags: MLOps, Pipeline, Airflow, DAG, DataScience

---

© 2026 YeongseonBooks. All rights reserved.
