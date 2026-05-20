---
title: "LLM Apps Ops 101 (6/6): LLM 앱 운영 완성"
series: llm-apps-ops-101
episode: 6
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
seo_description: 운영 성숙도는 기능을 더 쌓는 데 있지 않고, 한 요청이 남기는 검증·비용·품질·로그 신호를 하나의 흐름으로 연결하는 데 있습니다.
---

# LLM Apps Ops 101 (6/6): LLM 앱 운영 완성

운영 레이어를 따로따로 보면 각각 그럴듯해 보여도, 실제 장애는 그 경계 사이에서 설명이 막히는 경우가 많습니다. 이 글은 LLM Apps Ops 101 시리즈의 마지막 글입니다. 여기서는 입력 검증, 비용 계산, 품질 점검, 구조화 로그를 하나의 요청 흐름으로 연결해, 통합 운영 파이프라인이 어떤 모습이어야 하는지 정리하겠습니다.

운영 성숙도는 기능을 계속 덧붙이는 데 있지 않습니다. 한 요청이 시스템을 통과한 뒤, 그 흔적이 보안·비용·품질·로깅 관점에서 서로 연결되어 남는 상태를 만드는 데 있습니다. 그래야 문제가 생겼을 때 “무슨 일이 있었는가”를 하나의 흐름으로 설명할 수 있습니다.

## 먼저 던지는 질문

- 완성형 LLM 운영 파이프라인은 어떤 계층을 한 요청 안에서 연결해야 할까요?
- 모니터링, 비용, 평가, 보안, 배포가 따로 있으면 어떤 운영 공백이 생길까요?
- 최소 운영 앱의 health 상태는 어떤 누적 신호를 보여 줘야 할까요?

## 큰 그림

![LLM 운영 파이프라인 전체 구성](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/06/06-01-big-picture.ko.png)

*LLM 운영 파이프라인 전체 구성*

이 그림에서는 입력 검증, 모델 호출, 비용 계산, 평가, 로그 기록, health 상태가 하나의 운영 파이프라인으로 연결되는 모습을 봅니다. 완성형 운영 구조의 핵심은 기능을 나열하는 것이 아니라 같은 request_id 아래에서 신호를 합치는 것입니다.

> LLM 운영은 레이어를 많이 붙이는 일이 아니라, 한 요청을 비용·품질·보안·배포 신호로 끝까지 설명하는 일입니다.

## 왜 이 레이어가 중요한가

![입력 검증부터 로그 기록까지 이어지는 운영 흐름](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/06/06-01-why-this-layer-matters.ko.png)

*입력 검증부터 로그 기록까지 이어지는 운영 흐름*

통합 파이프라인이 중요한 이유는 요청 한 건이 여러 운영 신호를 따로 남기는 것이 아니라, 서로 연결된 흔적으로 남겨야 하기 때문입니다.

데모에서는 로깅, 평가, 비용 계산을 각각 독립 예제로 보여 줘도 문제가 없어 보입니다. 하지만 실제 운영에서는 나쁜 결과가 나왔을 때 그것이 위험 입력 때문인지, 비용 급증과 관련 있는지, 품질 저하 때문인지를 한 번에 설명해야 합니다. 이때 각 레이어가 서로 분리되어 있으면 원인 분석이 오히려 더 어려워집니다.

그래서 마지막 단계에서는 기능을 추가하는 것보다, 앞서 만든 신호를 한 요청 경로 위에 연결하는 일이 더 중요합니다. 입력 검증이 먼저 일어나고, 모델 호출 뒤에 비용과 품질이 계산되고, 마지막에 로그가 구조화되어 남는 순서가 바로 운영 파이프라인의 뼈대가 됩니다.

예제 파일: `en/06-ops-complete/main.py`

## 최소 실행 예제

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

## 이 코드에서 먼저 볼 점

![health 상태가 누적 호출 수와 비용을 드러내는 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/06/06-02-what-to-notice-in-this-code.ko.png)

*health 상태가 누적 호출 수와 비용을 드러내는 구조*

- `quality`, `total_tokens`, `cost_usd`를 한 응답에 같이 넣으면 서버와 클라이언트 모두 즉시 운영 맥락을 얻을 수 있습니다.
- `/health`에 누적 호출 수와 누적 비용을 넣으면, 아주 작은 예제에서도 상태 변화가 눈에 보입니다.
- 구조화된 `quality` 페이로드는 나중에 배치 평가와 대시보드 지표로 그대로 이어질 수 있습니다.

이 예제가 보여 주는 가장 중요한 감각은 “한 요청이 남기는 신호를 끊지 않는다”는 점입니다. 입력 검증이 먼저 실패하면 모델 호출 전에 멈추고, 통과하면 비용과 품질이 계산되고, 그 결과가 다시 구조화 로그와 health 상태에 반영됩니다. 이 연결이 있어야 운영자는 각 지표를 따로 보지 않고도 요청의 전체 수명을 설명할 수 있습니다.

## 어디서 자주 헷갈릴까요?

![배포·관측·평가·최적화가 다시 배포로 이어지는 루프](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/06/06-03-where-engineers-get-confused.ko.png)

*배포·관측·평가·최적화가 다시 배포로 이어지는 루프*

- 통합 파이프라인이 있다고 해서 저장소, 알람, 대시보드가 불필요해지는 것은 아닙니다. 다만 그 시스템들이 더 좋은 신호를 받게 됩니다.
- 인라인 평가는 가시성을 높여 주지만 지연 시간을 늘릴 수 있습니다. 실제 서비스에서는 동기·비동기 평가를 분리하기도 합니다.
- 단순 비용 공식은 데모에는 충분하지만, 실제 과금은 입력/출력 분리와 모델별 단가표가 필요할 수 있습니다.

특히 자주 생기는 오해는 “이제 모든 운영 문제가 해결됐다”는 기대입니다. 통합 파이프라인은 끝이 아니라 시작점입니다. 지금 단계에서 얻는 것은 저장, 알람, 대시보드로 연결할 수 있는 일관된 신호입니다. 그 위에 장기 보관, 추세 분석, 배치 평가, 비용 경보를 쌓아야 비로소 프로덕션 운영이 완성됩니다.

## 체크리스트

- [ ] 모델 호출 전에 입력을 검증한다
- [ ] 모든 응답에 `total_tokens`와 `cost_usd`를 계산한다
- [ ] 품질 리포트를 구조화된 형태로 로그에 남긴다
- [ ] `/health`에 누적 상태를 노출한다

## 정리

이제 요청 한 건이 전체 운영 흔적을 남기기 시작했습니다. 다음 단계는 새로운 엔드포인트 로직을 더하는 일이 아니라, 이 신호를 저장하고 알람을 걸고 대시보드로 연결하는 일입니다.

## 처음 질문으로 돌아가기

- **완성형 LLM 운영 파이프라인은 어떤 계층을 한 요청 안에서 연결해야 할까요?**
  - 입력 검증, 보안 guard, 모델 호출, 비용 집계, 품질 평가, 로그 기록, health reporting이 한 요청 안에서 이어져야 합니다.
- **모니터링, 비용, 평가, 보안, 배포가 따로 있으면 어떤 운영 공백이 생길까요?**
  - 각 계층의 지표가 join되지 않아 장애 원인, 비용 급증, 품질 하락, 보안 차단이 서로 다른 이야기로 분리됩니다.
- **최소 운영 앱의 health 상태는 어떤 누적 신호를 보여 줘야 할까요?**
  - 누적 호출 수, 오류 수, 총 비용, 평균 latency, 최근 차단 수, 마지막 provider 상태 같은 신호를 보여 줘야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM Apps Ops 101 (1/6): LLM 앱 모니터링과 로깅](./01-monitoring-and-logging.md)
- [LLM Apps Ops 101 (2/6): LLM 비용 추적과 최적화](./02-cost-tracking.md)
- [LLM Apps Ops 101 (3/6): LLM 출력 품질 평가](./03-evaluation.md)
- [LLM Apps Ops 101 (4/6): LLM 앱 보안](./04-security.md)
- [LLM Apps Ops 101 (5/6): LLM 앱 배포 전략](./05-deployment.md)
- **LLM Apps Ops 101 (6/6): LLM 앱 운영 완성 (현재 글)**

<!-- toc:end -->

---

## 참고 자료

- [FastAPI](https://fastapi.tiangolo.com/)
- [Groq API Reference](https://console.groq.com/docs/api-reference)
- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

Tags: LLMOps, Observability, Python, LLM
