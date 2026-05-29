---
series: mlops-101
episode: 2
title: "MLOps 101 (2/10): Experiment Tracking"
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

# MLOps 101 (2/10): Experiment Tracking

Once a team trains a model a few times, memory usually fails before compute does. File names alone do not explain which parameter set won last week, which data version produced the result, or why today's score moved.

The problem gets worse when multiple people are involved. One person leaves metrics in Slack, another stores only the best model, and someone else never records failed runs at all. At that point, reconstructing the past becomes harder than improving the model.

This is the 2nd post in the MLOps 101 series.

Here, we will treat experiment tracking as the team's short-term memory and focus on what must be recorded so results can be reproduced and compared.


![mlops 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/mlops-101/02/02-01-see-the-flow-first.en.png)
*mlops 101 chapter 2 flow overview*
> An experiment tracker is not a pretty dashboard. It is the shared memory system that stores each training run in one comparable format so the team never repeats the same mistake twice.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Experiment Tracking?
- Which signal should the example or diagram make visible for Experiment Tracking?
- What failure should be prevented first when Experiment Tracking reaches a real system?

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

## MLflow Tracking Patterns in Practice

Experiment tracking does not end at "record"; it must reach "compare." For that, key names and experiment scope need standardization first.

### Recommended Recording Schema

| Category | Required keys (examples) | Purpose |
|---|---|---|
| Param | `model_type`, `learning_rate`, `seed`, `data_version` | Fix input conditions |
| Metric | `val_auc`, `val_f1`, `train_time_sec` | Compare performance and cost |
| Tag | `owner`, `ticket`, `purpose` | Link organizational context |
| Artifact | `model.pkl`, `confusion_matrix.png`, `feature_importance.csv` | Enable result reuse |

Standardizing keys makes a visible difference from the next quarter onward. Even when team members change, the same experiment table remains readable, and model reviews shift from "gut feeling" to "evidence-based."

### Experiment Comparison Code

```python
import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient(tracking_uri="file:./mlruns")
exp = client.get_experiment_by_name("demo-full")
runs = client.search_runs(
    experiment_ids=[exp.experiment_id],
    order_by=["metrics.val_auc DESC"],
)

print("top runs")
for r in runs[:5]:
    print({
        "run_id": r.info.run_id,
        "val_auc": r.data.metrics.get("val_auc"),
        "lr": r.data.params.get("learning_rate"),
        "data": r.data.params.get("data_version"),
    })
```

This comparison code is what makes retrospective meetings productive. "Which experiment won and why?" becomes a quick lookup instead of a memory exercise.

### Run Comparison Table Template

Use this format for weekly model reviews to make promotion decisions explicit.

| run_id | data_version | val_auc | val_f1 | train_time_sec | Promotion candidate |
|---|---|---:|---:|---:|---|
| a1b2c3 | 2026-05-10 | 0.861 | 0.742 | 388 | Candidate |
| d4e5f6 | 2026-05-10 | 0.854 | 0.739 | 220 | Hold |
| g7h8i9 | 2026-05-03 | 0.847 | 0.733 | 190 | Rejected |

Promoting a model based on score alone ignores training cost, data recency, and stability. Including all three in the review table reduces production regret.

## Reproducible Experiment Wrapper

```python
import os
import subprocess
import mlflow

def run_experiment(cfg_path: str, data_version: str) -> None:
    mlflow.set_experiment("fraud-lr")
    with mlflow.start_run():
        mlflow.log_param("config", cfg_path)
        mlflow.log_param("data_version", data_version)
        mlflow.log_param("git_sha", os.getenv("GIT_SHA", "unknown"))

        subprocess.run(["python", "train.py", "--config", cfg_path], check=True)
        subprocess.run(["python", "evaluate.py", "--output", "metrics.json"], check=True)

        mlflow.log_artifact("metrics.json")
        mlflow.log_artifact("model.pkl")
```

The purpose of this wrapper is not to complicate the training script. It forces metadata at the experiment boundary so reproducibility gaps are caught early.

## Operating Conventions

- Never delete failed runs.
- Runs missing `data_version` and `git_sha` are excluded from promotion candidates.
- Promotion reviews include variance across the last 3 runs.
- Define a review cadence and document the model selection process.

With these conventions, experiment tracking evolves from a log store into an operational decision system.

## MLflow Autolog and Nested Runs

Manually calling `log_param` and `log_metric` is precise but repetitive. MLflow's `autolog` reduces this burden.

### Using autolog

```python
import mlflow
mlflow.autolog()

from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

X, y = make_classification(n_samples=2000, n_features=20, random_state=42)
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2)

with mlflow.start_run():
    clf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=0)
    clf.fit(X_train, y_train)
    # autolog records params, metrics, and model automatically
```

With `autolog` enabled, calling `fit()` captures hyperparameters, training metrics, and the model artifact in one shot. However, data version and team tags are not automatic—those still require manual addition.

### Structuring Sweeps with Nested Runs

When all sweep runs sit at the same level, it becomes hard to tell which sweep produced which run later. Nested runs add parent-child structure.

```python
import mlflow
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification

X, y = make_classification(n_samples=1000, random_state=42)

with mlflow.start_run(run_name="sweep-2026-05-12"):
    mlflow.set_tag("sweep_type", "grid")
    mlflow.set_tag("owner", "ml-team")

    for C in [0.01, 0.1, 1.0, 10.0]:
        for solver in ["lbfgs", "liblinear"]:
            with mlflow.start_run(run_name=f"C={C}-{solver}", nested=True):
                mlflow.log_param("C", C)
                mlflow.log_param("solver", solver)
                m = LogisticRegression(C=C, solver=solver, max_iter=1000).fit(X, y)
                mlflow.log_metric("acc", m.score(X, y))
```

The parent run holds sweep metadata (date, purpose, owner); child runs hold individual combination results. This structure enables both sweep-level and run-level comparison.

### Remote Tracking Server Setup

Local `mlruns` is quick to start but unsuitable for team sharing. A remote server gives everyone the same experiment table.

```bash
# Start tracking server (PostgreSQL backend)
mlflow server \
    --backend-store-uri postgresql://user:pass@db:5432/mlflow \
    --default-artifact-root s3://mlflow-artifacts/ \
    --host 0.0.0.0 \
    --port 5000
```

```python
# Point client code to the remote server
import mlflow
mlflow.set_tracking_uri("http://mlflow-server:5000")
```

Defaulting to a remote server eliminates the "experiments trapped in one laptop" problem. Using PostgreSQL as the backend also improves search and filter performance.

### Experiment Management Policy

| Item | Recommended policy | Impact of violation |
|---|---|---|
| Key name standard | Defined in team wiki, checked during PR review | Comparison view becomes meaningless |
| Data version required | CI fails if `data_version` param is missing | Reproduction impossible |
| Failed run preservation | No deletion, attach `status=failed` tag | Exploration history lost |
| Promotion criteria | Average val_auc over last 3 runs > threshold | Accidental peak deployed |
| Cleanup cadence | Archive runs unreferenced for 90+ days | Storage cost increase |

When this policy is part of team onboarding docs, new members record experiments consistently from day one.

### MLflow UI Tips

Launch the MLflow UI with `mlflow ui`. Default port is 5000.

```bash
mlflow ui --port 5000
# Open http://localhost:5000 in browser
```

Three most-used features:

1. **Compare view**: Select multiple runs and click Compare to see params and metrics side by side.
2. **Chart view**: Place metrics on x/y axes for scatter plots. Visually identifies which parameter combinations affect performance.
3. **Search filter**: Use queries like `params.C > 0.5 and metrics.val_auc > 0.85` to narrow runs of interest.

### Exporting Experiment Data

When sharing results in team meetings or documentation, exporting to a DataFrame is practical.

```python
import mlflow
import pandas as pd

client = mlflow.tracking.MlflowClient()
exp = client.get_experiment_by_name("demo-full")
runs = client.search_runs(
    experiment_ids=[exp.experiment_id],
    order_by=["metrics.val_auc DESC"],
    max_results=50,
)

rows = []
for r in runs:
    rows.append({
        "run_id": r.info.run_id[:8],
        "C": r.data.params.get("C"),
        "solver": r.data.params.get("solver"),
        "val_auc": r.data.metrics.get("val_auc"),
        "data_version": r.data.params.get("data_version"),
    })

df = pd.DataFrame(rows)
df.to_csv("experiment_report.csv", index=False)
print(df.head(10))
```

Sharing this CSV on a team wiki or Slack allows experiment review even without MLflow access.

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

## Answering the Opening Questions

- **Why is reproducing even the same model difficult without experiment management?**
  - Even the same logistic regression becomes unreproducible when run conditions like `C`, `max_iter`, `data_version`, and `git_sha` are missing. Without experiment tracking, only `model.pkl` and a single number remain, and the axes to explain why that metric occurred disappear.
- **Which of parameters, metrics, artifacts, and environment must you always record?**
  - The article bundled param, metric, and artifact in the same run as the minimum unit, adding `data_version` and `git_sha`. Because the MLflow example saved `model.pkl`, `acc.png`, and `val_acc` together, subsequent run comparison and promotion decisions became possible.
- **How should you understand the relationship between experiment and run in MLflow?**
  - An experiment is a container grouping related experiments like `fraud-detection-baseline`; a run is one actual training execution inside it. So nesting sweep runs under a parent or sorting multiple runs by `metrics.val_auc DESC` for comparison flows naturally.
<!-- toc:begin -->
## In this series

- [MLOps 101 (1/10): What Is MLOps?](./01-what-is-mlops.md)
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
