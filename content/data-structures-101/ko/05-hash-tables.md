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


![Data Structures 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-101/05/05-01-big-picture.ko.png)
*Data Structures 101 5장 흐름 개요*

## 먼저 던지는 질문

- 해시 함수는 어떤 역할을 하며, 좋은 해시 함수는 무엇이 다를까요?
- 충돌은 왜 생기고 어떤 방식으로 해결할 수 있을까요?
- 부하율(load factor)과 리해싱은 어떤 관계일까요?

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

## 전후 비교

**Before — searching keys with a list:**

```python
users = [(1, "Alice"), (2, "Bob"), (3, "Carol"), ...]   # one million entries

def find(uid):
    for k, v in users:
        if k == uid:
            return v
    return None
# 평균 O(n)
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

### 3단계: 개방 주소법

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
# 나쁜 hash function: 항상 같은 값을 반환
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
# mutable object를 dict key로 사용하면 어떻게 될까?
key = [1, 2, 3]
try:
    {key: "value"}    # TypeError: unhashable type: 'list'
except TypeError as e:
    print(f"error: {e}")

# tuple은 immutable이라 key로 사용 가능
print({(1, 2, 3): "value"})

# frozenset도 사용 가능
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


## 구현 관점 보강: 복잡도와 선택 기준

자료구조를 비교할 때는 평균 시간 복잡도만으로 결론을 내리면 정확도가 떨어집니다. 실제 시스템에서는 데이터 분포, 갱신 비율, 메모리 제약, 동시성 요구가 동시에 작동하기 때문입니다. 따라서 아래 표처럼 연산별 상한과 운영 조건을 함께 보는 기준이 필요합니다.

| 구조 | 조회 | 삽입 | 삭제 | 메모리 특성 | 적합한 상황 |
| --- | --- | --- | --- | --- | --- |
| 배열/동적 배열 | O(1) 인덱스, O(n) 탐색 | 끝 O(1) amortized, 중간 O(n) | 중간 O(n) | 연속 메모리, 캐시 효율 우수 | 읽기 중심, 랜덤 액세스 필요 |
| 연결 리스트 | O(n) | 노드 위치 확보 시 O(1) | 노드 위치 확보 시 O(1) | 포인터 오버헤드 큼 | 중간 삽입/삭제 빈번 |
| 해시 테이블 | 평균 O(1), 최악 O(n) | 평균 O(1) | 평균 O(1) | 버킷/재해시 비용 존재 | 키 기반 빠른 조회 |
| 균형 트리 | O(log n) | O(log n) | O(log n) | 포인터 구조, 정렬 유지 | 범위 질의, 순서 보존 |

구현 단계에서는 연산 정의를 코드 시그니처로 먼저 고정하는 방식이 안전합니다. 예를 들어 `insert`, `remove`, `contains`, `iterate`의 사전/사후 조건을 먼저 문서화하고, 그 뒤에 내부 저장 구조를 바꾸면 테스트 재사용성이 크게 올라갑니다. 같은 인터페이스에 배열 기반 구현과 링크 기반 구현을 각각 붙여 벤치마크하면, 개념 설명에서 보던 복잡도 표가 실제 지연 시간으로 어떻게 드러나는지 확인할 수 있습니다.

또한 사용 사례 비교는 데이터 흐름 단위로 해야 합니다. 예를 들어 이벤트 로그 파이프라인에서는 "대량 append + 배치 스캔" 패턴이 많아 동적 배열이 유리하지만, 작업 스케줄러에서는 "우선순위 갱신 + 최소값 추출"이 반복되어 힙이 더 적합합니다. 반대로 온라인 추천 시스템의 피처 저장소는 키 조회 비율이 매우 높아 해시 기반 구조가 기본 선택이 됩니다.

실습 팁으로는 동일한 입력 집합에 대해 최소 두 가지 구조를 구현하고, 다음 항목을 비교 기록하는 방식이 좋습니다: (1) 연산당 평균 지연 시간, (2) p95 지연 시간, (3) 메모리 사용량, (4) 구현 복잡도. 이 네 가지를 같이 보면 단순 Big-O 표기법이 놓치는 현실 제약까지 반영한 결정을 내릴 수 있습니다.

실무 적용 관점에서는 입력 데이터의 크기뿐 아니라 업데이트 패턴, 동시 접근, 메모리 상한을 함께 고려해 구조를 선택해야 안정적인 성능이 나옵니다.


## 실전 앵커: 구현과 복잡도 검증

개념을 정확히 이해하려면 설명 문장만 보는 것으로는 부족합니다. 손으로 구현하고, 연산 단위를 측정하고, 메모리 배치를 눈으로 그려 보는 과정이 함께 있어야 합니다. 아래 앵커는 이 시리즈 전체에서 공통으로 재사용할 수 있는 검증 틀입니다.

### 파이썬 미니 구현 묶음

```python
from collections import deque

# 1) 리스트: 끝 append/pop은 빠르고, 앞쪽 연산은 느립니다.
arr = []
arr.append(10)
arr.append(20)
arr.pop()

# 2) 스택: list로 LIFO 구현
stack = []
stack.append('A')
stack.append('B')
stack.pop()

# 3) 큐: deque로 FIFO 구현
queue = deque()
queue.append('job-1')
queue.append('job-2')
queue.popleft()

# 4) 트리 노드
class Node:
    def __init__(self, key, left=None, right=None):
        self.key = key
        self.left = left
        self.right = right

# 5) 그래프 인접 리스트와 너비 우선 탐색
graph = {
    'A': ['B', 'C'],
    'B': ['D'],
    'C': ['D'],
    'D': []
}

def bfs(start):
    seen = {start}
    q = deque([start])
    order = []
    while q:
        cur = q.popleft()
        order.append(cur)
        for nxt in graph[cur]:
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return order
```

### 연산 복잡도 비교표

| 구조 | 핵심 연산 | 평균 시간 | 최악 시간 | 메모리 관찰 포인트 |
| --- | --- | --- | --- | --- |
| 동적 배열 | 인덱스 조회 | O(1) | O(1) | 연속 메모리, 캐시 친화적 |
| 동적 배열 | 중간 삽입/삭제 | O(n) | O(n) | 이동 비용이 성능 병목 |
| 스택 | push/pop | O(1) | O(1) | 한쪽 끝 연산으로 단순 |
| 큐(덱) | enqueue/dequeue | O(1) | O(1) | 양 끝 연산이 안정적 |
| 트리(균형) | 탐색/삽입/삭제 | O(log n) | O(log n) | 높이 유지가 관건 |
| 그래프 | 순회(BFS/DFS) | O(V+E) | O(V+E) | 정점/간선 수에 비례 |

### 메모리 배치 그림

```text
동적 배열
[0][1][2][3][4]  (연속 주소)
  |  |  |  |
  +-- 인덱스로 즉시 접근

연결 리스트
[값|다음] -> [값|다음] -> [값|다음]
   ^ 포인터를 따라 이동

트리
        [8]
       /   \
     [3]   [10]
     / \
   [1] [6]

그래프(인접 리스트)
A: B, C
B: D
C: D
D: (없음)
```

### 문제 연결 지도

| 유형 | 대표 문제 | 이 글의 관점으로 보는 핵심 |
| --- | --- | --- |
| 배열/투포인터 | LeetCode 1, 88, 283 | 인덱스 이동과 덮어쓰기 비용 관리 |
| 스택 | LeetCode 20, 155, 739 | 상태를 되돌릴 때 LIFO가 자연스러운가 |
| 큐/BFS | LeetCode 102, 994, 542 | 레벨 단위 확산과 최단 거리 |
| 트리 | LeetCode 104, 226, 236 | 재귀와 반복 중 호출 깊이 제어 |
| 그래프 | LeetCode 200, 207, 417 | 방문 집합 설계와 순회 순서 |

실무에서 성능 이슈가 발생하면, 먼저 연산을 위 표의 행으로 대응시켜 병목을 분류한 뒤 구현을 교체하는 순서로 접근하는 편이 안전합니다.


### 운영에서 다시 확인할 기준

해시 테이블의 핵심은 평균 O(1) 자체보다 충돌 관리 정책입니다. 로드 팩터 임계값을 언제 넘는지, 리사이즈가 어떤 트래픽 구간에서 실행되는지, 키 분포가 편향되어 있는지 확인하지 않으면 성능 예측이 빗나갑니다. 운영 데이터로 버킷 분포를 점검하는 루틴을 두는 것이 좋습니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

해시 테이블의 핵심은 평균 O(1) 자체보다 충돌 관리 정책입니다. 로드 팩터 임계값을 언제 넘는지, 리사이즈가 어떤 트래픽 구간에서 실행되는지, 키 분포가 편향되어 있는지 확인하지 않으면 성능 예측이 빗나갑니다. 운영 데이터로 버킷 분포를 점검하는 루틴을 두는 것이 좋습니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

해시 테이블의 핵심은 평균 O(1) 자체보다 충돌 관리 정책입니다. 로드 팩터 임계값을 언제 넘는지, 리사이즈가 어떤 트래픽 구간에서 실행되는지, 키 분포가 편향되어 있는지 확인하지 않으면 성능 예측이 빗나갑니다. 운영 데이터로 버킷 분포를 점검하는 루틴을 두는 것이 좋습니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

해시 테이블의 핵심은 평균 O(1) 자체보다 충돌 관리 정책입니다. 로드 팩터 임계값을 언제 넘는지, 리사이즈가 어떤 트래픽 구간에서 실행되는지, 키 분포가 편향되어 있는지 확인하지 않으면 성능 예측이 빗나갑니다. 운영 데이터로 버킷 분포를 점검하는 루틴을 두는 것이 좋습니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

해시 테이블의 핵심은 평균 O(1) 자체보다 충돌 관리 정책입니다. 로드 팩터 임계값을 언제 넘는지, 리사이즈가 어떤 트래픽 구간에서 실행되는지, 키 분포가 편향되어 있는지 확인하지 않으면 성능 예측이 빗나갑니다. 운영 데이터로 버킷 분포를 점검하는 루틴을 두는 것이 좋습니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

해시 테이블의 핵심은 평균 O(1) 자체보다 충돌 관리 정책입니다. 로드 팩터 임계값을 언제 넘는지, 리사이즈가 어떤 트래픽 구간에서 실행되는지, 키 분포가 편향되어 있는지 확인하지 않으면 성능 예측이 빗나갑니다. 운영 데이터로 버킷 분포를 점검하는 루틴을 두는 것이 좋습니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

해시 테이블의 핵심은 평균 O(1) 자체보다 충돌 관리 정책입니다. 로드 팩터 임계값을 언제 넘는지, 리사이즈가 어떤 트래픽 구간에서 실행되는지, 키 분포가 편향되어 있는지 확인하지 않으면 성능 예측이 빗나갑니다. 운영 데이터로 버킷 분포를 점검하는 루틴을 두는 것이 좋습니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

해시 테이블의 핵심은 평균 O(1) 자체보다 충돌 관리 정책입니다. 로드 팩터 임계값을 언제 넘는지, 리사이즈가 어떤 트래픽 구간에서 실행되는지, 키 분포가 편향되어 있는지 확인하지 않으면 성능 예측이 빗나갑니다. 운영 데이터로 버킷 분포를 점검하는 루틴을 두는 것이 좋습니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.

## 처음 질문으로 돌아가기

- **해시 함수는 어떤 역할을 하며, 좋은 해시 함수는 무엇이 다를까요?**
  - 해시 함수는 키를 정수로 바꾼 뒤 `hash(key) % capacity`로 버킷 인덱스를 정하게 해 주는 출발점입니다. 좋은 해시 함수는 키를 여러 슬롯에 고르게 퍼뜨려서, `BadHash` 예제처럼 모든 값이 한 버킷에 몰려 평균 O(1)이 무너지는 일을 줄입니다.
- **충돌은 왜 생기고 어떤 방식으로 해결할 수 있을까요?**
  - 버킷 수는 유한하므로 서로 다른 키가 같은 인덱스로 가는 충돌은 피할 수 없습니다. 본문은 버킷 안에 `(key, value)`를 리스트로 이어 붙이는 체이닝과, 빈 슬롯을 찾을 때까지 앞으로 이동하는 개방 주소법 두 방식을 직접 코드로 보여 주었습니다.
- **부하율(load factor)과 리해싱은 어떤 관계일까요?**
  - `HashTable2`는 `(size + 1) / capacity > 0.75`가 되면 배열 크기를 두 배로 늘리고 모든 키를 다시 배치합니다. 리해싱은 한 번은 비싸지만 자주 일어나지 않아 평균 삽입 비용을 낮게 유지하고, 동시에 버킷이 지나치게 붐벼 탐색이 느려지는 것을 막아 줍니다.

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

- [Data Structures 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/data-structures-101/ko)

- [Open Data Structures — Hash Tables](https://opendatastructures.org/ods-python/5_Hash_Tables.html)
- [CPython dictobject.c source](https://github.com/python/cpython/blob/main/Objects/dictobject.c)
- [Wikipedia — Hash Table](https://en.wikipedia.org/wiki/Hash_table)
- [Raymond Hettinger — Modern Python Dictionaries (PyCon 2017)](https://www.youtube.com/watch?v=npw4s1QTmPg)

Tags: Computer Science, 자료구조, 해시 테이블, 해시 함수, 충돌 해결, 파이썬 dict
