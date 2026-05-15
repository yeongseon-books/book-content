---
series: distributed-systems-101
episode: 10
title: 운영 가능한 분산 시스템 패턴
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
last_reviewed: '2026-05-12'
---

# 운영 가능한 분산 시스템 패턴

이 글은 Distributed Systems 101 시리즈의 마지막 글입니다.

## 이 글에서 다룰 문제

- bulkhead로 장애를 어떻게 격리할 수 있을까요?
- circuit breaker는 연쇄 장애를 어떻게 끊어 줄까요?
- backpressure는 언제 부하를 안전하게 거절해야 할까요?
- timeout, retry, jitter는 어떤 조합으로 다뤄야 할까요?
- metrics, logs, traces를 포함한 관측성이 왜 운영 패턴의 일부일까요?

> 운영 가능한 분산 시스템은 장애가 없는 시스템이 아니라, 장애가 국소적으로 머물고 빠르게 회복되는 시스템입니다.

## 왜 중요한가

지금까지 다룬 복제, 합의, 큐, 트랜잭션은 모두 건축 재료였습니다. 운영 패턴은 그 재료를 장애가 흔한 현실에서도 버티게 하는 도구함입니다. 실제 프로덕션에서 시스템을 오래 살려 두는 힘은 기능보다 운영 경계에서 나옵니다.

> 좋은 운영 패턴은 예상된 장애를 일상적인 사건으로 바꿉니다.

## 한눈에 보는 개념

```mermaid
flowchart LR
    Cl["client"] -->|timeout| LB["load balancer"]
    LB --> S1["service A"]
    LB --> S2["service B (isolated pool)"]
    S1 -->|circuit breaker| Up["upstream"]
    S2 -->|backpressure| Q["queue"]
```

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

<!-- toc:begin -->
- [분산 시스템이란 무엇인가?](./01-what-is-a-distributed-system.md)
- [failure model](./02-failure-model.md)
- [RPC와 message passing](./03-rpc-and-message-passing.md)
- [consistency와 CAP](./04-consistency-and-cap.md)
- [replication](./05-replication.md)
- [consensus와 Raft](./06-consensus-and-raft.md)
- [leader election](./07-leader-election.md)
- [message queue와 event sourcing](./08-message-queue-and-event-sourcing.md)
- [distributed transaction](./09-distributed-transaction.md)
- **운영 가능한 분산 시스템 패턴 (현재 글)**
<!-- toc:end -->

## 참고 자료

- [Release It! — Michael Nygard](https://pragprog.com/titles/mnee2/release-it-second-edition/)
- [Circuit Breaker — Martin Fowler](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Google SRE Book](https://sre.google/sre-book/table-of-contents/)
- [AWS Well-Architected — Reliability Pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html)

Tags: Computer Science, Distributed Systems, Resilience, CircuitBreaker, Backpressure, Observability
