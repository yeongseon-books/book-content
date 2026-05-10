---
series: oop-101
episode: 8
title: SOLID 원칙 기초
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - OOP
  - SOLID
  - 설계 원칙
  - 클린 코드
seo_description: SOLID 5가지 원칙을 Python 예제로 설명하고 실무 적용법을 다룹니다.
last_reviewed: '2026-05-04'
---

# SOLID 원칙 기초

> Object-Oriented Programming 101 시리즈 (8/10)


## 이 글에서 다룰 문제

코드를 작성하는 것보다 유지보수하는 시간이 훨씬 깁니다. SOLID 원칙은 "변경이 쉬운 코드"를 만드는 가이드라인입니다. 한 곳을 수정했을 때 다른 곳이 깨지지 않고, 새 기능을 추가할 때 기존 코드를 최소한으로 변경하는 것이 목표입니다.

> SOLID = 변경에 강하고 확장에 유연한 설계를 위한 5가지 원칙

모든 원칙을 처음부터 완벽히 적용할 필요는 없습니다. 코드가 성장하면서 문제가 보일 때 해당 원칙을 적용하면 됩니다.

## 핵심 개념 잡기

> SOLID 5원칙 요약

```
S — Single Responsibility    한 클래스는 한 가지 이유로만 변경
O — Open/Closed             확장에 열려있고 수정에 닫혀있음
L — Liskov Substitution     자식은 부모를 대체할 수 있어야 함
I — Interface Segregation   큰 인터페이스보다 작은 인터페이스 여러 개
D — Dependency Inversion    구체가 아닌 추상에 의존
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 단일 책임 원칙(SRP) | 클래스는 하나의 책임만 가져야 합니다 |
| 개방-폐쇄 원칙(OCP) | 기존 코드 수정 없이 기능을 확장할 수 있어야 합니다 |
| 리스코프 치환 원칙(LSP) | 자식 클래스는 부모 클래스를 대체할 수 있어야 합니다 |
| 인터페이스 분리 원칙(ISP) | 사용하지 않는 메서드에 의존하면 안 됩니다 |
| 의존성 역전 원칙(DIP) | 상위 모듈은 하위 모듈이 아닌 추상에 의존해야 합니다 |

## Before / After

단일 책임 원칙 위반과 개선을 비교합니다.

```python
# before: SRP 위반 — 하나의 클래스가 여러 책임
class UserManager:
    def create_user(self, name: str) -> dict:
        user = {"name": name}
        # DB 저장 로직
        # 이메일 발송 로직
        # 로그 기록 로직
        return user
```

```python
# after: SRP 적용 — 각 클래스가 하나의 책임
class UserRepository:
    def save(self, user: dict) -> None:
        print(f"DB 저장: {user}")

class EmailService:
    def send_welcome(self, name: str) -> None:
        print(f"환영 이메일 발송: {name}")

class UserService:
    def __init__(self, repo: UserRepository, email: EmailService) -> None:
        self._repo = repo
        self._email = email

    def create_user(self, name: str) -> dict:
        user = {"name": name}
        self._repo.save(user)
        self._email.send_welcome(name)
        return user
```

## 단계별 실습

### Step 1: S — 단일 책임 원칙 (SRP)

```python
# 위반: Report 클래스가 데이터 처리와 출력을 모두 담당
class Report:
    def __init__(self, data: list[dict]) -> None:
        self.data = data

    def calculate_total(self) -> int:
        return sum(item["amount"] for item in self.data)

    def to_html(self) -> str:  # 출력 형식 변경 → Report 수정 필요
        total = self.calculate_total()
        return f"<h1>총합: {total}</h1>"


# 개선: 데이터 처리와 출력 분리
class SalesReport:
    def __init__(self, data: list[dict]) -> None:
        self.data = data

    def calculate_total(self) -> int:
        return sum(item["amount"] for item in self.data)


class ReportFormatter:
    def to_html(self, report: SalesReport) -> str:
        return f"<h1>총합: {report.calculate_total()}</h1>"

    def to_text(self, report: SalesReport) -> str:
        return f"총합: {report.calculate_total()}"


data = [{"amount": 100}, {"amount": 200}]
report = SalesReport(data)
formatter = ReportFormatter()
print(formatter.to_html(report))  # <h1>총합: 300</h1>
print(formatter.to_text(report))  # 총합: 300
```

### Step 2: O — 개방-폐쇄 원칙 (OCP)

```python
from typing import Protocol


class Discount(Protocol):
    def apply(self, price: int) -> int: ...


class NoDiscount:
    def apply(self, price: int) -> int:
        return price

class PercentDiscount:
    def __init__(self, percent: int) -> None:
        self.percent = percent

    def apply(self, price: int) -> int:
        return price - (price * self.percent // 100)

class FixedDiscount:
    def __init__(self, amount: int) -> None:
        self.amount = amount

    def apply(self, price: int) -> int:
        return max(0, price - self.amount)


def calculate_price(price: int, discount: Discount) -> int:
    """새 할인 유형 추가 시 이 함수 수정 불필요"""
    return discount.apply(price)


print(calculate_price(10000, NoDiscount()))           # 10000
print(calculate_price(10000, PercentDiscount(20)))     # 8000
print(calculate_price(10000, FixedDiscount(3000)))     # 7000
```

### Step 3: L — 리스코프 치환 원칙 (LSP)

```python
class Bird:
    def move(self) -> str:
        return "이동합니다"

class FlyingBird(Bird):
    def move(self) -> str:
        return "날아서 이동합니다"

class Penguin(Bird):
    def move(self) -> str:
        return "걸어서 이동합니다"


def make_bird_move(bird: Bird) -> None:
    print(bird.move())

# 모든 하위 클래스가 부모를 대체할 수 있음
make_bird_move(FlyingBird())  # 날아서 이동합니다
make_bird_move(Penguin())     # 걸어서 이동합니다
```

### Step 4: I — 인터페이스 분리 원칙 (ISP)

```python
from typing import Protocol


# 위반: 모든 기능을 하나의 인터페이스에
# class Worker(Protocol):
#     def code(self) -> str: ...
#     def test(self) -> str: ...
#     def design(self) -> str: ...  # 개발자에게 불필요


# 개선: 역할별로 분리
class Coder(Protocol):
    def code(self) -> str: ...

class Tester(Protocol):
    def test(self) -> str: ...

class Designer(Protocol):
    def design(self) -> str: ...


class Developer:
    def code(self) -> str:
        return "코드 작성 중"

    def test(self) -> str:
        return "테스트 작성 중"


class UxDesigner:
    def design(self) -> str:
        return "UI 디자인 중"


def assign_coding(worker: Coder) -> None:
    print(worker.code())

def assign_design(worker: Designer) -> None:
    print(worker.design())

assign_coding(Developer())    # 코드 작성 중
assign_design(UxDesigner())   # UI 디자인 중
```

### Step 5: D — 의존성 역전 원칙 (DIP)

```python
from typing import Protocol


class MessageSender(Protocol):
    def send(self, to: str, body: str) -> None: ...


class EmailSender:
    def send(self, to: str, body: str) -> None:
        print(f"이메일 발송 → {to}: {body}")

class SlackSender:
    def send(self, to: str, body: str) -> None:
        print(f"Slack 메시지 → {to}: {body}")


class NotificationService:
    """상위 모듈: 구체 클래스가 아닌 추상(Protocol)에 의존"""

    def __init__(self, sender: MessageSender) -> None:
        self._sender = sender

    def notify(self, user: str, message: str) -> None:
        self._sender.send(user, message)


# 이메일로 알림
service = NotificationService(EmailSender())
service.notify("kim@example.com", "배포 완료")

# Slack으로 교체 — NotificationService 수정 불필요
service = NotificationService(SlackSender())
service.notify("#deploy", "배포 완료")
```

## 이 코드에서 주목할 점

- SRP는 클래스를 작게 유지하여 변경 이유를 하나로 제한합니다
- OCP는 새 기능 추가 시 기존 코드를 수정하지 않게 합니다
- LSP는 상속 관계에서 자식이 부모를 안전하게 대체할 수 있게 합니다
- DIP는 Protocol과 의존성 주입으로 자연스럽게 구현됩니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 처음부터 모든 원칙 적용 | 과도한 추상화로 복잡해집니다 | 필요할 때 점진적으로 적용합니다 |
| SRP를 극단적으로 적용 | 클래스가 너무 잘게 쪼개집니다 | "변경의 이유"를 기준으로 판단합니다 |
| LSP 위반 — 자식이 예외 발생 | 부모 타입으로 사용할 수 없습니다 | 상속 대신 합성을 고려합니다 |
| ISP 무시 — 거대 인터페이스 | 불필요한 메서드 구현을 강제합니다 | 역할별로 Protocol을 분리합니다 |
| DIP 무시 — 구체 클래스 직접 의존 | 교체와 테스트가 어렵습니다 | 추상에 의존하고 주입합니다 |

## 실무에서 이렇게 쓰입니다

- FastAPI의 Depends()는 DIP를 프레임워크 수준에서 지원합니다
- Django의 settings 모듈은 SRP로 설정을 분리합니다
- 플러그인 시스템은 OCP를 기반으로 확장합니다
- REST API의 직렬화/역직렬화는 ISP로 인터페이스를 분리합니다
- 테스트 mock은 DIP 덕분에 구체 의존성을 교체합니다

## 현업 개발자는 이렇게 생각합니다

SOLID는 "규칙"이 아니라 "가이드라인"입니다. 모든 코드에 적용할 필요는 없고, 코드가 성장하면서 변경이 어려워지는 지점에서 적용하면 됩니다. 가장 실용적인 원칙은 SRP와 DIP입니다.

작은 프로젝트에서는 SOLID를 의식하지 않아도 됩니다. 하지만 팀 프로젝트에서 코드가 수만 줄을 넘어갈 때, SOLID를 이해하는 개발자와 그렇지 않은 개발자의 코드 품질 차이가 확연히 드러납니다.

## 체크리스트

- [ ] SOLID 5가지 원칙을 각각 설명할 수 있다
- [ ] SRP 위반을 식별하고 개선할 수 있다
- [ ] OCP를 Protocol/ABC로 구현할 수 있다
- [ ] LSP 위반 사례를 판별할 수 있다
- [ ] DIP를 의존성 주입으로 적용할 수 있다

## 정리 및 다음 글 안내

SOLID 원칙은 변경에 강하고 확장에 유연한 설계를 위한 가이드라인입니다. 처음부터 완벽히 적용하기보다, 코드가 성장하면서 필요한 시점에 적용하는 것이 현실적입니다. 다음 글에서는 SOLID를 포함한 OOP 원칙을 실제 프로젝트에 적용하는 설계 예제를 살펴봅니다.

<!-- toc:begin -->
- [객체지향이란 무엇인가?](./01-what-is-oop.md)
- [클래스와 인스턴스](./02-classes-and-instances.md)
- [캡슐화](./03-encapsulation.md)
- [상속](./04-inheritance.md)
- [다형성](./05-polymorphism.md)
- [추상화](./06-abstraction.md)
- [합성과 상속](./07-composition-vs-inheritance.md)
- **SOLID 원칙 기초 (현재 글)**
- [객체지향 설계 예제](./09-oop-design-example.md)
- [객체지향을 언제 피해야 할까?](./10-when-to-avoid-oop.md)
<!-- toc:end -->

## 참고 자료

- [Clean Architecture — Robert C. Martin](https://www.oreilly.com/library/view/clean-architecture/9780134494272/)
- [Real Python — SOLID Principles in Python](https://realpython.com/solid-principles-python/)
- [Agile Software Development — Robert C. Martin](https://www.oreilly.com/library/view/agile-software-development/0135974445/)
- [PEP 544 — Protocols: Structural subtyping](https://peps.python.org/pep-0544/)

Tags: Python, OOP, SOLID, 설계 원칙, 클린 코드
