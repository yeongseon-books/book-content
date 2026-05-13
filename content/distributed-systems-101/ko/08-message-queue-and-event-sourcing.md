---
series: distributed-systems-101
episode: 8
title: 메시지 큐와 이벤트 소싱
status: publish-ready
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
  - MessageQueue
  - EventSourcing
  - Kafka
  - CQRS
seo_description: 메시지 큐와 이벤트 소싱이 시간과 이력을 다루는 방식을 설명합니다.
last_reviewed: '2026-05-12'
---

# 메시지 큐와 이벤트 소싱

이 글은 Distributed Systems 101 시리즈의 여덟 번째 글입니다.

## 이 글에서 다룰 문제

- 메시지 큐는 어떤 결합 해소와 전달 보장을 제공할까요?
- at-most-once, at-least-once, exactly-once는 각각 무엇을 뜻할까요?
- 이벤트 소싱은 무엇이며 CQRS와는 어떤 관계일까요?
- Kafka를 브로커가 아니라 로그라고 부르는 이유는 무엇일까요?
- consumer group, partition, offset은 어떤 핵심 개념일까요?

> 메시지 큐와 이벤트 소싱은 분산 시스템에서 시간과 이력을 일급 도구로 끌어올리는 패턴입니다.

## 왜 중요한가

서비스 간 직접 호출은 가용성과 지연 시간을 강하게 묶습니다. 큐를 사이에 두면 한쪽의 생존 여부가 다른 쪽의 즉시 동작을 결정하지 않게 됩니다. 이벤트 소싱은 한 단계 더 나아가 상태를 이벤트의 합으로 정의하므로, 이력과 재생이 시스템의 본질이 됩니다.

> 큐는 시간을 분리하고, 이벤트는 진실의 원천을 분리합니다.

## 한눈에 보는 개념

```mermaid
flowchart LR
    P["producer"] --> Q["queue / log"]
    Q --> C1["consumer 1"]
    Q --> C2["consumer 2"]
    Q --> C3["consumer 3"]
```

생산자는 큐에 쓰고 소비자는 각자 속도로 읽습니다. 하나의 메시지를 여러 소비자가 서로 다른 목적으로 처리할 수도 있습니다.

## 핵심 용어

- **Message queue**: 메시지를 저장하고 전달해 주는 중간 매개체입니다.
- **Event sourcing**: 상태를 이벤트의 누적으로 표현하는 패턴입니다.
- **Offset**: 소비자가 어디까지 읽었는지를 가리키는 위치입니다.
- **Consumer group**: 메시지를 나눠 처리하는 소비자 집합의 단위입니다.
- **Idempotency**: 같은 메시지를 여러 번 처리해도 결과가 같게 유지되는 성질입니다.

## Before / After

**Before — 직접 호출 사슬**

```text
order -> payment -> inventory -> notify   (one death stops everything)
```

**After — 큐로 시간 분리**

```text
order -> queue
         -> payment consumer
         -> inventory consumer
         -> notify consumer
```

각 소비자는 자기 속도로 일하고, 잠시 죽어도 큐가 메시지를 붙들고 있습니다.

## 실습: 큐와 이벤트 소싱

### 1단계 — 메모리 큐에서 시작

```python
# 1_queue.py
from collections import deque
q = deque()
def produce(msg): q.append(msg)
def consume():
    if q: return q.popleft()
```

가장 단순한 메모리 큐입니다. 이후 단계는 이 아이디어를 분산 환경으로 확장합니다.

### 2단계 — 영속 큐(append-only log)

```python
# 2_log.py
import json
def produce(path, msg):
    with open(path, "a") as f: f.write(json.dumps(msg) + "\n")
def consume(path, offset):
    with open(path) as f:
        lines = f.readlines()
    return lines[offset], offset + 1
```

큐가 파일이 되는 순간 메시지는 프로세스 생명주기와 분리됩니다. 이것이 Kafka를 이해하는 가장 작은 출발점입니다.

### 3단계 — at-least-once와 멱등적 소비자

```python
# 3_idem.py
processed = set()
def consume_once(msg):
    if msg["id"] in processed: return "skip"
    processed.add(msg["id"])
    return "process"
```

큐가 같은 메시지를 두 번 전달해도 안전합니다. 메시지 ID가 중복을 걸러 줍니다.

### 4단계 — 이벤트 소싱으로 상태 재구성

```python
# 4_event.py
events = [
    {"type": "deposit", "amount": 100},
    {"type": "withdraw", "amount": 30},
]
def balance(events):
    b = 0
    for e in events:
        if e["type"] == "deposit": b += e["amount"]
        elif e["type"] == "withdraw": b -= e["amount"]
    return b
print(balance(events))  # 70
```

상태를 직접 저장하는 대신 이벤트 합으로 계산합니다. 따라서 과거 어느 시점도 재현할 수 있습니다.

### 5단계 — CQRS 읽기 모델

```python
# 5_cqrs.py
read_model = {"balance": 0}
def project(event):
    if event["type"] == "deposit": read_model["balance"] += event["amount"]
    elif event["type"] == "withdraw": read_model["balance"] -= event["amount"]
```

쓰기는 이벤트를 중심으로, 읽기는 미리 투영한 모델을 중심으로 분리합니다. 두 경로를 나누면 각각 최적화가 쉬워집니다.

## 이 코드에서 먼저 봐야 할 점

- 큐가 파일이 되는 순간 메시지는 내구성과 재생 가능성을 얻습니다.
- exactly-once는 큐만의 성질이 아니라 큐와 멱등적 소비자의 조합입니다.
- 이벤트 소싱에서는 이력이 본질이고, 스냅샷은 최적화일 뿐입니다.
- 읽기 모델은 언제든 다시 만들 수 있는 파생물입니다.

## 자주 하는 실수 5가지

1. **broker만으로 exactly-once가 보장된다고 믿습니다.** 소비자 멱등성이 함께 필요합니다.
2. **partition을 과도하게 많이 둡니다.** rebalance 비용과 메타데이터가 폭증합니다.
3. **이벤트를 수정 가능한 데이터처럼 다룹니다.** 기록된 이벤트는 바꾸지 않습니다.
4. **스냅샷 없이 매번 대규모 재생을 합니다.** 주기적 스냅샷이 필요합니다.
5. **읽기 모델을 진실의 원천으로 착각합니다.** 진실은 언제나 이벤트 로그에 있습니다.

## 실무에서는 이렇게 드러납니다

Kafka는 가장 널리 쓰이는 분산 append-only log 기반 스트리밍 백본입니다. RabbitMQ와 AWS SQS는 전통적인 메시지 큐에 가깝습니다. 이벤트 소싱은 금융, 주문, 감사 추적이 중요한 도메인에서 자주 채택됩니다. CQRS는 읽기와 쓰기 부하 특성이 크게 다른 시스템에서 빛을 발합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 큐를 넣기 전에 해당 흐름이 정말 비동기여도 되는지 먼저 확인합니다.
- 큐 기술을 고르기 전에 소비자 멱등성을 먼저 설계합니다.
- offset commit의 책임 주체를 명확히 적어 둡니다.
- 이벤트 스키마 버전 전략을 첫날부터 정합니다.
- 읽기 모델 재구성 시간을 SLO로 관리합니다.

## 체크리스트

- [ ] at-most-once, at-least-once, exactly-once를 각각 한 줄로 설명할 수 있는가?
- [ ] 이벤트 소싱이 감사 추적에 강한 이유를 설명할 수 있는가?
- [ ] consumer group과 partition의 관계를 설명할 수 있는가?
- [ ] CQRS가 읽기와 쓰기 경로를 왜 분리하는지 말할 수 있는가?
- [ ] 멱등성을 보장하는 패턴 하나를 바로 떠올릴 수 있는가?

## 연습 문제

1. 주문 시스템을 이벤트 소싱으로 설계하고 핵심 이벤트 다섯 개의 스키마를 적어 보세요.
2. at-least-once와 멱등적 소비자의 조합이 왜 사실상 exactly-once에 가깝게 동작하는지 설명해 보세요.
3. Kafka의 partition 수를 정할 때 고려할 기준 두 가지를 적어 보세요.

## 정리와 다음 글

메시지 큐와 이벤트 소싱은 분산 시스템에서 시간을 다루는 대표적인 도구입니다. 다음 글에서는 여러 노드에 걸친 트랜잭션, 즉 distributed transaction이 왜 어려운지와 현실적인 해법을 다룹니다.

<!-- toc:begin -->
- [분산 시스템이란 무엇인가?](./01-what-is-a-distributed-system.md)
- [failure model](./02-failure-model.md)
- [RPC와 message passing](./03-rpc-and-message-passing.md)
- [consistency와 CAP](./04-consistency-and-cap.md)
- [replication](./05-replication.md)
- [consensus와 Raft](./06-consensus-and-raft.md)
- [leader election](./07-leader-election.md)
- **message queue와 event sourcing (현재 글)**
- distributed transaction (예정)
- 운영 가능한 분산 시스템 패턴 (예정)
<!-- toc:end -->

## 참고 자료

- [Apache Kafka documentation](https://kafka.apache.org/documentation/)
- [Event Sourcing — Martin Fowler](https://martinfowler.com/eaaDev/EventSourcing.html)
- [CQRS — Martin Fowler](https://martinfowler.com/bliki/CQRS.html)
- [Designing Data-Intensive Applications — chapter 11](https://dataintensive.net/)

Tags: Computer Science, Distributed Systems, MessageQueue, EventSourcing, Kafka, CQRS
