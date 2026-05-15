---
series: data-science-101
episode: 3
title: 데이터 수집
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - DataScience
  - DataCollection
  - API
  - Database
  - Beginner
seo_description: 파일, API, DB, 로그에서 데이터를 모으는 방법과 출처 기록 원칙을 정리합니다
last_reviewed: '2026-05-12'
---

# 데이터 수집

이 글은 Data Science 101 시리즈의 세 번째 글입니다.

데이터 분석이라고 하면 모델링이나 시각화부터 떠올리기 쉽지만, 실제로는 수집 단계에서 이미 결과의 절반이 갈립니다. 누가 언제 어떤 경로로 데이터를 가져왔는지 모르면 같은 분석을 다시 할 수 없고, 결과를 검증하기도 어렵습니다. 팀원이 보내 준 엑셀 파일 하나로 시작한 분석이 나중에 왜 신뢰를 잃는지도 대개 여기서 시작됩니다.

이 글에서는 데이터를 수집하는 대표 경로 네 가지, 원본과 사본을 구분하는 습관, 출처를 기록하는 방법을 정리합니다. 수집은 단순히 데이터를 가져오는 단계가 아니라, 분석의 재현성을 만드는 기록 단계라는 점이 핵심입니다.

## 이 글에서 다룰 문제

- 분석에 필요한 데이터는 보통 어디서 가져올까요?
- 원본, 사본, 스냅샷은 왜 구분해야 할까요?
- 파일, API, 데이터베이스, 이벤트 로그는 각각 어떤 특성을 가질까요?
- 데이터 출처를 기록하는 습관은 왜 재현성의 핵심일까요?
- 수집 단계에서 놓친 문제가 왜 마지막 보고서까지 따라올까요?

> 모든 분석은 데이터를 어디에서 가져왔는지 적는 순간부터 신뢰를 얻기 시작합니다.

## 이 글에서 배우는 내용

- 파일, API, 데이터베이스, 이벤트 로그라는 네 가지 대표 출처
- 원본, 사본, 스냅샷의 차이
- 데이터 사전의 역할
- 5단계 수집 실습 흐름
- 수집 단계에서 자주 놓치는 함정 다섯 가지

## 왜 중요한가

수집 단계에서 빠진 행 하나, 잘못 가져온 기간 하나, 출처가 불분명한 파일 하나는 마지막 보고서까지 따라옵니다. 나중에 EDA를 잘하고 모델을 잘 만들어도 처음 데이터가 어디서 왔는지 설명할 수 없다면 결과를 믿기 어렵습니다.

현업에서 재현성은 거창한 시스템보다 작은 습관에서 시작됩니다. 원본 경로와 추출 시각을 적는 습관이 그 대표 사례입니다.

> 추적 가능한 데이터만 신뢰할 수 있습니다.

## 핵심 개념 한눈에 보기

```mermaid
flowchart LR
    File["파일 / CSV"] --> Stage["스테이징"]
    API["API"] --> Stage
    DB["데이터베이스"] --> Stage
    Log["이벤트 로그"] --> Stage
    Stage --> Analysis["분석"]
```

## 핵심 용어

- **Source of truth**: 데이터의 권위 있는 원본입니다.
- **Snapshot**: 특정 시점에 고정해서 떠 놓은 사본입니다.
- **Schema**: 데이터의 컬럼 구조와 타입입니다.
- **Data dictionary**: 각 컬럼의 의미를 문서화한 표입니다.
- **Provenance**: 데이터의 출처와 생성 이력입니다.

## Before / After

**Before**: 동료가 엑셀 파일을 보내 줍니다. 언제 뽑았는지, 어디서 추출했는지, 중간에 손으로 수정했는지 알 수 없습니다.

**After**: 같은 데이터를 웨어하우스에서 SQL로 다시 추출하고, 추출 시각과 해시를 기록합니다. 몇 달 뒤에도 같은 분석을 재현할 수 있습니다.

## 실습: 5단계 수집

### 1단계 — 파일에서 가져오기

```python
import pandas as pd
df = pd.read_csv("data/users-2026-05-04.csv")
print(df.shape)
```

파일 기반 수집은 가장 단순하지만 그만큼 위험하기도 합니다. 손으로 수정되기 쉽고 버전 추적도 약하기 때문입니다. 그래서 파일 이름에 날짜를 넣고 원본과 작업본을 분리하는 습관이 중요합니다.

### 2단계 — API에서 가져오기

```python
import requests
resp = requests.get("https://api.example.com/users", timeout=10)
resp.raise_for_status()
users = resp.json()
```

API 수집에서는 네트워크 실패, 인증, 응답 포맷 변경, rate limit을 항상 염두에 둬야 합니다. 한 번 성공했다고 끝이 아니라, 반복 수집에서도 안정적으로 동작하는지가 더 중요합니다.

### 3단계 — 데이터베이스에서 가져오기

```python
from sqlalchemy import create_engine
engine = create_engine("postgresql://user:pass@host/db")
df = pd.read_sql(
    "SELECT id, signup_at FROM users WHERE signup_at > '2026-01-01'",
    engine,
)
```

데이터베이스는 보통 가장 신뢰할 수 있는 원천입니다. 다만 운영 DB를 직접 조회하기보다 읽기 복제본이나 웨어하우스를 쓰는 편이 안전합니다. 어떤 쿼리로 가져왔는지도 함께 남겨야 합니다.

### 4단계 — 이벤트 로그에서 가져오기

```python
# JSONL — one JSON event per line
import json
with open("events.jsonl") as f:
    events = [json.loads(line) for line in f]
```

로그는 행동 데이터를 풍부하게 담지만 포맷 변경에 취약합니다. 이벤트 이름 하나, 필드 하나만 바뀌어도 분석이 조용히 깨질 수 있습니다. 그래서 로그 수집은 스키마 관리와 함께 봐야 합니다.

### 5단계 — 출처 기록하기

```python
import hashlib
import datetime

meta = {
    "source": "postgres://prod-replica/users",
    "fetched_at": datetime.datetime.utcnow().isoformat(),
    "row_count": len(df),
    "sha256": hashlib.sha256(
        pd.util.hash_pandas_object(df).values.tobytes()
    ).hexdigest()[:16],
}
print(meta)
```

출처, 시각, 행 수, 해시를 함께 남기면 나중에 같은 데이터였는지 빠르게 확인할 수 있습니다. 해시는 완벽한 메타데이터는 아니지만, 데이터가 바뀌었는지 감지하는 값싼 안전장치로 유용합니다.

## 이 코드에서 먼저 봐야 할 점

- 출처와 추출 시각은 항상 함께 기록해야 합니다.
- 해시는 데이터 변경 여부를 빠르게 확인하는 데 유용합니다.
- 원본은 수정하지 말고, 모든 변경은 스테이징 이후 단계에서 해야 합니다.

## 자주 하는 실수 다섯 가지

1. **원본 파일을 엑셀에서 바로 덮어쓰는 실수**: 되돌릴 방법이 사라집니다.
2. **API rate limit을 무시하는 실수**: 반복 수집 시 차단되거나 실패율이 높아집니다.
3. **스키마를 문서화하지 않는 실수**: 시간이 지나면 컬럼 의미가 증발합니다.
4. **로그 포맷 변경을 추적하지 않는 실수**: 분석이 조용히 깨집니다.
5. **민감 데이터를 개인 장비에 저장하는 실수**: 보안 사고로 이어질 수 있습니다.

## 실무에서는 이렇게 나타납니다

실무 데이터 팀은 수집 스크립트를 Airflow나 dbt 같은 파이프라인 안에서 돌립니다. 로드할 때마다 `load_id`, `fetched_at`, `source` 같은 메타데이터를 함께 붙이고, 데이터 사전은 Notion이나 Confluence에 유지합니다. 중요한 것은 도구 이름이 아니라 수집 과정을 반복 가능하고 설명 가능하게 만든다는 점입니다.

## 시니어는 이렇게 생각합니다

- 원본은 절대 수정하지 않습니다.
- 출처, 시각, 해시는 반사적으로 기록합니다.
- 스키마 변경은 알림으로 잡아야 합니다.
- 민감 데이터는 분석 전에 마스킹합니다.
- 데이터 사전은 가장 값비싼 문서 중 하나입니다.

## 체크리스트

- [ ] 대표적인 데이터 출처 네 가지를 알고 있습니다.
- [ ] snapshot이 무엇인지 설명할 수 있습니다.
- [ ] 데이터 사전을 작성할 수 있습니다.
- [ ] provenance를 기본값처럼 기록합니다.

## 연습 문제

1. 공개 API 하나를 골라 작은 샘플을 수집하고 메타데이터를 기록해 보세요.
2. 원본 → 스테이징 → 분석 흐름을 그림으로 그려 보세요.
3. 스키마 변경이 분석에 영향을 준 사례를 하나 적어 보세요.

## 정리 및 다음 글

데이터 수집은 단순한 입력 단계가 아니라 분석의 재현성을 만드는 기록 단계입니다. 원본, 스냅샷, 출처를 구분하는 습관이 있어야 이후 정제와 분석이 흔들리지 않습니다. 다음 글에서는 이렇게 모은 데이터를 실제로 어떻게 정제하고 검증하는지 살펴보겠습니다.

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
- [Google — Data Validation for Machine Learning](https://research.google/pubs/data-validation-for-machine-learning/)

Tags: DataScience, DataCollection, API, Database, Beginner
