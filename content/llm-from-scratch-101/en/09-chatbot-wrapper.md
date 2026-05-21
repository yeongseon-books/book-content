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

This is the final article in the LLM from Scratch 101 series.

---

## Questions to Keep in Mind

- What does a chatbot need beyond the model itself?
- Why design the multi-turn prompt format yourself?
- What do you gain by loading the model once via FastAPI lifespan?

## Big Picture

![LLM from Scratch 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/09/09-01-chatbot-model-history-streaming-ui.en.png)

*LLM from Scratch 101 chapter 9 flow overview*

This picture places Turning Your LLM into a Chatbot — FastAPI + Streaming inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

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

## Answering the Opening Questions

- **What does a chatbot need beyond the model itself?**
  - The article treats Turning Your LLM into a Chatbot — FastAPI + Streaming as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Why design the multi-turn prompt format yourself?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What do you gain by loading the model once via FastAPI lifespan?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

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
