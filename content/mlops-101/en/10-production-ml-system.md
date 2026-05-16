---
series: mlops-101
episode: 10
title: Building a Production ML System
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
  - Architecture
  - Production
  - DataScience
  - Pipeline
seo_description: Connect data, training, deployment, monitoring, drift detection, and retraining into one closed-loop production ML system.
last_reviewed: '2026-05-15'
---

# Building a Production ML System

Earlier in this series, we looked at experiment tracking, data versioning, training pipelines, deployment, monitoring, drift detection, retraining, and feature stores one by one. But knowing the parts individually is very different from wiring them into one operating system.

This is where many real teams struggle. Knowing the tool names does not create a system. Data has to move into training on a clear path, trained artifacts need an explicit promotion rule, and when something degrades in production the team needs a known response path.

This is the final post in the MLOps 101 series.

Here, we will connect the previous nine pieces into one closed operational loop and end with a practical maturity checklist.

## Questions this article answers

- How do the earlier nine components connect in a real system?
- Why is tool knowledge alone not enough to create an operating model?
- How do runbooks, on-call, and SLI/SLOs fit into the technical path?
- What is a practical way to assess team maturity?
- In what order should a team improve without absorbing too much complexity at once?

> Mental model: a production ML system is not a box of tools. It is a closed loop where data → training → deployment → observation → retraining are connected and each stage has a clear owner.

## Why It Matters

Building one good model and building an operable system are different jobs. The first is closer to experimentation. The second is closer to boundary design and recovery design. That is why individual tool knowledge is never enough.

An operable system needs three things at the same time. Data and model flow have to connect automatically, observation has to trigger response when signals go abnormal, and the team has to distinguish between what automation should do and what still needs human judgment.

## See the Loop First

![See the Loop First](../../../assets/mlops-101/10/10-01-see-the-loop-first.en.png)

*See the Loop First*
This diagram compresses the whole series into one loop. Data versioning and the feature store stabilize the inputs, the training pipeline produces a candidate model, the registry holds the version, deployment puts it into production, monitoring observes it, and drift plus retraining feed the next cycle.

The key detail is that this is a loop, not a line. Production signals have to flow back into training for MLOps to be complete.

## Key Terms

- **MLOps maturity**: manual → automated → autonomous stages.
- **Runbook**: documented response to an alert.
- **On-call**: rotating responsibility for incidents.
- **SLI/SLO**: indicators and objectives.
- **Postmortem**: blameless review after an incident.

## Before/After

**Before**: notebook training, manual deploys, users report outages.

**After**: a DAG runs data → model → alerts on its own.

## Hands-on: Encode the Maturity Checklist

### Step 1 — Check items

```python
checks = {
    "data_versioned": True,
    "pipeline_dag": True,
    "model_registry": True,
    "container_image": True,
    "metrics_endpoint": True,
    "drift_alert": False,
    "retraining_trigger": False,
    "feature_store": False,
    "runbook": True,
}
```

### Step 2 — Maturity score

```python
def maturity(checks: dict) -> str:
    score = sum(checks.values())
    if score >= 8:
        return "production"
    if score >= 5:
        return "transitional"
    return "early"

print(maturity(checks))
```

### Step 3 — Report what is missing

```python
def missing(checks: dict) -> list:
    return [k for k, v in checks.items() if not v]

print(missing(checks))
```

### Step 4 — Pick the next thing

```python
def next_step(missing_items: list) -> str:
    priority = ["drift_alert", "retraining_trigger", "feature_store"]
    for p in priority:
        if p in missing_items:
            return p
    return "done"

print(next_step(missing(checks)))
```

### Step 5 — Status line for the team chat

```python
def status_line(checks: dict) -> str:
    return f"{maturity(checks)} | next={next_step(missing(checks))}"

print(status_line(checks))
```

## What to Notice in This Code

- A checklist as code makes progress visible.
- The maturity score is a shared bar.
- Picking the *next* one item is enough to keep moving.

## Five Common Mistakes

1. **Trying to install all components at once.**
2. **Buying tools while ignoring organizational change.**
3. **Wiring alerts before defining SLOs.**
4. **Going on-call without runbooks.**
5. **Repeating the same incident — no postmortem culture.**

## How This Shows Up in Production

A fintech runs a payments model on Airflow + MLflow + Feast + Prometheus, with on-call engineers paged using runbooks attached to every alert.

## How a Senior Engineer Thinks

- Start small, grow one component at a time.
- Make boundaries explicit (teams and systems).
- Alerts mean *action* — informational signals belong on dashboards.
- Change one thing at a time.
- Documentation is part of the system.

## Checklist

- [ ] Data versioning is in place.
- [ ] Training runs as a DAG.
- [ ] A model registry exists.
- [ ] Monitoring and drift detection are live.
- [ ] A retraining trigger is connected.
- [ ] Runbooks and on-call rotation exist.

## Practice Problems

1. Pick the three components your team lacks and draft a six-week rollout plan.
2. Which component is most likely to break a `99% < 200ms` SLO?
3. Name two organizational risks that automated retraining introduces.

## Wrap-up and Next Steps

This series gave you the basic circuitry of MLOps. Now go pick *one* component and ship it inside a real project.

<!-- toc:begin -->
- [What is MLOps?](./01-what-is-mlops.md)
- [Experiment Tracking](./02-experiment-tracking.md)
- [Data Versioning](./03-data-versioning.md)
- [Model Training Pipeline](./04-training-pipeline.md)
- [Model Deployment](./05-model-deployment.md)
- [Model Monitoring](./06-model-monitoring.md)
- [Data Drift and Model Drift](./07-data-and-model-drift.md)
- [Retraining](./08-retraining.md)
- [Feature Store](./09-feature-store.md)
- **Building a Production ML System (current)**
<!-- toc:end -->

## References

- [Google — MLOps maturity](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)
- [Microsoft — MLOps maturity model](https://learn.microsoft.com/azure/architecture/example-scenario/mlops/mlops-maturity-model)
- [Made With ML](https://madewithml.com/)
- [Hidden Technical Debt in ML Systems](https://papers.nips.cc/paper_files/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html)

Tags: MLOps, Architecture, Production, DataScience, Pipeline
