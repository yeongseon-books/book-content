---
series: distributed-systems-101
episode: 4
title: "Distributed Systems 101 (4/10): 일관성과 CAP"
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
  - Consistency
  - CAP
  - Linearizability
  - Eventual Consistency
seo_description: 일관성 스펙트럼과 CAP, PACELC를 한 번에 읽는 기준을 정리합니다.
last_reviewed: '2026-05-15'
---

# Distributed Systems 101 (4/10): 일관성과 CAP

데이터가 한 군데에만 있을 때는 "최신값을 읽는다"는 말이 별일 아닙니다. 하지만 복제본이 둘 이상이 되는 순간부터는 어느 복제본을 읽는지, 파티션 중 무엇을 포기하는지에 따라 그 문장이 완전히 다른 뜻을 갖게 됩니다.

이 글은 Distributed Systems 101 시리즈의 네 번째 글입니다.

여기서는 일관성 모델을 스펙트럼으로 보고, CAP와 PACELC를 통해 설계 문서와 데이터베이스 문장을 읽는 기준을 만듭니다.


![Distributed Systems 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/distributed-systems-101/04/04-01-concept-at-a-glance.ko.png)
*Distributed Systems 101 4장 흐름 개요*

## 먼저 던지는 질문

- 여기서 말하는 일관성은 정확히 무엇이며 트랜잭션의 C와 어떻게 다를까요?
- linearizable, sequential, causal, eventual은 어떤 스펙트럼을 이룰까요?
- CAP 정리는 무엇을 말하며, 어디서 자주 오해될까요?

## 왜 중요한가

데이터베이스가 강한 일관성을 가진다, eventual consistency에 가깝다 같은 한 줄 설명은 설계 전체를 바꿉니다. 어떤 화면을 만들 수 있는지, 재시도 정책을 어떻게 둘지, 장애 시 어떤 동작을 허용할지가 모두 여기서 갈립니다. 이 언어를 모르면 데이터베이스 문서를 읽을 때 핵심을 놓치게 됩니다.

> 일관성 모델은 데이터가 맺는 사회적 계약입니다.

## 한눈에 보는 개념

왼쪽으로 갈수록 직관적이지만 비싸고, 오른쪽으로 갈수록 싸고 가용성이 높지만 직관에서 멀어집니다.

## 핵심 용어

- **Linearizability**: 시스템 전체가 하나의 시간선 위에서 동작하는 것처럼 보이는 모델입니다.
- **Sequential consistency**: 모든 노드가 같은 순서를 보지만, 실제 시간 순서까지 보장하지는 않는 모델입니다.
- **Causal consistency**: 인과적으로 연결된 연산의 순서만 보존하는 모델입니다.
- **Eventual consistency**: 충분한 시간이 지나면 모든 복제본이 같은 상태로 수렴하는 모델입니다.
- **CAP**: 파티션 중에는 일관성과 가용성을 동시에 끝까지 지킬 수 없다는 정리입니다.

## Before / After

**Before — 데이터베이스가 알아서 정하겠지**

```text
defaults silently chosen -> races and stale reads in production
```

**After — 모델을 명시적으로 선택**

```text
orders/payments -> linearizable, feeds/recommendations -> eventual
```

화면과 데이터셋별로 비용을 다르게 배분할 수 있습니다.

## 실습: 코드로 보는 일관성 모델

### 1단계 — 단일 노드(linearizable의 기준점)

```python
# 1_single.py
log = []
def write(x): log.append(x)
def read(): return log[-1] if log else None
```

단일 노드에서는 모든 읽기가 최신 쓰기를 봅니다. 우리가 직관이라고 부르는 감각의 출발점입니다.

### 2단계 — 비동기 복제본(eventual)

```python
# 2_eventual.py
import threading, time
primary = []
replica = []
def write(x):
    primary.append(x)
    threading.Thread(target=lambda: (time.sleep(0.5), replica.append(x))).start()
def read_primary(): return primary[-1] if primary else None
def read_replica(): return replica[-1] if replica else None
```

방금 쓴 값이 반대편 복제본에서는 0.5초 동안 보이지 않습니다. 이 코드 조각 하나가 eventual consistency의 본질을 보여 줍니다.

### 3단계 — read-your-writes 흉내 내기

```python
# 3_ryw.py
session_writes = {}
def write(uid, x):
    primary.append(x); session_writes[uid] = x
def read(uid):
    if uid in session_writes:
        return session_writes[uid]   # users see their own writes immediately
    return read_replica()
```

약한 모델 위에 더 강한 사용자 경험 보장을 얹는 대표적인 방식입니다.

### 4단계 — 파티션 시뮬레이션(CAP 선택)

```python
# 4_partition.py (pseudocode)
def write(x):
    if not majority_alive():
        # CP: refuse
        raise Exception("no majority")
        # AP: accept locally and merge later
```

두 줄의 차이가 CP와 AP를 갈라놓습니다.

### 5단계 — causal consistency 흉내 내기

```python
# 5_vector.py
clock = {"A":0, "B":0}
def tick(node): clock[node] += 1
def happens_before(a, b):
    return all(a[k] <= b[k] for k in a) and any(a[k] < b[k] for k in a)
```

인과 일관성은 happens-before 관계만 보존하면 됩니다. 서로 독립적인 동시 사건은 어떤 순서로 보여도 괜찮습니다.

## 이 코드에서 먼저 봐야 할 점

- 일관성은 이분법이 아니라 스펙트럼입니다.
- 같은 시스템 안에서도 화면이나 데이터셋마다 다른 모델을 선택할 수 있습니다.
- read-your-writes는 약한 모델에서 사용자 경험을 지키는 핵심 기술입니다.
- 파티션 중 CP와 AP를 고르는 일은 자동이 아니라 정책 결정입니다.

## 자주 하는 실수 5가지

1. **CAP의 C를 ACID의 C와 혼동합니다.** 두 개념은 다릅니다.
2. **시스템 전체를 한 단어로 CP라고 부릅니다.** 같은 시스템 안에서도 호출별 정책이 다를 수 있습니다.
3. **eventual을 곧바로, 금방으로 읽습니다.** 이 보장은 시간 상한을 주지 않습니다.
4. **read-your-writes가 자동이라고 생각합니다.** 직접 구현해야 합니다.
5. **파티션을 무시한 채 강한 일관성을 약속합니다.** 운영에서 곧바로 깨집니다.

## 실무에서는 이렇게 드러납니다

Spanner, etcd, ZooKeeper는 linearizable에 가깝게 동작하는 CP 계열입니다. DynamoDB, Cassandra, Redis Cluster는 기본적으로 eventual에 가까운 AP 성향을 가집니다. 같은 회사 안에서도 결제 시스템은 CP, 추천 캐시는 AP를 선택하는 경우가 흔합니다. PACELC는 파티션이 없는 평상시에도 지연과 일관성 사이의 비용을 보게 해 줍니다. 예를 들어 Cassandra는 `ONE`으로 읽으면 1ms 내로 응답하지만 오래된 값을 반환할 수 있고, `QUORUM`으로 읽으면 5ms 걸리지만 최신 값을 보장합니다. 이 선택을 엔드포인트별로 다르게 하는 것이 성숙한 설계입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 시스템 전체가 아니라 화면과 경로별로 모델을 매핑합니다.
- read-your-writes를 sticky session 같은 방식으로 명시적으로 제공합니다.
- 파티션 정책을 운영 책임의 일부로 다룹니다.
- 강한 일관성의 비용을 SLO로 측정합니다.
- 모델이 이름 붙어 있지 않은 문서는 신뢰하지 않습니다.
- 충돌 해소 전략을 설계 시점에 미리 정하고, 복구 시나리오를 테스트합니다.

## 체크리스트

- [ ] linearizable과 eventual의 차이를 한 줄로 말할 수 있는가?
- [ ] 파티션이 없을 때 CAP를 어떻게 이해해야 하는지 설명할 수 있는가?
- [ ] 시스템의 주요 화면을 일관성 모델에 매핑할 수 있는가?
- [ ] read-your-writes를 어떻게 구현할지 설명할 수 있는가?
- [ ] PACELC의 ELC가 무엇을 뜻하는지 알고 있는가?

## 연습 문제

1. 서비스의 핵심 데이터셋 세 개를 골라 linearizable, causal, eventual 중 어디에 놓을지 정해 보세요.
2. eventual consistency 시스템에서 read-your-writes를 보장하는 설계를 해 보세요.
3. 파티션 중 CP와 AP 중 무엇을 고를지, 그리고 왜 그런지 적어 보세요.

## 정리와 다음 글

일관성 모델은 데이터를 분산한 뒤 가장 중요한 트레이드오프 축입니다. 다음 글에서는 그 선택의 직접적 원인이 되는 복제 방식, 즉 replication과 동기/비동기 복제를 다룹니다.

## CAP 시나리오 심화: 시스템별 파티션 정책

실무에서 CAP를 활용하려면 "우리는 CP다"라는 한 줄이 아니라, API별 파티션 정책 문서가 필요합니다.

### 재고 서비스 파티션 정책

```yaml
# inventory-partition-policy.yaml
service: inventory
consistency_model: eventual (normal) / linearizable (stock deduction)

endpoints:
  GET /items/{id}/stock:
    partition_behavior: allow_stale_read
    max_staleness: 5s
    response_header: X-Data-Freshness
    rationale: >재고 조회는 약간의 오차를 허용해도
      구매 전환에 영향이 작음

  POST /items/{id}/deduct:
    partition_behavior: reject_without_quorum
    http_status: 503
    retry_hint: Retry-After header
    rationale: >재고 차감은 이중 차감 시 금전적 손실이므로
      일관성을 포기할 수 없음

  GET /items/search:
    partition_behavior: serve_from_local_replica
    staleness: unbounded
    rationale: 검색은 가용성이 우선

recovery:
  reconcile: version_vector_merge
  conflict_resolution: last_write_wins_with_audit
  max_reconcile_window: 30s
```

이 문서가 존재하면 파티션이 발생했을 때 "검색은 되는데 재고 차감이 안 되요"라는 보고를 받아도 정상 동작임을 즉시 알 수 있습니다.

### 결제 서비스 파티션 정책

```yaml
service: payment
consistency_model: linearizable

endpoints:
  POST /charges:
    partition_behavior: reject
    idempotency_key: required
    timeout: 5s
    on_timeout: check_idempotency_before_retry

  GET /charges/{id}:
    partition_behavior: reject
    rationale: >결제 상태를 오래된 값으로 보여주면
      이중 결제 위험이 있음

partition_detection:
  method: raft_leader_lease
  lease_duration: 10s
  on_lease_expire: step_down_and_reject_writes
```

결제는 모든 엔드포인트가 CP입니다. 파티션 중에는 아예 동작하지 않는 편이 이중 결제를 막는 것보다 싸기 때문입니다.

---

## PACELC: 파티션이 없을 때도 트레이드오프는 있다

CAP은 파티션 시의 선택만 다룹니다. PACELC는 평상시(Else)에도 지연(Latency)과 일관성(Consistency) 사이의 선택이 있다는 점을 명시합니다.

| 시스템 | P+A 또는 P+C | E+L 또는 E+C |
|---------|-------------|-------------|
| DynamoDB | PA | EL (기본 eventual, 빠른 응답) |
| Cassandra (QUORUM) | PC | EC (쿼럼 일치 시만 확인) |
| Spanner | PC | EC (TrueTime으로 linearizable) |
| MongoDB (majority) | PC | EC |
| Redis Cluster | PA | EL |
| CockroachDB | PC | EC |

DynamoDB를 선택한 팀이 "우리는 eventual이니까 괜찮아"라고 말하는 순간, 그 말의 진정한 의미는 "평상시에도 지연을 우선하고, 파티션 시에도 가용성을 우선한다"입니다. 이것이 적합한지는 데이터의 성격에 달려 있습니다.

---

## 일관성 모델 실습: 복제 지연 측정

실제로 복제 지연을 측정해 보면 eventual이 얼마나 "늘을 수 있는지" 체감할 수 있습니다.

```python
# replication_lag_monitor.py
import time
import redis

primary = redis.Redis(host="primary", port=6379)
replica = redis.Redis(host="replica", port=6380)

def measure_lag(iterations: int = 100) -> dict:
    lags = []
    for i in range(iterations):
        key = f"lag_test_{i}"
        value = str(time.time_ns())

        primary.set(key, value)
        start = time.time()

        # 복제본에서 값이 보일 때까지 폴링
        while True:
            result = replica.get(key)
            if result == value.encode():
                break
            time.sleep(0.001)

        lag_ms = (time.time() - start) * 1000
        lags.append(lag_ms)

    return {
        "p50_ms": sorted(lags)[len(lags) // 2],
        "p95_ms": sorted(lags)[int(len(lags) * 0.95)],
        "p99_ms": sorted(lags)[int(len(lags) * 0.99)],
        "max_ms": max(lags),
    }

# 예시 결과:
# {"p50_ms": 1.2, "p95_ms": 3.8, "p99_ms": 12.4, "max_ms": 45.2}
```

p99가 45ms라는 것은 100번 중 1번은 45ms 동안 오래된 값을 읽을 수 있다는 뜻입니다. 이 수치를 알아야 "재고 조회를 복제본에서 읽어도 될까"라는 질문에 데이터 기반으로 답할 수 있습니다.

---

## 충돌 해소 전략

AP 시스템에서는 파티션 복구 후 충돌이 발생합니다. 대표적인 해소 전략:

| 전략 | 설명 | 적합한 경우 |
|------|------|----------|
| Last Write Wins (LWW) | 타임스탬프 기준 최신 값 선택 | 세션 데이터, 캐시 |
| Version Vector | 동시 수정 감지 후 애플리케이션 해결 | 장바구니, 문서 편집 |
| CRDT | 수학적으로 충돌 불가능한 구조 | 카운터, 집합 연산 |
| Application Merge | 도메인 로직으로 병합 | 주문, 재고 |

```python
# CRDT G-Counter 예시
from collections import defaultdict

class GCounter:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.counts: dict[str, int] = defaultdict(int)

    def increment(self, amount: int = 1):
        self.counts[self.node_id] += amount

    def value(self) -> int:
        return sum(self.counts.values())

    def merge(self, other: "GCounter"):
        for node, count in other.counts.items():
            self.counts[node] = max(self.counts[node], count)

# 사용 예시
counter_a = GCounter("node-A")
counter_b = GCounter("node-B")

counter_a.increment(3)  # node-A에서 3회 증가
counter_b.increment(2)  # node-B에서 2회 증가

# 파티션 복구 후 merge
counter_a.merge(counter_b)
print(counter_a.value())  # 5 — 충돌 없이 정확한 합계
```

G-Counter는 각 노드가 자신의 카운터만 증가시키고, merge 시 max를 취합니다. 수학적으로 충돌이 불가능하므로 AP 시스템에서 안전하게 쓸 수 있습니다.

---

## 운영 대시보드 지표

| 범주 | 지표 | 의미 |
|------|------|------|
| 일관성 | 복제 지연 P99 | eventual의 "얼마나 eventual"인지 수치화 |
| 일관성 | stale read 비율 | 복제본 읽기에서 오래된 값 비율 |
| 가용성 | 쿼럼 도달 실패율 | CP 시스템에서 가용성 손실 측정 |
| 충돌 | 충돌 해소 횟수/시간 | AP 시스템의 복구 비용 |
| 파티션 | 파티션 감지~복구 시간 | 불일치 창의 크기 |

```python
from prometheus_client import Histogram, Counter, Gauge

replication_lag = Histogram(
    "replication_lag_seconds",
    "Replication lag from primary to replica",
    ["replica_id"],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0],
)

stale_reads = Counter(
    "stale_reads_total",
    "Reads that returned stale data",
    ["endpoint"],
)

quorum_failures = Counter(
    "quorum_failures_total",
    "Write requests rejected due to quorum loss",
)

conflict_resolutions = Counter(
    "conflict_resolutions_total",
    "Conflicts resolved after partition recovery",
    ["strategy"],  # lww, version_vector, crdt, app_merge
)
```

복제 지연 P99가 `max_staleness` 설정에 근접하면 경보를 울려야 합니다. 쿼럼 실패가 잦아지면 클러스터 확장이나 네트워크 점검이 필요합니다.

---

## Linearizability의 비용: 쿼럼 읽기/쓰기

Linearizable을 보장하려면 모든 읽기와 쓰기가 쿼럼을 통과해야 합니다. 이것이 성능에 어떤 영향을 주는지 코드로 보겠습니다.

```python
# quorum_rw.py — 쿼럼 읽기/쓰기 시뮬레이션
from dataclasses import dataclass
from typing import Optional
import time

@dataclass
class VersionedValue:
    value: str
    version: int
    timestamp: float

class QuorumStore:
    def __init__(self, nodes: int = 5):
        self.n = nodes
        self.w = nodes // 2 + 1  # write quorum
        self.r = nodes // 2 + 1  # read quorum
        # W + R > N 이므로 linearizable
        self.replicas: list[dict[str, VersionedValue]] = [
            {} for _ in range(nodes)
        ]
        self.version_counter = 0

    def write(self, key: str, value: str) -> bool:
        self.version_counter += 1
        vv = VersionedValue(value, self.version_counter, time.time())

        # W개 복제본에 쓰기 성공해야 확정
        acks = 0
        for i in range(self.n):
            self.replicas[i][key] = vv
            acks += 1
            if acks >= self.w:
                return True
        return False

    def read(self, key: str) -> Optional[str]:
        # R개 복제본에서 읽고 최신 버전 선택
        responses = []
        for i in range(self.n):
            if key in self.replicas[i]:
                responses.append(self.replicas[i][key])
            if len(responses) >= self.r:
                break

        if not responses:
            return None
        # 가장 높은 버전 선택
        latest = max(responses, key=lambda v: v.version)
        return latest.value

# N=5, W=3, R=3 → W+R=6 > 5 → 가장 최신 값을 반드시 읽음
store = QuorumStore(nodes=5)
store.write("balance", "1000")
print(store.read("balance"))  # "1000" — linearizable
```

핵심 공식은 `W + R > N`입니다. 이 조건을 만족하면 읽기 쿼럼과 쓰기 쿼럼이 반드시 겹치므로 최신 값을 한 개 이상의 노드에서 읽을 수 있습니다.

| 설정 | W | R | 특성 |
|------|---|---|------|
| N=3, W=2, R=2 | 2 | 2 | 균형 — 1노드 장애에도 읽기/쓰기 가능 |
| N=5, W=3, R=3 | 3 | 3 | 높은 내결성 — 2노드 장애까지 허용 |
| N=5, W=1, R=5 | 1 | 5 | 빠른 쓰기 / 느린 읽기 |
| N=5, W=5, R=1 | 5 | 1 | 느릴 쓰기 / 빠른 읽기 |

실무에서는 데이터의 성격에 따라 W와 R을 비대칭으로 설정합니다. 읽기가 많은 서비스는 W=N, R=1로 읽기 성능을 극대화하고, 쓰기가 많은 서비스는 W=1, R=N으로 쓰기 성능을 극대화합니다.

---

## 일관성 모델 선택 의사결정 매트릭스

| 데이터 유형 | 대표 예시 | 권장 모델 | 이유 |
|-----------|---------|-----------|------|
| 금전적 잔액 | 계좌 잔고, 재고 | Linearizable | 이중 차감 방지 |
| 사용자 세션 | 로그인 상태 | Linearizable | 사용자 경험 |
| 소셜 피드 | 타임라인 | Causal | 순서만 맞으면 됨 |
| 추천 캐시 | 개인화 결과 | Eventual | 새로고침해도 문제없음 |
| 로그/분석 | 클릭 이벤트 | Eventual | 대량 처리 우선 |
| 설정값 | feature flag | Causal | 변경 순서가 중요 |
| 결제 상태 | 충전/취소 | Linearizable | 이중 결제 방지 |

이 매트릭스를 설계 리뷰에서 사용하면 "이 API는 왜 eventual인가"에 대한 근거를 팀이 공유할 수 있습니다. 모든 데이터를 linearizable로 만들면 성능이 떨어지고, 모두 eventual로 만들면 금전적 안전성이 무너집니다. 데이터의 성격에 맞는 수준을 골라야 합니다.

---

## 실제 파티션 시나리오 워크스루

다음은 실제 파티션이 발생했을 때 시스템이 어떻게 동작하는지 단계별로 보여주는 예시입니다.

```text
[파티션 전]
  DC-A: [node-1, node-2, node-3]  ↔  DC-B: [node-4, node-5]
  모든 노드 정상, leader=node-1

[파티션 발생]
  DC-A: [node-1, node-2, node-3]  ✘  DC-B: [node-4, node-5]
  DC-A: quorum 3/5 → 쓰기 계속 가능 (CP 선택)
  DC-B: quorum 2/5 → 쓰기 불가 → 503 반환 (CP 선택)
         또는 로컬 읽기 허용 + 쓰기 거부 (하이브리드)

[복구]
  네트워크 복원 → DC-B 노드들이 DC-A 리더에 재접속
  → 로그 동기화 → ISR 복귀 → 정상 운영 재개
```

CP 시스템에서 DC-B는 파티션 동안 쓰기를 거부합니다. 이것이 "가용성을 희생한다"의 실제 의미입니다. AP 시스템이었다면 DC-B도 쓰기를 받고, 복구 후 충돌을 해소하는 방식을 택했을 것입니다.

### 파티션 감지와 복구 타이머

```python
# partition_monitor.py
import time
from enum import Enum

class ClusterState(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"  # 일부 노드 불통, 쿼럼 유지
    PARTITIONED = "partitioned"  # 쿼럼 손실

class PartitionMonitor:
    def __init__(self, total_nodes: int, quorum: int):
        self.total = total_nodes
        self.quorum = quorum
        self.reachable: set[str] = set()
        self.last_healthy = time.time()

    def update_reachability(self, reachable_nodes: set[str]):
        self.reachable = reachable_nodes
        if len(self.reachable) >= self.quorum:
            self.last_healthy = time.time()

    @property
    def state(self) -> ClusterState:
        if len(self.reachable) == self.total:
            return ClusterState.HEALTHY
        elif len(self.reachable) >= self.quorum:
            return ClusterState.DEGRADED
        else:
            return ClusterState.PARTITIONED

    @property
    def partition_duration_seconds(self) -> float:
        if self.state == ClusterState.PARTITIONED:
            return time.time() - self.last_healthy
        return 0.0
```

파티션 지속 시간이 길어질수록 복구 후 충돌 처리 비용이 늘어납니다. 이 지표를 모니터링하면 "파티션이 30초 이상 지속되면 운영자에게 알림"같은 정책을 자동화할 수 있습니다.

## 처음 질문으로 돌아가기

- **여기서 말하는 일관성은 정확히 무엇이며 트랜잭션의 C와 어떻게 다를까요?**
  - 여기서의 일관성은 "복제본들이 얼마나 같은 값을 보여주는가"입니다. ACID의 C는 "트랜잭션 전후 불변식이 유지되는가"입니다. 두 개념은 이름만 같고 다루는 문제가 다릅니다.
- **linearizable, sequential, causal, eventual은 어떤 스펙트럼을 이룰까요?**
  - 왼쪽으로 갈수록 강하고 비슸니다. linearizable은 시스템 전체가 하나의 시간선에서 동작하는 것처럼 보이고, eventual은 시간만 충분하면 수렴합니다. causal은 그 사이에서 인과 관계만 보존하는 실용적 절충안입니다.
- **CAP 정리는 무엇을 말하며, 어디서 자주 오해될까요?**
  - CAP은 "파티션 중에는 일관성과 가용성을 동시에 완벽히 지킬 수 없다"는 정리입니다. 가장 흔한 오해는 "3개 중 2개를 골라야 한다"는 해석인데, 실제로는 P는 선택이 아니라 현실이므로 C와 A 사이의 선택입니다. 또 이 선택은 시스템 전체가 아니라 엔드포인트별로 다를 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Distributed Systems 101 (1/10): 분산 시스템이란 무엇인가?](./01-what-is-a-distributed-system.md)
- [Distributed Systems 101 (2/10): 장애 모델](./02-failure-model.md)
- [Distributed Systems 101 (3/10): RPC와 메시지 전달](./03-rpc-and-message-passing.md)
- **일관성과 CAP (현재 글)**
- 복제 (예정)
- 합의와 Raft (예정)
- 리더 선출 (예정)
- 메시지 큐와 이벤트 소싱 (예정)
- 분산 트랜잭션 (예정)
- 운영 가능한 분산 시스템 패턴 (예정)

<!-- toc:end -->

## 참고 자료

- [CAP theorem (Wikipedia)](https://en.wikipedia.org/wiki/CAP_theorem)
- [Consistency model (Wikipedia)](https://en.wikipedia.org/wiki/Consistency_model)
- [PACELC theorem (Wikipedia)](https://en.wikipedia.org/wiki/PACELC_theorem)
- [Designing Data-Intensive Applications — chapter 9](https://dataintensive.net/)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/distributed-systems-101/ko)

Tags: Computer Science, Distributed Systems, Consistency, CAP, Linearizability, Eventual Consistency
