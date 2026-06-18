---
series: sqlalchemy-101
episode: 4
title: "바이브코딩을 위한 SQLAlchemy (4/10): DeclarativeBase와 mapped_column으로 모델 정의하기"
status: publish-ready
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - SQLAlchemy
  - ORM
  - Python
  - Database
---

# 바이브코딩을 위한 SQLAlchemy (4/10): DeclarativeBase와 mapped_column으로 모델 정의하기

이 글은 "바이브코딩을 위한 SQLAlchemy" 시리즈의 네 번째 글입니다. AI가 생성하는 ORM 모델 코드는 SQLAlchemy 버전에 따라 스타일이 크게 다릅니다. 2.x의 `DeclarativeBase`와 `Mapped[T]`, `mapped_column`을 이해하면, 생성된 코드가 최신 방식인지 구형인지 즉시 판단할 수 있습니다.

---

## 바이브코딩 현장에서 이 문제가 왜 생기는가

"SQLAlchemy ORM 모델 작성해 줘"라고 하면 AI는 `declarative_base()`(1.x 스타일)나 `DeclarativeBase`(2.x 스타일) 중 하나를 씁니다. 때로는 `Column`(구형)과 `mapped_column`(신형)이 섞인 코드도 나옵니다.

문제는 구형 스타일이 동작하기 때문에 바로 발견되지 않는다는 점입니다. `Column` 대신 `mapped_column`을 써야 타입 검사기(mypy, pyright)가 ORM 모델의 속성 타입을 올바르게 추론할 수 있습니다. `Mapped[int]`로 선언하면 `user.id`가 항상 `int`라는 사실을 정적 분석이 보장합니다.

`DeclarativeBase`를 상속한 클래스는 Python 클래스이면서 동시에 데이터베이스 테이블 매핑입니다. `__tablename__`으로 테이블 이름을 지정하고, `mapped_column`으로 컬럼을 선언합니다.

`Optional[str]`로 선언된 컬럼은 nullable이고, `str`만 있으면 NOT NULL입니다. 타입 어노테이션이 곧 데이터베이스 제약 조건이 됩니다.

> "ORM 모델은 Python 클래스와 데이터베이스 테이블의 거울입니다. 2.x에서 타입 어노테이션은 단순한 힌트가 아니라 스키마 계약입니다."

---

## 이 글에서 답할 질문 5가지

1. `DeclarativeBase`와 `declarative_base()`는 무엇이 다른가요?
2. `Mapped[T]`와 `mapped_column`은 왜 함께 써야 하나요?
3. `Optional[str]`과 `str`은 데이터베이스에서 어떻게 다른가요?
4. `__tablename__` 외에 어떤 클래스 레벨 설정이 있나요?
5. 여러 모델에서 공통 컬럼을 공유하려면 어떻게 하나요?

---

## ORM 모델 정의 핵심 개념

### DeclarativeBase 상속

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

`Base`는 모든 ORM 모델이 상속할 기반 클래스입니다. 내부에 MetaData가 있어 모든 모델의 테이블 정보를 관리합니다.

### Mapped[T]와 mapped_column

```python
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(200), unique=True)
```

`Mapped[int]`는 NOT NULL 정수, `Mapped[Optional[str]]`는 nullable 문자열을 의미합니다.

### Mixin으로 공통 컬럼 공유

```python
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, func

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

class User(TimestampMixin, Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
```

---

## Before / After 비교

| 항목 | Before (1.x 스타일) | After (2.x 스타일) |
| --- | --- | --- |
| 기반 클래스 | `declarative_base()` | `class Base(DeclarativeBase)` |
| 컬럼 선언 | `Column(Integer, ...)` | `Mapped[int] = mapped_column(...)` |
| nullable 표현 | `Column(String, nullable=True)` | `Mapped[Optional[str]]` |
| 타입 추론 | 런타임만 | 정적 분석 지원 |

---

## 자주 하는 실수

| 실수 | 원인 | 해결 |
| --- | --- | --- |
| `Column` 유지 | 1.x 습관 | `mapped_column`으로 교체 |
| `Optional` 누락 | nullable 의도 불명확 | `Mapped[Optional[T]]`로 명시 |
| `declarative_base()` 사용 | 구형 API | `DeclarativeBase` 상속 |
| 타입 어노테이션 없이 `mapped_column` | 타입 추론 불가 | `Mapped[T]`와 함께 사용 |

---

## AI 활용 팁

> "SQLAlchemy 2.x ORM 방식으로, `DeclarativeBase`를 상속하고 `Mapped[T]`와 `mapped_column`을 사용하는 User 모델을 작성해 줘. nullable 컬럼은 `Mapped[Optional[str]]`로 표현하고, 타임스탬프 Mixin도 포함해 줘."

생성된 코드 확인 포인트:
- `declarative_base()` 사용 여부(구형 API)
- `Column` 대신 `mapped_column` 사용 여부
- `Mapped[T]` 어노테이션 유무

---

## 체크리스트

- [ ] `DeclarativeBase`를 상속한 `Base` 클래스를 사용하는가
- [ ] `Mapped[T]`와 `mapped_column`을 함께 사용하는가
- [ ] nullable 컬럼에 `Mapped[Optional[T]]`를 사용하는가
- [ ] `Base.metadata.create_all(engine)`으로 테이블을 생성하는가
- [ ] 공통 컬럼은 Mixin 패턴으로 분리했는가

---

## 처음 질문으로 돌아가기

**`declarative_base()`를 계속 써도 되나요?**
동작하지만 2.x에서는 `DeclarativeBase` 상속이 권장됩니다. 타입 검사기 지원이 더 잘됩니다.

**`Mapped[T]`를 꼭 써야 하나요?**
필수는 아니지만, mypy와 pyright가 ORM 모델 속성의 타입을 올바르게 추론하려면 `Mapped[T]`가 필요합니다.

---

## 정리

`DeclarativeBase`와 `Mapped[T]`, `mapped_column`은 SQLAlchemy 2.x ORM의 표준 방식입니다. 타입 어노테이션이 스키마 계약이 되어 정적 분석 도구와 잘 연동됩니다. 다음 글에서는 Session의 Unit of Work 패턴과 Identity Map을 살펴봅니다.

---

## 참고 자료

- [SQLAlchemy ORM Mapping](https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html)
- [SQLAlchemy Mapped Column](https://docs.sqlalchemy.org/en/20/orm/mapping_columns.html)

---

<!-- toc:begin -->
## 시리즈 목차

1. 바이브코딩을 위한 SQLAlchemy (1/10): Engine과 Connection의 본질
2. 바이브코딩을 위한 SQLAlchemy (2/10): MetaData, Table, Column으로 schema를 Python 객체로 만들기
3. 바이브코딩을 위한 SQLAlchemy (3/10): select·insert·update·delete를 2.x style로 다루기
4. **바이브코딩을 위한 SQLAlchemy (4/10): DeclarativeBase와 mapped_column으로 모델 정의하기 (현재 글)**
5. 바이브코딩을 위한 SQLAlchemy (5/10): Session 깊이 보기: Unit of Work와 Identity Map의 동작 원리
6. 바이브코딩을 위한 SQLAlchemy (6/10): relationship과 back_populates로 양방향 탐색 안전하게 잇기
7. 바이브코딩을 위한 SQLAlchemy (7/10): 로딩 전략과 N+1 문제: lazy/joined/selectin을 언제 골라야 하는가
8. 바이브코딩을 위한 SQLAlchemy (8/10): 이벤트, hybrid_property, 그리고 커스텀 타입
9. 바이브코딩을 위한 SQLAlchemy (9/10): 비동기 SQLAlchemy: aiosqlite와 AsyncSession
10. 바이브코딩을 위한 SQLAlchemy (10/10): 프로덕션 패턴: 풀, 관측, 마이그레이션, 배포
<!-- toc:end -->

Tags: 바이브코딩, SQLAlchemy, ORM, Python, Database
