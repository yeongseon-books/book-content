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

The same code with different data produces a different model. That means MLOps without data versioning is only half built. You might be able to reproduce the code path, but you still cannot reproduce the outcome.

This is post 3 in the MLOps 101 series.

Here, we will treat data versioning not as file backup, but as a reproducibility contract that lets the whole team pull the same inputs in the same state.


![mlops 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/mlops-101/03/03-01-see-the-flow-first.en.png)
*mlops 101 chapter 3 flow overview*
> Data versioning is not a tool that forces large files into git. It is a pointer-plus-storage system that identifies the exact input state so the whole team can pull the same data in the same moment in time.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Data Versioning?
- Which signal should the example or diagram make visible for Data Versioning?
- What failure should be prevented first when Data Versioning reaches a real system?

## Questions this article answers

- Why can code versioning alone never reproduce an ML result?
- How should you think about DVC versus git-LFS?
- How do you keep large data files outside git without losing version consistency?
- Why are pointer files and hashes so important?
- How should data versions and model versions move together?

> Mental model: data versioning is not about putting large files into git. It is about operating a pointer plus remote-storage system that identifies the exact state of the input data.

## Why It Matters

One of the most common mistakes in ML systems is assuming the model came from the code. In practice, the model comes from the combination of code and data. When the input changes, the result changes, even if the repository did not.

That is why experiment tracking alone is not enough. A high metric becomes hard to explain, and an older model becomes impossible to rebuild, if the training data state was never preserved.

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

### Step 3 — Mimic the pointer

```python
import hashlib, json
h = hashlib.md5(open("data.csv", "rb").read()).hexdigest()
pointer = {"path": "data.csv", "md5": h}
with open("data.csv.ptr", "w") as f:
    json.dump(pointer, f, indent=2)
print(pointer)
```

### Step 4 — A pipeline stage

```python
from sklearn.linear_model import LogisticRegression
import pickle
df = pd.read_csv("data.csv")
m = LogisticRegression().fit(df[["x"]], df["y"])
with open("model.pkl", "wb") as f:
    pickle.dump(m, f)
```

### Step 5 — Change input, observe re-run signal

```python
df.loc[0, "y"] = 1 - df.loc[0, "y"]
df.to_csv("data.csv", index=False)
new_h = hashlib.md5(open("data.csv", "rb").read()).hexdigest()
print("changed:", new_h != h)
```

## What to Notice in This Code

- A hash change is the retraining trigger.
- Only the pointer file lives in git.
- A pipeline stage is command, inputs, outputs.

## Five Common Mistakes

1. Committing large data files directly to git.
2. Forgetting to configure a remote, breaking reproduction for collaborators.
3. Updating data without committing the change.
4. Forgetting to declare DVC stage inputs and outputs.
5. Tracking data but not models.

## How This Shows Up in Production

Vision datasets and large text corpora outgrow git-LFS quickly; DVC with an S3 backend is a typical pairing.

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

Data versioning is the precondition for reproduction. Next, the training pipeline automates the loop.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Data Versioning?**
  - The article treats Data Versioning as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Data Versioning?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Data Versioning reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

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
