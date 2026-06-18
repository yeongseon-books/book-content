---
title: "바이브코딩을 위한 SQL 기초 (8/10): AI에게 데이터 수정 쿼리를 시킬 때 주의할 점"
series: sql-101
episode: 8
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- SQL
- AI코딩
seo_description: "바이브코딩 시대, AI가 생성한 INSERT, UPDATE, DELETE 쿼리를 안전하게 실행하는 방법을 설명합니다. 트랜잭션, RETURNING, 실행 전 검증 루틴을 익힙니다"
---

# 바이브코딩을 위한 SQL 기초 (8/10): AI에게 데이터 수정 쿼리를 시킬 때 주의할 점

이 글은 바이브코딩을 위한 SQL 기초 시리즈의 8번째 글입니다.

"AI야, 오래된 임시 사용자 계정 삭제해줘."

AI가 만들어준 쿼리:

```sql
DELETE FROM users WHERE created_at < '2024-01-01';
```

아무 생각 없이 실행하면? 2024년 이전에 가입한 모든 사용자가 지워진다. 임시 계정만 지우려 했는데 오래된 진짜 사용자도 함께 사라진다.

이게 바이브코딩에서 가장 위험한 순간이다. AI가 만든 SELECT는 틀려도 다시 실행하면 된다. 하지만 AI가 만든 DELETE나 UPDATE는 실행 순간 돌이키기 어렵다.

이 글에서는 AI에게 데이터 수정 쿼리를 시킬 때 반드시 지켜야 할 절차와, 실수를 막는 안전 습관을 설명한다.

> AI가 만든 SELECT가 틀리면 다시 실행하면 된다. AI가 만든 DELETE가 틀리면 데이터가 사라진다.

---

## 이 글에서 다룰 문제
- AI가 만든 UPDATE/DELETE를 그냥 실행하면 왜 위험할까요?
- 트랜잭션이 바이브코딩에서 왜 필수 안전망일까요?
- 실행 전에 어떻게 영향 범위를 확인할 수 있을까요?
- `RETURNING`이 데이터 수정 검증에 어떻게 도움이 될까요?
- AI에게 안전한 수정 쿼리를 만들도록 요청하는 방법은 뭘까요?

읽기 전용 쿼리(SELECT)는 몇 번을 실행해도 데이터가 바뀌지 않는다. 하지만 INSERT, UPDATE, DELETE는 실행하는 순간 DB 상태가 바뀐다. 바이브코딩에서 AI에게 수정 쿼리를 시킬 때는 조회 쿼리와 완전히 다른 주의가 필요하다.

## 안전한 수정 쿼리 실행 절차

AI가 UPDATE나 DELETE를 만들어줬을 때 이 순서를 따르라:

**1단계: SELECT로 먼저 확인**
```sql
-- DELETE를 실행하기 전에
SELECT COUNT(*) FROM users WHERE created_at < '2024-01-01';
-- 몇 행이 영향받는지 먼저 본다
```

**2단계: 대상 데이터 직접 확인**
```sql
SELECT id, name, email, created_at FROM users
WHERE created_at < '2024-01-01'
LIMIT 10;
-- 실제 어떤 행인지 눈으로 확인
```

**3단계: 트랜잭션 안에서 실행**
```sql
BEGIN;

DELETE FROM users WHERE created_at < '2024-01-01' RETURNING *;
-- RETURNING으로 실제 삭제된 행 확인

-- 결과가 예상과 맞으면
COMMIT;
-- 예상과 다르면
-- ROLLBACK;
```

## 트랜잭션의 역할

트랜잭션은 "이 작업들을 하나의 묶음으로 처리하라"는 지시다. `BEGIN`으로 시작하고 `COMMIT`으로 확정하거나 `ROLLBACK`으로 취소한다.

```sql
BEGIN;
UPDATE orders SET status = 'cancelled' WHERE id IN (1, 2, 3);
-- 결과 확인...
COMMIT;  -- 확정
-- 또는 ROLLBACK;  -- 취소 (변경 없던 일로)
```

트랜잭션 안에서는 `COMMIT`하기 전까지 변경이 반영되지 않는다. 결과를 보고 맞으면 COMMIT, 틀리면 ROLLBACK.

## RETURNING: 변경된 행 즉시 확인

PostgreSQL의 RETURNING은 UPDATE/DELETE 후 변경된 행을 바로 볼 수 있다.

```sql
-- 삭제된 행 확인
DELETE FROM users WHERE id = 4 RETURNING *;

-- 수정된 행 확인
UPDATE users SET name = 'New Name' WHERE id = 1 RETURNING id, name;
```

AI에게 수정 쿼리를 만들 때 항상 `RETURNING *`를 붙여달라고 요청하라.

## WHERE가 빠진 UPDATE/DELETE의 재앙

```sql
-- WHERE가 없으면 전체 테이블이 영향받음
UPDATE users SET status = 'inactive';     -- 모든 사용자 비활성화
DELETE FROM orders;                        -- 모든 주문 삭제
```

AI가 UPDATE나 DELETE를 만들었을 때 `WHERE` 절이 있는지 반드시 확인하라. WHERE 없이 실행하면 전체 테이블이 바뀐다.

## UPSERT: 있으면 수정, 없으면 삽입

```sql
INSERT INTO users (id, name, signup_at)
VALUES (4, 'Margaret', '2026-04-10')
ON CONFLICT (id)
DO UPDATE SET name = EXCLUDED.name;
```

동일한 id가 이미 있으면 새로 넣는 대신 이름을 갱신한다. AI가 "있으면 업데이트, 없으면 삽입" 로직을 만들 때 사용한다.

## Before / After

**Before: AI가 만든 쿼리를 그냥 실행**
```sql
UPDATE orders SET status = 'expired'
WHERE status = 'pending' AND created_at < '2025-01-01';
```
WHERE 조건이 얼마나 많은 행에 영향을 주는지 모른 채 실행.

**After: 안전한 절차로 실행**
```sql
-- 1. 영향 범위 확인
SELECT COUNT(*) FROM orders
WHERE status = 'pending' AND created_at < '2025-01-01';

-- 2. 샘플 확인
SELECT id, user_id, status, created_at FROM orders
WHERE status = 'pending' AND created_at < '2025-01-01'
LIMIT 5;

-- 3. 트랜잭션 안에서 실행
BEGIN;
UPDATE orders SET status = 'expired'
WHERE status = 'pending' AND created_at < '2025-01-01'
RETURNING id, user_id, status;
-- 결과 확인 후
COMMIT;
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
| --- | --- | --- |
| WHERE 없이 UPDATE/DELETE | 전체 테이블 변경 | WHERE 유무 먼저 확인 |
| 트랜잭션 없이 실행 | 롤백 불가 | BEGIN/COMMIT 습관화 |
| 실행 전 SELECT 안 함 | 영향 범위 모름 | 동일 조건 COUNT(*) 먼저 |
| AI 쿼리 그대로 복붙 실행 | 조건 오류 발견 못함 | 반드시 WHERE 조건 검토 |

## AI에게 SQL 요청하는 팁

- "이 UPDATE/DELETE 실행 전에 SELECT로 영향 범위를 먼저 확인하는 쿼리도 같이 만들어줘"
- "트랜잭션(BEGIN/COMMIT)으로 감싸줘"
- "RETURNING *를 붙여줘"
- "WHERE 조건이 정확한지 한 번 더 확인해줘"라고 검증을 요청하라

## 운영 체크리스트
- [ ] UPDATE/DELETE 전에 SELECT로 영향 범위를 확인한다
- [ ] 트랜잭션(BEGIN/COMMIT/ROLLBACK)을 이해하고 있다
- [ ] WHERE 없는 UPDATE/DELETE의 위험을 알고 있다
- [ ] RETURNING으로 변경된 행을 확인하는 방법을 안다
- [ ] 중요한 변경 전 데이터 백업 또는 트랜잭션을 사용한다

## 처음 질문으로 돌아가기

AI에게 데이터 수정 쿼리를 시킬 때 가장 중요한 것은 "실행 전 확인"이다. SELECT로 대상을 먼저 보고, 트랜잭션 안에서 실행하고, RETURNING으로 결과를 확인하고, 맞으면 COMMIT. 이 절차를 습관화하면 AI가 만든 수정 쿼리로 인한 사고를 90% 이상 막을 수 있다.

## 정리

데이터를 바꾸는 SQL의 핵심은 문법보다 안전한 실행 절차다. WHERE를 명시하고, 트랜잭션으로 묶고, RETURNING으로 검증하는 습관이 있어야 변경 작업을 통제할 수 있다. AI에게 수정 쿼리를 시킬 때는 항상 "실행 전 확인 → 트랜잭션 → RETURNING" 루틴을 요청하라.

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
- **바이브코딩을 위한 SQL 기초 (8/10): AI에게 데이터 수정 쿼리를 시킬 때 주의할 점 (현재 글)**
- [바이브코딩을 위한 SQL 기초 (9/10): AI가 만든 쿼리가 느릴 때 — 인덱스와 실행 계획](./09-index-and-query-plan.md)
- [바이브코딩을 위한 SQL 기초 (10/10): AI와 함께 실전 데이터 분석 SQL 짜기](./10-practical-analysis-sql.md)
<!-- toc:end -->
Tags: 바이브코딩, SQL, AI코딩, DML, 트랜잭션
