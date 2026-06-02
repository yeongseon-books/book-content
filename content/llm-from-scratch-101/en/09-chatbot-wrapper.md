---
title: "LLM from Scratch 101 (9/9): Turning Your LLM into a Chatbot — FastAPI + Streaming"
series: llm-from-scratch-101
episode: 9
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- LLM
- PyTorch
- Transformer
- Tutorial
last_reviewed: '2026-04-29'
seo_description: While generate.py works, it feels more like a developer tool than
  a finished product. Adding a web interface and streaming makes the model feel alive.
---

# LLM from Scratch 101 (9/9): Turning Your LLM into a Chatbot — FastAPI + Streaming

> LLM from Scratch 101 series (9/9)

While `generate.py` works, it feels more like a developer tool than a finished product. Adding a web interface and streaming makes the model feel alive.

The model we've built is a char-level GPT with 1.2 million parameters. It's small, but it's enough to demonstrate how a modern AI application is structured.

Today's mental model is this: **A chatbot isn't just a model. It's a small system that integrates conversation history, streaming I/O, and a user interface.**

This is the final post in the LLM from Scratch 101 series.

---

![LLM from Scratch 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/09/09-01-chatbot-model-history-streaming-ui.en.png)
*LLM from Scratch 101 chapter 9 flow overview*

## Questions to Keep in Mind

- What does a chatbot need beyond the model itself?
- Why design the multi-turn prompt format yourself?
- What do you gain by loading the model once via FastAPI lifespan?

## Chatbot = Model + History + Streaming + UI

To build a functional chatbot, we need four components working together: the model itself, a way to track the conversation, a streaming protocol, and a browser-based frontend.

## Designing the Multi-turn Prompt Format

For this project, we'll concatenate the conversation history into a plain text block.

```text
User: Hello!
Bot: Nice to meet you.
User: Who is Romeo?
Bot:
```

Every time a new question arrives, we append it to the history and let the model fill in everything after the final `Bot:` marker. Because this series uses an English char-level vocabulary, any unsupported characters should be dropped with a warning before generation starts.

## Loading the Model Once — FastAPI Lifespan

Reloading `ckpt_sft.pt` for every request is inefficient. We load it once when the server starts and manage its lifecycle using FastAPI's `lifespan` handler.

## The /chat Endpoint — Simple Synchronous Calls

The `POST /chat` endpoint receives the conversation history and the current prompt as JSON. It generates the response and returns the full string at once.

## Why Streaming Matters — The "Falling Token" UX

Our implementation is char-level, but the streaming logic remains the same for subword tokens. It provides immediate feedback to the user as each character is generated.

## Streaming Tokens with SSE (Server-Sent Events)

The `GET /chat/stream` endpoint returns a `StreamingResponse`, allowing the server to push tokens to the client as they are produced.

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

## Minimal HTML Client — A Single-page App

On the browser side, the standard `EventSource` API is enough to handle the server's token stream.

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

The sample stays English-only on purpose. If a user pastes unsupported characters, the server drops them, returns a warning, and rejects the request when nothing usable remains.

You can run the server with `uvicorn server:app --reload`.

## Series wrap-up

Over the course of nine posts, we've built a small GPT from scratch using roughly 720 lines of code. We covered character-level tokenization, embeddings, causal self-attention, Transformer blocks, training loops, sampling, SFT, and finally, a FastAPI chatbot wrapper.

While this model functions more as a Shakespearian rhythm generator than a general-purpose assistant, it demystifies the entire pipeline.

For your next steps, I recommend exploring LoRA, vLLM, RoPE, RLHF, BPE tokenization, and mixed-precision training.

<!-- a-grade-example:begin -->

## Checklist

- [ ] Started the FastAPI app and called /chat.
- [ ] Composed multi-turn history into a single prompt string.
- [ ] Watched tokens drop one-by-one over SSE.
- [ ] Loaded the single-page HTML client and held a conversation.

<!-- a-grade-example:end -->

## Common Misconceptions

- It feels like a chatbot only needs a model, but without history serialization and an I/O protocol it cannot become a conversational system.
- It seems fine to reload the checkpoint per request, but lifespan loading is far more efficient.
- The difference between `/chat` and `/chat/stream` looks like a mere response-format change, but perceived speed differs dramatically for users.
- SSE seems necessary only for giant models, but even small models benefit greatly from immediacy perception.
- Unsupported character handling looks trivial, but in a char-level model it directly causes input loss and errors.

## Operations Checklist

- [ ] Have you defined exactly which text template serializes multi-turn history?
- [ ] Is the model loaded once in FastAPI lifespan?
- [ ] Have you confirmed what UX `/chat` and `/chat/stream` each provide?
- [ ] Does the server return 400 when unsupported characters cause an empty input?
- [ ] Have you verified that the browser `EventSource` correctly accumulates the token stream?

## Stabilizing the Frontend via Explicit API Contracts

The most practical improvement in a chatbot wrapper is fixing the API response contract. Including warnings, errors, and generation settings explicitly keeps UI and server loosely coupled yet stable:

```json
{
  "response": "My lord, I serve thee with a faithful heart.",
  "warning": "Dropped unsupported characters: \ud83d\ude0a",
  "meta": {
    "model": "ckpt_sft.pt",
    "temperature": 0.8,
    "top_k": 20,
    "top_p": 0.9,
    "max_new_tokens": 120
  }
}
```

With this structure, the client can separate text rendering from warning display, and generation-setting changes remain traceable in production.

### Splitting SSE event types simplifies UI branching

A single `data:` line works, but separating event types improves maintainability:

```text
event: token
data: M

event: token
data: y

event: warning
data: Dropped unsupported characters: \ud83d\ude0a

event: done
data: {"tokens":120}
```

In the browser, `source.addEventListener("token", ...)` lets you handle character accumulation, warning UI, and completion logic without conflicts.

### Server latency measurement example

```python
import time

start = time.perf_counter()
with torch.no_grad():
    out = state["model"].generate(idx, body.max_new_tokens, 0.8, 20, 0.9)
latency_ms = (time.perf_counter() - start) * 1000

resp = decode(out[0].tolist())[len(ids):]
print(f"latency_ms={latency_ms:.1f} chars={len(resp)}")
```

Sample log:

```text
latency_ms=184.2 chars=139
latency_ms=201.7 chars=120
```

Accumulated, these let you compute p50/p95 latency and explain streaming's perceived improvement with numbers.

### Architecture Comparison Table

| Configuration | Pros | Cons | When to Use |
| --- | --- | --- | --- |
| Single `/chat` synchronous | Simple implementation | High perceived wait | Initial validation |
| `/chat` + `/chat/stream` combined | UX improvement, backward compat | Two code paths to maintain | Demo/prototype |
| Queue + worker async | Scalability | Operational complexity | High-load services |

This series chose the second configuration—it offers the best perceived-UX improvement relative to implementation cost.

### Minimum security/operations checks

- Set an upper bound on input length (`prompt` max length, `history` max turns).
- Enforce a per-request `max_new_tokens` cap.
- Avoid logging raw prompt text in server logs.
- Specify CORS policy and attach rate limiting for public deployment.

Even for a small-model demo, following these four prevents expensive rework when scaling to a real service.

## Operational Layers Needed When Deploying a Chatbot Wrapper

Seeing streaming work locally is different from running a stable service. A chatbot wrapper needs API, session, and observability layers on top of model inference.

### Session and context management

Context length breaks first in conversational services. Naively accumulating long conversations exceeds model input limits quickly. Explicitly implement policies like keeping the most recent N turns, summary compression, or pinning important messages.

### Streaming protocol stabilization

SSE and WebSocket streams commonly experience mid-network disconnects. The server must safely terminate partial generation, and the client must avoid duplicate rendering on retry. Assigning sequence numbers to token events makes reconnection handling and debugging easier.

### API boundary and security defaults

Request body size limits, timeouts, concurrent request caps, and simple auth tokens should be defaults. Unlimited requests—even against a lightweight model—quickly degrade service quality.

### Observability metrics and alerts

The key in chatbot operations is discovering failures fast. Minimum metrics:

- Streaming start success rate
- Request completion rate (normal end / timeout / error)
- Average response latency (first token, full completion)
- Conversation length distribution and context truncation rate

Bundling these into a dashboard lets you separate model issues from API issues.

## Pre-Deployment Checklist

Before deploying the chatbot wrapper, failure-scenario checks come before feature demos:

- Does context truncation work as intended on long inputs?
- Does the UI recover gracefully on network disconnection mid-stream?
- Are timeout and queue policies consistent under concurrent request spikes?
- Does the log avoid storing user-sensitive information?

Passing these checks greatly reduces operational risk beyond model quality.

## Final Operational Standard

Chatbot wrapper quality is not judged by answer text alone. Response latency, failure recovery, session consistency, and observability must all be evaluated for true service quality.

The goal at this final stage is not "working" but "operationally viable working."

## Practice FAQ

### Should I follow these steps rigorously even for a tiny model?

Yes—smaller models benefit more from strict contracts. Low capacity magnifies input noise and implementation inconsistency. Establishing reproducible experiment units first accelerates quality improvements even before scaling.

### What if experiment speed and quality management conflict?

To go faster, reduce failure cost rather than increasing experiment count. Locking configs, standardizing logs, and storing checkpoint metadata let you run more *valid* experiments in the same time.

### What single thing is most worth recording?

The change rationale, expected effect, and observed result—briefly. Especially "why this value was chosen" lets you reconstruct decision context weeks later.

## Conclusion Note

Chatbot wrapper completeness is achieved only when model output and operational stability align simultaneously. At the final stage, polish failure recovery and observability before adding features.

In the first week after deployment, set metric thresholds conservatively for early warnings.

Periodically reviewing operational logs accumulates failure patterns as team knowledge.

The key is observability.

## Summary

This article wrapped the fine-tuned small GPT into a FastAPI + SSE-based chatbot system. Connecting the model, conversation history, streaming response, and browser UI gave all the code we have built so far its first application form.

We also confirmed that chatbot quality is not determined by model weights alone. System-level decisions—prompt format, lifespan loading, streaming method, unsupported character handling—directly affect user experience.

This series traveled from tokenizer through embedding, attention, block, GPT class, training, sampling, fine-tuning, and chatbot wrapper. A small model, but we touched the entire LLM application flow end to end.

## Answering the Opening Questions

- **What components does a chatbot need beyond the model?**
  - This article's chatbot required not just the model but conversation-history serialization, a FastAPI endpoint, SSE streaming, and a browser UI to be complete. `build_prompt`, `/chat`, `/chat/stream`, and `EventSource` each handled a different piece of that system.
- **Why must you design the multi-turn prompt format yourself?**
  - The model doesn't remember conversation state on its own, so you must specify how to concatenate past utterances in `User: ...
Bot: ...` format. Ending with `Bot:` as in the article's format is what makes it clear to the model where the current turn's answer should start.
- **What improves when you load the model once via FastAPI lifespan?**
  - Loading `ckpt_sft.pt` once in `lifespan` means you don't re-read the checkpoint per request, greatly reducing response latency and resource waste. Even with a small model, the structure of reusing `state["model"]` is what lets `/chat` and the streaming endpoint respond more immediately to users.

<!-- toc:begin -->
## In this series

- [LLM from Scratch 101 (1/9): Turning Text into Numbers](./01-tokenizer.md)
- [LLM from Scratch 101 (2/9): From Integers to Vectors and Positions](./02-embedding.md)
- [LLM from Scratch 101 (3/9): Deciding Which Tokens to Focus On](./03-attention.md)
- [LLM from Scratch 101 (4/9): The Transformer Block: A Unit of Depth](./04-transformer-block.md)
- [LLM from Scratch 101 (5/9): Assembly: Completing the GPT Model Class](./05-gpt-model.md)
- [LLM from Scratch 101 (6/9): Learning via Gradients](./06-training-loop.md)
- [LLM from Scratch 101 (7/9): Sampling — Generating Text from a Trained Model](./07-inference.md)
- [LLM from Scratch 101 (8/9): Adapting the Base Model to Specific Tasks](./08-finetuning.md)
- **LLM from Scratch 101 (9/9): Turning Your LLM into a Chatbot — FastAPI + Streaming (current)**

<!-- toc:end -->

## References

- [FastAPI Lifespan Events (Documentation)](https://fastapi.tiangolo.com/advanced/events/)
- [MDN EventSource (Documentation)](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)
- [FastAPI StreamingResponse (Documentation)](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [nanoGPT (GitHub)](https://github.com/karpathy/nanoGPT)

Tags: LLM, PyTorch, Transformer, Tutorial
