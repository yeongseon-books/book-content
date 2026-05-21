---
series: functional-programming-101
episode: 3
title: "Functional Programming 101 (3/10): immutable 데이터"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - Functional Programming
  - 불변성
  - tuple
  - frozenset
seo_description: Python에서 불변 데이터를 사용해 안전하고 예측 가능한 코드를 만드는 방법입니다.
last_reviewed: '2026-05-12'
---

# Functional Programming 101 (3/10): immutable 데이터

이 글은 Functional Programming 101 시리즈의 세 번째 글입니다.

상태 관련 버그를 줄이는 가장 강력한 방법 중 하나는 아예 기존 데이터를 바꾸지 않는 것입니다. 이미 생성한 값을 직접 수정하지 않고, 필요할 때마다 새 값을 만들어 쓰는 방식으로 사고를 전환하면 코드의 추적 가능성이 크게 좋아집니다.

Python은 기본적으로 mutable 객체를 많이 쓰는 언어이지만, 동시에 `tuple`, `frozenset`, `NamedTuple`, `frozen dataclass` 같은 좋은 불변 도구도 제공합니다. 중요한 것은 "무조건 복사하라"가 아니라, 바뀌지 않아야 하는 값을 명확하게 모델링하는 감각입니다.

## 먼저 던지는 질문

- Python에서 mutable 타입과 immutable 타입은 어떻게 구분할까요?
- `tuple`, `frozenset`, `NamedTuple`, `frozen dataclass`는 각각 언제 유용할까요?
- 함수 경계에서 원본 변경을 막으려면 어떤 패턴이 필요할까요?

## 큰 그림

![Functional Programming 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/functional-programming-101/03/03-01-big-picture.ko.png)

*Functional Programming 101 3장 흐름 개요*

## 왜 중요한가

mutable 데이터는 "누가, 언제, 무엇을 바꿨는가"를 추적하기 어렵게 만듭니다. 함수 하나가 받은 리스트를 직접 수정해 버리면, 호출한 쪽에서는 예상하지 못한 시점에 원본이 바뀐 상태를 만나게 됩니다. 이런 문제는 디버깅 비용을 크게 높입니다.

불변성을 기본값으로 두면 상태 관련 버그의 한 범주를 아예 제거할 수 있습니다. 특히 캐시 키, 설정 객체, 상태 이력, 병렬 처리처럼 값의 안정성이 중요한 영역에서는 불변 데이터가 매우 좋은 기본 선택입니다.

## 개념 개요

> Python에서는 모든 값을 똑같이 다루면 안 됩니다. 처음부터 "이 값은 바뀌어도 되는가"를 구분해야 설계가 단단해집니다.

```text
Immutable                       Mutable
─────────────────               ─────────────────
int, float, bool                list
str                             dict
tuple                           set
frozenset                       bytearray
bytes                           user-defined classes (default)
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 불변(immutable) | 생성 후 내부 상태를 바꿀 수 없는 객체입니다 |
| 가변(mutable) | 생성 후 내부 상태를 바꿀 수 있는 객체입니다 |
| 구조적 공유(structural sharing) | 일부만 바뀐 새 값을 만들 때, 바뀌지 않은 부분은 재사용하는 방식입니다 |
| frozen dataclass | `frozen=True`로 정의해 속성 할당을 막은 dataclass입니다 |
| 방어적 복사(defensive copy) | 원본 변경을 막기 위해 함수 경계에서 데이터를 복사하는 패턴입니다 |

## Before / After

원본 리스트를 직접 수정하는 코드는 호출자에게 숨은 부작용을 만듭니다. 새 리스트를 반환하면 변경이 명시적이 됩니다.

```python
# before: mutating the original list
def add_tag(tags: list[str], tag: str) -> list[str]:
    tags.append(tag)
    return tags

original = ["python", "fp"]
result = add_tag(original, "immutable")
print(original)  # ['python', 'fp', 'immutable'] — original changed!
```

```python
# after: creating a new list
def add_tag(tags: list[str], tag: str) -> list[str]:
    return [*tags, tag]

original = ["python", "fp"]
result = add_tag(original, "immutable")
print(original)  # ['python', 'fp'] — original preserved
print(result)    # ['python', 'fp', 'immutable']
```

## 단계별 실습

### Step 1: Python 내장 불변 타입

```python
# tuple — immutable sequence
point = (3, 4)
# point[0] = 5  # TypeError: 'tuple' does not support item assignment

# frozenset — immutable set
allowed = frozenset({"read", "write", "execute"})
# allowed.add("delete")  # AttributeError: 'frozenset' has no attribute 'add'

# str — immutable string
name = "hello"
upper_name = name.upper()  # creates a new string
print(name)        # hello — original preserved
print(upper_name)  # HELLO

# tuples are hashable and can serve as dict keys
grid: dict[tuple[int, int], str] = {
    (0, 0): "start",
    (1, 2): "goal",
}
print(grid[(0, 0)])  # start
```

이 예제에서 중요한 점은 "바꿀 수 없다"는 제약이 오히려 설계를 명확하게 만든다는 것입니다. 좌표, 권한 집합, 문자열 같은 값은 애초에 변경 가능한 상태로 둘 이유가 많지 않습니다.

### Step 2: NamedTuple로 의미 있는 불변 레코드 만들기

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
# p.x = 5.0  # AttributeError — immutable

# create a modified copy with _replace
p2 = p._replace(x=5.0)
print(p)   # Point(x=3.0, y=4.0) — original preserved
print(p2)  # Point(x=5.0, y=4.0)

red = Color(255, 0, 0)
print(red)  # Color(r=255, g=0, b=0)
```

`NamedTuple`은 읽기 쉬운 필드 이름과 불변성을 동시에 제공합니다. 작은 값 객체를 표현할 때 매우 경제적인 선택입니다.

### Step 3: frozen dataclass 사용하기

```python
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class User:
    name: str
    email: str
    role: str = "viewer"

user = User(name="Alice", email="alice@example.com")
# user.name = "Bob"  # FrozenInstanceError — cannot modify

# create a new instance
admin = replace(user, role="admin")
print(user)   # User(name='Alice', email='alice@example.com', role='viewer')
print(admin)  # User(name='Alice', email='alice@example.com', role='admin')

# frozen dataclasses are hashable — usable as dict keys and set elements
users = {user, admin}
print(len(users))  # 2
```

`frozen dataclass`는 실무에서 특히 유용합니다. 설정 객체, DTO, 도메인 값 객체처럼 "의미 있는 레코드"를 안정적으로 표현할 수 있기 때문입니다.

### Step 4: 불변 딕셔너리 패턴

```python
from types import MappingProxyType

# MappingProxyType — read-only dictionary view
config = {"host": "localhost", "port": 8080, "debug": True}
readonly_config = MappingProxyType(config)

print(readonly_config["host"])  # localhost
# readonly_config["host"] = "0.0.0.0"  # TypeError — cannot modify

# dictionary update — create a new dictionary
def update_config(config: dict, **updates) -> dict:
    return {**config, **updates}

original = {"host": "localhost", "port": 8080}
updated = update_config(original, port=9090, debug=False)

print(original)  # {'host': 'localhost', 'port': 8080} — original preserved
print(updated)   # {'host': 'localhost', 'port': 9090, 'debug': False}
```

딕셔너리는 편리하지만 무심코 수정하기 쉽습니다. 그래서 설정처럼 안정성이 필요한 데이터는 읽기 전용 뷰나 새 딕셔너리 반환 패턴을 습관적으로 쓰는 편이 안전합니다.

### Step 5: 불변 데이터로 상태 이력 관리하기

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

# state history — every change is tracked
history: list[AppState] = []

state = AppState(count=0, message="start")
history.append(state)

state = increment(state)
history.append(state)

state = increment(state)
history.append(state)

state = set_message(state, "done")
history.append(state)

for i, s in enumerate(history):
    print(f"Step {i}: count={s.count}, message='{s.message}'")
# Step 0: count=0, message='start'
# Step 1: count=1, message='start'
# Step 2: count=2, message='start'
# Step 3: count=2, message='done'
```

불변 데이터가 강력한 이유가 여기서 드러납니다. 현재 상태만 있는 것이 아니라, 상태 변화의 이력이 그대로 남습니다. undo/redo나 이벤트 소싱과 잘 맞는 이유도 이 때문입니다.

## 이 코드에서 주목할 점

- Python의 `tuple`, `frozenset`, `str`은 대표적인 내장 불변 타입입니다.
- `NamedTuple._replace()`와 `dataclasses.replace()`는 불변 업데이트의 핵심 패턴입니다.
- `frozen dataclass`는 hashable해서 dict 키나 set 원소로 활용할 수 있습니다.
- 불변 데이터는 상태 이력과 되돌리기 기능을 자연스럽게 구현하게 해 줍니다.

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 튜플 안에 mutable 객체를 넣음 | 바깥은 불변이어도 안쪽 리스트는 바뀔 수 있습니다 | 내부 원소도 가능하면 불변 타입으로 선택합니다 |
| 함수 인자로 받은 dict를 직접 수정함 | 호출자 데이터가 예기치 않게 바뀝니다 | `{**d, key: value}` 패턴으로 새 dict를 만듭니다 |
| mutable 기본 인자 사용 | 호출 간 상태가 공유됩니다 | 기본값으로 `None`을 사용합니다 |
| 매번 전체 복사를 강제함 | 큰 데이터에서는 성능이 나빠집니다 | 필요한 부분만 복사하거나 구조적 공유를 고려합니다 |
| `object.__setattr__`로 frozen 객체를 억지 수정 | 계약이 깨지고 디버깅이 어려워집니다 | frozen의 의도를 존중합니다 |

## 실무에서 이렇게 쓰입니다

- 런타임 변경을 막아야 하는 설정 객체를 `frozen dataclass`로 정의합니다.
- Redux 스타일 상태 관리에서 불변 업데이트 패턴을 사용합니다.
- API 응답 모델을 `NamedTuple`이나 frozen dataclass로 표현합니다.
- 캐시 키로 `tuple`이나 `frozenset`을 사용합니다.
- 이벤트 소싱에서 이력 객체를 불변 값으로 관리합니다.

## 현업에서는 이렇게 판단합니다

"모든 것을 불변으로 만들어라"는 구호는 실무적으로 너무 거칠습니다. 더 정확한 기준은 "기본값은 불변으로 두고, 성능이나 편의 때문에 꼭 필요할 때만 mutable을 허용하라"입니다. Python에서는 `frozen=True`와 `NamedTuple`만으로도 상당히 많은 영역을 안정화할 수 있습니다.

다만 큰 데이터 구조를 매번 전부 복사하는 방식은 비효율적일 수 있습니다. 그래서 불변성은 문법이 아니라 설계 원칙으로 이해해야 합니다. 제너레이터, 구조적 공유, 얕은 복사 전략과 함께 써야 실무적으로 균형이 맞습니다.

## 체크리스트

- [ ] Python의 mutable 타입과 immutable 타입을 구분할 수 있다
- [ ] `tuple`과 `frozenset`의 용도를 설명할 수 있다
- [ ] `frozen dataclass`를 정의하고 `replace()`로 갱신할 수 있다
- [ ] 함수 인자를 직접 수정하지 않는 불변 패턴을 적용할 수 있다
- [ ] 불변 데이터의 장점과 비용을 함께 설명할 수 있다

## 연습 문제

1. mutable `dict` 기반 설정 관리 코드를 frozen dataclass 기반으로 바꿔 보세요.
2. undo 기능이 있는 간단한 텍스트 편집기를 불변 상태 패턴으로 설계해 보세요.
3. `NamedTuple`로 2차원 벡터를 정의하고 덧셈, 뺄셈, 스칼라 곱 함수를 작성해 보세요.

## 정리와 다음 글

불변 데이터는 예측 불가능한 상태 변경을 줄이고 코드 안정성을 높입니다. Python은 `tuple`, `frozenset`, `NamedTuple`, `frozen dataclass`를 통해 이를 충분히 실용적으로 지원합니다. 다음 글에서는 함수를 인자로 받고 반환하는 **고차 함수**를 다룹니다.

## 처음 질문으로 돌아가기

- **Python에서 mutable 타입과 immutable 타입은 어떻게 구분할까요?**
  - 본문의 기준은 immutable 데이터를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **`tuple`, `frozenset`, `NamedTuple`, `frozen dataclass`는 각각 언제 유용할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **함수 경계에서 원본 변경을 막으려면 어떤 패턴이 필요할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Functional Programming 101 (1/10): 함수형 프로그래밍이란 무엇인가?](./01-what-is-fp.md)
- [Functional Programming 101 (2/10): 순수 함수와 부수효과](./02-pure-functions.md)
- **immutable 데이터 (현재 글)**
- 고차 함수 (예정)
- map, filter, reduce (예정)
- 클로저와 partial (예정)
- 재귀와 꼬리 호출 (예정)
- 지연 평가와 제너레이터 (예정)
- 함수 합성과 파이프라인 (예정)
- 객체지향과 함수형의 균형 (예정)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Data Model (Immutable Types)](https://docs.python.org/3/reference/datamodel.html)
- [Real Python — Immutability in Python](https://realpython.com/python-mutable-vs-immutable-types/)
- [Fluent Python — Chapter 8: Object References, Mutability, and Recycling](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)
- [Python 공식 문서 — dataclasses (frozen)](https://docs.python.org/3/library/dataclasses.html)

Tags: Python, Functional Programming, 불변성, tuple, frozenset
