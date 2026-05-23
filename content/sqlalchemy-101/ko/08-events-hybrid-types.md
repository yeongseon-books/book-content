---
title: "SQLAlchemy 101 (8/10): 이벤트, hybrid_property, 그리고 커스텀 타입"
series: sqlalchemy-101
episode: 8
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
- event
- hybrid_property
- SQLite
last_reviewed: '2026-05-12'
seo_description: event, hybrid_property, TypeDecorator로 모델 책임을 어디에 둘지 설명합니다
---

# SQLAlchemy 101 (8/10): 이벤트, hybrid_property, 그리고 커스텀 타입

도메인 규칙이 커질수록 같은 질문이 반복됩니다. 이메일 정규화는 어디에 둘지, 파생 속성은 Python property로 둘지 SQL 표현으로도 노출할지, 공통 변환 로직은 핸들러가 아니라 모델 가까이에 둘 수 없을지 같은 질문입니다.

이 글은 SQLAlchemy 101 시리즈의 여덟 번째 글입니다. 여기서는 event 시스템, `hybrid_property`, `TypeDecorator`를 묶어서 SQLAlchemy 확장점을 정리합니다.

중요한 것은 기능 목록을 외우는 일이 아닙니다. 같은 규칙이라도 타입 층, 속성 층, 이벤트 층 가운데 어디에 두느냐에 따라 적용 범위와 디버깅 방식이 크게 달라집니다. 이번 글은 그 경계를 분명하게 잡는 데 초점을 둡니다.

![이벤트, hybrid_property, 그리고 커스텀 타입](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/08/08-01-events-hybrid-property-and-custom-types.ko.png)

*이벤트, hybrid_property, 그리고 커스텀 타입*

![SQLAlchemy 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/08/08-02-why-this-matters.ko.png)
*SQLAlchemy 101 8장 흐름 개요*
> 이벤트, hybrid_property, 그리고 커스텀 타입의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- 이벤트, 속성, 타입 확장점은 각각 어떤 책임을 맡아야 할까요?
- `@validates`와 mapper 이벤트는 언제 선택이 갈릴까요?
- `hybrid_property`는 왜 Python 속성과 SQL 표현을 함께 제공할까요?

## 왜 중요한가

ORM을 처음 쓸 때는 모델이 곧 테이블이고 끝입니다. 그러다 도메인이 자라면 이메일 정규화, 비밀번호 해싱, audit log, 파생 컬럼, 암호화된 필드 같은 요구가 모델 안으로 밀려 들어옵니다. 이걸 매번 핸들러에서 처리하면 같은 코드가 여러 곳에 흩어지고 테스트도 어렵습니다.

SQLAlchemy의 event 시스템과 `hybrid_property`, `TypeDecorator`는 이 책임을 모델 가까이 두기 위한 공식 확장점입니다. 잘 쓰면 도메인 규칙이 한 곳에 모이고, 못 쓰면 어디서 데이터를 변형하는지 추적하기 어려운 코드가 됩니다. 이 글에서 각 도구의 선을 분명히 긋습니다.

## 멘탈 모델

![Mental model](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/08/08-03-mental-model.ko.png)

*멘탈 모델*
> SQLAlchemy 확장점은 세 층으로 나눠 생각합니다. **타입 층**은 컬럼 값을 DB로 들고 날 때 변환하고, **속성 층**은 Python 객체와 SQL 표현을 동시에 정의하며, **이벤트 층**은 객체·세션·엔진 라이프사이클의 특정 시점에 끼어듭니다.

같은 동작이라도 어느 층에 두느냐에 따라 영향 범위가 다릅니다. 예를 들어 이메일을 소문자로 저장하고 싶다면 세 가지 선택지가 있습니다.

- `TypeDecorator`로 `LowerString` 타입을 만들어 컬럼에 붙이면 모든 모델·모든 세션에서 자동 적용됩니다.
- `@validates("email")`로 모델에 데코레이터를 달면 그 모델에 한해 setter 시점에 검증 겸 정규화가 됩니다.
- `before_insert` 이벤트로 처리하면 INSERT 직전에만 동작하고 in-memory 객체 상태는 setter 시점까지 원본을 유지합니다.

선택 기준은 "이 규칙이 얼마나 일반적인가, 언제 적용돼야 하는가"입니다.

## 핵심 개념

![핵심 개념](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/08/08-04-core-concepts.ko.png)

*핵심 개념*
### 이벤트 시스템

SQLAlchemy는 거의 모든 객체에 `event.listen` / `@event.listens_for`로 핸들러를 붙일 수 있게 열어 둡니다. 자주 쓰는 대상은 세 종류입니다.

| 대상 | 대표 이벤트 | 쓰임새 |
| --- | --- | --- |
| Mapper(모델) | `before_insert`, `before_update`, `after_insert` | audit 컬럼, 파생 필드 계산 |
| Session | `before_flush`, `after_commit`, `after_rollback` | 트랜잭션 단위 후처리, outbox |
| Engine | `before_cursor_execute`, `after_cursor_execute` | 쿼리 로깅, 카운팅, slow query |

### `@validates`

`sqlalchemy.orm.validates`는 setter에 끼어드는 가장 단순한 훅입니다. 반환값이 실제 저장값이 되므로 검증과 정규화를 동시에 합니다.

### `hybrid_property`

`sqlalchemy.ext.hybrid.hybrid_property`는 Python 인스턴스에서는 일반 property처럼 동작하고, 클래스 수준에서는 SQL 표현으로 변환되는 이중 속성을 만듭니다. 그래서 `User.full_name == "Ada Lovelace"` 같은 where 절이 가능합니다.

### `TypeDecorator`

`sqlalchemy.types.TypeDecorator`는 기존 타입을 감싸 `process_bind_param`(쓸 때)과 `process_result_value`(읽을 때)에서 값을 바꿀 수 있게 합니다. JSON 자동 직렬화, 암호화, 통화·시간대 변환 같은 곳에 씁니다.

## 이전 방식과 개선 방식

이메일 정규화와 audit timestamp를 핸들러에서 처리하던 코드와, 모델 쪽으로 옮긴 코드를 비교합니다.

```python
# Before: handler 안에서 매번 처리
def create_user(session, email, name):
    email = email.strip().lower()
    user = User(email=email, name=name, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    session.add(user)
    session.commit()
    return user
```

```python
# After: 모델이 스스로 책임
from sqlalchemy import event
from sqlalchemy.orm import validates

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    name: Mapped[str]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]

    @validates("email")
    def _normalize_email(self, key, value):
        return value.strip().lower()

@event.listens_for(User, "before_insert")
def _set_timestamps_insert(mapper, connection, target):
    now = datetime.utcnow()
    target.created_at = now
    target.updated_at = now

@event.listens_for(User, "before_update")
def _bump_updated(mapper, connection, target):
    target.updated_at = datetime.utcnow()
```

After 버전은 `create_user` 함수 없이도 어디서 만들든 같은 규칙이 적용됩니다. 테스트도 `User(email="  A@B  ").email == "a@b"`만 검증하면 됩니다.

## 단계별 실습

![단계별 실습](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/08/08-05-step-by-step-walkthrough.ko.png)

*단계별 실습*
### 1단계: 환경 준비

`pip install "sqlalchemy>=2.0"`로 설치하고, SQLite로 작업합니다. 이전 글에서 만든 `Base`, `engine`, `Session`을 그대로 씁니다.

### 2단계: `@validates`로 이메일·점수 검증

```python
class Member(Base):
    __tablename__ = "members"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    score: Mapped[int]

    @validates("email")
    def _v_email(self, key, value):
        if "@" not in value:
            raise ValueError("invalid email")
        return value.strip().lower()

    @validates("score")
    def _v_score(self, key, value):
        if not 0 <= value <= 100:
            raise ValueError("score out of range")
        return value
```

setter 시점에서 바로 예외가 발생하므로 잘못된 데이터가 세션에 들어가기 전에 막을 수 있습니다.

### 3단계: `hybrid_property`로 파생 속성 만들기

```python
from sqlalchemy.ext.hybrid import hybrid_property

class Person(Base):
    __tablename__ = "people"
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]

    @hybrid_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @full_name.expression
    def full_name(cls):
        return cls.first_name + " " + cls.last_name
```

이제 `person.full_name`은 Python에서 동작하고, `select(Person).where(Person.full_name == "Ada Lovelace")`는 SQL `first_name || ' ' || last_name = ?`로 변환됩니다.

### 4단계: `TypeDecorator`로 LowerString·JSON 타입 만들기

```python
import json
from sqlalchemy.types import TypeDecorator, String, Text

class LowerString(TypeDecorator):
    impl = String
    cache_ok = True
    def process_bind_param(self, value, dialect):
        return value.lower() if value is not None else None
    def process_result_value(self, value, dialect):
        return value

class JSONText(TypeDecorator):
    impl = Text
    cache_ok = True
    def process_bind_param(self, value, dialect):
        return None if value is None else json.dumps(value, ensure_ascii=False)
    def process_result_value(self, value, dialect):
        return None if value is None else json.loads(value)

class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    handle: Mapped[str] = mapped_column(LowerString(64))
    settings: Mapped[dict] = mapped_column(JSONText)
```

이제 핸들러에서 dict을 그대로 넣고 꺼낼 수 있고, handle은 항상 소문자로 저장됩니다.

### 5단계: 엔진 수준에서 쿼리 카운터 달기

```python
from sqlalchemy import event

query_counter = {"n": 0}

@event.listens_for(engine, "before_cursor_execute")
def _count(conn, cursor, statement, parameters, context, executemany):
    query_counter["n"] += 1
```

테스트에서 `query_counter["n"]`을 비교하면 N+1 회귀를 잡을 수 있습니다. 이 패턴은 7편 loading strategies와 짝을 이룹니다.

### 6단계: 세션 이벤트로 outbox 패턴

```python
@event.listens_for(Session, "before_flush")
def _emit_outbox(session, flush_context, instances):
    for obj in session.new:
        if isinstance(obj, Order):
            session.add(OutboxEvent(type="OrderCreated", payload={"id": obj.id}))
```

`before_flush`에서 같은 세션에 추가하면 같은 트랜잭션으로 커밋돼 atomic한 outbox가 됩니다.

## 자주 하는 실수

- **`@validates`에서 부수 효과를 일으키기.** setter는 객체를 만들 때마다 호출됩니다. DB 조회나 외부 호출을 넣으면 성능과 테스트가 동시에 무너집니다.
- **`hybrid_property`에서 SQL expression을 빠뜨리기.** Python 부분만 있으면 where 절에서 못 씁니다. 두 정의가 같은 의미가 되도록 주의해야 합니다.
- **`TypeDecorator.cache_ok = True`를 빠뜨리기.** SQLAlchemy 2.x에서는 캐시 가능 여부를 명시하지 않으면 경고가 발생합니다.
- **이벤트에서 또 다른 ORM flush를 트리거하기.** `before_flush` 안에서 `session.commit()`을 호출하면 바로 깨집니다. 같은 세션에 add만 합니다.
- **모든 비즈니스 규칙을 이벤트로 옮기기.** 이벤트는 마법처럼 동작해 추적이 어렵습니다. 명시적으로 호출되는 서비스 함수가 더 적절한 경우도 많습니다.

## 실무에서 쓰는 패턴

production에서는 보통 다음처럼 분배합니다.

- **TypeDecorator**: 통화, 시간대, 암호화, JSON 등 데이터 표현 변환에만.
- **`@validates`**: 도메인 invariant(이메일 형식, 점수 범위) 같은 빠르고 부수효과 없는 검증.
- **Mapper 이벤트**(`before_insert`, `before_update`): audit 컬럼, 파생 필드 계산.
- **Session 이벤트**(`before_flush`, `after_commit`): outbox, 캐시 무효화, 도메인 이벤트 발행.
- **Engine 이벤트**(`before_cursor_execute`): 관측. 절대 비즈니스 로직을 넣지 않습니다.

또한 이벤트는 import 시점에 등록되므로 모듈 로딩 순서가 중요합니다. 보통 모델 정의 파일과 같은 모듈에 `@event.listens_for`를 두거나, 앱 부트 단계에서 명시적으로 `register_events()`를 호출합니다.

## 체크리스트

- [ ] `@validates`는 부수효과 없이 검증·정규화에만 쓴다
- [ ] `hybrid_property`는 Python과 SQL 두 정의를 모두 둔다
- [ ] `TypeDecorator`는 `cache_ok = True`를 명시한다
- [ ] mapper 이벤트는 audit·파생 필드 계산 같은 가벼운 작업에만 쓴다
- [ ] session 이벤트는 outbox·캐시 무효화 같은 트랜잭션 단위 작업에 쓴다
- [ ] engine 이벤트는 로깅·카운팅 등 관측에만 쓴다
- [ ] 이벤트 등록 위치를 한 곳에 모아 import 누락을 막는다

## 정리, 다음 글

이벤트와 `hybrid_property`, `TypeDecorator`는 도메인 규칙을 모델 근처에 두기 위한 SQLAlchemy의 공식 확장점입니다. 어떤 층에 둘지, 부수효과를 어디까지 허용할지 미리 정해 두면 코드가 어디서 무엇을 변형하는지 추적할 수 있습니다.

다음 글에서는 동기 패턴을 그대로 비동기로 옮기는 방법을 다룹니다. `aiosqlite` 드라이버와 `AsyncSession`, 그리고 비동기에서 lazy loading이 왜 더 위험한지 같이 살펴봅니다.

## 실전 앵커: 이벤트 훅의 실행 순서와 로그

이벤트를 안전하게 쓰려면 실행 순서를 아는 것이 먼저입니다. 아래 예시를 실행하면 한 트랜잭션에서 어떤 훅이 언제 불리는지 명확하게 볼 수 있습니다.

```python
@event.listens_for(Session, "before_flush")
def _before_flush(session, flush_context, instances):
    print("before_flush", len(session.new), len(session.dirty))

@event.listens_for(User, "before_insert")
def _before_insert(mapper, connection, target):
    print("before_insert", target.email)

@event.listens_for(Session, "after_commit")
def _after_commit(session):
    print("after_commit")
```

```text
before_flush 1 0
before_insert alice@example.com
after_commit
```

이 순서를 머리에 넣어 두면 "왜 값이 이 시점에는 아직 안 바뀌어 있지" 같은 디버깅 시간이 크게 줄어듭니다.

## hybrid_property를 인덱스 전략과 함께 보기

`hybrid_property`는 읽기 좋은 API를 만들지만, SQL 표현이 인덱스를 타지 못하면 성능이 떨어질 수 있습니다.

```python
@hybrid_property
def email_domain(self) -> str:
    return self.email.split("@", 1)[-1]

@email_domain.expression
def email_domain(cls):
    return func.substr(cls.email, func.instr(cls.email, "@") + 1)
```

이 표현식에 where를 자주 건다면 SQLite에서는 표현식 인덱스를 별도로 고려해야 합니다. 즉, 하이브리드는 편의 문법이 아니라 실행 계획까지 포함한 설계 대상으로 봐야 합니다.

## TypeDecorator와 마이그레이션 경계

커스텀 타입은 애플리케이션 계층에서 매우 강력하지만, DB 스키마 타입과 혼동하면 곤란합니다.

- `TypeDecorator(JSONText)`는 DB에는 `TEXT`로 저장될 수 있습니다.
- Alembic autogenerate는 내부 구현이 아니라 최종 DB 타입 기준으로 diff를 만듭니다.
- 타입 로직 변경(예: 직렬화 포맷 변경)은 스키마 변경이 아니라 데이터 마이그레이션 작업일 수 있습니다.

예를 들어 `settings`를 평문 JSON에서 암호화 JSON으로 바꾸면, DDL보다 데이터 재작성 배치가 핵심입니다. 이때는 10편 배포 순서처럼 이중 읽기/이중 쓰기 기간을 두는 편이 안전합니다.

## 이벤트 남용을 피하는 규칙

이벤트는 강력한 만큼 남용하기 쉽습니다. 팀 규칙으로 다음을 고정해 두면 장기 유지보수가 쉬워집니다.

- 이벤트 함수는 30줄 이하, 외부 IO 금지
- 예외 메시지는 도메인 문맥을 포함
- 이벤트 내부에서 `commit()`/`flush()` 호출 금지
- 이벤트 등록 위치를 `models/events.py`로 고정
- 테스트에서 이벤트 동작을 명시적으로 검증

## Session 이벤트와 outbox 상세 예시

원자적 outbox를 조금 더 현실적인 형태로 적으면 다음과 같습니다.

```python
class OutboxEvent(Base):
    __tablename__ = "outbox_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    topic: Mapped[str] = mapped_column(String(80), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONText, nullable=False)

@event.listens_for(Session, "before_flush")
def _outbox_order_created(session, flush_context, instances):
    for obj in session.new:
        if isinstance(obj, Order):
            session.add(OutboxEvent(topic="order.created", payload={"order_id": obj.id}))
```

주의할 점은 `obj.id`가 아직 없을 수 있다는 것입니다. 이 경우 `after_flush_postexec`를 사용해 PK가 채워진 뒤 outbox를 만드는 방식도 검토해야 합니다.

## 엔진 이벤트 기반 성능 프로파일링

7편의 N+1 점검을 확장해 느린 SQL 샘플을 남기는 방식입니다.

```python
SLOW_MS = 150

@event.listens_for(engine, "before_cursor_execute")
def _start(conn, cursor, statement, parameters, context, executemany):
    context._t0 = time.perf_counter()

@event.listens_for(engine, "after_cursor_execute")
def _end(conn, cursor, statement, parameters, context, executemany):
    ms = (time.perf_counter() - context._t0) * 1000
    if ms > SLOW_MS:
        logger.warning("slow_query_ms=%.1f sql=%s", ms, statement[:160])
```

이 로그는 10편의 운영 관측과 바로 연결됩니다. 학습 단계에서 미리 심어 두면 프로덕션 전환 시 구조를 바꿀 필요가 없습니다.

## 보강 앵커: 이벤트와 하이브리드 조합 예시

실제 도메인에서는 하이브리드 속성과 이벤트를 함께 사용합니다. 예를 들어 주문 금액과 할인 금액으로 `net_amount`를 노출하고, 업데이트 시 감사 로그를 남길 수 있습니다.

```python
class Invoice(Base):
    __tablename__ = "invoices"
    id: Mapped[int] = mapped_column(primary_key=True)
    gross_amount: Mapped[int]
    discount_amount: Mapped[int]

    @hybrid_property
    def net_amount(self) -> int:
        return self.gross_amount - self.discount_amount

    @net_amount.expression
    def net_amount(cls):
        return cls.gross_amount - cls.discount_amount

@event.listens_for(Invoice, "before_update")
def _audit_invoice(mapper, connection, target):
    logger.info("invoice_update id=%s net=%s", target.id, target.net_amount)
```

이 조합은 "도메인 의미"와 "운영 추적"을 동시에 모델 근처에 고정합니다.

## 보강 앵커: TypeDecorator 회귀 테스트

커스텀 타입은 작은 변경이 큰 데이터 오염으로 이어질 수 있으므로 round-trip 테스트를 권장합니다.

```python
def test_jsontext_roundtrip(session: Session):
    a = Account(handle="Alice", settings={"theme": "light"})
    session.add(a)
    session.commit()
    loaded = session.get(Account, a.id)

    assert loaded.handle == "alice"
    assert loaded.settings == {"theme": "light"}
```

이 테스트는 직렬화 포맷 변경, 인코딩 문제, 소문자 정규화 누락을 동시에 잡아 줍니다.

## 보강 앵커: 이벤트 디버깅 체크리스트

- 이벤트가 등록된 모듈이 실제로 import되는가
- 동일 이벤트가 중복 등록되지 않는가
- 이벤트 함수가 예외를 삼키지 않는가
- 이벤트 내부에서 세션 재진입을 유발하지 않는가
- 이벤트 로그에 객체 식별자(PK)가 포함되는가

이 다섯 항목만 점검해도 "이벤트가 안 돈다" 또는 "두 번 돈다" 문제의 대부분을 바로 좁힐 수 있습니다.

## 보강 메모

확장점을 도입할 때 가장 중요한 질문은 "이 규칙이 어디서 실행되는가"입니다. 타입 변환, 속성 계산, 이벤트 훅의 실행 위치가 분명해야 팀원이 로그만 보고도 데이터 흐름을 추적할 수 있고, 장애 시 복구 속도도 빨라집니다.

추가로, 이벤트 훅은 관측 지표와 짝을 이루어야 합니다. 훅이 실제로 몇 번 호출되는지 카운터를 남기지 않으면 동작 여부를 감에 의존하게 됩니다.

하이브리드 속성을 도입한 뒤에는 반드시 SQL expression 경로까지 테스트해야 합니다. Python 속성 테스트만 통과하면 쿼리 필터에서 실패하는 경우를 놓치기 쉽습니다.

결국 확장점 설계의 목표는 규칙을 숨기지 않는 것입니다. 코드 검색 한 번으로 데이터 변환 지점을 찾을 수 있어야 운영 품질이 유지됩니다.

운영 로그와 테스트가 함께 있어야 확장점은 신뢰할 수 있는 설계 도구가 됩니다.

요약하면, 확장점의 힘은 명시성과 검증 가능성에서 나옵니다.

## 처음 질문으로 돌아가기

- **이벤트, 속성, 타입 확장점은 각각 어떤 책임을 맡아야 할까요?**
  - 이 글은 확장점을 타입 층, 속성 층, 이벤트 층으로 나눴습니다. `TypeDecorator`는 `LowerString`과 `JSONText`처럼 DB에 쓰고 읽을 때 값을 바꾸고, `hybrid_property`는 `full_name`·`net_amount`처럼 Python 속성과 SQL 표현을 같이 제공하며, 이벤트는 `before_insert`, `before_flush`, `before_cursor_execute`처럼 특정 라이프사이클 순간에 개입합니다.
- **`@validates`와 mapper 이벤트는 언제 선택이 갈릴까요?**
  - `@validates`는 `email`, `score`처럼 setter 시점에 바로 검증·정규화해야 하는 값에 적합하고, 잘못된 데이터가 세션에 들어오기 전에 막아 줍니다. 반면 mapper 이벤트는 `before_insert`에서 timestamp를 채우거나 `before_update`에서 audit 값을 계산하는 식으로 flush 직전 공통 후처리를 걸 때 더 자연스럽습니다.
- **`hybrid_property`는 왜 Python 속성과 SQL 표현을 함께 제공할까요?**
  - 같은 도메인 규칙을 객체와 쿼리에서 따로 다시 쓰지 않게 하려는 것이 핵심입니다. 본문에서 `Person.full_name`과 `Invoice.net_amount`를 예로 든 것처럼, 인스턴스에서는 속성처럼 읽고 `select(...).where(...)`에서는 SQL 식으로 재사용해야 검색과 필터 조건이 같은 의미를 유지합니다.

<!-- toc:begin -->
## 시리즈 목차

- [SQLAlchemy 101 (1/10): SQLAlchemy 2.x 시작하기 - Engine과 Connection의 본질](./01-sqlalchemy-2x-engine-connection.md)
- [SQLAlchemy 101 (2/10): SQLAlchemy Core - MetaData, Table, Column으로 schema를 Python 객체로 만들기](./02-core-metadata-table-types.md)
- [SQLAlchemy 101 (3/10): SQLAlchemy Core - select·insert·update·delete를 2.x style로 다루기](./03-core-select-insert-update-delete.md)
- [SQLAlchemy 101 (4/10): ORM 기초: DeclarativeBase와 mapped_column으로 모델 정의하기](./04-orm-declarative-mapped-column.md)
- [SQLAlchemy 101 (5/10): Session 깊이 보기: Unit of Work와 Identity Map의 동작 원리](./05-session-unit-of-work-identity-map.md)
- [SQLAlchemy 101 (6/10): ORM 관계 매핑: relationship과 back_populates로 양방향 탐색 안전하게 잇기](./06-relationships-back-populates.md)
- [SQLAlchemy 101 (7/10): 로딩 전략과 N+1 문제: lazy/joined/selectin을 언제 골라야 하는가](./07-loading-strategies-n-plus-one.md)
- **SQLAlchemy 101 (8/10): 이벤트, hybrid_property, 그리고 커스텀 타입 (현재 글)**
- SQLAlchemy 101 (9/10): 비동기 SQLAlchemy: aiosqlite와 AsyncSession (예정)
- SQLAlchemy 101 (10/10): 프로덕션 패턴: 풀, 관측, 마이그레이션, 배포 (예정)

<!-- toc:end -->

## 참고 자료

- SQLAlchemy: Events — https://docs.sqlalchemy.org/en/20/core/event.html
- SQLAlchemy: ORM Events — https://docs.sqlalchemy.org/en/20/orm/events.html
- SQLAlchemy: Hybrid Attributes — https://docs.sqlalchemy.org/en/20/orm/extensions/hybrid.html
- SQLAlchemy: TypeDecorator — https://docs.sqlalchemy.org/en/20/core/custom_types.html

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/sqlalchemy-101/ko)

Tags: Python, SQLAlchemy, ORM, Database
