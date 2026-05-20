---
series: data-warehouse-101
episode: 6
title: "Data Warehouse 101 (6/10): ETL과 ELT"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - DataWarehouse
  - ETL
  - ELT
  - Pipeline
  - Analytics
seo_description: ETL과 ELT의 차이, 변환 위치, 현대 Warehouse가 ELT로 기우는 이유
last_reviewed: '2026-05-15'
---

# Data Warehouse 101 (6/10): ETL과 ELT

Warehouse 컴퓨팅 비용이 낮아지면서 원본을 먼저 적재하고 그다음 SQL로 변환하는 방식이 기본이 되었습니다. 이렇게 하면 변환 로직이 SQL 파일로 남아 버전 관리가 쉬워지고, 재실행과 디버깅도 훨씬 단순해집니다.

이 글은 Data Warehouse 101 시리즈의 6번째 글입니다.

## 먼저 던지는 질문

- ETL과 ELT는 변환을 어디에서 다르게 수행할까요?
- 현대 Warehouse가 ELT를 선호하는 이유는 무엇일까요?
- staging을 건너뛰면 어떤 문제가 생길까요?

## 큰 그림

![Data Warehouse 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-warehouse-101/06/06-01-concept-at-a-glance.ko.png)

*Data Warehouse 101 6장 흐름 개요*

이 그림에서는 ETL과 ELT를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> ETL과 ELT의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 이 글에서 배울 것

- ETL과 ELT의 차이
- 변환을 둘 위치를 고르는 기준
- 현대 Warehouse가 ELT를 선호하는 이유
- 파이프라인 실습 5단계
- 입문 단계에서 자주 나오는 실수 5가지

## 왜 중요한가

Warehouse 쪽 컴퓨트가 저렴해지면서 원본을 먼저 적재하고 SQL로 변환하는 방식이 기본값에 가까워졌습니다. 변환 로직이 SQL 파일로 남고 버전 관리가 가능해지며, 재실행도 쉬워졌기 때문입니다. 그래서 이제는 파이프라인을 코드처럼 다루는 감각이 중요합니다.

> 변환을 SQL로 끌어오면 가시성과 재현성이 함께 따라옵니다.

## 개념 한눈에 보기

## 핵심 용어

- **ETL**: Extract → Transform → Load. 적재 전에 변환을 끝내는 방식입니다.
- **ELT**: Extract → Load → Transform. 적재 후 Warehouse 안에서 변환하는 방식입니다.
- **Staging**: 원본을 최대한 보존하는 첫 적재 계층입니다.
- **dbt**: SQL 기반 변환과 테스트를 함께 관리하는 도구입니다.
- **Idempotent**: 여러 번 실행해도 같은 결과를 만드는 성질입니다.

## Before / After

**Before**: ETL 도중 변환이 실패했는데 원본이 이미 사라져 재처리가 복잡해집니다.

**After**: staging에 원본을 남겨 두고 SQL 변환만 다시 실행합니다.

## 실습: 파이프라인 5단계

### 1단계 — 원본 적재하기

```sql
COPY raw.orders
FROM 's3://bucket/orders/2026-05-04/'
FORMAT AS PARQUET;
```

### 2단계 — staging 모델 만들기

```sql
CREATE OR REPLACE TABLE staging.orders AS
SELECT
    order_id::BIGINT AS order_id,
    user_id::BIGINT AS user_id,
    amount::NUMERIC(12, 2) AS amount,
    created_at::TIMESTAMP AS created_at
FROM raw.orders;
```

### 3단계 — 변환 모델 만들기

```sql
CREATE OR REPLACE TABLE marts.fact_orders AS
SELECT
    order_id,
    user_id,
    amount,
    DATE(created_at) AS order_date
FROM staging.orders
WHERE amount > 0;
```

### 4단계 — 테스트하기

```sql
-- No negative amounts allowed
SELECT COUNT(*) AS bad
FROM marts.fact_orders
WHERE amount <= 0;
```

### 5단계 — 재실행하기

```sql
-- Raw stays put; only the transform replays
TRUNCATE marts.fact_orders;
INSERT INTO marts.fact_orders SELECT ...;
```

## 이 코드에서 먼저 봐야 할 점

- 원본, staging, mart로 흐름을 나누면 각 단계의 책임이 분명해집니다.
- 변환 로직이 SQL 파일에 모이면 리뷰와 버전 관리가 쉬워집니다.
- 같은 입력으로 다시 실행해도 같은 결과가 나오는 idempotent 구조가 중요합니다.

## 자주 하는 실수 5가지

1. **원본 데이터를 덮어씁니다.** 과거 시점 재현이 어려워집니다.
2. **변환을 Python 함수 안에 숨깁니다.** 로직이 보이지 않아 리뷰와 디버깅이 힘들어집니다.
3. **테스트 없이 적재합니다.** 잘못된 데이터가 그대로 대시보드까지 올라갈 수 있습니다.
4. **재실행할 때 결과가 달라집니다.** idempotent하지 않으면 파이프라인 신뢰가 떨어집니다.
5. **모든 변환을 한 모델에 몰아넣습니다.** 작은 모델로 나누는 편이 읽기와 유지보수에 유리합니다.

## 실무에서는 이렇게 나타납니다

Fivetran이나 Airbyte로 적재하고, dbt로 변환하고, Airflow나 Dagster로 스케줄을 관리하는 조합이 널리 쓰입니다. 변환 로직은 SQL 모델 형태로 Git에 남기고, 테스트도 같은 저장소에서 함께 관리합니다.

## 실무에서는 이렇게 생각합니다

- raw는 법적 기록처럼 보존합니다.
- 변환은 SQL 파일로 모아 둡니다.
- 모든 모델 옆에는 테스트가 있어야 합니다.
- idempotency는 재현성의 다른 이름이라고 봅니다.
- 파이프라인 자체도 버전 관리합니다.

## 체크리스트

- [ ] ETL과 ELT의 차이를 설명할 수 있다.
- [ ] Staging 계층의 역할을 이해하고 있다.
- [ ] Idempotent가 무엇을 뜻하는지 말할 수 있다.
- [ ] 변환 모델에 테스트를 붙여야 하는 이유를 알고 있다.

## 연습 문제

1. ETL이 더 적합한 사례 하나를 적어 보세요.
2. staging을 건너뛰었을 때의 위험 세 가지를 적어 보세요.
3. idempotent하지 않은 변환 예시 하나를 적어 보세요.

## 마무리와 다음 글

ELT는 Warehouse의 계산 능력을 적극적으로 활용하는 현대적인 적재 방식입니다. 원본 보존, SQL 중심 변환, 반복 가능한 재실행이라는 세 가지 장점이 함께 따라옵니다. 다음 글에서는 이렇게 준비한 데이터를 사람이 실제로 읽고 판단하는 도구인 BI와 대시보드를 살펴보겠습니다.

## 처음 질문으로 돌아가기

- **ETL과 ELT는 변환을 어디에서 다르게 수행할까요?**
  - 본문의 기준은 ETL과 ELT를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **현대 Warehouse가 ELT를 선호하는 이유는 무엇일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **staging을 건너뛰면 어떤 문제가 생길까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Warehouse 101 (1/10): Data Warehouse란 무엇인가?](./01-what-is-data-warehouse.md)
- [Data Warehouse 101 (2/10): OLTP와 OLAP](./02-oltp-and-olap.md)
- [Data Warehouse 101 (3/10): Fact와 Dimension](./03-fact-and-dimension.md)
- [Data Warehouse 101 (4/10): Star Schema](./04-star-schema.md)
- [Data Warehouse 101 (5/10): Partition과 Clustering](./05-partition-and-clustering.md)
- **ETL과 ELT (현재 글)**
- BI와 Dashboard (예정)
- Data Mart (예정)
- 성능 최적화 (예정)
- Warehouse 설계 예제 (예정)

<!-- toc:end -->

## 참고 자료

- [dbt — What Is dbt?](https://docs.getdbt.com/docs/introduction)
- [Fivetran — ELT vs ETL](https://www.fivetran.com/blog/elt-vs-etl)
- [Airbyte — Modern Data Stack](https://airbyte.com/blog/modern-data-stack)
- [Designing Data-Intensive Applications](https://dataintensive.net/)

Tags: DataWarehouse, ETL, ELT, Pipeline, Analytics
