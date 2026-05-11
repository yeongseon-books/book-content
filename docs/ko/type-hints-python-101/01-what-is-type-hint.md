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
last_reviewed: '2026-05-04'
---

# Python type hint란 무엇인가?

> Type Hints in Python 101 시리즈 (1/10)


## 이 글에서 다룰 문제

팀 프로젝트에서 함수의 인자가 문자열인지 정수인지 알 수 없으면, 코드를 읽는 데 시간이 걸리고 잘못된 타입을 전달하는 버그가 발생합니다. 타입 힌트는 이런 문제를 코드 자체에 문서화하여 해결합니다.

> 타입 힌트 = 코드에 내장된 문서

Python 3.5에서 PEP 484로 도입된 이후, FastAPI, Pydantic, SQLAlchemy 2.0 등 주요 라이브러리가 타입 힌트를 적극 활용하고 있습니다.

## 핵심 개념 잡기

> 동적 타입 vs 타입 힌트

```
동적 타입 (기본)              타입 힌트 적용
─────────────────           ─────────────────
def greet(name):            def greet(name: str) -> str:
    return "Hello " + name      return "Hello " + name
# name이 뭔지 모름            # name은 str, 반환도 str
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 타입 힌트(type hint) | 변수나 함수의 기대 타입을 명시하는 주석입니다 |
| PEP 484 | Python 타입 힌트 표준을 정의한 제안서입니다 |
| 정적 분석(static analysis) | 코드를 실행하지 않고 오류를 검출하는 기법입니다 |
| mypy | Python 타입 힌트를 검증하는 대표적인 정적 분석 도구입니다 |
| 런타임 비강제 | Python 인터프리터가 타입 힌트를 실행 시 검사하지 않습니다 |

## Before / After

타입 정보가 없는 코드를 타입 힌트로 개선합니다.

```python
# before: 인자와 반환 타입을 알 수 없음
def calculate_total(price, quantity, discount):
    return price * quantity * (1 - discount)
```

```python
# after: 타입이 명확하게 드러남
def calculate_total(price: float, quantity: int, discount: float) -> float:
    return price * quantity * (1 - discount)
```

## 단계별 실습

### Step 1: 변수 타입 힌트

```python
# 변수에 타입 힌트 적용
name: str = "Alice"
age: int = 30
height: float = 165.5
is_active: bool = True

# Python 3.9+: 내장 타입으로 컬렉션 표기
scores: list[int] = [85, 92, 78]
metadata: dict[str, str] = {"role": "admin", "team": "backend"}

print(f"이름: {name}, 나이: {age}")
print(f"점수: {scores}")
print(f"메타: {metadata}")
```

### Step 2: 함수 타입 힌트

```python
def greet(name: str) -> str:
    """이름을 받아 인사 메시지를 반환합니다."""
    return f"안녕하세요, {name}님!"


def add(a: int, b: int) -> int:
    """두 정수를 더합니다."""
    return a + b


def is_adult(age: int) -> bool:
    """성인 여부를 확인합니다."""
    return age >= 18


print(greet("Alice"))     # 안녕하세요, Alice님!
print(add(3, 5))          # 8
print(is_adult(20))       # True
```

### Step 3: 타입 힌트는 런타임에 강제되지 않음

```python
def double(n: int) -> int:
    return n * 2


# 타입 힌트와 다른 값을 전달해도 실행됨
result = double("hello")
print(result)  # hellohello

# Python은 타입 힌트를 무시하고 실행함
# 하지만 mypy 같은 도구가 이 오류를 잡아냄
# mypy 실행 시: error: Argument 1 to "double" has incompatible type "str"; expected "int"
```

### Step 4: __annotations__ 확인

```python
def process(name: str, count: int) -> list[str]:
    return [name] * count


# 함수의 타입 힌트는 __annotations__에 저장됨
print(process.__annotations__)
# {'name': <class 'str'>, 'count': <class 'int'>, 'return': list[str]}

# 변수 타입 힌트도 확인 가능
x: int = 10
y: str = "hello"
print(__annotations__)
# {'x': <class 'int'>, 'y': <class 'str'>}
```

### Step 5: None 반환 타입

```python
def log_message(message: str) -> None:
    """메시지를 출력합니다. 반환값 없음."""
    print(f"[LOG] {message}")


def save_to_file(data: str, path: str) -> None:
    """데이터를 파일에 저장합니다."""
    with open(path, "w") as f:
        f.write(data)
    print(f"저장 완료: {path}")


log_message("서버 시작")
# [LOG] 서버 시작

# 반환값이 없는 함수에 -> None을 명시하면
# 실수로 반환값을 사용하는 코드를 mypy가 잡아줌
```

## 이 코드에서 주목할 점

- 타입 힌트는 `변수: 타입`, `함수(인자: 타입) -> 반환타입` 형태로 작성합니다
- Python 런타임은 타입 힌트를 검사하지 않으므로 성능에 영향이 없습니다
- `__annotations__`에 타입 정보가 저장되어 런타임에서도 조회할 수 있습니다
- 반환값이 없는 함수에는 `-> None`을 명시합니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 타입 힌트를 런타임 검증으로 착각 | 잘못된 타입이 전달되어도 실행됩니다 | mypy나 pyright로 정적 검증합니다 |
| 모든 변수에 타입 힌트 적용 | 코드가 장황해집니다 | 함수 시그니처와 공개 API에 집중합니다 |
| Python 3.8에서 `list[int]` 사용 | TypeError가 발생합니다 | `from __future__ import annotations`를 추가합니다 |
| 반환 타입 생략 | 함수의 의도가 불명확해집니다 | `-> None` 포함 모든 함수에 반환 타입을 명시합니다 |
| 타입 힌트만 쓰고 검증 도구를 사용하지 않음 | 힌트가 틀려도 아무도 모릅니다 | CI에 mypy를 통합합니다 |

## 실무에서 이렇게 쓰입니다

- FastAPI는 타입 힌트로 요청/응답 스키마를 자동 생성합니다
- Pydantic은 타입 힌트 기반으로 데이터 검증을 수행합니다
- IDE(PyCharm, VS Code)가 자동완성과 오류 강조를 제공합니다
- 대규모 프로젝트에서 리팩터링 시 안전성을 확보합니다
- 새 팀원이 코드를 빠르게 이해할 수 있습니다

## 현업 개발자는 이렇게 생각합니다

타입 힌트는 "코드에 내장된 문서"입니다. 주석은 코드와 동기화되지 않지만, 타입 힌트는 정적 분석 도구가 검증하므로 항상 최신 상태를 유지합니다. 특히 FastAPI와 Pydantic을 사용하는 현대 Python 프로젝트에서는 타입 힌트가 선택이 아닌 필수입니다.

처음부터 모든 코드에 적용할 필요는 없습니다. 공개 API, 함수 시그니처부터 시작하고, mypy를 CI에 통합하면 자연스럽게 타입 힌트 커버리지가 늘어납니다.

## 체크리스트

- [ ] 변수에 타입 힌트를 적용할 수 있다
- [ ] 함수 인자와 반환 타입을 명시할 수 있다
- [ ] 타입 힌트가 런타임에 강제되지 않음을 이해한다
- [ ] `__annotations__`로 타입 정보를 확인할 수 있다
- [ ] 타입 힌트의 도입 이점을 설명할 수 있다

## 정리 및 다음 글 안내

타입 힌트는 Python 코드에 타입 정보를 명시하는 기능으로, 정적 분석 도구와 IDE를 통해 버그를 사전에 방지합니다. 다음 글에서는 `int`, `str`을 넘어 리스트, 딕셔너리, 튜플 등 **기본 타입과 collection 타입**의 힌트 작성법을 다룹니다.

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
- [mypy 공식 문서](https://mypy.readthedocs.io/)
- [Real Python — Python Type Checking](https://realpython.com/python-type-checking/)
