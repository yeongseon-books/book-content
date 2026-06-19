---
series: functional-programming-101
episode: 6
title: "Functional Programming 101 (6/10): 클로저와 partial"
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
  - 클로저
  - partial
  - functools
seo_description: 클로저와 functools.partial로 함수를 특화하는 방법을 설명합니다.
last_reviewed: '2026-05-12'
---

# Functional Programming 101 (6/10): 클로저와 partial

클로저는 처음 보면 조금 신기한 기능처럼 느껴집니다. 바깥 함수가 이미 끝났는데도 안쪽 함수가 예전 변수를 계속 기억하기 때문입니다. 하지만 이 메커니즘을 이해하면 데코레이터, 팩토리 함수, 콜백 설정 같은 패턴이 한꺼번에 정리됩니다.

이 글은 Functional Programming 101 시리즈의 6번째 글입니다.

`functools.partial`은 같은 문제를 다른 각도에서 풉니다. 기존 함수의 일부 인자를 미리 고정해 새 함수를 만들기 때문에, 클로저를 직접 쓰지 않고도 함수를 간단히 특화할 수 있습니다. 둘은 비슷해 보이지만 쓰임새가 조금 다릅니다.

![Functional Programming 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/functional-programming-101/06/06-01-closure-vs-partial-decision-flow.ko.png)
*Functional Programming 101 6장 흐름 개요*

## 이 글에서 다룰 문제

- 클로저는 바깥 스코프의 변수를 어떻게 기억할까요?
- 자유 변수와 cell object는 디버깅에서 왜 중요한 단서일까요?
- `functools.partial`은 어떤 상황에서 클로저보다 더 적합할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

클로저는 클래스를 쓰지 않고도 작은 상태를 캡슐화하게 해 줍니다. 상태가 단순하고 메서드도 하나면, 클래스보다 클로저가 훨씬 가볍고 읽기 쉬운 경우가 많습니다.

또한 `partial`은 이미 존재하는 함수를 재활용해 특화 버전을 만들 때 매우 유용합니다. `lambda x: f(x, fixed_arg)`보다 더 명확하고, 디버깅 시 고정된 인자도 드러나기 때문에 실무 코드에서 생각보다 큰 이점을 줍니다.

## 개념 개요

> 클로저의 핵심은 안쪽 함수가 바깥 변수에 대한 참조를 들고 있다는 사실입니다.

```text
outer_func(x)
  |
  +-- local variable x (becomes a free variable)
  |
  +-- inner_func(y)
       |
       +-- x + y  <- remembers outer x
            (closure)

클로저 vs partial 선택 기준:
  상태를 점진적으로 변경해야 한다 -> 클로저 (nonlocal)
  인자만 고정하면 충분하다        -> partial
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 클로저(closure) | 자신을 둘러싼 스코프의 변수를 기억하는 내부 함수입니다 |
| 자유 변수(free variable) | 함수 내부에서 사용하지만 로컬로 정의되지 않은 변수입니다 |
| cell object | Python이 자유 변수를 저장하는 내부 구조입니다 |
| partial | 기존 함수의 일부 인자를 고정해 새 함수를 만드는 도구입니다 |
| 커링(currying) | 여러 인자를 받는 함수를 단일 인자 함수들의 연쇄로 바꾸는 개념입니다 |

## 적용 전후 비교

같은 접두어를 계속 넘겨야 하는 코드는 의도보다 반복이 먼저 보입니다. 클로저로 그 반복을 흡수할 수 있습니다.

```python
# 이전: 매번 같은 인자를 전달
import logging

logger = logging.getLogger("app")

logger.info("[UserService] User created")
logger.info("[UserService] User queried")
logger.info("[UserService] User deleted")
```

```python
# 이후: closure로 prefix를 고정
import logging

def make_logger(prefix: str):
    logger = logging.getLogger("app")
    def log(message: str) -> None:
        logger.info(f"[{prefix}] {message}")
    return log

user_log = make_logger("UserService")
user_log("User created")
user_log("User queried")
user_log("User deleted")
```

## 단계별 실습

### 단계 1: 클로저의 기본 구조

```python
def make_counter(start: int = 0):
    """Creates a counter function."""
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

# c1과 c2는 독립적인 상태를 유지
print(c1())  # 4
print(c2())  # 102
```

클로저의 실무적 가치가 가장 잘 드러나는 예시입니다. 작은 상태를 함수 하나 안에 숨겨 둘 수 있어서, 가벼운 상태 캡슐화가 필요할 때 매우 유용합니다.

### 단계 2: 자유 변수 확인하기

```python
def make_greeter(greeting: str):
    def greet(name: str) -> str:
        return f"{greeting}, {name}!"
    return greet

hello = make_greeter("Hello")
bye = make_greeter("Goodbye")

print(hello("Alice"))  # Hello, Alice!
print(bye("Bob"))      # Goodbye, Bob!

# free variable 확인 — 디버깅 시 유용
print(hello.__code__.co_freevars)          # ('greeting',)
print(hello.__closure__[0].cell_contents)  # Hello
print(bye.__closure__[0].cell_contents)    # Goodbye
```

디버깅할 때는 이 내부 구조를 아는 것이 꽤 도움이 됩니다. 클로저가 예상과 다른 값을 기억하는 문제는 생각보다 자주 발생합니다.

### 단계 3: functools.partial 사용하기

```python
from functools import partial

# 기본 사용: 인자 고정
def power(base: int, exponent: int) -> int:
    return base ** exponent

square = partial(power, exponent=2)
cube = partial(power, exponent=3)

print(square(5))  # 25
print(cube(5))    # 125

# map에 partial 적용
numbers = [1, 2, 3, 4, 5]
squares = list(map(square, numbers))
cubes = list(map(cube, numbers))
print(squares)  # [1, 4, 9, 16, 25]
print(cubes)    # [1, 8, 27, 64, 125]

# 실전 예시: API client 설정
def send_request(method: str, url: str, headers: dict) -> str:
    return f"{method} {url} (headers={headers})"

api_get = partial(send_request, "GET", headers={"Authorization": "Bearer token"})
api_post = partial(send_request, "POST", headers={"Authorization": "Bearer token"})

print(api_get("/users"))   # GET /users (headers={'Authorization': 'Bearer token'})
print(api_post("/orders")) # POST /orders (headers={'Authorization': 'Bearer token'})
```

기존 함수 시그니처를 유지하면서 일부 인자만 고정하고 싶다면 `partial`이 훨씬 직관적입니다. 클로저를 새로 작성할 필요도 없습니다.

### 단계 4: 클로저와 partial 비교

```python
from functools import partial

# 방법 1: closure
def make_tax_calculator_closure(rate: float):
    def calculate(amount: float) -> float:
        return round(amount * rate, 2)
    return calculate

# 방법 2: partial
def calculate_tax(amount: float, rate: float) -> float:
    return round(amount * rate, 2)

tax_10_closure = make_tax_calculator_closure(0.1)
tax_10_partial = partial(calculate_tax, rate=0.1)

print(tax_10_closure(50000))  # 5000.0
print(tax_10_partial(50000))  # 5000.0

# 선택 기준
# - partial: 인자만 고정하면 될 때 (더 간결)
# - closure: 상태 변경(nonlocal)이 필요할 때

# partial은 repr에 고정 인자가 드러남
print(tax_10_partial)
# functools.partial(<function calculate_tax at 0x...>, rate=0.1)
```

둘 다 가능할 때는 대개 `partial`이 더 읽기 쉽습니다. 반대로 내부 상태를 점진적으로 바꾸거나 `nonlocal`이 필요하면 클로저가 더 자연스럽습니다.

### 단계 5: 루프 변수 공유 문제와 해결

```python
# 문제: 루프 안에서 클로저를 만들 때 변수 공유
funcs_wrong = []
for i in range(3):
    funcs_wrong.append(lambda: i)  # 모두 같은 i를 참조

print([f() for f in funcs_wrong])  # [2, 2, 2] — 의도와 다름!

# 해결 1: 기본 인자로 값 복사
funcs_correct = []
for i in range(3):
    funcs_correct.append(lambda x=i: x)  # 현재 i 값을 복사

print([f() for f in funcs_correct])  # [0, 1, 2] — 올바름

# 해결 2: partial 사용
from functools import partial

def identity(x: int) -> int:
    return x

funcs_partial = [partial(identity, i) for i in range(3)]
print([f() for f in funcs_partial])  # [0, 1, 2] — 올바름
```

루프 변수 공유는 클로저를 처음 쓸 때 가장 많이 빠지는 함정입니다. `partial`로 우회하거나 기본 인자로 값을 복사하는 것이 가장 명확한 해결책입니다.

### 단계 6: 실무 예시 — 이벤트 핸들러

```python
from functools import partial
from collections.abc import Callable

# event system
class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable]] = {}

    def on(self, event: str, handler: Callable) -> None:
        self._handlers.setdefault(event, []).append(handler)

    def emit(self, event: str, **data) -> None:
        for handler in self._handlers.get(event, []):
            handler(**data)

# context를 가진 handler를 만드는 closure
def make_logger_handler(prefix: str):
    def handler(**data) -> None:
        print(f"[{prefix}] {data}")
    return handler

# 기존 함수를 handler로 변환하는 partial
def log_event(level: str, **data) -> None:
    print(f"[{level}] {data}")

bus = EventBus()
bus.on("user.created", make_logger_handler("UserService"))
bus.on("user.created", partial(log_event, "INFO"))

bus.emit("user.created", name="Alice", email="alice@example.com")
# [UserService] {'name': 'Alice', 'email': 'alice@example.com'}
# [INFO] {'name': 'Alice', 'email': 'alice@example.com'}
```

이벤트 시스템, 웹훅, UI 콜백 같은 구조에서 클로저와 `partial`은 아주 자주 만납니다. 문법 장난이 아니라 실전 연결 도구라는 점이 중요합니다.

### 단계 7: 클로저로 데코레이터 구현하기

데코레이터는 클로저의 가장 대표적인 실무 적용입니다.

```python
import time
from functools import wraps

# 실행 시간을 측정하는 데코레이터 — 클로저 형태
def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)          # 바깥 func를 기억
        elapsed = time.perf_counter() - start
        print(f"{func.__name__}: {elapsed:.4f}s")
        return result
    return wrapper

@timeit
def slow_sum(numbers: list[int]) -> int:
    return sum(numbers)

result = slow_sum(list(range(1_000_000)))
# slow_sum: 0.0123s

# 인자를 받는 데코레이터 — 클로저를 두 겹으로 감쌈
def retry(max_attempts: int):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise
                    print(f"Attempt {attempt} failed: {e}. Retrying...")
        return wrapper
    return decorator

@retry(max_attempts=3)
def fetch_data(url: str) -> str:
    # 실제라면 HTTP 요청
    raise ConnectionError("timeout")

try:
    fetch_data("https://example.com")
except ConnectionError:
    print("All attempts failed")
# Attempt 1 failed: timeout. Retrying...
# Attempt 2 failed: timeout. Retrying...
# All attempts failed
```

`timeit`의 `wrapper` 안에서 `func`를 참조할 때 클로저가 작동합니다. `retry`는 `max_attempts`를 기억하는 클로저 안에 또 다른 클로저를 만드는 구조입니다. Python 데코레이터의 대부분이 이 패턴으로 작성됩니다.

## 이 코드에서 주목할 점

- 클로저는 바깥 변수를 `__closure__` 안에 보존해 바깥 함수가 끝난 뒤에도 살려 둡니다.
- 바깥 변수를 수정할 때만 `nonlocal`이 필요하고, 읽기만 할 때는 필요하지 않습니다.
- `partial`은 인자 고정이 목적일 때 가장 간단한 선택입니다.
- `map`과 `partial`을 조합하면 특화된 변환 함수를 간결하게 만들 수 있습니다.
- 데코레이터는 `@wraps`와 함께 클로저를 활용하는 대표 패턴입니다.

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 루프 안에서 클로저를 만들며 변수를 공유함 | 모든 클로저가 같은 마지막 값을 참조합니다 | 기본 인자로 값을 복사하거나 `partial`을 씁니다 |
| `nonlocal` 없이 바깥 변수를 수정함 | `UnboundLocalError`가 발생합니다 | `nonlocal` 선언을 추가합니다 |
| 클로저에 너무 많은 상태를 넣음 | 클래스가 더 적합한 상황이 됩니다 | 상태가 복잡하면 클래스로 전환합니다 |
| `partial` 대신 불필요한 `lambda`를 씀 | 의도가 덜 분명합니다 | 인자 고정 목적이면 `partial`을 사용합니다 |
| 디버깅 시 클로저 내부 상태를 확인하지 않음 | 자유 변수 값이 예상과 다를 수 있습니다 | `__closure__`를 확인합니다 |

## 실무에서 이렇게 쓰입니다

- 데코레이터는 설정 값을 기억하기 위해 클로저를 사용합니다.
- `map`의 콜백에 추가 인자를 붙일 때 `partial`을 사용합니다.
- 테스트에서 공통 파라미터를 고정한 함수를 만들어 재사용합니다.
- 로깅 유틸리티에서 접두어를 고정하는 데 클로저를 씁니다.
- 이벤트 핸들러에 컨텍스트를 바인딩할 때 클로저를 활용합니다.

## 현업에서는 이렇게 판단합니다

클로저는 "가벼운 객체"라고 생각하면 이해가 쉽습니다. 상태가 단순하고 메서드도 하나면, 클래스를 만드는 것보다 클로저가 훨씬 경제적입니다. 반대로 상태가 복잡하고 여러 행동이 필요해지면, 그때는 객체지향 모델이 더 낫습니다.

`functools.partial`은 과소평가된 도구입니다. `lambda x: f(x, fixed_arg)`보다 의도가 더 명확하고 `repr()`에도 고정 인자가 드러나서 디버깅에도 유리합니다. 좋은 팀은 클로저와 `partial`을 감으로 고르지 않고, 상태 기억이 필요한지 인자만 고정하면 되는지로 구분합니다.

## 처음 질문으로 돌아가기

- **클로저는 바깥 스코프의 변수를 어떻게 기억할까요?**
  Python은 내부 함수가 바깥 변수를 참조할 때 그 변수를 "자유 변수"로 만들고 `cell object`에 보관합니다. 바깥 함수가 종료되어도 이 cell은 살아남아 내부 함수의 `__closure__` 속성에서 접근할 수 있습니다. `hello.__closure__[0].cell_contents`로 실제 값을 확인할 수 있습니다.

- **자유 변수와 cell object는 디버깅에서 왜 중요한 단서일까요?**
  클로저가 예상과 다른 값을 내놓을 때, `func.__closure__[0].cell_contents`를 확인하면 실제로 기억하고 있는 값을 즉시 알 수 있습니다. 루프 변수 공유 문제처럼 "왜 모두 같은 결과가 나오지?"라는 버그를 추적할 때 가장 빠른 단서입니다.

- **`functools.partial`은 어떤 상황에서 클로저보다 더 적합할까요?**
  상태 변경 없이 기존 함수의 일부 인자만 고정하면 될 때 `partial`이 더 적합합니다. `make_validator(0, 100)`처럼 클로저를 새로 작성하는 대신 `partial(validate, min_val=0, max_val=100)`으로 표현할 수 있습니다. `repr()`에 고정 인자가 드러나서 디버깅도 더 쉽습니다.

## 운영 체크리스트

- [ ] 클로저가 바깥 변수를 기억하는 메커니즘을 설명할 수 있다
- [ ] `nonlocal`이 필요한 경우와 아닌 경우를 구분할 수 있다
- [ ] `functools.partial`로 함수를 특화할 수 있다
- [ ] 클로저와 `partial`의 선택 기준을 설명할 수 있다
- [ ] 루프 변수 공유 문제를 재현하고 해결할 수 있다

## 연습 문제

1. 감싼 함수의 호출 횟수를 세는 `make_call_counter(func)` 클로저를 작성해 보세요.
2. `map`에서 쓸 특화된 변환 함수를 `partial`로 만들어 적용해 보세요.
3. 루프 변수 공유 문제를 의도적으로 재현한 뒤 두 가지 방법으로 올바르게 수정해 보세요.

## 정리와 다음 글

클로저는 함수가 자신이 정의된 환경을 기억하게 만들고, `partial`은 기존 함수의 일부 인자를 고정해 새 함수를 만듭니다. 상태를 기억해야 하면 클로저가, 인자만 고정하면 되면 `partial`이 더 적합합니다. 다음 글에서는 반복을 자기 호출로 표현하는 **재귀와 꼬리 호출**을 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [Functional Programming 101 (1/10): 함수형 프로그래밍이란 무엇인가?](./01-what-is-fp.md)
- [Functional Programming 101 (2/10): 순수 함수와 부수효과](./02-pure-functions.md)
- [Functional Programming 101 (3/10): immutable 데이터](./03-immutable-data.md)
- [Functional Programming 101 (4/10): 고차 함수](./04-higher-order-functions.md)
- [Functional Programming 101 (5/10): map, filter, reduce](./05-map-filter-reduce.md)
- **Functional Programming 101 (6/10): 클로저와 partial (현재 글)**
- [Functional Programming 101 (7/10): 재귀와 꼬리 호출](./07-recursion.md)
- [Functional Programming 101 (8/10): 지연 평가와 제너레이터](./08-lazy-evaluation.md)
- [Functional Programming 101 (9/10): 함수 합성과 파이프라인](./09-function-composition.md)
- [객체지향과 함수형의 균형](./10-oop-and-fp-balance.md)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — functools.partial](https://docs.python.org/3/library/functools.html#functools.partial)
- [Real Python — Closures in Python](https://realpython.com/python-closure/)
- [Fluent Python — Chapter 9: Decorators and Closures](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)
- [PEP 3104 — Access to Names in Outer Scopes (nonlocal)](https://peps.python.org/pep-3104/)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/functional-programming-101/ko)
Tags: Python, Functional Programming, 클로저, partial, functools
