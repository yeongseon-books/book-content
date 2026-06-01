---
title: "LLM Apps Ops 101 (1/6): Monitoring and logging for LLM apps"
series: llm-apps-ops-101
episode: 1
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- LLMOps
- Observability
- Python
- LLM
last_reviewed: '2026-05-01'
seo_description: Treat one log line as the operating contract for one LLM call, and
  cost, latency, and debugging questions stop fragmenting across separate systems.
---

# LLM Apps Ops 101 (1/6): Monitoring and logging for LLM apps

Once an LLM app moves beyond a demo, the first real operations problem is not the outage itself. It is the inability to reconstruct what happened for one request across latency, token usage, and debugging context.

This is the first post in the LLM Apps Ops 101 series. Here, we will define the logging and monitoring baseline that makes each model call traceable after the fact.

![Monitoring and logging component layout](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/01/01-01-big-picture.en.png)
*Monitoring and logging component layout*
> Treat one log line as the operating contract for one LLM call, and cost, latency, and debugging questions stop fragmenting.

## Questions to Keep in Mind

- Which fields belong in every LLM request log?
- How do you tie latency, token usage, and response preview into one record?
- What log shape survives a later move to Datadog, BigQuery, or Elasticsearch?

## Why this layer matters
![Request and response logs per call](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/01/01-01-why-this-layer-matters.en.png)

*Request and response logs per call*
Observability starts with a log record that can fully explain one call after the fact.

A normal API can often get away with status code and response time. An LLM app cannot. Two calls may both succeed with HTTP 200 while one burns far more tokens or returns a suspiciously short answer.

Example file: `en/01-monitoring-and-logging/main.py`

## Minimal runnable example
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

## What to notice in this code
![Shared log schema for operating questions](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/01/01-02-what-to-notice-in-this-code.en.png)

*Shared log schema for operating questions*
- `JsonFormatter` keeps every event in one schema, so downstream ingestion stays simple.
- Putting `request_id` and `total_tokens` in the same record keeps debugging and cost analysis connected.
- Logging a short preview instead of the full answer reduces both data leakage risk and log volume.

The real point of this example is not the logging library API. It is the decision about which information to capture at request-start and response-end so that later questions have answers. When `latency_ms`, `model`, `prompt_preview`, `response_preview`, and `total_tokens` live in the same structure, you can answer "why was it slow?", "why was it expensive?", and "what did it say?" from one source.

## Where engineers get confused
![Metrics and logs narrow failures together](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/01/01-03-where-engineers-get-confused.en.png)

*Metrics and logs narrow failures together*
- Structured logs do not replace metrics. Metrics show trends; logs explain individual failures.
- Token counts include system instructions and generated output, not just the visible user prompt.
- Full-response logging feels convenient early on, but it becomes a privacy and storage liability fast.

A common misconception is that good logs eliminate the need for metrics. In practice, metrics surface the anomaly first and logs explain the cause. Average latency might look fine while P95 spikes silently—metrics catch that first, and logs explain which requests were slow.

## Fixing the dashboard axes before decorating panels

A monitoring dashboard becomes useful not when it looks polished, but when the questions it must answer are locked in first. In LLM operations, the three questions that repeat most often are:

1. Where is response latency growing right now?
2. Which endpoint-model combination is spiking in cost?
3. Does quality degradation correlate with a specific user cohort or prompt version?

Answering these maps directly to three panel axes: **latency**, **token/cost**, and **quality**. The latency axis should at minimum show p50, p95, and p99, splitting pre-processing time from provider response time. The token/cost axis should display `input_tokens`, `output_tokens`, and `estimated_cost_usd` alongside request count. The quality axis should carry fast-to-compute signals: length-failure rate, schema-failure rate, and keyword-miss rate.

In practice, the longer these three axes live on separate screens, the slower root-cause analysis becomes. If p95 rises at the same moment output tokens rise, the model's output length is likely the primary driver. If latency is stable but cost rises, the input prompt may have grown or cache hit rate may have dropped. The real purpose of a dashboard is not pretty visualization—it is overlaying different operations signals on the same time axis so correlation jumps out.

### Connecting per-request logs to panel-level aggregates

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

This code is not flashy, but it captures an operational baseline you can reuse immediately. Grouping by `route + model + prompt_version` lets the dashboard reveal which prompt version is moving both latency and cost at once. The same aggregation logic ports to Datadog, Grafana, or BigQuery without rework.

## Elevating prompt version management to a log contract

"The answers are different today" is a routine complaint in LLM services. The difficulty is separating whether the change comes from a model version update, a system prompt edit, or a few-shot example swap. That is why `prompt_version` should be treated as a contractual log field, not an optional annotation.

The most practical pattern is to bump `prompt_version` with each deployment unit and record `prompt_version`, `model`, `temperature`, and `max_tokens` on every request. This makes it possible to run regression analysis connecting cost spikes, latency increases, or quality drops directly to a prompt change. For A/B experiments, adding an `experiment_group` field lets you isolate failure rates and costs per cohort safely.

Mapping prompt versions 1:1 to Git tags improves operational visibility further. A version like `prompt_version=v2026.05.20-briefing` embeds both date and intent; combined with release notes that record the change purpose, post-incident explanation cost drops significantly. Once enough logs accumulate, you can answer trade-off questions like "which prompt was expensive but high quality?" with actual numbers.

## Preparing incident-response query templates in advance

Logs and dashboards exist, but if the team has not decided what to query first during an incident, response speed suffers. Operations teams benefit from pre-documenting "query templates"—queries they can fire immediately when something breaks. Examples:

- request_ids where p95 latency doubled in the last 30 minutes
- Top 20 requests by cost and their common `prompt_version`
- User segments where `schema_fail` occurred
- Time windows where `latency_p95_ms` spiked for the same `prompt_version`

The format—SQL, log explorer query, or PromQL—does not matter. What matters is that the questions are fixed. Fixed questions lock in the required log fields in reverse, and log instrumentation quality stabilizes as a result.

If your team can answer those four queries within 10 minutes, the monitoring system is fairly mature. If answering them requires restructuring the log schema first, fix the log contract before building more dashboard panels.

## Reading logs in ops review meetings: a practical sequence

In weekly ops reviews, more data can actually blur conclusions. A fixed reading order helps. First, check macro indicators: latency trends and error rates. Second, overlay cost signals—did cost grow disproportionately to traffic? Third, correlate quality metrics with prompt version to spot regressions. Only in the final step open sample log lines to read concrete cases.

This order matters because starting from individual logs draws attention to local anomalies. Working top-down from macro trends ensures the team discusses causes from the same context.

Record review outcomes in three columns: **observation**, **hypothesis**, **experiment**. For example: "Observation: p95 up + output tokens up. Hypothesis: prompt version v2026.05.20 encourages verbose answers. Experiment: apply output length cap and simplify instructions." This structure lets next week's review compare the effect using the same format.

## Checklist
- [ ] Always log request_id, model, latency_ms, and total_tokens
- [ ] Log previews instead of full answers by default
- [ ] Keep success and error events in the same schema
- [ ] Track P95 latency separately from average latency

## Summary

The goal is not pretty logs. The goal is one record shape that can answer later questions about incidents, cost spikes, and model behavior.

### Locking the structured log schema as an operating contract

Early on, log fields change often. But once a service enters production, field additions and removals must be managed strictly. The safest approach is to document the per-request schema and include a version field. Fixing `schema_version`, `service`, `environment`, `provider`, and `status` prevents dashboards and alert rules from breaking when someone adds a new field.

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

With this structure, `llm_request` events leave latency and token fields as `None`, then `llm_response` fills them in. Error events (`llm_error`) keep the same key set so queries stay simple.

### Connecting OpenTelemetry traces to logs

When metrics and logs alone cannot narrow the bottleneck, traces help. Especially when a request passes through prompt assembly, retrieval, model call, and post-processing stages, each span's duration must be visible separately. The key is to write `trace_id` into the log alongside `request_id` so cross-lookup is possible.

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

In production, swap the exporter to OTLP targeting Jaeger, Tempo, or Datadog APM. The important habit is not the tool choice but recording `request_id` and `trace_id` together so a single request's logs and traces can be cross-referenced.

### Minimal dashboard configuration

A dashboard does not need to start complex. Pin request rate, error rate, P95 latency, token usage, and per-model cost trends first—these are enough to sort questions quickly in an ops meeting.

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

Start with this minimal template so the team talks about the same numbers. Add per-tenant, per-model, and per-prompt-version breakdowns incrementally afterward.

## Answering the Opening Questions

- **Which fields belong in every LLM request log?**
  - At minimum, keep request_id, model, prompt and completion tokens, latency, status, error, response preview, and user or tenant keys.
- **How do you tie latency, token usage, and response preview into one record?**
  - Use one request_id for start and completion events, then record provider usage and measured latency in the same JSON record or joinable events.
- **What log shape survives a later move to Datadog, BigQuery, or Elasticsearch?**
  - A stable typed JSON schema survives best. If field names and request_id stay consistent, the backend can change without losing analysis.

<!-- toc:begin -->
## In this series

- **LLM Apps Ops 101 (1/6): Monitoring and logging for LLM apps (current)**
- LLM Apps Ops 101 (2/6): LLM cost tracking and optimization (upcoming)
- LLM Apps Ops 101 (3/6): Evaluating LLM output quality (upcoming)
- LLM Apps Ops 101 (4/6): LLM app security (upcoming)
- LLM Apps Ops 101 (5/6): LLM app deployment strategies (upcoming)
- LLM Apps Ops 101 (6/6): Completing the LLM ops pipeline (upcoming)

<!-- toc:end -->

---

## References

- [Groq API Reference](https://console.groq.com/docs/api-reference)
- [Python logging cookbook](https://docs.python.org/3/howto/logging-cookbook.html)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)

### Related Series

- [AI Evaluation 101](../../ai-evaluation-101/en/01-why-evaluate-llm-apps.md) — covers how to measure the "LLM quality" this series monitors at runtime, but earlier in the lifecycle. Useful when an ops metric wobbles and you need an evaluation method to confirm whether it counts as a regression.

Tags: LLMOps, Observability, Python, LLM
