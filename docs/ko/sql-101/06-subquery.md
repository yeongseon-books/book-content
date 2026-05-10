---
series: sql-101
episode: 6
title: Subquery
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - SQL
  - Subquery
  - CTE
  - Database
  - Query
seo_description: 스칼라, IN, EXISTS, 인라인 뷰, 그리고 CTE까지 — 복잡한 SQL을 층으로 푸는 법
last_reviewed: '2026-05-04'
---

# Subquery

> SQL 101 시리즈 (6/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 한 줄에 다 적기 어려운 쿼리는 *언제* *어떻게* 나누는 게 좋고, *CTE* 는 왜 *팀의 표준* 이 되었을까요?

> *서브쿼리는 *질문 안의 작은 질문* 이다. 작은 질문이 *명확* 해야 큰 답이 *맞다*.*

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *스칼라 subquery* 와 *IN / EXISTS*
- *인라인 뷰 (FROM 절 서브쿼리)*
- *CTE (WITH)* 의 가독성
- *상관(correlated) subquery* 의 의미와 비용
- 흔한 함정 5가지

## 왜 중요한가

복잡한 분석은 *층(layer)* 을 이루기 마련입니다. 한 줄에 모두 욱여넣은 쿼리는 *읽기 불가능* 하고 *수정 불가능* 합니다. *CTE* 와 *서브쿼리* 는 *단계를 분리* 해 *팀이 같이 읽을 수 있는* SQL 을 만듭니다.

> *읽히는 쿼리는 *고치기 쉬운 쿼리* 다.*

## 개념 한눈에 보기

```mermaid
flowchart TB
    Inner["내부 쿼리"] --> Outer["외부 쿼리"]
    Outer --> Result["결과"]
    CTE["WITH ... AS"] --> Outer
```

## 핵심 용어 정리

- **Scalar subquery**: *한 값만* 돌려주는 서브쿼리.
- **Inline view**: `FROM (SELECT ...) AS t`.
- **CTE**: `WITH name AS (...)` — *이름 있는* 서브쿼리.
- **Correlated subquery**: 외부 행을 *참조* 하는 서브쿼리.
- **EXISTS**: *존재* 여부만 본다.

## Before/After

**Before**: 200줄짜리 *한 덩어리* SQL — 어디부터 읽을지 모른다.

**After**: 4개의 *CTE* 로 *단계를 명명* — 누구나 *읽고 수정* 가능.

## 실습: Subquery 5단계

### 1단계 — 스칼라

```sql
SELECT name,
    (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) AS order_count
FROM users u;
```

### 2단계 — IN

```sql
SELECT * FROM users
WHERE id IN (SELECT user_id FROM orders WHERE total > 1000);
```

### 3단계 — EXISTS

```sql
SELECT * FROM users u
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id
);
```

### 4단계 — 인라인 뷰

```sql
SELECT t.country, t.users
FROM (
    SELECT country, COUNT(*) AS users
    FROM users GROUP BY country
) AS t
WHERE t.users > 100;
```

### 5단계 — CTE

```sql
WITH big_orders AS (
    SELECT user_id, SUM(total) AS spend
    FROM orders GROUP BY user_id
    HAVING SUM(total) > 1000
)
SELECT u.name, b.spend
FROM big_orders b
JOIN users u ON u.id = b.user_id;
```

## 이 코드에서 주목할 점

- *EXISTS* 는 `IN` 보다 *NULL 안전* 하고 *조기 종료* 가 가능.
- *인라인 뷰* 와 *CTE* 는 의미가 같지만 *CTE* 가 *읽기 좋다*.
- *상관 subquery* 는 *행마다 실행* 될 수 있어 *비싸다*.

## 자주 하는 실수 5가지

1. **`NOT IN (subquery)`** 인데 서브쿼리에 *NULL* 이 섞임. 결과가 *비어버린다*.
2. **상관 서브쿼리로 *N+1*.** *조인 + 집계* 로 바꾸자.
3. **CTE 가 *너무 깊음*.** 5단계 넘으면 *분리* 한다.
4. **인라인 뷰에 *별칭 누락*.** 일부 DB 는 *오류*.
5. **EXISTS 안에 `SELECT *`.** 의도가 *오해* 됨. `SELECT 1` 로.

## 실무에서는 이렇게 쓰입니다

ETL 의 *대부분의 단계* 는 CTE 로 *명명된 변환* 입니다. *cohort 분석*, *funnel*, *retention* 모두 *CTE 3~5개* 로 깔끔히 풀립니다.

## 시니어 엔지니어는 이렇게 생각합니다

- *복잡함은 *층을 만들어* 푼다.*
- *NOT IN 보다 *NOT EXISTS*.*
- *CTE 이름은 *결과의 의미* 로.*
- *상관 서브쿼리는 *조인이 가능한지* 본다.*
- *EXISTS 는 *효율적인 존재 검사*.*

## 체크리스트

- [ ] 스칼라/인라인/CTE 의 차이를 안다.
- [ ] EXISTS 와 IN 의 차이를 안다.
- [ ] 상관 서브쿼리의 비용을 안다.
- [ ] CTE 로 단계를 나눌 수 있다.

## 연습 문제

1. *주문이 있는 사용자* 만 EXISTS 로 추출.
2. *국가별 사용자 수* 를 *인라인 뷰* 와 *CTE* 두 가지로 작성.
3. *총 결제 1000 이상* 사용자의 *최근 주문일* 을 *CTE 두 단계* 로 구해 보세요.

## 정리 및 다음 단계

서브쿼리는 *질문을 쪼개는* 도구입니다. 다음 글은 *Window Function* 입니다.

<!-- toc:begin -->
- [SQL이란 무엇인가?](./01-what-is-sql.md)
- [SELECT 기본](./02-select-basics.md)
- [WHERE와 조건](./03-where-and-conditions.md)
- [JOIN](./04-join.md)
- [GROUP BY와 aggregate](./05-group-by-and-aggregate.md)
- **Subquery (현재 글)**
- Window Function (예정)
- INSERT, UPDATE, DELETE (예정)
- Index와 Query Plan (예정)
- 실전 분석 SQL (예정)
<!-- toc:end -->

## 참고 자료

- [PostgreSQL — Subqueries](https://www.postgresql.org/docs/current/functions-subquery.html)
- [PostgreSQL — WITH Queries (CTE)](https://www.postgresql.org/docs/current/queries-with.html)
- [Mode — Subqueries](https://mode.com/sql-tutorial/sql-sub-queries/)
- [Use The Index, Luke — IN vs EXISTS](https://use-the-index-luke.com/sql/where-clause/null/not-in)
