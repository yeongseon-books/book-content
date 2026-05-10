---
series: functional-programming-101
episode: 3
title: immutable 데이터
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
  - Functional Programming
  - 불변성
  - tuple
  - frozenset
seo_description: Python에서 불변 데이터를 활용하여 안전하고 예측 가능한 코드를 작성하는 방법을 다룹니다.
last_reviewed: '2026-05-04'
---

# immutable 데이터

> Functional Programming 101 시리즈 (3/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 데이터를 변경하지 않고 프로그램을 작성할 수 있을까요?

> 불변 데이터는 한번 생성되면 변경할 수 없습니다. 새 값이 필요하면 기존 데이터를 기반으로 새 데이터를 생성합니다. 이 글에서는 Python의 불변 타입과 불변 패턴을 활용하여 안전한 코드를 작성하는 방법을 다룹니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- Python의 mutable vs immutable 타입 구분
- tuple, frozenset, NamedTuple의 활용
- frozen dataclass로 불변 객체 만들기
- 불변 패턴이 병렬 처리와 디버깅을 쉽게 만드는 이유

## 왜 중요한가

mutable 데이터는 "누가 언제 변경했는지" 추적하기 어렵습니다. 함수에 리스트를 전달했는데 함수 내부에서 원본이 변경되면 버그를 찾기가 매우 어렵습니다.

> 불변 데이터 = 예측 불가능한 변경 제거

불변 데이터를 기본으로 사용하면 상태 관련 버그가 근본적으로 줄어들고, 코드의 추론이 쉬워집니다.

## 핵심 개념 잡기

> Python 타입의 가변/불변 분류

```
Immutable (불변)                 Mutable (가변)
─────────────────               ─────────────────
int, float, bool                list
str                             dict
tuple                           set
frozenset                       bytearray
bytes                           사용자 정의 클래스 (기본)
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 불변(immutable) | 생성 후 내부 상태를 변경할 수 없는 객체입니다 |
| 가변(mutable) | 생성 후에도 내부 상태를 변경할 수 있는 객체입니다 |
| 구조적 공유(structural sharing) | 불변 데이터 변경 시 변경되지 않은 부분을 재사용하는 기법입니다 |
| frozen dataclass | `frozen=True`로 생성한 변경 불가능한 dataclass입니다 |
| 방어적 복사(defensive copy) | 함수 경계에서 데이터를 복사하여 원본 변경을 방지하는 기법입니다 |

## Before / After

mutable 리스트를 불변 패턴으로 전환합니다.

```python
# before: 원본 리스트를 직접 변경
def add_tag(tags: list[str], tag: str) -> list[str]:
    tags.append(tag)
    return tags

original = ["python", "fp"]
result = add_tag(original, "immutable")
print(original)  # ['python', 'fp', 'immutable'] — 원본이 변경됨!
```

```python
# after: 새 리스트를 생성하여 반환
def add_tag(tags: list[str], tag: str) -> list[str]:
    return [*tags, tag]

original = ["python", "fp"]
result = add_tag(original, "immutable")
print(original)  # ['python', 'fp'] — 원본 유지
print(result)    # ['python', 'fp', 'immutable']
```

## 단계별 실습

### Step 1: Python 내장 불변 타입

```python
# tuple — 불변 시퀀스
point = (3, 4)
# point[0] = 5  # TypeError: 'tuple' does not support item assignment

# frozenset — 불변 집합
allowed = frozenset({"read", "write", "execute"})
# allowed.add("delete")  # AttributeError: 'frozenset' has no attribute 'add'

# str — 불변 문자열
name = "hello"
upper_name = name.upper()  # 새 문자열 생성
print(name)        # hello — 원본 유지
print(upper_name)  # HELLO


# tuple은 dict의 키로 사용 가능 (hashable)
grid: dict[tuple[int, int], str] = {
    (0, 0): "start",
    (1, 2): "goal",
}
print(grid[(0, 0)])  # start
```

### Step 2: NamedTuple로 의미 있는 불변 레코드

```python
from typing import NamedTuple


class Point(NamedTuple):
    x: float
    y: float

class Color(NamedTuple):
    r: int
    g: int
    b: int


p = Point(3.0, 4.0)
print(p.x, p.y)  # 3.0 4.0
# p.x = 5.0  # AttributeError — 불변

# 새 값이 필요하면 _replace로 복사 생성
p2 = p._replace(x=5.0)
print(p)   # Point(x=3.0, y=4.0) — 원본 유지
print(p2)  # Point(x=5.0, y=4.0)

red = Color(255, 0, 0)
print(red)  # Color(r=255, g=0, b=0)
```

### Step 3: frozen dataclass

```python
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class User:
    name: str
    email: str
    role: str = "viewer"


user = User(name="Alice", email="alice@example.com")
# user.name = "Bob"  # FrozenInstanceError — 변경 불가

# 새 인스턴스 생성
admin = replace(user, role="admin")
print(user)   # User(name='Alice', email='alice@example.com', role='viewer')
print(admin)  # User(name='Alice', email='alice@example.com', role='admin')


# frozen dataclass는 hashable → dict 키, set 원소로 사용 가능
users = {user, admin}
print(len(users))  # 2
```

### Step 4: 불변 딕셔너리 패턴

```python
from types import MappingProxyType


# MappingProxyType — 읽기 전용 딕셔너리 뷰
config = {"host": "localhost", "port": 8080, "debug": True}
readonly_config = MappingProxyType(config)

print(readonly_config["host"])  # localhost
# readonly_config["host"] = "0.0.0.0"  # TypeError — 변경 불가


# 딕셔너리 갱신 — 새 딕셔너리 생성
def update_config(config: dict, **updates) -> dict:
    return {**config, **updates}

original = {"host": "localhost", "port": 8080}
updated = update_config(original, port=9090, debug=False)

print(original)  # {'host': 'localhost', 'port': 8080} — 원본 유지
print(updated)   # {'host': 'localhost', 'port': 9090, 'debug': False}
```

### Step 5: 불변 데이터로 이력 관리

```python
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class AppState:
    count: int
    message: str


def increment(state: AppState) -> AppState:
    return replace(state, count=state.count + 1)

def set_message(state: AppState, msg: str) -> AppState:
    return replace(state, message=msg)


# 상태 이력 — 모든 변경 추적 가능
history: list[AppState] = []

state = AppState(count=0, message="시작")
history.append(state)

state = increment(state)
history.append(state)

state = increment(state)
history.append(state)

state = set_message(state, "완료")
history.append(state)

for i, s in enumerate(history):
    print(f"Step {i}: count={s.count}, message='{s.message}'")
# Step 0: count=0, message='시작'
# Step 1: count=1, message='시작'
# Step 2: count=2, message='시작'
# Step 3: count=2, message='완료'
```

## 이 코드에서 주목할 점

- Python의 tuple, frozenset, str은 기본 불변 타입입니다
- `NamedTuple._replace()`와 `dataclasses.replace()`는 불변 업데이트 패턴의 핵심입니다
- frozen dataclass는 hashable이므로 dict 키와 set 원소로 사용할 수 있습니다
- 불변 데이터를 사용하면 상태 이력(undo/redo)을 자연스럽게 구현할 수 있습니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| tuple 안에 mutable 객체 포함 | tuple은 불변이지만 내부 리스트는 변경 가능합니다 | 내부도 불변 타입을 사용합니다 |
| 함수 인자로 받은 dict를 직접 수정 | 호출자의 데이터가 변합니다 | `{**d, key: value}`로 새 dict를 만듭니다 |
| 기본 인자로 mutable 객체 사용 | 호출 간 상태가 공유됩니다 | `None`을 기본값으로 사용합니다 |
| 매번 전체를 복사 | 대용량 데이터에서 성능 문제가 발생합니다 | 구조적 공유나 필요한 부분만 복사합니다 |
| 불변 객체에 강제 변경 시도 | `object.__setattr__`로 우회하면 계약을 위반합니다 | frozen의 의도를 존중합니다 |

## 실무에서 이렇게 쓰입니다

- 설정 객체를 frozen dataclass로 정의하여 실행 중 변경을 방지합니다
- Redux 스타일 상태 관리에서 불변 상태 업데이트를 사용합니다
- API 응답 모델을 NamedTuple이나 frozen dataclass로 정의합니다
- 캐시 키로 tuple이나 frozenset을 사용합니다
- 이벤트 소싱에서 불변 이벤트 객체로 이력을 관리합니다

## 현업 개발자는 이렇게 생각합니다

"모든 것을 불변으로"가 목표가 아닙니다. 핵심은 기본적으로 불변을 선택하고, 성능이나 편의상 필요한 곳에서만 mutable을 사용하는 것입니다. Python에서는 `frozen=True`나 `NamedTuple`로 불변성을 쉽게 얻을 수 있습니다.

대규모 데이터 처리에서는 매번 전체를 복사하는 것이 비효율적일 수 있습니다. 이때는 제너레이터나 구조적 공유를 활용하여 불필요한 복사를 피하면서도 불변성의 이점을 유지할 수 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **얕은 복사 위험** — 중첩 자료의 공유 참조 함정을 인지합니다.
- **frozen dataclass** — 데이터 클래스의 frozen=True를 적극 활용합니다.
- **복사 비용** — 대규모 자료는 구조적 공유 라이브러리를 검토합니다.
- **동시성** — 불변성은 락 없는 동시성의 토대입니다.
- **디버깅** — 변경 추적이 단순해져 디버깅 시간을 줄입니다.

## 체크리스트

- [ ] Python의 mutable과 immutable 타입을 구분할 수 있다
- [ ] tuple과 frozenset을 적절히 사용할 수 있다
- [ ] frozen dataclass를 정의하고 `replace()`로 업데이트할 수 있다
- [ ] 함수 인자를 변경하지 않는 불변 패턴을 적용할 수 있다
- [ ] 불변 데이터의 장단점을 설명할 수 있다

## 연습 문제

1. mutable `dict`를 사용하는 설정 관리 코드를 frozen dataclass로 리팩터링하세요.
2. 상태 이력(undo)을 지원하는 간단한 텍스트 에디터를 불변 패턴으로 구현하세요.
3. `NamedTuple`로 2D 벡터를 정의하고 덧셈, 뺄셈, 스칼라 곱 함수를 작성하세요.

## 정리 및 다음 글 안내

불변 데이터는 예측 불가능한 변경을 제거하여 코드의 안정성을 높입니다. Python에서는 tuple, frozenset, NamedTuple, frozen dataclass로 불변성을 구현할 수 있습니다. 다음 글에서는 함수를 인자로 주고받는 **고차 함수**를 다룹니다.

<!-- toc:begin -->
- [함수형 프로그래밍이란 무엇인가?](./01-what-is-fp.md)
- [순수 함수와 부수효과](./02-pure-functions.md)
- **immutable 데이터 (현재 글)**
- [고차 함수](./04-higher-order-functions.md)
- [map, filter, reduce](./05-map-filter-reduce.md)
- [클로저와 partial](./06-closure-and-partial.md)
- [재귀와 꼬리 호출](./07-recursion.md)
- [지연 평가와 제너레이터](./08-lazy-evaluation.md)
- [함수 합성과 파이프라인](./09-function-composition.md)
- [객체지향과 함수형의 균형](./10-oop-and-fp-balance.md)
<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Data Model (Immutable Types)](https://docs.python.org/3/reference/datamodel.html)
- [Real Python — Immutability in Python](https://realpython.com/python-mutable-vs-immutable-types/)
- [Fluent Python — Chapter 8: Object References, Mutability, and Recycling](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)
- [Python 공식 문서 — dataclasses (frozen)](https://docs.python.org/3/library/dataclasses.html)
