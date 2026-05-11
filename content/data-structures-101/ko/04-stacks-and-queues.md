---
series: data-structures-101
episode: 4
title: 스택과 큐
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
  - 스택
  - 큐
  - LIFO
  - FIFO
seo_description: 스택(LIFO)과 큐(FIFO)의 동작 원리, 구현 방법, 그리고 실무에서 어떻게 쓰이는지 살펴봅니다.
last_reviewed: '2026-05-04'
---

# 스택과 큐

> Data Structures 101 시리즈 (4/10)


## 이 글에서 다룰 문제

스택과 큐는 프로그래밍 언어의 실행 모델, 운영체제의 스케줄링, 분산 시스템의 메시지 전달까지 모든 곳에 등장합니다. 단순한 ADT지만 깊게 이해하지 못하면 재귀·DFS·BFS·이벤트 루프 같은 핵심 개념을 다루기 어렵습니다.

> 스택을 모르면 재귀를 디버깅할 수 없고, 큐를 모르면 비동기 시스템을 설계할 수 없습니다.

## 전체 흐름
> 스택은 "위에 쌓고 위에서 꺼내는" 모델이고, 큐는 "뒤에 줄 서고 앞에서 빠지는" 모델입니다. 두 ADT 모두 양 끝에서만 연산하므로 배열·연결 리스트로 모두 O(1)에 구현할 수 있습니다.

```text
스택 (LIFO)              큐 (FIFO)
        push                  enqueue       dequeue
          ↓                      ↓             ↑
       ┌─────┐              ┌─────────────────┐
       │  C  │ ← top         │ A → B → C → D │
       │  B  │                └─────────────────┘
       │  A  │              앞(front)        뒤(back)
       └─────┘
          ↑
         pop
```

## Before / After

**Before — 큐로 list를 그대로 사용:**

```python
queue = []
queue.append("A")
queue.append("B")
front = queue.pop(0)   # O(n) — 모든 원소 한 칸씩 이동
```

**After — 큐에 deque 사용:**

```python
from collections import deque

queue = deque()
queue.append("A")
queue.append("B")
front = queue.popleft()   # O(1)
```

같은 동작이지만 큐가 커질수록 시간 차이가 압도적으로 벌어집니다.

## 단계별로 따라하기

### 1단계: 스택을 직접 구현

```python
class Stack:
    def __init__(self):
        self._data = []

    def push(self, value):
        self._data.append(value)

    def pop(self):
        if not self._data:
            raise IndexError("pop from empty stack")
        return self._data.pop()

    def peek(self):
        if not self._data:
            raise IndexError("peek from empty stack")
        return self._data[-1]

    def __len__(self):
        return len(self._data)


s = Stack()
for v in [1, 2, 3]:
    s.push(v)
print(s.pop(), s.pop(), s.pop())   # 3 2 1
```

배열의 끝에서만 연산하면 모두 O(1)이므로 list가 그대로 스택으로 쓰입니다.

### 2단계: 큐를 직접 구현

```python
from collections import deque


class Queue:
    def __init__(self):
        self._data = deque()

    def enqueue(self, value):
        self._data.append(value)

    def dequeue(self):
        if not self._data:
            raise IndexError("dequeue from empty queue")
        return self._data.popleft()

    def __len__(self):
        return len(self._data)


q = Queue()
for v in ["A", "B", "C"]:
    q.enqueue(v)
print(q.dequeue(), q.dequeue(), q.dequeue())   # A B C
```

deque는 양 끝에서 O(1)이므로 큐 구현에 가장 적합합니다.

### 3단계: 괄호 균형 검사 (스택의 고전적 활용)

```python
def is_balanced(expr: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    opens = set("([{")
    stack = []

    for ch in expr:
        if ch in opens:
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack


print(is_balanced("({[]})"))   # True
print(is_balanced("({[})"))    # False
print(is_balanced("(("))       # False
```

여는 괄호는 push, 닫는 괄호는 pop해서 짝을 검사합니다. 컴파일러의 구문 분석이 같은 원리로 동작합니다.

### 4단계: BFS 구현 (큐의 고전적 활용)

```python
from collections import deque


def bfs(graph: dict, start: str) -> list:
    visited = {start}
    queue = deque([start])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order


graph = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A", "D"],
    "D": ["B", "C", "E"],
    "E": ["D"],
}

print(bfs(graph, "A"))   # ['A', 'B', 'C', 'D', 'E']
```

큐를 사용하면 가까운 노드부터 차례대로 방문합니다. 같은 코드를 큐 대신 스택으로 바꾸면 DFS가 됩니다.

### 5단계: 데크는 둘 다 가능

```python
from collections import deque

dq = deque()
# 스택처럼
dq.append(1); dq.append(2); dq.append(3)
print(dq.pop())    # 3 (LIFO)

# 큐처럼
dq.append(1); dq.append(2); dq.append(3)
print(dq.popleft()) # 1 (FIFO)
```

deque는 양 끝 모두에서 O(1)이므로 스택과 큐를 모두 표현할 수 있는 일반화된 자료구조입니다.

## 이 코드에서 주목할 점

- 스택은 list로, 큐는 deque로 구현하면 모두 O(1)입니다
- 큐로 `list.pop(0)`을 쓰면 O(n)이라 절대 사용하지 말아야 합니다
- 스택과 큐의 차이는 "어느 끝에서 꺼내는가" 한 가지뿐입니다
- DFS와 BFS는 자료구조만 바꾸면 같은 코드입니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| `list.pop(0)`을 큐로 사용 | 매번 O(n) | `collections.deque` 사용 |
| 빈 컨테이너에 pop 시도 | IndexError | `if stack` 또는 try/except로 가드 |
| 재귀 깊이 한계 무시 | RecursionError | 명시적 스택으로 변환 |
| BFS에 visited 누락 | 무한 순회 | 방문 표시는 push할 때 즉시 |
| 우선순위 큐를 일반 큐로 오해 | 순서가 다름 | heap을 별도로 사용 |

## 실무에서는 이렇게 쓰입니다

- 함수 호출은 스택 위에서 동작합니다(콜 스택, 스택 트레이스)
- 웹 브라우저의 뒤로가기는 스택, 앞으로가기는 다른 스택
- 메시지 큐(RabbitMQ, Kafka)는 시스템 간 비동기 통신의 핵심
- 운영체제의 작업 스케줄러는 다양한 큐(FIFO, 우선순위 큐)를 조합
- 그래프 탐색에서 BFS는 큐, DFS는 스택(또는 재귀)으로 구현

## 체크리스트

- [ ] 스택의 LIFO와 큐의 FIFO 의미를 설명할 수 있는가
- [ ] 파이썬에서 큐로 list를 쓰면 안 되는 이유를 알고 있는가
- [ ] 괄호 균형 검사처럼 스택이 자연스러운 문제 패턴을 인지했는가
- [ ] BFS와 DFS의 차이가 자료구조 선택임을 이해했는가
- [ ] deque가 스택과 큐를 모두 지원한다는 것을 알고 있는가

## 정리 및 다음 단계

스택과 큐는 가장 단순한 ADT이지만 가장 자주 등장하는 자료구조입니다. 스택은 LIFO로 함수 호출·구문 분석·DFS에 쓰이고, 큐는 FIFO로 BFS·작업 스케줄링·메시지 전달에 쓰입니다. 파이썬에서는 스택은 list, 큐는 `collections.deque`가 표준 선택입니다. 두 자료구조의 차이는 "어느 끝에서 꺼내는가" 한 가지이지만, 그 한 가지가 시스템의 동작 양식을 완전히 바꿉니다.

다음 글에서는 키로 즉시 값을 찾을 수 있는 마법, 해시 테이블을 살펴봅니다. 평균 O(1) 검색이 어떻게 가능한지, 충돌은 어떻게 해결하는지 알아봅니다.

<!-- toc:begin -->
- [자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [배열과 동적 배열](./02-arrays-and-dynamic-arrays.md)
- [연결 리스트](./03-linked-lists.md)
- **스택과 큐 (현재 글)**
- 해시 테이블 (예정)
- 트리 (예정)
- 이진 탐색 트리 (예정)
- 힙 (예정)
- 그래프 (예정)
- 자료구조 선택 기준 (예정)
<!-- toc:end -->

## 참고 자료

- [Open Data Structures — Stacks and Queues](https://opendatastructures.org/ods-python/3_3_SEList_Space_Efficient_.html)
- [Python `collections.deque` docs](https://docs.python.org/3/library/collections.html#collections.deque)
- [Wikipedia — Stack (abstract data type)](https://en.wikipedia.org/wiki/Stack_(abstract_data_type))
- [Wikipedia — Queue (abstract data type)](https://en.wikipedia.org/wiki/Queue_(abstract_data_type))

Tags: Computer Science, 자료구조, 스택, 큐, LIFO, FIFO
