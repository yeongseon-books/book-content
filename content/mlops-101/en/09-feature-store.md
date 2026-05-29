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

- Why does train-serve skew keep reappearing in ML systems?
- What are the distinct roles of online and offline stores?
- How should you think about entities and feature views in Feast?

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

---

## See the Flow First

The center of this picture is the feature registry. Raw data becomes a shared feature definition, that definition flows into offline and online paths, training reads one side, serving reads the other, and both consume the same contract.

That is why the feature store should be definition-centered, not value-centered.

---

## Key Terms

- **Entity**: the join key for features (e.g., `user_id`).
- **Feature View**: a feature definition tied to a source.
- **Online store**: low-latency key-value (e.g., Redis).
- **Offline store**: large-scale analytics (Parquet/BigQuery).
- **Point-in-time join**: time-correct historical join.

Understanding the feature store starts with this definition layer, not with what database it uses underneath.

---

## Before/After

**Before**: training notebooks and serving code compute features independently.

**After**: one Feature View, called from both sides.

In the Before state, small implementation differences silently degrade production performance. In the After state, at least the feature definition is managed in one place.

---

## Data Versioning Tool Comparison

A feature store manages feature definitions, but version-controlling the raw data itself requires separate tooling. The table below compares three popular data versioning tools by storage method, Git integration, and scale.

| Tool | Storage Method | Git Integration | Scale | Key Strength |
|---|---|---|---|---|
| **DVC** | Remote store (S3, GCS) | Git remote linking | Medium | Explicit code/data separation |
| **LakeFS** | Git layer on S3/Azure | Git-like commands | Large | Branch/merge/tag on data |
| **Delta Lake** | Parquet + transaction log | Separate | Large | ACID, time travel, schema evolution |

DVC works most like Git — it keeps a `.dvc` metadata file in the repo while the actual data lives in a remote store. LakeFS brings Git-style version control on top of S3. Delta Lake provides ACID transactions in Spark environments. Selection criteria: team Git fluency, data volume, cloud infrastructure already in use.

---

## DVC Usage Example

DVC does not track data files directly in Git. Instead it stores metadata in Git and pushes the actual files to a remote store.

```bash
# 1. Initialize DVC
dvc init

# 2. Add a data file
dvc add data/train.csv

# 3. Commit the metadata
git add data/train.csv.dvc .gitignore
git commit -m "Add training data"

# 4. Set up remote storage
dvc remote add -d storage s3://my-bucket/dvc-store

# 5. Push data
dvc push

# 6. Pull in another environment
dvc pull
```

`dvc add` replaces the data file with a `.dvc` metadata pointer and adds the original to `.gitignore`. `dvc push` uploads to the remote store; `dvc pull` downloads. This structure ties code and data under the same Git commit, making it possible to trace which data version trained which model.

---

## Data Lineage Tracking

Even with data versioning, if you cannot trace which data trained which model, root-cause analysis becomes guesswork when performance drops. Data lineage records the creation, transformation, and consumption path of every dataset.

Key elements of lineage tracking:

1. **Source data**: where it was collected
2. **Transformation steps**: cleaning, feature engineering, aggregation
3. **Model training**: which model was trained on this dataset
4. **Prediction logs**: which model received which inputs

Without lineage, separating a data problem from a model problem is slow. The simplest approach is to log the data path and hash alongside the model run in a tool like MLflow.

```python
import mlflow
import hashlib

data_path = "data/train.csv"
with open(data_path, "rb") as f:
    data_hash = hashlib.md5(f.read()).hexdigest()

with mlflow.start_run():
    mlflow.log_param("data_path", data_path)
    mlflow.log_param("data_hash", data_hash)
    # training code follows
```

This links a model version to its data hash so that when production accuracy drops you can trace back to the exact dataset used for training.

---

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

The first thing to notice here is the entity and feature view. Which key to join on, which source to read from, and which features to expose are all fixed in code.

### Step 2 — Register

```bash
feast apply
```

Registration reflects the declared feature definitions into the system. The whole point of using a feature store is to share these definitions across teams and paths.

### Step 3 — Pull historical features

```python
from feast import FeatureStore
import pandas as pd

fs = FeatureStore(repo_path=".")
entity_df = pd.DataFrame({"user_id": [1, 2], "event_timestamp": pd.to_datetime(["2026-01-01", "2026-01-02"])})
training = fs.get_historical_features(entity_df, ["user_stats:age"]).to_df()
```

Timestamps matter here. For a given entity at a given point in time, only the feature values that were actually available at that moment should be joined — otherwise you leak future information.

### Step 4 — Materialize to online

```bash
feast materialize-incremental $(date -u +"%Y-%m-%dT%H:%M:%S")
```

Materialization bridges the offline definition to the online lookup path. Without this step, the definition that training saw never reaches the serving layer.

### Step 5 — Serve

```python
online = fs.get_online_features(
    features=["user_stats:age"],
    entity_rows=[{"user_id": 1}],
).to_dict()
```

This is where the shared definition becomes visible: input paths differ, but the feature name and its definition are the same.

---

## What to Notice in This Code

- The entity is the join key.
- A Feature View binds a definition to a source.
- Materialization bridges offline and online.
- Definition parity between training and serving is the highest priority.

The value of a feature store ultimately comes from reuse and consistency. It prevents multiple teams from computing the same feature independently.

---

## Five Common Mistakes

1. **Feature name collisions across teams.**
   Conflicts arise before reuse does.
2. **Time leakage from skipping point-in-time joins.**
   Future information leaks into training data.
3. **Different definitions in online and offline stores.**
   Train-serve skew reappears.
4. **No TTL or freshness policy.**
   Stale features continue to be served indefinitely.
5. **No monitoring on the features themselves.**
   Missing values and latency accumulate silently.

## Maintaining Train-Serve Consistency Without a Feature Store

Even without adopting a feature store, you can reduce train-serve skew. The key is extracting feature computation into a shared function and calling it from both training and serving code.

```python
# features.py
def compute_user_features(user_id: int, df) -> dict:
    user_df = df[df["user_id"] == user_id]
    return {
        "age": int(user_df["age"].iloc[0]),
        "purchase_count_7d": len(user_df[user_df["days_ago"] <= 7]),
    }
```

Both the training script and the serving API import this function:

```python
# train.py
from features import compute_user_features

features = compute_user_features(user_id, df)
```

```python
# serve.py
from features import compute_user_features

features = compute_user_features(user_id, live_df)
```

This approach is lighter than a feature store but may introduce latency when real-time lookups are needed. For small teams with few models, it is often practical enough.

---

## When to Adopt a Feature Store

A feature store is not necessary for every team. Consider adoption when:

1. **Multiple models share the same features.** Eliminates duplicate computation.
2. **Train-serve skew keeps recurring.** Centralized definitions are the fix.
3. **Real-time features are required.** Sub-5ms feature retrieval per request.
4. **Team size exceeds 5 engineers.** Shared definitions pay off at scale.

If you have 1-2 models and a team of 2-3, shared functions may be enough. A feature store is a tool, but it also creates operational overhead.

---

## How This Shows Up in Production

In fraud detection and recommendation systems where multiple models share user behavior features, the ROI of a feature store is high. A feature defined once can be reused by every team without re-implementation.

## How a Senior Engineer Thinks

- Features are assets — names and definitions form a catalog.
- Time correctness matters more than raw accuracy.
- Online/offline parity is the top priority.
- Monitor features themselves (freshness, missingness).
- Reuse is the highest-ROI MLOps investment.

---

## Checklist

- [ ] Feature View definitions are versioned.
- [ ] Point-in-time joins are used.
- [ ] Online materialization is scheduled.
- [ ] Feature freshness is monitored.

## Practice Problems

1. Define a *7-day rolling revenue* feature as a Feature View.
2. What kind of leakage occurs without point-in-time joins?
3. Name two alternatives to Feast and the trade-offs.

## Extended Feast Patterns

The value of a feature store lies in feature reuse and train-serve consistency. Achieving this requires designing feature definitions, materialization schedules, and freshness policies together.

### Expanded Entity/Feature View Example

```python
from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource
from feast.types import Int64, Float32

user = Entity(name="user_id", join_keys=["user_id"])

src = FileSource(
    path="data/user_features.parquet",
    timestamp_field="event_timestamp",
)

user_behavior_v1 = FeatureView(
    name="user_behavior_v1",
    entities=[user],
    ttl=timedelta(days=2),
    schema=[
        Field(name="purchase_cnt_7d", dtype=Int64),
        Field(name="avg_spend_30d", dtype=Float32),
    ],
    source=src,
)
```

Setting `ttl=timedelta(days=2)` means features older than 2 days are dropped from the online store. Too short and queries return null; too long and you serve stale values.

## Feature Serving Pattern Comparison

| Pattern | Advantage | Watch Out For |
|---|---|---|
| On-demand computation | Highest freshness | Potential latency increase |
| Online store lookup | Low latency | Must manage materialization lag |
| Hybrid | Balance of latency and freshness | Increased architecture complexity |

Low-latency services like recommendations and fraud detection typically default to online store lookups, computing a few expensive features on-demand as a hybrid.

## Materialization Operations

```bash
# Materialize a date range from offline to online
feast materialize 2026-05-01T00:00:00 2026-05-12T00:00:00

# Incremental materialization for recent data
feast materialize-incremental 2026-05-12T00:00:00
```

If materialization fails, the online store goes stale and model quality degrades. Monitor materialization success rate and latency as first-class signals.

## Train/Serve Consistency Check

```python
def compare_feature_value(train_value: float, serve_value: float, tolerance: float = 1e-6) -> bool:
    return abs(train_value - serve_value) <= tolerance
```

In practice, sample a set of entities periodically and compare training-extracted values against online-store values in a scheduled validation batch.

## Feature Governance Suggestions

- Include a domain prefix and version in feature names. Example: `risk_user_behavior_v1`.
- Assign an owning team and change approver per feature.
- Auto-generate an impact list of affected models on definition changes.
- Track missing rate, freshness, and materialization lag as feature-quality SLIs.

Without governance, a feature store quickly fills with conflicting definitions. The technology layer and operational policy must be designed together.

## Online/Offline Store Comparison

| Aspect | Offline Store | Online Store |
|---|---|---|
| Primary use | Training extraction, backfill, analysis | Real-time inference feature lookup |
| Latency | Minutes to hours | Milliseconds to seconds |
| Data shape | Large batch, point-in-time joins | Key-based latest-value lookup |
| Quality checks | Missing rate, schema, time alignment | Freshness, materialization lag, TTL expiry |
| Typical tech | Parquet/S3, BigQuery, Snowflake | Redis, DynamoDB, Cassandra |

The most commonly overlooked detail is that offline data quality criteria and online freshness criteria differ. Even if training data is clean, late materialization into the online store immediately degrades serving quality.

## Feast Query Code Patterns

Using the same feature names in training and serving while splitting only the lookup path is the simplest operational pattern.

```python
from __future__ import annotations

import pandas as pd
from feast import FeatureStore

store = FeatureStore(repo_path="feature_repo")

def load_training_features() -> pd.DataFrame:
    entity_df = pd.DataFrame(
        {
            "user_id": [101, 102, 103],
            "event_timestamp": pd.to_datetime(["2026-05-10", "2026-05-11", "2026-05-12"]),
        }
    )
    return store.get_historical_features(
        entity_df=entity_df,
        features=["user_behavior_v1:purchase_cnt_7d", "user_behavior_v1:avg_spend_30d"],
    ).to_df()

def load_online_features(user_id: int) -> dict:
    return store.get_online_features(
        features=["user_behavior_v1:purchase_cnt_7d", "user_behavior_v1:avg_spend_30d"],
        entity_rows=[{"user_id": user_id}],
    ).to_dict()
```

When the feature name set is identical between training and serving, narrowing down whether a performance drop comes from the model or the features becomes much faster.

## Detailed Feast Feature Definition Example

In Feast, defining features requires understanding four components: entity, data source, feature view, and feature service.

```python
from feast import Entity, FeatureView, Field, FileSource, FeatureService
from feast.types import Float32, Int64, String
from datetime import timedelta

# 1. Entity — the key used to look up features
customer = Entity(
    name="customer_id",
    join_keys=["customer_id"],
    description="Unique customer identifier",
)

# 2. Data source — where feature values are stored
customer_source = FileSource(
    path="data/customer_features.parquet",
    timestamp_field="event_timestamp",
    created_timestamp_column="created_timestamp",
)

# 3. Feature view — feature group with metadata
customer_features = FeatureView(
    name="customer_features",
    entities=[customer],
    ttl=timedelta(days=7),
    schema=[
        Field(name="total_purchases", dtype=Int64),
        Field(name="avg_order_value", dtype=Float32),
        Field(name="days_since_last_order", dtype=Int64),
        Field(name="preferred_category", dtype=String),
        Field(name="lifetime_value", dtype=Float32),
    ],
    source=customer_source,
    online=True,
    tags={"team": "ml-platform", "version": "v2"},
)

# 4. Feature service — bundle features needed by a specific model
fraud_detection_service = FeatureService(
    name="fraud_detection_features",
    features=[customer_features],
    description="Feature bundle for fraud detection model",
)
```

`ttl=timedelta(days=7)` means values older than 7 days are evicted from the online store. Set TTL too short and queries return null; set it too long and stale values drive inference.

## Feature Validation and Schema Evolution

As a feature store matures, schemas change: new features are added, types change, deprecated features are removed. Validation guards against bad data reaching the online store.

```python
from great_expectations.core import ExpectationSuite, ExpectationConfiguration
import great_expectations as gx

def create_feature_validation_suite(feature_view_name: str) -> ExpectationSuite:
    """Create a data-quality validation suite for a feature view."""
    suite = ExpectationSuite(expectation_suite_name=f"{feature_view_name}_validation")

    # Null ratio check
    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_not_be_null",
            kwargs={"column": "customer_id"},
        )
    )

    # Value range check
    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_between",
            kwargs={
                "column": "avg_order_value",
                "min_value": 0,
                "max_value": 100000,
            },
        )
    )

    # Uniqueness ratio check
    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_proportion_of_unique_values_to_be_between",
            kwargs={
                "column": "customer_id",
                "min_value": 0.99,
                "max_value": 1.0,
            },
        )
    )

    return suite
```

Plugging this validation into the feature ingestion pipeline prevents bad values from entering the online store. If `avg_order_value` is negative or unrealistically large, that signals an upstream ETL problem.

## Online/Offline Consistency Validation

The core promise of a feature store is "training and serving see the same feature values." When this promise breaks, training-serving skew appears.

```python
import numpy as np
from feast import FeatureStore

def validate_online_offline_consistency(
    store: FeatureStore,
    entity_ids: list[dict],
    feature_service_name: str,
    tolerance: float = 0.01,
) -> dict:
    """Validate that online and offline feature values are consistent."""
    # Online lookup
    online_features = store.get_online_features(
        features=store.get_feature_service(feature_service_name),
        entity_rows=entity_ids,
    ).to_dict()

    # Offline lookup (same point in time)
    offline_features = store.get_historical_features(
        features=store.get_feature_service(feature_service_name),
        entity_df=create_entity_df(entity_ids),
    ).to_df()

    mismatches = []
    for col in online_features:
        if col in ("customer_id", "event_timestamp"):
            continue
        online_vals = np.array(online_features[col])
        offline_vals = offline_features[col].values
        diff = np.abs(online_vals - offline_vals).max()
        if diff > tolerance:
            mismatches.append({"feature": col, "max_diff": float(diff)})

    return {
        "consistent": len(mismatches) == 0,
        "mismatches": mismatches,
        "checked_features": len(online_features) - 2,
    }
```

Running this validation periodically catches training-serving skew early.

## Wrap-up and Next Steps

A feature store is not a box for storing features — it is the contract layer that makes training and serving see the same definitions. With this layer in place, the world the model saw offline and the world it sees in production diverge less.

The one takeaway from this article: **the purpose of a feature store is consistency, not convenience.** The next post ties all the pieces together into a single operational ML system.

## Answering the Opening Questions

- **Why does training-serving skew keep recurring?**
  - When the training notebook uses pandas aggregation and the serving code uses different SQL or real-time formulas, even the same feature name `age` or `purchase_cnt_7d` can have different actual values. The article framed the feature store as a definition-sharing layer (not just storage) precisely because of this recurring computation-path divergence.
- **What's the role difference between online and offline stores?**
  - The offline store handles bulk extraction and point-in-time joins for training via `get_historical_features()`; the online store returns the latest features at millisecond latency for real-time inference via `get_online_features()`. The article explained that both stores share the same definitions but manage latency and quality criteria differently.
- **How should you understand entity and feature view in Feast?**
  - An entity is the join key like `user_id` or `customer_id` that features attach to; a feature view declares which features to read from which source for that key. With TTL, schema, and source together in one place (like `user_behavior_v1`), training and serving use the same feature name with the same meaning.
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
