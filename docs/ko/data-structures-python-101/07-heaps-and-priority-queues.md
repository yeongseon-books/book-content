---
series: data-structures-python-101
episode: 7
title: 힙과 우선순위 큐
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
  - Heap
  - Priority Queue
  - heapq
seo_description: Python heapq로 힙과 우선순위 큐를 구현하고 활용합니다.
last_reviewed: '2026-05-04'
---

# 힙과 우선순위 큐

> Data Structures with Python 101 시리즈 (7/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 항상 가장 작은(또는 큰) 값을 빠르게 꺼내려면 어떤 자료구조를 써야 할까요?

> 힙(Heap)은 최솟값 또는 최댓값을 O(1)에 조회하고 O(log n)에 삽입·삭제하는 자료구조입니다. Python의 heapq 모듈로 쉽게 사용할 수 있습니다. 이 글에서는 힙의 원리, heapq 사용법, 우선순위 큐 패턴을 다룹니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 힙의 구조와 힙 속성(heap property)
- Python heapq 모듈 사용법
- 최대 힙 구현 방법
- 우선순위 큐의 실무 활용 패턴

## 왜 중요한가

"가장 긴급한 작업부터 처리하라", "가장 가까운 노드를 먼저 방문하라"와 같은 요구사항은 어디에나 있습니다. 매번 정렬하면 O(n log n)이지만, 힙을 사용하면 O(log n)에 처리할 수 있습니다.

> 힙은 완전 이진 트리로, 부모 노드가 자식 노드보다 항상 작은(최소 힙) 또는 큰(최대 힙) 값을 가집니다.

Dijkstra 최단 경로, 작업 스케줄러, 이벤트 시뮬레이션 등 핵심 알고리즘이 힙에 기반합니다.

## 핵심 개념 잡기

> 힙 = 부모가 자식보다 항상 작은(min-heap) 완전 이진 트리

```
[최소 힙]             [배열 표현]
      1               인덱스: 0  1  2  3  4  5
    /   \              값:   [1, 3, 5, 7, 4, 8]
   3     5
  / \   /             부모 i의 자식: 2i+1, 2i+2
 7   4 8              자식 i의 부모: (i-1)//2
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 최소 힙(min-heap) | 부모가 자식보다 항상 작은 완전 이진 트리입니다 |
| 최대 힙(max-heap) | 부모가 자식보다 항상 큰 완전 이진 트리입니다 |
| heapify | 배열을 힙 구조로 변환하는 연산으로 O(n)입니다 |
| 우선순위 큐 | 우선순위가 높은 원소를 먼저 꺼내는 추상 자료형입니다 |
| 완전 이진 트리 | 마지막 레벨을 제외한 모든 레벨이 꽉 찬 트리입니다 |

## Before / After

가장 작은 값을 반복적으로 꺼내는 비효율적 방법과 힙을 사용한 효율적 방법을 비교합니다.

```python
# before: 매번 정렬하여 최솟값 추출 — O(n log n) per extraction
tasks = [5, 3, 8, 1, 4]
tasks.sort()
smallest = tasks.pop(0)  # 정렬 후 꺼냄 — 비효율
```

```python
# after: heapq로 최솟값 추출 — O(log n) per extraction
import heapq
tasks = [5, 3, 8, 1, 4]
heapq.heapify(tasks)           # O(n)으로 힙 구성
smallest = heapq.heappop(tasks) # O(log n)으로 최솟값 추출
```

## 단계별 실습

### Step 1: heapq 기본 사용법

```python
import heapq

data = [5, 3, 8, 1, 4, 2]

# 리스트를 힙으로 변환 — O(n)
heapq.heapify(data)
print(data)  # [1, 3, 2, 5, 4, 8] — 힙 순서

# 최솟값 조회 — O(1)
print(data[0])  # 1

# 최솟값 추출 — O(log n)
print(heapq.heappop(data))  # 1
print(heapq.heappop(data))  # 2

# 값 삽입 — O(log n)
heapq.heappush(data, 0)
print(data[0])  # 0
```

### Step 2: 최대 힙 구현 (부호 반전)

```python
import heapq

# Python heapq는 최소 힙만 지원
# 최대 힙은 값을 음수로 변환하여 구현
max_heap = []
for val in [5, 3, 8, 1, 4]:
    heapq.heappush(max_heap, -val)

# 최댓값 추출
print(-heapq.heappop(max_heap))  # 8
print(-heapq.heappop(max_heap))  # 5
print(-heapq.heappop(max_heap))  # 4
```

### Step 3: Top-K 문제 해결

```python
import heapq

scores = [85, 92, 78, 95, 88, 76, 91, 83, 97, 80]

# 상위 3개 — O(n log k)
top3 = heapq.nlargest(3, scores)
print(f"상위 3개: {top3}")  # [97, 95, 92]

# 하위 3개
bottom3 = heapq.nsmallest(3, scores)
print(f"하위 3개: {bottom3}")  # [76, 78, 80]
```

### Step 4: 우선순위 큐 구현

```python
import heapq

class PriorityQueue:
    def __init__(self):
        self._heap = []
        self._counter = 0  # 동일 우선순위 시 삽입 순서 유지

    def push(self, priority: int, item):
        heapq.heappush(self._heap, (priority, self._counter, item))
        self._counter += 1

    def pop(self):
        if not self._heap:
            raise IndexError("빈 큐에서 pop 할 수 없습니다")
        priority, _, item = heapq.heappop(self._heap)
        return item

    def peek(self):
        if not self._heap:
            raise IndexError("빈 큐에서 peek 할 수 없습니다")
        return self._heap[0][2]

    def __len__(self):
        return len(self._heap)

pq = PriorityQueue()
pq.push(3, "낮은 우선순위 작업")
pq.push(1, "긴급 작업")
pq.push(2, "보통 작업")

print(pq.pop())  # "긴급 작업"
print(pq.pop())  # "보통 작업"
print(pq.pop())  # "낮은 우선순위 작업"
```

### Step 5: 정렬된 리스트 병합

```python
import heapq

list1 = [1, 4, 7, 10]
list2 = [2, 5, 8, 11]
list3 = [3, 6, 9, 12]

# 여러 정렬된 이터러블을 하나로 병합 — O(n log k)
merged = list(heapq.merge(list1, list2, list3))
print(merged)  # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
```

## 이 코드에서 주목할 점

- heapq는 최소 힙만 지원하므로 최대 힙은 부호를 반전합니다
- heapify는 O(n)이지만, n번 heappush는 O(n log n)입니다
- 우선순위 큐에서 동일 우선순위 충돌을 피하려면 카운터를 사용합니다
- nlargest/nsmallest는 k가 작을 때 sorted()보다 효율적입니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| heappush 없이 append 후 heapify | 매번 O(n)이 됩니다 | heappush로 O(log n)에 삽입합니다 |
| 힙에서 임의 원소 삭제 시도 | heapq는 임의 삭제를 지원하지 않습니다 | lazy deletion 패턴을 사용합니다 |
| 최대 힙을 위해 커스텀 비교 시도 | Python 힙은 비교 함수를 받지 않습니다 | 부호 반전 또는 래퍼 클래스를 사용합니다 |
| heap[0]이 아닌 heap[-1]로 최댓값 조회 | heap[-1]은 최댓값이 아닙니다 | 최솟값만 heap[0]으로 보장됩니다 |
| 비교 불가 객체를 힙에 삽입 | TypeError가 발생합니다 | (priority, counter, item) 튜플을 사용합니다 |

## 실무에서 이렇게 쓰입니다

- 작업 스케줄러에서 우선순위가 높은 작업을 먼저 처리합니다
- Dijkstra 최단 경로 알고리즘에서 가장 가까운 노드를 선택합니다
- 이벤트 시뮬레이션에서 가장 빠른 시각의 이벤트를 처리합니다
- 로그 병합에서 여러 정렬된 로그 파일을 시간순으로 합칩니다
- 실시간 중앙값 계산에서 최대 힙과 최소 힙을 함께 사용합니다

## 현업 개발자는 이렇게 생각합니다

heapq를 직접 사용하는 경우보다 queue.PriorityQueue(스레드 안전)나 asyncio.PriorityQueue를 사용하는 경우가 더 많습니다. 하지만 내부적으로 모두 heapq에 기반하므로 heapq의 동작을 이해하는 것이 기본입니다.

Top-K 문제는 면접에서 자주 출제됩니다. "정렬 후 슬라이싱"이 아닌 "힙으로 O(n log k)"로 해결하면 면접관에게 좋은 인상을 줄 수 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **heapq는 min-heap** — max-heap은 부호 반전으로 만든다는 점을 잊지 않습니다.
- **Top-K 패턴** — nlargest/nsmallest로 의도를 명확히 합니다.
- **우선순위 튜플** — 동률 처리를 위해 (priority, idx, item) 패턴을 씁니다.
- **동기화 큐** — 동시성 환경은 queue.PriorityQueue를 검토합니다.
- **균형성** — 삽입·추출 모두 O(log n)임을 활용합니다.

## 체크리스트

- [ ] 힙의 구조와 힙 속성을 설명할 수 있다
- [ ] heapq의 heapify, heappush, heappop을 사용할 수 있다
- [ ] 부호 반전으로 최대 힙을 구현할 수 있다
- [ ] 우선순위 큐를 heapq로 구현할 수 있다
- [ ] nlargest/nsmallest로 Top-K 문제를 풀 수 있다

## 연습 문제

1. 정수 스트림에서 실시간으로 중앙값을 구하는 클래스를 작성하세요. (힌트: 최대 힙 + 최소 힙)
2. K개의 정렬된 리스트를 heapq.merge 없이 직접 병합하는 함수를 작성하세요.
3. 작업 목록에서 우선순위와 마감일을 기준으로 처리 순서를 결정하는 우선순위 큐를 구현하세요.

## 정리 및 다음 글 안내

힙은 최솟값/최댓값을 효율적으로 관리하는 자료구조이고, Python의 heapq 모듈로 쉽게 사용할 수 있습니다. 다음 글에서는 노드와 간선으로 관계를 표현하는 그래프를 다룹니다.

<!-- toc:begin -->
- [자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [배열과 리스트](./02-arrays-and-lists.md)
- [스택과 큐](./03-stacks-and-queues.md)
- [해시 테이블과 dict](./04-hash-tables-and-dict.md)
- [연결 리스트](./05-linked-lists.md)
- [트리와 이진 트리](./06-trees-and-binary-trees.md)
- **힙과 우선순위 큐 (현재 글)**
- 그래프 표현 (예정)
- set과 집합 연산 (예정)
- 자료구조 선택 기준 (예정)
<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — heapq](https://docs.python.org/3/library/heapq.html)
- [Real Python — The Python heapq Module](https://realpython.com/python-heapq-module/)
- [GeeksforGeeks — Heap Data Structure](https://www.geeksforgeeks.org/heap-data-structure/)
- [Visualgo — Heap Visualization](https://visualgo.net/en/heap)
