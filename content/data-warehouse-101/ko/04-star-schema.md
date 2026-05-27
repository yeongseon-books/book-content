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

![Data Warehouse 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-warehouse-101/04/04-01-concept-at-a-glance.ko.png)
*Data Warehouse 101 4장 흐름 개요*
> Star Schema는 '정규화 vs 비정규화' 균형을 일관되게 유지해 쿼리 성능과 유지보수 비용 둘 다 낮춥니다.

## 먼저 던지는 질문

- Star Schema는 왜 분석에서 가장 자주 보일까요?
- Snowflake Schema와는 어떤 점이 다를까요?
- 조인 홉 수가 성능과 가독성에 왜 중요할까요?

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

Star Schema는 중앙의 Fact 테이블과 그 주변의 Dimension 테이블들로 이루어집니다. 모든 분석이 Fact에서 시작하므로 조인 경로가 간단하고, 비즈니스 관점의 쿼리를 자연스럽게 구성할 수 있습니다.

## 핵심 용어

- **Star Schema**: 중앙 fact와 주변 dimension으로 이루어진 가장 단순한 분석 모델입니다.
- **Snowflake Schema**: dimension을 더 정규화해서 여러 홉을 거치게 만든 형태입니다.
- **Galaxy Schema**: 여러 fact가 공통 dimension을 공유하는 형태입니다.
- **Drill-down**: 요약에서 세부로 내려가는 탐색 방식입니다.
- **Slice and dice**: 여러 기준으로 부분 집합을 잘라 보는 분석 방식입니다.

## 전후 비교

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

Star Schema는 분석 모델을 단순하게 유지하면서도 자주 쓰는 질의를 빠르게 처리하기 좋은 형태입니다. 조인 구조가 짧고 설명이 명확하다는 점이 큰 장점입니다. 다음 글에서는 큰 테이블을 빠르게 읽기 위한 partition과 clustering을 봅니다.

## Star Schema를 DDL로 구현해 보기

Star Schema의 장점은 설명이 쉬운 구조라는 사실입니다. 중심 fact 하나와 주변 dimension 몇 개만 합의되면 대부분의 BI 질의가 예측 가능한 조인 경로를 가집니다. 아래는 전자상거래 기준 최소 스키마입니다.

```sql
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE,
    year INT,
    quarter INT,
    month INT,
    day INT,
    weekday INT
);

CREATE TABLE dim_store (
    store_key BIGINT PRIMARY KEY,
    store_id BIGINT,
    region TEXT,
    city TEXT
);

CREATE TABLE fact_orders (
    order_id BIGINT,
    date_key INT,
    product_key BIGINT,
    user_key BIGINT,
    store_key BIGINT,
    quantity INT,
    amount NUMERIC(12, 2)
);
```

이 구조에서 분석 질의는 항상 `fact_orders`에서 시작하고 필요한 dimension을 붙입니다. 경로가 단순하므로 쿼리 리뷰도 쉬워집니다.

## Star vs Snowflake 선택 기준

정규화를 더 진행한 Snowflake가 언제나 나쁜 것은 아닙니다. 다만 BI 소비 관점에서는 조인 홉이 증가할수록 복잡성과 비용이 함께 상승합니다.

| 항목 | Star Schema | Snowflake Schema |
| --- | --- | --- |
| 조인 수 | 적음 | 많음 |
| 쿼리 가독성 | 높음 | 낮아지기 쉬움 |
| 저장 중복 | 다소 높음 | 상대적으로 낮음 |
| BI 도구 적합성 | 높음 | 설정 난이도 증가 |
| 변경 영향 | 국소적 | 연쇄 영향 가능 |

대부분의 팀은 Star로 시작하고, 저장 비용이나 데이터 거버넌스 요구가 명확할 때 일부 차원만 Snowflake화하는 절충안을 택합니다.

## 설계 리뷰 체크포인트

Star Schema는 단순해 보이지만, 초기에 놓치기 쉬운 항목이 있습니다.

- fact grain이 한 줄로 선언되어 있는가
- 모든 fact 키가 surrogate key로 연결되는가
- dimension에 비즈니스 속성이 충분히 포함되어 있는가
- 대시보드 주요 질문이 2~3개 조인 안에서 해결되는가

이 네 가지를 충족하면 모델 수명주기가 길어집니다. 반대로 초기에는 간단해 보여도 나중에 뷰와 임시 테이블이 과도하게 늘어날 가능성이 큽니다.

## BI 소비를 고려한 컬럼 정책

실무에서는 모델 정확성 못지않게 소비 편의성이 중요합니다. 다음 정책이 도움이 됩니다.

```yaml
star_schema_conventions:
  naming:
    fact_prefix: "fact_"
    dim_prefix: "dim_"
    key_suffix: "_key"
  date_policy:
    require_dim_date_join: true
  null_policy:
    unknown_dimension_row: true
  semantic_layer:
    metrics_defined_in_mart: true
```

컬럼명, 키 접미사, 날짜 정책이 통일되면 BI 도구에서 자동 필드 매핑이 쉬워지고, 신규 팀원이 모델을 익히는 시간도 줄어듭니다.

## Star Schema 쿼리 패턴 확장

Star Schema가 좋은 이유는 같은 질문군을 반복 가능한 쿼리 패턴으로 만들 수 있기 때문입니다.

```sql
-- 월별 카테고리 매출
SELECT d.year, d.month, p.category, SUM(f.amount) AS revenue
FROM fact_orders f
JOIN dim_date d ON d.date_key = f.date_key
JOIN dim_product p ON p.product_key = f.product_key
GROUP BY d.year, d.month, p.category;

-- 지역별 주문 수
SELECT s.region, COUNT(*) AS orders
FROM fact_orders f
JOIN dim_store s ON s.store_key = f.store_key
GROUP BY s.region;
```

이처럼 중심 fact와 독립 dimension 조합으로 대부분의 질문을 커버할 수 있어, BI 모델도 안정적으로 유지됩니다.

## 아키텍처 비교 관점

| 비교 항목 | Star 중심 설계 | 과도한 정규화 설계 |
| --- | --- | --- |
| 신규 분석가 온보딩 | 빠름 | 느림 |
| 대시보드 유지보수 | 단순 | 조인 경로 복잡 |
| 스키마 이해 난이도 | 낮음 | 높음 |
| 오류 추적 | 쉬움 | 다단계 추적 필요 |

저장 공간만 보면 정규화가 유리할 수 있지만, 분석 조직에서는 해석 비용과 개발 비용이 더 큰 비중을 차지하는 경우가 많습니다.

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

- **Star Schema에서 Fact 테이블은 왜 중앙에 두나요?**
  - Fact가 중앙에 있으면 모든 분석 관점(Dimension)이 균등한 거리에 있어 조인 구조가 간단합니다.
- **Snowflake Schema는 Star Schema와 무엇이 다를까요?**
  - Snowflake는 Dimension을 추가로 정규화해 저장 공간을 절약하지만, 조인이 복잡해집니다.
- **Star Schema에서 역정규화가 왜 필요한가요?**
  - 읽기 성능을 최우선으로 하는 분석 워크로드에서는 조인을 줄이기 위해 의도적으로 중복을 허용합니다.

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

- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/data-warehouse-101/ko)

Tags: DataWarehouse, StarSchema, Modeling, Snowflake, Analytics
