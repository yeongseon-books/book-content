---
episode: 9
language: ko
last_reviewed: '2026-05-03'
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
  hashnode: true
  medium: true
  mkdocs: true
  tistory: true
title: aiosqlite로 비동기 SQLite 다루기
seo_description: aiosqlite는 SQLite를 비동기로 바꾸지 않는다. connection마다 백그라운드 스레드를 띄우고, await되는
  메서드 호출을…
---

# aiosqlite로 비동기 SQLite 다루기

`asyncio` 코드 안에 `sqlite3.connect()`를 그대로 두면 어떻게 될까요? 코드는 동작하지만, `execute()`가 동기 호출이라 이벤트 루프가 그 시간 동안 멈춥니다. 한 요청이 1초 걸리는 쿼리를 돌리면 같은 워커의 다른 모든 요청이 1초 동안 응답을 못 받습니다.

`aiosqlite`는 이 문제를 해결합니다. 다만 "해결"의 의미를 정확히 알아야 합니다. 이 라이브러리는 SQLite를 진짜 비동기로 만들지 않고, **별도 스레드에서 sqlite3 호출을 실행하고 결과를 future로 돌려주는 어댑터**입니다. 그래서 이벤트 루프는 안 막히지만, SQLite 엔진 자체의 단일 writer 제약은 그대로 남습니다.

![aiosqlite로 비동기 SQLite 다루기](../../assets/python-dbapi-101/09/09-01-asynchronous-sqlite-with-aiosqlite.ko.png)

*aiosqlite로 비동기 SQLite 다루기*

## 이 글에서 다룰 문제

asyncio 기반 프레임워크(FastAPI, aiohttp, Starlette)에서 동기 SQLite를 그대로 호출하면 I/O 시간만큼 워커가 멈춥니다. 한 워커가 100개의 동시 요청을 처리한다고 가정할 때, 평균 50ms짜리 쿼리 하나가 들어오면 다른 99개 요청의 p99 latency가 망가집니다.

해결책은 두 가지입니다. (1) 동기 sqlite3을 별도 스레드 풀(`run_in_executor`, FastAPI의 `def` 핸들러)로 옮기거나, (2) `aiosqlite`로 비동기 인터페이스를 사용하는 것. 둘은 본질적으로 같은 메커니즘이지만, `aiosqlite`는 connection-per-thread 관리를 캡슐화해 주고 `async with` 문법이 자연스럽게 어울립니다.

이 글은 `aiosqlite`가 실제로 무엇을 해 주고 무엇을 안 해 주는지를 정직하게 보여 줍니다. "비동기"라는 단어 때문에 동시 쓰기 처리량이 늘어날 거라고 기대하면 실망합니다.

## Mental Model: aiosqlite는 sqlite3 + thread + Future

![Mental Model: aiosqlite는 sqlite3 + thread + Future](../../assets/python-dbapi-101/09/09-02-mental-model-aiosqlite-is-sqlite3-thread.ko.png)

*Mental Model: aiosqlite는 sqlite3 + thread + Future*
> aiosqlite는 SQLite를 비동기로 바꾸지 않는다. connection마다 백그라운드 스레드를 띄우고, `await`되는 메서드 호출을 그 스레드의 큐로 넣고, 결과를 Future로 받아 이벤트 루프에 돌려준다.

이 구조의 함의:

- 이벤트 루프는 안 막힌다. 다른 코루틴이 그 동안 진행될 수 있다.
- 단일 connection 안에서는 호출이 직렬이다. 같은 connection을 두 코루틴이 동시에 쓸 수 없다.
- connection 하나당 스레드 하나가 따라다니므로, connection을 많이 만들면 스레드도 많이 생긴다.
- SQLite의 단일 writer 제약은 그대로다. `aiosqlite` connection 100개를 만들어도 동시에 쓰는 writer는 1명이다.

따라서 `aiosqlite`의 진짜 가치는 "동시성 이득"이 아니라 "**이벤트 루프 보호**"입니다. 동기 sqlite3을 async 코드에 직접 쓰지 않기 위한 어댑터로 이해하는 것이 정확합니다.

## 핵심 개념

![핵심 개념](../../assets/python-dbapi-101/09/09-03-core-concepts.ko.png)

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
# 동기
import sqlite3
conn = sqlite3.connect("app.db")
cur = conn.execute("SELECT 1")
row = cur.fetchone()

# 비동기
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

![단계별 실습: 가벼운 connection 풀 만들기](../../assets/python-dbapi-101/09/09-04-step-by-step-a-lightweight-connection-po.ko.png)

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

## 정리와 다음 글

- `aiosqlite`는 SQLite를 진짜 비동기로 만들지 않는다. 이벤트 루프 보호용 어댑터다.
- 동시 쓰기 처리량은 늘지 않는다. SQLite의 단일 writer 제약은 그대로다.
- async path가 진짜 필요할 때만 도입하라. 그렇지 않다면 `def` 핸들러 + sqlite3가 더 단순하다.
- 풀이 필요하면 가벼운 `asyncio.Queue` 기반으로 충분하다. lifespan에서 초기화하라.

다음 글(Ep10, 시리즈 마지막)은 production 패턴을 정리합니다. retry+timeout+observability, slow query logging, OpenTelemetry instrumentation, 백업 전략까지 한 번에 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [왜 DB-API 2.0인가 - PEP 249가 푼 문제](./01-why-db-api-pep-249.md)
- [Connection과 Cursor Lifecycle](./02-connection-cursor-lifecycle.md)
- [execute, executemany, fetch 패턴](./03-execute-fetch-patterns.md)
- [Parameter binding과 SQL injection 방어 (sqlite3, PEP 249)](./04-parameter-binding-sql-injection.md)
- [Transaction과 isolation level (sqlite3, PEP 249)](./05-transactions-isolation.md)
- [Row factory와 type adapter (sqlite3, PEP 249)](./06-row-factories-adapters.md)
- [PEP 249 예외 계층과 SQLite 에러 처리](./07-error-handling-exception-hierarchy.md)
- [SQLite Connection 관리: thread-safety, check_same_thread, 그리고 풀링](./08-connection-pooling.md)
- **aiosqlite로 비동기 SQLite 다루기 (현재 글)**
- SQLite Production 패턴: retry, timeout, 관측성, 백업 (예정)

<!-- toc:end -->

## 참고 자료

- [aiosqlite — Documentation](https://aiosqlite.omnilib.dev/)
- [aiosqlite — GitHub](https://github.com/omnilib/aiosqlite)
- [FastAPI — Concurrency and async/await](https://fastapi.tiangolo.com/async/)
- [Python asyncio — Streams and synchronization primitives](https://docs.python.org/3/library/asyncio.html)
- [SQLite — Write-Ahead Logging](https://www.sqlite.org/wal.html)
