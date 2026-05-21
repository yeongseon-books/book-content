---
series: computer-science-101
episode: 8
title: "Computer Science 101 (8/10): 데이터베이스"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
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
seo_description: SQL, 인덱스, 트랜잭션이 데이터베이스 성능과 무결성을 어떻게 좌우하는지 설명합니다.
last_reviewed: '2026-05-12'
---

# Computer Science 101 (8/10): 데이터베이스

수억 행 중 한 행을 1ms 안에 찾는 일은 SQL 문장 자체보다 그 뒤에 숨어 있는 자료구조와 실행 계획의 힘에 가깝습니다. 서비스 장애가 데이터베이스에서 시작되는 이유도, 짧은 쿼리 뒤에 깊은 비용이 숨어 있기 때문입니다.

이 글은 Computer Science 101 시리즈의 8번째 글입니다.

여기서는 관계형 데이터베이스의 기본 개념, SQL 조회와 수정, 인덱스, 트랜잭션과 ACID를 실무 중심으로 정리하겠습니다.

## 먼저 던지는 질문

- 데이터베이스는 많은 데이터를 어떻게 영구 저장하고 동시에 안전하게 읽고 쓸까요?
- 인덱스는 왜 조회 속도를 급격하게 바꿀까요?
- SQL 한 줄과 실제 실행 계획 사이에는 어떤 차이가 있을까요?

## 큰 그림

![Computer Science 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-101/08/08-01-concept-at-a-glance.ko.png)

*Computer Science 101 8장 흐름 개요*

## 이 글에서 배울 것

- 관계형 데이터베이스의 기본 개념
- SQL로 데이터를 조회하고 수정하는 방법
- 인덱스가 조회를 빠르게 만드는 원리
- 트랜잭션과 ACID의 의미

## 왜 중요한가

대부분의 서비스 장애는 데이터베이스에서 일어납니다. 느린 쿼리 하나가 전체 시스템을 마비시키고, 트랜잭션 한 줄을 놓치면 데이터가 깨집니다. SQL과 인덱스, 트랜잭션을 이해하지 못하면 백엔드 엔지니어로 성장할 수 없습니다.

> DB는 단순한 저장소가 아니라 동시성과 일관성을 책임지는 시스템

쿼리는 짧지만 그 뒤에는 깊은 알고리즘이 있습니다.

## 한눈에 보는 개념

> 인덱스는 책의 색인과 같습니다. 본문 전체를 뒤지지 않고 색인을 따라 곧장 페이지를 펼칩니다.

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| Table | 행과 열로 구성된 관계형 데이터의 기본 단위 |
| Primary key | 한 행을 유일하게 식별하는 열 |
| Index | 특정 열 기준으로 행을 빠르게 찾게 해 주는 자료구조 |
| Transaction | 여러 SQL 문을 하나의 논리 작업으로 묶는 단위 |
| ACID | 원자성·일관성·격리성·지속성 네 가지 속성 |
| Query planner | SQL을 어떤 방식으로 실행할지 결정하는 DB 구성 요소 |

## Before / After

**Before — 인덱스 없이 N+1 쿼리:**

```python
# Fetch orders for 100 users — 101 queries
users = cursor.execute("SELECT id FROM users").fetchall()
orders = []
for (user_id,) in users:
    cursor.execute("SELECT * FROM orders WHERE user_id = ?", (user_id,))
    orders.extend(cursor.fetchall())
```

**After — JOIN과 인덱스 활용:**

```python
# A single query, fast when user_id is indexed
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
print(f"before index: {time.perf_counter() - start:.4f}s")

cur.execute("CREATE INDEX idx_big_k ON big(k)")

start = time.perf_counter()
cur.execute("SELECT COUNT(*) FROM big WHERE k = ?", (target,)).fetchone()
print(f"after  index: {time.perf_counter() - start:.6f}s")
```

**Expected output:** `after index`가 `before index`보다 훨씬 짧아지고, 이어지는 `EXPLAIN QUERY PLAN`에서 인덱스 사용 여부를 확인할 수 있어야 합니다.

### 4단계: EXPLAIN QUERY PLAN으로 들여다보기

```python
for row in cur.execute("EXPLAIN QUERY PLAN SELECT * FROM big WHERE k = 12345"):
    print(row)
# A line like (… USING INDEX idx_big_k …) confirms the index is used
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
    """Atomic transfer between two accounts — both succeed or both fail."""
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

## 이 코드에서 먼저 봐야 할 점

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

시니어 엔지니어는 SQL을 쓰면서 동시에 실행 계획을 머릿속에 그립니다. 화면에 보이는 SQL과 DB가 실제로 밟는 단계는 다르기 때문에, `EXPLAIN`으로 인덱스 사용과 예상 row 수를 먼저 확인합니다.

또한 데이터베이스는 시스템에서 가장 위험한 상태 저장 구성 요소라는 사실을 압니다. 코드 배포는 롤백할 수 있어도 잘못된 마이그레이션은 되돌리기 어렵습니다. 그래서 스키마 변경은 항상 호환 가능하게, 트랜잭션은 짧게, 운영 SQL은 실행 전 `EXPLAIN`으로 검증합니다.

## 체크리스트

- [ ] 기본 키와 인덱스의 차이를 설명할 수 있는가
- [ ] WHERE 절에 인덱스가 걸리는 컬럼인지 확인하는 습관이 있는가
- [ ] 트랜잭션 안과 밖에서 무엇을 해야 하는지 구분하는가
- [ ] N+1 쿼리 문제를 알아차리고 고칠 수 있는가
- [ ] 운영 환경에 SQL을 쏘기 전에 `EXPLAIN`을 확인하는가

## 연습 문제

1. 200만 행짜리 테이블을 만들고 인덱스 추가 전후의 `SELECT` 시간을 측정해 보세요.
2. 사용자별 주문 총액을 (a) N+1 쿼리와 (b) JOIN + GROUP BY 한 번으로 각각 구해 시간을 비교해 보세요.
3. 중간에 예외를 발생시키는 계좌 이체 함수를 만들어 트랜잭션이 일관성을 지키는지 확인해 보세요.

## 정리 및 다음 단계

데이터베이스는 데이터를 영구적으로 보관하고, 동시 접근에서도 일관성을 보장합니다. SQL은 그 데이터를 다루는 언어, 인덱스는 빠른 조회를 가능케 하는 자료구조, 트랜잭션은 무결성을 지키는 장치입니다. EXPLAIN으로 쿼리를 들여다보는 습관이 좋은 백엔드 엔지니어를 만듭니다.

다음 글에서는 이 모든 시스템을 안정적으로 만들고 유지하는 방법 — 소프트웨어 엔지니어링 — 을 다룹니다.


## 학습 설계 지도: 이 글을 커리큘럼에 연결하기

컴퓨터 과학 입문을 빠르게 끝내는 접근보다, 서로 연결된 개념을 축적하는 접근이 이후 학습 효율을 높입니다. 이 글의 핵심 개념은 단독 지식이 아니라 운영체제, 네트워크, 데이터베이스, 소프트웨어 공학으로 이어지는 선행 지식입니다. 따라서 한 주 단위 학습에서 이 글을 기준점으로 삼고, 다음과 같은 연결 훈련을 함께 수행하는 것이 좋습니다.

| 학습 축 | 이 글에서 확인할 포인트 | 다음 과목 연결 |
| --- | --- | --- |
| 계산 모델 | 입력, 상태, 출력의 관계를 명확히 정의 | 알고리즘 설계, 분산 시스템 모델링 |
| 추상화 | 세부 구현을 숨기고 인터페이스를 구분 | API 설계, 모듈 경계 설계 |
| 자원 제약 | 시간·메모리·I/O 비용을 동시에 고려 | 성능 튜닝, 인프라 비용 최적화 |
| 검증 가능성 | 주장 대신 측정과 반례로 판단 | 테스트 전략, 실험 설계 |

연결 학습을 할 때는 "개념 정의 1회 + 사례 적용 2회 + 반례 점검 1회" 구조를 반복합니다. 예를 들어 시간 복잡도를 배웠다면, 단순히 O 표기법을 외우지 않고 입력 크기 변화에 따른 실행 시간 그래프를 직접 기록합니다. 그래프가 기대와 다를 때 원인을 추정하고, 캐시 지역성이나 상수항의 영향을 설명해 보는 과정이 필요합니다. 이 연습이 쌓이면 글에서 다룬 개념이 시험 대비 지식이 아니라 실무 의사결정 기준으로 바뀝니다.

또한 과목 간 언어를 통일해 두는 것이 중요합니다. 같은 현상을 운영체제에서는 스케줄링, 네트워크에서는 큐잉, 데이터베이스에서는 트랜잭션 대기라고 부를 수 있습니다. 이름은 달라도 "경합 상태에서 자원을 배분한다"는 본질은 동일합니다. 학습 노트에 용어 사전을 만들어 개념 동치 관계를 표시해 두면, 새로운 분야를 배울 때 기존 이해를 재사용하기 쉬워집니다.

마지막으로 주간 복습은 요약보다 질문 중심으로 구성합니다. "왜 이 추상화가 필요한가", "어떤 조건에서 깨지는가", "대안의 비용은 무엇인가"를 각각 한 문장으로 답하면 학습 깊이가 빠르게 올라갑니다. 이렇게 축적한 질문-답변 세트는 면접, 설계 리뷰, 코드 리뷰에서 그대로 활용 가능한 사고 프레임이 됩니다.

데이터베이스 단원에서는 인덱스 구조와 트랜잭션 격리 수준이 질의 성능과 정합성에 주는 트레이드오프를 사례로 점검합니다.


## 처음 질문으로 돌아가기

- **데이터베이스는 많은 데이터를 어떻게 영구 저장하고 동시에 안전하게 읽고 쓸까요?**
  - 본문의 기준은 데이터베이스를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **인덱스는 왜 조회 속도를 급격하게 바꿀까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **SQL 한 줄과 실제 실행 계획 사이에는 어떤 차이가 있을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Computer Science 101 (1/10): Computer Science란 무엇인가?](./01-what-is-computer-science.md)
- [Computer Science 101 (2/10): 계산과 프로그램](./02-computation-and-programs.md)
- [Computer Science 101 (3/10): 데이터 표현](./03-data-representation.md)
- [Computer Science 101 (4/10): 알고리즘과 복잡도](./04-algorithms-and-complexity.md)
- [Computer Science 101 (5/10): 컴퓨터 구조](./05-computer-architecture.md)
- [Computer Science 101 (6/10): 운영체제](./06-operating-systems.md)
- [Computer Science 101 (7/10): 네트워크](./07-networks.md)
- **데이터베이스 (현재 글)**
- 소프트웨어 엔지니어링 (예정)
- AI와 데이터사이언스까지의 연결 (예정)

<!-- toc:end -->

## 참고 자료

- [PostgreSQL — Documentation](https://www.postgresql.org/docs/current/)
- [Use The Index, Luke! — SQL 인덱싱 가이드](https://use-the-index-luke.com/)
- [SQLite EXPLAIN QUERY PLAN](https://www.sqlite.org/eqp.html)
- [Designing Data-Intensive Applications — Martin Kleppmann](https://dataintensive.net/)

Tags: Computer Science, 데이터베이스, SQL, 인덱스, 트랜잭션, ACID
