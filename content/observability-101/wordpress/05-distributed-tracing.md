---
series: observability-101
episode: 5
title: "바이브코딩을 위한 Observability 기초 (5/10): 분산 트레이싱 기초"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Observability
  - Tracing
  - OpenTelemetry
  - Microservices
seo_description: 바이브코딩으로 만든 마이크로서비스에서 span, trace, context propagation이 어떻게 동작하는지, AI 코드에 OpenTelemetry를 붙이는 방법을 설명합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 Observability 기초 (5/10): 분산 트레이싱 기초

이 글은 **바이브코딩을 위한 Observability 기초** 시리즈의 다섯 번째 글입니다. AI와 함께 마이크로서비스를 만들면 서비스가 여럿 생기고, 그 서비스들 사이를 요청이 지나다닙니다. 어디서 느려졌는지 찾는 것이 분산 트레이싱의 역할입니다.

---

메트릭으로는 느려졌다는 사실을 볼 수 있고, 로그로는 어떤 사건이 있었는지 읽을 수 있습니다. 그런데 바이브코딩으로 만든 서비스가 세 개, 다섯 개로 늘어나면, 어느 서비스가 병목인지 로그만으로는 찾기 어렵습니다. 서비스 A의 로그는 정상처럼 보이고, 서비스 B의 로그도 큰 문제가 없어 보이는데, 실제로는 둘 사이 호출이 길어졌을 수 있습니다.

AI에게 "마이크로서비스 A가 B를 호출하고 B가 C를 호출하는 구조 만들어줘"라고 하면 각 서비스는 잘 만들어주지만, 서비스 간 trace_id 전달은 빠뜨리는 경우가 많습니다. 그러면 트레이스가 중간에서 끊기고, 전체 요청 흐름을 볼 수 없게 됩니다.

> "분산 트레이싱은 AI가 만든 마이크로서비스들을 하나의 흐름으로 연결하는 기술입니다. trace_id가 서비스 간에 전달되어야 '어디서 느려졌는지' 볼 수 있습니다."

## 이 글에서 다룰 문제

- 스팬과 트레이스는 각각 무엇일까요?
- 요청이 여러 서비스를 지날 때 문맥 전파는 왜 중요할까요?
- 샘플링은 왜 비용 통제의 핵심일까요?
- AI가 생성한 마이크로서비스에 트레이싱을 붙일 때 주의할 점은 무엇일까요?
- 트레이스와 로그를 어떻게 연결할까요?

---

바이브코딩으로 만든 결제 서비스가 갑자기 느려졌습니다. checkout → payment → external-gateway 순서로 세 서비스가 있는데, 어느 구간에서 시간이 걸리는지 로그만으로는 파악하기 어렵습니다. 메트릭은 "checkout API가 느리다"는 것만 알려줍니다.

트레이스가 있으면 checkout span: 2.4s, 그 중 payment span: 2.1s, 그 중 external-gateway span: 1.9s처럼 병목이 즉시 보입니다.

## 트레이싱 핵심 용어

| 용어 | 정의 | 역할 |
| --- | --- | --- |
| Span | 하나의 작업 구간 | 함수 호출, DB 쿼리, HTTP 요청 같은 개별 단위 |
| Trace | 전체 요청 흐름 | 여러 Span을 하나의 trace_id로 묶은 트리 |
| Context | 전파되는 메타데이터 | trace_id, span_id, 부모 span_id |
| Baggage | 사용자 정의 데이터 | 서비스 간 전달할 비즈니스 데이터 |

## OpenTelemetry로 HTTP 문맥 전파하기

AI에게 이 패턴으로 요청하면 서비스 간 trace_id 전달이 됩니다.

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry.propagate import inject, extract
import requests

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(ConsoleSpanExporter())
)
tracer = trace.get_tracer(__name__)

# 서비스 A: 서비스 B를 호출할 때 context를 헤더에 주입
def service_a_call():
    with tracer.start_as_current_span("service_a_request") as span:
        span.set_attribute("service.name", "service-a")

        headers = {}
        inject(headers)  # traceparent 헤더 추가

        response = requests.get("http://service-b/api", headers=headers)
        span.set_attribute("http.status_code", response.status_code)
        return response.json()

# 서비스 B: 수신한 헤더에서 context 복원
def service_b_handler(incoming_headers: dict):
    ctx = extract(incoming_headers)  # 헤더에서 trace_id 복원

    with tracer.start_as_current_span("service_b_request", context=ctx) as span:
        span.set_attribute("service.name", "service-b")
        return {"status": "ok"}
```

`inject()`는 현재 trace_id를 HTTP 헤더에 넣고, `extract()`는 헤더에서 trace_id를 꺼내서 연결합니다. 이 두 줄이 없으면 트레이스가 서비스 경계에서 끊깁니다.

## 바이브코딩 맥락: 비즈니스 구간 수동 계측

AI가 자동 계측을 붙여줘도, 결제, 재고 같은 비즈니스 핵심 구간은 수동 스팬으로 명시하는 것이 좋습니다.

```python
import time
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

tracer = trace.get_tracer("checkout-service")

def checkout(order_id: str, amount: int) -> None:
    with tracer.start_as_current_span("checkout") as root:
        root.set_attribute("order.id", order_id)
        root.set_attribute("order.amount", amount)

        with tracer.start_as_current_span("validate_order"):
            time.sleep(0.02)

        with tracer.start_as_current_span("charge_payment") as span:
            try:
                time.sleep(0.35)
                raise TimeoutError("gateway timeout")
            except TimeoutError as exc:
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR, str(exc)))
                span.set_attribute("payment.retry", 2)
                raise
```

AI에게 "checkout 함수에 OpenTelemetry 스팬 추가해줘, validate_order와 charge_payment를 별도 스팬으로 나누고, 타임아웃 시 ERROR 상태로 기록해줘"라고 요청하면 이 패턴을 받을 수 있습니다.

## 샘플링 전략: 비용 통제의 핵심

모든 트레이스를 100% 저장하면 바이브코딩 초기 스타트업에서는 비용이 감당하기 어려울 수 있습니다.

| 정책 | 비율 | 권장 환경 |
| --- | --- | --- |
| 100% 저장 | 전체 | 개발 환경, 초기 디버깅 |
| Head 10% | 무작위 10% | 스테이징 |
| 오류 100% + 지연 100% + 정상 5% | 조합 | 프로덕션 기본 |

```python
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

# 개발: 100%
# sampler = TraceIdRatioBased(1.0)

# 프로덕션: 10%
sampler = TraceIdRatioBased(0.1)
provider = TracerProvider(sampler=sampler)
```

## Before / After: 트레이싱 없을 때와 있을 때

**Before (트레이싱 없음)**

```text
에러 알림: checkout latency > 2s
→ checkout 서비스 로그 확인 (정상처럼 보임)
→ payment 서비스 로그 확인 (타임아웃 몇 줄)
→ external-gateway 로그 확인 (응답 없음 메시지)
→ 총 30분, 세 서비스 로그를 수동으로 대조
```

**After (트레이싱 있음)**

```text
에러 알림: checkout latency > 2s
→ 트레이스 열기: checkout 2.4s
   ├─ validate_order: 20ms (정상)
   ├─ charge_payment: 2.1s ← 병목
   │   └─ external_gateway_call: 1.9s
   └─ db_write: 150ms (정상)
→ external-gateway 문제가 즉시 확인됨
→ 총 3분
```

## 트레이스와 로그 연결

트레이스만 있고 로그에 trace_id가 없으면 "느린 구간의 상세 에러 메시지"를 볼 수 없습니다. 두 신호를 연결하는 핵심은 로그에 trace_id를 포함하는 것입니다.

```python
import structlog
from opentelemetry import trace

logger = structlog.get_logger()

def process_order(order_id: str):
    span = trace.get_current_span()
    ctx = span.get_span_context()

    log = logger.bind(
        trace_id=format(ctx.trace_id, "032x"),
        span_id=format(ctx.span_id, "016x"),
    )
    log.info("order_processing_start", order_id=order_id)
    # ... 비즈니스 로직 ...
    log.info("order_processing_end", order_id=order_id)
```

Grafana에서 Loki(로그)와 Tempo(트레이스)를 연결하면 로그의 trace_id를 클릭해서 트레이스 화면으로 바로 이동할 수 있습니다.

## 자주 하는 실수

| 실수 | 문제 | AI 코드에서 확인할 점 |
| --- | --- | --- |
| 문맥 전파 누락 | 트레이스가 서비스 경계에서 끊김 | inject/extract 쌍이 있는지 확인 |
| 100% 저장 | 비용 급증 | 프로덕션에 샘플링 설정 확인 |
| 스팬 속성 과다 | 카디널리티 증가 | 핵심 비즈니스 필드만 속성으로 |
| 비동기 코드에서 문맥 손실 | 부모-자식 관계 흐려짐 | asyncio.create_task 사용 확인 |
| 로그에 trace_id 없음 | 트레이스-로그 연결 불가 | 로그 코드에 trace_id 바인딩 확인 |

## AI 프롬프트 팁

```text
[분산 트레이싱 요청]
"이 마이크로서비스들에 OpenTelemetry 트레이싱 추가해줘:
1. FastAPIInstrumentor로 자동 계측
2. 서비스 A → B → C 호출 체인에서 traceparent 헤더로 context 전달
   (서비스 A에서 inject, 서비스 B에서 extract)
3. checkout, charge_payment 구간은 수동 스팬으로 명시
4. 오류 발생 시 span.record_exception() 호출
5. 로그에 trace_id, span_id 자동 포함
6. 프로덕션 샘플링: 오류/느린 요청 100% + 정상 10%"
```

## 운영 체크리스트

- [ ] 첫 스팬을 콘솔이나 백엔드에서 확인했습니다.
- [ ] 서비스 간 문맥 전파(inject/extract)가 동작합니다.
- [ ] 샘플링 비율을 환경에 따라 설정했습니다.
- [ ] 로그에 trace_id를 함께 남깁니다.
- [ ] AI 생성 코드에 inject/extract 누락이 없는지 확인합니다.

## 처음 질문으로 돌아가기

- **스팬과 트레이스는 각각 무엇일까요?**
  스팬은 하나의 작업 구간(DB 쿼리 하나, HTTP 호출 하나)이고, 트레이스는 여러 스팬을 하나의 trace_id로 묶은 전체 요청 흐름입니다.

- **요청이 여러 서비스를 지날 때 문맥 전파는 왜 중요할까요?**
  trace_id가 서비스 경계에서 끊기면 트레이스가 조각납니다. inject/extract로 HTTP 헤더에 trace_id를 실어서 다음 서비스로 전달해야 전체 흐름을 볼 수 있습니다.

- **샘플링은 왜 비용 통제의 핵심일까요?**
  초당 1000 요청이면 하루 8,600만 건의 트레이스가 생깁니다. 모두 저장하면 비용이 감당하기 어렵습니다. 오류/느린 요청만 선별 저장하면 가치는 유지하면서 비용은 줄입니다.

---

## 정리

분산 트레이싱은 바이브코딩으로 만든 여러 서비스를 하나의 요청 흐름으로 연결해서 봅니다. 스팬, 문맥 전파, 샘플링이 자리 잡으면 "어느 서비스가 느린가"를 분 단위가 아니라 초 단위로 알 수 있습니다. 다음 글에서는 이렇게 모인 신호를 어떤 화면으로 보여줘야 운영에 도움이 되는지, 대시보드 설계를 다룹니다.

## 참고 자료

- [OpenTelemetry tracing](https://opentelemetry.io/docs/concepts/signals/traces/)
- [W3C Trace Context](https://www.w3.org/TR/trace-context/)
- [Sampling strategies](https://opentelemetry.io/docs/concepts/sampling/)
- [Jaeger architecture](https://www.jaegertracing.io/docs/latest/architecture/)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Observability 기초 (1/10): 관측성이란 무엇인가?
- 바이브코딩을 위한 Observability 기초 (2/10): 메트릭, 로그, 트레이스
- 바이브코딩을 위한 Observability 기초 (3/10): 메트릭 수집과 시각화
- 바이브코딩을 위한 Observability 기초 (4/10): 구조화된 로깅
- **바이브코딩을 위한 Observability 기초 (5/10): 분산 트레이싱 기초 (현재 글)**
- 바이브코딩을 위한 Observability 기초 (6/10): 대시보드 설계
- 바이브코딩을 위한 Observability 기초 (7/10): 경보와 온콜
- 바이브코딩을 위한 Observability 기초 (8/10): 서비스 수준 지표와 목표 기초
- 바이브코딩을 위한 Observability 기초 (9/10): 비용과 카디널리티
- 바이브코딩을 위한 Observability 기초 (10/10): 운영 가능한 관측성 스택
<!-- toc:end -->

Tags: 바이브코딩, Observability, Tracing, OpenTelemetry, Microservices
