---
series: observability-101
episode: 5
title: "Observability 101 (5/10): 분산 트레이싱 기초"
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
  - Tracing
  - OpenTelemetry
  - SRE
  - Microservices
seo_description: span, trace, context propagation과 OpenTelemetry로 첫 추적을 만드는 흐름을 설명합니다
last_reviewed: '2026-05-15'
---

# Observability 101 (5/10): 분산 트레이싱 기초

메트릭으로는 느려졌다는 사실을 볼 수 있고, 로그로는 어떤 사건이 있었는지 읽을 수 있습니다. 그런데 요청 하나가 다섯 개 서비스와 두 개 저장소를 거친 뒤 실패했다면, 어느 구간이 병목이었는지 찾는 일은 여전히 어렵습니다.

분산 트레이싱은 이 빈칸을 메웁니다. 요청 하나를 여러 구간으로 나눠 기록하고, 그 구간들을 하나의 흐름으로 묶어 주면 어디서 오래 걸렸는지 바로 보이기 시작합니다.

이 글은 Observability 101 시리즈의 5번째 글입니다.

## 먼저 던지는 질문

- 스팬과 트레이스는 각각 무엇일까요?
- 요청이 여러 서비스를 지날 때 문맥 전파는 왜 중요할까요?
- 샘플링은 왜 비용 통제의 핵심일까요?

## 큰 그림

![Observability 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/observability-101/05/05-01-concept-at-a-glance.ko.png)

*Observability 101 5장 흐름 개요*

분산 트레이싱 기초를 다루는 이번 장에서는 주요 개념과 실무 패턴을 봅니다. 시스템이 복잡해질수록 이 개념들이 어디에서 시작되고 어떤 결과를 만드는지 이해하는 것이 중요합니다.

> 분산 트레이싱 기초의 핵심은 도구 선택이 아니라, 언제 어디서 이 신호를 남기고 어떻게 해석할 것인가 하는 설계입니다.

## 왜 중요한가

마이크로서비스 환경에서는 느린 요청의 원인을 로그만으로 찾기 어렵습니다. 서비스 A의 로그는 정상처럼 보이고, 서비스 B의 로그도 큰 문제가 없어 보이는데, 실제로는 둘 사이 호출이 길어졌을 수 있습니다. 메트릭도 어느 시점부터 느려졌는지는 알려 주지만, 한 요청이 어디에서 막혔는지는 설명하지 못합니다.

분산 트레이싱이 필요한 이유는 요청을 전체 흐름으로 보기 위해서입니다. 하나의 요청이 어떤 서비스와 데이터베이스를 거쳤고, 어느 스팬이 길었고, 어떤 부모-자식 관계로 이어졌는지를 한눈에 보여 주면 원인 파악 시간이 크게 줄어듭니다.

## 트레이싱 용어 정리

분산 트레이싱에는 몇 가지 핵심 용어가 있습니다. 이 용어를 정확히 이해하면 트레이스 화면을 읽는 속도가 빨라집니다.

| 용어 | 정의 | 역할 |
| --- | --- | --- |
| Span | 하나의 작업 구간 | 함수 호출, DB 쿼리, HTTP 요청 같은 개별 단위 |
| Trace | 전체 요청 흐름 | 여러 Span을 하나의 trace_id로 묶은 트리 |
| Context | 전파되는 메타데이터 | trace_id, span_id, 부모 span_id 같은 식별자 |
| Baggage | 사용자 정의 데이터 | 서비스 간 전달할 비즈니스 데이터 (user_id, tenant_id 등) |

Context는 표준 식별자를 전파하고, Baggage는 애플리케이션이 필요한 임의의 데이터를 전파합니다. Baggage는 편리하지만 모든 서비스 호출에 실려 다니므로 과도하게 쓰면 오버헤드가 커집니다.

## OpenTelemetry로 HTTP 문맥 전파하기

분산 트레이싱의 핵심은 서비스 사이에서 trace_id를 끊지 않고 전달하는 것입니다. 아래는 OpenTelemetry로 HTTP 헤더를 통해 문맥을 전파하는 예제입니다.

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry.propagate import inject, extract
import requests

# Tracer 초기화
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(ConsoleSpanExporter())
)
tracer = trace.get_tracer(__name__)

# 서비스 A: 외부 API 호출
def service_a_call_external():
    with tracer.start_as_current_span("service_a_request") as span:
        span.set_attribute("service.name", "service-a")
        
        # Context를 헤더에 주입
        headers = {}
        inject(headers)
        
        # 서비스 B 호출
        response = requests.get("http://service-b/api", headers=headers)
        span.set_attribute("http.status_code", response.status_code)
        
        return response.json()

# 서비스 B: 수신한 요청 처리
def service_b_handler(incoming_headers: dict):
    # 헤더에서 Context 추출
    ctx = extract(incoming_headers)
    
    # 추출한 Context를 현재 Span의 부모로 설정
    with tracer.start_as_current_span("service_b_request", context=ctx) as span:
        span.set_attribute("service.name", "service-b")
        
        # 비즈니스 로직
        result = {"status": "ok"}
        
        return result

# 사용 예시
if __name__ == "__main__":
    # 서비스 A가 서비스 B를 호출
    # 실제로는 두 서비스가 별도 프로세스이지만,
    # 여기서는 개념 설명을 위해 한 코드에 모았음
    print("서비스 A가 서비스 B를 호출하고, trace_id가 전파됩니다.")
```

이 코드에서 `inject()`는 현재 Context를 HTTP 헤더에 넣고, `extract()`는 헤더에서 Context를 꺼냅니다. W3C Trace Context 표준에 따라 `traceparent` 헤더가 생성되고, 서비스 B는 이를 읽어 같은 트레이스로 이어갑니다.

## 샘플링 전략

모든 트레이스를 100% 저장하면 비용이 급격히 커집니다. 샘플링은 일부만 저장하는 전략입니다.

### Head-based Sampling

**정의**: 트레이스 시작 시점에 저장 여부를 결정합니다.

**장점**:
- 구현이 간단합니다.
- 시스템 부하가 적습니다.
- 예측 가능한 비용입니다.

**단점**:
- 느린 요청이나 오류를 놓칠 수 있습니다.
- 희귀한 문제를 포착하기 어렵습니다.

```python
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

# 10%만 저장
sampler = TraceIdRatioBased(0.1)
provider = TracerProvider(sampler=sampler)
```

### Tail-based Sampling

**정의**: 트레이스 종료 후 결과를 보고 저장 여부를 결정합니다.

**장점**:
- 느린 요청이나 오류를 선택적으로 저장할 수 있습니다.
- 중요한 트레이스를 놓치지 않습니다.

**단점**:
- 구현이 복잡합니다 (모든 span을 메모리에 모아야 함).
- 시스템 부하가 큽니다.

**사용 예시**:
- 응답 시간이 1초 이상인 트레이스만 저장
- HTTP 5xx 상태 코드가 포함된 트레이스만 저장
- 특정 경로 (`/api/payment`)만 100% 저장

### 실무 추천

1. **개발 환경**: 100% 저장 (전체 흐름 확인)
2. **스테이징**: 10% head-based sampling
3. **프로덕션**: 1% head-based + tail-based (error/slow 요청)

글로벌 트래픽이 매일 백만 건이 넘는다면 1% 샘플링에도 일만 건의 트레이스가 쌓입니다. 샘플링 비율은 트래픽과 비용을 보고 조정합니다.

## 한눈에 보는 구조

분산 트레이싱은 하나의 요청이 여러 서비스를 거칠 때 그 경로 전체를 한 줄로 봅니다. trace_id로 요청을 추적하고, span으로 각 구간을 기록합니다.

## 핵심 용어

- 트레이스: 하나의 요청 전체 흐름입니다.
- 스팬: 트레이스 안의 개별 구간입니다.
- 부모와 자식: 스팬 사이의 호출 관계입니다.
- 문맥 전파: trace_id 같은 정보를 헤더로 전달해 다음 서비스가 같은 요청으로 이어받게 하는 과정입니다.
- 샘플링: 모든 트레이스를 저장하지 않고 일부만 남기는 전략입니다.

## 바꾸기 전과 후

바꾸기 전에는 로그를 검색하며 어느 서비스가 느렸는지 추측합니다. 같은 요청의 로그를 겨우 모아도 실제 병목 구간을 확신하기 어렵습니다.

바꾼 뒤에는 트레이스 화면에서 느린 스팬이 바로 보입니다. 어느 서비스 호출이 길었는지, 부모 스팬과 자식 스팬이 어떻게 이어졌는지 한눈에 읽을 수 있습니다.

## 실습: 첫 트레이스를 다섯 단계로 만들기

### 1단계 — 추적 라이브러리 설치

```bash
pip install opentelemetry-api opentelemetry-sdk \
            opentelemetry-exporter-otlp
```

첫 단계는 표준 도구를 준비하는 일입니다. OpenTelemetry는 수집 표준을 통일해 주기 때문에, 나중에 백엔드를 바꾸더라도 코드 구조를 크게 흔들지 않게 도와줍니다.

### 2단계 — 추적기 설정

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor, ConsoleSpanExporter)

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(ConsoleSpanExporter()))
tracer = trace.get_tracer("app")
```

추적기를 초기화하면 애플리케이션이 스팬을 만들 수 있습니다. 처음에는 콘솔 출력만으로도 흐름을 이해하기에 충분합니다.

### 3단계 — 첫 스팬 만들기

```python
with tracer.start_as_current_span("handle_request") as s:
    s.set_attribute("user_id", 42)
    with tracer.start_as_current_span("db_query"):
        pass
```

한 요청을 상위 스팬과 하위 스팬으로 나누면 호출 구조가 드러납니다. 어느 구간이 자식 스팬인지 보이기 시작하면 병목 위치를 훨씬 빨리 좁힐 수 있습니다.

### 4단계 — 문맥 전파하기

```python
from opentelemetry.propagate import inject, extract

headers = {}
inject(headers)                  # before call: inject trace_id
ctx = extract(incoming_headers)  # at receiver: restore from headers
```

문맥 전파가 빠지면 트레이스는 중간에서 끊깁니다. 서비스가 둘 이상이면 헤더로 trace_id를 넘기는 일은 선택이 아니라 기본입니다.

### 5단계 — 샘플링 걸기

```python
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
TracerProvider(sampler=TraceIdRatioBased(0.1))   # 10% only
```

모든 트레이스를 100% 저장하면 비용이 빠르게 커집니다. 샘플링은 부끄러운 절충이 아니라, 분산 트레이싱을 오래 운영하기 위한 기본 장치입니다.

## 느린 요청을 이렇게 검증합니다

분산 트레이싱은 단순히 예쁜 그래프를 보는 도구가 아닙니다. 느린 요청 하나를 고르고, 어떤 스팬이 시간을 가장 많이 썼는지 확인하는 절차가 있어야 값이 생깁니다.

```text
trace_id=9f3c...
handle_request  2450ms
├─ auth_check    120ms
├─ payment_call 1980ms
└─ db_write      210ms
```

이 정도만 보여도 병목이 애플리케이션 전체인지, 특정 하위 호출인지 바로 갈립니다. 여기에 같은 trace_id 로그를 붙이면 원인 후보를 더 빠르게 좁힐 수 있습니다.

```text
Expected output:
- 루트 스팬과 하위 스팬의 시간 차이가 보입니다.
- 가장 긴 payment_call 스팬이 병목 후보로 드러납니다.
- 같은 trace_id 로그에서 timeout, retry, upstream status 같은 맥락을 확인할 수 있습니다.
```

## 이 코드에서 먼저 봐야 할 점

- 하나의 트레이스는 여러 스팬으로 이루어진 트리입니다.
- `traceparent` 헤더는 문맥 전파의 표준입니다.
- 샘플링 비율은 곧 비용과 가치의 균형점입니다.

## 자주 하는 실수 다섯 가지

1. 모든 트레이스를 100% 저장합니다. 비용이 빠르게 폭증합니다.
2. 문맥 전파를 빼먹습니다. 트레이스가 중간에서 끊깁니다.
3. 스팬 속성을 너무 많이 붙입니다. 카디널리티가 커집니다.
4. 비동기 코드에서 문맥을 잃습니다. 부모-자식 관계가 흐려집니다.
5. 트레이스만 보고 메트릭을 무시합니다. 전체 추세를 놓칩니다.

## 실무에서는 이렇게 생각한다

실무에서는 OpenTelemetry로 수집한 트레이스를 Tempo, Jaeger, Honeycomb 같은 백엔드로 보내고, 로그와 메트릭과 연결해서 봅니다. 이 연결이 있어야 느린 요청 하나를 전체 흐름 속에서 읽을 수 있습니다.

시니어 엔지니어는 스팬 이름과 문맥 전파를 특히 신경 씁니다. 이름이 제각각이면 읽기가 어렵고, 전파가 끊기면 트레이스 자체가 신뢰를 잃습니다. 좋은 트레이싱은 도구보다 일관성에서 나옵니다.

## 체크리스트

- [ ] 첫 스팬을 콘솔이나 백엔드에서 확인했습니다.
- [ ] `traceparent` 헤더의 역할을 이해합니다.
- [ ] 샘플링 비율을 정했습니다.
- [ ] 로그에 trace_id를 함께 남깁니다.

## 연습 문제

1. 두 서비스 사이에 문맥 전파를 연결해 보세요.
2. 환경별로 다른 샘플링 비율을 설계해 보세요.
3. 가장 느린 스팬을 찾는 질의를 하나 구상해 보세요.

## 정리

분산 트레이싱은 요청 하나의 흐름을 지도처럼 보여 줍니다. 스팬, 문맥 전파, 샘플링이 자리 잡으면 여러 서비스를 가로지르는 장애도 훨씬 빨리 좁힐 수 있습니다. 다음 글에서는 이렇게 모인 신호를 어떤 화면으로 보여 줘야 운영에 도움이 되는지, 대시보드 설계를 다루겠습니다.

## OpenTelemetry Python 계측 확장 예시

자동 계측만으로는 도메인 경계를 충분히 표현하기 어려운 경우가 많습니다. 결제, 재고, 쿠폰 같은 비즈니스 구간은 수동 스팬을 추가해 의미를 분명히 하는 편이 좋습니다.

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

스팬 이름은 이후 검색 키가 되므로 짧고 일관되게 유지합니다. 같은 동작을 `pay`, `payment_call`, `charge_gateway`처럼 섞어 쓰면 팀 전체 질의 품질이 떨어집니다.

## 문맥 전파 실전 패턴

서비스 간 호출에서 문맥 전파가 누락되는 지점은 주로 비HTTP 경계(큐, 배치, 비동기 작업)입니다. 아래 예시는 HTTP 헤더와 메시지 큐를 함께 다루는 단순 패턴입니다.

```python
from opentelemetry.propagate import inject, extract


def build_http_headers() -> dict:
    headers = {}
    inject(headers)
    return headers


def publish_message(payload: dict) -> dict:
    carrier = {}
    inject(carrier)
    return {
        "payload": payload,
        "trace_headers": carrier,
    }


def consume_message(message: dict):
    ctx = extract(message["trace_headers"])
    tracer = trace.get_tracer("worker")
    with tracer.start_as_current_span("worker.handle", context=ctx):
        # 실제 처리
        pass
```

메시지 시스템에서는 헤더 필드 이름 표준을 팀 문서로 고정해야 합니다. 생산자와 소비자가 다른 언어를 쓰는 경우가 많아서, 한쪽에서만 규칙을 알고 있으면 트레이스가 중간에서 끊깁니다.

## 샘플링 정책 설계 가이드

| 정책 | 장점 | 단점 | 권장 상황 |
| --- | --- | --- | --- |
| 100% 저장 | 디버깅 정보 최대 | 비용 급증 | 개발/단기 실험 |
| Head 10% | 단순, 예측 가능 | 희귀 오류 누락 가능 | 트래픽이 큰 정상 구간 |
| Tail (오류/지연 우선) | 가치 높은 트레이스 보존 | 설정 복잡 | 운영 환경 기본 |

추천 시작점은 "오류 100% + 지연 100% + 정상 5%"입니다. 이 조합이면 비용을 통제하면서도 장애 분석에 필요한 표본을 충분히 확보할 수 있습니다. 샘플링은 한 번 정하고 끝내는 설정이 아니라, 월별 트래픽과 장애 패턴에 맞춰 조정하는 운영 항목입니다.

## 처음 질문으로 돌아가기

- **스팬과 트레이스는 각각 무엇일까요?**
  - 본문의 기준은 분산 트레이싱 기초를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **요청이 여러 서비스를 지날 때 문맥 전파는 왜 중요할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **샘플링은 왜 비용 통제의 핵심일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Observability 101 (1/10): 관측성이란 무엇인가?](./01-what-is-observability.md)
- [Observability 101 (2/10): 메트릭, 로그, 트레이스](./02-metric-log-trace.md)
- [Observability 101 (3/10): 메트릭 수집과 시각화](./03-metric-collection.md)
- [Observability 101 (4/10): 구조화된 로깅](./04-structured-logging.md)
- **분산 트레이싱 기초 (현재 글)**
- 대시보드 설계 (예정)
- 경보와 온콜 (예정)
- 서비스 수준 지표와 목표 기초 (예정)
- 비용과 카디널리티 (예정)
- 운영 가능한 관측성 스택 (예정)

<!-- toc:end -->

## 참고 자료

- [OpenTelemetry tracing](https://opentelemetry.io/docs/concepts/signals/traces/)
- [W3C Trace Context](https://www.w3.org/TR/trace-context/)
- [Jaeger architecture](https://www.jaegertracing.io/docs/latest/architecture/)
- [Sampling strategies](https://opentelemetry.io/docs/concepts/sampling/)

Tags: Observability, Tracing, OpenTelemetry, SRE, Microservices
