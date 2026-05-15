---
title: LLM app deployment strategies
series: llm-apps-ops-101
episode: 5
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
last_reviewed: '2026-05-14'
seo_description: A deployable example proves startup, health, and one real chat request with the same script.
---

# LLM app deployment strategies

Operations-focused deployment advice only matters if the application can prove that it really starts.

This is the fifth post in the LLM Apps Ops 101 series. Here, we will make a FastAPI-based LLM endpoint deployable and add a self-test that verifies the full startup path.

A believable example should bring up the server, pass health, and complete one representative request without manual glue.

## Questions this post answers

- How much should a health check prove for a FastAPI LLM endpoint?
- How do you call the synchronous Groq client safely from an async endpoint?
- What is the simplest self-test flow that proves the server really starts?
- How should local self-tests connect to container deployment checks?

> A deployable example is not defined by nice-looking server code. It is defined by whether the same script can start the server, hit health, and complete a real chat request.

## Big picture
![Self-test flow for health and chat](../../../assets/llm-apps-ops-101/05/05-01-big-picture.en.png)

*Self-test flow for health and chat*

## Why this layer matters
![Startup verification reaches health check](../../../assets/llm-apps-ops-101/05/05-02-why-this-layer-matters.en.png)

*Startup verification reaches health check*

A deployment example is only credible when it can start the server and verify a real request on its own.

The most common documentation mistake is showing server code without proving that it actually boots. For an operations-focused post, health check plus one representative request is the minimum bar.

Example file: `en/05-deployment/main.py`

## Minimal runnable example
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

## What to notice in this code
![Async endpoint offloads sync model calls](../../../assets/llm-apps-ops-101/05/05-03-what-to-notice-in-this-code.en.png)

*Async endpoint offloads sync model calls*
- `asyncio.to_thread` prevents the synchronous Groq SDK from blocking the FastAPI event loop.
- Starting `uvicorn.Server` in code keeps documentation and verification in one place.
- Hitting both `/health` and `/chat` checks more than process startup; it verifies the real dependency path.

## Minimum deployment artifacts before the container exists

Real deployment guidance needs more than app code. It also needs the dependency file and the startup command.

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

Those three files close the loop between local proof and runtime packaging.

## Turn the self-test into an external HTTP check

In-process self-tests are useful, but deployment verification should also test the app from the outside.

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

That output proves readiness across the HTTP boundary, not just inside Python.

## Separate failure modes before deployment

Treat these as different failures, not one generic “deployment bug”:

1. **startup failure** — environment variables, import errors, lifespan initialization
2. **health failure** — routing or readiness problem after the process starts
3. **chat failure** — SDK auth, model networking, timeout, or dependency path issue
4. **shutdown failure** — threads or blocking work not exiting cleanly

Self-tests are valuable because they make those failure boundaries obvious.

## Where engineers get confused
![Self-test verifies startup and shutdown](../../../assets/llm-apps-ops-101/05/05-04-where-engineers-get-confused.en.png)

*Self-test verifies startup and shutdown*
- A health endpoint does not guarantee model quality. It only confirms basic service readiness.
- Using an async web framework does not magically make every external SDK async.
- A local self-test passing does not remove the need to verify secrets, networking, and timeout settings in deployment.
- A container starting does not guarantee readiness. A real request still needs to pass.

## Deployment verification order

```bash
# 1) Install dependencies and verify imports
python3 -m pip install -r requirements.txt

# 2) Start the app process
uvicorn main:app --host 127.0.0.1 --port 8015

# 3) Check health
curl --fail http://127.0.0.1:8015/health

# 4) Check one representative chat request
curl --fail -H "Content-Type: application/json" -d '{"message":"Explain Python async functions in two sentences."}' http://127.0.0.1:8015/chat
```

The same order works well in CI because each step narrows the failure surface.

## Checklist
- [ ] Call `/health` automatically after startup
- [ ] Send one real `/chat` request in the self-test
- [ ] Move blocking SDK calls into `to_thread`
- [ ] Confirm the background server exits cleanly
- [ ] Version the Dockerfile and dependency file beside the app code

## Summary
In deployment examples, the self-test is often more valuable than the endpoint code because it proves the instructions are real.

The next step is to combine deployment, security, quality, cost, and logging into one integrated request path so the service leaves a full operational trail.

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

### Official Docs

- [FastAPI deployment](https://fastapi.tiangolo.com/deployment/)
- [Uvicorn settings](https://www.uvicorn.org/settings/)
- [Dockerfile reference](https://docs.docker.com/reference/dockerfile/)

### Verification-friendly resource

- [HTTPX quickstart](https://www.python-httpx.org/quickstart/)

Tags: LLMOps, Observability, Python, LLM
