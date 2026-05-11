---
series: distributed-systems-101
episode: 4
title: consistency와 CAP
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
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
seo_description: 분산 데이터의 consistency 모델과 CAP 정리, PACELC까지 읽는 법을 한 장에 정리합니다.
last_reviewed: '2026-05-11'
---

# consistency와 CAP

> Distributed Systems 101 시리즈 (4/10)


## 이 글에서 다룰 문제

"DB가 강하게 일관적이다/eventual하다"라는 한 줄 차이가 시스템 전체 설계를 바꿉니다. 사용자에게 보일 화면, retry 정책, 장애 시 동작이 모두 여기서 정해집니다. CAP를 모르면 docs의 단어를 읽을 수 없습니다.

> consistency model은 데이터의 사회 계약입니다.

## 전체 흐름
```mermaid
flowchart LR
    A["linearizable"] --> B["sequential"]
    B --> C["causal"]
    C --> D["eventual"]
    A -.->|강함| D
```

왼쪽일수록 사용자가 보기에 직관적이지만 비쌉니다. 오른쪽일수록 싸고 가용성이 좋지만 직관과 멀어집니다.

## Before/After

**Before — "DB가 알아서"**

```text
잘 모르고 default를 쓴 결과 race, stale read 발생
```

**After — 명시적 model 선택**

```text
주문/결제 → linearizable, 피드/추천 → eventual
```

화면별로 적절한 model을 골라 비용을 분배합니다.

## model의 차이를 코드로

### 1단계 — single node (linearizable의 기준)

```python
# 예제 파일: 1_single.py
from collections import deque
log = []
def write(x): log.append(x)
def read(): return log[-1] if log else None
```

한 노드 안에선 모든 read가 마지막 write를 봅니다. 이 직관이 우리가 비교할 기준입니다.

### 2단계 — async replica (eventual)

```python
# 예제 파일: 2_eventual.py
import threading, time
primary = []
replica = []
def write(x):
    primary.append(x)
    threading.Thread(target=lambda: (time.sleep(0.5), replica.append(x))).start()
def read_primary(): return primary[-1] if primary else None
def read_replica(): return replica[-1] if replica else None
```

방금 쓴 값이 replica에서는 0.5초 동안 안 보입니다. 이게 eventual의 정체입니다.

### 3단계 — read-your-writes 흉내

```python
# 3_ryw.py
session_writes = {}
def write(uid, x):
    primary.append(x); session_writes[uid] = x
def read(uid):
    if uid in session_writes:
        return session_writes[uid]   # 자기 write는 즉시 보장
    return read_replica()
```

session 단위 보장으로 약한 consistency 위에 강한 보장을 얹는 흔한 패턴입니다.

### 4단계 — partition 시뮬레이션 (CAP 선택)

```python
# 4_partition.py (의사코드)
def write(x):
    if not majority_alive():
        # CP 선택: 거부
        raise Exception("no majority")
        # 또는 AP 선택: 자기 노드에만 쓰고 나중에 merge
```

같은 코드 두 줄 차이가 CP와 AP를 가릅니다.

### 5단계 — causal 흉내 (vector clock 한 줄)

```python
# 예제 파일: 5_vector.py
clock = {"A":0, "B":0}
def tick(node): clock[node] += 1
def happens_before(a, b):
    return all(a[k] <= b[k] for k in a) and any(a[k] < b[k] for k in a)
```

causal model은 happens-before만 보존하면 됩니다. 동시에 일어난 일은 임의 순서를 허용합니다.

## 이 코드에서 주목할 점

- consistency는 binary가 아니라 spectrum입니다.
- 같은 시스템 안에서도 화면별로 다른 model을 고를 수 있습니다.
- read-your-writes는 약한 model 위에서 사용자 경험을 살리는 핵심 트릭입니다.
- partition 시 CP/AP는 정책 결정입니다, 자동이 아닙니다.

## 자주 하는 실수 5가지

1. **CAP의 C를 transaction의 C와 헷갈린다.** 둘은 다른 개념입니다.
2. **"우리는 CP다"라고 단정한다.** 동일 시스템도 호출별로 다를 수 있습니다.
3. **eventual을 "결국 빠르게 일관됨"으로 본다.** 보장은 시간 상한 없습니다.
4. **read-your-writes를 자동으로 가정한다.** 명시적으로 구현해야 합니다.
5. **partition을 무시한 채 강한 consistency를 약속한다.** 약속을 못 지킵니다.

## 실무에서는 이렇게 쓰입니다

Spanner, etcd, ZooKeeper는 linearizable에 가깝게 동작합니다 (CP). DynamoDB, Cassandra, Redis Cluster는 기본이 eventual에 가깝습니다 (AP). 같은 회사 안에서도 결제 DB는 CP, 추천 캐시는 AP로 분리합니다. PACELC는 partition 없을 때(latency vs consistency)까지 보게 해 줍니다.

## 체크리스트

- [ ] linearizable과 eventual의 차이를 한 줄로 말할 수 있는가?
- [ ] CAP가 partition 없는 평소엔 어떤 의미인지 답할 수 있는가?
- [ ] 우리 시스템의 화면별 model을 매핑할 수 있는가?
- [ ] read-your-writes를 어떻게 구현할지 답할 수 있는가?
- [ ] PACELC의 ELC가 무엇인지 아는가?

## 정리 및 다음 단계

consistency model은 데이터를 분산할 때 가장 중요한 트레이드오프 축입니다. 다음 글에서는 이 model 선택의 직접적 원인 — replication 의 종류와 동기/비동기 — 를 다룹니다.

<!-- toc:begin -->
- [분산 시스템이란 무엇인가?](./01-what-is-a-distributed-system.md)
- [failure model](./02-failure-model.md)
- [RPC와 message passing](./03-rpc-and-message-passing.md)
- **consistency와 CAP (현재 글)**
- replication (예정)
- consensus와 Raft (예정)
- leader election (예정)
- message queue와 event sourcing (예정)
- distributed transaction (예정)
- 운영 가능한 분산 시스템 패턴 (예정)
<!-- toc:end -->

## 참고 자료

- [CAP theorem (Wikipedia)](https://en.wikipedia.org/wiki/CAP_theorem)
- [Consistency model (Wikipedia)](https://en.wikipedia.org/wiki/Consistency_model)
- [PACELC theorem (Wikipedia)](https://en.wikipedia.org/wiki/PACELC_theorem)
- [Designing Data-Intensive Applications — chapter 9](https://dataintensive.net/)

Tags: Computer Science, Distributed Systems, Consistency, CAP, Linearizability, Eventual Consistency
