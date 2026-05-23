---
series: design-patterns-101
episode: 4
title: "디자인 패턴 101 (4/10): 행위 패턴"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - DesignPatterns
  - Behavioral
  - Strategy
  - Observer
  - Command
seo_description: Behavioral 패턴으로 객체 협력과 흐름을 읽기 쉬운 구조로 바꾸는 방법을 설명합니다.
last_reviewed: '2026-05-23'
---

# 디자인 패턴 101 (4/10): 행위 패턴

코드를 잘 나눠 놓았는데도 변경이 어려운 순간이 있습니다. 클래스 하나를 고치면 알림 로직이 깨지고, 상태 전이를 추가하면 기존 분기가 흔들리고, 정렬 방식을 바꾸려면 호출부 전체를 뒤져야 합니다. 이런 문제는 구조가 아니라 **객체 사이의 책임 흐름**이 꼬여 있을 때 나타납니다. Behavioral 패턴은 바로 이 흐름에 이름을 붙이고, 변경이 번지지 않도록 경계를 만드는 도구입니다.

이 글은 Design Patterns 101 시리즈의 네 번째 글입니다. Strategy와 Observer는 뒤에 각각 독립 장(5장, 7장)이 있으므로 여기서는 개요 수준으로 다루고, Command, Iterator, State, Template Method, Chain of Responsibility에 더 많은 지면을 할애합니다.

![행위 패턴 책임 흐름](https://yeongseon-books.github.io/book-public-assets/assets/design-patterns-101/04/04-01-concept-at-a-glance.ko.png)
*행위 패턴이 다루는 책임 분배 — 알고리즘 교체, 이벤트 전파, 요청 객체화, 상태 전이, 순회 추상화*

## 먼저 던지는 질문

- Command가 단순한 함수 호출과 다른 점은 무엇일까요?
- State와 Strategy는 코드 모양이 거의 같은데, 왜 별도 패턴으로 분류될까요?
- Python에서 Iterator 패턴을 명시적으로 구현할 일이 거의 없는 이유는 무엇일까요?

## 객체 간 책임 분배가 어려운 이유

Creational 패턴은 "누가 만드는가", Structural 패턴은 "어떻게 묶는가"를 다룹니다. Behavioral 패턴은 그 다음 질문입니다. **만들어진 객체들이 서로 어떻게 대화하고, 누가 어떤 결정을 내리는가.**

저는 이 문제가 어려운 이유를 두 가지로 봅니다.

첫째, 책임 흐름은 코드에 명시적으로 드러나지 않습니다. 클래스 다이어그램에는 "A가 B를 호출한다"는 화살표가 보이지만, "A가 B에게 알릴지 말지를 누가 결정하는가", "A의 알고리즘을 런타임에 바꿀 수 있는가"는 보이지 않습니다.

둘째, 책임 분배를 잘못하면 변경이 연쇄적으로 번집니다. 결제 상태를 하나 추가했을 뿐인데 알림 로직, 로깅 로직, UI 렌더링 로직이 동시에 깨지는 경험을 해 본 적이 있다면, 그게 바로 책임 경계가 없는 상태입니다.

Behavioral 패턴 10개는 이 문제를 각각 다른 각도에서 풉니다. 이 글에서는 실무에서 가장 자주 만나는 7개를 다룹니다.

## Strategy와 Observer — 개요

이 두 패턴은 5장과 7장에서 깊게 다루므로 여기서는 핵심만 짚습니다.

**Strategy**는 알고리즘을 호출부에서 분리해 교체 가능하게 만듭니다. Python에서는 함수가 일급 객체이므로 클래스 없이도 Strategy를 적용할 수 있습니다.

```python
from typing import Callable

PricingStrategy = Callable[[int], int]

def no_discount(price: int) -> int:
    return price

def vip_discount(price: int) -> int:
    return int(price * 0.7)

def checkout(price: int, strategy: PricingStrategy = no_discount) -> int:
    return strategy(price)
```

**Observer**는 한 객체의 상태 변화를 여러 구독자에게 전파합니다. 발행자는 구독자가 누구인지 모르고, 구독자는 발행자의 내부를 모릅니다. Django signals, JavaScript의 `addEventListener`, Redis Pub/Sub 모두 이 구조입니다.

두 패턴의 공통점은 **간접 호출을 도입해 결합을 끊는다**는 것이고, 차이는 Strategy가 1:1 교체인 반면 Observer는 1:N 전파라는 점입니다.

## Command가 단순한 함수 호출과 다른 점

함수를 호출하면 그 자리에서 실행되고 끝납니다. Command 패턴은 "실행할 행위"를 객체로 만들어 **저장, 전달, 지연 실행, 취소**를 가능하게 합니다.

저는 이 차이를 "전화 통화 vs. 편지"에 비유합니다. 전화는 즉시 연결되지만 기록이 남지 않습니다. 편지는 보관할 수 있고, 순서를 바꿀 수 있고, 나중에 열어볼 수 있습니다.

### Undo 스택 예시

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol


class Command(Protocol):
    def execute(self) -> None: ...
    def undo(self) -> None: ...


@dataclass
class InsertText:
    document: list[str]
    position: int
    text: str

    def execute(self) -> None:
        self.document.insert(self.position, self.text)

    def undo(self) -> None:
        self.document.pop(self.position)


@dataclass
class Editor:
    document: list[str] = field(default_factory=list)
    history: list[Command] = field(default_factory=list)

    def run(self, cmd: Command) -> None:
        cmd.execute()
        self.history.append(cmd)

    def undo_last(self) -> None:
        if self.history:
            self.history.pop().undo()
```

```python
editor = Editor()
editor.run(InsertText(editor.document, 0, "Hello"))
editor.run(InsertText(editor.document, 1, "World"))
assert editor.document == ["Hello", "World"]

editor.undo_last()
assert editor.document == ["Hello"]
```

Command가 함수 호출과 결정적으로 다른 지점은 세 가지입니다.

1. **직렬화 가능** — Command 객체를 JSON이나 DB에 저장하면 작업 큐가 됩니다.
2. **취소 가능** — `undo` 메서드를 구현하면 실행을 되돌릴 수 있습니다.
3. **조합 가능** — 여러 Command를 묶어 트랜잭션처럼 다룰 수 있습니다.

### 잃는 것

Command를 도입하면 단순한 메서드 호출 하나가 클래스 하나로 바뀝니다. 행위가 10개면 클래스도 10개입니다. 취소가 필요 없고 큐잉도 필요 없다면 이 비용은 정당화되지 않습니다.

## State와 Strategy는 왜 코드 모양이 같아 보이는가

둘 다 "행위를 별도 객체에 위임한다"는 구조입니다. 클래스 다이어그램만 보면 거의 동일합니다. 차이는 **의도**에 있습니다.

- **Strategy**: 호출자가 알고리즘을 선택합니다. 한번 주입하면 보통 바뀌지 않습니다.
- **State**: 객체 스스로가 내부 상태에 따라 행위를 전환합니다. 전환은 런타임에 반복적으로 일어납니다.

### TCP 연결 상태 머신

```python
from __future__ import annotations
from typing import Protocol


class ConnectionState(Protocol):
    def open(self, ctx: Connection) -> None: ...
    def close(self, ctx: Connection) -> None: ...
    def send(self, ctx: Connection, data: bytes) -> None: ...


class Closed:
    def open(self, ctx: Connection) -> None:
        print("Opening connection...")
        ctx.state = Established()

    def close(self, ctx: Connection) -> None:
        print("Already closed.")

    def send(self, ctx: Connection, data: bytes) -> None:
        raise RuntimeError("Cannot send on closed connection")


class Established:
    def open(self, ctx: Connection) -> None:
        print("Already open.")

    def close(self, ctx: Connection) -> None:
        print("Closing connection...")
        ctx.state = Closed()

    def send(self, ctx: Connection, data: bytes) -> None:
        print(f"Sending {len(data)} bytes")


class Connection:
    def __init__(self) -> None:
        self.state: ConnectionState = Closed()

    def open(self) -> None:
        self.state.open(self)

    def close(self) -> None:
        self.state.close(self)

    def send(self, data: bytes) -> None:
        self.state.send(self, data)
```

`Connection`은 자신의 상태를 모릅니다. 각 상태 객체가 "다음에 어떤 상태로 갈지"를 결정합니다. 이 구조 덕분에 새 상태(예: `Listening`)를 추가할 때 기존 상태 클래스를 수정하지 않아도 됩니다.

### 잃는 것

상태가 3개 이하이고 전이가 단순하면 `if/elif`가 더 읽기 쉽습니다. State 패턴은 상태 수가 5개 이상이거나, 전이 규칙이 복잡해서 표로 그려야 이해되는 수준일 때 비용을 회수합니다.

## Iterator는 왜 Python에서 거의 등장하지 않는가

GoF의 Iterator 패턴은 "내부 구조를 노출하지 않고 컬렉션을 순회하는 방법"을 제공합니다. Java에서는 `Iterator<T>` 인터페이스를 직접 구현해야 하지만, Python은 이 패턴을 **언어 자체에 녹여 넣었습니다.**

```python
class SensorReadings:
    """최근 N개의 센서 값을 순환 버퍼로 저장합니다."""

    def __init__(self, capacity: int) -> None:
        self._buf: list[float] = []
        self._capacity = capacity

    def add(self, value: float) -> None:
        if len(self._buf) >= self._capacity:
            self._buf.pop(0)
        self._buf.append(value)

    def __iter__(self):
        """내부 버퍼 구조를 노출하지 않고 순회를 허용합니다."""
        return iter(self._buf)

    def __len__(self) -> int:
        return len(self._buf)
```

`__iter__`를 구현하는 순간 `for` 루프, `list()`, `sum()`, 언패킹 등 Python의 모든 이터레이션 프로토콜과 호환됩니다. 별도 `Iterator` 클래스를 만들 필요가 없습니다.

더 복잡한 순회가 필요하면 제너레이터가 있습니다.

```python
from pathlib import Path
from typing import Iterator


def walk_python_files(root: Path) -> Iterator[Path]:
    """디렉터리를 재귀 순회하되 .py 파일만 yield합니다."""
    for child in sorted(root.iterdir()):
        if child.is_dir() and not child.name.startswith("."):
            yield from walk_python_files(child)
        elif child.suffix == ".py":
            yield child
```

제너레이터는 상태를 자동으로 관리하고, `yield`에서 멈췄다가 다음 호출에서 이어갑니다. GoF Iterator가 풀려던 문제를 언어가 이미 해결한 셈입니다.

### 잃는 것

Python에서 Iterator 패턴을 "잃는다"기보다는, 패턴을 의식하지 않아도 되는 대신 **`__iter__`를 빠뜨리는 실수**가 생깁니다. 커스텀 컬렉션을 만들 때 `__iter__`를 구현하지 않으면 `for` 루프에서 `TypeError`가 나고, 디버깅에 시간을 씁니다.

## Template Method를 함수형으로 다시 보면

Template Method는 알고리즘의 뼈대를 부모 클래스에 고정하고, 세부 단계를 자식 클래스가 채우는 패턴입니다. GoF 시절에는 상속이 유일한 선택지였지만, Python에서는 함수를 넘기는 방식이 더 자연스러울 때가 많습니다.

### 상속 기반 — ETL 파이프라인

```python
from abc import ABC, abstractmethod
from typing import Any


class ETLPipeline(ABC):
    """뼈대: extract → transform → load 순서는 고정."""

    def run(self) -> None:
        raw = self.extract()
        cleaned = self.transform(raw)
        self.load(cleaned)

    @abstractmethod
    def extract(self) -> list[dict[str, Any]]: ...

    @abstractmethod
    def transform(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]: ...

    @abstractmethod
    def load(self, data: list[dict[str, Any]]) -> None: ...


class CsvToPostgres(ETLPipeline):
    def extract(self) -> list[dict[str, Any]]:
        # CSV 파일 읽기
        return [{"name": "Alice", "age": "30"}]

    def transform(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [{"name": r["name"], "age": int(r["age"])} for r in data]

    def load(self, data: list[dict[str, Any]]) -> None:
        print(f"Inserting {len(data)} rows into PostgreSQL")
```

### 함수 합성 기반 — 같은 문제, 다른 모양

```python
from typing import Any, Callable

ExtractFn = Callable[[], list[dict[str, Any]]]
TransformFn = Callable[[list[dict[str, Any]]], list[dict[str, Any]]]
LoadFn = Callable[[list[dict[str, Any]]], None]


def run_etl(extract: ExtractFn, transform: TransformFn, load: LoadFn) -> None:
    load(transform(extract()))
```

함수 합성 버전은 상속 계층이 없고, 각 단계를 독립적으로 테스트하기 쉽습니다. 단, 단계 간 공유 상태가 많거나 단계 수가 7-8개로 늘어나면 클래스 기반이 더 읽기 쉬워집니다.

### 잃는 것

Template Method는 상속을 강제합니다. Python에서 깊은 상속 계층은 디버깅을 어렵게 만듭니다. 단계가 3개 이하이고 공유 상태가 없다면 함수 합성이 더 낫습니다.

## Chain of Responsibility — 요청을 누가 처리할지 모를 때

Chain of Responsibility는 요청을 처리할 수 있는 객체들을 체인으로 연결하고, 요청이 체인을 따라 흐르다가 처리 가능한 핸들러를 만나면 멈추는 구조입니다.

저는 이 패턴을 웹 프레임워크의 미들웨어 스택에서 가장 자주 봅니다. Django의 미들웨어, Express의 `next()`, FastAPI의 dependency chain 모두 이 구조입니다.

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol


@dataclass
class Request:
    path: str
    headers: dict[str, str]
    user: str | None = None


class Handler(Protocol):
    def handle(self, request: Request) -> str | None: ...


@dataclass
class AuthHandler:
    next_handler: Handler | None = None

    def handle(self, request: Request) -> str | None:
        token = request.headers.get("Authorization")
        if not token:
            return "401 Unauthorized"
        request.user = token.split(" ")[-1]  # 단순화
        if self.next_handler:
            return self.next_handler.handle(request)
        return None


@dataclass
class RateLimitHandler:
    next_handler: Handler | None = None
    _counter: int = 0

    def handle(self, request: Request) -> str | None:
        self._counter += 1
        if self._counter > 100:
            return "429 Too Many Requests"
        if self.next_handler:
            return self.next_handler.handle(request)
        return None


@dataclass
class RouteHandler:
    next_handler: Handler | None = None

    def handle(self, request: Request) -> str | None:
        return f"200 OK — {request.path} by {request.user}"
```

```python
# 체인 조립
chain = AuthHandler(next_handler=RateLimitHandler(next_handler=RouteHandler()))

req = Request(path="/api/data", headers={"Authorization": "Bearer alice"})
result = chain.handle(req)
assert result == "200 OK — /api/data by alice"
```

### 잃는 것

체인이 길어지면 "이 요청이 어디서 처리됐는지" 추적이 어렵습니다. 디버깅할 때 체인의 모든 핸들러를 순서대로 따라가야 합니다. 핸들러가 3개 이하라면 단순한 `if/elif`가 더 명확합니다.

## Mediator와 Memento — 간략 소개

**Mediator**는 객체들이 서로 직접 참조하지 않고 중재자를 통해 소통하게 만듭니다. 채팅방이 대표적입니다. 사용자 A가 메시지를 보내면 채팅방(Mediator)이 다른 사용자들에게 전달합니다. GUI 프레임워크에서 폼 컴포넌트 간 상호작용을 조율할 때도 이 구조가 나타납니다.

**Memento**는 객체의 내부 상태를 외부에 저장했다가 복원하는 패턴입니다. 텍스트 에디터의 undo, 게임의 세이브/로드가 전형적인 예입니다. Command의 `undo`와 비슷해 보이지만, Command는 "행위의 역연산"이고 Memento는 "상태의 스냅샷"이라는 점이 다릅니다.

## Visitor — 구조를 바꾸지 않고 연산을 추가하기

Visitor는 객체 구조(예: AST, 파일 트리)를 순회하면서 각 노드 타입에 맞는 연산을 수행합니다. Python에서는 `functools.singledispatch`나 패턴 매칭(`match/case`)이 비슷한 역할을 하므로 GoF 스타일의 Visitor를 직접 구현할 일은 드뭅니다.

## 패턴별 트레이드오프 정리

| 패턴 | 얻는 것 | 잃는 것 |
| --- | --- | --- |
| Strategy | 알고리즘 교체가 한 줄 | 간접 호출 추가, 전략 객체 관리 |
| Observer | 발행자-구독자 완전 분리 | 순환 알림 위험, 디버깅 어려움 |
| Command | 저장·취소·큐잉 가능 | 행위 하나당 클래스 하나 |
| State | 상태 전이 규칙이 명시적 | 상태 수만큼 클래스 증가 |
| Iterator | 내부 구조 은닉 | Python에서는 언어가 이미 제공 |
| Template Method | 알고리즘 뼈대 고정 | 상속 강제, 깊은 계층 위험 |
| Chain of Responsibility | 핸들러 추가/제거 유연 | 요청 추적 어려움 |
| Mediator | 객체 간 직접 결합 제거 | 중재자가 God Object가 될 위험 |
| Memento | 상태 복원 가능 | 메모리 사용량 증가 |
| Visitor | 구조 변경 없이 연산 추가 | 새 노드 타입 추가 시 모든 Visitor 수정 |

## 처음 질문으로 돌아가기

- **Command가 단순한 함수 호출과 다른 점은 무엇일까요?**
  - 함수 호출은 즉시 실행되고 사라지지만, Command는 행위를 객체로 만들어 저장·전달·취소를 가능하게 합니다. Editor 예시에서 `InsertText` 객체를 `history` 리스트에 쌓아 두고 `undo_last()`로 되돌린 것이 그 차이입니다. 큐잉이나 재시도가 필요한 순간 Command의 가치가 드러납니다.

- **State와 Strategy는 코드 모양이 거의 같은데, 왜 별도 패턴으로 분류될까요?**
  - 둘 다 행위를 위임하지만, Strategy는 호출자가 외부에서 알고리즘을 선택하고 보통 한번 주입하면 바뀌지 않습니다. State는 객체 자신이 내부 상태에 따라 행위를 반복적으로 전환합니다. TCP Connection 예시에서 `Closed`가 스스로 `Established`로 전이하는 것이 Strategy에는 없는 특징입니다.

- **Python에서 Iterator 패턴을 명시적으로 구현할 일이 거의 없는 이유는 무엇일까요?**
  - Python이 `__iter__`/`__next__` 프로토콜과 제너레이터를 언어 수준에서 제공하기 때문입니다. `SensorReadings` 예시처럼 `__iter__`만 구현하면 `for` 루프, `sum()`, 언패킹 등 모든 이터레이션 인프라와 자동으로 호환됩니다. GoF가 별도 Iterator 클래스로 풀었던 문제를 언어가 이미 해결한 셈입니다.

<!-- toc:begin -->
## 시리즈 목차

- [디자인 패턴이란 무엇인가?](./01-what-are-design-patterns.md)
- [Creational 패턴](./02-creational-patterns.md)
- [Structural 패턴](./03-structural-patterns.md)
- **Behavioral 패턴 (현재 글)**
- Strategy 패턴 (예정)
- Adapter 패턴 (예정)
- Observer 패턴 (예정)
- Factory와 의존성 주입 (예정)
- 패턴을 남용하지 않는 법 (예정)
- Python에 어울리는 패턴 (예정)

<!-- toc:end -->

## 참고 자료

### 핵심 자료

- [Strategy Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/strategy)
- [Observer Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/observer)
- [Command Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/command)
- [State Pattern (refactoring.guru)](https://refactoring.guru/design-patterns/state)
- [Chain of Responsibility (refactoring.guru)](https://refactoring.guru/design-patterns/chain-of-responsibility)

### 실무 확장 읽을거리

- [The Python Language Reference — Data model (`__iter__`)](https://docs.python.org/3/reference/datamodel.html)
- [Python `functools.singledispatch`](https://docs.python.org/3/library/functools.html#functools.singledispatch)
- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/design-patterns-101/ko)

Tags: Computer Science, DesignPatterns, Behavioral, Strategy, Observer, Command
