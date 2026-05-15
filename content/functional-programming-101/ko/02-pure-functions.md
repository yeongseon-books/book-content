---
series: functional-programming-101
episode: 2
title: 순수 함수와 부수효과
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - Functional Programming
  - 순수 함수
  - 부수효과
  - 테스트
seo_description: 순수 함수의 두 가지 조건과 참조 투명성을 정의하고, 부수효과를 격리하여 테스트와 리팩터링이 쉬운 코드를 설계하는 실무 패턴을 다룹니다.
last_reviewed: '2026-05-12'
---

# 순수 함수와 부수효과

이 글은 Functional Programming 101 시리즈의 두 번째 글입니다.

함수형 프로그래밍을 이야기할 때 가장 먼저 제대로 잡아야 하는 개념이 순수 함수입니다. 같은 입력을 주면 항상 같은 결과가 나오는 함수, 그리고 함수 바깥의 상태를 바꾸지 않는 함수가 왜 중요한지 이해하면 이후에 나오는 불변성, 캐싱, 병렬 처리, 테스트 전략이 한 번에 연결됩니다.

현업에서는 모든 함수를 순수하게 만들 수는 없습니다. 파일을 저장해야 하고, 로그를 남겨야 하고, 데이터베이스도 호출해야 합니다. 그래서 핵심은 부수효과를 없애는 것이 아니라, 어디에 두고 어떻게 격리할지를 설계하는 것입니다.

## 이 글에서 다룰 문제

- 어떤 조건을 만족해야 함수를 순수 함수라고 부를 수 있을까요?
- 코드에서 부수효과는 어떤 형태로 나타나며 어떻게 식별할 수 있을까요?
- 순수한 계산과 IO를 분리하면 테스트는 어떻게 단순해질까요?
- 참조 투명성은 왜 캐싱과 리팩터링의 기반이 될까요?

> 멘탈 모델: 순수 함수는 "입력과 출력만 있는 계산 장치"이고, 부수효과는 프로그램이 바깥 세계와 접촉하는 경계입니다. 두 영역을 섞지 않을수록 시스템은 읽기 쉽고 테스트하기 쉬워집니다.

## 왜 중요한가

실제 버그의 상당수는 예상하지 못한 상태 변화에서 나옵니다. 전역 변수가 바뀌었거나, 인자로 받은 리스트가 몰래 수정됐거나, 현재 시간과 난수에 의존하는 로직이 숨어 있으면 테스트 결과와 운영 결과가 쉽게 어긋납니다.

순수 함수는 입력과 출력만 보면 동작을 설명할 수 있기 때문에 디버깅 비용이 매우 낮습니다. 반대로 부수효과가 중심에 있는 코드는 환경과 순서에 민감해지고, 테스트를 위해 mock과 fixture가 과도하게 늘어나는 경우가 많습니다.

## 개념 개요

> 순수 함수인지 판단할 때는 두 질문이면 충분합니다. 같은 입력이 항상 같은 결과를 내는가? 함수 바깥 상태를 바꾸는가?

```text
Call f(x)
  |
  +-- Same x always gives same result? -- No --> Impure
  |          |
  |         Yes
  |          |
  +-- Modifies external state? --------- Yes --> Impure
  |          |
  |         No
  |          |
  +-- Pure function!
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 순수 함수(pure function) | 참조 투명성을 가지며 부수효과가 없는 함수입니다 |
| 부수효과(side effect) | 함수 바깥 상태를 읽거나 바꾸는 모든 동작입니다 |
| 참조 투명성(referential transparency) | 함수 호출을 결과값으로 안전하게 대체할 수 있는 성질입니다 |
| 결정적(deterministic) | 같은 입력에 항상 같은 출력을 내는 성질입니다 |
| 멱등성(idempotent) | 여러 번 실행해도 결과가 같게 유지되는 성질입니다 |

## Before / After

전역 상태에 의존하는 함수는 입력이 같아도 결과가 달라질 수 있습니다. 의존성을 인자로 끌어오면 그 순간 함수는 예측 가능해집니다.

```python
# before: impure function depending on global state
discount_rate = 0.1

def apply_discount(price: float) -> float:
    return price * (1 - discount_rate)

print(apply_discount(10000))  # 9000.0
discount_rate = 0.2
print(apply_discount(10000))  # 8000.0 — same input, different result!
```

```python
# after: pure function — all dependencies as arguments
def apply_discount(price: float, discount_rate: float) -> float:
    return price * (1 - discount_rate)

print(apply_discount(10000, 0.1))  # 9000.0
print(apply_discount(10000, 0.1))  # 9000.0 — always the same
```

## 단계별 실습

### Step 1: 순수 함수 식별하기

```python
import random
from datetime import datetime


# Pure: output determined by input alone
def add(a: int, b: int) -> int:
    return a + b

def full_name(first: str, last: str) -> str:
    return f"{first} {last}"


# Impure: depends on external state
def get_random_number() -> int:
    return random.randint(1, 100)  # different every time

def get_current_time() -> str:
    return datetime.now().isoformat()  # depends on clock


print(add(2, 3))          # always 5
print(full_name("John", "Doe"))  # always "John Doe"
print(get_random_number())       # varies
print(get_current_time())        # varies
```

순수 함수와 비순수 함수를 구분하는 가장 빠른 방법은 숨은 입력이 있는지 보는 것입니다. 시간, 난수, 전역 상태, 환경 변수, 파일 시스템이 숨어 들어오면 순수성은 깨집니다.

### Step 2: 부수효과의 종류

```python
# Side effect 1: modifying external variables
counter = 0

def increment() -> int:
    global counter
    counter += 1  # modifies external state
    return counter


# Side effect 2: IO operations
def save_to_file(data: str) -> None:
    with open("output.txt", "w") as f:
        f.write(data)  # modifies file system


# Side effect 3: mutating arguments
def add_item(items: list, item: str) -> list:
    items.append(item)  # mutates the input list
    return items


# Pure alternative: return a new list
def add_item_pure(items: list, item: str) -> list:
    return [*items, item]  # original untouched, new list created


original = ["a", "b"]
new_list = add_item_pure(original, "c")
print(original)  # ['a', 'b'] — unchanged
print(new_list)  # ['a', 'b', 'c']
```

실무에서 가장 흔한 부수효과는 전역 상태보다도 "인자로 받은 mutable 객체를 직접 수정하는 것"입니다. 호출한 쪽이 예상하지 못한 변경을 만나기 시작하면 디버깅 난도가 급격히 올라갑니다.

### Step 3: 순수 로직과 부수효과 분리

```python
from dataclasses import dataclass


@dataclass
class Order:
    items: list[str]
    quantities: list[int]
    prices: list[float]


# Pure functions: computation only
def calculate_subtotal(order: Order) -> float:
    return sum(q * p for q, p in zip(order.quantities, order.prices))

def calculate_tax(subtotal: float, rate: float) -> float:
    return round(subtotal * rate, 2)

def calculate_total(subtotal: float, tax: float) -> float:
    return subtotal + tax

def format_receipt(order: Order, subtotal: float, tax: float, total: float) -> str:
    lines = ["=== Receipt ==="]
    for item, qty, price in zip(order.items, order.quantities, order.prices):
        lines.append(f"  {item} x{qty}: ${qty * price:,.2f}")
    lines.append(f"  Subtotal: ${subtotal:,.2f}")
    lines.append(f"  Tax: ${tax:,.2f}")
    lines.append(f"  Total: ${total:,.2f}")
    return "\n".join(lines)


# Side effects: IO only
def print_receipt(order: Order, tax_rate: float) -> None:
    subtotal = calculate_subtotal(order)
    tax = calculate_tax(subtotal, tax_rate)
    total = calculate_total(subtotal, tax)
    receipt = format_receipt(order, subtotal, tax, total)
    print(receipt)  # the only side effect


order = Order(
    items=["Coffee", "Cake"],
    quantities=[2, 1],
    prices=[4.50, 6.00],
)
print_receipt(order, 0.1)
# === Receipt ===
#   Coffee x2: $9.00
#   Cake x1: $6.00
#   Subtotal: $15.00
#   Tax: $1.50
#   Total: $16.50
```

이 구조는 이후에도 반복해서 쓰게 됩니다. 계산은 순수 코어에 모으고, 출력과 저장은 가장 바깥에서 처리하는 방식입니다.

### Step 4: 순수 함수 테스트

```python
# Pure functions: no mocks needed
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    return round(weight_kg / (height_m ** 2), 1)

def classify_bmi(bmi: float) -> str:
    if bmi < 18.5:
        return "underweight"
    elif bmi < 25:
        return "normal"
    elif bmi < 30:
        return "overweight"
    return "obese"


# Tests are simple — just check input and output
assert calculate_bmi(70, 1.75) == 22.9
assert classify_bmi(22.9) == "normal"
assert classify_bmi(17.0) == "underweight"
assert classify_bmi(27.5) == "overweight"
print("All tests passed")
```

순수 함수가 좋은 이유를 한 문장으로 요약하면 이것입니다. 테스트를 위해 환경을 준비할 필요가 거의 없습니다. 입력을 주고 출력을 검증하면 끝입니다.

### Step 5: 참조 투명성 활용

```python
# Referential transparency: function calls can be replaced by their results
def square(x: int) -> int:
    return x * x

def sum_of_squares(a: int, b: int) -> int:
    return square(a) + square(b)


# Equivalent transformations are safe
result1 = sum_of_squares(3, 4)    # square(3) + square(4)
result2 = 9 + 16                   # replace calls with results
print(result1 == result2)  # True

# This property enables:
# 1. Safe caching (memoization)
# 2. Safe parallel execution
# 3. Safe refactoring
print(sum_of_squares(3, 4))  # 25
```

참조 투명성이 있으면 함수 호출을 값으로 치환해도 의미가 바뀌지 않습니다. 캐시가 안전해지고, 병렬 실행을 고민하기 쉬워지고, 리팩터링 리스크도 크게 줄어듭니다.

## 이 코드에서 주목할 점

- 순수 함수는 입력과 출력만으로 설명할 수 있어서 테스트가 단순합니다.
- 부수효과를 없애는 것이 아니라 프로그램 경계로 밀어내는 것이 핵심입니다.
- 참조 투명성은 캐싱과 병렬 처리의 안전성을 높여 줍니다.
- mutable 인자를 받을 때는 직접 수정하는 대신 새 값을 반환하는 편이 안전합니다.

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 전역 변수에 의존하는 함수 작성 | 환경에 따라 테스트 결과가 달라집니다 | 의존성을 인자로 전달합니다 |
| mutable 기본 인자 사용 | 호출 간 상태가 공유됩니다 | 기본값으로 `None`을 사용합니다 |
| 인자 리스트를 제자리에서 수정 | 호출자 데이터가 예기치 않게 바뀝니다 | 새 리스트를 만들어 반환합니다 |
| 순수 함수 안에서 `print` 호출 | IO 자체가 부수효과입니다 | 출력은 별도 계층에서 처리합니다 |
| 모든 함수를 순수하게 만들려 함 | 프로그램은 결국 IO가 필요합니다 | 순수 코어와 비순수 셸을 구분합니다 |

## 실무에서 이렇게 쓰입니다

- 비즈니스 규칙을 순수 함수로 작성해 단위 테스트를 단순화합니다.
- 데이터 변환 파이프라인을 순수 함수들로 구성합니다.
- `functools.lru_cache`로 순수 함수 캐싱을 안전하게 적용합니다.
- FastAPI 의존성 주입 안에서 검증 로직을 순수 함수로 분리합니다.
- Functional Core, Imperative Shell 구조를 시스템 기본 패턴으로 사용합니다.

## 현업에서는 이렇게 판단합니다

순수 함수를 쓴다는 것은 부수효과를 없애겠다는 선언이 아닙니다. 프로그램은 결국 저장하고 출력하고 네트워크와 통신해야 합니다. 중요한 것은 비즈니스 규칙이 그 혼잡한 영역에 끌려 들어가지 않게 막는 것입니다.

그래서 강한 팀들은 순수 함수로 두꺼운 코어를 만들고, 그 바깥에 얇은 IO 셸을 둡니다. 코어는 단위 테스트로 촘촘하게 검증하고, 셸은 통합 테스트로 확인합니다. Python에서 가장 실용적인 함수형 적용 방식도 바로 이 구조입니다.

## 체크리스트

- [ ] 순수 함수의 두 조건을 설명할 수 있다
- [ ] 코드에서 부수효과를 식별할 수 있다
- [ ] 인자를 직접 수정하지 않는 함수를 작성할 수 있다
- [ ] 순수 로직과 부수효과를 분리하는 패턴을 적용할 수 있다
- [ ] 순수 함수가 테스트를 단순하게 만드는 이유를 설명할 수 있다

## 연습 문제

1. 전역 설정에 의존하는 할인 계산기를 순수 함수로 리팩터링해 보세요.
2. 보고서 출력 함수를 `format_report`와 `print_report`로 나눠 보세요.
3. 리스트를 제자리에서 수정하는 함수를 새 리스트를 반환하는 버전으로 바꿔 보세요.

## 정리와 다음 글

순수 함수는 같은 입력에 항상 같은 출력을 반환하고, 함수 바깥 상태를 수정하지 않습니다. 부수효과를 경계로 밀어내면 코드는 예측 가능해지고 테스트하기 쉬워집니다. 다음 글에서는 순수 함수와 바로 이어지는 개념인 **immutable 데이터**를 다룹니다.

<!-- toc:begin -->
- [함수형 프로그래밍이란 무엇인가?](./01-what-is-fp.md)
- **순수 함수와 부수효과 (현재 글)**
- [immutable 데이터](./03-immutable-data.md)
- [고차 함수](./04-higher-order-functions.md)
- [map, filter, reduce](./05-map-filter-reduce.md)
- [클로저와 partial](./06-closure-and-partial.md)
- [재귀와 꼬리 호출](./07-recursion.md)
- [지연 평가와 제너레이터](./08-lazy-evaluation.md)
- [함수 합성과 파이프라인](./09-function-composition.md)
- [객체지향과 함수형의 균형](./10-oop-and-fp-balance.md)
<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Functional Programming HOWTO](https://docs.python.org/3/howto/functional.html)
- [Real Python — Pure Functions in Python](https://realpython.com/python-functional-programming/)
- [Functional Core, Imperative Shell — Gary Bernhardt](https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell)
- [Clean Code — Chapter 3: Functions](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)

Tags: Python, Functional Programming, 순수 함수, 부수효과, 테스트
