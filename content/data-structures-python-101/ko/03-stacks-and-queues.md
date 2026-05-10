---
series: data-structures-python-101
episode: 3
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
  - Python
  - 자료구조
  - Stack
  - Queue
  - deque
seo_description: Python으로 스택과 큐를 구현하고 실무 활용 패턴을 설명합니다.
last_reviewed: '2026-05-04'
---

# 스택과 큐

> Data Structures with Python 101 시리즈 (3/10)


## 이 글에서 다룰 문제

스택과 큐는 가장 기본적인 추상 자료형입니다. 함수 호출 스택, 브라우저 뒤로 가기, 작업 큐, BFS 탐색 등 컴퓨터 과학 전반에서 사용됩니다. 이 두 가지를 이해하면 복잡한 알고리즘의 기반을 갖추게 됩니다.

> 스택은 "마지막에 넣은 것을 먼저 꺼내는" 구조이고, 큐는 "먼저 넣은 것을 먼저 꺼내는" 구조입니다.

웹 서버의 요청 처리, 메시지 브로커, 실행 취소(undo) 기능 등 실무의 핵심 패턴이 스택과 큐에 기반합니다.

## 핵심 개념 잡기

> 스택 = LIFO(Last In, First Out), 큐 = FIFO(First In, First Out)

```
[스택 — LIFO]           [큐 — FIFO]
  push → │ C │          enqueue → │ A │ B │ C │ → dequeue
         │ B │                    ↑               ↑
         │ A │                  뒤(rear)       앞(front)
         └───┘
  pop  ← │ C │ (마지막)  dequeue ← │ A │ (처음)
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 스택(Stack) | LIFO 원칙으로 동작하는 자료구조입니다 |
| 큐(Queue) | FIFO 원칙으로 동작하는 자료구조입니다 |
| push/pop | 스택에 원소를 넣고 꺼내는 연산입니다 |
| enqueue/dequeue | 큐에 원소를 넣고 꺼내는 연산입니다 |
| deque | 양쪽 끝에서 O(1) 삽입·삭제가 가능한 자료구조입니다 |

## Before / After

list로 큐를 구현한 비효율적 코드와 deque를 사용한 효율적 코드를 비교합니다.

```python
# before: list로 큐 구현 — pop(0)이 O(n)
queue = [1, 2, 3]
queue.append(4)       # enqueue
first = queue.pop(0)  # dequeue — O(n), 모든 원소 이동
```

```python
# after: deque로 큐 구현 — popleft()가 O(1)
from collections import deque
queue = deque([1, 2, 3])
queue.append(4)           # enqueue — O(1)
first = queue.popleft()   # dequeue — O(1)
```

## 단계별 실습

### Step 1: list로 스택 구현

```python
class Stack:
    def __init__(self):
        self._data = []

    def push(self, item):
        self._data.append(item)

    def pop(self):
        if self.is_empty():
            raise IndexError("빈 스택에서 pop 할 수 없습니다")
        return self._data.pop()

    def peek(self):
        if self.is_empty():
            raise IndexError("빈 스택에서 peek 할 수 없습니다")
        return self._data[-1]

    def is_empty(self):
        return len(self._data) == 0

    def __len__(self):
        return len(self._data)

stack = Stack()
stack.push("a")
stack.push("b")
stack.push("c")
print(stack.pop())   # "c"
print(stack.peek())  # "b"
print(len(stack))    # 2
```

### Step 2: deque로 큐 구현

```python
from collections import deque

class Queue:
    def __init__(self):
        self._data = deque()

    def enqueue(self, item):
        self._data.append(item)

    def dequeue(self):
        if self.is_empty():
            raise IndexError("빈 큐에서 dequeue 할 수 없습니다")
        return self._data.popleft()

    def peek(self):
        if self.is_empty():
            raise IndexError("빈 큐에서 peek 할 수 없습니다")
        return self._data[0]

    def is_empty(self):
        return len(self._data) == 0

    def __len__(self):
        return len(self._data)

queue = Queue()
queue.enqueue("task1")
queue.enqueue("task2")
queue.enqueue("task3")
print(queue.dequeue())  # "task1"
print(queue.peek())     # "task2"
```

### Step 3: 괄호 짝 검사 — 스택 활용

```python
def is_balanced(text: str) -> bool:
    pairs = {"(": ")", "[": "]", "{": "}"}
    stack = []
    for char in text:
        if char in pairs:
            stack.append(char)
        elif char in pairs.values():
            if not stack or pairs[stack.pop()] != char:
                return False
    return len(stack) == 0

print(is_balanced("({[]})"))   # True
print(is_balanced("({[})"))    # False
print(is_balanced("((()"))     # False
```

### Step 4: BFS에서 큐 활용

```python
from collections import deque

def bfs(graph: dict, start: str) -> list:
    visited = []
    queue = deque([start])
    seen = {start}
    while queue:
        node = queue.popleft()
        visited.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return visited

graph = {
    "A": ["B", "C"],
    "B": ["D"],
    "C": ["D", "E"],
    "D": [],
    "E": [],
}
print(bfs(graph, "A"))  # ['A', 'B', 'C', 'D', 'E']
```

### Step 5: 성능 비교 — list.pop(0) vs deque.popleft()

```python
import time
from collections import deque

n = 100_000

# list.pop(0) — O(n) per operation
data_list = list(range(n))
start = time.perf_counter()
while data_list:
    data_list.pop(0)
list_time = time.perf_counter() - start

# deque.popleft() — O(1) per operation
data_deque = deque(range(n))
start = time.perf_counter()
while data_deque:
    data_deque.popleft()
deque_time = time.perf_counter() - start

print(f"list.pop(0):      {list_time:.4f}초")
print(f"deque.popleft():  {deque_time:.4f}초")
print(f"deque가 {list_time / deque_time:.0f}배 빠릅니다")
```

## 이 코드에서 주목할 점

- list의 append/pop은 O(1)이므로 스택 구현에 적합합니다
- deque의 appendleft/popleft도 O(1)이므로 큐 구현에 적합합니다
- 빈 스택/큐에서 pop하면 에러가 발생하므로 방어 코드가 필요합니다
- BFS는 큐, DFS는 스택(또는 재귀)을 사용하는 것이 정석입니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| list.pop(0)으로 큐 구현 | O(n)이라 대규모 데이터에서 느립니다 | deque.popleft()를 사용합니다 |
| 빈 스택/큐에서 pop 호출 | IndexError가 발생합니다 | is_empty() 검사 후 pop합니다 |
| 스택과 큐를 혼동 | 잘못된 순서로 데이터를 처리합니다 | LIFO/FIFO 원칙을 명확히 구분합니다 |
| deque에 인덱스 접근 남용 | 중간 인덱스 접근은 O(n)입니다 | 양쪽 끝 연산만 사용하고, 중간 접근이 필요하면 list를 사용합니다 |
| maxlen 설정 없이 무한 큐 사용 | 메모리가 계속 증가합니다 | deque(maxlen=N)으로 크기를 제한합니다 |

## 실무에서 이렇게 쓰입니다

- 웹 브라우저의 뒤로/앞으로 기능을 스택 두 개로 구현합니다
- 실행 취소(undo) 기능을 스택으로 구현합니다
- 작업 큐(task queue)에서 요청을 FIFO로 처리합니다
- BFS 탐색에서 방문할 노드를 큐로 관리합니다
- rate limiter에서 최근 N개 요청을 deque(maxlen=N)으로 추적합니다

## 현업 개발자는 이렇게 생각합니다

직접 Stack, Queue 클래스를 만들기보다 list와 deque를 직접 사용하는 경우가 많습니다. 팀 내에서 "이 변수는 스택으로 사용합니다"라는 주석이나 타입 힌트로 의도를 전달합니다.

대규모 시스템에서는 in-memory 큐 대신 Redis, RabbitMQ, Kafka 같은 메시지 큐를 사용합니다. 하지만 기본 원리는 동일합니다. deque로 큐의 동작을 이해하면 메시지 큐 시스템도 쉽게 파악할 수 있습니다.

## 체크리스트

- [ ] 스택(LIFO)과 큐(FIFO)의 차이를 설명할 수 있다
- [ ] list로 스택을 구현할 수 있다
- [ ] deque로 큐를 구현할 수 있다
- [ ] 괄호 짝 검사를 스택으로 풀 수 있다
- [ ] list.pop(0)이 deque.popleft()보다 느린 이유를 설명할 수 있다

## 정리 및 다음 글 안내

스택은 LIFO, 큐는 FIFO 원칙으로 동작합니다. Python에서 스택은 list, 큐는 deque로 구현하는 것이 표준입니다. 다음 글에서는 O(1) 검색을 가능하게 하는 해시 테이블과 dict를 다룹니다.

<!-- toc:begin -->
- [자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [배열과 리스트](./02-arrays-and-lists.md)
- **스택과 큐 (현재 글)**
- 해시 테이블과 dict (예정)
- 연결 리스트 (예정)
- 트리와 이진 트리 (예정)
- 힙과 우선순위 큐 (예정)
- 그래프 표현 (예정)
- set과 집합 연산 (예정)
- 자료구조 선택 기준 (예정)
<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — collections.deque](https://docs.python.org/3/library/collections.html#collections.deque)
- [Real Python — Stacks and Queues in Python](https://realpython.com/queue-in-python/)
- [GeeksforGeeks — Stack Data Structure](https://www.geeksforgeeks.org/stack-data-structure/)
- [Visualgo — Stack and Queue Visualization](https://visualgo.net/en/list)

Tags: Python, 자료구조, Stack, Queue, deque
