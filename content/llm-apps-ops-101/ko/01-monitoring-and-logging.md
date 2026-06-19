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

전통적인 REST API는 상태 코드와 응답 시간만으로도 1차 분석이 됩니다. 500이면 서버 에러, 느리면 DB 쿼리 의심. 하지만 LLM 앱은 200 응답 안에 전혀 다른 운영 현실이 숨어 있습니다. 같은 성공 응답이어도 한쪽은 토큰을 3배 태우고 있고, 다른 한쪽은 한 줄짜리 답을 내뱉고 있을 수 있습니다. 상태 코드로는 이 차이를 구분할 수 없습니다.

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
| 어느 라우트? | `route`, `user_tier` | 비용 집중 지점 파악 불가 |

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

def ask_llm(client: Groq, prompt: str, route: str = "/chat", prompt_version: str = "v1.0") -> dict:
    request_id = str(uuid.uuid4())[:8]
    started = time.perf_counter()
    LOGGER.info(
        "llm_request",
        extra={
            "payload": {
                "request_id": request_id,
                "model": MODEL,
                "route": route,
                "prompt_version": prompt_version,
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
    schema_ok = len(answer) >= 20  # 최소 길이 기준
    record = {
        "request_id": request_id,
        "model": MODEL,
        "route": route,
        "prompt_version": prompt_version,
        "latency_ms": latency_ms,
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens,
        "response_preview": answer[:120],
        "schema_ok": schema_ok,
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
        "schema_ok_rate": sum(1 for r in results if r["schema_ok"]) / len(results),
    }
    print("=== monitoring summary ===")
    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
```

이 코드에서 중요한 점은 라이브러리 사용법이 아닙니다. 중요한 점은 설계 결정 네 가지입니다.

![공통 로그 스키마가 운영 질문을 하나로 묶는 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/01/01-02-what-to-notice-in-this-code.ko.png)

*공통 로그 스키마가 운영 질문을 하나로 묶는 구조*

**첫째, `request_id`가 요청과 응답을 묶습니다.** `llm_request` 이벤트와 `llm_response` 이벤트가 같은 `request_id`를 공유하기 때문에, 나중에 "이 요청의 프롬프트는 뭐였고, 토큰은 얼마나 나왔고, 얼마나 걸렸지?"를 한 번에 복원할 수 있습니다.

**둘째, 전체 답변 대신 미리보기만 남깁니다.** `response_preview`로 120자만 기록하는 이유는 두 가지입니다. 민감 정보 노출 위험을 줄이는 것, 그리고 로그 저장 비용을 억제하는 것. 실제로 LLM 응답 전문을 로그에 넣으면, 하루 만에 로그 볼륨이 수 배로 뛰어서 Elasticsearch 비용이 예산을 초과하는 일이 생깁니다.

**셋째, `JsonFormatter`가 스키마를 강제합니다.** 모든 이벤트가 같은 JSON 구조로 나가기 때문에, 수집기(Fluentd, Vector, Datadog Agent)가 바뀌어도 파싱 규칙을 다시 만들 필요가 없습니다.

**넷째, `route`와 `prompt_version`을 함께 기록합니다.** 이 두 필드가 있으면 "어떤 엔드포인트의 어떤 프롬프트 버전에서 문제가 발생했는가"를 집계 키로 바로 쓸 수 있습니다.

## 메트릭과 로그의 역할 분담

![메트릭과 로그가 함께 실패 범위를 좁히는 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/01/01-03-where-engineers-get-confused.ko.png)

*메트릭과 로그가 함께 실패 범위를 좁히는 구조*

실무에서 가장 자주 보는 오해는 "로그만 잘 남기면 모니터링 끝"이라는 생각입니다. 실제로는 역할이 완전히 다릅니다. **메트릭은 "지금 이상하다"를 먼저 알려주고, 로그는 "왜 이상한지"를 설명합니다.** 이 순서가 뒤집히면 장애 대응이 느려집니다.

예를 들어 P95 지연 시간이 갑자기 2배로 뛰었다고 합시다. 이 사실을 먼저 알려주는 건 메트릭(시계열 데이터)입니다. 메트릭이 없으면 사용자가 "느려요"라고 보고할 때까지 모릅니다. 메트릭이 알려준 뒤에, 어떤 요청이 느렸는지 찾는 건 로그의 역할입니다.

이 역할 분담을 대시보드에 반영하면 세 축이 됩니다.

| 축 | 보는 것 | 대표 패널 |
|---|---|---|
| 지연 시간 | 응답이 느려지고 있는가 | P50, P95, P99 추이 |
| 토큰/비용 | 비용이 예상을 벗어나는가 | input/output tokens, estimated cost |
| 품질 | 응답이 기대를 만족하는가 | schema_fail_rate, 길이 이상치율 |

이 세 축을 같은 시간축에 겹치면 인과 관계가 보이기 시작합니다. P95 지연이 오르면서 동시에 output token도 증가했다면? 모델이 장문 응답을 생성하고 있을 가능성이 큽니다.

### 요청 단위 로그를 패널 단위 집계로 연결하는 예시

```python
from collections import defaultdict
from statistics import median

def build_dashboard_buckets(records: list[dict]) -> dict:
    """route + model + prompt_version 단위로 대시보드 패널 데이터를 집계한다."""
    buckets: dict[tuple, list] = defaultdict(list)
    for row in records:
        key = (row["route"], row["model"], row["prompt_version"])
        buckets[key].append(row)

    panels = {}
    for key, rows in buckets.items():
        latencies = sorted(r["latency_ms"] for r in rows)
        in_tokens = sum(r["prompt_tokens"] for r in rows)
        out_tokens = sum(r["completion_tokens"] for r in rows)
        total_cost = round(sum(r.get("estimated_cost_usd", 0.0) for r in rows), 6)
        schema_fail = sum(1 for r in rows if not r.get("schema_ok", True))

        p95_index = max(0, int(len(latencies) * 0.95) - 1)
        p99_index = max(0, int(len(latencies) * 0.99) - 1)
        panels[str(key)] = {
            "request_count": len(rows),
            "latency_p50_ms": median(latencies),
            "latency_p95_ms": latencies[p95_index],
            "latency_p99_ms": latencies[p99_index],
            "input_tokens_total": in_tokens,
            "output_tokens_total": out_tokens,
            "cost_total_usd": total_cost,
            "schema_fail_rate": round(schema_fail / len(rows), 4),
        }
    return panels
```

집계 키가 `route + model + prompt_version`이기 때문에, "어떤 엔드포인트의 어떤 모델, 어떤 프롬프트 버전이 비용과 지연을 동시에 흔드는지" 바로 확인할 수 있습니다. Datadog이든 Grafana든 BigQuery든, 이 집계 로직은 그대로 재사용됩니다.

## 프롬프트 버전을 로그 계약으로 올리기

"어제까지 잘 되던 응답이 오늘 이상해졌습니다." 이 보고는 LLM 서비스에서 매우 흔합니다. 문제는 원인 후보가 셋이라는 겁니다. 모델 버전이 바뀌었는가, 시스템 프롬프트가 수정되었는가, few-shot 예시가 교체되었는가. 로그에 `prompt_version`이 없으면 이 셋을 분리할 방법이 없습니다.

실용적인 버전 관리 방식은 배포 단위마다 `prompt_version`을 올리고, 요청마다 다음을 함께 기록하는 겁니다.

```python
log_record = {
    "request_id": request_id,
    "prompt_version": "v2026.05.20-briefing",  # 날짜 + 목적
    "model": "gpt-4o-mini",
    "temperature": 0.3,
    "max_tokens": 512,
    "route": "/api/summarize",
    "experiment_group": "control",  # A/B 실험 중인 경우
}
```

`prompt_version`을 Git 태그와 1:1로 매핑하면 운영 가시성이 더 좋아집니다. A/B 실험을 하는 경우에는 `experiment_group` 필드를 추가하면 실험군별 비용과 실패율을 분리할 수 있습니다.

## 로그 스키마를 운영 계약으로 고정하기

초기에는 로그 필드가 자주 바뀝니다. 새 기능이 추가되면 필드가 늘고, 불필요한 필드는 빠집니다. 하지만 운영으로 넘어가면 이야기가 달라집니다. 대시보드 패널, 알림 규칙, 주간 리뷰 쿼리가 모두 특정 필드 이름에 의존하고 있기 때문입니다.

그래서 스키마 자체를 코드로 고정하는 편이 안전합니다.

```python
from dataclasses import dataclass, asdict
from typing import Literal

@dataclass
class LLMLogRecord:
    """LLM 호출 한 건의 운영 계약 스키마. 필드 변경은 PR 리뷰 필수."""
    schema_version: str          # "v2" — 로그 소비자가 파싱 버전을 확인
    service: str                 # "chat-api"
    environment: str             # "production" | "staging"
    event: Literal["llm_request", "llm_response", "llm_error"]
    request_id: str
    model: str
    provider: str                # "groq" | "openai" | "anthropic"
    route: str                   # "/api/chat" | "/api/summarize"
    prompt_version: str
    latency_ms: float | None
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    estimated_cost_usd: float | None
    schema_ok: bool | None
    status: Literal["ok", "error"]
    error_type: str | None
    prompt_preview: str | None   # 최대 80자
    response_preview: str | None # 최대 120자
    user_tier: str | None        # "free" | "pro" | "enterprise"

def to_json_payload(record: LLMLogRecord) -> dict:
    return asdict(record)
```

이 dataclass가 "운영 계약"인 이유는, 필드를 추가하거나 삭제할 때 코드 변경이 필요하기 때문입니다. Pull Request에서 리뷰어가 "이 필드 제거하면 대시보드 패널 3개가 깨진다"고 말할 수 있는 구조가 됩니다.

`schema_version` 필드가 들어가는 이유도 같습니다. 로그 소비자(대시보드, 알림, 분석 쿼리)가 "이 로그는 v2 스키마다"를 알 수 있으면, 스키마 마이그레이션을 점진적으로 할 수 있습니다.

## OpenTelemetry trace를 로그와 연결하기

메트릭과 로그만으로 원인을 좁히기 어려운 구간에서는 trace가 도움이 됩니다. 특히 요청이 프롬프트 구성 → 검색 → 모델 호출 → 후처리 여러 단계를 거칠 때, 각 span의 시간을 분리해서 봐야 병목을 찾을 수 있습니다.

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("llm-app")

def traced_llm_call(client, prompt: str, route: str, prompt_version: str) -> dict:
    with tracer.start_as_current_span("chat.request") as span:
        span.set_attribute("llm.model", MODEL)
        span.set_attribute("llm.route", route)
        span.set_attribute("llm.prompt_version", prompt_version)
        span.set_attribute("llm.prompt_length", len(prompt))
        result = ask_llm(client, prompt, route=route, prompt_version=prompt_version)
        span.set_attribute("llm.total_tokens", result["total_tokens"])
        span.set_attribute("llm.latency_ms", result["latency_ms"])
        span.set_attribute("llm.schema_ok", result["schema_ok"])

        trace_id = format(span.get_span_context().trace_id, "032x")
        LOGGER.info(
            "llm_trace_link",
            extra={"payload": {"request_id": result["request_id"], "trace_id": trace_id}},
        )
        return result
```

핵심은 `request_id`와 `trace_id`를 동시에 남겨서, 로그에서 trace로, trace에서 로그로 양방향 이동이 가능하도록 만드는 습관입니다. 운영에서는 exporter를 OTLP로 바꿔서 Jaeger, Tempo, Datadog APM 어디로든 보낼 수 있습니다.

## 지연 시간 분석 — 분포로 보기

평균 지연 시간은 운영 지표로 위험합니다. P95 또는 P99를 추적해야 "느린 요청이 얼마나 있는가"를 제대로 볼 수 있습니다.

```python
from statistics import median, stdev

def analyze_latency(latencies: list[float]) -> dict:
    """지연 시간 분포 분석. 평균이 아닌 분위수로 봐야 이상 요청이 보입니다."""
    if not latencies:
        return {}
    sorted_lat = sorted(latencies)
    n = len(sorted_lat)

    def pct(p: float) -> float:
        return sorted_lat[max(0, int(n * p) - 1)]

    mean = sum(sorted_lat) / n
    sd = stdev(sorted_lat) if n > 1 else 0.0
    outliers = [v for v in sorted_lat if v > mean + 2 * sd]

    return {
        "count": n,
        "p50_ms": pct(0.50),
        "p75_ms": pct(0.75),
        "p95_ms": pct(0.95),
        "p99_ms": pct(0.99),
        "mean_ms": round(mean, 1),
        "stdev_ms": round(sd, 1),
        "outlier_count": len(outliers),
        "outlier_ratio": round(len(outliers) / n, 4),
    }
```

이 함수가 반환하는 `outlier_ratio`가 0.05를 넘으면 (즉 요청의 5% 이상이 평균 + 2표준편차를 초과하면) 그 원인을 추적해야 합니다. 통상적으로는 긴 입력 프롬프트, 모델 API 부하, 또는 응답 길이 급증이 원인입니다.

## 장애 대응 — 질의 템플릿을 미리 준비하기

로그와 대시보드가 있어도, 장애 상황에서 "뭘 먼저 조회하지?"가 정해져 있지 않으면 대응이 느려집니다. 사람은 압박 상황에서 최적의 쿼리를 즉석에서 만들지 못합니다. 그래서 운영팀은 반복적으로 묻는 질문을 "질의 템플릿"으로 사전에 문서화해 둬야 합니다.

### 운영 회고에서 자주 쓰는 질의 4가지

1. **같은 `prompt_version`에서 `latency_p95_ms`가 급증한 시간대는 언제인가** — 프롬프트 변경이 지연의 원인인지 확인합니다.
2. **`estimated_cost_usd` 상위 요청은 어떤 route에서 나왔는가** — 비용 급증의 진원지를 특정합니다.
3. **`schema_ok=false`가 특정 모델에 집중되는가** — 모델 교체 후 출력 포맷 호환성을 점검합니다.
4. **`completion_tokens` 급증이 특정 `user_tier`와 연결되는가** — 사용 패턴 변화와 비용을 분리합니다.

이 네 질문에 10분 안에 답할 수 있으면 모니터링 체계가 성숙한 편입니다. 반대로, 이 질문에 답하려고 로그 구조를 먼저 뜯어고쳐야 한다면 대시보드보다 로그 계약부터 다시 정리하는 게 맞습니다.

### 대시보드 최소 설정 예시 (Grafana/Loki 기준)

```yaml
dashboard: llm-ops-overview
widgets:
  - name: requests_per_min
    query: count_over_time({event="llm_response"}[1m])
    alert:
      condition: "< 1 for 5m"
      message: "트래픽이 없습니다 — 서비스 장애 의심"

  - name: error_rate
    query: |
      sum(rate({event="llm_error"}[5m]))
      /
      sum(rate({event=~"llm_response|llm_error"}[5m]))
    alert:
      condition: "> 0.03 for 5m"
      message: "에러율 3% 초과"

  - name: p95_latency_ms
    query: quantile_over_time(0.95, {event="llm_response"} | unwrap latency_ms [5m])
    alert:
      condition: "> 2500 for 10m"
      message: "P95 지연 2.5초 초과"

  - name: total_tokens_per_min
    query: sum_over_time({event="llm_response"} | unwrap total_tokens [1m])

  - name: cost_per_hour
    query: sum_over_time({event="llm_response"} | unwrap estimated_cost_usd [1h])
    alert:
      condition: "> 50 for 1h"
      message: "시간당 비용 $50 초과"

  - name: schema_fail_rate
    query: |
      sum(rate({event="llm_response", schema_ok="false"}[5m]))
      /
      sum(rate({event="llm_response"}[5m]))
    alert:
      condition: "> 0.05 for 10m"
      message: "스키마 실패율 5% 초과 — 출력 품질 저하"

  - name: top_error_types
    query: topk(5, sum by (error_type) (rate({event="llm_error"}[10m])))
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

## 실무에서 자주 겪는 혼동

**"로그만 잘 남기면 운영 끝"이라는 착각.** 로그는 "왜"를 설명하지만, "언제"를 먼저 알려주는 건 메트릭입니다. 메트릭이 없으면 사용자 제보가 들어올 때까지 이상 징후를 모릅니다. 두 가지가 함께 있어야 합니다.

**응답 전문을 로그에 저장하는 실수.** 1,000자짜리 LLM 응답을 로그에 전부 남기면, 하루 트래픽 10,000건 기준으로 10MB 이상이 로그 스토리지에 쌓입니다. 미리보기(120자)와 별도 스토리지(S3, BigQuery)를 나눠야 합니다.

**`schema_ok` 필드 없이 운영하는 실수.** 200 응답이 나왔어도 응답 내용이 기대 형식을 벗어났는지 추적하지 않으면, 품질 저하를 수 주 뒤에야 발견합니다.

**평균 지연 시간만 추적하는 실수.** P95가 없으면 "느린 사용자"를 탐지하지 못합니다. 평균이 300ms여도 P99가 8,000ms일 수 있습니다.

## 운영 체크리스트

- [ ] 모든 LLM 호출에 `request_id`, `model`, `route`, `prompt_version`, `latency_ms`, `total_tokens`를 남기고 있다
- [ ] 응답 전문 대신 preview 로깅을 기본값으로 쓰고 있다
- [ ] 성공 이벤트와 실패 이벤트가 같은 JSON 스키마를 공유한다
- [ ] 평균 지연 시간과 별도로 P95, P99 지연 시간을 추적하고 있다
- [ ] `schema_ok` 필드로 출력 형식 실패율을 별도 추적하고 있다
- [ ] `prompt_version`을 요청마다 기록하고 있다
- [ ] 대시보드에 비용(시간당), 에러율, 지연, 스키마 실패율 알람이 연결되어 있다
- [ ] 장애 시 10분 안에 답할 질의 템플릿이 문서화되어 있다
- [ ] `request_id`와 `trace_id`가 연결되어 로그→트레이스 양방향 이동이 가능하다

## 정리

로그 한 줄을 LLM 호출 한 건의 운영 계약서라고 보면, 비용·지연·디버깅 질문이 흩어지지 않습니다. 이 글에서는 왜 전통 API 로그로는 부족한가부터 장애 대응 질의 템플릿까지, 이 원칙을 구체적으로 살펴봤습니다. 핵심은 개념을 외우는 것이 아니라 실무에서 어떤 판단을 바꾸는지 이해하는 데 있습니다.

## 처음 질문으로 돌아가기

- **같은 200 응답인데 어떤 요청은 비싸고 어떤 요청은 품질이 낮다면, 로그에 어떤 필드가 있어야 이 차이를 설명할 수 있을까요?**
  - `prompt_tokens`, `completion_tokens`, `schema_ok`, `route`, `prompt_version` 다섯 필드가 있어야 "이 요청이 왜 비쌌고, 품질은 어땠는가"를 한 줄로 설명할 수 있습니다. 이 중 하나라도 빠지면 그 질문에 대한 답이 사라집니다.

- **"어제까지 잘 되던 응답이 오늘 이상해졌다"는 보고가 들어왔을 때, 원인을 프롬프트 변경인지 모델 변경인지 10분 안에 분리할 수 있는 로그 구조는 무엇일까요?**
  - `prompt_version`과 `model`이 모든 요청 로그에 기록되어 있어야 합니다. 이 두 필드로 필터링하면 "어제의 v1.0 + gpt-4o-mini 조합"과 "오늘의 v1.1 + gpt-4o-mini 조합"을 분리해서 품질과 비용을 비교할 수 있습니다.

- **메트릭이 "이상하다"고 알려주고 로그가 "왜 이상한지" 설명하는 역할 분담은 구체적으로 어떻게 만들까요?**
  - 메트릭(P95 지연, 에러율, 시간당 비용)이 이상을 먼저 탐지하고, 로그(`latency_ms` 높은 요청의 `model`, `prompt_version`, `total_tokens`)가 원인을 설명하는 순서입니다. 이 순서를 대시보드 레이아웃에도 반영하면 됩니다 — 상단에 메트릭 요약, 하단에 로그 필터가 오는 구조입니다.

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
