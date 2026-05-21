---
title: "Python DB-API 101 (3/10): execute, executemany, fetch 패턴"
series: python-dbapi-101
episode: 3
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
- Python
- execute
- executemany
- fetchone
- fetchall
- Streaming Iteration
last_reviewed: '2026-05-12'
seo_description: DB-API의 모든 query 실행은 결국 cursor의 execute(), executemany()와 fetchone()…
---

# Python DB-API 101 (3/10): execute, executemany, fetch 패턴

DB-API의 모든 query 실행은 결국 cursor의 `execute()`, `executemany()`와 `fetchone()`, `fetchall()`, `fetchmany()` 다섯 메서드로 압축됩니다. 단순해 보이지만, 어떤 fetch 메서드를 언제 쓰느냐가 메모리 사용량, latency, 그리고 production에서 OOM이 터지는지 여부를 결정합니다. 이 글에서는 다섯 메서드의 동작과 실전 선택 기준을 정리합니다.

이 글은 Python DB-API 101 시리즈의 세 번째 글입니다.

![execute, executemany, and fetch patterns](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/03/03-01-execute-executemany-and-fetch-patterns.ko.png)

*execute, executemany, and fetch patterns*

## 먼저 던지는 질문

- `execute`, `executemany`, `fetchone`, `fetchall`, `fetchmany`는 각각 언제 써야 할까요?
- 큰 결과셋을 메모리를 터뜨리지 않고 처리하려면 어떤 패턴을 써야 할까요?
- `cursor.description`은 어떤 메타데이터를 제공할까요?

## 큰 그림

![Python DB-API 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/03/03-02-1-execute-one-statement-at-a-time.ko.png)

*Python DB-API 101 3장 흐름 개요*

## 1. execute - 한 번의 query

`cursor.execute(operation, parameters=None)`은 single SQL statement를 실행합니다. SELECT, INSERT, UPDATE, DELETE, DDL 모두 동일한 method를 씁니다.

```python
import sqlite3
conn = sqlite3.connect(":memory:")
cur = conn.cursor()

cur.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT)")
cur.execute("INSERT INTO notes (body) VALUES (?)", ("hello",))
print(cur.lastrowid)   # 1
print(cur.rowcount)    # 1
```

`execute()`는 cursor 자신을 반환하므로 chaining이 가능하지만, 가독성을 해치므로 production에서는 한 줄에 한 호출이 권장됩니다.

## 2. executemany - bulk write

![executemany - bulk write](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/03/03-03-2-executemany-bulk-write.ko.png)

*executemany - bulk write*
같은 statement를 여러 parameter set으로 반복 실행할 때 `executemany()`를 씁니다.

```python
rows = [("first",), ("second",), ("third",)]
cur.executemany("INSERT INTO notes (body) VALUES (?)", rows)
print(cur.rowcount)   # 3
conn.commit()
```

`executemany()`는 logical하게 loop + execute와 같지만, driver 차원에서 batch optimization을 수행하므로 보통 2~10배 빠릅니다. 단 driver마다 구현이 다릅니다.

- sqlite3: 내부적으로 loop이지만 prepared statement 재사용으로 parsing 비용 절감
- psycopg 2/3: `execute_batch()` 또는 `execute_values()`가 더 빠른 경우가 많음
- mysql.connector: `executemany()`가 자동으로 multi-row INSERT로 변환

`executemany()`의 흔한 함정은 SELECT에 쓰는 것입니다. PEP 249는 SELECT에서의 동작을 정의하지 않으므로 결과가 driver-dependent입니다. SELECT는 항상 `execute()` + iteration으로 처리합니다.

## 3. fetchone - 한 row씩

`fetchone()`은 다음 row를 tuple로, 없으면 `None`을 반환합니다.

```python
cur.execute("SELECT id, body FROM notes ORDER BY id")
row = cur.fetchone()
while row is not None:
    print(row)         # (1, 'hello')
    row = cur.fetchone()
```

이 패턴은 memory-safe하지만 코드가 길어집니다. cursor 자체가 iterable이므로 보통은 더 짧게 씁니다.

```python
cur.execute("SELECT id, body FROM notes ORDER BY id")
for row in cur:
    print(row)
```

`for row in cur`는 내부적으로 `fetchone()`을 호출하는 generator처럼 동작하고, 결과를 한 번에 메모리에 올리지 않습니다.

## 4. fetchall - 전체 한 번에

`fetchall()`은 남은 모든 row를 list로 반환합니다.

```python
cur.execute("SELECT id, body FROM notes")
rows = cur.fetchall()
print(rows)   # [(1, 'hello'), (2, 'first'), (3, 'second'), (4, 'third')]
```

작은 결과셋(수백 row 이하)에서는 가장 편하고 빠릅니다. 하지만 row 수가 수만 단위로 커지면 RAM이 한 번에 부풀어 OOM 위험이 생깁니다. test fixture, lookup table 같은 작은 데이터에만 쓰고, 사용자 입력이 row 수를 결정하는 query에는 절대 쓰지 않습니다.

## 5. fetchmany - chunk 단위

![fetchmany - chunk 단위](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/03/03-04-5-fetchmany-in-chunks.ko.png)

*fetchmany - chunk 단위*
`fetchmany(size=cursor.arraysize)`은 지정한 개수만큼만 가져옵니다.

```python
cur.execute("SELECT id, body FROM notes")
while True:
    chunk = cur.fetchmany(1000)
    if not chunk:
        break
    process(chunk)
```

`arraysize`는 cursor 속성으로, 기본값은 1입니다. 이 값을 크게 잡으면 driver가 server-side prefetch를 수행해 round-trip 횟수를 줄입니다.

```python
cur.arraysize = 500
for row in cur:        # prefetched in batches of 500
    process(row)
```

`fetchmany`는 streaming + batch processing이 동시에 필요한 ETL pipeline에 적합합니다.

## 6. 어떤 메서드를 언제 쓰나

| 상황 | 추천 |
| --- | --- |
| 1 row 조회 (PK lookup) | `fetchone()` |
| 작은 결과 (≤1000 row) | `fetchall()` |
| 큰 결과 한 row씩 처리 | `for row in cur` |
| 큰 결과 batch 처리 | `fetchmany(N)` |
| 대량 INSERT/UPDATE | `executemany()` |
| 1회 실행 | `execute()` |

## 7. 결과 메타데이터

`cursor.description`은 마지막 SELECT의 column metadata를 7-tuple list로 반환합니다.

```python
cur.execute("SELECT id, body FROM notes LIMIT 1")
cur.fetchone()
for col in cur.description:
    print(col[0], col[1])   # name, type_code
```

column 이름을 dict로 받고 싶으면 `description`을 직접 쓰거나 row factory를 설정합니다(다음 글들에서 다룹니다).

`cursor.rowcount`는 INSERT/UPDATE/DELETE의 영향받은 row 수를 알려줍니다. SELECT에서는 driver-dependent로 -1이 흔하므로 신뢰하지 않습니다.

## 8. Streaming + transformation 실전 예제

CSV로 export하는 ETL을 streaming + chunk로 작성합니다.

```python
import csv, sqlite3
def export_notes(db_path, csv_path, chunk=500):
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.arraysize = chunk
        cur.execute("SELECT id, body FROM notes ORDER BY id")
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "body"])
            while True:
                rows = cur.fetchmany(chunk)
                if not rows:
                    break
                writer.writerows(rows)
```

이 코드는 row 수와 무관하게 일정한 메모리만 사용합니다.

## 9. 자주 하는 실수

1. **결과셋이 큰 query에 `fetchall()` 호출** - 100만 row가 나오면 그대로 OOM. 항상 결과 크기를 가정하지 않고 streaming pattern을 default로 둡니다.
2. **SELECT에 `executemany()` 사용** - PEP 249가 정의하지 않은 동작. driver마다 결과가 달라 silent bug가 됩니다. SELECT는 `execute()`만 씁니다.
3. **`rowcount`로 SELECT row 수 확인** - 대부분의 driver에서 SELECT의 rowcount는 -1이거나 fetch 후에야 의미 있는 값이 됩니다. count가 필요하면 `SELECT COUNT(*)`를 별도로 던집니다.
4. **`arraysize`를 default 1로 두고 large fetch** - server-side cursor가 있는 driver에서 round-trip이 row 수만큼 발생합니다. ETL에서는 100~1000 사이로 조정합니다.
5. **iteration 중에 같은 cursor로 다른 query 실행** - 진행 중인 결과셋이 invalidate됩니다. cursor를 두 개 만들거나 결과를 list로 받은 뒤 처리합니다.

## 정리

- `execute()`는 단일 statement를, `executemany()`는 같은 statement의 대량 쓰기를 담당합니다.
- `fetchone`/`fetchall`/`fetchmany`/`for row in cur`는 습관이 아니라 결과 크기로 선택해야 합니다.
- `for row in cur`는 큰 결과셋에서 OOM을 막는 streaming 기본 패턴입니다.
- `arraysize`를 조정하면 driver의 prefetch 동작을 활용해 round-trip을 줄일 수 있습니다.
- `rowcount`는 INSERT/UPDATE/DELETE에서만 신뢰하고 SELECT에서는 별도 count query를 사용합니다.

다음 글에서는 parameter binding과 SQL injection 방어를 다룹니다.

<!-- a-grade-example:begin -->

## 체크리스트

- [ ] executemany로 다중 INSERT를 단일 호출로 처리했다.
- [ ] fetchmany로 chunk 단위로 결과를 받아 메모리 사용을 통제했다.
- [ ] cursor.description으로 컬럼 메타데이터를 추출해 dict로 변환했다.
- [ ] Streaming pipeline에서 generator + fetchmany 조합을 사용해 봤다.

<!-- a-grade-example:end -->

## 실전 패턴 추가: connection/cursor/transaction 경계를 명시하는 운영 코드

DB-API 코드는 SQL 문장보다 경계 관리가 더 중요합니다. 연결 수명, 커서 재사용 범위, 커밋/롤백 시점을 코드로 드러내야 장애 시 복구가 쉬워집니다.

```python
import sqlite3
from contextlib import contextmanager
from typing import Iterator

@contextmanager
def db_connection(path: str) -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(path, timeout=5.0)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def transfer(conn: sqlite3.Connection, sender: int, receiver: int, amount: int) -> None:
    if amount <= 0:
        raise ValueError("amount must be positive")

    cur = conn.cursor()
    cur.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, sender))
    cur.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, receiver))

def list_recent(conn: sqlite3.Connection, limit: int = 100) -> list[tuple[int, int, int]]:
    cur = conn.cursor()
    cur.execute(
        "SELECT sender_id, receiver_id, amount FROM transfers ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    return cur.fetchall()
```

이 패턴은 세 가지를 보장합니다. 첫째, 트랜잭션 성공/실패 경계를 컨텍스트 매니저 한 곳에서 통제합니다. 둘째, `execute` 파라미터 바인딩을 강제해 SQL 인젝션 리스크를 줄입니다. 셋째, 읽기/쓰기 함수를 분리해 장애 분석 시 어떤 쿼리가 상태를 바꿨는지 추적이 쉬워집니다. 소규모 서비스라도 이 구조를 일찍 도입하면 운영 중 데이터 정합성 이슈를 크게 줄일 수 있습니다.

## 처음 질문으로 돌아가기

- **`execute`, `executemany`, `fetchone`, `fetchall`, `fetchmany`는 각각 언제 써야 할까요?**
  - 본문의 기준은 execute, executemany, fetch 패턴를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **큰 결과셋을 메모리를 터뜨리지 않고 처리하려면 어떤 패턴을 써야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`cursor.description`은 어떤 메타데이터를 제공할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Python DB-API 101 (1/10): 왜 DB-API 2.0인가 - PEP 249가 푼 문제](./01-why-db-api-pep-249.md)
- [Python DB-API 101 (2/10): Connection과 Cursor Lifecycle](./02-connection-cursor-lifecycle.md)
- **Python DB-API 101 (3/10): execute, executemany, fetch 패턴 (현재 글)**
- Python DB-API 101 (4/10): Parameter binding과 SQL injection 방어 (sqlite3, PEP 249) (예정)
- Python DB-API 101 (5/10): Transaction과 isolation level (sqlite3, PEP 249) (예정)
- Python DB-API 101 (6/10): Row factory와 type adapter (sqlite3, PEP 249) (예정)
- Python DB-API 101 (7/10): PEP 249 예외 계층과 SQLite 에러 처리 (예정)
- Python DB-API 101 (8/10): SQLite Connection 관리: thread-safety, check_same_thread, 그리고 풀링 (예정)
- Python DB-API 101 (9/10): aiosqlite로 비동기 SQLite 다루기 (예정)
- Python DB-API 101 (10/10): SQLite Production 패턴: retry, timeout, 관측성, 백업 (예정)

<!-- toc:end -->

---

## 참고 자료

- [PEP 249 - Cursor methods](https://peps.python.org/pep-0249/#cursor-methods)
- [Python sqlite3 - Cursor.executemany](https://docs.python.org/3/library/sqlite3.html#sqlite3.Cursor.executemany)
- [psycopg 3 - Server-side cursors](https://www.psycopg.org/psycopg3/docs/advanced/cursors.html)
- [SQLite - Optimizing INSERT performance](https://www.sqlite.org/faq.html#q19)

Tags: Python, DB-API, PEP 249, Database
