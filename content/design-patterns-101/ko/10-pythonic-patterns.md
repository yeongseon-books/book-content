---
episode: 10
language: ko
last_reviewed: '2026-05-15'
seo_description: Python의 모듈, 함수, Protocol, 데코레이터로 GoF 패턴의 의도를 더 가볍게 표현하는 방법을 정리합니다.
series: design-patterns-101
status: publish-ready
tags:
- Computer Science
- DesignPatterns
- Python
- Idioms
- Protocols
- Decorators
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "디자인 패턴 101 (10/10): 파이썬에 어울리는 패턴"
---

# 디자인 패턴 101 (10/10): 파이썬에 어울리는 패턴

GoF 패턴을 처음 배우면 언어가 달라도 같은 구조를 그대로 옮기고 싶어집니다. 하지만 Python에서는 모듈, 일급 함수, Protocol, 데코레이터 같은 기본 도구만으로도 상당수 패턴을 더 짧고 읽기 쉬운 형태로 풀 수 있습니다.

이 글은 Design Patterns 101 시리즈의 마지막 글입니다.

이번 글에서는 GoF 패턴을 Python에 그대로 이식하는 대신, Python 언어 자체가 이미 제공하는 도구로 더 가볍게 표현하는 방법을 정리하겠습니다. 핵심은 패턴 이름보다 언어의 기본기를 먼저 믿는 것입니다.


![Design Patterns 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/10/10-01-concept-at-a-glance.ko.png)
*Design Patterns 101 10장 흐름 개요*

## 먼저 던지는 질문

- 왜 Python에서는 모듈이 이미 Singleton 역할을 할까요?
- Strategy와 Command를 함수로 표현하면 무엇이 좋아질까요?
- 인터페이스를 Protocol로 표현하는 이유는 무엇일까요?

## 왜 중요한가

Python은 모듈 로딩, 함수 전달, 구조적 타이핑, 데코레이터 문법처럼 많은 패턴을 언어 수준에서 지원합니다. 같은 문제를 Java식 클래스 계층으로 그대로 옮기면, Python 코드가 불필요하게 무거워지고 읽는 사람도 언어의 장점을 잃게 됩니다.

실무에서는 “패턴을 얼마나 충실히 재현했는가”보다 “언어에 맞게 얼마나 읽히게 풀었는가”가 더 중요합니다. Pythonic 설계는 패턴을 무시하는 태도가 아니라, 패턴의 의도를 Python다운 문법으로 번역하는 태도입니다.

## 한눈에 보는 개념

## 핵심 용어

- **Module-as-singleton**: 모듈은 한 번 로드되어 Singleton처럼 동작합니다.
- **First-class function**: 전달, 반환, 저장이 가능한 함수입니다.
- **Protocol**: 정적 검사까지 가능한 구조적 타이핑입니다.
- **Decorator (`@`)**: 함수나 클래스에 동작을 감싸 추가하는 문법입니다.
- **dataclass**: 값 객체에 필요한 동등성, repr, 불변성 표현을 쉽게 제공합니다.

## 변경 전후 비교

**Before (GoF as-is)**

```python
class SingletonConfig:
    _inst = None
    def __new__(cls):
        if cls._inst is None:
            cls._inst = super().__new__(cls)
        return cls._inst
```

**After (Pythonic)**

```python
# config.py
DEBUG = True
DB_URL = "postgres://..."
# elsewhere: from config import DEBUG, DB_URL
```

Python에서는 모듈이 이미 한 번만 로드됩니다. 굳이 Singleton 클래스를 재구현하는 순간 오히려 불필요한 복잡성이 생깁니다.

## 파이써닉 패턴을 익히는 5단계

### 1단계 — 모듈을 싱글턴처럼 씁니다

```python
# 1_module_singleton.py
# settings.py
import os
ENV = os.getenv("ENV", "dev")
SECRET = os.getenv("SECRET", "x")
```

어디서 import하든 같은 값을 공유합니다. Python에서는 이것만으로도 많은 Singleton 요구를 충분히 충족합니다.

### 2단계 — 전략와 커맨드를 함수로 표현합니다

```python
# 2_function_strategy.py
def asc(d): return sorted(d)
def desc(d): return sorted(d, reverse=True)

def run(strategy, data): return strategy(data)
print(run(desc, [3, 1, 2]))
```

명확성이 유지된다면 함수가 가장 자연스러운 Strategy입니다. 클래스를 만들지 않아도 역할과 교체 가능성이 충분히 살아납니다.

### 3단계 — 인터페이스는 프로토콜로 표현합니다

```python
# 3_protocol.py
from typing import Protocol

class Mailer(Protocol):
    def send(self, to: str, body: str) -> None: ...

class SmtpMailer:
    def send(self, to, body): ...   # satisfies without inheritance
```

상속 계층을 만들지 않고도 계약을 표현할 수 있다는 점이 중요합니다. 덕 타이핑의 유연성과 정적 검사의 안정성을 함께 가져갈 수 있습니다.

### 4단계 — 값 객체는 데이터클래스 데코레이터로 간단히 만듭니다

```python
# 4_dataclass.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    amount: int
    currency: str
```

값 객체에 필요한 비교, 표현, 불변성 설정을 짧은 문법으로 얻을 수 있습니다. Python에서 값 객체를 손으로 장황하게 만들 이유가 많이 줄어듭니다.

### 5단계 — 데코레이터 패턴은 `@` 문법으로 녹여 냅니다

```python
# 5_decorator.py
import time, functools

def timed(fn):
    @functools.wraps(fn)
    def wrap(*a, **k):
        t = time.time()
        try: return fn(*a, **k)
        finally: print(fn.__name__, time.time()-t)
    return wrap

@timed
def work(): time.sleep(0.1)
```

책에 나오는 Decorator 클래스를 그대로 옮기지 않아도 됩니다. Python은 이미 감싸기 구조를 언어 문법으로 제공하고 있습니다.

## 이 코드에서 주목할 점

- 클래스 계층이 거의 자라지 않습니다.
- 패턴의 의도가 언어 기본 도구 위에서 자연스럽게 드러납니다.
- 같은 목적을 더 적은 줄 수로 표현합니다.

## 자주 하는 실수 5가지

1. **Java식 GoF 구조를 그대로 옮기는 경우**: Python에 필요 없는 무게를 추가합니다.
2. **모듈이면 될 것을 Singleton 클래스로 만드는 경우**: 두 번째 인스턴스 가능성까지 열어 둡니다.
3. **Protocol로 충분한데 ABC를 강제하는 경우**: 불필요한 상속 구조가 생깁니다.
4. **데코레이터를 과하게 겹치고 `functools.wraps`를 빼먹는 경우**: 호출 흐름과 메타데이터가 흐려집니다.
5. **값 객체를 손코딩하는 경우**: `__eq__`, `__repr__` 같은 기본 기능을 놓치기 쉽습니다.

## 실무에서는 이렇게 드러납니다

`logging` 모듈은 모듈 Singleton처럼 읽히고, `sorted(key=...)`는 함수 Strategy이며, `typing.Protocol`은 인터페이스 역할을 하고, `@app.route(...)`는 Decorator의 일상적인 예입니다. Python 표준 라이브러리와 주요 프레임워크 자체가 Pythonic 패턴의 살아 있는 예시입니다.

## 빠르게 검증해 보기

Pythonic 표현이 더 나은지 아래 기준으로 비교해 보세요.

- 모듈, 함수, Protocol, 데코레이터, dataclass 중 이미 같은 의도를 담을 수 있는 도구가 있는지 먼저 봅니다.
- 교과서식 GoF 구조와 Python다운 표현을 나란히 두고 줄 수와 가독성을 비교합니다.
- 더 가벼운 표현이 필요한 확장 지점까지 그대로 남겨 두는지 확인합니다.

**기대 결과:** Python다운 형태가 패턴의 의도는 유지하면서도 상속, 클래스 수, 보일러플레이트를 눈에 띄게 줄여야 합니다.

## 시니어 엔지니어는 이렇게 판단합니다

- 패턴보다 언어 도구를 먼저 봅니다.
- Singleton 클래스보다 모듈, ABC보다 Protocol을 먼저 떠올립니다.
- 함수로 충분하면 클래스를 만들지 않습니다.
- 데코레이터에는 항상 `functools.wraps`를 붙입니다.
- 결국 패턴은 가독성을 위해 존재한다고 봅니다.

## 체크리스트

- [ ] 모듈이면 충분한데 Singleton 클래스를 만들지 않았는가?
- [ ] 함수로 충분한데 Strategy 클래스를 만들지 않았는가?
- [ ] Protocol로 충분한데 ABC를 강제하지 않았는가?
- [ ] 값 객체에 `dataclass`를 활용했는가?
- [ ] 데코레이터에 `functools.wraps`를 사용했는가?

## 연습 문제

1. Singleton 클래스를 하나 골라 모듈 기반 구성으로 접어 봅니다.
2. Strategy 클래스를 하나 함수 기반으로 단순화해 봅니다.
3. ABC 기반 인터페이스 하나를 Protocol로 바꾸고 정적 타입 검사까지 통과시켜 봅니다.

## 정리 및 다음 글

GoF 패턴은 어휘이지 매뉴얼이 아닙니다. Python에서는 언어가 이미 많은 패턴을 더 가볍게 표현할 수 있게 도와줍니다. Design Patterns 101 시리즈는 여기서 마무리하겠습니다. 앞으로는 패턴 이름을 구현 강박이 아니라 사고 단위로 사용해 보시기 바랍니다.

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

## 실무 케이스 스터디: 장고/플라스크에서 패턴 선택 기준

패턴 선택은 프레임워크보다 요구사항의 변화 양상에 의해 결정됩니다. 다음 기준은 두 프레임워크에서 공통으로 유효합니다.

### 판단 기준 표

| 질문 | 선택 기준 | 권장 패턴 |
| --- | --- | --- |
| 조건 분기가 월 단위로 늘어나는가 | 정책 확장이 핵심 | Strategy |
| 외부 API 계약이 자주 바뀌는가 | 경계 안정화가 핵심 | Adapter |
| 객체 조립 단계가 많고 옵션이 많은가 | 생성 과정을 명시화 | Builder/Factory |
| 이벤트 수신자가 유동적인가 | 발행/구독 분리 | Observer |

### 파이썬 구현 앵커

```python
from dataclasses import dataclass
from typing import Protocol

class Sender(Protocol):
    def send(self, msg: str) -> None: ...

@dataclass
class SlackSender:
    webhook: str

    def send(self, msg: str) -> None:
        # requests.post(self.webhook, json={"text": msg})
        pass

class SenderAdapter:
    def __init__(self, sender: Sender) -> None:
        self.sender = sender

    def notify(self, message: str) -> None:
        self.sender.send(message)
```

### 유엠엘 유사 구조

```text
[UseCase] --> [Notifier]
[Notifier] --> <<interface>> [Sender]
[SlackSender] --implements--> [Sender]
[SenderAdapter] --wraps--> [Sender]
```

### 변경 전후 비교

- 변경 전: 라우트/서비스 내부에서 외부 SDK를 직접 호출해 테스트와 교체 비용이 큽니다.
- 변경 후: 인터페이스 경계를 두고 패턴을 적용해 변경이 한 계층에서 끝납니다.

### 솔리드 점검표

| 원칙 | 점검 질문 |
| --- | --- |
| SRP | 클래스가 생성/정책/전송을 동시에 담당하지 않는가 |
| OCP | 새 요구를 기존 코드 수정 없이 추가할 수 있는가 |
| LSP | 대체 구현이 같은 계약을 유지하는가 |
| ISP | 과도하게 큰 인터페이스를 강요하지 않는가 |
| DIP | 상위 계층이 구체 구현 대신 추상에 의존하는가 |

이 점검표를 PR 템플릿에 넣으면 패턴 적용 품질이 팀 단위로 안정됩니다.


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


## 추가 검증 메모: 리팩터링 품질을 수치로 확인하기

패턴 리팩터링은 체감만으로 평가하면 흔들리기 쉽습니다. 아래 지표를 배포 전후로 비교하면 패턴 도입 효과를 더 객관적으로 확인할 수 있습니다.

- 변경 파일 수: 신규 요구 1건당 수정 파일 수가 줄어드는지 확인합니다.
- 테스트 시간: 단위 테스트 비중이 늘어 통합 테스트 의존이 줄어드는지 봅니다.
- 장애 복구 시간: 로그만으로 실패 계층을 특정하는 시간이 단축되는지 측정합니다.

```text
평가 주기: 2주
지표 1: 평균 PR 수정 파일 수
지표 2: 테스트 실패 원인 분류 가능 비율
지표 3: 회귀 버그 재발률
```

이 지표가 개선되지 않는다면 패턴 자체가 아니라 경계 설정 또는 인터페이스 설계가 잘못되었을 가능성이 큽니다. 이 경우 패턴을 더 추가하기보다 책임 분리 기준을 먼저 재정의하는 편이 안전합니다.


## 처음 질문으로 돌아가기

- **왜 Python에서는 모듈이 이미 Singleton 역할을 할까요?**
  - 본문의 기준은 Python에 어울리는 패턴를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Strategy와 Command를 함수로 표현하면 무엇이 좋아질까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **인터페이스를 Protocol로 표현하는 이유는 무엇일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Design Patterns 101 (1/10): 디자인 패턴이란 무엇인가?](./01-what-are-design-patterns.md)
- [Design Patterns 101 (2/10): Creational 패턴](./02-creational-patterns.md)
- [Design Patterns 101 (3/10): Structural 패턴](./03-structural-patterns.md)
- [Design Patterns 101 (4/10): Behavioral 패턴](./04-behavioral-patterns.md)
- [Design Patterns 101 (5/10): Strategy 패턴](./05-strategy-pattern.md)
- [Design Patterns 101 (6/10): Adapter 패턴](./06-adapter-pattern.md)
- [Design Patterns 101 (7/10): Observer 패턴](./07-observer-pattern.md)
- [Design Patterns 101 (8/10): Factory와 의존성 주입](./08-factory-and-di.md)
- [Design Patterns 101 (9/10): 패턴을 남용하지 않는 법](./09-avoiding-pattern-overuse.md)
- **Python에 어울리는 패턴 (현재 글)**

<!-- toc:end -->

## 참고 자료

### 핵심 자료

- [PEP 544 — Protocols](https://peps.python.org/pep-0544/)
- [dataclasses (Python docs)](https://docs.python.org/3/library/dataclasses.html)
- [functools.wraps (Python docs)](https://docs.python.org/3/library/functools.html#functools.wraps)

### 실무 확장 읽을거리

- [Python 3 Patterns, Recipes and Idioms (Bruce Eckel)](https://python-3-patterns-idioms-test.readthedocs.io/)
- [PEP 20 — The Zen of Python](https://peps.python.org/pep-0020/)

- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/ko)

Tags: Computer Science, DesignPatterns, Python, Idioms, Protocols, Decorators
