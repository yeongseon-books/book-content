---
series: data-warehouse-101
episode: 5
title: Partition과 Clustering
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - DataWarehouse
  - Partition
  - Clustering
  - Performance
  - Analytics
seo_description: Partition 과 Clustering 의 차이, pruning 의 원리, 그리고 큰 테이블을 빠르게 읽는 두 가지 축
last_reviewed: '2026-05-04'
---

# Partition과 Clustering

> Data Warehouse 101 시리즈 (5/10)


## 이 글에서 다룰 문제

Warehouse 의 fact 는 *수십억 행* 이 보통입니다. *일자별 partition* 만 잘 잡아도 *95%* 의 행을 *읽지 않고 건너뜁니다*. *비용은 직접 절약* 됩니다.

> *읽지 않은 데이터에는 비용이 들지 않는다.*

## 전체 흐름
```mermaid
flowchart LR
    Query["WHERE date = '2026-05-04'"] --> Engine["Query Engine"]
    Engine --> P1["partition: 2026-05-03 (skip)"]
    Engine --> P2["partition: 2026-05-04 (scan)"]
    Engine --> P3["partition: 2026-05-05 (skip)"]
```

## Before/After

**Before**: `WHERE order_date = '2026-05-04'` 인데 *전체 테이블* 을 스캔한다.

**After**: 같은 쿼리가 *하루치 partition* 만 읽는다. *비용 1/100*.

## 적용 5단계

### 1단계 — Partition 정의

```sql
-- BigQuery 예시
CREATE TABLE fact_orders (
    order_id BIGINT,
    user_key BIGINT,
    amount NUMERIC(12, 2),
    order_date DATE
)
PARTITION BY order_date;
```

### 2단계 — Clustering 추가

```sql
CREATE TABLE fact_orders (
    order_id BIGINT,
    user_key BIGINT,
    amount NUMERIC(12, 2),
    order_date DATE
)
PARTITION BY order_date
CLUSTER BY user_key;
```

### 3단계 — Pruning 되는 쿼리

```sql
-- 하루치 partition 만 읽힌다
SELECT SUM(amount)
FROM fact_orders
WHERE order_date = '2026-05-04';
```

### 4단계 — Pruning 안 되는 쿼리

```sql
-- order_date 에 함수가 걸리면 pruning 이 안 된다
SELECT SUM(amount)
FROM fact_orders
WHERE EXTRACT(YEAR FROM order_date) = 2026;
```

### 5단계 — Cluster key 활용

```sql
-- user_key 도 함께 걸면 더 적게 읽는다
SELECT SUM(amount)
FROM fact_orders
WHERE order_date BETWEEN '2026-05-01' AND '2026-05-31'
  AND user_key = 100;
```

## 이 코드에서 주목할 점

- *조건이 partition key* 와 *직접* 비교돼야 pruning 된다.
- *함수* 를 씌우면 *pruning 이 깨진다*.
- Clustering 은 *partition 안* 에서 *추가 효과* 를 준다.

## 자주 하는 실수 5가지

1. **Partition key 에 *함수* 적용.** *전체 스캔* 으로 떨어진다.
2. **Partition 너무 *잘게* 쪼갠다.** *메타데이터 비용* 이 *읽기 비용* 을 넘는다.
3. **Cluster key 를 *너무 많이* 잡는다.** *정렬 비용* 이 *읽기 이득* 을 넘는다.
4. **Partition 없이 *Index* 만 믿는다.** Warehouse 는 *index 의 세상* 이 아니다.
5. ***과거 partition* 을 *수정* 한다.** *재계산이 산더미*.

## 실무에서는 이렇게 쓰입니다

BigQuery, Snowflake, Redshift 모두 *partition + clustering* 을 *기본 도구* 로 갖습니다. *날짜 partition + 사용자 클러스터* 가 *기본 조합* 입니다.

## 체크리스트

- [ ] *Partition* 과 *Clustering* 의 차이를 안다.
- [ ] *Pruning* 이 깨지는 패턴을 안다.
- [ ] *비용 계산* 방식을 안다.
- [ ] *Partition key* 선택 기준을 안다.

## 정리 및 다음 단계

Partition 과 Clustering 은 *비용과 속도* 를 동시에 개선합니다. 다음 글에서는 데이터를 적재하는 방법, *ETL* 과 *ELT* 를 봅니다.

<!-- toc:begin -->
- [Data Warehouse란 무엇인가?](./01-what-is-data-warehouse.md)
- [OLTP와 OLAP](./02-oltp-and-olap.md)
- [Fact와 Dimension](./03-fact-and-dimension.md)
- [Star Schema](./04-star-schema.md)
- **Partition과 Clustering (현재 글)**
- ETL과 ELT (예정)
- BI와 Dashboard (예정)
- Data Mart (예정)
- 성능 최적화 (예정)
- Warehouse 설계 예제 (예정)
<!-- toc:end -->

## 참고 자료

- [BigQuery — Partitioned Tables](https://cloud.google.com/bigquery/docs/partitioned-tables)
- [BigQuery — Clustered Tables](https://cloud.google.com/bigquery/docs/clustered-tables)
- [Snowflake — Clustering Keys](https://docs.snowflake.com/en/user-guide/tables-clustering-keys)
- [Redshift — Distribution and Sort Keys](https://docs.aws.amazon.com/redshift/latest/dg/c_designing-tables-best-practices.html)
