---
series: design-patterns-101
episode: 1
title: "디자인 패턴 101 (1/10): 디자인 패턴이란 무엇인가?"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - DesignPatterns
  - SoftwareDesign
  - GoF
  - Architecture
  - Foundations
seo_description: 디자인 패턴을 정답집이 아니라 반복되는 설계 문제를 설명하고 합의하는 공통 어휘로 이해하도록 돕는 입문 글입니다.
last_reviewed: '2026-05-15'
---

# 디자인 패턴 101 (1/10): 디자인 패턴이란 무엇인가?

디자인 패턴을 처음 배우면 대개 이름부터 외우기 시작합니다. Strategy, Adapter, Observer 같은 이름이 먼저 보이기 때문입니다. 하지만 실무에서 패턴이 힘을 발휘하는 순간은 암기 시험이 아니라, 같은 문제를 반복해서 만나는 시점입니다.

이 글은 Design Patterns 101 시리즈의 첫 번째 글입니다.

이번 글에서는 디자인 패턴을 “정답 모음집”이 아니라, 반복되는 설계 문제를 빠르게 설명하고 합의하기 위한 공통 어휘로 정리해 보겠습니다. 핵심은 패턴 이름보다 먼저, 그 이름이 어떤 문제와 어떤 트레이드오프를 함께 불러오는지 이해하는 것입니다.

## 먼저 던지는 질문

- 디자인 패턴을 한 문장으로 정의하면 무엇일까요?
- GoF가 정리한 23개 패턴은 어떤 기준으로 나뉠까요?
- 패턴은 왜 코드보다 대화에서 먼저 가치를 만들까요?

## 큰 그림

![Design Patterns 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/01/01-01-concept-at-a-glance.ko.png)

*Design Patterns 101 1장 흐름 개요*

## 왜 중요한가

패턴의 가장 큰 효용은 구현 자체보다 합의 속도에 있습니다. 코드 리뷰에서 “여기 분기가 계속 늘어나니 Strategy로 빼자”라고 말했을 때, 팀 전체가 비슷한 구조를 즉시 떠올릴 수 있다면 이미 절반은 해결된 셈입니다.

반대로 패턴 이름만 알고 문제를 모르면 실무에서는 오히려 더 위험합니다. 이름은 그럴듯한데 왜 도입했는지 설명하지 못하면, 패턴은 설계를 단순화하는 도구가 아니라 복잡성을 정당화하는 장식이 됩니다.

## 한눈에 보는 개념

## 핵심 용어

- **디자인 패턴**: 반복해서 나타나는 설계 문제에 검증된 해법 구조를 붙인 이름입니다.
- **GoF**: Gang of Four를 뜻하며, 23개 패턴을 체계적으로 정리한 저자 그룹입니다.
- **Creational / Structural / Behavioral**: 생성, 구조, 행위를 기준으로 나눈 세 가지 패턴 계열입니다.
- **안티패턴**: 흔히 쓰이지만 결과적으로 해로운 접근입니다.
- **이디엄(idiom)**: 특정 언어의 문법과 관용구에 밀착된 작은 패턴입니다.

## 변경 전후 비교

**Before**

```python
# "if kind" branching scattered everywhere
if kind == "credit": process_credit(...)
elif kind == "paypal": process_paypal(...)
```

**After**

```python
# Strategy pattern in one line
processor = PROCESSORS[kind]
processor.charge(...)
```

이 차이의 핵심은 코드 길이가 아닙니다. 의도가 이름 붙은 구조로 드러났다는 점입니다. 패턴은 종종 구현보다 설명을 먼저 정리해 줍니다.

## 패턴을 익히는 5단계

### 1단계 — 문제를 먼저 알아봅니다

```python
# 1_problem.py
# Same branch, same object construction, same notification flow recurring?
# That is the stage for a pattern.
```

패턴은 공중에서 떨어지지 않습니다. 같은 분기, 같은 생성 방식, 같은 알림 흐름이 반복될 때 비로소 패턴을 꺼낼 이유가 생깁니다.

### 2단계 — 문제에 이름을 붙입니다

```python
# 2_name.py
# Branching? Strategy. Construction? Factory. Notifications? Observer.
```

이름은 단순한 라벨이 아닙니다. 문제와 해법 구조를 함께 호출하는 압축된 설명입니다.

### 3단계 — 구조를 먼저 그립니다

```python
# 3_structure.py
# Draw the class diagram before writing code.
```

패턴은 코드 조각이 아니라 관계의 모양입니다. 클래스를 어떻게 나누고, 누가 누구를 알고, 어디서 확장되는지 먼저 그려 보면 과한 설계를 줄이기 쉽습니다.

### 4단계 — 작게 적용합니다

```python
# 4_small.py
# Try it in one module before applying it system-wide.
```

처음부터 시스템 전체에 패턴을 퍼뜨리면 실패 비용이 커집니다. 한 모듈, 한 경계, 한 분기부터 적용해 보고 실제 이득이 있는지 확인하는 편이 안전합니다.

### 5단계 — 트레이드오프를 적어 둡니다

```python
# 5_tradeoff.md
# - Gained: branching gone, easier to extend
# - Lost: more classes to read
```

패턴은 늘 무언가를 얻는 대신 다른 비용을 추가합니다. 그 비용을 적지 않는 순간, 팀은 복잡성을 공짜라고 착각하기 쉽습니다.

## 이 코드에서 주목할 점

- 패턴은 코드를 바꾸기 전에 팀의 대화 방식을 먼저 바꿉니다.
- 어떤 패턴이든 이득과 비용이 함께 움직입니다.
- 패턴 적용 범위는 대개 전역이 아니라 국소적입니다.

## 자주 하는 실수 5가지

1. **어디에나 패턴을 들이대는 경우**: 단순한 코드가 불필요하게 복잡해집니다.
2. **이름만 외우고 문제를 모르는 경우**: 적용해야 할 순간을 못 알아봅니다.
3. **언어 특성을 무시하는 경우**: Python에서 모듈이면 충분한데 Singleton 클래스를 억지로 만듭니다.
4. **트레이드오프를 빼먹는 경우**: 클래스만 늘고 설명 가능성은 오히려 떨어집니다.
5. **패턴이 곧 정답이라고 믿는 경우**: 더 단순한 해법을 놓칩니다.

## 실무에서는 이렇게 드러납니다

패턴은 보통 코드 리뷰 어휘로 가장 자주 등장합니다. “여긴 Adapter 경계가 필요합니다”, “이 분기는 Strategy 모양입니다” 같은 말이 팀 안에서 자연스럽게 통하면, 설계 대화의 해상도가 훨씬 높아집니다. 결국 패턴은 구현 세부보다 합의를 빠르게 만드는 도구입니다.

## 빠르게 검증해 보기

패턴을 붙이기 전에 아래 세 가지를 먼저 확인해 보세요.

- 같은 분기, 생성, 알림 구조가 실제 코드에 세 번 이상 반복되는지 셉니다.
- 패턴 이름을 붙이기 전에 문제를 한 문장으로 적어 봅니다.
- 패턴을 도입했을 때 설명이 쉬워지는지, 아니면 추상화만 늘어나는지 비교합니다.

**기대 결과:** 패턴이 도움이 되는 경우, “왜 이 패턴이 필요한지”와 “무슨 비용이 생기는지”를 동시에 설명할 수 있어야 합니다.

## 시니어 엔지니어는 이렇게 판단합니다

- 패턴을 해법이 아니라 공통 어휘로 다룹니다.
- 이름보다 문제를 먼저 봅니다.
- 전역 적용보다 작은 범위에서 효과를 검증합니다.
- 트레이드오프를 항상 함께 설명합니다.
- 마지막까지 더 단순한 해법이 없는지 다시 확인합니다.

## 체크리스트

- [ ] 내가 푸는 문제를 한 줄로 적을 수 있는가?
- [ ] 그 문제에 어울리는 패턴 이름이 자연스럽게 떠오르는가?
- [ ] 구조를 코드보다 먼저 설명할 수 있는가?
- [ ] 이득과 비용을 함께 적었는가?
- [ ] 패턴 없이 더 단순하게 풀 수는 없는가?

## 연습 문제

1. 현재 코드에서 같은 분기 구조가 세 번 이상 반복되는 지점을 하나 찾습니다.
2. 그 문제에 가장 잘 맞는 패턴 이름을 하나 붙여 봅니다.
3. 적용 후 얻은 점 두 가지와 잃은 점 두 가지를 적어 봅니다.

## 정리 및 다음 글

디자인 패턴은 정답이 아니라 어휘입니다. 다음 글부터는 GoF의 23개 패턴을 생성, 구조, 행위 세 묶음으로 나눠서 살펴보겠습니다. 먼저 객체를 어떻게 만들 것인가를 다루는 Creational 패턴부터 시작합니다.

## 실전 보강: 패턴 선택을 코드와 표로 검증하기

디자인 패턴은 이름을 아는 것보다 **언제 적용하고 언제 버릴지**를 결정하는 능력이 더 중요합니다. 아래 보강 내용은 Python 코드, UML 유사 다이어그램, 선택 기준 표를 함께 사용해 판단 근거를 명확히 만드는 데 초점을 둡니다.

### 1) 전략 교체를 런타임으로 밀어내는 패턴

```python
from dataclasses import dataclass
from typing import Protocol

class DiscountPolicy(Protocol):
    def apply(self, price: int) -> int: ...

@dataclass
class NoDiscount:
    def apply(self, price: int) -> int:
        return price

@dataclass
class PercentDiscount:
    rate: float
    def apply(self, price: int) -> int:
        return int(price * (1 - self.rate))

@dataclass
class PriceCalculator:
    policy: DiscountPolicy

    def final_price(self, price: int) -> int:
        return self.policy.apply(price)
```

이 구조의 핵심은 `if/elif` 분기 증가를 객체 교체로 바꾸는 것입니다. 정책이 늘어도 기존 계산기 코드는 수정 없이 확장할 수 있습니다.

### 2) 유엠엘 유사 텍스트 다이어그램

```text
[Client] --> [PriceCalculator]
[PriceCalculator] --uses--> <<interface>> DiscountPolicy
[NoDiscount] ----implements----> DiscountPolicy
[PercentDiscount] -implements--> DiscountPolicy
```

다이어그램으로 보면 의존 방향이 분명해집니다. 구체 클래스가 아니라 추상 인터페이스로 향하면 테스트 더블 주입과 기능 확장이 쉬워집니다.

### 3) 패턴 도입 판단표

| 상황 | 도입 권장 패턴 | 기대 이점 | 과사용 신호 |
| --- | --- | --- | --- |
| 정책 분기가 자주 늘어남 | Strategy | 조건문 감소, 교체 용이 | 정책이 1개인데 인터페이스만 복잡 |
| 객체 생성 규칙이 다양함 | Factory | 생성 책임 분리 | 생성 규칙이 단순한데 팩토리 계층 과다 |
| 외부 라이브러리 인터페이스 상이 | Adapter | 호출부 안정화 | 어댑터가 비즈니스 규칙까지 흡수 |
| 이벤트 구독자가 동적으로 변함 | Observer | 결합도 완화 | 이벤트 흐름 추적 불가, 디버깅 난해 |

표를 사용하면 “패턴을 넣을지 말지”를 감각이 아니라 조건으로 설명할 수 있습니다.

### 4) 안티패턴 회피 예시

```python
# 과한 추상화 예시(피해야 함)
class AbstractFactoryProviderManager:
    def get_factory(self):
        ...

# 개선: 실제 문제에 맞춘 단순 함수

def build_storage(kind: str):
    if kind == "memory":
        return {}
    if kind == "sqlite":
        import sqlite3
        return sqlite3.connect("app.db")
    raise ValueError("unsupported storage")
```

패턴은 복잡성을 제거할 때만 가치가 있습니다. 불필요한 추상화 계층은 코드 탐색 비용만 늘립니다.

### 5) 테스트 가능성 기준으로 최종 판단

| 질문 | Pass 기준 |
| --- | --- |
| 교체 가능한 인터페이스가 필요한가 | 런타임 정책 변경 요구가 있음 |
| 테스트 더블 주입이 실제로 유용한가 | 외부 의존성 분리가 테스트 속도를 높임 |
| 새 요구가 들어올 때 수정 범위가 줄어드는가 | 기존 클래스 수정 없이 신규 클래스 추가 가능 |
| 팀이 패턴을 공통 언어로 이해하는가 | 리뷰에서 동일 용어로 의사결정 가능 |

패턴의 목적은 미학이 아니라 변경 비용 절감입니다. 코드, 다이어그램, 표 세 가지를 함께 점검하면 과설계와 미설계를 동시에 줄일 수 있습니다.

### 추가 사례: 패턴 적용 전후 비교

```python
# Before: 조건문이 도메인 로직 곳곳에 흩어진 경우

def notify(channel: str, message: str) -> None:
    if channel == "email":
        send_email(message)
    elif channel == "slack":
        send_slack(message)
    elif channel == "sms":
        send_sms(message)
    else:
        raise ValueError("unsupported channel")
```

```python
# After: 전략 등록 방식
from typing import Callable

class Notifier:
    def __init__(self) -> None:
        self._handlers: dict[str, Callable[[str], None]] = {}

    def register(self, channel: str, handler: Callable[[str], None]) -> None:
        self._handlers[channel] = handler

    def notify(self, channel: str, message: str) -> None:
        if channel not in self._handlers:
            raise ValueError("unsupported channel")
        self._handlers[channel](message)
```

이 전환의 장점은 기능 추가 시 기존 분기 로직을 수정하지 않아도 된다는 점입니다. 변경 충돌이 줄고 테스트 범위가 국소화됩니다.

| 평가 항목 | 분기 확장 방식 | 패턴 기반 방식 |
| --- | --- | --- |
| 신규 채널 추가 | 기존 함수 수정 필요 | 등록 코드 추가 |
| 회귀 위험 | 높음 | 낮음 |
| 테스트 범위 | 기존 케이스 재검증 범위 큼 | 신규 핸들러 중심 검증 |
| 리뷰 난이도 | 조건 중첩으로 상승 | 역할 분리로 하락 |

이처럼 패턴은 코드 양을 줄이는 도구라기보다, 변경 시 영향 범위를 예측 가능하게 만드는 구조적 장치입니다.

## 실무 심화: 패턴을 설계 의사결정 문서로 연결하기

패턴 학습의 목적은 이름을 아는 데서 끝나지 않습니다. 실무에서는 "왜 이 구조를 선택했는가"를 나중에 다시 설명해야 하고, 팀이 바뀌어도 같은 판단을 재현할 수 있어야 합니다. 그래서 패턴은 코드 안에만 두지 않고 ADR(Architecture Decision Record), 리뷰 체크리스트, 테스트 설계와 함께 다뤄야 합니다.

### 유엠엘 유사 다이어그램으로 책임 경계 확인

```text
[요구사항] --> [의사결정]
[의사결정] --> [패턴 후보: Strategy/Adapter/Observer]
[패턴 후보] --> [코드 구조]
[코드 구조] --> [테스트 전략]
[테스트 전략] --> [운영 지표]
```

이 흐름을 문서로 남기면 패턴 도입이 취향 논쟁이 아니라 근거 기반 결정이 됩니다.

### 변경 전후 리팩터링

```python
# 변경 전: 주문 할인 정책이 서비스 레이어에 박혀 있는 경우

def checkout(user_tier: str, amount: int) -> int:
    if user_tier == "vip":
        return int(amount * 0.8)
    if user_tier == "partner":
        return int(amount * 0.9)
    return amount
```

```python
# 변경 후: 정책 객체로 분리
from typing import Protocol

class DiscountPolicy(Protocol):
    def apply(self, amount: int) -> int: ...

class VipPolicy:
    def apply(self, amount: int) -> int:
        return int(amount * 0.8)

class PartnerPolicy:
    def apply(self, amount: int) -> int:
        return int(amount * 0.9)

class CheckoutService:
    def __init__(self, policy: DiscountPolicy) -> None:
        self.policy = policy

    def checkout(self, amount: int) -> int:
        return self.policy.apply(amount)
```

리팩터링 포인트는 코드 길이가 아니라 변경 축의 분리입니다. 정책 변경이 서비스 로직을 흔들지 않게 만들면 배포 리스크가 줄어듭니다.

### 장고/플라스크에서 드러나는 패턴

- Django에서는 결제, 알림, 권한 정책을 서비스 객체로 분리할 때 Strategy 성격이 자연스럽게 등장합니다.
- Flask에서는 블루프린트 경계에서 외부 SDK를 Adapter로 감싼 뒤 도메인 인터페이스만 노출하면 테스트가 쉬워집니다.
- 공통적으로 "프레임워크 객체를 도메인으로 직접 흘려보내지 않는다"는 경계 규칙이 유지보수 비용을 결정합니다.

### 솔리드 매핑으로 검증하기

| 관점 | 패턴 적용 전 | 패턴 적용 후 |
| --- | --- | --- |
| SRP | 서비스가 정책+흐름을 함께 가짐 | 정책 책임과 흐름 책임 분리 |
| OCP | 정책 추가 시 기존 함수 수정 | 정책 클래스 추가로 확장 |
| DIP | 구체 조건문에 의존 | 추상 정책 인터페이스 의존 |

이 표를 리뷰 때 사용하면 "패턴을 왜 넣었는지"를 기능 관점이 아닌 설계 관점으로 합의할 수 있습니다.

### 운영 관점 체크

1. 정책이 늘어날 때 테스트 케이스가 선형적으로 증가하는지 확인합니다.
2. 새 정책 추가가 기존 코드 수정 없이 가능한지 PR 단위로 검증합니다.
3. 로그에 정책 이름과 적용 결과를 남겨 장애 시 재현 가능성을 확보합니다.

패턴은 예쁜 구조를 위한 장식이 아니라, 변경 비용과 장애 비용을 줄이기 위한 안전장치입니다.


## 심화 워크숍: 패턴 적용을 운영 가능한 설계로 바꾸는 절차

패턴을 도입한 뒤 품질이 안정되는 팀과 그렇지 않은 팀의 차이는 구현 문법이 아니라 검증 절차입니다. 아래 절차는 패턴 적용을 코드 예제 수준에서 끝내지 않고, 리뷰/테스트/운영까지 연결하는 실무형 워크플로를 정리한 것입니다.

### 1단계: 요구사항을 변화 축으로 분해합니다

요구사항을 기능 단위로만 보면 패턴이 과하거나 부족해집니다. 먼저 "무엇이 자주 바뀌는지"를 분리해야 합니다. 예를 들어 결제 수단, 알림 채널, 저장소 구현, 권한 규칙은 변화 주기가 서로 다릅니다. 변화 주기가 다르면 클래스 경계도 달라져야 합니다.

```text
[요구사항]
  |- 자주 바뀜: 채널/정책/외부 API 계약
  |- 가끔 바뀜: 도메인 규칙
  |- 거의 안 바뀜: 엔터티 핵심 필드
```

이 분해를 먼저 하면 패턴 적용 대상이 명확해집니다.

### 2단계: 변경 전후를 코드로 고정합니다

```python
# 변경 전: 분기와 생성이 한 함수에 결합

def dispatch(kind: str, payload: dict) -> None:
    if kind == "email":
        client = SmtpClient(host="...")
        client.send(payload["to"], payload["body"])
    elif kind == "slack":
        client = SlackClient(webhook="...")
        client.push(payload["body"])
    else:
        raise ValueError("unsupported kind")
```

```python
# 변경 후: 생성과 실행을 분리
from typing import Protocol

class Sender(Protocol):
    def send(self, payload: dict) -> None: ...

class SenderFactory:
    def __init__(self, config: dict) -> None:
        self.config = config

    def create(self, kind: str) -> Sender:
        if kind == "email":
            return EmailSender(self.config["smtp_host"])
        if kind == "slack":
            return SlackSender(self.config["slack_webhook"])
        raise ValueError("unsupported kind")

class DispatchService:
    def __init__(self, factory: SenderFactory) -> None:
        self.factory = factory

    def dispatch(self, kind: str, payload: dict) -> None:
        self.factory.create(kind).send(payload)
```

변경 후 코드에서는 테스트 범위를 계층별로 나눌 수 있고, 새 채널 추가 시 수정 지점을 예측하기 쉬워집니다.

### 3단계: 유엠엘 유사 다이어그램으로 의존 방향을 검증합니다

```text
[Controller] --> [DispatchService]
[DispatchService] --> [SenderFactory]
[SenderFactory] --creates--> <<interface>> [Sender]
[EmailSender] --implements--> [Sender]
[SlackSender] --implements--> [Sender]
```

의존 방향이 위에서 아래로 한 번만 흐르면 코드 탐색 비용이 줄어듭니다.

### 4단계: 장고/플라스크 적용 지점을 분리합니다

- Django: `apps.py` 또는 설정 초기화 지점에서 팩토리/전략 조립을 끝내고, 뷰는 서비스 인터페이스만 호출합니다.
- Flask: `create_app()`에서 의존성 조립을 수행하고 블루프린트는 도메인 서비스에만 의존합니다.
- 공통 규칙: 프레임워크 객체(`request`, ORM 세션, 외부 SDK 클라이언트)를 도메인 모델 안으로 직접 흘려보내지 않습니다.

### 5단계: 솔리드 매핑으로 설계 품질을 점검합니다

| 원칙 | 적용 전 리스크 | 적용 후 기대 효과 |
| --- | --- | --- |
| SRP | 한 클래스가 정책/생성/실행을 동시에 담당 | 책임 분리로 변경 파급 축소 |
| OCP | 새 기능마다 기존 분기 수정 | 확장 지점 추가 중심으로 전환 |
| LSP | 대체 구현이 계약을 깨뜨림 | 인터페이스 테스트로 대체 가능성 보장 |
| ISP | 거대한 인터페이스 강요 | 용도별 작은 인터페이스 유지 |
| DIP | 상위 계층이 구체 SDK에 결합 | 추상 계약 의존으로 테스트 용이 |

### 6단계: 운영 로그와 알람 포인트를 함께 정의합니다

패턴을 적용해도 관측이 없으면 운영에서 효과를 확인할 수 없습니다. 다음 항목을 로그에 남겨야 합니다.

1. 선택된 전략/어댑터/팩토리 구현 이름
2. 처리 시간과 실패 원인(예외 타입)
3. 재시도 횟수와 최종 상태

이 로그가 있어야 "패턴 도입 이후 장애 회복 시간이 줄었는가"를 측정할 수 있습니다.

### 7단계: 테스트를 세 계층으로 분리합니다

```python
# 단위 테스트: 전략/어댑터 계약 테스트

def test_email_sender_contract():
    sender = FakeEmailSender()
    sender.send({"to": "a@example.com", "body": "hello"})
    assert sender.sent_count == 1
```

```python
# 통합 테스트: 팩토리 조립 + 서비스 실행

def test_dispatch_service_with_memory_config():
    cfg = {"smtp_host": "localhost", "slack_webhook": "http://localhost"}
    service = DispatchService(SenderFactory(cfg))
    service.dispatch("email", {"to": "a@example.com", "body": "x"})
```

```python
# 회귀 테스트: 새 구현 추가 시 기존 계약 보존

def test_new_sender_does_not_break_existing_contract():
    for sender in [FakeEmailSender(), FakeSlackSender()]:
        sender.send({"body": "ok"})
```

계층 분리를 하면 실패 원인을 더 빨리 좁힐 수 있습니다.

### 8단계: 패턴 남용 방지 규칙을 명시합니다

- 클래스 수가 늘어도 변경 지점 수가 줄지 않으면 과설계입니다.
- 인터페이스를 만들었는데 구현이 1개로 6개월 이상 유지되면 단순화 후보입니다.
- 패턴 이름을 설명해도 비즈니스 이득을 말할 수 없다면 적용 근거가 약합니다.

### 9단계: 문서화 템플릿

다음 템플릿을 ADR에 기록하면 팀 합의가 빨라집니다.

```text
문제: 어떤 변화가 반복되는가?
제약: 성능/보안/테스트/팀 숙련도 제약은 무엇인가?
선택: 어떤 패턴을 적용했는가?
대안: 왜 다른 패턴은 선택하지 않았는가?
결과: 얻는 이점과 추가 비용은 무엇인가?
```

### 10단계: 릴리스 후 회고 질문

1. 새 요구 추가 시 PR 수정 파일 수가 줄었는가?
2. 장애 발생 시 원인 계층(생성/구조/행위)을 빠르게 특정했는가?
3. 테스트 실행 시간이 합리적 수준으로 유지되는가?

이 회고를 반복하면 패턴은 지식이 아니라 조직 역량으로 축적됩니다.


## 처음 질문으로 돌아가기

- **디자인 패턴을 한 문장으로 정의하면 무엇일까요?**
  - 본문의 기준은 디자인 패턴이란 무엇인가?를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **GoF가 정리한 23개 패턴은 어떤 기준으로 나뉠까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **패턴은 왜 코드보다 대화에서 먼저 가치를 만들까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **디자인 패턴이란 무엇인가? (현재 글)**
- Creational 패턴 (예정)
- Structural 패턴 (예정)
- Behavioral 패턴 (예정)
- Strategy 패턴 (예정)
- Adapter 패턴 (예정)
- Observer 패턴 (예정)
- Factory와 의존성 주입 (예정)
- 패턴을 남용하지 않는 법 (예정)
- Python에 어울리는 패턴 (예정)

<!-- toc:end -->

## 참고 자료

### 핵심 자료

- [Design Patterns: Elements of Reusable Object-Oriented Software (GoF)](https://en.wikipedia.org/wiki/Design_Patterns)
- [refactoring.guru — Design Patterns](https://refactoring.guru/design-patterns)
- [Patterns of Enterprise Application Architecture](https://martinfowler.com/eaaCatalog/)

### 실무 확장 읽을거리

- [Head First Design Patterns](https://www.oreilly.com/library/view/head-first-design/9781492077992/)
- [Refactoring (Martin Fowler)](https://martinfowler.com/books/refactoring.html)

- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/ko)

Tags: Computer Science, DesignPatterns, SoftwareDesign, GoF, Architecture, Foundations
