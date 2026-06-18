---
series: observability-101
episode: 2
title: "바이브코딩을 위한 Observability 기초 (2/10): 메트릭, 로그, 트레이스"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Observability
  - Metrics
  - Logging
  - Tracing
seo_description: 바이브코딩으로 만든 서비스에서 메트릭, 로그, 트레이스가 각각 어떤 질문에 답하는지, 언제 무엇을 써야 하는지 정리합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 Observability 기초 (2/10): 메트릭, 로그, 트레이스

이 글은 **바이브코딩을 위한 Observability 기초** 시리즈의 두 번째 글입니다. AI와 함께 만든 서비스를 프로덕션에서 운영할 때, 세 신호를 어디에 써야 하는지 정확히 이해하면 비용은 줄고 장애 대응 속도는 빨라집니다.

---

관측성을 처음 배우면 세 신호를 모두 많이 모으면 된다고 생각하기 쉽습니다. 하지만 운영에서는 양보다 경계가 더 중요합니다. 바이브코딩으로 빠르게 만든 서비스일수록, 신호를 잘못 선택하면 비용은 커지고 답은 사라지는 상황이 됩니다.

AI에게 "모니터링 붙여줘"라고 하면 로그, 메트릭, 트레이스를 전부 다 달아주는 경우가 있습니다. 하지만 그것이 실제로 원하는 질문에 답하는지는 별개입니다.

> "메트릭, 로그, 트레이스를 각각 어떤 질문의 도구로 이해할지 먼저 정해야, AI에게 올바른 관측성 코드를 요청할 수 있습니다."

## 이 글에서 다룰 문제

- 메트릭, 로그, 트레이스는 각각 어떤 질문에 답할까요?
- 세 신호의 데이터 형태는 어떻게 다를까요?
- 카디널리티와 비용은 어디에서 커질까요?
- 바이브코딩 서비스에서 신호를 잘못 배분하면 어떤 문제가 생길까요?
- 처음 관측성을 붙일 때 가장 흔한 실수는 무엇일까요?

---

AI에게 "로그 남겨줘"라고 하면 모든 것을 로그에 넣습니다. 그러면 검색 비용이 커지고 답을 찾는 시간도 길어집니다. 반대로 "메트릭만 붙여줘"라고 하면 추세는 보이지만 왜 실패했는지는 설명이 안 됩니다.

세 신호의 역할을 정확히 구분하면, AI에게 더 좋은 프롬프트를 줄 수 있고, 같은 돈으로 더 많은 답을 얻을 수 있습니다.

## 세 신호 비교

| 구분 | 데이터 형태 | 저장 비용 | 질문 유형 | 대표 도구 |
| --- | --- | --- | --- | --- |
| 메트릭 | 시간별 숫자 | 낮음 (집계 가능) | 언제 얼마나? | Prometheus, Grafana |
| 로그 | 사건 + 맥락 필드 | 보통 | 왜 실패했나? | Loki, ELK |
| 트레이스 | 요청 경로 트리 | 높음 (샘플링 필수) | 어느 구간이 느린가? | Jaeger, Tempo |

비용을 보면 메트릭이 가장 저렴하고 트레이스가 가장 비쌉니다. 메트릭으로 먼저 범위를 좁히고, 로그로 이유를 확인하고, 트레이스는 필요한 요청만 깊게 파는 순서를 따르는 이유가 여기 있습니다.

## 바이브코딩 관점: 세 신호를 어떻게 나눌까

AI가 만든 서비스의 일반적인 패턴으로 구분하면 다음과 같습니다.

```text
집계해도 의미 있는 숫자 → 메트릭
  예: 초당 요청 수, 에러율, p95 지연 시간

개별 사건의 맥락이 필요한 데이터 → 로그
  예: 어떤 주문이 왜 실패했는지, 어떤 사용자가 어떤 에러를 만났는지

요청 경로와 구간별 소요 시간 → 트레이스
  예: checkout → payment → DB 순서로 어디서 시간이 걸렸는지
```

AI에게 관측성을 요청할 때 이 구분을 명확히 하면 훨씬 정확한 코드를 받습니다.

## OpenTelemetry로 세 신호 함께 내보내기

바이브코딩에서 가장 효율적인 접근은 OpenTelemetry를 처음부터 붙이는 것입니다. 하나의 SDK로 세 신호를 모두 내보낼 수 있기 때문입니다.

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

        with tracer.start_as_current_span("db_query"):
            pass  # DB 작업

        with tracer.start_as_current_span("external_api_call"):
            pass  # 외부 API 호출

        return {"status": "success", "order_id": order_id}

process_payment(12345)
```

이 코드는 AI에게 "checkout 함수에 OpenTelemetry 트레이스 추가해줘, order.id와 service.name 속성 포함"이라고 요청하면 비슷한 결과를 받을 수 있습니다.

## 카디널리티: AI가 실수하기 쉬운 지점

AI가 메트릭 코드를 짤 때 가장 흔한 실수는 user_id나 order_id를 라벨에 넣는 것입니다.

```text
# AI가 잘못 짤 수 있는 패턴 (절대 하지 말것)
http_requests_total{user_id="u-123456", path="/checkout"}
http_requests_total{user_id="u-123457", path="/checkout"}
# → 사용자 수만큼 시계열이 생겨 비용 폭발

# 올바른 패턴
http_requests_total{path="/checkout", status="200"}
# user_id는 로그에 남긴다
```

AI에게 메트릭 코드를 요청할 때는 "user_id나 request_id는 라벨에 넣지 말고, 유한한 값만 라벨로 써줘"라는 조건을 항상 포함하는 것이 좋습니다.

## Before / After: 신호 경계 없을 때와 있을 때

**Before (신호 경계 없음)**

```text
모든 것을 로그에 넣음
→ 하루 100GB 로그
→ 특정 사용자 실패 찾는 데 grep 5분
→ 에러율 추세는 로그 집계로 계산 (느리고 비쌈)
→ 어느 서비스 호출이 느린지 알 수 없음
```

**After (신호 경계 있음)**

```text
처리량/에러율/지연 → 메트릭 (초당 집계, 빠른 질의)
주문 실패 이유, user_id → 로그 (필드 기반 검색)
결제 → payment → DB 흐름 → 트레이스 (병목 위치 파악)
```

## 자주 하는 실수

| 실수 | 문제 | 바이브코딩 맥락 |
| --- | --- | --- |
| 모든 것을 로그에 넣음 | 검색 비용 급증 | AI가 기본적으로 로그 중심으로 짜는 경향 |
| user_id를 메트릭 라벨에 넣음 | 카디널리티 폭발 | AI가 "유용하겠다"고 판단해 넣는 경우 많음 |
| 평균만 봄 | 긴 꼬리 지연 숨겨짐 | 사용자는 느린 1%를 경험함 |
| 트레이스만 보고 메트릭 무시 | 전체 추세 놓침 | 개별 요청은 보이지만 전체 상황 파악 어려움 |
| 카운터와 게이지 혼동 | 그래프 의미 없어짐 | AI가 타입을 잘못 선택하는 경우 있음 |

## AI 프롬프트 팁

```text
[메트릭 코드 요청 시]
"Prometheus 메트릭 추가해줘. 단,
- user_id, order_id, request_id는 라벨로 쓰지 말 것
- 유한한 값만 라벨로 사용 (method, status_code, path_pattern)
- Counter는 요청 수/에러 수에, Histogram은 응답 시간에 사용
- p95, p99를 계산할 수 있도록 Histogram 버킷 설정"

[로그 코드 요청 시]
"구조화된 JSON 로그 추가해줘.
- trace_id, request_id 필드 포함
- 개인정보(email, 전화번호)는 마스킹
- ERROR 레벨은 즉시 경보 연결 예정"
```

## 운영 체크리스트

- [ ] 카운터, 게이지, 히스토그램의 차이를 설명할 수 있습니다.
- [ ] 카디널리티가 왜 비용과 연결되는지 이해합니다.
- [ ] trace_id의 역할을 설명할 수 있습니다.
- [ ] 질문에 따라 어떤 신호를 먼저 볼지 결정할 수 있습니다.
- [ ] AI에게 메트릭 코드 요청 시 카디널리티 제약을 명시합니다.

## 처음 질문으로 돌아가기

- **메트릭, 로그, 트레이스는 각각 어떤 질문에 답할까요?**
  메트릭은 "언제 얼마나", 로그는 "왜 실패했나", 트레이스는 "어느 구간이 느린가"에 답합니다. 각 신호는 서로 보완 관계입니다.

- **카디널리티와 비용은 어디에서 커질까요?**
  user_id, order_id 같은 고유값을 메트릭 라벨에 넣으면 시계열이 폭발합니다. AI가 이 실수를 자주 하므로, 프롬프트에 "유한한 라벨만 허용"을 명시해야 합니다.

- **세 신호의 데이터 형태는 어떻게 다를까요?**
  메트릭은 숫자 시계열, 로그는 구조화된 이벤트, 트레이스는 span 트리입니다. 저장 비용도 메트릭 < 로그 < 트레이스 순서입니다.

---

## 정리

메트릭, 로그, 트레이스는 같은 신호의 세 버전이 아닙니다. 각자 답하는 질문이 다르고, 함께 써야 비로소 운영의 흐름이 보입니다. 바이브코딩 맥락에서는 AI에게 관측성을 요청할 때 이 구분을 명확히 하는 것이 핵심입니다. 다음 글에서는 메트릭을 실제로 어떻게 수집하고 그래프로 만드는지 살펴봅니다.

## 참고 자료

- [Prometheus metric types](https://prometheus.io/docs/concepts/metric_types/)
- [Structured logging](https://www.datadoghq.com/blog/structured-logging/)
- [OpenTelemetry traces](https://opentelemetry.io/docs/concepts/signals/traces/)
- [PromQL 공식 문서](https://prometheus.io/docs/prometheus/latest/querying/basics/)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Observability 기초 (1/10): 관측성이란 무엇인가?
- **바이브코딩을 위한 Observability 기초 (2/10): 메트릭, 로그, 트레이스 (현재 글)**
- 바이브코딩을 위한 Observability 기초 (3/10): 메트릭 수집과 시각화
- 바이브코딩을 위한 Observability 기초 (4/10): 구조화된 로깅
- 바이브코딩을 위한 Observability 기초 (5/10): 분산 트레이싱 기초
- 바이브코딩을 위한 Observability 기초 (6/10): 대시보드 설계
- 바이브코딩을 위한 Observability 기초 (7/10): 경보와 온콜
- 바이브코딩을 위한 Observability 기초 (8/10): 서비스 수준 지표와 목표 기초
- 바이브코딩을 위한 Observability 기초 (9/10): 비용과 카디널리티
- 바이브코딩을 위한 Observability 기초 (10/10): 운영 가능한 관측성 스택
<!-- toc:end -->

Tags: 바이브코딩, Observability, Metrics, Logging, Tracing
