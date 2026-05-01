---
title: 'LLM 앱 운영 완성'
series: llm-apps-ops-101
episode: 6
language: ko
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

# LLM 앱 운영 완성

> LLM 앱 운영 101 (6/6)

이 시리즈에서 다룬 모니터링, 비용 추적, 품질 평가, 보안, 배포 전략을 하나의 프로덕션 서버로 통합합니다. 각 레이어는 독립적으로 교체 가능하고, 전체가 함께 동작할 때 신뢰할 수 있는 LLM 앱 운영 기반이 됩니다.

## 예제 코드
- [GitHub: ko/ep06_ops_complete.py](https://github.com/yeongseon-books/llm-apps-ops-101/blob/main/ko/ep06_ops_complete.py)

---

## 통합 운영 서버

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
from pathlib import Path
from typing import AsyncIterator, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

# ── 로거 ──────────────────────────────────────────────────────────────────
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "msg": record.getMessage(),
        }
        if hasattr(record, "extra"):
            log.update(record.extra)
        return json.dumps(log, ensure_ascii=False)

def build_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        h = logging.StreamHandler()
        h.setFormatter(JsonFormatter())
        logger.addHandler(h)
    return logger

logger = build_logger("llm_prod")

# ── 재시도 ─────────────────────────────────────────────────────────────────
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

# ── 속도 제한 ──────────────────────────────────────────────────────────────
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
            return False, f"{reset_in}초 후 재시도"
        self._calls[user_id].append(now)
        return True, ""

# ── 입력 검증 ──────────────────────────────────────────────────────────────
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
    """(passed, reason, sanitized) 반환."""
    if not text.strip():
        return False, "빈 입력", ""
    if len(text) > 4000:
        return False, f"입력 초과: {len(text)}자", ""
    for pat in INJECTION_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return False, "프롬프트 인젝션 탐지", ""
    sanitized = SENSITIVE_RE.sub("[REDACTED]", text)
    return True, "", sanitized

# ── 비용 추적 ──────────────────────────────────────────────────────────────
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

# ── FastAPI 앱 ──────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    user_id: str = Field(default="anonymous")
    system_prompt: str = Field(default="당신은 유용한 어시스턴트입니다.")
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
    logger.info("서버 시작", extra={"extra": {"model": "llama-3.1-8b-instant"}})
    yield
    logger.info("서버 종료")

app = FastAPI(title="LLM Production Server", lifespan=lifespan)

@app.middleware("http")
async def request_log(request: Request, call_next):
    t0 = time.perf_counter()
    resp = await call_next(request)
    ms = (time.perf_counter() - t0) * 1000
    logger.info(
        f"{request.method} {request.url.path}",
        extra={"extra": {"status": resp.status_code, "ms": round(ms, 1)}},
    )
    return resp

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "total_calls": total_calls,
        "cumulative_cost_usd": round(cumulative_cost, 4),
    }

@retry_backoff(max_retries=2)
async def _llm_call(llm, messages) -> tuple[str, dict]:
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, lambda: llm.invoke(messages))
    usage = getattr(response, "usage_metadata", {}) or {}
    return response.content, usage

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    global cumulative_cost, total_calls

    # 속도 제한
    allowed, reason = rate_limiter.is_allowed(req.user_id)
    if not allowed:
        raise HTTPException(status_code=429, detail=reason)

    # 입력 검증
    ok, reason, sanitized = validate_input(req.message)
    if not ok:
        raise HTTPException(status_code=400, detail=reason)

    if req.stream:
        messages = [SystemMessage(content=req.system_prompt), HumanMessage(content=sanitized)]
        async def token_stream() -> AsyncIterator[str]:
            for chunk in app.state.llm.stream(messages):
                if chunk.content:
                    yield f"data: {chunk.content}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(token_stream(), media_type="text/event-stream")

    record = CallRecord()
    messages = [SystemMessage(content=req.system_prompt), HumanMessage(content=sanitized)]
    t0 = time.perf_counter()

    try:
        content, usage = await _llm_call(app.state.llm, messages)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM 오류: {e}")

    record.latency_ms = (time.perf_counter() - t0) * 1000
    record.input_tokens = usage.get("input_tokens", 0)
    record.output_tokens = usage.get("output_tokens", 0)

    cumulative_cost += record.cost_usd
    total_calls += 1

    logger.info(
        "llm_call",
        extra={"extra": {
            "call_id": record.call_id,
            "latency_ms": round(record.latency_ms, 1),
            "tokens": record.input_tokens + record.output_tokens,
            "cost_usd": round(record.cost_usd, 6),
        }},
    )

    return ChatResponse(
        response=content,
        call_id=record.call_id,
        latency_ms=round(record.latency_ms, 1),
        cost_usd=round(record.cost_usd, 6),
    )
```

---

## 실행 방법

```bash
# 의존성 설치
pip install fastapi uvicorn langchain-groq pydantic

# 서버 시작
GROQ_API_KEY=<your_key> uvicorn server:app --host 0.0.0.0 --port 8000

# 헬스체크
curl http://localhost:8000/health

# 채팅 요청
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "파이썬 asyncio란 무엇인가요?", "user_id": "user_1"}'
```

---

## 시리즈 마무리

이 시리즈에서 구축한 레이어는 순서대로 쌓이는 구조입니다.

- 모니터링과 로깅이 기반이 됩니다.
- 비용 추적이 그 위에 올라가서 예산 초과를 막습니다.
- 품질 평가가 모델 교체나 프롬프트 변경 시 안전망이 됩니다.
- 보안 레이어가 악의적 사용을 억제합니다.
- 배포 구조가 전체를 프로덕션에서 신뢰할 수 있게 만듭니다.

각 레이어는 독립적으로 교체할 수 있습니다. 모니터링 백엔드를 Datadog으로 바꾸거나, 캐시를 Redis로 올리거나, 재시도 로직을 Tenacity 라이브러리로 교체해도 나머지는 그대로 작동합니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM 앱 모니터링과 로깅](./01-monitoring-and-logging.md)
- [LLM 비용 추적과 최적화](./02-cost-tracking.md)
- [LLM 출력 품질 평가](./03-evaluation.md)
- [LLM 앱 보안](./04-security.md)
- [LLM 앱 배포 전략](./05-deployment.md)
- **LLM 앱 운영 완성 (현재 글)**

<!-- toc:end -->

---

## 참고 자료

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [LangChain 운영 가이드](https://python.langchain.com/docs/guides/productionization/)
- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

Tags: LLMOps, Observability, Python, LLM
