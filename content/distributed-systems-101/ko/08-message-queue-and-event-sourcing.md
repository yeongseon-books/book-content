---
series: distributed-systems-101
episode: 8
title: "Distributed Systems 101 (8/10): 메시지 큐와 이벤트 소싱"
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
  - MessageQueue
  - EventSourcing
  - Kafka
  - CQRS
seo_description: 메시지 큐를 활용한 결합 해소와 전달 보장 전략, 이벤트 소싱과 CQRS 패턴을 통한 상태 관리 및 시스템 확장 방법을 상세히 정리합니다.
last_reviewed: '2026-05-15'
---

# Distributed Systems 101 (8/10): 메시지 큐와 이벤트 소싱

직접 호출은 참여하는 모든 서비스가 같은 순간에 건강해야 한다는 조건을 강하게 묶습니다. 반대로 큐와 로그를 사이에 두면 한쪽은 지금 끝내고, 다른 쪽은 나중에 따라와도 되며, 그 사이의 이력을 보존할 수 있습니다.

이 글은 Distributed Systems 101 시리즈의 여덟 번째 글입니다.

여기서는 메시지 큐와 이벤트 로그를 통해 시간이 어떻게 설계 도구가 되는지, 그리고 replay와 idempotency가 왜 운영 언어가 되는지 설명합니다.

## 먼저 던지는 질문

- 메시지 큐는 어떤 결합 해소와 전달 보장을 제공할까요?
- at-most-once, at-least-once, exactly-once는 각각 무엇을 뜻할까요?
- 이벤트 소싱은 무엇이며 CQRS와는 어떤 관계일까요?

## 큰 그림

![Distributed Systems 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/distributed-systems-101/08/08-01-concept-at-a-glance.ko.png)

*Distributed Systems 101 8장 흐름 개요*

## 왜 중요한가

서비스 간 직접 호출은 가용성과 지연 시간을 강하게 묶습니다. 큐를 사이에 두면 한쪽의 생존 여부가 다른 쪽의 즉시 동작을 결정하지 않게 됩니다. 이벤트 소싱은 한 단계 더 나아가 상태를 이벤트의 합으로 정의하므로, 이력과 재생이 시스템의 본질이 됩니다.

> 큐는 시간을 분리하고, 이벤트는 진실의 원천을 분리합니다.

## 한눈에 보는 개념

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

## 운영 시나리오: consumer lag과 재생 복구

큐의 진짜 시험대는 소비자가 뒤처질 때입니다.

1. 생산자는 초당 2,000개의 주문 이벤트를 계속 append합니다.
2. 한 consumer group 인스턴스가 재시작되며 3분 동안 offset commit을 멈춥니다.
3. lag은 커지지만 생산자는 계속 성공합니다. 로그가 시간을 흡수하기 때문입니다.
4. 소비자가 돌아오면 마지막 commit offset부터 backlog를 재생합니다.
5. 재시작 경계에서 같은 메시지를 두 번 볼 수 있으므로 멱등성 키가 복구의 안전성을 결정합니다.

그래서 운영에서는 lag, replay 완료 시간, 마지막 offset commit 시각을 핵심 메트릭으로 봅니다. 이 신호가 없으면 큐는 과부하를 한동안 숨긴 뒤, 오래된 읽기 모델이나 중복 부작용으로 문제를 드러냅니다.

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

- **메시지 큐는 어떤 결합 해소와 전달 보장을 제공할까요?**
  - 본문의 기준은 메시지 큐와 이벤트 소싱를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **at-most-once, at-least-once, exactly-once는 각각 무엇을 뜻할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **이벤트 소싱은 무엇이며 CQRS와는 어떤 관계일까요?**
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
- **메시지 큐와 이벤트 소싱 (현재 글)**
- 분산 트랜잭션 (예정)
- 운영 가능한 분산 시스템 패턴 (예정)

<!-- toc:end -->

## 참고 자료

- [Apache Kafka documentation](https://kafka.apache.org/documentation/)
- [Event Sourcing — Martin Fowler](https://martinfowler.com/eaaDev/EventSourcing.html)
- [CQRS — Martin Fowler](https://martinfowler.com/bliki/CQRS.html)
- [Designing Data-Intensive Applications — chapter 11](https://dataintensive.net/)
- [Kafka consumer design](https://docs.confluent.io/platform/current/clients/consumer.html)

Tags: Computer Science, Distributed Systems, MessageQueue, EventSourcing, Kafka, CQRS
