---
series: data-structures-101
episode: 3
title: "Data Structures 101 (3/10): 연결 리스트"
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
  - 연결 리스트
  - 포인터
  - 노드
  - 메모리
seo_description: 노드와 포인터 기반의 연결 리스트 구조를 이해하고 단일 및 이중 연결 리스트의 특징과 배열 대비 장단점을 상세히 다룹니다.
last_reviewed: '2026-05-12'
---

# Data Structures 101 (3/10): 연결 리스트

> 단일 연결 리스트는 노드마다 `next` 포인터만 가지므로 메모리는 덜 쓰지만 역방향 이동이 어렵습니다. 이중 연결 리스트는 `prev`와 `next`를 모두 가져 양방향 순회와 양 끝 조작이 편해지는 대신, 노드당 포인터 하나를 더 부담합니다.

이 글은 Data Structures 101 시리즈의 세 번째 글입니다.

![Data Structures 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-101/03/03-01-big-picture.ko.png)
*Data Structures 101 3장 흐름 개요*

## 이 글에서 다룰 문제

- 단일 연결 리스트와 이중 연결 리스트는 구조적으로 무엇이 다를까요?
- 연결 리스트는 왜 양 끝 삽입·삭제에 강하고, 왜 인덱스 접근에는 약할까요?
- 포인터 조작을 직접 구현할 때 어떤 실수를 가장 조심해야 할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

연결 리스트는 운영체제 커널, LRU 캐시, 메모리 할당기 같은 시스템 소프트웨어의 핵심 구성 요소입니다. 트리와 그래프 같은 더 복잡한 구조도 결국 포인터 연결을 이해해야 자연스럽게 읽힙니다.

> 배열이 위치로 데이터를 묶는다면, 연결 리스트는 관계로 데이터를 묶습니다.

## 핵심 한눈에 보기

> 단일 연결 리스트는 노드마다 `next` 포인터만 가지므로 메모리는 덜 쓰지만 역방향 이동이 어렵습니다. 이중 연결 리스트는 `prev`와 `next`를 모두 가져 양방향 순회와 양 끝 조작이 편해지는 대신, 노드당 포인터 하나를 더 부담합니다.

```text
Singly linked list
[10 | →] → [20 | →] → [30 | →] → [40 | None]
  ↑
 head

Doubly linked list
None ← [10 | ↔] ↔ [20 | ↔] ↔ [30 | ↔] ↔ [40] → None
         ↑                              ↑
        head                          tail
```

| 용어 | 의미 |
| --- | --- |
| 노드 | 값과 포인터를 담는 기본 단위 |
| 포인터 | 다른 노드를 가리키는 참조 |
| head | 첫 번째 노드를 가리키는 참조 |
| tail | 마지막 노드를 가리키는 참조 |
| sentinel | 경계 조건 처리를 단순화하는 더미 노드 |

## 전후 비교

**Before — prepend on an array:**

```python
data = list(range(1_000_000))
data.insert(0, -1)         # all 1,000,000 elements shift one slot: O(n)
```

**After — prepend on a linked list:**

```python
class Node:
    __slots__ = ("value", "next")
    def __init__(self, value, next=None):
        self.value, self.next = value, next

head = None
for v in range(1_000_000):
    head = Node(v, head)   # O(1) insert each time
```

배열은 위치를 유지해야 하지만 연결 리스트는 관계만 다시 연결하면 됩니다. 그래서 삽입 비용의 성격이 다릅니다.

## 단계별로 따라하기

### 1단계: 단일 연결 리스트 구현

```python
class Node:
    __slots__ = ("value", "next")
    def __init__(self, value, next=None):
        self.value = value
        self.next = next

class SinglyLinkedList:
    def __init__(self):
        self.head = None
        self._size = 0

    def push_front(self, value):
        self.head = Node(value, self.head)
        self._size += 1

    def pop_front(self):
        if self.head is None:
            raise IndexError("empty list")
        value = self.head.value
        self.head = self.head.next
        self._size -= 1
        return value

    def __len__(self):
        return self._size

    def __iter__(self):
        cur = self.head
        while cur is not None:
            yield cur.value
            cur = cur.next

lst = SinglyLinkedList()
for v in [3, 2, 1]:
    lst.push_front(v)
print(list(lst))   # [1, 2, 3]
```

`push_front`와 `pop_front`는 head 포인터만 바꾸면 되므로 둘 다 O(1)입니다.

### 2단계: 중간 노드 삭제

```python
def remove_value(self, target):
    """Remove the first node whose value equals target."""
    prev, cur = None, self.head
    while cur is not None:
        if cur.value == target:
            if prev is None:
                self.head = cur.next
            else:
                prev.next = cur.next
            self._size -= 1
            return True
        prev, cur = cur, cur.next
    return False

SinglyLinkedList.remove_value = remove_value

lst = SinglyLinkedList()
for v in [3, 2, 1]:
    lst.push_front(v)
lst.remove_value(2)
print(list(lst))   # [1, 3]
```

삭제 자체는 포인터 두 개만 만지면 되지만, 삭제 대상을 찾는 과정은 선형 탐색이어서 O(n)입니다.

### 3단계: 센티널을 둔 이중 연결 리스트

```python
class DNode:
    __slots__ = ("value", "prev", "next")
    def __init__(self, value):
        self.value = value
        self.prev = None
        self.next = None

class DoublyLinkedList:
    def __init__(self):
        self._head = DNode(None)        # sentinel head
        self._tail = DNode(None)        # sentinel tail
        self._head.next = self._tail
        self._tail.prev = self._head
        self._size = 0

    def push_back(self, value):
        node = DNode(value)
        last = self._tail.prev
        last.next = node
        node.prev = last
        node.next = self._tail
        self._tail.prev = node
        self._size += 1

    def remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev
        self._size -= 1

    def __iter__(self):
        cur = self._head.next
        while cur is not self._tail:
            yield cur.value
            cur = cur.next
```

sentinel을 두면 빈 리스트, 첫 노드, 마지막 노드 같은 특수 분기가 크게 줄어듭니다. 코드가 짧아지고 버그도 줄어드는 이유입니다.

### 4단계: 배열과 연결 리스트 성능 차이

```python
import time
from collections import deque

N = 100_000

# 1. Prepend
data = []
start = time.perf_counter()
for i in range(N):
    data.insert(0, i)
print(f"list.insert(0): {(time.perf_counter() - start) * 1000:.0f} ms")

dq = deque()
start = time.perf_counter()
for i in range(N):
    dq.appendleft(i)
print(f"deque.appendleft: {(time.perf_counter() - start) * 1000:.0f} ms")
```

`deque`는 양끝 조작이 O(1)에 가깝도록 설계되어 있습니다. 앞쪽 삽입이 지배적인 워크로드라면 배열보다 훨씬 자연스럽습니다.

### 5단계: 인덱스 접근의 한계

```python
import time
from collections import deque

N = 100_000

lst = list(range(N))
dq = deque(range(N))

start = time.perf_counter()
for _ in range(1000):
    _ = lst[N // 2]
print(f"list[mid]: {(time.perf_counter() - start) * 1e6:.0f} us")

start = time.perf_counter()
for _ in range(1000):
    _ = dq[N // 2]
print(f"deque[mid]: {(time.perf_counter() - start) * 1e6:.0f} us")
```

리스트는 O(1) 인덱싱이 가능하지만, 연결 리스트 계열은 중간 노드에 닿으려면 따라가야 합니다. 결국 어떤 연산이 주가 되는지가 선택을 결정합니다.

## 이 코드에서 주목할 점

- 노드는 메모리에 흩어져 있어 배열보다 캐시 친화성이 낮습니다.
- 각 노드는 값 외에 포인터 비용을 추가로 가집니다.
- 양 끝 연산은 O(1)이지만 임의 접근은 O(n)입니다.
- sentinel은 분기 수를 줄여 구현을 안정적으로 만듭니다.

## 단일 vs 이중 연결 리스트 비교

| 항목 | 단일 연결 리스트 | 이중 연결 리스트 |
| --- | --- | --- |
| 포인터 수 | 노드당 1개 (next) | 노드당 2개 (prev, next) |
| 메모리 사용 | 더 적음 | 노드당 포인터 1개 추가 |
| 역방향 순회 | 불가 (O(n) 재순회 필요) | O(1) 역방향 이동 |
| 앞 삽입/삭제 | O(1) | O(1) |
| 끝 삽입/삭제 | tail 없이 O(n), tail 있으면 O(1) | O(1) |
| 중간 노드 삭제 | prev 찾기 O(n) 필요 | 노드 참조만 있으면 O(1) |
| 구현 복잡도 | 단순 | 포인터 관리 두 배 |

## 디버깅 시나리오

### 시나리오 1: head 갱신을 빠뜨려서 리스트를 잃어버린 경우

```python
class Node:
    def __init__(self, val, next=None):
        self.val = val
        self.next = next

# 잘못된 구현: head를 갱신하지 않음
def bad_push_front(val):
    new_node = Node(val)
    # 실수: head를 로컬 변수로만 갱신
    # head = new_node  <-- 이 방식은 외부 head에 영향 없음

# 올바른 구현: 클래스로 상태를 감쌉니다
class LinkedList:
    def __init__(self):
        self.head = None

    def push_front(self, val):
        self.head = Node(val, self.head)  # 명시적 head 갱신
```

### 시나리오 2: 이중 연결 리스트에서 prev 갱신 누락

```python
# 잘못된 삽입 — prev 연결을 빠뜨림
def bad_insert_after(prev_node, new_val):
    new_node = DNode(new_val)
    new_node.next = prev_node.next
    prev_node.next = new_node
    # 실수: new_node.next.prev 갱신 누락!
    # 이제 역방향 순회가 깨집니다

# 올바른 삽입
def good_insert_after(prev_node, new_val):
    new_node = DNode(new_val)
    next_node = prev_node.next
    new_node.next = next_node
    new_node.prev = prev_node
    prev_node.next = new_node
    if next_node is not None:
        next_node.prev = new_node  # 반드시 갱신
```

### 시나리오 3: 빈 리스트 분기를 빠뜨린 경우

```python
# 잘못된 pop — 빈 리스트 처리 없음
def bad_pop_front(lst):
    value = lst.head.value  # head가 None이면 AttributeError!
    lst.head = lst.head.next
    return value

# 올바른 pop
def good_pop_front(lst):
    if lst.head is None:
        raise IndexError("pop from empty list")
    value = lst.head.value
    lst.head = lst.head.next
    if lst.head is not None:
        lst.head.prev = None  # 이중 연결일 경우
    return value
```

## 자주 하는 실수

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 배열처럼 인덱스로 계속 접근함 | 매번 O(n) 순회 발생 | 임의 접근이 많다면 배열을 선택합니다 |
| head 갱신을 놓침 | 리스트 전체를 잃어버림 | head 변경 지점을 명시적으로 관리합니다 |
| 삭제 시 prev 갱신을 빠뜨림 | 이중 연결 리스트가 깨짐 | 양방향 포인터를 항상 함께 갱신합니다 |
| 빈 리스트 분기를 빠뜨림 | `NoneType` 오류가 남 | sentinel로 경계 조건을 줄입니다 |
| 메모리 해제를 과도하게 걱정함 | 파이썬과 C/C++ 모델을 혼동함 | 파이썬은 GC, 저수준 언어는 명시 해제를 구분합니다 |

## 실무에서는 이렇게 쓰입니다

- Linux 커널은 `list_head`라는 이중 연결 리스트를 광범위하게 사용합니다.
- LRU 캐시는 해시 테이블과 이중 연결 리스트를 조합해 O(1) 갱신을 만듭니다.
- 메모리 할당기는 free block 목록을 연결 리스트로 관리합니다.
- 음악 플레이어의 이전/다음 트랙 이동은 이중 연결 리스트 모델과 잘 맞습니다.
- 텍스트 편집기의 rope 같은 구조도 연결 리스트 계열 아이디어를 확장한 예입니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 교과서적인 단일 연결 리스트를 실무 기본값으로 두지 않습니다. 많은 경우 배열과 deque가 캐시 친화성 덕분에 더 빠릅니다. 연결 리스트가 진짜 빛나는 순간은 양 끝만 자주 다루거나, 다른 구조가 이미 노드 참조를 직접 들고 있어 삭제를 O(1)로 할 수 있을 때입니다.

또한 포인터 조작은 머릿속으로만 추적하지 않습니다. 노드와 화살표를 종이에 그리며 한 단계씩 확인하는 습관이 버그를 가장 확실하게 줄입니다.

## 운영 체크리스트

- [ ] 단일 연결 리스트와 이중 연결 리스트의 구조 차이를 설명할 수 있습니다
- [ ] 양 끝 삽입이 O(1)이고 임의 접근이 O(n)인 이유를 이해했습니다
- [ ] sentinel 노드의 가치를 설명할 수 있습니다
- [ ] 연결 리스트가 배열보다 유리한 워크로드를 구분할 수 있습니다
- [ ] 파이썬 `deque`가 어떤 계열 구조와 가까운지 알고 있습니다

## 연습 문제

1. 위 `SinglyLinkedList`에 `reverse()`를 추가해 보세요. 새 리스트를 만들지 말고 포인터만 뒤집어야 합니다.

2. 단일 연결 리스트에 사이클이 있는지 검사하는 함수를 구현해 보세요. 힌트는 빠른 포인터와 느린 포인터입니다.

3. 정렬된 두 단일 연결 리스트를 하나의 정렬된 리스트로 합치는 함수를 작성해 보세요. 새 노드를 만들지 말고 기존 노드를 재사용해야 합니다.

## 정리 및 다음 단계

연결 리스트는 노드를 포인터로 이어 붙여 양 끝이나 이미 알고 있는 위치에서의 삽입·삭제를 O(1)로 만듭니다. 대신 임의 접근은 O(n)이고 캐시 친화성도 배열보다 떨어집니다. 단일과 이중 연결 리스트의 차이는 포인터 하나를 더 쓰는 대신 양방향 순회와 구현 편의를 얻느냐의 선택입니다.

다음 글에서는 배열이나 연결 리스트 위에 세워지는 두 ADT, 스택과 큐를 살펴봅니다. LIFO와 FIFO라는 단순한 규칙이 어떻게 강력한 추상화가 되는지 이어서 보겠습니다.

## 처음 질문으로 돌아가기

- **단일 연결 리스트와 이중 연결 리스트는 구조적으로 무엇이 다를까요?**
  - 단일은 `next` 포인터만 있어 한 방향으로만 이동 가능합니다. 이중은 `prev`와 `next` 모두 있어 양방향 이동과 O(1) 노드 삭제가 가능합니다. 대신 노드당 메모리가 포인터 하나만큼 더 필요합니다.
- **연결 리스트는 왜 양 끝 삽입·삭제에 강하고, 왜 인덱스 접근에는 약할까요?**
  - 양 끝 조작은 head/tail 포인터 몇 개만 바꾸면 되므로 O(1)입니다. 반면 임의 위치 접근은 head부터 따라가야 하므로 O(n)입니다. 주소 계산으로 바로 이동하는 배열과 다른 점입니다.
- **포인터 조작을 직접 구현할 때 어떤 실수를 가장 조심해야 할까요?**
  - head 갱신 누락, 이중 연결 리스트에서 prev 갱신 빠뜨림, 빈 리스트 처리 누락이 가장 흔한 세 가지 실수입니다. 포인터 변경 순서를 그림으로 그리며 확인하는 습관이 중요합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Structures 101 (1/10): 자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [Data Structures 101 (2/10): 배열과 동적 배열](./02-arrays-and-dynamic-arrays.md)
- **Data Structures 101 (3/10): 연결 리스트 (현재 글)**
- [Data Structures 101 (4/10): 스택과 큐](./04-stacks-and-queues.md)
- [Data Structures 101 (5/10): 해시 테이블](./05-hash-tables.md)
- [Data Structures 101 (6/10): 트리](./06-trees.md)
- [Data Structures 101 (7/10): 이진 탐색 트리](./07-binary-search-trees.md)
- [Data Structures 101 (8/10): 힙](./08-heaps.md)
- [Data Structures 101 (9/10): 그래프](./09-graphs.md)
- [자료구조 선택 기준](./10-choosing-data-structures.md)

<!-- toc:end -->

## 참고 자료

- [Data Structures 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/data-structures-101/ko)

- [Open Data Structures — Chapter 3 Linked Lists](https://opendatastructures.org/ods-python/3_Linked_Lists.html)
- [Linux Kernel `list.h`](https://github.com/torvalds/linux/blob/master/include/linux/list.h)
- [Wikipedia — Linked List](https://en.wikipedia.org/wiki/Linked_list)
- [Python collections.deque docs](https://docs.python.org/3/library/collections.html#collections.deque)

Tags: Computer Science, 자료구조, 연결 리스트, 포인터, 노드, 메모리
