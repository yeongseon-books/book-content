---
series: sql-101
episode: 3
title: WHERE와 조건
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
  - WHERE
  - Filter
  - Database
  - "NULL"
seo_description: WHERE 조건식, AND/OR 우선순위, IN·BETWEEN·LIKE, NULL 비교의 핵심을 정리합니다
last_reviewed: '2026-05-15'
---

# WHERE와 조건

데이터를 조회할 때 대부분의 비용과 정확도는 조건절에서 갈립니다. 어떤 행을 남기고 어떤 행을 버릴지 결정하는 문장이 바로 `WHERE`이기 때문입니다. SQL을 처음 배울 때는 비교 연산자만 외우고 넘어가기 쉽지만, 실무에서는 `NULL`, 우선순위, 인덱스 사용 여부까지 함께 봐야 합니다.

이 글은 SQL 101 시리즈의 세 번째 글입니다. 여기서는 `WHERE`를 단순한 필터가 아니라, 결과의 정확도와 성능을 동시에 좌우하는 문장으로 설명합니다.

## 이 글에서 다룰 문제

- 비교 연산자와 조건식은 어떻게 읽어야 할까요?
- `AND`와 `OR`의 우선순위는 왜 자주 문제를 만들까요?
- `IN`, `BETWEEN`, `LIKE`는 각각 어떤 상황에 어울릴까요?
- `NULL` 비교는 왜 일반 값 비교와 다를까요?
- 조건식 모양이 인덱스 사용 여부를 어떻게 바꿀까요?

> WHERE는 데이터의 입구입니다. 어떤 행을 정확히 통과시키고 정확히 막을지 여기서 결정됩니다.

## 왜 중요한가

비용 관점에서 보면 `WHERE` 한 줄이 쿼리 전체의 분위기를 결정합니다. 조건이 잘 설계되면 적은 행만 읽고 끝납니다. 반대로 조건이 흐릿하거나 인덱스를 타지 못하는 형태면 전체 테이블을 훑게 됩니다.

정확도 관점에서도 마찬가지입니다. `NULL`을 잘못 비교하거나 `AND`와 `OR`의 괄호를 빠뜨리면, 쿼리는 빠르게 실행되더라도 잘못된 답을 줄 수 있습니다. 실무에서 더 무서운 것은 느린 쿼리보다 틀린 결과를 조용히 내는 쿼리입니다.

## WHERE 평가 흐름

![WHERE 평가 흐름](https://yeongseon-books.github.io/book-public-assets/assets/sql-101/03/03-01-where-evaluation-flow.ko.png)
모든 행이 일단 후보로 들어오고, `WHERE` 조건식을 평가한 뒤 참인 행만 다음 단계로 넘어갑니다. 거짓뿐 아니라 `NULL` 결과도 통과하지 못한다는 점이 중요합니다. 이 세 값 논리가 `= NULL` 실수를 낳는 원인입니다.

## 핵심 개념 정리

### 조건식은 참과 거짓만 있는 것이 아니다

SQL은 보통 세 값 논리로 동작합니다. 결과는 참, 거짓, 그리고 `NULL`일 수 있습니다. `NULL`은 모른다는 뜻이므로, 비교 결과도 종종 모름이 됩니다. 그래서 `deleted_at = NULL`처럼 쓰면 기대와 달리 행이 잡히지 않습니다.

### 우선순위는 괄호로 명시하는 편이 안전하다

`AND`는 `OR`보다 먼저 결합합니다. 이 규칙을 기억하고 있어도, 긴 쿼리에서는 괄호로 의도를 드러내는 편이 낫습니다. 기계는 규칙대로 읽지만, 사람은 의도대로 읽고 싶어 하기 때문입니다.

### 인덱스를 잘 타는 조건식은 모양이 다르다

컬럼에 함수를 감싸거나 타입이 다른 값을 비교하면 인덱스 활용이 어려워질 수 있습니다. 같은 의미라도 데이터베이스가 쉽게 탐색할 수 있는 형태로 쓰는 것이 중요합니다.

## 다섯 가지 조건 패턴

### 1단계 — 비교 연산

```sql
SELECT * FROM users WHERE age >= 18;
```

가장 기본적인 형태입니다. 숫자, 날짜, 문자열 모두 이런 비교 연산을 중심으로 필터링합니다.

### 2단계 — 범위 조건

```sql
SELECT * FROM orders WHERE total BETWEEN 100 AND 500;
```

`BETWEEN`은 범위를 읽기 좋게 표현합니다. 다만 경계값이 포함된다는 점을 알고 써야 합니다.

### 3단계 — 목록 포함 여부

```sql
SELECT * FROM users WHERE country IN ('KR', 'JP', 'US');
```

조건 값이 몇 개 안 될 때는 `IN`이 읽기 쉽습니다. 목록이 지나치게 길어지면 별도 테이블과 조인하는 편이 더 낫습니다.

### 4단계 — 패턴 매칭

```sql
SELECT * FROM users WHERE email LIKE '%@example.com';
```

문자열 패턴을 찾을 때는 `LIKE`를 씁니다. 다만 와일드카드가 앞에 오면 인덱스를 쓰기 어려워져 비용이 커질 수 있습니다.

### 5단계 — NULL 확인

```sql
SELECT * FROM users WHERE deleted_at IS NULL;
```

**Expected output:**

| id | name | deleted_at |
| --- | --- | --- |
| 1 | Ada | NULL |
| 2 | Linus | NULL |

`NULL`은 `IS NULL`, `IS NOT NULL`로 다뤄야 합니다. 입문 단계에서 가장 먼저 몸에 익혀야 할 규칙 중 하나입니다.

## 이 코드에서 먼저 봐야 할 점

- `LIKE '%xxx'` 형태는 보통 인덱스를 잘 활용하지 못합니다.
- `IN`은 작은 목록에는 좋지만, 긴 목록을 무작정 넣는 방식은 오래 버티기 어렵습니다.
- `NULL` 비교는 `=`가 아니라 `IS NULL`로 써야 합니다.

이 세 가지는 문법 지식으로 끝나지 않습니다. 실제로 느린 쿼리와 잘못된 결과의 상당수가 여기서 나옵니다.

## 실무에서 자주 헷갈리는 지점

### `= NULL`이 왜 항상 문제일까

`NULL`은 값이 비어 있다는 뜻이 아니라 값을 모른다는 뜻에 가깝습니다. 그래서 `= NULL`은 참이 아니라 모름으로 평가되고, `WHERE`에서는 통과하지 못합니다. 삭제되지 않은 행을 찾을 때 `deleted_at = NULL`이라고 쓰면 결과가 비어 버리는 이유가 여기에 있습니다.

### 컬럼에 함수를 감싸면 왜 위험할까

예를 들어 `WHERE LOWER(email) = 'a@b.com'`처럼 쓰면 의미는 명확해 보입니다. 하지만 많은 데이터베이스에서는 이렇게 컬럼에 함수를 감싸는 순간 일반 인덱스를 활용하기 어렵습니다. 가능하면 저장 값과 비교 값을 같은 형태로 맞추거나, 정말 필요하면 함수 인덱스를 별도로 고려해야 합니다.

### 타입이 다르면 조용히 비싸질 수 있다

숫자 컬럼에 문자열을 비교하는 식의 암시적 변환은 문법 오류 없이 지나갈 수 있습니다. 문제는 데이터베이스가 내부에서 변환 작업을 하면서 인덱스 활용이 약해질 수 있다는 점입니다. 타입 일치는 성능과 정확도 모두에 영향을 줍니다.

## 체크리스트

- [ ] `IS NULL`과 `= NULL`의 차이를 설명할 수 있다.
- [ ] `AND`와 `OR`가 섞이면 괄호를 먼저 떠올린다.
- [ ] `LIKE` 패턴이 언제 비싸지는지 알고 있다.
- [ ] 컬럼에 함수를 감싸는 조건이 왜 조심스러운지 안다.
- [ ] 조건식이 인덱스 사용 여부에 영향을 준다는 점을 이해하고 있다.

## 정리

`WHERE`는 단순한 필터가 아니라 정확도와 성능의 기준점입니다. 참과 거짓만이 아니라 `NULL`까지 포함한 세 값 논리를 이해해야 하고, 사람이 읽기 쉬운 괄호와 데이터베이스가 처리하기 쉬운 조건식 모양을 함께 고려해야 합니다.

다음 글에서는 여러 테이블을 연결하는 `JOIN`을 다루며, 결과가 왜 갑자기 불어나는지와 카디널리티를 어떻게 읽어야 하는지 정리하겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [SQL이란 무엇인가?](./01-what-is-sql.md)
- [SELECT 기본](./02-select-basics.md)
- **WHERE와 조건 (현재 글)**
- JOIN 이해하기 (예정)
- GROUP BY와 집계 함수 (예정)
- 서브쿼리와 CTE (예정)
- 윈도 함수 (예정)
- 데이터를 바꾸는 SQL — INSERT, UPDATE, DELETE (예정)
- 인덱스와 쿼리 계획 (예정)
- 실전 분석 SQL (예정)

<!-- toc:end -->

## 참고 자료

- [PostgreSQL — WHERE clause](https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-WHERE)
- [PostgreSQL — Pattern Matching](https://www.postgresql.org/docs/current/functions-matching.html)
- [Use The Index, Luke — Where Clause](https://use-the-index-luke.com/sql/where-clause)
- [Mode — WHERE](https://mode.com/sql-tutorial/sql-where/)

Tags: SQL, Database, Postgres, Analytics
