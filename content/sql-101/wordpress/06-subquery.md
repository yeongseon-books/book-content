---
title: "바이브코딩을 위한 SQL 기초 (6/10): AI가 서브쿼리를 중첩했다 — 읽기 어려운 쿼리 해석"
series: sql-101
episode: 6
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- SQL
- AI코딩
seo_description: "바이브코딩 시대, AI가 생성한 중첩 서브쿼리와 CTE를 이해하고 읽는 방법을 설명합니다. 서브쿼리, EXISTS, 인라인 뷰, CTE의 실무 감각을 익힙니다"
---

# 바이브코딩을 위한 SQL 기초 (6/10): AI가 서브쿼리를 중첩했다 — 읽기 어려운 쿼리 해석

이 글은 바이브코딩을 위한 SQL 기초 시리즈의 6번째 글입니다.

"AI야, 지난달에 100만원 이상 결제한 사용자 중에서 아직 VIP가 아닌 사람만 뽑아줘."

AI가 만들어준 쿼리:

```sql
SELECT * FROM users
WHERE id IN (
    SELECT user_id FROM orders
    WHERE total > 1000000
      AND created_at >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
      AND created_at < DATE_TRUNC('month', CURRENT_DATE)
)
AND id NOT IN (
    SELECT user_id FROM vip_users WHERE is_active = true
);
```

읽을 수 있는가? 어떻게 실행되는지 머릿속에서 따라갈 수 있는가?

이것이 서브쿼리다. 쿼리 안에 쿼리가 들어있다. AI는 복잡한 조건을 서브쿼리로 표현하는 경향이 있다. 서브쿼리를 읽지 못하면 AI가 만든 복잡한 쿼리를 전혀 이해할 수 없다.

이 글에서는 서브쿼리를 어떻게 읽는지, CTE가 왜 더 나은지, AI가 서브쿼리를 만들 때 흔한 실수가 무엇인지 설명한다.

> AI가 만든 복잡한 쿼리를 이해 못하면 수정도, 검증도 할 수 없다. 서브쿼리 읽기는 바이브코딩의 필수 기술이다.

---

## 이 글에서 다룰 문제
- 서브쿼리는 어떤 순서로 읽어야 할까요?
- `IN`과 `EXISTS`는 언제 다르게 동작하고 어느 게 더 나을까요?
- CTE(`WITH`)가 서브쿼리보다 나은 이유가 뭘까요?
- `NOT IN`이 NULL 때문에 위험한 경우는 언제일까요?
- AI가 중첩 서브쿼리를 만들었을 때 어떻게 풀어서 이해할까요?

복잡한 분석 요청일수록 AI는 중첩 서브쿼리를 만들기 쉽다. 이를 읽지 못하면 결과가 맞는지 판단할 수 없고, 틀렸을 때 어디를 고쳐야 하는지도 모른다.

## 서브쿼리 유형 읽기

### 인라인 뷰 (FROM 절 서브쿼리)

```sql
SELECT t.country, t.users
FROM (
    SELECT country, COUNT(*) AS users
    FROM users GROUP BY country
) AS t
WHERE t.users > 100;
```

FROM 절 안의 괄호가 임시 테이블처럼 동작한다. 안쪽 쿼리를 먼저 실행해서 임시 결과를 만들고, 바깥 쿼리가 그 결과를 사용한다.

**읽는 방법**: 안쪽 괄호부터 읽어라. "국가별 사용자 수를 먼저 만들고, 그 중 100명 초과인 것만 가져온다."

### WHERE IN 서브쿼리

```sql
SELECT * FROM users
WHERE id IN (SELECT user_id FROM orders WHERE total > 1000);
```

**읽는 방법**: "주문 금액이 1000 이상인 주문의 user_id 목록을 먼저 구하고, 그 목록에 있는 사용자를 가져온다."

### EXISTS 서브쿼리

```sql
SELECT * FROM users u
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id
);
```

**읽는 방법**: "각 사용자에 대해, 그 사용자의 주문이 하나라도 있으면 포함한다."

EXISTS는 존재 여부만 확인한다. 첫 번째 매칭 행을 찾으면 멈추기 때문에 큰 데이터에서 IN보다 빠를 수 있다.

## CTE: 서브쿼리보다 읽기 좋은 방법

AI가 중첩 서브쿼리를 만들었다면 CTE로 바꿔달라고 요청하라. 같은 로직이지만 훨씬 읽기 쉽다.

```sql
-- 중첩 서브쿼리 (읽기 어려움)
SELECT * FROM (
    SELECT * FROM (
        SELECT user_id, SUM(total) AS spend
        FROM orders WHERE status = 'paid'
        GROUP BY user_id
    ) t1 WHERE spend > 100000
) t2 WHERE user_id > 100;

-- CTE로 단계별로 분리 (읽기 쉬움)
WITH paid_revenue AS (
    SELECT user_id, SUM(total) AS spend
    FROM orders WHERE status = 'paid'
    GROUP BY user_id
),
high_spenders AS (
    SELECT * FROM paid_revenue WHERE spend > 100000
)
SELECT * FROM high_spenders WHERE user_id > 100;
```

CTE는 `WITH 이름 AS (...)`로 중간 결과에 이름을 붙인다. 각 단계를 위에서 아래로 읽으면서 이해할 수 있다.

## AI가 서브쿼리에서 자주 하는 실수

### 실수 1: NOT IN과 NULL 혼용

```sql
-- NULL이 있으면 빈 결과가 나올 수 있음
SELECT * FROM users
WHERE id NOT IN (SELECT user_id FROM blocked_users);
-- blocked_users에 NULL이 하나라도 있으면 결과가 비어버림

-- 안전한 방법
SELECT * FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM blocked_users b WHERE b.user_id = u.id
);
```

AI가 `NOT IN`을 썼고 서브쿼리 결과에 NULL이 있을 가능성이 있다면, `NOT EXISTS`로 바꾸는 게 안전하다.

### 실수 2: 상관 서브쿼리 성능 문제

```sql
-- 각 사용자 행마다 서브쿼리를 반복 실행 (느림)
SELECT id, name,
    (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) AS order_count
FROM users u;

-- JOIN으로 바꾸면 훨씬 빠름
SELECT u.id, u.name, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;
```

AI가 SELECT 절에 서브쿼리를 넣으면, 행마다 반복 실행되어 데이터가 많을 때 매우 느려진다.

## Before / After

**Before: AI가 만든 중첩 서브쿼리**
```sql
SELECT name FROM users
WHERE id IN (
    SELECT user_id FROM orders
    WHERE total > (SELECT AVG(total) FROM orders)
);
```

**After: CTE로 단계 분리**
```sql
WITH avg_total AS (
    SELECT AVG(total) AS threshold FROM orders
),
high_orders AS (
    SELECT user_id FROM orders, avg_total
    WHERE total > threshold
)
SELECT u.name FROM users u
WHERE u.id IN (SELECT user_id FROM high_orders);
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
| --- | --- | --- |
| NOT IN + NULL 가능 서브쿼리 | 빈 결과 발생 | NOT EXISTS로 대체 |
| SELECT 절 상관 서브쿼리 | 행마다 반복 실행 (느림) | LEFT JOIN + GROUP BY로 변환 |
| 중첩 서브쿼리 3단계 이상 | 읽기 불가 | CTE로 단계별 분리 요청 |
| 서브쿼리 결과를 확인 안 함 | 중간 단계 오류 미발견 | CTE 단계별로 별도 실행해 확인 |

## AI에게 SQL 요청하는 팁

- "서브쿼리 대신 CTE(WITH 절)를 써줘"라고 하면 더 읽기 쉬운 쿼리를 얻는다
- "각 CTE 단계가 뭘 하는지 주석으로 설명해줘"를 요청하라
- "NOT IN 대신 NOT EXISTS를 써줘"라고 명시하면 NULL 함정을 피할 수 있다
- AI가 만든 복잡한 쿼리는 "이 쿼리를 단계별로 설명해줘"로 이해를 먼저 확인하라

## 운영 체크리스트
- [ ] 서브쿼리를 안쪽부터 읽는 방법을 알고 있다
- [ ] CTE가 중첩 서브쿼리보다 읽기 좋은 이유를 설명할 수 있다
- [ ] `NOT IN`과 NULL 혼용의 위험을 알고 있다
- [ ] 상관 서브쿼리가 성능 문제를 일으킬 수 있음을 안다
- [ ] AI에게 CTE 사용을 요청할 수 있다

## 처음 질문으로 돌아가기

AI가 서브쿼리를 중첩했을 때 읽는 방법은 하나다. 안쪽 괄호부터 읽어라. 각 서브쿼리가 무엇을 하는지 말로 설명할 수 있으면 이해한 것이다. 설명하지 못하면 CTE로 바꿔달라고 요청하라. CTE는 같은 로직을 단계별로 이름 붙여 표현하기 때문에 훨씬 이해하기 쉽다.

## 정리

서브쿼리와 CTE의 핵심은 복잡한 질문을 읽을 수 있는 층으로 나누는 데 있다. AI가 만든 중첩 서브쿼리는 CTE로 바꿔달라고 요청하면 이해와 검증이 모두 쉬워진다. NOT IN의 NULL 함정과 상관 서브쿼리의 성능 문제만 알아도 AI가 만든 복잡한 쿼리를 훨씬 안전하게 다룰 수 있다.

## 참고 자료
### 공식 문서
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
### 관련 시리즈
- [Database Systems 101](../../database-systems-101/ko/)
- [SQLAlchemy 101](../../sqlalchemy-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차
- [바이브코딩을 위한 SQL 기초 (1/10): AI에게 DB 쿼리 시키기 전에 알아야 할 것](./01-what-is-sql.md)
- [바이브코딩을 위한 SQL 기초 (2/10): AI가 만든 SELECT를 읽으려면](./02-select-basics.md)
- [바이브코딩을 위한 SQL 기초 (3/10): AI가 WHERE 조건을 잘못 짰을 때](./03-where-and-conditions.md)
- [바이브코딩을 위한 SQL 기초 (4/10): AI가 JOIN을 썼는데 맞는지 확인하려면](./04-join.md)
- [바이브코딩을 위한 SQL 기초 (5/10): AI가 GROUP BY를 넣었는데 집계가 이상할 때](./05-group-by-and-aggregate.md)
- **바이브코딩을 위한 SQL 기초 (6/10): AI가 서브쿼리를 중첩했다 — 읽기 어려운 쿼리 해석 (현재 글)**
- [바이브코딩을 위한 SQL 기초 (7/10): AI가 윈도우 함수를 썼는데 뭔지 모르겠다](./07-window-function.md)
- [바이브코딩을 위한 SQL 기초 (8/10): AI에게 데이터 수정 쿼리를 시킬 때 주의할 점](./08-insert-update-delete.md)
- [바이브코딩을 위한 SQL 기초 (9/10): AI가 만든 쿼리가 느릴 때 — 인덱스와 실행 계획](./09-index-and-query-plan.md)
- [바이브코딩을 위한 SQL 기초 (10/10): AI와 함께 실전 데이터 분석 SQL 짜기](./10-practical-analysis-sql.md)
<!-- toc:end -->
Tags: 바이브코딩, SQL, AI코딩, 서브쿼리, CTE
