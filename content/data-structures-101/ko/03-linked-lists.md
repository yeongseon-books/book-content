---
series: data-structures-101
episode: 3
title: 연결 리스트
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
  - 연결 리스트
  - 포인터
  - 노드
  - 메모리
seo_description: 단일/이중 연결 리스트의 구조, 배열과의 차이, 그리고 실무에서 언제 연결 리스트가 더 적합한지 살펴봅니다.
last_reviewed: '2026-05-04'
---

# 연결 리스트

> Data Structures 101 시리즈 (3/10)


## 이 글에서 다룰 문제

연결 리스트는 운영체제 커널·LRU 캐시·자유 메모리 리스트 등 시스템 소프트웨어의 핵심 자료구조입니다. 또한 트리·그래프 등 더 복잡한 자료구조의 기반이 됩니다. 포인터 조작은 처음에는 어렵지만 한 번 익히면 훨씬 다양한 자료구조를 다룰 수 있습니다.

> 배열은 "위치"로 데이터를 묶고, 연결 리스트는 "관계"로 데이터를 묶습니다.

## 개념 한눈에 보기

> 단일 연결 리스트는 각 노드가 다음 노드 주소만 가지므로 메모리를 적게 쓰지만 역방향 순회가 어렵습니다. 이중 연결 리스트는 양방향 포인터를 가져서 양쪽 모두 빠르지만 노드당 메모리가 더 듭니다.

```text
단일 연결 리스트
[10 | →] → [20 | →] → [30 | →] → [40 | None]
  ↑
 head

이중 연결 리스트
None ← [10 | ↔] ↔ [20 | ↔] ↔ [30 | ↔] ↔ [40] → None
         ↑                              ↑
        head                          tail
```

## Before / After

**Before — 배열에서 맨 앞에 값 추가:**

```python
data = list(range(1_000_000))
data.insert(0, -1)         # 1,000,000개 모두 한 칸씩 이동: O(n)
```

**After — 연결 리스트에서 맨 앞에 값 추가:**

```python
class Node:
    __slots__ = ("value", "next")
    def __init__(self, value, next=None):
        self.value, self.next = value, next


head = None
for v in range(1_000_000):
    head = Node(v, head)   # 매번 O(1) 삽입
```

## 실습: 단계별로 따라하기

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

`push_front`와 `pop_front`는 헤드 포인터만 바꾸므로 O(1)입니다.

### 2단계: 중간 노드 삭제

```python
def remove_value(self, target):
    """첫 번째로 만난 target 노드를 삭제."""
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

삭제 자체는 포인터 두 개만 수정하므로 O(1)이지만, 대상 노드를 찾기 위한 탐색이 O(n)입니다.

### 3단계: 이중 연결 리스트와 센티넬

```python
class DNode:
    __slots__ = ("value", "prev", "next")
    def __init__(self, value):
        self.value = value
        self.prev = None
        self.next = None


class DoublyLinkedList:
    def __init__(self):
        self._head = DNode(None)        # 센티넬 머리
        self._tail = DNode(None)        # 센티넬 꼬리
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

센티넬 노드 덕분에 빈 리스트·맨 앞·맨 뒤에 대한 분기를 없앨 수 있습니다. 코드가 짧아지고 버그도 줄어듭니다.

### 4단계: 배열과 연결 리스트 성능 비교

```python
import time
from collections import deque

N = 100_000

# 1. 맨 앞 삽입
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

deque는 이중 연결 리스트의 일종(블록 단위)이라서 양 끝 삽입이 O(1)입니다. 맨 앞 삽입이 자주 일어나면 deque를 선택해야 합니다.

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
print(f"list[mid]: {(time.perf_counter() - start) * 1e6:.0f} µs")

start = time.perf_counter()
for _ in range(1000):
    _ = dq[N // 2]
print(f"deque[mid]: {(time.perf_counter() - start) * 1e6:.0f} µs")
```

리스트는 인덱스 접근이 O(1)이지만 deque는 O(n)에 가깝습니다. 양 끝과 임의 인덱스 중 무엇이 더 자주 일어나는지에 따라 선택이 달라집니다.

## 이 코드에서 주목할 점

- 노드는 메모리상 흩어져 있어 캐시 친화성이 배열보다 떨어집니다
- 포인터를 위해 노드당 추가 메모리(포인터 1~2개)가 필요합니다
- 양 끝 연산은 O(1)이지만 임의 위치 접근은 O(n)입니다
- 센티넬 노드를 쓰면 분기와 버그가 줄어듭니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 배열을 흉내 내며 인덱스로 접근 | 매번 O(n) 순회 | 인덱스 접근이 잦으면 배열 선택 |
| head 포인터를 잃어버림 | 리스트 전체 분실 | head 갱신을 명시적으로 관리 |
| 삭제 후 prev 갱신 누락 | 이중 연결 리스트 깨짐 | 양방향 포인터를 세트로 갱신 |
| 빈 리스트 분기 누락 | NoneType 에러 | 센티넬로 빈 케이스 제거 |
| 메모리 누수 가정 | 파이썬에서는 GC가 처리 | C/C++라면 명시적 free 필요 |

## 실무에서는 이렇게 쓰입니다

- 리눅스 커널의 `list_head`는 이중 연결 리스트로 거의 모든 자료를 묶습니다
- LRU 캐시는 해시 테이블 + 이중 연결 리스트 조합으로 O(1) 갱신을 제공합니다
- 메모리 할당기는 자유 블록(free list)을 연결 리스트로 관리합니다
- 음악 플레이어의 다음/이전 곡 이동은 이중 연결 리스트와 잘 맞습니다
- 텍스트 에디터의 줄 단위 자료구조는 종종 연결 리스트의 변형(rope)을 씁니다

## 체크리스트

- [ ] 단일/이중 연결 리스트의 구조 차이를 설명할 수 있는가
- [ ] 양 끝 삽입이 O(1)이고 임의 인덱스 접근이 O(n)인 이유를 이해했는가
- [ ] 센티넬 노드의 장점을 알고 있는가
- [ ] 배열보다 연결 리스트가 적합한 워크로드를 구분할 수 있는가
- [ ] 파이썬에서 deque가 어떤 자료구조에 가까운지 인지하고 있는가

## 정리 및 다음 단계

연결 리스트는 노드를 포인터로 이어 붙여 만든 자료구조이며, 양 끝 또는 알려진 위치에서의 삽입·삭제가 O(1)이라는 강점이 있습니다. 대신 임의 인덱스 접근은 O(n)이고 메모리 캐시 친화성도 배열보다 낮습니다. 단일과 이중 연결 리스트는 추가 포인터 비용과 양방향 순회 능력을 맞바꾸는 트레이드오프 관계입니다.

다음 글에서는 연결 리스트와 배열을 기반으로 만드는 두 가지 ADT, 스택과 큐를 살펴봅니다. LIFO와 FIFO라는 단순한 규칙이 어떻게 강력한 추상화가 되는지 알아봅니다.

<!-- toc:begin -->
- [자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [배열과 동적 배열](./02-arrays-and-dynamic-arrays.md)
- **연결 리스트 (현재 글)**
- 스택과 큐 (예정)
- 해시 테이블 (예정)
- 트리 (예정)
- 이진 탐색 트리 (예정)
- 힙 (예정)
- 그래프 (예정)
- 자료구조 선택 기준 (예정)
<!-- toc:end -->

## 참고 자료

- [Open Data Structures — Chapter 3 Linked Lists](https://opendatastructures.org/ods-python/3_Linked_Lists.html)
- [Linux Kernel `list.h`](https://github.com/torvalds/linux/blob/master/include/linux/list.h)
- [Wikipedia — Linked List](https://en.wikipedia.org/wiki/Linked_list)
- [Python collections.deque docs](https://docs.python.org/3/library/collections.html#collections.deque)

Tags: Computer Science, 자료구조, 연결 리스트, 포인터, 노드, 메모리
