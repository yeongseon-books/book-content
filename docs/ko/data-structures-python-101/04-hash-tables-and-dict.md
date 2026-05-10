---
series: data-structures-python-101
episode: 4
title: 해시 테이블과 dict
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
  - 자료구조
  - dict
  - 해시 테이블
  - Hash Table
seo_description: Python dict의 해시 테이블 구현 원리와 성능 특성을 설명합니다.
last_reviewed: '2026-05-04'
---

# 해시 테이블과 dict

> Data Structures with Python 101 시리즈 (4/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: dict는 어떻게 수백만 개의 키 중에서 원하는 값을 즉시 찾을까요?

> dict는 내부적으로 해시 테이블로 구현됩니다. 키를 해시 함수로 변환하여 배열의 인덱스를 계산하고, 해당 위치에 값을 저장합니다. 이 글에서는 해시 테이블의 원리, dict의 내부 동작, 그리고 해시 충돌 처리 방법을 다룹니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 해시 테이블의 동작 원리
- Python dict의 내부 구현
- 해시 충돌과 해결 방법
- dict 연산별 시간 복잡도

## 왜 중요한가

dict는 Python에서 두 번째로 많이 사용하는 자료구조입니다. JSON 파싱, 설정 관리, 캐싱, 데이터 그룹핑 등 거의 모든 곳에서 dict를 사용합니다. 해시 테이블의 원리를 이해하면 dict를 더 효과적으로 사용할 수 있습니다.

> 해시 테이블은 "키 → 값" 매핑을 O(1)에 수행하는 자료구조입니다. 이 성능은 데이터 규모에 관계없이 일정합니다.

면접에서 "dict의 시간 복잡도가 왜 O(1)인가?"는 빈출 질문입니다. 해시 함수, 해시 충돌, 리사이징의 개념을 알아야 정확히 답할 수 있습니다.

## 핵심 개념 잡기

> 해시 테이블 = 키를 해시 함수로 변환하여 배열 인덱스에 매핑하는 자료구조

```
키 "alice"  → hash("alice") → 인덱스 3
키 "bob"    → hash("bob")   → 인덱스 7
키 "charlie"→ hash("charlie")→ 인덱스 1

배열:  [   |charlie|   |alice|   |   |   |bob|   ]
인덱스:  0     1     2    3    4   5   6   7   8
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 해시 함수 | 임의 크기의 데이터를 고정 크기의 정수로 변환합니다 |
| 해시 충돌 | 서로 다른 키가 같은 인덱스에 매핑되는 현상입니다 |
| 로드 팩터 | 저장된 원소 수 / 배열 크기 비율로, 높으면 충돌이 잦아집니다 |
| 리사이징 | 로드 팩터가 임계값을 넘으면 배열 크기를 늘리는 작업입니다 |
| hashable | __hash__()를 구현한 불변 객체로, dict 키로 사용 가능합니다 |

## Before / After

리스트에서 키-값을 선형 검색하는 방법과 dict로 즉시 조회하는 방법을 비교합니다.

```python
# before: 리스트 순회로 검색 — O(n)
users = [("alice", 95), ("bob", 82), ("charlie", 90)]
for name, score in users:
    if name == "charlie":
        print(score)
        break
```

```python
# after: dict로 즉시 조회 — O(1)
users = {"alice": 95, "bob": 82, "charlie": 90}
print(users["charlie"])  # 90
```

## 단계별 실습

### Step 1: dict 기본 연산

```python
scores = {}

# 삽입 — O(1)
scores["alice"] = 95
scores["bob"] = 82
scores["charlie"] = 90

# 조회 — O(1)
print(scores["alice"])      # 95
print(scores.get("diana", 0))  # 0 — 키 없으면 기본값

# 삭제 — O(1)
del scores["bob"]
print(scores)  # {'alice': 95, 'charlie': 90}

# 키 존재 확인 — O(1)
print("alice" in scores)    # True
```

### Step 2: hash() 함수 직접 확인

```python
# 불변 객체는 해시 가능
print(hash("hello"))    # 고정된 정수 (세션마다 다름)
print(hash(42))         # 42
print(hash((1, 2, 3)))  # tuple은 해시 가능

# 가변 객체는 해시 불가
try:
    hash([1, 2, 3])
except TypeError as e:
    print(f"에러: {e}")  # unhashable type: 'list'
```

### Step 3: 간단한 해시 테이블 직접 구현

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

### Step 4: defaultdict와 Counter 활용

```python
from collections import defaultdict, Counter

# defaultdict: 없는 키에 접근하면 기본값 자동 생성
word_count = defaultdict(int)
for word in "the cat sat on the mat".split():
    word_count[word] += 1
print(dict(word_count))
# {'the': 2, 'cat': 1, 'sat': 1, 'on': 1, 'mat': 1}

# Counter: 빈도 세기 전용
counter = Counter("the cat sat on the mat".split())
print(counter.most_common(2))  # [('the', 2), ('cat', 1)]
```

### Step 5: dict comprehension과 정렬

```python
scores = {"alice": 95, "bob": 82, "charlie": 90, "diana": 88}

# dict comprehension
high_scores = {k: v for k, v in scores.items() if v >= 90}
print(high_scores)  # {'alice': 95, 'charlie': 90}

# 값 기준 정렬
sorted_scores = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
print(sorted_scores)
# {'alice': 95, 'charlie': 90, 'diana': 88, 'bob': 82}
```

## 이 코드에서 주목할 점

- dict의 조회, 삽입, 삭제는 평균 O(1)이지만 최악의 경우 O(n)입니다
- hash() 결과는 Python 세션마다 달라집니다 (보안을 위한 해시 랜덤화)
- 가변 객체(list, dict, set)는 해시할 수 없어 dict 키로 사용할 수 없습니다
- Python 3.7부터 dict는 삽입 순서를 보장합니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 없는 키에 `d[key]`로 접근 | KeyError가 발생합니다 | `d.get(key, default)` 또는 `key in d` 검사를 사용합니다 |
| list를 dict 키로 사용 | TypeError — list는 해시 불가합니다 | tuple로 변환하여 사용합니다 |
| dict 순회 중 키 추가/삭제 | RuntimeError가 발생합니다 | `list(d.keys())`로 복사 후 순회합니다 |
| dict 비교 시 순서 의존 | dict 비교는 순서와 무관하지만 혼동하기 쉽습니다 | `==` 연산자로 비교하면 순서와 무관하게 동작합니다 |
| 중첩 dict 수정 시 기본값 누락 | KeyError가 발생합니다 | defaultdict(dict) 또는 setdefault()를 사용합니다 |

## 실무에서 이렇게 쓰입니다

- JSON 응답을 dict로 파싱하여 데이터를 추출합니다
- 환경 변수와 설정을 dict로 관리합니다
- 캐시를 dict로 구현하여 중복 계산을 방지합니다
- 로그 데이터를 Counter로 집계합니다
- API 파라미터를 dict로 전달합니다

## 현업 개발자는 이렇게 생각합니다

dict는 Python의 핵심입니다. 모듈, 클래스, 인스턴스의 속성이 모두 dict로 관리됩니다. dict의 성능 특성을 이해하면 Python 자체를 더 깊이 이해할 수 있습니다.

실무에서는 dict보다 dataclass나 Pydantic 모델을 사용하여 구조화된 데이터를 표현하는 추세입니다. 하지만 내부적으로는 모두 dict에 기반하므로, dict의 동작 원리를 아는 것이 기본입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **해시 가능성** — 키는 hashable이어야 한다는 점을 항상 확인합니다.
- **최악 O(n)** — 충돌 시 최악 비용도 인지합니다.
- **setdefault/defaultdict** — 초기화 패턴을 단순화합니다.
- **Counter** — 빈도 계산은 Counter가 가장 명료합니다.
- **순서 보장** — 3.7+ dict는 삽입 순서를 보장한다는 점을 활용합니다.

## 체크리스트

- [ ] 해시 테이블의 동작 원리를 설명할 수 있다
- [ ] dict의 조회, 삽입, 삭제 시간 복잡도를 말할 수 있다
- [ ] hashable 객체와 unhashable 객체를 구분할 수 있다
- [ ] defaultdict와 Counter를 활용할 수 있다
- [ ] dict comprehension으로 데이터를 변환할 수 있다

## 연습 문제

1. 문자열 리스트에서 각 문자열의 빈도를 dict로 세는 함수를 작성하세요. (Counter 사용 금지)
2. 두 dict의 키가 모두 같은지 확인하는 함수를 작성하세요.
3. 중첩 dict `{"a": {"b": {"c": 1}}}`에서 `"a.b.c"` 형식의 점 표기법으로 값을 조회하는 함수를 작성하세요.

## 정리 및 다음 글 안내

dict는 해시 테이블로 구현되어 O(1) 조회를 제공합니다. 해시 함수, 충돌, hashable 개념을 이해하면 dict를 더 효과적으로 사용할 수 있습니다. 다음 글에서는 배열과 다른 방식으로 데이터를 연결하는 연결 리스트를 다룹니다.

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
