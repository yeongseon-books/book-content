---
series: distributed-systems-101
episode: 3
title: "Distributed Systems 101 (3/10): RPC와 메시지 전달"
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
  - RPC
  - Messaging
  - Async
  - Idempotency
seo_description: 분산 시스템의 핵심인 RPC와 메시지 전달의 차이를 동기/비동기 관점에서 구조적으로 비교하고 상황별 선택 기준을 제시합니다.
last_reviewed: '2026-05-15'
---

# Distributed Systems 101 (3/10): RPC와 메시지 전달

서비스를 나누고 나면 다음 질문은 거의 항상 같습니다. "이 둘은 어떻게 말하게 할 것인가?" 응답을 기다리는 RPC를 쓸지, 큐를 사이에 둔 비동기 흐름을 쓸지에 따라 지연 예산과 장애 전파 범위가 완전히 달라집니다.

이 글은 Distributed Systems 101 시리즈의 세 번째 글입니다.

여기서는 RPC와 메시지 전달을 각각 하나의 통신 계약으로 보고, 어느 경계에서 어떤 방식을 택해야 하는지 선택 기준을 세웁니다.

## 먼저 던지는 질문

- RPC와 메시지 전달은 각각 무엇이며 어떻게 다를까요?
- 동기와 비동기, 요청-응답과 발행-구독은 어디서 갈릴까요?
- 두 모델은 각각 어떤 장단점이 있고 어디에 어울릴까요?

## 큰 그림

![Distributed Systems 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/distributed-systems-101/03/03-01-concept-at-a-glance.ko.png)

*Distributed Systems 101 3장 흐름 개요*

## 왜 중요한가

서비스를 분리한 뒤 가장 먼저 내려야 하는 결정 중 하나는 어떻게 통신할 것인가입니다. 이 선택이 지연 예산, 장애 전파 범위, 운영 복잡도를 함께 결정합니다. 잘못 고르면 한 노드의 지연이 전체 RPC 체인을 잡아끌고, 반대로 추적 불가능한 메시지 흐름이 생길 수도 있습니다.

> 통신 모델은 시스템의 결합도를 결정합니다.

## 한눈에 보는 개념

RPC는 양방향 계약이고, 메시지 전달은 중간 저장소를 둔 단방향 흐름입니다.

## 핵심 용어

- **RPC (Remote Procedure Call)**: 원격 함수를 로컬 함수처럼 호출하는 방식입니다. gRPC, JSON-RPC가 대표적입니다.
- **Message passing**: 생산자가 브로커에 메시지를 넣고 소비자가 나중에 가져가는 방식입니다. Kafka, RabbitMQ가 대표적입니다.
- **Synchronous**: 응답이 올 때까지 기다립니다.
- **Asynchronous**: 응답을 기다리지 않고 다음 작업으로 넘어갑니다.
- **At-least-once / exactly-once**: 브로커가 제공하려는 전달 보장 수준입니다.

## Before / After

**Before — 모든 호출을 RPC로 설계**

```text
service A -> B -> C -> D: if D slows down, A's response slows
```

**After — 중요한 경계는 메시지로 분리**

```text
A drops a message and returns; D processes asynchronously
```

이 전환으로 장애 전파 범위를 줄이고 사용자 응답 예산을 더 촘촘히 관리할 수 있습니다.

## 실습: 두 모델을 한 화면에 놓고 보기

### 1단계 — RPC(FastAPI)

```python
# 1_rpc_server.py
from fastapi import FastAPI
app = FastAPI()
@app.post("/charge")
def charge(amount: int):
    # process payment synchronously
    return {"ok": True, "id": "txn_1"}
```

```python
# 1_rpc_client.py
import requests
r = requests.post("http://127.0.0.1:8000/charge", json={"amount": 100}, timeout=2)
print(r.json())
```

응답이 도착해야 다음 줄이 실행됩니다. 실제로는 거의 함수 호출과 같은 감각입니다.

### 2단계 — 메시지 전달(메모리 큐)

```python
# 2_queue.py
from queue import Queue
import threading, time

q = Queue()

def consumer():
    while True:
        msg = q.get()
        time.sleep(0.5)
        print("processed:", msg)

threading.Thread(target=consumer, daemon=True).start()
q.put({"amount": 100, "id": "txn_1"})
print("producer returned immediately")
```

생산자는 즉시 반환되고, 소비자는 자기 속도로 큐를 비웁니다.

### 3단계 — RPC 체인의 위험

```python
# 3_chain.py (pseudocode)
def order():
    inv = rpc_inventory()    # 100ms
    pay = rpc_payment()      # 200ms
    ship = rpc_shipping()    # 150ms
    return ok                # total 450ms plus retry/timeout
```

모든 단계가 살아 있어야 응답 하나가 돌아옵니다. 한 노드가 느려지면 전체 호출이 함께 느려집니다.

### 4단계 — 비동기와 큐로 분리

```python
# 4_async.py (pseudocode)
def order():
    save_order_local()
    publish("order.created", payload)
    return "accepted"  # respond immediately
# separate workers handle inventory/payment/shipping
```

사용자는 빠른 응답을 받고, 느린 하위 단계는 뒤에서 처리됩니다.

### 5단계 — 전달 보장과 중복 처리

```python
# 5_dedup.py
seen = set()
def consume(msg):
    if msg["id"] in seen:
        return  # idempotent: ignore duplicates
    seen.add(msg["id"])
    process(msg)
```

대부분의 브로커는 at-least-once를 전제로 하므로, 소비자는 멱등성 키로 중복을 흡수해야 합니다.

## 이 코드에서 먼저 봐야 할 점

- RPC는 기다림 자체가 강한 결합을 만듭니다.
- 메시지 전달은 지금 당장 끝낼 필요가 없는 작업에 잘 맞습니다.
- 체인이 깊어질수록 RPC의 위험은 커집니다.
- exactly-once는 거의 항상 허상이고, 현실적인 답은 멱등적 소비자입니다.

## 자주 하는 실수 5가지

1. **모든 것을 RPC로 만듭니다.** 체인이 길어지며 지연과 장애 면적이 폭발합니다.
2. **모든 것을 큐 기반으로 만듭니다.** 즉시 응답이 필요한 사용자 경로가 불편해집니다.
3. **exactly-once를 그대로 믿습니다.** 현실은 브로커 보장과 멱등성 소비자의 조합입니다.
4. **멱등성 키를 생략합니다.** 재시도 한 번이 중복 결제로 이어질 수 있습니다.
5. **타임아웃과 재시도를 클라이언트에만 둡니다.** 브로커 쪽 DLQ와 재시도 정책도 함께 필요합니다.

## 실무에서는 이렇게 드러납니다

즉시 응답이 필요한 사용자 경로는 RPC를 사용하고, 메일 발송이나 분석처럼 오래 걸리는 작업은 큐로 넘깁니다. 많은 마이크로서비스 아키텍처는 내부 모듈 간 호출은 RPC로, 도메인 경계는 메시지로 나눕니다. Event sourcing과 CQRS는 이 메시지 모델을 끝까지 밀어붙인 설계라고 볼 수 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 정말 동기 응답이 필요한지부터 먼저 묻습니다.
- RPC 체인의 깊이를 제한합니다.
- 첫 커밋부터 멱등성 키를 설계에 넣습니다.
- 브로커는 기본적으로 at-least-once라고 가정합니다.
- DLQ와 재시도 정책을 운영 책임의 일부로 봅니다.

## 체크리스트

- [ ] RPC와 메시지 전달의 차이를 한 줄로 설명할 수 있는가?
- [ ] 깊은 RPC 체인이 왜 위험한지 설명할 수 있는가?
- [ ] at-least-once와 exactly-once의 의미를 알고 있는가?
- [ ] 멱등성 키를 설계해 본 적이 있는가?
- [ ] DLQ가 무엇이며 언제 쓰는지 말할 수 있는가?

## 연습 문제

1. 현재 서비스에서 RPC를 메시지로 바꿀 만한 호출 하나를 찾아 이유를 설명해 보세요.
2. 멱등성 키를 사용하는 결제 API를 한 단락으로 설계해 보세요.
3. at-least-once 전달에서 안전한 소비자가 갖춰야 할 조건 세 가지를 적어 보세요.

## 정리와 다음 글

RPC와 메시지 전달은 동기와 비동기, 결합도와 회복력을 서로 다르게 교환하는 두 모델입니다. 다음 글에서는 데이터가 여러 노드에 놓이는 순간 바로 등장하는 가장 큰 트레이드오프, 일관성과 CAP를 다룹니다.


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

- **RPC와 메시지 전달은 각각 무엇이며 어떻게 다를까요?**
  - 본문의 기준은 RPC와 메시지 전달를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **동기와 비동기, 요청-응답과 발행-구독은 어디서 갈릴까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **두 모델은 각각 어떤 장단점이 있고 어디에 어울릴까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Distributed Systems 101 (1/10): 분산 시스템이란 무엇인가?](./01-what-is-a-distributed-system.md)
- [Distributed Systems 101 (2/10): 장애 모델](./02-failure-model.md)
- **RPC와 메시지 전달 (현재 글)**
- 일관성과 CAP (예정)
- 복제 (예정)
- 합의와 Raft (예정)
- 리더 선출 (예정)
- 메시지 큐와 이벤트 소싱 (예정)
- 분산 트랜잭션 (예정)
- 운영 가능한 분산 시스템 패턴 (예정)

<!-- toc:end -->

## 참고 자료

- [Remote procedure call (Wikipedia)](https://en.wikipedia.org/wiki/Remote_procedure_call)
- [Message passing (Wikipedia)](https://en.wikipedia.org/wiki/Message_passing)
- [gRPC documentation](https://grpc.io/docs/)
- [Apache Kafka documentation](https://kafka.apache.org/documentation/)

Tags: Computer Science, Distributed Systems, RPC, Messaging, Async, Idempotency
