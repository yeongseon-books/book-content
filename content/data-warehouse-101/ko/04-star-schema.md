---
series: data-warehouse-101
episode: 4
title: "Data Warehouse 101 (4/10): Star Schema"
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
  - StarSchema
  - Modeling
  - Snowflake
  - Analytics
seo_description: Star Schema 구조, Snowflake와의 차이, BI가 별 모양을 좋아하는 이유
last_reviewed: '2026-05-15'
---

# Data Warehouse 101 (4/10): Star Schema

분석 쿼리는 조인 수가 늘어날수록 느려지기 쉽습니다. Star Schema는 중심 fact 하나와 그 주변 dimension으로 구조를 단순하게 만들기 때문에 읽기 성능과 이해 가능성을 함께 챙기기 좋습니다. BI 도구도 이런 별 모양을 전제로 drill-down 경험을 설계하는 경우가 많습니다.

이 글은 Data Warehouse 101 시리즈의 4번째 글입니다.

## 먼저 던지는 질문

- Star Schema는 왜 분석에서 가장 자주 보일까요?
- Snowflake Schema와는 어떤 점이 다를까요?
- 조인 홉 수가 성능과 가독성에 왜 중요할까요?

## 큰 그림

![Data Warehouse 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-warehouse-101/04/04-01-concept-at-a-glance.ko.png)

*Data Warehouse 101 4장 흐름 개요*

이 그림에서는 Star Schema를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> Star Schema의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 이 글에서 배울 것

- Star Schema의 구조
- Snowflake Schema와의 차이
- BI 도구가 Star Schema를 좋아하는 이유
- 설계 실습 5단계
- 입문 단계에서 자주 나오는 실수 5가지

## 왜 중요한가

분석 쿼리는 조인이 줄어들수록 읽기 쉽고 빠르게 동작합니다. Star Schema는 하나의 fact와 그 주위를 감싼 dimension으로 필요한 조인만 남긴 형태입니다. 그래서 BI 도구도 이 모양을 전제로 drill-down을 만들기 쉽습니다.

> 분석은 읽기의 게임입니다. 모양이 단순할수록 답도 빨리 나옵니다.

## 개념 한눈에 보기

## 핵심 용어

- **Star Schema**: 중앙 fact와 주변 dimension으로 이루어진 가장 단순한 분석 모델입니다.
- **Snowflake Schema**: dimension을 더 정규화해서 여러 홉을 거치게 만든 형태입니다.
- **Galaxy Schema**: 여러 fact가 공통 dimension을 공유하는 형태입니다.
- **Drill-down**: 요약에서 세부로 내려가는 탐색 방식입니다.
- **Slice and dice**: 여러 기준으로 부분 집합을 잘라 보는 분석 방식입니다.

## Before / After

**Before**: dim_user → dim_country → dim_continent처럼 조인이 길어져 BI 응답이 느려집니다.

**After**: dim_user 안에 country와 continent를 함께 두면 한 번의 조인으로 끝납니다.

## 실습: 설계 5단계

### 1단계 — fact 정의하기

```sql
CREATE TABLE fact_orders (
    order_id BIGINT,
    user_key BIGINT,
    product_key BIGINT,
    date_key INT,
    store_key BIGINT,
    amount NUMERIC(12, 2),
    qty INT
);
```

### 2단계 — dimension 정의하기

```sql
CREATE TABLE dim_product (
    product_key BIGINT PRIMARY KEY,
    product_id BIGINT,
    name TEXT,
    category TEXT,
    brand TEXT
);
```

### 3단계 — 별 모양 조인 만들기

```sql
SELECT p.category, SUM(f.amount) AS revenue
FROM fact_orders f
JOIN dim_product p ON p.product_key = f.product_key
GROUP BY p.category;
```

### 4단계 — 여러 dimension 연결하기

```sql
SELECT d.year, p.category, SUM(f.amount) AS revenue
FROM fact_orders f
JOIN dim_product p ON p.product_key = f.product_key
JOIN dim_date d ON d.date_key = f.date_key
GROUP BY d.year, p.category;
```

### 5단계 — drill-down 하기

```sql
-- Category to brand, one step deeper
SELECT p.brand, SUM(f.amount) AS revenue
FROM fact_orders f
JOIN dim_product p ON p.product_key = f.product_key
WHERE p.category = 'Coffee'
GROUP BY p.brand;
```

## 이 코드에서 먼저 봐야 할 점

- 조인 경로가 모두 fact와 dimension 사이 한 단계로 정리됩니다.
- category와 brand처럼 자주 함께 쓰는 속성은 같은 dimension에 두는 편이 실용적입니다.
- BI에서 보던 drill-down 동작이 거의 그대로 SQL로 이어집니다.

## 자주 하는 실수 5가지

1. **Snowflake처럼 과하게 정규화합니다.** 조인이 늘어나면서 BI 응답 속도가 떨어집니다.
2. **모든 컬럼을 fact에 몰아넣습니다.** 별 모양이 흐려지고 테이블 역할도 불분명해집니다.
3. **dimension을 지나치게 좁게 만듭니다.** 결국 필요한 속성을 다시 붙이느라 모델이 흔들립니다.
4. **surrogate key 없이 natural key만 사용합니다.** 상위 시스템 변경이 fact까지 전파됩니다.
5. **공유 가능한 dim을 fact마다 따로 만듭니다.** 기준 테이블이 갈라지면 숫자 해석도 달라지기 쉽습니다.

## 실무에서는 이렇게 나타납니다

Tableau, Looker, Power BI 같은 도구는 star schema를 전제로 가장 잘 동작하는 경우가 많습니다. dbt의 mart 레이어도 실무에서는 이런 별 모양으로 정리하는 일이 흔합니다.

## 실무에서는 이렇게 생각합니다

- 조인 한 번이 곧 비용이라는 감각으로 봅니다.
- dimension은 넓고 짧게 가져가되 의미를 분명히 둡니다.
- 속성 변화는 SCD 전략으로 다룹니다.
- BI 도구가 기대하는 가정을 데이터 모델에서 존중합니다.
- Snowflake는 이유가 분명할 때만 씁니다.

## 체크리스트

- [ ] Star와 Snowflake의 차이를 설명할 수 있다.
- [ ] Galaxy schema가 무엇인지 알고 있다.
- [ ] BI 도구가 왜 별 모양을 선호하는지 말할 수 있다.
- [ ] Drill-down 쿼리를 직접 작성할 수 있다.

## 연습 문제

1. fact_payments 주변에 둘 dimension 다섯 개를 적어 보세요.
2. Snowflake가 더 나은 예외 상황 하나를 설명해 보세요.
3. category → brand → product로 내려가는 drill-down을 적어 보세요.

## 마무리와 다음 글

Star Schema는 분석 모델을 단순하게 유지하면서도 자주 쓰는 질의를 빠르게 처리하기 좋은 형태입니다. 조인 구조가 짧고 설명이 명확하다는 점이 큰 장점입니다. 다음 글에서는 큰 테이블을 빠르게 읽기 위한 partition과 clustering을 살펴보겠습니다.

## 처음 질문으로 돌아가기

- **Star Schema는 왜 분석에서 가장 자주 보일까요?**
  - 본문의 기준은 Star Schema를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Snowflake Schema와는 어떤 점이 다를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **조인 홉 수가 성능과 가독성에 왜 중요할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Warehouse 101 (1/10): Data Warehouse란 무엇인가?](./01-what-is-data-warehouse.md)
- [Data Warehouse 101 (2/10): OLTP와 OLAP](./02-oltp-and-olap.md)
- [Data Warehouse 101 (3/10): Fact와 Dimension](./03-fact-and-dimension.md)
- **Star Schema (현재 글)**
- Partition과 Clustering (예정)
- ETL과 ELT (예정)
- BI와 Dashboard (예정)
- Data Mart (예정)
- 성능 최적화 (예정)
- Warehouse 설계 예제 (예정)

<!-- toc:end -->

## 참고 자료

- [Kimball — Star Schema](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/star-schemas/)
- [Microsoft — Star Schema and Power BI](https://learn.microsoft.com/en-us/power-bi/guidance/star-schema)
- [dbt — Mart Layer](https://docs.getdbt.com/best-practices/how-we-structure/4-marts)
- [Wikipedia — Star Schema](https://en.wikipedia.org/wiki/Star_schema)

Tags: DataWarehouse, StarSchema, Modeling, Snowflake, Analytics
