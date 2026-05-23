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

여기서는 Raft를 통해 합의 문제를 사람이 읽을 수 있는 수준으로 풀어 보고, term, log, quorum, commit이 어떤 약속을 만드는지 짚습니다.

![Distributed Systems 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/distributed-systems-101/06/06-01-concept-at-a-glance.ko.png)
*Distributed Systems 101 6장 흐름 개요*

## 먼저 던지는 질문

- 합의 문제란 무엇이며 어떤 안전성과 진행성 속성을 가질까요?
- Raft의 세 역할인 leader, follower, candidate는 어떻게 나뉠까요?
- term, log, index, commit은 각각 무엇을 뜻할까요?

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

## 적용 전후 비교
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
# 노드 5개 중 partition 한쪽에는 2개만 존재(leader 포함)
# - 그쪽은 과반이 없어 새 leader 선출 불가 -> write 수락 불가
# - 반대쪽은 노드 3개로 과반 확보 -> 새 leader 선출 -> 계속 동작
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

## 실전 설계 확장: Raft를 운영 가능한 시스템으로 만드는 방법

앞부분에서 Raft의 핵심 변수(term, log, commit)를 짚었다면, 이제는 운영 관점으로 내려와야 합니다. 실무에서 문제가 되는 지점은 "알고리즘을 안다"가 아니라 "장애 시점에도 같은 판단을 반복할 수 있다"입니다. 이를 위해서는 선거, 복제, 안전성, 스냅샷, 멤버십 변경, 관측 지표를 하나의 운영 모델로 연결해 두어야 합니다.

### Raft 합의 프로토콜 상세 흐름

Raft는 리더 중심 프로토콜입니다. 모든 쓰기 요청은 leader를 통과하고, follower는 leader가 보낸 로그를 복제합니다. candidate는 리더가 비정상으로 보일 때만 잠시 등장하는 선거 역할입니다.

```text
1) follower는 AppendEntries(heartbeat)를 기다립니다.
2) 일정 시간 heartbeat가 없으면 candidate로 전환합니다.
3) candidate는 term을 1 증가시키고 RequestVote를 브로드캐스트합니다.
4) 과반수 표를 얻으면 leader가 됩니다.
5) leader는 클라이언트 쓰기를 log entry로 추가하고 follower에 복제합니다.
6) 과반 복제가 확인되면 commit index를 올립니다.
7) commit된 엔트리를 상태 머신에 적용합니다.
```

핵심은 "쓰기 성공 응답 시점"입니다. leader 로컬 메모리에만 쓴 상태는 성공이 아닙니다. 과반 복제 후 commit된 시점이 성공입니다. 이 구분이 없으면 리더 장애 직후 데이터 소실로 이어집니다.

### 리더 선출: term 번호, 투표 규칙, split vote 처리

Raft에서 term은 시간의 논리적 버전입니다. 노드는 자신보다 작은 term 메시지를 거부하고, 더 큰 term 메시지를 받으면 즉시 follower로 내려갑니다. 이 단순한 규칙이 "오래된 리더" 문제를 정리합니다.

투표 규칙은 두 가지 제약을 결합합니다.

1. 한 term에서 한 노드는 한 번만 투표합니다.
2. 후보의 로그가 충분히 최신일 때만 투표합니다.

두 번째 규칙이 매우 중요합니다. 단순히 "먼저 요청한 후보"에게 표를 주면, 낡은 로그를 가진 후보가 리더가 될 수 있기 때문입니다. Raft는 `lastLogTerm`, `lastLogIndex`를 비교해 최신성 조건을 확인합니다.

split vote는 여러 candidate가 동시에 출현해 과반을 얻지 못하는 상황입니다. 실무에서는 아래 두 장치로 완화합니다.

- election timeout 랜덤화(예: 150ms~300ms)
- heartbeat interval을 election timeout보다 충분히 작게 유지(예: 50ms)

```yaml
raft_timing:
  heartbeat_interval_ms: 50
  election_timeout_min_ms: 150
  election_timeout_max_ms: 300
  pre_vote: true
```

`pre_vote`는 네트워크 일시 지연으로 분리되었던 노드가 복귀하며 term을 불필요하게 끌어올리는 문제를 줄이는 데 유용합니다.

### 로그 복제와 안전성: 왜 index+term 쌍이 중요한가

Raft의 안전성은 "로그의 위치(index)"와 "그 위치의 작성 시점(term)"을 함께 비교하는 데서 나옵니다. follower가 `prevLogIndex`, `prevLogTerm` 검증에 실패하면 leader는 한 칸씩 되돌아가 일치 지점을 찾고, 그 지점 이후를 다시 전송합니다.

이 과정은 비싸 보이지만 효과가 큽니다.

- 잘못 갈라진 분기 로그를 정리합니다.
- commit된 엔트리는 보존합니다.
- leader 변경 뒤에도 로그를 단일 직선 히스토리로 복원합니다.

아래와 같이 leader가 follower별 `next_index`를 추적하면 재동기화가 자동으로 진행됩니다.

```python
# raft_leader_sync.py
def replicate_to_follower(leader, follower_id):
    next_idx = leader.next_index[follower_id]
    prev_idx = next_idx - 1
    prev_term = leader.log[prev_idx]["term"] if prev_idx >= 0 else 0
    entries = leader.log[next_idx:]

    ok = send_append_entries(
        follower_id=follower_id,
        term=leader.current_term,
        prev_log_index=prev_idx,
        prev_log_term=prev_term,
        entries=entries,
        leader_commit=leader.commit_index,
    )

    if ok:
        leader.match_index[follower_id] = next_idx + len(entries) - 1
        leader.next_index[follower_id] = leader.match_index[follower_id] + 1
    else:
        leader.next_index[follower_id] = max(0, next_idx - 1)
```

### 커밋 규칙과 선형화 보장

Raft는 "과반 복제"만으로 충분해 보이지만, 엄밀히는 "현재 term의 엔트리"가 과반 복제되어야 commit index를 안전하게 전진시킬 수 있습니다. 이 조건이 있어야 이전 term의 불완전한 엔트리가 잘못 확정되는 일을 막습니다.

읽기 경로도 설계가 필요합니다.

- 강한 일관성 읽기: leader 확인(read index, quorum 확인) 후 응답
- 완화 읽기: follower stale read 허용(지연 허용 범위 명시)

쓰기와 읽기 모두 "어떤 일관성 계약으로 응답했는가"를 API 문서에 명시해야 장애 시 오해가 줄어듭니다.

읽기 선형화를 구현하는 대표적 방법은 ReadIndex입니다. leader가 quorum에게 heartbeat를 보내 자신이 여전히 leader임을 확인한 뒤, 현재 commit index까지 적용된 상태에서 읽기 결과를 반환합니다. 이 방식은 쓰기 로그를 추가하지 않으므로 성능 부담이 적으면서도 선형화를 보장합니다.

```python
# read_index.py — ReadIndex 기반 선형 읽기 흐름 (의사 코드)
def linearizable_read(leader, peers, key):
    # 1) 현재 commit index 기록
    read_index = leader.commit_index
    # 2) quorum heartbeat 확인
    acks = 1
    for p in peers:
        if p.confirm_leader(leader.current_term):
            acks += 1
    if acks <= len(peers) // 2:
        raise NotLeaderError("quorum 확인 실패")
    # 3) 상태 머신이 read_index까지 적용될 때까지 대기
    wait_until_applied(read_index)
    return state_machine.get(key)
```

Lease 기반 읽기는 heartbeat 주기 내에서는 quorum 확인을 생략해 지연을 줄이지만, 시계 skew가 크면 stale read가 발생할 수 있으므로 NTP 동기화 품질을 사전에 확보해야 합니다.

### 로그 컴팩션과 스냅샷: 무한 로그를 운영 가능한 크기로 줄이기

Raft 로그는 계속 쌓이기 때문에 컴팩션이 필수입니다. 일반적인 전략은 "특정 commit index까지 상태 머신 스냅샷 저장" 후, 그 이전 로그를 절단하는 방식입니다.

```yaml
snapshot:
  trigger:
    committed_entries: 10000
    wal_size_mb: 64
  retention:
    keep_last_snapshots: 3
  restore:
    verify_checksum: true
```

스냅샷에서 중요한 포인트는 세 가지입니다.

1. `last_included_index`, `last_included_term`를 반드시 저장합니다.
2. 스냅샷 전송 중에도 리더의 새 로그 복제는 계속 진행될 수 있어야 합니다.
3. 복구 시 스냅샷과 이후 증분 로그를 정확히 이어 붙여야 합니다.

초기 동기화가 느린 신규 노드에는 로그를 처음부터 보내기보다 스냅샷을 먼저 보내고, 이후 tail 로그를 따라잡게 하는 편이 훨씬 빠릅니다.

스냅샷 크기가 큰 시스템에서는 InstallSnapshot RPC를 chunk 단위로 분할 전송하고, 각 chunk에 offset과 done 플래그를 붙여 follower가 순서대로 조립합니다. 이 과정에서 leader는 해당 follower의 next_index를 스냅샷의 last_included_index + 1로 재설정합니다.

```python
# install_snapshot.py — 스냅샷 전송 흐름 (의사 코드)
CHUNK_SIZE = 1024 * 1024  # 1 MB

def send_snapshot(leader, follower_id, snapshot_path):
    with open(snapshot_path, "rb") as f:
        offset = 0
        while True:
            chunk = f.read(CHUNK_SIZE)
            done = len(chunk) < CHUNK_SIZE
            send_install_snapshot(
                follower_id=follower_id,
                term=leader.current_term,
                last_included_index=leader.snapshot_index,
                last_included_term=leader.snapshot_term,
                offset=offset,
                data=chunk,
                done=done,
            )
            offset += len(chunk)
            if done:
                break
    leader.next_index[follower_id] = leader.snapshot_index + 1
```

### Raft와 Paxos 비교

두 알고리즘 모두 합의를 해결하지만, 설계 관점이 다릅니다. 교육과 운영 자동화 측면에서는 Raft가 이해/구현 난도를 낮추는 장점이 있습니다.

| 항목 | Raft | Paxos |
| --- | --- | --- |
| 기본 구조 | leader 중심 로그 복제 | proposer/acceptor 기반 합의 |
| 이해 난도 | 상대적으로 낮음 | 상대적으로 높음 |
| 로그 복제 모델 | 알고리즘에 내장 | Multi-Paxos로 확장 필요 |
| 구현/운영 문서화 | 역할과 상태가 명확 | 변형이 많아 구현별 차이 큼 |
| 리더 교체 시 가시성 | term과 선거 이벤트로 명확 | 구현에 따라 추적 복잡도 상이 |

중요한 점은 "Raft가 항상 더 우월"이 아니라, 팀이 장애 시 일관된 판단을 할 수 있는 모델을 선택하는 것입니다. 대부분의 애플리케이션 메타데이터 계층에서는 Raft의 운영 단순성이 큰 장점으로 작동합니다.

실무에서 Paxos를 선택하는 경우는 단일 값 합의(예: 리더 선출 한 번)에 최적화하거나, 기존 Paxos 구현체(Google Chubby, Spanner)가 팀 내부에 이미 안정적으로 운영되고 있을 때입니다. 새로 구축하는 시스템에서 Multi-Paxos를 직접 구현하기보다는 Raft 라이브러리(etcd/raft, hashicorp/raft)를 임베딩하는 편이 운영 복잡도를 크게 줄입니다.

### Raft 클러스터 사이징 가이드

노드 수 결정은 장애 허용 능력과 쓰기 지연의 트레이드오프입니다.

| 노드 수 | 장애 허용 (f) | quorum | 쓰기 지연 특성 |
| --- | --- | --- | --- |
| 3 | 1 | 2 | 가장 빠름, 단일 장애만 허용 |
| 5 | 2 | 3 | 일반 프로덕션 권장 |
| 7 | 3 | 4 | 지리 분산 시 고려, 지연 증가 |

노드를 짝수(4, 6)로 두면 장애 허용 수는 홀수보다 늘지 않으면서 quorum 비용만 커집니다. 예를 들어 4노드 클러스터의 장애 허용은 1로 3노드와 동일하지만, quorum은 3이므로 쓰기마다 한 노드 더 기다려야 합니다. 따라서 홀수 노드가 비용 대비 효율이 높습니다.

지리 분산 배치에서는 quorum 응답 지연이 가장 먼 노드가 아니라 "과반 중 가장 먼 노드"에 의해 결정됩니다. 5노드를 서울 2, 도쿄 2, 싱가포르 1로 배치하면 quorum 3은 서울-도쿄 지연으로 결정되고, 싱가포르 노드는 쓰기 경로에 영향을 주지 않습니다.

### etcd/Raft 운영 패턴

Kubernetes control plane이 etcd에 의존한다는 사실은 "Raft 장애가 곧 제어면 장애"라는 뜻입니다. 따라서 etcd 운영에서는 클러스터 수명주기와 Raft 파라미터를 함께 관리해야 합니다.

```yaml
name: infra-etcd-1
data-dir: /var/lib/etcd
listen-client-urls: https://0.0.0.0:2379
advertise-client-urls: https://10.0.0.11:2379
listen-peer-urls: https://0.0.0.0:2380
initial-advertise-peer-urls: https://10.0.0.11:2380
initial-cluster: infra-etcd-1=https://10.0.0.11:2380,infra-etcd-2=https://10.0.0.12:2380,infra-etcd-3=https://10.0.0.13:2380
initial-cluster-state: existing
initial-cluster-token: infra-etcd-prod
heartbeat-interval: 100
election-timeout: 1000
snapshot-count: 10000
auto-compaction-mode: revision
auto-compaction-retention: "5000"
```

운영 패턴은 아래 순서를 추천합니다.

1. 홀수 노드(3 또는 5) 유지, 지리적으로 너무 멀리 분산하지 않습니다.
2. 디스크 지연과 fsync 성능을 우선 관리합니다.
3. 정기 스냅샷 백업과 복구 리허설을 분리된 절차로 운영합니다.
4. 클라이언트 재시도는 멱등성 키와 함께 설계합니다.

### 멤버십 변경: Joint Consensus를 왜 써야 하는가

Raft 클러스터에서 노드 추가/제거는 단순 리스트 수정이 아닙니다. 과반 집합이 바뀌는 순간 안전성이 흔들릴 수 있기 때문입니다. 이를 막기 위해 Joint Consensus를 사용합니다.

핵심 아이디어는 전환 중 일시적으로 "구성 C_old와 C_new 모두의 과반"을 요구하는 것입니다.

```text
단계 1) C_old -> C_old,new (공동 구성)
단계 2) C_old,new에서 로그 엔트리 commit
단계 3) C_new로 최종 전환
```

이 방식은 전환 중에도 서로 다른 다수 집합이 독립적으로 리더를 인정하는 split-brain을 막습니다. 운영 런북에는 구성 변경을 반드시 "한 번에 한 노드" 단위로 적용하도록 제한하는 것이 안전합니다.

### Raft 헬스 모니터링: Prometheus 지표 중심 점검

Raft는 내부 상태가 명확하므로 지표 기반 운영이 잘 맞습니다. 아래 지표들은 대부분의 etcd/raft 계열 시스템에서 최소 기준으로 잡아야 합니다.

```text
리더 안정성: leader_changes_seen_total
제안 처리: proposals_committed_total, proposals_failed_total
지연: peer_round_trip_time_seconds
적체: backend_commit_duration_seconds, wal_fsync_duration_seconds
상태: has_leader(0/1), is_learner(0/1)
```

Prometheus 알림 규칙 예시는 아래처럼 시작할 수 있습니다.

```yaml
groups:
  - name: raft-health
    rules:
      - alert: RaftLeaderFlapping
        expr: increase(etcd_server_leader_changes_seen_total[10m]) > 3
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "리더 변경이 과도하게 발생합니다"

      - alert: RaftNoLeader
        expr: max(etcd_server_has_leader) == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "클러스터가 리더를 잃었습니다"

      - alert: RaftProposalFailures
        expr: rate(etcd_server_proposals_failed_total[5m]) > 0
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "합의 제안 실패가 지속됩니다"
```

여기서 중요한 운영 습관은 "알림 임계치"를 고정값으로 두지 않고, 평시 분포(p95/p99) 기반으로 주기적으로 재조정하는 것입니다.

### 장애 대응 시퀀스: 리더 장애, 과반 손실, 복구

Raft 장애 대응은 즉흥 대응보다 고정 시퀀스가 훨씬 안전합니다.

1. `has_leader`와 리더 변경 횟수로 선거 안정성을 먼저 확인합니다.
2. `proposals_failed_total` 상승 여부로 쓰기 경로 손상을 확인합니다.
3. 디스크/네트워크 지연 지표를 보고 원인을 선거 문제와 I/O 문제로 분리합니다.
4. 과반 손실 시 쓰기 거절 정책을 명시적으로 적용합니다.
5. 복구 후 backlog 적용 완료 전까지 트래픽 해제를 보류합니다.

```shell
# etcd 상태 점검 예시
etcdctl endpoint status --cluster -w table
etcdctl endpoint health --cluster
etcdctl alarm list
```

이 시퀀스를 런북으로 고정해 두면, 담당자가 바뀌어도 같은 의사결정 품질을 재현할 수 있습니다. 합의 시스템의 실전 안정성은 알고리즘 자체보다 운영 일관성에서 갈립니다.

### 클라이언트 재시도와 멱등성

리더가 교체되는 순간 클라이언트는 일시적으로 응답을 받지 못합니다. 단순 재시도만 하면 중복 쓰기가 발생하므로 멱등성 키(idempotency key)를 함께 설계해야 합니다.

```python
# idempotent_write.py
from fastapi import FastAPI, HTTPException

app = FastAPI()
applied_requests: dict[str, dict] = {}

@app.post("/write")
async def write(idempotency_key: str, payload: dict):
    if idempotency_key in applied_requests:
        return {"status": "already_applied", "result": applied_requests[idempotency_key]}
    result = await submit_to_raft_leader(idempotency_key, payload)
    if result is None:
        raise HTTPException(status_code=503, detail="leader unavailable")
    applied_requests[idempotency_key] = result
    return {"status": "committed", "result": result}
```

핵심은 "같은 키로 두 번 들어오면 두 번째는 적용하지 않고 결과만 반환"하는 것입니다. 키는 클라이언트에서 생성해야 하며, 적용된 요청은 TTL로 만료시켜 메모리 무한 증가를 방지합니다.

### Raft 구현체 선택과 테스트 전략

직접 Raft를 구현하는 경우는 드물지만, 라이브러리를 선택할 때는 다음 기준이 유용합니다.

| 기준 | 확인 사항 |
| --- | --- |
| 로그 저장소 | WAL + 스냅샷이 분리되어 있는가 |
| 멤버십 변경 | Joint Consensus 또는 single-server 방식 지원 여부 |
| Pre-vote | 네트워크 분리 후 복귀 시 term 폭주 방지 |
| Learner 역할 | 투표 없이 로그만 복제받는 읽기 전용 노드 |
| 벤치마크 | fsync 포함 쓰기 처리량과 p99 지연 |

테스트 전략은 정상 경로보다 장애 경로에 집중해야 합니다.

```python
# raft_chaos_test.py (pseudocode)
import random

def test_leader_crash_during_commit():
    """리더가 과반 복제 직전에 죽으면 새 리더는 해당 엔트리를 commit하지 않아야 합니다."""
    cluster = create_cluster(nodes=5)
    leader = cluster.get_leader()
    # 로그 하나를 리더에만 쓰고 복제 전에 crash
    leader.append_local_only(entry={"cmd": "set x=1"})
    cluster.kill(leader)
    new_leader = cluster.wait_for_election()
    # 새 리더의 commit index에 해당 엔트리가 없어야 함
    assert not new_leader.has_committed({"cmd": "set x=1"})
```

이런 장애 시나리오 테스트 없이 합의 구현체를 선택하면, 운영 중 예상치 못한 엣지 케이스에서 데이터 손실이 발생할 수 있습니다. Jepsen 같은 도구가 존재하는 이유이기도 합니다.

## 처음 질문으로 돌아가기

- **합의 문제란 무엇이며 어떤 안전성과 진행성 속성을 가질까요?**
  - 합의 문제는 여러 노드가 부분 장애와 지연이 있는 환경에서도 같은 순서의 결정을 공유하도록 만드는 문제입니다. 안전성은 commit된 로그가 사라지지 않고 둘 이상의 리더가 동시에 쓰기를 확정하지 못하도록 막는 것이고, 진행성은 과반이 살아 있으면 결국 새 리더가 선출되어 쓰기가 전진하는 것입니다.
- **Raft의 세 역할인 leader, follower, candidate는 어떻게 나뉠까요?**
  - follower는 heartbeat를 수신하는 기본 상태이고, heartbeat가 끊기면 candidate로 전환해 선거를 시작합니다. 과반 표를 얻은 candidate가 leader가 되어 모든 쓰기를 받고 복제합니다.
- **term, log, index, commit은 각각 무엇을 뜻할까요?**
  - term은 리더십 세대 번호이고, log는 상태 변경 엔트리의 순서 목록이며, index는 로그 위치 번호입니다. commit은 과반 복제로 "사라지지 않는 상태"가 된 약속이며, commit된 엔트리만 상태 머신에 적용됩니다.

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
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/distributed-systems-101/ko)

Tags: Computer Science, Distributed Systems, Consensus, Raft, Paxos, Replication
