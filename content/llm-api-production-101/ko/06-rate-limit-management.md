---
episode: 6
language: ko
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
  medium: false
  mkdocs: true
  tistory: true
title: "LLM API Production 101 (6/6): 속도 제한 관리 — Rate Limit 대응 패턴"
seo_description: 토큰 버킷과 슬라이딩 윈도우로 429 전에 요청 흐름을 제어하는 rate limit 패턴을 다룹니다.
---

# LLM API Production 101 (6/6): 속도 제한 관리 — Rate Limit 대응 패턴

API를 오래 운영한 팀이라면 언젠가 같은 장면을 봅니다. 평소에는 멀쩡하던 경로가 바쁜 순간 갑자기 실패하기 시작하고, 로그에는 429와 rate-limit 경고가 빠르게 쌓입니다. LLM API는 특히 더 민감할 수 있습니다. 요청 하나가 큰 토큰 볼륨을 갖고, 다운스트림 연산 비용도 크기 때문입니다.

시스템은 보통 두 가지 극단 중 하나로 무너집니다. 하나는 아무 제어 없이 들어오는 요청을 모두 공급자로 밀어 넣는 방식입니다. 다른 하나는 과도하게 보수적으로 직렬화해서 사용 가능한 처리량마저 낭비하는 방식입니다. 좋은 운영은 그 사이에 있습니다. 허용된 예산은 적극적으로 쓰되, 애플리케이션이 먼저 흐름을 조절해야 합니다.

이 글의 관심사는 공급자 정책을 이론적으로 모두 모델링하는 데 있지 않습니다. 더 작은 목표가 있습니다. 애플리케이션 안에 가장 단순한 제어 계층을 두어, 429를 받은 뒤에 사후 반응하기 전에 먼저 요청 속도를 다듬는 것입니다. 이 출발점이 있어야 나중에 공유 카운터, 다중 키 풀링, 사용자별 쿼터 같은 설계로도 자연스럽게 확장할 수 있습니다.

이번 글에서는 토큰 버킷과 슬라이딩 윈도우라는 두 가지 기본 제한기를 구현하고, Groq 호출 앞단에 붙여 요청 흐름을 선제적으로 제어하는 패턴을 정리하겠습니다.

이 글은 LLM API Production 101 시리즈의 마지막 글입니다.

여기서는 429가 오기 전에 요청 흐름을 제어하는 rate limit 관리 패턴을 살펴보겠습니다.

![속도 제한 관리: Rate Limit 대응 패턴](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/06/06-01-rate-limit-management-patterns-for-stayi.ko.png)
*속도 제한 관리: Rate Limit 대응 패턴*
> rate limit 대응의 본질은 429를 잘 처리하는 데 있지 않습니다. 그보다 먼저 애플리케이션이 어떤 속도로 요청을 흘릴지 스스로 결정하는 데 있습니다.

## 먼저 던지는 질문

- rate limit 대응은 429 뒤에 처리하는 일일까요, 429 전에 흐름을 조절하는 일일까요?
- 토큰 버킷과 슬라이딩 윈도우는 각각 어떤 트래픽에 맞을까요?
- provider 429를 받은 뒤에도 애플리케이션은 무엇을 해야 할까요?

## 왜 이 글이 중요한가

재시도와 백오프만으로는 rate limit 문제를 풀 수 없습니다. 그 방식은 이미 공급자 한도를 넘어선 뒤에야 반응합니다. 반면 로컬 제한기는 초과 가능성을 공급자 앞에서 흡수합니다. 즉, 429를 외부의 놀라운 예외가 아니라 내부 정책의 일부로 바꿔 줍니다.

이 차이는 트래픽이 몰리는 순간 더 크게 드러납니다. 같은 시점에 여러 웹 요청이 한꺼번에 LLM 호출을 만들면, 아무 제어가 없을 때는 공급자가 처음으로 조절하는 주체가 됩니다. 하지만 애플리케이션에 제한기가 있으면 일부 요청은 즉시 통과시키고, 일부는 의도적으로 기다리게 만들 수 있습니다.

또한 rate limit 관리는 처리량만의 문제가 아닙니다. 예측 가능성의 문제이기도 합니다. 어느 정도 트래픽까지는 안정적으로 흘리고, 어디서부터 대기열이 생기며, 어떤 정책으로 재시도를 붙일지를 애플리케이션이 설명할 수 있어야 운영이 수월해집니다.

## 핵심 개념

### 왜 애플리케이션 쪽 제한기가 필요한가

![로컬 제한기가 공급자 앞에서 흐름을 조절하는 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/06/06-01-why-the-application-needs-its-own-limite.ko.png)

*로컬 제한기가 공급자 앞에서 흐름을 조절하는 구조*

로컬 제한기가 유용한 이유는 세 가지입니다. 순간적인 트래픽 스파이크를 공급자 앞에서 흡수할 수 있고, 여러 내부 경로에서 합쳐지는 요청 흐름을 한 정책으로 제어할 수 있으며, rate limit을 원격 놀람이 아니라 애플리케이션 정책으로 다룰 수 있습니다.

예를 들어 동시에 스무 개의 웹 요청이 들어와 같은 LLM 호출을 만든다고 가정해 보겠습니다. 아무 제한이 없으면 스무 개가 동시에 공급자로 갑니다. 제한기가 있으면 일부는 즉시 통과하고 나머지는 통제된 방식으로 기다립니다. 이 차이가 바로 외부 실패를 내부 제어로 바꾸는 차이입니다.

### 토큰 버킷은 어디에 잘 맞는가

![토큰 버킷의 채움 소비 반복 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/06/06-02-where-a-token-bucket-fits-best.ko.png)

*토큰 버킷의 채움 소비 반복 구조*

토큰 버킷은 일정 속도로 토큰이 채워지고 요청이 들어올 때 토큰을 소비하는 모델입니다. 덕분에 짧은 burst는 허용하면서 장기 평균은 제한할 수 있습니다. 사용자 입력이 짧게 몰렸다가 다시 잠잠해지는 웹 트래픽에 특히 잘 맞습니다.

예를 들어 초당 5개씩 채워지고 최대 10개까지 저장되는 버킷은, 한가한 시간에 모인 여유분으로 순간적인 10개 burst를 처리할 수 있습니다. 하지만 지속적인 부하는 다시 평균 5개 수준으로 수렴합니다. 이 특성이 user-facing 경로에 실용적입니다.

### 토큰 버킷 구현

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

사용은 단순합니다.

```python
bucket = TokenBucket(capacity=10, refill_rate_per_second=5)

if bucket.allow():
    print("request allowed")
else:
    print("wait before sending")
```

처음에는 모든 요청 비용을 `1`로 보는 것이 충분할 때가 많습니다. 하지만 LLM 경로에서는 요청 크기 차이가 크기 때문에 토큰 예산을 비용으로 삼는 변형도 자주 필요합니다.

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

이 변형이 중요한 이유는 공급자 한도가 RPM과 TPM을 함께 둘 수 있기 때문입니다. 작은 요청과 큰 요청을 같은 비용으로 보면 내부 정책과 실제 한도가 어긋날 수 있습니다.

### 슬라이딩 윈도우는 어디에 잘 맞는가

슬라이딩 윈도우는 최근 시간 창 안에 몇 개의 요청이 있었는지 직접 셉니다. “최근 60초 동안 최대 100개” 같은 정책을 구현하기에 직관적입니다. burst 완화는 토큰 버킷보다 덜 부드럽지만, 운영자에게 설명하기는 더 쉽습니다.

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

이 구현은 최근 창 바깥 이벤트를 제거하고 남은 개수로 허용 여부를 판단합니다. 공급자 정책이 분당 요청 수처럼 창 기반일 때 특히 잘 맞습니다.

### Groq 호출 앞에 제한기 붙이기

![제한기 통과 뒤 외부 호출로 가는 실행 경로](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/06/06-03-putting-a-limiter-in-front-of-groq-calls.ko.png)

*제한기 통과 뒤 외부 호출로 가는 실행 경로*

중요한 것은 제한기가 공급자 호출보다 먼저 실행된다는 점입니다.

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

이 순서가 핵심입니다. 공급자가 거절하기 전에 애플리케이션이 먼저 허가를 냅니다. 즉, 외부의 하드 리밋을 내부의 흐름 제어 정책으로 바꾸는 것입니다.

### 429를 받았을 때도 해야 할 일

![429 응답 뒤 backoff와 재허가가 이어지는 경로](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/06/06-04-what-to-do-after-a-429-anyway.ko.png)

*429 응답 뒤 backoff와 재허가가 이어지는 경로*

로컬 제한기가 있어도 429는 여전히 올 수 있습니다. 여러 프로세스가 경쟁할 수도 있고, 공급자가 토큰 기준으로 더 복잡한 한도를 적용할 수도 있기 때문입니다. 그래서 429는 여전히 재시도 가능한 오류로 다루되, 일반 일시 장애보다 더 신중해야 합니다.

좋은 기본 규칙은 `Retry-After`가 있으면 먼저 존중하고, 없으면 제한된 지수 백오프와 지터를 사용하며, 재시도 전에는 다시 로컬 허가를 받는 것입니다.

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

이 로직은 429를 사후 복구층으로 다룹니다. 하지만 여전히 출발점은 로컬 제한기입니다. proactive layer와 reactive layer가 분리되어야 합니다.

### 토큰 버킷과 슬라이딩 윈도우를 언제 고를까

![제한기 선택 기준이 갈리는 비교 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-api-production-101/06/06-05-choosing-token-bucket-versus-sliding-win.ko.png)

*제한기 선택 기준이 갈리는 비교 구조*

토큰 버킷은 짧은 burst를 허용하고 평균 속도를 부드럽게 제어하고 싶을 때 잘 맞습니다. 사용자 행동에 따라 순간 피크가 있는 트래픽이 대표적입니다. 슬라이딩 윈도우는 “최근 60초에 몇 개”처럼 창 기반 정책을 그대로 반영하고 싶을 때 더 직관적입니다.

많은 시스템에서는 토큰 버킷으로 시작해도 충분합니다. 이후 공급자 정책이 창 기반 설명과 더 잘 맞으면 슬라이딩 윈도우로 옮기거나 둘을 함께 조합할 수 있습니다. 중요한 것은 어떤 모델을 고르느냐보다, 애플리케이션이 먼저 허용 여부를 결정한다는 원칙입니다.

### 비용 추적 미들웨어를 같이 붙여야 하는 이유

rate limit은 요청 수만 제한한다고 끝나지 않습니다. LLM 경로에서는 요청 수보다 토큰 비용이 더 빨리 병목이 되기도 합니다. 그래서 제한기와 같은 위치에 비용 추적 미들웨어를 두면, “왜 제한이 걸렸는지”를 요청 수와 비용 두 축으로 동시에 설명할 수 있습니다.

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

    # 실제 환경에서는 구조화 로거/메트릭 시스템으로 전송
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

실전에서는 provider 응답에서 usage 필드를 추출해 헤더나 request state로 전달한 뒤 이 미들웨어에서 수집하는 방식이 자주 쓰입니다. 이렇게 수집한 `total_tokens` 분포를 보면, 같은 RPM이라도 어떤 엔드포인트가 TPM을 더 빠르게 소모하는지 즉시 드러납니다.

### 다중 워커 환경에서는 Redis 기반 공유 제한기로 전환하기

단일 프로세스 제한기는 학습과 소규모 배포에서는 충분하지만, 워커가 늘어나면 각 프로세스가 따로 카운트를 세게 됩니다. 이 상태에서는 애플리케이션 전체 한도를 보장할 수 없습니다. 최소한의 확장 경로는 Redis에 타임 윈도우 카운터를 두는 것입니다.

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

이 방식은 정교한 분산 제한기의 최종형은 아니지만, 로컬 카운터보다 훨씬 현실적입니다. 전체 서비스 기준으로 요청 수를 한 번에 볼 수 있고, 운영자가 한도 조정을 할 때 효과가 즉시 반영됩니다. 이후에는 Lua 스크립트 기반 원자 연산, 사용자별 키 분리, 지역별 샤딩으로 단계적으로 확장하면 됩니다.

### 요청 거절 응답도 계약으로 통일하기

rate limit이 동작할 때 응답 형식이 들쭉날쭉하면 클라이언트가 처리하기 어려워집니다. 제한기로 거절한 경우에도 표준 오류 payload를 유지하면 프런트엔드와 백엔드가 같은 규칙으로 행동할 수 있습니다.

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

def build_rate_limit_error(retry_after_seconds: float) -> dict:
    return {
        "error": {
            "code": "RATE_LIMITED",
            "message": "요청이 많아 잠시 대기 후 다시 시도해 주세요.",
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

이렇게 표준화하면 클라이언트는 `code`와 `retry_after_seconds`만 보고 재시도 UI를 통일할 수 있습니다. 운영 로그도 같은 코드값으로 집계할 수 있어, 공급자 429와 애플리케이션 선제 거절을 분리해 분석하기 쉬워집니다.

## 흔히 헷갈리는 지점

- 재시도와 백오프만 있으면 rate limit 관리가 된다고 생각하기 쉽지만 그것은 사후 대응입니다.
- 모든 요청 비용을 동일하게 보면 TPM 제약이 큰 환경에서 제어가 어긋날 수 있습니다.
- 로컬 제한기가 있어도 여러 프로세스·여러 서버 환경에서는 상태 공유 문제가 남습니다.
- `Retry-After`가 있으면 자체 백오프보다 우선하는 편이 보통 더 정확합니다.
- 토큰 버킷과 슬라이딩 윈도우 중 무엇이 더 우월한지가 아니라, 트래픽 패턴과 정책 표현에 무엇이 더 맞는지가 중요합니다.

## 운영 체크리스트

- [ ] 모델별 RPM, TPM, 동시성 한도를 한 표로 정리했다
- [ ] 공급자 호출 전에 로컬 제한기가 먼저 허가하도록 경로를 구성했다
- [ ] burst 중심이면 토큰 버킷, 창 기반 정책이면 슬라이딩 윈도우를 우선 검토했다
- [ ] 429 응답에서 `Retry-After`를 우선 처리하고 재허가 후 재시도하게 만들었다
- [ ] 다중 워커·다중 서버 환경으로 갈 때 공유 상태 설계가 필요함을 문서화했다

## 정리

이번 글에서는 토큰 버킷과 슬라이딩 윈도우라는 두 가지 기본 제한기를 구현하고, Groq 호출 앞에 붙여 요청 흐름을 선제적으로 조절하는 방식을 정리했습니다. 핵심은 429를 받은 뒤 사과하는 것이 아니라, 그 전에 애플리케이션이 스스로 어떤 속도로 요청을 보낼지 결정하는 데 있습니다.

또한 429 처리도 여전히 중요합니다. 다만 그것은 proactive control을 대체하는 수단이 아니라, 로컬 제한기를 통과했음에도 외부 정책과 충돌했을 때의 reactive recovery여야 합니다. 이 두 층이 분리되어야 트래픽이 몰릴 때도 동작이 예측 가능합니다.

이 글로 시리즈를 마무리합니다. 구조화 출력은 응답 계약을, 툴 호출은 실행 경계를, 스트리밍은 부분 상태 소비를, 캐시는 반복 비용 절감을, 재시도는 일시 장애 복구를, 속도 제한 관리는 트래픽 제어를 다뤘습니다. 이 여섯 가지가 합쳐지면 LLM API를 데모가 아니라 운영 가능한 시스템 경로로 다루는 기본 토대가 갖춰집니다.

## 처음 질문으로 돌아가기

- **rate limit 대응은 429 뒤에 처리하는 일일까요, 429 전에 흐름을 조절하는 일일까요?**
  좋은 rate limit 관리는 429가 난 뒤 사과하는 것이 아니라, 그 전에 애플리케이션이 요청 속도를 조절하는 일입니다.

- **토큰 버킷과 슬라이딩 윈도우는 각각 어떤 트래픽에 맞을까요?**
  토큰 버킷은 짧은 burst를 허용해야 할 때 맞고, 슬라이딩 윈도우는 일정 구간의 공정한 호출 수 제한이 중요할 때 잘 맞습니다.

- **provider 429를 받은 뒤에도 애플리케이션은 무엇을 해야 할까요?**
  Retry-After 같은 provider 신호를 읽고, backoff와 큐잉, 사용자 안내, 내부 메트릭을 함께 남겨 다음 호출 흐름을 조정해야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM API Production 101 (1/6): 구조화 출력 — JSON 모드와 응답 스키마](./01-structured-output.md)
- [LLM API Production 101 (2/6): 툴 호출 — 함수를 모델에 연결하기](./02-tool-calling.md)
- [LLM API Production 101 (3/6): 스트리밍 심화 — 청크 처리와 오류 복구](./03-streaming-in-depth.md)
- [LLM API Production 101 (4/6): 캐싱 전략 — 비용과 지연 시간 줄이기](./04-caching-strategies.md)
- [LLM API Production 101 (5/6): 재시도와 오류 처리 — 안정적인 API 호출 만들기](./05-retry-and-error-handling.md)
- **LLM API Production 101 (6/6): 속도 제한 관리 — Rate Limit 대응 패턴 (현재 글)**

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Groq errors guide](https://console.groq.com/docs/errors)
- [Wikipedia: Token bucket](https://en.wikipedia.org/wiki/Token_bucket)
- [Kong Engineering: scalable rate limiting algorithm](https://konghq.com/blog/engineering/how-to-design-a-scalable-rate-limiting-algorithm)

### 검증 보조 자료
- [HTTP Semantics — Retry-After](https://www.rfc-editor.org/rfc/rfc9110.html#field.retry-after)

### 관련 시리즈
- [재시도와 오류 처리 — 안정적인 API 호출 만들기](./05-retry-and-error-handling.md)
- [LLM API Production 101 시리즈](../)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-api-production-101/ko/06-rate-limit-management)

Tags: LLM, OpenAI, Streaming, Python
