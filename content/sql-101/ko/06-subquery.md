---
series: sql-101
episode: 6
title: "SQL 101 (6/10): 서브쿼리와 CTE"
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
  - Subquery
  - CTE
  - Database
  - Query
seo_description: 서브쿼리, EXISTS, 인라인 뷰, CTE로 복잡한 SQL을 읽기 좋은 단계로 나누는 법을 설명합니다
last_reviewed: '2026-05-15'
---

# SQL 101 (6/10): 서브쿼리와 CTE

실전 SQL은 한 줄로 끝나지 않는 경우가 많습니다. 사용자별 주문 합계를 먼저 만들고, 그중 큰 금액만 골라 다시 사용자 정보와 붙이는 식으로 질문이 겹겹이 쌓입니다. 이때 한 문장 안에 모든 로직을 밀어 넣으면 읽는 사람도, 나중에 고치는 사람도 곧 길을 잃습니다.

이 글은 SQL 101 시리즈의 여섯 번째 글입니다. 여기서는 서브쿼리와 CTE를 사용해 복잡한 질문을 단계로 나누고, 읽을 수 있는 SQL로 바꾸는 방법을 설명합니다.

## 먼저 던지는 질문

- 서브쿼리는 언제 쓰고, CTE는 언제 더 나을까요?
- 스칼라 서브쿼리와 인라인 뷰는 무엇이 다를까요?
- `IN`과 `EXISTS`는 어떤 상황에서 차이가 날까요?

## 큰 그림

![SQL 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/sql-101/06/06-01-subquery-layering-flow.ko.png)

*SQL 101 6장 흐름 개요*

이 그림에서는 서브쿼리가 메인 쿼리 안에 어떻게 내포되고, 각 서브쿼리의 결과가 외부 쿼리에 어떻게 영향을 미치는지 봅니다. 서브쿼리와 CTE는 복잡한 로직을 단계적으로 나누는 방법입니다.

> 서브쿼리와 CTE의 핵심은 문법 자체가 아니라, 큰 질문을 작은 단계로 나누어 각 단계의 결과가 명확하고 검증 가능하도록 설계하는 데 있습니다.

## 왜 중요한가

분석과 리포트는 대개 단계적입니다. 전체 이벤트에서 코호트 기준일을 만들고, 활동 로그를 붙이고, 다시 집계해 유지율을 구하는 식입니다. 이 과정을 한 덩어리 쿼리로 쓰면 문법은 맞더라도 팀이 함께 검토하기 어려워집니다.

반대로 의미 있는 단계 이름을 붙여 CTE로 나누면, 쿼리를 위에서 아래로 읽으며 각 중간 결과를 검증할 수 있습니다. 실무에서 좋은 SQL은 짧은 SQL이 아니라, 중간 의도를 설명할 수 있는 SQL인 경우가 많습니다.

## 서브쿼리 분해 흐름

내부 쿼리는 바깥 쿼리에 재료를 제공합니다. 이 재료를 이름 붙여 꺼내 놓은 형태가 CTE입니다. 의미는 비슷하지만, 사람이 읽는 경험은 꽤 달라집니다.

## 핵심 개념 정리

### 스칼라 서브쿼리는 값 하나를 돌려준다

스칼라 서브쿼리는 바깥 행마다 하나의 값이 필요할 때 사용합니다. 예를 들어 각 사용자 옆에 주문 수 한 개를 붙이고 싶을 때 어울립니다.

### 인라인 뷰는 FROM 절 안의 임시 테이블이다

`FROM (SELECT ...) AS t` 형태는 중간 결과를 임시 테이블처럼 다루는 방식입니다. 그룹화 결과를 다시 필터링할 때 자주 보입니다.

### CTE는 이름 붙은 중간 단계다

`WITH name AS (...)`는 문법 이상의 의미가 있습니다. 중간 단계가 무엇을 의미하는지 이름으로 드러낼 수 있기 때문입니다. 그래서 팀 협업에서는 인라인 뷰보다 CTE가 더 자주 선택됩니다.

### EXISTS는 존재 여부만 빠르게 확인한다

행이 실제로 존재하는지만 알고 싶다면 `EXISTS`가 의도를 잘 드러냅니다. 값 목록을 비교하는 `IN`과는 느낌이 다릅니다.

## VIEW vs CTE vs 서브쿼리 비교

각각 쿼리 안에서 중간 결과를 다루는 방법이지만, 수명, 최적화, 재사용성 측면에서 차이가 있습니다.

| 항목 | VIEW | CTE | 서브쿼리 |
| --- | --- | --- | --- |
| 수명 | CREATE로 생성 후 영구 존재 | 쿼리 실행 동안만 존재 | 쿼리 실행 동안만 존재 |
| 최적화 | 대개 인라인 확장 (DB마다 다름) | PostgreSQL은 대개 인라인 확장 | 옵티마이저가 최적화 |
| 재사용성 | 여러 쿼리에서 공유 가능 | 같은 문장 안에서만 참조 | 해당 위치에서만 사용 |
| 유지보수 | 스키마 변경 영향 받음 | 쿼리 자체에 정의 포함 | 쿼리 자체에 정의 포함 |
| 가독성 | 이름으로 추상화 | 이름으로 단계 명시 | 중첩 시 읽기 어려움 |

실무에서는 일회성 분석은 CTE로, 여러 곳에서 반복 참조되는 로직은 VIEW로 관리하는 경우가 많습니다. 서브쿼리는 간단한 조건에는 괜찮지만, 중첩이 깊어지면 CTE로 풀어 쓰는 편이 읽기 좋습니다.

## WITH RECURSIVE 예제

CTE는 재귀적으로 동작할 수도 있습니다. 예를 들어 조직도나 댓글 트리처럼 계층 구조를 탐색할 때 유용합니다.

```sql
WITH RECURSIVE employee_tree AS (
    -- 초기 조건: 최상위 관리자
    SELECT id, name, manager_id, 0 AS level
    FROM employees WHERE manager_id IS NULL

    UNION ALL

    -- 재귀 단계: 상위 직원의 부하 직원
    SELECT e.id, e.name, e.manager_id, et.level + 1
    FROM employees e
    JOIN employee_tree et ON e.manager_id = et.id
)
SELECT * FROM employee_tree ORDER BY level, name;
```

**Expected output:**

| id | name | manager_id | level |
| --- | --- | --- | --- |
| 1 | CEO | NULL | 0 |
| 2 | CTO | 1 | 1 |
| 3 | CFO | 1 | 1 |
| 4 | Dev Lead | 2 | 2 |
| 5 | Accountant | 3 | 2 |

재귀 CTE는 초기 쿼리와 재귀 단계로 나뉩니다. 초기 결과를 만든 뒤, 그 결과와 다시 조인하며 점점 범위를 넓혀 가는 구조입니다. 이런 패턴은 트리 전체를 한 번에 가져와야 할 때 특히 강력합니다.

## Materialized View

PostgreSQL에서는 CTE뿐 아니라 Materialized View도 제공합니다. VIEW가 매번 쿼리를 실행하는 반면, Materialized View는 결과를 디스크에 저장해 두고 필요할 때 갱신합니다.

```sql
CREATE MATERIALIZED VIEW user_order_summary AS
SELECT user_id, COUNT(*) AS order_count, SUM(total) AS total_spend
FROM orders
GROUP BY user_id;

-- 데이터 갱신
REFRESH MATERIALIZED VIEW user_order_summary;
```

Materialized View는 복잡한 집계를 미리 계산해 두고, 빠른 조회가 필요할 때 사용합니다. 대신 데이터가 변경되면 수동 또는 스케줄러로 갱신해야 합니다. 실시간성을 포기하는 대신 조회 성능을 얻는 절충입니다.

일반 VIEW와 비교하면 다음과 같습니다:

- **VIEW**: 매번 쿼리 재실행, 항상 최신 데이터, 저장 공간 불필요
- **Materialized View**: 결과 저장, 갱신 전까지 오래된 데이터, 디스크 공간 필요

사용자별 주문 합계처럼 자주 조회하지만 실시간일 필요는 없는 지표는 Materialized View로 만들면 조회 부담을 크게 줄일 수 있습니다.

## IN vs EXISTS 성능 비교

둘 다 필터링에 사용되지만, 데이터 분포와 인덱스 여부에 따라 성능 차이가 날 수 있습니다.

### IN 방식

```sql
SELECT * FROM users
WHERE id IN (SELECT user_id FROM orders WHERE total > 1000);
```

`IN`은 서브쿼리 결과를 먼저 구체화한 뒤 외부 쿼리와 비교합니다. 서브쿼리 결과가 작으면 효율적이지만, 결과가 크면 메모리 부담이 생길 수 있습니다.

### EXISTS 방식

```sql
SELECT * FROM users u
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id AND o.total > 1000
);
```

`EXISTS`는 존재 여부만 확인하므로, 첫 번째 매칭 행을 찾으면 즉시 멈춥니다. 인덱스가 잘 걸려 있으면 `EXISTS`가 더 빠를 수 있습니다.

### 선택 기준

- 서브쿼리 결과가 작고 중복이 없으면: `IN`
- 외부 테이블이 크고 서브쿼리가 빠르게 매칭되면: `EXISTS`
- `NULL` 처리가 중요하면: `EXISTS` (더 안전)

실무에서는 둘 다 작성해 보고 `EXPLAIN ANALYZE`로 비교하는 것이 가장 확실합니다.

## CTE 성능 고려사항

CTE는 가독성을 높여 주지만, PostgreSQL 11 이하에서는 항상 구체화(materialize)되어 최적화 기회를 제한할 수 있습니다. PostgreSQL 12 이상에서는 대부분의 CTE가 인라인 확장되지만, 필요하면 명시적으로 제어할 수 있습니다.

```sql
-- 구체화 강제
WITH big_orders AS MATERIALIZED (
    SELECT user_id, SUM(total) AS spend
    FROM orders GROUP BY user_id
    HAVING SUM(total) > 1000
)
SELECT * FROM big_orders;

-- 인라인 확장 강제
WITH big_orders AS NOT MATERIALIZED (
    SELECT user_id, SUM(total) AS spend
    FROM orders GROUP BY user_id
    HAVING SUM(total) > 1000
)
SELECT * FROM big_orders;
```

대부분의 경우 PostgreSQL 기본 동작에 맡기는 편이 좋지만, CTE를 여러 번 참조하거나 성능이 예상과 다를 때는 `MATERIALIZED` 키워드를 명시적으로 사용할 수 있습니다.

## 서브쿼리 안티패턴

서브쿼리는 편리하지만, 잘못 사용하면 성능 문제를 일으키기 쉽습니다.

### 안티패턴 1: SELECT 절의 상관 서브쿼리 반복

```sql
-- 나쁜 예
SELECT id, name,
    (SELECT COUNT(*) FROM orders WHERE user_id = u.id) AS order_count,
    (SELECT SUM(total) FROM orders WHERE user_id = u.id) AS total_spend
FROM users u;
```

같은 테이블을 두 번 스캔합니다. 더 나은 방식:

```sql
-- 좋은 예
SELECT u.id, u.name,
    COUNT(o.id) AS order_count,
    SUM(o.total) AS total_spend
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;
```

### 안티패턴 2: 중첩 서브쿼리 남발

```sql
-- 읽기 어려움
SELECT * FROM (
    SELECT * FROM (
        SELECT * FROM orders WHERE total > 100
    ) AS t1 WHERE user_id > 10
) AS t2 WHERE created_at > '2025-01-01';
```

CTE로 단계를 명확히 하는 편이 낫습니다:

```sql
-- 명확함
WITH filtered_orders AS (
    SELECT * FROM orders
    WHERE total > 100
      AND user_id > 10
      AND created_at > '2025-01-01'
)
SELECT * FROM filtered_orders;
```

서브쿼리와 CTE는 강력하지만, 무분별하게 쓰면 오히려 복잡도만 올라갑니다. 의미 있는 단계에만 사용하는 것이 중요합니다.
## 다섯 가지 패턴으로 보기

### 1단계 — 스칼라 서브쿼리

```sql
SELECT name,
    (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) AS order_count
FROM users u;
```

각 사용자 행 옆에 주문 수 하나를 붙입니다. 바깥 행마다 내부 쿼리가 의미를 가지므로 구조를 천천히 읽어야 합니다.

### 2단계 — `IN` 사용하기

```sql
SELECT * FROM users
WHERE id IN (SELECT user_id FROM orders WHERE total > 1000);
```

큰 금액 주문을 가진 사용자만 고르는 예시입니다. 서브쿼리가 사용자 ID 목록을 만들고, 바깥 쿼리가 그 목록에 포함되는 행만 남깁니다.

### 3단계 — `EXISTS` 사용하기

```sql
SELECT * FROM users u
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id
);
```

주문이 하나라도 있는 사용자를 찾습니다. 존재 여부가 핵심일 때는 `SELECT 1`처럼 의도를 단순하게 드러내는 편이 읽기 좋습니다.

### 4단계 — 인라인 뷰

```sql
SELECT t.country, t.users
FROM (
    SELECT country, COUNT(*) AS users
    FROM users GROUP BY country
) AS t
WHERE t.users > 100;
```

먼저 국가별 사용자 수를 만들고, 그 결과를 다시 바깥에서 필터링합니다. 집계 후 조건을 적용하는 구조가 잘 보입니다.

### 5단계 — CTE로 단계 이름 붙이기

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

**Expected output:**

| name | spend |
| --- | --- |
| Ada | 1450 |
| Grace | 2100 |

의미 있는 중간 결과에 `big_orders`라는 이름을 붙였습니다. 쿼리를 읽는 사람은 먼저 이 단계의 의미를 이해한 뒤, 다음 조인 단계로 내려오면 됩니다.

## 이 코드에서 먼저 봐야 할 점

- `EXISTS`는 존재 여부만 확인할 때 의도가 분명하고 `NULL` 처리도 비교적 안전합니다.
- 인라인 뷰와 CTE는 유사한 일을 하지만, CTE 쪽이 단계 이름을 드러내기 쉽습니다.
- 상관 서브쿼리는 바깥 행마다 반복 평가될 수 있어 비용이 커질 수 있습니다.

## 실무에서 자주 헷갈리는 지점

### `NOT IN`은 왜 조심해야 할까

서브쿼리 결과 안에 `NULL`이 섞이면 `NOT IN`은 예상과 다른 결과를 만들 수 있습니다. 그래서 부정 조건에서는 `NOT EXISTS`가 더 안전한 경우가 많습니다.

### 상관 서브쿼리는 왜 N+1처럼 느려질 수 있을까

바깥 쿼리의 각 행마다 내부 쿼리가 다시 의미를 가지면, 데이터량이 커질수록 반복 비용이 커집니다. 같은 결과를 조인과 집계 조합으로 바꿀 수 있다면 더 단순하고 빠른 형태가 되는 경우가 많습니다.

### CTE를 너무 깊게 쌓으면 오히려 읽기 어려울 수 있다

CTE는 쪼개기 도구이지만, 무조건 많이 쪼갠다고 좋아지지는 않습니다. 각 단계가 명확한 의미를 가지는지, 이름만 보고도 역할이 떠오르는지가 더 중요합니다.

## 체크리스트

- [ ] 스칼라 서브쿼리, 인라인 뷰, CTE의 차이를 설명할 수 있다.
- [ ] 존재 여부 확인에는 `EXISTS`를 우선 떠올릴 수 있다.
- [ ] `NOT IN`과 `NULL` 조합이 왜 위험한지 알고 있다.
- [ ] 상관 서브쿼리의 비용 문제를 이해하고 있다.
- [ ] 긴 쿼리를 의미 있는 단계 이름으로 나눌 수 있다.

## 정리

서브쿼리와 CTE의 핵심은 복잡한 질문을 읽을 수 있는 층으로 나누는 데 있습니다. 어떤 값 하나를 붙일지, 어떤 목록에 포함되는지, 어떤 중간 결과를 이름 붙여 관리할지를 구분할 수 있으면 큰 SQL도 훨씬 덜 복잡해집니다.

다음 글에서는 집계 결과를 각 행 옆에 다시 붙이는 윈도 함수를 다루겠습니다.

## 처음 질문으로 돌아가기

- **서브쿼리는 언제 쓰고, CTE는 언제 더 나을까요?**
  - 서브쿼리는 쿼리 안에 또 다른 쿼리를 넣는 방식입니다. CTE(WITH 절)는 서브쿼리를 변수처럼 먼저 정의한 후 참조하는 방식입니다.
- **스칼라 서브쿼리와 인라인 뷰는 무엇이 다를까요?**
  - 서브쿼리나 CTE가 없으면 복잡한 로직을 한 번에 한 줄의 SELECT로 풀어야 해서 가독성이 나빠집니다.
- **`IN`과 `EXISTS`는 어떤 상황에서 차이가 날까요?**
  - CTE를 사용하면 각 단계의 의도를 이름으로 명확하게 남길 수 있고, 디버깅과 유지보수가 훨씬 쉬워집니다.

<!-- toc:begin -->
## 시리즈 목차

- [SQL 101 (1/10): SQL이란 무엇인가?](./01-what-is-sql.md)
- [SQL 101 (2/10): SELECT 기본](./02-select-basics.md)
- [SQL 101 (3/10): WHERE와 조건](./03-where-and-conditions.md)
- [SQL 101 (4/10): JOIN 이해하기](./04-join.md)
- [SQL 101 (5/10): GROUP BY와 집계 함수](./05-group-by-and-aggregate.md)
- **서브쿼리와 CTE (현재 글)**
- 윈도 함수 (예정)
- 데이터를 바꾸는 SQL — INSERT, UPDATE, DELETE (예정)
- 인덱스와 쿼리 계획 (예정)
- 실전 분석 SQL (예정)

<!-- toc:end -->

## 참고 자료

- [PostgreSQL — Subqueries](https://www.postgresql.org/docs/current/functions-subquery.html)
- [PostgreSQL — WITH Queries (CTE)](https://www.postgresql.org/docs/current/queries-with.html)
- [Mode — Subqueries](https://mode.com/sql-tutorial/sql-sub-queries/)
- [Use The Index, Luke — IN vs EXISTS](https://use-the-index-luke.com/sql/where-clause/null/not-in)

Tags: SQL, Database, Postgres, Analytics
