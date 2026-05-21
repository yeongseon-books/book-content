---
series: sql-101
episode: 9
title: "SQL 101 (9/10): 인덱스와 쿼리 계획"
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
  - Index
  - QueryPlan
  - Performance
  - Postgres
seo_description: B-tree 인덱스, EXPLAIN 읽기, 인덱스가 건너뛰어지는 이유, 합성 인덱스 설계를 설명합니다
last_reviewed: '2026-05-15'
---

# SQL 101 (9/10): 인덱스와 쿼리 계획

이 글은 SQL 101 시리즈의 아홉 번째 글입니다. 여기서는 인덱스의 기본 원리와 `EXPLAIN`을 읽는 법, 그리고 인덱스가 왜 기대대로 쓰이지 않는지를 설명합니다.

같은 SQL인데 어떤 쿼리는 0.1초 만에 끝나고, 어떤 쿼리는 수십 초가 걸립니다. 이 차이는 대개 운이 아니라 실행 계획에서 나옵니다. 데이터베이스가 어떤 경로로 데이터를 읽기로 결정했는지 이해하지 못하면 튜닝은 추측에 머물기 쉽습니다.

## 먼저 던지는 질문

- B-tree 인덱스는 어떤 생각으로 이해하면 될까요?
- `EXPLAIN`과 `EXPLAIN ANALYZE`는 무엇이 다를까요?
- 인덱스가 있어도 왜 순차 스캔이 선택될까요?

## 큰 그림

![SQL 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/sql-101/09/09-01-plan-selection-flow.ko.png)

*SQL 101 9장 흐름 개요*

이 그림에서는 인덱스가 있을 때와 없을 때 쿼리 실행 계획이 어떻게 달라지는지 봅니다. 인덱스는 조회 속도를 빠르게 하지만, 모든 열에 인덱스를 만들면 쓰기 성능이 나빠집니다.

> 인덱스와 쿼리 계획의 핵심은 실행 계획을 읽고, 의도한 대로 인덱스를 탈 수 있는 쿼리를 짜고, 성능 개선이 정말 필요한 지점에만 인덱스를 만드는 데 있습니다.

## 왜 중요한가

데이터가 작을 때는 웬만한 쿼리도 빨라 보입니다. 하지만 행 수가 늘어나면 작은 조건식 차이가 큰 성능 차이로 바뀝니다. 이 시점부터는 쿼리 문장만 보는 것으로는 부족하고, 데이터베이스가 실제로 어떤 방식으로 읽고 있는지를 확인해야 합니다.

또 인덱스는 읽기를 빠르게 만드는 대신 쓰기 비용을 늘립니다. 많이 만들수록 좋은 것이 아니라, 어떤 조회를 빠르게 만들고 어떤 쓰기 부담을 감수할지 설계하는 문제에 가깝습니다.

## 실행 계획 선택 흐름

사용자가 SQL을 보내면 플래너가 여러 실행 방식을 검토합니다. 그리고 비용 추정을 바탕으로 순차 스캔을 할지, 인덱스 스캔을 할지, 어떤 조인 순서를 택할지 결정합니다. 성능 튜닝은 결국 이 선택을 읽고 이해하는 과정입니다.

## 핵심 개념 정리

### B-tree 인덱스는 가장 흔한 기본 인덱스다

정렬된 구조를 유지하면서 값을 빠르게 찾도록 돕는 인덱스입니다. 동등 비교와 범위 비교에서 특히 자주 쓰입니다.

### 순차 스캔은 무조건 나쁜 것이 아니다

전체 테이블을 읽는 방식이라서 느려 보이지만, 조건 선택도가 낮거나 테이블이 작으면 오히려 합리적인 선택일 수 있습니다. 인덱스가 있다고 항상 인덱스를 타는 것은 아닙니다.

### 선택도는 조건이 얼마나 많이 줄여 주는가를 뜻한다

거의 모든 행이 조건을 통과한다면 인덱스를 타는 이점이 작습니다. 반대로 아주 적은 행만 남긴다면 인덱스 사용 가치가 커집니다.

### 합성 인덱스는 왼쪽부터 읽는다는 감각이 중요하다

예를 들어 `(user_id, created_at)` 인덱스는 보통 `user_id`를 먼저 좁히는 쿼리에 잘 맞습니다. 컬럼 순서는 단순 장식이 아니라 사용 패턴과 직결됩니다.

## 인덱스 유형 비교

인덱스는 B-tree만 있는 것이 아닙니다. 데이터 특성과 조회 패턴에 따라 다른 유형이 더 적합할 수 있습니다.

| 인덱스 유형 | 주 용도 | 장점 | 단점 |
| --- | --- | --- | --- |
| B-tree | 동등/범위 비교, 정렬 | 가장 범용적 | 매우 긴 텍스트는 비효율적 |
| Hash | 동등 비교만 | 조회 매우 빠름 | 범위 검색, 정렬 불가 |
| GIN | 전문 검색, JSON, 배열 | 복합 데이터 검색 | 빌드 비용 높음 |
| GiST | 기하, 범위 검색 | 확장 가능한 프레임워크 | B-tree보다 느림 |

PostgreSQL의 기본 인덱스는 B-tree입니다. 대부분의 조회는 B-tree로 충분하지만, 전문 검색이나 JSON 필드 검색이 필요하면 GIN을 고려해야 합니다.

```sql
-- B-tree (기본)
CREATE INDEX idx_users_email ON users (email);

-- GIN (JSONB 검색)
CREATE INDEX idx_metadata ON logs USING GIN (metadata);

-- Hash (동등 비교 전용)
CREATE INDEX idx_hash ON users USING HASH (email);
```

인덱스 유형은 `USING` 키워드로 명시합니다. 생략하면 B-tree가 기본값입니다.

## CREATE INDEX 예제 + EXPLAIN 출력

인덱스를 만들기 전과 후의 실행 계획을 비교하면 인덱스의 효과를 명확히 확인할 수 있습니다.

### 인덱스 없이

```sql
EXPLAIN SELECT * FROM orders WHERE user_id = 42;
```

**Expected output:**

```text
Seq Scan on orders  (cost=0.00..1850.00 rows=50 width=128)
  Filter: (user_id = 42)
```

전체 테이블을 스캔하며 조건에 맞는 행을 걸러냅니다. 행이 많아지면 비용이 선형적으로 증가합니다.

### 인덱스 추가 후

```sql
CREATE INDEX idx_orders_user_id ON orders (user_id);

EXPLAIN SELECT * FROM orders WHERE user_id = 42;
```

**Expected output:**

```text
Index Scan using idx_orders_user_id on orders  (cost=0.29..12.50 rows=50 width=128)
  Index Cond: (user_id = 42)
```

인덱스를 타면서 `user_id=42` 조건에 맞는 행만 바로 찾습니다. 비용이 1850에서 12.5로 크게 줄었습니다.

## 인덱스를 걸지 말아야 할 때

인덱스는 읽기 성능을 올려 주지만, 모든 열에 무조건 걸면 오히려 해가 될 수 있습니다. 다음 상황에서는 인덱스 추가를 신중히 검토해야 합니다.

### 1. 선택도가 매우 낮을 때

대부분의 행이 조건을 통과하면 인덱스 스캔이 순차 스캔보다 느릴 수 있습니다.

```sql
-- 전체 사용자의 95%가 활성 상태라면
SELECT * FROM users WHERE is_active = true;
-- 인덱스를 타도 거의 모든 행을 읽어야 하므로 효과가 작음
```

### 2. 테이블이 매우 작을 때

행이 몇백 개 이하라면 순차 스캔도 충분히 빠를 수 있습니다. 인덱스 관리 비용이 오히려 부담이 될 수 있습니다.

### 3. 쓰기 빈도가 매우 높을 때

로그 테이블처럼 초당 수천 건씩 INSERT되는 테이블에는 인덱스 갱신 비용이 큰 부담이 됩니다. 조회가 드물다면 인덱스를 최소화하는 편이 낫습니다.

### 4. 열 값의 종류가 매우 적을 때 (Cardinality가 낮을 때)

```sql
-- is_deleted가 true/false 두 가지밖에 없다면
CREATE INDEX idx_is_deleted ON users (is_deleted); -- 효과가 작음
```

값의 종류가 적으면 인덱스로 분류하는 효과가 작습니다. 이런 경우 부분 인덱스를 고려하거나, 인덱스를 아예 만들지 않는 편이 나을 수 있습니다.

**인덱스 계획 체크리스트:**

- [ ] 조회 빈도 > 쓰기 빈도
- [ ] 선택도가 충분히 높음 (조건이 행을 잘 걸러냄)
- [ ] 테이블 크기가 충분히 큼
- [ ] 열의 Cardinality가 충분히 높음

## EXPLAIN ANALYZE 읽는 법

`EXPLAIN`은 계획만 보여 주지만, `EXPLAIN ANALYZE`는 실제로 실행하고 실제 시간과 행 수를 함께 보여 줍니다.

```sql
EXPLAIN ANALYZE
SELECT u.name, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;
```

**Expected output:**

```text
HashAggregate  (cost=2850.00..2950.00 rows=10000 width=40) (actual time=45.123..46.234 rows=10000 loops=1)
  Group Key: u.id, u.name
  ->  Hash Left Join  (cost=1200.00..2700.00 rows=50000 width=36) (actual time=12.345..38.567 rows=50000 loops=1)
        Hash Cond: (u.id = o.user_id)
        ->  Seq Scan on users u  (cost=0.00..450.00 rows=10000 width=32) (actual time=0.012..5.678 rows=10000 loops=1)
        ->  Hash  (cost=850.00..850.00 rows=50000 width=8) (actual time=12.123..12.123 rows=50000 loops=1)
              Buckets: 65536  Batches: 1  Memory Usage: 2048kB
              ->  Seq Scan on orders o  (cost=0.00..850.00 rows=50000 width=8) (actual time=0.034..6.789 rows=50000 loops=1)
Planning Time: 0.456 ms
Execution Time: 46.789 ms
```

### 읽는 순서

1. **가장 들여쓴 노드부터** 읽습니다 (아래에서 위로)
2. **actual time**: 실제 실행 시간 (ms)
3. **rows**: 예상 vs 실제 행 수 비교
4. **loops**: 해당 노드가 몇 번 반복됐는지

### 주의할 지표

- **예상 행 수 vs 실제 행 수**: 크게 차이 나면 통계 정보 갱신 필요
- **loops 값이 큼**: 중첩 루프가 비효율적일 가능성
- **Seq Scan이 긴 시간**: 인덱스 추가 검토
- **Hash Join의 Batches > 1**: 메모리 부족, work_mem 조정 고려

`EXPLAIN ANALYZE`는 실제로 쿼리를 실행하므로, UPDATE/DELETE같은 변경 작업에는 주의해서 사용해야 합니다. 테스트 환경이나 트랜잭션 안에서 실행하는 편이 안전합니다.
## 다섯 단계로 보는 튜닝 흐름

### 1단계 — 계획만 먼저 보기

```sql
EXPLAIN
SELECT * FROM users WHERE email = 'a@b.com';
```

**Expected output:**

```text
Index Scan using idx_users_email on users  (cost=0.28..8.30 rows=1 width=48)
  Index Cond: (email = 'a@b.com'::text)
```

실행하지 않고 계획만 봅니다. 어떤 스캔을 택했는지, 예상 행 수가 얼마인지부터 읽어 보는 출발점입니다.

### 2단계 — 실제 실행까지 보기

```sql
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'a@b.com';
```

실제로 실행한 뒤 실제 시간과 실제 행 수를 보여 줍니다. 운영 환경에서는 실제 실행이므로 더 조심해서 써야 합니다.

### 3단계 — 단일 컬럼 인덱스 추가하기

```sql
CREATE INDEX idx_users_email ON users (email);
```

이메일로 자주 찾는다면 기본적인 출발점이 됩니다.

### 4단계 — 합성 인덱스 설계하기

```sql
CREATE INDEX idx_orders_user_date
ON orders (user_id, created_at DESC);
```

사용자별 최근 주문을 자주 찾는 패턴에 맞춘 예시입니다. 조건과 정렬을 함께 고려한 형태입니다.

### 5단계 — 부분 인덱스 만들기

```sql
CREATE INDEX idx_users_active
ON users (id) WHERE deleted_at IS NULL;
```

## 실행 계획을 볼 때 먼저 확인할 세 가지

`EXPLAIN` 결과를 열었다면 인덱스를 추가하기 전에 먼저 아래 세 질문부터 확인하는 편이 좋습니다.

1. **어떤 스캔이 선택됐는가?** 인덱스를 기대했는데 `Seq Scan`이 보인다면 선택도나 조건식 모양을 먼저 의심해야 합니다.
2. **예상 행 수가 얼마나 되는가?** 예상 행 수와 실제 행 수가 크게 어긋나면 통계 정보나 데이터 분포를 다시 봐야 합니다.
3. **가장 비싼 단계가 어디인가?** 정렬, 해시 집계, 중첩 루프가 병목일 수 있으므로 필터만 보고 끝내면 안 됩니다.

## 자주 만나는 튜닝 점검표

| 증상 | 먼저 볼 것 | 자주 하는 대응 |
| --- | --- | --- |
| 인덱스가 있는데도 `Seq Scan`이 나온다 | 선택도, 함수/형변환 사용 여부 | 조건식을 바꾸거나 인덱스 종류를 다시 설계 |
| 합성 인덱스가 기대만큼 안 듣는다 | 왼쪽 컬럼부터 조건에 쓰였는지 | 조회 패턴에 맞게 컬럼 순서 재설계 |
| `EXPLAIN`은 좋아 보이는데 실제 시간은 길다 | 정렬, 조인, 실제 행 수 | 필터만이 아니라 전체 계획을 다시 점검 |

삭제되지 않은 사용자만 자주 읽는다면, 전체보다 작은 인덱스로도 충분한 경우가 있습니다.

## 이 코드에서 먼저 봐야 할 점

- 합성 인덱스는 컬럼 순서가 매우 중요합니다.
- 부분 인덱스는 조건이 명확할 때 특히 강력합니다.
- `EXPLAIN ANALYZE`는 실제 쿼리를 실행하므로 환경을 가려서 써야 합니다.

## 실무에서 자주 헷갈리는 지점

### 인덱스가 있는데 왜 순차 스캔을 할까

조건이 너무 많은 행을 통과시키면, 인덱스를 타고 다시 테이블을 읽는 비용보다 그냥 전체를 읽는 편이 나을 수 있습니다. 그래서 인덱스 존재 여부만 보지 말고, 조건이 얼마나 결과를 좁히는지도 함께 봐야 합니다.

### 컬럼에 함수를 감싸면 왜 인덱스를 놓치기 쉬울까

`WHERE LOWER(email) = 'x'`처럼 쓰면 일반 인덱스는 바로 활용하기 어렵습니다. 이런 패턴이 자주 필요하다면 함수 인덱스를 고려해야 합니다.

### 합성 인덱스는 왜 순서가 핵심일까

`(user_id, created_at)`와 `(created_at, user_id)`는 서로 다른 인덱스입니다. 어떤 조건이 먼저 들어오는지, 어떤 정렬을 자주 하는지에 따라 효율이 달라집니다.

### 인덱스를 많이 만들면 왜 쓰기가 느려질까

행을 추가하거나 수정할 때마다 관련 인덱스도 함께 갱신해야 합니다. 읽기 최적화만 보고 인덱스를 늘리면 쓰기 부하가 커질 수 있습니다.

## 체크리스트

- [ ] `Seq Scan`과 `Index Scan`의 차이를 설명할 수 있다.
- [ ] `EXPLAIN`과 `EXPLAIN ANALYZE`의 차이를 알고 있다.
- [ ] 합성 인덱스에서 컬럼 순서가 중요하다는 점을 이해하고 있다.
- [ ] 함수와 타입 변환이 인덱스 사용에 영향을 줄 수 있음을 안다.
- [ ] 인덱스가 읽기와 쓰기 사이의 절충이라는 점을 알고 있다.

## 정리

성능 튜닝의 출발점은 인덱스를 많이 만드는 것이 아니라, 실행 계획을 읽는 것입니다. 어떤 쿼리가 왜 순차 스캔을 택했는지, 어떤 조건이 선택도를 높이거나 낮추는지, 합성 인덱스가 어떤 패턴에 맞는지를 이해해야 제대로 된 개선이 가능합니다.

다음 글에서는 시리즈 마지막으로, 지금까지 배운 SELECT, JOIN, GROUP BY, 윈도 함수를 조합해 실전 분석 SQL 패턴을 정리하겠습니다.


## 실전 앵커: 인덱스 설계의 우선순위

인덱스는 많이 만들수록 좋은 자산이 아니라, 쓰기 비용과 저장공간을 같이 소비하는 선택입니다. 그래서 다음 우선순위로 설계하는 편이 안전합니다.

1. 트래픽이 큰 조회 쿼리의 `WHERE` + `ORDER BY`
2. 조인 키
3. 고선택도 조건
4. 나머지는 측정 후 추가

```sql
CREATE INDEX idx_orders_status_created_at
    ON orders (status, created_at DESC);
```

## 실전 앵커: 실행 계획 비교 예시

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id, customer_id, total_amount
FROM orders
WHERE status = 'paid'
  AND created_at >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY created_at DESC
LIMIT 100;
```

인덱스 추가 전후에 아래 항목을 비교합니다.

- 실제 실행 시간(`actual time`)
- 읽은 블록 수(`shared read blocks`)
- 반환 행 수 대비 스캔 행 수

이 세 항목이 개선되지 않으면 인덱스가 실질적으로 도움이 되지 않았을 가능성이 높습니다.

## 실전 앵커: 부분 인덱스 전략

상태값이 소수인 경우 부분 인덱스가 매우 유용합니다.

```sql
CREATE INDEX idx_orders_paid_recent
    ON orders (created_at DESC)
WHERE status = 'paid';
```

`status='paid'` 쿼리만 빠르게 만들고, 전체 인덱스보다 크기를 줄여 유지보수 비용도 낮출 수 있습니다.

## 실전 앵커: 튜닝 기록 템플릿

성능 작업은 결과만 기억하면 재현이 어렵습니다. 아래 템플릿을 남기면 팀 지식이 축적됩니다.

- 대상 쿼리와 호출 빈도
- 개선 전 `EXPLAIN ANALYZE`
- 적용한 인덱스/쿼리 변경
- 개선 후 `EXPLAIN ANALYZE`
- 쓰기 성능 영향 여부


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

- **B-tree 인덱스는 어떤 생각으로 이해하면 될까요?**
  - 인덱스는 특정 열의 값으로 행을 빠르게 찾을 수 있게 해 줍니다. 하지만 모든 열의 모든 조합에 인덱스를 만들 수는 없습니다.
- **`EXPLAIN`과 `EXPLAIN ANALYZE`는 무엇이 다를까요?**
  - EXPLAIN으로 쿼리 실행 계획을 보면, 데이터베이스가 인덱스를 타는지, 아니면 전체 테이블을 읽는지 알 수 있습니다.
- **인덱스가 있어도 왜 순차 스캔이 선택될까요?**
  - 성능 개선은 무조건 인덱스를 추가하는 것이 아니라, 느린 쿼리를 먼저 식별하고, 그 쿼리가 정말 개선 가치가 있을 때 단계적으로 시도해야 합니다.

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
- **인덱스와 쿼리 계획 (현재 글)**
- 실전 분석 SQL (예정)

<!-- toc:end -->

## 참고 자료

- [book-examples/sql-101 (ko)](https://github.com/yeongseon-books/book-examples/tree/main/sql-101/ko)

- [PostgreSQL — Indexes](https://www.postgresql.org/docs/current/indexes.html)
- [PostgreSQL — EXPLAIN](https://www.postgresql.org/docs/current/sql-explain.html)
- [Use The Index, Luke](https://use-the-index-luke.com/)
- [PostgreSQL — Partial Indexes](https://www.postgresql.org/docs/current/indexes-partial.html)
- [PostgreSQL — Planner Statistics](https://www.postgresql.org/docs/current/planner-stats.html)

Tags: SQL, Database, Postgres, Analytics
