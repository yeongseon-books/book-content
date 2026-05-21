---
series: design-patterns-101
episode: 9
title: "Design Patterns 101 (9/10): 패턴을 남용하지 않는 법"
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
  - Antipatterns
  - Simplicity
  - YAGNI
  - Refactoring
seo_description: 패턴 남용을 피하고 반복되는 변화가 생겼을 때만 추상화를 올리는 실무적 기준을 설명합니다.
last_reviewed: '2026-05-15'
---

# Design Patterns 101 (9/10): 패턴을 남용하지 않는 법

디자인 패턴을 배우고 나면 한동안은 세상이 전부 패턴 후보로 보입니다. 작은 함수도 Strategy로 보이고, 단순한 생성도 Factory로 보이며, 래퍼 하나에도 Decorator라는 이름을 붙이고 싶어집니다. 문제는 이 열정이 종종 미래 요구사항을 상상한 추상화로 이어진다는 점입니다.

이 글은 Design Patterns 101 시리즈의 9번째 글입니다.

이번 글에서는 패턴을 잘 아는 것과 패턴을 잘 쓰는 것이 왜 다른지 정리하겠습니다. 핵심은 패턴이 문제를 부르는 것이 아니라, 반복되는 문제가 패턴을 불러야 한다는 사실입니다.

## 먼저 던지는 질문

- 좋은 패턴이 어떻게 나쁜 코드로 바뀔까요?
- 단순한 대안은 왜 종종 더 강할까요?
- YAGNI는 패턴 선택과 어떤 관계가 있을까요?

## 큰 그림

![Design Patterns 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/09/09-01-concept-at-a-glance.ko.png)

*Design Patterns 101 9장 흐름 개요*

## 왜 중요한가

미리 적용한 패턴은 쉽게 잘못 적용한 패턴이 됩니다. 아직 변화가 한 번도 반복되지 않았는데 구조부터 일반화하면, 시스템은 미래를 대비한다는 명분 아래 현재의 단순함을 잃습니다.

반대로 단순한 코드에서 시작해 반복되는 변화가 정말 생겼을 때 패턴으로 끌어올리면, 추상화의 근거를 실제 코드에서 찾을 수 있습니다. 이 차이가 패턴을 설계 도구로 쓰는 팀과 장식으로 쓰는 팀을 가릅니다.

## 한눈에 보는 개념

## 핵심 용어

- **YAGNI**: 지금 당장 필요하지 않다면 아직 만들지 않는다는 원칙입니다.
- **Premature abstraction**: 너무 이른 시점의 추상화입니다.
- **Pattern fever**: 모든 코드를 패턴으로 환원하고 싶어지는 상태입니다.
- **Cargo cult**: 모양만 흉내 내고 문제와 이유를 놓치는 태도입니다.
- **Refactor to pattern**: 단순한 코드를 다듬는 과정에서 패턴이 자연스럽게 드러나는 접근입니다.

## Before / After

**Before (overdone)**

```python
# Just one algorithm — but Strategy plus Factory plus Builder
class GreetStrategy: ...
class HelloStrategy(GreetStrategy): ...
class GreetFactory: ...
class GreetBuilder: ...
```

**After (simple)**

```python
def greet(name): return f"Hello, {name}"
```

지금 존재하는 요구사항이 한 줄이라면, 그 한 줄이 가장 정확한 설계일 수 있습니다. 추상화는 요구가 생긴 뒤에 올려도 늦지 않습니다.

## 패턴 남용을 피하는 5단계

### 1단계 — 가장 단순한 코드에서 시작합니다

```python
# 1_simple.py
def discount(price, kind):
    return {"vip": price*0.7, "member": price*0.9}.get(kind, price)
```

분기 하나짜리 코드에 패턴부터 들이대면 거의 항상 과합니다. 단순함은 나중에 얻기 어려운 장점이므로 시작점부터 잃지 않는 편이 좋습니다.

### 2단계 — 변화가 반복될 때만 추상화합니다

```python
# 2_when_repeats.py
# When tiers grow past six and per-tier policy starts diverging — then Strategy.
class Discount: ...
```

세 번째 변화쯤에서야 추상화가 값을 하기 시작하는 경우가 많습니다. 반복되지 않은 미래 요구를 위해 현재 코드를 비틀 필요는 없습니다.

### 3단계 — 먼저 함수 추출로 의도를 드러냅니다

```python
# 3_extract.py
def vip_price(p): return p * 0.7
def member_price(p): return p * 0.9
```

이름 있는 함수만으로도 충분히 많은 의도를 표현할 수 있습니다. 클래스 계층을 올리기 전에 함수 분리만으로 해결되는지 먼저 보는 습관이 중요합니다.

### 4단계 — 리팩터링 과정에서 패턴을 발견합니다

```python
# 4_refactor_to_pattern.py
# When five branches grow into the same shape, *then* lift to Strategy.
```

같은 형태의 분기가 정말 반복된다면 그때 패턴 이름이 붙습니다. 패턴은 계획서의 첫 줄보다 리팩터링의 결과로 나오는 편이 더 건강합니다.

### 5단계 — 필요 없어지면 패턴도 지웁니다

```python
# 5_remove_pattern.py
# If only one usage remains, fold the Strategy/Factory back into a function.
```

한때 맞았던 추상화가 지금도 맞는다고 보장할 수는 없습니다. 사용처가 줄었다면 오히려 다시 접어 넣는 편이 더 좋은 설계일 수 있습니다.

## 이 코드에서 주목할 점

- 가장 강한 시작점은 대개 단순한 함수입니다.
- 패턴은 반복되는 변화가 생겼을 때 정당화됩니다.
- 추상화는 한 번 더 미뤄도 되는 경우가 많습니다.

## 자주 하는 실수 5가지

1. **요구보다 추상화가 먼저 달리는 경우**: 상상한 미래를 위해 현재 코드를 복잡하게 만듭니다.
2. **이름만 패턴인 경우**: `XxxFactory`가 사실상 `new` 한 번 감싼 수준입니다.
3. **Strategy 안에 다시 if/elif가 있는 경우**: 패턴이 분기를 흡수하지 못했습니다.
4. **Decorator를 끝없이 겹치는 경우**: 디버깅이 악몽이 됩니다.
5. **DI 컨테이너가 모든 배선을 자동으로 처리하는 경우**: 보이지 않는 의존성이 쌓입니다.

## 실무에서는 이렇게 드러납니다

좋은 라이브러리는 패턴을 많이 쓰는 대신 정확하게 씁니다. requests, FastAPI, pytest 같은 도구를 보면 어렵지 않은 조합으로 큰 문제를 해결합니다. 주니어와 시니어의 차이는 패턴 이름을 많이 아느냐보다, 언제 기다려야 하는지 아느냐에 더 가깝습니다.

## 빠르게 검증해 보기

새 추상화가 과한지 의심되면 아래를 먼저 확인해 보세요.

- 그 변화가 실제 코드에서 반복되었는지, 아니면 설계 회의 안에서만 예상되는지 구분합니다.
- 함수 추출이나 작은 모듈 분리만으로 의도가 충분히 드러나는지 시험해 봅니다.
- 패턴을 빼면 당장 어떤 구체적 고통이 돌아오는지 적어 봅니다.

**기대 결과:** 고통이 아직 가정에 머문다면, 지금은 단순한 코드가 더 좋은 설계일 가능성이 큽니다.

## 시니어 엔지니어는 이렇게 판단합니다

- 함수에서 시작합니다.
- 변화가 반복될 때만 추상화합니다.
- 패턴 이름은 계획이 아니라 결과라고 봅니다.
- 쓰이지 않는 추상화는 지웁니다.
- 코드 리뷰에서 “왜 이 패턴인가?”를 끝까지 묻습니다.

## 체크리스트

- [ ] 이 추상화가 지금 정말 필요한가?
- [ ] 변화가 세 번 이상 반복되었는가?
- [ ] 함수 추출만으로 충분하지 않은가?
- [ ] 패턴 이름이 역할을 정확히 설명하는가?
- [ ] 사용처가 하나로 줄면 다시 접어 넣을 수 있는가?

## 연습 문제

1. 코드베이스에서 과하게 추상화된 지점 하나를 골라 단순 함수로 되돌려 봅니다.
2. 최근 변경 빈도를 세어 보고 추상화 후보와 단순 유지 대상을 나눠 봅니다.
3. PR 리뷰 체크리스트에 “왜 이 패턴인가?” 질문을 추가해 봅니다.

## 정리 및 다음 글

패턴은 어휘이지 정답이 아닙니다. 마지막 글에서는 Python의 함수, 모듈, Protocol 같은 언어 도구가 많은 GoF 패턴을 어떻게 더 가볍게 녹여 내는지 살펴보겠습니다.

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

## 처음 질문으로 돌아가기

- **좋은 패턴이 어떻게 나쁜 코드로 바뀔까요?**
  - 본문의 기준은 패턴을 남용하지 않는 법를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **단순한 대안은 왜 종종 더 강할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **YAGNI는 패턴 선택과 어떤 관계가 있을까요?**
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
- **패턴을 남용하지 않는 법 (현재 글)**
- Python에 어울리는 패턴 (예정)

<!-- toc:end -->

## 참고 자료

### 핵심 자료

- [YAGNI (Martin Fowler)](https://martinfowler.com/bliki/Yagni.html)
- [Refactoring to Patterns (Joshua Kerievsky)](https://www.industriallogic.com/xp/refactoring/)
- [Premature Abstraction (C2 wiki)](https://wiki.c2.com/?PrematureGeneralization)

### 실무 확장 읽을거리

- [Worse Is Better (Richard Gabriel)](https://www.dreamsongs.com/RiseOfWorseIsBetter.html)
- [PEP 20 — The Zen of Python](https://peps.python.org/pep-0020/)

Tags: Computer Science, DesignPatterns, Antipatterns, Simplicity, YAGNI, Refactoring
