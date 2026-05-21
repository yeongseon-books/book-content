---
series: sql-101
episode: 7
title: "SQL 101 (7/10): 윈도 함수"
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
  - WindowFunction
  - Analytics
  - Database
  - Query
seo_description: 윈도 함수로 행을 유지한 채 순위, 누적값, 이전 값 비교를 계산하는 방법을 설명합니다
last_reviewed: '2026-05-15'
---

# SQL 101 (7/10): 윈도 함수

이 글은 SQL 101 시리즈의 일곱 번째 글입니다. 여기서는 윈도 함수를 사용해 원본 행을 유지하면서 그룹별 계산 결과를 덧붙이는 방법을 설명합니다.

`GROUP BY`를 배우고 나면 자연스럽게 다음 질문이 나옵니다. 그룹별 합계나 평균은 구할 수 있는데, 원본 행은 그대로 두면서 그 합계나 순위를 옆에 붙일 수는 없을까 하는 질문입니다. 이 지점에서 윈도 함수가 등장합니다.

![SQL 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/sql-101/07/07-01-window-calculation-flow.ko.png)
*SQL 101 7장 흐름 개요*
> 윈도 함수의 핵심은 행 개수를 줄이지 않으면서 전체 데이터의 맥락 속에서 각 행의 위치나 값을 계산한다는 점입니다.

## 먼저 던지는 질문

- `OVER (PARTITION BY ...)`는 무엇을 뜻할까요?
- `ROW_NUMBER`, `RANK`, `DENSE_RANK`는 어떻게 다를까요?
- `LAG`, `LEAD`는 왜 시계열 분석에서 자주 쓰일까요?

## 왜 중요한가

실무 분석에서는 순위, 직전 값 대비 변화량, 누적 합계, 이동 평균이 자주 필요합니다. 이 문제를 `GROUP BY`만으로 해결하려면 중간 집계 결과를 다시 원본과 조인해야 하는 경우가 많습니다. 윈도 함수는 이런 작업을 훨씬 직접적으로 표현하게 해 줍니다.

특히 코호트, 퍼널, 유지율 같은 분석은 시계열과 그룹별 비교를 자주 포함합니다. 윈도 함수는 SQL이 단순 조회 언어를 넘어 분석 언어로 쓰이게 만든 핵심 도구라고 볼 수 있습니다.

## 윈도 계산 흐름

원본 행이 먼저 있고, 그 행들을 어떤 그룹으로 나눌지와 어떤 순서로 볼지를 `OVER (...)` 안에서 정의합니다. 그 위에 순위 함수나 누적 합계 함수를 얹어 계산 열을 추가하는 방식입니다.

## 핵심 개념 정리

### 파티션은 계산을 나누는 기준이다

`PARTITION BY country`라면 국가별로 따로 계산합니다. 파티션을 빼면 전체 테이블이 하나의 그룹처럼 동작합니다.

### 정렬은 순서 의존 함수의 의미를 만든다

`ROW_NUMBER`, `RANK`, `LAG` 같은 함수는 순서가 있어야 의미가 있습니다. `ORDER BY`가 빠지면 무엇이 첫 번째이고 이전 값인지 정의할 수 없습니다.

### 프레임은 현재 행 기준으로 어디까지 볼지 정한다

누적 합계나 이동 평균처럼 범위가 중요한 계산은 프레임을 함께 보는 편이 안전합니다. 기본값에 기대면 데이터베이스별 차이와 해석 혼선이 생길 수 있습니다.

## 다섯 가지 패턴으로 보기

### 1단계 — 행 번호 붙이기

```sql
SELECT id, country,
    ROW_NUMBER() OVER (PARTITION BY country ORDER BY signup_at) AS seq
FROM users;
```

국가별 가입 순서를 각 행에 붙입니다. 원본 행은 그대로 있고, 계산 열만 추가됩니다.

### 2단계 — 순위 매기기

```sql
SELECT product_id, total,
    RANK() OVER (PARTITION BY product_id ORDER BY total DESC) AS rk
FROM orders;
```

상품별로 주문 금액 순위를 계산합니다. 동률이 있을 때 순위가 어떻게 처리되는지 확인하는 것이 중요합니다.

## 트랜잭션 격리 수준

윈도 함수는 단일 쿼리 안에서 동작하지만, 실무에서는 여러 쿼리가 동시에 실행됩니다. 이때 트랜잭션 격리 수준이 결과에 영향을 줄 수 있습니다.

| 격리 수준 | 발생 가능한 현상 | 성능 | 설명 |
| --- | --- | --- | --- |
| Read Uncommitted | Dirty Read, Non-repeatable Read, Phantom Read | 가장 빠름 | 커밋되지 않은 데이터도 읽음 |
| Read Committed | Non-repeatable Read, Phantom Read | 빠름 | 커밋된 데이터만 읽음 (PostgreSQL 기본값) |
| Repeatable Read | Phantom Read | 보통 | 같은 행은 트랜잭션 내내 같은 값 |
| Serializable | 없음 | 가장 느림 | 완전한 직렬화, 동시성 최소 |

PostgreSQL의 기본값은 Read Committed입니다. 대부분의 경우 이 수준으로 충분하지만, 분석 쿼리에서 일관된 스냅샷이 필요하다면 Repeatable Read를 고려할 수 있습니다.

```sql
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT * FROM orders WHERE created_at >= '2026-01-01';
-- 이 트랜잭션 안에서는 동일한 쿼리가 항상 같은 결과를 돌려줍니다
COMMIT;
```

격리 수준을 높일수록 동시성 문제는 줄어들지만, 대신 잠금 경합과 성능 저하가 발생할 수 있습니다. 윈도 함수처럼 집계와 비교를 동시에 수행하는 쿼리는 격리 수준 선택이 결과 일관성에 영향을 줄 수 있으므로, 트랜잭션 범위를 명확히 설계하는 것이 중요합니다.

## BEGIN/COMMIT/ROLLBACK 예제

윈도 함수를 포함한 복잡한 분석 쿼리는 트랜잭션 안에서 실행하는 편이 안전합니다. 중간 단계를 임시 테이블로 만들거나, 여러 단계를 한 번에 검증할 때 특히 유용합니다.

```sql
BEGIN;

-- 임시 테이블 생성
CREATE TEMP TABLE user_rank AS
SELECT user_id, total,
    RANK() OVER (ORDER BY total DESC) AS rk
FROM orders;

-- 중간 결과 검증
SELECT COUNT(*) FROM user_rank WHERE rk <= 10;

-- 결과가 예상과 맞으면 커밋
COMMIT;

-- 또는 문제가 있으면 롤백
-- ROLLBACK;
```

트랜잭션을 사용하면 중간 결과를 확인한 뒤 최종 커밋 여부를 결정할 수 있습니다. 특히 임시 테이블을 만들어 윈도 함수 결과를 재사용하거나, 여러 단계 분석을 안전하게 검증하는 패턴에서 자주 씁니다.

## 데드락

여러 트랜잭션이 동시에 실행될 때, 서로 상대방이 점유한 자원을 기다리며 무한 대기 상태에 빠지는 문제를 데드락이라고 합니다. 윈도 함수 자체는 읽기 전용 계산이므로 데드락을 일으키지 않지만, 집계 결과를 바탕으로 UPDATE나 INSERT를 수행하는 경우 주의가 필요합니다.

### 데드락 시나리오

```sql
-- 트랜잭션 1
BEGIN;
UPDATE orders SET status = 'shipped' WHERE id = 100;
-- 대기: id=200 잠금 요청
UPDATE orders SET status = 'shipped' WHERE id = 200;
COMMIT;

-- 트랜잭션 2 (동시에 실행)
BEGIN;
UPDATE orders SET status = 'shipped' WHERE id = 200;
-- 대기: id=100 잠금 요청
UPDATE orders SET status = 'shipped' WHERE id = 100;
COMMIT;
```

위 상황에서 트랜잭션 1은 id=100을 잠그고 id=200을 기다리고, 트랜잭션 2는 id=200을 잠그고 id=100을 기다립니다. PostgreSQL은 이런 상황을 감지하면 한쪽 트랜잭션을 자동으로 중단시킵니다.

**데드락 회피 방법:**

- 잠금 순서를 일정하게 유지합니다 (예: 항상 id 오름차순으로 UPDATE)
- 트랜잭션 길이를 짧게 유지합니다
- 가능하면 SELECT ... FOR UPDATE로 명시적 잠금을 먼저 획듍합니다
- 윈도 함수 결과를 바탕으로 일괄 업데이트할 때는 순서를 명확히 합니다

윈도 함수로 순위를 매긴 뒤 상위 N개만 업데이트하는 패턴에서는 순위 계산과 업데이트를 분리하고, 업데이트 순서를 일정하게 유지하는 것이 안전합니다.
### 3단계 — 이전 값 읽기

```sql
SELECT user_id, signup_at,
    LAG(signup_at) OVER (PARTITION BY user_id ORDER BY signup_at) AS prev_signup
FROM users;
```

각 사용자 기준으로 직전 가입 시점을 붙입니다. 시계열 비교의 기본 패턴입니다.

### 4단계 — 누적 합계 만들기

```sql
SELECT day, revenue,
    SUM(revenue) OVER (ORDER BY day) AS running_total
FROM daily_revenue;
```

**Expected output:**

| day | revenue | running_total |
| --- | --- | --- |
| 2026-04-01 | 100 | 100 |
| 2026-04-02 | 120 | 220 |
| 2026-04-03 | 90 | 310 |

날짜가 지날수록 매출이 얼마나 누적되는지 보여 줍니다.

### 5단계 — 이동 평균 계산하기

```sql
SELECT day, revenue,
    AVG(revenue) OVER (
        ORDER BY day
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS ma_7
FROM daily_revenue;
```

현재 행을 기준으로 직전 6일과 오늘까지 포함한 7일 평균을 구합니다. 프레임을 직접 적어 두는 습관이 특히 중요합니다.

## 윈도 함수 실전 패턴

윈도 함수를 실무에서 자주 사용하는 패턴을 모아봅니다.

### 패턴 1: 그룹별 상위 N건 추출

```sql
WITH ranked AS (
    SELECT product_id, user_id, total,
        ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY total DESC) AS rk
    FROM orders
)
SELECT * FROM ranked WHERE rk <= 3;
```

상품별로 금액 상위 3건만 가져옵니다.

### 패턴 2: 전월 대비 증감률

```sql
SELECT month,
    revenue,
    LAG(revenue) OVER (ORDER BY month) AS prev_revenue,
    revenue - LAG(revenue) OVER (ORDER BY month) AS diff,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY month)) * 100.0
        / NULLIF(LAG(revenue) OVER (ORDER BY month), 0),
        2
    ) AS growth_pct
FROM monthly_revenue;
```

전월 매출을 가져와서 증감률을 계산합니다. `NULLIF`로 0 나눗셈을 방지합니다.

### 패턴 3: 누적 점유율

```sql
SELECT product_id, revenue,
    SUM(revenue) OVER (ORDER BY revenue DESC) AS running_total,
    ROUND(
        SUM(revenue) OVER (ORDER BY revenue DESC) * 100.0
        / SUM(revenue) OVER (),
        2
    ) AS cumulative_pct
FROM product_revenue;
```

누적 매출이 전체의 몇 퍼센트인지 계산합니다. 파레토 분석에 유용합니다.

### 패턴 4: 행 간 차이 계산

```sql
SELECT day, active_users,
    active_users - LAG(active_users) OVER (ORDER BY day) AS daily_change
FROM daily_active_users;
```

일별 활성 사용자 변화량을 계산합니다.

### 패턴 5: 파티션별 분위수

```sql
SELECT country, user_id, revenue,
    NTILE(4) OVER (PARTITION BY country ORDER BY revenue DESC) AS quartile
FROM user_revenue;
```

국가별로 사용자를 매출 기준 4분위로 나납니다.

윈도 함수는 이처럼 비교, 순위, 비율, 누적 같은 분석을 직관적으로 표현하게 해 줍니다. 패턴을 익히 두면 실무에서 비슷한 문제를 빠르게 풀 수 있습니다.

## 이 코드에서 먼저 봐야 할 점

- `OVER ()`가 비어 있으면 전체 행이 하나의 파티션처럼 계산됩니다.
- 순위와 이전 값 함수는 `ORDER BY`가 있어야 의미가 분명합니다.
- 프레임을 명시하지 않으면 기본 동작을 오해하기 쉽습니다.

### 윈도 함수 결과를 UPDATE에 바로 쓸 수 있을까

윈도 함수는 SELECT에서만 쓸 수 있고, UPDATE나 DELETE의 SET 절에는 직접 쓸 수 없습니다. 대신 CTE나 서브쿼리로 먼저 계산한 뒤 조인하는 패턴을 사용합니다.

```sql
WITH ranked AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY created_at DESC) AS rk
    FROM orders
)
UPDATE orders o
SET is_recent = true
FROM ranked r
WHERE o.id = r.id AND r.rk <= 100;
```

이 패턴은 윈도 함수 결과를 CTE로 만든 뒤, UPDATE 문에서 그 결과를 조인해 사용하는 방식입니다.
## 실무에서 자주 헷갈리는 지점

### `ROW_NUMBER`와 `RANK`는 무엇이 다를까

`ROW_NUMBER`는 동률이 있어도 순서를 끊지 않고 1, 2, 3처럼 번호를 붙입니다. `RANK`는 동률이 있으면 같은 순위를 주고 다음 순위를 건너뜁니다. 같은 순위 정책으로 어떤 보고서를 만들고 싶은지 먼저 정해야 합니다.

### 파티션을 빼먹으면 왜 이상한 숫자가 나올까

사용자별 첫 주문을 찾으려는데 `PARTITION BY user_id`를 빼먹으면 전체 테이블 기준 첫 주문만 남는 식의 오류가 생깁니다. 윈도 함수는 파티션 기준을 분명히 적는 것이 핵심입니다.

### 기본 프레임에 기대면 왜 위험할까

특히 누적 합계와 이동 평균은 프레임이 어디까지인지에 따라 결과가 달라집니다. 쿼리를 읽는 사람이 즉시 이해할 수 있도록 범위를 명시하는 편이 낫습니다.

## 체크리스트

- [ ] `PARTITION BY`가 계산을 어떤 단위로 나누는지 설명할 수 있다.
- [ ] `ROW_NUMBER`와 `RANK`의 차이를 알고 있다.
- [ ] `LAG`와 `LEAD`를 이용해 이전 값과 다음 값을 붙일 수 있다.
- [ ] 누적 합계와 이동 평균의 차이를 이해하고 있다.
- [ ] 프레임을 명시하는 습관이 있다.

## 실전 앵커: 윈도 함수와 집계 함수의 경계

윈도 함수는 행을 유지하면서 계산을 붙이고, 집계 함수는 행을 줄입니다. 이 경계를 명확히 이해하면 분석 SQL이 훨씬 안정됩니다.

```sql
SELECT
    customer_id,
    ordered_at,
    total_amount,
    SUM(total_amount) OVER (
        PARTITION BY customer_id
        ORDER BY ordered_at
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_revenue
FROM orders;
```

## 실전 앵커: 프레임 지정 실수 줄이기

`ORDER BY`만 쓰고 프레임을 생략하면 의도와 다른 결과가 나올 수 있습니다. 특히 중복 정렬 키가 있을 때 `RANGE`와 `ROWS` 차이가 크게 드러납니다.

```sql
-- 명시적으로 ROWS 프레임 지정
AVG(total_amount) OVER (
    PARTITION BY customer_id
    ORDER BY ordered_at, order_id
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
) AS avg_7_orders
```

## 실전 앵커: 트랜잭션 격리 수준 데모

윈도 계산 결과를 리포트로 저장하는 배치에서는 격리 수준 이해가 필요합니다. 아래는 재현 실험용 시나리오입니다.

```sql
-- 세션 A
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT COUNT(*) FROM orders WHERE status = 'paid';
-- 세션 B가 INSERT/COMMIT 후에도
SELECT COUNT(*) FROM orders WHERE status = 'paid';
COMMIT;
```

`READ COMMITTED`에서는 두 번째 조회 결과가 바뀔 수 있고, `REPEATABLE READ`에서는 트랜잭션 시작 시점 스냅샷을 유지합니다. 분석 배치의 일관성을 맞추려면 이 차이를 명시적으로 선택해야 합니다.

## 실전 앵커: 순위 계산과 동률 처리

```sql
SELECT
    DATE(ordered_at) AS d,
    customer_id,
    SUM(total_amount) AS revenue,
    ROW_NUMBER() OVER (PARTITION BY DATE(ordered_at) ORDER BY SUM(total_amount) DESC) AS rn,
    RANK()       OVER (PARTITION BY DATE(ordered_at) ORDER BY SUM(total_amount) DESC) AS rnk,
    DENSE_RANK() OVER (PARTITION BY DATE(ordered_at) ORDER BY SUM(total_amount) DESC) AS drnk
FROM orders
GROUP BY DATE(ordered_at), customer_id;
```

동률 처리 정책(`ROW_NUMBER`, `RANK`, `DENSE_RANK`)을 문서로 남기면 지표 해석 충돌을 줄일 수 있습니다.

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

## 정리

윈도 함수는 행을 줄이지 않고도 그룹별 계산을 붙일 수 있게 해 줍니다. 순위, 변화량, 누적값, 이동 평균 같은 실전 분석 패턴이 모두 여기서 나옵니다. `PARTITION BY`, `ORDER BY`, 프레임의 역할을 분명히 이해하면 훨씬 읽기 좋은 분석 SQL을 만들 수 있습니다.

다음 글에서는 데이터를 읽는 쿼리에서 한 걸음 나아가, 실제로 데이터를 넣고 수정하고 삭제하는 DML을 안전하게 다루는 방법을 보겠습니다.

## 처음 질문으로 돌아가기

- **`OVER (PARTITION BY ...)`는 무엇을 뜻할까요?**
  - 윈도 함수는 GROUP BY처럼 행을 묶지 않고, 각 행에 대해 윈도(범위)를 정의한 후 그 범위 내에서 계산합니다.
- **`ROW_NUMBER`, `RANK`, `DENSE_RANK`는 어떻게 다를까요?**
  - ROW_NUMBER(), RANK(), LAG() 같은 함수는 행의 순서나 이전 값을 알아야 할 때 유용합니다.
- **`LAG`, `LEAD`는 왜 시계열 분석에서 자주 쓰일까요?**
  - 윈도를 정의할 때 PARTITION BY로 그룹을 나누고, ORDER BY로 순서를 정하면, 각 그룹 안에서 계산이 정해집니다.

<!-- toc:begin -->
## 시리즈 목차

- [SQL 101 (1/10): SQL이란 무엇인가?](./01-what-is-sql.md)
- [SQL 101 (2/10): SELECT 기본](./02-select-basics.md)
- [SQL 101 (3/10): WHERE와 조건](./03-where-and-conditions.md)
- [SQL 101 (4/10): JOIN 이해하기](./04-join.md)
- [SQL 101 (5/10): GROUP BY와 집계 함수](./05-group-by-and-aggregate.md)
- [SQL 101 (6/10): 서브쿼리와 CTE](./06-subquery.md)
- **윈도 함수 (현재 글)**
- 데이터를 바꾸는 SQL — INSERT, UPDATE, DELETE (예정)
- 인덱스와 쿼리 계획 (예정)
- 실전 분석 SQL (예정)

<!-- toc:end -->

## 참고 자료

- [book-examples/sql-101 (ko)](https://github.com/yeongseon-books/book-examples/tree/main/sql-101/ko)

- [PostgreSQL — Window Functions](https://www.postgresql.org/docs/current/tutorial-window.html)
- [PostgreSQL — Window Function Reference](https://www.postgresql.org/docs/current/functions-window.html)
- [Mode — Window Functions](https://mode.com/sql-tutorial/sql-window-functions/)
- [Use The Index, Luke — Top-N](https://use-the-index-luke.com/sql/partial-results/top-n-queries)

Tags: SQL, Database, Postgres, Analytics
