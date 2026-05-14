---
title: LLM 앱 배포 전략
series: llm-apps-ops-101
episode: 5
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
last_reviewed: '2026-05-14'
seo_description: 배포 가능한 예제의 기준은 보기 좋은 서버 코드가 아니라, 같은 스크립트로 서버 기동, 헬스체크, 실제 채팅 요청까지 검증할 수 있는가입니다.
---

# LLM 앱 배포 전략

운영 관점의 배포 조언은 애플리케이션이 정말 뜬다는 사실을 증명할 수 있을 때만 의미가 있습니다.

이 글은 LLM Apps Ops 101 시리즈의 다섯 번째 글입니다. 여기서는 FastAPI 기반 LLM 엔드포인트를 실제로 배포 가능한 형태로 만들고, 서버 기동부터 헬스체크와 대표 요청 한 건까지 검증하는 self-test를 붙여 보겠습니다.

문서에서 가장 흔한 문제는 예쁘게 보이는 서버 코드와 실제로 기동이 보장되는 서버 코드가 다르다는 점입니다. 운영 글이라면 최소한 서버가 뜨고, `/health`가 응답하고, `/chat`이 한 번은 끝까지 성공하는지 스스로 증명해야 합니다.

## 이 글에서 다룰 문제

- FastAPI 기반 LLM 엔드포인트에서 health check는 어디까지 증명해야 하는가?
- 동기식 Groq 클라이언트를 비동기 엔드포인트에서 어떻게 안전하게 호출하는가?
- 서버가 실제로 뜬다는 것을 증명하는 가장 단순한 self-test 흐름은 무엇인가?
- 로컬 self-test와 컨테이너 배포 검증은 어떻게 이어져야 하는가?

> 배포 가능한 예제의 기준은 서버 코드가 보기 좋으냐가 아닙니다. 같은 스크립트로 서버를 띄우고, health를 확인하고, 실제 채팅 요청까지 끝낼 수 있어야 합니다.

## 큰 그림

![self-test가 헬스체크와 채팅 요청을 검증하는 흐름](../../../assets/llm-apps-ops-101/05/05-01-big-picture.ko.png)

*self-test가 헬스체크와 채팅 요청을 검증하는 흐름*

## 왜 이 레이어가 중요한가

![서버 기동 확인이 헬스체크로 이어지는 흐름](../../../assets/llm-apps-ops-101/05/05-02-why-this-layer-matters.ko.png)

*서버 기동 확인이 헬스체크로 이어지는 흐름*

배포 예제가 신뢰를 얻으려면, 서버를 띄운 뒤 실제 요청 경로를 스스로 검증할 수 있어야 합니다.

운영 글에서 서버 코드만 보여 주고 실제 기동을 증명하지 않으면, 독자는 마지막 단계에서 가장 많은 시간을 잃습니다. import는 되는데 startup에서 죽는지, health는 되는데 모델 호출이 막히는지, 종료가 깔끔하지 않아 포트가 남는지 같은 문제는 코드만 읽어서는 보이지 않습니다.

예제 파일: `en/05-deployment/main.py`

## 최소 실행 예제

```python
import asyncio
import os
import threading
import time
from contextlib import asynccontextmanager

import httpx
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field
from groq import Groq

MODEL = "llama-3.1-8b-instant"

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)

class ChatResponse(BaseModel):
    response: str
    model: str

def call_model(client: Groq, message: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": "You are a concise Python assistant."},
            {"role": "user", "content": message},
        ],
    )
    return response.choices[0].message.content or ""

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = Groq(api_key=os.environ["GROQ_API_KEY"])
    yield

app = FastAPI(title="llm-deployment-demo", lifespan=lifespan)

class ThreadSafeServer(uvicorn.Server):
    def install_signal_handlers(self) -> None:
        return None

@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "model": MODEL}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    answer = await asyncio.to_thread(call_model, app.state.client, request.message)
    return ChatResponse(response=answer, model=MODEL)

def run_server(server: uvicorn.Server) -> None:
    server.run()

def main() -> None:
    config = uvicorn.Config(app, host="127.0.0.1", port=8015, log_level="warning")
    server = ThreadSafeServer(config)
    thread = threading.Thread(target=run_server, args=(server,), daemon=True)
    thread.start()

    for _ in range(40):
        try:
            health = httpx.get("http://127.0.0.1:8015/health", timeout=2.0)
            if health.status_code == 200:
                break
        except Exception:
            time.sleep(0.25)
    else:
        raise RuntimeError("server did not start")

    print("HEALTH:", health.json())
    response = httpx.post(
        "http://127.0.0.1:8015/chat",
        json={"message": "Explain Python async functions in two sentences."},
        timeout=30.0,
    )
    print("CHAT:", response.json())

    server.should_exit = True
    thread.join(timeout=10)
    if thread.is_alive():
        raise RuntimeError("server did not stop cleanly")

if __name__ == "__main__":
    main()
```

## 이 코드에서 먼저 볼 점

![비동기 엔드포인트가 동기 모델 호출을 분리하는 구조](../../../assets/llm-apps-ops-101/05/05-03-what-to-notice-in-this-code.ko.png)

*비동기 엔드포인트가 동기 모델 호출을 분리하는 구조*

- `asyncio.to_thread`는 동기식 Groq SDK가 FastAPI 이벤트 루프를 막지 않게 해 줍니다.
- 코드 안에서 `uvicorn.Server`를 직접 띄우면 문서와 검증 절차를 하나의 예제로 묶을 수 있습니다.
- `/health`와 `/chat`을 모두 호출해야 프로세스 기동만이 아니라 실제 의존성 경로까지 확인할 수 있습니다.

## 컨테이너 배포 전 최소 산출물

운영에서 실제로 필요한 것은 앱 코드만이 아닙니다. 의존성 파일과 실행 명령도 함께 보여 줘야 배포 문서가 닫힙니다.

```text
app/
├── main.py
├── requirements.txt
└── Dockerfile
```

```text
fastapi==0.115.0
uvicorn==0.30.6
httpx==0.27.2
groq==0.11.0
```

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

ENV PORT=8000
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

이 세 파일이 같이 있어야 로컬 self-test에서 끝나지 않고 컨테이너 런타임까지 생각할 수 있습니다. 배포 전략 글이 실제로 도움이 되려면 “어떤 프로세스가 어떤 포트에서 어떤 명령으로 뜨는가”까지 분명해야 합니다.

## self-test를 curl 검증으로 바꾸기

애플리케이션 내부 self-test는 좋은 출발점이지만, 배포 직전에는 바깥에서 보는 검증도 필요합니다. 그래야 네트워크 경계와 JSON 직렬화, 헤더 설정까지 함께 확인할 수 있습니다.

```bash
uvicorn main:app --host 127.0.0.1 --port 8015 &
SERVER_PID=$!

curl --fail http://127.0.0.1:8015/health

curl --fail \
  -H "Content-Type: application/json" \
  -d '{"message":"Explain Python async functions in two sentences."}' \
  http://127.0.0.1:8015/chat

kill $SERVER_PID
wait $SERVER_PID 2>/dev/null || true
```

**Expected output:**

```text
{"status":"ok","model":"llama-3.1-8b-instant"}
{"response":"Async functions let Python suspend work at await points so other tasks can run.","model":"llama-3.1-8b-instant"}
```

이 출력이 중요한 이유는, 애플리케이션이 외부 클라이언트 기준으로도 준비되었다는 사실을 보여 주기 때문입니다. 운영에서는 내부 함수 호출보다 HTTP 경계 검증이 더 직접적인 증거가 됩니다.

## 배포 전에 꼭 분리해서 봐야 할 실패

실패는 한 종류가 아닙니다. 아래 네 가지를 분리해서 보면 디버깅이 빨라집니다.

1. **startup 실패** — 환경 변수, import, lifespan 초기화 문제
2. **health 실패** — 서버 기동은 됐지만 라우팅이나 readiness 문제
3. **chat 실패** — 모델 SDK, 네트워크, 인증, 타임아웃 문제
4. **shutdown 실패** — 백그라운드 스레드나 블로킹 작업 정리 문제

운영 글에서 self-test를 권하는 이유도 여기에 있습니다. 실패를 이 순서대로 분리해 보여 주면, 독자가 어디서부터 봐야 하는지 바로 알 수 있습니다.

## 어디서 자주 헷갈릴까요?

![self-test가 기동과 종료를 함께 검증하는 구조](../../../assets/llm-apps-ops-101/05/05-04-where-engineers-get-confused.ko.png)

*self-test가 기동과 종료를 함께 검증하는 구조*

- health 엔드포인트는 모델 품질을 보장하지 않습니다. 기본적인 서비스 준비 상태만 확인합니다.
- 비동기 웹 프레임워크를 쓴다고 해서 외부 SDK가 자동으로 비동기화되지는 않습니다.
- 로컬 self-test가 통과해도 배포 환경의 비밀값, 네트워크, 타임아웃 설정은 별도로 검증해야 합니다.
- 컨테이너가 뜬다고 해서 곧바로 readiness가 보장되는 것도 아닙니다. 실제 요청이 통과해야 합니다.

특히 자주 나오는 오해는 “async endpoint니까 괜찮겠지”라는 생각입니다. 실제로는 내부에서 동기 SDK를 바로 호출하면 이벤트 루프가 막혀서 동시성이 무너질 수 있습니다. 또 `/health`만 통과하고 끝내면 모델 호출 경로는 검증하지 못합니다. 운영 글에서는 가벼운 준비 상태 확인과 실제 대표 요청 검증을 꼭 분리해서 보여 주는 편이 좋습니다.

## 배포 점검 순서

```bash
# 1) 의존성 설치와 import 확인
python3 -m pip install -r requirements.txt

# 2) 앱 프로세스 기동
uvicorn main:app --host 127.0.0.1 --port 8015

# 3) health 확인
curl --fail http://127.0.0.1:8015/health

# 4) 대표 chat 요청 확인
curl --fail -H "Content-Type: application/json" -d '{"message":"Explain Python async functions in two sentences."}' http://127.0.0.1:8015/chat
```

실제 배포 파이프라인에서도 이 흐름을 거의 그대로 유지하는 편이 좋습니다. 단계를 나누어야 실패 지점을 로그와 알림으로 바로 연결할 수 있습니다.

## 체크리스트

- [ ] startup 뒤에 `/health`를 자동 호출한다
- [ ] self-test에서 실제 `/chat` 요청 한 건을 보낸다
- [ ] 블로킹 SDK 호출은 `to_thread`로 분리한다
- [ ] 백그라운드 서버가 정상 종료하는지 확인한다
- [ ] Dockerfile과 의존성 파일을 함께 관리한다

## 정리

배포 예제에서는 엔드포인트 코드보다 self-test가 더 값질 때가 많습니다. 예제가 실제로 작동한다는 사실을 증명해 주기 때문입니다.

다음 글에서는 모니터링, 비용, 품질, 보안을 한 요청 경로 위에 묶어 통합 운영 파이프라인으로 마무리하겠습니다.

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

### 공식 문서

- [FastAPI deployment](https://fastapi.tiangolo.com/deployment/)
- [Uvicorn settings](https://www.uvicorn.org/settings/)
- [Dockerfile reference](https://docs.docker.com/reference/dockerfile/)

### 검증에 도움 되는 자료

- [HTTPX quickstart](https://www.python-httpx.org/quickstart/)

Tags: LLMOps, Observability, Python, LLM
