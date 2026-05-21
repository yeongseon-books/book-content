---
title: "Python DB-API 101 (1/10): 왜 DB-API 2.0인가 - PEP 249가 푼 문제"
series: python-dbapi-101
episode: 1
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
- DB-API
- PEP 249
- SQLite
- Database Driver
- Standardization
last_reviewed: '2026-05-12'
seo_description: Python으로 데이터베이스를 다룬 적이 있다면 sqlite3, psycopg, pymysql, oracledb 같은
  패키지를 한 번쯤…
---

# Python DB-API 101 (1/10): 왜 DB-API 2.0인가 - PEP 249가 푼 문제

Python으로 데이터베이스를 다룬 적이 있다면 `sqlite3`, `psycopg`, `pymysql`, `oracledb` 같은 패키지를 한 번쯤 써봤을 겁니다. 그리고 신기하게도 그 사용법이 묘하게 비슷합니다. `connect()`로 연결을 만들고 `cursor()`로 cursor를 받고 `execute()`로 쿼리를 던지고 `fetchone()`/`fetchall()`로 결과를 꺼냅니다. 이 통일성은 우연이 아니라 1996년에 합의된 표준, **PEP 249 — Python Database API Specification v2.0** (줄여서 DB-API 2.0) 덕분입니다.

이번 첫 글에서는 DB-API 2.0이 왜 필요했는지, 무엇을 표준화했는지, 그리고 왜 이 시리즈가 SQLite를 기준으로 출발하는지 정리합니다.

이 글은 Python DB-API 101 시리즈의 첫 번째 글입니다.

![Why DB-API 2.0 - the problem PEP 249 solved](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/01/01-01-why-db-api-2-0-the-problem-pep-249-solve.ko.png)

*Why DB-API 2.0 - the problem PEP 249 solved*

![Python DB-API 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/01/01-02-1-the-chaos-before-db-api.ko.png)
*Python DB-API 101 1장 흐름 개요*

## 먼저 던지는 질문

- PEP 249 이전에는 Python의 데이터베이스 접근 코드가 왜 그렇게 제각각이었을까요?
- DB-API 2.0은 정확히 어떤 다섯 가지를 표준화했을까요?
- driver마다 `paramstyle`이 다른데도 왜 애플리케이션 코드는 대부분 그대로 옮겨질까요?

## 1. DB-API 이전의 혼돈

표준이 없던 시절, 각 데이터베이스 라이브러리는 자기만의 API를 가졌습니다.

```python
# 상상된 오래된 Oracle 모듈
conn = oracle.open("dsn", "user", "pass")
result = oracle.run_sql(conn, "SELECT * FROM users")
rows = oracle.read_all(result)

# 상상된 오래된 mysql 모듈
db = mysql.connect("server")
db.send("SELECT * FROM users")
data = db.receive_rows()
```

같은 일을 시키는데 함수 이름, 인자 순서, 반환 타입이 모두 달랐습니다. 한 회사 안에서도 oracle 코드와 mysql 코드가 완전히 다른 모양을 가졌고, DB를 갈아끼우는 것은 사실상 코드를 새로 쓰는 일이었습니다.

## 2. PEP 249가 표준화한 5가지

![PEP 249가 표준화한 5가지](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/01/01-03-2-five-things-pep-249-standardized.ko.png)

*PEP 249가 표준화한 5가지*
DB-API 2.0은 모든 driver가 지켜야 할 최소 contract를 정의합니다.

1. **Module-level constants**: `apilevel`, `threadsafety`, `paramstyle`
2. **Connection objects**: `connect()`, `close()`, `commit()`, `rollback()`, `cursor()`
3. **Cursor objects**: `execute()`, `executemany()`, `fetchone()`, `fetchall()`, `fetchmany()`, `rowcount`, `description`
4. **Type objects**: `Date`, `Time`, `Timestamp`, `Binary`, `STRING`, `NUMBER`, `DATETIME`, `ROWID`
5. **Exception hierarchy**: `Error` → `InterfaceError`, `DatabaseError` → `DataError`, `OperationalError`, `IntegrityError`, `InternalError`, `ProgrammingError`, `NotSupportedError`

이 정도만 합의되어도 application 코드는 driver 교체에 매우 유연해집니다.

## 3. SQLite로 첫 DB-API 코드 작성하기

이 시리즈는 모든 예제를 SQLite로 진행합니다. SQLite는 Python 표준 라이브러리(`sqlite3`)에 포함되어 있어서 별도 설치가 없고, 파일 하나가 곧 데이터베이스라 환경 셋업이 사실상 0초입니다.

```python
import sqlite3

# 1. 연결을 엽니다 — 파일이 없으면 자동 생성됩니다
conn = sqlite3.connect("notes.db")

# 2. 커서 획득
cur = conn.cursor()

# 3. Prepare schema
cur.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        body TEXT
    )
""")

# 4. 매개변수 바인딩을 사용한 INSERT
cur.execute(
    "INSERT INTO notes (title, body) VALUES (?, ?)",
    ("Starting DB-API", "First PEP 249 example"),
)

# 5. 트랜잭션 커밋
conn.commit()

# 6. SELECT
cur.execute("SELECT id, title FROM notes")
for row in cur.fetchall():
    print(row)

# 7. Cleanup
cur.close()
conn.close()
```

이 7단계는 PostgreSQL이든 MySQL이든 거의 그대로입니다. 차이점은 `connect()` 인자와 `paramstyle`(parameter 표기법) 정도입니다.

## 4. paramstyle 한 가지가 다르다

![paramstyle 한 가지가 다르다](https://yeongseon-books.github.io/book-public-assets/assets/python-dbapi-101/01/01-04-4-only-paramstyle-really-differs.ko.png)

*paramstyle 한 가지가 다르다*
PEP 249는 5가지 paramstyle을 허용합니다.

| paramstyle | 예시 | 사용 driver |
| --- | --- | --- |
| `qmark` | `WHERE id = ?` | sqlite3 |
| `numeric` | `WHERE id = :1` | oracledb |
| `named` | `WHERE id = :id` | sqlite3, oracledb |
| `format` | `WHERE id = %s` | psycopg2(legacy), pymysql |
| `pyformat` | `WHERE id = %(id)s` | psycopg2 |

driver를 import한 후 `module.paramstyle`로 어떤 표기법을 쓰는지 확인할 수 있습니다.

```python
import sqlite3
print(sqlite3.paramstyle)  # 'qmark'
```

이 한 가지 차이만 추상화하면 driver 교체가 한결 수월해집니다. SQLAlchemy 같은 라이브러리는 이 차이를 자동으로 흡수해주는 역할을 합니다 (다음 시리즈에서 다룹니다).

## 5. 같은 코드를 PostgreSQL로 옮기기

위 SQLite 예제를 psycopg(PostgreSQL driver)로 옮기면 거의 변화가 없습니다.

```python
import psycopg

conn = psycopg.connect("dbname=notes user=postgres password=secret")
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        body TEXT
    )
""")

cur.execute(
    "INSERT INTO notes (title, body) VALUES (%s, %s)",  # qmark -> format
    ("Starting DB-API", "First PEP 249 example"),
)
conn.commit()

cur.execute("SELECT id, title FROM notes")
for row in cur.fetchall():
    print(row)

cur.close()
conn.close()
```

바뀐 곳은 `import` 라인, `connect()` 인자, parameter 표기법(`?` -> `%s`) 세 곳뿐입니다. application 로직(execute, fetchall, commit, rollback)은 그대로 작동합니다.

## 6. DB-API가 안 다루는 것

표준이라고 해서 모든 걸 표준화하지는 않습니다. PEP 249가 의도적으로 비워둔 영역이 있습니다.

- **Connection pooling**: driver/library가 알아서 (sqlite3는 단일 connection 권장, psycopg는 `psycopg_pool` 별도)
- **Async API**: PEP 249 자체는 sync. async는 `aiosqlite`, `asyncpg`, `aiomysql`로 별도
- **ORM 기능**: SQLAlchemy, Django ORM, Tortoise ORM이 별도 추상화
- **Schema migration**: Alembic, Django migrations가 별도
- **Server-side cursor 세부사항**: 일부만 표준화, 대부분 driver 확장

이 빈 곳을 채우는 것이 SQLAlchemy, Alembic, FastAPI + databases 같은 상위 라이브러리의 존재 이유입니다.

## 흔히 놓치는 함정 다섯 가지

### 1. autocommit이 driver마다 다름

PEP 249는 명시적 transaction을 가정합니다. SQLite는 default가 "암묵적 transaction begin", PostgreSQL/MySQL은 "default autocommit OFF". 같은 코드라도 `conn.commit()`을 빠뜨리면 driver별로 결과가 다릅니다.

### 2. cursor를 닫지 않음

`cur.close()`를 호출하지 않아도 GC로 정리되지만, server-side cursor를 쓰는 PostgreSQL 같은 환경에서는 connection leak처럼 보일 수 있습니다. `with conn.cursor() as cur:` 패턴(driver가 지원하면)을 쓰는 습관이 안전합니다.

### 3. fetchall()을 큰 결과에 사용

`fetchall()`은 모든 row를 메모리에 올립니다. 100만 row면 OOM. 큰 결과는 `fetchmany(size=1000)`나 cursor 자체의 iterator를 쓰세요.

```python
cur.execute("SELECT * FROM big_table")
for row in cur:  # streaming iteration
    process(row)
```

### 4. execute()를 string concatenation으로 만듦

```python
# 절대 이렇게 하지 마세요 — SQL 인젝션
cur.execute(f"SELECT * FROM users WHERE name = '{name}'")
```

반드시 parameter binding을 사용해야 합니다. 4편에서 자세히 다룹니다.

### 5. 같은 connection을 여러 thread에서 공유

`threadsafety=1`인 driver는 connection을 thread간 공유 불가입니다. sqlite3는 default가 `check_same_thread=True`라 다른 thread에서 쓰면 에러. multi-threaded app에서는 thread당 connection을 만들거나 connection pool을 씁니다.

## 체크리스트

- [ ] sqlite3로 connect → cursor → execute → fetch → close 사이클을 한 번 돌렸다.
- [ ] 같은 코드를 PostgreSQL(psycopg) 드라이버로 옮길 때 무엇이 달라지는지 확인했다.
- [ ] paramstyle 차이를 한 줄로 설명할 수 있다.
- [ ] DB-API가 제공하지 않는 기능(connection pool, ORM, migration)을 구분할 수 있다.

<!-- a-grade-example:end -->

## 심화 앵커: 표준화가 운영에 주는 직접 효과

PEP 249의 핵심 가치는 문법 통일보다 운영 절차 통일에 있습니다. `connect()`, `cursor()`, `execute()`, `commit()`, `rollback()` 경계가 고정되면 driver가 달라도 장애 대응 문서를 재사용할 수 있습니다.

```python
# sqlite3
import sqlite3
conn = sqlite3.connect("app.db")
cur = conn.cursor()
cur.execute("SELECT 1")
cur.close()
conn.close()

# psycopg2
import psycopg2
conn = psycopg2.connect("dbname=app user=postgres password=secret")
cur = conn.cursor()
cur.execute("SELECT 1")
cur.close()
conn.close()
```

```text
Connection lifecycle
open -> cursor acquire -> execute/fetch -> commit/rollback -> cursor close -> connection close
```

운영 점검에서는 다음 세 가지를 함께 기록해야 합니다.

- 같은 쿼리 세트를 sqlite3/psycopg2에서 실행했을 때 결과 row 수와 타입
- `OperationalError` 발생 시 재시도 성공률과 평균 지연 시간
- `IntegrityError` 발생 시 사용자 응답 정책(재시도 금지) 일관성

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

### 짧은 운영 참고

실서비스에서는 SQL 실행 자체보다 경계 관리가 더 자주 문제를 만듭니다. connection 생성과 종료, commit/rollback 분기를 로그와 테스트로 고정하면 장애 대응 시간이 짧아집니다.

## 정리

- DB-API 2.0(PEP 249)은 Python 데이터베이스 driver가 따르는 최소 공통 계약입니다.
- `connect → cursor → execute → fetch → commit → close` 흐름은 sqlite3, psycopg, pymysql에서 거의 같습니다.
- driver 간 가장 눈에 띄는 차이는 `paramstyle`이며, 나머지 애플리케이션 로직은 대부분 유지됩니다.
- DB-API는 pooling, async, ORM, migration 같은 상위 문제를 일부러 비워 두었습니다.
- autocommit, cursor 정리, `fetchall()` 메모리 사용, SQL injection, thread safety가 가장 먼저 부딪히는 함정입니다.

다음 글에서는 connection과 cursor의 lifecycle을 더 깊이 들여다보고, context manager로 안전하게 다루는 패턴을 정리합니다.

<!-- a-grade-example:begin -->

## 처음 질문으로 돌아가기

- **PEP 249 이전에는 Python의 데이터베이스 접근 코드가 왜 그렇게 제각각이었을까요?**
  - 본문의 기준은 왜 DB-API 2.0인가 - PEP 249가 푼 문제를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **DB-API 2.0은 정확히 어떤 다섯 가지를 표준화했을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **driver마다 `paramstyle`이 다른데도 왜 애플리케이션 코드는 대부분 그대로 옮겨질까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **Python DB-API 101 (1/10): 왜 DB-API 2.0인가 - PEP 249가 푼 문제 (현재 글)**
- Python DB-API 101 (2/10): Connection과 Cursor Lifecycle (예정)
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

- [PEP 249 - Python Database API Specification v2.0](https://peps.python.org/pep-0249/)
- [Python sqlite3 module documentation](https://docs.python.org/3/library/sqlite3.html)
- [SQLite official documentation](https://www.sqlite.org/docs.html)
- [psycopg 3 documentation - DB-API 2.0 compliance](https://www.psycopg.org/psycopg3/docs/)

### 관련 시리즈

- [SQLAlchemy 101](../../sqlalchemy-101/ko/01-sqlalchemy-2x-engine-connection.md) — 이 시리즈가 다루는 DB-API를 한 단계 위에서 추상화하는 ORM·Core 계층을 다룹니다. SQLAlchemy 사용 중 connection 동작이나 SQL 실행 단계가 의심스러울 때 이 시리즈로 한 단계 내려가 디버깅하기를 권장합니다.

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/python-dbapi-101/ko)

Tags: Python, DB-API, PEP 249, Database
