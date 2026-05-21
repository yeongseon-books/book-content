---
series: data-structures-101
episode: 8
title: "Data Structures 101 (8/10): 힙"
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
  - 힙
  - 우선순위 큐
  - heapq
  - 정렬
seo_description: 최소값과 최대값을 빠르게 추출하는 힙의 구조와 배열 기반 구현 방법, 파이썬 heapq 사용법 및 우선순위 큐 활용 사례를 상세히 다룹니다.
last_reviewed: '2026-05-12'
---

# Data Structures 101 (8/10): 힙

이 글은 Data Structures 101 시리즈의 여덟 번째 글입니다.

## 먼저 던지는 질문

- 힙 불변식과 완전 이진 트리는 어떤 관계일까요?
- 힙은 왜 배열 하나만으로 표현할 수 있을까요?
- 삽입(sift up)과 삭제(sift down)는 어떻게 동작할까요?

## 큰 그림

![Data Structures 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-101/08/08-01-heap-array-mapping.ko.png)

*Data Structures 101 8장 흐름 개요*

## 왜 중요한가

힙은 작업 스케줄링, 다익스트라 알고리즘, 이벤트 시뮬레이션, 외부 정렬의 핵심입니다. BST가 정렬된 데이터를 다루는 범용 트리라면, 힙은 양 극단만 빠르게 꺼내는 데 집중한 특화 구조입니다.

> 힙은 우선순위 큐의 사실상 표준 구현입니다.

## 핵심 한눈에 보기

> 힙은 완전 이진 트리이기 때문에 빈 칸 없이 배열에 담을 수 있습니다. 그래서 부모·자식 관계를 포인터가 아니라 인덱스 계산만으로 찾을 수 있고, 메모리 효율도 좋습니다.

### 힙 배열 매핑

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| 최소 힙 | 부모 ≤ 자식 |
| 최대 힙 | 부모 ≥ 자식 |
| 완전 이진 트리 | 마지막 레벨을 제외하면 모두 차 있고, 마지막도 왼쪽부터 채워지는 이진 트리 |
| sift up | 새 원소를 부모와 비교하며 위로 올리는 과정 |
| sift down | 루트 원소를 더 작은 자식과 바꾸며 아래로 내리는 과정 |

## 전후 비교

**Before — sort on every insert:**

```python
events = []
def add(event):
    events.append(event)
    events.sort()

def pop_next():
    return events.pop(0)
# Insert O(n log n), pop O(n)
```

**After — use a heap:**

```python
import heapq
events = []
def add(event):
    heapq.heappush(events, event)

def pop_next():
    return heapq.heappop(events)
# Insert and pop are both O(log n)
```

모든 원소를 항상 정렬해 둘 필요는 없습니다. “다음에 꺼낼 하나”만 빠르게 보장하면 되는 문제라면 힙이 더 정확한 선택입니다.

## 단계별로 따라하기

### 1단계: 힙 직접 구현

```python
class MinHeap:
    def __init__(self):
        self._data = []

    def push(self, value):
        self._data.append(value)
        self._sift_up(len(self._data) - 1)

    def pop(self):
        if not self._data:
            raise IndexError("pop from empty heap")
        top = self._data[0]
        last = self._data.pop()
        if self._data:
            self._data[0] = last
            self._sift_down(0)
        return top

    def _sift_up(self, i):
        while i > 0:
            parent = (i - 1) // 2
            if self._data[i] < self._data[parent]:
                self._data[i], self._data[parent] = self._data[parent], self._data[i]
                i = parent
            else:
                break

    def _sift_down(self, i):
        n = len(self._data)
        while True:
            left, right = 2 * i + 1, 2 * i + 2
            smallest = i
            if left < n and self._data[left] < self._data[smallest]:
                smallest = left
            if right < n and self._data[right] < self._data[smallest]:
                smallest = right
            if smallest == i:
                break
            self._data[i], self._data[smallest] = self._data[smallest], self._data[i]
            i = smallest

h = MinHeap()
for v in [5, 3, 8, 1, 9, 2]:
    h.push(v)

result = []
while h._data:
    result.append(h.pop())
print(result)   # [1, 2, 3, 5, 8, 9]
```

push는 끝에 붙인 뒤 위로 올리고, pop은 마지막 원소를 루트에 올린 뒤 아래로 내립니다. 둘 다 트리 높이만큼만 움직이므로 O(log n)입니다.

### 2단계: 파이썬 힙 큐 모듈

```python
import heapq

heap = []
for v in [5, 3, 8, 1, 9, 2]:
    heapq.heappush(heap, v)

print(heap)                      # internal array (the tree representation)
print(heapq.heappop(heap))       # 1
print(heapq.heappop(heap))       # 2

# k smallest / largest
import heapq
data = [5, 3, 8, 1, 9, 2, 7]
print(heapq.nsmallest(3, data))   # [1, 2, 3]
print(heapq.nlargest(3, data))    # [9, 8, 7]
```

`heapq`는 최소 힙만 제공합니다. 최대 힙이 필요하면 값을 음수로 바꿔 넣고 꺼낼 때 다시 되돌리는 방식이 흔합니다.

### 3단계: 우선순위 큐로 사용하기

```python
import heapq
from itertools import count

queue = []
tie_breaker = count()

def schedule(priority, task):
    heapq.heappush(queue, (priority, next(tie_breaker), task))

schedule(0, "critical alert")
schedule(2, "nightly batch")
schedule(1, "retry failed payment")
schedule(0, "page on-call")
schedule(1, "retry webhook")

order = []
while queue:
    priority, _, task = heapq.heappop(queue)
    order.append((priority, task))

print(order)

expected = [
    (0, "critical alert"),
    (0, "page on-call"),
    (1, "retry failed payment"),
    (1, "retry webhook"),
    (2, "nightly batch"),
]
print(f"order matches expectation: {order == expected}")

# [
#   (0, 'critical alert'),
#   (0, 'page on-call'),
#   (1, 'retry failed payment'),
#   (1, 'retry webhook'),
#   (2, 'nightly batch'),
# ]
# order matches expectation: True
```

이제 예제가 실제 스케줄러에 더 가까워졌습니다. 출력 순서가 다르면 우선순위 방향을 거꾸로 잡았거나, tie-break 카운터를 빼먹었거나, 큐 안의 항목을 제자리에서 바꿔 힙 불변식을 깨뜨렸을 가능성이 큽니다.

### 4단계: 힙화 - 배열을 한 번에 힙으로 만들기

```python
import heapq

data = [5, 3, 8, 1, 9, 2, 7]
heapq.heapify(data)   # O(n) — sift down from the leaves backward
print(data)            # [1, 3, 2, 5, 9, 8, 7]
```

빈 힙에 하나씩 넣으면 O(n log n)이지만, 이미 배열이 있다면 `heapify` 한 번이 O(n)입니다. 대량 초기 적재에서는 이 차이가 중요합니다.

### 5단계: 힙 정렬

```python
import heapq

def heap_sort(data):
    h = data[:]
    heapq.heapify(h)
    return [heapq.heappop(h) for _ in range(len(h))]

print(heap_sort([5, 3, 8, 1, 9, 2, 7]))
# [1, 2, 3, 5, 7, 8, 9]
```

힙 정렬은 전체적으로 O(n log n)입니다. 평균 성능은 퀵정렬보다 느릴 수 있지만, 최악도 O(n log n)을 보장한다는 장점이 있습니다.

## 이 코드에서 주목할 점

- 완전 이진 트리는 배열에 빈 칸 없이 들어가므로 메모리 효율이 좋습니다.
- 힙은 정렬 구조가 아니라 부분 순서 구조입니다.
- `heapify`가 O(n)이라는 사실은 힙의 가장 우아한 성질 중 하나입니다.
- BST가 전체 정렬을 다룬다면, 힙은 양 극단만 관리합니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 힙을 정렬된 구조로 착각함 | 인덱스 접근 결과가 기대와 다름 | “가장 작은 값만 빠르다”는 점을 기억합니다 |
| `heapq`로 최대 힙을 직접 기대함 | 동작이 반대가 됨 | 값을 음수로 넣거나 래퍼를 씁니다 |
| tie-break를 넣지 않음 | 비교 불가능 객체에서 오류 발생 | 카운터를 추가합니다 |
| 힙으로 임의 검색까지 해결하려 함 | 검색은 O(n) | 검색이 많으면 BST나 dict를 씁니다 |
| `heapify` 없이 반복 push만 함 | O(n log n) 비용을 냄 | 초기 배열이 있으면 `heapify`를 사용합니다 |

## 실무에서는 이렇게 쓰입니다

- 다익스트라 최단 경로는 우선순위 큐 없이는 비실용적입니다.
- 운영체제 스케줄러와 작업 큐는 다음 작업 선정을 위해 힙을 사용합니다.
- 이벤트 기반 시뮬레이션은 시간 순서 이벤트 큐를 힙으로 관리합니다.
- 일부 메모리 할당기는 크기 기준 free block 관리를 위해 힙을 씁니다.
- A* 탐색, 허프만 코딩, 외부 병합 정렬도 힙에 크게 의존합니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 “다음으로 처리할 가장 작은 것 또는 가장 큰 것”이라는 패턴이 보이면 곧바로 힙을 떠올립니다. 전체 정렬이라는 더 무거운 도구를 습관처럼 들고 오지 않습니다. 동시에 tie-break, 안정성, 우선순위 변경 가능성 같은 세부 요구를 먼저 확인합니다.

또한 “상위 k개만 필요한가, 전체가 필요한가”를 구분합니다. 백만 개 중 상위 10개만 필요하다면 전체 정렬은 과합니다. 자료구조와 알고리즘을 함께 보면 이런 선택이 훨씬 명확해집니다.

## 체크리스트

- [ ] 힙 불변식과 완전 이진 트리의 의미를 설명할 수 있습니다
- [ ] 부모와 자식 인덱스 공식을 알고 있습니다
- [ ] sift up, sift down, 시간 복잡도를 이해했습니다
- [ ] `heapq`가 최소 힙만 제공한다는 점을 알고 있습니다
- [ ] 힙과 BST 중 무엇을 선택해야 할지 기준이 있습니다

## 연습 문제

1. 위 `MinHeap`을 비교 함수 기반으로 일반화해 최소 힙과 최대 힙을 모두 구현해 보세요.

2. 최소 힙과 최대 힙 두 개를 이용해 스트림의 중앙값을 O(log n) 갱신으로 유지해 보세요.

3. 백만 개 정수에서 가장 큰 100개를 찾는 세 가지 방법 — 전체 정렬, `heapq.nlargest`, 크기 100의 최소 힙 유지 — 을 구현하고 시간을 비교해 보세요.

## 정리 및 다음 단계

힙은 완전 이진 트리를 배열에 빈 칸 없이 담아, 양 극단을 빠르게 다루는 데 특화된 구조입니다. 삽입과 삭제는 O(log n), `heapify`는 O(n)이며, 우선순위 큐의 사실상 표준 구현입니다. 임의 키 검색은 O(n)이므로 BST나 dict와는 목적이 분명히 다릅니다. 작업 스케줄링, 최단 경로, 이벤트 시뮬레이션처럼 “다음 차례”를 빨리 골라야 하는 시스템의 기본 도구입니다.

다음 글에서는 관계 표현의 가장 일반적인 형태인 그래프를 봅니다. 트리는 그래프의 특수한 경우이며, 그래프의 표현 방식과 기본 순회 알고리즘을 함께 다루겠습니다.


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

힙은 최솟값 또는 최댓값을 빠르게 꺼내는 데 최적화되어 있습니다. 다만 중간 원소 삭제나 임의 탐색은 비효율적이므로, 요구사항이 바뀌면 힙 하나로 모든 문제를 해결하려 하지 않는 것이 좋습니다. 우선순위 큐의 목적을 분명히 하고 다른 구조와 조합하는 설계를 권장합니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.



### 운영에서 다시 확인할 기준

힙은 최솟값 또는 최댓값을 빠르게 꺼내는 데 최적화되어 있습니다. 다만 중간 원소 삭제나 임의 탐색은 비효율적이므로, 요구사항이 바뀌면 힙 하나로 모든 문제를 해결하려 하지 않는 것이 좋습니다. 우선순위 큐의 목적을 분명히 하고 다른 구조와 조합하는 설계를 권장합니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.



### 운영에서 다시 확인할 기준

힙은 최솟값 또는 최댓값을 빠르게 꺼내는 데 최적화되어 있습니다. 다만 중간 원소 삭제나 임의 탐색은 비효율적이므로, 요구사항이 바뀌면 힙 하나로 모든 문제를 해결하려 하지 않는 것이 좋습니다. 우선순위 큐의 목적을 분명히 하고 다른 구조와 조합하는 설계를 권장합니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.



### 운영에서 다시 확인할 기준

힙은 최솟값 또는 최댓값을 빠르게 꺼내는 데 최적화되어 있습니다. 다만 중간 원소 삭제나 임의 탐색은 비효율적이므로, 요구사항이 바뀌면 힙 하나로 모든 문제를 해결하려 하지 않는 것이 좋습니다. 우선순위 큐의 목적을 분명히 하고 다른 구조와 조합하는 설계를 권장합니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.



### 운영에서 다시 확인할 기준

힙은 최솟값 또는 최댓값을 빠르게 꺼내는 데 최적화되어 있습니다. 다만 중간 원소 삭제나 임의 탐색은 비효율적이므로, 요구사항이 바뀌면 힙 하나로 모든 문제를 해결하려 하지 않는 것이 좋습니다. 우선순위 큐의 목적을 분명히 하고 다른 구조와 조합하는 설계를 권장합니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.



### 운영에서 다시 확인할 기준

힙은 최솟값 또는 최댓값을 빠르게 꺼내는 데 최적화되어 있습니다. 다만 중간 원소 삭제나 임의 탐색은 비효율적이므로, 요구사항이 바뀌면 힙 하나로 모든 문제를 해결하려 하지 않는 것이 좋습니다. 우선순위 큐의 목적을 분명히 하고 다른 구조와 조합하는 설계를 권장합니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.



### 운영에서 다시 확인할 기준

힙은 최솟값 또는 최댓값을 빠르게 꺼내는 데 최적화되어 있습니다. 다만 중간 원소 삭제나 임의 탐색은 비효율적이므로, 요구사항이 바뀌면 힙 하나로 모든 문제를 해결하려 하지 않는 것이 좋습니다. 우선순위 큐의 목적을 분명히 하고 다른 구조와 조합하는 설계를 권장합니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.



### 운영에서 다시 확인할 기준

힙은 최솟값 또는 최댓값을 빠르게 꺼내는 데 최적화되어 있습니다. 다만 중간 원소 삭제나 임의 탐색은 비효율적이므로, 요구사항이 바뀌면 힙 하나로 모든 문제를 해결하려 하지 않는 것이 좋습니다. 우선순위 큐의 목적을 분명히 하고 다른 구조와 조합하는 설계를 권장합니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.

## 처음 질문으로 돌아가기

- **힙 불변식과 완전 이진 트리는 어떤 관계일까요?**
  - 본문의 기준은 힙를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **힙은 왜 배열 하나만으로 표현할 수 있을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **삽입(sift up)과 삭제(sift down)는 어떻게 동작할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Structures 101 (1/10): 자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [Data Structures 101 (2/10): 배열과 동적 배열](./02-arrays-and-dynamic-arrays.md)
- [Data Structures 101 (3/10): 연결 리스트](./03-linked-lists.md)
- [Data Structures 101 (4/10): 스택과 큐](./04-stacks-and-queues.md)
- [Data Structures 101 (5/10): 해시 테이블](./05-hash-tables.md)
- [Data Structures 101 (6/10): 트리](./06-trees.md)
- [Data Structures 101 (7/10): 이진 탐색 트리](./07-binary-search-trees.md)
- **힙 (현재 글)**
- 그래프 (예정)
- 자료구조 선택 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Data Structures 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/data-structures-101/ko)

- [Open Data Structures — Heaps](https://opendatastructures.org/ods-python/10_Heaps.html)
- [Python `heapq` documentation](https://docs.python.org/3/library/heapq.html)
- [Wikipedia — Binary Heap](https://en.wikipedia.org/wiki/Binary_heap)
- [Wikipedia — Priority Queue](https://en.wikipedia.org/wiki/Priority_queue)

Tags: Computer Science, 자료구조, 힙, 우선순위 큐, heapq, 정렬
