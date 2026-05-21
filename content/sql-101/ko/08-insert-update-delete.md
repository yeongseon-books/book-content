---
series: sql-101
episode: 8
title: "SQL 101 (8/10): 데이터를 바꾸는 SQL — INSERT, UPDATE, DELETE"
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
  - DML
  - Transaction
  - Database
  - Postgres
seo_description: INSERT, UPDATE, DELETE를 트랜잭션과 RETURNING으로 안전하게 다루는 방법을 설명합니다
last_reviewed: '2026-05-15'
---

# SQL 101 (8/10): 데이터를 바꾸는 SQL — INSERT, UPDATE, DELETE

지금까지는 주로 데이터를 읽는 SQL을 다뤘습니다. 하지만 운영 환경에서 더 긴장되는 순간은 데이터를 바꿀 때입니다. 한 줄의 `UPDATE`나 `DELETE`가 서비스 데이터 전체에 영향을 줄 수 있기 때문입니다. 그래서 데이터를 바꾸는 SQL은 읽는 SQL보다 훨씬 더 보수적으로 다뤄야 합니다.

이 글은 SQL 101 시리즈의 여덟 번째 글입니다. 여기서는 `INSERT`, `UPDATE`, `DELETE`를 단순한 문법이 아니라, 트랜잭션과 검증 절차 안에서 안전하게 실행하는 작업으로 설명합니다.

## 먼저 던지는 질문

- `INSERT`, `UPDATE`, `DELETE`의 기본 형태는 무엇일까요?
- 트랜잭션은 왜 데이터 변경 작업의 기본 안전망일까요?
- `RETURNING`은 왜 실무에서 특히 유용할까요?

## 큰 그림

![SQL 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/sql-101/08/08-01-safe-data-change-flow.ko.png)

*SQL 101 8장 흐름 개요*

이 그림에서는 INSERT, UPDATE, DELETE가 데이터를 어떻게 변경하고, 각 작업이 트랜잭션과 제약 조건에 어떻게 영향을 받는지 봅니다. 데이터 변경은 조회보다 신중해야 합니다.

> INSERT, UPDATE, DELETE의 핵심은 데이터 변경의 문법이 아니라, 어떤 행을 어떤 순서로 변경할 때 데이터 일관성과 비즈니스 규칙이 깨지지 않는지 사전에 검증하는 데 있습니다.

## 왜 중요한가

운영 데이터는 한 번 잘못 바꾸면 되돌리기 어렵습니다. 특히 `WHERE`가 빠진 `UPDATE`나 `DELETE`는 사고로 바로 이어집니다. 그래서 실무에서는 문장을 작성하는 능력만큼, 실행 전에 검증하고 되돌릴 수 있게 준비하는 습관이 중요합니다.

트랜잭션과 `RETURNING`은 이런 안전 장치를 만드는 기본 도구입니다. 데이터를 바꾸기 전후를 확인하고, 결과가 이상하면 롤백할 수 있어야 합니다. 이 감각은 입문 단계부터 몸에 익혀 두는 편이 좋습니다.

## 안전한 변경 흐름

안전한 데이터 변경 작업은 대개 이런 흐름을 따릅니다. 트랜잭션을 시작하고, 변경을 실행하고, 영향을 받은 행을 확인한 뒤, 맞으면 커밋하고 아니면 롤백합니다.

## 핵심 개념 정리

### DML은 데이터 조작 문장이다

`INSERT`, `UPDATE`, `DELETE`는 DML에 속합니다. 읽기 전용 쿼리와 달리 상태를 바꾸므로, 항상 영향 범위를 의식해야 합니다.

### 트랜잭션은 여러 변경을 하나의 작업으로 묶는다

트랜잭션 안에서 실행한 작업은 전부 성공하거나 전부 실패하도록 다룰 수 있습니다. 중간에 하나라도 문제가 생기면 롤백해 이전 상태로 되돌릴 수 있습니다.

### `RETURNING`은 결과 검증의 기본 도구다

PostgreSQL에서는 변경된 행을 바로 돌려받을 수 있습니다. 이 기능이 있으면 변경 대상이 정말 의도한 행이 맞는지 즉시 확인할 수 있습니다.

### UPSERT는 제약 조건과 함께 동작한다

`ON CONFLICT`는 충돌을 감지할 고유 제약 조건이 있어야 의미가 있습니다. 고유 키나 기본 키 없이 UPSERT를 기대하면 원하는 동작이 나오지 않습니다.

## 다섯 가지 안전한 패턴

### 1단계 — 새 행 추가하기

```sql
INSERT INTO users (id, name, signup_at)
VALUES (4, 'Margaret', '2026-04-10');
```

새 데이터를 넣는 가장 기본 형태입니다. 가능하면 어떤 컬럼에 어떤 값을 넣는지 명시적으로 적는 편이 안전합니다.

### 2단계 — 조건을 붙여 수정하기

```sql
UPDATE users SET name = 'Margaret Hamilton' WHERE id = 4;
```

`UPDATE`에서 가장 중요한 부분은 `WHERE`입니다. 어떤 행을 바꿀지 정확히 제한하지 않으면 전체 행이 영향을 받을 수 있습니다.

### 3단계 — 트랜잭션 안에서 삭제하기

```sql
BEGIN;
DELETE FROM users WHERE id = 4 RETURNING *;
-- 결과를 검토한 뒤
COMMIT;
```

**Expected output:**

| id | name | signup_at |
| --- | --- | --- |
| 4 | Margaret Hamilton | 2026-04-10 |

삭제는 특히 되돌리기 어렵기 때문에, 트랜잭션과 `RETURNING`을 함께 쓰는 습관이 중요합니다.

### 4단계 — 충돌 시 수정으로 전환하기

```sql
INSERT INTO users (id, name, signup_at)
VALUES (4, 'Margaret', '2026-04-10')
ON CONFLICT (id)
DO UPDATE SET name = EXCLUDED.name;
```

동일한 `id`가 이미 있으면 새로 넣는 대신 이름을 갱신합니다. `EXCLUDED`는 삽입을 시도했던 새 값을 가리킵니다.

### 5단계 — 여러 행 한 번에 넣기

```sql
INSERT INTO users (id, name, signup_at) VALUES
    (5, 'Edsger', '2026-04-11'),
    (6, 'Donald', '2026-04-12'),
    (7, 'Barbara', '2026-04-13');
```

대량 입력을 한 행씩 여러 번 보내기보다 한 문장으로 묶는 편이 보통 더 효율적입니다.

## 이 코드에서 먼저 봐야 할 점

- `UPDATE`와 `DELETE`에는 항상 `WHERE`가 있는지 먼저 확인합니다.
- 변경 작업은 트랜잭션 안에서 검증하는 편이 안전합니다.
- `RETURNING`은 실제로 어떤 행이 바뀌었는지 확인하는 가장 직접적인 수단입니다.

## 실무에서 자주 헷갈리는 지점

### 변경 전에 SELECT를 먼저 보는 습관이 왜 중요할까

예상으로 대상 행을 짚지 말고, 먼저 같은 조건으로 `SELECT`를 실행해 보는 편이 좋습니다. 어떤 행이 바뀔지 눈으로 확인한 뒤 변경 문장을 실행하면 사고 확률이 크게 줄어듭니다.

### 여러 문장을 따로 실행하면 어떤 문제가 생길까

중간 단계에서 실패했을 때 앞선 변경만 남고 뒤쪽 변경은 사라질 수 있습니다. 예를 들어 잔액 차감은 됐는데 이력 기록은 실패한 상태가 생길 수 있습니다. 이런 반쪽 상태를 막는 기본 장치가 트랜잭션입니다.

### UPSERT는 왜 고유 제약 없이 안심할 수 없을까

충돌을 감지할 기준이 없으면 `ON CONFLICT`는 기대한 대로 동작하지 않습니다. UPSERT를 설계할 때는 먼저 어떤 컬럼 조합이 고유성을 보장하는지부터 정해야 합니다.

## 정규화 단계

INSERT, UPDATE, DELETE는 데이터를 바꾸는 작업이므로, 테이블 설계가 얼마나 잘 되어 있는지가 작업의 안전성에 큰 영향을 줍니다. 정규화는 중복과 불일치를 줄여 데이터 무결성을 높이는 설계 원칙입니다.

| 단계 | 조건 | 위반 예시 | 해결 방법 |
| --- | --- | --- | --- |
| 1NF | 모든 열이 원자값 (atomic) | `tags` 열에 `"python,sql"` 문자열 저장 | 별도 `post_tags` 테이블로 분리 |
| 2NF | 기본키에 완전히 종속 | `(user_id, order_id)` 기본키에 `user_name` 포함 | `users` 테이블로 분리 |
| 3NF | 비키 열 간 종속성 없음 | `orders`에 `user_country`를 저장 (`users.country`와 중복) | `users` 테이블로 분리 |
| BCNF | 모든 결정자가 후보키 | `(instructor, course)` 테이블에 `instructor → department` 종속성 | `instructors` 테이블로 분리 |

1NF부터 BCNF까지 단계가 올라갈수록 중복이 줄고 수정 이상 현상이 줄어듭니다. 하지만 조인이 많아지므로, 실무에서는 3NF 정도를 대체로 목표로 삼고 성능이 필요한 경우는 역정규화를 고려합니다.

## 비정규화→정규화 변환 예제

다음은 1NF를 위반하는 테이블을 정규화하는 예시입니다.

### 비정규화 테이블

```sql
CREATE TABLE posts_denorm (
    id INT PRIMARY KEY,
    title TEXT,
    tags TEXT  -- "파이썬,SQL,데이터베이스"
);

INSERT INTO posts_denorm VALUES
(1, 'SQL 기초', '파이썬,SQL'),
(2, '데이터 분석', 'SQL,데이터베이스');
```

이 구조는 `tags` 열에 여러 값을 문자열로 묶어놓았기 때문에 1NF를 위반합니다. 특정 태그를 가진 글을 찾으려면 `LIKE '%SQL%'` 같은 패턴을 써야 하므로 인덱스도 타기 어렵습니다.

### 정규화 후

```sql
CREATE TABLE posts (
    id INT PRIMARY KEY,
    title TEXT
);

CREATE TABLE tags (
    id INT PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE post_tags (
    post_id INT REFERENCES posts(id),
    tag_id INT REFERENCES tags(id),
    PRIMARY KEY (post_id, tag_id)
);

-- 데이터 삽입
INSERT INTO posts VALUES (1, 'SQL 기초'), (2, '데이터 분석');
INSERT INTO tags VALUES (1, '파이썬'), (2, 'SQL'), (3, '데이터베이스');
INSERT INTO post_tags VALUES (1,1), (1,2), (2,2), (2,3);

-- SQL 태그를 가진 글 찾기
SELECT p.id, p.title
FROM posts p
JOIN post_tags pt ON p.id = pt.post_id
JOIN tags t ON t.id = pt.tag_id
WHERE t.name = 'SQL';
```

이제 각 태그가 독립된 행으로 저장되므로, 태그별로 정확히 검색할 수 있고 인덱스도 효과적입니다. 테이블이 늘어나지만 INSERT, UPDATE 작업은 훨씬 안전해집니다.

## 역정규화가 필요한 순간

정규화는 데이터 무결성을 높이지만, 조회 성능에는 부담을 줄 수 있습니다. 특히 자주 조회되지만 거의 변경되지 않는 데이터는 역정규화를 고려할 수 있습니다.

### 역정규화가 유용한 경우

- **읽기 빈도 ≫ 쓰기 빈도**: 대시보드, 리포트처럼 조회가 집중되는 테이블
- **복잡한 조인이 반복됨**: 매번 3-4개 테이블을 조인하는 패턴
- **집계된 지표**: 사용자별 총 주문액, 국가별 판매량 같은 집계 값

### 역정규화 패턴

```sql
-- 정규화된 형태
SELECT u.name, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;

-- 역정규화: users 테이블에 order_count 열 추가
ALTER TABLE users ADD COLUMN order_count INT DEFAULT 0;

-- INSERT/UPDATE/DELETE 시 함께 갱신
CREATE OR REPLACE FUNCTION update_user_order_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE users SET order_count = (
        SELECT COUNT(*) FROM orders WHERE user_id = NEW.user_id
    ) WHERE id = NEW.user_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_order_count
AFTER INSERT OR UPDATE OR DELETE ON orders
FOR EACH ROW EXECUTE FUNCTION update_user_order_count();
```

역정규화하면 조회는 빨라지지만, 대신 INSERT/UPDATE/DELETE마다 동기화 비용이 발생합니다. 어느 쪽 비용이 더 크냐는 실제 사용 패턴을 측정해서 결정하는 편이 안전합니다.

**역정규화 하는 대신 고려할 대안:**

- Materialized View: 주기적 갱신으로 조회 성능 확보
- 캐시 레이어: Redis 같은 외부 캐시에 집계 결과 저장
- 인덱스 최적화: 역정규화 대신 합성 인덱스 추가

## 데이터 변경 전 체크리스트

본격적인 UPDATE나 DELETE를 실행하기 전에 다음 항목을 확인하면 사고를 크게 줄일 수 있습니다.

1. **대상 행 수 확인**: 먼저 `SELECT COUNT(*) FROM ... WHERE ...`로 영향받는 행 수를 확인합니다
2. **대상 데이터 검토**: `SELECT * FROM ... WHERE ...`로 실제 데이터를 보고 의도와 맞는지 확인합니다
3. **트랜잭션 시작**: `BEGIN;`으로 트랜잭션을 엽니다
4. **변경 실행 + RETURNING**: UPDATE/DELETE에 `RETURNING *`를 붙여 결과를 확인합니다
5. **결과 검증**: 반환된 행이 예상과 맞는지 확인합니다
6. **커밋/롤백 결정**: 맞으면 `COMMIT`, 아니면 `ROLLBACK`

```sql
-- 예시: 특정 상태의 주문을 취소하기
-- 1. 대상 행 수 확인
SELECT COUNT(*) FROM orders WHERE status = 'pending' AND created_at < '2025-01-01';

-- 2. 대상 데이터 검토
SELECT id, user_id, total, status FROM orders WHERE status = 'pending' AND created_at < '2025-01-01';

-- 3. 트랜잭션 시작
BEGIN;

-- 4. 변경 실행
UPDATE orders
SET status = 'cancelled'
WHERE status = 'pending' AND created_at < '2025-01-01'
RETURNING id, user_id, status;

-- 5. 결과 확인 후 6. 커밋/롤백
COMMIT;
-- ROLLBACK;
```

이 순서를 습관화하면 데이터 변경 작업의 안전성을 크게 높일 수 있습니다.
실무에서는 역정규화를 바로 적용하기보다, 먼저 인덱스와 쿼리 최적화로 해결을 시도하고 그래도 부족할 때 신중하게 적용하는 편이 좋습니다.
## 체크리스트

- [ ] `UPDATE`와 `DELETE`를 실행하기 전에 `WHERE`를 먼저 점검한다.
- [ ] 변경 전 `SELECT`, 변경 후 `RETURNING`을 활용할 수 있다.
- [ ] `BEGIN`, `COMMIT`, `ROLLBACK` 흐름을 설명할 수 있다.
- [ ] UPSERT가 제약 조건 위에서 동작한다는 점을 알고 있다.
- [ ] 여러 행 입력은 한 번에 묶는 편이 효율적이라는 점을 이해하고 있다.

## 정리

데이터를 바꾸는 SQL의 핵심은 문법보다 안전한 실행 절차입니다. `WHERE`를 명시하고, 트랜잭션으로 묶고, `RETURNING`으로 검증하는 습관이 있어야 변경 작업을 통제할 수 있습니다. 읽는 SQL보다 쓰는 SQL을 더 천천히 다뤄야 한다는 감각을 여기서 꼭 가져가면 좋습니다.

다음 글에서는 읽기 성능을 좌우하는 인덱스와 쿼리 계획을 다루겠습니다.

## 처음 질문으로 돌아가기

- **`INSERT`, `UPDATE`, `DELETE`의 기본 형태는 무엇일까요?**
  - INSERT로 새 행을 추가할 때는 NOT NULL 제약과 PRIMARY KEY 중복을 항상 확인해야 합니다.
- **트랜잭션은 왜 데이터 변경 작업의 기본 안전망일까요?**
  - UPDATE와 DELETE는 WHERE 조건을 정확하게 써야 합니다. 잘못된 조건은 의도하지 않은 대량 변경을 일으킵니다.
- **`RETURNING`은 왜 실무에서 특히 유용할까요?**
  - 데이터 변경 작업은 트랜잭션으로 감싸서, 실수한 경우 ROLLBACK으로 되돌릴 수 있도록 습관 들이는 것이 좋습니다.

<!-- toc:begin -->
## 시리즈 목차

- [SQL 101 (1/10): SQL이란 무엇인가?](./01-what-is-sql.md)
- [SQL 101 (2/10): SELECT 기본](./02-select-basics.md)
- [SQL 101 (3/10): WHERE와 조건](./03-where-and-conditions.md)
- [SQL 101 (4/10): JOIN 이해하기](./04-join.md)
- [SQL 101 (5/10): GROUP BY와 집계 함수](./05-group-by-and-aggregate.md)
- [SQL 101 (6/10): 서브쿼리와 CTE](./06-subquery.md)
- [SQL 101 (7/10): 윈도 함수](./07-window-function.md)
- **데이터를 바꾸는 SQL — INSERT, UPDATE, DELETE (현재 글)**
- 인덱스와 쿼리 계획 (예정)
- 실전 분석 SQL (예정)

<!-- toc:end -->

## 참고 자료

- [PostgreSQL — INSERT](https://www.postgresql.org/docs/current/sql-insert.html)
- [PostgreSQL — UPDATE](https://www.postgresql.org/docs/current/sql-update.html)
- [PostgreSQL — DELETE](https://www.postgresql.org/docs/current/sql-delete.html)
- [PostgreSQL — Transactions](https://www.postgresql.org/docs/current/tutorial-transactions.html)

Tags: SQL, Database, Postgres, Analytics
