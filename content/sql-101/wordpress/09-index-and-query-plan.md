---
title: "바이브코딩을 위한 SQL 기초 (9/10): AI가 만든 쿼리가 느릴 때 — 인덱스와 실행 계획"
series: sql-101
episode: 9
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- SQL
- AI코딩
seo_description: "바이브코딩 시대, AI가 생성한 느린 쿼리를 개선하는 방법을 설명합니다. EXPLAIN, 인덱스 설계, 실행 계획 읽기를 실무 감각으로 익힙니다"
---

# 바이브코딩을 위한 SQL 기초 (9/10): AI가 만든 쿼리가 느릴 때 — 인덱스와 실행 계획

이 글은 바이브코딩을 위한 SQL 기초 시리즈의 9번째 글입니다.

"AI가 만든 쿼리인데 개발 환경에서는 빨랐는데 실서버에서는 30초가 걸린다."

바이브코딩으로 만든 앱이 처음엔 잘 돌아가다가 사용자가 늘면서 갑자기 느려지는 경험. 데이터가 적을 때는 괜찮았던 AI의 쿼리가 데이터가 쌓이면서 문제를 일으키는 경우다.

문제는 대부분 같은 곳에 있다. 인덱스가 없거나, 인덱스가 있어도 쿼리가 그것을 타지 않는 형태다.

이 글에서는 AI가 만든 쿼리가 느릴 때 어떻게 진단하고, 어떻게 해결하는지 설명한다. EXPLAIN 읽기와 인덱스 기본 개념이 핵심이다.

> 개발 환경에서 빠른 쿼리가 실서버에서 느린 건 데이터 양의 차이다. AI는 이를 고려하지 않는다. 성능은 내가 챙겨야 한다.

---

## 이 글에서 다룰 문제
- AI가 만든 쿼리가 왜 데이터가 많아지면 느려질까요?
- EXPLAIN으로 실행 계획을 어떻게 읽을까요?
- 인덱스가 있어도 왜 사용되지 않을 수 있을까요?
- 어떤 컬럼에 인덱스를 만들어야 할까요?
- AI에게 성능을 고려한 쿼리를 만들도록 요청하는 방법은 뭘까요?

데이터가 100개일 때와 100만 개일 때는 완전히 다른 세계다. AI는 문법적으로 맞는 쿼리를 만들지만, 데이터 규모를 고려한 최적화는 내가 챙겨야 하는 영역이다.

## EXPLAIN으로 실행 계획 읽기

EXPLAIN은 쿼리를 실제로 실행하지 않고 어떻게 실행할지 계획을 보여준다.

```sql
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';
```

결과 예시:
```
Seq Scan on users  (cost=0.00..1850.00 rows=1 width=128)
  Filter: (email = 'test@example.com'::text)
```

`Seq Scan`은 순차 스캔이다. 전체 테이블을 처음부터 끝까지 읽는다는 뜻이다. 데이터가 100만 개면 100만 개를 모두 읽는다.

인덱스를 추가하면:
```sql
CREATE INDEX idx_users_email ON users (email);
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';
```

```
Index Scan using idx_users_email on users  (cost=0.29..8.30 rows=1 width=128)
  Index Cond: (email = 'test@example.com'::text)
```

`Index Scan`으로 바뀌었다. 전체를 읽는 대신 인덱스로 바로 찾는다.

## EXPLAIN ANALYZE: 실제 실행 시간까지

```sql
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';
```

실제로 실행하고 시간도 보여준다. `actual time`이 실제 시간이다.

주의: EXPLAIN ANALYZE는 실제로 실행되므로 UPDATE/DELETE에는 트랜잭션 안에서 사용하라.

## 인덱스가 있어도 안 쓰이는 경우

AI가 만든 쿼리가 인덱스를 타지 않는 패턴들:

### 컬럼에 함수 적용

```sql
-- 인덱스 못 탐 (email 컬럼을 함수로 감쌈)
SELECT * FROM users WHERE LOWER(email) = 'test@example.com';

-- 인덱스 탐 (컬럼을 그대로 씀)
SELECT * FROM users WHERE email = 'test@example.com';
```

AI가 대소문자 무시 검색을 위해 `LOWER()`를 쓰면 인덱스를 못 탄다.

### LIKE 앞에 와일드카드

```sql
-- 인덱스 못 탐
SELECT * FROM users WHERE email LIKE '%@example.com';

-- 인덱스 탐
SELECT * FROM users WHERE email LIKE 'test%';
```

앞에 `%`가 오면 인덱스를 사용하기 어렵다.

### 날짜 함수 사용

```sql
-- 인덱스 못 탐
SELECT * FROM orders WHERE YEAR(created_at) = 2026;

-- 인덱스 탐
SELECT * FROM orders WHERE created_at >= '2026-01-01' AND created_at < '2027-01-01';
```

## 어떤 컬럼에 인덱스를 만들어야 하나

**인덱스가 효과 있는 경우:**
- WHERE 조건에 자주 쓰이는 컬럼
- JOIN 조건에 쓰이는 컬럼 (외래 키)
- ORDER BY에 쓰이는 컬럼

**인덱스가 효과 없거나 오히려 나쁜 경우:**
- 값의 종류가 2-3개밖에 없는 컬럼 (`is_active`, `status` 등)
- 매우 작은 테이블
- INSERT/UPDATE/DELETE가 매우 빈번한 테이블 (인덱스 유지 비용)

```sql
-- 자주 쓰이는 기본 인덱스
CREATE INDEX idx_orders_user_id ON orders (user_id);
CREATE INDEX idx_orders_created_at ON orders (created_at);

-- 복합 인덱스 (user_id로 필터하고 created_at으로 정렬하는 패턴)
CREATE INDEX idx_orders_user_date ON orders (user_id, created_at DESC);
```

## Before / After

**Before: AI가 만든 느린 쿼리**
```sql
SELECT * FROM orders
WHERE YEAR(created_at) = 2026 AND user_id = 42;
```
`YEAR()` 함수 때문에 인덱스를 못 타고 전체 테이블 스캔.

**After: 인덱스를 타는 형태**
```sql
SELECT id, user_id, total, created_at FROM orders
WHERE user_id = 42
  AND created_at >= '2026-01-01'
  AND created_at < '2027-01-01';

-- 복합 인덱스 추가
CREATE INDEX idx_orders_user_created ON orders (user_id, created_at);
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
| --- | --- | --- |
| 컬럼에 함수 적용 | 인덱스 사용 불가 | 컬럼 그대로 쓰는 형태로 변경 |
| LIKE 앞에 % | 인덱스 사용 불가 | 뒤에 %만 (전방 검색만 인덱스 사용) |
| 인덱스 없이 대용량 테이블 JOIN | 전체 스캔으로 느림 | JOIN 키 컬럼에 인덱스 추가 |
| SELECT * 사용 | 불필요한 컬럼 읽기 | 필요한 컬럼만 선택 |

## AI에게 SQL 요청하는 팁

- "이 쿼리가 인덱스를 타는지 EXPLAIN으로 확인해줘"라고 요청하라
- "컬럼에 함수를 쓰지 말고 범위 조건으로 바꿔줘"
- "이 쿼리에 필요한 인덱스도 같이 만들어줘"라고 하면 인덱스까지 함께 받을 수 있다
- "10만 건 이상 데이터에서도 빠르게 동작하도록 최적화해줘"라고 명시하라

## 운영 체크리스트
- [ ] EXPLAIN으로 Seq Scan vs Index Scan을 구분할 수 있다
- [ ] 인덱스가 있어도 안 쓰이는 패턴을 알고 있다
- [ ] 어떤 컬럼에 인덱스를 만들어야 하는지 기준을 안다
- [ ] 복합 인덱스의 컬럼 순서가 중요하다는 것을 안다
- [ ] 인덱스가 쓰기 성능에 영향을 준다는 것을 이해하고 있다

## 처음 질문으로 돌아가기

AI가 만든 쿼리가 느릴 때 첫 번째 할 일은 EXPLAIN으로 Seq Scan인지 Index Scan인지 확인하는 것이다. Seq Scan이면 인덱스가 없거나 쿼리가 인덱스를 타지 않는 형태다. AI가 컬럼에 함수를 쓰거나 LIKE 앞에 %를 붙였다면 인덱스를 타지 않는 패턴이다. 이 두 가지만 확인해도 대부분의 느린 쿼리 원인을 찾을 수 있다.

## 정리

성능 튜닝의 출발점은 인덱스를 많이 만드는 것이 아니라 실행 계획을 읽는 것이다. EXPLAIN으로 어떤 스캔이 선택됐는지 확인하고, AI가 만든 쿼리가 인덱스를 타는 형태인지 검토하는 습관이 바이브코딩에서 성능 문제를 예방하는 가장 효과적인 방법이다.

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
- [바이브코딩을 위한 SQL 기초 (6/10): AI가 서브쿼리를 중첩했다 — 읽기 어려운 쿼리 해석](./06-subquery.md)
- [바이브코딩을 위한 SQL 기초 (7/10): AI가 윈도우 함수를 썼는데 뭔지 모르겠다](./07-window-function.md)
- [바이브코딩을 위한 SQL 기초 (8/10): AI에게 데이터 수정 쿼리를 시킬 때 주의할 점](./08-insert-update-delete.md)
- **바이브코딩을 위한 SQL 기초 (9/10): AI가 만든 쿼리가 느릴 때 — 인덱스와 실행 계획 (현재 글)**
- [바이브코딩을 위한 SQL 기초 (10/10): AI와 함께 실전 데이터 분석 SQL 짜기](./10-practical-analysis-sql.md)
<!-- toc:end -->
Tags: 바이브코딩, SQL, AI코딩, 인덱스, EXPLAIN
