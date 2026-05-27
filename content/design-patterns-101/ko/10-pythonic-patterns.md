---
episode: 10
language: ko
last_reviewed: '2026-05-23'
seo_description: Python의 모듈, 함수, Protocol, 데코레이터로 GoF 패턴의 의도를 더 가볍게 표현하는 방법을 정리합니다.
series: design-patterns-101
status: publish-ready
tags:
- Computer Science
- DesignPatterns
- Python
- Idioms
- Protocols
- Decorators
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "디자인 패턴 101 (10/10): 파이썬에 어울리는 패턴"
---

# 디자인 패턴 101 (10/10): 파이썬에 어울리는 패턴

GoF 책이 나온 1994년, 저자들이 주로 쓰던 언어는 C++과 Smalltalk였습니다. 이후 Java가 패턴 교육의 사실상 표준 언어가 되면서, 많은 개발자가 패턴을 "클래스 계층으로 표현하는 것"이라고 무의식적으로 받아들이게 되었습니다. 저는 Python으로 처음 Strategy를 구현할 때 ABC를 만들고 구현 클래스를 세 개 작성한 뒤, 동료에게 "그냥 함수 넘기면 되지 않나요?"라는 리뷰를 받고서야 언어가 달라지면 패턴의 표현도 달라져야 한다는 사실을 체감했습니다.

이 글은 Design Patterns 101 시리즈의 마지막 글입니다. 시리즈 전체를 관통하는 질문 하나로 마무리합니다. **GoF 패턴의 의도를 유지하면서, Python이 이미 제공하는 도구로 얼마나 가볍게 표현할 수 있는가?** 그리고 그 가벼움이 적절하지 않은 경우는 언제인가?

![Design Patterns 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/10/10-01-concept-at-a-glance.ko.png)

*GoF 클래스 구조에서 Python 네이티브 표현으로의 전환 흐름*
> GoF의 많은 패턴이 Python에서 단 한 줄로 줄어드는 이유는, 일급 함수·데코레이터·프로토콜이 정적 언어가 패턴으로 우회하던 문제를 이미 언어 차원에서 해결하기 때문입니다.

## 먼저 던지는 질문

- Python에서 Singleton 클래스를 직접 구현하면 어떤 문제가 생기고, 모듈 변수로 대체하면 어떤 문제가 새로 생길까요?
- Strategy나 Command를 함수로 표현했을 때, 클래스 기반 대비 잃는 것은 무엇일까요?
- Python에서도 GoF 클래스 구조를 그대로 쓰는 편이 나은 경우는 어떤 상황일까요?

## GoF가 Java에서 출발했다는 사실을 기억해야 하는 이유

GoF 패턴 23개 중 상당수는 언어의 한계를 우회하기 위한 장치입니다. Java에는 일급 함수가 없었으니 Strategy를 인터페이스 + 구현 클래스로 표현해야 했고, 모듈 개념이 없었으니 Singleton을 `private` 생성자로 강제해야 했습니다. C++에는 가비지 컬렉터가 없었으니 객체 생성과 소멸의 책임을 명시적으로 분리하는 Creational 패턴이 더 절실했습니다.

Python은 이 제약 대부분이 없습니다.

| 언어 제약 (Java/C++) | Python이 제공하는 대안 |
| --- | --- |
| 함수를 값으로 전달 불가 | 일급 함수, `Callable` 타입 힌트 |
| 전역 단일 인스턴스 강제 수단 없음 | 모듈은 한 번만 로드됨 |
| 인터페이스 없이 다형성 불가 | 덕 타이핑 + `Protocol` |
| 객체에 동작 추가 시 상속 필요 | 데코레이터 `@` 문법 |
| 반복자를 위한 별도 클래스 필요 | `yield` 한 줄이면 Iterator |

이 표가 말하는 바는 단순합니다. **패턴의 의도는 유효하지만, 표현 방식은 언어에 맞게 바뀌어야 합니다.** Java식 클래스 계층을 Python에 그대로 옮기면, 언어가 이미 풀어 놓은 문제를 다시 손으로 풀게 됩니다.

## Singleton이 모듈 변수로 풀리는 이유와 풀리지 않는 경우

### Before: 전통적 Singleton 클래스

```python
import threading

class AppConfig:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._loaded = False
        return cls._instance

    def load(self, path: str) -> None:
        # 설정 파일 로드
        self._loaded = True
```

Double-checked locking까지 넣으면 10줄이 넘습니다. 그런데 이 코드에는 더 심각한 문제가 있습니다. 테스트에서 인스턴스를 초기화할 방법이 없습니다. `_instance`를 `None`으로 되돌리는 `reset()` 메서드를 추가하면 프로덕션에서 실수로 호출될 위험이 생기고, 추가하지 않으면 테스트 격리가 깨집니다.

### After: 모듈 변수

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

```python
# 사용하는 쪽
from config import config

def connect_db():
    return create_engine(config.db_url)
```

Python의 import 시스템은 모듈을 한 번만 실행합니다. `sys.modules`에 캐시되므로 어디서 import하든 같은 객체를 받습니다. 스레드 안전성은 import lock이 보장합니다. 테스트에서는 `monkeypatch`나 `unittest.mock.patch`로 `config` 객체를 교체하면 됩니다.

### 모듈 변수로 풀리지 않는 경우

모듈 변수가 만능은 아닙니다. 다음 상황에서는 클래스 기반 접근이 여전히 필요합니다.

- **지연 초기화가 필수인 경우**: 모듈 로드 시점에 외부 서비스 연결을 열면 import만으로 부작용이 생깁니다. 이때는 `__init__`에서 연결하되 인스턴스 생성 시점을 제어하는 팩토리가 낫습니다.
- **런타임에 설정을 교체해야 하는 경우**: `frozen=True` dataclass는 불변이므로, 설정 리로드가 필요하면 mutable 객체나 별도 reload 메커니즘이 필요합니다.
- **프레임워크가 클래스 인스턴스를 요구하는 경우**: Django의 `AppConfig`, Flask의 `app` 객체처럼 프레임워크 자체가 클래스 기반 싱글턴을 전제하는 경우가 있습니다.

## Strategy를 함수로 표현했을 때 잃는 것과 얻는 것

### Before: ABC 기반 Strategy

```python
from abc import ABC, abstractmethod
from decimal import Decimal

class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, order: "Order") -> Decimal:
        ...

class NoDiscount(DiscountStrategy):
    def calculate(self, order: "Order") -> Decimal:
        return Decimal("0")

class BulkDiscount(DiscountStrategy):
    def calculate(self, order: "Order") -> Decimal:
        if order.quantity >= 100:
            return order.subtotal * Decimal("0.1")
        return Decimal("0")

class VIPDiscount(DiscountStrategy):
    def calculate(self, order: "Order") -> Decimal:
        return order.subtotal * Decimal("0.15")
```

ABC 하나에 구현 클래스 세 개. 각 클래스는 메서드 하나뿐입니다.

### After: 함수 기반 Strategy

```python
from decimal import Decimal
from typing import Callable

type DiscountFn = Callable[["Order"], Decimal]

def no_discount(order: "Order") -> Decimal:
    return Decimal("0")

def bulk_discount(order: "Order") -> Decimal:
    if order.quantity >= 100:
        return order.subtotal * Decimal("0.1")
    return Decimal("0")

def vip_discount(order: "Order") -> Decimal:
    return order.subtotal * Decimal("0.15")

def apply_discount(order: "Order", strategy: DiscountFn) -> Decimal:
    return strategy(order)
```

`type` 문(3.12+)이나 `TypeAlias`로 시그니처를 명시하면 타입 검사기가 잘못된 함수 전달을 잡아 줍니다.

### 얻는 것

- 클래스 3개 → 함수 3개. 보일러플레이트가 사라집니다.
- `functools.partial`로 파라미터를 바인딩하면 새 전략을 한 줄로 만들 수 있습니다.
- 테스트에서 lambda 하나로 stub을 만들 수 있습니다.

### 잃는 것

- **상태를 가진 전략**: 할인 이력을 누적하거나, 외부 서비스 클라이언트를 들고 있어야 하는 전략은 함수 하나로 표현하기 어렵습니다. 클로저로 감쌀 수는 있지만, 상태가 복잡해지면 클래스가 더 읽기 쉽습니다.
- **여러 메서드를 묶는 전략**: `calculate`뿐 아니라 `describe`, `validate` 같은 메서드가 함께 필요하면 함수 하나로는 부족합니다.
- **프레임워크 통합**: DI 컨테이너가 클래스 기반 등록을 전제하는 경우 함수를 억지로 끼워 넣으면 오히려 복잡해집니다.

저는 "메서드가 하나뿐인 전략은 함수, 둘 이상이면 클래스"를 기본 판단 기준으로 씁니다.

## Command를 callable로 표현하기

GoF Command 패턴의 핵심은 "요청을 객체로 캡슐화하여 큐에 넣거나 되돌릴 수 있게 한다"입니다. Python에서는 callable이면 무엇이든 Command가 됩니다.

```python
from functools import partial

def send_email(to: str, subject: str, body: str) -> None:
    print(f"Sending to {to}: {subject}")

def delete_file(path: str) -> None:
    print(f"Deleting {path}")

# Command 큐: callable 리스트
command_queue: list[partial] = [
    partial(send_email, "admin@ex.com", "Report", "Monthly stats"),
    partial(delete_file, "/tmp/old_report.csv"),
]

# 실행
for cmd in command_queue:
    cmd()
```

`partial`은 인자를 미리 바인딩한 callable을 만듭니다. 큐에 넣고, 직렬화하고, 나중에 실행하는 것이 자연스럽습니다. Undo가 필요하면 `(do, undo)` 튜플을 큐에 넣는 방식으로 확장합니다.

```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class UndoableCommand:
    execute: Callable[[], None]
    undo: Callable[[], None]

history: list[UndoableCommand] = []

def do(cmd: UndoableCommand) -> None:
    cmd.execute()
    history.append(cmd)

def undo_last() -> None:
    if history:
        history.pop().undo()
```

Undo까지 필요한 순간에도 클래스 계층 없이 dataclass + callable 조합으로 충분합니다.

## Observer를 콜백 리스트와 시그널로 표현하기

### Before: GoF Observer 클래스

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

class Logger(Observer):
    def update(self, event: str) -> None:
        print(f"[LOG] {event}")

class Metrics(Observer):
    def update(self, event: str) -> None:
        print(f"[METRIC] {event}")
```

### After: 콜백 리스트

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
bus.on("order.created", lambda data: print(f"[METRIC] {data}"))
bus.emit("order.created", "order-123")
```

20줄 안에 pub/sub이 완성됩니다. 프로덕션에서 더 견고한 구현이 필요하면 `blinker`나 `pyee`를 쓰면 됩니다.

```python
from blinker import signal

order_created = signal("order-created")

@order_created.connect
def log_order(sender, **kwargs):
    print(f"[LOG] {kwargs['order_id']}")

order_created.send(None, order_id="order-123")
```

`blinker`는 Flask가 내부적으로 쓰는 시그널 라이브러리입니다. 약한 참조 기반이라 메모리 누수 걱정이 적고, 네임스페이스 분리도 지원합니다.

## Generator가 Iterator 패턴을 흡수한 방식

GoF Iterator는 컬렉션의 내부 구조를 노출하지 않고 순회하기 위한 패턴입니다. Java에서는 `Iterator` 인터페이스를 구현하는 별도 클래스가 필요합니다. Python에서는 `yield` 한 줄이면 됩니다.

### Before: `__iter__` + `__next__` 클래스

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

### After: generator 함수

```python
from collections.abc import Iterator

def fibonacci(limit: int) -> Iterator[int]:
    a, b = 0, 1
    for _ in range(limit):
        yield a
        a, b = b, a + b
```

12줄이 5줄로 줄었습니다. 상태 관리(`self.a`, `self.b`, `self.count`)를 Python 런타임이 대신 합니다. generator는 `__iter__`와 `__next__`를 자동으로 구현하므로 `for` 루프, `list()`, `itertools` 함수와 바로 호환됩니다.

generator의 진짜 힘은 **게으른 평가(lazy evaluation)** 에 있습니다. 10억 개의 피보나치 수를 메모리에 올리지 않고도 하나씩 꺼낼 수 있습니다. 이 특성 덕분에 대용량 파일 처리, 스트리밍 API 응답, 페이지네이션 같은 실무 시나리오에서 Iterator 클래스를 직접 만들 일이 거의 없습니다.

## Python decorator는 GoF Decorator와 같은 패턴인가

결론부터 말하면, **의도는 같고 메커니즘은 다릅니다.**

GoF Decorator는 객체를 감싸서 동작을 추가하되, 원래 인터페이스를 유지하는 패턴입니다. Java에서는 같은 인터페이스를 구현하는 래퍼 클래스를 만듭니다. Python의 `@` 데코레이터는 함수(또는 클래스)를 받아서 새 함수를 반환하는 고차 함수입니다.

### Before: GoF 스타일 래퍼 클래스

```python
from typing import Protocol

class HttpClient(Protocol):
    def get(self, url: str) -> str: ...

class BasicClient:
    def get(self, url: str) -> str:
        return f"response from {url}"

class LoggingClient:
    def __init__(self, inner: HttpClient):
        self._inner = inner

    def get(self, url: str) -> str:
        print(f"[REQ] GET {url}")
        result = self._inner.get(url)
        print(f"[RES] {len(result)} bytes")
        return result

class RetryClient:
    def __init__(self, inner: HttpClient, retries: int = 3):
        self._inner = inner
        self._retries = retries

    def get(self, url: str) -> str:
        for attempt in range(self._retries):
            try:
                return self._inner.get(url)
            except Exception:
                if attempt == self._retries - 1:
                    raise
        return ""  # unreachable

# 조립
client = RetryClient(LoggingClient(BasicClient()))
```

### After: 함수 데코레이터

```python
import functools
import time
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

def retry(retries: int = 3):
    def decorator(fn: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for attempt in range(retries):
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    if attempt == retries - 1:
                        raise
                    time.sleep(0.1 * (2 ** attempt))
            return fn(*args, **kwargs)  # unreachable
        return wrapper
    return decorator

@retry(retries=3)
@logged
def fetch(url: str) -> str:
    return f"response from {url}"
```

`functools.wraps`는 원래 함수의 `__name__`, `__doc__`, `__module__`을 보존합니다. 이걸 빼먹으면 디버깅 시 스택 트레이스에 `wrapper`만 보여서 추적이 어려워집니다.

두 접근의 차이는 **조합 방식**입니다. 클래스 래퍼는 런타임에 동적으로 조립할 수 있고, 함수 데코레이터는 정의 시점에 정적으로 쌓입니다. HTTP 클라이언트처럼 미들웨어를 런타임에 조건부로 끼워 넣어야 하는 경우에는 클래스 래퍼가 더 유연합니다.

## Template Method를 고차 함수로 표현하기

GoF Template Method는 알고리즘의 뼈대를 상위 클래스에 정의하고, 세부 단계를 하위 클래스가 오버라이드하는 패턴입니다. Python에서는 고차 함수에 hook을 전달하는 방식이 더 자연스럽습니다.

### Before: ABC + 상속

```python
from abc import ABC, abstractmethod

class DataExporter(ABC):
    def export(self, data: list[dict]) -> str:
        filtered = self.filter(data)
        transformed = self.transform(filtered)
        return self.format(transformed)

    @abstractmethod
    def filter(self, data: list[dict]) -> list[dict]: ...

    @abstractmethod
    def transform(self, data: list[dict]) -> list[dict]: ...

    @abstractmethod
    def format(self, data: list[dict]) -> str: ...
```

하위 클래스를 만들 때마다 세 메서드를 모두 구현해야 합니다.

### After: 고차 함수 + hook callable

```python
from typing import Callable

type Filter = Callable[[list[dict]], list[dict]]
type Transform = Callable[[list[dict]], list[dict]]
type Formatter = Callable[[list[dict]], str]

def export_data(
    data: list[dict],
    *,
    filter_fn: Filter = lambda d: d,
    transform_fn: Transform = lambda d: d,
    format_fn: Formatter = str,
) -> str:
    return format_fn(transform_fn(filter_fn(data)))

# 사용
import json

result = export_data(
    raw_data,
    filter_fn=lambda d: [r for r in d if r["active"]],
    transform_fn=lambda d: [{"name": r["name"]} for r in d],
    format_fn=lambda d: json.dumps(d, ensure_ascii=False),
)
```

상속 계층 없이 각 단계를 독립적으로 교체할 수 있습니다. 기본값을 제공하면 모든 hook을 매번 지정할 필요도 없습니다.

## State를 dict-of-handlers와 match로 표현하기

GoF State 패턴은 상태별 동작을 별도 클래스로 분리합니다. Python에서는 상태가 단순할 때 dict 매핑이나 `match` 문으로 충분합니다.

### dict-of-handlers

```python
from typing import Callable

type Handler = Callable[["Order"], "Order"]

def handle_pending(order: "Order") -> "Order":
    print(f"Validating order {order.id}")
    return order._replace(state="confirmed")

def handle_confirmed(order: "Order") -> "Order":
    print(f"Processing payment for {order.id}")
    return order._replace(state="paid")

def handle_paid(order: "Order") -> "Order":
    print(f"Shipping order {order.id}")
    return order._replace(state="shipped")

STATE_HANDLERS: dict[str, Handler] = {
    "pending": handle_pending,
    "confirmed": handle_confirmed,
    "paid": handle_paid,
}

def advance(order: "Order") -> "Order":
    handler = STATE_HANDLERS.get(order.state)
    if handler is None:
        raise ValueError(f"No handler for state: {order.state}")
    return handler(order)
```

### match 문 (3.10+)

```python
def advance(order: "Order") -> "Order":
    match order.state:
        case "pending":
            return order._replace(state="confirmed")
        case "confirmed":
            return order._replace(state="paid")
        case "paid":
            return order._replace(state="shipped")
        case _:
            raise ValueError(f"Unknown state: {order.state}")
```

상태가 3-5개이고 전이 로직이 단순하면 `match`가 가장 읽기 쉽습니다. 상태가 10개를 넘거나 전이 조건이 복잡해지면 dict-of-handlers가 확장에 유리합니다. 상태별로 진입/퇴장 훅이 필요하거나 상태 간 공유 컨텍스트가 복잡하면 그때 클래스 기반 State 패턴이 자연스러워집니다.

## Protocol 기반 Adapter — 클래스 없는 인터페이스

GoF Adapter는 호환되지 않는 인터페이스를 맞추는 패턴입니다. Java에서는 인터페이스를 구현하는 어댑터 클래스를 만듭니다. Python에서는 Protocol 덕분에 **기존 클래스를 수정하지 않고도** 인터페이스를 맞출 수 있습니다.

```python
from typing import Protocol

class Notifier(Protocol):
    def notify(self, message: str) -> None: ...

# 외부 라이브러리의 클래스 — 수정 불가
class SlackWebhook:
    def __init__(self, url: str):
        self.url = url

    def post(self, text: str) -> None:
        print(f"Slack: {text}")

# Adapter: SlackWebhook을 Notifier로 맞춤
class SlackNotifier:
    def __init__(self, webhook: SlackWebhook):
        self._webhook = webhook

    def notify(self, message: str) -> None:
        self._webhook.post(message)

def send_alert(notifier: Notifier, msg: str) -> None:
    notifier.notify(msg)

# SlackNotifier는 Notifier Protocol을 만족 — 상속 없음
send_alert(SlackNotifier(SlackWebhook("https://hooks.slack.com/...")), "서버 다운")
```

`SlackNotifier`는 `Notifier`를 상속하지 않습니다. `notify` 메서드의 시그니처가 일치하기만 하면 mypy가 Protocol 호환으로 인정합니다. 이것이 구조적 타이핑(structural typing)의 힘입니다. 외부 라이브러리 클래스를 감쌀 때 특히 유용합니다. 원본 코드를 건드리지 않고 우리 시스템의 인터페이스에 맞출 수 있기 때문입니다.

## Abstract Factory를 팩토리 함수와 클로저로 표현하기

GoF Abstract Factory는 관련 객체 군을 생성하는 인터페이스를 제공합니다. Python에서는 팩토리 함수가 dataclass 인스턴스를 반환하는 형태로 단순화됩니다.

```python
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class Button:
    label: str
    style: str

@dataclass(frozen=True)
class Dialog:
    title: str
    buttons: list[Button]

type UIFactory = Callable[[str], Dialog]

def dark_theme_factory(title: str) -> Dialog:
    return Dialog(
        title=title,
        buttons=[
            Button("OK", style="dark-primary"),
            Button("Cancel", style="dark-secondary"),
        ],
    )

def light_theme_factory(title: str) -> Dialog:
    return Dialog(
        title=title,
        buttons=[
            Button("OK", style="light-primary"),
            Button("Cancel", style="light-secondary"),
        ],
    )

def create_dialog(factory: UIFactory, title: str) -> Dialog:
    return factory(title)
```

클래스 계층 없이 함수 시그니처 하나로 팩토리 계약을 표현합니다. 테마가 추가되면 함수 하나만 더 만들면 됩니다.

## Python에서 여전히 클래스 기반 패턴이 자연스러운 경우

지금까지 함수, 모듈, Protocol로 패턴을 가볍게 표현하는 방법을 봤습니다. 하지만 모든 상황에서 클래스를 피해야 한다는 뜻은 아닙니다. 다음 세 가지 경우에는 GoF 클래스 구조가 Python에서도 더 나은 선택입니다.

### 1. 상태와 동작이 밀접하게 결합된 경우

```python
class ConnectionPool:
    def __init__(self, max_size: int):
        self._pool: list[Connection] = []
        self._max_size = max_size
        self._lock = threading.Lock()

    def acquire(self) -> Connection:
        with self._lock:
            if self._pool:
                return self._pool.pop()
            return self._create()

    def release(self, conn: Connection) -> None:
        with self._lock:
            if len(self._pool) < self._max_size:
                self._pool.append(conn)
            else:
                conn.close()

    def _create(self) -> Connection:
        return Connection(...)
```

커넥션 풀은 내부 상태(`_pool`, `_lock`)와 동작(`acquire`, `release`)이 분리되면 오히려 위험합니다. 함수로 쪼개면 상태 관리 책임이 호출자에게 넘어가고, 동시성 버그가 생기기 쉽습니다.

### 2. 여러 객체가 협력하는 복합 패턴

Mediator, Chain of Responsibility처럼 여러 참여자가 서로를 참조하며 협력하는 패턴은 클래스로 표현해야 각 참여자의 역할과 관계가 명확해집니다. 함수와 클로저로 표현하면 "누가 누구를 알고 있는지"가 코드에서 보이지 않게 됩니다.

### 3. 프레임워크가 클래스 기반 확장을 전제하는 경우

Django의 `View`, `ModelAdmin`, `Form`은 상속 기반 확장을 전제합니다. 이런 프레임워크 위에서 작업할 때 함수형 접근을 억지로 끼워 넣으면 프레임워크의 기능(미들웨어 훅, 시그널, admin 자동 등록 등)을 잃게 됩니다. 프레임워크의 관례를 따르는 것이 팀 전체의 생산성에 더 이롭습니다.

저는 이 판단을 한 문장으로 요약합니다. **"함수로 표현했을 때 상태 관리가 호출자에게 넘어가거나, 객체 간 관계가 코드에서 사라지면 클래스가 맞다."**

## 처음 질문으로 돌아가기

- **Python에서 Singleton 클래스를 직접 구현하면 어떤 문제가 생기고, 모듈 변수로 대체하면 어떤 문제가 새로 생길까요?**
  - Singleton 클래스는 double-checked locking의 복잡성과 테스트 격리 문제를 동시에 안고 옵니다. 모듈 변수는 import 시스템이 단일 인스턴스를 보장하므로 이 문제가 사라지지만, 지연 초기화가 필요하거나 런타임에 설정을 교체해야 하는 경우에는 별도 메커니즘이 필요합니다.

- **Strategy나 Command를 함수로 표현했을 때, 클래스 기반 대비 잃는 것은 무엇일까요?**
  - 상태를 가진 전략, 여러 메서드를 묶는 전략, DI 컨테이너 통합이 필요한 경우에는 함수 표현이 오히려 복잡해집니다. 메서드가 하나뿐이고 상태가 없는 전략이라면 함수가 보일러플레이트를 제거하면서 타입 힌트로 계약을 유지하는 최선의 선택입니다.

- **Python에서도 GoF 클래스 구조를 그대로 쓰는 편이 나은 경우는 어떤 상황일까요?**
  - 상태와 동작이 밀접하게 결합된 경우(커넥션 풀), 여러 객체가 서로를 참조하며 협력하는 경우(Mediator), 프레임워크가 클래스 기반 확장을 전제하는 경우(Django View)입니다. 함수로 표현했을 때 상태 관리 책임이 호출자에게 넘어가거나 객체 간 관계가 보이지 않게 되면, 그것이 클래스로 돌아가야 할 신호입니다.

이 시리즈는 1장에서 "패턴은 문제-해법 쌍에 붙인 이름"이라고 정의하며 시작했습니다. 10장에 와서 같은 말을 다시 합니다. 패턴의 본체는 클래스 구조가 아니라 의도입니다. 의도를 이해하면 언어가 제공하는 가장 자연스러운 도구로 표현할 수 있고, 그 도구가 부족할 때만 클래스 계층을 꺼내면 됩니다.

<!-- toc:begin -->
## 시리즈 목차

- [Design Patterns 101 (1/10): 디자인 패턴이란 무엇인가?](./01-what-are-design-patterns.md)
- [Design Patterns 101 (2/10): Creational 패턴](./02-creational-patterns.md)
- [Design Patterns 101 (3/10): Structural 패턴](./03-structural-patterns.md)
- [Design Patterns 101 (4/10): Behavioral 패턴](./04-behavioral-patterns.md)
- [Design Patterns 101 (5/10): Strategy 패턴](./05-strategy-pattern.md)
- [Design Patterns 101 (6/10): Adapter 패턴](./06-adapter-pattern.md)
- [Design Patterns 101 (7/10): Observer 패턴](./07-observer-pattern.md)
- [Design Patterns 101 (8/10): Factory와 의존성 주입](./08-factory-and-di.md)
- [Design Patterns 101 (9/10): 패턴을 남용하지 않는 법](./09-avoiding-pattern-overuse.md)
- **Python에 어울리는 패턴 (현재 글)**

<!-- toc:end -->

## 참고 자료

### 핵심 자료

- [PEP 544 — Protocols](https://peps.python.org/pep-0544/)
- [PEP 634 — Structural Pattern Matching](https://peps.python.org/pep-0634/)
- [dataclasses (Python docs)](https://docs.python.org/3/library/dataclasses.html)
- [functools.wraps (Python docs)](https://docs.python.org/3/library/functools.html#functools.wraps)

### 실무 확장 읽을거리

- [Python 3 Patterns, Recipes and Idioms (Bruce Eckel)](https://python-3-patterns-idioms-test.readthedocs.io/)
- [Fluent Python, 2nd Edition (Luciano Ramalho)](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/) — Part IV: Object-Oriented Idioms
- [PEP 20 — The Zen of Python](https://peps.python.org/pep-0020/)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/ko)

Tags: Computer Science, DesignPatterns, Python, Idioms, Protocols, Decorators
