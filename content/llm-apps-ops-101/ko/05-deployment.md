---
title: 'LLM 앱 배포 전략'
series: llm-apps-ops-101
episode: 5
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

# LLM 앱 배포 전략

> LLM 앱 운영 101 (5/6)

LLM 앱을 로컬에서 프로덕션으로 올릴 때 가장 자주 마주치는 문제는 타임아웃, 동시성, 재시도 처리입니다. 이 포스트에서는 FastAPI 기반 서버, 연결 풀링, 재시도 로직, 헬스체크를 갖춘 배포 가능한 LLM 서버를 구축합니다.

<!-- ebook-only:start -->

이 장의 핵심: **배포는 모델 버전·프롬프트 버전·코드 버전을 함께 관리하는 것이다.** 세 버전이 어긋나면 재현 불가능한 버그가 생긴다.

## 이 장의 위치

이 글은 시리즈 6편 중 5번째 장입니다.
앞 장에서는 **LLM 앱 보안**을 다뤘습니다.
이 장을 마치면 다음 장에서 **LLM 앱 운영 완성**으로 이어집니다.
<!-- ebook-only:end -->

## 예제 코드
예제 코드: [github.com/yeongseon-books/llm-apps-ops-101](https://github.com/yeongseon-books/llm-apps-ops-101/tree/main/ko)

---

## 배포 구조 개요

LLM API 호출은 기본적으로 느립니다. 응답 생성에 수 초가 걸리고, 네트워크 오류나 속도 제한(429)이 언제든 발생할 수 있습니다. 프로덕션 서버는 다음 세 가지를 갖춰야 합니다.

- **비동기 처리**: 한 요청이 LLM 응답을 기다리는 동안 다른 요청을 처리할 수 있어야 합니다.
- **지수 백오프 재시도**: 일시적 오류를 자동으로 복구합니다.
- **스트리밍 응답**: 첫 토큰을 빠르게 반환해 체감 지연을 줄입니다.

---

## 재시도 데코레이터

```python
import asyncio
import functools
import logging
import time
from typing import Callable, TypeVar

logger = logging.getLogger("llm_server")
T = TypeVar("T")

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exceptions: tuple = (Exception,),
):
    """지수 백오프 재시도 데코레이터 (동기 + 비동기 모두 지원)."""

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
                    logger.warning(f"재시도 {attempt + 1}/{max_retries}: {e} — {delay:.1f}초 대기")
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

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
```

---

## FastAPI LLM 서버

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

# ── 요청/응답 스키마 ─────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    system_prompt: str = Field(default="당신은 유용한 어시스턴트입니다.")
    temperature: float = Field(default=0.0, ge=0.0, le=1.0)
    stream: bool = Field(default=False)

class ChatResponse(BaseModel):
    response: str
    model: str
    latency_ms: float

# ── 앱 초기화 ─────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 앱 시작 시 LLM 클라이언트 초기화
    app.state.llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.environ["GROQ_API_KEY"],
        temperature=0.0,
    )
    logger.info("LLM 클라이언트 초기화 완료")
    yield
    logger.info("서버 종료")

app = FastAPI(title="LLM API Server", lifespan=lifespan)

# ── 미들웨어: 요청 로깅 ──────────────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    t0 = time.perf_counter()
    response = await call_next(request)
    latency = (time.perf_counter() - t0) * 1000
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({latency:.0f}ms)")
    return response

# ── 헬스체크 ─────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "model": "llama-3.1-8b-instant"}

# ── 채팅 엔드포인트 ───────────────────────────────────────────────────────
@retry_with_backoff(max_retries=2, base_delay=1.0)
async def _call_llm(llm: ChatGroq, messages: list) -> str:
    response = await asyncio.get_event_loop().run_in_executor(
        None, lambda: llm.invoke(messages)
    )
    return response.content

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    messages = [
        SystemMessage(content=request.system_prompt),
        HumanMessage(content=request.message),
    ]

    if request.stream:
        async def stream_response() -> AsyncIterator[str]:
            llm = request.app.state.llm
            for chunk in llm.stream(messages):
                if chunk.content:
                    yield f"data: {chunk.content}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(stream_response(), media_type="text/event-stream")

    t0 = time.perf_counter()
    try:
        llm = app.state.llm
        content = await _call_llm(llm, messages)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM 호출 실패: {str(e)}")

    return ChatResponse(
        response=content,
        model="llama-3.1-8b-instant",
        latency_ms=round((time.perf_counter() - t0) * 1000, 1),
    )
```

---

## 스트리밍 클라이언트 예시

```python
import httpx

async def stream_chat(message: str, base_url: str = "http://localhost:8000"):
    payload = {"message": message, "stream": True}
    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("POST", f"{base_url}/chat", json=payload) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: ") and not line.endswith("[DONE]"):
                    token = line[6:]
                    print(token, end="", flush=True)
    print()

# 서버 시작: uvicorn server:app --host 0.0.0.0 --port 8000
# asyncio.run(stream_chat("파이썬 asyncio를 한 문장으로 설명해 주세요."))
```

---

## 배포 체크리스트

**환경 변수**: `GROQ_API_KEY`는 `.env` 파일이나 비밀 관리 서비스에서 주입합니다. 코드에 직접 넣지 않습니다.

**타임아웃 설정**: 클라이언트 타임아웃은 LLM 응답 시간보다 충분히 크게 잡아야 합니다. Groq는 보통 2–5초이지만, 복잡한 요청은 15–30초까지 걸릴 수 있습니다.

**동시성 제한**: `--workers` 수를 늘리면 처리량이 올라가지만, 동시에 나가는 LLM API 요청 수도 늘어납니다. API 속도 제한에 맞게 조정해야 합니다.

**그레이스풀 셧다운**: `lifespan` 컨텍스트 매니저를 사용하면 SIGTERM 수신 시 진행 중인 요청을 완료하고 종료합니다.

<!-- blog-only:start -->
다음 글: [LLM 앱 운영 완성](./06-ops-complete.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## 시리즈 목차

- [LLM 앱 모니터링과 로깅](./01-monitoring-and-logging.md)
- [LLM 비용 추적과 최적화](./02-cost-tracking.md)
- [LLM 출력 품질 평가](./03-evaluation.md)
- [LLM 앱 보안](./04-security.md)
- **LLM 앱 배포 전략 (현재 글)**
- LLM 앱 운영 완성 (예정)

<!-- toc:end -->

---

## 참고 자료

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Uvicorn 배포 가이드](https://www.uvicorn.org/deployment/)
- [LangChain 스트리밍](https://python.langchain.com/docs/expression_language/streaming)

Tags: LLMOps, Observability, Python, LLM
