---
series: observability-101
episode: 4
title: "Observability 101 (4/10): 구조화된 로깅"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Observability
  - Logging
  - Python
  - JSON
  - DevOps
seo_description: JSON 로그와 상관관계 ID로 운영 로그를 질의 가능한 데이터로 바꾸는 방법을 설명합니다
last_reviewed: '2026-05-15'
---

# Observability 101 (4/10): 구조화된 로깅

장애가 났을 때 로그가 있는데도 답을 찾지 못하는 경우가 많습니다. 로그 줄 수는 많은데 검색어를 조금만 바꾸면 결과가 달라지고, 같은 요청의 여러 줄이 서로 이어지지 않기 때문입니다. 자유 형식 문장은 읽기에는 편하지만 질의에는 약합니다.

구조화된 로깅은 이 문제를 정면으로 다룹니다. 로그를 설명문이 아니라 데이터로 남기면, 운영자는 문자열을 감으로 뒤지는 대신 필드 기반 질의를 할 수 있습니다.

이 글은 Observability 101 시리즈의 4번째 글입니다.

## 먼저 던지는 질문

- 왜 자유 형식 로그는 운영에서 금방 한계에 부딪힐까요?
- 구조화된 로그는 무엇이 다를까요?
- 로그 수준은 어떤 기준으로 나눠야 할까요?

## 큰 그림

![Observability 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/observability-101/04/04-01-concept-at-a-glance.ko.png)

*Observability 101 4장 흐름 개요*

구조화된 로깅를 다루는 이번 장에서는 주요 개념과 실무 패턴을 봅니다. 시스템이 복잡해질수록 이 개념들이 어디에서 시작되고 어떤 결과를 만드는지 이해하는 것이 중요합니다.

> 구조화된 로깅의 핵심은 도구 선택이 아니라, 언제 어디서 이 신호를 남기고 어떻게 해석할 것인가 하는 설계입니다.

## 왜 중요한가

운영에서는 장애 후 5분이 특히 중요합니다. 그 시간 안에 책임 서비스와 실패 이유를 좁히지 못하면, 팀은 금방 여러 가설을 동시에 따라가기 시작합니다. 로그가 질의 가능하지 않으면 이 첫 5분이 길어집니다.

구조화된 로그는 이 시간을 줄입니다. level, event, request_id, user_id, reason 같은 필드가 분리되어 있으면 특정 사용자, 특정 요청, 특정 에러 유형만 바로 골라 볼 수 있습니다. 로그가 데이터가 되는 순간, 장애 대응 속도가 달라집니다.

## 비정형 vs 정형 로그

로그 형식을 바꾸는 것만으로도 운영 효율이 크게 달라집니다.

| 구분 | 비정형 로그 | 정형 로그 (JSON) |
| --- | --- | --- |
| 검색성 | 문자열 grep 의존 | 필드 기반 질의 가능 |
| 파싱 비용 | 높음 (정규식 필요) | 낮음 (JSON parser 사용) |
| 알림 연동 | 어려움 (문자열 매칭) | 쉽음 (필드 조건 필터) |
| 집계 | 불가능에 가깨움 | 쉽게 가능 (GROUP BY) |
| 예시 | `User 123 login failed` | `{"event":"login_failed","user_id":123}` |

비정형 로그는 사람이 읽기에 편하지만, 기계가 질의하기에 약합니다. 정형 로그는 눈으로 읽기에는 불편할 수 있지만, 장애 대응과 집계에서 훨씬 빠릅니다.

## structlog로 FastAPI 미들웨어 만들기

structlog는 Python에서 구조화된 로그를 다루기 위한 대표적인 라이브러리입니다. 아래는 FastAPI에서 요청마다 구조화된 로그를 남기는 예제입니다.

```python
import structlog
import uuid
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# structlog 초기화
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()
app = FastAPI()

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    start_time = time.time()
    
    # 컴텍스트 바인드
    log = logger.bind(request_id=request_id, path=request.url.path, method=request.method)
    
    log.info("request_start")
    
    try:
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000
        
        log.info(
            "request_end",
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2)
        )
        
        return response
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        log.error(
            "request_error",
            error=str(e),
            duration_ms=round(duration_ms, 2)
        )
        return JSONResponse(status_code=500, content={"error": "Internal server error"})

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    logger.info("user_lookup", user_id=user_id)
    return {"user_id": user_id, "name": "test"}
```

이 코드는 모든 요청에 request_id를 붙이고, 시작과 끝을 구조화된 JSON 로그로 남깁니다. `bind()`로 공통 필드를 묶으면 매번 반복하지 않아도 됩니다.

## 로그 레벨 전략

로그 레벨은 단순한 분류가 아니라 저장량과 주목도를 동시에 통제하는 장치입니다.

| 레벨 | 기준 | 예시 | 저장 기간 |
| --- | --- | --- | --- |
| DEBUG | 개발 중 상세 흐름 | 함수 호출, 변수 값 | 짧게 (1일 이하) |
| INFO | 정상 이벤트 | 요청 시작/끝, 사용자 행동 | 보통 (7일) |
| WARNING | 주의 필요 (조치 가능) | 재시도, deprecated API 사용 | 길게 (30일) |
| ERROR | 요청 실패 | 예외 발생, 외부 API 타임아웃 | 매우 길게 (90일+) |
| CRITICAL | 시스템 위험 | DB 연결 실패, 메모리 부족 | 영구 |

### 레벨별 운영 지침

- **DEBUG**: 프로덕션에서는 끄지 말기. 개발 환경에서만 켜서 흐름을 확인하는 용도입니다.
- **INFO**: 기본 레벨. 대부분의 정상 이벤트는 INFO입니다.
- **WARNING**: 경보로 연결할 필요는 없지만, 나중에 문제가 될 수 있는 조짐를 남깁니다.
- **ERROR**: 즉시 경보로 연결. 사용자 요청이 실패했다면 ERROR입니다.
- **CRITICAL**: 온콜 알림. 시스템 전체가 위험한 상황에만 사용합니다.

레벨을 나누는 기준을 미리 합의해 두면 로그를 볼 때 중요도를 바로 판단할 수 있습니다. WARNING이 넘치면 기준이 널매한 것이고, ERROR가 매일 없으면 기준이 너무 높은 것입니다.

## 한눈에 보는 구조

로그를 구조화하면 검색 속도가 빨라지고 집계가 가능해집니다. JSON 같은 정형 포맷으로 남기면 대규모에서 비용도 통제할 수 있습니다.

## 핵심 용어

- 로그 수준: DEBUG, INFO, WARNING, ERROR, CRITICAL처럼 중요도를 나누는 기준입니다.
- 구조화 필드: 이벤트를 설명하는 key=value 데이터입니다.
- 상관관계 ID: 하나의 요청을 여러 로그 줄로 묶는 식별자입니다.
- 저장 대상: 로그가 최종적으로 적재되는 위치입니다.
- 샘플링: 로그 양이 너무 많을 때 일부만 남기는 전략입니다.

## 바꾸기 전과 후

바꾸기 전에는 `print(f"user {uid} failed: {e}")` 같은 줄이 쌓입니다. 사람 눈으로는 이해되지만, 사용자별 실패 건수를 집계하거나 같은 요청의 흐름만 모아 보려면 곧 한계가 옵니다.

바꾼 뒤에는 `logger.error("login_failed", user_id=uid, reason=str(e))`처럼 이벤트와 필드가 나뉩니다. 이제 로그는 읽는 문장인 동시에 질의 가능한 데이터가 됩니다.

## 실습: 구조화된 로깅을 다섯 단계로 붙이기

### 1단계 — 기본 로거 만들기

```python
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("app")
log.info("started")
```

기본 로거만으로도 print보다 낫습니다. 최소한 수준 구분이 생기고, 출력 경로를 통제할 수 있기 때문입니다.

### 2단계 — 구조화 출력 형식 붙이기

```python
import json, logging

class JsonFmt(logging.Formatter):
    def format(self, r):
        return json.dumps({"lvl": r.levelname, "msg": r.getMessage(),
                            **getattr(r, "extra", {})})

h = logging.StreamHandler(); h.setFormatter(JsonFmt())
log = logging.getLogger("app"); log.addHandler(h); log.setLevel("INFO")
```

한 줄이 JSON으로 바뀌는 순간 필드 기반 검색이 가능해집니다. 이 변화 하나만으로도 로그 분석 방식이 크게 달라집니다.

### 3단계 — 맥락 필드 넣기

```python
def login(uid):
    log.info("login_attempt", extra={"extra": {"user_id": uid}})
```

로그는 사건만 남기면 부족합니다. 누구 요청이었는지, 어떤 주문이었는지, 어느 경로였는지 같은 맥락이 있어야 장애를 좁힐 수 있습니다.

### 4단계 — 상관관계 식별자 전달하기

```python
import uuid
def handle(req):
    rid = req.headers.get("x-request-id") or str(uuid.uuid4())
    log.info("request_in", extra={"extra": {"rid": rid}})
```

상관관계 ID가 있으면 같은 요청의 여러 줄을 하나로 묶을 수 있습니다. 분산 시스템에서는 trace_id나 request_id가 로그의 기본 필드라고 생각하는 편이 좋습니다.

### 5단계 — 수준 정책 정하기

```text
DEBUG    → development detail
INFO     → normal events
WARNING  → cautions (actionable)
ERROR    → failed requests
CRITICAL → system risk
```

모든 로그를 INFO로 남기면 중요한 줄이 묻힙니다. 수준 정책은 저장량과 주목도를 동시에 통제하는 장치입니다.

## 요청 하나를 이렇게 따라갑니다

구조화된 로그의 가장 큰 장점은 요청 하나를 필드 조건으로 바로 모을 수 있다는 점입니다. 아래처럼 request_id 또는 trace_id를 기준으로 좁히면 장애 대응의 첫 5분이 훨씬 짧아집니다.

```bash
# JSON 로그에서 특정 요청만 필터링
grep '"rid": "req-7f2a"' app.log

# ERROR 레벨만 다시 확인
grep '"lvl": "ERROR"' app.log | grep '"rid": "req-7f2a"'
```

```json
{"lvl":"INFO","msg":"request_in","rid":"req-7f2a","path":"/login"}
{"lvl":"ERROR","msg":"login_failed","rid":"req-7f2a","reason":"db_timeout"}
```

```text
Expected output:
- 같은 rid를 가진 로그 줄만 모입니다.
- ERROR 한 줄에서 실패 유형을 바로 읽을 수 있습니다.
- user_email 같은 민감 필드는 원문 대신 마스킹 또는 해시 값으로 남습니다.
```

## 이 코드에서 먼저 봐야 할 점

- `extra`를 이용하면 임의의 필드를 자연스럽게 붙일 수 있습니다.
- 상관관계 ID는 가능한 한 모든 요청 로그에 실려야 합니다.
- JSON 한 줄 형식은 Loki, ELK, BigQuery 같은 여러 저장소로 쉽게 보낼 수 있습니다.

## 자주 하는 실수 다섯 가지

1. print만 사용합니다. 검색과 집계가 금방 막힙니다.
2. 모든 로그를 INFO로 남깁니다. 진짜 신호가 묻힙니다.
3. 개인정보를 그대로 기록합니다. 보안과 규정 준수 문제가 생깁니다.
4. 메시지 문자열 안에만 정보를 넣습니다. 필드가 없으니 질의가 약해집니다.
5. 스택 트레이스를 한 줄로 뭉개서 남깁니다. 읽기와 분석이 모두 어려워집니다.

## 실무에서는 이렇게 생각한다

대부분의 팀은 JSON 로그를 Loki나 ELK로 보내고, 상관관계 ID로 트레이스와 연결합니다. 로그는 더 많이 남기는 것보다 더 잘 질의할 수 있게 남기는 편이 중요합니다.

또 하나 잊기 쉬운 점은 개인정보 처리입니다. 운영에 유용하다는 이유로 원문 데이터를 전부 남기기 시작하면, 로그는 가장 빠르게 위험해지는 저장소가 됩니다. 마스킹과 해시 정책은 로깅 설계의 일부여야 합니다.

## 체크리스트

- [ ] JSON 한 줄 형식으로 로그를 남깁니다.
- [ ] 로그 수준 정책이 있습니다.
- [ ] 상관관계 ID를 전파합니다.
- [ ] 민감 정보 마스킹 규칙이 있습니다.

## 연습 문제

1. 기존 print 한 줄을 구조화된 로그로 바꿔 보세요.
2. 미들웨어에서 상관관계 ID를 주입해 보세요.
3. 특정 사용자 ID의 ERROR 로그만 조회하는 질의를 설계해 보세요.

## 정리

구조화된 로그는 운영 로그를 설명문에서 데이터로 바꿉니다. 로그 수준, 맥락 필드, 상관관계 ID가 자리 잡으면 장애 대응의 첫 5분이 짧아집니다. 다음 글에서는 요청이 여러 서비스를 가로지를 때 왜 분산 트레이싱이 필요한지 이어서 보겠습니다.

## JSON 로그 필드 표준 제안

구조화된 로깅을 도입해도 팀마다 필드 이름이 다르면 운영 효율이 낮아집니다. 아래처럼 최소 공통 스키마를 두면 질의 템플릿과 경보 규칙을 재사용하기 쉽습니다.

| 필드 | 타입 | 설명 | 예시 |
| --- | --- | --- | --- |
| ts | number | Unix epoch 또는 ISO 타임스탬프 | 1716000123.22 |
| level | string | 로그 수준 | INFO |
| event | string | 이벤트 이름 | payment_failed |
| service | string | 서비스 이름 | checkout-api |
| env | string | 실행 환경 | prod |
| trace_id | string | 분산 추적 식별자 | 9f3c... |
| request_id | string | 요청 식별자 | req-12ab |
| route | string | 정규화된 경로 | /orders/:id |
| status_code | number | HTTP 상태 코드 | 502 |
| error_code | string | 도메인 오류 코드 | GATEWAY_TIMEOUT |

중요한 점은 "모든 정보를 다 넣기"가 아니라 "자주 묻는 질문에 답할 최소 필드"를 고정하는 것입니다. 사용자 이메일, 카드 번호, 주민번호처럼 민감한 값은 원문 저장을 피하고 마스킹 또는 해시로 대체해야 합니다.

## structlog 초기화 템플릿

```python
import logging
import structlog


def configure_logger() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def mask_email(email: str) -> str:
    name, domain = email.split("@")
    visible = name[:2] if len(name) >= 2 else name
    return f"{visible}***@{domain}"
```

이 구성은 운영에서 자주 필요한 두 가지를 만족합니다. 첫째, 예외 정보를 JSON 안에 구조적으로 남깁니다. 둘째, request context를 `contextvars`로 전달해 비동기 코드에서도 공통 필드를 유지합니다.

## 로그 레벨 운영 기준

로그 레벨을 정의할 때는 "중요도"만이 아니라 "행동"을 기준으로 삼는 편이 좋습니다. 즉, 해당 로그를 본 사람이 무엇을 해야 하는가를 먼저 정합니다.

| 레벨 | 질문 | 운영 행동 | 예시 이벤트 |
| --- | --- | --- | --- |
| DEBUG | 흐름이 맞는가 | 개발 환경 확인 | serializer_mismatch |
| INFO | 정상 처리 중인가 | 대시보드 참고 | request_end |
| WARNING | 악화 조짐인가 | 티켓/리뷰 | retry_exhausted_soon |
| ERROR | 요청 실패인가 | 경보 또는 즉시 점검 | payment_failed |
| CRITICAL | 광범위 장애인가 | 온콜 호출 | db_unavailable |

레벨 기준이 없으면 팀마다 동일 이벤트를 서로 다른 레벨로 기록하게 됩니다. 그러면 경보 규칙의 신뢰도가 떨어지고, 같은 장애를 두 번 세 번 처리하게 됩니다. 레벨 사전은 코드 리뷰 체크리스트에 포함하는 편이 좋습니다.

## 처음 질문으로 돌아가기

- **왜 자유 형식 로그는 운영에서 금방 한계에 부딪힐까요?**
  - 본문의 기준은 구조화된 로깅를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **구조화된 로그는 무엇이 다를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **로그 수준은 어떤 기준으로 나눠야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Observability 101 (1/10): 관측성이란 무엇인가?](./01-what-is-observability.md)
- [Observability 101 (2/10): 메트릭, 로그, 트레이스](./02-metric-log-trace.md)
- [Observability 101 (3/10): 메트릭 수집과 시각화](./03-metric-collection.md)
- **구조화된 로깅 (현재 글)**
- 분산 트레이싱 기초 (예정)
- 대시보드 설계 (예정)
- 경보와 온콜 (예정)
- 서비스 수준 지표와 목표 기초 (예정)
- 비용과 카디널리티 (예정)
- 운영 가능한 관측성 스택 (예정)

<!-- toc:end -->

## 참고 자료

- [Python logging](https://docs.python.org/3/library/logging.html)
- [structlog](https://www.structlog.org/)
- [OpenTelemetry logs](https://opentelemetry.io/docs/concepts/signals/logs/)
- [Twelve-factor logs](https://12factor.net/logs)

Tags: Observability, Logging, Python, JSON, DevOps
