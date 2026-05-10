---
series: data-structures-python-101
episode: 5
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
  - Python
  - 자료구조
  - Linked List
  - 연결 리스트
  - 노드
seo_description: Python으로 단일·이중 연결 리스트를 구현하고 배열과 비교합니다.
last_reviewed: '2026-05-04'
---

# 연결 리스트

> Data Structures with Python 101 시리즈 (5/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: Python에 list가 있는데 연결 리스트를 왜 배워야 할까요?

> Python list는 배열 기반이라 중간 삽입·삭제가 O(n)입니다. 연결 리스트는 노드를 포인터로 연결하여 삽입·삭제를 O(1)에 수행합니다. 이 글에서는 단일 연결 리스트와 이중 연결 리스트를 Python으로 구현하고, 배열과의 차이를 비교합니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 연결 리스트의 구조와 동작 원리
- 단일 연결 리스트(singly linked list) 구현
- 이중 연결 리스트(doubly linked list) 구현
- 배열과 연결 리스트의 성능 비교

## 왜 중요한가

연결 리스트는 자료구조의 기본 중 기본입니다. 트리, 그래프, 해시 테이블의 체이닝 등 고급 자료구조의 빌딩 블록이 됩니다. 연결 리스트를 직접 구현하면 포인터(참조) 개념을 확실히 익힐 수 있습니다.

> 연결 리스트는 각 노드가 데이터와 다음 노드에 대한 참조를 가지는 자료구조입니다.

코딩 면접에서 연결 리스트 문제는 가장 자주 출제되는 유형 중 하나입니다. 뒤집기, 순환 감지, 병합 등 다양한 변형 문제가 있습니다.

## 핵심 개념 잡기

> 연결 리스트 = 노드들이 포인터로 연결된 선형 자료구조

```
[단일 연결 리스트]
  head → [A|→] → [B|→] → [C|→] → None

[이중 연결 리스트]
  None ← [←|A|→] ⇄ [←|B|→] ⇄ [←|C|→] → None
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 노드(Node) | 데이터와 다음 노드에 대한 참조를 가지는 단위입니다 |
| head | 연결 리스트의 첫 번째 노드를 가리킵니다 |
| tail | 연결 리스트의 마지막 노드를 가리킵니다 |
| 단일 연결 리스트 | 각 노드가 다음 노드만 참조하는 구조입니다 |
| 이중 연결 리스트 | 각 노드가 이전과 다음 노드를 모두 참조하는 구조입니다 |

## Before / After

배열에서 중간 삭제와 연결 리스트에서 중간 삭제를 비교합니다.

```python
# before: list 중간 삭제 — O(n), 뒤의 원소를 모두 이동
data = [10, 20, 30, 40, 50]
data.pop(2)  # 30 삭제 — 40, 50이 한 칸씩 앞으로 이동
```

```python
# after: 연결 리스트 중간 삭제 — O(1), 포인터만 변경
# node_b.next = node_b.next.next
# 30 노드를 건너뛰고 20 → 40 연결
```

## 단계별 실습

### Step 1: Node 클래스 정의

```python
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

    def __repr__(self):
        return f"Node({self.data})"
```

### Step 2: 단일 연결 리스트 구현

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
        return " → ".join(parts)

sll = SinglyLinkedList()
sll.append("A")
sll.append("B")
sll.append("C")
print(sll)          # A → B → C
sll.prepend("Z")
print(sll)          # Z → A → B → C
sll.delete("B")
print(sll)          # Z → A → C
print(len(sll))     # 3
```

### Step 3: 연결 리스트 뒤집기

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
print(f"원본: {sll}")  # A → B → C → D
sll.head = reverse_linked_list(sll.head)
print(f"뒤집기: {sll}")  # D → C → B → A
```

### Step 4: 이중 연결 리스트 구현

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
        return " ⇄ ".join(parts)

dll = DoublyLinkedList()
dll.append("A")
dll.append("B")
dll.append("C")
dll.prepend("Z")
print(dll)  # Z ⇄ A ⇄ B ⇄ C
```

### Step 5: 순환 감지 (Floyd's algorithm)

```python
def has_cycle(head: Node) -> bool:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False

# 순환 없는 리스트
a, b, c = Node("A"), Node("B"), Node("C")
a.next, b.next = b, c
print(has_cycle(a))  # False

# 순환 있는 리스트
c.next = a  # C → A 순환
print(has_cycle(a))  # True
```

## 이 코드에서 주목할 점

- 연결 리스트의 prepend는 O(1)이지만 list의 insert(0, x)는 O(n)입니다
- 연결 리스트는 인덱스 접근이 O(n)이라 랜덤 접근에는 부적합합니다
- 뒤집기, 순환 감지 등은 코딩 면접 단골 문제입니다
- Python의 collections.deque는 내부적으로 이중 연결 리스트입니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| next 포인터 업데이트 순서 오류 | 노드가 유실되어 리스트가 끊깁니다 | 다음 노드를 임시 변수에 저장한 뒤 포인터를 수정합니다 |
| head가 None인 경우 미처리 | NoneType 에러가 발생합니다 | head가 None인 경우를 먼저 처리합니다 |
| 삭제 후 size 미갱신 | len()이 잘못된 값을 반환합니다 | 삭제 성공 시 _size -= 1을 빠뜨리지 않습니다 |
| 이중 연결 리스트에서 prev 미설정 | 역방향 순회가 불가능합니다 | 삽입·삭제 시 prev와 next를 모두 업데이트합니다 |
| 순환 참조로 무한 루프 발생 | while current가 끝나지 않습니다 | Floyd 알고리즘으로 순환을 감지합니다 |

## 실무에서 이렇게 쓰입니다

- LRU 캐시를 이중 연결 리스트 + dict로 구현합니다
- 텍스트 에디터의 실행 취소를 연결 리스트로 관리합니다
- 메모리 할당자가 빈 블록을 연결 리스트로 관리합니다
- 해시 테이블의 체이닝 방식이 연결 리스트를 사용합니다
- 브라우저 히스토리를 이중 연결 리스트로 구현합니다

## 현업 개발자는 이렇게 생각합니다

Python에서는 연결 리스트를 직접 구현할 일이 거의 없습니다. list와 deque가 대부분의 상황을 커버하기 때문입니다. 하지만 연결 리스트의 개념을 이해하면 deque, LRU 캐시, 그래프 등의 동작 원리를 파악할 수 있습니다.

면접 준비에서 연결 리스트는 필수입니다. 포인터 조작, 경계 조건 처리, 재귀적 사고를 연습하기에 최적의 자료구조입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **실전 빈도** — Python에서 직접 만들 일은 드물다는 현실을 인정합니다.
- **개념 가치** — 포인터·메모리 모델 학습 자료로 가치가 큽니다.
- **deque 대체** — 양방향 작업은 deque가 거의 항상 우월합니다.
- **불변식** — head/tail/length 불변식을 명시하면 버그가 줄어듭니다.
- **회수 패턴** — LRU 캐시·체인 자료구조에서 응용을 봅니다.

## 체크리스트

- [ ] 단일 연결 리스트의 append, prepend, delete를 구현할 수 있다
- [ ] 연결 리스트를 뒤집는 알고리즘을 작성할 수 있다
- [ ] 이중 연결 리스트의 장점을 설명할 수 있다
- [ ] Floyd의 순환 감지 알고리즘을 설명할 수 있다
- [ ] 배열과 연결 리스트의 성능 차이를 비교할 수 있다

## 연습 문제

1. 단일 연결 리스트에서 중간 노드를 한 번의 순회로 찾는 함수를 작성하세요. (힌트: slow/fast 포인터)
2. 두 정렬된 연결 리스트를 하나의 정렬된 연결 리스트로 병합하는 함수를 작성하세요.
3. 연결 리스트에서 끝에서 N번째 노드를 삭제하는 함수를 작성하세요.

## 정리 및 다음 글 안내

연결 리스트는 노드를 포인터로 연결하여 삽입·삭제에 O(1)을 달성합니다. 배열과 달리 연속된 메모리가 필요 없지만, 인덱스 접근이 O(n)입니다. 다음 글에서는 계층 구조를 표현하는 트리와 이진 트리를 다룹니다.

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
