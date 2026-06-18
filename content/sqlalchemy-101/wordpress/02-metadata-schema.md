---
title: "바이브코딩을 위한 SQLAlchemy 기초 (2/10): MetaData와 Schema"
series: sqlalchemy-101
episode: 2
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - SQLAlchemy
  - Python
  - Database
  - Schema
---

# 바이브코딩을 위한 SQLAlchemy 기초 (2/10): MetaData와 Schema

이 글은 "바이브코딩을 위한 SQLAlchemy 기초" 시리즈의 두 번째 글입니다.

---

바이브코딩에서 AI는 `CREATE TABLE` SQL과 SQLAlchemy 모델 코드를 빠르게 만들어 줍니다. 그런데 AI가 만든 코드에서 테이블 스키마는 문자열 SQL로만 관리되는 경우가 많습니다. 컬럼 이름 하나를 바꿨는데 런타임에서야 `no such column`이 터지고, IDE는 자동완성조차 해주지 않습니다.

더 심각한 문제는 AI가 생성한 코드에서 `naming_convention` 없이 MetaData를 쓰거나, `nullable=True`를 기본값으로 방치하거나, SQLite에서 `ON DELETE CASCADE`를 적었지만 `PRAGMA foreign_keys = ON`을 켜지 않는 패턴입니다. 스키마 정의 시점에는 오류가 없지만, 운영에서 고아 데이터가 남거나 마이그레이션 도구가 제약 조건을 DROP하지 못하는 상황이 생깁니다.

SQLAlchemy Core의 `MetaData`, `Table`, `Column`은 스키마를 Python 객체로 만드는 도구입니다. 컬럼 이름 typo가 런타임이 아닌 AttributeError로 즉시 잡히고, 같은 정의가 Alembic의 autogenerate 기준이 됩니다. 문자열 SQL과 Python 객체 스키마의 차이가 운영 안전성의 차이입니다.

> **핵심 인사이트:** `MetaData`는 애플리케이션의 스키마 카탈로그입니다. `naming_convention`을 처음부터 설정하면 Alembic이 ALTER TABLE을 안전하게 생성합니다. SQLite에서 `ForeignKey(ondelete="CASCADE")`는 `PRAGMA foreign_keys = ON` 없이는 동작하지 않습니다.

## 이 글에서 다룰 문제

- `MetaData`는 어떤 역할을 하고 왜 스키마 카탈로그라고 부를까요?
- `Table`과 `Column`을 Python 객체로 두면 어떤 실수가 줄어들까요?
- `default`와 `server_default`는 어떻게 다를까요?
- SQLite의 type affinity가 왜 함정이 될 수 있나요?
- AI가 만든 스키마 코드에서 확인해야 할 것은 무엇인가요?

## MetaData와 Schema 핵심 패턴

```python
from sqlalchemy import (
    MetaData, Table, Column, Integer, String, DateTime, Text,
    ForeignKey, UniqueConstraint, Index, create_engine,
)
from datetime import datetime, timezone

# MetaData: 스키마 카탈로그 - naming_convention은 Alembic에서 필수
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(table_name)s_%(column_0_name)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(100), nullable=False),           # nullable 명시 필수
    Column("email", String(255), nullable=False, unique=True),
    Column("created_at", DateTime, nullable=False,
           default=lambda: datetime.now(timezone.utc)),    # Python 측 기본값
)

posts = Table(
    "posts", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer,
           ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("title", String(200), nullable=False),
    Column("body", Text, nullable=False),
    Index("ix_posts_user_id", "user_id"),
)
```

```python
from sqlalchemy import event

engine = create_engine("sqlite:///app.db")

# SQLite foreign key PRAGMA: connect event로 자동 적용
@event.listens_for(engine, "connect")
def _enable_fk(dbapi_conn, _):
    cur = dbapi_conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    cur.close()

# 스키마 생성: idempotent (CREATE TABLE IF NOT EXISTS)
metadata.create_all(engine)

# Reflection: 기존 DB 스키마를 Python 객체로 가져오기
existing = MetaData()
users_r = Table("users", existing, autoload_with=engine)
print([c.name for c in users_r.columns])
```

```python
# default vs server_default 차이
# default: Python이 INSERT 시 채워주는 값
# server_default: DB의 DEFAULT 절 (raw SQL로 INSERT해도 동작)
from sqlalchemy import text

flagged_col_python = Column(
    "flagged", Integer, nullable=False,
    default=0             # SQLAlchemy INSERT 시 Python이 채움
)

flagged_col_server = Column(
    "flagged", Integer, nullable=False,
    server_default=text("0")  # DB 레벨 DEFAULT - raw SQL도 동작
)
# 둘 중 하나만 쓸 것 (동시에 쓰면 어디서 채워졌는지 추적 어려움)
```

## 변경 전후 비교

**Before: 문자열 SQL로만 스키마 관리**
```text
- CREATE TABLE 문자열을 여러 곳에서 관리
- 컬럼 이름 typo가 런타임 OperationalError로 발견됨
- naming_convention 없어 Alembic이 제약 DROP 실패
- ON DELETE CASCADE 적었지만 PRAGMA 없어 silent bug
- nullable 기본값(True)으로 방치 → NULL 데이터 누적
```

**After: MetaData + Table + Column**
```text
- 스키마가 Python 객체로 단일 소스 관리
- users.c.typo_name → AttributeError (즉시 발견)
- naming_convention으로 Alembic ALTER TABLE 안전 생성
- connect event로 PRAGMA foreign_keys = ON 자동 적용
- nullable=False 명시로 의도를 코드로 표현
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| `naming_convention` 없이 시작 | Alembic DROP CONSTRAINT 실패 | 프로젝트 첫날부터 적용 |
| `nullable=True` 기본값 방치 | 의도치 않은 NULL 데이터 누적 | 허용 의도가 없으면 `nullable=False` 명시 |
| SQLite PRAGMA 없이 CASCADE | 부모 삭제해도 자식 행이 남음 | connect event로 `PRAGMA foreign_keys = ON` |
| `default`와 `server_default` 동시 사용 | 어디서 채워졌는지 추적 어려움 | 하나만 선택 |
| MetaData를 함수 안에서 매번 생성 | reflection/migration 도구 혼란 | module-level 단일 인스턴스 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"SQLAlchemy 2.x로 users, posts 테이블 스키마를 만들어줘.
MetaData에 naming_convention 포함,
모든 Column에 nullable 명시,
ForeignKey에 ondelete='CASCADE',
SQLite에서 foreign_keys PRAGMA를 connect event로 자동 적용"

# AI 결과물 검증 체크포인트:
# - MetaData에 naming_convention이 설정되어 있는가?
# - 모든 Column에 nullable이 명시되어 있는가?
# - SQLite ForeignKey와 PRAGMA가 함께 설정되어 있는가?
# - default와 server_default 중 하나만 사용하는가?
# - MetaData가 module-level 단일 인스턴스인가?
```

## 운영 체크리스트

- [ ] `MetaData`에 `naming_convention`이 설정되어 있다
- [ ] 모든 `Column`에 `nullable` 의도가 명시되어 있다
- [ ] `ForeignKey(ondelete=...)`와 `PRAGMA foreign_keys = ON`이 함께 설정된다
- [ ] `default`와 `server_default` 중 하나만 사용한다
- [ ] `MetaData`가 module-level 단일 인스턴스로 관리된다

## 처음 질문으로 돌아가기

- **MetaData의 역할은?** 애플리케이션의 스키마 카탈로그입니다. 모든 Table 정의를 담아 두는 컨테이너이며, `metadata.create_all(engine)`으로 DB에 스키마를 생성하고, Alembic의 `target_metadata`로도 사용됩니다.
- **Python 객체로 스키마를 두면 어떤 실수가 줄어드는가?** 컬럼 이름 typo가 런타임이 아닌 AttributeError로 즉시 잡히고, IDE 자동완성이 가능합니다. 같은 정의를 select/insert/update에 재사용하므로 스키마와 쿼리가 어긋나지 않습니다.
- **SQLite의 type affinity 함정은?** `String(100)`이라고 적어도 SQLite는 길이를 강제하지 않습니다. 길이 제한이 필요하면 애플리케이션 측에서 검증하거나 `CHECK` 제약을 명시해야 합니다.

## 정리

바이브코딩에서 AI가 만든 스키마 코드에서 `naming_convention`, `nullable`, SQLite PRAGMA를 반드시 확인하세요. `MetaData`는 마이그레이션 도구의 기준이 됩니다. 처음부터 올바르게 설정하면 이후 ALTER TABLE 작업이 안전해집니다. 다음 글에서는 이 스키마 객체로 select, insert, update, delete를 Core 스타일로 다루는 방법을 알아봅니다.

## 참고 자료

- [SQLAlchemy 2.x - Working with Database Metadata](https://docs.sqlalchemy.org/en/20/tutorial/metadata.html)
- [SQLAlchemy 2.x - Column and Data Types](https://docs.sqlalchemy.org/en/20/core/types.html)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/sqlalchemy-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 SQLAlchemy 기초 (1/10): Engine과 Connection
- **바이브코딩을 위한 SQLAlchemy 기초 (2/10): MetaData와 Schema (현재 글)**
- 바이브코딩을 위한 SQLAlchemy 기초 (3/10): Core CRUD
- 바이브코딩을 위한 SQLAlchemy 기초 (4/10): ORM 모델 정의
- 바이브코딩을 위한 SQLAlchemy 기초 (5/10): Session과 Unit of Work
- 바이브코딩을 위한 SQLAlchemy 기초 (6/10): 관계 매핑
- 바이브코딩을 위한 SQLAlchemy 기초 (7/10): 로딩 전략과 N+1
- 바이브코딩을 위한 SQLAlchemy 기초 (8/10): 이벤트와 확장점
- 바이브코딩을 위한 SQLAlchemy 기초 (9/10): 비동기 SQLAlchemy
- 바이브코딩을 위한 SQLAlchemy 기초 (10/10): 프로덕션 패턴
<!-- toc:end -->

Tags: 바이브코딩, SQLAlchemy, Python, Database, Schema
