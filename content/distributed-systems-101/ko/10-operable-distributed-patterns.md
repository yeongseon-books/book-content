---
series: distributed-systems-101
episode: 10
title: "Distributed Systems 101 (10/10): 운영 가능한 분산 시스템 패턴"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - Distributed Systems
  - Resilience
  - CircuitBreaker
  - Backpressure
  - Observability
seo_description: bulkhead, circuit breaker, backpressure, 관측성 패턴을 묶어 설명합니다.
last_reviewed: '2026-05-15'
---

# Distributed Systems 101 (10/10): 운영 가능한 분산 시스템 패턴

마지막 질문은 장애를 없애는 방법이 아닙니다. 느린 upstream 하나가 전체 장애로 번지지 않게 막고, 운영자가 사용자보다 먼저 이상 신호를 읽게 만드는 방법이 핵심입니다.

이 글은 Distributed Systems 101 시리즈의 마지막 글입니다.

여기서는 분산 시스템 이론을 day-2 운영으로 바꾸는 패턴들, 즉 timeout budget, circuit breaker, load shedding, observability를 하나의 운영 경계로 묶어 봅니다.


![Distributed Systems 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/distributed-systems-101/10/10-01-concept-at-a-glance.ko.png)
*Distributed Systems 101 10장 흐름 개요*

## 먼저 던지는 질문

- bulkhead로 장애를 어떻게 격리할 수 있을까요?
- circuit breaker는 연쇄 장애를 어떻게 끊어 줄까요?
- backpressure는 언제 부하를 안전하게 거절해야 할까요?

## 왜 중요한가

지금까지 다룬 복제, 합의, 큐, 트랜잭션은 모두 건축 재료였습니다. 운영 패턴은 그 재료를 장애가 흔한 현실에서도 버티게 하는 도구함입니다. 실제 프로덕션에서 시스템을 오래 살려 두는 힘은 기능보다 운영 경계에서 나옵니다.

> 좋은 운영 패턴은 예상된 장애를 일상적인 사건으로 바꿉니다.

## 한눈에 보는 개념

호출 경계마다 timeout, breaker, bulkhead, backpressure를 조합해야 한 곳의 실패가 옆 경계로 번지지 않습니다.

## 핵심 용어

- **Bulkhead**: 스레드, 연결 풀 같은 자원을 나눠 한 곳의 폭발이 다른 곳으로 퍼지지 않게 하는 경계입니다.
- **Circuit breaker**: 연속 실패를 감지하면 잠시 호출 자체를 끊는 장치입니다.
- **Backpressure**: 큐 길이 초과나 명시적 거절로 과부하를 밖으로 드러내는 메커니즘입니다.
- **Jitter**: thundering herd를 막기 위해 재시도 간격에 넣는 랜덤 오프셋입니다.
- **Observability**: 메트릭, 로그, 트레이스로 시스템을 바깥에서 이해할 수 있게 하는 신호 체계입니다.

## Before / After

**Before — 무한 재시도와 공유 풀**

```text
one upstream slows down -> retry storm everywhere -> total stall
```

**After — breaker + bulkhead + backpressure**

```text
one upstream slows down -> breaker open -> partial rejection -> other paths healthy
```

운영 패턴의 핵심 약속은 한 곳의 죽음이 다음 곳으로 번지지 않게 만드는 것입니다.

## 실습: 짧은 코드로 보는 운영 패턴

### 1단계 — timeout

```python
# 1_timeout.py
import requests
def call():
    return requests.get("https://api.example.com/x", timeout=2.0)
```

타임아웃 없는 외부 호출은 운영 사고의 가장 흔한 원인 중 하나입니다.

### 2단계 — exponential backoff + jitter

```python
# 2_backoff.py
import time, random
def with_retry(fn, retries=4):
    for i in range(retries):
        try: return fn()
        except Exception:
            time.sleep(min(2**i, 10) + random.random())
    raise
```

jitter가 없으면 모든 클라이언트가 같은 순간 다시 몰려 upstream을 두 번째로 무너뜨립니다.

### 3단계 — circuit breaker

```python
# 3_breaker.py
import time
class Breaker:
    def __init__(self, threshold=5, cool=10):
        self.fails = 0; self.until = 0
        self.threshold, self.cool = threshold, cool
    def call(self, fn):
        if time.time() < self.until:
            raise RuntimeError("breaker open")
        try:
            r = fn(); self.fails = 0; return r
        except Exception:
            self.fails += 1
            if self.fails >= self.threshold:
                self.until = time.time() + self.cool
            raise
```

연속 실패가 임계값을 넘으면 cool-down 동안 호출 자체를 막습니다.

### 4단계 — bulkhead(연결 풀 분리)

```python
# 4_bulkhead.py (pseudocode)
pool_payment = ConnectionPool(size=10)
pool_search  = ConnectionPool(size=10)
# payment overload does not affect the search pool
```

같은 프로세스 안이라도 자원 풀을 나누는 순간 격리 경계가 생깁니다.

### 5단계 — backpressure

```python
# 5_backpressure.py
from collections import deque
q, MAX = deque(), 100
def enqueue(msg):
    if len(q) >= MAX:
        return "rejected"   # rejecting is safer than silence
    q.append(msg); return "ok"
```

큐가 가득 찼다면 거절해야 합니다. 조용히 멎는 시스템보다 빠르게 거절하는 시스템이 훨씬 안전합니다.

## 운영 시나리오: retry storm를 어디서 끊을 것인가

대표적인 day-2 사고는 느린 upstream 하나가 모든 보호 장치를 늦게 깨우는 상황입니다.

1. upstream 지연이 80ms에서 3초로 급등합니다.
2. 타임아웃이 느슨한 클라이언트는 blocked socket을 계속 쌓습니다.
3. 재시도가 시작되며 이미 느린 upstream에 부하를 몇 배로 더 얹습니다.
4. circuit breaker가 임계값을 넘긴 뒤 열리면서 추가 호출을 막습니다.
5. bulkhead는 다른 경로가 같은 자원 고갈에 휘말리지 않게 지킵니다.
6. backpressure는 끝없이 쌓는 대신 새 작업을 거절해 장애를 밖으로 드러냅니다.

여기서 중요한 것은 순서입니다. timeout만 있고 retry budget이 없으면 부하 증폭을 못 막습니다. breaker만 있고 observability가 없으면 이유 없는 거절처럼 보입니다. queue만 있고 backpressure가 없으면 장애를 늦출 뿐 사라지게 하지는 못합니다.

## 이 코드에서 먼저 봐야 할 점

- timeout < retry budget < user-facing latency라는 부등식이 깨지면 운영 전체가 무너집니다.
- breaker는 차단뿐 아니라 자동 회복 경로도 가져야 합니다.
- bulkhead는 코드 패턴이 아니라 자원 경계 설계입니다.
- backpressure는 정중한 거절입니다. 실패를 빠르게 밖으로 드러냅니다.

## 자주 하는 실수 5가지

1. **외부 호출에 타임아웃을 두지 않습니다.** 느린 upstream 하나가 전체를 잡아끕니다.
2. **jitter 없는 재시도를 합니다.** thundering herd가 같은 장애를 두 번 만듭니다.
3. **breaker 없이 끝없이 재시도합니다.** 사용자 대기 시간만 늘어납니다.
4. **모든 의존성을 하나의 공유 풀로 처리합니다.** 한쪽 스파이크가 전부에 번집니다.
5. **관측성 없이 패턴만 붙입니다.** 효과를 재지 못하면 다음 장애를 막을 수 없습니다.

## 실무에서는 이렇게 드러납니다

Hystrix의 역사적 패턴, resilience4j, Envoy와 Istio의 retry 및 circuit breaker, AWS App Mesh, Kubernetes의 HPA와 PDB, Kafka나 SQS 기반의 backpressure까지 본질은 같습니다. SRE 팀은 이런 패턴을 SLO와 연결해 자동 알람과 대응 절차로 바꿉니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 모든 외부 호출에 명시적 타임아웃과 재시도 예산을 둡니다.
- breaker와 bulkhead의 임계값은 부하 테스트 결과로 정합니다.
- 메트릭, 로그, 트레이스 없이 패턴만 도입하지 않습니다.
- 평상시에 chaos test로 장애를 연습합니다.
- 사용자 지연 시간을 SLI로 두고 SLO 위반을 자동으로 페이지합니다.

## 체크리스트

- [ ] 모든 외부 호출에 명시적 타임아웃이 있는가?
- [ ] 재시도에 jitter가 포함되어 있는가?
- [ ] 핵심 의존성마다 breaker가 붙어 있는가?
- [ ] 자원 풀이 도메인별로 분리되어 있는가?
- [ ] 메트릭, 로그, 트레이스가 하나의 trace ID로 연결되는가?

## 연습 문제

1. timeout, retry, breaker를 함께 적용한 단일 호출 의사코드를 작성해 보세요.
2. backpressure를 도입할지 결정할 때 볼 기준 두 가지를 적어 보세요.
3. chaos test로 반복해서 리허설할 장애 시나리오 세 가지를 골라 보세요.

## 정리와 다음 학습

분산 시스템의 거의 모든 도구는 결국 운영 가능성으로 수렴합니다. 이 시리즈를 한 문장으로 묶으면 이렇습니다. 실패는 흔하고, 좋은 시스템은 실패를 평범하게 다룹니다. 다음 학습 주제로는 secure-by-design, observability, SRE 시리즈를 권합니다.


## 실전 설계 확장: 운영 패턴 심화

### Circuit Breaker 상태 머신 구현

기본 breaker 코드(3단계)는 closed와 open 두 상태만 다뤘습니다. 실제 운영에서는 half-open 상태가 있어야 자동 회복이 가능합니다. half-open은 cool-down이 끝난 뒤 제한된 요청만 통과시켜 upstream 회복 여부를 탐침하는 구간입니다.

```python
# circuit_breaker_full.py
import time
from enum import Enum

class State(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, threshold=5, cool_seconds=30, probe_max=3):
        self.state = State.CLOSED
        self.fail_count = 0
        self.threshold = threshold
        self.cool_seconds = cool_seconds
        self.probe_max = probe_max
        self.open_since = 0.0
        self.probe_success = 0

    def call(self, fn):
        if self.state == State.OPEN:
            if time.time() - self.open_since >= self.cool_seconds:
                self.state = State.HALF_OPEN
                self.probe_success = 0
            else:
                raise RuntimeError("circuit open — fast fail")

        try:
            result = fn()
        except Exception as exc:
            self._on_failure()
            raise exc

        self._on_success()
        return result

    def _on_failure(self):
        if self.state == State.HALF_OPEN:
            self.state = State.OPEN
            self.open_since = time.time()
            return
        self.fail_count += 1
        if self.fail_count >= self.threshold:
            self.state = State.OPEN
            self.open_since = time.time()

    def _on_success(self):
        if self.state == State.HALF_OPEN:
            self.probe_success += 1
            if self.probe_success >= self.probe_max:
                self.state = State.CLOSED
                self.fail_count = 0
        else:
            self.fail_count = 0
```

상태 전이를 정리하면 다음과 같습니다.

```text
CLOSED --[fail_count >= threshold]--> OPEN
OPEN   --[cool_seconds elapsed]-----> HALF_OPEN
HALF_OPEN --[probe success >= N]----> CLOSED
HALF_OPEN --[any failure]-----------> OPEN
```

핵심은 half-open에서 probe 요청 수를 제한하는 것입니다. 한꺼번에 모든 트래픽을 보내면 회복 중인 upstream을 다시 무너뜨릴 수 있습니다.

### Bulkhead 패턴: 세마포어 기반 격리

연결 풀 분리 외에 세마포어로 동시 호출 수를 제한하는 방법도 있습니다. 이 방식은 HTTP 클라이언트 하나를 공유하면서도 도메인별 동시성 상한을 독립으로 둘 수 있습니다.

```python
# bulkhead_semaphore.py
import asyncio

class Bulkhead:
    def __init__(self, name: str, max_concurrent: int):
        self.name = name
        self._sem = asyncio.Semaphore(max_concurrent)

    async def execute(self, coro):
        if self._sem.locked():
            raise RuntimeError(f"bulkhead '{self.name}' full — rejecting")
        async with self._sem:
            return await coro

# 사용 예시
payment_bulk = Bulkhead("payment", max_concurrent=10)
search_bulk = Bulkhead("search", max_concurrent=20)
```

payment 서비스에 장애가 나도 search 세마포어에는 영향이 없습니다. 거절된 요청은 즉시 503을 받으므로 스레드가 블로킹되지 않습니다.

### 분산 트레이싱: OpenTelemetry 계측

메트릭은 "무엇이 느린가"를 보여 주고, 트레이스는 "왜 느린가"를 보여 줍니다. OpenTelemetry SDK를 붙이면 서비스 간 호출 경로를 하나의 trace ID로 추적할 수 있습니다.

```python
# tracing_setup.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter

provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("order-service")

def process_order(order_id: str):
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_id)
        with tracer.start_as_current_span("validate_payment"):
            validate(order_id)
        with tracer.start_as_current_span("reserve_inventory"):
            reserve(order_id)
```

콘솔에 출력되는 트레이스 구조는 다음과 같습니다.

```text
Trace ID: 4bf92f3577b34da6a3ce929d0e0e4736
  Span: process_order        [0ms - 145ms]
    Span: validate_payment   [2ms - 89ms]
    Span: reserve_inventory  [90ms - 142ms]
```

validate_payment이 87ms를 차지하고 있다면, 해당 span의 attribute와 status code를 보고 payment 서비스의 p99 지연을 확인하는 식으로 원인을 좁혀 갑니다.

### Rate Limiting: Token Bucket 구현

backpressure가 큐 단위의 거절이라면, rate limiting은 API 경계에서의 거절입니다. Token bucket 알고리즘은 일정 속도로 토큰이 채워지고, 요청마다 토큰 하나를 소비합니다.

```python
# rate_limiter.py
import time

class TokenBucket:
    def __init__(self, rate: float, capacity: int):
        self.rate = rate          # tokens per second
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.monotonic()

    def allow(self) -> bool:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_refill = now
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False

# 초당 100 요청, 버스트 최대 150
limiter = TokenBucket(rate=100, capacity=150)

def handle_request(request):
    if not limiter.allow():
        return {"status": 429, "detail": "rate limit exceeded"}
    return process(request)
```

capacity가 rate보다 큰 이유는 짧은 버스트를 허용하되 지속 과부하는 차단하기 위해서입니다. 분산 환경에서는 Redis 기반 sliding window를 쓰지만, 단일 인스턴스 보호에는 이 구현으로 충분합니다.

### Health Check 패턴: Liveness와 Readiness 분리

Kubernetes 환경에서 두 가지 프로브를 섞어 쓰면 장애 대응이 꼬입니다.

- **Liveness**: 프로세스가 살아 있는가? 실패하면 컨테이너를 재시작합니다.
- **Readiness**: 트래픽을 받을 준비가 되었는가? 실패하면 Service endpoint에서 제거합니다.

```python
# health.py — FastAPI 예시
from fastapi import FastAPI, Response

app = FastAPI()
_ready = False

@app.get("/healthz")
def liveness():
    return {"status": "alive"}

@app.get("/readyz")
def readiness(response: Response):
    if not _ready:
        response.status_code = 503
        return {"status": "not ready", "reason": "warming up"}
    return {"status": "ready"}

@app.on_event("startup")
async def warmup():
    global _ready
    await load_model_or_cache()
    _ready = True
```

liveness에 DB 연결 체크를 넣는 실수가 흔합니다. DB가 잠깐 느려질 때마다 컨테이너가 재시작되면 cascading restart가 발생합니다. liveness는 프로세스 자체의 생존만 확인하고, 외부 의존성 상태는 readiness에서 다뤄야 합니다.

### Graceful Degradation 전략

모든 기능을 동등하게 보호할 수는 없습니다. 장애 시 어떤 기능을 먼저 포기할지 미리 정하는 것이 graceful degradation입니다.

```yaml
# degradation_policy.yaml
tiers:
  - name: critical
    features: [checkout, payment_callback]
    action_on_overload: keep_alive
  - name: important
    features: [product_search, cart_update]
    action_on_overload: serve_cached_response
  - name: nice_to_have
    features: [recommendations, recently_viewed]
    action_on_overload: return_empty_with_200
```

코드에서는 feature flag나 load shedding middleware가 현재 부하 수준에 따라 tier를 순서대로 떨어뜨립니다.

```python
# degradation.py
import psutil

def current_tier_cutoff() -> str:
    cpu = psutil.cpu_percent(interval=0.1)
    if cpu > 90:
        return "critical"       # nice_to_have, important 모두 차단
    elif cpu > 75:
        return "important"      # nice_to_have만 차단
    return "nice_to_have"       # 전부 정상
```

이 정책이 문서에 없으면 장애 시간에 누가 어떤 기능을 끌지 실시간으로 논쟁합니다.

### 운영 런북 템플릿

장애 대응 시간을 줄이는 가장 효과적인 방법은 미리 쓴 런북입니다.

```text
=== Runbook: Circuit Breaker Open Alert ===

1. 증상 확인
   - Grafana: breaker_state{service="payment"} == 2 (open)
   - 최근 5분간 payment upstream 5xx 비율 확인

2. 영향 범위 파악
   - payment 호출하는 서비스 목록: checkout, refund, subscription
   - 사용자 영향: 결제 불가, 구독 갱신 지연

3. 즉시 대응
   - payment upstream 상태 확인 (status page, 내부 채널)
   - 자동 회복 대기: half-open 전이까지 cool_seconds(30s) 확인
   - 수동 개입 필요 시: breaker 강제 reset API 호출
     curl -X POST http://checkout:8080/admin/breaker/payment/reset

4. 에스컬레이션 조건
   - 5분 내 자동 회복 안 됨 → payment 팀 호출
   - 10분 내 미회복 → degradation tier를 critical로 전환

5. 복구 확인
   - breaker_state가 0(closed)로 돌아옴
   - 5xx 비율 정상 범위(< 0.1%) 진입
   - 적체된 요청 재처리 완료 확인
```

### Prometheus/Grafana 메트릭 설계

운영 패턴의 효과를 측정하려면 패턴별 메트릭이 필요합니다.

```yaml
# prometheus_metrics.yaml — 계측 항목 정의
metrics:
  - name: circuit_breaker_state
    type: gauge
    labels: [service, dependency]
    description: "0=closed, 1=half_open, 2=open"

  - name: circuit_breaker_transitions_total
    type: counter
    labels: [service, dependency, from_state, to_state]
    description: "상태 전이 횟수"

  - name: bulkhead_available_permits
    type: gauge
    labels: [service, bulkhead_name]
    description: "남은 동시 호출 슬롯"

  - name: bulkhead_rejected_total
    type: counter
    labels: [service, bulkhead_name]
    description: "bulkhead 포화로 거절된 요청 수"

  - name: rate_limiter_rejected_total
    type: counter
    labels: [service, endpoint]
    description: "rate limit 초과로 거절된 요청 수"

  - name: backpressure_queue_depth
    type: gauge
    labels: [service, queue_name]
    description: "현재 큐 적재량"

  - name: request_duration_seconds
    type: histogram
    labels: [service, method, path, status]
    buckets: [0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
    description: "요청 처리 시간 분포"
```

Grafana 대시보드에서 이 메트릭을 조합하면 다음 질문에 즉시 답할 수 있습니다.

- 지금 어떤 breaker가 열려 있는가?
- bulkhead 거절이 증가하는 서비스는 어디인가?
- rate limit에 걸리는 클라이언트가 특정 IP에 집중되어 있는가?
- 큐 적재량이 증가 추세인가, 안정 상태인가?


운영에서 이 지표를 SLO와 연결하면 "breaker가 열린 시간 / 전체 시간"을 error budget 소진으로 환산할 수 있고, budget 잔여량이 임계치 아래로 떨어지면 자동으로 on-call에 페이지를 보냅니다. 이 접근의 장점은 단순 장애 횟수가 아니라 "사용자에게 노출된 장애 시간"으로 심각성을 판단한다는 점입니다. 동일한 장애라도 circuit breaker가 빠르게 열린 경우와 느리게 열린 경우의 사용자 영향은 크게 다르므로, 열림 시간 기반 지표가 더 정확한 판단을 돕습니다.

Grafana alert rule 예시로 breaker open 상태를 감지하는 PromQL은 다음과 같습니다.

```text
# Breaker가 2분 이상 OPEN 상태이면 critical alert 발생
ALERT CircuitBreakerStuck
  IF circuit_breaker_state == 2
  FOR 2m
  LABELS { severity = "critical" }
  ANNOTATIONS {
    summary = "{{ $labels.service }} -> {{ $labels.dependency }} breaker stuck open",
    runbook = "https://wiki.internal/runbooks/breaker-open"
  }
```

alert에 runbook URL을 포함시키면 on-call 엔지니어가 알림을 받는 즉시 대응 절차로 진입할 수 있습니다. 알림과 런북이 분리되어 있으면 장애 초기 대응 시간이 수 분 늘어납니다.


## 처음 질문으로 돌아가기

- **bulkhead로 장애를 어떻게 격리할 수 있을까요?**
  - 연결 풀이나 세마포어를 도메인별로 분리하면, 한 의존성이 포화되어도 다른 의존성의 동시 호출 슬롯은 그대로 남습니다. 4단계 코드에서 `pool_payment`과 `pool_search`를 나눈 것, 세마포어 기반 Bulkhead에서 `payment_bulk`이 가득 차도 `search_bulk`은 영향받지 않는 것이 이 원리입니다. 격리의 단위는 코드가 아니라 자원 경계입니다.

- **circuit breaker는 연쇄 장애를 어떻게 끊어 줄까요?**
  - 연속 실패가 threshold를 넘으면 OPEN 상태로 전이해 이후 호출을 즉시 실패시킵니다. 이렇게 하면 느린 upstream에 추가 부하를 싣지 않고, 호출자 쪽 스레드도 블로킹되지 않습니다. cool-down 후 HALF_OPEN에서 소수의 probe 요청만 보내 회복을 확인한 뒤 CLOSED로 돌아갑니다. 런북에서 본 것처럼 자동 회복이 안 되면 수동 reset이나 degradation tier 전환으로 에스컬레이션합니다.

- **backpressure는 언제 부하를 안전하게 거절해야 할까요?**
  - 큐 깊이가 MAX를 넘거나, token bucket의 토큰이 바닥났을 때 즉시 거절합니다. 5단계 코드의 `"rejected"` 응답과 rate limiter의 429 응답이 이에 해당합니다. 핵심은 "조용히 느려지는 것"보다 "빠르게 거절하는 것"이 전체 시스템 안정에 유리하다는 판단입니다. degradation 정책과 결합하면 critical tier는 유지하면서 nice_to_have tier만 먼저 거절하는 단계적 shed가 가능합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Distributed Systems 101 (1/10): 분산 시스템이란 무엇인가?](./01-what-is-a-distributed-system.md)
- [Distributed Systems 101 (2/10): 장애 모델](./02-failure-model.md)
- [Distributed Systems 101 (3/10): RPC와 메시지 전달](./03-rpc-and-message-passing.md)
- [Distributed Systems 101 (4/10): 일관성과 CAP](./04-consistency-and-cap.md)
- [Distributed Systems 101 (5/10): 복제](./05-replication.md)
- [Distributed Systems 101 (6/10): 합의와 Raft](./06-consensus-and-raft.md)
- [Distributed Systems 101 (7/10): 리더 선출](./07-leader-election.md)
- [Distributed Systems 101 (8/10): 메시지 큐와 이벤트 소싱](./08-message-queue-and-event-sourcing.md)
- [Distributed Systems 101 (9/10): 분산 트랜잭션](./09-distributed-transaction.md)
- **운영 가능한 분산 시스템 패턴 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [Release It! — Michael Nygard](https://pragprog.com/titles/mnee2/release-it-second-edition/)
- [Circuit Breaker — Martin Fowler](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Google SRE Book](https://sre.google/sre-book/table-of-contents/)
- [AWS Well-Architected — Reliability Pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html)
- [Resilience4j CircuitBreaker guide](https://resilience4j.readme.io/docs/circuitbreaker)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/distributed-systems-101/ko)

Tags: Computer Science, Distributed Systems, Resilience, CircuitBreaker, Backpressure, Observability
