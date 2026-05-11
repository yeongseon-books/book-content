---
series: functional-programming-101
episode: 6
title: 클로저와 partial
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
  - 클로저
  - partial
  - functools
seo_description: 클로저의 동작 원리와 functools.partial을 활용한 함수 커스터마이징을 다룹니다.
last_reviewed: '2026-05-04'
---

# 클로저와 partial

> Functional Programming 101 시리즈 (6/10)


## 이 글에서 다룰 문제

클로저는 상태를 캡슐화하면서도 클래스를 사용하지 않는 경량 패턴입니다. 데코레이터, 팩토리 함수, 콜백 모두 클로저에 기반합니다.

> 클로저 = 데이터를 품은 함수

`functools.partial`은 기존 함수의 인자를 미리 채워 특화된 버전을 만드는 도구입니다. 두 패턴 모두 고차 함수와 결합하여 유연한 코드를 작성합니다.

## 핵심 개념 잡기

> 클로저의 구조

```
outer_func(x)
  │
  ├─ 지역 변수 x (자유 변수가 됨)
  │
  └─ inner_func(y)
       │
       └─ x + y  ← 외부의 x를 기억
           (클로저)
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 클로저(closure) | 외부 스코프의 변수를 기억하는 내부 함수입니다 |
| 자유 변수(free variable) | 함수 내부에서 사용되지만 로컬이 아닌 변수입니다 |
| 셀 객체(cell object) | Python이 자유 변수를 저장하는 내부 구조입니다 |
| partial | 기존 함수의 일부 인자를 고정한 새 함수를 생성합니다 |
| 커링(currying) | 다인자 함수를 단인자 함수의 연쇄로 변환하는 기법입니다 |

## Before / After

반복되는 인자를 클로저로 제거합니다.

```python
# before: 매번 같은 인자를 전달
import logging

logger = logging.getLogger("app")

logger.info("[UserService] 사용자 생성")
logger.info("[UserService] 사용자 조회")
logger.info("[UserService] 사용자 삭제")
```

```python
# after: 클로저로 prefix를 고정
import logging

def make_logger(prefix: str):
    logger = logging.getLogger("app")
    def log(message: str) -> None:
        logger.info(f"[{prefix}] {message}")
    return log

user_log = make_logger("UserService")
user_log("사용자 생성")
user_log("사용자 조회")
user_log("사용자 삭제")
```

## 단계별 실습

### Step 1: 클로저 기초

```python
def make_counter(start: int = 0):
    """카운터 함수를 생성합니다."""
    count = start

    def counter() -> int:
        nonlocal count
        count += 1
        return count

    return counter


c1 = make_counter()
print(c1())  # 1
print(c1())  # 2
print(c1())  # 3

c2 = make_counter(100)
print(c2())  # 101

# c1과 c2는 독립적인 상태
print(c1())  # 4
print(c2())  # 102
```

### Step 2: 자유 변수 확인

```python
def make_greeter(greeting: str):
    def greet(name: str) -> str:
        return f"{greeting}, {name}!"
    return greet


hello = make_greeter("안녕하세요")
bye = make_greeter("안녕히 가세요")

print(hello("Alice"))  # 안녕하세요, Alice!
print(bye("Bob"))      # 안녕히 가세요, Bob!

# 자유 변수 확인
print(hello.__code__.co_freevars)      # ('greeting',)
print(hello.__closure__[0].cell_contents)  # 안녕하세요
print(bye.__closure__[0].cell_contents)    # 안녕히 가세요
```

### Step 3: functools.partial

```python
from functools import partial


# 기본 사용법: 인자 고정
def power(base: int, exponent: int) -> int:
    return base ** exponent

square = partial(power, exponent=2)
cube = partial(power, exponent=3)

print(square(5))  # 25
print(cube(5))    # 125


# 실용 예: API 클라이언트 구성
def send_request(method: str, url: str, headers: dict) -> str:
    return f"{method} {url} (headers={headers})"

api_get = partial(send_request, "GET", headers={"Authorization": "Bearer token"})
api_post = partial(send_request, "POST", headers={"Authorization": "Bearer token"})

print(api_get("/users"))
# GET /users (headers={'Authorization': 'Bearer token'})
print(api_post("/orders"))
# POST /orders (headers={'Authorization': 'Bearer token'})
```

### Step 4: 클로저 vs partial

```python
from functools import partial


# 방법 1: 클로저
def make_tax_calculator_closure(rate: float):
    def calculate(amount: float) -> float:
        return round(amount * rate, 2)
    return calculate


# 방법 2: partial
def calculate_tax(amount: float, rate: float) -> float:
    return round(amount * rate, 2)

make_tax_calculator_partial = lambda rate: partial(calculate_tax, rate=rate)


# 사용법은 동일
tax_10 = make_tax_calculator_closure(0.1)
tax_10_p = make_tax_calculator_partial(0.1)

print(tax_10(50000))    # 5000.0
print(tax_10_p(50000))  # 5000.0


# 선택 기준
# - 클로저: 상태 변경(nonlocal)이 필요한 경우
# - partial: 기존 함수의 인자만 고정하는 경우
```

### Step 5: 실전 활용 — 이벤트 핸들러

```python
from functools import partial
from typing import Callable


# 이벤트 시스템
class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable]] = {}

    def on(self, event: str, handler: Callable) -> None:
        self._handlers.setdefault(event, []).append(handler)

    def emit(self, event: str, **data) -> None:
        for handler in self._handlers.get(event, []):
            handler(**data)


# 클로저로 컨텍스트를 포함한 핸들러 생성
def make_logger_handler(prefix: str):
    def handler(**data) -> None:
        print(f"[{prefix}] {data}")
    return handler

# partial로 기존 함수를 핸들러로 변환
def log_event(level: str, **data) -> None:
    print(f"[{level}] {data}")


bus = EventBus()
bus.on("user.created", make_logger_handler("UserService"))
bus.on("user.created", partial(log_event, "INFO"))

bus.emit("user.created", name="Alice", email="alice@example.com")
# [UserService] {'name': 'Alice', 'email': 'alice@example.com'}
# [INFO] {'name': 'Alice', 'email': 'alice@example.com'}
```

## 이 코드에서 주목할 점

- 클로저는 외부 변수를 `__closure__`에 저장하여 함수 호출 이후에도 유지합니다
- `nonlocal`은 외부 변수를 변경할 때 필요합니다 (읽기만 할 때는 불필요)
- `partial`은 기존 함수의 인자를 고정하여 특화된 함수를 만드는 간편한 방법입니다
- 상태가 필요하면 클로저, 인자 고정만 필요하면 `partial`이 적합합니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 반복문에서 클로저의 변수 공유 | 모든 클로저가 같은 변수를 참조합니다 | 기본 인자로 값을 복사합니다 |
| nonlocal 없이 외부 변수 변경 시도 | UnboundLocalError가 발생합니다 | `nonlocal` 선언을 추가합니다 |
| 클로저로 과도한 상태 관리 | 클래스가 더 적합합니다 | 상태가 복잡하면 클래스를 사용합니다 |
| partial 대신 불필요한 lambda | `partial`이 더 명확하고 빠릅니다 | 인자 고정이 목적이면 partial을 사용합니다 |
| 디버깅 시 클로저 상태 확인 누락 | 자유 변수가 예상과 다를 수 있습니다 | `__closure__`로 상태를 확인합니다 |

## 실무에서 이렇게 쓰입니다

- 데코레이터 내부에서 클로저로 설정값을 기억합니다
- 콜백 함수에 `partial`로 추가 인자를 전달합니다
- 테스트에서 `partial`로 공통 파라미터를 고정합니다
- 로깅 유틸리티를 클로저로 만들어 prefix를 고정합니다
- 이벤트 핸들러에 클로저로 컨텍스트를 바인딩합니다

## 현업 개발자는 이렇게 생각합니다

클로저는 "가벼운 객체"입니다. 상태가 단순하고 메서드가 하나인 경우 클래스보다 클로저가 적합합니다. 반대로 상태가 복잡하고 메서드가 여러 개면 클래스를 사용하는 것이 맞습니다.

`functools.partial`은 과소평가된 도구입니다. `lambda x: f(x, fixed_arg)` 대신 `partial(f, fixed_arg)`를 사용하면 더 명확하고, `repr()`로 고정된 인자를 확인할 수 있어 디버깅도 쉬워집니다.

## 체크리스트

- [ ] 클로저가 외부 변수를 기억하는 메커니즘을 설명할 수 있다
- [ ] `nonlocal`이 필요한 상황과 아닌 상황을 구분할 수 있다
- [ ] `functools.partial`로 함수의 인자를 고정할 수 있다
- [ ] 클로저와 partial의 선택 기준을 알고 있다
- [ ] 반복문에서 클로저 변수 공유 문제를 해결할 수 있다

## 정리 및 다음 글 안내

클로저는 함수가 자신이 정의된 환경을 기억하는 메커니즘이고, `partial`은 기존 함수의 인자를 고정합니다. 상태가 필요하면 클로저, 인자 고정만 필요하면 partial을 선택합니다. 다음 글에서는 함수형 프로그래밍의 핵심 기법인 **재귀와 꼬리 호출**을 다룹니다.

<!-- toc:begin -->
- [함수형 프로그래밍이란 무엇인가?](./01-what-is-fp.md)
- [순수 함수와 부수효과](./02-pure-functions.md)
- [immutable 데이터](./03-immutable-data.md)
- [고차 함수](./04-higher-order-functions.md)
- [map, filter, reduce](./05-map-filter-reduce.md)
- **클로저와 partial (현재 글)**
- [재귀와 꼬리 호출](./07-recursion.md)
- [지연 평가와 제너레이터](./08-lazy-evaluation.md)
- [함수 합성과 파이프라인](./09-function-composition.md)
- [객체지향과 함수형의 균형](./10-oop-and-fp-balance.md)
<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — functools.partial](https://docs.python.org/3/library/functools.html#functools.partial)
- [Real Python — Closures in Python](https://realpython.com/python-closure/)
- [Fluent Python — Chapter 9: Decorators and Closures](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)
- [PEP 3104 — Access to Names in Outer Scopes (nonlocal)](https://peps.python.org/pep-3104/)
