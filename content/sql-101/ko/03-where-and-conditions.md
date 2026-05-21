---
series: sql-101
episode: 3
title: "SQL 101 (3/10): WHERE와 조건"
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

# SQL 101 (3/10): WHERE와 조건

데이터를 조회할 때 대부분의 비용과 정확도는 조건절에서 갈립니다. 어떤 행을 남기고 어떤 행을 버릴지 결정하는 문장이 바로 `WHERE`이기 때문입니다. SQL을 처음 배울 때는 비교 연산자만 외우고 넘어가기 쉽지만, 실무에서는 `NULL`, 우선순위, 인덱스 사용 여부까지 함께 봐야 합니다.

이 글은 SQL 101 시리즈의 세 번째 글입니다. 여기서는 `WHERE`를 단순한 필터가 아니라, 결과의 정확도와 성능을 동시에 좌우하는 문장으로 설명합니다.

## 먼저 던지는 질문

- 비교 연산자와 조건식은 어떻게 읽어야 할까요?
- `AND`와 `OR`의 우선순위는 왜 자주 문제를 만들까요?
- `IN`, `BETWEEN`, `LIKE`는 각각 어떤 상황에 어울릴까요?

## 큰 그림

![SQL 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/sql-101/03/03-01-where-evaluation-flow.ko.png)

*SQL 101 3장 흐름 개요*

이 그림에서 WHERE가 데이터 흐름에서 어느 단계에 배치되는지 봅니다. 핵심은 조건식이 행을 어떻게 필터링하고, 그 필터링이 성능과 정확성에 미치는 영향을 이해하는 것입니다.

> WHERE의 핵심은 조건식의 문법이 아니라, 어떤 조건으로 어떤 행을 선택하는지 명확히 정의하고, 그 선택이 데이터베이스 성능에 어떻게 영향을 미치는지 아는 데 있습니다.

## 왜 중요한가

비용 관점에서 보면 `WHERE` 한 줄이 쿼리 전체의 분위기를 결정합니다. 조건이 잘 설계되면 적은 행만 읽고 끝납니다. 반대로 조건이 흐릿하거나 인덱스를 타지 못하는 형태면 전체 테이블을 훑게 됩니다.

정확도 관점에서도 마찬가지입니다. `NULL`을 잘못 비교하거나 `AND`와 `OR`의 괄호를 빠뜨리면, 쿼리는 빠르게 실행되더라도 잘못된 답을 줄 수 있습니다. 실무에서 더 무서운 것은 느린 쿼리보다 틀린 결과를 조용히 내는 쿼리입니다.

## WHERE 평가 흐름

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

## 비교 연산자와 논리 연산자 우선순위

조건식을 정확하게 작성하려면 연산자의 우선순위를 알아야 합니다. 다음 표는 SQL에서 자주 쓰는 비교 연산자와 논리 연산자를 우선순위 순서대로 정리한 것입니다.

| 우선순위 | 연산자 | 설명 |
| --- | --- | --- |
| 1 | `()` | 괄호 — 가장 먼저 평가 |
| 2 | `NOT` | 논리 부정 |
| 3 | 비교 연산자 | `=`, `<>`, `>`, `<`, `>=`, `<=`, `BETWEEN`, `IN`, `LIKE`, `IS NULL` |
| 4 | `AND` | 논리적 AND |
| 5 | `OR` | 논리적 OR |

`AND`가 `OR`보다 먼저 결합하므로, 복잡한 조건식에서는 괄호로 의도를 명확히 하는 편이 안전합니다. 예를 들어 `A OR B AND C`는 `A OR (B AND C)`로 해석됩니다.

```sql
-- 괄호 없이 쓰면 예상과 다를 수 있습니다
SELECT * FROM users
WHERE country = 'US' OR country = 'UK' AND age >= 18;

-- 의도를 명확히 하려면 괄호를 쓰세요
SELECT * FROM users
WHERE (country = 'US' OR country = 'UK') AND age >= 18;
```

쪰 번째 쿼리는 `country = 'UK' AND age >= 18`을 먼저 평가하고, 그 결과를 `country = 'US'`와 OR로 합칩니다. 두 번째 쿼리는 국가 조건을 먼저 모으고, 그 결과를 나이 조건과 AND로 결합합니다. 의도가 완전히 다릅니다.

## BETWEEN, IN, LIKE, IS NULL 예제 모음

### BETWEEN으로 범위 필터링

```sql
-- 나이가 18세 이상 30세 이하
SELECT name, age FROM users WHERE age BETWEEN 18 AND 30;

-- 날짜 범위
SELECT * FROM orders WHERE order_date BETWEEN '2026-01-01' AND '2026-01-31';
```

`BETWEEN`은 양 끝을 포함하는 범위 조건입니다. `age >= 18 AND age <= 30`과 같은 의미이지만, 읽기 더 쉬습니다.

### IN으로 목록 매칭

```sql
-- 국가가 US, UK, FR 중 하나
SELECT * FROM users WHERE country IN ('US', 'UK', 'FR');

-- 순자 목록
SELECT * FROM users WHERE id IN (1, 3, 5, 7);
```

`IN`은 여러 개의 `OR` 조건을 간결하게 만들어 줍니다. `country = 'US' OR country = 'UK' OR country = 'FR'`을 한 줄로 표현할 수 있습니다.

### LIKE로 패턴 검색

```sql
-- 이메일이 example.com으로 끝나는 사용자
SELECT * FROM users WHERE email LIKE '%@example.com';

-- 이름이 A로 시작
SELECT * FROM users WHERE name LIKE 'A%';

-- 이름에 'in'이 포함
SELECT * FROM users WHERE name LIKE '%in%';
```

`LIKE`는 문자열 패턴을 찾을 때 쓰입니다. `%`는 0개 이상의 문자, `_`는 정확히 1개의 문자를 나타냅니다. 단, 와일드카드가 앞에 오면 (`%xxx`) 인덱스를 쓰기 어려워 비용이 커질 수 있습니다.

### IS NULL로 NULL 검사

```sql
-- 삭제되지 않은 사용자
SELECT * FROM users WHERE deleted_at IS NULL;

-- 삭제된 사용자
SELECT * FROM users WHERE deleted_at IS NOT NULL;

-- 생년월일이 비어 있는 행
SELECT * FROM users WHERE birth_date IS NULL;
```

`NULL`은 값이 없다거나 알 수 없다는 특별한 상태이므로, `= NULL`이 아니라 `IS NULL`로 비교해야 합니다. `= NULL`은 항상 모름으로 평가되어 결과를 반환하지 않습니다.

### 여러 조건 조합 예제

```sql
-- 미국 또는 영국 사용자 중 성인
SELECT * FROM users
WHERE (country = 'US' OR country = 'UK') AND age >= 18;

-- 이메일이 있고, 삭제되지 않은 활성 사용자
SELECT * FROM users
WHERE email IS NOT NULL AND deleted_at IS NULL;

-- 주문 금액이 100 이상 500 이하, 상태가 'paid' 또는 'shipped'
SELECT * FROM orders
WHERE total BETWEEN 100 AND 500
  AND status IN ('paid', 'shipped');
```

실무에서는 여러 조건을 조합하는 경우가 대부분입니다. 이때 괄호로 의도를 명확히 하고, 각 조건이 무엇을 걸러내는지 주석이나 부연 설명으로 남겨 두면 다른 사람이 읽기 쉬워집니다.

## 인덱스와 WHERE 조건 순서

인덱스는 특정 열의 값을 빠르게 찾기 위해 데이터베이스가 내부에 만들어 두는 보조 자료 구조입니다. `WHERE` 조건을 쓸 때 인덱스가 있는 열을 먼저 쓰면 데이터베이스가 훨씬 빠르게 행을 찾을 수 있습니다.

### 인덱스를 타는 조건

```sql
-- user_id에 인덱스가 있다고 가정
CREATE INDEX idx_user_id ON orders(user_id);

-- 인덱스를 활용할 수 있는 조건
SELECT * FROM orders WHERE user_id = 123;
```

이 쿼리는 `user_id` 인덱스를 통해 빠르게 실행됩니다. 데이터베이스는 전체 테이블을 읽지 않고, 인덱스를 통해 해당 행만 바로 찾습니다.

### 인덱스를 못 타는 조건

```sql
-- 컴럼에 함수를 감싸면 인덱스 활용이 어려움
SELECT * FROM orders WHERE YEAR(order_date) = 2026;

-- 대신 이렇게 쓰는 편이 낫습니다
SELECT * FROM orders
WHERE order_date >= '2026-01-01' AND order_date < '2027-01-01';
```

컴럼에 함수를 감싸면 데이터베이스는 모든 행의 `order_date`를 읽어서 함수를 적용한 뒤 비교해야 합니다. 이렇게 하면 인덱스를 활용하기 어려워집니다. 가능하면 컴럼을 그대로 두고 비교 값을 조정하는 편이 낫습니다.

### 조건 순서와 성능

대부분의 현대 데이터베이스는 쿼리 최적화기가 조건 순서를 알아서 재배치합니다. 하지만 원칙적으로는 선택도가 높은 조건(적은 행을 걸러내는 조건)을 먼저 쓰면 데이터베이스가 불필요한 비교를 줄일 수 있습니다.

```sql
-- user_id가 100명, status='pending'이 10명이라면
-- 선택도가 높은 조건을 먼저
SELECT * FROM orders
WHERE status = 'pending' AND user_id = 123;
```

이 경우 `status = 'pending'`이 먼저 10명을 걸러내고, 그 중에서 `user_id = 123`을 찾는 것이 효율적일 수 있습니다. 하지만 현대 데이터베이스는 통계 정보를 바탕으로 자동으로 순서를 조정하므로, 조건의 의미가 명확한 것이 순서보다 더 중요합니다.
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

## WHERE 조건 작성 모범 사례

실무에서 WHERE 조건을 작성할 때는 가독성과 성능을 함께 고려해야 합니다. 다음은 자주 쓰는 모범 사례입니다.

### 날짜 범위 조건

```sql
-- 좋은 예: 인덱스를 타기 쉬운 형태
SELECT * FROM orders
WHERE order_date >= '2026-01-01' 
  AND order_date < '2026-02-01';

-- 피할 예: 함수 사용
-- SELECT * FROM orders
-- WHERE EXTRACT(MONTH FROM order_date) = 1;
```

### NULL 처리

```sql
-- 좋은 예: 명시적으로 IS NULL 사용
SELECT * FROM users WHERE deleted_at IS NULL;

-- 피할 예: = NULL은 동작하지 않음
-- SELECT * FROM users WHERE deleted_at = NULL;
```

### 복잡한 AND/OR 조합

```sql
-- 좋은 예: 괄호로 의도 명확히
SELECT * FROM products
WHERE (category = 'electronics' OR category = 'computers')
  AND price > 100
  AND in_stock = true;

-- 피할 예: 괄호 없이 혼동 가능
-- SELECT * FROM products
-- WHERE category = 'electronics' OR category = 'computers'
--   AND price > 100 AND in_stock = true;
```
## 처음 질문으로 돌아가기

- **비교 연산자와 조건식은 어떻게 읽어야 할까요?**
  - WHERE는 FROM에서 온 행을 필터링하는 단계입니다. 이 단계의 조건식이 성능을 크게 좌우합니다.
- **`AND`와 `OR`의 우선순위는 왜 자주 문제를 만들까요?**
  - 조건식을 정확하게 쓰지 않으면 실수로 많은 행을 선택하거나, 반대로 필요한 행을 빼먹을 수 있습니다.
- **`IN`, `BETWEEN`, `LIKE`는 각각 어떤 상황에 어울릴까요?**
  - 인덱스가 있는 열로 필터링하면 데이터베이스는 전체 테이블을 읽지 않고도 빠르게 조건을 만족하는 행만 찾을 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [SQL 101 (1/10): SQL이란 무엇인가?](./01-what-is-sql.md)
- [SQL 101 (2/10): SELECT 기본](./02-select-basics.md)
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
