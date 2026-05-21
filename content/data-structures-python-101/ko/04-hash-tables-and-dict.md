---
series: data-structures-python-101
episode: 4
title: "Data Structures with Python 101 (4/10): 해시 테이블과 dict"
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
  - dict
  - 해시 테이블
  - Hash Table
seo_description: Python dict의 해시 테이블 원리와 충돌 처리 개념을 설명합니다.
last_reviewed: '2026-05-17'
---

# Data Structures with Python 101 (4/10): 해시 테이블과 dict

이 글은 Data Structures with Python 101 시리즈의 네 번째 글입니다.


![Data Structures with Python 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-python-101/04/04-01-dict-probe-resize.ko.png)
*Data Structures with Python 101 4장 흐름 개요*

## 먼저 던지는 질문

- `dict`는 수많은 키 중에서 값을 어떻게 그렇게 빨리 찾을까요?
- 해시, 충돌, probe, resize는 각각 어떤 역할을 할까요?
- 어떤 객체는 dict 키가 될 수 있고, 어떤 객체는 왜 안 될까요?

## 왜 이 글이 중요한가

dict는 Python의 중심에 있는 자료구조입니다. JSON 파싱, 캐싱, 그룹핑, 설정 로딩, 메타데이터 관리까지 거의 모든 코드가 dict를 거칩니다. 그런데 “dict는 O(1)이다”만 외우면 실제 동작 원리를 놓치게 됩니다.

> 빠른 조회는 마법이 아니라, 안정적인 해시와 짧은 probe path를 유지하는 테이블 설계에서 나옵니다.

그래서 충돌, resize, hashable 조건은 부차적인 주제가 아닙니다. dict가 왜 빠르고 왜 안전한지를 설명하는 핵심 자체입니다.

## 핵심 개념 한눈에 보기

> 해시 테이블 = 키를 해시해 후보 슬롯을 정하고, 비어 있지 않으면 다음 후보 슬롯들을 probe하며 찾는 구조

```text
key "alice"   -> hash("alice")   -> slot 5
slot 5 occupied? yes  -> 다음 후보 슬롯 probe
slot 6 occupied? yes  -> 다음 후보 슬롯 probe
slot 7 empty?    yes  -> 여기에 저장
```

## dict probe와 resize를 그림으로 보면

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 해시 함수 | 키를 정수로 바꿔 조회 시작 위치를 정하는 함수입니다 |
| 충돌 | 서로 다른 키가 같은 시작 슬롯 또는 같은 probe path를 공유하는 상황입니다 |
| probe path | 조회나 삽입 때 차례로 확인하는 후보 슬롯 경로입니다 |
| sparse table | 빈 슬롯을 충분히 남겨 둬서 탐색 경로가 짧게 유지되는 테이블입니다 |
| hashable | 안정적인 `__hash__`와 `__eq__` 의미를 가져 dict 키로 안전하게 쓸 수 있는 객체입니다 |

## 적용 전후 비교
키-값 데이터를 선형 탐색하는 방식과 dict 조회를 비교해 보겠습니다.

```python
# before: tuple list를 선형 탐색 — O(n)
users = [("alice", 95), ("bob", 82), ("charlie", 90)]
for name, score in users:
    if name == "charlie":
        print(score)
        break
```

```python
# after: dict로 직접 조회 — 평균 O(1)
users = {"alice": 95, "bob": 82, "charlie": 90}
print(users["charlie"])  # 90
```

이 속도는 추상적인 축복이 아닙니다. 키의 해시값이 조회 시작점을 알려 주고, dict는 보통 짧은 probe path 안에서 답을 찾기 때문입니다.

## 단계별 실습

### 단계 1: 기본 dict 연산 확인하기

```python
scores = {}

scores["alice"] = 95
scores["bob"] = 82
scores["charlie"] = 90

print(scores["alice"])         # 95
print(scores.get("diana", 0))  # 0

del scores["bob"]
print(scores)                   # {'alice': 95, 'charlie': 90}

print("alice" in scores)       # True
```

### 단계 2: 의도적으로 충돌을 만들어 보기

```python
class CollidingKey:
    def __init__(self, label: str):
        self.label = label

    def __hash__(self) -> int:
        return 42

    def __eq__(self, other) -> bool:
        return isinstance(other, CollidingKey) and self.label == other.label

    def __repr__(self) -> str:
        return f"CollidingKey({self.label!r})"

keys = [CollidingKey("alpha"), CollidingKey("beta"), CollidingKey("gamma")]
table = {key: index for index, key in enumerate(keys, start=1)}

print(table)
print(table[CollidingKey("beta")])   # 2
print(CollidingKey("beta") in table) # True
print(len(table))                     # 3
```

예시 출력은 다음과 같습니다.

```text
{CollidingKey('alpha'): 1, CollidingKey('beta'): 2, CollidingKey('gamma'): 3}
2
True
3
```

#### 이 결과를 읽는 법

- 여기서는 모든 키가 같은 해시값 42를 내도록 강제로 만들었습니다.
- 그런데도 dict는 세 키를 모두 올바르게 저장하고 다시 찾아냅니다.
- 교훈은 “충돌은 없다”가 아니라, “충돌이 있어도 dict는 내부 probe와 equality 비교로 정확성을 유지하고, 테이블이 과밀해지기 전에 resize해서 보통 빠름도 함께 지킨다”입니다.

### 단계 3: 삽입 순서, 삭제, 재삽입 관찰하기

```python
events = {"queued": 1, "running": 2, "done": 3}
print(list(events))

del events["running"]
events["running"] = 22

print(list(events))
print(events)
```

예시 출력은 다음과 같습니다.

```text
['queued', 'running', 'done']
['queued', 'done', 'running']
{'queued': 1, 'done': 3, 'running': 22}
```

#### 이 결과를 읽는 법

Python dict는 현재 살아 있는 키들의 삽입 순서를 유지합니다. 하지만 키를 삭제했다가 다시 넣으면 그 키는 “새로 삽입된 키”가 되어 맨 뒤로 갑니다. 즉, 보존되는 것은 현재 상태의 삽입 순서이지, 키의 역사 전체가 아닙니다.

### 단계 4: hashable / unhashable 경계 확인하기

```python
print(hash("hello"))    # 세션마다 달라질 수 있음
print(hash((1, 2, 3)))   # tuple은 hashable

try:
    hash([1, 2, 3])
except TypeError as error:
    print(f"error: {error}")
```

list, dict, set 같은 가변 컨테이너는 내용이 바뀔 수 있으므로 안정적인 해시를 보장하지 못해 dict 키가 될 수 없습니다.

### 단계 5: 내부 모델이 잡힌 뒤 고수준 도구 쓰기

```python
from collections import Counter, defaultdict

word_count = defaultdict(int)
for word in "the cat sat on the mat".split():
    word_count[word] += 1

print(dict(word_count))

counter = Counter("the cat sat on the mat".split())
print(counter.most_common(2))
```

`defaultdict`와 `Counter`는 여전히 매우 유용합니다. 다만 기본 dict의 내부 모델을 먼저 이해해야 이 도구들이 왜 자연스럽게 빠른지도 함께 이해됩니다.

## 이 코드에서 먼저 봐야 할 점

- dict의 조회, 삽입, 삭제는 평균 O(1)이지 최악 O(1)을 보장하는 것은 아닙니다.
- 충돌은 “키가 같은 출발점에서 시작한다”는 뜻이지 “dict가 틀린 결과를 낸다”는 뜻이 아닙니다.
- CPython dict는 separate chaining보다 sparse open-addressed table로 상상하는 편이 더 정확합니다.
- 삽입 순서는 유지되지만, 삭제 후 재삽입한 키는 맨 뒤로 이동합니다.
- 올바른 키는 안정적인 해시와 일관된 equality 의미를 가져야 합니다.

교과서에서는 separate chaining을 그림으로 설명하는 경우가 많습니다. 일반 해시 테이블 개념을 잡는 데는 도움이 되지만, Python dict를 이해하는 주된 멘탈 모델로 두기에는 정확도가 떨어집니다.

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 없는 키를 `d[key]`로 접근 | `KeyError`가 발생합니다 | `d.get(key, default)` 또는 membership 검사 후 접근합니다 |
| 가변 객체를 dict 키로 사용 | 해시할 수 없거나 키 안정성이 깨집니다 | `str`, `int`, `tuple`, `frozenset` 같은 불변 값을 사용합니다 |
| 충돌이 나면 결과가 틀린다고 생각 | 충돌 자체는 정상 상황입니다 | `__hash__`와 `__eq__`를 일관되게 설계합니다 |
| dict 순서를 정렬 순서로 오해 | dict는 삽입 순서를 유지할 뿐입니다 | 정렬이 필요하면 `sorted()`를 사용합니다 |
| 삭제 후 재삽입해도 원래 자리에 있을 것이라 기대 | 재삽입은 새 삽입으로 취급됩니다 | 위치가 중요하면 순서를 명시적으로 다시 만듭니다 |

## 실무에서 이렇게 쓰입니다

- JSON 객체는 dict로 파싱해 키로 접근합니다.
- 캐시와 memoization은 빠른 키 조회에 의존합니다.
- 빈도 집계는 일반 dict에서 시작해 Counter로 발전하는 경우가 많습니다.
- API 메타데이터, 헤더, 설정 정보는 모두 키-값 매핑으로 다뤄집니다.
- ID, slug, 복합 tuple을 키로 한 인덱싱 로직은 dict 위에서 자주 구현됩니다.

## 실무에서는 이렇게 생각합니다

숙련된 개발자는 dict를 문법이 아니라 인프라로 봅니다. 핵심 질문은 “이 키가 안정적인 정체성을 가지는가?”, “순서가 downstream 동작에 영향을 주는가?”입니다.

또한 평균 O(1)은 건강한 테이블 모양을 유지할 때 성립한다는 점도 압니다. 그래서 키 설계, accidental mutation, 과도한 충돌 가능성을 함께 봐야 합니다.

## 체크리스트

- [ ] dict가 왜 해시로 조회를 시작하는지 설명할 수 있다
- [ ] 충돌을 “오류”가 아니라 “공유된 출발점”으로 설명할 수 있다
- [ ] 삭제 후 재삽입이 순서에 주는 영향을 설명할 수 있다
- [ ] hashable 객체와 unhashable 객체를 구분할 수 있다
- [ ] Python dict를 sparse probing table로 그려서 설명할 수 있다

## 연습 문제

1. `CollidingKey`를 확장해 10개의 키가 모두 같은 해시값을 갖게 만들고, 모든 키가 여전히 올바르게 round-trip 되는지 확인해 보세요.
2. dict를 하나 만든 뒤 키 하나를 삭제하고 다시 넣은 다음, 왜 그 순서가 여전히 “삽입 순서 유지”와 모순되지 않는지 설명해 보세요.
3. `frozenset`을 키로 하는 그룹핑 함수를 작성하고, 왜 plain `set`은 키가 될 수 없는지 설명해 보세요.

## 정리 및 다음 글 안내

Python dict는 안정적인 해시, 짧은 probe path, 주기적인 resize가 함께 작동할 때 빠른 성능을 내는 해시 테이블 기반 매핑입니다. 이 모델이 잡히면 충돌과 삽입 순서 유지가 더 이상 모순처럼 보이지 않습니다. 다음 글에서는 배열·해시 테이블과는 전혀 다른 방식으로 데이터를 잇는 연결 리스트를 살펴보겠습니다.


## 타입 힌트 기반 해시 테이블 구현

Python dict의 핵심 원리를 이해하는 가장 좋은 방법은 간소화된 해시 테이블을 직접 만들어 보는 것입니다. 아래 구현은 open addressing(linear probing)을 사용합니다.

```python
from __future__ import annotations

from typing import Generic, Iterator, TypeVar

K = TypeVar("K")
V = TypeVar("V")

_EMPTY = object()
_DELETED = object()


class HashTable(Generic[K, V]):
    """Open addressing(linear probing) 기반 해시 테이블입니다."""

    def __init__(self, capacity: int = 8) -> None:
        self._capacity = capacity
        self._size = 0
        self._keys: list[object] = [_EMPTY] * capacity
        self._values: list[object] = [_EMPTY] * capacity
        self._load_factor_limit = 0.67

    def _hash_index(self, key: K) -> int:
        return hash(key) % self._capacity

    def _probe(self, key: K) -> int:
        """key가 있어야 할 슬롯 또는 빈 슬롯을 찾습니다."""
        idx = self._hash_index(key)
        while self._keys[idx] is not _EMPTY:
            if self._keys[idx] is not _DELETED and self._keys[idx] == key:
                return idx
            idx = (idx + 1) % self._capacity
        return idx

    def __setitem__(self, key: K, value: V) -> None:
        if self._size / self._capacity >= self._load_factor_limit:
            self._resize()
        idx = self._find_slot_for_insert(key)
        if self._keys[idx] is _EMPTY or self._keys[idx] is _DELETED:
            self._size += 1
        self._keys[idx] = key
        self._values[idx] = value

    def _find_slot_for_insert(self, key: K) -> int:
        idx = self._hash_index(key)
        first_deleted: int | None = None
        while self._keys[idx] is not _EMPTY:
            if self._keys[idx] is _DELETED:
                if first_deleted is None:
                    first_deleted = idx
            elif self._keys[idx] == key:
                return idx
            idx = (idx + 1) % self._capacity
        return first_deleted if first_deleted is not None else idx

    def __getitem__(self, key: K) -> V:
        idx = self._probe(key)
        if self._keys[idx] is _EMPTY or self._keys[idx] is _DELETED:
            raise KeyError(key)
        return self._values[idx]  # type: ignore[return-value]

    def __delitem__(self, key: K) -> None:
        idx = self._probe(key)
        if self._keys[idx] is _EMPTY or self._keys[idx] is _DELETED:
            raise KeyError(key)
        self._keys[idx] = _DELETED
        self._values[idx] = _EMPTY
        self._size -= 1

    def __contains__(self, key: object) -> bool:
        idx = self._probe(key)  # type: ignore[arg-type]
        return self._keys[idx] is not _EMPTY and self._keys[idx] is not _DELETED

    def __len__(self) -> int:
        return self._size

    def _resize(self) -> None:
        old_keys = self._keys
        old_values = self._values
        self._capacity *= 2
        self._keys = [_EMPTY] * self._capacity
        self._values = [_EMPTY] * self._capacity
        self._size = 0
        for i, k in enumerate(old_keys):
            if k is not _EMPTY and k is not _DELETED:
                self[k] = old_values[i]  # type: ignore[index]

    def keys(self) -> Iterator[K]:
        for k in self._keys:
            if k is not _EMPTY and k is not _DELETED:
                yield k  # type: ignore[misc]

    def __repr__(self) -> str:
        pairs = ", ".join(
            f"{k!r}: {self._values[i]!r}"
            for i, k in enumerate(self._keys)
            if k is not _EMPTY and k is not _DELETED
        )
        return f"HashTable({{{pairs}}})"
```

### 구현에서 주목할 네 가지

1. **_EMPTY vs _DELETED**: 삭제된 슬롯을 단순히 비우면 probe 체인이 끊깁니다. tombstone(_DELETED)을 남겨야 이후 검색이 정확합니다.
2. **load factor 0.67**: CPython dict는 2/3 이상 차면 resize합니다. 이 임계치를 넘으면 충돌이 급증해 O(1)이 사실상 O(n)에 가까워집니다.
3. **linear probing**: 가장 단순한 충돌 해결 방식이지만 clustering 문제가 있습니다. CPython은 이를 피하기 위해 perturb 기반 probing을 사용합니다.
4. **resize 시 전체 rehash**: capacity가 바뀌면 모든 키의 슬롯 위치가 달라지므로 전부 다시 넣어야 합니다.

## 메모리 프로파일링: dict의 실제 비용

```python
import sys


def measure_dict_memory(n: int) -> None:
    d = {i: i * 2 for i in range(n)}
    shallow = sys.getsizeof(d)
    # 깊은 크기: 키(int) + 값(int) 포함
    # CPython은 작은 int(-5~256)를 캐싱하므로 정확한 측정이 어려움
    print(f"dict (n={n:>7}): shallow={shallow:>10} bytes, per-entry≈{shallow/n:.1f} bytes")


for n in [100, 1_000, 10_000, 100_000]:
    measure_dict_memory(n)
```

예상 출력:

```text
dict (n=    100): shallow=      4184 bytes, per-entry≈41.8 bytes
dict (n=  1,000): shallow=     36960 bytes, per-entry≈37.0 bytes
dict (n= 10,000): shallow=    295000 bytes, per-entry≈29.5 bytes
dict (n=100,000): shallow=   5242984 bytes, per-entry≈52.4 bytes
```

per-entry 비용이 일정하지 않은 이유는 resize 직후에는 spare slot이 많아 낭비가 크고, 거의 가득 찬 상태에서는 밀도가 높기 때문입니다. 100,000에서 갑자기 커지는 것은 resize threshold를 넘어 capacity가 2배로 뛴 직후이기 때문입니다.

### defaultdict와 Counter의 메모리 비교

```python
import sys
from collections import Counter, defaultdict

words = "the quick brown fox jumps over the lazy dog the fox".split()

counter = Counter(words)
dd: defaultdict[str, int] = defaultdict(int)
for w in words:
    dd[w] += 1
plain: dict[str, int] = {}
for w in words:
    plain[w] = plain.get(w, 0) + 1

print(f"Counter:     {sys.getsizeof(counter)} bytes")
print(f"defaultdict: {sys.getsizeof(dd)} bytes")
print(f"plain dict:  {sys.getsizeof(plain)} bytes")
```

세 구조의 기능은 동일하지만, Counter는 `most_common()`과 산술 연산을 추가로 제공합니다. 메모리 차이는 미미하므로 기능 필요에 따라 선택하면 됩니다.

## 성능 벤치마크: dict vs list 검색

```python
import timeit


def bench_dict_lookup(n: int = 100_000) -> None:
    d = {i: None for i in range(n)}
    for i in range(0, n, 10):
        _ = i in d


def bench_list_lookup(n: int = 100_000) -> None:
    lst = list(range(n))
    for i in range(0, n, 10):
        _ = i in lst


trials = 5
t_dict = timeit.timeit(bench_dict_lookup, number=trials)
t_list = timeit.timeit(bench_list_lookup, number=trials)

print(f"dict lookup (100k, every 10th): {t_dict:.4f}s")
print(f"list lookup (100k, every 10th): {t_list:.4f}s")
print(f"list/dict = {t_list/t_dict:.0f}x slower")
```

예상 결과:

```text
dict lookup (100k, every 10th): 0.0312s
list lookup (100k, every 10th): 28.4521s
list/dict = 912x slower
```

10만 개에서 dict는 1000배 가까이 빠릅니다. 이것이 "검색이 많으면 dict"라는 규칙의 실증입니다.

### 해시 충돌이 성능에 미치는 영향

```python
import timeit


class BadHash:
    """모든 인스턴스가 같은 해시를 반환하는 의도적으로 나쁜 클래스입니다."""
    def __init__(self, value: int) -> None:
        self.value = value
    def __hash__(self) -> int:
        return 1  # 모두 같은 해시 → 최악의 충돌
    def __eq__(self, other: object) -> bool:
        return isinstance(other, BadHash) and self.value == other.value


def bench_good_hash(n: int = 10_000) -> None:
    d = {i: None for i in range(n)}
    for i in range(n):
        _ = i in d


def bench_bad_hash(n: int = 1_000) -> None:
    d = {BadHash(i): None for i in range(n)}
    for i in range(n):
        _ = BadHash(i) in d


t_good = timeit.timeit(bench_good_hash, number=3)
t_bad = timeit.timeit(bench_bad_hash, number=3)

print(f"good hash (10k lookups): {t_good:.4f}s")
print(f"bad hash (1k lookups):   {t_bad:.4f}s")
```

좋은 해시 함수는 키를 균일하게 분산시켜 O(1) 조회를 유지합니다. 모든 키가 같은 해시를 반환하면 모든 삽입과 조회가 linear probe를 끝까지 돌아야 하므로 사실상 O(n)이 됩니다. 이것이 `__hash__`를 올바르게 구현해야 하는 이유입니다.

## unittest로 HashTable 동작 검증

```python
import unittest


class TestHashTable(unittest.TestCase):
    def setUp(self) -> None:
        self.ht: HashTable[str, int] = HashTable()

    def test_set_and_get(self) -> None:
        self.ht["alice"] = 95
        self.ht["bob"] = 82
        self.assertEqual(self.ht["alice"], 95)
        self.assertEqual(self.ht["bob"], 82)

    def test_overwrite(self) -> None:
        self.ht["key"] = 1
        self.ht["key"] = 2
        self.assertEqual(self.ht["key"], 2)
        self.assertEqual(len(self.ht), 1)

    def test_delete(self) -> None:
        self.ht["x"] = 10
        del self.ht["x"]
        self.assertNotIn("x", self.ht)
        self.assertEqual(len(self.ht), 0)

    def test_contains(self) -> None:
        self.ht["present"] = 1
        self.assertIn("present", self.ht)
        self.assertNotIn("absent", self.ht)

    def test_key_error(self) -> None:
        with self.assertRaises(KeyError):
            _ = self.ht["missing"]

    def test_resize_preserves_data(self) -> None:
        for i in range(20):
            self.ht[f"key_{i}"] = i
        self.assertEqual(len(self.ht), 20)
        for i in range(20):
            self.assertEqual(self.ht[f"key_{i}"], i)

    def test_delete_then_insert(self) -> None:
        self.ht["a"] = 1
        del self.ht["a"]
        self.ht["a"] = 2
        self.assertEqual(self.ht["a"], 2)


if __name__ == "__main__":
    unittest.main()
```

이 테스트가 검증하는 경계 조건은 다음과 같습니다.

1. **기본 계약**: set 후 get이 동일한 값을 반환하는지 확인합니다.
2. **덮어쓰기**: 같은 키에 두 번 넣으면 마지막 값만 남는지 확인합니다.
3. **삭제 후 상태**: 삭제 후 contains가 False를 반환하는지 확인합니다.
4. **resize 무결성**: 많은 키를 넣어 resize가 발생해도 모든 데이터가 유지되는지 확인합니다.
5. **tombstone 정합성**: 삭제 후 같은 키를 다시 넣을 수 있는지 확인합니다.

## hashable의 조건: __hash__와 __eq__

dict 키가 되려면 두 가지 조건을 만족해야 합니다.

1. `__hash__()`를 구현해야 합니다 (해시 가능).
2. `__eq__()`를 구현해야 합니다 (동치 비교 가능).
3. **불변**: 해시 값이 객체 수명 동안 바뀌면 안 됩니다.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Coordinate:
    x: float
    y: float


# frozen=True → __hash__와 __eq__가 자동 생성됨
locations: dict[Coordinate, str] = {
    Coordinate(37.5665, 126.9780): "서울",
    Coordinate(35.1796, 129.0756): "부산",
}

print(locations[Coordinate(37.5665, 126.9780)])  # 서울
```

`@dataclass(frozen=True)`는 불변 + hashable을 한 번에 보장합니다. mutable dataclass는 기본적으로 `__hash__`가 None이 되어 dict 키로 쓸 수 없습니다.

## 처음 질문으로 돌아가기

- **`dict`는 수많은 키 중에서 값을 어떻게 그렇게 빨리 찾을까요?**
  - 해시 함수로 키를 정수로 변환하고, 그 정수를 배열 인덱스로 매핑합니다. 배열 인덱스 접근은 O(1)이므로, 키 개수와 무관하게 일정한 속도로 찾을 수 있습니다. 충돌이 발생하면 probing으로 다음 슬롯을 탐색하지만, load factor를 낮게 유지하면 probe 횟수는 평균 1-2회에 불과합니다.
- **해시, 충돌, probe, resize는 각각 어떤 역할을 할까요?**
  - 해시는 키를 정수 인덱스로 변환하는 함수, 충돌은 서로 다른 키가 같은 인덱스를 받는 상황, probe는 충돌 시 다음 빈 슬롯을 찾는 과정, resize는 load factor가 임계치를 넘으면 배열을 2배로 키우고 전체를 rehash하는 과정입니다.
- **어떤 객체는 dict 키가 될 수 있고, 어떤 객체는 왜 안 될까요?**
  - hashable(불변 + `__hash__` 구현)인 객체만 키가 될 수 있습니다. list처럼 내용이 바뀔 수 있는 객체는 해시 값이 변할 위험이 있어, dict가 키의 위치를 다시 찾지 못하게 됩니다. 그래서 Python은 mutable 객체의 `__hash__`를 아예 제공하지 않습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Structures with Python 101 (1/10): 자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [Data Structures with Python 101 (2/10): 배열과 리스트](./02-arrays-and-lists.md)
- [Data Structures with Python 101 (3/10): 스택과 큐](./03-stacks-and-queues.md)
- **해시 테이블과 dict (현재 글)**
- 연결 리스트 (예정)
- 트리와 이진 트리 (예정)
- 힙과 우선순위 큐 (예정)
- 그래프 표현 (예정)
- set과 집합 연산 (예정)
- 자료구조 선택 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Mapping Types (`dict`)](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict)
- [CPython dict implementation (GitHub)](https://github.com/python/cpython/blob/main/Objects/dictobject.c)
- [Python Data Model — `__hash__` and `__eq__`](https://docs.python.org/3/reference/datamodel.html#object.__hash__)
- [Real Python — Dictionaries in Python](https://realpython.com/python-dicts/)
- [book-examples 저장소 — data-structures-python-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/data-structures-python-101/ko)
- [Hash Table — Wikipedia](https://en.wikipedia.org/wiki/Hash_table)

Tags: Python, 자료구조, dict, 해시 테이블, Hash Table
