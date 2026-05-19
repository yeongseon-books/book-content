---
series: testing-101
episode: 3
title: 통합 테스트
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

# 통합 테스트

단위 테스트가 모두 초록색인데 실제 환경에서는 500 오류가 나는 장면은 낯설지 않습니다. 함수 하나씩 떼어 놓고 보면 맞았지만, HTTP 라우팅과 서비스 계층, 저장소, 데이터베이스가 이어지는 순간 계약이 어긋나는 경우가 많기 때문입니다.

실무 버그는 모듈 내부보다 경계에서 자주 나옵니다. 스키마가 달라졌거나, 요청 형식이 달라졌거나, 권한 체크가 예상과 다르게 엮이는 식입니다. 통합 테스트는 바로 그 경계를 보는 테스트입니다.

이 글은 Testing 101 시리즈의 세 번째 글입니다. 여기서는 통합 테스트가 단위 테스트와 어떻게 다른지, 실제 DB와 HTTP 계층을 왜 붙여 보는지, 그리고 느린 테스트를 어떻게 다루는지 정리하겠습니다.

---

## 이 글에서 다룰 문제

- 통합 테스트는 무엇을 함께 검증할까요?
- 실제 DB나 HTTP 계층은 왜 붙여 봐야 할까요?
- 테스트 컨테이너와 픽스처는 어떤 상황에서 유용할까요?
- 느린 테스트를 일상 개발 흐름과 어떻게 분리할까요?
- 통합 테스트에서 가장 자주 생기는 실수는 무엇일까요?

> 통합 테스트는 여러 부품이 연결된 상태를 검증합니다. 각 부품이 따로 맞더라도 연결 지점에서 문제가 생길 수 있다는 가정을 전제로 합니다.

## 왜 중요한가

대부분의 운영 버그는 경계에서 드러납니다. 데이터베이스 스키마가 바뀌었는데 저장 코드가 그대로이거나, API 계약이 달라졌는데 호출부가 예전 형식을 계속 쓰는 경우가 대표적입니다. 이런 문제는 단위 테스트만으로는 잘 드러나지 않습니다.

통합 테스트는 조립 상태를 확인합니다. 단위 테스트가 부품 검수라면, 통합 테스트는 부품을 실제로 끼워 맞춘 뒤 움직여 보는 단계에 가깝습니다. 비용은 더 들지만, 그만큼 실제 사고와 가까운 문제를 잡습니다.

## 한눈에 보는 구조

![한눈에 보는 구조](https://yeongseon-books.github.io/book-public-assets/assets/testing-101/03/03-01-diagram.ko.png)

*한눈에 보는 구조*
이 그림에서 중요한 지점은 테스트 대상이 함수 하나가 아니라 흐름이라는 점입니다. 라우트, 서비스, 저장소, 데이터베이스가 함께 맞물릴 때 어떤 응답이 나오는지 봅니다. 그래서 통합 테스트는 로직 검증과 계약 검증을 동시에 수행합니다.

## 핵심 용어

- **통합 테스트**: 두 개 이상 컴포넌트를 함께 실행해 검증하는 테스트입니다.
- **테스트 컨테이너**: 테스트용 DB나 Redis를 컨테이너로 잠깐 띄우는 방식입니다.
- **테스트 데이터베이스**: 운영 DB와 분리된 전용 데이터베이스입니다.
- **시드 데이터(seed data)**: 테스트가 시작할 때 미리 넣어 두는 데이터입니다.
- **느린 테스트 마커**: 기본 실행에서 제외할 수 있도록 붙이는 태그입니다.

## 바꾸기 전과 후

**바꾸기 전 — 단위 테스트만 있는 상태**

```text
- 함수 단위 테스트 100개 통과
- 실제 배포 뒤 DB 컬럼 누락으로 500 오류 발생
```

**바꾼 뒤 — 통합 테스트를 추가한 상태**

```text
- 단위 테스트 100개
- POST /users 통합 테스트 5개 (실제 DB 사용)
- 스키마 공백을 배포 전에 CI에서 발견
```

단위 테스트가 쓸모없다는 뜻은 아닙니다. 다만 부품 검수만으로 조립 불량을 막을 수 없다는 뜻입니다. 통합 테스트는 상위 계층에서 조립 상태를 한 번 더 확인합니다.

## 다섯 단계로 FastAPI와 SQLite 붙여 보기

### 1단계 — 테스트 대상 코드 준비

```python
# src/app.py
from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()
engine = create_engine("sqlite:///./test.db", future=True)
Session = sessionmaker(bind=engine, future=True)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)

Base.metadata.create_all(engine)
app = FastAPI()

@app.post("/users")
def create_user(email: str):
    with Session() as s:
        u = User(email=email)
        s.add(u); s.commit(); s.refresh(u)
        return {"id": u.id, "email": u.email}
```

### 2단계 — 테스트 클라이언트 준비

```python
# tests/test_users_integration.py
from fastapi.testclient import TestClient
from src.app import app, Base, engine

def setup_function():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

client = TestClient(app)
```

### 3단계 — 정상 경로 검증

```python
def test_create_user_returns_201_and_persists():
    res = client.post("/users", params={"email": "a@b.com"})
    assert res.status_code == 200
    body = res.json()
    assert body["email"] == "a@b.com"
```

### 4단계 — 중복 입력 실패 확인

```python
def test_duplicate_email_fails():
    client.post("/users", params={"email": "a@b.com"})
    res = client.post("/users", params={"email": "a@b.com"})
    assert res.status_code in (400, 409, 500)  # 정책이 무엇이든 실패해야 함
```

### 5단계 — 느린 테스트 분리

```python
import pytest

@pytest.mark.slow
def test_large_batch_insert():
    for i in range(1000):
        client.post("/users", params={"email": f"u{i}@e.com"})
```

```bash
pytest -m "not slow"   # 기본 실행
pytest -m slow         # 야간 실행
```

## 이 코드에서 먼저 볼 점

- 각 테스트 전에 스키마를 다시 만들어 상태를 분리합니다.
- HTTP 호출과 DB 저장이 함께 실행되므로 라우팅과 영속화가 동시에 검증됩니다.
- 느린 테스트를 마커로 분리해 일상 개발 흐름을 지키고 있습니다.

통합 테스트에서 가장 중요한 성질은 상태 분리입니다. 테스트 순서에 따라 통과 여부가 달라지면 신뢰할 수 없습니다. 그래서 통합 테스트는 실제 의존을 붙이더라도 시작 상태를 반복 가능하게 관리해야 합니다.

## 어디서 자주 헷갈릴까요?

첫 번째 실수는 운영 데이터베이스에 테스트를 연결하는 일입니다. 가장 위험한 안티패턴입니다. 테스트는 항상 전용 DB를 써야 합니다.

두 번째 실수는 통합 테스트를 쓴다고 하면서 DB까지 모두 목(mock)으로 대체하는 경우입니다. 그러면 연결 지점에서 생기는 문제를 검증하지 못합니다. 외부 결제망처럼 비용이 큰 의존은 대역으로 바꿀 수 있지만, 검증하려는 경계를 지나치게 지워 버리면 통합 테스트의 의미가 줄어듭니다.

세 번째 실수는 모든 통합 테스트를 매번 돌려 PR 시간을 30분 이상으로 늘리는 경우입니다. 느린 테스트를 구분하고 실행 계층을 나누는 운영 감각이 필요합니다.

## 직접 검증해 볼 것

1. 첫 번째 `POST /users` 호출 뒤에 실제로 `users` 테이블에 한 행이 생겼는지 조회해 봅니다. HTTP 응답만 보고 끝내면 저장 계층 오류를 놓칠 수 있습니다.
2. 같은 이메일을 두 번 보냈을 때 어떤 상태 코드로 실패시킬지 팀 정책을 정하고, 테스트도 그 정책에 맞춰 좁혀 둡니다. `400, 409, 500`처럼 넓은 허용 범위는 경고 신호입니다.
3. `pytest -m "not slow"`와 `pytest -m slow`를 각각 실행해, 빠른 기본 경로와 무거운 검증 경로가 실제로 분리되는지 확인합니다.

**예상 결과:** 정상 경로에서는 사용자 생성과 영속화가 모두 확인되고, 중복 입력은 팀이 정한 단일 실패 정책으로 고정되어야 합니다.

## 실패 신호와 첫 점검

- 테스트가 운영 DB 연결 문자열을 재사용하면 가장 먼저 실행을 멈추고 격리 환경부터 분리해야 합니다.
- 테스트 순서를 바꿨을 때만 실패하면 스키마 재생성이나 시드 데이터 정리가 부족한 경우가 많습니다.
- 실패 상태 코드를 너무 느슨하게 허용하면 회귀가 생겨도 테스트가 초록색으로 남을 수 있습니다.

## 실무에서는 이렇게 생각합니다

대부분의 백엔드 팀은 핵심 시나리오에 대해 실제 DB를 붙인 통합 테스트를 유지합니다. Postgres와 testcontainers 조합이 자주 쓰이고, 외부 API는 VCR이나 목 서버로 대체하는 식으로 경계를 조정합니다.

경험 많은 엔지니어는 통합 테스트를 많이 쓰는 것보다 어디를 붙여 볼지 신중하게 고릅니다. 모든 조합을 다 검증하려고 들면 느리고 비싼 테스트 묶음만 남습니다. 사고가 자주 나는 경계, 계약이 자주 바뀌는 지점, 권한과 상태 전이가 만나는 지점부터 우선순위를 줍니다.

## 체크리스트

- [ ] 실제 DB 또는 실제 HTTP 계층을 포함한 테스트가 있습니다.
- [ ] 각 테스트가 깨끗한 상태에서 시작합니다.
- [ ] 느린 테스트를 마커나 별도 잡으로 분리했습니다.
- [ ] 정상 경로뿐 아니라 실패 경로도 최소 한 개 포함했습니다.

## 연습 문제

1. `GET /users` 라우트를 추가하고 통합 테스트 두 개를 작성해 보세요.
2. 잘못된 입력에 대해 400 응답을 확인하는 테스트를 추가해 보세요.
3. 테스트 실행 순서를 바꿔도 통과하는지 확인해 보세요.

## 정리

통합 테스트는 부품이 아니라 연결 상태를 봅니다. 단위 테스트가 맞더라도 경계에서는 문제가 생길 수 있기 때문에, 실제 의존을 붙여 보는 검증이 필요합니다. 다음 글에서는 사용자 화면까지 포함해 가장 현실에 가까운 신호를 주는 E2E 테스트를 다루겠습니다.

<!-- toc:begin -->
- [테스트란 무엇인가?](./01-what-is-testing.md)
- [단위 테스트](./02-unit-test.md)
- **통합 테스트 (현재 글)**
- E2E 테스트 (예정)
- 테스트 더블 (예정)
- Mock과 Stub (예정)
- 테스트 커버리지 (예정)
- 회귀 테스트 (예정)
- CI에서 테스트 실행하기 (예정)
- 테스트 전략 세우기 (예정)
<!-- toc:end -->

## 참고 자료

### 공식 문서
- [FastAPI testing guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Session basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- [pytest markers](https://docs.pytest.org/en/stable/example/markers.html)

### 실무 참고
- [Testcontainers](https://testcontainers.com/)
- [Martin Fowler — Integration Test](https://martinfowler.com/bliki/IntegrationTest.html)

Tags: Testing, Integration, pytest, Database, HTTP
