---
title: "바이브코딩을 위한 객체지향 기초 (9/10): 객체지향 설계 예제"
series: oop-101
episode: 9
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - Python
  - OOP
  - 설계 예제
  - 바이브코딩
  - 리팩터링
  - 클래스 설계
last_reviewed: '2026-06-18'
seo_description: 온라인 서점 주문 시스템을 AI와 함께 설계하는 예제로 OOP 개념을 통합합니다. 바이브코딩 관점에서 실전 설계 과정을 설명합니다.
---

# 바이브코딩을 위한 객체지향 기초 (9/10): 객체지향 설계 예제

이 글은 **바이브코딩을 위한 객체지향 기초** 시리즈의 아홉 번째 글입니다.

---

지금까지 캡슐화, 상속, 다형성, 추상화, 합성, SOLID를 각각 배웠습니다. 하지만 막상 AI에게 "온라인 서점 주문 시스템을 만들어 줘"라고 하면 AI가 만들어 준 코드가 어떤 원칙에 따라 설계된 건지 파악하기 어렵습니다.

이 글에서는 온라인 서점 주문 시스템을 예제로, AI와 함께 설계하는 과정을 단계별로 따라가 봅니다. 각 단계에서 AI가 내리는 설계 결정과 그 이유를 이해하면, 나중에 기능을 추가하거나 수정할 때 훨씬 자신감 있게 접근할 수 있습니다.

AI가 클래스 계층을 만들어줬는데 왜 이렇게 짰는지 이해하려면 OOP를 알아야 합니다.

> "좋은 설계는 처음부터 완벽한 다이어그램이 아니라, 동작하는 모델을 만들고 변경 가능성이 큰 지점에 유연성을 추가하면서 다듬어집니다."

## 이 글에서 다룰 문제

- AI에게 시스템을 요청하면 어떤 클래스 구조가 나오고, 왜 그렇게 나올까요?
- 값 객체, 엔티티, 서비스 클래스는 어떤 역할을 나누어 맡을까요?
- AI가 만든 `Money`, `Cart`, `Order` 클래스를 어떻게 읽고 수정할 수 있을까요?
- 할인 정책, 결제 수단처럼 자주 바뀌는 요소를 AI는 어떻게 분리하나요?
- 기능을 추가할 때 어느 클래스를 수정해야 하는지 어떻게 판단할까요?

## 핵심 개념 잡기

AI가 온라인 서점 주문 시스템을 만들 때 일반적으로 이런 구조가 나옵니다.

```text
OrderService
├── Cart          -> 장바구니 관리
├── DiscountPolicy -> 할인 정책 (전략 패턴)
├── PaymentGateway -> 결제 처리 (DIP)
└── OrderRepository -> 주문 저장 (DIP)
```

| 용어 | 설명 |
|------|------|
| 값 객체(value object) | 동등성으로 비교되는 불변 객체입니다 (`Money`) |
| 엔티티(entity) | 고유 식별자로 구분되는 객체입니다 (`Book`) |
| 서비스 클래스 | 도메인 객체 간의 협력을 조율하는 클래스입니다 (`OrderService`) |

## Before / After: AI가 절차지향을 OOP로 바꾸는 방식

```python
# Before: 절차지향 — 모든 로직이 한 함수에 몰림
def process_order(items, payment_type, discount_code):
    total = sum(item["price"] * item["qty"] for item in items)
    if discount_code == "SAVE10":
        total = int(total * 0.9)
    if payment_type == "card":
        print(f"카드 결제: {total}원")
    elif payment_type == "bank":
        print(f"계좌이체: {total}원")
    print(f"주문 저장: {total}원, {len(items)}개")
```

```python
# After: OOP — 책임이 분리됨
class OrderItem:
    def __init__(self, name: str, price: int, quantity: int) -> None:
        self.name = name
        self.price = price
        self.quantity = quantity

    @property
    def total(self) -> int:
        return self.price * self.quantity

class Order:
    def __init__(self, items: list["OrderItem"]) -> None:
        self.items = items

    @property
    def subtotal(self) -> int:
        return sum(item.total for item in self.items)
```

## 바이브코딩 관점: AI가 Money를 값 객체로 만드는 이유

AI가 `Money` 클래스를 만들면서 `@dataclass(frozen=True)`를 붙이는 이유가 있습니다. 금액은 변경되면 안 되는 **불변 값**입니다.

```python
from dataclasses import dataclass

@dataclass(frozen=True)  # 불변: 생성 후 변경 불가
class Money:
    amount: int

    def __add__(self, other: "Money") -> "Money":
        return Money(self.amount + other.amount)  # 새 객체 반환

    def __mul__(self, factor: int) -> "Money":
        return Money(self.amount * factor)

    def apply_discount(self, percent: int) -> "Money":
        return Money(self.amount - (self.amount * percent // 100))

@dataclass
class Book:
    book_id: str
    title: str
    price: Money

book = Book("B001", "Python 기초", Money(25000))
print(book.price.amount)           # 25000
print((book.price * 3).amount)     # 75000
print(book.price.apply_discount(10).amount)  # 22500
```

`frozen=True`는 "한 번 만들면 수정하지 말라"는 의도입니다. 금액이 중간에 바뀌면 버그가 생기기 때문에 AI가 이 패턴을 씁니다.

## 장바구니: 캡슐화 실전 예시

```python
@dataclass
class CartItem:
    book: Book
    quantity: int

    @property
    def total(self) -> Money:
        return self.book.price * self.quantity

class Cart:
    def __init__(self) -> None:
        self._items: dict[str, CartItem] = {}  # 내부 상태 보호

    def add(self, book: Book, quantity: int = 1) -> None:
        if book.book_id in self._items:
            existing = self._items[book.book_id]
            self._items[book.book_id] = CartItem(book, existing.quantity + quantity)
        else:
            self._items[book.book_id] = CartItem(book, quantity)

    @property
    def subtotal(self) -> Money:
        total = Money(0)
        for item in self._items.values():
            total = total + item.total
        return total

    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self._items.values())

cart = Cart()
cart.add(Book("B001", "Python 기초", Money(25000)), 2)
cart.add(Book("B002", "Django 실전", Money(35000)))
print(f"소계: {cart.subtotal.amount}원, {cart.item_count}권")
# 소계: 85000원, 3권
```

## 할인 정책: 전략 패턴 + OCP

```python
from typing import Protocol

class DiscountPolicy(Protocol):
    def calculate(self, subtotal: Money) -> Money: ...

class NoDiscount:
    def calculate(self, subtotal: Money) -> Money:
        return subtotal

class PercentDiscount:
    def __init__(self, percent: int) -> None:
        self._percent = percent

    def calculate(self, subtotal: Money) -> Money:
        return subtotal.apply_discount(self._percent)

class BulkDiscount:
    """5만원 이상 주문 시 10% 할인"""
    def calculate(self, subtotal: Money) -> Money:
        if subtotal.amount >= 50000:
            return subtotal.apply_discount(10)
        return subtotal

# 새 할인 정책 추가 = 새 클래스 추가만으로 충분
class MembershipDiscount:
    def __init__(self, member_level: str) -> None:
        self._level = member_level

    def calculate(self, subtotal: Money) -> Money:
        rates = {"gold": 15, "silver": 10, "bronze": 5}
        return subtotal.apply_discount(rates.get(self._level, 0))
```

## 전체 조립: OrderService

```python
class PaymentGateway(Protocol):
    def charge(self, amount: Money) -> bool: ...

class OrderRepository(Protocol):
    def save(self, order_data: dict) -> str: ...

class OrderService:
    def __init__(
        self,
        discount: DiscountPolicy,
        payment: PaymentGateway,
        repo: OrderRepository,
    ) -> None:
        self._discount = discount
        self._payment = payment
        self._repo = repo

    def checkout(self, cart: Cart) -> str | None:
        if cart.item_count == 0:
            print("장바구니가 비어있습니다")
            return None

        subtotal = cart.subtotal
        final = self._discount.calculate(subtotal)

        if not self._payment.charge(final):
            print("결제 실패")
            return None

        order_data = {
            "items": [(i.book.title, i.quantity) for i in cart._items.values()],
            "subtotal": subtotal.amount,
            "total": final.amount,
        }
        return self._repo.save(order_data)
```

## 실수 패턴

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 도메인 로직을 서비스에 넣음 | 모델이 빈껍데기(빈혈 도메인 모델)가 됩니다 | 비즈니스 로직은 도메인 모델에 넣습니다 |
| 모든 것을 한 번에 설계 | 과도한 추상화로 시작합니다 | 간단하게 시작하고 필요할 때 리팩터링합니다 |
| 값 객체를 가변으로 만듦 | 공유 참조 시 예기치 않은 변경입니다 | `frozen=True` 또는 읽기 전용으로 만듭니다 |
| 순환 의존성 | A가 B를, B가 A를 참조합니다 | 인터페이스를 분리하여 의존 방향을 통일합니다 |
| 테스트 없이 리팩터링 | 동작이 바뀌어도 알 수 없습니다 | 리팩터링 전 테스트를 작성합니다 |

## AI 팁: 기능 추가 시 어느 클래스를 수정해야 하는가?

AI가 만든 시스템에 기능을 추가할 때 이렇게 판단하세요.

```text
질문 1: 새 할인 정책을 추가하고 싶다
-> DiscountPolicy를 구현하는 새 클래스를 추가
-> OrderService 수정 없음

질문 2: 새 결제 수단을 추가하고 싶다
-> PaymentGateway를 구현하는 새 클래스를 추가
-> OrderService 수정 없음

질문 3: 장바구니에 새 규칙을 추가하고 싶다
-> Cart 클래스의 add() 메서드 수정
-> 다른 클래스 수정 없음

질문 4: 주문 저장 방식을 바꾸고 싶다
-> OrderRepository를 구현하는 새 클래스를 추가
-> OrderService 수정 없음
```

AI에게 "이 시스템에서 X 기능을 추가하려면 어느 클래스를 수정해야 하나?"라고 물어보면 설계를 이해하는 데 도움이 됩니다.

## 체크리스트

- [ ] 요구사항에서 클래스를 도출할 수 있다
- [ ] 값 객체와 엔티티를 구분하여 설계할 수 있다
- [ ] 합성과 DIP로 클래스 간 결합도를 낮출 수 있다
- [ ] 전략 패턴으로 교체 가능한 정책을 설계할 수 있다
- [ ] 기능 추가 시 어느 클래스를 수정해야 하는지 판단할 수 있다

## 처음 질문으로 돌아가기

- **AI가 만든 구조에서 어떤 클래스를 수정해야 할까요?**
  Protocol로 정의된 인터페이스를 보면 확장 지점을 알 수 있습니다. `DiscountPolicy`, `PaymentGateway`, `OrderRepository`가 Protocol이면 새 구현 클래스를 추가하면 됩니다.

- **값 객체와 엔티티는 어떻게 구분할까요?**
  `Money(1000) == Money(1000)` — 같은 값이면 같은 객체(값 객체). `Book("B001", ...) != Book("B001", ...)` — 같은 ID라도 다른 인스턴스(엔티티). AI가 `@dataclass(frozen=True)`를 쓰면 값 객체 패턴입니다.

- **할인 정책이 자주 바뀔 것 같다면?**
  전략 패턴(`DiscountPolicy Protocol`)을 쓰면 새 정책 추가 시 기존 코드를 수정하지 않아도 됩니다. AI에게 "할인 정책을 쉽게 추가할 수 있도록 전략 패턴을 적용해 줘"라고 요청하면 됩니다.

## 정리

실전 설계에서는 단일 원칙이 아니라 여러 OOP 원칙이 함께 적용됩니다. `Money`는 캡슐화, `Cart`는 정보 은닉, `DiscountPolicy`는 OCP, `OrderService`는 DIP를 각각 담당합니다. AI가 만든 코드가 복잡해 보여도 각 원칙이 왜 필요한지 이해하면 수정과 확장이 훨씬 쉬워집니다. 다음 글에서는 객체지향을 언제 쓰지 말아야 하는지 알아봅니다.

## 참고 자료

- [Python 공식 문서 — dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [Refactoring — Martin Fowler](https://refactoring.com/)
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
- 바이브코딩을 위한 객체지향 기초 (8/10): SOLID 원칙 기초
- **바이브코딩을 위한 객체지향 기초 (9/10): 객체지향 설계 예제 (현재 글)**
- 바이브코딩을 위한 객체지향 기초 (10/10): 객체지향을 언제 피해야 할까?

<!-- toc:end -->

Tags: Python, OOP, 설계 예제, 바이브코딩, 리팩터링, 클래스 설계
