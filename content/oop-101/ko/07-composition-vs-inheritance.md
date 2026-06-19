---
title: "Object-Oriented Programming 101 (7/10): 합성과 상속"
series: oop-101
episode: 7
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
  - 합성
  - 상속
  - 설계 패턴
last_reviewed: '2026-05-15'
seo_description: 합성과 상속의 차이, 위임, 의존성 주입까지 실무 선택 기준으로 비교합니다.
---

# Object-Oriented Programming 101 (7/10): 합성과 상속

객체지향 설계에서 가장 자주 나오는 질문 하나를 꼽으라면 이것입니다. 기존 클래스를 확장할 때 상속을 써야 할까, 아니면 다른 객체를 내부에 두는 합성을 써야 할까. 둘 다 재사용을 돕지만, 변경 비용과 테스트 방식은 크게 달라집니다.

상속은 타입 관계가 명확하고 LSP가 성립할 때 강력합니다. 합성은 행위를 교체하거나 조합해야 할 때 더 유연합니다. 실무에서는 "is-a" 관계인가를 먼저 확인하고, 아니라면 합성을 선택하는 것이 대부분 더 안전합니다.

이 글은 OOP 101 시리즈의 7번째 글입니다.

![Object-Oriented Programming 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/07/07-01-big-picture.ko.png)
*Object-Oriented Programming 101 7장 흐름 개요*

## 이 글에서 다룰 문제

- "상속보다 합성을 선호하라"는 말이 실무에서 어떤 상황에 적용될까요?
- 위임(delegation) 패턴은 합성과 어떻게 다르고, 언제 쓰면 적합할까요?
- 의존성 주입으로 합성 관계를 더 유연하게 만드는 방법은 무엇일까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 이 글에서 배울 것

- 합성과 상속의 구조적 차이를 코드로 비교합니다
- 위임 패턴을 활용해 합성 객체에 행위를 위임합니다
- 전략 패턴으로 알고리즘을 런타임에 교체하는 법을 익힙니다
- 의존성 주입(DI)으로 합성 관계를 테스트 친화적으로 만듭니다
- "is-a" vs "has-a" 판단 기준을 실무 예시로 확인합니다

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 합성(composition) | 다른 객체를 멤버로 포함하여 기능을 구성하는 방식입니다 |
| 위임(delegation) | 메서드 호출을 내부 객체에게 전달하는 패턴입니다 |
| 전략 패턴(strategy) | 알고리즘을 별도 객체로 캡슐화하여 교체 가능하게 만듭니다 |
| 의존성 주입(DI) | 객체가 의존하는 객체를 외부에서 주입받는 패턴입니다 |
| Mixin | 다중 상속으로 기능을 추가하는 소규모 클래스입니다 |

## 전후 비교

자동차 기능 구현을 비교합니다.

```python
# before: 상속으로 모든 기능을 구현 — 기능 조합이 어려워짐
class Car:
    def drive(self): return "Driving"

class GPSCar(Car):
    def navigate(self): return "Navigating"

class GPSCarWithAudio(GPSCar):
    def play_music(self): return "Playing music"

# GPS 없이 Audio만 있는 차를 만들면? 계층이 폭발함
```

```python
# after: 합성으로 기능 조합 — 유연하고 교체 가능
from typing import Protocol

class GPSUnit(Protocol):
    def navigate(self, destination: str) -> str: ...

class AudioSystem(Protocol):
    def play(self, track: str) -> str: ...

class TomTomGPS:
    def navigate(self, destination: str) -> str:
        return f"TomTom: Navigating to {destination}"

class GoogleGPS:
    def navigate(self, destination: str) -> str:
        return f"Google: Route to {destination} found"

class BasicAudio:
    def play(self, track: str) -> str:
        return f"Playing: {track}"

class Car:
    def __init__(
        self,
        gps: GPSUnit | None = None,
        audio: AudioSystem | None = None,
    ) -> None:
        self._gps = gps
        self._audio = audio

    def navigate(self, destination: str) -> str:
        if self._gps is None:
            return "No GPS installed"
        return self._gps.navigate(destination)

    def play(self, track: str) -> str:
        if self._audio is None:
            return "No audio system"
        return self._audio.play(track)

# GPS와 Audio를 런타임에 교체 가능
car = Car(gps=GoogleGPS(), audio=BasicAudio())
print(car.navigate("Seoul"))      # Google: Route to Seoul found
print(car.play("My Favorite Song"))  # Playing: My Favorite Song

# GPS만 있는 차
gps_only = Car(gps=TomTomGPS())
print(gps_only.navigate("Busan"))  # TomTom: Navigating to Busan
print(gps_only.play("Track 1"))   # No audio system
```

## 단계별 실습

### 1단계: 합성으로 로거 구성

```python
from typing import Protocol

class LogHandler(Protocol):
    def emit(self, level: str, message: str) -> None: ...

class ConsoleHandler:
    def emit(self, level: str, message: str) -> None:
        print(f"[{level.upper()}] {message}")

class FileHandler:
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def emit(self, level: str, message: str) -> None:
        print(f"[FILE:{self.filename}] [{level.upper()}] {message}")

class Logger:
    def __init__(self, name: str, handlers: list[LogHandler]) -> None:
        self.name = name
        self._handlers = handlers

    def info(self, message: str) -> None:
        self._emit("info", message)

    def error(self, message: str) -> None:
        self._emit("error", message)

    def _emit(self, level: str, message: str) -> None:
        for handler in self._handlers:
            handler.emit(level, f"[{self.name}] {message}")

logger = Logger("app", [ConsoleHandler(), FileHandler("app.log")])
logger.info("Server started")
logger.error("Connection failed")
```

### 2단계: 전략 패턴으로 할인 정책 교체

```python
from typing import Protocol
from dataclasses import dataclass

class DiscountStrategy(Protocol):
    def apply(self, amount: int) -> int: ...

class NoDiscount:
    def apply(self, amount: int) -> int:
        return amount

class PercentDiscount:
    def __init__(self, rate: float) -> None:
        if not 0 <= rate <= 1:
            raise ValueError("Rate must be 0.0 to 1.0")
        self.rate = rate

    def apply(self, amount: int) -> int:
        return int(amount * (1 - self.rate))

class FlatDiscount:
    def __init__(self, flat: int) -> None:
        self.flat = flat

    def apply(self, amount: int) -> int:
        return max(0, amount - self.flat)

@dataclass
class Cart:
    items: list[dict]
    discount: DiscountStrategy = NoDiscount()

    def subtotal(self) -> int:
        return sum(item["price"] * item["qty"] for item in self.items)

    def total(self) -> int:
        return self.discount.apply(self.subtotal())

items = [{"name": "Book", "price": 15000, "qty": 2}]

cart_vip = Cart(items, PercentDiscount(0.2))
print(f"VIP total: {cart_vip.total():,}")   # 24,000

cart_coupon = Cart(items, FlatDiscount(5000))
print(f"Coupon total: {cart_coupon.total():,}")  # 25,000
```

### 3단계: 위임 패턴

```python
class EmailService:
    def send(self, to: str, subject: str, body: str) -> None:
        print(f"Email -> {to}: [{subject}] {body[:30]}")

class NotificationService:
    """EmailService에 발송 기능을 위임"""

    def __init__(self, email_service: EmailService) -> None:
        self._email = email_service

    def notify_order_shipped(self, email: str, order_id: str) -> None:
        self._email.send(
            to=email,
            subject="Your order has shipped",
            body=f"Order #{order_id} is on its way!"
        )

    def notify_password_reset(self, email: str, token: str) -> None:
        self._email.send(
            to=email,
            subject="Password reset",
            body=f"Use token: {token}"
        )

svc = NotificationService(EmailService())
svc.notify_order_shipped("alice@example.com", "ORD-1234")
```

### 4단계: Mixin으로 기능 추가

```python
class TimestampMixin:
    """생성/수정 시간을 자동으로 관리"""
    from datetime import datetime

    def __post_init__(self) -> None:
        from datetime import datetime
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def touch(self) -> None:
        from datetime import datetime
        self.updated_at = datetime.now()

class SerializableMixin:
    """딕셔너리 직렬화 기능 추가"""

    def to_dict(self) -> dict:
        return {
            k: v for k, v in self.__dict__.items()
            if not k.startswith("_")
        }

from dataclasses import dataclass

@dataclass
class Product(TimestampMixin, SerializableMixin):
    name: str
    price: int

    def __post_init__(self) -> None:
        super().__post_init__()

p = Product("Keyboard", 50000)
print(p.to_dict())
```

### 5단계: 의존성 주입으로 테스트 용이성 확보

```python
from typing import Protocol

class PaymentGateway(Protocol):
    def charge(self, amount: int, card_token: str) -> str: ...

class StripGateway:
    def charge(self, amount: int, card_token: str) -> str:
        return f"stripe_txn_{card_token}_{amount}"

class MockPaymentGateway:
    """테스트용 게이트웨이 — 실제 결제 없이 동작"""
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def charge(self, amount: int, card_token: str) -> str:
        self.calls.append({"amount": amount, "card_token": card_token})
        return f"mock_txn_{len(self.calls)}"

class OrderService:
    def __init__(self, gateway: PaymentGateway) -> None:
        self._gateway = gateway

    def checkout(self, order_id: str, amount: int, card_token: str) -> str:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        txn_id = self._gateway.charge(amount, card_token)
        return f"Order {order_id} paid: {txn_id}"

# 프로덕션
service = OrderService(StripGateway())

# 테스트
mock = MockPaymentGateway()
test_service = OrderService(mock)
result = test_service.checkout("ORD-1", 50000, "tok_abc")
print(result)              # Order ORD-1 paid: mock_txn_1
print(mock.calls)         # [{'amount': 50000, 'card_token': 'tok_abc'}]
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| "has-a" 관계에 상속 사용 | 결합도가 높아지고 계층이 불필요하게 깊어집니다 | 포함 관계는 합성으로 표현합니다 |
| 합성 객체를 생성자에서 직접 생성 | 의존성이 숨어 테스트하기 어려워집니다 | 외부에서 주입받아 Protocol로 타입을 지정합니다 |
| 전략을 너무 많이 분리 | 클래스 수가 폭발적으로 늘어납니다 | 변경이 자주 일어나는 부분만 전략으로 분리합니다 |
| Mixin에 상태(attribute) 추가 | MRO 충돌과 예상치 못한 부작용이 생깁니다 | Mixin은 메서드만 추가하고 상태는 피합니다 |
| DI 없이 의존성을 하드코딩 | 구현을 교체하려면 코드를 수정해야 합니다 | 생성자로 주입받고 Protocol로 타입을 선언합니다 |

## 실무에서 이렇게 쓰입니다

```python
from typing import Protocol

class StorageBackend(Protocol):
    def read(self, path: str) -> bytes: ...
    def write(self, path: str, data: bytes) -> None: ...

class LocalStorage:
    def read(self, path: str) -> bytes:
        with open(path, "rb") as f:
            return f.read()

    def write(self, path: str, data: bytes) -> None:
        with open(path, "wb") as f:
            f.write(data)

class S3Storage:
    def __init__(self, bucket: str) -> None:
        self.bucket = bucket

    def read(self, path: str) -> bytes:
        print(f"S3 read: s3://{self.bucket}/{path}")
        return b""

    def write(self, path: str, data: bytes) -> None:
        print(f"S3 write: s3://{self.bucket}/{path} ({len(data)} bytes)")

class FileProcessor:
    def __init__(self, storage: StorageBackend) -> None:
        self._storage = storage

    def process(self, input_path: str, output_path: str) -> None:
        data = self._storage.read(input_path)
        processed = data.upper()
        self._storage.write(output_path, processed)

# 스토리지 백엔드를 바꿔도 FileProcessor는 수정 없음
processor = FileProcessor(S3Storage("my-bucket"))
processor.process("input.txt", "output.txt")
```

## 현업 개발자는 이렇게 생각합니다

"상속보다 합성을 선호하라"는 규칙은 상속을 쓰지 말라는 뜻이 아닙니다. 타입 계층이 명확하고 LSP가 성립하는 곳, 즉 자식을 부모 타입으로 무리 없이 교체할 수 있을 때는 상속이 강력합니다.

합성은 행위를 조합하거나 교체해야 할 때 더 유연합니다. 특히 외부 의존성(데이터베이스, 이메일 서버, 결제 API)은 의존성 주입 + 합성으로 구성하면 테스트 더블로 쉽게 교체할 수 있습니다.

## 운영 체크리스트

- [ ] "is-a" vs "has-a" 기준으로 상속/합성을 선택할 수 있다
- [ ] 전략 패턴으로 알고리즘을 런타임에 교체할 수 있다
- [ ] 위임 패턴으로 합성 객체에 메서드를 위임할 수 있다
- [ ] 의존성 주입으로 테스트 가능한 설계를 만들 수 있다
- [ ] Mixin을 올바르게 사용할 수 있다

## 연습 문제

1. `Robot` 클래스를 합성으로 설계하세요. `MovementModule`, `SensorModule`, `ArmModule`을 별도 클래스로 만들고 Robot에 주입합니다. 각 모듈을 교체해도 Robot이 동작해야 합니다.
2. 텍스트 필터 파이프라인을 전략 패턴으로 구현하세요. `UpperCaseFilter`, `StripFilter`, `TruncateFilter`를 만들고 `Pipeline` 클래스에서 조합합니다.
3. `UserRepository`를 의존성 주입으로 설계하세요. `SqlUserRepo`와 `InMemoryUserRepo`를 `UserRepository` Protocol을 만족하도록 구현합니다.

## 정리 및 다음 단계

합성은 행위를 유연하게 조합하고, 상속은 타입 계층을 명확하게 합니다. 의존성 주입으로 합성 관계를 테스트 친화적으로 만들면 변경에 강한 설계를 얻습니다.

다음 글에서는 SOLID 원칙을 다룹니다. SRP, OCP, LSP, ISP, DIP 다섯 원칙을 주문 처리 시스템 예제로 단계별로 적용합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Object-Oriented Programming 101 (1/10): 객체지향이란 무엇인가?](./01-what-is-oop.md)
- [Object-Oriented Programming 101 (2/10): 클래스와 인스턴스](./02-classes-and-instances.md)
- [Object-Oriented Programming 101 (3/10): 캡슐화](./03-encapsulation.md)
- [Object-Oriented Programming 101 (4/10): 상속](./04-inheritance.md)
- [Object-Oriented Programming 101 (5/10): 다형성](./05-polymorphism.md)
- [Object-Oriented Programming 101 (6/10): 추상화](./06-abstraction.md)
- **Object-Oriented Programming 101 (7/10): 합성과 상속 (현재 글)**
- [Object-Oriented Programming 101 (8/10): SOLID 원칙 기초](./08-solid-principles.md)
- [Object-Oriented Programming 101 (9/10): 객체지향 설계 예제](./09-oop-design-example.md)
- [객체지향을 언제 피해야 할까?](./10-when-to-avoid-oop.md)

<!-- toc:end -->

## 참고 자료

- [GoF — Design Patterns: Elements of Reusable Object-Oriented Software](https://www.oreilly.com/library/view/design-patterns-elements/0201633612/)
- [Real Python — Inheritance and Composition](https://realpython.com/inheritance-composition-python/)
- [Effective Python — Item 38: Accept Functions Instead of Classes for Simple Interfaces](https://effectivepython.com/)
- [Clean Architecture — Robert C. Martin](https://www.oreilly.com/library/view/clean-architecture-a/9780134494272/)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/oop-101/ko)
Tags: Python, OOP, 합성, 상속, 설계 패턴
