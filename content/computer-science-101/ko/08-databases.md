---
series: computer-science-101
episode: 8
title: 데이터베이스
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - 데이터베이스
  - SQL
  - 인덱스
  - 트랜잭션
  - ACID
seo_description: 데이터베이스가 데이터를 어떻게 저장·조회·보호하는지 인덱스와 트랜잭션 중심으로 다루는 CS 입문 시리즈입니다.
last_reviewed: '2026-05-11'
---

# 데이터베이스

> Computer Science 101 시리즈 (8/10)


## 이 글에서 다룰 문제

대부분의 서비스 장애는 데이터베이스에서 일어납니다. 느린 쿼리 하나가 전체 시스템을 마비시키고, 트랜잭션 한 줄을 놓치면 데이터가 깨집니다. SQL과 인덱스, 트랜잭션을 이해하지 못하면 백엔드 엔지니어로 성장할 수 없습니다.

> DB는 단순한 저장소가 아니라 동시성과 일관성을 책임지는 시스템

쿼리는 짧지만 그 뒤에는 깊은 알고리즘이 있습니다.

## 전체 흐름
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
# 한 번의 쿼리로 끝나며 user_id 인덱스가 있으면 더 빠릅니다
cursor.execute("""
    SELECT u.id, o.id, o.amount
    FROM users u
    JOIN orders o ON o.user_id = u.id
""")
orders = cursor.fetchall()
```

## 단계별로 따라하기

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
# 전체 행을 조회합니다
for row in cur.execute("SELECT id, email FROM users"):
    print(row)

# 조건 필터링 후 정렬하고 일부만 가져옵니다
for row in cur.execute(
    "SELECT name, email FROM users WHERE name LIKE 'A%' ORDER BY id LIMIT 10"
):
    print(row)

# 테이블을 조인해 함께 조회합니다
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
# (... USING INDEX idx_big_k ...) 같은 문구가 보이면 인덱스를 사용한 것입니다
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

## 체크리스트

- [ ] 기본 키와 인덱스의 차이를 설명할 수 있는가
- [ ] WHERE 절에 인덱스가 걸리는 컬럼인지 확인하는 습관이 있는가
- [ ] 트랜잭션 안과 밖에서 무엇을 해야 하는지 구분하는가
- [ ] N+1 쿼리 문제를 알아차리고 고칠 수 있는가
- [ ] 운영 환경에 SQL을 쏘기 전에 `EXPLAIN`을 확인하는가

## 정리 및 다음 단계

데이터베이스는 데이터를 영구적으로 보관하고, 동시 접근에서도 일관성을 보장합니다. SQL은 그 데이터를 다루는 언어, 인덱스는 빠른 조회를 가능케 하는 자료구조, 트랜잭션은 무결성을 지키는 장치입니다. EXPLAIN으로 쿼리를 들여다보는 습관이 좋은 백엔드 엔지니어를 만듭니다.

다음 글에서는 이 모든 시스템을 안정적으로 만들고 유지하는 방법 — 소프트웨어 엔지니어링 — 을 다룹니다.

<!-- toc:begin -->
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
<!-- toc:end -->

## 참고 자료

- [PostgreSQL — Documentation](https://www.postgresql.org/docs/current/)
- [Use The Index, Luke! — SQL 인덱싱 가이드](https://use-the-index-luke.com/)
- [SQLite EXPLAIN QUERY PLAN](https://www.sqlite.org/eqp.html)
- [Designing Data-Intensive Applications — Martin Kleppmann](https://dataintensive.net/)

Tags: Computer Science, 데이터베이스, SQL, 인덱스, 트랜잭션, ACID
