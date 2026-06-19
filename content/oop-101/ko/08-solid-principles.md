---
title: "Object-Oriented Programming 101 (8/10): SOLID 원칙 기초"
series: oop-101
episode: 8
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
  - SOLID
  - 설계 원칙
  - 클린 코드
last_reviewed: '2026-05-17'
seo_description: SOLID 다섯 원칙을 Python 예제와 함께 실무적으로 적용하는 기준을 정리합니다.
---

# Object-Oriented Programming 101 (8/10): SOLID 원칙 기초

SOLID가 진짜 와닿는 순간은 서비스 하나가 계속 커지면서 새로운 요구사항이 들어올 때마다 엉뚱한 코드까지 함께 흔들릴 때입니다. 할인 정책 하나를 바꿨는데 배송 코드가 깨지거나, 이메일 발송 로직을 수정했더니 결제 테스트가 실패하는 상황이 그 예입니다.

SOLID는 이러한 변경 파급을 줄이기 위한 설계 원칙 다섯 가지입니다. 각 원칙을 따로 외우는 것보다, 하나의 주문 처리 흐름에서 원칙을 하나씩 적용해 보는 것이 훨씬 효과적입니다.

이 글은 OOP 101 시리즈의 8번째 글입니다.

![Object-Oriented Programming 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/08/08-01-big-picture.ko.png)
*Object-Oriented Programming 101 8장 흐름 개요*

## 이 글에서 다룰 문제

- SRP, OCP, LSP, ISP, DIP는 각각 어떤 문제를 해결하나요?
- SOLID 원칙을 동시에 적용하면 코드 구조가 어떻게 달라지나요?
- 작은 프로젝트에서도 SOLID를 지켜야 할까요, 아니면 어느 시점부터 적용하는 것이 좋을까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 이 글에서 배울 것

- SRP: 클래스의 변경 이유를 하나로 제한하는 방법을 익힙니다
- OCP: 기존 코드를 수정하지 않고 기능을 확장하는 패턴을 배웁니다
- LSP: 하위 타입 치환이 안전한지 판단하는 기준을 세웁니다
- ISP: 인터페이스를 작게 유지하는 이유를 이해합니다
- DIP: 구체 구현이 아닌 추상에 의존하는 방법을 실습합니다

## 핵심 개념

| 원칙 | 이름 | 핵심 |
|------|------|------|
| SRP | 단일 책임 원칙 | 한 클래스는 변경 이유가 하나여야 합니다 |
| OCP | 개방-폐쇄 원칙 | 확장에는 열려 있고, 수정에는 닫혀 있어야 합니다 |
| LSP | 리스코프 치환 원칙 | 자식은 부모를 무리 없이 대체할 수 있어야 합니다 |
| ISP | 인터페이스 분리 원칙 | 클라이언트는 사용하지 않는 인터페이스에 의존하면 안 됩니다 |
| DIP | 의존성 역전 원칙 | 상위 모듈이 하위 구현에 직접 의존하면 안 됩니다 |

## 단계별 실습: 주문 처리 시스템으로 보는 SOLID

### 1단계: SRP — 단일 책임 원칙

```python
# SRP 위반: OrderService가 너무 많은 일을 함
class OrderServiceBad:
    def checkout(self, order, payment):
        # 주문 검증
        if not order.items:
            raise ValueError("Empty order")
        # 결제 처리
        print(f"Charging {payment.amount}")
        # 이메일 발송
        print(f"Sending email to {order.customer_email}")
        # 재고 감소
        for item in order.items:
            print(f"Reducing stock for {item.product_id}")
```

```python
# SRP 준수: 각 책임을 별도 클래스로 분리
from dataclasses import dataclass, field
from typing import Protocol

@dataclass
class OrderItem:
    product_id: str
    quantity: int
    unit_price: int

    def subtotal(self) -> int:
        return self.quantity * self.unit_price

@dataclass
class Order:
    customer_email: str
    items: list[OrderItem] = field(default_factory=list)

    def total_amount(self) -> int:
        return sum(item.subtotal() for item in self.items)

class OrderValidator:
    def validate(self, order: Order) -> None:
        if not order.items:
            raise ValueError("Order must have at least one item")
        if order.total_amount() <= 0:
            raise ValueError("Order total must be positive")

class EmailNotifier:
    def send_confirmation(self, email: str, order_id: str) -> None:
        print(f"[Email] Order {order_id} confirmed -> {email}")

class InventoryService:
    def reserve(self, items: list[OrderItem]) -> None:
        for item in items:
            print(f"[Inventory] Reserved {item.quantity}x {item.product_id}")
```

각 클래스의 변경 이유: `OrderValidator`는 검증 규칙, `EmailNotifier`는 알림 형식, `InventoryService`는 재고 로직이 바뀔 때만 수정합니다.

### 2단계: OCP — 개방-폐쇄 원칙

```python
# OCP 위반: 새 할인을 추가할 때마다 checkout()을 수정해야 함
def checkout_bad(order: Order, discount_type: str) -> int:
    total = order.total_amount()
    if discount_type == "percent":
        return int(total * 0.9)
    elif discount_type == "flat":
        return max(0, total - 5000)
    # 새 타입 추가 시 여기를 수정해야 함
    return total
```

```python
# OCP 준수: 확장은 새 클래스 추가, 기존 코드는 수정 없음
class DiscountPolicy(Protocol):
    def apply(self, amount: int) -> int: ...

class NoDiscount:
    def apply(self, amount: int) -> int:
        return amount

class PercentDiscount:
    def __init__(self, rate: float) -> None:
        self.rate = rate

    def apply(self, amount: int) -> int:
        return int(amount * (1 - self.rate))

class FlatDiscount:
    def __init__(self, amount: int) -> None:
        self.flat = amount

    def apply(self, amount: int) -> int:
        return max(0, amount - self.flat)

class BuyTwoGetOneDiscount:
    """신규 정책 — 기존 코드 수정 없이 추가"""
    def apply(self, amount: int) -> int:
        return int(amount * 0.67)

def checkout(order: Order, discount: DiscountPolicy) -> int:
    return discount.apply(order.total_amount())
```

### 3단계: LSP — 리스코프 치환 원칙

```python
# LSP 위반: Rectangle을 Square로 치환하면 계약이 깨짐
class Rectangle:
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

class Square(Rectangle):
    def __init__(self, side: float) -> None:
        super().__init__(side, side)

    @Rectangle.width.setter
    def width(self, value: float) -> None:
        self._width = value
        self._height = value  # 정사각형은 항상 같아야 해서 height도 바꿈

def scale_width(rect: Rectangle, new_width: float) -> float:
    rect.width = new_width
    return rect.area()  # Rectangle: new_width * height / Square: new_width^2
```

```python
# LSP 준수: 상속 계층 대신 별도 추상화
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

class Rectangle(Shape):
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

class Square(Shape):
    def __init__(self, side: float) -> None:
        self.side = side

    def area(self) -> float:
        return self.side ** 2

def total_area(shapes: list[Shape]) -> float:
    return sum(s.area() for s in shapes)

print(total_area([Rectangle(3, 4), Square(5)]))  # 37.0
```

### 4단계: ISP — 인터페이스 분리 원칙

```python
# ISP 위반: 거대 인터페이스 — 일부 메서드만 필요한 구현체에 불필요한 의무
from abc import ABC, abstractmethod

class AllInOneWorker(ABC):
    @abstractmethod
    def read_file(self, path: str) -> bytes: ...
    @abstractmethod
    def write_file(self, path: str, data: bytes) -> None: ...
    @abstractmethod
    def send_email(self, to: str, body: str) -> None: ...
    @abstractmethod
    def query_db(self, sql: str) -> list: ...
```

```python
# ISP 준수: 작은 인터페이스로 분리
from typing import Protocol

class FileReader(Protocol):
    def read_file(self, path: str) -> bytes: ...

class FileWriter(Protocol):
    def write_file(self, path: str, data: bytes) -> None: ...

class EmailSender(Protocol):
    def send_email(self, to: str, body: str) -> None: ...

class ReportService:
    def __init__(self, reader: FileReader, sender: EmailSender) -> None:
        self._reader = reader
        self._sender = sender

    def send_report(self, path: str, recipient: str) -> None:
        data = self._reader.read_file(path)
        self._sender.send_email(recipient, data.decode())
```

### 5단계: DIP — 의존성 역전 원칙

```python
# DIP 위반: OrderService가 구체 구현에 직접 의존
class OrderServiceBad:
    def __init__(self) -> None:
        self._db = PostgresDatabase()    # 구체 클래스 직접 생성
        self._mailer = SendgridMailer()  # 구체 클래스 직접 생성

    def place(self, order: Order) -> None:
        self._db.save(order)
        self._mailer.send(order.customer_email)
```

```python
# DIP 준수: 추상에 의존, 외부에서 주입
from typing import Protocol

class OrderRepository(Protocol):
    def save(self, order: Order) -> None: ...

class MailService(Protocol):
    def send_confirmation(self, email: str, order_id: str) -> None: ...

class OrderService:
    def __init__(
        self,
        repository: OrderRepository,
        mailer: MailService,
        validator: OrderValidator,
    ) -> None:
        self._repo = repository
        self._mailer = mailer
        self._validator = validator

    def place(self, order: Order) -> str:
        self._validator.validate(order)
        order_id = f"ORD-{id(order):x}"
        self._repo.save(order)
        self._mailer.send_confirmation(order.customer_email, order_id)
        return order_id

# 테스트용 In-Memory 구현
class InMemoryOrderRepository:
    def __init__(self) -> None:
        self._store: list[Order] = []

    def save(self, order: Order) -> None:
        self._store.append(order)

class MockMailer:
    def __init__(self) -> None:
        self.sent: list[dict] = []

    def send_confirmation(self, email: str, order_id: str) -> None:
        self.sent.append({"email": email, "order_id": order_id})

# 조립
repo = InMemoryOrderRepository()
mailer = MockMailer()
service = OrderService(repo, mailer, OrderValidator())

order = Order("alice@example.com", [OrderItem("P001", 2, 15000)])
order_id = service.place(order)
print(order_id)
print(mailer.sent)  # [{'email': 'alice@example.com', 'order_id': '...'}]
```

## 자주 하는 실수

| 원칙 | 흔한 실수 | 해결 방법 |
|------|----------|----------|
| SRP | 서비스 클래스에 검증, 저장, 알림 모두 포함 | 각 책임을 별도 클래스로 분리합니다 |
| OCP | 새 정책 추가 시 기존 메서드에 elif 추가 | Protocol + 새 클래스 추가로 확장합니다 |
| LSP | 부모 계약을 하위 클래스에서 강화 또는 약화 | 부모와 동일한 사전/사후 조건을 유지합니다 |
| ISP | 하나의 대형 Protocol에 모든 메서드 정의 | 사용 단위별로 작은 Protocol로 분리합니다 |
| DIP | 서비스 내부에서 `SomeClass()` 직접 생성 | 생성자 주입으로 의존성을 외부에서 제공받습니다 |

## 실무에서 이렇게 쓰입니다

SOLID는 규칙 목록이 아니라 설계 판단의 언어입니다. 코드 리뷰에서 "이 메서드가 변경되는 이유가 둘 이상인가?"(SRP), "새 기능을 추가할 때 이 파일을 수정해야 하나?"(OCP)처럼 질문으로 활용합니다.

모든 코드에 SOLID를 처음부터 적용할 필요는 없습니다. 기능이 두 번 이상 변경될 때, 같은 수정이 여러 파일에 동시에 필요할 때, 테스트가 점점 복잡해질 때가 리팩터링 타이밍입니다.

## 운영 체크리스트

- [ ] SRP: 클래스의 변경 이유가 하나인지 확인할 수 있다
- [ ] OCP: 새 기능 추가 시 기존 코드 수정 없이 가능한지 점검할 수 있다
- [ ] LSP: 하위 클래스를 부모 타입으로 안전하게 교체할 수 있다
- [ ] ISP: 사용하지 않는 메서드에 의존하는 클래스가 없는지 확인할 수 있다
- [ ] DIP: 생성자 주입으로 의존성을 외부에서 제공할 수 있다

## 연습 문제

1. `UserService` 클래스가 사용자 생성, 이메일 발송, 비밀번호 해싱, DB 저장을 모두 하고 있습니다. SRP를 적용하여 분리하세요.
2. 보고서 출력 시스템이 PDF, Excel, HTML 형식을 `if/elif`로 처리합니다. OCP를 적용하여 새 형식을 기존 코드 수정 없이 추가할 수 있게 만드세요.
3. `PaymentService`가 `StripeGateway()`를 내부에서 직접 생성합니다. DIP를 적용하여 테스트에서 Mock으로 교체할 수 있게 만드세요.

## 정리 및 다음 단계

SOLID는 "어디를 수정해야 하는가"를 명확하게 만드는 설계 언어입니다. 한 번에 다섯 원칙 모두를 적용하려 하기보다, 코드가 아프기 시작할 때 가장 필요한 원칙 하나부터 적용합니다.

다음 글에서는 지금까지 배운 OOP 개념을 온라인 서점 주문 시스템 설계에 통합적으로 적용합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Object-Oriented Programming 101 (1/10): 객체지향이란 무엇인가?](./01-what-is-oop.md)
- [Object-Oriented Programming 101 (2/10): 클래스와 인스턴스](./02-classes-and-instances.md)
- [Object-Oriented Programming 101 (3/10): 캡슐화](./03-encapsulation.md)
- [Object-Oriented Programming 101 (4/10): 상속](./04-inheritance.md)
- [Object-Oriented Programming 101 (5/10): 다형성](./05-polymorphism.md)
- [Object-Oriented Programming 101 (6/10): 추상화](./06-abstraction.md)
- [Object-Oriented Programming 101 (7/10): 합성과 상속](./07-composition-vs-inheritance.md)
- **Object-Oriented Programming 101 (8/10): SOLID 원칙 기초 (현재 글)**
- [Object-Oriented Programming 101 (9/10): 객체지향 설계 예제](./09-oop-design-example.md)
- [객체지향을 언제 피해야 할까?](./10-when-to-avoid-oop.md)

<!-- toc:end -->

## 참고 자료

- [PEP 544 — Protocols: Structural subtyping](https://peps.python.org/pep-0544/)
- [Python abc 공식 문서](https://docs.python.org/3/library/abc.html)
- [Real Python — SOLID Principles](https://realpython.com/solid-principles-python/)
- [Clean Code — Robert C. Martin](https://www.oreilly.com/library/view/clean-code/9780136083238/)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/oop-101/ko)
Tags: Python, OOP, SOLID, 설계 원칙, 클린 코드
