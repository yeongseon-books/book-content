---
title: "Python DB-API 101 (2/10): Connection과 Cursor Lifecycle"
series: python-dbapi-101
episode: 2
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
- Connection
- Cursor
- Context Manager
- Resource Management
- SQLite
last_reviewed: '2026-05-12'
seo_description: connection과 cursor의 역할을 이해하고 context manager로 자원 누수 없이 DB 연결을 관리하는 실전 패턴을 정리합니다.
---

# Python DB-API 101 (2/10): Connection과 Cursor Lifecycle

DB-API의 두 핵심 객체는 connection과 cursor입니다. 이름은 평범하지만, 둘의 lifecycle을 잘못 다루면 connection leak, lock, race condition이 줄줄이 생깁니다. 이 글에서는 두 객체가 어떻게 만들어지고 살고 닫히는지, context manager로 안전하게 관리하는 패턴, 그리고 자주 빠지는 lifecycle 함정을 정리합니다.

이 글은 Python DB-API 101 시리즈의 두 번째 글입니다.

![Connection and cursor lifecycle](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/02/02-01-connection-and-cursor-lifecycle.ko.png)

*Connection and cursor lifecycle*

## 먼저 던지는 질문

- Connection과 cursor는 각각 어떤 책임을 가질까요?
- `with` context manager는 connection과 cursor 자원을 어떻게 보호할까요?
- 호출마다 새 connection을 여는 방식과 재사용하는 방식은 어떤 차이를 만들까요?

## 큰 그림

![Python DB-API 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/02/02-02-1-what-a-connection-is.ko.png)

*Python DB-API 101 2장 흐름 개요*

## 1. Connection이란

Connection은 application과 database 사이의 단일 통신 채널입니다. TCP socket(PostgreSQL, MySQL) 또는 file handle(SQLite)을 감싼 객체이고, 한 connection은 한 transaction context를 가집니다.

```python
import sqlite3
conn = sqlite3.connect("notes.db")
print(type(conn))           # <class 'sqlite3.Connection'>
print(conn.in_transaction)  # False (no query yet)
```

`sqlite3.connect()`의 인자 몇 가지를 살펴보면 lifecycle을 더 잘 이해할 수 있습니다.

```python
conn = sqlite3.connect(
    "notes.db",
    timeout=5.0,                  # how long to wait for a lock
    isolation_level="DEFERRED",   # transaction-begin strategy (None == autocommit)
    check_same_thread=True,       # disallow cross-thread use
    cached_statements=128,        # statement cache size
)
```

## 2. Cursor란

Cursor는 single query 실행 단위입니다. connection 안에 cursor를 여러 개 만들 수 있고, 각 cursor는 자기 result set을 들고 있습니다.

```python
cur = conn.cursor()
cur.execute("SELECT 1")
print(cur.description)  # column metadata of the last query
print(cur.rowcount)     # number of affected rows
```

SQLite는 단일 file이라 cursor가 사실상 thin wrapper지만, PostgreSQL은 cursor당 server-side state(특히 `cursor("name")`로 만든 named cursor)를 가집니다. 그래서 닫는 습관이 중요합니다.

## 3. Context manager로 안전하게

![Context manager로 안전하게](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/02/02-03-3-safe-use-with-context-managers.ko.png)

*Context manager로 안전하게*
수동 close는 빠뜨리기 쉽습니다. Python의 `with` 문이 가장 안전합니다.

```python
import sqlite3

with sqlite3.connect("notes.db") as conn:
    cur = conn.cursor()
    cur.execute("INSERT INTO notes (title) VALUES (?)", ("hello",))
    # On block exit, SQLite auto-commits or rolls back the transaction.
```

주의: SQLite의 `Connection`을 `with`로 쓰면 connection을 닫는 게 아니라 transaction만 commit/rollback 합니다. connection 자체를 닫으려면 명시적으로 `conn.close()`를 호출하거나 외부 wrapper를 만들어야 합니다.

```python
from contextlib import contextmanager

@contextmanager
def open_db(path):
    conn = sqlite3.connect(path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

with open_db("notes.db") as conn:
    conn.execute("INSERT INTO notes (title) VALUES (?)", ("hi",))
```

이 패턴은 production code에서 거의 표준입니다. exception 발생 시 rollback, 성공 시 commit, 어떤 경우든 close 보장.

## 4. Cursor lifecycle 세부

```python
with sqlite3.connect("notes.db") as conn:
    cur = conn.cursor()
    cur.execute("SELECT id, title FROM notes")
    while True:
        row = cur.fetchone()
        if row is None:
            break
        print(row)
    cur.close()
```

cursor는 한 번에 하나의 active query만 가집니다. 같은 cursor에 새 `execute()`를 하면 이전 result set은 사라집니다. 두 query 결과를 동시에 들고 있으려면 cursor 두 개를 만드세요.

```python
cur1 = conn.cursor()
cur2 = conn.cursor()
cur1.execute("SELECT id FROM users")
cur2.execute("SELECT id FROM orders")
# Both result sets are alive at the same time.
```

## 5. Connection 재사용 vs 매번 열기

![Connection 재사용 vs 매번 열기](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/02/02-04-5-reusing-vs-reopening-a-connection.ko.png)

*Connection 재사용 vs 매번 열기*
매 query마다 새 connection을 여는 코드는 보기 깔끔하지만 비용이 큽니다.

```python
# Inefficient — connect/close on every call
def get_note(note_id):
    with sqlite3.connect("notes.db") as conn:
        return conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
```

SQLite 파일 connection은 약 1~2ms이지만, PostgreSQL TCP + auth handshake는 수십 ms입니다. 그래서:

- single-user CLI: 매번 열어도 OK
- multi-request server: connection pool (8편)
- long-running script: 한 번 열고 재사용

```python
# For long-running processes
class NoteRepo:
    def __init__(self, path):
        self.conn = sqlite3.connect(path)

    def get(self, note_id):
        return self.conn.execute(
            "SELECT * FROM notes WHERE id = ?", (note_id,)
        ).fetchone()

    def close(self):
        self.conn.close()
```

## 6. close 누락은 어떻게 보이나

connection을 안 닫으면:

- SQLite: file handle 누수, OS 한계 도달 시 `Too many open files`
- PostgreSQL: `pg_stat_activity`에 좀비 connection 누적, `max_connections` 초과 시 신규 접속 거부
- MySQL: `SHOW PROCESSLIST`에 sleeping connection, 일정 시간 후 server timeout

production에서 connection leak 진단의 첫 단계는 항상 "오래된 idle connection이 있는가" 확인입니다.

## 흔히 놓치는 함정 다섯 가지

### 1. SQLite `with conn` 의 의미 오해

`with sqlite3.connect(path) as conn:` 는 연결을 닫지 않습니다. transaction만 자동 commit/rollback 합니다. close까지 자동화하려면 위의 `open_db` 같은 wrapper가 필요합니다.

### 2. cursor를 함수 인자로 넘김

```python
def query(cur):
    cur.execute(...)
    return cur.fetchall()
```

이렇게 cursor를 외부로 노출하면 호출자가 cursor lifecycle을 책임져야 합니다. function이 connection을 받아 내부에서 cursor를 만들고 닫는 게 깔끔합니다.

### 3. Long-running connection의 idle timeout

PostgreSQL/MySQL은 서버가 idle connection을 일정 시간 후 끊습니다. application이 그 사실을 모르고 다음 query를 던지면 `OperationalError: server closed the connection`. 해결은 connection pool의 health check(`SELECT 1` ping)나 `pool_pre_ping=True`(SQLAlchemy).

### 4. Multiprocessing에서 connection 공유

`fork()` 후 자식 process가 부모의 connection을 그대로 쓰면 양쪽이 같은 socket에 동시 write 합니다. 결과는 corrupted protocol. 해결은 자식에서 새 connection을 만들거나, `multiprocessing.Process` 시작 직후 `conn = create_new_connection()`.

### 5. Cursor를 끝까지 안 읽고 새 query

```python
cur.execute("SELECT * FROM big_table")
cur.execute("SELECT 1")  # PostgreSQL: errors or discards the previous result
```

server-side cursor를 쓰는 환경에서는 이전 결과를 다 읽거나 명시적으로 `cur.close()` 후 새 query를 던져야 합니다.

## 정리

- Connection은 통신 채널이자 transaction context이고, cursor는 단일 query 실행 단위입니다.
- `with` 문은 lifecycle 관리의 기본 패턴이지만, SQLite의 `with conn`은 close가 아니라 commit/rollback만 담당합니다.
- 실무에서는 try/commit/except/rollback/finally/close를 감싼 context manager로 일관성을 만드는 편이 안전합니다.
- 동시 결과셋이 필요하면 cursor를 여러 개 만들고, connection은 재사용하거나 pool로 관리합니다.
- connection leak, idle timeout, fork 이후 공유, cursor 미정리는 가장 흔한 lifecycle 버그입니다.

다음 글에서는 `execute()`, `executemany()`, `fetchone()`/`fetchall()`/`fetchmany()`의 실전 패턴을 정리합니다.

<!-- a-grade-example:begin -->

## 체크리스트

- [ ] `with sqlite3.connect(...) as conn:` 패턴으로 자원 누수 없이 query를 실행했다.
- [ ] Cursor를 여러 개 열어 동시에 동일 connection에서 read하는 동작을 확인했다.
- [ ] Connection을 매번 여는 코드와 재사용하는 코드의 성능 차이를 측정했다.
- [ ] close 누락 시 sqlite3가 던지는 경고/락 증상을 직접 재현했다.

<!-- a-grade-example:end -->

## 심화 앵커: connection/cursor 경계 관측 템플릿

lifecycle 문제는 코드 리뷰보다 관측 지표에서 먼저 드러납니다. 아래 템플릿은 커밋/롤백/종료를 메트릭으로 남기는 최소 구조입니다.

```python
import sqlite3
import time
from contextlib import contextmanager

@contextmanager
def tracked_conn(path: str):
    t0 = time.perf_counter()
    conn = sqlite3.connect(path, timeout=5.0, isolation_level="IMMEDIATE")
    try:
        yield conn
        conn.commit()
        print("metric=db.commit count=1")
    except Exception:
        conn.rollback()
        print("metric=db.rollback count=1")
        raise
    finally:
        conn.close()
        print(f"metric=db.conn_lifetime_ms value={(time.perf_counter()-t0)*1000:.1f}")
```

```text
request start -> open connection -> open cursor -> execute -> commit/rollback -> close cursor -> close connection
```

SQLite에서 시작해도 cursor 종료 습관을 유지하면 psycopg2 전환 시 `idle in transaction` 누적을 크게 줄일 수 있습니다.

## 심화 실전 부록: 운영에서 바로 쓰는 앵커 모음

### 1) sqlite3와 psycopg2 비교 코드

```python
# sqlite3
import sqlite3
sconn = sqlite3.connect("app.db", timeout=5.0)
scur = sconn.cursor()
scur.execute("SELECT 1")
print(scur.fetchone())
scur.close()
sconn.close()

# psycopg2
import psycopg2
pconn = psycopg2.connect("dbname=app user=postgres password=secret host=127.0.0.1")
pcur = pconn.cursor()
pcur.execute("SELECT 1")
print(pcur.fetchone())
pcur.close()
pconn.close()
```

두 driver 모두 `connect -> cursor -> execute -> fetch -> close` 경계가 동일합니다. 이 공통 경계를 기준으로 테스트를 작성하면 이식성과 운영 안정성이 동시에 올라갑니다.

### 2) connection lifecycle 다이어그램

```text
Client Request
  -> Connection Open
  -> Cursor Open
  -> SQL Execute
  -> Fetch/Validate
  -> Commit or Rollback
  -> Cursor Close
  -> Connection Close
Response
```

트랜잭션이 길어지는 구간은 대개 `SQL Execute`와 `Commit` 사이입니다. 이 구간 시간을 측정해야 lock 경합 원인을 찾을 수 있습니다.

### 3) SQL 인젝션 재현과 차단

```python
import sqlite3

def demo_injection():
    con = sqlite3.connect(":memory:")
    con.executescript(
        "CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT);"
        "INSERT INTO users(name) VALUES ('alice');"
        "INSERT INTO users(name) VALUES ('bob');"
    )

    payload = "alice' OR 1=1 --"

    unsafe_sql = f"SELECT id, name FROM users WHERE name = '{payload}'"
    unsafe_rows = con.execute(unsafe_sql).fetchall()

    safe_rows = con.execute(
        "SELECT id, name FROM users WHERE name = ?", (payload,)
    ).fetchall()

    return unsafe_rows, safe_rows
```

문자열 결합 SQL은 입력값이 문법으로 재해석되는 순간 무너집니다. 바인딩 SQL은 입력값을 값으로만 다룹니다.

### 4) isolation level 비교표

| 항목 | SQLite DEFERRED | SQLite IMMEDIATE | SQLite EXCLUSIVE | PostgreSQL READ COMMITTED |
| --- | --- | --- | --- | --- |
| 트랜잭션 시작 시 lock | 없음 | RESERVED | EXCLUSIVE | MVCC 스냅샷 |
| write 충돌 감지 시점 | 늦음 | 빠름 | 매우 빠름 | 행/인덱스 잠금 시 |
| 동시 read 허용 | 높음 | 높음 | 낮음 | 높음 |
| 운영 기본값 추천 | 보통 | 높음 | 제한적 | 높음 |

SQLite에서는 write가 포함되면 `IMMEDIATE`가 충돌을 앞당겨 장애 분석을 쉽게 만듭니다.

### 5) connection pool 메트릭 템플릿

```python
from dataclasses import dataclass
import time

@dataclass
class PoolMetric:
    wait_ms: float
    in_use: int
    busy_rate: float

def report_pool(wait_ms: float, in_use: int, busy_count: int, total_count: int) -> PoolMetric:
    busy_rate = 0.0 if total_count == 0 else busy_count / total_count
    metric = PoolMetric(wait_ms=wait_ms, in_use=in_use, busy_rate=busy_rate)
    print(f"metric=pool.wait_ms value={metric.wait_ms:.1f}")
    print(f"metric=pool.in_use value={metric.in_use}")
    print(f"metric=db.busy_rate value={metric.busy_rate:.4f}")
    return metric
```

풀 크기 증가보다 `wait_ms`와 `busy_rate` 추세를 먼저 봐야 병목 원인을 정확히 분리할 수 있습니다.

### 6) async aiosqlite 트랜잭션 패턴

```python
import aiosqlite
from contextlib import asynccontextmanager

@asynccontextmanager
async def tx(conn: aiosqlite.Connection):
    await conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
        await conn.commit()
    except Exception:
        await conn.rollback()
        raise

async def create_note(conn: aiosqlite.Connection, body: str) -> int:
    async with tx(conn):
        cur = await conn.execute("INSERT INTO notes(body) VALUES (?)", (body,))
        return cur.lastrowid
```

`aiosqlite`는 이벤트 루프를 보호하지만, writer 1개 제약은 그대로입니다. 트랜잭션 길이를 짧게 유지해야 체감 성능이 좋아집니다.

### 7) 예외 계층 운영 트리

```text
DB-API Error
├─ IntegrityError      -> 재시도 금지, 입력/업무 규칙 응답
├─ OperationalError    -> SQLITE_BUSY/LOCKED만 제한적 재시도
├─ ProgrammingError    -> 코드 수정, 즉시 알림
├─ InterfaceError      -> 드라이버 사용 오류, 즉시 수정
└─ DatabaseError       -> 손상 가능성 점검, 복구 런북 실행
```

예외 클래스와 SQLite 코드(`sqlite_errorname`)를 함께 기록하면 재시도 정책을 정밀하게 적용할 수 있습니다.

### 8) 프로덕션 구성 템플릿

```python
import sqlite3

def open_prod(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path, timeout=5.0, isolation_level=None)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.row_factory = sqlite3.Row
    return conn
```

환경별 권장값:

- 개발: `busy_timeout=1000`, 상세 SQL 로그 ON
- 스테이징: `busy_timeout=3000`, slow query 임계치 150ms
- 프로덕션: `busy_timeout=5000`, slow query 임계치 p95*2 기준

### 9) 백업/복구 검증 템플릿

```python
import sqlite3

def backup_and_check(src_path: str, dst_path: str):
    src = sqlite3.connect(src_path)
    dst = sqlite3.connect(dst_path)
    try:
        src.backup(dst)
    finally:
        src.close()
        dst.close()

    chk = sqlite3.connect(dst_path)
    try:
        result = chk.execute("PRAGMA integrity_check").fetchone()[0]
        if result != "ok":
            raise RuntimeError(result)
    finally:
        chk.close()
```

백업은 생성 성공보다 복구 성공이 중요합니다. 주기적으로 restore 리허설을 자동화해야 장애 시 복구 시간을 예측할 수 있습니다.

### 10) 운영 체크리스트 확장

- 트랜잭션 길이 p95를 측정하고 100ms 이상 구간을 분리합니다.
- `SQLITE_BUSY` 비율과 retry 성공률을 같은 대시보드에서 봅니다.
- slow query 로그에는 SQL 라벨, 경과 시간, row 수를 남깁니다.
- PII가 포함될 수 있는 파라미터는 마스킹 후 기록합니다.
- 릴리스 전 부하 테스트에서 lock 충돌 재현 스크립트를 실행합니다.
- 배포 직후 `PRAGMA foreign_keys` 활성 상태를 점검합니다.
- 백업 파일 무결성(`integrity_check`)과 복구 후 핵심 테이블 row count를 함께 검증합니다.

부록의 목적은 새 개념 추가가 아니라 실전에서 반복되는 실패를 미리 차단하는 기본 템플릿을 제공하는 것입니다.

## 추가 심화 노트: 운영 품질 게이트

아래 항목은 개발 환경에서는 자주 생략되지만, 운영에서는 장애 예방에 직접 영향을 줍니다.

### A. 배포 전 검증 스크립트 예시

```bash
python -m pytest tests/test_dbapi_contract.py -q
python scripts/check_sql_bindings.py
python scripts/check_transaction_boundaries.py
```

### B. 계약 테스트 예시

```python
def test_dbapi_contract(conn):
    cur = conn.cursor()
    cur.execute("SELECT 1")
    assert cur.fetchone()[0] == 1
    cur.close()
```

### C. 관측성 필드 표준

| 필드 | 설명 |
| --- | --- |
| `db.driver` | sqlite3 / psycopg2 |
| `db.operation` | SELECT/INSERT/UPDATE/DELETE |
| `db.retry.count` | 재시도 횟수 |
| `db.elapsed_ms` | 실행 시간 |
| `db.tx.state` | commit/rollback |

### D. 성능 측정 루틴

```python
import time

def timed(fn, *args, **kwargs):
    t0 = time.perf_counter()
    v = fn(*args, **kwargs)
    elapsed = (time.perf_counter() - t0) * 1000
    print(f"metric=db.elapsed_ms value={elapsed:.1f}")
    return v
```

### E. 장애 대응 기본 규칙

- `IntegrityError`: 재시도하지 않고 입력/업무 규칙 오류로 처리합니다.
- `OperationalError`의 BUSY/LOCKED 계열: 짧은 백오프 재시도를 적용합니다.
- `ProgrammingError`: 코드 수정 대상이므로 즉시 알림합니다.
- `DatabaseError`의 손상 징후: 복구 런북으로 전환합니다.

이 노트는 새로운 개념을 추가하기보다, 본문의 원칙을 운영 절차로 고정하는 데 목적이 있습니다.

## 최종 보강: 실무 FAQ

### Q1. 왜 작은 프로젝트에서도 DB-API 경계를 엄격히 지켜야 하나요?

초기에는 코드량이 작아 보이지만, 운영 장애는 대부분 경계가 모호한 코드에서 시작됩니다. connect/execute/commit/close 경계를 명시하면 장애 원인을 단계별로 좁힐 수 있습니다.

### Q2. SQLite와 PostgreSQL을 함께 고려할 때 가장 먼저 맞춰야 할 것은 무엇인가요?

파라미터 바인딩 규칙과 트랜잭션 종료 규칙입니다. paramstyle 차이(`?` vs `%s`)는 어댑터로 흡수하고, 커밋/롤백 시점은 애플리케이션 레벨에서 동일하게 고정해야 합니다.

### Q3. 성능보다 먼저 챙겨야 할 지표는 무엇인가요?

`db.elapsed_ms`, `db.retry.count`, `db.busy_rate`, `db.tx.rollback.count` 네 가지입니다. 이 네 지표만 있어도 병목과 실패 패턴을 빠르게 분리할 수 있습니다.

### Q4. 운영 중 가장 자주 반복되는 실수는 무엇인가요?

- 예외를 `except Exception`으로 한 번에 처리해 재시도 가능/불가를 구분하지 않는 실수
- 문자열 결합 SQL이 테스트 없이 섞여 들어가는 실수
- 트랜잭션 경계를 함수 밖으로 흘려 보내는 실수
- 백업 성공 여부만 보고 복구 리허설을 생략하는 실수

### Q5. 팀 단위로 품질을 유지하려면 어떤 합의가 필요하나요?

코드 스타일 합의보다 더 중요한 것은 실패 처리 합의입니다. 어떤 예외를 retry할지, 어떤 예외를 즉시 실패로 처리할지, 어떤 로그 필드를 남길지를 문서와 테스트로 고정해야 합니다.

## 보충 메모: 릴리스 전 점검

릴리스 직전에는 코드 품질보다 운영 안전성을 먼저 점검합니다.

- 트랜잭션이 열리는 함수마다 commit/rollback 경로가 모두 존재하는지 확인합니다.
- cursor가 함수 경계를 넘어 누수되지 않는지 확인합니다.
- 예외 분기에서 retry 가능한 코드와 불가능한 코드를 분리했는지 확인합니다.
- 관측 로그에 최소 필드(`db.operation`, `db.elapsed_ms`, `db.tx.state`)가 남는지 확인합니다.

짧은 점검이지만 장애를 크게 줄이는 효과가 있습니다.

### 짧은 운영 참고

실서비스에서는 SQL 실행 자체보다 경계 관리가 더 자주 문제를 만듭니다. connection 생성과 종료, commit/rollback 분기를 로그와 테스트로 고정하면 장애 대응 시간이 짧아집니다.

### 추가 점검 한 줄

cursor를 외부로 반환하는 함수가 있다면 lifecycle 책임자가 모호해집니다. repository 함수 안에서 cursor를 열고 닫는 구조로 통일하면 누수와 장기 락을 줄일 수 있습니다.

## 처음 질문으로 돌아가기

- **Connection과 cursor는 각각 어떤 책임을 가질까요?**
  - 본문의 기준은 Connection과 Cursor Lifecycle를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **`with` context manager는 connection과 cursor 자원을 어떻게 보호할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **호출마다 새 connection을 여는 방식과 재사용하는 방식은 어떤 차이를 만들까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Python DB-API 101 (1/10): 왜 DB-API 2.0인가 - PEP 249가 푼 문제](./01-why-db-api-pep-249.md)
- **Python DB-API 101 (2/10): Connection과 Cursor Lifecycle (현재 글)**
- Python DB-API 101 (3/10): execute, executemany, fetch 패턴 (예정)
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

- [PEP 249 - Connection and Cursor objects](https://peps.python.org/pep-0249/#connection-objects)
- [Python sqlite3 - Connection class](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection)
- [psycopg 3 - Connection lifecycle](https://www.psycopg.org/psycopg3/docs/basic/usage.html)
- [SQLite - File locking and concurrency](https://www.sqlite.org/lockingv3.html)

Tags: Python, DB-API, PEP 249, Database
