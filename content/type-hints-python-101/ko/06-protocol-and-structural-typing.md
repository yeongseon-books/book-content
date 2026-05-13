---
series: type-hints-python-101
episode: 6
title: Protocol과 structural typing
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
  - Type Hints
  - Protocol
  - structural typing
  - 덕 타이핑
  - 인터페이스
seo_description: Protocol로 상속 없이 인터페이스를 정의하고 structural typing을 활용하는 방법을 다룹니다.
last_reviewed: '2026-05-12'
---

# Protocol과 structural typing

Python은 오래전부터 덕 타이핑을 써 왔습니다. `close()`가 있으면 닫을 수 있는 객체로 취급하고, `render()`가 있으면 렌더링 가능한 객체로 취급합니다. 그런데 전통적인 추상 베이스 클래스는 여전히 명시적 상속을 요구합니다.

이 글은 Type Hints (Python) 101 시리즈의 6번째 글입니다. 여기서는 `Protocol`로 "이 메서드가 있으면 충분하다"는 계약을 어떻게 적는지, 그리고 그것이 structural typing과 어떻게 연결되는지 살펴봅니다.

## 이 글에서 다룰 문제

- 상속 없이 인터페이스 계약을 적을 수 있을까요?
- ABC와 Protocol은 무엇이 다를까요?
- 속성만으로도 Protocol을 만족시킬 수 있을까요?
- 런타임 `isinstance()` 검사가 필요하면 어떻게 해야 할까요?

> Protocol은 Python의 덕 타이핑 철학을 정적 타입 시스템 안으로 가져오는 장치입니다.

## 왜 이 주제가 중요한가

상속 기반 인터페이스는 결합도를 높입니다. 외부 라이브러리 클래스나 이미 만들어진 내부 클래스가 필요한 메서드를 모두 갖고 있어도, 베이스 클래스를 상속하지 않았다는 이유만으로 타입 호환이 깨질 수 있습니다. `Protocol`은 이 문제를 줄입니다.

즉, 중요한 것은 계보가 아니라 구조입니다. 필요한 메서드와 속성이 있으면 타입 검사기는 그 객체를 호환 가능한 것으로 봅니다. 이 방식은 Python 런타임의 실제 사용 방식과도 잘 맞습니다.

## 한눈에 보는 개념

```text
class Closeable(Protocol):     class FileHandler:
    def close(self) -> None:       def close(self) -> None:
        ...                            self.file.close()

        │                                    │
        └──── 구조가 맞으므로 호환됨 ───────────┘
                 (상속 필요 없음)
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| Protocol | 필요한 메서드와 속성을 정의하지만 상속을 강제하지 않는 타입 계약입니다 |
| structural typing | 상속 계보가 아니라 구조로 타입 호환성을 판단하는 방식입니다 |
| nominal typing | 명시적 클래스 계층으로 호환성을 판단하는 방식입니다 |
| @runtime_checkable | Protocol에 대해 `isinstance()`를 허용하는 데코레이터입니다 |
| ABC | 공통 구현과 추상 메서드를 함께 둘 수 있는 상속 기반 추상 클래스입니다 |

## 바꾸기 전과 후

```python
from abc import ABC, abstractmethod


class Closeable(ABC):
    @abstractmethod
    def close(self) -> None: ...


class FileHandler(Closeable):  # 상속 필요
    def close(self) -> None:
        print("closed")


def cleanup(resource: Closeable) -> None:
    resource.close()
```

```python
from typing import Protocol


class Closeable(Protocol):
    def close(self) -> None: ...


class FileHandler:  # 상속 불필요
    def close(self) -> None:
        print("closed")


def cleanup(resource: Closeable) -> None:
    resource.close()


cleanup(FileHandler())  # OK
```

## 단계별로 익히기

### 1단계: 기본 Protocol 정의하기

```python
from typing import Protocol


class Renderable(Protocol):
    def render(self) -> str: ...


class HtmlWidget:
    def render(self) -> str:
        return "<div>Hello</div>"


class JsonResponse:
    def render(self) -> str:
        return '{"message": "hello"}'


def display(item: Renderable) -> None:
    print(item.render())


display(HtmlWidget())     # OK
display(JsonResponse())   # OK
```

둘 다 `Renderable`을 상속하지 않았지만, `render() -> str` 구조가 맞기 때문에 호환됩니다.

### 2단계: 속성을 가진 Protocol

```python
from typing import Protocol


class Named(Protocol):
    name: str


class User:
    def __init__(self, name: str) -> None:
        self.name = name


class Product:
    def __init__(self, name: str, price: int) -> None:
        self.name = name
        self.price = price


def greet(entity: Named) -> str:
    return f"Hello, {entity.name}!"


greet(User("Alice"))             # OK
greet(Product("Book", 25))       # OK
```

메서드뿐 아니라 속성도 Protocol 계약에 넣을 수 있습니다.

### 3단계: `@runtime_checkable`

```python
from typing import Protocol, runtime_checkable


@runtime_checkable
class Sizeable(Protocol):
    def __len__(self) -> int: ...


print(isinstance([1, 2, 3], Sizeable))   # True
print(isinstance("hello", Sizeable))     # True
print(isinstance(42, Sizeable))          # False
```

다만 이 검사는 메서드 존재 여부만 확인할 뿐, 시그니처 전체를 정밀하게 검증하지는 않습니다.

### 4단계: Protocol 상속으로 합성하기

```python
from typing import Protocol


class Readable(Protocol):
    def read(self) -> str: ...


class Writable(Protocol):
    def write(self, data: str) -> None: ...


class ReadWritable(Readable, Writable, Protocol):
    ...


class FileHandler:
    def read(self) -> str:
        return "data"

    def write(self, data: str) -> None:
        print(f"Writing: {data}")


def process(stream: ReadWritable) -> None:
    content = stream.read()
    stream.write(content.upper())


process(FileHandler())  # OK
```

### 5단계: ABC와 Protocol의 선택 기준

```python
from abc import ABC, abstractmethod
from typing import Protocol


# 모든 구현 클래스를 직접 관리하고, 공통 구현도 주고 싶을 때
class BasePlugin(ABC):
    @abstractmethod
    def execute(self) -> None: ...

    def log(self) -> None:
        print(f"Running {self.__class__.__name__}")


# 외부 클래스도 구조만 맞으면 받으려 할 때
class Executable(Protocol):
    def execute(self) -> None: ...
```

공통 구현이 필요하면 ABC가 맞고, 느슨한 인터페이스 계약이 필요하면 Protocol이 더 잘 맞습니다.

## 여기서 먼저 봐야 할 점

- Protocol은 구현보다 시그니처를 정의하는 도구입니다.
- 구조만 맞으면 상속 없이도 호환됩니다.
- `@runtime_checkable`은 제한적인 런타임 확인 수단입니다.
- 여러 Protocol을 합쳐 더 큰 계약으로 만들 수 있습니다.

## 자주 헷갈리는 지점

| 실수 | 왜 문제인가 | 권장 방식 |
| --- | --- | --- |
| Protocol에 실제 구현을 넣음 | 인터페이스와 구현 경계가 흐려집니다 | 본문은 `...`로 두고 계약만 적습니다 |
| 다중 상속 Protocol에서 `Protocol` 베이스를 빼먹음 | 일반 클래스로 바뀔 수 있습니다 | 베이스 목록에 `Protocol`을 유지합니다 |
| `runtime_checkable`로 시그니처 검증까지 된다고 생각함 | 존재 여부만 봅니다 | 정밀 검증은 mypy/pyright에 맡깁니다 |
| 공통 구현이 필요한데 Protocol을 선택함 | 기본 메서드를 제공하기 어렵습니다 | 공통 구현이 필요하면 ABC를 씁니다 |
| Protocol을 너무 잘게 쪼갬 | 읽기와 유지보수가 어려워집니다 | 함께 움직이는 메서드는 하나로 묶습니다 |

## 실무에서는 이렇게 연결됩니다

- 플러그인 시스템은 `execute()`만 있으면 받는 Protocol을 둘 수 있습니다.
- 테스트에서는 mock 객체가 구조만 맞아도 Protocol 계약을 만족할 수 있습니다.
- 어댑터 패턴은 외부 클래스 수정 없이 내부 Protocol을 만족시키는 데 유리합니다.
- 저장소 계층은 서로 다른 백엔드가 같은 Protocol을 구현하도록 만들 수 있습니다.

## 실무 판단 기준

공개 인터페이스를 설계할 때는 ABC보다 Protocol이 더 유연한 경우가 많습니다. 구현 클래스가 인터페이스의 존재를 미리 알 필요가 없고, 외부 라이브러리 타입도 쉽게 수용할 수 있기 때문입니다. 특히 "우리가 소유하지 않은 클래스도 받아야 한다"는 조건이 있다면 Protocol이 거의 기본 선택입니다.

반대로 공통 기본 구현, 헬퍼 메서드, 서브클래스 강제가 중요하면 ABC가 낫습니다. 두 도구는 경쟁 관계라기보다 계약의 성격이 다른 도구라고 보는 편이 정확합니다.

## 체크리스트

- [ ] 외부 클래스도 만족해야 하는 인터페이스에 Protocol을 사용했습니다
- [ ] 공통 구현이 필요한 경우에만 ABC를 고려했습니다
- [ ] `isinstance()`가 꼭 필요할 때만 `@runtime_checkable`을 붙였습니다
- [ ] Protocol을 핵심 메서드 중심으로 유지했습니다
- [ ] mypy나 pyright로 호환성을 확인할 준비가 되어 있습니다

## 연습 문제

1. `to_json() -> str`와 `from_json(data: str)`를 가진 `Serializable` Protocol을 정의해 보세요.

2. `get(id: int)`, `save(entity)`, `delete(id: int)`를 가진 `Repository` Protocol을 만들고 서비스 함수를 연결해 보세요.

3. 같은 인터페이스를 ABC와 Protocol 두 방식으로 각각 구현해 차이를 비교해 보세요.

## 정리와 다음 글

`Protocol`은 Python 타입 시스템에서 structural typing을 구현하는 핵심 도구입니다. 상속이 아니라 메서드와 속성의 구조로 호환성을 판단하므로, Python의 덕 타이핑과 잘 맞습니다. 공통 구현이 필요할 때는 ABC, 느슨하고 확장 가능한 인터페이스 계약이 필요할 때는 Protocol을 쓰면 됩니다.

다음 글에서는 타입 관계를 입력과 출력 사이에 그대로 보존하는 Generic을 다루겠습니다.

<!-- toc:begin -->
- [Python type hint란 무엇인가?](./01-what-is-type-hint.md)
- [기본 타입과 collection 타입](./02-basic-and-collection-types.md)
- [Optional과 Union](./03-optional-and-union.md)
- [함수 타입 힌트](./04-function-type-hints.md)
- [TypedDict와 dataclass](./05-typeddict-and-dataclass.md)
- **Protocol과 structural typing (현재 글)**
- [Generic 이해하기](./07-generic.md)
- [mypy와 pyright 사용하기](./08-mypy-and-pyright.md)
- [Pydantic과 타입 힌트](./09-pydantic-and-type-hints.md)
- [타입 힌트를 잘 쓰는 기준](./10-type-hints-best-practices.md)
<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — typing.Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol)
- [PEP 544 — Protocols: Structural subtyping](https://peps.python.org/pep-0544/)
- [mypy 문서 — Protocols and structural subtyping](https://mypy.readthedocs.io/en/stable/protocols.html)
- [Real Python — Structural Typing](https://realpython.com/python-protocol/)

Tags: Python, Type Hints, Protocol, structural typing, 덕 타이핑, 인터페이스
