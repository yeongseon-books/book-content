
# 데이터베이스

> Computer Science 101 시리즈 (8/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 수억 건의 데이터에서 원하는 한 줄을 어떻게 1ms 만에 찾아낼 수 있을까요?

> 데이터베이스는 대량의 데이터를 영구적으로 저장하고, 동시에 여러 사용자가 안전하게 읽고 쓸 수 있게 해 줍니다. SQL은 그 데이터를 다루는 표준 언어이고, 인덱스는 빠른 조회를 가능케 하는 자료구조이며, 트랜잭션은 데이터 일관성을 지켜 줍니다. 이 글에서는 SQL의 기초, 인덱스의 원리, ACID 트랜잭션, 그리고 자주 마주치는 성능 함정을 다룹니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 관계형 데이터베이스의 기본 개념
- SQL로 데이터를 조회·수정하는 법
- 인덱스가 어떻게 조회를 빠르게 만드는가
- 트랜잭션과 ACID

## 왜 중요한가

대부분의 서비스 장애는 데이터베이스에서 일어납니다. 느린 쿼리 하나가 전체 시스템을 마비시키고, 트랜잭션 한 줄을 놓치면 데이터가 깨집니다. SQL과 인덱스, 트랜잭션을 이해하지 못하면 백엔드 엔지니어로 성장할 수 없습니다.

> DB는 단순한 저장소가 아니라 동시성과 일관성을 책임지는 시스템

쿼리는 짧지만 그 뒤에는 깊은 알고리즘이 있습니다.

## 개념 한눈에 보기

> 인덱스는 책의 색인과 같습니다. 본문 전체를 뒤지지 않고 색인을 따라 곧장 페이지를 펼칩니다.

```text
인덱스 없이 SELECT * FROM users WHERE email = 'a@b.com'
  → 모든 행을 스캔 (Full Table Scan)  — O(n)

인덱스 있을 때 (B-Tree)
  → 트리에서 이진 탐색       — O(log n)

100만 행 기준
  - 풀 스캔  : 약 1,000,000번 비교
  - B-Tree   : 약 20번 비교
```

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| 테이블(table) | 행과 열로 구성된 관계형 데이터의 기본 단위 |
| 기본 키(primary key) | 행을 유일하게 식별하는 컬럼 |
| 인덱스(index) | 특정 컬럼 값으로 빠르게 행을 찾기 위한 자료구조 (보통 B-Tree) |
| 트랜잭션(transaction) | 여러 SQL을 하나의 논리적 단위로 묶는 작업 |
| ACID | 트랜잭션이 만족해야 하는 4가지 성질: 원자성·일관성·고립성·지속성 |
| 쿼리 플래너 | SQL을 어떻게 실행할지 결정하는 DB 컴포넌트 |

## Before / After

**Before — 인덱스 없이 N+1 쿼리:**

```python
# 사용자 100명의 주문을 가져오기 — 101번의 쿼리
users = cursor.execute("SELECT id FROM users").fetchall()
orders = []
for (user_id,) in users:
    cursor.execute("SELECT * FROM orders WHERE user_id = ?", (user_id,))
    orders.extend(cursor.fetchall())
```

**After — JOIN과 인덱스 활용:**

```python
# 한 번의 쿼리로 끝, user_id에 인덱스가 있으면 빠릅니다
cursor.execute("""
    SELECT u.id, o.id, o.amount
    FROM users u
    JOIN orders o ON o.user_id = u.id
""")
orders = cursor.fetchall()
```

## 실습: 단계별로 따라하기

### 1단계: SQLite로 작은 DB 만들기

```python
import sqlite3

conn = sqlite3.connect(":memory:")
cur = conn.cursor()

cur.executescript("""
    CREATE TABLE users (
        id    INTEGER PRIMARY KEY,
        email TEXT NOT NULL UNIQUE,
        name  TEXT NOT NULL
    );

    CREATE TABLE orders (
        id      INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id),
        amount  INTEGER NOT NULL
    );
""")

cur.executemany(
    "INSERT INTO users (email, name) VALUES (?, ?)",
    [("a@x.com", "Alice"), ("b@x.com", "Bob"), ("c@x.com", "Carol")],
)
cur.executemany(
    "INSERT INTO orders (user_id, amount) VALUES (?, ?)",
    [(1, 1000), (1, 500), (2, 700)],
)
conn.commit()
```

### 2단계: 기본 쿼리

```python
# SELECT
for row in cur.execute("SELECT id, email FROM users"):
    print(row)

# WHERE + ORDER BY + LIMIT
for row in cur.execute(
    "SELECT name, email FROM users WHERE name LIKE 'A%' ORDER BY id LIMIT 10"
):
    print(row)

# JOIN
for row in cur.execute("""
    SELECT u.name, SUM(o.amount) AS total
    FROM users u
    LEFT JOIN orders o ON o.user_id = u.id
    GROUP BY u.id
"""):
    print(row)
```

### 3단계: 인덱스가 만드는 차이

```python
import sqlite3
import time
import random

conn = sqlite3.connect(":memory:")
cur = conn.cursor()
cur.execute("CREATE TABLE big (id INTEGER PRIMARY KEY, k INTEGER, v TEXT)")
cur.executemany(
    "INSERT INTO big (k, v) VALUES (?, ?)",
    [(random.randint(0, 10_000_000), "x") for _ in range(200_000)],
)
conn.commit()

target = 12345

start = time.perf_counter()
cur.execute("SELECT COUNT(*) FROM big WHERE k = ?", (target,)).fetchone()
print(f"인덱스 전: {time.perf_counter() - start:.4f}s")

cur.execute("CREATE INDEX idx_big_k ON big(k)")

start = time.perf_counter()
cur.execute("SELECT COUNT(*) FROM big WHERE k = ?", (target,)).fetchone()
print(f"인덱스 후: {time.perf_counter() - start:.6f}s")
```

### 4단계: EXPLAIN QUERY PLAN으로 들여다보기

```python
for row in cur.execute("EXPLAIN QUERY PLAN SELECT * FROM big WHERE k = 12345"):
    print(row)
# (… USING INDEX idx_big_k …) 같은 줄이 보이면 인덱스를 사용하는 것
```

### 5단계: 트랜잭션과 ACID

```python
conn = sqlite3.connect(":memory:")
cur = conn.cursor()
cur.execute("CREATE TABLE accounts (id INTEGER PRIMARY KEY, balance INTEGER)")
cur.executemany(
    "INSERT INTO accounts (id, balance) VALUES (?, ?)",
    [(1, 1000), (2, 1000)],
)
conn.commit()


def transfer(src: int, dst: int, amount: int) -> None:
    """원자적으로 두 계좌 간 이체 — 둘 다 성공하거나 둘 다 실패."""
    try:
        cur.execute("BEGIN")
        cur.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, src))
        cur.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, dst))
        conn.commit()
    except Exception:
        conn.rollback()
        raise


transfer(1, 2, 300)
print(cur.execute("SELECT * FROM accounts").fetchall())
```

## 이 코드에서 주목할 점

- 인덱스 하나로 같은 쿼리가 수백 배 빨라질 수 있습니다
- N+1 쿼리는 거의 항상 JOIN 또는 IN 절로 한 번에 해결할 수 있습니다
- 트랜잭션은 부분 실패를 막아 데이터 정합성을 지킵니다
- `EXPLAIN`/`EXPLAIN QUERY PLAN`은 모든 DB의 필수 디버깅 도구입니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 자주 조회하는 컬럼에 인덱스 없음 | 풀 스캔으로 응답 지연 | `EXPLAIN`을 보고 인덱스 추가 |
| 모든 컬럼에 인덱스 추가 | 쓰기 성능·디스크 사용량 폭증 | 자주 쓰는 조회 패턴에만 |
| 트랜잭션 누락 | 부분 적용으로 데이터 깨짐 | 관련 변경은 `BEGIN`/`COMMIT`으로 묶기 |
| ORM의 lazy loading 방치 | N+1 쿼리 발생 | `select_related`/`joinedload` 등 명시적 로딩 |
| 트랜잭션 안에서 외부 API 호출 | 락 점유 시간 폭증 | DB 트랜잭션은 짧게, 외부 호출은 밖에서 |

## 실무에서는 이렇게 쓰입니다

- 백엔드 API의 거의 모든 영구 저장소
- 분석용 OLAP DB(ClickHouse, BigQuery)와 트랜잭션용 OLTP DB의 분리
- 인덱스 설계와 쿼리 튜닝이 응답 시간 SLO를 좌우
- 트랜잭션 격리 수준 선택 — Read Committed, Repeatable Read, Serializable
- 마이그레이션 전략 — Zero-downtime schema change, online DDL

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 SQL을 짤 때 항상 "이 쿼리의 실행 계획은 어떨까"를 떠올립니다. 화면에 보이는 SQL과 DB가 실제로 수행하는 단계는 다릅니다. EXPLAIN으로 인덱스 사용 여부를 확인하고, 행 수와 비용을 보면서 쿼리를 다듬습니다.

또한 데이터베이스가 시스템의 상태를 가진 가장 위험한 부품이라는 점을 압니다. 코드 배포는 되돌릴 수 있어도 잘못된 마이그레이션은 되돌리기 어렵습니다. 그래서 모든 스키마 변경은 backward-compatible하게, 모든 트랜잭션은 짧게, 모든 운영 SQL은 `EXPLAIN` 후에 실행한다는 원칙을 따릅니다.

## 체크리스트

- [ ] 기본 키와 인덱스의 차이를 설명할 수 있는가
- [ ] WHERE 절에 인덱스가 걸리는 컬럼인지 확인하는 습관이 있는가
- [ ] 트랜잭션 안과 밖에서 무엇을 해야 하는지 구분하는가
- [ ] N+1 쿼리 문제를 알아차리고 고칠 수 있는가
- [ ] 운영 환경에 SQL을 쏘기 전에 `EXPLAIN`을 확인하는가

## 연습 문제

1. 200만 행짜리 테이블을 만들어 인덱스 추가 전·후의 `SELECT` 시간을 측정하세요.

2. 사용자별 주문 합계를 (a) N+1 쿼리, (b) 단일 JOIN+GROUP BY로 각각 작성하고 시간을 비교하세요.

3. 두 계좌 간 이체 함수에서 중간에 예외가 발생하는 경우 잔액이 깨지지 않는지 트랜잭션을 활용해 검증하세요.

## 정리 및 다음 단계

데이터베이스는 데이터를 영구적으로 보관하고, 동시 접근에서도 일관성을 보장합니다. SQL은 그 데이터를 다루는 언어, 인덱스는 빠른 조회를 가능케 하는 자료구조, 트랜잭션은 무결성을 지키는 장치입니다. EXPLAIN으로 쿼리를 들여다보는 습관이 좋은 백엔드 엔지니어를 만듭니다.

다음 글에서는 이 모든 시스템을 안정적으로 만들고 유지하는 방법 — 소프트웨어 엔지니어링 — 을 다룹니다.

- [Computer Science란 무엇인가?](./01-what-is-computer-science.md)
- [계산과 프로그램](./02-computation-and-programs.md)
- [데이터 표현](./03-data-representation.md)
- [알고리즘과 복잡도](./04-algorithms-and-complexity.md)
- [컴퓨터 구조](./05-computer-architecture.md)
- [운영체제](./06-operating-systems.md)
- [네트워크](./07-networks.md)
- **데이터베이스 (현재 글)**
- [소프트웨어 엔지니어링](./09-software-engineering.md)
- [AI와 데이터사이언스까지의 연결](./10-ai-and-data-science.md)
## 참고 자료

- [PostgreSQL — Documentation](https://www.postgresql.org/docs/current/)
- [Use The Index, Luke! — SQL 인덱싱 가이드](https://use-the-index-luke.com/)
- [SQLite EXPLAIN QUERY PLAN](https://www.sqlite.org/eqp.html)
- [Designing Data-Intensive Applications — Martin Kleppmann](https://dataintensive.net/)

Tags: Computer Science, 데이터베이스, SQL, 인덱스, 트랜잭션, ACID

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
