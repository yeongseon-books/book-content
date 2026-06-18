---
series: sqlalchemy-101
episode: 5
title: "바이브코딩을 위한 SQLAlchemy (5/10): Session 깊이 보기: Unit of Work와 Identity Map의 동작 원리"
status: publish-ready
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - SQLAlchemy
  - Session
  - ORM
  - Python
---

# 바이브코딩을 위한 SQLAlchemy (5/10): Session 깊이 보기: Unit of Work와 Identity Map의 동작 원리

이 글은 "바이브코딩을 위한 SQLAlchemy" 시리즈의 다섯 번째 글입니다. Session은 SQLAlchemy ORM의 핵심이지만, 내부 동작을 모르면 AI가 생성한 코드에서 데이터가 저장되지 않거나, 같은 객체가 두 번 조회되거나, 예상치 못한 시점에 SQL이 실행되는 문제가 발생합니다.

---

## 바이브코딩 현장에서 이 문제가 왜 생기는가

AI에게 "FastAPI에서 SQLAlchemy Session 사용 예제 작성해 줘"라고 하면 대부분의 코드는 동작합니다. 하지만 실제 운영 환경에서는 트랜잭션이 의도치 않게 열린 채 남아 있거나, 객체 변경이 반영되지 않는 문제가 생깁니다.

이유는 Unit of Work와 Identity Map을 이해하지 못해서입니다. Session은 단순한 연결 래퍼가 아닙니다. 변경 추적기이자 객체 캐시입니다. `session.add()`는 즉시 INSERT하지 않습니다. `session.commit()`이 호출될 때 쌓인 변경사항을 한 번에 처리합니다. 이것이 Unit of Work입니다.

Identity Map은 같은 트랜잭션 안에서 동일한 ID의 객체를 한 번만 조회하게 해 줍니다. `session.get(User, 1)`을 두 번 호출해도 SQL은 한 번만 실행됩니다. 이 덕분에 캐시 불일치 버그가 줄어들지만, 오래된 데이터를 보게 될 수도 있습니다.

`flush()`는 변경사항을 SQL로 변환해 데이터베이스로 보내지만 커밋하지 않습니다. `commit()` 전에 생성된 ID를 알아야 할 때 사용합니다.

> "Session은 단순한 데이터베이스 연결이 아닙니다. 변경사항의 무대 뒤 감독자입니다. 막이 내려야(commit) 관객이 봅니다."

---

## 이 글에서 답할 질문 5가지

1. `session.add()`를 호출하면 즉시 SQL이 실행되나요?
2. `flush()`와 `commit()`의 차이는 무엇인가요?
3. Identity Map이 왜 캐시 불일치를 일으킬 수 있나요?
4. Session을 FastAPI와 함께 사용할 때 어떤 패턴이 좋은가요?
5. `session.expire_on_commit`은 언제 중요해지나요?

---

## Session 핵심 개념

### Session 생성과 사용

```python
from sqlalchemy.orm import Session

with Session(engine) as session:
    user = User(name="Alice", email="alice@example.com")
    session.add(user)
    session.commit()  # 이 시점에 INSERT 실행
    print(user.id)    # commit 후 ID 사용 가능
```

### flush vs commit

```python
with Session(engine) as session:
    user = User(name="Bob")
    session.add(user)
    session.flush()       # SQL 실행, 트랜잭션은 유지
    print(user.id)        # flush 후 ID 사용 가능
    post = Post(user_id=user.id, title="Hello")
    session.add(post)
    session.commit()      # 전체 트랜잭션 커밋
```

### Identity Map

```python
with Session(engine) as session:
    user1 = session.get(User, 1)  # SELECT 실행
    user2 = session.get(User, 1)  # SQL 없음, 캐시 반환
    assert user1 is user2         # True
```

### sessionmaker 팩토리 패턴

```python
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# FastAPI 의존성 주입 패턴
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## Before / After 비교

| 항목 | Before (잘못된 패턴) | After (올바른 패턴) |
| --- | --- | --- |
| Session 생성 | 요청마다 `Session(engine)` 직접 생성 | `sessionmaker`로 팩토리 사용 |
| 변경 반영 | `add()` 직후 완료로 오해 | `commit()` 후 반영 확인 |
| 연결 관리 | `close()` 수동 호출 누락 | `with` 구문 사용 |
| ID 접근 | `add()` 직후 ID 접근 | `flush()` 또는 `commit()` 후 접근 |

---

## 자주 하는 실수

| 실수 | 원인 | 해결 |
| --- | --- | --- |
| `add()` 후 바로 ID 접근 | Unit of Work 오해 | `flush()` 후 접근 |
| Session 닫지 않음 | 연결 풀 소진 | `with` 또는 `finally: db.close()` |
| 오래된 데이터 조회 | Identity Map 캐시 | `session.expire(obj)` 또는 새 Session |
| `autoflush` 동작 오해 | 자동 flush 시점 불명확 | `autoflush=False`로 명시적 제어 |

---

## AI 활용 팁

> "FastAPI와 SQLAlchemy ORM을 사용하는 CRUD 라우터를 작성해 줘. `sessionmaker`로 Session 팩토리를 만들고, 의존성 주입으로 Session을 관리해 줘. `autocommit=False, autoflush=False` 설정을 포함해 줘."

생성된 코드 확인 포인트:
- Session이 `with` 구문이나 `finally`로 닫히는지
- `commit()` 없이 변경사항을 저장하려는 코드 여부
- `add()` 직후 ID를 읽으려는 코드 여부

---

## 체크리스트

- [ ] Session은 요청당 하나를 원칙으로 생성하는가
- [ ] `with Session()` 또는 `try/finally`로 Session을 닫는가
- [ ] 쓰기 후 `commit()`을 명시적으로 호출하는가
- [ ] `flush()` 후 생성된 ID를 안전하게 접근하는가
- [ ] FastAPI에서 `get_db()` 의존성 패턴을 사용하는가

---

## 처음 질문으로 돌아가기

**`session.add()` 후 바로 ID를 읽을 수 있나요?**
아닙니다. `flush()` 또는 `commit()` 후에 ID가 채워집니다.

**`flush()`와 `commit()`은 언제 구분해야 하나요?**
같은 트랜잭션 내에서 INSERT 후 생성된 ID를 참조해야 할 때 `flush()`를 먼저 사용합니다.

---

## 정리

Session은 변경 추적기(Unit of Work)이자 객체 캐시(Identity Map)입니다. `add()`는 즉시 SQL을 실행하지 않고, `commit()` 시점에 모든 변경을 한 번에 처리합니다. 다음 글에서는 ORM 관계(relationship)와 back_populates를 살펴봅니다.

---

## 참고 자료

- [SQLAlchemy Session Basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- [SQLAlchemy Unit of Work Pattern](https://docs.sqlalchemy.org/en/20/orm/session_state_management.html)

---

<!-- toc:begin -->
## 시리즈 목차

1. 바이브코딩을 위한 SQLAlchemy (1/10): Engine과 Connection의 본질
2. 바이브코딩을 위한 SQLAlchemy (2/10): MetaData, Table, Column으로 schema를 Python 객체로 만들기
3. 바이브코딩을 위한 SQLAlchemy (3/10): select·insert·update·delete를 2.x style로 다루기
4. 바이브코딩을 위한 SQLAlchemy (4/10): DeclarativeBase와 mapped_column으로 모델 정의하기
5. **바이브코딩을 위한 SQLAlchemy (5/10): Session 깊이 보기: Unit of Work와 Identity Map의 동작 원리 (현재 글)**
6. 바이브코딩을 위한 SQLAlchemy (6/10): relationship과 back_populates로 양방향 탐색 안전하게 잇기
7. 바이브코딩을 위한 SQLAlchemy (7/10): 로딩 전략과 N+1 문제: lazy/joined/selectin을 언제 골라야 하는가
8. 바이브코딩을 위한 SQLAlchemy (8/10): 이벤트, hybrid_property, 그리고 커스텀 타입
9. 바이브코딩을 위한 SQLAlchemy (9/10): 비동기 SQLAlchemy: aiosqlite와 AsyncSession
10. 바이브코딩을 위한 SQLAlchemy (10/10): 프로덕션 패턴: 풀, 관측, 마이그레이션, 배포
<!-- toc:end -->

Tags: 바이브코딩, SQLAlchemy, Session, ORM, Python
