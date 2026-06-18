---
title: "바이브코딩을 위한 객체지향 기초 (5/10): 다형성"
series: oop-101
episode: 5
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - Python
  - OOP
  - 다형성
  - 바이브코딩
  - 덕 타이핑
  - 프로토콜
last_reviewed: '2026-06-18'
seo_description: AI가 isinstance() 분기 대신 다형성을 사용하는 이유를 설명합니다. 덕 타이핑과 Protocol을 바이브코딩 관점에서 이해합니다.
---

# 바이브코딩을 위한 객체지향 기초 (5/10): 다형성

이 글은 **바이브코딩을 위한 객체지향 기초** 시리즈의 다섯 번째 글입니다.

---

AI에게 결제 시스템을 만들어 달라고 하면 카드 결제, 계좌이체, 포인트 결제를 각각 다른 클래스로 만들고 모두 `pay()` 메서드를 가지게 합니다. 처음엔 왜 굳이 이렇게 나누는지 이해가 안 갈 수 있습니다. 그냥 `if payment_type == "card"` 분기로 하면 안 되나요?

AI가 이렇게 설계하는 이유가 있습니다. 새 결제 수단이 추가될 때마다 기존 코드를 고칠 필요 없이 새 클래스만 추가하면 됩니다. 이것이 다형성의 힘입니다. 다형성을 이해하지 못하면 AI 코드가 왜 이런 구조인지 파악하기 어렵고, 수정할 때 실수가 생깁니다.

AI가 클래스 계층을 만들어줬는데 왜 이렇게 짰는지 이해하려면 OOP를 알아야 합니다.

> "AI가 만든 코드에서 `if isinstance(x, TypeA)`가 많이 보인다면, 다형성으로 리팩터링할 기회입니다."

## 이 글에서 다룰 문제

- 다형성은 왜 타입 분기문을 줄이는 가장 강력한 도구일까요?
- 상속 기반 다형성과 덕 타이핑은 어떤 차이로 쓰일까요?
- `Protocol`은 덕 타이핑을 정적 분석 차원에서 어떻게 보강할까요?
- AI가 `Protocol`을 사용하는 이유는 무엇인가요?
- `isinstance()` 분기를 다형성으로 바꾸는 방법은 무엇인가요?

## 핵심 개념 잡기

Python에서 다형성은 세 가지 방식으로 구현됩니다.

```text
1. 상속 기반 다형성
   Animal -> Dog.speak(), Cat.speak()

2. 덕 타이핑 (Duck Typing)
   "quack() 메서드가 있으면 오리다"
   상속 없이도 같은 메서드가 있으면 같은 방식으로 사용 가능

3. Protocol (Python 3.8+)
   구조적 서브타이핑: 타입 힌트로 덕 타이핑 검증
```

| 용어 | 설명 |
|------|------|
| 다형성(polymorphism) | 같은 인터페이스가 타입에 따라 다르게 동작하는 것입니다 |
| 덕 타이핑(duck typing) | 객체의 타입이 아니라 메서드의 존재 여부로 판단합니다 |
| 프로토콜(Protocol) | 구조적 서브타이핑을 지원하는 typing 모듈의 클래스입니다 |

## Before / After: AI가 타입 분기를 다형성으로 바꾸는 이유

```python
# Before: 타입 기반 분기 — 결제 수단이 늘 때마다 수정 필요
def process_payment(payment, amount):
    if payment["type"] == "credit_card":
        print(f"신용카드 결제: {amount}원")
    elif payment["type"] == "bank_transfer":
        print(f"계좌이체: {amount}원")
    # 새 결제 수단 추가 -> elif 추가 필요 -> 기존 코드 수정
```

```python
# After: 다형성 — 새 결제 수단에도 기존 코드 수정 불필요
class CreditCard:
    def pay(self, amount: int) -> str:
        return f"신용카드 결제: {amount}원"

class BankTransfer:
    def pay(self, amount: int) -> str:
        return f"계좌이체: {amount}원"

class PointPay:
    def pay(self, amount: int) -> str:
        return f"포인트 결제: {amount}원"

def process_payment(payment, amount: int) -> None:
    print(payment.pay(amount))  # pay() 메서드만 있으면 어떤 타입이든 동작

# 새 결제 수단 추가: 기존 코드 수정 없이 새 클래스만 추가
process_payment(CreditCard(), 50000)  # 신용카드 결제: 50000원
process_payment(BankTransfer(), 30000)  # 계좌이체: 30000원
process_payment(PointPay(), 10000)  # 포인트 결제: 10000원
```

## 바이브코딩 관점: AI가 Protocol을 쓰는 이유

AI가 만든 코드에서 `from typing import Protocol`이 보이면, 덕 타이핑에 타입 안전성을 더한 패턴입니다.

```python
from typing import Protocol

class Writable(Protocol):
    def write(self, data: str) -> None: ...  # 이 메서드만 있으면 충분

class FileWriter:
    def write(self, data: str) -> None:
        print(f"파일에 저장: {data}")

class DatabaseWriter:
    def write(self, data: str) -> None:
        print(f"DB에 저장: {data}")

class ApiWriter:
    def write(self, data: str) -> None:
        print(f"API로 전송: {data}")

def save_data(writer: Writable, data: str) -> None:
    writer.write(data)  # writer의 타입이 뭔지 몰라도 동작

# 상속 관계 없이도 Protocol을 만족하면 사용 가능
save_data(FileWriter(), "안녕하세요")    # 파일에 저장: 안녕하세요
save_data(DatabaseWriter(), "안녕하세요")  # DB에 저장: 안녕하세요
save_data(ApiWriter(), "안녕하세요")     # API로 전송: 안녕하세요
```

`Protocol`은 상속 없이도 같은 인터페이스를 정의합니다. `Writable`을 상속하지 않아도 `write()` 메서드만 있으면 `Writable`로 취급합니다. AI가 이 패턴을 쓰면 타입 검사기(mypy, pyright)가 인터페이스 위반을 미리 잡아줍니다.

## 상속 기반 다형성 예시

```python
class Shape:
    def area(self) -> float:
        raise NotImplementedError

    def describe(self) -> str:
        return f"{type(self).__name__}: 넓이 = {self.area():.2f}"

class Circle(Shape):
    def __init__(self, radius: float) -> None:
        self.radius = radius

    def area(self) -> float:
        import math
        return math.pi * self.radius ** 2

class Rectangle(Shape):
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

# 다형성: 같은 describe() 호출, 다른 area() 결과
shapes: list[Shape] = [Circle(5), Rectangle(4, 6)]
for shape in shapes:
    print(shape.describe())
# Circle: 넓이 = 78.54
# Rectangle: 넓이 = 24.00
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| `isinstance()` 분기 남발 | 다형성의 이점이 사라집니다 | 공통 인터페이스로 통일합니다 |
| 덕 타이핑에서 메서드 이름 불일치 | `AttributeError`가 런타임에 발생합니다 | `Protocol`로 타입 힌트를 추가합니다 |
| 모든 것을 상속으로 해결 | 불필요한 계층이 생깁니다 | 덕 타이핑이나 Protocol을 먼저 고려합니다 |
| `NotImplementedError` 미발생 | 부모의 기본 구현이 의도치 않게 사용됩니다 | 추상 메서드가 필요하면 ABC를 사용합니다 |
| Protocol에 구현 코드 작성 | Protocol은 인터페이스 정의용입니다 | 메서드 본문은 `...`만 작성합니다 |

## AI 팁: 다형성 패턴 활용하기

AI와 함께 코딩할 때 다형성을 활용하는 방법입니다.

```python
# AI에게 이렇게 요청하세요:
# "이 if/elif 분기를 다형성 패턴으로 리팩터링해 줘"

# Before: AI가 리팩터링하기 전
def notify(channel: str, message: str) -> None:
    if channel == "email":
        print(f"이메일 발송: {message}")
    elif channel == "slack":
        print(f"Slack 전송: {message}")
    elif channel == "sms":
        print(f"SMS 발송: {message}")

# After: AI가 Protocol 패턴으로 변환
from typing import Protocol

class NotificationChannel(Protocol):
    def send(self, message: str) -> None: ...

class EmailChannel:
    def send(self, message: str) -> None:
        print(f"이메일 발송: {message}")

class SlackChannel:
    def send(self, message: str) -> None:
        print(f"Slack 전송: {message}")

def notify(channel: NotificationChannel, message: str) -> None:
    channel.send(message)  # 새 채널 추가해도 이 함수는 수정 불필요
```

## 체크리스트

- [ ] 상속 기반 다형성을 구현할 수 있다
- [ ] 덕 타이핑의 원리를 이해하고 활용할 수 있다
- [ ] `Protocol`을 사용하여 구조적 서브타이핑을 정의할 수 있다
- [ ] `isinstance()` 분기 대신 다형성을 적용할 수 있다
- [ ] AI 코드에서 다형성 패턴을 식별하고 확장할 수 있다

## 처음 질문으로 돌아가기

- **다형성은 왜 타입 분기문을 줄이는 도구일까요?**
  타입 분기(`if isinstance(...)`)는 새 타입이 추가될 때마다 기존 코드를 수정해야 합니다. 다형성은 새 클래스를 추가하기만 하면 됩니다. AI가 이 패턴을 쓰면 나중에 기능 추가가 쉬워집니다.

- **덕 타이핑과 Protocol의 차이는 무엇인가요?**
  덕 타이핑은 런타임에 메서드 존재를 확인합니다. Protocol은 타입 검사기가 정적 분석 단계에서 인터페이스 만족 여부를 확인하게 해줍니다. AI가 Protocol을 쓰면 코드 완성과 오류 검출이 더 잘 됩니다.

- **AI 코드에서 다형성을 어떻게 확장할까요?**
  새 기능을 추가할 때 기존 클래스를 수정하지 말고, 같은 인터페이스를 구현하는 새 클래스를 만들어 보세요. AI에게 "이 Protocol을 구현하는 새 클래스를 만들어 줘"라고 하면 일관된 패턴으로 확장해 줍니다.

## 정리

다형성은 같은 인터페이스로 다른 구현을 호출하여 코드의 유연성을 높입니다. Python은 덕 타이핑, 상속, Protocol 세 가지 방식으로 다형성을 지원합니다. AI가 이 패턴을 사용하는 이유는 새 기능 추가 시 기존 코드를 최소한으로 수정하기 위해서입니다. 다음 글에서는 추상화를 통해 공통 인터페이스를 강제하는 방법과 AI가 ABC를 쓰는 이유를 알아봅니다.

## 참고 자료

- [Python 공식 문서 — typing.Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol)
- [Real Python — Duck Typing in Python](https://realpython.com/duck-typing-python/)
- [PEP 544 — Protocols: Structural subtyping](https://peps.python.org/pep-0544/)
- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/oop-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 객체지향 기초 (1/10): 객체지향이란 무엇인가?
- 바이브코딩을 위한 객체지향 기초 (2/10): 클래스와 인스턴스
- 바이브코딩을 위한 객체지향 기초 (3/10): 캡슐화
- 바이브코딩을 위한 객체지향 기초 (4/10): 상속
- **바이브코딩을 위한 객체지향 기초 (5/10): 다형성 (현재 글)**
- 바이브코딩을 위한 객체지향 기초 (6/10): 추상화
- 바이브코딩을 위한 객체지향 기초 (7/10): 합성과 상속
- 바이브코딩을 위한 객체지향 기초 (8/10): SOLID 원칙 기초
- 바이브코딩을 위한 객체지향 기초 (9/10): 객체지향 설계 예제
- 바이브코딩을 위한 객체지향 기초 (10/10): 객체지향을 언제 피해야 할까?

<!-- toc:end -->

Tags: Python, OOP, 다형성, 바이브코딩, 덕 타이핑, 프로토콜
