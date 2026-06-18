---
title: "바이브코딩을 위한 객체지향 기초 (8/10): SOLID 원칙 기초"
series: oop-101
episode: 8
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - Python
  - OOP
  - SOLID
  - 바이브코딩
  - 설계 원칙
  - 클린 코드
last_reviewed: '2026-06-18'
seo_description: AI가 SOLID 원칙을 적용하는 이유를 설명합니다. 바이브코딩 관점에서 SRP, OCP, LSP, ISP, DIP를 실무 예제로 이해합니다.
---

# 바이브코딩을 위한 객체지향 기초 (8/10): SOLID 원칙 기초

이 글은 **바이브코딩을 위한 객체지향 기초** 시리즈의 여덟 번째 글입니다.

---

AI가 만든 코드를 보다 보면 `OrderValidator`, `OrderPricer`, `OrderRepository`, `ReceiptNotifier`처럼 하나의 기능이 여러 클래스로 나뉘어 있는 경우가 있습니다. 처음엔 "그냥 하나의 `OrderService`에 다 넣으면 안 되나?"라는 생각이 들 수 있습니다.

AI가 이렇게 나눈 데는 이유가 있습니다. 검증 규칙이 바뀔 때, 할인 정책이 바뀔 때, 저장 방식이 바뀔 때, 알림 채널이 바뀔 때 — 네 가지 변경 이유가 하나의 클래스에 있으면 어떤 이유로 수정하든 같은 파일을 건드려야 합니다. 이것이 SOLID 원칙 중 SRP(단일 책임 원칙)가 필요한 이유입니다.

AI가 클래스 계층을 만들어줬는데 왜 이렇게 짰는지 이해하려면 OOP를 알아야 합니다.

> "SOLID는 다섯 글자를 외우는 과목이 아니라, '변경을 한 곳에 가둬 두기'라는 한 가지 목표를 다섯 각도에서 본 것입니다."

## 이 글에서 다룰 문제

- SRP는 왜 "변경 이유가 하나여야 한다"고 말할까요?
- OCP는 새 기능을 추가할 때 기존 코드를 왜 수정하면 안 된다고 할까요?
- LSP 위반이 실제 코드에서 어떻게 드러나나요?
- ISP와 DIP는 테스트 작성에 어떻게 도움이 될까요?
- AI 코드에서 SOLID 위반 신호를 어떻게 찾을 수 있을까요?

## 핵심 개념 잡기

SOLID는 다섯 원칙의 약자입니다. 중요한 것은 약자를 외우는 것이 아니라 각 원칙이 어떤 고장 신호를 해결하는지 이해하는 것입니다.

| 원칙 | 설명 | 고장 신호 |
|------|------|----------|
| SRP | 클래스는 한 번에 하나의 이유로만 바뀌어야 합니다 | 한 클래스가 너무 많은 이유로 수정됨 |
| OCP | 확장에는 열려 있고 수정에는 닫혀 있어야 합니다 | 새 기능마다 기존 if/elif 수정 필요 |
| LSP | 하위 타입은 부모 계약을 깨면 안 됩니다 | 특정 자식만 예외를 던짐 |
| ISP | 클라이언트는 자신이 쓰는 메서드에만 의존해야 합니다 | 인터페이스의 메서드 대부분이 미사용 |
| DIP | 상위 정책은 구체 도구가 아닌 추상에 의존해야 합니다 | 정책 테스트에 실제 인프라가 필요함 |

## Before / After: AI가 SRP를 적용하는 이유

```python
# Before: 검증, 가격, 저장, 알림이 한 클래스에 — 변경 이유가 4가지
class OrderService:
    def checkout(self, order: dict) -> int:
        if not order["items"]:
            raise ValueError("주문 항목이 없습니다")
        total = sum(item["price"] for item in order["items"])
        if order["customer_tier"] == "vip":
            total = int(total * 0.8)
        print(f"주문 저장: {order['email']}")
        print(f"영수증 발송: {total}원")
        return total
```

```python
# After: 책임이 분리됨 — 각자 하나의 이유로만 변경됨
class OrderValidator:
    def validate(self, order: dict) -> None:
        if not order["items"]:
            raise ValueError("주문 항목이 없습니다")

class OrderPricer:
    def __init__(self, discount_policy) -> None:
        self.discount_policy = discount_policy

    def calculate_total(self, order: dict) -> int:
        subtotal = sum(item["price"] for item in order["items"])
        return self.discount_policy.apply(subtotal, order)

class OrderRepository:
    def save(self, order: dict, total: int) -> None:
        print(f"주문 저장: {order['email']} -> {total}원")

class ReceiptNotifier:
    def send(self, email: str, total: int) -> None:
        print(f"영수증 발송: {email}, {total}원")

class CheckoutService:
    def __init__(self, validator, pricer, repository, notifier) -> None:
        self.validator = validator
        self.pricer = pricer
        self.repository = repository
        self.notifier = notifier

    def checkout(self, order: dict) -> int:
        self.validator.validate(order)
        total = self.pricer.calculate_total(order)
        self.repository.save(order, total)
        self.notifier.send(order["email"], total)
        return total
```

이제 할인 규칙이 바뀌면 `OrderPricer`만, 알림 방식이 바뀌면 `ReceiptNotifier`만 수정합니다.

## 바이브코딩 관점: OCP — AI가 if/elif를 Protocol로 바꾸는 이유

```python
# OCP 위반: 새 할인 규칙마다 기존 코드 수정 필요
class OrderPricer:
    def calculate_total(self, order: dict) -> int:
        subtotal = sum(item["price"] for item in order["items"])
        if order["customer_tier"] == "vip":
            return int(subtotal * 0.8)
        elif order["customer_tier"] == "premium":
            return int(subtotal * 0.9)
        # 새 등급 추가 -> elif 추가 -> 기존 코드 수정
        return subtotal
```

```python
# OCP 적용: 새 할인 규칙 추가 = 새 클래스 추가만으로 충분
from typing import Protocol

class DiscountPolicy(Protocol):
    def apply(self, subtotal: int, order: dict) -> int: ...

class NoDiscount:
    def apply(self, subtotal: int, order: dict) -> int:
        return subtotal

class VipDiscount:
    def apply(self, subtotal: int, order: dict) -> int:
        if order["customer_tier"] == "vip":
            return int(subtotal * 0.8)
        return subtotal

class SeasonalDiscount:  # 새 할인 추가: OrderPricer 수정 없음
    def apply(self, subtotal: int, order: dict) -> int:
        return int(subtotal * 0.85)

class OrderPricer:
    def __init__(self, discount: DiscountPolicy) -> None:
        self.discount = discount

    def calculate_total(self, order: dict) -> int:
        subtotal = sum(item["price"] for item in order["items"])
        return self.discount.apply(subtotal, order)  # 어떤 정책이든 동작
```

## DIP: AI가 테스트 가능한 코드를 만드는 방법

DIP(의존성 역전 원칙)가 적용된 코드는 실제 인프라 없이 테스트할 수 있습니다.

```python
from typing import Protocol

class OrderWriter(Protocol):
    def save(self, order: dict, total: int) -> None: ...

class ReceiptSender(Protocol):
    def send_receipt(self, email: str, total: int) -> None: ...

# 테스트용 가짜 구현 (실제 DB, 이메일 불필요)
class FakeWriter:
    def __init__(self) -> None:
        self.saved: list[tuple[str, int]] = []

    def save(self, order: dict, total: int) -> None:
        self.saved.append((order["email"], total))

class FakeSender:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def send_receipt(self, email: str, total: int) -> None:
        self.messages.append(f"{email}:{total}")

# 테스트: 실제 DB와 이메일 서버 없이도 가능
writer = FakeWriter()
sender = FakeSender()
service = CheckoutService(
    validator=OrderValidator(),
    pricer=OrderPricer(VipDiscount()),
    writer=writer,
    sender=sender,
)

order = {
    "email": "kim@example.com",
    "customer_tier": "vip",
    "items": [{"price": 20000}],
}
total = service.checkout(order)
print(total)              # 16000
print(writer.saved)       # [('kim@example.com', 16000)]
```

## AI 코드에서 SOLID 위반 신호

| 위반 신호 | 어떤 원칙 | 해결 방향 |
|----------|----------|----------|
| 한 클래스가 3가지 이상 이유로 수정됨 | SRP | 역할별 클래스로 분리 |
| 기능 추가마다 기존 if/elif 수정 | OCP | Protocol + 구현 클래스 추가 |
| 특정 자식 타입만 예외를 임의로 바꿈 | LSP | 계약을 지키는 구현으로 수정 |
| 인터페이스 메서드 대부분이 미사용 | ISP | 작은 인터페이스로 분할 |
| 정책 테스트에 실제 DB가 필요함 | DIP | Protocol + 가짜 구현 주입 |

## 자주 하는 실수

| 실수 | 왜 아픈가 | 더 나은 선택 |
|------|----------|--------------|
| 아픔도 없는데 SOLID를 한꺼번에 적용 | 설계가 추상적이기만 하고 보상이 없습니다 | 보이는 실패 모양에서 시작합니다 |
| OCP를 "절대 기존 코드를 수정하지 않기"로 이해 | 간접 계층이 가치보다 빨리 늘어납니다 | 실제로 자주 바뀌는 규칙만 뽑습니다 |
| 시그니처만 맞으면 LSP라고 생각 | 런타임에서 여전히 호출자를 깨뜨립니다 | 동작 기대까지 확인합니다 |
| 편하다고 거대한 인터페이스 유지 | 클라이언트가 불필요한 메서드까지 구현합니다 | 호출자 기준으로 쪼갭니다 |
| 내부에서 구체 구현을 직접 생성하고도 DIP라고 부름 | 테스트와 교체 비용이 그대로 남습니다 | 외부에서 추상을 주입합니다 |

## AI 팁: SOLID를 기준으로 AI 코드 개선 요청하기

```python
# AI에게 이렇게 요청하세요:

# SRP 적용:
# "이 클래스가 너무 많은 일을 하고 있어. 책임을 분리해 줘"

# OCP 적용:
# "새 할인 정책이 추가될 때 기존 코드를 수정하지 않아도 되도록 바꿔 줘"

# DIP 적용:
# "이 클래스를 실제 DB 없이 테스트할 수 있도록 리팩터링해 줘"
# -> AI가 Protocol + 의존성 주입 패턴으로 변환해 줌
```

## 체크리스트

- [ ] SRP를 눈에 보이는 고장 신호와 연결해 설명할 수 있다
- [ ] OCP를 위해 if/elif를 Protocol 패턴으로 바꿀 수 있다
- [ ] DIP를 적용하여 테스트 가능한 코드를 만들 수 있다
- [ ] AI 코드에서 SOLID 위반 신호를 식별할 수 있다
- [ ] AI에게 SOLID 원칙을 기준으로 개선을 요청할 수 있다

## 처음 질문으로 돌아가기

- **SRP는 왜 "변경 이유가 하나여야 한다"고 말할까요?**
  변경 이유가 여러 개면 관련 없는 수정도 같은 파일을 건드립니다. AI가 `OrderValidator`, `OrderPricer`로 나눈 것은 각자 하나의 이유로만 변경되도록 설계한 것입니다.

- **OCP는 왜 기존 코드를 수정하면 안 된다고 할까요?**
  기존 코드를 수정하면 이미 테스트된 기능이 깨질 수 있습니다. Protocol 패턴으로 새 구현 클래스를 추가하면 기존 코드는 건드리지 않습니다. AI가 이 패턴을 쓰면 확장이 쉬워집니다.

- **DIP는 테스트에 어떻게 도움이 될까요?**
  구체 구현 대신 Protocol을 주입받으면 테스트할 때 가짜 구현을 주입할 수 있습니다. 실제 DB나 이메일 서버 없이도 정책 로직만 테스트할 수 있습니다.

## 정리

SOLID는 다섯 슬로건을 외우는 것이 아니라 변경 비용을 줄이는 설계 원칙입니다. AI가 복잡해 보이는 구조를 만들 때는 이 원칙들이 배경에 있는 경우가 많습니다. SRP와 DIP부터 이해하면 AI 코드를 수정하고 확장하는 것이 훨씬 쉬워집니다. 다음 글에서는 실전 설계 예제로 이 모든 개념을 한 번에 적용해 봅니다.

## 참고 자료

- [Real Python — SOLID Principles in Python](https://realpython.com/solid-principles-python/)
- [Python 공식 문서 — abc 모듈](https://docs.python.org/3/library/abc.html)
- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/oop-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 객체지향 기초 (1/10): 객체지향이란 무엇인가?
- 바이브코딩을 위한 객체지향 기초 (2/10): 클래스와 인스턴스
- 바이브코딩을 위한 객체지향 기초 (3/10): 캡슐화
- 바이브코딩을 위한 객체지향 기초 (4/10): 상속
- 바이브코딩을 위한 객체지향 기초 (5/10): 다형성
- 바이브코딩을 위한 객체지향 기초 (6/10): 추상화
- 바이브코딩을 위한 객체지향 기초 (7/10): 합성과 상속
- **바이브코딩을 위한 객체지향 기초 (8/10): SOLID 원칙 기초 (현재 글)**
- 바이브코딩을 위한 객체지향 기초 (9/10): 객체지향 설계 예제
- 바이브코딩을 위한 객체지향 기초 (10/10): 객체지향을 언제 피해야 할까?

<!-- toc:end -->

Tags: Python, OOP, SOLID, 바이브코딩, 설계 원칙, 클린 코드
