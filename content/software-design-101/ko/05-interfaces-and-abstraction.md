---
series: software-design-101
episode: 5
title: "Software Design 101 (5/10): 인터페이스와 추상화"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - SoftwareDesign
  - Interfaces
  - Abstraction
  - LSP
  - Polymorphism
seo_description: 인터페이스의 조건과 추상화 설계법을 학습하고 다형성으로 분기를 줄입니다. LSP, ISP 원칙으로 유연한 구조를 만드는 실무 방법을 정리합니다.
last_reviewed: '2026-05-15'
---

# Software Design 101 (5/10): 인터페이스와 추상화

알림 기능 하나를 만들 때 `notify("email", ...)`, `notify("sms", ...)`, `notify("push", ...)` 같은 분기가 계속 늘어나기 시작하면 인터페이스가 구현 세부를 바깥으로 흘리고 있다는 신호일 수 있습니다. 호출자가 원하는 일보다 구현 방식이 더 많이 드러날수록 구조는 빨리 뻣뻣해집니다.

이 글은 Software Design 101 시리즈의 5번째 글입니다.

여기서는 좋은 인터페이스가 무엇인지, 추상화 수준을 어떻게 맞춰야 하는지, 다형성이 분기를 어떻게 줄이는지, LSP와 ISP가 왜 인터페이스 품질을 판단하는 기준이 되는지 설명합니다. 구현 교체가 쉬운 구조가 어떻게 만들어지는지도 함께 보겠습니다.

## 먼저 던지는 질문

- 더 나은 인터페이스는 무엇으로 판단할 수 있을까요?
- 추상화 수준이 너무 낮거나 높으면 어떤 문제가 생길까요?
- 다형성은 분기문을 어떻게 줄여 줄까요?

## 큰 그림

![Software Design 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/software-design-101/05/05-01-concept-at-a-glance.ko.png)

*Software Design 101 5장 흐름 개요*

## 왜 중요한가

인터페이스는 약속입니다. 약속이 작고 분명하면 구현과 호출자 양쪽 모두 움직일 여지가 생깁니다. 반대로 인터페이스에 구현 세부가 너무 많이 드러나면 호출자는 내부 사정을 함께 떠안게 됩니다.

실무에서 인터페이스 품질은 교체 비용으로 드러납니다. 같은 결제 게이트웨이인데 벤더만 바꾸려 했을 뿐인데 호출자 전부를 손봐야 한다면, 문제는 구현체보다 인터페이스 설계에 있을 가능성이 큽니다.

## 전체 그림

호출자는 하나의 모양만 알고, 여러 구현은 그 뒤에 놓입니다. 이 구조가 잘 작동하려면 인터페이스가 호출자의 관심사와 같은 높이에서 설계되어야 합니다.

## 기본 용어

- <strong>인터페이스</strong>: 호출 가능한 약속의 모양입니다.
- <strong>추상화 수준</strong>: 인터페이스가 호출자의 어휘와 얼마나 잘 맞는지를 뜻합니다.
- <strong>다형성</strong>: 같은 호출이 여러 구현으로 분기될 수 있는 성질입니다.
- <strong>LSP</strong>: 하위 타입은 상위 타입이 쓰이는 자리에 문제없이 들어갈 수 있어야 한다는 원칙입니다.
- <strong>누수된 추상화</strong>: 내부 구현 세부가 인터페이스 밖으로 새는 상태입니다.

## 변경 전과 변경 후

**변경 전**

```python
def notify(kind, user, msg):
    if kind == "email": send_email(user, msg)
    elif kind == "sms": send_sms(user, msg)
    elif kind == "push": send_push(user, msg)
```

**변경 후**

```python
class Notifier:
    def send(self, user, msg): ...

def notify(notifier: Notifier, user, msg):
    notifier.send(user, msg)
```

두 번째 구조에서는 새 채널을 추가할 때 기존 함수 내부 분기를 늘릴 필요가 없습니다. 호출자는 “보낸다”는 의도만 알고 있으면 됩니다.

## 좋은 인터페이스를 만드는 다섯 단계

### 1단계 — 호출자의 언어로 이름 짓기

```python
# 1_naming.py
# Bad: process_data()
# Good: charge_user()
```

메서드 이름은 구현 절차보다 의도를 담아야 합니다. `process_data`보다 `charge_user`가 훨씬 많은 문맥을 전달합니다.

### 2단계 — 추상화 높이를 맞춘다

```python
# 2_level.py
# Bad: send_bytes_over_tcp(host, port, payload)
# Good: notify(user, message)
```

호출자가 네트워크 소켓 세부를 신경 쓰지 않아도 된다면 인터페이스에 올릴 이유도 없습니다. 추상화는 필요한 디테일만 남기고 나머지는 숨기는 일입니다.

### 3단계 — 인자는 적게, 의도는 분명하게 둔다

```python
# 3_params.py
# Bad: charge(u, a, c, r, m, x, y)
# Good: charge(user, amount, *, reason)
```

위치 인자가 계속 늘어나면 호출 의도가 흐려집니다. 인자 수가 많아질수록 인터페이스가 너무 많은 일을 요구하는지 의심해 볼 필요가 있습니다.

### 4단계 — LSP를 확인한다

```python
# 4_lsp.py
class Bird:
    def fly(self): ...

class Penguin(Bird):
    def fly(self): raise NotImplementedError
# Callers break — Bird itself needs a redesign.
```

하위 타입이 상위 타입의 약속을 깨면, 문제는 펭귄 하나가 아니라 상위 인터페이스 설계일 가능성이 큽니다. 타입 계층을 다시 생각해야 합니다.

### 5단계 — 큰 인터페이스 하나보다 작은 인터페이스 여러 개를 둔다

```python
# 5_isp.py
class Reader:
    def read(self): ...

class Writer:
    def write(self, x): ...
# Better than one giant IO interface.
```

읽기만 필요한 호출자에게 쓰기 메서드까지 강요하면 불필요한 결합이 생깁니다. 인터페이스도 책임별로 나뉘는 편이 좋습니다.

## 빠르게 검증해 보기

인터페이스 품질을 빠르게 보려면 메서드 이름과 인자 목록만 따로 빼서 읽어 보세요. 구현 설명 없이도 호출 의도가 보이면 추상화 높이가 맞을 가능성이 큽니다.

```python
class Notifier:
    def send(self, user, msg): ...
```

**Expected output:** 이름만 봐도 호출자가 무엇을 원하는지 읽히고, 구현 교체가 필요할 때도 호출 코드가 크게 바뀌지 않아야 합니다.

그다음 하위 구현 하나를 골라 상위 계약을 깨지 않는지 확인합니다. `NotImplementedError`를 던지기 시작하면 인터페이스 설계를 다시 봐야 합니다.

## 실패 신호와 먼저 볼 것

| 실패 신호 | 먼저 볼 것 |
| --- | --- |
| 메서드 이름이 구현 용어로 가득하다 | 호출자 언어가 아니라 구현자 언어인지 봅니다 |
| 인자가 계속 늘어난다 | 인터페이스가 여러 책임을 품고 있는지 확인합니다 |
| 하위 타입이 예외로 계약을 회피한다 | 상위 타입의 약속 자체를 다시 설계합니다 |

좋은 인터페이스는 구현을 감추는 것보다, 호출자의 의도를 짧고 안정적으로 표현하는 데 더 가깝습니다.

## 이 코드에서 먼저 볼 점

- 이름이 구현이 아니라 호출자의 어휘에 맞춰져 있습니다.
- 인자 목록이 짧고 의미가 선명합니다.
- 구현을 바꿔도 호출자 쪽 파급이 작습니다.

## 어디서 많이 헷갈릴까

인터페이스를 추가하는 것과 추상화를 잘하는 것은 다릅니다. 메서드 이름이 `flush_buffer`, `get_redis_client`처럼 구현 용어를 그대로 담고 있다면, 타입만 인터페이스일 뿐 추상화 높이는 거의 그대로일 수 있습니다.

또 하나 흔한 실수는 LSP 문제를 하위 클래스 탓으로만 보는 것입니다. 펭귄이 날 수 없는 것이 잘못이 아니라, `Bird`라는 상위 타입이 “날 수 있음”을 기본 약속으로 삼은 설계가 잘못됐을 가능성이 큽니다.

## 실무에서는 이렇게 본다

결제 게이트웨이, 저장소, 알림 채널처럼 구현 교체가 자주 일어나는 곳에서 인터페이스 품질은 바로 비용으로 이어집니다. 잘 설계된 인터페이스는 벤더 교체나 테스트 대체 구현이 들어와도 호출자가 거의 변하지 않게 합니다.

코드 리뷰에서는 이런 질문을 던지면 좋습니다. “이 이름이 호출자의 의도를 말하는가?”, “이 인자 중 구현 세부가 섞여 있지 않은가?”, “하위 타입이 상위 계약을 정말 지키는가?”, “읽기 전용 호출자에게 쓰기까지 강요하고 있지 않은가?”

## 체크리스트

- [ ] 메서드 이름이 호출자의 언어로 읽히는가?
- [ ] 인자 수가 적고 의도가 분명한가?
- [ ] 하위 타입이 상위 타입의 계약을 깨지 않는가?
- [ ] 인터페이스가 한 가지 책임에 집중하는가?
- [ ] 구현 세부가 인터페이스 밖으로 새지 않는가?

## 연습 문제

1. 현재 코드의 인터페이스 하나를 골라 인자 수를 줄여 보세요.
2. 큰 인터페이스 하나를 두 개의 좁은 인터페이스로 나눠 보세요.
3. 코드베이스에서 LSP 위반 사례 하나를 찾고 무엇을 바꿔야 할지 적어 보세요.

## 정리

좋은 인터페이스는 자유의 단위입니다. 호출자는 의도만 말하고, 구현은 뒤에서 바뀔 수 있어야 합니다. 추상화 수준이 맞고 계약이 안정적일수록 구조는 더 오래 버팁니다.

다음 글에서는 이런 인터페이스들이 모여 만드는 큰 구조, 계층 아키텍처를 다룹니다.

## 설계 경계를 코드로 내리는 추가 예시

실무에서 설계 논의가 길어지는 이유는 "모듈 경계"가 문장으로만 남기 쉽기 때문입니다. 경계를 글로 합의한 뒤 코드로 고정하지 않으면 다음 기능을 붙이는 순간 경계가 다시 흐려집니다. 그래서 설계 문서와 함께, 경계를 강제하는 최소한의 구조를 코드에 먼저 두는 방식이 안전합니다.

### 모듈 경계 예시: 주문 결제 도메인

아래 구조는 결제 정책, 결제 수단 어댑터, 외부 API 호출을 분리합니다. 핵심은 도메인 모듈이 인프라 구현을 직접 모르고, 인터페이스를 통해서만 협력한다는 점입니다.

```text
order/
  domain/
    payment_policy.py
    ports.py
  application/
    checkout_service.py
  infrastructure/
    stripe_gateway.py
    kakao_gateway.py
```

```python
# domain/ports.py
from typing import Protocol

class PaymentGateway(Protocol):
    def authorize(self, order_id: str, amount: int) -> str: ...
    def capture(self, payment_id: str) -> None: ...

class RiskChecker(Protocol):
    def is_suspicious(self, user_id: str, amount: int) -> bool: ...
```

이렇게 포트를 먼저 정의하면 애플리케이션 계층은 "무엇을 요청하는가"만 알면 됩니다. Stripe, KakaoPay, 사내 결제 모듈처럼 구현체가 달라져도 애플리케이션 서비스의 제어 흐름은 유지됩니다. 변경 비용을 구현체 내부로 가두는 효과가 생깁니다.

### 의존성 주입(DI) 예시: 생성 시점에서 연결

```python
# application/checkout_service.py
from dataclasses import dataclass
from domain.ports import PaymentGateway, RiskChecker

@dataclass
class CheckoutService:
    gateway: PaymentGateway
    risk_checker: RiskChecker

    def checkout(self, order_id: str, user_id: str, amount: int) -> str:
        if self.risk_checker.is_suspicious(user_id, amount):
            raise ValueError("risk blocked")
        payment_id = self.gateway.authorize(order_id, amount)
        self.gateway.capture(payment_id)
        return payment_id
```

```python
# composition_root.py
from application.checkout_service import CheckoutService
from infrastructure.stripe_gateway import StripeGateway
from infrastructure.simple_risk_checker import SimpleRiskChecker

service = CheckoutService(
    gateway=StripeGateway(api_key="masked"),
    risk_checker=SimpleRiskChecker(),
)
```

DI의 핵심은 프레임워크 사용 여부가 아니라 "조립 위치"를 분리하는 것입니다. 비즈니스 로직 내부에서 구현체를 `new` 하지 않으면 테스트에서 대체 객체를 넣기 쉬워지고, 운영에서 구현체 교체 시 영향 범위가 줄어듭니다.

### 인터페이스 패턴: 정책 객체 분리

가격 계산이나 할인 규칙은 가장 자주 바뀌는 영역입니다. 이 규칙을 서비스 코드 안에 `if` 체인으로 붙이면 기능은 빠르게 나오지만 변경 지점이 폭발합니다. 아래처럼 정책 인터페이스를 두면 규칙 추가를 클래스 추가로 제한할 수 있습니다.

```python
from typing import Protocol

class DiscountPolicy(Protocol):
    def discount(self, amount: int) -> int: ...

class RatePolicy:
    def __init__(self, rate: float) -> None:
        self.rate = rate

    def discount(self, amount: int) -> int:
        return int(amount * self.rate)

class FixedPolicy:
    def __init__(self, fixed: int) -> None:
        self.fixed = fixed

    def discount(self, amount: int) -> int:
        return min(self.fixed, amount)
```

정책 인터페이스를 쓰면 런타임 선택도 단순해집니다. 신규 캠페인 규칙은 기존 서비스 코드를 수정하기보다 새 정책 클래스를 추가하고 조립부에서 연결하면 끝납니다. 이 방식은 OCP를 실무적으로 지키는 가장 단순한 패턴입니다.

### 경계 품질을 확인하는 운영 체크

- 모듈 경계를 넘는 import가 늘어나는지 주간으로 확인합니다.
- 애플리케이션 계층에서 인프라 타입을 직접 참조하는지 검사합니다.
- 변경 요청 하나당 수정 파일 수를 기록해 경계 누수를 추적합니다.
- 구현체 교체(예: 결제 게이트웨이 변경) 리허설을 분기마다 1회 실행합니다.

설계는 문서에서 시작하지만, 유지보수성은 경계 강제 구조와 조립 규칙에서 결정됩니다. 경계를 합의한 다음 즉시 포트, 조립부, 테스트 대역을 갖춘 최소 코드를 두면 다음 변경에서 체감되는 비용 차이가 명확하게 나타납니다.

## 처음 질문으로 돌아가기

- **더 나은 인터페이스는 무엇으로 판단할 수 있을까요?**
  - 본문의 기준은 인터페이스와 추상화를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **추상화 수준이 너무 낮거나 높으면 어떤 문제가 생길까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **다형성은 분기문을 어떻게 줄여 줄까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Software Design 101 (1/10): 소프트웨어 설계란 무엇인가?](./01-what-is-software-design.md)
- [Software Design 101 (2/10): 관심사 분리](./02-separation-of-concerns.md)
- [Software Design 101 (3/10): 모듈과 경계](./03-modules-and-boundaries.md)
- [Software Design 101 (4/10): 의존성 방향](./04-dependency-direction.md)
- **인터페이스와 추상화 (현재 글)**
- 계층 아키텍처 (예정)
- 데이터 흐름 설계 (예정)
- 변경 영향 줄이기 (예정)
- 설계 원칙 모음 (예정)
- 작은 프로젝트로 설계 연습 (예정)

<!-- toc:end -->

## 참고 자료

- [Liskov Substitution Principle (Barbara Liskov)](https://www.cs.cmu.edu/~wing/publications/LiskovWing94.pdf)
- [Interface Segregation Principle](https://web.archive.org/web/20150905081110/http://www.objectmentor.com/resources/articles/isp.pdf)
- [Joshua Bloch — How to Design a Good API](https://www.youtube.com/watch?v=heh4OeB9A-c)
- [Designing Data-Intensive Applications — Abstractions](https://dataintensive.net/)

### 실전 확인용 문서

- [typing.Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol)
- [abc — Abstract Base Classes](https://docs.python.org/3/library/abc.html)

Tags: Computer Science, SoftwareDesign, Interfaces, Abstraction, LSP, Polymorphism
