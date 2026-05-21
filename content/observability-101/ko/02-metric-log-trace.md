---
series: observability-101
episode: 2
title: "Observability 101 (2/10): 메트릭, 로그, 트레이스"
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
  - Metrics
  - Logging
  - Tracing
  - SRE
seo_description: 메트릭, 로그, 트레이스가 답하는 질문의 차이와 언제 무엇을 써야 하는지 정리합니다
last_reviewed: '2026-05-15'
---

# Observability 101 (2/10): 메트릭, 로그, 트레이스

관측성을 처음 배우면 세 신호를 모두 많이 모으면 된다고 생각하기 쉽습니다. 하지만 운영에서는 양보다 경계가 더 중요합니다. 어떤 질문은 메트릭으로 바로 답할 수 있고, 어떤 질문은 로그가 없으면 끝까지 설명되지 않으며, 어떤 질문은 트레이스가 없으면 위치를 찾기조차 어렵습니다.

신호를 잘못 고르면 두 가지가 동시에 나빠집니다. 비용은 커지고 답은 사라집니다. 그래서 메트릭, 로그, 트레이스를 각각 어떤 질문의 도구로 이해할지 먼저 정리해야 합니다.

이 글은 Observability 101 시리즈의 2번째 글입니다.

## 먼저 던지는 질문

- 메트릭, 로그, 트레이스는 각각 어떤 질문에 답할까요?
- 세 신호의 데이터 형태는 어떻게 다를까요?
- 카디널리티와 비용은 어디에서 커질까요?

## 큰 그림

![Observability 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/observability-101/02/02-01-concept-at-a-glance.ko.png)

*Observability 101 2장 흐름 개요*

메트릭, 로그, 트레이스 각각이 다른 질문에 답합니다. 어떤 값이 들어오고, 어느 구간이 느린지, 왜 실패했는지는 다른 신호로 봐야 합니다. 한 신호만으로는 불완전합니다.

> 메트릭, 로그, 트레이스는 각각을 빠르게 신호로 씁니다. 메트릭만 보면 증상을 보지만 왜를 찾을 수 없고, 로그만 머십으면 비용만 올라갑니다.

## 왜 중요한가

운영 비용이 커지는 팀을 보면 한 가지 패턴이 자주 보입니다. 모든 것을 로그에 넣거나, 반대로 메트릭만 잔뜩 그려 놓고 이유를 찾지 못합니다. 둘 다 신호의 경계를 구분하지 못해서 생기는 문제입니다.

메트릭, 로그, 트레이스의 역할을 정확히 구분하면 같은 돈으로 더 많은 답을 얻을 수 있습니다. 전체 추세는 메트릭으로, 사건의 맥락은 로그로, 요청 경로는 트레이스로 나누면 도구가 단순해지고 검색 시간도 줄어듭니다.

## 메트릭, 로그, 트레이스 비교

세 신호는 각각 다른 데이터 형태, 저장 비용, 질문 유형, 대표 도구를 가집니다.

| 구분 | 데이터 형태 | 저장 비용 | 질문 유형 | 대표 도구 |
| --- | --- | --- | --- | --- |
| 메트릭 | 시간별 숫자 | 낮음 (집계 가능) | 언제 얼마나? | Prometheus, Grafana |
| 로그 | 사건 + 맥락 필드 | 보통 | 왜 실패했나? | Loki, ELK, BigQuery |
| 트레이스 | 요청 경로 트리 | 높음 (샘플링 필수) | 어느 구간이 느린가? | Jaeger, Tempo |

비용을 보면 메트릭이 가장 저렴하고, 트레이스가 가장 비쌌니다. 그래서 운영에서는 메트릭으로 먼저 범위를 좌히고, 로그로 이유를 확인하고, 트레이스는 필요한 요청만 깊게 파는 순서를 따릅니다.

## 세 신호의 연결

메트릭, 로그, 트레이스는 각각 따로 보면 불완전하지만 함께 보면 한 줄의 이야기가 됩니다.

메트릭은 "언제부터 문제인가"를 보여 주고, 트레이스는 "어디서 문제인가"를 가리키고, 로그는 "왜 문제인가"를 설명합니다. 이 세 질문이 하나의 흐름으로 연결되는 순간, 장애는 예감이 아니라 추론이 됩니다.

예를 들어 결제 API가 느려졌다면:

1. 메트릭: 지난 10분간 p95 지연이 3배 증가
2. 트레이스: payment_gateway span이 전체 지연의 80% 차지
3. 로그: `{"event": "payment_timeout", "gateway": "stripe", "retry": 3}`

이 순서로 보면 증상, 위치, 이유가 한 줄로 연결됩니다. 세 신호를 따로 배우는 것보다 함께 연습하는 편이 훨씬 빠르게 운영 감각을 만듭니다.

## OpenTelemetry로 트레이스 스팬 생성하기

세 신호 가운데 트레이스가 가장 다루기 어렵습니다. 아래는 OpenTelemetry로 간단한 스팬을 남기는 Python 예제입니다.

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor

# 추적기 초기화
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(ConsoleSpanExporter())
)

tracer = trace.get_tracer(__name__)

# 스팬 생성
def process_payment(order_id: int):
    with tracer.start_as_current_span("payment_processing") as span:
        span.set_attribute("order.id", order_id)
        span.set_attribute("service.name", "payment-service")
        
        # 하위 스팬
        with tracer.start_as_current_span("db_query"):
            # DB 작업 시뮬레이션
            pass
        
        with tracer.start_as_current_span("external_api_call"):
            # 외부 API 호출 시뮬레이션
            pass
        
        return {"status": "success", "order_id": order_id}

# 사용
process_payment(12345)
```

이 코드를 실행하면 콘솔에 스팬 정보가 출력됩니다. 하나의 요청이 여러 구간으로 나뉘어지고, 각 구간의 시작과 끝이 기록됩니다. 나중에 느린 요청을 분석할 때 어느 스팬이 길었는지 한눈에 볼 수 있습니다.
## 한눈에 보는 구조

세 신호는 다른 질문에 답합니다. 전체 추세는 메트릭, 구체적 사건은 로그, 분산 경로는 트레이스로 봅니다. 한 신호만으로는 불완전합니다.

## 핵심 용어

- 카운터: 값이 계속 증가하는 메트릭입니다. 총 요청 수처럼 누적량을 표현할 때 씁니다.
- 게이지: 값이 오르내리는 메트릭입니다. 큐 길이, 메모리 사용량처럼 현재 상태를 나타냅니다.
- 히스토그램: 값의 분포를 보여 주는 메트릭입니다. p95, p99 같은 꼬리 지연을 계산할 때 중요합니다.
- 스팬: 트레이스 안의 한 구간입니다. 서비스 호출 하나, 데이터베이스 쿼리 하나가 스팬이 됩니다.
- 라벨: 신호에 붙이는 식별자입니다. 잘 쓰면 분류가 쉬워지지만, 과하면 비용이 폭증합니다.

## 바꾸기 전과 후

바꾸기 전에는 모든 사건을 로그에 밀어 넣습니다. 나중에 검색으로 다 찾으면 된다고 믿지만, 실제로는 검색이 느리고 비용도 커집니다. 반대로 메트릭만 보면 평균은 보이지만 왜 실패했는지 설명되지 않습니다.

바꾼 뒤에는 기준이 분명합니다. 전체 처리량과 에러율은 메트릭으로, 주문 한 건이 왜 실패했는지는 로그로, 특정 요청이 어느 서비스에서 오래 걸렸는지는 트레이스로 봅니다. 신호마다 맡는 질문이 달라지면 운영 판단도 빨라집니다.

## 세 신호를 함께 쓰는 순서

장애 대응에서 세 신호를 보는 순서가 중요합니다. 아래는 실제 장애 대응 흐름을 보여줍니다.

### 1단계: 메트릭으로 범위 좌히기

경보가 울렸을 때 가장 먼저 할 일은 전체 장애인지 일부 장애인지 확인하는 것입니다.

- 모든 엔드포인트의 에러율이 올랐나?
- 특정 경로만 느린가?
- 특정 지역이나 사용자 그룹에만 문제가 있는가?

이 질문들은 메트릭으로만 답할 수 있습니다. 로그를 보기 전에 메트릭으로 범위를 먼저 좌히면 불필요한 로그 검색을 피할 수 있습니다.

### 2단계: 트레이스로 위치 찾기

범위를 좌혔다면 다음은 어느 구간이 느린지 찾는 것입니다.

- 느린 요청 몸 건을 골라 트레이스를 평니다.
- 어느 스팬이 가장 오래 걸렸는지 확인합니다.
- 해당 스팬의 서비스 이름과 작업 이름을 기록합니다.

트레이스는 "어디"를 찾는 도구입니다. 서비스가 여럿일 때 트레이스 없이 책임 서비스를 찾기란 거의 불가능합니다.

### 3단계: 로그로 이유 확인

위치를 찾았다면 마지막으로 이유를 확인합니다.

- 트레이스에서 얻은 trace_id로 로그를 필터링합니다.
- 해당 구간의 ERROR 레벨 로그를 확인합니다.
- 에러 메시지, 스택 트레이스, 외부 API 응답을 확인합니다.

로그는 "왜"을 설명하는 도구입니다. 메트릭과 트레이스가 좌히고 가리켜 준 지점에서 로그가 이유를 말해 줍니다.

### 예시: 결제 API 장애

```text
1. 메트릭: payment_api p95 latency 180ms → 1.8s (10배 증가)
   ⇒ 전체 결제 API가 느림

2. 트레이스: trace_id=9f3c...
   payment_api span: 1.7s
     ├─ auth_check: 80ms
     ├─ card_gateway: 1.5s  ← 병목!
     └─ db_write: 120ms
   ⇒ card_gateway 호출이 문제

3. 로그: grep 'trace_id=9f3c' | grep ERROR
   {"level":"ERROR","event":"gateway_timeout","gateway":"stripe","timeout_ms":1500}
   ⇒ Stripe API가 1.5초 대기 후 타임아웃
```

이 세 단계를 거치면 "결제가 느리다"는 모호한 증상에서 "외부 결제사 API가 타임아웃"이라는 구체적인 원인으로 좋혀집니다.

## 실습: 세 신호를 다섯 단계로 비교하기

### 1단계 — 카운터

```python
http_requests_total = 0

def on_request():
    global http_requests_total
    http_requests_total += 1
```

카운터는 가장 단순한 메트릭입니다. 전체 처리량처럼 계속 누적되는 값을 기록할 때 적합합니다. 시스템이 바쁘고 한가한 흐름을 보는 첫 출발점이 됩니다.

### 2단계 — 히스토그램

```python
import time
buckets = {0.1: 0, 0.5: 0, 1.0: 0, "inf": 0}

def observe(d):
    for b in [0.1, 0.5, 1.0]:
        if d <= b: buckets[b] += 1; return
    buckets["inf"] += 1
```

평균만 보면 긴 꼬리를 놓치기 쉽습니다. 히스토그램은 요청 분포를 남겨 주기 때문에 p95와 p99를 볼 수 있습니다. 사용자는 평균이 아니라 느린 일부 요청을 기억한다는 점에서 특히 중요합니다.

### 3단계 — 구조화된 로그

```python
import json
def log(event, **f):
    print(json.dumps({"event": event, **f}))

log("payment_failed", order_id=42, reason="card_declined")
```

로그는 사건을 남깁니다. 결제가 왜 실패했는지, 어떤 주문 번호에서 어떤 사유가 나왔는지처럼 메트릭으로는 담기 어려운 맥락을 기록합니다. 운영에서 "왜"를 설명하는 재료는 대개 로그에 있습니다.

### 4단계 — 단순한 트레이스

```python
import uuid, time

def span(name, trace_id):
    s = time.time()
    log("span_start", trace_id=trace_id, name=name)
    yield
    log("span_end", trace_id=trace_id, name=name, dur=time.time()-s)
```

트레이스는 요청의 이동 경로를 보여 줍니다. 같은 trace_id 아래에서 시작과 끝을 남기면, 어느 구간이 길어졌는지와 어떤 서비스가 병목인지 읽을 수 있습니다.

### 5단계 — 선택 기준 세우기

```text
"overall throughput" → metric
"why this order failed" → log
"which service was slow for this request" → trace
```

결국 중요한 것은 선택 기준입니다. 처리량과 추세를 보고 싶으면 메트릭, 사건의 이유를 알고 싶으면 로그, 요청 경로를 따라가려면 트레이스를 고릅니다. 이 기준이 선명할수록 신호 설계가 단순해집니다.

## 주문 실패를 이렇게 나눠 봅니다

주문 API 오류가 늘었다면 세 신호를 한꺼번에 뒤지기보다 질문을 나눠 시작하는 편이 좋습니다.

```text
질문 1. 전체 실패율이 올라갔는가?         → metric
질문 2. 어떤 주문에서 어떤 이유로 실패했는가? → log
질문 3. 어느 서비스 호출이 가장 느렸는가?    → trace
```

예를 들어 아래처럼 세 단계로 보면, 같은 장애도 훨씬 짧은 시간 안에 설명할 수 있습니다.

```text
metric: 5xx ratio 0.4% → 6.2%
log: payment_failed reason=card_gateway_timeout
trace: checkout → payment-gateway span p95 2.4s
```

```text
Expected output:
- 메트릭은 장애 범위를 알려 줍니다.
- 로그는 실패 유형을 분류하게 해 줍니다.
- 트레이스는 느려진 위치를 특정하게 해 줍니다.
```

## 이 코드에서 먼저 봐야 할 점

- 카운터는 올라가기만 하고, 게이지는 오르내립니다.
- 히스토그램은 평균이 가리는 분포를 보여 줍니다.
- trace_id는 로그와 트레이스를 이어 주는 공통 키입니다.

## 자주 하는 실수 다섯 가지

1. 모든 것을 로그에 넣습니다. 검색 비용이 커지고 답을 찾는 시간도 길어집니다.
2. 카운터와 게이지를 혼동합니다. 그래프가 의미를 잃습니다.
3. 평균만 봅니다. 긴 꼬리 지연이 숨겨집니다.
4. user_id 같은 고유값을 라벨에 넣습니다. 카디널리티가 폭발합니다.
5. 트레이스만 보고 메트릭을 무시합니다. 전체 추세를 놓칩니다.

## 실무에서는 이렇게 생각한다

대부분의 팀은 메트릭으로 경보를 만들고, 로그로 디버깅하고, 트레이스로 원인 서비스를 찾습니다. 세 신호가 같은 정보를 세 번 저장하는 구조는 오래 버티지 못합니다. 질문 영역을 나누는 순간부터 비용과 운영 시간이 함께 줄어듭니다.

시니어 엔지니어가 특히 먼저 보는 것은 경계입니다. 어떤 질문을 메트릭으로 풀고, 어떤 질문을 로그로 넘기고, 어떤 문제에만 트레이스를 깊게 쓰는지 합의가 있으면 시스템이 커져도 신호 설계가 덜 흔들립니다.

## 체크리스트

- [ ] 카운터, 게이지, 히스토그램의 차이를 설명할 수 있습니다.
- [ ] 카디널리티가 왜 비용과 연결되는지 이해합니다.
- [ ] trace_id의 역할을 설명할 수 있습니다.
- [ ] 질문에 따라 어떤 신호를 먼저 볼지 결정할 수 있습니다.

## 연습 문제

1. 카운터와 게이지의 예를 각각 세 개씩 적어 보세요.
2. 평균이 p99를 가리는 사례를 하나 설명해 보세요.
3. 세 개의 서비스를 거치는 요청에서 trace_id가 어떻게 이어질지 스케치해 보세요.

## 정리

메트릭, 로그, 트레이스는 같은 신호의 세 버전이 아닙니다. 각자 답하는 질문이 다르고, 함께 써야 비로소 운영의 흐름이 보입니다. 다음 글에서는 이 가운데 메트릭을 실제로 어떻게 수집하고 그래프로 만드는지 살펴보겠습니다.

## 언제 어떤 신호를 먼저 볼까

장애 대응 시간을 줄이려면 "항상 메트릭부터" 같은 고정 규칙보다, 질문 유형에 맞춰 시작점을 고르는 편이 효과적입니다.

| 시작 질문 | 1차 신호 | 2차 신호 | 3차 신호 | 이유 |
| --- | --- | --- | --- | --- |
| 전체 품질이 흔들렸는가 | 메트릭 | 트레이스 | 로그 | 범위 확인이 먼저 필요합니다. |
| 특정 주문이 왜 실패했는가 | 로그 | 트레이스 | 메트릭 | 사건 맥락이 먼저 필요합니다. |
| 특정 호출이 왜 느린가 | 트레이스 | 로그 | 메트릭 | 병목 구간 식별이 핵심입니다. |
| 배포 영향이 있었는가 | 메트릭 | 로그 | 트레이스 | 시점 비교가 우선입니다. |

중요한 점은 한 신호로 끝내지 않는 것입니다. 메트릭에서 이상을 봤다면 같은 시간축으로 트레이스를 열고, 같은 trace_id로 로그를 확인해야 결론이 완성됩니다. 반대로 로그에서 에러 원인을 봤다면 메트릭으로 영향 범위를 측정해 "몇 명에게 영향을 줬는가"를 확인해야 합니다.

## 상관관계 필드 설계 예시

신호 간 연결이 약한 팀은 보통 필드 설계가 들쭉날쭉합니다. 아래처럼 공통 필드를 정하면 대시보드, 로그 저장소, 트레이스 백엔드가 같은 요청을 가리키게 됩니다.

```python
import json
import time
from typing import Dict

COMMON_FIELDS = [
    "ts", "service", "env", "trace_id", "span_id", "request_id",
    "route", "status_code", "error_code"
]


def write_log(event: str, fields: Dict[str, object]) -> None:
    payload = {
        "ts": time.time(),
        "event": event,
        **fields,
    }
    print(json.dumps(payload, ensure_ascii=False))


write_log(
    "payment_failed",
    {
        "service": "checkout-api",
        "env": "prod",
        "trace_id": "9f3c1f9e...",
        "span_id": "5a8b...",
        "request_id": "req-42",
        "route": "/checkout",
        "status_code": 502,
        "error_code": "UPSTREAM_TIMEOUT",
    },
)
```

운영에서는 필드 수를 늘리는 것보다 필드 의미를 고정하는 편이 더 중요합니다. 서비스마다 `requestId`, `req_id`, `rid`를 섞어 쓰면 질의 템플릿을 재사용할 수 없습니다. 팀 공통 사전을 먼저 만들고, 신규 서비스는 그 사전을 그대로 따르게 하는 정책이 유지보수에 유리합니다.

## 세 신호 비교: 의사결정 관점

| 신호 | 강점 | 약점 | 비용 위험 | 실무 권장 |
| --- | --- | --- | --- | --- |
| 메트릭 | 빠른 집계, 넓은 범위 감시 | 사건 맥락 부족 | 고카디널리티 라벨 | 증상 감지 기본 신호 |
| 로그 | 실패 원인, 도메인 맥락 | 저장량 증가, 검색 비용 | 본문 과다, 민감정보 | 원인 설명 핵심 신호 |
| 트레이스 | 요청 경로, 병목 위치 | 샘플링 없으면 고비용 | 100% 저장, 속성 과다 | 병목 분석 핵심 신호 |

운영 성숙도가 높아질수록 신호별 담당 질문이 선명해집니다. 예를 들어 "p95가 상승했다"는 알림은 메트릭 담당, "어느 span이 길어졌는가"는 트레이스 담당, "왜 timeout이 났는가"는 로그 담당으로 역할을 나누면 회의 시간이 짧아집니다.

## 처음 질문으로 돌아가기

- **메트릭, 로그, 트레이스는 각각 어떤 질문에 답할까요?**
  - 메트릭은 추세를 답고, 로그는 사건의 맥락을 답하며, 트레이스는 요청 경로 전체를 봅니다. 메트릭 몇 개나 로그 한 줄로는 불완전합니다.
- **세 신호의 데이터 형태는 어떻게 다를까요?**
  - 메트릭은 숫자만 볼 수 있고, 로그는 문맥 데이터를 남길 수 있으며, 트레이스는 흐름을 계속 본다는 중요합니다.
- **카디널리티와 비용은 어디에서 커질까요?**
  - 라벨을 많이 내면 만들어진 메트릭 종류가 많으면 처리 비용도 많습니다. 보존 기간도 길어지면 비용도 마른다니다. 처음부터 비용 개념으로 빌도고, 라벨 개수를 줄입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Observability 101 (1/10): 관측성이란 무엇인가?](./01-what-is-observability.md)
- **메트릭, 로그, 트레이스 (현재 글)**
- 메트릭 수집과 시각화 (예정)
- 구조화된 로깅 (예정)
- 분산 트레이싱 기초 (예정)
- 대시보드 설계 (예정)
- 경보와 온콜 (예정)
- 서비스 수준 지표와 목표 기초 (예정)
- 비용과 카디널리티 (예정)
- 운영 가능한 관측성 스택 (예정)

<!-- toc:end -->

## 참고 자료

- [Prometheus metric types](https://prometheus.io/docs/concepts/metric_types/)
- [Structured logging](https://www.datadoghq.com/blog/structured-logging/)
- [OpenTelemetry traces](https://opentelemetry.io/docs/concepts/signals/traces/)
- [Histograms vs averages](https://prometheus.io/docs/practices/histograms/)

Tags: Observability, Metrics, Logging, Tracing, SRE
