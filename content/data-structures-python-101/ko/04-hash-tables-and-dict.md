---
series: data-structures-python-101
episode: 4
title: 해시 테이블과 dict
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
last_reviewed: '2026-05-12'
---

# 해시 테이블과 dict

이 글은 Data Structures with Python 101 시리즈의 네 번째 글입니다.

## 이 글에서 다룰 문제

- dict는 수많은 키 중에서 값을 어떻게 즉시 찾아낼까요?
- 해시 함수, 해시 충돌, 리사이징은 각각 어떤 역할을 할까요?
- 어떤 객체는 dict 키가 될 수 있고, 어떤 객체는 왜 안 될까요?
- defaultdict와 Counter는 기본 dict와 무엇이 다를까요?

> 멘탈 모델: dict는 “키를 저장하는 배열”이 아니라, 키를 해시값으로 바꿔 배열 위치를 계산하는 해시 테이블입니다. 빠른 조회는 그 변환 규칙에서 나옵니다.

## 왜 이 글이 중요한가

dict는 Python에서 list 다음으로 가장 자주 쓰는 자료구조입니다. JSON 파싱, 설정 관리, 캐싱, 그룹핑, API 파라미터 구성까지 거의 모든 Python 코드에 등장합니다. dict를 잘 안다는 것은 Python 코드의 절반 이상을 더 정확히 읽는다는 뜻에 가깝습니다.

> 해시 테이블은 키를 값에 O(1)로 매핑하는 구조입니다.

면접에서 “dict가 왜 O(1)인가?”라는 질문이 자주 나오는 이유도 같습니다. 답하려면 해시 함수, 충돌, 리사이징, hashable 객체 개념을 함께 이해해야 합니다. 현업에서도 이 지식은 중요합니다. 키 선택이 잘못되면 성능뿐 아니라 설계 자체가 흔들릴 수 있기 때문입니다.

## 핵심 개념 한눈에 보기

> 해시 테이블 = 키를 해시 함수로 정수로 바꾼 뒤, 그 값을 배열 인덱스로 사용해 저장하는 구조

```
key "alice"   -> hash("alice")  -> index 3
key "bob"     -> hash("bob")    -> index 7
key "charlie" -> hash("charlie")-> index 1

array:  [   |charlie|   |alice|   |   |   |bob|   ]
index:    0     1     2    3    4   5   6   7   8
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 해시 함수 | 임의 크기의 데이터를 고정 크기 정수로 변환하는 함수입니다 |
| 해시 충돌 | 서로 다른 키가 같은 인덱스로 매핑되는 상황입니다 |
| 로드 팩터 | 저장 원소 수를 배열 크기로 나눈 값으로, 높을수록 충돌 가능성이 커집니다 |
| 리사이징 | 로드 팩터가 커지면 내부 배열을 확장해 다시 배치하는 과정입니다 |
| hashable | `__hash__()`를 제공하고 불변 성질을 가져 dict 키로 사용할 수 있는 객체입니다 |

## Before / After

키-값 데이터를 list로 순회하는 방식과 dict로 조회하는 방식을 비교해 보겠습니다.

```python
# before: linear search in a list — O(n)
users = [("alice", 95), ("bob", 82), ("charlie", 90)]
for name, score in users:
    if name == "charlie":
        print(score)
        break
```

```python
# after: instant lookup with dict — O(1)
users = {"alice": 95, "bob": 82, "charlie": 90}
print(users["charlie"])  # 90
```

여기서 중요한 점은 dict가 “마법처럼 빠른 구조”가 아니라는 사실입니다. 빠른 이유는 키를 해시해서 위치를 계산할 수 있기 때문입니다. 그래서 키가 안정적이고 해시 가능해야 합니다.

## 단계별 실습

### Step 1: Basic dict operations

```python
scores = {}

# insert — O(1)
scores["alice"] = 95
scores["bob"] = 82
scores["charlie"] = 90

# lookup — O(1)
print(scores["alice"])      # 95
print(scores.get("diana", 0))  # 0 — default when key is missing

# delete — O(1)
del scores["bob"]
print(scores)  # {'alice': 95, 'charlie': 90}

# membership check — O(1)
print("alice" in scores)    # True
```

### Step 2: Inspect the hash() function

```python
# immutable objects are hashable
print(hash("hello"))    # a fixed integer (varies per session)
print(hash(42))         # 42
print(hash((1, 2, 3)))  # tuples are hashable

# mutable objects are not hashable
try:
    hash([1, 2, 3])
except TypeError as e:
    print(f"error: {e}")  # unhashable type: 'list'
```

### Step 3: Build a simple hash table from scratch

```python
class SimpleHashTable:
    def __init__(self, size: int = 10):
        self._size = size
        self._buckets = [[] for _ in range(size)]

    def _hash(self, key: str) -> int:
        return hash(key) % self._size

    def put(self, key: str, value):
        idx = self._hash(key)
        for i, (k, v) in enumerate(self._buckets[idx]):
            if k == key:
                self._buckets[idx][i] = (key, value)
                return
        self._buckets[idx].append((key, value))

    def get(self, key: str, default=None):
        idx = self._hash(key)
        for k, v in self._buckets[idx]:
            if k == key:
                return v
        return default

ht = SimpleHashTable()
ht.put("name", "Alice")
ht.put("age", 30)
print(ht.get("name"))   # Alice
print(ht.get("email"))  # None
```

### Step 4: Use defaultdict and Counter

```python
from collections import defaultdict, Counter

# defaultdict: auto-creates default values for missing keys
word_count = defaultdict(int)
for word in "the cat sat on the mat".split():
    word_count[word] += 1
print(dict(word_count))
# {'the': 2, 'cat': 1, 'sat': 1, 'on': 1, 'mat': 1}

# Counter: built for frequency counting
counter = Counter("the cat sat on the mat".split())
print(counter.most_common(2))  # [('the', 2), ('cat', 1)]
```

### Step 5: dict comprehension and sorting

```python
scores = {"alice": 95, "bob": 82, "charlie": 90, "diana": 88}

# dict comprehension
high_scores = {k: v for k, v in scores.items() if v >= 90}
print(high_scores)  # {'alice': 95, 'charlie': 90}

# sort by value
sorted_scores = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
print(sorted_scores)
# {'alice': 95, 'charlie': 90, 'diana': 88, 'bob': 82}
```

## 이 코드에서 먼저 봐야 할 점

- dict의 조회, 삽입, 삭제는 평균적으로 O(1)이지만 최악의 경우 O(n)도 가능합니다.
- `hash()` 결과는 세션마다 달라질 수 있습니다. 보안상의 이유로 해시 랜덤화가 적용되기 때문입니다.
- list, dict, set 같은 가변 객체는 해시할 수 없어서 dict 키로 쓸 수 없습니다.
- Python 3.7 이후 dict는 삽입 순서를 유지하지만, 그것이 해시 테이블이라는 본질을 바꾸지는 않습니다.

dict를 제대로 쓰려면 “조회가 빠르다”는 결과만 기억하면 부족합니다. 왜 빠른지, 어떤 키가 안정적인지, 충돌이 생겨도 왜 평균 성능을 유지하는지까지 함께 이해해야 실무에서 잘못된 설계를 피할 수 있습니다.

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 없는 키를 `d[key]`로 접근 | `KeyError`가 발생합니다 | `d.get(key, default)` 또는 `key in d`를 사용합니다 |
| list를 dict 키로 사용 | 가변 객체라 해시할 수 없습니다 | tuple 같은 불변 구조로 바꿉니다 |
| 순회 중 키 추가/삭제 | `RuntimeError`가 발생할 수 있습니다 | `list(d.keys())`처럼 복사해 순회합니다 |
| dict 비교가 순서에 의존한다고 오해 | 비교는 순서와 무관하게 이뤄집니다 | 순서가 아니라 키와 값 자체를 비교합니다 |
| 중첩 dict 기본값 미처리 | 하위 키 접근에서 `KeyError`가 납니다 | `defaultdict`나 `setdefault()`를 검토합니다 |

## 실무에서 이렇게 쓰입니다

- JSON 응답은 대부분 dict로 파싱해 값을 꺼냅니다.
- 환경 변수와 설정 로딩은 dict 기반으로 이뤄집니다.
- 캐시는 dict를 사용해 중복 계산을 피합니다.
- 로그 집계와 빈도 분석은 Counter로 간결하게 작성합니다.
- API 요청 파라미터와 메타데이터는 dict로 묶어 전달합니다.

## 실무에서는 이렇게 생각합니다

dict는 Python의 중심에 있는 자료구조입니다. 모듈, 클래스, 인스턴스 속성도 결국 dict와 깊게 연결되어 있습니다. 그래서 dict의 성능 특성을 이해하면 Python이라는 언어 자체를 더 구조적으로 보게 됩니다.

실무에서는 dataclass나 Pydantic 모델처럼 구조화된 타입을 더 자주 쓰더라도, 내부적으로는 dict와 맞닿아 있습니다. 겉모습이 더 정교해졌을 뿐, 키-값 매핑의 본질은 여전히 dict가 담당합니다.

## 체크리스트

- [ ] 해시 테이블이 어떻게 동작하는지 설명할 수 있다
- [ ] dict의 조회, 삽입, 삭제 시간 복잡도를 설명할 수 있다
- [ ] hashable 객체와 unhashable 객체를 구분할 수 있다
- [ ] defaultdict와 Counter를 활용할 수 있다
- [ ] dict comprehension으로 데이터를 변환할 수 있다

## 연습 문제

1. Counter를 쓰지 않고, 일반 dict만으로 문자열 list의 빈도를 세는 함수를 작성해 보세요.
2. 두 dict가 정확히 같은 키 집합을 갖는지 확인하는 함수를 작성해 보세요.
3. `{"a": {"b": {"c": 1}}}` 형태의 중첩 dict에서 `"a.b.c"` 같은 경로 문자열로 값을 가져오는 함수를 작성해 보세요.

## 정리 및 다음 글 안내

dict는 해시 테이블로 구현되어 빠른 키 기반 조회를 제공합니다. 해시 함수, 충돌, 리사이징, hashable 객체라는 네 가지 축을 이해하면 dict를 단순 문법이 아니라 성능 특성을 가진 도구로 다룰 수 있습니다. 다음 글에서는 배열과는 전혀 다른 방식으로 데이터를 잇는 연결 리스트를 살펴보겠습니다.

<!-- toc:begin -->
- [자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [배열과 리스트](./02-arrays-and-lists.md)
- [스택과 큐](./03-stacks-and-queues.md)
- **해시 테이블과 dict (현재 글)**
- 연결 리스트 (예정)
- 트리와 이진 트리 (예정)
- 힙과 우선순위 큐 (예정)
- 그래프 표현 (예정)
- set과 집합 연산 (예정)
- 자료구조 선택 기준 (예정)
<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Mapping Types (dict)](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict)
- [CPython dict implementation (GitHub)](https://github.com/python/cpython/blob/main/Objects/dictobject.c)
- [Real Python — Dictionaries in Python](https://realpython.com/python-dicts/)
- [Hash Table — Wikipedia](https://en.wikipedia.org/wiki/Hash_table)

Tags: Python, 자료구조, dict, 해시 테이블, Hash Table
