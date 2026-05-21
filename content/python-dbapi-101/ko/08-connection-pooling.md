---
episode: 8
language: ko
last_reviewed: '2026-05-12'
series: python-dbapi-101
status: publish-ready
tags:
- Python
- SQLite
- Connection Pool
- Concurrency
- Threading
- PEP 249
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "Python DB-API 101 (8/10): SQLite Connection 관리: thread-safety, check_same_thread, 그리고 풀링"
seo_description: SQLite connection은 다른 DB의 client/server connection과 다르다.
---

# Python DB-API 101 (8/10): SQLite Connection 관리: thread-safety, check_same_thread, 그리고 풀링

다른 DB와 달리 SQLite는 별도의 서버 프로세스가 없습니다. connection은 그냥 파일 핸들이고, 트랜잭션 락은 파일 시스템에 표현됩니다. 이 단순함 덕분에 SQLite는 임베디드부터 중간 규모 웹앱까지 쓰이지만, 동시에 connection을 어떻게 다룰지에 대한 의사결정을 개발자에게 그대로 떠넘깁니다.

"connection 하나를 전역으로 공유해도 되는가?", "스레드마다 새로 만들어야 하는가?", "FastAPI 같은 비동기 프레임워크에서 connection을 어떻게 쥐어야 하는가?" 이 글은 그 질문들에 답합니다.

이 글은 Python DB-API 101 시리즈의 여덟 번째 글입니다.

![SQLite Connection 관리: thread-safety, check_same_thread, 그리고 풀링](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/08/08-01-sqlite-connection-management-thread-safe.ko.png)

*SQLite Connection 관리: thread-safety, check_same_thread, 그리고 풀링*

![Python DB-API 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/08/08-02-mental-model-a-connection-is-a-file-hand.ko.png)
*Python DB-API 101 8장 흐름 개요*

## 먼저 던지는 질문

- SQLite Connection 관리: thread-safety, check_same_thread, 그리고 풀링를 운영 관점에서 볼 때 먼저 어떤 경계를 확인해야 할까요?
- SQLite Connection 관리: thread-safety, check_same_thread, 그리고 풀링에서 예제나 다이어그램으로 검증해야 할 핵심 신호는 무엇일까요?
- SQLite Connection 관리: thread-safety, check_same_thread, 그리고 풀링를 실제 시스템에 적용할 때 어떤 실패를 먼저 막아야 할까요?

## Mental Model: connection은 "파일을 연 핸들"이다

> SQLite connection은 다른 DB의 client/server connection과 다르다. 별도 프로세스가 없고, 락은 파일 시스템 락이며, connection 객체는 본질적으로 파일 핸들 + 캐시 + 트랜잭션 상태다.

이 차이가 결정하는 것:

- connection을 새로 여는 비용은 PostgreSQL보다 훨씬 작다. 핸드셰이크가 없다.
- 그러나 connection 객체 자체에 트랜잭션 상태와 prepared statement 캐시가 있다. 그래서 "세션"의 의미는 그대로 있다.
- 동시에 여러 connection이 같은 파일을 열 수 있지만, 쓰기는 한 번에 하나만 가능(WAL 모드에서도 writer는 1개).
- thread-safety는 SQLite C 라이브러리가 컴파일된 모드에 따라 정해진다.

이 모델을 가지면 "pool로 connection을 재사용해 비용을 아낀다"가 SQLite에서는 부차적인 목적이 된다는 것이 보입니다. 진짜 목적은 "스레드/요청별로 트랜잭션 경계를 명확하게 갖는 것"입니다.

## 핵심 개념

![핵심 개념](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/08/08-03-core-concepts.ko.png)

*핵심 개념*
### SQLite의 세 가지 thread-safety 모드

SQLite C 라이브러리는 컴파일 시 세 가지 native 모드 중 하나를 가집니다.

- **Single-thread**: 어떤 스레드 동시성도 허용하지 않음. 임베디드용.
- **Multi-thread**: 서로 다른 connection을 서로 다른 스레드에서 사용 가능. 한 connection을 두 스레드가 동시에 쓰면 안 됨.
- **Serialized**: 한 connection을 여러 스레드가 동시에 사용해도 안전. 내부 mutex가 직렬화.

이 native 모드 이름과 Python DB-API의 `sqlite3.threadsafety` 숫자는 같은 체계가 아닙니다. Python이 노출하는 DB-API 매핑은 다음과 같습니다.

- **0** -> SQLite single-thread
- **1** -> SQLite multi-thread
- **3** -> SQLite serialized

SQLite 컴파일 타임의 `SQLITE_THREADSAFE` 숫자도 또 다릅니다(같은 순서로 `0`, `2`, `1`).

Python의 `sqlite3` 모듈은 DB-API 값을 이렇게 노출합니다.

```python
import sqlite3
print(sqlite3.threadsafety)  # 0, 1, or 3
```

대부분의 배포판에서 `1` 또는 `3`을 봅니다. Python 3.11+에서 값 `3`은 SQLite의 `serialized` 모드에 대응합니다. 반대로 값 `1`은 `multi-thread`에 대응하므로, connection 하나를 여러 스레드가 공유해도 된다는 뜻이 아닙니다.

### `check_same_thread`의 의미

`sqlite3.connect()`는 기본값 `check_same_thread=True`로 동작합니다. 이는 **Python 레벨의 가드**이며, SQLite C 라이브러리의 thread-safety 모드와 별개입니다. 같은 connection을 만든 스레드가 아닌 다른 스레드에서 사용하려고 하면 `sqlite3` 모듈이 `ProgrammingError`를 던집니다.

```python
import sqlite3, threading

conn = sqlite3.connect("app.db")  # check_same_thread=True (default)

def worker():
    conn.execute("SELECT 1")  # ProgrammingError

threading.Thread(target=worker).start()
```

`check_same_thread=False`로 끄면 Python 가드가 사라지고, 이후의 안전성은 전적으로 SQLite C 라이브러리가 어떤 thread-safety 모드로 컴파일되어 있느냐에 달립니다. 즉 `check_same_thread=False`만으로는 안전하지 않습니다. **connection 하나를 여러 스레드에서 공유하려면 먼저 `sqlite3.threadsafety == 3`인지 확인**해야 합니다. 그 외에는 더 안전한 기본 원칙, 즉 connection 하나를 여러 스레드가 공유하지 않는 쪽으로 설계하세요.

### per-thread vs shared connection

| 전략 | 장점 | 단점 | 적합한 경우 |
|------|------|------|------------|
| 요청마다 새 connection | 가장 단순. 트랜잭션 경계가 요청과 일치 | connection 생성 빈도가 높음(SQLite는 저비용이지만 0은 아님) | 짧은 요청, 낮은 동시성 |
| 스레드별 connection (`threading.local`) | 스레드 안에서 재사용. `check_same_thread` 가드 유지 | 스레드 풀이 커지면 connection 수 증가 | 전통적인 WSGI/Flask |
| 단일 shared connection | 가장 작은 자원 사용 | `sqlite3.threadsafety == 3` + `check_same_thread=False` 필수, writer가 직렬화됨 | 임베디드, 단일 워커 |
| asyncio용 외부 풀(`aiosqlite`) | 코루틴 친화적 | 순차 실행 모델이라 동시성 이득은 제한적 | FastAPI/aiohttp |

### 왜 SQLite에는 큰 connection pool이 어울리지 않는가

PostgreSQL용 pool은 (1) connection 핸드셰이크 비용을 아끼고, (2) 서버의 동시 connection 한도를 보호하기 위해 존재합니다. SQLite에는 (1) 핸드셰이크가 없고, (2) 서버 프로세스가 없으므로 한도라는 개념이 다릅니다. 대신 SQLite의 한도는 **writer 1명**이라는 점입니다. 30개의 connection을 풀에 띄워도 쓰기 처리량은 늘어나지 않습니다. 오히려 writer 경쟁이 늘어 BUSY 에러만 더 자주 봅니다.

따라서 "큰 풀"이 아니라 "역할별로 나뉜 작은 풀"이 어울립니다. 예: read connection 다수 + write connection 1개.

## Before / After

### Before: 전역 connection을 그대로 공유

```python
# app.py
import sqlite3
conn = sqlite3.connect("app.db", check_same_thread=False)

def get_user(user_id: int):
    return conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
```

문제는 두 스레드가 동시에 `execute()`를 호출하면, `serialized` 모드라도 cursor 상태와 트랜잭션 경계가 뒤섞입니다. 한 스레드가 `BEGIN`한 트랜잭션을 다른 스레드가 무심코 `commit()`해 버릴 수 있습니다.

### After: 요청 단위 connection + WAL 모드

```python
import sqlite3
from contextlib import contextmanager

DB_PATH = "app.db"

def open_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, isolation_level=None, timeout=5.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def db_session():
    conn = open_conn()
    try:
        yield conn
    finally:
        conn.close()

def get_user(user_id: int):
    with db_session() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE id=?", (user_id,)
        ).fetchone()
```

요청마다 새 connection을 열고 닫으며, WAL 모드로 reader가 writer를 막지 않게 합니다. SQLite의 connection 생성 비용이 작기 때문에 이 패턴이 대부분의 웹앱에 충분합니다.

## 단계별 실습: FastAPI에서 SQLite를 안전하게 쥐기

![단계별 실습: FastAPI에서 SQLite를 안전하게 쥐기](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/08/08-04-step-by-step-holding-sqlite-safely-in-fa.ko.png)

*단계별 실습: FastAPI에서 SQLite를 안전하게 쥐기*
### 1단계: 환경 점검

```python
import sqlite3
print("sqlite3 version:", sqlite3.sqlite_version)
print("threadsafety:", sqlite3.threadsafety)
```

`threadsafety`가 1 미만이라면 멀티스레드에서 connection을 공유할 수 없습니다. 보통 1 또는 3입니다.

### 2단계: connection 팩토리

```python
import sqlite3

DB_PATH = "app.db"

def open_conn(*, readonly: bool = False) -> sqlite3.Connection:
    uri = f"file:{DB_PATH}?mode={'ro' if readonly else 'rwc'}"
    conn = sqlite3.connect(
        uri,
        uri=True,
        isolation_level=None,
        timeout=5.0,
        check_same_thread=True,
    )
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    if readonly:
        conn.execute("PRAGMA query_only=ON")
    conn.row_factory = sqlite3.Row
    return conn
```

읽기 전용 connection을 별도로 열 수 있게 했습니다. read 트래픽이 많은 경우 의도를 명시할 수 있습니다.

### 3단계: FastAPI dependency

```python
from fastapi import FastAPI, Depends
import sqlite3

app = FastAPI()

def get_db() -> sqlite3.Connection:
    conn = open_conn()
    try:
        yield conn
    finally:
        conn.close()

@app.get("/users/{user_id}")
def read_user(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    row = db.execute(
        "SELECT id, email FROM users WHERE id=?", (user_id,)
    ).fetchone()
    return dict(row) if row else {"error": "not found"}
```

FastAPI는 `Depends`마다 새 generator를 호출하므로, 요청 단위로 새 connection이 만들어지고 응답 후 닫힙니다.

### 4단계: write 경로 분리

```python
@app.post("/users", status_code=201)
def create_user(payload: UserCreate, db: sqlite3.Connection = Depends(get_db)):
    db.execute("BEGIN IMMEDIATE")
    try:
        cur = db.execute(
            "INSERT INTO users(email) VALUES (?)", (payload.email,)
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {"id": cur.lastrowid}
```

`open_conn()`이 `isolation_level=None`로 connection을 열기 때문에 SQLite는 명시적 `BEGIN ...`이 나오기 전까지 autocommit 모드에 머뭅니다. 여기서는 `BEGIN IMMEDIATE`가 write 트랜잭션 경계를 만들고, 성공 시 `commit()`, 예외 시 `rollback()`이 그 경계를 닫습니다.

### 5단계: 동시 쓰기 시뮬레이션

```python
import concurrent.futures, sqlite3

def writer(i):
    conn = open_conn()
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("INSERT INTO log(msg) VALUES (?)", (f"msg-{i}",))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
    list(ex.map(writer, range(200)))
```

`busy_timeout`(`timeout=5.0`)과 WAL 모드 덕분에 이 코드가 BUSY 에러 없이 끝나는지 확인합니다. 만약 BUSY가 자주 보인다면 워커 수를 줄이거나, write를 단일 큐로 직렬화하는 구조를 검토합니다.

## 자주 하는 실수

**전역 connection 하나에 `check_same_thread=False`만 켜고 끝.** 진짜로 안전한지 검증하지 않은 상태입니다. `sqlite3.threadsafety` 값을 확인하고, 동시 쓰기가 허용되는 경계인지 명확히 하세요.

**WSGI 서버의 worker마다 connection 풀을 정교하게 관리.** SQLite에서는 과한 최적화입니다. 요청 단위 open/close가 더 단순하고 안전합니다.

**writer를 여러 스레드가 동시에 호출.** WAL 모드라도 writer는 1명입니다. 동시성을 늘리려면 read를 분리하거나, write를 큐로 직렬화하세요.

**`PRAGMA journal_mode=WAL`을 트랜잭션 안에서 실행.** WAL 전환은 트랜잭션 밖에서 한 번만 해야 합니다. connection을 열자마자 호출하세요.

**FastAPI에서 module-level singleton connection 사용.** 비동기 컨텍스트에서 트랜잭션 경계가 요청과 어긋나 의도치 않은 commit이 일어납니다. dependency-injection 패턴을 쓰세요.

**timeout 미설정.** 기본 `timeout=5.0`이 있지만 워크로드에 따라 너무 길거나 짧을 수 있습니다. p99 락 대기 시간을 측정해서 결정하세요.

## 실무: read/write 분리와 단일 writer 큐

쓰기 처리량이 병목이라면, 다음 패턴을 고려할 수 있습니다.

```python
import queue, threading, sqlite3

write_queue: queue.Queue = queue.Queue()

def writer_worker():
    conn = open_conn()
    while True:
        job = write_queue.get()
        if job is None:
            break
        sql, params = job
        with conn:
            conn.execute(sql, params)

threading.Thread(target=writer_worker, daemon=True).start()
```

요청 핸들러는 큐에 넣기만 하고, 단일 writer 스레드가 직렬로 처리합니다. 이렇게 하면 BUSY 에러를 완전히 제거할 수 있고, 트랜잭션 묶음을 키워 처리량을 올릴 수 있습니다. 단점은 쓰기 결과를 즉시 반환하기 어렵다는 것이므로, "fire-and-forget"이 허용되는 경로(예: 로그, 이벤트 기록)에 적합합니다.

읽기는 그대로 요청별 connection을 사용하면 됩니다. WAL 모드 덕분에 reader는 writer를 기다리지 않습니다.

## 체크리스트

- [ ] `sqlite3.threadsafety` 값을 확인했는가?
- [ ] connection 전략(요청별 / 스레드별 / 단일 / 큐)을 한 가지로 정했는가?
- [ ] `journal_mode=WAL`, `synchronous=NORMAL`, `foreign_keys=ON`을 connection 직후에 설정하는가?
- [ ] `timeout`(또는 `busy_timeout`)을 의도적으로 설정했는가?
- [ ] writer가 여러 스레드에서 동시에 호출되는 경로가 없는가?
- [ ] FastAPI에서는 `Depends(get_db)`로 요청 단위 connection을 주입하는가?
- [ ] 트랜잭션 경계가 `with conn:` 블록으로 명시되어 있는가?
- [ ] 읽기 전용 경로에 `mode=ro` 또는 `query_only=ON`을 사용했는가?
- [ ] 동시 쓰기 부하 테스트로 BUSY 발생률을 측정했는가?
- [ ] connection 누수가 없는지 (`PRAGMA database_list`나 OS 핸들 모니터링) 확인했는가?

## 정리
- SQLite connection은 파일 핸들에 가깝고, 큰 connection pool보다 "역할별 작은 connection 전략"이 어울립니다.
- `sqlite3.threadsafety`와 `check_same_thread`는 별개의 가드이며 둘 다 이해해야 합니다.
- 대부분의 웹앱에는 "요청 단위 open/close + WAL 모드 + busy_timeout"이 가장 단순하고 안전한 기본값입니다.
- 쓰기 병목이 있다면 read/write 분리, 단일 writer 큐를 검토합니다.

다음 글에서는 동기 모델을 떠나 `aiosqlite`로 비동기 SQLite를 다룹니다. asyncio 컨텍스트에서 connection과 트랜잭션을 어떻게 쥐는지, 그리고 FastAPI의 async path와 어떻게 어우러지는지 살펴봅니다.

## 심화 앵커: 풀링 메트릭으로 병목을 식별하는 방법

SQLite 풀링은 connection 생성 비용 절감보다 경계 제어가 목적입니다. 그래서 풀 크기보다 대기 시간과 BUSY 비율을 먼저 봐야 합니다.

```python
import sqlite3
import queue
import time

class Pool:
    def __init__(self, path: str, size: int = 4):
        self.q = queue.Queue(maxsize=size)
        for _ in range(size):
            conn = sqlite3.connect(path, timeout=5.0, isolation_level=None)
            conn.execute("PRAGMA journal_mode=WAL")
            self.q.put(conn)

    def acquire(self):
        t0 = time.perf_counter()
        conn = self.q.get()
        print(f"metric=pool.wait_ms value={(time.perf_counter()-t0)*1000:.1f}")
        return conn
```

| 지표 | 의미 |
| --- | --- |
| `pool.wait_ms` | connection 대기 시간 |
| `pool.in_use` | 동시 사용 수 |
| `db.busy_rate` | 락 충돌 비율 |

권장 구조는 read 경로와 write 경로 분리입니다. read pool은 다수, write 경로는 단일 직렬화로 두는 편이 SQLite 특성과 가장 잘 맞습니다.

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

## 처음 질문으로 돌아가기

- **SQLite Connection 관리: thread-safety, check_same_thread, 그리고 풀링를 운영 관점에서 볼 때 먼저 어떤 경계를 확인해야 할까요?**
  - 본문의 기준은 SQLite Connection 관리: thread-safety, check_same_thread, 그리고 풀링를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **SQLite Connection 관리: thread-safety, check_same_thread, 그리고 풀링에서 예제나 다이어그램으로 검증해야 할 핵심 신호는 무엇일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **SQLite Connection 관리: thread-safety, check_same_thread, 그리고 풀링를 실제 시스템에 적용할 때 어떤 실패를 먼저 막아야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Python DB-API 101 (1/10): 왜 DB-API 2.0인가 - PEP 249가 푼 문제](./01-why-db-api-pep-249.md)
- [Python DB-API 101 (2/10): Connection과 Cursor Lifecycle](./02-connection-cursor-lifecycle.md)
- [Python DB-API 101 (3/10): execute, executemany, fetch 패턴](./03-execute-fetch-patterns.md)
- [Python DB-API 101 (4/10): Parameter binding과 SQL injection 방어 (sqlite3, PEP 249)](./04-parameter-binding-sql-injection.md)
- [Python DB-API 101 (5/10): Transaction과 isolation level (sqlite3, PEP 249)](./05-transactions-isolation.md)
- [Python DB-API 101 (6/10): Row factory와 type adapter (sqlite3, PEP 249)](./06-row-factories-adapters.md)
- [Python DB-API 101 (7/10): PEP 249 예외 계층과 SQLite 에러 처리](./07-error-handling-exception-hierarchy.md)
- **Python DB-API 101 (8/10): SQLite Connection 관리: thread-safety, check_same_thread, 그리고 풀링 (현재 글)**
- Python DB-API 101 (9/10): aiosqlite로 비동기 SQLite 다루기 (예정)
- Python DB-API 101 (10/10): SQLite Production 패턴: retry, timeout, 관측성, 백업 (예정)

<!-- toc:end -->

## 참고 자료

- [Python `sqlite3` — Threadsafety](https://docs.python.org/3/library/sqlite3.html#sqlite3.threadsafety)
- [SQLite And Multiple Threads](https://www.sqlite.org/threadsafe.html)
- [Write-Ahead Logging](https://www.sqlite.org/wal.html)
- [SQLite URI filenames](https://www.sqlite.org/uri.html)
- [FastAPI — Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/python-dbapi-101/ko)

Tags: Python, DB-API, PEP 249, Database
