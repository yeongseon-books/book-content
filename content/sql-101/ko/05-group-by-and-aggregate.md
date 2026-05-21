---
series: sql-101
episode: 5
title: "SQL 101 (5/10): GROUP BY와 집계 함수"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - SQL
  - GroupBy
  - Aggregate
  - Database
  - Analytics
seo_description: GROUP BY, 집계 함수, HAVING, NULL 그룹, 다중 그룹화의 실무 감각을 설명합니다
last_reviewed: '2026-05-15'
---

# SQL 101 (5/10): GROUP BY와 집계 함수

분석 SQL에서 숫자를 만드는 순간부터 `GROUP BY`와 집계 함수가 등장합니다. 사용자 수, 국가별 매출, 일별 주문 수처럼 대시보드에 보이는 거의 모든 숫자는 여러 행을 묶고 압축한 결과입니다. 그래서 이 주제는 단순한 문법보다, 어떤 행을 하나의 그룹으로 볼지 결정하는 사고방식이 더 중요합니다.

이 글은 SQL 101 시리즈의 다섯 번째 글입니다. 여기서는 `GROUP BY`와 집계 함수를 통해 행을 줄여 의미를 만드는 방식을 설명합니다.

## 먼저 던지는 질문

- `GROUP BY`는 언제 실행되고 무엇을 기준으로 묶을까요?
- `SUM`, `COUNT`, `AVG` 같은 집계 함수는 어떤 차이를 가질까요?
- `WHERE`와 `HAVING`은 어떻게 역할이 나뉠까요?

## 큰 그림

![SQL 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/sql-101/05/05-01-aggregation-flow.ko.png)

*SQL 101 5장 흐름 개요*

이 그림에서는 GROUP BY가 행들을 어떻게 묶고, 집계 함수가 각 그룹에서 어떤 값을 계산하는지 봅니다. 집계는 많은 행을 적은 수의 그룹 행으로 축약하는 강력한 도구입니다.

> GROUP BY의 핵심은 집계 함수의 이름이 아니라, 어떤 기준으로 행을 나누고 각 그룹에서 어떤 값을 요약할 때 데이터의 의미가 유지되는지 정확히 판단하는 데 있습니다.

## 왜 중요한가

대부분의 보고서는 결국 집계입니다. 일별 활성 사용자, 국가별 평균 구매액, 사용자당 주문 수 같은 숫자는 데이터가 많아질수록 더 자주 요구됩니다. 이때 그룹 기준을 잘못 잡거나 조인 후 카디널리티를 놓치면, 겉보기에는 멀쩡한 숫자가 나와도 실제로는 틀린 결과가 될 수 있습니다.

또 집계는 행을 압축하는 작업이기 때문에, 무엇이 사라지고 무엇이 남는지 항상 의식해야 합니다. 개별 주문 행은 사라지지만, 국가별 총액은 남습니다. 이 감각이 있어야 집계 결과를 읽고 검증할 수 있습니다.

## 집계 흐름

`WHERE`는 집계 전에 행을 걸러 내고, `GROUP BY`는 남은 행을 묶고, 집계 함수는 그룹마다 숫자를 계산합니다. 그 뒤 `HAVING`은 계산된 그룹 결과를 다시 걸러 냅니다. 이 순서를 머리에 넣어 두면 `WHERE COUNT(*) > 1` 같은 오류가 왜 생기는지 바로 이해됩니다.

## 핵심 개념 정리

### 그룹 키는 행을 어떤 관점으로 묶을지 정한다

`GROUP BY country`라면 국가별로 묶는 것이고, `GROUP BY country, day`라면 국가와 날짜 조합별로 묶는 것입니다. 같은 데이터라도 어떤 열을 그룹 키로 선택하느냐에 따라 완전히 다른 보고서가 됩니다.

### 집계 함수마다 NULL 처리 방식이 다르다

`COUNT(*)`는 행 자체를 세고, `COUNT(col)`은 해당 컬럼이 `NULL`이 아닌 행만 셉니다. `AVG`도 `NULL` 값을 0으로 보지 않고 제외합니다. 이 차이를 모르고 읽으면 숫자 해석이 어긋납니다.

### HAVING은 집계된 결과를 위한 조건이다

집계 전에 걸러야 하는 조건은 `WHERE`, 집계 결과에 대한 조건은 `HAVING`입니다. 사용자 수가 100명 이상인 국가만 보고 싶다면 먼저 국가별 집계를 만든 뒤 `HAVING COUNT(*) > 100`으로 걸러야 합니다.

## 다섯 가지 집계 패턴

### 1단계 — 전체 행 수 세기

```sql
SELECT COUNT(*) AS total_users FROM users;
```

가장 단순한 집계입니다. 전체 사용자 수처럼 하나의 숫자만 필요할 때 자주 등장합니다.

### 2단계 — 범주별 개수 세기

```sql
SELECT country, COUNT(*) AS users
FROM users
GROUP BY country;
```

**Expected output:**

| country | users |
| --- | --- |
| KR | 2 |
| US | 1 |

국가마다 몇 명이 있는지처럼 그룹별 숫자를 만들 때 가장 기본이 되는 형태입니다.

### 3단계 — 여러 기준으로 묶기

```sql
SELECT country, signup_at::date AS day, COUNT(*) AS users
FROM users
GROUP BY country, day;
```

국가별이면서 동시에 날짜별인 숫자를 만들 때 씁니다. 그룹 키가 늘어날수록 결과는 더 세분화됩니다.

### 4단계 — 집계 결과에 조건 걸기

```sql
SELECT country, COUNT(*) AS users
FROM users
GROUP BY country
HAVING COUNT(*) > 100;
```

먼저 국가별 사용자 수를 계산한 뒤, 100명을 넘는 국가만 남깁니다.

### 5단계 — 중복 제거 후 세기

```sql
SELECT country, COUNT(DISTINCT user_id) AS active_users
FROM events
GROUP BY country;
```

이벤트 테이블처럼 한 사용자가 여러 행을 가질 때는 `COUNT(DISTINCT ...)`가 자주 필요합니다. 다만 비용이 큰 연산일 수 있다는 점을 함께 기억해야 합니다.

## 이 코드에서 먼저 봐야 할 점

- `WHERE`는 집계 전, `HAVING`은 집계 후에 동작합니다.
- `COUNT(*)`와 `COUNT(col)`은 같은 것이 아닙니다.
- `COUNT(DISTINCT ...)`는 큰 테이블에서 비용이 커질 수 있습니다.

## 실무에서 자주 헷갈리는 지점

### 왜 그룹에 없는 컬럼은 SELECT에 못 적을까

집계 결과는 그룹마다 한 행으로 줄어듭니다. 그런데 그룹 키도 아니고 집계 함수도 아닌 컬럼을 함께 고르면, 그 그룹 안의 어떤 값을 대표로 보여 줘야 하는지 결정할 수 없습니다. 그래서 대부분의 데이터베이스는 오류를 냅니다.

### 조인 뒤 집계가 왜 쉽게 틀릴까

주문과 주문 항목을 조인한 뒤 주문 금액을 합산하면, 한 주문이 여러 항목으로 반복될 수 있습니다. 이런 경우에는 작은 쪽을 먼저 집계하거나, 조인 전후 행 수를 반드시 비교해야 합니다.

### 너무 많은 컬럼으로 그룹화하면 어떤 문제가 생길까

그룹 키를 지나치게 많이 넣으면 사실상 원본 행을 거의 그대로 유지하는 결과가 됩니다. 숫자는 나오지만 해석 가능한 집계가 되지 않습니다. 그룹 키는 보고 싶은 관점을 드러내는 최소 단위여야 합니다.

## 집계 함수 비교 표

집계 함수는 여러 행을 하나의 값으로 압축하는 도구입니다. 각 함수는 NULL을 다루는 방식과 주의점이 다릅니다.

| 함수 | 역할 | NULL 처리 | 주의점 |
| --- | --- | --- | --- |
| `COUNT(*)` | 전체 행 수 | NULL도 포함 | 가장 기본적인 집계 |
| `COUNT(col)` | 특정 컴럼의 NULL 아닌 행 수 | NULL 제외 | `COUNT(*)`와 다름 |
| `SUM(col)` | 합계 | NULL 제외 | 모든 값이 NULL이면 NULL 반환 |
| `AVG(col)` | 평균 | NULL 제외 | NULL을 0으로 간주하지 않음 |
| `MIN(col)` | 최소값 | NULL 제외 | 문자열, 날짜에도 사용 가능 |
| `MAX(col)` | 최대값 | NULL 제외 | 문자열, 날짜에도 사용 가능 |

### NULL 처리 예제

```sql
CREATE TABLE sales (
    id INT,
    amount INT
);

INSERT INTO sales VALUES (1, 100), (2, NULL), (3, 200);

SELECT 
    COUNT(*) AS total_rows,
    COUNT(amount) AS non_null_count,
    SUM(amount) AS total_amount,
    AVG(amount) AS avg_amount
FROM sales;
```

**Expected output:**

| total_rows | non_null_count | total_amount | avg_amount |
| --- | --- | --- | --- |
| 3 | 2 | 300 | 150 |

`COUNT(*)`는 3을 반환하지만, `COUNT(amount)`는 NULL을 제외하고 2를 반환합니다. `AVG(amount)`는 300 / 2 = 150이지, 300 / 3 = 100이 아닙니다.

## GROUP BY + HAVING 복합 예제

### 국가별 사용자 수 집계 + 필터링

```sql
SELECT 
    country,
    COUNT(*) AS user_count,
    AVG(age) AS avg_age
FROM users
GROUP BY country
HAVING COUNT(*) >= 10
ORDER BY user_count DESC;
```

이 쿼리는 국가별로 사용자를 묶고, 10명 이상인 국가만 남기고, 사용자 수 내림차순으로 정렬합니다. `HAVING`은 집계 후 필터링이므로, `COUNT(*)`처럼 집계 함수를 쓸 수 있습니다.

### 주문 상태별 금액 합계

```sql
SELECT 
    status,
    COUNT(*) AS order_count,
    SUM(total) AS total_amount,
    AVG(total) AS avg_amount,
    MIN(total) AS min_amount,
    MAX(total) AS max_amount
FROM orders
WHERE created_at >= '2026-01-01'
GROUP BY status
HAVING SUM(total) > 1000
ORDER BY total_amount DESC;
```

이 쿼리는 2026년 이후 주문을 상태별로 묶고, 총액이 1000 이상인 그룹만 보여 줍니다. 여러 집계 함수를 함께 쓰면 한 번에 다양한 통계를 볼 수 있습니다.

### 여러 기준으로 그룹화 + HAVING

```sql
SELECT 
    country,
    DATE_TRUNC('month', signup_at) AS month,
    COUNT(*) AS new_users
FROM users
WHERE signup_at >= '2025-01-01'
GROUP BY country, month
HAVING COUNT(*) >= 5
ORDER BY country, month;
```

국가와 월을 함께 그룹 키로 쓰면, 국가별이면서 동시에 월별인 세분화된 결과를 얻을 수 있습니다. 이 패턴은 시계열 분석에서 자주 나옵니다.

### 조인 후 집계 + HAVING

```sql
SELECT 
    u.country,
    COUNT(DISTINCT o.id) AS order_count,
    SUM(o.total) AS total_revenue
FROM users u
JOIN orders o ON o.user_id = u.id
WHERE o.status = 'completed'
GROUP BY u.country
HAVING COUNT(DISTINCT o.id) >= 100
ORDER BY total_revenue DESC;
```

조인을 한 뒤 집계할 때는 카디널리티를 특히 조심해야 합니다. 한 사용자가 여러 주문을 가지므로 `COUNT(DISTINCT o.id)`로 중복을 제거해야 정확한 주문 수를 얻을 수 있습니다.

## WINDOW 함수와의 차이

집계 함수는 여러 행을 하나로 압축하지만, WINDOW 함수(윈도우 함수)는 행을 유지하면서 집계 값을 계산합니다. 이 차이를 이해하면 언제 `GROUP BY`를 쓰고 언제 WINDOW 함수를 써야 할지 판단할 수 있습니다.

### GROUP BY로 집계 (행을 압축)

```sql
SELECT 
    country,
    COUNT(*) AS user_count
FROM users
GROUP BY country;
```

**Expected output:**

| country | user_count |
| --- | --- |
| US | 5 |
| UK | 3 |

결과는 국가당 한 행으로 압축됩니다. 개별 사용자 정보는 사라집니다.

### WINDOW 함수로 집계 (행을 유지)

```sql
SELECT 
    name,
    country,
    COUNT(*) OVER (PARTITION BY country) AS user_count
FROM users;
```

**Expected output:**

| name | country | user_count |
| --- | --- | --- |
| Ada | US | 5 |
| Bob | US | 5 |
| Grace | UK | 3 |

각 행은 그대로 유지되고, `user_count` 컴럼에 그 사용자가 속한 국가의 전체 사용자 수가 표시됩니다.

### 언제 무엇을 쓸까

- **GROUP BY**: 결과를 그룹별 한 행으로 압축하고 싶을 때
- **WINDOW 함수**: 개별 행을 유지하면서 그룹 통계를 각 행에 표시하고 싶을 때

예를 들어 국가별 합계만 보고 싶다면 `GROUP BY`를 쓰고, 각 주문의 금액과 함께 그 국가의 전체 합계를 함께 표시하고 싶다면 WINDOW 함수를 씁니다.

```sql
-- 각 주문의 금액과, 그 국가의 전체 합계를 함께 표시
SELECT 
    o.id AS order_id,
    u.country,
    o.total AS order_total,
    SUM(o.total) OVER (PARTITION BY u.country) AS country_total
FROM orders o
JOIN users u ON u.id = o.user_id;
```

이 쿼리는 각 주문 행을 유지하면서, 그 주문이 속한 국가의 전체 주문 합계를 함께 보여 줍니다. 이렇게 하면 개별 주문의 비율을 계산하거나, 순위를 매기는 분석을 할 때 유용합니다.

WINDOW 함수는 다음 글에서 자세히 다루지만, 여기서는 집계 함수와의 관계만 알아 두면 충분합니다.
## 체크리스트

- [ ] `WHERE`와 `HAVING`의 차이를 설명할 수 있다.
- [ ] `COUNT(*)`와 `COUNT(col)`의 차이를 알고 있다.
- [ ] 여러 컬럼으로 그룹화할 수 있다.
- [ ] 조인 뒤 집계할 때 카디널리티를 먼저 확인한다.
- [ ] `NULL`이 별도 그룹으로 보일 수 있다는 점을 이해하고 있다.

## 정리

`GROUP BY`와 집계 함수는 많은 행을 숫자로 바꾸는 핵심 도구입니다. 어떤 기준으로 묶는지, 집계 함수가 `NULL`을 어떻게 다루는지, 조건을 집계 전과 후 중 어디에 둬야 하는지를 이해하면 보고서의 기본 구조를 훨씬 안정적으로 만들 수 있습니다.

다음 글에서는 복잡한 질문을 여러 단계로 나누는 방법인 서브쿼리와 CTE를 다루겠습니다.

## 집계 작성 모범 사례

실무에서 집계 쿼리를 작성할 때 자주 마주치는 패턴을 좋은 예와 피할 예로 비교합니다.

```sql
-- 좋은 예: 그룹 키와 집계 함수 명확히
SELECT 
    country,
    DATE_TRUNC('month', signup_at) AS signup_month,
    COUNT(*) AS new_users,
    AVG(age) AS avg_age
FROM users
WHERE signup_at >= '2025-01-01'
GROUP BY country, signup_month
HAVING COUNT(*) >= 10
ORDER BY country, signup_month;

-- 피할 예: 그룹 키가 불분명하고 별칭 없음
-- SELECT country, DATE_TRUNC('month', signup_at), COUNT(*), AVG(age)
-- FROM users WHERE signup_at >= '2025-01-01'
-- GROUP BY country, DATE_TRUNC('month', signup_at);
```
## 처음 질문으로 돌아가기

- **`GROUP BY`는 언제 실행되고 무엇을 기준으로 묶을까요?**
  - GROUP BY는 같은 값을 가진 행들을 묶어서, 각 그룹에 대해 집계 함수(SUM, COUNT, AVG 등)로 요약 값을 계산합니다.
- **`SUM`, `COUNT`, `AVG` 같은 집계 함수는 어떤 차이를 가질까요?**
  - GROUP BY 기준이 모호하거나 잘못되면, 비즈니스 질문에 맞지 않는 그룹으로 데이터를 잘못 요약할 수 있습니다.
- **`WHERE`와 `HAVING`은 어떻게 역할이 나뉠까요?**
  - 집계 결과를 필터링할 때는 WHERE가 아니라 HAVING을 사용합니다. WHERE는 개별 행을 필터링하고, HAVING은 그룹을 필터링합니다.

<!-- toc:begin -->
## 시리즈 목차

- [SQL 101 (1/10): SQL이란 무엇인가?](./01-what-is-sql.md)
- [SQL 101 (2/10): SELECT 기본](./02-select-basics.md)
- [SQL 101 (3/10): WHERE와 조건](./03-where-and-conditions.md)
- [SQL 101 (4/10): JOIN 이해하기](./04-join.md)
- **GROUP BY와 집계 함수 (현재 글)**
- 서브쿼리와 CTE (예정)
- 윈도 함수 (예정)
- 데이터를 바꾸는 SQL — INSERT, UPDATE, DELETE (예정)
- 인덱스와 쿼리 계획 (예정)
- 실전 분석 SQL (예정)

<!-- toc:end -->

## 참고 자료

- [PostgreSQL — GROUP BY](https://www.postgresql.org/docs/current/tutorial-agg.html)
- [PostgreSQL — Aggregate Functions](https://www.postgresql.org/docs/current/functions-aggregate.html)
- [Mode — GROUP BY](https://mode.com/sql-tutorial/sql-group-by/)
- [SQLBolt — Aggregates](https://sqlbolt.com/lesson/select_queries_with_aggregates)

Tags: SQL, Database, Postgres, Analytics
