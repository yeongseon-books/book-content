---
title: "바이브코딩을 위한 pytest 기초 (10/10): 테스트하기 좋은 코드"
series: pytest-101
episode: 10
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - pytest
  - Testing
  - Design
  - Architecture
---

# 바이브코딩을 위한 pytest 기초 (10/10): 테스트하기 좋은 코드

이 글은 "바이브코딩을 위한 pytest 기초" 시리즈의 마지막 글입니다.

---

바이브코딩에서 AI는 동작하는 코드를 빠르게 만들어 줍니다. 그런데 AI가 만든 코드를 테스트하려고 할 때 막히는 경우가 있습니다. 함수 안에서 데이터베이스를 직접 호출하거나, 이메일 전송 API를 내부에서 import하거나, `datetime.now()`로 현재 시각을 직접 쓰는 코드는 단위 테스트를 작성하기 어렵습니다.

테스트하기 어렵다는 것은 설계 신호입니다. 코드가 너무 많은 일을 한 번에 하거나, 외부 의존성이 내부에 고정되어 있다는 뜻입니다.

테스트하기 좋은 코드의 핵심은 두 가지입니다. 안쪽에는 순수 규칙(pure function, 입력만 보고 출력을 결정), 바깥쪽에는 교체 가능한 부작용(DB, 이메일, 외부 API). 순수 함수는 Mock 없이 바로 테스트할 수 있습니다. 부작용은 의존성 주입(Dependency Injection)으로 테스트에서 Fake로 교체합니다.

AI가 만든 코드에서 "이 함수를 테스트하려면 무엇이 필요한가"를 물어보세요. 데이터베이스, 이메일 서버, 외부 API가 없으면 테스트할 수 없다면 설계를 다시 봐야 합니다.

> **핵심 인사이트:** 안쪽에는 순수 규칙, 바깥쪽에는 교체 가능한 부작용. 순수 함수는 테스트에 Mock이 필요 없습니다. 의존성 주입으로 외부 의존성을 테스트에서 Fake로 교체할 수 있게 만들면 테스트 속도와 신뢰도가 함께 높아집니다.

## 이 글에서 다룰 문제

- 테스트하기 어려운 코드는 어떤 패턴을 갖고 있을까요?
- 순수 함수는 테스트 설계에서 왜 중요할까요?
- 의존성 주입은 어떻게 테스트 가능성을 높일까요?
- Protocol을 이용한 Fake 객체는 어떻게 만들까요?
- AI가 만든 코드를 테스트 가능하게 리팩터링하려면 어떻게 해야 할까요?

## 테스트하기 좋은 코드 핵심 패턴

```python
# Before: 모든 것이 섞인 함수 - 테스트하기 어렵다
def create_order(user_id: str, items: list):
    db = Database()                          # 직접 DB 연결
    user = db.get_user(user_id)
    total = sum(item["price"] for item in items)
    charge = stripe.charge(user.card_id, total)  # 실제 결제 호출
    order = db.save_order(user_id, items, charge.id)
    send_email(user.email, f"주문 #{order.id}")   # 실제 이메일 전송
    return order
```

```python
# After: 순수 규칙과 부작용 분리
from typing import Protocol

# 1. 순수 규칙 (Mock 없이 바로 테스트 가능)
def build_charge_request(card_id: str, items: list) -> dict:
    total = sum(item["price"] for item in items)
    return {"card_id": card_id, "amount": total}

def finalize_order(user_id: str, items: list, charge_id: str) -> dict:
    return {
        "user_id": user_id,
        "items": items,
        "charge_id": charge_id,
        "status": "confirmed",
    }

# 2. 교체 가능한 인터페이스 (Protocol)
class PaymentGateway(Protocol):
    def charge(self, card_id: str, amount: int) -> str: ...

class EmailSender(Protocol):
    def send(self, to: str, body: str) -> None: ...

# 3. 의존성 주입으로 조합
def create_order(
    user_id: str,
    items: list,
    payment: PaymentGateway,
    emailer: EmailSender,
    db,
):
    user = db.get_user(user_id)
    req = build_charge_request(user.card_id, items)   # 순수 함수
    charge_id = payment.charge(**req)                  # 주입된 의존성
    order = finalize_order(user_id, items, charge_id)  # 순수 함수
    emailer.send(user.email, f"주문 확인: {order}")    # 주입된 의존성
    return db.save_order(order)
```

```python
# 테스트: Fake로 교체, 실제 결제/이메일 없이 테스트
class FakePayment:
    def charge(self, card_id: str, amount: int) -> str:
        return f"fake-charge-{card_id}"

class FakeEmailer:
    def __init__(self):
        self.sent = []
    def send(self, to: str, body: str) -> None:
        self.sent.append((to, body))

def test_build_charge_request():
    req = build_charge_request("card-123", [{"price": 1000}, {"price": 500}])
    assert req == {"card_id": "card-123", "amount": 1500}

def test_create_order_sends_email(fake_db):
    emailer = FakeEmailer()
    create_order("user-1", [{"price": 1000}], FakePayment(), emailer, fake_db)
    assert len(emailer.sent) == 1
    assert "user-1@example.com" in emailer.sent[0][0]
```

## 변경 전후 비교

**Before: 테스트하기 어려운 코드**
```text
- 함수 안에서 DB, 결제 API, 이메일을 직접 호출
- 테스트하려면 실제 DB와 API가 필요
- Mock이 복잡해지고 테스트가 느려짐
- 비즈니스 규칙과 I/O가 섞여 규칙 검증이 어려움
```

**After: 테스트하기 좋은 코드**
```text
- 순수 함수로 비즈니스 규칙 분리 → Mock 없이 테스트
- Protocol로 의존성 인터페이스 정의
- Fake 객체로 빠르고 격리된 테스트
- 규칙, 조합, I/O 각 계층이 독립적으로 테스트됨
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 함수 내부에서 import | 의존성 교체 불가 | 생성자나 인수로 주입 |
| 전역 상태 사용 | 테스트 간 간섭 발생 | 함수 인수로 상태 전달 |
| 순수 로직과 I/O 혼합 | Mock 복잡도 증가 | 규칙과 I/O를 별도 함수로 분리 |
| Protocol 없이 구현에 의존 | Fake 작성 어려움 | Protocol로 인터페이스 명시 |
| 테스트 작성 후 리팩터링 포기 | 코드가 점점 테스트하기 어려워짐 | 테스트 어려움을 설계 신호로 인식 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"이 create_order 함수를 테스트하기 좋은 구조로 리팩터링해줘.
순수 비즈니스 규칙 함수를 분리하고,
DB, 결제, 이메일은 Protocol로 추상화해서
Fake 객체로 교체할 수 있게 만들어줘"

# AI 결과물 검증 체크포인트:
# - 순수 함수(입력 → 출력, 부작용 없음)가 분리되어 있는가?
# - 외부 의존성이 Protocol로 정의되어 있는가?
# - Fake 구현체로 테스트를 작성할 수 있는가?
# - Mock 없이 테스트 가능한 비즈니스 로직이 있는가?
# - 테스트가 느리거나 네트워크에 의존하지 않는가?
```

## 운영 체크리스트

- [ ] 비즈니스 규칙이 순수 함수로 분리되어 있다
- [ ] 외부 의존성(DB, API, 이메일)이 Protocol로 추상화되어 있다
- [ ] Fake 객체로 단위 테스트를 실행할 수 있다
- [ ] 테스트가 네트워크 없이 로컬에서 빠르게 실행된다
- [ ] "테스트하기 어렵다"는 신호를 설계 개선의 계기로 삼는다

## 처음 질문으로 돌아가기

- **테스트하기 어려운 코드의 공통점은?** 외부 의존성이 함수 내부에 고정되어 있습니다. DB 연결, 이메일 클라이언트, 현재 시각이 함수 안에서 직접 생성되면 테스트에서 교체할 수 없습니다.
- **순수 함수란?** 동일한 입력이면 항상 동일한 출력을 반환하고, 외부 상태를 읽거나 변경하지 않는 함수입니다. DB 쿼리, 파일 쓰기, API 호출이 없습니다. 테스트에 Mock이 필요 없어서 빠르고 안정적입니다.
- **Protocol을 쓰는 이유는?** Python의 `typing.Protocol`은 구조적 타입(structural typing)을 제공합니다. `charge()` 메서드가 있으면 `PaymentGateway`로 인식합니다. 실제 Stripe와 FakePayment 모두 같은 Protocol을 만족하면 테스트에서 교체할 수 있습니다.

## 정리

바이브코딩에서 AI가 만든 코드가 테스트하기 어렵다면, 그것은 설계 신호입니다. 순수 함수로 비즈니스 규칙을 분리하고, Protocol로 외부 의존성을 추상화하고, Fake 객체로 테스트하세요. pytest 101 시리즈를 통해 첫 테스트 작성부터 픽스처, 파라미터화, Mock, 커버리지, CI, 그리고 테스트하기 좋은 코드 설계까지 테스트의 기초를 갖추셨기를 바랍니다.

## 참고 자료

- [Python — typing.Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol)
- [Architecture Patterns with Python — Harry Percival](https://www.cosmicpython.com/)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/pytest-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 pytest 기초 (1/10): pytest란 무엇인가?
- 바이브코딩을 위한 pytest 기초 (2/10): 첫 번째 테스트 작성
- 바이브코딩을 위한 pytest 기초 (3/10): assert와 예외 테스트
- 바이브코딩을 위한 pytest 기초 (4/10): 픽스처
- 바이브코딩을 위한 pytest 기초 (5/10): 파라미터화 테스트
- 바이브코딩을 위한 pytest 기초 (6/10): Mock과 패치
- 바이브코딩을 위한 pytest 기초 (7/10): 파일, 환경변수, 시간 테스트
- 바이브코딩을 위한 pytest 기초 (8/10): 커버리지
- 바이브코딩을 위한 pytest 기초 (9/10): CI와 GitHub Actions
- **바이브코딩을 위한 pytest 기초 (10/10): 테스트하기 좋은 코드 (현재 글)**
<!-- toc:end -->

Tags: 바이브코딩, pytest, Testing, Design, Architecture
