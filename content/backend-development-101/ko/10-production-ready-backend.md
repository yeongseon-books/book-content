---
series: backend-development-101
episode: 10
title: "Backend Development 101 (10/10): 운영 가능한 백엔드 구조"
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
  - BestPractices
  - Python
  - Production
seo_description: 운영 가능한 백엔드 프로젝트의 구조와 설정 전략, 관측성(Observability)을 프로젝트에 녹여내는 기준을 정리합니다.
last_reviewed: '2026-05-15'
---

# Backend Development 101 (10/10): 운영 가능한 백엔드 구조

이 글은 Backend Development 101 시리즈의 10번째 글입니다.


지금까지 배운 HTTP 서버, 라우팅, 서비스, 데이터베이스, 인증, 로깅, 테스트, 배포를 실제 프로젝트 구조 안에 묶는 순간부터 코드의 성격이 달라집니다. 기능이 동작하는 것과 운영 가능한 구조를 갖추는 것은 서로 다른 문제이기 때문입니다.

이 글은 Backend Development 101 시리즈의 마지막 글입니다. 여기서는 운영 가능한 백엔드가 왜 결국 구조의 문제로 귀결되는지 정리하고, 지금까지 배운 레이어를 하나의 프로젝트에 배치하는 기준을 살펴보겠습니다.

## 먼저 던지는 질문

- 지금까지 배운 아홉 개 레이어를 하나의 프로젝트 구조로 어떻게 배치할까요?
- dev, staging, prod 설정은 어떤 방식으로 나눠야 할까요?
- observability의 세 기둥은 프로젝트 안에서 어디에 놓일까요?

## 큰 그림

![Backend Development 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/backend-development-101/10/10-01-concept-at-a-glance.ko.png)

*Backend Development 101 10장 흐름 개요*

## 왜 중요한가

좋은 구조는 새로 합류한 동료가 30분 안에 필요한 코드를 찾게 해 줍니다. 반대로 나쁜 구조는 몇 달 뒤의 자기 자신도 길을 잃게 만듭니다. 운영 가능한 코드는 대개 화려한 코드가 아니라 읽기 쉬운 구조에서 시작합니다.

결국 프로덕션 레디라는 말은 기능을 많이 붙였다는 뜻이 아니라, 책임 경계와 운영 기준이 코드 구조 안에 드러나 있다는 뜻에 가깝습니다. 이 점을 이해하면 “잘 돌아가는 코드”와 “운영 가능한 백엔드”의 차이가 선명해집니다.

> 운영 가능한 백엔드는 기능의 양보다 구조의 명확성에서 먼저 결정됩니다.

## 한눈에 보는 개념

각 화살표는 물리적인 디렉터리 경계와 맞물려야 합니다. 구조가 좋다면 요청 흐름도 파일 구조를 따라 자연스럽게 읽힙니다.

## 핵심 용어

- **Project layout**: 코드가 물리적으로 어디에 놓이는지에 대한 규칙입니다.
- **Config layering**: 환경별 설정을 덮어쓰는 전략입니다.
- **Secret manager**: secret을 코드 밖에서 관리하는 시스템입니다.
- **SLO**: 성능과 가용성에 대해 팀이 지키겠다고 약속한 수치 기준입니다.
- **Capacity plan**: 현재 트래픽의 N배를 견디기 위한 계획입니다.

## 개선 전/개선 후

**Before (everything in one file)**

```text
app.py   # routing, business, DB, auth, logging — all together
```

**After (layers visible as directories)**

```text
src/
├── api/            # routers, middleware
├── services/       # business rules
├── repositories/   # DB access
├── db/             # models, migrations
├── auth/           # authn/authz
├── observability/  # logging, metrics, tracing
├── config/         # per-environment settings
└── main.py         # wiring only
tests/
deploy/
```

레이어가 디렉터리로 드러나면 새 기능이 어느 위치에 속하는지 판단하기 쉬워집니다. 구조는 곧 코드 리뷰 기준이기도 합니다.

## 실습: 다섯 단계로 보는 운영 가능한 구조

### 단계 1 — 디렉터리 레이아웃

```bash
mkdir -p src/{api,services,repositories,db,auth,observability,config}
mkdir -p tests deploy
touch src/main.py
```

물리적 디렉터리 구조는 협업의 공통 언어입니다. 이름만 봐도 책임이 떠오르는 구조가 가장 강합니다.

### 단계 2 — 계층형 설정

```python
# src/config/settings.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env: str = "dev"
    db_url: str
    jwt_secret: str
    log_level: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
```

운영에서는 `.env` 대신 secret manager가 환경 변수를 주입하는 방식이 더 자연스럽습니다. 핵심은 설정을 코드에 넣지 않고 환경에서 주입하는 구조를 지키는 데 있습니다.

### 단계 3 — 메인 진입점은 조립만 담당

```python
# src/main.py
from fastapi import FastAPI
from src.api import users, orders
from src.observability import setup_logging, setup_metrics

def create_app() -> FastAPI:
    app = FastAPI()
    setup_logging()
    setup_metrics(app)
    app.include_router(users.router)
    app.include_router(orders.router)
    return app

app = create_app()
```

`main.py`는 배선만 담당해야 합니다. 비즈니스 로직이 이 파일에 들어오기 시작하면 테스트와 구조 모두 빠르게 무거워집니다.

### 단계 4 — 한 화면 관측성

```python
# src/observability/__init__.py
import logging, time
from prometheus_client import Counter, Histogram

REQUESTS = Counter("http_requests_total", "Total requests", ["route", "status"])
LATENCY = Histogram("http_request_seconds", "Latency", ["route"])

def setup_logging():
    logging.basicConfig(level="INFO", format="%(asctime)s %(levelname)s %(message)s")

def setup_metrics(app):
    @app.middleware("http")
    async def observe(request, call_next):
        start = time.time()
        response = await call_next(request)
        LATENCY.labels(request.url.path).observe(time.time() - start)
        REQUESTS.labels(request.url.path, response.status_code).inc()
        return response
```

로그와 메트릭은 나중에 붙이는 옵션이 아니라 처음부터 넣어 두는 운영 장치입니다. 구조에 들어 있지 않으면 실제 장애 때 붙일 시간이 없습니다.

### 단계 5 — 서비스 목표와 용량 기준선

```text
- Availability: 99.9% (43 minutes downtime per month)
- p95 latency: under 300 ms
- Error rate: under 0.1%
- 1 instance = 200 RPS (capacity baseline)
```

숫자로 적어 두어야 알람과 용량 계획이 자연스럽게 따라옵니다. “빠르게”나 “안정적으로” 같은 표현만으로는 운영 기준이 되지 못합니다.

## 검증 포인트

**Expected output:** 새 팀원이 `api`, `services`, `repositories`, `config`, `observability` 디렉터리 이름만 보고 요청 흐름을 따라갈 수 있어야 하고, `main.py`는 wiring 코드만 남아 있어야 합니다.

### 먼저 확인할 실패 지점

- `main.py`에 비즈니스 규칙이 들어가면 테스트 단위가 곧바로 무거워집니다.
- 환경별 차이를 코드 조건문으로 처리하기 시작하면 config layering을 다시 설계합니다.
- 로그와 메트릭이 나중에 붙는 구조라면 운영 준비보다 기능 추가를 먼저 선택한 신호입니다.

## 이 코드에서 먼저 볼 점

- `main.py`가 얇을수록 테스트가 쉬워집니다.
- 설정은 코드에 박아 두지 않고 환경에서 주입합니다.
- observability는 처음부터 있어야 나중에 빠르게 디버깅할 수 있습니다.

프로젝트 구조는 단순한 취향 문제가 아닙니다. 디버깅 속도, 새 팀원의 적응 속도, 리뷰 기준, 운영 안정성이 모두 여기에 영향을 받습니다.

## 자주 하는 실수 5가지

1. **레이어 경계가 조금씩 무너지는 것을 방치하는 실수**입니다. 오늘 router에 들어간 작은 SQL이 내일의 기준이 됩니다.
2. **설정을 코드에 하드코딩하는 실수**입니다. 환경별 동작 차이가 재현 불가능한 버그를 만듭니다.
3. **observability를 나중으로 미루는 실수**입니다. 사고가 나면 이미 늦습니다.
4. **SLO를 숫자로 적지 않는 실수**입니다. “빠르게”는 목표가 아닙니다.
5. **`main.py`에 비즈니스 로직을 넣는 실수**입니다. 앱 전체를 띄워야만 테스트할 수 있게 됩니다.

## 운영에서는 이렇게 드러납니다

많은 회사는 layered directory, config layering, observability 기본 설정이 baked in 된 표준 템플릿을 유지합니다. 새 서비스는 그 템플릿을 복제해 시작하고, 시니어 엔지니어는 종종 그 템플릿을 관리하는 역할까지 맡습니다.

좋은 구조의 품질은 시간이 지나야 더 잘 드러납니다. 여섯 달 뒤 새 팀원이 첫 PR을 얼마나 빨리 올리는지, 장애 때 어디를 봐야 할지 얼마나 빨리 감이 오는지가 결국 구조의 성패를 말해 줍니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 오늘보다 여섯 달 뒤에 더 편한 구조를 선택합니다.
- 새 레이어는 이름과 책임이 분명해야 합니다.
- “이 코드를 어디에 둬야 하지?”라는 질문이 자주 나오면 구조를 다시 봅니다.
- observability 없이 운영하는 것은 눈 감고 운전하는 것과 비슷합니다.
- 좋은 구조는 새 팀원의 첫 PR 속도로 측정할 수 있습니다.

## 체크리스트

- [ ] 아홉 개 레이어가 디렉터리로 드러나 있습니다.
- [ ] `main.py`는 wiring만 수행합니다.
- [ ] 설정은 환경별로 분리되어 있습니다.
- [ ] secret은 코드 안에 없습니다.
- [ ] 로그와 메트릭이 처음부터 켜져 있습니다.
- [ ] SLO가 숫자로 적혀 있습니다.

## 연습 문제

1. 가지고 있는 작은 프로젝트 하나를 위 디렉터리 구조로 재배치해 보세요.
2. `.env` 하나로 환경 변수를 주입하는 `Settings` 클래스를 만들어 보세요.
3. `/metrics` endpoint를 열고 Prometheus 형식 출력이 나오는지 확인해 보세요.

## 정리와 다음 단계

운영 가능한 백엔드는 구조에서 시작합니다. 아홉 개 레이어를 디렉터리로 분리하고, 설정과 observability를 초기에 심어 두면 몇 달 뒤의 여러분과 팀이 훨씬 편하게 코드를 다시 만날 수 있습니다.

추천하는 다음 학습 흐름은 다음과 같습니다.

- *Testing 101* — 테스트 전략을 공정처럼 설계하는 감각을 익힙니다.
- *DevOps 101* — CI/CD를 반복 가능한 자동화로 바꾸는 법을 배웁니다.
- *Observability 101* — 로그, 메트릭, 트레이스를 하나의 그림으로 연결합니다.

이 시리즈를 끝까지 따라오셨다면, 이제 작은 백엔드를 운영 가능한 구조로 끌어올리는 기본 감각은 이미 갖춘 셈입니다.


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

- **지금까지 배운 아홉 개 레이어를 하나의 프로젝트 구조로 어떻게 배치할까요?**
  - 본문의 기준은 운영 가능한 백엔드 구조를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **dev, staging, prod 설정은 어떤 방식으로 나눠야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **observability의 세 기둥은 프로젝트 안에서 어디에 놓일까요?**
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
- [Backend Development 101 (8/10): 백엔드 테스트](./08-testing-the-backend.md)
- [Backend Development 101 (9/10): 백엔드 배포](./09-deploying-the-backend.md)
- **운영 가능한 백엔드 구조 (현재 글)**

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [FastAPI Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [Prometheus Python client](https://github.com/prometheus/client_python)
- [The Twelve-Factor App](https://12factor.net/)

### 추가 읽을거리

- [backend-development-101 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/backend-development-101/ko)

- [Google SRE Book](https://sre.google/books/)

Tags: Backend, Architecture, BestPractices, Python, Production
