---
series: functional-programming-101
episode: 2
title: 순수 함수와 부수효과
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
  - 순수 함수
  - 부수효과
  - 테스트
seo_description: 순수 함수의 정의와 부수효과를 분리하는 설계 패턴을 다룹니다.
last_reviewed: '2026-05-04'
---

# 순수 함수와 부수효과

> Functional Programming 101 시리즈 (2/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 같은 입력에 항상 같은 출력을 보장하는 함수를 어떻게 작성할까요?

> 순수 함수는 외부 상태에 의존하지 않고, 외부 상태를 변경하지 않습니다. 부수효과를 분리하면 테스트가 쉬워지고 코드의 예측 가능성이 높아집니다. 이 글에서는 순수 함수의 정의, 식별 방법, 부수효과 관리 패턴을 다룹니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 순수 함수의 두 가지 조건
- 부수효과의 종류와 식별 방법
- 순수 로직과 부수효과를 분리하는 패턴
- 순수 함수가 테스트를 단순화하는 이유

## 왜 중요한가

버그의 상당수는 예상치 못한 상태 변경에서 발생합니다. 순수 함수는 입력과 출력만으로 동작이 결정되므로 추론이 쉽고 테스트가 간단합니다.

> 순수 함수 = 예측 가능한 코드의 기본 단위

실무에서 모든 함수를 순수하게 만들 수는 없지만, 비즈니스 로직을 순수 함수로 작성하고 IO를 경계에 몰아넣는 아키텍처는 유지보수 비용을 크게 줄여줍니다.

## 핵심 개념 잡기

> 순수 함수 판별 흐름

```
함수 f(x) 호출
  │
  ├─ 같은 x에 항상 같은 결과? ── No ──> 비순수
  │          │
  │         Yes
  │          │
  ├─ 외부 상태를 변경하는가? ── Yes ──> 비순수
  │          │
  │         No
  │          │
  └─ 순수 함수!
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 순수 함수(pure function) | 참조 투명성을 가지며 부수효과가 없는 함수입니다 |
| 부수효과(side effect) | 함수 외부의 상태를 변경하는 모든 동작입니다 |
| 참조 투명성(referential transparency) | 함수 호출을 그 결과값으로 대체할 수 있는 성질입니다 |
| 결정론적(deterministic) | 같은 입력에 항상 같은 출력을 반환하는 성질입니다 |
| 멱등성(idempotent) | 여러 번 실행해도 결과가 동일한 성질입니다 |

## Before / After

부수효과가 있는 함수를 순수 함수로 전환합니다.

```python
# before: 전역 상태에 의존하는 비순수 함수
discount_rate = 0.1

def apply_discount(price: float) -> float:
    return price * (1 - discount_rate)

print(apply_discount(10000))  # 9000.0
discount_rate = 0.2
print(apply_discount(10000))  # 8000.0 — 같은 입력, 다른 결과!
```

```python
# after: 순수 함수 — 모든 의존성을 인자로 받음
def apply_discount(price: float, discount_rate: float) -> float:
    return price * (1 - discount_rate)

print(apply_discount(10000, 0.1))  # 9000.0
print(apply_discount(10000, 0.1))  # 9000.0 — 항상 같은 결과
```

## 단계별 실습

### Step 1: 순수 함수 식별

```python
import random
from datetime import datetime


# 순수 함수: 입력만으로 결과가 결정됨
def add(a: int, b: int) -> int:
    return a + b

def full_name(first: str, last: str) -> str:
    return f"{first} {last}"


# 비순수 함수: 외부 상태에 의존
def get_random_number() -> int:
    return random.randint(1, 100)  # 매번 다른 결과

def get_current_time() -> str:
    return datetime.now().isoformat()  # 시간에 의존


print(add(2, 3))          # 항상 5
print(full_name("김", "철수"))  # 항상 "김 철수"
print(get_random_number())     # 매번 다름
print(get_current_time())      # 매번 다름
```

### Step 2: 부수효과의 종류

```python
# 부수효과 1: 외부 변수 변경
counter = 0

def increment() -> int:
    global counter
    counter += 1  # 외부 상태 변경
    return counter


# 부수효과 2: IO 작업
def save_to_file(data: str) -> None:
    with open("output.txt", "w") as f:
        f.write(data)  # 파일 시스템 변경


# 부수효과 3: 인자 변경 (mutable)
def add_item(items: list, item: str) -> list:
    items.append(item)  # 입력 리스트를 변경
    return items


# 순수 대안: 새 리스트 반환
def add_item_pure(items: list, item: str) -> list:
    return [*items, item]  # 원본 유지, 새 리스트 생성


original = ["a", "b"]
new_list = add_item_pure(original, "c")
print(original)  # ['a', 'b'] — 원본 변경 없음
print(new_list)  # ['a', 'b', 'c']
```

### Step 3: 순수 로직과 부수효과 분리

```python
from dataclasses import dataclass


@dataclass
class Order:
    items: list[str]
    quantities: list[int]
    prices: list[float]


# 순수 함수: 계산만 담당
def calculate_subtotal(order: Order) -> float:
    return sum(q * p for q, p in zip(order.quantities, order.prices))

def calculate_tax(subtotal: float, rate: float) -> float:
    return round(subtotal * rate, 2)

def calculate_total(subtotal: float, tax: float) -> float:
    return subtotal + tax

def format_receipt(order: Order, subtotal: float, tax: float, total: float) -> str:
    lines = ["=== 영수증 ==="]
    for item, qty, price in zip(order.items, order.quantities, order.prices):
        lines.append(f"  {item} x{qty}: {qty * price:,.0f}원")
    lines.append(f"  소계: {subtotal:,.0f}원")
    lines.append(f"  세금: {tax:,.0f}원")
    lines.append(f"  합계: {total:,.0f}원")
    return "\n".join(lines)


# 부수효과: IO만 담당
def print_receipt(order: Order, tax_rate: float) -> None:
    subtotal = calculate_subtotal(order)
    tax = calculate_tax(subtotal, tax_rate)
    total = calculate_total(subtotal, tax)
    receipt = format_receipt(order, subtotal, tax, total)
    print(receipt)  # 유일한 부수효과


order = Order(
    items=["커피", "케이크"],
    quantities=[2, 1],
    prices=[4500.0, 6000.0],
)
print_receipt(order, 0.1)
# === 영수증 ===
#   커피 x2: 9,000원
#   케이크 x1: 6,000원
#   소계: 15,000원
#   세금: 1,500원
#   합계: 16,500원
```

### Step 4: 테스트 용이성 비교

```python
# 순수 함수: mock 없이 테스트 가능
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    return round(weight_kg / (height_m ** 2), 1)

def classify_bmi(bmi: float) -> str:
    if bmi < 18.5:
        return "저체중"
    elif bmi < 25:
        return "정상"
    elif bmi < 30:
        return "과체중"
    return "비만"


# 테스트가 단순 — 입력과 출력만 확인
assert calculate_bmi(70, 1.75) == 22.9
assert classify_bmi(22.9) == "정상"
assert classify_bmi(17.0) == "저체중"
assert classify_bmi(27.5) == "과체중"
print("모든 테스트 통과")
```

### Step 5: 참조 투명성 활용

```python
# 참조 투명성: 함수 호출을 결과값으로 대체 가능
def square(x: int) -> int:
    return x * x

def sum_of_squares(a: int, b: int) -> int:
    return square(a) + square(b)


# 동치 변환이 가능
result1 = sum_of_squares(3, 4)    # square(3) + square(4)
result2 = 9 + 16                   # 함수 호출을 결과로 대체
print(result1 == result2)  # True

# 이런 성질 덕분에:
# 1. 캐싱(memoization)이 안전
# 2. 병렬 실행이 안전
# 3. 리팩터링이 안전
print(sum_of_squares(3, 4))  # 25
```

## 이 코드에서 주목할 점

- 순수 함수는 입력과 출력만으로 동작이 결정되어 테스트가 단순합니다
- 부수효과는 제거하는 것이 아니라 경계로 밀어내는 것입니다
- 참조 투명성은 캐싱과 병렬 처리를 안전하게 만들어줍니다
- mutable 인자를 받는 함수는 새 값을 반환하는 방식으로 개선할 수 있습니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 전역 변수에 의존하는 함수 | 테스트 결과가 환경에 따라 달라집니다 | 의존성을 인자로 전달합니다 |
| mutable 기본값 사용 | 호출 간에 상태가 공유됩니다 | `None`을 기본값으로 사용합니다 |
| 인자로 받은 리스트를 직접 변경 | 호출자의 데이터가 변합니다 | 새 리스트를 생성하여 반환합니다 |
| 순수 함수 안에서 print 호출 | IO는 부수효과입니다 | 로깅은 별도 레이어에서 처리합니다 |
| 모든 함수를 순수하게 만들려 함 | IO 없이는 프로그램이 동작하지 않습니다 | 순수 핵심 + 비순수 경계를 구분합니다 |

## 실무에서 이렇게 쓰입니다

- 비즈니스 규칙을 순수 함수로 작성하여 단위 테스트를 단순화합니다
- 데이터 변환 파이프라인을 순수 함수로 구성합니다
- 순수 함수는 `functools.lru_cache`로 안전하게 캐싱합니다
- FastAPI 의존성 주입에서 순수 함수로 검증 로직을 분리합니다
- 순수 핵심(pure core) + 비순수 셸(impure shell) 아키텍처를 적용합니다

## 현업 개발자는 이렇게 생각합니다

"순수 함수를 쓴다"는 것은 모든 부수효과를 제거한다는 뜻이 아닙니다. 프로그램은 외부와 소통해야 하므로 IO는 불가피합니다. 핵심은 비즈니스 로직을 순수하게 유지하고, IO를 프로그램의 경계로 밀어내는 것입니다.

이 패턴을 "Functional Core, Imperative Shell"이라 부릅니다. 순수 함수로 된 핵심을 두꺼운 테스트로 감싸고, 얇은 IO 셸은 통합 테스트로 검증하는 구조가 실무에서 가장 효과적입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **결정성** — 동일 입력 동일 출력이라는 계약을 코드로 강제합니다.
- **부수효과 표시** — I/O 함수는 이름과 위치로 분명히 드러냅니다.
- **로깅 위치** — 코어 함수 내부 로깅은 순수성을 깨뜨립니다.
- **난수·시간** — 시드·시간을 인자로 받아 결정성을 회복합니다.
- **테스트 자산화** — 순수 함수 테스트는 회귀 자산으로 가장 유리합니다.

## 체크리스트

- [ ] 순수 함수의 두 가지 조건을 설명할 수 있다
- [ ] 코드에서 부수효과를 식별할 수 있다
- [ ] mutable 인자를 변경하지 않는 함수를 작성할 수 있다
- [ ] 순수 로직과 부수효과를 분리하는 패턴을 적용할 수 있다
- [ ] 순수 함수의 테스트 이점을 설명할 수 있다

## 연습 문제

1. 전역 설정에 의존하는 할인 계산 함수를 순수 함수로 리팩터링하세요.
2. `format_report`(순수)와 `print_report`(부수효과)로 보고서 출력을 분리하세요.
3. mutable 리스트를 직접 변경하는 함수를 새 리스트를 반환하도록 개선하세요.

## 정리 및 다음 글 안내

순수 함수는 같은 입력에 항상 같은 출력을 보장하고, 외부 상태를 변경하지 않습니다. 부수효과를 경계로 밀어내면 테스트 가능하고 예측 가능한 코드를 작성할 수 있습니다. 다음 글에서는 순수 함수와 밀접한 **immutable 데이터**를 다룹니다.

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
