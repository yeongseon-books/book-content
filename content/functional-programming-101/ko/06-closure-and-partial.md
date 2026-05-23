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

`functools.partial`은 같은 문제를 다른 각도에서 풉니다. 기존 함수의 일부 인자를 미리 고정해 새 함수를 만들기 때문에, 클로저를 직접 쓰지 않고도 함수를 간단히 특화할 수 있습니다. 둘은 비슷해 보이지만 쓰임새가 조금 다릅니다.

![Functional Programming 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/functional-programming-101/06/06-01-closure-vs-partial-decision-flow.ko.png)
*Functional Programming 101 6장 흐름 개요*

## 먼저 던지는 질문

- 클로저는 바깥 스코프의 변수를 어떻게 기억할까요?
- 자유 변수와 cell object는 디버깅에서 왜 중요한 단서일까요?
- `functools.partial`은 어떤 상황에서 클로저보다 더 적합할까요?

## 왜 중요한가

클로저는 클래스를 쓰지 않고도 작은 상태를 캡슐화하게 해 줍니다. 상태가 단순하고 메서드도 하나면, 클래스보다 클로저가 훨씬 가볍고 읽기 쉬운 경우가 많습니다.

또한 `partial`은 이미 존재하는 함수를 재활용해 특화 버전을 만들 때 매우 유용합니다. `lambda x: f(x, fixed_arg)`보다 더 명확하고, 디버깅 시 고정된 인자도 드러나기 때문에 실무 코드에서 생각보다 큰 이점을 줍니다.

## 개념 개요

> 클로저의 핵심은 안쪽 함수가 바깥 변수에 대한 참조를 들고 있다는 점입니다.

```text
outer_func(x)
  |
  +-- local variable x (becomes a free variable)
  |
  +-- inner_func(y)
       |
       +-- x + y  <- remembers outer x
            (closure)
```

## 클로저와 `partial` 선택 흐름

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

# free variable 확인
print(hello.__code__.co_freevars)      # ('greeting',)
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

# 실전 예시: API client 설정
def send_request(method: str, url: str, headers: dict) -> str:
    return f"{method} {url} (headers={headers})"

api_get = partial(send_request, "GET", headers={"Authorization": "Bearer token"})
api_post = partial(send_request, "POST", headers={"Authorization": "Bearer token"})

print(api_get("/users"))
# 사용자 조회 GET /users (headers={'Authorization': 'Bearer token'})
print(api_post("/orders"))
# 주문 생성 POST /orders (headers={'Authorization': 'Bearer token'})
```

기존 함수 시그니처를 유지하면서 일부 인자만 고정하고 싶다면 `partial`이 훨씬 직관적입니다. 클로저를 새로 작성할 필요도 없습니다.

### 단계 4: 클로저와 partial 비교

```python
from functools import partial

# approach 1: closure
def make_tax_calculator_closure(rate: float):
    def calculate(amount: float) -> float:
        return round(amount * rate, 2)
    return calculate

# approach 2: partial
def calculate_tax(amount: float, rate: float) -> float:
    return round(amount * rate, 2)

make_tax_calculator_partial = lambda rate: partial(calculate_tax, rate=rate)

# 사용 방법은 동일
tax_10 = make_tax_calculator_closure(0.1)
tax_10_p = make_tax_calculator_partial(0.1)

print(tax_10(50000))    # 5000.0
print(tax_10_p(50000))  # 5000.0

# selection criteria
# - closure: 상태 변경(nonlocal)이 필요할 때
# - partial: 인자만 고정하면 될 때
```

둘 다 가능할 때는 대개 `partial`이 더 읽기 쉽습니다. 반대로 내부 상태를 점진적으로 바꾸거나 `nonlocal`이 필요하면 클로저가 더 자연스럽습니다.

### 단계 5: 실무 예시 — 이벤트 핸들러

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

### 단계 6: 실무 예시 — 테넌트별 웹훅 처리기 조립하기

```python
from dataclasses import dataclass
from functools import partial

@dataclass(frozen=True)
class TenantPolicy:
    tenant: str
    retry_limit: int
    audit_channel: str

def make_retry_decider(policy: TenantPolicy):
    attempts = 0

    def should_retry(status: str) -> bool:
        nonlocal attempts
        attempts += 1
        return status == "temporary-failure" and attempts < policy.retry_limit

    return should_retry

def publish_audit(channel: str, event_name: str, payload: dict) -> None:
    print(f"[{channel}] {event_name}: {payload}")

policy = TenantPolicy(
    tenant="store-kr",
    retry_limit=3,
    audit_channel="orders.webhook",
)

should_retry = make_retry_decider(policy)
record_audit = partial(publish_audit, policy.audit_channel)

event = {"order_id": "A-1024", "status": "temporary-failure"}
record_audit("webhook.received", {"tenant": policy.tenant, **event})

if should_retry(event["status"]):
    record_audit("webhook.retry_scheduled", {"order_id": event["order_id"], "attempt": 1})
```

이 패턴은 운영 코드에서 특히 유용합니다. 클로저는 테넌트별 재시도 상태를 기억하고, `partial`은 공통 감사 채널을 고정합니다. 덕분에 각 웹훅 핸들러는 설정 객체를 계속 다시 넘기지 않아도 되고, 어떤 값이 컨텍스트인지도 코드에 바로 드러납니다.

## 이 코드에서 주목할 점

- 클로저는 바깥 변수를 `__closure__` 안에 보존해 바깥 함수가 끝난 뒤에도 살려 둡니다.
- 바깥 변수를 수정할 때만 `nonlocal`이 필요하고, 읽기만 할 때는 필요하지 않습니다.
- `partial`은 인자 고정이 목적일 때 가장 간단한 선택입니다.
- 상태 변경이 필요하면 클로저, 인자 고정만 필요하면 `partial`이 더 적합합니다.

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 루프 안에서 클로저를 만들며 변수를 공유함 | 모든 클로저가 같은 마지막 값을 참조합니다 | 기본 인자로 값을 복사합니다 |
| `nonlocal` 없이 바깥 변수를 수정함 | `UnboundLocalError`가 발생합니다 | `nonlocal` 선언을 추가합니다 |
| 클로저에 너무 많은 상태를 넣음 | 클래스가 더 적합한 상황이 됩니다 | 상태가 복잡하면 클래스로 전환합니다 |
| `partial` 대신 불필요한 `lambda`를 씀 | 의도가 덜 분명합니다 | 인자 고정 목적이면 `partial`을 사용합니다 |
| 디버깅 시 클로저 내부 상태를 확인하지 않음 | 자유 변수 값이 예상과 다를 수 있습니다 | `__closure__`를 확인합니다 |

## 실무에서 이렇게 쓰입니다

- 데코레이터는 설정 값을 기억하기 위해 클로저를 사용합니다.
- 콜백에 추가 인자를 붙일 때 `partial`을 사용합니다.
- 테스트에서 공통 파라미터를 고정한 함수를 만들어 재사용합니다.
- 로깅 유틸리티에서 접두어를 고정하는 데 클로저를 씁니다.
- 이벤트 핸들러에 컨텍스트를 바인딩할 때 클로저를 활용합니다.

## 현업에서는 이렇게 판단합니다

클로저는 "가벼운 객체"라고 생각하면 이해가 쉽습니다. 상태가 단순하고 메서드도 하나면, 클래스를 만드는 것보다 클로저가 훨씬 경제적입니다. 반대로 상태가 복잡하고 여러 행동이 필요해지면, 그때는 객체지향 모델이 더 낫습니다.

`functools.partial`은 과소평가된 도구입니다. `lambda x: f(x, fixed_arg)`보다 의도가 더 명확하고 `repr()`에도 고정 인자가 드러나서 디버깅에도 유리합니다. 좋은 팀은 클로저와 `partial`을 감으로 고르지 않고, 상태 기억이 필요한지 인자만 고정하면 되는지로 구분합니다.

## 체크리스트

- [ ] 클로저가 바깥 변수를 기억하는 메커니즘을 설명할 수 있다
- [ ] `nonlocal`이 필요한 경우와 아닌 경우를 구분할 수 있다
- [ ] `functools.partial`로 함수를 특화할 수 있다
- [ ] 클로저와 `partial`의 선택 기준을 설명할 수 있다
- [ ] 루프 변수 공유 문제를 재현하고 해결할 수 있다

## 연습 문제

1. 감싼 함수의 호출 횟수를 세는 `make_call_counter(func)` 클로저를 작성해 보세요.
2. 유틸리티 함수 안에서 `sorted`의 `key` 인자를 `partial`로 특화해 보세요.
3. 루프 변수 공유 문제를 의도적으로 재현한 뒤 올바르게 수정해 보세요.

## 정리와 다음 글

클로저는 함수가 자신이 정의된 환경을 기억하게 만들고, `partial`은 기존 함수의 일부 인자를 고정해 새 함수를 만듭니다. 상태를 기억해야 하면 클로저가, 인자만 고정하면 되면 `partial`이 더 적합합니다. 다음 글에서는 반복을 자기 호출로 표현하는 **재귀와 꼬리 호출**을 다룹니다.

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

## 처음 질문으로 돌아가기

- **클로저는 바깥 스코프의 변수를 어떻게 기억할까요?**
  - 본문의 기준은 클로저와 partial를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **자유 변수와 cell object는 디버깅에서 왜 중요한 단서일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`functools.partial`은 어떤 상황에서 클로저보다 더 적합할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Functional Programming 101 (1/10): 함수형 프로그래밍이란 무엇인가?](./01-what-is-fp.md)
- [Functional Programming 101 (2/10): 순수 함수와 부수효과](./02-pure-functions.md)
- [Functional Programming 101 (3/10): immutable 데이터](./03-immutable-data.md)
- [Functional Programming 101 (4/10): 고차 함수](./04-higher-order-functions.md)
- [Functional Programming 101 (5/10): map, filter, reduce](./05-map-filter-reduce.md)
- **클로저와 partial (현재 글)**
- 재귀와 꼬리 호출 (예정)
- 지연 평가와 제너레이터 (예정)
- 함수 합성과 파이프라인 (예정)
- 객체지향과 함수형의 균형 (예정)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — functools.partial](https://docs.python.org/3/library/functools.html#functools.partial)
- [Real Python — Closures in Python](https://realpython.com/python-closure/)
- [Fluent Python — Chapter 9: Decorators and Closures](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)
- [PEP 3104 — Access to Names in Outer Scopes (nonlocal)](https://peps.python.org/pep-3104/)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/functional-programming-101/ko)
Tags: Python, Functional Programming, 클로저, partial, functools
