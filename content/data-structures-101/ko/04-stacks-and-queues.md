---
series: data-structures-101
episode: 4
title: 스택과 큐
status: publish-ready
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
seo_description: LIFO와 FIFO라는 단순한 규칙이 시스템 동작을 결정하는 스택과 큐의 원리 및 구현 방식과 실무 활용 사례를 상세히 다룹니다.
last_reviewed: '2026-05-12'
---

# 스택과 큐

이 글은 Data Structures 101 시리즈의 네 번째 글입니다.

## 이 글에서 다룰 문제

- 스택과 큐라는 ADT는 각각 어떤 규칙을 가질까요?
- 파이썬에서는 어떤 자료구조로 스택과 큐를 구현하는 편이 자연스러울까요?
- 함수 호출, BFS, 메시지 큐 같은 시스템은 왜 이 두 구조 위에서 이해할 수 있을까요?
- DFS와 BFS의 차이가 결국 자료구조 선택이라는 말은 무슨 뜻일까요?

함수 호출은 왜 “쌓인다”고 말할까요? 메시지 큐, 작업 큐, 프린터 큐가 모두 큐라는 이름을 공유하는 이유는 무엇일까요? 겉보기에는 단순하지만, 이 두 ADT는 언어 런타임과 분산 시스템까지 관통합니다.

> 스택은 마지막에 넣은 것을 먼저 꺼내는 LIFO 구조이고, 큐는 먼저 들어온 것을 먼저 꺼내는 FIFO 구조입니다. 규칙은 단순하지만 이 규칙 하나가 함수 호출, 트리 순회, 작업 스케줄링, 메시지 전달 같은 시스템 동작을 결정합니다.

## 왜 중요한가

스택과 큐는 언어 실행 모델, 운영체제 스케줄링, 비동기 메시징의 기본 어휘입니다. 이 둘을 깊이 이해하지 못하면 재귀, DFS, BFS, 이벤트 루프를 운영 관점에서 설명하기 어렵습니다.

> 스택을 모르면 재귀를 디버깅하기 어렵고, 큐를 모르면 비동기 시스템을 설계하기 어렵습니다.

## 핵심 한눈에 보기

> 스택은 “위에 넣고 위에서 꺼내는” 모델이고, 큐는 “뒤로 들어오고 앞으로 나가는” 모델입니다. 두 ADT 모두 양 끝만 만지므로, 적절한 기반 구조를 쓰면 핵심 연산을 O(1)로 유지할 수 있습니다.

```text
Stack (LIFO)              Queue (FIFO)
        push                  enqueue       dequeue
          ↓                      ↓             ↑
       ┌─────┐              ┌─────────────────┐
       │  C  │ ← top         │ A → B → C → D │
       │  B  │                └─────────────────┘
       │  A  │              front           back
       └─────┘
          ↑
         pop
```

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| 스택 | Last-In-First-Out ADT |
| 큐 | First-In-First-Out ADT |
| push / pop | 스택 삽입 / 제거 |
| enqueue / dequeue | 큐 삽입 / 제거 |
| deque | 양 끝 삽입·삭제를 모두 지원하는 일반화 구조 |

## Before / After

**Before — using a list as a queue directly:**

```python
queue = []
queue.append("A")
queue.append("B")
front = queue.pop(0)   # O(n) — every element shifts one slot
```

**After — using deque as a queue:**

```python
from collections import deque

queue = deque()
queue.append("A")
queue.append("B")
front = queue.popleft()   # O(1)
```

동작은 같아 보이지만 큐 길이가 길어질수록 차이는 급격히 커집니다. 파이썬에서 큐를 list로 구현하면 거의 항상 잘못된 출발입니다.

## 단계별로 따라하기

### 1단계: 스택 직접 구현

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

배열의 한쪽 끝만 사용하면 각 연산이 O(1)이므로, 파이썬 list는 이미 좋은 스택입니다.

### 2단계: 큐 직접 구현

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

`deque`는 양 끝이 모두 O(1)이므로 큐의 기반 구조로 이상적입니다.

### 3단계: 스택의 고전 예시 — 괄호 균형 검사

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

여는 괄호에서 push하고 닫는 괄호에서 pop해 대응 관계를 확인합니다. 파서와 컴파일러도 같은 원리 위에 서 있습니다.

### 4단계: 큐의 고전 예시 — BFS

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

큐를 쓰면 가까운 노드부터 방문합니다. 같은 코드에서 큐 대신 스택을 넣으면 DFS가 됩니다.

### 5단계: deque는 둘 다 할 수 있다

```python
from collections import deque

dq = deque()
# As a stack
dq.append(1); dq.append(2); dq.append(3)
print(dq.pop())    # 3 (LIFO)

# As a queue
dq.append(1); dq.append(2); dq.append(3)
print(dq.popleft()) # 1 (FIFO)
```

deque는 양 끝 조작이 모두 빠르기 때문에 스택과 큐를 모두 표현할 수 있는 일반화된 구조입니다.

## 이 코드에서 주목할 점

- 파이썬에서는 스택은 list, 큐는 deque가 표준 선택입니다.
- `list.pop(0)`로 큐를 구현하면 O(n)이므로 피해야 합니다.
- 스택과 큐의 차이는 “어느 끝에서 꺼내는가” 하나뿐입니다.
- DFS와 BFS의 구조적 차이도 결국 스택 vs 큐입니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| `list.pop(0)`로 큐를 구현함 | 연산마다 O(n) 이동 발생 | `collections.deque`를 사용합니다 |
| 빈 컨테이너에서 pop함 | `IndexError`가 발생함 | 길이 검사나 예외 처리를 넣습니다 |
| 재귀 깊이 한계를 무시함 | `RecursionError` 가능 | 명시적 스택으로 바꿉니다 |
| BFS에서 visited를 늦게 표시함 | 중복 방문 또는 무한 순회 | enqueue 시점에 바로 표시합니다 |
| 우선순위 큐를 일반 큐처럼 다룸 | 처리 순서가 틀어짐 | 별도로 힙을 사용합니다 |

## 실무에서는 이렇게 쓰입니다

- 함수 호출과 스택 트레이스는 스택 위에서 이해할 수 있습니다.
- 브라우저의 뒤로 가기와 앞으로 가기는 보통 두 개의 스택으로 모델링됩니다.
- RabbitMQ, Kafka 같은 메시지 시스템은 큐 개념의 실전 확장판입니다.
- 운영체제 스케줄러는 FIFO 큐와 우선순위 큐를 조합합니다.
- 그래프 탐색에서는 BFS가 큐를, DFS가 스택 또는 재귀를 사용합니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 재귀 함수를 보는 순간 머릿속에 호출 스택을 같이 그립니다. 입력 깊이가 커질 수 있다면 재귀 한계를 먼저 의식하고, 필요하면 곧바로 명시적 스택 기반 반복으로 바꿉니다.

또한 “작업 큐”라는 말도 뭉뚱그리지 않습니다. 단순 FIFO, 우선순위 큐, 지연 큐, backpressure가 있는 큐는 시스템 거동이 완전히 다릅니다. 이름이 같다고 같은 구조라고 가정하지 않습니다.

## 체크리스트

- [ ] LIFO와 FIFO의 의미를 설명할 수 있습니다
- [ ] 파이썬에서 큐를 list로 구현하면 안 되는 이유를 알고 있습니다
- [ ] 괄호 균형 검사처럼 스택이 자연스러운 문제를 구분할 수 있습니다
- [ ] BFS와 DFS의 차이가 자료구조 선택이라는 점을 이해했습니다
- [ ] deque가 스택과 큐를 모두 지원한다는 점을 알고 있습니다

## 연습 문제

1. 두 개의 스택으로 큐를 구현해 보세요. `enqueue`는 첫 번째 스택에 push하고, `dequeue`는 두 번째 스택이 비었을 때 첫 번째를 옮긴 뒤 pop합니다. 분할 상환 비용은 얼마일까요?

2. 스택으로 후위 표기식 계산기를 구현해 보세요. 예를 들어 `"3 4 + 2 *"`는 14가 되어야 합니다.

3. 위 BFS 코드에서 deque를 list 기반 스택으로 바꿔 보세요. DFS로 바뀌는지, 방문 순서는 어떻게 달라지는지 확인해 보세요.

## 정리 및 다음 단계

스택과 큐는 가장 단순하면서 가장 자주 만나는 ADT입니다. 스택은 LIFO로 함수 호출·파싱·DFS를 설명하고, 큐는 FIFO로 BFS·스케줄링·메시징을 설명합니다. 파이썬에서는 스택은 list, 큐는 `collections.deque`가 표준 선택입니다. 차이는 “어느 끝에서 꺼내는가” 하나지만, 그 하나가 시스템의 동작 방식을 완전히 바꿉니다.

다음 글에서는 키로 값을 거의 즉시 찾게 해 주는 해시 테이블을 다룹니다. 평균 O(1) 탐색이 어떻게 가능한지, 충돌은 어떻게 처리하는지 이어서 보겠습니다.

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
