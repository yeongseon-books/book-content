---
series: backend-development-101
episode: 5
title: "Backend Development 101 (5/10): Database Layer"
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
  - Database
  - SQL
  - SQLAlchemy
  - Python
seo_description: Repository 패턴과 트랜잭션, migration, N+1 핵심을 정리합니다
last_reviewed: '2026-05-15'
---

# Backend Development 101 (5/10): Database Layer

이 글은 Backend Development 101 시리즈의 5번째 글입니다.


service가 직접 SQL을 쓰기 시작하면 쿼리 중복과 데이터 접근 규칙의 분산이 빠르게 커집니다. 처음에는 편해 보여도 성능 조정, 캐시 추가, 테스트 격리 같은 작업이 모두 어려워집니다.

이 글은 Backend Development 101 시리즈의 다섯 번째 글입니다. 여기서는 repository pattern을 중심으로 database layer를 분리하고, ORM·migration·transaction·N+1까지 함께 정리해 보겠습니다.

## 먼저 던지는 질문

- 왜 service가 SQL을 직접 작성하지 않는 편이 좋을까요?
- repository pattern은 어떤 경계를 만들어 줄까요?
- ORM은 왜 편리하면서도 함정을 함께 가져올까요?

## 큰 그림

![Backend Development 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/backend-development-101/05/05-01-concept-at-a-glance.ko.png)

*Backend Development 101 5장 흐름 개요*

## 왜 중요한가

데이터베이스는 가장 자주 바뀌는 것 같지만, 실제로는 가장 조심스럽게 바꿔야 하는 영역입니다. 처음부터 레이어를 분리해 두면 데이터베이스를 바꾸거나 캐시를 끼우거나 테스트용 인메모리 엔진으로 교체하는 작업이 한곳에서 정리됩니다.

repository는 데이터베이스와 service 사이의 번역기 역할을 합니다. service는 도메인 언어로 말하고, repository는 그것을 SQL이나 ORM 호출로 바꿉니다. 이 경계가 있어야 시스템이 진화해도 나머지 층이 덜 흔들립니다.

> repository는 service의 도메인 언어를 데이터베이스 질의로 번역하는 경계입니다.

## 한눈에 보는 개념

service는 SQL을 몰라도 되고, repository만 데이터 접근 세부 구현을 알면 됩니다. 이 단순한 분리가 데이터 계층을 교체 가능한 형태로 만들어 줍니다.

## 핵심 용어

- **Repository**: 데이터베이스 접근을 함수 같은 메서드로 감싸는 객체입니다.
- **ORM**: 객체와 테이블을 연결해 주는 도구입니다.
- **Migration**: 스키마 변경을 코드로 버전 관리하는 방식입니다.
- **Transaction**: 함께 commit되거나 rollback되는 작업 단위입니다.
- **N+1**: 하나의 조회 뒤에 자식 데이터를 위해 N개의 쿼리가 더 나가는 대표적인 성능 함정입니다.

## 개선 전/개선 후

**Before (서비스 안에 SQL 직접 작성)**

```python
def create_user(name):
    cur = db.execute("INSERT INTO users(name) VALUES(?)", (name,))
    return cur.lastrowid
```

**After (리포지터리로 감싸기)**

```python
# repositories/user_repo.py
class UserRepository:
    def __init__(self, session):
        self.session = session

    def save(self, user):
        self.session.add(user)
        self.session.flush()
        return user
```

쿼리 변경은 이제 한 파일 안에서 끝납니다. service는 저장 방식이 바뀌어도 의미 있는 메서드만 계속 호출하면 됩니다.

## 실습: 다섯 단계로 보는 데이터베이스 계층

### 단계 1 — 경량 데이터베이스와 ORM 준비

```python
# 1_setup.py
from sqlalchemy import create_engine, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase): pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))

engine = create_engine("sqlite:///app.db")
Base.metadata.create_all(engine)
```

ORM을 쓰면 테이블과 객체 사이의 대응을 코드로 관리할 수 있습니다. 입문 단계에서는 SQL을 전혀 안 보게 만드는 도구가 아니라, 데이터 계층을 정리하는 도구로 이해하는 편이 좋습니다.

### 단계 2 — 세션과 저장소

```python
# 2_repo.py
from sqlalchemy.orm import Session

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, name: str) -> User:
        u = User(name=name)
        self.session.add(u)
        self.session.flush()
        return u

    def get(self, uid: int) -> User | None:
        return self.session.get(User, uid)
```

repository는 session을 받아 필요한 쿼리만 수행합니다. service는 add, get 같은 도메인 의미를 가진 메서드만 알면 됩니다.

### 단계 3 — 트랜잭션

```python
# 3_tx.py
from sqlalchemy.orm import Session
with Session(engine) as s, s.begin():
    repo = UserRepository(s)
    repo.add("Alice")
    repo.add("Bob")
# Exiting cleanly commits; an exception rolls back.
```

트랜잭션은 데이터 일관성을 지키는 마지막 안전장치입니다. 정상 종료되면 commit되고, 중간에 예외가 나면 rollback된다는 흐름을 몸에 익혀야 합니다.

### 단계 4 — 마이그레이션

```bash
pip install alembic
alembic init migrations
alembic revision --autogenerate -m "add users"
alembic upgrade head
```

스키마 변경을 버전 관리하지 않으면 환경마다 상태가 달라지기 쉽습니다. migration은 “지금 DB가 어떤 상태여야 하는가”를 코드로 남기는 장치입니다.

### 단계 5 — 반복 조회 문제 제거

```python
# 5_eager.py
from sqlalchemy.orm import selectinload
stmt = select(Order).options(selectinload(Order.items))
orders = session.scalars(stmt).all()
```

자식 데이터를 한 번에 가져오면 N+1 문제를 피할 수 있습니다. ORM을 쓸 때 가장 자주 만나는 성능 함정 중 하나라서 초기에 꼭 감을 잡아 두는 편이 좋습니다.

## 검증 포인트

**Expected output:** `Base.metadata.create_all(engine)` 뒤에는 `users` 테이블이 생기고, transaction 블록 안의 두 `add()` 호출은 예외가 없을 때만 함께 commit되어야 합니다.

### 먼저 확인할 실패 지점

- 같은 요청에서 session을 오래 붙잡고 있으면 연결 누수와 lock 경합이 생기기 쉽습니다.
- migration 없이 수동으로 스키마를 바꾸면 환경 간 drift가 바로 시작됩니다.
- 목록 조회가 갑자기 느려지면 eager loading 없이 relation을 반복 조회하고 있지 않은지 먼저 봅니다.

## 이 코드에서 먼저 볼 점

- session은 보통 요청 단위로 짧게 유지합니다.
- repository는 raw dict보다 도메인 객체를 반환하는 편이 자연스럽습니다.
- migration은 직접 `ALTER TABLE` 하는 것보다 훨씬 안전합니다.

이 세 가지 원칙을 지키면 database layer가 예측 가능해집니다. 반대로 session을 길게 잡거나, 쿼리를 여기저기 흩뿌리거나, 운영 DB를 수동으로 수정하기 시작하면 문제는 조용히 쌓입니다.

## 자주 하는 실수 5가지

1. **ORM 객체를 그대로 클라이언트에 반환하는 실수**입니다. Pydantic DTO 같은 별도 응답 모델이 더 안전합니다.
2. **session을 전역으로 공유하는 실수**입니다. 동시성 버그가 따라옵니다.
3. **운영 스키마를 손으로 고치는 실수**입니다. 환경이 서로 다른 방향으로 드리프트합니다.
4. **모든 relation을 lazy loading으로만 두는 실수**입니다. N+1이 조용히 커집니다.
5. **테스트에서 실제 DB만 사용하는 실수**입니다. 속도가 느려지고 반복 실행이 어려워집니다.

## 운영에서는 이렇게 드러납니다

많은 백엔드는 PostgreSQL + ORM + Alembic + Repository 조합으로 시작합니다. 트래픽이 커지면 read replica, Redis, Elasticsearch 같은 요소가 추가되지만, service는 거의 그대로 유지되고 repository 내부만 바뀌는 경우가 많습니다.

바로 그 진화 가능성이 repository 경계의 가치입니다. 데이터 접근이 한곳에 모여 있어야 성능 최적화도, 저장소 교체도, 테스트 전략도 통제할 수 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 모든 쿼리는 인덱스 관점에서도 확인합니다.
- 모든 migration에는 되돌리는 경로도 함께 고민합니다.
- repository 메서드는 도메인 언어로 말해야 합니다.
- 트랜잭션은 가능한 짧게 유지합니다.
- 운영에서는 slow query log를 항상 켜 둡니다.

## 체크리스트

- [ ] SQL을 repository 뒤로 숨길 수 있습니다.
- [ ] 트랜잭션 블록을 작성할 수 있습니다.
- [ ] Alembic migration을 만들 수 있습니다.
- [ ] N+1 문제를 알아보고 eager loading으로 줄일 수 있습니다.
- [ ] DTO와 ORM 객체의 차이를 설명할 수 있습니다.

## 연습 문제

1. `OrderRepository.find_recent(limit=10)`을 구현하고 인덱스를 점검해 보세요.
2. `users.email` 컬럼을 추가하는 Alembic migration을 만들어 보세요.
3. 의도적으로 N+1 쿼리를 만든 뒤 `selectinload` 적용 전후 차이를 측정해 보세요.

## 정리와 다음 글

repository는 데이터베이스 위에 놓인 번역기입니다. 다음 글에서는 누가 무엇을 볼 수 있는지 결정하는 인증과 권한 문제로 넘어가겠습니다.


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

- **왜 service가 SQL을 직접 작성하지 않는 편이 좋을까요?**
  - 본문의 기준은 Database Layer를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **repository pattern은 어떤 경계를 만들어 줄까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **ORM은 왜 편리하면서도 함정을 함께 가져올까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Backend Development 101 (1/10): 백엔드 개발이란 무엇인가?](./01-what-is-backend-development.md)
- [Backend Development 101 (2/10): HTTP 서버 만들기](./02-building-an-http-server.md)
- [Backend Development 101 (3/10): Routing과 Controller](./03-routing-and-controllers.md)
- [Backend Development 101 (4/10): Service Layer](./04-service-layer.md)
- **Database Layer (현재 글)**
- 인증과 권한 (예정)
- Logging과 Error Handling (예정)
- 백엔드 테스트 (예정)
- 백엔드 배포 (예정)
- 운영 가능한 백엔드 구조 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [SQLAlchemy relationship loading techniques](https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html)

### 추가 읽을거리

- [backend-development-101 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/backend-development-101/ko)

- [Repository pattern (Martin Fowler)](https://martinfowler.com/eaaCatalog/repository.html)

Tags: Backend, Database, SQL, SQLAlchemy, Python
