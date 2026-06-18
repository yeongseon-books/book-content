---
title: "바이브코딩을 위한 SQLAlchemy 기초 (7/10): 로딩 전략과 N+1"
series: sqlalchemy-101
episode: 7
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - SQLAlchemy
  - Python
  - ORM
  - NplusOne
---

# 바이브코딩을 위한 SQLAlchemy 기초 (7/10): 로딩 전략과 N+1

이 글은 "바이브코딩을 위한 SQLAlchemy 기초" 시리즈의 일곱 번째 글입니다.

---

바이브코딩에서 AI는 SQLAlchemy ORM 쿼리 코드를 빠르게 만들어 줍니다. `session.execute(select(User)).scalars().all()`처럼 깔끔한 코드가 순식간에 생성됩니다. 그런데 이 코드에서 `user.posts`처럼 관계 속성에 접근하는 순간 예상치 못한 SELECT가 수십, 수백 번 추가로 나갑니다.

ORM이 가장 자주 비판받는 이유는 쿼리 횟수가 눈에 보이지 않는다는 사실입니다. 100명의 사용자를 가져와 각 사용자의 게시글 수를 출력하는 핸들러가 1 + 100 = 101번의 SELECT를 실행하는 것이 N+1 문제입니다. 코드 한 줄은 단순해 보이지만 실제로는 SELECT가 수십 번 나가고, 단일 쿼리라면 5ms일 작업이 800ms로 늘어납니다.

AI가 만든 ORM 코드에는 기본 lazy 로딩이 그대로 남아있는 경우가 많습니다. 로딩 전략을 명시하지 않으면 관계 속성에 접근할 때마다 추가 SELECT가 발사됩니다.

> **핵심 인사이트:** lazy 로딩은 관계 속성에 접근할 때마다 추가 SELECT를 발사합니다. 컬렉션(일대다) 로딩에는 `selectinload`가, 단일 객체(다대일, 일대일) 로딩에는 `joinedload`가 더 자주 권장됩니다. `raiseload`로 의도치 않은 lazy 로딩을 조기에 차단하세요.

## 이 글에서 다룰 문제

- 기본 lazy 로딩은 어떤 상황에서 N+1을 만들까요?
- `joinedload`와 `selectinload`는 각각 어떤 쿼리를 생성할까요?
- 컬렉션 관계에서 왜 `selectinload`가 더 자주 권장될까요?
- `raiseload`는 언제 사용해야 할까요?
- AI가 만든 ORM 쿼리 코드에서 N+1 위험을 어떻게 확인하나요?

## 로딩 전략 핵심 패턴

```python
from sqlalchemy.orm import selectinload, joinedload, raiseload
from sqlalchemy import select

# N+1 문제: lazy 로딩의 함정
with session:
    users = session.execute(select(User)).scalars().all()
    for user in users:
        print(user.posts)  # 각 user마다 SELECT posts 추가 발사!
        # N명이면 1 + N번 SELECT

# selectinload: 컬렉션(일대다)에 권장
with session:
    users = session.execute(
        select(User).options(selectinload(User.posts))
    ).scalars().all()
    # SELECT users (1번) + SELECT posts WHERE user_id IN (...) (1번)
    # 총 2번으로 해결
    for user in users:
        print(user.posts)  # 추가 SELECT 없음
```

```python
# joinedload: 단일 객체 관계(다대일, 일대일)에 권장
with session:
    posts = session.execute(
        select(Post).options(joinedload(Post.author))
    ).scalars().all()
    # SELECT posts JOIN users (1번으로 해결)
    # 컬렉션에서 joinedload → 중복 행 문제 발생 가능

# raiseload: 의도치 않은 lazy 로딩 차단
with session:
    users = session.execute(
        select(User).options(raiseload(User.posts))
    ).scalars().all()
    try:
        _ = users[0].posts  # InvalidRequestError 즉시 발생
    except Exception as e:
        print(f"Lazy loading blocked: {e}")
        # 개발 중 N+1 위치를 조기에 발견하는 도구
```

```python
# 중첩 로딩: User → Post → Comment
with session:
    users = session.execute(
        select(User).options(
            selectinload(User.posts).selectinload(Post.comments)
        )
    ).scalars().all()
    # SELECT users, SELECT posts WHERE ..., SELECT comments WHERE ...
    # 총 3번 (N+1 없음)

# echo=True로 실제 SQL 횟수 확인
engine = create_engine("sqlite:///app.db", echo=True)
```

## 변경 전후 비교

**Before: 로딩 전략 미설정**
```text
- 관계 속성 기본값 lazy 로딩
- user.posts 접근 시마다 SELECT 추가 발사
- 100명의 사용자 → 101번 SELECT
- echo=True로 확인 전까지 문제 모름
- 게시글 50건 + 태그 → 51번 SELECT
```

**After: 명시적 로딩 전략**
```text
- selectinload(User.posts)로 컬렉션 일괄 로딩
- joinedload(Post.author)로 단일 객체 JOIN 로딩
- 2번 SELECT로 100명 + 게시글 처리
- raiseload로 개발 중 lazy 로딩 즉시 차단
- echo=True로 실제 SQL 횟수 검증
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 로딩 전략 없이 관계 접근 | N+1 문제 발생 | `selectinload` 또는 `joinedload` 명시 |
| 컬렉션에 `joinedload` 사용 | 중복 행 발생 가능 | 컬렉션에는 `selectinload` 사용 |
| 단일 객체에 `selectinload` | 불필요한 두 번째 쿼리 | 다대일에는 `joinedload` 사용 |
| `echo=True` 없이 쿼리 수 추측 | N+1 발견 못 함 | 개발 중 `echo=True`로 SQL 확인 |
| `raiseload` 미사용 | N+1 위치를 프로덕션에서 발견 | 개발/스테이징에서 `raiseload`로 조기 발견 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"SQLAlchemy ORM으로 User 목록과 각 User의 Post를 함께 조회해줘.
N+1 문제 없이 2번 이하의 SELECT로,
컬렉션에 selectinload 사용,
단일 객체 관계에 joinedload 사용,
echo=True로 SQL 확인 가능하게"

# AI 결과물 검증 체크포인트:
# - 관계 속성에 접근하는 루프에서 로딩 전략이 없는가? (없으면 N+1)
# - 컬렉션에 joinedload를 사용하는가? (중복 행 문제)
# - select().options()로 명시적 로딩 전략이 설정되어 있는가?
# - echo=True나 SQL 카운터로 실제 쿼리 횟수를 검증하는가?
```

## 운영 체크리스트

- [ ] 루프 안에서 관계 속성에 접근하는 코드에 `selectinload` 또는 `joinedload`를 설정한다
- [ ] 컬렉션(일대다)에 `selectinload`, 단일 객체(다대일)에 `joinedload`를 선택한다
- [ ] `echo=True`로 개발 중 실제 SQL 횟수를 확인한다
- [ ] 개발/스테이징 환경에서 `raiseload`로 의도치 않은 lazy 로딩을 차단한다
- [ ] 중첩 로딩이 필요하면 `.selectinload(...).selectinload(...)`로 체이닝한다

## 처음 질문으로 돌아가기

- **N+1 문제가 왜 심각한가?** 100명의 사용자 목록과 각 사용자의 게시글을 조회하면 1 + 100 = 101번의 SELECT가 발사됩니다. 5ms짜리 단일 쿼리가 500ms짜리 핸들러가 됩니다. 트래픽이 늘수록 DB 부하가 선형으로 증가합니다.
- **`selectinload`와 `joinedload`의 선택 기준은?** `selectinload`는 별도의 SELECT IN 쿼리로 컬렉션을 가져옵니다. 중복 행 없이 일대다를 처리하기에 적합합니다. `joinedload`는 JOIN으로 단일 쿼리에서 데이터를 가져오지만, 컬렉션에서는 중복 행이 생길 수 있습니다. 단일 객체(다대일)에는 `joinedload`가 더 효율적입니다.
- **`raiseload`는 언제 사용하는가?** 개발 중 "이 쿼리에서 lazy 로딩이 발생하면 즉시 오류를 내라"는 안전망입니다. N+1이 생길 수 있는 위치를 프로덕션이 아닌 개발 단계에서 발견하는 데 유용합니다.

## 정리

바이브코딩에서 AI가 만든 ORM 쿼리 코드에서 루프 안 관계 속성 접근, 컬렉션에 `joinedload` 사용, 로딩 전략 미설정을 확인하세요. `selectinload`와 `joinedload`를 상황에 맞게 선택하고, `echo=True`로 실제 SQL 횟수를 검증하면 N+1 문제를 사전에 잡을 수 있습니다. 다음 글에서는 이벤트, `hybrid_property`, 커스텀 타입을 다룹니다.

## 참고 자료

- [SQLAlchemy 2.x - Relationship Loading Techniques](https://docs.sqlalchemy.org/en/20/orm/loading_relationships.html)
- [SQLAlchemy 2.x - Selectin Loading](https://docs.sqlalchemy.org/en/20/orm/loading_relationships.html#select-in-loading)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/sqlalchemy-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 SQLAlchemy 기초 (1/10): Engine과 Connection
- 바이브코딩을 위한 SQLAlchemy 기초 (2/10): MetaData와 Schema
- 바이브코딩을 위한 SQLAlchemy 기초 (3/10): Core CRUD
- 바이브코딩을 위한 SQLAlchemy 기초 (4/10): ORM 모델 정의
- 바이브코딩을 위한 SQLAlchemy 기초 (5/10): Session과 Unit of Work
- 바이브코딩을 위한 SQLAlchemy 기초 (6/10): 관계 매핑
- **바이브코딩을 위한 SQLAlchemy 기초 (7/10): 로딩 전략과 N+1 (현재 글)**
- 바이브코딩을 위한 SQLAlchemy 기초 (8/10): 이벤트와 확장점
- 바이브코딩을 위한 SQLAlchemy 기초 (9/10): 비동기 SQLAlchemy
- 바이브코딩을 위한 SQLAlchemy 기초 (10/10): 프로덕션 패턴
<!-- toc:end -->

Tags: 바이브코딩, SQLAlchemy, Python, ORM, NplusOne
