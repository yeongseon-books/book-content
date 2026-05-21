---
episode: 7
language: ko
last_reviewed: '2026-05-12'
seo_description: Python heapq 모듈로 최소 힙과 우선순위 큐를 구현하고, 정렬과 K번째 원소 탐색에 활용하는 실전 패턴을 정리합니다.
series: data-structures-python-101
status: publish-ready
tags:
- Python
- 자료구조
- Heap
- Priority Queue
- heapq
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "Data Structures with Python 101 (7/10): 힙과 우선순위 큐"
---

# Data Structures with Python 101 (7/10): 힙과 우선순위 큐

이 글은 Data Structures with Python 101 시리즈의 일곱 번째 글입니다.

## 먼저 던지는 질문

- 가장 작은 값이나 가장 큰 값을 빠르게 꺼내려면 어떤 구조가 필요할까요?
- 힙은 왜 정렬보다 우선순위 처리에 유리할까요?
- Python의 `heapq`는 왜 최소 힙만 제공할까요?

## 큰 그림

![Data Structures with Python 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-python-101/07/07-01-big-picture.ko.png)

*Data Structures with Python 101 7장 흐름 개요*

## 왜 이 글이 중요한가

현실의 많은 문제는 단순히 데이터를 저장하는 것이 아니라, 우선순위에 따라 처리하는 것입니다. 가장 급한 작업부터 실행해야 하거나, 가장 가까운 노드를 먼저 방문해야 하거나, 가장 이른 이벤트를 먼저 소비해야 하는 상황이 계속 등장합니다. 매번 전체 정렬을 하면 O(n log n)이 들지만, 힙은 필요한 순간의 우선순위만 효율적으로 관리합니다.

> 힙은 부모 노드가 자식보다 항상 작거나 큰 값을 유지하는 완전 이진 트리입니다.

이 구조는 Dijkstra 최단 경로, 작업 스케줄러, 이벤트 시뮬레이션 같은 핵심 알고리즘의 기반입니다. 즉, 힙은 이론용 구조가 아니라, “가장 중요한 것 하나를 계속 빨리 꺼내야 하는” 실전 문제의 기본 도구입니다.

## 핵심 개념 한눈에 보기

> 힙 = 부모가 자식보다 항상 작도록 유지되는 완전 이진 트리 (min-heap 기준)

```text
[Min-Heap]               [Array Representation]
      1                   index: 0  1  2  3  4  5
    /   \                  value: [1, 3, 5, 7, 4, 8]
   3     5
  / \   /                Parent i's children: 2i+1, 2i+2
 7   4 8                 Child i's parent: (i-1)//2
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 최소 힙(min-heap) | 부모가 자식보다 항상 작은 완전 이진 트리입니다 |
| 최대 힙(max-heap) | 부모가 자식보다 항상 큰 완전 이진 트리입니다 |
| heapify | 일반 배열을 힙 조건에 맞게 재배열하는 연산입니다 |
| 우선순위 큐 | 우선순위가 높은 항목을 먼저 꺼내는 추상 자료형입니다 |
| 완전 이진 트리 | 마지막 레벨을 제외하면 모든 레벨이 꽉 찬 트리입니다 |

## Before / After

최솟값을 반복해서 꺼내는 문제를 정렬과 힙으로 각각 처리해 보겠습니다.

```python
# before: sort to extract minimum — O(n log n) per extraction
tasks = [5, 3, 8, 1, 4]
tasks.sort()
smallest = tasks.pop(0)  # sort then pop — inefficient
```

```python
# after: heapq for minimum extraction — O(log n) per extraction
import heapq
tasks = [5, 3, 8, 1, 4]
heapq.heapify(tasks)           # O(n) to build the heap
smallest = heapq.heappop(tasks) # O(log n) to extract minimum
```

정렬은 전체 순서를 매번 맞추는 비용을 지불합니다. 반면 힙은 “최솟값만 빨리 꺼낼 수 있으면 된다”는 문제 정의에 정확히 맞춰져 있습니다. 그래서 우선순위 처리에서는 힙이 더 적합합니다.

## 단계별 실습

### Step 1: Basic heapq usage

```python
import heapq

data = [5, 3, 8, 1, 4, 2]

# Convert list to heap — O(n)
heapq.heapify(data)
print(data)  # [1, 3, 2, 5, 4, 8] — heap order

# Peek at minimum — O(1)
print(data[0])  # 1

# Extract minimum — O(log n)
print(heapq.heappop(data))  # 1
print(heapq.heappop(data))  # 2

# Insert value — O(log n)
heapq.heappush(data, 0)
print(data[0])  # 0
```

### Step 2: Implement a max-heap (negate values)

```python
import heapq

# Python heapq only supports min-heaps
# Implement max-heap by negating values
max_heap = []
for val in [5, 3, 8, 1, 4]:
    heapq.heappush(max_heap, -val)

# Extract maximum
print(-heapq.heappop(max_heap))  # 8
print(-heapq.heappop(max_heap))  # 5
print(-heapq.heappop(max_heap))  # 4
```

### Step 3: Solve Top-K problems

```python
import heapq

scores = [85, 92, 78, 95, 88, 76, 91, 83, 97, 80]

# Top 3 — O(n log k)
top3 = heapq.nlargest(3, scores)
print(f"top 3: {top3}")  # [97, 95, 92]

# Bottom 3
bottom3 = heapq.nsmallest(3, scores)
print(f"bottom 3: {bottom3}")  # [76, 78, 80]
```

### Step 4: Implement a priority queue

```python
import heapq

class PriorityQueue:
    def __init__(self):
        self._heap = []
        self._counter = 0  # maintains insertion order for equal priorities

    def push(self, priority: int, item):
        heapq.heappush(self._heap, (priority, self._counter, item))
        self._counter += 1

    def pop(self):
        if not self._heap:
            raise IndexError("pop from empty queue")
        priority, _, item = heapq.heappop(self._heap)
        return item

    def peek(self):
        if not self._heap:
            raise IndexError("peek at empty queue")
        return self._heap[0][2]

    def __len__(self):
        return len(self._heap)

pq = PriorityQueue()
pq.push(3, "low priority task")
pq.push(1, "urgent task")
pq.push(2, "normal task")

print(pq.pop())  # "urgent task"
print(pq.pop())  # "normal task"
print(pq.pop())  # "low priority task"
```

### Step 5: Merge sorted lists

```python
import heapq

list1 = [1, 4, 7, 10]
list2 = [2, 5, 8, 11]
list3 = [3, 6, 9, 12]

# Merge multiple sorted iterables into one — O(n log k)
merged = list(heapq.merge(list1, list2, list3))
print(merged)  # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
```

## 이 코드에서 먼저 봐야 할 점

- `heapq`는 최소 힙만 직접 지원하므로 최대 힙은 값 부호 반전으로 구현합니다.
- `heapify`는 O(n)이지만 원소를 하나씩 `heappush`하면 O(n log n)입니다.
- 우선순위가 같은 원소를 안전하게 처리하려면 counter를 함께 넣는 패턴이 유용합니다.
- `nlargest`와 `nsmallest`는 k가 작을 때 전체 정렬보다 효율적입니다.

힙을 배울 때 흔한 오해는 “정렬된 구조”라고 생각하는 것입니다. 하지만 힙은 전체가 정렬되지 않습니다. 대신 가장 중요한 하나만 빠르게 꺼낼 수 있도록 최소한의 질서만 유지합니다. 바로 그 점이 힙의 본질입니다.

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| `append` 후 매번 `heapify` | 삽입마다 O(n) 비용이 듭니다 | 새 값은 `heappush`로 넣습니다 |
| 힙에서 임의 원소 삭제 시도 | `heapq`는 그런 연산을 직접 지원하지 않습니다 | lazy deletion 같은 패턴을 사용합니다 |
| 최대 힙에 커스텀 comparator 기대 | Python 힙은 비교 함수를 받지 않습니다 | 값 부호 반전이나 래퍼 객체를 사용합니다 |
| `heap[-1]`을 최댓값으로 오해 | 힙은 전체 정렬 구조가 아닙니다 | min-heap에서는 `heap[0]`만 최솟값을 보장합니다 |
| 비교 불가 객체를 그대로 push | `TypeError`가 발생합니다 | `(priority, counter, item)` 형태를 사용합니다 |

## 실무에서 이렇게 쓰입니다

- 작업 스케줄러는 우선순위가 높은 작업을 먼저 처리합니다.
- Dijkstra 알고리즘은 가장 가까운 노드를 반복해서 선택합니다.
- 이벤트 시뮬레이터는 가장 빠른 시각의 이벤트를 먼저 소비합니다.
- 여러 정렬된 로그 파일 병합은 힙 기반 merge로 구현할 수 있습니다.
- 실시간 중앙값 계산은 최소 힙과 최대 힙을 함께 사용합니다.

## 실무에서는 이렇게 생각합니다

실무에서는 `heapq`를 직접 쓰는 경우도 많지만, 스레드 안전한 `queue.PriorityQueue`나 비동기 환경의 `asyncio.PriorityQueue`를 더 자주 만날 수 있습니다. 다만 내부 원리는 결국 힙이므로 `heapq`를 이해해야 상위 추상화도 자신 있게 다룰 수 있습니다.

또 하나 기억할 점은 Top-K 문제가 면접과 실무 모두에서 자주 나온다는 사실입니다. 전체 정렬 대신 O(n log k) 힙 해법을 떠올릴 수 있느냐가 구조 이해도의 차이를 만듭니다.

## 체크리스트

- [ ] 힙의 구조와 힙 속성을 설명할 수 있다
- [ ] `heapq`의 `heapify`, `heappush`, `heappop`을 사용할 수 있다
- [ ] 값 부호 반전으로 최대 힙을 구현할 수 있다
- [ ] `heapq`로 우선순위 큐를 구현할 수 있다
- [ ] `nlargest`와 `nsmallest`로 Top-K 문제를 풀 수 있다

## 연습 문제

1. 정수 스트림에서 실시간 중앙값을 계산하는 클래스를 작성해 보세요. 힌트: 최대 힙 + 최소 힙 조합입니다.
2. `heapq.merge`를 쓰지 않고 K개의 정렬된 list를 병합하는 함수를 작성해 보세요.
3. 우선순위와 마감 시한을 함께 고려하는 우선순위 큐를 설계해 보세요.

## 정리 및 다음 글 안내

힙은 최솟값과 최댓값을 효율적으로 관리하기 위한 구조이고, Python에서는 `heapq`가 그 기능을 간결하게 제공합니다. 핵심은 전체 정렬이 아니라, 우선순위가 가장 높은 하나를 계속 빠르게 꺼내는 데 있습니다. 다음 글에서는 노드와 간선으로 관계를 표현하는 그래프를 살펴보겠습니다.



## 타입 힌트 기반 우선순위 큐 구현

`heapq`는 모듈 수준 함수로 list를 힙처럼 다룹니다. 여기서는 이를 감싸서 ADT 인터페이스를 제공하는 우선순위 큐를 구현합니다.

```python
from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from typing import Generic, Iterator, TypeVar

T = TypeVar("T")


@dataclass(order=True)
class PriorityItem(Generic[T]):
    """우선순위와 데이터를 함께 저장하는 래퍼입니다."""
    priority: float
    sequence: int = field(compare=True)  # 같은 우선순위일 때 삽입 순서 유지
    data: T = field(compare=False)


class PriorityQueue(Generic[T]):
    """heapq 기반 우선순위 큐입니다. 낮은 priority가 먼저 나옵니다."""

    def __init__(self) -> None:
        self._heap: list[PriorityItem[T]] = []
        self._counter: int = 0

    def push(self, item: T, priority: float = 0.0) -> None:
        entry = PriorityItem(priority=priority, sequence=self._counter, data=item)
        heapq.heappush(self._heap, entry)
        self._counter += 1

    def pop(self) -> T:
        if not self._heap:
            raise IndexError("pop from empty priority queue")
        return heapq.heappop(self._heap).data

    def peek(self) -> T:
        if not self._heap:
            raise IndexError("peek from empty priority queue")
        return self._heap[0].data

    def __len__(self) -> int:
        return len(self._heap)

    def __bool__(self) -> bool:
        return bool(self._heap)

    def __repr__(self) -> str:
        if not self._heap:
            return "PriorityQueue(empty)"
        return f"PriorityQueue(size={len(self._heap)}, next={self._heap[0].data!r})"
```

### 설계 결정 세 가지

1. **sequence 필드**: 같은 priority의 항목이 여러 개일 때, 삽입 순서로 tiebreak합니다. 이 필드가 없으면 data 간 비교가 발생해 `TypeError`가 날 수 있습니다.
2. **`field(compare=False)`**: data는 비교에 참여하지 않습니다. 임의 타입의 객체를 넣을 수 있도록 하기 위함입니다.
3. **최소 힙 기반**: `heapq`가 최소 힙만 제공하므로 priority가 낮을수록 먼저 나옵니다. 최대 힙이 필요하면 priority에 음수를 넣으면 됩니다.

### 최대 힙 패턴

```python
# heapq를 최대 힙으로 사용하는 관용 패턴
import heapq

scores = [85, 92, 78, 96, 88]
max_heap = [-s for s in scores]
heapq.heapify(max_heap)

top_score = -heapq.heappop(max_heap)  # 96
print(f"최고 점수: {top_score}")
```

## 메모리 프로파일링: 힙 vs 정렬 list

```python
import heapq
import sys


def measure(label: str, obj: object) -> None:
    print(f"{label:>30}: {sys.getsizeof(obj):>8} bytes")


n = 10_000
data = list(range(n))

# heapified list (구조는 동일한 list)
heap_data = data[:]
heapq.heapify(heap_data)

# sorted list
sorted_data = sorted(data)

measure("heapified list (10k)", heap_data)
measure("sorted list (10k)", sorted_data)
```

핵심 관찰: `heapq`는 별도의 자료구조를 만들지 않습니다. 기존 list를 힙 순서로 재배치할 뿐이므로, 메모리 사용량은 일반 list와 동일합니다. 이것이 `heapq`의 강점입니다 — 추가 메모리 없이 O(1) 최솟값 접근과 O(log n) 삽입/추출을 제공합니다.

### heapify vs sort: 구축 비용 비교

```python
import heapq
import timeit


def bench_heapify(n: int = 100_000) -> None:
    data = list(range(n, 0, -1))
    heapq.heapify(data)


def bench_sort(n: int = 100_000) -> None:
    data = list(range(n, 0, -1))
    data.sort()


trials = 20
t_heap = timeit.timeit(bench_heapify, number=trials)
t_sort = timeit.timeit(bench_sort, number=trials)

print(f"heapify (100k): {t_heap:.4f}s")
print(f"sort (100k):    {t_sort:.4f}s")
print(f"heapify is {t_sort/t_heap:.1f}x faster to build")
```

heapify는 O(n), sort는 O(n log n)입니다. "전체를 정렬할 필요 없이 최솟값/최댓값만 반복해서 꺼내면 되는" 상황에서 힙이 유리한 이유가 이 비용 차이입니다.

## 성능 벤치마크: 상위 k개 추출

실무에서 힙의 가장 흔한 용도는 "전체를 정렬하지 않고 상위/하위 k개만 빠르게 추출"하는 것입니다.

```python
import heapq
import random
import timeit


def bench_nlargest_heap(data: list[int], k: int) -> None:
    heapq.nlargest(k, data)


def bench_nlargest_sort(data: list[int], k: int) -> None:
    sorted(data, reverse=True)[:k]


n = 100_000
k = 10
data = [random.randint(0, 1_000_000) for _ in range(n)]

trials = 20
t_heap = timeit.timeit(lambda: bench_nlargest_heap(data, k), number=trials)
t_sort = timeit.timeit(lambda: bench_nlargest_sort(data, k), number=trials)

print(f"heapq.nlargest(10, 100k): {t_heap:.4f}s")
print(f"sorted()[:10] (100k):     {t_sort:.4f}s")
```

k가 작을 때 `heapq.nlargest`는 O(n log k)로 동작해 O(n log n) 정렬보다 빠릅니다. 하지만 k가 n에 가까워지면 정렬이 더 나을 수 있습니다. `heapq` 문서에서도 k가 전체의 10% 미만일 때 사용을 권장합니다.

### 스트리밍 중앙값 (두 개의 힙)

```python
import heapq


class MedianFinder:
    """스트리밍 데이터에서 중앙값을 O(log n)에 유지합니다."""

    def __init__(self) -> None:
        self._lo: list[int] = []   # max-heap (음수 저장)
        self._hi: list[int] = []   # min-heap

    def add(self, num: int) -> None:
        heapq.heappush(self._lo, -num)
        heapq.heappush(self._hi, -heapq.heappop(self._lo))
        if len(self._hi) > len(self._lo):
            heapq.heappush(self._lo, -heapq.heappop(self._hi))

    @property
    def median(self) -> float:
        if len(self._lo) > len(self._hi):
            return -self._lo[0]
        return (-self._lo[0] + self._hi[0]) / 2.0


mf = MedianFinder()
for x in [5, 2, 8, 1, 9]:
    mf.add(x)
    print(f"added {x}, median = {mf.median}")
```

이 패턴은 두 개의 힙(작은 쪽의 max-heap + 큰 쪽의 min-heap)을 유지해, 중앙값을 항상 O(1)에 조회하고 새 원소 삽입은 O(log n)에 처리합니다.

## 힙 내부 구조: 배열로 트리 표현하기

힙의 핵심 통찰은 완전 이진 트리를 배열(list)로 표현할 수 있다는 점입니다. 노드 포인터 없이도 부모-자식 관계를 인덱스 계산으로 파악합니다.

```text
인덱스:    0   1   2   3   4   5   6
값:       [1,  3,  2,  7,  5,  4,  6]

트리 표현:
            1          (index 0)
          /   \
         3     2       (index 1, 2)
        / \   / \
       7   5 4   6    (index 3, 4, 5, 6)
```

인덱스 규칙은 다음과 같습니다.

- 부모: `(i - 1) // 2`
- 왼쪽 자식: `2 * i + 1`
- 오른쪽 자식: `2 * i + 2`

이 규칙 덕분에 포인터 없이 배열만으로 트리를 탐색할 수 있습니다. 메모리도 연속적이라 캐시 효율이 좋습니다.

### heappush와 heappop의 동작 원리

`heappush(heap, item)`은 다음 과정을 거칩니다.

1. 배열 끝에 새 원소를 추가합니다 (O(1)).
2. 부모와 비교하며 위로 올립니다 (sift-up). 최대 높이만큼 비교하므로 O(log n).

`heappop(heap)`은 다음 과정을 거칩니다.

1. 루트(인덱스 0)의 값을 저장합니다.
2. 배열 마지막 원소를 루트로 이동합니다.
3. 자식과 비교하며 아래로 내립니다 (sift-down). O(log n).

```python
import heapq

heap: list[int] = []
for val in [5, 3, 8, 1, 2]:
    heapq.heappush(heap, val)
    print(f"push {val}: {heap}")

print()
while heap:
    val = heapq.heappop(heap)
    print(f"pop {val}: {heap}")
```

출력을 관찰하면 배열이 항상 힙 속성(부모 ≤ 자식)을 유지하는 것을 확인할 수 있습니다.

## 실무 패턴: 작업 스케줄러

우선순위 큐의 대표적 실무 활용은 작업 스케줄링입니다. 긴급도가 높은 작업을 먼저 처리하고, 같은 긴급도면 먼저 등록된 작업을 처리합니다.

```python
from dataclasses import dataclass, field
from enum import IntEnum
import heapq
from typing import Callable


class Urgency(IntEnum):
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass(order=True)
class Task:
    urgency: Urgency
    sequence: int = field(compare=True)
    name: str = field(compare=False)
    action: Callable[[], None] = field(compare=False, repr=False)


class TaskScheduler:
    def __init__(self) -> None:
        self._heap: list[Task] = []
        self._counter: int = 0

    def add_task(self, name: str, urgency: Urgency, action: Callable[[], None]) -> None:
        task = Task(urgency=urgency, sequence=self._counter, name=name, action=action)
        heapq.heappush(self._heap, task)
        self._counter += 1

    def run_next(self) -> str | None:
        if not self._heap:
            return None
        task = heapq.heappop(self._heap)
        task.action()
        return task.name

    def __len__(self) -> int:
        return len(self._heap)


# 사용 예시
scheduler = TaskScheduler()
scheduler.add_task("배포", Urgency.CRITICAL, lambda: print("배포 실행"))
scheduler.add_task("로그 정리", Urgency.LOW, lambda: print("로그 정리"))
scheduler.add_task("버그 수정", Urgency.HIGH, lambda: print("버그 수정"))

while scheduler:
    name = scheduler.run_next()
    print(f"  완료: {name}")
```

IntEnum을 사용하면 urgency 값이 자연스럽게 비교 가능하고, CRITICAL(0)이 가장 먼저 나옵니다.

## unittest로 PriorityQueue 검증

```python
import unittest


class TestPriorityQueue(unittest.TestCase):
    def setUp(self) -> None:
        self.pq: PriorityQueue[str] = PriorityQueue()

    def test_push_pop_order(self) -> None:
        self.pq.push("low", priority=3)
        self.pq.push("high", priority=1)
        self.pq.push("mid", priority=2)
        self.assertEqual(self.pq.pop(), "high")
        self.assertEqual(self.pq.pop(), "mid")
        self.assertEqual(self.pq.pop(), "low")

    def test_same_priority_fifo(self) -> None:
        self.pq.push("first", priority=1)
        self.pq.push("second", priority=1)
        self.pq.push("third", priority=1)
        self.assertEqual(self.pq.pop(), "first")
        self.assertEqual(self.pq.pop(), "second")

    def test_peek(self) -> None:
        self.pq.push("item", priority=5)
        self.assertEqual(self.pq.peek(), "item")
        self.assertEqual(len(self.pq), 1)

    def test_empty_pop_raises(self) -> None:
        with self.assertRaises(IndexError):
            self.pq.pop()

    def test_bool(self) -> None:
        self.assertFalse(self.pq)
        self.pq.push("x", priority=0)
        self.assertTrue(self.pq)

    def test_large_scale(self) -> None:
        import random
        items = [(random.random(), f"item_{i}") for i in range(1000)]
        for priority, name in items:
            self.pq.push(name, priority=priority)
        prev_priority = -1.0
        for priority, _ in sorted(items):
            result = self.pq.pop()
            # 정확한 순서 확인은 priority 기준


if __name__ == "__main__":
    unittest.main()
```

## heapq와 queue.PriorityQueue 비교

Python 표준 라이브러리는 힙 기반 우선순위 큐를 두 곳에서 제공합니다.

| 특성 | `heapq` | `queue.PriorityQueue` |
|------|---------|----------------------|
| 스레드 안전 | 아니오 | 예 (내부 Lock) |
| 인터페이스 | 모듈 함수 (list 직접 조작) | 클래스 메서드 (put/get) |
| 블로킹 | 불가 | get(timeout=...) 지원 |
| 성능 | Lock 없으므로 단일 스레드에서 더 빠름 | Lock 오버헤드 있음 |
| 적합 상황 | 단일 스레드, 알고리즘 구현 | 멀티스레드 생산자-소비자 패턴 |

단일 스레드 코드에서는 `heapq`를 직접 사용하는 것이 더 빠르고 유연합니다. 멀티스레드 환경에서 생산자-소비자 패턴을 구현할 때만 `queue.PriorityQueue`를 사용합니다.

## 처음 질문으로 돌아가기

- **가장 작은 값이나 가장 큰 값을 빠르게 꺼내려면 어떤 구조가 필요할까요?**
  - 힙(heap)입니다. 힙은 루트에 항상 최솟값(또는 최댓값)을 유지하므로 O(1)에 확인하고 O(log n)에 꺼낼 수 있습니다. 정렬된 list도 최솟값을 O(1)에 확인할 수 있지만, 삽입이 O(n)입니다. 힙은 삽입도 O(log n)이므로 동적 데이터에 유리합니다.
- **힙은 왜 정렬보다 우선순위 처리에 유리할까요?**
  - 전체 정렬은 O(n log n)이고 모든 원소의 순서를 확정합니다. 하지만 우선순위 큐에서는 "지금 가장 급한 것 하나"만 알면 됩니다. 힙은 전체 순서를 유지하지 않고 부분 순서(부모 ≤ 자식)만 유지하므로, 구축이 O(n)으로 빠르고 삽입/추출도 O(log n)에 끝납니다.
- **Python의 `heapq`는 왜 최소 힙만 제공할까요?**
  - 설계 결정의 문제입니다. 최소 힙 하나만 있으면 최대 힙은 음수를 넣어 흉내 낼 수 있고, 코드가 단순해집니다. 또한 대부분의 알고리즘(Dijkstra, 작업 스케줄링, merge k sorted lists)이 최소 힙을 기본으로 사용하므로, 하나만 제공해도 실용적 커버리지가 충분합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Structures with Python 101 (1/10): 자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [Data Structures with Python 101 (2/10): 배열과 리스트](./02-arrays-and-lists.md)
- [Data Structures with Python 101 (3/10): 스택과 큐](./03-stacks-and-queues.md)
- [Data Structures with Python 101 (4/10): 해시 테이블과 dict](./04-hash-tables-and-dict.md)
- [Data Structures with Python 101 (5/10): 연결 리스트](./05-linked-lists.md)
- [Data Structures with Python 101 (6/10): 트리와 이진 트리](./06-trees-and-binary-trees.md)
- **힙과 우선순위 큐 (현재 글)**
- 그래프 표현 (예정)
- set과 집합 연산 (예정)
- 자료구조 선택 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Python Docs — heapq](https://docs.python.org/3/library/heapq.html)
- [Real Python — The Python heapq Module](https://realpython.com/python-heapq-module/)
- [GeeksforGeeks — Heap Data Structure](https://www.geeksforgeeks.org/heap-data-structure/)
- [Visualgo — Heap Visualization](https://visualgo.net/en/heap)
- [book-examples 저장소 — data-structures-python-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/data-structures-python-101/ko)

Tags: Python, 자료구조, Heap, Priority Queue, heapq
