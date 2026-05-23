---
title: "SQLAlchemy 101 (9/10): 비동기 SQLAlchemy: aiosqlite와 AsyncSession"
series: sqlalchemy-101
episode: 9
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
- SQLAlchemy
- async
- aiosqlite
- AsyncSession
- SQLite
last_reviewed: '2026-05-12'
seo_description: AsyncSession과 aiosqlite를 써서 비동기 SQLAlchemy를 안전하게 다루는 방법을 설명합니다
---

# SQLAlchemy 101 (9/10): 비동기 SQLAlchemy: aiosqlite와 AsyncSession

비동기 웹 애플리케이션으로 넘어가면 같은 ORM 코드라도 더 엄격한 규칙이 생깁니다. 동기 코드에서 "그냥 속성 접근"처럼 보이던 lazy 로딩이 비동기 컨텍스트에서는 곧바로 오류가 되기 때문입니다.

이 글은 SQLAlchemy 101 시리즈의 아홉 번째 글입니다. 여기서는 `AsyncSession`, `async_sessionmaker`, `aiosqlite`를 기준으로 비동기 SQLAlchemy의 사용 패턴을 정리합니다.

중요한 점은 동기 ORM과 완전히 다른 제품을 배우는 것이 아니라, 거의 같은 API를 더 명시적인 IO 규칙 위에서 다시 읽는 일이라는 사실입니다. 어디에서 `await`가 필요하고, 왜 eager loading이 더 중요해지는지를 이번 글에서 정리합니다.

![비동기 SQLAlchemy: aiosqlite와 AsyncSession](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/09/09-01-async-sqlalchemy-with-aiosqlite-and-asyn.ko.png)

*비동기 SQLAlchemy: aiosqlite와 AsyncSession*

![SQLAlchemy 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/09/09-02-why-this-matters.ko.png)
*SQLAlchemy 101 9장 흐름 개요*
> 비동기 SQLAlchemy: aiosqlite와 AsyncSession의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- `create_async_engine`과 `AsyncSession`은 동기 버전과 무엇이 같고 무엇이 다를까요?
- URL에 `sqlite+aiosqlite` 같은 비동기 드라이버 표기는 왜 중요할까요?
- async 환경에서는 왜 암묵적 IO를 피해야 할까요?

## 왜 중요한가

FastAPI, Starlette, aiohttp 같은 async 프레임워크에서 동기 SQLAlchemy를 그대로 쓰면 이벤트 루프가 블록됩니다. SQLAlchemy 2.x의 async API는 1.4부터 정식 도입돼 안정화됐고, SQLite도 `aiosqlite` 드라이버로 같은 패턴을 쓸 수 있습니다.

다만 async가 동기와 달리 신경 써야 할 지점이 몇 군데 있습니다. 특히 lazy loading은 동기에서는 추가 SELECT 한 번이지만 async에서는 "동기 IO를 비동기 컨텍스트에서 호출"하는 형태가 돼 즉시 예외가 됩니다. 이 글에서 그 차이를 확실히 짚습니다.

## 멘탈 모델

![Mental model](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/09/09-03-mental-model.ko.png)

*멘탈 모델*
> async SQLAlchemy는 **기존 ORM의 얇은 awaitable wrapper**입니다. 내부적으로 동기 ORM을 thread pool 위에서 돌리지 않고, greenlet 기반 어댑터로 동기 호출을 비동기 경계에 노출합니다. 그래서 API는 거의 같지만, "암묵적 IO"가 일어날 자리는 모두 명시적 `await`이 필요합니다.

여기서 먼저 볼 점은 두 가지입니다.

- **명시적 IO**: `select`, `insert`, `update`, `delete`는 모두 `await session.execute(...)` 또는 `await session.scalars(...)`로 호출합니다.
- **암묵적 IO 차단**: lazy load 같은 "내가 모르는 사이 일어나는 SQL"은 async에서는 거의 다 에러로 바뀝니다. 그래서 eager loading 전략이 더 강하게 요구됩니다.

## 핵심 개념

![핵심 개념](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/09/09-04-core-concepts.ko.png)

*핵심 개념*
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

## 이전 방식과 개선 방식

동기 코드를 async로 옮기는 1대1 매핑입니다.

```python
# 이전: 동기 버전
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
# 이후: 비동기 버전
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

![단계별 실습](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/09/09-05-step-by-step-walkthrough.ko.png)

*단계별 실습*
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

## 정리, 다음 글

async SQLAlchemy는 동기 API의 awaitable 버전이지만, "암묵적 IO"가 사라진다는 점에서 사고방식의 전환이 필요합니다. 드라이버를 async로 바꾸고, `await`을 추가하고, eager loading을 기본으로 둔다는 세 가지만 지키면 대부분의 코드는 그대로 옮겨집니다.

다음 글은 production 운영 패턴입니다. 풀 사이즈, pre-ping, 관측, slow query, 마이그레이션과의 배포 순서까지 다룹니다.

## async 실전 앵커: MissingGreenlet 재현과 해결

async ORM에서 가장 많이 만나는 오류를 먼저 재현해 보겠습니다.

```python
async with SessionLocal() as session:
    user = await session.get(User, 1)
    print(len(user.posts))
```

위 코드는 관계가 lazy이면 다음과 비슷한 예외를 냅니다.

```text
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called;
can't call await_only() here. Was IO attempted in an unexpected place?
```

해결은 항상 명시적 eager loading입니다.

```python
stmt = select(User).options(selectinload(User.posts)).where(User.id == 1)
user = await session.scalar(stmt)
print(len(user.posts))
```

비동기 환경에서 "관계 접근은 이미 로드된 상태여야 한다"를 팀 규칙으로 고정하면 대부분의 오류를 예방할 수 있습니다.

## AsyncSession 트랜잭션 패턴

가장 안전한 기본형은 아래 두 레이어입니다.

```python
async with SessionLocal() as session:
    async with session.begin():
        ...
```

외부 함수는 `commit()`을 호출하지 않고, 예외는 위로 올립니다. 상위에서 트랜잭션 경계를 소유하면 동기 코드와 동일한 설계를 유지할 수 있습니다.

```python
async def create_order(session: AsyncSession, user_id: int, amount: int) -> int:
    order = Order(user_id=user_id, amount=amount)
    session.add(order)
    await session.flush()
    return order.id

async with SessionLocal() as session:
    async with session.begin():
        oid = await create_order(session, user_id=10, amount=5000)
```

## aiosqlite 한계와 write 직렬화

`aiosqlite`는 async API를 제공하지만 SQLite의 단일 writer 제약은 그대로입니다. 동시에 많은 write를 보내면 `database is locked` 또는 `SQLITE_BUSY`가 발생할 수 있습니다.

완화책은 다음 순서로 적용합니다.

- 트랜잭션을 짧게 유지
- 대량 write는 배치로 묶어 flush 횟수 감소
- 재시도는 `OperationalError`/busy 상황에만 제한적으로 적용
- write 비중이 커지면 PostgreSQL + asyncpg 전환 검토

```python
from sqlalchemy.exc import OperationalError

for attempt in range(3):
    try:
        async with SessionLocal() as session:
            async with session.begin():
                session.add(obj)
        break
    except OperationalError:
        if attempt == 2:
            raise
        await asyncio.sleep(0.2 * (attempt + 1))
```

## async 관측: 쿼리 시간과 태스크 상관관계

비동기에서는 동일한 초에 여러 코루틴이 섞여 로그가 읽기 어렵습니다. 엔진 이벤트에 request_id를 함께 남기면 추적이 쉬워집니다.

```python
request_id_var = contextvars.ContextVar("request_id", default="-")

@event.listens_for(engine.sync_engine, "before_cursor_execute")
def _before(conn, cursor, statement, params, context, executemany):
    context._t0 = time.perf_counter()

@event.listens_for(engine.sync_engine, "after_cursor_execute")
def _after(conn, cursor, statement, params, context, executemany):
    ms = (time.perf_counter() - context._t0) * 1000
    rid = request_id_var.get()
    logger.info("rid=%s sql_ms=%.1f sql=%s", rid, ms, statement[:120])
```

`AsyncEngine`에서도 이벤트 타깃은 내부 `sync_engine`이라는 점을 기억해 두면 됩니다.

## Async Alembic 연계

운영에서는 애플리케이션은 async라도 마이그레이션은 동기 연결을 별도로 두는 경우가 많습니다. 핵심은 "런타임 세션 경로"와 "DDL 실행 경로"를 분리하는 것입니다.

- 앱 코드: `sqlite+aiosqlite:///...`
- Alembic env: 동기 URL(`sqlite:///...`) 또는 공식 async 템플릿

이 분리를 명시해 두면 배포 시점에 마이그레이션 실패 원인을 빨리 좁힐 수 있습니다.

## Async 테스트 패턴

`pytest-asyncio`에서 자주 쓰는 fixture 골격입니다.

```python
@pytest_asyncio.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        yield session

    await engine.dispose()
```

테스트마다 엔진을 닫아 주지 않으면 이벤트 루프 종료 시 경고가 남고, 파일 핸들 누수로 이어질 수 있습니다.

## 보강 앵커: 비동기 관계 로딩 계약

async 프로젝트에서는 관계 접근 계약을 문서로 못 박아 두는 편이 좋습니다.

- 서비스 함수는 필요한 관계를 `options(...)`로 명시한다
- DTO 변환 함수는 SQL을 발생시키지 않는다
- `lazy="raise"` 또는 테스트용 `raiseload`로 누락을 검출한다

```python
stmt = (
    select(User)
    .options(selectinload(User.posts), selectinload(User.teams))
    .where(User.id == user_id)
)
user = await session.scalar(stmt)
```

이 계약을 지키면 MissingGreenlet 계열 오류를 구조적으로 차단할 수 있습니다.

## 보강 앵커: async 성능 프로파일링 루틴

배포 전 부하 리허설에서 다음 지표를 동시에 봅니다.

- 요청당 await SQL 횟수
- 평균/상위 지연(P95/P99)
- `OperationalError` 발생률
- `database is locked` 재시도 횟수

비동기라고 해서 DB 병목이 사라지지 않습니다. 오히려 동시 요청이 늘어 병목이 더 빨리 드러납니다.

## 보강 앵커: 취소(cancel)와 롤백

async 환경에서는 요청 취소가 자주 일어납니다. 취소 예외가 발생하면 세션을 명시적으로 정리해야 합니다.

```python
async with SessionLocal() as session:
    try:
        async with session.begin():
            await do_write(session)
    except asyncio.CancelledError:
        await session.rollback()
        raise
```

이 처리가 없으면 커넥션 반환 지연과 예기치 않은 트랜잭션 잔존 문제가 생길 수 있습니다.

## 보강 앵커: 비동기 배치 패턴

대량 처리에서는 한 트랜잭션에 너무 많이 담지 않는 것이 핵심입니다.

```python
async def import_users(rows: list[dict], chunk: int = 500):
    for i in range(0, len(rows), chunk):
        part = rows[i:i+chunk]
        async with SessionLocal() as session:
            async with session.begin():
                session.add_all([User(**r) for r in part])
```

청크 단위 커밋은 실패 범위를 줄이고, sqlite busy 경쟁을 완화합니다.

## 보강 앵커: AsyncSession + repository 패턴 예시

코드베이스가 커지면 쿼리 코드를 핸들러에서 분리하는 편이 좋습니다. async에서도 원칙은 같습니다.

```python
class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_detail(self, user_id: int) -> User | None:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.posts), selectinload(User.teams))
        )
        return await self.session.scalar(stmt)

    async def create(self, email: str, name: str) -> User:
        u = User(email=email, name=name)
        self.session.add(u)
        await self.session.flush()
        return u
```

핵심은 repository가 트랜잭션 경계를 갖지 않는다는 점입니다. 트랜잭션은 상위 서비스 계층에서 `async with session.begin()`으로 관리합니다.

## 보강 앵커: 종료 시그널과 엔진 정리

웹 서버 종료 시 `await engine.dispose()`를 호출하지 않으면 풀 커넥션 정리가 지연되어 테스트/개발 환경에서 경고가 누적될 수 있습니다.

```python
@app.on_event("shutdown")
async def shutdown_event():
    await engine.dispose()
```

작아 보이지만 장기 실행 프로세스에서는 이 한 줄이 리소스 누수를 막는 안전장치가 됩니다.

## 보강 앵커: 읽기-쓰기 분리 준비

SQLite 단계에서는 단일 DB를 쓰더라도, 코드 구조를 읽기/쓰기 경로로 분리해 두면 PostgreSQL 전환 시 유리합니다.

- read query 함수와 write command 함수를 분리
- write 함수는 항상 트랜잭션 컨텍스트에서만 호출
- read 함수는 로딩 전략을 명시하고 side effect 금지

이 분리는 비동기 전환 이후 장애 분석에서도 도움이 됩니다. 문제가 read 지연인지 write 경합인지 빠르게 구분할 수 있기 때문입니다.

마지막으로 async 코드 리뷰에서는 "await 없는 DB 접근이 있는가"를 전용 체크 항목으로 두는 편이 효과적입니다. 특히 직렬화 코드와 유틸 함수에서 관계 접근이 숨어 들어오기 쉽습니다.

async 환경에서도 원칙은 동일합니다. 트랜잭션을 짧게 유지하고, 관계 로딩은 명시하고, 종료 시 자원을 정리하면 예측 가능한 동작을 만들 수 있습니다.

이 기준을 지키면 비동기 전환 이후에도 데이터 계층의 예측 가능성을 유지할 수 있습니다.

## 처음 질문으로 돌아가기

- **`create_async_engine`과 `AsyncSession`은 동기 버전과 무엇이 같고 무엇이 다를까요?**
  - 기본 구조는 동기 버전과 거의 같아서 엔진, 세션 팩토리, `select(User)` 같은 ORM 패턴을 그대로 가져갑니다. 대신 `async with SessionLocal()`과 `await session.execute(...)`가 필수이고, DDL은 `await conn.run_sync(Base.metadata.create_all)`처럼 동기 함수를 비동기 경계에서 감싸야 하며 `expire_on_commit=False`도 사실상 기본값으로 둡니다.
- **URL에 `sqlite+aiosqlite` 같은 비동기 드라이버 표기는 왜 중요할까요?**
  - `sqlite:///`가 아니라 `sqlite+aiosqlite:///./app.db`처럼 드라이버를 명시해야 SQLAlchemy가 async DBAPI 어댑터를 선택하고 `AsyncEngine` 경로를 구성할 수 있습니다. 본문이 PostgreSQL의 `postgresql+asyncpg`까지 함께 보여 준 이유도, 비동기 전환의 첫 단추가 URL dialect+driver 문자열이기 때문입니다.
- **async 환경에서는 왜 암묵적 IO를 피해야 할까요?**
  - 동기 코드에서는 lazy 관계 접근이 추가 SELECT 한 번으로 끝나지만, async에서는 그 숨은 IO가 `MissingGreenlet` 오류로 바로 드러납니다. 그래서 `selectinload(User.posts)` 같은 eager loading, `await session.flush()`, 요청 단위 세션 종료처럼 IO 경계를 모두 코드에 명시해야 예측 가능한 동작을 유지할 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [SQLAlchemy 101 (1/10): SQLAlchemy 2.x 시작하기 - Engine과 Connection의 본질](./01-sqlalchemy-2x-engine-connection.md)
- [SQLAlchemy 101 (2/10): SQLAlchemy Core - MetaData, Table, Column으로 schema를 Python 객체로 만들기](./02-core-metadata-table-types.md)
- [SQLAlchemy 101 (3/10): SQLAlchemy Core - select·insert·update·delete를 2.x style로 다루기](./03-core-select-insert-update-delete.md)
- [SQLAlchemy 101 (4/10): ORM 기초: DeclarativeBase와 mapped_column으로 모델 정의하기](./04-orm-declarative-mapped-column.md)
- [SQLAlchemy 101 (5/10): Session 깊이 보기: Unit of Work와 Identity Map의 동작 원리](./05-session-unit-of-work-identity-map.md)
- [SQLAlchemy 101 (6/10): ORM 관계 매핑: relationship과 back_populates로 양방향 탐색 안전하게 잇기](./06-relationships-back-populates.md)
- [SQLAlchemy 101 (7/10): 로딩 전략과 N+1 문제: lazy/joined/selectin을 언제 골라야 하는가](./07-loading-strategies-n-plus-one.md)
- [SQLAlchemy 101 (8/10): 이벤트, hybrid_property, 그리고 커스텀 타입](./08-events-hybrid-types.md)
- **SQLAlchemy 101 (9/10): 비동기 SQLAlchemy: aiosqlite와 AsyncSession (현재 글)**
- SQLAlchemy 101 (10/10): 프로덕션 패턴: 풀, 관측, 마이그레이션, 배포 (예정)

<!-- toc:end -->

## 참고 자료

- SQLAlchemy: Asynchronous I/O — https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- aiosqlite — https://github.com/omnilib/aiosqlite
- SQLAlchemy: AsyncSession API — https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#sqlalchemy.ext.asyncio.AsyncSession
- FastAPI: SQL (Relational) Databases — https://fastapi.tiangolo.com/tutorial/sql-databases/

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/sqlalchemy-101/ko)

Tags: Python, SQLAlchemy, ORM, Database
