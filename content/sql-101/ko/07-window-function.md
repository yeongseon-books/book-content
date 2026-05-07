---
series: sql-101
episode: 7
title: Window Function
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
  - WindowFunction
  - Analytics
  - Database
  - Query
seo_description: ROW_NUMBER, RANK, LAG/LEAD, 누적 합계 — 행을 줄이지 않고 그룹별 계산을 더하는 SQL 도구
last_reviewed: '2026-05-04'
---

# Window Function

> SQL 101 시리즈 (7/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: GROUP BY 는 *행을 줄여서* 답을 만드는데, *행을 그대로 두면서* 그룹별 계산을 *더하는* 방법은 없을까요?

> *Window function 은 *집계의 결과를 *옆에 붙여 주는* 도구다.*

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *OVER (PARTITION BY ...)* 의 의미
- *ROW_NUMBER, RANK, DENSE_RANK*
- *LAG / LEAD* 와 *시간 비교*
- *누적 합계 (running total)*
- 흔한 함정 5가지

## 왜 중요한가

순위, 차이, 누적 — *행 단위 분석* 에 필수입니다. GROUP BY 만 쓰면 *세부를 잃습니다*. Window 는 *세부 + 집계* 를 *동시에* 보여줍니다. *cohort, funnel, retention* 의 핵심 도구입니다.

> *Window 는 SQL 을 *분석 언어로* 만든 결정적 도구다.*

## 개념 한눈에 보기

```mermaid
flowchart LR
    Rows["원본 행"] --> Win["OVER(PARTITION BY ... ORDER BY ...)"]
    Win --> Func["ROW_NUMBER / SUM / LAG"]
    Func --> Out["행 + 계산 결과"]
```

## 핵심 용어 정리

- **Partition**: 같은 *그룹으로 묶일* 행들.
- **Frame**: window 안에서 *어디까지 볼지*.
- **Ranking function**: `ROW_NUMBER, RANK, DENSE_RANK`.
- **Offset function**: `LAG, LEAD` — 이전/다음 행.
- **Running total**: 누적 합.

## Before/After

**Before**: *국가별 매출 합* 을 GROUP BY 로 구한 뒤 *원본과 다시 조인*.

**After**: `SUM(total) OVER (PARTITION BY country)` 한 줄로 *행 그대로* 합계가 옆에 붙는다.

## 실습: 5가지 패턴

### 1단계 — 행 번호

```sql
SELECT id, country,
    ROW_NUMBER() OVER (PARTITION BY country ORDER BY signup_at) AS seq
FROM users;
```

### 2단계 — 순위

```sql
SELECT product_id, total,
    RANK() OVER (PARTITION BY product_id ORDER BY total DESC) AS rk
FROM orders;
```

### 3단계 — 이전 값

```sql
SELECT user_id, signup_at,
    LAG(signup_at) OVER (PARTITION BY user_id ORDER BY signup_at) AS prev_signup
FROM users;
```

### 4단계 — 누적 합계

```sql
SELECT day, revenue,
    SUM(revenue) OVER (ORDER BY day) AS running_total
FROM daily_revenue;
```

### 5단계 — 이동 평균 (7일)

```sql
SELECT day, revenue,
    AVG(revenue) OVER (
        ORDER BY day
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS ma_7
FROM daily_revenue;
```

## 이 코드에서 주목할 점

- `OVER ()` 가 *비어 있으면* 전체가 한 partition.
- ORDER BY 가 있어야 *순서 의존* 함수가 의미를 가진다.
- frame 을 *명시* 하지 않으면 DB 별 *기본값* 이 다르다.

## 자주 하는 실수 5가지

1. **`RANK` 와 `ROW_NUMBER` 혼동.** 동률 처리 다름.
2. **PARTITION 빠뜨림.** *전체* 가 한 그룹이 됨.
3. **frame 미명시.** 기본 *RANGE UNBOUNDED PRECEDING* 가 *의도와 다름*.
4. **`LAG` 의 *NULL* 무시.** 첫 행에 NULL 처리 필요.
5. **window 와 GROUP BY 같이 쓰며 *충돌*.** 적용 시점 오해.

## 실무에서는 이렇게 쓰입니다

*매출 7일 이동 평균*, *사용자별 N번째 주문*, *전월 대비 증가율* — 모두 window 한 줄입니다. *time series* 분석의 *핵심 도구* 입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- *Window 는 *세부를 잃지 않는* 집계.*
- *frame 은 *항상 명시*.*
- *RANK 는 *동률 정책* 에 따라 골라 쓴다.*
- *LAG/LEAD 는 *시계열 비교* 의 기본.*
- *복잡한 window 는 *CTE* 로 한 단계 빼낸다.*

## 체크리스트

- [ ] PARTITION BY 의 의미를 안다.
- [ ] ROW_NUMBER 와 RANK 의 차이를 안다.
- [ ] LAG/LEAD 를 쓸 수 있다.
- [ ] frame 의 기본값 위험을 안다.

## 연습 문제

1. *사용자별 첫 주문* 만 골라 보세요 (`ROW_NUMBER = 1`).
2. *상품별 매출 상위 3* 위를 RANK 로 추출.
3. *일별 매출* 의 *7일 이동 평균* 을 구해 보세요.

## 정리 및 다음 단계

Window 는 *행을 살리는 집계* 입니다. 다음 글은 *INSERT/UPDATE/DELETE* 입니다.

<!-- toc:begin -->
- [SQL이란 무엇인가?](./01-what-is-sql.md)
- [SELECT 기본](./02-select-basics.md)
- [WHERE와 조건](./03-where-and-conditions.md)
- [JOIN](./04-join.md)
- [GROUP BY와 aggregate](./05-group-by-and-aggregate.md)
- [Subquery](./06-subquery.md)
- **Window Function (현재 글)**
- INSERT, UPDATE, DELETE (예정)
- Index와 Query Plan (예정)
- 실전 분석 SQL (예정)
<!-- toc:end -->

## 참고 자료

- [PostgreSQL — Window Functions](https://www.postgresql.org/docs/current/tutorial-window.html)
- [PostgreSQL — Window Function Reference](https://www.postgresql.org/docs/current/functions-window.html)
- [Mode — Window Functions](https://mode.com/sql-tutorial/sql-window-functions/)
- [Use The Index, Luke — Top-N](https://use-the-index-luke.com/sql/partial-results/top-n-queries)

Tags: SQL, WindowFunction, Analytics, Database, Query
