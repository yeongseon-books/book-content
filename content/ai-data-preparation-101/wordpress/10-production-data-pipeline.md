---
title: "바이브코딩을 위한 AI 데이터 준비 (10/10): 프로덕션 데이터 파이프라인"
series: ai-data-preparation-101
episode: 10
language: ko
tags:
- Data Pipelines
- Production
- DVC
- Airflow
- pandera
- MLOps
- 바이브코딩
targets:
  wordpress: true
---

# 바이브코딩을 위한 AI 데이터 준비 (10/10): 프로덕션 데이터 파이프라인

이 글은 **바이브코딩을 위한 AI 데이터 준비** 시리즈의 마지막 글입니다.

---

바이브코딩으로 정제, PII 처리, 품질 필터링, 분할을 각각 구현했는데 "다음 주에 새 데이터가 들어오면 어떻게 하나요?"라는 질문이 생깁니다. 노트북을 다시 위에서부터 실행하면 결과가 바뀔 수 있고, 어느 단계에서 얼마나 데이터가 줄었는지도 모릅니다.

개별 기법을 이해하는 것과 그것들을 매일 반복 가능한 시스템으로 묶는 것은 전혀 다른 문제입니다. 프로덕션 파이프라인에서 요구되는 것은 알고리즘이 아니라 시스템 속성입니다. 같은 입력이면 같은 출력이 나와야 하고, 어느 단계에서 몇 행이 떨어졌는지 관측 가능해야 합니다.

핵심 요구사항은 네 가지입니다. Reproducibility(같은 입력 = 같은 출력), Versioning(데이터셋 버전이 코드 커밋과 연결), Observability(단계별 통계와 실패 원인), Idempotency(같은 단계를 다시 실행해도 결과 불변).

> \"프로덕션 데이터 파이프라인은 스크립트 모음이 아니라, 각 단계가 입력·출력·버전·통계를 가진 재실행 가능한 계약들의 연결입니다.\"

## 이 글에서 다룰 질문

1. 여러 데이터 준비 단계를 하나의 파이프라인으로 묶으려면 어떤 시스템 속성이 필요한가요?
2. DVC와 stage fingerprint는 버전 관리와 idempotency를 어떻게 함께 해결하나요?
3. Airflow는 단순 스케줄링 외에 어떤 운영 가치를 주나요?
4. stage별 통계 수집으로 무엇을 감지할 수 있나요?
5. pandera schema validation이 왜 마지막 안전망인가요?

---

## 6단계 파이프라인 아키텍처

| 단계 | 기능 | 이전 에피소드 |
|------|------|--------------|
| 1. Ingest | 소스 데이터 수집 | Ep2 |
| 2. Clean/Dedup | 정제 + 중복 제거 | Ep3 |
| 3. PII | 개인정보 익명화 | Ep4 |
| 4. Quality | 품질 필터링 | Ep6 |
| 5. Chunk | 토크나이제이션/청킹 | Ep5 |
| 6. Split | 학습/평가/테스트 분할 | Ep9 |

## Before / After: 스크립트 묶음 vs 파이프라인

**Before (수동 스크립트 실행)**
```python
# 매번 노트북 위에서부터 실행
df = pd.read_json("raw.jsonl", lines=True)
df = clean(df)          # 어느 버전 clean 함수?
df = remove_pii(df)     # 파라미터가 바뀌었을 수 있음
df.to_parquet("train.parquet")
# 문제: 어느 입력으로 만들어진 파일인지 추적 불가
```

**After (fingerprint 기반 캐싱 파이프라인)**
```python
import yaml, hashlib, pathlib

class Stage:
    name: str
    inputs: list[str]
    params: dict

    def fingerprint(self) -> str:
        """입력 + 파라미터 + stage명으로 고유 식별자를 생성합니다."""
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
        self.execute()  # 서브클래스에서 구현
        self.write_manifest()
```

## 6단계 구현 (이전 에피소드 연결)

```python
import pandas as pd
from datetime import datetime

# Stage 1: Ingest
def stage_ingest(sources: list[str]) -> pd.DataFrame:
    dfs = [pd.read_json(s, lines=True) for s in sources]
    df = pd.concat(dfs, ignore_index=True)
    df["ingested_at"] = datetime.utcnow()
    return df

# Stage 2: 정제 + Dedup (Ep3)
def stage_clean(df: pd.DataFrame) -> pd.DataFrame:
    df["text"] = df["text"].str.strip().str.replace(r"\s+", " ", regex=True)
    df = df[df["text"].str.len() >= 50]
    df = df.drop_duplicates(subset=["text"])
    return df

# Stage 3: PII (Ep4)
def stage_pii(df: pd.DataFrame) -> pd.DataFrame:
    from presidio_analyzer import AnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine
    analyzer, anonymizer = AnalyzerEngine(), AnonymizerEngine()
    def redact(t: str) -> str:
        results = analyzer.analyze(text=t, language="en")
        return anonymizer.anonymize(text=t, analyzer_results=results).text
    df["text"] = df["text"].map(redact)
    return df

# Stage 4: 품질 (Ep6)
def stage_quality(df: pd.DataFrame) -> pd.DataFrame:
    def passes(t: str) -> bool:
        words = t.split()
        return 50 <= len(words) <= 100_000
    return df[df["text"].map(passes)]

# Stage 5: Chunk (Ep5)
def stage_chunk(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in df.iterrows():
        chunks = [r["text"][i:i+2000] for i in range(0, len(r["text"]), 1800)]
        for i, c in enumerate(chunks):
            rows.append({**r.to_dict(), "chunk_id": i, "text": c})
    return pd.DataFrame(rows)

# Stage 6: 분할 (Ep9)
def stage_split(df: pd.DataFrame, time_col: str = "ingested_at") -> dict:
    df = df.sort_values(time_col)
    n = len(df)
    return {
        "train": df.iloc[:int(n*0.8)],
        "val":   df.iloc[int(n*0.8):int(n*0.9)],
        "test":  df.iloc[int(n*0.9):],
    }
```

## Observability: stage 통계 수집

```python
import json, time

def with_stats(stage_fn):
    """stage 함수를 감싸 rows_in/out, drop_rate, duration을 기록합니다."""
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

# 모든 stage에 stats 수집 적용
stage_clean = with_stats(stage_clean)
stage_quality = with_stats(stage_quality)
```

`drop_rate`가 평소 0.1인데 갑자기 0.5가 되면 upstream source가 깨졌을 가능성이 높습니다.

## Airflow DAG 오케스트레이션

```python
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

Airflow의 가치는 cron 대체가 아닙니다. retry, stage별 재실행, lineage UI, 실패 알림이 핵심입니다.

## Schema Validation: 마지막 안전망

```python
import pandera as pa
from pandera.typing import Series

class TextSchema(pa.DataFrameModel):
    id: Series[str] = pa.Field(unique=True)
    text: Series[str] = pa.Field(str_length={"min_value": 1})
    source: Series[str]
    ingested_at: Series["datetime64[ns]"]

# 각 stage 진입 시점마다 검증
TextSchema.validate(df)
# 스키마 검증 실패 시 loud하게 실패 → 조용한 실패가 가장 비쌉니다
```

## DVC로 데이터 버전 관리

```bash
dvc init
dvc remote add -d s3 s3://my-bucket/datasets

# stage별 산출물 추적
dvc add data/02_clean.parquet
dvc add data/05_chunked.parquet
git add data/02_clean.parquet.dvc data/05_chunked.parquet.dvc
git commit -m "data: v2026.05.03"
dvc push
```

## 흔한 실수

| 실수 | 문제 | 해결 방법 |
|------|------|-----------||
| 단계만 순서대로 실행 | 스크립트 묶음일 뿐, 파이프라인 아님 | 입출력 계약, 버전, 통계 추가 |
| 캐시를 나중에 붙임 | 초기 설계와 idempotency가 연결 안 됨 | fingerprint 기반 캐시를 처음부터 |
| cron으로 스케줄링 | retry/lineage/재실행 불가 | Airflow 같은 오케스트레이터 사용 |
| schema validation 생략 | source drift가 조용히 파이프라인 통과 | pandera로 stage 진입 시 검증 |

## AI 팁

파이프라인 장애 발생 시 런북이 없으면 새벽에 로그를 처음부터 읽게 됩니다. 최소 런북은 다음 4단계로 구성하세요.

1. 입력 확인: 파일 개수, 용량, 인코딩이 평소 범위인지 확인
2. 원인 분리: 중복 제거율/PII 탐지/품질 필터 제거율 급등 여부 확인
3. 영향도 추정: 최종 샘플 수 감소율, 토큰 길이 변화율, 도메인 분포 변화
4. 재실행 기준: 입력 스냅샷과 설정 해시를 고정한 상태에서만 재실행

```python
# 배포 전 게이트 검사
def release_readiness(summary: dict) -> tuple[bool, list[str]]:
    issues = []
    if not summary.get("dataset_sha256"):
        issues.append("missing_dataset_sha256")
    if summary.get("duplicate_ratio", 1.0) > 0.10:
        issues.append("duplicate_ratio_too_high")
    if summary.get("null_ratio", 1.0) > 0.02:
        issues.append("null_ratio_too_high")
    if summary.get("contamination_ratio", 1.0) > 0.01:
        issues.append("contamination_ratio_too_high")
    if summary.get("human_reviewed_rows", 0) < 100:
        issues.append("insufficient_human_review")
    return len(issues) == 0, issues
```

## 체크리스트

- [ ] 모든 stage가 입력, 출력, 파라미터, fingerprint, manifest를 가진다
- [ ] DVC로 데이터 버전을 코드 커밋과 1:1로 연결했다
- [ ] stage별 rows_in/out, drop_rate, duration을 자동 수집한다
- [ ] PII redaction을 ingest 직후 초반 단계에 배치했다
- [ ] pandera schema validation과 stage 단위 재실행을 오케스트레이터에서 지원한다

## 처음 질문으로 돌아가기

**파이프라인에 필요한 시스템 속성은?** Reproducibility(동일 입력 = 동일 출력), Versioning(데이터 버전 + 코드 커밋 연결), Observability(단계별 통계), Idempotency(재실행 결과 불변) 네 가지입니다.

**DVC와 fingerprint caching은?** fingerprint가 같으면 stage를 건너뜁니다. 입력 파일 + stage명 + 파라미터를 모두 해시에 포함해야 idempotency와 캐싱을 동시에 보장합니다.

**Airflow의 운영 가치는?** retry, stage별 재실행, lineage UI가 핵심입니다. 어느 단계가 실패했는지 보이고 그 단계만 다시 돌릴 수 있어야 운영 비용이 줄어듭니다.

**stage 통계로 무엇을 감지하나요?** quality drop_rate가 평소 0.1에서 0.5로 급등하면 upstream source가 깨졌을 가능성이 높습니다. 후행 지표보다 단계별 제거율이 더 빠른 신호입니다.

**pandera schema validation이 마지막 안전망인 이유는?** source format 변경은 조용히 파이프라인을 통과합니다. stage 진입 시 schema 검증이 있어야 loud하게 실패해 문제를 빨리 잡을 수 있습니다.

## 정리

프로덕션 데이터 파이프라인의 핵심은 단계를 모아 두는 것이 아니라, 각 단계가 버전·캐시·통계를 가진 재실행 가능한 계약이 되게 만드는 것입니다. DVC, fingerprint caching, Airflow, stats logging, pandera는 reproducibility와 observability를 시스템 차원에서 보장하는 수단입니다.

이로써 raw 데이터 수집부터 프로덕션 파이프라인까지 10편의 시리즈가 마무리됩니다.

## 참고 자료

- [AI 데이터 준비 원문: 프로덕션 데이터 파이프라인](../ko/10-production-data-pipeline.md)
- [DVC - Data Version Control](https://dvc.org/doc)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [pandera - Statistical Data Testing](https://pandera.readthedocs.io/)

---

<!-- toc:begin -->
## 시리즈 목차

1. [바이브코딩을 위한 AI 데이터 준비 (1/10): 데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
2. [바이브코딩을 위한 AI 데이터 준비 (2/10): 원본 데이터 수집과 카탈로깅](./02-source-data-collection-cataloging.md)
3. [바이브코딩을 위한 AI 데이터 준비 (3/10): 데이터 정제와 중복 제거](./03-cleaning-deduplication.md)
4. [바이브코딩을 위한 AI 데이터 준비 (4/10): PII 탐지와 익명화](./04-pii-detection-anonymization.md)
5. [바이브코딩을 위한 AI 데이터 준비 (5/10): Tokenization과 Chunking](./05-tokenization-chunking.md)
6. [바이브코딩을 위한 AI 데이터 준비 (6/10): 데이터 품질 필터링](./06-quality-filtering.md)
7. [바이브코딩을 위한 AI 데이터 준비 (7/10): 합성 데이터 생성](./07-synthetic-data-generation.md)
8. [바이브코딩을 위한 AI 데이터 준비 (8/10): 데이터 증강 기법](./08-data-augmentation.md)
9. [바이브코딩을 위한 AI 데이터 준비 (9/10): 학습/평가/테스트 분할](./09-train-eval-test-splitting.md)
10. **바이브코딩을 위한 AI 데이터 준비 (10/10): 프로덕션 데이터 파이프라인 (현재 글)**
<!-- toc:end -->

Tags: Data Pipelines, Production, DVC, Airflow, pandera, MLOps, 바이브코딩
