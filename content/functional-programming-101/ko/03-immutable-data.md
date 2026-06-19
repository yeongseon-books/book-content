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

상태 관련 버그를 줄이는 가장 강력한 방법 중 하나는 아예 기존 데이터를 바꾸지 않는 것입니다. 이미 생성한 값을 직접 수정하지 않고, 필요할 때마다 새 값을 만들어 쓰는 방식으로 사고를 전환하면 코드의 추적 가능성이 크게 좋아집니다.

이 글은 Functional Programming 101 시리즈의 3번째 글입니다.

Python은 기본적으로 mutable 객체를 많이 쓰는 언어이지만, 동시에 `tuple`, `frozenset`, `NamedTuple`, `frozen dataclass` 같은 좋은 불변 도구도 제공합니다. 중요한 것은 "무조건 복사하라"가 아니라, 바뀌지 않아야 하는 값을 명확하게 모델링하는 감각입니다.

![Functional Programming 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/functional-programming-101/03/03-01-big-picture.ko.png)
*Functional Programming 101 3장 흐름 개요*

## 이 글에서 다룰 문제

- Python에서 mutable 타입과 immutable 타입은 어떻게 구분할까요?
- `tuple`, `frozenset`, `NamedTuple`, `frozen dataclass`는 각각 언제 유용할까요?
- 함수 경계에서 원본 변경을 막으려면 어떤 패턴이 필요할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

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

## 적용 전후 비교

원본 리스트를 직접 수정하는 코드는 호출자에게 숨은 부작용을 만듭니다. 새 리스트를 반환하면 변경이 명시적이 됩니다.

```python
# 이전: 원본 리스트를 변경
def add_tag(tags: list[str], tag: str) -> list[str]:
    tags.append(tag)
    return tags

original = ["python", "fp"]
result = add_tag(original, "immutable")
print(original)  # ['python', 'fp', 'immutable'] — original changed!
```

```python
# 이후: 새 리스트 생성
def add_tag(tags: list[str], tag: str) -> list[str]:
    return [*tags, tag]

original = ["python", "fp"]
result = add_tag(original, "immutable")
print(original)  # ['python', 'fp'] — original preserved
print(result)    # ['python', 'fp', 'immutable']
```

## 단계별 실습

### 단계 1: Python 내장 불변 타입

```python
# tuple — 불변 시퀀스
point = (3, 4)
# point[0] = 5  # TypeError: 'tuple'은 item assignment를 지원하지 않음

# frozenset — 불변 집합
allowed = frozenset({"read", "write", "execute"})
# allowed.add("delete")  # AttributeError: 'frozenset'에는 'add' attribute가 없음

# str — 불변 문자열
name = "hello"
upper_name = name.upper()  # creates a new string
print(name)        # hello — original preserved
print(upper_name)  # HELLO

# tuple은 hashable하며 dict key로 사용할 수 있음
grid: dict[tuple[int, int], str] = {
    (0, 0): "start",
    (1, 2): "goal",
}
print(grid[(0, 0)])  # start
```

이 예제에서 중요한 점은 "바꿀 수 없다"는 제약이 오히려 설계를 명확하게 만든다는 사실입니다. 좌표, 권한 집합, 문자열 같은 값은 애초에 변경 가능한 상태로 둘 이유가 많지 않습니다.

### 단계 2: NamedTuple로 의미 있는 불변 레코드 만들기

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
# p.x = 5.0  # AttributeError — 불변 객체

# _replace로 수정된 복사본 생성
p2 = p._replace(x=5.0)
print(p)   # Point(x=3.0, y=4.0) — original preserved
print(p2)  # Point(x=5.0, y=4.0)

red = Color(255, 0, 0)
print(red)  # Color(r=255, g=0, b=0)

# map으로 포인트 컬렉션 변환
points = [Point(1.0, 2.0), Point(3.0, 4.0), Point(5.0, 6.0)]
scaled = list(map(lambda p: Point(p.x * 2, p.y * 2), points))
print(scaled)  # [Point(x=2.0, y=4.0), Point(x=6.0, y=8.0), Point(x=10.0, y=12.0)]
```

`NamedTuple`은 읽기 쉬운 필드 이름과 불변성을 동시에 제공합니다. 작은 값 객체를 표현할 때 매우 경제적인 선택입니다.

### 단계 3: frozen dataclass 사용하기

```python
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class User:
    name: str
    email: str
    role: str = "viewer"

user = User(name="Alice", email="alice@example.com")
# user.name = "Bob"  # FrozenInstanceError — 수정 불가

# 새 인스턴스 생성
admin = replace(user, role="admin")
print(user)   # User(name='Alice', email='alice@example.com', role='viewer')
print(admin)  # User(name='Alice', email='alice@example.com', role='admin')

# frozen dataclass는 hashable — dict key와 set element로 사용 가능
users = {user, admin}
print(len(users))  # 2

# filter로 역할 필터링
all_users = [user, admin, User("Bob", "bob@example.com", "viewer")]
admins = list(filter(lambda u: u.role == "admin", all_users))
print([u.name for u in admins])  # ['Alice']
```

`frozen dataclass`는 실무에서 특히 유용합니다. 설정 객체, DTO, 도메인 값 객체처럼 "의미 있는 레코드"를 안정적으로 표현할 수 있기 때문입니다.

### 단계 4: 불변 딕셔너리 패턴

```python
from types import MappingProxyType

# MappingProxyType — 읽기 전용 dictionary view
config = {"host": "localhost", "port": 8080, "debug": True}
readonly_config = MappingProxyType(config)

print(readonly_config["host"])  # localhost
# readonly_config["host"] = "0.0.0.0"  # TypeError — 수정 불가

# dictionary update — 새 dictionary 생성
def update_config(config: dict, **updates) -> dict:
    return {**config, **updates}

original = {"host": "localhost", "port": 8080}
updated = update_config(original, port=9090, debug=False)

print(original)  # {'host': 'localhost', 'port': 8080} — original preserved
print(updated)   # {'host': 'localhost', 'port': 9090, 'debug': False}

# 설정 체인: 각 단계가 새 dict를 반환
base_config = {"timeout": 30, "retries": 3, "debug": False}
dev_config = update_config(base_config, debug=True, timeout=5)
prod_config = update_config(base_config, retries=5)
print(dev_config)   # {'timeout': 5, 'retries': 3, 'debug': True}
print(prod_config)  # {'timeout': 30, 'retries': 5, 'debug': False}
```

딕셔너리는 편리하지만 무심코 수정하기 쉽습니다. 그래서 설정처럼 안정성이 필요한 데이터는 읽기 전용 뷰나 새 딕셔너리 반환 패턴을 습관적으로 쓰는 편이 안전합니다.

### 단계 5: 불변 데이터로 상태 이력 관리하기

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

# 상태 이력 — 모든 변경이 추적됨
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

# map으로 이력에서 원하는 정보 추출
counts = list(map(lambda s: s.count, history))
print(counts)  # [0, 1, 2, 2]
```

불변 데이터가 강력한 이유가 여기서 드러납니다. 현재 상태만 있는 것이 아니라, 상태 변화의 이력이 그대로 남습니다. undo/redo나 이벤트 소싱과 잘 맞는 이유도 이 때문입니다.

### 단계 6: 불변 데이터와 함수형 변환 조합하기

```python
from dataclasses import dataclass, replace
from functools import reduce

@dataclass(frozen=True)
class Product:
    id: str
    name: str
    price: int
    stock: int

products = [
    Product("P1", "Coffee", 4500, 100),
    Product("P2", "Tea", 3000, 50),
    Product("P3", "Juice", 5500, 0),
    Product("P4", "Water", 1000, 200),
]

# filter: 재고 있는 상품만
in_stock = list(filter(lambda p: p.stock > 0, products))

# map: 10% 할인 적용 (새 Product 객체 생성)
discounted = list(map(lambda p: replace(p, price=int(p.price * 0.9)), in_stock))

# reduce: 총 재고 가치 계산
total_value = reduce(lambda acc, p: acc + p.price * p.stock, discounted, 0)

print([p.name for p in discounted])    # ['Coffee', 'Tea', 'Water']
print(f"할인 가격: {[p.price for p in discounted]}")  # [4050, 2700, 900]
print(f"총 재고 가치: {total_value:,}")  # 총 재고 가치: 585,000
```

### 단계 7: `MappingProxyType`으로 dict를 읽기 전용으로 만들기

```python
from types import MappingProxyType

# 설정 딕셔너리를 읽기 전용으로 노출
_config = {
    "host": "localhost",
    "port": 5432,
    "db": "myapp",
}

# MappingProxyType은 dict를 래핑해 수정을 막음
CONFIG = MappingProxyType(_config)

print(CONFIG["host"])  # 'localhost' — 읽기는 가능

try:
    CONFIG["host"] = "production-db"  # TypeError 발생
except TypeError as e:
    print(f"수정 불가: {e}")

# 업데이트가 필요하면 원본 dict를 갱신하고 다시 래핑
def update_config(base: dict, overrides: dict) -> MappingProxyType:
    return MappingProxyType({**base, **overrides})

dev_config = update_config(_config, {"host": "dev-db", "port": 5433})
print(dev_config["host"])  # 'dev-db'
print(dev_config["db"])    # 'myapp' — 원본 값 유지
```

`MappingProxyType`은 `frozen dataclass`나 `NamedTuple`이 어울리지 않는 dict 형태의 설정 객체를 읽기 전용으로 노출할 때 유용합니다. 외부에 노출하는 API 설정, 플러그인 시스템 기본값, 환경별 상수 맵에 자주 쓰입니다.

## 이 코드에서 주목할 점

- Python의 `tuple`, `frozenset`, `str`은 대표적인 내장 불변 타입입니다.
- `NamedTuple._replace()`와 `dataclasses.replace()`는 불변 업데이트의 핵심 패턴입니다.
- `frozen dataclass`는 hashable해서 dict 키나 set 원소로 활용할 수 있습니다.
- 불변 데이터는 `map`/`filter` 파이프라인과 자연스럽게 결합됩니다.
- `MappingProxyType`은 dict를 읽기 전용으로 감싸 설정 객체 노출에 적합합니다.

## 자주 하는 실수

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

"모든 것을 불변으로 만들어라"는 구호는 실무적으로 너무 거칩니다. 더 정확한 기준은 "기본값은 불변으로 두고, 성능이나 편의 때문에 꼭 필요할 때만 mutable을 허용하라"입니다. Python에서는 `frozen=True`와 `NamedTuple`만으로도 상당히 많은 영역을 안정화할 수 있습니다.

다만 큰 데이터 구조를 매번 전부 복사하는 방식은 비효율적일 수 있습니다. 그래서 불변성은 문법이 아니라 설계 원칙으로 이해해야 합니다. 제너레이터, 구조적 공유, 얕은 복사 전략과 함께 써야 실무적으로 균형이 맞습니다.

## 처음 질문으로 돌아가기

- **Python에서 mutable 타입과 immutable 타입은 어떻게 구분할까요?**
  생성 후 내부 값을 바꿀 수 있으면 mutable(`list`, `dict`, `set`), 바꿀 수 없으면 immutable(`int`, `str`, `tuple`, `frozenset`)입니다. `id()` 함수로 확인할 수 있습니다. 문자열에 `upper()`를 호출하면 원본이 아닌 새 객체가 반환됩니다.

- **`tuple`, `frozenset`, `NamedTuple`, `frozen dataclass`는 각각 언제 유용할까요?**
  순서가 있는 불변 값 묶음은 `tuple`, 중복 없는 불변 집합은 `frozenset`, 필드 이름이 있는 가벼운 값 객체는 `NamedTuple`, 검증 로직이나 메서드가 필요한 구조화된 값 객체는 `frozen dataclass`가 적합합니다.

- **함수 경계에서 원본 변경을 막으려면 어떤 패턴이 필요할까요?**
  리스트는 `[*original, new_item]`으로, 딕셔너리는 `{**original, key: value}`로 새 객체를 반환합니다. dataclass는 `replace(obj, field=new_value)`를 씁니다. 원칙은 하나입니다. 받은 객체를 직접 수정하지 말고 새 객체를 만들어 반환합니다.

## 운영 체크리스트

- [ ] Python의 mutable 타입과 immutable 타입을 구분할 수 있다
- [ ] `tuple`과 `frozenset`의 용도를 설명할 수 있다
- [ ] `frozen dataclass`를 정의하고 `replace()`로 갱신할 수 있다
- [ ] 함수 인자를 직접 수정하지 않는 불변 패턴을 적용할 수 있다
- [ ] 불변 데이터의 장점과 비용을 함께 설명할 수 있다

## 연습 문제

1. mutable `dict` 기반 설정 관리 코드를 frozen dataclass 기반으로 바꿔 보세요.
2. undo 기능이 있는 간단한 텍스트 편집기를 불변 상태 패턴으로 설계해 보세요.
3. `NamedTuple`로 2차원 벡터를 정의하고 `map`으로 벡터 목록에 스케일 변환을 적용해 보세요.

## 정리와 다음 글

불변 데이터는 예측 불가능한 상태 변경을 줄이고 코드 안정성을 높입니다. Python은 `tuple`, `frozenset`, `NamedTuple`, `frozen dataclass`를 통해 이를 충분히 실용적으로 지원합니다. 다음 글에서는 함수를 인자로 받고 반환하는 **고차 함수**를 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [Functional Programming 101 (1/10): 함수형 프로그래밍이란 무엇인가?](./01-what-is-fp.md)
- [Functional Programming 101 (2/10): 순수 함수와 부수효과](./02-pure-functions.md)
- **Functional Programming 101 (3/10): immutable 데이터 (현재 글)**
- [Functional Programming 101 (4/10): 고차 함수](./04-higher-order-functions.md)
- [Functional Programming 101 (5/10): map, filter, reduce](./05-map-filter-reduce.md)
- [Functional Programming 101 (6/10): 클로저와 partial](./06-closure-and-partial.md)
- [Functional Programming 101 (7/10): 재귀와 꼬리 호출](./07-recursion.md)
- [Functional Programming 101 (8/10): 지연 평가와 제너레이터](./08-lazy-evaluation.md)
- [Functional Programming 101 (9/10): 함수 합성과 파이프라인](./09-function-composition.md)
- [객체지향과 함수형의 균형](./10-oop-and-fp-balance.md)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Data Model (Immutable Types)](https://docs.python.org/3/reference/datamodel.html)
- [Real Python — Immutability in Python](https://realpython.com/python-mutable-vs-immutable-types/)
- [Fluent Python — Chapter 8: Object References, Mutability, and Recycling](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)
- [Python 공식 문서 — dataclasses (frozen)](https://docs.python.org/3/library/dataclasses.html)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/functional-programming-101/ko)
Tags: Python, Functional Programming, 불변성, tuple, frozenset
