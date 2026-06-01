---
title: "AI Data Preparation 101 (10/10): Building a Production Data Pipeline"
series: ai-data-preparation-101
episode: 10
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- Data Pipelines
- Production
- DVC
- Airflow
- pandera
- MLOps
last_reviewed: '2026-05-14'
seo_description: Episodes 1-9 covered cleaning, dedup, PII redaction, tokenization,
  chunking, quality filtering, synthesis, augmentation, and splitting.
---

# AI Data Preparation 101 (10/10): Building a Production Data Pipeline

Cleaning, deduplication, PII handling, tokenization, filtering, and splitting all matter on their own, but production requires them to run as one repeatable system. The hard part is not knowing each step in isolation, but wiring them into a pipeline you can rerun and trust.

This is the final post in the AI Data Preparation 101 series. Here we cover how to turn the earlier stages into a production data pipeline with reproducibility and observability built in.


![Architecture - a 6-stage pipeline](https://yeongseon-books.github.io/book-public-assets/assets/ai-data-preparation-101/10/10-01-architecture-a-6-stage-pipeline.en.png)
*Architecture - a 6-stage pipeline*

> A production data pipeline is not a script you run once — it is a versioned, observable, reproducible system where every dataset has a lineage, a hash, and an owner, because the next retrain depends on being able to recreate the last one.

## Questions to Keep in Mind

- Which system properties turn a set of preprocessing scripts into a production pipeline?
- How do versioning, fingerprints, and cache keys work together to preserve reproducibility?
- What operational value do orchestrators such as Airflow add beyond a cron job?

## "How do I tie everything we learned into one pipeline?"

Episodes 1-9 covered cleaning, dedup, PII redaction, tokenization, chunking, quality filtering, synthesis, augmentation, and splitting. In production these stages must run automatically every week or every day. The final episode is a pipeline design that integrates all of them.

Four requirements for a production data pipeline:

1. **Reproducibility** - the same input must always produce the same output
2. **Versioning** - track dataset versions like git
3. **Observability** - measure per-stage statistics, drift, and failures
4. **Idempotency** - rerunning a stage twice must not change the result

## Architecture - a 6-stage pipeline

Each stage owns input/output parquet files plus a manifest. The manifest records input fingerprints, code versions, and parameters.

## Dataset versioning with DVC

Manage datasets like git. Code commits and data versions are tied 1:1.

```bash
# pip install dvc
dvc init
dvc remote add -d s3 s3://my-bucket/datasets

# Track per-stage outputs
dvc add data/02_clean.parquet
dvc add data/05_chunked.parquet
git add data/02_clean.parquet.dvc data/05_chunked.parquet.dvc
git commit -m "data: v2026.05.03"
dvc push
```

```python
# pipeline.py
import yaml, hashlib, pathlib, pandas as pd

class Stage:
    name: str
    inputs: list[str]
    outputs: list[str]
    params: dict

    def fingerprint(self) -> str:
        h = hashlib.sha256()
        h.update(self.name.encode())
        for p in sorted(self.inputs):
            h.update(pathlib.Path(p).read_bytes())
        h.update(yaml.safe_dump(self.params, sort_keys=True).encode())
        return h.hexdigest()[:12]

    def is_cached(self) -> bool:
        manifest = pathlib.Path(f"manifests/{self.name}.yaml")
        if not manifest.exists():
            return False
        return yaml.safe_load(manifest.read_text())["fingerprint"] == self.fingerprint()

    def run(self):
        if self.is_cached():
            print(f"[skip] {self.name} cached")
            return
        self.execute()  # implemented by subclass
        self.write_manifest()
```

When `fingerprint` is unchanged, the stage is not re-executed. Idempotency and caching are solved together.

## Per-stage implementation - integrated pipeline

```python
import pandas as pd
from datetime import datetime

# Stage 1: Ingest
def stage_ingest(sources: list[str]) -> pd.DataFrame:
    dfs = [pd.read_json(s, lines=True) for s in sources]
    df = pd.concat(dfs, ignore_index=True)
    df["ingested_at"] = datetime.utcnow()
    return df

# Stage 2: Clean + Dedup (Ep3)
def stage_clean(df: pd.DataFrame) -> pd.DataFrame:
    df["text"] = df["text"].str.strip().str.replace(r"\s+", " ", regex=True)
    df = df[df["text"].str.len() >= 50]
    df = df.drop_duplicates(subset=["text"])
    return df

# Stage 3: PII (Ep4)
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def stage_pii(df: pd.DataFrame) -> pd.DataFrame:
    def redact(t: str) -> str:
        results = analyzer.analyze(text=t, language="en")
        return anonymizer.anonymize(text=t, analyzer_results=results).text
    df["text"] = df["text"].map(redact)
    return df

# Stage 4: Quality (Ep6)
def stage_quality(df: pd.DataFrame) -> pd.DataFrame:
    def passes(t: str) -> bool:
        words = t.split()
        return 50 <= len(words) <= 100_000
    return df[df["text"].map(passes)]

# Stage 5: Tokenize/Chunk (Ep5)
def stage_chunk(df: pd.DataFrame, max_tokens: int = 500) -> pd.DataFrame:
    rows = []
    for _, r in df.iterrows():
        # recursive_chunk from Ep5
        chunks = [r["text"][i:i+2000] for i in range(0, len(r["text"]), 1800)]
        for i, c in enumerate(chunks):
            rows.append({**r.to_dict(), "chunk_id": i, "text": c})
    return pd.DataFrame(rows)

# Stage 6: Split + Version (Ep9)
def stage_split(df: pd.DataFrame, time_col: str = "ingested_at") -> dict:
    df = df.sort_values(time_col)
    n = len(df)
    return {
        "train": df.iloc[:int(n*0.8)],
        "val":   df.iloc[int(n*0.8):int(n*0.9)],
        "test":  df.iloc[int(n*0.9):],
    }
```

## Pipeline orchestration - Airflow example

Production picks one of Airflow, Prefect, or Dagster. Airflow is the most common.

```python
# dags/data_prep.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default = {"owner": "ml-platform", "retries": 2, "retry_delay": timedelta(minutes=10)}

with DAG("data_prep", default_args=default,
         schedule_interval="@daily", start_date=datetime(2026, 1, 1)) as dag:
    t1 = PythonOperator(task_id="ingest",  python_callable=stage_ingest_task)
    t2 = PythonOperator(task_id="clean",   python_callable=stage_clean_task)
    t3 = PythonOperator(task_id="pii",     python_callable=stage_pii_task)
    t4 = PythonOperator(task_id="quality", python_callable=stage_quality_task)
    t5 = PythonOperator(task_id="chunk",   python_callable=stage_chunk_task)
    t6 = PythonOperator(task_id="split",   python_callable=stage_split_task)
    t1 >> t2 >> t3 >> t4 >> t5 >> t6
```

Airflow provides retry, scheduling, and a lineage UI. Failed stages alone can be rerun, saving cost.

## Observability - per-stage statistics

```python
import json, time

def with_stats(stage_fn):
    def wrapper(df, *args, **kwargs):
        n_in = len(df)
        t0 = time.time()
        out = stage_fn(df, *args, **kwargs)
        n_out = len(out) if hasattr(out, "__len__") else sum(len(v) for v in out.values())
        stats = {
            "stage": stage_fn.__name__,
            "rows_in": n_in,
            "rows_out": n_out,
            "drop_rate": 1 - n_out / max(n_in, 1),
            "duration_s": round(time.time() - t0, 2),
            "ts": datetime.utcnow().isoformat(),
        }
        with open(f"stats/{stage_fn.__name__}.jsonl", "a") as f:
            f.write(json.dumps(stats) + "\n")
        return out
    return wrapper

stage_clean = with_stats(stage_clean)
```

Plotting per-stage drop_rate over time exposes source distribution drift immediately. A quality drop_rate that normally sits at 0.1 jumping to 0.5 signals the source broke.

## Schema validation - Great Expectations / pandera

If the input/output schema changes, the pipeline breaks silently. Schema checks are the last safety net.

```python
# pip install pandera
import pandera as pa
from pandera.typing import Series

class TextSchema(pa.DataFrameModel):
    id: Series[str] = pa.Field(unique=True)
    text: Series[str] = pa.Field(str_length={"min_value": 1})
    source: Series[str]
    ingested_at: Series["datetime64[ns]"]

# Validate at every stage entry
TextSchema.validate(df)
```

Stages fail loudly when the schema breaks. Better than silently producing a broken dataset.

## 5 common mistakes

1. **Re-running the entire pipeline without caching**: cost and time explode. Fingerprint-based stage caching is mandatory.
2. **Skipping schema validation**: silent source format changes let pipelines pass while producing broken datasets in production.
3. **Decoupling dataset version from code commit**: when bugs hit, you cannot trace which dataset version trained the model. DVC + git tag is the standard pairing.
4. **Not collecting stage statistics**: drift detection is delayed and root-cause analysis becomes impossible.
5. **Doing PII redaction last**: even one raw PII landing on disk is a compliance violation. Redact right after ingest or clean.

## Key Takeaways

- A production data pipeline has 6 stages: ingest -> clean/dedup -> PII -> quality -> tokenize/chunk -> split.
- Use DVC to map dataset versions 1:1 with git commits.
- Per-stage fingerprint caching solves both idempotency and cost.
- Airflow / Prefect / Dagster handle schedule, retry, and lineage.
- Collect drop_rate, duration, and schema stats at every stage to monitor drift.
- Redact PII immediately after ingest.

This concludes the series. We started from GIGO in Ep1 and ended at a production pipeline. Next up: multimodal data preparation, or model evaluation.

---

## Operational checklist

- [ ] Give every stage explicit inputs, outputs, parameters, and a fingerprinted manifest
- [ ] Tie dataset versions to code commits through DVC or an equivalent mechanism
- [ ] Collect rows in/out, drop rate, duration, and timestamp metrics for every stage
- [ ] Place PII handling close to ingest so raw identifiers do not spread downstream
- [ ] Fail loudly on schema drift and support stage-level reruns from the orchestrator


## Design principles for turning a pipeline into an operating system

As a pipeline grows in stages, quality depends less on individual stage performance and more on the clarity of contracts between stages. For a data preparation pipeline, "it ran successfully once" matters far less than "it produces the same result every time." Operational design breaks down into five axes.

### 1) Lock down input contracts first

Document the file format, required columns, null policies, timezone conventions, and encoding for every input. For example, if `event_time` is ambiguous between UTC and local time, split boundaries shift daily and train/validation leakage happens silently. Batches that fail schema validation at the pipeline entry point should halt immediately — this is safer long-term than letting partial data propagate.

### 2) Assign identifiers to per-stage artifacts

When intermediate outputs follow a path like `raw -> normalized -> deduped -> pii-redacted -> filtered -> tokenized`, attach a data version identifier rather than relying on filenames alone. In production you must always be able to answer "why did yesterday's model differ?" At minimum, three pieces must be linked:

- Data version ID
- Pipeline code commit SHA
- Config file hash at execution time

With this linkage, reproducibility experiments, regression analysis, and rollback decisions finish quickly. Without it, you cannot recreate the same dataset, and incident recovery devolves into guesswork meetings.

### 3) Decompose quality metrics per stage

If you only watch trailing indicators like final token count or training loss, you are already too late. Watching removal rates and distribution shifts at each stage lets you narrow causes early. For example, if the quality filter stage normally removes 18% but today removes 43%, suspect an input distribution change or an overly sensitive rule before blaming the model.

Minimum operational metrics in practice:

- Schema validation failure count
- Deduplication rate (document-level, sentence-level)
- PII detection count (by type)
- Quality filter removal rate (by rule)
- Token length distribution (p50, p90, p99)

### 4) Treat failure as the default path, not an exception

Production batches will fail. The question is not whether, but what the team can know immediately when they do. Failure alerts must include which stage failed, which input batch triggered it, and what differs from the last successful run. Sending just "batch failed" forces the on-call engineer to re-read logs from scratch.

### 5) State explicit success conditions for each batch

Judging success by exit code alone misses quality degradation. Even if every stage exits cleanly, a final usable-sample count 30% below the threshold can severely harm training quality. Separate technical success (all stages completed) from data-quality success (output meets defined thresholds).

## Incident response runbook example

A production pipeline lives by its runbook, not its architecture doc. A runbook answers "what do I check at 2 AM and in what order?" rather than "how does this work?" Below is a minimal runbook directly applicable to a data preparation pipeline.

### Step 1. Verify the input layer

- Confirm new file count and total size are within normal range.
- Confirm file encoding and compression format match previous runs.
- Check that partition paths (date, region, customer) are not missing.

### Step 2. Isolate the quality degradation cause

- Dedup rate spike: check for upstream re-sends or dedup key changes.
- PII detection spike: check whether regex/NER rules were updated.
- Quality filter spike: check for language distribution shifts or over-aggressive HTML cleaning rules.

### Step 3. Estimate training impact

- Final sample count reduction rate
- Mean token length change rate
- Domain distribution shift (e.g., support 40% → 12%)

These three items separate "rerun immediately" from "proceed conditionally." If impact is large, halt the batch, fix the root cause, and rerun.

### Step 4. Rerun criteria

A rerun is not a simple retry — it is a guarantee of identical conditions. Pin the input snapshot and config hash before rerunning. Otherwise what looks like "recovery succeeded" actually produced a different dataset.

## Extension scenario: multi-domain data pipeline

Once a single-domain pipeline stabilizes, the natural next step is feeding multiple domains (product docs, customer support conversations, code comments, policy documents) into the same system. The most common mistake at this point is merging quality criteria into a single threshold. Each domain differs in sentence length, structure, and acceptable noise levels, so filters and sampling strategies must stay separate.

Strategies that work in practice:

- Separate preprocessing rules per domain while maintaining a common interface.
- Set quality metric thresholds independently per domain.
- Apply domain-weighted sampling just before the final merge.
- Run model evaluation on per-domain validation sets to track regressions.

This structure keeps pipeline complexity under control as data volume grows, and prevents a failure in one domain from cascading into a full pipeline halt.

## Role separation and responsibility boundaries for team operations

When pipeline quality wobbles, the most frequently missed factor is not technology but responsibility boundaries. If the data engineer, ML engineer, and service owner are not watching the same metrics, even a detected problem is slow to resolve. Defining role-specific responsibilities from day one of operations is critical.

- Data Engineer: input contracts, schema validation, intermediate artifact lineage management
- ML Engineer: quality filter thresholds, training impact analysis, rerun criteria ownership
- Service Owner: batch approve/halt decisions, incident communication, release criteria sign-off

With this separation, when an incident occurs the first question is "what criteria trigger a halt?" rather than "who should fix this?" Recovery time drops and recurrence rates for the same failure mode decrease.

## Answering the Opening Questions

- **What system properties are needed to unify multiple preparation stages into one production-ready pipeline?**
  - A production-ready pipeline in this article has per-`Stage` inputs, outputs, parameters, and manifests, and logs statistics like `rows_in`, `rows_out`, and `drop_rate`. Even with many stages, clear contracts and observability make results explainable when re-run.
- **How do DVC and stage fingerprints solve data versioning and idempotency together?**
  - `dvc add data/02_clean.parquet` pins artifact versions, while `fingerprint()` lets stages with unchanged inputs and parameters show `[skip] cached`. This answers both "what was used?" and "why wasn't it re-run?" simultaneously.
- **What operational value does an orchestrator like Airflow provide beyond simple scheduling?**
  - Fixing flow as `t1 >> t2 >> ... >> t6` in a DAG gives you retry, lineage UI, and the ability to re-execute only the failed stage. Unlike cron, you can immediately see which stage broke and where to resume.
<!-- toc:begin -->
## In this series

- [AI Data Preparation 101 (1/10): Why Data Preparation Determines Model Quality](./01-why-data-preparation-matters.md)
- [AI Data Preparation 101 (2/10): Source Data Collection and Cataloging](./02-source-data-collection-cataloging.md)
- [AI Data Preparation 101 (3/10): Cleaning and Deduplication](./03-cleaning-deduplication.md)
- [AI Data Preparation 101 (4/10): PII Detection and Anonymization for Training Data](./04-pii-detection-anonymization.md)
- [AI Data Preparation 101 (5/10): Tokenization and Chunking Strategies](./05-tokenization-chunking.md)
- [AI Data Preparation 101 (6/10): Quality Filtering - Heuristics and Classifiers](./06-quality-filtering.md)
- [AI Data Preparation 101 (7/10): Synthetic Data Generation - From Self-Instruct to Distillation](./07-synthetic-data-generation.md)
- [AI Data Preparation 101 (8/10): Data Augmentation - From EDA to Back-Translation](./08-data-augmentation.md)
- [AI Data Preparation 101 (9/10): Train/Eval/Test Splitting and Contamination Control](./09-train-eval-test-splitting.md)
- **Building a Production Data Pipeline (current)**

<!-- toc:end -->

## References

- [DVC - Data Version Control](https://dvc.org/doc)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [pandera - Statistical Data Testing](https://pandera.readthedocs.io/)
- [Great Expectations - Data Quality Pipeline](https://docs.greatexpectations.io/)

Tags: Data Pipelines, Production, DVC, Airflow, pandera, MLOps
