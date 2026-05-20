---
series: mlops-101
episode: 6
title: "MLOps 101 (6/10): Model Monitoring"
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
  - Monitoring
  - Prometheus
  - Observability
  - DataScience
seo_description: Track latency, error rate, and prediction distribution so production ML systems reveal trouble before users become the monitoring system.
last_reviewed: '2026-05-15'
---

# MLOps 101 (6/10): Model Monitoring

Once a model is deployed, it can look calm from the outside. Requests still succeed and responses still come back, but latency may be climbing, the prediction mix may be skewing, or downstream business results may already be weakening.

That is why model monitoring is not an optional operations add-on. It is the layer that tells you not only whether the model is alive, but what kind of state it is alive in right now and whether a problem is already forming.

This is post 6 in the MLOps 101 series.

Here, we will treat monitoring as the observation layer where system metrics, model metrics, and business metrics meet, starting from a practical Prometheus-based baseline.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Model Monitoring?
- Which signal should the example or diagram make visible for Model Monitoring?
- What failure should be prevented first when Model Monitoring reaches a real system?

## Big Picture

![mlops 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/mlops-101/06/06-01-see-the-flow-first.en.png)

*mlops 101 chapter 6 flow overview*

This picture places Model Monitoring inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> Model monitoring is not watching a dashboard. It is catching production anomalies fast enough to prevent silent performance loss from compounding into a large incident.

## Questions this article answers

- Why is accuracy alone too slow as a production signal?
- How should you think about metrics, logs, and traces?
- What roles do Prometheus and Grafana play for model serving?
- Why is prediction distribution the starting point for drift detection?
- How do you design alert rules that humans can actually act on?

> Mental model: model monitoring is not just about server health. It is the observation layer that combines request behavior and prediction behavior so problems surface early.

## Why It Matters

Accuracy usually arrives late, especially when labels are delayed. Latency, error rate, input distribution, and prediction-class balance often move first. That means a live model cannot be judged by one metric alone.

Without monitoring, deployment is close to driving with your eyes closed. The team cannot tell when the abnormal behavior started, which version it started on, or whether the issue belongs to the runtime, the model, or the business process around it.

## See the Flow First

This is the smallest useful monitoring shape. The application exposes time-series metrics on `/metrics`, Prometheus scrapes them, Grafana visualizes them, and Alertmanager routes meaningful threshold crossings to humans.

The critical idea is that collection has to be automatic. A dashboard that depends on someone remembering to open it is a habit, not an operations system.

## Key Terms

- **Metric**: a numeric time series.
- **Log**: a textual event record.
- **Trace**: the path of a single request.
- **SLO**: a service level objective, e.g. 99% under 200 ms.
- **Alert**: a notification fired when a threshold is crossed.

## Before/After

**Before**: incidents are discovered when users complain.

**After**: alerts arrive in the team channel automatically.

## Hands-on: Add Prometheus Metrics to a FastAPI Model

### Step 1 — Install

```bash
pip install prometheus-client
```

### Step 2 — Counter and histogram

```python
from prometheus_client import Counter, Histogram

REQS = Counter("predict_requests_total", "total predict requests")
LAT = Histogram("predict_latency_seconds", "predict latency")
```

### Step 3 — Wire into FastAPI

```python
import time
from fastapi import FastAPI
from prometheus_client import make_asgi_app

app = FastAPI()
app.mount("/metrics", make_asgi_app())

@app.post("/predict")
def predict(x: float):
    start = time.time()
    REQS.inc()
    result = {"prediction": int(x > 0.5)}
    LAT.observe(time.time() - start)
    return result
```

### Step 4 — Track prediction distribution

```python
PRED = Counter("predict_class_total", "predicted class", ["cls"])

def record(p: int):
    PRED.labels(cls=str(p)).inc()
```

### Step 5 — Alert rule

```yaml
groups:
  - name: model
    rules:
      - alert: HighLatency
        expr: histogram_quantile(0.99, rate(predict_latency_seconds_bucket[5m])) > 0.5
        for: 5m
        labels:
          severity: warning
```

**Expected effect:** if the 99th percentile latency stays above the threshold for five minutes, the alert enters the warning state instead of paging immediately on one noisy spike.

The point of alert rules is not to generate more numbers. It is to send only signals that a human or automation can act on.

## First Checks When Monitoring Says Something Is Off

When an alert fires, the team needs a first-check sequence, not a vague reminder to "look at the dashboard." A short sequence reduces mean time to understanding.

### Check 1 — Is the problem request-path latency or model behavior?

```text
Look at p95/p99 latency, error rate, and request volume together.
```

If latency and error rate spike together, start in the runtime path. If latency is stable but prediction distribution changes sharply, start in the model/data path.

### Check 2 — Did prediction distribution change before business metrics moved?

```text
Compare recent class distribution against the previous healthy window.
```

If the class mix changed first, investigate input drift before assuming the serving stack broke.

### Check 3 — Does the alert link to a runbook with the next action?

```yaml
annotations:
  runbook: https://internal.example/runbooks/model-latency
```

An alert without an explicit next action is a status light, not an operating tool.

## What to Notice in This Code

- The `/metrics` endpoint is scraped by Prometheus on a schedule.
- A histogram lets you compute quantiles later.
- Labels turn one counter into many prediction-class series.

## Five Common Mistakes

1. **Only watching system metrics like CPU and memory.**
2. **Not recording prediction distribution — drift becomes invisible.**
3. **Too many alerts — humans go numb.**
4. **No SLO defined, so no shared bar to clear.**
5. **No dashboard, so context is lost during incidents.**

## How This Shows Up in Production

A payments fraud model emits metrics every minute. When fraud rate crosses an SLO, on-call gets paged with a runbook attached.

## How a Senior Engineer Thinks

- Watch all three layers (system, model, business).
- Every alert must be *actionable*.
- A dashboard should be readable in five seconds.
- An SLO is a business agreement, not a number.
- Runbooks live next to the alert.

## Checklist

- [ ] A `/metrics` endpoint is exposed.
- [ ] Latency and error-rate alerts are configured.
- [ ] Prediction distribution is tracked.
- [ ] Each alert links to a runbook.

## Practice Problems

1. Write an alert rule that fires when *error rate exceeds 1%*.
2. Add a metric for *mean input value* per minute.
3. Pick four widgets for the first screen of a Grafana dashboard.

## Wrap-up and Next Steps

Monitoring is the *prerequisite* for drift detection. The next post tackles *Data Drift and Model Drift* directly.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Model Monitoring?**
  - The article treats Model Monitoring as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Model Monitoring?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Model Monitoring reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [MLOps 101 (1/10): What Is MLOps?](./01-what-is-mlops.md)
- [MLOps 101 (2/10): Experiment Tracking](./02-experiment-tracking.md)
- [MLOps 101 (3/10): Data Versioning](./03-data-versioning.md)
- [MLOps 101 (4/10): Model Training Pipeline](./04-training-pipeline.md)
- [MLOps 101 (5/10): Model Deployment](./05-model-deployment.md)
- **Model Monitoring (current)**
- Data Drift and Model Drift (upcoming)
- Retraining (upcoming)
- Feature Store (upcoming)
- Building a Production ML System (upcoming)

<!-- toc:end -->

## References

- [Prometheus documentation](https://prometheus.io/docs/)
- [prometheus-client (Python)](https://github.com/prometheus/client_python)
- [Grafana documentation](https://grafana.com/docs/)
- [Google SRE workbook — SLOs](https://sre.google/workbook/implementing-slos/)

Tags: MLOps, Monitoring, Prometheus, Observability, DataScience
