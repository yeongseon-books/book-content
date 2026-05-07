---
series: data-structures-101
episode: 5
title: 해시 테이블
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
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
seo_description: 해시 테이블이 평균 O(1) 검색을 어떻게 달성하는지, 충돌과 리해싱 전략을 직접 구현하며 살펴봅니다.
last_reviewed: '2026-05-04'
---

# 해시 테이블

> Data Structures 101 시리즈 (5/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 1조 개의 키 중에서 하나를 찾는 데에도 평균 한 번의 연산이면 끝나는 자료구조가 있다면 믿어지나요?

> 해시 테이블은 키를 정수 인덱스로 변환하는 해시 함수를 사용해 배열에 직접 접근하는 자료구조입니다. 평균 시간 복잡도가 O(1)이라는 놀라운 성능을 보여 주지만, 충돌·리해싱·해시 함수의 품질 같은 미묘한 문제를 정확히 다뤄야 합니다. 이 글에서는 해시 테이블의 동작 원리, 두 가지 충돌 해결 전략(체이닝·개방 주소법), 그리고 파이썬 dict의 내부 구현 아이디어를 살펴봅니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 해시 함수의 역할과 좋은 해시 함수의 조건
- 충돌(collision)이 발생하는 이유와 해결 방법
- 부하율(load factor)과 리해싱(rehashing)의 관계
- 파이썬 dict와 set이 내부적으로 동작하는 방식

## 왜 중요한가

해시 테이블은 거의 모든 프로그래밍 언어의 표준 라이브러리에 들어가 있습니다. 파이썬의 dict/set, 자바의 HashMap, 자바스크립트의 Object/Map. 데이터베이스 인덱스, 캐시 시스템, 컴파일러의 심볼 테이블이 모두 해시 테이블을 사용합니다. 시간 복잡도가 평균 O(1)이라는 사실 하나로 컴퓨터과학의 많은 알고리즘이 가능해집니다.

> dict가 없으면 알고리즘 문제 풀이의 절반은 풀기 어렵습니다.

## 개념 한눈에 보기

> 해시 테이블은 "키 → 해시값 → 인덱스"의 두 단계 변환을 거쳐 배열의 특정 위치로 이동합니다. 두 키가 같은 인덱스로 매핑되는 충돌은 체이닝(연결 리스트)이나 개방 주소법(다음 빈 칸 탐색)으로 해결합니다.

```text
"apple" → hash() → 17234... → % 8 → 2
"banana" → hash() → 89123... → % 8 → 7

인덱스: 0  1  2  3  4  5  6  7
배열:  [ ][ ][ap][ ][ ][ ][ ][ba]

충돌 발생 시 (체이닝)
인덱스 2: ["apple", 1] → ["apricot", 5]
```

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| 해시 함수(hash function) | 키를 정수로 변환하는 함수 |
| 버킷(bucket) | 배열의 한 칸 |
| 충돌(collision) | 서로 다른 키가 같은 인덱스로 매핑되는 현상 |
| 부하율(load factor) | (저장된 항목 수) / (배열 크기) |
| 리해싱(rehashing) | 부하율이 높아지면 더 큰 배열로 옮기는 작업 |

## Before / After

**Before — 리스트로 키 검색:**

```python
users = [(1, "Alice"), (2, "Bob"), (3, "Carol"), ...]   # 100만 개

def find(uid):
    for k, v in users:
        if k == uid:
            return v
    return None
# 평균 O(n)
```

**After — dict로 키 검색:**

```python
users = {1: "Alice", 2: "Bob", 3: "Carol", ...}

def find(uid):
    return users.get(uid)
# 평균 O(1)
```

## 실습: 단계별로 따라하기

### 1단계: 가장 단순한 해시 테이블 (체이닝)

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

각 버킷은 키-값 쌍의 리스트입니다. 충돌이 일어나면 같은 버킷에 추가합니다.

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

부하율이 0.75를 넘으면 배열을 두 배로 키우고 모든 키를 다시 해싱합니다. 비싸지만 가끔 일어나므로 분할 상환 O(1)을 유지합니다.

### 3단계: 개방 주소법 (선형 탐사)

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

체이닝 대신 충돌 시 다음 빈 칸을 찾아갑니다. 캐시 친화성은 더 좋지만 삭제가 까다롭습니다(`_DELETED` 표시 필요).

### 4단계: 좋은 해시 함수의 영향

```python
# 나쁜 해시 함수: 항상 같은 값을 반환
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
print(f"나쁜 해시: {(time.perf_counter() - start) * 1000:.0f} ms")

good_set = set()
start = time.perf_counter()
for i in range(5000):
    good_set.add(i)
print(f"좋은 해시: {(time.perf_counter() - start) * 1000:.0f} ms")
```

모든 키가 같은 버킷으로 들어가면 해시 테이블이 사실상 연결 리스트가 됩니다. O(1)이 O(n)으로 무너집니다.

### 5단계: 가변 객체는 키로 쓸 수 없다

```python
# 가변 객체를 dict 키로 쓰면 어떻게 될까
key = [1, 2, 3]
try:
    {key: "value"}    # TypeError: unhashable type: 'list'
except TypeError as e:
    print(f"오류: {e}")

# tuple은 불변이라 키로 쓸 수 있음
print({(1, 2, 3): "value"})

# frozenset도 가능
print({frozenset({1, 2}): "value"})
```

해시 테이블은 키의 해시가 변하지 않는다고 가정합니다. 가변 객체를 키로 쓰면 같은 객체를 다시 찾을 수 없게 됩니다.

## 이 코드에서 주목할 점

- 해시 테이블의 평균 O(1)은 "좋은 해시 함수 + 적절한 부하율"이라는 전제 위에 있습니다
- 충돌은 피할 수 없으며, 어떻게 처리하느냐가 자료구조의 성격을 결정합니다
- 리해싱은 비싸지만 분할 상환되므로 평균은 여전히 O(1)입니다
- 개방 주소법은 캐시 친화성이 좋고, 체이닝은 부하율 한계가 더 유연합니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 가변 객체를 키로 사용 | TypeError 또는 키 분실 | tuple, frozenset 사용 |
| `__hash__`만 정의 | `__eq__` 없으면 충돌 처리 실패 | 둘 다 함께 정의 |
| 해시 충돌 가정 안 함 | 최악 O(n) 무시 | 해시 품질을 검증 |
| 순서 의존 | dict 순서를 키 순으로 가정 | 명시적 정렬 사용 |
| 부하율 무시 | 메모리 낭비 또는 성능 저하 | 0.5~0.75 부근 유지 |

## 실무에서는 이렇게 쓰입니다

- 데이터베이스의 해시 인덱스는 동등 비교 검색을 O(1)에 처리합니다
- 캐시(Redis, Memcached)는 키-값 저장소로 해시 테이블을 사용합니다
- 컴파일러/인터프리터의 심볼 테이블은 해시 테이블입니다
- 중복 제거, 빈도 계산(Counter), 그룹화(groupby)는 모두 dict 기반
- 분산 시스템의 일관된 해싱(consistent hashing)은 노드 분산에 필수

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 dict를 "사실상 무료"인 자료구조처럼 사용하지만, 보안이 민감한 곳에서는 다르게 생각합니다. 해시 충돌 공격(hash flooding)으로 서비스를 마비시킬 수 있다는 사실을 알기 때문입니다. 그래서 신뢰할 수 없는 입력은 해시 키로 직접 쓰지 않거나, SipHash 같은 키-인지 해시 함수를 사용합니다.

또한 시니어는 dict의 순서 보장(파이썬 3.7+)을 안다고 해서 그것에 의존하는 비즈니스 로직을 만들지 않습니다. 명시적 순서가 필요하면 `OrderedDict`나 정렬된 컬렉션을 사용합니다. 자료구조의 우연한 속성에 의존하면 미래의 자신을 곤란하게 만듭니다.

## 체크리스트

- [ ] 해시 함수가 무엇을 하고 왜 필요한지 설명할 수 있는가
- [ ] 충돌이 왜 일어나며 어떻게 해결하는지 두 가지 방법을 알고 있는가
- [ ] 부하율과 리해싱의 관계를 이해했는가
- [ ] 가변 객체를 키로 쓸 수 없는 이유를 알고 있는가
- [ ] 평균 O(1)과 최악 O(n)의 차이를 인지했는가

## 연습 문제

1. 위 `HashTable`에 `delete(key)` 메서드를 구현해 보세요. 체이닝에서는 단순하지만 개방 주소법에서는 어떤 점이 까다로울까요?

2. 문자열 빈도수를 세는 두 가지 코드를 작성해 보세요. 하나는 dict로, 다른 하나는 list로 구현하고 100만 단어 입력에서 시간을 비교합니다.

3. 자신만의 클래스를 dict 키로 쓰려면 어떤 메서드를 구현해야 할까요? 잘못 구현했을 때 어떤 버그가 생길지 예상해 봅니다.

## 정리 및 다음 단계

해시 테이블은 키를 정수 인덱스로 변환해서 배열에 직접 접근하는 자료구조이며, 평균 O(1)이라는 압도적인 검색 성능을 제공합니다. 좋은 해시 함수, 적절한 부하율 관리, 충돌 해결 전략이 이 성능의 비결입니다. 다만 정렬된 순회나 범위 질의에는 약하고, 최악의 경우 O(n)으로 떨어질 수 있다는 한계도 인지해야 합니다.

다음 글에서는 계층 구조를 자연스럽게 표현하는 자료구조인 트리를 살펴봅니다. 파일 시스템, DOM, 조직도 등 거의 모든 계층적 데이터의 기본 골격이 됩니다.

<!-- toc:begin -->
- [자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [배열과 동적 배열](./02-arrays-and-dynamic-arrays.md)
- [연결 리스트](./03-linked-lists.md)
- [스택과 큐](./04-stacks-and-queues.md)
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
