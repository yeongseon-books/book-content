---
series: type-hints-python-101
episode: 2
title: 기본 타입과 collection 타입
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - Type Hints
  - 컬렉션 타입
  - list
  - dict
  - tuple
seo_description: int, str부터 list, dict, tuple까지 Python 타입 힌트의 기본 타입과 컬렉션 타입을 다룹니다.
last_reviewed: '2026-05-12'
---

# 기본 타입과 collection 타입

타입 힌트를 처음 붙일 때 가장 많이 나오는 질문은 단순합니다. `name: str`은 알겠는데, 리스트와 딕셔너리 안에 무엇이 들어가는지는 어떻게 적어야 할까요? 바로 이 지점부터 타입 힌트가 문서 수준을 넘어 실제 오류 방지 도구로 바뀝니다.

이 글은 Type Hints (Python) 101 시리즈의 2번째 글입니다. 여기서는 기본 스칼라 타입과 컬렉션 타입을 어떻게 표현하는지, 그리고 컨테이너 안쪽 타입까지 적어야 하는 이유를 정리합니다.

## 이 글에서 다룰 문제

- `int`, `str`, `float`, `bool`, `bytes`, `None`은 어떻게 적을까요?
- `list`, `dict`, `tuple`, `set`은 왜 원소 타입까지 붙여야 할까요?
- 고정 길이 튜플과 가변 길이 튜플은 어떻게 다를까요?
- 중첩된 자료구조는 어떤 방식으로 읽기 좋게 표현할까요?

> 컬렉션 타입 힌트의 핵심은 컨테이너의 종류가 아니라, 그 안에 무엇이 들어가는지를 명시하는 데 있습니다.

## 왜 이 주제가 중요한가

실무 Python 코드는 대부분 컬렉션과 함께 움직입니다. API 응답은 딕셔너리와 리스트로 오고, 설정은 중첩 딕셔너리로 들어오며, 쿼리 결과는 튜플 목록으로 다뤄집니다. 이때 `list`나 `dict`만 적어 두면 분석기는 안쪽 원소를 `object`에 가깝게 취급하고, 엉뚱한 메서드 호출이나 잘못된 값 삽입을 충분히 잡아내지 못합니다.

예를 들어 `list[int]`와 `list[str]`는 전혀 다른 계약입니다. 전자에는 합계를 구할 수 있지만 후자에는 `sum()`을 쓰기 어렵습니다. 이 차이를 타입 힌트에 적지 않으면, 도구는 호출자가 어떤 연산을 해도 미리 경고할 근거를 얻지 못합니다.

## 한눈에 보는 개념

```text
스칼라 타입:  int    str    float    bool    None
                  \    |      /         |
컬렉션 타입:   list[int]  dict[str, float]  tuple[str, int]
                  \            |                /
중첩 타입:     dict[str, list[int]]
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| 스칼라 타입 | `int`, `str`, `float`, `bool`처럼 단일 값을 나타내는 타입입니다 |
| 매개화된 타입 | `list[int]`처럼 타입 인자를 가진 제네릭 타입입니다 |
| 동종 튜플 | 길이는 가변이고 원소 타입은 같은 튜플입니다. 예: `tuple[int, ...]` |
| 이종 튜플 | 길이와 위치별 타입이 정해진 튜플입니다. 예: `tuple[str, int]` |
| 타입 별칭 | 복잡한 타입에 이름을 붙여 가독성을 높이는 방식입니다 |

## 바꾸기 전과 후

```python
def get_prices(items: list) -> dict:
    result = {}
    for item in items:
        result[item.name] = item.price  # 타입 검사기: 속성을 알 수 없음
    return result
```

```python
def get_prices(items: list[Product]) -> dict[str, int]:
    result: dict[str, int] = {}
    for item in items:
        result[item.name] = item.price  # 타입 검사기: OK
    return result
```

컨테이너의 내부 타입을 적는 순간, 분석기는 `item.name`, `item.price`, `result`의 키와 값까지 추적할 수 있습니다.

## 단계별로 익히기

### 1단계: 기본 스칼라 타입

```python
name: str = "Alice"
age: int = 30
height: float = 5.7
is_active: bool = True
data: bytes = b"hello"
nothing: None = None
```

복잡한 타입도 결국은 이런 기본 타입을 조합해서 표현합니다.

### 2단계: list와 set

```python
names: list[str] = ["Alice", "Bob", "Charlie"]
unique_ids: set[int] = {1, 2, 3}

# 중첩 리스트
matrix: list[list[int]] = [
    [1, 2, 3],
    [4, 5, 6],
]


def get_active_users(users: list[str]) -> set[str]:
    return set(users)
```

`list[str]`는 모든 원소가 문자열이어야 한다는 뜻입니다. 따라서 `names.append(42)` 같은 코드는 타입 검사기에서 바로 걸립니다.

### 3단계: dict

```python
scores: dict[str, int] = {"Alice": 95, "Bob": 87}
config: dict[str, str | int | bool] = {
    "host": "localhost",
    "port": 8080,
    "debug": True,
}


def get_headers() -> dict[str, str]:
    return {"Content-Type": "application/json"}
```

`dict[str, int]`는 키는 문자열, 값은 정수라는 뜻입니다. 값 타입이 섞여 있다면 `Union` 또는 `|` 문법을 함께 써야 합니다.

### 4단계: tuple — 고정 구조와 가변 구조

```python
# 이종 튜플: 길이 고정, 위치별 타입 고정
coordinate: tuple[float, float] = (37.5, 127.0)
record: tuple[str, int, bool] = ("Alice", 30, True)

# 동종 튜플: 길이 가변, 모든 원소 타입 동일
numbers: tuple[int, ...] = (1, 2, 3, 4, 5)
empty: tuple[()] = ()
```

`tuple[int, ...]`의 `...`는 정수 원소가 0개 이상 이어질 수 있다는 뜻입니다. 반대로 `tuple[str, int]`는 정확히 두 칸짜리 구조입니다.

### 5단계: 복잡한 타입은 별칭으로 정리하기

```python
# 가독성을 위한 타입 별칭
UserScores = dict[str, list[int]]
Config = dict[str, str | int | bool | list[str]]


def aggregate_scores(data: UserScores) -> dict[str, float]:
    return {name: sum(scores) / len(scores) for name, scores in data.items()}


scores: UserScores = {
    "Alice": [95, 87, 92],
    "Bob": [78, 85, 90],
}
```

중첩 구조가 길어지면 타입 별칭이 가독성에 큰 도움을 줍니다. Python 3.12 이상에서는 `type UserScores = dict[str, list[int]]` 문법도 사용할 수 있습니다.

## 여기서 먼저 봐야 할 점

- 컬렉션 타입은 원소 타입까지 적어야 정적 분석에 의미가 생깁니다.
- 튜플은 `tuple[int, int]`와 `tuple[int, ...]`가 전혀 다른 구조입니다.
- `dict[str, list[int]]` 같은 중첩 타입도 충분히 실용적으로 사용할 수 있습니다.
- 타입 별칭은 중첩 구조가 길어질수록 가치가 커집니다.

## 자주 헷갈리는 지점

| 실수 | 왜 문제인가 | 권장 방식 |
| --- | --- | --- |
| `list`, `dict`만 적음 | 원소 타입을 추적할 수 없습니다 | `list[int]`, `dict[str, str]`처럼 매개화합니다 |
| `tuple[int, int]`와 `tuple[int, ...]`를 혼동함 | 하나는 고정 길이, 하나는 가변 길이입니다 | 의도한 구조를 정확히 구분합니다 |
| Python 3.9+에서 `typing.List`를 계속 씀 | 불필요한 임포트가 늘어납니다 | 내장 컬렉션 타입을 직접 사용합니다 |
| `dict[str, Any]`를 너무 넓게 씀 | 값 타입 안전성이 사라집니다 | 가능한 한 구체 타입이나 TypedDict를 씁니다 |
| 불변 집합인데 `set`을 사용함 | 가변성 계약이 어긋납니다 | 불변이 필요하면 `frozenset[T]`를 검토합니다 |

## 실무에서는 이렇게 연결됩니다

- JSON 구조는 `dict[str, list[dict[str, str]]]`처럼 중첩 타입으로 표현합니다.
- 데이터베이스 결과는 `list[tuple[int, str, float]]`처럼 행 구조를 타입으로 적을 수 있습니다.
- 설정 로더는 `dict[str, str | int | bool]` 형태로 혼합 값을 관리합니다.
- 캐시나 저장소 래퍼는 이후 Generic과 결합해 `dict[str, T]` 형태로 확장됩니다.

## 실무 판단 기준

경험 많은 개발자는 컬렉션 타입을 절대 맨몸으로 두지 않습니다. `list`라고만 적는 순간 가장 중요한 정보인 원소 타입을 버리기 때문입니다. `list[int]`를 적는 데 몇 초 더 걸리더라도, 잘못된 타입이 세 단계 아래 호출 체인으로 흘러가는 문제를 미리 막는 효과가 훨씬 큽니다.

또한 타입을 넓게 잡는 것보다 정확하게 잡는 편을 선호합니다. `dict[str, Any]`는 편해 보이지만 곧 분석기를 무력화합니다. 데이터의 모양을 알고 있다면 더 구체적인 컬렉션 타입이나 `TypedDict`로 이동하는 편이 좋습니다.

## 체크리스트

- [ ] 컬렉션 타입에 원소 타입을 함께 적었습니다
- [ ] 고정 구조 데이터에는 이종 튜플을 사용했습니다
- [ ] 복잡한 중첩 타입에는 타입 별칭을 고려했습니다
- [ ] `list`, `dict`, `tuple`을 타입 인자 없이 두지 않았습니다
- [ ] Python 3.9+ 스타일의 내장 타입 문법을 사용했습니다

## 연습 문제

1. `flatten(matrix: list[list[int]]) -> list[int]` 함수를 작성하고 mypy로 검사해 보세요.

2. `StudentRecord = tuple[str, int, list[float]]` 타입 별칭을 만들고, 학생 목록에서 평균 점수를 계산하는 함수를 작성해 보세요.

3. `dict[str, dict[str, str | int | list[str]]]` 형태의 설정 구조를 타입으로 적고, 특정 값을 꺼내는 함수를 만들어 보세요.

## 정리와 다음 글

기본 타입과 컬렉션 타입은 Python 타입 힌트의 가장 넓은 바닥을 이룹니다. `int`, `str`, `float`, `bool` 같은 스칼라 타입 위에 `list[T]`, `dict[K, V]`, `tuple[...]`, `set[T]` 같은 컨테이너가 쌓입니다. 여기서 중요한 습관은 컬렉션 안쪽 타입을 생략하지 않는 것입니다.

다음 글에서는 값이 없을 수도 있거나 여러 타입 중 하나일 수 있는 상황을 표현하는 `Optional`과 `Union`을 다룹니다.

<!-- toc:begin -->
- [Python type hint란 무엇인가?](./01-what-is-type-hint.md)
- **기본 타입과 collection 타입 (현재 글)**
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

- [Python 공식 문서 — typing 모듈](https://docs.python.org/3/library/typing.html)
- [PEP 585 — Type Hinting Generics In Standard Collections](https://peps.python.org/pep-0585/)
- [mypy 문서 — Built-in types](https://mypy.readthedocs.io/en/stable/builtin_types.html)
- [Real Python — Python Type Checking](https://realpython.com/python-type-checking/)

Tags: Python, Type Hints, 컬렉션 타입, list, dict, tuple
