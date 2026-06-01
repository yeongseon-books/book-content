---
episode: 3
language: en
last_reviewed: '2026-05-15'
series: llm-api-production-101
status: publish-ready
tags:
- LLM
- OpenAI
- Streaming
- Python
targets:
  ebook: true
  medium: true
  mkdocs: true
  tistory: false
title: "LLM API Production 101 (3/6): Streaming in depth — chunk handling and error recovery"
seo_description: Master LLM streaming by treating responses as partial state, enforcing inactivity timeouts, and preserving output during connection failures.
---

# LLM API Production 101 (3/6): Streaming in depth — chunk handling and error recovery

Streaming looks flashy in a demo, but in production it is really a protocol problem. Showing the first token quickly makes an application feel alive and reduces abandonment on long answers. That part is obvious. What is less obvious is that `stream=True` changes the failure model. Chunks may arrive without text, the connection may go quiet before it ends, the stream may fail after partial output has already been shown, and the final metadata may never arrive.

This is the third post in the LLM API Production 101 series.

A non-streaming call usually ends as either success or exception. Streaming is different: progress and failure can coexist within a single request. Thirty chunks may arrive normally, then the connection may go silent for twelve seconds, then drop. That request is neither a clean success nor an empty failure.

So the streaming consumer cannot look only at the final string. It needs to track accumulated text, the time of the last valid chunk, whether a finish signal was observed, and where failure occurred. Without that discipline, you get the hardest kind of bug report: "sometimes the answer stops halfway through."

In this post, we use the Groq streaming path as a reference and work through the baseline chunk loop, empty-delta handling, read timeout enforcement, partial-result preservation, and retry decisions from an operational perspective.

Here we focus on safely consuming and recovering from streaming responses that carry partial state.

![Streaming in depth: chunk handling and error recovery](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/03/03-01-streaming-in-depth-chunk-handling-and-er.en.png)
*Streaming in depth: chunk handling and error recovery*
> A stream is not one late string; it is partial state that can succeed, fail, or remain incomplete.

## Questions to Keep in Mind

- Why should streaming be treated as a session with partial state instead of one final string?
- How should empty chunks and mid-stream failures be represented?
- After a streaming failure, what should be preserved and what should be rebuilt?

## Why this post matters

Streaming looks like a UX enhancement, but it is actually code that consumes a transport protocol. That means partial responses, connection terminations, timeouts, and missing finish signals are problems the application must handle directly. Ignoring this responsibility does not improve the user experience — it makes it more confusing.

In production environments especially, partial responses are meaningful state. If the user has seen part of an answer, that call is not an "empty failure." It needs to appear in logs, be reflected in the UI, and be assumed by retry policies. Tokens already sent are not retractable.

Observability also matters. Whether progress was happening up to a certain point, whether a finish signal appeared, whether the interruption was a transport timeout or a provider-side cut — distinguishing these is what makes failure analysis possible. That distinction is what turns streaming from "a fancy feature" into "an explainable operational path."

## What changes when the response is a stream

![Streaming session with partial-state flow](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/03/03-01-what-changes-when-the-response-is-a-stre.en.png)

*Streaming session with partial-state flow*

A non-streaming call ends in success with a final object or failure with an exception. Streaming is different. Thirty chunks may arrive normally, then nothing comes for twelve seconds, then the connection drops. That request is neither full success nor empty failure.

At minimum, you should track: accumulated text so far, the time of the last meaningful chunk, whether a finish signal was observed, and whether the ending was normal completion, timeout, or exception. With that information, you can treat the stream as an observable timeline rather than a simple exception.

## The baseline chunk loop

![Execution path of the baseline chunk loop](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/03/03-02-the-baseline-chunk-loop.en.png)

*Execution path of the baseline chunk loop*

The minimal reference implementation looks like this.

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

stream = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": "Explain FastAPI dependency injection for beginners.",
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

This loop simultaneously creates visible output for the user and a final string for the application to preserve. But it is not production-ready yet: it lacks empty-chunk handling, inactivity detection, and partial-result preservation on exceptions.

## Treating empty chunks as normal

Treating text-free chunks as errors makes logs noisy. Some chunks carry only role information or termination metadata with no new content.

```python
for chunk in stream:
    choice = chunk.choices[0]
    delta = choice.delta.content

    if delta is not None and delta != "":
        print(delta, end="", flush=True)
        parts.append(delta)

    if choice.finish_reason is not None:
        print(f"\nfinish_reason={choice.finish_reason}")
```

The important point is that the consumer stays calm. Empty chunks are not warning signals — they are part of the protocol. Recording normal events as anomalies makes it harder to spot real failures.

## Enforcing timeouts outside the loop

![Sync loop versus async timeout comparison](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/03/03-03-enforcing-timeouts-outside-the-loop.en.png)

*Sync loop versus async timeout comparison*

A synchronous `for chunk in stream:` loop blocks while waiting for the next chunk. Checking the clock inside the loop body only runs after something has already arrived. To detect true inter-chunk inactivity, you must wrap the read itself.

```python
import asyncio
import os

from groq import AsyncGroq

INACTIVITY_TIMEOUT_SECONDS = 8.0

client = AsyncGroq(api_key=os.environ["GROQ_API_KEY"])

async def consume_stream(prompt: str) -> dict:
    stream = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    parts: list[str] = []

    while True:
        try:
            chunk = await asyncio.wait_for(
                anext(stream),
                timeout=INACTIVITY_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError as exc:
            return {"status": "timeout", "text": "".join(parts), "error": str(exc)}
        except StopAsyncIteration:
            return {"status": "completed", "text": "".join(parts)}

        delta = chunk.choices[0].delta.content
        if delta:
            parts.append(delta)
            print(delta, end="", flush=True)

asyncio.run(consume_stream("Explain why Python context managers are useful."))
```

What matters here is not total request time but "is progress still happening." If you must stay on a synchronous path, a transport timeout is the next best thing, though it cannot detect true per-chunk silence as precisely.

```python
import os

from groq import Groq

client = Groq(
    api_key=os.environ["GROQ_API_KEY"],
    timeout=8.0,
)

stream = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "Explain Python generators."}],
    stream=True,
)

for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
```

## Keeping partial output on failure

![State preserved in a streaming result object](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/03/03-04-keeping-partial-output-on-failure.en.png)

*State preserved in a streaming result object*

Returning a result object that always includes partial text makes recovery and UI handling easier.

```python
import os

from groq import Groq

def stream_text(prompt: str) -> dict:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    stream = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        stream=True,
    )

    parts: list[str] = []
    finish_reason = None

    try:
        for chunk in stream:
            choice = chunk.choices[0]
            delta = choice.delta.content
            if delta:
                parts.append(delta)
                print(delta, end="", flush=True)

            if choice.finish_reason is not None:
                finish_reason = choice.finish_reason

        return {
            "status": "completed",
            "text": "".join(parts),
            "finish_reason": finish_reason,
            "saw_finish_reason": finish_reason is not None,
        }
    except Exception as exc:
        return {
            "status": "failed",
            "text": "".join(parts),
            "error": str(exc),
            "finish_reason": finish_reason,
            "saw_finish_reason": finish_reason is not None,
        }
```

The value of this wrapper is simple. The caller can distinguish completed and failed while still receiving any text produced before the interruption. A web UI can keep the partial text visible and append "response was interrupted" instead of blanking the screen.

## Signals that the stream may be incomplete

![Retry decision after stream interruption](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/03/03-05-retrying-after-a-streaming-failure.en.png)

*Retry decision after stream interruption*

You cannot always prove a stream was incomplete, but suspicious signals exist: mid-sentence endings, unclosed code blocks, missing finish_reason, and absent usage metadata. These checks gauge transport completeness, not answer quality.

Retry decisions depend on whether the user has already seen partial output. For internal pipelines, a full retry is often fine. For interactive UIs, keeping the partial response visible and attaching the next attempt as a new block is more honest.

```python
result = stream_text("Explain the difference between FastAPI and Flask.")

print("partial_text=")
print(result["text"])

if result["status"] == "completed":
    print("stream completed normally")
else:
    print("stream interrupted")
    print("show retry button to the user")
```

## Delivering chunks to the browser with FastAPI SSE

Once the terminal loop is stable, the next step is web delivery. Server-Sent Events (SSE) let you forward chunks over a single HTTP connection in order. The key principle is not to pass raw model chunks through, but to wrap them as application events that carry state alongside content.

```python
import json
import os

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from groq import Groq

app = FastAPI()
client = Groq(api_key=os.environ["GROQ_API_KEY"])

def sse_event(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

@app.get("/api/stream")
def stream_answer(q: str):
    def event_generator():
        parts: list[str] = []
        stream = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": q}],
            stream=True,
            temperature=0,
        )

        yield sse_event("start", {"status": "started"})
        try:
            for chunk in stream:
                choice = chunk.choices[0]
                delta = choice.delta.content
                if delta:
                    parts.append(delta)
                    yield sse_event("token", {"text": delta})

                if choice.finish_reason is not None:
                    yield sse_event("finish", {"finish_reason": choice.finish_reason})

            yield sse_event("done", {"text": "".join(parts)})
        except Exception as exc:
            yield sse_event(
                "error",
                {
                    "message": "stream interrupted",
                    "partial_text": "".join(parts),
                    "error_type": type(exc).__name__,
                },
            )

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

The advantage of this structure is that the UI and logs share the same state model. The frontend accumulates `token` events for immediate rendering and uses the `error` event to keep `partial_text` visible while showing a retry button. Operators can aggregate failure patterns by event type.

## Client reconnection with event IDs

When SSE is deployed in production, mobile network environments cause frequent disconnections. Attaching event IDs lets the client track how far it got, enabling recovery on reconnection.

```python
def sse_event_with_id(event_id: int, event: str, data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    return f"id: {event_id}\nevent: {event}\ndata: {payload}\n\n"

event_id = 0
event_id += 1
wire = sse_event_with_id(event_id, "token", {"text": "Hello"})
print(wire)
```

The server logs event IDs alongside session IDs, and the client stores the last received ID to send a `Last-Event-ID` header on reconnection. Starting with full regeneration is acceptable, but having this structure in place dramatically improves disconnection recovery quality for interactive products.

## Structured streaming session logs

Streaming failures are hard to reproduce after the fact, so capturing a session summary while the request is alive is worthwhile. Collecting token count, chunk count, last event time, and termination reason in one record makes post-incident analysis much faster.

```python
import time
from dataclasses import dataclass

@dataclass
class StreamSessionLog:
    request_id: str
    chunk_count: int
    text_chars: int
    status: str
    finish_reason: str | None
    elapsed_ms: int

def build_stream_log(
    request_id: str,
    chunk_count: int,
    text: str,
    status: str,
    finish_reason: str | None,
    started_at: float,
) -> StreamSessionLog:
    return StreamSessionLog(
        request_id=request_id,
        chunk_count=chunk_count,
        text_chars=len(text),
        status=status,
        finish_reason=finish_reason,
        elapsed_ms=int((time.monotonic() - started_at) * 1000),
    )
```

This log structure is simple but powerful. If many requests have `status=failed` with high `chunk_count`, you suspect a network-segment problem first. If `finish_reason` distribution shifts suddenly, you detect a model or parameter change quickly.

## Streaming combined with structured output

After stabilizing text streaming, teams often try JSON structured output on the same path. The common mistake is calling `json.loads()` on partial strings as chunks arrive. A JSON object may be syntactically incomplete until the final chunk, so parsing should be deferred until after the finish signal.

```python
import json

parts: list[str] = []
finished = False

def on_chunk(delta_text: str | None, finish_reason: str | None) -> None:
    global finished
    if delta_text:
        parts.append(delta_text)
    if finish_reason is not None:
        finished = True

def finalize_structured_output() -> dict:
    raw = "".join(parts)
    if not finished:
        raise RuntimeError("stream ended without explicit finish signal")
    return json.loads(raw)
```

This pattern matters operationally because it separates failure locations clearly. "Transport failure mid-stream" and "parse failure after completion" map to different retry strategies: the former is a transport problem, the latter is a prompt/schema problem.

One more practical tip: even when JSON parsing succeeds, do not trust it immediately. On the structured-output path, a final Pydantic validation step is still necessary. Smooth transport does not guarantee business-field correctness.

Streaming path quality breaks into three layers: transport completeness, syntactic completeness, and semantic completeness. Separating logs and exceptions across these three layers turns vague reports like "sometimes the answer stops" into concrete improvement work.

## Common misconceptions

- Thinking streaming is just "printing the normal response faster" causes you to miss partial-failure handling entirely.
- Logging all text-free chunks as anomalies turns normal protocol events into noise.
- Checking the clock inside a synchronous iterator body cannot detect true inter-chunk inactivity.
- Discarding accumulated text on stream failure makes recovery and debugging harder.
- Retrying after partial output has been shown to the user is both an API policy and a UX policy.

## Operational checklist

- [ ] Built a consumption loop that maintains both user output and internal accumulated text
- [ ] Treated empty deltas and termination metadata as normal protocol events
- [ ] Applied a read-wrapping timeout or transport timeout to detect inactivity
- [ ] Returned partial text and finish-signal status together on failure
- [ ] Defined separate retry policies for UI-facing and internal-pipeline paths

## Closing

In this post, we treated streaming not as a flashy output mode but as a response session with partial state. The baseline chunk loop is only a starting point. Production requires empty-chunk handling, read timeout enforcement, partial-result preservation, and finish-signal verification working together.

The important point is that even when a stream breaks, you should be able to explain what happened. How far the output got, why it stopped, and what to preserve on retry — capturing these as state is what makes the streaming path a trustworthy system component.

The next post applies the same operational perspective to cost and latency. If streaming was about handling partial responses, caching is about avoiding repeated computation for identical work.

## Answering the Opening Questions

- **Why should streaming be treated as a session with partial state instead of one final string?**
  A streamed response accumulates across many chunks, so you need session state for accumulated text, finish signals, and failure context.

- **How should empty chunks and mid-stream failures be represented?**
  Empty chunks may be normal protocol signals and should not be discarded. Mid-stream failures should preserve partial output and error cause together.

- **After a streaming failure, what should be preserved and what should be rebuilt?**
  Preserve partial results and request identifiers. Rebuild the next request with careful attention to duplicate output, user display, and log correlation.

<!-- toc:begin -->
## In this series

- [LLM API Production 101 (1/6): Structured output — JSON mode and response schemas](./01-structured-output.md)
- [LLM API Production 101 (2/6): Tool calling — connecting functions to the model](./02-tool-calling.md)
- **LLM API Production 101 (3/6): Streaming in depth — chunk handling and error recovery (current)**
- LLM API Production 101 (4/6): Caching strategies — reducing cost and latency (upcoming)
- LLM API Production 101 (5/6): Retry and error handling — making API calls reliable (upcoming)
- LLM API Production 101 (6/6): Rate limit management — patterns for staying within limits (upcoming)

<!-- toc:end -->

## References

### Official Docs

- [Groq Text Chat docs](https://console.groq.com/docs/text-chat)
- [MDN Server-sent events guide](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)

### Verification-Friendly References

- [Python asyncio.wait_for documentation](https://docs.python.org/3/library/asyncio-task.html#asyncio.wait_for)

### Related Series

- [Tool calling — connecting functions to the model](./02-tool-calling.md)
- [Caching strategies — reducing cost and latency](./04-caching-strategies.md)

Tags: LLM, OpenAI, Streaming, Python
