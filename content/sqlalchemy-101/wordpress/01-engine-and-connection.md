---
series: sqlalchemy-101
episode: 1
title: "바이브코딩을 위한 SQLAlchemy (1/10): Engine과 Connection의 본질"
status: publish-ready
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - SQLAlchemy
  - Python
  - Database
  - Backend
---

# 바이브코딩을 위한 SQLAlchemy (1/10): Engine과 Connection의 본질

이 글은 "바이브코딩을 위한 SQLAlchemy" 시리즈의 첫 번째 글입니다. AI와 함께 코드를 빠르게 작성할수록, 데이터베이스 연결의 작동 원리를 정확히 이해하는 일이 더 중요해집니다. Engine이 무엇이고 Connection이 왜 별도로 존재하는지 모른 채 코드를 생성하면, 연결 누수와 트랜잭션 오류가 조용히 쌓입니다.

---

## 바이브코딩 현장에서 이 문제가 왜 생기는가

AI에게 "SQLAlchemy로 데이터베이스에 연결하는 코드 만들어 줘"라고 요청하면 대부분 동작하는 코드를 받습니다. 그런데 그 코드를 프로덕션에 올리는 순간 문제가 시작됩니다. 연결 풀이 소진되고, 트랜잭션이 중간에 끊기고, 같은 요청에서 두 개의 연결이 열립니다.

이유는 간단합니다. `Engine`과 `Connection`의 관계를 모르면 AI가 생성한 코드를 검증할 기준 자체가 없기 때문입니다. `create_engine()`이 언제 연결을 만드는지, `with engine.connect()`가 무엇을 보장하는지 알아야 비로소 생성된 코드가 맞는지 틀린지 판단할 수 있습니다.

Engine은 연결 풀을 관리하는 팩토리입니다. 애플리케이션이 시작할 때 한 번만 만들고, 요청마다 재사용합니다. Connection은 실제 데이터베이스와 통신하는 통로입니다. 열고 닫는 비용이 있으므로 컨텍스트 매니저로 관리해야 합니다.

SQLAlchemy 2.x에서는 모든 실행이 트랜잭션 안에서 이루어집니다. `commit()`을 명시적으로 호출하지 않으면 변경사항이 반영되지 않습니다. 이 점이 1.x와 가장 크게 다른 부분입니다.

> "Engine은 공장이고 Connection은 공장에서 빌린 작업대입니다. 작업대는 쓰고 나면 반드시 돌려줘야 합니다."

---

## 이 글에서 답할 질문 5가지

1. `create_engine()`을 호출하면 즉시 데이터베이스에 연결되나요?
2. `engine.connect()`와 `engine.begin()`의 차이는 무엇인가요?
3. 트랜잭션을 명시적으로 커밋하지 않으면 어떻게 되나요?
4. 연결 풀은 언제 활성화되고 언제 반환되나요?
5. SQLAlchemy 1.x 코드를 2.x 스타일로 바꾸려면 무엇을 바꿔야 하나요?

---

## Engine과 Connection 핵심 개념

### Engine: 지연 초기화 팩토리

```python
from sqlalchemy import create_engine

engine = create_engine(
    "sqlite:///example.db",
    echo=True,      # SQL 로그 출력
    pool_size=5,    # 풀 크기
)
```

`create_engine()`은 즉시 데이터베이스에 연결하지 않습니다. 첫 번째 `connect()` 호출이 있을 때 풀이 초기화됩니다. 이 지연 초기화 방식 덕분에 모듈 임포트 시점에 데이터베이스가 없어도 앱이 시작될 수 있습니다.

### Connection: 컨텍스트 매니저로 관리

```python
with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print(result.fetchone())
    conn.commit()  # 2.x에서는 명시적 커밋 필요
```

`with` 블록을 벗어나면 Connection이 자동으로 닫히고 풀에 반환됩니다. 예외가 발생해도 연결 누수가 생기지 않습니다.

### begin(): 자동 커밋 트랜잭션

```python
with engine.begin() as conn:
    conn.execute(text("INSERT INTO users(name) VALUES ('Alice')"))
    # 블록 종료 시 자동 커밋, 예외 발생 시 자동 롤백
```

`begin()`은 블록 종료 시 커밋을, 예외 시 롤백을 자동으로 처리합니다. 단일 트랜잭션 단위 작업에 가장 적합합니다.

---

## Before / After 비교

| 항목 | Before (잘못된 패턴) | After (올바른 패턴) |
| --- | --- | --- |
| 엔진 생성 | 요청마다 `create_engine()` 호출 | 앱 시작 시 한 번만 생성 |
| 연결 관리 | `conn = engine.connect()` 후 수동 close | `with engine.connect()` 사용 |
| 트랜잭션 | 커밋 없이 INSERT | `conn.commit()` 또는 `begin()` 사용 |
| 2.x 스타일 | `engine.execute()` (1.x 방식) | `conn.execute()` (2.x 방식) |

---

## 자주 하는 실수

| 실수 | 원인 | 해결 |
| --- | --- | --- |
| 연결 풀 소진 | `with` 없이 `connect()` 호출 | 항상 컨텍스트 매니저 사용 |
| 변경사항 미반영 | `commit()` 누락 | `begin()` 또는 명시적 `commit()` |
| 엔진 중복 생성 | 함수 안에서 `create_engine()` | 모듈 레벨에서 한 번만 생성 |
| 1.x API 혼용 | `engine.execute()` 사용 | `with engine.connect() as conn` |

---

## AI 활용 팁

AI에게 SQLAlchemy 코드를 요청할 때 이 프롬프트를 사용하세요:

> "SQLAlchemy 2.x 스타일로, `engine.begin()`을 사용하는 단일 트랜잭션 INSERT 코드를 작성해 줘. 모듈 레벨 엔진 생성 패턴을 따르고, 연결 풀 설정 옵션도 포함해 줘."

생성된 코드에서 반드시 확인할 것:
- `engine.execute()` 대신 `conn.execute()` 사용 여부
- `with` 구문으로 연결 관리 여부
- `commit()` 또는 `begin()` 사용 여부

---

## 체크리스트

- [ ] `create_engine()`을 모듈 레벨에서 한 번만 호출하고 있는가
- [ ] 모든 `connect()`가 `with` 구문 안에 있는가
- [ ] 2.x에서 `conn.execute()`를 사용하고 있는가
- [ ] 쓰기 작업 후 `commit()` 또는 `begin()`으로 트랜잭션을 닫는가
- [ ] `pool_size`와 `max_overflow`를 명시적으로 설정했는가

---

## 처음 질문으로 돌아가기

**`create_engine()`을 호출하면 즉시 연결되나요?**
아닙니다. Engine은 지연 초기화 팩토리입니다. 첫 번째 `connect()` 호출 시 풀이 초기화됩니다.

**`begin()`과 `connect()`의 차이는?**
`begin()`은 블록 종료 시 자동 커밋, 예외 시 자동 롤백을 처리합니다. `connect()`는 수동으로 `commit()`을 호출해야 합니다.

---

## 정리

Engine은 연결 풀을 관리하는 팩토리이고, Connection은 실제 통신 채널입니다. SQLAlchemy 2.x에서는 `conn.execute()`와 명시적 트랜잭션 관리가 기본입니다. 다음 글에서는 MetaData와 Table로 Python 객체로 스키마를 정의하는 방법을 살펴봅니다.

---

## 참고 자료

- [SQLAlchemy 2.0 Engine Configuration](https://docs.sqlalchemy.org/en/20/core/engines.html)
- [SQLAlchemy 2.0 Migration Guide](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html)

---

<!-- toc:begin -->
## 시리즈 목차

1. **바이브코딩을 위한 SQLAlchemy (1/10): Engine과 Connection의 본질 (현재 글)**
2. 바이브코딩을 위한 SQLAlchemy (2/10): MetaData, Table, Column으로 schema를 Python 객체로 만들기
3. 바이브코딩을 위한 SQLAlchemy (3/10): select·insert·update·delete를 2.x style로 다루기
4. 바이브코딩을 위한 SQLAlchemy (4/10): DeclarativeBase와 mapped_column으로 모델 정의하기
5. 바이브코딩을 위한 SQLAlchemy (5/10): Session 깊이 보기: Unit of Work와 Identity Map의 동작 원리
6. 바이브코딩을 위한 SQLAlchemy (6/10): relationship과 back_populates로 양방향 탐색 안전하게 잇기
7. 바이브코딩을 위한 SQLAlchemy (7/10): 로딩 전략과 N+1 문제: lazy/joined/selectin을 언제 골라야 하는가
8. 바이브코딩을 위한 SQLAlchemy (8/10): 이벤트, hybrid_property, 그리고 커스텀 타입
9. 바이브코딩을 위한 SQLAlchemy (9/10): 비동기 SQLAlchemy: aiosqlite와 AsyncSession
10. 바이브코딩을 위한 SQLAlchemy (10/10): 프로덕션 패턴: 풀, 관측, 마이그레이션, 배포
<!-- toc:end -->

Tags: 바이브코딩, SQLAlchemy, Python, Database, Backend
