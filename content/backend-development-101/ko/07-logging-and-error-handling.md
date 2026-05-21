---
series: backend-development-101
episode: 7
title: "Backend Development 101 (7/10): Logging과 Error Handling"
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
  - Logging
  - Observability
  - Python
  - ErrorHandling
seo_description: 구조화 로그와 글로벌 예외 처리를 통해 백엔드 운영 가시성을 확보하고, 장애 발생 시 원인을 빠르게 추적하는 방법을 익힙니다.
last_reviewed: '2026-05-15'
---

# Backend Development 101 (7/10): Logging과 Error Handling

이 글은 Backend Development 101 시리즈의 7번째 글입니다.


새벽에 장애 알림이 왔을 때 코드를 처음부터 다시 읽는 것만으로는 원인을 빨리 찾기 어렵습니다. 운영에서 중요한 것은 실패를 다시 실행하는 능력보다, 이미 일어난 요청을 로그와 오류 응답만으로 설명하는 능력입니다.

이 글은 Backend Development 101 시리즈의 일곱 번째 글입니다. 여기서는 구조화 로그, request_id, 글로벌 예외 처리라는 세 가지 축을 중심으로 운영에서 읽히는 백엔드를 만드는 방법을 정리해 보겠습니다.


![Backend Development 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/backend-development-101/07/07-01-concept-at-a-glance.ko.png)
*Backend Development 101 7장 흐름 개요*

## 먼저 던지는 질문

- 왜 `print` 대신 logger를 써야 할까요?
- 구조화 로그는 어떤 모양이어야 운영에서 쓸모가 있을까요?
- 글로벌 예외 처리는 왜 응답 일관성을 지켜 줄까요?

## 왜 중요한가

코드는 한 번 작성하고 수년 동안 운영합니다. 운영의 대부분은 새로운 코드를 쓰는 일이 아니라, 이미 돌아가는 시스템의 상태를 읽는 일입니다. 그때 가장 자주 읽는 것이 로그입니다.

처음부터 구조화 로그를 남겨 두면 장애 대응 시간은 체감상 차원이 다르게 줄어듭니다. 반대로 `print` 조각과 일관성 없는 에러 응답만 쌓이면, 실제 장애보다 로그 해석에 더 많은 시간을 쓰게 됩니다.

> 좋은 운영은 결국 로그를 읽어 원인을 설명할 수 있는 구조에서 시작합니다.

## 한눈에 보는 개념

정상 경로든 오류 경로든 결국 모두 로그로 모입니다. 운영 가능한 시스템은 이 흐름이 일관되게 설계되어 있습니다.

## 핵심 용어

- **Logger**: 로그 레코드를 내보내는 객체입니다.
- **Log level**: DEBUG / INFO / WARNING / ERROR / CRITICAL 같은 심각도 구분입니다.
- **Structured log**: 보통 JSON처럼 기계가 읽기 쉬운 형식의 로그입니다.
- **request_id**: 하나의 요청을 모든 레이어에서 추적하기 위한 식별자입니다.
- **Global exception handler**: 예외를 응답으로 바꾸는 단일 진입점입니다.

## 개선 전/개선 후

**Before (print 디버깅)**

```python
print("user=", user_id, "error", e)
```

**After (구조화된 로그)**

```python
import logging, json
log = logging.getLogger("app")

log.error(json.dumps({
    "event": "order_failed",
    "user_id": user_id,
    "error": str(e),
}))
```

`event` 같은 필드 하나만 있어도 집계와 검색이 훨씬 쉬워집니다. 운영에서 중요한 것은 사람이 한 줄씩 읽는 편의보다, 시스템이 대량 로그를 묶어 해석할 수 있느냐입니다.

## 실습: 다섯 단계로 보는 로그와 예외 처리

### 단계 1 — 표준 로거 설정

```python
# 1_setup.py
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
)
log = logging.getLogger("app")
log.info("server started")
```

표준 logger 설정만 잘해도 print보다 훨씬 나은 출발점이 됩니다. 최소한 시간, 레벨, 로거 이름 정도는 항상 남겨야 합니다.

### 단계 2 — 구조화 로그

```python
# 2_json_log.py
import logging, json, sys
class JsonFmt(logging.Formatter):
    def format(self, r):
        return json.dumps({"level": r.levelname, "msg": r.getMessage()})
h = logging.StreamHandler(sys.stdout)
h.setFormatter(JsonFmt())
logging.basicConfig(handlers=[h], level=logging.INFO)
logging.info("hello")
```

구조화 로그는 한 줄짜리 JSON이어야 검색과 집계가 쉬워집니다. 사람이 보기에 예쁘지 않아도 운영에서는 이 형식이 훨씬 강합니다.

### 단계 3 — 요청 식별자 미들웨어

```python
# 3_request_id.py
from fastapi import FastAPI, Request
import uuid, logging

app = FastAPI()
log = logging.getLogger("app")

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    rid = str(uuid.uuid4())
    request.state.rid = rid
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    log.info(f"req rid={rid} path={request.url.path}")
    return response
```

request_id가 있으면 하나의 요청이 router, service, repository, 외부 API 호출을 어떻게 통과했는지 끝까지 따라갈 수 있습니다. 운영에서는 이 식별자 하나가 디버깅 시간을 크게 줄입니다.

### 단계 4 — 전역 예외 처리기

```python
# 4_global_handler.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

class DomainError(Exception):
    def __init__(self, code: str, message: str):
        self.code, self.message = code, message

@app.exception_handler(DomainError)
async def handle_domain(_: Request, exc: DomainError):
    return JSONResponse(
        status_code=400,
        content={"code": exc.code, "message": exc.message},
    )
```

예외를 한곳에서 응답으로 바꾸면 클라이언트가 항상 같은 형태의 오류 응답을 받게 됩니다. 운영자 입장에서도 어떤 종류의 실패인지 더 빠르게 읽을 수 있습니다.

### 단계 5 — 로그 레벨 선택

```python
# 5_levels.py
log.debug("trace data")
log.info("user logged in")
log.warning("retrying upstream call")
log.error("payment failed")
log.critical("database is down")
```

모든 것을 ERROR로 찍으면 알람은 금방 소음이 됩니다. 레벨은 중요도의 차이를 전달하기 위해 존재합니다.

## 검증 포인트

**Expected output:** 같은 요청에서 남은 로그 라인은 모두 같은 `request_id`를 가져야 하고, `DomainError`는 일관된 JSON 오류 응답으로 바뀌어야 합니다.

### 먼저 확인할 실패 지점

- 로그를 검색하기 어렵다면 한 줄 JSON 형식이 깨졌는지 먼저 봅니다.
- `request_id`가 응답 헤더에 없으면 middleware에서 response에 넣는 부분을 확인합니다.
- stack trace가 전혀 남지 않으면 예외를 잡고 버리고 있지 않은지 점검합니다.

## 이 코드에서 먼저 볼 점

- 로그 한 줄은 한 줄로 끝나야 검색이 잘 됩니다.
- 모든 로그에 request_id가 들어가야 추적이 가능합니다.
- domain error는 안정적인 코드로 비즈니스 의미를 담아야 합니다.

특히 domain error와 infra error를 구분하는 감각이 중요합니다. 비즈니스 규칙 위반과 데이터베이스 장애는 전혀 다른 문제이기 때문입니다.

## 자주 하는 실수 5가지

1. **print 디버깅에 머무는 실수**입니다. 운영 환경에서는 print가 사라지거나 맥락 없이 흩어집니다.
2. **모든 로그를 ERROR로 남기는 실수**입니다. 알람 피로도만 높아지고 진짜 장애를 놓칩니다.
3. **비밀번호나 토큰을 로그에 남기는 실수**입니다. 즉시 보안 사고가 됩니다.
4. **예외를 모두 잡고 무시하는 실수**입니다. 오류가 조용히 사라집니다.
5. **stack trace를 버리고 메시지만 남기는 실수**입니다. 디버깅이 추측 게임이 됩니다.

## 운영에서는 이렇게 드러납니다

운영 로그는 보통 CloudWatch, Loki, Datadog 같은 수집기로 흘러갑니다. 이때 `event=order_failed` 같은 필드는 곧바로 대시보드와 알람의 기준이 됩니다. 구조화 로그를 초기에 도입하면 관측성의 절반은 이미 준비된 셈입니다.

좋은 운영 팀은 코드보다 로그를 먼저 믿습니다. 왜 실패했는지, 어디서 느려졌는지, 어떤 요청이 문제였는지를 로그만으로 상당 부분 답할 수 있어야 하기 때문입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 로그는 사람이 읽는 메모가 아니라 집계 가능한 데이터입니다.
- request_id는 응답 헤더에도 항상 되돌려줍니다.
- domain error와 infra error를 분리합니다.
- 누군가를 깨우는 로그는 반드시 행동 가능한 정보여야 합니다.
- “왜 실패했는가”를 로그만으로 설명할 수 있어야 합니다.

## 체크리스트

- [ ] 표준 logger를 설정할 수 있습니다.
- [ ] JSON 구조화 로그를 남길 수 있습니다.
- [ ] request_id middleware를 작성할 수 있습니다.
- [ ] 글로벌 예외 처리기를 등록할 수 있습니다.
- [ ] 의도를 가지고 로그 레벨을 고를 수 있습니다.

## 연습 문제

1. 모든 JSON 로그 라인에 request_id가 자동으로 들어가도록 만들어 보세요.
2. `DomainError`와 `InfraError`를 분리해 각각 다르게 처리해 보세요.
3. route에 가짜 예외를 넣고 stack trace가 로그에 남는지 확인해 보세요.

## 정리와 다음 글

좋은 로그와 일관된 예외 처리는 운영의 눈입니다. 다음 글에서는 백엔드를 안전하게 바꿀 수 있게 해 주는 테스트 전략을 살펴보겠습니다.


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

- **왜 `print` 대신 logger를 써야 할까요?**
  - 본문의 기준은 Logging과 Error Handling를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **구조화 로그는 어떤 모양이어야 운영에서 쓸모가 있을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **글로벌 예외 처리는 왜 응답 일관성을 지켜 줄까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Backend Development 101 (1/10): 백엔드 개발이란 무엇인가?](./01-what-is-backend-development.md)
- [Backend Development 101 (2/10): HTTP 서버 만들기](./02-building-an-http-server.md)
- [Backend Development 101 (3/10): Routing과 Controller](./03-routing-and-controllers.md)
- [Backend Development 101 (4/10): Service Layer](./04-service-layer.md)
- [Backend Development 101 (5/10): Database Layer](./05-database-layer.md)
- [Backend Development 101 (6/10): 인증과 권한](./06-auth-and-authorization.md)
- **Logging과 Error Handling (현재 글)**
- 백엔드 테스트 (예정)
- 백엔드 배포 (예정)
- 운영 가능한 백엔드 구조 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Python logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [FastAPI exception handlers](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [Twelve-Factor logs](https://12factor.net/logs)

### 추가 읽을거리

- [backend-development-101 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/backend-development-101/ko)

- [structlog docs](https://www.structlog.org/en/stable/)

Tags: Backend, Logging, Observability, Python, ErrorHandling
