---
series: data-warehouse-101
episode: 10
title: Warehouse 설계 예제
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
  - Design
  - Example
  - EndToEnd
  - Analytics
seo_description: 전자상거래 Warehouse를 grain부터 mart까지 설계하는 전체 예제
last_reviewed: '2026-05-15'
---

# Warehouse 설계 예제

개별 개념을 따로 이해하는 것과 실제로 하나의 Warehouse를 설계하는 일은 다릅니다. 하나의 도메인을 처음부터 끝까지 따라가 보면 grain, dimension, schema, 적재 흐름, mart가 왜 그 자리에 놓이는지 훨씬 분명해집니다. 이 마지막 글은 앞선 개념을 한 번에 조립해 보는 예제입니다.

이 글은 Data Warehouse 101 시리즈의 마지막 글입니다.

## 이 글에서 다룰 문제

- Warehouse 설계는 왜 grain 한 줄에서 시작해야 할까요?
- fact, dimension, schema, partition, ETL, mart는 어떤 순서로 연결될까요?
- 전자상거래 도메인에서 어떤 dimension을 공통 자산으로 볼 수 있을까요?
- 설계를 문서 없이 진행하면 왜 금방 흔들릴까요?
- 완성된 Warehouse가 대시보드와 어떻게 이어지는지 어떻게 설명할까요?

## 이 글에서 배울 것

- 전자상거래 예제로 end-to-end 설계를 보는 법
- grain → dimension → schema → partition → ETL → mart의 순서
- 각 조각이 대시보드로 어떻게 이어지는지
- 설계 실습 5단계
- 입문 단계에서 자주 나오는 실수 5가지

## 왜 중요한가

개별 개념을 아는 것만으로는 설계를 설명하기 어렵습니다. 실제로는 각 조각이 왜 그 자리에 놓이는지 연결해서 보여 줄 수 있어야 합니다. 마지막 글인 이 예제가 바로 그 조립 과정을 한 번에 보여 줍니다.

> 깔끔한 설계는 거의 항상 grain 한 줄에서 시작합니다.

## 개념 한눈에 보기

![엔드투엔드 Warehouse 설계 흐름](https://yeongseon-books.github.io/book-public-assets/assets/data-warehouse-101/10/10-01-concept-at-a-glance.ko.png)

*원천 시스템에서 staging, fact/dimension, mart를 거쳐 최종 대시보드로 이어지는 전체 Warehouse 설계 흐름*

## 핵심 용어

- **Grain**: fact 한 행이 무엇을 의미하는지 적는 설계의 출발점입니다.
- **Conformed dimension**: 여러 fact가 함께 공유하는 차원입니다.
- **Surrogate key**: Warehouse가 발급하는 대체 식별자입니다.
- **Slowly Changing Dimension (SCD)**: 차원 속성 변화를 시간에 따라 기록하는 방식입니다.
- **Mart**: 소비자에게 바로 제공하는 주제별 최종 모델입니다.

## Before / After

**Before**: source DB를 직접 조회하며 분석할 때마다 SQL을 새로 작성해 느리고 비싸고 자주 깨집니다.

**After**: Warehouse에 star schema와 mart가 준비되어 있어 분석가가 짧은 SQL로 대시보드를 만듭니다.

## 실습: 5단계 설계

### 1단계 — grain 정의하기

> *fact_orders grain*: one row per *order*.

### 2단계 — dimension 식별하기

```text
dim_user      : user attributes
dim_product   : product attributes
dim_date      : date attributes (year, month, weekday)
dim_channel   : acquisition channel
```

### 3단계 — star schema 작성하기

```sql
CREATE TABLE fact_orders (
    order_id      STRING,
    order_date    DATE,
    user_key      INT64,
    product_key   INT64,
    channel_key   INT64,
    quantity      INT64,
    amount        NUMERIC
)
PARTITION BY order_date
CLUSTER BY user_key, product_key;
```

### 4단계 — ETL/ELT 흐름 정리하기

```text
source.orders  --(append)-->  staging.orders
                              |
                              v
              transform: surrogate keys, SCD type 2
                              |
                              v
                       fact_orders / dim_*
```

### 5단계 — mart와 대시보드 연결하기

```sql
CREATE OR REPLACE VIEW mart_sales AS
SELECT
    d.year,
    d.month,
    p.category,
    SUM(f.amount) AS revenue
FROM fact_orders f
JOIN dim_date d    ON d.date_key   = f.order_date
JOIN dim_product p ON p.product_key = f.product_key
GROUP BY d.year, d.month, p.category;
```

## 이 코드에서 먼저 봐야 할 점

- grain 한 줄이 fact 구조와 dimension 범위를 함께 결정합니다.
- surrogate key를 두면 source 시스템의 키 변경을 완충할 수 있습니다.
- mart는 raw 데이터를 그대로 노출하는 곳이 아니라 대시보드에 맞춰 준비된 답을 제공하는 계층입니다.

## 자주 하는 실수 5가지

1. **grain을 문서에 명확히 적지 않습니다.** 한 줄 정의가 없으면 모델 경계가 계속 흔들립니다.
2. **모든 컬럼을 fact에 몰아넣습니다.** 속성은 dimension으로 분리해야 모델이 단순해집니다.
3. **source key를 그대로 재사용합니다.** 상위 시스템 변경이 곧바로 Warehouse 문제로 이어질 수 있습니다.
4. **SCD를 고려하지 않습니다.** 과거 기준으로 다시 봐야 할 때 숫자가 어긋납니다.
5. **mart 없이 raw fact를 대시보드에 직접 연결합니다.** 작은 구조 변경도 사용자 화면에 바로 충격을 줍니다.

## 실무에서는 이렇게 나타납니다

실무에서는 한 페이지 안팎의 design doc에 grain, dimension, partition, owner를 먼저 적는 경우가 많습니다. 리뷰가 끝나면 PR로 DDL과 변환 모델을 올리고, 이어서 ETL DAG를 추가합니다. 대시보드는 가능하면 mart만 바라보도록 경계를 분명히 둡니다.

## 실무에서는 이렇게 생각합니다

- 항상 grain부터 정의합니다.
- Conformed dimension은 조직 전체 자산으로 공유합니다.
- fact/dimension과 mart 사이의 경계를 분명히 둡니다.
- 오너 없는 테이블은 만들지 않습니다.
- 문서 없는 설계는 설계가 아니라고 봅니다.

## 체크리스트

- [ ] Grain을 한 줄 문장으로 적을 수 있다.
- [ ] Conformed dimension의 의미를 설명할 수 있다.
- [ ] Star schema DDL을 직접 작성할 수 있다.
- [ ] Mart와 fact의 차이를 명확히 말할 수 있다.

## 연습 문제

1. 블로그 댓글 시스템의 grain과 dimension을 적어 보세요.
2. 광고 클릭 로그를 위한 fact_clicks를 설계해 보세요.
3. 월간 매출 대시보드를 위한 mart view SQL을 적어 보세요.

## 마무리와 다음 글

이제는 grain에서 시작해 dimension, fact, partition, 적재 흐름, mart, 대시보드까지 하나의 흐름으로 연결해서 볼 수 있어야 합니다. 개별 개념을 외우는 단계보다 중요한 것은 이 연결 관계를 이해하는 일입니다. 다음 시리즈에서는 이렇게 준비한 데이터를 바탕으로 Data Science와 MLOps로 한 걸음 더 나아가겠습니다.

<!-- toc:begin -->
- [Data Warehouse란 무엇인가?](./01-what-is-data-warehouse.md)
- [OLTP와 OLAP](./02-oltp-and-olap.md)
- [Fact와 Dimension](./03-fact-and-dimension.md)
- [Star Schema](./04-star-schema.md)
- [Partition과 Clustering](./05-partition-and-clustering.md)
- [ETL과 ELT](./06-etl-and-elt.md)
- [BI와 Dashboard](./07-bi-and-dashboard.md)
- [Data Mart](./08-data-mart.md)
- [성능 최적화](./09-performance-optimization.md)
- **Warehouse 설계 예제 (현재 글)**
<!-- toc:end -->

## 참고 자료

- [Kimball Group — Dimensional Modeling Techniques](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)
- [BigQuery — Schema Design Best Practices](https://cloud.google.com/bigquery/docs/best-practices-schema-design)
- [dbt — How We Structure Our Projects](https://docs.getdbt.com/best-practices/how-we-structure/1-guide-overview)
- [Snowflake — Data Modeling](https://docs.snowflake.com/en/user-guide/table-considerations)

Tags: DataWarehouse, Design, Example, EndToEnd, Analytics
