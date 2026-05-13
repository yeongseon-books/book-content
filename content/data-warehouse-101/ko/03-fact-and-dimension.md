---
series: data-warehouse-101
episode: 3
title: Fact와 Dimension
status: publish-ready
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
seo_description: Fact와 Dimension의 역할, 분리 이유, 분석 모델의 기본 단위
last_reviewed: '2026-05-12'
---

# Fact와 Dimension

분석 질문은 대부분 얼마를 어떤 기준으로 보고 싶은지로 정리됩니다. 매출, 수량, 건수 같은 측정값과 사용자, 상품, 날짜 같은 속성을 분리해 두면 집계는 단순해지고 속성 변경도 더 유연하게 처리할 수 있습니다.

이 글은 Data Warehouse 101 시리즈의 3번째 글입니다.

## 이 글에서 다룰 문제

- Fact 테이블과 Dimension 테이블은 무엇을 다르게 담을까요?
- 측정값과 속성을 분리하면 어떤 이점이 생길까요?
- 분석 모델에서 grain을 먼저 정해야 하는 이유는 무엇일까요?
- Surrogate key와 conformed dimension은 왜 자주 등장할까요?
- OLAP 모델링을 시작할 때 가장 먼저 적어야 할 문장은 무엇일까요?

## 이 글에서 배울 것

- Fact 테이블의 정의
- Dimension 테이블의 정의
- 둘을 분리했을 때 얻는 이점
- 모델링 실습 5단계
- 입문 단계에서 자주 나오는 실수 5가지

## 왜 중요한가

분석 질문은 대개 얼마나 많이 일어났는지와 어떤 기준으로 나눌 것인지로 읽힙니다. 측정값과 속성을 분리하면 집계는 빠르게 유지되고, 속성 변화는 더 유연하게 다룰 수 있습니다. 이 분리가 OLAP 모델링의 출발점입니다.

> 측정값과 속성을 분리하면 둘 다 더 오래 깔끔하게 유지됩니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    Fact["fact_orders (amount, qty)"] --> DimUser["dim_user"]
    Fact --> DimProduct["dim_product"]
    Fact --> DimDate["dim_date"]
```

## 핵심 용어

- **Fact**: 금액, 수량, 시간처럼 측정 가능한 이벤트입니다.
- **Dimension**: 사용자, 상품, 날짜처럼 fact의 맥락을 설명하는 속성 집합입니다.
- **Grain**: fact 한 행이 무엇을 의미하는지 적는 가장 작은 단위입니다.
- **Surrogate key**: 차원 테이블 내부에서 쓰는 대체 식별자입니다.
- **Conformed dimension**: 여러 fact가 함께 공유하는 공통 차원입니다.

## Before / After

**Before**: 주문 한 행에 사용자 이름과 상품 이름까지 함께 들어 있어 이름이 바뀌면 과거 행까지 모두 손봐야 합니다.

**After**: 사용자 이름은 dim_user에서만 관리하고 fact는 그대로 둡니다.

## 실습: 모델링 5단계

### 1단계 — dimension 만들기

```sql
CREATE TABLE dim_user (
    user_key BIGINT PRIMARY KEY,
    user_id BIGINT,
    name TEXT,
    country TEXT
);
```

### 2단계 — date dimension 만들기

```sql
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE,
    year INT,
    month INT,
    day_of_week INT
);
```

### 3단계 — fact 만들기

```sql
CREATE TABLE fact_orders (
    order_id BIGINT,
    user_key BIGINT,
    date_key INT,
    amount NUMERIC(12, 2),
    qty INT
);
```

### 4단계 — 분석용 조인 만들기

```sql
SELECT u.country, SUM(f.amount) AS revenue
FROM fact_orders f
JOIN dim_user u ON u.user_key = f.user_key
GROUP BY u.country;
```

### 5단계 — 시간 축 분석하기

```sql
SELECT d.year, d.month, SUM(f.amount) AS revenue
FROM fact_orders f
JOIN dim_date d ON d.date_key = f.date_key
GROUP BY d.year, d.month
ORDER BY 1, 2;
```

## 이 코드에서 먼저 봐야 할 점

- fact는 측정값과 분석 키를 중심으로 가볍게 유지합니다.
- dimension은 사람이 읽고 해석하는 데 필요한 속성을 담습니다.
- 잘 만든 dimension은 여러 fact가 함께 재사용할 수 있습니다.

## 자주 하는 실수 5가지

1. **fact에 문자열 속성을 직접 넣습니다.** 행 수가 커질수록 저장 비용과 조인 비용이 빠르게 커집니다.
2. **grain을 섞습니다.** 주문 단위와 상품 단위를 한 fact에 넣으면 집계 결과를 믿기 어려워집니다.
3. **surrogate key 없이 natural key만 씁니다.** 상위 시스템 키가 바뀌는 순간 과거 fact까지 영향을 받습니다.
4. **date dimension을 만들지 않습니다.** 주말, 공휴일, 회계 캘린더 같은 분석이 금방 불편해집니다.
5. **dimension에 측정값을 넣습니다.** 테이블의 역할이 흐려지고 팀 전체가 헷갈리기 쉽습니다.

## 실무에서는 이렇게 나타납니다

전자상거래에서는 fact_orders, fact_payments, fact_refunds를 따로 두고 dim_user, dim_product, dim_date를 공통으로 공유하는 경우가 많습니다. 사용자 국가가 바뀌어도 dim_user 한 곳만 관리하면 되므로 운영 부담이 줄어듭니다.

## 실무에서는 이렇게 생각합니다

- grain은 한 문장으로 정확히 쓸 수 있어야 합니다.
- conformed dimension은 팀 자산처럼 다룹니다.
- surrogate key로 상류 시스템의 변화를 흡수합니다.
- 날짜 차원은 대부분의 분석을 떠받치는 등뼈로 봅니다.
- fact는 좁고 길게, dimension은 넓고 짧게 가져갑니다.

## 체크리스트

- [ ] Fact와 Dimension의 역할 차이를 설명할 수 있다.
- [ ] Grain을 한 줄 문장으로 적을 수 있다.
- [ ] Surrogate key가 왜 필요한지 이해하고 있다.
- [ ] Date dimension이 분석에 주는 이점을 알고 있다.

## 연습 문제

1. fact_payments의 grain을 한 문장으로 적어 보세요.
2. dim_product에 들어갈 컬럼 다섯 개를 적어 보세요.
3. surrogate key를 생략했을 때의 단점 세 가지를 적어 보세요.

## 마무리와 다음 글

Fact와 Dimension을 분리하는 일은 분석 모델의 출발점입니다. 무엇을 세고 무엇으로 자를지 분명해지면 이후 설계가 훨씬 단순해집니다. 다음 글에서는 이 구조를 가장 널리 쓰는 형태로 정리한 Star Schema를 살펴보겠습니다.

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

Tags: DataWarehouse, Fact, Dimension, Modeling, Analytics
