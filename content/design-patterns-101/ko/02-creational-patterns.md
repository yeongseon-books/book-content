---
series: design-patterns-101
episode: 2
title: "디자인 패턴 101 (2/10): 생성 패턴"
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
  - Creational
  - Factory
  - Singleton
  - Builder
seo_description: Creational 패턴으로 객체 생성 책임을 분리하고 결합도를 낮추는 방법을 설명합니다.
last_reviewed: '2026-05-15'
---

# 디자인 패턴 101 (2/10): 생성 패턴

코드를 읽다 보면 객체를 쓰는 코드보다 객체를 만드는 코드가 더 눈에 띄는 순간이 있습니다. `new SomeService()`가 도메인 곳곳에 흩어지고, 환경에 따라 다른 구현을 골라야 하고, 생성 인자가 계속 늘어나기 시작할 때입니다. 이 시점부터 문제는 기능보다 생성 책임의 위치로 옮겨갑니다.

이 글은 Design Patterns 101 시리즈의 2번째 글입니다.

이번 글에서는 Creational 패턴을 “객체를 멋지게 만드는 기법”이 아니라, 생성 책임을 한곳에 모아 결합도를 낮추는 설계 도구로 보겠습니다. 무엇을 만들지보다, 누가 만들고 어디서 조립하는지가 더 중요합니다.


![Design Patterns 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/02/02-01-concept-at-a-glance.ko.png)
*Design Patterns 101 2장 흐름 개요*

## 먼저 던지는 질문

- Creational 패턴은 정확히 어떤 설계 문제를 풀까요?
- Factory Method와 Abstract Factory는 어디서 갈릴까요?
- Builder는 언제 필요하고 언제 과할까요?

## 왜 중요한가

도메인 코드 안에 `new SomeService()`가 흩어져 있으면, 시스템은 이미 구체 구현과 강하게 묶인 상태입니다. 나중에 구현을 바꾸려면 호출자까지 함께 바꿔야 하고, 테스트에서는 가짜 객체를 끼워 넣기도 어려워집니다.

Creational 패턴은 이 문제를 정면으로 다룹니다. 생성 분기를 한곳에 모으고, 복잡한 조립을 단계로 나누고, 관련 객체를 묶어서 만들고, 필요하면 기존 객체를 복제해 새 인스턴스를 만듭니다. 결국 목표는 같습니다. 사용하는 코드가 생성 세부를 덜 알게 만드는 것입니다.

## 한눈에 보는 개념

## 핵심 용어

- **Factory Method**: 어떤 구체 클래스를 만들지 하위 구현이나 분기 로직이 결정하게 합니다.
- **Abstract Factory**: 관련된 객체 묶음을 일관된 가족 단위로 생성합니다.
- **Builder**: 복잡한 객체를 단계별로 조립합니다.
- **Singleton**: 인스턴스가 하나만 존재하도록 보장합니다.
- **Prototype**: 기존 객체를 복제해서 새 객체를 만듭니다.

## 변경 전후 비교

**Before**

```python
def make_notifier(kind):
    if kind == "email": return EmailNotifier(smtp_host="...")
    elif kind == "sms": return SmsNotifier(api_key="...")
```

**After**

```python
class NotifierFactory:
    def create(self, kind) -> Notifier: ...

# the caller knows nothing about the concrete class
notifier = factory.create(kind)
```

이후 호출자는 어떤 구현이 생성되는지 몰라도 됩니다. 생성 책임이 한곳으로 모였기 때문에 새 종류를 추가하거나 테스트 더블을 넣을 때 변경 범위를 훨씬 작게 유지할 수 있습니다.

## 생성 패턴을 익히는 5단계

### 1단계 — 팩토리 메서드로 분기를 한곳에 모읍니다

```python
# 1_factory.py
class Notifier:
    def send(self, msg): ...

class NotifierFactory:
    def create(self, kind: str) -> Notifier:
        if kind == "email": return EmailNotifier()
        if kind == "sms": return SmsNotifier()
        raise ValueError(kind)
```

여기서 중요한 점은 생성 분기가 여기 한곳에만 존재한다는 사실입니다. 호출자가 구현 선택을 떠안지 않게 만드는 것이 첫 번째 이득입니다.

### 2단계 — 추상 팩토리로 관련 객체를 함께 만듭니다

```python
# 2_abstract_factory.py
class UIFactory:
    def button(self) -> "Button": ...
    def textbox(self) -> "TextBox": ...

class MacFactory(UIFactory): ...
class WinFactory(UIFactory): ...
```

Mac용 버튼과 Mac용 텍스트박스처럼 같이 움직여야 하는 객체군이 있다면, 가족 단위 생성이 더 안전합니다. 조합이 뒤섞이는 실수를 줄일 수 있기 때문입니다.

### 3단계 — 빌더로 복잡한 조립을 읽히게 만듭니다

```python
# 3_builder.py
class QueryBuilder:
    def __init__(self): self.parts = []
    def select(self, *cols): self.parts.append(("SELECT", cols)); return self
    def from_(self, t): self.parts.append(("FROM", t)); return self
    def where(self, c): self.parts.append(("WHERE", c)); return self
    def build(self) -> str: ...
```

인자가 많고 조립 순서가 중요한 객체는 Builder가 효과적입니다. 생성자 한 줄에 모든 의미를 몰아넣는 대신, 단계 자체가 문서 역할을 하게 만들 수 있습니다.

### 4단계 — 싱글턴은 마지막 수단으로 다룹니다

```python
# 4_singleton.py
# In Python, the module itself is usually a singleton.
# A dedicated class is rarely necessary.
import logging
logger = logging.getLogger("app")
```

Singleton은 가장 쉽게 남용되는 Creational 패턴입니다. 인스턴스를 하나로 제한하는 순간 전역 상태와 수명 주기 문제가 따라오기 때문입니다. Python에서는 모듈 수준 객체로 충분한 경우가 많습니다.

### 5단계 — 프로토타입으로 복제가 더 싼 상황을 다룹니다

```python
# 5_prototype.py
import copy

class ReportTemplate:
    def __init__(self, layout): self.layout = layout

base = ReportTemplate({"header": "Q1", "rows": []})
def new_report():
    return copy.deepcopy(base)
```

생성 과정이 무겁고 기본 골격이 반복된다면 복제가 더 실용적일 수 있습니다. 다만 깊은 복사의 비용과 가변 데이터 공유 여부는 반드시 함께 봐야 합니다.

## 이 코드에서 주목할 점

- 호출자는 구체 클래스를 직접 알지 않아도 됩니다.
- 새 종류를 추가해도 호출자 코드를 건드리지 않을 수 있습니다.
- 복잡한 조립을 사람이 읽기 쉬운 단계로 분해합니다.

## 자주 하는 실수 5가지

1. **Singleton을 기본값처럼 쓰는 경우**: 결국 전역 변수와 다르지 않게 됩니다.
2. **Factory 안에 비즈니스 정책까지 넣는 경우**: 생성 책임과 도메인 규칙이 섞입니다.
3. **단순 객체에 Builder를 도입하는 경우**: 의식만 늘고 이득이 없습니다.
4. **가족이 하나뿐인데 Abstract Factory부터 도입하는 경우**: 미래를 상상한 추상화가 됩니다.
5. **Prototype의 deepcopy 비용을 무시하는 경우**: 성능 병목이 숨어듭니다.

## 실무에서는 이렇게 드러납니다

DI 컨테이너, ORM 쿼리 빌더, UI 컴포넌트 팩토리 같은 프레임워크 내부를 보면 Creational 패턴이 뼈대처럼 깔려 있습니다. 실무에서 이 패턴들을 알아야 하는 이유는 이름을 말하기 위해서가 아니라, 생성 책임이 어디에 모여 있는지 빠르게 읽어내기 위해서입니다.

## 빠르게 검증해 보기

Creational 패턴이 정말 필요한지 아래 기준으로 점검해 보세요.

- 같은 종류의 객체를 만드는 코드가 여러 호출자에 흩어져 있는지 확인합니다.
- 테스트에서 협력자를 바꾸기 위해 과한 monkey patch나 환경 분기가 필요한지 봅니다.
- 호출자가 구체 클래스, 생성자 인자, 환경별 분기를 꼭 알아야 하는지 따져 봅니다.

**기대 결과:** 리팩터링이 잘 되면 호출자는 생성 세부를 덜 알고, 테스트에서는 가짜 객체를 훨씬 쉽게 끼워 넣을 수 있어야 합니다.

## 시니어 엔지니어는 이렇게 판단합니다

- 생성 책임을 사용하는 코드 밖으로 밀어냅니다.
- Singleton은 정말 피할 수 없을 때만 선택합니다.
- 인자가 많고 조립 단계가 읽혀야 할 때 Builder를 꺼냅니다.
- 최소 두 가족 이상이 있을 때 Abstract Factory를 고려합니다.
- Prototype은 복제 비용까지 측정한 뒤에 채택합니다.

## 체크리스트

- [ ] 호출자가 구체 클래스를 몰라도 되는가?
- [ ] 새 종류를 추가해도 호출자 코드를 바꾸지 않는가?
- [ ] Singleton이 정말 필요한가?
- [ ] Builder가 실제로 복잡도를 낮추는가?
- [ ] Prototype의 복제 비용을 확인했는가?

## 연습 문제

1. `new Xxx()` 호출이 여러 곳에 흩어진 클래스를 골라 Factory로 모아 봅니다.
2. 인자가 일곱 개 이상인 생성자 하나를 Builder 형태로 바꿔 봅니다.
3. Singleton 클래스로 만든 구성 요소 하나를 모듈 수준 객체로 바꿀 수 있는지 검토해 봅니다.

## 정리 및 다음 글

생성 책임을 통제하면 결합이 느슨해집니다. 다음 글에서는 객체를 어떻게 엮어 더 큰 구조를 만들지에 집중하는 Structural 패턴으로 넘어가겠습니다.

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

## 실무 심화: 생성 책임과 조립 책임을 분리하는 운영 설계

Creational 패턴의 핵심은 "객체를 어디서 만들 것인가"를 결정하는 것입니다. 실무에서는 생성 규칙이 환경별로 다르고 비밀값 로딩, 연결 재시도, 모의 객체 주입이 함께 얽히기 때문에 생성 책임을 분리하지 않으면 테스트와 운영이 동시에 어려워집니다.

### 유엠엘 유사 다이어그램

```text
[Controller] --> [Service]
[Service] --> <<interface>> [Repository]
[RepositoryFactory] --creates--> [PostgresRepository]
[RepositoryFactory] --creates--> [MemoryRepository]
[Config] --> [RepositoryFactory]
```

서비스는 인터페이스만 알고, 구체 구현 선택은 팩토리가 담당하는 구조입니다.

### 변경 전후 리팩터링

```python
# 변경 전: 서비스가 생성 규칙을 직접 보유
class OrderService:
    def __init__(self, env: str) -> None:
        if env == "prod":
            self.repo = PostgresRepository(dsn="...")
        else:
            self.repo = MemoryRepository()
```

```python
# 변경 후: 생성 책임을 팩토리로 이동
from typing import Protocol

class OrderRepository(Protocol):
    def save(self, order_id: str) -> None: ...

class RepositoryFactory:
    @staticmethod
    def create(env: str) -> OrderRepository:
        if env == "prod":
            return PostgresRepository(dsn="...")
        return MemoryRepository()

class OrderService:
    def __init__(self, repo: OrderRepository) -> None:
        self.repo = repo
```

이후 서비스 테스트는 메모리 저장소를 직접 주입해 빠르게 수행할 수 있습니다.

### 장고/플라스크 적용 예시

- Django에서는 settings 기반으로 저장소/메시지 브로커 구현을 바꿀 때 앱 시작 시 팩토리 조립 계층을 둡니다.
- Flask에서는 application factory(`create_app`)에서 의존성 조립을 끝내고, 뷰 함수는 이미 주입된 서비스만 사용합니다.

### 솔리드 매핑

| 원칙 | Creational 패턴이 만드는 효과 |
| --- | --- |
| SRP | 서비스는 비즈니스, 팩토리는 생성 규칙 담당 |
| OCP | 신규 저장소 추가 시 기존 서비스 수정 최소화 |
| DIP | 고수준 모듈이 인터페이스에 의존 |

### 실전 운영 팁

1. 팩토리에 재시도 정책까지 넣지 말고 연결 생성 책임만 유지합니다.
2. Builder를 도입했다면 `build()` 직전에 검증 규칙을 명시해 불완전 객체 생성을 막습니다.
3. Singleton이 필요하더라도 수명 주기를 문서화해 테스트 격리를 깨지 않도록 관리합니다.

Creational 패턴은 객체를 "잘 만드는 기술"이 아니라 시스템을 "안전하게 바꾸는 기술"입니다.


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

- **Creational 패턴은 정확히 어떤 설계 문제를 풀까요?**
  - 본문의 기준은 Creational 패턴를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Factory Method와 Abstract Factory는 어디서 갈릴까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Builder는 언제 필요하고 언제 과할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Design Patterns 101 (1/10): 디자인 패턴이란 무엇인가?](./01-what-are-design-patterns.md)
- **Creational 패턴 (현재 글)**
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

- [Factory Method (refactoring.guru)](https://refactoring.guru/design-patterns/factory-method)
- [Abstract Factory (refactoring.guru)](https://refactoring.guru/design-patterns/abstract-factory)
- [Builder (refactoring.guru)](https://refactoring.guru/design-patterns/builder)

### 실무 확장 읽을거리

- [Singleton — Why You Should Use It Sparingly](https://martinfowler.com/bliki/InversionOfControl.html)
- [copy — Shallow and deep copy operations (Python docs)](https://docs.python.org/3/library/copy.html)

- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/ko)

Tags: Computer Science, DesignPatterns, Creational, Factory, Singleton, Builder
