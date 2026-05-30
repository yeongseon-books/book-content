---
series: mlops-101
episode: 3
title: "MLOps 101 (3/10): Data Versioning"
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
  - DVC
  - DataVersioning
  - Reproducibility
  - DataScience
seo_description: Version data with pointers, hashes, and remote storage so ML pipelines can reproduce the same inputs across time and across teammates.
last_reviewed: '2026-05-15'
---

# MLOps 101 (3/10): Data Versioning

Teams usually remember to keep code in git and sometimes remember to save model files. The largest input of all—the data—is often the least controlled. When yesterday's training run works and today's result shifts unexpectedly, this is where the investigation usually begins.

This is the 3rd post in the MLOps 101 series.

The same code with different data produces a different model. That means MLOps without data versioning is only half built. You might be able to reproduce the code path, but you still cannot reproduce the outcome.

Here, we will treat data versioning not as file backup, but as a reproducibility contract that lets the whole team pull the same inputs in the same state.


![mlops 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/mlops-101/03/03-01-see-the-flow-first.en.png)
*mlops 101 chapter 3 flow overview*
> Data versioning is not a tool that forces large files into git. It is a pointer-plus-storage system that identifies the exact input state so the whole team can pull the same data in the same moment in time.

## Questions to Keep in Mind

- Why can code versioning alone never reproduce an ML result?
- How should you think about DVC versus git-LFS?
- How do you keep large data files outside git without losing version consistency?

## Why It Matters

One of the most common mistakes in ML systems is assuming the model came from the code. In practice, the model comes from the combination of code and data. When the input changes, the result changes, even if the repository did not. Even when data stays the same, a different preprocessing order yields a different outcome.

That is why experiment tracking alone is not enough. A high metric becomes hard to explain, and an older model becomes impossible to rebuild, if the training data state was never preserved.

### Feature Store Architecture

Feature Store is a concept that travels alongside data versioning. It splits into offline and online stores so training and serving reuse the same features.

| Store | Backend | Latency | Primary Use |
| --- | --- | --- | --- |
| Offline store | Parquet on S3, BigQuery, Snowflake | Minutes–hours | Training data prep, batch feature generation |
| Online store | Redis, DynamoDB, Cassandra | ms–seconds | Real-time inference feature serving |

Training pulls bulk data from the offline store; serving reads only the freshest features from the online store.

### Feast Configuration Example

Feast is an open-source Feature Store. Combined with data versioning, it ensures feature definitions stay consistent between training and serving.

```yaml
# feature_repo/feature_store.yaml
project: mlops_demo
registry: data/registry.db
provider: local
online_store:
  type: redis
  connection_string: "localhost:6379"
offline_store:
  type: file
```

Feature definition file:

```python
# feature_repo/features.py
from feast import Entity, FeatureView, Field, FileSource
from feast.types import Float32, Int64
from datetime import timedelta

user = Entity(name="user_id", join_keys=["user_id"])

user_features_source = FileSource(
    path="data/user_features.parquet",
    timestamp_field="event_timestamp",
)

user_features = FeatureView(
    name="user_features",
    entities=[user],
    ttl=timedelta(days=1),
    schema=[
        Field(name="age", dtype=Int64),
        Field(name="score", dtype=Float32),
    ],
    source=user_features_source,
)
```

Run `feast apply` to register feature definitions. Training and serving code can then reference features by the same name.

### Preventing Training-Serving Skew

When training uses one feature computation and serving uses a different one, model performance drops sharply. This is called training-serving skew.

**Common causes:**

1. Training builds features with pandas, serving rebuilds them with SQL — slight logic differences produce different values.
2. Training uses batch features, serving uses real-time features with different logic.
3. Feature versions diverge: training on v1, serving on v2.

**Prevention methods:**

1. **Use a Feature Store**: training and serving reference the same feature definition.
2. **Write feature tests**: compare training features and serving features with identical inputs.
3. **Version explicitly**: include version in feature names; record which feature version a model used.

```python
# Training
features_train = feast_store.get_historical_features(
    entity_df=train_entities,
    features=["user_features:age", "user_features:score"],
)

# Serving
features_online = feast_store.get_online_features(
    entity_rows=[{"user_id": 123}],
    features=["user_features:age", "user_features:score"],
)
```

With a Feature Store, the same feature name automatically matches between training and serving, greatly reducing skew risk.

## See the Flow First

This picture explains why a tool such as DVC exists. The git repository stores a pointer file instead of the large dataset itself, the real data lives in remote storage, and the pipeline reads the pointer to recover the exact input state.

The pointer and the remote have to move together. If either side is missing, reproducibility breaks.

## Key Terms

- **DVC**: Data Version Control. Tracks data and models on top of git.
- **Pointer file**: a `.dvc` file holding a hash and metadata.
- **Remote**: S3, GCS, SSH, or local storage backing DVC.
- **Stage**: a pipeline step with inputs, command, and outputs.
- **Repro**: re-runs only the steps whose inputs changed.

## Before/After

**Before**: `data_v3_final.csv` exists only on one teammate's laptop.

**After**: `git pull && dvc pull` reproduces the exact dataset everywhere.

The gap is bigger than it looks. In the Before state, data handoff becomes a collaboration bottleneck — small updates depend on messengers and manual copies. In the After state, data becomes a shared team asset.

## Hands-on: 5 Steps Through DVC

### Step 1 — Create sample data

```python
import pandas as pd
df = pd.DataFrame({"x": range(100), "y": [i % 2 for i in range(100)]})
df.to_csv("data.csv", index=False)
```

### Step 2 — Initialize DVC (assumed)

```bash
# pip install dvc
# git init && dvc init
# dvc add data.csv
# git add data.csv.dvc .gitignore
# git commit -m "track data v1"
```

Only the pointer and config go into git — the actual data file is managed by DVC. The code repo stays lightweight while data state is versioned.

### Step 3 — Mimic the pointer

```python
import hashlib, json
h = hashlib.md5(open("data.csv", "rb").read()).hexdigest()
pointer = {"path": "data.csv", "md5": h}
with open("data.csv.ptr", "w") as f:
    json.dump(pointer, f, indent=2)
print(pointer)
```

The pointer does not hold the data — it precisely identifies which data. When this hash changes, it signals that the input changed, and that signal becomes the trigger for retraining or reproduction.

### Step 4 — A pipeline stage

```python
from sklearn.linear_model import LogisticRegression
import pickle
df = pd.read_csv("data.csv")
m = LogisticRegression().fit(df[["x"]], df["y"])
with open("model.pkl", "wb") as f:
    pickle.dump(m, f)
```

Data versioning gains meaning when connected to a pipeline. Knowing which stage must re-run when input changes is what enables operational automation.

### Step 5 — Change input, observe re-run signal

```python
df.loc[0, "y"] = 1 - df.loc[0, "y"]
df.to_csv("data.csv", index=False)
new_h = hashlib.md5(open("data.csv", "rb").read()).hexdigest()
print("changed:", new_h != h)
```

This demonstrates why hashes matter. Even when the filename is identical, the system must detect that contents changed. The core of data versioning is making the pipeline — not a person — read this change.

## DVC Operational Workflow

Understanding the flow matters more than memorizing commands. The standard DVC workflow:

1. Track raw data or preprocessing outputs with `dvc add`.
2. Commit generated `.dvc` files and pipeline definitions to git.
3. Upload actual data files with `dvc push` to remote storage.
4. Other environments restore the same state with `git pull` then `dvc pull`.
5. When data changes, repeat the same cycle to create a new version.

The advantage: collaborators can mechanically restore "same code + same data" state.

## Common DVC Commands

```bash
# Initial setup
pip install dvc[s3]
dvc init
dvc remote add -d storage s3://my-bucket/mlops-demo

# Track data
dvc add data/raw/train.parquet
git add data/raw/train.parquet.dvc .gitignore
git commit -m "Track raw training dataset"

# Sync to remote
dvc push

# Restore in another environment
git pull
dvc pull

# View version history
git log -- data/raw/train.parquet.dvc
```

The commands are simple, but what matters operationally is the habit of commit message conventions and documenting data change rationale.

## Reading a `.dvc` File

A typical `.dvc` file looks like:

```yaml
outs:
  - md5: 3f7dd2b9c8a8f6a9e33f0d6b14f7d22a
    size: 128947221
    path: data/raw/train.parquet
```

- `md5`: the hash identifying file contents.
- `size`: file size in bytes.
- `path`: path relative to the working directory.

The key insight: this file is not data — it is a pointer to the data's state.

## Pipeline Definition with DVC

Data versioning becomes powerful when combined with training pipelines:

```yaml
stages:
  preprocess:
    cmd: python src/preprocess.py --input data/raw/train.parquet --output data/processed/train.parquet
    deps:
      - src/preprocess.py
      - data/raw/train.parquet
    outs:
      - data/processed/train.parquet

  train:
    cmd: python src/train.py --data data/processed/train.parquet --model artifacts/model.pkl
    deps:
      - src/train.py
      - data/processed/train.parquet
    outs:
      - artifacts/model.pkl
```

With explicit `deps` and `outs`, only the stages with changed inputs re-run — saving time and cost.

## Full Pipeline Definition Example

```yaml
stages:
  ingest:
    cmd: python src/ingest.py --output data/raw/events.parquet
    deps:
      - src/ingest.py
    outs:
      - data/raw/events.parquet

  validate:
    cmd: python src/validate.py --input data/raw/events.parquet --schema schemas/events_v3.json
    deps:
      - src/validate.py
      - data/raw/events.parquet
      - schemas/events_v3.json
    metrics:
      - reports/validation_metrics.json:
          cache: false

  preprocess:
    cmd: python src/preprocess.py --input data/raw/events.parquet --output data/processed/features.parquet
    deps:
      - src/preprocess.py
      - data/raw/events.parquet
    outs:
      - data/processed/features.parquet

  split:
    cmd: python src/split.py --input data/processed/features.parquet --train data/split/train.parquet --val data/split/val.parquet
    deps:
      - src/split.py
      - data/processed/features.parquet
    outs:
      - data/split/train.parquet
      - data/split/val.parquet

  train:
    cmd: python src/train.py --train data/split/train.parquet --model artifacts/model.pkl
    deps:
      - src/train.py
      - data/split/train.parquet
    outs:
      - artifacts/model.pkl
    params:
      - train.yaml:
          - model.n_estimators
          - model.max_depth

  evaluate:
    cmd: python src/evaluate.py --model artifacts/model.pkl --data data/split/val.parquet
    deps:
      - src/evaluate.py
      - artifacts/model.pkl
      - data/split/val.parquet
    metrics:
      - reports/eval_metrics.json:
          cache: false
    plots:
      - reports/confusion_matrix.csv:
          cache: false
```

Running `dvc repro` re-executes only from the first changed stage. If data changes, it restarts from validate; if preprocessing code changes, it restarts from preprocess.

### DVC Metrics and Plots

```bash
# View metrics
dvc metrics show

# Compare metrics across branches
dvc metrics diff main

# Generate plots
dvc plots show reports/confusion_matrix.csv
```

Saving metrics as JSON enables one-command branch comparisons — useful in PR reviews to objectively show "how did this change affect performance?"

## git-LFS vs DVC Selection Criteria

| Criterion | git-LFS | DVC |
| --- | --- | --- |
| File size | Suitable up to hundreds of MB | GB–TB scale |
| Pipeline | None | DAG definition via `dvc.yaml` |
| Remote storage | Git hosting LFS server | S3, GCS, Azure, SSH, etc. |
| Caching | None | Per-stage caching |
| Team workflow | Same as git | Requires separate `dvc pull/push` |
| Best for | Small binaries, images | Large training data, ML pipelines |

For a small team managing a few dozen-MB files, git-LFS may suffice. But when training data reaches GB scale and pipeline reproduction is needed, DVC fits better.

## Data Validation Example

Adding a validation stage that checks schema and quality on every data version change prevents bad data from reaching training:

```python
import json
import pandas as pd

def validate_schema(df: pd.DataFrame, schema_path: str) -> dict:
    with open(schema_path) as f:
        schema = json.load(f)

    errors = []
    for col_def in schema["columns"]:
        name = col_def["name"]
        dtype = col_def["dtype"]
        nullable = col_def.get("nullable", True)

        if name not in df.columns:
            errors.append(f"Missing column: {name}")
            continue

        if not nullable and df[name].isnull().any():
            null_rate = df[name].isnull().mean()
            errors.append(f"Column {name} has {null_rate:.2%} nulls")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "row_count": len(df),
        "column_count": len(df.columns),
    }
```

Place this in the pipeline's validate stage to block schema violations before they reach training.

## Operational Policy Recommendations

| Item | Recommended Policy |
| --- | --- |
| Raw data retention | Keep versions for at least 90 days |
| Reproduction guarantee | Deployed models must record training data hash |
| Access control | Separate read/write permissions on remote storage |
| Audit trail | Model promotion requires data version link |

Data versioning is not storage management — it is a model accountability system. This link is what lets you narrow down root causes when quality issues arise.

## Data Lineage Tracking

Data versioning does not end at preserving change history. It must also track which data produced which model version.

| Stage | Tracked Item | Example Record | Operational Purpose |
| --- | --- | --- | --- |
| Ingest | Source file path, collection time | `s3://raw/2026-05-12/events.parquet` | Identify collection gaps/delays |
| Validate | Schema version, quality score | `schema=v3, null_rate=0.7%` | Block bad input early |
| Train | Data hash, model version | `md5=...`, `model=v42` | Guarantee training reproducibility |
| Deploy | Promoted model, reference data link | `champion=v42, data=v18` | Deployment rationale audit |

Maintaining a lineage table in both documentation and the model registry enables simultaneous backtracking of model code and data path when performance degrades.

## What to Notice in This Code

- A hash change is the retraining trigger.
- Only the pointer file lives in git.
- A pipeline stage is command, inputs, outputs.
- Data versions and model versions must travel together for comparison to be possible.

## Five Common Mistakes

1. **Committing large data files directly to git.** The repo bloats and collaboration suffers immediately.
2. **Forgetting to configure a remote.** Collaborators get pointer files but cannot pull actual data.
3. **Updating data without committing the version change.** Training result differences become unexplainable later.
4. **Forgetting to declare stage inputs and outputs.** The system cannot determine which stages to re-run.
5. **Tracking data but not models.** The data-model link weakens.

## How This Shows Up in Production

Vision datasets, large text corpora, and log-based recommendation data grow quickly — DVC with an object-storage backend is the common pairing. Small test samples can stay in git, but actual training inputs belong in a remote store connected via pointers.

## How a Senior Engineer Thinks

- Git is for code; DVC is for data and models.
- A configured remote is the default.
- Commit code and data versions together.
- Use pipelines so only changed hashes re-run.
- Small samples can stay in git for tests.

## Checklist

- [ ] Data files are tracked by DVC or LFS.
- [ ] A remote is configured.
- [ ] Models are tracked too.
- [ ] The reproduction command is documented.

## Practice Problems

1. Track a small CSV with DVC.
2. Modify the data and observe the hash change.
3. Mimic an S3 remote with a local directory.

## Wrap-up and Next Steps

Data versioning is the precondition for reproduction. The same code is not enough — you must be able to pull the same data to rebuild the same model.

The key takeaway: **in ML systems, data is not an input file — it is a versioned operational asset.** Next, the training pipeline automates the loop.

## Answering the Opening Questions

- **Why can't code versioning alone reproduce training results?**
  - Even with the same `train.py`, if `data.csv` contents change the hash changes—and a different model is produced. The reproducibility the article emphasized is only achieved when data state (`.dvc` pointers or `md5`) is fixed alongside the code commit.
- **How should you understand the difference between DVC and git-LFS?**
  - git-LFS is useful for storing large files outside the repo, but unlike DVC it doesn't connect `deps`, `outs`, and `dvc repro` for pipeline reproduction. So for hundreds-of-MB binaries git-LFS works, but for GB-scale training data with stage re-execution needs, DVC fits better.
- **How do you maintain version consistency while keeping large data files outside git?**
  - As the article's example showed: commit only pointers like `data.csv.dvc` and pipeline definitions to git, then `dvc push` the actual files to remote storage like S3. Other environments restore the same state with `git pull && dvc pull`, so code and data move as one release unit.
<!-- toc:begin -->
## In this series

- [MLOps 101 (1/10): What Is MLOps?](./01-what-is-mlops.md)
- [MLOps 101 (2/10): Experiment Tracking](./02-experiment-tracking.md)
- **Data Versioning (current)**
- Model Training Pipeline (upcoming)
- Model Deployment (upcoming)
- Model Monitoring (upcoming)
- Data Drift and Model Drift (upcoming)
- Retraining (upcoming)
- Feature Store (upcoming)
- Building a Production ML System (upcoming)

<!-- toc:end -->

## References

- [DVC — Get Started](https://dvc.org/doc/start)
- [git-LFS](https://git-lfs.com/)
- [Pachyderm](https://www.pachyderm.com/)
- [Google — Data versioning](https://cloud.google.com/architecture/ml-on-gcp-best-practices)

Tags: MLOps, DVC, DataVersioning, Reproducibility, DataScience
