---
episode: 9
language: ko
last_reviewed: '2026-05-12'
series: python-dbapi-101
status: publish-ready
tags:
- Python
- SQLite
- asyncio
- aiosqlite
- Async
- PEP 249
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "Python DB-API 101 (9/10): aiosqlite로 비동기 SQLite 다루기"
seo_description: aiosqlite는 SQLite를 비동기로 바꾸지 않는다. connection마다 백그라운드 스레드를 띄우고, await되는
  메서드 호출을…
---

# Python DB-API 101 (9/10): aiosqlite로 비동기 SQLite 다루기

`asyncio` 코드 안에 `sqlite3.connect()`를 그대로 두면 어떻게 될까요? 코드는 동작하지만, `execute()`가 동기 호출이라 이벤트 루프가 그 시간 동안 멈춥니다. 한 요청이 1초 걸리는 쿼리를 돌리면 같은 워커의 다른 모든 요청이 1초 동안 응답을 못 받습니다.

`aiosqlite`는 이 문제를 해결합니다. 다만 "해결"의 의미를 정확히 알아야 합니다. 이 라이브러리는 SQLite를 진짜 비동기로 만들지 않고, **별도 스레드에서 sqlite3 호출을 실행하고 결과를 future로 돌려주는 어댑터**입니다. 그래서 이벤트 루프는 안 막히지만, SQLite 엔진 자체의 단일 writer 제약은 그대로 남습니다.

이 글은 Python DB-API 101 시리즈의 아홉 번째 글입니다.

![aiosqlite로 비동기 SQLite 다루기](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/09/09-01-asynchronous-sqlite-with-aiosqlite.ko.png)

*aiosqlite로 비동기 SQLite 다루기*

## 먼저 던지는 질문

- aiosqlite로 비동기 SQLite 다루기를 운영 관점에서 볼 때 먼저 어떤 경계를 확인해야 할까요?
- aiosqlite로 비동기 SQLite 다루기에서 예제나 다이어그램으로 검증해야 할 핵심 신호는 무엇일까요?
- aiosqlite로 비동기 SQLite 다루기를 실제 시스템에 적용할 때 어떤 실패를 먼저 막아야 할까요?

## 큰 그림

![Python DB-API 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/09/09-02-mental-model-aiosqlite-is-sqlite3-thread.ko.png)

*Python DB-API 101 9장 흐름 개요*

## Mental Model: aiosqlite는 sqlite3 + thread + Future

> aiosqlite는 SQLite를 비동기로 바꾸지 않는다. connection마다 백그라운드 스레드를 띄우고, `await`되는 메서드 호출을 그 스레드의 큐로 넣고, 결과를 Future로 받아 이벤트 루프에 돌려준다.

이 구조의 함의:

- 이벤트 루프는 안 막힌다. 다른 코루틴이 그 동안 진행될 수 있다.
- 단일 connection 안에서는 호출이 직렬이다. 같은 connection을 두 코루틴이 동시에 쓸 수 없다.
- connection 하나당 스레드 하나가 따라다니므로, connection을 많이 만들면 스레드도 많이 생긴다.
- SQLite의 단일 writer 제약은 그대로다. `aiosqlite` connection 100개를 만들어도 동시에 쓰는 writer는 1명이다.

따라서 `aiosqlite`의 진짜 가치는 "동시성 이득"이 아니라 "**이벤트 루프 보호**"입니다. 동기 sqlite3을 async 코드에 직접 쓰지 않기 위한 어댑터로 이해하는 것이 정확합니다.

## 핵심 개념

![핵심 개념](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/09/09-03-core-concepts.ko.png)

*핵심 개념*
### 설치와 기본 사용

```bash
pip install aiosqlite
```

```python
import asyncio
import aiosqlite

async def main():
    async with aiosqlite.connect("app.db") as db:
        await db.execute("CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY, body TEXT)")
        await db.execute("INSERT INTO notes(body) VALUES (?)", ("hello",))
        await db.commit()
        async with db.execute("SELECT id, body FROM notes") as cur:
            async for row in cur:
                print(row)

asyncio.run(main())
```

`aiosqlite.connect()`는 동기 sqlite3 connection과 비슷한 인터페이스를 제공하지만, 모든 메서드가 코루틴입니다. `async with`로 닫고, `async for`로 결과를 순회합니다.

### 동기와 비동기를 한 줄로 비교

```python
# Sync
import sqlite3
conn = sqlite3.connect("app.db")
cur = conn.execute("SELECT 1")
row = cur.fetchone()

# Async
import aiosqlite
async with aiosqlite.connect("app.db") as conn:
    async with conn.execute("SELECT 1") as cur:
        row = await cur.fetchone()
```

API가 거의 1:1로 대응됩니다. `await`만 붙는다고 보면 됩니다.

### 트랜잭션

`aiosqlite`도 `isolation_level` 인자를 그대로 받습니다. 기본값은 `""`(빈 문자열)이며, 이는 sqlite3의 동작과 같이 "암시적 BEGIN"을 사용합니다. 명시적 트랜잭션을 원하면 `isolation_level=None`로 두고 직접 `BEGIN`을 호출합니다.

```python
async with aiosqlite.connect("app.db", isolation_level=None) as db:
    await db.execute("BEGIN IMMEDIATE")
    try:
        await db.execute("UPDATE accounts SET balance=balance-? WHERE id=?", (10, 1))
        await db.execute("UPDATE accounts SET balance=balance+? WHERE id=?", (10, 2))
        await db.commit()
    except Exception:
        await db.rollback()
        raise
```

`async with db:`처럼 connection 자체를 context manager로 쓰는 동기 패턴은 `aiosqlite`에서 동일하게 동작하지 않습니다. connection의 `__aexit__`은 commit이 아니라 close를 의미합니다.

## Before / After: FastAPI 핸들러

### Before: async path에서 동기 sqlite3 직접 호출

```python
from fastapi import FastAPI
import sqlite3

app = FastAPI()
conn = sqlite3.connect("app.db", check_same_thread=False)

@app.get("/notes/{note_id}")
async def read_note(note_id: int):
    cur = conn.execute("SELECT body FROM notes WHERE id=?", (note_id,))
    row = cur.fetchone()
    return {"body": row[0] if row else None}
```

문제 두 가지: (1) `execute()`가 이벤트 루프를 막고, (2) 전역 connection을 공유해 트랜잭션 경계가 모호합니다.

### After: aiosqlite + per-request connection

```python
from fastapi import FastAPI, Depends
import aiosqlite

app = FastAPI()
DB_PATH = "app.db"

async def get_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("PRAGMA foreign_keys=ON")
        db.row_factory = aiosqlite.Row
        yield db

@app.get("/notes/{note_id}")
async def read_note(note_id: int, db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute("SELECT body FROM notes WHERE id=?", (note_id,)) as cur:
        row = await cur.fetchone()
    return {"body": row["body"] if row else None}
```

이벤트 루프가 보호되고, 트랜잭션 경계가 요청과 일치합니다. 단점은 요청마다 connection-per-thread가 새로 생긴다는 것이므로, 트래픽이 큰 경우 다음 절의 풀 패턴을 검토합니다.

## 단계별 실습: 가벼운 connection 풀 만들기

![단계별 실습: 가벼운 connection 풀 만들기](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/09/09-04-step-by-step-a-lightweight-connection-po.ko.png)

*단계별 실습: 가벼운 connection 풀 만들기*
`aiosqlite`는 풀을 기본 제공하지 않습니다. 직접 만든다면 다음과 같은 모양이 됩니다.

### 1단계: 풀 인터페이스

```python
import asyncio
import aiosqlite
from contextlib import asynccontextmanager

class SQLitePool:
    def __init__(self, path: str, *, size: int = 5):
        self._path = path
        self._size = size
        self._queue: asyncio.Queue[aiosqlite.Connection] = asyncio.Queue(maxsize=size)
        self._initialized = False
        self._lock = asyncio.Lock()

    async def _init(self) -> None:
        for _ in range(self._size):
            conn = await aiosqlite.connect(self._path)
            await conn.execute("PRAGMA journal_mode=WAL")
            await conn.execute("PRAGMA foreign_keys=ON")
            conn.row_factory = aiosqlite.Row
            await self._queue.put(conn)
        self._initialized = True

    async def initialize(self) -> None:
        async with self._lock:
            if not self._initialized:
                await self._init()

    @asynccontextmanager
    async def acquire(self):
        conn = await self._queue.get()
        try:
            yield conn
        finally:
            await self._queue.put(conn)

    async def close(self) -> None:
        while not self._queue.empty():
            conn = self._queue.get_nowait()
            await conn.close()
```

핵심은 단순 `asyncio.Queue`입니다. 풀에서 connection을 꺼내고, 사용 후 다시 넣습니다.

### 2단계: FastAPI lifespan에서 초기화

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

pool = SQLitePool("app.db", size=5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await pool.initialize()
    yield
    await pool.close()

app = FastAPI(lifespan=lifespan)

async def get_db():
    async with pool.acquire() as conn:
        yield conn
```

요청이 끝날 때 connection은 풀로 반환되며, 다음 요청이 재사용합니다. 풀 크기는 보통 워커 수의 1~2배가 적절합니다.

### 3단계: 트랜잭션 헬퍼

```python
@asynccontextmanager
async def transactional(conn: aiosqlite.Connection):
    await conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
        await conn.commit()
    except Exception:
        await conn.rollback()
        raise

@app.post("/notes", status_code=201)
async def create_note(payload: NoteCreate, db = Depends(get_db)):
    async with transactional(db):
        cur = await db.execute(
            "INSERT INTO notes(body) VALUES (?)", (payload.body,)
        )
    return {"id": cur.lastrowid}
```

`transactional` 컨텍스트가 commit/rollback을 책임지므로 핸들러 코드가 간결해집니다.

### 4단계: 부하 측정

```python
import asyncio, aiosqlite, time

async def reader(pool, i):
    async with pool.acquire() as conn:
        await conn.execute("SELECT 1")

async def main():
    pool = SQLitePool("app.db", size=10)
    await pool.initialize()
    t0 = time.perf_counter()
    await asyncio.gather(*(reader(pool, i) for i in range(1000)))
    print(f"{time.perf_counter()-t0:.3f}s")
    await pool.close()

asyncio.run(main())
```

같은 부하를 풀 없이(매번 connect/close) 돌려서 비교해 보세요. 풀 크기가 너무 작으면 큐 대기가 길어지고, 너무 크면 스레드/메모리만 늘어납니다.

## 자주 하는 실수

**한 connection을 여러 코루틴에서 동시에 사용.** `aiosqlite` connection은 직렬화되어 있지만, "동시 사용"은 정의되지 않습니다. 풀에서 한 connection은 한 번에 한 코루틴만 쥐어야 합니다.

**`async with db:`로 트랜잭션을 기대.** `__aexit__`은 close입니다. 트랜잭션 경계는 `BEGIN`/`commit`/`rollback`을 직접 호출하거나 위의 `transactional` 헬퍼를 쓰세요.

**`aiosqlite`를 쓰면 동시 쓰기 처리량이 늘 거라 기대.** SQLite의 단일 writer 제약은 그대로입니다. `aiosqlite`는 이벤트 루프를 보호할 뿐 writer 직렬성은 그대로 둡니다.

**풀 크기를 매우 크게.** connection당 스레드가 따라다니므로, 100개를 만들면 100개의 스레드가 생깁니다. 워커 수의 1~2배로 시작해 측정 후 조정하세요.

**lifespan 없이 module-level에서 connect 호출.** import 시점에 이벤트 루프가 없으면 실패합니다. lifespan이나 startup 이벤트에서 초기화합니다.

**`asyncio.run(...)` 안에서 `aiosqlite`를 만들고 다른 `asyncio.run(...)`에서 재사용.** 이벤트 루프가 다르므로 동작하지 않습니다. 같은 루프 안에서 만들고 닫으세요.

## 실무: FastAPI sync vs async + aiosqlite 결정 가이드

FastAPI는 핸들러가 `def`(동기)이면 자동으로 thread pool에서 실행합니다. 즉 동기 `sqlite3`도 사실상 안전하게 쓸 수 있습니다. `async def` 핸들러로 바꿔야 하는 이유는 다음 중 하나일 때입니다.

- 같은 핸들러에서 `await`해야 하는 다른 I/O가 있다(예: 외부 HTTP 호출).
- WebSocket이나 SSE처럼 핸들러 자체가 async를 요구한다.
- 한 요청 안에서 여러 SQLite 호출을 다른 await 대상과 인터리빙하고 싶다.

위 조건이 없다면 `def` 핸들러 + 동기 `sqlite3`이 더 단순하고 빠릅니다. `aiosqlite`는 위 조건을 만족하는 진짜 async path에서만 도입하세요.

## 체크리스트

- [ ] async 핸들러에서 동기 sqlite3을 직접 호출하는 경로가 없는가?
- [ ] 한 connection을 여러 코루틴이 동시에 쓰는 경로가 없는가?
- [ ] 트랜잭션은 `BEGIN`/`commit`/`rollback`을 직접 다루거나 헬퍼로 감쌌는가?
- [ ] 풀을 만들었다면 lifespan에서 초기화/종료가 보장되는가?
- [ ] 풀 크기를 측정 기반으로 결정했는가? (워커 수의 1~2배에서 시작)
- [ ] PRAGMA(WAL, foreign_keys 등)가 connection 생성 직후에 설정되는가?
- [ ] busy_timeout 또는 SQLite 측 timeout이 의도적으로 설정되어 있는가?
- [ ] async path가 진짜 필요한지(다른 await 대상 존재 여부) 검토했는가?
- [ ] 동시 쓰기 부하 테스트로 BUSY 발생률을 확인했는가?
- [ ] 풀 누수 모니터링(예: `_queue.qsize()`)이 있는가?

## 정리
- `aiosqlite`는 SQLite를 진짜 비동기로 만들지 않는다. 이벤트 루프 보호용 어댑터다.
- 동시 쓰기 처리량은 늘지 않는다. SQLite의 단일 writer 제약은 그대로다.
- async path가 진짜 필요할 때만 도입하라. 그렇지 않다면 `def` 핸들러 + sqlite3가 더 단순하다.
- 풀이 필요하면 가벼운 `asyncio.Queue` 기반으로 충분하다. lifespan에서 초기화하라.

다음 글(Ep10, 시리즈 마지막)은 production 패턴을 정리합니다. retry+timeout+observability, slow query logging, OpenTelemetry instrumentation, 백업 전략까지 한 번에 다룹니다.

## 심화 앵커: aiosqlite 운영 패턴의 상한 관리

`aiosqlite`는 이벤트 루프를 보호하지만, connection 하나당 백그라운드 스레드가 생긴다는 제약이 있습니다. 따라서 풀 크기를 크게 잡는 대신 트랜잭션 길이를 짧게 유지해야 합니다.

```python
import asyncio
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
```

운영에서는 세 가지를 함께 측정합니다.

- loop lag: 이벤트 루프 지연
- pool wait time: connection 획득 대기
- `SQLITE_BUSY` 비율: write 경합 정도

비동기 전환의 목표는 write 처리량 증가가 아니라, 같은 워커에서 다른 요청이 막히지 않게 만드는 것입니다.

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

- **aiosqlite로 비동기 SQLite 다루기를 운영 관점에서 볼 때 먼저 어떤 경계를 확인해야 할까요?**
  - 본문의 기준은 aiosqlite로 비동기 SQLite 다루기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **aiosqlite로 비동기 SQLite 다루기에서 예제나 다이어그램으로 검증해야 할 핵심 신호는 무엇일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **aiosqlite로 비동기 SQLite 다루기를 실제 시스템에 적용할 때 어떤 실패를 먼저 막아야 할까요?**
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
- [Python DB-API 101 (8/10): SQLite Connection 관리: thread-safety, check_same_thread, 그리고 풀링](./08-connection-pooling.md)
- **Python DB-API 101 (9/10): aiosqlite로 비동기 SQLite 다루기 (현재 글)**
- Python DB-API 101 (10/10): SQLite Production 패턴: retry, timeout, 관측성, 백업 (예정)

<!-- toc:end -->

## 참고 자료

- [aiosqlite — Documentation](https://aiosqlite.omnilib.dev/)
- [aiosqlite — GitHub](https://github.com/omnilib/aiosqlite)
- [FastAPI — Concurrency and async/await](https://fastapi.tiangolo.com/async/)
- [Python asyncio — Streams and synchronization primitives](https://docs.python.org/3/library/asyncio.html)
- [SQLite — Write-Ahead Logging](https://www.sqlite.org/wal.html)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/python-dbapi-101/ko)

Tags: Python, DB-API, PEP 249, Database
