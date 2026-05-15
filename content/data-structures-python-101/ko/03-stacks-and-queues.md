---
series: data-structures-python-101
episode: 3
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
  - Python
  - 자료구조
  - Stack
  - Queue
  - deque
seo_description: Python의 list와 deque를 활용해 스택(Stack)과 큐(Queue)를 효율적으로 구현하고 연산 성능과 실무 활용 사례를 분석합니다.
last_reviewed: '2026-05-12'
---

# 스택과 큐

이 글은 Data Structures with Python 101 시리즈의 세 번째 글입니다.

## 이 글에서 다룰 문제

- 스택과 큐는 각각 어떤 순서 규칙으로 동작할까요?
- Python에서는 왜 스택에 list를, 큐에 deque를 주로 사용할까요?
- `list.pop(0)`이 큐 구현에 부적절한 이유는 무엇일까요?
- BFS, undo, 작업 처리 같은 문제에 스택과 큐를 어떻게 연결할 수 있을까요?

> 멘탈 모델: 스택과 큐의 핵심은 저장 방식이 아니라 “꺼내는 순서”입니다. LIFO와 FIFO를 구분하는 순간, 어떤 구조를 써야 할지도 거의 자동으로 결정됩니다.

## 왜 이 글이 중요한가

스택과 큐는 가장 기본적인 추상 자료형입니다. 함수 호출 스택, 브라우저 뒤로 가기, 작업 큐, BFS 탐색처럼 운영 코드와 알고리즘 코드의 양쪽에서 모두 반복해서 등장합니다. 이 둘을 정확히 이해하면 더 복잡한 흐름 제어 구조를 훨씬 쉽게 읽을 수 있습니다.

> 스택은 마지막에 넣은 값을 먼저 꺼내고, 큐는 먼저 넣은 값을 먼저 꺼냅니다.

이 차이는 단순해 보이지만, 실제 코드의 동작 순서를 완전히 바꿉니다. 그래서 구현보다 먼저 순서를 머릿속에 고정하는 것이 중요합니다. 웹 서버의 요청 처리, 메시지 브로커의 작업 소비, undo/redo 기능도 결국 이 원리 위에 올라갑니다.

## 핵심 개념 한눈에 보기

> Stack = LIFO, Queue = FIFO

```text
[Stack — LIFO]            [Queue — FIFO]
  push -> | C |           enqueue -> | A | B | C | -> dequeue
          | B |                     ^               ^
          | A |                   rear            front
          +---+
  pop  <- | C | (last)    dequeue <- | A | (first)
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 스택(Stack) | LIFO 원칙으로 동작하는 자료구조입니다 |
| 큐(Queue) | FIFO 원칙으로 동작하는 자료구조입니다 |
| push / pop | 스택에 데이터를 넣고 꺼내는 연산입니다 |
| enqueue / dequeue | 큐에 데이터를 넣고 꺼내는 연산입니다 |
| deque | 양쪽 끝 삽입·삭제를 O(1)에 제공하는 구조입니다 |

## Before / After

큐처럼 보이는 코드를 list로 구현할 때 생기는 문제를 먼저 보겠습니다.

```python
# before: queue with list — pop(0) is O(n)
queue = [1, 2, 3]
queue.append(4)       # enqueue
first = queue.pop(0)  # dequeue — O(n), shifts all elements
```

```python
# after: queue with deque — popleft() is O(1)
from collections import deque
queue = deque([1, 2, 3])
queue.append(4)           # enqueue — O(1)
first = queue.popleft()   # dequeue — O(1)
```

겉보기 기능은 같아도 자료구조가 다르면 비용이 전혀 다릅니다. 큐를 list로 구현하는 실수는 초반에는 티가 안 나지만, 요청량이나 데이터 크기가 커지는 순간 병목으로 드러납니다.

## 단계별 실습

### Step 1: Implement a stack with list

```python
class Stack:
    def __init__(self):
        self._data = []

    def push(self, item):
        self._data.append(item)

    def pop(self):
        if self.is_empty():
            raise IndexError("cannot pop from an empty stack")
        return self._data.pop()

    def peek(self):
        if self.is_empty():
            raise IndexError("cannot peek an empty stack")
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

### Step 2: Implement a queue with deque

```python
from collections import deque

class Queue:
    def __init__(self):
        self._data = deque()

    def enqueue(self, item):
        self._data.append(item)

    def dequeue(self):
        if self.is_empty():
            raise IndexError("cannot dequeue from an empty queue")
        return self._data.popleft()

    def peek(self):
        if self.is_empty():
            raise IndexError("cannot peek an empty queue")
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

### Step 3: Balanced parentheses check — stack in action

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

### Step 4: BFS with a queue

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

### Step 5: Performance comparison — list.pop(0) vs deque.popleft()

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

print(f"list.pop(0):      {list_time:.4f}s")
print(f"deque.popleft():  {deque_time:.4f}s")
print(f"deque is {list_time / deque_time:.0f}x faster")
```

## 이 코드에서 먼저 봐야 할 점

- stack은 끝 append/pop만 필요하므로 list와 자연스럽게 맞습니다.
- queue는 앞에서 꺼내는 연산이 핵심이므로 `popleft()`가 O(1)인 deque가 맞습니다.
- 빈 스택이나 빈 큐에서 값을 꺼내면 예외가 발생하므로 방어 코드가 필요합니다.
- BFS는 큐, DFS는 스택 또는 재귀라는 연결 고리를 기억해 두면 탐색 알고리즘이 훨씬 잘 읽힙니다.

스택과 큐를 배우는 목적은 클래스를 직접 만드는 데 있지 않습니다. “이 흐름이 역순 처리인가, 순차 처리인가”를 구분하고 그에 맞는 기본 구조를 바로 떠올리는 데 있습니다.

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| `list.pop(0)`으로 큐 구현 | 호출마다 O(n)이라 데이터가 커지면 매우 느립니다 | `deque.popleft()`를 사용합니다 |
| 빈 스택/큐에서 pop 호출 | `IndexError`가 발생합니다 | `is_empty()` 검사나 예외 처리를 추가합니다 |
| 스택과 큐를 혼동 | 처리 순서가 바뀌어 버그가 생깁니다 | LIFO와 FIFO를 먼저 분리해 생각합니다 |
| deque에 중간 인덱스 접근 남용 | 중간 접근은 O(n)이라 장점이 사라집니다 | 양끝 연산 중심으로 사용합니다 |
| 무한히 커지는 큐 사용 | 메모리가 계속 증가합니다 | 필요하면 `deque(maxlen=N)`으로 상한을 둡니다 |

## 실무에서 이렇게 쓰입니다

- 브라우저의 뒤로/앞으로 기능은 보통 두 개의 스택으로 모델링합니다.
- undo 기능은 최근 작업을 스택으로 보관합니다.
- 작업 큐와 배치 처리기는 FIFO 순서로 요청을 소비합니다.
- BFS는 방문할 노드를 큐에 넣고 꺼내며 진행합니다.
- 최근 N개 이벤트만 유지하는 로직은 `deque(maxlen=N)`으로 간결하게 구현합니다.

## 실무에서는 이렇게 생각합니다

현업에서는 Stack, Queue 클래스를 직접 정의하는 경우보다 list와 deque를 바로 사용하는 경우가 많습니다. 대신 변수 이름, 주석, 타입 힌트로 “이 구조를 스택처럼 쓴다”는 의도를 드러냅니다.

규모가 커지면 in-memory 큐 대신 Redis, RabbitMQ, Kafka 같은 외부 시스템으로 넘어갑니다. 그래도 기본 원리는 바뀌지 않습니다. deque로 FIFO를 이해해 두면 메시지 큐 시스템도 같은 눈으로 읽을 수 있습니다.

## 체크리스트

- [ ] 스택(LIFO)과 큐(FIFO)의 차이를 설명할 수 있다
- [ ] list로 스택을 구현할 수 있다
- [ ] deque로 큐를 구현할 수 있다
- [ ] 괄호 짝 검사 문제를 스택으로 풀 수 있다
- [ ] `list.pop(0)`이 `deque.popleft()`보다 느린 이유를 설명할 수 있다

## 연습 문제

1. 두 개의 스택으로 큐를 구현해 보세요. `enqueue`, `dequeue`, `peek`를 모두 포함해야 합니다.
2. 스택을 사용해 문자열을 뒤집는 함수를 작성해 보세요.
3. `deque(maxlen=5)`를 만들고 10개의 값을 넣어 본 뒤 어떤 값이 남는지 확인해 보세요.

## 정리 및 다음 글 안내

스택은 LIFO, 큐는 FIFO라는 단순한 규칙 위에서 동작합니다. Python에서는 스택은 list, 큐는 deque라는 관례가 사실상 표준이며, 이 선택은 내부 연산 비용과 정확히 맞닿아 있습니다. 다음 글에서는 빠른 키 기반 조회를 가능하게 만드는 해시 테이블과 dict를 살펴보겠습니다.

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
