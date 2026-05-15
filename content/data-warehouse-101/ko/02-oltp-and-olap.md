---
series: data-warehouse-101
episode: 2
title: OLTP와 OLAP
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
  - OLTP
  - OLAP
  - Database
  - Analytics
seo_description: OLTP와 OLAP의 워크로드 차이, 행 저장과 열 저장의 트레이드오프 및 두 시스템을 분리해야 하는 이유를 정리합니다.
last_reviewed: '2026-05-12'
---

# OLTP와 OLAP

OLTP는 지금 이 순간의 한 건을 빠르게 처리하고, OLAP는 과거 전체를 한 번에 훑습니다. 최적화 방향이 정반대라서 같은 엔진으로 두 요구를 모두 잘 만족시키기 어렵습니다.

이 글은 Data Warehouse 101 시리즈의 2번째 글입니다.

## 이 글에서 다룰 문제

- OLTP와 OLAP는 어떤 워크로드를 다르게 처리할까요?
- 행 저장과 열 저장은 어느 쿼리에서 차이가 커질까요?
- 하나의 엔진으로 두 요구를 함께 처리하면 왜 곤란할까요?
- CDC나 복제 지연은 분리 설계에서 어떻게 받아들여야 할까요?
- 현업에서 OLTP와 OLAP를 나누는 기준은 무엇일까요?

## 이 글에서 배울 것

- OLTP와 OLAP의 워크로드 차이
- 행 저장과 열 저장의 트레이드오프
- 두 시스템을 분리해야 하는 이유
- 비교 실습 5단계
- 입문 단계에서 자주 나오는 실수 5가지

## 왜 중요한가

OLTP는 지금 한 건을 빠르게 처리해야 하고, OLAP는 과거 전체를 한 번에 훑어야 합니다. 최적화 방향이 반대라서 하나의 엔진이 두 요구를 모두 잘 만족시키기는 어렵습니다. 그래서 워크로드의 모양을 먼저 보고 시스템을 나누는 판단이 중요합니다.

> 맞는 도구를 고르는 편이 낫습니다. 하나로 둘 다 하려 하면 둘 다 불편해집니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    User["User"] --> OLTP["OLTP DB (row store)"]
    OLTP --> CDC["CDC / ETL"]
    CDC --> OLAP["OLAP DB (column store)"]
    Analyst["Analyst"] --> OLAP
```

## 핵심 용어

- **OLTP**: 짧고 동시성이 높은 읽기/쓰기 트랜잭션입니다.
- **OLAP**: 넓은 범위를 읽는 대용량 집계 중심 쿼리입니다.
- **행 저장**: 한 행의 모든 컬럼을 함께 저장하는 방식입니다.
- **열 저장**: 같은 컬럼의 값을 연속해서 저장하는 방식입니다.
- **CDC**: Change Data Capture. OLTP의 변경을 OLAP 쪽으로 흘려 보내는 방식입니다.

## Before / After

**Before**: 하나의 Postgres에서 결제 처리와 월간 분석이 충돌해 지연이 발생합니다.

**After**: OLTP는 Postgres, OLAP는 BigQuery를 맡아 각자의 일에 맞게 최적화됩니다.

## 실습: 비교 5단계

### 1단계 — OLTP 패턴

```sql
-- Update one user's balance
UPDATE accounts SET balance = balance - 1000 WHERE id = 42;
```

### 2단계 — OLAP 패턴

```sql
-- Average balance across all users
SELECT AVG(balance) FROM accounts;
```

### 3단계 — 행 저장의 비용

```sql
-- Row store reads all columns even if you ask for one
SELECT amount FROM fact_orders;
```

### 4단계 — 열 저장의 이점

```sql
-- Column store scans only the amount column
SELECT SUM(amount) FROM fact_orders;
```

### 5단계 — 분리된 흐름

```sql
-- OLTP receives single-row INSERT
INSERT INTO orders VALUES (...);
-- OLAP analyzes accumulated facts
SELECT date_trunc('day', created_at), COUNT(*) FROM fact_orders GROUP BY 1;
```

## 이 코드에서 먼저 봐야 할 점

- 짧은 쿼리는 행 저장에서 더 빠르게 처리됩니다.
- 큰 집계는 열 저장에서 더 유리합니다.
- 두 시스템이 감당하는 동시성의 성격도 완전히 다릅니다.

## 자주 하는 실수 5가지

1. **OLAP 쿼리를 OLTP에서 실행합니다.** 잠금 대기가 늘고 지연이 누적됩니다.
2. **OLAP에 짧은 트랜잭션을 그대로 보냅니다.** 비용만 늘고 효과는 거의 없습니다.
3. **두 시스템 사이의 동기화 지연이 0이라고 가정합니다.** 실제 운영에서는 몇 분의 lag를 감안해야 합니다.
4. **인덱스 전략을 그대로 복사합니다.** 접근 패턴이 다르므로 따로 설계해야 합니다.
5. **백업 정책을 공유합니다.** OLTP에는 PITR이, OLAP에는 snapshot이 더 적절한 경우가 많습니다.

## 실무에서는 이렇게 나타납니다

서비스 결제는 Postgres나 MySQL 같은 OLTP에 두고, 매출 리포트는 Snowflake나 BigQuery 같은 OLAP에 둡니다. 두 시스템 사이는 Debezium 같은 CDC로 연결하고, 약간의 지연이 생기는 전제를 받아들입니다.

## 실무에서는 이렇게 생각합니다

- 먼저 워크로드의 모양부터 봅니다.
- 하나의 엔진으로 두 역할을 모두 맡기는 결정은 의심부터 합니다.
- 비용은 결국 접근 패턴이 만든다고 봅니다.
- 복제 지연은 버그가 아니라 상수처럼 다룹니다.
- 분리 이후의 일관성 모델을 처음부터 설계합니다.

## 체크리스트

- [ ] OLTP와 OLAP의 차이를 세 줄로 설명할 수 있습니다.
- [ ] 행 저장과 열 저장의 차이를 이해했습니다.
- [ ] CDC가 무엇인지 설명할 수 있습니다.
- [ ] 두 시스템의 백업 방식 차이를 알고 있습니다.

## 연습 문제

1. OLTP 워크로드 예시 세 가지를 적어 보세요.
2. OLAP 워크로드 예시 세 가지를 적어 보세요.
3. 어떤 쿼리가 행 저장에 더 잘 맞는지 설명해 보세요.

## 마무리와 다음 글

OLTP와 OLAP는 최적화 방향이 다릅니다. 다음 글에서는 OLAP의 핵심 개념인 Fact와 Dimension을 살펴봅니다.

<!-- toc:begin -->
- [Data Warehouse란 무엇인가?](./01-what-is-data-warehouse.md)
- **OLTP와 OLAP (현재 글)**
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

- [Wikipedia — OLTP](https://en.wikipedia.org/wiki/Online_transaction_processing)
- [Wikipedia — OLAP](https://en.wikipedia.org/wiki/Online_analytical_processing)
- [Snowflake — Columnar Storage](https://docs.snowflake.com/en/user-guide/intro-key-concepts)
- [Designing Data-Intensive Applications](https://dataintensive.net/)

Tags: DataWarehouse, OLTP, OLAP, Database, Analytics
