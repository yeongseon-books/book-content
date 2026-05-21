---
series: data-structures-python-101
episode: 3
title: "Data Structures with Python 101 (3/10): 스택과 큐"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
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

# Data Structures with Python 101 (3/10): 스택과 큐

이 글은 Data Structures with Python 101 시리즈의 세 번째 글입니다.

## 먼저 던지는 질문

- 스택과 큐는 각각 어떤 순서 규칙으로 동작할까요?
- Python에서는 왜 스택에 list를, 큐에 deque를 주로 사용할까요?
- `list.pop(0)`이 큐 구현에 부적절한 이유는 무엇일까요?

## 큰 그림

![Data Structures with Python 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-python-101/03/03-01-big-picture.ko.png)

*Data Structures with Python 101 3장 흐름 개요*

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



## 타입 힌트 기반 스택 구현

스택은 LIFO(Last In, First Out) 규칙을 따르는 가장 단순한 ADT입니다. Python list의 `append()`와 `pop()`이 이미 LIFO를 제공하지만, 명시적 Stack 클래스를 만들면 "이 컬렉션은 LIFO로만 접근한다"는 의도를 코드에 고정할 수 있습니다.

```python
from __future__ import annotations

from typing import Generic, Iterator, TypeVar

T = TypeVar("T")


class Stack(Generic[T]):
    """list 기반 LIFO 스택입니다."""

    def __init__(self) -> None:
        self._data: list[T] = []

    def push(self, item: T) -> None:
        self._data.append(item)

    def pop(self) -> T:
        if not self._data:
            raise IndexError("pop from empty stack")
        return self._data.pop()

    def peek(self) -> T:
        if not self._data:
            raise IndexError("peek from empty stack")
        return self._data[-1]

    def __len__(self) -> int:
        return len(self._data)

    def __bool__(self) -> bool:
        return bool(self._data)

    def __iter__(self) -> Iterator[T]:
        return reversed(self._data)

    def __repr__(self) -> str:
        return f"Stack(top={self._data[-1]!r}, size={len(self._data)})" if self._data else "Stack(empty)"
```

### 설계 결정 세 가지

1. **`__iter__`가 역순을 반환하는 이유**: 스택은 위에서부터 꺼내는 구조이므로, 순회도 top부터 bottom 순서가 자연스럽습니다.
2. **`__bool__` 제공 이유**: `if stack:` 패턴으로 비어 있는지 간결하게 확인할 수 있습니다. `__len__`만 있으면 Python이 자동으로 truthiness를 판단하지만, 명시적 `__bool__`이 의도를 더 드러냅니다.
3. **중간 접근 금지**: `__getitem__`을 의도적으로 구현하지 않았습니다. 스택에서 중간 원소에 접근하는 것은 ADT 계약 위반이므로, 아예 지원하지 않는 것이 올바릅니다.

## 타입 힌트 기반 큐 구현

큐는 FIFO(First In, First Out) 규칙을 따릅니다. deque를 내부에 사용해 O(1) enqueue/dequeue를 보장합니다.

```python
from __future__ import annotations

from collections import deque
from typing import Generic, Iterator, TypeVar

T = TypeVar("T")


class Queue(Generic[T]):
    """deque 기반 FIFO 큐입니다."""

    def __init__(self, maxsize: int = 0) -> None:
        self._data: deque[T] = deque(maxlen=maxsize if maxsize > 0 else None)
        self._maxsize = maxsize

    def enqueue(self, item: T) -> None:
        if self._maxsize > 0 and len(self._data) >= self._maxsize:
            raise OverflowError("queue is full")
        self._data.append(item)

    def dequeue(self) -> T:
        if not self._data:
            raise IndexError("dequeue from empty queue")
        return self._data.popleft()

    def front(self) -> T:
        if not self._data:
            raise IndexError("front from empty queue")
        return self._data[0]

    @property
    def is_full(self) -> bool:
        return self._maxsize > 0 and len(self._data) >= self._maxsize

    def __len__(self) -> int:
        return len(self._data)

    def __bool__(self) -> bool:
        return bool(self._data)

    def __iter__(self) -> Iterator[T]:
        return iter(self._data)

    def __repr__(self) -> str:
        if not self._data:
            return "Queue(empty)"
        return f"Queue(front={self._data[0]!r}, size={len(self._data)})"
```

### maxsize를 둔 이유

실무에서 큐는 대부분 bounded입니다. 메모리를 무한정 사용하면 OOM(Out of Memory) 위험이 있기 때문입니다. `maxsize=0`은 무한 큐를 의미하고, 양수를 넣으면 가득 찼을 때 `OverflowError`를 발생시킵니다. 이 설계는 `queue.Queue`의 패턴을 따릅니다.

## 메모리 프로파일링: list-stack vs deque-queue

스택과 큐의 메모리 비용을 직접 측정해 보겠습니다.

```python
import sys
from collections import deque


def shallow_size(label: str, obj: object) -> None:
    print(f"{label:>25}: {sys.getsizeof(obj):>8} bytes")


n = 10_000

# Stack: list 기반
stack_data = list(range(n))
shallow_size("list-stack (10k)", stack_data)

# Queue: deque 기반
queue_data = deque(range(n))
shallow_size("deque-queue (10k)", queue_data)

# 비교: deque with maxlen
bounded_queue = deque(range(n), maxlen=n)
shallow_size("bounded deque (10k)", bounded_queue)
```

예상 출력:

```text
        list-stack (10k):    85176 bytes
       deque-queue (10k):    85096 bytes
      bounded deque (10k):    85096 bytes
```

10,000개 수준에서 list와 deque의 얕은 크기는 거의 동일합니다. deque가 유리한 것은 크기가 아니라 앞쪽 삽입/삭제의 시간 복잡도입니다. deque는 내부적으로 고정 크기 블록의 이중 연결 리스트로 구현되어, 양 끝 연산이 O(1)입니다.

### 깊은 메모리 비교: 원소까지 포함

```python
import sys
from collections import deque
from typing import Any


def deep_getsizeof(obj: Any, seen: set[int] | None = None) -> int:
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)
    size = sys.getsizeof(obj)
    if isinstance(obj, (list, tuple, deque, set, frozenset)):
        size += sum(deep_getsizeof(item, seen) for item in obj)
    elif isinstance(obj, dict):
        size += sum(deep_getsizeof(k, seen) + deep_getsizeof(v, seen) for k, v in obj.items())
    return size


n = 10_000
stack_deep = deep_getsizeof(list(range(n)))
queue_deep = deep_getsizeof(deque(range(n)))

print(f"list-stack deep:  {stack_deep:>10} bytes")
print(f"deque-queue deep: {queue_deep:>10} bytes")
```

두 구조 모두 Python int 객체를 동일하게 참조하므로 깊은 크기도 유사합니다. 메모리 관점에서 스택/큐 선택의 핵심은 크기가 아니라, 어떤 끝에서 연산하느냐에 따른 시간 비용입니다.

## 성능 벤치마크: pop(0) vs popleft()

"list를 큐로 쓰면 안 된다"의 근거를 숫자로 확인합니다.

```python
import timeit
from collections import deque


def bench_list_queue(n: int = 10_000) -> None:
    """list를 큐처럼 사용: pop(0)으로 dequeue"""
    q: list[int] = list(range(n))
    for _ in range(n):
        q.pop(0)


def bench_deque_queue(n: int = 10_000) -> None:
    """deque를 큐로 사용: popleft()로 dequeue"""
    q: deque[int] = deque(range(n))
    for _ in range(n):
        q.popleft()


trials = 10

t_list = timeit.timeit(bench_list_queue, number=trials)
t_deque = timeit.timeit(bench_deque_queue, number=trials)

print(f"list.pop(0) x 10k (trials={trials}):   {t_list:.4f}s")
print(f"deque.popleft() x 10k (trials={trials}): {t_deque:.4f}s")
print(f"list is {t_list / t_deque:.1f}x slower")
```

예상 결과:

```text
list.pop(0) x 10k (trials=10):   0.4523s
deque.popleft() x 10k (trials=10): 0.0041s
list is 110.3x slower
```

10,000개 기준으로 이미 100배 이상 차이가 납니다. 원소가 10만 개로 늘면 차이는 1,000배 이상으로 벌어집니다. `pop(0)`은 남은 원소를 전부 앞으로 당기는 O(n) 연산이기 때문입니다.

### push/pop 혼합 시나리오 벤치마크

실무에서는 순수하게 전부 넣고 전부 빼는 경우보다, 넣기와 빼기가 교차되는 패턴이 더 흔합니다.

```python
import timeit
from collections import deque


def bench_mixed_list(n: int = 10_000) -> None:
    q: list[int] = []
    for i in range(n):
        q.append(i)
        if i % 3 == 0 and q:
            q.pop(0)


def bench_mixed_deque(n: int = 10_000) -> None:
    q: deque[int] = deque()
    for i in range(n):
        q.append(i)
        if i % 3 == 0 and q:
            q.popleft()


trials = 10
t1 = timeit.timeit(bench_mixed_list, number=trials)
t2 = timeit.timeit(bench_mixed_deque, number=trials)

print(f"mixed list:  {t1:.4f}s")
print(f"mixed deque: {t2:.4f}s")
print(f"ratio: {t1/t2:.1f}x")
```

혼합 시나리오에서도 deque가 일관되게 빠릅니다. "큐가 필요하면 deque"는 벤치마크가 뒷받침하는 규칙입니다.

## unittest로 Stack과 Queue 검증

```python
import unittest


class TestStack(unittest.TestCase):
    def setUp(self) -> None:
        self.stack: Stack[int] = Stack()

    def test_push_pop_lifo(self) -> None:
        self.stack.push(1)
        self.stack.push(2)
        self.stack.push(3)
        self.assertEqual(self.stack.pop(), 3)
        self.assertEqual(self.stack.pop(), 2)
        self.assertEqual(self.stack.pop(), 1)

    def test_peek_does_not_remove(self) -> None:
        self.stack.push(42)
        self.assertEqual(self.stack.peek(), 42)
        self.assertEqual(len(self.stack), 1)

    def test_pop_empty_raises(self) -> None:
        with self.assertRaises(IndexError):
            self.stack.pop()

    def test_bool(self) -> None:
        self.assertFalse(self.stack)
        self.stack.push(1)
        self.assertTrue(self.stack)

    def test_iter_top_first(self) -> None:
        for i in range(5):
            self.stack.push(i)
        self.assertEqual(list(self.stack), [4, 3, 2, 1, 0])


class TestQueue(unittest.TestCase):
    def setUp(self) -> None:
        self.queue: Queue[str] = Queue()

    def test_enqueue_dequeue_fifo(self) -> None:
        self.queue.enqueue("a")
        self.queue.enqueue("b")
        self.queue.enqueue("c")
        self.assertEqual(self.queue.dequeue(), "a")
        self.assertEqual(self.queue.dequeue(), "b")
        self.assertEqual(self.queue.dequeue(), "c")

    def test_front_does_not_remove(self) -> None:
        self.queue.enqueue("x")
        self.assertEqual(self.queue.front(), "x")
        self.assertEqual(len(self.queue), 1)

    def test_dequeue_empty_raises(self) -> None:
        with self.assertRaises(IndexError):
            self.queue.dequeue()

    def test_bounded_queue_overflow(self) -> None:
        bq: Queue[int] = Queue(maxsize=3)
        bq.enqueue(1)
        bq.enqueue(2)
        bq.enqueue(3)
        with self.assertRaises(OverflowError):
            bq.enqueue(4)

    def test_is_full(self) -> None:
        bq: Queue[int] = Queue(maxsize=2)
        self.assertFalse(bq.is_full)
        bq.enqueue(1)
        bq.enqueue(2)
        self.assertTrue(bq.is_full)


if __name__ == "__main__":
    unittest.main()
```

이 테스트는 여섯 가지 경계를 검증합니다.

1. **LIFO/FIFO 순서**: 넣은 순서와 꺼내는 순서가 각각의 규칙을 따르는지 확인합니다.
2. **peek/front 비파괴**: 확인 연산이 원소를 제거하지 않는지 확인합니다.
3. **빈 상태 예외**: 빈 구조에서 꺼내면 명확한 에러가 발생하는지 확인합니다.
4. **bounded overflow**: 크기 제한을 초과하면 OverflowError가 나는지 확인합니다.
5. **truthiness**: 빈 스택/큐가 falsy인지 확인합니다.
6. **순회 순서**: 스택은 top-first, 큐는 front-first로 순회하는지 확인합니다.

## 실무 패턴: 스택과 큐의 응용

### 괄호 검증 (스택)

```python
def is_balanced(expression: str) -> bool:
    """괄호 짝이 맞는지 스택으로 검증합니다."""
    pairs = {"(": ")", "[": "]", "{": "}"}
    stack: list[str] = []

    for char in expression:
        if char in pairs:
            stack.append(char)
        elif char in pairs.values():
            if not stack:
                return False
            if pairs[stack.pop()] != char:
                return False

    return len(stack) == 0


assert is_balanced("({[]})")
assert not is_balanced("({[}])")
assert is_balanced("")
```

### BFS 레벨 순회 (큐)

```python
from collections import deque
from typing import Any


def bfs_levels(graph: dict[str, list[str]], start: str) -> list[list[str]]:
    """그래프를 BFS로 순회하며 레벨별로 노드를 반환합니다."""
    visited: set[str] = {start}
    queue: deque[tuple[str, int]] = deque([(start, 0)])
    levels: list[list[str]] = []

    while queue:
        node, level = queue.popleft()
        if level == len(levels):
            levels.append([])
        levels[level].append(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, level + 1))

    return levels


graph = {"A": ["B", "C"], "B": ["D"], "C": ["D", "E"], "D": [], "E": []}
print(bfs_levels(graph, "A"))
# [['A'], ['B', 'C'], ['D', 'E']]
```

이 두 패턴은 스택과 큐의 가장 대표적인 실무 적용입니다. 괄호 검증은 "가장 최근에 연 것을 먼저 닫아야 한다"는 LIFO 규칙, BFS는 "먼저 발견한 것을 먼저 처리한다"는 FIFO 규칙을 그대로 반영합니다.

## 처음 질문으로 돌아가기

- **스택과 큐는 각각 어떤 순서 규칙으로 동작할까요?**
  - 스택은 LIFO(Last In, First Out)로 가장 나중에 넣은 원소를 먼저 꺼냅니다. 큐는 FIFO(First In, First Out)로 가장 먼저 넣은 원소를 먼저 꺼냅니다. 괄호 검증이 스택, BFS가 큐를 사용하는 이유가 바로 이 순서 규칙 때문입니다.
- **Python에서는 왜 스택에 list를, 큐에 deque를 주로 사용할까요?**
  - list의 `append()`/`pop()`은 끝 연산이므로 O(1)입니다. 스택은 한쪽 끝에서만 동작하므로 list가 최적입니다. 큐는 양쪽 끝(뒤에 넣고 앞에서 빼기)을 쓰는데, list의 `pop(0)`은 O(n)입니다. deque의 `popleft()`는 O(1)이므로 큐에는 deque가 맞습니다.
- **`list.pop(0)`이 큐 구현에 부적절한 이유는 무엇일까요?**
  - list는 연속 배열이므로 앞 원소를 제거하면 나머지 원소를 전부 한 칸 앞으로 당겨야 합니다. 벤치마크에서 확인했듯이 10,000개 기준으로 deque보다 100배 이상 느리고, 원소가 많을수록 차이는 더 벌어집니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Structures with Python 101 (1/10): 자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [Data Structures with Python 101 (2/10): 배열과 리스트](./02-arrays-and-lists.md)
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
- [book-examples 저장소 — data-structures-python-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/data-structures-python-101/ko)
- [GeeksforGeeks — Stack Data Structure](https://www.geeksforgeeks.org/stack-data-structure/)
- [Visualgo — Stack and Queue Visualization](https://visualgo.net/en/list)

Tags: Python, 자료구조, Stack, Queue, deque
