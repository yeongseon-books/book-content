---
series: backend-development-101
episode: 8
title: 백엔드 테스트
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Backend
  - Testing
  - Pytest
  - Python
  - QualityAssurance
seo_description: pytest와 TestClient로 안전한 백엔드 변경 환경을 만드는 방법입니다
last_reviewed: '2026-05-12'
---

# 백엔드 테스트

이 글은 Backend Development 101 시리즈의 여덟 번째 글입니다. 테스트 없이 코드를 바꾸는 일은 매번 도박에 가깝습니다. 여기서는 unit, integration, E2E 테스트를 어떻게 나눠 생각해야 하는지, 그리고 pytest와 FastAPI TestClient로 변경에 안전한 백엔드를 만드는 방법을 살펴보겠습니다.

## 이 글에서 다룰 문제

- unit, integration, E2E 테스트는 각각 무엇을 검증할까요?
- pytest로 service를 어떻게 테스트할 수 있을까요?
- FastAPI `TestClient`는 endpoint를 어떻게 검증하게 해 줄까요?
- 실제 데이터베이스를 띄우지 않고도 어떤 부분까지 테스트할 수 있을까요?
- fixture와 mock은 언제 쓰고 언제 과하게 쓰게 될까요?

## 왜 중요한가

테스트가 없는 코드는 읽을 수는 있어도 안전하게 바꾸기 어렵습니다. 좋은 백엔드의 핵심은 처음부터 완벽하게 짜는 것이 아니라, 나중에 바꿔도 무너지지 않게 만드는 데 있습니다. 그 안전망이 자동화된 테스트입니다.

테스트는 평소에는 눈에 잘 띄지 않지만, 장애가 났을 때와 기능을 빠르게 추가해야 할 때 가장 큰 차이를 만듭니다. 새 기능마다 손으로 브라우저를 클릭해 확인하는 팀은 결국 변경 속도가 급격히 떨어집니다.

> 테스트는 코드를 읽기 좋게 만드는 장치가 아니라, 바꾸기 안전하게 만드는 안전망입니다.

## 한눈에 보는 개념

```mermaid
flowchart LR
    Unit["Unit"] --> Int["Integration"]
    Int --> E2E["E2E"]
    Unit -->|"fast and many"| Pyramid
    E2E -->|"slow and few"| Pyramid
```

테스트 피라미드의 핵심은 아래쪽에 빠르고 많은 테스트를 두고, 위쪽에 느리고 적은 테스트를 두는 것입니다. 이 비율이 깨지면 팀의 개발 속도도 함께 무너집니다.

## 핵심 용어

- **Unit test**: 함수나 클래스 하나 같은 작은 단위를 검증합니다.
- **Integration test**: 여러 모듈이 함께 제대로 동작하는지 검증합니다.
- **E2E test**: 실제 사용자처럼 전체 시스템을 끝까지 검증합니다.
- **Fixture**: 반복되는 준비 코드를 재사용 가능하게 만든 장치입니다.
- **Mock**: 외부 의존성을 대신하는 가짜 객체입니다.

## Before/After

**Before (manual checks)**

```python
# Click around in the browser every time
```

**After (automatic verification)**

```python
def test_create_user(client):
    r = client.post("/users", json={"name": "Alice"})
    assert r.status_code == 200
    assert r.json()["name"] == "Alice"
```

자동 검증이 생기면 배포 전마다 같은 시나리오를 다시 눌러 볼 필요가 줄어듭니다. 결국 테스트의 목적은 코드를 읽기 좋게 만드는 것이 아니라, 바꾸기 안전하게 만드는 것입니다.

## 실습: 다섯 단계로 보는 테스트

### Step 1 — First pytest test

```python
# tests/test_basic.py
def add(a, b): return a + b

def test_add():
    assert add(2, 3) == 5
```

```bash
pytest -q
```

가장 작은 테스트부터 시작하면 자동 검증의 감각을 빠르게 익힐 수 있습니다. 핵심은 “호출했다”가 아니라 “기대값을 assert했다”입니다.

### Step 2 — Unit test a service with mocks

```python
# tests/test_user_service.py
from unittest.mock import MagicMock
from services.user_service import UserService

def test_register():
    repo = MagicMock()
    repo.insert.return_value = {"id": 1, "name": "A"}
    svc = UserService(repo)
    result = svc.register("A")
    repo.insert.assert_called_once()
    assert result["id"] == 1
```

unit test에서는 외부 의존성을 잘라내고 service의 판단만 검증합니다. mock은 그 경계를 빠르게 세워 주는 도구입니다.

### Step 3 — FastAPI TestClient

```python
# tests/test_api.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    assert client.get("/health").status_code == 200
```

TestClient를 쓰면 실제 서버 프로세스를 띄우지 않고도 endpoint를 호출할 수 있습니다. 라우팅과 응답 형식 검증에 매우 유용합니다.

### Step 4 — Fixture for in-memory DB

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from db import Base

@pytest.fixture
def engine():
    e = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(e)
    return e
```

fixture를 쓰면 반복되는 설정 코드를 한곳에 모을 수 있습니다. 테스트가 많아질수록 이 재사용성이 큰 차이를 만듭니다.

### Step 5 — Dependency override

```python
# tests/test_with_db.py
def test_create_user(client, engine):
    app.dependency_overrides[get_engine] = lambda: engine
    r = client.post("/users", json={"name": "Bob"})
    assert r.status_code == 200
```

FastAPI의 `dependency_overrides`를 쓰면 실제 운영용 데이터베이스 없이도 꽤 많은 경로를 검증할 수 있습니다. 빠른 테스트를 만드는 핵심 포인트 중 하나입니다.

## 이 코드에서 먼저 볼 점

- unit test는 mock으로 외부 의존성을 끊습니다.
- integration test는 실제 session 같은 연결을 확인합니다.
- fixture는 같은 설정을 반복해서 쓰지 않게 해 줍니다.

이 구조가 중요한 이유는, 모든 테스트를 E2E로만 하려 들면 너무 느려져서 결국 아무도 자주 실행하지 않게 되기 때문입니다. 빠른 하단 테스트가 많아야 개발 속도도 유지됩니다.

## 자주 하는 실수 5가지

1. **E2E만 작성하는 실수**입니다. 너무 느려서 결국 자주 돌리지 않게 됩니다.
2. **테스트 안에서 `time.sleep`으로 기다리는 실수**입니다. flaky test의 지름길입니다.
3. **테스트끼리 데이터베이스 상태를 공유하는 실수**입니다. 테스트 간 간섭이 생깁니다.
4. **너무 많이 mock하는 실수**입니다. 실제 동작을 검증하지 못하게 됩니다.
5. **호출만 하고 assert를 하지 않는 실수**입니다. 실행은 테스트가 아닙니다.

## 운영에서는 이렇게 드러납니다

CI에서는 보통 모든 PR마다 `pytest`가 실행됩니다. unit test는 수 초, integration test는 수십 초, E2E는 수 분 정도로 분포하는 것이 자연스럽습니다. 이 피라미드 형태가 무너지면 개발 속도도 함께 무거워집니다.

시니어 엔지니어는 커버리지 숫자만 보지 않고 위험한 지점이 제대로 보호되고 있는지를 봅니다. 결제, 인증, 데이터 변경처럼 실패 비용이 큰 부분에는 더 촘촘한 테스트가 필요합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 새 기능은 테스트와 함께 배포되어야 합니다.
- 버그는 고치기 전에 테스트로 먼저 재현합니다.
- 테스트 이름은 문장처럼 읽혀야 합니다.
- mock은 내부가 아니라 외부 경계에서 사용합니다.
- 커버리지 숫자보다 위험 구간 보호가 더 중요합니다.

## 체크리스트

- [ ] 첫 pytest 테스트를 실행할 수 있습니다.
- [ ] mock으로 service unit test를 작성할 수 있습니다.
- [ ] TestClient로 endpoint를 호출할 수 있습니다.
- [ ] 인메모리 DB fixture를 만들 수 있습니다.
- [ ] `dependency_overrides`를 사용할 수 있습니다.

## 연습 문제

1. mock repository를 사용해 `OrderService.create` unit test를 작성해 보세요.
2. 잘못된 비밀번호로 `POST /login`을 호출했을 때 `401`이 나는지 검증해 보세요.
3. 같은 endpoint에 대해 인메모리 DB 기반 integration test를 추가해 보세요.

## 정리와 다음 글

테스트는 변경을 위한 안전망입니다. 다음 글에서는 작성한 코드를 실제 사용자에게 전달하는 과정, 즉 백엔드 배포를 살펴보겠습니다.

<!-- toc:begin -->
- [백엔드 개발이란 무엇인가?](./01-what-is-backend-development.md)
- [HTTP 서버 만들기](./02-building-an-http-server.md)
- [Routing과 Controller](./03-routing-and-controllers.md)
- [Service Layer](./04-service-layer.md)
- [Database Layer](./05-database-layer.md)
- [인증과 권한](./06-auth-and-authorization.md)
- [Logging과 Error Handling](./07-logging-and-error-handling.md)
- **백엔드 테스트 (현재 글)**
- 백엔드 배포 (예정)
- 운영 가능한 백엔드 구조 (예정)
<!-- toc:end -->

## 참고 자료

- [pytest documentation](https://docs.pytest.org/en/stable/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Testing pyramid (Martin Fowler)](https://martinfowler.com/articles/practical-test-pyramid.html)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

Tags: Backend, Testing, Pytest, Python, QualityAssurance
