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

이 글은 Backend Development 101 시리즈의 8번째 글입니다.


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

## 개선 전/개선 후

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

### 단계 1 — 첫 파이썬 테스트 실행

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

### 단계 2 — 모의 객체로 서비스 단위 테스트

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

### 단계 3 — 프레임워크 테스트 클라이언트

```python
# tests/test_api.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    assert client.get("/health").status_code == 200
```

TestClient를 쓰면 실제 서버 프로세스를 띄우지 않고도 endpoint를 호출할 수 있습니다. 라우팅과 응답 형식 검증에 매우 유용합니다.

### 단계 4 — 메모리 기반 데이터베이스 픽스처

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

### 단계 5 — 의존성 오버라이드

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

### 웹 프레임워크 요청/응답 예시: 계약이 드러나는 엔드포인트

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

### 미들웨어 패턴: 요청 식별자와 지연 시간 측정

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

### 응용 프로그램 인터페이스 응답 계약 표준화 예시

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


## 실전 앵커: 운영 가능한 백엔드 기준선

입문 단계에서 가장 흔한 오해는 "기능이 동작하면 백엔드가 완성되었다"는 판단입니다. 실제 운영에서는 기능 성공률보다 실패 시 복구 속도, 오류 원인 분리 가능성, 배포 재현 가능성이 더 먼저 평가됩니다. 아래 예시는 라우트-검증-인증-서비스-저장소-배포까지 이어지는 기준선을 하나의 흐름으로 고정하는 방법입니다.

### 요청 검증과 라우트 계약을 먼저 고정하기

```python
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix='/v1/orders', tags=['orders'])

class CreateOrderBody(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=50)
    coupon_code: str | None = Field(default=None, min_length=4, max_length=32)

@router.post('', status_code=status.HTTP_201_CREATED)
def create_order(body: CreateOrderBody):
    if body.quantity > 20:
        raise HTTPException(status_code=409, detail='재고 충돌이 발생했습니다.')
    return {
        'order_id': 1001,
        'product_id': body.product_id,
        'quantity': body.quantity,
        'coupon_code': body.coupon_code,
    }
```

검증 규칙을 코드에 박아두면 API 문서와 런타임 동작이 어긋나는 구간이 줄어듭니다. 특히 `409`, `422`, `401`처럼 의미를 가진 상태 코드를 먼저 분리해 두면 클라이언트 재시도 정책도 단순해집니다.

### ORM 모델과 저장소 경계를 분리하기

```python
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String(30), default='user', nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default='created', nullable=False)
    user: Mapped[User] = relationship()
```

모델은 스키마를 설명하고, 저장소는 데이터 접근 전략을 설명해야 합니다. 한 함수에서 SQL 작성, 비즈니스 정책, 응답 직렬화를 모두 처리하면 변경 범위를 예측하기 어렵습니다.

### 인증 미들웨어와 권한 검사 분리하기

```python
from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt

SECRET_KEY = 'replace-in-env'
ALGORITHM = 'HS256'

def require_identity(request: Request):
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='토큰이 필요합니다.')

    token = auth.split(' ', 1)[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise HTTPException(status_code=401, detail='유효하지 않은 토큰입니다.') from exc

    subject = payload.get('sub')
    role = payload.get('role', 'user')
    if not subject:
        raise HTTPException(status_code=401, detail='토큰 주체가 비어 있습니다.')
    return {'sub': subject, 'role': role}

def require_admin(identity = Depends(require_identity)):
    if identity['role'] != 'admin':
        raise HTTPException(status_code=403, detail='관리자 권한이 필요합니다.')
    return identity
```

인증(Authentication)과 인가(Authorization)를 분리하면 장애 원인도 분리됩니다. 토큰 형식 문제는 `401`, 권한 부족은 `403`으로 명확하게 갈라져야 운영 대시보드에서 경향을 읽을 수 있습니다.

### 전역 예외 처리와 로그 정책

```python
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()
logger = logging.getLogger('backend')

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(
        'unhandled_exception',
        extra={
            'path': request.url.path,
            'method': request.method,
            'client': request.client.host if request.client else 'unknown',
        },
    )
    return JSONResponse(
        status_code=500,
        content={'code': 'internal_error', 'message': '일시적인 오류가 발생했습니다.'},
    )
```

"오류를 숨기는 것"과 "오류를 통제하는 것"은 다릅니다. 사용자에게는 안정된 계약을 주고, 내부 로그에는 분석 가능한 맥락을 남겨야 다음 배포에서 같은 장애를 줄일 수 있습니다.

### 배포 설정을 코드와 함께 버전 고정하기

```yaml
services:
  api:
    image: ghcr.io/yeongseon-books/backend101-api:1.0.0
    ports:
      - '8000:8000'
    env_file:
      - .env
    environment:
      - APP_ENV=production
      - LOG_LEVEL=INFO
      - DATABASE_URL=postgresql+psycopg://app:app@db:5432/app
    command: >
      uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
    healthcheck:
      test: ['CMD', 'curl', '-f', 'http://localhost:8000/healthz']
      interval: 15s
      timeout: 3s
      retries: 5
      start_period: 10s
```

배포 설정은 문서가 아니라 실행 파일이어야 합니다. 이미지 태그를 고정하고 헬스체크를 포함하면 "어제는 됐는데 오늘은 안 된다"는 비재현 문제를 크게 줄일 수 있습니다.

### 운영 전 체크리스트: 실패를 가정하고 검증하기

1. 입력 검증 실패(`422/400`)와 비즈니스 충돌(`409`)이 구분되는지 확인합니다.
2. 토큰 누락, 토큰 만료, 권한 부족이 `401/403`으로 분리되는지 확인합니다.
3. 데이터베이스 타임아웃 시 재시도 정책과 사용자 메시지가 분리되는지 확인합니다.
4. 배포 직후 `healthz`와 핵심 API 성공률을 함께 확인합니다.
5. 장애 로그만으로 요청 식별자, 사용자 식별자, 실패 경로를 역추적할 수 있는지 확인합니다.

이 기준선을 매 글의 주제에 연결해 두면 학습이 단발성 지식으로 끝나지 않습니다. 라우팅을 배울 때도, 테스트를 배울 때도, 배포를 배울 때도 같은 운영 질문으로 품질을 판별하게 됩니다.



### 장애 복구 훈련 시나리오

다음 시나리오는 문서로만 읽지 말고 실제로 실행해야 효과가 있습니다. 첫째, 데이터베이스 연결 문자열을 일부러 잘못 넣은 뒤 애플리케이션이 어떤 상태 코드를 반환하는지 확인합니다. 둘째, 인증 헤더를 제거한 요청과 만료 토큰 요청을 각각 보내서 인증 실패와 권한 실패가 로그에서 구분되는지 점검합니다. 셋째, 동일한 요청을 짧은 간격으로 반복 호출해서 지연 시간 분포가 비정상적으로 튀는 구간이 있는지 확인합니다.

여기서 핵심은 "문제가 생겼다"가 아니라 "어떤 계층에서 문제가 생겼는가"를 즉시 분류하는 습관입니다. 라우트 계약 문제인지, 서비스 규칙 문제인지, 저장소 연결 문제인지, 배포 설정 문제인지가 1차 대응 속도를 좌우합니다. 팀이 같은 체크리스트와 같은 로그 필드를 공유하면, 장애 대응이 개인 역량이 아니라 시스템 역량으로 바뀝니다.

### 배포 변경 점검 표

| 변경 항목 | 사전 확인 | 배포 직후 확인 | 실패 시 대응 |
| --- | --- | --- | --- |
| 환경 변수 변경 | 필수 키 존재, 기본값 검토 | 부팅 로그에서 로딩 확인 | 즉시 롤백, 누락 키 보완 |
| 의존성 버전 변경 | 호환성 노트 확인 | 핵심 경로 지연 시간 비교 | 이전 이미지 재배포 |
| 데이터베이스 스키마 변경 | 마이그레이션 롤백 스크립트 점검 | 읽기/쓰기 경로 샘플 호출 | 스키마 롤백 또는 읽기 전용 전환 |
| 인증 정책 변경 | 테스트 토큰으로 권한 매트릭스 점검 | 401/403 비율 관찰 | 정책 플래그 즉시 원복 |

이 표를 릴리스 템플릿에 넣어두면 매번 같은 실수를 반복하지 않게 됩니다. 백엔드 품질은 새 기능 추가 속도보다 변경 실패를 얼마나 빨리 안전하게 되돌릴 수 있는지에서 결정됩니다.


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

- [backend-development-101 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/backend-development-101/ko)

- [Testing pyramid (Martin Fowler)](https://martinfowler.com/articles/practical-test-pyramid.html)

Tags: Backend, Testing, Pytest, Python, QualityAssurance
