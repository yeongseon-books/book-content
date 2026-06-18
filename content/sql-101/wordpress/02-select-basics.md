---
title: "바이브코딩을 위한 SQL 기초 (2/10): AI가 만든 SELECT를 읽으려면 — 기본 조회"
series: sql-101
episode: 2
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- SQL
- AI코딩
seo_description: "바이브코딩 시대, AI가 생성한 SELECT 쿼리를 이해하고 검증하는 방법을 설명합니다. 컬럼 선택, 별칭, 정렬, LIMIT의 실무 감각을 익힙니다"
---

# 바이브코딩을 위한 SQL 기초 (2/10): AI가 만든 SELECT를 읽으려면 — 기본 조회

이 글은 바이브코딩을 위한 SQL 기초 시리즈의 2번째 글입니다.

"AI야, 최근 가입한 사용자 목록 뽑아줘."

AI가 아래 쿼리를 돌려줬다.

```sql
SELECT u.id, u.name AS user_name, u.email, u.signup_at AS joined_on
FROM users AS u
ORDER BY u.signup_at DESC
LIMIT 50;
```

이걸 읽을 수 있는가? 모든 줄이 무슨 뜻인지 바로 이해가 되는가? `AS`가 왜 붙었는지, `LIMIT 50`이 어디서 나왔는지, `ORDER BY u.signup_at DESC`가 없으면 어떻게 되는지 설명할 수 있는가?

바이브코딩에서 AI가 만든 SELECT를 그냥 복붙하는 것과, 읽고 이해한 뒤 실행하는 것은 완전히 다른 결과를 낳는다. 이해 없는 복붙은 조용히 틀린 결과를 낼 수 있고, 데이터가 많아지면 성능 문제로 이어진다.

이 글에서는 SELECT의 각 부분이 무슨 역할을 하는지, AI가 만든 SELECT를 어떻게 읽어야 하는지 정리한다.

> SELECT는 결과 집합의 모양을 설계하는 도구다. AI가 만들어줘도 그 모양이 내가 원하는 것인지는 내가 판단해야 한다.

---

## 이 글에서 다룰 문제
- SELECT 문장은 어떤 순서로 읽어야 할까요?
- AI가 `SELECT *`를 만들었을 때 그냥 써도 될까요?
- `AS` 별칭은 왜 붙이고 어디서 사용할 수 있을까요?
- `ORDER BY`가 없으면 결과 순서가 어떻게 될까요?
- `DISTINCT`는 언제 써야 하고 언제 쓰면 안 될까요?

AI가 만든 SELECT를 검토할 때 가장 먼저 봐야 할 것이 있다. 어떤 컬럼을 가져오는지, 어떤 순서로 정렬하는지, 몇 개를 가져오는지다. 이 세 가지를 이해하지 못하면 결과가 맞는지 판단할 수 없다.

## SELECT 평가 흐름

AI가 만든 쿼리를 읽을 때 헷갈리는 부분 중 하나가 실행 순서다. 쓰는 순서는 `SELECT ... FROM ... WHERE ...`이지만, 논리적 실행 순서는 다르다.

| 단계 | 절 | 역할 |
| --- | --- | --- |
| 1 | `FROM` | 어떤 테이블에서 데이터를 가져올지 |
| 2 | `WHERE` | 행을 필터링 (집계 전) |
| 3 | `GROUP BY` | 행을 그룹으로 묶음 |
| 4 | `HAVING` | 그룹 결과를 필터링 |
| 5 | `SELECT` | 표시할 열을 선택하고 별칭 부여 |
| 6 | `ORDER BY` | 결과를 정렬 |
| 7 | `LIMIT` / `OFFSET` | 결과 행 수 제한 |

이 순서를 알면 왜 `WHERE`에서 `SELECT`에서 정의한 별칭을 못 쓰는지 이해된다. `WHERE`는 `SELECT`보다 먼저 실행되어 별칭을 모르기 때문이다.

## AI가 만든 SELECT 읽는 법

### 컬럼 선택 — 뭘 가져오는지 확인하기

```sql
SELECT id, name, signup_at FROM users;
```

AI가 `SELECT *`를 만들었다면 다시 요청하라. 실서비스 테이블은 컬럼이 수십 개일 수 있다. 필요한 컬럼만 명시하는 것이 성능과 가독성 모두에 좋다.

### 별칭 — 왜 AS를 붙이는가

```sql
SELECT name AS user_name, signup_at AS joined_on FROM users;
```

`AS`는 컬럼 이름을 바꾸는 것이다. AI가 `AS`를 붙이는 이유는 결과를 읽는 사람 기준으로 이름을 정리하기 위해서다. 계산 컬럼이나 조인 결과에서는 특히 중요하다.

중요한 점: `ORDER BY`에서는 별칭을 쓸 수 있지만, `WHERE`에서는 쓸 수 없다.

### 정렬 — ORDER BY 없으면 어떻게 될까

```sql
SELECT id, name FROM users ORDER BY signup_at DESC;
```

`ORDER BY`가 없으면 결과 순서가 보장되지 않는다. AI가 만든 쿼리에 `ORDER BY`가 없다면, 순서가 중요한 쿼리인지 확인하라. 페이지네이션이나 최근 데이터를 보여주는 경우는 반드시 명시해야 한다.

### LIMIT — 몇 개를 가져오는가

```sql
SELECT id, name FROM users ORDER BY id LIMIT 10;
```

`LIMIT`가 없으면 전체 테이블을 읽는다. 개발 중에 실수로 수십만 건을 읽어버리는 상황을 막기 위해 탐색 쿼리에는 항상 `LIMIT`를 넣어라.

### DISTINCT — 왜 붙었을까

```sql
SELECT DISTINCT country FROM users;
```

`DISTINCT`는 중복을 제거하지만 비용이 있다. AI가 `DISTINCT`를 붙였다면 왜 중복이 생기는지 먼저 생각해보라. 중복의 원인이 잘못된 JOIN이라면 `DISTINCT`로 덮어두는 것보다 JOIN을 고치는 게 맞다.

## Before / After

**Before: AI가 만든 쿼리를 그냥 실행**
```sql
SELECT * FROM users ORDER BY id;
```
컬럼 30개 전체를 읽는다. 순서도 id 기준이라 최신 사용자가 아래에 있다.

**After: 의도에 맞게 수정 요청**
```sql
SELECT id, name, signup_at FROM users ORDER BY signup_at DESC LIMIT 20;
```
필요한 3개 컬럼만, 최신 가입자부터, 20명만 가져온다.

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
| --- | --- | --- |
| `SELECT *` 그대로 쓰기 | 불필요한 컬럼, 성능 저하 | AI에게 필요한 컬럼 명시 요청 |
| `ORDER BY` 없이 페이지네이션 | 순서가 매번 달라질 수 있음 | 정렬 기준 명시 필수 |
| 별칭을 `WHERE`에 쓰기 | 오류 발생 | `ORDER BY`에서만 별칭 사용 |
| `DISTINCT`로 중복 원인 숨기기 | 근본 문제가 남음 | JOIN 조건 재검토 |

## AI에게 SQL 요청하는 팁

- "필요한 컬럼만 가져와줘"를 항상 붙여라
- "최신 순으로 정렬해줘"처럼 정렬 의도를 명시하라
- "일단 10개만 가져와줘"로 먼저 소량 확인하라
- AI가 `DISTINCT`를 붙이면 왜 붙였는지 물어보라

## 운영 체크리스트
- [ ] `SELECT *` 없이 필요한 컬럼만 골라 쓸 수 있다
- [ ] 별칭이 어떤 상황에서 보이는지 설명할 수 있다
- [ ] `ORDER BY`와 `LIMIT`를 함께 고려하는 습관이 있다
- [ ] `DISTINCT`가 비용이 있는 연산이라는 점을 알고 있다
- [ ] 문장을 읽을 때 논리적 평가 순서를 떠올릴 수 있다

## 처음 질문으로 돌아가기

AI가 만든 SELECT를 읽을 때 세 가지를 먼저 본다. 어떤 컬럼을 가져오는지 (SELECT 절), 어떤 순서인지 (ORDER BY), 몇 개인지 (LIMIT). 이 세 가지가 내가 원하는 것과 맞는지 확인하는 것이 바이브코딩에서 SQL을 다루는 첫 번째 습관이다.

## 정리

SELECT의 핵심은 결과의 모양을 정확히 만드는 데 있다. 필요한 컬럼을 고르고, 읽기 쉬운 이름을 붙이고, 정렬과 제한을 명시하면 같은 데이터도 훨씬 다루기 쉬워진다. AI가 만들어준 SELECT가 이 기준을 충족하는지 검토하는 습관이 바이브코딩의 품질을 결정한다.

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
- **바이브코딩을 위한 SQL 기초 (2/10): AI가 만든 SELECT를 읽으려면 — 기본 조회 (현재 글)**
- [바이브코딩을 위한 SQL 기초 (3/10): AI가 WHERE 조건을 잘못 짰을 때](./03-where-and-conditions.md)
- [바이브코딩을 위한 SQL 기초 (4/10): AI가 JOIN을 썼는데 맞는지 확인하려면](./04-join.md)
- [바이브코딩을 위한 SQL 기초 (5/10): AI가 GROUP BY를 넣었는데 집계가 이상할 때](./05-group-by-and-aggregate.md)
- [바이브코딩을 위한 SQL 기초 (6/10): AI가 서브쿼리를 중첩했다 — 읽기 어려운 쿼리 해석](./06-subquery.md)
- [바이브코딩을 위한 SQL 기초 (7/10): AI가 윈도우 함수를 썼는데 뭔지 모르겠다](./07-window-function.md)
- [바이브코딩을 위한 SQL 기초 (8/10): AI에게 데이터 수정 쿼리를 시킬 때 주의할 점](./08-insert-update-delete.md)
- [바이브코딩을 위한 SQL 기초 (9/10): AI가 만든 쿼리가 느릴 때 — 인덱스와 실행 계획](./09-index-and-query-plan.md)
- [바이브코딩을 위한 SQL 기초 (10/10): AI와 함께 실전 데이터 분석 SQL 짜기](./10-practical-analysis-sql.md)
<!-- toc:end -->
Tags: 바이브코딩, SQL, AI코딩, SELECT, Query
