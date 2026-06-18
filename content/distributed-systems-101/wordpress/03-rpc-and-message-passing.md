---
series: distributed-systems-101
episode: 3
title: "바이브코딩을 위한 분산 시스템 기초 (3/10): RPC와 메시지 전달"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - 분산시스템
  - RPC
  - 메시지큐
  - 비동기
  - 멱등성
language: ko
---

# 바이브코딩을 위한 분산 시스템 기초 (3/10): RPC와 메시지 전달

이 글은 **바이브코딩을 위한 분산 시스템 기초** 시리즈의 3편입니다. AI가 만든 서비스를 스케일하려면 서비스 간 통신 모델을 선택하는 기준을 알아야 합니다. RPC와 메시지 전달 중 어느 것을 쓰느냐에 따라 장애 전파 범위와 사용자 경험이 완전히 달라집니다.

---

AI에게 "주문 서비스와 결제 서비스를 연결해줘"라고 하면 대부분 HTTP 호출 코드를 만들어 줍니다. 이 방식은 단순하지만, 결제 서비스가 느려지는 순간 주문 서비스 전체가 함께 느려집니다. 언제 직접 호출하고 언제 큐를 사이에 둬야 할지 기준이 없으면 서비스는 약한 고리 하나에 의해 전체가 무너집니다.

서비스를 나누고 나면 다음 질문은 거의 항상 같습니다. "이 둘은 어떻게 말하게 할 것인가?"

> "통신 모델은 시스템의 결합도를 결정합니다. RPC는 양방향 계약이고, 메시지 전달은 중간 저장소를 둔 단방향 흐름입니다."

## 이 글에서 다룰 질문들

- RPC와 메시지 전달은 각각 무엇이며 어떻게 다를까요?
- 동기와 비동기, 어느 경계에서 어떤 방식을 선택해야 할까요?
- 깊은 RPC 체인이 왜 위험한지 코드로 확인할 수 있을까요?
- AI가 만든 서비스에서 메시지 큐를 어디에 넣어야 할까요?
- exactly-once는 왜 허상이고, 현실적인 답은 무엇일까요?

---

## 바이브코딩과 통신 모델: AI가 선호하는 패턴의 함정

AI는 대부분 HTTP REST 호출로 서비스 간 통신 코드를 작성합니다. 이 패턴은 직관적이지만 서비스 체인이 길어지면 위험해집니다.

### Before: AI가 만든 직렬 RPC 체인

```python
# AI가 만들어 준 주문 처리 — 모든 호출이 직렬 RPC
def process_order(order_id: str):
    # 모든 서비스가 동시에 건강해야 함
    inventory = requests.post(f"{INVENTORY_URL}/deduct", timeout=2)  # 100ms
    payment   = requests.post(f"{PAYMENT_URL}/charge",   timeout=3)  # 200ms
    shipping  = requests.post(f"{SHIPPING_URL}/create",  timeout=2)  # 150ms
    notify    = requests.post(f"{NOTIFY_URL}/send",      timeout=1)  # 50ms
    return {"ok": True}  # 총 500ms + 재시도 시간
```

배송 서비스가 느려지면 사용자는 주문 응답을 받을 때까지 기다려야 합니다. 이메일 발송이 실패해도 전체 주문이 실패합니다.

### After: 사용자 경로와 후속 처리를 분리

```python
# 즉시 응답이 필요한 것(RPC)과 나중에 해도 되는 것(메시지)을 분리
from uuid import uuid4

def process_order(order_id: str, customer_id: str, amount: int):
    # 1. 동기 RPC: 즉시 결과가 필요한 것
    stock = inventory_client.check(order_id, timeout=1.0)
    if not stock.available:
        return {"error": "품절"}

    # 2. 로컬 저장: 주문 상태 기록
    db.save_order(order_id, status="pending")

    # 3. 비동기 메시지: 시간이 걸려도 되는 것
    queue.publish("order.created", {
        "order_id": order_id,
        "customer_id": customer_id,
        "amount": amount,
    })

    # 4. 즉시 응답: 사용자는 기다리지 않아도 됨
    return {"order_id": order_id, "status": "accepted"}

# 결제/배송/이메일은 별도 worker가 큐에서 꺼내 처리
```

---

## RPC vs 메시지 전달: 결합도의 차이

| 특성 | RPC | 메시지 전달 |
|------|-----|-----------|
| 응답 방식 | 동기 — 응답 대기 | 비동기 — 즉시 반환 |
| 결합도 | 강함 — 수신자가 살아 있어야 함 | 약함 — 큐가 버퍼 역할 |
| 장애 전파 | 수신자 지연이 발신자에 전파 | 큐가 전파 차단 |
| 적합한 용도 | 즉시 결과가 필요한 경우 | 지연을 허용하는 작업 |
| 대표 기술 | gRPC, REST, JSON-RPC | Kafka, RabbitMQ, SQS |

### 통신 방식 선택 기준

```
사용자가 즉시 결과를 봐야 하는가?
├── 예 → 동기 RPC
│   └── 체인 깊이 > 2? → 중간에 비동기 경계 삽입 고려
└── 아니오 → 비동기 메시지
    ├── 순서가 중요한가? → 파티션 키 기반 큐 (Kafka)
    └── 순서 무관? → 작업 큐 (RabbitMQ, SQS)
```

---

## 자주 하는 실수

| 실수 | 결과 | 올바른 접근 |
|------|------|------------|
| 모든 것을 RPC로 연결 | 체인이 길어지며 장애 면적 폭발 | 즉시 응답 불필요한 작업은 큐로 분리 |
| exactly-once를 그대로 믿음 | 브로커 재시작 시 중복 발생 | at-least-once + 멱등성 소비자 조합 |
| 멱등성 키 생략 | 재시도 한 번이 중복 결제 유발 | 첫 커밋부터 멱등성 키 설계 포함 |
| DLQ 없이 운영 | 처리 실패 메시지가 사라짐 | Dead Letter Queue와 재시도 정책 설정 |
| 무한 재시도 | 순간 장애가 영구 부하로 전환 | 최대 재시도 횟수 + 지수 백오프 |

---

## AI 팁: AI가 만든 서비스에 메시지 큐를 도입하는 법

1. **지연 허용 목록 작성**: 이메일 발송, 통계 집계, 외부 알림 등 실시간이 아니어도 되는 작업을 목록으로 만드세요.
2. **AI에게 분리 요청**: "결제와 이메일 발송을 분리하고 이메일은 Kafka 메시지로 발행하도록 수정해줘"
3. **멱등성 키 추가 요청**: "메시지 소비자에 idempotency_key 기반 중복 처리 방지 로직을 추가해줘"
4. **DLQ 설정 요청**: "최대 3회 재시도 후 실패하면 dead letter queue로 보내도록 설정해줘"

```python
# 멱등성을 갖춘 메시지 소비자 예시
seen_keys = set()  # 실제로는 Redis나 DB에 저장

def consume_message(msg: dict):
    key = msg["idempotency_key"]
    if key in seen_keys:
        return  # 이미 처리한 메시지 — 무시
    seen_keys.add(key)
    process(msg)  # 실제 처리
```

---

## 실전 체크리스트

- [ ] RPC와 메시지 전달의 차이를 한 줄로 설명할 수 있다
- [ ] 깊은 RPC 체인이 왜 위험한지 설명할 수 있다
- [ ] at-least-once와 exactly-once의 의미를 알고 있다
- [ ] 멱등성 키를 설계해봤다
- [ ] DLQ가 무엇이며 언제 쓰는지 말할 수 있다
- [ ] AI가 만든 서비스에서 큐로 분리할 만한 호출을 찾아봤다

---

## 처음 질문으로 돌아가기

- **RPC와 메시지 전달은 각각 무엇이며 어떻게 다를까요?**
  RPC는 응답을 기다리는 직접 호출이고, 메시지 전달은 브로커를 통해 비동기로 전달하는 방식입니다. RPC는 강한 결합, 메시지는 약한 결합을 만듭니다.

- **AI가 만든 서비스에서 메시지 큐를 어디에 넣어야 할까요?**
  사용자에게 즉시 결과를 보여주지 않아도 되는 작업, 체인 깊이가 3 이상인 경우, 장애 전파를 차단해야 하는 경계에 큐를 넣으면 됩니다.

- **exactly-once는 왜 허상이고, 현실적인 답은 무엇일까요?**
  브로커와 소비자 사이에서 완전한 exactly-once는 극도로 비쌉니다. 현실적인 답은 at-least-once 브로커 + 멱등성 소비자 조합입니다.

---

## 정리

RPC와 메시지 전달은 동기와 비동기, 결합도와 회복력을 서로 다르게 교환하는 두 모델입니다. AI가 만든 직렬 RPC 체인을 적절한 메시지 경계로 나누면 장애 전파를 막고 사용자 응답을 빠르게 할 수 있습니다. 다음 글에서는 데이터가 여러 노드에 놓일 때 생기는 가장 큰 트레이드오프인 일관성과 CAP를 다룹니다.

---

## 참고 자료

- [Remote procedure call (Wikipedia)](https://en.wikipedia.org/wiki/Remote_procedure_call)
- [Message passing (Wikipedia)](https://en.wikipedia.org/wiki/Message_passing)
- [gRPC documentation](https://grpc.io/docs/)
- [Apache Kafka documentation](https://kafka.apache.org/documentation/)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 분산 시스템 기초 (1/10): 분산 시스템이란 무엇인가?
- 바이브코딩을 위한 분산 시스템 기초 (2/10): 장애 모델
- **바이브코딩을 위한 분산 시스템 기초 (3/10): RPC와 메시지 전달 (현재 글)**
- 바이브코딩을 위한 분산 시스템 기초 (4/10): 일관성과 CAP
- 바이브코딩을 위한 분산 시스템 기초 (5/10): 복제
- 바이브코딩을 위한 분산 시스템 기초 (6/10): 합의와 Raft
- 바이브코딩을 위한 분산 시스템 기초 (7/10): 리더 선출
- 바이브코딩을 위한 분산 시스템 기초 (8/10): 메시지 큐와 이벤트 소싱
- 바이브코딩을 위한 분산 시스템 기초 (9/10): 분산 트랜잭션
- 바이브코딩을 위한 분산 시스템 기초 (10/10): 운영 가능한 분산 패턴
<!-- toc:end -->

Tags: 바이브코딩, 분산시스템, RPC, 메시지큐, 비동기, 멱등성
