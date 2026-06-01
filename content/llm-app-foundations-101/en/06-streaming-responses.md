---
title: "LLM App Foundations 101 (6/6): Handling streaming responses — real-time output"
series: llm-app-foundations-101
episode: 6
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- LLM
- OpenAI
- Prompt Engineering
- Python
last_reviewed: '2026-05-01'
seo_description: Enhance user experience by implementing real-time LLM output with streaming, incremental rendering, and efficient async response handling.
---

# LLM App Foundations 101 (6/6): Handling streaming responses — real-time output

One of the easiest ways to make an LLM application feel slow is to treat it like an ordinary blocking API call. The server sends a prompt, waits in silence, and only returns once the entire answer is finished. The feature works, but the experience feels worse than it needs to.

This is the final post in the LLM App Foundations 101 series.

The problem is not total generation time — it is visibility. A user staring at a blank box for several seconds cannot tell whether the model is thinking, the network is stalled, or the app is broken. If the first characters appear within a few hundred milliseconds and text continues flowing, the same five-second wait feels entirely different.

Streaming also changes how you think about the response itself. Without streaming, a completion is one object with one final text field. With streaming, the answer becomes a sequence of chunks — some carrying text, some carrying metadata, one signaling the end. Once you start building chat UIs or browser copilots, that event-oriented model becomes more natural than waiting for one large string.

![Handling streaming responses: real-time output](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/06/06-01-handling-streaming-responses-real-time-o.en.png)
*Handling streaming responses: real-time output*

## Questions to Keep in Mind

- Does streaming finish the answer sooner, or show the generation flow earlier?
- How do you read text, finish signals, and usage from chunks?
- How does a FastAPI server relay the model stream to a user?

## Why this post matters

Once answer quality is sufficient, the first thing users notice is often not speed but silence. When the application shows nothing for several seconds, users cannot confirm whether the model is actually working. Streaming does not hide latency — it exposes progress.

Streaming also changes how you handle the response in code. A non-streaming response is a single completed object. A streaming response is an event sequence. Some chunks carry text, some carry finish signals or metadata. Once you start building UIs, this event-driven model is actually more natural.

From an operations perspective, streaming may not increase throughput, but it improves measurable product metrics: time to first token, user cancellation rate, and long-answer abandonment rate. Streaming is not just a code pattern — it is a measurable UX strategy.

## The best way to think about streaming: consuming a flow of generation events, not receiving a single response body

The moment you set `stream=True`, your mental model shifts. Previously you received one finished string. Now you handle pieces arriving in order. Your consumer code must manage three concerns simultaneously: partial text for the user, the full accumulated text for storage, and usage metadata that may only appear at the end.

This perspective matters because treating streaming as merely a display trick leads to gaps in storage, logging, pipeline integration, and cancellation handling later. A stream is not text — it is an event flow. Understanding it that way aligns UI and server design together.

> The core of streaming is not making the model finish faster. It is exposing the in-progress answer as an event flow so that waiting becomes legible.

## The smallest Groq streaming example

![Stream chunks arriving before full completion](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/06/06-01-the-smallest-groq-streaming-example.en.png)

*Stream chunks arriving before full completion*

With the Groq SDK, streaming starts with one parameter: `stream=True`. Instead of receiving one completed response object, you receive an iterable stream of chunks.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

stream = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "system",
            "content": "You are a concise Python tutor.",
        },
        {
            "role": "user",
            "content": "Explain Python generators in five sentences.",
        },
    ],
    temperature=0.3,
    stream=True,
)

for chunk in stream:
    print(chunk)
```

The output looks verbose at first, but printing raw chunks is useful for debugging — it reveals which chunks carry text and which carry only control information.

## Extracting text from each chunk

![Chunk fields for text finish and usage](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/06/06-02-extracting-text-from-each-chunk.en.png)

*Chunk fields for text finish and usage*

In chat streaming, the text you want to render lives in `chunk.choices[0].delta.content`. Not every chunk contains visible text, so your loop should treat missing content as normal.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

stream = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": "Explain the difference between FastAPI and Flask for beginners.",
        }
    ],
    temperature=0.2,
    stream=True,
)

parts: list[str] = []

for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
        parts.append(delta)

final_text = "".join(parts)
print("\n---")
print(final_text)
```

The important defensive habit: always expect some chunks to contain no text. Depending on the SDK, a chunk may carry role information, a stop marker, or usage metadata without any new output content.

## Streaming versus sync and async patterns

![Sync and async streaming execution comparison](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/06/06-03-streaming-versus-sync-and-async-patterns.en.png)

*Sync and async streaming execution comparison*

Streaming and async are not the same concept. Streaming describes how the response arrives (in pieces). Async describes how your application waits (without blocking). You can have synchronous streaming or asynchronous streaming.

```python
import asyncio
import os

from groq import AsyncGroq

client = AsyncGroq(api_key=os.environ["GROQ_API_KEY"])

async def main() -> None:
    stream = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": "Explain why asyncio helps in web servers.",
            }
        ],
        temperature=0.2,
        stream=True,
    )

    parts: list[str] = []

    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            print(delta, end="", flush=True)
            parts.append(delta)

    final_text = "".join(parts)
    print("\n---")
    print(final_text)

asyncio.run(main())
```

For a small CLI tool, synchronous streaming is enough. For a multi-user FastAPI server, asynchronous streaming is the natural fit.

## Reading token usage during or after streaming

![Final chunk usage and fallback aggregation](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/06/06-04-reading-token-usage-during-or-after-stre.en.png)

*Final chunk usage and fallback aggregation*

In streaming, usage metadata usually appears only at the end. With Groq, the final chunk may expose provider metadata under `x_groq`.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

stream = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "Explain Python decorators."}],
    stream=True,
)

parts: list[str] = []
last_chunk = None

for chunk in stream:
    last_chunk = chunk
    delta = chunk.choices[0].delta.content
    if delta:
        parts.append(delta)

final_text = "".join(parts)
print(final_text)

usage = None
if last_chunk is not None:
    groq_meta = getattr(last_chunk, "x_groq", None)
    if groq_meta is not None:
        usage = getattr(groq_meta, "usage", None)

if usage is not None:
    print("prompt_tokens:", usage.prompt_tokens)
    print("completion_tokens:", usage.completion_tokens)
    print("total_tokens:", usage.total_tokens)
else:
    print("usage metadata was not present in the final chunk")
```

The final-chunk metadata can be empty in production: a proxy may close the connection early, the SDK version may change, or the client may cancel mid-stream. For that reason, capture usage from both the last chunk and server-side request-level metrics.

## A robust stream consumer with TTFT measurement

In production, you want a single consume function that handles text accumulation, time-to-first-token measurement, and graceful cancellation together.

```python
import time

def consume_stream(stream) -> tuple[str, float | None]:
    parts: list[str] = []
    first_token_at: float | None = None
    started_at = time.perf_counter()

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if not delta:
            continue

        if first_token_at is None:
            first_token_at = time.perf_counter() - started_at

        parts.append(delta)

    return "".join(parts), first_token_at
```

This gives two key values: the safely reconstructed final text, and the time-to-first-token (TTFT) — the moment the user actually sees the first character. Streaming quality is often better measured by TTFT than by total generation time.

## Streaming operations: cancellation, error branching, backpressure

Once streaming enters a real service, the first need is not pretty output but termination control. User cancellation, network drops, and server restarts all happen mid-stream.

```python
class StreamCancelled(Exception):
    pass

def consume_with_cancel(stream, is_cancelled) -> str:
    parts: list[str] = []
    for chunk in stream:
        if is_cancelled():
            raise StreamCancelled("User requested cancellation")

        delta = chunk.choices[0].delta.content
        if delta:
            parts.append(delta)

    return "".join(parts)
```

This pattern prevents "the model call runs to completion even after the user cancelled" waste.

### Streaming error classification

Unlike non-streaming calls, streaming must distinguish "failure before start" from "failure mid-stream."

| Failure point | Example | Recommended response |
|---|---|---|
| Before start | Auth failure, invalid model ID | Immediate error response |
| Mid-stream | Network drop, client disconnect | Save partial result + record interrupted state |
| Near end | Missing done event | Timeout then force-close |

Treating mid-stream failures as simple 500 errors makes the user feel "nothing happened." Preserving partial text and providing retry guidance is far better.

### Backpressure mitigation with sentence-buffered SSE

When browser consumption is slow, server buffers can fill. Buffering at sentence boundaries rather than individual tokens reduces transmission overhead and stabilizes the user experience.

```python
async def sentence_buffered_sse(stream):
    buffer = ""
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if not delta:
            continue

        buffer += delta
        if buffer.endswith((".", "!", "?", "\n")):
            yield f"data: {buffer}\n\n"
            buffer = ""

    if buffer:
        yield f"data: {buffer}\n\n"
    yield "data: [done]\n\n"
```

This approach trades per-token real-time feel for reduced transmission load and more stable rendering.

### Streaming metrics to track separately

Streaming improvements are invisible in average response time. Separate these metrics.

| Metric | Meaning | Goal |
|---|---|---|
| TTFT (time to first token) | When the first character arrives | As low as possible |
| Stream completion rate | Fraction reaching `[done]` normally | As high as possible |
| Mid-stream abort rate | Cancellation/disconnect fraction | Track by cause |
| Avg tokens streamed | Average streamed token count | Baseline per use case |

Streaming quality is about "how quickly does output become visible" — without measuring TTFT separately, improvements go unnoticed.

## Relaying the stream through FastAPI

![FastAPI relaying chunks to the browser](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/06/06-05-relaying-the-stream-through-fastapi.en.png)

*FastAPI relaying chunks to the browser*

In a browser-based product, the server sits between the provider and the user — holding API keys, authentication, prompt policy, and usage logging.

```python
import os

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from groq import AsyncGroq

app = FastAPI()
client = AsyncGroq(api_key=os.environ["GROQ_API_KEY"])

@app.get("/chat/stream")
async def chat_stream(prompt: str) -> StreamingResponse:
    async def event_gen():
        stream = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            stream=True,
        )

        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield f"data: {delta}\n\n"

        yield "data: [done]\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream")
```

Common failure modes to anticipate: browsers disconnecting mid-stream (server must clean up), reverse proxies buffering chunks (delivering them in bursts instead of incrementally), and missing termination events (frontend cannot distinguish normal completion from network failure). SSE relay looks like simple output code but is actually a transmission protocol that includes termination signals and cancellation handling.

## Common misconceptions

- Streaming does not significantly reduce total generation time. Its real value is perceived latency and visibility.
- Streaming and async are not the same concept. One is about response delivery; the other is about how your application waits.
- Not every chunk contains text. Empty `delta` is normal — assuming otherwise breaks the consumer loop.
- Focusing only on incremental rendering while forgetting final-string reconstruction is a common mistake. Storage, caching, and downstream processing all need the full text.
- Omitting an explicit termination signal makes it impossible for browser UIs to distinguish normal completion from connection failure.

## Operational checklist

- [ ] Verified that `stream=True` returns a different object type than the default
- [ ] Chunk handler safely treats `choices[0].delta.content` as possibly `None`
- [ ] Confirmed that concatenated stream output equals the non-stream result
- [ ] Written both synchronous `for` and asynchronous `async for` versions of the stream consumer
- [ ] FastAPI route uses `StreamingResponse` with explicit `media_type` and termination event
- [ ] TTFT is measured separately from total response time

## Answering the Opening Questions

- Does streaming finish the answer sooner, or show the generation flow earlier?
  - Streaming mainly shows partial output earlier. The model still generates the full answer, but the user sees chunks while generation continues.

- How do you read text, finish signals, and usage from chunks?
  - Accumulate delta text from chunks, then read finish signals and usage from the final provider-specific chunk or a fallback accounting path.

- How does a FastAPI server relay the model stream to a user?
  - FastAPI wraps the upstream model chunks in a server-side stream via `StreamingResponse` and forwards them to the browser or client.

<!-- toc:begin -->
## In this series

- [LLM App Foundations 101 (1/6): LLM API first call — sending your first request](./01-llm-api-first-call.md)
- [LLM App Foundations 101 (2/6): Understanding tokens — cost, limits, and context windows](./02-understanding-tokens.md)
- [LLM App Foundations 101 (3/6): Prompt engineering basics — system, user, and assistant roles](./03-prompt-engineering-basics.md)
- [LLM App Foundations 101 (4/6): Few-shot and chain-of-thought — steering better answers](./04-few-shot-and-cot.md)
- [LLM App Foundations 101 (5/6): Managing conversation state — building a multi-turn chatbot](./05-conversation-state.md)
- **LLM App Foundations 101 (6/6): Handling streaming responses — real-time output (current)**

<!-- toc:end -->

---

## References

### Official docs

- [Groq text generation docs](https://console.groq.com/docs/text-chat)
- [Groq Python SDK repository](https://github.com/groq/groq-python)
- [FastAPI StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [MDN Server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)

### Related series

- [Managing conversation state — building a multi-turn chatbot](./05-conversation-state.md)
- [Streaming in depth — chunk handling and error recovery](../../llm-api-production-101/en/03-streaming-in-depth.md)
- [Chatbot pattern — conversation history and state](../../ai-app-patterns-101/en/01-chatbot-pattern.md)

Tags: LLM, OpenAI, Prompt Engineering, Python
