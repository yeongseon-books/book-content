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


## 이 글에서 다룰 문제

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

## 체크리스트

- [ ] *4가지 출처* 의 차이를 안다.
- [ ] *Snapshot* 의 의미를 안다.
- [ ] *데이터 사전* 을 작성할 수 있다.
- [ ] *Provenance* 를 *기록* 한다.

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
