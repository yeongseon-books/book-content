---
series: data-warehouse-101
episode: 8
title: Data Mart
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
  - DataMart
  - Modeling
  - Domain
  - Analytics
seo_description: Data Mart의 정의, Warehouse와의 차이, 도메인별 분석 구역의 역할
last_reviewed: '2026-05-12'
---

# Data Mart

Warehouse는 전사 공통 데이터를 모으는 중심 저장소입니다. 하지만 영업, 재무, 운영 팀은 같은 데이터를 두고도 다른 용어와 다른 기준으로 질문합니다. Data Mart는 이런 차이를 흡수해서 각 팀이 바로 쓸 수 있는 형태로 다시 정리한 얇은 계층입니다.

이 글은 Data Warehouse 101 시리즈의 8번째 글입니다.

## 이 글에서 다룰 문제

- Data Mart는 Warehouse와 무엇이 다를까요?
- 조직 공통 데이터와 팀 전용 분석 영역은 왜 분리할까요?
- 도메인별 vocabulary를 데이터 모델에 반영하면 무엇이 좋아질까요?
- conformed dimension은 여러 mart 사이에서 어떤 역할을 할까요?
- 권한 분리와 self-service 분석은 mart 설계에서 왜 중요할까요?

## 이 글에서 배울 것

- Data Mart의 정의
- Warehouse와 Data Mart의 차이
- 도메인별 작은 분석 구역이 필요한 이유
- Mart 설계 실습 5단계
- 입문 단계에서 자주 나오는 실수 5가지

## 왜 중요한가

Warehouse는 조직 전체가 공유하는 공통 데이터를 담습니다. 하지만 영업, 재무, 운영은 서로 다른 용어와 질문으로 데이터를 읽습니다. Data Mart는 이 차이를 팀 언어로 다시 정리해 주는 얇은 계층입니다.

> 공통성은 Warehouse에 두고, 도메인 언어는 Mart에 둡니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    DW["Warehouse (Conformed)"] --> SalesMart["Sales Mart"]
    DW --> FinanceMart["Finance Mart"]
    DW --> OpsMart["Ops Mart"]
    SalesMart --> SalesBI["Sales Dashboard"]
    FinanceMart --> FinanceBI["Finance Dashboard"]
```

## 핵심 용어

- **Data Mart**: 특정 도메인이나 팀에 맞춰 좁힌 분석 구역입니다.
- **Conformed Dimension**: 여러 mart가 함께 쓰는 공통 차원입니다.
- **Domain Modeling**: 팀의 용어와 규칙에 맞춰 데이터를 다시 읽는 모델링입니다.
- **Aggregated Mart**: 반복 집계를 미리 계산해 둔 mart입니다.
- **Self-service**: 분석가가 직접 조회하고 활용할 수 있는 사용 방식입니다.

## Before / After

**Before**: 영업팀이 Warehouse의 raw fact를 직접 조회해 조인이 복잡하고 응답도 느립니다.

**After**: sales mart가 팀 용어에 맞춰 미리 정리되어 대시보드가 빠르게 열립니다.

## 실습: Mart 설계 5단계

### 1단계 — 도메인 정의하기

```text
"The sales mart sees data at the *opportunity* level. It bundles *customer, stage, amount, owner*."
```

### 2단계 — conformed dimension 사용하기

```sql
CREATE OR REPLACE TABLE sales_mart.fact_opportunity AS
SELECT
    o.opp_id,
    u.user_key AS owner_key,
    c.customer_key,
    o.stage,
    o.amount,
    o.created_at
FROM staging.opportunities o
JOIN warehouse.dim_user u ON u.user_id = o.owner_id
JOIN warehouse.dim_customer c ON c.customer_id = o.customer_id;
```

### 3단계 — 미리 집계하기

```sql
CREATE OR REPLACE TABLE sales_mart.agg_pipeline_by_owner AS
SELECT
    owner_key,
    stage,
    SUM(amount) AS pipeline_amount,
    COUNT(*) AS opp_count
FROM sales_mart.fact_opportunity
GROUP BY 1, 2;
```

### 4단계 — mart 질의하기

```sql
SELECT u.name, SUM(a.pipeline_amount) AS total_pipeline
FROM sales_mart.agg_pipeline_by_owner a
JOIN warehouse.dim_user u ON u.user_key = a.owner_key
WHERE a.stage IN ('proposal', 'negotiation')
GROUP BY u.name;
```

### 5단계 — 권한 분리하기

```sql
GRANT SELECT ON SCHEMA sales_mart TO ROLE sales_readers;
GRANT SELECT ON SCHEMA finance_mart TO ROLE finance_readers;
```

## 이 코드에서 먼저 봐야 할 점

- conformed dimension은 Warehouse의 공통 기준을 그대로 가져옵니다.
- 팀이 실제로 쓰는 용어가 컬럼명과 모델 이름에 반영됩니다.
- 권한을 도메인 단위로 나누면 데이터 노출 범위를 관리하기 쉽습니다.

## 자주 하는 실수 5가지

1. **mart마다 별도 dimension을 만듭니다.** 결국 팀마다 숫자가 달라지는 원인이 됩니다.
2. **Warehouse 정리 없이 mart부터 만듭니다.** 공통 기준을 나중에 맞추기가 훨씬 어려워집니다.
3. **모든 컬럼을 mart로 끌고 옵니다.** 비용은 늘고 사용성은 오히려 떨어집니다.
4. **권한 분리를 생략합니다.** 민감 데이터가 불필요하게 넓게 노출될 수 있습니다.
5. **mart가 실시간 뷰인지 물질화된 복사본인지 모호합니다.** 갱신 주기와 소유자를 명확히 적어야 합니다.

## 실무에서는 이렇게 나타납니다

dbt 프로젝트에서는 marts 폴더를 도메인별로 나누는 경우가 많습니다. 영업, 재무, 제품, 마케팅이 각자의 mart를 가지되, 공통 dimension은 Warehouse에서 공유해 숫자 기준을 맞춥니다.

## 실무에서는 이렇게 생각합니다

- Mart는 Warehouse를 팀 언어로 다시 쓴 결과라고 봅니다.
- Conformed dimension은 조직의 헌법처럼 다룹니다.
- Mart는 작고 자주 갱신하는 쪽이 낫습니다.
- 권한은 도메인 경계를 따라 나눕니다.
- Mart의 수명도 지표로 관리합니다.

## 체크리스트

- [ ] Warehouse와 Mart의 차이를 설명할 수 있다.
- [ ] Conformed dimension이 왜 중요한지 알고 있다.
- [ ] 권한 분리가 필요한 이유를 말할 수 있다.
- [ ] 사전 집계가 주는 이점과 비용을 이해하고 있다.

## 연습 문제

1. 재무 마트에 둘 fact 테이블 세 개를 골라 보세요.
2. 각 mart가 서로 다른 dimension을 쓸 때 생길 충돌을 설명해 보세요.
3. 권한 분리가 없는 mart의 위험 두 가지를 적어 보세요.

## 마무리와 다음 글

Mart는 팀과 공통 데이터 모델 사이를 연결하는 얇은 다리입니다. 좋은 mart는 팀별 용어를 반영하면서도 공통 기준을 깨지 않습니다. 다음 글에서는 이렇게 쌓아 올린 모델을 더 빠르고 저렴하게 읽기 위한 성능 최적화 패턴을 살펴보겠습니다.

<!-- toc:begin -->
- [Data Warehouse란 무엇인가?](./01-what-is-data-warehouse.md)
- [OLTP와 OLAP](./02-oltp-and-olap.md)
- [Fact와 Dimension](./03-fact-and-dimension.md)
- [Star Schema](./04-star-schema.md)
- [Partition과 Clustering](./05-partition-and-clustering.md)
- [ETL과 ELT](./06-etl-and-elt.md)
- [BI와 Dashboard](./07-bi-and-dashboard.md)
- **Data Mart (현재 글)**
- 성능 최적화 (예정)
- Warehouse 설계 예제 (예정)
<!-- toc:end -->

## 참고 자료

- [Kimball — Data Mart](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)
- [dbt — Mart Layer](https://docs.getdbt.com/best-practices/how-we-structure/4-marts)
- [Snowflake — Schema Design](https://docs.snowflake.com/en/user-guide/intro-key-concepts)
- [Wikipedia — Data Mart](https://en.wikipedia.org/wiki/Data_mart)

Tags: DataWarehouse, DataMart, Modeling, Domain, Analytics
