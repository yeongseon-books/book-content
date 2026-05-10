---
series: functional-programming-101
episode: 10
title: 객체지향과 함수형의 균형
status: content-ready
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
seo_description: 객체지향과 함수형 프로그래밍을 적절히 혼용하는 실용적 설계 기준을 다룹니다.
last_reviewed: '2026-05-04'
---

# 객체지향과 함수형의 균형

> Functional Programming 101 시리즈 (10/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 객체지향과 함수형 중 하나를 선택해야 할까요, 아니면 둘을 함께 사용할 수 있을까요?

> Python은 다중 패러다임 언어입니다. 객체지향과 함수형은 대립이 아니라 상호 보완 관계입니다. 이 글에서는 두 패러다임의 강점을 살려 상황에 맞는 설계를 선택하는 실용적 기준을 다룹니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 객체지향과 함수형의 강점과 약점 비교
- 두 패러다임을 혼용하는 패턴
- 상황별 설계 선택 기준
- Python에서의 실용적 하이브리드 설계

## 왜 중요한가

"OOP만 사용" 또는 "FP만 사용"은 비현실적입니다. 실무 코드는 상태 관리가 필요한 부분(OOP)과 데이터 변환이 필요한 부분(FP)이 공존합니다. 두 패러다임을 적절히 조합하는 것이 좋은 설계의 핵심입니다.

> 좋은 설계 = 문제에 맞는 패러다임 선택

Python의 표준 라이브러리도 `pathlib`(OOP)과 `itertools`(FP)를 함께 제공합니다. 언어가 지원하는 모든 도구를 활용하는 것이 Pythonic합니다.

## 핵심 개념 잡기

> OOP vs FP — 강점 비교

```
OOP가 적합한 상황                FP가 적합한 상황
─────────────────               ─────────────────
상태 + 행위가 결합               상태 없는 데이터 변환
여러 인스턴스 관리               파이프라인 데이터 처리
프레임워크 통합                  동시성 / 병렬 처리
복잡한 도메인 모델               수학적 / 선언적 로직
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 다중 패러다임(multi-paradigm) | 여러 프로그래밍 스타일을 지원하는 언어입니다 |
| 하이브리드 설계 | OOP와 FP를 목적에 맞게 조합하는 설계 방식입니다 |
| Functional Core, Imperative Shell | 순수 함수 핵심 + 부수효과 경계 아키텍처입니다 |
| 값 객체(value object) | 불변이고 동등성으로 비교되는 객체입니다 |
| 서비스 함수 | 상태 없이 동작하는 비즈니스 로직 함수입니다 |

## Before / After

순수 OOP를 하이브리드로 전환합니다.

```python
# before: 모든 것을 클래스로
class OrderProcessor:
    def __init__(self, tax_rate: float) -> None:
        self.tax_rate = tax_rate

    def calculate_total(self, items: list[dict]) -> float:
        subtotal = sum(i["price"] * i["qty"] for i in items)
        return subtotal * (1 + self.tax_rate)

    def format_receipt(self, items: list[dict]) -> str:
        total = self.calculate_total(items)
        return f"합계: {total:,.0f}원"

processor = OrderProcessor(0.1)
print(processor.format_receipt([{"price": 10000, "qty": 2}]))
```

```python
# after: 값 객체(OOP) + 순수 함수(FP) 혼합
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
    return f"합계: {total:,.0f}원"

items = [OrderItem("커피", 10000, 2)]
print(format_receipt(items, 0.1))
```

## 단계별 실습

### Step 1: 값 객체 + 순수 함수

```python
from dataclasses import dataclass, replace
from typing import NamedTuple


# 값 객체: 불변, 동등성 기반
@dataclass(frozen=True)
class Money:
    amount: int
    currency: str = "KRW"

class Percentage(NamedTuple):
    value: float


# 순수 함수: 값 객체를 변환
def apply_discount(price: Money, discount: Percentage) -> Money:
    discounted = int(price.amount * (1 - discount.value))
    return replace(price, amount=discounted)

def add_tax(price: Money, tax: Percentage) -> Money:
    taxed = int(price.amount * (1 + tax.value))
    return replace(price, amount=taxed)

def format_money(money: Money) -> str:
    return f"{money.amount:,}{money.currency}"


price = Money(50000)
discounted = apply_discount(price, Percentage(0.1))
final = add_tax(discounted, Percentage(0.1))

print(f"원가: {format_money(price)}")         # 원가: 50,000KRW
print(f"할인 후: {format_money(discounted)}")  # 할인 후: 45,000KRW
print(f"세금 후: {format_money(final)}")       # 세금 후: 49,500KRW
```

### Step 2: Functional Core, Imperative Shell

```python
from dataclasses import dataclass


# === Functional Core (순수 함수) ===
@dataclass(frozen=True)
class User:
    name: str
    email: str
    active: bool = True

def validate_email(email: str) -> list[str]:
    """이메일 검증 — 순수 함수."""
    errors = []
    if "@" not in email:
        errors.append("@ 기호가 필요합니다")
    if "." not in email.split("@")[-1]:
        errors.append("도메인에 .이 필요합니다")
    return errors

def create_user_data(name: str, email: str) -> User | list[str]:
    """사용자 생성 검증 — 순수 함수."""
    errors = validate_email(email)
    if not name.strip():
        errors.append("이름이 비어있습니다")
    if errors:
        return errors
    return User(name=name.strip(), email=email.lower())


# === Imperative Shell (부수효과) ===
def handle_registration(name: str, email: str) -> None:
    """등록 처리 — 부수효과 포함."""
    result = create_user_data(name, email)
    if isinstance(result, list):
        for error in result:
            print(f"  오류: {error}")
    else:
        print(f"  등록 완료: {result}")
        # 실제로는 DB 저장, 이메일 발송 등


handle_registration("Alice", "alice@example.com")
# 등록 완료: User(name='Alice', email='alice@example.com', active=True)

handle_registration("", "invalid-email")
# 오류: @ 기호가 필요합니다
# 오류: 이름이 비어있습니다
```

### Step 3: 클래스 + 함수형 메서드

```python
from dataclasses import dataclass
from typing import Callable, Iterator


@dataclass
class DataPipeline:
    """클래스로 파이프라인을 구성하되, 각 단계는 순수 함수입니다."""
    steps: list[Callable] = None

    def __post_init__(self) -> None:
        if self.steps is None:
            self.steps = []

    def add_step(self, func: Callable) -> "DataPipeline":
        """새 단계를 추가한 새 파이프라인을 반환합니다 (불변)."""
        return DataPipeline(steps=[*self.steps, func])

    def run(self, data):
        """파이프라인을 실행합니다."""
        result = data
        for step in self.steps:
            result = step(result)
        return result


# 순수 함수 단계
def normalize(records: list[dict]) -> list[dict]:
    return [{**r, "name": r["name"].strip().title()} for r in records]

def enrich(records: list[dict]) -> list[dict]:
    return [{**r, "name_len": len(r["name"])} for r in records]

def filter_valid(records: list[dict]) -> list[dict]:
    return [r for r in records if r.get("score", 0) > 0]


# 파이프라인 조립 (OOP 인터페이스 + FP 실행)
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

### Step 4: 패러다임 선택 가이드

```python
# 상황 1: 상태 관리 → OOP
class ShoppingCart:
    def __init__(self) -> None:
        self._items: list[dict] = []

    def add(self, item: str, price: int) -> None:
        self._items.append({"item": item, "price": price})

    @property
    def total(self) -> int:
        return sum(i["price"] for i in self._items)


# 상황 2: 데이터 변환 → FP
def transform_prices(
    items: list[dict],
    rate: float,
) -> list[dict]:
    return [{**i, "price": int(i["price"] * rate)} for i in items]


# 상황 3: 프레임워크 통합 → OOP (프레임워크가 요구)
class UserSerializer:
    def to_dict(self, user) -> dict:
        return {"name": user.name, "email": user.email}


# 상황 4: 유틸리티 → FP
def slugify(text: str) -> str:
    return text.lower().strip().replace(" ", "-")


# 혼합 사용
cart = ShoppingCart()
cart.add("커피", 4500)
cart.add("케이크", 6000)

# OOP 객체의 데이터를 FP로 변환
discounted = transform_prices(cart._items, 0.9)
print(f"할인 전: {cart.total:,}원")
print(f"할인 후: {sum(i['price'] for i in discounted):,}원")
# 할인 전: 10,500원
# 할인 후: 9,450원
```

### Step 5: 설계 결정 체크리스트

```python
"""
패러다임 선택 체크리스트:

1. 상태 + 행위가 함께 변경되는가?
   → Yes: 클래스 (OOP)
   → No: 함수 (FP)

2. 여러 인스턴스가 필요한가?
   → Yes: 클래스 (OOP)
   → No: 모듈 수준 함수 (FP)

3. 데이터 변환이 주목적인가?
   → Yes: 순수 함수 파이프라인 (FP)
   → No: 상황에 따라 판단

4. 프레임워크가 클래스를 요구하는가?
   → Yes: 클래스 (OOP) + 내부 로직은 FP
   → No: 자유롭게 선택

5. 테스트 용이성이 중요한가?
   → Yes: 순수 함수 우선 (FP)
   → 상태 테스트가 필요하면: 클래스 (OOP)
"""

# 실전 하이브리드 패턴: 불변 값 객체 + 순수 함수 + 얇은 클래스 셸
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
    print(f"설정 유효: {config}")
# 설정 유효: Config(host='localhost', port=8080, debug=True)
```

## 이 코드에서 주목할 점

- 값 객체(frozen dataclass)는 OOP의 구조와 FP의 불변성을 결합합니다
- "Functional Core, Imperative Shell"은 테스트 가능한 핵심을 만드는 아키텍처입니다
- 클래스의 공개 인터페이스를 OOP로, 내부 로직을 FP로 구현하는 하이브리드가 효과적입니다
- 선택 기준은 "상태 관리가 필요한가?"입니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 패러다임 순수주의 고집 | 불필요한 복잡성이 추가됩니다 | 문제에 맞는 도구를 선택합니다 |
| 모든 것을 클래스로 래핑 | 함수로 충분한 경우가 많습니다 | "상태가 필요한가?" 먼저 질문합니다 |
| 함수형만 고집하며 상태 회피 | 상태 관리가 필요한 곳에서는 비효율적입니다 | 상태가 필요하면 클래스를 사용합니다 |
| 팀 내 스타일 불일치 | 코드 리뷰와 협업이 어려워집니다 | 팀 가이드라인을 합의합니다 |
| 과도한 추상화 | 간단한 코드가 더 나은 경우가 많습니다 | YAGNI 원칙을 적용합니다 |

## 실무에서 이렇게 쓰입니다

- Django/FastAPI: 클래스 기반 뷰 + 순수 함수 비즈니스 로직을 조합합니다
- 데이터 파이프라인: 함수형 변환 + OOP 커넥터를 함께 사용합니다
- 테스트: 순수 함수는 단위 테스트, 클래스는 통합 테스트로 검증합니다
- 설정 관리: frozen dataclass(OOP) + 검증 함수(FP)를 조합합니다
- 이벤트 처리: 이벤트 객체(OOP) + 핸들러 함수(FP)를 조합합니다

## 현업 개발자는 이렇게 생각합니다

"OOP vs FP"는 잘못된 이분법입니다. Python의 강점은 두 패러다임을 자유롭게 조합할 수 있다는 것입니다. 데이터 모델은 dataclass로, 비즈니스 로직은 순수 함수로, 프레임워크 통합은 클래스로 — 이것이 실용적인 Python 코드입니다.

"어떤 패러다임을 사용하는가?"보다 "코드가 테스트하기 쉬운가?", "변경이 쉬운가?", "읽기 쉬운가?"가 더 중요한 질문입니다. 이 시리즈에서 다룬 순수 함수, 불변 데이터, 고차 함수, 파이프라인이 여러분의 도구상자에 새로운 도구가 되길 바랍니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **도메인이 결정** — 데이터 변환은 FP, 상태 캡슐은 OOP가 자연스럽습니다.
- **불변 객체** — OOP 안에서도 불변 객체를 우선합니다.
- **의존성 주입** — 함수 인자가 곧 의존성 주입입니다.
- **테스트 가성비** — FP 코어 + OOP 셸 구조가 테스트 가성비가 큽니다.
- **현실 인정** — Python 표준 라이브러리는 OOP·FP 혼합이 자연스럽습니다.

## 체크리스트

- [ ] OOP와 FP의 강점과 약점을 비교할 수 있다
- [ ] "Functional Core, Imperative Shell" 패턴을 설명할 수 있다
- [ ] 값 객체와 순수 함수를 조합하여 설계할 수 있다
- [ ] 상황별 패러다임 선택 기준을 적용할 수 있다
- [ ] 하이브리드 설계 패턴을 실무에 적용할 수 있다

## 연습 문제

1. 쇼핑 카트를 OOP(Cart 클래스) + FP(할인 계산, 세금 계산 순수 함수)로 하이브리드 설계하세요.
2. "Functional Core, Imperative Shell" 패턴으로 파일 기반 설정 로더를 구현하세요.
3. 기존 OOP 코드에서 순수 함수로 추출할 수 있는 부분을 식별하고 리팩터링하세요.

## 정리 및 다음 글 안내

객체지향과 함수형은 대립이 아니라 상호 보완입니다. Python에서는 값 객체(OOP) + 순수 함수(FP) + 얇은 클래스 셸의 하이브리드가 가장 실용적입니다. 이 시리즈에서 다룬 순수 함수, 불변 데이터, 고차 함수, 클로저, 제너레이터, 함수 합성이 여러분의 코드를 더 깔끔하고 테스트 가능하게 만들어줄 것입니다.

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
