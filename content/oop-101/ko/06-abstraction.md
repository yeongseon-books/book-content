---
title: 추상화
series: oop-101
episode: 6
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
  - Python
  - OOP
  - 추상화
  - ABC
  - 인터페이스
last_reviewed: '2026-05-12'
seo_description: ABC와 abstractmethod로 공통 인터페이스를 강제하는 Python 추상화 설계를 설명합니다.
---

# 추상화

팀이 커질수록 같은 역할의 클래스가 조금씩 다른 모양으로 만들어지는 문제가 자주 생깁니다. 파일 저장소는 `read_file()`을 쓰고, 데이터베이스 저장소는 `fetch()`를 쓰고, API 클라이언트는 `load()`를 쓰기 시작하면 호출부는 구현체마다 달라집니다. 그때 필요한 것이 구현보다 먼저 합의된 인터페이스입니다.

추상화는 복잡한 내부를 숨기는 이야기로만 끝나지 않습니다. 실제 설계에서는 어떤 메서드를 반드시 구현해야 하는지, 어떤 공통 동작을 부모가 가져가야 하는지, 어디까지를 팀의 계약으로 강제할지를 정하는 문제에 가깝습니다.

이 글은 OOP 101 시리즈의 6번째 글입니다.

## 이 글에서 다룰 문제

> 추상화는 구현을 지우는 작업이 아니라, 여러 구현체가 공유해야 할 최소한의 계약을 선명하게 만드는 작업입니다.

- 추상 클래스와 `@abstractmethod`는 어떤 시점에 특히 가치가 커질까요?
- ABC와 Protocol은 비슷해 보여도 어떤 설계 철학 차이를 가질까요?
- 템플릿 메서드 패턴은 부모와 자식의 책임을 어떻게 나눌까요?
- 모든 인터페이스를 추상 클래스로 만들면 왜 오히려 설계가 무거워질 수 있을까요?

## 핵심 개념 잡기

> 추상 클래스 구조

```text
ABC (Abstract Base Class)
├── @abstractmethod read()     -> must implement
├── @abstractmethod write()    -> must implement
├── close()                    -> shared implementation (optional override)
│
├── FileStorage(ABC)
│   ├── read()  implemented
│   └── write() implemented
│
└── MemoryStorage(ABC)
    ├── read()  implemented
    └── write() implemented
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 추상 클래스(abstract class) | 인스턴스화할 수 없고 하위 클래스에 구현을 강제합니다 |
| `@abstractmethod` | 하위 클래스에서 반드시 오버라이딩해야 하는 메서드를 표시합니다 |
| ABC(Abstract Base Class) | Python `abc` 모듈이 제공하는 추상 클래스 베이스입니다 |
| 구체 클래스(concrete class) | 모든 추상 메서드를 구현하여 인스턴스화 가능한 클래스입니다 |
| 템플릿 메서드 패턴 | 알고리즘 골격을 정의하고 세부 단계를 하위 클래스에 위임합니다 |

## 전후 비교

데이터 소스 인터페이스를 비교합니다.

```python
# before: no interface enforcement — method name mismatch risk
class FileStorage:
    def read_file(self, path):
        pass

class DbStorage:
    def fetch_data(self, query):  # different method name
        pass
```

```python
# after: ABC enforces the interface
from abc import ABC, abstractmethod

class Storage(ABC):
    @abstractmethod
    def read(self, key: str) -> str: ...

    @abstractmethod
    def write(self, key: str, data: str) -> None: ...

class FileStorage(Storage):
    def read(self, key: str) -> str:
        return f"Reading {key} from file"

    def write(self, key: str, data: str) -> None:
        print(f"Writing {key} to file: {data}")
```

## 단계별 실습

### 1단계: 기본 추상 클래스

```python
from abc import ABC, abstractmethod


class Animal(ABC):
    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def speak(self) -> str:
        """Return the animal's sound"""
        ...

    def describe(self) -> str:
        """Shared implementation — optional override"""
        return f"{self.name}: {self.speak()}"


class Dog(Animal):
    def speak(self) -> str:
        return "woof"

class Cat(Animal):
    def speak(self) -> str:
        return "meow"

dog = Dog("Buddy")
print(dog.describe())  # Buddy: woof

# animal = Animal("animal")  # TypeError: Can't instantiate abstract class
```

### 2단계: 추상 프로퍼티

```python
from abc import ABC, abstractmethod


class Vehicle(ABC):
    @property
    @abstractmethod
    def fuel_type(self) -> str: ...

    @property
    @abstractmethod
    def max_speed(self) -> int: ...

    def specs(self) -> str:
        return f"Fuel: {self.fuel_type}, Max speed: {self.max_speed}km/h"


class ElectricCar(Vehicle):
    @property
    def fuel_type(self) -> str:
        return "electric"

    @property
    def max_speed(self) -> int:
        return 250


class GasCar(Vehicle):
    @property
    def fuel_type(self) -> str:
        return "gasoline"

    @property
    def max_speed(self) -> int:
        return 220


ev = ElectricCar()
gas = GasCar()
print(ev.specs())   # Fuel: electric, Max speed: 250km/h
print(gas.specs())  # Fuel: gasoline, Max speed: 220km/h
```

### 3단계: 템플릿 메서드 패턴

```python
from abc import ABC, abstractmethod


class DataPipeline(ABC):
    """Data processing pipeline — skeleton fixed, steps delegated to subclasses"""

    def run(self) -> list[str]:
        raw = self.extract()
        cleaned = self.transform(raw)
        self.load(cleaned)
        return cleaned

    @abstractmethod
    def extract(self) -> list[str]: ...

    @abstractmethod
    def transform(self, data: list[str]) -> list[str]: ...

    @abstractmethod
    def load(self, data: list[str]) -> None: ...


class CsvPipeline(DataPipeline):
    def extract(self) -> list[str]:
        return ["  Alice,30  ", "  Bob,25  ", "  Charlie,35  "]

    def transform(self, data: list[str]) -> list[str]:
        return [row.strip() for row in data]

    def load(self, data: list[str]) -> None:
        for row in data:
            print(f"Saving: {row}")


pipeline = CsvPipeline()
result = pipeline.run()
# Saving: Alice,30
# Saving: Bob,25
# Saving: Charlie,35
print(result)  # ['Alice,30', 'Bob,25', 'Charlie,35']
```

### 4단계: ABC의 register()

```python
from abc import ABC, abstractmethod


class Drawable(ABC):
    @abstractmethod
    def draw(self) -> str: ...


class ThirdPartyWidget:
    """External library class — cannot modify"""
    def draw(self) -> str:
        return "Widget rendered"


Drawable.register(ThirdPartyWidget)

widget = ThirdPartyWidget()
print(isinstance(widget, Drawable))  # True
print(widget.draw())                 # Widget rendered
```

### 5단계: ABC vs Protocol 선택

```python
from abc import ABC, abstractmethod
from typing import Protocol


# ABC: explicit inheritance required — good for frameworks, team contracts
class Serializer(ABC):
    @abstractmethod
    def serialize(self, data: dict) -> str: ...

class JsonSerializer(Serializer):
    def serialize(self, data: dict) -> str:
        import json
        return json.dumps(data)


# Protocol: no inheritance needed — good for cross-library compatibility
class SerializerProto(Protocol):
    def serialize(self, data: dict) -> str: ...

class YamlSerializer:  # does not inherit Protocol
    def serialize(self, data: dict) -> str:
        return "\n".join(f"{k}: {v}" for k, v in data.items())


def save(serializer: SerializerProto, data: dict) -> None:
    print(serializer.serialize(data))

save(JsonSerializer(), {"name": "Kim"})  # {"name": "Kim"}
save(YamlSerializer(), {"name": "Kim"})  # name: Kim
```

## 이 코드에서 주목할 점

- ABC의 추상 메서드를 구현하지 않으면 인스턴스 생성 시 `TypeError`가 발생합니다
- 템플릿 메서드 패턴은 알고리즘 골격을 부모에, 세부 단계를 자식에 위임합니다
- `register()`로 기존 클래스를 수정하지 않고 ABC에 등록할 수 있습니다
- ABC는 명시적 계약, Protocol은 구조적 호환 — 상황에 따라 선택합니다

## 자주 하는 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 추상 메서드를 하나라도 미구현 | 인스턴스 생성 시 TypeError입니다 | IDE가 미구현 메서드를 표시합니다 |
| ABC에 구현 코드를 과도하게 넣음 | 상속 결합도가 높아집니다 | 공통 유틸리티만 넣습니다 |
| 모든 인터페이스를 ABC로 정의 | 불필요한 상속 강제입니다 | 외부 호환이 필요하면 Protocol이 적합합니다 |
| `@abstractmethod` 없이 ABC 사용 | 인스턴스화가 가능해져 의미가 없습니다 | 최소 하나의 추상 메서드를 정의합니다 |
| 추상 클래스를 데이터 저장에 사용 | 추상 클래스는 인터페이스 정의용입니다 | 데이터는 dataclass나 일반 클래스를 사용합니다 |

## 실무에서 이렇게 쓰입니다

- Python의 `collections.abc`(Iterable, Sequence, Mapping)가 ABC입니다
- Django의 `View` 클래스는 템플릿 메서드 패턴을 활용합니다
- 플러그인 아키텍처에서 ABC로 플러그인 인터페이스를 정의합니다
- 테스트에서 ABC를 상속한 mock 클래스를 만들어 구현 여부를 보장합니다
- 데이터 처리 파이프라인에서 Extract/Transform/Load 단계를 ABC로 추상화합니다

## 현업 개발자는 이렇게 생각합니다

추상 클래스는 팀 규모가 커질수록 가치가 증가합니다. 소규모 프로젝트에서는 덕 타이핑으로 충분하지만, 여러 명이 각자 구현체를 만들 때 ABC가 "이것은 반드시 구현하세요"라는 명확한 계약을 제공합니다.

Python 생태계에서는 ABC와 Protocol을 상황에 따라 혼용합니다. 내부 팀 코드는 ABC, 외부 라이브러리와의 호환은 Protocol이 일반적입니다.

## 체크리스트

- [ ] ABC와 `@abstractmethod`로 추상 클래스를 정의할 수 있다
- [ ] 추상 프로퍼티를 정의할 수 있다
- [ ] 템플릿 메서드 패턴을 구현할 수 있다
- [ ] ABC와 Protocol의 차이를 설명할 수 있다
- [ ] `register()`로 기존 클래스를 ABC에 등록할 수 있다

## 정리 및 다음 글 안내

추상화는 복잡성을 관리하고 일관된 인터페이스를 강제하는 핵심 원칙입니다. ABC와 Protocol을 상황에 맞게 활용하면 확장 가능하고 안전한 설계가 가능합니다. 다음 글에서는 합성과 상속의 차이를 비교하고 각각의 적절한 사용 시점을 알아봅니다.

<!-- toc:begin -->
- [객체지향이란 무엇인가?](./01-what-is-oop.md)
- [클래스와 인스턴스](./02-classes-and-instances.md)
- [캡슐화](./03-encapsulation.md)
- [상속](./04-inheritance.md)
- [다형성](./05-polymorphism.md)
- **추상화 (현재 글)**
- 합성과 상속 (예정)
- SOLID 원칙 기초 (예정)
- 객체지향 설계 예제 (예정)
- 객체지향을 언제 피해야 할까? (예정)
<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — abc 모듈](https://docs.python.org/3/library/abc.html)
- [Real Python — Abstract Base Classes](https://realpython.com/python-interface/)
- [Python collections.abc 문서](https://docs.python.org/3/library/collections.abc.html)
- [Fluent Python — Chapter 13: Interfaces, Protocols, and ABCs](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)

Tags: Python, OOP, 추상화, ABC, 인터페이스
