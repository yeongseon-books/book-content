---
series: data-warehouse-101
episode: 8
title: "Data Warehouse 101 (8/10): Data Mart"
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
last_reviewed: '2026-05-15'
---

# Data Warehouse 101 (8/10): Data Mart

이 글은 데이터 웨어하우스 101 시리즈의 8번째 글입니다.

Warehouse는 전사 공통 데이터를 모으는 중심 저장소입니다. 하지만 영업, 재무, 운영 팀은 같은 데이터를 두고도 다른 용어와 다른 기준으로 질문합니다. Data Mart는 이런 차이를 흡수해서 각 팀이 바로 쓸 수 있는 형태로 다시 정리한 얇은 계층입니다.


![Data Warehouse 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-warehouse-101/08/08-01-concept-at-a-glance.ko.png)
*Data Warehouse 101 8장 흐름 개요*
> Data Mart는 '중앙 집중식 정의 + 분산식 적응'의 균형으로 설계합니다.

## 먼저 던지는 질문

- Data Mart는 Warehouse와 무엇이 다를까요?
- 조직 공통 데이터와 팀 전용 분석 영역은 왜 분리할까요?
- 도메인별 vocabulary를 데이터 모델에 반영하면 무엇이 좋아질까요?

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

Data Mart는 Warehouse의 중앙 저장소에서 특정 조직이나 용도로 준비한 작은 저장소입니다. 각 팀이 필요한 뷰를 자유롭게 만들되, 기초가 되는 Fact와 Dimension은 중앙에서 일관되게 관리합니다.

## 핵심 용어

- **Data Mart**: 특정 도메인이나 팀에 맞춰 좁힌 분석 구역입니다.
- **Conformed Dimension**: 여러 mart가 함께 쓰는 공통 차원입니다.
- **Domain Modeling**: 팀의 용어와 규칙에 맞춰 데이터를 다시 읽는 모델링입니다.
- **Aggregated Mart**: 반복 집계를 미리 계산해 둔 mart입니다.
- **Self-service**: 분석가가 직접 조회하고 활용할 수 있는 사용 방식입니다.

## 전후 비교

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

## 데이터 마트 유형

Data Mart는 생성 방식과 데이터 소스에 따라 세 가지로 분류할 수 있습니다.

| 유형 | 데이터 소스 | 갱신 방식 | 적합 조직 | 특징 |
|---|---|---|---|---|
| 종속형 (Dependent) | Warehouse에서 파생 | Warehouse 변경 시 자동 반영 | 대기업, 중앙 집중식 조직 | Conformed dimension 공유, 일관성 높음 |
| 독립형 (Independent) | OLTP 시스템에서 직접 추출 | 팀별 ETL 파이프라인 | 소규모 조직, 신속한 MVP | 구축 빠르지만 중복 높고 일관성 낮음 |
| 하이브리드 (Hybrid) | Warehouse + 도메인 특화 소스 | 공통 부분은 Warehouse, 특화 부분은 직접 | 중간 규모 조직 | 유연성과 일관성의 균형 |

종속형 mart는 중앙 Warehouse의 일관된 정의를 그대로 사용하므로 숫자가 팀마다 달라지지 않습니다. 독립형은 구축이 빠르지만 나중에 통합하기 어려워질 수 있습니다. 하이브리드는 두 방식의 장점을 혼합합니다.


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

## SQL 예제: 마트 생성 CTAS

아래는 CTAS(Create Table As Select)를 사용해 마트 테이블을 물리적으로 생성하는 예제입니다.

```sql
CREATE TABLE sales_mart.monthly_pipeline AS
SELECT
    DATE_TRUNC('month', o.created_at) AS month,
    u.region,
    o.stage,
    COUNT(*) AS opp_count,
    SUM(o.amount) AS pipeline_amount,
    AVG(o.amount) AS avg_deal_size
FROM staging.opportunities o
JOIN warehouse.dim_user u ON u.user_key = o.owner_key
WHERE o.created_at >= '2025-01-01'
GROUP BY 1, 2, 3;
```

이 마트는 월별, 지역별, 단계별로 파이프라인 요약을 미리 계산해 둡니다. 대시보드는 이 테이블에서 바로 읽으므로 응답 속도가 빠릅니다.

```sql
-- 마트 갱신 (일별 스케줄)
TRUNCATE sales_mart.monthly_pipeline;
INSERT INTO sales_mart.monthly_pipeline
SELECT ...; -- 위 쿼리 재실행
```

물리적으로 저장하면 조회 속도가 빠르지만 저장 공간이 필요하고 갱신 주기를 관리해야 합니다. 비교를 위해 뷰로 만든 경우도 보겠습니다.

```sql
-- 같은 로직을 뷰로 정의
CREATE OR REPLACE VIEW sales_mart.monthly_pipeline_view AS
SELECT ...; -- 위와 동일
```

뷰는 갱신 부담이 없지만 조회할 때마다 계산하므로 느릴 수 있습니다.


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

## 마트 vs 뷰 vs 물리화된 뷰

마트를 구현하는 세 가지 방식은 각각 장단점이 있습니다.

### 테이블 (CTAS)

물리적으로 저장되므로 조회 속도가 빠릅니다. 대신 저장 공간을 사용하고, 갱신 주기를 명시적으로 관리해야 합니다. 대시보드가 자주 조회되고 데이터 양이 크면 테이블이 적합합니다.

```sql
CREATE TABLE marts.daily_summary AS SELECT ...;
```

### 뷰 (View)

저장 공간을 사용하지 않고 항상 최신 데이터를 반환합니다. 대신 조회할 때마다 원본 테이블을 스캔하므로 느릴 수 있습니다. 데이터 양이 작고 실시간성이 중요하면 뷰가 적합합니다.

```sql
CREATE OR REPLACE VIEW marts.daily_summary AS SELECT ...;
```

### 물리화된 뷰 (Materialized View)

결과를 물리적으로 저장하면서 자동 갱신을 지원하는 중간 방식입니다. BigQuery, Snowflake, PostgreSQL 등이 지원하며, 갱신 주기는 Warehouse 엔진이 관리합니다.

```sql
CREATE MATERIALIZED VIEW marts.daily_summary AS SELECT ...;
REFRESH MATERIALIZED VIEW marts.daily_summary;
```

세 방식 중 선택은 데이터 크기, 조회 빈도, 실시간성 요구, 비용 제약을 모두 고려해 결정합니다.


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

Mart는 팀과 공통 데이터 모델 사이를 연결하는 얇은 다리입니다. 좋은 mart는 팀별 용어를 반영하면서도 공통 기준을 깨지 않습니다. 다음 글에서는 이렇게 쌓아 올린 모델을 더 빠르고 저렴하게 읽기 위한 성능 최적화 패턴을 봅니다.


## Data Mart 운영 모델을 표로 정리하기

Data Mart는 단순 복사본이 아니라 소비자 관점의 재구성 계층입니다. 어떤 마트를 만들지 결정할 때는 도메인 경계, 소유자, 갱신 주기를 먼저 정해야 합니다.

| 마트 유형 | 목적 | 데이터 원천 | 갱신 주기 | 주 소유자 |
| --- | --- | --- | --- | --- |
| Sales Mart | 파이프라인/매출 분석 | 주문, 고객, 채널 | 시간당 | 영업 분석팀 |
| Finance Mart | 정산/손익 검증 | 결제, 환불, 회계분류 | 일배치 | 재무 데이터팀 |
| Product Mart | 기능 사용성 분석 | 이벤트 로그, 실험 데이터 | 15분~시간 | 제품 분석팀 |
| Ops Mart | 운영 모니터링 | 물류, SLA, 장애 이벤트 | 5분~시간 | 운영팀 |

이 표처럼 목적과 오너를 명확히 두면 마트 스키마가 불필요하게 비대해지는 것을 막을 수 있습니다.

## 공통 차원(Conformed Dimension) 관리 원칙

마트를 빠르게 만들다 보면 팀마다 서로 다른 고객/상품 차원을 만들기 쉽습니다. 장기적으로는 지표 충돌 원인이 되므로 공통 차원 정책이 필수입니다.

```yaml
conformed_dimensions:
  dim_customer:
    steward: "data-governance"
    required_keys: [customer_key, customer_id]
    scd_type: 2
  dim_product:
    steward: "commerce-data"
    required_keys: [product_key, product_id]
    scd_type: 1
  dim_date:
    steward: "platform"
    required_keys: [date_key, full_date]
    scd_type: 0
```

여기서 핵심은 "각 마트가 자유롭게 뷰를 구성하되, 기준 차원은 중앙에서 관리"하는 균형입니다.

## Mart 빌드 SQL 패턴

아래는 Sales Mart를 빌드할 때 자주 쓰는 패턴입니다.

```sql
CREATE OR REPLACE TABLE sales_mart.fact_daily_revenue AS
SELECT
    d.full_date,
    c.segment,
    ch.channel_name,
    SUM(f.amount) AS revenue,
    COUNT(DISTINCT f.order_id) AS orders
FROM warehouse.fact_orders f
JOIN warehouse.dim_date d ON d.date_key = f.date_key
JOIN warehouse.dim_customer c ON c.customer_key = f.customer_key
JOIN warehouse.dim_channel ch ON ch.channel_key = f.channel_key
GROUP BY 1, 2, 3;
```

이 패턴은 소비자에게 필요한 수준의 사전 집계를 제공해 대시보드 쿼리를 단순화합니다. 다만 과도한 사전 집계는 유연성을 떨어뜨릴 수 있으므로 사용 빈도가 높은 질문에 한정하는 편이 좋습니다.

## 마트 품질 검증 체크

마트가 늘수록 검증 자동화가 중요해집니다. 최소한 다음 항목은 배포 전에 확인해야 합니다.

1. 기본 키 중복이 없는가
2. 공통 지표 정의가 중앙 기준과 일치하는가
3. 갱신 지연이 SLA 이내인가
4. 권한이 도메인 경계에 맞게 분리되었는가

이 네 가지가 안정적으로 유지되면 마트가 늘어나도 조직 전체 숫자 해석은 흔들리지 않습니다.


## 도메인별 마트 설계 예시 확장

데이터 마트는 팀의 질문 단위를 모델에 반영하는 작업입니다. 예를 들어 재무팀은 "확정 매출"과 "정산 예정"을 구분해 보지만, 제품팀은 동일 기간의 "활성 사용자당 매출"을 더 자주 봅니다. 따라서 같은 fact를 공유하더라도 mart 표현은 달라집니다.

```sql
CREATE OR REPLACE VIEW finance_mart.v_revenue_settlement AS
SELECT
    d.full_date,
    SUM(CASE WHEN f.status = 'paid' THEN f.amount ELSE 0 END) AS booked_revenue,
    SUM(CASE WHEN f.status = 'pending' THEN f.amount ELSE 0 END) AS pending_revenue
FROM warehouse.fact_orders f
JOIN warehouse.dim_date d ON d.date_key = f.date_key
GROUP BY d.full_date;
```

같은 데이터를 팀 언어로 안전하게 번역하는 것이 마트의 본질입니다.

## 데이터 거버넌스 정책 표

| 정책 항목 | 내용 | 책임 |
| --- | --- | --- |
| 지표 정의 승인 | 공통 지표 변경은 거버넌스 리뷰 필수 | 데이터 거버넌스 |
| 접근 권한 | 도메인 역할 기반 최소 권한 | 보안/플랫폼 |
| 라인리지 기록 | mart 컬럼의 상류 lineage 추적 | 데이터 플랫폼 |
| 변경 공지 | breaking change 사전 공지 | mart 오너 |

정책이 없으면 마트가 늘어날수록 조직 내 지표 신뢰가 빠르게 약해집니다.

## 메타데이터 관리 포인트

마트 품질은 테이블 데이터만으로 판단하기 어렵습니다. 컬럼 설명, 오너, 갱신 주기, 품질 상태 같은 메타데이터를 함께 관리해야 사용자가 자신 있게 소비할 수 있습니다.


## 실무 적용 메모

아래 메모는 해당 장의 개념을 실제 운영 환경에 옮길 때 반복적으로 확인하는 항목을 정리한 것입니다. 단순히 지식을 아는 것과 운영에서 안정적으로 반복하는 것은 다르기 때문에, 팀 단위 규칙으로 문서화해 두는 편이 좋습니다.

| 점검 영역 | 질문 | 권장 기준 |
| --- | --- | --- |
| 데이터 정의 | 같은 용어를 팀마다 다르게 쓰는가 | 용어집과 지표 정의를 단일 출처로 관리 |
| 파이프라인 안정성 | 재실행 시 결과가 동일한가 | idempotent 원칙, 상태 테이블 관리 |
| 비용 통제 | 월별 비용이 예측 가능한가 | 스캔 바이트, 고비용 쿼리 상위 추적 |
| 품질 보증 | 잘못된 데이터 유입을 조기에 잡는가 | null/중복/범위 검증 자동화 |
| 책임 분리 | 장애 시 소유자가 명확한가 | 계층별 owner와 on-call 채널 지정 |

운영에서는 기술 선택보다 경계와 책임이 더 큰 차이를 만듭니다. 예를 들어 모델이 훌륭해도 지표 소유자가 없으면 숫자 불일치 이슈가 장기간 방치될 수 있습니다. 반대로 도구가 완벽하지 않아도 책임 경계가 명확하면 복구 속도와 개선 속도가 빠릅니다.

```yaml
operating_baseline:
  contracts:
    raw: "append-only and replayable"
    transform: "test-required before publish"
    serving: "semantic definitions are versioned"
  quality_checks:
    - not_null
    - unique_key
    - accepted_values
    - referential_integrity
  cost_controls:
    - heavy_query_review_weekly
    - partition_filter_required
    - select_star_block_in_pr
  ownership:
    data_platform: "ingestion and storage"
    analytics_engineering: "transform and marts"
    domain_analytics: "metric definition and dashboard"
```

이 기준을 프로젝트 초기에 합의하면, 시리즈에서 다룬 개념이 문서 지식으로 끝나지 않고 운영 습관으로 정착됩니다. 특히 신규 팀원이 합류했을 때 학습 속도가 빨라지고, 장애나 지표 충돌 같은 사건이 생겨도 공통된 기준으로 빠르게 의사결정을 내릴 수 있습니다.

또한 분기 단위 회고에서는 기술 성능 지표뿐 아니라 의사결정 지표도 함께 보는 것이 좋습니다. 예를 들어 "대시보드 숫자 논쟁으로 소모된 회의 시간", "지표 정의 변경 후 영향 범위 확인 시간", "재처리 요청 처리 리드타임" 같은 운영 지표를 추적하면 데이터 조직의 성숙도를 더 현실적으로 파악할 수 있습니다.


## 실전 앵커: 모델, 파이프라인, 성능 검증

아래 예시는 이 글의 개념을 실제 운영으로 옮길 때 바로 재사용할 수 있는 최소 앵커입니다. 스키마, 적재 설정, 성능 비교를 한 묶음으로 두면 설계 논의가 추상 수준에서 끝나지 않고 실행 가능한 결정으로 이어집니다.

```sql
-- 공통 분석 질의 템플릿: 기간 + 세그먼트 + 지표
WITH scoped AS (
    SELECT
        f.date_key,
        f.amount,
        f.qty,
        c.segment,
        p.category
    FROM fact_sales f
    JOIN dim_customer c ON c.customer_key = f.customer_key
    JOIN dim_product p ON p.product_key = f.product_key
    WHERE f.date_key BETWEEN 20260101 AND 20260331
)
SELECT
    segment,
    category,
    SUM(amount) AS revenue,
    SUM(qty) AS units,
    COUNT(*) AS order_lines,
    ROUND(SUM(amount) / NULLIF(COUNT(*), 0), 2) AS avg_line_amount
FROM scoped
GROUP BY 1, 2
ORDER BY revenue DESC;
```

```yaml
pipeline_contract:
  schedule: "0 * * * *"
  source:
    type: cdc
    lag_slo_minutes: 15
  transform:
    engine: dbt
    model_layers: [stg, int, mart]
  quality_tests:
    - not_null
    - unique
    - relationships
    - accepted_values
  publish:
    target: mart_sales_daily
    strategy: merge
```

```mermaid
flowchart LR
    A["OLTP 주문/결제"] --> B["Raw 적재"]
    B --> C["Staging 정제"]
    C --> D["Fact/Dimension 모델"]
    D --> E["Mart 집계"]
    E --> F["대시보드/리포트"]
```

성능 비교는 반드시 동일 조건에서 수행해야 합니다. 파티션 필터 유무, 조인 순서, 집계 단위를 고정하지 않으면 숫자가 설계를 설명하지 못합니다.

| 비교 항목 | 조건 A(비최적화) | 조건 B(최적화) | 해석 |
| --- | --- | --- | --- |
| 스캔 바이트 | 480GB | 62GB | 파티션 프루닝이 대부분의 차이를 만듭니다. |
| 실행 시간 | 94초 | 18초 | 집계 이전 필터링으로 셔플 비용이 줄어듭니다. |
| 슬롯/크레딧 사용량 | 높음 | 중간 | 비용 안정성이 높아집니다. |
| 재현성 | 낮음 | 높음 | 표준 템플릿 쿼리 사용 시 비교 가능성이 유지됩니다. |

운영에서는 "정확한 한 번"보다 "안전한 재실행"이 더 중요한 경우가 많습니다. 그래서 적재 키를 두고 upsert 기준을 명확히 정의하는 방식이 필요합니다.

```sql
-- 재실행 가능한 머지 예시
MERGE INTO mart_sales_daily t
USING (
    SELECT
        d.full_date,
        c.segment,
        p.category,
        SUM(f.amount) AS revenue,
        SUM(f.qty) AS units
    FROM fact_sales f
    JOIN dim_date d ON d.date_key = f.date_key
    JOIN dim_customer c ON c.customer_key = f.customer_key
    JOIN dim_product p ON p.product_key = f.product_key
    WHERE d.full_date >= CURRENT_DATE - INTERVAL '7 day'
    GROUP BY 1, 2, 3
) s
ON t.full_date = s.full_date
AND t.segment = s.segment
AND t.category = s.category
WHEN MATCHED THEN UPDATE SET
    revenue = s.revenue,
    units = s.units,
    updated_at = CURRENT_TIMESTAMP
WHEN NOT MATCHED THEN INSERT (
    full_date, segment, category, revenue, units, updated_at
) VALUES (
    s.full_date, s.segment, s.category, s.revenue, s.units, CURRENT_TIMESTAMP
);
```

이 패턴을 기준선으로 두면, 모델 변경이나 파이프라인 장애가 생겨도 영향을 계층별로 좁혀 복구할 수 있습니다. 데이터 웨어하우스 운영은 쿼리 한두 개의 튜닝보다, 반복 가능한 설계 계약을 지키는 과정에 더 가깝습니다.


### 운영 확장 메모

데이터 웨어하우스를 오래 운영하면 기술 선택보다 운영 규율이 성능과 신뢰도를 좌우합니다. 다음 예시는 팀에서 반복적으로 사용하는 점검 묶음입니다.

```sql
-- 파티션 필터 누락 탐지용 예시
EXPLAIN
SELECT category, SUM(amount) AS revenue
FROM fact_sales
WHERE date_key BETWEEN 20260101 AND 20260131
GROUP BY category;
```

```yaml
review_policy:
  query_rules:
    - require_partition_filter: true
    - block_select_star_on_fact: true
    - require_owner_for_metric_change: true
  incident_rules:
    - classify: [schema_change, pipeline_lag, quality_failure]
    - first_response_minutes: 15
```

```mermaid
flowchart LR
    A["모델 변경 요청"] --> B["영향 범위 분석"]
    B --> C["샘플 검증 쿼리"]
    C --> D["배치 재실행"]
    D --> E["지표 대조"]
    E --> F["배포 승인"]
```

아키텍처가 단순해 보여도, 계약과 검증 루프를 문서화해 두면 신규 인원이 합류해도 같은 품질을 유지할 수 있습니다.


### 운영 확장 메모

데이터 웨어하우스를 오래 운영하면 기술 선택보다 운영 규율이 성능과 신뢰도를 좌우합니다. 다음 예시는 팀에서 반복적으로 사용하는 점검 묶음입니다.

```sql
-- 파티션 필터 누락 탐지용 예시
EXPLAIN
SELECT category, SUM(amount) AS revenue
FROM fact_sales
WHERE date_key BETWEEN 20260101 AND 20260131
GROUP BY category;
```

```yaml
review_policy:
  query_rules:
    - require_partition_filter: true
    - block_select_star_on_fact: true
    - require_owner_for_metric_change: true
  incident_rules:
    - classify: [schema_change, pipeline_lag, quality_failure]
    - first_response_minutes: 15
```

```mermaid
flowchart LR
    A["모델 변경 요청"] --> B["영향 범위 분석"]
    B --> C["샘플 검증 쿼리"]
    C --> D["배치 재실행"]
    D --> E["지표 대조"]
    E --> F["배포 승인"]
```

아키텍처가 단순해 보여도, 계약과 검증 루프를 문서화해 두면 신규 인원이 합류해도 같은 품질을 유지할 수 있습니다.

## 처음 질문으로 돌아가기

- **Data Mart는 Warehouse와 어떻게 다른가요?**
  - Warehouse는 전사 통합 저장소, Data Mart는 특정 팀이나 용도의 전문 저장소입니다.
- **각 팀이 따로 Data Mart를 만들면 데이터 정의가 달라질 수 있지 않을까요?**
  - Fact와 Dimension의 정의는 중앙에서 관리하고, 선택과 조합은 각 Mart에서 합니다.
- **Data Mart의 크기가 너무 커지면 어떻게 할까요?**
  - 용도별로 추가로 분해하거나, Warehouse로 돌아가 구조를 재설계합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Warehouse 101 (1/10): Data Warehouse란 무엇인가?](./01-what-is-data-warehouse.md)
- [Data Warehouse 101 (2/10): OLTP와 OLAP](./02-oltp-and-olap.md)
- [Data Warehouse 101 (3/10): Fact와 Dimension](./03-fact-and-dimension.md)
- [Data Warehouse 101 (4/10): Star Schema](./04-star-schema.md)
- [Data Warehouse 101 (5/10): Partition과 Clustering](./05-partition-and-clustering.md)
- [Data Warehouse 101 (6/10): ETL과 ELT](./06-etl-and-elt.md)
- [Data Warehouse 101 (7/10): BI와 Dashboard](./07-bi-and-dashboard.md)
- **Data Mart (현재 글)**
- 성능 최적화 (예정)
- Warehouse 설계 예제 (예정)

<!-- toc:end -->

## 참고 자료

- [Kimball — Data Mart](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)
- [dbt — Mart Layer](https://docs.getdbt.com/best-practices/how-we-structure/4-marts)
- [Snowflake — Schema Design](https://docs.snowflake.com/en/user-guide/intro-key-concepts)
- [Wikipedia — Data Mart](https://en.wikipedia.org/wiki/Data_mart)

- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/data-warehouse-101/ko)

Tags: DataWarehouse, DataMart, Modeling, Domain, Analytics
