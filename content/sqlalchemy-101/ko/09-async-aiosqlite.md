---
title: "비동기 SQLAlchemy: aiosqlite와 AsyncSession"
series: sqlalchemy-101
episode: 9
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
  - async
  - aiosqlite
  - AsyncSession
  - SQLite
last_reviewed: '2026-05-03'
---

# 비동기 SQLAlchemy: aiosqlite와 AsyncSession

## 이 글에서 배울 것

- SQLAlchemy 2.x의 async 스택 구조: `create_async_engine`, `AsyncEngine`, `AsyncSession`
- SQLite를 async로 쓰기 위한 `aiosqlite` 드라이버 설정
- 동기 패턴을 async로 옮기는 1대1 매핑(`session.execute`, `session.scalars`)
- async에서 lazy loading이 더 위험한 이유와 회피 전략
- async + FastAPI 같은 web framework에서의 세션 라이프사이클

## 이 글에서 답할 질문

- SQLAlchemy 2.x의 `create_async_engine`, `AsyncEngine`, `AsyncSession`은 동기 스택과 어떻게 매핑되는가?
- SQLite를 async로 쓰기 위해 `aiosqlite` 드라이버는 어떻게 설치·설정하는가?
- 동기 코드의 `session.execute` / `session.scalars`를 async로 옮길 때의 1대1 변환 규칙은 무엇인가?
- async 환경에서 lazy loading이 더 위험한 이유는 무엇이며 어떻게 회피하는가?
- FastAPI 같은 async web framework에서 `AsyncSession`의 라이프사이클은 어떻게 잡는 것이 안전한가?

## 왜 중요한가

FastAPI, Starlette, aiohttp 같은 async 프레임워크에서 동기 SQLAlchemy를 그대로 쓰면 이벤트 루프가 블록됩니다. SQLAlchemy 2.x의 async API는 1.4부터 정식 도입돼 안정화됐고, SQLite도 `aiosqlite` 드라이버로 같은 패턴을 쓸 수 있습니다.

다만 async가 동기와 달리 신경 써야 할 지점이 몇 군데 있습니다. 특히 lazy loading은 동기에서는 추가 SELECT 한 번이지만 async에서는 "동기 IO를 비동기 컨텍스트에서 호출"하는 형태가 돼 즉시 예외가 됩니다. 이 글에서 그 차이를 확실히 짚습니다.

## Mental Model

> async SQLAlchemy는 **기존 ORM의 얇은 awaitable wrapper**입니다. 내부적으로 동기 ORM을 thread pool 위에서 돌리지 않고, greenlet 기반 어댑터로 동기 호출을 비동기 경계에 노출합니다. 그래서 API는 거의 같지만, "암묵적 IO"가 일어날 자리는 모두 명시적 `await`이 필요합니다.

핵심은 두 가지입니다.

- **명시적 IO**: `select`, `insert`, `update`, `delete`는 모두 `await session.execute(...)` 또는 `await session.scalars(...)`로 호출합니다.
- **암묵적 IO 차단**: lazy load 같은 "내가 모르는 사이 일어나는 SQL"은 async에서는 거의 다 에러로 바뀝니다. 그래서 eager loading 전략이 더 강하게 요구됩니다.

## 핵심 개념

### `create_async_engine` / `AsyncEngine`

`from sqlalchemy.ext.asyncio import create_async_engine`로 만든 엔진은 `AsyncEngine`입니다. 동기 `Engine`과 거의 같지만, `connect`/`begin`이 async context manager입니다.

### URL과 드라이버

| DB | URL |
| --- | --- |
| SQLite | `sqlite+aiosqlite:///./app.db` |
| PostgreSQL | `postgresql+asyncpg://user:pass@host/db` |
| MySQL | `mysql+aiomysql://user:pass@host/db` |

이 글에서는 `pip install "sqlalchemy>=2.0" aiosqlite`로 SQLite 기준으로 설명합니다.

### `AsyncSession` / `async_sessionmaker`

`AsyncSession`은 동기 `Session`의 awaitable 버전입니다. `async_sessionmaker`로 팩토리를 만들고, `async with` 블록 안에서 사용합니다. **`expire_on_commit=False`가 사실상 필수**입니다. 이유는 아래에서 설명합니다.

### lazy IO 차단

async에서는 `obj.posts` 같은 lazy 접근이 동기 SQL을 호출하므로, SQLAlchemy가 `MissingGreenlet` 류 에러를 던집니다. async에서는 7편의 `selectinload`/`joinedload`가 "선택"이 아니라 "기본 전략"이 됩니다.

## Before-After

동기 코드를 async로 옮기는 1대1 매핑입니다.

```python
# Before: sync
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///./app.db")
SessionLocal = sessionmaker(engine, expire_on_commit=False)

def list_users():
    with SessionLocal() as session:
        result = session.execute(select(User))
        return result.scalars().all()
```

```python
# After: async
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

engine = create_async_engine("sqlite+aiosqlite:///./app.db")
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def list_users():
    async with SessionLocal() as session:
        result = await session.execute(select(User))
        return result.scalars().all()
```

차이점은 다음과 같습니다.

- `create_engine` → `create_async_engine`
- URL 드라이버: `sqlite:///` → `sqlite+aiosqlite:///`
- `sessionmaker` → `async_sessionmaker(class_=AsyncSession)`
- `with SessionLocal()` → `async with SessionLocal()`
- `session.execute(...)` → `await session.execute(...)`

## 단계별 실습

### 1단계: 환경 준비

```bash
pip install "sqlalchemy>=2.0" aiosqlite
```

### 2단계: 엔진과 세션 팩토리

```python
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

engine = create_async_engine("sqlite+aiosqlite:///./app.db", echo=False)
SessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)
```

### 3단계: 테이블 생성

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase): ...

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    name: Mapped[str]

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

`engine.begin()`은 async context manager이고, DDL은 동기 함수이므로 `conn.run_sync(...)`로 감쌉니다.

### 4단계: 기본 CRUD

```python
async def create_user(email: str, name: str) -> User:
    async with SessionLocal() as session:
        async with session.begin():
            user = User(email=email, name=name)
            session.add(user)
        await session.refresh(user)
        return user

async def get_user(user_id: int) -> User | None:
    async with SessionLocal() as session:
        return await session.get(User, user_id)

async def list_users() -> list[User]:
    async with SessionLocal() as session:
        result = await session.scalars(select(User).order_by(User.id))
        return list(result)
```

`session.begin()`도 async context manager이고, 빠져나갈 때 자동 커밋·롤백을 합니다.

### 5단계: relationship과 eager loading

```python
from sqlalchemy.orm import selectinload

async def list_users_with_posts():
    async with SessionLocal() as session:
        stmt = select(User).options(selectinload(User.posts))
        result = await session.scalars(stmt)
        return list(result)
```

`selectinload`을 빼면 핸들러에서 `user.posts`를 읽을 때 `MissingGreenlet` 같은 에러가 납니다. async에서는 **eager loading이 기본 전략**입니다.

### 6단계: FastAPI 통합

```python
from fastapi import FastAPI, Depends

app = FastAPI()

async def get_session():
    async with SessionLocal() as session:
        yield session

@app.get("/users")
async def list_users(session: AsyncSession = Depends(get_session)):
    result = await session.scalars(select(User).options(selectinload(User.posts)))
    return [{"id": u.id, "email": u.email, "posts": len(u.posts)} for u in result]
```

요청 단위로 세션이 열리고 닫히며, 핸들러는 `await`만 신경 쓰면 됩니다.

## 자주 하는 실수

- **`expire_on_commit=True`를 그대로 두기.** 커밋 후 객체 속성을 읽을 때 lazy refresh가 일어나는데, async에서는 이게 즉시 에러가 됩니다. async에서는 `False`가 사실상 기본값입니다.
- **lazy 관계를 그대로 사용.** 동기에서는 추가 SELECT로 끝나지만, async에서는 `MissingGreenlet`로 깨집니다. `selectinload`/`joinedload`로 항상 명시합니다.
- **동기 드라이버 URL을 사용.** `sqlite:///`로는 async 엔진이 만들어지지 않습니다. `sqlite+aiosqlite:///` 처럼 드라이버를 명시해야 합니다.
- **`run_sync`를 잊고 DDL 호출.** `create_all`은 동기 함수이므로 `await conn.run_sync(Base.metadata.create_all)` 형태로 감쌉니다.
- **세션을 요청 사이에 공유.** `AsyncSession`도 thread/coroutine safe하지 않습니다. 요청마다 새로 만듭니다.

## 실무에서 쓰는 패턴

- **세션 라이프사이클은 요청 단위.** FastAPI라면 dependency, Starlette라면 middleware로 묶습니다.
- **eager loading 정책을 핸들러별로 정의.** "이 엔드포인트는 어떤 관계를 같이 쓰는가"를 query 함수가 직접 표현하면 N+1 회귀를 막을 수 있습니다.
- **트랜잭션 경계는 `async with session.begin()`.** 명시적인 begin/commit보다 컨텍스트 매니저가 안전합니다.
- **SQLite 한정 주의사항.** SQLite는 단일 writer만 허용합니다. async라도 여러 코루틴이 동시에 write를 하면 `SQLITE_BUSY`가 납니다. write가 많은 워크로드라면 PostgreSQL + asyncpg가 더 자연스럽습니다.
- **테스트.** `pytest-asyncio`를 쓰고, fixture에서 `engine` / `SessionLocal`을 만들고 fixture 끝에서 `await engine.dispose()`로 닫습니다.

## 체크리스트

- [ ] URL에 async 드라이버를 명시했다(`sqlite+aiosqlite://`)
- [ ] `async_sessionmaker(..., class_=AsyncSession, expire_on_commit=False)`로 팩토리를 만들었다
- [ ] 모든 SQL 호출이 `await session.execute / scalars / get` 형태다
- [ ] relationship 접근은 `selectinload`/`joinedload`로 미리 로드한다
- [ ] DDL은 `await conn.run_sync(...)`로 감쌌다
- [ ] 세션은 요청·작업 단위로 새로 만들고 끝에 닫는다
- [ ] 종료 시 `await engine.dispose()`를 호출한다

## 연습 문제

1. 위의 동기 CRUD를 async 버전으로 옮겨 단위 테스트로 동등성을 확인하세요.
2. `selectinload`을 빼고 lazy 접근을 시도해 어떤 에러가 발생하는지 직접 재현해 보세요.
3. FastAPI에 `/users/{id}` 엔드포인트를 만들어 async 세션 의존성과 eager loading을 함께 적용하세요.

## 정리, 다음 글

async SQLAlchemy는 동기 API의 awaitable 버전이지만, "암묵적 IO"가 사라진다는 점에서 사고방식의 전환이 필요합니다. 드라이버를 async로 바꾸고, `await`을 추가하고, eager loading을 기본으로 둔다는 세 가지만 지키면 대부분의 코드는 그대로 옮겨집니다.

다음 글은 production 운영 패턴입니다. 풀 사이즈, pre-ping, 관측, slow query, 마이그레이션과의 배포 순서까지 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [SQLAlchemy 2.x 시작하기 - Engine과 Connection의 본질](./01-sqlalchemy-2x-engine-connection.md)
- [SQLAlchemy Core - MetaData, Table, Column으로 schema를 Python 객체로 만들기](./02-core-metadata-table-types.md)
- [SQLAlchemy Core - select·insert·update·delete를 2.x style로 다루기](./03-core-select-insert-update-delete.md)
- [ORM 기초: DeclarativeBase와 mapped_column으로 모델 정의하기](./04-orm-declarative-mapped-column.md)
- [Session 깊이 보기: Unit of Work와 Identity Map의 동작 원리](./05-session-unit-of-work-identity-map.md)
- [ORM Relationships: relationship과 back_populates로 양방향 탐색 안전하게 잇기](./06-relationships-back-populates.md)
- [로딩 전략과 N+1 문제: lazy/joined/selectin을 언제 골라야 하는가](./07-loading-strategies-n-plus-one.md)
- [이벤트, hybrid_property, 그리고 커스텀 타입](./08-events-hybrid-types.md)
- **비동기 SQLAlchemy: aiosqlite와 AsyncSession (현재 글)**
- production 패턴: 풀, 관측, 마이그레이션, 배포 (예정)

<!-- toc:end -->

## 참고 자료

- SQLAlchemy: Asynchronous I/O — https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- aiosqlite — https://github.com/omnilib/aiosqlite
- SQLAlchemy: AsyncSession API — https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#sqlalchemy.ext.asyncio.AsyncSession
- FastAPI: SQL (Relational) Databases — https://fastapi.tiangolo.com/tutorial/sql-databases/

Tags: Python, SQLAlchemy, ORM, Database
