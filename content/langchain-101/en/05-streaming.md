---
title: "LangChain 101 (5/6): Streaming — handling real-time output"
series: langchain-101
episode: 5
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- LangChain
- LCEL
- Python
- LLM
last_reviewed: '2026-05-01'
seo_description: Streaming is not a different chain design; it is a different way
  of consuming the chain while the model is still generating.
---

# LangChain 101 (5/6): Streaming — handling real-time output

Long model responses feel slow even when total latency is acceptable. Streaming changes that experience by letting the same chain surface useful output before the full response is finished.

This is the fifth post in the LangChain 101 series. It covers `stream()`, `astream()`, and the practical patterns for delivering partial output to users.

![The flow at a glance](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/05/05-02-the-flow-at-a-glance.en.png)
*The flow at a glance*
> Streaming is not a different chain design; it is a different way of consuming the chain while the model is still generating.

## Questions to Keep in Mind

- How do `stream()` and `astream()` change user experience and server structure?
- When collecting chunks, how should empty chunks and mid-stream errors be handled?
- Where should a FastAPI streaming endpoint handle backpressure and exceptions?

## Minimal runnable example

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

chain = (
    ChatPromptTemplate.from_template("Explain {topic} in three sentences.")
    | ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"])
    | StrOutputParser()
)

for chunk in chain.stream({"topic": "astream"}):
    print(chunk, end="", flush=True)
```

## Basic streaming

![Direct model and chain streaming comparison](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/05/05-01-basic-streaming.en.png)

*Direct model and chain streaming comparison*
`stream()` returns a generator. Iterate over it with a `for` loop.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

# stream directly from the LLM
print("=== LLM direct streaming ===")
for chunk in llm.stream("List five advantages of Python."):
    print(chunk.content, end="", flush=True)

print("\n\n=== chain streaming ===")
prompt = ChatPromptTemplate.from_messages([
    ("human", "Explain {topic} in three paragraphs."),
])

chain = prompt | llm | StrOutputParser()

for chunk in chain.stream({"topic": "vector search"}):
    print(chunk, end="", flush=True)

print()
```

`end=""` and `flush=True` suppress the newline and force immediate output. `StrOutputParser()` extracts the string content from each `AIMessageChunk` during streaming.

From an operational standpoint, the difference matters: with the parser attached, downstream HTTP responses or UI events receive plain text, keeping the pipeline simple.

---

## Collecting streamed output

![Reassembling chunks into final text](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/05/05-02-collecting-streamed-output.en.png)

*Reassembling chunks into final text*
When you need the full text after streaming, accumulate chunks in a list.

```python
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

chain = (
    ChatPromptTemplate.from_messages([("human", "{question}")])
    | llm
    | StrOutputParser()
)

chunks = []
print("streaming: ", end="")
for chunk in chain.stream({"question": "What is FAISS?"}):
    print(chunk, end="", flush=True)
    chunks.append(chunk)

full_text = "".join(chunks)
print(f"\n\ntotal characters: {len(full_text)}")
```

This pattern is extremely common in production. You stream for user experience, then retain the full text for logging, caching, or post-processing.

---

## astream() — async streaming

![Async for streaming execution path](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/05/05-03-astream-async-streaming.en.png)

*Async for streaming execution path*
In async frameworks like FastAPI, use `astream()` with `async for`.

```python
import asyncio
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

chain = (
    ChatPromptTemplate.from_messages([("human", "Explain {topic} briefly.")])
    | llm
    | StrOutputParser()
)

async def stream_response(topic: str) -> None:
    print(f"streaming: {topic}")
    async for chunk in chain.astream({"topic": topic}):
        print(chunk, end="", flush=True)
    print()

async def main() -> None:
    await stream_response("embedding vectors")
    await stream_response("FAISS indexes")

asyncio.run(main())
```

The mental model is simple: `stream()` for synchronous CLI scripts, `astream()` for async web servers. Chain structure stays the same; only the caller context changes.

---

## FastAPI streaming endpoint

In production, stream to the client over HTTP using Server-Sent Events.

```python
import os

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

app = FastAPI()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

chain = (
    ChatPromptTemplate.from_messages([("human", "{question}")])
    | llm
    | StrOutputParser()
)

@app.get("/stream")
async def stream_endpoint(question: str):
    async def generate():
        async for chunk in chain.astream({"question": question}):
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")
```

Start the server:

```bash
pip install fastapi uvicorn
uvicorn main:app --reload
```

Test it:

```bash
curl "http://localhost:8000/stream?question=What+is+RAG"
```

The most common production issue here is not code — it is the network layer. If a proxy or gateway buffers responses, the application is streaming but the client sees everything arrive at once. "Streaming does not work" complaints usually start in the deployment path configuration, not in LangChain.

---

## astream_events() for fine-grained control

![Selecting specific chain events](https://yeongseon-books.github.io/book-public-assets/assets/langchain-101/05/05-04-astream-events-for-fine-grained-control.en.png)

*Selecting specific chain events*
`astream_events()` exposes individual events from each component in the chain.

```python
import asyncio
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

chain = (
    ChatPromptTemplate.from_messages([("human", "Explain {topic}.")])
    | llm
    | StrOutputParser()
)

async def main() -> None:
    async for event in chain.astream_events({"topic": "FAISS"}, version="v2"):
        event_type = event["event"]
        if event_type == "on_llm_stream":
            chunk = event["data"].get("chunk", "")
            if hasattr(chunk, "content") and chunk.content:
                print(chunk.content, end="", flush=True)
    print()

asyncio.run(main())
```

`astream_events()` is useful when a chain has multiple components and you need to distinguish which one is producing output — for example, isolating latency between Prompt, Retriever, and LLM steps, or identifying which events appear mid-flow in a Tool Calling chain.

## Attaching streaming logs with callbacks

In operations, "it was shown" matters less than "what was shown when." A callback handler lets you log token-level events in a consistent format.

```python
import os
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

class StreamLogHandler(BaseCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        if token:
            print(f"[token] {token!r}")

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
    streaming=True,
    callbacks=[StreamLogHandler()],
)

chain = (
    ChatPromptTemplate.from_template("Explain {topic} in two paragraphs.")
    | llm
    | StrOutputParser()
)

for chunk in chain.stream({"topic": "callback handlers"}):
    print(chunk, end="", flush=True)
```

This approach is more useful in server operations than CLI demos. Storing token events alongside a `request_id` helps reproduce user complaints like "the response just stopped."

## stream vs astream operational selection criteria

| Factor | `stream()` | `astream()` |
|---|---|---|
| Caller context | Synchronous function | Async function |
| Iteration style | `for chunk in ...` | `async for chunk in ...` |
| Best fit | CLI, batch scripts | FastAPI, WebSocket servers |
| Cancellation | Relatively simple | Needs disconnect/timeout branching |

Establishing a team rule upfront (e.g. "all API layer code uses `astream` exclusively") prevents event-loop blocking issues.

## Handling empty chunks and mid-stream errors

Streaming event formats vary by model provider, so code must not mistake empty chunks for errors.

```python
def safe_stream(chain, payload: dict) -> str:
    chunks: list[str] = []
    try:
        for chunk in chain.stream(payload):
            if not chunk:
                continue
            print(chunk, end="", flush=True)
            chunks.append(chunk)
    except Exception as exc:
        print(f"\n[stream-error] {type(exc).__name__}: {exc}")
    finally:
        print()
    return "".join(chunks)
```

The key principle: even on failure, do not lose the partial text already sent. Show partial results to the user and log the exception type alongside the last chunk timestamp.

## SSE format in FastAPI

Plain `text/plain` works, but when the frontend needs per-event boundaries, SSE format is more reliable.

```python
import json
import os

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

app = FastAPI()

chain = (
    ChatPromptTemplate.from_template("Answer briefly: {question}")
    | ChatGroq(model="llama-3.1-8b-instant", api_key=os.environ["GROQ_API_KEY"])
    | StrOutputParser()
)

@app.get("/sse")
async def sse(question: str):
    async def generate():
        async for chunk in chain.astream({"question": question}):
            if not chunk:
                continue
            payload = json.dumps({"type": "token", "text": chunk}, ensure_ascii=False)
            yield f"data: {payload}\n\n"
        yield 'data: {"type":"done"}\n\n'

    return StreamingResponse(generate(), media_type="text/event-stream")
```

With this structure, the client can use the `done` event to determine rendering completion definitively. Adding timeout policies is also far easier when working with event boundaries.

## Measuring first-token latency in LangSmith

Streaming quality depends more on first-token latency than total latency. Tracking both values separately in your trace logs pays dividends.

```text
trace_id=trc_05_stream_001
model=llama-3.1-8b-instant
latency_total_ms=1820
latency_first_token_ms=410
tokens_out=278
status=success
```

Even with identical total latency, a fast first token feels dramatically better. Tuning order is typically `first_token -> tokens/sec -> total_latency`.

## Streaming operations checklist

- **Cancellation handling**: Does the generation loop stop immediately when the client disconnects?
- **Partial result policy**: On mid-stream error, is partial text preserved for the user?
- **Observability**: Are first-token latency, total latency, and output token count recorded?
- **Buffering path**: Is chunk buffering disabled at the proxy/gateway layer?
- **Retry policy**: Are mid-stream retries handled as new requests rather than continuations?

Including this checklist in pre-deployment review prevents the classic scenario where the demo works but production feels sluggish.

## Combining Tool Calling with streaming

In production chat interfaces, tool execution and final-answer streaming appear together. Show users two distinct phases:

1. **Tool execution phase**: status events like "calculating" or "looking up"
2. **Final response generation phase**: token-by-token streaming

```python
from langchain_core.messages import HumanMessage, ToolMessage

async def run_tool_then_stream(question: str):
    messages = [HumanMessage(content=question)]

    # Round 1: check for tool requests
    first = llm_with_tools.invoke(messages)
    messages.append(first)

    for tc in first.tool_calls:
        result = tool_map[tc["name"]].invoke(tc["args"])
        print(f"[tool] {tc['name']} -> {result}")
        messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))

    # Round 2: stream the final answer
    async for chunk in llm_with_tools.astream(messages):
        if hasattr(chunk, "content") and chunk.content:
            print(chunk.content, end="", flush=True)
    print()
```

This pattern lets users understand that the system is executing tools, not frozen, improving perceived quality.

## Backpressure-aware transmission control

Pushing tokens to a slow client without limits can grow server memory and queues rapidly. Minimal flow control at the transmission layer is essential.

```python
import asyncio

async def throttled_generate(chain, payload: dict, delay_sec: float = 0.0):
    async for chunk in chain.astream(payload):
        if not chunk:
            continue
        yield chunk
        if delay_sec > 0:
            await asyncio.sleep(delay_sec)
```

In practice, adjust network buffer policies, SSE frame sizes, and gateway timeouts together rather than relying solely on artificial delays. The point is that the application layer must not completely ignore backpressure.

## Streaming event schema design

Agreeing on an event schema with the client simplifies frontend rendering logic.

| event.type | payload example | frontend action |
|---|---|---|
| `status` | `{ "phase": "tool_calling" }` | Show status badge |
| `token` | `{ "text": "FAISS" }` | Append to output area |
| `usage` | `{ "tokens_out": 180 }` | Update cost/stats display |
| `done` | `{}` | Re-enable input field |
| `error` | `{ "message": "provider timeout" }` | Show error toast |

Without this agreement, the frontend must parse provider-specific exception formats directly, and maintenance cost rises quickly.

---

## What to notice in this code

- The chain definition barely changes from the `invoke()` version. The real change is how you consume output.
- `stream()` means synchronous iteration, while `astream()` means asynchronous iteration over the same logical response.
- Collecting chunks into a list and joining them later is a common pattern for logging, caching, or post-processing.
- `astream_events()` exposes chain-level events, which is useful for debugging and instrumentation beyond simple token display.

## Where engineers get confused

- Streaming does not change the final answer format. It changes when the application receives each piece.
- Async streaming affects the caller too, so your framework and endpoint style must support async flow.
- Event streams are powerful, but they are unnecessary overhead if all you need is progressive text rendering.

## Checklist

- [ ] I can run the same chain with both `invoke()` and `stream()`
- [ ] I can explain the difference between `astream()` and `astream_events()`
- [ ] I understand how `StreamingResponse` fits around streamed chunks in FastAPI

## Conclusion

Streaming in LangChain requires one change: replace `invoke()` with `stream()` or `astream()`. Chain structure stays the same. With FastAPI, `StreamingResponse` delivers the output to clients in real time.

The final post assembles all the components covered in this series into one complete chain.

## Answering the Opening Questions

- **How do `stream()` and `astream()` change user experience and server structure?**
  `stream()` returns a synchronous iterator of partial output, while `astream()` fits async servers. Both reduce time to first visible token.

- **When collecting chunks, how should empty chunks and mid-stream errors be handled?**
  Empty chunks can be normal protocol events, and mid-stream errors should preserve partial output plus error context.

- **Where should a FastAPI streaming endpoint handle backpressure and exceptions?**
  Handle cancellation, slow clients, and provider exceptions at the generator or async-generator boundary so connection cleanup and logging stay separate.

<!-- toc:begin -->
## In this series

- [LangChain 101 (1/6): LangChain introduction — LCEL and the Runnable interface](./01-lcel-runnable-basics.md)
- [LangChain 101 (2/6): Prompt and LLM chain — assembling your first chain](./02-prompt-llm-chain.md)
- [LangChain 101 (3/6): Retriever — document search and context injection](./03-retriever.md)
- [LangChain 101 (4/6): Tool calling — connecting external tools](./04-tool-calling.md)
- **LangChain 101 (5/6): Streaming — handling real-time output (current)**
- LangChain 101 (6/6): Putting it together — a complete chain in one file (upcoming)

<!-- toc:end -->

---

## References

- [LangChain streaming guide](https://python.langchain.com/docs/expression_language/streaming/)
- [astream_events reference](https://python.langchain.com/docs/expression_language/interface/)
- [FastAPI StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)

Tags: LangChain, LCEL, Python, LLM
