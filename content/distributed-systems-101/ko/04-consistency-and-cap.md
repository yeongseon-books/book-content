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

## 먼저 던지는 질문

- 여기서 말하는 일관성은 정확히 무엇이며 트랜잭션의 C와 어떻게 다를까요?
- linearizable, sequential, causal, eventual은 어떤 스펙트럼을 이룰까요?
- CAP 정리는 무엇을 말하며, 어디서 자주 오해될까요?

## 큰 그림

![Distributed Systems 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/distributed-systems-101/04/04-01-concept-at-a-glance.ko.png)

*Distributed Systems 101 4장 흐름 개요*

이 그림에서는 일관성과 CAP를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 일관성과 CAP의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

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

Spanner, etcd, ZooKeeper는 linearizable에 가깝게 동작하는 CP 계열입니다. DynamoDB, Cassandra, Redis Cluster는 기본적으로 eventual에 가까운 AP 성향을 가집니다. 같은 회사 안에서도 결제 시스템은 CP, 추천 캐시는 AP를 선택하는 경우가 흔합니다. PACELC는 파티션이 없는 평상시에도 지연과 일관성 사이의 비용을 보게 해 줍니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 시스템 전체가 아니라 화면과 경로별로 모델을 매핑합니다.
- read-your-writes를 sticky session 같은 방식으로 명시적으로 제공합니다.
- 파티션 정책을 운영 책임의 일부로 다룹니다.
- 강한 일관성의 비용을 SLO로 측정합니다.
- 모델이 이름 붙어 있지 않은 문서는 신뢰하지 않습니다.

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

## 처음 질문으로 돌아가기

- **여기서 말하는 일관성은 정확히 무엇이며 트랜잭션의 C와 어떻게 다를까요?**
  - 본문의 기준은 일관성과 CAP를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **linearizable, sequential, causal, eventual은 어떤 스펙트럼을 이룰까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **CAP 정리는 무엇을 말하며, 어디서 자주 오해될까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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

Tags: Computer Science, Distributed Systems, Consistency, CAP, Linearizability, Eventual Consistency
