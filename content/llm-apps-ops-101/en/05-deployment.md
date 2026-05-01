---
title: 'LLM app deployment strategies'
series: llm-apps-ops-101
episode: 5
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

# LLM app deployment strategies

> LLM Apps Ops 101 (5/6)

Moving an LLM app from local to production surfaces three recurring pain points: timeouts, concurrency, and retry handling. This post builds a deployable LLM server with FastAPI, exponential-backoff retries, streaming responses, and health checks.

---

## Deployment architecture

LLM API calls are inherently slow. Generating a response takes seconds, and network errors or rate limits (429) can strike at any time. A production server needs three capabilities.

- **Async processing**: handle other requests while one is waiting for the LLM.
- **Exponential backoff**: recover from transient failures automatically.
- **Streaming**: return the first token quickly to reduce perceived latency.

---

## Retry decorator

```python
import asyncio
import functools
import logging
import time
from typing import Callable

logger = logging.getLogger("llm_server")

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exceptions: tuple = (Exception,),
):
    """Exponential backoff retry — works for both sync and async functions."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if attempt == max_retries:
                        break
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    logger.warning(f"retry {attempt + 1}/{max_retries}: {e} — waiting {delay:.1f}s")
                    await asyncio.sleep(delay)
            raise last_exc

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if attempt == max_retries:
                        break
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    time.sleep(delay)
            raise last_exc

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator
```

---

## FastAPI LLM server

```python
import os
import time
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    system_prompt: str = Field(default="You are a helpful assistant.")
    temperature: float = Field(default=0.0, ge=0.0, le=1.0)
    stream: bool = Field(default=False)

class ChatResponse(BaseModel):
    response: str
    model: str
    latency_ms: float

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.environ["GROQ_API_KEY"],
        temperature=0.0,
    )
    logger.info("LLM client initialized")
    yield
    logger.info("server shutting down")

app = FastAPI(title="LLM API Server", lifespan=lifespan)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    t0 = time.perf_counter()
    response = await call_next(request)
    ms = (time.perf_counter() - t0) * 1000
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({ms:.0f}ms)")
    return response

@app.get("/health")
async def health():
    return {"status": "ok", "model": "llama-3.1-8b-instant"}

@retry_with_backoff(max_retries=2, base_delay=1.0)
async def _call_llm(llm: ChatGroq, messages: list) -> str:
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, lambda: llm.invoke(messages))
    return response.content

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    messages = [
        SystemMessage(content=request.system_prompt),
        HumanMessage(content=request.message),
    ]

    if request.stream:
        async def token_stream() -> AsyncIterator[str]:
            for chunk in app.state.llm.stream(messages):
                if chunk.content:
                    yield f"data: {chunk.content}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(token_stream(), media_type="text/event-stream")

    t0 = time.perf_counter()
    try:
        content = await _call_llm(app.state.llm, messages)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM call failed: {e}")

    return ChatResponse(
        response=content,
        model="llama-3.1-8b-instant",
        latency_ms=round((time.perf_counter() - t0) * 1000, 1),
    )
```

---

## Streaming client

```python
import httpx

async def stream_chat(message: str, base_url: str = "http://localhost:8000"):
    payload = {"message": message, "stream": True}
    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("POST", f"{base_url}/chat", json=payload) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: ") and not line.endswith("[DONE]"):
                    print(line[6:], end="", flush=True)
    print()

# Run server: uvicorn server:app --host 0.0.0.0 --port 8000
# asyncio.run(stream_chat("Explain Python asyncio in one sentence."))
```

---

## Deployment checklist

**Environment variables**: inject `GROQ_API_KEY` via a secrets manager or `.env` file. Never hardcode it.

**Timeouts**: client timeouts must exceed the longest expected LLM response. Groq typically responds in 2–5 s, but complex prompts can take 15–30 s.

**Concurrency**: increasing `--workers` raises throughput but also multiplies outbound LLM API requests. Tune against your API rate limits.

**Graceful shutdown**: the `lifespan` context manager ensures SIGTERM lets in-flight requests complete before the process exits.

<!-- toc:begin -->
## In this series

- [Monitoring and logging for LLM apps](./01-monitoring-and-logging.md)
- [LLM cost tracking and optimization](./02-cost-tracking.md)
- [Evaluating LLM output quality](./03-evaluation.md)
- [LLM app security](./04-security.md)
- **LLM app deployment strategies (current)**
- Completing the LLM ops pipeline (upcoming)

<!-- toc:end -->

---

## References

- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [Uvicorn deployment guide](https://www.uvicorn.org/deployment/)
- [LangChain streaming](https://python.langchain.com/docs/expression_language/streaming)

Tags: LLMOps, Observability, Python, LLM
