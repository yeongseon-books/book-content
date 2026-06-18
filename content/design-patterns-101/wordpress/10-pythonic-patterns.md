---
series: design-patterns-101
episode: 10
title: "바이브코딩을 위한 디자인 패턴 기초 (10/10): 파이썬에 어울리는 패턴"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - DesignPatterns
  - Python
  - Idioms
  - Protocols
  - AI코딩
seo_description: Python의 일급 함수, Protocol, 데코레이터로 GoF 패턴을 가볍게 표현하고, AI 코드에서 Pythonic 구조를 발견하는 바이브코딩 마무리 가이드입니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 디자인 패턴 기초 (10/10): 파이썬에 어울리는 패턴

**바이브코딩을 위한 디자인 패턴 기초** 시리즈의 마지막 글입니다. 이 시리즈는 AI와 함께 코딩할 때 디자인 패턴을 어떻게 읽고 활용할지를 다룹니다.

AI에게 Strategy 패턴을 요청하면 때로 ABC 클래스에 구현 클래스 여러 개가 붙은 Java 스타일 코드가 나옵니다. Python에서는 같은 의도를 함수 하나로 표현할 수 있는데도요. 이 마지막 글에서는 Python이 이미 제공하는 도구로 패턴의 의도를 얼마나 가볍게 표현할 수 있는지, 그리고 AI에게 어떻게 Pythonic한 코드를 요청하는지 다룹니다.

---

GoF 책이 나온 1994년, 저자들이 주로 쓰던 언어는 C++과 Smalltalk였습니다. 이후 Java가 패턴 교육의 사실상 표준 언어가 되면서, 많은 개발자가 패턴을 "클래스 계층으로 표현하는 것"이라고 무의식적으로 받아들이게 되었습니다. AI도 마찬가지입니다. "Strategy 패턴으로 구현해줘"라고 하면 ABC + 구현 클래스 구조를 기본으로 내놓는 경우가 많습니다.

하지만 Python에서는 다릅니다. 일급 함수, 덕 타이핑, Protocol, 데코레이터가 정적 언어가 패턴으로 우회하던 문제를 이미 언어 차원에서 해결합니다.

> "GoF의 많은 패턴이 Python에서 단 몇 줄로 줄어드는 이유는, 일급 함수·데코레이터·프로토콜이 정적 언어가 패턴으로 우회하던 문제를 이미 언어 차원에서 해결하기 때문입니다. AI에게 'Pythonic하게'라고 명시하면 더 가벼운 구조를 받을 수 있습니다."

## 이 글에서 다룰 문제

- AI가 Java 스타일 패턴을 만들어 줬을 때 Python 방식으로 어떻게 바꿀까요?
- Strategy, Command, Observer를 함수로 표현했을 때 잃는 것은 무엇일까요?
- Python에서도 GoF 클래스 구조가 필요한 경우는 언제일까요?
- AI에게 Pythonic한 패턴 구현을 어떻게 요청할까요?
- 처음 배우는 사람이 가장 자주 놓치는 포인트는 무엇일까요?

## Python이 이미 해결한 GoF 패턴들

| 언어 제약 (Java/C++) | Python이 제공하는 대안 |
| --- | --- |
| 함수를 값으로 전달 불가 | 일급 함수, `Callable` 타입 힌트 |
| 전역 단일 인스턴스 강제 수단 없음 | 모듈은 한 번만 로드됨 |
| 인터페이스 없이 다형성 불가 | 덕 타이핑 + `Protocol` |
| 객체에 동작 추가 시 상속 필요 | 데코레이터 `@` 문법 |
| 반복자를 위한 별도 클래스 필요 | `yield` 한 줄이면 Iterator |

## Strategy: ABC 클래스 → 함수

AI에게 "Python답게 Strategy 패턴 구현해줘"라고 하면:

**Java 스타일 (AI가 기본으로 만드는 구조):**

```python
from abc import ABC, abstractmethod

class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, order: "Order") -> int: ...

class NoDiscount(DiscountStrategy):
    def calculate(self, order: "Order") -> int:
        return 0

class VIPDiscount(DiscountStrategy):
    def calculate(self, order: "Order") -> int:
        return int(order.subtotal * 0.15)
```

**Pythonic 방식:**

```python
from typing import Callable

DiscountFn = Callable[["Order"], int]

def no_discount(order: "Order") -> int:
    return 0

def vip_discount(order: "Order") -> int:
    return int(order.subtotal * 0.15)

def apply_discount(order: "Order", strategy: DiscountFn = no_discount) -> int:
    return strategy(order)
```

ABC 클래스와 구현 클래스들이 함수 몇 개로 줄었습니다. 새 전략은 함수 하나를 추가하면 됩니다.

## Singleton: 클래스 → 모듈 변수

AI가 만든 Singleton 클래스를 Python 방식으로 단순화하기:

**AI가 기본으로 만드는 구조:**

```python
class AppConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
        return cls._instance
```

**Pythonic 방식:**

```python
# config.py
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class _Config:
    env: str
    db_url: str
    debug: bool

config = _Config(
    env=os.environ.get("APP_ENV", "dev"),
    db_url=os.environ.get("DB_URL", "sqlite:///local.db"),
    debug=os.environ.get("DEBUG", "0") == "1",
)
```

`from config import config`로 어디서든 같은 객체를 씁니다. Python의 import 시스템이 Singleton을 이미 보장합니다.

## Iterator: 클래스 → Generator

AI가 만든 Iterator 클래스를 generator로 단순화하기:

**Java 스타일:**

```python
class FibonacciIterator:
    def __init__(self, limit: int):
        self.limit = limit
        self.a, self.b = 0, 1
        self.count = 0

    def __iter__(self):
        return self

    def __next__(self) -> int:
        if self.count >= self.limit:
            raise StopIteration
        value = self.a
        self.a, self.b = self.b, self.a + self.b
        self.count += 1
        return value
```

**Pythonic 방식:**

```python
from collections.abc import Iterator

def fibonacci(limit: int) -> Iterator[int]:
    a, b = 0, 1
    for _ in range(limit):
        yield a
        a, b = b, a + b
```

12줄이 5줄로 줄었습니다. 상태 관리를 Python 런타임이 대신합니다.

## Decorator: Python `@` 문법 활용하기

AI가 만든 GoF 스타일 Decorator를 Python 데코레이터로:

**GoF 스타일 래퍼 클래스:**

```python
class LoggingClient:
    def __init__(self, inner: HttpClient):
        self._inner = inner

    def get(self, url: str) -> str:
        print(f"[REQ] GET {url}")
        result = self._inner.get(url)
        print(f"[RES] {len(result)} bytes")
        return result
```

**Python 데코레이터:**

```python
import functools
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def logged(fn: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"[CALL] {fn.__name__}")
        result = fn(*args, **kwargs)
        print(f"[DONE] {fn.__name__}")
        return result
    return wrapper

@logged
def fetch(url: str) -> str:
    return f"response from {url}"
```

`functools.wraps`는 원래 함수의 이름과 docstring을 보존합니다. 빠뜨리면 디버깅할 때 스택 트레이스에 `wrapper`만 보입니다.

## Before / After: Pythonic vs Java 스타일 Observer

**Java 스타일 Observer (AI가 기본으로 만드는 구조):**

```python
from abc import ABC, abstractmethod

class Subject:
    def __init__(self):
        self._observers: list["Observer"] = []

    def attach(self, obs: "Observer") -> None:
        self._observers.append(obs)

    def notify(self, event: str) -> None:
        for obs in self._observers:
            obs.update(event)

class Observer(ABC):
    @abstractmethod
    def update(self, event: str) -> None: ...
```

**Pythonic Observer (콜백 리스트):**

```python
from typing import Callable

type EventHandler = Callable[[str], None]

class EventBus:
    def __init__(self):
        self._handlers: dict[str, list[EventHandler]] = {}

    def on(self, event: str, handler: EventHandler) -> None:
        self._handlers.setdefault(event, []).append(handler)

    def emit(self, event: str, data: str) -> None:
        for handler in self._handlers.get(event, []):
            handler(data)

bus = EventBus()
bus.on("order.created", lambda data: print(f"[LOG] {data}"))
bus.emit("order.created", "order-123")
```

## 클래스 기반이 여전히 더 나은 경우

함수와 모듈로 단순화한다고 해서 항상 좋은 건 아닙니다. 세 가지 경우에는 GoF 클래스 구조가 더 낫습니다.

**상태와 동작이 밀접하게 결합된 경우:** 커넥션 풀처럼 내부 상태와 동작이 분리되면 위험한 경우는 클래스가 맞습니다.

**여러 객체가 협력하는 복합 패턴:** Mediator, Chain of Responsibility처럼 여러 참여자가 협력하는 패턴은 클래스로 표현해야 관계가 명확해집니다.

**프레임워크가 클래스 기반 확장을 전제하는 경우:** Django의 `View`, `ModelAdmin`은 상속 기반 확장을 전제합니다. 함수형 접근을 억지로 끼워 넣으면 프레임워크 기능을 잃게 됩니다.

## AI 활용 팁

**Pythonic 구현 요청:**

```
"Strategy 패턴으로 할인 정책을 구현해줘.
Java 스타일 ABC 클래스 대신 Python 함수와 Callable 타입 힌트를
사용해서 가볍게 만들어줘. 상태가 없는 전략은 함수로,
상태가 필요한 전략만 클래스로."
```

**Singleton 단순화 요청:**

```
"이 Singleton 클래스를 Python 모듈 변수로 단순화해줘.
frozen=True dataclass로 불변성을 보장하고,
모듈 import를 통해 단일 인스턴스를 공유하도록."
```

**Iterator 단순화 요청:**

```
"이 Iterator 클래스를 Python generator로 바꿔줘.
__iter__와 __next__ 대신 yield를 사용해서
코드를 5줄 이내로 줄여줘."
```

## 운영 체크리스트

- [ ] Python 내장 기능이 대체하는 GoF 패턴을 예로 들 수 있습니다.
- [ ] ABC 클래스 기반 Strategy를 함수로 단순화할 수 있습니다.
- [ ] `functools.wraps`를 사용한 데코레이터를 작성할 수 있습니다.
- [ ] 클래스 기반이 더 나은 경우를 설명할 수 있습니다.

## 정리

이 시리즈의 핵심 주제로 마무리합니다. AI가 만든 코드에서 패턴을 발견하는 능력, 그 패턴이 어떤 문제를 풀고 있는지 이해하는 능력, 그리고 Python에 맞는 표현으로 요청하는 능력. 이 세 가지가 "AI가 만든 코드를 내 것으로 만드는" 핵심입니다.

패턴을 많이 아는 것보다, 패턴이 풀려는 문제를 이해하고, 언어에 맞게 표현하고, 필요할 때만 사용하는 것이 중요합니다. 그리고 AI와 함께 코딩할 때 그 언어가 공통 어휘가 됩니다.

## 처음 질문으로 돌아가기

- **AI가 Java 스타일 패턴을 만들어 줬을 때 Python 방식으로 어떻게 바꿀까요?**
  - ABC 클래스는 함수로, `__iter__`/`__next__`는 generator로, 클래스 변수 Singleton은 모듈 변수로 단순화할 수 있습니다. AI에게 "Pythonic하게"라고 명시하세요.
- **Strategy, Command, Observer를 함수로 표현했을 때 잃는 것은 무엇일까요?**
  - 상태를 가진 전략, 여러 메서드가 필요한 경우, 프레임워크 통합에서 클래스가 더 자연스럽습니다. "메서드가 하나뿐이면 함수, 둘 이상이면 클래스"가 기준입니다.
- **Python에서도 GoF 클래스 구조가 필요한 경우는 언제일까요?**
  - 상태와 동작이 밀접하게 결합되거나, 여러 객체가 협력하거나, 프레임워크가 클래스 기반 확장을 전제할 때입니다.

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 디자인 패턴 기초 (1/10): 디자인 패턴이란 무엇인가?
- 바이브코딩을 위한 디자인 패턴 기초 (2/10): 생성 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (3/10): 구조 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (4/10): 행위 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (5/10): 전략 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (6/10): 어댑터 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (7/10): 옵저버 패턴
- 바이브코딩을 위한 디자인 패턴 기초 (8/10): 팩토리와 의존성 주입
- 바이브코딩을 위한 디자인 패턴 기초 (9/10): 패턴을 남용하지 않는 법
- **바이브코딩을 위한 디자인 패턴 기초 (10/10): 파이썬에 어울리는 패턴 (현재 글)**

<!-- toc:end -->

## 참고 자료

### 핵심 자료

- [PEP 544 — Protocols](https://peps.python.org/pep-0544/)
- [PEP 634 — Structural Pattern Matching](https://peps.python.org/pep-0634/)
- [dataclasses (Python docs)](https://docs.python.org/3/library/dataclasses.html)
- [functools.wraps (Python docs)](https://docs.python.org/3/library/functools.html#functools.wraps)

### 실무 확장 읽을거리

- [Fluent Python, 2nd Edition (Luciano Ramalho)](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)
- [PEP 20 — The Zen of Python](https://peps.python.org/pep-0020/)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/ko)

Tags: 바이브코딩, DesignPatterns, Python, Idioms, Protocols, AI코딩
