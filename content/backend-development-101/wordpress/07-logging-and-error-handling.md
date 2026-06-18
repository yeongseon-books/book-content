---
series: backend-development-101
episode: 7
title: "바이브코딩을 위한 백엔드 개발 기초 (7/10): Logging과 Error Handling"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - Backend
  - Logging
  - Observability
  - Python
  - ErrorHandling
seo_description: AI가 만든 백엔드에서 장애를 추적할 수 있으려면 구조화 로그와 에러 처리 설계가 필요합니다. 바이브코딩 관점에서 운영 가시성을 확보하는 방법을 설명합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 백엔드 개발 기초 (7/10): Logging과 Error Handling

이 글은 **바이브코딩을 위한 백엔드 개발 기초** 시리즈의 7번째 글입니다. AI에게 코드를 맡기기 전에 백엔드가 어떻게 동작하는지 이해해야 원하는 결과를 얻을 수 있습니다.

---

AI가 만든 서버에서 새벽 3시에 알림이 왔는데, 로그에는 `Exception occurred`만 반복된다면 장애 대응은 사실상 추측 게임이 됩니다. 바이브코딩으로 빠르게 만든 서버일수록 로깅과 에러 처리가 취약한 경우가 많습니다. `print()` 문이 로그 역할을 하고, 모든 예외가 500으로 반환되고, 어떤 요청에서 문제가 생겼는지 알 수 없습니다.

> 운영에서 로그는 '디버깅용 print'가 아니라 '미래의 나에게 보내는 증거'이고, 에러 처리는 '예외를 잡는 것'이 아니라 '실패를 비즈니스 결정으로 바꾸는 일'입니다.

## 이 글에서 다룰 문제

- 왜 `print` 대신 logger를 써야 할까요?
- 구조화 로그는 어떤 모양이어야 운영에서 쓸모가 있을까요?
- 글로벌 예외 처리는 왜 응답 일관성을 지켜 줄까요?
- AI가 만든 코드에서 로깅과 에러 처리의 어떤 문제를 먼저 수정해야 할까요?
- 바이브코딩 프로젝트에서 최소한으로 갖춰야 할 관측 설계는 무엇일까요?

## 바이브코딩과 관측 가능성: AI가 자주 만드는 문제

AI가 만든 코드에서 로깅과 에러 처리의 전형적인 문제들:

- `print()` 또는 `logging.info("message")` 같은 비구조화 로그
- 모든 예외를 `except Exception: pass`로 삼키거나 500으로 반환
- request_id 없이 어떤 요청에서 에러가 났는지 추적 불가
- 도메인 에러(재고 부족)와 인프라 에러(DB 장애)를 같은 방식으로 처리
- 에러 응답 포맷이 엔드포인트마다 다름

## 구조화 로그: JSON이어야 하는 이유

문자열 로그는 사람이 읽기 편하지만 시스템이 처리하기 어렵습니다. JSON 로그는 검색, 필터링, 알림에서 차원이 다릅니다.

```json
{
  "timestamp": "2026-06-18T03:11:22.441Z",
  "level": "ERROR",
  "event": "payment_failed",
  "request_id": "f9f99af8-2f0e-4b61-b66f-a7f1cd3cd9af",
  "user_id": 42,
  "order_id": "ord_9A12",
  "error_code": "PAYMENT_PROVIDER_TIMEOUT",
  "duration_ms": 1734
}
```

이 구조에서 `level=ERROR AND error_code=PAYMENT_PROVIDER_TIMEOUT` 같은 쿼리와 임계치 알림 설정이 가능합니다.

```python
import structlog

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.JSONRenderer(),
    ],
)

log = structlog.get_logger("app")
log.info("order_created", order_id="ord_9A12", user_id=42)
```

## Request ID: 요청 추적의 핵심

모든 로그에 request_id가 없으면 에러가 났을 때 어떤 요청에서 시작됐는지 알 수 없습니다.

```python
import time
import uuid
from fastapi import FastAPI, Request
import structlog

app = FastAPI()
log = structlog.get_logger("api")

@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    started = time.perf_counter()

    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

    # 요청 단위 컨텍스트 자동 바인딩
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        endpoint=request.url.path,
        method=request.method,
    )

    response = await call_next(request)
    duration_ms = int((time.perf_counter() - started) * 1000)
    log.info("request_completed", status_code=response.status_code, duration_ms=duration_ms)

    response.headers["X-Request-ID"] = request_id
    return response
```

이제 모든 로그 라인에 request_id가 자동으로 붙습니다. 에러 보고를 받았을 때 request_id로 전체 흐름을 추적할 수 있습니다.

## 글로벌 예외 처리: 에러를 응답으로 번역하는 경계

AI가 만든 코드에서 예외 처리가 없으면 FastAPI가 기본 500을 반환합니다. 글로벌 예외 처리기를 추가하면 모든 에러를 일관된 포맷으로 반환할 수 있습니다.

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import structlog

app = FastAPI()
log = structlog.get_logger("api")

@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    request_id = request.headers.get("X-Request-ID", "unknown")
    log.info("validation_error", errors=exc.errors())
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "code": "VALIDATION_ERROR",
            "detail": "입력값이 유효하지 않습니다.",
            "request_id": request_id,
        },
    )

@app.exception_handler(Exception)
async def unhandled_handler(request: Request, exc: Exception):
    request_id = request.headers.get("X-Request-ID", "unknown")
    log.exception("unhandled_exception")  # stack trace 포함
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "code": "INTERNAL_SERVER_ERROR",
            "detail": "일시적인 오류가 발생했습니다.",
            "request_id": request_id,
        },
    )
```

## 도메인 에러와 인프라 에러 분리

도메인 에러(비즈니스 규칙 위반)와 인프라 에러(DB 장애, 외부 API 실패)는 성격이 다릅니다. 같은 방식으로 처리하면 사용자에게 잘못된 메시지를 주거나 보안 정보가 노출됩니다.

```python
class DomainError(Exception):
    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail

class InfrastructureError(Exception):
    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail

# service에서
def create_order(command):
    if command.quantity <= 0:
        raise DomainError("INVALID_QUANTITY", "수량은 1 이상이어야 합니다.")

    try:
        save_to_db(command)
    except TimeoutError as exc:
        raise InfrastructureError("DB_TIMEOUT", "데이터 저장에 실패했습니다.") from exc

# controller에서
@app.post("/orders")
async def create_order_endpoint(payload: dict, request: Request):
    request_id = request.headers.get("X-Request-ID", "unknown")
    try:
        create_order(payload)
        return {"result": "ok"}
    except DomainError as exc:
        # 사용자에게 수정 가능한 피드백
        return JSONResponse(status_code=400, content={"code": exc.code, "detail": exc.detail, "request_id": request_id})
    except InfrastructureError as exc:
        log.error("infra_error", code=exc.code)
        # 내부 원인은 감추고 안전한 메시지 반환
        return JSONResponse(status_code=503, content={"code": exc.code, "detail": "잠시 후 다시 시도해 주세요.", "request_id": request_id})
```

## Before/After: 로깅 개선

### Before: print 기반 비구조화 로그

```python
@app.post("/orders")
def create_order(payload: dict):
    try:
        order = service.create(payload)
        print("order created:", order["id"])  # 검색 불가
        return order
    except Exception as e:
        print("error:", e)  # 컨텍스트 없음
        return {"error": "failed"}, 500
```

### After: 구조화 로그 + 에러 처리

```python
@app.post("/orders", status_code=201)
def create_order(payload: CreateOrderRequest, request: Request):
    try:
        order = service.create(payload)
        log.info("order_created", order_id=order["id"])  # 구조화
        return order
    except DomainError as exc:
        log.warning("domain_error", code=exc.code)
        raise HTTPException(status_code=400, detail=exc.detail)
    except Exception:
        log.exception("unexpected_error")  # stack trace 포함
        raise HTTPException(status_code=500, detail="일시적인 오류입니다.")
```

## AI가 만든 로깅/에러 코드에서 자주 하는 실수

| 실수 | 왜 위험한가 | AI에게 수정 요청 방법 |
| --- | --- | --- |
| print()로 로그 남기기 | 검색/집계/알림 불가 | "structlog 또는 python-json-logger로 JSON 구조화 로그를 사용해줘" |
| 예외를 잡고 로그 없이 삼키기 | 실패 신호가 관측 계층으로 전달 안 됨 | "예외를 잡을 때 반드시 log.exception()을 호출해줘" |
| 모든 실패를 500 하나로 처리 | 클라이언트 재시도/안내/운영 대응이 모두 비효율적 | "DomainError는 400, InfrastructureError는 503으로 분리해줘" |
| request_id 없음 | 요청 추적 불가 | "미들웨어에서 request_id를 생성하고 모든 로그에 포함시켜줘" |
| 에러 응답에 내부 스택 노출 | 보안 사고 위험 | "에러 응답의 detail에는 안전한 메시지만 담고, 상세 내용은 로그에만 기록해줘" |

## AI 팁: 로깅/에러 처리를 AI에게 요청하는 방법

**구조화 로그**: "structlog를 사용해서 JSON 포맷으로 로그를 남겨줘. 모든 로그에 request_id, endpoint, method를 포함해줘."

**글로벌 에러 처리**: "FastAPI에 글로벌 예외 핸들러를 추가해줘. ValidationError, HTTPException, 그 외 예외를 각각 처리하도록 해줘."

**에러 분류**: "비즈니스 규칙 위반은 DomainError, 외부 의존성 실패는 InfrastructureError로 구분해줘. controller에서 HTTP 상태 코드로 번역해줘."

## 체크리스트

- [ ] print()와 logger의 차이를 설명할 수 있습니다.
- [ ] JSON 구조화 로그가 필요한 이유를 말할 수 있습니다.
- [ ] request_id의 역할과 구현 방법을 설명할 수 있습니다.
- [ ] DomainError와 InfrastructureError를 분리해야 하는 이유를 말할 수 있습니다.
- [ ] AI가 만든 코드에서 print() 기반 로그와 예외를 삼키는 패턴을 발견할 수 있습니다.

## 처음 질문으로 돌아가기

- **왜 `print` 대신 logger를 써야 할까요?**
  - logger는 레벨, 타임스탬프, 컨텍스트(request_id, user_id)를 자동으로 포함합니다. JSON 포맷으로 남기면 검색, 집계, 알림 시스템과 연동할 수 있습니다. print는 이 모든 것이 불가능합니다.
- **구조화 로그는 어떤 모양이어야 운영에서 쓸모가 있을까요?**
  - 최소한 timestamp, level, event, request_id, endpoint, duration_ms 필드가 있어야 합니다. 이 필드들을 기준으로 에러를 필터링하고 알림을 설정할 수 있습니다.
- **글로벌 예외 처리는 왜 응답 일관성을 지켜 줄까요?**
  - 글로벌 핸들러가 없으면 엔드포인트마다 에러 응답 포맷이 달라집니다. 클라이언트가 에러를 파싱하기 어렵고, 모니터링 도구가 에러를 제대로 집계할 수 없습니다.

## 정리

AI가 만든 백엔드에서 운영 문제가 생기면 로그가 없거나 구조화되지 않아서 원인을 찾기 어려운 경우가 많습니다. structlog로 JSON 로그를 남기고, request_id를 미들웨어로 자동 주입하고, 글로벌 예외 핸들러로 에러를 일관되게 처리하는 설계를 AI에게 명시적으로 요청하면 운영 가능한 서버를 만들 수 있습니다.

## 참고 자료

### 공식 문서

- [Python logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [FastAPI exception handlers](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [Twelve-Factor logs](https://12factor.net/logs)

### 추가 읽을거리

- [backend-development-101 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/backend-development-101/ko)
- [structlog docs](https://www.structlog.org/en/stable/)

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 백엔드 개발 기초 (1/10): 백엔드 개발이란 무엇인가?](./01-what-is-backend-development.md)
- [바이브코딩을 위한 백엔드 개발 기초 (2/10): HTTP 서버 만들기](./02-building-an-http-server.md)
- [바이브코딩을 위한 백엔드 개발 기초 (3/10): Routing과 Controller](./03-routing-and-controllers.md)
- [바이브코딩을 위한 백엔드 개발 기초 (4/10): Service Layer](./04-service-layer.md)
- [바이브코딩을 위한 백엔드 개발 기초 (5/10): Database Layer](./05-database-layer.md)
- [바이브코딩을 위한 백엔드 개발 기초 (6/10): 인증과 권한](./06-auth-and-authorization.md)
- **바이브코딩을 위한 백엔드 개발 기초 (7/10): Logging과 Error Handling (현재 글)**
- [바이브코딩을 위한 백엔드 개발 기초 (8/10): 백엔드 테스트](./08-testing-the-backend.md)
- [바이브코딩을 위한 백엔드 개발 기초 (9/10): 백엔드 배포](./09-deploying-the-backend.md)
- [바이브코딩을 위한 백엔드 개발 기초 (10/10): 운영 가능한 백엔드 구조](./10-production-ready-backend.md)

<!-- toc:end -->

Tags: 바이브코딩, Backend, Logging, Observability, Python, ErrorHandling
