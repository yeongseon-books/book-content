---
series: mlops-101
episode: 9
title: "MLOps 101 (9/10): Feature Store"
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
  - FeatureStore
  - Feast
  - DataScience
  - Pipeline
seo_description: Use a feature store to keep training and serving on the same feature definitions, with Feast examples for online and offline paths.
last_reviewed: '2026-05-15'
---

# MLOps 101 (9/10): Feature Store

When a feature with the same name starts being calculated separately in training code and serving code, the two paths drift sooner or later. Training may use a daily aggregate, serving may use a slightly different real-time expression, and the model ends up seeing two different worlds.

Train-serve skew is difficult precisely because it is not always obvious. Offline evaluation can still look healthy while production behavior is already weaker because the feature path changed.

This is the 9th post in the MLOps 101 series.

Here, we will treat a feature store not as a storage box for features, but as the contract layer that lets training and serving share the same definitions.


![mlops 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/mlops-101/09/09-01-see-the-flow-first.en.png)
*mlops 101 chapter 9 flow overview*
> A feature store is not a data warehouse. It is a definition layer that guarantees training uses the same features as serving, eliminating one large class of production bugs.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Feature Store?
- Which signal should the example or diagram make visible for Feature Store?
- What failure should be prevented first when Feature Store reaches a real system?

## Questions this article answers

- Why does train-serve skew keep reappearing in ML systems?
- What are the distinct roles of online and offline stores?
- How should you think about entities and feature views in Feast?
- Why are point-in-time joins so important?
- How does a feature store increase reuse across teams?

> Mental model: a feature store is not just a place to keep feature values. It is the layer where a feature is defined once and reused consistently by both training and serving.

## Why It Matters

If two systems compute the same feature separately, divergence is only a matter of time. A small difference in timestamp handling, null behavior, or aggregation logic is enough to create a different model input.

That is why the real value of a feature store is consistency rather than storage. Training extraction and serving lookup have to reference the same definition if you want train-serve skew to shrink.

## See the Flow First

The center of this picture is the feature registry. Raw data becomes a shared feature definition, that definition flows into offline and online paths, training reads one side, serving reads the other, and both consume the same contract.

That is why the feature store should be definition-centered, not value-centered.

## Key Terms

- **Entity**: the join key for features (e.g., `user_id`).
- **Feature View**: a feature definition tied to a source.
- **Online store**: low-latency key-value (e.g., Redis).
- **Offline store**: large-scale analytics (Parquet/BigQuery).
- **Point-in-time join**: time-correct historical join.

## Before/After

**Before**: training notebooks and serving code compute features independently.

**After**: one Feature View, called from both sides.

## Hands-on: A Tiny Feast Workflow

### Step 1 — Definitions

```python
from feast import Entity, FeatureView, Field, FileSource
from feast.types import Float32

user = Entity(name="user_id", join_keys=["user_id"])
src = FileSource(path="users.parquet", timestamp_field="event_ts")

view = FeatureView(
    name="user_stats",
    entities=[user],
    schema=[Field(name="age", dtype=Float32)],
    source=src,
)
```

### Step 2 — Register

```bash
feast apply
```

### Step 3 — Pull historical features

```python
from feast import FeatureStore
import pandas as pd

fs = FeatureStore(repo_path=".")
entity_df = pd.DataFrame({"user_id": [1, 2], "event_timestamp": pd.to_datetime(["2026-01-01", "2026-01-02"])})
training = fs.get_historical_features(entity_df, ["user_stats:age"]).to_df()
```

### Step 4 — Materialize to online

```bash
feast materialize-incremental $(date -u +"%Y-%m-%dT%H:%M:%S")
```

### Step 5 — Serve

```python
online = fs.get_online_features(
    features=["user_stats:age"],
    entity_rows=[{"user_id": 1}],
).to_dict()
```

## What to Notice in This Code

- The entity is the join key.
- A Feature View binds a definition to a source.
- Materialization is what bridges offline and online.

## Five Common Mistakes

1. **Feature name collisions across teams.**
2. **Time leakage from skipping point-in-time joins.**
3. **Different definitions in online and offline stores.**
4. **No TTL — stale values get served.**
5. **No monitoring — silent missing features.**

## How This Shows Up in Production

A payments fraud model uses Feast to share user behavior features between training and serving, with the same code path used by three teams.

## How a Senior Engineer Thinks

- Features are assets — names and definitions form a catalog.
- Time correctness matters more than raw accuracy.
- Online/offline parity is the top priority.
- Monitor features themselves (freshness, missingness).
- Reuse is the highest-ROI MLOps investment.

## Checklist

- [ ] Feature View definitions are versioned.
- [ ] Point-in-time joins are used.
- [ ] Online materialization is scheduled.
- [ ] Feature freshness is monitored.

## Practice Problems

1. Define a *7-day rolling revenue* feature as a Feature View.
2. What kind of leakage occurs without point-in-time joins?
3. Name two alternatives to Feast and the trade-offs.

## Wrap-up and Next Steps

A Feature Store is one piece. The final post stitches everything into a working production ML system.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Feature Store?**
  - The article treats Feature Store as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Feature Store?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Feature Store reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [MLOps 101 (1/10): What Is MLOps?](./01-what-is-mlops.md)
- [MLOps 101 (2/10): Experiment Tracking](./02-experiment-tracking.md)
- [MLOps 101 (3/10): Data Versioning](./03-data-versioning.md)
- [MLOps 101 (4/10): Model Training Pipeline](./04-training-pipeline.md)
- [MLOps 101 (5/10): Model Deployment](./05-model-deployment.md)
- [MLOps 101 (6/10): Model Monitoring](./06-model-monitoring.md)
- [MLOps 101 (7/10): Data Drift and Model Drift](./07-data-and-model-drift.md)
- [MLOps 101 (8/10): Retraining](./08-retraining.md)
- **Feature Store (current)**
- Building a Production ML System (upcoming)

<!-- toc:end -->

## References

- [Feast documentation](https://docs.feast.dev/)
- [Tecton — feature platforms](https://www.tecton.ai/blog/)
- [Uber — feature store](https://www.uber.com/blog/michelangelo-machine-learning-platform/)
- [Google Vertex AI Feature Store](https://cloud.google.com/vertex-ai/docs/featurestore)

Tags: MLOps, FeatureStore, Feast, DataScience, Pipeline
