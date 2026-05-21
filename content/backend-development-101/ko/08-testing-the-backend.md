---
series: backend-development-101
episode: 8
title: "Backend Development 101 (8/10): 백엔드 테스트"
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
last_reviewed: '2026-05-15'
---

# Backend Development 101 (8/10): 백엔드 테스트

테스트 없이 코드를 바꾸는 일은 매번 도박에 가깝습니다. 기능이 늘수록 중요한 것은 코드를 한 번에 완벽하게 쓰는 능력이 아니라, 나중에 바꿔도 무너지지 않게 만드는 안전망입니다.

이 글은 Backend Development 101 시리즈의 여덟 번째 글입니다. 여기서는 unit·integration·E2E 테스트를 어떻게 나눠 생각해야 하는지, 그리고 pytest와 FastAPI TestClient로 변경에 안전한 백엔드를 만드는 방법을 살펴보겠습니다.

## 먼저 던지는 질문

- unit, integration, E2E 테스트는 각각 무엇을 검증할까요?
- pytest로 service를 어떻게 테스트할 수 있을까요?
- FastAPI `TestClient`는 endpoint를 어떻게 검증하게 해 줄까요?

## 큰 그림

![Backend Development 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/backend-development-101/08/08-01-concept-at-a-glance.ko.png)

*Backend Development 101 8장 흐름 개요*

## 왜 중요한가

테스트가 없는 코드는 읽을 수는 있어도 안전하게 바꾸기 어렵습니다. 좋은 백엔드의 핵심은 처음부터 완벽하게 짜는 것이 아니라, 나중에 바꿔도 무너지지 않게 만드는 데 있습니다. 그 안전망이 자동화된 테스트입니다.

테스트는 평소에는 눈에 잘 띄지 않지만, 장애가 났을 때와 기능을 빠르게 추가해야 할 때 가장 큰 차이를 만듭니다. 새 기능마다 손으로 브라우저를 클릭해 확인하는 팀은 결국 변경 속도가 급격히 떨어집니다.

> 테스트는 코드를 읽기 좋게 만드는 장치가 아니라, 바꾸기 안전하게 만드는 안전망입니다.

## 한눈에 보는 개념

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

## 검증 포인트

**Expected output:** `pytest -q`는 기본 unit test를 통과해야 하고, `TestClient`로 호출한 `/health`는 `200`, 잘못된 로그인은 `401`을 돌려줘야 합니다.

### 먼저 확인할 실패 지점

- 테스트끼리 DB 상태가 섞이면 fixture scope와 초기화 위치를 다시 봅니다.
- mock이 너무 많아 실제 경로를 안 탄다면 integration test를 한 단계 추가합니다.
- `dependency_overrides`를 썼다면 테스트 끝에서 반드시 원복하는 습관을 들입니다.

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


## 추가 실전 섹션: 요청/응답 계약과 운영 패턴 심화

백엔드 품질은 기능 수보다 계약의 명확성과 운영 신뢰성에서 결정됩니다. 아래 표는 라우터-서비스-DB-인증-로깅-배포까지 이어지는 경계에서 자주 쓰는 선택 기준입니다.

| 계층 | 핵심 질문 | 권장 패턴 | 실패 신호 |
| --- | --- | --- | --- |
| Router/Controller | 입력이 어떤 계약을 가져야 하는가 | Pydantic 스키마 + 명시적 상태코드 | 200/500만 남발 |
| Service | 비즈니스 규칙이 어디에 있는가 | use case 단위 메서드 | 라우트에 로직 과밀 |
| Repository | 데이터 접근이 한곳에 모였는가 | 메서드 중심 데이터 추상화 | SQL 흩어짐 |
| Auth | 신원/권한이 분리되어 있는가 | AuthN/AuthZ 분리 + 짧은 토큰 | 서버 권한검사 누락 |
| Observability | 장애를 재현 없이 설명 가능한가 | request_id + 구조화 로그 | print 디버깅 의존 |
| Deploy | 재현 가능하게 배포되는가 | 이미지 버전 고정 + healthcheck | 수동 SSH 배포 |

### FastAPI 요청/응답 예시: 계약이 드러나는 엔드포인트

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

class OrderIn(BaseModel):
    item_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=100)

@app.post('/orders', status_code=201)
def create_order(payload: OrderIn):
    if payload.quantity > 20:
        raise HTTPException(status_code=409, detail='stock conflict')
    return {'order_id': 101, 'item_id': payload.item_id, 'quantity': payload.quantity}
```

입력 검증과 상태코드를 분리하면 클라이언트 재시도 정책, 알람 기준, 운영 대시보드 해석이 훨씬 명확해집니다.

### Middleware 패턴: request_id + 지연 시간 측정

```python
import time
import uuid
from fastapi import Request

@app.middleware('http')
async def tracing_middleware(request: Request, call_next):
    rid = str(uuid.uuid4())
    request.state.request_id = rid
    start = time.perf_counter()
    response = await call_next(request)
    latency_ms = (time.perf_counter() - start) * 1000
    response.headers['X-Request-ID'] = rid
    response.headers['X-Response-Time-MS'] = f'{latency_ms:.2f}'
    return response
```

운영에서는 "느리다"보다 "어느 요청이 몇 ms 걸렸는가"가 더 중요합니다. 이 헤더와 로그 필드가 있으면 API 게이트웨이/애플리케이션 로그를 상호 추적하기 쉬워집니다.

### API 응답 계약 표준화 예시

| 상황 | HTTP | body 예시 | 클라이언트 액션 |
| --- | --- | --- | --- |
| 입력 오류 | 422/400 | `{ "code": "invalid_input", ... }` | 사용자 입력 수정 |
| 인증 실패 | 401 | `{ "code": "unauthorized" }` | 토큰 갱신/재로그인 |
| 권한 부족 | 403 | `{ "code": "forbidden" }` | 권한 요청 |
| 충돌 | 409 | `{ "code": "conflict" }` | 재시도 또는 사용자 안내 |
| 서버 오류 | 500 | `{ "code": "internal_error" }` | 재시도 + 관찰 |

응답 계약이 고정되면 프론트엔드, 모바일, 배치 클라이언트가 동일한 오류 처리 전략을 재사용할 수 있습니다.

### 배포 전 체크 시나리오

1. `GET /healthz`와 핵심 비즈니스 경로를 동시에 확인합니다.
2. 새 버전에서 에러율/지연시간이 baseline 대비 악화되지 않았는지 봅니다.
3. 데이터베이스 migration의 롤백 경로를 문서로 확인합니다.
4. 운영 secret이 이미지에 포함되지 않았는지 검증합니다.
5. 롤백 명령을 실제로 1회 리허설합니다.

이 체크리스트는 기능 완성보다 운영 안정성을 우선순위로 두는 습관을 만들어 줍니다.


## 처음 질문으로 돌아가기

- **unit, integration, E2E 테스트는 각각 무엇을 검증할까요?**
  - 본문의 기준은 백엔드 테스트를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **pytest로 service를 어떻게 테스트할 수 있을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **FastAPI `TestClient`는 endpoint를 어떻게 검증하게 해 줄까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Backend Development 101 (1/10): 백엔드 개발이란 무엇인가?](./01-what-is-backend-development.md)
- [Backend Development 101 (2/10): HTTP 서버 만들기](./02-building-an-http-server.md)
- [Backend Development 101 (3/10): Routing과 Controller](./03-routing-and-controllers.md)
- [Backend Development 101 (4/10): Service Layer](./04-service-layer.md)
- [Backend Development 101 (5/10): Database Layer](./05-database-layer.md)
- [Backend Development 101 (6/10): 인증과 권한](./06-auth-and-authorization.md)
- [Backend Development 101 (7/10): Logging과 Error Handling](./07-logging-and-error-handling.md)
- **백엔드 테스트 (현재 글)**
- 백엔드 배포 (예정)
- 운영 가능한 백엔드 구조 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [pytest documentation](https://docs.pytest.org/en/stable/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

### 추가 읽을거리

- [Testing pyramid (Martin Fowler)](https://martinfowler.com/articles/practical-test-pyramid.html)

Tags: Backend, Testing, Pytest, Python, QualityAssurance
