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

이 글은 Distributed Systems 101 시리즈의 일곱 번째 글입니다.

여기서는 lease와 fencing token을 함께 써서, 리더를 고르는 문제를 넘어 예전 리더의 영향력을 끊는 운영 안전장치로 설명합니다.

## 먼저 던지는 질문

- 왜 리더 선출이 필요하며 어떤 안전 조건이 필요할까요?
- lease와 heartbeat는 각각 어떤 역할을 할까요?
- fencing token은 왜 이전 리더를 막는 핵심 장치일까요?

## 큰 그림

![Distributed Systems 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/distributed-systems-101/07/07-01-concept-at-a-glance.ko.png)

*Distributed Systems 101 7장 흐름 개요*

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

## Before / After

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
# old leader A: token=5, GC pause 30s
# meanwhile new leader B: token=6 issued
# A wakes up and tries to write with token=5 -> resource server rejects
# B's write with token=6 succeeds
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

- **왜 리더 선출이 필요하며 어떤 안전 조건이 필요할까요?**
  - 본문의 기준은 리더 선출를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **lease와 heartbeat는 각각 어떤 역할을 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **fencing token은 왜 이전 리더를 막는 핵심 장치일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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

Tags: Computer Science, Distributed Systems, LeaderElection, Lease, Coordination, Liveness
