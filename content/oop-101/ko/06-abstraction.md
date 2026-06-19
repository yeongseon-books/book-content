---
title: "Object-Oriented Programming 101 (6/10): 추상화"
series: oop-101
episode: 6
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
  - Python
  - OOP
  - 추상화
  - ABC
  - 인터페이스
last_reviewed: '2026-05-17'
seo_description: ABC와 abstractmethod로 공통 인터페이스를 강제하는 Python 추상화 설계를 설명합니다.
---

# Object-Oriented Programming 101 (6/10): 추상화

추상화는 복잡한 구현을 뒤에 숨기고, 호출자가 알아야 할 것만 앞으로 내미는 설계 원칙입니다. 잘 만든 추상화는 "어떻게"가 아닌 "무엇"을 드러냅니다. 데이터베이스에 어떻게 저장하는지, 네트워크에 어떻게 전송하는지 호출자가 알 필요 없이 `save()`, `send()`만 호출하면 됩니다.

추상화가 진짜 필요해지는 순간은 구현체가 두세 개로 늘어나면서 호출부가 어떤 메서드 이름을 불러야 할지 추측하기 시작할 때입니다. Python에서는 `abc.ABC`와 `@abstractmethod`로 명시적 계약을 강제하고, `typing.Protocol`로 구조적 서브타이핑을 제공합니다.

이 글은 OOP 101 시리즈의 6번째 글입니다.

![Object-Oriented Programming 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/oop-101/06/06-01-big-picture.ko.png)
*Object-Oriented Programming 101 6장 흐름 개요*

## 이 글에서 다룰 문제

- 추상 클래스(`ABC`)와 인터페이스(`Protocol`)는 언제 각각 선택해야 할까요?
- `@abstractmethod`를 쓰면 미구현 메서드를 컴파일 수준이 아닌 런타임에서 잡는데, 이것을 어떻게 보완할까요?
- 추상화 계층을 너무 많이 쌓으면 어떤 문제가 생기고, 어느 수준이 적절할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 이 글에서 배울 것

- `abc.ABC`와 `@abstractmethod`로 강제 계약 클래스를 만드는 법을 익힙니다
- `typing.Protocol`과 ABC의 차이를 코드로 확인합니다
- 템플릿 메서드 패턴을 구현합니다
- 추상화 계층을 적절하게 설계하는 기준을 세웁니다
- 플러그인 시스템 설계에서 추상화를 적용합니다

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 추상 클래스(ABC) | 직접 인스턴스화할 수 없는 클래스로, 하위 클래스에 계약을 강제합니다 |
| 추상 메서드 | 구현이 없고 하위 클래스에서 반드시 오버라이딩해야 하는 메서드입니다 |
| 구체 클래스 | 추상 메서드를 모두 구현한 클래스로, 인스턴스화 가능합니다 |
| Protocol | 구조적 서브타이핑을 위한 인터페이스 정의 방식입니다 |
| 템플릿 메서드 | 알고리즘의 뼈대를 정의하고 세부 구현을 하위 클래스에 위임합니다 |

## 전후 비교

알림 발송 시스템을 비교합니다.

```python
# before: 추상화 없음 — 계약이 암묵적
class EmailNotifier:
    def notify(self, message: str) -> None:
        print(f"Email: {message}")

class SMSNotifier:
    def notify(self, msg: str) -> None:  # 이름이 달라도 오류 없음
        print(f"SMS: {msg}")
```

```python
# after: ABC로 계약 명시 — 미구현 시 인스턴스화 불가
from abc import ABC, abstractmethod

class Notifier(ABC):
    @abstractmethod
    def notify(self, message: str) -> None:
        """Send notification with message."""

    @abstractmethod
    def channel_name(self) -> str:
        """Return channel identifier."""

class EmailNotifier(Notifier):
    def notify(self, message: str) -> None:
        print(f"[Email] {message}")

    def channel_name(self) -> str:
        return "email"

class SMSNotifier(Notifier):
    def notify(self, message: str) -> None:
        print(f"[SMS] {message}")

    def channel_name(self) -> str:
        return "sms"

def send_all(notifiers: list[Notifier], message: str) -> None:
    for n in notifiers:
        print(f"Sending via {n.channel_name()}")
        n.notify(message)

send_all([EmailNotifier(), SMSNotifier()], "Order confirmed!")
```

## 단계별 실습

### 1단계: 추상 기반 클래스 기본

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    def __init__(self, color: str = "black") -> None:
        self.color = color

    @abstractmethod
    def area(self) -> float:
        """Calculate area."""

    @abstractmethod
    def perimeter(self) -> float:
        """Calculate perimeter."""

    def describe(self) -> str:
        """구체 메서드 — 오버라이딩 가능하지만 필수 아님"""
        return (
            f"{self.__class__.__name__} ({self.color}): "
            f"area={self.area():.2f}, perimeter={self.perimeter():.2f}"
        )

class Circle(Shape):
    def __init__(self, radius: float, color: str = "black") -> None:
        super().__init__(color)
        self.radius = radius

    def area(self) -> float:
        import math
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
        import math
        return 2 * math.pi * self.radius

class Triangle(Shape):
    def __init__(self, a: float, b: float, c: float) -> None:
        super().__init__()
        if a + b <= c or a + c <= b or b + c <= a:
            raise ValueError("Invalid triangle sides")
        self.a, self.b, self.c = a, b, c

    def area(self) -> float:
        s = (self.a + self.b + self.c) / 2
        return (s * (s - self.a) * (s - self.b) * (s - self.c)) ** 0.5

    def perimeter(self) -> float:
        return self.a + self.b + self.c

shapes: list[Shape] = [Circle(5, "red"), Triangle(3, 4, 5)]
for s in shapes:
    print(s.describe())
```

`Shape()`를 직접 호출하면 `TypeError: Can't instantiate abstract class Shape`가 발생합니다. 모든 추상 메서드를 구현한 하위 클래스만 인스턴스화할 수 있습니다.

### 2단계: 템플릿 메서드 패턴

```python
from abc import ABC, abstractmethod

class DataProcessor(ABC):
    """알고리즘 뼈대를 정의하고 세부 단계를 하위 클래스에 위임"""

    def process(self, data: list) -> list:
        """템플릿 메서드 — 처리 순서를 고정"""
        validated = self.validate(data)
        transformed = self.transform(validated)
        return self.output(transformed)

    @abstractmethod
    def validate(self, data: list) -> list:
        """Filter invalid records."""

    @abstractmethod
    def transform(self, data: list) -> list:
        """Apply business logic."""

    def output(self, data: list) -> list:
        """기본 구현 제공 — 필요 시 오버라이딩"""
        return data

class SalesProcessor(DataProcessor):
    def validate(self, data: list) -> list:
        return [d for d in data if d.get("amount", 0) > 0]

    def transform(self, data: list) -> list:
        return [{**d, "tax": int(d["amount"] * 0.1)} for d in data]

class ReturnProcessor(DataProcessor):
    def validate(self, data: list) -> list:
        return [d for d in data if d.get("reason")]

    def transform(self, data: list) -> list:
        return [{**d, "refund": d["amount"]} for d in data]

sales = [{"id": "S1", "amount": 10000}, {"id": "S2", "amount": -500}]
result = SalesProcessor().process(sales)
print(result)  # [{'id': 'S1', 'amount': 10000, 'tax': 1000}]
```

### 3단계: ABC vs Protocol 비교

```python
# ABC 방식: 명시적 상속 필요, 공통 구현 공유 가능
from abc import ABC, abstractmethod

class Repository(ABC):
    @abstractmethod
    def find(self, id: str) -> dict | None:
        ...

    @abstractmethod
    def save(self, entity: dict) -> None:
        ...

    def exists(self, id: str) -> bool:
        """공통 로직 ABC에 포함"""
        return self.find(id) is not None

# Protocol 방식: 상속 불필요, 외부 클래스도 만족 가능
from typing import Protocol

class Fetchable(Protocol):
    def find(self, id: str) -> dict | None:
        ...

# 어떤 클래스든 find(id) 메서드가 있으면 Fetchable을 만족
```

선택 기준: 공통 구현(기본 메서드)을 공유해야 하거나 내부 팀 계약이면 ABC, 외부 라이브러리 통합이나 런타임 교체가 자주 일어나면 Protocol이 적합합니다.

### 4단계: 추상 프로퍼티

```python
from abc import ABC, abstractmethod

class DatabaseConnection(ABC):
    @property
    @abstractmethod
    def connection_string(self) -> str:
        """Database connection URL."""

    @abstractmethod
    def execute(self, query: str) -> list:
        """Execute a query."""

    @abstractmethod
    def close(self) -> None:
        """Close the connection."""

    def __enter__(self) -> "DatabaseConnection":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

class PostgresConnection(DatabaseConnection):
    def __init__(self, host: str, port: int, database: str) -> None:
        self.host = host
        self.port = port
        self.database = database

    @property
    def connection_string(self) -> str:
        return f"postgresql://{self.host}:{self.port}/{self.database}"

    def execute(self, query: str) -> list:
        print(f"[Postgres] {query}")
        return []

    def close(self) -> None:
        print("[Postgres] Connection closed")

with PostgresConnection("localhost", 5432, "mydb") as conn:
    print(conn.connection_string)
    conn.execute("SELECT * FROM users")
```

### 5단계: 플러그인 시스템

```python
from abc import ABC, abstractmethod
from typing import ClassVar

class Plugin(ABC):
    NAME: ClassVar[str] = ""
    PRIORITY: ClassVar[int] = 0

    @abstractmethod
    def execute(self, context: dict) -> dict:
        """Execute plugin logic and return modified context."""

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate plugin configuration."""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(priority={self.PRIORITY})"

class LoggingPlugin(Plugin):
    NAME = "logging"
    PRIORITY = 10

    def execute(self, context: dict) -> dict:
        print(f"[LOG] context keys: {list(context.keys())}")
        return context

    def validate_config(self) -> bool:
        return True

class TimestampPlugin(Plugin):
    NAME = "timestamp"
    PRIORITY = 5

    def execute(self, context: dict) -> dict:
        from datetime import datetime
        context["processed_at"] = datetime.now().isoformat()
        return context

    def validate_config(self) -> bool:
        return True

class PluginRunner:
    def __init__(self) -> None:
        self._plugins: list[Plugin] = []

    def register(self, plugin: Plugin) -> None:
        if not plugin.validate_config():
            raise ValueError(f"Invalid config for {plugin.NAME}")
        self._plugins.append(plugin)
        self._plugins.sort(key=lambda p: p.PRIORITY)

    def run(self, context: dict) -> dict:
        for plugin in self._plugins:
            context = plugin.execute(context)
        return context

runner = PluginRunner()
runner.register(LoggingPlugin())
runner.register(TimestampPlugin())
result = runner.run({"user_id": "u1", "action": "checkout"})
print(result.get("processed_at"))
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 추상 클래스를 직접 인스턴스화 | `TypeError`가 발생합니다 | 구체 하위 클래스를 만들어 사용합니다 |
| `@abstractmethod` 없이 ABC만 상속 | 계약이 강제되지 않습니다 | 필수 메서드에 `@abstractmethod`를 붙입니다 |
| ABC와 Protocol을 혼용 | 추상화 계층이 복잡해집니다 | 외부 통합에는 Protocol, 내부 계약에는 ABC를 선택합니다 |
| 추상화 계층을 4단계 이상 쌓음 | 변경 추적이 어려워집니다 | 2~3단계로 제한합니다 |
| `raise NotImplementedError`로 추상 메서드 흉내 | 미구현이 인스턴스화 시 아닌 호출 시 잡힙니다 | `@abstractmethod`가 더 안전합니다 |

## 실무에서 이렇게 쓰입니다

```python
from abc import ABC, abstractmethod
from typing import Any

class CacheBackend(ABC):
    @abstractmethod
    def get(self, key: str) -> Any:
        ...

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        ...

    @abstractmethod
    def delete(self, key: str) -> bool:
        ...

    def get_or_set(self, key: str, factory: callable, ttl: int = 300) -> Any:
        """공통 캐시 패턴 — 하위 클래스가 재정의 불필요"""
        value = self.get(key)
        if value is None:
            value = factory()
            self.set(key, value, ttl)
        return value

class InMemoryCache(CacheBackend):
    def __init__(self) -> None:
        self._store: dict = {}

    def get(self, key: str) -> Any:
        return self._store.get(key)

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        self._store[key] = value

    def delete(self, key: str) -> bool:
        return self._store.pop(key, None) is not None

cache = InMemoryCache()
result = cache.get_or_set("user:1", lambda: {"name": "Alice"})
print(result)  # {'name': 'Alice'}
```

## 현업 개발자는 이렇게 생각합니다

추상화는 경계를 선명하게 만드는 도구입니다. "이 계층은 이 계약만 알면 된다"를 명시할 때 ABC나 Protocol을 씁니다. 하지만 모든 클래스를 추상화로 감싸면 오히려 코드 탐색이 어려워집니다.

실무 기준은 간단합니다. 구현이 두 개 이상 생길 것으로 예상되는 지점, 또는 테스트에서 Mock으로 대체해야 하는 의존성에 추상화를 도입합니다. 하나의 구현만 있고 앞으로도 그럴 것 같다면 추상화를 미룹니다.

## 운영 체크리스트

- [ ] `ABC`와 `@abstractmethod`로 계약 클래스를 만들 수 있다
- [ ] 추상 클래스를 직접 인스턴스화하면 `TypeError`가 남을 확인했다
- [ ] 템플릿 메서드 패턴을 구현할 수 있다
- [ ] ABC와 Protocol의 선택 기준을 설명할 수 있다
- [ ] 추상화 계층 깊이를 적절하게 유지할 수 있다

## 연습 문제

1. `Animal` ABC를 만드세요. `speak()`, `move()`, `eat()` 추상 메서드를 정의하고, `Dog`와 `Bird`를 구현합니다.
2. `ReportGenerator` ABC에 템플릿 메서드를 구현하세요. `fetch_data()`, `format_data()`, `export()` 단계를 정의하고, CSV와 HTML 버전을 만듭니다.
3. `CacheBackend` Protocol을 별도로 정의하고, ABC 버전과 Protocol 버전의 차이를 설명하는 문서를 작성하세요.

## 정리 및 다음 단계

추상화는 구현의 복잡성을 숨기고 계약으로 소통하는 설계 원칙입니다. Python에서는 ABC로 명시적 계약을, Protocol로 유연한 구조적 서브타이핑을 구현합니다.

다음 글에서는 합성과 상속의 실무적 선택 기준을 다룹니다. 언제 상속을 쓰고, 언제 합성이 더 나은지 코드로 비교합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Object-Oriented Programming 101 (1/10): 객체지향이란 무엇인가?](./01-what-is-oop.md)
- [Object-Oriented Programming 101 (2/10): 클래스와 인스턴스](./02-classes-and-instances.md)
- [Object-Oriented Programming 101 (3/10): 캡슐화](./03-encapsulation.md)
- [Object-Oriented Programming 101 (4/10): 상속](./04-inheritance.md)
- [Object-Oriented Programming 101 (5/10): 다형성](./05-polymorphism.md)
- **Object-Oriented Programming 101 (6/10): 추상화 (현재 글)**
- [Object-Oriented Programming 101 (7/10): 합성과 상속](./07-composition-vs-inheritance.md)
- [Object-Oriented Programming 101 (8/10): SOLID 원칙 기초](./08-solid-principles.md)
- [Object-Oriented Programming 101 (9/10): 객체지향 설계 예제](./09-oop-design-example.md)
- [객체지향을 언제 피해야 할까?](./10-when-to-avoid-oop.md)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — abc 모듈](https://docs.python.org/3/library/abc.html)
- [PEP 544 — Protocols: Structural subtyping](https://peps.python.org/pep-0544/)
- [Real Python — Abstract Base Classes](https://realpython.com/python-interface/)
- [Fluent Python — Chapter 13: Interfaces, Protocols, and ABCs](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/oop-101/ko)
Tags: Python, OOP, 추상화, ABC, 인터페이스
