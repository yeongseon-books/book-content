
# Building a Production Data Pipeline

> AI Data Preparation 101 series (10/10)

---
## "How do I tie everything we learned into one pipeline?"

Episodes 1-9 covered cleaning, dedup, PII redaction, tokenization, chunking, quality filtering, synthesis, augmentation, and splitting. In production these stages must run automatically every week or every day. The final episode is a pipeline design that integrates all of them.

Four requirements for a production data pipeline:

1. **Reproducibility** - the same input must always produce the same output
2. **Versioning** - track dataset versions like git
3. **Observability** - measure per-stage statistics, drift, and failures
4. **Idempotency** - rerunning a stage twice must not change the result

## Architecture - a 6-stage pipeline

![Architecture - a 6-stage pipeline](https://yeongseon-books.github.io/book-public-assets/assets/ai-data-preparation-101/10/10-01-architecture-a-6-stage-pipeline.en.png)

*Architecture - a 6-stage pipeline*
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

## AI Data Preparation 101 series

- [Why Data Preparation Determines Model Quality](./01-why-data-preparation-matters.md)
- [Source Data Collection and Cataloging](./02-source-data-collection-cataloging.md)
- [Cleaning and Deduplication](./03-cleaning-deduplication.md)
- [PII Detection and Anonymization for Training Data](./04-pii-detection-anonymization.md)
- [Tokenization and Chunking Strategies](./05-tokenization-chunking.md)
- [Quality Filtering - Heuristics and Classifiers](./06-quality-filtering.md)
- [Synthetic Data Generation - From Self-Instruct to Distillation](./07-synthetic-data-generation.md)
- [Data Augmentation - From EDA to Back-Translation](./08-data-augmentation.md)
- [Train/Eval/Test Splitting and Contamination Control](./09-train-eval-test-splitting.md)
- **Building a Production Data Pipeline (current)**
## References

- [DVC - Data Version Control](https://dvc.org/doc)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [pandera - Statistical Data Testing](https://pandera.readthedocs.io/)
- [Great Expectations - Data Quality Pipeline](https://docs.greatexpectations.io/)

Tags: Data Pipelines, Production, DVC, Airflow, pandera, MLOps

---

© 2026 YeongseonBooks. All rights reserved.
