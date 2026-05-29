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

This is the 4th post in the MLOps 101 series.

Here, we will distinguish a training pipeline from simple script automation and show why stage boundaries and a DAG matter.


![mlops 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/mlops-101/04/04-01-see-the-flow-first.en.png)
*mlops 101 chapter 4 flow overview*
> A training pipeline is not a large script with a scheduler attached. It is a DAG of small stages with clear inputs and outputs, designed so failed stages do not force the whole run to restart.

## Questions to Keep in Mind

- Why split a single training script into multiple pipeline stages?
- How is a DAG different from a plain execution order?
- Where do Airflow, Prefect, and Kubeflow fit into the picture?

## Why It Matters

Manual training is slow, hard to reproduce, and difficult to debug. When a nightly training job fails and the whole process has to restart from the beginning, the operating cost rises quickly.

When stages are split cleanly, the team can narrow the failure immediately and rerun only the part whose inputs changed. A pipeline is the mechanism that raises both observability and recoverability for training.

### Model Serving Patterns

Moving a trained model into production takes one of three broad forms. Each pattern trades off response time, throughput, and infrastructure complexity differently.

| Pattern | Latency | Throughput | Best suited for |
| --- | --- | --- | --- |
| Batch inference | minutes–hours | Very high | Weekly reports, bulk predictions |
| Real-time inference | ms–seconds | Moderate | Per-request responses, recommendations, search |
| Streaming inference | sub-second | High | Real-time fraud detection, anomaly detection, log analysis |

#### Batch inference

All inputs are gathered and processed at a scheduled time. Airflow or Cron handles scheduling; results go to a database or file store. Best when throughput matters more than response speed.

#### Real-time inference

An HTTP endpoint receives a request and returns a prediction immediately. Frameworks like FastAPI, Flask, and BentoML are common. Best when response time is critical and results differ per request.

#### Streaming inference

Data arrives through a message queue (Kafka, Kinesis) and is processed sequentially. Best when events arrive continuously and each event needs an immediate decision.

### FastAPI Model Serving Example

A slightly expanded example that includes version info, input validation, logging, and latency measurement:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import pickle
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Model API", version="1.0.0")

# load model at startup
MODEL_PATH = "model.pkl"
try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    logger.info(f"Model loaded from {MODEL_PATH}")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    model = None

class PredictRequest(BaseModel):
    x: float = Field(..., ge=0, le=100, description="Input feature (0-100)")

class PredictResponse(BaseModel):
    prediction: int
    model_version: str
    latency_ms: float

@app.get("/healthz")
def health():
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "ok", "version": "1.0.0"}

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    start = time.time()
    try:
        pred = int(model.predict([[req.x]])[0])
        latency = (time.time() - start) * 1000
        logger.info(f"Prediction: x={req.x}, pred={pred}, latency={latency:.2f}ms")
        return PredictResponse(
            prediction=pred,
            model_version="1.0.0",
            latency_ms=round(latency, 2),
        )
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail="Prediction error")
```

This code includes input-range validation (`ge=0, le=100`), model-load failure handling, latency measurement, and structured logging — all of which are essential for diagnosing issues quickly in production.

### Model Packaging

Deploying a model requires bundling code, model file, libraries, and environment into a single artifact. Three common approaches:

#### 1. Docker image

The most widely used approach. Bundles model, code, libraries, and OS environment together.

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY model.pkl .
COPY main.py .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Advantage: environment consistency, high compatibility with orchestrators like Kubernetes.

#### 2. ONNX format

ONNX is a framework-neutral model format. Converting PyTorch, TensorFlow, or scikit-learn models to ONNX makes them usable across languages and runtimes.

```python
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

initial_type = [("float_input", FloatTensorType([None, 1]))]
onnx_model = convert_sklearn(model, initial_types=initial_type)

with open("model.onnx", "wb") as f:
    f.write(onnx_model.SerializeToString())
```

Advantage: inference speed optimization, framework independence.

#### 3. BentoML bundle

BentoML packages model and API code together.

```python
import bentoml
from sklearn.linear_model import LogisticRegression

# save model
model = LogisticRegression().fit([[0], [1]], [0, 1])
bentoml.sklearn.save_model("lr_model", model)

# serving code (service.py)
import bentoml
from bentoml.io import JSON

runner = bentoml.sklearn.get("lr_model:latest").to_runner()
svc = bentoml.Service("lr_service", runners=[runner])

@svc.api(input=JSON(), output=JSON())
def predict(input_data):
    result = runner.predict.run([input_data["x"]])
    return {"prediction": int(result[0])}
```

Advantage: model saving, API serving, and Docker build handled in one place.

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

## Airflow vs Prefect: Design Differences

When choosing an orchestrator, team workflow and failure-response patterns matter more than feature lists.

| Aspect | Airflow | Prefect |
| --- | --- | --- |
| DAG expression | Static DAG definitions | Flexible dynamic flow expression |
| Operational track record | Mature, large-scale batch operations | Easy onboarding, smooth local development |
| UI observability | Strong task/schedule visibility | Good execution state/retry visibility |
| Best-fit team | Data-platform / batch-centric teams | Product teams running frequent experiments |

Neither is universally superior. The deciding factor is how often your team changes pipelines and what kind of pipelines they run.

## Airflow DAG Extended Example

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime

def validate_schema():
    print("validate schema")

def train_model():
    print("train model")

def evaluate_model():
    print("evaluate model")

def register_model():
    print("register model")

with DAG(
    dag_id="ml_training_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="0 2 * * *",
    catchup=False,
    max_active_runs=1,
) as dag:
    start = EmptyOperator(task_id="start")
    schema = PythonOperator(task_id="validate_schema", python_callable=validate_schema)
    train = PythonOperator(task_id="train", python_callable=train_model)
    evaluate = PythonOperator(task_id="evaluate", python_callable=evaluate_model)
    register = PythonOperator(task_id="register", python_callable=register_model)
    end = EmptyOperator(task_id="end")

    start >> schema >> train >> evaluate >> register >> end
```

The key in this structure is that each stage isolates failure causes clearly.

## Pipeline Configuration File

```yaml
pipeline:
  name: churn-train
  schedule: "0 2 * * *"
  retries: 2
  retry_delay_sec: 300

data:
  source: s3://ml-data/churn/raw/
  schema_path: schemas/churn_v3.json
  min_rows: 50000

training:
  algorithm: xgboost
  objective: binary:logistic
  max_depth: 6
  eta: 0.1
  n_estimators: 400

evaluation:
  min_auc: 0.84
  max_inference_latency_ms: 80

registry:
  model_name: churn-risk-model
  stage_on_success: Staging
```

Separating parameters into a config file lets teams change operational settings without modifying code.

## Pipeline Quality Gates

- Block progression to the training stage when input schema validation fails.
- Block registry enrollment when evaluation metrics fall below threshold.
- On retry exhaustion, send an alert with a runbook link.
- Verify output consistency when re-running the same inputs.

These gates turn pipeline automation from a simple scheduler into a quality defense line.

## DVC Pipeline Integration

Even without a heavy orchestrator like Airflow, a DVC pipeline can deliver reproducible training flows. For smaller teams this approach is lighter.

### `dvc.yaml` training pipeline

```yaml
stages:
  prepare:
    cmd: python src/prepare.py --config params.yaml
    deps:
      - src/prepare.py
      - data/raw/
    params:
      - params.yaml:
          - data.sample_rate
          - data.random_seed
    outs:
      - data/prepared/

  train:
    cmd: python src/train.py --config params.yaml
    deps:
      - src/train.py
      - data/prepared/
    params:
      - params.yaml:
          - model.algorithm
          - model.n_estimators
          - model.max_depth
    outs:
      - artifacts/model.pkl
    metrics:
      - reports/train_metrics.json:
          cache: false

  evaluate:
    cmd: python src/evaluate.py --model artifacts/model.pkl --data data/prepared/test.parquet
    deps:
      - src/evaluate.py
      - artifacts/model.pkl
      - data/prepared/test.parquet
    metrics:
      - reports/eval_metrics.json:
          cache: false
```

### `params.yaml` separation

```yaml
data:
  sample_rate: 1.0
  random_seed: 42

model:
  algorithm: random_forest
  n_estimators: 200
  max_depth: 8
  min_samples_leaf: 5
```

When parameters live outside code, changing an experiment does not require code changes. `dvc params diff` shows exactly which parameters shifted.

### Pipeline reproduction and caching

```bash
# full reproduction
dvc repro

# single stage only
dvc repro train

# unchanged inputs → cache hit
# "Stage 'train' didn't change, skipping"
```

DVC compares input hashes per stage and only re-runs what changed. If heavy preprocessing is already complete, only training re-runs — saving significant time and cost.

## Pipeline Error Handling Pattern

The most critical aspect of an operational pipeline is how it responds to failure. This pattern structures per-stage failure handling:

```python
import logging
import traceback
from dataclasses import dataclass
from typing import Callable

logger = logging.getLogger(__name__)

@dataclass
class StageResult:
    name: str
    success: bool
    output_path: str | None = None
    error: str | None = None

def run_stage(name: str, fn: Callable, retries: int = 2) -> StageResult:
    for attempt in range(retries + 1):
        try:
            output = fn()
            logger.info(f"Stage '{name}' succeeded on attempt {attempt + 1}")
            return StageResult(name=name, success=True, output_path=output)
        except Exception as e:
            logger.warning(f"Stage '{name}' attempt {attempt + 1} failed: {e}")
            if attempt == retries:
                return StageResult(
                    name=name,
                    success=False,
                    error=traceback.format_exc(),
                )
    return StageResult(name=name, success=False, error="Unknown")
```

The key: define a retry count and produce structured error information on final failure. When connected to an alerting system, nightly batch failures become visible first thing in the morning.

## Pipeline Observability Metrics

```python
import time
from prometheus_client import Histogram, Counter

STAGE_DURATION = Histogram(
    "pipeline_stage_duration_seconds",
    "Duration of each pipeline stage",
    ["stage_name"],
)
STAGE_FAILURES = Counter(
    "pipeline_stage_failures_total",
    "Number of stage failures",
    ["stage_name"],
)

def timed_stage(name: str, fn: Callable):
    start = time.time()
    try:
        result = fn()
        STAGE_DURATION.labels(stage_name=name).observe(time.time() - start)
        return result
    except Exception:
        STAGE_FAILURES.labels(stage_name=name).inc()
        raise
```

Recording execution time and failure count per stage lets you see bottleneck stages and flaky stages on a dashboard immediately.

In production, connect these metrics to a Grafana dashboard with alert conditions. For example, trigger a Slack alert when `pipeline_stage_duration_seconds{stage_name="train"}` exceeds the SLA threshold (e.g., 3600 seconds). This ensures the on-call team is aware immediately when nightly batch pipelines run longer than expected.

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

A training pipeline is not simple automation — it is the structure that decomposes training into stages for easier reproduction and faster recovery. The key takeaway: **a good pipeline prioritizes failure-recovery speed over training speed.** Next, model deployment turns trained artifacts into live services.

## Answering the Opening Questions

- **Why split a single training script into a multi-stage pipeline?**
  - Separating `ingest`, `preprocess`, `train`, `evaluate` lets you narrow failure points immediately and re-run only the segment with changed inputs. Especially, separating evaluation from training creates an operational boundary to block sub-threshold models before registry.
- **How is a DAG different from a simple execution order?**
  - A DAG is not just "run top to bottom" — it explicitly states dependencies between stages and re-execution scope. So Airflow's `validate_schema >> train >> evaluate >> register` reveals not just order but where to stop and where to restart.
- **Where do orchestrators like Airflow, Prefect, and Kubeflow fit?**
  - These tools do not design stage boundaries for you — they schedule, retry, and alert around already-separated stages. The core is having small stages, idempotency, caching, and failure logs first, not the orchestrator name.
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
