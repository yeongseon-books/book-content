---
title: 'Monitoring and logging for LLM apps'
series: llm-apps-ops-101
episode: 1
language: en
status: draft
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- LLMOps
- Observability
- Python
- LLM
last_reviewed: '2026-05-01'
---

# Monitoring and logging for LLM apps

> LLM Apps Ops 101 (1/6)

The moment you push an LLM app to production, monitoring becomes non-negotiable. Unlike standard web services, LLM apps have response times measured in seconds, token consumption that maps directly to cost, and non-deterministic outputs. This post builds a practical monitoring foundation: structured logs, latency tracking, and token accounting.

## Example code
Example code: [github.com/yeongseon-books/llm-apps-ops-101](https://github.com/yeongseon-books/llm-apps-ops-101/tree/main/en)

---

## Why LLM monitoring is different

A conventional API dashboard needs three numbers: status codes, response time, and throughput. LLM apps require more.

- **Token usage**: input and output tokens must be recorded separately to reverse-engineer cost.
- **Model parameters**: temperature and max_tokens alter outputs even with the same prompt.
- **Prompt version**: prompt changes need to be correlated with quality shifts.
- **Latency distribution**: P95 and P99 matter more than mean — they determine the experience for the tail.

---

## Structured logger

```python
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if hasattr(record, "extra"):
            log.update(record.extra)
        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)
        return json.dumps(log)

def build_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    return logger

logger = build_logger("llm_ops")

@dataclass
class LLMCallRecord:
    call_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    model: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: float = 0.0
    success: bool = True
    error: str = ""
    prompt_preview: str = ""
    response_preview: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

    def log(self):
        level = logging.INFO if self.success else logging.ERROR
        logger.log(
            level,
            "llm_call",
            extra={
                "extra": {
                    "call_id": self.call_id,
                    "model": self.model,
                    "prompt_tokens": self.prompt_tokens,
                    "completion_tokens": self.completion_tokens,
                    "total_tokens": self.total_tokens,
                    "latency_ms": round(self.latency_ms, 1),
                    "success": self.success,
                    "error": self.error,
                    "prompt_preview": self.prompt_preview[:120],
                    "response_preview": self.response_preview[:120],
                }
            },
        )
```

---

## Instrumented invoke wrapper

```python
import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

def instrumented_invoke(llm: ChatGroq, prompt: str) -> tuple[str, LLMCallRecord]:
    record = LLMCallRecord(model=llm.model_name, prompt_preview=prompt)
    t0 = time.perf_counter()
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        record.latency_ms = (time.perf_counter() - t0) * 1000
        record.response_preview = response.content

        usage = getattr(response, "usage_metadata", None)
        if usage:
            record.prompt_tokens = usage.get("input_tokens", 0)
            record.completion_tokens = usage.get("output_tokens", 0)

        record.success = True
        return response.content, record

    except Exception as e:
        record.latency_ms = (time.perf_counter() - t0) * 1000
        record.success = False
        record.error = str(e)
        raise
    finally:
        record.log()
```

---

## Latency histogram

Mean latency hides SLA violations. Track distributions.

```python
import math
from collections import defaultdict

class LatencyHistogram:
    BUCKETS = [100, 250, 500, 1000, 2000, 5000, float("inf")]

    def __init__(self):
        self._counts: dict[float, int] = defaultdict(int)
        self._total = 0.0
        self._n = 0
        self._min = float("inf")
        self._max = 0.0

    def record(self, ms: float):
        self._total += ms
        self._n += 1
        self._min = min(self._min, ms)
        self._max = max(self._max, ms)
        for b in self.BUCKETS:
            if ms <= b:
                self._counts[b] += 1
                break

    def percentile(self, p: float) -> float:
        if self._n == 0:
            return 0.0
        target = math.ceil(p / 100 * self._n)
        cumulative = 0
        prev_b = 0.0
        for b in self.BUCKETS:
            cumulative += self._counts[b]
            if cumulative >= target:
                ratio = (target - (cumulative - self._counts[b])) / max(self._counts[b], 1)
                return prev_b + ratio * (b - prev_b if b != float("inf") else prev_b)
            prev_b = b
        return self._max

    def summary(self) -> dict:
        return {
            "n": self._n,
            "mean_ms": round(self._total / self._n, 1) if self._n else 0,
            "min_ms": round(self._min, 1) if self._n else 0,
            "max_ms": round(self._max, 1),
            "p50_ms": round(self.percentile(50), 1),
            "p95_ms": round(self.percentile(95), 1),
            "p99_ms": round(self.percentile(99), 1),
        }
```

---

## Token budget tracker

```python
from dataclasses import dataclass

@dataclass
class TokenBudget:
    daily_limit: int
    used: int = 0

    @property
    def remaining(self) -> int:
        return max(0, self.daily_limit - self.used)

    @property
    def utilization(self) -> float:
        return self.used / self.daily_limit if self.daily_limit else 0.0

    def consume(self, tokens: int) -> bool:
        self.used += tokens
        if self.used > self.daily_limit:
            logger.warning("token_budget_exceeded", extra={"extra": {
                "used": self.used, "limit": self.daily_limit,
                "over": self.used - self.daily_limit,
            }})
            return False
        if self.utilization > 0.8:
            logger.warning("token_budget_80pct", extra={"extra": {
                "used": self.used, "limit": self.daily_limit,
            }})
        return True

    def report(self) -> dict:
        return {
            "used": self.used,
            "limit": self.daily_limit,
            "remaining": self.remaining,
            "utilization_pct": round(self.utilization * 100, 1),
        }
```

---

## End-to-end example

```python
histogram = LatencyHistogram()
budget = TokenBudget(daily_limit=50_000)

def run_with_monitoring(prompt: str) -> str:
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.environ["GROQ_API_KEY"],
        temperature=0.0,
    )
    content, record = instrumented_invoke(llm, prompt)
    budget.consume(record.total_tokens)
    histogram.record(record.latency_ms)
    return content

if __name__ == "__main__":
    questions = [
        "What is list comprehension in Python?",
        "Explain the difference between REST and GraphQL.",
        "What is the difference between Docker and a virtual machine?",
    ]
    for q in questions:
        ans = run_with_monitoring(q)
        print(f"\nQ: {q}")
        print(f"A: {ans[:200]}...")

    print("\n=== latency summary ===")
    print(json.dumps(histogram.summary(), indent=2))
    print("\n=== token budget ===")
    print(json.dumps(budget.report(), indent=2))
```

---

## Principles

**Instrument at design time, not as an afterthought.** Wrapping call sites with `instrumented_invoke` gives 100% coverage without touching business logic.

Structured logs are queryable without schema migrations. Whether you ship them to Elasticsearch, BigQuery, or Datadog, the JSON shape stays the same.

P95 and P99 are user-experience metrics. If your mean LLM call is 1 s but P99 is 8 s, one in a hundred users waits 8 s every time they interact.

<!-- blog-only:start -->
Next: [LLM cost tracking and optimization](./02-cost-tracking.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## In this series

- **Monitoring and logging for LLM apps (current)**
- LLM cost tracking and optimization (upcoming)
- Evaluating LLM output quality (upcoming)
- LLM app security (upcoming)
- LLM app deployment strategies (upcoming)
- Completing the LLM ops pipeline (upcoming)

<!-- toc:end -->

---

## References

- [LangChain Callbacks](https://python.langchain.com/docs/modules/callbacks/)
- [Groq API response metadata](https://console.groq.com/docs/api-reference)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)

Tags: LLMOps, Observability, Python, LLM
