---
series: backend-development-101
episode: 5
title: "Backend Development 101 (5/10): Database Layer"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Backend
  - Database
  - SQL
  - SQLAlchemy
  - Python
seo_description: Repository 패턴과 트랜잭션, migration, N+1 핵심을 정리합니다
last_reviewed: '2026-05-15'
---

# Backend Development 101 (5/10): Database Layer

service가 직접 SQL을 쓰기 시작하면 쿼리 중복과 데이터 접근 규칙의 분산이 빠르게 커집니다. 처음에는 편해 보여도 성능 조정, 캐시 추가, 테스트 격리 같은 작업이 모두 어려워집니다.

이 글은 Backend Development 101 시리즈의 다섯 번째 글입니다. 여기서는 repository pattern을 중심으로 database layer를 분리하고, ORM·migration·transaction·N+1까지 함께 정리해 보겠습니다.

## 먼저 던지는 질문

- 왜 service가 SQL을 직접 작성하지 않는 편이 좋을까요?
- repository pattern은 어떤 경계를 만들어 줄까요?
- ORM은 왜 편리하면서도 함정을 함께 가져올까요?

## 큰 그림

![Backend Development 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/backend-development-101/05/05-01-concept-at-a-glance.ko.png)

*Backend Development 101 5장 흐름 개요*

이 그림에서는 Database Layer를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> Database Layer의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

데이터베이스는 가장 자주 바뀌는 것 같지만, 실제로는 가장 조심스럽게 바꿔야 하는 영역입니다. 처음부터 레이어를 분리해 두면 데이터베이스를 바꾸거나 캐시를 끼우거나 테스트용 인메모리 엔진으로 교체하는 작업이 한곳에서 정리됩니다.

repository는 데이터베이스와 service 사이의 번역기 역할을 합니다. service는 도메인 언어로 말하고, repository는 그것을 SQL이나 ORM 호출로 바꿉니다. 이 경계가 있어야 시스템이 진화해도 나머지 층이 덜 흔들립니다.

> repository는 service의 도메인 언어를 데이터베이스 질의로 번역하는 경계입니다.

## 한눈에 보는 개념

service는 SQL을 몰라도 되고, repository만 데이터 접근 세부 구현을 알면 됩니다. 이 단순한 분리가 데이터 계층을 교체 가능한 형태로 만들어 줍니다.

## 핵심 용어

- **Repository**: 데이터베이스 접근을 함수 같은 메서드로 감싸는 객체입니다.
- **ORM**: 객체와 테이블을 연결해 주는 도구입니다.
- **Migration**: 스키마 변경을 코드로 버전 관리하는 방식입니다.
- **Transaction**: 함께 commit되거나 rollback되는 작업 단위입니다.
- **N+1**: 하나의 조회 뒤에 자식 데이터를 위해 N개의 쿼리가 더 나가는 대표적인 성능 함정입니다.

## Before/After

**Before (SQL inside the service)**

```python
def create_user(name):
    cur = db.execute("INSERT INTO users(name) VALUES(?)", (name,))
    return cur.lastrowid
```

**After (wrapped by a repository)**

```python
# repositories/user_repo.py
class UserRepository:
    def __init__(self, session):
        self.session = session

    def save(self, user):
        self.session.add(user)
        self.session.flush()
        return user
```

쿼리 변경은 이제 한 파일 안에서 끝납니다. service는 저장 방식이 바뀌어도 의미 있는 메서드만 계속 호출하면 됩니다.

## 실습: 다섯 단계로 보는 Database Layer

### Step 1 — SQLite + SQLAlchemy setup

```python
# 1_setup.py
from sqlalchemy import create_engine, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase): pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))

engine = create_engine("sqlite:///app.db")
Base.metadata.create_all(engine)
```

ORM을 쓰면 테이블과 객체 사이의 대응을 코드로 관리할 수 있습니다. 입문 단계에서는 SQL을 전혀 안 보게 만드는 도구가 아니라, 데이터 계층을 정리하는 도구로 이해하는 편이 좋습니다.

### Step 2 — Session and repository

```python
# 2_repo.py
from sqlalchemy.orm import Session

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, name: str) -> User:
        u = User(name=name)
        self.session.add(u)
        self.session.flush()
        return u

    def get(self, uid: int) -> User | None:
        return self.session.get(User, uid)
```

repository는 session을 받아 필요한 쿼리만 수행합니다. service는 add, get 같은 도메인 의미를 가진 메서드만 알면 됩니다.

### Step 3 — Transactions

```python
# 3_tx.py
from sqlalchemy.orm import Session
with Session(engine) as s, s.begin():
    repo = UserRepository(s)
    repo.add("Alice")
    repo.add("Bob")
# Exiting cleanly commits; an exception rolls back.
```

트랜잭션은 데이터 일관성을 지키는 마지막 안전장치입니다. 정상 종료되면 commit되고, 중간에 예외가 나면 rollback된다는 흐름을 몸에 익혀야 합니다.

### Step 4 — Migrations

```bash
pip install alembic
alembic init migrations
alembic revision --autogenerate -m "add users"
alembic upgrade head
```

스키마 변경을 버전 관리하지 않으면 환경마다 상태가 달라지기 쉽습니다. migration은 “지금 DB가 어떤 상태여야 하는가”를 코드로 남기는 장치입니다.

### Step 5 — Killing N+1

```python
# 5_eager.py
from sqlalchemy.orm import selectinload
stmt = select(Order).options(selectinload(Order.items))
orders = session.scalars(stmt).all()
```

자식 데이터를 한 번에 가져오면 N+1 문제를 피할 수 있습니다. ORM을 쓸 때 가장 자주 만나는 성능 함정 중 하나라서 초기에 꼭 감을 잡아 두는 편이 좋습니다.

## 검증 포인트

**Expected output:** `Base.metadata.create_all(engine)` 뒤에는 `users` 테이블이 생기고, transaction 블록 안의 두 `add()` 호출은 예외가 없을 때만 함께 commit되어야 합니다.

### 먼저 확인할 실패 지점

- 같은 요청에서 session을 오래 붙잡고 있으면 연결 누수와 lock 경합이 생기기 쉽습니다.
- migration 없이 수동으로 스키마를 바꾸면 환경 간 drift가 바로 시작됩니다.
- 목록 조회가 갑자기 느려지면 eager loading 없이 relation을 반복 조회하고 있지 않은지 먼저 봅니다.

## 이 코드에서 먼저 볼 점

- session은 보통 요청 단위로 짧게 유지합니다.
- repository는 raw dict보다 도메인 객체를 반환하는 편이 자연스럽습니다.
- migration은 직접 `ALTER TABLE` 하는 것보다 훨씬 안전합니다.

이 세 가지 원칙을 지키면 database layer가 예측 가능해집니다. 반대로 session을 길게 잡거나, 쿼리를 여기저기 흩뿌리거나, 운영 DB를 수동으로 수정하기 시작하면 문제는 조용히 쌓입니다.

## 자주 하는 실수 5가지

1. **ORM 객체를 그대로 클라이언트에 반환하는 실수**입니다. Pydantic DTO 같은 별도 응답 모델이 더 안전합니다.
2. **session을 전역으로 공유하는 실수**입니다. 동시성 버그가 따라옵니다.
3. **운영 스키마를 손으로 고치는 실수**입니다. 환경이 서로 다른 방향으로 드리프트합니다.
4. **모든 relation을 lazy loading으로만 두는 실수**입니다. N+1이 조용히 커집니다.
5. **테스트에서 실제 DB만 사용하는 실수**입니다. 속도가 느려지고 반복 실행이 어려워집니다.

## 운영에서는 이렇게 드러납니다

많은 백엔드는 PostgreSQL + ORM + Alembic + Repository 조합으로 시작합니다. 트래픽이 커지면 read replica, Redis, Elasticsearch 같은 요소가 추가되지만, service는 거의 그대로 유지되고 repository 내부만 바뀌는 경우가 많습니다.

바로 그 진화 가능성이 repository 경계의 가치입니다. 데이터 접근이 한곳에 모여 있어야 성능 최적화도, 저장소 교체도, 테스트 전략도 통제할 수 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 모든 쿼리는 인덱스 관점에서도 확인합니다.
- 모든 migration에는 되돌리는 경로도 함께 고민합니다.
- repository 메서드는 도메인 언어로 말해야 합니다.
- 트랜잭션은 가능한 짧게 유지합니다.
- 운영에서는 slow query log를 항상 켜 둡니다.

## 체크리스트

- [ ] SQL을 repository 뒤로 숨길 수 있습니다.
- [ ] 트랜잭션 블록을 작성할 수 있습니다.
- [ ] Alembic migration을 만들 수 있습니다.
- [ ] N+1 문제를 알아보고 eager loading으로 줄일 수 있습니다.
- [ ] DTO와 ORM 객체의 차이를 설명할 수 있습니다.

## 연습 문제

1. `OrderRepository.find_recent(limit=10)`을 구현하고 인덱스를 점검해 보세요.
2. `users.email` 컬럼을 추가하는 Alembic migration을 만들어 보세요.
3. 의도적으로 N+1 쿼리를 만든 뒤 `selectinload` 적용 전후 차이를 측정해 보세요.

## 정리와 다음 글

repository는 데이터베이스 위에 놓인 번역기입니다. 다음 글에서는 누가 무엇을 볼 수 있는지 결정하는 인증과 권한 문제로 넘어가겠습니다.

## 처음 질문으로 돌아가기

- **왜 service가 SQL을 직접 작성하지 않는 편이 좋을까요?**
  - 본문의 기준은 Database Layer를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **repository pattern은 어떤 경계를 만들어 줄까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **ORM은 왜 편리하면서도 함정을 함께 가져올까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Backend Development 101 (1/10): 백엔드 개발이란 무엇인가?](./01-what-is-backend-development.md)
- [Backend Development 101 (2/10): HTTP 서버 만들기](./02-building-an-http-server.md)
- [Backend Development 101 (3/10): Routing과 Controller](./03-routing-and-controllers.md)
- [Backend Development 101 (4/10): Service Layer](./04-service-layer.md)
- **Database Layer (현재 글)**
- 인증과 권한 (예정)
- Logging과 Error Handling (예정)
- 백엔드 테스트 (예정)
- 백엔드 배포 (예정)
- 운영 가능한 백엔드 구조 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [SQLAlchemy relationship loading techniques](https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html)

### 추가 읽을거리

- [Repository pattern (Martin Fowler)](https://martinfowler.com/eaaCatalog/repository.html)

Tags: Backend, Database, SQL, SQLAlchemy, Python
