---
series: testing-101
episode: 3
title: "Testing 101 (3/10): 통합 테스트"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Testing
  - Integration
  - pytest
  - Database
  - HTTP
seo_description: DB와 HTTP를 포함해 여러 모듈이 함께 동작하는지 검증하는 통합 테스트의 정의와 실습.
last_reviewed: '2026-05-12'
---

# Testing 101 (3/10): 통합 테스트

단위 테스트가 모두 초록색인데 실제 환경에서는 500 오류가 나는 장면은 낯설지 않습니다. 함수 하나씩 떼어 놓고 보면 맞았지만, HTTP 라우팅과 서비스 계층, 저장소, 데이터베이스가 이어지는 순간 계약이 어긋나는 경우가 많기 때문입니다.

실무 버그는 모듈 내부보다 경계에서 자주 나옵니다. 스키마가 달라졌거나, 요청 형식이 달라졌거나, 권한 체크가 예상과 다르게 엮이는 식입니다. 통합 테스트는 바로 그 경계를 보는 테스트입니다.

이 글은 Testing 101 시리즈의 세 번째 글입니다. 여기서는 통합 테스트가 단위 테스트와 어떻게 다른지, 실제 DB와 HTTP 계층을 왜 붙여 보는지, 그리고 느린 테스트를 어떻게 다루는지 정리하겠습니다.

![Testing 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/testing-101/03/03-01-diagram.ko.png)
*Testing 101 3장 흐름 개요*
> 통합 테스트는 부품 조립 상태의 계약 위반을 감시합니다.

## 이 글에서 다룰 문제

- 통합 테스트는 무엇을 함께 검증할까요?
- 실제 DB나 HTTP 계층은 왜 붙여 봐야 할까요?
- 테스트 컨테이너와 픽스처는 어떤 상황에서 유용할까요?
- 인메모리 DB와 실제 DB는 언제 각각 선택해야 할까요?
- 통합 테스트 상태 격리는 어떻게 구현할까요?

대부분의 운영 버그는 경계에서 드러납니다. 데이터베이스 스키마가 바뀌었는데 저장 코드가 그대로이거나, API 계약이 달라졌는데 호출부가 예전 형식을 계속 쓰는 경우가 대표적입니다. 이런 문제는 단위 테스트만으로는 잘 드러나지 않습니다.

통합 테스트는 조립 상태를 확인합니다. 단위 테스트가 부품 검수라면, 통합 테스트는 부품을 실제로 끼워 맞춘 뒤 움직여 보는 단계에 가깝습니다. 비용은 더 들지만, 그만큼 실제 사고와 가까운 문제를 잡습니다.

## 한눈에 보는 구조

라우트, 서비스, 저장소, 데이터베이스가 함께 맞물릴 때 어떤 응답이 나오는지 봅니다. 그래서 통합 테스트는 로직 검증과 계약 검증을 동시에 수행합니다.

| 용어 | 의미 |
|------|------|
| 통합 테스트 | 두 개 이상 컴포넌트를 함께 실행해 검증하는 테스트 |
| 테스트 컨테이너 | 테스트용 DB나 Redis를 컨테이너로 잠깐 띄우는 방식 |
| 테스트 데이터베이스 | 운영 DB와 분리된 전용 데이터베이스 |
| 시드 데이터 | 테스트가 시작할 때 미리 넣어 두는 데이터 |
| 느린 테스트 마커 | 기본 실행에서 제외할 수 있도록 붙이는 태그 |

## 단위 테스트만 있는 상태 vs 통합 테스트를 추가한 상태

**단위 테스트만 있는 상태**

```text
- 함수 단위 테스트 100개 통과
- 실제 배포 뒤 DB 컬럼 누락으로 500 오류 발생
- 원인: 마이그레이션에 신규 컬럼 반영 누락
```

**통합 테스트를 추가한 상태**

```text
- 단위 테스트 100개
- POST /users 통합 테스트 5개 (실제 DB 사용)
- 스키마 공백을 배포 전에 CI에서 발견
- 컬럼 누락으로 인한 인서트 실패 → CI가 차단
```

단위 테스트가 쓸모없다는 뜻이 아닙니다. 부품 검수만으로 조립 불량을 막을 수 없다는 뜻입니다. 통합 테스트는 상위 계층에서 조립 상태를 한 번 더 확인합니다.

## 인메모리 DB와 실제 DB 선택 기준

| 기준 | 인메모리 DB (SQLite) | 실제 DB (Postgres, MySQL) |
|---|---|---|
| 실행 속도 | 빠름 (수백 ms) | 느림 (수초) |
| 설정 복잡도 | 낮음 | 높음 (Docker 또는 별도 서버) |
| 운영 환경과의 일치 | 낮음 (SQL 방언 차이 존재) | 높음 |
| 트랜잭션 격리 | 제한적 | 완전 지원 |
| JSON 컬럼, Full-text 검색 | 제한적 | 전체 지원 |
| CI 속도 | 빠름 | 느림 |

대부분의 팀은 개발 중에는 SQLite로 빠르게 돌리고, CI에서는 실제 DB를 띄워 운영 환경과의 차이를 검증합니다. 둘 중 하나만 고르지 말고 상황에 따라 바꿀 수 있게 만드는 편이 좋습니다.

## FastAPI TestClient로 HTTP 계층 검증하기

FastAPI의 `TestClient`는 내부에서 `httpx`를 씁니다. 실제 HTTP 요청을 만들지 않고도 ASGI 인터페이스를 직접 호출하므로, 네트워크 오버헤드 없이 라우팅과 미들웨어까지 검증할 수 있습니다.

```python
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_create_user_returns_id_and_email():
    res = client.post(
        "/users",
        json={"email": "a@b.com", "name": "Alice"},
    )
    assert res.status_code == 201
    body = res.json()
    assert "id" in body
    assert body["email"] == "a@b.com"

def test_create_user_with_auth_header():
    res = client.post(
        "/users",
        json={"email": "admin@b.com"},
        headers={"Authorization": "Bearer test-token"}
    )
    assert res.status_code == 201
```

이 방식은 단위 테스트보다는 느리지만, 실제 서버를 띄우는 것보다는 빠릅니다. 인증 헤더, 쿠키, 쿼리 파라미터까지 모두 검증할 수 있어 API 계약 테스트로 쓰기에 적합합니다.

## 테스트 격리 — 트랜잭션 롤백 패턴

각 테스트가 깨끗한 상태에서 시작하려면 스키마를 매번 재생성하거나, 트랜잭션을 열고 끝에서 롤백하는 방법을 씁니다.

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.app import Base

engine = create_engine("sqlite:///./test.db", future=True)
Session = sessionmaker(bind=engine, future=True)

@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    # 정리는 다음 테스트의 drop_all이 처리
```

더 빠른 방법은 트랜잭션 안에서 테스트를 실행하고 끝에 롤백하는 것입니다.

```python
@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()
```

롤백 패턴은 중첩 트랜잭션이나 `COMMIT`을 호출하는 코드와 충돌할 수 있으므로, 팀 상황에 맞게 고르는 것이 좋습니다.

## 다섯 단계로 FastAPI와 SQLite 통합 테스트 만들기

### 1단계 — 테스트 대상 코드 준비

```python
# src/app.py
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import IntegrityError

Base = declarative_base()
engine = create_engine("sqlite:///./test.db", future=True)
Session = sessionmaker(bind=engine, future=True)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False, default="")

Base.metadata.create_all(engine)
app = FastAPI()

@app.post("/users", status_code=201)
def create_user(email: str, name: str = ""):
    with Session() as s:
        try:
            u = User(email=email, name=name)
            s.add(u)
            s.commit()
            s.refresh(u)
            return {"id": u.id, "email": u.email}
        except IntegrityError:
            raise HTTPException(status_code=409, detail="Email already exists")
```

### 2단계 — 테스트 클라이언트 준비

```python
# tests/integration/test_users.py
import pytest
from fastapi.testclient import TestClient
from src.app import app, Base, engine

@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

client = TestClient(app)
```

### 3단계 — 정상 경로 검증

```python
def test_create_user_returns_201_and_persists():
    res = client.post("/users", params={"email": "a@b.com", "name": "Alice"})
    assert res.status_code == 201
    body = res.json()
    assert body["email"] == "a@b.com"
    assert "id" in body
```

### 4단계 — 중복 입력 실패 확인

```python
def test_duplicate_email_returns_409():
    client.post("/users", params={"email": "a@b.com"})
    res = client.post("/users", params={"email": "a@b.com"})
    assert res.status_code == 409
    assert "already exists" in res.json()["detail"]
```

### 5단계 — 느린 테스트 분리

```python
@pytest.mark.slow
def test_large_batch_insert():
    for i in range(500):
        res = client.post("/users", params={"email": f"u{i}@example.com"})
        assert res.status_code == 201
```

```bash
pytest -m "not slow"   # 기본 실행
pytest -m slow         # 야간 실행
```

## 테스트 컨테이너로 실제 Postgres 띄우기

인메모리 DB로 충분하지 않을 때는 Docker 컨테이너로 실제 DB를 잠깐 띄울 수 있습니다. `testcontainers-python`을 쓰면 테스트 시작 시 Postgres를 자동으로 올리고, 끝나면 내립니다.

```python
import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine, text

@pytest.fixture(scope="session")
def postgres_url():
    with PostgresContainer("postgres:15") as pg:
        yield pg.get_connection_url()

@pytest.fixture
def pg_engine(postgres_url):
    engine = create_engine(postgres_url)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()

def test_user_creation_with_real_postgres(pg_engine):
    with pg_engine.connect() as conn:
        conn.execute(text("INSERT INTO users (email) VALUES ('pg@test.com')"))
        conn.commit()
        result = conn.execute(text("SELECT email FROM users WHERE email='pg@test.com'"))
        assert result.fetchone()[0] == "pg@test.com"
```

이 방식은 로컬과 CI에서 모두 같은 환경을 만들 수 있어 운영 DB와의 차이를 미리 잡습니다. 다만 컨테이너 시작 시간이 수 초 걸리므로, 자주 돌리는 테스트보다는 CI 전용 검증에 더 적합합니다.

## 이 코드에서 먼저 볼 점

- 각 테스트 전에 스키마를 다시 만들어 상태를 분리합니다.
- HTTP 호출과 DB 저장이 함께 실행되므로 라우팅과 영속화가 동시에 검증됩니다.
- 느린 테스트를 마커로 분리해 일상 개발 흐름을 지키고 있습니다.
- 중복 입력 실패는 구체적인 상태 코드(409)로 고정합니다.

통합 테스트에서 가장 중요한 성질은 상태 분리입니다. 테스트 순서에 따라 통과 여부가 달라지면 신뢰할 수 없습니다.

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
|------|------|------------|
| 운영 DB에 테스트 연결 | 실제 데이터 오염, 운영 환경에 영향 | 전용 테스트 DB 또는 인메모리 DB 사용 |
| 모든 의존을 mock으로 대체 | 경계 문제를 검증하지 못함 | 검증하려는 경계는 실제 의존 포함 |
| 테스트 간 상태 누적 | 순서를 바꾸면 실패 | `autouse` fixture로 상태 초기화 |
| 모든 통합 테스트를 PR마다 실행 | CI 30분 이상으로 병목 | 마커로 계층 분리, 느린 것은 야간 잡 |
| 실패 상태 코드를 넓게 허용 | 회귀가 생겨도 초록색 유지 | 단일 실패 정책으로 좁게 고정 |
| 시드 데이터 없이 빈 DB에서 조회 | 조회 결과가 빈 것과 오류를 구분 못함 | 필요한 시드 데이터를 fixture에서 명시적으로 삽입 |

## 직접 검증해 볼 것

1. 첫 번째 `POST /users` 호출 뒤에 실제로 `users` 테이블에 한 행이 생겼는지 조회해 봅니다. HTTP 응답만 보고 끝내면 저장 계층 오류를 놓칠 수 있습니다.
2. 같은 이메일을 두 번 보냈을 때 정확히 409가 반환되는지 확인합니다. `400, 409, 500`처럼 넓은 허용 범위는 경고 신호입니다.
3. `pytest -m "not slow"`와 `pytest -m slow`를 각각 실행해, 빠른 기본 경로와 무거운 검증 경로가 실제로 분리되는지 확인합니다.

**예상 결과:** 정상 경로에서는 사용자 생성과 영속화가 모두 확인되고, 중복 입력은 팀이 정한 단일 실패 정책으로 고정되어야 합니다.

## CI에서 통합 테스트 실행하기

통합 테스트는 DB 서비스가 필요하므로 CI 구성이 단위 테스트보다 복잡합니다.

```yaml
name: integration-test
on:
  pull_request:

jobs:
  integration:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: testdb
          POSTGRES_USER: testuser
          POSTGRES_PASSWORD: testpass
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'
      - run: pip install -r requirements-dev.txt
      - name: Run integration tests
        env:
          DATABASE_URL: postgresql://testuser:testpass@localhost:5432/testdb
        run: pytest tests/integration -q -m "not slow"
```

`services` 블록은 잡이 시작할 때 자동으로 Postgres 컨테이너를 띄우고, 잡이 끝나면 내립니다.

## 운영 관점에서 생각하기

대부분의 백엔드 팀은 핵심 시나리오에 대해 실제 DB를 붙인 통합 테스트를 유지합니다. Postgres와 testcontainers 조합이 자주 쓰이고, 외부 API는 VCR이나 목 서버로 대체하는 식으로 경계를 조정합니다.

경험 많은 엔지니어는 통합 테스트를 많이 쓰는 것보다 어디를 붙여 볼지 신중하게 고릅니다. 모든 조합을 다 검증하려고 들면 느리고 비싼 테스트 묶음만 남습니다. 사고가 자주 나는 경계, 계약이 자주 바뀌는 지점, 권한과 상태 전이가 만나는 지점부터 우선순위를 줍니다.

테스트 실패 메시지에는 입력값, 기대값, 실제값이 함께 남아야 하며, 그래야 CI 로그만으로도 원인을 좁힐 수 있습니다. 실패한 요청의 응답 본문을 출력하는 것이 디버깅 시간을 크게 줄입니다.

## 운영 체크리스트

- [ ] 실제 DB 또는 실제 HTTP 계층을 포함한 테스트가 있습니다.
- [ ] 각 테스트가 깨끗한 상태에서 시작합니다.
- [ ] 느린 테스트를 마커나 별도 잡으로 분리했습니다.
- [ ] 정상 경로뿐 아니라 실패 경로도 최소 한 개 포함했습니다.
- [ ] CI에서 테스트 전용 DB를 사용합니다.

## 연습 문제

1. `GET /users/{id}` 라우트를 추가하고 존재하는 ID와 없는 ID에 대한 통합 테스트를 각각 작성해 보세요.
2. 잘못된 입력(이메일 형식 오류)에 대해 422 응답을 확인하는 테스트를 추가해 보세요.
3. 테스트 실행 순서를 바꿔도 통과하는지 확인해 보세요.
4. `@pytest.mark.slow`를 붙인 테스트를 만들고 `-m "not slow"` 실행에서 제외되는지 확인하세요.

## 정리

통합 테스트는 부품이 아니라 연결 상태를 봅니다. 단위 테스트가 맞더라도 경계에서는 문제가 생길 수 있기 때문에, 실제 의존을 붙여 보는 검증이 필요합니다. 다음 글에서는 사용자 화면까지 포함해 가장 현실에 가까운 신호를 주는 E2E 테스트를 다루겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Testing 101 (1/10): 테스트란 무엇인가?](./01-what-is-testing.md)
- [Testing 101 (2/10): 단위 테스트](./02-unit-test.md)
- **Testing 101 (3/10): 통합 테스트 (현재 글)**
- [Testing 101 (4/10): E2E 테스트](./04-e2e-test.md)
- [Testing 101 (5/10): 테스트 더블](./05-test-double.md)
- [Testing 101 (6/10): Mock과 Stub](./06-mock-and-stub.md)
- [Testing 101 (7/10): 테스트 커버리지](./07-test-coverage.md)
- [Testing 101 (8/10): 회귀 테스트](./08-regression-test.md)
- [Testing 101 (9/10): CI에서 테스트 실행하기](./09-tests-in-ci.md)
- [테스트 전략 세우기](./10-test-strategy.md)

<!-- toc:end -->

## 참고 자료

- 실습 예제 저장소(book-examples): https://github.com/yeongseon-books/book-examples/tree/main/testing-101/ko
### 공식 문서
- [FastAPI testing guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Session basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- [pytest markers](https://docs.pytest.org/en/stable/example/markers.html)

### 실무 참고
- [Testcontainers](https://testcontainers.com/)
- [Martin Fowler — Integration Test](https://martinfowler.com/bliki/IntegrationTest.html)

Tags: Testing, Integration, pytest, Database, HTTP
