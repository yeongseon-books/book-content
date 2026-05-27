---
series: design-patterns-101
episode: 5
title: "Design Patterns 101 (5/10): The Strategy Pattern"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - DesignPatterns
  - Strategy
  - Polymorphism
  - Behavioral
  - OCP
seo_description: How the Strategy pattern turns branching algorithms into swappable units and how to keep the Python version lightweight.
last_reviewed: '2026-05-23'
---

# Design Patterns 101 (5/10): The Strategy Pattern

In article 4 we surveyed Behavioral patterns and introduced Strategy as "the pattern that separates algorithms so they can be swapped." That one-liner is enough for a catalog entry, but the moment I try to apply Strategy in production, questions pile up fast. Is this branch really a Strategy candidate? Should it be a class or just a function? How do I handle a default? Is runtime swapping safe? I will answer each of these questions while digging deep into Strategy.

This is the 5th post in the Design Patterns 101 series.

![Strategy pattern structure](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/05/05-01-concept-at-a-glance.en.png)
*Context depends only on the Strategy interface; concrete algorithms are replaced independently*

## Questions to Keep in Mind

- Are all `if/elif` branches Strategy candidates, or must specific conditions be met?
- In Python, when does the choice between a class-based Strategy and a function-based Strategy diverge?
- What operational benefits emerge from swapping a Strategy at runtime?

## Telling apart real Strategy candidates from branch noise

Not every `if/elif` qualifies. I check three conditions simultaneously before reaching for Strategy.

**First, each branch must be algorithmically independent.** Every branch receives the same input shape and produces the same output shape, but the internal computation differs. If branches reference each other's results or depend on ordering, State or Chain of Responsibility fits better than Strategy.

**Second, the branch axis must be likely to grow.** Payment methods, shipping carriers, discount policies — axes where business requirements keep adding options are Strategy candidates. By contrast, `if response.status_code == 200` will not grow unless the HTTP spec changes, so extracting a Strategy there is over-engineering.

**Third, the call site should want to delegate the selection responsibility.** Sometimes the caller choosing the algorithm directly is perfectly natural. A CLI tool that receives `--format json` and picks a JSON formatter has clear branching where the caller owns the choice. Strategy shines when the call site wants to hand selection off to an external source — configuration, user input, or a runtime condition.

Branches that fail any of these three conditions produce what I call "premature Strategy": more classes, more indirection, no payoff.

## Three ways to express Strategy in Python

### Approach 1: Protocol-based classes

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
    tiers: list[tuple[int, float]]  # (quantity threshold, discount rate)

    def calculate(self, base_price: int, quantity: int) -> int:
        applicable_rate = 0.0
        for threshold, rate in sorted(self.tiers, reverse=True):
            if quantity >= threshold:
                applicable_rate = rate
                break
        return int(base_price * quantity * (1 - applicable_rate))
```

Class-based Strategy is the right fit **when the algorithm carries state**. `BulkPricing` needs a `threshold`; `TieredPricing` needs a `tiers` list. Using Protocol gives structural typing without inheritance, which means test fakes need no base class either.

### Approach 2: Functions (Callable)

```python
from typing import Callable

PricingFn = Callable[[int, int], int]


def standard_pricing(base_price: int, quantity: int) -> int:
    return base_price * quantity


def vip_pricing(base_price: int, quantity: int) -> int:
    return int(base_price * quantity * 0.7)


def seasonal_pricing(discount: float) -> PricingFn:
    """Closure-based Strategy that captures configuration."""
    def _calculate(base_price: int, quantity: int) -> int:
        return int(base_price * quantity * (1 - discount))
    return _calculate


class Order:
    def __init__(self, pricing: PricingFn = standard_pricing):
        self._pricing = pricing

    def total(self, base_price: int, quantity: int) -> int:
        return self._pricing(base_price, quantity)
```

Function-based Strategy works **when there is no state, or a closure suffices**. Functions are first-class objects in Python, so there is no reason to wrap them in a class. `sorted(key=lambda x: x.age)` is the canonical function Strategy everyone already uses.

### Approach 3: dict-of-callables (registry)

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

A dict registry is natural **when the Strategy must be selected by a string key** — an API parameter, a config file value, a database column. The external world speaks strings; the registry translates them into callables.

### Trade-offs across the three approaches

| Criterion | Protocol class | Function | dict-of-callables |
| --- | --- | --- | --- |
| Holding state | Natural | Requires closure | Closure or partial |
| Type checking | Full mypy support | Callable type hint | Runtime KeyError possible |
| Test fake | Write one class | One-line lambda | Insert lambda into dict |
| Extension scope | Add a new class file | Add a new function | Add one line to dict |
| Over-engineering risk | High | Low | Medium |

I default to functions first, then promote to a class when state appears. Starting with classes leaves unnecessary scaffolding behind.

## Strategy and OCP — reshaping how change looks

The Open/Closed Principle says code should be open for extension and closed for modification. Strategy is the most direct pattern that makes OCP visible in code structure. Here is what the shape of change looks like before and after.

**Before — extending by modification:**

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

Adding a new carrier means opening this method and appending an `elif`. That is modification of existing code — an OCP violation. Tests must re-run the entire method.

**After — extending by addition:**

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

Adding a new carrier no longer touches `ShippingCalculator`. Create a new class, inject it, done. The shape of change moved from "edit existing code" to "add new code."

There is a cost: tracing the full flow now requires following Strategy interface, implementation class, and injection site. If there are only two branches and no growth is expected, `if/elif` reads better. OCP pays off only on axes where change is frequent.

## Why a Default Strategy should always exist

When a context accepts a Strategy but has no default, every caller must explicitly choose one. If most callers use the same Strategy, that is unnecessary burden.

```python
class RetryPolicy(Protocol):
    def should_retry(self, attempt: int, error: Exception) -> bool: ...
    def delay_seconds(self, attempt: int) -> float: ...


class NoRetry:
    """Null Object Strategy — never retries."""
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

`NoRetry` is the Null Object pattern combined with Strategy. With a default in place, callers only specify a Strategy when they need something special. Most code stays simple.

When choosing a default, I pick **the safest behavior**. For retries, "no retry" is safe. For discounts, "no discount" is safe. If the default fires in an unexpected situation, the system must not end up in a dangerous state.

## Registration trade-offs as Strategy count grows

Once there are many Strategies, "how to find and wire the right one" becomes the real question. Three registration styles compared.

### Manual dict registration

```python
STRATEGIES: dict[str, ShippingStrategy] = {
    "standard": StandardShipping(),
    "express": ExpressShipping(),
    "same_day": SameDayShipping(),
}
```

Explicit and IDE-traceable. The downside: forget to add a new Strategy to the dict and a runtime KeyError surfaces in production.

### Decorator-based auto-registration

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

Creating a Strategy class automatically registers it. The downside: the decorator only runs when the module is imported, creating an implicit coupling to import order. IDE "find usages" also becomes harder.

### entry_points / plugin approach

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

External packages can provide Strategies, turning the application into a plugin architecture. The downside: complex setup and type safety is only verifiable at runtime. Overkill for most applications.

My rule of thumb: fewer than 10 Strategies — manual dict. Ten or more, or scattered across modules — decorator. External extensibility required — entry_points.

## Runtime swapping and A/B tests feel natural with Strategy

The core property of Strategy is that the context knows nothing about algorithm internals. Thanks to this property, swapping a Strategy at runtime requires zero changes to context code.

```python
import random


class ABTestPricingSelector:
    """Factory that picks a Strategy based on a feature flag."""

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
        # Deterministic hashing keeps the same user in the same group
        bucket = hash(user_id) % 100
        if bucket < self._ratio * 100:
            return self._experiment
        return self._control


# Usage
selector = ABTestPricingSelector(
    control=standard_pricing,
    experiment=vip_pricing,
    experiment_ratio=0.05,
)

order = Order(pricing=selector.select(user_id="user-42"))
```

In this structure, `Order` has no idea an A/B test is running. Strategy selection lives in a separate layer; business logic stays clean.

Combine this with a feature-flag system (LaunchDarkly, Unleash, or a homegrown one) and Strategies can be switched without a deploy. Roll a new discount policy to 5% of traffic, watch the metrics, then ramp to 100% — all by changing which Strategy gets selected.

## How Strategy simplifies testing

One of the most practical benefits of Strategy is how easy it becomes to cut external dependencies in tests.

```python
def test_order_total_uses_injected_strategy():
    """Replace Strategy with a fake to verify Order logic in isolation."""
    fixed_pricing: PricingFn = lambda base, qty: 999

    order = Order(pricing=fixed_pricing)
    assert order.total(base_price=10000, quantity=3) == 999


def test_exponential_backoff_delay():
    """Unit-test a Strategy independently."""
    policy = ExponentialBackoff(base=1.0, max_attempts=3)
    assert policy.delay_seconds(0) == 1.0
    assert policy.delay_seconds(1) == 2.0
    assert policy.delay_seconds(2) == 4.0
    assert policy.should_retry(2, IOError()) is True
    assert policy.should_retry(3, IOError()) is False
```

Strategy helps testing in two ways.

1. **Context tests**: inject a fake Strategy to isolate and verify context logic. Even if the real Strategy calls external APIs, databases, or network services, one fake cuts all of that out.
2. **Strategy tests**: each Strategy is unit-tested independently. No context needed — just input and output — so tests are fast and obvious.

No mock library required. A one-line lambda is already a fake Strategy. That is why Strategy testing in Python is particularly lightweight.

## Two pitfalls when Strategy goes wrong

### Pitfall 1: Premature Strategy

Applying Strategy to code with two branches that will never grow adds files to read, indirection to follow, and type traces to lose. Cost paid, nothing gained.

I treat "the moment a third branch appears" as the trigger for introducing Strategy. Two branches are clearer as `if/else`. When the third arrives, it signals a fourth is coming, and that is when I refactor.

### Pitfall 2: Strategy mutating Context state directly

```python
# Bad — Strategy modifies Context internals
class AggressiveDiscount:
    def calculate(self, order: "MutableOrder") -> int:
        order.applied_coupons.append("AGGRESSIVE")  # Mutates Context!
        return int(order.base_price * 0.5)
```

When a Strategy mutates Context state, swapping Strategies becomes unsafe. Apply Strategy A, then switch to Strategy B — A's side effects bleed into B's behavior. Debugging becomes extremely difficult.

The principle is simple. **A Strategy receives input and returns a result; it does not mutate Context state directly.** If side effects are needed, the Strategy returns a result and the Context uses that result to update its own state.

```python
# Good — Strategy returns a result only
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

## Answering the Opening Questions

- **Are all `if/elif` branches Strategy candidates, or must specific conditions be met?**
  - Three conditions must hold simultaneously. Each branch is algorithmically independent, the branch axis is likely to grow, and the call site wants to delegate selection to an external source. As the shipping example showed, carriers that keep getting added are candidates; HTTP status codes that never change are not.

- **In Python, when does the choice between a class-based Strategy and a function-based Strategy diverge?**
  - When the algorithm itself needs configuration state, use a class. When it does not, use a function. `BulkPricing` needs a threshold as an instance variable, so a class is natural. `vip_pricing` is pure input-output, so a bare function is more Pythonic. A closure can capture state too, but once configuration exceeds one or two values, a dataclass reads better.

- **What operational benefits emerge from swapping a Strategy at runtime?**
  - As the A/B test example showed, algorithms can be switched without a deploy. Combined with feature flags, a new policy can be applied to 5% of traffic, validated against metrics, then gradually expanded. Context code never changes, so rollback is a single line reverting the Strategy selection.

<!-- toc:begin -->
## Series Table of Contents

- [Design Patterns 101 (1/10): What Are Design Patterns?](./01-what-are-design-patterns.md)
- [Design Patterns 101 (2/10): Creational Patterns](./02-creational-patterns.md)
- [Design Patterns 101 (3/10): Structural Patterns](./03-structural-patterns.md)
- [Design Patterns 101 (4/10): Behavioral Patterns](./04-behavioral-patterns.md)
- **The Strategy Pattern (current)**
- The Adapter Pattern (upcoming)
- The Observer Pattern (upcoming)
- Factory and Dependency Injection (upcoming)
- When Not to Use Patterns (upcoming)
- Patterns That Fit Python (upcoming)

<!-- toc:end -->

## References

### Core References

- [Strategy Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/strategy)
- [Open/Closed Principle (Wikipedia)](https://en.wikipedia.org/wiki/Open%E2%80%93closed_principle)
- [PEP 544 — Protocols](https://peps.python.org/pep-0544/)

### Practical Extensions

- [sorted(key=...) (Python docs)](https://docs.python.org/3/howto/sorting.html)
- [functools — Higher-order functions and operations on callables (Python docs)](https://docs.python.org/3/library/functools.html)
- [importlib.metadata — entry_points (Python docs)](https://docs.python.org/3/library/importlib.metadata.html)
- [Example code for this series (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/en)

Tags: Computer Science, DesignPatterns, Strategy, Polymorphism, Behavioral, OCP
