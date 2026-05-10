---
series: oop-101
episode: 6
title: 추상화
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
  - OOP
  - 추상화
  - ABC
  - 인터페이스
seo_description: Python ABC를 활용한 추상 클래스 설계와 인터페이스 정의 방법을 다룹니다.
last_reviewed: '2026-05-04'
---

# 추상화

> Object-Oriented Programming 101 시리즈 (6/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 공통 인터페이스를 정의하되, 직접 인스턴스화할 수 없는 클래스를 어떻게 만들까요?

> 추상화는 복잡한 시스템에서 핵심적인 인터페이스만 노출하고 세부 구현을 숨기는 원칙입니다. Python의 `abc` 모듈을 사용하면 추상 클래스와 추상 메서드를 정의하여 하위 클래스에 구현을 강제할 수 있습니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 추상화의 목적과 추상 클래스의 역할
- Python `abc.ABC`와 `@abstractmethod` 사용법
- 추상 프로퍼티와 추상 클래스 메서드
- 추상 클래스 vs Protocol의 선택 기준

## 왜 중요한가

여러 개발자가 각자 다른 데이터 소스(파일, DB, API)에 대한 클래스를 만들 때, 공통 인터페이스를 정의하지 않으면 메서드 이름과 시그니처가 제각각이 됩니다. 추상 클래스는 "이 메서드는 반드시 구현하세요"라는 계약을 컴파일(인스턴스 생성) 시점에 강제합니다.

> 추상 클래스 = 인스턴스화 불가 + 하위 클래스에 메서드 구현 강제

Protocol은 "구조적으로 일치하면 OK"인 반면, ABC는 "명시적으로 상속해야 OK"입니다. 팀 규모가 크거나 프레임워크를 만들 때는 ABC의 명시성이 실수를 줄여줍니다.

## 핵심 개념 잡기

> 추상 클래스 구조

```
ABC (Abstract Base Class)
├── @abstractmethod read()     → 반드시 구현
├── @abstractmethod write()    → 반드시 구현
├── close()                    → 공통 구현 (선택적 오버라이딩)
│
├── FileStorage(ABC)
│   ├── read()  ✅ 구현
│   └── write() ✅ 구현
│
└── MemoryStorage(ABC)
    ├── read()  ✅ 구현
    └── write() ✅ 구현
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 추상 클래스(abstract class) | 인스턴스화할 수 없고 하위 클래스에 구현을 강제합니다 |
| `@abstractmethod` | 하위 클래스에서 반드시 오버라이딩해야 하는 메서드를 표시합니다 |
| ABC(Abstract Base Class) | Python `abc` 모듈이 제공하는 추상 클래스 베이스입니다 |
| 구체 클래스(concrete class) | 모든 추상 메서드를 구현하여 인스턴스화 가능한 클래스입니다 |
| 템플릿 메서드 패턴 | 알고리즘 골격을 정의하고 세부 단계를 하위 클래스에 위임합니다 |

## Before / After

데이터 소스 인터페이스를 비교합니다.

```python
# before: 인터페이스 강제 없음 — 메서드 이름 불일치 위험
class FileStorage:
    def read_file(self, path):
        pass

class DbStorage:
    def fetch_data(self, query):  # 메서드 이름이 다름
        pass
```

```python
# after: ABC로 인터페이스 강제
from abc import ABC, abstractmethod

class Storage(ABC):
    @abstractmethod
    def read(self, key: str) -> str: ...

    @abstractmethod
    def write(self, key: str, data: str) -> None: ...

class FileStorage(Storage):
    def read(self, key: str) -> str:
        return f"파일에서 {key} 읽기"

    def write(self, key: str, data: str) -> None:
        print(f"파일에 {key} 저장: {data}")
```

## 단계별 실습

### Step 1: 기본 추상 클래스

```python
from abc import ABC, abstractmethod


class Animal(ABC):
    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def speak(self) -> str:
        """동물의 울음소리를 반환합니다"""
        ...

    def describe(self) -> str:
        """공통 구현 — 오버라이딩 선택"""
        return f"{self.name}: {self.speak()}"


class Dog(Animal):
    def speak(self) -> str:
        return "멍멍"

class Cat(Animal):
    def speak(self) -> str:
        return "야옹"

dog = Dog("바둑이")
print(dog.describe())  # 바둑이: 멍멍

# animal = Animal("동물")  # TypeError: Can't instantiate abstract class
```

### Step 2: 추상 프로퍼티

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
        return f"연료: {self.fuel_type}, 최대 속도: {self.max_speed}km/h"


class ElectricCar(Vehicle):
    @property
    def fuel_type(self) -> str:
        return "전기"

    @property
    def max_speed(self) -> int:
        return 250


class GasCar(Vehicle):
    @property
    def fuel_type(self) -> str:
        return "가솔린"

    @property
    def max_speed(self) -> int:
        return 220


ev = ElectricCar()
gas = GasCar()
print(ev.specs())   # 연료: 전기, 최대 속도: 250km/h
print(gas.specs())  # 연료: 가솔린, 최대 속도: 220km/h
```

### Step 3: 템플릿 메서드 패턴

```python
from abc import ABC, abstractmethod


class DataPipeline(ABC):
    """데이터 처리 파이프라인 — 골격은 고정, 단계는 하위 클래스가 구현"""

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
            print(f"저장: {row}")


pipeline = CsvPipeline()
result = pipeline.run()
# 저장: Alice,30
# 저장: Bob,25
# 저장: Charlie,35
print(result)  # ['Alice,30', 'Bob,25', 'Charlie,35']
```

### Step 4: ABC의 register()

```python
from abc import ABC, abstractmethod


class Drawable(ABC):
    @abstractmethod
    def draw(self) -> str: ...


class ThirdPartyWidget:
    """외부 라이브러리 클래스 — 수정 불가"""
    def draw(self) -> str:
        return "위젯 렌더링"


Drawable.register(ThirdPartyWidget)

widget = ThirdPartyWidget()
print(isinstance(widget, Drawable))  # True
print(widget.draw())                 # 위젯 렌더링
```

### Step 5: ABC vs Protocol 선택

```python
from abc import ABC, abstractmethod
from typing import Protocol


# ABC: 명시적 상속 필요 — 프레임워크, 팀 규약에 적합
class Serializer(ABC):
    @abstractmethod
    def serialize(self, data: dict) -> str: ...

class JsonSerializer(Serializer):
    def serialize(self, data: dict) -> str:
        import json
        return json.dumps(data)


# Protocol: 상속 불필요 — 라이브러리 간 호환에 적합
class SerializerProto(Protocol):
    def serialize(self, data: dict) -> str: ...

class YamlSerializer:  # Protocol을 상속하지 않음
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

## 흔한 실수 5가지

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

## 시니어 엔지니어는 이렇게 생각합니다

- **ABC 사용** — 강한 계약이 필요할 때만 ABC를 사용합니다.
- **인터페이스 단순** — 메서드 수가 적을수록 좋습니다.
- **의도 드러내기** — 추상화는 도메인 어휘를 코드로 노출하는 일입니다.
- **과추상 경계** — 재사용 가능성 가설이 약하면 추상화를 미룹니다.
- **문서화** — 추상화의 의미는 코드 외부에 명시합니다.

## 체크리스트

- [ ] ABC와 `@abstractmethod`로 추상 클래스를 정의할 수 있다
- [ ] 추상 프로퍼티를 정의할 수 있다
- [ ] 템플릿 메서드 패턴을 구현할 수 있다
- [ ] ABC와 Protocol의 차이를 설명할 수 있다
- [ ] `register()`로 기존 클래스를 ABC에 등록할 수 있다

## 연습 문제

1. `NotificationSender` ABC를 정의하고 `EmailSender`, `SmsSender`, `SlackSender`를 구현하세요.
2. `ReportGenerator` ABC에 템플릿 메서드 패턴을 적용하여 `HtmlReport`와 `PdfReport`를 만드세요.
3. `collections.abc.Sequence`를 상속하여 커스텀 시퀀스 클래스를 구현하세요.

## 정리 및 다음 글 안내

추상화는 복잡성을 관리하고 일관된 인터페이스를 강제하는 핵심 원칙입니다. ABC와 Protocol을 상황에 맞게 활용하면 확장 가능하고 안전한 설계가 가능합니다. 다음 글에서는 합성과 상속의 차이를 비교하고 각각의 적절한 사용 시점을 알아봅니다.

<!-- toc:begin -->
- [객체지향이란 무엇인가?](./01-what-is-oop.md)
- [클래스와 인스턴스](./02-classes-and-instances.md)
- [캡슐화](./03-encapsulation.md)
- [상속](./04-inheritance.md)
- [다형성](./05-polymorphism.md)
- **추상화 (현재 글)**
- [합성과 상속](./07-composition-vs-inheritance.md)
- [SOLID 원칙 기초](./08-solid-principles.md)
- [객체지향 설계 예제](./09-oop-design-example.md)
- [객체지향을 언제 피해야 할까?](./10-when-to-avoid-oop.md)
<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — abc 모듈](https://docs.python.org/3/library/abc.html)
- [Real Python — Abstract Base Classes](https://realpython.com/python-interface/)
- [Python collections.abc 문서](https://docs.python.org/3/library/collections.abc.html)
- [Fluent Python — Chapter 13: Interfaces, Protocols, and ABCs](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)

Tags: Python, OOP, 추상화, ABC, 인터페이스
