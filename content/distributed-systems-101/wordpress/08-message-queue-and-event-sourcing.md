---
title: "바이브코딩을 위한 Distributed Systems 기초 (8/10): 메시지 큐와 이벤트 소싱"
series: distributed-systems-101
episode: 8
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - DistributedSystems
  - MessageQueue
  - EventSourcing
  - Kafka
  - CQRS
---

# 바이브코딩을 위한 Distributed Systems 기초 (8/10): 메시지 큐와 이벤트 소싱

이 글은 "바이브코딩을 위한 Distributed Systems 기초" 시리즈의 8번째 글입니다.

---

바이브코딩에서 AI는 메시지 큐와 Kafka 코드를 빠르게 만들어 줍니다. 하지만 직접 호출은 참여하는 모든 서비스가 같은 순간에 건강해야 한다는 조건을 강하게 묶습니다. 반대로 큐와 로그를 사이에 두면 한쪽은 지금 끝내고, 다른 쪽은 나중에 따라와도 되며, 그 사이의 이력을 보존할 수 있습니다.

큐는 시간을 분리하고, 이벤트는 진실의 원천을 분리합니다. 이벤트 소싱은 상태를 이벤트의 누적으로 정의하므로, 이력과 재생이 시스템의 본질이 됩니다.

AI가 만들어 준 큐/이벤트 코드에서 전달 보장 수준(at-most-once/at-least-once/exactly-once), idempotency 설계, DLQ(Dead Letter Queue) 설정 여부를 확인해야 합니다.

메시지 큐와 이벤트 로그를 통해 시간이 어떻게 설계 도구가 되는지, replay와 idempotency가 왜 운영 언어가 되는지 정리합니다.

> **핵심 인사이트:** 큐는 시간을 분리합니다. 생산자와 소비자가 동시에 살아있지 않아도 됩니다. Idempotency 없는 at-least-once는 중복 처리로 데이터를 오염시킵니다.

## 이 글에서 다룰 문제

- 메시지 큐는 어떤 결합 해소와 전달 보장을 제공할까요?
- at-most-once, at-least-once, exactly-once는 각각 무엇을 뜻할까요?
- Idempotency가 왜 필수인가요?
- 이벤트 소싱과 CQRS는 어떤 관계일까요?
- AI가 만든 큐/이벤트 코드에서 확인해야 할 것은 무엇인가요?

## 메시지 큐와 이벤트 소싱 핵심 패턴

```python
# At-least-once + Idempotency 패턴
import uuid
from typing import Set

class IdempotentConsumer:
    def __init__(self, db):
        self.db = db
        self.processed_ids: Set[str] = set()  # 처리된 메시지 ID 추적

    def process_message(self, message_id: str, payload: dict):
        """멱등적 메시지 처리 - 중복 수신해도 안전"""
        if message_id in self.processed_ids:
            return  # 이미 처리됨, 무시

        with self.db.transaction():
            self.db.execute("INSERT INTO orders ...", payload)
            self.processed_ids.add(message_id)
            # 처리 완료 후 ack (at-least-once)

# Kafka 기본 패턴
from kafka import KafkaProducer, KafkaConsumer

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    acks='all',  # 모든 레플리카 확인 후 ack
    enable_idempotence=True,  # 중복 전송 방지
)

consumer = KafkaConsumer(
    'orders',
    bootstrap_servers=['localhost:9092'],
    group_id='order-processor',
    auto_offset_reset='earliest',
    enable_auto_commit=False,  # 수동 offset commit (처리 후)
)
```

## 변경 전후 비교

**Before: 직접 HTTP 호출**
```text
- 결제 서비스가 다운되면 주문 서비스도 실패
- 재시도 시 중복 결제 발생 가능
- 이력 없음, 재생 불가
- 서비스 장애가 연쇄적으로 전파
```

**After: 메시지 큐 + Idempotency**
```text
- 결제 서비스 다운 중에도 주문은 큐에 저장
- Idempotency key로 중복 결제 방지
- 이벤트 로그로 이력 재생 가능
- 장애 격리: 소비자 속도와 독립
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| At-least-once에 idempotency 없음 | 중복 처리로 데이터 오염 | 모든 메시지 핸들러를 멱등적으로 설계 |
| DLQ 없이 실패 메시지 방치 | 실패한 메시지가 사라짐 | Dead Letter Queue 필수 설정 |
| Auto commit 사용 | 처리 전 offset 커밋 시 메시지 손실 | 처리 완료 후 수동 commit |
| 메시지 스키마 버전 관리 없음 | 소비자 업데이트 시 호환성 깨짐 | Avro/Protobuf 등 스키마 레지스트리 |
| Consumer lag 모니터링 없음 | 지연 쌓여도 인지 못함 | Consumer group lag 알람 설정 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"Kafka를 사용한 주문 처리 시스템을 만들어줘.
At-least-once 전달 보장,
Idempotency key로 중복 처리 방지,
DLQ 설정, 수동 offset commit까지 포함해야 해"

# AI 결과물 검증 체크포인트:
# - Idempotency가 없는 at-least-once → 중복 처리 위험
# - enable_auto_commit=True → 처리 전 손실 위험
# - DLQ 없음 → 실패 메시지 추적 불가
# - Consumer lag 모니터링 설정 여부
```

## 운영 체크리스트

- [ ] 모든 메시지 핸들러가 멱등적으로 구현되어 있다
- [ ] Dead Letter Queue가 설정되어 있다
- [ ] 수동 offset commit을 사용한다 (처리 완료 후)
- [ ] Consumer group lag을 모니터링한다
- [ ] 메시지 스키마가 버전 관리된다

## 처음 질문으로 돌아가기

- **At-least-once와 exactly-once의 차이는?** At-least-once는 중복 전달 가능하지만 손실 없음, exactly-once는 정확히 한 번(비용이 높음). 실무에서는 at-least-once + idempotency 조합이 일반적.
- **Idempotency가 왜 필수인가요?** At-least-once 재시도 시 같은 메시지를 여러 번 처리할 수 있습니다. 멱등하지 않으면 중복 결제, 중복 적립 등 데이터 오염이 발생합니다.
- **이벤트 소싱과 CQRS의 관계는?** 이벤트 소싱은 상태를 이벤트의 누적으로 저장, CQRS는 쓰기(Command)와 읽기(Query) 모델을 분리합니다. 함께 쓰면 복잡한 읽기 패턴에 유연하게 대응할 수 있습니다.

## 정리

바이브코딩에서 AI가 만들어 준 메시지 큐 코드에서 Idempotency 설계, DLQ 설정, 수동 offset commit 여부를 반드시 확인하세요. 큐는 결합 해소와 장애 격리를 가능하게 하지만, Idempotency 없이는 오히려 중복 처리 문제를 만듭니다. 다음 글에서는 분산 트랜잭션을 다룹니다.

## 참고 자료

- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Designing Data-Intensive Applications — Chapter 11](https://dataintensive.net/)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/distributed-systems-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Distributed Systems 기초 (1/10): 분산 시스템이란 무엇인가?
- 바이브코딩을 위한 Distributed Systems 기초 (2/10): 장애 모델
- 바이브코딩을 위한 Distributed Systems 기초 (3/10): RPC와 메시지 패싱
- 바이브코딩을 위한 Distributed Systems 기초 (4/10): 일관성과 CAP
- 바이브코딩을 위한 Distributed Systems 기초 (5/10): 복제
- 바이브코딩을 위한 Distributed Systems 기초 (6/10): 합의와 Raft
- 바이브코딩을 위한 Distributed Systems 기초 (7/10): 리더 선출
- **바이브코딩을 위한 Distributed Systems 기초 (8/10): 메시지 큐와 이벤트 소싱 (현재 글)**
- 바이브코딩을 위한 Distributed Systems 기초 (9/10): 분산 트랜잭션
- 바이브코딩을 위한 Distributed Systems 기초 (10/10): 운영 가능한 분산 시스템 패턴
<!-- toc:end -->

Tags: 바이브코딩, DistributedSystems, MessageQueue, EventSourcing, Kafka, CQRS
