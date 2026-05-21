---
title: "SQLAlchemy 101 (7/10): 로딩 전략과 N+1 문제: lazy/joined/selectin을 언제 골라야 하는가"
series: sqlalchemy-101
episode: 7
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
- N+1
- selectinload
- SQLite
last_reviewed: '2026-05-12'
seo_description: lazy, joinedload, selectinload와 N+1 문제를 언제 어떻게 다루는지 설명합니다
---

# SQLAlchemy 101 (7/10): 로딩 전략과 N+1 문제: lazy/joined/selectin을 언제 골라야 하는가

ORM이 가장 자주 비판받는 이유는 대개 쿼리 횟수가 눈에 보이지 않는다는 점입니다. 코드 한 줄은 단순해 보이는데 실제로는 SELECT가 수십 번 더 나가는 경우가 많고, 그 대표적인 패턴이 N+1입니다.

이 글은 SQLAlchemy 101 시리즈의 일곱 번째 글입니다. 여기서는 lazy 로딩이 N+1을 어떻게 만들고, `joinedload`, `selectinload`, `raiseload`를 어떤 기준으로 선택해야 하는지 설명합니다.

6편에서 관계를 정의했다면 이제 그 관계를 어떤 SQL 패턴으로 읽을지 결정해야 합니다. 관계 정의가 객체 그래프의 뼈대라면, 로딩 전략은 그 그래프를 얼마나 비싸게 읽을지 결정하는 실행 계획에 가깝습니다.

![로딩 전략과 N+1 문제 - lazy/joined/selectin 선택 기준](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/07/07-01-loading-strategies-and-the-n-1-problem-w.ko.png)

*로딩 전략과 N+1 문제 - lazy/joined/selectin 선택 기준*

## 먼저 던지는 질문

- 기본 lazy 로딩은 어떤 상황에서 N+1을 만들까요?
- `joinedload`와 `selectinload`는 각각 어떤 쿼리를 추가로 만들까요?
- 컬렉션 관계에서는 왜 `selectinload`가 더 자주 권장될까요?

## 큰 그림

![SQLAlchemy 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/07/07-02-why-it-matters.ko.png)

*SQLAlchemy 101 7장 흐름 개요*

이 그림에서는 로딩 전략과 N+1 문제: lazy/joined/selectin을 언제 골라야 하는가를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 로딩 전략과 N+1 문제: lazy/joined/selectin을 언제 골라야 하는가의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

ORM의 lazy 로딩은 코드 가독성을 높여 줍니다. `user.orders`라고 적기만 하면 알아서 SELECT가 발사됩니다. 그러나 이 편리함이 종종 운영 환경에서 100배 가까운 SELECT 폭증을 만듭니다.

- 100명의 사용자를 가져와 각 사용자의 마지막 주문 시각을 출력하는 핸들러: 1 + 100 = 101 SELECT.
- 게시글 목록 50건과 각 게시글의 태그를 보여 주는 응답: 1 + 50 = 51 SELECT.
- 운영 모니터링 도구가 "이 엔드포인트는 평균 80개 쿼리를 사용합니다"라고 경고를 보내는 시점이 N+1을 알아차리는 가장 흔한 순간입니다.

이 패턴은 디스크 IO나 네트워크 왕복 비용이 누적되어, 단일 쿼리로 처리하면 5ms일 작업이 800ms로 늘어나는 식의 회귀를 만듭니다. 그리고 SQLite처럼 단일 파일 기반 엔진에서도 락 경합과 트랜잭션 크기에 영향을 주기 때문에 지역 개발 환경에서도 영향이 큽니다.

## 멘탈 모델

![Mental model](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/07/07-03-mental-model.ko.png)

*멘탈 모델*
> "관계 속성에 처음 접근하면 SELECT가 한 번 발사된다." 이 한 문장이 lazy 로딩의 전부입니다. N+1은 이 한 문장이 N번 반복될 때 일어납니다. `joinedload`는 부모 SELECT에 LEFT JOIN을 붙여 한 번에 가져오는 전략, `selectinload`는 부모를 먼저 가져온 뒤 자식들을 IN(...) 한 방으로 가져오는 전략입니다.

```text
lazy (default):    SELECT users         (1)
                   SELECT orders WHERE user_id = ?   ← 사용자 1번
                   SELECT orders WHERE user_id = ?   ← 사용자 2번
                   ... (총 N번)

selectinload:      SELECT users         (1)
                   SELECT orders WHERE user_id IN (1, 2, ...)   (1)

joinedload:        SELECT users LEFT OUTER JOIN orders ...      (1)
```

쿼리 횟수만 보면 joinedload가 항상 좋아 보이지만, 컬렉션 측면(일대다)에서는 row가 부모×자식 조합으로 폭증할 수 있어 traffic이 오히려 늘어납니다. 그래서 컬렉션은 보통 `selectinload`를 권장합니다.

## 핵심 개념

![핵심 개념](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/07/07-04-core-concepts.ko.png)

*핵심 개념*
### 1) 기본 lazy 로딩이 만드는 N+1

```python
with Session(engine) as session:
    users = session.scalars(select(User)).all()      # SELECT users
    for u in users:
        for o in u.orders:                           # SELECT orders WHERE user_id = ? × N
            print(u.email, o.amount)
```

`u.orders`에 처음 접근하는 순간마다 SELECT가 발사됩니다. 이것이 정확히 N+1 패턴입니다.

### 2) joinedload: LEFT JOIN으로 한 번에

```python
from sqlalchemy.orm import joinedload

stmt = select(User).options(joinedload(User.orders))
users = session.scalars(stmt).unique().all()
```

ORM은 다음과 같은 SQL을 만듭니다.

```sql
SELECT users.id, users.email, orders.id, orders.user_id, orders.amount
FROM users
LEFT OUTER JOIN orders ON users.id = orders.user_id
```

한 SELECT로 부모와 자식을 동시에 가져옵니다. 다만 일대다 관계에서는 부모 행이 자식 수만큼 중복되기 때문에, `unique()`를 호출해 ORM이 부모를 1개씩으로 합쳐 주도록 해야 합니다. 자식 컬렉션이 50건씩 달려 있다면 한 부모에 대해 50개 row가 만들어지므로, traffic 측면에서 손해일 수 있습니다.

### 3) selectinload: IN(...) 한 방으로

```python
from sqlalchemy.orm import selectinload

stmt = select(User).options(selectinload(User.orders))
users = session.scalars(stmt).all()
```

ORM은 두 개의 SELECT만 사용합니다.

```sql
SELECT users.id, users.email FROM users
SELECT orders.id, orders.user_id, orders.amount
FROM orders WHERE orders.user_id IN (1, 2, 3, ...)
```

부모 row 중복이 없고, 자식이 한 번의 IN 쿼리로 깔끔하게 묶입니다. 일대다 컬렉션에는 보통 이 전략이 가장 효율적입니다.

### 4) 어떤 전략을 언제 쓰는가

| 상황 | 권장 전략 | 이유 |
| --- | --- | --- |
| 다대일/일대일 (자식 → 부모) | `joinedload` | LEFT JOIN으로 한 row에 함께 묶임. 폭증 위험 없음. |
| 일대다 (부모 → 자식 컬렉션) | `selectinload` | IN 묶음 1회. row 폭증 회피. |
| 다대다 | `selectinload` | 위와 동일. |
| 큰 자식 컬렉션을 페이지네이션 | lazy + 별도 SELECT | 부모만 미리 가져오고, 자식은 명시적 SELECT로 LIMIT/OFFSET. |

`subqueryload`도 존재하지만, 모던 코드는 거의 항상 `selectinload`로 충분합니다.

### 5) raiseload로 N+1을 즉시 노출시키기

```python
from sqlalchemy.orm import raiseload

stmt = select(User).options(raiseload(User.orders))
users = session.scalars(stmt).all()
for u in users:
    print(u.orders)        # InvalidRequestError 발생
```

`raiseload`는 lazy 로딩을 금지합니다. 명시적으로 eager 로딩을 적지 않은 상태에서 자식 속성에 접근하면 즉시 예외가 납니다. 테스트 환경 또는 특정 핸들러에서 N+1을 사전에 잡고 싶을 때 유용합니다.

또는 모델 정의 단계에서 `relationship(..., lazy="raise")`로 설정해 두면 해당 관계에 한해 항상 eager 로딩을 강제할 수 있습니다.

## 이전 방식과 개선 방식

### 이전: lazy 로딩으로 N+1 발생

```python
with Session(engine) as session:
    users = session.scalars(select(User).limit(50)).all()
    return [
        {"email": u.email, "orders": [o.amount for o in u.orders]}
        for u in users
    ]
# echo 결과: SELECT users 1번 + SELECT orders WHERE user_id = ? 50번 = 51 SELECT
```

### 개선 후: selectinload 한 줄 추가

```python
with Session(engine) as session:
    stmt = select(User).options(selectinload(User.orders)).limit(50)
    users = session.scalars(stmt).all()
    return [
        {"email": u.email, "orders": [o.amount for o in u.orders]}
        for u in users
    ]
# echo 결과: SELECT users 1번 + SELECT orders WHERE user_id IN (...) 1번 = 2 SELECT
```

`options(selectinload(...))` 한 줄로 51 → 2 SELECT가 됩니다. 이 차이가 운영 환경에서 응답시간 5배~50배 개선으로 이어집니다.

## 단계별 실습

![단계별 실습](https://yeongseon-books.github.io/book-public-assets/assets/sqlalchemy-101/07/07-05-step-by-step-walkthrough.ko.png)

*단계별 실습*
```python
from sqlalchemy import ForeignKey, String, create_engine, select
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, Session,
    mapped_column, relationship, selectinload, joinedload, raiseload,
)

engine = create_engine("sqlite:///loader_demo.db", echo=True, future=True)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    orders: Mapped[list["Order"]] = relationship(back_populates="user")

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[int] = mapped_column()
    user: Mapped[User] = relationship(back_populates="orders")

def seed():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        for i in range(5):
            u = User(email=f"u{i}@example.com")
            for j in range(3):
                u.orders.append(Order(amount=10 * (j + 1)))
            s.add(u)
        s.commit()

def lazy_demo():
    print("--- lazy (default) ---")
    with Session(engine) as s:
        users = s.scalars(select(User)).all()
        for u in users:
            for o in u.orders:
                pass            # SELECT N번 발사

def selectin_demo():
    print("--- selectinload ---")
    with Session(engine) as s:
        users = s.scalars(select(User).options(selectinload(User.orders))).all()
        for u in users:
            for o in u.orders:
                pass            # SELECT 2번만 사용

def raiseload_demo():
    print("--- raiseload ---")
    with Session(engine) as s:
        users = s.scalars(select(User).options(raiseload(User.orders))).all()
        try:
            users[0].orders         # InvalidRequestError
        except Exception as e:
            print("blocked:", type(e).__name__)

if __name__ == "__main__":
    seed()
    lazy_demo()
    selectin_demo()
    raiseload_demo()
```

`echo=True`로 켠 채 실행하면, lazy_demo는 약 6번의 SELECT, selectin_demo는 2번의 SELECT만 발사하는 모습을 확인할 수 있습니다. raiseload_demo는 자식 속성 접근 시점에 즉시 예외가 납니다.

## 자주 하는 실수

### 1) joinedload를 컬렉션에 무분별하게 사용

`joinedload(User.orders)`는 한 번의 SELECT로 끝나지만, 사용자 50명에 평균 100개의 주문이 있으면 5,000개의 row가 만들어져 네트워크로 흘러갑니다. 컬렉션은 거의 항상 `selectinload`가 안전합니다. `joinedload`는 다대일/일대일에서 권장합니다.

### 2) `unique()` 누락

joinedload 후에는 부모 row가 중복으로 나오므로 `session.scalars(stmt).unique().all()`로 부모를 합쳐야 합니다. 빠뜨리면 부모 객체가 자식 수만큼 반복되어 응답에 잘못된 데이터가 들어갑니다.

### 3) 응답 직전에 lazy 로딩

핸들러에서 미리 eager 로딩을 걸지 않고, 직렬화 단계에서 자식 속성에 접근하면 그 시점에 SELECT가 발사됩니다. 응답 단계의 SELECT는 트랜잭션 길이를 늘리고, 직렬화 라이브러리가 detached 객체에 접근하면 오류가 납니다.

### 4) options를 select 외부에 두기

```python
stmt = select(User)
users = session.scalars(stmt, options=selectinload(User.orders)).all()   # 잘못된 사용
```

`options(...)`는 항상 `select(...).options(...)` 형태로 select 객체에 부착해야 합니다. `scalars()`의 키워드 인자가 아닙니다.

### 5) raiseload 없이 N+1을 "느낌"으로만 점검

수동으로 echo를 켜서 잡는 N+1 점검은 회귀가 잦습니다. 테스트 환경에서 특정 핸들러에 `raiseload`를 켜 두거나, SQLAlchemy의 `event.listens_for(Engine, "before_cursor_execute")`로 query count assertion을 만들어 두면 회귀를 자동으로 잡을 수 있습니다.

## 실무에서 자주 만나는 상황

- **응답 모델별 eager 정책**: 동일 ORM 모델이 여러 응답에 쓰이면, 응답마다 필요한 자식이 다릅니다. 각 핸들러에서 필요한 `options`를 명시하는 편이 안전합니다. 모델 정의 단계의 `lazy="joined"`는 모든 호출에 영향을 줘서 부담이 큽니다.
- **페이지네이션 + selectinload**: `select(User).limit(20).options(selectinload(User.orders))`처럼 자르고 나서 자식을 한 방에 가져오면 응답 크기를 안정시킬 수 있습니다.
- **테스트에서 query count assertion**: `with capture_queries() as q: ...; assert len(q) == 2` 형태의 헬퍼는 ORM 회귀 방지에 매우 효과적입니다. 작은 SQLAlchemy 이벤트 한 줄로 구현됩니다.
- **로깅과 추적**: production에서는 `echo=True`가 비현실적이므로, slow query log 또는 OpenTelemetry SQL exporter로 N+1을 가시화합니다.
- **DTO/Pydantic 분리**: ORM 객체를 그대로 반환하지 않고 DTO로 변환하는 단계를 두면, 어떤 자식이 필요한지 명시적으로 드러나서 eager 정책을 짜기 쉽습니다.

## 체크리스트

- [ ] 핸들러마다 필요한 자식 컬렉션이 정확히 무엇인지 정의했는가?
- [ ] 컬렉션은 `selectinload`, 다대일/일대일은 `joinedload`로 결정했는가?
- [ ] joinedload 사용 시 `unique()`를 호출했는가?
- [ ] 테스트에 query count assertion 또는 `raiseload`가 들어 있는가?
- [ ] production에서 SQL 추적 수단(slow log/observability)이 있는가?
- [ ] 모델 정의 단계의 `lazy=...` 변경이 다른 핸들러에 부작용을 주지 않는지 점검했는가?

## SQL echo 비교: lazy vs selectinload vs joinedload

같은 요구사항(사용자와 주문 목록 조회)에서 전략별 SQL 차이를 한 번에 비교해 보겠습니다.

```text
# lazy
SELECT users.id, users.email FROM users
SELECT orders.id, orders.user_id, orders.amount FROM orders WHERE ? = orders.user_id
SELECT orders.id, orders.user_id, orders.amount FROM orders WHERE ? = orders.user_id
...

# selectinload
SELECT users.id, users.email FROM users
SELECT orders.id, orders.user_id, orders.amount
FROM orders WHERE orders.user_id IN (?, ?, ?, ?, ?)

# joinedload
SELECT users.id, users.email, orders.id, orders.user_id, orders.amount
FROM users LEFT OUTER JOIN orders ON users.id = orders.user_id
```

핵심은 "몇 번 나가느냐"보다 "얼마나 많은 row를 옮기느냐"입니다. selectinload는 보통 균형이 좋고, joinedload는 부모당 자식 수가 적을 때 특히 유리합니다.

## 프로파일링 앵커: 요청당 쿼리 수와 총 row 수

N+1을 정확히 잡으려면 쿼리 수만 보지 말고 총 row 수까지 봐야 합니다.

```python
metrics = {"queries": 0, "rows": 0}

@event.listens_for(engine, "after_cursor_execute")
def _profile(conn, cursor, statement, params, context, executemany):
    metrics["queries"] += 1
    if cursor.rowcount and cursor.rowcount > 0:
        metrics["rows"] += cursor.rowcount
```

joinedload에서 `queries`는 1이지만 `rows`가 급증하면 전체 전송량이 증가했을 가능성이 큽니다.

## 핸들러별 로딩 정책 표준

운영 팀에서 실제로 적용하는 간단한 규칙은 다음과 같습니다.

- 목록 API: `selectinload` 기본
- 상세 API(1건): 필요한 경우 `joinedload` 허용
- 대용량 컬렉션: 관계 로딩 대신 전용 쿼리 + 페이지네이션
- 직렬화 전 단계: `raiseload`로 누락 관계 접근 차단

이 규칙은 코드 리뷰 체크리스트로 옮길 수 있어 회귀 방지에 효과적입니다.

## 실패 사례: DTO 직렬화 단계의 지연 SQL

실제 장애에서 자주 보는 패턴은 "서비스 함수는 빨랐는데 JSON 직렬화에서 느려짐"입니다. 이유는 직렬화 코드가 관계 속성에 접근하면서 lazy SQL을 발사하기 때문입니다.

```python
def to_user_dto(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "orders": [o.amount for o in user.orders],
    }
```

이 함수를 쓰는 코드에서는 쿼리 함수 단계에서 반드시 `selectinload(User.orders)`를 포함해야 합니다. DTO 코드는 데이터 접근 정책이 아니라 변환만 담당하도록 분리해야 합니다.

## 7편 요약 운영 체크

- 쿼리 수가 줄어도 row 폭증 여부를 함께 본다
- 컬렉션은 기본적으로 `selectinload`를 선택한다
- joinedload를 쓰면 `unique()`를 빠뜨리지 않는다
- 테스트에서 `raiseload` 또는 쿼리 수 assertion을 강제한다
- 직렬화 단계에서 SQL이 발생하지 않도록 경계를 분리한다

## 보강 앵커: 페이지네이션과 로딩 전략 결합

목록 API에서 가장 실용적인 패턴은 "먼저 부모를 자르고, 그 뒤 관계를 묶어 읽기"입니다.

```python
def list_user_page(session: Session, page: int, size: int):
    stmt = (
        select(User)
        .order_by(User.id)
        .limit(size)
        .offset((page - 1) * size)
        .options(selectinload(User.orders))
    )
    return session.scalars(stmt).all()
```

이 패턴은 응답 크기와 쿼리 수를 동시에 예측 가능하게 만듭니다.

## 보강 앵커: 로딩 정책을 함수 시그니처로 드러내기

```python
def get_user_for_detail(session: Session, user_id: int) -> User | None:
    stmt = (
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.orders), selectinload(User.tags))
    )
    return session.scalar(stmt)
```

핸들러가 어떤 관계를 필요로 하는지 쿼리 함수 이름과 시그니처에 드러내면, 직렬화 단계의 추가 SQL을 구조적으로 막을 수 있습니다.

## 보강 앵커: 로딩 전략 성능 리허설

배포 전에 최소한 아래 세 케이스를 측정하는 것을 권장합니다.

- 부모 20건, 자식 평균 3건
- 부모 20건, 자식 평균 30건
- 부모 100건, 자식 평균 5건

같은 코드라도 데이터 분포가 바뀌면 최적 전략이 달라집니다. 이 리허설은 단순 벤치마크가 아니라 운영 사고를 줄이는 예방 작업입니다.

## 보강 메모

N+1은 ORM 지식 문제가 아니라 운영 비용 문제입니다. 같은 기능이더라도 로딩 전략이 다르면 DB CPU, 네트워크 전송량, 응답 지연이 동시에 바뀝니다. 그래서 로딩 전략 선택은 성능 최적화가 아니라 기능 설계의 일부로 다루는 편이 맞습니다.

추가로, 배치 작업에서는 관계 컬렉션을 통째로 붙이지 말고 필요한 집계만 별도 쿼리로 가져오면 메모리와 네트워크를 함께 줄일 수 있습니다.

또 하나의 실전 팁은 API 응답 스키마와 로딩 전략 매핑 표를 문서화해 두는 것입니다. 어떤 엔드포인트가 어떤 관계를 필수로 요구하는지 명시하면 신규 기능 추가 시 N+1 회귀가 눈에 띄게 줄어듭니다.

실무에서는 로딩 전략 결정 기록을 ADR로 남겨 두면 팀 합의가 유지됩니다. 성능 회귀가 발생했을 때 왜 해당 전략을 선택했는지 바로 추적할 수 있기 때문입니다.

이 문서화 습관만으로도 신규 팀원이 성능 함정을 피하는 데 큰 도움이 됩니다.

## 처음 질문으로 돌아가기

- **기본 lazy 로딩은 어떤 상황에서 N+1을 만들까요?**
  - 본문의 기준은 로딩 전략과 N+1 문제: lazy/joined/selectin을 언제 골라야 하는가를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **`joinedload`와 `selectinload`는 각각 어떤 쿼리를 추가로 만들까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **컬렉션 관계에서는 왜 `selectinload`가 더 자주 권장될까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [SQLAlchemy 101 (1/10): SQLAlchemy 2.x 시작하기 - Engine과 Connection의 본질](./01-sqlalchemy-2x-engine-connection.md)
- [SQLAlchemy 101 (2/10): SQLAlchemy Core - MetaData, Table, Column으로 schema를 Python 객체로 만들기](./02-core-metadata-table-types.md)
- [SQLAlchemy 101 (3/10): SQLAlchemy Core - select·insert·update·delete를 2.x style로 다루기](./03-core-select-insert-update-delete.md)
- [SQLAlchemy 101 (4/10): ORM 기초: DeclarativeBase와 mapped_column으로 모델 정의하기](./04-orm-declarative-mapped-column.md)
- [SQLAlchemy 101 (5/10): Session 깊이 보기: Unit of Work와 Identity Map의 동작 원리](./05-session-unit-of-work-identity-map.md)
- [SQLAlchemy 101 (6/10): ORM 관계 매핑: relationship과 back_populates로 양방향 탐색 안전하게 잇기](./06-relationships-back-populates.md)
- **SQLAlchemy 101 (7/10): 로딩 전략과 N+1 문제: lazy/joined/selectin을 언제 골라야 하는가 (현재 글)**
- SQLAlchemy 101 (8/10): 이벤트, hybrid_property, 그리고 커스텀 타입 (예정)
- SQLAlchemy 101 (9/10): 비동기 SQLAlchemy: aiosqlite와 AsyncSession (예정)
- SQLAlchemy 101 (10/10): 프로덕션 패턴: 풀, 관측, 마이그레이션, 배포 (예정)

<!-- toc:end -->

## 참고 자료

- [SQLAlchemy 2.x Loading Relationships](https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html)
- [`selectinload` deep dive](https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#sqlalchemy.orm.selectinload)
- [`joinedload` and result uniquing](https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#joined-eager-loading)
- [`raiseload` for forbidding lazy](https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#preventing-unwanted-lazy-loads-with-raiseload)

## 정리와 다음 글

기본 lazy 로딩은 코드를 읽기 쉽게 만들지만, 무신경하게 두면 N+1을 만듭니다. 일대다와 다대다는 `selectinload`로, 다대일과 일대일은 `joinedload`로 미리 끌어오는 것이 일반적인 권장 패턴입니다. `joinedload`는 부모 row 중복을 만들 수 있으므로 `unique()`를 잊지 말아야 합니다. `raiseload`는 N+1을 즉시 노출시키는 강력한 도구이며, query count assertion과 함께 회귀 방지에 매우 효과적입니다. 다음 글에서는 이벤트 시스템과 hybrid property, 사용자 정의 타입을 다루며, ORM이 단순 데이터 매핑을 넘어 도메인 표현 도구로 어떻게 확장되는지를 살펴봅니다.

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/sqlalchemy-101/ko)

Tags: Python, SQLAlchemy, ORM, Database
