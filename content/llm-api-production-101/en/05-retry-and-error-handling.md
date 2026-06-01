---
episode: 5
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
title: "LLM API Production 101 (5/6): Retry and error handling — making API calls reliable"
seo_description: Build reliable LLM applications by implementing an error classification system and bounded retry policies using exponential backoff and jitter.
---

# LLM API Production 101 (5/6): Retry and error handling — making API calls reliable

Once an LLM API call sits on a production path, failure stops being an exception in the human sense. It becomes part of the runtime. Networks stall. Providers slow down. Requests hit time limits. A client process can lose connectivity at the wrong moment. The real question is not whether failures happen. It is whether the application reacts to them predictably.

This is the fifth post in the LLM API Production 101 series.

One of the most common mistakes is retrying everything. Teams catch a broad exception, sleep, try again, and call that resilience. The problem is that not all failures are temporary. Authentication problems are not fixed by waiting two seconds. Invalid request payloads are not fixed by a second attempt. Schema-validation failures are not fixed just because the same call was repeated three times.

That is why retries work only when they begin with error classification. A retry policy is not "try again when something goes wrong." It is "retry only the failures that are likely to be transient, with bounded backoff and explicit stop conditions." This post uses `tenacity` to build that policy around a Groq API call.

![Retry and error handling: making API calls reliable](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/05/05-01-retry-and-error-handling-making-api-call.en.png)
*Retry and error handling: making API calls reliable*
> A good retry policy is not code that catches many exceptions — it is code that narrowly selects only the failures worth trying again.

## Questions to Keep in Mind

- Why should API failures not share one retry policy?
- Which failures are retryable, and which should fail fast?
- After final failure, how should user messages and internal logs differ?

## Why this post matters

Retry is not a simple reliability toggle. It is an operational policy that decides which failures are worth recovering from, and at what cost. Without this policy, transient network blips and permanent configuration errors flow through the same path, making the system both slower and noisier.

In the LLM path specifically, resending the same request is not free. Latency increases and token spend recurs. A retry must therefore pass the question "is there a reasonable chance this will succeed if I wait briefly?" before it fires. Increasing retry count without classification is closer to waste than to reliability.

Retry also connects to user experience. How many automatic recovery attempts are allowed, what message the user sees after final failure, and what details go into internal logs — all of these need to be decided ahead of time so that system behavior stays consistent.

## Why all failures should not share one retry policy

![Comparison between transient and permanent failures](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/05/05-01-why-all-failures-should-not-share-one-re.en.png)

*Comparison between transient and permanent failures*

Retries help only when the failure is likely to go away. A short network interruption may resolve on the next attempt. A temporary timeout may succeed after a brief pause. Some 5xx provider failures are also retry candidates.

Other failures are different:

- invalid API credentials
- malformed request payloads
- application-side parsing bugs
- schema-validation failures caused by bad output contracts

If you retry those blindly, you do not increase reliability. You only increase latency, noise, and wasted quota. The first step is always to separate retryable failures from failures that should stop immediately.

## What `tenacity` gives you

`tenacity` lets you describe retry conditions, wait strategy, and stop rules as policy instead of scattering `while True`, counters, and `sleep()` calls through the code.

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

## Creating an error hierarchy for retry decisions

![Structure for wrapping provider exceptions](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/05/05-02-creating-an-error-hierarchy-for-retry-de.en.png)

*Structure for wrapping provider exceptions*

The most practical pattern is to normalize low-level provider exceptions into application-level categories.

```python
class RetryableLLMError(Exception):
    pass

class NonRetryableLLMError(Exception):
    pass
```

Once those exist, the retry layer can ignore provider-specific details. The application passes only "retryable or not" to the retry policy. That keeps the policy readable even as the provider SDK evolves.

## Adding exponential backoff to a Groq call

![Retry flow with exponential backoff](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/05/05-03-adding-exponential-backoff-to-a-groq-cal.en.png)

*Retry flow with exponential backoff*

One operational detail matters first: the Groq client can apply its own retries. To avoid stacking SDK retries on top of `tenacity` retries, the sample disables SDK retries and lets the application policy own the loop.

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

Three things matter here. `retry_if_exception_type(RetryableLLMError)` makes the retry scope explicit. `wait_exponential_jitter(initial=1, max=8)` creates bounded exponential backoff with jitter instead of immediate hammering. `reraise=True` ensures the final failure is not swallowed after all attempts are exhausted.

## Which failures are retryable

![Decision flow for retryable error classes](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/05/05-04-which-failures-are-retryable.en.png)

*Decision flow for retryable error classes*

A useful first-pass classification:

**Usually retryable** — network interruptions, connection failures, transport-level timeouts, transient 5xx responses, some 429 rate-limit responses.

**Usually not retryable** — authentication failures, malformed request bodies, missing or invalid model names, application bugs, schema-validation failures in structured output.

That last case is worth stressing. If a Pydantic validation step fails because the model returned the wrong shape, retrying the exact same request is unlikely to help. A prompt adjustment, fallback path, or user-visible error message is often more honest than blind repetition.

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

```python
try:
    completion = client.chat.completions.create(...)
except Exception as exc:
    raise classify_exception(exc) from exc
```

This keeps the retry policy body stable even as SDK exception types grow.

## Reproducing failure deliberately to verify backoff logs

Retry code is hard to feel confident about until a real failure occurs. Before production, attach a deliberately-failing function in place of the provider call and verify that attempt count and log output match expectations.

```python
import logging

from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("retry-demo")

class RetryableLLMError(Exception):
    pass

attempt_counter = {"count": 0}

@retry(
    retry=retry_if_exception_type(RetryableLLMError),
    wait=wait_exponential_jitter(initial=1, max=2),
    stop=stop_after_attempt(3),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def flaky_lookup() -> str:
    attempt_counter["count"] += 1
    logger.info("attempt=%s", attempt_counter["count"])
    if attempt_counter["count"] < 3:
        raise RetryableLLMError("temporary upstream timeout")
    return "recovered on third attempt"

print(flaky_lookup())
```

This is policy verification, not failure reproduction. The logs show attempt count, wait intervals, and final outcome, so you can confirm before deployment: "does it really stop after three attempts?", "does backoff avoid thundering-herd timing?", "does it stop cleanly on success?"

## Separating final failure into user messages and internal logs

Once the retry budget is exhausted, the application must decide how to surface the failure. Users need a short, stable message. Internal systems need debugging fields.

```python
def build_failure_response(exc: Exception, attempt_count: int) -> tuple[dict, dict]:
    user_payload = {
        "message": "Please try again shortly. The request could not be completed.",
        "retryable": isinstance(exc, RetryableLLMError),
    }
    log_payload = {
        "retryable": isinstance(exc, RetryableLLMError),
        "attempt_count": attempt_count,
        "final_error_type": type(exc).__name__,
        "final_error_message": str(exc),
    }
    return user_payload, log_payload

user_payload, log_payload = build_failure_response(RetryableLLMError("timeout"), attempt_count=3)
print(user_payload)
print(log_payload)
```

This separation keeps user experience stable while giving operators immediate visibility into retry behavior and failure classification. Non-retryable errors (such as structured-output validation failures) can route to entirely different follow-up logic through the same function.

## What the user should see after final failure

![Paths after the final failed attempt](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/05/05-05-what-the-user-should-see-after-final-fai.en.png)

*Paths after the final failed attempt*

Retries do not eliminate failure. They shape failure into a more predictable form. After the last allowed attempt, three things must be clear: what the user sees, what goes into internal logs, and where automatic recovery stops. Internally, log fields like `retryable`, `attempt_count`, and `final_error_type` make post-incident analysis fast. Exposing raw provider exception text to users adds noise and sometimes leaks sensitive information.

## Retry budgets to prevent thundering-herd amplification

A per-request retry policy can still cause problems at scale. If all traffic fails simultaneously and each request retries three times, a 100 RPS path suddenly produces 300+ additional calls. A system-level retry budget caps the total retry volume within a time window.

```python
import time
from collections import deque

class RetryBudget:
    def __init__(self, window_seconds: int, max_retries_in_window: int) -> None:
        self.window_seconds = window_seconds
        self.max_retries_in_window = max_retries_in_window
        self.events: deque[float] = deque()

    def allow_retry(self) -> bool:
        now = time.monotonic()
        while self.events and now - self.events[0] >= self.window_seconds:
            self.events.popleft()

        if len(self.events) >= self.max_retries_in_window:
            return False

        self.events.append(now)
        return True

budget = RetryBudget(window_seconds=60, max_retries_in_window=120)
print(budget.allow_retry())
```

This is simpler than a full circuit breaker but effective: it caps retry volume during cascading failure, reducing pressure on both provider and application. In multi-worker deployments, sharing this counter through Redis makes the budget service-wide.

## Treating 429 and 5xx with different backoff curves

In production logs, 429 and 5xx carry different signals. 429 is a policy collision — the provider is telling you to slow down. 5xx is provider instability. Using the same wait strategy for both can either recover too slowly from 5xx or retry too aggressively into 429.

```python
import random

def compute_backoff_seconds(error_type: str, attempt: int) -> float:
    if error_type == "rate_limit":
        # 429: wait more conservatively
        return min(2 ** (attempt + 1), 16) + random.uniform(0, 0.5)

    if error_type == "server_error":
        # 5xx: shorter initial backoff for faster recovery
        return min(2**attempt, 8) + random.uniform(0, 0.3)

    return 0.0

for i in range(3):
    print("429 backoff", i, compute_backoff_seconds("rate_limit", i))
    print("5xx backoff", i, compute_backoff_seconds("server_error", i))
```

The exact numbers matter less than the separation. Once backoff policies are split, tuning becomes targeted: if 429 spikes cluster at certain hours, adjust only the rate-limit path; if 5xx increases, investigate provider switching or timeout redesign first.

## Recording retry attempts in request context

Debugging retry failures is hard when the final log only records the last exception. Recording each attempt's error type and planned wait makes root-cause separation much faster.

```python
from dataclasses import dataclass, field

@dataclass
class RetryAttempt:
    attempt: int
    error_type: str
    planned_sleep_seconds: float

@dataclass
class RetryTrace:
    request_id: str
    attempts: list[RetryAttempt] = field(default_factory=list)

    def add(self, attempt: int, error_type: str, planned_sleep_seconds: float) -> None:
        self.attempts.append(
            RetryAttempt(
                attempt=attempt,
                error_type=error_type,
                planned_sleep_seconds=planned_sleep_seconds,
            )
        )

trace = RetryTrace(request_id="req-2026-05-15-001")
trace.add(attempt=1, error_type="RateLimitError", planned_sleep_seconds=1.2)
trace.add(attempt=2, error_type="RateLimitError", planned_sleep_seconds=2.1)
print(trace)
```

These fields integrate directly into APM or structured logging. Operators can immediately see which error type repeats at which attempt, making backoff tuning and budget adjustments data-driven rather than gut-feel.

## Common misconceptions

- Increasing retry count does not automatically improve reliability — classification must come first.
- Omitting jitter from exponential backoff causes multiple requests to collide at the same retry instant.
- Stacking SDK retries on top of application retries inflates actual attempt count beyond what you intended.
- Structured-output validation failures are rarely fixed by resending the same request.
- Exposing the same level of detail to users and internal logs degrades both user experience and debugging quality.

## Operational checklist

- [ ] Separated retryable and non-retryable errors with the same criteria in both docs and code
- [ ] Confirmed SDK retry and application retry do not stack unintentionally
- [ ] Set exponential backoff with jitter and explicit max attempt count
- [ ] Routed structured-output and streaming failures to a separate policy
- [ ] Designed user-facing messages and internal log fields independently after final failure

## Answering the Opening Questions

- **Why should API failures not share one retry policy?**
  Authentication, input, rate limit, network, and provider failures have different recovery paths, so one policy hides the real cause and wastes both time and quota.

- **Which failures are retryable, and which should fail fast?**
  Transient network errors and some 429/5xx failures are retry candidates; bad keys, bad model IDs, and invalid request schemas usually need a fix, not repetition.

- **After final failure, how should user messages and internal logs differ?**
  Users need a short actionable message; internal logs need classification, provider response, attempt count, and correlation ID.

<!-- toc:begin -->
## In this series

- [LLM API Production 101 (1/6): Structured output — JSON mode and response schemas](./01-structured-output.md)
- [LLM API Production 101 (2/6): Tool calling — connecting functions to the model](./02-tool-calling.md)
- [LLM API Production 101 (3/6): Streaming in depth — chunk handling and error recovery](./03-streaming-in-depth.md)
- [LLM API Production 101 (4/6): Caching strategies — reducing cost and latency](./04-caching-strategies.md)
- **LLM API Production 101 (5/6): Retry and error handling — making API calls reliable (current)**
- LLM API Production 101 (6/6): Rate limit management — patterns for staying within limits (upcoming)

<!-- toc:end -->

## References

### Official Docs

- [Tenacity documentation](https://tenacity.readthedocs.io/en/latest/)
- [Groq Text Chat docs](https://console.groq.com/docs/text-chat)

### Verification-Friendly References

- [HTTP Semantics — 429 Too Many Requests](https://www.rfc-editor.org/rfc/rfc9110.html#name-429-too-many-requests)

### Related Series

- [Caching strategies — reducing cost and latency](./04-caching-strategies.md)
- [Rate limit management — patterns for staying within limits](./06-rate-limit-management.md)

Tags: LLM, OpenAI, Streaming, Python
