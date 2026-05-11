---
series: data-warehouse-101
episode: 3
title: Fact와 Dimension
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
  - Fact
  - Dimension
  - Modeling
  - Analytics
seo_description: Fact 테이블과 Dimension 테이블의 역할, 측정값과 속성의 분리, 그리고 분석 모델의 기본 단위
last_reviewed: '2026-05-04'
---

# Fact와 Dimension

> Data Warehouse 101 시리즈 (3/10)


## 이 글에서 다룰 문제

분석 질문은 거의 항상 *얼마(measure)* 를 *어떤 단면(dimension)* 별로 보고 싶어합니다. *둘을 분리* 해 두면 *집계는 빠르게*, *속성 변경은 유연하게* 다룰 수 있습니다.

> *측정과 속성을 나눠라. 함께 두면 둘 다 느려진다.*

## 전체 흐름
```mermaid
flowchart LR
    Fact["fact_orders (amount, qty)"] --> DimUser["dim_user"]
    Fact --> DimProduct["dim_product"]
    Fact --> DimDate["dim_date"]
```

## Before/After

**Before**: *주문 한 행* 안에 *사용자 이름, 상품 이름* 까지 다 들어 있다. *이름이 바뀌면* 모든 행을 *고쳐야 한다*.

**After**: 사용자 이름은 *dim_user* 한 곳에서만 관리한다. *fact 는 그대로*.

## 모델링 5단계

### 1단계 — Dimension 만들기

```sql
CREATE TABLE dim_user (
    user_key BIGINT PRIMARY KEY,
    user_id BIGINT,
    name TEXT,
    country TEXT
);
```

### 2단계 — Date dimension

```sql
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE,
    year INT,
    month INT,
    day_of_week INT
);
```

### 3단계 — Fact 만들기

```sql
CREATE TABLE fact_orders (
    order_id BIGINT,
    user_key BIGINT,
    date_key INT,
    amount NUMERIC(12, 2),
    qty INT
);
```

### 4단계 — 조인 분석

```sql
SELECT u.country, SUM(f.amount) AS revenue
FROM fact_orders f
JOIN dim_user u ON u.user_key = f.user_key
GROUP BY u.country;
```

### 5단계 — 시간축 분석

```sql
SELECT d.year, d.month, SUM(f.amount) AS revenue
FROM fact_orders f
JOIN dim_date d ON d.date_key = f.date_key
GROUP BY d.year, d.month
ORDER BY 1, 2;
```

## 이 코드에서 주목할 점

- *fact 는 가벼운 수치* 만 갖는다.
- *dimension 은 의미를 갖는 속성* 을 갖는다.
- 같은 dimension 을 *여러 fact* 가 *공유* 한다.

## 자주 하는 실수 5가지

1. **fact 안에 *문자열 속성* 을 직접 넣는다.** 행 수가 *수억* 이면 *저장 비용 폭발*.
2. **Grain 을 *섞는다*.** *주문 단위* 와 *상품 단위* 를 한 fact 에 두면 *집계가 거짓말*.
3. **Surrogate key 없이 *natural key* 만 쓴다.** 키가 *바뀌면* 모든 fact 가 *흔들린다*.
4. **Date dimension 을 *만들지 않는다*.** *주말 / 공휴일* 분석이 *어렵다*.
5. **Dimension 에 *측정값* 을 둔다.** 의미가 흐려져 *팀이 헷갈린다*.

## 실무에서는 이렇게 쓰입니다

전자상거래는 *fact_orders, fact_payments, fact_refunds* 를 두고 *dim_user, dim_product, dim_date* 를 *공유* 합니다. 사용자 *국가가 바뀔 때* 도 dim_user 한 곳만 갱신합니다.

## 체크리스트

- [ ] *Fact* 와 *Dimension* 의 차이를 안다.
- [ ] *Grain* 을 한 줄로 적을 수 있다.
- [ ] *Surrogate key* 의 필요성을 안다.
- [ ] *Date dimension* 의 가치를 안다.

## 정리 및 다음 단계

Fact 와 Dimension 의 분리가 *분석 모델의 출발점* 입니다. 다음 글에서는 가장 흔한 모델인 *Star Schema* 를 봅니다.

<!-- toc:begin -->
- [Data Warehouse란 무엇인가?](./01-what-is-data-warehouse.md)
- [OLTP와 OLAP](./02-oltp-and-olap.md)
- **Fact와 Dimension (현재 글)**
- Star Schema (예정)
- Partition과 Clustering (예정)
- ETL과 ELT (예정)
- BI와 Dashboard (예정)
- Data Mart (예정)
- 성능 최적화 (예정)
- Warehouse 설계 예제 (예정)
<!-- toc:end -->

## 참고 자료

- [Kimball — Fact Table Design](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)
- [dbt — Dimensional Modeling](https://docs.getdbt.com/best-practices/how-we-structure/1-guide-overview)
- [Snowflake — Star Schema](https://docs.snowflake.com/en/user-guide/intro-key-concepts)
- [BigQuery — Schema Design](https://cloud.google.com/bigquery/docs/schemas)
