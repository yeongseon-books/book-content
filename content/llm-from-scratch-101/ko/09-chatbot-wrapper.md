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

대화형 애플리케이션으로 바꾸려면 모델만으로는 부족합니다. 대화 히스토리를 어떤 형식으로 직렬화할지, 모델을 언제 한 번만 메모리에 올릴지, 토큰을 한 번에 줄지 스트리밍으로 흘려 줄지, 브라우저에서 어떻게 받아서 보여 줄지까지 함께 설계해야 합니다.

이 단계에서 비로소 "LLM 애플리케이션"이라는 말이 현실적인 의미를 갖습니다. 학습된 가중치 하나를 넘어, 요청-응답 프로토콜과 상태 관리, 사용자 인터페이스까지 묶인 작은 시스템이 되기 때문입니다.

이번 글에서는 파인튜닝한 `ckpt_sft.pt`를 FastAPI 서버에 올리고, multi-turn prompt format, synchronous `/chat` endpoint, SSE streaming endpoint, 최소 HTML 클라이언트를 붙여 시리즈를 마무리하겠습니다.

이 글은 LLM from Scratch 101 시리즈의 마지막 글입니다.

이제 모델을 감싸는 시스템까지 이해하면, 직접 만든 소형 GPT가 실제 AI 애플리케이션의 축소판으로 보이기 시작합니다.

## 먼저 던지는 질문

- 챗봇은 모델 외에 어떤 구성 요소를 더 필요로 할까요?
- multi-turn prompt format은 왜 직접 설계해야 할까요?
- FastAPI lifespan으로 모델을 한 번만 로드하면 무엇이 좋아질까요?

## 큰 그림

![LLM from Scratch 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/09/09-01-chatbot-model-history-streaming-ui.ko.png)

*LLM from Scratch 101 9장 흐름 개요*

이 그림에서는 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 이 글이 중요한가

많은 입문자가 모델을 학습시키는 것과 서비스를 만드는 것을 별개의 일처럼 느낍니다. 하지만 실제 애플리케이션에서는 두 문제가 정확히 만납니다. 어떤 prompt format을 쓸지, 어떤 요청 경로를 만들지, 모델을 언제 로드할지 같은 결정이 곧 사용자 경험과 운영 비용을 좌우합니다.

또한 이 글은 앞선 여덟 편의 내용을 실제 시스템으로 묶어 줍니다. 토크나이저는 입력 검증에, 생성 루프는 응답 생성에, 파인튜닝은 대화형 형식 적응에, sampling은 응답 품질 조절에 사용됩니다. 즉, 지금까지 만든 조각들이 여기서 하나의 앱으로 합쳐집니다.

실전적으로도 중요합니다. 모델을 요청마다 다시 로드하면 느리고 비효율적이며, 스트리밍이 없으면 사용자는 응답 지연을 더 크게 느낍니다. 작은 예제라도 FastAPI lifespan, SSE, 클라이언트 이벤트 처리 같은 개념을 직접 연결해 보는 경험은 이후 더 큰 시스템으로 갈 때 큰 기반이 됩니다.

## 핵심 관점

챗봇을 "모델에 프롬프트를 넣고 답을 받는 도구"로만 보면 중요한 절반이 빠집니다. 더 정확한 관점은 이렇습니다. **챗봇은 모델, 대화 히스토리, 스트리밍 I/O, 사용자 인터페이스가 함께 움직이는 작은 시스템**입니다.

이 관점이 중요한 이유는 문제를 제대로 분해하게 해 주기 때문입니다. 모델은 텍스트를 생성할 뿐이고, multi-turn prompt format은 문맥을 직렬화하며, API endpoint는 요청/응답 계약을 만들고, SSE는 토큰을 점진적으로 밀어 넣고, 브라우저는 그것을 사용자 경험으로 바꿉니다.

즉, 챗봇 품질은 모델 가중치만으로 결정되지 않습니다. 히스토리 직렬화 방식, unsupported character 처리, streaming 여부, 클라이언트 반응성까지 모두 함께 작용합니다. 작은 예제일수록 이 시스템 관점이 더 분명하게 보입니다.

> 이번 글의 핵심은 이것입니다. 챗봇은 모델 하나가 아니라, 대화 상태와 스트리밍 입출력을 함께 묶은 작은 애플리케이션입니다.

## 핵심 개념

### 챗봇은 모델 + 히스토리 + 스트리밍 + UI의 결합입니다

단일 프롬프트 생성과 챗봇의 차이는 대화 상태와 상호작용 방식에 있습니다. 챗봇은 현재 입력뿐 아니라 이전 사용자 발화와 이전 모델 응답까지 함께 문맥으로 묶어야 하고, 결과를 한 번에 줄지 점진적으로 줄지도 결정해야 합니다.

이 구조를 이해하면 왜 마지막 글이 단순한 API 래퍼가 아닌지 알 수 있습니다. 지금까지 만든 모델을 실제 사용자 경험에 연결하는 단계이기 때문입니다.

### multi-turn prompt format은 대화 상태를 직렬화하는 계약입니다

이번 예제에서는 대화 이력을 평문 블록으로 이어 붙입니다. 가장 단순하지만 디버깅하기 쉬운 형식입니다.

```text
User: Hello!
Bot: Nice to meet you.
User: Who is Romeo?
Bot:
```

새 질문이 올 때마다 과거 히스토리를 이어 붙이고 마지막에 `Bot:`을 남겨 두면, 모델은 그 뒤를 생성합니다. char-level 모델이므로 vocab 밖 문자는 사전에 걸러지거나 경고와 함께 드롭됩니다. 이 처리 역시 대화 시스템의 일부입니다.

### 모델은 요청마다 로드하지 말고 서버 시작 시 한 번만 올립니다

`ckpt_sft.pt`를 요청마다 다시 읽는 것은 매우 비효율적입니다. FastAPI의 `lifespan` 훅을 사용하면 서버 시작 시 모델을 한 번만 로드하고, 종료 시 정리할 수 있습니다. 작은 모델에서도 이 차이는 UX와 서버 비용에 분명히 나타납니다.

### synchronous endpoint와 streaming endpoint는 역할이 다릅니다

`POST /chat`은 가장 단순한 형태입니다. history와 prompt를 JSON으로 받고, 전체 응답 문자열을 한 번에 돌려줍니다. 반면 `GET /chat/stream`은 생성되는 토큰을 SSE로 조금씩 흘려 보내므로, 사용자는 응답이 완성되기 전부터 모델이 생각을 이어 가는 듯한 체감을 얻게 됩니다.

특히 작은 모델에서는 절대 속도가 빠르더라도 streaming의 체감 이점이 큽니다. 사용자는 정적 대기보다 점진적 출력을 더 빠르게 느끼기 때문입니다.

### FastAPI 서버 코드는 작지만 운영 포인트가 응축되어 있습니다

아래 코드는 서버 구현의 핵심입니다. prompt 구성, unsupported character 처리, lifespan 모델 로드, `/chat`, `/chat/stream`까지 모두 포함합니다.

```python
# server.py
from contextlib import asynccontextmanager

import torch
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from data import decode, stoi
from model import GPT, GPTConfig
templates = Jinja2Templates(directory="templates"); state = {}

class ChatBody(BaseModel):
    prompt: str
    history: list[dict[str, str]] = []
    max_new_tokens: int = 120

def build_prompt(history, prompt):
    lines = []
    for t in history: lines += [f"User: {t['user']}", f"Bot: {t['bot']}"]
    lines.append(f"User: {prompt}")
    lines.append("Bot:")
    return "\n".join(lines)

def encode_chat_text(text: str):
    dropped = sorted({c for c in text if c not in stoi})
    ids = [stoi[c] for c in text if c in stoi]
    if not ids:
        raise ValueError("Prompt became empty after dropping unsupported characters.")
    return ids, dropped

@asynccontextmanager
async def lifespan(app: FastAPI):
    d = "cuda" if torch.cuda.is_available() else "cpu"
    ckpt = torch.load("ckpt_sft.pt", map_location=d)
    m = GPT(GPTConfig(**ckpt["config"])).to(d); m.load_state_dict(ckpt["model"]); m.eval()
    state["device"] = d; state["model"] = m
    yield
    state.clear()

app = FastAPI(lifespan=lifespan)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(body: ChatBody):
    text = build_prompt(body.history, body.prompt)
    try:
        ids, dropped = encode_chat_text(text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    idx = torch.tensor([ids], dtype=torch.long, device=state["device"])
    with torch.no_grad(): out = state["model"].generate(idx, body.max_new_tokens, 0.8, 20, 0.9)
    response = {"response": decode(out[0].tolist())[len(ids):]}
    if dropped:
        response["warning"] = f"Dropped unsupported characters: {''.join(dropped)}"
    return response

@app.get("/chat/stream")
async def chat_stream(prompt: str):
    async def event_gen():
        try:
            ids, dropped = encode_chat_text(build_prompt([], prompt))
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        if dropped:
            yield f"data: [warning] Dropped unsupported characters: {''.join(dropped)}\n\n"
        current = torch.tensor([ids], dtype=torch.long, device=state["device"])
        for _ in range(120):
            with torch.no_grad(): next_ids = state["model"].generate(current, 1, 0.8, 20, 0.9)
            current = next_ids; token_id = next_ids[0, -1].item()
            yield f"data: {decode([token_id])}\n\n"
    return StreamingResponse(event_gen(), media_type="text/event-stream")
```

이 예제는 짧지만 실제 서비스의 핵심 논점을 모두 건드립니다. prompt 직렬화, 입력 검증, 모델 생명주기 관리, 동기 응답, 스트리밍 응답, 경고 메시지 반환까지 한 파일에 압축되어 있습니다.

### 브라우저 쪽은 `EventSource`만으로도 충분합니다

SSE를 받는 최소 클라이언트는 매우 짧게 만들 수 있습니다. 표준 `EventSource` API가 서버의 `text/event-stream`을 그대로 받아 주기 때문입니다.

```html
<!doctype html>
<html lang="en"><body>
<h1>Mini Bot</h1>
<input id="prompt" size="50" placeholder="Question"><button id="send">Send</button>
<pre id="out"></pre>
<script>
const promptEl=document.getElementById('prompt'),out=document.getElementById('out');let source=null;
document.getElementById('send').onclick=()=>{if(source)source.close();out.textContent='';
source=new EventSource(`/chat/stream?prompt=${encodeURIComponent(promptEl.value)}`);
source.onmessage=e=>out.textContent+=e.data;source.onerror=()=>source.close();};
</script></body></html>
```

이 클라이언트는 일부러 최소 형태를 유지합니다. 중요한 것은 화려한 UI가 아니라, 서버가 한 글자씩 흘려 보내는 응답이 브라우저에서 실시간으로 이어 붙는다는 사실을 눈으로 확인하는 데 있습니다.

### 시리즈 전체를 실제 앱의 축소판으로 다시 볼 수 있습니다

여기까지 오면 이번 시리즈가 단순한 모델 수업이 아니었다는 점이 분명해집니다. 토크나이저는 입력 인코딩과 문자 검증에 쓰였고, 임베딩과 어텐션은 모델 본체가 되었고, 학습과 파인튜닝은 출력 습관을 만들었고, 생성 루프는 API와 UI의 핵심 엔진이 되었습니다.

즉, 약 120만 파라미터의 작은 char-level GPT라도 현대 AI 애플리케이션이 어떤 층위로 구성되는지 보여 주는 좋은 축소판이 됩니다.

## 흔히 헷갈리는 지점

- 챗봇은 모델만 있으면 된다고 느끼기 쉽지만, 히스토리 직렬화와 I/O 프로토콜이 없으면 대화형 시스템이 되지 않습니다.
- 요청마다 체크포인트를 다시 로드해도 된다고 생각하기 쉽지만, lifespan 로딩이 훨씬 효율적입니다.
- `/chat`과 `/chat/stream`의 차이를 단순 응답 형식 차이로 보기 쉽지만, 사용자의 체감 속도는 크게 달라집니다.
- SSE가 거대한 모델에서만 필요하다고 느끼기 쉽지만, 작은 모델에서도 즉시성 체감을 크게 높여 줍니다.
- unsupported character 처리를 사소하게 보기 쉽지만, char-level 모델에서는 실제 입력 손실과 오류로 바로 이어집니다.

## 운영 체크리스트

- [ ] multi-turn history를 어떤 텍스트 템플릿으로 직렬화하는지 명확히 정했는가
- [ ] FastAPI lifespan에서 모델을 한 번만 로드하도록 구현했는가
- [ ] `/chat`과 `/chat/stream` 두 경로가 각각 어떤 UX를 주는지 확인했는가
- [ ] unsupported character가 모두 드롭되어 빈 입력이 되는 경우를 400 오류로 처리하는가
- [ ] 브라우저 `EventSource`가 토큰 스트림을 정상적으로 이어 붙이는지 직접 확인했는가

## 정리

이번 글에서는 파인튜닝한 소형 GPT를 FastAPI와 SSE 기반의 챗봇 시스템으로 감쌌습니다. 모델, 대화 히스토리, 스트리밍 응답, 브라우저 UI가 연결되면서 지금까지 만든 코드가 비로소 하나의 애플리케이션 형태를 갖추게 되었습니다.

또한 챗봇 품질이 모델 가중치만으로 결정되지 않는다는 점도 확인했습니다. prompt format, lifespan 로딩, 스트리밍 방식, unsupported character 처리 같은 시스템 수준 결정이 사용자 경험에 직접 영향을 줍니다.

이 시리즈는 토크나이저에서 출발해 임베딩, 어텐션, 블록, GPT 클래스, 학습, 샘플링, 파인튜닝, 챗봇 래퍼까지 이어졌습니다. 작은 모델이지만 LLM 애플리케이션의 전체 흐름을 끝에서 끝까지 직접 만져 본 셈입니다.

## 처음 질문으로 돌아가기

- **챗봇은 모델 외에 어떤 구성 요소를 더 필요로 할까요?**
  - 본문의 기준은 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **multi-turn prompt format은 왜 직접 설계해야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **FastAPI lifespan으로 모델을 한 번만 로드하면 무엇이 좋아질까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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

Tags: LLM, PyTorch, Transformer, Tutorial
