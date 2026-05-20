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

이 그림에서는 Partition과 Clustering를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> Partition과 Clustering의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

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

## 처음 질문으로 돌아가기

- **Partition과 Clustering은 각각 어떤 문제를 해결할까요?**
  - 본문의 기준은 Partition과 Clustering를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Pruning은 실제로 어떻게 비용을 줄일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Partition key와 cluster key는 어떤 기준으로 고를까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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
