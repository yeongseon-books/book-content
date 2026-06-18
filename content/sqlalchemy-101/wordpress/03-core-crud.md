---
series: sqlalchemy-101
episode: 3
title: "바이브코딩을 위한 SQLAlchemy (3/10): select·insert·update·delete를 2.x style로 다루기"
status: publish-ready
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - SQLAlchemy
  - Python
  - CRUD
  - Database
---

# 바이브코딩을 위한 SQLAlchemy (3/10): select·insert·update·delete를 2.x style로 다루기

이 글은 "바이브코딩을 위한 SQLAlchemy" 시리즈의 세 번째 글입니다. AI가 생성한 쿼리 코드에서 가장 흔히 보이는 문제는 1.x 스타일과 2.x 스타일이 섞인 것입니다. `session.execute()`와 `conn.execute()`가 혼용되고, Result 객체를 잘못 처리하는 코드가 나옵니다.

---

## 바이브코딩 현장에서 이 문제가 왜 생기는가

AI 모델은 SQLAlchemy 1.x와 2.x 코드를 모두 학습했습니다. 그래서 "SQLAlchemy 쿼리 코드 작성해 줘"라고만 하면 두 버전의 코드가 뒤섞여 나올 수 있습니다. `engine.execute()`(1.x에서 deprecated), `query.filter_by()`(ORM 스타일), `select().where()`(Core 스타일)가 한 파일에 있는 경우도 봅니다.

2.x에서 중요한 변화는 `Result` 객체입니다. `fetchall()`이 아니라 `scalars()`, `mappings()`, `all()` 같은 메서드로 결과를 다루는 방식이 표준이 되었습니다. 이 차이를 모르면 생성된 코드가 왜 타입 오류를 내는지 이해할 수 없습니다.

SQL 표현식은 Python 연산자로 조합할 수 있습니다. `select(users).where(users.c.id == 1)`처럼 쓰면 SQL 인젝션 없이 안전한 파라미터화 쿼리가 만들어집니다. JOIN, CTE, subquery도 같은 방식으로 조합합니다.

`text()`는 원시 SQL을 써야 할 때 사용합니다. 하지만 파라미터는 반드시 바인드 파라미터로 처리해야 합니다. f-string으로 값을 직접 넣으면 SQL 인젝션에 취약해집니다.

> "SQL 표현식 빌더는 Python으로 SQL을 조립하는 도구입니다. 완성된 조립품은 데이터베이스로 보내기 전에 자동으로 파라미터화됩니다."

---

## 이 글에서 답할 질문 5가지

1. SQLAlchemy 2.x에서 `select()`는 어떻게 사용하나요?
2. `Result` 객체에서 행을 꺼내는 방법에는 무엇이 있나요?
3. `text()`를 안전하게 사용하는 방법은 무엇인가요?
4. JOIN과 서브쿼리는 어떻게 표현하나요?
5. INSERT, UPDATE, DELETE의 2.x 스타일은 무엇인가요?

---

## Core CRUD 핵심 개념

### SELECT

```python
from sqlalchemy import select

stmt = select(users).where(users.c.name == "Alice")

with engine.connect() as conn:
    result = conn.execute(stmt)
    for row in result:
        print(row.name, row.email)
```

### INSERT

```python
from sqlalchemy import insert

stmt = insert(users).values(name="Bob", email="bob@example.com")

with engine.begin() as conn:
    conn.execute(stmt)
```

### UPDATE

```python
from sqlalchemy import update

stmt = (
    update(users)
    .where(users.c.id == 1)
    .values(name="Robert")
)

with engine.begin() as conn:
    conn.execute(stmt)
```

### DELETE

```python
from sqlalchemy import delete

stmt = delete(users).where(users.c.id == 1)

with engine.begin() as conn:
    conn.execute(stmt)
```

### Result 객체 다루기

```python
result = conn.execute(select(users))

# 전체 행 리스트
rows = result.all()

# 매핑(딕셔너리 형태)
mappings = result.mappings().all()

# 첫 번째 행
first = result.first()

# 스칼라 값 (단일 컬럼)
names = result.scalars().all()
```

---

## Before / After 비교

| 항목 | Before (1.x 스타일) | After (2.x 스타일) |
| --- | --- | --- |
| 쿼리 실행 | `engine.execute(stmt)` | `conn.execute(stmt)` |
| 결과 처리 | `result.fetchall()` | `result.all()` 또는 `result.mappings()` |
| ORM 쿼리 | `session.query(User)` | `session.execute(select(User))` |
| raw SQL | f-string 삽입 | `text()`와 바인드 파라미터 |

---

## 자주 하는 실수

| 실수 | 원인 | 해결 |
| --- | --- | --- |
| `engine.execute()` 사용 | 1.x 패턴 | `with engine.connect() as conn` |
| f-string으로 값 삽입 | SQL 인젝션 위험 | `:param` 바인드 파라미터 사용 |
| Result 소진 후 재사용 | cursor 특성 이해 부족 | `.all()`로 리스트화 후 재사용 |
| 트랜잭션 없이 UPDATE | `connect()` 사용 | `begin()` 또는 명시적 `commit()` |

---

## AI 활용 팁

> "SQLAlchemy 2.x Core 방식으로 users 테이블에서 active=True인 사용자를 조회하고, 이름 기준으로 정렬하는 select 쿼리를 작성해 줘. `engine.connect()` 컨텍스트 매니저와 `result.mappings().all()`을 사용해 줘."

생성된 코드 확인 포인트:
- `engine.execute()` 사용 여부(2.x에서 제거됨)
- f-string 또는 문자열 연결로 파라미터 삽입 여부
- Result 재사용 문제 여부

---

## 체크리스트

- [ ] `engine.execute()` 대신 `conn.execute()`를 사용하는가
- [ ] 바인드 파라미터(`:param`)로 값을 전달하는가
- [ ] 쓰기 작업에 `engine.begin()` 또는 `commit()`을 사용하는가
- [ ] `Result.all()`로 미리 소비하여 재사용하는가
- [ ] JOIN은 `.join()` 또는 `select().join()` 방식을 사용하는가

---

## 처음 질문으로 돌아가기

**`engine.execute()`를 쓰면 안 되나요?**
SQLAlchemy 2.x에서 제거되었습니다. `with engine.connect() as conn: conn.execute()` 패턴을 사용해야 합니다.

**`fetchall()`과 `all()`의 차이는?**
둘 다 결과를 리스트로 반환하지만, 2.x에서는 `all()`, `scalars().all()`, `mappings().all()` 메서드를 사용하는 것이 표준입니다.

---

## 정리

2.x의 Core CRUD는 `conn.execute()`, SQL 표현식 빌더, Result 객체를 중심으로 구성됩니다. `text()`는 바인드 파라미터와 함께 사용해야 안전합니다. 다음 글에서는 ORM 모델을 DeclarativeBase와 mapped_column으로 정의하는 방법을 살펴봅니다.

---

## 참고 자료

- [SQLAlchemy Core SELECT](https://docs.sqlalchemy.org/en/20/core/selectable.html)
- [SQLAlchemy Working with Data](https://docs.sqlalchemy.org/en/20/tutorial/data.html)

---

<!-- toc:begin -->
## 시리즈 목차

1. 바이브코딩을 위한 SQLAlchemy (1/10): Engine과 Connection의 본질
2. 바이브코딩을 위한 SQLAlchemy (2/10): MetaData, Table, Column으로 schema를 Python 객체로 만들기
3. **바이브코딩을 위한 SQLAlchemy (3/10): select·insert·update·delete를 2.x style로 다루기 (현재 글)**
4. 바이브코딩을 위한 SQLAlchemy (4/10): DeclarativeBase와 mapped_column으로 모델 정의하기
5. 바이브코딩을 위한 SQLAlchemy (5/10): Session 깊이 보기: Unit of Work와 Identity Map의 동작 원리
6. 바이브코딩을 위한 SQLAlchemy (6/10): relationship과 back_populates로 양방향 탐색 안전하게 잇기
7. 바이브코딩을 위한 SQLAlchemy (7/10): 로딩 전략과 N+1 문제: lazy/joined/selectin을 언제 골라야 하는가
8. 바이브코딩을 위한 SQLAlchemy (8/10): 이벤트, hybrid_property, 그리고 커스텀 타입
9. 바이브코딩을 위한 SQLAlchemy (9/10): 비동기 SQLAlchemy: aiosqlite와 AsyncSession
10. 바이브코딩을 위한 SQLAlchemy (10/10): 프로덕션 패턴: 풀, 관측, 마이그레이션, 배포
<!-- toc:end -->

Tags: 바이브코딩, SQLAlchemy, Python, CRUD, Database
