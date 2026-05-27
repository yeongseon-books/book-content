---
series: distributed-systems-101
episode: 9
title: "Distributed Systems 101 (9/10): 분산 트랜잭션"
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
  - Transactions
  - TwoPhaseCommit
  - Saga
  - Idempotency
seo_description: 2PC, Saga, Outbox 패턴과 멱등성 설계를 통해 여러 서비스에 걸친 분산 트랜잭션의 정합성을 유지하는 현실적인 해법을 제시합니다.
last_reviewed: '2026-05-15'
---

# Distributed Systems 101 (9/10): 분산 트랜잭션

분산 트랜잭션의 진짜 난점은 모두가 정상일 때가 아닙니다. 한쪽은 이미 커밋했고 다른 쪽은 타임아웃 난 상태에서, 비즈니스는 여전히 하나의 결과를 요구하는 그 순간이 문제를 만듭니다.

이 글은 Distributed Systems 101 시리즈의 9번째 글입니다.

여기서는 2PC의 강한 모델과 Saga, outbox, 멱등적 복구 같은 현실적 대안을 비교해, 부분 실패를 어떻게 살아남는지에 초점을 맞춥니다.

![Distributed Systems 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/distributed-systems-101/09/09-01-concept-at-a-glance.ko.png)
*Distributed Systems 101 9장 흐름 개요*

## 먼저 던지는 질문

- 단일 노드 트랜잭션과 분산 트랜잭션은 무엇이 다를까요?
- 2-phase commit은 어떻게 동작하고 어디서 약할까요?
- Saga의 핵심인 보상 트랜잭션은 무엇일까요?

## 왜 중요한가

마이크로서비스와 다중 저장소 구조가 늘수록 두 시스템을 하나의 비즈니스 흐름으로 묶어야 하는 장면이 많아집니다. 하지만 단일 데이터베이스에서 비교적 싸게 얻을 수 있는 ACID는 여러 노드를 넘는 순간 훨씬 비싸지거나, 아예 성립하기 어려워집니다. 분산 트랜잭션은 결국 명시적인 트레이드오프 위에서 하는 설계입니다.

> 분산 트랜잭션은 ACID의 모방이 아니라 복구 가능한 비일관성의 설계입니다.

## 한눈에 보는 개념

coordinator가 두 참가자에게 prepare를 보내고, 둘 다 yes를 보냈을 때만 commit합니다. 이것이 2PC의 핵심입니다.

## 핵심 용어

- **2PC**: prepare와 commit 두 단계로 모든 참여자의 동의를 모으는 프로토콜입니다.
- **Saga**: 여러 로컬 트랜잭션을 보상 작업으로 되돌리는 패턴입니다.
- **Compensation**: 이미 커밋된 작업을 비즈니스 의미상 되돌리는 동작입니다.
- **Outbox**: 데이터베이스 쓰기와 메시지 발행을 같은 트랜잭션 안에 묶기 위한 테이블 패턴입니다.
- **Idempotency**: 같은 요청을 여러 번 실행해도 결과가 한 번 실행한 것과 같게 유지되는 성질입니다.

## 적용 전후 비교
**Before — 서비스 간 직접 호출**

```text
service A succeeds / service B fails -> data inconsistency
```

**After — Saga와 보상**

```text
service A succeeds / service B fails -> compensate A -> consistent end state
```

분산 시스템에서 롤백은 시간을 되돌리는 일이 아니라, 새로운 사건을 추가해 상태를 되돌리는 일에 가깝습니다.

## 실습: 분산 트랜잭션 패턴

### 1단계 — 단일 DB 트랜잭션

```python
# 1_single.py
import sqlite3
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE acct(id TEXT, bal INT)")
db.execute("INSERT INTO acct VALUES ('A', 100), ('B', 0)")
with db:
    db.execute("UPDATE acct SET bal=bal-30 WHERE id='A'")
    db.execute("UPDATE acct SET bal=bal+30 WHERE id='B'")
```

하나의 데이터베이스 안에서는 ACID만으로 충분합니다. 어려움은 그다음 단계부터 시작됩니다.

### 2단계 — 2PC(의사코드)

```python
# 2_2pc.py
def prepare(svc): return svc.prepare()    # yes/no
def commit(svc):  svc.commit()
def abort(svc):   svc.abort()
def two_pc(svcs):
    if all(prepare(s) for s in svcs):
        for s in svcs: commit(s)
    else:
        for s in svcs: abort(s)
```

모든 참여자가 yes라고 답했을 때만 commit합니다. coordinator가 중간에 죽으면 참가자들이 오래 잠길 수 있으므로 타임아웃과 복구 설계가 필수입니다.

### 3단계 — Saga(보상)

```python
# 3_saga.py
def book_flight():  return "F1"
def book_hotel():   raise RuntimeError("no room")
def cancel_flight(f): print(f"cancel {f}")

def saga():
    f = book_flight()
    try:
        h = book_hotel()
    except Exception:
        cancel_flight(f)
        raise
saga()
```

각 단계는 로컬에서 커밋되고, 중간에 실패하면 앞에서 성공한 단계를 의미상 되돌립니다.

### 4단계 — outbox 패턴

```python
# 4_outbox.py (pseudocode)
# 하나의 transaction 내부에서:
#   INSERT INTO orders ...
#   INSERT INTO outbox(event=...) VALUES (...)
# 별도 worker가 outbox를 읽어 message broker로 발행
```

데이터베이스 쓰기와 메시지 발행을 하나의 데이터베이스 트랜잭션으로 묶어 dual-write 문제를 피합니다.

### 5단계 — 멱등적 소비자

```python
# 5_idem.py
processed = set()
def apply(event):
    if event["id"] in processed: return
    processed.add(event["id"])
    # actual processing
```

분산 트랜잭션의 마지막 안전망입니다. 같은 메시지가 다시 와도 결과는 한 번만 반영됩니다.

## 운영 시나리오: 주문 저장은 성공했고 relay만 실패한 경우

현실에서 자주 터지는 사고는 트랜잭션 자체보다 커밋 뒤의 전달 경계에서 생깁니다.

1. 서비스가 하나의 로컬 트랜잭션 안에서 `orders`와 `outbox`를 함께 기록합니다.
2. API는 호출자에게 `201 Created`를 반환합니다.
3. outbox relay가 Kafka publish 전에 죽습니다.
4. 재시작한 relay는 outbox 테이블을 다시 훑어 아직 publish되지 않은 row를 전송합니다.
5. relay가 publish 뒤 상태 업데이트 전에 죽었다면, downstream은 같은 메시지를 두 번 볼 수 있습니다.

이 흐름 때문에 운영 계약은 "relay는 절대 실패하지 않는다"가 아니라 "at-least-once publish와 멱등적 소비자가 함께 안전하다"가 됩니다. outbox는 dual-write 문제를 없애는 것이 아니라, 복구 가능한 backlog 문제로 바꿉니다.

## 이 코드에서 먼저 봐야 할 점

- 2PC는 강하지만 lock이 길고 coordinator 장애에 취약합니다.
- Saga는 장애가 흔한 현실에 잘 맞지만, 보상의 의미는 도메인이 직접 정의해야 합니다.
- outbox는 두 시스템 동시 쓰기를 한 번의 DB 쓰기로 바꾸는 우회로입니다.
- 멱등성은 거의 모든 패턴 밑바닥에 깔린 공통 기반입니다.

## 자주 하는 실수 5가지

1. **마이크로서비스에서 2PC를 기본값처럼 씁니다.** 가용성과 성능이 크게 떨어집니다.
2. **보상 설계 없이 Saga를 시작합니다.** 부분 실패가 영구 불일치가 됩니다.
3. **DB 쓰기와 메시지 발행을 dual-write로 분리합니다.** 둘이 함께 성공함을 보장할 수 없습니다.
4. **2PC 타임아웃을 너무 짧게 둡니다.** false abort가 자주 발생합니다.
5. **멱등성을 빠뜨립니다.** 재시도 한 번이 중복 결제나 중복 차감으로 이어집니다.

## 실무에서는 이렇게 드러납니다

XA와 2PC는 여전히 일부 RDBMS 클러스터와 브로커에서 쓰입니다. 그러나 마이크로서비스의 결제, 예약, 주문 흐름에서는 Saga가 사실상 표준 패턴에 가깝습니다. Kafka와 데이터베이스를 함께 쓰는 환경에서는 outbox가 가장 흔한 현실적 해법입니다. Spanner나 CockroachDB 같은 글로벌 데이터베이스는 내부적으로 합의와 2PC를 결합해 사용자에게는 ACID처럼 보이게 만듭니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 이 흐름이 정말 원자적이어야 하는지부터 먼저 묻습니다.
- 가능하면 단일 DB 트랜잭션 안에 묶고, 외부 통지는 outbox로 분리합니다.
- Saga 보상이 실제 비즈니스 의미에서 가능한지 도메인 전문가와 확인합니다.
- 모든 실패 분기에는 운영 복구 절차나 자동화 스크립트를 붙입니다.
- 외부 호출에는 멱등성 키를 표준 장치로 둡니다.

## 체크리스트

- [ ] 2PC와 Saga의 차이를 한 줄로 설명할 수 있는가?
- [ ] outbox 패턴이 해결하는 문제가 무엇인지 말할 수 있는가?
- [ ] 보상 트랜잭션의 한계를 하나 설명할 수 있는가?
- [ ] 멱등성 키가 어디에 놓이는지 머릿속 그림이 있는가?
- [ ] 결제 흐름에서 어떤 패턴을 택할지 근거를 댈 수 있는가?

## 연습 문제

1. 항공권과 호텔 예약 흐름을 Saga로 설계하고 보상 단계를 적어 보세요.
2. dual-write와 outbox의 차이를 한 단락으로 설명해 보세요.
3. 멱등성 키 없이 결제를 재시도했을 때 왜 위험한지 시나리오를 만들어 보세요.

## 정리와 다음 글

분산 트랜잭션은 ACID를 그대로 복제하는 일이 아니라 결국 합의된 상태로 수렴하도록 설계하는 일입니다. 다음 마지막 글에서는 지금까지의 도구를 묶어 운영 가능한 분산 시스템 패턴으로 정리합니다.

## 실전 설계 확장: 2PC, Saga, Outbox, TCC

이제부터는 "분산 트랜잭션이 실제로 어떻게 깨지고 어떻게 복구되는가"를 패턴별로 구체화합니다. 핵심은 단일 정답을 찾는 것이 아니라, 도메인 제약과 장애 모델에 맞는 실패 계약을 선택하는 것입니다.

### 2PC 상세 흐름: 준비와 확정의 분리

2PC는 coordinator가 참여자(participant)에게 두 단계를 강제합니다.

1. **prepare 단계**: 각 참여자는 변경 가능 여부를 검사하고, 가능하면 로컬 잠금을 잡은 채 `YES`를 기록합니다.
2. **commit 단계**: coordinator는 모든 `YES`를 받았을 때만 전원 commit을 지시합니다.

아래 코드는 Flask 스타일 의사코드로, prepare 로그와 최종 결정 로그를 분리해 기록합니다.

```python
# 2pc_coordinator.py
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List

class Vote(str, Enum):
    YES = "YES"
    NO = "NO"

@dataclass
class ParticipantClient:
    name: str

    def prepare(self, tx_id: str, payload: dict) -> Vote:
        # 실제 구현에서는 HTTP/gRPC 호출
        return Vote.YES

    def commit(self, tx_id: str) -> None:
        pass

    def abort(self, tx_id: str) -> None:
        pass

class DecisionLog:
    def __init__(self) -> None:
        self.records: Dict[str, str] = {}

    def write(self, tx_id: str, state: str) -> None:
        self.records[tx_id] = state

    def read(self, tx_id: str) -> str | None:
        return self.records.get(tx_id)

def run_2pc(tx_id: str, payload: dict, participants: List[ParticipantClient], log: DecisionLog) -> str:
    log.write(tx_id, "PREPARING")
    votes: Dict[str, Vote] = {}

    for p in participants:
        vote = p.prepare(tx_id=tx_id, payload=payload)
        votes[p.name] = vote
        if vote == Vote.NO:
            log.write(tx_id, "ABORT")
            for pp in participants:
                pp.abort(tx_id)
            return "ABORT"

    log.write(tx_id, "COMMIT")
    for p in participants:
        p.commit(tx_id)
    return "COMMIT"
```

실무에서 중요한 포인트는 `PREPARING`과 `COMMIT/ABORT`가 모두 durable 로그여야 한다는 사실입니다. 메모리 상태만으로 운영하면 coordinator 재시작 후 결정을 잃어 in-doubt 상태를 과도하게 만들 수 있습니다.

### 2PC coordinator 장애 처리: in-doubt를 줄이는 설계

2PC의 대표 약점은 coordinator 단일 장애점입니다. 특히 참여자는 `prepare YES` 후 잠금을 잡고 기다리기 때문에, coordinator가 죽으면 애플리케이션 지연이 연쇄적으로 커집니다.

실무 복구 전략은 보통 세 층으로 분리합니다.

1. **결정 로그 복구**: coordinator 재기동 시 `PREPARING` 트랜잭션을 스캔합니다.
2. **참여자 질의**: 각 참여자에게 `tx_id` 최종 상태를 질의합니다.
3. **결정 재전파**: 다수 참여자가 `COMMITTED`면 commit 재전파, 아니면 abort 재전파를 수행합니다.

```python
# 2pc_recovery.py
def recover_pending_transactions(log, participants):
    for tx_id, state in log.records.items():
        if state != "PREPARING":
            continue

        participant_states = []
        for p in participants:
            participant_states.append(p.query_tx_state(tx_id))

        if "COMMITTED" in participant_states:
            log.write(tx_id, "COMMIT")
            for p in participants:
                p.commit(tx_id)
        else:
            log.write(tx_id, "ABORT")
            for p in participants:
                p.abort(tx_id)
```

여기서 핵심 운영 지표는 `in_doubt_count`, `prepare_lock_wait_ms`, `coordinator_recovery_seconds`입니다. 2PC를 선택했다면 기능 성공률보다 이 세 지표를 먼저 경보화해야 합니다.

### Saga: 오케스트레이션과 코레오그래피

Saga는 글로벌 잠금 대신 로컬 커밋 + 보상으로 정합성을 맞춥니다. 구현 방식은 두 가지가 널리 쓰입니다.

#### 오케스트레이션 방식

중앙 오케스트레이터가 단계 순서와 보상 순서를 명시적으로 관리합니다.

```python
# saga_orchestrator.py
from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

@app.post("/checkout")
def checkout(order_id: str, user_id: str, amount: int):
    reserve = requests.post("http://inventory/reserve", json={"order_id": order_id}).json()
    if reserve["status"] != "ok":
        raise HTTPException(status_code=409, detail="재고 부족")

    charge = requests.post(
        "http://payment/charge",
        json={"order_id": order_id, "user_id": user_id, "amount": amount},
    ).json()
    if charge["status"] != "ok":
        requests.post("http://inventory/release", json={"order_id": order_id})
        raise HTTPException(status_code=409, detail="결제 실패")

    ship = requests.post("http://shipping/create", json={"order_id": order_id}).json()
    if ship["status"] != "ok":
        requests.post("http://payment/refund", json={"order_id": order_id})
        requests.post("http://inventory/release", json={"order_id": order_id})
        raise HTTPException(status_code=409, detail="배송 생성 실패")

    return {"status": "completed", "order_id": order_id}
```

장점은 흐름 가시성이 높고 실패 분기가 한곳에 모인다는 사실입니다. 단점은 오케스트레이터가 비대해지면 배포 속도와 변경 충돌이 커진다는 사실입니다.

#### 코레오그래피 방식

중앙 제어자 없이 이벤트를 통해 각 서비스가 다음 단계를 수행합니다.

```python
# saga_choreography_payment_consumer.py
def on_inventory_reserved(event):
    order_id = event["order_id"]
    ok = try_charge_card(order_id=order_id, amount=event["amount"])
    if ok:
        publish("PaymentCharged", {"order_id": order_id})
    else:
        publish("PaymentFailed", {"order_id": order_id, "reason": "insufficient_funds"})

def on_shipping_failed(event):
    order_id = event["order_id"]
    refund(order_id=order_id)
    publish("PaymentRefunded", {"order_id": order_id})
```

장점은 서비스 자율성이 높고 중앙 병목이 줄어든다는 사실입니다. 단점은 전체 흐름 추적이 어려워 분산 트레이싱과 상관관계 키(correlation id)가 사실상 필수라는 사실입니다.

### Saga 보상 로직: 취소가 아니라 역방향 도메인 명령

보상 트랜잭션은 SQL rollback이 아닙니다. 이미 외부 세계에 반영된 결과를 비즈니스 의미로 상쇄하는 새 명령입니다. 따라서 "무조건 원복"이 아니라 "원복이 가능한 범위"를 먼저 정의해야 합니다.

예를 들어 결제 보상은 다음과 같이 제약을 가집니다.

- PG 승인 취소 가능 시간 창(예: 승인 후 10분 이내)
- 부분 환불 허용 여부
- 포인트, 쿠폰, 재고 예약의 역순 복구 규칙

```python
# compensation_policy.py
from datetime import datetime, timedelta

def compensate_payment(payment, now: datetime):
    if payment.status != "captured":
        return {"status": "noop", "reason": "이미 취소되었거나 미확정 상태입니다."}

    if now - payment.captured_at <= timedelta(minutes=10):
        cancel_authorization(payment.pg_tx_id)
        return {"status": "compensated", "mode": "void"}

    create_refund(payment.pg_tx_id, amount=payment.amount)
    return {"status": "compensated", "mode": "refund"}
```

운영에서 자주 실패하는 지점은 보상 자체가 다시 실패하는 경우입니다. 그래서 Saga 상태 저장소에는 `compensate_retry_count`, `last_error_code`, `next_retry_at`를 남기고 재시도 정책을 명시해야 합니다.

### 트랜잭셔널 아웃박스 구현: dual-write를 복구 가능한 backlog로 전환

Outbox의 목적은 "DB 반영"과 "메시지 발행"을 하나의 로컬 트랜잭션으로 묶어, 중간 장애를 재처리 가능한 형태로 바꾸는 것입니다.

```python
# outbox_schema.sql (개념 예시)
# CREATE TABLE outbox (
#   id TEXT PRIMARY KEY,
#   aggregate_type TEXT NOT NULL,
#   aggregate_id TEXT NOT NULL,
#   event_type TEXT NOT NULL,
#   payload_json TEXT NOT NULL,
#   status TEXT NOT NULL DEFAULT 'PENDING',
#   created_at TIMESTAMP NOT NULL,
#   published_at TIMESTAMP NULL
# );
```

```python
# outbox_writer.py
import json
import sqlite3
import uuid
from datetime import datetime

def create_order_with_outbox(db: sqlite3.Connection, order_id: str, user_id: str, amount: int):
    with db:
        db.execute(
            "INSERT INTO orders(id, user_id, amount, status) VALUES (?, ?, ?, 'CREATED')",
            (order_id, user_id, amount),
        )
        db.execute(
            "INSERT INTO outbox(id, aggregate_type, aggregate_id, event_type, payload_json, created_at) "
            "VALUES (?, 'order', ?, 'OrderCreated', ?, ?)",
            (
                str(uuid.uuid4()),
                order_id,
                json.dumps({"order_id": order_id, "user_id": user_id, "amount": amount}),
                datetime.utcnow().isoformat(),
            ),
        )
```

```python
# outbox_relay.py
def relay_batch(db, broker, batch_size: int = 100):
    rows = db.execute(
        "SELECT id, event_type, payload_json FROM outbox WHERE status='PENDING' ORDER BY created_at LIMIT ?",
        (batch_size,),
    ).fetchall()

    for row in rows:
        outbox_id, event_type, payload_json = row
        broker.publish(topic=event_type, payload=payload_json)
        with db:
            db.execute(
                "UPDATE outbox SET status='PUBLISHED', published_at=CURRENT_TIMESTAMP WHERE id=?",
                (outbox_id,),
            )
```

이 구조에서는 relay가 publish 직후 죽으면 중복 발행이 생길 수 있습니다. 따라서 소비자는 `event_id` 또는 `outbox_id` 기반 멱등성 저장소를 가져야 하며, 이것이 outbox와 항상 쌍으로 다뤄져야 하는 이유입니다.

### TCC 패턴: 강한 비즈니스 제어가 필요한 경우

TCC(Try-Confirm-Cancel)는 각 서비스가 명시적 예약 상태를 노출하는 패턴입니다.

- **Try**: 실제 확정 전 자원을 임시 예약합니다.
- **Confirm**: 모든 단계가 성공하면 예약을 확정합니다.
- **Cancel**: 중간 실패 시 예약을 해제합니다.

```python
# tcc_inventory.py
from fastapi import FastAPI, HTTPException

app = FastAPI()
reservations = {}

@app.post("/tcc/try")
def try_reserve(order_id: str, sku: str, qty: int):
    if not has_available_stock(sku, qty):
        raise HTTPException(status_code=409, detail="재고 부족")
    token = hold_stock(order_id=order_id, sku=sku, qty=qty)
    reservations[order_id] = token
    return {"status": "tried", "token": token}

@app.post("/tcc/confirm")
def confirm(order_id: str):
    token = reservations.get(order_id)
    if not token:
        return {"status": "already_confirmed_or_cancelled"}
    confirm_stock(token)
    reservations.pop(order_id, None)
    return {"status": "confirmed"}

@app.post("/tcc/cancel")
def cancel(order_id: str):
    token = reservations.get(order_id)
    if not token:
        return {"status": "already_confirmed_or_cancelled"}
    release_stock(token)
    reservations.pop(order_id, None)
    return {"status": "cancelled"}
```

TCC는 Saga보다 제어력이 높지만 서비스 구현 부담이 큽니다. 모든 참여자가 예약 상태 모델과 만료 정책을 제공해야 하기 때문입니다.

### 패턴 비교: 2PC vs Saga vs TCC

| 항목 | 2PC | Saga | TCC |
| --- | --- | --- | --- |
| 정합성 모델 | 강한 원자성 지향 | 최종 일관성 | 예약 후 확정 일관성 |
| 잠금/자원 점유 | 길어질 수 있음 | 짧음(로컬 커밋) | 예약 기간 동안 점유 |
| 장애 시 복잡도 | coordinator 복구가 핵심 | 보상 설계가 핵심 | 토큰/만료/중복 처리 |
| 성능/가용성 | 상대적으로 불리함 | 비교적 유리함 | 도메인 의존적 |
| 적합한 도메인 | 내부 시스템 간 강한 일관성 | 주문/예약/결제 등 서비스 경계 | 좌석, 재고, 한도처럼 예약이 중요한 도메인 |

의사결정 기준은 기술 선호가 아니라 비즈니스 실패 비용입니다. 실패했을 때 "잠시 지연"이 더 치명적인지, "보상 처리"가 더 치명적인지를 먼저 판단해야 합니다.

### 분산 트랜잭션 모니터링: in-doubt와 보상 실패를 먼저 본다

실패를 막을 수는 없지만, 오래 모르는 실패는 줄일 수 있습니다. 분산 트랜잭션 대시보드의 핵심 신호는 다음과 같습니다.

- `tx_in_doubt_total`: 2PC 준비 후 최종 결정이 없는 건수
- `tx_prepare_timeout_total`: prepare 단계 타임아웃 건수
- `saga_compensation_failed_total`: 보상 단계 최종 실패 건수
- `saga_compensation_retrying_total`: 재시도 중인 보상 건수
- `outbox_backlog_count`: 발행 대기 outbox 적체량
- `outbox_oldest_pending_seconds`: 가장 오래된 미발행 이벤트의 경과 시간

```yaml
alerts:
  - name: distributed_tx_in_doubt_spike
    expr: tx_in_doubt_total > 0
    for: 5m
    severity: critical
  - name: saga_compensation_failure
    expr: increase(saga_compensation_failed_total[10m]) > 3
    for: 2m
    severity: critical
  - name: outbox_backlog_growing
    expr: outbox_oldest_pending_seconds > 120
    for: 5m
    severity: warning
```

운영 런북에는 "어떤 버튼을 누르는가"까지 있어야 합니다. 예를 들어 `tx_in_doubt_total > 0`이면 coordinator 결정 로그 점검, 참여자 상태 질의, commit/abort 재전파 순서로 자동화 스크립트를 실행하도록 명시합니다. Saga 보상 실패는 재시도 한도를 넘은 건을 수동 큐로 보내고, 도메인 담당자가 환불/재고/알림 상태를 교차 확인하는 절차를 포함해야 합니다.

## 처음 질문으로 돌아가기

- **단일 노드 트랜잭션과 분산 트랜잭션은 무엇이 다를까요?**
  - 단일 노드 트랜잭션은 하나의 DB 로그와 잠금 체계 안에서 commit/rollback이 끝나지만, 분산 트랜잭션은 서비스 경계를 넘어 로컬 커밋, 메시지 전달, 재시도, 보상까지 포함한 운영 계약으로 완성됩니다. 그래서 "즉시 원자성" 대신 "복구 가능한 최종 일관성"을 설계해야 하며, outbox와 멱등성 같은 장치가 필수입니다.
- **2-phase commit은 어떻게 동작하고 어디서 약할까요?**
  - 2PC는 prepare에서 전원 동의를 받고 commit을 전파하는 두 단계로 동작합니다. 강점은 원자성 모델이 명확하다는 점이지만, coordinator 장애 시 참여자가 in-doubt로 잠길 수 있고 prepare 잠금이 길어지면 가용성과 지연이 급격히 나빠집니다. 그래서 결정 로그 내구성, 재기동 복구 로직, in-doubt 모니터링을 함께 설계해야 실전에서 버틸 수 있습니다.
- **Saga의 핵심인 보상 트랜잭션은 무엇일까요?**
  - 보상 트랜잭션은 데이터베이스 rollback이 아니라, 이미 발생한 비즈니스 결과를 역방향 명령으로 상쇄하는 동작입니다. 오케스트레이션과 코레오그래피 모두에서 보상 실패 재시도 정책, 만료 시간 창, 멱등 키를 명시해야 하며, 이 설계가 Saga의 성공 여부를 결정합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Distributed Systems 101 (1/10): 분산 시스템이란 무엇인가?](./01-what-is-a-distributed-system.md)
- [Distributed Systems 101 (2/10): 장애 모델](./02-failure-model.md)
- [Distributed Systems 101 (3/10): RPC와 메시지 전달](./03-rpc-and-message-passing.md)
- [Distributed Systems 101 (4/10): 일관성과 CAP](./04-consistency-and-cap.md)
- [Distributed Systems 101 (5/10): 복제](./05-replication.md)
- [Distributed Systems 101 (6/10): 합의와 Raft](./06-consensus-and-raft.md)
- [Distributed Systems 101 (7/10): 리더 선출](./07-leader-election.md)
- [Distributed Systems 101 (8/10): 메시지 큐와 이벤트 소싱](./08-message-queue-and-event-sourcing.md)
- **분산 트랜잭션 (현재 글)**
- 운영 가능한 분산 시스템 패턴 (예정)

<!-- toc:end -->

## 참고 자료

- [Two-phase commit — Wikipedia](https://en.wikipedia.org/wiki/Two-phase_commit_protocol)
- [Saga pattern — microservices.io](https://microservices.io/patterns/data/saga.html)
- [Transactional Outbox — microservices.io](https://microservices.io/patterns/data/transactional-outbox.html)
- [Designing Data-Intensive Applications — chapter 9](https://dataintensive.net/)
- [Life of a Cloud Spanner read-write transaction](https://cloud.google.com/spanner/docs/transactions)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/distributed-systems-101/ko)

Tags: Computer Science, Distributed Systems, Transactions, TwoPhaseCommit, Saga, Idempotency
