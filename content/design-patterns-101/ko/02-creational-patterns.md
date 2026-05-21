---
series: design-patterns-101
episode: 2
title: "Design Patterns 101 (2/10): Creational 패턴"
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

# Design Patterns 101 (2/10): Creational 패턴

코드를 읽다 보면 객체를 쓰는 코드보다 객체를 만드는 코드가 더 눈에 띄는 순간이 있습니다. `new SomeService()`가 도메인 곳곳에 흩어지고, 환경에 따라 다른 구현을 골라야 하고, 생성 인자가 계속 늘어나기 시작할 때입니다. 이 시점부터 문제는 기능보다 생성 책임의 위치로 옮겨갑니다.

이 글은 Design Patterns 101 시리즈의 2번째 글입니다.

이번 글에서는 Creational 패턴을 “객체를 멋지게 만드는 기법”이 아니라, 생성 책임을 한곳에 모아 결합도를 낮추는 설계 도구로 보겠습니다. 무엇을 만들지보다, 누가 만들고 어디서 조립하는지가 더 중요합니다.

## 먼저 던지는 질문

- Creational 패턴은 정확히 어떤 설계 문제를 풀까요?
- Factory Method와 Abstract Factory는 어디서 갈릴까요?
- Builder는 언제 필요하고 언제 과할까요?

## 큰 그림

![Design Patterns 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/02/02-01-concept-at-a-glance.ko.png)

*Design Patterns 101 2장 흐름 개요*

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

## Before / After

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

## Creational 패턴을 익히는 5단계

### 1단계 — Factory Method로 분기를 한곳에 모읍니다

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

### 2단계 — Abstract Factory로 관련 객체를 함께 만듭니다

```python
# 2_abstract_factory.py
class UIFactory:
    def button(self) -> "Button": ...
    def textbox(self) -> "TextBox": ...

class MacFactory(UIFactory): ...
class WinFactory(UIFactory): ...
```

Mac용 버튼과 Mac용 텍스트박스처럼 같이 움직여야 하는 객체군이 있다면, 가족 단위 생성이 더 안전합니다. 조합이 뒤섞이는 실수를 줄일 수 있기 때문입니다.

### 3단계 — Builder로 복잡한 조립을 읽히게 만듭니다

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

### 4단계 — Singleton은 마지막 수단으로 다룹니다

```python
# 4_singleton.py
# In Python, the module itself is usually a singleton.
# A dedicated class is rarely necessary.
import logging
logger = logging.getLogger("app")
```

Singleton은 가장 쉽게 남용되는 Creational 패턴입니다. 인스턴스를 하나로 제한하는 순간 전역 상태와 수명 주기 문제가 따라오기 때문입니다. Python에서는 모듈 수준 객체로 충분한 경우가 많습니다.

### 5단계 — Prototype으로 복제가 더 싼 상황을 다룹니다

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

### 2) UML 유사 텍스트 다이어그램

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

Tags: Computer Science, DesignPatterns, Creational, Factory, Singleton, Builder
