---
series: backend-development-101
episode: 9
title: "Backend Development 101 (9/10): 백엔드 배포"
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
  - Deployment
  - Docker
  - DevOps
  - Python
seo_description: Docker와 healthcheck로 백엔드를 안전하게 배포하는 기본기입니다
last_reviewed: '2026-05-15'
---

# Backend Development 101 (9/10): 백엔드 배포

이 글은 Backend Development 101 시리즈의 9번째 글입니다.


로컬에서는 잘 되던 애플리케이션이 운영에서 깨지는 이유는 코드만의 문제가 아니라 환경 차이 때문인 경우가 많습니다. 같은 코드를 어디서나 같은 방식으로 실행할 수 없다면, 배포는 언제나 사람 기억과 현장 판단에 의존하게 됩니다.

여기서는 Docker, 환경 변수, healthcheck, rolling update를 중심으로 배포를 재현성의 문제로 이해해 보겠습니다.

## 먼저 던지는 질문

- 배포 환경은 어떤 요소들로 이루어질까요?
- Dockerfile은 왜 재현 가능한 실행 환경을 만드는 핵심일까요?
- 환경 변수와 secret은 어떻게 분리해야 할까요?

## 큰 그림

![Backend Development 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/backend-development-101/09/09-01-concept-at-a-glance.ko.png)

*Backend Development 101 9장 흐름 개요*

## 왜 중요한가

배포가 두려운 일이 되는 순간 출시 빈도는 떨어집니다. 출시가 드물어질수록 한 번의 배포에 더 많은 변경이 묶이고, 위험은 오히려 커집니다. 그래서 시니어 엔지니어가 만드는 좋은 배포는 화려한 배포가 아니라 드라마가 없는 배포입니다.

배포를 안정화한다는 것은 운영 환경의 차이를 코드와 설정 안에 고정해 두는 일입니다. “내 노트북에서는 됐는데요”라는 말이 더 이상 변명이 되지 않게 만드는 과정이라고 볼 수도 있습니다.

> 배포는 코드가 아니라 환경 차이까지 함께 재현 가능하게 만드는 작업입니다.

## 한눈에 보는 개념

코드는 이미지가 되고, 이미지는 어디에서나 같은 방식으로 실행되어야 합니다. 이 재현성이 있어야 운영 문제를 환경 탓으로만 돌리지 않을 수 있습니다.

## 핵심 용어

- **Container**: 의존성을 안에 포함한 실행 단위입니다.
- **Image**: 컨테이너를 만드는 청사진입니다.
- **Registry**: 이미지를 저장하는 저장소입니다.
- **Healthcheck**: 컨테이너가 살아 있는지 runner에게 알려 주는 점검 경로입니다.
- **Rolling update**: 새 버전으로 트래픽을 점진적으로 옮기는 배포 방식입니다.

## 개선 전/개선 후

**Before (manual deploy)**

```bash
ssh server
git pull
pip install -r requirements.txt
systemctl restart app
```

**After (Dockerized — same image runs everywhere)**

```bash
docker build -t myapp:1.2.3 .
docker push registry/myapp:1.2.3
# Production pulls the same image and runs it
```

수동 배포는 사람이 기억에 의존합니다. 반면 이미지 기반 배포는 “무엇이 실행되고 있는가”를 버전으로 고정해 줍니다.

## 실습: 다섯 단계로 보는 배포

### 단계 1 — 컨테이너 이미지 명세 파일

```dockerfile
# Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Dockerfile은 런타임 환경을 코드로 고정합니다. 운영에서 쓰는 Python 버전과 의존성이 로컬과 달라질 때 생기는 문제를 크게 줄여 줍니다.

### 단계 2 — 빌드와 실행

```bash
docker build -t myapp:0.1 .
docker run -p 8000:8000 myapp:0.1
```

이미지를 한 번 만들면 어디에서나 같은 방식으로 실행할 수 있어야 합니다. 이것이 컨테이너 기반 배포의 가장 큰 장점입니다.

### 단계 3 — 환경 변수

```python
# main.py
import os
DB_URL = os.environ["DATABASE_URL"]
JWT_SECRET = os.environ["JWT_SECRET"]
```

```bash
docker run -e DATABASE_URL=postgres://... -e JWT_SECRET=... myapp:0.1
```

설정과 secret을 이미지 안에 구워 넣지 않고 바깥에서 주입해야 환경별 차이를 통제할 수 있습니다. 특히 secret은 코드와 이미지에서 분리되어야 합니다.

### 단계 4 — 헬스체크 엔드포인트

```python
# health.py
@app.get("/healthz")
def healthz():
    return {"status": "ok"}
```

In `docker-compose.yml`:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/healthz"]
  interval: 10s
  retries: 3
```

새 버전이 진짜 준비되었는지 확인하지 않고 트래픽을 보내면 죽은 인스턴스로 요청이 흘러갑니다. healthcheck는 단순 모니터링이 아니라 트래픽 제어 신호입니다.

### 단계 5 — 롤링 업데이트

```bash
# Kubernetes, ECS, Docker Swarm — same idea
# 1) deploy the new image
# 2) wait for healthcheck to pass
# 3) shift traffic gradually
# 4) remove the old version
```

새 버전이 실제로 준비됐는지 먼저 확인하고, 통과한 뒤에만 트래픽을 옮겨야 합니다. 무중단 배포는 마법이 아니라, 검증과 점진적 전환을 순서대로 밟는 운영 절차입니다.

## 검증 포인트

**Expected output:** `docker build`가 같은 Dockerfile에서 같은 이미지를 만들고, `/healthz`는 `{"status": "ok"}`를 반환하며, 새 버전은 healthcheck를 통과한 뒤에만 트래픽을 받아야 합니다.

### 먼저 확인할 실패 지점

- 컨테이너가 바로 종료되면 `CMD` 경로와 포트 바인딩부터 확인합니다.
- 이미지마다 동작이 다르면 secret이나 설정이 이미지 안에 고정된 경우가 많습니다.
- rollout 중 오류가 커지면 healthcheck 통과 전에 트래픽을 붙이고 있지 않은지 먼저 봅니다.

## 이 코드에서 먼저 볼 점

- secret은 이미지 안에 넣지 않습니다.
- `--no-cache-dir` 같은 옵션은 이미지를 더 가볍게 만듭니다.
- 애플리케이션이 스스로 healthcheck endpoint를 제공해야 합니다.

이미지가 작고, 설정이 분리되어 있고, healthcheck가 명확할수록 배포 자동화는 훨씬 예측 가능해집니다. 반대로 이 세 가지가 없으면 장애 대응도 사람 손에 의존하게 됩니다.

## 자주 하는 실수 5가지

1. **운영에서 `latest` 태그만 쓰는 실수**입니다. 어떤 버전이 살아 있는지 알기 어렵습니다.
2. **secret을 이미지에 구워 넣는 실수**입니다. 이미지가 유출되면 secret도 함께 유출됩니다.
3. **load balancer 뒤에서 healthcheck를 생략하는 실수**입니다. 죽은 인스턴스로 트래픽이 갑니다.
4. **운영 migration을 수동으로만 처리하는 실수**입니다. 배포 자동화의 의미가 약해집니다.
5. **rollback 절차를 준비하지 않는 실수**입니다. 장애 대응이 즉흥적으로 변합니다.

## 운영에서는 이렇게 드러납니다

배포가 실패하는 장면은 다양해 보여도, 원인을 분류하면 대부분 이미지, 설정, 인프라 신호 세 영역으로 정리됩니다. 이미지는 동일한데 설정이 다르면 같은 버전에서도 다른 동작이 나오고, 설정이 같아도 인프라 신호가 늦으면 정상 컨테이너가 비정상으로 판정될 수 있습니다. 그래서 배포 절차는 명령어 순서보다 검증 지점을 어디에 두는지가 더 중요합니다.

실무에서는 배포 직후 5분이 가장 중요합니다. 이 구간에서 readiness 실패율, 5xx 비율, 응답 지연 분포를 동시에 보지 않으면 문제를 늦게 발견하게 됩니다. 반대로 이 지표를 릴리스 템플릿에 고정해 두면, 담당자가 바뀌어도 같은 기준으로 이상 징후를 발견할 수 있습니다.

또 하나 자주 놓치는 부분은 롤백의 정의입니다. 단순히 이전 이미지를 다시 띄우는 것만으로는 충분하지 않습니다. 환경 변수 변경, 데이터베이스 마이그레이션, 캐시 스키마 변경이 함께 들어갔다면 되돌림 절차도 계층별로 분리돼 있어야 합니다. 배포 문서에 "무엇을 되돌리고, 무엇은 유지하는지"를 명시해 두면 야간 장애 대응에서 의사결정 속도가 크게 빨라집니다.

많은 팀은 Docker + GitHub Actions + 오케스트레이터(Kubernetes, ECS 등) 조합을 씁니다. PR이 merge되면 CI가 이미지를 만들고 registry에 push하고 배포를 진행합니다. 운영자는 명령을 직접 치기보다 시스템 상태를 관찰하는 쪽으로 역할이 이동합니다.

배포가 안정화된 팀일수록 “배포하는 법”보다 “문제 생기면 어떻게 되돌릴 것인가”를 더 분명히 문서화해 둡니다. 좋은 배포는 성공 절차뿐 아니라 실패 절차도 예측 가능해야 합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 모든 배포는 되돌릴 수 있어야 합니다.
- secret은 오직 secret manager에 둡니다.
- 이미지가 작을수록 빌드와 배포가 빨라집니다.
- migration은 이전 버전과의 호환성을 고려해 설계합니다.
- 누군가를 깨우는 배포는 그 자체로 나쁜 배포입니다.

## 체크리스트

- [ ] Dockerfile을 작성하고 이미지를 빌드할 수 있습니다.
- [ ] 설정을 환경 변수로 분리할 수 있습니다.
- [ ] `/healthz` endpoint를 추가할 수 있습니다.
- [ ] secret을 이미지 밖에 둘 수 있습니다.
- [ ] rolling update 흐름을 설명할 수 있습니다.

## 연습 문제

1. FastAPI 앱을 Dockerize하고 로컬에서 실행해 보세요.
2. `.env` 파일과 `docker run --env-file`로 설정을 분리해 보세요.
3. healthcheck를 일부러 깨뜨리고 컨테이너 상태가 어떻게 바뀌는지 확인해 보세요.

## 정리와 다음 글

배포는 재현성의 문제입니다. 마지막 글에서는 지금까지 배운 아홉 개 레이어를 하나의 운영 가능한 백엔드 구조로 묶어 보겠습니다.


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

### 객체 관계 매핑 모델과 저장소 경계를 분리하기

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

- **배포 환경은 어떤 요소들로 이루어질까요?**
  - 본문의 기준은 백엔드 배포를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Dockerfile은 왜 재현 가능한 실행 환경을 만드는 핵심일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **환경 변수와 secret은 어떻게 분리해야 할까요?**
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
- **백엔드 배포 (현재 글)**
- 운영 가능한 백엔드 구조 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Docker get-started](https://docs.docker.com/get-started/)
- [Kubernetes probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [GitHub Actions for Python](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python)

### 추가 읽을거리

- [backend-development-101 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/backend-development-101/ko)

- [The Twelve-Factor App](https://12factor.net/)

Tags: Backend, Deployment, Docker, DevOps, Python
