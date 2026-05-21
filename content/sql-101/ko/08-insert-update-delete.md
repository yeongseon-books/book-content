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

이 글은 SQL 101 시리즈의 여덟 번째 글입니다. 여기서는 `INSERT`, `UPDATE`, `DELETE`를 단순한 문법이 아니라, 트랜잭션과 검증 절차 안에서 안전하게 실행하는 작업으로 설명합니다.

지금까지는 주로 데이터를 읽는 SQL을 다뤘습니다. 하지만 운영 환경에서 더 긴장되는 순간은 데이터를 바꿀 때입니다. 한 줄의 `UPDATE`나 `DELETE`가 서비스 데이터 전체에 영향을 줄 수 있기 때문입니다. 그래서 데이터를 바꾸는 SQL은 읽는 SQL보다 훨씬 더 보수적으로 다뤄야 합니다.


![SQL 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/sql-101/08/08-01-safe-data-change-flow.ko.png)
*SQL 101 8장 흐름 개요*
> INSERT, UPDATE, DELETE의 핵심은 데이터 변경의 문법이 아니라, 어떤 행을 어떤 순서로 변경할 때 데이터 일관성과 비즈니스 규칙이 깨지지 않는지 사전에 검증하는 데 있습니다.

## 먼저 던지는 질문

- `INSERT`, `UPDATE`, `DELETE`의 기본 형태는 무엇일까요?
- 트랜잭션은 왜 데이터 변경 작업의 기본 안전망일까요?
- `RETURNING`은 왜 실무에서 특히 유용할까요?

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


## 실전 앵커: 변경 작업의 기본 루틴

대량 변경에서는 "바로 실행"보다 "검증 후 실행"이 기본입니다.

1. 같은 조건으로 `SELECT`를 먼저 실행해 영향 행 수를 확인합니다.
2. 트랜잭션을 시작하고 변경합니다.
3. `RETURNING`으로 실제 변경 행을 검토합니다.
4. 기대와 다르면 `ROLLBACK`, 맞으면 `COMMIT`합니다.

```sql
BEGIN;

SELECT COUNT(*)
FROM orders
WHERE status = 'pending'
  AND ordered_at < CURRENT_DATE - INTERVAL '30 days';

UPDATE orders
SET status = 'expired'
WHERE status = 'pending'
  AND ordered_at < CURRENT_DATE - INTERVAL '30 days'
RETURNING order_id, customer_id, status;

COMMIT;
```

## 실전 앵커: 배치 삭제와 잠금 경합 완화

큰 테이블에서 한 번에 삭제하면 잠금과 WAL 부담이 커집니다.

```sql
-- 배치 단위 삭제
DELETE FROM event_logs
WHERE log_id IN (
    SELECT log_id
    FROM event_logs
    WHERE created_at < CURRENT_DATE - INTERVAL '180 days'
    ORDER BY log_id
    LIMIT 5000
);
```

작은 배치를 반복하면 서비스 트래픽과 공존하기가 훨씬 수월합니다.

## 실전 앵커: 업데이트 범위 오염 방지

조인 업데이트는 편리하지만 조건을 잘못 쓰면 범위가 폭발합니다.

```sql
UPDATE orders o
SET risk_grade = r.risk_grade
FROM risk_snapshot r
WHERE o.customer_id = r.customer_id
  AND r.snapshot_date = CURRENT_DATE;
```

이때 `risk_snapshot`의 키 유일성을 먼저 확인해야 합니다. 키가 중복되면 같은 행이 여러 번 매칭되어 예상치 못한 결과가 나올 수 있습니다.

## 실전 앵커: 변경 전후 비교 쿼리

운영에서 가장 도움이 되는 습관은 변경 전후를 같은 SQL로 기록하는 것입니다.

```sql
SELECT status, COUNT(*)
FROM orders
GROUP BY status
ORDER BY status;
```

변경 전 결과와 변경 후 결과를 티켓/PR에 함께 남기면, 장애 대응 속도와 리뷰 신뢰도가 크게 올라갑니다.


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


## 추가 실습 메모: 운영에서 바로 쓰는 검증 질문

아래 질문 네 가지를 기준으로 쿼리를 다시 읽어 보면, 단순히 동작하는 SQL과 운영에 견디는 SQL을 구분할 수 있습니다.

- 이 쿼리는 같은 날 다시 실행해도 같은 결과를 재현할 수 있는가
- 조건절이 인덱스를 활용할 수 있는 형태로 작성되었는가
- 조인 이후 행 수가 의도대로 증가 또는 유지되는가
- 실행 계획에서 가장 비싼 노드가 무엇인지 설명할 수 있는가

짧은 쿼리라도 이 질문을 통과하면, 장애 대응과 지표 신뢰도에서 차이가 크게 납니다.

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

- [book-examples/sql-101 (ko)](https://github.com/yeongseon-books/book-examples/tree/main/sql-101/ko)

- [PostgreSQL — INSERT](https://www.postgresql.org/docs/current/sql-insert.html)
- [PostgreSQL — UPDATE](https://www.postgresql.org/docs/current/sql-update.html)
- [PostgreSQL — DELETE](https://www.postgresql.org/docs/current/sql-delete.html)
- [PostgreSQL — Transactions](https://www.postgresql.org/docs/current/tutorial-transactions.html)

Tags: SQL, Database, Postgres, Analytics
