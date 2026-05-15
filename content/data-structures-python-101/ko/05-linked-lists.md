---
series: data-structures-python-101
episode: 5
title: 연결 리스트
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
  - Linked List
  - 연결 리스트
  - 노드
seo_description: 연결 리스트의 구조와 배열 대비 장단점을 Python 코드로 설명합니다.
last_reviewed: '2026-05-12'
---

# 연결 리스트

이 글은 Data Structures with Python 101 시리즈의 다섯 번째 글입니다.

## 이 글에서 다룰 문제

- Python에 이미 list가 있는데 왜 연결 리스트를 따로 배워야 할까요?
- 단일 연결 리스트와 이중 연결 리스트는 어떻게 다를까요?
- 연결 리스트는 왜 삽입·삭제에는 강하고, 인덱스 접근에는 약할까요?
- 뒤집기와 순환 감지 같은 대표 문제는 어떤 사고방식으로 풀어야 할까요?

> 멘탈 모델: 연결 리스트는 값을 “연속된 칸”에 저장하지 않고, 노드가 다음 노드를 가리키는 방식으로 이어 붙입니다. 그래서 위치 기반 접근보다 포인터 변경이 핵심 연산이 됩니다.

## 왜 이 글이 중요한가

연결 리스트는 자료구조에서 가장 기본적인 빌딩 블록 중 하나입니다. 트리, 그래프, 해시 테이블의 체이닝, LRU 캐시 같은 구조를 제대로 이해하려면 결국 노드와 참조를 다루는 감각이 필요합니다. 연결 리스트는 그 감각을 가장 직접적으로 훈련시키는 구조입니다.

> 연결 리스트는 각 노드가 데이터와 다음 노드에 대한 참조를 저장하는 선형 자료구조입니다.

코딩 면접에서 연결 리스트 문제가 자주 나오는 이유도 같습니다. 뒤집기, 순환 감지, 병합, 중간 노드 찾기처럼 포인터 조작과 경계 조건 처리를 한꺼번에 볼 수 있기 때문입니다. 즉, 연결 리스트를 잘 다루는 사람은 단순 문법보다 데이터 흐름을 더 잘 이해하는 경우가 많습니다.

## 핵심 개념 한눈에 보기

> 연결 리스트 = 노드들이 참조로 연결된 선형 구조

```text
[Singly Linked List]
  head -> [A|->] -> [B|->] -> [C|->] -> None

[Doubly Linked List]
  None <- [<-|A|->] <-> [<-|B|->] <-> [<-|C|->] -> None
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 노드(Node) | 데이터와 다음 노드 참조를 담는 기본 단위입니다 |
| head | 연결 리스트의 첫 번째 노드를 가리키는 참조입니다 |
| tail | 마지막 노드를 가리키는 참조입니다 |
| 단일 연결 리스트 | 각 노드가 다음 노드만 가리키는 구조입니다 |
| 이중 연결 리스트 | 각 노드가 이전 노드와 다음 노드를 모두 가리키는 구조입니다 |

## Before / After

배열 기반 구조와 연결 리스트 기반 구조가 중간 삭제를 어떻게 다르게 처리하는지 보겠습니다.

```python
# before: delete from middle of list — O(n), shifts all subsequent elements
data = [10, 20, 30, 40, 50]
data.pop(2)  # removes 30 — 40 and 50 shift left
```

```python
# after: delete from middle of linked list — O(1), change pointers only
# node_b.next = node_b.next.next
# skip node 30 and connect 20 -> 40
```

여기서 연결 리스트의 장단점이 동시에 드러납니다. 삭제 자체는 포인터 변경만으로 끝나지만, 삭제할 노드를 찾기까지는 보통 순차 탐색이 필요합니다. 그래서 “무엇을 빨리 하려는 구조인가”를 분리해서 봐야 합니다.

## 단계별 실습

### Step 1: Define the Node class

```python
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

    def __repr__(self):
        return f"Node({self.data})"
```

### Step 2: Implement a singly linked list

```python
class SinglyLinkedList:
    def __init__(self):
        self.head = None
        self._size = 0

    def append(self, data):
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self._size += 1

    def prepend(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        self._size += 1

    def delete(self, data):
        if self.head is None:
            return
        if self.head.data == data:
            self.head = self.head.next
            self._size -= 1
            return
        current = self.head
        while current.next:
            if current.next.data == data:
                current.next = current.next.next
                self._size -= 1
                return
            current = current.next

    def __len__(self):
        return self._size

    def __str__(self):
        parts = []
        current = self.head
        while current:
            parts.append(str(current.data))
            current = current.next
        return " -> ".join(parts)

sll = SinglyLinkedList()
sll.append("A")
sll.append("B")
sll.append("C")
print(sll)          # A -> B -> C
sll.prepend("Z")
print(sll)          # Z -> A -> B -> C
sll.delete("B")
print(sll)          # Z -> A -> C
print(len(sll))     # 3
```

### Step 3: Reverse a linked list

```python
def reverse_linked_list(head: Node) -> Node:
    prev = None
    current = head
    while current:
        next_node = current.next
        current.next = prev
        prev = current
        current = next_node
    return prev

sll = SinglyLinkedList()
for item in ["A", "B", "C", "D"]:
    sll.append(item)
print(f"original: {sll}")  # A -> B -> C -> D
sll.head = reverse_linked_list(sll.head)
print(f"reversed: {sll}")  # D -> C -> B -> A
```

### Step 4: Implement a doubly linked list

```python
class DNode:
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None

class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self._size = 0

    def append(self, data):
        new_node = DNode(data)
        if self.tail is None:
            self.head = self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self._size += 1

    def prepend(self, data):
        new_node = DNode(data)
        if self.head is None:
            self.head = self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        self._size += 1

    def __str__(self):
        parts = []
        current = self.head
        while current:
            parts.append(str(current.data))
            current = current.next
        return " <-> ".join(parts)

dll = DoublyLinkedList()
dll.append("A")
dll.append("B")
dll.append("C")
dll.prepend("Z")
print(dll)  # Z <-> A <-> B <-> C
```

### Step 5: Cycle detection (Floyd's algorithm)

```python
def has_cycle(head: Node) -> bool:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False

# no cycle
a, b, c = Node("A"), Node("B"), Node("C")
a.next, b.next = b, c
print(has_cycle(a))  # False

# cycle present
c.next = a  # C -> A creates a cycle
print(has_cycle(a))  # True
```

## 이 코드에서 먼저 봐야 할 점

- 연결 리스트의 `prepend`는 O(1)이지만 `list.insert(0, x)`는 O(n)입니다.
- 인덱스 접근은 O(n)이므로 랜덤 접근이 많으면 연결 리스트는 불리합니다.
- 뒤집기와 순환 감지는 연결 리스트 사고방식을 가장 잘 드러내는 대표 문제입니다.
- Python의 `collections.deque`를 이해할 때도 이중 연결 구조에 대한 감각이 도움이 됩니다.

연결 리스트는 “무조건 빠른 구조”가 아닙니다. 배열보다 느린 점도 많습니다. 대신 참조를 바꿔 구조를 재배열하는 문제에서는 매우 강력합니다. 결국 핵심은 메모리 배치가 아니라 연결 관계를 조작하는 능력입니다.

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| `next` 업데이트 순서 실수 | 노드가 유실되어 리스트가 끊어질 수 있습니다 | 포인터를 바꾸기 전 다음 노드를 임시 변수에 저장합니다 |
| `head is None` 케이스 누락 | `NoneType` 관련 오류가 발생합니다 | 빈 리스트 조건을 항상 먼저 처리합니다 |
| 삭제 후 `_size` 미갱신 | `len()` 결과가 실제와 달라집니다 | 성공적으로 삭제했을 때 반드시 감소시킵니다 |
| 이중 연결 리스트에서 `prev` 누락 | 역방향 순회와 삭제가 꼬입니다 | 삽입·삭제 때 `prev`와 `next`를 모두 맞춥니다 |
| 순환 리스트를 일반 순회로 처리 | 무한 루프에 빠집니다 | Floyd 알고리즘 같은 감지 로직을 사용합니다 |

## 실무에서 이렇게 쓰입니다

- LRU 캐시는 이중 연결 리스트와 dict를 조합해 구현합니다.
- 텍스트 에디터의 undo 이력은 연결 구조로 관리하기 좋습니다.
- 메모리 할당자는 빈 블록 목록을 연결 리스트로 관리하기도 합니다.
- 해시 테이블 체이닝은 충돌 버킷을 연결 리스트로 연결할 수 있습니다.
- 브라우저 히스토리는 이전/다음 이동 때문에 이중 연결 구조와 잘 맞습니다.

## 실무에서는 이렇게 생각합니다

Python에서는 연결 리스트를 직접 구현할 일이 많지 않습니다. list와 deque가 대부분의 요구를 해결하기 때문입니다. 그래도 연결 리스트를 이해하는 이유는 구현 자체보다, 참조 기반 구조가 어떻게 움직이는지 감각을 익히기 위해서입니다.

면접 관점에서도 연결 리스트는 필수입니다. 포인터 조작, 경계 조건 처리, 재귀와 반복 전환 능력을 모두 보여 줄 수 있기 때문입니다. 즉, 연결 리스트 문제를 잘 푼다는 것은 다른 자료구조 문제에도 강하다는 신호가 됩니다.

## 체크리스트

- [ ] 단일 연결 리스트의 append, prepend, delete를 구현할 수 있다
- [ ] 연결 리스트를 뒤집는 알고리즘을 작성할 수 있다
- [ ] 이중 연결 리스트의 장점을 설명할 수 있다
- [ ] Floyd의 순환 감지 알고리즘을 설명할 수 있다
- [ ] 배열과 연결 리스트의 성능 차이를 비교할 수 있다

## 연습 문제

1. 단일 연결 리스트에서 한 번의 순회로 가운데 노드를 찾는 함수를 작성해 보세요. 힌트: slow/fast 포인터를 사용합니다.
2. 정렬된 연결 리스트 두 개를 받아 하나의 정렬된 연결 리스트로 합치는 함수를 작성해 보세요.
3. 연결 리스트의 뒤에서 N번째 노드를 삭제하는 함수를 작성해 보세요.

## 정리 및 다음 글 안내

연결 리스트는 노드를 참조로 연결해 삽입과 삭제를 유연하게 처리하는 구조입니다. 배열처럼 연속 메모리를 요구하지 않지만, 인덱스 기반 임의 접근은 느립니다. 즉, 연결 리스트는 “위치로 찾는 구조”보다 “연결을 바꾸는 구조”에 가깝습니다. 다음 글에서는 계층 구조를 표현하는 트리와 이진 트리를 살펴보겠습니다.

<!-- toc:begin -->
- [자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [배열과 리스트](./02-arrays-and-lists.md)
- [스택과 큐](./03-stacks-and-queues.md)
- [해시 테이블과 dict](./04-hash-tables-and-dict.md)
- **연결 리스트 (현재 글)**
- 트리와 이진 트리 (예정)
- 힙과 우선순위 큐 (예정)
- 그래프 표현 (예정)
- set과 집합 연산 (예정)
- 자료구조 선택 기준 (예정)
<!-- toc:end -->

## 참고 자료

- [Real Python — Linked Lists in Python](https://realpython.com/linked-lists-python/)
- [GeeksforGeeks — Linked List Data Structure](https://www.geeksforgeeks.org/data-structures/linked-list/)
- [Visualgo — Linked List Visualization](https://visualgo.net/en/list)
- [LeetCode — Linked List Problems](https://leetcode.com/tag/linked-list/)

Tags: Python, 자료구조, Linked List, 연결 리스트, 노드
