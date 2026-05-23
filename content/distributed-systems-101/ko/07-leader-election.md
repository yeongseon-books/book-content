---
series: distributed-systems-101
episode: 7
title: "Distributed Systems 101 (7/10): 리더 선출"
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
  - LeaderElection
  - Lease
  - Coordination
  - Liveness
seo_description: 안전한 리더 선출을 위한 임대(Lease), 하트비트 작동 원리와 스플릿 브레인 방지를 위한 펜싱 토큰 기법을 상세히 다룹니다.
last_reviewed: '2026-05-15'
---

# Distributed Systems 101 (7/10): 리더 선출

리더 선출에서 가장 위험한 장면은 "누가 이기느냐"가 아닙니다. 죽었다고 믿었던 예전 리더가 늦게 깨어나 다시 쓰기를 시도하는 순간입니다. 이 장면을 막지 못하면 시스템은 아주 짧은 순간에도 두 리더를 허용하게 됩니다.

여기서는 lease와 fencing token을 함께 써서, 리더를 고르는 문제를 넘어 예전 리더의 영향력을 끊는 운영 안전장치로 설명합니다.

![Distributed Systems 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/distributed-systems-101/07/07-01-concept-at-a-glance.ko.png)
*Distributed Systems 101 7장 흐름 개요*

## 먼저 던지는 질문

- 왜 리더 선출이 필요하며 어떤 안전 조건이 필요할까요?
- lease와 heartbeat는 각각 어떤 역할을 할까요?
- fencing token은 왜 이전 리더를 막는 핵심 장치일까요?

## 왜 중요한가

분산 시스템에서 치명적인 버그 상당수는 두 리더가 동시에 존재하는 순간 발생합니다. 두 리더가 같은 자원에 동시에 쓰기 시작하면 데이터는 곧바로 깨집니다. 올바른 리더 선출은 어떤 시점에도 하나의 리더만 권한을 가진다는 약속을 만들어 냅니다.

> 좋은 리더 선출은 리더가 둘인 순간이 없다는 약속입니다.

## 한눈에 보는 개념

여러 후보가 lock service에 lease를 요청하고, 한 후보만 리더가 되어 heartbeat로 lease를 갱신합니다.

## 핵심 용어

- **Leader**: 특정 시점에 쓰기 권한을 가진 노드입니다.
- **Lease**: TTL이 지나면 자동 만료되는 임시 권한입니다.
- **Heartbeat**: lease를 연장하기 위해 주기적으로 보내는 신호입니다.
- **Fencing token**: 이전 리더의 요청을 거부하기 위해 단조 증가하는 ID입니다.
- **Split-brain**: 두 노드가 동시에 자신이 리더라고 믿는 상태입니다.

## 적용 전후 비교
**Before — heartbeat만으로 리더 판단**

```text
an old leader stalled by GC pause comes back and writes to the same resource
```

**After — lease + fencing token**

```text
the old leader's request is rejected by a smaller token; only the new leader passes
```

토큰 비교 한 줄이 split-brain을 차단합니다.

## 실습: 선출과 fencing

### 1단계 — lease 기반 선출(의사코드)

```python
# 1_lease.py
import time
class Lease:
    def __init__(self, ttl): self.ttl, self.expires = ttl, 0
    def acquire(self, now):
        if now >= self.expires:
            self.expires = now + self.ttl
            return True
        return False
```

만료된 lease만 새로 획득할 수 있습니다. TTL 자체가 안전 경계입니다.

### 2단계 — heartbeat로 갱신

```python
# 2_heartbeat.py
def renew(lease, now):
    lease.expires = now + lease.ttl
```

리더는 보통 TTL의 3분의 1 주기로 갱신합니다. 한두 번의 지연을 흡수할 마진이 필요합니다.

### 3단계 — fencing token

```python
# 3_fence.py
counter = 0
def grant_leader():
    global counter
    counter += 1
    return counter   # monotonically increasing token
```

새 리더가 선출될 때마다 토큰은 증가합니다. 자원 서버는 더 작은 토큰의 요청을 거부하면 됩니다.

### 4단계 — 자원 서버의 거부 로직

```python
# 4_resource.py
last_token = 0
def write(token, data):
    global last_token
    if token < last_token:
        return "rejected (stale leader)"
    last_token = token
    return "ok"
```

이 한 줄이 예전 리더의 쓰기를 막아 냅니다.

### 5단계 — split-brain 시나리오

```python
# 5_split.py (pseudocode)
# 기존 leader A: token=5, GC pause 30초
# 그동안 새 leader B: token=6 발급
# A가 깨어나 token=5로 write 시도 -> resource server가 거부
# B의 token=6 write는 성공
```

토큰이 없는 설계였다면 A의 쓰기가 실제로 반영되어 데이터가 망가졌을 것입니다.

## 운영 시나리오: GC pause 뒤에 깨어난 예전 리더

실전에서 자주 보는 사고는 깔끔한 장애보다 "너무 오래 멈췄다가 돌아온 리더"에 가깝습니다.

1. 리더 A가 `ttl=5초` lease와 fencing token `41`을 받습니다.
2. 긴 GC pause나 CPU starvation으로 A가 8초 동안 멈춥니다.
3. lock service는 heartbeat를 받지 못해 lease를 만료시키고 리더 B를 선출합니다.
4. B는 fencing token `42`를 받고 쓰기를 받기 시작합니다.
5. A가 깨어나 token `41`로 자원 서버에 쓰기를 시도합니다.
6. 자원 서버는 `41 < 42`를 보고 A의 요청을 거부합니다.

리더를 고르는 일은 lease 저장소가 맡고, 최종 쓰기 허용 여부는 자원 서버가 판단합니다. 선출 이벤트만 남기고 토큰 검증을 빼면 상황은 보여도 실제 보호는 하지 못합니다.

## 이 코드에서 먼저 봐야 할 점

- lease는 자동 만료되므로 네트워크 파티션을 자연스럽게 다룹니다.
- heartbeat는 TTL보다 충분히 자주 보내야 합니다.
- token의 본질은 단조 증가에 있습니다.
- 거부 판단은 클라이언트가 아니라 자원 서버가 내려야 합니다.

## 자주 하는 실수 5가지

1. **heartbeat만으로 충분하다고 생각합니다.** GC pause와 네트워크 지연이 반영되지 않습니다.
2. **TTL을 너무 짧게 잡습니다.** false failover가 자주 납니다.
3. **token 검증을 자원 서버에 넣지 않습니다.** 이전 리더가 쓰기를 성공시킵니다.
4. **token을 랜덤 값으로 만듭니다.** 비교 가능한 순서가 사라집니다.
5. **split-brain 복구를 수동 절차에 맡깁니다.** 설계가 자동으로 막아야 합니다.

## 실무에서는 이렇게 드러납니다

Kubernetes의 `kube-controller-manager`와 `kube-scheduler`는 etcd lease를 사용해 리더를 선출합니다. ZooKeeper의 ephemeral znode도 본질적으로 같은 패턴입니다. Kafka controller, HDFS NameNode HA, 분산 cron 역시 lease와 fencing의 변형으로 볼 수 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- TTL은 최대 GC pause와 네트워크 RTT를 넉넉히 넘겨 잡습니다.
- 선출 이벤트를 메트릭으로 내보내고, 잦은 선출을 버그 신호로 봅니다.
- fencing token을 자원 서버 API의 첫 번째 인자로 취급합니다.
- 리더 교체 중 진행 중이던 요청이 어떻게 처리되는지 명세에 남깁니다.
- split-brain 시나리오를 테스트로 강제로 재현합니다.

## 체크리스트

- [ ] lease와 heartbeat의 역할을 한 줄로 설명할 수 있는가?
- [ ] fencing token이 왜 단조 증가해야 하는지 말할 수 있는가?
- [ ] split-brain 시나리오를 한 문장으로 적을 수 있는가?
- [ ] TTL을 정하는 기준이 있는가?
- [ ] etcd나 ZooKeeper 위에서 리더 선출을 구현하는 그림이 떠오르는가?

## 연습 문제

1. TTL이 5초인 시스템에서 GC pause가 8초 동안 일어나면 어떤 일이 벌어지는지 분석해 보세요.
2. fencing token 없이도 안전한 리더 선출이 가능한 조건이 무엇인지 한 줄로 적어 보세요.
3. etcd lease 위에 분산 cron을 구현하는 의사코드를 써 보세요.

## 정리와 다음 글

리더 선출은 lease와 fencing을 이용해 한 시점에 한 리더라는 약속을 유지하는 작업입니다. 다음 글에서는 리더 없이도 작업을 분배하고 시간을 축으로 설계하는 도구, 메시지 큐와 이벤트 소싱을 살펴봅니다.

## 실전 설계 확장: 리더 선출 패턴과 운영 안전장치

앞에서 lease, heartbeat, fencing token의 기본 동작을 확인했다면, 이제는 실제 시스템에서 어떤 선출 패턴을 고르고 어떻게 운영 안정성을 붙일지 결정해야 합니다. 리더 선출은 알고리즘 자체보다 "오래 멈췄던 예전 리더가 복귀했을 때도 안전한가"라는 질문으로 평가해야 합니다.

### Bully 알고리즘과 Ring 알고리즘 비교

리더 선출 입문에서 자주 등장하는 두 고전 패턴은 Bully와 Ring입니다. 둘 다 "리더가 사라지면 새 리더를 고른다"는 목적은 같지만, 통신 형태와 장애 모델 가정이 다릅니다.

| 항목 | Bully 알고리즘 | Ring 알고리즘 |
| --- | --- | --- |
| 기본 가정 | 각 노드는 고유 ID를 알고 있고, 더 큰 ID가 우선합니다. | 노드가 논리적 링 순서로 연결되어 있습니다. |
| 선출 방식 | 장애를 감지한 노드가 자신보다 큰 ID에게 선출 메시지를 보냅니다. | 선출 메시지를 링으로 돌리며 가장 큰 ID를 수집합니다. |
| 메시지 복잡도 | 최악의 경우 O(n^2)입니다. | 보통 O(n)~O(2n)입니다. |
| 장점 | 구현이 단순하고 수렴이 빠른 편입니다. | 트래픽 패턴이 예측 가능하고 분산됩니다. |
| 단점 | 높은 ID 노드에 부하가 집중되기 쉽습니다. | 링 단절 구간이 생기면 추가 복구 절차가 필요합니다. |
| 실무 적합성 | 소규모 고정 멤버십에서 이해용으로 유용합니다. | 토폴로지가 안정적인 환경에서 학습용으로 좋습니다. |

실무에서는 위 알고리즘을 그대로 쓰기보다, membership과 failure detector를 별도로 두고 lease 기반 선출로 단순화하는 경우가 많습니다. 이유는 명확합니다. Bully/Ring은 "누가 리더인지"는 정하지만 "예전 리더를 어떻게 막을지"는 직접 해결해야 하기 때문입니다.

### Lease 기반 리더 선출 구현 뼈대

아래 예시는 lock service를 단순화한 Python 코드입니다. 핵심은 세 가지입니다. `owner_id`로 현재 리더를 기록하고, `expires_at`으로 권한 유효 시간을 관리하며, 선출 성공 시마다 fencing token을 증가시킵니다.

```python
# lease_election.py
from dataclasses import dataclass
from time import monotonic

@dataclass
class LeaseState:
    owner_id: str | None = None
    expires_at: float = 0.0
    token: int = 0

class LeaseElection:
    def __init__(self, ttl_seconds: float):
        self.ttl_seconds = ttl_seconds
        self.state = LeaseState()

    def try_acquire(self, candidate_id: str) -> tuple[bool, int]:
        now = monotonic()
        if now >= self.state.expires_at:
            self.state.owner_id = candidate_id
            self.state.expires_at = now + self.ttl_seconds
            self.state.token += 1
            return True, self.state.token

        if self.state.owner_id == candidate_id:
            self.state.expires_at = now + self.ttl_seconds
            return True, self.state.token

        return False, self.state.token

    def heartbeat(self, candidate_id: str) -> bool:
        now = monotonic()
        if candidate_id != self.state.owner_id:
            return False
        if now >= self.state.expires_at:
            return False
        self.state.expires_at = now + self.ttl_seconds
        return True
```

이 구조의 중요한 점은 heartbeat가 "권한 연장"이지 "권한 획득"이 아니라는 점입니다. 권한 획득은 오직 만료 경계에서만 허용해야 서로 다른 두 노드가 동시에 성공하는 경로를 줄일 수 있습니다.

### ZooKeeper ephemeral znode 패턴

ZooKeeper 계열에서는 보통 `/election` 아래에 ephemeral sequential znode를 생성하고, 가장 작은 시퀀스를 가진 노드를 리더로 봅니다. 세션이 끊기면 ephemeral 노드가 자동 삭제되므로 lease 만료와 비슷한 효과를 얻습니다.

```text
/election
  /candidate-0000000012   <- follower
  /candidate-0000000013   <- follower
  /candidate-0000000014   <- leader (smallest sequence)
```

운영 포인트는 "모든 후보를 watch"하지 않는 것입니다. 각 후보는 자기 바로 앞 노드만 watch하는 패턴을 써야 thundering herd를 줄일 수 있습니다.

1. 후보 노드가 `EPHEMERAL_SEQUENTIAL`로 참가합니다.
2. 자신보다 작은 번호 중 가장 큰 predecessor를 찾습니다.
3. predecessor 삭제 이벤트를 watch합니다.
4. 이벤트가 오면 다시 목록을 확인하고, 자신이 최소 번호면 리더가 됩니다.

이 방식은 리더 교체 시 전체 후보가 동시에 깨어나는 폭주를 완화하고, 선출 트래픽을 선형 수준으로 제한하는 데 효과적입니다.

### Fencing token으로 split-brain 차단하기

split-brain은 "선출 계층"과 "자원 접근 계층"이 분리될 때 발생합니다. 선출에서 새 리더가 정해졌더라도, 예전 리더가 늦게 도착한 쓰기를 자원 서버가 받아주면 보호가 무너집니다. 따라서 자원 서버는 마지막으로 수락한 토큰보다 작은 요청을 반드시 거부해야 합니다.

```python
# fenced_resource.py
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI()
last_token = 0
state: dict[str, str] = {}

class WriteRequest(BaseModel):
    key: str
    value: str

@app.post("/write")
def write(req: WriteRequest, x_fencing_token: int = Header(...)):
    global last_token
    if x_fencing_token < last_token:
        raise HTTPException(status_code=409, detail="stale leader token")
    last_token = x_fencing_token
    state[req.key] = req.value
    return {"status": "ok", "last_token": last_token}
```

여기서 비교 연산자는 시스템 요구사항에 맞춰 `<=` 또는 `<`를 선택합니다. 일반적으로 같은 리더의 재시도를 허용하려면 `<`를, 단 한 번만 적용되는 명령을 강제하려면 멱등 키와 함께 `<=` 정책을 조합합니다.

### 리더 헬스 모니터링과 우아한 stepdown

리더 선출은 "승리"보다 "사임"이 더 중요합니다. 리더가 외부 의존성(DB, 메시지 브로커, quorum 저장소)에 접근하지 못하는데도 lease만 연장하면, 살아 있지만 일하지 못하는 리더가 시스템을 막아 세웁니다.

아래는 우아한 stepdown을 위한 최소 규칙입니다.

1. 리더는 heartbeat 전마다 핵심 dependency health를 점검합니다.
2. 연속 실패 횟수가 임계치를 넘으면 heartbeat를 중단하고 스스로 follower로 내려옵니다.
3. in-flight 요청은 즉시 실패시키지 말고 짧은 drain 윈도우에서 정리합니다.

```python
# graceful_stepdown.py
class LeaderRuntime:
    def __init__(self, max_failures: int = 3):
        self.max_failures = max_failures
        self.consecutive_failures = 0
        self.is_leader = False

    def check_dependencies(self) -> bool:
        # DB ping, broker metadata fetch, lock store read 등
        return True

    def on_heartbeat_tick(self) -> str:
        if not self.is_leader:
            return "follower"

        if self.check_dependencies():
            self.consecutive_failures = 0
            return "renewed"

        self.consecutive_failures += 1
        if self.consecutive_failures >= self.max_failures:
            self.is_leader = False
            return "stepdown"
        return "degraded"
```

이 절차를 넣으면 장애 전파가 줄어듭니다. 불완전한 리더가 오래 버티며 오류를 퍼뜨리기 전에 스스로 물러나도록 만들기 때문입니다.

### Kubernetes coordination API 기반 리더 선출

Kubernetes에서는 `coordination.k8s.io`의 `Lease` 리소스를 사용해 애플리케이션 리더 선출을 구현할 수 있습니다. 핵심 필드는 `holderIdentity`, `renewTime`, `leaseDurationSeconds`입니다.

```yaml
apiVersion: coordination.k8s.io/v1
kind: Lease
metadata:
  name: order-worker-leader
  namespace: production
spec:
  holderIdentity: worker-a-7d8b6c4f9f-hx2kg
  leaseDurationSeconds: 15
  acquireTime: "2026-05-20T03:11:15Z"
  renewTime: "2026-05-20T03:11:25Z"
  leaseTransitions: 42
```

애플리케이션 운영 시 권장 파라미터 예시는 다음과 같습니다.

- `leaseDurationSeconds`: 15
- `renewDeadline`: 10
- `retryPeriod`: 2

이 세 값은 `leaseDurationSeconds > renewDeadline > retryPeriod` 관계를 유지해야 합니다. 그래야 일시 지연을 흡수하면서도 실패 감지를 늦추지 않습니다.

간단 점검 명령은 아래와 같습니다.

```shell
kubectl -n production get lease order-worker-leader -o yaml
kubectl -n production describe lease order-worker-leader
```

`leaseTransitions`가 짧은 시간에 급격히 증가하면 리더 불안정 신호입니다. 이때는 애플리케이션 오류만 보지 말고 GC pause, CPU throttle, 네트워크 지연, API server 지연을 함께 확인해야 합니다.

### 선출 안정성 메트릭과 Prometheus 알림

리더 선출은 "동작했다"로 끝나지 않고 "얼마나 안정적으로 동작하는가"를 측정해야 합니다. 최소한 아래 메트릭을 수집합니다.

- `leader_election_is_leader` (gauge): 현재 인스턴스가 리더인지 여부
- `leader_election_transitions_total` (counter): 리더 전환 횟수
- `leader_election_renew_failures_total` (counter): lease 갱신 실패 횟수
- `leader_election_renew_latency_seconds` (histogram): 갱신 지연 분포
- `fencing_reject_total` (counter): stale token 거부 횟수

Python 서비스에서 Prometheus client로 계측하는 예시는 아래와 같습니다.

```python
# metrics.py
from prometheus_client import Counter, Gauge, Histogram

IS_LEADER = Gauge("leader_election_is_leader", "1 if this instance is leader")
TRANSITIONS = Counter("leader_election_transitions_total", "leader changes")
RENEW_FAILURES = Counter("leader_election_renew_failures_total", "renew failures")
RENEW_LATENCY = Histogram(
    "leader_election_renew_latency_seconds",
    "renew request latency",
    buckets=(0.01, 0.05, 0.1, 0.2, 0.5, 1, 2),
)
FENCING_REJECT = Counter("fencing_reject_total", "stale leader rejections")
```

알림 규칙 예시는 다음과 같습니다.

```yaml
groups:
  - name: leader-election
    rules:
      - alert: LeaderElectionFlapping
        expr: increase(leader_election_transitions_total[10m]) >= 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "리더 전환이 과도하게 자주 발생합니다"
      - alert: RenewFailureBurst
        expr: increase(leader_election_renew_failures_total[5m]) > 20
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "lease 갱신 실패가 급증했습니다"
```

운영에서 특히 중요한 해석은 이렇습니다. `transitions_total` 증가와 `renew_latency` p99 상승이 함께 보이면 선출 로직 버그보다 인프라 지연 가능성이 큽니다. 반대로 `fencing_reject_total`이 증가하는데 전환 횟수는 안정적이면, 예전 리더 프로세스 종료 지연이나 클라이언트 재시도 정책을 먼저 의심해야 합니다.

### 리더 선출 런북 최소 체크포인트

마지막으로, 리더 선출 장애 대응 런북은 다음 질문에 즉시 답할 수 있어야 합니다.

1. 현재 리더는 누구이며 토큰 값은 얼마인가?
2. 마지막 10분 동안 리더가 몇 번 바뀌었는가?
3. stale token 거부가 증가했는가?
4. 리더가 dependency 실패로 stepdown했는가, 아니면 lease 만료로 교체되었는가?
5. 재시작 없이 문제를 완화할 수 있는 파라미터(renew deadline, retry period, TTL)는 무엇인가?

이 다섯 가지를 즉시 확인할 수 있으면, 리더 선출 문제를 "증상"이 아니라 "경계와 원인" 단위로 다룰 수 있습니다.

### TTL 파라미터 설계 가이드

TTL을 정할 때 자주 쓰는 공식은 다음과 같습니다.

```text
leaseDuration >= maxGCPause + maxNetworkRTT + clockSkew + safetyMargin
```

각 항의 실무 기준은 이렇습니다.

- `maxGCPause`: JVM 기반 서비스라면 CMS/G1 기준 200ms-2s, ZGC/Shenandoah라면 10ms 이하를 가정합니다.
- `maxNetworkRTT`: 같은 리전 AZ 간이면 1-2ms, 크로스 리전이면 50-150ms를 잡습니다.
- `clockSkew`: NTP 동기화 환경에서 보통 수십 ms 이내이지만, VM 마이그레이션 직후 수백 ms까지 뛸 수 있습니다.
- `safetyMargin`: 위 세 값 합산의 2배 이상을 권장합니다.

예를 들어 JVM 서비스(G1GC, maxGCPause=1s)가 같은 리전(RTT=2ms, clockSkew=50ms)에서 동작한다면 최소 TTL은 `(1000 + 2 + 50) * 3 = ~3.2s`이므로 5초가 합리적 시작점입니다. heartbeat 주기는 TTL의 1/3인 약 1.5-2초로 설정하면 한두 번의 갱신 실패를 흡수할 수 있습니다.

TTL이 너무 짧으면 네트워크 순간 지연에 불필요한 리더 전환(flapping)이 일어나고, 너무 길면 실제 장애 시 복구 시간이 길어집니다. 운영 초기에는 보수적으로 잡고, `leader_election_transitions_total` 메트릭을 관찰하며 점진적으로 줄여 가는 것이 안전합니다.

## 처음 질문으로 돌아가기

- **왜 리더 선출이 필요하며 어떤 안전 조건이 필요할까요?**
  - 리더 선출이 필요한 이유는 쓰기 권한을 한 시점에 하나로 제한해 split-brain을 막기 위해서입니다. 안전 조건은 "동시에 두 리더가 쓰지 못한다"로 요약되며, 본문에서 본 것처럼 lease 만료 경계, 단조 증가 fencing token, 자원 서버의 토큰 거부 검증이 함께 있어야 이 조건이 실제로 지켜집니다.
- **lease와 heartbeat는 각각 어떤 역할을 할까요?**
  - lease는 리더 권한의 유효 기간을 정의하는 안전 경계이고, heartbeat는 그 권한을 연장하는 유지 신호입니다. 즉 lease는 "권한이 언제 끝나는지"를, heartbeat는 "현재 리더가 아직 건강하게 일하는지"를 나타냅니다. Kubernetes Lease와 stepdown 예시처럼 heartbeat가 멈추거나 dependency 점검이 실패하면 다음 후보가 권한을 가져가도록 설계해야 합니다.
- **fencing token은 왜 이전 리더를 막는 핵심 장치일까요?**
  - fencing token은 선출 결과를 자원 서버 검증으로 연결하는 마지막 안전장치이기 때문입니다. 예전 리더가 GC pause 뒤에 복귀해도 더 작은 토큰이면 거부되므로 데이터 오염이 발생하지 않습니다. 본문에서 본 FastAPI 예시와 `fencing_reject_total` 메트릭이 바로 이 보호막이 실제로 동작하는지 확인하는 운영 근거입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Distributed Systems 101 (1/10): 분산 시스템이란 무엇인가?](./01-what-is-a-distributed-system.md)
- [Distributed Systems 101 (2/10): 장애 모델](./02-failure-model.md)
- [Distributed Systems 101 (3/10): RPC와 메시지 전달](./03-rpc-and-message-passing.md)
- [Distributed Systems 101 (4/10): 일관성과 CAP](./04-consistency-and-cap.md)
- [Distributed Systems 101 (5/10): 복제](./05-replication.md)
- [Distributed Systems 101 (6/10): 합의와 Raft](./06-consensus-and-raft.md)
- **리더 선출 (현재 글)**
- 메시지 큐와 이벤트 소싱 (예정)
- 분산 트랜잭션 (예정)
- 운영 가능한 분산 시스템 패턴 (예정)

<!-- toc:end -->

## 참고 자료

- [Leader election — Wikipedia](https://en.wikipedia.org/wiki/Leader_election)
- [How to do distributed locking — Martin Kleppmann](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)
- [etcd lease and leader election](https://etcd.io/docs/v3.5/learning/lock/)
- [Kubernetes leader election library](https://pkg.go.dev/k8s.io/client-go/tools/leaderelection)
- [ZooKeeper recipes and solutions — Leader Election](https://zookeeper.apache.org/doc/current/recipes.html#sc_leaderElection)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/distributed-systems-101/ko)

Tags: Computer Science, Distributed Systems, LeaderElection, Lease, Coordination, Liveness
