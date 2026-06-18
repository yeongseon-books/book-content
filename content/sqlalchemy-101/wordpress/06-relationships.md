---
series: sqlalchemy-101
episode: 6
title: "바이브코딩을 위한 SQLAlchemy (6/10): relationship과 back_populates로 양방향 탐색 안전하게 잇기"
status: publish-ready
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - SQLAlchemy
  - ORM
  - Relationships
  - Python
---

# 바이브코딩을 위한 SQLAlchemy (6/10): relationship과 back_populates로 양방향 탐색 안전하게 잇기

이 글은 "바이브코딩을 위한 SQLAlchemy" 시리즈의 여섯 번째 글입니다. ORM 관계 설정은 AI가 생성한 코드에서 가장 자주 잘못 설정되는 부분입니다. `backref`와 `back_populates`의 차이, cascade 설정의 의미, 다대다 관계의 연결 테이블 처리 방법을 이해해야 관계 코드를 올바르게 검증할 수 있습니다.

---

## 바이브코딩 현장에서 이 문제가 왜 생기는가

"User와 Post 사이의 일대다 관계를 SQLAlchemy ORM으로 구현해 줘"라고 하면 동작하는 코드를 받습니다. 하지만 `backref`를 쓴 경우와 `back_populates`를 쓴 경우의 동작이 미묘하게 다릅니다. `cascade="all, delete-orphan"`을 잘못 설정하면 연결 객체를 삭제할 때 예상치 못한 cascade가 일어납니다.

더 복잡한 문제는 관계가 로드되지 않은 상태에서 접근할 때입니다. Lazy loading이 기본값이라 Session 밖에서 `user.posts`에 접근하면 `DetachedInstanceError`가 발생합니다. 이 오류를 AI에게 수정해달라고 하면 종종 근본 원인이 아닌 임시방편 코드가 나옵니다.

`back_populates`는 양방향 관계의 양쪽을 명시적으로 연결합니다. 코드를 읽는 사람이 관계의 양쪽을 바로 파악할 수 있어 `backref`보다 권장됩니다. 다음 글의 로딩 전략과 함께 이해해야 관계를 안전하게 다룰 수 있습니다.

> "relationship은 테이블 간의 약속입니다. back_populates는 그 약속을 양쪽이 모두 서명한 계약서로 만듭니다."

---

## 이 글에서 답할 질문 5가지

1. `backref`와 `back_populates`의 차이는 무엇인가요?
2. `cascade="all, delete-orphan"`은 언제 써야 하나요?
3. 다대다 관계는 어떻게 모델링하나요?
4. `DetachedInstanceError`는 왜 발생하고 어떻게 예방하나요?
5. `ForeignKey`와 `relationship`은 어떻게 연결되나요?

---

## relationship 핵심 개념

### 일대다 관계

```python
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    posts: Mapped[list["Post"]] = relationship(
        "Post", back_populates="author"
    )

class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship("User", back_populates="posts")
```

### cascade 설정

```python
# User 삭제 시 Post도 삭제
posts: Mapped[list["Post"]] = relationship(
    "Post",
    back_populates="author",
    cascade="all, delete-orphan"
)
```

`cascade="all, delete-orphan"`은 부모 객체 삭제 시 자식을 함께 삭제합니다. 연결 테이블의 중간 객체에는 사용하지 않아야 합니다.

### 다대다 관계

```python
from sqlalchemy import Table, Column, Integer, ForeignKey

post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id")),
    Column("tag_id", Integer, ForeignKey("tags.id")),
)

class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    tags: Mapped[list["Tag"]] = relationship(
        "Tag", secondary=post_tags, back_populates="posts"
    )
```

---

## Before / After 비교

| 항목 | Before (문제 있는 패턴) | After (올바른 패턴) |
| --- | --- | --- |
| 양방향 선언 | `backref` 단독 사용 | `back_populates` 명시적 선언 |
| cascade | 미설정 또는 과도한 설정 | 의도에 맞게 명시적 설정 |
| 관계 접근 | Session 밖에서 lazy load | Session 안에서 접근 또는 eager load |
| 다대다 | 수동 SQL로 연결 관리 | `secondary` 테이블 설정 |

---

## 자주 하는 실수

| 실수 | 원인 | 해결 |
| --- | --- | --- |
| `DetachedInstanceError` | Session 밖에서 lazy load | `selectinload` 또는 Session 안에서 접근 |
| cascade 과다 적용 | `delete-orphan` 남용 | 관계 의미에 맞게 선택 |
| `back_populates` 불일치 | 한쪽만 선언 | 양쪽 모두 일치하게 선언 |
| 다대다 중간 테이블 누락 | ORM만으로 해결하려 함 | `secondary` 테이블 명시 |

---

## AI 활용 팁

> "SQLAlchemy 2.x ORM으로 User와 Post 일대다 관계, Post와 Tag 다대다 관계를 작성해 줘. `back_populates`를 사용하고, User 삭제 시 Post가 cascade 삭제되도록 설정해 줘."

생성된 코드 확인 포인트:
- `backref` 대신 `back_populates` 사용 여부
- `back_populates` 양쪽 이름이 일치하는지
- cascade 설정이 의도에 맞는지

---

## 체크리스트

- [ ] 양방향 관계에 `back_populates`를 사용하는가
- [ ] `back_populates` 양쪽의 attribute 이름이 서로 맞는가
- [ ] cascade가 의도한 삭제 동작을 하는가
- [ ] 다대다에 `secondary` 테이블이 설정되었는가
- [ ] Session 밖에서 관계에 접근하지 않는가

---

## 처음 질문으로 돌아가기

**`backref`와 `back_populates`는 어떻게 다른가요?**
`backref`는 한쪽만 선언하면 반대쪽이 자동 생성됩니다. `back_populates`는 양쪽을 명시적으로 선언합니다. 가독성과 타입 추론 측면에서 `back_populates`가 권장됩니다.

**`DetachedInstanceError`를 어떻게 예방하나요?**
Session이 닫히기 전에 관계를 접근하거나, `selectinload` 등 eager loading을 사용하면 예방할 수 있습니다.

---

## 정리

`relationship`과 `back_populates`로 ORM 모델 간의 관계를 명시적으로 선언하면, 객체 그래프를 Python으로 자연스럽게 탐색할 수 있습니다. 다음 글에서는 이 관계가 로드되는 방식(lazy/joined/selectin)과 N+1 문제를 살펴봅니다.

---

## 참고 자료

- [SQLAlchemy Relationship Configuration](https://docs.sqlalchemy.org/en/20/orm/relationships.html)
- [SQLAlchemy Cascade](https://docs.sqlalchemy.org/en/20/orm/cascades.html)

---

<!-- toc:begin -->
## 시리즈 목차

1. 바이브코딩을 위한 SQLAlchemy (1/10): Engine과 Connection의 본질
2. 바이브코딩을 위한 SQLAlchemy (2/10): MetaData, Table, Column으로 schema를 Python 객체로 만들기
3. 바이브코딩을 위한 SQLAlchemy (3/10): select·insert·update·delete를 2.x style로 다루기
4. 바이브코딩을 위한 SQLAlchemy (4/10): DeclarativeBase와 mapped_column으로 모델 정의하기
5. 바이브코딩을 위한 SQLAlchemy (5/10): Session 깊이 보기: Unit of Work와 Identity Map의 동작 원리
6. **바이브코딩을 위한 SQLAlchemy (6/10): relationship과 back_populates로 양방향 탐색 안전하게 잇기 (현재 글)**
7. 바이브코딩을 위한 SQLAlchemy (7/10): 로딩 전략과 N+1 문제: lazy/joined/selectin을 언제 골라야 하는가
8. 바이브코딩을 위한 SQLAlchemy (8/10): 이벤트, hybrid_property, 그리고 커스텀 타입
9. 바이브코딩을 위한 SQLAlchemy (9/10): 비동기 SQLAlchemy: aiosqlite와 AsyncSession
10. 바이브코딩을 위한 SQLAlchemy (10/10): 프로덕션 패턴: 풀, 관측, 마이그레이션, 배포
<!-- toc:end -->

Tags: 바이브코딩, SQLAlchemy, ORM, Relationships, Python
