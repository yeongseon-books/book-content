---
series: oop-101
episode: 10
title: 객체지향을 언제 피해야 할까?
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
  - 함수형 프로그래밍
  - dataclass
  - 설계 판단
seo_description: 객체지향이 적합하지 않은 상황과 대안적 접근 방법을 다룹니다.
last_reviewed: '2026-05-04'
---

# 객체지향을 언제 피해야 할까?

> Object-Oriented Programming 101 시리즈 (10/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 모든 문제를 클래스로 해결해야 할까요? 객체지향이 오히려 방해가 되는 상황은 언제일까요?

> 객체지향은 강력한 도구이지만 만능은 아닙니다. 간단한 스크립트, 데이터 변환 파이프라인, 상태 없는 유틸리티에서는 함수와 모듈만으로 더 깔끔한 코드를 작성할 수 있습니다. 이 글에서는 OOP가 적합하지 않은 상황과 대안을 다룹니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 객체지향이 과도한 상황의 신호
- 함수 기반 접근이 더 적합한 패턴
- dataclass와 NamedTuple의 활용
- OOP와 함수형 프로그래밍의 적절한 혼용

## 왜 중요한가

"망치를 들면 모든 것이 못으로 보인다"는 말처럼, OOP를 배우면 모든 것을 클래스로 만들려는 경향이 있습니다. 그러나 Python은 다중 패러다임 언어이고, 상황에 맞는 도구를 선택하는 것이 좋은 코드의 핵심입니다.

> 좋은 설계 = 문제에 맞는 도구 선택

불필요한 클래스는 코드를 읽기 어렵게 만들고, 유지보수 비용을 높입니다. "이것을 클래스로 만들어야 하는가?"라는 질문을 항상 자문해야 합니다.

## 핵심 개념 잡기

> OOP vs 대안 — 선택 기준

```
클래스가 필요한 경우              클래스가 불필요한 경우
─────────────────────           ─────────────────────
상태 + 행위가 결합               상태 없는 변환 함수
여러 인스턴스가 필요              단일 실행 스크립트
교체 가능한 전략이 필요           데이터만 담는 컨테이너
프레임워크가 클래스를 요구         파이프라인 데이터 처리
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 다중 패러다임(multi-paradigm) | 절차, 객체지향, 함수형을 혼용할 수 있는 언어입니다 |
| 빈혈 도메인 모델(anemic) | 데이터만 있고 행위가 없는 클래스입니다 |
| dataclass | 데이터 중심 클래스를 간결하게 정의하는 Python 기능입니다 |
| 고차 함수(higher-order function) | 함수를 인자로 받거나 반환하는 함수입니다 |
| 클로저(closure) | 외부 변수를 기억하는 내부 함수입니다 |

## Before / After

불필요한 클래스를 제거합니다.

```python
# before: 메서드 하나뿐인 불필요한 클래스
class Validator:
    def validate_email(self, email: str) -> bool:
        return "@" in email and "." in email

validator = Validator()
print(validator.validate_email("test@example.com"))
```

```python
# after: 함수로 충분
def validate_email(email: str) -> bool:
    return "@" in email and "." in email

print(validate_email("test@example.com"))
```

## 단계별 실습

### Step 1: 클래스 대신 함수

```python
# 불필요한 클래스 — 상태 없이 메서드만 있음
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


# 개선: 모듈 수준 함수
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

### Step 2: 클래스 대신 dataclass / NamedTuple

```python
from dataclasses import dataclass
from typing import NamedTuple


# 불필요한 boilerplate — 수동 __init__, __repr__, __eq__
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


# 개선 1: dataclass
@dataclass
class Point:
    x: float
    y: float

# 개선 2: NamedTuple (불변)
class ImmutablePoint(NamedTuple):
    x: float
    y: float


p1 = Point(1, 2)
p2 = Point(1, 2)
print(p1)        # Point(x=1, y=2)
print(p1 == p2)  # True

ip = ImmutablePoint(3, 4)
print(ip.x)  # 3
# ip.x = 10  # AttributeError — 불변
```

### Step 3: 클래스 대신 고차 함수

```python
# 전략 패턴 — 클래스 버전
from typing import Protocol

class Formatter(Protocol):
    def format(self, value: float) -> str: ...

class CurrencyFormatter:
    def format(self, value: float) -> str:
        return f"{value:,.0f}원"

class PercentFormatter:
    def format(self, value: float) -> str:
        return f"{value:.1f}%"


# 개선: 함수로 충분 — 클래스 없이
from typing import Callable

def currency_format(value: float) -> str:
    return f"{value:,.0f}원"

def percent_format(value: float) -> str:
    return f"{value:.1f}%"

def display_values(
    values: list[float],
    formatter: Callable[[float], str],
) -> None:
    for v in values:
        print(formatter(v))


display_values([1000, 2500, 50000], currency_format)
# 1,000원
# 2,500원
# 50,000원

display_values([0.95, 0.87, 0.12], percent_format)
# 0.9%
# 0.9%
# 0.1%
```

### Step 4: 클래스 대신 딕셔너리 / 튜플

```python
# 불필요한 클래스 — 데이터만 담는 용도
class Config:
    def __init__(self, host: str, port: int, debug: bool) -> None:
        self.host = host
        self.port = port
        self.debug = debug


# 개선 1: TypedDict (구조화된 딕셔너리)
from typing import TypedDict

class Config(TypedDict):
    host: str
    port: int
    debug: bool

config: Config = {"host": "localhost", "port": 8080, "debug": True}
print(config["host"])  # localhost


# 개선 2: 간단한 설정은 dict로 충분
config = {"host": "localhost", "port": 8080, "debug": True}
```

### Step 5: 함수형 파이프라인

```python
from functools import reduce


# 데이터 변환 — 클래스 없이 함수 체이닝
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
    return [f"{d['name']}: {d['score']}점" for d in data]


# 파이프라인 실행
result = format_results(sort_by_score(filter_passing(clean_names(load_data()))))
for line in result:
    print(line)
# Diana: 95점
# Bob: 92점
# Alice: 85점
```

## 이 코드에서 주목할 점

- 상태 없는 유틸리티 함수는 모듈 수준 함수가 더 간결합니다
- `dataclass`와 `NamedTuple`은 데이터 중심 클래스의 boilerplate를 제거합니다
- 단순 전략 패턴은 `Callable`로 대체 가능합니다
- 데이터 변환 파이프라인은 함수 체이닝이 자연스럽습니다

## 흔한 실수 5가지

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

## 연습 문제

1. 메서드가 3개인 `MathHelper` 클래스를 모듈 수준 함수로 리팩터링하세요.
2. `Student` 클래스를 `dataclass`로 변환하고 정렬, 필터링 함수를 작성하세요.
3. CSV 파일을 읽고 변환하여 JSON으로 출력하는 파이프라인을 함수 체이닝으로 구현하세요.

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
