---
series: sql-101
episode: 10
title: "SQL 101 (10/10): 실전 분석 SQL"
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
  - Analytics
  - Cohort
  - Funnel
  - Retention
seo_description: DAU, 코호트, 퍼널, 유지율, 그룹별 Top-N까지 실전 분석 SQL 패턴을 한 번에 정리합니다
last_reviewed: '2026-05-15'
---

# SQL 101 (10/10): 실전 분석 SQL

이 글은 SQL 101 시리즈의 마지막 글입니다. 여기서는 일별 활성 사용자, 코호트 유지율, 퍼널, 그룹별 Top-N처럼 실무에서 자주 만나는 분석 SQL의 기본 구조를 정리합니다.

시리즈 앞부분에서 배운 `SELECT`, `WHERE`, `JOIN`, `GROUP BY`, 서브쿼리, 윈도 함수는 각각 따로 존재하는 기능이 아닙니다. 실제 분석 업무에서는 이 도구들이 한 쿼리 안에서 층층이 결합됩니다. 그래서 시리즈 마지막에서는 문법별 설명보다, 자주 반복되는 분석 패턴을 한 번에 보는 편이 더 도움이 됩니다.

## 먼저 던지는 질문

- DAU, WAU, MAU 같은 활성 사용자 지표는 어떤 모양으로 작성할까요?
- 코호트와 유지율은 어떤 단계로 계산할까요?
- 퍼널 분석은 어떻게 한 쿼리 안에 정리할 수 있을까요?

## 큰 그림

![SQL 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/sql-101/10/10-01-analytics-query-layering-flow.ko.png)

*SQL 101 10장 흐름 개요*

이 그림에서는 SELECT, WHERE, JOIN, GROUP BY, 윈도 함수가 함께 어떻게 복잡한 분석 쿼리를 만드는지 봅니다. 실전 쿼리는 앞의 개념들을 조합하여 비즈니스 질문에 답하는 도구입니다.

> 실전 분석 SQL의 핵심은 개별 기능을 외우는 것이 아니라, 여러 기능을 조합하여 복잡한 질문을 명확하고 유지보수 가능한 작은 단계들로 분해하는 데 있습니다.

## 왜 중요한가

현업에서 받는 분석 요청의 상당수는 완전히 새로운 문제가 아닙니다. 활성 사용자, 유지율, 전환율, 상위 매출 상품처럼 이미 자주 등장한 패턴의 변형인 경우가 많습니다. 이 패턴을 알고 있으면 요청이 들어왔을 때 처음부터 빈 화면에서 시작하지 않아도 됩니다.

또 좋은 분석 SQL은 개인의 임시 스크립트로 끝나지 않고 팀의 자산이 됩니다. 정의가 명확하고 재사용 가능한 쿼리는 이후 대시보드, 모델링, 리뷰 문화의 기반이 됩니다.

## 분석 쿼리 적층 흐름

대부분의 분석 SQL은 원본 이벤트를 정리하고, 집계하고, 필요하면 윈도 함수로 후처리한 뒤 최종 보고서 형태로 만듭니다. 중요한 점은 각 단계를 명확히 구분하는 것입니다.

## 핵심 개념 정리

### 활성 사용자 지표는 정의부터 맞춰야 한다

DAU, WAU, MAU는 단순히 `COUNT(DISTINCT user_id)`만 쓰면 끝나는 문제가 아닙니다. 어떤 이벤트를 활동으로 볼지, 어느 시간대를 기준으로 날짜를 자를지 먼저 합의해야 합니다.

### 코호트는 같은 출발점을 가진 사용자 묶음이다

같은 가입일, 같은 첫 결제일처럼 공통 기준으로 사용자를 묶고, 이후 날짜별로 얼마나 다시 활동했는지를 계산하면 유지율이 나옵니다. 정의가 불명확하면 숫자는 쉽게 엇갈립니다.

### 퍼널은 단계별 전환을 보는 구조다

조회, 장바구니, 결제처럼 단계가 분명한 흐름에서는 각 단계별 사용자 수와 전환율을 계산합니다. 이때 시간 순서를 보장할지 여부가 분석 품질에 큰 영향을 줍니다.

### 그룹별 Top-N은 윈도 함수가 가장 직관적이다

상품별 상위 3건, 국가별 상위 5명처럼 그룹 안에서 순위를 매겨야 하는 문제는 `ROW_NUMBER`나 `RANK`가 잘 맞습니다.

## 쿼리 최적화 체크리스트

느린 쿼리를 개선하기 전에 먼저 확인할 항목을 체계적으로 정리하면 개선 방향을 빠르게 잡을 수 있습니다.

| 항목 | 확인 방법 | 개선 방향 |
| --- | --- | --- |
| 인덱스 확인 | `EXPLAIN` 결과에 Index Scan이 나오는가? | 조건에 맞는 열에 인덱스 추가 |
| 풀스캔 제거 | Seq Scan이 크고 비용이 높은가? | WHERE 조건 강화, 인덱스 추가 |
| 조인 순서 | 작은 테이블을 먼저 필터링하는가? | 조인 순서 재배치, CTE로 중간 결과 축소 |
| 서브쿼리 비용 | 상관 서브쿼리가 loops 높게 반복되는가? | JOIN으로 변환, CTE로 한 번만 계산 |
| 집계 성능 | HashAggregate가 메모리 초과하는가? | work_mem 조정, GROUP BY 열 축소 |
| 정렬 비용 | Sort가 크고 디스크 사용하는가? | 인덱스로 정렬 대체, LIMIT 추가 |

실무에서는 이 순서대로 하나씩 확인하면서 가장 큰 병목을 먼저 해결하는 편이 효과적입니다. 모든 항목을 동시에 개선하려 하면 오히려 미그러질 수 있습니다.

## Slow Query 개선 Before/After

다음은 실제 느린 쿼리를 개선하는 예시입니다.

### Before: 느린 쿼리

```sql
SELECT u.name, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at >= '2025-01-01'
GROUP BY u.id, u.name
ORDER BY order_count DESC;
```

**EXPLAIN ANALYZE 결과:**

```text
Sort  (cost=3500.00..3550.00 rows=20000 width=40) (actual time=125.456..126.789 rows=20000 loops=1)
  Sort Key: (count(o.id)) DESC
  ->  HashAggregate  (cost=2800.00..2900.00 rows=20000 width=40) (actual time=98.123..102.456 rows=20000 loops=1)
        Group Key: u.id, u.name
        ->  Hash Left Join  (cost=1500.00..2600.00 rows=80000 width=36) (actual time=23.456..85.678 rows=80000 loops=1)
              Hash Cond: (u.id = o.user_id)
              ->  Seq Scan on users u  (cost=0.00..850.00 rows=20000 width=32) (actual time=0.023..15.678 rows=20000 loops=1)
                    Filter: (created_at >= '2025-01-01')
                    Rows Removed by Filter: 30000
              ->  Hash  (cost=1000.00..1000.00 rows=80000 width=8) (actual time=23.123..23.123 rows=80000 loops=1)
Planning Time: 1.234 ms
Execution Time: 127.890 ms
```

문제점:

- `users` 테이블에 Seq Scan이 발생하며 30000행을 필터링으로 제거
- `created_at` 조건을 먼저 걸러낼 인덱스가 없음
- 전체 실행 시간 127ms

### After: 인덱스 추가 후

```sql
-- 인덱스 추가
CREATE INDEX idx_users_created_at ON users (created_at);

-- 동일한 쿼리 재실행
EXPLAIN ANALYZE
SELECT u.name, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at >= '2025-01-01'
GROUP BY u.id, u.name
ORDER BY order_count DESC;
```

**EXPLAIN ANALYZE 결과:**

```text
Sort  (cost=1800.00..1850.00 rows=20000 width=40) (actual time=42.123..43.456 rows=20000 loops=1)
  Sort Key: (count(o.id)) DESC
  ->  HashAggregate  (cost=1200.00..1300.00 rows=20000 width=40) (actual time=35.678..39.012 rows=20000 loops=1)
        Group Key: u.id, u.name
        ->  Hash Left Join  (cost=600.00..1000.00 rows=80000 width=36) (actual time=8.123..28.456 rows=80000 loops=1)
              Hash Cond: (u.id = o.user_id)
              ->  Index Scan using idx_users_created_at on users u  (cost=0.29..250.00 rows=20000 width=32) (actual time=0.012..3.456 rows=20000 loops=1)
                    Index Cond: (created_at >= '2025-01-01')
              ->  Hash  (cost=1000.00..1000.00 rows=80000 width=8) (actual time=8.012..8.012 rows=80000 loops=1)
Planning Time: 0.890 ms
Execution Time: 44.567 ms
```

개선 결과:

- Seq Scan이 Index Scan으로 변경
- Rows Removed by Filter가 사라짐 (인덱스로 바로 필터링)
- 실행 시간 127ms → 44ms로 65% 감소

인덱스 하나로 큰 효과를 얻을 수 있지만, 모든 쿼리가 이렇게 단순하지는 않습니다. 조인 순서, 서브쿼리, 집계 방식도 함께 검토해야 할 때가 많습니다.
## 다섯 가지 실전 패턴

### 1단계 — 일별 활성 사용자

```sql
SELECT event_at::date AS day, COUNT(DISTINCT user_id) AS dau
FROM events
GROUP BY day
ORDER BY day;
```

가장 기본적인 분석 쿼리입니다. 특정 날짜에 활동한 고유 사용자 수를 계산합니다.

### 2단계 — 코호트 유지율의 뼈대

```sql
WITH cohort AS (
    SELECT user_id, MIN(event_at)::date AS cohort_day FROM events GROUP BY user_id
),
activity AS (
    SELECT e.user_id, c.cohort_day,
        (e.event_at::date - c.cohort_day) AS day_n
    FROM events e JOIN cohort c USING (user_id)
)
SELECT cohort_day, day_n, COUNT(DISTINCT user_id) AS users
FROM activity
GROUP BY cohort_day, day_n
ORDER BY cohort_day, day_n;
```

먼저 각 사용자의 출발일을 만들고, 이후 활동일까지의 차이를 계산한 뒤 코호트 날짜와 경과 일수별로 집계합니다.

### 3단계 — 퍼널 수치 한 번에 보기

```sql
SELECT
    COUNT(DISTINCT user_id) FILTER (WHERE step = 'view')   AS s1_view,
    COUNT(DISTINCT user_id) FILTER (WHERE step = 'cart')   AS s2_cart,
    COUNT(DISTINCT user_id) FILTER (WHERE step = 'pay')    AS s3_pay
FROM events;
```

**Expected output:**

| s1_view | s2_cart | s3_pay |
| --- | --- | --- |
| 1200 | 420 | 180 |

한 쿼리 안에서 단계별 사용자 수를 나란히 놓는 기본 패턴입니다. 이후 이 값을 바탕으로 전환율을 계산할 수 있습니다.

### 4단계 — 그룹별 상위 N건 찾기

```sql
WITH ranked AS (
    SELECT product_id, total,
        ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY total DESC) AS rk
    FROM orders
)
SELECT * FROM ranked WHERE rk <= 3;
```

상품별로 주문 금액 상위 3건만 남기는 예시입니다. 윈도 함수를 실전에서 자주 쓰는 대표 패턴입니다.

### 5단계 — 전월 대비 성장률 계산하기

```sql
WITH monthly AS (
    SELECT DATE_TRUNC('month', day) AS month, SUM(revenue) AS rev
    FROM daily_revenue GROUP BY month
)
SELECT month, rev,
    rev - LAG(rev) OVER (ORDER BY month) AS diff,
    (rev - LAG(rev) OVER (ORDER BY month)) * 100.0
        / NULLIF(LAG(rev) OVER (ORDER BY month), 0) AS mom_pct
FROM monthly;
```

## 지표를 믿기 전에 먼저 확인할 점

분석 SQL은 실행만 됐다고 끝나지 않습니다. 숫자를 바로 공유하기 전에 아래 항목을 먼저 점검하는 편이 안전합니다.

- **정의를 먼저 맞췄는가**: 활성 사용자, 코호트 시작일, 퍼널 단계 정의가 문서와 같은지 확인합니다.
- **중간 단계 행 수가 예상과 맞는가**: CTE마다 행 수가 어떻게 줄거나 늘어나는지 확인하면 논리 오류를 빨리 찾을 수 있습니다.
- **시간대 기준이 분명한가**: 일별·월별 지표는 시간대 하나만 달라도 결과가 흔들릴 수 있습니다.

## 실전 분석에서 자주 보는 점검표

| 증상 | 먼저 볼 것 | 자주 하는 대응 |
| --- | --- | --- |
| DAU가 예상보다 낮다 | 활동 이벤트 정의와 날짜 절단 기준 | 정의와 `DATE_TRUNC`, 시간대 처리 재확인 |
| 퍼널 전환율이 지나치게 높다 | 단계가 시간 순서대로 계산됐는지 | 단계 간 시간 조건을 명시 |
| 유지율이 갑자기 흔들린다 | 코호트 정의와 중복 제거 방식 | 코호트 CTE와 집계 기준 재검토 |

월별 매출을 먼저 만들고, 직전 월과의 차이와 성장률을 계산합니다. `NULLIF`를 써서 0으로 나누는 문제를 피하는 점도 중요합니다.

## 이 코드에서 먼저 봐야 할 점

- 활성 사용자 지표는 대개 `COUNT(DISTINCT user_id)`에서 시작합니다.
- 퍼널은 `FILTER (WHERE ...)`를 쓰면 한 줄에 구조가 잘 드러납니다.
- 성장률 계산에서는 `NULLIF`로 0 나눗셈을 막는 습관이 필요합니다.

## 실무에서 자주 헷갈리는 지점

### 활성 사용자의 정의가 팀마다 다를 수 있다

로그인만 활동으로 볼지, 조회 이벤트도 포함할지에 따라 숫자가 달라집니다. 쿼리보다 먼저 정의를 문서화해야 합니다.

### 시간대 처리를 빼먹으면 날짜가 어긋난다

UTC 기준 로그를 로컬 시간대 기준 대시보드에 바로 쓰면 날짜 경계가 밀릴 수 있습니다. 일별 지표일수록 시간대 기준을 분명히 해야 합니다.

### 퍼널은 개수만 세면 끝나지 않는다

단계별 수를 세는 것과, 실제로 사용자가 그 단계를 시간 순서대로 밟았는지 확인하는 것은 다른 문제입니다. 단순 퍼널에서 끝낼지, 시간 순서를 포함한 엄격한 퍼널로 갈지 목적을 먼저 정해야 합니다.

### 분석 쿼리를 몇 개의 CTE로 나눠야 할까

분석 쿼리가 복잡할수록 CTE 단계가 늘어나지만, 매 단계마다 인라인 확장되면 플래너가 최적화하기 어려워지는 경우도 있습니다. CTE를 너무 많이 쓰는 대신, 의미 있는 단계마다 하나씩 만들고 EXPLAIN으로 확인하는 편이 안전합니다.
### 코호트 기준이 모호하면 유지율이 흔들린다

가입일 기준인지, 첫 결제일 기준인지, 첫 핵심 행동 기준인지에 따라 완전히 다른 보고서가 됩니다. 숫자보다 정의가 먼저입니다.

## 체크리스트

- [ ] DAU를 기본 형태로 작성할 수 있다.
- [ ] 코호트와 활동 단계를 CTE로 나눌 수 있다.
- [ ] 퍼널 단계별 사용자 수를 `FILTER`로 집계할 수 있다.
- [ ] 그룹별 Top-N을 윈도 함수로 구할 수 있다.
- [ ] 시간대와 지표 정의를 먼저 맞춰야 한다는 점을 이해하고 있다.

## 정리

실전 분석 SQL은 새로운 문법의 집합이 아니라, 이미 배운 도구를 여러 층으로 결합한 결과입니다. 이벤트를 정리하고, 집계하고, 윈도 함수로 비교하고, 중간 단계를 CTE로 이름 붙이는 흐름이 핵심입니다. 이 구조를 익혀 두면 새로운 분석 요청이 들어와도 훨씬 빠르게 첫 초안을 만들 수 있습니다.

이 글로 SQL 101 시리즈를 마칩니다. 다음 단계에서는 더 깊은 쿼리 계획 읽기, 실제 PostgreSQL 운영, 데이터 웨어하우스 모델링으로 자연스럽게 이어질 수 있습니다.


## 실전 앵커: 서브쿼리 대 CTE 비교 실험

복잡한 분석에서 같은 결과를 내는 두 구조를 직접 비교해 보면, 리뷰/운영 관점에서 어떤 형태가 유지보수에 유리한지 명확해집니다.

```sql
-- 중첩 서브쿼리 방식
SELECT *
FROM (
    SELECT customer_id, DATE(ordered_at) AS d, SUM(total_amount) AS rev
    FROM orders
    WHERE status = 'paid'
    GROUP BY customer_id, DATE(ordered_at)
) t
WHERE rev >= 100000;
```

```sql
-- CTE 방식
WITH paid_orders AS (
    SELECT * FROM orders WHERE status = 'paid'
),
daily_revenue AS (
    SELECT customer_id, DATE(ordered_at) AS d, SUM(total_amount) AS rev
    FROM paid_orders
    GROUP BY customer_id, DATE(ordered_at)
)
SELECT *
FROM daily_revenue
WHERE rev >= 100000;
```

CTE 방식은 단계별 검증이 쉬워 실무 협업에서 더 자주 선택됩니다.

## 실전 앵커: 퍼널 분석과 조인 시각화

퍼널은 조인 순서와 조건을 잘못 잡으면 전환율이 왜곡됩니다.

```text
signup_users
  -> activated_users
      -> paid_users

각 단계는 반드시 같은 사용자 키 기준으로 연결
기간 조건은 단계별 이벤트 시간 기준으로 별도 적용
```

```sql
WITH s AS (
    SELECT DISTINCT user_id FROM events WHERE event_name = 'signup'
), a AS (
    SELECT DISTINCT user_id FROM events WHERE event_name = 'activated'
), p AS (
    SELECT DISTINCT user_id FROM events WHERE event_name = 'paid'
)
SELECT
    (SELECT COUNT(*) FROM s) AS signup_users,
    (SELECT COUNT(*) FROM s JOIN a USING (user_id)) AS activated_users,
    (SELECT COUNT(*) FROM s JOIN a USING (user_id) JOIN p USING (user_id)) AS paid_users;
```

## 실전 앵커: 분석 배치의 격리 수준 데모

지표 배치가 길게 실행될 때는 트랜잭션 격리 수준을 명시해야 결과 일관성을 보장할 수 있습니다.

```sql
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- 코호트 모수 계산
SELECT cohort_month, COUNT(*) FROM cohorts GROUP BY cohort_month;

-- 유지율 계산
SELECT cohort_month, month_n, retained_users
FROM retention_snapshot;

COMMIT;
```

같은 배치 안에서 모수와 분자가 다른 스냅샷을 보지 않게 하는 것이 핵심입니다.

## 실전 앵커: 분석 SQL 검증 체크리스트

- 집계 단위가 문서로 명시되어 있는가
- 분자/분모 정의가 쿼리에서 일관적인가
- 중복 제거 기준(`DISTINCT`)이 근거와 함께 기록되어 있는가
- 재실행 시 동일 결과가 나오는가
- 실행 계획에서 병목 노드가 확인되는가


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

- **DAU, WAU, MAU 같은 활성 사용자 지표는 어떤 모양으로 작성할까요?**
  - 복잡한 쿼리는 한 번에 완성하려 하기보다, CTE로 각 단계를 나누어 검증하면서 진행하는 편이 빠르고 안전합니다.
- **코호트와 유지율은 어떤 단계로 계산할까요?**
  - 쿼리를 짤 때는 먼저 필요한 데이터를 FROM과 WHERE로 정확히 필터링하고, 그 다음 GROUP BY나 윈도로 분석하는 순서를 지키는 것이 중요합니다.
- **퍼널 분석은 어떻게 한 쿼리 안에 정리할 수 있을까요?**
  - 분석 쿼리의 성능과 가독성을 모두 챙기려면, 각 단계에서 몇 개의 행이 남는지 확인하고, 불필요한 열은 일찍 제거하는 습관이 도움됩니다.

<!-- toc:begin -->
## 시리즈 목차

- [SQL 101 (1/10): SQL이란 무엇인가?](./01-what-is-sql.md)
- [SQL 101 (2/10): SELECT 기본](./02-select-basics.md)
- [SQL 101 (3/10): WHERE와 조건](./03-where-and-conditions.md)
- [SQL 101 (4/10): JOIN 이해하기](./04-join.md)
- [SQL 101 (5/10): GROUP BY와 집계 함수](./05-group-by-and-aggregate.md)
- [SQL 101 (6/10): 서브쿼리와 CTE](./06-subquery.md)
- [SQL 101 (7/10): 윈도 함수](./07-window-function.md)
- [SQL 101 (8/10): 데이터를 바꾸는 SQL — INSERT, UPDATE, DELETE](./08-insert-update-delete.md)
- [SQL 101 (9/10): 인덱스와 쿼리 계획](./09-index-and-query-plan.md)
- **실전 분석 SQL (현재 글)**

<!-- toc:end -->

## 참고 자료

- [book-examples/sql-101 (ko)](https://github.com/yeongseon-books/book-examples/tree/main/sql-101/ko)

- [Mode — Advanced SQL](https://mode.com/sql-tutorial/)
- [PostgreSQL — Window Functions](https://www.postgresql.org/docs/current/tutorial-window.html)
- [dbt — Analytics Engineering](https://docs.getdbt.com/)
- [Looker — Block Library](https://cloud.google.com/looker/docs)
- [PostgreSQL — Aggregate Functions](https://www.postgresql.org/docs/current/functions-aggregate.html)

Tags: SQL, Database, Postgres, Analytics
