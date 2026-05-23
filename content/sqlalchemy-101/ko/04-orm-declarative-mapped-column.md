---
title: "SQLAlchemy 101 (4/10): ORM 기초: DeclarativeBase와 mapped_column으로 모델 정의하기"
series: sqlalchemy-101
episode: 4
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
- ORM
- DeclarativeBase
- mapped_column
- SQLite
last_reviewed: '2026-05-12'
seo_description: DeclarativeBase, Mapped, mapped_column으로 ORM 모델을 정의하는 방법을 설명합니다
---

# SQLAlchemy 101 (4/10): ORM 기초: DeclarativeBase와 mapped_column으로 모델 정의하기

Core에서 `Table`과 `Column`으로 스키마를 다뤘다면 이제 같은 구조를 Python 클래스 위로 끌어올릴 차례입니다. ORM은 행을 객체로 매핑하고, 객체 상태를 추적해 SQL 실행 시점까지 연결합니다.

이 글은 SQLAlchemy 101 시리즈의 네 번째 글입니다. 여기서는 `DeclarativeBase`, `Mapped[T]`, `mapped_column(...)`을 중심으로 SQLAlchemy 2.x ORM 모델 정의를 정리합니다.

중요한 점은 ORM이 Core와 분리된 세계가 아니라는 사실입니다. 모델 클래스를 정의하는 순간 내부에서는 여전히 `Table`과 `Column`이 만들어지고, `MetaData`에 등록됩니다. 이 연결을 이해해야 이후 Session과 relationship도 덜 헷갈립니다.

![ORM 기초: DeclarativeBase와 mapped_column으로 모델 정의하기](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/04/04-01-orm-basics-defining-models-with-declarat.ko.png)

*ORM 기초: DeclarativeBase와 mapped_column으로 모델 정의하기*

![SQLAlchemy 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/04/04-02-why-it-matters.ko.png)
*SQLAlchemy 101 4장 흐름 개요*
> ORM 기초: DeclarativeBase와 mapped_column으로 모델 정의하기의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- `DeclarativeBase`는 어떤 역할을 하고 왜 `MetaData`와 함께 묶일까요?
- `Mapped[T]`와 `mapped_column`은 타입 힌트, 컬럼 정의와 어떻게 연결될까요?
- `__tablename__`, `__table_args__`, `repr`는 언제부터 필요해질까요?

## 왜 중요한가

Core만으로도 데이터베이스 작업은 충분히 가능합니다. 그러나 애플리케이션이 커지면 다음과 같은 부담이 빠르게 늘어납니다.

- 행 단위 dict를 일일이 다루기 힘들어집니다. `row["email"]`보다 `user.email`이 훨씬 안전하고 읽기 쉽습니다.
- 비즈니스 규칙을 둘 곳이 마땅치 않습니다. ORM 모델은 도메인 객체이자 데이터 매핑이므로, 규칙을 클래스 메서드로 함께 둘 수 있습니다.
- 변경 추적이 수동입니다. 어떤 필드가 바뀌었는지 코드로 직접 비교해서 UPDATE 문을 만들어야 합니다. ORM의 Unit of Work는 이 추적을 자동화합니다 (다음 글에서 다룹니다).
- 관계(관계형 데이터)의 탐색이 SQL JOIN 작성으로 직결됩니다. ORM은 `user.orders` 같은 속성 접근으로 풀어 줍니다 (Ep6).

ORM은 마법이 아니라, Core 위에 얇은 레이어를 얹어 위 비용을 줄이는 도구입니다. 그 첫걸음이 모델 정의입니다.

## 멘탈 모델

![Mental model](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/04/04-03-mental-model.ko.png)

*멘탈 모델*
> ORM 모델 클래스는 "파이썬 클래스 + Core `Table`"의 결합입니다. `DeclarativeBase`는 그 바인딩의 그릇(`MetaData`)이고, `mapped_column`은 그 안에 들어갈 `Column`을 타입 힌트로부터 만들어 주는 헬퍼입니다.

다이어그램으로 보면 단순합니다.

```text
DeclarativeBase
   └── metadata: MetaData       # Core의 schema catalog (Ep2)
         └── tables: dict[str, Table]
               └── Table("users", ...)   <─── ORM 클래스 User가 매핑됨
                     └── Column("id", ...)
                     └── Column("email", ...)
```

즉, ORM 클래스를 정의하는 순간 Core의 `Table` 객체가 자동으로 생성되어 `Base.metadata`에 등록됩니다. 그래서 Ep2에서 배운 `metadata.create_all(engine)`을 그대로 사용해 ORM이 정의한 스키마를 만들 수 있습니다. ORM은 별개의 세계가 아니라, Core 위에서 동작하는 같은 세계입니다.

## 핵심 개념

![핵심 개념](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/04/04-04-core-concepts.ko.png)

*핵심 개념*
### 1) DeclarativeBase

2.x에서 ORM 베이스 클래스는 다음 한 줄로 충분합니다.

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

`Base`는 두 가지 역할을 합니다.

- 모든 ORM 모델 클래스의 부모가 되어, 매핑 처리 로직을 상속시킵니다.
- 내부에 `Base.metadata`라는 `MetaData` 인스턴스를 보유합니다. 모든 모델의 `Table`이 여기에 모입니다.

Ep2에서 `naming_convention`을 권장한 이유가 여기서 다시 등장합니다. ORM에서도 같은 컨벤션을 공유하려면 다음과 같이 명시적으로 `MetaData`를 주입할 수 있습니다.

```python
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
```

이렇게 두면 ORM이 자동으로 만드는 인덱스/외래키/유니크 제약의 이름이 일관되게 잡힙니다. Alembic으로 마이그레이션을 만들 때 이름이 안정적이어야 diff 결과가 깔끔해집니다.

### 2) Mapped[T]와 mapped_column

2.x ORM 모델은 다음 패턴으로 정의합니다.

```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    nickname: Mapped[str | None] = mapped_column(String(50))
```

여기서 일어나는 일을 한 줄씩 짚어 보겠습니다.

- `Mapped[int]`: 이 컬럼은 SQL `INTEGER`로 매핑되며 NOT NULL입니다.
- `Mapped[str | None]`: `Optional`이므로 NULL 허용입니다. `nullable=True`를 명시적으로 쓸 필요가 없습니다.
- `mapped_column(...)`: Core의 `Column(...)`과 거의 같은 인자를 받습니다. `primary_key=True`, `unique=True`, `default=...`, `server_default=...` 등이 모두 동작합니다.
- `String(255)`: 타입을 생략하면 `Mapped[str]` → 일반 `String`(SQLite에서는 `TEXT`로 affinity 매핑)이 자동 선택됩니다. 길이 제한이 필요하면 직접 적어 주는 편이 명확합니다.

### 3) __tablename__과 __table_args__

```python
from sqlalchemy import Index, UniqueConstraint

class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        UniqueConstraint("user_id", "external_ref", name="uq_orders_user_ext"),
        Index("ix_orders_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column()
    external_ref: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[str] = mapped_column()
```

`__tablename__`은 Core의 `Table(name=...)`에 해당하고, `__table_args__`은 `Table(...)`에 함께 넘기던 제약과 인덱스를 모아 두는 자리입니다. 튜플로 작성하며, 마지막 원소로 `dict`를 넣어 `{"sqlite_autoincrement": True}` 같은 dialect 옵션을 줄 수도 있습니다.

### 4) repr와 디버그 가독성

ORM 객체는 기본 `__repr__`이 그리 친절하지 않습니다. 디버깅을 자주 한다면 다음 패턴을 권합니다.

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r})"
```

작은 차이지만, 로그에 객체가 찍히는 순간을 위해 미리 깔아 두면 두고두고 도움이 됩니다.

## 이전 방식과 개선 방식

### 이전: Core만 사용한 INSERT-SELECT

```python
from sqlalchemy import MetaData, Table, Column, Integer, String, insert, select

metadata = MetaData()
users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String(255), unique=True),
)

with engine.begin() as conn:
    metadata.create_all(conn)
    conn.execute(insert(users), [{"email": "a@x.com"}, {"email": "b@x.com"}])

with engine.connect() as conn:
    rows = conn.execute(select(users)).all()
    for row in rows:
        print(row.email)   # row는 Row 객체, Table이라는 스키마 객체에 의존
```

### 개선 후: ORM 모델로 동일 작업

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy import String, select

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)

Base.metadata.create_all(engine)

with Session(engine) as session:
    session.add_all([User(email="a@x.com"), User(email="b@x.com")])
    session.commit()

    users_list = session.scalars(select(User)).all()
    for u in users_list:
        print(u.email)   # u는 User 인스턴스, 도메인 객체로 다룰 수 있음
```

차이는 두 가지입니다. 첫째, `users_list`의 원소가 dict-like Row가 아니라 `User` 인스턴스입니다. 둘째, INSERT 시점에 SQL을 직접 작성하지 않고 객체를 `add_all()`로 등록한 뒤 `commit()`이 한 번에 처리합니다. 이 두 가지가 ORM이 주는 본질적 가치입니다.

## 단계별 실습

![단계별 실습](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/04/04-05-step-by-step-walkthrough.ko.png)

*단계별 실습*
준비물은 SQLite와 SQLAlchemy 2.x뿐입니다. 다음 코드를 한 파일에 저장해 실행해 보면 ORM의 흐름이 손에 익습니다.

```python
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

engine = create_engine("sqlite:///orm_demo.db", echo=False, future=True)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    nickname: Mapped[str | None] = mapped_column(String(50))

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r})"

def main() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add_all([
            User(email="alice@example.com", nickname="alice"),
            User(email="bob@example.com"),
        ])
        session.commit()

    with Session(engine) as session:
        for u in session.scalars(select(User).order_by(User.id)).all():
            print(u, "nickname=", u.nickname)

if __name__ == "__main__":
    main()
```

실행 흐름을 단계로 정리하면 다음과 같습니다.

1. `create_engine`으로 SQLite 엔진을 만듭니다 (Ep1).
2. `Base.metadata.create_all(engine)`로 ORM이 만들어 둔 `users` 테이블을 생성합니다.
3. `Session`을 열어 객체를 `add_all`로 등록하고 `commit()`을 호출하면 INSERT가 실행됩니다.
4. 새 `Session`에서 `scalars(select(User))`로 ORM 인스턴스를 가져옵니다.
5. 출력 결과는 `User(id=1, email='alice@example.com')` 형태로, 우리가 정의한 `__repr__`이 사용됩니다.

여기서 Session과 Unit of Work의 자세한 동작은 다음 글의 주제입니다. 이번 글에서는 "모델을 정의하면 `create_all`로 스키마가 만들어지고, 객체로 INSERT/SELECT를 할 수 있다"는 흐름을 확인하는 것이 목표입니다.

## 자주 하는 실수

### 1) Mapped[T]를 빠뜨려 일반 클래스 속성으로 정의

```python
class User(Base):
    __tablename__ = "users"
    id = mapped_column(primary_key=True)        # 동작은 하지만 타입 정보가 없음
    email = mapped_column(String(255))
```

이렇게 쓰면 모델은 만들어지지만 `user.email`의 타입을 IDE/mypy가 알지 못합니다. 코드 베이스가 커질수록 안전성과 가독성에서 손해가 큽니다. 가능한 한 항상 `Mapped[T]`로 명시하는 편을 권합니다.

### 2) Optional 누락으로 NULL 허용 컬럼이 NOT NULL로 만들어짐

```python
nickname: Mapped[str] = mapped_column(String(50))   # NOT NULL
```

NULL을 허용하려면 `Mapped[str | None]`을 사용해야 합니다. 데이터베이스 스키마 의도와 파이썬 타입이 어긋나면 런타임에 IntegrityError가 발생합니다.

### 3) default와 server_default를 혼동

`default=...`는 파이썬 측에서 INSERT 시점에 값을 채워 SQL 파라미터로 보냅니다. `server_default=...`는 SQL `DEFAULT` 절을 만들어 데이터베이스가 직접 처리합니다. 마이그레이션이나 직접 SQL 삽입 시에도 기본값이 필요하다면 반드시 `server_default`를 함께 적어야 합니다 (Ep2 참고).

### 4) 한 번 만든 매핑을 같은 테이블 이름으로 재정의

같은 프로세스 안에서 `User` 클래스를 두 번 정의하면 SQLAlchemy가 경고를 띄우거나 오류를 냅니다. 테스트에서 모듈 reload를 자주 하는 환경이라면 fixture에서 `Base.metadata.clear()`를 사용하거나, 아예 테스트 전용 별도 `Base`를 두는 편이 안전합니다.

### 5) ORM과 Core의 Table을 두 번 정의

`User` ORM 클래스를 정의해 두고, 같은 이름의 `Table("users", metadata, ...)`를 또 만들면 충돌합니다. ORM을 쓰기로 했다면 스키마 정의 책임은 한쪽으로 모아야 합니다. 보통 ORM이 정의를 갖고, 어쩔 수 없이 Core가 필요하면 `User.__table__`로 가져다 씁니다.

## 실무에서 자주 만나는 상황

- **공통 컬럼 분리**: `id`, `created_at`, `updated_at` 같은 공통 컬럼은 믹스인 클래스로 모아 두면 모델별 보일러플레이트를 줄일 수 있습니다.
- **Enum 매핑**: 파이썬 `enum.Enum`을 그대로 `Mapped[MyEnum]`으로 매핑하면 자동으로 `Enum` 타입이 적용됩니다. SQLite에서는 `VARCHAR`로 저장되며 값의 유효성 검사는 ORM 측에서 수행됩니다.
- **JSON 필드**: `from sqlalchemy import JSON`을 활용해 `Mapped[dict] = mapped_column(JSON)` 형태로 직렬화 가능한 데이터를 컬럼에 저장할 수 있습니다. SQLite에서도 동작합니다.
- **테스트 격리**: 테스트마다 `Base.metadata.drop_all/create_all`을 반복하면 느립니다. SQLite는 in-memory 엔진(`sqlite:///:memory:`)을 활용해 fixture 단위로 빠르게 재생성하는 패턴이 흔히 쓰입니다.
- **마이그레이션 시드**: ORM 모델로 만든 스키마를 기준으로 Alembic의 autogenerate를 돌리려면, Alembic env에서 `target_metadata = Base.metadata`로 연결해 줘야 합니다 (alembic-101 시리즈에서 다룹니다).

## 체크리스트

- [ ] `DeclarativeBase`를 상속한 `Base` 클래스를 정의했는가?
- [ ] 모든 컬럼을 `Mapped[T]: mapped_column(...)` 형태로 선언했는가?
- [ ] NULL 허용 여부를 `Optional`(`| None`)로 명확히 표현했는가?
- [ ] `__tablename__`을 명시했는가? (자동 추론에 의존하지 않기)
- [ ] 인덱스/유니크 제약을 `__table_args__`로 한곳에 모았는가?
- [ ] `Base.metadata`에 `naming_convention`이 적용되어 있는가?
- [ ] `__repr__`을 정의해 디버그 출력이 의미 있게 보이도록 했는가?

## 모델 정의 실전 패턴: 하이브리드 속성과 도메인 기본값

모델 정의 단계에서 가장 큰 차이를 만드는 지점은 "컬럼만 만들고 끝낼 것인가"입니다. 실제 운영 모델은 파생 속성과 정규화 규칙을 함께 가질 때 유지보수가 쉬워집니다.

```python
from datetime import datetime, timezone
from sqlalchemy import String, DateTime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    price_cents: Mapped[int] = mapped_column(nullable=False)
    tax_rate: Mapped[float] = mapped_column(nullable=False, default=0.1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    @hybrid_property
    def price_with_tax(self) -> int:
        return int(self.price_cents * (1 + self.tax_rate))

    @price_with_tax.expression
    def price_with_tax(cls):
        return cls.price_cents * (1 + cls.tax_rate)
```

`hybrid_property`를 지금부터 모델에 두면 8편에서 다룰 내용을 앞당겨 적용할 수 있습니다. Python 객체에서는 `product.price_with_tax`, SQL에서는 `select(Product).where(Product.price_with_tax > 10000)`처럼 같은 의미를 유지합니다.

## SQL echo로 모델-스키마 일치 검증

모델 정의를 바꾼 뒤 `Base.metadata.create_all(engine)`만 믿고 넘어가면 누락을 놓치기 쉽습니다. 다음처럼 DDL 로그를 확인하면 정의가 실제 SQL로 어떻게 내려갔는지 즉시 점검할 수 있습니다.

```python
engine = create_engine("sqlite:///orm_model.db", echo=True)
Base.metadata.create_all(engine)
```

```text
INFO sqlalchemy.engine.Engine CREATE TABLE products (
    id INTEGER NOT NULL,
    name VARCHAR(120) NOT NULL,
    price_cents INTEGER NOT NULL,
    tax_rate FLOAT NOT NULL,
    created_at DATETIME NOT NULL,
    PRIMARY KEY (id)
)
```

모델 리뷰에서 중요한 것은 파이썬 코드가 아니라 최종 DDL입니다. `nullable`, `unique`, 인덱스 이름이 기대와 같지 않다면 배포 전에 반드시 수정합니다.

## Alembic 연계를 위한 준비

4편 단계에서 아래 연결을 미리 맞춰 두면 10편의 배포 파트와 alembic-101로 넘어갈 때 마찰이 줄어듭니다.

```python
# alembic/env.py
from app.models import Base
target_metadata = Base.metadata
```

`target_metadata`를 중심으로 autogenerate가 동작하므로, 모델 모듈 import 누락이 있으면 마이그레이션 diff에 테이블이 통째로 빠집니다. 팀 규칙으로 `models/__init__.py`에서 모든 모델을 명시적으로 import하게 두는 편이 안전합니다.

## 모델 계층의 경계 규칙

운영 코드 기준으로 다음 규칙을 고정하면 이후 Session, relationship, 로딩 전략에서 일관성이 생깁니다.

- 모델 클래스는 "스키마 + 가벼운 도메인 규칙"까지만 담당합니다.
- 외부 API 호출, 파일 IO, 네트워크 요청은 모델 메서드에 넣지 않습니다.
- 모델은 단위 테스트가 가능한 순수 규칙(정규화, 범위 검증, 파생 속성)에 집중합니다.
- 서비스 계층은 트랜잭션 경계와 시나리오 조합을 담당합니다.

이 경계를 먼저 세워 두면 ORM 코드베이스가 커져도 유지보수 난이도가 급격히 오르지 않습니다.

## 보강 앵커: 모델 정의 품질 점검 표

모델이 늘어나면 사람이 눈으로만 검토하기 어렵습니다. 다음 표를 PR 템플릿에 넣어 두면 누락을 크게 줄일 수 있습니다.

| 점검 항목 | 질문 | 실패 시 증상 |
| --- | --- | --- |
| nullable 의도 | `Mapped[T]`에 `None` 포함 여부가 의도와 맞는가 | 배포 후 IntegrityError 증가 |
| 인덱스/유니크 | 조회·중복 제약 컬럼에 인덱스가 있는가 | 목록 API 지연, 중복 데이터 |
| naming convention | 제약 이름이 일관된가 | Alembic diff 불안정 |
| 기본값 위치 | `default`와 `server_default` 중 어디서 채우는가 | 환경별 값 불일치 |
| 표현 규칙 | `__repr__`과 하이브리드 속성이 디버깅에 충분한가 | 온콜 디버깅 지연 |

작아 보이지만 이런 점검표가 모델 계층의 장기 품질을 좌우합니다.

## 처음 질문으로 돌아가기

- **`DeclarativeBase`는 어떤 역할을 하고 왜 `MetaData`와 함께 묶일까요?**
  - `DeclarativeBase`는 ORM 모델들의 공통 부모이면서 `Base.metadata`를 품은 그릇이라서, 모델 클래스를 선언하는 순간 내부 `Table`이 같은 카탈로그에 등록됩니다. 그래서 ORM으로 정의한 `User`와 `Order`도 결국 `Base.metadata.create_all(engine)` 한 번으로 생성되며, naming convention도 이 지점에서 함께 통일됩니다.
- **`Mapped[T]`와 `mapped_column`은 타입 힌트, 컬럼 정의와 어떻게 연결될까요?**
  - `Mapped[int] = mapped_column(primary_key=True)`는 파이썬 타입 힌트와 SQL 컬럼 정의를 한 줄에 묶어 주고, `Mapped[str | None]`처럼 `None`이 포함되면 nullable 의도도 함께 드러납니다. 본문에서 `email`, `nickname`, `String(255)` 예시로 보여 준 것처럼, ORM 모델 정의가 사실상 Core `Column(...)`을 더 읽기 좋게 감싼 형태입니다.
- **`__tablename__`, `__table_args__`, `repr`는 언제부터 필요해질까요?**
  - `__tablename__`은 자동 추론에 맡기지 않고 테이블 이름을 고정할 때 바로 필요하고, `__table_args__`는 `UniqueConstraint`, `Index`, `sqlite_autoincrement` 같은 제약을 모델 옆에 명시할 때 중요해집니다. `__repr__`은 `User(id=..., email=...)`처럼 객체 로그를 바로 읽게 해 주므로, Session과 디버깅이 많아지는 순간부터 비용 대비 효과가 큽니다.

<!-- toc:begin -->
## 시리즈 목차

- [SQLAlchemy 101 (1/10): SQLAlchemy 2.x 시작하기 - Engine과 Connection의 본질](./01-sqlalchemy-2x-engine-connection.md)
- [SQLAlchemy 101 (2/10): SQLAlchemy Core - MetaData, Table, Column으로 schema를 Python 객체로 만들기](./02-core-metadata-table-types.md)
- [SQLAlchemy 101 (3/10): SQLAlchemy Core - select·insert·update·delete를 2.x style로 다루기](./03-core-select-insert-update-delete.md)
- **SQLAlchemy 101 (4/10): ORM 기초: DeclarativeBase와 mapped_column으로 모델 정의하기 (현재 글)**
- SQLAlchemy 101 (5/10): Session 깊이 보기: Unit of Work와 Identity Map의 동작 원리 (예정)
- SQLAlchemy 101 (6/10): ORM 관계 매핑: relationship과 back_populates로 양방향 탐색 안전하게 잇기 (예정)
- SQLAlchemy 101 (7/10): 로딩 전략과 N+1 문제: lazy/joined/selectin을 언제 골라야 하는가 (예정)
- SQLAlchemy 101 (8/10): 이벤트, hybrid_property, 그리고 커스텀 타입 (예정)
- SQLAlchemy 101 (9/10): 비동기 SQLAlchemy: aiosqlite와 AsyncSession (예정)
- SQLAlchemy 101 (10/10): 프로덕션 패턴: 풀, 관측, 마이그레이션, 배포 (예정)

<!-- toc:end -->

## 참고 자료

- [SQLAlchemy 2.x ORM Quick Start](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)
- [Declarative Mapping with `DeclarativeBase`](https://docs.sqlalchemy.org/en/20/orm/declarative_styles.html)
- [`mapped_column()` API reference](https://docs.sqlalchemy.org/en/20/orm/mapping_api.html#sqlalchemy.orm.mapped_column)
- [Naming conventions in MetaData](https://docs.sqlalchemy.org/en/20/core/constraints.html#configuring-constraint-naming-conventions)

## 정리와 다음 글

ORM의 출발점은 단순합니다. `DeclarativeBase`는 `MetaData`를 품은 그릇이고, `Mapped[T]`는 컬럼의 SQL 타입과 nullable 여부를 한 번에 표현하며, `mapped_column(...)`은 Core의 `Column(...)`을 타입 힌트와 결합한 헬퍼입니다. 이 세 도구로 정의한 모델은 그대로 `Base.metadata.create_all(engine)`으로 SQLite 스키마가 됩니다. 다음 글에서는 이 모델 위에서 `Session`이 어떻게 객체 변경을 추적하고, Unit of Work와 Identity Map이 어떤 식으로 SQL을 묶어 주는지 자세히 다룹니다.

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/sqlalchemy-101/ko)

Tags: Python, SQLAlchemy, ORM, Database
