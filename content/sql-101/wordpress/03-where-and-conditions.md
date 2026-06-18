---
title: "바이브코딩을 위한 SQL 기초 (3/10): AI가 WHERE 조건을 잘못 짰을 때 — 조건과 필터"
series: sql-101
episode: 3
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- SQL
- AI코딩
seo_description: "바이브코딩 시대, AI가 생성한 WHERE 조건의 오류를 찾아내는 방법을 설명합니다. NULL 비교, AND/OR 우선순위, IN/BETWEEN/LIKE의 실무 감각을 익힙니다"
---

# 바이브코딩을 위한 SQL 기초 (3/10): AI가 WHERE 조건을 잘못 짰을 때 — 조건과 필터

이 글은 바이브코딩을 위한 SQL 기초 시리즈의 3번째 글입니다.

"AI야, 삭제되지 않은 활성 사용자 중에서 미국 또는 영국 사람만 뽑아줘."

AI가 이런 쿼리를 만들어줬다.

```sql
SELECT * FROM users
WHERE deleted_at = NULL OR country = 'US' OR country = 'UK' AND is_active = true;
```

실행해봤더니 결과가 이상하다. 삭제된 사용자도 포함되어 있고, 비활성 사용자도 섞여 있다. AI가 틀렸다. 아니, 정확히는 AI가 만든 조건에 두 가지 고전적인 실수가 있다.

1. `deleted_at = NULL`은 절대 작동하지 않는다. NULL 비교는 `IS NULL`로 해야 한다.
2. `OR`와 `AND`의 우선순위 때문에 조건이 의도와 다르게 결합된다.

이 글에서는 AI가 WHERE 조건을 만들 때 자주 하는 실수와, 그것을 내가 어떻게 찾아낼 수 있는지 설명한다.

> WHERE 조건 하나가 틀리면 조용히 틀린 결과가 나온다. 느린 쿼리보다 틀린 결과가 더 위험하다.

---

## 이 글에서 다룰 문제
- AI가 만든 WHERE 조건이 정말 내가 원하는 행을 걸러내고 있을까요?
- `NULL` 비교를 잘못 쓰면 어떤 결과가 나올까요?
- `AND`와 `OR`가 섞이면 왜 괄호가 필수일까요?
- `IN`, `BETWEEN`, `LIKE`는 각각 언제 쓰면 좋을까요?
- 조건식이 인덱스 성능에 영향을 준다는 게 무슨 뜻일까요?

WHERE는 결과의 정확도와 성능을 동시에 결정한다. 조건이 잘 설계되면 적은 행만 읽고 끝난다. 반대로 조건이 흐릿하거나 인덱스를 타지 못하는 형태면 전체 테이블을 훑는다. 실무에서 더 무서운 것은 느린 쿼리보다 틀린 결과를 조용히 내는 쿼리다.

## WHERE 평가 흐름

모든 행이 일단 후보로 들어오고, WHERE 조건식을 평가한 뒤 참인 행만 다음 단계로 넘어간다. 거짓뿐 아니라 NULL 결과도 통과하지 못한다는 점이 중요하다. SQL은 참/거짓이 아니라 참/거짓/NULL의 세 값 논리로 동작한다.

## AI가 WHERE에서 자주 하는 실수

### 실수 1: NULL을 `=`로 비교

```sql
-- AI가 만든 잘못된 쿼리
SELECT * FROM users WHERE deleted_at = NULL;

-- 올바른 쿼리
SELECT * FROM users WHERE deleted_at IS NULL;
```

`= NULL`은 항상 NULL(모름)으로 평가되어 결과가 비어버린다. AI가 NULL 조건을 만들면 반드시 `IS NULL` 또는 `IS NOT NULL`인지 확인하라.

### 실수 2: AND/OR 우선순위 괄호 없음

```sql
-- AI가 만든 쿼리 (의도와 다르게 동작)
SELECT * FROM users
WHERE country = 'US' OR country = 'UK' AND age >= 18;

-- AND가 OR보다 먼저 결합되어 사실상 이렇게 읽힌다
-- country = 'US' OR (country = 'UK' AND age >= 18)

-- 의도대로 하려면 괄호 필수
SELECT * FROM users
WHERE (country = 'US' OR country = 'UK') AND age >= 18;
```

AI가 AND와 OR를 섞은 조건을 만들면 괄호가 있는지 반드시 확인하라. 없다면 의도대로 동작하지 않을 가능성이 높다.

### 실수 3: 컬럼에 함수 감싸기

```sql
-- AI가 만든 쿼리 (인덱스를 못 탄다)
SELECT * FROM orders WHERE YEAR(order_date) = 2026;

-- 인덱스를 타는 형태로 수정
SELECT * FROM orders
WHERE order_date >= '2026-01-01' AND order_date < '2027-01-01';
```

컬럼에 함수를 감싸면 인덱스를 사용하기 어려워진다. AI가 이런 패턴을 만들면 범위 조건으로 바꿔달라고 요청하라.

## 조건 패턴 읽기

### BETWEEN: 범위 조건

```sql
SELECT * FROM orders WHERE total BETWEEN 100 AND 500;
```

경계값(100, 500)이 포함된다. `>= 100 AND <= 500`과 같은 의미다.

### IN: 목록 포함 여부

```sql
SELECT * FROM users WHERE country IN ('KR', 'JP', 'US');
```

여러 OR 조건을 간결하게 표현한다. 목록이 너무 길어지면 서브쿼리나 JOIN으로 바꾸는 게 낫다.

### LIKE: 패턴 검색

```sql
SELECT * FROM users WHERE name LIKE 'A%';    -- A로 시작
SELECT * FROM users WHERE email LIKE '%@example.com';  -- 끝에 일치
```

앞에 `%`가 오면(`%xxx`) 인덱스를 타기 어렵다. AI가 이 패턴을 만들면 성능에 주의하라.

### IS NULL / IS NOT NULL

```sql
SELECT * FROM users WHERE deleted_at IS NULL;      -- 삭제 안 된 사용자
SELECT * FROM users WHERE deleted_at IS NOT NULL;  -- 삭제된 사용자
```

## Before / After

**Before: AI가 만든 조건 (버그 포함)**
```sql
SELECT * FROM users
WHERE country = 'US' OR country = 'UK' AND is_active = true AND deleted_at = NULL;
```
삭제된 사용자도 나오고, UK 비활성 사용자는 제외되지 않는다.

**After: 올바른 조건**
```sql
SELECT id, name, country FROM users
WHERE (country = 'US' OR country = 'UK')
  AND is_active = true
  AND deleted_at IS NULL;
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
| --- | --- | --- |
| `= NULL` 사용 | 결과가 항상 비어있음 | `IS NULL`로 변경 |
| AND/OR 괄호 없음 | 조건이 의도와 다르게 결합 | 괄호로 우선순위 명시 |
| 컬럼에 함수 적용 | 인덱스 사용 불가 | 범위 조건으로 재작성 |
| NOT IN과 NULL 혼용 | 예상치 못한 빈 결과 | NOT EXISTS로 대체 |

## AI에게 SQL 요청하는 팁

- "NULL인 경우도 처리해줘"를 명시하면 `IS NULL` 패턴이 나온다
- "AND와 OR 조건은 괄호로 묶어줘"라고 요청하면 안전하다
- 날짜 조건은 "BETWEEN보다 범위 조건(>=, <)으로 써줘"가 더 인덱스 친화적이다
- AI가 만든 WHERE가 있으면 "이 조건이 정확히 어떤 행을 거르는지 설명해줘"라고 물어보라

## 운영 체크리스트
- [ ] `IS NULL`과 `= NULL`의 차이를 설명할 수 있다
- [ ] `AND`와 `OR`가 섞이면 괄호를 먼저 확인한다
- [ ] `LIKE '%xxx'` 형태가 인덱스에 문제가 될 수 있음을 안다
- [ ] 컬럼에 함수를 감싸는 조건이 왜 느려지는지 안다
- [ ] 조건식이 인덱스 사용 여부에 영향을 준다는 점을 이해하고 있다

## 처음 질문으로 돌아가기

AI가 WHERE 조건을 잘못 짰을 때 확인할 세 가지: NULL을 `IS NULL`로 비교하는지, AND/OR 우선순위에 괄호가 있는지, 컬럼에 함수를 감싸지 않는지. 이 세 가지만 체크해도 AI가 만든 WHERE 조건의 80%는 검증할 수 있다.

## 정리

WHERE는 단순한 필터가 아니라 정확도와 성능의 기준점이다. 참과 거짓만이 아니라 NULL까지 포함한 세 값 논리를 이해해야 하고, 사람이 읽기 쉬운 괄호와 데이터베이스가 처리하기 쉬운 조건식 모양을 함께 고려해야 한다. AI가 만든 WHERE는 항상 이 관점으로 검토하라.

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
- **바이브코딩을 위한 SQL 기초 (3/10): AI가 WHERE 조건을 잘못 짰을 때 (현재 글)**
- [바이브코딩을 위한 SQL 기초 (4/10): AI가 JOIN을 썼는데 맞는지 확인하려면](./04-join.md)
- [바이브코딩을 위한 SQL 기초 (5/10): AI가 GROUP BY를 넣었는데 집계가 이상할 때](./05-group-by-and-aggregate.md)
- [바이브코딩을 위한 SQL 기초 (6/10): AI가 서브쿼리를 중첩했다 — 읽기 어려운 쿼리 해석](./06-subquery.md)
- [바이브코딩을 위한 SQL 기초 (7/10): AI가 윈도우 함수를 썼는데 뭔지 모르겠다](./07-window-function.md)
- [바이브코딩을 위한 SQL 기초 (8/10): AI에게 데이터 수정 쿼리를 시킬 때 주의할 점](./08-insert-update-delete.md)
- [바이브코딩을 위한 SQL 기초 (9/10): AI가 만든 쿼리가 느릴 때 — 인덱스와 실행 계획](./09-index-and-query-plan.md)
- [바이브코딩을 위한 SQL 기초 (10/10): AI와 함께 실전 데이터 분석 SQL 짜기](./10-practical-analysis-sql.md)
<!-- toc:end -->
Tags: 바이브코딩, SQL, AI코딩, WHERE, NULL
