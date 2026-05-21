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

## 먼저 던지는 질문

- bulkhead로 장애를 어떻게 격리할 수 있을까요?
- circuit breaker는 연쇄 장애를 어떻게 끊어 줄까요?
- backpressure는 언제 부하를 안전하게 거절해야 할까요?

## 큰 그림

![Distributed Systems 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/distributed-systems-101/10/10-01-concept-at-a-glance.ko.png)

*Distributed Systems 101 10장 흐름 개요*

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


## 실전 설계 확장: 합의, CAP, 메시지 큐 운영

분산 시스템을 실제로 운영할 때는 "요청을 받았다"보다 "요청이 어느 경계에서 확정되었는가"를 더 먼저 확인해야 합니다. 이유는 단순합니다. 네트워크 지연과 부분 장애가 존재하면 성공/실패 이분법으로 상태를 설명할 수 없고, 노드별 관측 시점이 달라 같은 사건을 다르게 기록할 수 있기 때문입니다. 따라서 설계 문서에는 기능 설명뿐 아니라 합의 규칙, 파티션 시 동작 규칙, 큐 처리 규칙이 함께 들어가야 운영에서 재현 가능한 판단이 가능합니다.

### 합의 알고리즘을 어디에 쓰는가

합의 알고리즘은 이론 주제가 아니라 운영 안전장치입니다. 예를 들어 주문 서비스의 리더 노드가 동시에 두 개 생기면, 같은 주문 번호에 서로 다른 상태가 기록될 수 있습니다. 이때 Raft 같은 리더 기반 합의는 "현재 임기의 과반이 인정한 리더만 쓰기 가능"이라는 제약으로 이중 기록을 막습니다.

```text
노드 5개 구성에서 과반수는 3개입니다.
리더가 쓰기를 확정하려면 최소 3개 노드에 로그가 복제되어야 합니다.
2개 노드만 성공한 쓰기는 클라이언트 성공 응답으로 확정하면 안 됩니다.
```

실무 문서에 반드시 적어야 하는 항목은 다음과 같습니다.

- 리더 선출 타임아웃 범위(예: 150ms~300ms 랜덤)
- 하트비트 간격(예: 50ms)
- 로그 확정 기준(과반 복제 이후 commit)
- 장애 복구 시 재조인 절차(스냅샷/로그 재동기화)

이 네 가지를 수치로 고정하면, 장애 대응 중에 팀원마다 다른 가정을 들고 판단하는 상황을 줄일 수 있습니다.

### CAP을 선언으로 끝내지 않고 시나리오로 적기

"우리 시스템은 AP" 같은 문장은 운영에서 거의 도움이 되지 않습니다. 어떤 API가 파티션 중에도 쓰기를 받는지, 읽기 결과가 얼마나 오래 뒤처질 수 있는지를 함께 정의해야 합니다.

예시로 재고 서비스의 파티션 정책을 문서화하면 아래처럼 표현할 수 있습니다.

```yaml
service: inventory
partition_policy:
  write:
    mode: reject_when_no_quorum
    http_status: 503
  read:
    mode: allow_stale_read
    max_staleness_seconds: 5
recovery_policy:
  reconcile: last_write_wins_with_version_check
  audit_log_required: true
```

위 정책의 의미는 명확합니다. 네트워크가 갈라졌을 때 쓰기를 무조건 받지 않고, 읽기는 최대 5초까지 오래된 값을 허용합니다. 대신 복구 후에는 버전 검증과 감사 로그 기반으로 충돌을 정리합니다. CAP 선택은 이렇게 엔드포인트별 동작과 관측 지표로 내려와야 실제 운영 정책이 됩니다.

### 메시지 큐 설정은 처리량보다 재처리 안전성을 먼저 본다

메시지 큐를 도입하면 비동기로 느슨한 결합을 얻지만, 동시에 중복 처리와 순서 역전이 기본 위험이 됩니다. 큐 설정에서 가장 먼저 다룰 항목은 처리량이 아니라 "실패한 메시지를 어떻게 안전하게 다시 처리할 것인가"입니다.

아래는 RabbitMQ 스타일의 실무 기본 설정 예시입니다.

```yaml
queue:
  name: order.events
  durable: true
  arguments:
    x-dead-letter-exchange: order.dlx
    x-message-ttl: 60000
consumer:
  prefetch_count: 20
  ack_mode: manual
  retry:
    max_attempts: 5
    backoff_ms: 200
idempotency:
  key_source: event_id
  ttl_seconds: 86400
```

핵심은 세 가지입니다.

- `durable: true`로 브로커 재시작 후에도 큐 정의를 유지합니다.
- `manual ack`로 실제 처리 완료 후에만 확인 응답을 보냅니다.
- `event_id` 기반 멱등성 저장소를 두어 중복 전달을 결과 중복으로 이어지지 않게 막습니다.

Kafka를 쓰는 경우도 원칙은 같습니다. 파티션 키를 어떻게 잡아 순서를 보존할지, 커밋 시점을 처리 성공 이후로 둘지, DLQ 토픽을 어떻게 운영할지를 문서로 고정해야 장애 시간에 판단 비용을 줄일 수 있습니다.

### 장애 주입 기반 검증 루프

설계를 문서로만 두면 시간이 지나며 가정이 깨집니다. 그래서 운영 전 검증 루프를 습관화해야 합니다.

1. 리더 노드 강제 종료: 선출 시간과 요청 오류율을 측정합니다.
2. 네트워크 지연 주입: p95/p99 지연과 타임아웃 비율을 기록합니다.
3. 큐 소비자 중단: 적체량 증가 속도와 복구 시간을 측정합니다.
4. 중복 메시지 재주입: 멱등성 키로 결과 중복이 차단되는지 확인합니다.

이 검증을 CI 야간 작업이나 스테이징 런북에 포함하면, 새 기능이 들어와도 합의/CAP/큐 운영 규칙이 계속 살아 있는지 지속적으로 확인할 수 있습니다.

### 운영 대시보드에서 반드시 보는 지표

- 합의 계층: 리더 변경 횟수, 선출 소요 시간, 로그 복제 지연
- 요청 계층: 성공률, 타임아웃률, 재시도 횟수, 멱등성 충돌률
- 큐 계층: consumer lag, DLQ 유입량, 재처리 성공률
- 데이터 계층: 복제 지연, 버전 충돌 건수, 보정 작업 처리량

지표를 계층별로 보면 "느리다"라는 증상을 "리더 불안정 때문에 재시도가 폭증했다"처럼 원인 단위로 분해할 수 있습니다. 분산 시스템 운영 성숙도는 결국 이 분해 능력에서 드러납니다.


## 처음 질문으로 돌아가기

- **bulkhead로 장애를 어떻게 격리할 수 있을까요?**
  - 본문의 기준은 운영 가능한 분산 시스템 패턴를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **circuit breaker는 연쇄 장애를 어떻게 끊어 줄까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **backpressure는 언제 부하를 안전하게 거절해야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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

Tags: Computer Science, Distributed Systems, Resilience, CircuitBreaker, Backpressure, Observability
