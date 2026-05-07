---
series: data-science-101
episode: 3
title: 데이터 수집
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - DataScience
  - DataCollection
  - API
  - Database
  - Beginner
seo_description: 파일, API, 데이터베이스, 로그까지 데이터를 모으는 4가지 경로와 수집 단계의 흔한 실수 정리
last_reviewed: '2026-05-04'
---

# 데이터 수집

> Data Science 101 시리즈 (3/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: *분석에 필요한 데이터* 는 *어디서, 어떻게* 가져올까요? *원본* 과 *사본* 은 어떻게 구분할까요?

> *모든 분석의 시작은 *어디서 왔는지* 를 적는 것이다.*

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *4가지 데이터 출처*: 파일, API, DB, 로그
- *원본/사본/스냅샷* 의 차이
- *데이터 사전 (data dictionary)* 의 역할
- 5단계 수집 실습
- 흔한 함정 5가지

## 왜 중요한가

수집 단계의 *기록 누락* 은 *분석의 마지막* 까지 따라옵니다. *어디서 왔는지* 를 적는 *사소한 습관* 이 *재현성* 을 만듭니다.

> *추적 가능* 한 데이터만 *신뢰 가능* 하다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    File["File / CSV"] --> Stage["Staging"]
    API["API"] --> Stage
    DB["Database"] --> Stage
    Log["Event Log"] --> Stage
    Stage --> Analysis["Analysis"]
```

## 핵심 용어 정리

- **Source of Truth**: *원본 데이터* 의 *최종 출처*.
- **Snapshot**: 특정 시점의 *고정된 사본*.
- **Schema**: 컬럼/타입의 *형식 정의*.
- **Data Dictionary**: 컬럼의 *의미* 를 *문서화* 한 표.
- **Provenance**: 데이터의 *출처와 이력*.

## Before/After

**Before**: 동료가 보내준 *엑셀 파일* 로 분석. *언제* 받았는지 *어디서* 왔는지 *모른다*.

**After**: 동일 데이터를 *DB 에서 SQL 로* 추출, *해시 + 시각* 을 *기록*. *몇 달 뒤* 에도 *재현 가능*.

## 실습: 5단계 수집

### 1단계 — 파일에서

```python
import pandas as pd
df = pd.read_csv("data/users-2026-05-04.csv")
print(df.shape)
```

### 2단계 — API 에서

```python
import requests
resp = requests.get("https://api.example.com/users", timeout=10)
resp.raise_for_status()
users = resp.json()
```

### 3단계 — DB 에서

```python
from sqlalchemy import create_engine
engine = create_engine("postgresql://user:pass@host/db")
df = pd.read_sql("SELECT id, signup_at FROM users WHERE signup_at > '2026-01-01'", engine)
```

### 4단계 — 로그/이벤트에서

```python
# 한 줄당 JSON 인 이벤트 로그
import json
with open("events.jsonl") as f:
    events = [json.loads(line) for line in f]
```

### 5단계 — 출처 기록

```python
import hashlib, datetime
meta = {
    "source": "postgres://prod-replica/users",
    "fetched_at": datetime.datetime.utcnow().isoformat(),
    "row_count": len(df),
    "sha256": hashlib.sha256(pd.util.hash_pandas_object(df).values.tobytes()).hexdigest()[:16],
}
print(meta)
```

## 이 코드에서 주목할 점

- *출처* 와 *시각* 을 *항상* 함께 적는다.
- *해시* 는 *데이터가 바뀌었는지* 를 *값싸게* 알려준다.
- *원본* 은 *수정하지 않는다*. 변경은 *staging* 에서.

## 자주 하는 실수 5가지

1. ***엑셀* 로 *원본* 을 덮어쓴다.** 되돌릴 수 없다.
2. **API 의 *rate limit* 을 무시.** 차단됨.
3. ***스키마* 를 *문서* 에 적지 않는다.** 컬럼 의미가 사라짐.
4. ***로그 형식 변경* 을 *추적* 하지 않는다.** 분석이 *조용히* 깨진다.
5. ***개인 PC* 에 *민감 데이터* 를 저장.** 보안 사고.

## 실무에서는 이렇게 쓰입니다

데이터팀은 *수집 스크립트* 를 *Airflow / dbt* 로 돌립니다. 모든 *load* 에는 *load_id, fetched_at, source* 가 *컬럼* 으로 붙습니다. *데이터 사전* 은 *Notion / Confluence* 에 두고 *PR 마다* 갱신합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- *원본은 절대 수정* 하지 않는다.
- *출처/시각/해시* 를 *습관* 처럼 적는다.
- *스키마 변화* 를 *경보* 로 잡는다.
- *민감 데이터* 는 *마스킹* 후 분석.
- *데이터 사전* 이 *최고의 문서*.

## 체크리스트

- [ ] *4가지 출처* 의 차이를 안다.
- [ ] *Snapshot* 의 의미를 안다.
- [ ] *데이터 사전* 을 작성할 수 있다.
- [ ] *Provenance* 를 *기록* 한다.

## 연습 문제

1. *공개 API* 한 개를 골라 *데이터를 수집* 하고 *메타* 를 적어 보세요.
2. *원본 → staging → analysis* 흐름을 *그림* 으로 그려 보세요.
3. *스키마가 바뀐 사례* 를 *문서* 로 정리해 보세요.

## 정리 및 다음 단계

수집 단계는 *기록* 의 단계입니다. 다음 글에서는 모은 데이터를 *깨끗하게 정제* 하는 법을 살펴봅니다.

<!-- toc:begin -->
- [Data Science란 무엇인가?](./01-what-is-data-science.md)
- [문제를 데이터 문제로 바꾸기](./02-problem-to-data-problem.md)
- **데이터 수집 (현재 글)**
- 데이터 정제 (예정)
- 탐색적 데이터 분석 (예정)
- 시각화 (예정)
- 모델링 (예정)
- 평가 (예정)
- 결과 해석 (예정)
- 데이터 프로젝트 전체 흐름 (예정)
<!-- toc:end -->

## 참고 자료

- [requests — Quickstart](https://requests.readthedocs.io/en/latest/user/quickstart/)
- [pandas — IO Tools](https://pandas.pydata.org/docs/user_guide/io.html)
- [Airflow — Concepts](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html)
- [Google — Data Validation in ML Pipelines](https://research.google/pubs/data-validation-for-machine-learning/)

Tags: DataScience, DataCollection, API, Database, Beginner
