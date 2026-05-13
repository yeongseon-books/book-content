---
series: type-hints-python-101
episode: 1
title: Python type hint란 무엇인가?
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
  - 타입 힌트
  - 정적 분석
  - mypy
  - 코드 품질
seo_description: Python 타입 힌트의 개념, 등장 배경, 기본 문법과 활용 이유를 살펴봅니다.
last_reviewed: '2026-05-12'
---

# Python type hint란 무엇인가?

작은 스크립트에서는 `data`, `value`, `result` 같은 이름만으로도 버틸 수 있습니다. 하지만 코드가 길어지고 함수가 여러 파일을 오가기 시작하면, 호출자가 무엇을 넘겨야 하고 무엇을 돌려받는지 시그니처만 보고 알 수 있어야 합니다.

이 글은 Type Hints (Python) 101 시리즈의 첫 번째 글입니다. 여기서는 타입 힌트가 무엇이고, Python의 동적 타이핑과 어떻게 공존하며, 왜 실무에서 빠르게 가치가 드러나는지부터 정리합니다.

## 이 글에서 다룰 문제

- 타입 힌트는 정적 타입 언어의 타입 선언과 무엇이 다를까요?
- PEP 484가 해결하려던 문제는 무엇이었을까요?
- 변수, 매개변수, 반환값에 어떤 문법으로 타입을 붙일까요?
- Python 런타임은 타입 힌트를 어떻게 다루고, mypy나 pyright는 무엇을 검사할까요?

> 타입 힌트는 Python을 정적 타입 언어로 바꾸는 기능이 아니라, 동적 언어 코드에 검증 가능한 계약을 추가하는 장치입니다.

## 왜 이 주제가 중요한가

Python은 유연합니다. 같은 변수에 문자열도 넣고, 리스트도 넣고, `None`도 넣을 수 있습니다. 이 유연성은 빠른 개발에는 유리하지만, 팀 단위 코드베이스에서는 함수 계약이 숨어 버리는 문제가 생깁니다. `calculate_total(data)`라는 시그니처만 보고는 `data`가 리스트인지, 딕셔너리인지, 모델 객체인지 알기 어렵습니다.

타입 힌트는 이 모호함을 줄입니다. 호출자는 함수 몸체를 열어 보지 않아도 입력과 출력의 형태를 먼저 읽을 수 있고, IDE와 정적 분석 도구는 그 계약을 코드 실행 전에 검증할 수 있습니다. 즉, 타입 힌트는 문서이면서 동시에 자동 검사 대상입니다.

## 한눈에 보는 개념

타입 힌트는 선택적 주석이지만, 도구는 이 주석을 진지하게 읽습니다.

```text
def greet(name: str) -> str:
         ^^^^  ^^^     ^^^
         매개변수 이름  타입    반환 타입
              │               │
        Python 런타임은 무시함
              │               │
        mypy/pyright는 정적으로 검증함
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| 타입 힌트 | 변수나 표현식이 기대하는 타입을 적는 주석성 어노테이션입니다 |
| PEP 484 | 2014년에 타입 힌트를 표준화한 Python 제안서입니다 |
| 정적 분석 | 코드를 실행하지 않고 오류 가능성을 검사하는 방식입니다 |
| 동적 타이핑 | 타입을 컴파일 시점이 아니라 실행 시점에 다루는 모델입니다 |
| 점진적 타이핑 | 기존 코드베이스에 타입 힌트를 조금씩 확장하는 방식입니다 |

## 바꾸기 전과 후

타입 힌트가 없으면 함수 계약을 시그니처에서 읽을 수 없습니다.

```python
def calculate_total(prices, tax_rate):
    subtotal = sum(prices)
    return int(subtotal * (1 + tax_rate))

# prices가 list인지 tuple인지, tax_rate가 무엇인지 시그니처만으로는 알 수 없습니다.
```

```python
def calculate_total(prices: list[int], tax_rate: float) -> int:
    subtotal = sum(prices)
    return int(subtotal * (1 + tax_rate))

# prices는 list[int], tax_rate는 float, 반환값은 int라는 계약이 드러납니다.
```

## 단계별로 익히기

### 1단계: 함수 매개변수와 반환값에 붙이기

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"


result = greet("Alice")  # OK
# greet(42)  # mypy 오류: Argument 1 has incompatible type "int"
```

기본 문법은 `매개변수: 타입`, `-> 반환타입`입니다. 중요한 점은 Python이 이 힌트를 실행 시점에 강제하지 않는다는 사실입니다.

### 2단계: 변수에도 붙이기

```python
count: int = 0
name: str = "Alice"
prices: list[int] = [1000, 2000, 3000]
config: dict[str, str] = {"host": "localhost", "port": "8080"}
```

변수 주석은 `이름: 타입 = 값` 형태를 씁니다. 다만 값만 봐도 타입이 분명한 지역 변수는 굳이 모두 적지 않아도 됩니다.

### 3단계: 내장 제네릭 타입 쓰기

```python
# Python 3.9+ — 내장 타입을 직접 사용합니다.
names: list[str] = ["Alice", "Bob"]
scores: dict[str, int] = {"Alice": 95, "Bob": 87}
coordinates: tuple[float, float] = (37.5, 127.0)
unique_ids: set[int] = {1, 2, 3}
```

Python 3.9부터는 `typing.List[str]` 대신 `list[str]`처럼 표준 컬렉션 타입을 바로 사용할 수 있습니다.

### 4단계: 클래스에도 적용하기

```python
class User:
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

    def greet(self) -> str:
        return f"Hi, I'm {self.name}."


user = User("Alice", 30)
print(user.greet())
```

`__init__`의 반환 타입은 항상 `None`입니다. `self`는 별도로 적지 않아도 분석기가 추론합니다.

### 5단계: 타입 검사기로 확인하기

```bash
pip install mypy
mypy app.py
```

```python
# app.py
def add(a: int, b: int) -> int:
    return a + b


add("hello", "world")  # mypy: Argument 1 has incompatible type "str"
```

이 순간부터 타입 힌트는 단순 메모가 아니라 자동으로 검증되는 계약이 됩니다.

## 여기서 먼저 봐야 할 점

- 타입 힌트 문법의 핵심은 `:`와 `->` 두 가지입니다.
- Python 런타임은 타입 힌트를 무시하므로, 잘못된 값이 들어와도 실행 자체는 될 수 있습니다.
- 실제 가치는 mypy, pyright, IDE 자동완성 같은 도구가 힌트를 읽을 때 생깁니다.
- 모든 지역 변수보다 공개 함수 시그니처에 먼저 붙일 때 투자 대비 효과가 큽니다.

## 자주 헷갈리는 지점

| 실수 | 왜 문제인가 | 권장 방식 |
| --- | --- | --- |
| 타입 힌트가 런타임 검증도 해 준다고 생각함 | Python은 힌트를 강제하지 않습니다 | 검증은 mypy, pyright, Pydantic 같은 도구에 맡깁니다 |
| Python 3.9+에서도 `typing.List`를 계속 씀 | 불필요한 임포트가 늘어납니다 | `list[str]`처럼 내장 타입을 바로 씁니다 |
| 모든 지역 변수에 타입을 붙임 | 코드만 길어지고 읽기 어려워집니다 | 추론 가능한 지역 변수는 생략합니다 |
| `__init__`에 `-> None`을 빼먹음 | 시그니처가 덜 분명해집니다 | 생성자는 항상 `-> None`을 적습니다 |
| 타입 힌트와 런타임 데이터 검증을 혼동함 | 잘못된 JSON 입력은 막지 못합니다 | 외부 데이터 검증은 Pydantic 같은 도구로 처리합니다 |

## 실무에서는 이렇게 연결됩니다

- FastAPI는 타입 힌트로 API 문서와 요청 스키마를 생성합니다.
- VS Code와 Pylance는 타입 정보를 바탕으로 자동완성과 오류 표시를 강화합니다.
- 대규모 코드베이스는 mypy를 CI에 넣어 리팩터링 회귀를 미리 잡습니다.
- 라이브러리는 `.pyi` 스텁 파일로 사용자에게 타입 정보를 제공합니다.

## 실무 판단 기준

시니어 엔지니어는 타입 힌트를 규칙 준수 항목보다 커뮤니케이션 도구로 봅니다. 여섯 달 뒤의 동료가 함수 몸체를 열어 보기 전에, 시그니처만 읽고도 안전하게 호출할 수 있게 만드는 편이 더 중요합니다. 좋은 타입 시그니처 하나가 긴 docstring보다 더 빨리 오해를 줄일 때가 많습니다.

또한 타입 힌트는 규모가 커질수록 복리처럼 이익이 커집니다. 처음에는 함수 몇 개에 불과하지만, 시간이 지나면 자동완성 품질, 리팩터링 안정성, 코드 리뷰 속도, 신규 입사자 온보딩 속도까지 영향을 줍니다.

## 체크리스트

- [ ] 함수 매개변수에 타입을 붙였습니다
- [ ] 함수 반환 타입을 명시했습니다
- [ ] Python 3.9+ 스타일의 내장 제네릭 타입을 사용했습니다
- [ ] mypy 또는 pyright로 타입 힌트를 검증할 준비가 되어 있습니다
- [ ] 추론 가능한 지역 변수에는 과한 주석을 달지 않았습니다

## 연습 문제

1. 예전에 작성한 Python 파일 하나를 골라 모든 함수 시그니처에 타입 힌트를 추가해 보세요. 그런 다음 `mypy`를 실행해 오류를 정리해 보세요.

2. `width: float`, `height: float`, `area() -> float`를 가진 `Rectangle` 클래스를 작성하고 mypy로 검사해 보세요.

3. 일부러 세 가지 타입 오류를 넣어 보세요. 잘못된 인자 타입, 잘못된 반환 타입, 누락된 반환 힌트를 각각 넣고 분석기가 어떤 메시지를 내는지 확인해 보세요.

## 정리와 다음 글

타입 힌트는 Python 코드의 실행 방식을 바꾸지 않습니다. 대신 함수와 데이터의 계약을 코드 위에 명시하고, 정적 분석 도구가 그 계약을 실행 전에 검사할 수 있게 만듭니다. 처음에는 공개 함수 시그니처부터 붙이는 방식이 가장 효율적입니다.

다음 글에서는 `int`, `str`, `bool` 같은 기본 타입과 `list`, `dict`, `tuple`, `set` 같은 컬렉션 타입을 어떻게 정확하게 적는지 자세히 보겠습니다.

<!-- toc:begin -->
- **Python type hint란 무엇인가? (현재 글)**
- [기본 타입과 collection 타입](./02-basic-and-collection-types.md)
- [Optional과 Union](./03-optional-and-union.md)
- [함수 타입 힌트](./04-function-type-hints.md)
- [TypedDict와 dataclass](./05-typeddict-and-dataclass.md)
- [Protocol과 structural typing](./06-protocol-and-structural-typing.md)
- [Generic 이해하기](./07-generic.md)
- [mypy와 pyright 사용하기](./08-mypy-and-pyright.md)
- [Pydantic과 타입 힌트](./09-pydantic-and-type-hints.md)
- [타입 힌트를 잘 쓰는 기준](./10-type-hints-best-practices.md)
<!-- toc:end -->

## 참고 자료

- [PEP 484 — Type Hints](https://peps.python.org/pep-0484/)
- [Python 공식 문서 — typing 모듈](https://docs.python.org/3/library/typing.html)
- [mypy 공식 문서](https://mypy.readthedocs.io/en/stable/)
- [Real Python — Python Type Checking](https://realpython.com/python-type-checking/)

Tags: Python, Type Hints, 타입 힌트, 정적 분석, mypy, 코드 품질
