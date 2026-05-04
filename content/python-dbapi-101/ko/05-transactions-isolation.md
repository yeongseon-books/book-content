---
title: Transaction과 isolation level (sqlite3, PEP 249)
series: python-dbapi-101
episode: 5
language: ko
status: publish-ready
targets:
  tistory: true
  hashnode: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Python
- SQLite
- Transaction
- Isolation
- WAL
- PEP 249
last_reviewed: '2026-05-03'
seo_title: Transaction과 isolation level
seo_description: sqlite3 driver는 편의를 위해 implicit BEGIN을 자동으로 거는데, 이 동작을 모르면 위 두 사고가
  동시에 발생하기…
---

# Transaction과 isolation level (sqlite3, PEP 249)

## 이 글에서 답할 질문

- sqlite3는 왜 기본적으로 implicit BEGIN을 자동으로 거나요?
- `isolation_level=None`은 무엇을 의미하나요?
- `BEGIN DEFERRED`, `IMMEDIATE`, `EXCLUSIVE`는 lock 동작이 어떻게 다른가요?
- WAL mode가 transaction 동작에 어떤 영향을 주나요?
- Python 3.12에 추가된 `autocommit` 매개변수는 기존 `isolation_level`과 어떻게 다른가요?

> Transaction은 "commit/rollback 호출"이 아니라 "어디부터 어디까지가 한 단위인가"를 정하는 일입니다. sqlite3는 이 단위를 driver가 자동으로 잡아 주므로, 자동 동작을 정확히 알아야 의도하지 않은 lock과 데이터 유실을 피할 수 있습니다.

> Python DB-API 101 시리즈 (5/10)

---

## 이 글에서 배울 것

이 글에서는 sqlite3 driver의 transaction 동작을 PEP 249 관점에서 깊이 다룹니다. 구체적으로:

1. **PEP 249의 transaction 모델** — connection이 transaction 단위, `commit()`/`rollback()`이 종료 신호.
2. **sqlite3의 implicit BEGIN** — DML 실행 직전 driver가 자동으로 `BEGIN`을 발행하는 quirk.
3. **`isolation_level` 4가지 값** — `''` (default deferred), `'DEFERRED'`, `'IMMEDIATE'`, `'EXCLUSIVE'`, `None` (autocommit).
4. **WAL vs rollback journal** — 동시 reader/writer 동작 차이.
5. **SAVEPOINT를 활용한 nested transaction** — `with con:` 컨텍스트 매니저의 정확한 의미.
6. **Python 3.12 `autocommit` 매개변수** — 새로운 명시적 모델.

---

## 왜 중요한가

운영에서 가장 흔한 데이터 사고는 두 가지입니다.

1. **`commit()`을 잊어버림** — INSERT는 메모리에만 남고 프로세스 종료 시 사라집니다.
2. **모르는 사이 `BEGIN IMMEDIATE`가 걸려 다른 connection이 lock을 기다림** — 사용자에게 5초 timeout 오류로 노출됩니다.

sqlite3 driver는 편의를 위해 implicit BEGIN을 자동으로 거는데, 이 동작을 모르면 위 두 사고가 동시에 발생하기 쉽습니다. PEP 249는 driver마다 다른 이 자동 동작을 명시적으로 통제할 수 있도록 `isolation_level` (sqlite3) 또는 `autocommit` 속성을 노출합니다.

이 글에서는 5가지 모드의 동작을 코드와 lock 시나리오로 비교합니다. 한 번 정리해 두면 transaction 관련 운영 이슈의 80%가 사라집니다.

---

## Mental Model — connection이 transaction 단위

```
Connection lifecycle (sqlite3 default)
─────────────────────────────────────────
  open
    │
    │  cur.execute('SELECT ...')   ← transaction 없음
    │  cur.execute('INSERT ...')   ← driver가 implicit BEGIN
    │  cur.execute('UPDATE ...')   ← 같은 transaction 안
    │
    │  con.commit()                ← transaction 종료, durable
    │
    │  cur.execute('INSERT ...')   ← 새 implicit BEGIN
    │  con.rollback()              ← 변경 폐기
    │
  close
```

핵심 두 가지:

- **PEP 249는 모든 connection이 transaction을 시작한다고 가정합니다.** 즉 `autocommit=False`가 default.
- **sqlite3 default는 "DML 직전에 자동 BEGIN"** — SELECT만 할 때는 transaction이 열리지 않으므로 commit이 필요 없습니다.

---

## 핵심 개념

### `isolation_level` 5가지 값

| 값 | BEGIN 종류 | autocommit? | 자동 BEGIN 시점 |
|---|---|---|---|
| `''` (default) | `BEGIN` (= DEFERRED) | No | 첫 DML(INSERT/UPDATE/DELETE) 직전 |
| `'DEFERRED'` | `BEGIN DEFERRED` | No | 동일 |
| `'IMMEDIATE'` | `BEGIN IMMEDIATE` | No | 동일 (즉시 RESERVED lock 획득) |
| `'EXCLUSIVE'` | `BEGIN EXCLUSIVE` | No | 동일 (즉시 EXCLUSIVE lock 획득) |
| `None` | (BEGIN 없음) | **Yes** | 매 statement가 즉시 commit |

### BEGIN 모드별 lock 동작

SQLite는 동시 접근을 4단계 lock으로 제어합니다: UNLOCKED → SHARED → RESERVED → PENDING → EXCLUSIVE.

- **DEFERRED** — `BEGIN`만 호출되고 lock은 첫 read에서 SHARED, 첫 write에서 RESERVED로 승격. 다른 reader와 동시 가능.
- **IMMEDIATE** — `BEGIN` 시점에 즉시 RESERVED lock. 다른 writer는 즉시 차단되지만 reader는 계속 가능.
- **EXCLUSIVE** — `BEGIN` 시점에 즉시 EXCLUSIVE lock. 다른 reader/writer 모두 차단.

WAL mode가 아닌 default rollback journal에서는 writer 한 명과 reader 다수가 동시 가능, writer는 commit 시점에 잠시 EXCLUSIVE를 잡습니다.

### WAL mode

```python
con.execute('PRAGMA journal_mode=WAL')
```

WAL(Write-Ahead Logging)은 writer가 별도 `.wal` 파일에 기록하므로 **reader와 writer가 진짜로 동시에 동작**합니다. 운영 워크로드에서는 거의 항상 WAL이 권장입니다. 단, 같은 디렉터리에 `.wal`과 `.shm` 파일이 생기고, network filesystem에서는 정상 동작이 보장되지 않습니다.

### Python 3.12 `autocommit` 매개변수

```python
con = sqlite3.connect(path, autocommit=False)  # PEP 249 호환
con = sqlite3.connect(path, autocommit=True)   # 매 statement immediate commit
con = sqlite3.connect(path, autocommit=sqlite3.LEGACY_TRANSACTION_CONTROL)  # 기존 isolation_level 동작
```

3.12 이후로는 `autocommit`이 명시적이고 권장 방법입니다. legacy 코드와의 호환을 위해 `LEGACY_TRANSACTION_CONTROL`이 default입니다.

---

## Before / After

### Before — commit 누락

```python
import sqlite3

con = sqlite3.connect('shop.db')
con.execute('CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY, total INTEGER)')
con.execute('INSERT INTO orders(total) VALUES (10000)')
# con.commit()  ← 누락
con.close()

# 새 프로세스에서 확인
con2 = sqlite3.connect('shop.db')
print(con2.execute('SELECT COUNT(*) FROM orders').fetchone())
# → (0,)   ← INSERT가 사라짐
```

`con.close()`는 commit하지 않습니다. 실수로 commit을 빠뜨리면 데이터가 그대로 사라집니다.

### After — context manager

```python
with sqlite3.connect('shop.db') as con:
    con.execute('INSERT INTO orders(total) VALUES (10000)')
# 블록 정상 종료 시 commit, 예외 발생 시 rollback
```

`with con:`은 connection 자체에 대한 컨텍스트 매니저로, **transaction을 종료**합니다. connection을 close하지는 않으므로 별도로 닫아 줘야 합니다.

---

## 단계별 실습

### 단계 1 — 기본 동작 관찰

```python
import sqlite3

con = sqlite3.connect(':memory:')
con.execute('CREATE TABLE t(v INTEGER)')

# SELECT만 하면 transaction이 안 열림
con.execute('SELECT * FROM t').fetchall()
print(con.in_transaction)   # → False

# DML 직전 implicit BEGIN
con.execute('INSERT INTO t(v) VALUES (1)')
print(con.in_transaction)   # → True

con.commit()
print(con.in_transaction)   # → False
```

### 단계 2 — autocommit (`isolation_level=None`)

```python
con = sqlite3.connect(':memory:', isolation_level=None)
con.execute('CREATE TABLE t(v INTEGER)')
con.execute('INSERT INTO t(v) VALUES (1)')
# 별도 commit 없이도 즉시 durable
print(con.in_transaction)   # → False
```

대량 batch insert에는 적합하지 않습니다. 매 statement마다 fsync가 발생해 매우 느립니다.

### 단계 3 — IMMEDIATE로 lock 충돌 방지

긴 트랜잭션에서 read → modify → write 패턴을 쓰면 default DEFERRED는 SQLITE_BUSY가 늦게 터질 수 있습니다. write 의도가 분명하다면 처음부터 IMMEDIATE로 락을 잡습니다.

```python
con = sqlite3.connect('shop.db', isolation_level='IMMEDIATE')

with con:
    balance = con.execute('SELECT balance FROM accounts WHERE id=1').fetchone()[0]
    new_balance = balance - 1000
    con.execute('UPDATE accounts SET balance=? WHERE id=1', (new_balance,))
```

다른 writer는 IMMEDIATE 시점에 즉시 차단되므로, 우리 트랜잭션 중간에 다른 writer가 끼어들어 lost-update가 생기지 않습니다.

### 단계 4 — WAL mode 활성화

```python
con = sqlite3.connect('shop.db')
con.execute('PRAGMA journal_mode=WAL')
con.execute('PRAGMA synchronous=NORMAL')   # WAL에서 안전 + 빠름
```

`journal_mode`는 데이터베이스 파일 단위로 영구 저장되므로, 한 번만 설정하면 됩니다.

### 단계 5 — SAVEPOINT로 nested transaction

PEP 249는 nested transaction을 정의하지 않지만, SQLite는 `SAVEPOINT`로 흉내낼 수 있습니다.

```python
con.execute('SAVEPOINT sp1')
try:
    con.execute("INSERT INTO orders(total) VALUES (5000)")
    con.execute("INSERT INTO order_items VALUES (?, ?)", (1, 'item-A'))
    con.execute('RELEASE SAVEPOINT sp1')
except Exception:
    con.execute('ROLLBACK TO SAVEPOINT sp1')
    con.execute('RELEASE SAVEPOINT sp1')
    raise
```

OUTER transaction은 그대로 유지되고, savepoint 내부만 부분 rollback됩니다.

### 단계 6 — Python 3.12 명시적 autocommit

```python
import sqlite3
assert sqlite3.sqlite_version_info >= (3, 24)   # SAVEPOINT 안정 동작

con = sqlite3.connect('shop.db', autocommit=False)
con.execute('BEGIN IMMEDIATE')
try:
    con.execute('UPDATE accounts SET balance = balance - 1000 WHERE id = 1')
    con.execute('UPDATE accounts SET balance = balance + 1000 WHERE id = 2')
    con.commit()
except Exception:
    con.rollback()
    raise
```

`autocommit=False`로 두면 BEGIN을 명시적으로 작성해야 하며, driver가 자동으로 끼어들지 않습니다.

---

## 자주 하는 실수

1. **`con.close()`가 commit해 줄 거라고 가정** — 그러지 않습니다. 변경은 사라집니다.
2. **`with sqlite3.connect(...) as con:`을 close로 착각** — 이 컨텍스트는 transaction을 종료할 뿐, connection은 그대로 열려 있습니다. close는 따로 호출하거나 `contextlib.closing`을 함께 씁니다.
3. **장시간 read에 default DEFERRED 사용** — read 도중 다른 writer가 들어와 commit하면 본인은 SQLITE_BUSY를 만나기 쉽습니다. read-only면 `BEGIN`을 명시하지 않거나, 일관성이 필요하면 `BEGIN IMMEDIATE`.
4. **`isolation_level=None`을 batch insert에 사용** — 매 statement fsync로 100~1000배 느려질 수 있습니다.
5. **WAL mode를 NFS/SMB에 설정** — 잠금 동작이 깨져 데이터 손상 가능. 로컬 디스크에서만 사용.
6. **여러 connection이 같은 transaction을 공유한다고 가정** — 각 connection은 독립된 transaction 컨텍스트를 가집니다. 같은 트랜잭션을 공유하려면 같은 connection 객체를 사용해야 합니다.
7. **`PRAGMA journal_mode=WAL`을 transaction 안에서 호출** — DDL 변경처럼 외부 lock이 필요해 실패합니다. connection 시작 직후에 설정하세요.
8. **3.12 이상에서 `isolation_level`과 `autocommit`을 혼용** — `autocommit`이 우선합니다. 새 코드는 `autocommit`만 쓰는 것이 깔끔합니다.

---

## 실무 적용

### 운영 워크로드 권장 설정

```python
con = sqlite3.connect('app.db', timeout=5.0, isolation_level='IMMEDIATE')
con.execute('PRAGMA journal_mode=WAL')
con.execute('PRAGMA synchronous=NORMAL')
con.execute('PRAGMA foreign_keys=ON')
con.execute('PRAGMA busy_timeout=5000')
```

- `timeout=5.0` (Python) + `busy_timeout=5000` (SQLite) — lock 충돌 시 5초까지 자동 재시도.
- `IMMEDIATE` — write 의도를 명시해 SQLITE_BUSY 위험을 앞당김.
- `WAL` + `synchronous=NORMAL` — 동시성과 성능 균형.

### transaction-per-request 패턴 (FastAPI 예시)

```python
from contextlib import contextmanager

@contextmanager
def tx():
    con = sqlite3.connect('app.db', isolation_level='IMMEDIATE')
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()

# 사용
with tx() as con:
    con.execute('INSERT INTO orders(total) VALUES (?)', (10000,))
```

요청 1건 = transaction 1건 = connection 1건. 단순하고 디버깅 쉬움.

### 모니터링

운영에서는 다음 두 metric만 있어도 사고를 빠르게 잡습니다.

- `SQLITE_BUSY` 카운트 — lock 경합이 늘면 IMMEDIATE 빈도나 transaction 길이를 점검.
- transaction 평균 길이(ms) — 100ms를 넘기 시작하면 read-modify-write 구간을 분리하는 신호.

### 백업

WAL mode에서는 `.backup()` API가 안전합니다.

```python
src = sqlite3.connect('app.db')
dst = sqlite3.connect('backup.db')
with dst:
    src.backup(dst)
```

---

## 체크리스트

- [ ] `con.close()` 전에 항상 `con.commit()` 또는 `with con:`로 끝낸다.
- [ ] write가 포함된 함수는 `isolation_level='IMMEDIATE'`로 시작한다.
- [ ] 운영 DB는 WAL mode + `synchronous=NORMAL` + `busy_timeout=5000`을 기본값으로 둔다.
- [ ] read-only 쿼리는 별도 connection 또는 명시적 `BEGIN`을 쓰지 않는다.
- [ ] `autocommit=None` (legacy)을 batch insert에 쓰지 않는다.
- [ ] nested 동작이 필요하면 `SAVEPOINT`를 명시적으로 작성한다.
- [ ] Python 3.12+ 신규 코드는 `autocommit=False` + 명시적 BEGIN으로 작성한다.

---

## 연습 문제

1. **commit 누락 실험** — `with con:` 없이 INSERT 후 close하고, 새 프로세스에서 row 수가 0인 것을 확인하세요. 이어서 `with con:`을 추가하고 다시 확인하세요.
2. **DEFERRED vs IMMEDIATE** — 두 개의 Python 프로세스에서 동시에 INSERT를 시작하고, 한쪽이 SQLITE_BUSY를 만나는 시점이 DEFERRED일 때와 IMMEDIATE일 때 어떻게 다른지 관찰하세요.
3. **WAL 효과** — `journal_mode=DELETE`(default)와 `WAL`에서 reader 5명 + writer 1명이 동시에 동작할 때 처리량을 비교하세요.
4. **SAVEPOINT** — 한 트랜잭션 안에서 INSERT 3건 → SAVEPOINT → 추가 INSERT 2건 → ROLLBACK TO 시 row 수가 어떻게 되는지 확인하세요.
5. **autocommit 비교** — Python 3.12+에서 `autocommit=True`/`False`/`LEGACY_TRANSACTION_CONTROL` 세 모드의 `con.in_transaction` 값을 동일 시나리오에서 비교하세요.

---

## 정리·다음 글

sqlite3의 transaction은 driver가 친절하게 자동 관리해 주지만, 그 자동 동작을 모르면 운영에서 lock과 데이터 유실로 직결됩니다. `isolation_level` 5가지 값과 `BEGIN` 변종, WAL mode를 한 번 정리해 두면 대부분의 transaction 이슈가 진단 가능해집니다.

다음 글에서는 **row factory와 type adapter**를 다룹니다. 기본 tuple 결과를 dict, dataclass, Pydantic 모델로 받는 방법, `detect_types`와 사용자 정의 adapter/converter, 그리고 새 타입(예: `Decimal`, `enum`)을 안전하게 매핑하는 법을 코드로 정리합니다.

<!-- toc:begin -->
## 시리즈 목차

- [왜 DB-API 2.0인가 - PEP 249가 푼 문제](./01-why-db-api-pep-249.md)
- [Connection과 Cursor Lifecycle](./02-connection-cursor-lifecycle.md)
- [execute, executemany, fetch 패턴](./03-execute-fetch-patterns.md)
- [Parameter binding과 SQL injection 방어 (sqlite3, PEP 249)](./04-parameter-binding-sql-injection.md)
- **Transaction과 isolation level (sqlite3, PEP 249) (현재 글)**
- Row factory와 type adapter (sqlite3, PEP 249) (예정)
- PEP 249 예외 계층과 SQLite 에러 처리 (예정)
- SQLite Connection 관리: thread-safety, check_same_thread, 그리고 풀링 (예정)
- aiosqlite로 비동기 SQLite 다루기 (예정)
- SQLite Production 패턴: retry, timeout, 관측성, 백업 (예정)

<!-- toc:end -->

---

## 참고 자료

- [PEP 249 – Python Database API Specification v2.0](https://peps.python.org/pep-0249/)
- [Python sqlite3 — transaction control](https://docs.python.org/3/library/sqlite3.html#sqlite3-controlling-transactions)
- [SQLite — File Locking and Concurrency](https://www.sqlite.org/lockingv3.html)
- [SQLite — Write-Ahead Logging](https://www.sqlite.org/wal.html)
- [SQLite — PRAGMA journal_mode](https://www.sqlite.org/pragma.html#pragma_journal_mode)
- [Python 3.12 sqlite3 autocommit](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.autocommit)

Tags: Python, DB-API, PEP 249, Database
