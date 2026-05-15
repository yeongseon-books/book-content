---
title: 객체지향을 언제 피해야 할까?
series: oop-101
episode: 10
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
  - 함수형 프로그래밍
  - dataclass
  - 설계 판단
last_reviewed: '2026-05-12'
seo_description: 객체지향이 과한 상황과 함수, dataclass, 함수형 접근이 더 나은 경우를 설명합니다.
---

# 객체지향을 언제 피해야 할까?

객체지향을 배우고 나면 한동안 모든 문제를 클래스로 풀고 싶어집니다. 하지만 Python에서는 그 습관이 오히려 코드를 무겁게 만드는 경우가 많습니다. 상태 없는 유틸리티 함수, 단순 데이터 컨테이너, 일회성 스크립트까지 전부 클래스 계층으로 감싸면 읽기도 테스트도 번거로워집니다.

좋은 설계자는 객체지향을 잘 쓰는 사람인 동시에, 객체지향을 쓰지 않아야 할 순간도 잘 구분하는 사람입니다. Python이 다중 패러다임 언어라는 점을 받아들이면, 함수와 모듈, `dataclass`, `NamedTuple`, 고차 함수가 더 자연스러운 해법인 장면이 분명히 보이기 시작합니다.

이 글은 OOP 101 시리즈의 마지막 글입니다.

## 이 글에서 다룰 문제

> 설계의 성숙도는 클래스를 많이 만드는 데서 드러나지 않습니다. 클래스가 필요 없는 문제를 함수와 데이터 구조로 단순하게 끝낼 수 있는지에서 더 잘 드러납니다.

- 어떤 신호가 보이면 객체지향이 과한 설계라고 판단할 수 있을까요?
- 상태 없는 로직은 왜 클래스보다 함수가 더 읽기 쉬운 경우가 많을까요?
- `dataclass`, `NamedTuple`, `TypedDict`는 어떤 종류의 클래스를 대체할 수 있을까요?
- 하나의 코드베이스 안에서 객체지향과 함수형 스타일을 어떻게 균형 있게 섞을 수 있을까요?

## 핵심 개념 잡기

> OOP vs 대안 — 선택 기준

```text
When classes make sense            When classes are overkill
─────────────────────              ─────────────────────
State + behavior together          Stateless transformation functions
Multiple instances needed          Single-run scripts
Swappable strategies required      Data-only containers
Framework demands classes          Pipeline data processing
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 다중 패러다임(multi-paradigm) | 절차, 객체지향, 함수형을 혼용할 수 있는 언어입니다 |
| 빈혈 도메인 모델(anemic) | 데이터만 있고 행위가 없는 클래스입니다 |
| dataclass | 데이터 중심 클래스를 간결하게 정의하는 Python 기능입니다 |
| 고차 함수(higher-order function) | 함수를 인자로 받거나 반환하는 함수입니다 |
| 클로저(closure) | 외부 변수를 기억하는 내부 함수입니다 |

## 전후 비교

불필요한 클래스를 제거합니다.

```python
# before: unnecessary class with a single method
class Validator:
    def validate_email(self, email: str) -> bool:
        return "@" in email and "." in email

validator = Validator()
print(validator.validate_email("test@example.com"))
```

```python
# after: a plain function is enough
def validate_email(email: str) -> bool:
    return "@" in email and "." in email

print(validate_email("test@example.com"))
```

## 단계별 실습

### 1단계: 클래스 대신 함수

```python
# Unnecessary class — stateless, methods only
class StringUtils:
    @staticmethod
    def capitalize_words(text: str) -> str:
        return " ".join(w.capitalize() for w in text.split())

    @staticmethod
    def count_words(text: str) -> int:
        return len(text.split())

    @staticmethod
    def truncate(text: str, max_len: int) -> str:
        if len(text) <= max_len:
            return text
        return text[:max_len - 3] + "..."


# Better: module-level functions
def capitalize_words(text: str) -> str:
    return " ".join(w.capitalize() for w in text.split())

def count_words(text: str) -> int:
    return len(text.split())

def truncate(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


print(capitalize_words("hello world"))  # Hello World
print(count_words("one two three"))     # 3
print(truncate("abcdefghij", 8))        # abcde...
```

### 2단계: 클래스 대신 dataclass / NamedTuple

```python
from dataclasses import dataclass
from typing import NamedTuple


# Unnecessary boilerplate — manual __init__, __repr__, __eq__
class ManualPoint:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ManualPoint):
            return NotImplemented
        return self.x == other.x and self.y == other.y


# Better 1: dataclass
@dataclass
class Point:
    x: float
    y: float

# Better 2: NamedTuple (immutable)
class ImmutablePoint(NamedTuple):
    x: float
    y: float


p1 = Point(1, 2)
p2 = Point(1, 2)
print(p1)        # Point(x=1, y=2)
print(p1 == p2)  # True

ip = ImmutablePoint(3, 4)
print(ip.x)  # 3
# ip.x = 10  # AttributeError — immutable
```

### 3단계: 클래스 대신 고차 함수

```python
# Strategy pattern — class version
from typing import Protocol

class Formatter(Protocol):
    def format(self, value: float) -> str: ...

class CurrencyFormatter:
    def format(self, value: float) -> str:
        return f"${value:,.2f}"

class PercentFormatter:
    def format(self, value: float) -> str:
        return f"{value:.1f}%"


# Better: functions are enough — no classes needed
from typing import Callable

def currency_format(value: float) -> str:
    return f"${value:,.2f}"

def percent_format(value: float) -> str:
    return f"{value:.1f}%"

def display_values(
    values: list[float],
    formatter: Callable[[float], str],
) -> None:
    for v in values:
        print(formatter(v))


display_values([1000, 2500, 50000], currency_format)
# $1,000.00
# $2,500.00
# $50,000.00

display_values([0.95, 0.87, 0.12], percent_format)
# 0.9%
# 0.9%
# 0.1%
```

### 4단계: 클래스 대신 딕셔너리 / 튜플

```python
# Unnecessary class — just holding data
class Config:
    def __init__(self, host: str, port: int, debug: bool) -> None:
        self.host = host
        self.port = port
        self.debug = debug


# Better 1: TypedDict (structured dictionary)
from typing import TypedDict

class Config(TypedDict):
    host: str
    port: int
    debug: bool

config: Config = {"host": "localhost", "port": 8080, "debug": True}
print(config["host"])  # localhost


# Better 2: a plain dict is enough for simple config
config = {"host": "localhost", "port": 8080, "debug": True}
```

### 5단계: 함수형 파이프라인

```python
from functools import reduce


# Data transformation — function chaining without classes
def load_data() -> list[dict]:
    return [
        {"name": "  Alice  ", "score": 85},
        {"name": "  Bob  ", "score": 92},
        {"name": "  Charlie  ", "score": 78},
        {"name": "  Diana  ", "score": 95},
    ]

def clean_names(data: list[dict]) -> list[dict]:
    return [{**d, "name": d["name"].strip()} for d in data]

def filter_passing(data: list[dict], threshold: int = 80) -> list[dict]:
    return [d for d in data if d["score"] >= threshold]

def sort_by_score(data: list[dict]) -> list[dict]:
    return sorted(data, key=lambda d: d["score"], reverse=True)

def format_results(data: list[dict]) -> list[str]:
    return [f"{d['name']}: {d['score']} points" for d in data]


# Run the pipeline
result = format_results(sort_by_score(filter_passing(clean_names(load_data()))))
for line in result:
    print(line)
# Diana: 95 points
# Bob: 92 points
# Alice: 85 points
```

## 이 코드에서 주목할 점

- 상태 없는 유틸리티 함수는 모듈 수준 함수가 더 간결합니다
- `dataclass`와 `NamedTuple`은 데이터 중심 클래스의 boilerplate를 제거합니다
- 단순 전략 패턴은 `Callable`로 대체 가능합니다
- 데이터 변환 파이프라인은 함수 체이닝이 자연스럽습니다

## 자주 하는 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 모든 것을 클래스로 만듦 | 불필요한 복잡성입니다 | 함수로 충분한지 먼저 검토합니다 |
| 메서드 하나뿐인 클래스 | 함수가 더 명확합니다 | 함수로 변환합니다 |
| 상태 없는 static 메서드만 있는 클래스 | 네임스페이스 남용입니다 | 모듈 수준 함수로 변환합니다 |
| dataclass가 적합한데 일반 클래스 사용 | boilerplate가 많아집니다 | `@dataclass` 데코레이터를 사용합니다 |
| 함수형이 적합한데 OOP 강제 | 코드가 장황해집니다 | Python은 다중 패러다임을 활용합니다 |

## 실무에서 이렇게 쓰입니다

- CLI 스크립트는 보통 함수만으로 작성합니다
- 데이터 분석 파이프라인(pandas)은 함수 체이닝을 사용합니다
- API 응답 모델은 `dataclass`나 Pydantic `BaseModel`을 사용합니다
- 설정 관리는 `TypedDict`나 환경 변수 딕셔너리로 처리합니다
- 테스트 유틸리티는 모듈 수준 함수로 작성합니다

## 현업 개발자는 이렇게 생각합니다

Python의 강점은 다중 패러다임입니다. 함수, 클래스, 모듈을 상황에 맞게 조합하는 것이 Pythonic한 코드입니다. "이것을 클래스로 만들어야 할까?"에 대한 답은 "상태와 행위가 함께 변경되는가?"입니다.

실무에서는 처음에 함수로 시작하고, 상태 관리가 필요해지면 클래스로 전환하는 접근이 가장 실용적입니다. 불필요한 클래스를 만들지 않는 것도 좋은 설계 능력입니다.

## 체크리스트

- [ ] 클래스가 불필요한 상황을 식별할 수 있다
- [ ] 함수 기반 접근이 적합한 패턴을 알고 있다
- [ ] `dataclass`와 `NamedTuple`을 적절히 사용할 수 있다
- [ ] 고차 함수로 간단한 전략 패턴을 대체할 수 있다
- [ ] OOP와 함수형 스타일을 혼용하여 코드를 작성할 수 있다

## 정리 및 다음 글 안내

객체지향은 강력한 도구이지만, 모든 문제에 적합하지는 않습니다. Python의 다중 패러다임을 활용하여 상황에 맞는 도구를 선택하는 것이 좋은 코드의 핵심입니다. 이 시리즈에서 다룬 캡슐화, 상속, 다형성, 추상화, 합성, SOLID가 여러분의 설계 도구상자가 되길 바랍니다.

<!-- toc:begin -->
- [객체지향이란 무엇인가?](./01-what-is-oop.md)
- [클래스와 인스턴스](./02-classes-and-instances.md)
- [캡슐화](./03-encapsulation.md)
- [상속](./04-inheritance.md)
- [다형성](./05-polymorphism.md)
- [추상화](./06-abstraction.md)
- [합성과 상속](./07-composition-vs-inheritance.md)
- [SOLID 원칙 기초](./08-solid-principles.md)
- [객체지향 설계 예제](./09-oop-design-example.md)
- **객체지향을 언제 피해야 할까? (현재 글)**
<!-- toc:end -->

## 참고 자료

- [Stop Writing Classes — PyCon Talk by Jack Diederich](https://www.youtube.com/watch?v=o9pEzgHorH0)
- [Python 공식 문서 — dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [Real Python — When to Use Classes in Python](https://realpython.com/python3-object-oriented-programming/)
- [Fluent Python — Chapter 6: Design Patterns with First-Class Functions](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)

Tags: Python, OOP, 함수형 프로그래밍, dataclass, 설계 판단
