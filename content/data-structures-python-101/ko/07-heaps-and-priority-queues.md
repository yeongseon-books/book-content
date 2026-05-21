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


## Python 구현 보강: 타입 힌트와 검증 루틴

Python에서 자료구조를 학습할 때는 동작 예시만 확인하는 단계에서 멈추지 않고, 타입 힌트와 최소 검증 루틴을 함께 작성해야 설계 의도가 명확해집니다. 특히 `TypeVar`, `Generic`, `Protocol`을 사용하면 자료구조 API의 입력/출력 계약을 코드 차원에서 드러낼 수 있습니다. 아래 예시는 여러 글에서 재사용할 수 있는 기본 인터페이스 패턴입니다.

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Iterable, Iterator, Optional, TypeVar

T = TypeVar("T")

@dataclass
class Node(Generic[T]):
    value: T
    next: Optional["Node[T]"] = None

class Container(Generic[T]):
    def __init__(self, items: Optional[Iterable[T]] = None) -> None:
        self._size = 0
        self._head: Optional[Node[T]] = None
        if items is not None:
            for item in items:
                self.push(item)

    def push(self, value: T) -> None:
        self._head = Node(value=value, next=self._head)
        self._size += 1

    def pop(self) -> T:
        if self._head is None:
            raise IndexError("empty container")
        node = self._head
        self._head = node.next
        self._size -= 1
        return node.value

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[T]:
        cur = self._head
        while cur is not None:
            yield cur.value
            cur = cur.next
```

이 패턴의 핵심은 세 가지입니다. 첫째, 공개 메서드의 타입을 먼저 확정하여 구현 교체 비용을 낮춥니다. 둘째, 예외 조건(`IndexError`)을 명시해 호출자 책임을 분리합니다. 셋째, `__iter__`, `__len__` 같은 파이썬 데이터 모델 메서드를 제공해 표준 라이브러리와 자연스럽게 결합합니다.

성능 확인은 `timeit` 단일 숫자보다 시나리오 기반으로 진행하는 편이 정확합니다. 예를 들어 "1만 건 push 후 1만 건 pop", "임의 키 5천 건 조회", "중복 원소 30% 포함 집합 연산"처럼 입력 특성을 고정하고 결과를 비교합니다. 또한 `mypy`나 `pyright`로 정적 타입 검사를 돌리면 API 오용을 조기에 발견할 수 있습니다.

마지막으로 학습 기록에는 "왜 이 구현을 선택했는가"를 반드시 남깁니다. 같은 기능을 `list`, `deque`, 사용자 정의 클래스 중 무엇으로 표현했는지와 그 이유를 적어두면, 이후 코드베이스에서 자료구조를 교체해야 할 때 판단 근거를 재사용할 수 있습니다.

실무 코드에서는 `TypeVar` 기반 제네릭 API를 유지하고, `pytest`로 빈 입력/최대 입력/중복 입력 경계 조건을 검증해 구현 신뢰도를 높입니다.


## 처음 질문으로 돌아가기

- **가장 작은 값이나 가장 큰 값을 빠르게 꺼내려면 어떤 구조가 필요할까요?**
  - 본문의 기준은 힙과 우선순위 큐를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **힙은 왜 정렬보다 우선순위 처리에 유리할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Python의 `heapq`는 왜 최소 힙만 제공할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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

Tags: Python, 자료구조, Heap, Priority Queue, heapq
