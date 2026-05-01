---
title: Retry and error handling — making API calls reliable
series: llm-api-production-101
episode: 5
language: en
status: draft
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- LLM
- OpenAI
- Streaming
- Python
last_reviewed: '2026-04-30'
---

# Retry and error handling — making API calls reliable

> LLM API Production 101 (5/6)

Example code: [github.com/yeongseon-books/llm-api-production-101](https://github.com/yeongseon-books/llm-api-production-101/tree/main/en/05-retry-and-error-handling)

Once an LLM API call sits on a production path, failure stops being an exception in the human sense. It becomes part of the runtime. Networks stall. Providers slow down. Requests hit time limits. A client process can lose connectivity at the wrong moment. The real question is not whether failures happen. It is whether the application reacts to them predictably.

One of the most common mistakes is retrying everything. Teams catch a broad exception, sleep, try again, and call that resilience. The problem is that not all failures are temporary. Authentication problems are not fixed by waiting two seconds. Invalid request payloads are not fixed by a second attempt. Schema-validation failures are not fixed just because the same call was repeated three times.

That is why retries work only when they begin with error classification. A retry policy is not “try again when something goes wrong.” It is “retry only the failures that are likely to be transient, with bounded backoff and explicit stop conditions.” In this post, we will use `tenacity` to build that policy around a Groq API call.

The main idea is simple: **a retry is not a friendly loop, it is a bounded recovery strategy built on top of error classification**.

---

## Runtime setup

The examples assume Python 3.10 or later with `groq` and `tenacity` installed.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install groq tenacity
export GROQ_API_KEY="your-issued-key"
```

---

## Why all failures should not share one retry policy

Retries help only when the failure is likely to go away. A short network interruption may resolve on the next attempt. A temporary timeout may succeed after a brief pause. Some 5xx provider failures are also retry candidates.

Other failures are different:

- invalid API credentials
- malformed request payloads
- application-side parsing bugs
- schema-validation failures caused by bad output contracts

If you retry those blindly, you do not increase reliability. You only increase latency, noise, and wasted quota. The first step is to separate retryable failures from failures that should stop immediately.

---

## What `tenacity` gives you

`tenacity` lets you describe retry conditions, wait strategy, and stop rules as policy instead of scattering `while True`, counters, and `sleep()` calls through the code.

The smallest example looks like this:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
)
def flaky_operation() -> str:
    raise RuntimeError("temporary failure")
```

That is only the shape. In a real LLM path, the important part is constraining **which exceptions** trigger the retry.

---

## Creating an error hierarchy for retry decisions

One practical pattern is to normalize low-level exceptions into application-level categories.

```python
class RetryableLLMError(Exception):
    pass

class NonRetryableLLMError(Exception):
    pass
```

Once those exist, the retry layer can ignore provider-specific details and focus on the higher-level decision: retryable or not. That keeps the retry policy easy to read even if the provider SDK evolves later.

---

## Adding exponential backoff to a Groq call

The example below retries only errors that the application classifies as transient. One operational detail matters before the code starts: the Groq client can apply its own retries. To avoid stacking SDK retries on top of `tenacity` retries by accident, the sample disables SDK retries and lets the application policy own the loop.

```python
import logging
import os

from groq import APIConnectionError, APIStatusError, Groq, RateLimitError
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
client = Groq(api_key=os.environ["GROQ_API_KEY"], max_retries=0)

class RetryableLLMError(Exception):
    pass

class NonRetryableLLMError(Exception):
    pass

@retry(
    retry=retry_if_exception_type(RetryableLLMError),
    wait=wait_exponential_jitter(initial=1, max=8),
    stop=stop_after_attempt(3),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def call_llm(messages: list[dict]) -> str:
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0,
        )
        return completion.choices[0].message.content
    except RateLimitError as exc:
        raise RetryableLLMError("provider rate limit hit") from exc
    except APIConnectionError as exc:
        raise RetryableLLMError("provider connection failed") from exc
    except APIStatusError as exc:
        if exc.status_code >= 500:
            raise RetryableLLMError(f"provider server error: {exc.status_code}") from exc
        raise NonRetryableLLMError(f"provider request failed: {exc.status_code}") from exc

messages = [
    {"role": "system", "content": "You are a concise Python tutor."},
    {"role": "user", "content": "Explain Python context managers in three sentences."},
]

try:
    text = call_llm(messages)
    print(text)
except NonRetryableLLMError as exc:
    logger.error("request failed without retry: %s", exc)
except RetryableLLMError as exc:
    logger.error("request still failed after retries: %s", exc)
```

Three things matter here.

First, `retry_if_exception_type(RetryableLLMError)` makes the retry scope explicit.

Second, `wait_exponential_jitter(initial=1, max=8)` creates bounded exponential backoff with jitter instead of immediate hammering.

Third, `reraise=True` ensures that the final failure is not swallowed after all attempts are exhausted.

---

## Which failures are retryable

In practice, a useful first-pass classification looks like this.

### Usually retryable

- network interruptions
- connection failures and transport-level timeouts
- transient 5xx responses
- some rate-limit responses such as 429

### Usually not retryable or separately handled

- authentication failures
- malformed request bodies
- missing or invalid model names
- application bugs
- schema-validation failures in structured output

That last case is worth stressing. If a Pydantic validation step fails because the model returned the wrong shape, retrying the exact same request may not help. A prompt adjustment, fallback path, or user-visible error is often more honest than blind repetition.

---

## Moving classification into a dedicated function

If the retry wrapper grows too many `except` branches, pull classification into its own function.

```python
def classify_exception(exc: Exception) -> Exception:
    if isinstance(exc, (RateLimitError, APIConnectionError)):
        return RetryableLLMError(str(exc))

    if isinstance(exc, APIStatusError):
        if exc.status_code >= 500:
            return RetryableLLMError(str(exc))
        return NonRetryableLLMError(str(exc))

    return NonRetryableLLMError(f"unexpected error: {exc}")
```

Then the call path becomes smaller:

```python
try:
    completion = client.chat.completions.create(...)
except Exception as exc:
    raise classify_exception(exc) from exc
```

This is easier to maintain when you later add more provider-specific exception types or change your retry policy.

---

## Choosing attempt count and backoff

More retries do not automatically mean more resilience. The right values depend on three questions:

- how long can the user wait
- how much value is there in another attempt
- how expensive is a repeated call in latency and quota

For interactive UI paths, two or three attempts are often enough. Background jobs can justify longer retry windows. `wait_exponential_jitter(initial=1, max=8)` is a reasonable starting point, not a universal answer. Immediate five-attempt retry loops are usually too aggressive.

---

## What the user should see after final failure

Retries do not eliminate failure. They shape failure.

After the last allowed attempt, the application should make at least three things clear:

- what short message the user receives
- what details are logged internally
- where automatic recovery stops

In practice, that often means logging fields such as `retryable`, `attempt_count`, and `final_error_type`, while keeping the user-facing message stable and short. Raw provider exception text is usually too noisy or too revealing to display directly.

---

## Closing

In this post, we used `tenacity`, exponential backoff, and a small error hierarchy to build a more reliable LLM call path. The central lesson is that retry policy starts with classification, not with a loop. Decide what deserves another attempt first. Only then decide how many attempts and how much delay are acceptable.

Caching reduced repeated work. Retries smooth over temporary failure. The final post steps even further out and looks at the outer constraint around all of this: how to keep request flow inside the provider’s rate limits without turning traffic spikes into outages.

<!-- toc:begin -->
## In this series

- [Structured output — JSON mode and response schemas](./01-structured-output.md)
- [Tool calling — connecting functions to the model](./02-tool-calling.md)
- [Streaming in depth — chunk handling and error recovery](./03-streaming-in-depth.md)
- [Caching strategies — reducing cost and latency](./04-caching-strategies.md)
- **Retry and error handling — making API calls reliable (current)**
- Rate limit management — patterns for staying within limits (upcoming)

<!-- toc:end -->

---

## References

- <https://tenacity.readthedocs.io/en/latest/>
- <https://console.groq.com/docs/text-chat>

Tags: LLM, OpenAI, Streaming, Python
