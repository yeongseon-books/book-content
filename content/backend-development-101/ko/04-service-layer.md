---
series: backend-development-101
episode: 4
title: "Backend Development 101 (4/10): Service Layer"
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
  - Architecture
  - DesignPatterns
  - Python
  - DDD
seo_description: 서비스 레이어의 역할과 비즈니스 로직을 모으는 기준을 정리하고, 의존성 주입과 트랜잭션 경계 설계를 통해 테스트 가능성을 높입니다.
last_reviewed: '2026-05-15'
---

# Backend Development 101 (4/10): Service Layer

이 글은 Backend Development 101 시리즈의 4번째 글입니다.


controller가 점점 많은 일을 맡기 시작하면 같은 비즈니스 규칙이 REST, 배치, 다른 인터페이스에 흩어지기 쉽습니다. 이때 가장 먼저 무너지는 것은 코드 길이가 아니라 규칙의 단일 출처입니다.

이 글은 Backend Development 101 시리즈의 네 번째 글입니다. 여기서는 비즈니스 로직이 왜 service layer에 모여야 하는지, 그리고 그 경계가 왜 운영 수명과 테스트 가능성을 좌우하는지 살펴보겠습니다.

## 먼저 던지는 질문

- 비즈니스 로직은 왜 controller도 repository도 아닌 service가 맡아야 할까요?
- controller, service, repository는 각각 어디까지 책임져야 할까요?
- 트랜잭션 경계는 어느 층에서 시작하는 편이 자연스러울까요?

## 큰 그림

![Backend Development 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/backend-development-101/04/04-01-concept-at-a-glance.ko.png)

*Backend Development 101 4장 흐름 개요*

## 왜 중요한가

비즈니스 로직을 controller에 넣으면 같은 규칙이 여러 입구에 흩어집니다. REST API, gRPC, 배치 작업이 모두 같은 규칙을 써야 하는데, 각 입구마다 중복 구현이 생기기 쉽습니다. 반대로 service에 규칙을 모아 두면 어떤 경로로 들어오든 같은 판단을 하게 만들 수 있습니다.

결국 service layer는 코드 정리용 장식이 아니라, 비즈니스 규칙의 단일 출처를 만드는 장치입니다. 이 원칙 하나가 서비스의 유지보수성과 테스트 가능성을 크게 갈라놓습니다.

> 비즈니스 규칙은 입구가 아니라 service에 모여야 오래 버티는 구조가 됩니다.

## 한눈에 보는 개념

service는 오케스트레이터입니다. repository, 외부 API, 이벤트 버스를 연결하고 실행 순서를 조율합니다. 비즈니스 행위 하나가 service 메서드 하나로 드러나는 구조가 가장 읽기 쉽습니다.

## 핵심 용어

- **Service**: 하나의 비즈니스 use case를 책임지는 객체입니다.
- **Use case**: 주문 생성, 송금, 환불처럼 의미 있는 업무 시나리오입니다.
- **Transaction boundary**: 함께 commit되거나 rollback되는 작업 단위입니다.
- **Domain event**: 어떤 비즈니스 행위가 일어났음을 알리는 메시지입니다.
- **Dependency injection**: 협력 객체를 생성자나 인자로 전달받는 방식입니다.

## 개선 전/개선 후

**Before (컨트롤러가 모든 것을 처리)**

```python
@app.post("/orders")
def create_order(payload, db, mail):
    if payload.amount <= 0:
        raise HTTPException(400)
    order = db.insert("orders", payload.dict())
    mail.send(payload.email, "ordered")
    return order
```

**After (서비스가 규칙을 소유)**

```python
# services/order_service.py
class OrderService:
    def __init__(self, repo, mailer):
        self.repo = repo
        self.mailer = mailer

    def create(self, payload):
        if payload.amount <= 0:
            raise ValueError("amount must be > 0")
        order = self.repo.save(payload)
        self.mailer.send(payload.email, "ordered")
        return order

# routers/orders.py
@router.post("")
def create_order(payload, svc: OrderService = Depends(get_order_service)):
    return svc.create(payload)
```

controller가 얇아지면 같은 service를 배치 작업이나 다른 인터페이스에서도 그대로 재사용할 수 있습니다. 입구가 바뀌어도 규칙이 바뀌지 않는다는 점이 핵심입니다.

## 실습: 다섯 단계로 보는 서비스 계층

### 단계 1 — 가장 작은 서비스

```python
# 1_service.py
class GreetService:
    def hello(self, name: str) -> str:
        return f"hello, {name}"
```

가장 작은 service는 입력을 받아 의미 있는 결과를 돌려주는 함수형 구조를 가집니다. 중요한 것은 파일 크기가 아니라 책임 이름이 분명한가입니다.

### 단계 2 — 의존성 주입

```python
# 2_di.py
class UserService:
    def __init__(self, repo):
        self.repo = repo

    def register(self, name: str):
        return self.repo.insert({"name": name})
```

service가 의존성을 직접 만들지 않고 전달받으면 테스트가 쉬워집니다. 실제 repository 대신 mock이나 fake를 넣어도 같은 규칙을 검증할 수 있기 때문입니다.

### 단계 3 — 트랜잭션 경계

```python
# 3_tx.py
class TransferService:
    def __init__(self, accounts, tx):
        self.accounts = accounts
        self.tx = tx

    def transfer(self, src, dst, amount):
        with self.tx.begin():
            self.accounts.debit(src, amount)
            self.accounts.credit(dst, amount)
```

트랜잭션은 repository가 아니라 service 안에서 시작하는 편이 자연스럽습니다. 하나의 use case가 여러 저장 작업을 묶어야 할 때, 그 경계를 service만이 알고 있기 때문입니다.

### 단계 4 — 외부 호출 통합

```python
# 4_external.py
class CheckoutService:
    def __init__(self, repo, payment_gw):
        self.repo = repo
        self.gw = payment_gw

    def checkout(self, cart):
        receipt = self.gw.charge(cart.total)
        return self.repo.save_order(cart, receipt.id)
```

외부 결제 게이트웨이 같은 의존성이 끼어드는 순간 service의 조율 역할이 더 선명해집니다. 어느 순서로 검증하고 저장하고 호출할지 결정하는 곳이 바로 여기입니다.

### 단계 5 — 도메인 이벤트 발행

```python
# 5_event.py
class OrderService:
    def __init__(self, repo, bus):
        self.repo = repo
        self.bus = bus

    def place(self, payload):
        order = self.repo.save(payload)
        self.bus.publish("OrderPlaced", {"id": order.id})
        return order
```

domain event를 발행하면 다른 기능이 service를 직접 호출하지 않고도 비즈니스 변화를 감지할 수 있습니다. 서비스 간 결합을 줄이는 데 도움이 되는 이유가 여기에 있습니다.

## 검증 포인트

**Expected output:** service 메서드는 HTTP 객체 없이 plain input만 받아도 같은 결과를 반환해야 하고, 트랜잭션 블록 안의 두 작업은 함께 성공하거나 함께 rollback되어야 합니다.

### 먼저 확인할 실패 지점

- service가 `HTTPException`을 직접 던지면 controller 경계가 무너진 신호입니다.
- repository가 트랜잭션을 열기 시작하면 use case 전체 경계가 어디인지 다시 확인합니다.
- 외부 API 호출 전후 순서를 설명하기 어려우면 service 책임이 섞인 경우가 많습니다.

## 이 코드에서 먼저 볼 점

- service는 의존성을 직접 생성하지 않고 전달받습니다.
- 트랜잭션은 repository가 아니라 service 안에서 시작합니다.
- 외부 호출은 다음 단계로 넘어가기 전에 검증되어야 합니다.

이 세 가지를 지키면 service 파일만 읽어도 비즈니스 규칙의 핵심 흐름이 보입니다. 반대로 경계가 흐려지면 규칙이 controller, repository, 외부 모듈로 흩어져 읽기 어려워집니다.

## 자주 하는 실수 5가지

1. **HTTP request 객체를 service에 그대로 넘기는 실수**입니다. service는 plain input을 받는 편이 좋습니다.
2. **service에서 `HTTPException`을 던지는 실수**입니다. 도메인 오류는 controller에서 HTTP로 번역하는 편이 낫습니다.
3. **repository에서 트랜잭션을 여는 실수**입니다. 하나의 use case가 둘 이상의 트랜잭션으로 쪼개질 수 있습니다.
4. **service끼리 서로 직접 import하는 실수**입니다. 순환 의존성이 생기기 쉽고, event bus 같은 다른 연결 방식이 더 낫습니다.
5. **모든 메서드를 하나의 service에 몰아넣는 실수**입니다. 도메인별로 나눌수록 읽기 쉽습니다.

## 운영에서는 이렇게 드러납니다

큰 백엔드에서는 보통 `services/orders/`, `services/payments/`처럼 도메인별 service 디렉터리를 둡니다. use case 하나가 service 메서드 하나와 대응되도록 유지하면, 새 팀원이 들어와도 흐름을 빠르게 이해할 수 있습니다.

DDD를 엄격하게 적용하지 않더라도 이 분리는 거의 언제나 도움이 됩니다. service layer는 과한 추상이 아니라, 중복 규칙과 엉킨 책임을 막는 가장 실용적인 경계이기 때문입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 하나의 use case는 하나의 메서드로 읽혀야 합니다.
- service는 입력에서 결과로 이어지는 흐름으로 설계합니다.
- 트랜잭션 경계는 명시적으로 드러냅니다.
- 재시도 정책은 호출 지점이 아니라 service 안에서 결정합니다.
- service 파일만 읽어도 비즈니스 규칙이 설명되어야 합니다.

## 체크리스트

- [ ] controller / service / repository의 역할을 구분할 수 있습니다.
- [ ] service에 의존성을 주입할 수 있습니다.
- [ ] service 안에서 트랜잭션을 시작할 수 있습니다.
- [ ] HTTP 예외와 도메인 예외를 구분할 수 있습니다.
- [ ] domain event가 무엇인지 설명할 수 있습니다.

## 연습 문제

1. `RefundService.refund(order_id)`를 만들고 잘못된 ID에 `RefundError`를 던져 보세요.
2. `TransferService`에 잔액 부족 검사를 추가해 보세요.
3. service 메서드가 길어졌다면 새로운 service로 분리해 보세요.

## 정리와 다음 글

Service Layer는 비즈니스 규칙의 집입니다. 다음 글에서는 한 층 더 내려가, 데이터가 실제로 머무는 Database Layer를 살펴보겠습니다.


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

- **비즈니스 로직은 왜 controller도 repository도 아닌 service가 맡아야 할까요?**
  - 본문의 기준은 Service Layer를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **controller, service, repository는 각각 어디까지 책임져야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **트랜잭션 경계는 어느 층에서 시작하는 편이 자연스러울까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Backend Development 101 (1/10): 백엔드 개발이란 무엇인가?](./01-what-is-backend-development.md)
- [Backend Development 101 (2/10): HTTP 서버 만들기](./02-building-an-http-server.md)
- [Backend Development 101 (3/10): Routing과 Controller](./03-routing-and-controllers.md)
- **Service Layer (현재 글)**
- Database Layer (예정)
- 인증과 권한 (예정)
- Logging과 Error Handling (예정)
- 백엔드 테스트 (예정)
- 백엔드 배포 (예정)
- 운영 가능한 백엔드 구조 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [FastAPI dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)

### 추가 읽을거리

- [backend-development-101 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/backend-development-101/ko)

- [Service Layer pattern (Martin Fowler)](https://martinfowler.com/eaaCatalog/serviceLayer.html)
- [DDD reference (Eric Evans)](https://www.domainlanguage.com/ddd/reference/)
- [Architecture Patterns with Python](https://www.cosmicpython.com/)

Tags: Backend, Architecture, DesignPatterns, Python, DDD
