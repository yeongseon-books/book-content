---
series: functional-programming-101
episode: 10
title: 객체지향과 함수형의 균형
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - Functional Programming
  - OOP
  - 다중 패러다임
  - 설계 판단
seo_description: Python에서 객체지향과 함수형을 함께 쓰는 실전 설계 기준을 설명합니다.
last_reviewed: '2026-05-12'
---

# 객체지향과 함수형의 균형

이 글은 Functional Programming 101 시리즈의 마지막 글입니다.

함수형 프로그래밍을 배우다 보면 어느 순간 "그럼 객체지향은 버려야 하나?"라는 질문이 나옵니다. 반대로 객체지향에 익숙한 팀에서는 함수형 기법을 도입할 때 "결국 클래스가 더 익숙한데 굳이 왜?"라는 반응도 나옵니다. 둘 다 문제를 너무 이분법으로 보는 시선입니다.

Python은 애초에 다중 패러다임 언어입니다. 데이터 모델은 객체지향적으로 두고, 핵심 계산은 순수 함수로 분리하고, 프레임워크 경계에서는 다시 클래스나 핸들러를 쓰는 식의 혼합 설계가 가장 현실적입니다. 중요한 것은 신념이 아니라 선택 기준입니다.

## 이 글에서 다룰 문제

- 객체지향과 함수형은 각각 어떤 문제에 더 잘 맞을까요?
- 두 패러다임을 섞을 때 가장 실용적인 기본 패턴은 무엇일까요?
- Functional Core, Imperative Shell은 Python에서 어떻게 적용할 수 있을까요?
- 상태 관리와 데이터 변환 사이에서 어떤 기준으로 설계를 고르면 좋을까요?

> 멘탈 모델: 좋은 설계는 OOP나 FP 중 하나를 신앙처럼 고르는 일이 아니라, 상태가 필요한 부분은 객체로, 계산이 중심인 부분은 함수로 두는 문제 적합성의 선택입니다.

## 왜 중요한가

"OOP만 써라" 또는 "FP만 써라"는 생산 코드 기준으로는 비현실적입니다. 실제 시스템에는 상태를 오래 들고 있어야 하는 부분도 있고, 입력을 받아 값을 변환하기만 하면 되는 부분도 있습니다. 두 성격을 같은 도구로 밀어붙이면 오히려 코드가 더 나빠집니다.

Python 표준 라이브러리만 봐도 `pathlib` 같은 객체지향 도구와 `itertools` 같은 함수형 도구가 함께 존재합니다. Pythonic하다는 말은 한 패러다임만 고집하는 것이 아니라, 언어가 주는 여러 도구를 목적에 맞게 조합하는 데 더 가깝습니다.

## 개념 개요

> 상태 관리와 데이터 변환은 같은 문제처럼 보여도 요구 사항이 다릅니다.

```text
OOP Fits Best                  FP Fits Best
─────────────────             ─────────────────
State + behavior together     Stateless data transformation
Managing multiple instances   Pipeline data processing
Framework integration         Concurrency / parallelism
Complex domain models         Mathematical / declarative logic
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 다중 패러다임(multi-paradigm) | 여러 프로그래밍 스타일을 지원하는 언어 특성입니다 |
| 하이브리드 설계(hybrid design) | 목적에 따라 OOP와 FP를 함께 쓰는 설계 방식입니다 |
| Functional Core, Imperative Shell | 순수 함수 코어와 부수효과 경계를 분리하는 아키텍처입니다 |
| 값 객체(value object) | 동일성보다 값의 동등성으로 비교하는 불변 객체입니다 |
| 서비스 함수(service function) | 상태 없이 비즈니스 로직을 수행하는 함수입니다 |

## Before / After

모든 것을 클래스 안에 넣는 설계는 익숙하지만, 계산 로직까지 상태 객체에 묶어 버릴 수 있습니다. 값 객체와 순수 함수를 분리하면 테스트성과 재사용성이 좋아집니다.

```python
# before: everything in a class
class OrderProcessor:
    def __init__(self, tax_rate: float) -> None:
        self.tax_rate = tax_rate

    def calculate_total(self, items: list[dict]) -> float:
        subtotal = sum(i["price"] * i["qty"] for i in items)
        return subtotal * (1 + self.tax_rate)

    def format_receipt(self, items: list[dict]) -> str:
        total = self.calculate_total(items)
        return f"Total: ${total:,.2f}"

processor = OrderProcessor(0.1)
print(processor.format_receipt([{"price": 25.00, "qty": 2}]))
```

```python
# after: value objects (OOP) + pure functions (FP)
from dataclasses import dataclass

@dataclass(frozen=True)
class OrderItem:
    name: str
    price: float
    qty: int

def calculate_total(items: list[OrderItem], tax_rate: float) -> float:
    subtotal = sum(i.price * i.qty for i in items)
    return subtotal * (1 + tax_rate)

def format_receipt(items: list[OrderItem], tax_rate: float) -> str:
    total = calculate_total(items, tax_rate)
    return f"Total: ${total:,.2f}"

items = [OrderItem("Coffee", 25.00, 2)]
print(format_receipt(items, 0.1))
```

## 단계별 실습

### Step 1: 값 객체와 순수 함수 조합하기

```python
from dataclasses import dataclass, replace
from typing import NamedTuple


# value objects: immutable, equality-based
@dataclass(frozen=True)
class Money:
    amount: int
    currency: str = "USD"

class Percentage(NamedTuple):
    value: float


# pure functions: transform value objects
def apply_discount(price: Money, discount: Percentage) -> Money:
    discounted = int(price.amount * (1 - discount.value))
    return replace(price, amount=discounted)

def add_tax(price: Money, tax: Percentage) -> Money:
    taxed = int(price.amount * (1 + tax.value))
    return replace(price, amount=taxed)

def format_money(money: Money) -> str:
    return f"{money.amount:,} {money.currency}"


price = Money(50000)
discounted = apply_discount(price, Percentage(0.1))
final = add_tax(discounted, Percentage(0.1))

print(f"Original: {format_money(price)}")       # Original: 50,000 USD
print(f"After discount: {format_money(discounted)}")  # After discount: 45,000 USD
print(f"After tax: {format_money(final)}")       # After tax: 49,500 USD
```

값 객체는 OOP의 명시적인 데이터 모델링 장점을 가져오고, 순수 함수는 FP의 예측 가능성을 제공합니다. 둘을 함께 쓰면 서로의 약점을 상당 부분 보완할 수 있습니다.

### Step 2: Functional Core, Imperative Shell 적용하기

```python
from dataclasses import dataclass


# === Functional Core (pure functions) ===
@dataclass(frozen=True)
class User:
    name: str
    email: str
    active: bool = True

def validate_email(email: str) -> list[str]:
    """Email validation — pure function."""
    errors = []
    if "@" not in email:
        errors.append("@ symbol is required")
    if "." not in email.split("@")[-1]:
        errors.append("Domain must contain a dot")
    return errors

def create_user_data(name: str, email: str) -> User | list[str]:
    """User creation validation — pure function."""
    errors = validate_email(email)
    if not name.strip():
        errors.append("Name is empty")
    if errors:
        return errors
    return User(name=name.strip(), email=email.lower())


# === Imperative Shell (side effects) ===
def handle_registration(name: str, email: str) -> None:
    """Registration handler — contains side effects."""
    result = create_user_data(name, email)
    if isinstance(result, list):
        for error in result:
            print(f"  Error: {error}")
    else:
        print(f"  Registered: {result}")
        # In production: save to DB, send email, etc.


handle_registration("Alice", "alice@example.com")
# Registered: User(name='Alice', email='alice@example.com', active=True)

handle_registration("", "invalid-email")
# Error: @ symbol is required
# Error: Name is empty
```

이 패턴은 Python에서 함수형 사고를 가장 실용적으로 도입하는 방법입니다. 핵심 규칙은 순수 함수로 두고, 실제 부수효과는 가장 바깥쪽 핸들러에서만 수행합니다.

### Step 3: 클래스와 함수형 메서드 함께 쓰기

```python
from dataclasses import dataclass
from typing import Callable, Iterator


@dataclass
class DataPipeline:
    """A class that composes a pipeline where each stage is a pure function."""
    steps: list[Callable] = None

    def __post_init__(self) -> None:
        if self.steps is None:
            self.steps = []

    def add_step(self, func: Callable) -> "DataPipeline":
        """Returns a new pipeline with the added step (immutable)."""
        return DataPipeline(steps=[*self.steps, func])

    def run(self, data):
        """Executes the pipeline."""
        result = data
        for step in self.steps:
            result = step(result)
        return result


# pure function stages
def normalize(records: list[dict]) -> list[dict]:
    return [{**r, "name": r["name"].strip().title()} for r in records]

def enrich(records: list[dict]) -> list[dict]:
    return [{**r, "name_len": len(r["name"])} for r in records]

def filter_valid(records: list[dict]) -> list[dict]:
    return [r for r in records if r.get("score", 0) > 0]


# assemble the pipeline (OOP interface + FP execution)
pipeline = (
    DataPipeline()
    .add_step(normalize)
    .add_step(filter_valid)
    .add_step(enrich)
)

data = [
    {"name": "  alice  ", "score": 85},
    {"name": "  bob  ", "score": 0},
    {"name": "  charlie  ", "score": 92},
]

result = pipeline.run(data)
for r in result:
    print(r)
# {'name': 'Alice', 'score': 85, 'name_len': 5}
# {'name': 'Charlie', 'score': 92, 'name_len': 7}
```

공개 인터페이스는 클래스로 두고, 내부 실행은 순수 함수로 흘려보내는 방식도 아주 효과적입니다. 프레임워크 친화성과 테스트성을 동시에 챙길 수 있습니다.

### Step 4: 패러다임 선택 기준 세우기

```python
# Situation 1: state management -> OOP
class ShoppingCart:
    def __init__(self) -> None:
        self._items: list[dict] = []

    def add(self, item: str, price: int) -> None:
        self._items.append({"item": item, "price": price})

    @property
    def total(self) -> int:
        return sum(i["price"] for i in self._items)


# Situation 2: data transformation -> FP
def transform_prices(
    items: list[dict],
    rate: float,
) -> list[dict]:
    return [{**i, "price": int(i["price"] * rate)} for i in items]


# Situation 3: framework integration -> OOP (framework requires it)
class UserSerializer:
    def to_dict(self, user) -> dict:
        return {"name": user.name, "email": user.email}


# Situation 4: utility -> FP
def slugify(text: str) -> str:
    return text.lower().strip().replace(" ", "-")


# mixed usage
cart = ShoppingCart()
cart.add("Coffee", 450)
cart.add("Cake", 600)

# transform OOP object data with FP
discounted = transform_prices(cart._items, 0.9)
print(f"Before discount: {cart.total:,}")
print(f"After discount: {sum(i['price'] for i in discounted):,}")
# Before discount: 1,050
# After discount: 945
```

이 예제는 패러다임 선택이 정체성이 아니라 상황 판단임을 잘 보여 줍니다. 상태를 오래 들고 있어야 하면 OOP, 데이터만 바꾸면 되면 FP가 더 자연스럽습니다.

### Step 5: 설계 판단 체크리스트

```python
"""
Paradigm selection checklist:

1. Does state change together with behavior?
   -> Yes: class (OOP)
   -> No: function (FP)

2. Do you need multiple instances?
   -> Yes: class (OOP)
   -> No: module-level function (FP)

3. Is data transformation the main goal?
   -> Yes: pure function pipeline (FP)
   -> No: judge by context

4. Does the framework require classes?
   -> Yes: class (OOP) + internal logic as FP
   -> No: choose freely

5. Is testability a priority?
   -> Yes: pure functions first (FP)
   -> State testing needed: class (OOP)
"""

# practical hybrid pattern: immutable value objects + pure functions + thin class shell
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    host: str
    port: int
    debug: bool

def validate_config(config: Config) -> list[str]:
    errors = []
    if not config.host:
        errors.append("host is required")
    if config.port < 1 or config.port > 65535:
        errors.append("port must be 1-65535")
    return errors


config = Config(host="localhost", port=8080, debug=True)
errors = validate_config(config)
if not errors:
    print(f"Config valid: {config}")
# Config valid: Config(host='localhost', port=8080, debug=True)
```

팀 차원의 기준을 만들 때도 결국 이런 질문이 필요합니다. 상태가 핵심인가, 변환이 핵심인가, 테스트 우선순위는 무엇인가. 이 기준이 없으면 패러다임 논쟁은 금방 취향 싸움이 됩니다.

## 이 코드에서 주목할 점

- 값 객체(`frozen dataclass`)는 OOP의 구조화와 FP의 불변성을 함께 제공합니다.
- Functional Core, Imperative Shell은 테스트 가능한 코어를 만드는 실용 패턴입니다.
- 공개 인터페이스는 OOP, 내부 계산은 FP로 두는 혼합 설계가 매우 효과적입니다.
- 선택 기준은 결국 "상태 관리가 필요한가"입니다.

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 패러다임 순수주의 | 불필요한 복잡성을 만듭니다 | 문제에 맞는 도구를 고릅니다 |
| 모든 것을 클래스에 넣음 | 함수로 충분한 로직까지 무거워집니다 | 먼저 상태가 필요한지 묻습니다 |
| 상태를 무조건 피하려 함 | 상태 관리가 필요한 곳에서 오히려 비효율적입니다 | 필요한 곳에서는 클래스를 사용합니다 |
| 팀 안에서 스타일이 뒤섞임 | 리뷰와 협업 비용이 커집니다 | 팀 기준을 명확히 합의합니다 |
| 과도한 추상화 | 단순한 코드가 더 읽기 좋을 수 있습니다 | YAGNI를 적용합니다 |

## 실무에서 이렇게 쓰입니다

- Django/FastAPI에서 클래스 기반 인터페이스와 순수 함수 비즈니스 로직을 함께 사용합니다.
- 데이터 파이프라인에서는 OOP 커넥터와 FP 변환 단계를 결합합니다.
- 테스트는 순수 함수에 단위 테스트, 클래스에는 통합 테스트를 집중합니다.
- 설정은 frozen dataclass, 검증은 순수 함수로 분리합니다.
- 이벤트 객체는 OOP로, 핸들러 로직은 FP로 구성합니다.

## 현업에서는 이렇게 판단합니다

"OOP vs FP"는 Python에서는 대체로 잘못된 질문입니다. 더 좋은 질문은 "이 코드는 테스트하기 쉬운가", "변경하기 쉬운가", "읽기 쉬운가"입니다. 값 객체는 dataclass로, 비즈니스 로직은 순수 함수로, 프레임워크 경계는 클래스나 핸들러로 두는 방식이 실무적으로 가장 자주 성공합니다.

이 시리즈에서 다룬 순수 함수, 불변 데이터, 고차 함수, 클로저, 제너레이터, 함수 합성은 서로 따로 떨어진 기술이 아닙니다. 모두 더 작고 예측 가능한 계산 단위를 만들기 위한 도구입니다. 객체지향과 함수형의 균형을 잡는다는 것은 그 도구들을 상황에 맞게 조합할 수 있다는 뜻입니다.

## 체크리스트

- [ ] 객체지향과 함수형의 장단점을 비교할 수 있다
- [ ] Functional Core, Imperative Shell 패턴을 설명할 수 있다
- [ ] 값 객체와 순수 함수를 함께 사용하는 설계를 할 수 있다
- [ ] 상황별 패러다임 선택 기준을 적용할 수 있다
- [ ] 하이브리드 설계 패턴을 실제 코드에 적용할 수 있다

## 연습 문제

1. 장바구니를 OOP(`Cart` 클래스) + FP(할인, 세금 계산 함수) 혼합 구조로 설계해 보세요.
2. 파일 기반 설정 로더를 Functional Core, Imperative Shell 패턴으로 구현해 보세요.
3. 기존 OOP 코드에서 순수 함수로 뽑아낼 수 있는 부분을 찾아 리팩터링해 보세요.

## 정리와 다음 글

객체지향과 함수형은 경쟁 관계가 아니라 상호 보완 관계입니다. Python에서는 불변 값 객체(OOP) + 순수 함수(FP) + 얇은 클래스 셸이라는 조합이 가장 실용적인 경우가 많습니다. 이 시리즈에서 다룬 함수형 도구들을 적절히 섞어 쓰면 더 읽기 쉽고 테스트하기 쉬운 코드를 만들 수 있습니다.

<!-- toc:begin -->
- [함수형 프로그래밍이란 무엇인가?](./01-what-is-fp.md)
- [순수 함수와 부수효과](./02-pure-functions.md)
- [immutable 데이터](./03-immutable-data.md)
- [고차 함수](./04-higher-order-functions.md)
- [map, filter, reduce](./05-map-filter-reduce.md)
- [클로저와 partial](./06-closure-and-partial.md)
- [재귀와 꼬리 호출](./07-recursion.md)
- [지연 평가와 제너레이터](./08-lazy-evaluation.md)
- [함수 합성과 파이프라인](./09-function-composition.md)
- **객체지향과 함수형의 균형 (현재 글)**
<!-- toc:end -->

## 참고 자료

- [Functional Core, Imperative Shell — Gary Bernhardt](https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell)
- [Clean Architecture — Robert C. Martin](https://www.oreilly.com/library/view/clean-architecture-a/9780134494272/)
- [Fluent Python — Chapter 7: Functions as First-Class Objects](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)
- [Python 공식 문서 — Programming FAQ](https://docs.python.org/3/faq/programming.html)

Tags: Python, Functional Programming, OOP, 다중 패러다임, 설계 판단
