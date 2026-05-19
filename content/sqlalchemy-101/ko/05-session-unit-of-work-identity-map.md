---
title: 'Session 깊이 보기: Unit of Work와 Identity Map의 동작 원리'
series: sqlalchemy-101
episode: 5
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
- Session
- Unit of Work
- SQLite
last_reviewed: '2026-05-12'
seo_description: Session, Unit of Work, Identity Map이 어떻게 함께 동작하는지 설명합니다
---

# Session 깊이 보기: Unit of Work와 Identity Map의 동작 원리

ORM 모델을 정의했다고 해서 곧바로 안전한 데이터 작업이 되는 것은 아닙니다. 객체를 언제 INSERT하고, 변경을 언제 UPDATE로 모으고, 같은 행을 왜 같은 객체로 취급하는지 이해하려면 `Session`을 먼저 알아야 합니다.

이 글은 SQLAlchemy 101 시리즈의 다섯 번째 글입니다. 여기서는 `Session`, Unit of Work, Identity Map이 실제로 어떤 식으로 함께 움직이는지 정리합니다.

현업에서 `commit()` 뒤에 예상치 못한 SELECT가 한 번 더 나가거나, 같은 사용자를 읽었는데 객체 동일성이 맞지 않거나, 테스트에서 INSERT 직후 조회가 비는 문제는 대부분 이 계층의 오해에서 시작합니다. 이번 글은 그 오해를 풀기 위한 기준선을 만듭니다.

![Session 깊이 보기: Unit of Work와 Identity Map의 동작 원리](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/05/05-01-session-in-depth-how-unit-of-work-and-id.ko.png)

*Session 깊이 보기: Unit of Work와 Identity Map의 동작 원리*

## 이 글에서 다룰 문제

- `Session`은 단순한 connection 래퍼가 아니라 무엇을 관리할까요?
- Unit of Work는 변경을 어떻게 모으고, 언제 SQL로 내보낼까요?
- `flush()`와 `commit()`은 어떤 순서와 의미 차이가 있을까요?
- Identity Map은 왜 같은 PK를 같은 객체로 보장할까요?
- `expire_on_commit`, detached 객체, 세션 범위는 어디서 자주 사고가 날까요?

## 왜 중요한가

![핵심 개념](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/05/05-02-why-it-matters.ko.png)

*핵심 개념*
Session을 잘 이해하지 못한 채로 ORM을 쓰면 정체불명의 동작에 자주 부딪칩니다. 대표적인 예를 들면 다음과 같습니다.

- "분명히 `commit()`했는데 다른 함수에서 같은 객체의 속성에 접근하니 추가 SELECT가 한 번 더 나갑니다." → `expire_on_commit` 동작입니다.
- "한 함수에서 `select`로 가져온 user와 다른 함수에서 가져온 user가 다른 객체입니다." → Session이 다르거나, 같은 Session이어도 닫혀 버린 경우입니다.
- "테스트에서 데이터를 INSERT한 직후에 SELECT를 했는데 결과가 비어 있습니다." → 자동 flush 시점이나 트랜잭션 격리에 대한 오해입니다.
- "FastAPI 핸들러에서 `Session`을 모듈 전역으로 두었는데 동시 요청 시 이상한 데이터가 섞입니다." → Session은 요청 단위 자원으로 다뤄야 합니다.

이런 문제들은 모두 "Session이 어떤 객체를 들고 있고, 언제 SQL을 보내는가"라는 한 가지 질문으로 수렴합니다. 그 질문에 답하려면 Unit of Work와 Identity Map을 알아야 합니다.

## 멘탈 모델

![Mental model](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/05/05-03-mental-model.ko.png)

*멘탈 모델*
> `Session`은 작업 메모지(Unit of Work)와 캐시 노트(Identity Map)를 한 권의 노트로 묶어 둔 것입니다. 노트가 열려 있는 동안은 같은 PK의 행을 같은 객체로 다루고, 노트를 덮을 때(`commit`)에 모든 변경을 한 번에 SQL로 보냅니다.

상태 전이를 그림으로 보면 다음과 같습니다.

```text
[transient]   → session.add()    → [pending]
[pending]     → session.flush()  → [persistent]   (SQL INSERT 발사)
[persistent]  → session.delete() → [deleted]
[deleted]     → session.flush()  → [persistent×]  (SQL DELETE 발사)
[persistent]  → session.expunge()/session 종료 → [detached]
```

여기서 먼저 볼 점은 두 가지입니다.

- "Session에 등록되어 있는가"가 transient/pending/persistent를 가르는 기준입니다.
- "그 객체가 가리키는 행이 데이터베이스에 존재하는가"는 SQL이 실제로 발사된 후에야 확정됩니다.

## 핵심 개념

![핵심 개념](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/05/05-04-core-concepts.ko.png)

*핵심 개념*
### 1) Session은 트랜잭션의 컨텍스트입니다

`Session`은 내부적으로 하나의 트랜잭션을 들고 있고, `commit()` 또는 `rollback()`이 그 트랜잭션을 종료합니다.

```python
from sqlalchemy.orm import Session

with Session(engine) as session:
    user = User(email="alice@example.com")
    session.add(user)
    session.commit()       # 이 시점까지가 한 트랜잭션
```

`with` 블록을 빠져나가면 자동으로 `close()`가 호출되어 커넥션이 풀로 반환됩니다 (Ep1의 connection pool 참고). 핸들러 한 번 = Session 한 번 = 트랜잭션 한 번이 가장 단순한 모델입니다.

### 2) Unit of Work: 변경을 모아 두었다가 한 번에 보냅니다

`session.add(obj)`는 즉시 INSERT를 실행하지 않습니다. 대신 Session의 "pending" 영역에 객체를 등록해 둡니다. 진짜 SQL은 다음 두 시점에 발사됩니다.

- `session.flush()`를 명시적으로 호출할 때
- 다음 query/`commit()` 직전에 자동으로 (autoflush=True 기본값)

```python
with Session(engine) as session:
    a = User(email="a@x.com")
    b = User(email="b@x.com")
    session.add(a)
    session.add(b)
    # 아직 SQL 없음 — 두 객체는 pending 상태
    session.flush()
    # 여기서 INSERT 두 건이 한 번에 발사됨, a.id / b.id 가 채워짐
    session.commit()
    # 트랜잭션 커밋
```

이 묶음 처리가 Unit of Work의 중심 동작입니다. 100개의 객체를 INSERT하면 100번의 왕복 호출 대신 한 번의 INSERT로 묶이며, 그 사이에 발생한 UPDATE와 DELETE도 의존성 순서를 고려해 순서가 결정됩니다.

### 3) flush와 commit의 차이

| 동작 | flush | commit |
| --- | --- | --- |
| SQL 발사 | 예 (INSERT/UPDATE/DELETE) | 예 (필요 시 flush 후 COMMIT) |
| 트랜잭션 종료 | 아니오 | 예 (`COMMIT;`) |
| Identity Map 변화 | 새 PK가 채워짐 | `expire_on_commit=True`면 모든 객체 만료 |
| 사용 시점 | PK가 즉시 필요할 때 (외래키 참조 등) | 작업 단위 종료 |

flush는 "지금까지의 변경을 SQL로 내보내라"이고, commit은 "트랜잭션을 끝내라"입니다. commit은 보통 내부적으로 flush를 먼저 호출합니다.

### 4) Identity Map: 같은 PK는 같은 객체

```python
with Session(engine) as session:
    u1 = session.get(User, 1)
    u2 = session.get(User, 1)
    assert u1 is u2          # True — 같은 객체
```

같은 Session 안에서 PK 1번 User를 두 번 조회해도 데이터베이스 SELECT는 한 번만 일어납니다. 두 번째 조회는 Identity Map(파이썬 dict)에서 곧장 반환됩니다. 이 보장 덕분에 ORM 코드에서는 "같은 행을 가리키는 두 객체가 다른 값을 갖는" 일이 일어나지 않습니다.

다만 Session이 다르면 Identity Map도 다르므로, 다른 Session에서 받은 두 객체는 `is` 비교에서 False입니다. 동등성은 PK 비교(`u1.id == u2.id`)로 판정해야 합니다.

### 5) expire_on_commit의 함정

기본값이 `True`이기 때문에, `commit()` 직후 모든 ORM 객체가 만료(expired) 상태가 됩니다. 이 상태에서 속성에 접근하면 자동으로 SELECT가 한 번 더 나갑니다.

```python
with Session(engine) as session:
    user = User(email="alice@example.com")
    session.add(user)
    session.commit()
    print(user.email)        # ← 여기서 SELECT 한 번 더
```

대부분의 웹 핸들러는 commit 직후에 응답을 만들면서 객체 속성을 다시 읽기 때문에, 이 추가 SELECT가 누적되면 성능에 영향을 줍니다. 필요에 따라 `Session(engine, expire_on_commit=False)`로 끌 수 있지만, 그러면 commit 후의 객체가 stale 상태가 될 수 있다는 점을 인지해야 합니다.

## 이전 방식과 개선 방식

### 이전: 손으로 변경 추적

```python
def update_email(conn, user_id, new_email):
    row = conn.execute(select(users).where(users.c.id == user_id)).first()
    if row is None:
        return
    if row.email == new_email:
        return                       # 변경 없음 → UPDATE 생략
    conn.execute(update(users).where(users.c.id == user_id).values(email=new_email))
```

변경이 있는지 직접 비교하고, UPDATE 문을 직접 만들어야 합니다. 컬럼이 늘어날수록 코드가 복잡해집니다.

### 개선 후: ORM Session에 맡기기

```python
def update_email(session, user_id, new_email):
    user = session.get(User, user_id)
    if user is None:
        return
    user.email = new_email           # 속성 변경만 — Session이 dirty로 표시
    # 함수 종료 후 commit() 시점에 Session이 자동으로 UPDATE 발사
```

Session은 어떤 속성이 변경되었는지 추적해 두고, flush 시 변경된 컬럼만 골라 UPDATE를 만듭니다. 변경이 없으면 UPDATE 자체가 생략됩니다.

## 단계별 실습

![단계별 실습](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/05/05-05-step-by-step-walkthrough.ko.png)

*단계별 실습*
다음 코드를 한 파일에 저장해 실행하면 Session이 만드는 SQL과 Identity Map의 동작을 한 번에 관찰할 수 있습니다.

```python
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

engine = create_engine("sqlite:///session_demo.db", echo=True, future=True)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r})"

def main() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        a = User(email="a@example.com")
        b = User(email="b@example.com")
        session.add_all([a, b])
        print("before flush, a.id =", a.id)         # None
        session.flush()
        print("after flush, a.id =", a.id)          # 1
        session.commit()

    with Session(engine) as session:
        u1 = session.get(User, 1)
        u2 = session.get(User, 1)
        print("u1 is u2 ?", u1 is u2)               # True

        u1.email = "alice@example.com"
        # 아직 SQL 없음 — dirty로만 표시
        session.commit()
        # 여기서 UPDATE users SET email=... WHERE id=1 한 줄

if __name__ == "__main__":
    main()
```

`echo=True`로 켜 두면 어느 시점에 어떤 SQL이 나가는지 콘솔에서 직접 확인할 수 있습니다. 처음 ORM을 익힐 때는 이 옵션을 켜 두고 한 줄 한 줄 의도와 SQL을 맞춰 보는 편을 강력히 권합니다.

## 자주 하는 실수

### 1) 모듈 전역 Session 공유

```text
session = Session(engine)         # 모듈 로드 시 한 번 생성

def handler(...):
    user = session.get(User, 1)   # 동시 요청에서 같은 Session 사용 — 위험
```

`Session`은 스레드 안전하지 않습니다. 웹 서버에서는 요청 단위로 새 `Session`을 만들고 끝나면 닫아야 합니다. 패턴은 보통 `sessionmaker`나 의존성 주입 컨테이너로 캡슐화합니다.

```python
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def handler():
    with SessionLocal() as session:
        ...
```

### 2) commit 후 detach된 객체 사용

```python
with Session(engine) as session:
    user = session.get(User, 1)

print(user.email)        # DetachedInstanceError 가능성
```

`with` 블록을 빠져나오는 순간 user는 detached 상태가 되고, 만료된 속성에 접근하면 오류가 납니다. 응답 직전에 필요한 속성을 미리 읽어 두거나, `expire_on_commit=False`를 활용하면 완화할 수 있습니다.

### 3) `flush=False`로 가정한 채 query 호출

기본은 autoflush=True이므로, query 직전에 pending 변경이 자동으로 SQL로 나갑니다. "테스트에서 INSERT 직후 SELECT가 비어 있다"라는 증상은 보통 query를 다른 Session에서 실행하기 때문입니다. 같은 Session에서라면 autoflush가 처리해 줍니다.

### 4) commit 안 하고 with 블록 종료

```python
with Session(engine) as session:
    session.add(User(email="x@y.com"))
# commit 호출 없음 → 트랜잭션이 ROLLBACK 됨
```

`Session`의 컨텍스트 매니저는 commit을 자동으로 호출하지 않습니다. 의도적으로 명시적인 `commit()` 호출이 필요합니다. 변경 작업을 했으면 반드시 commit이나 rollback을 호출해야 합니다.

### 5) 다른 Session 객체끼리 `is` 비교

다른 Session에서 같은 PK 1번 user를 가져왔다면 `u1 is u2`는 False입니다. Identity Map은 Session 단위입니다. 동등성은 항상 PK 또는 비즈니스 키로 비교해야 합니다.

## 실무에서 자주 만나는 상황

- **요청 단위 Session**: FastAPI에서는 `Depends`로 `SessionLocal()` 컨텍스트를 열고 응답 종료 시 닫는 패턴을 사용합니다. Session 생성 비용은 거의 없으며, 진짜 비용은 커넥션 획득에 있습니다 (Ep1 pool 참고).
- **Read 전용 트랜잭션**: 읽기만 하는 핸들러는 `expire_on_commit=False`와 짧은 트랜잭션이면 충분합니다. 명시적 commit 없이 `with` 블록 종료로 정리해도 됩니다.
- **벌크 작업**: 수만 건 INSERT는 ORM 객체보다 Core `insert(table)`이나 `Session.execute(insert(User), [{...}, ...])`처럼 stmt 기반 벌크가 빠릅니다. ORM의 dirty 추적 비용이 사라집니다.
- **트랜잭션 외부의 객체 사용**: 응답 직전에 객체 속성을 미리 dict로 변환해 두면, detached 상태와 무관하게 직렬화할 수 있습니다.
- 테스트: 각 테스트마다 SAVEPOINT를 활용해 빠르게 롤백하는 패턴(`Session(begin_nested=True)` 또는 `connection.begin()`을 감싸는 패턴)이 널리 쓰입니다.

## 체크리스트

- [ ] Session을 요청/작업 단위로 생성하고 닫는가?
- [ ] commit과 flush의 차이를 이해하고, 필요 시 명시적으로 호출하는가?
- [ ] `expire_on_commit` 동작이 응답 경로에 추가 SELECT를 만들지 점검했는가?
- [ ] 같은 Session 안에서만 `is` 비교를 사용하고, 그 외에는 PK로 비교하는가?
- [ ] 벌크 작업에서는 ORM 객체 대신 stmt 기반 INSERT를 검토했는가?
- [ ] `sessionmaker`로 Session 생성 정책을 한곳에 모았는가?

<!-- toc:begin -->
## 시리즈 목차

- [SQLAlchemy 2.x 시작하기 - Engine과 Connection의 본질](./01-sqlalchemy-2x-engine-connection.md)
- [SQLAlchemy Core - MetaData, Table, Column으로 schema를 Python 객체로 만들기](./02-core-metadata-table-types.md)
- [SQLAlchemy Core - select·insert·update·delete를 2.x style로 다루기](./03-core-select-insert-update-delete.md)
- [ORM 기초: DeclarativeBase와 mapped_column으로 모델 정의하기](./04-orm-declarative-mapped-column.md)
- **Session 깊이 보기: Unit of Work와 Identity Map의 동작 원리 (현재 글)**
- ORM 관계 매핑: relationship과 back_populates로 양방향 탐색 안전하게 잇기 (예정)
- 로딩 전략과 N+1 문제: lazy/joined/selectin을 언제 골라야 하는가 (예정)
- 이벤트, hybrid_property, 그리고 커스텀 타입 (예정)
- 비동기 SQLAlchemy: aiosqlite와 AsyncSession (예정)
- 프로덕션 패턴: 풀, 관측, 마이그레이션, 배포 (예정)

<!-- toc:end -->

## 참고 자료

- [SQLAlchemy 2.x ORM Session basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- [Unit of Work pattern in SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/session_state_management.html)
- [Identity Map](https://docs.sqlalchemy.org/en/20/glossary.html#term-identity-map)
- [`expire_on_commit` parameter](https://docs.sqlalchemy.org/en/20/orm/session_api.html#sqlalchemy.orm.Session.params.expire_on_commit)

## 정리와 다음 글

`Session`은 단순한 커넥션 래퍼가 아니라, 변경을 모아 두는 작업 메모지(Unit of Work)와 같은 PK를 같은 객체로 묶어 주는 캐시(Identity Map)를 함께 들고 있는 컨텍스트입니다. `add`는 pending 등록이고, 실제 SQL은 flush 시점에 발사되며, commit은 트랜잭션을 종료합니다. `expire_on_commit`은 편리하지만 commit 직후 추가 SELECT를 유발할 수 있고, 모듈 전역 Session 공유는 동시성 문제를 만들기 쉽습니다. 다음 글에서는 이 Session 위에서 관계(`relationship`)를 정의하고, `back_populates`로 양방향 탐색을 안전하게 잇는 법을 다룹니다.

Tags: Python, SQLAlchemy, ORM, Database
