---
series: distributed-systems-101
episode: 4
title: "바이브코딩을 위한 분산 시스템 기초 (4/10): 일관성과 CAP"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - 분산시스템
  - 일관성
  - CAP정리
  - 선형화가능성
  - EventualConsistency
language: ko
---

# 바이브코딩을 위한 분산 시스템 기초 (4/10): 일관성과 CAP

이 글은 **바이브코딩을 위한 분산 시스템 기초** 시리즈의 4편입니다. AI가 만든 서비스를 스케일하려면 데이터베이스가 어떤 일관성을 보장하는지 선택해야 합니다. 이 선택이 결제 화면의 정확도와 추천 피드의 속도를 동시에 결정합니다.

---

AI에게 "사용자 잔액 조회 API를 만들어줘"라고 하면 DB에서 SELECT를 하는 코드가 나옵니다. 그런데 그 DB에 복제본이 두 개 있고, 방금 다른 서버가 잔액을 차감했다면? 복제본에서 읽는 사용자는 차감 전 금액을 볼 수 있습니다. 이것이 일관성 문제입니다.

데이터가 한 군데에만 있을 때는 "최신값을 읽는다"는 말이 별일 아닙니다. 하지만 복제본이 둘 이상이 되는 순간부터는 어느 복제본을 읽는지에 따라 그 문장이 완전히 다른 뜻을 갖게 됩니다.

> "일관성 모델은 데이터가 맺는 사회적 계약입니다. 결제 데이터와 추천 피드에 같은 계약을 맺을 필요는 없습니다."

## 이 글에서 다룰 질문들

- 일관성 모델이란 무엇이며 ACID의 C와 어떻게 다를까요?
- linearizable, causal, eventual은 어떤 스펙트럼을 이룰까요?
- CAP 정리는 실무에서 어떻게 사용해야 할까요?
- AI가 선택한 DB의 기본 일관성 설정을 어떻게 확인할까요?
- 화면마다 다른 일관성 수준을 어떻게 설계할 수 있을까요?

---

## 바이브코딩과 일관성: DB 기본 설정의 함정

AI가 코드를 작성할 때 DB의 일관성 설정을 명시적으로 고르지 않으면 기본값이 적용됩니다. 기본값이 무엇인지 모르면 잠재적 버그를 안고 서비스를 운영하게 됩니다.

### Before: 기본 설정으로 모든 것을 읽기

```python
# AI가 만든 코드 — 일관성 설정 없음
def get_balance(user_id: str) -> int:
    # 어떤 복제본에서 읽는지 명시하지 않음
    result = db.query("SELECT balance FROM accounts WHERE id = ?", user_id)
    return result[0]["balance"]
```

이 코드는 읽기 요청이 비동기 복제본으로 분산될 경우 방금 차감된 잔액이 아닌 오래된 값을 반환할 수 있습니다.

### After: 화면 성격에 맞는 일관성 명시

```python
# 결제 관련: linearizable 읽기 (최신값 보장)
def get_balance_for_payment(user_id: str) -> int:
    # 리더에서 직접 읽기 — 최신값 보장, 지연 약간 증가
    result = db.query(
        "SELECT balance FROM accounts WHERE id = ?",
        user_id,
        read_preference="primary"  # 복제본이 아닌 기준 노드에서 읽기
    )
    return result[0]["balance"]

# 대시보드 표시: eventual 읽기 (약간 오래된 값 허용)
def get_balance_for_display(user_id: str) -> int:
    # 복제본에서 읽기 — 최대 2초 지연 가능, 빠른 응답
    result = db.query(
        "SELECT balance FROM accounts WHERE id = ?",
        user_id,
        read_preference="secondary",
        max_staleness_seconds=2
    )
    return result[0]["balance"]
```

---

## 일관성 모델 스펙트럼

왼쪽으로 갈수록 직관적이지만 비싸고, 오른쪽으로 갈수록 빠르지만 오래된 값을 볼 수 있습니다.

| 모델 | 보장 | 비용 | 대표 시스템 |
|------|------|------|------------|
| Linearizable | 전체가 하나의 시간선처럼 동작 | 높음 | Spanner, etcd |
| Sequential | 모든 노드가 같은 순서를 봄 | 중간 | ZooKeeper |
| Causal | 인과 관계 있는 연산의 순서만 보존 | 중간 | MongoDB causal |
| Eventual | 시간이 지나면 모든 복제본이 수렴 | 낮음 | DynamoDB, Cassandra |

### CAP 정리: 파티션 중의 선택

파티션(네트워크 단절)이 발생했을 때, 일관성(C)과 가용성(A) 중 하나를 포기해야 합니다.

| 선택 | 동작 | 대표 시스템 | 적합한 경우 |
|------|------|------------|------------|
| CP | 파티션 중 쓰기 거부 — 일관성 유지 | etcd, ZooKeeper | 결제, 재고 차감 |
| AP | 파티션 중에도 쓰기 수용 — 충돌은 나중에 해결 | Cassandra, DynamoDB | 피드, 추천, 로그 |

실무에서는 시스템 전체가 CP나 AP인 경우는 드뭅니다. **결제 API는 CP로, 상품 조회 API는 AP로** 설정하는 하이브리드가 일반적입니다.

---

## 자주 하는 실수

| 실수 | 결과 | 올바른 접근 |
|------|------|------------|
| CAP의 C를 ACID의 C와 혼동 | 잘못된 DB 선택으로 이어짐 | CAP의 C는 linearizability, ACID의 C는 무결성 제약 |
| 시스템 전체를 CP라고 단정 | 같은 시스템 내 호출별 정책이 다를 수 있음 | API별로 일관성 정책을 명시 |
| eventual을 "곧바로"로 해석 | 복제 지연이 초~분 단위일 수 있음 | 실제 복제 지연 P99를 측정해 결정 |
| read-your-writes가 자동이라 가정 | 방금 쓴 값이 읽기에서 보이지 않을 수 있음 | 세션 기반 sticky read 구현 |
| 강한 일관성을 모든 곳에 적용 | 불필요한 지연과 비용 증가 | 데이터 성격에 따라 모델 분리 |

---

## AI 팁: AI가 선택한 DB 설정을 검토하는 법

1. **기본 read preference 확인**: AI가 생성한 DB 연결 설정에서 `read_preference`가 명시되어 있는지 확인하세요.
2. **화면별 정책 요청**: "결제 잔액 조회는 primary에서, 피드 조회는 secondary에서 읽도록 분리해줘"
3. **복제 지연 측정 요청**: "복제본의 복제 지연을 모니터링하는 코드를 추가해줘"
4. **충돌 해소 전략 확인**: AP 시스템이라면 파티션 복구 후 충돌이 어떻게 해소되는지 물어보세요.

```python
# 데이터 유형별 일관성 모델 매핑 예시
CONSISTENCY_MAP = {
    "account_balance":    "linearizable",  # 이중 차감 방지
    "session_status":     "linearizable",  # 로그인 상태 정확성
    "social_feed":        "causal",        # 순서만 맞으면 됨
    "recommendation":     "eventual",      # 새로고침해도 문제없음
    "click_log":          "eventual",      # 대량 처리 우선
}
```

---

## 실전 체크리스트

- [ ] linearizable과 eventual의 차이를 한 줄로 말할 수 있다
- [ ] CAP의 C와 ACID의 C가 다름을 설명할 수 있다
- [ ] 내 서비스의 주요 데이터셋에 일관성 모델을 매핑해봤다
- [ ] read-your-writes를 어떻게 구현할지 설명할 수 있다
- [ ] AI가 생성한 DB 코드의 read preference를 확인했다
- [ ] 파티션 중 CP/AP 중 무엇을 선택할지 데이터 유형별로 결정해봤다

---

## 처음 질문으로 돌아가기

- **일관성 모델이란 무엇이며 ACID의 C와 어떻게 다를까요?**
  일관성 모델은 분산 복제본 사이에서 어떤 값을 읽을 수 있는지에 대한 보장입니다. ACID의 C는 단일 DB 내 무결성 제약(외래 키, 유니크 등)을 뜻합니다. 둘은 다른 개념입니다.

- **AI가 선택한 DB의 기본 일관성 설정을 어떻게 확인할까요?**
  DynamoDB는 기본이 eventual, MongoDB는 기본이 primary 읽기(linearizable에 가까움), Cassandra는 기본이 ONE(eventual)입니다. DB 문서에서 default read/write consistency level을 확인하세요.

- **화면마다 다른 일관성 수준을 어떻게 설계할 수 있을까요?**
  결제/잔액처럼 정확성이 중요한 화면은 primary 읽기를, 피드/추천처럼 속도가 중요한 화면은 replica 읽기를 사용하도록 API 레이어에서 분리하면 됩니다.

---

## 정리

일관성 모델은 데이터의 성격에 따라 선택하는 트레이드오프입니다. 모든 데이터를 linearizable로 만들면 성능이 떨어지고, 모두 eventual로 만들면 금전적 안전성이 무너집니다. 바이브코딩으로 만든 서비스에서는 AI가 선택한 기본값을 반드시 확인하고, 데이터 성격에 맞게 수정해야 합니다. 다음 글에서는 이 선택의 직접적 원인이 되는 복제 방식을 다룹니다.

---

## 참고 자료

- [CAP theorem (Wikipedia)](https://en.wikipedia.org/wiki/CAP_theorem)
- [Consistency model (Wikipedia)](https://en.wikipedia.org/wiki/Consistency_model)
- [PACELC theorem (Wikipedia)](https://en.wikipedia.org/wiki/PACELC_theorem)
- [Designing Data-Intensive Applications — chapter 9](https://dataintensive.net/)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 분산 시스템 기초 (1/10): 분산 시스템이란 무엇인가?
- 바이브코딩을 위한 분산 시스템 기초 (2/10): 장애 모델
- 바이브코딩을 위한 분산 시스템 기초 (3/10): RPC와 메시지 전달
- **바이브코딩을 위한 분산 시스템 기초 (4/10): 일관성과 CAP (현재 글)**
- 바이브코딩을 위한 분산 시스템 기초 (5/10): 복제
- 바이브코딩을 위한 분산 시스템 기초 (6/10): 합의와 Raft
- 바이브코딩을 위한 분산 시스템 기초 (7/10): 리더 선출
- 바이브코딩을 위한 분산 시스템 기초 (8/10): 메시지 큐와 이벤트 소싱
- 바이브코딩을 위한 분산 시스템 기초 (9/10): 분산 트랜잭션
- 바이브코딩을 위한 분산 시스템 기초 (10/10): 운영 가능한 분산 패턴
<!-- toc:end -->

Tags: 바이브코딩, 분산시스템, 일관성, CAP정리, 선형화가능성, EventualConsistency
