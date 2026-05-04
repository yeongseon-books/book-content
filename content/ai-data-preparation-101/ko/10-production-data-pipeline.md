---
title: 프로덕션 데이터 파이프라인 구축
series: ai-data-preparation-101
episode: 10
language: ko
status: content-ready
targets:
  tistory: true
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
last_reviewed: '2026-05-03'
seo_description: Ep1~9에서 cleaning, dedup, PII redaction, tokenization, chunking, quality…
---

# 프로덕션 데이터 파이프라인 구축

> AI Data Preparation 101 시리즈 (10/10)

---
## "지금까지 배운 걸 어떻게 한 pipeline으로 묶나요?"

Ep1~9에서 cleaning, dedup, PII redaction, tokenization, chunking, quality filtering, synthesis, augmentation, splitting을 다뤘습니다. production에서 이 단계들을 매주 또는 매일 자동으로 돌려야 합니다. 마지막 편은 모든 단계를 통합한 pipeline 설계입니다.

production data pipeline의 4가지 요구사항:

1. **Reproducibility** — 같은 input은 항상 같은 output을 만들어야 함
2. **Versioning** — dataset의 version을 git처럼 추적
3. **Observability** — stage별 통계, drift, failure를 측정
4. **Idempotency** — 같은 stage를 두 번 돌려도 결과가 변하지 않아야 함

## 아키텍처 — 6 stage pipeline

![아키텍처 — 6 stage pipeline](../../../assets/ai-data-preparation-101/10/10-01-6-stage-pipeline.ko.png)
각 stage는 input parquet과 output parquet, manifest를 가집니다. manifest에는 input fingerprint, code version, parameters가 모두 기록됩니다.

## DVC로 dataset versioning

dataset을 git처럼 version 관리합니다. 코드 commit과 data version이 1:1로 묶입니다.

```bash
# pip install dvc
dvc init
dvc remote add -d s3 s3://my-bucket/datasets

# Stage별 산출물 추적
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
        self.execute()  # subclass에서 구현
        self.write_manifest()
```

`fingerprint`가 같으면 stage를 재실행하지 않습니다. idempotency와 caching이 동시에 해결됩니다.

## Stage별 구현 예 — 통합 pipeline

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
    from typing import Callable
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

## Pipeline orchestration — Airflow 예

production은 Airflow, Prefect, Dagster 중 하나를 씁니다. Airflow가 가장 보편적입니다.

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

Airflow는 retry, scheduling, lineage UI를 제공합니다. failed stage만 재실행할 수 있어 cost를 아낍니다.

## Observability — stage 통계 수집

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

stage별 drop_rate를 시계열로 plot하면 source distribution drift를 즉시 감지할 수 있습니다. 평소 0.1이던 quality drop_rate가 0.5로 뛰면 source가 깨졌다는 신호입니다.

## Schema validation — Great Expectations / pandera

input/output schema가 변하면 pipeline은 silent하게 깨집니다. schema check가 마지막 안전망입니다.

```python
# pip install pandera
import pandera as pa
from pandera.typing import Series

class TextSchema(pa.DataFrameModel):
    id: Series[str] = pa.Field(unique=True)
    text: Series[str] = pa.Field(str_length={"min_value": 1})
    source: Series[str]
    ingested_at: Series["datetime64[ns]"]

# 모든 stage 입력에서 검증
TextSchema.validate(df)
```

schema가 깨지면 stage가 fail합니다. silently 잘못된 dataset을 만드는 것보다 나은 선택입니다.

## 흔한 실수 5가지

1. **Caching 없이 매번 전체 파이프라인 재실행**: cost와 시간이 폭발합니다. fingerprint 기반 stage caching이 필수입니다.
2. **Schema validation 생략**: source format이 바뀌어도 silent하게 pipeline이 통과해 잘못된 dataset이 production에 배포됩니다.
3. **Dataset version과 code commit을 분리**: 버그 발생 시 어떤 dataset version으로 학습했는지 추적 불가. DVC + git tag 조합이 표준입니다.
4. **stage 통계 수집 안 함**: drift 감지가 늦어지고 model 품질 저하의 원인 분석이 불가합니다.
5. **PII redaction을 마지막에**: 한 번이라도 PII가 raw로 disk에 떨어지면 compliance 위반입니다. ingest 직후 또는 clean 직후에 합니다.

## 핵심 요약

- Production data pipeline은 ingest -> clean/dedup -> PII -> quality -> tokenize/chunk -> split의 6 stage입니다.
- DVC로 dataset versioning을 git commit과 1:1 매핑합니다.
- Stage 단위 fingerprint caching으로 idempotency와 cost를 동시에 잡습니다.
- Airflow / Prefect / Dagster로 schedule, retry, lineage를 관리합니다.
- 모든 stage에서 drop_rate, duration, schema 통계를 수집해 drift를 모니터링합니다.
- PII redaction은 ingest 직후 단계에 배치합니다.

이 시리즈는 여기까지입니다. Ep1의 GIGO에서 시작해 production pipeline까지 왔습니다. 다음 시리즈는 multimodal data 준비, 또는 model evaluation으로 이어집니다.

---

<!-- toc:begin -->
## AI Data Preparation 101 시리즈

- [데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
- [원본 데이터 수집과 카탈로깅](./02-source-data-collection-cataloging.md)
- [데이터 정제와 중복 제거](./03-cleaning-deduplication.md)
- [학습 데이터 PII 탐지와 익명화](./04-pii-detection-anonymization.md)
- [Tokenization과 Chunking 전략](./05-tokenization-chunking.md)
- [데이터 품질 필터링 — Heuristic과 Classifier](./06-quality-filtering.md)
- [합성 데이터 생성 — Self-Instruct부터 Distillation까지](./07-synthetic-data-generation.md)
- [데이터 증강 기법 — EDA부터 Back-Translation까지](./08-data-augmentation.md)
- [학습/평가/테스트 분할과 Contamination 통제](./09-train-eval-test-splitting.md)
- **프로덕션 데이터 파이프라인 구축 (현재 글)**
<!-- toc:end -->

## 참고 자료

- [DVC - Data Version Control](https://dvc.org/doc)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [pandera - Statistical Data Testing](https://pandera.readthedocs.io/)
- [Great Expectations - Data Quality Pipeline](https://docs.greatexpectations.io/)

Tags: Data Pipelines, Production, DVC, Airflow, pandera, MLOps
