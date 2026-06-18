---
series: design-patterns-101
episode: 5
title: "바이브코딩을 위한 디자인 패턴 기초 (5/10): 전략 패턴"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - DesignPatterns
  - Strategy
  - Polymorphism
  - Behavioral
  - AI코딩
seo_description: AI가 생성한 if/elif 분기를 Strategy 패턴으로 교체하고, Python에서 가볍게 구현하는 바이브코딩 실전 가이드입니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 디자인 패턴 기초 (5/10): 전략 패턴

**바이브코딩을 위한 디자인 패턴 기초** 시리즈의 다섯 번째 글입니다. 이 시리즈는 AI와 함께 코딩할 때 디자인 패턴을 어떻게 읽고 활용할지를 다룹니다.

AI에게 "결제 수단별로 다른 처리를 해줘"라고 하면 거의 항상 `if/elif` 분기가 나옵니다. 처음에는 괜찮습니다. 그런데 결제 수단이 늘어나면서 같은 분기가 코드 여러 곳에 복제됩니다. Strategy 패턴을 알면 AI에게 정확히 어떤 구조를 요청해야 하는지 알 수 있습니다.

---

4장에서 Behavioral 패턴을 훑을 때 Strategy를 "알고리즘을 교체 가능하게 분리하는 패턴"으로 소개했습니다. 한 줄 요약으로는 충분하지만, 실무에서 Strategy를 적용하려고 하면 금방 질문이 쏟아집니다. 이 분기가 정말 Strategy 후보인지, 클래스로 만들어야 하는지 함수면 되는지, 기본 전략은 어떻게 두는지, 런타임에 바꿔도 안전한지.

바이브코딩 맥락에서는 한 가지가 더 추가됩니다. AI가 만들어 준 Strategy 구조를 어떻게 읽고 확장해야 하는지, 그리고 AI에게 어떻게 요청하면 원하는 Strategy 구조를 정확하게 받을 수 있는지.

> "Strategy 패턴은 알고리즘마다 분기되던 if/elif 체인을 교체 가능한 객체로 바꿉니다. AI에게 '새 배송업체 추가해줘'라고 하면 어디에 무엇을 넣어야 하는지 바로 알 수 있게 됩니다."

## 이 글에서 다룰 문제

- 모든 if/elif 분기가 Strategy 후보일까요, 아니면 특정 조건을 만족해야 할까요?
- AI가 만든 Strategy 코드에서 클래스 방식과 함수 방식을 어떻게 구분할까요?
- Strategy를 런타임에 교체하면 어떤 운영상 이점이 생길까요?
- 바이브코딩에서 Strategy를 잘못 적용하면 어떤 문제가 생길까요?
- 처음 배우는 사람이 가장 자주 놓치는 포인트는 무엇일까요?

## 이 분기가 Strategy 후보인지 가려내는 세 가지 조건

모든 `if/elif`가 Strategy 후보는 아닙니다. 세 가지 조건을 동시에 만족하는지 먼저 확인하세요.

**첫째, 분기마다 알고리즘이 독립적인가.** 각 분기가 같은 입력을 받아 같은 형태의 출력을 내지만, 내부 계산 방식이 다른 경우입니다.

**둘째, 분기가 앞으로 늘어날 가능성이 높은가.** 결제 수단, 배송 업체, 할인 정책처럼 비즈니스 요구에 따라 옵션이 추가되는 축이라면 Strategy 후보입니다.

**셋째, 호출부가 알고리즘 선택 책임에서 벗어나야 하는가.** 호출부가 "어떤 알고리즘을 쓸지"를 직접 결정하는 게 자연스러운 경우도 있습니다. Strategy가 빛나는 건 선택을 외부(설정, 사용자 입력, 런타임 조건)에 위임하고 싶을 때입니다.

## Python에서 Strategy를 표현하는 세 가지 방식

### 방식 1: Protocol 기반 클래스 (상태가 필요할 때)

```python
from typing import Protocol
from dataclasses import dataclass

class PricingStrategy(Protocol):
    def calculate(self, base_price: int, quantity: int) -> int: ...

@dataclass
class BulkPricing:
    threshold: int = 10
    discount_rate: float = 0.15

    def calculate(self, base_price: int, quantity: int) -> int:
        if quantity >= self.threshold:
            return int(base_price * quantity * (1 - self.discount_rate))
        return base_price * quantity
```

AI가 이 구조를 만들어 줬다면 새 할인 정책은 새 클래스를 하나 추가하면 됩니다.

### 방식 2: 함수 (상태가 없을 때)

```python
from typing import Callable

PricingFn = Callable[[int, int], int]

def standard_pricing(base_price: int, quantity: int) -> int:
    return base_price * quantity

def vip_pricing(base_price: int, quantity: int) -> int:
    return int(base_price * quantity * 0.7)
```

함수 Strategy는 상태가 없거나 클로저로 충분할 때 씁니다. AI에게 "함수형으로 Strategy 패턴 구현해줘"라고 하면 이 방식으로 나옵니다.

### 방식 3: dict 레지스트리 (문자열 키로 선택할 때)

```python
PRICING_STRATEGIES: dict[str, PricingFn] = {
    "standard": standard_pricing,
    "vip": vip_pricing,
    "summer_sale": lambda base, qty: int(base * qty * 0.8),
}

def calculate_price(tier: str, base_price: int, quantity: int) -> int:
    strategy = PRICING_STRATEGIES.get(tier)
    if strategy is None:
        raise ValueError(f"Unknown pricing tier: {tier}")
    return strategy(base_price, quantity)
```

API 요청의 파라미터, 설정 파일의 값처럼 외부에서 문자열로 들어오는 선택지를 Strategy로 연결할 때 씁니다.

## Before / After: OCP를 만족하는 코드로

**Before — 새 배송업체마다 기존 함수를 수정:**

```python
class ShippingCalculator:
    def cost(self, carrier: str, weight_kg: float) -> int:
        if carrier == "standard":
            return int(3000 + 500 * weight_kg)
        elif carrier == "express":
            return int(6000 + 800 * weight_kg)
        elif carrier == "same_day":
            return int(15000 + 1200 * weight_kg)
        raise ValueError(f"Unknown carrier: {carrier}")
```

새 배송업체를 추가하려면 이 메서드를 열어서 `elif`를 추가해야 합니다.

**After — 새 배송업체는 새 클래스 추가로 확장:**

```python
from typing import Protocol

class ShippingStrategy(Protocol):
    def cost(self, weight_kg: float) -> int: ...

class StandardShipping:
    def cost(self, weight_kg: float) -> int:
        return int(3000 + 500 * weight_kg)

class ExpressShipping:
    def cost(self, weight_kg: float) -> int:
        return int(6000 + 800 * weight_kg)

class ShippingCalculator:
    def __init__(self, strategy: ShippingStrategy):
        self._strategy = strategy

    def total_cost(self, weight_kg: float) -> int:
        return self._strategy.cost(weight_kg)
```

`ShippingCalculator`는 건드리지 않습니다. 새 클래스를 만들어 주입하면 끝입니다.

## Strategy 선택 기준 정리

| 기준 | Protocol 클래스 | 함수 | dict 레지스트리 |
| --- | --- | --- | --- |
| 상태 보유 | 자연스러움 | 클로저 필요 | 클로저 또는 partial |
| 타입 검사 | mypy 완전 지원 | Callable 타입 힌트 | 런타임 KeyError 가능 |
| 테스트 | 클래스 하나 작성 | lambda 한 줄 | dict에 lambda 삽입 |
| 과잉 설계 위험 | 높음 | 낮음 | 중간 |

AI에게 요청할 때는 "상태가 없으면 함수로, 상태가 있으면 클래스로" 명시하면 원하는 방식을 더 정확하게 받을 수 있습니다.

## AI 활용 팁

**Strategy 패턴으로 분기 제거 요청:**

```
"지금 결제 처리가 if/elif로 되어 있어. 결제 수단이 앞으로 계속
추가될 거야. Strategy 패턴으로 리팩토링해줘.
각 결제 수단을 별도 클래스로 만들고, dict 레지스트리로
문자열 키로 선택할 수 있게 해줘. Python Protocol 사용해서."
```

**런타임 교체 가능한 Strategy 요청:**

```
"A/B 테스트를 위해 할인 정책을 런타임에 교체할 수 있어야 해.
Strategy 패턴으로 구현하되, 사용자 ID 해시를 기반으로
실험 그룹을 결정하는 셀렉터도 함께 만들어줘."
```

**테스트 친화적인 Strategy 요청:**

```
"Strategy 패턴으로 만든 OrderService 테스트를 짜줘.
fake Strategy를 lambda로 주입해서 외부 의존 없이
비즈니스 로직만 검증하는 방식으로."
```

## 운영 체크리스트

- [ ] 모든 if/elif가 Strategy 후보가 아닌 이유를 설명할 수 있습니다.
- [ ] 함수 방식과 클래스 방식 Strategy를 언제 선택할지 말할 수 있습니다.
- [ ] AI가 만든 Strategy 구조에서 새 알고리즘을 추가할 수 있습니다.
- [ ] Strategy가 테스트를 단순하게 만드는 이유를 설명할 수 있습니다.

## 정리

이 글에서 다룬 핵심은 세 가지입니다. 첫째 Strategy가 적합한 분기는 세 가지 조건을 만족합니다: 알고리즘이 독립적이고, 앞으로 늘어날 가능성이 높고, 선택을 외부에 위임하고 싶을 때입니다. 둘째 Python에서는 상태가 없으면 함수, 있으면 클래스로 표현합니다. 셋째 AI에게 Strategy 구조를 요청하면 새 알고리즘 추가가 기존 코드 수정 없이 가능해집니다.

## 처음 질문으로 돌아가기

- **모든 if/elif 분기가 Strategy 후보일까요?**
  - 아닙니다. 알고리즘이 독립적이고, 분기가 앞으로 늘어날 가능성이 높고, 선택을 외부에 위임해야 할 때만 Strategy가 적합합니다.
- **AI가 만든 Strategy에서 클래스 방식과 함수 방식을 어떻게 구분할까요?**
  - 메서드가 하나뿐이고 상태가 없다면 함수로 단순화할 수 있습니다. 상태가 있거나 여러 메서드가 필요하다면 클래스가 더 자연스럽습니다.
- **Strategy를 런타임에 교체하면 어떤 이점이 있나요?**
  - A/B 테스트, 기능 플래그, 사용자 등급별 정책 적용이 가능합니다. 배포 없이 알고리즘을 전환할 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 디자인 패턴 기초 (1/10): 디자인 패턴이란 무엇인가?
- 바이브코딩을 위한 디자인 패턴 기초 (2/10): 생성 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (3/10): 구조 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (4/10): 행위 패턴
- **바이브코딩을 위한 디자인 패턴 기초 (5/10): 전략 패턴 (현재 글)**
- 바이브코딩을 위한 디자인 패턴 기초 (6/10): 어댑터 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (7/10): 옵저버 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (8/10): 팩토리와 의존성 주입
- 바이브코딩을 위한 디자인 패턴 기초 (9/10): 패턴을 남용하지 않는 법
- 바이브코딩을 위한 디자인 패턴 기초 (10/10): 파이썬에 어울리는 패턴

<!-- toc:end -->

## 참고 자료

### 핵심 자료

- [Strategy Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/strategy)
- [Open/Closed Principle (Wikipedia)](https://en.wikipedia.org/wiki/Open%E2%80%93closed_principle)
- [PEP 544 — Protocols](https://peps.python.org/pep-0544/)

### 실무 확장 읽을거리

- [sorted(key=...) (Python docs)](https://docs.python.org/3/howto/sorting.html)
- [functools — Higher-order functions (Python docs)](https://docs.python.org/3/library/functools.html)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/ko)

Tags: 바이브코딩, DesignPatterns, Strategy, Polymorphism, Behavioral, AI코딩
