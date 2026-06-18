---
series: observability-101
episode: 4
title: "바이브코딩을 위한 Observability 기초 (4/10): 구조화된 로깅"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Observability
  - Logging
  - Python
  - JSON
seo_description: 바이브코딩으로 만든 서비스에서 print 문과 자유 형식 로그를 JSON 구조화 로그로 바꾸는 방법과, AI 코드에서 흔히 생기는 로깅 실수를 설명합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 Observability 기초 (4/10): 구조화된 로깅

이 글은 **바이브코딩을 위한 Observability 기초** 시리즈의 네 번째 글입니다. AI가 생성한 코드에서 로그는 대부분 `print`나 자유 형식 문자열로 남습니다. 이것을 질의 가능한 데이터로 바꾸는 방법을 다룹니다.

---

장애가 났을 때 로그가 있는데도 답을 찾지 못하는 경우가 많습니다. 바이브코딩 결과물에서 특히 자주 나타나는 패턴입니다. AI가 생성한 코드는 대부분 `print(f"User {uid} failed: {e}")` 같은 자유 형식 로그를 남기기 때문입니다. 로그 줄 수는 많은데, 검색어를 조금만 바꾸면 결과가 달라지고, 같은 요청의 여러 줄이 서로 이어지지 않습니다.

구조화된 로깅은 이 문제를 정면으로 다룹니다. 로그를 설명문이 아니라 데이터로 남기면, 장애 대응의 첫 5분이 훨씬 짧아집니다.

> "AI가 만든 코드에서 `print(f'...')` 한 줄을 `logger.error('payment_failed', user_id=uid, reason=str(e))`로 바꾸는 순간, 로그가 질의 가능한 데이터가 됩니다."

## 이 글에서 다룰 문제

- 왜 자유 형식 로그는 운영에서 금방 한계에 부딪힐까요?
- 구조화된 로그는 무엇이 다를까요?
- 로그 수준은 어떤 기준으로 나눠야 할까요?
- AI가 생성한 로그 코드에서 자주 보이는 문제는 무엇일까요?
- 개인정보 처리를 어떻게 해야 할까요?

---

바이브코딩으로 만든 서비스에서 장애가 나면, 로그는 있지만 쓸모가 없는 상황이 자주 나타납니다. "결제 실패" 같은 메시지는 있지만 어떤 사용자의 어떤 주문인지, 어떤 에러 코드가 나왔는지는 문자열 안에 묻혀 있습니다. 로그가 데이터가 되어야 5분 안에 원인을 좁힐 수 있습니다.

AI에게 "로그 개선해줘"라고 하면 structlog나 loguru를 붙여주지만, 필드 설계까지 해주지는 않는 경우가 많습니다. 어떤 필드가 항상 있어야 하는지 직접 지정해야 합니다.

## 비정형 vs 정형 로그

| 구분 | 비정형 로그 | 정형 로그 (JSON) |
| --- | --- | --- |
| 검색성 | 문자열 grep 의존 | 필드 기반 질의 가능 |
| 파싱 비용 | 높음 (정규식 필요) | 낮음 (JSON parser) |
| 알림 연동 | 어려움 (문자열 매칭) | 쉬움 (필드 조건 필터) |
| 집계 | 거의 불가능 | 쉽게 가능 (GROUP BY) |
| 예시 | `User 123 login failed` | `{"event":"login_failed","user_id":123}` |

## structlog로 FastAPI 미들웨어 만들기

AI에게 이 코드를 직접 요청하거나, 이 패턴을 참고해서 요청할 수 있습니다.

```python
import structlog
import uuid
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

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

    log = logger.bind(
        request_id=request_id,
        path=request.url.path,
        method=request.method
    )

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
```

모든 요청에 `request_id`가 붙기 때문에 같은 요청의 여러 로그 줄을 하나로 모을 수 있습니다.

## 로그 수준 전략

| 레벨 | 기준 | 예시 | 저장 기간 |
| --- | --- | --- | --- |
| DEBUG | 개발 중 상세 흐름 | 함수 호출, 변수 값 | 짧게 (1일 이하) |
| INFO | 정상 이벤트 | 요청 시작/끝, 사용자 행동 | 보통 (7일) |
| WARNING | 주의 필요 (조치 가능) | 재시도, deprecated 사용 | 길게 (30일) |
| ERROR | 요청 실패 | 예외 발생, 외부 API 타임아웃 | 매우 길게 (90일+) |
| CRITICAL | 시스템 위험 | DB 연결 실패 | 영구 |

AI가 생성한 코드는 모든 것을 `INFO`로 남기는 경향이 있습니다. "결제 실패는 ERROR, 재시도는 WARNING, 정상 요청은 INFO로 구분해줘"라고 명시적으로 요청하세요.

## Before / After: 로그 품질 개선

**Before (AI 기본 생성 코드)**

```python
# AI가 기본으로 생성하는 패턴
print(f"Processing order {order_id} for user {user_id}")
try:
    result = process_payment(order_id)
    print(f"Payment success: {result}")
except Exception as e:
    print(f"Payment failed: {e}")
```

**After (구조화된 로그)**

```python
# 개선된 패턴
log = logger.bind(order_id=order_id, user_id=user_id)
log.info("payment_processing_start")
try:
    result = process_payment(order_id)
    log.info("payment_success", amount=result["amount"])
except Exception as e:
    log.error("payment_failed", reason=str(e), error_code=getattr(e, "code", "UNKNOWN"))
```

After 패턴에서는 `order_id`, `user_id`, `reason`, `error_code` 필드가 분리되어 있어서 "이번 주 결제 실패를 에러 코드별로 집계해줘"라는 질의가 바로 가능합니다.

## 공통 로그 필드 표준

AI에게 로그 코드를 요청할 때 이 필드 목록을 주면 일관된 구조를 받습니다.

| 필드 | 타입 | 설명 | 예시 |
| --- | --- | --- | --- |
| ts | number | Unix epoch | 1716000123.22 |
| level | string | 로그 수준 | INFO |
| event | string | 이벤트 이름 | payment_failed |
| service | string | 서비스 이름 | checkout-api |
| trace_id | string | 분산 추적 식별자 | 9f3c... |
| request_id | string | 요청 식별자 | req-12ab |
| route | string | 정규화된 경로 | /orders/:id |
| status_code | number | HTTP 상태 코드 | 502 |
| error_code | string | 도메인 오류 코드 | GATEWAY_TIMEOUT |

## 개인정보 마스킹: 바이브코딩의 보안 위험

AI가 생성한 코드에서 가장 흔한 보안 문제 중 하나는 개인정보가 로그에 그대로 남는 것입니다.

```python
import hashlib
import re
from typing import Any

PII_FIELDS = {"email", "phone", "card_number", "ssn"}

def mask_value(key: str, value: Any) -> Any:
    if key in PII_FIELDS:
        if isinstance(value, str):
            return hashlib.sha256(value.encode()).hexdigest()[:16]
        return "***"
    return value

def sanitize_log(payload: dict) -> dict:
    return {k: mask_value(k, v) for k, v in payload.items()}

# 사용 예시
raw = {"event": "user_registered", "email": "user@example.com", "plan": "pro"}
safe = sanitize_log(raw)
# {"event": "user_registered", "email": "a1b2c3d4...", "plan": "pro"}
```

AI에게 로그 코드를 요청할 때 "email, phone, card_number는 반드시 마스킹해줘"라는 조건을 포함하세요.

## 자주 하는 실수

| 실수 | 문제 | AI 코드에서 확인할 점 |
| --- | --- | --- |
| `print`만 사용 | 검색과 집계 불가 | `logger.info()` 형태로 교체 요청 |
| 모든 로그를 INFO로 남김 | 진짜 신호가 묻힘 | 레벨 정책 명시 후 요청 |
| 개인정보 그대로 기록 | 보안 사고 위험 | PII 필드 마스킹 조건 명시 |
| 메시지 문자열 안에만 정보 | 필드 없어 질의 약함 | 키-값 필드로 분리 요청 |
| trace_id 없음 | 요청 흐름 추적 불가 | 모든 요청에 trace_id 포함 요청 |

## AI 프롬프트 팁

```text
[구조화된 로그 요청]
"이 서비스에 구조화된 로깅 추가해줘:
1. structlog 사용, JSON 형식 출력
2. 모든 요청에 request_id, trace_id 자동 포함
3. 로그 레벨 정책:
   - 정상 요청 시작/끝: INFO
   - 외부 API 타임아웃: ERROR
   - 재시도 발생: WARNING
   - DB 연결 실패: CRITICAL
4. email, phone, card_number 필드는 SHA-256 해시로 마스킹
5. 개인정보를 메시지 문자열에 직접 넣지 말 것"
```

## 운영 체크리스트

- [ ] JSON 한 줄 형식으로 로그를 남깁니다.
- [ ] 로그 수준 정책이 팀에 합의되어 있습니다.
- [ ] 모든 요청에 trace_id 또는 request_id가 포함됩니다.
- [ ] 민감 정보 마스킹 규칙이 코드에 적용되어 있습니다.
- [ ] AI 생성 코드의 로그 레벨이 올바른지 검토합니다.

## 처음 질문으로 돌아가기

- **왜 자유 형식 로그는 운영에서 금방 한계에 부딪힐까요?**
  grep은 가능하지만 필드 기반 질의와 집계가 안 됩니다. "이번 주 어떤 에러 코드가 가장 많이 나왔지?"라는 질문에 답하려면 JSON 필드가 필요합니다.

- **구조화된 로그는 무엇이 다를까요?**
  이벤트 이름, 필드가 분리되어 있어서 `level=ERROR AND service=payment AND error_code=TIMEOUT`처럼 조건 검색이 가능합니다.

- **로그 수준은 어떤 기준으로 나눠야 할까요?**
  "이 로그를 본 사람이 무엇을 해야 하는가"를 기준으로 정합니다. 즉시 경보가 필요하면 ERROR, 업무 시간에 확인하면 WARNING, 참고용이면 INFO입니다.

---

## 정리

구조화된 로그는 운영 로그를 설명문에서 데이터로 바꿉니다. 바이브코딩으로 만든 서비스에서 AI가 생성한 `print` 문과 자유 형식 로그를 JSON 구조화 로그로 교체하는 것만으로도 장애 대응 속도가 크게 달라집니다. 다음 글에서는 요청이 여러 서비스를 가로지를 때 분산 트레이싱이 왜 필요한지 살펴봅니다.

## 참고 자료

- [Python logging](https://docs.python.org/3/library/logging.html)
- [structlog](https://www.structlog.org/)
- [OpenTelemetry logs](https://opentelemetry.io/docs/concepts/signals/logs/)
- [Twelve-factor logs](https://12factor.net/logs)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Observability 기초 (1/10): 관측성이란 무엇인가?
- 바이브코딩을 위한 Observability 기초 (2/10): 메트릭, 로그, 트레이스
- 바이브코딩을 위한 Observability 기초 (3/10): 메트릭 수집과 시각화
- **바이브코딩을 위한 Observability 기초 (4/10): 구조화된 로깅 (현재 글)**
- 바이브코딩을 위한 Observability 기초 (5/10): 분산 트레이싱 기초
- 바이브코딩을 위한 Observability 기초 (6/10): 대시보드 설계
- 바이브코딩을 위한 Observability 기초 (7/10): 경보와 온콜
- 바이브코딩을 위한 Observability 기초 (8/10): 서비스 수준 지표와 목표 기초
- 바이브코딩을 위한 Observability 기초 (9/10): 비용과 카디널리티
- 바이브코딩을 위한 Observability 기초 (10/10): 운영 가능한 관측성 스택
<!-- toc:end -->

Tags: 바이브코딩, Observability, Logging, Python, JSON
