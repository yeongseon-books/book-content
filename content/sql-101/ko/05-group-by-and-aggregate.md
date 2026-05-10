---
series: sql-101
episode: 5
title: GROUP BY와 aggregate
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
  - GroupBy
  - Aggregate
  - Database
  - Analytics
seo_description: GROUP BY의 동작 원리, 집계 함수, HAVING과 WHERE의 차이, 그리고 한 번에 여러 그룹을 보는 방법
last_reviewed: '2026-05-04'
---

# GROUP BY와 aggregate

> SQL 101 시리즈 (5/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 한 줄짜리 합계는 쉬운데, *카테고리별 합계* 가 어려운 이유는 무엇이고, *HAVING* 은 *WHERE* 와 어떻게 다를까요?

> *집계는 *행을 줄여서 의미를 만드는* 일이다.*

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *GROUP BY* 의 평가 시점과 *집계 함수*
- *HAVING* 과 *WHERE* 의 차이
- 여러 컬럼으로 그룹화하기
- *NULL* 그룹의 처리
- 흔한 함정 5가지

## 왜 중요한가

대시보드 숫자의 *대부분* 은 GROUP BY 결과입니다. *일별 매출, 사용자별 주문 수, 국가별 평균* — 모두 같은 모양입니다. 여기서 *NULL* 과 *조인 카디널리티* 를 못 보면 *숫자가 거짓말* 을 합니다.

> *집계는 *행을 한 줄로 압축* 한다. 무엇을 *버리는지* 안다는 뜻이다.*

## 개념 한눈에 보기

```mermaid
flowchart LR
    Rows["행"] --> Where["WHERE"]
    Where --> Group["GROUP BY 키"]
    Group --> Agg["SUM/COUNT/AVG"]
    Agg --> Having["HAVING"]
    Having --> Out["결과"]
```

## 핵심 용어 정리

- **Aggregate function**: `SUM, COUNT, AVG, MIN, MAX` 등.
- **Grouping key**: 같은 그룹으로 묶이는 *기준 컬럼*.
- **HAVING**: *집계 결과* 에 거는 조건.
- **NULL group**: NULL 도 *하나의 그룹*.
- **Distinct count**: `COUNT(DISTINCT x)` — 중복 제거 후 세기.

## Before/After

**Before**: `SELECT user_id, SUM(total) FROM orders;` — *오류*. user_id 는 *그룹화* 되어야 함.

**After**: `SELECT user_id, SUM(total) FROM orders GROUP BY user_id;` — *올바른 집계*.

## 실습: 집계 5단계

### 1단계 — 단순 집계

```sql
SELECT COUNT(*) AS total_users FROM users;
```

### 2단계 — 카테고리별

```sql
SELECT country, COUNT(*) AS users
FROM users
GROUP BY country;
```

### 3단계 — 여러 키

```sql
SELECT country, signup_at::date AS day, COUNT(*) AS users
FROM users
GROUP BY country, day;
```

### 4단계 — HAVING

```sql
SELECT country, COUNT(*) AS users
FROM users
GROUP BY country
HAVING COUNT(*) > 100;
```

### 5단계 — DISTINCT 카운트

```sql
SELECT country, COUNT(DISTINCT user_id) AS active_users
FROM events
GROUP BY country;
```

## 이 코드에서 주목할 점

- WHERE 는 *집계 전*, HAVING 은 *집계 후*.
- `COUNT(*)` 는 *NULL 포함*, `COUNT(col)` 은 *NULL 제외*.
- `COUNT(DISTINCT)` 는 *비싸다*. 큰 테이블에서는 *근사 함수* 를 고려한다.

## 자주 하는 실수 5가지

1. **GROUP BY *컬럼 빠뜨림*.** SELECT 의 *비집계 컬럼* 은 *전부* 그룹에 들어가야 한다.
2. **WHERE 자리에 *집계 조건*.** `WHERE COUNT(*) > 1` 은 *오류*. HAVING 으로.
3. **`AVG(NULL)`** 을 0 처럼 가정. NULL 은 *제외* 된다.
4. **조인 후 합계가 *부풀어* 오름.** *카디널리티* 가 1:N.
5. **그룹화에 *너무 많은 컬럼*.** 그룹이 *모두 1행* 이라 의미가 *없음*.

## 실무에서는 이렇게 쓰입니다

*일별 활성 사용자(DAU)*, *국가별 결제 합계*, *상품별 평균 평점* — 분석 리포트의 *기본 단위* 입니다. 큰 그룹은 *materialized view* 로 *미리 집계* 합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- *집계 *전 / 후* 조건을 분리해 사고한다.*
- *NULL 이 *수치를 왜곡* 할 수 있다고 가정.*
- *DISTINCT COUNT 는 *비용을 본다*.*
- *조인 + 집계는 *작은 테이블 먼저 집계*.*
- *그룹 키는 *해석 가능* 해야 한다.*

## 체크리스트

- [ ] WHERE 와 HAVING 의 차이를 안다.
- [ ] `COUNT(*)` 와 `COUNT(col)` 의 차이를 안다.
- [ ] 다중 키 그룹화를 쓸 수 있다.
- [ ] NULL 그룹의 의미를 안다.

## 연습 문제

1. *국가별 사용자 수* 와 *국가별 활성 사용자 수* 를 함께 구해 보세요.
2. *주문 100건 이상인 사용자* 만 골라 보세요.
3. 일별 *DAU* 를 *이벤트 테이블* 로 계산해 보세요.

## 정리 및 다음 단계

GROUP BY 는 *행을 줄여 의미를 만드는* 도구입니다. 다음 글은 *Subquery*.

<!-- toc:begin -->
- [SQL이란 무엇인가?](./01-what-is-sql.md)
- [SELECT 기본](./02-select-basics.md)
- [WHERE와 조건](./03-where-and-conditions.md)
- [JOIN](./04-join.md)
- **GROUP BY와 aggregate (현재 글)**
- Subquery (예정)
- Window Function (예정)
- INSERT, UPDATE, DELETE (예정)
- Index와 Query Plan (예정)
- 실전 분석 SQL (예정)
<!-- toc:end -->

## 참고 자료

- [PostgreSQL — GROUP BY](https://www.postgresql.org/docs/current/tutorial-agg.html)
- [PostgreSQL — Aggregate Functions](https://www.postgresql.org/docs/current/functions-aggregate.html)
- [Mode — GROUP BY](https://mode.com/sql-tutorial/sql-group-by/)
- [SQLBolt — Aggregates](https://sqlbolt.com/lesson/select_queries_with_aggregates)

Tags: SQL, GroupBy, Aggregate, Database, Analytics
