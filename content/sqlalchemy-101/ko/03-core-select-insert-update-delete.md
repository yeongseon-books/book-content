---
title: SQLAlchemy Core - select·insert·update·delete를 2.x style로 다루기
series: sqlalchemy-101
episode: 3
language: ko
status: draft
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
- Python
- SQLAlchemy
- Core
- SQL Expression
- Result
- SQLite
last_reviewed: '2026-05-03'
---

# SQLAlchemy Core - select·insert·update·delete를 2.x style로 다루기

> SQLAlchemy 101 시리즈 (3/10)

---

2편에서 우리는 `MetaData`와 `Table`로 schema를 Python 객체로 만들었습니다. 이제 그 객체로 실제 SQL을 빌드할 차례입니다. raw `text()`만으로도 SQL을 실행할 수는 있지만, Core SQL expression의 진가는 Python으로 SQL을 조립하면서 컴파일 단계에서 typo와 type 오류를 잡고, dialect 차이에 흔들리지 않게 만드는 데 있습니다.

이 글은 SQLAlchemy 2.x style의 `select()`, `insert()`, `update()`, `delete()`와 결과를 다루는 `Result`/`Row` 객체를 정리합니다. 1편의 Engine, 2편의 schema가 여기서 합쳐져 한 권의 작은 작업 매뉴얼이 됩니다.

## 이 글에서 배울 것

- 2.x style의 통일된 `select()` 구성: `select(...)`, `where()`, `order_by()`, `limit()`, `offset()`, `group_by()`, `having()`
- `Result` 객체의 모양과 `.all()`, `.first()`, `.one()`, `.one_or_none()`, `.scalars()`, `.mappings()`의 의미
- `insert(table).values(...)`와 `executemany`-스타일 dict list 입력
- `inserted_primary_key`로 새로 생긴 PK 받기, `Insert.from_select()`로 INSERT-SELECT 구성
- `update(table).where(...).values(...)`와 RETURNING 사용 (SQLite 3.35+)
- `delete(table).where(...)`의 안전한 패턴과 "모두 지우기"의 위험
- JOIN을 표현하는 두 가지 방식: `select.join()`과 `select(...).select_from(a.join(b))`
- Subquery, CTE(`select.cte()`), `func.*` 집계 함수의 기본 사용

## 이 글에서 답할 질문

- 1.x의 `select([users])`와 2.x의 `select(users)`는 어떻게 다른가?
- `Result.all()`이 반환하는 것은 `list[Row]`인가, `list[tuple]`인가?
- INSERT 후 새로 생긴 ID는 어디서 받는가?
- UPDATE에 LIMIT을 걸고 싶을 때 SQLite에서는 어떻게 하나?
- DELETE 절에 WHERE를 까먹으면 무엇이 일어나는가?
- JOIN을 가장 간결하게 적는 2.x 패턴은 무엇인가?

## 왜 중요한가

raw SQL 문자열로만 작업하면 다음 세 가지 비용이 누적됩니다. 첫째, 컬럼 이름 변경이 발생할 때마다 application 전체 grep이 필요합니다. 둘째, 같은 SQL을 여러 곳에서 약간씩 다르게 적게 되어 동작이 미묘하게 달라집니다. 셋째, dialect 차이를 모두 손으로 처리해야 합니다.

Core SQL expression은 schema 객체와 Python 표현식을 조합해 SQL을 구성하므로 첫 두 비용을 거의 0으로 만듭니다. 컬럼 이름 변경은 schema 한 곳만 바꾸면 import 시점에 영향을 받는 모든 expression이 자동으로 따라옵니다. 같은 select 객체를 함수로 캡슐화해 재사용할 수 있고, dialect 별 차이는 SQLAlchemy compiler가 알아서 풀어줍니다.

또한 ORM이 본격적으로 등장하는 4편 이후에도 Core SQL expression은 사라지지 않습니다. ORM의 `select()`는 Core의 `select()`와 같은 객체이고, 복잡한 쿼리에서는 결국 Core 표현식으로 내려와야 합니다. 이 글이 그 토대를 만듭니다.

## Mental Model

2.x style의 SQL은 "절(clause)을 메서드 chaining으로 쌓는 식"입니다. `select(...)`로 시작해서 `where`, `order_by`, `limit` 같은 메서드를 호출하면 새로운 statement 객체가 반환되고, 마지막에 Connection이 그것을 실행해 `Result`를 돌려줍니다.

> 2.x의 select은 immutable한 statement 객체다. 메서드를 호출할 때마다 원본은 변하지 않고 새로운 statement가 만들어진다. Result는 한 번만 순회 가능한 stream-like 객체이며, 무엇을 꺼낼지(`Row`, scalar, mapping)는 Result에서 결정한다.

```
select(users.c.id, users.c.name)        # statement 1
   .where(users.c.email == "a@x.com")   # statement 2
   .order_by(users.c.id)                 # statement 3
   .limit(10)                            # statement 4
                  │
                  ▼
       conn.execute(stmt) → Result
                  │
       ┌──────────┼─────────────┐
       ▼          ▼             ▼
   .all()    .scalars()    .mappings()
   list[Row] ScalarResult  MappingResult
              .all() →     .all() →
              list[T]      list[dict]
```

이 mental model이 잡히면 INSERT/UPDATE/DELETE도 같은 패턴으로 적힙니다. 그저 시작 함수가 `insert/update/delete`로 바뀔 뿐입니다.

## 핵심 개념

### select 기본형

```python
from sqlalchemy import select
from schema import users

stmt = (
    select(users.c.id, users.c.name)
    .where(users.c.email == "alice@example.com")
    .order_by(users.c.id.desc())
    .limit(5)
)

with engine.connect() as conn:
    rows = conn.execute(stmt).all()
    for row in rows:
        print(row.id, row.name)
```

`select(*cols_or_tables)`는 SELECT 대상이 될 컬럼이나 테이블을 받습니다. `select(users)`처럼 테이블 전체를 넣으면 모든 컬럼이 select됩니다. WHERE 절은 Python 비교 연산자(`==`, `!=`, `<`, `<=`, `>`, `>=`, `.in_(...)`, `.like(...)`, `.is_(None)`)를 그대로 씁니다. 여러 조건은 콤마(`AND`) 또는 `or_()`/`and_()` 함수로 결합합니다.

```python
from sqlalchemy import or_, and_

stmt = select(users).where(
    or_(users.c.name == "Alice", users.c.name == "Bob"),
    users.c.email.like("%@example.com"),
)
```

### Result 다루기

`conn.execute(stmt)`는 `Result` 객체를 돌려주고, 그 위에서 다양한 형태로 데이터를 꺼냅니다.

| 메서드 | 반환 |
| --- | --- |
| `.all()` | `list[Row]` |
| `.first()` | `Row | None` |
| `.one()` | `Row` (없거나 둘 이상이면 예외) |
| `.one_or_none()` | `Row | None` (둘 이상이면 예외) |
| `.scalar()` | 단일 컬럼 단일 값 |
| `.scalar_one()` | 단일 컬럼 단일 값, 없거나 둘 이상이면 예외 |
| `.scalars().all()` | 첫 컬럼만 모아 `list` |
| `.mappings().all()` | `list[dict]`처럼 동작하는 list |

`Row`는 named tuple처럼 동작합니다. `row.name`, `row[1]`, `row._mapping["name"]` 모두 가능합니다. ORM/Core 양쪽에서 같은 인터페이스를 갖습니다.

`.scalars()`는 select가 단일 객체(`select(users)`)를 반환할 때 자주 씁니다. ORM에서 자주 등장하지만 Core에서도 동일합니다.

### insert

```python
from sqlalchemy import insert

with engine.begin() as conn:
    result = conn.execute(
        insert(users).values(name="Alice", email="alice@example.com")
    )
    print(result.inserted_primary_key)   # (1,)
```

여러 row를 한 번에 넣을 때는 list of dicts를 두 번째 인자로 넘깁니다.

```python
with engine.begin() as conn:
    conn.execute(
        insert(users),
        [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": "Bob",   "email": "bob@example.com"},
        ],
    )
```

이 형식은 dialect에 따라 `executemany`로 매핑되며 보통 가장 빠른 bulk insert 경로입니다.

#### INSERT-SELECT

다른 테이블에서 데이터를 골라 그대로 넣고 싶을 때:

```python
from sqlalchemy import insert, select

stmt = insert(archive_users).from_select(
    ["id", "name", "email"],
    select(users.c.id, users.c.name, users.c.email).where(users.c.active.is_(False)),
)
with engine.begin() as conn:
    conn.execute(stmt)
```

#### RETURNING (SQLite 3.35+)

SQLite 3.35부터는 INSERT/UPDATE/DELETE에 RETURNING 절이 가능합니다.

```python
from sqlalchemy import insert

stmt = insert(users).values(name="Alice", email="a@x.com").returning(users.c.id, users.c.created_at)
with engine.begin() as conn:
    new_id, created_at = conn.execute(stmt).one()
```

오래된 SQLite (3.34 이하)에서는 동작하지 않으므로 환경 호환성을 확인합니다.

### update

```python
from sqlalchemy import update

stmt = (
    update(users)
    .where(users.c.email == "alice@example.com")
    .values(name="Alice Liddell")
)
with engine.begin() as conn:
    result = conn.execute(stmt)
    print(result.rowcount)   # 영향받은 row 수
```

`update`도 RETURNING을 지원합니다(SQLite 3.35+):

```python
stmt = update(users).where(users.c.id == 1).values(name="Alice").returning(users.c.id, users.c.name)
```

#### UPDATE-LIMIT 주의

SQLite는 기본적으로 `UPDATE ... LIMIT`을 지원하지 않습니다(빌드 옵션에 따라 다름). 이식성 있는 방법은 subquery로 대상 PK를 골라내는 것입니다.

```python
sub = select(users.c.id).where(users.c.active.is_(False)).limit(100).scalar_subquery()
stmt = update(users).where(users.c.id.in_(sub)).values(active=True)
```

### delete

```python
from sqlalchemy import delete

stmt = delete(users).where(users.c.id == 42)
with engine.begin() as conn:
    conn.execute(stmt)
```

WHERE 없는 `delete(users)`는 전체 테이블을 지웁니다. 사고를 막기 위해 application 코드에서는 WHERE 없는 delete를 명시적으로 금지하는 helper를 두는 편이 안전합니다.

```python
def safe_delete(conn, table, condition):
    if condition is None:
        raise ValueError("WHERE-less delete is forbidden")
    return conn.execute(delete(table).where(condition))
```

### JOIN

JOIN은 두 가지 방식으로 적을 수 있습니다.

```python
# A: select(...).join(...)
stmt = (
    select(users.c.name, posts.c.title)
    .join(posts, posts.c.user_id == users.c.id)
    .order_by(posts.c.created_at.desc())
)

# B: select(...).select_from(a.join(b, ...))
joined = users.join(posts, posts.c.user_id == users.c.id)
stmt = select(users.c.name, posts.c.title).select_from(joined)
```

A 형식이 짧고 가장 흔하지만, 여러 테이블을 복잡하게 결합할 때는 B 형식이 더 명확합니다. Foreign key가 정의되어 있으면 `select(...).join(posts)`처럼 ON 절을 생략할 수도 있습니다.

LEFT OUTER JOIN은 `outerjoin()`을 씁니다.

```python
stmt = select(users.c.name, posts.c.title).outerjoin(posts, posts.c.user_id == users.c.id)
```

### Subquery와 CTE

```python
sub = select(posts.c.user_id).where(posts.c.title.like("%news%")).subquery()
stmt = select(users).join(sub, sub.c.user_id == users.c.id)
```

CTE는 `select.cte("name")`로 만듭니다.

```python
recent = (
    select(posts.c.user_id, posts.c.title)
    .where(posts.c.created_at > "2026-01-01")
    .cte("recent")
)
stmt = select(recent.c.user_id, recent.c.title)
```

### 집계 함수

`func` namespace로 SQL 함수를 호출합니다.

```python
from sqlalchemy import func

stmt = select(users.c.id, func.count(posts.c.id).label("post_count")).join(posts).group_by(users.c.id)
```

`label()`로 alias를 주면 `row.post_count`로 접근할 수 있습니다.

## Before-After

### Before: text 기반 동적 쿼리

```python
def find_users(active=None, email_like=None, limit=10):
    sql = "SELECT id, name, email FROM users WHERE 1=1"
    params = {}
    if active is not None:
        sql += " AND active = :active"; params["active"] = active
    if email_like:
        sql += " AND email LIKE :email"; params["email"] = email_like
    sql += f" LIMIT {limit}"   # 위험: int 캐스팅 안 함
    with engine.connect() as conn:
        return conn.execute(text(sql), params).all()
```

문제: 문자열 조립이 깨지기 쉽고, `LIMIT`처럼 binding되지 않는 부분에서 type 오류·SQL injection 위험이 생깁니다.

### After: select 기반 동적 쿼리

```python
from sqlalchemy import select
from schema import users

def find_users(active=None, email_like=None, limit=10):
    stmt = select(users.c.id, users.c.name, users.c.email)
    if active is not None:
        stmt = stmt.where(users.c.active.is_(active))
    if email_like:
        stmt = stmt.where(users.c.email.like(email_like))
    stmt = stmt.limit(int(limit))
    with engine.connect() as conn:
        return conn.execute(stmt).all()
```

이제 컬럼 이름 typo는 schema 단계에서 잡히고, `LIMIT` 값도 SQLAlchemy compiler가 안전하게 다룹니다. `stmt`는 immutable하므로 `where`/`limit`을 누적할 때마다 새 statement가 만들어져 race condition도 없습니다.

## 단계별 실습

### 1단계: 데이터 준비

```python
from sqlalchemy import create_engine, insert
from schema import metadata, users, posts

engine = create_engine("sqlite:///app.db")
metadata.create_all(engine)

with engine.begin() as conn:
    conn.execute(insert(users), [
        {"name": "Alice", "email": "alice@example.com"},
        {"name": "Bob",   "email": "bob@example.com"},
    ])
    conn.execute(insert(posts), [
        {"user_id": 1, "title": "hello",      "body": "first post"},
        {"user_id": 1, "title": "news today", "body": "second post"},
        {"user_id": 2, "title": "intro",      "body": "bob's first"},
    ])
```

### 2단계: 다양한 select

```python
from sqlalchemy import select, func
from schema import users, posts

with engine.connect() as conn:
    # 1) 단순 select
    rows = conn.execute(select(users)).all()

    # 2) 조건과 정렬
    rows = conn.execute(
        select(users.c.id, users.c.name)
        .where(users.c.email.like("%@example.com"))
        .order_by(users.c.id.desc())
    ).all()

    # 3) JOIN과 집계
    rows = conn.execute(
        select(users.c.name, func.count(posts.c.id).label("post_count"))
        .join(posts, posts.c.user_id == users.c.id)
        .group_by(users.c.name)
    ).all()
    for row in rows:
        print(row.name, row.post_count)

    # 4) scalar
    n = conn.execute(select(func.count()).select_from(users)).scalar_one()
    print(f"users={n}")
```

### 3단계: insert / update / delete를 트랜잭션 안에서

```python
from sqlalchemy import insert, update, delete

with engine.begin() as conn:
    # insert + RETURNING
    result = conn.execute(
        insert(users).values(name="Carol", email="carol@example.com").returning(users.c.id)
    )
    cid = result.scalar_one()

    # update
    conn.execute(update(users).where(users.c.id == cid).values(name="Carol C"))

    # delete (안전한 패턴)
    conn.execute(delete(posts).where(posts.c.user_id == cid))
```

### 4단계: subquery와 CTE

```python
from sqlalchemy import select

sub = select(posts.c.user_id).where(posts.c.title.like("%news%")).subquery()
stmt = select(users).join(sub, sub.c.user_id == users.c.id)
print(conn.execute(stmt).all())

cte = select(posts.c.user_id, func.count().label("n")).group_by(posts.c.user_id).cte("c")
stmt = select(users.c.name, cte.c.n).join(cte, cte.c.user_id == users.c.id)
```

## 자주 하는 실수

**1. 1.x style을 그대로 적기.** `select([users])` (list 전달), `engine.execute(stmt)` (Connection 없이 실행), `stmt.execute()` (statement에서 직접 실행)는 모두 2.x에서 제거되었습니다.

**2. `Result.all()` 결과를 두 번 순회하기.** `Result`는 일회용입니다. 다시 순회하려면 `.all()`로 list로 변환한 뒤 그 list를 사용합니다.

**3. `.one()`을 무지성으로 쓰기.** row가 없거나 두 개 이상이면 예외가 나는 strict 메서드입니다. 0개 가능한 경우 `.one_or_none()`, 다수 가능한 경우 `.first()`를 씁니다.

**4. `update`/`delete`에 WHERE를 빼먹기.** 전체 테이블이 영향을 받습니다. helper로 명시적으로 금지하거나 코드 리뷰에서 잡습니다.

**5. JOIN 조건을 빼고 cross join을 만들기.** `select(users, posts)`만 적으면 cross join이 됩니다. 항상 `.join(posts, posts.c.user_id == users.c.id)`를 명시합니다.

**6. SQL injection을 막을 거라 믿고 raw f-string에 user input을 넣기.** Core SQL expression은 자동으로 binding하지만, `text(f"SELECT * FROM users WHERE name = '{name}'")` 같은 코드는 여전히 injection을 만듭니다. binding을 신뢰하려면 `text(...)`에 `:name`을 쓰고 dict로 넘깁니다.

## 실무 적용

실무 코드에서 select은 보통 함수로 캡슐화해서 재사용합니다.

```python
# repos/user_repo.py
from sqlalchemy import select, insert, update
from schema import users

def get_user_by_email(conn, email: str):
    return conn.execute(select(users).where(users.c.email == email)).first()

def create_user(conn, name: str, email: str) -> int:
    return conn.execute(
        insert(users).values(name=name, email=email).returning(users.c.id)
    ).scalar_one()

def deactivate_user(conn, user_id: int) -> int:
    return conn.execute(
        update(users).where(users.c.id == user_id).values(active=False)
    ).rowcount
```

이 패턴의 핵심은 함수가 `Connection`을 인자로 받는다는 점입니다. transaction 경계는 호출 측이 결정하므로 같은 함수가 한 transaction 안에서 다른 함수와 함께 호출될 수 있습니다. ORM의 Session도 같은 원칙으로 동작합니다(5편에서 다룹니다).

읽기 함수가 list를 반환할 때는 `.all()`이 아닌 `.scalars().all()`이나 `.mappings().all()`이 더 다루기 쉬울 때가 많습니다. JSON 응답으로 그대로 직렬화하려면 `.mappings().all()`이 가장 자연스럽습니다.

```python
def list_users_as_dict(conn) -> list[dict]:
    return [dict(m) for m in conn.execute(select(users)).mappings().all()]
```

성능 측면에서는 큰 결과 집합을 한 번에 메모리에 적재하지 않도록 streaming iteration을 활용합니다.

```python
with engine.connect().execution_options(stream_results=True) as conn:
    for row in conn.execute(select(users)):
        process(row)
```

## 체크리스트

- [ ] `select`, `insert`, `update`, `delete`를 모두 2.x style로 적을 수 있다
- [ ] `Row`, `.scalar()`, `.scalars()`, `.mappings()`의 차이를 안다
- [ ] `.first()`, `.one()`, `.one_or_none()`을 상황에 맞게 선택한다
- [ ] WHERE 없는 update/delete를 application 레벨에서 막는다
- [ ] JOIN은 항상 ON 조건을 명시한다 (cross join 회피)
- [ ] SQLite의 RETURNING 지원 버전(3.35+)을 알고 있다
- [ ] subquery와 CTE를 만들 수 있다
- [ ] select 함수로 도메인 로직을 캡슐화하고 Connection을 인자로 받는다

## 연습 문제

1. `users(id, name, email, active)`와 `posts(id, user_id, title, created_at)` schema에서, "지난 30일간 글을 5개 이상 쓴 active user"를 select하는 Core 표현식을 작성하세요. 결과는 `name`, `post_count` 두 컬럼이어야 합니다.
2. RETURNING을 사용해 새 user를 만들고 동시에 PK와 `created_at`을 받는 함수를 작성하세요. SQLite 3.34 이하 환경에서 fallback 경로(`inserted_primary_key`)를 함께 구현하세요.
3. update에 LIMIT 100을 걸어 "비활성 user 100명을 한 번에 활성화"하는 SQLite 호환 코드를 subquery 방식으로 구현하세요.
4. `mappings()`로 select 결과를 list of dict로 받아 JSON 응답을 만들고, 같은 함수에 `stream_results=True`를 적용해 큰 결과 집합을 streaming으로 처리하는 두 버전을 비교하세요.

## 정리·다음 글

이 글에서 우리는 SQLAlchemy Core의 SQL expression을 한 권의 작업 매뉴얼처럼 정리했습니다. `select`/`insert`/`update`/`delete`는 모두 immutable statement 객체이며, `Result`에서 `Row`/scalar/mapping을 자유롭게 꺼낼 수 있습니다. JOIN, subquery, CTE, 집계 함수는 schema 객체와 `func` namespace의 조합으로 표현됩니다. RETURNING이나 streaming 같은 dialect 기능도 SQLAlchemy의 통일된 인터페이스 안에서 자연스럽게 사용할 수 있습니다.

다음 글부터 ORM이 등장합니다. 4편에서는 `DeclarativeBase`와 `mapped_column`으로 Python class를 데이터베이스 row와 매핑하는 방법을 다룹니다. 이 글에서 본 `users.c.name`이 ORM에서는 `User.name`으로 바뀌고, `select(users)`가 `select(User)`로 바뀌는 것이 핵심 차이입니다. Core를 정확히 이해하고 ORM으로 올라가야 ORM의 마법을 디버깅할 수 있습니다.

## 참고 자료

- [SQLAlchemy 2.x - Using SELECT Statements](https://docs.sqlalchemy.org/en/20/tutorial/data_select.html)
- [SQLAlchemy 2.x - Inserting Rows with Core](https://docs.sqlalchemy.org/en/20/tutorial/data_insert.html)
- [SQLAlchemy 2.x - Updating and Deleting Rows](https://docs.sqlalchemy.org/en/20/tutorial/data_update.html)
- [SQLAlchemy 2.x - Result Set API](https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.Result)
- [SQLite RETURNING clause](https://www.sqlite.org/lang_returning.html)

Tags: Python, SQLAlchemy, Core, SQL Expression, Result, SQLite
