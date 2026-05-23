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

새벽 3시에 on-call 알림이 울렸는데, 알림 제목이 `500 error spike` 한 줄뿐이고 로그에는 `Exception occurred`만 반복된다면 장애 대응은 사실상 추측 게임이 됩니다. 반대로 요청 단위 식별자, 일관된 에러 코드, 구조화된 로그 필드가 갖춰진 시스템에서는 같은 장애를 훨씬 짧은 시간 안에 설명할 수 있습니다. 운영에서 중요한 능력은 에러를 "없애는" 능력보다 에러를 "관측 가능한 신호"로 바꾸는 능력입니다.

이 글에서는 운영 관측성 관점에서 Logging과 Error Handling을 하나의 설계 문제로 다룹니다. JSON 구조화 로그, 로그 레벨 정책, request ID/correlation ID, FastAPI 글로벌 예외 처리기, 도메인 예외와 인프라 예외 분리, 응답 스키마 표준화, 로그 보존/로테이션, 알림 기준, 샘플링 전략까지 실제 운영에서 바로 적용 가능한 단위로 정리하겠습니다.

![Backend Development 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/backend-development-101/07/07-01-concept-at-a-glance.ko.png)
*Backend Development 101 7장 흐름 개요*

## 먼저 던지는 질문

- 왜 `print` 대신 logger를 써야 할까요?
- 구조화 로그는 어떤 모양이어야 운영에서 쓸모가 있을까요?
- 글로벌 예외 처리는 왜 응답 일관성을 지켜 줄까요?

## 관측 가능한 백엔드는 어떻게 다른가

운영 가능한 백엔드는 "실패해도 멈추지 않는 시스템"이 아니라 "실패했을 때 원인을 잃어버리지 않는 시스템"입니다. 이 관점에서 Logging과 Error Handling은 별개 기능이 아닙니다. 에러가 발생했을 때 어떤 응답이 나가고, 어떤 로그가 남고, 어떤 알림이 울리고, 누가 어떤 근거로 의사결정하는지가 하나의 체계로 연결됩니다.

실무에서는 다음 네 가지가 동시에 만족되어야 장애 대응 속도가 올라갑니다.

| 관점 | 질문 | 필요한 설계 |
|---|---|---|
| 추적성 | 이 에러가 어떤 요청에서 시작됐는가? | request_id, correlation_id, 컨텍스트 전파 |
| 해석성 | 이 로그를 쿼리/집계할 수 있는가? | JSON 구조화 로그, 필드 표준 |
| 일관성 | 클라이언트가 에러를 기계적으로 처리 가능한가? | 고정된 에러 응답 스키마 |
| 행동성 | 어떤 에러가 사람을 깨워야 하는가? | 레벨 정책, 알림 임계치, 온콜 룰 |

코드를 잘 작성하는 것과 운영을 잘하는 것은 다릅니다. 코드 품질은 로컬 테스트에서 보이지만, 운영 품질은 "문제가 생겼을 때 우리가 무엇을 볼 수 있는가"에서 드러납니다.

## Structured Logging: 왜 JSON인가

문자열 로그는 사람이 콘솔에서 읽기에는 편합니다. 운영 시스템이 대량 로그를 파싱하고 검색하고 집계하는 데는 매우 불리합니다. `"payment failed for user 42"` 같은 문장은 사람이 이해는 해도, 시스템 입장에서는 필드가 없는 자유 텍스트일 뿐입니다.

JSON 로그는 이 문제를 해결합니다. 같은 정보라도 다음처럼 구조를 가지면 검색과 알림이 달라집니다.

```json
{
  "timestamp": "2026-05-21T03:11:22.441Z",
  "level": "ERROR",
  "event": "payment_failed",
  "request_id": "f9f99af8-2f0e-4b61-b66f-a7f1cd3cd9af",
  "user_id": 42,
  "order_id": "ord_9A12",
  "error_code": "PAYMENT_PROVIDER_TIMEOUT",
  "duration_ms": 1734
}
```

운영에서 JSON이 강력한 이유는 세 가지입니다.

- 파싱: 파서가 정규식 없이 필드를 안정적으로 추출합니다.
- 필터링: `level=ERROR AND error_code=PAYMENT_PROVIDER_TIMEOUT` 같은 쿼리가 가능합니다.
- 알림: 특정 필드 조합에 임계치를 걸어 노이즈를 줄인 알림 정책을 만들 수 있습니다.

### `python-json-logger` 기본 설정

```python
import logging
import sys
from pythonjsonlogger import jsonlogger

handler = logging.StreamHandler(sys.stdout)
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s %(user_id)s %(endpoint)s %(duration_ms)s'
)
handler.setFormatter(formatter)

root = logging.getLogger()
root.setLevel(logging.INFO)
root.handlers = [handler]

logger = logging.getLogger("app")
logger.info("application_started", extra={"request_id": "-", "user_id": "-", "endpoint": "-", "duration_ms": 0})
```

### `structlog` 설정 예시

```python
import logging
import sys
import structlog

logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    logger_factory=structlog.PrintLoggerFactory(),
)

log = structlog.get_logger("app")
log.info("startup", component="api")
```

`structlog`의 장점은 "로그 문자열"이 아니라 "이벤트 + 속성" 중심으로 사고하게 만든다는 점입니다. 팀 단위로 필드 표준을 맞추기 좋고, contextvars 기반으로 request_id를 자동 주입하기도 쉽습니다.

## 로그 레벨은 심각도가 아니라 운영 계약입니다

많은 팀이 로그 레벨을 감정적으로 씁니다. "문제가 커 보이니 ERROR" 같은 방식입니다. 운영에서는 레벨을 감정이 아니라 계약으로 다뤄야 합니다. 레벨마다 "무엇이 벌어지고", "누가 반응하며", "어떤 액션이 필요한지"가 명확해야 합니다.

| 레벨 | 운영 의미 | 예시 | 기본 알림 |
|---|---|---|---|
| DEBUG | 개발/문제 재현용 상세 문맥 | SQL 바인딩 값, 분기별 내부 상태 | 운영 기본 비활성 |
| INFO | 정상 흐름에서 중요한 상태 전이 | 로그인 성공, 배치 시작/완료 | 페이지 없음 |
| WARNING | 자동 복구 가능하나 추적이 필요한 이상 징후 | 외부 API 1회 실패 후 재시도 성공 | 슬랙 요약 |
| ERROR | 요청 실패 또는 기능 실패 발생 | 결제 실패, DB 트랜잭션 롤백 | 임계치 초과 시 페이지 |
| CRITICAL | 서비스 핵심 기능이 광범위하게 중단 | DB 연결 불가, 인증 시스템 전체 장애 | 즉시 페이지 |

### 레벨 결정 테이블

아래 질문으로 레벨을 결정하면 팀 간 편차를 줄일 수 있습니다.

| 판단 질문 | Yes | No |
|---|---|---|
| 사용자 요청이 실패했는가? | ERROR 이상 | INFO/WARNING |
| 자동 복구 없이 운영자 개입이 필요한가? | CRITICAL 후보 | ERROR 이하 |
| 재시도/폴백으로 정상 응답이 가능한가? | WARNING | ERROR |
| 디버깅 전용 세부 정보인가? | DEBUG | INFO 이상 |

레벨 오남용이 만들어내는 대표 문제는 "모든 것이 ERROR"인 상태입니다. 이 경우 알림 시스템은 신뢰를 잃고, 결국 진짜 장애가 와도 아무도 급하게 보지 않습니다.

## Request ID와 Correlation ID: 서비스 경계를 넘는 추적

단일 서비스에서도 request_id는 유용하지만, 마이크로서비스 환경에서는 correlation_id가 없으면 장애 원인 경로를 잃기 쉽습니다.

- request_id: 현재 서비스가 받은 HTTP 요청 단위 식별자
- correlation_id: 서비스 체인을 가로지르는 전체 트랜잭션 식별자

권장 패턴은 다음과 같습니다.

1. 클라이언트에서 `X-Request-ID`를 보내면 신뢰 가능한 규칙에서 수용합니다.
2. 값이 없으면 게이트웨이 또는 첫 서비스가 새로 발급합니다.
3. 내부 호출(outbound HTTP/gRPC) 시 헤더를 반드시 전파합니다.
4. 로그와 에러 응답에 동일 ID를 기록합니다.

### FastAPI 미들웨어 패턴

```python
import time
import uuid
from fastapi import FastAPI, Request
from starlette.responses import Response
import structlog

app = FastAPI()
log = structlog.get_logger("api")

@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    started = time.perf_counter()

    # 클라이언트가 보낸 ID가 없으면 서버에서 생성
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    correlation_id = request.headers.get("X-Correlation-ID") or request_id

    # 요청 단위 컨텍스트 바인딩
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        correlation_id=correlation_id,
        endpoint=request.url.path,
        method=request.method,
    )

    try:
        response: Response = await call_next(request)
        return response
    finally:
        duration_ms = int((time.perf_counter() - started) * 1000)
        # 모든 요청에서 공통 필드 기록
        log.info("request_completed", status_code=getattr(locals().get("response"), "status_code", 500), duration_ms=duration_ms)
        if "response" in locals():
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Correlation-ID"] = correlation_id
```

핵심은 "모든 로그 라인에 컨텍스트가 자동으로 붙는 구조"입니다. 개발자가 매번 `extra={"request_id": ...}`를 수동으로 넣게 하면 빠진 로그가 반드시 생깁니다.

## FastAPI 글로벌 예외 처리: 에러를 응답으로 번역하는 경계

프로세스가 예외 하나로 즉시 종료되면 웹 서버는 신뢰 가능한 서비스가 아닙니다. ASGI 서버(Uvicorn/Gunicorn) + FastAPI 조합에서는 미처리 예외가 발생해도 프로세스 전체가 매번 죽는 구조가 아니라, 요청 단위 실패를 500 응답으로 반환하는 흐름을 갖습니다. 여기서 중요한 점은 "500으로 응답했다"로 끝내지 않고, 예외를 표준화된 응답/로그로 번역하는 공통 경계를 두는 것입니다.

### 기본 예외 핸들러 설계

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import structlog

app = FastAPI()
log = structlog.get_logger("api")

def error_payload(code: str, detail: str, request_id: str) -> dict:
    return {
        "error": "request_failed",
        "code": code,
        "detail": detail,
        "request_id": request_id,
    }

@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    request_id = request.headers.get("X-Request-ID", "unknown")
    log.info("validation_error", errors=exc.errors())
    return JSONResponse(
        status_code=422,
        content=error_payload("VALIDATION_ERROR", "입력값이 유효하지 않습니다.", request_id),
    )

@app.exception_handler(StarletteHTTPException)
async def http_handler(request: Request, exc: StarletteHTTPException):
    request_id = request.headers.get("X-Request-ID", "unknown")
    log.warning("http_error", status_code=exc.status_code, detail=str(exc.detail))
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload("HTTP_ERROR", str(exc.detail), request_id),
    )

@app.exception_handler(Exception)
async def unhandled_handler(request: Request, exc: Exception):
    request_id = request.headers.get("X-Request-ID", "unknown")
    # stack trace를 남겨 원인 분석 가능성 확보
    log.exception("unhandled_exception")
    return JSONResponse(
        status_code=500,
        content=error_payload("INTERNAL_SERVER_ERROR", "일시적인 오류가 발생했습니다.", request_id),
    )
```

`Exception` 핸들러를 마지막 안전망으로 두면, 누락된 예외가 있어도 응답 계약이 깨지지 않습니다. 동시에 `log.exception`으로 traceback을 남겨 사후 분석이 가능합니다.

## 도메인 예외와 인프라 예외를 분리해야 하는 이유

장애 대응에서 가장 위험한 설계는 서로 다른 성격의 실패를 같은 예외로 섞는 것입니다. "재고 부족"과 "DB 연결 실패"는 원인도, 사용자 메시지도, 재시도 전략도 다릅니다.

- 도메인 예외(Domain): 비즈니스 규칙 위반. 예: 재고 부족, 이미 취소된 주문.
- 인프라 예외(Infrastructure): 외부 의존성 실패. 예: DB 타임아웃, 메시지 브로커 연결 끊김.

권장 경계는 "컨트롤러(HTTP 경계)에서 번역"입니다.

```python
class DomainError(Exception):
    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail

class InfrastructureError(Exception):
    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail

def create_order(command):
    # 비즈니스 규칙 위반
    if command.quantity <= 0:
        raise DomainError("INVALID_QUANTITY", "수량은 1 이상이어야 합니다.")

    # 저장소 장애
    try:
        save_to_db(command)
    except TimeoutError as exc:
        raise InfrastructureError("DB_TIMEOUT", "데이터 저장에 실패했습니다.") from exc
```

```python
@app.post("/orders")
async def create_order_endpoint(payload: dict, request: Request):
    request_id = request.headers.get("X-Request-ID", "unknown")

    try:
        create_order(payload)
        return {"result": "ok"}
    except DomainError as exc:
        return JSONResponse(
            status_code=400,
            content={"error": "request_failed", "code": exc.code, "detail": exc.detail, "request_id": request_id},
        )
    except InfrastructureError as exc:
        log.error("infra_error", code=exc.code)
        return JSONResponse(
            status_code=503,
            content={"error": "request_failed", "code": exc.code, "detail": "일시적인 장애입니다. 잠시 후 다시 시도해 주세요.", "request_id": request_id},
        )
```

도메인 예외는 사용자에게 수정 가능한 피드백을 주고, 인프라 예외는 내부 원인 세부 정보를 감춘 채 안전한 메시지로 번역하는 것이 원칙입니다.

## 에러 응답 포맷 표준화

프런트엔드, 모바일, 외부 API 소비자가 안정적으로 동작하려면 에러 응답 형식이 고정되어야 합니다. 추천 스키마는 다음과 같습니다.

```json
{
  "error": "request_failed",
  "code": "PAYMENT_PROVIDER_TIMEOUT",
  "detail": "일시적인 결제 장애가 발생했습니다.",
  "request_id": "f9f99af8-2f0e-4b61-b66f-a7f1cd3cd9af"
}
```

필드 역할은 명확해야 합니다.

- `error`: 상위 분류(예: request_failed, auth_failed)
- `code`: 기계 처리 가능한 안정 코드(버전 간 유지)
- `detail`: 사용자 또는 운영자에게 보여줄 설명(민감정보 제외)
- `request_id`: 지원팀과 개발팀이 같은 사건을 가리키는 연결 키

가장 흔한 실수는 `detail`에 내부 예외 원문을 그대로 노출하는 것입니다. SQL, 토큰, 내부 URL, 스택 트레이스가 외부로 새어나가 보안 사고로 이어질 수 있습니다.

## 로그 컨텍스트 풍부화: user_id, endpoint, duration은 기본값

로그가 많아도 컨텍스트가 부족하면 쓸모가 없습니다. 최소한 다음 필드는 거의 모든 로그에 공통으로 들어가야 합니다.

| 필드 | 목적 | 비고 |
|---|---|---|
| request_id | 단일 요청 추적 | 필수 |
| correlation_id | 서비스 간 연쇄 추적 | 마이크로서비스 필수 |
| user_id | 사용자 영향 범위 파악 | 익명 사용자는 null 허용 |
| endpoint | 문제가 발생한 경로 확인 | 템플릿화(`/orders/{id}`) 권장 |
| duration_ms | 성능/타임아웃 분석 | 모든 완료 로그에 기록 |
| status_code | 실패 비율 계산 | HTTP 서버 필수 |

컨텍스트를 수동 삽입하면 누락이 반복됩니다. 미들웨어 + logger adapter/structlog contextvars로 자동화하는 편이 안전합니다.

## 운영 시나리오로 보는 실패 패턴

### 시나리오 1: 3am 알림이 왔는데 맥락이 없다

- 증상: ERROR 로그는 많은데 어떤 요청/사용자/엔드포인트인지 알 수 없음
- 원인: request_id 부재, endpoint/user_id 누락, 단순 문자열 로그
- 해결: 공통 필드 강제, 핸들러에서 `log.exception`, 에러 코드 표준화

### 시나리오 2: 로그 볼륨이 ELK 비용과 성능을 무너뜨린다

- 증상: 인덱싱 지연, 쿼리 타임아웃, 스토리지 급증
- 원인: DEBUG 상시 활성화, 중복 로그, 대용량 payload 원문 저장
- 해결: 레벨 정책 재정의, 샘플링, payload 마스킹/요약, 보존기간 계층화

### 시나리오 3: 에러 응답에 민감정보가 노출된다

- 증상: 클라이언트에서 내부 스택/토큰/SQL 메시지 확인
- 원인: 예외 문자열을 그대로 `detail`로 전달
- 해결: 외부 응답은 안전 문구 + 안정 코드, 내부 로그에만 상세 원인 저장

### 시나리오 4: 마이크로서비스 장애인데 원인 체인을 못 찾는다

- 증상: 서비스 A/B/C 로그가 각각 흩어져 사건 연결 불가
- 원인: correlation_id 미전파, outbound 헤더 누락
- 해결: 게이트웨이에서 발급, 모든 내부 호출에 헤더 전파, 공통 라이브러리화

운영 관점의 핵심은 "한 번의 장애를 다음 장애 대응 자산으로 바꾸는 것"입니다. 동일한 실패가 재발했을 때 조사 시간이 줄어들지 않으면 관측 설계가 부족한 신호입니다.

## 로그 로테이션과 보존 정책

컨테이너/클라우드 환경에서는 표준 출력으로 내보내고 수집기가 처리하는 방식이 일반적입니다. 그래도 로테이션/보존 정책은 명시해야 합니다.

- 애플리케이션 레벨: 파일 로깅 사용 시 `RotatingFileHandler` 또는 플랫폼 로테이터 적용
- 수집기 레벨: hot/warm/cold 저장 계층 분리
- 보존 기간: 운영/보안/감사 요구사항에 맞춰 차등 적용

예시 정책:

| 로그 종류 | 보존 기간 | 목적 |
|---|---|---|
| 애플리케이션 INFO | 14일 | 운영 점검 |
| ERROR/CRITICAL | 90일 | 장애 RCA, 감사 |
| 보안 감사 로그 | 180일 이상 | 컴플라이언스 |

보존 기간을 길게만 잡는 것은 답이 아닙니다. 검색 비용과 개인정보 보존 리스크도 함께 올라갑니다. "왜 이 로그를 이 기간 보관하는가"가 정책 문서에 남아 있어야 합니다.

## Alerting 전략: 페이지와 정보 알림을 분리

온콜을 깨우는 기준이 모호하면 팀은 빠르게 소진됩니다. 알림은 "사건 수"가 아니라 "행동 필요성"으로 분류해야 합니다.

- 페이지(on-call wake-up): 즉시 사람 개입 없이는 고객 영향이 확산되는 사건
- 정보 알림(info digest): 추세 확인 또는 근무시간 대응 가능한 사건

예시 룰:

| 조건 | 채널 | 응답 기대 |
|---|---|---|
| 5분 ERROR 비율 > 5% and 지속 10분 | PagerDuty | 즉시 대응 |
| CRITICAL 1건 이상 | PagerDuty + 전화 | 즉시 대응 |
| WARNING 급증(전주 대비 3배) | Slack | 근무시간 분석 |
| validation error 증가 | Slack daily | 제품/UX 개선 입력 |

중요한 점은 "모든 ERROR를 페이지하지 않는다"입니다. ERROR 중에서도 고객 영향, 복구 가능성, 지속 시간을 조합해 우선순위를 정해야 합니다.

## 운영 패턴: 중앙집중 로깅과 고트래픽 샘플링

중앙집중 로깅(ELK, Datadog, Cloud Logging)은 선택이 아니라 기본 인프라에 가깝습니다. 서비스 인스턴스에 남은 로컬 로그만으로는 장애 시점 재구성이 어렵습니다.

### 중앙집중 로깅 최소 기준

- 모든 인스턴스 로그가 단일 쿼리 평면에서 조회 가능
- request_id/correlation_id 기준 cross-service 검색 가능
- 대시보드와 알림 규칙이 동일 필드 표준을 공유

### 샘플링 전략

트래픽이 매우 높을 때 INFO 로그를 100% 저장하면 비용과 지연이 급증합니다. 대신 이벤트 성격에 따라 샘플링합니다.

- ERROR/CRITICAL: 100% 수집
- WARNING: 상황별 20~100%
- INFO: 1~10% 샘플링(핵심 이벤트는 예외적으로 100%)

샘플링은 무조건 비율만 줄이는 작업이 아닙니다. "무엇을 버리고 무엇을 반드시 남길지"를 명확히 정의하는 설계 작업입니다.

## 시니어 관점에서 보는 흔한 실수와 이유

1. **예외를 잡고 로그 없이 삼키는 실수**
   - 왜 위험한가: 실패 신호가 관측 계층으로 전달되지 않아 잠복 장애가 됩니다.
2. **모든 실패를 500 하나로 처리하는 실수**
   - 왜 위험한가: 클라이언트 재시도/사용자 안내/운영 대응이 모두 비효율적으로 변합니다.
3. **에러 코드 없이 메시지 문자열만 쓰는 실수**
   - 왜 위험한가: 다국어/문구 변경 시 자동 처리 규칙이 깨집니다.
4. **요청 완료 로그에서 duration을 빼는 실수**
   - 왜 위험한가: 지연 문제를 기능별로 분리 분석할 근거를 잃습니다.
5. **민감정보 마스킹 정책 없이 로깅하는 실수**
   - 왜 위험한가: 운영 편의보다 큰 보안 리스크를 만들고, 사고 대응 비용이 폭증합니다.

좋은 팀은 "로그를 많이 남기는 팀"이 아니라 "결정에 필요한 로그를 일관되게 남기는 팀"입니다.

## 적용 체크리스트

- [ ] JSON 구조화 로그를 기본 포맷으로 사용합니다.
- [ ] 로그 레벨별 운영 의미와 알림 정책이 문서화되어 있습니다.
- [ ] request_id/correlation_id를 헤더와 로그에 일관되게 전파합니다.
- [ ] 글로벌 예외 처리기가 모든 미처리 예외를 안전하게 500으로 변환합니다.
- [ ] 도메인 예외와 인프라 예외를 분리하고 경계에서 번역합니다.
- [ ] 에러 응답 스키마 `{error, code, detail, request_id}`를 고정합니다.
- [ ] 민감정보 마스킹, 로테이션, 보존 정책이 정의되어 있습니다.
- [ ] 페이지 알림과 정보 알림을 분리해 온콜 피로를 제어합니다.

## 처음 질문으로 돌아가기

- **왜 `print` 대신 logger를 써야 할까요?**
  - 운영에서는 한 줄 메시지보다 필드가 중요하기 때문입니다. logger 기반 JSON 로그를 쓰면 `request_id`, `user_id`, `endpoint`, `duration_ms`를 기준으로 사건을 재구성할 수 있고, 알림/대시보드 자동화도 가능합니다.
- **구조화 로그는 어떤 모양이어야 운영에서 쓸모가 있을까요?**
  - `timestamp`, `level`, `event`, `request_id`, `code`, `duration_ms` 같은 공통 필드를 갖는 단일 라인 JSON이어야 합니다. 이 형태가 있어야 검색, 집계, 임계치 알림, 서비스 간 상관분석이 가능합니다.
- **글로벌 예외 처리는 왜 응답 일관성을 지켜 줄까요?**
  - 예외가 어디서 발생하든 컨트롤러 경계에서 `{error, code, detail, request_id}`로 번역되기 때문입니다. 클라이언트는 안정적으로 처리하고, 운영자는 `request_id`로 내부 로그를 즉시 연결할 수 있습니다.

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
