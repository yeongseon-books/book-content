---
series: data-structures-python-101
episode: 1
title: "Data Structures with Python 101 (1/10): 자료구조란 무엇인가?"
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
  - 자료구조
  - Data Structures
  - 알고리즘
  - 프로그래밍 기초
seo_description: 자료구조가 왜 중요한지와 Python 내장 구조의 선택 기준을 설명합니다.
last_reviewed: '2026-05-12'
---

# Data Structures with Python 101 (1/10): 자료구조란 무엇인가?

이 글은 Data Structures with Python 101 시리즈의 첫 번째 글입니다.


![Data Structures with Python 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-python-101/01/01-01-big-picture.ko.png)
*Data Structures with Python 101 1장 흐름 개요*

## 먼저 던지는 질문

- 자료구조는 정확히 무엇이고 왜 따로 배워야 할까요?
- 같은 데이터를 저장해도 자료구조에 따라 성능이 왜 크게 달라질까요?
- Python이 기본으로 제공하는 list, dict, set, tuple은 각각 어떤 역할에 맞을까요?

## 왜 이 글이 중요한가

프로그램은 데이터를 입력받고, 처리하고, 다시 출력합니다. 이때 데이터를 어떤 구조로 저장하느냐에 따라 같은 기능도 밀리초 안에 끝날 수 있고, 불필요하게 오래 걸릴 수도 있습니다. 자료구조는 그 차이를 만드는 가장 기본적인 레버입니다.

> 자료구조는 데이터를 효율적으로 저장하고 접근하고 수정하기 위한 조직화 방식입니다. 올바른 자료구조를 고르면 코드가 더 단순해지고, 성능도 더 안정적으로 나옵니다.

자료구조가 코딩 면접의 단골 주제인 이유도 여기에 있습니다. 단순히 문제 풀이 기술을 묻는 것이 아니라, 데이터를 어떻게 모델링하고 연산 비용을 어떻게 판단하는지를 보기 때문입니다. 현업에서도 상황은 같습니다. 성능 문제는 종종 복잡한 알고리즘보다, 잘못 고른 자료구조 하나에서 시작합니다.

## 핵심 개념 한눈에 보기

> 자료구조 = 데이터를 효율적으로 접근·수정할 수 있도록 정리하는 방식

```text
[single variable]    →  stores 1 value
[list]               →  stores N values in order
[dict]               →  stores N key-value pairs (O(1) lookup)
[tree]               →  represents hierarchies (O(log n) search)
[graph]              →  represents networks of relationships
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 자료구조 | 데이터를 어떻게 저장하고 꺼낼지를 정하는 구조로, 삽입·삭제·검색 비용을 좌우합니다 |
| 시간 복잡도 | 데이터 크기가 커질 때 연산 시간이 어떻게 증가하는지 설명하는 개념입니다 |
| 공간 복잡도 | 자료구조가 데이터를 저장하기 위해 얼마나 많은 메모리를 쓰는지 설명합니다 |
| 추상 자료형(ADT) | 구현 세부사항을 숨기고 "어떤 연산이 가능한가"만 정의하는 개념입니다 |
| 내장 자료구조 | Python이 기본으로 제공하는 list, dict, set, tuple 같은 구조입니다 |

## 적용 전후 비교
자료구조를 모르고 코드를 쓰는 경우와, 연산 특성을 고려해 구조를 고른 경우를 비교해 보겠습니다.

```python
# before: list에서 탐색 — O(n)
users = ["alice", "bob", "charlie", "diana"]
if "charlie" in users:
    print("found")
```

```python
# after: set에서 탐색 — O(1)
users = {"alice", "bob", "charlie", "diana"}
if "charlie" in users:
    print("found")
```

list는 순서 보존에는 좋지만 검색은 선형으로 진행됩니다. 반면 set은 순서를 포기하는 대신 membership test를 매우 빠르게 수행합니다. 자료구조를 배운다는 것은 이런 교환관계를 이해하는 일입니다.

## 단계별 실습

### 단계 1: list와 set의 검색 속도 비교

```python
import time

data_list = list(range(1_000_000))
data_set = set(range(1_000_000))

target = 999_999

start = time.perf_counter()
_ = target in data_list
list_time = time.perf_counter() - start

start = time.perf_counter()
_ = target in data_set
set_time = time.perf_counter() - start

print(f"list search: {list_time:.6f}s")
print(f"set  search: {set_time:.6f}s")
print(f"set is {list_time / set_time:.0f}x faster")
```

### 단계 2: dict의 O(1) 키-값 조회 확인

```python
scores: dict[str, int] = {"alice": 95, "bob": 82, "charlie": 90}
print(scores["bob"])          # 82 — O(1) access
print(scores.get("diana", 0)) # 0 — default when key is missing
```

### 단계 3: tuple로 불변 데이터 표현

```python
point: tuple[int, int] = (3, 4)
# point[0] = 5  # TypeError — tuple은 immutable
print(f"x={point[0]}, y={point[1]}")
```

### 단계 4: list를 스택으로 사용

```python
stack: list[str] = []
stack.append("a")
stack.append("b")
stack.append("c")
print(stack.pop())  # "c" — last in, first out
print(stack.pop())  # "b"
```

### 단계 5: collections 모듈 탐색

```python
from collections import deque, Counter, defaultdict

# deque: 양 끝 삽입/삭제 O(1)
dq: deque[int] = deque([1, 2, 3])
dq.appendleft(0)
print(list(dq))  # [0, 1, 2, 3]

# Counter: 빈도 계산
counter = Counter("abracadabra")
print(counter.most_common(3))  # [('a', 5), ('b', 2), ('r', 2)]

# defaultdict: 기본값이 있는 dict
dd: defaultdict[str, list[str]] = defaultdict(list)
dd["fruits"].append("apple")
print(dd)  # defaultdict(<class 'list'>, {'fruits': ['apple']})
```

## 이 코드에서 먼저 봐야 할 점

- list의 `in` 연산은 O(n)이지만 set의 `in` 연산은 O(1)입니다.
- dict는 키 기반 조회를 O(1)에 제공하므로 검색이 많은 코드에서 기본 선택지가 됩니다.
- tuple은 불변이라 dict의 키나 set의 원소처럼 해시 가능한 위치에 넣을 수 있습니다.
- `collections` 모듈은 "기본 자료구조로는 살짝 불편한 패턴"을 보완해 주는 특화 구조를 제공합니다.

핵심은 Python이 쓸 만한 자료구조를 이미 풍부하게 제공한다는 점입니다. 새 구조를 직접 만들 일은 드뭅니다. 대신 각 구조의 연산 특성을 이해하고 상황에 맞게 고르는 판단이 더 중요합니다.

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 모든 곳에 list 사용 | 검색이 O(n)이라 데이터가 커질수록 느려집니다 | 조회가 많으면 set이나 dict를 우선 검토합니다 |
| list를 dict 키로 사용 | list는 가변 객체라 해시할 수 없습니다 | tuple로 변환한 뒤 키로 사용합니다 |
| 자료구조 크기를 무시 | 메모리 사용량이 급격히 커질 수 있습니다 | 데이터 규모와 생명주기를 함께 봅니다 |
| set에 순서를 기대 | set은 순서를 보장하지 않습니다 | 순서가 중요하면 list나 다른 구조를 사용합니다 |
| 시간 복잡도 확인 없이 구현 | 작은 데이터에서는 지나가도 규모가 커지면 병목이 됩니다 | 구조를 고르기 전에 주요 연산의 비용을 먼저 확인합니다 |

## 실무에서 이렇게 쓰입니다

- 캐시 시스템은 O(1) 조회를 위해 dict를 사용합니다.
- 중복 제거 파이프라인은 set으로 고유값만 유지합니다.
- 작업 큐는 deque로 FIFO 처리를 구현합니다.
- 좌표나 설정 키처럼 바뀌면 안 되는 값은 tuple로 고정합니다.
- 로그 분석과 빈도 집계는 Counter로 간결하게 처리합니다.

## 실무에서는 이렇게 생각합니다

경험 있는 개발자는 코드를 쓰기 전에 "이 데이터를 어디에 담을까?"보다 "이 데이터를 가장 자주 어떻게 다룰까?"를 먼저 묻습니다. 검색이 많은지, 순서가 중요한지, 중복 허용 여부가 핵심인지에 따라 출발점이 달라지기 때문입니다.

실무에서는 Python 내장 자료구조만으로도 대부분의 문제를 충분히 해결할 수 있습니다. 결국 중요한 것은 list, dict, set, tuple의 차이를 정확히 알고, 그 차이가 성능과 가독성에 어떤 영향을 주는지 설명할 수 있는가입니다.
## 추상 자료형(ADT)과 구체 구현의 구분

핵심 개념 표에서 추상 자료형(ADT)을 잠깐 언급했습니다. 이 개념을 좀 더 깊이 들여다보겠습니다. ADT는 "무엇을 할 수 있는가"만 정의하고, "어떻게 하는가"는 숨깁니다. 예를 들어 Stack ADT는 다음 세 가지 연산만 약속합니다.

| 연산 | 설명 |
|------|------|
| push(item) | 맨 위에 원소를 추가합니다 |
| pop() | 맨 위 원소를 꺼내고 반환합니다 |
| peek() | 맨 위 원소를 꺼내지 않고 확인합니다 |

이 약속을 지키기만 하면 내부를 list로 구현하든, 연결 리스트로 구현하든 사용하는 쪽 코드는 바뀌지 않습니다. Python의 `list`는 Stack ADT를 직접 구현한 것은 아니지만, `append`와 `pop`이 LIFO 동작을 제공하므로 Stack처럼 사용할 수 있습니다.

ADT를 먼저 정의하고 구현을 나중에 고르는 습관은 두 가지 이점을 줍니다. 첫째, 코드의 의도가 명확해집니다. "여기서는 LIFO 접근만 한다"는 계약이 코드에 드러나므로, 실수로 중간 원소에 접근하는 버그를 방지합니다. 둘째, 나중에 구현을 교체할 수 있습니다. 처음에는 list로 충분하다가 스레드 안전이 필요해지면 `queue.LifoQueue`로 바꾸면 됩니다. ADT 계약이 동일하므로 호출 코드를 수정할 필요가 없습니다.

이 시리즈 전체에서 각 글은 하나의 ADT를 다루고, Python에서 그 ADT를 구현하는 구체 방법을 보여줍니다. 2장의 배열/리스트는 Sequence ADT, 3장의 스택/큐는 Stack과 Queue ADT, 4장의 해시 테이블은 Map ADT에 대응합니다. ADT를 먼저 이해한 뒤 구현을 보면, 왜 특정 구현이 특정 연산에 유리한지를 구조적으로 파악할 수 있습니다.

### ADT와 Python 프로토콜의 대응

Python 3.8 이후의 `typing.Protocol`은 ADT 개념을 코드로 표현하는 도구입니다. Protocol은 구조적 서브타이핑(structural subtyping)을 지원하므로, 명시적 상속 없이도 "이 메서드가 있으면 이 타입으로 취급한다"는 계약을 강제할 수 있습니다.

```python
from typing import Protocol, TypeVar

T = TypeVar("T")


class StackADT(Protocol[T]):
    """Stack 추상 자료형의 프로토콜 정의입니다."""

    def push(self, item: T) -> None: ...
    def pop(self) -> T: ...
    def peek(self) -> T: ...
    def __len__(self) -> int: ...


class ListStack:
    """list 기반 Stack 구현입니다."""

    def __init__(self) -> None:
        self._data: list[object] = []

    def push(self, item: object) -> None:
        self._data.append(item)

    def pop(self) -> object:
        if not self._data:
            raise IndexError("pop from empty stack")
        return self._data.pop()

    def peek(self) -> object:
        if not self._data:
            raise IndexError("peek from empty stack")
        return self._data[-1]

    def __len__(self) -> int:
        return len(self._data)
```

`ListStack`은 `StackADT`를 상속하지 않지만, 동일한 메서드 시그니처를 갖고 있으므로 `isinstance(ListStack(), StackADT)`는 `True`를 반환합니다(`@runtime_checkable` 적용 시). 이 패턴은 Java의 인터페이스와 비슷하지만, 명시적 `implements` 선언 없이도 동작한다는 점에서 더 유연합니다.

ADT 사고방식은 이 시리즈 전체의 골격입니다. 각 글에서 새로운 자료구조를 만날 때마다 "이 구조는 어떤 ADT를 구현하는가? 어떤 연산을 O(1)로 보장하는가?"를 먼저 확인하는 습관을 들이면, 단순 암기가 아니라 체계적 이해로 이어집니다.


## 타입 힌트 기반 자료구조 인터페이스 설계

Python에서 자료구조를 학습할 때는 동작만 확인하고 끝내면 안 됩니다. 타입 힌트와 `Protocol`을 활용하면 자료구조가 어떤 연산 계약을 제공하는지 코드 수준에서 드러낼 수 있습니다. 이 시리즈 전체에 걸쳐 반복되는 패턴이므로 첫 글에서 기본 뼈대를 먼저 잡겠습니다.

```python
from __future__ import annotations

from typing import Generic, Iterator, Protocol, TypeVar, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class Container(Protocol[T]):
    """자료구조가 공통으로 지원할 수 있는 최소 인터페이스입니다."""

    def __len__(self) -> int: ...
    def __contains__(self, item: object) -> bool: ...
    def __iter__(self) -> Iterator[T]: ...


class SearchableCollection(Generic[T]):
    """list, set, dict를 감싸서 동일한 인터페이스로 비교하는 예시 구현입니다."""

    def __init__(self) -> None:
        self._data: list[T] = []
        self._index: set[T] = set()

    def add(self, item: T) -> None:
        if item not in self._index:
            self._data.append(item)
            self._index.add(item)

    def __contains__(self, item: object) -> bool:
        return item in self._index  # O(1) lookup via set

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[T]:
        return iter(self._data)

    def __repr__(self) -> str:
        return f"SearchableCollection({self._data!r})"
```

이 설계에서 핵심은 세 가지입니다.

1. **`Protocol`로 계약을 선언합니다.** 구체 클래스가 무엇이든 `__len__`, `__contains__`, `__iter__`만 갖추면 동일한 인터페이스로 다룰 수 있습니다.
2. **복합 구조로 장점을 조합합니다.** `list`로 순서를 유지하면서 `set`으로 O(1) 조회를 보장합니다. 이것은 10장에서 다시 다루는 복합 자료구조 패턴의 출발점입니다.
3. **타입 변수 `T`로 재사용성을 높입니다.** `SearchableCollection[str]`, `SearchableCollection[int]`처럼 어떤 원소 타입이든 안전하게 사용할 수 있습니다.

## 메모리 프로파일링: 구조별 비용 비교

자료구조를 선택할 때 시간 복잡도만 보면 절반만 본 것입니다. 메모리 사용량도 함께 확인해야 합니다. Python의 `sys.getsizeof()`는 객체 자체의 크기만 보여 주므로, 컨테이너 안에 들어 있는 원소까지 포함한 실제 비용을 측정하려면 재귀적으로 합산해야 합니다.

```python
import sys
from collections import deque


def deep_getsizeof(obj: object, seen: set[int] | None = None) -> int:
    """객체와 그 내용물의 전체 메모리 사용량을 재귀적으로 측정합니다."""
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)
    size = sys.getsizeof(obj)
    if isinstance(obj, dict):
        size += sum(deep_getsizeof(k, seen) + deep_getsizeof(v, seen) for k, v in obj.items())
    elif isinstance(obj, (list, tuple, set, frozenset, deque)):
        size += sum(deep_getsizeof(item, seen) for item in obj)
    return size


# 10만 개 정수를 각 구조에 넣고 메모리 비교
n = 100_000
data_list = list(range(n))
data_set = set(range(n))
data_dict = {i: i for i in range(n)}
data_tuple = tuple(range(n))

print(f"list : {deep_getsizeof(data_list):>12,} bytes")
print(f"set  : {deep_getsizeof(data_set):>12,} bytes")
print(f"dict : {deep_getsizeof(data_dict):>12,} bytes")
print(f"tuple: {deep_getsizeof(data_tuple):>12,} bytes")
```

64비트 CPython 3.12 기준 예시 출력입니다.

```text
list :    4,348,040 bytes
set  :    4,194,528 bytes
dict :    7,331,432 bytes
tuple:    4,248,024 bytes
```

이 결과에서 읽을 수 있는 것은 다음과 같습니다.

- **dict는 키와 값을 모두 저장**하므로 메모리가 가장 큽니다. O(1) 조회의 대가입니다.
- **set은 키만 저장**하므로 dict보다 작지만, 해시 테이블 오버헤드 때문에 list보다는 약간 큽니다.
- **tuple은 list보다 약간 작습니다.** 불변이라 over-allocation이 필요 없기 때문입니다.

메모리가 중요한 환경(임베디드, 대규모 배치)에서는 이 차이가 설계 결정에 직접 영향을 줍니다. 예를 들어 조회 빈도가 낮으면 dict 대신 정렬된 list + `bisect`로 메모리를 절약할 수 있습니다.

## 성능 벤치마크: timeit으로 정밀 비교

단일 `time.perf_counter()` 호출보다 `timeit`을 사용하면 GC 영향과 운영체제 스케줄링 노이즈를 줄여 더 정확한 비교가 가능합니다.

```python
import timeit


def benchmark_membership(structure_name: str, setup: str, stmt: str, number: int = 1000) -> float:
    """주어진 구조에서 membership test를 number회 반복해 평균 시간을 반환합니다."""
    elapsed = timeit.timeit(stmt, setup=setup, number=number)
    avg_us = (elapsed / number) * 1_000_000  # microseconds
    print(f"{structure_name:12s}: {avg_us:>8.2f} µs/op")
    return avg_us


n = 1_000_000
target = n - 1  # worst case for list

benchmark_membership(
    "list",
    f"data = list(range({n}))",
    f"{target} in data",
    number=100,
)
benchmark_membership(
    "set",
    f"data = set(range({n}))",
    f"{target} in data",
    number=100_000,
)
benchmark_membership(
    "dict",
    f"data = {{i: None for i in range({n})}}",
    f"{target} in data",
    number=100_000,
)
```

이 벤치마크가 보여 주는 것은 Big-O 표기가 실제 코드에서 어떤 크기의 차이로 나타나는가입니다. list의 O(n) 검색은 원소 100만 개 기준으로 수 밀리초가 걸리지만, set과 dict의 O(1) 검색은 마이크로초 단위입니다. 데이터가 작을 때는 차이가 보이지 않지만, 규모가 커지는 순간 이 격차는 사용자 체감 지연으로 직결됩니다.

## unittest로 자료구조 동작 검증

자료구조를 직접 구현하거나 감싸서 사용할 때는 경계 조건을 반드시 테스트해야 합니다. 빈 입력, 단일 원소, 중복 입력, 최대 크기 입력이 대표적인 경계입니다.

```python
import unittest


class TestSearchableCollection(unittest.TestCase):
    def test_add_and_contains(self) -> None:
        sc: SearchableCollection[str] = SearchableCollection()
        sc.add("hello")
        self.assertIn("hello", sc)
        self.assertNotIn("world", sc)

    def test_dedup(self) -> None:
        sc: SearchableCollection[int] = SearchableCollection()
        for _ in range(100):
            sc.add(42)
        self.assertEqual(len(sc), 1)

    def test_order_preserved(self) -> None:
        sc: SearchableCollection[int] = SearchableCollection()
        for x in [3, 1, 4, 1, 5]:
            sc.add(x)
        self.assertEqual(list(sc), [3, 1, 4, 5])

    def test_empty_collection(self) -> None:
        sc: SearchableCollection[str] = SearchableCollection()
        self.assertEqual(len(sc), 0)
        self.assertNotIn("anything", sc)
        self.assertEqual(list(sc), [])


if __name__ == "__main__":
    unittest.main()
```

이 테스트가 검증하는 것은 네 가지입니다.

1. **기본 동작**: 추가한 원소를 찾을 수 있고, 추가하지 않은 원소는 찾을 수 없습니다.
2. **중복 방어**: 같은 값을 여러 번 넣어도 내부에는 한 번만 저장됩니다.
3. **순서 보존**: 삽입 순서가 유지됩니다.
4. **빈 상태**: 아무것도 없을 때 오류 없이 동작합니다.

실무에서는 이 네 경계를 모든 컬렉션 클래스에 적용하는 것이 좋습니다. pytest를 사용한다면 `@pytest.mark.parametrize`로 입력 크기를 0, 1, 100, 10만처럼 나눠 확인하면 규모별 동작도 함께 검증할 수 있습니다.

## Big-O 비교표: Python 내장 자료구조

아래 표는 이 시리즈 전체에서 반복적으로 참조할 기준표입니다. 각 구조의 주요 연산 비용을 한눈에 비교할 수 있습니다.

| 연산 | list | dict | set | deque | tuple |
|------|------|------|-----|-------|-------|
| 인덱스 접근 | O(1) | - | - | O(n) | O(1) |
| 검색 (`in`) | O(n) | O(1) | O(1) | O(n) | O(n) |
| 끝 추가 | O(1)* | O(1)* | O(1)* | O(1) | - |
| 앞 추가 | O(n) | - | - | O(1) | - |
| 중간 삽입 | O(n) | - | - | O(n) | - |
| 끝 삭제 | O(1) | - | - | O(1) | - |
| 임의 삭제 | O(n) | O(1)* | O(1)* | O(n) | - |
| 정렬 | O(n log n) | - | - | - | - |

\* amortized

이 표를 읽을 때 기억할 점은 두 가지입니다. 첫째, O(1)이라고 모두 같은 속도가 아닙니다. dict의 O(1) 조회는 해시 계산과 probe를 거치므로, list의 O(1) 인덱스 접근보다 상수 비용이 큽니다. 둘째, amortized O(1)은 가끔 비싼 연산(재할당)이 끼지만 평균적으로 O(1)이라는 뜻입니다.

## 체크리스트

- [ ] 자료구조의 정의와 역할을 설명할 수 있다
- [ ] list, dict, set, tuple의 차이를 설명할 수 있다
- [ ] set이 list보다 조회에 유리한 이유를 설명할 수 있다
- [ ] collections 모듈의 deque, Counter, defaultdict를 사용할 수 있다
- [ ] 시간 복잡도 개념을 자료구조 선택에 연결해 설명할 수 있다

## 연습 문제

1. 정수 100만 개가 들어 있는 list와 set에서 같은 값을 찾는 코드를 작성하고 실행 시간을 비교해 보세요.
2. 문자열 list에서 원래 순서를 유지한 채 중복만 제거하는 함수를 작성해 보세요. 힌트: `dict.fromkeys()`를 활용할 수 있습니다.
3. 학생 이름과 점수를 dict에 저장한 뒤, 점수 기준 내림차순으로 출력하는 코드를 작성해 보세요.
4. `SearchableCollection` 클래스에 `remove(item)` 메서드를 추가하고, 삭제 후에도 순서가 유지되는지 테스트를 작성해 보세요.
5. `deep_getsizeof` 함수를 사용해 deque와 list의 메모리 사용량을 원소 수 1천, 1만, 10만 단위로 비교하고 결과를 표로 정리해 보세요.

## 정리 및 다음 글 안내

자료구조는 데이터를 효율적으로 저장하고 접근하기 위한 기본 설계 도구입니다. Python은 list, dict, set, tuple처럼 강력한 내장 구조를 이미 갖추고 있고, 개발자는 각 구조의 특성을 이해한 뒤 상황에 맞게 선택하면 됩니다. 다음 글에서는 이 시리즈의 출발점이 되는 배열과 리스트를 더 깊이 들여다보겠습니다.

## 처음 질문으로 돌아가기

- **자료구조는 정확히 무엇이고 왜 따로 배워야 할까요?**
  - 자료구조는 데이터의 저장 방식과 접근 비용을 결정하는 조직화 방식입니다. 같은 기능을 구현해도 구조 선택에 따라 O(n)과 O(1)의 차이가 생기기 때문에, 프로그래밍 언어 문법과 별도로 학습해야 합니다.
- **같은 데이터를 저장해도 자료구조에 따라 성능이 왜 크게 달라질까요?**
  - list는 원소를 순서대로 나열하므로 검색 시 처음부터 끝까지 확인해야 합니다(O(n)). set은 해시 테이블로 구현되어 위치를 바로 계산하므로 O(1)에 검색합니다. 저장 방식 자체가 연산 비용을 결정하기 때문입니다.
- **Python이 기본으로 제공하는 list, dict, set, tuple은 각각 어떤 역할에 맞을까요?**
  - list는 순서가 중요한 순차 데이터, dict는 키-값 매핑과 빠른 조회, set은 중복 제거와 membership test, tuple은 불변 좌표나 복합 키에 적합합니다. 핵심은 "가장 자주 하는 연산이 무엇인가"를 기준으로 고르는 것입니다.

<!-- toc:begin -->
## 시리즈 목차

- **자료구조란 무엇인가? (현재 글)**
- 배열과 리스트 (예정)
- 스택과 큐 (예정)
- 해시 테이블과 dict (예정)
- 연결 리스트 (예정)
- 트리와 이진 트리 (예정)
- 힙과 우선순위 큐 (예정)
- 그래프 표현 (예정)
- set과 집합 연산 (예정)
- 자료구조 선택 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Data Structures](https://docs.python.org/3/tutorial/datastructures.html)
- [Problem Solving with Algorithms and Data Structures using Python](https://runestone.academy/ns/books/published/pythonds3/index.html)
- [Real Python — Common Python Data Structures](https://realpython.com/python-data-structures/)
- [Big-O Cheat Sheet](https://www.bigocheatsheet.com/)
- [book-examples 저장소 — data-structures-python-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/data-structures-python-101/ko)

Tags: Python, 자료구조, Data Structures, 알고리즘, 프로그래밍 기초
