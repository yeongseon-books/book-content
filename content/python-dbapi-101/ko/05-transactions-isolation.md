---
title: "Python DB-API 101 (5/10): Transaction과 isolation level (sqlite3, PEP 249)"
series: python-dbapi-101
episode: 5
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
- Transaction
- Isolation
- WAL
- PEP 249
last_reviewed: '2026-05-12'
seo_title: Transaction과 isolation level
seo_description: sqlite3 driver는 편의를 위해 implicit BEGIN을 자동으로 거는데, 이 동작을 모르면 위 두 사고가
  동시에 발생하기…
---

# Python DB-API 101 (5/10): Transaction과 isolation level (sqlite3, PEP 249)

sqlite3는 편의를 위해 트랜잭션을 암묵적으로 시작합니다. 이 동작을 이해하지 못하면 commit 누락과 lock 대기가 함께 생기므로, 이 글에서는 isolation level과 autocommit 관점을 함께 정리합니다.

이 글은 Python DB-API 101 시리즈의 다섯 번째 글입니다.

![Transaction과 isolation level (sqlite3, PEP 249)](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/05/05-01-transactions-and-isolation-levels-sqlite.ko.png)

*Transaction과 isolation level (sqlite3, PEP 249)*

![Python DB-API 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/05/05-02-mental-model-connection-is-the-transacti.ko.png)
*Python DB-API 101 5장 흐름 개요*

## 먼저 던지는 질문

- Transaction과 isolation level (sqlite3, PEP 249)를 운영 관점에서 볼 때 먼저 어떤 경계를 확인해야 할까요?
- Transaction과 isolation level (sqlite3, PEP 249)에서 예제나 다이어그램으로 검증해야 할 핵심 신호는 무엇일까요?
- Transaction과 isolation level (sqlite3, PEP 249)를 실제 시스템에 적용할 때 어떤 실패를 먼저 막아야 할까요?

## Mental Model — connection이 transaction 단위

```text
Connection lifecycle (sqlite3 default)
─────────────────────────────────────────
  open
    │
    │  cur.execute('SELECT ...')   ← no transaction
    │  cur.execute('INSERT ...')   ← driver issues implicit BEGIN
    │  cur.execute('UPDATE ...')   ← same transaction
    │
    │  con.commit()                ← transaction ends, durable
    │
    │  cur.execute('INSERT ...')   ← new implicit BEGIN
    │  con.rollback()              ← changes discarded
    │
  close
```

> transaction은 `commit()`과 `rollback()`이라는 함수 이름이 아니라, "어디부터 어디까지를 한 덩어리로 묶을 것인가"를 정하는 경계입니다. sqlite3는 그 경계를 자동으로 잡아 주기 때문에, 자동 동작을 모르면 락과 데이터 손실을 함께 맞게 됩니다.

핵심 두 가지:

- **PEP 249는 모든 connection이 transaction을 시작한다고 가정합니다.** 즉 `autocommit=False`가 default.
- **sqlite3 default는 "DML 직전에 자동 BEGIN"** — SELECT만 할 때는 transaction이 열리지 않으므로 commit이 필요 없습니다.

---

## 핵심 개념

![핵심 개념](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/05/05-03-core-concepts.ko.png)

*핵심 개념*
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

### WAL 모드

```python
con.execute('PRAGMA journal_mode=WAL')
```

WAL(Write-Ahead Logging)은 writer가 별도 `.wal` 파일에 기록하므로 **reader와 writer가 진짜로 동시에 동작**합니다. 운영 워크로드에서는 거의 항상 WAL이 권장입니다. 단, 같은 디렉터리에 `.wal`과 `.shm` 파일이 생기고, network filesystem에서는 정상 동작이 보장되지 않습니다.

### Python 3.12 `autocommit` 매개변수

```python
con = sqlite3.connect(path, autocommit=False)  # PEP 249 compliant
con = sqlite3.connect(path, autocommit=True)   # commit after every statement
con = sqlite3.connect(path, autocommit=sqlite3.LEGACY_TRANSACTION_CONTROL)  # legacy isolation_level behaviour
```

3.12 이후로는 `autocommit`이 명시적이고 권장 방법입니다. legacy 코드와의 호환을 위해 `LEGACY_TRANSACTION_CONTROL`이 default입니다.

---

## 적용 전후 비교
### Before — commit 누락

```python
import sqlite3

con = sqlite3.connect('shop.db')
con.execute('CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY, total INTEGER)')
con.execute('INSERT INTO orders(total) VALUES (10000)')
# con.commit() ← 잊어버렸습니다
con.close()

# 새 프로세스에서
con2 = sqlite3.connect('shop.db')
print(con2.execute('SELECT COUNT(*) FROM orders').fetchone())
# → (0,) ← INSERT가 삭제되었습니다.
```

`con.close()`는 commit하지 않습니다. 실수로 commit을 빠뜨리면 데이터가 그대로 사라집니다.

### 적용 후 — 컨텍스트 매니저

```python
with sqlite3.connect('shop.db') as con:
    con.execute('INSERT INTO orders(total) VALUES (10000)')
# 정상 종료 시 커밋, 예외 시 롤백
```

`with con:`은 connection 자체에 대한 컨텍스트 매니저로, **transaction을 종료**합니다. connection을 close하지는 않으므로 별도로 닫아 줘야 합니다.

---

## 단계별 실습

![단계별 실습](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/05/05-04-step-by-step-walkthrough.ko.png)

*단계별 실습*
### 단계 1 — 기본 동작 관찰

```python
import sqlite3

con = sqlite3.connect(':memory:')
con.execute('CREATE TABLE t(v INTEGER)')

# SELECT만으로는 트랜잭션이 열리지 않습니다
con.execute('SELECT * FROM t').fetchall()
print(con.in_transaction)   # → False

# DML 전에 암묵적 BEGIN
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
# 이미 영속 처리됨, commit 불필요
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
con.execute('PRAGMA synchronous=NORMAL')   # safe + fast under WAL
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
assert sqlite3.sqlite_version_info >= (3, 24)   # SAVEPOINT stable

con = sqlite3.connect('shop.db', autocommit=False)
print(con.in_transaction)   # → True
try:
    con.execute('UPDATE accounts SET balance = balance - 1000 WHERE id = 1')
    con.execute('UPDATE accounts SET balance = balance + 1000 WHERE id = 2')
    con.commit()
except Exception:
    con.rollback()
    raise
```

`autocommit=False`로 두면 sqlite3가 `connect()`, `commit()`, `rollback()` 뒤에 `BEGIN DEFERRED` 트랜잭션을 암묵적으로 다시 열어 둡니다. 따라서 Python 3.12+의 일반적인 PEP 249 흐름에서는 `autocommit=False`에 수동 `BEGIN`을 덧붙이지 않습니다.

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

# Usage
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
- [ ] `sqlite3.LEGACY_TRANSACTION_CONTROL` legacy 모드를 batch insert에 쓰지 않는다.
- [ ] nested 동작이 필요하면 `SAVEPOINT`를 명시적으로 작성한다.
- [ ] Python 3.12+ 신규 코드는 `autocommit=False`로 PEP 249 의미를 따르고, 중복되는 수동 `BEGIN`을 덧붙이지 않는다.

---

## 심화 앵커: isolation level 비교를 코드로 재현하기

격리 수준은 용어 암기보다 충돌 시점을 재현해 보는 편이 빠릅니다. `IMMEDIATE`는 write 의도를 트랜잭션 시작 시점에 드러내므로 충돌을 늦게 맞지 않습니다.

```python
import sqlite3

conn = sqlite3.connect("app.db", isolation_level="IMMEDIATE", timeout=1.0)
conn.execute("BEGIN IMMEDIATE")
try:
    conn.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
    conn.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2")
    conn.commit()
except Exception:
    conn.rollback()
    raise
finally:
    conn.close()
```

| 모드 | 충돌 감지 시점 | 권장 |
| --- | --- | --- |
| DEFERRED | 첫 write 시점 | read 중심 |
| IMMEDIATE | BEGIN 시점 | write 포함 기본값 |
| EXCLUSIVE | BEGIN 시점(전체 차단) | 유지보수 작업 |

운영 규칙은 단순합니다. `OperationalError(BUSY/LOCKED)`는 짧은 백오프 재시도, `IntegrityError`는 즉시 실패, `CORRUPT` 계열은 복구 절차로 전환합니다.

## 정리
sqlite3의 transaction은 driver가 친절하게 자동 관리해 주지만, 그 자동 동작을 모르면 운영에서 lock과 데이터 유실로 직결됩니다. `isolation_level` 5가지 값과 `BEGIN` 변종, WAL mode를 한 번 정리해 두면 대부분의 transaction 이슈가 진단 가능해집니다.

다음 글에서는 **row factory와 type adapter**를 다룹니다. 기본 tuple 결과를 dict, dataclass, Pydantic 모델로 받는 방법, `detect_types`와 사용자 정의 adapter/converter, 그리고 새 타입(예: `Decimal`, `enum`)을 안전하게 매핑하는 법을 코드로 정리합니다.

## 처음 질문으로 돌아가기

- **Transaction과 isolation level (sqlite3, PEP 249)를 운영 관점에서 볼 때 먼저 어떤 경계를 확인해야 할까요?**
  - 먼저 봐야 할 경계는 transaction이 connection 어디서 열리고 `commit()` 또는 `rollback()`으로 어디서 닫히는지입니다. sqlite3는 첫 DML 직전에 implicit `BEGIN`을 거는 driver이므로, 이 자동 경계를 모르면 `con.close()`만 호출하고 데이터를 잃거나 lock 대기를 뒤늦게 맞게 됩니다.
- **Transaction과 isolation level (sqlite3, PEP 249)에서 예제나 다이어그램으로 검증해야 할 핵심 신호는 무엇일까요?**
  - 본문에서 가장 중요한 신호는 `con.in_transaction` 값, `isolation_level`별 BEGIN 방식, 그리고 `DEFERRED`·`IMMEDIATE`·`EXCLUSIVE`가 락을 잡는 시점입니다. 여기에 `PRAGMA journal_mode=WAL`과 Python 3.12의 `autocommit=False` 예제를 함께 보면, 읽기/쓰기 혼합 워크로드에서 어떤 설정이 충돌을 앞당기고 어떤 설정이 동시성을 높이는지 바로 드러납니다.
- **Transaction과 isolation level (sqlite3, PEP 249)를 실제 시스템에 적용할 때 어떤 실패를 먼저 막아야 할까요?**
  - 우선 막아야 할 실패는 commit 누락으로 인한 데이터 유실, 장시간 DEFERRED 트랜잭션으로 인한 `SQLITE_BUSY`, 그리고 WAL 없이 writer가 reader를 오래 막는 상황입니다. 그래서 이 글은 write 경로의 `IMMEDIATE`, 운영 기본값으로 `WAL + synchronous=NORMAL + busy_timeout`, 그리고 nested 작업용 `SAVEPOINT`를 실무 기본 패턴으로 묶었습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Python DB-API 101 (1/10): 왜 DB-API 2.0인가 - PEP 249가 푼 문제](./01-why-db-api-pep-249.md)
- [Python DB-API 101 (2/10): Connection과 Cursor Lifecycle](./02-connection-cursor-lifecycle.md)
- [Python DB-API 101 (3/10): execute, executemany, fetch 패턴](./03-execute-fetch-patterns.md)
- [Python DB-API 101 (4/10): Parameter binding과 SQL injection 방어 (sqlite3, PEP 249)](./04-parameter-binding-sql-injection.md)
- **Python DB-API 101 (5/10): Transaction과 isolation level (sqlite3, PEP 249) (현재 글)**
- Python DB-API 101 (6/10): Row factory와 type adapter (sqlite3, PEP 249) (예정)
- Python DB-API 101 (7/10): PEP 249 예외 계층과 SQLite 에러 처리 (예정)
- Python DB-API 101 (8/10): SQLite Connection 관리: thread-safety, check_same_thread, 그리고 풀링 (예정)
- Python DB-API 101 (9/10): aiosqlite로 비동기 SQLite 다루기 (예정)
- Python DB-API 101 (10/10): SQLite Production 패턴: retry, timeout, 관측성, 백업 (예정)

<!-- toc:end -->

---

## 참고 자료

- [PEP 249 – Python Database API Specification v2.0](https://peps.python.org/pep-0249/)
- [Python sqlite3 — transaction control](https://docs.python.org/3/library/sqlite3.html#sqlite3-controlling-transactions)
- [SQLite — File Locking and Concurrency](https://www.sqlite.org/lockingv3.html)
- [SQLite — Write-Ahead Logging](https://www.sqlite.org/wal.html)
- [SQLite — PRAGMA journal_mode](https://www.sqlite.org/pragma.html#pragma_journal_mode)
- [Python 3.12 sqlite3 autocommit](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.autocommit)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/python-dbapi-101/ko)

Tags: Python, DB-API, PEP 249, Database
