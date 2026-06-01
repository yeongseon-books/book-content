---
title: "LLM App Foundations 101 (1/6): LLM API first call — sending your first request"
series: llm-app-foundations-101
episode: 1
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
last_reviewed: '2026-06-01'
seo_description: 'Walk through your first Groq API call: how the SDK wraps an HTTP request, what fields to read in the response, and which numbers to log from day one.'
---

# LLM App Foundations 101 (1/6): LLM API first call — sending your first request

The first confusing thing about LLM application development is not the model. It is the boundary between your code and the model service. A chat UI makes the whole thing feel magical, but the runtime reality is plain: your application sends an HTTP request and receives a JSON response. That round trip is the foundation.

This is the first post in the LLM App Foundations 101 series.

Getting this structure right early makes everything that follows clearer. Reading token usage, designing prompt structures, attaching streaming — all of those build on the request-response shape of the first call. If you skip this step, every later feature stays in a "it works but I don't know why" state.

At the beginner stage, it is more useful to learn which fields go into the request body and which fields come back in the response than to craft clever prompts. The model is a remote service. Remote services always have explicit contracts and failure modes. Once you internalize that, you can explain problems with logs and structure instead of guesswork.

Here we will build the smallest success path with the Groq Python SDK and turn the first call into an operational mental model.

![LLM API first call: sending your first request](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/01/01-01-llm-api-first-call-sending-your-first-re.en.png)
*LLM API first call: sending your first request*

## Questions to Keep in Mind

- What request-response shape sits underneath the SDK call?
- When the first call fails, should you inspect authentication, the model id, or the message format first?
- Where do you read the response body, token usage, and model name?

## Why this post matters

The first call is not a toy example. It is the reference point for every feature that comes after. The location where you read token usage, the location where you extract the response body, the location where you record the model name — all of those are decided here. If you skip this step loosely, cost analysis and incident analysis both get blurry later.

If you think of the LLM as "one smart object," you will look for problems in the wrong place. In reality, the call involves network requests, authentication headers, JSON serialization, model selection, and response parsing — a full remote invocation chain. So understanding the first call means understanding the service boundary first, not the model itself.

In production this difference shows up immediately. If you get a `401`, you check credentials, not the prompt. If you get a `429`, you check call frequency before touching the wording. Once you build the habit of seeing the first call transparently, everything that follows in LLM development becomes less mysterious and far more manageable.

## The best way to understand the first call: see it as a JSON request and JSON response round trip, not as an SDK method

The Groq SDK is convenient, but it does not change the underlying contract. `client.chat.completions.create()` still builds a JSON request and wraps the JSON response in a Python object. So when understanding the first call, "which fields do I send, which fields do I receive" is more accurate than "how do I call the method."

This perspective matters because SDK syntax changes while the core contract stays stable. Sending a model ID, sending a message array, and reading generated text plus usage from the response — that structure carries forward into streaming and tool calling unchanged.

> The core of the first LLM call is not the syntax for invoking the model. It is understanding the input-output contract with the remote service as a visible structure.

## Core concepts

The first sentence to remember is simple. An LLM API is still an API. Your application does not talk to the model directly — it calls a model service. So the request contains a model and input messages, and the response contains generated text plus metadata like usage.

![JSON request and response flow](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/01/01-01-what-an-llm-api-is.en.png)

*JSON request and response flow*

Conceptually, the request body looks like this:

```json
{
  "model": "llama-3.1-8b-instant",
  "messages": [
    {
      "role": "user",
      "content": "Show me a small Python example that reads an environment variable."
    }
  ]
}
```

The three blocks to look at first in the response are `model`, `choices`, and `usage`:

```json
{
  "model": "llama-3.1-8b-instant",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "import os\nprint(os.environ['HOME'])"
      }
    }
  ],
  "usage": {
    "prompt_tokens": 24,
    "completion_tokens": 31,
    "total_tokens": 55
  }
}
```

The actual setup is short. Create an account, issue a key, store it in an environment variable, install the SDK. The important habit is keeping the key out of source code.

```bash
export GROQ_API_KEY="your-issued-key"
```

```python
import os

api_key = os.environ["GROQ_API_KEY"]
print(f"API key loaded: {api_key[:6]}...")
```

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install groq
```

![Client setup and first call chain](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/01/01-02-sending-your-first-request.en.png)

*Client setup and first call chain*

The smallest success path is the code below. This single block confirms the first milestone: "I sent a request, got an answer back, and read the body."

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": "Explain Python list comprehensions in one paragraph.",
        }
    ],
)

print(completion.choices[0].message.content)
```

Now stop reading just the body. You need the full response object — model name, token usage, and finish reason — to track what actually happened.

![Completion object fields and branches](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/01/01-03-inspecting-the-response-object.en.png)

*Completion object fields and branches*

```python
import json
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": "Explain the difference between an HTTP API and an SDK in three sentences.",
        }
    ],
)

print(json.dumps(completion.to_dict(), indent=2, ensure_ascii=False))
```

In production, the minimum values to record are the generated text, `usage`, model name, and `finish_reason`. With those four, you have enough material to explain cost and truncation issues.

![Authentication rate limit and retry branches](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/01/01-04-why-the-http-mental-model-still-matters.en.png)

*Authentication rate limit and retry branches*

Even with an SDK, the network boundary does not disappear. A slow response might be a network or token-length issue. A `401` might be an authentication issue. A `429` might be a rate limit issue. So when understanding the first call, the habit of reading boundary conditions before the prompt is what matters.

![Sync waits and async gather comparison](https://yeongseon-books.github.io/book-public-assets/assets/llm-app-foundations-101/01/01-05-synchronous-and-asynchronous-patterns.en.png)

*Sync waits and async gather comparison*

Synchronous calling is the simplest pattern for getting started:

```python
import os

from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": "Explain asynchronous programming in one paragraph.",
        }
    ],
)

print(completion.choices[0].message.content)
```

When your application already runs on an async runtime or needs to coordinate multiple I/O tasks, async calling is the natural fit:

```python
import asyncio
import os

from groq import AsyncGroq

client = AsyncGroq(api_key=os.environ["GROQ_API_KEY"])

async def main() -> None:
    completion = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": "Give me two situations where asyncio is useful.",
            }
        ],
    )

    print(completion.choices[0].message.content)

asyncio.run(main())
```

Handling multiple requests concurrently extends into patterns like `asyncio.gather()`. Since this post focuses on the first success path and structural understanding, we will close with one complete reference example:

```python
import os

from groq import Groq

def main() -> None:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a concise Python tutor.",
            },
            {
                "role": "user",
                "content": (
                    "Explain the difference between a Python function and a method "
                    "in no more than five sentences, and add one short example line."
                ),
            },
        ],
    )

    content = completion.choices[0].message.content or ""
    usage = completion.usage

    print("=== answer ===")
    print(content)
    print()
    print("=== metadata ===")
    print(f"model: {completion.model}")
    print(f"prompt_tokens: {usage.prompt_tokens}")
    print(f"completion_tokens: {usage.completion_tokens}")
    print(f"total_tokens: {usage.total_tokens}")

if __name__ == "__main__":
    main()
```

## Common misconceptions

- It is easy to assume the SDK removes the HTTP boundary, but authentication, rate limiting, and network latency remain.
- It is tempting to read only `choices[0].message.content`, but in production you also need `usage`, `model`, and `finish_reason`.
- Async calling looks like an advanced feature, but it is fundamentally a structural choice about waiting for multiple I/O tasks. It does not improve output quality.
- It is easy to blame prompt wording when the first call fails, but at the beginner stage, a missing API key, an incorrect model ID, or a malformed message array are far more common causes.

## Provider comparison and failure patterns

At the first-call stage, it helps to see the commonalities and differences in the request contract across providers rather than just one SDK's syntax. The same chat API shape varies slightly in field names and response wrappers between providers. Copy-pasting without knowing these differences leads to `400` errors or parsing failures.

The minimum call with the OpenAI Python SDK looks like this:

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-4.1-mini",
    input="Explain the difference between a Python list and a tuple in three sentences.",
)

print(response.output_text)
```

The minimum call with the Anthropic Python SDK looks like this:

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-3-5-haiku-latest",
    max_tokens=200,
    messages=[
        {"role": "user", "content": "Explain the difference between a Python list and a tuple in three sentences."}
    ],
)

print(message.content[0].text)
```

The key point is not switching models — it is fixing where you extract the response body. OpenAI uses `output_text` or block-based responses; Anthropic uses a `content` array. If your team defines an `extract_text(response)` helper early, switching providers barely touches the upper-layer logic.

```python
def extract_text(provider: str, payload) -> str:
    if provider == "groq":
        return payload.choices[0].message.content or ""
    if provider == "openai":
        return getattr(payload, "output_text", "") or ""
    if provider == "anthropic":
        blocks = getattr(payload, "content", [])
        return "".join(getattr(block, "text", "") for block in blocks)
    raise ValueError(f"Unsupported provider: {provider}")
```

### Logging fields to add from the first call

Even in beginner code, these fields are worth logging immediately. They are what let you connect tokens, cost, and incidents later.

| Field | Purpose | What breaks if missing |
|---|---|---|
| `provider` | Identifies which service was called | Cannot isolate failure segments |
| `model` | Actual model that responded | Cannot track model-change regressions |
| `request_id` | Provider-issued request identifier | Support queries and tracing are difficult |
| `latency_ms` | Response time | Can only guess at slowness causes |
| `prompt_tokens` / `completion_tokens` | Usage | Cost analysis is impossible |
| `finish_reason` | Why generation stopped | Truncation detection is delayed |

A minimal logging function is enough:

```python
import time

def call_and_log(client, model: str, messages: list[dict[str, str]]) -> str:
    started = time.perf_counter()
    completion = client.chat.completions.create(model=model, messages=messages)
    latency_ms = (time.perf_counter() - started) * 1000

    choice = completion.choices[0]
    usage = completion.usage
    print(
        {
            "provider": "groq",
            "model": completion.model,
            "latency_ms": round(latency_ms, 1),
            "finish_reason": choice.finish_reason,
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens,
        }
    )
    return choice.message.content or ""
```

### Basic retry skeleton for 401, 429, and 5xx

The fastest way to build operational instinct at the first-call stage is to make error branches explicit. A `401` is never solved by retrying. A `429` and some `5xx` responses are valid candidates for backoff retries.

```python
import random
import time

def call_with_retry(create_fn, max_attempts: int = 4):
    for attempt in range(1, max_attempts + 1):
        try:
            return create_fn()
        except Exception as exc:  # Narrow to SDK-specific exceptions for production.
            msg = str(exc)
            if "401" in msg or "403" in msg:
                raise
            if ("429" in msg or "500" in msg or "503" in msg) and attempt < max_attempts:
                sleep_s = (2 ** (attempt - 1)) + random.random() * 0.2
                time.sleep(sleep_s)
                continue
            raise
```

What matters at this stage is not a perfect error framework. It is drawing a clear line between errors that should fail immediately and errors that should be retried with back-off.

### Building cost awareness from the start

Getting into the habit of estimating per-request cost early makes later prompt design far more grounded.

| Scenario | prompt_tokens | completion_tokens | Price assumption (USD/1M) | Estimated cost per call |
|---|---:|---:|---|---:|
| Short Q&A | 180 | 120 | input 0.20 / output 0.60 | 0.000108 |
| Medium explanation | 850 | 400 | input 0.20 / output 0.60 | 0.000410 |
| Long analysis | 2200 | 900 | input 0.20 / output 0.60 | 0.000980 |

```python
def estimate_cost_usd(
    prompt_tokens: int,
    completion_tokens: int,
    in_price_per_m: float,
    out_price_per_m: float,
) -> float:
    return (prompt_tokens / 1_000_000) * in_price_per_m + (
        completion_tokens / 1_000_000
    ) * out_price_per_m
```

Prices change with providers and model versions, so the calculation habit matters more than the exact numbers. Once you wire this function in, you can see "good answer" and "sustainable answer" on the same screen.

## Post-first-call safety harness

Once the first call succeeds, many teams jump straight to prompt experiments. From an operational perspective, it is better to attach safety mechanisms first. Request ID tracking, timeouts, and idempotency keys cost less when added early.

```python
import os
import uuid
from typing import Any

from groq import Groq

def create_completion_with_request_context(client: Groq, messages: list[dict[str, str]]) -> Any:
    request_id = str(uuid.uuid4())
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        timeout=20.0,
    )
    print({"request_id": request_id, "model": completion.model})
    return completion

client = Groq(api_key=os.environ["GROQ_API_KEY"])
result = create_completion_with_request_context(
    client,
    [{"role": "user", "content": "Summarize the core principles of Python exception handling in three sentences."}],
)
print(result.choices[0].message.content)
```

The point is not a complex framework. It is the minimum mechanism that guarantees "I can find this call again later." That single step already changes incident response speed significantly.

## Operational checklist

- [ ] After the first successful call, run an OpenAI or Anthropic auxiliary call to confirm response-parsing differences.
- [ ] Do not treat `401`, `429`, and `5xx` as the same error — codify per-branch handling (immediate failure vs. retry).
- [ ] Log `model`, `finish_reason`, `latency_ms`, and `total_tokens` as shared fields on every call.
- [ ] Wire the cost estimation function and verify numbers for at least 3 scenarios (short/medium/long request).
- [ ] `GROQ_API_KEY` is set as an environment variable; no key string appears in source.
- [ ] `pip install groq` succeeded and `import groq` runs without error.
- [ ] `client.chat.completions.create(model=..., messages=[...])` returns a 200 response.
- [ ] You printed `choices[0].message.content`, `usage.total_tokens`, and `model` from the response.
- [ ] You ran the same call once synchronously and once asynchronously.

## Summary

The first LLM API call looks small, but it already contains the full core structure. Read the key from the environment, create the client, send model and messages, read body and metadata from the response. Every feature that comes after is just handling this loop with more precision.

Three instincts to take away from this post. First, the SDK is a convenience layer — the core contract is still JSON in, JSON out. Second, do not read only the body; also read token usage, model name, and finish reason so you build operational awareness. Third, sync vs. async is not a quality question — it is an application structure question.

The next post keeps the same call but puts tokens at the center. Length limits, cost, and latency all converge on the token budget. Now that you understand the structure of the first call, it is time to read that structure in numbers.

## Answering the Opening Questions

- What request-response shape sits underneath the SDK call?
  - It looks like an SDK method, but underneath it sends a JSON request containing the model ID and message array, and receives a JSON response containing generated text and usage.

- When the first call fails, should you inspect authentication, the model id, or the message format first?
  - Start with authentication and key placement, then narrow to the model ID and message array format.

- Where do you read the response body, token usage, and model name?
  - Read the body from `choices[0].message.content`, token accounting from `usage`, and the actual model from `model`.

<!-- toc:begin -->
## In this series

- **LLM App Foundations 101 (1/6): LLM API first call — sending your first request (current)**
- LLM App Foundations 101 (2/6): Understanding tokens — cost, limits, and context windows (upcoming)
- LLM App Foundations 101 (3/6): Prompt engineering basics — system, user, and assistant roles (upcoming)
- LLM App Foundations 101 (4/6): Few-shot and chain-of-thought — steering better answers (upcoming)
- LLM App Foundations 101 (5/6): Managing conversation state — building a multi-turn chatbot (upcoming)
- LLM App Foundations 101 (6/6): Handling streaming responses — real-time output (upcoming)

<!-- toc:end -->

---

## References

- [Groq quickstart](https://console.groq.com/docs/quickstart)
- [Groq Python SDK](https://github.com/groq/groq-python)
- [Groq API reference](https://console.groq.com/docs/api-reference)
- [Groq models](https://console.groq.com/docs/models)

### Related Series

- [LLM API Production 101](../../llm-api-production-101/en/01-structured-output.md) — picks up where this series ends. After first calls, tokens, and basic prompting, that series tackles structured output, tool calling, streaming, and retries — the problems you hit once the toy demo has to actually serve users.

Tags: LLM, OpenAI, Prompt Engineering, Python
