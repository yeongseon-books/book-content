---
series: functional-programming-101
episode: 2
title: "Functional Programming 101 (2/10): 순수 함수와 부수효과"
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

# Functional Programming 101 (2/10): 순수 함수와 부수효과

이 글은 Functional Programming 101 시리즈의 두 번째 글입니다.

함수형 프로그래밍을 이야기할 때 가장 먼저 제대로 잡아야 하는 개념이 순수 함수입니다. 같은 입력을 주면 항상 같은 결과가 나오는 함수, 그리고 함수 바깥의 상태를 바꾸지 않는 함수가 왜 중요한지 이해하면 이후에 나오는 불변성, 캐싱, 병렬 처리, 테스트 전략이 한 번에 연결됩니다.

현업에서는 모든 함수를 순수하게 만들 수는 없습니다. 파일을 저장해야 하고, 로그를 남겨야 하고, 데이터베이스도 호출해야 합니다. 그래서 핵심은 부수효과를 없애는 것이 아니라, 어디에 두고 어떻게 격리할지를 설계하는 것입니다.

## 먼저 던지는 질문

- 어떤 조건을 만족해야 함수를 순수 함수라고 부를 수 있을까요?
- 코드에서 부수효과는 어떤 형태로 나타나며 어떻게 식별할 수 있을까요?
- 순수한 계산과 IO를 분리하면 테스트는 어떻게 단순해질까요?

## 큰 그림

![Functional Programming 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/functional-programming-101/02/02-01-big-picture.ko.png)

*Functional Programming 101 2장 흐름 개요*

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


## 심화 앵커: 실무에서 바로 쓰는 함수형 패턴 모음

이 절은 앞선 개념을 한 번에 묶어 실무 코드로 옮기는 기준을 제시합니다. 공통 원칙은 단순합니다. 입력을 정규화하고, 순수 함수로 계산하고, 경계에서만 부수효과를 수행합니다. 이 구조가 잡히면 테스트 코드도 자연스럽게 단순해집니다.

### `functools`와 `itertools`를 함께 쓰는 파이프라인

```python
from functools import reduce
from itertools import islice, groupby
from operator import itemgetter

raw_orders = [
    {"order_id": "O-1", "store": "seoul", "amount": 12000, "status": "paid"},
    {"order_id": "O-2", "store": "seoul", "amount": 9000, "status": "cancelled"},
    {"order_id": "O-3", "store": "busan", "amount": 15000, "status": "paid"},
    {"order_id": "O-4", "store": "busan", "amount": 7000, "status": "paid"},
]

def normalize(order: dict) -> dict:
    return {
        **order,
        "store": order["store"].strip().lower(),
        "status": order["status"].strip().lower(),
    }

def is_paid(order: dict) -> bool:
    return order["status"] == "paid"

def with_fee(order: dict) -> dict:
    fee = int(order["amount"] * 0.03)
    return {**order, "fee": fee, "net": order["amount"] - fee}

normalized = map(normalize, raw_orders)
paid_only = filter(is_paid, normalized)
settled = list(map(with_fee, paid_only))

# groupby는 key 정렬이 선행되어야 동작이 안정적입니다.
settled_sorted = sorted(settled, key=itemgetter("store"))
report = {
    store: reduce(
        lambda acc, o: {
            "orders": acc["orders"] + 1,
            "gross": acc["gross"] + o["amount"],
            "fee": acc["fee"] + o["fee"],
            "net": acc["net"] + o["net"],
        },
        orders,
        {"orders": 0, "gross": 0, "fee": 0, "net": 0},
    )
    for store, orders in groupby(settled_sorted, key=itemgetter("store"))
}

print(report)
# {
#   'busan': {'orders': 2, 'gross': 22000, 'fee': 660, 'net': 21340},
#   'seoul': {'orders': 1, 'gross': 12000, 'fee': 360, 'net': 11640}
# }
```

### 순수 함수 리팩터링 전후 비교

```python
# before: 계산과 로그 출력이 섞인 형태

def score_user_before(user: dict) -> int:
    base = user["purchases"] * 10
    if user["vip"]:
        base += 30
    print(f"[DEBUG] scored {user['id']} => {base}")
    return base

# after: 계산은 순수 함수, 출력은 외부 경계

def score_user(user: dict) -> int:
    base = user["purchases"] * 10
    bonus = 30 if user["vip"] else 0
    return base + bonus

def score_and_log(user: dict) -> int:
    score = score_user(user)
    print(f"[DEBUG] scored {user['id']} => {score}")
    return score
```

핵심은 `before`가 틀렸다는 뜻이 아니라, 테스트 비용이 높아진다는 점입니다. `score_user()`는 입력과 출력만 검증하면 되기 때문에 fixture나 mock 없이 단위 테스트를 만들 수 있습니다.

### 불변 데이터 구조 선택 기준

| 상황 | 권장 타입 | 이유 |
|---|---|---|
| 위치 좌표, 버전 쌍 | `tuple[int, int]` | 해시 가능, 키로 사용 가능 |
| 권한 집합 | `frozenset[str]` | 중복 제거 + 불변 |
| 설정 객체 | `@dataclass(frozen=True)` | 타입 명시 + 불변 업데이트 용이 |
| 레코드 스냅샷 | `NamedTuple` | 가볍고 필드 접근이 명확 |

```python
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class AppConfig:
    host: str
    port: int
    debug: bool

base = AppConfig(host="localhost", port=8000, debug=False)
debug_cfg = replace(base, debug=True)

print(base)      # AppConfig(host='localhost', port=8000, debug=False)
print(debug_cfg) # AppConfig(host='localhost', port=8000, debug=True)
```

### 재귀 호출 스택을 시각화하며 검증하기

```python
def sum_nested(values, depth: int = 0) -> int:
    indent = "  " * depth
    print(f"{indent}sum_nested({values})")

    if isinstance(values, int):
        print(f"{indent}-> int {values}")
        return values

    total = 0
    for item in values:
        total += sum_nested(item, depth + 1)

    print(f"{indent}-> total {total}")
    return total

nested = [1, [2, [3, 4], 5], [6, 7]]
print(sum_nested(nested))
```

재귀가 안전한지 확인할 때는 두 가지를 함께 봅니다. 종료 조건이 모든 경로에서 도달 가능한지, 그리고 입력 크기가 커졌을 때 반복으로 전환해야 하는지입니다.

### Python에서 구현하는 monad-like 패턴

엄밀한 수학적 모나드 구현이 아니라, 에러 전파를 일관되게 다루는 실전 패턴입니다.

```python
from dataclasses import dataclass
from typing import Generic, TypeVar, Callable

T = TypeVar("T")
E = TypeVar("E")
U = TypeVar("U")

@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T

@dataclass(frozen=True)
class Err(Generic[E]):
    error: E

Result = Ok[T] | Err[E]

def bind(result: Result[T, E], fn: Callable[[T], Result[U, E]]) -> Result[U, E]:
    if isinstance(result, Err):
        return result
    return fn(result.value)

def parse_int(text: str) -> Result[int, str]:
    return Ok(int(text)) if text.isdigit() else Err("not a digit")

def positive(n: int) -> Result[int, str]:
    return Ok(n) if n > 0 else Err("must be positive")

def reciprocal(n: int) -> Result[float, str]:
    return Err("division by zero") if n == 0 else Ok(1 / n)

r1 = bind(bind(parse_int("8"), positive), reciprocal)
r2 = bind(bind(parse_int("x"), positive), reciprocal)

print(r1)  # Ok(value=0.125)
print(r2)  # Err(error='not a digit')
```

이 패턴의 장점은 `try/except`를 중첩하지 않고도 실패 경로를 동일한 타입으로 유지할 수 있다는 점입니다.

### 속성 기반 테스트 예시 (`hypothesis`)

```python
# pip install hypothesis
from hypothesis import given, strategies as st

def normalize_email(email: str) -> str:
    return email.strip().lower()

@given(st.text())
def test_normalize_email_idempotent(raw: str) -> None:
    once = normalize_email(raw)
    twice = normalize_email(once)
    assert once == twice

@given(st.lists(st.integers(min_value=-10_000, max_value=10_000), max_size=100))
def test_sum_matches_builtin(xs: list[int]) -> None:
    assert sum(xs) == __builtins__["sum"](xs)
```

예제 기반 테스트는 특정 입력에 집중하고, 속성 기반 테스트는 함수의 보편적 성질을 검증합니다. 둘을 함께 쓰면 경계 조건 누락을 크게 줄일 수 있습니다.

### 운영 경계에서의 구성 원칙

- 계산 함수는 가능한 한 `print`, 파일 IO, 네트워크 호출을 포함하지 않습니다.
- API 핸들러나 CLI 엔트리포인트에서만 부수효과를 수행합니다.
- 파이프라인 단계마다 입력/출력 타입을 문서화해 연결 오류를 줄입니다.
- 불변 객체를 기본값으로 두고, 변경이 필요할 때만 새 객체를 만듭니다.

이 원칙을 지키면 코드 리뷰에서 "무엇이 바뀌었는가"가 아니라 "어디에서 부수효과가 발생하는가"를 빠르게 확인할 수 있습니다.



## 검증 시나리오: 경계 조건을 먼저 잠그기

실무에서 함수형 스타일이 유지되는 팀은 구현보다 먼저 검증 포인트를 고정합니다. 입력 경계, 빈 컬렉션, 정렬 안정성, 타입 변환 실패를 먼저 적어 두면 리팩터링 과정에서도 동작이 흔들리지 않습니다.

```python
from functools import reduce

def pipeline(values: list[int]) -> dict[str, int]:
    filtered = [v for v in values if v >= 0]
    squared = [v * v for v in filtered]
    total = reduce(lambda acc, x: acc + x, squared, 0)
    return {
        "count": len(squared),
        "total": total,
        "max": max(squared) if squared else 0,
    }

# 경계 조건 검증
assert pipeline([]) == {"count": 0, "total": 0, "max": 0}
assert pipeline([-3, -1]) == {"count": 0, "total": 0, "max": 0}
assert pipeline([0, 2, 3]) == {"count": 3, "total": 13, "max": 9}

print("Pass")
```

또한 지연 평가를 사용할 때는 소비 시점을 테스트에 명시해 두는 편이 좋습니다. generator는 한 번 소비하면 비어야 정상이며, 이 성질이 깨지면 중간 단계에서 의도치 않은 materialize가 발생했을 가능성이 큽니다.

```python
from itertools import islice

def naturals():
    n = 0
    while True:
        yield n
        n += 1

stream = naturals()
first_five = list(islice(stream, 5))
next_three = list(islice(stream, 3))

assert first_five == [0, 1, 2, 3, 4]
assert next_three == [5, 6, 7]
print("Pass")
```

이런 검증 코드는 예제 코드가 아니라 운영 안전장치입니다. 새 규칙을 추가할 때도 기존 성질이 유지되는지 빠르게 확인할 수 있습니다.



## 리뷰 포인트: 코드 리뷰에서 바로 확인할 항목

함수형 스타일을 적용한 코드 리뷰에서는 다음 네 가지를 빠르게 확인합니다. 첫째, 계산 함수가 외부 상태를 직접 읽거나 쓰지 않는지 확인합니다. 둘째, mutable 인자를 제자리에서 수정하지 않는지 확인합니다. 셋째, 파이프라인 단계의 입력과 출력 타입이 자연스럽게 연결되는지 확인합니다. 넷째, 실패 경로가 값으로 표현되는지 확인합니다.

```python
def reviewer_checklist() -> list[str]:
    return [
        "pure-core",
        "immutable-update",
        "typed-boundary",
        "explicit-failure-path",
    ]

assert len(reviewer_checklist()) == 4
print("Pass")
```

이 항목을 PR 템플릿에 고정해 두면 스타일 논쟁보다 설계 품질을 빠르게 맞출 수 있습니다.


## 처음 질문으로 돌아가기

- **어떤 조건을 만족해야 함수를 순수 함수라고 부를 수 있을까요?**
  - 본문의 기준은 순수 함수와 부수효과를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **코드에서 부수효과는 어떤 형태로 나타나며 어떻게 식별할 수 있을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **순수한 계산과 IO를 분리하면 테스트는 어떻게 단순해질까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Functional Programming 101 (1/10): 함수형 프로그래밍이란 무엇인가?](./01-what-is-fp.md)
- **순수 함수와 부수효과 (현재 글)**
- immutable 데이터 (예정)
- 고차 함수 (예정)
- map, filter, reduce (예정)
- 클로저와 partial (예정)
- 재귀와 꼬리 호출 (예정)
- 지연 평가와 제너레이터 (예정)
- 함수 합성과 파이프라인 (예정)
- 객체지향과 함수형의 균형 (예정)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Functional Programming HOWTO](https://docs.python.org/3/howto/functional.html)
- [Real Python — Pure Functions in Python](https://realpython.com/python-functional-programming/)
- [Functional Core, Imperative Shell — Gary Bernhardt](https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell)
- [Clean Code — Chapter 3: Functions](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/functional-programming-101/ko)
Tags: Python, Functional Programming, 순수 함수, 부수효과, 테스트
