---
title: "LLM from Scratch 101 (9/9): 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍"
series: llm-from-scratch-101
episode: 9
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- LLM
- PyTorch
- Transformer
- Tutorial
last_reviewed: '2026-05-12'
seo_description: generate.py까지 오면 모델은 돌아가지만 아직은 개발자 도구에 가깝습니다.
---

# LLM from Scratch 101 (9/9): 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍

`generate.py`까지 만들면 모델은 분명히 동작합니다. 프롬프트를 넣으면 문자가 이어지고, 샘플링 설정에 따라 결과도 달라집니다. 하지만 그 상태는 아직 개발자 도구에 가깝습니다. 실제 사용자 경험과는 거리가 있습니다.

이 글은 LLM from Scratch 101 시리즈의 마지막 글입니다.

대화형 애플리케이션으로 바꾸려면 모델만으로는 부족합니다. 대화 히스토리를 어떤 형식으로 직렬화할지, 모델을 언제 한 번만 메모리에 올릴지, 토큰을 한 번에 줄지 스트리밍으로 흘려 줄지, 브라우저에서 어떻게 받아서 보여 줄지까지 함께 설계해야 합니다.

이번 글에서는 파인튜닝한 `ckpt_sft.pt`를 FastAPI 서버에 올리고, multi-turn prompt format, synchronous `/chat` endpoint, SSE streaming endpoint, 최소 HTML 클라이언트를 붙여 시리즈를 마무리하겠습니다.

![LLM from Scratch 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/09/09-01-chatbot-model-history-streaming-ui.ko.png)
*LLM from Scratch 101 9장 흐름 개요*

## 이 글에서 다룰 문제

- 챗봇은 모델 외에 어떤 구성 요소를 더 필요로 할까요?
- multi-turn prompt format은 왜 직접 설계해야 할까요?
- FastAPI lifespan으로 모델을 한 번만 로드하면 무엇이 좋아질까요?
- SSE 스트리밍과 동기 응답은 각각 어떤 상황에 적합할까요?
- 챗봇 래퍼의 흔한 실패 모드는 무엇일까요?

## 챗봇 시스템 아키텍처

챗봇은 모델 하나가 아니라 여러 계층이 협력하는 시스템입니다.

```
브라우저 (index.html)
    |
    |  HTTP POST /chat          → 동기 응답 (전체 텍스트 한 번에)
    |  GET /chat/stream?prompt= → SSE 스트림 (토큰 단위 점진 출력)
    |
FastAPI 서버 (server.py)
    |
    |── lifespan: 서버 시작 시 모델 1회 로드 → state["model"]
    |
    |── build_prompt(history, prompt)
    |      └── "User: ...\nBot: ...\nUser: ...\nBot:" 직렬화
    |
    |── encode_chat_text(text)
    |      └── 미지원 문자 드롭 + 빈 입력 400 오류 처리
    |
    |── model.generate(idx, max_new, temperature, top_k, top_p)
    |      └── 06-training-loop, 07-inference 의 동일 코드
    |
    └── decode(ids) → 응답 문자열

ckpt_sft.pt (08-finetuning 의 출력)
    └── GPT 가중치 + config + sft_meta
```

각 계층이 독립적으로 교체 가능하게 설계하면 나중에 모델을 바꿔도 서버 코드는 그대로 둘 수 있습니다.

## multi-turn prompt format

대화 히스토리를 직렬화하는 방식은 모델이 어떤 형식으로 SFT를 받았는지와 일치해야 합니다. 이번 시리즈의 SFT 형식은 `Q:/A:` 였으므로, 챗봇도 같은 마커를 씁니다. 단, multi-turn을 위해 `User:/Bot:` 레이블로 확장합니다.

```
[1턴]
User: Hello!
Bot: Nice to meet you.

[2턴 (User 발화 추가)]
User: Hello!
Bot: Nice to meet you.
User: Who is Romeo?
Bot:          ← 모델이 여기서부터 생성

[3턴 (Bot 응답 추가 후 다음 User 발화)]
User: Hello!
Bot: Nice to meet you.
User: Who is Romeo?
Bot: A young lover who loves Juliet.
User: And Juliet?
Bot:
```

새 질문이 올 때마다 과거 히스토리를 이어 붙이고 마지막에 `Bot:`을 남겨 두면, 모델은 그 뒤를 생성합니다. char-level 모델이므로 vocab 밖 문자는 사전에 걸러지거나 경고와 함께 드롭됩니다.

컨텍스트 길이 제한이 있으므로 `block_size`를 초과하면 가장 오래된 히스토리부터 잘라냅니다. 이 정책을 명시적으로 구현해 두어야 긴 대화에서 조용히 오류가 생기는 것을 막을 수 있습니다.

## server.py 전체 구현

```python
# server.py
"""
실행:
    pip install fastapi uvicorn jinja2 pydantic
    uvicorn server:app --reload --port 8000

디렉토리 구조:
    server.py
    templates/index.html
    ckpt_sft.pt
    data.py  model.py
"""

from contextlib import asynccontextmanager
from pathlib import Path

import torch
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from data import decode, stoi
from model import GPT, GPTConfig


# ─── 설정 ────────────────────────────────────────────────────────────────────

CKPT_PATH      = "ckpt_sft.pt"
MAX_HISTORY_TURNS = 10           # 최대 보존 대화 턴 수
MAX_PROMPT_LEN = 500             # 입력 문자 길이 상한
MAX_NEW_TOKENS = 120             # 생성 토큰 상한

templates = Jinja2Templates(directory="templates")
state: dict = {}                 # lifespan에서 모델/디바이스를 공유


# ─── 요청/응답 스키마 ─────────────────────────────────────────────────────────

class ChatBody(BaseModel):
    prompt: str
    history: list[dict[str, str]] = []   # [{"user": ..., "bot": ...}, ...]
    max_new_tokens: int = MAX_NEW_TOKENS


class ChatResponse(BaseModel):
    response: str
    warning: str | None = None
    meta: dict = {}


# ─── 유틸리티 ────────────────────────────────────────────────────────────────

def build_prompt(history: list[dict[str, str]], prompt: str) -> str:
    """대화 히스토리와 현재 입력을 단일 시퀀스로 직렬화합니다."""
    # 컨텍스트 오버플로 방지: 최근 N 턴만 유지
    recent = history[-MAX_HISTORY_TURNS:]
    lines: list[str] = []
    for turn in recent:
        lines.append(f"User: {turn['user']}")
        lines.append(f"Bot: {turn['bot']}")
    lines.append(f"User: {prompt}")
    lines.append("Bot:")
    return "\n".join(lines)


def encode_chat_text(text: str) -> tuple[list[int], list[str]]:
    """
    텍스트를 토큰 ID 리스트로 변환합니다.
    vocab에 없는 문자는 드롭하고 경고 목록을 반환합니다.
    빈 결과라면 ValueError를 올립니다.
    """
    dropped = sorted({c for c in text if c not in stoi})
    ids = [stoi[c] for c in text if c in stoi]
    if not ids:
        raise ValueError("Prompt became empty after dropping unsupported characters.")
    return ids, dropped


def run_generate(ids: list[int], max_new: int) -> list[int]:
    """모델 추론을 실행하고 새 토큰 ID 리스트를 반환합니다."""
    device = state["device"]
    model  = state["model"]
    idx    = torch.tensor([ids], dtype=torch.long, device=device)
    with torch.no_grad():
        out = model.generate(idx, max_new, temperature=0.8, top_k=20, top_p=0.9)
    return out[0].tolist()[len(ids):]   # 새로 생성된 토큰만 반환


# ─── 앱 생명주기 ─────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """서버 시작 시 모델을 한 번만 로드합니다."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[lifespan] loading {CKPT_PATH} on {device} ...")
    ckpt  = torch.load(CKPT_PATH, map_location=device)
    model = GPT(GPTConfig(**ckpt["config"])).to(device)
    model.load_state_dict(ckpt["model"])
    model.eval()
    state["device"] = device
    state["model"]  = model
    state["config"] = ckpt["config"]
    param_count = sum(p.numel() for p in model.parameters())
    print(f"[lifespan] ready — {param_count:,} params")
    yield
    state.clear()
    print("[lifespan] model unloaded")


app = FastAPI(title="Mini GPT Chatbot", lifespan=lifespan)


# ─── 엔드포인트 ──────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """최소 HTML 클라이언트를 제공합니다."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health():
    """서버 상태와 모델 정보를 반환합니다."""
    return {
        "status": "ok",
        "device": state.get("device"),
        "config": state.get("config"),
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(body: ChatBody):
    """
    동기 응답 엔드포인트.
    전체 응답 텍스트를 한 번에 반환합니다.
    """
    # 입력 길이 상한
    if len(body.prompt) > MAX_PROMPT_LEN:
        raise HTTPException(status_code=400, detail=f"prompt가 {MAX_PROMPT_LEN}자를 초과합니다.")

    text = build_prompt(body.history, body.prompt)

    try:
        ids, dropped = encode_chat_text(text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    new_ids  = run_generate(ids, body.max_new_tokens)
    response = decode(new_ids)

    return ChatResponse(
        response=response,
        warning=f"미지원 문자 드롭: {''.join(dropped)}" if dropped else None,
        meta={
            "model":          CKPT_PATH,
            "temperature":    0.8,
            "top_k":          20,
            "top_p":          0.9,
            "max_new_tokens": body.max_new_tokens,
            "input_tokens":   len(ids),
            "output_tokens":  len(new_ids),
        },
    )


@app.get("/chat/stream")
async def chat_stream(prompt: str, max_new: int = MAX_NEW_TOKENS):
    """
    SSE 스트리밍 엔드포인트.
    토큰 단위로 점진적으로 응답을 흘려 보냅니다.

    SSE 이벤트 형식:
        event: token    data: <문자>
        event: warning  data: <메시지>
        event: done     data: {"output_tokens": N}
    """
    if len(prompt) > MAX_PROMPT_LEN:
        raise HTTPException(status_code=400, detail=f"prompt가 {MAX_PROMPT_LEN}자를 초과합니다.")

    async def event_gen():
        try:
            ids, dropped = encode_chat_text(build_prompt([], prompt))
        except ValueError as e:
            yield f"event: error\ndata: {e}\n\n"
            return

        if dropped:
            yield f"event: warning\ndata: 미지원 문자 드롭: {''.join(dropped)}\n\n"

        device  = state["device"]
        model   = state["model"]
        current = torch.tensor([ids], dtype=torch.long, device=device)
        count   = 0

        for _ in range(max_new):
            with torch.no_grad():
                next_ids = model.generate(current, 1, temperature=0.8, top_k=20, top_p=0.9)
            current   = next_ids
            token_id  = next_ids[0, -1].item()
            char      = decode([token_id])
            # SSE는 빈 줄(\n\n)이 이벤트 구분자이므로 개행 문자를 이스케이프
            safe_char = char.replace("\n", "\\n")
            yield f"event: token\ndata: {safe_char}\n\n"
            count += 1

        yield f"event: done\ndata: {{\"output_tokens\": {count}}}\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream")
```

## 최소 HTML 클라이언트 (templates/index.html)

```html
<!doctype html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Mini GPT Bot</title>
  <style>
    body { font-family: monospace; max-width: 720px; margin: 40px auto; padding: 0 16px; }
    #log { border: 1px solid #ccc; padding: 12px; height: 360px; overflow-y: auto;
           white-space: pre-wrap; background: #f9f9f9; margin-bottom: 8px; }
    #prompt { width: calc(100% - 90px); padding: 6px; font-size: 14px; }
    button  { padding: 6px 12px; font-size: 14px; cursor: pointer; }
    .user   { color: #0055aa; }
    .bot    { color: #006600; }
    .warn   { color: #cc6600; font-size: 12px; }
  </style>
</head>
<body>
<h2>Mini GPT Chatbot</h2>
<div id="log"></div>
<input id="prompt" placeholder="질문을 입력하세요..." autofocus>
<button id="send">전송</button>
<button id="clear">초기화</button>

<script>
const log    = document.getElementById('log');
const input  = document.getElementById('prompt');
let history  = [];   // [{user: ..., bot: ...}]
let source   = null;

function append(cls, text) {
  const span = document.createElement('span');
  span.className = cls;
  span.textContent = text;
  log.appendChild(span);
  log.scrollTop = log.scrollHeight;
}

document.getElementById('clear').onclick = () => {
  history = [];
  log.innerHTML = '';
  if (source) { source.close(); source = null; }
};

document.getElementById('send').onclick = () => {
  const prompt = input.value.trim();
  if (!prompt) return;
  input.value = '';

  if (source) source.close();

  append('user', `\nYou: ${prompt}\n`);
  append('bot', 'Bot: ');

  let botText = '';

  // SSE 스트리밍 요청
  source = new EventSource(`/chat/stream?prompt=${encodeURIComponent(prompt)}`);

  source.addEventListener('token', e => {
    const char = e.data.replace(/\\n/g, '\n');
    botText += char;
    // 마지막 Bot: span에 문자 추가
    const spans = log.querySelectorAll('.bot');
    spans[spans.length - 1].textContent += char;
    log.scrollTop = log.scrollHeight;
  });

  source.addEventListener('warning', e => {
    append('warn', `\n[경고] ${e.data}\n`);
  });

  source.addEventListener('done', e => {
    source.close(); source = null;
    history.push({ user: prompt, bot: botText });
    append('bot', '\n');
  });

  source.addEventListener('error', e => {
    append('warn', `\n[오류] 연결이 끊겼습니다.\n`);
    source.close(); source = null;
  });
};

// Enter 키 지원
input.addEventListener('keydown', e => {
  if (e.key === 'Enter') document.getElementById('send').click();
});
</script>
</body>
</html>
```

## 서버 실행 및 테스트

```bash
# 의존성 설치
pip install fastapi uvicorn jinja2 pydantic

# 서버 시작
uvicorn server:app --reload --port 8000
```

서버 시작 로그:

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
[lifespan] loading ckpt_sft.pt on cpu ...
[lifespan] ready — 1,198,656 params
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

동기 응답 테스트 (curl):

```bash
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Who is Romeo?", "history": [], "max_new_tokens": 60}' \
  | python -m json.tool
```

예시 출력:

```json
{
  "response": " A young man who loves Juliet deeply.",
  "warning": null,
  "meta": {
    "model": "ckpt_sft.pt",
    "temperature": 0.8,
    "top_k": 20,
    "top_p": 0.9,
    "max_new_tokens": 60,
    "input_tokens": 17,
    "output_tokens": 38
  }
}
```

multi-turn 테스트:

```bash
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "And what about Juliet?",
    "history": [{"user": "Who is Romeo?", "bot": " A young man who loves Juliet deeply."}],
    "max_new_tokens": 60
  }' | python -m json.tool
```

헬스 체크:

```bash
curl http://localhost:8000/health
```

```json
{
  "status": "ok",
  "device": "cpu",
  "config": {"n_layer": 6, "n_head": 6, "n_embd": 384, "block_size": 256, "vocab_size": 65}
}
```

## SSE 이벤트 타입 설계

단일 `data:` 줄로도 동작하지만, 이벤트 타입을 분리하면 UI 처리 분기가 단순해집니다.

```
event: token
data: M

event: token
data: y

event: token
data: \n   ← 개행 문자는 \\n으로 이스케이프

event: warning
data: 미지원 문자 드롭: 😊

event: done
data: {"output_tokens": 38}
```

브라우저에서는 `source.addEventListener("token", ...)` 형태로 각 이벤트를 독립적으로 처리합니다. 이렇게 하면 텍스트 누적, 경고 UI, 완료 처리 로직이 충돌하지 않습니다.

## 응답 지연 계측

```python
# latency.py — 서버 없이 생성 지연만 측정합니다
import time
import torch
from data import encode, decode
from model import GPT, GPTConfig

device = "cuda" if torch.cuda.is_available() else "cpu"
ckpt   = torch.load("ckpt_sft.pt", map_location=device)
model  = GPT(GPTConfig(**ckpt["config"])).to(device)
model.load_state_dict(ckpt["model"])
model.eval()

prompts = [
    "Q: Who is Romeo?\nA:",
    "Q: Write one sentence about loyalty.\nA:",
]

for prompt in prompts:
    ids = encode(prompt)
    idx = torch.tensor([ids], dtype=torch.long, device=device)

    start = time.perf_counter()
    with torch.no_grad():
        out = model.generate(idx, 60, temperature=0.8, top_k=20, top_p=0.9)
    elapsed_ms = (time.perf_counter() - start) * 1000

    result = decode(out[0].tolist())[len(ids):]
    print(f"latency_ms={elapsed_ms:6.1f}  output_chars={len(result):3d}  [{result[:40]!r}]")
```

예시 출력:

```
latency_ms= 184.2  output_chars=37  [' A young man who loves Juliet deeply.']
latency_ms= 201.7  output_chars=44  [' My lord, I serve thee with faithful heart.']
```

이 수치가 누적되면 p50/p95 지연을 바로 계산할 수 있고, streaming 적용 전후 체감 개선을 숫자로 설명할 수 있습니다.

## 아키텍처 선택 비교

| 구성 | 장점 | 단점 | 권장 시점 |
| --- | --- | --- | --- |
| 단일 `/chat` 동기 응답 | 구현 단순, 디버깅 쉬움 | 대기 체감 큼 | 초기 검증 |
| `/chat` + `/chat/stream` 병행 | UX 개선, 호환성 유지 | 코드 경로 2개 관리 | 데모/프로토타입 |
| queue + worker 비동기 | 확장성, 동시 요청 처리 | 운영 복잡도 상승 | 고부하 서비스 |

이번 시리즈는 두 번째 구성을 택합니다. 학습 비용 대비 사용자 체감 개선이 가장 크기 때문입니다.

## 챗봇 래퍼 실패 모드 진단

| 증상 | 흔한 원인 | 첫 대응 |
| --- | --- | --- |
| 서버 시작 시 OOM | 모델이 너무 큼 또는 메모리 부족 | `--workers 1`, CPU 전용으로 시작 |
| 빈 응답 반환 | 입력이 모두 드롭됨 (OOV) | `/health`로 vocab 확인, 입력 필터링 |
| SSE가 한 번에 쏟아짐 | 버퍼링 문제 또는 토큰 1개씩 생성 미구현 | `model.generate(idx, 1, ...)` 루프 확인 |
| 대화가 길어질수록 품질 저하 | 컨텍스트 초과 | `MAX_HISTORY_TURNS` 줄이기, 히스토리 요약 |
| 400 오류 반복 | unsupported char 또는 빈 prompt | 클라이언트에서 입력 사전 검증 |
| 응답이 이전 답변을 반복 | temperature 너무 낮거나 히스토리 누적 | temperature 높이기, 히스토리 리셋 |

## 보안 및 운영 체크리스트

최소한의 체크 목록입니다. 소형 모델 데모라도 이 기본값을 지키면 이후 확장 시 재작업 비용이 줄어듭니다.

```python
# server.py 에 추가하면 좋은 설정들

from fastapi.middleware.cors import CORSMiddleware

# CORS: 로컬 개발 시에는 허용, 배포 시에는 명시적으로 제한
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # 배포 시 도메인으로 변경
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# 요청 검증 (ChatBody 스키마에 추가)
class ChatBody(BaseModel):
    prompt: str
    history: list[dict[str, str]] = []
    max_new_tokens: int = MAX_NEW_TOKENS

    @property
    def validated_prompt(self) -> str:
        p = self.prompt.strip()
        if len(p) == 0:
            raise ValueError("prompt가 비어 있습니다.")
        if len(p) > MAX_PROMPT_LEN:
            raise ValueError(f"prompt가 {MAX_PROMPT_LEN}자를 초과합니다.")
        return p
```

- 입력 길이 상한을 둡니다 (`MAX_PROMPT_LEN`).
- 요청당 `max_new_tokens` 상한을 강제합니다 (`MAX_NEW_TOKENS`).
- 서버 로그에 프롬프트 원문을 그대로 남기지 않습니다.
- CORS 정책을 명시적으로 설정합니다.
- 공개 배포 시 rate limit을 추가합니다.

## 시리즈 전체 흐름 되돌아보기

여기까지 오면 이번 시리즈가 단순한 모델 수업이 아니었다는 점이 분명해집니다.

```
01. tokenizer  ─► 글자를 정수로 변환 (stoi, itos, encode, decode)
                   ↓ 서버에서 encode_chat_text() 로 재사용
02. embedding  ─► 정수를 벡터로, 위치 정보 추가
                   ↓ model.py 의 tok_emb + pos_emb
03. attention  ─► 어떤 토큰을 얼마나 볼지 결정
                   ↓ CausalSelfAttention 그대로 사용
04. block      ─► 어텐션 + FFN + 잔차 연결
                   ↓ Block 클래스, n_layer 번 쌓임
05. gpt model  ─► 전체 조립 + weight tying
                   ↓ GPT 클래스 서버에서 로드
06. training   ─► AdamW + 코사인 학습률 + grad clip
                   ↓ ckpt.pt 생성
07. inference  ─► temperature / top-k / top-p 샘플링
                   ↓ model.generate() 서버 엔드포인트에서 호출
08. finetuning ─► loss masking + instruction 데이터
                   ↓ ckpt_sft.pt 생성
09. server     ─► FastAPI + SSE + 브라우저 UI
                   ↓ 완성된 챗봇 애플리케이션
```

약 120만 파라미터의 작은 char-level GPT이지만, 현대 AI 애플리케이션이 어떤 계층으로 구성되는지 끝에서 끝까지 직접 만져 본 셈입니다.

## 운영 체크리스트

- [ ] multi-turn history를 어떤 텍스트 템플릿으로 직렬화하는지 명확히 정했는가
- [ ] FastAPI lifespan에서 모델을 한 번만 로드하도록 구현했는가
- [ ] `/chat`과 `/chat/stream` 두 경로가 각각 어떤 UX를 주는지 확인했는가
- [ ] unsupported character가 모두 드롭되어 빈 입력이 되는 경우를 400 오류로 처리하는가
- [ ] 브라우저 EventSource가 토큰 스트림을 정상적으로 이어 붙이는지 직접 확인했는가
- [ ] `/health` 엔드포인트로 서버 상태를 확인할 수 있는가
- [ ] `MAX_HISTORY_TURNS`로 컨텍스트 오버플로를 방지하고 있는가

## 정리

이번 글에서는 파인튜닝한 소형 GPT를 FastAPI와 SSE 기반의 챗봇 시스템으로 감쌌습니다. 모델, 대화 히스토리, 스트리밍 응답, 브라우저 UI가 연결되면서 지금까지 만든 코드가 하나의 애플리케이션 형태를 갖추게 되었습니다.

챗봇 품질이 모델 가중치만으로 결정되지 않는다는 점도 확인했습니다. prompt format, lifespan 로딩, 스트리밍 방식, unsupported character 처리 같은 시스템 수준 결정이 사용자 경험에 직접 영향을 줍니다.

이 시리즈는 토크나이저에서 출발해 임베딩, 어텐션, 블록, GPT 클래스, 학습, 샘플링, 파인튜닝, 챗봇 래퍼까지 이어졌습니다. 작은 모델이지만 LLM 애플리케이션의 전체 흐름을 끝에서 끝까지 직접 만져 본 셈입니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM from Scratch 101 (1/9): 글자를 숫자로 바꾸기](./01-tokenizer.md)
- [LLM from Scratch 101 (2/9): 정수에서 벡터로, 그리고 위치](./02-embedding.md)
- [LLM from Scratch 101 (3/9): 어떤 토큰을 얼마나 볼지 스스로 정하기](./03-attention.md)
- [LLM from Scratch 101 (4/9): 블록 하나, 깊이의 단위](./04-transformer-block.md)
- [LLM from Scratch 101 (5/9): 조립: GPT 모델 클래스 완성](./05-gpt-model.md)
- [LLM from Scratch 101 (6/9): 기울기로 배우기](./06-training-loop.md)
- [LLM from Scratch 101 (7/9): 샘플링 — 학습된 모델에서 글 뽑아내기](./07-inference.md)
- [LLM from Scratch 101 (8/9): 베이스 모델을 우리 작업에 맞추기](./08-finetuning.md)
- **LLM from Scratch 101 (9/9): 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍 (현재 글)**

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [FastAPI Lifespan Events (Documentation)](https://fastapi.tiangolo.com/advanced/events/)
- [MDN EventSource (Documentation)](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)
- [FastAPI StreamingResponse (Documentation)](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [nanoGPT (GitHub)](https://github.com/karpathy/nanoGPT)

### 관련 시리즈

- [LLM API 프로덕션 101 — 스트리밍 심화](../../llm-api-production-101/ko/03-streaming-in-depth.md)
- [AI 앱 패턴 101 — 챗봇 패턴](../../ai-app-patterns-101/ko/01-chatbot-pattern.md)
- [LangChain 101 — Streaming](../../langchain-101/ko/05-streaming.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-from-scratch-101/ko/09-chatbot-wrapper)

Tags: LLM, PyTorch, Transformer, Tutorial
