---
series: data-structures-101
episode: 1
title: "Data Structures 101 (1/10): 자료구조란 무엇인가?"
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
  - 추상 자료형
  - 알고리즘 기초
  - 시간 복잡도
  - 전공 개요
seo_description: 자료구조와 ADT의 차이, 그리고 구조 선택이 성능을 바꾸는 이유를 설명합니다.
last_reviewed: '2026-05-12'
---

# Data Structures 101 (1/10): 자료구조란 무엇인가?

이 글은 Data Structures 101 시리즈의 첫 번째 글입니다.


![Data Structures 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-101/01/01-01-big-picture.ko.png)
*Data Structures 101 1장 흐름 개요*

## 먼저 던지는 질문

- 자료구조와 추상 자료형(ADT)은 어떻게 다를까요?
- 같은 데이터를 다루는데도 왜 구조 선택에 따라 성능이 크게 달라질까요?
- 입력 크기가 커질수록 자료구조 선택이 어떤 식으로 비용 차이를 만들까요?

## 왜 중요한가

좋은 코드를 쓴다는 말은 결국 데이터를 어떻게 표현할지 잘 결정한다는 뜻입니다. 알고리즘은 언제나 자료구조 위에서 실행되므로, 잘못된 구조를 고르면 좋은 알고리즘도 쉽게 느려집니다.

> 알고리즘 + 자료구조 = 프로그램 — Niklaus Wirth

이 시리즈는 아홉 가지 핵심 자료구조가 어떻게 동작하는지, 시간·공간 복잡도는 어떤지, 그리고 언제 무엇을 선택해야 하는지를 한 장의 지도처럼 연결해서 설명합니다.

## 핵심 한눈에 보기

> 자료구조는 논리적 형태와 물리적 메모리 배치라는 두 층으로 이해해야 합니다. ADT가 인터페이스를 정의한다면, 자료구조는 그 인터페이스를 실제로 구현하는 메모리 전략입니다.

```text
            ADT (Abstract Data Type)
              "what can be done"
                    |
        ┌───────────┼───────────┐
        |           |           |
      List         Set         Map
        |           |           |
   ┌────┴────┐  ┌───┴───┐  ┌───┴───┐
  array  linked  hash  tree  hash  tree
        |
   (concrete data structure: memory layout)
```

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| 자료구조 | 메모리 안에 데이터를 저장하고 조작하는 구체적인 방법 |
| 추상 자료형(ADT) | 데이터와 연산을 인터페이스 수준에서 정의한 개념 |
| 시간 복잡도 | 입력이 커질 때 실행 시간이 늘어나는 비율 |
| 공간 복잡도 | 입력이 커질 때 메모리 사용량이 늘어나는 비율 |
| 분할 상환 비용 | 여러 번의 연산을 평균냈을 때의 1회 비용 |

## 전후 비교

**Before — without thinking about data structures:**

```python
# Find a specific ID among 10 million users
users = [{"id": i, "name": f"user{i}"} for i in range(10_000_000)]

def find_user(target_id: int):
    for user in users:
        if user["id"] == target_id:
            return user
    return None

# 5 million comparisons on average, 10 million in the worst case
```

**After — with a data structure in mind:**

```python
# Index the same data with a hash table
users = {i: {"id": i, "name": f"user{i}"} for i in range(10_000_000)}

def find_user(target_id: int):
    return users.get(target_id)

# One comparison on average
```

겉보기에는 둘 다 같은 데이터를 다루지만, 하나는 선형 탐색이고 다른 하나는 키 기반 인덱싱입니다. 실무 성능 차이는 대부분 이렇게 단순한 선택에서 시작합니다.

## 단계별로 따라하기

### 1단계: 같은 데이터, 다른 구조

```python
import time

N = 1_000_000

list_data = list(range(N))
set_data = set(list_data)

def measure(label, fn):
    start = time.perf_counter()
    fn()
    elapsed = (time.perf_counter() - start) * 1000
    print(f"{label}: {elapsed:.2f} ms")

measure("list lookup", lambda: (N - 1) in list_data)
measure("set lookup", lambda: (N - 1) in set_data)
```

리스트는 앞에서부터 끝까지 훑고, 집합은 해시를 통해 곧바로 버킷으로 이동합니다. 데이터가 커질수록 격차가 더 선명해집니다.

### 2단계: 추상 인터페이스와 구현 분리해서 보기

```python
from abc import ABC, abstractmethod

class Stack(ABC):
    """ADT: pop returns whatever was pushed last."""

    @abstractmethod
    def push(self, value): ...

    @abstractmethod
    def pop(self): ...

class ListStack(Stack):
    def __init__(self):
        self._data = []

    def push(self, value):
        self._data.append(value)

    def pop(self):
        return self._data.pop()

class LinkedStack(Stack):
    def __init__(self):
        self._head = None

    def push(self, value):
        self._head = (value, self._head)

    def pop(self):
        value, self._head = self._head
        return value
```

`Stack`라는 ADT는 동일하지만 구현은 다를 수 있습니다. 호출자는 인터페이스만 알면 되고, 성능과 메모리 특성은 구현체가 책임집니다.

### 3단계: 시간 복잡도 비교표

```python
operations = {
    "Array":             {"search": "O(n)",     "insert": "O(n)",  "delete": "O(n)"},
    "Dynamic Array":     {"search": "O(n)",     "insert": "O(1)*", "delete": "O(n)"},
    "Linked List":       {"search": "O(n)",     "insert": "O(1)",  "delete": "O(1)"},
    "Hash Table":        {"search": "O(1)",     "insert": "O(1)",  "delete": "O(1)"},
    "Balanced BST":      {"search": "O(log n)", "insert": "O(log n)", "delete": "O(log n)"},
    "Heap":              {"search": "O(n)",     "insert": "O(log n)", "min": "O(1)"},
}

for ds, ops in operations.items():
    print(f"{ds:<20} {ops}")
```

`*`는 분할 상환 비용입니다. 동적 배열은 가끔 크게 비싼 재할당을 치르지만, 긴 구간으로 평균내면 끝 삽입이 O(1)로 유지됩니다.

### 4단계: 잘못 고른 구조의 비용

```python
# Scenario: process events arriving every second by priority
import heapq

events = []
# Wrong choice: sort on every insert
def add_wrong(priority, event):
    events.append((priority, event))
    events.sort()

# Right choice: a heap
heap = []
def add_right(priority, event):
    heapq.heappush(heap, (priority, event))

# add_wrong is O(n log n) per insert
# add_right is O(log n) per insert
# At 1 million events per day, that is a 1000x difference
```

자료구조를 잘못 고르면 같은 기능도 비용 구조가 완전히 달라집니다. 운영에서 병목은 대개 이런 반복 연산 경로에서 터집니다.

### 5단계: 시리즈 로드맵

```python
roadmap = [
    (1, "What Are Data Structures?", "the big picture"),
    (2, "Arrays and Dynamic Arrays", "fixed/variable contiguous memory"),
    (3, "Linked Lists", "nodes connected by pointers"),
    (4, "Stacks and Queues", "LIFO and FIFO"),
    (5, "Hash Tables", "instant access by key"),
    (6, "Trees", "expressing hierarchy"),
    (7, "Binary Search Trees", "fast search in a sorted tree"),
    (8, "Heaps", "implementing priority queues"),
    (9, "Graphs", "modeling arbitrary relationships"),
    (10, "Choosing Data Structures", "when to use which"),
]

for num, title, keywords in roadmap:
    print(f"  {num:02d}. {title} — {keywords}")
```

이 시리즈는 개별 구조를 따로 외우게 하려는 글이 아닙니다. 어떤 문제에서 어떤 구조가 자연스럽게 선택되는지 연결해서 이해하는 것이 목표입니다.

## 이 코드에서 주목할 점

- 같은 ADT라도 구현체에 따라 성능 특성이 크게 달라집니다.
- 시간 복잡도는 입력이 커질수록 드러나는 증가율을 설명합니다.
- 동적 배열과 해시 테이블처럼 가끔 비싼 연산을 하는 구조는 분할 상환 분석이 필요합니다.
- 성능 문제는 알고리즘뿐 아니라 자료구조 선택에서도 결정됩니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| ADT와 구현을 같은 것으로 봄 | “스택은 배열이다”처럼 단정하게 됨 | ADT는 인터페이스, 구현은 별개로 구분합니다 |
| 작은 입력만 보고 성능을 판단함 | 성장률 차이를 놓침 | 입력이 커질 때 비용이 어떻게 변하는지 봅니다 |
| 빅오만 보고 끝냄 | 상수 항과 캐시 효과를 무시함 | 실측과 메모리 특성도 함께 봅니다 |
| 한 구조를 모든 문제에 재사용함 | 접근 패턴과 맞지 않음 | 문제의 주 연산에 맞춰 구조를 바꿉니다 |
| 공간 복잡도를 무시함 | 메모리 병목을 놓침 | 시간과 공간을 같이 분석합니다 |

## 실무에서는 이렇게 쓰입니다

- 데이터베이스 인덱스는 빠른 탐색을 위해 B-Tree 계열을 사용합니다.
- 운영체제 스케줄러는 우선순위 큐를 활용해 다음 작업을 고릅니다.
- 브라우저의 뒤로 가기는 스택 모델로 이해할 수 있습니다.
- 라우팅 테이블과 의존성 관계, 소셜 그래프는 그래프로 모델링됩니다.
- Redis, Memcached 같은 인메모리 캐시는 해시 테이블 위에서 동작합니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 먼저 “가장 자주 일어나는 연산이 무엇인가”를 묻습니다. 검색이 많은지, 삽입이 많은지, 정렬 순회가 중요한지 이름 붙인 뒤에야 자료구조를 고릅니다. 워크로드를 먼저 정의하면 선택지는 대부분 자연스럽게 좁혀집니다.

또한 처음부터 트리나 힙을 꺼내지 않습니다. 대개는 list와 dict 같은 기본 구조로 시작하고, 실제 병목이 확인됐을 때만 더 복잡한 구조로 교체합니다. 자료구조에서도 성급한 최적화는 유지보수 비용만 올릴 수 있습니다.

## 체크리스트

- [ ] 자료구조와 ADT의 차이를 설명할 수 있습니다
- [ ] 하나의 ADT가 여러 구현을 가질 수 있다는 점을 이해했습니다
- [ ] 시간 복잡도가 입력 증가에 따른 성장률이라는 점을 알고 있습니다
- [ ] 분할 상환 비용이 무엇이고 언제 쓰이는지 설명할 수 있습니다
- [ ] 시리즈 전체의 큰 흐름을 파악했습니다

## 연습 문제

1. 서점 책장, 편의점 줄, 휴대폰 주소록처럼 현실 시스템 하나를 골라 어떤 자료구조와 닮았는지 분석해 보세요. 어떤 연산이 빠르고 어떤 연산이 느린가요?

2. 1단계 측정 코드를 N = 100k, 1M, 10M으로 바꿔 실행해 보세요. list와 set의 격차는 어떻게 벌어지나요?

3. 최근에 작성한 코드 하나를 골라 사용한 자료구조를 모두 적어 보세요. 더 명확하거나 더 빠른 대안이 있었는지도 함께 검토해 보세요.

## 정리 및 다음 단계

자료구조는 데이터를 메모리에 어떻게 놓고 어떤 연산을 효율적으로 지원할지 결정합니다. 같은 데이터라도 구조를 잘못 고르면 수십 배에서 수천 배까지 느려질 수 있습니다. ADT가 인터페이스를, 자료구조가 구현을 뜻한다는 구분을 명확히 해 두면 이후의 설계 판단이 훨씬 선명해집니다.

다음 글에서는 가장 기본적인 구조인 배열을 다룹니다. 고정 배열과 동적 배열이 어떻게 다르고, 파이썬의 `list`가 내부에서 무엇을 하는지 살펴보겠습니다.


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

자료구조를 배우는 초기에 가장 중요한 습관은 문제를 먼저 연산 집합으로 번역하는 것입니다. 예를 들어 검색창 자동완성은 "앞부분 일치 조회"가 핵심이고, 주문 이벤트 파이프라인은 "끝에 추가하고 오래된 항목을 제거"가 핵심입니다. 문제 문장을 곧바로 코드로 옮기지 않고 연산으로 쪼개면, 어떤 구조가 맞는지 선택 기준이 선명해집니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

자료구조를 배우는 초기에 가장 중요한 습관은 문제를 먼저 연산 집합으로 번역하는 것입니다. 예를 들어 검색창 자동완성은 "앞부분 일치 조회"가 핵심이고, 주문 이벤트 파이프라인은 "끝에 추가하고 오래된 항목을 제거"가 핵심입니다. 문제 문장을 곧바로 코드로 옮기지 않고 연산으로 쪼개면, 어떤 구조가 맞는지 선택 기준이 선명해집니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

자료구조를 배우는 초기에 가장 중요한 습관은 문제를 먼저 연산 집합으로 번역하는 것입니다. 예를 들어 검색창 자동완성은 "앞부분 일치 조회"가 핵심이고, 주문 이벤트 파이프라인은 "끝에 추가하고 오래된 항목을 제거"가 핵심입니다. 문제 문장을 곧바로 코드로 옮기지 않고 연산으로 쪼개면, 어떤 구조가 맞는지 선택 기준이 선명해집니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

자료구조를 배우는 초기에 가장 중요한 습관은 문제를 먼저 연산 집합으로 번역하는 것입니다. 예를 들어 검색창 자동완성은 "앞부분 일치 조회"가 핵심이고, 주문 이벤트 파이프라인은 "끝에 추가하고 오래된 항목을 제거"가 핵심입니다. 문제 문장을 곧바로 코드로 옮기지 않고 연산으로 쪼개면, 어떤 구조가 맞는지 선택 기준이 선명해집니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

자료구조를 배우는 초기에 가장 중요한 습관은 문제를 먼저 연산 집합으로 번역하는 것입니다. 예를 들어 검색창 자동완성은 "앞부분 일치 조회"가 핵심이고, 주문 이벤트 파이프라인은 "끝에 추가하고 오래된 항목을 제거"가 핵심입니다. 문제 문장을 곧바로 코드로 옮기지 않고 연산으로 쪼개면, 어떤 구조가 맞는지 선택 기준이 선명해집니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

자료구조를 배우는 초기에 가장 중요한 습관은 문제를 먼저 연산 집합으로 번역하는 것입니다. 예를 들어 검색창 자동완성은 "앞부분 일치 조회"가 핵심이고, 주문 이벤트 파이프라인은 "끝에 추가하고 오래된 항목을 제거"가 핵심입니다. 문제 문장을 곧바로 코드로 옮기지 않고 연산으로 쪼개면, 어떤 구조가 맞는지 선택 기준이 선명해집니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.

## 처음 질문으로 돌아가기

- **자료구조와 추상 자료형(ADT)은 어떻게 다를까요?**
  - 본문의 기준은 자료구조란 무엇인가?를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **같은 데이터를 다루는데도 왜 구조 선택에 따라 성능이 크게 달라질까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **입력 크기가 커질수록 자료구조 선택이 어떤 식으로 비용 차이를 만들까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **자료구조란 무엇인가? (현재 글)**
- 배열과 동적 배열 (예정)
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

- [Introduction to Algorithms (CLRS) — Cormen et al.](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)
- [Open Data Structures — Pat Morin](https://opendatastructures.org/)
- [Wikipedia — Data Structure](https://en.wikipedia.org/wiki/Data_structure)
- [Python Time Complexity Wiki](https://wiki.python.org/moin/TimeComplexity)

Tags: Computer Science, 자료구조, 추상 자료형, 알고리즘 기초, 시간 복잡도, 전공 개요
