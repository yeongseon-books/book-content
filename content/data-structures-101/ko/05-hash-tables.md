---
series: data-structures-101
episode: 5
title: "Data Structures 101 (5/10): 해시 테이블"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - 자료구조
  - 해시 테이블
  - 해시 함수
  - 충돌 해결
  - 파이썬 dict
seo_description: 해시 테이블의 O(1) 탐색, 충돌 처리, dict 내부 아이디어를 설명합니다.
last_reviewed: '2026-05-12'
---

# Data Structures 101 (5/10): 해시 테이블

이 글은 Data Structures 101 시리즈의 다섯 번째 글입니다.

## 먼저 던지는 질문

- 해시 함수는 어떤 역할을 하며, 좋은 해시 함수는 무엇이 다를까요?
- 충돌은 왜 생기고 어떤 방식으로 해결할 수 있을까요?
- 부하율(load factor)과 리해싱은 어떤 관계일까요?

## 큰 그림

![Data Structures 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-101/05/05-01-big-picture.ko.png)

*Data Structures 101 5장 흐름 개요*

이 그림에서는 해시 테이블를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 해시 테이블의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

해시 테이블은 거의 모든 언어의 표준 라이브러리에 들어 있습니다. 파이썬의 `dict`, 자바의 `HashMap`, 자바스크립트의 `Map` 모두 같은 계열입니다. 캐시, 심볼 테이블, 해시 인덱스도 이 구조 위에서 설명됩니다.

> dict가 없으면 알고리즘 문제의 절반은 갑자기 훨씬 어려워집니다.

## 핵심 한눈에 보기

> 해시 테이블은 “key → hash value → index”라는 두 단계 변환을 거칩니다. 두 키가 같은 슬롯으로 들어오면 체이닝으로 연결하거나, open addressing으로 다음 빈 슬롯을 탐색해 충돌을 해결합니다.

```text
"apple" → hash() → 17234... → % 8 → 2
"banana" → hash() → 89123... → % 8 → 7

index: 0  1  2  3  4  5  6  7
array:[ ][ ][ap][ ][ ][ ][ ][ba]

When a collision occurs (chaining)
index 2: ["apple", 1] → ["apricot", 5]
```

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| 해시 함수 | 키를 정수로 매핑하는 함수 |
| 버킷 | 내부 배열의 한 슬롯 |
| 충돌 | 서로 다른 키가 같은 인덱스로 가는 현상 |
| 부하율 | 저장된 원소 수 / 배열 크기 |
| 리해싱 | 더 큰 배열로 옮기며 모든 키를 다시 배치하는 과정 |

## Before / After

**Before — searching keys with a list:**

```python
users = [(1, "Alice"), (2, "Bob"), (3, "Carol"), ...]   # one million entries

def find(uid):
    for k, v in users:
        if k == uid:
            return v
    return None
# average O(n)
```

**After — searching keys with a dict:**

```text
users = {1: "Alice", 2: "Bob", 3: "Carol", ...}

def find(uid):
    return users.get(uid)
# average O(1)
```

이 차이는 데이터가 커질수록 더 절대적이 됩니다. 검색이 핵심인 시스템에서 해시 테이블이 기본 선택이 되는 이유입니다.

## 단계별로 따라하기

### 1단계: 최소 해시 테이블 구현 — 체이닝

```python
class HashTable:
    def __init__(self, capacity=8):
        self._capacity = capacity
        self._size = 0
        self._buckets = [[] for _ in range(capacity)]

    def _index(self, key):
        return hash(key) % self._capacity

    def put(self, key, value):
        bucket = self._buckets[self._index(key)]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self._size += 1

    def get(self, key):
        for k, v in self._buckets[self._index(key)]:
            if k == key:
                return v
        raise KeyError(key)

h = HashTable()
h.put("apple", 1); h.put("banana", 2)
print(h.get("apple"))   # 1
```

각 버킷은 키-값 쌍의 리스트입니다. 충돌이 나면 같은 버킷 뒤에 이어 붙입니다.

### 2단계: 부하율과 리해싱

```python
class HashTable2(HashTable):
    LOAD_FACTOR_LIMIT = 0.75

    def put(self, key, value):
        if (self._size + 1) / self._capacity > self.LOAD_FACTOR_LIMIT:
            self._rehash(self._capacity * 2)
        super().put(key, value)

    def _rehash(self, new_capacity):
        old = [(k, v) for bucket in self._buckets for k, v in bucket]
        self._capacity = new_capacity
        self._buckets = [[] for _ in range(new_capacity)]
        self._size = 0
        for k, v in old:
            super().put(k, v)

h = HashTable2(capacity=4)
for i in range(10):
    h.put(f"key{i}", i)
    print(f"size={h._size}, capacity={h._capacity}")
```

부하율이 0.75를 넘으면 배열을 두 배로 늘리고 모두 다시 배치합니다. 비싸지만 자주 일어나지 않기 때문에 평균 비용은 O(1)로 유지됩니다.

### 3단계: Open Addressing

```python
class OpenAddressTable:
    _EMPTY = object()
    _DELETED = object()

    def __init__(self, capacity=8):
        self._capacity = capacity
        self._slots = [self._EMPTY] * capacity
        self._size = 0

    def _probe(self, key):
        idx = hash(key) % self._capacity
        for _ in range(self._capacity):
            slot = self._slots[idx]
            if slot is self._EMPTY or (slot is not self._DELETED and slot[0] == key):
                return idx
            idx = (idx + 1) % self._capacity
        raise RuntimeError("table full")

    def put(self, key, value):
        idx = self._probe(key)
        if self._slots[idx] is self._EMPTY:
            self._size += 1
        self._slots[idx] = (key, value)

t = OpenAddressTable()
t.put("a", 1); t.put("b", 2)
```

체이닝 대신 다음 빈 칸을 찾아갑니다. 캐시 친화성은 좋아지지만 삭제 처리가 까다로워져 `_DELETED` 같은 마커가 필요합니다.

### 4단계: 해시 함수 품질의 영향

```python
# Bad hash function: always returns the same value
class BadHash:
    def __init__(self, val):
        self.val = val
    def __hash__(self):
        return 0
    def __eq__(self, other):
        return self.val == other.val

import time

bad_set = set()
start = time.perf_counter()
for i in range(5000):
    bad_set.add(BadHash(i))
print(f"bad hash: {(time.perf_counter() - start) * 1000:.0f} ms")

good_set = set()
start = time.perf_counter()
for i in range(5000):
    good_set.add(i)
print(f"good hash: {(time.perf_counter() - start) * 1000:.0f} ms")
```

모든 키가 한 버킷으로 몰리면 해시 테이블은 사실상 연결 리스트가 됩니다. 평균 O(1)은 해시 품질이 받쳐 줄 때만 성립합니다.

### 5단계: 가변 객체는 키가 될 수 없다

```python
# What happens if you use a mutable object as a dict key?
key = [1, 2, 3]
try:
    {key: "value"}    # TypeError: unhashable type: 'list'
except TypeError as e:
    print(f"error: {e}")

# A tuple is immutable, so it works as a key
print({(1, 2, 3): "value"})

# A frozenset works too
print({frozenset({1, 2}): "value"})
```

해시 테이블은 키의 해시 값이 바뀌지 않는다고 가정합니다. 키가 변하면 다시 찾을 수 없게 되므로, 가변 객체는 기본적으로 키로 쓸 수 없습니다.

## 이 코드에서 주목할 점

- 평균 O(1)은 좋은 해시 함수와 적절한 부하율 위에 서 있습니다.
- 충돌은 피할 수 없고, 이를 어떻게 처리하느냐가 구조의 성격을 만듭니다.
- 리해싱은 비싸지만 분할 상환되므로 평균 비용은 여전히 낮습니다.
- open addressing은 캐시 친화적이고, 체이닝은 높은 부하율에서도 비교적 유연합니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 가변 객체를 키로 사용함 | `TypeError` 또는 키 유실 | tuple, frozenset 같은 불변 타입을 사용합니다 |
| `__hash__`만 정의함 | 충돌 처리 시 동등성 판단이 깨짐 | `__hash__`와 `__eq__`를 함께 정의합니다 |
| 충돌 가능성을 무시함 | 최악 O(n)을 놓침 | 해시 품질과 입력 특성을 검토합니다 |
| dict 순서를 키 순서로 착각함 | 정렬 의미가 깨짐 | 필요하면 명시적으로 정렬합니다 |
| 부하율을 신경 쓰지 않음 | 메모리 낭비 또는 성능 저하 | 0.5~0.75 부근을 의식합니다 |

## 실무에서는 이렇게 쓰입니다

- 데이터베이스 해시 인덱스는 동등 비교 조회를 빠르게 처리합니다.
- Redis, Memcached 같은 캐시는 해시 테이블 기반 키-값 저장소입니다.
- 컴파일러와 인터프리터의 심볼 테이블도 해시 테이블입니다.
- 중복 제거, 빈도 집계, 그룹화는 대부분 dict 기반으로 작성됩니다.
- 분산 시스템은 consistent hashing으로 키를 여러 노드에 분산합니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 dict를 거의 공짜 자원처럼 쓰되, 보안 민감한 맥락에서는 해시 플러딩을 먼저 떠올립니다. 신뢰할 수 없는 입력을 그대로 키로 쓰는 서비스는 공격 표면이 될 수 있다는 점을 알고 있습니다.

또한 파이썬 3.7+의 dict가 삽입 순서를 보장한다는 사실과, 비즈니스 로직이 그 성질에 기대면 위험하다는 사실을 동시에 압니다. 순서가 정말 중요하면 정렬 컬렉션이나 명시적 구조를 선택합니다.

## 체크리스트

- [ ] 해시 함수가 무엇을 하는지 설명할 수 있습니다
- [ ] 충돌 해결 전략 두 가지와 각각의 특성을 알고 있습니다
- [ ] 부하율과 리해싱의 관계를 이해했습니다
- [ ] 가변 객체를 키로 쓸 수 없는 이유를 설명할 수 있습니다
- [ ] 평균 O(1)과 최악 O(n)을 구분할 수 있습니다

## 연습 문제

1. 위 `HashTable`에 `delete(key)`를 추가해 보세요. 체이닝에서는 비교적 단순한데, open addressing에서는 무엇이 까다로운지 함께 정리해 보세요.

2. 단어 빈도를 세는 코드를 dict 버전과 list 버전으로 각각 작성해 보세요. 백만 단어 입력에서 얼마나 차이 나는지 비교해 보세요.

3. 사용자 정의 클래스를 dict 키로 쓰려면 어떤 메서드를 구현해야 할까요? 잘못 구현하면 어떤 버그가 생길까요?

## 정리 및 다음 단계

해시 테이블은 키를 정수 인덱스로 바꿔 배열로 점프함으로써 평균 O(1) 조회를 제공합니다. 비결은 좋은 해시 함수, 적절한 부하율 관리, 충돌 해결 전략입니다. 대신 정렬 순회나 범위 질의에는 약하고, 최악의 경우 O(n)으로 무너질 수 있다는 한계도 함께 이해해야 합니다.

다음 글에서는 계층 구조를 자연스럽게 표현하는 트리를 봅니다. 파일 시스템, DOM, 조직도처럼 관계가 위에서 아래로 펼쳐지는 데이터의 기본 골격입니다.

## 처음 질문으로 돌아가기

- **해시 함수는 어떤 역할을 하며, 좋은 해시 함수는 무엇이 다를까요?**
  - 본문의 기준은 해시 테이블를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **충돌은 왜 생기고 어떤 방식으로 해결할 수 있을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **부하율(load factor)과 리해싱은 어떤 관계일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Structures 101 (1/10): 자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [Data Structures 101 (2/10): 배열과 동적 배열](./02-arrays-and-dynamic-arrays.md)
- [Data Structures 101 (3/10): 연결 리스트](./03-linked-lists.md)
- [Data Structures 101 (4/10): 스택과 큐](./04-stacks-and-queues.md)
- **해시 테이블 (현재 글)**
- 트리 (예정)
- 이진 탐색 트리 (예정)
- 힙 (예정)
- 그래프 (예정)
- 자료구조 선택 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Open Data Structures — Hash Tables](https://opendatastructures.org/ods-python/5_Hash_Tables.html)
- [CPython dictobject.c source](https://github.com/python/cpython/blob/main/Objects/dictobject.c)
- [Wikipedia — Hash Table](https://en.wikipedia.org/wiki/Hash_table)
- [Raymond Hettinger — Modern Python Dictionaries (PyCon 2017)](https://www.youtube.com/watch?v=npw4s1QTmPg)

Tags: Computer Science, 자료구조, 해시 테이블, 해시 함수, 충돌 해결, 파이썬 dict
