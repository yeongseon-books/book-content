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


![Distributed Systems 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/distributed-systems-101/08/08-01-concept-at-a-glance.ko.png)
*Distributed Systems 101 8장 흐름 개요*

## 먼저 던지는 질문

- 메시지 큐는 어떤 결합 해소와 전달 보장을 제공할까요?
- at-most-once, at-least-once, exactly-once는 각각 무엇을 뜻할까요?
- 이벤트 소싱은 무엇이며 CQRS와는 어떤 관계일까요?

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


## 실전 설계 확장: 메시지 큐와 이벤트 소싱 운영

앞선 실습이 큐와 이벤트 소싱의 핵심 감각을 잡는 단계였다면, 이 절은 실제 서비스 설계 문서에 들어가는 판단 기준을 다룹니다. 핵심은 기술 이름이 아니라 경계입니다. 어떤 경계에서 순서를 보장하고, 어떤 경계에서 재처리를 허용하며, 어떤 경계에서 스키마 호환성을 강제할지 미리 정하지 않으면 장애 때마다 동일한 논쟁을 반복하게 됩니다.

### Kafka와 RabbitMQ를 구조로 비교하기

둘 다 메시지를 전달하지만 내부 모델이 다르기 때문에 설계 결론도 달라집니다.

| 항목 | Kafka | RabbitMQ |
| --- | --- | --- |
| 기본 모델 | append-only 분산 로그 | exchange + queue 기반 라우팅 |
| 메시지 보관 | 토픽 보존 기간 동안 로그에 유지 | 소비 후 ack되면 큐에서 제거가 기본 |
| 재생(replay) | offset 이동으로 자연스럽게 지원 | 별도 재적재/재큐잉 전략 필요 |
| 소비 병렬성 | partition 단위 병렬 처리 | queue/consumer 채널 단위 병렬 처리 |
| 순서 보장 단위 | partition 내부 | 단일 queue 내부(재큐잉 시 깨질 수 있음) |
| 강점 | 이벤트 로그, 분석 파이프라인, 대용량 스트리밍 | 라우팅 유연성, 작업 큐, 복잡한 전달 토폴로지 |

설계에서 가장 중요한 질문은 "메시지를 전달하고 끝낼 것인가, 로그로 남겨 반복 소비할 것인가"입니다. 전달 중심이면 RabbitMQ가 단순해지고, 이력 중심이면 Kafka가 자연스럽습니다. 이벤트 소싱을 본격적으로 적용할 때 Kafka가 자주 선택되는 이유도 여기에 있습니다. 이벤트를 지우지 않고 남겨야 읽기 모델을 다시 만들 수 있기 때문입니다.

### 이벤트 저장소 구현 패턴

이벤트 소싱의 최소 단위는 "aggregate 단위 append-only 저장"입니다. 아래 예시는 FastAPI 서비스에서 주문 aggregate 이벤트를 PostgreSQL에 저장하는 전형적인 형태입니다.

```python
# app/event_store.py
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Connection


@dataclass
class DomainEvent:
    event_id: str
    aggregate_id: str
    aggregate_type: str
    event_type: str
    event_version: int
    payload: dict[str, Any]
    occurred_at: datetime


def append_event(
    conn: Connection,
    *,
    stream_id: str,
    expected_version: int,
    event: DomainEvent,
) -> int:
    row = conn.execute(
        text(
            """
            INSERT INTO event_store (
                stream_id,
                stream_version,
                event_id,
                aggregate_id,
                aggregate_type,
                event_type,
                event_version,
                payload,
                occurred_at
            )
            SELECT
                :stream_id,
                :next_version,
                :event_id,
                :aggregate_id,
                :aggregate_type,
                :event_type,
                :event_version,
                CAST(:payload AS jsonb),
                :occurred_at
            WHERE :expected_version = (
                SELECT COALESCE(MAX(stream_version), 0)
                FROM event_store
                WHERE stream_id = :stream_id
            )
            RETURNING stream_version
            """
        ),
        {
            "stream_id": stream_id,
            "next_version": expected_version + 1,
            "event_id": event.event_id,
            "aggregate_id": event.aggregate_id,
            "aggregate_type": event.aggregate_type,
            "event_type": event.event_type,
            "event_version": event.event_version,
            "payload": json.dumps(event.payload),
            "occurred_at": event.occurred_at.astimezone(timezone.utc),
            "expected_version": expected_version,
        },
    ).fetchone()

    if row is None:
        raise ValueError("concurrency_conflict")

    return int(row.stream_version)
```

이 패턴의 요점은 optimistic concurrency control입니다. `expected_version`이 맞는 경우에만 append를 허용하므로 동일 aggregate에 대한 경쟁 쓰기 충돌을 감지할 수 있습니다. 즉, 이벤트 저장소가 단순 로그 파일이 아니라 도메인 불변식을 지키는 경계가 됩니다.

다음은 최소 스키마 예시입니다.

```sql
CREATE TABLE event_store (
    id BIGSERIAL PRIMARY KEY,
    stream_id TEXT NOT NULL,
    stream_version BIGINT NOT NULL,
    event_id TEXT NOT NULL UNIQUE,
    aggregate_id TEXT NOT NULL,
    aggregate_type TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_version INT NOT NULL,
    payload JSONB NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(stream_id, stream_version)
);
```

`UNIQUE(stream_id, stream_version)`은 순서 보장을, `event_id UNIQUE`는 중복 적재 차단을 담당합니다. 이벤트 저장소를 운영할 때 이 두 제약은 사실상 필수입니다.

### 이벤트 로그로 읽기 모델 다시 만들기

이벤트 소싱과 CQRS의 결합점은 "읽기 모델은 파생물"이라는 선언입니다. 파생물이라면 망가졌을 때 버리고 다시 만들 수 있어야 합니다.

```python
# app/rebuild_projection.py
from sqlalchemy import text
from sqlalchemy.engine import Connection


def rebuild_order_projection(conn: Connection) -> None:
    conn.execute(text("TRUNCATE TABLE order_read_model"))

    rows = conn.execute(
        text(
            """
            SELECT event_type, payload
            FROM event_store
            WHERE aggregate_type = 'order'
            ORDER BY id ASC
            """
        )
    ).fetchall()

    for row in rows:
        event_type = row.event_type
        payload = row.payload

        if event_type == "OrderCreated":
            conn.execute(
                text(
                    """
                    INSERT INTO order_read_model(order_id, status, total_amount)
                    VALUES (:order_id, 'CREATED', :total_amount)
                    """
                ),
                {"order_id": payload["order_id"], "total_amount": payload["total_amount"]},
            )
        elif event_type == "OrderPaid":
            conn.execute(
                text("UPDATE order_read_model SET status='PAID' WHERE order_id=:order_id"),
                {"order_id": payload["order_id"]},
            )
        elif event_type == "OrderCancelled":
            conn.execute(
                text("UPDATE order_read_model SET status='CANCELLED' WHERE order_id=:order_id"),
                {"order_id": payload["order_id"]},
            )
```

실무에서는 전체 재빌드와 증분 업데이트를 분리해 둡니다. 평소에는 증분 projector가 이벤트를 따라가고, 스키마 변경이나 버그 수정 시점에는 전체 재빌드를 실행합니다. 이때 중요한 운영 지표가 "재빌드 완료 시간"입니다. 읽기 모델이 40분 비어도 되는지, 4분 안에 복구해야 하는지는 도메인 요구사항으로 정해야 합니다.

### Consumer Group 리밸런싱을 이해해야 하는 이유

Kafka consumer group은 인스턴스가 늘거나 줄 때 partition 할당을 다시 계산합니다. 이 순간을 리밸런싱이라고 부릅니다. 문제는 리밸런싱 동안 해당 consumer가 잠시 읽기를 멈출 수 있다는 점입니다. 트래픽이 높은 시간대에 리밸런싱이 잦으면 lag가 계단형으로 증가합니다.

운영 설계에서 반드시 정해야 할 항목은 다음입니다.

- partition 수와 consumer 수의 목표 비율
- cooperative-sticky 같은 할당 전략 사용 여부
- 세션 타임아웃(`session.timeout.ms`)과 하트비트 간격(`heartbeat.interval.ms`)
- offset commit 시점(처리 전/후)

아래는 개념을 단순화한 Python 의사 코드입니다.

```python
def on_partitions_revoked(partitions):
    flush_inflight_state()
    commit_offsets_sync(partitions)


def on_partitions_assigned(partitions):
    warmup_cache(partitions)
    seek_to_committed(partitions)
```

핵심은 revoke 시점에 진행 중 상태를 정리하고 commit 경계를 명확히 남기는 것입니다. 이 처리가 없으면 같은 레코드를 재처리하거나, 반대로 처리했지만 커밋하지 못한 구간이 생깁니다. 따라서 리밸런싱은 "가끔 일어나는 내부 동작"이 아니라 전달 보장 의미를 결정하는 1급 설계 요소입니다.

### Exactly-once를 현실적으로 만드는 트랜잭셔널 아웃박스

브로커만으로 전체 시스템 exactly-once를 보장하기는 어렵습니다. 일반적인 실패 시나리오는 DB 커밋 성공 후 publish 실패, 혹은 publish 성공 후 DB 롤백입니다. 이 간극을 줄이는 대표 패턴이 transactional outbox입니다.

1. 비즈니스 데이터 변경과 outbox insert를 같은 DB 트랜잭션으로 커밋합니다.
2. 별도 relay 프로세스가 outbox를 읽어 Kafka/RabbitMQ로 발행합니다.
3. 발행 성공 시 outbox 상태를 `SENT`로 바꿉니다.
4. 소비자는 `event_id` 기반 멱등성으로 중복 발행을 흡수합니다.

```python
# app/order_service.py
from sqlalchemy import text
from sqlalchemy.engine import Connection


def create_order_with_outbox(conn: Connection, order_id: str, amount: int) -> None:
    conn.execute(
        text("INSERT INTO orders(order_id, amount, status) VALUES (:id, :amount, 'CREATED')"),
        {"id": order_id, "amount": amount},
    )

    conn.execute(
        text(
            """
            INSERT INTO outbox(event_id, topic, payload, status)
            VALUES (:event_id, :topic, CAST(:payload AS jsonb), 'PENDING')
            """
        ),
        {
            "event_id": f"order-created-{order_id}",
            "topic": "order.events",
            "payload": '{"type":"OrderCreated","order_id":"%s","amount":%d}'
            % (order_id, amount),
        },
    )
```

relay는 보통 짧은 주기로 `PENDING`을 폴링하거나 CDC(Change Data Capture)로 outbox 변화를 구독합니다. 어떤 방식을 택하든 핵심은 "비즈니스 상태와 이벤트 발행 의도를 같은 원자 경계에 넣는 것"입니다. 이것이 현업에서 말하는 exactly-once에 가장 가까운 구현입니다.

### 이벤트 스키마 진화와 버전 전략

이벤트 소싱을 도입하면 스키마 변경이 곧 역사 변경 문제로 이어집니다. 이미 기록된 과거 이벤트는 수정할 수 없으므로, 읽는 쪽 호환성을 먼저 설계해야 합니다.

권장 원칙은 다음과 같습니다.

- 이벤트 이름은 의미가 바뀌면 새 타입으로 분리합니다.
- 필드 추가는 backward compatible 방식으로 하고 기본값을 명시합니다.
- 필드 삭제는 즉시 삭제 대신 deprecate 기간을 둡니다.
- 이벤트 payload에 `schema_version`을 포함합니다.

```json
{
  "event_id": "evt-20260521-0001",
  "event_type": "OrderPaid",
  "schema_version": 2,
  "payload": {
    "order_id": "order-123",
    "paid_amount": 12000,
    "currency": "KRW",
    "paid_at": "2026-05-21T10:20:00Z"
  }
}
```

projector에서 버전별 변환 함수를 두면 오래된 이벤트도 점진적으로 흡수할 수 있습니다.

```python
def normalize_order_paid(event: dict) -> dict:
    version = event.get("schema_version", 1)
    payload = event["payload"]

    if version == 1:
        return {
            "order_id": payload["order_id"],
            "paid_amount": payload["amount"],
            "currency": "KRW",
            "paid_at": payload["paid_at"],
        }

    if version == 2:
        return payload

    raise ValueError("unsupported_schema_version")
```

이 접근의 장점은 재빌드 시점에도 동일 projector 코드를 재사용할 수 있다는 점입니다. 즉, 스키마 진화 전략은 평시 처리와 복구 처리 모두를 지배합니다.

### 운영 메트릭: lag, 처리량, DLQ

메시지 큐 운영에서 대시보드 첫 화면은 화려할 필요가 없습니다. 대신 의사결정 가능한 세 신호를 고정합니다.

1. **Consumer lag**: 생산 속도 대비 소비 지연입니다. 증가 기울기가 핵심입니다.
2. **Throughput**: 초당 처리량입니다. 정상 구간의 기준선을 팀이 공유해야 합니다.
3. **DLQ 유입량**: 스키마 불일치, 비즈니스 검증 실패, 일시 장애가 섞여 들어오는 경보 신호입니다.

예를 들어 운영 규칙을 아래처럼 수치화할 수 있습니다.

```yaml
alerts:
  - name: consumer-lag-high
    condition: lag > 50000 for 5m
    action: scale-consumer
  - name: throughput-drop
    condition: throughput_per_sec < 1200 for 10m
    action: investigate-rebalance-or-downstream
  - name: dlq-spike
    condition: dlq_in_per_min > 100 for 3m
    action: pause-producer-and-check-schema
```

여기서 중요한 점은 경보의 후속 액션까지 함께 적는 것입니다. lag 경보가 울렸을 때 무조건 인스턴스를 늘리면, 실제 원인이 하류 DB lock 경합인 경우 문제를 악화시킬 수 있습니다. 따라서 지표는 단일 숫자가 아니라 원인 가설과 연결된 runbook 형태로 관리해야 합니다.

### 실무 적용 순서 제안

메시지 큐와 이벤트 소싱을 한 번에 크게 도입하기보다, 아래 순서로 경계를 확정하면 실패 비용을 줄일 수 있습니다.

1. **멱등성 키 확정**: `event_id` 생성 규칙을 먼저 고정합니다.
2. **발행 경계 확정**: outbox 패턴으로 DB와 이벤트 발행 경계를 일치시킵니다.
3. **소비 경계 확정**: offset commit 시점을 "처리 성공 이후"로 문서화합니다.
4. **복구 경계 확정**: 읽기 모델 재빌드 절차와 목표 시간을 SLO로 선언합니다.
5. **진화 경계 확정**: 스키마 버전 규칙과 deprecation 기간을 운영 정책으로 고정합니다.

이 다섯 경계를 먼저 정하면, 기술 스택이 Kafka든 RabbitMQ든 운영 동작은 예측 가능해집니다. 결국 분산 시스템에서 중요한 것은 도구 이름보다 실패 시에도 같은 결과를 재현할 수 있는 설계 언어입니다.


## 처음 질문으로 돌아가기

- **메시지 큐는 어떤 결합 해소와 전달 보장을 제공할까요?**
  - 메시지 큐는 생산자와 소비자의 실행 시점을 분리해 한쪽 장애가 다른 쪽 즉시 실패로 전파되지 않게 만듭니다. 전달 보장은 브로커 설정만으로 완성되지 않고, ack 시점·offset commit 시점·소비자 멱등성까지 포함해 정의해야 하며, 실무에서는 consumer lag와 DLQ 같은 운영 신호로 그 보장이 실제로 유지되는지 확인합니다.
- **at-most-once, at-least-once, exactly-once는 각각 무엇을 뜻할까요?**
  - at-most-once는 유실 가능성을 감수하고 중복을 줄이는 방식, at-least-once는 중복 가능성을 감수하고 유실을 줄이는 방식입니다. exactly-once는 단일 브로커 옵션이 아니라 트랜잭셔널 아웃박스, 처리 후 commit, `event_id` 멱등성 저장소를 함께 설계했을 때 비즈니스 관점에서 근사적으로 달성되는 성질입니다.
- **이벤트 소싱은 무엇이며 CQRS와는 어떤 관계일까요?**
  - 이벤트 소싱은 현재 상태를 최신 row가 아니라 이벤트 이력의 합으로 정의하는 방식이며, CQRS는 그 이력을 읽기 목적에 맞는 projection으로 분리해 조회 성능과 모델 단순성을 얻는 패턴입니다. 그래서 읽기 모델은 언제든 재생성 가능한 파생물이고, 진실의 원천은 이벤트 저장소라는 점이 두 패턴의 결합 핵심입니다.

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
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/distributed-systems-101/ko)

Tags: Computer Science, Distributed Systems, MessageQueue, EventSourcing, Kafka, CQRS
