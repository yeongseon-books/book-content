---
series: data-structures-101
episode: 8
title: 힙
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
  - 힙
  - 우선순위 큐
  - heapq
  - 정렬
seo_description: 힙의 구조, 우선순위 큐의 표준 구현 방식, 그리고 파이썬 heapq 모듈 사용법을 익힙니다.
last_reviewed: '2026-05-04'
---

# 힙

> Data Structures 101 시리즈 (8/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 매번 가장 높은 우선순위 작업을 꺼내야 한다면 어떤 자료구조를 써야 할까요? 정렬해 두면 삽입이 느리고, 그냥 두면 꺼내는 게 느립니다.

> 힙은 부모가 자식보다 항상 작거나(최소 힙) 크다(최대 힙)는 단 하나의 규칙을 가진 완전 이진 트리입니다. 이 규칙 덕분에 최솟값(또는 최댓값)을 O(1)에 보고, O(log n)에 꺼낼 수 있습니다. 우선순위 큐의 표준 구현이며, 파이썬에서는 `heapq` 모듈로 제공됩니다. 이 글에서는 힙의 구조, 배열 표현, 그리고 직접 구현을 통해 동작 원리를 익힙니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 힙 불변식과 완전 이진 트리의 관계
- 힙을 배열로 표현하는 방법
- 삽입(sift up)과 삭제(sift down) 연산의 동작
- 파이썬 `heapq`의 사용법과 한계

## 왜 중요한가

힙은 작업 스케줄링, 다익스트라 알고리즘, 이벤트 시뮬레이션, 외부 정렬 등 "다음에 처리할 가장 작은(또는 가장 큰) 것"을 빠르게 골라야 하는 모든 시스템의 핵심입니다. BST가 일반적인 정렬 트리라면, 힙은 "양 극단만 빠르게" 다루는 특수 자료구조입니다.

> 힙 = 우선순위 큐의 사실상 표준 구현.

## 개념 한눈에 보기

> 힙은 완전 이진 트리이면서 부모-자식 사이에 크기 관계 불변식을 유지합니다. 완전 이진 트리는 배열로 표현할 때 인덱스 계산만으로 부모-자식을 찾을 수 있어 메모리 효율이 매우 좋습니다.

```text
최소 힙
        1            인덱스: 0  1  2  3  4  5  6
       / \           배열:  [1, 3, 2, 5, 4, 6, 7]
      3   2
     / \ / \         부모(i) = (i - 1) // 2
    5  4 6  7        왼자식(i) = 2*i + 1
                     오른자식(i) = 2*i + 2
```

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| 최소 힙(min-heap) | 부모 ≤ 자식 |
| 최대 힙(max-heap) | 부모 ≥ 자식 |
| 완전 이진 트리 | 마지막 레벨을 제외하고 모든 레벨이 채워진 이진 트리 |
| sift up | 새 원소를 부모와 비교하며 위로 올림 |
| sift down | 루트의 새 원소를 자식과 비교하며 아래로 내림 |

## Before / After

**Before — 매번 정렬:**

```python
events = []
def add(event):
    events.append(event)
    events.sort()

def pop_next():
    return events.pop(0)
# 삽입 O(n log n), pop O(n)
```

**After — 힙 사용:**

```python
import heapq
events = []
def add(event):
    heapq.heappush(events, event)

def pop_next():
    return heapq.heappop(events)
# 삽입과 pop 모두 O(log n)
```

## 실습: 단계별로 따라하기

### 1단계: 힙을 직접 구현 (sift up/down)

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

push는 끝에 추가한 뒤 위로 올리고, pop은 마지막 원소를 루트로 옮긴 뒤 아래로 내립니다. 둘 다 트리 높이만큼만 비교하므로 O(log n).

### 2단계: 파이썬 heapq 모듈

```python
import heapq

heap = []
for v in [5, 3, 8, 1, 9, 2]:
    heapq.heappush(heap, v)

print(heap)                      # 내부 배열 (트리 표현)
print(heapq.heappop(heap))       # 1
print(heapq.heappop(heap))       # 2

# 가장 작은 k개
import heapq
data = [5, 3, 8, 1, 9, 2, 7]
print(heapq.nsmallest(3, data))   # [1, 2, 3]
print(heapq.nlargest(3, data))    # [9, 8, 7]
```

`heapq`는 최소 힙만 제공합니다. 최대 힙이 필요하면 값에 음수를 곱해서 넣습니다.

### 3단계: 우선순위 큐로 사용

```python
import heapq

# (우선순위, 작업) 튜플로 저장
tasks = []
heapq.heappush(tasks, (3, "report"))
heapq.heappush(tasks, (1, "alert"))
heapq.heappush(tasks, (2, "email"))

while tasks:
    priority, task = heapq.heappop(tasks)
    print(f"[{priority}] {task}")

# [1] alert
# [2] email
# [3] report
```

같은 우선순위의 동점 처리가 필요하면 `(priority, counter, task)` 형태로 안정성을 추가합니다.

### 4단계: heapify - 배열을 한 번에 힙으로

```python
import heapq

data = [5, 3, 8, 1, 9, 2, 7]
heapq.heapify(data)   # O(n) - sift down을 잎부터 거꾸로
print(data)            # [1, 3, 2, 5, 9, 8, 7]
```

비어 있는 힙에 n번 push하면 O(n log n)이지만, 한 번에 heapify하면 O(n)입니다. 큰 데이터를 한꺼번에 힙으로 만들 때 유리합니다.

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

전체 시간 복잡도는 O(n log n). 평균적으로 퀵소트보다는 느리지만 최악 O(n log n)을 보장합니다.

## 이 코드에서 주목할 점

- 완전 이진 트리는 배열로 표현해도 빈 칸이 없습니다(메모리 효율 ↑)
- 힙은 "정렬된 자료구조"가 아닙니다. 부분적 순서만 보장합니다
- heapify가 O(n)인 것은 힙의 우아한 성질입니다
- BST가 모든 키를 정렬하는 데 비해, 힙은 양 극단만 관리합니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 힙을 정렬된 자료구조로 오해 | 임의 인덱스 접근 시 잘못된 값 | "가장 작은 것만 빠르다"로 이해 |
| 최대 힙으로 heapq 직접 사용 | heapq는 최소 힙만 | 음수 변환 또는 wrapper 클래스 |
| 동점 처리 누락 | 비교 불가능 객체로 에러 | counter 추가 |
| BST 대용으로 사용 | 임의 검색은 O(n) | 검색이 자주면 BST/dict |
| heapify를 잊고 push 반복 | O(n log n) 대신 O(n) 가능 | 한 번에 heapify |

## 실무에서는 이렇게 쓰입니다

- 다익스트라 최단 경로 알고리즘은 우선순위 큐 없이는 비효율적
- 운영체제 스케줄러, 작업 큐는 우선순위 힙으로 다음 작업 결정
- 이벤트 기반 시뮬레이션(시간 순 이벤트 처리)은 힙이 필수
- 메모리 할당기 중 일부는 자유 블록을 크기별 힙으로 관리
- A* 길찾기, Huffman 코딩, 외부 정렬(merge sort)도 힙을 활용

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 "다음에 처리할 가장 작은(또는 가장 큰) 것"이라는 패턴이 보이면 즉시 힙을 떠올립니다. 정렬이라는 더 비싼 도구를 쓰지 않습니다. 또한 동점 처리, 안정성, 변경 가능한 우선순위 같은 미묘한 요구사항을 미리 점검합니다. 우선순위가 변할 수 있다면 표준 힙으로는 부족하고 indexed heap 같은 변형이 필요합니다.

또한 시니어는 "k개만 필요한가, 전체가 필요한가"를 묻습니다. 100만 개에서 10개만 필요하면 `heapq.nsmallest`가 정렬보다 훨씬 빠릅니다. 자료구조와 알고리즘을 함께 보는 시야가 차이를 만듭니다.

## 체크리스트

- [ ] 힙의 불변식과 완전 이진 트리의 의미를 설명할 수 있는가
- [ ] 배열 인덱스로 부모/자식을 찾는 공식을 알고 있는가
- [ ] sift up/down의 동작과 시간 복잡도를 이해했는가
- [ ] heapq가 최소 힙만 제공한다는 것을 알고 있는가
- [ ] 힙과 BST의 용도 차이를 구분할 수 있는가

## 연습 문제

1. 위 `MinHeap`을 일반화해서 비교 함수를 받을 수 있게 만들어 보세요. 그러면 같은 코드로 최소·최대 힙을 모두 만들 수 있습니다.

2. 두 힙(min/max)을 사용해 스트림에서 중앙값을 O(log n)에 갱신하는 자료구조를 구현해 보세요.

3. 100만 개 정수에서 가장 큰 100개를 찾는 코드를 (a) 정렬 후 슬라이싱, (b) `heapq.nlargest`, (c) 크기 100짜리 최소 힙으로 직접 관리하는 세 가지로 구현하고 시간을 비교해 보세요.

## 정리 및 다음 단계

힙은 "양 극단만 빠르게 다루기"에 특화된 완전 이진 트리이며, 우선순위 큐의 표준 구현입니다. 배열로 빈 칸 없이 표현 가능하고, 삽입과 삭제 모두 O(log n)이며, heapify는 O(n)이라는 우아한 성질을 가집니다. 임의 키 검색은 O(n)이라 BST나 dict와는 용도가 분명히 다릅니다. 작업 스케줄링, 다익스트라, 이벤트 시뮬레이션 등 "다음 차례를 빠르게 결정"해야 하는 모든 시스템의 기반입니다.

다음 글에서는 가장 일반적인 관계 표현 자료구조인 그래프를 살펴봅니다. 트리는 그래프의 특수한 경우이며, 그래프의 표현 방법과 기본 알고리즘을 익힙니다.

<!-- toc:begin -->
- [자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [배열과 동적 배열](./02-arrays-and-dynamic-arrays.md)
- [연결 리스트](./03-linked-lists.md)
- [스택과 큐](./04-stacks-and-queues.md)
- [해시 테이블](./05-hash-tables.md)
- [트리](./06-trees.md)
- [이진 탐색 트리](./07-binary-search-trees.md)
- **힙 (현재 글)**
- 그래프 (예정)
- 자료구조 선택 기준 (예정)
<!-- toc:end -->

## 참고 자료

- [Open Data Structures — Heaps](https://opendatastructures.org/ods-python/10_Heaps.html)
- [Python `heapq` documentation](https://docs.python.org/3/library/heapq.html)
- [Wikipedia — Binary Heap](https://en.wikipedia.org/wiki/Binary_heap)
- [Wikipedia — Priority Queue](https://en.wikipedia.org/wiki/Priority_queue)

Tags: Computer Science, 자료구조, 힙, 우선순위 큐, heapq, 정렬
