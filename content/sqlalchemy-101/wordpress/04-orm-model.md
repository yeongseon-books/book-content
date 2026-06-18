---
title: "바이브코딩을 위한 SQLAlchemy 기초 (4/10): ORM 모델 정의"
series: sqlalchemy-101
episode: 4
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - SQLAlchemy
  - Python
  - ORM
  - DeclarativeBase
---

# 바이브코딩을 위한 SQLAlchemy 기초 (4/10): ORM 모델 정의

이 글은 "바이브코딩을 위한 SQLAlchemy 기초" 시리즈의 네 번째 글입니다.

---

바이브코딩에서 AI는 SQLAlchemy ORM 모델 코드를 빠르게 만들어 줍니다. `class User(Base)`와 컬럼 정의, 관계 속성까지 한 번에 생성해 주는데, 이 코드가 실제로 Core의 어떤 구조 위에서 동작하는지 이해하지 못하면 Session, relationship, 마이그레이션에서 예상치 못한 문제가 생깁니다.

AI가 생성한 ORM 모델 코드에서 자주 보이는 패턴이 있습니다. `DeclarativeBase` 대신 1.x 스타일의 `declarative_base()`를 사용하거나, `Mapped[T]` 타입 힌트 없이 컬럼을 정의하거나, `__tablename__`을 누락하거나, `__table_args__`에 `naming_convention`을 연결하지 않는 패턴입니다. 코드는 돌아가지만 타입 체커가 속성을 인식하지 못하고, Alembic이 제약 조건을 추적하지 못합니다.

SQLAlchemy 2.x ORM은 Core 위에 얹혀 동작합니다. ORM 모델 클래스를 정의하는 순간 내부에서 Core의 `Table`과 `Column`이 만들어지고, `Base.metadata`에 등록됩니다. ORM은 별개의 세계가 아니라 Core 위에서 동작하는 같은 세계입니다.

> **핵심 인사이트:** `DeclarativeBase`를 상속한 모델 클래스는 Core의 `Table` 객체를 자동으로 생성하고 `Base.metadata`에 등록합니다. `Mapped[T]`와 `mapped_column`을 쓰면 타입 힌트와 컬럼 정의가 하나로 통합되어 IDE 자동완성과 타입 체커가 모델 속성을 올바르게 인식합니다.

## 이 글에서 다룰 문제

- `DeclarativeBase`는 Core의 `MetaData`와 어떻게 연결될까요?
- `Mapped[T]`와 `mapped_column`은 타입 힌트와 컬럼 정의를 어떻게 통합할까요?
- `__tablename__`, `__table_args__`는 언제 필요할까요?
- AI가 만든 ORM 모델 코드에서 확인해야 할 것은 무엇인가요?
- 2.x 스타일 모델 정의가 1.x와 어떻게 다른가요?

## ORM 모델 정의 핵심 패턴

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, UniqueConstraint
from datetime import datetime, timezone
from typing import Optional

# DeclarativeBase: Base와 MetaData의 그릇
class Base(DeclarativeBase):
    pass
# Base.metadata → Core MetaData에 자동 연결됨

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
    )

    # Mapped[T] + mapped_column: 타입 힌트와 컬럼 정의 통합
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    # Optional: NULL 허용 컬럼
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # relationship은 6편에서 자세히 다룸
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="author")

    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.name!r})"
```

```python
class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    author: Mapped["User"] = relationship("User", back_populates="posts")

# ORM 모델이 Core Table 객체를 들고 있음을 확인
print(User.__table__)       # Core Table("users", ...)
print(User.__table__.c)     # Core Column 집합
print(Base.metadata.tables) # 모든 등록된 테이블
```

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///app.db")

# ORM 모델의 스키마를 DB에 생성 (Core create_all과 같은 원리)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

# 기본 사용 패턴
with Session() as session:
    user = User(name="Alice", email="alice@example.com")
    session.add(user)
    session.commit()
    print(user.id)  # commit 후 id 자동 채워짐
```

## 변경 전후 비교

**Before: 1.x 스타일 모델 정의**
```text
- declarative_base() 함수 사용 (2.x에서 deprecated)
- Column() 직접 사용 - 타입 힌트 없음
- IDE가 User.name의 타입을 Column으로 인식
- 타입 체커가 속성 타입을 알 수 없음
- __repr__ 누락으로 디버깅 어려움
```

**After: 2.x 스타일 DeclarativeBase**
```text
- DeclarativeBase 클래스 상속
- Mapped[str] + mapped_column으로 타입과 컬럼 통합
- IDE 자동완성과 타입 체커가 str로 올바르게 인식
- Optional[str]으로 NULL 허용 여부가 타입에 표현됨
- __repr__ 정의로 세션 디버깅 가능
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| `declarative_base()` 함수 사용 | 2.x에서 deprecated | `DeclarativeBase` 클래스 상속 |
| `Mapped[T]` 없이 `Column()` 사용 | 타입 체커가 타입 모름 | `Mapped[str] = mapped_column(...)` 사용 |
| `__tablename__` 누락 | 클래스 이름에서 추측 (오류 위험) | 항상 명시적으로 선언 |
| `__repr__` 없음 | 세션 디버깅 시 `<User object>` 출력 | `__repr__` 정의 |
| nullable=False를 Mapped에서 누락 | NULL 데이터 허용됨 | `Mapped[str]`(not Optional)로 표현 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"SQLAlchemy 2.x ORM 모델을 만들어줘.
DeclarativeBase 상속, Mapped[T] + mapped_column 사용,
Optional[T]로 nullable 여부 타입에 표현,
__tablename__, __repr__ 포함,
ForeignKey와 relationship 기본 구조 포함"

# AI 결과물 검증 체크포인트:
# - declarative_base() 함수 대신 DeclarativeBase 클래스를 쓰는가?
# - 모든 컬럼이 Mapped[T] 타입 힌트와 함께 정의되어 있는가?
# - NULL 허용 컬럼이 Optional[T]로 표현되어 있는가?
# - __tablename__이 명시되어 있는가?
# - __repr__이 정의되어 있는가?
```

## 운영 체크리스트

- [ ] `DeclarativeBase` 클래스를 상속한다 (1.x `declarative_base()` 아님)
- [ ] 모든 컬럼을 `Mapped[T] = mapped_column(...)` 형식으로 정의한다
- [ ] NULL 허용 컬럼은 `Mapped[Optional[T]]`, 비허용은 `Mapped[T]`로 표현한다
- [ ] 각 모델에 `__tablename__`과 `__repr__`을 정의한다
- [ ] `Base.metadata.create_all(engine)`으로 스키마를 생성한다

## 처음 질문으로 돌아가기

- **`DeclarativeBase`와 Core MetaData의 연결은?** `DeclarativeBase`를 상속한 모델 클래스를 정의하면 내부에서 Core `Table` 객체가 자동 생성되어 `Base.metadata`에 등록됩니다. `Base.metadata.create_all(engine)`으로 모든 ORM 모델의 스키마를 한 번에 생성할 수 있습니다.
- **`Mapped[T]`와 `mapped_column`의 역할은?** `Mapped[T]`는 타입 힌트이고, `mapped_column(...)`은 Core Column 정의입니다. 둘을 함께 쓰면 IDE와 타입 체커가 `user.name`을 `str`로, `user.bio`를 `Optional[str]`로 올바르게 인식합니다.
- **ORM이 Core의 별개 세계가 아닌 이유는?** ORM 모델 클래스 내부에는 여전히 Core `Table`과 `Column` 객체가 있습니다. `User.__table__`로 접근 가능하며, 복잡한 쿼리에서는 이 Core 객체를 직접 사용할 수 있습니다.

## 정리

바이브코딩에서 AI가 만든 ORM 모델 코드에서 `declarative_base()` 함수 사용, `Mapped[T]` 누락, `Optional[T]` 미사용을 확인하세요. 2.x 스타일로 정의된 ORM 모델은 IDE 자동완성과 타입 체커가 올바르게 동작하고, Alembic 마이그레이션과도 안전하게 연동됩니다. 다음 글에서는 Session, Unit of Work, Identity Map의 동작 원리를 다룹니다.

## 참고 자료

- [SQLAlchemy 2.x - ORM Mapped Class Configuration](https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html)
- [SQLAlchemy 2.x - Mapped Column](https://docs.sqlalchemy.org/en/20/orm/mapping_columns.html)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/sqlalchemy-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 SQLAlchemy 기초 (1/10): Engine과 Connection
- 바이브코딩을 위한 SQLAlchemy 기초 (2/10): MetaData와 Schema
- 바이브코딩을 위한 SQLAlchemy 기초 (3/10): Core CRUD
- **바이브코딩을 위한 SQLAlchemy 기초 (4/10): ORM 모델 정의 (현재 글)**
- 바이브코딩을 위한 SQLAlchemy 기초 (5/10): Session과 Unit of Work
- 바이브코딩을 위한 SQLAlchemy 기초 (6/10): 관계 매핑
- 바이브코딩을 위한 SQLAlchemy 기초 (7/10): 로딩 전략과 N+1
- 바이브코딩을 위한 SQLAlchemy 기초 (8/10): 이벤트와 확장점
- 바이브코딩을 위한 SQLAlchemy 기초 (9/10): 비동기 SQLAlchemy
- 바이브코딩을 위한 SQLAlchemy 기초 (10/10): 프로덕션 패턴
<!-- toc:end -->

Tags: 바이브코딩, SQLAlchemy, Python, ORM, DeclarativeBase
