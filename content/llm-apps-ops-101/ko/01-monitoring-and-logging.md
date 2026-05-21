---
title: "LLM Apps Ops 101 (1/6): LLM 앱 모니터링과 로깅"
series: llm-apps-ops-101
episode: 1
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- LLMOps
- Observability
- Python
- LLM
last_reviewed: '2026-05-12'
seo_description: LLM 호출 한 건을 나중에 복원할 수 있는 로그 구조를 먼저 잡아야 비용, 지연 시간, 장애 분석이 하나의 기록으로 연결됩니다.
---

# LLM Apps Ops 101 (1/6): LLM 앱 모니터링과 로깅

LLM 앱이 데모를 넘어 실제 트래픽을 받기 시작하면, 가장 먼저 드러나는 문제는 장애 자체보다도 “이 요청에서 정확히 무슨 일이 있었지?”를 다시 설명하지 못하는 상태입니다. 이 글은 LLM Apps Ops 101 시리즈의 첫 번째 글입니다. 여기서는 요청 한 건의 지연 시간, 토큰 사용량, 디버깅 맥락을 나중에 한 번에 복원할 수 있도록, 모니터링과 로깅의 최소 기준을 어디서부터 세워야 하는지 정리하겠습니다.

보통 API 운영에서는 상태 코드와 응답 시간만으로도 출발할 수 있습니다. 하지만 LLM 앱은 같은 200 응답이어도 토큰 사용량이 크게 다를 수 있고, 응답 길이만 이상해도 바로 품질 문제로 이어질 수 있습니다. 그래서 관측 가능성의 출발점은 예쁜 대시보드가 아니라, 호출 한 건을 다시 설명할 수 있는 로그 레코드입니다.

## 먼저 던지는 질문

- 모든 LLM 요청 로그에는 어떤 필드가 반드시 들어가야 할까요?
- 지연 시간, 토큰 사용량, 응답 미리보기를 어떻게 한 레코드에 묶을까요?
- 나중에 Datadog, BigQuery, Elasticsearch로 옮겨도 버틸 로그 형태는 무엇일까요?

## 큰 그림

![모니터링과 로깅 컴포넌트 구성](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/01/01-01-big-picture.ko.png)

*모니터링과 로깅 컴포넌트 구성*

이 그림에서는 애플리케이션, LLM provider, 로그 저장소, 운영 대시보드가 하나의 관측 흐름으로 연결되는 모습을 봅니다. LLM 앱 운영의 첫 기준은 대시보드가 아니라 요청 한 건을 다시 설명할 수 있는 로그 구조입니다.

> 로그 한 줄을 LLM 호출 한 건의 운영 계약서라고 보면 비용, 지연 시간, 디버깅 질문이 흩어지지 않습니다.

## 왜 이 레이어가 중요한가

![요청과 응답 로그가 한 호출을 잇는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/01/01-01-why-this-layer-matters.ko.png)

*요청과 응답 로그가 한 호출을 잇는 흐름*

관측 가능성의 시작은 화려한 시각화가 아니라, 호출 한 건을 나중에 설명할 수 있는 기록입니다.

일반적인 웹 API는 상태 코드와 응답 시간만 있어도 1차 분석이 가능합니다. 하지만 LLM 앱은 같은 성공 요청 안에서도 비용, 지연 시간, 응답 품질 신호가 크게 갈립니다. 두 요청이 모두 200이어도 한쪽은 토큰을 과하게 태우고 있을 수 있고, 다른 한쪽은 비정상적으로 짧은 답을 내고 있을 수 있습니다. 운영자가 정말 알고 싶은 것은 “성공했는가”만이 아니라 “어떤 비용과 맥락으로 성공했는가”입니다.

그래서 요청 로그와 응답 로그를 서로 다른 관심사로 분리해 두되, `request_id` 같은 공통 키로 다시 합칠 수 있어야 합니다. 이 기준이 있어야 나중에 장애 분석, 비용 분석, 품질 분석이 서로 다른 저장소로 흩어지지 않습니다.

예제 파일: `en/01-monitoring-and-logging/main.py`

## 최소 실행 예제

```python
import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone

from groq import Groq

MODEL = "llama-3.1-8b-instant"

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "event": record.getMessage(),
        }
        extra = getattr(record, "payload", None)
        if extra:
            payload.update(extra)
        return json.dumps(payload, ensure_ascii=False)

def build_logger() -> logging.Logger:
    logger = logging.getLogger("llm_monitoring")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    logger.propagate = False
    return logger

LOGGER = build_logger()

def ask_llm(client: Groq, prompt: str) -> dict:
    request_id = str(uuid.uuid4())[:8]
    started = time.perf_counter()
    LOGGER.info(
        "llm_request",
        extra={
            "payload": {
                "request_id": request_id,
                "model": MODEL,
                "prompt_preview": prompt[:80],
            }
        },
    )
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "You are a concise Python assistant.",
            },
            {"role": "user", "content": prompt},
        ],
    )
    latency_ms = round((time.perf_counter() - started) * 1000, 1)
    usage = response.usage
    if usage is None:
        raise RuntimeError("usage metadata missing from Groq response")
    answer = response.choices[0].message.content or ""
    record = {
        "request_id": request_id,
        "model": MODEL,
        "latency_ms": latency_ms,
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens,
        "response_preview": answer[:120],
    }
    LOGGER.info("llm_response", extra={"payload": record})
    return record | {"answer": answer}

def main() -> None:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    prompts = [
        "Explain Python list comprehensions in two sentences.",
        "Explain the difference between a generator and an iterator in two sentences.",
    ]
    results = [ask_llm(client, prompt) for prompt in prompts]
    summary = {
        "calls": len(results),
        "latency_ms": [result["latency_ms"] for result in results],
        "total_tokens": sum(result["total_tokens"] for result in results),
    }
    print("=== monitoring summary ===")
    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
```

## 이 코드에서 먼저 볼 점

![공통 로그 스키마가 운영 질문을 하나로 묶는 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/01/01-02-what-to-notice-in-this-code.ko.png)

*공통 로그 스키마가 운영 질문을 하나로 묶는 구조*

- `JsonFormatter`가 모든 이벤트를 같은 형태로 밀어 넣기 때문에, 나중에 수집기나 저장소가 바뀌어도 스키마를 다시 뒤엎지 않아도 됩니다.
- `request_id`와 `total_tokens`가 같은 레코드에 있어야 디버깅 정보와 비용 정보가 분리되지 않습니다.
- 전체 답변 대신 짧은 미리보기만 남기면 민감 정보 노출 위험과 로그 저장 비용을 동시에 줄일 수 있습니다.

이 예제의 핵심은 로깅 라이브러리 사용법 자체가 아닙니다. 더 중요한 점은 요청 시작 시점과 응답 완료 시점에 어떤 정보를 남겨야 나중 질문에 답할 수 있는가입니다. `latency_ms`, `model`, `prompt_preview`, `response_preview`, `total_tokens`가 한 구조 안에 있으면 “왜 느렸지?”, “왜 비쌌지?”, “무슨 답이 나왔지?”를 같은 출처에서 다시 볼 수 있습니다.

## 어디서 자주 헷갈릴까요?

![메트릭과 로그가 함께 실패 범위를 좁히는 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/01/01-03-where-engineers-get-confused.ko.png)

*메트릭과 로그가 함께 실패 범위를 좁히는 구조*

- 구조화 로그가 메트릭을 대체하지는 않습니다. 메트릭은 추세를 보고, 로그는 개별 호출을 설명합니다.
- 토큰 수는 사용자가 눈으로 보는 프롬프트만이 아니라 system message와 생성된 출력까지 함께 포함합니다.
- 응답 전문 로깅은 초반에는 편리해 보여도, 곧 개인정보와 저장 비용 문제로 돌아옵니다.

실무에서 특히 자주 나오는 오해는 “로그만 잘 남기면 observability가 끝난다”는 생각입니다. 실제로는 메트릭이 먼저 이상 징후를 보여 주고, 로그가 그 원인을 설명합니다. 평균 지연 시간만 보면 멀쩡한데 P95가 급등하는 상황은 메트릭이 먼저 알려 주고, 그 뒤에 어떤 요청이 길어졌는지는 로그가 설명하는 식입니다.

## 체크리스트

- [ ] 항상 `request_id`, `model`, `latency_ms`, `total_tokens`를 남긴다
- [ ] 기본값은 전체 답변이 아니라 preview 로깅으로 둔다
- [ ] 성공 이벤트와 실패 이벤트를 같은 스키마로 유지한다
- [ ] 평균 지연 시간과 별도로 P95 지연 시간을 추적한다

## 정리

목표는 예쁜 로그를 만드는 것이 아닙니다. 나중에 장애, 비용 급증, 모델 이상 동작에 대한 질문이 들어왔을 때, 같은 형태의 레코드 하나로 그 요청을 다시 설명할 수 있게 만드는 것입니다.

### 구조화 로그 스키마를 운영 계약으로 고정하기

초기에는 로그 필드가 자주 바뀝니다. 하지만 운영으로 넘어가면 필드 추가와 제거를 엄격히 관리해야 합니다. 가장 안전한 방법은 요청 단위 스키마를 문서화하고 버전 필드를 넣는 것입니다. 예를 들어 `schema_version`, `service`, `environment`, `provider`, `status`를 고정하면, 대시보드와 알림 규칙이 필드 변경으로 깨지는 일을 크게 줄일 수 있습니다.

```python
from dataclasses import dataclass, asdict
from typing import Literal

@dataclass
class LLMLogRecord:
    schema_version: str
    service: str
    environment: str
    event: Literal["llm_request", "llm_response", "llm_error"]
    request_id: str
    model: str
    provider: str
    latency_ms: float | None
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    status: Literal["ok", "error"]
    error_type: str | None
    prompt_preview: str | None
    response_preview: str | None

def to_json_payload(record: LLMLogRecord) -> dict:
    return asdict(record)
```

이 구조를 기준으로 `llm_request`에는 지연 시간과 토큰 수를 비워 두고, `llm_response`에서 채우는 방식으로 합의해 두면 분석 시 혼선이 줄어듭니다. 실패 이벤트(`llm_error`)도 같은 키 집합을 유지해야 쿼리가 단순해집니다.

### OpenTelemetry trace를 로그와 연결하기

메트릭과 로그만으로 원인을 좁히기 어려운 구간에서는 trace가 큰 도움이 됩니다. 특히 요청이 프롬프트 구성, 검색, 모델 호출, 후처리 단계를 거칠 때 각 span의 시간이 분리되어 보여야 병목을 빠르게 찾을 수 있습니다. 핵심은 trace id를 로그에 함께 남겨 교차 탐색이 가능하도록 만드는 것입니다.

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("llm-app")

def traced_llm_call(client, prompt: str) -> dict:
    with tracer.start_as_current_span("chat.request") as span:
        span.set_attribute("llm.model", MODEL)
        span.set_attribute("llm.prompt_length", len(prompt))
        result = ask_llm(client, prompt)
        span.set_attribute("llm.total_tokens", result["total_tokens"])
        span.set_attribute("llm.latency_ms", result["latency_ms"])

        trace_id = format(span.get_span_context().trace_id, "032x")
        LOGGER.info(
            "llm_trace_link",
            extra={"payload": {"request_id": result["request_id"], "trace_id": trace_id}},
        )
        return result
```

운영에서는 exporter를 OTLP로 바꾸어 Jaeger, Tempo, Datadog APM 같은 백엔드로 보내면 됩니다. 중요한 점은 도구 선택이 아니라 `request_id`와 `trace_id`를 동시에 남겨 한 요청의 로그와 trace를 이어 보는 습관입니다.

### 대시보드 최소 설정 예시

대시보드는 처음부터 복잡하게 만들 필요가 없습니다. 요청량, 오류율, P95 지연 시간, 토큰 사용량, 모델별 비용 추이를 먼저 고정하면 운영 회의에서 질문을 빠르게 정렬할 수 있습니다.

```yaml
dashboard: llm-ops-overview
widgets:
  - name: requests_per_min
    query: count_over_time({event="llm_response"}[1m])
  - name: error_rate
    query: |
      sum(rate({event="llm_error"}[5m]))
      /
      sum(rate({event=~"llm_response|llm_error"}[5m]))
  - name: p95_latency_ms
    query: quantile_over_time(0.95, {event="llm_response"} | unwrap latency_ms [5m])
  - name: total_tokens_per_min
    query: sum_over_time({event="llm_response"} | unwrap total_tokens [1m])
  - name: top_error_types
    query: topk(5, sum by (error_type) (rate({event="llm_error"}[10m])))
alerts:
  - name: p95_latency_regression
    condition: p95_latency_ms > 2500 for 10m
  - name: error_rate_spike
    condition: error_rate > 0.03 for 5m
```

위와 같은 최소 템플릿을 먼저 적용하면 팀이 같은 숫자를 보고 대화할 수 있습니다. 이후에는 tenant별 분해, 모델별 분해, 프롬프트 버전별 분해를 단계적으로 추가하는 방식이 안전합니다.

## 처음 질문으로 돌아가기

- **모든 LLM 요청 로그에는 어떤 필드가 반드시 들어가야 할까요?**
  - request_id, model, prompt·completion token, latency, status, error, response preview, 사용자 또는 tenant 키가 최소 필드가 됩니다.
- **지연 시간, 토큰 사용량, 응답 미리보기를 어떻게 한 레코드에 묶을까요?**
  - 요청 시작과 응답 완료를 같은 request_id로 묶고, provider usage와 latency 측정값을 같은 JSON record 또는 join 가능한 이벤트로 남깁니다.
- **나중에 Datadog, BigQuery, Elasticsearch로 옮겨도 버틸 로그 형태는 무엇일까요?**
  - 필드 이름과 타입이 고정된 JSON 로그가 가장 오래 버팁니다. 저장소가 바뀌어도 스키마와 request_id가 유지되면 분석을 이어갈 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- **LLM Apps Ops 101 (1/6): LLM 앱 모니터링과 로깅 (현재 글)**
- LLM Apps Ops 101 (2/6): LLM 비용 추적과 최적화 (예정)
- LLM Apps Ops 101 (3/6): LLM 출력 품질 평가 (예정)
- LLM Apps Ops 101 (4/6): LLM 앱 보안 (예정)
- LLM Apps Ops 101 (5/6): LLM 앱 배포 전략 (예정)
- LLM Apps Ops 101 (6/6): LLM 앱 운영 완성 (예정)

<!-- toc:end -->

---

## 참고 자료

- [Groq API Reference](https://console.groq.com/docs/api-reference)
- [Python logging cookbook](https://docs.python.org/3/howto/logging-cookbook.html)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)

### 관련 시리즈

- [AI Evaluation 101](../../ai-evaluation-101/ko/01-why-evaluate-llm-apps.md) — 이 시리즈가 운영 단계에서 추적하는 "LLM 품질"을 릴리스 전 단계에서 어떻게 측정할지 다룹니다. 모니터링 지표가 흔들릴 때, 어떤 평가 방식으로 회귀 여부를 확인할지 결정하는 데 도움이 됩니다.

Tags: LLMOps, Observability, Python, LLM
