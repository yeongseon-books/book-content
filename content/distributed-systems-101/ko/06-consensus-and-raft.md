---
series: distributed-systems-101
episode: 6
title: "Distributed Systems 101 (6/10): 합의와 Raft"
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
  - Consensus
  - Raft
  - Paxos
  - Replication
seo_description: 분산 시스템의 핵심인 합의 문제와 Raft 알고리즘의 작동 원리, 로그 복제 및 커밋 구조를 예제 코드로 상세히 설명합니다.
last_reviewed: '2026-05-15'
---

# Distributed Systems 101 (6/10): 합의와 Raft

"클러스터가 동의하면 된다"는 말은 쉽지만, 실제로는 가장 까다로운 요구 사항 중 하나입니다. 리더가 중간에 사라지고 메시지가 늦게 도착하는 상황에서도 모두가 같은 로그를 본다고 약속해야 하기 때문입니다.

이 글은 Distributed Systems 101 시리즈의 여섯 번째 글입니다.

여기서는 Raft를 통해 합의 문제를 사람이 읽을 수 있는 수준으로 풀어 보고, term, log, quorum, commit이 어떤 약속을 만드는지 짚습니다.

## 먼저 던지는 질문

- 합의 문제란 무엇이며 어떤 안전성과 진행성 속성을 가질까요?
- Raft의 세 역할인 leader, follower, candidate는 어떻게 나뉠까요?
- term, log, index, commit은 각각 무엇을 뜻할까요?

## 큰 그림

![Distributed Systems 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/distributed-systems-101/06/06-01-concept-at-a-glance.ko.png)

*Distributed Systems 101 6장 흐름 개요*

## 왜 중요한가

합의 알고리즘은 etcd, ZooKeeper, Consul, CockroachDB 같은 시스템의 중심에 놓여 있습니다. Kubernetes control plane도 etcd 위에 서 있습니다. 합의를 이해하면 왜 시스템이 이런 식으로 동작하는지에 대한 질문 절반은 자연스럽게 풀립니다.

> 합의는 분산 시스템에서 동의가 갖는 가치입니다.

## 한눈에 보는 개념

하나의 leader가 로그를 받고 follower에게 복제합니다. 다수에게 도달한 엔트리만 commit으로 인정됩니다.

## 핵심 용어

- **Consensus**: N개의 노드가 하나의 값에 동의하는 문제입니다.
- **Term**: 단조 증가하는 epoch입니다. 새 리더가 뽑히면 새 term이 시작됩니다.
- **Log**: index로 식별되는 엔트리들의 순서 있는 목록입니다.
- **Commit**: 다수가 받은 엔트리가 더 이상 사라지지 않는 약속 상태입니다.
- **Quorum**: 보통 2f+1 중 f+1, 즉 다수를 뜻합니다.

## Before / After

**Before — 리더 혼자 결정**

```text
fast, but consistency breaks if the leader lies
```

**After — 다수의 동의로 결정**

```text
slightly slower, but safe even if a node dies or lies
```

다수결은 분산 시스템의 핵심 안전장치입니다.

## 실습: 짧은 코드로 보는 Raft의 핵심

### 1단계 — 상태 정의

```python
# 1_state.py
from dataclasses import dataclass, field
@dataclass
class Node:
    role: str = "follower"
    term: int = 0
    log: list = field(default_factory=list)
    commit_index: int = -1
    voted_for: int | None = None
```

term, log, commit_index는 Raft 논문의 첫 장을 여는 핵심 상태 변수입니다.

### 2단계 — 선거(단순화)

```python
# 2_election.py
def election_timeout(self, peers):
    self.term += 1
    self.role = "candidate"
    self.voted_for = self.id
    votes = 1
    for p in peers:
        if p.request_vote(self.term, self.id):
            votes += 1
    if votes > len(peers) // 2 + 1:
        self.role = "leader"
```

가장 먼저 타임아웃에 도달한 노드가 candidate가 되어 표를 모읍니다. 다수를 얻으면 leader가 됩니다.

### 3단계 — 로그 복제

```python
# 3_replicate.py
def append_entries(self, term, prev_index, entries):
    if term < self.term: return False
    if prev_index >= 0 and self.log[prev_index]["term"] != term:
        return False  # mismatch
    self.log = self.log[:prev_index+1] + entries
    return True
```

leader는 자신의 로그를 follower에게 보내고, follower는 이전 index와 term이 맞지 않으면 거부합니다. 로그 일관성은 바로 이 쌍으로 지켜집니다.

### 4단계 — commit

```python
# 4_commit.py
def maybe_commit(self, peers):
    for i in range(self.commit_index + 1, len(self.log)):
        acks = 1 + sum(1 for p in peers if p.match_index >= i)
        if acks > len(peers) // 2 + 1:
            self.commit_index = i
```

다수가 해당 엔트리를 갖게 되는 순간 commit됩니다. 이 시점부터 그 엔트리는 더 이상 사라지지 않습니다.

### 5단계 — 파티션 시나리오

```python
# 5_partition.py (pseudocode)
# 5 nodes, only 2 (leader included) on one side of a partition
# - that side has no majority -> cannot elect a new leader -> cannot accept writes
# - the other side has 3 nodes -> majority -> elects a new leader -> keeps working
```

다수를 잃은 쪽이 의도적으로 멈추는 설계가 split-brain을 막는 핵심입니다.

## 이 코드에서 먼저 봐야 할 점

- term은 단조 증가합니다. 예전 term의 메시지는 거절됩니다.
- 로그는 순서 자체가 본질이며, 일치는 index와 term 쌍으로 검증합니다.
- commit은 모두가 받았다는 뜻이 아니라 다수가 받았다는 약속입니다.
- 파티션된 쪽이 멈추는 것이 오히려 정답입니다.

## 자주 하는 실수 5가지

1. **리더 한 명만 있으면 안전하다고 생각합니다.** 안전성은 올바른 선거에서 나옵니다.
2. **리더가 받으면 commit이라고 생각합니다.** commit은 다수가 받았을 때입니다.
3. **모든 노드에 같은 타임아웃을 둡니다.** split vote가 자주 납니다.
4. **로그 일치 검사를 생략합니다.** 잘못된 엔트리가 commit될 수 있습니다.
5. **파티션된 쪽이 계속 써도 된다고 생각합니다.** 다수가 없으면 멈춰야 합니다.

## 실무에서는 이렇게 드러납니다

etcd, Consul, ZooKeeper의 ZAB, CockroachDB, TiKV는 모두 합의 알고리즘 위에 서 있습니다. 데이터베이스의 leader election, 분산 락, 설정 저장소는 전형적인 합의 사용 사례입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 합의는 비싸므로 자주 호출하지 않고 메타데이터 수준에만 씁니다.
- 타임아웃은 측정값을 바탕으로 무작위화합니다.
- 노드 수는 3, 5, 7처럼 홀수로 유지합니다.
- 리더 교체 중에도 안전한 클라이언트 재시도를 설계합니다.
- 읽기를 leader-only로 둘지 lease 기반으로 풀지 의도적으로 결정합니다.

## 체크리스트

- [ ] 합의를 한 줄로 정의할 수 있는가?
- [ ] term, log, commit의 관계를 설명할 수 있는가?
- [ ] 5노드 클러스터에서 몇 개까지 장애를 견디는지 말할 수 있는가?
- [ ] split vote를 어떻게 줄이는지 알고 있는가?
- [ ] etcd가 합의 위에 있다는 사실을 설계 판단에 반영하고 있는가?

## 연습 문제

1. 3노드와 5노드 클러스터의 장애 허용 능력을 비교해 보세요.
2. Raft의 randomized election timeout이 split vote를 줄이는 이유를 설명해 보세요.
3. etcd를 사용해 분산 락을 만드는 방식을 한 단락으로 적어 보세요.

## 정리와 다음 글

합의는 분산 시스템의 가장 단단한 문제이고, Raft는 그 문제를 사람이 읽을 수 있게 정리한 형태입니다. 다음 글에서는 합의 위에서 실제 리더를 안전하게 뽑고 교체하는 문제, 즉 leader election을 다룹니다.


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




### 추가 운영 예시: 쿼럼 손실과 복구 절차

쿼럼이 깨진 순간에는 "일단 쓰기를 받고 나중에 맞춘다"보다 "확정 가능한 쓰기만 받는다"를 기본값으로 두는 편이 안전합니다. 예를 들어 5노드 클러스터에서 2노드만 살아 있으면 새로운 쓰기는 거절하고, 읽기는 최신성 등급을 함께 내려 사용자와 상위 서비스가 의사결정을 할 수 있게 해야 합니다.

```yaml
degraded_mode:
  quorum_required: 3
  write_policy: reject
  read_policy:
    allow: true
    staleness_label: required
  response_headers:
    X-Consistency-Level: stale-possible
```

복구 시에는 아래 순서를 런북으로 고정해 두는 것이 좋습니다. 첫째, 리더 안정화 여부 확인. 둘째, 복제 지연이 임계치 아래로 내려왔는지 확인. 셋째, 큐 적체가 해소되었는지 확인. 넷째, 그 뒤에만 쓰기 트래픽 제한을 해제합니다. 이 순서가 바뀌면 겉보기 정상화 뒤에 데이터 불일치가 남을 가능성이 커집니다.

## 처음 질문으로 돌아가기

- **합의 문제란 무엇이며 어떤 안전성과 진행성 속성을 가질까요?**
  - 본문의 기준은 합의와 Raft를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Raft의 세 역할인 leader, follower, candidate는 어떻게 나뉠까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **term, log, index, commit은 각각 무엇을 뜻할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Distributed Systems 101 (1/10): 분산 시스템이란 무엇인가?](./01-what-is-a-distributed-system.md)
- [Distributed Systems 101 (2/10): 장애 모델](./02-failure-model.md)
- [Distributed Systems 101 (3/10): RPC와 메시지 전달](./03-rpc-and-message-passing.md)
- [Distributed Systems 101 (4/10): 일관성과 CAP](./04-consistency-and-cap.md)
- [Distributed Systems 101 (5/10): 복제](./05-replication.md)
- **합의와 Raft (현재 글)**
- 리더 선출 (예정)
- 메시지 큐와 이벤트 소싱 (예정)
- 분산 트랜잭션 (예정)
- 운영 가능한 분산 시스템 패턴 (예정)

<!-- toc:end -->

## 참고 자료

- [Raft consensus algorithm](https://raft.github.io/)
- [In Search of an Understandable Consensus Algorithm (Raft paper)](https://raft.github.io/raft.pdf)
- [Paxos (Wikipedia)](https://en.wikipedia.org/wiki/Paxos_(computer_science))
- [etcd documentation](https://etcd.io/docs/)

Tags: Computer Science, Distributed Systems, Consensus, Raft, Paxos, Replication
