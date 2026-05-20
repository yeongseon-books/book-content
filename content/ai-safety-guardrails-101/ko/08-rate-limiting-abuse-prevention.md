---
title: "AI Safety & Guardrails 101 (8/10): Rate Limiting과 남용 방지"
series: ai-safety-guardrails-101
episode: 8
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- AI Safety
- Rate Limiting
- Abuse Prevention
- Anomaly Detection
last_reviewed: '2026-05-14'
seo_description: 전통적인 API 남용은 "초당 요청 수" 위주였습니다. LLM API는 두 가지 차원이 추가됩니다.
---

# AI Safety & Guardrails 101 (8/10): Rate Limiting과 남용 방지

전통적인 API 보호는 초당 요청 수를 세는 것으로 상당 부분 해결됐습니다. 하지만 LLM API는 그렇지 않습니다. 한 요청이 100토큰일 수도 있고 100,000토큰일 수도 있으며, 스트리밍 응답은 출력 비용을 끝없이 늘릴 수 있습니다. 그래서 남용 방지도 다차원으로 설계해야 합니다.

실무에서는 이 차이가 곧 비용 사고로 이어집니다. RPS는 낮아도 긴 컨텍스트와 장문 출력만으로 비용이 폭증할 수 있고, 사용자당 한도만 두면 IP를 돌리거나 조직 단위 키를 바꿔 우회할 수 있습니다. 결국 요청 수, 입력 토큰, 출력 토큰, 비용을 함께 봐야 합니다.

이 글은 LLM rate limiting을 트래픽 제어가 아니라 비용·남용·가용성 통제 문제로 다룹니다. token bucket, output budget, anomaly detection, 단계적 escalation이 왜 함께 있어야 하는지 설명합니다.

이 글은 AI Safety & Guardrails 101 시리즈의 8번째 글입니다.

이 글에서는 quota 차원, bucket 알고리즘, output cap, 비용 제한, 이상 징후 탐지, 단계적 대응을 정리합니다.

## 먼저 던지는 질문

- LLM rate limiting은 왜 요청 수보다 리소스 소비를 기준으로 봐야 할까요?
- 토큰, 비용, 사용자·키 단위 한도는 각각 어떤 abuse를 막을까요?
- 한도 초과 시 차단과 완화 응답은 어떻게 나눠야 할까요?

## 큰 그림

![Rate limiting과 abuse 방지 흐름](https://yeongseon-books.github.io/book-public-assets/assets/ai-safety-guardrails-101/08/08-01-big-picture.ko.png)

*Rate limiting과 abuse 방지 흐름*

이 그림에서는 요청이 들어올 때 토큰과 비용을 계량하고 bucket을 차감한 뒤 한도 초과 여부에 따라 차단하거나 완화하는 흐름을 봅니다. LLM abuse 방지는 호출 횟수보다 실제 소비 리소스를 기준으로 설계해야 합니다.

> LLM rate limiting의 단위는 요청 한 번이 아니라 토큰, 비용, 도구 호출처럼 실제로 고갈되는 자원입니다.

## 왜 이 글이 중요한가

다차원 rate limiting을 잘 설계하면 비용 폭주와 서비스 남용을 같은 구조 안에서 통제할 수 있습니다. 사용자 경험을 과도하게 해치지 않으면서도, 비정상적인 burst와 자동화 공격을 조기에 감지할 수 있습니다.

반대로 RPS만 제한하면 대형 입력과 긴 출력으로도 충분히 비용이 폭증합니다. 출력 토큰을 끝에서만 계산하면 무한 스트리밍 공격을 막지 못하고, 사용자 기준 한도만 두면 조직 단위 spend나 IP 회전 공격을 놓치게 됩니다.

따라서 LLM rate limiting은 네트워크 보호가 아니라 경제적 안전장치이기도 합니다. 토큰과 달러를 함께 통제해야 실제로 안전합니다.

## 핵심 관점

LLM 시스템에서 중요한 것은 “몇 번 호출했는가”보다 “얼마나 많은 리소스를 썼는가”입니다. 토큰 수, 응답 길이, 모델 단가, 스트리밍 지속 시간이 각각 비용과 장애에 직접 연결됩니다. 이 때문에 rate limit도 요청 횟수가 아니라 자원 예산의 형태를 가져야 합니다.

운영 설계는 보통 hybrid입니다. quota 차원에는 token bucket을 쓰고, 비정상 burst 감시에는 sliding window나 이상 탐지를 붙입니다. 여기에 사용자, IP, API 키라는 세 경계를 겹쳐 공격 우회를 어렵게 만듭니다.

> LLM rate limiting의 본질은 초당 요청 제한이 아닙니다. 토큰과 비용이 예산 밖으로 새지 않게 만드는 리소스 회계 시스템입니다.

## 핵심 개념

### LLM 한도는 네 가지 차원을 동시에 봐야 합니다

- **Token cost**: a single request can be 100 tokens or 100,000 tokens. RPS alone cannot prevent cost runaway.
- **Output token cost**: streaming makes infinite-output attacks possible. Measuring only input misses them.

따라서 최소한 RPS, input tokens per minute, output tokens per minute, dollars per minute를 함께 관리해야 합니다.

### token bucket은 quota 관리의 기본입니다

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

`cost`를 1로 두면 RPS, 입력 토큰 수로 두면 TPM, 비용 단위로 두면 spend limiter가 됩니다. 같은 메커니즘을 여러 자원에 재사용할 수 있다는 점이 장점입니다.

### 사용자·IP·키를 함께 제한해야 우회가 어려워집니다

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

사용자 한도는 개인 남용을 막고, IP 한도는 세션 회전을 막고, 키 한도는 조직 단위 비용 상한을 만듭니다. 세 경계가 겹쳐야 우회 비용이 커집니다.

### 출력 토큰은 스트리밍 중에 과금해야 합니다

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

`max_tokens`만 믿으면 부족합니다. 애플리케이션 레이어에서 별도 cap을 두고 스트리밍 도중 예산을 차감해야 무한 출력 공격을 막을 수 있습니다.

### 비용 캡은 토큰이 아니라 달러 단위로도 필요합니다

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

모델 단가가 다르면 같은 토큰 수라도 비용 영향이 달라집니다. plan tier별로 capacity와 refill 값을 조정하는 편이 일반적입니다.

### 이상 징후 탐지는 평균과 분산을 함께 봐야 합니다

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

평균만 보면 평소 편차가 큰 사용자를 오탐지하기 쉽습니다. z-score를 같이 보면 false positive를 줄일 수 있습니다.

### 이상 징후 이후에는 단계적 escalation이 낫습니다

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

warning → soft throttle → CAPTCHA → suspend 순서가 일반적입니다. 첫 이상 신호에서 즉시 차단하면 정상 burst까지 같이 죽여 사용자 불만이 커집니다.

### 분산 환경에서는 강한 일관성과 지역 성능을 분리합니다

- **Strong consistency**: Redis Cluster or etcd. Accurate but adds latency.
- **Eventual consistency**: per-region local counters with async sync. Faster but allows brief over-spend bursts.

보통 비용 차원은 강한 일관성을, RPS 차원은 지역 로컬 카운터를 더 선호합니다.

## 흔히 헷갈리는 지점

- RPS 한도만 있으면 충분하다고 생각하기 쉽습니다.
- 입력 토큰만 계산하면 비용도 통제된다고 보기 쉽지만, 출력 스트리밍이 더 큰 구멍일 수 있습니다.
- 사용자 기준 한도만 있으면 된다고 생각하기 쉽지만, IP 회전과 조직 키 남용을 놓칩니다.
- anomaly가 보이면 바로 차단하는 것이 최선이라고 여기기 쉽습니다.

## 운영 체크리스트

- [ ] RPS, 입력 토큰, 출력 토큰, 비용 한도를 각각 정의합니다.
- [ ] 사용자·IP·API 키 경계를 동시에 적용합니다.
- [ ] 스트리밍 도중 출력 토큰 예산을 차감하고 별도 output cap을 둡니다.
- [ ] z-score 기반 이상 탐지와 단계적 escalation 정책을 문서화합니다.
- [ ] 비용 차원은 강한 일관성 저장소로, 지역 RPS는 저지연 카운터로 분리합니다.

## 정리

LLM rate limiting은 더 이상 초당 요청 수 제한이 아닙니다. 토큰과 비용, 출력 길이와 이상 행동을 함께 다루는 예산 시스템입니다. 이 구조를 갖춰야 남용과 비용 폭주를 동시에 막을 수 있습니다.

운영에서는 token bucket이 좋은 출발점이지만, anomaly detection과 escalation이 빠지면 거친 차단 시스템이 됩니다. 반대로 이상 탐지만 있고 강제 한도가 없으면 사고를 실시간으로 막지 못합니다.

여기서 기억할 문장은 하나입니다. 요청을 세지 말고, 소비를 계산해야 합니다.

## 처음 질문으로 돌아가기

- **LLM rate limiting은 왜 요청 수보다 리소스 소비를 기준으로 봐야 할까요?**
  - 짧은 요청과 긴 요청의 비용이 크게 다르고, 출력 토큰 폭주나 tool loop가 요청 수만으로는 보이지 않기 때문입니다.
- **토큰, 비용, 사용자·키 단위 한도는 각각 어떤 abuse를 막을까요?**
  - 토큰 한도는 context·출력 폭주, 비용 한도는 예산 남용, 사용자·키 한도는 credential sharing과 automated scraping을 막습니다.
- **한도 초과 시 차단과 완화 응답은 어떻게 나눠야 할까요?**
  - 악성·반복 abuse는 차단하고, 정상 사용자의 일시 초과는 짧은 답변, 대기, 하위 모델, 재시도 안내로 완화할 수 있습니다.
<!-- toc:begin -->
## 시리즈 목차

- [AI Safety & Guardrails 101 (1/10): AI Safety가 왜 중요한가](./01-why-ai-safety-matters.md)
- [AI Safety & Guardrails 101 (2/10): Prompt Injection 방어](./02-prompt-injection-defense.md)
- [AI Safety & Guardrails 101 (3/10): 출력 필터링과 콘텐츠 모더레이션](./03-output-filtering.md)
- [AI Safety & Guardrails 101 (4/10): PII 감지와 마스킹](./04-pii-detection-redaction.md)
- [AI Safety & Guardrails 101 (5/10): Jailbreak 탐지](./05-jailbreak-detection.md)
- [AI Safety & Guardrails 101 (6/10): 독성과 편향 탐지](./06-toxicity-bias-detection.md)
- [AI Safety & Guardrails 101 (7/10): Hallucination Guardrail — Grounding 검증](./07-hallucination-guardrails.md)
- **AI Safety & Guardrails 101 (8/10): Rate Limiting과 남용 방지 (현재 글)**
- AI Safety & Guardrails 101 (9/10): 감사 로깅과 컴플라이언스 (예정)
- AI Safety & Guardrails 101 (10/10): 운영 가드레일 시스템 구축 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Stripe Engineering - Scaling your API with rate limiters](https://stripe.com/blog/rate-limiters)
- [Cloudflare - How we built rate limiting capable of scaling to millions of domains](https://blog.cloudflare.com/counting-things-a-lot-of-different-things/)
- [OpenAI API - Rate limits documentation](https://platform.openai.com/docs/guides/rate-limits)
- [Redis - Rate limiting patterns](https://redis.io/docs/latest/develop/use/patterns/distributed-locks/)

### 관련 시리즈

- [LLM API 프로덕션 101 — 속도 제한 관리](../../llm-api-production-101/ko/06-rate-limit-management.md)
- [운영 가드레일 시스템 구축](./10-production-guardrail-system.md)

Tags: AI Safety, Rate Limiting, Abuse Prevention, Anomaly Detection
