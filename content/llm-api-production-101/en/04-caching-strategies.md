---
episode: 4
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
title: "LLM API Production 101 (4/6): Caching strategies — reducing cost and latency"
seo_description: Reduce LLM API costs and latency by implementing a robust request-hash caching strategy with TTL-based expiration and stable key generation.
---

# LLM API Production 101 (4/6): Caching strategies — reducing cost and latency

Once an LLM feature reaches production traffic, the first thing that often looks expensive is not the model choice by itself. It is repetition. The same question comes in again, the same system prompt is sent again, the same context is serialized again, and the same answer is generated again. At that point, teams often jump straight to prompt trimming or model switching. Sometimes that is necessary. Often, the cheaper fix is much simpler: stop recomputing work you already paid for.

That is what caching means in this context. The idea is familiar from web servers, databases, CDNs, and search systems, but LLM traffic adds a few complications. The cache key cannot be just the visible user question. Temperature matters. The system prompt matters. The model name matters. Structured-output settings matter. If any of those inputs change, a cached answer may no longer represent the same task.

An LLM cache is therefore not just a response-string store. It is a contract that defines which input combinations represent the same work. If the contract is too loose, you get incorrect reuse. If it is too strict, hit rate collapses. The core design challenge is identity definition, not storage technology.

This post builds the smallest useful cache for an LLM API path: an in-memory cache keyed by a request hash, with TTL-based expiration. We start there, then extend to shared caches and semantic matching.

This is the fourth post in the LLM API Production 101 series.

![Caching strategies: reducing cost and latency](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/04/04-01-caching-strategies-reducing-cost-and-lat.en.png)
*Caching strategies: reducing cost and latency*
> An LLM cache is not about storing responses — it is about strictly defining when two requests represent the same work.

## Questions to Keep in Mind

- Why is an LLM cache a request-identity contract rather than just a response store?
- What belongs in a cache key besides the prompt text?
- Which paths should avoid caching even when calls are expensive?

## Why this post matters

Caching is a cost-reduction tool and a correctness boundary at the same time. When you avoid recomputing work that has already been paid for, latency and token spend drop together. But a poorly designed cache key causes something worse than waste: it silently returns stale or incorrect answers for requests that look similar but are not the same task.

In the LLM path, system prompts and generation options are especially critical. Even when a user asks the same question, the summarizer prompt and the classifier prompt are different jobs. Whether temperature is 0 or 0.8 can change what the result means. A cache must therefore be keyed on the full execution contract, not the visible question alone.

Caching also requires thinking about expiration and invalidation from the start. If old answers live forever, cost drops but accuracy and trust degrade. TTL and version fields are the minimum devices that keep a cache honest.

## Why an LLM path needs caching

![Cost flow of repeated uncached requests](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/04/04-01-why-an-llm-path-needs-caching.en.png)

*Cost flow of repeated uncached requests*

Production logs usually show more repetition than people expect. It appears in at least four places:

- FAQ-style chatbots
- internal tools that summarize or rewrite similar text repeatedly
- dashboards where multiple users trigger the same report
- interactive sessions where users re-ask the same question with only tiny variations

Without a cache, the system pays the full latency and token cost every time. That is wasted work when the task is materially the same.

The important part is defining "the same task" correctly. A human may think two prompts look identical while the runtime contract is not. If one request uses a different model, a different system instruction, a different temperature, or a structured-output mode, it is not the same job anymore. Caching starts with that boundary.

## What belongs in the cache key

![Structure of a normalized cache key](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/04/04-02-what-belongs-in-the-cache-key.en.png)

*Structure of a normalized cache key*

The most common mistake is caching only by the visible user prompt.

```python
cache[user_prompt] = response_text
```

That is too loose. These two requests may have the same user text and still be different operations:

- one uses `llama-3.1-8b-instant`, the other uses another model
- one has a summarizer system prompt, the other has a classifier prompt
- one uses `temperature=0`, the other uses `temperature=0.8`
- one expects JSON output, the other expects free-form prose

At minimum, a safe cache key should usually include:

- `model`
- `messages`
- `temperature`
- `response_format`
- when relevant, `tools`, `max_tokens`, and other generation options

The cleanest pattern is to normalize the entire request payload into canonical JSON and hash that string into a fixed-length key. The cache key represents the full request contract, not just the human-readable question.

## Building a request hash

The function below turns a request payload into canonical JSON and then into a SHA-256 hash.

```python
import hashlib
import json
from typing import Any

def build_cache_key(payload: dict[str, Any]) -> str:
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

request_payload = {
    "model": "llama-3.1-8b-instant",
    "messages": [
        {"role": "system", "content": "You are a concise summarizer."},
        {"role": "user", "content": "Summarize the difference between FastAPI and Flask in three sentences."},
    ],
    "temperature": 0,
}

print(build_cache_key(request_payload))
```

`sort_keys=True` prevents dictionary key-order differences from producing different hashes for identical requests. Fixed `separators` eliminate whitespace variation. The result is a compact fixed-length key that still represents the full request contract.

## Why TTL matters

![Lifecycle stages of a cached entry](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/04/04-03-why-ttl-matters.en.png)

*Lifecycle stages of a cached entry*

A hash key alone is not enough. Without TTL, stale responses live forever. A model may change, a prompt policy may change, or the underlying business meaning may shift while the cache keeps serving old output. Memory usage also grows without any bound. TTL makes the cache honest about what it is: a temporary copy, not the source of truth.

For LLM traffic, TTL usually depends on the workload:

- static FAQ paths can use longer TTLs
- internal drafting tools often fit medium TTLs
- real-time summaries need shorter TTLs
- tool-driven answers backed by changing external state may need tiny TTLs or no caching at all

There is no universal correct number. The useful habit is making TTL explicit in code instead of leaving expiration to chance.

## A minimal in-memory TTL cache

Here is a single-process cache that stores the value and its expiration time.

```python
import time
from dataclasses import dataclass
from typing import Any

@dataclass
class CacheEntry:
    value: Any
    expires_at: float

class TTLCache:
    def __init__(self) -> None:
        self._store: dict[str, CacheEntry] = {}

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None

        if time.time() >= entry.expires_at:
            del self._store[key]
            return None

        return entry.value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        self._store[key] = CacheEntry(
            value=value,
            expires_at=time.time() + ttl_seconds,
        )

    def delete(self, key: str) -> None:
        self._store.pop(key, None)
```

This uses lazy eviction: expired entries are removed when they are read. That keeps the implementation small and is enough to explain the core behavior. This cache is local to the current process. If you run multiple Uvicorn or Gunicorn workers, each worker has its own store — this is not a service-wide shared cache.

## Putting the cache in front of Groq calls

![Execution path for cache hit and miss](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/04/04-04-putting-the-cache-in-front-of-groq-calls.en.png)

*Execution path for cache hit and miss*

Now we place the cache directly in front of a completion request.

```python
import hashlib
import json
import os
import time
from dataclasses import dataclass
from typing import Any

from groq import Groq

@dataclass
class CacheEntry:
    value: Any
    expires_at: float

class TTLCache:
    def __init__(self) -> None:
        self._store: dict[str, CacheEntry] = {}

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        if time.time() >= entry.expires_at:
            del self._store[key]
            return None
        return entry.value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        self._store[key] = CacheEntry(value=value, expires_at=time.time() + ttl_seconds)

def build_cache_key(payload: dict[str, Any]) -> str:
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

cache = TTLCache()
client = Groq(api_key=os.environ["GROQ_API_KEY"])

def cached_completion(payload: dict[str, Any], ttl_seconds: int = 300) -> dict[str, Any]:
    key = build_cache_key(payload)
    cached = cache.get(key)
    if cached is not None:
        return {"source": "cache", "content": cached}

    completion = client.chat.completions.create(**payload)
    content = completion.choices[0].message.content
    cache.set(key, content, ttl_seconds=ttl_seconds)
    return {"source": "model", "content": content}

payload = {
    "model": "llama-3.1-8b-instant",
    "messages": [
        {"role": "system", "content": "You are a concise Python tutor."},
        {"role": "user", "content": "Explain Python dataclasses in three sentences."},
    ],
    "temperature": 0,
}

print(cached_completion(payload))
print(cached_completion(payload))
```

The first call goes to the model. The second one hits the cache because the payload is the same. Returning `source` explicitly makes cache-hit behavior observable in logs and metrics.

## When not to cache

![Comparison between cacheable and unsafe paths](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/04/04-05-when-not-to-cache.en.png)

*Comparison between cacheable and unsafe paths*

Not every response is a valid cache target. A few cases deserve extra caution:

- answers that depend on rapidly changing external data
- answers that include user-specific permissions or secrets
- responses containing sensitive personal information
- generation paths where high temperature and variation are the point

The same visible question can produce a genuinely different correct answer a few minutes later. If a response is user-scoped or tenant-scoped, include that scope in the cache key or skip caching entirely.

Invalidation is not just about TTL. When prompt policy, model, output format, or business rules change, bumping the cache version is safer than waiting for entries to age out.

```python
messages = [
    {"role": "system", "content": "You are a concise summarizer."},
    {"role": "user", "content": "Summarize the FastAPI and Flask difference."},
]

payload = {
    "cache_version": "v2",
    "model": "llama-3.1-8b-instant",
    "messages": messages,
    "temperature": 0,
}
```

This pattern is more predictable than relying on natural expiration. New contracts get a new version, and old entries become unreachable immediately.

## Measuring hit rate and staleness together

Attaching a cache is not the end of the work. In production you need to know whether the cache is actually saving cost, whether stale answers are lingering too long, and which paths consistently miss. A minimal metrics layer makes those questions answerable.

```python
import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any

@dataclass
class CacheEntry:
    value: Any
    expires_at: float

class TTLCache:
    def __init__(self) -> None:
        self._store: dict[str, CacheEntry] = {}
        self.metrics = {"hits": 0, "misses": 0, "expired": 0}

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            self.metrics["misses"] += 1
            return None

        if time.time() >= entry.expires_at:
            self.metrics["expired"] += 1
            self.metrics["misses"] += 1
            del self._store[key]
            return None

        self.metrics["hits"] += 1
        return entry.value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        self._store[key] = CacheEntry(value=value, expires_at=time.time() + ttl_seconds)

def build_cache_key(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

cache = TTLCache()
payload = {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": "hi"}]}
key = build_cache_key(payload)

print(cache.get(key))
cache.set(key, "cached-response", ttl_seconds=1)
print(cache.get(key))
time.sleep(1.1)
print(cache.get(key))
print(cache.metrics)
```

Even this minimal counter set enables practical operational reasoning. If hit rate is low but expiration is rare, the key may be too strict. If expiration is frequent but staleness reports still appear, TTL may still be too long. Because caching is both a performance feature and a correctness feature, tracking hits, misses, and expirations together is necessary.

## Scaling to Redis: a shared cache beyond a single process

An in-memory cache is fine for learning the logic, but in real deployments with multiple workers the hit rate fragments. The same request goes to the model once per worker instead of once per service. A shared store like Redis solves that.

```python
import hashlib
import json
from typing import Any

import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

def build_cache_key(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"llm:completion:v1:{digest}"

def get_cached_text(payload: dict[str, Any]) -> str | None:
    key = build_cache_key(payload)
    return r.get(key)

def set_cached_text(payload: dict[str, Any], text: str, ttl_seconds: int) -> None:
    key = build_cache_key(payload)
    r.setex(key, ttl_seconds, text)
```

The practical detail here is the namespace prefix. `llm:completion:v1:` makes it easy to scope bulk operations. When urgent invalidation is needed, bump the version prefix or run a targeted cleanup against the old prefix.

## Semantic caching: reusing answers when wording differs but meaning matches

Exact-key matching is safe but can yield low hit rates when users phrase the same question differently. A semantic cache uses embedding similarity as a secondary lookup layer.

```python
from dataclasses import dataclass

@dataclass
class SemanticEntry:
    query: str
    embedding: list[float]
    answer: str

def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

def find_semantic_hit(
    query_embedding: list[float],
    entries: list[SemanticEntry],
    threshold: float = 0.92,
) -> SemanticEntry | None:
    best: SemanticEntry | None = None
    best_score = 0.0
    for entry in entries:
        score = cosine_similarity(query_embedding, entry.embedding)
        if score > best_score:
            best_score = score
            best = entry

    if best is not None and best_score >= threshold:
        return best
    return None
```

This approach is strong for cost reduction but carries false-positive risk. The safe default lookup order is `exact-key cache -> semantic cache -> model call`. Responses served from the semantic layer should log `cache_source=semantic` and `similarity_score` so that quality regressions are visible.

## Common misconceptions

- Keying only on the user question text is usually too loose — model, system prompt, and generation options all affect output meaning.
- TTL is not a performance knob. It is a correctness device that limits how long a cached answer is trusted.
- An in-memory cache is a single-process example, not a service-wide shared cache.
- Responses that depend on external state or user permissions need scope in the key, or should skip caching entirely.
- Optimizing only for hit rate can mask the larger problem of serving stale answers.

## Operational checklist

- [ ] Included model, messages, temperature, and response format in the cache key
- [ ] Used canonical JSON serialization and SHA-256 for stable request hashing
- [ ] Set TTL per workload type with defaults pinned in code
- [ ] Defined separate cache policy for user-scoped or sensitive responses
- [ ] Supported explicit invalidation via `cache_version` on model or prompt changes
- [ ] Tracked hit rate, miss rate, and expiration count as production metrics

## Answering the Opening Questions

- **Why is an LLM cache a request-identity contract rather than just a response store?**
  A cache only works safely when the application can prove two requests represent the same work. Identity definition must come before storage.

- **What belongs in a cache key besides the prompt text?**
  Model, generation options, system instructions, schema version, and any other value that changes output meaning.

- **Which paths should avoid caching even when calls are expensive?**
  Permission-sensitive, freshness-critical, or safety-sensitive paths where a stale answer is more dangerous than the cost of a fresh call.

<!-- toc:begin -->
## In this series

- [LLM API Production 101 (1/6): Structured output — JSON mode and response schemas](./01-structured-output.md)
- [LLM API Production 101 (2/6): Tool calling — connecting functions to the model](./02-tool-calling.md)
- [LLM API Production 101 (3/6): Streaming in depth — chunk handling and error recovery](./03-streaming-in-depth.md)
- **LLM API Production 101 (4/6): Caching strategies — reducing cost and latency (current)**
- LLM API Production 101 (5/6): Retry and error handling — making API calls reliable (upcoming)
- LLM API Production 101 (6/6): Rate limit management — patterns for staying within limits (upcoming)

<!-- toc:end -->

## References

### Official Docs

- [Groq Text Chat docs](https://console.groq.com/docs/text-chat)
- [Python hashlib documentation](https://docs.python.org/3/library/hashlib.html)

### Verification-Friendly References

- [Python json.dumps documentation](https://docs.python.org/3/library/json.html#json.dumps)

### Related Series

- [Streaming in depth — chunk handling and error recovery](./03-streaming-in-depth.md)
- [Retry and error handling — making API calls reliable](./05-retry-and-error-handling.md)

Tags: LLM, OpenAI, Streaming, Python
