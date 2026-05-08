
# Rate Limiting과 남용 방지

> AI Safety & Guardrails 101 시리즈 (8/10)

---
<!-- a-grade-intro:begin -->
## 핵심 질문

Rate Limiting과 남용 방지를 어떻게 설계해야 비용·서비스 모두를 지킬 수 있을까요?

이 글은 그 질문에 답하기 위해 Rate Limiting과 남용 방지의 핵심 결정과 운영 함정을 살펴봅니다.

<!-- a-grade-intro:end -->

## Section 1

## LLM API에서 rate limiting이 다른 이유

전통적인 API 남용은 "초당 요청 수" 위주였습니다. LLM API는 두 가지 차원이 추가됩니다.

- **토큰 비용**: 한 요청이 100 토큰일 수도, 100,000 토큰일 수도 있습니다. RPS 제한만으로는 비용 폭주를 막지 못합니다.
- **출력 토큰 비용**: streaming으로 무한히 출력을 받아내는 공격이 가능합니다. 입력만 측정하면 놓칩니다.

따라서 LLM 시스템의 rate limit은 (RPS, input tokens/min, output tokens/min, $/min) 네 가지 차원을 모두 추적해야 합니다.

## Token Bucket과 Sliding Window

기본 알고리즘 두 가지를 비교합니다.

| 알고리즘 | 장점 | 약점 |
| --- | --- | --- |
| Token bucket | burst 허용, 구현 단순 | 장시간 평균은 정확하나 짧은 burst가 모이면 비용 폭주 |
| Sliding window | 평균 정확, 분석 용이 | Redis 키 비용이 큼, burst에 인색 |

LLM에는 token bucket을 quota dimension으로 두고, sliding window를 burst 감지용으로 병행하는 hybrid가 일반적입니다.

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

`cost`는 RPS의 경우 1, 토큰의 경우 실제 input/output 토큰 수입니다.

## Per-User, Per-IP, Per-Key Limits

세 가지 경계를 모두 둡니다.

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

User 한도는 가장 좁고, IP 한도는 한 사용자가 IP를 돌려가며 우회하지 못하게 합니다. API key 한도는 조직 단위 비용 cap입니다.

## 출력 토큰 cap

응답 streaming 중에도 토큰을 차감해야 합니다. 응답이 끝나는 시점에만 차감하면 무한 출력 공격을 막지 못합니다.

```python
def stream_with_budget(prompt: str, user_id: str, max_output: int):
    bucket_key = f"u:{user_id}:out"
    spent = 0
    for chunk in llm.stream(prompt, max_tokens=max_output):
        token_count = len(chunk.split())  # 실제는 tokenizer 사용
        if not token_bucket(bucket_key, capacity=200_000, refill_per_sec=200_000/60, cost=token_count):
            yield "[output quota exceeded]"
            return
        spent += token_count
        yield chunk
```

`max_tokens` 파라미터를 항상 명시하고, application 단에서도 추가 cap을 둡니다. 모델이 무시하거나 streaming proxy가 다를 수 있습니다.

## 비용 예산 limiter

토큰 단위가 아닌 달러 단위로도 cap을 둡니다. 모델별 단가를 곱해 누적합니다.

```python
PRICING = {
    "gpt-4o": {"in": 2.50/1_000_000, "out": 10.00/1_000_000},
    "gpt-4o-mini": {"in": 0.15/1_000_000, "out": 0.60/1_000_000},
}

def charge(user_id: str, model: str, in_tok: int, out_tok: int) -> bool:
    p = PRICING[model]
    cost_cents = int((in_tok * p["in"] + out_tok * p["out"]) * 100_000)  # 0.001¢ 단위
    return token_bucket(f"u:{user_id}:cost", capacity=10_000_000, refill_per_sec=10_000_000/86400, cost=cost_cents)
```

일일 $10 cap이 위 예시입니다. 사용자의 plan tier에 따라 capacity와 refill을 다르게 설정합니다.

## 이상 징후 탐지

단순 threshold로 걸리지 않는 패턴을 잡으려면 이상 징후 탐지가 필요합니다. 사용자별 평균과 표준편차를 추적합니다.

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

Z-score 3을 넘으면 정상 분포에서 0.13% 미만의 이벤트입니다. 평소 분당 5건을 보내던 사용자가 갑자기 분당 200건을 보내면 잡힙니다.

## CAPTCHA와 단계적 escalation

이상이 감지되면 즉시 차단보다 단계적 escalation이 사용자 경험을 보호합니다.

1. **경고 응답 헤더**: `X-Rate-Warning: approaching limit`
2. **Soft throttle**: 응답에 인공 지연 추가
3. **CAPTCHA 요구**: 새 세션 토큰 발급 시 검증
4. **API key 일시 중지**: 자동화된 abuse 확실 시
5. **수동 검토**: 위 단계가 24시간 내 반복되면 ticket 생성

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

## Distributed counter 정확도

Redis 단일 노드는 단일 장애 지점입니다. 여러 region에서 limiter를 운영하면 두 가지 옵션이 있습니다.

- **Strong consistency**: Redis Cluster나 etcd 사용. 정확하지만 지연 증가.
- **Eventual consistency**: region별 local counter + 비동기 sync. 빠르지만 짧은 burst 허용.

LLM API는 비용 cap이 중요하므로 보통 strong consistency를 택하고, RPS 한도는 region별 local로 둡니다.

## Common Mistakes

1. **RPS만 제한**: 한 요청이 100K 토큰을 쓸 수 있으므로 비용 폭주를 막지 못합니다. 토큰과 비용 차원을 함께 제한합니다.
2. **출력 토큰 미측정**: 무한 streaming 공격이 통과합니다. 응답 도중에도 차감해야 합니다.
3. **User 한도만 두고 IP/key 한도 생략**: 한 사용자가 IP를 돌려 우회하거나 한 조직이 quota를 폭주시킵니다.
4. **이상 징후를 평균만으로 판단**: 표준편차와 z-score를 함께 사용해야 false positive를 줄입니다.
5. **Anomaly 즉시 차단**: 정상 사용자의 burst도 막아 항의가 폭증합니다. 경고 → 지연 → CAPTCHA → 중지 순서로 escalation합니다.

## 핵심 요약

- LLM rate limit은 RPS, input tokens, output tokens, 비용 네 차원을 모두 추적합니다.
- Token bucket으로 quota를, sliding window로 burst를 모니터링하는 hybrid가 표준입니다.
- User, IP, API key 세 경계에 한도를 걸어 우회를 막습니다.
- 출력 토큰은 streaming 도중에도 차감하고, max_tokens를 항상 명시합니다.
- Z-score 기반 이상 탐지와 단계적 escalation으로 false positive와 abuse를 동시에 줄입니다.

---

## 시니어 엔지니어는 이렇게 생각합니다

- **user·IP·token 다층 한도** — 단일 차원으로는 우회됩니다.
- **token bucket이 표준 알고리즘** — burst 허용과 평균 한도를 동시에 표현합니다.
- **비용 기반 한도가 LLM에 적합** — 요청 수보다 token이 비용 신호입니다.
- **이상 행동 패턴을 자동 탐지** — 스크래핑·brute force를 빠르게 차단합니다.
- **한도 초과 시 UX를 명확히** — 오류 메시지가 사용자 신뢰를 결정합니다.

## AI Safety & Guardrails 101 시리즈

- [Ep1 AI 안전이 왜 중요한가](./01-why-ai-safety-matters.md)
- [Ep2 Prompt Injection 방어](./02-prompt-injection-defense.md)
- [Ep3 출력 필터링과 콘텐츠 모더레이션](./03-output-filtering.md)
- [Ep4 PII 탐지와 마스킹](./04-pii-detection-redaction.md)
- [Ep5 Jailbreak 탐지](./05-jailbreak-detection.md)
- [Ep6 Toxicity와 Bias 탐지](./06-toxicity-bias-detection.md)
- [Ep7 Hallucination Guardrail - Grounding 검증](./07-hallucination-guardrails.md)
- **Ep8 Rate Limiting과 남용 방지 (현재 글)**
- Ep9 Audit Logging과 컴플라이언스 (예정)
- Ep10 프로덕션 Guardrail 시스템 구축 (예정)
## 참고 자료

- [Stripe Engineering - Scaling your API with rate limiters](https://stripe.com/blog/rate-limiters)
- [Cloudflare - How we built rate limiting capable of scaling to millions of domains](https://blog.cloudflare.com/counting-things-a-lot-of-different-things/)
- [OpenAI API - Rate limits documentation](https://platform.openai.com/docs/guides/rate-limits)
- [Redis - Rate limiting patterns](https://redis.io/docs/latest/develop/use/patterns/distributed-locks/)

Tags: AI Safety, Rate Limiting, Abuse Prevention, Anomaly Detection

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
