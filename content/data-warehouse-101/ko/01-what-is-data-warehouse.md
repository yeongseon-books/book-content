---
series: data-warehouse-101
episode: 1
title: Data Warehouse란 무엇인가?
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
  - Analytics
  - OLAP
  - Database
  - BI
seo_description: Data Warehouse의 정의, OLTP와 다른 점, 분석을 위한 데이터 저장소가 필요한 이유
last_reviewed: '2026-05-11'
---

# Data Warehouse란 무엇인가?

> Data Warehouse 101 시리즈 (1/10)


## 이 글에서 다룰 문제

서비스가 커지면 주문 한 건을 처리하는 데이터베이스와 어제 매출 합계를 빠르게 계산하는 데이터베이스가 서로 다른 요구를 받기 시작합니다. 같은 테이블과 같은 엔진으로 두 일을 동시에 처리하려고 하면 운영 쿼리도 느려지고 분석 쿼리도 느려집니다. 그래서 운영용 저장소와 분석용 저장소를 분리하는 사고방식이 필요합니다.

> 운영 트래픽과 분석 트래픽은 같은 길에 오래 두지 않는 편이 좋습니다.

## 전체 흐름
```mermaid
flowchart LR
    Service["서비스 DB (OLTP)"] --> ETL["ETL / ELT"]
    ETL --> DW["Data Warehouse"]
    DW --> BI["BI / Dashboard"]
    DW --> ML["ML / Analytics"]
```

## Before/After

**Before**: 서비스 DB에서 6개월 매출을 직접 집계하느라 프로덕션 응답이 느려집니다.

**After**: Warehouse에 한 번 적재한 뒤 필요한 관점으로 빠르게 집계합니다.

## 첫 분석 쿼리 5단계

### 1단계 — 사실 테이블 만들기

```sql
CREATE TABLE fact_orders (
    order_id BIGINT,
    user_id BIGINT,
    amount NUMERIC(12, 2),
    order_date DATE
);
```

### 2단계 — 데이터 적재

```sql
INSERT INTO fact_orders VALUES
    (1, 100, 25000, '2026-01-15'),
    (2, 100, 18000, '2026-02-03'),
    (3, 200, 42000, '2026-02-10');
```

### 3단계 — 월별 매출

```sql
SELECT date_trunc('month', order_date) AS month,
       SUM(amount) AS revenue
FROM fact_orders
GROUP BY 1
ORDER BY 1;
```

### 4단계 — 사용자별 합계

```sql
SELECT user_id, SUM(amount) AS total
FROM fact_orders
GROUP BY user_id;
```

### 5단계 — 상위 고객

```sql
SELECT user_id, SUM(amount) AS total
FROM fact_orders
GROUP BY user_id
ORDER BY total DESC
LIMIT 10;
```

## 이 코드에서 주목할 점

- 분석 쿼리는 개별 행보다 집계를 중심으로 작성합니다.
- 날짜 컬럼은 거의 모든 분석의 기준축이 되므로 처음부터 명확히 둡니다.
- 원본 시스템을 직접 흔들지 않고 복사된 데이터를 대상으로 분석합니다.

## 자주 하는 실수 5가지

1. **서비스 DB에서 바로 분석 쿼리를 실행합니다.** 운영 장애로 이어지기 쉬운 대표 패턴입니다.
2. **모든 테이블을 그대로 복사합니다.** Warehouse는 목적에 맞게 다시 모델링해야 합니다.
3. **시간 컬럼 없이 적재합니다.** 나중에 시계열 분석이 막힙니다.
4. **적재 전에 모든 변환을 끝내려 합니다.** 먼저 원본을 보존하고 변환은 Warehouse 안에서 관리하는 편이 안전합니다.
5. **Warehouse를 실시간 시스템처럼 설계합니다.** 실제로는 분 단위 신선도로 충분한 경우가 많습니다.

## 실무에서는 이렇게 쓰입니다

초기에는 Postgres replica를 분석용으로 써서 시작하는 팀도 많습니다. 데이터 규모와 사용자 수가 커지면 BigQuery, Snowflake, Redshift 같은 전용 엔진으로 옮겨 갑니다. 대시보드, 정기 리포트, ML feature 추출까지 대부분의 분석 작업이 Warehouse를 출발점으로 삼습니다.

## 체크리스트

- [ ] OLTP와 OLAP의 차이를 설명할 수 있다.
- [ ] 운영 저장소와 분석 저장소를 왜 분리해야 하는지 말할 수 있다.
- [ ] ETL / ELT의 큰 흐름을 알고 있다.
- [ ] Warehouse에서 시간 컬럼이 왜 중요한지 이해하고 있다.

## 정리 및 다음 단계

Data Warehouse는 분석을 위해 따로 마련한 저장소입니다. 운영 시스템을 보호하면서도 넓은 범위의 집계를 빠르게 수행하려면 이런 분리가 필요합니다. 다음 글에서는 OLTP와 OLAP가 어떻게 다르고 왜 같은 엔진에 오래 함께 두기 어려운지 더 자세히 살펴보겠습니다.

<!-- toc:begin -->
- **Data Warehouse란 무엇인가? (현재 글)**
- OLTP와 OLAP (예정)
- Fact와 Dimension (예정)
- Star Schema (예정)
- Partition과 Clustering (예정)
- ETL과 ELT (예정)
- BI와 Dashboard (예정)
- Data Mart (예정)
- 성능 최적화 (예정)
- Warehouse 설계 예제 (예정)
<!-- toc:end -->

## 참고 자료

- [Kimball Group — Data Warehouse Concepts](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/)
- [BigQuery — What Is a Data Warehouse?](https://cloud.google.com/learn/what-is-a-data-warehouse)
- [Snowflake — Data Warehouse Guide](https://www.snowflake.com/guides/what-data-warehouse/)
- [AWS — Data Warehouse Concepts](https://aws.amazon.com/data-warehouse/)

Tags: DataWarehouse, Analytics, OLAP, Database, BI
