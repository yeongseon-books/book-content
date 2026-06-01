---
episode: 6
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
title: "LLM API Production 101 (6/6): Rate limit management — patterns for staying within limits"
seo_description: Manage LLM API traffic effectively using token-bucket and sliding-window patterns to prevent 429 errors and optimize throughput.
---

# LLM API Production 101 (6/6): Rate limit management — patterns for staying within limits

Any team that runs APIs long enough eventually sees the same scene. A path that usually works fine starts failing at a busy moment, and the logs begin to fill with 429s or rate-limit warnings. LLM APIs are not different. In some ways they are harsher, because each request can be large in token volume and expensive in downstream compute. When traffic spikes, the pain shows up quickly.

This is the last post in the LLM API Production 101 series.

Systems usually fail here in one of two directions. The first is doing nothing and letting every request hit the provider as fast as it arrives. The second is overcorrecting and serializing far more traffic than necessary, which wastes available throughput. Good production behavior sits between those extremes. Send requests aggressively enough to use the allowed budget, but conservatively enough that your own application becomes the first line of control.

This post implements two simple local limiters for that job: a token bucket and a sliding-window limiter. We start with those, then extend to cost-tracking middleware, Redis-based shared counters, and standardized rejection responses.

![Rate limit management: patterns for staying within limits](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/06/06-01-rate-limit-management-patterns-for-stayi.en.png)
*Rate limit management: patterns for staying within limits*
> Rate limit management is not about handling 429s well — it is about the application deciding its own request velocity before the provider has to say no.

## Questions to Keep in Mind

- Is rate limit management something you do after a 429, or before traffic reaches the provider?
- When does a token bucket fit better than a sliding window?
- What should the app still do after receiving a provider 429?

## Why this post matters

Retries and backoff alone cannot solve rate-limit problems. They react only after the provider's allowance has already been exceeded. A local limiter absorbs the excess before it reaches the provider, turning 429 from an unexpected external event into a handled part of internal policy.

This difference is amplified during traffic spikes. When many web requests simultaneously trigger LLM calls with no control layer, the provider becomes the first entity to throttle. With a local limiter, some requests pass immediately and others wait in a controlled manner — the application owns the throttling decision.

Rate limit management is also a predictability problem. How much traffic flows stably, where queuing begins, and what policy governs retries must all be explainable by the application before operations can run smoothly.

## Why the application needs its own limiter

![Local limiter controlling flow before the provider](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/06/06-01-why-the-application-needs-its-own-limite.en.png)

*Local limiter controlling flow before the provider*

A local limiter is useful for three reasons: it absorbs short traffic spikes before they reach the provider, it controls the combined flow from multiple internal code paths under one policy, and it turns rate limits into an application policy instead of a remote surprise.

Imagine twenty web requests arriving at the same moment, all triggering the same LLM call. Without a local control layer, all twenty rush to the provider together. With a limiter, some pass immediately and others wait in a controlled way. That is the difference between external failure and internal control.

## Where a token bucket fits best

![Refill and consume cycle of a token bucket](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/06/06-02-where-a-token-bucket-fits-best.en.png)

*Refill and consume cycle of a token bucket*

A token bucket refills at a steady rate. Each request consumes one or more tokens. That gives you a useful balance: short bursts are allowed up to the bucket size, but the long-term average stays bounded.

For example, if five tokens are added per second and the bucket capacity is ten, a quiet period can accumulate enough room for a burst of ten requests. After that, sustained traffic still settles back to about five per second. That makes token buckets a good fit for user-facing traffic with short spikes.

## Implementing a token bucket

```python
import time

class TokenBucket:
    def __init__(self, capacity: int, refill_rate_per_second: float) -> None:
        self.capacity = capacity
        self.tokens = float(capacity)
        self.refill_rate_per_second = refill_rate_per_second
        self.last_refill = time.monotonic()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.refill_rate_per_second,
        )
        self.last_refill = now

    def allow(self, cost: float = 1.0) -> bool:
        self._refill()
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False
```

Usage is straightforward:

```python
bucket = TokenBucket(capacity=10, refill_rate_per_second=5)

if bucket.allow():
    print("request allowed")
else:
    print("wait before sending")
```

In a first implementation, treating every request as cost `1` is often enough. But LLM workloads have large size variance, so a token-budget variant is frequently needed:

```python
def estimate_token_cost(prompt_tokens: int, reserved_completion_tokens: int) -> int:
    return prompt_tokens + reserved_completion_tokens

bucket = TokenBucket(capacity=40_000, refill_rate_per_second=20_000 / 60)
cost = estimate_token_cost(prompt_tokens=1200, reserved_completion_tokens=800)

if bucket.allow(cost=cost):
    print("token-budget request allowed")
else:
    print("wait for token budget to refill")
```

This variant matters because provider limits often combine RPM and TPM. Treating a small request and a 20,000-token request as the same cost causes the internal policy to drift from the actual limit.

## Where a sliding window fits best

A sliding-window limiter counts how many requests occurred inside the most recent time window. If the policy is "no more than 100 requests in the last 60 seconds," this model maps directly onto that rule. It is less burst-friendly than a token bucket, but easier to reason about when the provider policy is stated in explicit window terms.

```python
import time
from collections import deque

class SlidingWindowLimiter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.events: deque[float] = deque()

    def allow(self) -> bool:
        now = time.monotonic()

        while self.events and now - self.events[0] >= self.window_seconds:
            self.events.popleft()

        if len(self.events) >= self.max_requests:
            return False

        self.events.append(now)
        return True
```

This keeps only recent events inside the active window and rejects requests once the count is full. It maps well when the provider policy is window-based.

## Putting a limiter in front of Groq calls

![Execution path from local gate to provider call](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/06/06-03-putting-a-limiter-in-front-of-groq-calls.en.png)

*Execution path from local gate to provider call*

The critical ordering: the application acquires local permission before talking to the provider.

```python
import os
import time

from groq import Groq

class TokenBucket:
    def __init__(self, capacity: int, refill_rate_per_second: float) -> None:
        self.capacity = capacity
        self.tokens = float(capacity)
        self.refill_rate_per_second = refill_rate_per_second
        self.last_refill = time.monotonic()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.refill_rate_per_second,
        )
        self.last_refill = now

    def wait_for_token(self, cost: float = 1.0) -> None:
        while True:
            self._refill()
            if self.tokens >= cost:
                self.tokens -= cost
                return
            time.sleep(0.1)

bucket = TokenBucket(capacity=10, refill_rate_per_second=5)
client = Groq(api_key=os.environ["GROQ_API_KEY"])

def limited_completion(prompt: str) -> str:
    bucket.wait_for_token()
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return completion.choices[0].message.content

print(limited_completion("Explain the difference between a list and a tuple in Python."))
```

This turns a remote hard limit into a local flow-control decision.

## What to do after a 429 anyway

![Recovery path after a provider 429](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/06/06-04-what-to-do-after-a-429-anyway.en.png)

*Recovery path after a provider 429*

Even with a local limiter, 429s can still arrive. Multiple workers may compete, or the provider may enforce token-based limits that a simple request counter cannot see. The local limiter is the proactive layer; 429 handling is the reactive recovery layer.

A good default rule: honor `Retry-After` if present, otherwise use bounded exponential backoff with jitter, and reacquire local permission before retrying.

```python
import os
import random
import time

from groq import APIStatusError, Groq

class TokenBucket:
    def __init__(self, capacity: int, refill_rate_per_second: float) -> None:
        self.capacity = capacity
        self.tokens = float(capacity)
        self.refill_rate_per_second = refill_rate_per_second
        self.last_refill = time.monotonic()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate_per_second)
        self.last_refill = now

    def wait_for_token(self, cost: float = 1.0) -> None:
        while True:
            self._refill()
            if self.tokens >= cost:
                self.tokens -= cost
                return
            time.sleep(0.1)

bucket = TokenBucket(capacity=10, refill_rate_per_second=5)
client = Groq(api_key=os.environ["GROQ_API_KEY"], max_retries=0)

def retry_after_seconds(exc: APIStatusError) -> float | None:
    value = exc.response.headers.get("retry-after")
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None

def limited_completion_with_429(prompt: str) -> str:
    for attempt in range(3):
        bucket.wait_for_token()
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            return completion.choices[0].message.content
        except APIStatusError as exc:
            if exc.status_code != 429 or attempt == 2:
                raise

            retry_after = retry_after_seconds(exc)
            sleep_seconds = retry_after if retry_after is not None else min(2**attempt, 8) + random.uniform(0, 0.5)
            time.sleep(sleep_seconds)

    raise RuntimeError("unreachable")
```

This logic treats 429 as a reactive recovery layer. The starting point remains the local limiter — proactive and reactive layers must stay separate.

## Choosing token bucket versus sliding window

![Comparison for choosing a limiter](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/06/06-05-choosing-token-bucket-versus-sliding-win.en.png)

*Comparison for choosing a limiter*

Token buckets work well when short bursts are acceptable, when you want smooth average-rate control, and when traffic has user-driven spikes. Sliding windows work well when the provider policy is stated as requests per minute, when you want a direct "how many in the last N seconds" rule, and when operator clarity matters more than burst smoothing.

In many systems, starting with a token bucket is a reasonable default. If the provider policy maps more naturally onto a window-based description, switch to a sliding window or combine both. The important principle is not which model you pick but that the application decides admission first.

## Cost-tracking middleware alongside the limiter

Rate limits are not only about request count. In LLM paths, token cost can hit the bottleneck before request count does. Placing a cost-tracking middleware at the same layer as the limiter lets you explain "why the limit was hit" across both request-count and token-cost dimensions simultaneously.

```python
import time
from fastapi import FastAPI, Request

app = FastAPI()

@app.middleware("http")
async def cost_tracking_middleware(request: Request, call_next):
    started = time.monotonic()
    response = await call_next(request)
    elapsed_ms = int((time.monotonic() - started) * 1000)

    prompt_tokens = int(response.headers.get("x-llm-prompt-tokens", "0"))
    completion_tokens = int(response.headers.get("x-llm-completion-tokens", "0"))
    total_tokens = prompt_tokens + completion_tokens

    # In production, send to structured logger or metrics system
    print(
        {
            "path": request.url.path,
            "status_code": response.status_code,
            "elapsed_ms": elapsed_ms,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
        }
    )
    return response
```

In practice, extract the usage field from the provider response and pass it via headers or request state so this middleware can collect it. The `total_tokens` distribution immediately shows which endpoints consume TPM faster even at the same RPM.

## Redis-based shared limiter for multi-worker deployments

A single-process limiter is enough for learning and small-scale deployments, but as workers increase each process counts separately. The application-wide limit cannot be guaranteed. The minimum scaling path is a Redis time-window counter.

```python
import time

import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

def allow_with_redis_window(key: str, max_requests: int, window_seconds: int) -> bool:
    now = int(time.time())
    bucket = now // window_seconds
    redis_key = f"rl:{key}:{bucket}"

    with r.pipeline() as pipe:
        pipe.incr(redis_key)
        pipe.expire(redis_key, window_seconds + 2)
        current_count, _ = pipe.execute()

    return int(current_count) <= max_requests

print(allow_with_redis_window("llm-chat", max_requests=100, window_seconds=60))
```

This is not the final form of a distributed limiter, but it is far more realistic than local-only counters. The entire service sees one count, and limit adjustments take effect immediately. Further evolution includes Lua-script atomic operations, per-user key separation, and regional sharding.

## Standardizing rejection responses as a contract

When the rate limiter fires, an inconsistent response format makes client handling difficult. Maintaining a standard error payload for limiter rejections lets frontend and backend follow the same rules.

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

def build_rate_limit_error(retry_after_seconds: float) -> dict:
    return {
        "error": {
            "code": "RATE_LIMITED",
            "message": "Too many requests. Please wait and try again.",
            "retry_after_seconds": retry_after_seconds,
        }
    }

@app.get("/api/chat")
def chat_example():
    allowed = False
    if not allowed:
        payload = build_rate_limit_error(retry_after_seconds=1.5)
        raise HTTPException(status_code=429, detail=payload)
    return {"ok": True}
```

Standardizing this way lets clients use `code` and `retry_after_seconds` to unify their retry UI. Operations logs can also aggregate by the same code value, making it easy to distinguish provider 429s from application-level preemptive rejections.

## Common misconceptions

- Retries and backoff alone do not constitute rate limit management — they are purely reactive.
- Treating all requests as equal cost drifts from reality in TPM-heavy environments.
- A local limiter does not guarantee the service-wide limit when multiple processes or servers run independently.
- When `Retry-After` is present, it should take precedence over self-calculated backoff.
- The question is not whether token bucket or sliding window is superior — it is which fits the traffic pattern and policy description better.

## Operational checklist

- [ ] Documented RPM, TPM, and concurrency limits per model in a single table
- [ ] Built the request path so the local limiter grants permission before the provider call
- [ ] Chose token bucket for burst-heavy traffic or sliding window for window-based policies
- [ ] Honored `Retry-After` on 429 responses and reacquired local permission before retrying
- [ ] Documented the need for shared-state design when scaling to multi-worker or multi-server

## Answering the Opening Questions

- **Is rate limit management something you do after a 429, or before traffic reaches the provider?**
  Good rate limit management controls flow before 429s, instead of only reacting after the provider rejects a request.

- **When does a token bucket fit better than a sliding window?**
  Token buckets fit bursty traffic that needs refill-based smoothing; sliding windows fit fair limits over a fixed recent interval.

- **What should the app still do after receiving a provider 429?**
  Read provider signals like Retry-After, apply backoff, queue or reject safely, inform users, and record metrics for the next control decision.

<!-- toc:begin -->
## In this series

- [LLM API Production 101 (1/6): Structured output — JSON mode and response schemas](./01-structured-output.md)
- [LLM API Production 101 (2/6): Tool calling — connecting functions to the model](./02-tool-calling.md)
- [LLM API Production 101 (3/6): Streaming in depth — chunk handling and error recovery](./03-streaming-in-depth.md)
- [LLM API Production 101 (4/6): Caching strategies — reducing cost and latency](./04-caching-strategies.md)
- [LLM API Production 101 (5/6): Retry and error handling — making API calls reliable](./05-retry-and-error-handling.md)
- **LLM API Production 101 (6/6): Rate limit management — patterns for staying within limits (current)**

<!-- toc:end -->

## References

### Official Docs

- [Groq errors guide](https://console.groq.com/docs/errors)
- [Wikipedia: Token bucket](https://en.wikipedia.org/wiki/Token_bucket)
- [Kong Engineering: scalable rate limiting algorithm](https://konghq.com/blog/engineering/how-to-design-a-scalable-rate-limiting-algorithm)

### Verification-Friendly References

- [HTTP Semantics — Retry-After](https://www.rfc-editor.org/rfc/rfc9110.html#field.retry-after)

### Related Series

- [Retry and error handling — making API calls reliable](./05-retry-and-error-handling.md)
- [LLM API Production 101 series](../)

Tags: LLM, OpenAI, Streaming, Python
