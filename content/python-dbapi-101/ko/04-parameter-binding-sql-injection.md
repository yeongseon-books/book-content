---
title: "Python DB-API 101 (4/10): Parameter binding과 SQL injection 방어 (sqlite3, PEP 249)"
series: python-dbapi-101
episode: 4
language: ko
status: publish-ready
targets:
  tistory: true
  hashnode: false
  medium: false
  mkdocs: true
  ebook: true
tags:
- Python
- SQLite
- SQL Injection
- Parameter Binding
- PEP 249
- Security
last_reviewed: '2026-05-12'
seo_title: Parameter binding과 SQL injection 방어
seo_description: 핵심은 SQL 토큰화(tokenization)가 binding보다 먼저 끝난다는 점입니다. ?
---

# Python DB-API 101 (4/10): Parameter binding과 SQL injection 방어 (sqlite3, PEP 249)

사용자 입력을 문자열로 이어 붙이는 SQL은 작은 편의처럼 보여도 전체 테이블 노출로 이어질 수 있습니다. 이 글에서는 sqlite3와 PEP 249 기준으로 parameter binding이 왜 SQL injection을 막는지 코드로 확인합니다.

이 글은 Python DB-API 101 시리즈의 네 번째 글입니다.

![Parameter binding과 SQL injection 방어 (sqlite3, PEP 249)](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/04/04-01-parameter-binding-and-sql-injection-defe.ko.png)

*Parameter binding과 SQL injection 방어 (sqlite3, PEP 249)*

## 먼저 던지는 질문

- Parameter binding과 SQL injection 방어 (sqlite3, PEP 249)를 운영 관점에서 볼 때 먼저 어떤 경계를 확인해야 할까요?
- Parameter binding과 SQL injection 방어 (sqlite3, PEP 249)에서 예제나 다이어그램으로 검증해야 할 핵심 신호는 무엇일까요?
- Parameter binding과 SQL injection 방어 (sqlite3, PEP 249)를 실제 시스템에 적용할 때 어떤 실패를 먼저 막아야 할까요?

## 큰 그림

![Python DB-API 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/04/04-02-mental-model-keep-query-string-and-value.ko.png)

*Python DB-API 101 4장 흐름 개요*

## Mental Model — query string과 값을 끝까지 분리

```text
[ User input ] ─┐
                │
                ▼
        [ cursor.execute(SQL, params) ]
                │
       ┌────────┴─────────┐
       ▼                  ▼
  [ SQL parser ]    [ value binder ]
   (parses ?, :name)   (sqlite3 type-checks
                        and escapes safely)
       │                  │
       └────────┬─────────┘
                ▼
        [ prepared statement ]
                │
                ▼
        [ SQLite executes ]
```

> SQL injection은 query string과 사용자 입력이 하나의 문자열로 합쳐지는 순간 시작됩니다. parameter binding은 이 둘을 끝까지 분리해서, 값이 SQL 문법으로 다시 해석되지 못하게 막습니다.

핵심은 SQL 토큰화(tokenization)가 binding보다 먼저 끝난다는 점입니다. `?`는 SQL parser에게 "여기에 값이 하나 들어올 자리"라고 알려 줄 뿐, 어떤 값이 와도 SQL 문법으로 재해석되지 않습니다. `' OR 1=1 --`이라는 문자열은 그대로 12글자짜리 문자열 값으로만 처리됩니다.

---

## 핵심 개념

![핵심 개념](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/04/04-03-core-concepts.ko.png)

*핵심 개념*
### qmark style (`?`)

sqlite3 default. 위치 기반 binding이라 순서가 중요합니다.

```python
cur.execute('SELECT * FROM users WHERE name = ? AND age >= ?', ('Alice', 18))
```

### named style (`:name`)

sqlite3 native. dict로 binding하면 순서 무관, 같은 값을 여러 번 참조 가능.

```python
cur.execute(
    'SELECT * FROM users WHERE name = :name AND created_by = :name',
    {'name': 'Alice'},
)
```

### paramstyle

PEP 249는 driver가 자신이 지원하는 placeholder 스타일을 `module.paramstyle`로 노출하도록 규정합니다.

| Style | Example | Drivers |
|---|---|---|
| `qmark` | `WHERE id = ?` | sqlite3 |
| `numeric` | `WHERE id = :1` | (rare) |
| `named` | `WHERE id = :id` | sqlite3, oracledb |
| `format` | `WHERE id = %s` | mysql-connector |
| `pyformat` | `WHERE id = %(id)s` | psycopg, pymysql |

sqlite3는 `qmark`와 `named`를 모두 지원합니다. `import sqlite3; print(sqlite3.paramstyle)` → `'qmark'`. portable code에서는 사용 driver의 `paramstyle`에 맞춰 구성하거나, SQLAlchemy Core 같은 abstraction을 씁니다.

### binding되지 않는 자리

placeholder는 값 자리에만 쓸 수 있습니다. 다음은 binding 대상이 아닙니다.

- table name (`FROM ?` ❌)
- column name (`SELECT ? FROM users` ❌)
- ORDER BY 방향 (`ORDER BY age ?` ❌)
- LIMIT/OFFSET (sqlite3는 일부 지원, 다른 driver는 미지원)

이런 자리에는 whitelist 검증을 거쳐 직접 문자열로 삽입합니다.

---

## Before / After

![Before / after](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/04/04-04-before-after.ko.png)

*Before / after*
### Before — 취약한 코드

```python
import sqlite3

con = sqlite3.connect(':memory:')
con.executescript('''
    CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT, secret TEXT);
    INSERT INTO users(name, secret) VALUES ('Alice', 'A-token');
    INSERT INTO users(name, secret) VALUES ('Bob',   'B-token');
''')

def find_user_BAD(name: str):
    sql = f"SELECT id, name, secret FROM users WHERE name = '{name}'"
    return con.execute(sql).fetchall()

# Normal call
print(find_user_BAD('Alice'))
# → [(1, 'Alice', 'A-token')]

# Attack
print(find_user_BAD("Alice' OR 1=1 --"))
# → [(1, 'Alice', 'A-token'), (2, 'Bob', 'B-token')]   ← all rows leaked
```

### After — parameter binding

```python
def find_user_OK(name: str):
    sql = 'SELECT id, name, secret FROM users WHERE name = ?'
    return con.execute(sql, (name,)).fetchall()

print(find_user_OK("Alice' OR 1=1 --"))
# → []   ← no user with that name, so empty
```

차이는 한 줄입니다. 그러나 보안 결과는 정반대입니다.

---

## 단계별 실습

### 단계 1 — 환경 준비

```python
import sqlite3

con = sqlite3.connect(':memory:')
con.executescript('''
    CREATE TABLE products(
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        price INTEGER NOT NULL,
        category TEXT NOT NULL
    );
''')
```

### 단계 2 — `?` placeholder로 단건 insert

```python
con.execute(
    'INSERT INTO products(name, price, category) VALUES (?, ?, ?)',
    ('Notebook', 12000, 'stationery'),
)
con.commit()
```

값은 항상 **tuple 또는 list**로 넘깁니다. 단일 값이라도 `(value,)`처럼 쉼표를 빠뜨리지 마세요.

### 단계 3 — `:name` placeholder

```python
con.execute(
    '''INSERT INTO products(name, price, category)
       VALUES (:name, :price, :category)''',
    {'name': 'Pen', 'price': 1500, 'category': 'stationery'},
)
con.commit()
```

dict의 key가 placeholder 이름과 정확히 일치해야 합니다.

### 단계 4 — `executemany`로 bulk insert

```python
rows = [
    ('Eraser', 800,  'stationery'),
    ('Mug',    9000, 'kitchen'),
    ('Lamp',   25000,'home'),
]
con.executemany(
    'INSERT INTO products(name, price, category) VALUES (?, ?, ?)',
    rows,
)
con.commit()
```

dict-style:

```python
rows = [
    {'name': 'Bowl', 'price': 4000, 'category': 'kitchen'},
    {'name': 'Vase', 'price': 18000,'category': 'home'},
]
con.executemany(
    'INSERT INTO products(name, price, category) VALUES (:name, :price, :category)',
    rows,
)
con.commit()
```

### 단계 5 — `IN (...)` 다루기

placeholder는 단일 값이므로 `IN (?)`에 list를 직접 넘기면 안 됩니다. 동적으로 placeholder를 생성합니다.

```python
ids = [1, 3, 5]
placeholders = ','.join('?' * len(ids))
sql = f'SELECT * FROM products WHERE id IN ({placeholders})'
print(con.execute(sql, ids).fetchall())
```

`placeholders` 변수는 SQL 토큰(쉼표와 `?`)만 포함하므로 안전합니다. 실제 값은 여전히 binding으로 전달됩니다.

### 단계 6 — 동적 ORDER BY 안전하게

```python
ALLOWED = {'name', 'price', 'category'}
ALLOWED_DIR = {'ASC', 'DESC'}

def list_products(order_by: str, direction: str):
    if order_by not in ALLOWED or direction.upper() not in ALLOWED_DIR:
        raise ValueError('invalid sort')
    sql = f'SELECT * FROM products ORDER BY {order_by} {direction.upper()}'
    return con.execute(sql).fetchall()
```

핵심은 **whitelist 검증**입니다. 사용자 입력이 SQL에 들어가지만, 허용된 값만 통과되므로 injection이 불가능합니다.

---

## 자주 하는 실수

1. **f-string으로 SQL 조립** — 가장 흔하고 가장 위험. code review에서 무관용으로 막아야 합니다.
2. **placeholder 따옴표로 감싸기** — `WHERE name = '?'`는 placeholder가 아니라 **물음표 한 글자**입니다. driver는 placeholder를 인식하지 못해 에러를 내거나 잘못된 결과를 반환합니다.
3. **단일 값 tuple 누락** — `con.execute(sql, ('Alice'))`는 string을 iterable로 보고 5개 인자가 있다고 해석합니다. 반드시 `('Alice',)`.
4. **table/column name binding 시도** — `cursor.execute('SELECT ? FROM ?', ('id', 'users'))`는 syntax error. 이런 자리는 whitelist + f-string.
5. **`%` operator로 escape하려는 시도** — `sql % values`는 binding이 아니라 Python 문자열 포맷팅입니다. SQL injection 그대로 노출됩니다.
6. **`executemany`에 단일 dict 전달** — `executemany(sql, {'a': 1})`는 dict의 key를 iteration하므로 잘못 동작합니다. list of dicts(`[{'a': 1}, {'a': 2}]`)여야 합니다.
7. **driver paramstyle 가정** — sqlite3 코드를 그대로 psycopg에 옮기면 `?`가 동작하지 않습니다. 새 driver에서는 `module.paramstyle`을 먼저 확인하거나 SQLAlchemy로 추상화하세요.

---

## 실무 적용

### 코드 리뷰 자동 검출

`bandit` 정적 분석은 `B608` rule로 SQL string formatting을 잡아 줍니다.

```bash
pip install bandit
bandit -r src/ -ll
```

CI에 넣어 merge 전에 차단합니다.

### query 로깅에서 값 마스킹

운영 로그에 SQL과 값이 그대로 찍히면 PII가 노출될 수 있습니다. binding 사용 시 log adapter에서 값을 hash 처리하거나 길이만 남기세요.

```python
def log_sql(sql, params):
    masked = tuple('***' if isinstance(p, str) and len(p) > 0 else p for p in params)
    logger.info('sql=%s params=%s', sql, masked)
```

### prepared statement 캐싱

driver는 같은 SQL string을 반복 호출하면 prepared statement를 재사용합니다. 따라서 **SQL string은 상수로 두고, 값만 binding으로 전달**하는 것이 성능에도 유리합니다. f-string으로 매번 다른 string을 만들면 캐시가 무효화됩니다.

### migration 시 driver 교체

sqlite3 → PostgreSQL로 옮길 때 가장 흔한 이슈가 paramstyle 차이입니다. 처음부터 SQLAlchemy Core(`text(':name')` + `bindparam`)나 ORM을 쓰면 driver 교체 비용이 크게 줄어듭니다 (다음 시리즈인 `sqlalchemy-101`에서 다룹니다).

---

## 체크리스트

- [ ] 모든 SQL은 `cursor.execute(sql, params)` 형태로 작성한다.
- [ ] f-string·`%`·`+`로 값을 SQL에 합치는 코드는 코드 리뷰에서 무조건 막는다.
- [ ] 단일 값 binding은 `(value,)` 형태로 쉼표를 잊지 않는다.
- [ ] table/column name 등 binding 불가능한 자리는 whitelist로 검증한다.
- [ ] `IN (...)`은 placeholder 개수를 동적으로 생성하고 값은 binding으로 넘긴다.
- [ ] `bandit B608` 같은 정적 분석을 CI에 추가한다.
- [ ] 로그에 binding 값을 그대로 남기지 않고 마스킹 규칙을 둔다.
- [ ] 새 driver를 도입하면 `module.paramstyle`을 먼저 확인한다.

---

## 정리
PEP 249의 parameter binding은 SQL injection을 차단하는 가장 단순하면서도 가장 강력한 도구입니다. 값과 SQL 문법을 끝까지 분리하는 것이 핵심이고, 이 분리가 깨지는 자리(table name 등)는 whitelist로 보완합니다.

다음 글에서는 **transaction과 isolation level**을 다룹니다. `commit`/`rollback`의 정확한 의미, sqlite3의 `isolation_level=None` autocommit 모드, BEGIN의 종류(DEFERRED, IMMEDIATE, EXCLUSIVE)와 lock 동작을 코드로 비교합니다.

## 심화 앵커: 인젝션 방어를 회귀 테스트로 고정하기

보안 규칙은 문장보다 테스트가 강합니다. 아래 테스트를 CI에 넣으면 문자열 결합 SQL이 다시 들어오는 순간 즉시 탐지할 수 있습니다.

```python
import sqlite3

def test_injection_blocked():
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT)")
    con.execute("INSERT INTO users(name) VALUES (?)", ("alice",))
    payload = "alice' OR 1=1 --"
    rows = con.execute("SELECT id FROM users WHERE name = ?", (payload,)).fetchall()
    assert rows == []
```

placeholder로 바인딩할 수 없는 자리는 whitelist 검증을 별도로 둬야 합니다.

```python
ALLOWED_SORT = {"name", "created_at"}
if sort not in ALLOWED_SORT:
    raise ValueError("invalid sort")
sql = f"SELECT id, name FROM users ORDER BY {sort}"
```

sqlite3(`?`)와 psycopg2(`%s`)의 차이를 감추기 위해 문자열 포맷팅으로 우회하면 취약점이 재발합니다. paramstyle 확인을 이관 체크리스트에 포함해야 합니다.

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

## 처음 질문으로 돌아가기

- **Parameter binding과 SQL injection 방어 (sqlite3, PEP 249)를 운영 관점에서 볼 때 먼저 어떤 경계를 확인해야 할까요?**
  - 본문의 기준은 Parameter binding과 SQL injection 방어 (sqlite3, PEP 249)를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Parameter binding과 SQL injection 방어 (sqlite3, PEP 249)에서 예제나 다이어그램으로 검증해야 할 핵심 신호는 무엇일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Parameter binding과 SQL injection 방어 (sqlite3, PEP 249)를 실제 시스템에 적용할 때 어떤 실패를 먼저 막아야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Python DB-API 101 (1/10): 왜 DB-API 2.0인가 - PEP 249가 푼 문제](./01-why-db-api-pep-249.md)
- [Python DB-API 101 (2/10): Connection과 Cursor Lifecycle](./02-connection-cursor-lifecycle.md)
- [Python DB-API 101 (3/10): execute, executemany, fetch 패턴](./03-execute-fetch-patterns.md)
- **Python DB-API 101 (4/10): Parameter binding과 SQL injection 방어 (sqlite3, PEP 249) (현재 글)**
- Python DB-API 101 (5/10): Transaction과 isolation level (sqlite3, PEP 249) (예정)
- Python DB-API 101 (6/10): Row factory와 type adapter (sqlite3, PEP 249) (예정)
- Python DB-API 101 (7/10): PEP 249 예외 계층과 SQLite 에러 처리 (예정)
- Python DB-API 101 (8/10): SQLite Connection 관리: thread-safety, check_same_thread, 그리고 풀링 (예정)
- Python DB-API 101 (9/10): aiosqlite로 비동기 SQLite 다루기 (예정)
- Python DB-API 101 (10/10): SQLite Production 패턴: retry, timeout, 관측성, 백업 (예정)

<!-- toc:end -->

---

## 참고 자료

- [PEP 249 – Python Database API Specification v2.0](https://peps.python.org/pep-0249/)
- [Python sqlite3 — placeholders](https://docs.python.org/3/library/sqlite3.html#sqlite3-placeholders)
- [OWASP — SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [Bandit — B608 hardcoded_sql_expressions](https://bandit.readthedocs.io/en/latest/plugins/b608_hardcoded_sql_expressions.html)
- [SQLite SQL parameters](https://www.sqlite.org/lang_expr.html#varparam)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/python-dbapi-101/ko)

Tags: Python, DB-API, PEP 249, Database
