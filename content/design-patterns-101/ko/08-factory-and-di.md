---
series: design-patterns-101
episode: 8
title: "디자인 패턴 101 (8/10): 팩토리와 의존성 주입"
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
  - Factory
  - DependencyInjection
  - Composition
  - IoC
seo_description: Factory와 의존성 주입으로 객체 조립과 사용을 분리해 테스트성과 교체 가능성을 높이는 방법을 설명합니다.
last_reviewed: '2026-05-15'
---

# 디자인 패턴 101 (8/10): 팩토리와 의존성 주입

객체를 잘 만들고 잘 조합하는 문제는 결국 한 질문으로 모입니다. “이 객체는 누가 만들고, 어디서 연결하고, 누가 넘겨줘야 하는가?” 도메인 코드가 스스로 의존성을 만들기 시작하면 생성 책임과 사용 책임이 섞이고, 테스트와 교체가 급격히 어려워집니다.

이 글은 Design Patterns 101 시리즈의 8번째 글입니다.

이번 글에서는 Factory와 Dependency Injection을 함께 보겠습니다. 핵심은 조립은 바깥 한곳에서 하고, 도메인은 주어진 의존성을 사용만 하게 만드는 것입니다. 그 조립 지점을 Composition Root라고 부릅니다.

## 먼저 던지는 질문

- 생성 책임이 흩어져 있으면 왜 변경 비용이 커질까요?
- Factory는 어떤 생성 분기를 캡슐화할까요?
- Dependency Injection은 어떤 사고방식을 요구할까요?

## 큰 그림

![Design Patterns 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/08/08-01-concept-at-a-glance.ko.png)

*Design Patterns 101 8장 흐름 개요*

## 왜 중요한가

도메인 객체가 자신의 의존성을 직접 만들면, 도메인은 기능뿐 아니라 생성 방식과 환경 차이까지 알게 됩니다. 이 순간부터 테스트는 실제 인프라를 더 많이 끌고 오게 되고, 운영 환경에 따라 다른 구현을 선택하는 분기도 도메인 안에 스며듭니다.

Factory와 DI는 이 문제를 끊어 냅니다. 도메인은 “무엇을 쓸지”만 알고, “어떻게 만들지”는 바깥으로 밀어냅니다. 그 결과 테스트에서는 가짜 객체를 쉽게 넣을 수 있고, 운영에서는 환경별 구현을 한곳에서 관리할 수 있습니다.

## 한눈에 보는 개념

## 핵심 용어

- **Factory**: 생성 과정을 감싸는 함수나 객체입니다.
- **Dependency Injection**: 의존성을 외부에서 제공하는 방식입니다.
- **Composition Root**: 객체 그래프를 한 번에 연결하는 단일 진입점입니다.
- **Constructor injection**: `__init__`를 통해 의존성을 받는 방식입니다.
- **DI container**: 자동 배선을 돕는 도구이며, 필요할 때만 써야 합니다.

## 변경 전후 비교

**Before**

```python
class OrderService:
    def __init__(self):
        self.repo = PostgresOrderRepo("dsn")
        self.mailer = SmtpMailer("smtp.example.com")
        self.bus = EventBus()
```

**After**

```python
class OrderService:
    def __init__(self, repo, mailer, bus):
        self.repo, self.mailer, self.bus = repo, mailer, bus
```

`OrderService`는 더 이상 협력자를 스스로 고르지 않습니다. 덕분에 테스트, 환경별 교체, 수명 주기 관리가 훨씬 쉬워집니다.

## 팩토리와 의존성 주입를 익히는 5단계

### 1단계 — 생성 분기를 팩토리로 뺍니다

```python
# 1_factory.py
def make_mailer(env):
    if env == "prod":
        return SmtpMailer("smtp.example.com")
    return InMemoryMailer()
```

환경 분기를 도메인 바깥으로 끌어내는 첫 단계입니다. 생성 차이를 한곳에 모으면 읽기도 쉽고 변경도 안전합니다.

### 2단계 — 생성자 주입으로 도메인을 단순화합니다

```python
# 2_ctor.py
class OrderService:
    def __init__(self, repo, mailer):
        self.repo, self.mailer = repo, mailer
```

도메인은 받은 협력자를 사용하기만 합니다. 이 단순한 차이가 테스트성과 교체 가능성에 큰 영향을 줍니다.

### 3단계 — 구성 루트를 한곳에 둡니다

```python
# 3_main.py
def main():
    repo = PostgresOrderRepo(os.environ["DSN"])
    mailer = make_mailer(os.environ["ENV"])
    service = OrderService(repo, mailer)
    service.run()

if __name__ == "__main__":
    main()
```

`main`이나 부트스트랩 함수처럼 한곳에서 객체 그래프를 연결하면, 시스템 조립 방식을 읽는 비용이 크게 줄어듭니다.

### 4단계 — 테스트는 직접 조립하게 둡니다

```python
# 4_test.py
def test_submit():
    repo = InMemoryOrderRepo()
    mailer = InMemoryMailer()
    svc = OrderService(repo, mailer)
    svc.submit(...)
    assert mailer.sent == 1
```

테스트는 `main`을 우회하고 필요한 가짜 객체를 직접 조립하면 됩니다. 좋은 DI 설계는 테스트가 가장 먼저 편해집니다.

### 5단계 — 의존성 주입 컨테이너는 정말 필요할 때만 씁니다

```python
# 5_container.py
# A tiny hand-rolled container — only when truly needed.
class Container:
    def __init__(self): self._reg = {}
    def register(self, key, factory): self._reg[key] = factory
    def get(self, key): return self._reg[key]()
```

프로젝트 규모가 작다면 수동 배선이 훨씬 읽기 쉽습니다. 컨테이너는 편의 도구이지, 설계 문제를 가려 주는 마법이 아닙니다.

## 이 코드에서 주목할 점

- 도메인은 의존성을 받기만 합니다.
- 환경 차이는 Composition Root의 단일 분기로 모입니다.
- 테스트는 가짜 객체를 직접 만들어 주입합니다.

## 자주 하는 실수 5가지

1. **도메인 코드가 환경 변수를 직접 읽는 경우**: 조립 책임이 안으로 샙니다.
2. **Factory 안에 비즈니스 정책을 넣는 경우**: 생성과 규칙이 섞입니다.
3. **DI 컨테이너를 과하게 쓰는 경우**: 보이지 않는 마법이 디버깅 비용을 키웁니다.
4. **순환 의존성을 컨테이너로 우회하는 경우**: 설계 문제를 숨길 뿐입니다.
5. **컨테이너 자체를 everywhere 주입하는 경우**: 단순한 구조를 불필요하게 무겁게 만듭니다.

## 실무에서는 이렇게 드러납니다

FastAPI의 `Depends`, Spring의 `@Autowired`, Django 설정 기반 백엔드 선택, 마이크로서비스 부트스트랩 코드는 모두 DI와 Factory의 변형입니다. 대규모 시스템일수록 “객체를 누가 만들었는가”를 읽어내는 능력이 중요해집니다.

## 빠르게 검증해 보기

조립이 정말 도메인 밖에 있는지 아래 항목으로 확인해 보세요.

- 도메인 서비스 안에서 환경 변수 읽기, SDK 생성, 인프라 import가 남아 있는지 찾습니다.
- 테스트 하나를 골라 InMemory 협력자만으로 서비스를 직접 조립해 봅니다.
- 운영/테스트 배선 차이가 Composition Root 한곳에만 있는지 확인합니다.

**기대 결과:** 애플리케이션 서비스는 테스트에서 쉽게 인스턴스화되고, 환경별 선택은 부트스트랩 경계에만 남아 있어야 합니다.

## 시니어 엔지니어는 이렇게 판단합니다

- 항상 “이 객체는 누가 만드는가?”를 먼저 묻습니다.
- 조립은 바깥에 두고 사용은 안에 둡니다.
- 컨테이너는 실제 규모가 생긴 뒤에만 도입합니다.
- 환경 차이는 Composition Root로 모읍니다.
- Factory는 생성만 하고 정책 판단은 도메인에 둡니다.

## 체크리스트

- [ ] 도메인이 환경 변수를 직접 읽지 않는가?
- [ ] Composition Root가 한곳에 모여 있는가?
- [ ] Factory가 정책 판단까지 품고 있지 않은가?
- [ ] 컨테이너가 정말 필요한가?
- [ ] 테스트가 객체를 직접 조립할 수 있는가?

## 연습 문제

1. 환경에 따라 다른 Mailer를 반환하는 Factory를 작성해 봅니다.
2. `OrderService`를 생성자 주입 형태로 바꾸고 테스트를 추가해 봅니다.
3. DB, mailer, event bus를 Composition Root 하나에서 연결해 봅니다.

## 정리 및 다음 글

Factory와 DI는 조립과 사용을 분리합니다. 다음 글에서는 패턴 자체가 언제 비용이 되기 시작하는지, 패턴 남용을 피하는 법을 살펴보겠습니다.

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


## 처음 질문으로 돌아가기

- **생성 책임이 흩어져 있으면 왜 변경 비용이 커질까요?**
  - 본문의 기준은 Factory와 의존성 주입를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Factory는 어떤 생성 분기를 캡슐화할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Dependency Injection은 어떤 사고방식을 요구할까요?**
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
- **Factory와 의존성 주입 (현재 글)**
- 패턴을 남용하지 않는 법 (예정)
- Python에 어울리는 패턴 (예정)

<!-- toc:end -->

## 참고 자료

### 핵심 자료

- [Factory Method (refactoring.guru)](https://refactoring.guru/design-patterns/factory-method)
- [Inversion of Control Containers and the Dependency Injection pattern (Martin Fowler)](https://martinfowler.com/articles/injection.html)
- [Composition Root (Mark Seemann)](https://blog.ploeh.dk/2011/07/28/CompositionRoot/)

### 실무 확장 읽을거리

- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Dependency Injector providers overview](https://python-dependency-injector.ets-labs.org/providers/index.html)

- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/ko)

Tags: Computer Science, DesignPatterns, Factory, DependencyInjection, Composition, IoC
