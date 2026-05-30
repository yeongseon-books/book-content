---
series: mlops-101
episode: 1
title: "MLOps 101 (1/10): What Is MLOps?"
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
  - DevOps
  - MLSystem
  - Production
  - DataScience
seo_description: Understand MLOps as an operational loop for data, training, deployment, monitoring, and retraining so ML models stay reliable in production.
last_reviewed: '2026-05-15'
---

# MLOps 101 (1/10): What Is MLOps?

Training one good model and running that model in production for months are very different jobs. A model can look great inside a notebook, then become hard to reproduce after deployment, drift when the input shape changes, or lose performance with no trace of when the decline started.

Many teams make the same assumption at this point: if model quality improves, operations will take care of themselves. In practice, the opposite is usually true. In production, the model, data, code, deployment path, monitoring, and retraining loop all have to move together.

This is the first post in the MLOps 101 series.

Here, we will treat MLOps not as a list of tool names, but as the operational loop that lets a model stay alive in production.


![mlops 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/mlops-101/01/01-01-see-the-loop-first.en.png)
*mlops 101 chapter 1 flow overview*
> MLOps is not the tool collection that runs when a model file lands on a server. It is the operational system linking data → training → registration → deployment → monitoring → retraining in one loop.

## Questions to Keep in Mind

- What boundary should you inspect first when applying What Is MLOps??
- Which signal should the example or diagram make visible for What Is MLOps??
- What failure should be prevented first when What Is MLOps? reaches a real system?

## Questions this article answers

- What makes MLOps different from simply attaching DevOps habits to ML?
- Why do even accurate models break down quickly in real production systems?
- What does it actually mean to manage data, code, and models together?
- Which building blocks let a team reproduce, deploy, observe, and improve a model over time?
- How does MLOps maturity usually progress in practice?

> Mental model: MLOps is not the technique for deploying one model file. It is the operating system around a loop of data → training → registration → deployment → monitoring → retraining.

## Why It Matters

Most ML projects fail first at the operating model, not at the model metric. Teams cannot rerun last week's best experiment, cannot tell which data trained the live model, and cannot explain why performance is slipping because the evidence was never captured.

That is why the starting point for MLOps is not buying a larger platform. It is deciding whether the same inputs can produce the same result again, whether the live model can be observed, and whether the team knows which part of the loop to revisit when something goes wrong.

## MLOps Maturity Model

Not every team needs full automation from day one. Google and Microsoft describe MLOps in staged maturity levels. The practical approach is to identify where your team currently sits, then prepare for the next level.

### Level 0 — Manual Process

Every step runs by hand. Training happens in a notebook, model files are copied manually, and deployment is a config change. There is no reproducibility and no monitoring. Most teams start here.

### Level 1 — ML Pipeline Automation

The training process is automated as a pipeline. Data collection through model training runs end-to-end, and an experiment tracker records metrics. Deployment is still manual, and monitoring is partial at best.

### Level 2 — CI/CD Pipeline Automation

Both training and deployment are automated. Code changes trigger build, test, and deploy steps automatically. Alerts fire when model performance drops below a threshold. Drift detection and retrain triggers are active. This level is where you can realistically call the system operational MLOps.

Most teams are somewhere between Level 1 and Level 2. What matters is not the level name but knowing exactly what your team lacks and what the next priority should be.

## What Happens Without MLOps

Many teams assume MLOps can be added later. In practice, starting without a system means technical debt accumulates fast.

### 1. Irreproducibility

You cannot recreate last week's best model. The data version was never saved, the parameters exist only in memory, and no commit is linked to the experiment. Without reproducibility, improvement is guesswork.

### 2. Deployment Bottleneck

A model that ran fine in a notebook breaks on the server. Library versions differ, paths differ, environment variables differ. When every deployment is manual labor, model improvement speed drops with it.

### 3. Drift Neglect

Once deployed, teams assume the model is done. But input distributions shift over time and the model gradually ages. Without a mechanism to detect this, the team only learns about degradation from user complaints.

### 4. Collaboration Breakdown

One person creates `model_final_v2_really.pkl`, another shares accuracy via messenger, another passes notebooks on USB. As the team grows, confusion grows with it.

MLOps is the attempt to solve these four problems at the system level.

## ML Project Stages and Tools

An ML project's lifecycle breaks into distinct stages. Understanding what each stage does and which tools operate there makes it clear that MLOps is not simply DevOps copy-pasted onto ML.

| Stage | Primary Role | Representative Tools |
|---|---|---|
| Data Collection | Pull raw data from logs, APIs, databases | Kafka, Airflow, Fivetran |
| Data Cleaning | Handle missing values, outliers, duplicates; transform | Pandas, dbt, Great Expectations |
| Feature Engineering | Create and select features for model input | Feast, Tecton, pandas |
| Model Training | Choose algorithm and tune hyperparameters | scikit-learn, PyTorch, XGBoost |
| Model Evaluation | Measure metrics against validation data and compare | MLflow, W&B, Neptune |
| Model Deployment | Expose trained result as a service endpoint | FastAPI, BentoML, Seldon |
| Monitoring | Track input distributions, prediction quality, system metrics | Prometheus, Grafana, Evidently |
| Retraining | Retrain when performance drops or drift is detected | Airflow, Kubeflow Pipelines |

The key is that these stages do not run independently. The monitoring output from the last stage feeds back into data collection and training, closing the loop.

## See the Loop First

This loop is the shortest useful picture of MLOps. Data and code feed a training pipeline, the trained model moves into a registry, deployment sends that version into production, and monitoring feeds real operating signals back into the next training cycle.

The important detail is that this is not a one-time delivery pipeline. Models age, input distributions change, and production conditions keep moving. MLOps exists to make that change manageable.

## Key Terms

- **MLOps**: ML plus DevOps; continuous training, deployment, and monitoring.
- **CT (Continuous Training)**: retraining as data changes.
- **Model Registry**: a versioned store for trained models.
- **Feature Store**: a shared store for features.
- **Drift**: how data and model behavior shift over time.

## Before/After

**Before**: a single notebook, manual deployment, no monitoring.

**After**: an automated pipeline, versioned models, and drift alerts.

The difference is not just automation. In the Before state, almost no evidence remains to explain problems. In the After state, you can recreate the same model and trace what changed.

## Hands-on: 5 Steps Through a Mini MLOps Loop

### Step 1 — Snapshot the data

```python
import hashlib, json
data = [{"x": 1, "y": 0}, {"x": 2, "y": 1}]
snap = hashlib.sha1(json.dumps(data).encode()).hexdigest()[:10]
print("data version:", snap)
```

This single hash line matters. The most common reason a model cannot be retrained to the same result is not code — it is that the data changed underneath. A data version pins the training input to something identifiable.

### Step 2 — Train a model

```python
from sklearn.linear_model import LogisticRegression
import numpy as np
X = np.array([[1], [2], [3], [4]])
y = np.array([0, 0, 1, 1])
model = LogisticRegression().fit(X, y)
```

The model type is not the point. What matters is that this training result can be connected back to the data version and the code that produced it.

### Step 3 — Register the model

```python
import pickle, os
os.makedirs("registry", exist_ok=True)
with open("registry/model_v1.pkl", "wb") as f:
    pickle.dump(model, f)
```

You do not need a massive registry platform from the start. Even a single file with a version rule and a fixed location turns the model from "something I ran once" into a managed artifact.

### Step 4 — Attach metadata

```python
meta = {"data_version": snap, "model_version": "v1", "metric": float(model.score(X, y))}
print(meta)
```

A model file alone loses meaning over time. Recording which data version produced it, what performance it achieved, and what name it was registered under makes comparison and promotion possible.

### Step 5 — Log a prediction

```python
import time
log = {"ts": time.time(), "pred": int(model.predict([[5]])[0])}
print("log:", log)
```

This step is the starting point for operations. A deployed model ultimately produces predictions, and the distribution, latency, and failure rate of those predictions drive the next decision. MLOps does not end at training — it restarts from this log.

## What to Notice in This Code

- A data hash is the seed of reproducibility.
- A registry can start as a single file.
- Metadata turns a model file into an operational asset.
- Prediction logs make monitoring and drift detection possible.

The example is small, but it demonstrates the core MLOps attitude: treat data, model, and operational signals not as separate concerns but as one connected flow.

## Five Common Mistakes

1. Versioning models but not data and code — you cannot recreate the same model.
2. Deploying without monitoring — you only learn about failures from users.
3. Shipping a notebook to production — experiment and production boundaries collapse, taking reproducibility with them.
4. Triggering retraining manually — without schedule, performance, or drift criteria, every team member decides differently.
5. Tracking model metrics without business metrics — production models are not evaluated on accuracy alone.

## How This Shows Up in Production

Recommendation systems, fraud detection, and demand forecasting live in fast-changing data where MLOps is not optional — it is survival. Models do not stay good once and remain good forever. Conversely, if data rarely changes and only batch runs are needed, building version control and deploy automation incrementally is more realistic than buying a heavy platform up front.

From a senior engineer's perspective, the loop matters more than accuracy. Can you explain which data produced this model? Can you retrain it? Do operating signals remain? When something breaks, which stage do you return to?

## MLOps Maturity Roadmap

In practice, not every team starts from the same place. A clear adoption sequence reduces failure risk. The table below splits maturity levels by operational characteristics and exit criteria.

| Level | Operational Characteristics | Must-Have Items | Exit Criteria to Next Level |
|---|---|---|---|
| Level 0 Manual | Notebook-centric, manual deploy | Minimal experiment logs, model file storage rule | Same-experiment reproducibility rate above 80% |
| Level 1 Repeatable Training | Data/code/model versions linked | Experiment tracking, data versioning, training script separation | Weekly training pipeline runs stably |
| Level 2 Automated Deployment | Auto-promotion after evaluation | Model registry, deploy pipeline, rollback rules | Mean recovery time from deploy failure under 30 min |
| Level 3 Observation-Based Ops | Continuous post-deploy observation | Latency/error-rate/prediction-distribution monitoring, drift alerts | Runbook execution rate above 90% after anomaly detection |
| Level 4 Closed-Loop Ops | Detect-retrain-promote loop automated | Retrain trigger, champion-challenger comparison, approval policy | Manual interventions decrease each quarterly ops review |

The core of this table is not a technology stack list — it is an operational contract. When judging which level your team occupies, check reproducibility, recoverability, and observability before checking tool adoption.

## Traditional CI/CD vs ML CI/CD

When people call MLOps an extension of DevOps, the most commonly missed point is that the verification target differs. Traditional CI/CD centers on verifying code behavior. ML CI/CD centers on verifying model behavior — a product of code and data combined.

| Comparison | Traditional CI/CD | ML CI/CD |
|---|---|---|
| Change Input | Code changes | Code + data + feature definitions + hyperparameters |
| Build Artifact | Binary, container image | Model artifact + metadata + container image |
| Test Criteria | Unit/integration/E2E pass | Tests pass + performance threshold + drift risk |
| Deploy Decision | Functionality correctness | Functionality + prediction quality + operational stability |
| Rollback Trigger | Error rate, outage | Error rate + quality degradation + distribution anomaly |

ML CI/CD does not stop at "the code runs." It must include "the model still produces meaningful predictions in production." Consequently, the test stage must include data schema checks, feature-missing checks, and performance comparison against a baseline model as defaults.

## Minimal CI/CD Pipeline Example

Below is a minimal pipeline flow commonly used in model repositories.

```yaml
name: ml-ci-cd
on:
  push:
    branches: [main]

jobs:
  train-and-validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run unit tests
        run: pytest -q
      - name: Train model
        run: python train.py --config configs/train.yaml
      - name: Validate model quality
        run: python evaluate.py --min-auc 0.82 --max-latency-ms 80
      - name: Register model
        run: python register_model.py --stage Staging
```

The intent of this pipeline is not simple automation. It bundles training and evaluation into a single release unit so that only models meeting operational criteria advance to the next stage.

## Adoption Priority Order

The most common sticking point when adopting MLOps is "what to do first." The following order generally has the lowest failure rate:

1. Lock experiment tracking and data version linkage first.
2. Decompose the training pipeline into rerunnable stages.
3. Document model registry and promotion criteria.
4. Attach post-deploy monitoring and drift alerts.
5. Connect retraining automation last.

Following this order prevents automation from amplifying operational risk. Conversely, automating retraining before an observation system is in place risks deploying bad models faster.

## Checklist

- [ ] Data is versioned.
- [ ] Models are versioned.
- [ ] Predictions are logged.
- [ ] Retraining is documented.

## Practice Problems

1. Build a data hash for your team's most recent model.
2. Save two model versions to a registry and compare them.
3. Add latency to the prediction log.

## Wrap-up and Next Steps

MLOps is a system, not a single line of model code. Next, experiment tracking begins the journey.

## Answering the Opening Questions

- **How is MLOps different from simply bolting DevOps onto ML?**
  - In this article, MLOps is not just training automation—it's a system that ties data hashing, model registry, prediction logs, and retraining triggers into a single operational loop. While traditional CI/CD focuses on code deployment, MLOps includes drift detection and CT to keep models alive over time.
- **Why do even highly accurate models quickly develop problems in production?**
  - As shown in the article, input distributions shift enough to trigger KS tests, and prediction distributions and performance can keep wobbling in production. Without data versions, prediction logs, and retraining criteria, a model that scored well locally loses the evidence to explain why performance dropped after deployment.
- **What does "managing data, code, and model together" actually mean in practice?**
  - Even in a small example, we created data versions with `snap`, stored models in `registry/model_v1.pkl`, and recorded metrics and model version together in a `meta` dictionary. The point is leaving linkage—which data and which code produced which model—so you can reproduce results and trace problems later.
<!-- toc:begin -->
## In this series

- **What Is MLOps? (current)**
- Experiment Tracking (upcoming)
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

- [Google — MLOps levels](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)
- [ml-ops.org](https://ml-ops.org/)
- [Microsoft — MLOps maturity](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/mlops-maturity-model)
- [Sculley et al. — Hidden Tech Debt in ML](https://papers.nips.cc/paper_files/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html)

Tags: MLOps, DevOps, MLSystem, Production, DataScience
