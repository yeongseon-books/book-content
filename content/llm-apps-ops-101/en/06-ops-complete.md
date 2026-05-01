---
title: 'Completing the LLM ops pipeline'
series: llm-apps-ops-101
episode: 6
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

# Completing the LLM ops pipeline

> LLM Apps Ops 101 (6/6)

This post assembles monitoring, cost tracking, quality evaluation, security, and deployment into a single production server. Each layer is independently replaceable; together they form a reliable operational foundation for any LLM app.

<!-- ebook-only:start -->

**The key idea**: LLMOps automates the develop → deploy → monitor → retrain loop. Collect feedback and trigger alerts when metrics degrade.

## Where this chapter fits

This is chapter 6 of 6 in the series.
The previous chapter covered **LLM app deployment strategies**.
<!-- ebook-only:end -->

## Example code
Example code: [github.com/yeongseon-books/llm-apps-ops-101](https://github.com/yeongseon-books/llm-apps-ops-101/tree/main/en)

---

## Integrated production server

```python
import asyncio
import functools
import json
import logging
import os
import re
import time
import uuid
from collections import defaultdict
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

# ── logger ─────────────────────────────────────────────────────────────────
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log = {"ts": datetime.utcnow().isoformat() + "Z", "level": record.levelname, "msg": record.getMessage()}
        if hasattr(record, "extra"):
            log.update(record.extra)
        return json.dumps(log)

def build_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        h = logging.StreamHandler()
        h.setFormatter(JsonFormatter())
        logger.addHandler(h)
    return logger

logger = build_logger("llm_prod")

# ── retry ──────────────────────────────────────────────────────────────────
def retry_backoff(max_retries: int = 2, base_delay: float = 1.0):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    if attempt == max_retries:
                        break
                    await asyncio.sleep(base_delay * (2 ** attempt))
            raise last_exc
        return wrapper
    return decorator

# ── rate limiter ────────────────────────────────────────────────────────────
class RateLimiter:
    def __init__(self, max_calls: int = 10, window: int = 60):
        self.max_calls = max_calls
        self.window = window
        self._calls: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, user_id: str) -> tuple[bool, str]:
        now = time.time()
        cutoff = now - self.window
        self._calls[user_id] = [t for t in self._calls[user_id] if t > cutoff]
        if len(self._calls[user_id]) >= self.max_calls:
            reset_in = int(self._calls[user_id][0] + self.window - now)
            return False, f"retry in {reset_in}s"
        self._calls[user_id].append(now)
        return True, ""

# ── input validation ────────────────────────────────────────────────────────
INJECTION_PATTERNS = [
    r"ignore\s+(?:all\s+)?(?:previous|prior)\s+instructions?",
    r"forget\s+everything",
    r"override\s+(?:safety|system)",
]

SENSITIVE_RE = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    r"|\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"
    r"|(?:sk|pk|api|key)[-_][A-Za-z0-9]{16,}",
    re.IGNORECASE,
)

def validate_input(text: str) -> tuple[bool, str, str]:
    if not text.strip():
        return False, "empty input", ""
    if len(text) > 4000:
        return False, f"input too long: {len(text)}", ""
    for pat in INJECTION_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return False, "prompt injection detected", ""
    return True, "", SENSITIVE_RE.sub("[REDACTED]", text)

# ── cost tracking ───────────────────────────────────────────────────────────
MODEL_PRICING = {"llama-3.1-8b-instant": {"input": 0.00005, "output": 0.00008}}

@dataclass
class CallRecord:
    call_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0
    model: str = "llama-3.1-8b-instant"

    @property
    def cost_usd(self) -> float:
        p = MODEL_PRICING.get(self.model, {"input": 0, "output": 0})
        return (self.input_tokens * p["input"] + self.output_tokens * p["output"]) / 1000

cumulative_cost = 0.0
total_calls = 0

# ── FastAPI ─────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    user_id: str = Field(default="anonymous")
    system_prompt: str = Field(default="You are a helpful assistant.")
    stream: bool = False

class ChatResponse(BaseModel):
    response: str
    call_id: str
    latency_ms: float
    cost_usd: float

rate_limiter = RateLimiter()

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.environ["GROQ_API_KEY"],
        temperature=0.0,
    )
    logger.info("server started")
    yield
    logger.info("server stopped")

app = FastAPI(title="LLM Production Server", lifespan=lifespan)

@app.middleware("http")
async def request_log(request: Request, call_next):
    t0 = time.perf_counter()
    resp = await call_next(request)
    ms = (time.perf_counter() - t0) * 1000
    logger.info(f"{request.method} {request.url.path}", extra={"status": resp.status_code, "ms": round(ms, 1)})
    return resp

@app.get("/health")
async def health():
    return {"status": "ok", "total_calls": total_calls, "cumulative_cost_usd": round(cumulative_cost, 4)}

@retry_backoff(max_retries=2)
async def _llm_call(llm, messages) -> tuple[str, dict]:
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, lambda: llm.invoke(messages))
    return response.content, getattr(response, "usage_metadata", {}) or {}

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    global cumulative_cost, total_calls

    allowed, reason = rate_limiter.is_allowed(req.user_id)
    if not allowed:
        raise HTTPException(status_code=429, detail=reason)

    ok, reason, sanitized = validate_input(req.message)
    if not ok:
        raise HTTPException(status_code=400, detail=reason)

    messages = [SystemMessage(content=req.system_prompt), HumanMessage(content=sanitized)]

    if req.stream:
        async def token_stream() -> AsyncIterator[str]:
            for chunk in app.state.llm.stream(messages):
                if chunk.content:
                    yield f"data: {chunk.content}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(token_stream(), media_type="text/event-stream")

    record = CallRecord()
    t0 = time.perf_counter()
    try:
        content, usage = await _llm_call(app.state.llm, messages)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM error: {e}")

    record.latency_ms = (time.perf_counter() - t0) * 1000
    record.input_tokens = usage.get("input_tokens", 0)
    record.output_tokens = usage.get("output_tokens", 0)
    cumulative_cost += record.cost_usd
    total_calls += 1

    logger.info("llm_call", extra={
        "call_id": record.call_id,
        "latency_ms": round(record.latency_ms, 1),
        "tokens": record.input_tokens + record.output_tokens,
        "cost_usd": round(record.cost_usd, 6),
    })

    return ChatResponse(
        response=content,
        call_id=record.call_id,
        latency_ms=round(record.latency_ms, 1),
        cost_usd=round(record.cost_usd, 6),
    )
```

---

## Running the server

```bash
pip install fastapi uvicorn langchain-groq pydantic

GROQ_API_KEY=<your_key> uvicorn server:app --host 0.0.0.0 --port 8000

curl http://localhost:8000/health

curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Python asyncio?", "user_id": "user_1"}'
```

---

## Series summary

The layers built across this series stack in order.

Monitoring and logging form the foundation — you cannot improve what you cannot see. Cost tracking sits on top and prevents budget overruns. Quality evaluation acts as a safety net when you change models or prompts. Security filters contain misuse. The deployment structure holds it all together in production.

Each layer is independently swappable. Replace the monitoring backend with Datadog, move the cache to Redis, or swap the retry logic for Tenacity — the rest continues working unchanged.

<!-- toc:begin -->
## In this series

- [Monitoring and logging for LLM apps](./01-monitoring-and-logging.md)
- [LLM cost tracking and optimization](./02-cost-tracking.md)
- [Evaluating LLM output quality](./03-evaluation.md)
- [LLM app security](./04-security.md)
- [LLM app deployment strategies](./05-deployment.md)
- **Completing the LLM ops pipeline (current)**

<!-- toc:end -->

---

## References

- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [LangChain productionization guide](https://python.langchain.com/docs/guides/productionization/)
- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

Tags: LLMOps, Observability, Python, LLM
