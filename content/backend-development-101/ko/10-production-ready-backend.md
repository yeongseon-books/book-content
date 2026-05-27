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

기능이 돌아가는 백엔드와 운영 가능한 백엔드는 같은 단계가 아닙니다. 운영 가능한 백엔드는 트래픽 증가, 장애 대응, 배포 복구를 예측 가능한 절차로 처리할 수 있어야 합니다.

이 글은 Backend Development 101 시리즈의 마지막 글입니다.

이번 글은 시리즈 1~9편에서 나눠 다뤘던 서버, 라우팅, 서비스 레이어, 데이터베이스, 인증, 로깅, 테스트, 배포를 하나의 프로덕션 구조로 묶는 캡스톤입니다. 핵심은 "기능 목록"이 아니라 "운영 성숙도"입니다. 운영 성숙도는 관측 가능성(Observable), 배포 가능성(Deployable), 테스트 가능성(Testable), 복구 가능성(Recoverable) 네 축으로 확인할 수 있습니다.

![Backend Development 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/backend-development-101/10/10-01-concept-at-a-glance.ko.png)
*Backend Development 101 10장 흐름 개요*

> 'production-ready'는 '잘 돌아간다'가 아니라 '실패해도 살아남고, 실패한 사실이 보이고, 다시 일어설 수 있다'는 세 줄의 합입니다 — health check·observability·graceful shutdown·migration·rollback이 빠진 시스템은 production이 아니라 production 흉내입니다.

## 먼저 던지는 질문

- 지금까지 배운 아홉 개 레이어를 하나의 프로젝트 구조로 어떻게 배치할까요?
- dev, staging, prod 설정은 어떤 방식으로 나눠야 할까요?
- observability의 세 기둥은 프로젝트 안에서 어디에 놓일까요?

## "Production-ready"를 기능이 아닌 운영 성숙도로 정의하기

운영 준비 상태를 기능 개수로 판단하면 거의 항상 실패합니다. 사용자 스토리가 많이 닫혀 있어도, 장애 때 원인을 찾지 못하면 서비스는 운영 불가능 상태입니다. 반대로 기능이 적어도 운영 기준이 명확하면 안전하게 확장할 수 있습니다.

아래 표는 실무에서 많이 쓰는 운영 성숙도 기준입니다.

| 축 | 질문 | 최소 기준 | 빠르게 검증하는 방법 |
|---|---|---|---|
| Observable | 장애 원인을 10분 안에 좁힐 수 있는가 | 구조화 로그, 지표, 트레이스 ID | `/metrics` 확인, 로그 샘플 조회 |
| Deployable | 근무 시간 배포가 두렵지 않은가 | 무중단 전략, 헬스체크, 롤백 경로 | 스테이징 롤링 배포 리허설 |
| Testable | 리팩터링 시 회귀를 빨리 잡는가 | 단위/통합 테스트, CI 게이트 | PR에서 테스트 자동 실행 |
| Recoverable | 실패 후 정상 상태 복귀가 빠른가 | graceful shutdown, 재시도/타임아웃 | 강제 종료 시나리오 점검 |

프로덕션 레디는 문제가 생겨도 예측 가능한 방식으로 대응할 수 있음을 뜻합니다.

## 실전 FastAPI 프로젝트 레이아웃

프로젝트 구조는 취향이 아니라 운영 절차입니다. 폴더 이름만 보고 책임 경계를 판단할 수 있어야 코드 리뷰 속도와 장애 대응 속도가 올라갑니다.

```text
backend-app/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── routers/
│   │       │   ├── users.py
│   │       │   ├── orders.py
│   │       │   └── health.py
│   │       └── __init__.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   ├── security.py
│   │   └── rate_limit.py
│   ├── db/
│   │   ├── session.py
│   │   └── base.py
│   ├── models/
│   │   ├── user.py
│   │   └── order.py
│   ├── schemas/
│   │   ├── user.py
│   │   └── order.py
│   ├── repositories/
│   │   ├── user_repository.py
│   │   └── order_repository.py
│   ├── services/
│   │   ├── user_service.py
│   │   └── order_service.py
│   ├── observability/
│   │   ├── metrics.py
│   │   └── middleware.py
│   └── __init__.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── scripts/
│   ├── run-dev.sh
│   └── smoke-test.sh
├── docs/
│   ├── runbook.md
│   └── architecture.md
├── pyproject.toml
├── .env.example
└── README.md
```

핵심은 세 가지입니다.

- `main.py`는 조립(wiring)만 담당합니다.
- `api -> services -> repositories -> db` 방향만 허용합니다.
- 테스트와 운영 스크립트를 코드와 같은 저장소에서 버전 관리합니다.

## 환경별 설정: pydantic-settings와 비밀 관리 분리

운영에서 가장 자주 반복되는 문제는 "설정이 코드에 섞여 있음"입니다. 설정은 환경에서 주입하고, 코드는 설정을 소비만 해야 합니다.

```python
# app/core/config.py
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 운영 환경
    env: str = Field(default="dev", alias="APP_ENV")
    debug: bool = Field(default=False, alias="APP_DEBUG")

    # API
    api_v1_prefix: str = "/api/v1"
    project_name: str = "backend-development-101"

    # 데이터베이스
    db_url: str = Field(alias="DATABASE_URL")
    db_pool_size: int = 10
    db_max_overflow: int = 20

    # 보안
    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"
    cors_allow_origins: list[str] = ["http://localhost:3000"]

    # 관측성
    metrics_enabled: bool = True
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

개발 환경에서는 `.env`가 편합니다. 운영 환경에서는 Vault, Secret Manager, Key Vault 같은 비밀 저장소를 통해 런타임에 주입하는 방식이 안전합니다.

| 환경 | 권장 방식 | 금지 패턴 |
|---|---|---|
| dev | `.env` + `.env.example` | 개인 PC에 평문 키 하드코딩 |
| staging | CI에서 시크릿 주입 | 스테이징 키를 코드 저장소에 커밋 |
| prod | Vault/Key Vault + IAM 권한 | SSH 접속 후 수동 편집 |

## App Factory 패턴: create_app()로 부팅 경로를 고정하기

운영 가능한 앱은 부팅 경로가 예측 가능해야 합니다. `create_app()`은 부팅 순서를 코드로 고정해 주는 패턴입니다.

```python
# app/main.py (요약)
from fastapi import FastAPI
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.observability.metrics import setup_metrics

def create_app() -> FastAPI:
    settings = get_settings()

    # 1) 로깅 먼저 초기화
    configure_logging(level=settings.log_level)

    # 2) 앱 생성
    app = FastAPI(title=settings.project_name, debug=settings.debug)

    # 3) 미들웨어/라우터/헬스체크/메트릭 순서로 등록
    setup_metrics(app)
    register_middlewares(app, settings)
    register_routers(app, settings)
    register_health_routes(app)

    # 4) 시작/종료 훅 등록
    register_lifecycle_events(app)
    return app

app = create_app()
```

## Graceful Shutdown: SIGTERM을 정상 종료 절차로 다루기

```python
# app/core/lifecycle.py
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 앱 시작
    logger.info("app.starting")
    app.state.is_draining = False

    try:
        yield
    finally:
        # 앱 종료 - 새로운 요청 차단 후 연결 정리
        logger.info("app.shutting_down")
        app.state.is_draining = True

        # DB 풀/백그라운드 태스크 정리 시간을 확보
        await asyncio.sleep(2)

        # 실제 프로젝트에서는 DB 엔진 dispose, consumer stop 등을 수행
        logger.info("app.shutdown_complete")
```

왜 중요한지 운영 시나리오로 보면 명확합니다.

- 롤링 배포 중 인스턴스가 종료되면, 드레이닝 없이 종료된 요청이 실패합니다.
- 메시지 컨슈머가 즉시 종료되면 처리 중복이나 유실이 발생할 수 있습니다.
- DB 커넥션을 반납하지 않으면 다음 인스턴스에서 풀 고갈이 빨리 옵니다.

무중단 배포는 "새 인스턴스를 빨리 띄우는 기술"이 아니라 "기존 인스턴스를 안전하게 내리는 기술"에 더 가깝습니다.

## Rate Limiting과 Throttling: 남용을 설계로 차단하기

인증이 있어도 남용은 발생합니다. 크롤러, 과도한 재시도, 버그성 클라이언트는 모두 정상 토큰으로 시스템을 압박할 수 있습니다.

슬라이딩 윈도우 패턴은 시간 구간 내 요청 수를 완만하게 제한할 때 자주 사용합니다.

```python
# app/core/rate_limit.py
import time
from collections import defaultdict, deque
from fastapi import HTTPException, Request

class SlidingWindowRateLimiter:
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self.bucket: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str) -> None:
        now = time.time()
        window_start = now - self.window_seconds
        q = self.bucket[key]

        # 윈도우 밖 요청 제거
        while q and q[0] < window_start:
            q.popleft()

        if len(q) >= self.limit:
            raise HTTPException(status_code=429, detail="Too Many Requests")

        q.append(now)

rate_limiter = SlidingWindowRateLimiter(limit=100, window_seconds=60)

def enforce_rate_limit(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    rate_limiter.check(client_ip)
```

## CORS와 보안 헤더: 브라우저 경계에서 막을 수 있는 문제

CORS는 인증 기능이 아닙니다. "어떤 웹 오리진에서 브라우저 요청을 허용할지"를 제한하는 정책입니다. 보안 헤더는 브라우저가 위험한 동작을 하지 않도록 가이드합니다.

```python
# app/core/security.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

def configure_security(app: FastAPI, allow_origins: list[str]) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-Id"],
    )
    app.add_middleware(SecurityHeadersMiddleware)
```

각 항목이 막는 대표 위험은 아래와 같습니다.

| 설정 | 막는 문제 | 설정 실수 예 |
|---|---|---|
| CORS origin 제한 | 임의 도메인의 브라우저 호출 | `allow_origins=["*"]` + credentials 허용 |
| `X-Frame-Options` | 클릭재킹 | 설정 누락 |
| HSTS | HTTPS 다운그레이드 | 운영에서만 꺼져 있음 |
| CSP | 스크립트 인젝션 노출 감소 | 너무 느슨한 `unsafe-inline` 남용 |

## DI Wiring: main.py에서 서비스 체인을 명시적으로 연결하기

"의존성 주입"은 프레임워크 매직이 아니라 책임 경계 문서화입니다. 요청마다 DB 세션을 만들고, 리포지토리를 통해 서비스를 구성한 뒤, 라우터가 서비스를 호출하도록 연결하면 테스트 대체가 쉬워집니다.

```python
# app/api/deps.py
from collections.abc import Generator
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_service(db: Session) -> UserService:
    user_repo = UserRepository(db)
    return UserService(user_repo)
```

```python
# app/api/v1/routers/users.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_user_service
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    service: UserService = get_user_service(db)
    return service.get_user_profile(user_id)
```

## 모니터링: Prometheus 메트릭을 최소 셋으로 시작하기

운영 초기에 복잡한 대시보드를 만들 필요는 없습니다. 대신 세 개를 반드시 확보합니다.

- 지연 시간(latency): 히스토그램(`http_request_duration_seconds`)
- 오류 수(error): 카운터(`http_request_errors_total`)
- 처리량(throughput): 카운터(`http_requests_total`)

```python
# app/observability/metrics.py
import time
from fastapi import FastAPI, Request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.responses import Response

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "path", "status"],
)

REQUEST_ERRORS = Counter(
    "http_request_errors_total",
    "Total number of failed HTTP requests",
    ["method", "path", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
    buckets=(0.01, 0.05, 0.1, 0.3, 0.5, 1.0, 2.0, 5.0),
)

def setup_metrics(app: FastAPI) -> None:
    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start

        method = request.method
        path = request.url.path
        status = str(response.status_code)

        REQUEST_COUNT.labels(method, path, status).inc()
        REQUEST_LATENCY.labels(method, path).observe(elapsed)
        if response.status_code >= 500:
            REQUEST_ERRORS.labels(method, path, status).inc()

        return response

    @app.get("/metrics", include_in_schema=False)
    def metrics():
        # Prometheus scrape endpoint
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

## Health Check: shallow와 deep를 분리하기

헬스체크 하나로 모든 것을 검사하면 오탐이 늘어납니다. shallow와 deep를 분리하면 운영 의도가 선명해집니다.

```python
# app/api/v1/routers/health.py
from fastapi import APIRouter
from sqlalchemy import text
from app.db.session import SessionLocal

router = APIRouter(tags=["health"])

@router.get("/health/live")
def liveness_check():
    # 프로세스가 살아 있는지만 확인
    return {"status": "alive"}

@router.get("/health/ready")
def readiness_check():
    # 핵심 의존성(DB, 캐시 등)이 준비됐는지 확인
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        # 실제 서비스에서는 cache.ping()도 함께 검사
        return {"status": "ready", "db": "ok", "cache": "ok"}
    finally:
        db.close()
```

분리 기준은 다음과 같습니다.

| 엔드포인트 | 목적 | 실패 시 조치 |
|---|---|---|
| `/health/live` | 프로세스 생존 확인 | 프로세스 재시작 판단 |
| `/health/ready` | 트래픽 수용 가능 여부 | 로드밸런서 대상 제외 |

이 구분이 없으면 "앱은 살아 있는데 준비되지 않은 상태"를 표현할 방법이 없습니다.

## 운영 시나리오로 보는 구조의 가치

### 1) 부하에서 갑자기 크래시

증상은 p95 지연 급등 뒤 500 증가입니다. 원인은 대개 DB 커넥션 풀 미설정 또는 너무 작은 풀 크기입니다.

- 교훈: `db_pool_size`, `max_overflow`, 타임아웃을 설정하지 않으면 정상 트래픽에서도 병목이 발생합니다.
- 예방: 부하 테스트를 CI 야간 작업으로 넣고, 연결 수/대기 시간을 메트릭으로 수집합니다.

### 2) 프로덕션에서 디버깅 불가

증상은 "에러가 난다" 외 정보가 없습니다. 원인은 구조화 로그 미적용, 요청 ID 누락, 에러 분류 부재입니다.

- 교훈: 문자열 로그만 남기면 사건 순서 재구성이 어렵습니다.
- 예방: JSON 로그 + `request_id`, `user_id`, `route`, `latency_ms` 공통 필드를 강제합니다.

### 3) 신규 개발자 온보딩 2일 소요

증상은 로컬 실행 실패, DB 초기화 혼선, 테스트 실행 경로 불명확입니다.

- 교훈: 코드가 아니라 문서와 스크립트가 온보딩 속도를 결정합니다.
- 예방: `README.md`에 5분 실행 절차와 `scripts/run-dev.sh` 제공, `make test` 같은 단일 진입점 유지.

### 4) 배포 후 기존 클라이언트 깨짐

증상은 모바일 구버전 앱에서 4xx 폭증입니다. 원인은 버전 없는 엔드포인트 변경입니다.

- 교훈: API 진화는 코드보다 계약 관리 문제입니다.
- 예방: `/api/v1`, `/api/v2`를 명시하고, 폐기 일정과 호환 정책을 문서화합니다.

## 캡스톤: 시리즈 1~9를 묶는 main.py 예시

아래 코드는 이 시리즈에서 다룬 핵심 요소를 한 파일에 조립한 예시입니다. 실제 서비스에서는 모듈 분리 수준이 더 높겠지만, 운영 관점을 한 번에 확인하기 위한 캡스톤으로 읽으면 됩니다.

```python
# app/main.py
import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.api.v1.routers import health, orders, users
from app.core.config import get_settings
from app.core.rate_limit import enforce_rate_limit
from app.db.session import close_engine, initialize_engine
from app.observability.metrics import setup_metrics

logger = logging.getLogger(__name__)

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 요청 단위 공통 컨텍스트 처리
        request_id = request.headers.get("X-Request-Id", "generated-request-id")
        request.state.request_id = request_id

        try:
            response = await call_next(request)
        except Exception as exc:
            logger.exception("unhandled_error", extra={"request_id": request_id})
            return JSONResponse(status_code=500, content={"detail": "internal_error"})

        response.headers["X-Request-Id"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 단계: 리소스 초기화
    settings = get_settings()
    logger.info("app.start", extra={"env": settings.env})
    initialize_engine(settings.db_url, settings.db_pool_size, settings.db_max_overflow)
    app.state.is_draining = False

    try:
        yield
    finally:
        # 종료 단계: 드레이닝 후 리소스 정리
        app.state.is_draining = True
        logger.info("app.stop.begin")
        close_engine()
        logger.info("app.stop.complete")

def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.project_name,
        debug=settings.debug,
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-Id"],
    )

    # 요청 컨텍스트/보안 헤더
    app.add_middleware(RequestContextMiddleware)

    # 관측성
    if settings.metrics_enabled:
        setup_metrics(app)

    # 공통 레이트 리밋 의존성
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        enforce_rate_limit(request)
        return await call_next(request)

    # API 버전 라우팅
    app.include_router(users.router, prefix=settings.api_v1_prefix)
    app.include_router(orders.router, prefix=settings.api_v1_prefix)
    app.include_router(health.router)

    @app.get("/")
    def root():
        return {"service": settings.project_name, "env": settings.env}

    return app

app = create_app()
```

## 프로덕션 체크리스트: 카테고리별 요구사항과 검증 방법

배포 전 체크리스트는 "할 일 목록"이 아니라 "위험 통제 목록"이어야 합니다.

| 카테고리 | 요구사항 | 검증 방법 |
|---|---|---|
| 구조 | `api/services/repositories` 경계 준수 | 아키텍처 리뷰 + import 규칙 검사 |
| 설정 | 환경별 값 주입, 시크릿 외부화 | `env` 스캔 + 배포 파이프라인 시크릿 점검 |
| 데이터베이스 | 풀/타임아웃/재시도 정책 설정 | 부하 테스트 + DB 연결 메트릭 |
| 보안 | CORS 제한, 보안 헤더, 인증 만료 정책 | 보안 스캔 + 수동 헤더 검증 |
| 관측성 | 로그/메트릭/트레이스 최소 기준 충족 | `/metrics` 수집, 로그 쿼리, 추적 샘플 |
| 헬스체크 | live/ready 분리 | 롤링 배포 중 ready 동작 확인 |
| 배포 | 무중단 배포 + 롤백 절차 | 스테이징 리허설, 실패 주입 테스트 |
| 테스트 | 단위+통합+스모크 테스트 자동화 | PR 게이트와 nightly 실행 기록 |
| 문서 | 온보딩/런북/장애 대응 절차 최신화 | 신규 인원 1명으로 따라하기 검증 |
| API 호환성 | 버전 전략과 폐기 정책 문서화 | 계약 테스트 + 구버전 클라이언트 회귀 |

## 시니어가 자주 보는 실수와 판단 기준

### 흔한 실수

- `main.py`에 비즈니스 로직을 넣어 테스트 경계를 흐립니다.
- repository를 건너뛰고 router에서 직접 ORM을 호출합니다.
- `.env`를 운영에 그대로 복사해 권한/감사 추적을 잃습니다.
- 에러 로그를 문자열로만 남겨 검색/집계를 포기합니다.
- 버전 없는 API를 수정해 기존 소비자를 깨뜨립니다.

시니어는 복잡한 코드를 선호하지 않습니다. 바뀌기 쉬운 지점과 고정해야 할 경계를 구분하는 구조를 선호합니다.

## 처음 질문으로 돌아가기

- **지금까지 배운 아홉 개 레이어를 하나의 프로젝트 구조로 어떻게 배치할까요?**
  - API(`routers`)는 입력/출력 계약만 처리하고, 서비스는 비즈니스 규칙, 리포지토리는 영속성 접근, `models/schemas`는 데이터 형태를 분리해 `api -> services -> repositories -> db` 단방향 흐름으로 고정하면 됩니다. `main.py`는 이 레이어를 조립하는 진입점으로만 유지해야 운영/테스트 경계가 무너지지 않습니다.
- **dev, staging, prod 설정은 어떤 방식으로 나눠야 할까요?**
  - `pydantic-settings`로 설정 스키마를 고정하고, dev는 `.env`, staging/prod는 CI와 Vault 계열 시크릿 주입으로 분리하면 됩니다. 코드에는 기본값과 타입만 두고, 민감 값과 환경별 값은 런타임 주입으로 관리해야 배포와 설정 변경을 분리할 수 있습니다.
- **observability의 세 기둥은 프로젝트 안에서 어디에 놓일까요?**
  - 로그는 요청 컨텍스트 미들웨어에서 공통 필드를 강제하고, 메트릭은 HTTP 미들웨어와 `/metrics` 엔드포인트에 배치하며, 트레이스는 라우터 경계에서 시작해 서비스/리포지토리 호출로 이어지게 연결하면 됩니다. 즉, 관측성은 `observability/` 폴더 하나가 아니라 요청 경로 전체를 관통하는 계약으로 설계해야 합니다.

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
