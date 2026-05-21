---
series: sql-101
episode: 4
title: "SQL 101 (4/10): JOIN 이해하기"
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
  - JOIN
  - Relational
  - Database
  - Query
seo_description: INNER·LEFT·RIGHT·FULL·CROSS JOIN의 차이와 카디널리티 함정을 실전 감각으로 설명합니다
last_reviewed: '2026-05-15'
---

# SQL 101 (4/10): JOIN 이해하기

SQL을 배우다 보면 어느 순간부터 질문이 한 테이블 안에서 끝나지 않습니다. 어떤 사용자가 어떤 주문을 했는지, 그 주문에 어떤 상품이 들어 있었는지, 결제는 어떻게 나뉘었는지까지 보려면 여러 테이블을 함께 읽어야 합니다. 이때 시작되는 주제가 `JOIN`입니다.

이 글은 SQL 101 시리즈의 네 번째 글입니다. 여기서는 JOIN을 컬럼을 붙이는 기교가 아니라, 서로 다른 집합의 행을 어떤 기준으로 연결할지 결정하는 연산으로 설명합니다.

## 먼저 던지는 질문

- `INNER JOIN`, `LEFT JOIN`, `RIGHT JOIN`, `FULL JOIN`, `CROSS JOIN`은 무엇이 다를까요?
- 조인 키와 카디널리티는 왜 먼저 확인해야 할까요?
- 결과가 예상보다 갑자기 커지는 이유는 무엇일까요?

## 큰 그림

![SQL 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/sql-101/04/04-01-join-result-flow.ko.png)

*SQL 101 4장 흐름 개요*

이 그림에서는 JOIN이 여러 테이블을 어떻게 연결하는지 봅니다. 조인의 종류와 조인 조건이 결과 집합의 크기와 내용을 어떻게 결정하는지를 이해하는 것이 중요합니다.

> JOIN의 핵심은 조인 종류의 이름을 외우는 것이 아니라, 어떤 조건으로 어떤 두 테이블을 연결할 때 결과가 어떻게 달라지는지 정확히 예측할 수 있는 것입니다.

## 왜 중요한가

실무 쿼리의 대부분은 조인을 포함합니다. 보고서에서는 사용자, 주문, 상품, 이벤트 테이블이 함께 등장하고, 서비스 운영 쿼리에서도 관계를 따라가며 데이터를 읽습니다. 이때 조인의 핵심은 문법보다 카디널리티입니다. 한 사용자가 주문을 여러 번 가질 수 있고, 한 주문이 여러 결제로 나뉠 수 있다는 사실을 놓치면 합계가 쉽게 부풀어 오릅니다.

좋은 분석가는 JOIN을 많이 아는 사람이 아니라, 조인 전후의 행 수가 왜 변하는지 설명할 수 있는 사람에 가깝습니다.

## JOIN 결과 흐름

`INNER JOIN`은 양쪽에 모두 존재하는 행만 남기고, `LEFT JOIN`은 왼쪽 테이블의 행을 모두 보존합니다. `CROSS JOIN`은 조건 없이 가능한 모든 조합을 만들기 때문에 특히 조심해야 합니다.

## 핵심 개념 정리

### 조인 키는 테이블을 연결하는 기준이다

조인 키는 두 테이블이 서로 어떤 행과 연결되는지를 결정하는 열입니다. 보통 기본 키와 외래 키 조합이 자주 쓰입니다. 예를 들어 `users.id`와 `orders.user_id`는 사용자를 주문과 연결하는 전형적인 키입니다.

### 카디널리티는 조인 결과의 크기를 예측하게 해 준다

카디널리티는 한 행이 다른 테이블에서 몇 개의 짝을 가질 수 있는지를 뜻합니다. 1:1인지, 1:N인지, N:M인지에 따라 결과 행 수와 집계 방식이 달라집니다. 조인 전 합계가 조인 후 달라졌다면 대부분 카디널리티를 놓친 경우입니다.

### LEFT JOIN의 NULL은 의미 있는 신호다

`LEFT JOIN` 후 오른쪽 테이블 컬럼이 `NULL`로 보인다면, 대개 매칭되는 행이 없었다는 뜻입니다. 이 특성을 이용해 주문이 없는 사용자처럼 짝이 없는 행을 찾을 수 있습니다.

## 다섯 가지 조인 패턴

### 1단계 — 내부 조인

```sql
SELECT u.name, o.id AS order_id
FROM users u
INNER JOIN orders o ON o.user_id = u.id;
```

주문이 있는 사용자만 결과에 남습니다. 양쪽에 연결되는 행이 있을 때만 보인다고 이해하면 됩니다.

### 2단계 — 왼쪽 조인

```sql
SELECT u.name, o.id AS order_id
FROM users u
LEFT JOIN orders o ON o.user_id = u.id;
```

주문이 없는 사용자도 빠지지 않습니다. 대신 오른쪽 컬럼인 `order_id`는 `NULL`일 수 있습니다.

### 3단계 — 짝이 없는 행 찾기

```sql
SELECT u.id, u.name
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE o.id IS NULL;
```

**Expected output:**

| id | name |
| --- | --- |
| 3 | Grace |

주문이 한 건도 없는 사용자를 찾는 전형적인 패턴입니다. `LEFT JOIN` 뒤 `NULL` 여부를 보는 이유를 잘 보여 줍니다.

### 4단계 — 자기 자신과 조인하기

```sql
SELECT e.name AS emp, m.name AS manager
FROM employees e
LEFT JOIN employees m ON m.id = e.manager_id;
```

같은 테이블 안에서도 관계를 따라갈 수 있습니다. 직원과 관리자처럼 계층 구조를 표현할 때 자주 쓰입니다.

### 5단계 — 여러 테이블을 연결하기

```sql
SELECT u.name, p.name AS product
FROM users u
JOIN orders o ON o.user_id = u.id
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON p.id = oi.product_id;
```

실전 쿼리는 대개 이런 식으로 세 개 이상 테이블이 이어집니다. 이때는 각 단계의 카디널리티를 끊어서 점검하는 습관이 중요합니다.

## 이 코드에서 먼저 봐야 할 점

- `LEFT JOIN` 뒤의 `NULL`은 데이터 오류가 아니라 매칭 없음의 신호일 수 있습니다.
- 여러 테이블을 조인할수록 기준 테이블과 각 단계의 관계를 더 명확히 확인해야 합니다.
- 조인 결과를 바로 합계 내기 전에 행 수가 얼마나 늘었는지 먼저 확인하는 편이 안전합니다.

## 실무에서 자주 헷갈리는 지점

### 합계가 왜 두 배, 세 배로 불어날까

예를 들어 주문 한 건이 결제 두 건으로 나뉘어 있다면, `orders`와 `payments`를 그대로 조인한 뒤 주문 금액을 합산하면 주문 금액이 결제 건수만큼 반복됩니다. 이런 경우에는 결제 테이블을 먼저 집계해 1:1 형태로 만든 뒤 조인하는 편이 안전합니다.

### LEFT JOIN 뒤에 WHERE를 잘못 쓰면 어떻게 될까

`LEFT JOIN`을 했더라도 이후 `WHERE o.status = 'paid'`처럼 오른쪽 테이블 조건을 직접 걸면, `NULL` 행이 제거되어 사실상 `INNER JOIN`처럼 동작할 수 있습니다. 왼쪽 행을 보존하려면 조건을 `ON` 절에 둘지, `WHERE`에 둘지를 의식적으로 결정해야 합니다.

### 실수로 CROSS JOIN이 생기는 경우

조인 조건을 빠뜨리면 가능한 모든 조합이 만들어집니다. 작은 샘플에서는 티가 안 나도, 실무 데이터에서는 행 수가 순식간에 폭증합니다. 조인 조건이 있는지, 조인 키가 맞는지 검토하는 습관이 필요합니다.

## JOIN 유형 비교

JOIN은 두 테이블을 어떻게 연결할지 결정하는 연산입니다. 각 JOIN 유형은 결과 행 수와 내용을 다르게 만듭니다. 다음 표는 주요 JOIN 유형의 차이를 보여 줍니다.

| JOIN 유형 | 결과 행 | 설명 | Venn 다이어그램 설명 |
| --- | --- | --- | --- |
| `INNER JOIN` | 양쪽 테이블에 모두 존재하는 행만 | 조인 조건을 만족하는 행만 반환 | 교집합 |
| `LEFT JOIN` | 왼쪽 테이블의 모든 행 + 오른쪽 매칭 | 왼쪽 테이블 행은 모두 보존, 오른쪽은 매칭되면 표시 | 왼쪽 전체 |
| `RIGHT JOIN` | 오른쪽 테이블의 모든 행 + 왼쪽 매칭 | 오른쪽 테이블 행은 모두 보존, 왼쪽은 매칭되면 표시 | 오른쪽 전체 |
| `FULL OUTER JOIN` | 양쪽 테이블의 모든 행 | 매칭되지 않는 행도 모두 표시 (NULL 포함) | 합집합 |
| `CROSS JOIN` | 가능한 모든 조합 (Cartesian product) | 조인 조건 없이 모든 행 조합 | 모든 조합 |

### 각 JOIN의 행 수 예측

- **INNER JOIN**: 최소 0개, 최대 `min(left_count, right_count)`
- **LEFT JOIN**: 정확히 `left_count` (1:N 관계면 더 많을 수 있음)
- **RIGHT JOIN**: 정확히 `right_count` (1:N 관계면 더 많을 수 있음)
- **FULL OUTER JOIN**: 최소 `max(left_count, right_count)`, 최대 `left_count + right_count`
- **CROSS JOIN**: 정확히 `left_count × right_count`

실무에서 가장 자주 쓰는 것은 `INNER JOIN`과 `LEFT JOIN`입니다. `CROSS JOIN`은 의도치 않게 조인 조건을 빠뜨릴 때 발생하기 쉬우므로 특히 조심해야 합니다.

## 다중 테이블 JOIN 예제

실무에서는 두 테이블만 연결하는 경우보다 세 개 이상 테이블을 연결하는 경우가 훨씬 많습니다. 이때는 각 단계마다 어떤 테이블이 어떻게 연결되는지 명확하게 파악해야 합니다.

### 사용자 → 주문 → 결제 연결

```sql
SELECT 
    u.name AS user_name,
    o.id AS order_id,
    o.total AS order_total,
    p.amount AS payment_amount,
    p.status AS payment_status
FROM users u
JOIN orders o ON o.user_id = u.id
JOIN payments p ON p.order_id = o.id
WHERE u.country = 'US'
ORDER BY u.id, o.id;
```

이 쿼리는 세 테이블을 순차적으로 연결합니다. 먼저 `users`와 `orders`를 연결하고, 그 결과에 `payments`를 다시 연결합니다. 이때 주의할 점은 한 주문에 여러 결제가 있으려나, 한 사용자가 여러 주문을 가지면 결과 행이 불어납니다.

### 사용자 → 주문 → 주문 항목 → 상품 연결

```sql
SELECT 
    u.name AS user_name,
    o.id AS order_id,
    prod.name AS product_name,
    oi.quantity,
    oi.price
FROM users u
JOIN orders o ON o.user_id = u.id
JOIN order_items oi ON oi.order_id = o.id
JOIN products prod ON prod.id = oi.product_id
WHERE o.status = 'completed'
ORDER BY u.id, o.id, oi.id;
```

이 쿼리는 네 테이블을 연결합니다. 한 주문에 여러 항목이 있으므로, 결과는 주문 항목 수만큼 반복됩니다. 이럴 때 주문 금액을 그냥 합산하면 항목 수만큼 불어나므로 조심해야 합니다.

### 여러 단계 LEFT JOIN

```sql
SELECT 
    u.name,
    o.id AS order_id,
    p.amount AS payment_amount
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
LEFT JOIN payments p ON p.order_id = o.id;
```

모든 사용자를 보존하면서 주문과 결제 정보를 붙이는 패턴입니다. 주문이 없는 사용자는 `order_id`와 `payment_amount`가 모두 `NULL`로 나옵니다.

## 자기 조인 (Self Join)

같은 테이블을 두 번 참조하여 조인하는 기법을 자기 조인이라고 부릅니다. 계층 구조나 그래프 관계를 표현할 때 유용합니다.

### 직원과 관리자 관계

```sql
CREATE TABLE employees (
    id INT PRIMARY KEY,
    name TEXT NOT NULL,
    manager_id INT
);

INSERT INTO employees (id, name, manager_id) VALUES
    (1, 'Alice', NULL),
    (2, 'Bob', 1),
    (3, 'Charlie', 1),
    (4, 'Diana', 2);

-- 직원과 그 관리자 이름을 함께 표시
SELECT 
    e.name AS employee,
    m.name AS manager
FROM employees e
LEFT JOIN employees m ON m.id = e.manager_id;
```

**Expected output:**

| employee | manager |
| --- | --- |
| Alice | NULL |
| Bob | Alice |
| Charlie | Alice |
| Diana | Bob |

이 패턴은 같은 테이블을 `e`와 `m`이라는 별칭으로 두 번 참조합니다. `e`는 직원, `m`은 관리자로 해석할 수 있습니다.

### 같은 국가 사용자 쌍 찾기

```sql
-- 같은 국가에 사는 다른 사용자 쌍
SELECT 
    u1.name AS user1,
    u2.name AS user2,
    u1.country
FROM users u1
JOIN users u2 ON u1.country = u2.country AND u1.id < u2.id;
```

이 쿼리는 같은 국가에 사는 사용자 쌍을 찾습니다. `u1.id < u2.id` 조건을 붙여서 중복 조합을 피합니다. 자기 자신과의 조합도 제외됩니다.

### 연속된 이벤트 찾기

```sql
-- 같은 사용자의 연속된 두 이벤트
SELECT 
    e1.user_id,
    e1.event_name AS first_event,
    e2.event_name AS next_event,
    e2.created_at - e1.created_at AS time_diff
FROM events e1
JOIN events e2 ON e2.user_id = e1.user_id AND e2.id = e1.id + 1
ORDER BY e1.user_id, e1.id;
```

이 쿼리는 같은 사용자의 연속된 두 이벤트를 찾습니다. 실무에서는 이런 패턴으로 사용자 행동 흐름을 분석하거나, 퍼널 분석을 할 때 자주 나옵니다.

자기 조인은 처음에는 낯설 수 있지만, 한 번 이해하면 계층 구조나 시계열 비교 같은 복잡한 문제를 훨씬 간결하게 해결할 수 있습니다.
## 체크리스트

- [ ] `INNER JOIN`과 `LEFT JOIN`의 차이를 설명할 수 있다.
- [ ] 조인 전에 카디널리티를 먼저 적어 보는 습관이 있다.
- [ ] `LEFT JOIN` 뒤 `NULL`이 무엇을 뜻하는지 알고 있다.
- [ ] 짝이 없는 행을 찾는 안티 조인 패턴을 쓸 수 있다.
- [ ] 조인 후 바로 합계 내기 전에 행 수를 먼저 검증한다.

## 정리

JOIN의 본질은 집합과 관계를 읽는 데 있습니다. 어떤 키로 연결하는지, 한 행이 몇 개의 짝을 가질 수 있는지, 그 결과 행 수가 어떻게 바뀌는지를 이해해야 안전한 조인이 가능합니다. 문법보다 카디널리티를 먼저 보는 습관이 실무에서 특히 중요합니다.

다음 글에서는 여러 행을 하나의 의미 있는 숫자로 압축하는 `GROUP BY`와 집계 함수를 다룹니다.

## 처음 질문으로 돌아가기

- **`INNER JOIN`, `LEFT JOIN`, `RIGHT JOIN`, `FULL JOIN`, `CROSS JOIN`은 무엇이 다를까요?**
  - JOIN은 여러 테이블의 행을 조건에 따라 연결하는 작업입니다. 조인 종류와 조인 조건이 결과의 크기를 좌우합니다.
- **조인 키와 카디널리티는 왜 먼저 확인해야 할까요?**
  - INNER JOIN은 양쪽 테이블 모두에 일치하는 행만 반환하고, LEFT JOIN은 왼쪽 테이블의 모든 행을 남긴 채로 오른쪽을 붙입니다.
- **결과가 예상보다 갑자기 커지는 이유는 무엇일까요?**
  - 조인 조건이 잘못되면 의도하지 않은 중복이나 누락이 생깁니다. 항상 조인 기준을 명확히 해야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [SQL 101 (1/10): SQL이란 무엇인가?](./01-what-is-sql.md)
- [SQL 101 (2/10): SELECT 기본](./02-select-basics.md)
- [SQL 101 (3/10): WHERE와 조건](./03-where-and-conditions.md)
- **JOIN 이해하기 (현재 글)**
- GROUP BY와 집계 함수 (예정)
- 서브쿼리와 CTE (예정)
- 윈도 함수 (예정)
- 데이터를 바꾸는 SQL — INSERT, UPDATE, DELETE (예정)
- 인덱스와 쿼리 계획 (예정)
- 실전 분석 SQL (예정)

<!-- toc:end -->

## 참고 자료

- [PostgreSQL — Joins](https://www.postgresql.org/docs/current/tutorial-join.html)
- [SQLBolt — Multi-table queries with JOIN](https://sqlbolt.com/lesson/select_queries_with_joins)
- [Mode — JOIN](https://mode.com/sql-tutorial/sql-joins/)
- [Use The Index, Luke — Joins](https://use-the-index-luke.com/sql/join)

Tags: SQL, Database, Postgres, Analytics
