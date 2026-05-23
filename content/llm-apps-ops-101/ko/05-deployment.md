---
title: "LLM Apps Ops 101 (5/6): LLM 앱 배포 전략"
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

# LLM Apps Ops 101 (5/6): LLM 앱 배포 전략

운영 관점의 배포 조언은 애플리케이션이 정말 뜬다는 사실을 증명할 수 있을 때만 의미가 있습니다.

여기서는 FastAPI 기반 LLM 엔드포인트를 실제로 배포 가능한 형태로 만들고, 서버 기동부터 헬스체크와 대표 요청 한 건까지 검증하는 self-test를 붙여 보겠습니다.

문서에서 가장 흔한 문제는 예쁘게 보이는 서버 코드와 실제로 기동이 보장되는 서버 코드가 다르다는 사실입니다. 운영 글이라면 최소한 서버가 뜨고, `/health`가 응답하고, `/chat`이 한 번은 끝까지 성공하는지 스스로 증명해야 합니다.

![self-test가 헬스체크와 채팅 요청을 검증하는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/05/05-01-big-picture.ko.png)
*self-test가 헬스체크와 채팅 요청을 검증하는 흐름*
> LLM 앱의 배포 검증은 서버가 켜졌는지가 아니라 한 번의 실제 요청이 끝까지 통과하는지에서 시작합니다.

## 먼저 던지는 질문

- 배포 전 self-test는 왜 health check와 실제 chat 요청을 함께 검증해야 할까요?
- 비동기 endpoint와 동기 모델 호출 사이에는 어떤 실패 경계가 생길까요?
- 컨테이너 배포 전에 최소로 준비해야 할 산출물은 무엇일까요?

## 왜 이 레이어가 중요한가

![서버 기동 확인이 헬스체크로 이어지는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/05/05-02-why-this-layer-matters.ko.png)

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

![비동기 엔드포인트가 동기 모델 호출을 분리하는 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/05/05-03-what-to-notice-in-this-code.ko.png)

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

## 자체 점검을 호출 검증으로 바꾸기

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

## 배포 패턴을 환경별로 분리해 설계하기

LLM 앱 배포에서 가장 흔한 실수는 개발, 스테이징, 프로덕션을 같은 방식으로 다루는 것입니다. 실제로는 환경마다 목적이 다르기 때문에 배포 패턴도 달라야 합니다. 개발 환경은 빠른 피드백이 우선이라 단일 인스턴스와 느슨한 제한이 적합합니다. 스테이징은 운영과 유사한 트래픽 경로를 검증하는 곳이라 보안 가드레일, 비용 계측, 평가 훅을 모두 활성화해야 합니다. 프로덕션은 가용성과 롤백 속도가 핵심이라 무중단 배포와 점진 전환 전략이 필수입니다.

실무에서 자주 쓰는 패턴은 블루/그린, 카나리, 롤링 세 가지입니다. 블루/그린은 전환이 단순하고 롤백이 빠르지만 인프라 비용이 더 듭니다. 카나리는 위험을 단계적으로 노출할 수 있지만 관측 체계가 성숙해야 합니다. 롤링은 비용 효율이 좋지만 세션과 캐시 일관성에 주의해야 합니다.

## 자체 점검을 배포 게이트로 강제하기

자체 점검은 선택 기능이 아니라 배포 게이트입니다. 서버가 뜨는지, health endpoint가 응답하는지, 실제 모델 호출이 성공하는지, 로그와 비용 기록이 남는지까지 한 번에 검증해야 합니다. 특히 LLM 앱에서는 `/health`만 통과하고 실제 `/chat`이 실패하는 상황이 흔하므로, 대표 요청 검증은 반드시 포함해야 합니다.

### 배포 전 자체 점검 스크립트 예시

```python
import httpx

def run_predeploy_smoke(base_url: str) -> dict:
    report = {"health": False, "chat": False, "cost_log": False}

    health = httpx.get(f"{base_url}/health", timeout=5.0)
    report["health"] = health.status_code == 200

    chat = httpx.post(
        f"{base_url}/chat",
        json={"message": "운영 점검 요청입니다."},
        timeout=20.0,
    )
    report["chat"] = chat.status_code == 200 and "answer" in chat.text

    metrics = httpx.get(f"{base_url}/ops/last-record", timeout=5.0)
    report["cost_log"] = metrics.status_code == 200 and "estimated_cost_usd" in metrics.text
    return report
```

이 수준의 검증만 있어도 "배포는 됐지만 운영 기능이 죽어 있는" 상태를 상당수 걸러낼 수 있습니다. 그리고 리포트를 CI 아티팩트로 보관하면 장애 회고 때 배포 시점의 상태를 재구성하기 쉽습니다.

## 운영 신호를 기준으로 한 카나리 전환

카나리 배포를 쓸 때는 트래픽 비율보다 중단 기준을 먼저 정해야 합니다. 예를 들어 5% 트래픽에서 `p95 지연 30% 이상 상승`, `비용/요청 20% 이상 상승`, `평가 실패율 2배 증가` 중 하나라도 만족하면 즉시 롤백하는 식입니다.

이 기준은 반드시 코드와 문서에 동시에 남겨야 합니다. 특히 프롬프트 버전이 바뀌는 배포에서는 카나리 구간의 로그를 별도 태그로 남겨야 합니다. `prompt_version`, `deployment_id`, `canary_group`를 기록하면, 전환 후 문제가 생겼을 때 어느 배포가 영향을 줬는지 빠르게 추적할 수 있습니다.

## 배포 실패를 줄이는 체크포인트

배포 실패는 대부분 코드보다 경계 조건에서 발생합니다. 환경 변수 누락, 모델 키 권한 부족, 타임아웃 과소 설정, 로그 수집 에이전트 충돌 같은 문제입니다. 그래서 릴리스 템플릿에는 기능 체크리스트뿐 아니라 운영 체크리스트가 별도로 있어야 합니다.

권장 체크포인트는 다음과 같습니다. `환경 변수 검증`, `모델 연결 테스트`, `비용 레코드 생성 확인`, `평가 훅 활성화`, `보안 규칙 버전 확인`, `롤백 경로 확인`입니다. 이 항목을 자동화하면 배포의 재현성이 크게 올라갑니다. 배포 전략의 본질은 멋진 아키텍처가 아니라 같은 절차를 매번 동일하게 실행할 수 있는가입니다.

## 어디서 자주 헷갈릴까요?

![self-test가 기동과 종료를 함께 검증하는 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/05/05-04-where-engineers-get-confused.ko.png)

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

## 배포 후 30분 관찰 구간을 운영 규칙으로 만들기

배포 직후 30분은 가장 많은 신호가 나오는 시간대입니다. 이 시간을 그냥 지나치면 문제가 생겨도 원인을 놓치기 쉽습니다. 그래서 팀 차원에서 "배포 후 30분 관찰"을 명시적인 규칙으로 두는 편이 좋습니다.

관찰 항목은 단순해야 합니다. `error rate`, `latency p95`, `요청당 비용`, `평가 실패율`, `보안 차단율` 다섯 개만 봐도 충분합니다. 기준선 대비 급격히 흔들리는 항목이 있으면 즉시 전환 중단 또는 롤백을 검토합니다.

이 구간에서 중요한 점은 책임자 지정입니다. 누가 대시보드를 보고, 누가 롤백 버튼을 누를 권한이 있는지 명확해야 합니다. 역할이 모호하면 신호를 봐도 결정이 늦어집니다.

또한 배포 메모에는 "이번 배포에서 바뀐 프롬프트 버전/모델/인프라 설정"을 함께 적어야 합니다. 그래야 관찰 중 이상이 생겼을 때 변경 범위를 빠르게 좁힐 수 있습니다.

## 체크리스트

- [ ] startup 뒤에 `/health`를 자동 호출한다
- [ ] self-test에서 실제 `/chat` 요청 한 건을 보낸다
- [ ] 블로킹 SDK 호출은 `to_thread`로 분리한다
- [ ] 백그라운드 서버가 정상 종료하는지 확인한다
- [ ] Dockerfile과 의존성 파일을 함께 관리한다

## 운영 안정성을 높이는 롤백 설계 원칙

배포 전략의 완성은 성공 배포가 아니라 빠른 롤백 능력입니다. LLM 앱은 모델, 프롬프트, 인프라가 동시에 바뀔 수 있어 실패 원인이 복합적입니다. 그래서 롤백도 단일 버튼이 아니라 계층적으로 설계해야 합니다.

첫째, 트래픽 롤백입니다. 라우팅 비율을 즉시 이전 버전으로 되돌립니다. 둘째, 프롬프트 롤백입니다. 코드 배포를 유지한 채 prompt_version만 이전값으로 복구합니다. 셋째, 모델 롤백입니다. 라우팅 규칙에서 고위험 모델을 제외합니다. 넷째, 인프라 롤백입니다. 이미지 태그나 설정 버전을 이전으로 돌립니다.

이 네 단계가 분리되어 있으면 장애 시 영향도를 최소화하며 원인을 좁힐 수 있습니다. 특히 프롬프트 롤백 경로가 없으면 코드 재배포까지 기다려야 하므로 대응 시간이 길어집니다.

## 정리

배포 예제에서는 엔드포인트 코드보다 self-test가 더 값질 때가 많습니다. 예제가 실제로 작동한다는 사실을 증명해 주기 때문입니다.

다음 글에서는 모니터링, 비용, 품질, 보안을 한 요청 경로 위에 묶어 통합 운영 파이프라인으로 마무리하겠습니다.

### 운영용 Dockerfile 보강 포인트

앞선 Dockerfile은 학습용 최소 예제입니다. 실제 운영에서는 이미지 크기, 보안, 시작 속도를 함께 고려해야 합니다. 특히 루트 사용자로 실행하지 않고, 헬스체크를 이미지에 내장하면 오케스트레이터가 비정상 인스턴스를 더 빠르게 감지할 수 있습니다.

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
RUN useradd -m appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

이 구성은 Kubernetes, ECS, ACA 같은 환경에서 동일한 신호를 제공합니다. 앱 내부 `/health`와 컨테이너 `HEALTHCHECK`가 일치하면 장애 분석 시 관측 지점이 분리되지 않습니다.

### readiness를 고려한 health endpoint 확장

운영에서는 단순 liveness와 readiness를 분리하는 편이 안전합니다. 프로세스는 살아 있어도 모델 클라이언트 초기화가 실패한 상태일 수 있기 때문입니다.

```python
@app.get("/health/live")
async def health_live() -> dict:
    return {"status": "alive"}

@app.get("/health/ready")
async def health_ready() -> dict:
    client_ready = hasattr(app.state, "client") and app.state.client is not None
    return {
        "status": "ready" if client_ready else "not_ready",
        "model": MODEL,
        "provider": "groq",
    }
```

`/health/live`는 프로세스 생존만, `/health/ready`는 외부 의존성 준비 상태까지 포함하도록 나누면 롤링 업데이트 중 트래픽 유입 타이밍을 더 정확히 제어할 수 있습니다.

### 블루-그린 배포 설정 예시

LLM 앱은 모델 버전, 프롬프트 버전, SDK 버전이 동시에 바뀌기 쉽기 때문에 롤백 가능한 배포 전략이 특히 중요합니다. 블루-그린은 가장 해석이 쉬운 전략 중 하나입니다.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: llm-chat
spec:
  replicas: 4
  strategy:
    blueGreen:
      activeService: llm-chat-active
      previewService: llm-chat-preview
      autoPromotionEnabled: false
      scaleDownDelaySeconds: 60
  selector:
    matchLabels:
      app: llm-chat
  template:
    metadata:
      labels:
        app: llm-chat
    spec:
      containers:
        - name: app
          image: ghcr.io/example/llm-chat:2026-05-14
          ports:
            - containerPort: 8000
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8000
```

이 방식에서는 preview 서비스에서 `/chat` self-test를 먼저 수행하고, 통과 시점에만 active로 승격합니다. 승격 후 오류율이나 P95 지연 시간이 임계치를 넘으면 즉시 블루로 되돌리는 절차를 자동화해 두는 편이 좋습니다.

## 처음 질문으로 돌아가기

- **배포 전 self-test는 왜 health check와 실제 chat 요청을 함께 검증해야 할까요?**
  - health만 통과하면 서버는 살아 있지만 provider 인증, payload, timeout, 응답 parsing 실패를 놓칠 수 있습니다.
- **비동기 endpoint와 동기 모델 호출 사이에는 어떤 실패 경계가 생길까요?**
  - async 서버가 sync 모델 호출에 막히면 event loop 지연, timeout 전파, worker 고갈 문제가 생깁니다.
- **컨테이너 배포 전에 최소로 준비해야 할 산출물은 무엇일까요?**
  - 환경 변수, health endpoint, 외부 chat self-test, timeout 설정, 로그 스키마, rollback 절차가 최소 산출물입니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM Apps Ops 101 (1/6): LLM 앱 모니터링과 로깅](./01-monitoring-and-logging.md)
- [LLM Apps Ops 101 (2/6): LLM 비용 추적과 최적화](./02-cost-tracking.md)
- [LLM Apps Ops 101 (3/6): LLM 출력 품질 평가](./03-evaluation.md)
- [LLM Apps Ops 101 (4/6): LLM 앱 보안](./04-security.md)
- **LLM Apps Ops 101 (5/6): LLM 앱 배포 전략 (현재 글)**
- LLM Apps Ops 101 (6/6): LLM 앱 운영 완성 (예정)

<!-- toc:end -->

---

## 참고 자료

- [LLM Apps Ops 101 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/llm-apps-ops-101/ko)
### 공식 문서

- [FastAPI deployment](https://fastapi.tiangolo.com/deployment/)
- [Uvicorn settings](https://www.uvicorn.org/settings/)
- [Dockerfile reference](https://docs.docker.com/reference/dockerfile/)

### 검증에 도움 되는 자료

- [HTTPX quickstart](https://www.python-httpx.org/quickstart/)

Tags: LLMOps, Observability, Python, LLM
