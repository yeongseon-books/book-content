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
last_reviewed: '2026-05-04'
---

# Protocol과 structural typing

> Type Hints in Python 101 시리즈 (6/10)


## 이 글에서 다룰 문제

ABC는 상속을 강제하므로 외부 라이브러리 클래스에 적용할 수 없습니다. Protocol은 상속 없이 "이 메서드가 있으면 충분하다"는 조건을 정의하여, Python의 덕 타이핑 철학과 정적 분석을 모두 지원합니다.

> Protocol = 정적 타입의 덕 타이핑

Go의 인터페이스, TypeScript의 구조적 타입과 같은 개념입니다.

## 핵심 개념 잡기

> nominal typing vs structural typing

```
Nominal (ABC)                  Structural (Protocol)
─────────────────             ─────────────────
class Dog(Animal):            class Dog:
    ...                           def speak(self): ...
상속 관계로 판단                메서드 존재로 판단
명시적 선언 필요                암묵적 호환
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| Protocol | 필요한 메서드/속성을 정의하는 구조적 인터페이스입니다 |
| structural typing | 타입 호환성을 구조(메서드/속성)로 판단하는 체계입니다 |
| nominal typing | 타입 호환성을 명시적 상속으로 판단하는 체계입니다 |
| @runtime_checkable | isinstance()로 Protocol 준수를 런타임에 확인합니다 |
| ABC | 상속 기반의 추상 클래스입니다 |

## Before / After

ABC 상속을 Protocol로 전환합니다.

```python
# before: ABC — 상속 강제
from abc import ABC, abstractmethod

class Serializable(ABC):
    @abstractmethod
    def to_json(self) -> str: ...

class User(Serializable):  # 상속 필수
    def to_json(self) -> str:
        return '{"name": "Alice"}'
```

```python
# after: Protocol — 상속 불필요
from typing import Protocol

class Serializable(Protocol):
    def to_json(self) -> str: ...

class User:  # 상속 없이 호환
    def to_json(self) -> str:
        return '{"name": "Alice"}'

def save(obj: Serializable) -> None:
    print(obj.to_json())

save(User())  # OK — User는 to_json()이 있으므로 Serializable
```

## 단계별 실습

### Step 1: Protocol 기본

```python
from typing import Protocol


class HasLength(Protocol):
    def __len__(self) -> int: ...


def print_length(obj: HasLength) -> None:
    print(f"길이: {len(obj)}")


# 상속 없이 __len__만 있으면 호환
print_length([1, 2, 3])          # 길이: 3
print_length("hello")            # 길이: 5
print_length({"a": 1, "b": 2})   # 길이: 2


# 사용자 정의 클래스도 상속 없이 호환
class Inventory:
    def __init__(self, items: list[str]) -> None:
        self._items = items

    def __len__(self) -> int:
        return len(self._items)

print_length(Inventory(["사과", "바나나", "체리"]))  # 길이: 3
```

### Step 2: 메서드 시그니처 Protocol

```python
from typing import Protocol


class Drawable(Protocol):
    def draw(self, x: int, y: int) -> None: ...


class Circle:
    def __init__(self, radius: int) -> None:
        self.radius = radius

    def draw(self, x: int, y: int) -> None:
        print(f"원({self.radius}) at ({x}, {y})")

class Rectangle:
    def __init__(self, w: int, h: int) -> None:
        self.w = w
        self.h = h

    def draw(self, x: int, y: int) -> None:
        print(f"사각형({self.w}x{self.h}) at ({x}, {y})")


def render(shapes: list[Drawable]) -> None:
    for shape in shapes:
        shape.draw(0, 0)


shapes: list[Drawable] = [Circle(5), Rectangle(10, 20)]
render(shapes)
# 원(5) at (0, 0)
# 사각형(10x20) at (0, 0)
```

### Step 3: 속성 Protocol

```python
from typing import Protocol


class Named(Protocol):
    @property
    def name(self) -> str: ...

class Aged(Protocol):
    @property
    def age(self) -> int: ...

class Person(Named, Aged, Protocol):
    """Named + Aged를 결합한 Protocol."""
    ...


class Employee:
    def __init__(self, name: str, age: int, dept: str) -> None:
        self._name = name
        self._age = age
        self.dept = dept

    @property
    def name(self) -> str:
        return self._name

    @property
    def age(self) -> int:
        return self._age


def introduce(person: Person) -> str:
    return f"{person.name} ({person.age}세)"


emp = Employee("Alice", 30, "Engineering")
print(introduce(emp))  # Alice (30세)
```

### Step 4: @runtime_checkable

```python
from typing import Protocol, runtime_checkable


@runtime_checkable
class Closable(Protocol):
    def close(self) -> None: ...


class DatabaseConnection:
    def close(self) -> None:
        print("DB 연결 종료")

class FileHandle:
    def close(self) -> None:
        print("파일 닫기")

class Logger:
    def log(self, msg: str) -> None:
        print(msg)


# runtime_checkable로 isinstance 사용 가능
db = DatabaseConnection()
fh = FileHandle()
logger = Logger()

print(isinstance(db, Closable))      # True
print(isinstance(fh, Closable))      # True
print(isinstance(logger, Closable))  # False


def cleanup(resources: list[Closable]) -> None:
    for r in resources:
        r.close()

cleanup([db, fh])
# DB 연결 종료
# 파일 닫기
```

### Step 5: Protocol vs ABC 비교

```python
from abc import ABC, abstractmethod
from typing import Protocol


# ABC: 상속 강제 — 외부 클래스에 적용 불가
class SerializableABC(ABC):
    @abstractmethod
    def to_dict(self) -> dict: ...

# Protocol: 상속 불필요 — 어떤 클래스든 호환
class SerializableProto(Protocol):
    def to_dict(self) -> dict: ...


# 외부 라이브러리의 클래스 (수정 불가)
class ExternalUser:
    def __init__(self, name: str) -> None:
        self.name = name
    def to_dict(self) -> dict:
        return {"name": self.name}


# ABC: ExternalUser는 SerializableABC를 상속하지 않으므로 타입 불일치
# Protocol: ExternalUser는 to_dict()가 있으므로 호환

def save_proto(obj: SerializableProto) -> None:
    data = obj.to_dict()
    print(f"저장: {data}")

save_proto(ExternalUser("Alice"))  # OK — Protocol은 구조만 확인
# 저장: {'name': 'Alice'}


# 결론:
# - 내부 코드 계층 → ABC (명시적 계약)
# - 외부 호환 + 덕 타이핑 → Protocol
```

## 이 코드에서 주목할 점

- Protocol은 상속 없이 메서드/속성의 존재로 타입 호환성을 판단합니다
- `@runtime_checkable`을 추가하면 isinstance()로 런타임 검증이 가능합니다
- Protocol은 결합(composition)이 자유로워 작은 인터페이스를 조합할 수 있습니다
- 외부 라이브러리 클래스에 타입을 부여할 때 Protocol이 유일한 선택입니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| Protocol을 직접 인스턴스화 | Protocol은 타입 정의용입니다 | 구현 클래스를 따로 만듭니다 |
| @runtime_checkable 없이 isinstance | TypeError가 발생합니다 | 데코레이터를 추가합니다 |
| Protocol에 구현 로직 포함 | Protocol은 인터페이스 정의입니다 | 메서드 본문은 `...`만 씁니다 |
| 너무 큰 Protocol | 인터페이스 분리 원칙 위반입니다 | 작은 Protocol로 분리합니다 |
| ABC와 Protocol 혼용 | 두 체계가 충돌합니다 | 프로젝트 내에서 하나를 선택합니다 |

## 실무에서 이렇게 쓰입니다

- 저장소 패턴(Repository)을 Protocol로 정의하여 구현체를 교체합니다
- 플러그인 시스템의 인터페이스를 Protocol로 정의합니다
- 테스트에서 목(mock) 객체가 Protocol을 충족하는지 검증합니다
- 외부 SDK 클래스에 타입 안전한 래퍼를 적용합니다
- 의존성 주입에서 인터페이스를 Protocol로 정의합니다

## 현업 개발자는 이렇게 생각합니다

Protocol은 Python의 "덕 타이핑" 철학과 정적 타입 분석을 양립시키는 핵심 도구입니다. Go의 인터페이스처럼 "이것만 할 수 있으면 된다"를 코드로 표현합니다. ABC보다 유연하고, 외부 클래스에도 적용 가능합니다.

인터페이스 분리 원칙(ISP)을 Protocol로 구현하면, 작은 Protocol을 여러 개 정의하고 필요에 따라 조합하는 유연한 설계가 가능합니다.

## 체크리스트

- [ ] Protocol의 정의와 structural typing의 원리를 설명할 수 있다
- [ ] Protocol로 인터페이스를 정의할 수 있다
- [ ] @runtime_checkable의 용도를 이해한다
- [ ] Protocol과 ABC의 차이를 설명할 수 있다
- [ ] 작은 Protocol을 결합하여 복합 인터페이스를 만들 수 있다

## 정리 및 다음 글 안내

Protocol은 상속 없이 구조적 호환성을 검증하는 도구입니다. Python의 덕 타이핑을 정적 분석으로 확장하여 유연하고 안전한 코드를 작성할 수 있습니다. 다음 글에서는 타입 매개변수를 활용하는 **Generic 이해하기**를 다룹니다.

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

- [PEP 544 — Protocols: Structural subtyping](https://peps.python.org/pep-0544/)
- [Python 공식 문서 — typing.Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol)
- [mypy 공식 문서 — Protocols and structural subtyping](https://mypy.readthedocs.io/en/stable/protocols.html)
- [Real Python — Duck Typing and Protocols](https://realpython.com/python-protocol/)
