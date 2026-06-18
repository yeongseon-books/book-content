---
title: "바이브코딩을 위한 SQL 기초 (5/10): AI가 GROUP BY를 넣었는데 집계가 이상할 때"
series: sql-101
episode: 5
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- SQL
- AI코딩
seo_description: "바이브코딩 시대, AI가 생성한 GROUP BY 집계 쿼리의 오류를 찾아내는 방법을 설명합니다. WHERE vs HAVING, COUNT 함정, 집계 단위 설계를 실무 감각으로 익힙니다"
---

# 바이브코딩을 위한 SQL 기초 (5/10): AI가 GROUP BY를 넣었는데 집계가 이상할 때

이 글은 바이브코딩을 위한 SQL 기초 시리즈의 5번째 글입니다.

"AI야, 국가별 사용자 수랑 평균 나이 뽑아줘. 그런데 사용자가 10명 이상인 국가만."

AI가 만들어준 쿼리:

```sql
SELECT country, COUNT(*) AS user_count, AVG(age) AS avg_age
FROM users
WHERE COUNT(*) >= 10
GROUP BY country;
```

실행하면 오류가 난다. `WHERE`에 집계 함수를 쓸 수 없기 때문이다. 이게 GROUP BY를 배울 때 가장 먼저 만나는 함정이다.

맞는 쿼리는 이렇다:

```sql
SELECT country, COUNT(*) AS user_count, AVG(age) AS avg_age
FROM users
GROUP BY country
HAVING COUNT(*) >= 10;
```

AI가 WHERE와 HAVING을 헷갈리면 오류가 나거나, 더 나쁜 경우에는 조용히 틀린 결과가 나온다. 이 글에서는 AI가 GROUP BY를 썼을 때 어떻게 검증하는지 설명한다.

> 집계 쿼리에서 숫자는 나오는데 틀린 경우가 가장 위험하다. 숫자가 나왔으니 맞겠지 하고 그냥 쓰게 된다.

---

## 이 글에서 다룰 문제
- WHERE와 HAVING이 왜 다른지, AI가 잘 구분해서 썼는지 어떻게 알까요?
- `COUNT(*)`와 `COUNT(컬럼)`은 어떻게 다를까요?
- 집계 결과가 예상보다 크거나 작을 때 어떻게 찾을까요?
- JOIN 후 GROUP BY를 하면 왜 집계가 부풀어질 수 있을까요?
- GROUP BY 없이 집계 함수를 쓰면 어떻게 될까요?

대시보드에 보이는 숫자는 거의 다 집계 결과다. 그리고 집계 쿼리는 틀려도 숫자가 나오기 때문에 발견하기 어렵다. AI가 만든 집계 쿼리를 검증하는 습관이 없으면, 조용히 틀린 지표를 보게 된다.

## 집계 흐름 이해하기

```
WHERE (집계 전 행 필터)
  → GROUP BY (행을 그룹으로 묶기)
    → 집계 함수 계산 (COUNT, SUM, AVG...)
      → HAVING (집계 결과 필터)
```

이 순서가 핵심이다. WHERE는 집계 전, HAVING은 집계 후다. 집계 함수를 WHERE에 쓰면 오류가 난다.

## AI가 GROUP BY에서 자주 하는 실수

### 실수 1: WHERE에 집계 함수 사용

```sql
-- 오류 발생
SELECT country, COUNT(*) AS cnt
FROM users
WHERE COUNT(*) >= 10  -- 집계 함수를 WHERE에 쓸 수 없음
GROUP BY country;

-- 올바른 쿼리
SELECT country, COUNT(*) AS cnt
FROM users
GROUP BY country
HAVING COUNT(*) >= 10;
```

### 실수 2: COUNT(*) vs COUNT(컬럼) 혼동

```sql
SELECT
    COUNT(*) AS total_rows,       -- NULL 포함, 모든 행
    COUNT(age) AS non_null_age,   -- age가 NULL이 아닌 행만
    AVG(age) AS avg_age           -- NULL 제외하고 평균
FROM users;
```

AI가 `COUNT(*)`를 써야 할 곳에 `COUNT(컬럼)`을 쓰거나 그 반대를 하면 숫자가 달라진다. NULL이 있는 컬럼이라면 특히 주의하라.

### 실수 3: JOIN 후 집계 부풀기

4편에서 나온 카디널리티 문제다. 주문과 주문 아이템을 JOIN한 뒤 주문 금액을 합산하면, 한 주문이 여러 아이템 수만큼 반복되어 합계가 부풀어진다.

```sql
-- 합계가 부풀어지는 경우
SELECT u.name, SUM(o.total) AS total_spend
FROM users u
JOIN orders o ON o.user_id = u.id
JOIN order_items oi ON oi.order_id = o.id
GROUP BY u.name;
-- order_items 수만큼 o.total이 반복 합산됨

-- 안전한 방법: 집계를 먼저 한 뒤 JOIN
WITH order_totals AS (
    SELECT user_id, SUM(total) AS spend
    FROM orders
    GROUP BY user_id
)
SELECT u.name, ot.spend
FROM users u
JOIN order_totals ot ON ot.user_id = u.id;
```

### 실수 4: 그룹 키 외 컬럼 SELECT

```sql
-- 오류 또는 비정상 결과
SELECT country, name, COUNT(*) AS cnt
FROM users
GROUP BY country;  -- name은 그룹 키가 아닌데 SELECT에 있음
```

GROUP BY에 없는 컬럼을 SELECT에 넣으면 오류가 나거나, 임의의 값이 선택된다. AI가 만든 SELECT 컬럼이 GROUP BY에 모두 포함되어 있는지 확인하라.

## 집계 함수 비교

| 함수 | 역할 | NULL 처리 |
| --- | --- | --- |
| `COUNT(*)` | 전체 행 수 | NULL 포함 |
| `COUNT(col)` | NULL 아닌 행 수 | NULL 제외 |
| `SUM(col)` | 합계 | NULL 제외 |
| `AVG(col)` | 평균 | NULL 제외 (0으로 간주 안 함) |
| `MIN(col)` | 최솟값 | NULL 제외 |
| `MAX(col)` | 최댓값 | NULL 제외 |

## Before / After

**Before: AI가 만든 쿼리 (HAVING 위치 오류)**
```sql
SELECT country, COUNT(*) AS user_count
FROM users
WHERE COUNT(*) > 5
GROUP BY country;
-- 오류: aggregate functions are not allowed in WHERE
```

**After: 올바른 HAVING 사용**
```sql
SELECT country, COUNT(*) AS user_count
FROM users
GROUP BY country
HAVING COUNT(*) > 5
ORDER BY user_count DESC;
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
| --- | --- | --- |
| 집계 조건을 WHERE에 넣음 | 오류 발생 | HAVING으로 이동 |
| COUNT(*) vs COUNT(col) 혼동 | NULL 처리 결과 다름 | NULL 여부에 따라 구분 |
| JOIN 후 바로 SUM | 집계 부풀기 | 먼저 집계 후 JOIN |
| GROUP BY 키가 SELECT와 불일치 | 오류 또는 임의값 | SELECT = GROUP BY + 집계함수 |

## AI에게 SQL 요청하는 팁

- "집계 조건(예: 10명 이상인 국가만)은 HAVING을 써줘"라고 명시하라
- "NULL이 있는 컬럼을 집계할 때 처리 방식 설명해줘"라고 물어보라
- "JOIN 후 집계할 때 카디널리티 문제 없는지 확인해줘"를 요청하라
- 집계 결과가 나오면 "원본 데이터와 비교해서 숫자가 맞는지 검증해줘"를 물어보라

## 운영 체크리스트
- [ ] WHERE와 HAVING의 차이를 설명할 수 있다
- [ ] `COUNT(*)`와 `COUNT(col)`의 차이를 알고 있다
- [ ] GROUP BY 키와 SELECT 컬럼 관계를 이해하고 있다
- [ ] JOIN 후 집계할 때 카디널리티를 먼저 확인한다
- [ ] NULL이 집계 함수에서 어떻게 처리되는지 안다

## 처음 질문으로 돌아가기

AI가 GROUP BY를 쓴 쿼리를 받았을 때 세 가지를 확인하라. 집계 조건이 HAVING에 있는지 (WHERE가 아닌지), SELECT의 컬럼이 GROUP BY 키나 집계 함수인지, JOIN이 포함되어 있다면 집계가 부풀어질 가능성이 없는지. 이 세 가지만 체크해도 집계 오류의 대부분을 잡을 수 있다.

## 정리

GROUP BY와 집계 함수는 많은 행을 숫자로 바꾸는 핵심 도구다. AI가 만든 집계 쿼리는 숫자가 나와도 틀릴 수 있다. WHERE vs HAVING, NULL 처리, JOIN 후 카디널리티를 항상 의식하며 검토하는 습관이 바이브코딩의 데이터 품질을 결정한다.

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
- **바이브코딩을 위한 SQL 기초 (5/10): AI가 GROUP BY를 넣었는데 집계가 이상할 때 (현재 글)**
- [바이브코딩을 위한 SQL 기초 (6/10): AI가 서브쿼리를 중첩했다 — 읽기 어려운 쿼리 해석](./06-subquery.md)
- [바이브코딩을 위한 SQL 기초 (7/10): AI가 윈도우 함수를 썼는데 뭔지 모르겠다](./07-window-function.md)
- [바이브코딩을 위한 SQL 기초 (8/10): AI에게 데이터 수정 쿼리를 시킬 때 주의할 점](./08-insert-update-delete.md)
- [바이브코딩을 위한 SQL 기초 (9/10): AI가 만든 쿼리가 느릴 때 — 인덱스와 실행 계획](./09-index-and-query-plan.md)
- [바이브코딩을 위한 SQL 기초 (10/10): AI와 함께 실전 데이터 분석 SQL 짜기](./10-practical-analysis-sql.md)
<!-- toc:end -->
Tags: 바이브코딩, SQL, AI코딩, GROUP BY, 집계
