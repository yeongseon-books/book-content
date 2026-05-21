---
title: "Object-Oriented Programming 101 (9/10): 객체지향 설계 예제"
series: oop-101
episode: 9
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
  - Python
  - OOP
  - 설계 예제
  - 리팩터링
  - 클래스 설계
last_reviewed: '2026-05-15'
seo_description: 온라인 서점 주문 시스템 예제로 OOP 설계와 리팩터링 과정을 단계별로 보여줍니다.
---

# Object-Oriented Programming 101 (9/10): 객체지향 설계 예제

개념을 따로 배울 때는 캡슐화, 상속, 다형성, 합성, SOLID가 각각 이해되는 듯 보입니다. 그런데 실제 기능 하나를 설계하려고 하면 갑자기 어려워집니다. 어디서 클래스를 나누고, 어떤 규칙은 지금 적용하고 어떤 규칙은 나중으로 미뤄야 할지 판단이 필요해지기 때문입니다.

그래서 실전 예제가 중요합니다. 좋은 설계는 처음부터 완벽한 다이어그램을 그려서 나오기보다, 동작하는 모델을 만들고 변경 가능성이 큰 지점에 유연성을 추가하면서 점점 다듬어집니다. 이 글에서는 그 흐름을 주문 시스템 예제로 따라가 보겠습니다.

이 글은 OOP 101 시리즈의 9번째 글입니다.

## 먼저 던지는 질문

- 요구사항에서 어떤 클래스를 도출하고, 어떤 책임을 어디에 둘지 어떻게 판단할까요?
- 값 객체, 엔티티, 서비스 클래스는 어떤 식으로 역할을 나누면 좋을까요?
- 할인 정책, 결제 수단, 저장소처럼 바뀌기 쉬운 요소는 어떻게 분리해야 할까요?

## 큰 그림

![Object-Oriented Programming 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/09/09-01-concept-overview.ko.png)

*Object-Oriented Programming 101 9장 흐름 개요*

## 핵심 개념 잡기

> 온라인 서점 주문 시스템 구조

```text
OrderService
├── Cart          -> cart management
├── Discount      -> discount policy (strategy pattern)
├── PaymentGateway -> payment processing (DIP)
└── OrderRepository -> order persistence (DIP)
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 도메인 모델 | 비즈니스 개념을 클래스로 표현한 것입니다 |
| 서비스 클래스 | 도메인 객체 간의 협력을 조율하는 클래스입니다 |
| 값 객체(value object) | 동등성으로 비교되는 불변 객체입니다 |
| 엔티티(entity) | 고유 식별자로 구분되는 객체입니다 |
| 리팩터링 | 동작을 유지하면서 코드 구조를 개선하는 것입니다 |

## 전후 비교

주문 처리 로직을 비교합니다.

```python
# before: procedural — all logic in a single function
def process_order(items, payment_type, discount_code):
    total = sum(item["price"] * item["qty"] for item in items)
    if discount_code == "SAVE10":
        total = int(total * 0.9)
    if payment_type == "card":
        print(f"Card payment: ${total}")
    elif payment_type == "bank":
        print(f"Bank transfer: ${total}")
    print(f"Order saved: ${total}, {len(items)} items")
```

```python
# after: OOP — responsibilities separated
class Order:
    def __init__(self, items: list["OrderItem"]) -> None:
        self.items = items

    @property
    def subtotal(self) -> int:
        return sum(item.total for item in self.items)

class OrderItem:
    def __init__(self, name: str, price: int, quantity: int) -> None:
        self.name = name
        self.price = price
        self.quantity = quantity

    @property
    def total(self) -> int:
        return self.price * self.quantity
```

## 단계별 실습

### 1단계: 도메인 모델 정의

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    """Value object — represents monetary amounts"""
    amount: int

    def __add__(self, other: "Money") -> "Money":
        return Money(self.amount + other.amount)

    def __mul__(self, factor: int) -> "Money":
        return Money(self.amount * factor)

    def apply_discount(self, percent: int) -> "Money":
        return Money(self.amount - (self.amount * percent // 100))

@dataclass
class Book:
    """Entity — identified by unique ID"""
    book_id: str
    title: str
    price: Money

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Book):
            return NotImplemented
        return self.book_id == other.book_id

book = Book("B001", "Python Basics", Money(25000))
print(book.price.amount)  # 25000
print((book.price * 3).amount)  # 75000
```

### 2단계: 장바구니 클래스

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
        self._items: dict[str, CartItem] = {}

    def add(self, book: Book, quantity: int = 1) -> None:
        if book.book_id in self._items:
            existing = self._items[book.book_id]
            self._items[book.book_id] = CartItem(book, existing.quantity + quantity)
        else:
            self._items[book.book_id] = CartItem(book, quantity)

    def remove(self, book_id: str) -> None:
        self._items.pop(book_id, None)

    @property
    def items(self) -> list[CartItem]:
        return list(self._items.values())

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
cart.add(Book("B001", "Python Basics", Money(25000)), 2)
cart.add(Book("B002", "Django in Practice", Money(35000)))
print(f"Subtotal: ${cart.subtotal.amount}, {cart.item_count} books")
# Subtotal: $85000, 3 books
```

### 3단계: 할인 정책 — 전략 패턴

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
    """10% off for orders over $50,000"""
    def calculate(self, subtotal: Money) -> Money:
        if subtotal.amount >= 50000:
            return subtotal.apply_discount(10)
        return subtotal

print(NoDiscount().calculate(Money(85000)).amount)       # 85000
print(PercentDiscount(20).calculate(Money(85000)).amount) # 68000
print(BulkDiscount().calculate(Money(85000)).amount)      # 76500
```

### 4단계: 결제 게이트웨이 — DIP

```python
from typing import Protocol

class PaymentGateway(Protocol):
    def charge(self, amount: Money) -> bool: ...

class CardPayment:
    def charge(self, amount: Money) -> bool:
        print(f"Card payment: ${amount.amount}")
        return True

class BankTransfer:
    def charge(self, amount: Money) -> bool:
        print(f"Bank transfer: ${amount.amount}")
        return True

class OrderRepository(Protocol):
    def save(self, order_data: dict) -> str: ...

class InMemoryOrderRepo:
    def __init__(self) -> None:
        self._orders: dict[str, dict] = {}
        self._counter = 0

    def save(self, order_data: dict) -> str:
        self._counter += 1
        order_id = f"ORD-{self._counter:04d}"
        self._orders[order_id] = order_data
        print(f"Order saved: {order_id}")
        return order_id
```

### 5단계: 주문 서비스 — 전체 조립

```python
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
            print("Cart is empty")
            return None

        subtotal = cart.subtotal
        final = self._discount.calculate(subtotal)

        success = self._payment.charge(final)
        if not success:
            print("Payment failed")
            return None

        order_data = {
            "items": [(i.book.title, i.quantity) for i in cart.items],
            "subtotal": subtotal.amount,
            "total": final.amount,
        }
        return self._repo.save(order_data)

# Assembly and execution
cart = Cart()
cart.add(Book("B001", "Python Basics", Money(25000)), 2)
cart.add(Book("B002", "Django in Practice", Money(35000)))

service = OrderService(
    discount=BulkDiscount(),
    payment=CardPayment(),
    repo=InMemoryOrderRepo(),
)

order_id = service.checkout(cart)
# Card payment: $76500
# Order saved: ORD-0001
print(f"Order complete: {order_id}")  # Order complete: ORD-0001
```

## 이 코드에서 주목할 점

- `Money`는 값 객체로 금액 연산을 안전하게 캡슐화합니다
- `Cart`는 내부 딕셔너리를 숨기고 메서드로만 접근하게 합니다(캡슐화)
- `DiscountPolicy`는 전략 패턴으로 할인 정책을 런타임에 교체합니다(OCP)
- `OrderService`는 모든 의존성을 Protocol로 받아 교체와 테스트가 쉽습니다(DIP)

## 자주 하는 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 도메인 로직을 서비스에 넣음 | 모델이 빈껍데기(빈혈 도메인 모델)가 됩니다 | 비즈니스 로직은 도메인 모델에 넣습니다 |
| 모든 것을 한 번에 설계 | 과도한 추상화로 시작합니다 | 간단하게 시작하고 필요할 때 리팩터링합니다 |
| 값 객체를 가변으로 만듦 | 공유 참조 시 예기치 않은 변경입니다 | `frozen=True` 또는 읽기 전용으로 만듭니다 |
| 순환 의존성 | A가 B를, B가 A를 참조합니다 | 인터페이스를 분리하여 의존 방향을 통일합니다 |
| 테스트 없이 리팩터링 | 동작이 바뀌어도 알 수 없습니다 | 리팩터링 전 테스트를 작성합니다 |

## 실무에서 이렇게 쓰입니다

- 이커머스 플랫폼에서 장바구니, 결제, 할인을 분리 설계합니다
- 도메인 주도 설계(DDD)에서 엔티티와 값 객체 패턴을 활용합니다
- 결제 게이트웨이 교체(PG사 변경)를 Protocol로 대응합니다
- 마이크로서비스에서 각 서비스의 도메인 모델을 독립적으로 설계합니다
- A/B 테스트에서 할인 정책을 전략 패턴으로 교체합니다

## 현업 개발자는 이렇게 생각합니다

좋은 설계의 핵심은 "변경이 예상되는 곳에 유연성을 두는 것"입니다. 할인 정책이 자주 바뀔 것이라면 전략 패턴으로, 결제 수단이 추가될 것이라면 DIP로 대비합니다.

처음부터 모든 것을 완벽하게 설계하려 하지 마세요. 동작하는 간단한 코드를 먼저 작성하고, 중복이나 결합도가 문제가 될 때 원칙을 적용하여 리팩터링하는 것이 실무적 접근입니다.

## 실전에서 먼저 깨지는 지점

| 먼저 흔들리는 지점 | 전형적인 증상 | 대응 포인트 |
|--------------------|--------------|-------------|
| 결제 게이트웨이 | 승인 실패와 저장 실패가 뒤섞여 재시도 기준이 모호합니다 | 결제 성공/실패를 도메인 이벤트처럼 분리하고 저장은 그 뒤에 수행합니다 |
| 할인 정책 | 주문 금액 계산 로직이 서비스 메서드 안 분기문으로 커집니다 | 정책 객체를 유지하고, 조합 규칙만 별도 팩토리나 룰 엔진으로 올립니다 |
| 저장소 | 테스트는 빠른데 실제 DB 붙이면 트랜잭션 경계가 달라집니다 | 저장소 인터페이스를 유지한 채 커밋 시점과 예외 번역 규칙을 명시합니다 |
| 장바구니 모델 | 수량 변경, 재고 확인, 쿠폰 적용 책임이 한 클래스에 몰립니다 | 상태 변경 메서드와 검증 메서드를 분리하고, 재고 확인은 별도 협력 객체로 둡니다 |

## 안전하게 리팩터링하는 순서

1. 먼저 현재 절차지향 흐름을 테스트로 고정합니다.
2. 그다음 계산 로직처럼 순수한 부분부터 값 객체(`Money`)로 옮깁니다.
3. 외부 I/O가 섞인 결제와 저장은 마지막에 Protocol 경계 뒤로 밀어냅니다.
4. 마지막으로 조립 코드에서 어떤 구현을 넣을지 결정하게 만들어, 도메인 모델이 프레임워크나 인프라를 직접 모르도록 유지합니다.

## 체크리스트

- [ ] 요구사항에서 클래스를 도출할 수 있다
- [ ] 값 객체와 엔티티를 구분하여 설계할 수 있다
- [ ] 합성과 DIP로 클래스 간 결합도를 낮출 수 있다
- [ ] 전략 패턴으로 교체 가능한 정책을 설계할 수 있다
- [ ] 절차지향 코드를 객체지향으로 리팩터링할 수 있다

## 정리 및 다음 글 안내

실전 설계에서는 단일 원칙이 아니라 여러 OOP 원칙이 함께 적용됩니다. 간단하게 시작하고, 변경이 필요할 때 점진적으로 개선하는 것이 현실적인 접근입니다. 다음 글에서는 객체지향을 언제 사용하지 말아야 하는지 알아봅니다.

## 설계 예제를 UML 텍스트로 먼저 고정하기

코드를 쓰기 전에 협력 구조를 텍스트 UML로 먼저 고정하면, 리팩터링 중에도 책임 경계가 흔들리지 않습니다.

```text
[TicketController]
    |
    v
[TicketService]
  + create_ticket()
  + close_ticket()
    |
    +--> [TicketRepository]
    +--> [AssignmentPolicy]
    +--> [NotificationPort]

[Ticket]
  - id
  - status
  - assignee
  + assign_to()
  + close()
```

## before/after: 서비스 메서드 단일 거대 함수 분해

```python
# before

def create_ticket(payload: dict, db, slack_client):
    # 파싱, 검증, 담당자 선정, 저장, 알림 전송이 모두 혼재
    ...
```

```python
# after
from dataclasses import dataclass

@dataclass
class Ticket:
    id: str
    title: str
    status: str = 'open'
    assignee: str | None = None

    def assign_to(self, engineer: str) -> None:
        if self.status != 'open':
            raise ValueError('only open ticket can be assigned')
        self.assignee = engineer

    def close(self) -> None:
        if self.status == 'closed':
            raise ValueError('already closed')
        self.status = 'closed'

class RoundRobinAssignmentPolicy:
    def __init__(self, members: list[str]) -> None:
        self.members = members
        self._index = 0

    def pick(self) -> str:
        engineer = self.members[self._index % len(self.members)]
        self._index += 1
        return engineer
```

## 위반과 교정

| 위반 | 운영 문제 | 교정 |
|---|---|---|
| 컨트롤러가 도메인 상태 전이를 직접 수정 | API별 규칙 불일치 | 도메인 메서드로 상태 전이 통일 |
| 정책이 서비스에 하드코딩 | 실험/교체 난이도 상승 | 정책 객체 주입 |
| 알림 실패가 트랜잭션과 결합 | 핵심 기능까지 롤백 | outbox/비동기 알림으로 분리 |

## 비교표: 리팩터링 전후

| 항목 | 리팩터링 전 | 리팩터링 후 |
|---|---|---|
| 코드 탐색 | 한 함수 내부 추적 | 객체 경계별 탐색 |
| 테스트 | 통합 테스트 의존 | 도메인 단위 테스트 가능 |
| 변경 대응 | 수정 충돌 빈번 | 영향 범위 축소 |

## 실전 시나리오: 요구사항 변경을 견디는 구조로 바꾸기

현업에서는 기능 추가보다 규칙 변경이 더 자주 발생합니다. 따라서 클래스 구조를 평가할 때는 "지금 동작하는가"보다 "다음 변경을 어디까지 건드려야 하는가"를 기준으로 보는 편이 안전합니다.

```python
from dataclasses import dataclass
from typing import Protocol


@dataclass
class LineItem:
    name: str
    quantity: int
    unit_price: int

    def subtotal(self) -> int:
        return self.quantity * self.unit_price


class DiscountPolicy(Protocol):
    def apply(self, amount: int) -> int:
        ...


class NoDiscount:
    def apply(self, amount: int) -> int:
        return amount


class PercentDiscount:
    def __init__(self, percent: int) -> None:
        if not 0 <= percent <= 100:
            raise ValueError('percent must be 0..100')
        self.percent = percent

    def apply(self, amount: int) -> int:
        return int(amount * (100 - self.percent) / 100)


class Invoice:
    def __init__(self, items: list[LineItem], policy: DiscountPolicy) -> None:
        self.items = items
        self.policy = policy

    def total(self) -> int:
        base = sum(i.subtotal() for i in self.items)
        return self.policy.apply(base)
```

이 코드는 할인 규칙이 바뀌어도 `Invoice.total()`을 수정할 필요가 없습니다. 확장은 구현 클래스 추가로 닫히고, 핵심 흐름은 안정적으로 유지됩니다.

## UML 스타일로 보는 협력 관계

```text
[Invoice]
  - items: list[LineItem]
  - policy: DiscountPolicy
  + total()

[LineItem]
  + subtotal()

[DiscountPolicy] <<interface>>
  + apply(amount)
      ^
      +-- [NoDiscount]
      +-- [PercentDiscount]
```

협력 구조를 이렇게 텍스트로 적어 두면 코드 리뷰에서 "어디가 정책 축이고 어디가 도메인 축인가"를 빠르게 맞출 수 있습니다.

## 안티패턴과 교정 절차

| 안티패턴 | 발견 신호 | 교정 순서 |
|---|---|---|
| 거대 클래스(God Object) | 메서드가 20개 이상, 변경 이력이 분산됨 | 책임 축 분해 → 협력 인터페이스 도출 |
| 데이터만 가진 빈 클래스 | 메서드 없이 getter/setter만 존재 | 규칙 메서드 이동 또는 dataclass로 단순화 |
| 상속 트리 우회 분기 | 하위 클래스 타입 체크 분기 존재 | 다형성 계약 재정의 |
| 인프라 타입 누수 | 도메인 계층이 SDK 응답 객체 의존 | DTO 변환 계층 추가 |

## 전후 비교: 테스트 유지비

| 항목 | 리팩터링 전 | 리팩터링 후 |
|---|---|---|
| 테스트 준비 | 전역 상태 초기화 필요 | 객체 단위 상태 생성 |
| 실패 원인 추적 | 함수 체인 전체 역추적 | 클래스 메서드 단위 추적 |
| 회귀 범위 | 넓고 불명확 | 좁고 예측 가능 |

## 팀 적용 체크리스트

- 도메인 용어와 클래스 이름이 일치하는지 확인합니다.
- 인스턴스 생성 시점에 불변식이 완성되는지 확인합니다.
- 정책 변경이 기존 코드 수정이 아닌 구현 추가로 가능한지 점검합니다.
- 코드 리뷰에서 UML 텍스트 10줄로 협력 구조를 먼저 합의합니다.
- 테스트 이름이 메서드명보다 비즈니스 규칙을 설명하는지 확인합니다.

## 미니 케이스 스터디: 규칙 추가 한 번으로 검증하기

아래 예시는 정책 확장을 기존 코드 수정 없이 추가하는 최소 단위입니다.

```python
class WeekendPolicy:
    def apply(self, amount: int, is_weekend: bool) -> int:
        if is_weekend:
            return int(amount * 0.95)
        return amount


def estimate(amount: int, is_weekend: bool) -> int:
    policy = WeekendPolicy()
    return policy.apply(amount, is_weekend)
```

핵심은 새로운 정책이 호출 경로를 깨지 않고 들어온다는 점입니다. 변경 이력이 정책 클래스에만 남도록 경계를 유지하면 회귀 위험이 줄어듭니다.

| 확인 질문 | Pass 기준 |
|---|---|
| 새 정책 추가 시 기존 함수 수정이 필요한가 | 아니오 |
| 예외 정책이 기존 계약과 같은가 | 예 |
| 테스트가 정책별로 분리되어 있는가 | 예 |


## 리팩터링 회고: 변경 비용을 수치로 보는 방법

- 수정 파일 수가 기능 하나당 5개를 넘으면 경계 재설계를 검토합니다.
- 타입 분기 if/elif가 3개 이상 누적되면 다형성 또는 전략 객체로 이동합니다.
- 회귀 테스트 작성 시간이 구현 시간보다 길어지면 책임 배치를 재검토합니다.

```python
def complexity_signal(changed_files: int, branch_count: int) -> str:
    if changed_files >= 5 or branch_count >= 3:
        return 'refactor-needed'
    return 'acceptable'
```

위 방식은 엄밀한 메트릭은 아니지만, 팀이 감각이 아니라 기준으로 논의하게 만드는 데 유용합니다.

## 검증 노트: 객체 설계 품질을 점검하는 질문

아래 질문은 구현 이후 리뷰에서 반복적으로 사용하는 기준입니다.

- 이 메서드가 실패할 때 예외 타입과 메시지가 호출자 계약과 일치하는가.
- 같은 규칙이 다른 클래스나 함수에 중복되어 있지 않은가.
- 상태 변경이 메서드 한 경로로만 이루어지는가.
- 외부 의존성 없이 단위 테스트가 가능한가.

```python
def review_signal(duplicate_rules: int, mutable_paths: int) -> str:
    if duplicate_rules > 0:
        return '중복 규칙 제거 필요'
    if mutable_paths > 1:
        return '상태 변경 경로 통합 필요'
    return '구조 안정'
```

이런 체크를 글 단위 예제에도 적용하면, 객체지향을 문법이 아니라 유지보수 전략으로 이해하는 데 도움이 됩니다.

## 한 줄 정리 확장

객체지향 품질은 클래스 개수가 아니라 변경 영향 범위를 얼마나 줄였는지로 판단합니다.

## 보강 메모

설계 선택은 정답 찾기가 아니라 변경 비용을 낮추는 의사결정입니다. 같은 기능이라도 경계를 먼저 정의하면 리뷰와 테스트가 단순해집니다.

## 처음 질문으로 돌아가기

- **요구사항에서 어떤 클래스를 도출하고, 어떤 책임을 어디에 둘지 어떻게 판단할까요?**
  - 본문의 기준은 객체지향 설계 예제를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **값 객체, 엔티티, 서비스 클래스는 어떤 식으로 역할을 나누면 좋을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **할인 정책, 결제 수단, 저장소처럼 바뀌기 쉬운 요소는 어떻게 분리해야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Object-Oriented Programming 101 (1/10): 객체지향이란 무엇인가?](./01-what-is-oop.md)
- [Object-Oriented Programming 101 (2/10): 클래스와 인스턴스](./02-classes-and-instances.md)
- [Object-Oriented Programming 101 (3/10): 캡슐화](./03-encapsulation.md)
- [Object-Oriented Programming 101 (4/10): 상속](./04-inheritance.md)
- [Object-Oriented Programming 101 (5/10): 다형성](./05-polymorphism.md)
- [Object-Oriented Programming 101 (6/10): 추상화](./06-abstraction.md)
- [Object-Oriented Programming 101 (7/10): 합성과 상속](./07-composition-vs-inheritance.md)
- [Object-Oriented Programming 101 (8/10): SOLID 원칙 기초](./08-solid-principles.md)
- **객체지향 설계 예제 (현재 글)**
- 객체지향을 언제 피해야 할까? (예정)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [Python 공식 문서 — typing.Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol)
- [Refactoring — Martin Fowler](https://refactoring.com/)
- [Domain-Driven Design — Eric Evans](https://www.oreilly.com/library/view/domain-driven-design/0321125215/)

Tags: Python, OOP, 설계 예제, 리팩터링, 클래스 설계
