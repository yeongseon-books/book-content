---
title: SQLAlchemy 2.x 시작하기 - Engine과 Connection의 본질
series: sqlalchemy-101
episode: 1
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
- Python
- SQLAlchemy
- Engine
- Connection
- SQLite
- DBAPI
last_reviewed: '2026-05-03'
seo_description: SQLAlchemy의 Engine은 "데이터베이스와 통신할 수 있는 능력 그 자체를 객체화한 것"입니다.
---

# SQLAlchemy 2.x 시작하기 - Engine과 Connection의 본질

> SQLAlchemy 101 시리즈 (1/10)

---

`pip install sqlalchemy`로 SQLAlchemy를 설치하고 처음 코드를 적을 때 가장 자주 마주치는 오해는 "SQLAlchemy가 `sqlite3` 같은 표준 드라이버를 대체한다"는 생각입니다. 사실은 정반대입니다. SQLAlchemy는 PEP 249 DB-API 드라이버 **위에 얹히는** 라이브러리이고, 우리가 `create_engine("sqlite:///app.db")`라고 적는 순간 내부에서는 여전히 `import sqlite3`가 일어나고 있습니다. 이 한 가지 사실만 정확히 잡고 가도 SQLAlchemy의 거의 모든 동작이 자연스럽게 설명됩니다.

이 시리즈는 SQLAlchemy 2.x를 SQLite 기준으로 처음부터 끝까지 따라갑니다. 첫 글은 가장 아래 계층, 즉 `Engine`과 `Connection`이 무엇이고 왜 이런 모양으로 설계되었는지를 다룹니다. ORM이나 Session은 다음 글들에서 본격적으로 등장하므로, 일단 여기서는 "SQL 한 줄을 어떻게 SQLite 파일까지 보내는가"라는 구체적인 질문에 답합니다.

![SQLAlchemy 2.x 시작하기 - Engine과 Connection의 본질](../../../assets/sqlalchemy-101/01/01-01-getting-started-with-sqlalchemy-2-x-engi.ko.png)

*SQLAlchemy 2.x 시작하기 - Engine과 Connection의 본질*
## 핵심 질문

Engine과 Connection의 본질을 이해하면 어떤 DB 연결 사고를 예방할 수 있을까요?

이 글은 그 질문에 답하기 위해 Engine과 Connection의 핵심 결정과 운영 함정을 살펴봅니다.

## 이 글에서 다룰 문제

![핵심 개념](../../../assets/sqlalchemy-101/01/01-02-why-this-matters.ko.png)

*핵심 개념*
많은 SQLAlchemy 입문 자료가 ORM의 `Base = declarative_base()`부터 시작합니다. 그 결과 ORM이 아닌 곳에서 문제가 발생했을 때, 예컨대 connection이 끊어졌거나 transaction이 의도와 다르게 commit되었을 때, 어디를 들여다봐야 할지 감을 잡기 어렵습니다. Engine과 Connection은 ORM의 Session을 받쳐주는 토대이고, Session 내부에서 문제가 생기면 결국 Connection 수준에서 디버깅해야 합니다.

또한 production 환경에서 자주 등장하는 이슈, 예를 들면 SQLite의 `database is locked` 오류, `Lost connection` 재시도, connection pool exhaustion, autocommit 모드 차이 같은 문제는 모두 Engine 설정에서 시작합니다. 이 토대를 정확히 이해하지 못하면 ORM을 쓰면서도 `pool_size`, `pool_recycle`, `connect_args` 같은 옵션을 추측에 의존해 설정하게 됩니다.

마지막으로 1.x와 2.x의 차이는 단순한 syntax 변화가 아니라 사용 모델 자체의 변화입니다. 2.x는 "execute는 Connection에 속하고, 모든 Connection 사용은 transaction 안에서 일어나야 한다"는 원칙을 강제합니다. 이 원칙을 모르면 2.x 스타일로 적은 코드가 1.x 사고방식 때문에 미묘하게 잘못 동작합니다.

## Mental Model

![Mental model](../../../assets/sqlalchemy-101/01/01-03-mental-model.ko.png)

*Mental model*
SQLAlchemy의 Engine은 "데이터베이스와 통신할 수 있는 능력 그 자체를 객체화한 것"입니다. Connection 객체가 실제 통신 채널이고, Engine은 그 채널을 만들 수 있는 권한과 설정을 들고 있는 factory입니다.

> Engine은 connection이 아니다. Engine은 connection을 **만들 수 있는** 객체이며, dialect와 pool을 들고 있는 설계도이다. 실제로 SQL이 흐르는 통로는 Connection이고, Connection은 항상 transaction 컨텍스트 안에서 살아간다.

이 모델을 그림으로 그리면 다음과 같습니다.

```text
Application code
      │
      ▼
   Engine ── (Dialect: sqlite) ── (URL: sqlite:///app.db)
      │
      ├── ConnectionPool (lazy)
      │       └── DBAPI connection (sqlite3.Connection) × N
      │
      └── connect() / begin()
              │
              ▼
          Connection (SQLAlchemy wrapper)
              │
              ▼
          execute(text("SELECT 1"))
              │
              ▼
          DBAPI cursor → SQLite 파일
```

핵심은 다음 세 가지입니다. 첫째, Engine은 dialect(어떤 DB 종류인지)와 URL(어디에 있는지), 그리고 pool(connection을 몇 개나 어떻게 재사용할지)을 묶은 단위입니다. 둘째, Connection은 PEP 249 DBAPI connection을 한 겹 감싼 객체이며, 모든 SQL 실행은 Connection의 메서드로 이루어집니다. 셋째, 2.x에서는 transaction이 명시적입니다. `connect()`만 쓰면 transaction이 자동으로 시작되지만 명시적으로 commit해야 하고, `begin()`을 쓰면 블록을 빠져나갈 때 자동으로 commit/rollback됩니다.

## 핵심 개념

![핵심 개념](../../../assets/sqlalchemy-101/01/01-04-core-concepts.ko.png)

*핵심 개념*
### Core와 ORM의 두 계층

SQLAlchemy는 두 개의 큰 계층으로 이루어져 있습니다. **Core**는 SQL을 Python 표현식으로 빌드하고 Engine/Connection으로 실행하는 계층입니다. **ORM**은 Core 위에 매핑된 Python class와 Session을 얹어서 객체-관계 매핑을 제공합니다. 둘은 분리되어 있지만 상호 보완적이고, ORM 안에서도 필요하면 언제든 Core로 내려올 수 있습니다.

이 시리즈의 1~3편은 Core를 다루고, 4편부터 ORM을 본격적으로 다룹니다. ORM만 쓰는 사람도 Core를 알아야 production 디버깅이 가능합니다.

### Engine은 lazy factory다

`create_engine()`은 호출 시점에 데이터베이스에 연결하지 않습니다. 단지 dialect를 import하고 URL을 파싱하고 pool을 준비할 뿐입니다. 첫 connect 시도가 일어날 때 비로소 SQLite 파일이 열리거나 생성됩니다.

```python
from sqlalchemy import create_engine

engine = create_engine("sqlite:///app.db", echo=True)
# 이 시점에는 아직 app.db 파일이 열리지 않았다.

with engine.connect() as conn:
    # 여기서 비로소 sqlite3.connect("app.db")가 호출된다.
    ...
```

이 lazy 동작 덕분에 application 시작 시 `engine`을 module 변수로 만들어두는 것이 안전합니다. 실제 file lock이나 network connection이 application import 시점에 발생하지 않기 때문입니다.

### URL과 dialect

SQLAlchemy URL은 `dialect+driver://user:pass@host:port/database` 형식이지만 SQLite는 host와 user 부분이 비어 있습니다.

| URL | 의미 |
| --- | --- |
| `sqlite:///app.db` | 현재 작업 디렉터리 기준 상대 경로 |
| `sqlite:////var/data/app.db` | 절대 경로 (`///`에 추가로 `/`가 붙은 형태) |
| `sqlite://` | in-memory DB (`:memory:`와 동일) |
| `sqlite:///:memory:` | 위와 같은 in-memory DB |

`echo=True`는 SQLAlchemy가 실행하는 모든 SQL을 stderr에 로깅합니다. 학습 단계에서는 거의 항상 켜놓는 편이 좋습니다.

### Connection vs Session

| 구분 | Connection (Core) | Session (ORM) |
| --- | --- | --- |
| 위치 | Core | ORM |
| 들고 있는 것 | DBAPI connection 한 개 | identity map, unit of work, 그리고 Connection |
| 다루는 단위 | row, Result | mapped object |
| transaction | 명시적 (`begin()`) | 명시적 (`begin()` 또는 `commit()`) |

이 시리즈에서는 일단 Connection만 다루고, Session은 5편에서 본격적으로 등장합니다.

### 2.x style: 명시적 transaction

1.x에서 흔하던 `engine.execute("SELECT 1")` 호출은 2.x에서 제거되었습니다. 2.x에서는 SQL 실행이 반드시 Connection을 통해야 하고, Connection은 transaction 안에서 살아갑니다. 2.x style을 정리하면 다음 세 가지 패턴이 핵심입니다.

```python
# 패턴 A: 읽기 (commit 필요 없음)
with engine.connect() as conn:
    rows = conn.execute(text("SELECT * FROM users")).all()

# 패턴 B: 쓰기 (명시적 commit)
with engine.connect() as conn:
    conn.execute(text("INSERT INTO users(name) VALUES (:n)"), {"n": "Alice"})
    conn.commit()

# 패턴 C: 자동 commit/rollback (가장 권장)
with engine.begin() as conn:
    conn.execute(text("INSERT INTO users(name) VALUES (:n)"), {"n": "Bob"})
# 블록을 정상 종료하면 commit, 예외 발생 시 rollback
```

쓰기가 섞여 있을 때는 패턴 C(`engine.begin()`)를 기본으로 쓰고, 순수 읽기일 때만 패턴 A(`engine.connect()`)를 쓰는 것을 권장합니다.

## Before-After

### Before: 1.x style + 직접 sqlite3

```python
# 1.x 또는 그 이전 사고방식: 명시성 부족, transaction 모호
import sqlite3
conn = sqlite3.connect("app.db")
cur = conn.cursor()
cur.execute("INSERT INTO users(name) VALUES (?)", ("Alice",))
conn.commit()
conn.close()

# 또는 SQLAlchemy 1.x:
from sqlalchemy import create_engine
engine = create_engine("sqlite:///app.db")
engine.execute("INSERT INTO users(name) VALUES ('Alice')")  # 2.x에서는 사라짐
```

문제: connection lifecycle을 사람이 관리해야 하고, transaction 경계가 모호하며, parameter binding 형식이 driver마다 다릅니다(`?`, `%s`, `:name` 등).

### After: 2.x style + 명시적 transaction

```python
from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///app.db", echo=False, future=True)

def add_user(name: str) -> None:
    with engine.begin() as conn:  # 자동 commit/rollback
        conn.execute(
            text("INSERT INTO users(name) VALUES (:name)"),
            {"name": name},
        )
```

이제 다음이 보장됩니다.

- Connection은 블록을 벗어나면 자동으로 pool에 반환됩니다.
- 예외가 발생하면 자동으로 rollback됩니다.
- parameter binding은 dialect와 무관하게 항상 `:name` named style을 씁니다.
- DBAPI는 여전히 `sqlite3`이지만 더 이상 직접 import할 일이 없습니다.

## 단계별 실습

![단계별 실습](../../../assets/sqlalchemy-101/01/01-05-step-by-step-practice.ko.png)

*단계별 실습*
이 절은 빈 디렉터리에서 시작해서 첫 번째 SQLAlchemy 2.x 코드를 돌려보는 과정을 따라갑니다.

### 1단계: 환경 준비

```bash
mkdir sqlalchemy-101-ep1 && cd sqlalchemy-101-ep1
python3 -m venv .venv && source .venv/bin/activate
pip install "sqlalchemy>=2.0"
python -c "import sqlalchemy; print(sqlalchemy.__version__)"
```

2.x 버전이 출력되어야 합니다. 1.4가 보인다면 `pip install --upgrade "sqlalchemy>=2.0"`를 실행합니다.

### 2단계: Engine 생성과 첫 연결

`step2.py`:

```python
from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///app.db", echo=True)

with engine.connect() as conn:
    result = conn.execute(text("SELECT sqlite_version()"))
    print(result.scalar())
```

실행하면 SQLAlchemy가 출력하는 SQL 로그와 함께 SQLite 버전이 출력됩니다. 이 시점에 `app.db` 파일이 디스크에 생성됩니다.

### 3단계: 테이블 만들기와 데이터 삽입

`step3.py`:

```python
from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///app.db", echo=False)

with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE
        )
    """))
    conn.execute(
        text("INSERT INTO users(name, email) VALUES (:n, :e)"),
        [
            {"n": "Alice", "e": "alice@example.com"},
            {"n": "Bob", "e": "bob@example.com"},
        ],
    )
```

`execute(stmt, list_of_dicts)` 형식은 `executemany`처럼 동작합니다. dialect와 무관하게 named binding(`:n`, `:e`)을 그대로 씁니다.

### 4단계: 결과 다루기

`step4.py`:

```python
from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///app.db")

with engine.connect() as conn:
    result = conn.execute(text("SELECT id, name, email FROM users ORDER BY id"))

    for row in result:
        # row는 named tuple-like
        print(row.id, row.name, row.email)

    # 다시 가져오려면 새 execute 필요 (Result는 한 번만 순회 가능)
    rows = conn.execute(text("SELECT * FROM users")).all()
    print(f"총 {len(rows)}명")
```

### 5단계: SQLite 전용 PRAGMA 적용

SQLite는 기본적으로 foreign key 제약을 강제하지 않습니다. 이 동작을 모든 connection에 자동으로 적용하려면 `connect` 이벤트를 씁니다.

```python
from sqlalchemy import create_engine, event

engine = create_engine("sqlite:///app.db")

@event.listens_for(engine, "connect")
def _enable_fk(dbapi_conn, connection_record):
    cur = dbapi_conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    cur.close()
```

이 패턴은 dialect-specific 설정을 application 전체에 일관되게 적용하는 표준 방법입니다.

## 자주 하는 실수

**1. `engine = create_engine(...)`을 함수 안에서 매번 호출하기.** Engine은 application 전역에 하나만 만들어 module-level 변수로 공유해야 합니다. 매번 만들면 connection pool이 매번 새로 만들어져서 의미가 사라집니다.

**2. `with engine.connect()` 안에서 commit을 잊기.** 2.x에서 `connect()`는 transaction을 자동으로 시작하지만 자동으로 commit하지 않습니다. INSERT/UPDATE를 했는데 데이터가 사라진 것 같다면 거의 항상 이 문제입니다. 쓰기가 섞이면 `begin()`을 쓰는 것이 안전합니다.

**3. Connection을 함수 인자로 넘기지 않고 전역으로 들고 있기.** Connection은 짧게 살아야 하는 자원입니다. context manager 안에서만 사용하고 빠져나오면 pool에 반환합니다.

**4. raw SQL을 string formatting으로 만들기.** `f"SELECT * FROM users WHERE name = '{name}'"` 같은 코드는 SQL injection을 만듭니다. 항상 `text("... WHERE name = :name")`와 `{"name": name}` 조합을 씁니다.

**5. SQLite 절대 경로에서 슬래시 개수 헷갈리기.** `sqlite:///` 다음의 경로는 상대 경로이고, 절대 경로는 슬래시가 하나 더 붙어 `sqlite:////var/data/app.db`가 됩니다. 이걸 헷갈리면 의도와 다른 곳에 파일이 생깁니다.

**6. `echo=True`를 production에 그대로 두기.** 학습용 옵션이지 production 옵션이 아닙니다. production에서는 SQLAlchemy logger를 직접 다루는 편이 낫습니다.

## 실무 적용

실무에서 SQLAlchemy Engine은 보통 application 전역 single instance로 관리합니다. FastAPI나 Flask 같은 framework에서는 다음 패턴이 일반적입니다.

```python
# db.py
from sqlalchemy import create_engine, event
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

@event.listens_for(engine, "connect")
def _sqlite_pragmas(dbapi_conn, _):
    if DATABASE_URL.startswith("sqlite"):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON")
        cur.execute("PRAGMA journal_mode = WAL")
        cur.close()
```

여기에는 production에서 의미 있는 옵션이 몇 가지 더 들어 있습니다. `pool_pre_ping=True`는 pool에서 꺼낸 connection이 살아 있는지 가벼운 쿼리로 확인해서 stale connection을 자동으로 폐기합니다. `check_same_thread=False`는 SQLite에서 multi-thread 환경(예: FastAPI worker)에서 connection 공유를 허용합니다(자세한 내용은 8편에서 다룹니다). `journal_mode = WAL`은 concurrent reader/writer 처리량을 크게 높여줍니다.

테스트에서는 `sqlite:///:memory:`나 임시 파일을 쓰면 격리된 fixture를 만들 수 있습니다.

```python
import pytest
from sqlalchemy import create_engine, text

@pytest.fixture
def engine():
    eng = create_engine("sqlite:///:memory:")
    with eng.begin() as conn:
        conn.execute(text("CREATE TABLE t(id INTEGER PRIMARY KEY)"))
    yield eng
    eng.dispose()
```

`engine.dispose()`는 pool에 들어 있는 모든 connection을 닫습니다. 테스트 종료 시 leak을 막는 표준 정리 코드입니다.

## 체크리스트

- [ ] SQLAlchemy 2.x를 설치했고 `sqlalchemy.__version__`이 2.0 이상인 것을 확인했다
- [ ] `create_engine()`이 lazy factory라는 것을 이해했다
- [ ] `engine.connect()`와 `engine.begin()`의 차이를 한 줄로 설명할 수 있다
- [ ] 2.x에서 `engine.execute(...)`가 사라진 이유를 안다
- [ ] `text()`와 named parameter binding을 사용했다
- [ ] SQLite URL의 슬래시 규칙(`sqlite:///` 상대 vs `sqlite:////` 절대)을 안다
- [ ] `event.listens_for(engine, "connect")`로 PRAGMA를 적용해 봤다
- [ ] application code에서 Engine을 module-level 단일 instance로 관리한다

## 정리·다음 글

이 글에서 우리는 SQLAlchemy를 가장 아래 계층부터 보았습니다. Engine은 dialect와 pool을 들고 있는 lazy factory이고, Connection은 PEP 249 DBAPI connection을 감싼 짧게 사는 자원이며, 2.x style은 모든 실행을 명시적인 transaction 안에서 다룹니다. SQLite에 한정하면 URL 표기, in-memory DB, foreign key PRAGMA 같은 dialect-specific 디테일이 추가로 필요합니다.

다음 글에서는 한 단계 위로 올라가 **MetaData, Table, Column, type system**을 다룹니다. raw SQL 문자열 대신 Python 객체로 schema를 선언하는 Core의 진짜 매력이 본격적으로 등장합니다. ORM 이전 단계인 Core SQL expression이 어떤 모양인지를 이해하면, 4편 이후의 ORM이 훨씬 쉽게 읽힙니다.

<!-- toc:begin -->
## 시리즈 목차

- **SQLAlchemy 2.x 시작하기 - Engine과 Connection의 본질 (현재 글)**
- SQLAlchemy Core - MetaData, Table, Column으로 schema를 Python 객체로 만들기 (예정)
- SQLAlchemy Core - select·insert·update·delete를 2.x style로 다루기 (예정)
- ORM 기초: DeclarativeBase와 mapped_column으로 모델 정의하기 (예정)
- Session 깊이 보기: Unit of Work와 Identity Map의 동작 원리 (예정)
- ORM Relationships: relationship과 back_populates로 양방향 탐색 안전하게 잇기 (예정)
- 로딩 전략과 N+1 문제: lazy/joined/selectin을 언제 골라야 하는가 (예정)
- 이벤트, hybrid_property, 그리고 커스텀 타입 (예정)
- 비동기 SQLAlchemy: aiosqlite와 AsyncSession (예정)
- production 패턴: 풀, 관측, 마이그레이션, 배포 (예정)

<!-- toc:end -->

## 참고 자료

- [SQLAlchemy 2.x Tutorial - Establishing Connectivity](https://docs.sqlalchemy.org/en/20/tutorial/engine.html)
- [SQLAlchemy 2.x - Working with Engines and Connections](https://docs.sqlalchemy.org/en/20/core/connections.html)
- [SQLAlchemy 2.0 Migration Guide](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html)
- [SQLite URL forms](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#connect-strings)
- [PEP 249 - Python Database API Specification 2.0](https://peps.python.org/pep-0249/)

Tags: Python, SQLAlchemy, ORM, Database
