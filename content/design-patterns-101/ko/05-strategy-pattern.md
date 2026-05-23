---
series: design-patterns-101
episode: 5
title: "디자인 패턴 101 (5/10): 전략 패턴"
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
  - Strategy
  - Polymorphism
  - Behavioral
  - OCP
seo_description: Strategy 패턴으로 분기 폭발을 교체 가능한 알고리즘 단위로 바꾸고 Python에서 가볍게 구현하는 방법을 설명합니다.
last_reviewed: '2026-05-23'
---

# 디자인 패턴 101 (5/10): 전략 패턴

4장에서 Behavioral 패턴을 훑을 때 Strategy를 "알고리즘을 교체 가능하게 분리하는 패턴"으로 소개했습니다. 한 줄 요약으로는 충분하지만, 실무에서 Strategy를 적용하려고 하면 금방 질문이 쏟아집니다. 이 분기가 정말 Strategy 후보인지, 클래스로 만들어야 하는지 함수면 되는지, 기본 전략은 어떻게 두는지, 런타임에 바꿔도 안전한지. 저는 이 질문들에 하나씩 답하면서 Strategy를 깊게 파 보겠습니다.

이 글은 Design Patterns 101 시리즈의 다섯 번째 글입니다.

![Strategy 패턴 구조](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/05/05-01-concept-at-a-glance.ko.png)
*Context가 Strategy 인터페이스에만 의존하고, 구체 알고리즘은 독립적으로 교체되는 구조*

## 먼저 던지는 질문

- 모든 `if/elif` 분기가 Strategy 후보일까요, 아니면 특정 조건을 만족해야 할까요?
- Python에서 Strategy를 클래스로 만드는 것과 함수로 만드는 것은 언제 갈라질까요?
- Strategy를 런타임에 교체하면 어떤 운영상 이점이 생길까요?

## 분기 폭발이 정말 Strategy 후보인지 가려내는 방법

모든 `if/elif`가 Strategy 후보는 아닙니다. 저는 세 가지 조건을 동시에 만족하는지 먼저 확인합니다.

**첫째, 분기마다 알고리즘이 독립적인가.** 각 분기가 같은 입력을 받아 같은 형태의 출력을 내지만, 내부 계산 방식이 서로 다른 경우입니다. 반대로 분기들이 서로의 결과를 참조하거나 순서에 의존한다면 Strategy보다 State나 Chain of Responsibility가 더 맞습니다.

**둘째, 분기가 앞으로 늘어날 가능성이 높은가.** 결제 수단, 배송 업체, 할인 정책처럼 비즈니스 요구에 따라 옵션이 추가되는 축이라면 Strategy 후보입니다. 반면 `if response.status_code == 200` 같은 분기는 HTTP 스펙이 바뀌지 않는 한 늘어나지 않으므로 Strategy로 빼면 과잉입니다.

**셋째, 호출부가 알고리즘 선택 책임에서 벗어나야 하는가.** 호출부가 "어떤 알고리즘을 쓸지"를 직접 결정하는 게 자연스러운 경우도 있습니다. 예를 들어 CLI 도구에서 `--format json`을 받아 JSON 포매터를 고르는 코드는 분기가 명확하고 호출부가 선택 책임을 가지는 게 맞습니다. Strategy가 빛나는 건 호출부가 선택을 외부(설정, 사용자 입력, 런타임 조건)에 위임하고 싶을 때입니다.

이 세 조건을 만족하지 않는 분기에 Strategy를 적용하면, 클래스만 늘고 읽기 어려운 코드가 됩니다. 저는 이걸 "premature Strategy"라고 부릅니다.

## Python에서 Strategy를 표현하는 세 가지 방식

### 방식 1: Protocol 기반 클래스

```python
from typing import Protocol
from dataclasses import dataclass


class PricingStrategy(Protocol):
    def calculate(self, base_price: int, quantity: int) -> int: ...


@dataclass
class StandardPricing:
    def calculate(self, base_price: int, quantity: int) -> int:
        return base_price * quantity


@dataclass
class BulkPricing:
    threshold: int = 10
    discount_rate: float = 0.15

    def calculate(self, base_price: int, quantity: int) -> int:
        if quantity >= self.threshold:
            return int(base_price * quantity * (1 - self.discount_rate))
        return base_price * quantity


@dataclass
class TieredPricing:
    tiers: list[tuple[int, float]]  # (수량 임계값, 할인율)

    def calculate(self, base_price: int, quantity: int) -> int:
        applicable_rate = 0.0
        for threshold, rate in sorted(self.tiers, reverse=True):
            if quantity >= threshold:
                applicable_rate = rate
                break
        return int(base_price * quantity * (1 - applicable_rate))
```

클래스 Strategy는 **상태를 가져야 할 때** 적합합니다. `BulkPricing`의 `threshold`나 `TieredPricing`의 `tiers`처럼 알고리즘 자체에 설정값이 필요한 경우입니다. Protocol을 쓰면 상속 없이 구조적 타이핑으로 계약을 표현할 수 있어서, 테스트용 fake를 만들 때도 별도 상속이 필요 없습니다.

### 방식 2: 함수(Callable)

```python
from typing import Callable

PricingFn = Callable[[int, int], int]


def standard_pricing(base_price: int, quantity: int) -> int:
    return base_price * quantity


def vip_pricing(base_price: int, quantity: int) -> int:
    return int(base_price * quantity * 0.7)


def seasonal_pricing(discount: float) -> PricingFn:
    """클로저로 설정을 캡처하는 함수 Strategy."""
    def _calculate(base_price: int, quantity: int) -> int:
        return int(base_price * quantity * (1 - discount))
    return _calculate


class Order:
    def __init__(self, pricing: PricingFn = standard_pricing):
        self._pricing = pricing

    def total(self, base_price: int, quantity: int) -> int:
        return self._pricing(base_price, quantity)
```

함수 Strategy는 **상태가 없거나 클로저로 충분할 때** 씁니다. Python에서 함수는 일급 객체이므로 별도 클래스를 만들 이유가 없습니다. `sorted(key=lambda x: x.age)`가 대표적인 함수 Strategy입니다.

### 방식 3: dict-of-callables (레지스트리)

```python
PRICING_STRATEGIES: dict[str, PricingFn] = {
    "standard": standard_pricing,
    "vip": vip_pricing,
    "summer_sale": seasonal_pricing(0.2),
}


def calculate_price(tier: str, base_price: int, quantity: int) -> int:
    strategy = PRICING_STRATEGIES.get(tier)
    if strategy is None:
        raise ValueError(f"Unknown pricing tier: {tier}")
    return strategy(base_price, quantity)
```

dict 레지스트리는 **문자열 키로 Strategy를 선택해야 할 때** 자연스럽습니다. API 요청의 파라미터, 설정 파일의 값, 데이터베이스 컬럼 등 외부에서 문자열로 들어오는 선택지를 Strategy로 연결할 때 씁니다.

### 세 방식의 트레이드오프

| 기준 | Protocol 클래스 | 함수 | dict-of-callables |
| --- | --- | --- | --- |
| 상태 보유 | 자연스러움 | 클로저 필요 | 클로저 또는 partial |
| 타입 검사 | mypy 완전 지원 | Callable 타입 힌트 | 런타임 KeyError 가능 |
| 테스트 fake | 클래스 하나 작성 | lambda 한 줄 | dict에 lambda 삽입 |
| 확장 시 변경 범위 | 새 클래스 파일 추가 | 새 함수 추가 | dict에 한 줄 추가 |
| 과잉 설계 위험 | 높음 | 낮음 | 중간 |

저는 기본적으로 함수부터 시작하고, 상태가 필요해지면 클래스로 올리는 순서를 권합니다. 처음부터 클래스로 시작하면 불필요한 구조가 남기 쉽습니다.

## Strategy와 OCP — 변경의 모양을 바꾸는 리팩토링

Open/Closed Principle은 "확장에 열려 있고 수정에 닫혀 있어야 한다"는 원칙입니다. Strategy는 이 원칙을 코드 모양으로 드러내는 가장 직접적인 패턴입니다. 구체적으로 어떻게 변경의 모양이 바뀌는지 보겠습니다.

**Before — 수정으로 확장하는 코드:**

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

새 배송 업체를 추가하려면 이 메서드를 열어서 `elif`를 추가해야 합니다. 기존 코드를 수정하는 것이므로 OCP를 위반합니다. 테스트도 이 메서드 전체를 다시 돌려야 합니다.

**After — 추가로 확장하는 코드:**

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


class SameDayShipping:
    def cost(self, weight_kg: float) -> int:
        return int(15000 + 1200 * weight_kg)


class ShippingCalculator:
    def __init__(self, strategy: ShippingStrategy):
        self._strategy = strategy

    def total_cost(self, weight_kg: float) -> int:
        return self._strategy.cost(weight_kg)
```

새 배송 업체를 추가할 때 `ShippingCalculator`는 건드리지 않습니다. 새 클래스를 하나 만들고 주입하면 끝입니다. 변경의 모양이 "기존 코드 수정"에서 "새 코드 추가"로 바뀌었습니다.

이 변환에서 잃는 것도 있습니다. 전체 흐름을 파악하려면 Strategy 인터페이스 → 구현 클래스 → 주입 지점을 따라가야 합니다. 분기가 2개이고 앞으로도 늘어나지 않을 거라면 `if/elif`가 더 읽기 쉽습니다. OCP는 "변경이 자주 일어나는 축"에만 적용할 때 가치가 있습니다.

## Default Strategy를 항상 두어야 하는 이유

Strategy를 주입받는 컨텍스트에 기본값이 없으면, 모든 호출자가 매번 Strategy를 명시적으로 선택해야 합니다. 대부분의 호출자가 같은 Strategy를 쓴다면 이건 불필요한 부담입니다.

```python
class RetryPolicy(Protocol):
    def should_retry(self, attempt: int, error: Exception) -> bool: ...
    def delay_seconds(self, attempt: int) -> float: ...


class NoRetry:
    """아무것도 재시도하지 않는 Null Object Strategy."""
    def should_retry(self, attempt: int, error: Exception) -> bool:
        return False

    def delay_seconds(self, attempt: int) -> float:
        return 0.0


class ExponentialBackoff:
    def __init__(self, base: float = 1.0, max_attempts: int = 5):
        self._base = base
        self._max_attempts = max_attempts

    def should_retry(self, attempt: int, error: Exception) -> bool:
        return attempt < self._max_attempts

    def delay_seconds(self, attempt: int) -> float:
        return self._base * (2 ** attempt)


class HttpClient:
    def __init__(self, retry: RetryPolicy | None = None):
        self._retry = retry or NoRetry()

    def get(self, url: str) -> bytes:
        for attempt in range(10):
            try:
                return self._do_request(url)
            except IOError as e:
                if not self._retry.should_retry(attempt, e):
                    raise
                import time
                time.sleep(self._retry.delay_seconds(attempt))
        raise IOError("max retries exceeded")

    def _do_request(self, url: str) -> bytes:
        ...
```

`NoRetry`는 Null Object 패턴과 Strategy의 결합입니다. 기본 Strategy가 있으면 호출자는 "특별한 경우"에만 Strategy를 명시하면 됩니다. 대부분의 코드가 단순해집니다.

기본 Strategy를 고를 때 저는 **가장 안전한 동작**을 기본으로 둡니다. 재시도라면 "재시도 안 함"이 안전하고, 할인이라면 "할인 없음"이 안전합니다. 예상치 못한 상황에서 기본 Strategy가 실행되더라도 시스템이 위험해지지 않아야 합니다.

## Strategy 등록 방식별 트레이드오프

Strategy가 많아지면 "어떤 Strategy를 어떻게 찾아서 연결하는가"가 중요해집니다. 세 가지 등록 방식을 비교합니다.

### 수동 dict 등록

```python
STRATEGIES: dict[str, ShippingStrategy] = {
    "standard": StandardShipping(),
    "express": ExpressShipping(),
    "same_day": SameDayShipping(),
}
```

장점은 명시적이라 IDE에서 바로 추적됩니다. 단점은 새 Strategy를 만들고 dict에 등록하는 걸 잊으면 런타임 KeyError가 납니다.

### 데코레이터 기반 자동 등록

```python
from typing import Callable, Any

_REGISTRY: dict[str, Any] = {}


def register_strategy(name: str) -> Callable:
    def decorator(cls: type) -> type:
        _REGISTRY[name] = cls()
        return cls
    return decorator


def get_strategy(name: str) -> ShippingStrategy:
    if name not in _REGISTRY:
        raise ValueError(f"No strategy registered for: {name}")
    return _REGISTRY[name]


@register_strategy("overnight")
class OvernightShipping:
    def cost(self, weight_kg: float) -> int:
        return int(20000 + 1500 * weight_kg)
```

장점은 Strategy 클래스를 만들면 등록이 자동으로 따라옵니다. 단점은 모듈이 import되어야 데코레이터가 실행되므로, import 순서에 의존하는 암묵적 결합이 생깁니다. 또한 IDE에서 "이 Strategy는 어디서 쓰이는가"를 추적하기 어렵습니다.

### entry_points / 플러그인 방식

```toml
# pyproject.toml
[project.entry-points."myapp.shipping"]
overnight = "myapp.shipping.overnight:OvernightShipping"
```

```python
from importlib.metadata import entry_points


def load_shipping_strategies() -> dict[str, ShippingStrategy]:
    eps = entry_points(group="myapp.shipping")
    return {ep.name: ep.load()() for ep in eps}
```

장점은 외부 패키지가 Strategy를 제공할 수 있어 플러그인 아키텍처가 됩니다. 단점은 설정이 복잡하고, 타입 안전성을 런타임에만 검증할 수 있습니다. 대부분의 애플리케이션에서는 과잉입니다.

저는 Strategy가 10개 미만이면 수동 dict, 10개 이상이거나 여러 모듈에 흩어져 있으면 데코레이터, 외부 확장이 필요하면 entry_points를 권합니다.

## 런타임 교체와 A/B 테스트가 Strategy에서 자연스러운 이유

Strategy의 핵심 특성은 컨텍스트가 알고리즘 내부를 모른다는 것입니다. 이 특성 덕분에 런타임에 Strategy를 바꿔도 컨텍스트 코드는 전혀 변경할 필요가 없습니다.

```python
import random


class ABTestPricingSelector:
    """Feature flag 기반으로 Strategy를 선택하는 팩토리."""

    def __init__(
        self,
        control: PricingFn,
        experiment: PricingFn,
        experiment_ratio: float = 0.1,
    ):
        self._control = control
        self._experiment = experiment
        self._ratio = experiment_ratio

    def select(self, user_id: str) -> PricingFn:
        # 결정적 해싱으로 같은 유저는 항상 같은 그룹
        bucket = hash(user_id) % 100
        if bucket < self._ratio * 100:
            return self._experiment
        return self._control


# 사용
selector = ABTestPricingSelector(
    control=standard_pricing,
    experiment=vip_pricing,
    experiment_ratio=0.05,
)

order = Order(pricing=selector.select(user_id="user-42"))
```

이 구조에서 `Order`는 A/B 테스트가 진행 중인지 전혀 모릅니다. Strategy 선택 로직만 별도 계층에 있고, 비즈니스 로직은 깨끗하게 유지됩니다.

Feature flag 시스템(LaunchDarkly, Unleash, 자체 구현)과 결합하면 배포 없이 Strategy를 전환할 수 있습니다. 새 할인 정책을 5% 트래픽에만 적용하고, 지표를 확인한 뒤 100%로 올리는 흐름이 Strategy 교체 한 줄로 가능합니다.

## Strategy가 테스트를 단순하게 만드는 구조

Strategy 패턴의 가장 실용적인 이점 중 하나는 테스트에서 외부 의존성을 잘라내기 쉽다는 점입니다.

```python
def test_order_total_uses_injected_strategy():
    """Strategy를 fake로 교체해 Order 로직만 검증."""
    fixed_pricing: PricingFn = lambda base, qty: 999

    order = Order(pricing=fixed_pricing)
    assert order.total(base_price=10000, quantity=3) == 999


def test_exponential_backoff_delay():
    """Strategy 자체를 독립적으로 단위 테스트."""
    policy = ExponentialBackoff(base=1.0, max_attempts=3)
    assert policy.delay_seconds(0) == 1.0
    assert policy.delay_seconds(1) == 2.0
    assert policy.delay_seconds(2) == 4.0
    assert policy.should_retry(2, IOError()) is True
    assert policy.should_retry(3, IOError()) is False
```

Strategy 패턴이 테스트를 돕는 방식은 두 가지입니다.

1. **컨텍스트 테스트**: fake Strategy를 주입해서 컨텍스트의 로직만 격리 검증합니다. 외부 API, 데이터베이스, 네트워크 호출이 Strategy 안에 있더라도 fake 하나로 전부 잘라냅니다.
2. **Strategy 테스트**: 각 Strategy를 독립적으로 단위 테스트합니다. 컨텍스트 없이 입력-출력만 검증하면 되므로 테스트가 빠르고 명확합니다.

mock 라이브러리 없이도 lambda 한 줄이면 fake Strategy가 됩니다. 이 점이 Python에서 Strategy 테스트가 특히 가벼운 이유입니다.

## Strategy를 잘못 쓰면 생기는 두 가지 함정

### 함정 1: Premature Strategy

분기가 2개이고 앞으로도 늘어나지 않을 코드에 Strategy를 적용하면, 읽어야 할 파일이 늘고 간접 호출이 생기고 타입 추적이 어려워집니다. 얻는 것 없이 비용만 치르는 상태입니다.

저는 "세 번째 분기가 추가되는 순간"을 Strategy 도입 시점으로 봅니다. 두 개까지는 `if/else`가 더 명확합니다. 세 번째가 오면 "네 번째도 오겠구나"라는 신호이므로 그때 리팩토링합니다.

### 함정 2: Strategy가 Context의 가변 상태를 직접 조작

```python
# 나쁜 예 — Strategy가 Context 내부를 직접 변경
class AggressiveDiscount:
    def calculate(self, order: "MutableOrder") -> int:
        order.applied_coupons.append("AGGRESSIVE")  # Context 상태 변경!
        return int(order.base_price * 0.5)
```

Strategy가 Context의 상태를 직접 바꾸면 Strategy 간 교체가 안전하지 않게 됩니다. Strategy A를 적용한 뒤 Strategy B로 바꾸면 A가 남긴 부작용이 B의 동작에 영향을 줍니다. 디버깅이 극도로 어려워집니다.

원칙은 단순합니다. **Strategy는 입력을 받아 결과를 반환할 뿐, Context의 상태를 직접 변경하지 않습니다.** 부작용이 필요하면 Strategy가 결과를 반환하고, Context가 그 결과를 바탕으로 자신의 상태를 변경하는 구조로 만듭니다.

```python
# 좋은 예 — Strategy는 결과만 반환
from dataclasses import dataclass


@dataclass
class PricingResult:
    final_price: int
    applied_label: str


class AggressiveDiscount:
    def calculate(self, base_price: int, quantity: int) -> PricingResult:
        return PricingResult(
            final_price=int(base_price * quantity * 0.5),
            applied_label="AGGRESSIVE",
        )
```

## 처음 질문으로 돌아가기

- **모든 `if/elif` 분기가 Strategy 후보일까요, 아니면 특정 조건을 만족해야 할까요?**
  - 세 가지 조건을 동시에 만족해야 합니다. 분기마다 알고리즘이 독립적이고, 분기가 앞으로 늘어날 가능성이 높고, 호출부가 선택 책임을 외부에 위임하고 싶을 때입니다. 배송비 예시에서 본 것처럼 업체가 계속 추가되는 축이라면 후보이고, HTTP 상태 코드처럼 고정된 분기라면 아닙니다.

- **Python에서 Strategy를 클래스로 만드는 것과 함수로 만드는 것은 언제 갈라질까요?**
  - 알고리즘 자체에 설정 상태가 필요하면 클래스, 없으면 함수입니다. `BulkPricing`처럼 threshold를 인스턴스 변수로 가져야 하면 클래스가 자연스럽고, `vip_pricing`처럼 입력-출력만 있으면 함수 한 줄이 더 Python답습니다. 클로저로 상태를 캡처할 수도 있지만, 설정이 2개 이상이면 dataclass가 더 읽기 쉽습니다.

- **Strategy를 런타임에 교체하면 어떤 운영상 이점이 생길까요?**
  - A/B 테스트 예시에서 본 것처럼 배포 없이 알고리즘을 전환할 수 있습니다. Feature flag와 결합하면 5% 트래픽에만 새 정책을 적용하고 지표를 확인한 뒤 점진적으로 확대하는 흐름이 가능합니다. Context 코드는 전혀 변경하지 않으므로 롤백도 Strategy 선택 한 줄을 되돌리면 끝입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Design Patterns 101 (1/10): 디자인 패턴이란 무엇인가?](./01-what-are-design-patterns.md)
- [Design Patterns 101 (2/10): Creational 패턴](./02-creational-patterns.md)
- [Design Patterns 101 (3/10): Structural 패턴](./03-structural-patterns.md)
- [Design Patterns 101 (4/10): Behavioral 패턴](./04-behavioral-patterns.md)
- **Strategy 패턴 (현재 글)**
- Adapter 패턴 (예정)
- Observer 패턴 (예정)
- Factory와 의존성 주입 (예정)
- 패턴을 남용하지 않는 법 (예정)
- Python에 어울리는 패턴 (예정)

<!-- toc:end -->

## 참고 자료

### 핵심 자료

- [Strategy Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/strategy)
- [Open/Closed Principle (Wikipedia)](https://en.wikipedia.org/wiki/Open%E2%80%93closed_principle)
- [PEP 544 — Protocols](https://peps.python.org/pep-0544/)

### 실무 확장 읽을거리

- [sorted(key=...) (Python docs)](https://docs.python.org/3/howto/sorting.html)
- [functools — Higher-order functions and operations on callables (Python docs)](https://docs.python.org/3/library/functools.html)
- [importlib.metadata — entry_points (Python docs)](https://docs.python.org/3/library/importlib.metadata.html)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/ko)

Tags: Computer Science, DesignPatterns, Strategy, Polymorphism, Behavioral, OCP
