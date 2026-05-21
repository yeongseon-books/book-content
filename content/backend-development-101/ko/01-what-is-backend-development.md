---
series: backend-development-101
episode: 1
title: "Backend Development 101 (1/10): 백엔드 개발이란 무엇인가?"
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
  - WebDevelopment
  - HTTP
  - Architecture
  - Python
seo_description: 백엔드 개발의 역할과 계층 구조를 정의하고, 요청이 HTTP 서버부터 데이터베이스까지 흐르는 전체 지도를 한눈에 파악합니다.
last_reviewed: '2026-05-15'
---

# Backend Development 101 (1/10): 백엔드 개발이란 무엇인가?

이 글은 Backend Development 101 시리즈의 1번째 글입니다.


사용자는 화면만 보지만, 서비스가 오래 버티는지는 화면 뒤의 구조가 결정합니다. 요청을 어디서 받고, 어떤 규칙을 어디에 두고, 데이터를 어디까지 믿을지 정하지 않으면 기능은 금방 붙어도 운영은 오래 가지 못합니다.

이 글은 Backend Development 101 시리즈의 첫 번째 글입니다. 여기서는 백엔드를 하나의 기술이 아니라 요청을 받고, 규칙을 적용하고, 데이터를 다루고, 응답을 돌려주는 책임의 집합으로 이해해 보겠습니다.

## 먼저 던지는 질문

- 백엔드는 정확히 어떤 역할과 경계를 가지는 계층일까요?
- 하나의 요청은 HTTP 서버, 라우터, 서비스, 데이터베이스를 어떻게 통과할까요?
- 왜 백엔드를 한 덩어리가 아니라 여러 레이어로 나눠 이해해야 할까요?

## 큰 그림

![Backend Development 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/backend-development-101/01/01-01-concept-at-a-glance.ko.png)

*Backend Development 101 1장 흐름 개요*

## 왜 중요한가

프론트엔드만 만들면 사용자가 보는 화면은 빠르게 만들 수 있습니다. 하지만 데이터, 인증, 정합성, 운영 같은 문제는 모두 화면 뒤에서 처리됩니다. 결국 시스템이 오래 살아남으려면 백엔드가 어떤 책임을 지는지부터 분명히 이해해야 합니다.

백엔드는 눈에 잘 보이지 않지만, 실제로는 가장 많은 운영 판단이 모이는 곳입니다. 어떤 입력을 믿을 수 있는지, 어떤 데이터를 저장해야 하는지, 오류를 어떻게 남기고 복구할지 같은 결정이 모두 여기서 내려집니다. 그래서 입문 단계일수록 기능 이름보다 책임의 지도를 먼저 잡는 편이 훨씬 중요합니다.

> 백엔드는 하나의 기능이 아니라, 요청을 받아 규칙을 적용하고 데이터를 다루는 책임의 집합입니다.

## 한눈에 보는 개념

요청은 왼쪽에서 오른쪽으로 흘러가고, 응답은 같은 길을 되짚어 돌아옵니다. 이 그림만 이해해도 이후 글에서 배우는 HTTP, 라우팅, 서비스, 데이터베이스, 인증, 로깅, 테스트, 배포가 모두 하나의 구조 안에 들어간다는 감각을 잡을 수 있습니다.

## 핵심 용어

- **HTTP server**: 요청이 가장 먼저 도착하는 입구입니다.
- **Router**: 어떤 경로를 어떤 함수가 처리할지 정합니다.
- **Service**: 비즈니스 규칙이 머무는 계층입니다.
- **Repository**: 데이터베이스와 대화하는 계층입니다.
- **Middleware**: 모든 요청에 공통으로 적용되는 동작입니다.

이 용어들이 중요한 이유는, 백엔드 코드를 읽을 때 결국 “이 책임을 어느 층에 두어야 하는가”를 계속 판단하게 되기 때문입니다. 용어가 곧 구조의 경계라고 생각하면 훨씬 덜 헷갈립니다.

## 개선 전/개선 후

**Before (the frontend does everything)**

```python
# A password check inside the browser
if password == "admin123":
    show_dashboard()
```

**After (the backend owns the rule)**

```python
# server.py
@app.post("/login")
def login(body):
    if not auth.verify(body["email"], body["password"]):
        return 401, {"error": "invalid"}
    return 200, {"token": auth.token(body["email"])}
```

비밀번호 검증은 클라이언트가 아니라 서버가 책임져야 합니다. 클라이언트는 결과를 소비하는 쪽이고, 규칙을 집행하는 쪽은 백엔드입니다. 이 구분이 흐려지면 보안과 운영 품질이 한 번에 무너집니다.

## 실습: 다섯 단계로 보는 첫 번째 백엔드

### 단계 1 — 가장 작은 서버

```python
# 1_app.py
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def hello():
    return {"message": "hello"}
```

이 예제는 가장 작은 형태의 백엔드입니다. 경로 하나와 함수 하나만 있어도 이미 서버는 요청을 받고 응답을 돌려줄 수 있습니다.

### 단계 2 — 실행하기

```bash
uvicorn 1_app:app --reload
```

`http://127.0.0.1:8000/`를 열면 JSON 응답이 보입니다. 이 순간부터 백엔드는 화면을 그리는 프로그램이 아니라 데이터를 반환하는 프로그램이라는 사실이 분명해집니다.

### 단계 3 — 라우트 추가

```python
# 2_routes.py
from fastapi import FastAPI
app = FastAPI()

USERS = [{"id": 1, "name": "Alice"}]

@app.get("/users")
def list_users():
    return USERS
```

경로를 하나 더 추가하면 서버는 다른 주소를 다른 함수로 연결하기 시작합니다. 백엔드 구조가 복잡해지는 출발점이 바로 여기입니다.

### 단계 4 — 입력 받기

```python
# 3_input.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserIn(BaseModel):
    name: str

@app.post("/users")
def create_user(payload: UserIn):
    return {"id": 99, "name": payload.name}
```

입력을 받는 순간부터 검증이 중요해집니다. 백엔드는 사용자가 보낸 값을 그대로 믿지 않고, 먼저 형태와 타입을 확인해야 합니다.

### 단계 5 — 요청 호출하기

```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"name":"Bob"}' http://127.0.0.1:8000/users
```

요청을 보내고 JSON을 돌려받으면, 백엔드의 가장 기본적인 책임이 모두 한 바퀴 연결됩니다. 경로를 고르고, 입력을 검증하고, 데이터를 만들고, 응답을 반환하는 흐름입니다.

## 검증 포인트

**Expected output:** `uvicorn 1_app:app --reload` 뒤에 `/`는 `{"message": "hello"}`를, `POST /users`는 새 사용자 JSON을 반환해야 합니다.

### 먼저 확인할 실패 지점

- `uvicorn`이 `1_app:app`을 찾지 못하면 파일명과 앱 객체 이름이 맞는지 봅니다.
- `POST /users`가 `422`를 반환하면 `name` 필드가 payload에 포함되었는지 확인합니다.
- `GET /users`가 비어 있어도 정상입니다. 여기서 중요한 것은 요청 흐름이 라우트와 응답으로 연결되는지입니다.

## 이 코드에서 먼저 볼 점

- 서버는 결국 경로를 함수에 연결하는 구조입니다.
- 입력은 함수에 도달하기 전에 검증됩니다.
- 응답은 화면이 아니라 JSON 같은 데이터입니다.

이 세 가지를 먼저 이해하면 이후의 모든 세부 주제가 어디에 붙는지 자연스럽게 보입니다. 인증은 입력과 권한 검증에 붙고, 데이터베이스는 서비스 뒤쪽에 붙고, 로깅은 전체 흐름을 따라갑니다.

## 자주 하는 실수 5가지

1. **백엔드를 데이터베이스 코드와 동일시하는 실수**입니다. 실제로는 라우팅, 인증, 검증, 로깅, 배포까지 모두 포함합니다.
2. **모든 로직을 라우트 핸들러에 넣는 실수**입니다. 파일 하나가 금방 통제 불가능해집니다.
3. **클라이언트 검증만 믿는 실수**입니다. 서버는 항상 다시 검증해야 합니다.
4. **모든 오류를 500으로 돌려주는 실수**입니다. 400, 404, 409 같은 의미 있는 상태 코드를 써야 합니다.
5. **로그를 남기지 않는 실수**입니다. 운영에서 무슨 일이 있었는지 알 방법이 사라집니다.

## 운영에서는 이렇게 드러납니다

스타트업이든 큰 회사든 백엔드의 큰 형태는 크게 다르지 않습니다. Router, Service, Repository, Middleware라는 분리가 유지되고, 팀은 그 경계를 기준으로 기능을 추가합니다. 이 지도를 한 번 익혀 두면 처음 보는 코드베이스도 훨씬 빨리 읽을 수 있습니다.

반대로 이 구조를 건너뛰면 새 프로젝트를 볼 때마다 파일 배치와 책임 분리가 모두 낯설게 느껴집니다. 결국 백엔드 입문의 핵심은 프레임워크 문법보다 구조 감각을 먼저 얻는 데 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 비즈니스 규칙은 라우트가 아니라 서비스에 둡니다.
- 모든 입력은 항상 다시 검증합니다.
- 모든 의존성은 테스트 가능하도록 주입할 수 있어야 합니다.
- 로그와 메트릭은 코드와 함께 설계합니다.
- 기준은 “내 컴퓨터에서 동작한다”가 아니라 “운영 가능하다”입니다.

## 체크리스트

- [ ] 백엔드의 다섯 레이어를 말할 수 있습니다.
- [ ] 가장 작은 FastAPI 서버를 실행할 수 있습니다.
- [ ] GET과 POST의 차이를 설명할 수 있습니다.
- [ ] 입력 검증이 왜 중요한지 설명할 수 있습니다.
- [ ] 다음 글이 무엇을 다루는지 알고 있습니다.

## 연습 문제

1. `/health` 경로를 추가하고 `{"status": "ok"}`를 반환해 보세요.
2. `GET /users/{user_id}`를 추가하고 path parameter를 그대로 돌려줘 보세요.
3. `POST /login`에서 비밀번호가 틀리면 `401`을 반환하도록 바꿔 보세요.

## 정리와 다음 글

백엔드는 하나의 기능이 아니라 여러 책임이 모인 구조입니다. 다음 글에서는 그중 가장 아래쪽 입구를 열어, HTTP 서버가 실제로 어떻게 요청을 읽고 응답을 쓰는지 직접 살펴보겠습니다.


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



## 추가 보강: 검증 가능한 예제 세트

### 입력 크기 대비 알고리즘/학습 선택 표

| 상황 | 빠른 선택 | 검증 기준 |
| --- | --- | --- |
| 작은 입력, 빠른 프로토타입 | 단순 구현 우선 | 정답 검증 테스트 3종 |
| 큰 입력, 지연시간 민감 | 차수 낮은 알고리즘 또는 안정적 optimizer | 시간/메모리 동시 측정 |
| 운영 장애 재현 필요 | 로그/추적 필드 강화 | 동일 입력 재실행 가능성 |

### 짧은 비교 코드

```python
import time

def measure(fn, *args, repeat=3):
    best = float('inf')
    for _ in range(repeat):
        t0 = time.perf_counter()
        fn(*args)
        best = min(best, time.perf_counter() - t0)
    return best
```

측정 코드는 화려할 필요가 없습니다. 같은 입력, 같은 환경, 같은 반복 기준을 유지하는 것이 더 중요합니다. 이 습관이 있어야 최적화 전후의 차이를 신뢰할 수 있습니다.

### 실전 점검 질문

1. 지금 선택한 방법의 시간/공간 비용을 한 문장으로 설명할 수 있는가
2. 경계 입력에서 동작이 바뀌는 지점을 테스트로 고정했는가
3. 운영 로그만으로 실패 원인을 분리할 수 있는가

이 질문에 즉답할 수 있으면 구현이 아니라 설계 수준에서 품질을 확보한 상태에 가깝습니다.

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

- **백엔드는 정확히 어떤 역할과 경계를 가지는 계층일까요?**
  - 본문의 기준은 백엔드 개발이란 무엇인가?를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **하나의 요청은 HTTP 서버, 라우터, 서비스, 데이터베이스를 어떻게 통과할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **왜 백엔드를 한 덩어리가 아니라 여러 레이어로 나눠 이해해야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **백엔드 개발이란 무엇인가? (현재 글)**
- HTTP 서버 만들기 (예정)
- Routing과 Controller (예정)
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

- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [HTTP overview (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview)
- [The Twelve-Factor App](https://12factor.net/)

### 추가 읽을거리

- [backend-development-101 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/backend-development-101/ko)

- [Backend roadmap](https://roadmap.sh/backend)

Tags: Backend, WebDevelopment, HTTP, Architecture, Python
