---
title: "바이브코딩을 위한 DevOps 기초 (8/10): 로그 수집과 분석"
series: devops-101
episode: 8
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- DevOps
- AI코딩
seo_description: "바이브코딩으로 만든 앱에서 문제가 생기면 로그가 원인을 알려줍니다. 구조화 로그 설계와 분산 시스템에서 문제를 빠르게 찾는 로깅 전략을 정리합니다."
---

# 바이브코딩을 위한 DevOps 기초 (8/10): 로그 수집과 분석

이 글은 바이브코딩을 위한 DevOps 기초 시리즈의 8번째 글입니다.

AI 코딩 도구로 만든 앱을 배포했더니 에러가 납니다. 어디서 에러가 나는지 알기 위해 서버에 SSH로 접속해서 로그를 찾습니다. 그런데 로그가 `print("error occurred")`처럼 단순 문자열이면 언제, 어떤 사용자가, 어떤 요청에서 에러가 났는지 알 수가 없습니다.

로그는 모니터링이 "무엇이 문제인지"를 알려준다면, "왜 문제인지"를 설명합니다. 잘 설계된 로그는 특정 사용자의 요청이 시스템을 어떻게 통과했는지 한 번에 추적하게 해줍니다. 반면 `print` 문 수준의 로그는 서버가 여러 대가 되는 순간 거의 쓸모가 없어집니다.

AI에게 "로깅 코드 추가해줘"라고 요청하면 로그를 추가해줍니다. 하지만 구조화 로그가 무엇인지, correlation ID가 왜 필요한지, 로그를 중앙에서 수집하는 이유가 무엇인지 모르면 AI가 만든 로그 코드가 실제 디버깅에 도움이 되지 않을 수 있습니다.

> 로그는 지금 보는 것보다 문제가 생긴 뒤에 더 자주 읽힙니다.

---

## 이 글에서 다룰 문제
- 구조화 로그와 비구조화 로그는 실무 디버깅에서 무엇이 다를까요?
- correlation ID는 왜 분산 시스템에서 필수일까요?
- 여러 서버의 로그를 한곳에 모아야 하는 이유는 무엇일까요?
- AI가 만든 로그 코드에서 자주 생기는 문제는 무엇일까요?
- 로그에 PII를 남기면 왜 위험할까요?

## 로그 레벨 기준

| 레벨 | 용도 | 운영 환경 |
|---|---|---|
| DEBUG | 상세한 변수 값, 내부 상태 | 기본 OFF (일시적으로만) |
| INFO | 정상 흐름, 사용자 행동 | ON |
| WARNING | 문제는 아니지만 주의 필요 | ON |
| ERROR | 기능 실패, 예외 발생 | ON |
| CRITICAL | 시스템 전체 중단 가능 | 항상 ON |

운영 환경에서 DEBUG를 켜두면 비용과 노이즈가 폭증합니다. AI가 만든 코드에 DEBUG 로그가 많다면 반드시 확인하세요.

## 구조화 로그 + Correlation ID 적용

```python
import structlog
import uuid
from fastapi import FastAPI, Request

# 구조화 로그 설정
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ]
)
log = structlog.get_logger()

app = FastAPI()

@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    # 요청마다 고유 ID 생성 (외부에서 전달되면 그것을 사용)
    rid = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    structlog.contextvars.bind_contextvars(request_id=rid)
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    return response

@app.post("/orders")
async def create_order(order_id: str, user_id: str):
    log.info("order.create.start", order_id=order_id)
    try:
        # ... 주문 처리
        log.info("order.create.success", order_id=order_id)
    except Exception as e:
        log.error("order.create.failed", order_id=order_id, error=str(e))
        raise
```

이제 모든 로그에 `request_id`가 포함됩니다. 특정 요청에서 무슨 일이 있었는지 request_id 하나로 전체 흐름을 추적할 수 있습니다.

## Before / After

**Before**: "에러가 났다는 신고를 받고 서버 로그를 봤는데 `Error: connection failed`만 있었다. 어떤 사용자가, 어떤 시간에, 어떤 요청에서 났는지 알 수 없어서 재현이 불가능했다."

**After**: "에러 로그에 request_id, user_id, 시각, 에러 상세가 JSON으로 남는다. Grafana에서 request_id로 검색하면 해당 요청의 전체 흐름을 1분 안에 찾을 수 있다."

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| `print()`로 로그를 남기는 실수 | 시간, 레벨, 구조가 없어 운영에서 쓸 수 없음 | structlog, logging 모듈로 교체 |
| PII(개인정보)를 로그에 그대로 남기는 실수 | 이름, 이메일, 전화번호는 규정 위반 | 마스킹 처리 후 로그 기록 |
| 보존 기간 없이 로그를 계속 쌓는 실수 | 저장 비용이 예상치 못하게 폭증 | 30일 또는 90일 보존 정책 설정 |
| correlation ID 없이 운영하는 실수 | 분산 시스템에서 특정 요청의 에러를 추적 불가 | 모든 요청에 UUID 기반 request_id 부여 |
| ERROR에 스택트레이스를 안 남기는 실수 | 에러가 어디서 발생했는지 알 수 없음 | 예외 처리 시 반드시 exc_info=True 포함 |

## AI에게 로깅 관련 질문하는 팁

로깅 코드를 AI에게 요청할 때 이 정보를 포함하면 실제로 쓸 수 있는 결과를 받습니다:

```
프레임워크: [FastAPI, Django, Flask 등]
로그 형식: [JSON 구조화 로그]
추적 필드: [request_id, user_id, service]
민감 정보 마스킹: [이메일, 전화번호 등]
중앙 수집 도구: [Grafana Loki, ELK 등]
```

AI가 만든 로그 코드를 받았다면 반드시 확인할 것: DEBUG 로그가 운영 환경에서 켜지지 않는지, PII가 그대로 남는 곳은 없는지, 에러 핸들링에서 스택트레이스가 포함되는지.

## 운영 체크리스트

- [ ] 로그가 JSON 구조화 형태로 출력됩니다
- [ ] 모든 요청에 request_id(correlation ID)가 부여됩니다
- [ ] 이름, 이메일 등 PII가 마스킹됩니다
- [ ] 로그 보존 기간이 설정되어 있습니다
- [ ] 에러 로그에 스택트레이스가 포함됩니다

## 처음 질문으로 돌아가기

"AI가 `print()`로 로그를 만들어줬는데 왜 바꿔야 하나요?"

서버 한 대에서 혼자 개발할 때는 `print()`도 충분합니다. 하지만 서버가 여러 대가 되거나, 에러가 나서 원인을 추적해야 할 때 `print()` 로그는 거의 쓸모가 없습니다. 언제, 어떤 요청에서, 어떤 에러가 났는지 구조화된 정보가 있어야 빠르게 문제를 찾을 수 있습니다. 바이브코딩으로 빠르게 만든 앱이라도 운영 로그 설계는 처음부터 제대로 해야 합니다.

## 정리

로그는 서비스 상태를 시간을 거슬러 읽게 해주는 기록입니다. 구조화 로그, correlation ID, 중앙 수집 세 가지가 갖춰지면 문제 원인을 찾는 시간이 크게 줄어듭니다. 다음 글에서는 로그와 메트릭을 묶어 실제 장애에 대응하는 방법을 다룹니다.

## 참고 자료
### 공식 문서
- [structlog Documentation](https://www.structlog.org/)
- [Grafana Loki](https://grafana.com/docs/loki/latest/)
- [OpenTelemetry Logs](https://opentelemetry.io/docs/specs/otel/logs/)
### 관련 시리즈
- [바이브코딩을 위한 DevOps 기초 (7/10): 모니터링과 알림](./07-monitoring-and-alerting.md)
- [바이브코딩을 위한 DevOps 기초 (9/10): 장애 대응과 on-call](./09-incident-and-oncall.md)

---

<!-- toc:begin -->
## 시리즈 목차
- [바이브코딩을 위한 DevOps 기초 (1/10): DevOps란 무엇인가?](./01-what-is-devops.md)
- [바이브코딩을 위한 DevOps 기초 (2/10): CI 파이프라인](./02-ci-pipeline.md)
- [바이브코딩을 위한 DevOps 기초 (3/10): CD와 배포 전략](./03-cd-and-deployment.md)
- [바이브코딩을 위한 DevOps 기초 (4/10): 환경 분리와 설정 관리](./04-environments-and-config.md)
- [바이브코딩을 위한 DevOps 기초 (5/10): Infrastructure as Code](./05-infrastructure-as-code.md)
- [바이브코딩을 위한 DevOps 기초 (6/10): 컨테이너와 빌드](./06-containers-and-build.md)
- [바이브코딩을 위한 DevOps 기초 (7/10): 모니터링과 알림](./07-monitoring-and-alerting.md)
- **바이브코딩을 위한 DevOps 기초 (8/10): 로그 수집과 분석 (현재 글)**
- [바이브코딩을 위한 DevOps 기초 (9/10): 장애 대응과 on-call](./09-incident-and-oncall.md)
- [바이브코딩을 위한 DevOps 기초 (10/10): 운영 가능한 DevOps 흐름](./10-operable-devops-flow.md)
<!-- toc:end -->

Tags: 바이브코딩, DevOps, AI코딩, Logging, Observability
