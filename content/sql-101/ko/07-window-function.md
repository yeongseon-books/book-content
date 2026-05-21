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

`GROUP BY`를 배우고 나면 자연스럽게 다음 질문이 나옵니다. 그룹별 합계나 평균은 구할 수 있는데, 원본 행은 그대로 두면서 그 합계나 순위를 옆에 붙일 수는 없을까 하는 질문입니다. 이 지점에서 윈도 함수가 등장합니다.

이 글은 SQL 101 시리즈의 일곱 번째 글입니다. 여기서는 윈도 함수를 사용해 원본 행을 유지하면서 그룹별 계산 결과를 덧붙이는 방법을 설명합니다.

## 먼저 던지는 질문

- `OVER (PARTITION BY ...)`는 무엇을 뜻할까요?
- `ROW_NUMBER`, `RANK`, `DENSE_RANK`는 어떻게 다를까요?
- `LAG`, `LEAD`는 왜 시계열 분석에서 자주 쓰일까요?

## 큰 그림

![SQL 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/sql-101/07/07-01-window-calculation-flow.ko.png)

*SQL 101 7장 흐름 개요*

이 그림에서는 윈도 함수가 행을 집계하지 않으면서도 행별로 전체 데이터에 대한 계산 값을 어떻게 붙이는지 봅니다. 윈도 함수는 GROUP BY와 다르게 원본 행의 개수를 유지하면서 분석 열을 추가합니다.

> 윈도 함수의 핵심은 행 개수를 줄이지 않으면서 전체 데이터의 맥락 속에서 각 행의 위치나 값을 계산한다는 점입니다.

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

- [PostgreSQL — Window Functions](https://www.postgresql.org/docs/current/tutorial-window.html)
- [PostgreSQL — Window Function Reference](https://www.postgresql.org/docs/current/functions-window.html)
- [Mode — Window Functions](https://mode.com/sql-tutorial/sql-window-functions/)
- [Use The Index, Luke — Top-N](https://use-the-index-luke.com/sql/partial-results/top-n-queries)

Tags: SQL, Database, Postgres, Analytics
