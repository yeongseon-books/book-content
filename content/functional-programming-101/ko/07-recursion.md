---
series: functional-programming-101
episode: 7
title: "Functional Programming 101 (7/10): 재귀와 꼬리 호출"
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
  - 재귀
  - 꼬리 호출
  - 스택
seo_description: 재귀의 종료 조건 설계와 메모이제이션을 학습하고, Python 스택 한계를 고려해 반복으로 전환하거나 트리 탐색에 적용하는 기준을 제시합니다.
last_reviewed: '2026-05-12'
---

# Functional Programming 101 (7/10): 재귀와 꼬리 호출

이 글은 Functional Programming 101 시리즈의 일곱 번째 글입니다.

재귀는 반복문 없이 문제를 풀게 해 주는 기법이지만, 단순히 "함수가 자기 자신을 다시 부른다" 정도로만 이해하면 실무에서는 금방 한계를 만납니다. 중요한 것은 언제 재귀가 구조를 더 잘 드러내는지, 그리고 Python에서는 어디서부터 반복으로 바꿔야 하는지를 아는 것입니다.

특히 Python은 꼬리 호출 최적화(TCO)를 지원하지 않습니다. 그래서 함수형 언어에서 자연스럽게 쓰는 재귀 패턴도 Python에서는 깊이에 따라 위험해질 수 있습니다. 이 차이를 이해해야 재귀를 예쁘기만 한 코드가 아니라 안전한 도구로 사용할 수 있습니다.

## 먼저 던지는 질문

- 재귀 함수는 어떤 구조를 가져야 안전하게 동작할까요?
- base case는 왜 항상 먼저 생각해야 할까요?
- Python에서 꼬리 재귀는 왜 이론만큼 실용적이지 않을까요?

## 큰 그림

![Functional Programming 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/functional-programming-101/07/07-01-big-picture.ko.png)

*Functional Programming 101 7장 흐름 개요*

## 왜 중요한가

트리 순회, 분할 정복, 중첩 구조 해제, 수학적 정의 같은 문제는 재귀로 표현할 때 가장 자연스럽습니다. 반복문으로도 풀 수는 있지만, 문제 구조 자체가 사라져 코드가 오히려 덜 읽힐 수 있습니다.

하지만 Python에서는 재귀 깊이 한계가 기본 1000이기 때문에, 구조가 재귀적이라는 이유만으로 무조건 재귀를 택하면 안 됩니다. 읽기 쉬움과 실행 안전성 사이에서 균형을 잡는 것이 실무 감각입니다.

## 개념 개요

> 재귀를 읽을 때는 내려가는 과정보다 base case에 도달한 뒤 값이 어떻게 되돌아오는지를 보는 것이 중요합니다.

```text
factorial(4)
  -> 4 * factorial(3)
       -> 3 * factorial(2)
            -> 2 * factorial(1)
                 -> 1  (base case)
            <- 2 * 1 = 2
       <- 3 * 2 = 6
  <- 4 * 6 = 24
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 재귀(recursion) | 함수가 자기 자신을 다시 호출하는 기법입니다 |
| base case | 재귀를 멈추는 종료 조건입니다 |
| 꼬리 재귀(tail recursion) | 함수의 마지막 연산이 재귀 호출인 형태입니다 |
| 스택 오버플로우(stack overflow) | 재귀 깊이가 한계를 넘어서 발생하는 오류입니다 |
| 분할 정복(divide and conquer) | 문제를 더 작은 하위 문제로 나누어 푸는 전략입니다 |

## Before / After

반복문의 누적 합도 재귀로 표현할 수 있습니다. 다만 그 표현이 실제로 더 적절한지는 별도의 판단이 필요합니다.

```python
# before: iterative sum
def sum_iterative(numbers: list[int]) -> int:
    total = 0
    for n in numbers:
        total += n
    return total

print(sum_iterative([1, 2, 3, 4, 5]))  # 15
```

```python
# after: recursive sum
def sum_recursive(numbers: list[int]) -> int:
    if not numbers:  # base case
        return 0
    return numbers[0] + sum_recursive(numbers[1:])

print(sum_recursive([1, 2, 3, 4, 5]))  # 15
```

## 단계별 실습

### Step 1: 기본 재귀 — 팩토리얼

```python
def factorial(n: int) -> int:
    """n! = n * (n-1) * ... * 1"""
    if n <= 1:  # base case
        return 1
    return n * factorial(n - 1)

print(factorial(5))   # 120
print(factorial(10))  # 3628800

# visualize the call stack
def factorial_verbose(n: int, depth: int = 0) -> int:
    indent = "  " * depth
    print(f"{indent}factorial({n})")
    if n <= 1:
        print(f"{indent}-> 1")
        return 1
    result = n * factorial_verbose(n - 1, depth + 1)
    print(f"{indent}-> {result}")
    return result

factorial_verbose(4)
# factorial(4)
#   factorial(3)
#     factorial(2)
#       factorial(1)
#       -> 1
#     -> 2
#   -> 6
# -> 24
```

재귀를 이해하는 가장 좋은 방법은 호출 스택을 눈으로 따라가는 것입니다. base case가 왜 중요한지, 반환값이 어떻게 쌓여 올라오는지가 바로 보입니다.

### Step 2: 피보나치와 메모이제이션

```python
from functools import lru_cache

# naive recursion: O(2^n) — very slow
def fib_naive(n: int) -> int:
    if n <= 1:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)

# memoization: O(n) — eliminates duplicate computation
@lru_cache(maxsize=None)
def fib_memo(n: int) -> int:
    if n <= 1:
        return n
    return fib_memo(n - 1) + fib_memo(n - 2)

print(fib_naive(10))  # 55 (slow)
print(fib_memo(100))  # 354224848179261915075 (fast)

# check cache statistics
print(fib_memo.cache_info())
# CacheInfo(hits=98, misses=101, maxsize=None, currsize=101)
```

재귀가 느린 것이 아니라, 같은 하위 문제를 중복 계산하는 재귀가 느린 것입니다. 이 차이를 이해하면 메모이제이션이 왜 강력한지 바로 연결됩니다.

### Step 3: 꼬리 재귀와 Python의 한계

```python
import sys

# normal recursion — stack frames accumulate
def factorial_normal(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial_normal(n - 1)  # multiplication is pending

# tail recursion — result passed as argument
def factorial_tail(n: int, acc: int = 1) -> int:
    if n <= 1:
        return acc
    return factorial_tail(n - 1, n * acc)  # last operation is the recursive call

# Python does NOT support tail call optimization (TCO)
print(sys.getrecursionlimit())  # default 1000
print(factorial_tail(900))  # works but...
# factorial_tail(1500)  # RecursionError!

# solution: convert to iteration
def factorial_iterative(n: int) -> int:
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

print(factorial_iterative(10000))  # no problem
```

많은 입문자가 여기서 한 번 헷갈립니다. 꼬리 재귀는 이론적으로 스택을 줄일 수 있는 형태이지만, Python 런타임이 그 최적화를 해 주지 않기 때문에 깊이가 깊어지면 결국 반복이 더 안전합니다.

### Step 4: 트리 순회와 재귀의 궁합

```python
from typing import Any

# traverse nested dicts (tree structure)
def flatten_dict(
    d: dict,
    parent_key: str = "",
    sep: str = ".",
) -> dict[str, Any]:
    """Flattens a nested dictionary."""
    items: list[tuple[str, Any]] = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

config = {
    "database": {
        "host": "localhost",
        "port": 5432,
        "credentials": {
            "user": "admin",
            "password": "secret",
        },
    },
    "debug": True,
}

flat = flatten_dict(config)
for k, v in flat.items():
    print(f"  {k}: {v}")
# database.host: localhost
# database.port: 5432
# database.credentials.user: admin
# database.credentials.password: secret
# debug: True
```

중첩 딕셔너리, 트리, AST처럼 구조 자체가 재귀적일 때는 재귀가 문제 도메인을 가장 직접적으로 반영합니다.

### Step 5: 재귀를 반복으로 바꾸기

```python
# recursive version: total size of a simulated file tree
def total_size_recursive(tree: dict) -> int:
    """Total size of a file tree represented as nested dicts."""
    total = 0
    for name, value in tree.items():
        if isinstance(value, dict):
            total += total_size_recursive(value)
        else:
            total += value
    return total

# iterative version: explicit stack management
def total_size_iterative(tree: dict) -> int:
    total = 0
    stack = [tree]
    while stack:
        current = stack.pop()
        for name, value in current.items():
            if isinstance(value, dict):
                stack.append(value)
            else:
                total += value
    return total

file_tree = {
    "src": {
        "main.py": 1200,
        "utils": {
            "helpers.py": 800,
            "config.py": 400,
        },
    },
    "README.md": 300,
    "tests": {
        "test_main.py": 600,
    },
}

print(total_size_recursive(file_tree))  # 3300
print(total_size_iterative(file_tree))  # 3300
```

실무에서는 이 전환이 매우 중요합니다. 구조는 재귀적으로 이해하되, 실행은 명시적 스택으로 바꿔 안정성을 확보하는 경우가 많습니다.

## 이 코드에서 주목할 점

- 모든 재귀에는 반드시 base case가 있어야 합니다.
- `@lru_cache`는 중복 호출을 제거해 재귀 성능을 크게 개선합니다.
- Python은 꼬리 호출 최적화를 지원하지 않으므로 깊은 재귀는 반복으로 바꾸는 편이 안전합니다.
- 트리 순회는 재귀가 가장 자연스럽게 읽히는 대표 사례입니다.

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| base case를 빼먹음 | 무한 재귀로 스택 오버플로우가 납니다 | 종료 조건을 먼저 작성합니다 |
| 깊은 재귀를 그대로 사용함 | Python 기본 한계를 쉽게 넘깁니다 | 깊이가 크면 반복으로 전환합니다 |
| 메모이제이션 없이 중복 계산함 | 시간 복잡도가 폭증합니다 | `@lru_cache`를 적용합니다 |
| 매 호출마다 리스트 슬라이싱을 함 | 호출마다 O(n) 복사가 생깁니다 | 인덱스를 인자로 넘기는 방식을 고려합니다 |
| 꼬리 재귀면 안전하다고 믿음 | Python은 TCO를 하지 않습니다 | 반복문으로 바꿉니다 |

## 실무에서 이렇게 쓰입니다

- 파싱한 JSON의 중첩 구조를 재귀로 순회합니다.
- 파일 시스템 트리 탐색 로직을 재귀적으로 표현합니다.
- 퀵정렬, 병합정렬 같은 분할 정복 알고리즘에 적용합니다.
- AST 처리에서 재귀 패턴을 사용합니다.
- 깊이가 불확실하면 명시적 스택 기반 반복으로 바꿉니다.

## 현업에서는 이렇게 판단합니다

재귀는 트리, 그래프, 중첩 구조를 설명하는 가장 자연스러운 도구입니다. 하지만 Python에서는 언제나 재귀 깊이 제한을 먼저 떠올려야 합니다. 깊이가 얕고 구조 표현이 중요한 경우에만 재귀를 그대로 유지하고, 깊이가 크거나 입력이 불확실하면 반복으로 전환하는 편이 안전합니다.

결국 재귀와 반복의 선택은 우아함과 안정성의 균형입니다. 구조를 드러내는 데 재귀가 압도적으로 좋다면 쓰되, 운영 환경에서 스택 리스크가 생기면 주저 없이 명시적 스택으로 옮기는 것이 실전적인 판단입니다.

## 체크리스트

- [ ] 재귀 함수의 올바른 base case를 설정할 수 있다
- [ ] 재귀 호출에서 스택 프레임이 어떻게 쌓이는지 설명할 수 있다
- [ ] `@lru_cache`로 재귀 성능을 개선할 수 있다
- [ ] 명시적 스택을 사용해 재귀를 반복으로 바꿀 수 있다
- [ ] 재귀와 반복 중 무엇을 택할지 기준을 설명할 수 있다

## 연습 문제

1. 이진 탐색을 재귀 버전과 반복 버전으로 각각 구현해 보세요.
2. 중첩 리스트 `[1, [2, [3, 4], 5], 6]`를 평탄화하는 재귀 함수를 작성해 보세요.
3. `@lru_cache` 대신 dict를 직접 사용해 메모이제이션을 구현해 보세요.

## 정리와 다음 글

재귀는 문제를 더 작은 같은 문제로 분해해 푸는 방식입니다. 다만 Python은 꼬리 호출 최적화를 지원하지 않으므로 깊이 제한을 항상 염두에 두어야 합니다. 다음 글에서는 값이 정말 필요해질 때까지 계산을 미루는 **지연 평가와 제너레이터**를 다룹니다.


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

- **재귀 함수는 어떤 구조를 가져야 안전하게 동작할까요?**
  - 본문의 기준은 재귀와 꼬리 호출를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **base case는 왜 항상 먼저 생각해야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Python에서 꼬리 재귀는 왜 이론만큼 실용적이지 않을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Functional Programming 101 (1/10): 함수형 프로그래밍이란 무엇인가?](./01-what-is-fp.md)
- [Functional Programming 101 (2/10): 순수 함수와 부수효과](./02-pure-functions.md)
- [Functional Programming 101 (3/10): immutable 데이터](./03-immutable-data.md)
- [Functional Programming 101 (4/10): 고차 함수](./04-higher-order-functions.md)
- [Functional Programming 101 (5/10): map, filter, reduce](./05-map-filter-reduce.md)
- [Functional Programming 101 (6/10): 클로저와 partial](./06-closure-and-partial.md)
- **재귀와 꼬리 호출 (현재 글)**
- 지연 평가와 제너레이터 (예정)
- 함수 합성과 파이프라인 (예정)
- 객체지향과 함수형의 균형 (예정)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — sys.setrecursionlimit](https://docs.python.org/3/library/sys.html#sys.setrecursionlimit)
- [Real Python — Recursion in Python](https://realpython.com/python-recursion/)
- [Python 공식 문서 — functools.lru_cache](https://docs.python.org/3/library/functools.html#functools.lru_cache)
- [The Little Schemer — Daniel P. Friedman](https://mitpress.mit.edu/9780262560993/the-little-schemer/)

Tags: Python, Functional Programming, 재귀, 꼬리 호출, 스택
