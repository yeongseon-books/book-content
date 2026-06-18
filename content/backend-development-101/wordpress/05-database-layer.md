---
series: backend-development-101
episode: 5
title: "바이브코딩을 위한 백엔드 개발 기초 (5/10): Database Layer"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - Backend
  - Database
  - SQL
  - SQLAlchemy
  - Python
seo_description: AI가 만든 DB 코드에서 N+1 문제, 트랜잭션 누락, 마이그레이션 관리 실수를 발견하고 수정하는 방법을 바이브코딩 관점에서 설명합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 백엔드 개발 기초 (5/10): Database Layer

이 글은 **바이브코딩을 위한 백엔드 개발 기초** 시리즈의 5번째 글입니다. AI에게 코드를 맡기기 전에 백엔드가 어떻게 동작하는지 이해해야 원하는 결과를 얻을 수 있습니다.

---

AI가 만든 서비스 계층이 자라기 시작하면 데이터베이스 코드는 거의 항상 같은 증상으로 무너집니다. 목록 API는 처음에 빠르다가 어느 날 갑자기 10배 느려지고, 운영 배포 직후 특정 엔드포인트만 500을 냅니다. SQL 자체가 틀린 경우보다, 데이터 접근 책임이 흩어져 있고 스키마 변경 이력이 통제되지 않으며 세션 수명이 요청 경계를 벗어나 있는 경우가 더 많습니다.

> DB layer의 목적은 'SQL을 잘 쓰는 것'이 아니라 '도메인 객체와 행(row) 사이의 경계를 한 곳에 모아 두는 것'입니다 — 이 경계가 위 계층으로 새는 순간 비즈니스 로직 안에서 SQL이 자라고, 테스트가 불가능해집니다.

## 이 글에서 다룰 문제

- 왜 service가 SQL을 직접 작성하지 않는 편이 좋을까요?
- repository pattern은 어떤 경계를 만들어 줄까요?
- ORM은 왜 편리하면서도 함정을 함께 가져올까요?
- AI가 만든 DB 코드에서 N+1 문제와 트랜잭션 누락을 어떻게 발견할까요?
- 마이그레이션을 AI에게 맡길 때 주의할 점은 무엇일까요?

## 바이브코딩과 Database Layer: AI가 자주 만드는 문제

AI에게 API를 요청하면 service 내부에서 직접 SQL을 실행하거나, ORM을 사용하되 로딩 전략을 지정하지 않는 코드가 자주 나옵니다. 로컬 샘플 데이터에서는 문제가 없어 보이지만, 운영 데이터 크기에서 N+1 문제로 폭발합니다.

또한 AI는 마이그레이션을 "모델을 바꾸고 나서 migrate 명령어 한 번 실행"으로 단순화하는 경향이 있습니다. 실제로는 constraint 이름, 인덱스 생성 방식, nullable 전환의 데이터 백필 절차를 수동으로 검토해야 합니다.

## Repository Pattern: 테스트 가능성과 교체 가능성

repository는 "DB에 접근하는 코드 묶음"이 아닙니다. service 계층이 도메인 언어로 말하도록 만들고, 데이터 접근 구현을 교체 가능한 어댑터로 제한하는 경계입니다.

```python
from typing import Protocol

class UserRepository(Protocol):
    def find_by_email(self, email: str) -> User | None: ...
    def save(self, user: User) -> User: ...

class UserService:
    def __init__(self, users: UserRepository):
        self.users = users

    def register(self, email: str) -> User:
        if self.users.find_by_email(email):
            raise ValueError("이미 가입된 이메일입니다")
        return self.users.save(User(id=None, email=email))
```

이 구조에서 테스트는 fake repository로 빠르게 실행할 수 있고, DB 교체 시 service 코드는 건드리지 않습니다.

## N+1 문제: 목록 API가 갑자기 느려지는 원인

N+1은 "목록 1회 조회 + 각 항목마다 추가 조회" 패턴입니다. AI가 만든 코드에서 가장 흔한 성능 문제입니다.

```text
# N+1이 발생하는 로그 패턴
[req-8f1] SELECT id, title FROM orders ORDER BY created_at DESC LIMIT 50;
[req-8f1] SELECT id, order_id, price FROM order_items WHERE order_id = 101;
[req-8f1] SELECT id, order_id, price FROM order_items WHERE order_id = 102;
...
[req-8f1] SELECT id, order_id, price FROM order_items WHERE order_id = 150;
```

50개 주문을 가져오는 데 51번의 쿼리가 실행됩니다.

해결은 eager loading을 지정하는 것입니다:

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

stmt = (
    select(OrderModel)
    .options(selectinload(OrderModel.items))  # eager loading 지정
    .order_by(OrderModel.created_at.desc())
    .limit(50)
)
orders = session.scalars(stmt).all()
```

## Before/After: Service에서 SQL 직접 실행 vs Repository 사용

### Before: AI가 자주 만드는 패턴

```python
class OrderService:
    def get_recent_orders(self, user_id: int):
        # service가 SQL을 직접 실행
        conn = get_db()
        result = conn.execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
            (user_id,)
        )
        return result.fetchall()
```

### After: Repository를 통한 접근

```python
class OrderRepository:
    def __init__(self, session):
        self.session = session

    def find_recent_by_user(self, user_id: int, limit: int = 10) -> list[OrderModel]:
        stmt = (
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .where(OrderModel.user_id == user_id)
            .order_by(OrderModel.created_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())

class OrderService:
    def __init__(self, order_repo: OrderRepository):
        self.order_repo = order_repo

    def get_recent_orders(self, user_id: int):
        return self.order_repo.find_recent_by_user(user_id)
```

## AI가 만든 DB 코드에서 자주 하는 실수

| 실수 | 왜 문제인가 | AI에게 수정 요청 방법 |
| --- | --- | --- |
| service에서 즉석 SQL 작성 | 도메인 규칙과 데이터 접근이 결합 | "SQL 쿼리는 repository 클래스로 분리해줘" |
| "ORM이 알아서 최적화" 기대 | 로딩 전략 기본값은 lazy loading | "목록 API에서 N+1이 발생하지 않도록 selectinload를 추가해줘" |
| 마이그레이션 자동 생성본을 무검토 적용 | 제약조건/인덱스/데이터 백필 누락 | "autogenerate 결과를 리뷰하고 수동으로 검토해야 할 항목을 알려줘" |
| 세션 생명주기 방치 | 커넥션 누수와 lock 경합 | "요청 스코프 내에서 세션을 열고 닫는 패턴으로 작성해줘" |
| 인덱스 없는 기능 배포 | 데이터 규모가 커지면 즉시 병목 | "WHERE 절에 사용되는 컬럼에 인덱스를 추가해줘" |

## AI 팁: Database Layer를 AI에게 요청하는 방법

**Repository 분리**: "DB 접근 코드를 repository 클래스로 분리해줘. service는 repository 인터페이스만 알도록 해줘."

**N+1 방지**: "목록을 조회할 때 관련 데이터를 한 번에 가져오도록 selectinload 또는 joinedload를 사용해줘."

**마이그레이션 안전성**: "Alembic 마이그레이션 스크립트를 생성해줘. autogenerate 결과에서 주의해야 할 점도 설명해줘."

**커넥션 풀**: "SQLAlchemy engine에 pool_size, max_overflow, pool_pre_ping 설정을 추가해줘."

## 체크리스트

- [ ] repository pattern의 역할과 이점을 설명할 수 있습니다.
- [ ] N+1 문제가 무엇인지, 어떻게 해결하는지 설명할 수 있습니다.
- [ ] service가 SQL을 직접 실행하지 않아야 하는 이유를 말할 수 있습니다.
- [ ] Alembic 마이그레이션 자동 생성본을 그대로 적용하면 안 되는 이유를 설명할 수 있습니다.
- [ ] AI가 만든 코드에서 N+1 위험이 있는 목록 조회를 발견할 수 있습니다.

## 처음 질문으로 돌아가기

- **왜 service가 SQL을 직접 작성하지 않는 편이 좋을까요?**
  - 도메인 규칙과 데이터 접근이 결합되면 변경 비용이 커집니다. repository 경계가 있으면 성능 개선과 인프라 변경이 service 로직을 흔들지 않습니다.
- **repository pattern은 어떤 경계를 만들어 줄까요?**
  - 도메인 언어(find_by_email, save)로 데이터에 접근하게 하고, SQL/ORM 세부사항을 캡슐화합니다. 테스트에서는 fake로 대체할 수 있습니다.
- **ORM은 왜 편리하면서도 함정을 함께 가져올까요?**
  - CRUD와 관계 매핑은 편리하게 해주지만, lazy loading 기본값이 N+1 문제를 만들 수 있습니다. 핵심 엔드포인트는 로딩 전략을 명시해야 합니다.

## 정리

Database Layer의 품질은 "쿼리가 동작하느냐"가 아니라 "변경과 운영에서 예측 가능하냐"로 결정됩니다. AI에게 DB 코드를 요청할 때 "repository 패턴으로 분리해줘", "N+1이 발생하지 않도록 eager loading을 사용해줘", "마이그레이션 스크립트의 주의 사항을 설명해줘"를 명시하면 훨씬 안전한 코드를 얻을 수 있습니다.

## 참고 자료

### 공식 문서

- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [SQLAlchemy relationship loading techniques](https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html)

### 추가 읽을거리

- [backend-development-101 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/backend-development-101/ko)
- [Repository pattern (Martin Fowler)](https://martinfowler.com/eaaCatalog/repository.html)

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 백엔드 개발 기초 (1/10): 백엔드 개발이란 무엇인가?](./01-what-is-backend-development.md)
- [바이브코딩을 위한 백엔드 개발 기초 (2/10): HTTP 서버 만들기](./02-building-an-http-server.md)
- [바이브코딩을 위한 백엔드 개발 기초 (3/10): Routing과 Controller](./03-routing-and-controllers.md)
- [바이브코딩을 위한 백엔드 개발 기초 (4/10): Service Layer](./04-service-layer.md)
- **바이브코딩을 위한 백엔드 개발 기초 (5/10): Database Layer (현재 글)**
- [바이브코딩을 위한 백엔드 개발 기초 (6/10): 인증과 권한](./06-auth-and-authorization.md)
- [바이브코딩을 위한 백엔드 개발 기초 (7/10): Logging과 Error Handling](./07-logging-and-error-handling.md)
- [바이브코딩을 위한 백엔드 개발 기초 (8/10): 백엔드 테스트](./08-testing-the-backend.md)
- [바이브코딩을 위한 백엔드 개발 기초 (9/10): 백엔드 배포](./09-deploying-the-backend.md)
- [바이브코딩을 위한 백엔드 개발 기초 (10/10): 운영 가능한 백엔드 구조](./10-production-ready-backend.md)

<!-- toc:end -->

Tags: 바이브코딩, Backend, Database, SQL, SQLAlchemy, Python
