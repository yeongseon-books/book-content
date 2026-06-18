---
series: database-systems-101
episode: 3
title: "바이브코딩을 위한 데이터베이스 시스템 기초 (3/10): SQL과 쿼리 처리"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Computer Science
  - Database
  - SQL
  - Optimizer
  - 실행계획
  - 쿼리
seo_description: AI가 만든 SQL이 왜 느린지 이해하려면 쿼리가 파싱에서 실행까지 거치는 과정을 알아야 합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 데이터베이스 시스템 기초 (3/10): SQL과 쿼리 처리

이 글은 **바이브코딩을 위한 데이터베이스 시스템 기초** 시리즈의 3번째 글입니다. AI 코딩 도구로 빠르게 서비스를 만들 때 데이터베이스가 왜 그렇게 동작하는지 이해하면, AI가 만든 쿼리의 문제를 직접 발견하고 수정할 수 있습니다.

---

AI가 작성한 SQL이 개발 환경에서는 빠르다가 운영 환경에서 갑자기 느려지는 경험을 하셨나요? 데이터가 많아지면 당연히 느려진다고 생각하기 쉽지만, 실제 원인은 대부분 다른 곳에 있습니다. SQL은 "무엇을 원하는지"만 적는 언어이고, "어떻게 찾을지"는 DBMS가 결정합니다. 그 결정의 근거가 바로 실행 계획입니다.

`SELECT * FROM orders WHERE user_id = 7` 같은 SQL 한 줄은 너무 단순해 보여서 많은 사람이 "데이터베이스가 알아서 찾아 오겠지" 정도로 생각합니다. 맞는 말이지만, 바로 그 "알아서"가 어디까지를 뜻하는지 모르면 성능 문제를 만났을 때 손댈 수 있는 지점이 거의 없어집니다.

SQL은 절차를 적는 언어가 아닙니다. 원하는 결과를 선언하면 DBMS가 그것을 파싱하고, 의미를 해석하고, 가능한 실행 계획들 중 하나를 고른 뒤, 실제로 행을 만들어 냅니다.

> 같은 결과를 만드는 SQL은 여러 개일 수 있고, 같은 SQL을 실행하는 방법도 여러 개일 수 있습니다. 옵티마이저는 그 가능성들 사이에서 하나를 고르는 엔진입니다.

## 이 글에서 다룰 질문

- SQL이 선언형 언어라는 사실은 어떤 결과를 낳을까요?
- 쿼리는 어떤 네 단계를 거쳐 실행될까요?
- 가장 단순한 EXPLAIN 출력은 어떻게 읽어야 할까요?
- AI가 생성한 SQL에서 성능 문제를 어떻게 진단할까요?
- N+1 문제는 왜 생기고 어떻게 잡을까요?

---

## 쿼리 처리의 네 단계

SQL은 텍스트에서 시작해 실행 계획 트리로 바뀌고, 실행기는 그 트리를 따라가며 결과 행을 생산합니다.

```
SQL text → Parser → Planner/Optimizer → Plan tree → Executor → Rows
```

**핵심 용어**

- **DDL/DML**: DDL은 스키마를 정의하고(CREATE, ALTER), DML은 데이터를 읽고 바꿉니다(SELECT, INSERT, UPDATE, DELETE).
- **실행 계획(Plan)**: 옵티마이저가 선택한 쿼리 실행 단계의 트리입니다.
- **비용(Cost)**: 여러 계획을 비교하기 위해 옵티마이저가 사용하는 추정치입니다.
- **Seq Scan vs Index Scan**: 테이블 전체를 읽을지, 인덱스를 따라 필요한 부분만 읽을지의 차이입니다.
- **Estimate vs Actual**: 옵티마이저가 예상한 행 수와 실제 행 수입니다. 차이가 크면 통계가 낡았을 가능성이 큽니다.

## 바이브코딩 관점: AI가 만드는 SQL의 성능 문제 패턴

AI는 기능적으로 올바른 SQL을 잘 만듭니다. 하지만 성능을 의식한 쿼리 작성은 훨씬 약합니다. 가장 자주 보이는 패턴입니다.

| AI 생성 패턴 | 문제 | EXPLAIN으로 보이는 신호 |
|---|---|---|
| `SELECT *` 남발 | 불필요한 컬럼 전송, 커버링 인덱스 불가 | 넓은 width, 큰 row count |
| 루프 안 SQL 반복 | N+1 문제, 요청당 수백 번 쿼리 | 짧은 쿼리가 수없이 반복 |
| 인덱스 없는 컬럼 필터 | 풀스캔 | Seq Scan + 큰 rows |
| WHERE에 함수 적용 | 인덱스 무력화 | Seq Scan on indexed column |
| 불필요한 서브쿼리 중첩 | 계획 복잡도 증가 | 여러 단계 Hash/Sort |

## Before / After: 느린 쿼리 vs 실행 계획 읽고 개선하기

**Before — 증거 없이 쿼리가 느리다고 단정하는 상황**

```sql
SELECT * FROM orders WHERE user_id = 7;
-- slow. Add another index. Still slow. Blame the cache...
```

**After — 실행 계획을 읽고 판단하기**

```sql
EXPLAIN QUERY PLAN
SELECT * FROM orders WHERE user_id = 7;
-- SCAN orders         ← full scan (인덱스 없음)
-- 인덱스 생성 후:
-- SEARCH orders USING INDEX idx_orders_user_id (user_id=?)
```

처음에는 전체 스캔이 보이고, 인덱스를 만든 뒤에는 인덱스를 사용했다는 증거가 보입니다. 한 줄의 계획 출력이 가설을 살리거나 죽입니다.

## 실행 계획에서 빨간 신호 찾기

EXPLAIN 출력에서 다음 패턴이 보이면 즉시 개선이 필요합니다.

```
-- 문제 있음: 예상 행 수와 실제 행 수 차이가 크다
Seq Scan on orders (rows=50000) → actual rows=50

-- 문제 있음: 인덱스가 있는데 Seq Scan
Seq Scan on users WHERE email = 'a@x.com'  ← lower() 함수 때문에 인덱스 무력화

-- 문제 있음: 큰 테이블에 Nested Loop
Nested Loop on large_table (수백만 rows)
```

```
-- 좋음: 인덱스 스캔 + 예상과 실제 근접
Index Scan using idx_user_id on orders (rows=52) actual rows=50
```

## 자주 하는 실수 5가지

| 번호 | 실수 | 왜 문제인가 |
|---|---|---|
| 1 | EXPLAIN도 보지 않고 쿼리를 느리다고 단정 | 증거 없는 튜닝은 운에 기대는 디버깅입니다 |
| 2 | 인덱스를 만들고 안심 | 옵티마이저가 선택하지 않으면 그 인덱스는 없는 것과 같습니다 |
| 3 | `SELECT *`를 습관처럼 씀 | 네트워크, 메모리, 캐시 비용이 조용히 쌓입니다 |
| 4 | 루프 안에서 SQL을 반복 호출 | N+1 문제는 코드 리뷰에서 막아야 합니다 |
| 5 | DDL과 DML을 한 트랜잭션에 섞음 | 엔진마다 동작 차이가 생겨 운영 위험이 커집니다 |

## AI 팁: AI가 만든 SQL 성능 검사 루틴

AI가 생성한 SQL을 코드베이스에 합치기 전, 다음 루틴으로 빠르게 검사할 수 있습니다.

**1단계: EXPLAIN으로 계획 확인**

```sql
-- SQLite
EXPLAIN QUERY PLAN SELECT ...

-- PostgreSQL
EXPLAIN (ANALYZE, BUFFERS) SELECT ...
```

**2단계: 위험 신호 체크**
- `Seq Scan`이 나오는가? → 인덱스 필요 여부 검토
- 예상 rows와 실제 rows 차이가 10배 이상인가? → ANALYZE 실행
- WHERE 절에 함수가 있는가? → 함수형 인덱스 검토

**3단계: N+1 확인**
- 루프 안에 `SELECT` 호출이 있는가?
- ORM의 lazy loading이 N번 쿼리를 만드는가?

## 체크리스트

- [ ] 느린 쿼리에 대해 실제로 EXPLAIN을 확인했는가?
- [ ] `SELECT *` 대신 필요한 컬럼을 명시하고 있는가?
- [ ] 루프 안에 SQL 호출이 숨어 있지 않은가?
- [ ] AI가 생성한 SQL에 EXPLAIN을 실행해 계획을 확인했는가?
- [ ] N+1 패턴이 있는지 코드를 검토했는가?

## 처음 질문으로 돌아가기

- **SQL이 선언형 언어라는 사실은 어떤 결과를 낳을까요?**
  SQL은 무엇을 원하는지만 적고 어떻게 찾을지는 옵티마이저가 결정합니다. 그래서 같은 SQL도 데이터와 통계에 따라 전혀 다른 계획으로 실행될 수 있습니다.

- **쿼리는 어떤 네 단계를 거쳐 실행될까요?**
  파싱(문법 검사), 최적화(실행 계획 선택), 계획 트리 생성, 실행기(실제 행 생성)의 네 단계를 거칩니다.

- **AI가 생성한 SQL에서 성능 문제를 어떻게 진단할까요?**
  EXPLAIN 출력에서 Seq Scan 여부, 예상/실제 행 수 차이, WHERE 절의 함수 사용을 확인합니다.

## 정리

여러분은 SQL로 무엇을 쓰고, DBMS는 어떻게 실행할지를 정합니다. AI가 만든 SQL이 느리다고 느껴질 때 가장 먼저 할 일은 EXPLAIN을 실행해 옵티마이저가 어떤 판단을 내렸는지 읽는 것입니다. 다음 글에서는 옵티마이저가 가장 강력하게 활용하는 도구인 인덱스를 다룹니다.

## 참고 자료

- [database-systems-101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/database-systems-101/ko)
- [SQLite — EXPLAIN QUERY PLAN](https://www.sqlite.org/eqp.html)
- [PostgreSQL — Using EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)
- [Use The Index, Luke!](https://use-the-index-luke.com/)
- [Database System Concepts (Silberschatz)](https://www.db-book.com/)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 데이터베이스 시스템 기초 (1/10): 데이터베이스 시스템이란 무엇인가?
- 바이브코딩을 위한 데이터베이스 시스템 기초 (2/10): 관계형 모델
- **바이브코딩을 위한 데이터베이스 시스템 기초 (3/10): SQL과 쿼리 처리 (현재 글)**
- 바이브코딩을 위한 데이터베이스 시스템 기초 (4/10): 인덱스
- 바이브코딩을 위한 데이터베이스 시스템 기초 (5/10): 트랜잭션과 ACID
- 바이브코딩을 위한 데이터베이스 시스템 기초 (6/10): 격리 수준
- 바이브코딩을 위한 데이터베이스 시스템 기초 (7/10): 정규화와 모델링
- 바이브코딩을 위한 데이터베이스 시스템 기초 (8/10): 쿼리 최적화
- 바이브코딩을 위한 데이터베이스 시스템 기초 (9/10): 복제와 백업
- 바이브코딩을 위한 데이터베이스 시스템 기초 (10/10): OLTP와 OLAP

<!-- toc:end -->

Tags: 바이브코딩, Computer Science, Database, SQL, Optimizer, 실행계획, 쿼리
