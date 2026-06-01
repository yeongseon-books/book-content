---
title: "LLM Apps Ops 101 (6/6): Completing the LLM ops pipeline"
series: llm-apps-ops-101
episode: 6
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
seo_description: Operational maturity is not about stacking features. It is about
  making one request produce connected signals for validation, cost, quality, and
  logs.
---

# LLM Apps Ops 101 (6/6): Completing the LLM ops pipeline

Individual operational layers can look fine in isolation and still leave incidents hard to explain. The real milestone is getting one request to emit connected signals for safety, cost, quality, and logging.

This is the final post in the LLM Apps Ops 101 series. Here, we will connect the earlier pieces into one integrated operations pipeline.

![LLM ops pipeline complete overview](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/06/06-01-big-picture.en.png)
*LLM ops pipeline complete overview*
> LLM operations is not adding many layers; it is explaining one request across cost, quality, security, and deployment signals.

## Questions to Keep in Mind

- Which layers must a complete LLM operations pipeline connect inside one request?
- What operations gap appears when monitoring, cost, evaluation, security, and deployment stay separate?
- What cumulative signals should the health state of a minimal operations app expose?

## Why this layer matters
![Ops flow from validation to logging](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/06/06-01-why-this-layer-matters.en.png)

*Ops flow from validation to logging*
An integrated pipeline matters because one request should leave connected traces for validation, cost, quality, and logging.

When each operational layer lives alone, demos look clean but incidents stay hard to explain. In production, you need one place to tell whether a bad outcome came from unsafe input, rising cost, or degrading output quality.

Example file: `en/06-ops-complete/main.py`

## Minimal runnable example
```python
import asyncio
import json
import logging
import os
import re
import threading
import time
from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from groq import Groq

MODEL = "llama-3.1-8b-instant"
PRICE_PER_MILLION_TOKENS = 0.05
INJECTION_PATTERNS = [r"ignore\s+all\s+previous\s+instructions", r"reveal\s+your\s+system\s+prompt"]

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
    logger = logging.getLogger("llm_ops_pipeline")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    logger.propagate = False
    return logger

LOGGER = build_logger()

@dataclass
class QualityReport:
    length_ok: bool
    keywords_ok: bool
    answer_length: int
    missing_keywords: list[str]

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    expected_keywords: list[str] = Field(default_factory=list)

class ChatResponse(BaseModel):
    response: str
    total_tokens: int
    cost_usd: float
    quality: dict

def estimate_cost(total_tokens: int) -> float:
    return round((total_tokens / 1_000_000) * PRICE_PER_MILLION_TOKENS, 8)

def validate_input(text: str) -> None:
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            raise HTTPException(status_code=400, detail="prompt injection detected")

def evaluate_output(answer: str, expected_keywords: list[str]) -> QualityReport:
    missing = [keyword for keyword in expected_keywords if keyword.lower() not in answer.lower()]
    return QualityReport(
        length_ok=60 <= len(answer) <= 400,
        keywords_ok=not missing,
        answer_length=len(answer),
        missing_keywords=missing,
    )

def call_model(client: Groq, message: str) -> tuple[str, int]:
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": "You are a concise Python assistant."},
            {"role": "user", "content": message},
        ],
    )
    usage = response.usage
    if usage is None:
        raise RuntimeError("usage metadata missing from Groq response")
    answer = response.choices[0].message.content or ""
    return answer, usage.total_tokens

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = Groq(api_key=os.environ["GROQ_API_KEY"])
    app.state.total_calls = 0
    app.state.total_cost_usd = 0.0
    yield

app = FastAPI(title="llm-ops-pipeline", lifespan=lifespan)

class ThreadSafeServer(uvicorn.Server):
    def install_signal_handlers(self) -> None:
        return None

@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "total_calls": app.state.total_calls,
        "total_cost_usd": round(app.state.total_cost_usd, 8),
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    validate_input(request.message)
    started = time.perf_counter()
    answer, total_tokens = await asyncio.to_thread(call_model, app.state.client, request.message)
    quality = evaluate_output(answer, request.expected_keywords)
    cost_usd = estimate_cost(total_tokens)
    app.state.total_calls += 1
    app.state.total_cost_usd += cost_usd
    LOGGER.info(
        "llm_call",
        extra={
            "payload": {
                "latency_ms": round((time.perf_counter() - started) * 1000, 1),
                "total_tokens": total_tokens,
                "cost_usd": cost_usd,
                "quality": asdict(quality),
            }
        },
    )
    return ChatResponse(
        response=answer,
        total_tokens=total_tokens,
        cost_usd=cost_usd,
        quality=asdict(quality),
    )

def run_server(server: uvicorn.Server) -> None:
    server.run()

def main() -> None:
    config = uvicorn.Config(app, host="127.0.0.1", port=8016, log_level="warning")
    server = ThreadSafeServer(config)
    thread = threading.Thread(target=run_server, args=(server,), daemon=True)
    thread.start()

    for _ in range(40):
        try:
            health = httpx.get("http://127.0.0.1:8016/health", timeout=2.0)
            if health.status_code == 200:
                break
        except Exception:
            time.sleep(0.25)
    else:
        raise RuntimeError("server did not start")

    print("HEALTH:", health.json())
    response = httpx.post(
        "http://127.0.0.1:8016/chat",
        json={
            "message": "Explain Python's GIL in two sentences.",
                    "expected_keywords": ["GIL", "thread", "lock"],
        },
        timeout=30.0,
    )
    print("CHAT:", response.json())
    final_health = httpx.get("http://127.0.0.1:8016/health", timeout=2.0)
    print("FINAL_HEALTH:", final_health.json())

    server.should_exit = True
    thread.join(timeout=10)
    if thread.is_alive():
        raise RuntimeError("server did not stop cleanly")

if __name__ == "__main__":
    main()
```

## What to notice in this code
![Health state exposes cumulative calls and cost](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/06/06-02-what-to-notice-in-this-code.en.png)

*Health state exposes cumulative calls and cost*
- Returning `quality`, `total_tokens`, and `cost_usd` in one response gives both server and client immediate operating context.
- Adding cumulative call count and cost to `/health` makes state changes visible even in a tiny demo.
- The structured `quality` payload can later be aligned with batch evaluation jobs and dashboards.

The most important instinct this example builds is "do not break the signal chain of a single request." If input validation fails, the flow stops before the model call. If it passes, cost and quality are computed, and those results feed back into structured logs and health state. Without that link, an operator must cross-reference separate systems to explain one request's full lifecycle.

## Establish the baseline for your integrated ops pipeline

At the operations-completion stage, "connection" matters more than "existence" of each layer. Security, cost, evaluation, and logging can each work fine individually, but if they are not joined by `request_id`, incident response speed does not improve meaningfully. The baseline document must therefore be a data-flow contract, not a feature list.

The first contract to lock is the set of common fields: `request_id`, `trace_id`, `user_tier`, `model`, `prompt_version`, `input_tokens`, `output_tokens`, `estimated_cost_usd`, `policy_decision`, `evaluation_status`. When all layers emit these fields consistently, cross-store joins become possible later.

A gap teams commonly miss: different teams using the same field name with different semantics. For example, one team's `success` means HTTP 200, while another's `success` includes passing evaluation. The integrated pipeline must define such terms upfront and reflect them identically in docs and code.

## Combine cost, quality, and security into one check report

Metrics built across the series should converge into a single check report at the end. Instead of opening five dashboards during a morning review, read key metrics on one page and drill into anomalies from there.

### Daily ops report example

```python
def build_daily_ops_report(rows: list[dict]) -> dict:
    total = len(rows)
    if total == 0:
        return {"status": "no-traffic"}

    blocked = sum(1 for r in rows if not r.get("input_allowed", True) or not r.get("output_allowed", True))
    eval_fail = sum(1 for r in rows if r.get("evaluation_status") in {"fail-fast", "review"})
    total_cost = sum(float(r.get("estimated_cost_usd", 0.0)) for r in rows)
    p95_latency = sorted(r.get("latency_ms", 0) for r in rows)[max(0, int(total * 0.95) - 1)]

    return {
        "request_count": total,
        "blocked_rate": round(blocked / total, 4),
        "evaluation_attention_rate": round(eval_fail / total, 4),
        "cost_total_usd": round(total_cost, 4),
        "latency_p95_ms": p95_latency,
    }
```

Keeping the report structure simple speeds up cross-team communication. When someone asks "why did cost rise today," evaluation failure rate, block rate, and latency are visible on the same table.

## Track prompt version and deployment version together

In LLM operations, code deployments and prompt deployments move at different speeds. The same code with a different prompt can produce wildly different operational outcomes. The final stage therefore requires tracking `deployment_id` and `prompt_version` together.

The recommended approach: declare prompt version in deployment metadata and record both values in every request log. This lets you quickly narrow "quality is drifting but no code changed" to a prompt change. Conversely, when the prompt is unchanged but code differs, investigate infrastructure or library changes first.

## Exit criteria for judging operational maturity

The most important question when closing this series is: "what must be true for operations to be considered complete?" Practical exit criteria:

- You can trace a single request through `security decision → model call → cost calculation → quality evaluation → log record`.
- Within 30 minutes of an incident, you can present blast radius and cause hypothesis with data.
- Before deploying a new prompt version, regression evaluation and security tests pass automatically.
- Cost spikes, quality drops, and block-rate anomalies trigger threshold-based alerts automatically.

When these four are met, operations no longer depend on "the experienced person's intuition." The team can produce the same quality with the same procedure regardless of personnel changes — and that is the practical meaning of LLM app operations completion.
## Where engineers get confused
![Deploy monitor evaluate optimize redeploy loop](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/06/06-03-where-engineers-get-confused.en.png)

*Deploy monitor evaluate optimize redeploy loop*
- An integrated pipeline does not remove the need for storage, alerts, and dashboards. It just gives them better signals.
- Inline evaluation improves visibility but can add latency. Production systems often split synchronous and asynchronous checks.
- A simple cost formula is fine for the demo, but real billing models may require input/output separation and model-specific tables.

The most common misconception at this stage is "all operational problems are now solved." The integrated pipeline is a starting point, not a finish line. What you gain now is a consistent signal that can feed into storage, alerts, and dashboards. On top of that you still need long-term retention, trend analysis, batch evaluation, and cost alerting to truly reach production operations maturity.

## Clarify team operating model and responsibility boundaries

Even when the integrated pipeline is technically complete, ambiguous responsibility boundaries slow real incident response. The final step is defining roles and decision boundaries.

Recommended model: the application team owns prompts and evaluation criteria, the platform team owns deployment and observability infrastructure, and the security team owns policy rules and incident response procedures. However, the per-request log schema must be co-owned — if any one team changes fields unilaterally, the entire pipeline breaks.

Operations meetings also need common metrics. If teams look at different numbers, they interpret the same incident differently. Fix a weekly-meeting template with `cost`, `quality`, `latency`, `security`, `deployment stability` items referencing the same data source.

Ultimately, operations completion is not about adopting more tools. It is about reaching an organizational state where the same event is explained with the same data and acted on with the same rules. Once you reach that point, the LLM app transitions from an experimental service to a repeatable product operation.
## Checklist
- [ ] Validate input before the model call
- [ ] Compute total_tokens and cost_usd for every response
- [ ] Log the quality report in structured form
- [ ] Expose cumulative state in /health

## Criteria for building a next-quarter ops roadmap

After operations completion, "what to stabilize" matters more than "what to build." The next-quarter roadmap should be framed as operational-metric improvement targets rather than feature lists.

For example: `evaluation failure rate down 30%`, `cost prediction error below 10%`, `security false-positive rate down 20%`, `deployment rollback time under 15 minutes`. Numeric targets keep the team moving in the same direction. Each goal must also name a responsible team and measurement cadence to create execution accountability.

Teams with mature ops can also iterate on new model adoption and prompt experiments faster — because they detect failures early and roll back safely. Good operations is not a brake on innovation; it is a safety harness that enables faster experimentation.

## Summary
At this point one request leaves a full operational trail. From here, the next step is persistence, alerting, and dashboards rather than new endpoint logic.

## Answering the Opening Questions

- **Which layers must a complete LLM operations pipeline connect inside one request?**
  - Input validation, security guards, model calls, cost accounting, quality evaluation, log records, and health reporting must connect inside one request.
- **What operations gap appears when monitoring, cost, evaluation, security, and deployment stay separate?**
  - Metrics cannot be joined, so root cause, cost spikes, quality drops, and security blocks become separate stories.
- **What cumulative signals should the health state of a minimal operations app expose?**
  - Expose cumulative calls, errors, total cost, average latency, recent blocks, and last provider status.

<!-- toc:begin -->
## In this series

- [LLM Apps Ops 101 (1/6): Monitoring and logging for LLM apps](./01-monitoring-and-logging.md)
- [LLM Apps Ops 101 (2/6): LLM cost tracking and optimization](./02-cost-tracking.md)
- [LLM Apps Ops 101 (3/6): Evaluating LLM output quality](./03-evaluation.md)
- [LLM Apps Ops 101 (4/6): LLM app security](./04-security.md)
- [LLM Apps Ops 101 (5/6): LLM app deployment strategies](./05-deployment.md)
- **LLM Apps Ops 101 (6/6): Completing the LLM ops pipeline (current)**

<!-- toc:end -->

---

## References

- [FastAPI](https://fastapi.tiangolo.com/)
- [Groq API Reference](https://console.groq.com/docs/api-reference)
- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

Tags: LLMOps, Observability, Python, LLM
