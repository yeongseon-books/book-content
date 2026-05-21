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

이 글은 SQL 101 시리즈의 여섯 번째 글입니다. 여기서는 서브쿼리와 CTE를 사용해 복잡한 질문을 단계로 나누고, 읽을 수 있는 SQL로 바꾸는 방법을 설명합니다.

실전 SQL은 한 줄로 끝나지 않는 경우가 많습니다. 사용자별 주문 합계를 먼저 만들고, 그중 큰 금액만 골라 다시 사용자 정보와 붙이는 식으로 질문이 겹겹이 쌓입니다. 이때 한 문장 안에 모든 로직을 밀어 넣으면 읽는 사람도, 나중에 고치는 사람도 곧 길을 잃습니다.


![SQL 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/sql-101/06/06-01-subquery-layering-flow.ko.png)
*SQL 101 6장 흐름 개요*
> 서브쿼리와 CTE의 핵심은 문법 자체가 아니라, 큰 질문을 작은 단계로 나누어 각 단계의 결과가 명확하고 검증 가능하도록 설계하는 데 있습니다.

## 먼저 던지는 질문

- 서브쿼리는 언제 쓰고, CTE는 언제 더 나을까요?
- 스칼라 서브쿼리와 인라인 뷰는 무엇이 다를까요?
- `IN`과 `EXISTS`는 어떤 상황에서 차이가 날까요?

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

## 구체화 뷰(Materialized View)

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


## 실전 앵커: 서브쿼리와 CTE를 고르는 기준

둘 다 같은 결과를 만들 수 있지만, 실무에서는 "재사용 범위"와 "리뷰 난이도"로 선택하는 편이 좋습니다.

- 한 번만 쓰고 의미가 짧으면 인라인 서브쿼리
- 여러 단계에서 재사용하면 CTE
- 디버깅이 필요하면 단계별 CTE

```sql
WITH paid_orders AS (
    SELECT *
    FROM orders
    WHERE status = 'paid'
),
customer_revenue AS (
    SELECT customer_id, SUM(total_amount) AS revenue
    FROM paid_orders
    GROUP BY customer_id
)
SELECT *
FROM customer_revenue
WHERE revenue >= 100000;
```

## 실전 앵커: `IN` 대 `EXISTS`를 실행 계획으로 비교

```sql
-- IN
SELECT c.customer_id
FROM customers c
WHERE c.customer_id IN (
    SELECT o.customer_id
    FROM orders o
    WHERE o.status = 'paid'
);

-- EXISTS
SELECT c.customer_id
FROM customers c
WHERE EXISTS (
    SELECT 1
    FROM orders o
    WHERE o.customer_id = c.customer_id
      AND o.status = 'paid'
);
```

카디널리티가 큰 환경에서는 `EXISTS`가 조기 종료 특성 덕분에 더 유리한 경우가 많습니다. 결국 정답은 `EXPLAIN ANALYZE`로 확인해야 합니다.

## 실전 앵커: 상관 서브쿼리 대체 전략

상관 서브쿼리는 읽기 쉽지만 행마다 반복 실행될 수 있습니다.

```sql
-- 상관 서브쿼리
SELECT o.order_id,
       (SELECT SUM(oi.quantity * oi.unit_price)
        FROM order_items oi
        WHERE oi.order_id = o.order_id) AS amount
FROM orders o;
```

데이터가 커지면 아래처럼 미리 집계해 JOIN하는 구조가 더 안정적입니다.

```sql
WITH item_sum AS (
    SELECT order_id, SUM(quantity * unit_price) AS amount
    FROM order_items
    GROUP BY order_id
)
SELECT o.order_id, i.amount
FROM orders o
LEFT JOIN item_sum i ON i.order_id = o.order_id;
```

## 실전 앵커: CTE 디버깅 루틴

복잡한 분석 SQL은 최종 결과만 보지 말고 CTE를 하나씩 단독 실행해 행 수를 확인합니다. 특히 각 단계에서 기본 키 유일성이 깨지는지 확인하면, 뒤쪽 JOIN 오류를 초기에 발견할 수 있습니다.


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

- [book-examples/sql-101 (ko)](https://github.com/yeongseon-books/book-examples/tree/main/sql-101/ko)

- [PostgreSQL — Subqueries](https://www.postgresql.org/docs/current/functions-subquery.html)
- [PostgreSQL — WITH Queries (CTE)](https://www.postgresql.org/docs/current/queries-with.html)
- [Mode — Subqueries](https://mode.com/sql-tutorial/sql-sub-queries/)
- [Use The Index, Luke — IN vs EXISTS](https://use-the-index-luke.com/sql/where-clause/null/not-in)

Tags: SQL, Database, Postgres, Analytics
