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

## Before/After

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

### Step 1 — Directory layout

```bash
mkdir -p src/{api,services,repositories,db,auth,observability,config}
mkdir -p tests deploy
touch src/main.py
```

물리적 디렉터리 구조는 협업의 공통 언어입니다. 이름만 봐도 책임이 떠오르는 구조가 가장 강합니다.

### Step 2 — Layered configuration

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

### Step 3 — main.py is wiring only

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

### Step 4 — Observability on one page

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

### Step 5 — SLO and capacity baseline

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

- [Google SRE Book](https://sre.google/books/)

Tags: Backend, Architecture, BestPractices, Python, Production
