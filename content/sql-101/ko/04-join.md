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

이 글은 SQL 101 시리즈의 네 번째 글입니다. 여기서는 JOIN을 컬럼을 붙이는 기교가 아니라, 서로 다른 집합의 행을 어떤 기준으로 연결할지 결정하는 연산으로 설명합니다.

SQL을 배우다 보면 어느 순간부터 질문이 한 테이블 안에서 끝나지 않습니다. 어떤 사용자가 어떤 주문을 했는지, 그 주문에 어떤 상품이 들어 있었는지, 결제는 어떻게 나뉘었는지까지 보려면 여러 테이블을 함께 읽어야 합니다. 이때 시작되는 주제가 `JOIN`입니다.


![SQL 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/sql-101/04/04-01-join-result-flow.ko.png)
*SQL 101 4장 흐름 개요*
> JOIN의 핵심은 조인 종류의 이름을 외우는 것이 아니라, 어떤 조건으로 어떤 두 테이블을 연결할 때 결과가 어떻게 달라지는지 정확히 예측할 수 있는 것입니다.

## 먼저 던지는 질문

- `INNER JOIN`, `LEFT JOIN`, `RIGHT JOIN`, `FULL JOIN`, `CROSS JOIN`은 무엇이 다를까요?
- 조인 키와 카디널리티는 왜 먼저 확인해야 할까요?
- 결과가 예상보다 갑자기 커지는 이유는 무엇일까요?

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


## 실전 앵커: 조인 결과를 그림으로 검증하기

조인은 결과 행 수를 먼저 예측하지 않으면 품질 사고로 이어지기 쉽습니다. 아래처럼 간단한 텍스트 그림을 먼저 적고 쿼리를 작성하면, 중복 증폭을 빠르게 발견할 수 있습니다.

```text
customers (1) ---- (N) orders ---- (N) order_items

고객 1명
  주문 3건
    주문별 아이템 4건, 2건, 1건
=> JOIN 결과는 7행
```

이 행 수 예측을 먼저 해 두면 `COUNT(*)`가 왜 예상보다 크게 나오는지 설명할 수 있습니다.

## 실전 앵커: 중복 증폭 방지 패턴

```sql
-- 문제 패턴: JOIN 후 바로 SUM
SELECT c.customer_id, SUM(oi.quantity * oi.unit_price) AS amount
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY c.customer_id;
```

위 쿼리는 의도에 맞을 수도 있지만, 다른 테이블이 추가되면 금액이 중복 합산될 수 있습니다. 안전한 방식은 집계를 먼저 수행한 뒤 조인하는 것입니다.

```sql
WITH order_amount AS (
    SELECT order_id, SUM(quantity * unit_price) AS amount
    FROM order_items
    GROUP BY order_id
)
SELECT c.customer_id, SUM(oa.amount) AS total_amount
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
JOIN order_amount oa ON oa.order_id = o.order_id
GROUP BY c.customer_id;
```

## 실전 앵커: 조인 키 인덱스 전략

조인 성능은 키 컬럼 인덱스 설계와 거의 직결됩니다.

```sql
CREATE INDEX idx_orders_customer_id ON orders (customer_id);
CREATE INDEX idx_order_items_order_id ON order_items (order_id);
```

`EXPLAIN`에서 `Hash Join`과 `Nested Loop` 중 무엇이 선택되는지를 보며, 데이터 크기와 선택도에 맞게 키 인덱스를 조정합니다.

## 실전 앵커: LEFT JOIN 필터 위치

초급자가 자주 놓치는 포인트는 필터를 `ON`에 둘지 `WHERE`에 둘지입니다.

```sql
-- LEFT JOIN 의미를 유지
SELECT c.customer_id, o.order_id
FROM customers c
LEFT JOIN orders o
  ON o.customer_id = c.customer_id
 AND o.status = 'paid';
```

같은 조건을 `WHERE o.status = 'paid'`로 옮기면 사실상 INNER JOIN으로 바뀔 수 있습니다.


## 심화 실습 시나리오: 쿼리 품질을 수치로 검증하기

문장 길이가 길어질수록 SQL 품질은 느낌이 아니라 **측정 가능한 기준**으로 관리해야 합니다. 아래 절차는 어떤 주제의 SQL이든 그대로 적용할 수 있는 공통 루틴입니다.

1. 입력 데이터 범위(기간, 상태, 대상 테넌트)를 명시합니다.
2. 같은 조건으로 `COUNT(*)`를 먼저 실행해 모수 행 수를 기록합니다.
3. 본 쿼리를 실행하고 결과 행 수와 합계 지표를 기록합니다.
4. `EXPLAIN (ANALYZE, BUFFERS)`를 실행해 병목 노드를 확인합니다.
5. 인덱스/조건식을 조정한 뒤 2~4를 다시 반복합니다.

```sql
-- 1) 모수 확인
SELECT COUNT(*) AS base_rows
FROM orders
WHERE ordered_at >= DATE '2026-01-01'
  AND ordered_at <  DATE '2026-02-01';

-- 2) 본 쿼리(예시)
SELECT
    customer_id,
    COUNT(*) AS order_count,
    SUM(total_amount) AS revenue
FROM orders
WHERE ordered_at >= DATE '2026-01-01'
  AND ordered_at <  DATE '2026-02-01'
GROUP BY customer_id
ORDER BY revenue DESC
LIMIT 20;

-- 3) 계획 확인
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    customer_id,
    COUNT(*) AS order_count,
    SUM(total_amount) AS revenue
FROM orders
WHERE ordered_at >= DATE '2026-01-01'
  AND ordered_at <  DATE '2026-02-01'
GROUP BY customer_id;
```

이 과정을 습관화하면 "왜 느린지"를 추측하지 않고 설명할 수 있습니다. 특히 팀 협업에서는 성능 이슈를 재현 가능한 단위로 공유할 수 있다는 점이 중요합니다.

## 심화 실습 시나리오: 조인·서브쿼리·CTE 선택 비교

아래 세 방식은 결과가 같아 보이지만, 데이터 크기와 통계 상태에 따라 실행 계획이 크게 달라질 수 있습니다.

```sql
-- A. 직접 조인
SELECT c.customer_id, SUM(o.total_amount) AS revenue
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
WHERE o.status = 'paid'
GROUP BY c.customer_id;
```

```sql
-- B. 서브쿼리
SELECT c.customer_id, x.revenue
FROM customers c
JOIN (
    SELECT customer_id, SUM(total_amount) AS revenue
    FROM orders
    WHERE status = 'paid'
    GROUP BY customer_id
) x ON x.customer_id = c.customer_id;
```

```sql
-- C. CTE
WITH paid_orders AS (
    SELECT customer_id, total_amount
    FROM orders
    WHERE status = 'paid'
),
revenue_by_customer AS (
    SELECT customer_id, SUM(total_amount) AS revenue
    FROM paid_orders
    GROUP BY customer_id
)
SELECT c.customer_id, r.revenue
FROM customers c
JOIN revenue_by_customer r ON r.customer_id = c.customer_id;
```

실무에서 권장하는 방법은 "문법 취향"이 아니라 "검증 가능성"으로 고르는 것입니다. 변경이 자주 일어나는 쿼리는 CTE가 리뷰와 테스트에 유리하고, 단발성 쿼리는 인라인 구조가 간결할 수 있습니다.

## 심화 실습 시나리오: 인덱스 전략과 유지비용

인덱스는 조회 성능을 높이지만 쓰기 비용을 늘립니다. 그래서 읽기/쓰기 비율을 기준으로 설계해야 합니다.

```sql
-- 조회 패턴에 맞춘 합성 인덱스
CREATE INDEX idx_orders_customer_status_created
    ON orders (customer_id, status, created_at DESC);

-- 자주 쓰는 상태값만 가볍게 다루는 부분 인덱스
CREATE INDEX idx_orders_paid_created
    ON orders (created_at DESC)
WHERE status = 'paid';
```

인덱스를 추가한 뒤에는 반드시 아래를 확인합니다.

- `INSERT`/`UPDATE` TPS가 과도하게 떨어지지 않는가
- VACUUM/ANALYZE 주기가 비정상적으로 늘어나지 않는가
- 실제 주요 쿼리에서 `Index Scan` 또는 `Bitmap Index Scan`으로 전환되었는가

인덱스는 "있으면 좋은 옵션"이 아니라 **운영 비용이 있는 구조물**입니다. 성능 개선 수치와 유지 비용을 같이 기록해야 장기적으로 안정됩니다.

## 심화 실습 시나리오: 트랜잭션 격리 수준 재현 데모

분석 SQL이든 운영 SQL이든 동시성 환경에서는 격리 수준 이해가 필요합니다. 다음은 재현 가능한 기본 데모입니다.

```sql
-- 세션 A
BEGIN;
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
SELECT COUNT(*) FROM inventory WHERE product_id = 10;

-- 세션 B
BEGIN;
UPDATE inventory SET quantity = quantity - 1 WHERE product_id = 10;
COMMIT;

-- 세션 A에서 다시 실행
SELECT COUNT(*) FROM inventory WHERE product_id = 10;
COMMIT;
```

`READ COMMITTED`에서는 같은 트랜잭션 안에서도 두 번째 조회가 다른 스냅샷을 볼 수 있습니다. 반면 `REPEATABLE READ`로 바꾸면 시작 시점 스냅샷이 유지됩니다.

```sql
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT SUM(total_amount) FROM orders WHERE status = 'paid';
-- 다른 세션의 커밋 이후에도 동일 스냅샷 유지
SELECT SUM(total_amount) FROM orders WHERE status = 'paid';
COMMIT;
```

배치 지표 계산에서는 이 차이가 그대로 숫자 불일치로 나타납니다. 따라서 격리 수준을 문서화하고, 배치 쿼리에서 명시적으로 설정하는 것이 안전합니다.

## 심화 실습 시나리오: 리뷰 체크리스트를 쿼리 옆에 남기기

SQL 리뷰를 사람 기억에 의존하면 시간이 지나면서 기준이 흔들립니다. 아래 항목을 PR 본문이나 문서에 고정하면 품질 편차를 줄일 수 있습니다.

- 질문의 비즈니스 정의가 SQL 조건으로 정확히 번역되었는가
- 키 유일성(기본키/대체키)이 조인 경로에서 유지되는가
- 기간 조건이 반열린 구간으로 작성되어 경계 오류가 없는가
- `NULL` 처리 규칙이 명시되어 있는가
- 결과 검증용 샘플 출력(행 수, 합계, 상위 N)이 첨부되었는가

이 기준은 학습용 글에서도 그대로 유효합니다. SQL은 결국 데이터와 의사결정을 연결하는 도구이기 때문에, 쿼리 자체보다 **검증 가능한 사고 과정**을 남기는 습관이 더 오래 갑니다.


## 추가 실습 메모: 운영에서 바로 쓰는 검증 질문

아래 질문 네 가지를 기준으로 쿼리를 다시 읽어 보면, 단순히 동작하는 SQL과 운영에 견디는 SQL을 구분할 수 있습니다.

- 이 쿼리는 같은 날 다시 실행해도 같은 결과를 재현할 수 있는가
- 조건절이 인덱스를 활용할 수 있는 형태로 작성되었는가
- 조인 이후 행 수가 의도대로 증가 또는 유지되는가
- 실행 계획에서 가장 비싼 노드가 무엇인지 설명할 수 있는가

짧은 쿼리라도 이 질문을 통과하면, 장애 대응과 지표 신뢰도에서 차이가 크게 납니다.

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

- [book-examples/sql-101 (ko)](https://github.com/yeongseon-books/book-examples/tree/main/sql-101/ko)

- [PostgreSQL — Joins](https://www.postgresql.org/docs/current/tutorial-join.html)
- [SQLBolt — Multi-table queries with JOIN](https://sqlbolt.com/lesson/select_queries_with_joins)
- [Mode — JOIN](https://mode.com/sql-tutorial/sql-joins/)
- [Use The Index, Luke — Joins](https://use-the-index-luke.com/sql/join)

Tags: SQL, Database, Postgres, Analytics
