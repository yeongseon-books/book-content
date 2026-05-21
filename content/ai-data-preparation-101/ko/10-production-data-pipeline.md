---
title: "AI Data Preparation 101 (10/10): 프로덕션 데이터 파이프라인 구축"

series: ai-data-preparation-101

episode: 10

language: ko

status: publish-ready

targets:

  tistory: true

  medium: false

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

seo_description: Ep1~9에서 cleaning, dedup, PII redaction, tokenization, chunking, quality…
---

# AI Data Preparation 101 (10/10): 프로덕션 데이터 파이프라인 구축

이 글은 AI Data Preparation 101 시리즈의 마지막 글입니다.


정제, 중복 제거, PII 처리, 토큰화, 품질 필터링, 분할을 각각 이해하는 것과 그것들을 프로덕션에서 매일 반복 가능한 시스템으로 묶는 것은 전혀 다른 문제입니다. 운영의 어려움은 개별 기법을 모르는 데서보다, 그 기법들을 다시 돌려도 같은 결과를 내는 파이프라인으로 만드는 데서 더 자주 나타납니다.

이 단계에서 요구되는 것은 알고리즘이 아니라 시스템 속성입니다. 같은 입력이면 같은 출력이 나와야 하고, 어느 단계에서 몇 행이 떨어졌는지 관측 가능해야 하며, 중간 산출물과 데이터 버전이 코드 커밋과 연결돼야 합니다.

좋은 팀은 모델 학습보다 먼저 데이터 파이프라인의 재실행 가능성과 관측성을 검증합니다. 모델은 바뀌어도 파이프라인은 계속 남기 때문입니다.

이 글은 AI Data Preparation 101 시리즈의 마지막 글입니다. 여기서는 앞선 아홉 편의 단계를 하나의 프로덕션 데이터 파이프라인으로 묶기 위해 필요한 버전 관리, 캐싱, 오케스트레이션, 관측성, 스키마 검증을 정리하겠습니다.

프로덕션 데이터 파이프라인은 결국 데이터셋을 코드처럼 다루는 문제입니다. 버전, 캐시, lineage, schema validation, scheduler, retry가 모두 필요합니다. 한 단계라도 임시 스크립트로 남겨 두면 파이프라인 전체의 신뢰도가 떨어집니다.


![Architecture - a 6-stage pipeline](https://yeongseon-books.github.io/book-public-assets/assets/ai-data-preparation-101/10/10-01-6-stage-pipeline.ko.png)
*Architecture - a 6-stage pipeline*
> 프로덕션 데이터 파이프라인 구축의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- 여러 데이터 준비 단계를 실제 운영 가능한 하나의 파이프라인으로 묶으려면 어떤 시스템 속성이 필요할까요?
- DVC와 stage fingerprint는 데이터 버전 관리와 idempotency를 어떻게 함께 해결할까요?
- Airflow 같은 오케스트레이터는 단순 스케줄링 외에 어떤 운영 가치를 줄까요?

## 왜 이 글이 중요한가

프로덕션 파이프라인을 잘 만들면 데이터셋 재생성, 버그 재현, drift 분석, 비용 절감이 모두 쉬워집니다. 특히 모델이 여러 개로 늘어날수록 재사용 가능한 데이터 파이프라인은 조직의 핵심 자산이 됩니다.

반대로 매번 수동 스크립트를 이어 붙이는 방식은 같은 입력에서도 결과가 달라지고, 어느 단계가 원인인지 추적하기 어려우며, PII나 schema 변화 같은 사고를 조기에 잡지 못합니다. 배포 직전에만 보이는 문제들이 늘어납니다.

이 글은 데이터 준비를 마무리하는 마지막 편으로서, 개별 기법을 운영 가능한 시스템으로 승격시키는 기준을 제시합니다. 결국 데이터 품질은 파이프라인 품질과 분리할 수 없습니다.

## 핵심 관점

프로덕션 파이프라인의 핵심은 단계가 많다는 사실이 아닙니다. 각 단계가 입력, 출력, 파라미터, 코드 버전, fingerprint를 명시적으로 갖고, 다시 실행해도 같은 결과를 내는 계약을 가진다는 점이 중요합니다.

이 계약이 있으면 캐시를 안전하게 쓸 수 있고, stage 단위 재실행과 롤백이 가능해집니다. 반대로 계약이 없으면 캐시도 믿기 어렵고, “다시 돌려 보자”가 사실상 다른 결과를 만드는 행위가 됩니다.

운영에서 pipeline orchestration, stats logging, schema validation은 부가 기능이 아닙니다. reproducibility와 observability를 시스템 차원에서 보장하는 핵심 장치입니다.

> 프로덕션 데이터 파이프라인은 스크립트 모음이 아니라, 각 단계가 입력·출력·버전·통계를 가진 재실행 가능한 계약들의 연결입니다.

## 핵심 개념

### 프로덕션 데이터 파이프라인의 네 가지 요구사항

마지막 편에서는 앞선 단계를 하나의 시스템으로 묶습니다. 핵심 요구사항은 네 가지입니다.

1. **Reproducibility**: 같은 입력은 항상 같은 출력이 나와야 합니다.

2. **Versioning**: 데이터셋 버전이 코드 커밋과 연결돼야 합니다.

3. **Observability**: stage별 통계와 실패 원인을 볼 수 있어야 합니다.

4. **Idempotency**: 같은 stage를 다시 실행해도 결과가 바뀌지 않아야 합니다.

### 아키텍처는 여섯 단계 파이프라인으로 정리할 수 있습니다

각 stage는 input/output parquet와 manifest를 갖습니다. manifest에 fingerprint, 코드 버전, 파라미터를 남겨 두면 데이터셋을 파일이 아니라 재현 가능한 산출물로 다룰 수 있습니다.

### DVC와 fingerprint caching으로 버전과 재실행을 묶습니다

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

`fingerprint`가 같으면 stage를 건너뛰는 방식은 캐시와 idempotency를 동시에 해결합니다. 중요한 점은 입력 파일, stage 이름, 파라미터를 모두 fingerprint에 넣는 것입니다.

### Stage 구현은 이전 편의 개념을 그대로 연결합니다

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

# Stage 4: 품질 (Ep6)
def stage_quality(df: pd.DataFrame) -> pd.DataFrame:
    def passes(t: str) -> bool:
        words = t.split()
        return 50 <= len(words) <= 100_000
    return df[df["text"].map(passes)]

# Stage 5: Tokenize/Chunk (Ep5)
def stage_chunk(df: pd.DataFrame, max_tokens: int = 500) -> pd.DataFrame:
    rows = []
    for _, r in df.iterrows():
        # Ep5의 recursive_chunk 사용
        chunks = [r["text"][i:i+2000] for i in range(0, len(r["text"]), 1800)]
        for i, c in enumerate(chunks):
            rows.append({**r.to_dict(), "chunk_id": i, "text": c})
    return pd.DataFrame(rows)

# Stage 6: 분할 + 버전 관리 (Ep9)
def stage_split(df: pd.DataFrame, time_col: str = "ingested_at") -> dict:
    df = df.sort_values(time_col)
    n = len(df)
    return {
        "train": df.iloc[:int(n*0.8)],
        "val":   df.iloc[int(n*0.8):int(n*0.9)],
        "test":  df.iloc[int(n*0.9):],
    }
```

여기서 보이는 ingest -> clean/dedup -> PII -> quality -> tokenize/chunk -> split 순서는 임의가 아닙니다. PII를 늦게 처리하면 raw 민감정보가 더 많은 산출물에 퍼지고, split을 너무 일찍 하면 이후 변환 단계에서 분할 무결성을 다시 관리해야 합니다.

### 오케스트레이션은 Airflow 같은 도구에 맡깁니다

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

Airflow의 가치는 단순 cron 대체가 아닙니다. retry, scheduling, lineage UI, stage별 재실행이 가능하다는 점이 큽니다. 어느 단계가 실패했는지 보이고, 실패한 단계만 다시 돌릴 수 있어야 운영 비용이 줄어듭니다.

### observability는 stage 통계로 시작합니다

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

`drop_rate`, `duration_s`, `rows_in/out`만 꾸준히 남겨도 source drift를 빨리 감지할 수 있습니다. 예를 들어 평소 0.1이던 quality drop rate가 갑자기 0.5가 되면 upstream source가 깨졌을 가능성이 높습니다.

### schema validation은 마지막 안전망입니다

```python
# pip install pandera
import pandera as pa
from pandera.typing import Series

class TextSchema(pa.DataFrameModel):
    id: Series[str] = pa.Field(unique=True)
    text: Series[str] = pa.Field(str_length={"min_value": 1})
    source: Series[str]
    ingested_at: Series["datetime64[ns]"]

# 각 stage 진입 시점마다 검증
TextSchema.validate(df)
```

스키마 체크가 없으면 source format 변경이 조용히 파이프라인을 통과합니다. stage가 loud하게 실패하는 편이 훨씬 낫습니다. 데이터 파이프라인에서 조용한 실패는 대개 가장 비싼 실패입니다.

## 흔히 헷갈리는 지점

- **단계를 순서대로 실행만 하면 파이프라인입니다**: 입출력 계약, 버전, 캐시, 통계가 없으면 단지 스크립트 묶음일 뿐입니다.
- **캐시는 나중에 속도 문제가 생기면 붙이면 됩니다**: fingerprint 기반 캐시는 idempotency와 재현성 설계와 연결돼 있어 초기에 함께 들어가야 합니다.
- **스케줄러는 cron이면 충분합니다**: retry, lineage, stage별 재실행, 상태 가시성이 없으면 운영 비용이 크게 늘어납니다.
- **schema validation이 없어도 테스트 데이터 몇 건이면 충분합니다**: 실제 source format drift는 조용히 들어오므로 자동 검증이 마지막 안전망입니다.

## 운영 체크리스트

- [ ] 모든 stage가 입력, 출력, 파라미터, fingerprint, manifest를 가진다
- [ ] DVC 또는 동급 도구로 데이터 버전을 코드 커밋과 1:1로 연결했다
- [ ] stage별 rows_in/out, drop_rate, duration, timestamp를 자동 수집한다
- [ ] PII redaction을 ingest 직후 초반 단계에 배치했다
- [ ] schema validation과 stage 단위 재실행을 오케스트레이터 수준에서 지원한다

## 정리

프로덕션 데이터 파이프라인의 핵심은 여러 단계를 모아 두는 것이 아니라, 각 단계가 버전·캐시·통계를 가진 재실행 가능한 계약이 되게 만드는 것입니다. 그래야 데이터셋을 코드처럼 다룰 수 있습니다.

DVC, fingerprint caching, Airflow, stats logging, pandera 같은 도구는 개별 기능이 아니라 reproducibility와 observability를 붙잡기 위한 수단입니다. 이 장치들이 있어야 정제, PII 처리, 토큰화, 분할이 운영에서 계속 살아남습니다.

이로써 시리즈는 raw 데이터에서 시작해 프로덕션 파이프라인까지 닫혔습니다. 이후 실제 모델 학습과 평가 시리즈를 볼 때도, 기반 데이터 파이프라인을 어떻게 설계했는지가 결과 해석의 출발점이라는 사실은 그대로 유지됩니다.

## 프로덕션 파이프라인을 운영 체계로 바꾸는 설계 원칙

파이프라인을 구성하는 단계가 많아질수록, 품질은 개별 단계의 성능보다 단계 사이 계약의 명확성에서 갈립니다. 특히 정제 파이프라인은 "한 번 잘 돌았다"보다 "다시 돌려도 같은 결과를 낸다"가 훨씬 중요합니다. 이 관점에서 운영 설계는 크게 다섯 축으로 정리할 수 있습니다.

### 1) 입력 계약을 먼저 고정합니다

입력 데이터의 파일 포맷, 필수 컬럼, null 허용 정책, 시간대 기준, 인코딩을 계약으로 문서화해야 합니다. 예를 들어 이벤트 로그의 `event_time`이 UTC인지 로컬 시간인지가 불분명하면, 분할 기준이 매일 달라지고 train/validation leakage가 조용히 발생합니다. 파이프라인 시작 단계에서 스키마 검증을 통과하지 못한 배치는 즉시 중단시키는 편이 장기적으로 더 안전합니다.

### 2) 단계별 산출물에 식별자를 부여합니다

`raw -> normalized -> deduped -> pii-redacted -> filtered -> tokenized`처럼 중간 산출물을 남길 때, 단순 파일명 대신 데이터 버전 식별자를 붙입니다. 운영에서는 "어제 모델이 왜 달라졌는가"를 반드시 추적해야 하므로, 최소한 다음 세 가지가 연결돼야 합니다.

- 데이터 버전 ID
- 파이프라인 코드 커밋 SHA
- 실행 시점의 설정 파일 해시

이 연결이 있으면 재현 실험, 회귀 분석, 롤백 판단이 빠르게 끝납니다. 반대로 이 연결이 없으면 같은 데이터를 다시 만들 수 없어서, 장애 복구가 아니라 추측 회의만 길어집니다.

### 3) 품질 지표를 단계별로 분해해서 봅니다

최종 토큰 수, 학습 손실 같은 후행 지표만 보면 이미 늦습니다. 각 단계에서 제거율과 분포 변화를 먼저 봐야 원인을 좁힐 수 있습니다. 예를 들어 품질 필터 단계 제거율이 평소 18%인데 오늘 43%라면, 모델 문제 이전에 입력 분포 변화나 규칙 과민 반응을 의심해야 합니다.

실무에서 자주 쓰는 최소 관측 지표는 다음과 같습니다.

- 스키마 검증 실패 건수
- 중복 제거율(문서 단위, 문장 단위)
- PII 탐지 건수(유형별)
- 품질 필터 제거율(규칙별)
- 토큰 길이 분포(p50, p90, p99)

### 4) 실패를 예외가 아니라 기본 경로로 다룹니다

운영 배치는 반드시 실패합니다. 문제는 실패 자체가 아니라, 실패했을 때 팀이 무엇을 즉시 알 수 있느냐입니다. 실패 알림에는 "어느 단계에서", "어떤 입력 배치에서", "이전 성공 실행과 무엇이 다른지"가 함께 들어가야 합니다. 단순히 "배치 실패"만 보내면 결국 담당자가 로그를 처음부터 다시 읽게 됩니다.

### 5) 배치 성공 조건을 명시합니다

성공 여부를 종료 코드 하나로만 판단하면 품질 저하를 놓치기 쉽습니다. 예를 들어 모든 단계가 정상 종료됐더라도, 최종 usable sample 수가 기준치보다 30% 낮으면 학습 품질에 심각한 영향을 줄 수 있습니다. 따라서 기술적 성공과 데이터 품질 성공을 분리해서 선언해야 합니다.

## 장애 대응 런북 예시

운영 파이프라인은 문서가 아니라 런북으로 유지돼야 합니다. 런북은 "무슨 원리인가"보다 "새벽 2시에 어떤 순서로 확인할 것인가"를 답해야 합니다. 아래는 데이터 준비 파이프라인에 바로 적용할 수 있는 최소 런북 예시입니다.

### 단계 1. 입력 계층 확인

- 신규 파일 개수와 총 용량이 평소 범위인지 확인합니다.
- 파일 인코딩과 압축 포맷이 기존과 동일한지 확인합니다.
- 파티션 경로(날짜, 리전, 고객사)가 누락되지 않았는지 점검합니다.

### 단계 2. 품질 저하 원인 분리

- 중복 제거율 급등: 업스트림 재전송 또는 dedup key 변경 가능성을 점검합니다.
- PII 탐지 급등: 정규식/NER 룰 변경 여부를 확인합니다.
- 품질 필터 급등: 언어 분포 변화 또는 HTML 정제 규칙 과적용을 확인합니다.

### 단계 3. 학습 영향도 추정

- 최종 샘플 수 감소율
- 평균 토큰 길이 변화율
- 도메인 분포 변화(예: support 40% -> 12%)

이 세 항목으로 "즉시 재실행"과 "조건부 진행"을 분리합니다. 영향도가 크면 배치를 중지하고 원인 수정 후 재실행합니다.

### 단계 4. 재실행 기준

재실행은 단순 반복이 아니라 동일 조건 보장입니다. 입력 스냅샷과 설정 해시를 고정한 상태에서 재실행해야 합니다. 그렇지 않으면 "복구 성공"처럼 보여도 실제로는 다른 데이터를 만든 것이 됩니다.

## 확장 시나리오: 멀티 도메인 데이터 파이프라인

단일 도메인에서 파이프라인이 안정화되면 보통 여러 도메인(제품 문서, 고객 지원 대화, 코드 주석, 정책 문서)을 함께 넣고 싶어집니다. 이때 가장 흔한 실수는 도메인별 품질 기준을 하나로 합치는 것입니다. 도메인마다 문장 길이, 구조, 허용 잡음 수준이 다르므로, 필터와 샘플링 전략도 분리해야 합니다.

실무에서는 다음 전략이 효과적입니다.

- 도메인별 전처리 규칙을 분리하되, 공통 인터페이스를 유지합니다.
- 도메인별 품질 지표 임계값을 따로 설정합니다.
- 최종 병합 직전에 도메인 가중치 샘플링을 적용합니다.
- 모델 평가도 도메인별 검증 세트로 분리해 회귀를 추적합니다.

이 구조를 쓰면 데이터 볼륨이 늘어나도 파이프라인 복잡도를 통제할 수 있고, 특정 도메인 장애가 전체 파이프라인 중단으로 번지는 것을 막을 수 있습니다.

## 팀 운영을 위한 역할 분리와 책임 경계

파이프라인 품질이 흔들릴 때 가장 자주 놓치는 부분은 기술이 아니라 책임 경계입니다. 데이터 엔지니어, ML 엔지니어, 서비스 오너가 같은 지표를 보지 않으면 문제를 발견해도 해결 속도가 느려집니다. 그래서 운영 초기부터 역할별 책임을 명시하는 것이 중요합니다.

- 데이터 엔지니어: 입력 계약, 스키마 검증, 중간 산출물 계보 관리
- ML 엔지니어: 품질 필터 기준, 학습 영향도 분석, 재실행 기준 관리
- 서비스 오너: 배치 승인/중단 결정, 장애 커뮤니케이션, 릴리스 기준 확정

이렇게 분리하면 장애가 생겼을 때 "누가 고칠까"보다 "어떤 기준으로 중단할까"를 먼저 결정할 수 있습니다. 결과적으로 복구 시간이 줄고, 같은 장애의 재발률도 낮아집니다.

## 처음 질문으로 돌아가기

- **여러 데이터 준비 단계를 실제 운영 가능한 하나의 파이프라인으로 묶으려면 어떤 시스템 속성이 필요할까요?**
  - 본문의 기준은 프로덕션 데이터 파이프라인 구축를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **DVC와 stage fingerprint는 데이터 버전 관리와 idempotency를 어떻게 함께 해결할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Airflow 같은 오케스트레이터는 단순 스케줄링 외에 어떤 운영 가치를 줄까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI Data Preparation 101 (1/10): 데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
- [AI Data Preparation 101 (2/10): 원본 데이터 수집과 카탈로깅](./02-source-data-collection-cataloging.md)
- [AI Data Preparation 101 (3/10): 데이터 정제와 중복 제거](./03-cleaning-deduplication.md)
- [AI Data Preparation 101 (4/10): 학습 데이터 PII 탐지와 익명화](./04-pii-detection-anonymization.md)
- [AI Data Preparation 101 (5/10): Tokenization과 Chunking 전략](./05-tokenization-chunking.md)
- [AI Data Preparation 101 (6/10): 데이터 품질 필터링 — Heuristic과 Classifier](./06-quality-filtering.md)
- [AI Data Preparation 101 (7/10): 합성 데이터 생성 — Self-Instruct부터 Distillation까지](./07-synthetic-data-generation.md)
- [AI Data Preparation 101 (8/10): 데이터 증강 기법 — EDA부터 Back-Translation까지](./08-data-augmentation.md)
- [AI Data Preparation 101 (9/10): 학습/평가/테스트 분할과 Contamination 통제](./09-train-eval-test-splitting.md)
- **프로덕션 데이터 파이프라인 구축 (현재 글)**

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [DVC - Data Version Control](https://dvc.org/doc)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [pandera - Statistical Data Testing](https://pandera.readthedocs.io/)
- [Great Expectations - Data Quality Pipeline](https://docs.greatexpectations.io/)

### 관련 시리즈
- [LLM API 프로덕션 101 — 캐싱 전략 — 비용과 지연 시간 줄이기](../../llm-api-production-101/ko/04-caching-strategies.md)
- [AI Evaluation 101 — LLM-as-Judge — 모델로 모델을 평가하기](../../ai-evaluation-101/ko/04-llm-as-judge.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/ai-data-preparation-101/ko/10-production-data-pipeline)

Tags: Data Pipelines, Production, DVC, Airflow, pandera, MLOps