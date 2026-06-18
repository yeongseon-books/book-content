---
title: "바이브코딩을 위한 SQLAlchemy 기초 (9/10): 비동기 SQLAlchemy"
series: sqlalchemy-101
episode: 9
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - SQLAlchemy
  - Python
  - Async
  - AsyncSession
---

# 바이브코딩을 위한 SQLAlchemy 기초 (9/10): 비동기 SQLAlchemy

이 글은 "바이브코딩을 위한 SQLAlchemy 기초" 시리즈의 아홉 번째 글입니다.

---

바이브코딩에서 AI는 FastAPI + SQLAlchemy 비동기 코드를 빠르게 만들어 줍니다. `async def`, `await`, `AsyncSession`이 포함된 코드가 순식간에 생성됩니다. 그런데 이 코드가 실제로 어떻게 동작하는지 이해하지 못하면 예상치 못한 오류와 성능 문제를 만납니다.

동기 ORM에서 "그냥 속성 접근"처럼 보이던 lazy 로딩이 비동기 컨텍스트에서는 즉시 오류가 됩니다. `await`를 빠뜨리거나, 동기 드라이버 URL을 비동기 engine에 사용하거나, `AsyncSession`을 동기 `Session`처럼 사용하면 이벤트 루프가 블록되거나 `MissingGreenlet` 오류가 발생합니다.

비동기 SQLAlchemy는 동기 버전과 완전히 다른 제품을 배우는 것이 아닙니다. 거의 같은 API를 더 명시적인 IO 규칙 위에서 다시 읽는 일입니다. 어디에서 `await`가 필요하고, 왜 eager loading이 더 중요해지는지가 핵심입니다.

> **핵심 인사이트:** `AsyncSession`에서는 lazy 로딩이 동작하지 않습니다. `user.posts`에 접근하면 `MissingGreenlet` 오류가 발생합니다. 모든 관계 로딩을 `selectinload`나 `joinedload`로 명시해야 합니다. URL에 `sqlite+aiosqlite://`처럼 비동기 드라이버를 명시해야 합니다.

## 이 글에서 다룰 문제

- `create_async_engine`과 `AsyncSession`은 동기 버전과 무엇이 같고 다른가요?
- URL에 `sqlite+aiosqlite`가 필요한 이유는 무엇인가요?
- async 환경에서 왜 lazy 로딩이 오류가 될까요?
- FastAPI에서 `AsyncSession`을 어떻게 의존성 주입할까요?
- AI가 만든 비동기 SQLAlchemy 코드에서 확인해야 할 것은 무엇인가요?

## 비동기 SQLAlchemy 핵심 패턴

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from models import Base, User, Post

# 비동기 engine: URL에 aiosqlite 드라이버 명시 필수
engine = create_async_engine(
    "sqlite+aiosqlite:///app.db",  # 동기: "sqlite:///app.db"
    echo=False,
)

AsyncSessionFactory = async_sessionmaker(
    engine,
    expire_on_commit=False,  # commit 후 속성 접근 시 추가 SELECT 방지
    class_=AsyncSession,
)

# 스키마 생성
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

```python
# AsyncSession 기본 사용
async def get_user(user_id: int) -> User | None:
    async with AsyncSessionFactory() as session:
        return await session.get(User, user_id)

# 관계 로딩: AsyncSession에서 lazy 로딩 불가 → selectinload 필수
async def get_users_with_posts() -> list[User]:
    async with AsyncSessionFactory() as session:
        result = await session.execute(
            select(User).options(selectinload(User.posts))
            # lazy 로딩 금지: user.posts 접근 시 MissingGreenlet 오류
        )
        return result.scalars().all()

# INSERT
async def create_user(name: str, email: str) -> User:
    async with AsyncSessionFactory() as session:
        user = User(name=name, email=email)
        session.add(user)
        await session.commit()
        return user  # expire_on_commit=False → id 즉시 사용 가능
```

```python
# FastAPI 의존성 주입 패턴
from fastapi import Depends, FastAPI
from typing import AsyncGenerator

app = FastAPI()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        yield session

@app.get("/users/{user_id}")
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    user = await db.get(User, user_id)
    if user is None:
        return {"error": "not found"}
    return {"id": user.id, "name": user.name}
```

## 변경 전후 비교

**Before: 비동기 컨텍스트에서의 오류 패턴**
```text
- 동기 드라이버 URL "sqlite:///" → 이벤트 루프 블록
- AsyncSession에서 user.posts 접근 → MissingGreenlet 오류
- await 없이 session.execute() 호출 → TypeError
- 동기 Session을 async def 핸들러에서 사용 → 이벤트 루프 블록
- expire_on_commit=True → commit 후 속성 접근 시 추가 SELECT
```

**After: 올바른 비동기 패턴**
```text
- "sqlite+aiosqlite:///"로 비동기 드라이버 명시
- selectinload로 관계를 미리 로딩 (lazy 로딩 없음)
- await session.execute(), await session.commit() 명시
- FastAPI Depends로 AsyncSession 의존성 주입
- expire_on_commit=False로 commit 후 안전한 속성 접근
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 동기 드라이버 URL 사용 | 이벤트 루프 블록 | `sqlite+aiosqlite://` URL 사용 |
| `AsyncSession`에서 lazy 로딩 | `MissingGreenlet` 오류 | `selectinload`/`joinedload` 명시 |
| `await` 누락 | `TypeError: object is not awaitable` | 모든 DB 호출에 `await` 추가 |
| 동기 Session을 async 핸들러에서 사용 | 이벤트 루프 블록 | `AsyncSession`과 `async_sessionmaker` 사용 |
| `run_sync` 없이 동기 함수 직접 호출 | `greenlet` 오류 | `await conn.run_sync(...)` 사용 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"FastAPI와 SQLAlchemy 2.x 비동기 버전으로 User CRUD를 만들어줘.
create_async_engine, AsyncSession, async_sessionmaker 사용,
URL에 sqlite+aiosqlite 드라이버,
FastAPI Depends로 AsyncSession 주입,
관계 로딩에 selectinload 사용 (lazy 로딩 없음)"

# AI 결과물 검증 체크포인트:
# - URL이 sqlite+aiosqlite:// 형식인가?
# - AsyncSession에서 관계 속성에 직접 접근하는가? (있으면 오류)
# - 모든 DB 호출에 await가 있는가?
# - 동기 Session이 async 함수 안에서 사용되는가? (있으면 안 됨)
# - expire_on_commit=False가 설정되어 있는가?
```

## 운영 체크리스트

- [ ] `create_async_engine` URL에 `+aiosqlite` 비동기 드라이버를 명시한다
- [ ] `AsyncSession`에서 관계 속성에 `selectinload`/`joinedload`를 명시한다
- [ ] 모든 DB 호출(`execute`, `commit`, `get`)에 `await`를 사용한다
- [ ] `async_sessionmaker(expire_on_commit=False)`를 설정한다
- [ ] FastAPI `Depends`로 `AsyncSession` 의존성을 주입한다

## 처음 질문으로 돌아가기

- **동기와 비동기 SQLAlchemy의 핵심 차이는?** API는 거의 같습니다. 차이는 "암묵적 IO"가 허용되지 않는다는 점입니다. 동기에서는 `user.posts` 접근 시 암묵적으로 SELECT가 발사되지만, 비동기에서는 이 암묵적 IO를 허용하지 않아 `MissingGreenlet` 오류가 됩니다. 모든 IO는 명시적 `await`이 필요합니다.
- **비동기 환경에서 eager loading이 더 중요한 이유는?** `AsyncSession`에서는 lazy 로딩이 불가능합니다. 관계 데이터가 필요하면 쿼리 시점에 `selectinload` 또는 `joinedload`로 미리 가져와야 합니다. 동기 환경보다 더 명시적인 로딩 전략이 요구됩니다.
- **`run_sync`는 언제 사용하는가?** `Base.metadata.create_all(engine)`처럼 동기 함수를 비동기 컨텍스트에서 호출할 때 `await conn.run_sync(Base.metadata.create_all)`로 감쌉니다. Alembic의 마이그레이션 실행도 같은 패턴을 씁니다.

## 정리

바이브코딩에서 AI가 만든 비동기 SQLAlchemy 코드에서 동기 드라이버 URL, `AsyncSession`에서의 lazy 로딩, `await` 누락을 반드시 확인하세요. 비동기 환경에서는 모든 관계 로딩을 명시적으로 설정해야 합니다. 다음 글에서는 connection pool, 관측, 마이그레이션, 배포 패턴 등 프로덕션에서 필요한 내용을 다룹니다.

## 참고 자료

- [SQLAlchemy 2.x - Asyncio Extension](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [aiosqlite 드라이버](https://pypi.org/project/aiosqlite/)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/sqlalchemy-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 SQLAlchemy 기초 (1/10): Engine과 Connection
- 바이브코딩을 위한 SQLAlchemy 기초 (2/10): MetaData와 Schema
- 바이브코딩을 위한 SQLAlchemy 기초 (3/10): Core CRUD
- 바이브코딩을 위한 SQLAlchemy 기초 (4/10): ORM 모델 정의
- 바이브코딩을 위한 SQLAlchemy 기초 (5/10): Session과 Unit of Work
- 바이브코딩을 위한 SQLAlchemy 기초 (6/10): 관계 매핑
- 바이브코딩을 위한 SQLAlchemy 기초 (7/10): 로딩 전략과 N+1
- 바이브코딩을 위한 SQLAlchemy 기초 (8/10): 이벤트와 확장점
- **바이브코딩을 위한 SQLAlchemy 기초 (9/10): 비동기 SQLAlchemy (현재 글)**
- 바이브코딩을 위한 SQLAlchemy 기초 (10/10): 프로덕션 패턴
<!-- toc:end -->

Tags: 바이브코딩, SQLAlchemy, Python, Async, AsyncSession
