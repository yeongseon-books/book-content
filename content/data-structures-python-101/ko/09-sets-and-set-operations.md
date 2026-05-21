---
series: data-structures-python-101
episode: 9
title: "Data Structures with Python 101 (9/10): set과 집합 연산"
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
  - set
  - 집합 연산
  - frozenset
seo_description: 파이썬 set의 해시 원리를 이해하고 중복 제거, 집합 연산, 권한 필터링 등 실무 패턴과 불변 객체인 frozenset 활용법을 익힙니다.
last_reviewed: '2026-05-17'
---

# Data Structures with Python 101 (9/10): set과 집합 연산

이 글은 Data Structures with Python 101 시리즈의 아홉 번째 글입니다.


![Data Structures with Python 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-python-101/09/09-01-set.ko.png)
*Data Structures with Python 101 9장 흐름 개요*

## 먼저 던지는 질문

- `set`은 왜 중복 제거와 membership test에 강할까요?
- 충돌과 hashability는 set에서 어떤 의미를 가질까요?
- 왜 `frozenset`은 set 원소나 dict 키가 될 수 있고 plain `set`은 안 될까요?

## 왜 이 글이 중요한가

중복 제거, 존재 여부 확인, 컬렉션 비교는 권한 관리, 태그 시스템, 데이터 정제, 처리 완료 추적처럼 실무의 거의 모든 영역에 등장합니다. list로도 구현할 수 있지만, 데이터가 커질수록 비용 차이가 급격히 벌어집니다.

> `set`은 값을 저장하지 않는 dict와 같은 해시 테이블 계열 구조입니다.

그래서 set을 배울 때는 `|`, `&` 같은 문법만 익히는 것으로 끝나면 안 됩니다. hashability, collision, uniqueness가 어떻게 맞물리는지까지 이해해야 실전에서 제대로 사용할 수 있습니다.

## 핵심 개념 한눈에 보기

> `set` = 중복 없는 키만 저장하는 해시 테이블 기반 컬렉션

```text
A = {1, 2, 3, 4}      B = {3, 4, 5, 6}

union        A | B  = {1, 2, 3, 4, 5, 6}
intersection A & B  = {3, 4}
difference   A - B  = {1, 2}
sym. diff.   A ^ B  = {1, 2, 5, 6}
```

## set 저장 모델을 그림으로 보면

## 핵심 개념

| 용어 | 설명 |
|------|------|
| set | 중복 없는 키만 저장하는 해시 기반 컬렉션입니다 |
| hashability | 원소가 안정적인 해시와 equality 의미를 가져야 한다는 조건입니다 |
| collision | 서로 다른 값이 같은 lookup/probe path를 공유하는 상황입니다 |
| `frozenset` | 자기 자신도 해시 가능한 불변 set입니다 |
| 집합 연산 | 합집합, 교집합, 차집합, 대칭차집합처럼 membership 기반으로 계산하는 연산입니다 |

## Before / After

list 기반 중복 제거와 set 기반 중복 제거를 비교해 보겠습니다.

```python
# before: list로 중복 제거 — O(n^2)
values = [1, 2, 3, 4, 2, 3]
unique = []
for value in values:
    if value not in unique:
        unique.append(value)
```

```python
# after: set으로 중복 제거 — 평균 O(n)
values = [1, 2, 3, 4, 2, 3]
unique = set(values)
print(unique)  # {1, 2, 3, 4}
```

좋은 점은 속도만이 아닙니다. set을 쓰는 순간 “여기서는 순서보다 membership과 uniqueness가 중요하다”는 의도가 코드에 바로 드러납니다.

## 단계별 실습

### Step 1: 기본 set 연산 확인하기

```python
fruits = {"apple", "banana", "cherry"}

fruits.add("date")
fruits.discard("banana")

print("apple" in fruits)  # True
print(len(fruits))         # 3
```

### Step 2: 충돌을 강제로 만들고도 dedup이 유지되는지 보기

```python
class Tag:
    def __init__(self, name: str):
        self.name = name

    def __hash__(self) -> int:
        return 7

    def __eq__(self, other) -> bool:
        return isinstance(other, Tag) and self.name == other.name

    def __repr__(self) -> str:
        return f"Tag({self.name!r})"

seen = {Tag("python"), Tag("api"), Tag("python")}

print(seen)
print(Tag("python") in seen)  # True
print(len(seen))               # 2
```

예시 출력은 다음과 같습니다.

```text
{Tag('api'), Tag('python')}
True
2
```

#### 이 결과를 읽는 법

- 세 객체 모두 같은 해시값을 쓰게 했으므로 충돌은 반드시 발생합니다.
- 그런데도 set에는 논리적으로 두 원소만 남습니다. `Tag("python")` 두 개가 equality 기준으로 같은 키이기 때문입니다.
- 즉, set의 속도는 해시 테이블에서 오지만, 정확성은 안정적인 해시와 올바른 equality 의미에 달려 있습니다.

### Step 3: “list는 안 된다”를 넘어서 `frozenset`이 왜 되는지 증명하기

```python
try:
    invalid = {{1, 2}}
except TypeError as error:
    print(type(error).__name__, error)

allowed = {frozenset({"read", "write"}), frozenset({"read"})}
print(frozenset({"read", "write"}) in allowed)  # True

role_map = {frozenset({"read", "write"}): "editor"}
print(role_map[frozenset({"write", "read"})])   # editor
```

예시 출력은 다음과 같습니다.

```text
TypeError unhashable type: 'set'
True
editor
```

#### 이 결과를 읽는 법

plain `set`은 가변 객체라서 자기 자신을 다른 set의 원소나 dict 키로 넣을 수 없습니다. 반면 `frozenset`은 생성 후 내용이 바뀌지 않으므로 안정적인 해시를 만들 수 있고, 그래서 중첩 set이나 dict 키 역할을 안전하게 수행합니다.

### Step 4: 집합 연산을 저장 모델과 연결해 보기

```python
a = {1, 2, 3, 4, 5}
b = {4, 5, 6, 7, 8}

print(a | b)  # union
print(a & b)  # intersection
print(a - b)  # difference
print(a ^ b)  # symmetric difference
```

이 연산자들이 자연스러운 이유는 set이 애초부터 “고유한 키의 membership” 중심 구조이기 때문입니다.

### Step 5: 태그 필터링은 proof가 아니라 응용으로 보기

```python
articles = [
    {"title": "Python Intro", "tags": {"python", "beginner"}},
    {"title": "Django REST", "tags": {"python", "django", "api"}},
    {"title": "React Hooks", "tags": {"javascript", "react"}},
    {"title": "Flask API", "tags": {"python", "flask", "api"}},
]

required = {"python", "api"}
matches = [article for article in articles if required <= article["tags"]]
print([article["title"] for article in matches])
```

태그 필터링은 좋은 실무 예시입니다. 다만 이 예시가 의미 있으려면 먼저 membership과 subset 검사가 왜 빠른지 내부 모델부터 이해해야 합니다.

## 이 코드에서 먼저 봐야 할 점

- set은 key-only hash table로 이해하는 편이 가장 정확합니다.
- set에서도 collision은 발생하지만 uniqueness와 membership semantics는 깨지지 않습니다.
- dedup은 해시가 탐색 범위를 좁히고 equality가 동일성을 확정하기 때문에 성립합니다.
- `frozenset`은 이름만 다른 alias가 아니라, 해시 가능한 불변 set이라는 중요한 역할을 가집니다.
- 집합 연산이 간결한 이유는 구조 자체가 unique-key membership 중심이기 때문입니다.

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 빈 set을 `{}`로 생성 | `{}`는 빈 dict입니다 | `set()`을 사용합니다 |
| 충돌은 일어나지 않는다고 생각 | 해시 테이블에서 충돌은 정상입니다 | 안정적인 `__hash__`와 `__eq__`를 설계합니다 |
| 가변 값을 set 원소로 사용 | 해시할 수 없거나 안전하지 않습니다 | `tuple`, `frozenset` 같은 불변 값을 사용합니다 |
| set 순서가 의미 있다고 가정 | 반복 순서는 안정적인 의미 계약이 아닙니다 | 출력 순서가 필요하면 명시적으로 정렬합니다 |
| `frozenset`을 단지 문법 취향으로 생각 | 중첩 set과 dict key 문제를 해결합니다 | set 자체를 원소/키로 써야 할 때 사용합니다 |

## 실무에서 이렇게 쓰입니다

- 권한 집합은 교집합·부분집합 검사와 함께 관리됩니다.
- 데이터 정제 파이프라인은 raw 값을 먼저 set으로 바꿔 중복을 제거합니다.
- 이미 처리한 ID를 set에 기록해 중복 작업을 막습니다.
- feature flag와 태그는 membership 중심이라 set과 잘 맞습니다.
- 두 데이터셋의 차이를 루프보다 차집합으로 표현하면 의도와 비용이 함께 명확해집니다.

## 실무에서는 이렇게 생각합니다

숙련된 개발자는 순서가 제품 요구사항이 아니라 membership이 핵심일 때 가장 먼저 set을 떠올립니다. 이 한 번의 선택만으로 코드가 짧아지고 accidental O(n²)도 줄어듭니다.

또한 정확성은 원소 semantics에 달려 있다는 점도 압니다. equality나 해시가 불안정하면 set은 더 이상 믿을 수 있는 dedup 도구가 아닙니다.

## 체크리스트

- [ ] set이 dict와 같은 해시 테이블 계열 구조라는 점을 설명할 수 있다
- [ ] collision과 equality가 어떻게 함께 올바른 dedup을 만드는지 설명할 수 있다
- [ ] `set`과 `frozenset`의 hashability 경계를 설명할 수 있다
- [ ] 합집합, 교집합, 차집합, 대칭차집합을 상황에 맞게 사용할 수 있다
- [ ] 순서보다 membership이 중요할 때 set을 선택할 수 있다

## 연습 문제

1. `Tag` 예시를 확장해 5개의 객체가 모두 같은 해시값을 갖게 만든 뒤, membership이 여전히 올바르게 동작하는지 확인해 보세요.
2. `frozenset` 권한 묶음들의 set을 만들고, 그중 `read`와 `write`를 모두 가진 묶음을 찾아 보세요.
3. 큰 입력에서 list 기반 중복 제거 루프와 `set(values)`를 비교하고, 왜 차이가 나는지 저장 모델로 설명해 보세요.

## 정리 및 다음 글 안내

Python `set`은 key-only hash table입니다. 그래서 빠른 membership test, 자동 dedup, 간결한 집합 연산이 모두 같은 저장 모델에서 나옵니다. 그리고 그 정확성은 안정적인 해시와 equality에 달려 있습니다. 다음 글에서는 시리즈를 마무리하며 상황별로 어떤 자료구조를 선택해야 하는지 기준을 정리하겠습니다.


## 타입 힌트 기반 집합 구현

Python set의 내부 원리를 이해하기 위해 해시 테이블 기반의 간소화된 집합을 구현합니다.

```python
from __future__ import annotations

from typing import Generic, Iterator, TypeVar

T = TypeVar("T")

_EMPTY = object()
_DELETED = object()


class HashSet(Generic[T]):
    """Open addressing 기반 집합입니다."""

    def __init__(self, capacity: int = 8) -> None:
        self._capacity = capacity
        self._size = 0
        self._slots: list[object] = [_EMPTY] * capacity

    def _hash_index(self, item: T) -> int:
        return hash(item) % self._capacity

    def add(self, item: T) -> None:
        if self._size / self._capacity >= 0.67:
            self._resize()
        idx = self._find_slot(item)
        if self._slots[idx] is _EMPTY or self._slots[idx] is _DELETED:
            self._slots[idx] = item
            self._size += 1

    def _find_slot(self, item: T) -> int:
        idx = self._hash_index(item)
        first_deleted: int | None = None
        while self._slots[idx] is not _EMPTY:
            if self._slots[idx] is _DELETED:
                if first_deleted is None:
                    first_deleted = idx
            elif self._slots[idx] == item:
                return idx
            idx = (idx + 1) % self._capacity
        return first_deleted if first_deleted is not None else idx

    def __contains__(self, item: object) -> bool:
        idx = self._hash_index(item)  # type: ignore[arg-type]
        while self._slots[idx] is not _EMPTY:
            if self._slots[idx] is not _DELETED and self._slots[idx] == item:
                return True
            idx = (idx + 1) % self._capacity
        return False

    def discard(self, item: T) -> None:
        idx = self._hash_index(item)
        while self._slots[idx] is not _EMPTY:
            if self._slots[idx] is not _DELETED and self._slots[idx] == item:
                self._slots[idx] = _DELETED
                self._size -= 1
                return
            idx = (idx + 1) % self._capacity

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[T]:
        for slot in self._slots:
            if slot is not _EMPTY and slot is not _DELETED:
                yield slot  # type: ignore[misc]

    def _resize(self) -> None:
        old_slots = self._slots
        self._capacity *= 2
        self._slots = [_EMPTY] * self._capacity
        self._size = 0
        for slot in old_slots:
            if slot is not _EMPTY and slot is not _DELETED:
                self.add(slot)  # type: ignore[arg-type]

    def union(self, other: HashSet[T]) -> HashSet[T]:
        result: HashSet[T] = HashSet()
        for item in self:
            result.add(item)
        for item in other:
            result.add(item)
        return result

    def intersection(self, other: HashSet[T]) -> HashSet[T]:
        result: HashSet[T] = HashSet()
        for item in self:
            if item in other:
                result.add(item)
        return result

    def difference(self, other: HashSet[T]) -> HashSet[T]:
        result: HashSet[T] = HashSet()
        for item in self:
            if item not in other:
                result.add(item)
        return result

    def __repr__(self) -> str:
        items = ", ".join(repr(item) for item in self)
        return f"HashSet({{{items}}})"
```

### 설계 결정 세 가지

1. **중복 자동 무시**: `add()`에서 이미 존재하는 원소면 아무 일도 하지 않습니다. 이것이 set의 핵심 계약입니다.
2. **집합 연산 반환 타입**: union, intersection, difference 모두 새로운 HashSet을 반환합니다. 원본은 변하지 않습니다 (Python set의 `|`, `&`, `-` 연산자와 동일).
3. **discard vs remove**: discard는 원소가 없어도 에러를 내지 않습니다. Python set의 `discard()`와 동일한 계약입니다.

## 메모리 프로파일링: set vs list vs frozenset

```python
import sys


def compare_memory(n: int) -> None:
    data_list = list(range(n))
    data_set = set(range(n))
    data_frozenset = frozenset(range(n))

    print(f"n={n:>7}")
    print(f"  list:      {sys.getsizeof(data_list):>10} bytes")
    print(f"  set:       {sys.getsizeof(data_set):>10} bytes")
    print(f"  frozenset: {sys.getsizeof(data_frozenset):>10} bytes")


for n in [100, 1_000, 10_000]:
    compare_memory(n)
    print()
```

set은 해시 테이블을 유지해야 하므로 같은 원소 수에서 list보다 메모리를 더 씁니다. frozenset은 set과 거의 동일한 크기입니다 (불변일 뿐 내부 구조는 같습니다). 메모리를 더 쓰는 대가로 O(1) membership test를 얻는 것이 핵심 교환입니다.

### 깊은 메모리 측정

```python
import sys
from typing import Any


def deep_getsizeof(obj: Any, seen: set[int] | None = None) -> int:
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)
    size = sys.getsizeof(obj)
    if isinstance(obj, (list, tuple, set, frozenset)):
        size += sum(deep_getsizeof(item, seen) for item in obj)
    elif isinstance(obj, dict):
        size += sum(deep_getsizeof(k, seen) + deep_getsizeof(v, seen) for k, v in obj.items())
    return size


n = 10_000
list_deep = deep_getsizeof(list(range(n)))
set_deep = deep_getsizeof(set(range(n)))

print(f"list deep (10k): {list_deep:>10} bytes ({list_deep/n:.1f} per elem)")
print(f"set deep (10k):  {set_deep:>10} bytes ({set_deep/n:.1f} per elem)")
```

## 성능 벤치마크: 집합 연산 속도

```python
import random
import timeit


def bench_membership_list(data: list[int], targets: list[int]) -> None:
    for t in targets:
        _ = t in data


def bench_membership_set(data: set[int], targets: list[int]) -> None:
    for t in targets:
        _ = t in data


n = 100_000
k = 10_000
universe = list(range(n))
targets = random.sample(universe, k)

data_list = universe[:]
data_set = set(universe)

trials = 5
t_list = timeit.timeit(lambda: bench_membership_list(data_list, targets), number=trials)
t_set = timeit.timeit(lambda: bench_membership_set(data_set, targets), number=trials)

print(f"list membership (10k in 100k): {t_list:.4f}s")
print(f"set membership (10k in 100k):  {t_set:.4f}s")
print(f"list/set = {t_list/t_set:.0f}x")
```

### 집합 연산 벤치마크

```python
import random
import timeit


def bench_set_ops(n: int = 50_000) -> None:
    a = set(random.sample(range(n * 2), n))
    b = set(random.sample(range(n * 2), n))

    _ = a | b   # union
    _ = a & b   # intersection
    _ = a - b   # difference
    _ = a ^ b   # symmetric difference


def bench_list_ops(n: int = 50_000) -> None:
    a = random.sample(range(n * 2), n)
    b = random.sample(range(n * 2), n)

    # list로 동일한 연산 흉내
    _ = list(set(a) | set(b))
    _ = [x for x in a if x in set(b)]
    _ = [x for x in a if x not in set(b)]


trials = 5
t_set = timeit.timeit(bench_set_ops, number=trials)
t_list = timeit.timeit(bench_list_ops, number=trials)

print(f"set operations (50k):  {t_set:.4f}s")
print(f"list operations (50k): {t_list:.4f}s")
```

set의 집합 연산(`|`, `&`, `-`, `^`)은 C 레벨에서 구현되어 있어, Python 레벨의 list 컴프리헨션보다 훨씬 빠릅니다.

## unittest로 HashSet 검증

```python
import unittest


class TestHashSet(unittest.TestCase):
    def setUp(self) -> None:
        self.hs: HashSet[int] = HashSet()

    def test_add_and_contains(self) -> None:
        self.hs.add(1)
        self.hs.add(2)
        self.assertIn(1, self.hs)
        self.assertIn(2, self.hs)
        self.assertNotIn(3, self.hs)

    def test_duplicate_ignored(self) -> None:
        self.hs.add(5)
        self.hs.add(5)
        self.hs.add(5)
        self.assertEqual(len(self.hs), 1)

    def test_discard(self) -> None:
        self.hs.add(10)
        self.hs.discard(10)
        self.assertNotIn(10, self.hs)
        self.assertEqual(len(self.hs), 0)

    def test_discard_missing(self) -> None:
        # discard는 없는 원소에 대해 에러를 내지 않음
        self.hs.discard(999)  # no error

    def test_union(self) -> None:
        a: HashSet[int] = HashSet()
        b: HashSet[int] = HashSet()
        for i in [1, 2, 3]:
            a.add(i)
        for i in [3, 4, 5]:
            b.add(i)
        result = a.union(b)
        self.assertEqual(sorted(result), [1, 2, 3, 4, 5])

    def test_intersection(self) -> None:
        a: HashSet[int] = HashSet()
        b: HashSet[int] = HashSet()
        for i in [1, 2, 3, 4]:
            a.add(i)
        for i in [3, 4, 5, 6]:
            b.add(i)
        result = a.intersection(b)
        self.assertEqual(sorted(result), [3, 4])

    def test_difference(self) -> None:
        a: HashSet[int] = HashSet()
        b: HashSet[int] = HashSet()
        for i in [1, 2, 3]:
            a.add(i)
        for i in [2, 3, 4]:
            b.add(i)
        result = a.difference(b)
        self.assertEqual(sorted(result), [1])

    def test_resize(self) -> None:
        for i in range(50):
            self.hs.add(i)
        self.assertEqual(len(self.hs), 50)
        for i in range(50):
            self.assertIn(i, self.hs)


if __name__ == "__main__":
    unittest.main()
```

## set 컴프리헨션과 집합 대수

set 컴프리헨션은 list 컴프리헨션과 동일한 문법에 중괄호를 씁니다.

```python
# 1부터 100까지의 수 중 3의 배수이면서 5의 배수인 것
multiples = {x for x in range(1, 101) if x % 3 == 0 and x % 5 == 0}
print(multiples)  # {15, 30, 45, 60, 75, 90}

# 동일한 결과를 집합 연산으로
threes = {x for x in range(1, 101) if x % 3 == 0}
fives = {x for x in range(1, 101) if x % 5 == 0}
print(threes & fives)  # {15, 30, 45, 60, 75, 90}
```

집합 대수의 기본 법칙은 코드로 검증할 수 있습니다.

```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}
c = {4, 5, 6, 7}

# 분배법칙: A & (B | C) == (A & B) | (A & C)
assert a & (b | c) == (a & b) | (a & c)

# 드모르간: ~(A | B) == ~A & ~B (전체집합 U 기준)
u = set(range(10))
assert u - (a | b) == (u - a) & (u - b)
```

이 법칙들은 복잡한 필터 조건을 집합 연산으로 분해할 때 유용합니다.

## 실무 패턴: 중복 제거와 집합 연산

```python
# 패턴 1: 순서를 유지하면서 중복 제거
def deduplicate_ordered(items: list[str]) -> list[str]:
    """삽입 순서를 유지하면서 중복을 제거합니다."""
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


# 패턴 2: 두 데이터 소스의 차이 분석
def analyze_changes(old_ids: set[str], new_ids: set[str]) -> dict[str, set[str]]:
    """이전/현재 상태를 비교해 추가/삭제/유지를 구분합니다."""
    return {
        "added": new_ids - old_ids,
        "removed": old_ids - new_ids,
        "unchanged": old_ids & new_ids,
    }


# 패턴 3: 태그 기반 필터링
articles = {
    "글1": {"python", "자료구조"},
    "글2": {"python", "웹"},
    "글3": {"자료구조", "알고리즘"},
}

# python AND 자료구조 태그를 모두 가진 글
target_tags = {"python", "자료구조"}
matched = [title for title, tags in articles.items() if target_tags <= tags]
print(matched)  # ['글1']
```

`<=` 연산자는 부분집합 검사입니다. `target_tags <= tags`는 "target_tags의 모든 원소가 tags에 포함되는가"를 의미합니다.

## 처음 질문으로 돌아가기

- **`set`은 왜 중복 제거와 membership test에 강할까요?**
  - set은 내부적으로 해시 테이블을 사용합니다. 원소를 추가할 때 해시로 슬롯을 계산하고, 이미 같은 값이 있으면 무시합니다(자동 중복 제거). membership test도 해시로 슬롯을 바로 찾으므로 O(1)입니다. list의 O(n) 선형 탐색과 대비됩니다.
- **충돌과 hashability는 set에서 어떤 의미를 가질까요?**
  - 충돌은 서로 다른 원소가 같은 슬롯에 매핑되는 상황으로, probing으로 해결합니다. hashable이란 `__hash__()`를 구현하고 값이 불변인 객체를 뜻합니다. list처럼 내용이 바뀔 수 있는 객체는 해시가 변할 위험이 있어 set 원소가 될 수 없습니다.
- **왜 `frozenset`은 set 원소나 dict 키가 될 수 있고 plain `set`은 안 될까요?**
  - frozenset은 불변이므로 해시 값이 객체 수명 동안 변하지 않습니다. plain set은 add/discard로 내용이 바뀔 수 있어, 해시 값이 변할 위험이 있습니다. 해시 기반 구조(set, dict)는 키/원소의 해시가 바뀌면 정합성이 깨지므로, 불변인 frozenset만 허용합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Structures with Python 101 (1/10): 자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [Data Structures with Python 101 (2/10): 배열과 리스트](./02-arrays-and-lists.md)
- [Data Structures with Python 101 (3/10): 스택과 큐](./03-stacks-and-queues.md)
- [Data Structures with Python 101 (4/10): 해시 테이블과 dict](./04-hash-tables-and-dict.md)
- [Data Structures with Python 101 (5/10): 연결 리스트](./05-linked-lists.md)
- [Data Structures with Python 101 (6/10): 트리와 이진 트리](./06-trees-and-binary-trees.md)
- [Data Structures with Python 101 (7/10): 힙과 우선순위 큐](./07-heaps-and-priority-queues.md)
- [Data Structures with Python 101 (8/10): 그래프 표현](./08-graph-representations.md)
- **set과 집합 연산 (현재 글)**
- 자료구조 선택 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Python Docs — Set Types](https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset)
- [CPython set implementation (GitHub)](https://github.com/python/cpython/blob/main/Objects/setobject.c)
- [Python Data Model — `__hash__` and `__eq__`](https://docs.python.org/3/reference/datamodel.html#object.__hash__)
- [Real Python — Sets in Python](https://realpython.com/python-sets/)
- [Python TimeComplexity — Set](https://wiki.python.org/moin/TimeComplexity)
- [book-examples 저장소 — data-structures-python-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/data-structures-python-101/ko)

Tags: Python, 자료구조, set, 집합 연산, frozenset
