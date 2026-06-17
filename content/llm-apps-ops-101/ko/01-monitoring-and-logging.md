---
title: "LLM Apps Ops 101 (1/6): LLM 앱 모니터링과 로깅"
series: llm-apps-ops-101
episode: 1
language: ko
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/284"
    published_at: '2026-06-06'
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

이 글은 LLM Apps Ops 101 시리즈의 첫 번째 글입니다.

"LLM 앱에서 에러가 났습니다." 슬랙에 이 메시지가 올라왔을 때, 정말 어려운 부분은 장애 자체가 아닙니다. 어려운 부분은 그 다음 질문입니다. "그때 프롬프트에 뭐가 들어갔지?" "토큰이 얼마나 나갔지?" "어제 같은 요청은 왜 정상이었지?" 이 질문들에 답할 수 없으면, 팀은 장애를 겪은 게 아니라 장애를 목격만 한 겁니다.

전통적인 REST API는 상태 코드와 응답 시간만으로도 1차 분석이 됩니다. 500이면 서버 에러, 느리면 DB 쿼리 의심. 하지만 LLM 앱은 200 응답 안에 전혀 다른 운영 현실이 숨어 있습니다. 같은 성공 응답이어도 한쪽은 토큰을 3배 태우고 있고, 다른 한쪽은 한 줄짜리 답을 내뱉고 있을 수 있습니다. 상태 코드로는 이 차이를 구분할 수 없습니다. 저는 팀들이 "우리 API 에러율 0.1%입니다"라고 보고하면서, 정작 응답 품질이 바닥을 치고 있는 걸 몇 주 뒤에야 발견하는 경우를 여러 번 봤습니다.

그래서 LLM 앱 모니터링의 출발점은 대시보드가 아닙니다. 호출 한 건을 나중에 다시 설명할 수 있는 로그 레코드, 이것이 출발점입니다.

![모니터링과 로깅 컴포넌트 구성](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/01/01-01-big-picture.ko.png)
*요청 한 건의 비용, 지연, 품질 신호가 하나의 레코드로 연결되는 구조*
> 로그 한 줄을 LLM 호출 한 건의 운영 계약서라고 보면, 비용·지연·디버깅 질문이 흩어지지 않습니다.

## 이 글에서 다룰 문제

- 같은 200 응답인데 어떤 요청은 비싸고 어떤 요청은 품질이 낮다면, 로그에 어떤 필드가 있어야 이 차이를 설명할 수 있을까요?
- "어제까지 잘 되던 응답이 오늘 이상해졌다"는 보고가 들어왔을 때, 원인을 프롬프트 변경인지 모델 변경인지 10분 안에 분리할 수 있는 로그 구조는 무엇일까요?
- 메트릭이 "이상하다"고 알려주고 로그가 "왜 이상한지" 설명하는 역할 분담은 구체적으로 어떻게 만들까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 왜 전통 API 로그로는 부족한가

![요청과 응답 로그가 한 호출을 잇는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/01/01-01-why-this-layer-matters.ko.png)

*요청과 응답 로그가 한 호출을 잇는 흐름*

일반적인 웹 API에서는 요청 로그가 `method`, `path`, `status_code`, `duration_ms` 네 필드면 충분합니다. 이 필드만으로도 "어디서 느린가", "어디서 실패하는가"를 찾을 수 있습니다. LLM 앱은 다릅니다. 두 요청이 모두 200이고 응답 시간도 비슷한데, 한쪽은 토큰을 500개 써서 비용이 적게 나왔고 다른 한쪽은 4,000개를 써서 비용이 8배 나왔을 수 있습니다.

이 차이를 사후에 설명하려면, 요청 시점에 이미 다음이 기록되어 있어야 합니다.

| 운영 질문 | 필요한 필드 | 없으면 생기는 문제 |
|---|---|---|
| 왜 비쌌지? | `prompt_tokens`, `completion_tokens` | 비용 급증 원인을 모름 |
| 왜 느렸지? | `latency_ms`, `model` | 모델 교체 효과를 측정 못 함 |
| 뭘 물어봤지? | `prompt_preview` (80자) | 디버깅 시 재현 불가 |
| 뭘 답했지? | `response_preview` (120자) | 품질 저하 시점을 특정 못 함 |
| 어떤 버전? | `prompt_version` | 회귀 원인 분리 불가 |

저는 이 표를 "로그 필드 하나가 빠지면 운영 질문 하나에 답할 수 없다"는 규칙으로 기억합니다. 실제로 초기 단계에서 `prompt_tokens`를 안 남기고 운영하다가, 한 달 뒤 비용이 3배 오른 원인을 찾으려고 로그를 열었는데 토큰 수가 없어서 처음부터 다시 계측해야 했던 팀을 본 적 있습니다. 한 달치 비용 데이터가 그냥 사라진 겁니다.

핵심은 이겁니다. LLM 앱의 로그는 "무슨 일이 있었는가"를 넘어 "어떤 비용과 맥락으로 그 일이 있었는가"까지 남겨야 합니다. 요청 로그와 응답 로그를 `request_id`로 묶어 두면, 나중에 장애 분석, 비용 분석, 품질 분석이 같은 레코드에서 시작할 수 있습니다.

## 최소 실행 예제 — 호출 한 건을 설명할 수 있는 로그

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

이 코드에서 중요한 점은 라이브러리 사용법이 아닙니다. 중요한 점은 설계 결정 세 가지입니다.

![공통 로그 스키마가 운영 질문을 하나로 묶는 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/01/01-02-what-to-notice-in-this-code.ko.png)

*공통 로그 스키마가 운영 질문을 하나로 묶는 구조*

**첫째, `request_id`가 요청과 응답을 묶습니다.** `llm_request` 이벤트와 `llm_response` 이벤트가 같은 `request_id`를 공유하기 때문에, 나중에 "이 요청의 프롬프트는 뭐였고, 토큰은 얼마나 나왔고, 얼마나 걸렸지?"를 한 번에 복원할 수 있습니다. 이게 없으면 요청 시점 정보와 응답 시점 정보가 분리되어, 장애 분석 시 시간순 매칭을 수동으로 해야 합니다.

**둘째, 전체 답변 대신 미리보기만 남깁니다.** `response_preview`로 120자만 기록하는 이유는 두 가지입니다. 민감 정보 노출 위험을 줄이는 것, 그리고 로그 저장 비용을 억제하는 것. 실제로 LLM 응답 전문을 로그에 넣으면, 하루 만에 로그 볼륨이 수 배로 뛰어서 Elasticsearch 비용이 예산을 초과하는 일이 생깁니다. 저는 초기에 전문 로깅을 켰다가 3일 만에 로그 스토리지 알람을 받고 미리보기로 전환한 팀을 알고 있습니다.

**셋째, `JsonFormatter`가 스키마를 강제합니다.** 모든 이벤트가 같은 JSON 구조로 나가기 때문에, 수집기(Fluentd, Vector, Datadog Agent)가 바뀌어도 파싱 규칙을 다시 만들 필요가 없습니다. 이건 사소해 보이지만, 나중에 로그 파이프라인을 교체할 때 가장 큰 차이를 만듭니다.

## 메트릭과 로그의 역할 분담

![메트릭과 로그가 함께 실패 범위를 좁히는 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/01/01-03-where-engineers-get-confused.ko.png)

*메트릭과 로그가 함께 실패 범위를 좁히는 구조*

실무에서 가장 자주 보는 오해는 "로그만 잘 남기면 모니터링 끝"이라는 생각입니다. 실제로는 역할이 완전히 다릅니다. **메트릭은 "지금 이상하다"를 먼저 알려주고, 로그는 "왜 이상한지"를 설명합니다.** 이 순서가 뒤집히면 장애 대응이 느려집니다.

예를 들어 P95 지연 시간이 갑자기 2배로 뛰었다고 합시다. 이 사실을 먼저 알려주는 건 메트릭(시계열 데이터)입니다. 메트릭이 없으면 사용자가 "느려요"라고 보고할 때까지 모릅니다. 메트릭이 알려준 뒤에, 어떤 요청이 느렸는지 찾는 건 로그의 역할입니다. `latency_ms`가 높은 요청을 필터링하고, 그 요청의 `model`, `prompt_version`, `total_tokens`를 보면서 원인을 좁힙니다.

이 역할 분담을 대시보드에 반영하면 세 축이 됩니다.

| 축 | 보는 것 | 대표 패널 |
|---|---|---|
| 지연 시간 | 응답이 느려지고 있는가 | P50, P95, P99 추이 |
| 토큰/비용 | 비용이 예상을 벗어나는가 | input/output tokens, estimated cost |
| 품질 | 응답이 기대를 만족하는가 | schema_fail_rate, 길이 이상치율 |

이 세 축을 같은 시간축에 겹치면 인과 관계가 보이기 시작합니다. P95 지연이 오르면서 동시에 output token도 증가했다면? 모델이 장문 응답을 생성하고 있을 가능성이 큽니다. 반대로 지연은 안정적인데 비용만 치솟으면? 입력 프롬프트가 길어졌거나 캐시 히트율이 떨어진 겁니다.

### 요청 단위 로그를 패널 단위 집계로 연결하는 예시

```python
from collections import defaultdict
from statistics import median

def build_dashboard_buckets(records: list[dict]) -> dict:
    buckets = defaultdict(list)
    for row in records:
        key = (row["route"], row["model"], row["prompt_version"])
        buckets[key].append(row)

    panels = {}
    for key, rows in buckets.items():
        latencies = sorted(r["latency_ms"] for r in rows)
        in_tokens = sum(r["input_tokens"] for r in rows)
        out_tokens = sum(r["output_tokens"] for r in rows)
        total_cost = round(sum(r["estimated_cost_usd"] for r in rows), 6)
        schema_fail = sum(1 for r in rows if not r["schema_ok"])

        p95_index = max(0, int(len(latencies) * 0.95) - 1)
        panels[str(key)] = {
            "request_count": len(rows),
            "latency_p50_ms": median(latencies),
            "latency_p95_ms": latencies[p95_index],
            "input_tokens_total": in_tokens,
            "output_tokens_total": out_tokens,
            "cost_total_usd": total_cost,
            "schema_fail_rate": round(schema_fail / len(rows), 4),
        }
    return panels
```

이 코드가 화려하지 않지만 운영에서 바로 쓸 수 있는 이유는, 집계 키가 `route + model + prompt_version`이기 때문입니다. 이 세 값을 묶으면 "어떤 엔드포인트의 어떤 모델, 어떤 프롬프트 버전이 비용과 지연을 동시에 흔드는지" 바로 확인할 수 있습니다. Datadog이든 Grafana든 BigQuery든, 이 집계 로직은 그대로 재사용됩니다.

## 프롬프트 버전을 로그 계약으로 올리기

"어제까지 잘 되던 응답이 오늘 이상해졌습니다." 이 보고는 LLM 서비스에서 매우 흔합니다. 문제는 원인 후보가 셋이라는 겁니다. 모델 버전이 바뀌었는가, 시스템 프롬프트가 수정되었는가, few-shot 예시가 교체되었는가. 로그에 `prompt_version`이 없으면 이 셋을 분리할 방법이 없습니다.

저는 프롬프트 버전을 "선택 필드"가 아니라 "운영 계약 필드"로 취급하라고 권합니다. 이유는 간단합니다. 비용 급증, 지연 증가, 품질 저하가 발생했을 때, `prompt_version`이 로그에 있으면 "이 프롬프트 버전부터 문제가 시작됐다"를 증명할 수 있습니다. 없으면 "아마 그때 바꿨을 겁니다"라는 추측만 남습니다.

실용적인 버전 관리 방식은 배포 단위마다 `prompt_version`을 올리고, 요청마다 다음을 함께 기록하는 겁니다.

```python
log_record = {
    "request_id": request_id,
    "prompt_version": "v2026.05.20-briefing",  # 날짜 + 목적
    "model": "gpt-4o-mini",
    "temperature": 0.3,
    "max_tokens": 512,
}
```

`prompt_version`을 Git 태그와 1:1로 매핑하면 운영 가시성이 더 좋아집니다. 릴리스 노트에 변경 의도를 남기면, 장애 회고에서 "왜 이 버전을 배포했는가"까지 설명할 수 있습니다. A/B 실험을 하는 경우에는 `experiment_group` 필드를 추가하면 실험군별 비용과 실패율을 분리할 수 있습니다.

## 로그 스키마를 운영 계약으로 고정하기

초기에는 로그 필드가 자주 바뀝니다. 새 기능이 추가되면 필드가 늘고, 불필요한 필드는 빠집니다. 하지만 운영으로 넘어가면 이야기가 달라집니다. 대시보드 패널, 알림 규칙, 주간 리뷰 쿼리가 모두 특정 필드 이름에 의존하고 있기 때문입니다. 필드 하나를 이름만 바꿔도 알림이 깨질 수 있습니다.

그래서 스키마 자체를 코드로 고정하는 편이 안전합니다.

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

이 dataclass가 "운영 계약"인 이유는, 필드를 추가하거나 삭제할 때 코드 변경이 필요하기 때문입니다. Pull Request에서 리뷰어가 "이 필드 제거하면 대시보드 패널 3개가 깨진다"고 말할 수 있는 구조가 됩니다. 암묵적으로 dict에 키를 넣고 빼는 것과는 안전성이 크게 다릅니다.

`schema_version` 필드가 들어가는 이유도 같습니다. 로그 소비자(대시보드, 알림, 분석 쿼리)가 "이 로그는 v2 스키마다"를 알 수 있으면, 스키마 마이그레이션을 점진적으로 할 수 있습니다. 한 번에 모든 소비자를 바꾸지 않아도 됩니다.

### OpenTelemetry trace를 로그와 연결하기

메트릭과 로그만으로 원인을 좁히기 어려운 구간에서는 trace가 도움이 됩니다. 특히 요청이 프롬프트 구성 → 검색 → 모델 호출 → 후처리 여러 단계를 거칠 때, 각 span의 시간을 분리해서 봐야 병목을 찾을 수 있습니다.

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

핵심은 도구 선택이 아닙니다. `request_id`와 `trace_id`를 동시에 남겨서, 로그에서 trace로, trace에서 로그로 양방향 이동이 가능하도록 만드는 습관입니다. 운영에서는 exporter를 OTLP로 바꿔서 Jaeger, Tempo, Datadog APM 어디로든 보낼 수 있습니다.

## 장애 대응 — 질의 템플릿을 미리 준비하기

로그와 대시보드가 있어도, 장애 상황에서 "뭘 먼저 조회하지?"가 정해져 있지 않으면 대응이 느려집니다. 사람은 압박 상황에서 최적의 쿼리를 즉석에서 만들지 못합니다. 그래서 운영팀은 반복적으로 묻는 질문을 "질의 템플릿"으로 사전에 문서화해 둬야 합니다.

### 운영 회고에서 자주 쓰는 질의 4가지

1. **같은 `prompt_version`에서 `latency_p95_ms`가 급증한 시간대는 언제인가** — 프롬프트 변경이 지연의 원인인지 확인합니다.
2. **`estimated_cost_usd` 상위 요청은 어떤 route에서 나왔는가** — 비용 급증의 진원지를 특정합니다.
3. **`schema_ok=false`가 특정 모델에 집중되는가** — 모델 교체 후 출력 포맷 호환성을 점검합니다.
4. **`output_tokens` 급증이 특정 고객 티어와 연결되는가** — 사용 패턴 변화와 비용을 분리합니다.

이 네 질문에 10분 안에 답할 수 있으면 모니터링 체계가 성숙한 편입니다. 반대로, 이 질문에 답하려고 로그 구조를 먼저 뜯어고쳐야 한다면 대시보드보다 로그 계약부터 다시 정리하는 게 맞습니다.

질의 템플릿은 SQL이든 Elasticsearch 쿼리든 형식이 중요하지 않습니다. 중요한 건 **질문이 고정되어 있다**는 사실입니다. 질문이 고정되면 필요한 로그 필드도 역으로 고정되고, 계측 품질이 안정됩니다.

### 대시보드 최소 설정 예시

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

이 최소 템플릿을 먼저 적용하면 팀이 같은 숫자를 보고 대화할 수 있습니다. 이후에는 tenant별, 모델별, 프롬프트 버전별 분해를 단계적으로 추가하는 방식이 안전합니다.

### 주간 운영 리뷰에서 로그를 읽는 순서

주간 리뷰에서는 데이터가 많을수록 오히려 결론이 흐려질 수 있습니다. 읽는 순서를 고정하는 편이 좋습니다.

1. **거시 지표** — 지연 시간과 오류 비율의 전체 추이를 먼저 확인합니다.
2. **비용 신호** — 트래픽 변화 대비 비용이 비정상적으로 커졌는지 겹쳐 봅니다.
3. **품질 지표** — 프롬프트 버전과 연결해 회귀 가능성을 점검합니다.
4. **샘플 로그** — 마지막에만 개별 로그를 열어 구체 사례를 읽습니다.

이 순서가 중요한 이유는, 처음부터 개별 로그를 읽으면 국소적 이상에 시선을 빼앗기기 때문입니다. 거시 지표에서 좁혀 들어가면 팀이 같은 맥락에서 원인을 논의할 수 있습니다.

리뷰 결과는 "관찰 → 가설 → 실험" 세 칸으로 기록하는 게 좋습니다. 예를 들어 "관찰: P95 상승 + output token 증가", "가설: 프롬프트 v2026.05.20이 장문 응답을 유도", "실험: 출력 길이 제한과 지시문 간소화 적용." 이렇게 남겨 두면 다음 주에 같은 구조로 효과를 비교할 수 있습니다.

## 운영 체크리스트

- [ ] 모든 LLM 호출에 `request_id`, `model`, `latency_ms`, `total_tokens`를 남기고 있다
- [ ] 응답 전문 대신 preview 로깅을 기본값으로 쓰고 있다
- [ ] 성공 이벤트와 실패 이벤트가 같은 JSON 스키마를 공유한다
- [ ] 평균 지연 시간과 별도로 P95 지연 시간을 추적하고 있다
- [ ] `prompt_version`을 요청마다 기록하고 있다
- [ ] 장애 시 10분 안에 답할 질의 템플릿이 문서화되어 있다

## 정리

이 글에서 다룬 핵심은 세 가지입니다. 첫째 같은 200 응답인데 어떤 요청은 비싸고 어떤 요청은 품질이 낮다면, 로그에 어떤 필드가 있어야 이 차이를 설명할 수 있을, 둘째 "어제까지 잘 되던 응답이 오늘 이상해졌다"는 보고가 들어왔을 때, 원인을 프롬프트 변경인지 모델 변경인지 10분 안에 분리할 수 있는 로그 구조는 무엇일, 셋째 메트릭이 "이상하다"고 알려주고 로그가 "왜 이상한지" 설명하는 역할 분담은 구체적으로 어떻게 만들입니다. 왜 전통 API 로그로는 부족한가에서 시작해 실무 적용까지 이어지는 흐름을 따라가면 이 주제의 전체 그림이 잡힙니다.

## 처음 질문으로 돌아가기

- **같은 200 응답인데 어떤 요청은 비싸고 어떤 요청은 품질이 낮다면, 로그에 어떤 필드가 있어야 이 차이를 설명할 수 있을까요?**
  - 이 코드에서 중요한 점은 라이브러리 사용법이 아닙니다. 중요한 점은 설계 결정 세 가지입니다.
- **"어제까지 잘 되던 응답이 오늘 이상해졌다"는 보고가 들어왔을 때, 원인을 프롬프트 변경인지 모델 변경인지 10분 안에 분리할 수 있는 로그 구조는 무엇일까요?**
  - "어제까지 잘 되던 응답이 오늘 이상해졌습니다." 이 보고는 LLM 서비스에서 매우 흔합니다. 문제는 원인 후보가 셋이라는 겁니다.
- **메트릭이 "이상하다"고 알려주고 로그가 "왜 이상한지" 설명하는 역할 분담은 구체적으로 어떻게 만들까요?**
  - 실무에서 가장 자주 보는 오해는 "로그만 잘 남기면 모니터링 끝"이라는 생각입니다. 실제로는 역할이 완전히 다릅니다. **메트릭은 "지금 이상하다"를 먼저 알려주고, 로그는 "왜 이상한지"를 설명합니다.** 이 순서가 뒤집히면 장애 대응이 느려집니다.

<!-- toc:begin -->
## 시리즈 목차

- **LLM Apps Ops 101 (1/6): LLM 앱 모니터링과 로깅 (현재 글)**
- [LLM Apps Ops 101 (2/6): LLM 비용 추적과 최적화](./02-cost-tracking.md)
- [LLM Apps Ops 101 (3/6): LLM 출력 품질 평가](./03-evaluation.md)
- [LLM Apps Ops 101 (4/6): LLM 앱 보안](./04-security.md)
- [LLM Apps Ops 101 (5/6): LLM 앱 배포 전략](./05-deployment.md)
- [LLM Apps Ops 101 (6/6): LLM 앱 운영 완성](./06-ops-complete.md)

<!-- toc:end -->

---

## 참고 자료

- [LLM Apps Ops 101 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/llm-apps-ops-101/ko)
- [Groq API Reference](https://console.groq.com/docs/api-reference)
- [Python logging cookbook](https://docs.python.org/3/howto/logging-cookbook.html)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)

### 관련 시리즈

- [AI Evaluation 101](../../ai-evaluation-101/ko/01-why-evaluate-llm-apps.md) — 이 시리즈가 운영 단계에서 추적하는 "LLM 품질"을 릴리스 전 단계에서 어떻게 측정할지 다룹니다. 모니터링 지표가 흔들릴 때, 어떤 평가 방식으로 회귀 여부를 확인할지 결정하는 데 도움이 됩니다.

Tags: LLMOps, Observability, Python, LLM
