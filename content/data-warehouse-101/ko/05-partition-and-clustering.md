---
series: data-warehouse-101
episode: 5
title: "Data Warehouse 101 (5/10): Partition과 Clustering"
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
  - Partition
  - Clustering
  - Performance
  - Analytics
seo_description: Partition과 Clustering의 차이, pruning 원리, 빠른 읽기의 두 축
last_reviewed: '2026-05-15'
---

# Data Warehouse 101 (5/10): Partition과 Clustering

Warehouse fact는 수십억 행까지 커지는 일이 흔합니다. 이때 중요한 것은 더 빨리 읽는 것만이 아니라 아예 읽지 않아도 되는 데이터를 건너뛰는 일입니다. 날짜 기준 partition만 잘 잡아도 대부분의 데이터를 스캔하지 않고 넘어갈 수 있고, 그만큼 비용도 바로 줄어듭니다.

이 글은 Data Warehouse 101 시리즈의 5번째 글입니다.

## 먼저 던지는 질문

- Partition과 Clustering은 각각 어떤 문제를 해결할까요?
- Pruning은 실제로 어떻게 비용을 줄일까요?
- Partition key와 cluster key는 어떤 기준으로 고를까요?

## 큰 그림

![Data Warehouse 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-warehouse-101/05/05-01-concept-at-a-glance.ko.png)

*Data Warehouse 101 5장 흐름 개요*

Partition은 큰 테이블을 범위 기준(보통 날짜)으로 나누어 필요한 부분만 스캔하고, Clustering은 같은 값들을 물리적으로 가깝게 배치해 필터링 성능을 높입니다. 둘을 함께 쓰면 대용량 테이블의 쿼리 성능이 획기적으로 개선됩니다.

> Partition은 메타데이터 기반 스캔 범위 축소, Clustering은 물리적 배치 기반 I/O 축소로 각각 다른 방식으로 성능을 높입니다.

## 이 글에서 배울 것

- Partition의 정의와 효과
- Clustering의 정의와 효과
- Pruning이 동작하는 방식
- 적용 실습 5단계
- 입문 단계에서 자주 나오는 실수 5가지

## 왜 중요한가

Warehouse fact 테이블은 쉽게 수십억 행으로 커집니다. 날짜 기준 partition만 잘 잡아도 엔진은 읽지 않아도 될 데이터를 대부분 건너뜁니다. 이 절약이 곧 속도와 비용 둘 다에 바로 연결됩니다.

> 읽지 않은 데이터에는 비용을 내지 않습니다.

## 개념 한눈에 보기

Partition은 큰 테이블을 범위(보통 날짜)로 나누어 필요한 부분만 스캔하고, Clustering은 같은 값을 물리적으로 가깝게 배치해 I/O를 줄입니다. 둘을 함께 쓰면 수억 행 테이블도 빠르게 조회할 수 있습니다.

## 핵심 용어

- **Partition**: 보통 날짜 컬럼을 기준으로 테이블을 물리적으로 나누는 방식입니다.
- **Clustering**: partition 내부를 자주 조회하는 컬럼 순서로 정리하는 방식입니다.
- **Pruning**: WHERE 조건을 보고 읽을 partition만 고르는 동작입니다.
- **Partition key**: 테이블을 나누는 기준 컬럼입니다.
- **Cluster key**: partition 안에서 정렬 기준이 되는 컬럼입니다.

## Before / After

**Before**: `WHERE order_date = '2026-05-04'` 조건이 있어도 전체 테이블을 스캔합니다.

**After**: 같은 쿼리가 하루치 partition만 읽어 비용과 시간이 크게 줄어듭니다.

## 실습: 적용 5단계

### 1단계 — 파티셔닝 정의하기

```sql
-- BigQuery example
CREATE TABLE fact_orders (
    order_id BIGINT,
    user_key BIGINT,
    amount NUMERIC(12, 2),
    order_date DATE
)
PARTITION BY order_date;
```

### 2단계 — 클러스터링 추가하기

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

### 3단계 — pruning 되는 쿼리

```sql
-- Reads only one daily partition
SELECT SUM(amount)
FROM fact_orders
WHERE order_date = '2026-05-04';
```

### 4단계 — pruning을 깨는 쿼리

```sql
-- Wrapping order_date in a function disables pruning
SELECT SUM(amount)
FROM fact_orders
WHERE EXTRACT(YEAR FROM order_date) = 2026;
```

### 5단계 — 클러스터 키의 이점 보기

```sql
-- Add user_key and read even less
SELECT SUM(amount)
FROM fact_orders
WHERE order_date BETWEEN '2026-05-01' AND '2026-05-31'
  AND user_key = 100;
```

## 이 코드에서 먼저 봐야 할 점

- pruning은 조건이 partition key와 직접 비교될 때 가장 잘 동작합니다.
- partition key에 함수를 씌우면 엔진이 건너뛸 범위를 찾기 어려워집니다.
- clustering은 partition 내부에서 읽을 범위를 더 줄여 주는 보조 장치입니다.

## 자주 하는 실수 5가지

1. **partition key에 함수를 적용합니다.** 곧바로 전체 스캔으로 돌아가기 쉽습니다.
2. **partition을 지나치게 잘게 쪼갭니다.** 메타데이터 관리 비용이 읽기 이득을 잡아먹을 수 있습니다.
3. **cluster key를 너무 많이 선택합니다.** 정렬 비용은 늘고 실제 이득은 크지 않을 수 있습니다.
4. **partition 없이 index만 믿습니다.** Warehouse는 OLTP 데이터베이스와 최적화 방식이 다릅니다.
5. **과거 partition을 자주 수정합니다.** 재처리 범위가 커지면서 운영이 무거워집니다.

## 실무에서는 이렇게 나타납니다

BigQuery, Snowflake, Redshift 모두 partition과 clustering을 핵심 최적화 도구로 제공합니다. 날짜 partition에 사용자나 상품 기준 clustering을 더하는 조합이 실무에서 자주 보이는 기본 형태입니다.

## 실무에서는 이렇게 생각합니다

- partition key가 WHERE 절 첫 문장에 오게 설계합니다.
- pruning이 깨지는 패턴은 팀 문서로 남깁니다.
- 비용은 bytes scanned 기준으로 봅니다.
- cluster key는 적고 자주 쓰는 컬럼만 둡니다.
- 과거 partition은 update보다 append에 가깝게 다룹니다.

## 체크리스트

- [ ] Partition과 Clustering의 차이를 설명할 수 있다.
- [ ] Pruning이 깨지는 대표 패턴을 알고 있다.
- [ ] Warehouse 비용이 주로 무엇으로 계산되는지 이해하고 있다.
- [ ] Partition key를 어떤 기준으로 고르는지 말할 수 있다.

## 연습 문제

1. fact_payments의 partition key와 cluster key를 골라 보세요.
2. pruning을 깨는 쿼리 패턴 세 가지를 적어 보세요.
3. partition을 지나치게 잘게 쪼갰을 때의 단점 두 가지를 적어 보세요.

## 마무리와 다음 글

Partition과 Clustering은 큰 테이블에서 비용과 속도를 함께 다루는 기본 장치입니다. 핵심은 데이터를 전부 읽지 않도록 설계하는 데 있습니다. 다음 글에서는 이렇게 설계한 Warehouse에 데이터를 어떤 흐름으로 넣을지, ETL과 ELT를 살펴보겠습니다.



## 파티셔닝 전략을 표로 정리하기

Partition과 Clustering은 "빠르게 읽는 기술"이 아니라 "불필요한 읽기를 줄이는 기술"입니다. 설계 단계에서 키를 잘못 고르면 쿼리 최적화 여지가 크게 줄어듭니다.

| 전략 | 기준 컬럼 | 기대 효과 | 주의점 | 권장 상황 |
| --- | --- | --- | --- | --- |
| 일 단위 partition | `order_date` | 범위 조회 스캔 급감 | 너무 세밀하면 메타데이터 증가 | 트래픽 큰 이벤트 테이블 |
| 월 단위 partition | `order_month` | 관리 단순 | 일 단위 질의에서 과다 스캔 | 중간 규모 로그/집계 |
| clustering 1개 | `user_key` | point filter 가속 | 고카디널리티 과다 시 재정렬 비용 | 사용자 기준 탐색 빈번 |
| clustering 2개 | `user_key, product_key` | 복합 필터 개선 | 키 과다 시 효율 저하 | 드릴다운 분석 빈번 |

이 표를 보면 partition은 큰 범위 절단, clustering은 절단된 범위 내 추가 정렬이라는 역할 분담이 분명해집니다.

## pruning을 살리는 SQL 패턴

pruning은 SQL 한 줄 차이로 성능이 크게 달라집니다.

```sql
-- Good: partition key 직접 비교
SELECT SUM(amount)
FROM fact_orders
WHERE order_date BETWEEN '2026-05-01' AND '2026-05-31';

-- Bad: 함수 적용으로 pruning 약화 가능
SELECT SUM(amount)
FROM fact_orders
WHERE DATE_TRUNC('month', order_date) = DATE '2026-05-01';
```

첫 쿼리는 파티션 경계를 바로 계산할 수 있어 읽기 범위가 좁습니다. 둘째 쿼리는 엔진에 따라 전체 스캔으로 돌아갈 수 있습니다.

## 운영 시점 점검 지표

키를 잘 골랐는지 검증하려면 운영 지표를 봐야 합니다. 최소한 아래 항목을 주간으로 점검하는 편이 좋습니다.

```yaml
partition_observability:
  - metric: bytes_scanned_per_query
    target: "decreasing trend"
  - metric: partition_pruning_ratio
    target: ">= 0.8 for date-filtered workloads"
  - metric: avg_query_latency
    target: "stable under peak"
  - metric: recluster_jobs_per_day
    target: "controlled"
```

특히 `partition_pruning_ratio`는 모델 설계 품질을 잘 보여 줍니다. 날짜 조건이 있는 쿼리인데 비율이 낮다면 SQL 작성 규칙이나 파티션 키 자체를 재검토해야 합니다.

## SQL 파티션 DDL 예시 확장

아래는 실무에서 자주 쓰는 형태의 DDL입니다.

```sql
CREATE TABLE marts.fact_orders (
    order_id STRING,
    user_key INT64,
    product_key INT64,
    order_date DATE,
    amount NUMERIC,
    quantity INT64,
    created_at TIMESTAMP
)
PARTITION BY order_date
CLUSTER BY user_key, product_key;
```

핵심은 partition key를 질의의 기본 축과 일치시키는 것입니다. 대부분의 도메인에서 시간 축이 가장 안정적이므로 날짜를 기본값으로 삼고, 두 번째 축은 실제 필터 빈도 기준으로 고르는 편이 안전합니다.



## 파티션 DDL 실전 패턴

실제 운영에서는 적재 전략과 파티션 키를 함께 설계해야 합니다. 아래 예시는 일 단위 적재와 월 단위 조회를 동시에 고려한 패턴입니다.

```sql
CREATE TABLE analytics.fact_events (
    event_id STRING,
    user_key INT64,
    event_type STRING,
    event_time TIMESTAMP,
    event_date DATE,
    payload_size INT64
)
PARTITION BY event_date
CLUSTER BY user_key, event_type;
```

이 구조에서는 시간 범위를 우선 절단하고, 사용자/이벤트 유형으로 추가 스캔 감소를 기대할 수 있습니다.

## 운영 점검 표

| 점검 항목 | 목표 | 경고 신호 |
| --- | --- | --- |
| 파티션 수 증가율 | 예측 가능 | 급격한 증가 |
| pruning 비율 | 높음 유지 | 필터 쿼리인데 낮음 |
| recluster 작업량 | 안정적 | 지속 과다 |
| 쿼리 비용 | 완만 | 특정 대시보드 급증 |

점검 표를 주간 회고에 붙이면 최적화가 개인 역량이 아니라 팀 습관으로 정착됩니다.

## 클러스터 키 선정 가이드

클러스터 키는 "자주 쓰는 필터, 낮은 변경 빈도"를 기준으로 고르는 편이 좋습니다. 반대로 무작위성이 큰 컬럼이나 거의 필터링하지 않는 컬럼은 키 후보에서 제외하는 것이 안전합니다.



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

## 처음 질문으로 돌아가기

- **Partition 없이 큰 테이블을 조회하면 어떤 문제가 생길까요?**
  - 필요 없는 데이터까지 전부 스캔해야 하므로 쿼리 시간과 비용이 선형으로 증가합니다.
- **Clustering은 어떤 컬럼을 기준으로 해야 할까요?**
  - 가장 자주 필터링되는 컬럼이나 조인 키를 선택해 I/O를 최소화합니다.
- **Partition 전략을 바꾸려면 데이터를 다시 정렬해야 할까요?**
  - 많은 데이터 웨어하우스가 자동으로 리파티셔닝을 제공하지만 비용과 시간을 고려해 결정해야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Warehouse 101 (1/10): Data Warehouse란 무엇인가?](./01-what-is-data-warehouse.md)
- [Data Warehouse 101 (2/10): OLTP와 OLAP](./02-oltp-and-olap.md)
- [Data Warehouse 101 (3/10): Fact와 Dimension](./03-fact-and-dimension.md)
- [Data Warehouse 101 (4/10): Star Schema](./04-star-schema.md)
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

Tags: DataWarehouse, Partition, Clustering, Performance, Analytics
