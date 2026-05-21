---
series: data-structures-101
episode: 2
title: "Data Structures 101 (2/10): 배열과 동적 배열"
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
  - 배열
  - 동적 배열
  - 메모리
  - 파이썬 리스트
seo_description: 메모리 연속 배치와 인덱싱의 원리, 동적 배열의 확장 전략 및 분할 상환 비용 분석을 통해 배열 자료구조의 핵심을 상세히 다룹니다.
last_reviewed: '2026-05-12'
---

# Data Structures 101 (2/10): 배열과 동적 배열

이 글은 Data Structures 101 시리즈의 두 번째 글입니다.


![Data Structures 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-101/02/02-01-big-picture.ko.png)
*Data Structures 101 2장 흐름 개요*

## 먼저 던지는 질문

- 고정 배열은 왜 인덱싱이 O(1)일까요?
- 동적 배열은 공간이 모자랄 때 어떻게 늘어나고, 왜 append가 평균적으로 빠를까요?
- 파이썬의 `list`는 내부적으로 어떤 자료구조에 가까울까요?

## 왜 중요한가

배열은 가장 기본적이면서도 가장 빠른 자료구조 중 하나입니다. CPU 캐시와 궁합이 좋고, 인덱싱은 O(1)이며, 해시 테이블·힙·동적 배열 같은 구조도 내부적으로는 배열 위에 세워집니다.

> 배열을 깊이 이해하지 못하면 다른 자료구조도 끝까지 깊게 이해하기 어렵습니다.

이 글에서는 “값을 여러 개 담는 컨테이너” 수준에서 멈추지 않고, 메모리 배치·재할당·캐시 친화성까지 함께 봅니다.

## 핵심 한눈에 보기

> 배열은 메모리의 연속 구간입니다. `arr[i]`는 시작 주소 + `i × 원소 크기`로 계산하므로 O(1)입니다. 동적 배열은 capacity가 부족해지면 보통 두 배 큰 블록을 새로 할당하고 기존 값을 복사합니다.

```text
Fixed array (size = 5)
addr: 100 104 108 112 116
val:  [10][20][30][40][50]
       ↑
  arr[2] = 100 + 2*4 = 108

Dynamic array (size = 3, capacity = 4)
val:  [10][20][30][ - ]   one slot free
append(40) → [10][20][30][40]   capacity full
append(50) → new block (capacity 8) → [10][20][30][40][50][ ][ ][ ]
```

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| 고정 배열 | 생성 시 크기가 고정되는 배열 |
| 동적 배열 | 필요할 때 크기를 늘릴 수 있는 배열 |
| 용량(capacity) | 현재 확보된 최대 저장 공간 |
| 재할당(reallocation) | 더 큰 블록을 새로 잡고 원소를 복사하는 과정 |
| 분할 상환 비용 | 여러 번의 연산 전체를 평균냈을 때의 비용 |

## 전후 비교

**Before — building a list with `+`:**

```python
result = []
for i in range(1_000_000):
    result = result + [i]   # O(n) copy each time → O(n^2) overall
```

**After — using append:**

```python
result = []
for i in range(1_000_000):
    result.append(i)        # amortized O(1) → O(n) overall
```

겉보기에는 비슷해도 비용 구조는 완전히 다릅니다. 실무에서는 이런 차이가 수백 배에서 수천 배까지 벌어집니다.

## 단계별로 따라하기

### 1단계: 인덱싱은 정말 상수 시간일까

```python
import time

data = list(range(10_000_000))

start = time.perf_counter()
_ = data[0]
print(f"data[0]:        {(time.perf_counter() - start) * 1e6:.2f} us")

start = time.perf_counter()
_ = data[5_000_000]
print(f"data[5_000_000]: {(time.perf_counter() - start) * 1e6:.2f} us")

start = time.perf_counter()
_ = data[9_999_999]
print(f"data[-1]:        {(time.perf_counter() - start) * 1e6:.2f} us")
```

세 위치 모두 비슷한 시간이 나옵니다. 배열 인덱싱은 스캔이 아니라 주소 계산이기 때문입니다.

### 2단계: 동적 배열 확장을 직접 구현해 보기

```python
class DynamicArray:
    def __init__(self):
        self._capacity = 1
        self._size = 0
        self._data = [None] * self._capacity

    def append(self, value):
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        self._data[self._size] = value
        self._size += 1

    def _resize(self, new_cap):
        new_data = [None] * new_cap
        for i in range(self._size):
            new_data[i] = self._data[i]
        self._data = new_data
        self._capacity = new_cap

    def __getitem__(self, i):
        if not 0 <= i < self._size:
            raise IndexError(i)
        return self._data[i]

    def __len__(self):
        return self._size

arr = DynamicArray()
for i in range(10):
    arr.append(i)
    print(f"size={len(arr)}, capacity={arr._capacity}")
```

capacity가 1, 2, 4, 8, 16처럼 증가하는 모습을 볼 수 있습니다. 이 doubling 전략이 append의 평균 비용을 낮게 유지하는 핵심입니다.

### 3단계: 분할 상환 비용 이해하기

```python
# Count the total copies during n appends
copies = 0
size = 0
capacity = 1

for _ in range(1024):
    if size == capacity:
        copies += size       # copy old elements to the new block
        capacity *= 2
    size += 1

print(f"total appends: {size}, total copies: {copies}")
print(f"average: {copies / size:.2f}")
```

평균 복사 횟수는 1보다 작습니다. 대부분의 append는 빈 슬롯에 값을 쓰기만 하고, 가끔만 비싼 resize를 치릅니다.

### 4단계: 중간과 앞쪽 삽입은 왜 비쌀까

```python
import time

data = list(range(100_000))

start = time.perf_counter()
data.append(-1)              # append at the end: O(1)
print(f"append: {(time.perf_counter() - start) * 1e6:.2f} us")

data = list(range(100_000))
start = time.perf_counter()
data.insert(0, -1)           # insert at the front: O(n)
print(f"insert(0): {(time.perf_counter() - start) * 1e6:.2f} us")
```

앞에 삽입하면 뒤 원소를 전부 한 칸씩 밀어야 합니다. 이런 패턴이 핵심이라면 연결 리스트나 deque가 더 잘 맞습니다.

### 5단계: 캐시 친화성

```python
import time

# Sum the same one million integers
list_data = list(range(1_000_000))

start = time.perf_counter()
total = 0
for x in list_data:
    total += x
print(f"list iteration: {(time.perf_counter() - start) * 1000:.2f} ms")

# Compare with a dict — slower
dict_data = {i: i for i in range(1_000_000)}

start = time.perf_counter()
total = 0
for v in dict_data.values():
    total += v
print(f"dict iteration: {(time.perf_counter() - start) * 1000:.2f} ms")
```

연속 메모리는 CPU 캐시 라인에 잘 실립니다. 그래서 원소 수가 같아도 list 순회가 dict보다 유리한 경우가 많습니다.

## 이 코드에서 주목할 점

- 인덱싱은 주소 계산이므로 위치와 무관하게 O(1)입니다.
- doubling 전략 덕분에 append의 분할 상환 비용이 O(1)로 유지됩니다.
- 중간이나 앞쪽 삽입은 구조적으로 O(n)입니다.
- 연속 메모리는 캐시 친화적이라 실제 벤치마크에서도 강합니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| `+`로 리스트를 반복 확장함 | O(n^2) 복사 폭발 | `append`나 컴프리헨션을 사용합니다 |
| 앞쪽 삽입을 자주 함 | 매번 O(n) 이동 발생 | `collections.deque`를 사용합니다 |
| capacity와 size를 혼동함 | 메모리 추정이 틀어짐 | size는 사용량, capacity는 확보량으로 구분합니다 |
| 큰 슬라이스를 반복 생성함 | 메모리와 시간이 낭비됨 | 가능하면 슬라이스 대신 인덱스를 씁니다 |
| 정렬된 리스트를 선형 탐색함 | O(log n) 기회를 버림 | `bisect`를 검토합니다 |

## 실무에서는 이렇게 쓰입니다

- NumPy `ndarray`는 C 레벨의 배열 모델로 수치 계산을 가속합니다.
- Pandas 열(column)은 내부적으로 연속 배열 기반입니다.
- 파일 I/O 버퍼, 네트워크 패킷, 이미지 픽셀 데이터는 모두 배열적 성격이 강합니다.
- 게임 엔진의 ECS는 캐시 친화성을 위해 배열을 적극 활용합니다.
- 컬럼형 데이터베이스는 정렬된 배열처럼 스캔하고 압축합니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 “list”와 “array”를 같은 말로 뭉뚱그리지 않습니다. 파이썬의 `list`는 동적 배열 계열이지만, 다른 언어의 컬렉션은 전혀 다른 의미를 가질 수 있기 때문입니다. `ArrayList`, `std::vector`, `Vec`는 한 가족이지만 `LinkedList`는 성격이 완전히 다릅니다.

또한 최종 크기를 안다면 capacity를 미리 확보합니다. `[None] * n`처럼 한 번에 메모리를 잡으면 재할당 비용을 모두 제거할 수 있습니다. 작은 차이처럼 보여도 핫패스에서는 체감 성능 차이가 분명합니다.

## 체크리스트

- [ ] 배열 인덱싱이 왜 O(1)인지 메모리 배치로 설명할 수 있습니다
- [ ] doubling과 분할 상환 비용의 관계를 이해했습니다
- [ ] capacity와 size를 구분할 수 있습니다
- [ ] 앞쪽 삽입이 왜 비싼지 알고 있습니다
- [ ] 캐시 친화성이 성능에 미치는 영향을 이해했습니다

## 연습 문제

1. 위 `DynamicArray`에 `pop()`과 `__delitem__()`을 추가해 보세요. size가 capacity의 1/4 아래로 떨어지면 절반으로 줄이는 축소 전략도 함께 넣어 보세요.

2. 백만 번 `append`하는 방식과 `[None] * 1_000_000`으로 미리 할당한 뒤 인덱스로 쓰는 방식을 비교해 보세요. 차이는 얼마나 날까요?

3. 정렬된 리스트에서 `bisect.insort`의 시간 복잡도는 무엇일까요? 검색은 O(log n)인데 삽입은 왜 그렇지 않을까요?

## 정리 및 다음 단계

배열은 같은 크기의 원소를 메모리에 연속 배치하는 구조라 인덱싱이 O(1)이고 캐시 친화적입니다. 동적 배열은 공간이 부족해질 때 capacity를 키워 끝 삽입의 분할 상환 비용을 O(1)로 유지합니다. 하지만 중간이나 앞쪽 삽입은 여전히 O(n)이므로, 그런 패턴이 지배적이라면 다음 글의 연결 리스트나 deque가 더 적합할 수 있습니다.

다음 글에서는 포인터로 이어진 노드 구조인 연결 리스트를 봅니다. 배열의 “비싼 중간 삽입” 문제를 어떻게 해결하고, 대신 무엇을 포기하는지 비교하겠습니다.


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

배열 기반 구현을 운영에 적용할 때는 재할당 시점을 예측하는 습관이 중요합니다. 입력이 급증하는 시간대에 용량 확장이 겹치면 지연 시간이 순간적으로 튈 수 있습니다. 초기 용량을 예상 트래픽에 맞춰 잡고, 배치 입력 구간에는 여유 공간을 사전에 확보하면 흔들림을 줄일 수 있습니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

배열 기반 구현을 운영에 적용할 때는 재할당 시점을 예측하는 습관이 중요합니다. 입력이 급증하는 시간대에 용량 확장이 겹치면 지연 시간이 순간적으로 튈 수 있습니다. 초기 용량을 예상 트래픽에 맞춰 잡고, 배치 입력 구간에는 여유 공간을 사전에 확보하면 흔들림을 줄일 수 있습니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

배열 기반 구현을 운영에 적용할 때는 재할당 시점을 예측하는 습관이 중요합니다. 입력이 급증하는 시간대에 용량 확장이 겹치면 지연 시간이 순간적으로 튈 수 있습니다. 초기 용량을 예상 트래픽에 맞춰 잡고, 배치 입력 구간에는 여유 공간을 사전에 확보하면 흔들림을 줄일 수 있습니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

배열 기반 구현을 운영에 적용할 때는 재할당 시점을 예측하는 습관이 중요합니다. 입력이 급증하는 시간대에 용량 확장이 겹치면 지연 시간이 순간적으로 튈 수 있습니다. 초기 용량을 예상 트래픽에 맞춰 잡고, 배치 입력 구간에는 여유 공간을 사전에 확보하면 흔들림을 줄일 수 있습니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

배열 기반 구현을 운영에 적용할 때는 재할당 시점을 예측하는 습관이 중요합니다. 입력이 급증하는 시간대에 용량 확장이 겹치면 지연 시간이 순간적으로 튈 수 있습니다. 초기 용량을 예상 트래픽에 맞춰 잡고, 배치 입력 구간에는 여유 공간을 사전에 확보하면 흔들림을 줄일 수 있습니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

배열 기반 구현을 운영에 적용할 때는 재할당 시점을 예측하는 습관이 중요합니다. 입력이 급증하는 시간대에 용량 확장이 겹치면 지연 시간이 순간적으로 튈 수 있습니다. 초기 용량을 예상 트래픽에 맞춰 잡고, 배치 입력 구간에는 여유 공간을 사전에 확보하면 흔들림을 줄일 수 있습니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

배열 기반 구현을 운영에 적용할 때는 재할당 시점을 예측하는 습관이 중요합니다. 입력이 급증하는 시간대에 용량 확장이 겹치면 지연 시간이 순간적으로 튈 수 있습니다. 초기 용량을 예상 트래픽에 맞춰 잡고, 배치 입력 구간에는 여유 공간을 사전에 확보하면 흔들림을 줄일 수 있습니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

배열 기반 구현을 운영에 적용할 때는 재할당 시점을 예측하는 습관이 중요합니다. 입력이 급증하는 시간대에 용량 확장이 겹치면 지연 시간이 순간적으로 튈 수 있습니다. 초기 용량을 예상 트래픽에 맞춰 잡고, 배치 입력 구간에는 여유 공간을 사전에 확보하면 흔들림을 줄일 수 있습니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.

## 처음 질문으로 돌아가기

- **고정 배열은 왜 인덱싱이 O(1)일까요?**
  - 본문의 기준은 배열과 동적 배열를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **동적 배열은 공간이 모자랄 때 어떻게 늘어나고, 왜 append가 평균적으로 빠를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **파이썬의 `list`는 내부적으로 어떤 자료구조에 가까울까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Structures 101 (1/10): 자료구조란 무엇인가?](./01-what-are-data-structures.md)
- **배열과 동적 배열 (현재 글)**
- 연결 리스트 (예정)
- 스택과 큐 (예정)
- 해시 테이블 (예정)
- 트리 (예정)
- 이진 탐색 트리 (예정)
- 힙 (예정)
- 그래프 (예정)
- 자료구조 선택 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Data Structures 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/data-structures-101/ko)

- [Open Data Structures — Chapter 2 Array-Based Lists](https://opendatastructures.org/ods-python/2_Array_Based_Lists.html)
- [CPython listobject.c source](https://github.com/python/cpython/blob/main/Objects/listobject.c)
- [Wikipedia — Dynamic Array](https://en.wikipedia.org/wiki/Dynamic_array)
- [Python collections.deque docs](https://docs.python.org/3/library/collections.html#collections.deque)

Tags: Computer Science, 자료구조, 배열, 동적 배열, 메모리, 파이썬 리스트
