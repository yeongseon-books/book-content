---
title: "바이브코딩을 위한 SQLAlchemy 기초 (1/10): Engine과 Connection"
series: sqlalchemy-101
episode: 1
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - SQLAlchemy
  - Python
  - Database
  - Engine
---

# 바이브코딩을 위한 SQLAlchemy 기초 (1/10): Engine과 Connection

이 글은 "바이브코딩을 위한 SQLAlchemy 기초" 시리즈의 첫 번째 글입니다.

---

바이브코딩에서 AI는 SQLAlchemy 코드를 빠르게 만들어 줍니다. ORM 모델, 쿼리, 세션 코드까지 한 번에 생성해 주는데, 이 편리함 때문에 가장 밑바닥인 Engine과 Connection의 역할을 이해하지 못한 채 코드가 배포됩니다. 코드가 돌아가는 이유보다 결과만 먼저 보게 되는 것입니다.

그러다 `database is locked`, `Lost connection`, `ROLLBACK`이 로그에 찍히는 순간 어디서 시작해야 할지 막막해집니다. Pool 사이즈 옵션을 추측에 의존해 바꾸거나, `connect()` 안에서 `commit()`을 잊어서 INSERT가 사라지거나, `engine.execute()`가 2.x에서 왜 없어졌는지 모른 채 1.x 코드를 복붙합니다.

SQLAlchemy는 `sqlite3` 같은 드라이버를 대체하는 게 아닙니다. PEP 249 DB-API 드라이버 위에 올라가는 계층입니다. Engine은 "데이터베이스와 통신할 수 있는 능력을 객체화한 것"이고, Connection은 실제 SQL이 흐르는 통로입니다. 이 구조를 이해하면 Session, ORM, connection pool이 같은 선에서 읽힙니다.

> **핵심 인사이트:** SQLAlchemy 2.x에서는 모든 SQL 실행이 Connection을 통해야 하고, Connection은 항상 transaction 컨텍스트 안에 있어야 합니다. 쓰기가 있으면 `engine.begin()`으로, 읽기만이면 `engine.connect()`로, 그리고 transaction 경계는 항상 명시적으로 다뤄야 합니다.

## 이 글에서 다룰 문제

- `Engine`은 정확히 무엇이고, `Connection`과 어떻게 역할을 나눌까요?
- SQLAlchemy 2.x가 transaction을 더 명시적으로 다루는 이유는 무엇인가요?
- `connect()`와 `begin()`은 언제 구분해서 써야 할까요?
- AI가 만든 SQLAlchemy 코드에서 Engine 관련으로 확인할 것은 무엇인가요?
- `pool_pre_ping`, `pool_recycle` 같은 옵션은 언제 필요할까요?

## Engine과 Connection 핵심 패턴

```python
from sqlalchemy import create_engine, text

# Engine: lazy factory - create_engine 호출 시 DB에 연결하지 않음
engine = create_engine(
    "sqlite:///app.db",
    echo=False,
    pool_pre_ping=True,   # stale connection 자동 감지
    pool_recycle=1800,    # 30분 이상 된 connection 재생성
)

# 패턴 A: 읽기 (commit 불필요)
with engine.connect() as conn:
    rows = conn.execute(text("SELECT * FROM users")).all()

# 패턴 B: 쓰기 (명시적 commit)
with engine.connect() as conn:
    conn.execute(text("INSERT INTO users(name) VALUES (:name)"), {"name": "Alice"})
    conn.commit()

# 패턴 C: 자동 commit/rollback (권장)
with engine.begin() as conn:
    conn.execute(text("INSERT INTO users(name) VALUES (:name)"), {"name": "Bob"})
# 블록 정상 종료 → commit, 예외 발생 → rollback 자동
```

```python
# SQLite 전용 설정: PRAGMA를 모든 connection에 자동 적용
from sqlalchemy import event

@event.listens_for(engine, "connect")
def _sqlite_pragmas(dbapi_conn, _):
    cur = dbapi_conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    cur.execute("PRAGMA journal_mode = WAL")  # concurrent read/write 향상
    cur.close()

# connection pool 상태 확인 (부하 테스트 후 체크포인트)
with engine.begin() as conn:
    conn.execute(text("SELECT 1"))
print(engine.pool.status())
# 예: Pool size: 5, Checked out: 0, Overflow: -4
```

```python
# 테스트 fixture: in-memory DB로 격리
import pytest
from sqlalchemy import create_engine, text

@pytest.fixture
def engine():
    eng = create_engine("sqlite:///:memory:")
    with eng.begin() as conn:
        conn.execute(text("CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT)"))
    yield eng
    eng.dispose()  # pool의 모든 connection 종료 (leak 방지)
```

## 변경 전후 비교

**Before: 1.x 스타일 + transaction 모호**
```text
- engine.execute("INSERT ...") 직접 호출 (2.x에서 제거됨)
- connection lifecycle을 사람이 수동 관리
- commit을 잊으면 데이터가 조용히 사라짐
- f-string으로 SQL 조합 → SQL injection 위험
- engine을 함수 안에서 매번 생성 → pool 의미 없음
```

**After: 2.x 스타일 + 명시적 transaction**
```text
- engine.begin() 컨텍스트에서 자동 commit/rollback
- engine은 module-level 단일 인스턴스
- named parameter binding으로 SQL injection 방지
- pool_pre_ping으로 stale connection 자동 처리
- echo=True로 실제 SQL 확인 (학습/디버깅 시)
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| `engine.execute()` 사용 | 2.x에서 제거됨 | `conn.execute()` 사용 |
| `connect()` 후 commit 누락 | INSERT가 rollback되어 사라짐 | 쓰기는 `begin()` 사용 |
| engine을 함수 안에서 매번 생성 | pool이 매번 새로 만들어져 의미 없음 | module-level 단일 인스턴스 |
| f-string SQL 조합 | SQL injection 위험 | `text("... :name")` + dict binding |
| `echo=True`를 production에 방치 | 민감한 SQL이 로그에 노출 | 환경변수로 제어, production에서 off |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"SQLAlchemy 2.x로 SQLite 연결 코드를 만들어줘.
engine은 module-level singleton, pool_pre_ping=True 포함,
SQLite foreign_keys PRAGMA 자동 적용,
쓰기는 engine.begin(), 읽기는 engine.connect() 패턴으로"

# AI 결과물 검증 체크포인트:
# - engine.execute() 대신 conn.execute()를 사용하는가?
# - 쓰기 작업이 engine.begin() 블록 안에 있는가?
# - engine이 module-level 단일 인스턴스인가?
# - SQL parameter가 f-string이 아닌 named binding인가?
# - pool_pre_ping이 설정되어 있는가?
```

## 운영 체크리스트

- [ ] `create_engine()`이 module-level 단일 인스턴스로 관리된다
- [ ] 쓰기 작업은 `engine.begin()`, 읽기는 `engine.connect()`로 구분한다
- [ ] SQL parameter에 f-string 대신 named binding을 사용한다
- [ ] `pool_pre_ping=True`로 stale connection을 자동 처리한다
- [ ] SQLite 환경에서 `PRAGMA foreign_keys = ON`이 connect event로 적용된다

## 처음 질문으로 돌아가기

- **Engine과 Connection의 역할 차이는?** Engine은 dialect와 pool을 들고 있는 lazy factory입니다. `create_engine()` 호출 시점에 DB에 연결하지 않습니다. Connection은 실제 SQL이 흐르는 통로이며, transaction 안에서 살아갑니다.
- **`connect()`와 `begin()`의 차이는?** `connect()`는 transaction을 자동으로 시작하지만 자동으로 commit하지 않습니다. `begin()`은 블록을 정상 종료하면 자동 commit, 예외 발생 시 자동 rollback합니다. 쓰기가 섞이면 `begin()`이 안전합니다.
- **2.x에서 transaction이 명시적인 이유는?** "모든 SQL 실행은 Connection을 통해야 하고, Connection은 transaction 안에서 살아간다"는 원칙을 강제합니다. 1.x의 암묵적 동작이 만든 버그(commit 누락, stale transaction)를 방지합니다.

## 정리

바이브코딩에서 AI가 만든 SQLAlchemy 코드에서 `engine.execute()`, f-string SQL, commit 누락, engine 반복 생성을 반드시 확인하세요. Engine과 Connection의 역할을 이해하면 Session과 ORM의 동작도 같은 선에서 읽힙니다. 다음 글에서는 MetaData, Table, Column으로 스키마를 Python 객체로 만드는 방법을 다룹니다.

## 참고 자료

- [SQLAlchemy 2.x - Establishing Connectivity](https://docs.sqlalchemy.org/en/20/tutorial/engine.html)
- [SQLAlchemy 2.0 Migration Guide](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/sqlalchemy-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- **바이브코딩을 위한 SQLAlchemy 기초 (1/10): Engine과 Connection (현재 글)**
- 바이브코딩을 위한 SQLAlchemy 기초 (2/10): MetaData와 Schema
- 바이브코딩을 위한 SQLAlchemy 기초 (3/10): Core CRUD
- 바이브코딩을 위한 SQLAlchemy 기초 (4/10): ORM 모델 정의
- 바이브코딩을 위한 SQLAlchemy 기초 (5/10): Session과 Unit of Work
- 바이브코딩을 위한 SQLAlchemy 기초 (6/10): 관계 매핑
- 바이브코딩을 위한 SQLAlchemy 기초 (7/10): 로딩 전략과 N+1
- 바이브코딩을 위한 SQLAlchemy 기초 (8/10): 이벤트와 확장점
- 바이브코딩을 위한 SQLAlchemy 기초 (9/10): 비동기 SQLAlchemy
- 바이브코딩을 위한 SQLAlchemy 기초 (10/10): 프로덕션 패턴
<!-- toc:end -->

Tags: 바이브코딩, SQLAlchemy, Python, Database, Engine
