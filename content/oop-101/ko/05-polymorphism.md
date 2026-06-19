---
title: "Object-Oriented Programming 101 (5/10): 다형성"
series: oop-101
episode: 5
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
  - 다형성
  - 덕 타이핑
  - 프로토콜
last_reviewed: '2026-05-12'
seo_description: 덕 타이핑과 Protocol을 포함해 Python 다형성을 실무 관점에서 설명합니다.
---

# Object-Oriented Programming 101 (5/10): 다형성

다형성을 이해하지 못하면 객체지향 코드는 곧 분기문 모음으로 돌아가기 쉽습니다. 결제 수단이 늘 때마다 `if isinstance(...)`가 늘어나고, 파일 저장 방식이 바뀔 때마다 호출부가 함께 수정됩니다. 겉으로는 객체를 썼는데, 실제로는 타입 분기 중심 코드에 머무는 셈입니다.

Python은 여기서 특히 흥미롭습니다. 상속만으로 다형성을 만드는 언어가 아니라, 덕 타이핑과 `Protocol`까지 활용해 같은 인터페이스를 다양한 방식으로 표현할 수 있기 때문입니다. 중요한 것은 클래스 계층보다 호출부가 무엇을 기대하는지 명확히 하는 일입니다.

이 글은 OOP 101 시리즈의 5번째 글입니다.

![Object-Oriented Programming 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/05/05-01-big-picture.ko.png)
*Object-Oriented Programming 101 5장 흐름 개요*

## 이 글에서 다룰 문제

- 다형성은 왜 타입 분기문을 줄이는 가장 강력한 도구일까요?
- 상속 기반 다형성과 덕 타이핑은 어떤 차이로 쓰일까요?
- `Protocol`은 덕 타이핑을 정적 분석 차원에서 어떻게 보강할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 이 글에서 배울 것

- 다형성이 `isinstance` 분기문을 제거하는 원리를 이해합니다
- 상속 기반 다형성과 덕 타이핑의 차이를 코드로 확인합니다
- `typing.Protocol`로 구조적 서브타이핑을 구현합니다
- 실무에서 다형성을 활용한 전략 패턴을 익힙니다
- 다형성이 필요한 시점과 과도한 추상화를 피하는 기준을 세웁니다

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 다형성(polymorphism) | 같은 인터페이스가 타입에 따라 다르게 동작하는 것입니다 |
| 덕 타이핑(duck typing) | 객체의 타입이 아니라 메서드의 존재 여부로 판단합니다 |
| 프로토콜(Protocol) | 구조적 서브타이핑을 지원하는 typing 모듈의 클래스입니다 |
| 디스패치(dispatch) | 호출 시점에 실제 타입의 메서드를 선택하는 메커니즘입니다 |
| 인터페이스(interface) | 객체가 제공해야 하는 메서드의 집합입니다 |

## 전후 비교

결제 처리 코드를 비교합니다.

```python
# before: 타입 기반 분기 — 결제 수단이 늘 때마다 수정 필요
def process_payment(payment: dict, amount: int) -> str:
    if payment["type"] == "credit_card":
        return f"Credit card payment: {amount}"
    elif payment["type"] == "bank_transfer":
        return f"Bank transfer: {amount}"
    elif payment["type"] == "crypto":
        return f"Crypto payment: {amount}"
    else:
        raise ValueError(f"Unknown payment type: {payment['type']}")
```

```python
# after: 다형성 — 새 결제 수단을 추가해도 process_payment는 수정 불필요
from typing import Protocol

class PaymentMethod(Protocol):
    def pay(self, amount: int) -> str:
        ...

class CreditCard:
    def pay(self, amount: int) -> str:
        return f"Credit card payment: {amount}"

class BankTransfer:
    def pay(self, amount: int) -> str:
        return f"Bank transfer: {amount}"

class Crypto:
    def pay(self, amount: int) -> str:
        return f"Crypto payment: {amount}"

def process_payment(method: PaymentMethod, amount: int) -> str:
    return method.pay(amount)

methods = [CreditCard(), BankTransfer(), Crypto()]
for m in methods:
    print(process_payment(m, 50000))
```

새 결제 수단을 추가할 때 `process_payment`는 건드리지 않아도 됩니다. 확장은 새 클래스 추가로, 기존 코드는 닫힌 상태로 유지됩니다.

## 단계별 실습

### 1단계: 상속 기반 다형성

```python
class Animal:
    def __init__(self, name: str) -> None:
        self.name = name

    def speak(self) -> str:
        raise NotImplementedError("Subclasses must implement speak()")

class Dog(Animal):
    def speak(self) -> str:
        return f"{self.name}: Woof!"

class Cat(Animal):
    def speak(self) -> str:
        return f"{self.name}: Meow!"

class Duck(Animal):
    def speak(self) -> str:
        return f"{self.name}: Quack!"

def make_noise(animals: list[Animal]) -> None:
    for animal in animals:
        print(animal.speak())

make_noise([Dog("Rex"), Cat("Whiskers"), Duck("Donald")])
```

`make_noise`는 `Animal` 타입만 알면 됩니다. 실제로 어떤 동물인지는 `speak()` 호출 시점에 결정됩니다.

### 2단계: 덕 타이핑 — 상속 없이도 다형성

```python
class Dog:
    def speak(self) -> str:
        return "Woof!"

class Robot:
    def speak(self) -> str:
        return "Beep boop!"

class ParrotBot:
    def speak(self) -> str:
        return "Polly wants a cracker!"

# Animal을 상속하지 않아도 speak()가 있으면 동작함
def introduce(speaker: object) -> None:
    if hasattr(speaker, "speak") and callable(speaker.speak):
        print(speaker.speak())

for s in [Dog(), Robot(), ParrotBot()]:
    introduce(s)
```

Python은 타입 계층이 아니라 실제 메서드 존재 여부로 인터페이스를 만족시킵니다. 이것이 덕 타이핑입니다.

### 3단계: Protocol로 구조적 서브타이핑

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Drawable(Protocol):
    def draw(self) -> str:
        ...

    def bounding_box(self) -> tuple[float, float, float, float]:
        ...

class Circle:
    def __init__(self, cx: float, cy: float, r: float) -> None:
        self.cx, self.cy, self.r = cx, cy, r

    def draw(self) -> str:
        return f"Circle at ({self.cx}, {self.cy}) r={self.r}"

    def bounding_box(self) -> tuple[float, float, float, float]:
        return (self.cx - self.r, self.cy - self.r,
                self.cx + self.r, self.cy + self.r)

class Rectangle:
    def __init__(self, x: float, y: float, w: float, h: float) -> None:
        self.x, self.y, self.w, self.h = x, y, w, h

    def draw(self) -> str:
        return f"Rect at ({self.x}, {self.y}) {self.w}x{self.h}"

    def bounding_box(self) -> tuple[float, float, float, float]:
        return (self.x, self.y, self.x + self.w, self.y + self.h)

def render(shapes: list[Drawable]) -> None:
    for shape in shapes:
        print(shape.draw())
        print(f"  bbox: {shape.bounding_box()}")

shapes: list[Drawable] = [Circle(0, 0, 5), Rectangle(1, 1, 10, 8)]
render(shapes)

# @runtime_checkable이 있으면 isinstance 검사 가능
print(isinstance(Circle(0, 0, 1), Drawable))  # True
```

`Circle`과 `Rectangle`은 `Drawable`을 명시적으로 상속하지 않습니다. 메서드 구조만 일치하면 Protocol을 만족합니다.

### 4단계: 전략 패턴으로 알고리즘 교체

```python
from typing import Protocol

class SortStrategy(Protocol):
    def sort(self, data: list[int]) -> list[int]:
        ...

class BubbleSort:
    def sort(self, data: list[int]) -> list[int]:
        arr = data.copy()
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr

class QuickSort:
    def sort(self, data: list[int]) -> list[int]:
        if len(data) <= 1:
            return data
        pivot = data[len(data) // 2]
        left = [x for x in data if x < pivot]
        middle = [x for x in data if x == pivot]
        right = [x for x in data if x > pivot]
        return self.sort(left) + middle + self.sort(right)

class Sorter:
    def __init__(self, strategy: SortStrategy) -> None:
        self.strategy = strategy

    def sort(self, data: list[int]) -> list[int]:
        return self.strategy.sort(data)

data = [3, 1, 4, 1, 5, 9, 2, 6]
for strategy in [BubbleSort(), QuickSort()]:
    sorter = Sorter(strategy)
    print(f"{strategy.__class__.__name__}: {sorter.sort(data)}")
```

### 5단계: 파일 저장 전략

```python
import json
from typing import Protocol

class StorageBackend(Protocol):
    def write(self, key: str, data: dict) -> None:
        ...

    def read(self, key: str) -> dict | None:
        ...

class InMemoryStorage:
    def __init__(self) -> None:
        self._store: dict[str, dict] = {}

    def write(self, key: str, data: dict) -> None:
        self._store[key] = data.copy()

    def read(self, key: str) -> dict | None:
        return self._store.get(key)

class JsonFileStorage:
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self._data: dict = {}

    def write(self, key: str, data: dict) -> None:
        self._data[key] = data

    def read(self, key: str) -> dict | None:
        return self._data.get(key)

class DataService:
    def __init__(self, storage: StorageBackend) -> None:
        self.storage = storage

    def save_user(self, user_id: str, user_data: dict) -> None:
        self.storage.write(f"user:{user_id}", user_data)

    def get_user(self, user_id: str) -> dict | None:
        return self.storage.read(f"user:{user_id}")

# 테스트에서는 InMemoryStorage, 프로덕션에서는 JsonFileStorage
service = DataService(InMemoryStorage())
service.save_user("u1", {"name": "Alice", "email": "alice@example.com"})
print(service.get_user("u1"))  # {'name': 'Alice', 'email': 'alice@example.com'}
```

`DataService`는 `StorageBackend` Protocol만 알면 됩니다. 스토리지 구현을 바꿔도 서비스 코드는 그대로입니다.

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 다형성을 위해 불필요한 상속 도입 | 상속 계층이 복잡해집니다 | 덕 타이핑이나 Protocol로 대체합니다 |
| `isinstance` 분기를 다형성 도입 후에도 유지 | 다형성의 목적이 사라집니다 | 분기를 객체 메서드로 이전합니다 |
| Protocol 없이 덕 타이핑만 사용 | 타입 검사기가 오류를 잡지 못합니다 | `typing.Protocol`로 계약을 명시합니다 |
| 모든 클래스에 공통 기반 클래스 강제 | 불필요한 결합이 생깁니다 | 호출부가 필요한 메서드만 Protocol에 정의합니다 |
| 추상 메서드를 너무 많이 정의 | 구현체가 불필요한 메서드를 억지로 채워야 합니다 | ISP 원칙에 따라 작은 인터페이스로 분리합니다 |

## 실무에서 이렇게 쓰입니다

알림 발송 시스템에서 다형성이 어떻게 동작하는지 확인합니다.

```python
from typing import Protocol
from dataclasses import dataclass

@dataclass
class Notification:
    title: str
    body: str
    recipient: str

class NotificationChannel(Protocol):
    def send(self, notification: Notification) -> bool:
        ...

class EmailChannel:
    def send(self, notification: Notification) -> bool:
        print(f"[EMAIL] To: {notification.recipient} | {notification.title}")
        return True

class SMSChannel:
    def send(self, notification: Notification) -> bool:
        print(f"[SMS] {notification.recipient}: {notification.body[:60]}")
        return True

class PushChannel:
    def send(self, notification: Notification) -> bool:
        print(f"[PUSH] {notification.title} -> {notification.recipient}")
        return True

class NotificationService:
    def __init__(self, channels: list[NotificationChannel]) -> None:
        self.channels = channels

    def notify(self, notification: Notification) -> dict[str, bool]:
        results = {}
        for channel in self.channels:
            channel_name = channel.__class__.__name__
            results[channel_name] = channel.send(notification)
        return results

service = NotificationService([EmailChannel(), SMSChannel(), PushChannel()])
n = Notification("Order Confirmed", "Your order #1234 has been confirmed.", "alice@example.com")
print(service.notify(n))
```

새 채널(예: KakaoChannel)을 추가할 때 `NotificationService`는 수정하지 않습니다.

## 현업 개발자는 이렇게 생각합니다

다형성의 실무 가치는 "기존 코드를 수정하지 않고 새 동작을 추가하는 능력"입니다. 결제 수단이 늘어도, 알림 채널이 추가되어도, 저장 방식이 바뀌어도 핵심 흐름 코드는 그대로여야 합니다.

Python에서 다형성은 상속보다 Protocol이 더 유연합니다. 외부 라이브러리의 클래스도 Protocol을 만족하면 그대로 사용할 수 있고, 상속 계층 없이도 타입 안전성을 확보할 수 있습니다.

## 운영 체크리스트

- [ ] 타입 분기(`isinstance`)를 다형성으로 대체할 수 있다
- [ ] 덕 타이핑과 상속 기반 다형성의 차이를 설명할 수 있다
- [ ] `typing.Protocol`로 인터페이스를 정의할 수 있다
- [ ] 전략 패턴을 Protocol + 합성으로 구현할 수 있다
- [ ] 다형성을 도입할 타이밍과 피해야 할 타이밍을 구분할 수 있다

## 연습 문제

1. 세금 계산 시스템을 만드세요. `TaxCalculator` Protocol을 정의하고, `KoreaVAT`, `USStateTax`, `NoTax` 세 가지 구현체를 작성합니다.
2. 파일 파서 시스템을 구현하세요. `FileParser` Protocol에 `parse(content: str) -> dict` 메서드를 정의하고, `JsonParser`와 `CsvParser`를 구현합니다.
3. 게임 캐릭터 능력치 시스템에서 다형성을 활용하세요. `AttackStrategy` Protocol로 `MeleeAttack`, `RangedAttack`, `MagicAttack`을 구현하고 런타임에 교체합니다.

## 정리 및 다음 단계

다형성은 타입 분기 없이 다양한 동작을 처리하는 핵심 OOP 원칙입니다. Python에서는 상속, 덕 타이핑, Protocol 세 가지 방식이 있으며, 실무에서는 Protocol + 합성이 가장 유연합니다.

다음 글에서는 추상화를 다룹니다. `abc.ABC`, `@abstractmethod`, 그리고 Protocol의 차이를 명확하게 정리합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Object-Oriented Programming 101 (1/10): 객체지향이란 무엇인가?](./01-what-is-oop.md)
- [Object-Oriented Programming 101 (2/10): 클래스와 인스턴스](./02-classes-and-instances.md)
- [Object-Oriented Programming 101 (3/10): 캡슐화](./03-encapsulation.md)
- [Object-Oriented Programming 101 (4/10): 상속](./04-inheritance.md)
- **Object-Oriented Programming 101 (5/10): 다형성 (현재 글)**
- [Object-Oriented Programming 101 (6/10): 추상화](./06-abstraction.md)
- [Object-Oriented Programming 101 (7/10): 합성과 상속](./07-composition-vs-inheritance.md)
- [Object-Oriented Programming 101 (8/10): SOLID 원칙 기초](./08-solid-principles.md)
- [Object-Oriented Programming 101 (9/10): 객체지향 설계 예제](./09-oop-design-example.md)
- [객체지향을 언제 피해야 할까?](./10-when-to-avoid-oop.md)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — typing.Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol)
- [PEP 544 — Protocols: Structural subtyping](https://peps.python.org/pep-0544/)
- [Real Python — Python Protocol](https://realpython.com/python-protocol/)
- [Fluent Python — Duck Typing and Protocols](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/oop-101/ko)
Tags: Python, OOP, 다형성, 덕 타이핑, 프로토콜
