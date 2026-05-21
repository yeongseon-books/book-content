---
series: functional-programming-101
episode: 4
title: "Functional Programming 101 (4/10): 고차 함수"
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
  - 고차 함수
  - 콜백
  - 데코레이터
seo_description: 함수를 받고 반환하는 고차 함수의 원리와 Python 실전 패턴을 설명합니다.
last_reviewed: '2026-05-12'
---

# Functional Programming 101 (4/10): 고차 함수

이 글은 Functional Programming 101 시리즈의 네 번째 글입니다.

고차 함수는 이름만 들으면 추상적인 개념처럼 느껴집니다. 하지만 Python 개발자는 이미 매일 쓰고 있습니다. `sorted(key=...)`, `map(func, ...)`, 데코레이터, 콜백 등록 모두 함수 자체를 값처럼 전달한다는 점에서 고차 함수입니다.

중요한 이유는 단순합니다. 코드에서 반복되는 것은 종종 데이터가 아니라 "동작의 뼈대"이기 때문입니다. 변하는 부분을 함수로 분리해 인자로 넘기거나, 설정이 들어간 새 함수를 만들어 반환하면 중복을 줄이면서도 유연성을 확보할 수 있습니다.

## 먼저 던지는 질문

- 고차 함수는 어떤 두 형태로 나타날까요?
- `sorted`, `map`, `filter`는 왜 고차 함수의 대표 예시일까요?
- 함수를 반환하는 팩토리 패턴은 어떤 상황에서 유용할까요?

## 큰 그림

![Functional Programming 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/functional-programming-101/04/04-01-big-picture.ko.png)

*Functional Programming 101 4장 흐름 개요*

## 왜 중요한가

반복 패턴을 함수로 추출하다 보면 어느 시점부터는 로직의 뼈대는 같고, 실제로 달라지는 것은 조건식이나 후처리 방식뿐인 경우가 많습니다. 이때 동작을 함수로 받아들이면 전략 패턴을 클래스 없이도 간결하게 구현할 수 있습니다.

또한 Python 생태계 자체가 고차 함수에 크게 기대고 있습니다. 정렬 기준, 검증 콜백, 미들웨어, 데코레이터, 의존성 주입까지 모두 같은 원리로 연결됩니다. 개념을 이해하고 쓰는 것과, 그냥 관용구로 외워서 쓰는 것 사이에는 유지보수 품질 차이가 큽니다.

## 개념 개요

> 고차 함수는 크게 두 가지입니다. 함수를 인자로 받거나, 함수를 반환합니다.

```text
Form 1: Accept a function          Form 2: Return a function
─────────────────────              ─────────────────
sorted(data, key=func)             def make_adder(n):
map(func, data)                        return lambda x: x + n
filter(func, data)                 adder = make_adder(5)
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 고차 함수(higher-order function) | 함수를 인자로 받거나 함수를 반환하는 함수입니다 |
| 콜백(callback) | 다른 함수에 인자로 전달되는 함수입니다 |
| 일급 객체(first-class object) | 변수 할당, 인자 전달, 반환이 가능한 객체입니다 |
| 팩토리 함수(factory function) | 새로운 함수나 객체를 만들어 반환하는 함수입니다 |
| 데코레이터(decorator) | 함수를 받아 기능이 추가된 새 함수를 반환하는 고차 함수입니다 |

## Before / After

비슷한 함수가 계속 늘어나는 신호는 대개 "변하는 조건만 분리하라"는 뜻입니다.

```python
# before: three functions with nearly identical logic
def get_adults(people: list[dict]) -> list[dict]:
    result = []
    for p in people:
        if p["age"] >= 18:
            result.append(p)
    return result

def get_seniors(people: list[dict]) -> list[dict]:
    result = []
    for p in people:
        if p["age"] >= 65:
            result.append(p)
    return result
```

```python
# after: higher-order function with condition as argument
from collections.abc import Callable

def filter_people(
    people: list[dict],
    predicate: Callable[[dict], bool],
) -> list[dict]:
    return [p for p in people if predicate(p)]

adults = filter_people(people, lambda p: p["age"] >= 18)
seniors = filter_people(people, lambda p: p["age"] >= 65)
```

## 단계별 실습

### Step 1: 함수를 인자로 전달하기

```python
from collections.abc import Callable

def apply_operation(
    values: list[int],
    operation: Callable[[int], int],
) -> list[int]:
    return [operation(v) for v in values]

numbers = [1, 2, 3, 4, 5]

doubled = apply_operation(numbers, lambda x: x * 2)
print(doubled)  # [2, 4, 6, 8, 10]

squared = apply_operation(numbers, lambda x: x ** 2)
print(squared)  # [1, 4, 9, 16, 25]

def negate(x: int) -> int:
    return -x

negated = apply_operation(numbers, negate)
print(negated)  # [-1, -2, -3, -4, -5]
```

같은 순회 구조 안에서 어떤 연산을 할지만 바뀌는 경우, 고차 함수는 중복을 제거하면서 의도를 더 선명하게 만듭니다.

### Step 2: sorted의 key 파라미터 이해하기

```python
from dataclasses import dataclass

@dataclass
class Student:
    name: str
    score: int
    grade: int

students = [
    Student("Alice", 85, 3),
    Student("Bob", 92, 2),
    Student("Charlie", 78, 3),
    Student("Diana", 95, 1),
]

# sort by score
by_score = sorted(students, key=lambda s: s.score, reverse=True)
for s in by_score:
    print(f"{s.name}: {s.score}")
# Diana: 95
# Bob: 92
# Alice: 85
# Charlie: 78

# multi-key sort: grade then score
by_grade_score = sorted(students, key=lambda s: (s.grade, -s.score))
for s in by_grade_score:
    print(f"  Grade {s.grade} {s.name}: {s.score}")
#   Grade 1 Diana: 95
#   Grade 2 Bob: 92
#   Grade 3 Alice: 85
#   Grade 3 Charlie: 78
```

`sorted(key=...)`는 실무에서 가장 많이 만나는 고차 함수입니다. 정렬 알고리즘을 다시 쓰는 대신, "무엇을 기준으로 정렬할지"만 함수로 넘기면 됩니다.

### Step 3: 함수를 반환하는 팩토리 함수

```python
from collections.abc import Callable

def make_multiplier(factor: int) -> Callable[[int], int]:
    """Creates a multiplier function."""
    def multiplier(x: int) -> int:
        return x * factor
    return multiplier

def make_validator(min_val: float, max_val: float) -> Callable[[float], bool]:
    """Creates a range validation function."""
    def validate(value: float) -> bool:
        return min_val <= value <= max_val
    return validate

double = make_multiplier(2)
triple = make_multiplier(3)
print(double(5))  # 10
print(triple(5))  # 15

is_valid_score = make_validator(0, 100)
is_valid_rate = make_validator(0.0, 1.0)
print(is_valid_score(85))   # True
print(is_valid_score(150))  # False
print(is_valid_rate(0.75))  # True
```

함수를 반환하는 패턴은 설정이 들어간 동작을 만드는 데 강력합니다. "지금 당장 값을 계산하는 함수"가 아니라 "나중에 호출할 규칙 자체"를 생성하는 셈입니다.

### Step 4: 데코레이터와 고차 함수

```python
import time
from collections.abc import Callable
from typing import Any
from functools import wraps

def timer(func: Callable) -> Callable:
    """A decorator that measures execution time."""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__}: {elapsed:.4f}s")
        return result
    return wrapper

def retry(max_attempts: int) -> Callable:
    """Creates a retry decorator."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise
                    print(f"  Attempt {attempt} failed: {e}")
            return None
        return wrapper
    return decorator

@timer
def slow_sum(n: int) -> int:
    return sum(range(n))

@retry(max_attempts=3)
def unstable_operation() -> str:
    import random
    if random.random() < 0.7:
        raise ValueError("transient error")
    return "success"

result = slow_sum(1_000_000)
print(f"Result: {result}")
# slow_sum: 0.0234s
# Result: 499999500000
```

데코레이터는 결국 함수를 받아 함수를 돌려주는 고차 함수입니다. 이 관점을 잡으면 `@wraps`가 왜 필요한지, 재시도·로깅·권한 검사 같은 횡단 관심사를 왜 데코레이터로 분리하는지 자연스럽게 이해됩니다.

### Step 5: 고차 함수로 파이프라인 만들기

```python
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")

def compose(*funcs: Callable) -> Callable:
    """Composes functions from right to left."""
    def composed(value):
        result = value
        for func in reversed(funcs):
            result = func(result)
        return result
    return composed

def strip_whitespace(text: str) -> str:
    return text.strip()

def to_lower(text: str) -> str:
    return text.lower()

def replace_spaces(text: str) -> str:
    return text.replace(" ", "-")

def truncate_20(text: str) -> str:
    return text[:20]

slugify = compose(truncate_20, replace_spaces, to_lower, strip_whitespace)

print(slugify("  Hello World Python  "))  # hello-world-python
print(slugify("  Functional Programming Guide  "))  # functional-programmi
```

고차 함수는 파이프라인과도 자연스럽게 이어집니다. 작은 변환 함수를 조합하는 방식은 이후 함수 합성 글에서 더 확장됩니다.

## 이 코드에서 주목할 점

- 고차 함수는 변하는 동작을 인자로 받아 중복을 제거합니다.
- 팩토리 함수는 설정이 다른 함수를 동적으로 만들어 냅니다.
- 데코레이터는 고차 함수의 문법 설탕이며 `@wraps`는 메타데이터 보존에 중요합니다.
- 함수 합성은 작은 함수를 묶어 더 큰 변환을 만드는 대표 패턴입니다.

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 복잡한 `lambda`를 남발함 | 디버깅과 리뷰가 어려워집니다 | 이름 있는 함수로 분리합니다 |
| `@wraps`를 빼먹음 | 함수 이름과 docstring이 사라집니다 | 데코레이터에 항상 `@wraps`를 넣습니다 |
| 고차 함수 중첩이 과도함 | 가독성이 급격히 떨어집니다 | 두 단계가 넘으면 중간 변수를 둡니다 |
| 타입 힌트를 생략함 | `Callable` 시그니처가 अस्पष्ट해집니다 | `Callable[[int], str]`처럼 명시합니다 |
| 부수효과 있는 콜백을 넘김 | 실행 순서와 상태에 민감해집니다 | 가능하면 순수 함수 콜백을 사용합니다 |

## 실무에서 이렇게 쓰입니다

- FastAPI의 `Depends()`는 의존성 주입을 고차 함수 패턴으로 활용합니다.
- `sorted(key=...)`, `min(key=...)`, `max(key=...)`는 모두 고차 함수입니다.
- 로깅, 인증, 캐싱 데코레이터를 같은 구조로 구현합니다.
- 이벤트 핸들러 등록은 콜백 패턴을 사용합니다.
- 테스트 픽스처 생성에 팩토리 함수를 활용합니다.

## 현업에서는 이렇게 판단합니다

고차 함수의 핵심 가치는 추상화입니다. 반복되는 흐름에서 "변하는 부분"만 함수로 끌어내면 클래스 계층 없이도 전략을 교체할 수 있습니다. Python에서 데코레이터와 정렬 키 함수가 널리 쓰이는 이유도 결국 같은 추상화 비용 대비 효과가 크기 때문입니다.

다만 추상화가 항상 정답은 아닙니다. 정말로 함수 인자를 받아야 하는지, 단순한 코드를 괜히 일반화하고 있지는 않은지 계속 점검해야 합니다. 좋은 고차 함수는 중복을 줄이지만, 나쁜 고차 함수는 읽는 사람의 인지 부하만 늘립니다.

## 체크리스트

- [ ] 고차 함수의 두 형태를 설명할 수 있다
- [ ] `sorted(key=...)`에 적절한 함수를 전달할 수 있다
- [ ] 팩토리 함수를 작성해 함수를 동적으로 생성할 수 있다
- [ ] 데코레이터가 고차 함수라는 점을 이해하고 간단한 데코레이터를 작성할 수 있다
- [ ] 고차 함수로 중복 로직을 줄일 수 있다

## 연습 문제

1. `make_formatter(format_str)` 함수를 만들어 숫자 포맷 함수를 동적으로 생성해 보세요.
2. 실행 시간, 호출 횟수, 결과를 기록하는 `@trace` 데코레이터를 작성해 보세요.
3. `filter_by(predicate)`, `sort_by(key)`, `transform(func)`를 조합한 데이터 처리 파이프라인을 구현해 보세요.

## 정리와 다음 글

고차 함수는 함수를 인자로 받거나 반환하면서 동작을 추상화합니다. 팩토리 패턴과 데코레이터는 가장 자주 만나는 응용 형태입니다. 다음 글에서는 이 개념이 가장 직접적으로 드러나는 **map, filter, reduce**를 다룹니다.


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

- **고차 함수는 어떤 두 형태로 나타날까요?**
  - 본문의 기준은 고차 함수를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **`sorted`, `map`, `filter`는 왜 고차 함수의 대표 예시일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **함수를 반환하는 팩토리 패턴은 어떤 상황에서 유용할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Functional Programming 101 (1/10): 함수형 프로그래밍이란 무엇인가?](./01-what-is-fp.md)
- [Functional Programming 101 (2/10): 순수 함수와 부수효과](./02-pure-functions.md)
- [Functional Programming 101 (3/10): immutable 데이터](./03-immutable-data.md)
- **고차 함수 (현재 글)**
- map, filter, reduce (예정)
- 클로저와 partial (예정)
- 재귀와 꼬리 호출 (예정)
- 지연 평가와 제너레이터 (예정)
- 함수 합성과 파이프라인 (예정)
- 객체지향과 함수형의 균형 (예정)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Functional Programming HOWTO](https://docs.python.org/3/howto/functional.html)
- [Real Python — Primer on Python Decorators](https://realpython.com/primer-on-python-decorators/)
- [Fluent Python — Chapter 7: Functions as First-Class Objects](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)
- [Python 공식 문서 — functools](https://docs.python.org/3/library/functools.html)

Tags: Python, Functional Programming, 고차 함수, 콜백, 데코레이터
