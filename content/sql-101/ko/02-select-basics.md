---
series: sql-101
episode: 2
title: "SQL 101 (2/10): SELECT 기본"
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
  - SELECT
  - Query
  - Database
  - Postgres
seo_description: SELECT 절의 흐름, 컬럼 선택, 별칭, 정렬, LIMIT와 DISTINCT의 실무 감각을 정리합니다
last_reviewed: '2026-05-15'
---

# SQL 101 (2/10): SELECT 기본

SELECT는 가장 자주 쓰는 SQL 문장입니다. 그래서 익숙하다는 이유로 대충 쓰기 쉽습니다. 하지만 실무에서는 바로 이 문장에서 비용, 가독성, 유지보수성이 크게 갈립니다. 같은 데이터를 읽더라도 필요한 컬럼만 고르고, 의미 있는 별칭을 붙이고, 정렬과 제한을 명시하는 습관이 팀 전체의 쿼리 품질을 바꿉니다.

이 글은 SQL 101 시리즈의 두 번째 글입니다. 여기서는 SELECT를 한 줄짜리 조회 문장이 아니라, 결과 집합의 모양을 설계하는 기본 도구로 정리합니다.

## 먼저 던지는 질문

- SELECT 문장은 어떤 순서로 읽어야 할까요?
- 컬럼을 명시하는 습관은 왜 중요할까요?
- 별칭은 어디까지 보이고 어디에서는 안 보일까요?

## 큰 그림

![SQL 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/sql-101/02/02-01-select-evaluation-flow.ko.png)

*SQL 101 2장 흐름 개요*

SELECT이 다른 절단 지나면 진짜 모든 데이터를 가져올 주는 게 아니라 지금 이 주문에 실제로 필요한 데이터만 루는 도구입니다.

> SELECT는 결과 집합의 모양을 설계하는 기본 도구입니다. 한두 줄의 데이터도 엄을 명시하고, 단순 가능한 연산과 마음가지 단정하는 습관이 팀 전체의 쿼리 품질을 바꿀 담니다.

## 왜 중요한가

분석 환경에서는 하루에도 수십, 수백 번 SELECT를 작성합니다. 백엔드 코드 뒤에서도 ORM이 결국 SELECT를 만들어 냅니다. 이때 읽기 쉬운 SELECT는 리뷰 속도를 올리고, 잘못된 SELECT는 눈치채기 어려운 비용을 누적시킵니다.

특히 컬럼을 명시하는 습관은 몇 달 뒤의 팀원을 돕습니다. 어떤 열이 정말 필요한지 문장 안에 드러나기 때문입니다. 반대로 `SELECT *`가 남발된 쿼리는 처음에는 편해 보여도, 테이블 구조가 바뀌는 순간 예상치 못한 성능 문제와 해석 혼선을 만들기 쉽습니다.

## SELECT 평가 흐름

문장을 쓰는 순서는 `SELECT ... FROM ... WHERE ...`이지만, 논리적으로는 보통 `FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT` 순서로 이해하면 읽기 쉽습니다. 이 감각이 있어야 왜 별칭이 `WHERE`에서는 안 보이고 `ORDER BY`에서는 보이는지 같은 규칙도 자연스럽게 이해됩니다.

## 핵심 개념 정리

### 프로젝션은 필요한 열만 고르는 일이다

SELECT에서 가장 먼저 해야 할 일은 필요한 열만 고르는 것입니다. 이 작업을 프로젝션이라고 부릅니다. 데이터베이스가 가진 정보 전체를 가져오는 것이 아니라, 지금 이 질문에 필요한 열만 남기는 일입니다.

### 별칭은 읽기 비용을 줄이는 장치다

`AS`로 붙이는 별칭은 짧은 장식이 아니라 결과를 이해하기 쉽게 만드는 장치입니다. 특히 여러 테이블을 조인하거나 계산 열이 섞이는 쿼리에서는 별칭이 없으면 결과 해석이 어려워집니다.

### 정렬과 제한은 화면 친화적인 기본 습관이다

분석 도구나 콘솔에서 큰 테이블을 바로 읽을 때는 `ORDER BY`와 `LIMIT`를 함께 생각하는 편이 안전합니다. 정렬 기준이 없으면 결과 순서는 예측하기 어렵고, 제한이 없으면 필요 이상으로 많은 행을 읽게 됩니다.

## 자주 반복하는 다섯 가지 패턴

### 1단계 — 필요한 컬럼만 적기

```sql
SELECT id, name, signup_at FROM users;
```

가장 기본이면서 가장 중요한 습관입니다. 지금 필요한 정보가 세 열이라면 세 열만 적습니다. 이 습관 하나로 쿼리 의도가 또렷해집니다.

### 2단계 — 별칭으로 결과 이름 정리하기

```sql
SELECT name AS user_name, signup_at AS joined_on FROM users;
```

원본 컬럼명이 항상 결과 표현에 적합한 것은 아닙니다. 결과를 읽는 사람 기준으로 이름을 정리하면 대시보드나 후속 쿼리에서도 해석이 쉬워집니다.

### 3단계 — 정렬 기준 명시하기

```sql
SELECT id, name FROM users ORDER BY signup_at DESC;
```

가장 최근 가입자부터 보고 싶다면 그 의도를 정렬로 드러냅니다. 정렬을 빼면 데이터베이스가 어떤 순서로 결과를 내놓을지 보장되지 않습니다.

### 4단계 — 상위 몇 개만 먼저 보기

```sql
SELECT id, name FROM users ORDER BY id LIMIT 10;
```

**Expected output:**

| id | name |
| --- | --- |
| 1 | Ada |
| 2 | Linus |
| 3 | Grace |

큰 테이블을 분석할 때는 전부 읽기보다 작은 샘플부터 보는 편이 좋습니다. `LIMIT`는 화면에 맞는 첫 샘플을 만들 때 특히 유용합니다.

### 5단계 — 중복 제거가 정말 필요한지 판단하기

```sql
SELECT DISTINCT country FROM users;
```

`DISTINCT`는 중복 제거를 해 주지만 공짜는 아닙니다. 정렬이나 해시 작업이 뒤따를 수 있어서 비용이 생깁니다. 따라서 중복 제거가 필요한 이유를 먼저 분명히 해야 합니다.

## 이 코드에서 먼저 봐야 할 점

- SELECT를 작성하는 순서와 엔진이 논리적으로 평가하는 순서는 다릅니다.
- 별칭은 `WHERE`에서는 보이지 않지만 `ORDER BY`에서는 활용할 수 있습니다.
- `DISTINCT`는 결과를 예쁘게 만드는 장치가 아니라, 비용이 있는 연산입니다.

입문 단계에서 SELECT를 잘 쓴다는 말은 문법을 외운다는 뜻이 아닙니다. 결과 열이 왜 이 이름인지, 왜 이 순서로 정렬했는지, 왜 이 정도 행만 먼저 보는지 설명할 수 있다는 뜻에 가깝습니다.

## SELECT 절 실행 순서

SQL 문장을 작성하는 순서와 데이터베이스 엔진이 논리적으로 평가하는 순서는 다릅니다. 이 차이를 이해하면 별칭이 어느 단계에서 보이고, `WHERE`에서는 왜 쓸 수 없는지 같은 규칙이 자연스럽게 이해됩니다.

| 단계 | 절 | 역할 |
| --- | --- | --- |
| 1 | `FROM` | 어떤 테이블에서 데이터를 가져올지 결정 |
| 2 | `WHERE` | 행을 필터링 (집계 전 조건) |
| 3 | `GROUP BY` | 행을 그룹으로 묶음 |
| 4 | `HAVING` | 그룹 결과를 필터링 |
| 5 | `SELECT` | 표시할 열을 선택하고 별칭 부여 |
| 6 | `ORDER BY` | 결과를 정렬 |
| 7 | `LIMIT` / `OFFSET` | 결과 행 수 제한 |

이 순서를 알면 왜 `WHERE`에서는 `SELECT`에서 정의한 별칭을 못 쓰는지, 그런데 `ORDER BY`에서는 왜 별칭을 쓸 수 있는지가 명확해집니다. `WHERE`는 `SELECT`보다 먼저 실행되어 별칭을 모르고, `ORDER BY`는 나중에 실행되어 별칭을 알 수 있기 때문입니다.

## DISTINCT, LIMIT, OFFSET 예제 모음

### DISTINCT로 중복 제거

```sql
-- 국가 목록을 중복 없이 가져오기
SELECT DISTINCT country FROM users;
```

`DISTINCT`는 결과에서 중복된 행을 제거합니다. 단, 내부적으로 정렬이나 해시 작업이 발생할 수 있어 비용이 있다는 점을 기억해야 합니다. 중복이 왜 생기는지 먼저 파악하는 것이 더 중요합니다.

### LIMIT으로 결과 수 제한

```sql
-- 처음 5명만 가져오기
SELECT name, signup_at FROM users ORDER BY signup_at LIMIT 5;
```

큰 테이블을 탐색할 때는 전체를 다 읽기보다 작은 샘플부터 보는 편이 안전합니다. `LIMIT`는 결과의 행 수를 제한하는 가장 기본적인 도구입니다.

### OFFSET으로 시작 위치 조절

```sql
-- 5번째 행부터 10개만 가져오기
SELECT id, name FROM users ORDER BY id LIMIT 10 OFFSET 5;
```

`OFFSET`은 시작 위치를 건너뛀는 데 쓰입니다. 페이지네이션을 구현할 때 자주 나오는 패턴입니다. 단, 큰 OFFSET은 여전히 앞쪽 행을 훈고 건너뛰어야 하므로 비용이 생길 수 있습니다.

### DISTINCT와 ORDER BY 함께 쓰기

```sql
-- 국가 목록을 중복 없이, 알파벳 순서로
SELECT DISTINCT country FROM users ORDER BY country;
```

중복을 제거하고 나서 정렬하는 패턴도 가능합니다. 단, `ORDER BY`에 쓰는 열은 `SELECT`에 포함되어 있어야 합니다.

## 별칭(AS) 활용 패턴

별칭은 결과를 읽기 쉬게 만드는 도구입니다. 단순히 이름을 바꾸는 것을 넘어, 후속 쿼리나 대시보드에서 해석을 돕는 핵심 수단입니다.

### 계산 열에 별칭 붙이기

```sql
SELECT 
    name,
    EXTRACT(YEAR FROM signup_at) AS signup_year,
    CURRENT_DATE - signup_at AS days_since_signup
FROM users;
```

계산된 열에는 별칭이 특히 중요합니다. 별칭 없이 결과를 보면 `EXTRACT(YEAR FROM signup_at)` 같은 식이 그대로 컴럼명으로 나와 해석이 어렵습니다.

### 테이블 별칭 활용

```sql
SELECT u.name, u.email
FROM users AS u
WHERE u.signup_at >= '2026-01-01';
```

테이블 이름이 길 때는 짧은 별칭을 붙여서 매번 긴 이름을 반복하지 않아도 됩니다. 특히 조인을 쓸 때 테이블 별칭은 가독성을 크게 높여 줍니다.

### 별칭을 ORDER BY에 활용

```sql
SELECT 
    name,
    signup_at AS joined
FROM users
ORDER BY joined DESC;
```

`ORDER BY`는 `SELECT`보다 나중에 평가되기 때문에, `SELECT`에서 정의한 별칭을 그대로 쓸 수 있습니다. 이렇게 하면 같은 열 이름을 두 번 반복하지 않아도 되어 코드가 짧아집니다.

### 별칭은 WHERE에서 보이지 않는다

```sql
-- 이 쿼리는 오류를 냅니다
-- SELECT name, signup_at AS joined
-- FROM users
-- WHERE joined >= '2026-02-01';

-- 대신 이렇게 써야 합니다
SELECT name, signup_at AS joined
FROM users
WHERE signup_at >= '2026-02-01';
```

`WHERE`는 `SELECT`보다 먼저 평가되므로, `SELECT`에서 정의한 별칭을 쓸 수 없습니다. 이 규칙을 모르고 별칭을 쓰면 오류가 발생합니다.
## 실무에서 자주 헷갈리는 지점

### `SELECT *`는 왜 반사적으로 쓰면 안 될까

작은 예제에서는 편하지만, 실제 서비스 테이블은 컬럼 수가 많습니다. 사용하지도 않는 텍스트 컬럼, JSON 컬럼, 큰 메타데이터 컬럼까지 한꺼번에 가져오면 네트워크와 메모리 부담이 커집니다. 인덱스만으로 답할 수 있는 쿼리도 불필요한 열 때문에 테이블 접근이 필요해질 수 있습니다.

### `ORDER BY 1`은 왜 읽기 어려울까

컬럼 위치로 정렬하면 처음에는 짧아 보입니다. 하지만 SELECT 목록이 바뀌는 순간 정렬 의미도 함께 흔들립니다. 실무에서는 컬럼 이름을 직접 쓰는 편이 훨씬 명확합니다.

### `DISTINCT`는 중복의 원인을 숨길 수 있다

조인 때문에 중복이 생겼는데 `DISTINCT`로 일단 지워 버리면, 왜 중복이 생겼는지 놓치기 쉽습니다. 중복 제거는 결과를 다듬는 도구이지, 데이터 모델 문제를 덮는 도구가 아닙니다.

## 체크리스트

- [ ] `SELECT *` 없이 필요한 컬럼만 골라 쓸 수 있다.
- [ ] 별칭이 어떤 상황에서 보이는지 설명할 수 있다.
- [ ] `ORDER BY`와 `LIMIT`를 함께 고려하는 습관이 있다.
- [ ] `DISTINCT`가 비용이 있는 연산이라는 점을 알고 있다.
- [ ] 문장을 읽을 때 논리적 평가 순서를 떠올릴 수 있다.

## 정리

SELECT의 핵심은 문장의 모양을 정확히 만드는 데 있습니다. 필요한 컬럼을 고르고, 읽기 쉬운 이름을 붙이고, 정렬과 제한을 명시하면 같은 데이터도 훨씬 다루기 쉬워집니다. 작은 습관처럼 보여도 이런 문장들이 쌓이면 팀의 분석 속도와 리뷰 품질이 달라집니다.

다음 글에서는 행을 걸러 내는 기준인 `WHERE`와 조건식을 집중해서 보겠습니다.

## 실무에서 SELECT를 잘 쓰는 법

실무 SQL에서 SELECT는 단순한 조회를 넘어 팀의 데이터 작업 품질을 결정합니다. 다음은 실무에서 자주 쓰는 패턴들입니다.

### 필요한 컴럼만 명시하기

API 백엔드나 대시보드 쿼리에서는 필요한 컴럼만 골라야 합니다. 사용하지 않는 데이터를 가져오면 네트워크 비용과 메모리 사용량이 커집니다.

### 정렬 기준을 항상 명시하기

정렬 없이 결과를 반환하면 순서가 보장되지 않습니다. 특히 페이지네이션이나 최근 데이터를 보여 주는 경우에는 항상 `ORDER BY`를 명시해야 합니다.

### 별칭으로 가독성 높이기

계산 열이나 조인 결과에는 의미 있는 별칭을 붙여야 합니다. 코드 리뷰와 유지보수가 훨씬 쉬워집니다.

### LIMIT로 안전 장치 걸기

큰 테이블을 탐색할 때는 항상 `LIMIT`를 고려하세요. 특히 개발 환경에서 전체 테이블을 읽는 실수를 방지할 수 있습니다.

## SELECT 작성 모범 사례

실무에서 SELECT를 작성할 때 자주 마주치는 패턴을 좋은 예와 피할 예로 비교해 보겠습니다.

### 컴럼 선택

```sql
-- 좋은 예: 필요한 컴럼만 명시
SELECT id, name, email, created_at FROM users;

-- 피할 예: 전체 컴럼 가져오기
-- SELECT * FROM users;
```

### 별칭 사용

```sql
-- 좋은 예: 의미 있는 별칭
SELECT 
    u.name AS user_name,
    COUNT(o.id) AS order_count,
    SUM(o.total) AS total_spent
FROM users u
JOIN orders o ON o.user_id = u.id
GROUP BY u.id, u.name;

-- 피할 예: 별칭 없이 복잡한 식
-- SELECT u.name, COUNT(o.id), SUM(o.total)
-- FROM users u JOIN orders o ON o.user_id = u.id
-- GROUP BY u.id, u.name;
```

### 정렬과 제한

```sql
-- 좋은 예: 정렬 기준과 제한 명시
SELECT name, signup_at FROM users
ORDER BY signup_at DESC
LIMIT 10;

-- 피할 예: 정렬 없이 LIMIT
-- SELECT name, signup_at FROM users LIMIT 10;
```

### 여러 줄로 가독성 향상

```sql
-- 좋은 예: 컴럼을 여러 줄로 나눠 쓰기
SELECT 
    u.id,
    u.name,
    u.email,
    u.country,
    COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.deleted_at IS NULL
GROUP BY u.id, u.name, u.email, u.country
HAVING COUNT(o.id) > 0
ORDER BY order_count DESC
LIMIT 100;

-- 피할 예: 한 줄로 긴 쿼리
-- SELECT u.id, u.name, u.email, u.country, COUNT(o.id) AS order_count FROM users u LEFT JOIN orders o ON o.user_id = u.id WHERE u.deleted_at IS NULL GROUP BY u.id, u.name, u.email, u.country HAVING COUNT(o.id) > 0 ORDER BY order_count DESC LIMIT 100;
```

여러 줄로 나누면 각 절의 역할이 명확해지고, 코드 리뷰와 디버그가 쉬워집니다.
## 처음 질문으로 돌아가기

- **SELECT 문장은 어떤 순서로 읽어야 할까요?**
  - SELECT 문장은 쓰는 순서랗지만, 데이터베이스 엔진은 FROM → WHERE → SELECT → ORDER BY → LIMIT 순서로 단답니다.
- **컬럼을 명시하는 습관은 왜 중요할까요?**
  - 컬럼을 명시하는 습관은 짧은 두 줄을 단른다는 의차를 누마 스는닌다. 이는 직접 단른 집합과 데이터 단라연을 렌다는 뻣니다.
- **별칭은 어디까지 보이고 어디에서는 안 보일까요?**
  - WHERE를 단모 동연을 개스니다. 동약을 메일 다음 앞에서도 동약의 간단한 머를 비주는 동기단서를 면다 다른 것도 니무다는 뻔 공닝긴.

<!-- toc:begin -->
## 시리즈 목차

- [SQL 101 (1/10): SQL이란 무엇인가?](./01-what-is-sql.md)
- **SELECT 기본 (현재 글)**
- WHERE와 조건 (예정)
- JOIN 이해하기 (예정)
- GROUP BY와 집계 함수 (예정)
- 서브쿼리와 CTE (예정)
- 윈도 함수 (예정)
- 데이터를 바꾸는 SQL — INSERT, UPDATE, DELETE (예정)
- 인덱스와 쿼리 계획 (예정)
- 실전 분석 SQL (예정)

<!-- toc:end -->

## 참고 자료

- [PostgreSQL — SELECT](https://www.postgresql.org/docs/current/sql-select.html)
- [SQLBolt — SELECT queries](https://sqlbolt.com/lesson/select_queries_introduction)
- [Mode — SELECT statement](https://mode.com/sql-tutorial/sql-select-statement/)
- [SQL Style Guide](https://www.sqlstyle.guide/)

Tags: SQL, Database, Postgres, Analytics
