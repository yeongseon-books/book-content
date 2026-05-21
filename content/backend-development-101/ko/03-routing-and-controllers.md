---
series: backend-development-101
episode: 3
title: "Backend Development 101 (3/10): Routing과 Controller"
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
  - FastAPI
  - Architecture
  - REST
  - Python
seo_description: 라우터와 컨트롤러를 분리하여 백엔드 엔드포인트를 깔끔하게 설계하고, 입력 파라미터와 REST 스타일의 설계를 익힙니다.
last_reviewed: '2026-05-15'
---

# Backend Development 101 (3/10): Routing과 Controller

이 글은 Backend Development 101 시리즈의 3번째 글입니다.


엔드포인트가 몇 개 안 될 때는 한 파일에 몰아넣어도 돌아갑니다. 하지만 기능이 늘어나는 순간 코드는 급격히 읽기 어려워지고, 새 경로를 어디에 두어야 하는지부터 다시 고민하게 됩니다.

이 글은 Backend Development 101 시리즈의 세 번째 글입니다. 여기서는 router와 controller를 분리해 요청 입구를 정리하고, path·query·body parameter를 어떤 기준으로 나눠야 하는지 함께 살펴보겠습니다.


![Backend Development 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/backend-development-101/03/03-01-concept-at-a-glance.ko.png)
*Backend Development 101 3장 흐름 개요*

## 먼저 던지는 질문

- router와 controller는 각각 무엇을 책임져야 할까요?
- path, query, body parameter는 언제 어떻게 나눠 써야 할까요?
- REST 스타일 엔드포인트는 어떤 기준으로 설계해야 할까요?

## 왜 중요한가

작은 프로젝트에서는 한 파일도 충분해 보입니다. 하지만 엔드포인트 수가 늘어나면 그 한 파일이 곧 지옥이 됩니다. 새 기능이 들어올 때마다 “이 코드를 어디에 두지?”라는 질문이 생기면, 이미 구조가 약하다는 신호입니다.

좋은 구조는 매번 위치를 고민하지 않게 해 줍니다. router는 경로의 지도 역할을 하고, controller는 입력을 받고 다음 레이어로 넘기는 접수창구 역할을 합니다. 이 둘을 분리하면 기능이 커져도 코드가 스스로 정리되기 시작합니다.

> router는 주소를 고르고, controller는 입력을 받아 다음 레이어로 넘깁니다.

## 한눈에 보는 개념

router는 지도를, controller는 접수창구를, service는 실제 규칙을 처리하는 전문가를 떠올리면 이해하기 쉽습니다. 이 비유가 중요한 이유는, 요청이 복잡해져도 각 층이 맡아야 할 일이 달라지지 않기 때문입니다.

## 핵심 용어

- **Router**: URL 패턴을 핸들러에 연결하는 계층입니다.
- **Controller**: 요청을 받고 검증한 뒤 service를 호출하는 계층입니다.
- **Path parameter**: `/users/{id}`의 `{id}`처럼 자원을 식별하는 값입니다.
- **Query parameter**: `/users?active=true`의 `active`처럼 필터 조건입니다.
- **Body**: POST나 PUT 요청에서 전달하는 JSON payload입니다.

## 개선 전/개선 후

**Before (모든 것이 한 파일에)**

```python
# main.py
from fastapi import FastAPI
app = FastAPI()

@app.get("/users")
def list_users(): ...

@app.get("/orders")
def list_orders(): ...

@app.get("/products")
def list_products(): ...
```

**After (모듈마다 라우터 분리)**

```python
# routers/users.py
from fastapi import APIRouter
router = APIRouter(prefix="/users", tags=["users"])

@router.get("")
def list_users():
    return []

# main.py
from fastapi import FastAPI
from routers import users, orders
app = FastAPI()
app.include_router(users.router)
app.include_router(orders.router)
```

기능마다 파일을 나누면 수정 위치가 분명해집니다. 어떤 경로가 어디에 있는지 찾는 시간이 줄어드는 것만으로도 코드베이스 수명이 크게 늘어납니다.

## 실습: 다섯 단계로 정리하는 라우팅

### 단계 1 — 경로 파라미터

```python
# 1_path.py
from fastapi import FastAPI
app = FastAPI()

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"id": user_id}
```

path parameter는 대개 자원의 정체성을 나타냅니다. `/users/10`에서 `10`은 필터가 아니라 특정 사용자를 가리키는 식별자입니다.

### 단계 2 — 쿼리 파라미터

```python
# 2_query.py
from fastapi import FastAPI
app = FastAPI()

@app.get("/users")
def list_users(active: bool = True, limit: int = 10):
    return {"active": active, "limit": limit}
```

query parameter는 목록을 좁히거나 정렬 방식을 조정할 때 자연스럽습니다. identity가 아니라 filtering에 가깝다는 점이 핵심입니다.

### 단계 3 — 자바스크립트 객체 표기법 본문

```python
# 3_body.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserIn(BaseModel):
    name: str
    age: int

@app.post("/users")
def create_user(payload: UserIn):
    return {"id": 1, **payload.model_dump()}
```

body는 새 자원을 만들거나 기존 자원을 변경할 때 의미를 가집니다. 입력 모델을 명시하면 서버는 유효하지 않은 payload를 자동으로 거절할 수 있습니다.

### 단계 4 — 라우터 분리

```python
# routers/products.py
from fastapi import APIRouter
router = APIRouter(prefix="/products", tags=["products"])

@router.get("")
def list_products():
    return []

@router.get("/{pid}")
def get_product(pid: int):
    return {"id": pid}
```

도메인별로 router를 분리하면 products, orders, users처럼 관심사가 파일 구조에 그대로 드러납니다. 기능이 늘수록 이런 물리적 분리가 큰 힘을 발휘합니다.

### 단계 5 — 컨트롤러에서 서비스 호출

```python
# controllers/user_controller.py
from services.user_service import UserService

class UserController:
    def __init__(self, svc: UserService):
        self.svc = svc

    def create(self, payload):
        return self.svc.register(payload.name, payload.age)
```

controller는 얇게 유지해야 합니다. 입력을 받고 필요한 검증을 거친 뒤, 실제 비즈니스 규칙은 service에 넘기는 것이 핵심입니다.

## 검증 포인트

**Expected output:** `/users/10`은 `{"id": 10}`을, `GET /users?active=false&limit=5`는 필터 값이 반영된 JSON을 반환해야 합니다.

### 먼저 확인할 실패 지점

- path parameter 타입이 맞지 않으면 FastAPI가 `422`를 반환합니다.
- `APIRouter`를 분리한 뒤 경로가 안 보이면 `include_router()` 호출 여부를 먼저 봅니다.
- controller가 비대해지면 service 호출과 입력 변환만 남도록 다시 나눕니다.

## 이 코드에서 먼저 볼 점

- path는 주로 identity, query는 주로 filtering에 씁니다.
- body는 POST, PUT, PATCH에서 의미가 큽니다.
- `tags`는 OpenAPI 문서에서 엔드포인트를 그룹화합니다.

이 구분이 중요한 이유는 API가 커질수록 URL 설계가 곧 유지보수성으로 이어지기 때문입니다. 파라미터의 역할이 명확할수록 문서도 읽기 쉬워지고, 클라이언트와의 계약도 더 안정적이 됩니다.

## 자주 하는 실수 5가지

1. **모든 입력을 query string에 몰아넣는 실수**입니다. 필터는 query, 새 자원은 body가 자연스럽습니다.
2. **비즈니스 로직을 controller에 넣는 실수**입니다. 재사용성과 테스트성이 모두 떨어집니다.
3. **`/getUsers` 같은 동사형 URL을 쓰는 실수**입니다. REST는 명사와 HTTP 메서드 조합을 선호합니다.
4. **검증되지 않은 입력을 바로 DB로 보내는 실수**입니다. Pydantic 모델로 항상 경계를 세워야 합니다.
5. **GET으로 상태를 바꾸는 실수**입니다. GET은 안전해야 합니다.

## 운영에서는 이렇게 드러납니다

큰 백엔드에서는 보통 `routers/orders.py`, `routers/payments.py`처럼 도메인별 router 디렉터리를 둡니다. 새 기능이 들어오면 먼저 “어느 router에 어떤 path를 추가할 것인가”부터 정합니다. 이 단순한 규칙 하나가 코드베이스의 수명을 몇 년씩 늘려 줍니다.

controller를 얇게 유지하면 인증, 로깅, 테스트 전략도 함께 단순해집니다. 요청 입구를 읽는 데 걸리는 시간이 줄어들기 때문입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- URL은 명사이고, 동작은 HTTP 메서드가 표현합니다.
- controller는 한 화면 안에 들어올 정도로 얇아야 합니다.
- 입력은 항상 Pydantic으로 모델링합니다.
- 인증과 로깅 middleware는 router 수준에서 붙입니다.
- 새 엔드포인트를 만들기 전에 기존 엔드포인트를 확장할 수 있는지 먼저 봅니다.

## 체크리스트

- [ ] path, query, body parameter를 구분할 수 있습니다.
- [ ] `APIRouter`로 라우트를 분리할 수 있습니다.
- [ ] 명사 기반 REST URL을 설계할 수 있습니다.
- [ ] controller에서 service로 흐르는 구조를 설명할 수 있습니다.
- [ ] `/docs`의 OpenAPI 문서를 열어 보았습니다.

## 연습 문제

1. `/orders` router를 만들고 `GET /orders`, `GET /orders/{id}`, `POST /orders`를 추가해 보세요.
2. `GET /users`에 `?role=admin` 필터를 추가해 보세요.
3. Pydantic `OrderIn` 모델을 만들고 잘못된 payload에 `422`가 나오는지 확인해 보세요.

## 정리와 다음 글

router는 지도이고 controller는 접수창구입니다. 다음 글에서는 그 뒤편으로 들어가, 실제 비즈니스 규칙이 머무는 Service Layer를 살펴보겠습니다.


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

- **router와 controller는 각각 무엇을 책임져야 할까요?**
  - 본문의 기준은 Routing과 Controller를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **path, query, body parameter는 언제 어떻게 나눠 써야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **REST 스타일 엔드포인트는 어떤 기준으로 설계해야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Backend Development 101 (1/10): 백엔드 개발이란 무엇인가?](./01-what-is-backend-development.md)
- [Backend Development 101 (2/10): HTTP 서버 만들기](./02-building-an-http-server.md)
- **Routing과 Controller (현재 글)**
- Service Layer (예정)
- Database Layer (예정)
- 인증과 권한 (예정)
- Logging과 Error Handling (예정)
- 백엔드 테스트 (예정)
- 백엔드 배포 (예정)
- 운영 가능한 백엔드 구조 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [FastAPI Path operations](https://fastapi.tiangolo.com/tutorial/path-params/)
- [FastAPI APIRouter](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [Pydantic Models](https://docs.pydantic.dev/latest/concepts/models/)

### 추가 읽을거리

- [backend-development-101 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/backend-development-101/ko)

- [REST API Tutorial](https://restfulapi.net/)

Tags: Backend, FastAPI, Architecture, REST, Python
