---
title: "바이브코딩을 위한 Distributed Systems 기초 (9/10): 분산 트랜잭션"
series: distributed-systems-101
episode: 9
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - DistributedSystems
  - Transactions
  - Saga
  - Outbox
  - Idempotency
---

# 바이브코딩을 위한 Distributed Systems 기초 (9/10): 분산 트랜잭션

이 글은 "바이브코딩을 위한 Distributed Systems 기초" 시리즈의 9번째 글입니다.

---

바이브코딩에서 AI는 분산 트랜잭션 코드를 빠르게 만들어 줍니다. 하지만 분산 트랜잭션의 진짜 난점은 모두가 정상일 때가 아닙니다. 한쪽은 이미 커밋했고 다른 쪽은 타임아웃 난 상태에서, 비즈니스는 여전히 하나의 결과를 요구하는 그 순간이 문제를 만듭니다.

단일 데이터베이스에서 비교적 싸게 얻을 수 있는 ACID는 여러 노드를 넘는 순간 훨씬 비싸지거나, 아예 성립하기 어려워집니다. 분산 트랜잭션은 결국 명시적인 트레이드오프 위에서 하는 설계입니다.

분산 트랜잭션은 ACID의 모방이 아니라 복구 가능한 비일관성의 설계입니다. 2PC의 강한 모델과 Saga, Outbox, 멱등적 복구 같은 현실적 대안을 비교해 정리합니다.

> **핵심 인사이트:** 분산 트랜잭션에서 "완벽한 원자성"을 추구하면 가용성과 성능을 희생합니다. Saga + Outbox + Idempotency 조합이 현실적 대안입니다.

## 이 글에서 다룰 문제

- 단일 노드 트랜잭션과 분산 트랜잭션은 무엇이 다를까요?
- 2-phase commit은 어떻게 동작하고 어디서 약할까요?
- Saga의 핵심인 보상 트랜잭션은 무엇일까요?
- Outbox 패턴은 어떤 문제를 해결할까요?
- AI가 만든 분산 트랜잭션 코드에서 확인해야 할 것은 무엇인가요?

## 분산 트랜잭션 핵심 패턴

```python
# Saga 패턴: 보상 트랜잭션으로 실패 복구
class OrderSaga:
    def execute(self, order_id: str, amount: float):
        """주문 → 결제 → 재고 차감 순서"""
        steps = [
            (self.create_order, self.cancel_order),
            (self.charge_payment, self.refund_payment),
            (self.reduce_inventory, self.restore_inventory),
        ]
        completed = []
        try:
            for action, compensation in steps:
                action(order_id, amount)
                completed.append(compensation)
        except Exception as e:
            # 역순으로 보상 트랜잭션 실행
            for compensation in reversed(completed):
                compensation(order_id, amount)
            raise

# Outbox 패턴: DB 쓰기와 메시지 발행을 원자적으로
# 1. 주문 INSERT + outbox INSERT를 하나의 트랜잭션으로
def place_order(db, order: dict):
    with db.transaction():
        db.execute("INSERT INTO orders ...", order)
        db.execute(
            "INSERT INTO outbox (event_type, payload) VALUES (?, ?)",
            ("order_placed", json.dumps(order))
        )
    # 별도 프로세스가 outbox를 읽어 메시지 큐에 발행
```

## 변경 전후 비교

**Before: 2PC 또는 분산 호출 직접 연결**
```text
- Coordinator 장애 시 전체 시스템 블록
- 결제 서비스 타임아웃 후 주문만 생성된 상태
- 실패 복구 절차 없음
- 데이터 불일치 수동 확인 필요
```

**After: Saga + Outbox + Idempotency**
```text
- 각 단계가 독립적으로 실패/복구 가능
- 보상 트랜잭션으로 비즈니스 롤백
- Outbox로 DB 쓰기와 메시지 발행 원자적 처리
- Idempotency key로 중복 처리 방지
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 보상 트랜잭션 없는 Saga | 실패 시 부분 실행 상태로 남음 | 모든 단계에 보상 트랜잭션 설계 |
| Outbox 없이 DB 쓰기 + 메시지 발행 | DB 성공 후 메시지 실패 가능성 | Outbox 패턴으로 원자성 확보 |
| Idempotency 없는 보상 트랜잭션 | 보상 중복 실행 시 오류 | 보상도 멱등적으로 설계 |
| 2PC를 마이크로서비스에 적용 | 가용성 저하, 블로킹 위험 | Saga 패턴으로 전환 |
| 분산 트랜잭션 상태 추적 없음 | 실패 위치 파악 불가 | 각 단계 상태를 DB에 기록 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"주문 → 결제 → 재고 차감 흐름을 Saga 패턴으로 구현해줘.
각 단계에 보상 트랜잭션 포함,
Outbox 패턴으로 메시지 발행 원자성 확보,
Idempotency key도 포함해야 해"

# AI 결과물 검증 체크포인트:
# - 각 Saga 단계에 보상 트랜잭션이 있는가?
# - DB 쓰기와 메시지 발행이 원자적인가? (Outbox 없으면 위험)
# - 보상 트랜잭션도 멱등적인가?
# - 실패 상태가 어딘가에 기록되는가?
```

## 운영 체크리스트

- [ ] 모든 Saga 단계에 보상 트랜잭션이 설계되어 있다
- [ ] DB 쓰기와 메시지 발행에 Outbox 패턴을 사용한다
- [ ] 모든 단계가 멱등적으로 구현되어 있다
- [ ] Saga 실행 상태가 추적 가능하다
- [ ] 장기 실행 Saga의 타임아웃 처리가 있다

## 처음 질문으로 돌아가기

- **2PC의 약점은?** Coordinator 장애 시 전체가 블록됩니다. 마이크로서비스 환경에서 가용성이 크게 떨어집니다.
- **Saga의 보상 트랜잭션이란?** 이미 커밋된 작업을 비즈니스 의미상 되돌리는 동작입니다. 기술적 롤백이 아닌 "취소 주문 생성"처럼 새로운 이벤트로 표현합니다.
- **Outbox 패턴이 해결하는 문제는?** DB 트랜잭션과 메시지 발행을 원자적으로 묶습니다. DB 성공 후 메시지 발행 실패를 막습니다.

## 정리

바이브코딩에서 AI가 만들어 준 분산 트랜잭션 코드에서 보상 트랜잭션 완비, Outbox 패턴 사용, Idempotency 설계를 반드시 확인하세요. 분산 환경에서 완벽한 원자성보다 복구 가능성을 설계하는 것이 현실적입니다. 다음 글에서는 시리즈 마지막으로 운영 가능한 분산 시스템 패턴을 정리합니다.

## 참고 자료

- [Saga Pattern — Chris Richardson](https://microservices.io/patterns/data/saga.html)
- [Transactional Outbox Pattern](https://microservices.io/patterns/data/transactional-outbox.html)
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
- 바이브코딩을 위한 Distributed Systems 기초 (8/10): 메시지 큐와 이벤트 소싱
- **바이브코딩을 위한 Distributed Systems 기초 (9/10): 분산 트랜잭션 (현재 글)**
- 바이브코딩을 위한 Distributed Systems 기초 (10/10): 운영 가능한 분산 시스템 패턴
<!-- toc:end -->

Tags: 바이브코딩, DistributedSystems, Transactions, Saga, Outbox, Idempotency
