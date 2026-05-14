---
title: Rate Limiting and Abuse Prevention
series: ai-safety-guardrails-101
episode: 8
language: en
status: content-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Safety
- Rate Limiting
- Abuse Prevention
- Anomaly Detection
last_reviewed: '2026-05-14'
seo_description: Prevent LLM API abuse and cost overruns by tracking requests, tokens, and spend using hybrid token bucket and anomaly detection algorithms.
---

# Rate Limiting and Abuse Prevention

> AI Safety & Guardrails 101 Series (8/10)

Rate limiting for LLM APIs is not just about requests per second. Token volume, streaming output, and cost all move independently, so abuse control has to watch more than one meter.

This is post 8 in the AI Safety & Guardrails 101 series. It maps out the quota dimensions and burst-detection patterns that make sense for LLM traffic.

---

## Questions this post answers

- Why is LLM rate limiting about more than requests per second?
- How do token bucket and sliding window serve different goals?
- Why should user, IP, and API-key quotas overlap?
- How do output-token and spend caps differ from request limits?
- Why is staged escalation safer than instant suspension?

## Why Rate Limiting Is Different for LLM APIs

Traditional API abuse control is mostly about requests per second. LLM APIs add two dimensions.

- **Token cost**: a single request can be 100 tokens or 100,000 tokens. RPS alone cannot prevent cost runaway.
- **Output token cost**: streaming makes infinite-output attacks possible. Measuring only input misses them.

So an LLM rate limiter must track four dimensions at once: RPS, input tokens per minute, output tokens per minute, and dollars per minute.

## Token Bucket vs Sliding Window

Compare the two basic algorithms.

| Algorithm | Strength | Weakness |
| --- | --- | --- |
| Token bucket | Allows bursts, simple to implement | Long-term average accurate, but stacked short bursts can overrun cost |
| Sliding window | Accurate average, easy to analyze | Expensive in Redis keys, stingy with bursts |

The common LLM pattern is hybrid: token buckets for quota dimensions and sliding windows for burst detection.

```python
import time
import redis

r = redis.Redis()

def token_bucket(key: str, capacity: int, refill_per_sec: float, cost: int) -> bool:
    now = time.time()
    pipe = r.pipeline()
    pipe.hgetall(key)
    state = pipe.execute()[0]
    tokens = float(state.get(b"tokens", capacity))
    last = float(state.get(b"ts", now))
    tokens = min(capacity, tokens + (now - last) * refill_per_sec)
    if tokens < cost:
        r.hset(key, mapping={"tokens": tokens, "ts": now})
        return False
    tokens -= cost
    r.hset(key, mapping={"tokens": tokens, "ts": now})
    r.expire(key, 3600)
    return True
```

`cost` is 1 for RPS, or actual input or output token count for token quotas.

## Per-User, Per-IP, Per-Key Limits

Apply all three boundaries.

```python
def allow_request(user_id: str, ip: str, api_key: str, input_tokens: int) -> tuple[bool, str]:
    if not token_bucket(f"u:{user_id}:rps", capacity=60, refill_per_sec=1, cost=1):
        return False, "user rps"
    if not token_bucket(f"u:{user_id}:tok", capacity=100_000, refill_per_sec=100_000/60, cost=input_tokens):
        return False, "user tokens"
    if not token_bucket(f"ip:{ip}:rps", capacity=120, refill_per_sec=2, cost=1):
        return False, "ip rps"
    if not token_bucket(f"k:{api_key}:tok", capacity=1_000_000, refill_per_sec=1_000_000/60, cost=input_tokens):
        return False, "key tokens"
    return True, ""
```

User limits are the tightest, IP limits stop one user from cycling addresses, and API key limits cap whole-organization spend.

## Output Token Cap

Charge tokens during streaming, not only on completion. Charging at the end leaves infinite-output attacks open.

```python
def stream_with_budget(prompt: str, user_id: str, max_output: int):
    bucket_key = f"u:{user_id}:out"
    spent = 0
    for chunk in llm.stream(prompt, max_tokens=max_output):
        token_count = len(chunk.split())  # use a real tokenizer in production
        if not token_bucket(bucket_key, capacity=200_000, refill_per_sec=200_000/60, cost=token_count):
            yield "[output quota exceeded]"
            return
        spent += token_count
        yield chunk
```

Always set `max_tokens` and add an additional application-side cap; the model can ignore it or a streaming proxy may behave differently.

## Cost Budget Limiter

Cap by dollars, not just tokens. Multiply by per-model pricing and accumulate.

```python
PRICING = {
    "gpt-4o": {"in": 2.50/1_000_000, "out": 10.00/1_000_000},
    "gpt-4o-mini": {"in": 0.15/1_000_000, "out": 0.60/1_000_000},
}

def charge(user_id: str, model: str, in_tok: int, out_tok: int) -> bool:
    p = PRICING[model]
    cost_cents = int((in_tok * p["in"] + out_tok * p["out"]) * 100_000)  # 0.001 cent units
    return token_bucket(f"u:{user_id}:cost", capacity=10_000_000, refill_per_sec=10_000_000/86400, cost=cost_cents)
```

The example caps a user at roughly $10 per day. Vary capacity and refill by plan tier.

## Anomaly Detection

To catch patterns that simple thresholds miss, track per-user mean and standard deviation.

```python
import math
from collections import deque

class AnomalyDetector:
    def __init__(self, window: int = 60):
        self.window = window
        self.history: dict[str, deque] = {}

    def observe(self, user_id: str, rate: float) -> bool:
        h = self.history.setdefault(user_id, deque(maxlen=self.window))
        h.append(rate)
        if len(h) < 10:
            return False
        mean = sum(h) / len(h)
        var = sum((x - mean) ** 2 for x in h) / len(h)
        sd = math.sqrt(var) or 1
        z = (rate - mean) / sd
        return z > 3.0
```

A z-score above 3 represents an event in the lower 0.13 percent of a normal distribution. A user who normally sends 5 requests per minute will trip when they suddenly send 200.

## CAPTCHA and Tiered Escalation

Once you flag an anomaly, prefer tiered escalation over instant blocks; it preserves UX for legitimate bursts.

1. **Warning header**: `X-Rate-Warning: approaching limit`
2. **Soft throttle**: insert artificial latency in the response
3. **CAPTCHA challenge**: required when issuing a new session token
4. **Suspend the API key**: when automated abuse is confirmed
5. **Manual review**: open a ticket if the same user trips repeatedly within 24 hours

```python
def handle_anomaly(user_id: str, severity: int):
    if severity == 1:
        return {"warning": True}
    if severity == 2:
        time.sleep(2)
    if severity == 3:
        return {"require_captcha": True}
    if severity >= 4:
        r.set(f"suspended:{user_id}", "1", ex=3600)
        return {"suspended": True}
```

## Distributed Counter Accuracy

A single Redis node is a single point of failure. With limiters across multiple regions, choose:

- **Strong consistency**: Redis Cluster or etcd. Accurate but adds latency.
- **Eventual consistency**: per-region local counters with async sync. Faster but allows brief over-spend bursts.

LLM APIs care about cost caps, so most teams pick strong consistency for cost dimensions and per-region local for RPS.

## Common Mistakes

1. **Limiting only RPS.** A single request can spend 100K tokens, so cost still runs away. Limit token and dollar dimensions too.
2. **Not measuring output tokens.** Infinite streaming attacks slip through. Charge during the stream.
3. **Setting only user limits.** A user can cycle IPs or one organization can exhaust the quota for everyone. Add IP and key boundaries.
4. **Anomaly detection on the mean alone.** Add standard deviation and z-score to keep false positives down.
5. **Blocking on the first anomaly.** Legitimate bursts get cut off and complaints flood in. Escalate: warn, slow, CAPTCHA, suspend.

## Key Takeaways

- LLM rate limits track four dimensions: RPS, input tokens, output tokens, and cost.
- Hybrid pattern: token bucket for quotas, sliding window for burst monitoring.
- Apply user, IP, and API key boundaries together so attackers cannot trivially cycle out.
- Charge output tokens during the stream and always set `max_tokens` plus an application-side cap.
- Combine z-score anomaly detection with tiered escalation to balance abuse prevention against false positives.

## Operational Checklist

- [ ] Define separate limits for requests, input tokens, output tokens, and spend.
- [ ] Apply quotas at user, IP, and API-key boundaries together.
- [ ] Charge output tokens while the response is still streaming.
- [ ] Use anomaly detection to escalate gradually instead of suspending immediately.
- [ ] Keep cost-critical counters strongly consistent even if regional RPS counters are local.

---

<!-- toc:begin -->
## AI Safety & Guardrails 101 Series

- [Ep1 Why AI Safety Matters](./01-why-ai-safety-matters.md)
- [Ep2 Prompt Injection Defense](./02-prompt-injection-defense.md)
- [Ep3 Output Filtering and Content Moderation](./03-output-filtering.md)
- [Ep4 PII Detection and Redaction](./04-pii-detection-redaction.md)
- [Ep5 Jailbreak Detection](./05-jailbreak-detection.md)
- [Ep6 Toxicity and Bias Detection](./06-toxicity-bias-detection.md)
- [Ep7 Hallucination Guardrails - Grounding Checks](./07-hallucination-guardrails.md)
- **Ep8 Rate Limiting and Abuse Prevention (current)**
- Ep9 Audit Logging and Compliance (upcoming)
- Ep10 Building a Production Guardrail System (upcoming)
<!-- toc:end -->

## References

- [Stripe Engineering - Scaling your API with rate limiters](https://stripe.com/blog/rate-limiters)
- [Cloudflare - How we built rate limiting capable of scaling to millions of domains](https://blog.cloudflare.com/counting-things-a-lot-of-different-things/)
- [OpenAI API - Rate limits documentation](https://platform.openai.com/docs/guides/rate-limits)
- [Redis - Rate limiting patterns](https://redis.io/docs/latest/develop/use/patterns/distributed-locks/)

Tags: AI Safety, Rate Limiting, Abuse Prevention, Anomaly Detection
