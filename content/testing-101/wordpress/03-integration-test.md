---
series: testing-101
episode: 3
title: "바이브코딩을 위한 테스팅 기초 (3/10): 통합 테스트"
status: content-ready
targets:
  wordpress: true
  tistory: false
  medium: false
  hashnode: false
  mkdocs: false
  ebook: false
language: ko
tags:
  - 바이브코딩
  - Testing
  - Integration
  - pytest
  - Database
  - HTTP
seo_description: AI가 만든 코드가 DB와 HTTP까지 연결됐을 때 제대로 동작하는지 확인하는 통합 테스트. 단위 테스트가 모두 통과해도 배포 후 터지는 이유와 해결 방법.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 테스팅 기초 (3/10): 통합 테스트

이 글은 **바이브코딩을 위한 테스팅 기초** 시리즈의 세 번째 글입니다. AI가 만든 코드가 데이터베이스, HTTP, 외부 서비스와 연결됐을 때 무엇이 깨지는지 확인하는 통합 테스트를 설명합니다.

---

AI가 만든 단위 테스트가 모두 초록색인데 실제 배포 후 500 오류가 나는 장면은 낯설지 않습니다. 함수 하나씩 보면 맞았지만, HTTP 라우팅, 서비스 계층, 저장소, 데이터베이스가 이어지는 순간 계약이 어긋나기 때문입니다.

AI는 함수의 로직은 잘 만들지만 시스템 간 경계에서 생기는 문제는 자주 놓칩니다. 스키마 불일치, API 계약 변경, 권한 체크 누락 같은 문제는 단위 테스트만으로는 드러나지 않습니다. 통합 테스트는 바로 그 경계를 검증합니다.

> 통합 테스트는 AI가 만든 부품들이 실제로 연결됐을 때 계약 위반을 감시합니다.

## 이 글에서 다룰 문제

- 통합 테스트는 무엇을 함께 검증할까요?
- AI가 만든 코드에서 DB나 HTTP 계층은 왜 직접 붙여 봐야 할까요?
- 테스트 컨테이너와 픽스처는 어떤 상황에서 유용할까요?
- 바이브코딩 환경에서 통합 테스트를 과도하게 만들면 어떤 문제가 생길까요?
- 운영 DB에 테스트를 연결하는 실수를 어떻게 막을까요?

AI 코드의 버그 중 상당수는 함수 내부가 아니라 경계에서 드러납니다. AI는 "사용자를 DB에 저장한다"는 로직은 맞게 만들지만, 실제 DB 스키마와 맞지 않거나 트랜잭션 처리를 빠뜨리는 경우가 있습니다. 통합 테스트는 AI 코드가 실제 시스템 위에서 동작하는지 확인합니다.

## 한눈에 보는 구조

통합 테스트의 대상은 함수 하나가 아니라 흐름입니다. 라우트, 서비스, 저장소, 데이터베이스가 함께 맞물릴 때 어떤 응답이 나오는지 봅니다.

- **통합 테스트**: 두 개 이상 컴포넌트를 함께 실행해 검증하는 테스트입니다.
- **테스트 컨테이너**: 테스트용 DB를 컨테이너로 잠깐 띄우는 방식입니다.
- **테스트 데이터베이스**: 운영 DB와 분리된 전용 데이터베이스입니다.
- **시드 데이터(seed data)**: 테스트가 시작할 때 미리 넣어 두는 데이터입니다.
- **느린 테스트 마커**: 기본 실행에서 제외할 수 있도록 붙이는 태그입니다.

## 인메모리 DB vs 실제 DB

| 기준 | 인메모리 DB (SQLite) | 실제 DB (Postgres, MySQL) |
|---|---|---|
| 실행 속도 | 빠름 | 느림 |
| 운영 환경과의 일치 | 낮음 (SQL 방언 차이) | 높음 |
| AI 코드 검증 신뢰도 | 중간 | 높음 |
| 설정 복잡도 | 낮음 | 높음 |

AI가 만든 코드에서 실제 DB와의 차이 때문에 발생하는 버그가 적지 않습니다. 가능하면 실제 DB와 가까운 환경에서 검증하는 편이 안전합니다.

## 바꾸기 전과 후

**바꾸기 전 — AI가 만든 코드, 단위 테스트만 있는 상태**

```text
- 함수 단위 테스트 100개 통과
- AI가 만든 저장 코드에 DB 컬럼 누락
- 실제 배포 뒤 500 오류 발생
```

**바꾼 뒤 — 통합 테스트로 경계 검증**

```text
- 단위 테스트 100개
- POST /users 통합 테스트 5개 (실제 DB 사용)
- AI 코드의 스키마 공백을 배포 전에 CI에서 발견
```

## 다섯 단계로 FastAPI + SQLite 통합 테스트

### 1단계 — AI가 만든 테스트 대상 코드

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
def test_create_user_returns_200_and_persists():
    res = client.post("/users", params={"email": "a@b.com"})
    assert res.status_code == 200
    body = res.json()
    assert body["email"] == "a@b.com"
    assert "id" in body  # AI가 id 반환을 빠뜨리는 케이스 검증
```

### 4단계 — AI가 놓치기 쉬운 중복 입력 처리

```python
def test_duplicate_email_fails():
    client.post("/users", params={"email": "dup@b.com"})
    res = client.post("/users", params={"email": "dup@b.com"})
    assert res.status_code in (400, 409, 500)  # 실패해야 함
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

## AI 코드의 통합 테스트 함정

AI가 만든 코드에서 통합 테스트 없이 자주 터지는 패턴입니다.

```python
# AI가 만든 코드 (단위 테스트는 통과)
def save_user(email: str, session):
    user = User(email=email)
    session.add(user)
    session.commit()  # 실제 DB에서는 unique constraint 위반 예외 발생 가능
    return user

# 통합 테스트로 잡는 케이스
def test_save_user_raises_on_duplicate(db_session):
    save_user("a@b.com", db_session)
    with pytest.raises(Exception):  # 실제 DB 동작 확인
        save_user("a@b.com", db_session)
```

## 자주 하는 실수

첫 번째 실수는 운영 데이터베이스에 테스트를 연결하는 일입니다. 가장 위험한 안티패턴입니다. 테스트는 항상 전용 DB를 써야 합니다.

두 번째 실수는 통합 테스트를 쓴다고 하면서 DB까지 모두 mock으로 대체하는 경우입니다. 그러면 연결 지점의 문제를 검증하지 못합니다.

세 번째 실수는 모든 통합 테스트를 매번 돌려 PR 시간을 30분 이상으로 늘리는 경우입니다. 느린 테스트를 구분하고 실행 계층을 나누는 것이 중요합니다.

## AI 팁: 통합 테스트 프롬프트

```text
프롬프트 예시:
"POST /users 엔드포인트의 FastAPI 통합 테스트를 작성해 줘.
TestClient를 사용하고, 각 테스트 전에 SQLite DB를 초기화해 줘.
정상 케이스와 중복 이메일 실패 케이스를 포함해 줘."

확인 포인트:
1. 운영 DB가 아닌 테스트 전용 DB를 사용하는지
2. 각 테스트가 독립적인 상태에서 시작하는지
3. HTTP 응답 코드와 바디를 모두 검증하는지
```

## 운영 체크리스트

- [ ] 실제 DB 또는 실제 HTTP 계층을 포함한 테스트가 있습니다.
- [ ] 각 테스트가 깨끗한 상태에서 시작합니다.
- [ ] 운영 DB가 아닌 테스트 전용 DB를 사용합니다.
- [ ] 느린 테스트를 마커나 별도 잡으로 분리했습니다.

## 처음 질문으로 돌아가기

- **통합 테스트는 무엇을 함께 검증할까요?**
  두 개 이상의 컴포넌트가 연결됐을 때 계약이 유지되는지 검증합니다. AI가 만든 HTTP 라우팅과 DB 저장이 실제로 연결되는지 확인합니다.

- **AI가 만든 코드에서 DB나 HTTP 계층은 왜 직접 붙여 봐야 할까요?**
  AI는 함수 로직은 잘 만들지만 스키마 불일치, 트랜잭션 누락, 에러 응답 형식 오류 같은 경계 문제를 자주 놓칩니다. 실제 의존을 붙여야 이 문제가 보입니다.

- **운영 DB에 테스트를 연결하는 실수를 어떻게 막을까요?**
  환경 변수나 설정으로 테스트 DB URL을 분리하고, CI에서 테스트 전용 DB 컨테이너를 사용합니다.

## 정리

통합 테스트는 AI가 만든 부품들이 실제 시스템에서 올바르게 연결되는지 확인합니다. 단위 테스트가 맞더라도 경계에서는 문제가 생길 수 있기 때문에 실제 의존을 붙여 보는 검증이 필요합니다. 다음 글에서는 사용자 화면까지 포함한 E2E 테스트를 다루겠습니다.

## 참고 자료

- 실습 예제 저장소: https://github.com/yeongseon-books/book-examples/tree/main/testing-101/ko
- [FastAPI testing guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [Testcontainers](https://testcontainers.com/)
- [Martin Fowler — Integration Test](https://martinfowler.com/bliki/IntegrationTest.html)

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 테스팅 기초 (1/10): 테스트란 무엇인가?](./01-what-is-testing.md)
- [바이브코딩을 위한 테스팅 기초 (2/10): 단위 테스트](./02-unit-test.md)
- **바이브코딩을 위한 테스팅 기초 (3/10): 통합 테스트 (현재 글)**
- [바이브코딩을 위한 테스팅 기초 (4/10): E2E 테스트](./04-e2e-test.md)
- [바이브코딩을 위한 테스팅 기초 (5/10): 테스트 더블](./05-test-double.md)
- [바이브코딩을 위한 테스팅 기초 (6/10): Mock과 Stub](./06-mock-and-stub.md)
- [바이브코딩을 위한 테스팅 기초 (7/10): 테스트 커버리지](./07-test-coverage.md)
- [바이브코딩을 위한 테스팅 기초 (8/10): 회귀 테스트](./08-regression-test.md)
- [바이브코딩을 위한 테스팅 기초 (9/10): CI에서 테스트 실행하기](./09-tests-in-ci.md)
- [바이브코딩을 위한 테스팅 기초 (10/10): 테스트 전략 세우기](./10-test-strategy.md)

<!-- toc:end -->

Tags: 바이브코딩, Testing, Integration, pytest, Database, HTTP
