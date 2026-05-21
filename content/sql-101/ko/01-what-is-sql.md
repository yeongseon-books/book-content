---
series: sql-101
episode: 1
title: "SQL 101 (1/10): SQL이란 무엇인가?"
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
  - Database
  - RDBMS
  - Postgres
  - Analytics
seo_description: SQL의 역할, 관계형 모델, 선언형 질의, 그리고 실무에서 SQL이 중요한 이유를 설명합니다
last_reviewed: '2026-05-15'
---

# SQL 101 (1/10): SQL이란 무엇인가?

이 글은 SQL 101 시리즈의 첫 번째 글입니다. 여기서는 SQL을 단순한 조회 문법이 아니라, 관계형 데이터를 다루기 위한 선언형 언어라는 관점에서 설명합니다.

처음 SQL을 배우면 문법부터 외우려는 경우가 많습니다. 그런데 실무에서 더 중요한 출발점은 문법이 아니라 관점입니다. 왜 사람들은 수십 년 동안 SQL을 계속 쓰는지, 왜 스프레드시트와 애플리케이션 코드 사이에서 SQL이 공통 언어로 남았는지를 먼저 이해해야 이후 문법도 빠르게 정리됩니다.

![SQL 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/sql-101/01/01-01-query-flow-at-a-glance.ko.png)
*SQL 101 1장 흐름 개요*
> SQL의 핵심은 문법을 외우는 것이 아니라, 데이터베이스가 선언형 문장을 어떻게 해석하고 실행하는지 이해하는 데 있습니다.

## 먼저 던지는 질문

- SQL은 정확히 어떤 종류의 언어일까요?
- 관계형 모델은 왜 지금도 데이터 작업의 기본 토대일까요?
- 선언형 언어라는 말은 실무에서 무엇을 뜻할까요?

## 왜 중요한가

분석가, 백엔드 엔지니어, 데이터 엔지니어가 같은 데이터베이스를 바라볼 때 공통으로 만나는 언어가 SQL입니다. 데이터가 스프레드시트 범위를 넘는 순간, SQL은 선택지가 아니라 기본 도구가 됩니다. 사용자 수를 세고, 주문 합계를 계산하고, 로그에서 이상 징후를 찾는 일은 결국 SQL 한두 줄에서 시작하는 경우가 많습니다.

또 SQL은 오래된 기술이라서 불리한 것이 아니라, 오래 살아남았기 때문에 유리한 기술입니다. PostgreSQL, MySQL, SQLite, BigQuery, Snowflake처럼 제품은 달라도 핵심 문장은 크게 달라지지 않습니다. 한 번 제대로 익히면 여러 환경으로 옮겨 갈 수 있습니다.

## 질의 흐름 한눈에 보기

애플리케이션이나 BI 도구는 SQL 문장을 데이터베이스 엔진에 전달합니다. 그러면 엔진은 테이블과 인덱스를 읽어 실행 계획을 세우고, 최종 결과 집합을 반환합니다. 여기서 중요한 점은 사용자가 인덱스를 어떤 순서로 훑으라고 직접 지시하지 않는다는 것입니다. 사용자는 원하는 결과를 말하고, 엔진이 가능한 실행 방법을 고릅니다.

## 핵심 개념 정리

### 관계형 모델은 무엇을 약속할까

관계형 모델의 기본 단위는 테이블입니다. 테이블은 행과 열로 이루어지고, 각 행은 하나의 사실을, 각 열은 그 사실의 속성을 나타냅니다. 예를 들어 사용자 테이블이라면 한 행은 한 명의 사용자이고, `name`, `signup_at` 같은 열이 그 사용자의 속성입니다.

이 모델이 강한 이유는 데이터를 구조화된 형태로 다루게 해 주기 때문입니다. 어떤 값이 이름인지, 어떤 값이 날짜인지, 어떤 열이 기본 키인지가 명확해야 조인, 집계, 정렬, 필터가 안정적으로 동작합니다.

### 선언형 언어라는 말의 뜻

SQL을 처음 접할 때 가장 낯선 부분이 바로 선언형이라는 표현입니다. 파이썬이나 자바처럼 절차형 코드에 익숙하면, 무엇을 몇 번 반복하고 어떤 순서로 처리할지를 직접 써야 익숙합니다. 반면 SQL에서는 보통 그 절차를 상세하게 적지 않습니다.

예를 들어 `SELECT name FROM users WHERE signup_at >= '2026-02-01';`라고 쓰면, 우리는 이름을 가져오고 특정 날짜 이후 가입자만 보겠다고 선언한 것입니다. 인덱스를 쓸지, 테이블 전체를 읽을지, 어떤 순서로 평가할지는 데이터베이스가 판단합니다.

### SQL의 큰 분류

실무에서는 SQL을 한 덩어리로 보지 않고 몇 가지 묶음으로 나눠 생각하면 이해가 쉬워집니다.

| 분류 | 의미 | 대표 문장 |
| --- | --- | --- |
| DDL | 구조를 정의하는 문장 | `CREATE`, `ALTER`, `DROP` |
| DML | 데이터를 읽고 바꾸는 문장 | `SELECT`, `INSERT`, `UPDATE`, `DELETE` |
| DCL | 권한을 다루는 문장 | `GRANT`, `REVOKE` |

입문 단계에서는 DML, 그중에서도 `SELECT`가 중심입니다. 하지만 이후 운영 단계로 가면 인덱스를 만들고 권한을 조정하는 일도 결국 SQL 안에서 다뤄집니다.

## SQL vs NoSQL — 언제 무엇을 선택할까

관계형 데이터베이스를 배우다 보면 NoSQL 같은 대안을 자주 듣습니다. 그런데 SQL과 NoSQL은 완전히 대체 관계가 아니라, 각자 적합한 문제 영역이 다릅니다. 다음 표는 두 접근의 주요 차이를 보여 줍니다.

| 기준 | SQL (관계형) | NoSQL |
| --- | --- | --- |
| 구조 | 테이블, 행, 열로 고정된 스키마 | Document, Key-Value, Column-Family 등 유연한 구조 |
| 스키마 | 사전 정의 필수, 변경 시 마이그레이션 | 스키마리스 또는 동적 스키마 |
| 확장 | 수직 확장(Scale-Up) 위주 | 수평 확장(Scale-Out) 중심 |
| 트랜잭션 | ACID 보장, 복잡한 트랜잭션 가능 | 제한적, 최종 일관성 중심 (일부 예외) |
| 적합한 경우 | 복잡한 조인, 정확한 집계, 트랜잭션 일관성 | 대량 쓰기, 유연한 스키마, 분산 확장 |

데이터가 명확한 관계를 가지고, 집계와 조인이 자주 필요하고, 정확한 합계를 보장해야 하는 경우에는 관계형 모델이 강합니다. 반면 스키마가 자주 바뀌고, 쓰기 처리량이 크고, 여러 서버로 데이터를 나눠야 하는 경우에는 NoSQL이 더 적합할 수 있습니다.
## 손으로 읽어 보는 첫 쿼리 다섯 단계

처음부터 복잡한 쿼리를 보는 것보다 아주 작은 흐름을 직접 읽는 편이 낫습니다.

### 1단계 — 테이블 만들기

```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    name TEXT NOT NULL,
    signup_at DATE NOT NULL
);
```

이 문장은 `users`라는 테이블을 만들고, 각 사용자는 `id`, `name`, `signup_at`을 가진다고 정의합니다. 여기서 `PRIMARY KEY`는 각 사용자를 유일하게 식별하는 기준이고, `NOT NULL`은 값이 비어 있으면 안 된다는 제약입니다.

### 2단계 — 데이터 넣기

```sql
INSERT INTO users (id, name, signup_at) VALUES
    (1, 'Ada', '2026-01-01'),
    (2, 'Linus', '2026-02-15'),
    (3, 'Grace', '2026-03-30');
```

이제 구조만 있는 테이블에 실제 행을 넣습니다. 입문 단계에서는 이처럼 아주 작은 샘플 데이터를 만들어 두면 나중에 `WHERE`, `GROUP BY`, `JOIN`을 연습하기 쉽습니다.

### 3단계 — 전체 읽기

```sql
SELECT * FROM users;
```

이 문장은 `users` 테이블의 모든 열을 보여 달라는 뜻입니다. 학습용으로는 편하지만, 실무에서는 필요한 열만 명시하는 습관이 더 중요합니다. 이 주제는 다음 글에서 자세히 다룹니다.

### 4단계 — 조건 걸기

```sql
SELECT name FROM users WHERE signup_at >= '2026-02-01';
```

**Expected output:**

| name |
| --- |
| Linus |
| Grace |

여기서는 전체 행을 다 읽는 대신 조건을 통과한 사용자만 남깁니다. 그리고 열도 `name`만 고릅니다. SQL은 이런 식으로 열과 행을 동시에 줄여서 원하는 결과를 만듭니다.

### 5단계 — 개수 세기

```sql
SELECT COUNT(*) AS total FROM users;
```

분석 SQL의 출발점은 대개 개수를 정확하게 세는 데 있습니다. `COUNT(*)`는 행 수를 세고, `AS total`은 결과 열 이름을 붙입니다.

## 이 코드에서 먼저 봐야 할 점

- SQL 문장 어디에도 데이터를 어떤 순서로 읽을지 적지 않았습니다.
- `SELECT`, `FROM`, `WHERE`는 결과 집합을 만드는 기본 뼈대입니다.
- 같은 결과를 여러 방식으로 표현할 수 있지만, 읽기 쉬운 형태가 실무에서는 더 중요합니다.

처음 배울 때는 실행 속도보다 문장의 의미를 정확히 읽는 연습이 먼저입니다. 어떤 테이블에서, 어떤 열을, 어떤 조건으로 가져오는지 말로 설명할 수 있어야 합니다.

## SQL 방언 비교 — PostgreSQL, MySQL, SQLite

SQL 표준이 있지만, 실무에서 쓰는 데이터베이스마다 구현이 조금씩 다릅니다. 이 차이를 방언(dialect)이라고 부릅니다. 입문 단계에서는 하나에 집중하되, 나중에 다른 환경으로 옮길 때 어떤 부분이 바뀌는지 알아 두면 학습이 쉬워집니다.

### 문자열 연결

- **PostgreSQL**: `'Hello' || ' ' || 'World'` 또는 `CONCAT('Hello', ' ', 'World')`
- **MySQL**: `CONCAT('Hello', ' ', 'World')`
- **SQLite**: `'Hello' || ' ' || 'World'`

PostgreSQL과 SQLite는 `||` 연산자를 지원하지만, MySQL은 기본적으로 `CONCAT` 함수를 씁니다.

### 자동 증가 ID

- **PostgreSQL**: `SERIAL` 또는 `GENERATED BY DEFAULT AS IDENTITY`
- **MySQL**: `AUTO_INCREMENT`
- **SQLite**: `INTEGER PRIMARY KEY AUTOINCREMENT`

각 데이터베이스마다 자동으로 증가하는 기본 키를 만드는 방법이 다릅니다. 하지만 기본 아이디어는 같습니다.

### LIMIT과 OFFSET

- **PostgreSQL**: `LIMIT 10 OFFSET 5`
- **MySQL**: `LIMIT 10 OFFSET 5` 또는 `LIMIT 5, 10`
- **SQLite**: `LIMIT 10 OFFSET 5`

대부분의 SQL 데이터베이스에서 `LIMIT`와 `OFFSET`은 비슷하게 동작하지만, MySQL은 순서가 약간 다른 구문도 지원합니다.

### 날짜/시간 함수

- **PostgreSQL**: `NOW()`, `CURRENT_DATE`, `INTERVAL '1 day'`
- **MySQL**: `NOW()`, `CURDATE()`, `DATE_ADD(NOW(), INTERVAL 1 DAY)`
- **SQLite**: `datetime('now')`, `date('now')`

날짜와 시간 다루기는 세 데이터베이스 모두 조금씩 다릅니다. 이 부분은 문서를 참고하면서 쓰는 편이 안전합니다.

이런 차이가 있지만 핵심 SELECT, WHERE, JOIN, GROUP BY 문법은 대부분 공통입니다. 한 가지를 제대로 익히면 다른 환경으로 옮기는 비용이 크지 않습니다.

## 실전 예제 — 테이블 만들고 데이터 넣기

앞에서 다섯 단계로 쪼개서 본 예제를 이제 하나로 이어서 봅니다. 이 예제는 PostgreSQL 기준이지만, MySQL이나 SQLite에서도 거의 그대로 동작합니다.

```sql
-- 테이블 정의
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    signup_at DATE NOT NULL,
    country TEXT
);

-- 샘플 데이터 삽입
INSERT INTO users (name, email, signup_at, country) VALUES
    ('Ada', 'ada@example.com', '2026-01-01', 'US'),
    ('Linus', 'linus@example.com', '2026-02-15', 'FI'),
    ('Grace', 'grace@example.com', '2026-03-30', 'US'),
    ('Alan', 'alan@example.com', '2026-04-12', 'UK'),
    ('Sophie', 'sophie@example.com', '2026-05-08', 'FR');

-- 전체 데이터 확인
SELECT * FROM users;

-- 조건부 조회
SELECT name, country FROM users WHERE country = 'US';

-- 정렬
SELECT name, signup_at FROM users ORDER BY signup_at DESC;

-- 집계
SELECT country, COUNT(*) AS user_count
FROM users
GROUP BY country;
```

이 예제에서는 테이블을 만들고, 데이터를 넣고, 조회하고, 필터링하고, 정렬하고, 집계하는 기본 흐름을 모두 볼 수 있습니다. 입문 단계에서는 이 정도 흐름을 여러 번 반복해 보는 것이 가장 좋습니다.
## 실무에서 자주 헷갈리는 지점

### `SELECT *`는 왜 조심해야 할까

작은 테이블에서는 `SELECT *`가 편해 보입니다. 하지만 컬럼 수가 많아지고 데이터량이 커지면 네트워크 비용과 메모리 사용량이 함께 커집니다. 특히 대시보드 쿼리나 API 뒤쪽 쿼리에서는 필요한 열만 명시하는 습관이 중요합니다.

### NULL은 0이나 빈 문자열이 아니다

`NULL`은 값이 0이라는 뜻도 아니고 빈 문자열이라는 뜻도 아닙니다. 값이 없거나 아직 알 수 없다는 별도 상태입니다. 이 차이를 놓치면 나중에 집계와 비교 연산에서 예상과 다른 결과가 나옵니다.

### 스키마를 대충 잡으면 나중에 비용이 커진다

처음에는 모든 값을 문자열로 넣고 싶어질 수 있습니다. 하지만 날짜는 날짜형으로, 수량은 숫자형으로, 식별자는 일관된 타입으로 저장해야 이후 조건절과 집계가 정확해집니다. SQL을 잘 쓰는 것과 스키마를 잘 만드는 것은 분리되지 않습니다.

## 체크리스트

- [ ] SQL이 선언형 언어라는 뜻을 설명할 수 있다.
- [ ] 테이블, 행, 열의 차이를 말할 수 있다.
- [ ] `SELECT`, `FROM`, `WHERE`의 역할을 구분할 수 있다.
- [ ] DDL과 DML의 차이를 알고 있다.
- [ ] `NULL`이 별도 상태라는 점을 이해하고 있다.

## SQL 학습 경로

SQL을 배울 때는 문법을 순서대로 외우기보다, 실제 질문을 SQL로 표현하는 연습을 많이 하는 편이 더 효과적입니다. 다음은 추천하는 학습 순서입니다.

1. **기본 SELECT**: 테이블에서 데이터 읽어 오기
2. **WHERE 조건**: 행 필터링
3. **JOIN**: 여러 테이블 연결
4. **GROUP BY와 집계**: 숫자 만들기
5. **서브쿼리와 CTE**: 복잡한 질문 나누기
6. **WINDOW 함수**: 행별 비교와 순위
7. **DML**: INSERT, UPDATE, DELETE
8. **인덱스와 성능**: 쿼리 최적화

각 단계마다 실제 데이터로 연습하고, 같은 결과를 얻는 여러 방법을 비교해 보면 SQL의 유연성을 느낄 수 있습니다.

## 실전 앵커: 선언형 사고를 체감하는 작은 실험

문법을 외우는 속도보다 중요한 것은 **질문을 데이터 연산으로 바꾸는 습관**입니다. 아래 예시는 같은 질문을 서로 다른 방식으로 푸는 과정입니다. 처음에는 절차적으로 접근하지만, SQL에서는 선언형으로 바꿔야 최적화 여지가 생깁니다.

```sql
-- 질문: 2026년 1분기 결제 완료 주문의 국가별 매출 상위 5개
SELECT
    c.country,
    SUM(o.total_amount) AS revenue
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.status = 'paid'
  AND o.ordered_at >= DATE '2026-01-01'
  AND o.ordered_at <  DATE '2026-04-01'
GROUP BY c.country
ORDER BY revenue DESC
LIMIT 5;
```

이 쿼리는 "어떻게 반복할지"를 쓰지 않았지만, 데이터베이스는 내부적으로 필터, 조인, 집계 순서를 계산해 실행 계획을 고릅니다. 즉 SQL의 핵심은 반복문을 숨기는 것이 아니라, **최적화 가능한 형태로 의도를 전달하는 것**입니다.

## 실전 앵커: 같은 요구사항을 두 가지 모델로 비교하기

관계형 모델을 이해할 때는 정규화 수준에 따라 쿼리가 어떻게 달라지는지 보는 편이 빠릅니다. 예를 들어 주문 데이터가 비정규화되어 있다면 처음에는 조회가 쉬워 보입니다.

```sql
-- 비정규화된 단일 테이블 예시
SELECT order_id, customer_name, product_name, quantity, unit_price
FROM order_flat
WHERE ordered_at >= DATE '2026-05-01';
```

하지만 고객 이름 수정, 상품 가격 변경, 중복 데이터 정리 같은 변경 작업이 반복되면 관리 비용이 급격히 커집니다. 반대로 정규화된 구조에서는 JOIN이 필요하지만 변경 안정성이 높아집니다.

```sql
SELECT
    o.order_id,
    c.customer_name,
    p.product_name,
    oi.quantity,
    oi.unit_price
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p ON p.product_id = oi.product_id
WHERE o.ordered_at >= DATE '2026-05-01';
```

처음 학습 단계에서는 JOIN이 번거롭게 보이지만, 실무에서는 이 구조가 데이터 품질을 지키는 핵심 안전장치가 됩니다.

## 실전 앵커: 실행 계획을 읽는 최소 루틴

`EXPLAIN`을 무겁게 느끼는 초급자가 많지만, 아래 세 줄만 먼저 보면 충분합니다.

```sql
EXPLAIN
SELECT *
FROM orders
WHERE customer_id = 42
  AND ordered_at >= DATE '2026-01-01';
```

1) `Seq Scan`인지 `Index Scan`인지, 2) 예상 행 수(`rows`)가 현실과 비슷한지, 3) 비용이 급격히 커지는 연산이 있는지를 확인합니다. 이 루틴이 생기면 SQL을 문법이 아니라 **실행되는 프로그램**으로 볼 수 있습니다.

## 실전 앵커: 학습용 체크 SQL

아래 질문을 직접 SQL로 작성해 보면, 시리즈 전체를 훨씬 빠르게 흡수할 수 있습니다.

- 특정 기간 결제 금액 상위 고객 10명
- 카테고리별 평균 주문 금액과 중앙값 비교
- 첫 구매 후 30일 내 재구매한 사용자 비율
- 결제 실패 원인 코드별 분포

질문을 SQL로 바꾸는 반복이 쌓이면, 이후 JOIN·윈도 함수·인덱스 학습이 각각 분리된 주제가 아니라 하나의 분석 흐름으로 연결됩니다.

## 심화 실습 시나리오: 쿼리 품질을 수치로 검증하기

문장 길이가 길어질수록 SQL 품질은 느낌이 아니라 **측정 가능한 기준**으로 관리해야 합니다. 아래 절차는 어떤 주제의 SQL이든 그대로 적용할 수 있는 공통 루틴입니다.

1. 입력 데이터 범위(기간, 상태, 대상 테넌트)를 명시합니다.
2. 같은 조건으로 `COUNT(*)`를 먼저 실행해 모수 행 수를 기록합니다.
3. 본 쿼리를 실행하고 결과 행 수와 합계 지표를 기록합니다.
4. `EXPLAIN (ANALYZE, BUFFERS)`를 실행해 병목 노드를 확인합니다.
5. 인덱스/조건식을 조정한 뒤 2~4를 다시 반복합니다.

```sql
-- 1) 모수 확인
SELECT COUNT(*) AS base_rows
FROM orders
WHERE ordered_at >= DATE '2026-01-01'
  AND ordered_at <  DATE '2026-02-01';

-- 2) 본 쿼리(예시)
SELECT
    customer_id,
    COUNT(*) AS order_count,
    SUM(total_amount) AS revenue
FROM orders
WHERE ordered_at >= DATE '2026-01-01'
  AND ordered_at <  DATE '2026-02-01'
GROUP BY customer_id
ORDER BY revenue DESC
LIMIT 20;

-- 3) 계획 확인
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    customer_id,
    COUNT(*) AS order_count,
    SUM(total_amount) AS revenue
FROM orders
WHERE ordered_at >= DATE '2026-01-01'
  AND ordered_at <  DATE '2026-02-01'
GROUP BY customer_id;
```

이 과정을 습관화하면 "왜 느린지"를 추측하지 않고 설명할 수 있습니다. 특히 팀 협업에서는 성능 이슈를 재현 가능한 단위로 공유할 수 있다는 점이 중요합니다.

## 심화 실습 시나리오: 조인·서브쿼리·CTE 선택 비교

아래 세 방식은 결과가 같아 보이지만, 데이터 크기와 통계 상태에 따라 실행 계획이 크게 달라질 수 있습니다.

```sql
-- A. 직접 조인
SELECT c.customer_id, SUM(o.total_amount) AS revenue
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
WHERE o.status = 'paid'
GROUP BY c.customer_id;
```

```sql
-- B. 서브쿼리
SELECT c.customer_id, x.revenue
FROM customers c
JOIN (
    SELECT customer_id, SUM(total_amount) AS revenue
    FROM orders
    WHERE status = 'paid'
    GROUP BY customer_id
) x ON x.customer_id = c.customer_id;
```

```sql
-- C. CTE
WITH paid_orders AS (
    SELECT customer_id, total_amount
    FROM orders
    WHERE status = 'paid'
),
revenue_by_customer AS (
    SELECT customer_id, SUM(total_amount) AS revenue
    FROM paid_orders
    GROUP BY customer_id
)
SELECT c.customer_id, r.revenue
FROM customers c
JOIN revenue_by_customer r ON r.customer_id = c.customer_id;
```

실무에서 권장하는 방법은 "문법 취향"이 아니라 "검증 가능성"으로 고르는 것입니다. 변경이 자주 일어나는 쿼리는 CTE가 리뷰와 테스트에 유리하고, 단발성 쿼리는 인라인 구조가 간결할 수 있습니다.

## 심화 실습 시나리오: 인덱스 전략과 유지비용

인덱스는 조회 성능을 높이지만 쓰기 비용을 늘립니다. 그래서 읽기/쓰기 비율을 기준으로 설계해야 합니다.

```sql
-- 조회 패턴에 맞춘 합성 인덱스
CREATE INDEX idx_orders_customer_status_created
    ON orders (customer_id, status, created_at DESC);

-- 자주 쓰는 상태값만 가볍게 다루는 부분 인덱스
CREATE INDEX idx_orders_paid_created
    ON orders (created_at DESC)
WHERE status = 'paid';
```

인덱스를 추가한 뒤에는 반드시 아래를 확인합니다.

- `INSERT`/`UPDATE` TPS가 과도하게 떨어지지 않는가
- VACUUM/ANALYZE 주기가 비정상적으로 늘어나지 않는가
- 실제 주요 쿼리에서 `Index Scan` 또는 `Bitmap Index Scan`으로 전환되었는가

인덱스는 "있으면 좋은 옵션"이 아니라 **운영 비용이 있는 구조물**입니다. 성능 개선 수치와 유지 비용을 같이 기록해야 장기적으로 안정됩니다.

## 심화 실습 시나리오: 트랜잭션 격리 수준 재현 데모

분석 SQL이든 운영 SQL이든 동시성 환경에서는 격리 수준 이해가 필요합니다. 다음은 재현 가능한 기본 데모입니다.

```sql
-- 세션 A
BEGIN;
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
SELECT COUNT(*) FROM inventory WHERE product_id = 10;

-- 세션 B
BEGIN;
UPDATE inventory SET quantity = quantity - 1 WHERE product_id = 10;
COMMIT;

-- 세션 A에서 다시 실행
SELECT COUNT(*) FROM inventory WHERE product_id = 10;
COMMIT;
```

`READ COMMITTED`에서는 같은 트랜잭션 안에서도 두 번째 조회가 다른 스냅샷을 볼 수 있습니다. 반면 `REPEATABLE READ`로 바꾸면 시작 시점 스냅샷이 유지됩니다.

```sql
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT SUM(total_amount) FROM orders WHERE status = 'paid';
-- 다른 세션의 커밋 이후에도 동일 스냅샷 유지
SELECT SUM(total_amount) FROM orders WHERE status = 'paid';
COMMIT;
```

배치 지표 계산에서는 이 차이가 그대로 숫자 불일치로 나타납니다. 따라서 격리 수준을 문서화하고, 배치 쿼리에서 명시적으로 설정하는 것이 안전합니다.

## 심화 실습 시나리오: 리뷰 체크리스트를 쿼리 옆에 남기기

SQL 리뷰를 사람 기억에 의존하면 시간이 지나면서 기준이 흔들립니다. 아래 항목을 PR 본문이나 문서에 고정하면 품질 편차를 줄일 수 있습니다.

- 질문의 비즈니스 정의가 SQL 조건으로 정확히 번역되었는가
- 키 유일성(기본키/대체키)이 조인 경로에서 유지되는가
- 기간 조건이 반열린 구간으로 작성되어 경계 오류가 없는가
- `NULL` 처리 규칙이 명시되어 있는가
- 결과 검증용 샘플 출력(행 수, 합계, 상위 N)이 첨부되었는가

이 기준은 학습용 글에서도 그대로 유효합니다. SQL은 결국 데이터와 의사결정을 연결하는 도구이기 때문에, 쿼리 자체보다 **검증 가능한 사고 과정**을 남기는 습관이 더 오래 갑니다.

## 정리

SQL은 데이터를 다루는 팀이 함께 사용하는 공용어입니다. 핵심은 절차를 세세하게 적는 것이 아니라 원하는 결과를 선언하는 데 있습니다. 관계형 모델, 선언형 사고방식, 기본 문장 구조를 여기서 잡아 두면 이후의 `SELECT`, `WHERE`, `JOIN`, 집계 문장이 모두 더 자연스럽게 이어집니다.

다음 글에서는 가장 자주 쓰는 문장인 `SELECT`를 중심으로, 컬럼을 명시하고 정렬하고 제한하는 기본 패턴을 정리합니다.

## 처음 질문으로 돌아가기

- **SQL은 정확히 어떤 종류의 언어일까요?**
  - 관계형 모델, 선언형 질의, 그리고 데이터베이스 엔진의 역할을 함께 이해해야 합니다.
- **관계형 모델은 왜 지금도 데이터 작업의 기본 토대일까요?**
  - 관계형 모델은 행과 열로 데이터를 구조화하고, 각 테이블이 어떤 사실의 집합을 나타내는지 명확히 해야 합니다.
- **선언형 언어라는 말은 실무에서 무엇을 뜻할까요?**
  - 선언형 언어는 절차를 직접 지시하지 않고 원하는 결과를 선언하면, 엔진이 최적의 실행 계획을 세웁니다.

<!-- toc:begin -->
## 시리즈 목차

- **SQL이란 무엇인가? (현재 글)**
- SELECT 기본 (예정)
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

- [book-examples/sql-101 (ko)](https://github.com/yeongseon-books/book-examples/tree/main/sql-101/ko)

- [PostgreSQL Tutorial — SQL](https://www.postgresql.org/docs/current/tutorial-sql.html)
- [SQLBolt — Interactive SQL Lessons](https://sqlbolt.com/)
- [Use The Index, Luke](https://use-the-index-luke.com/)
- [Mode — SQL Tutorial](https://mode.com/sql-tutorial/)

Tags: SQL, Database, Postgres, Analytics
