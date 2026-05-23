---
series: data-structures-python-101
episode: 6
title: "Data Structures with Python 101 (6/10): 트리와 이진 트리"
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
  - Tree
  - Binary Tree
  - BST
seo_description: 트리와 이진 탐색 트리(BST)의 계층 구조, 순회 방법, 탐색 원리를 Python 예제로 설명하고 재귀적 사고방식을 익힙니다.
last_reviewed: '2026-05-15'
---

# Data Structures with Python 101 (6/10): 트리와 이진 트리

이 글은 Data Structures with Python 101 시리즈의 여섯 번째 글입니다.


![Data Structures with Python 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-python-101/06/06-01-tree-shape-at-a-glance.ko.png)
*Data Structures with Python 101 6장 흐름 개요*

## 먼저 던지는 질문

- 파일 시스템, DOM, 조직도는 왜 트리 구조로 모델링될까요?
- 트리의 루트, 리프, 깊이, 높이는 각각 무엇을 뜻할까요?
- 이진 트리 순회는 왜 재귀와 잘 맞을까요?

## 왜 이 글이 중요한가

트리는 컴퓨터 과학에서 가장 널리 쓰이는 구조 중 하나입니다. 파일 시스템, HTML DOM, 데이터베이스 인덱스, AST까지 계층 관계를 표현해야 하는 곳에는 거의 항상 트리가 등장합니다. 그래서 트리를 이해하는 것은 특정 알고리즘 하나를 배우는 문제가 아니라, 복잡한 시스템을 구조적으로 읽는 연습에 가깝습니다.

> 트리를 이해하면 재귀 사고가 자연스러워집니다. 대부분의 트리 알고리즘은 재귀로 가장 잘 표현됩니다.

특히 이진 탐색 트리(BST)는 트리 위에 정렬 규칙을 얹은 구조입니다. 이 규칙 덕분에 선형 검색 O(n) 대신 O(log n)에 가까운 탐색이 가능해집니다. 물론 균형이 무너질 수 있다는 한계도 함께 배워야 합니다.

## 핵심 개념 한눈에 보기

> 트리 = 루트에서 시작해 자식 노드로 분기하는 계층 구조

```text
        [root]
       /      \
    [child]  [child]
    /   \       \
 [leaf] [leaf]  [leaf]

Binary Search Tree (BST):
        [8]
       /   \
     [3]   [10]
    /   \      \
  [1]   [6]   [14]
```

## 트리 구조를 그림으로 보면

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 루트(root) | 트리의 가장 위에 있는 시작 노드입니다 |
| 리프(leaf) | 자식이 없는 말단 노드입니다 |
| 깊이(depth) | 루트에서 특정 노드까지 내려가는 거리입니다 |
| 높이(height) | 특정 노드에서 가장 먼 리프까지의 거리입니다 |
| 이진 탐색 트리(BST) | 왼쪽 자식 < 부모 < 오른쪽 자식 규칙을 만족하는 트리입니다 |

## 적용 전후 비교
정렬된 데이터를 list로 순차 탐색하는 경우와 BST로 탐색하는 경우를 비교해 보겠습니다.

```python
# before: 정렬된 list에서 선형 탐색 — O(n)
data = [1, 3, 6, 8, 10, 14]
for item in data:
    if item == 10:
        print("found")
        break
```

```python
# after: BST 탐색 — O(log n)
# BST: 8 → 10 → 발견 (2단계)
def search_bst(node, target):
    if node is None:
        return False
    if target == node.data:
        return True
    elif target < node.data:
        return search_bst(node.left, target)
    else:
        return search_bst(node.right, target)
```

BST의 장점은 매 단계에서 볼 필요 없는 절반을 버릴 수 있다는 사실입니다. 그래서 정렬 규칙은 단순한 예쁜 성질이 아니라, 탐색 비용을 줄이는 핵심 계약입니다.

## 단계별 실습

### 단계 1: 이진 트리 노드 정의하기

```python
class TreeNode:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

    def __repr__(self):
        return f"TreeNode({self.data})"
```

### 단계 2: 트리 순회 구현
```python
def inorder(node):
    """Inorder traversal: left → root → right"""
    if node is None:
        return []
    return inorder(node.left) + [node.data] + inorder(node.right)

def preorder(node):
    """Preorder traversal: root → left → right"""
    if node is None:
        return []
    return [node.data] + preorder(node.left) + preorder(node.right)

def postorder(node):
    """Postorder traversal: left → right → root"""
    if node is None:
        return []
    return postorder(node.left) + postorder(node.right) + [node.data]

# Build tree:        1
#                  /   \
#                 2     3
#                / \
#               4   5
root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)
root.left.left = TreeNode(4)
root.left.right = TreeNode(5)

print(f"inorder:   {inorder(root)}")    # [4, 2, 5, 1, 3]
print(f"preorder:  {preorder(root)}")   # [1, 2, 4, 5, 3]
print(f"postorder: {postorder(root)}")  # [4, 5, 2, 3, 1]
```

### 단계 3: 레벨 순서 순회 (BFS)
```python
from collections import deque

def level_order(root):
    """Level-order traversal: nodes at the same depth, left to right"""
    if root is None:
        return []
    result = []
    queue = deque([root])
    while queue:
        node = queue.popleft()
        result.append(node.data)
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)
    return result

print(f"level-order: {level_order(root)}")  # [1, 2, 3, 4, 5]
```

### 단계 4: 이진 탐색 트리 구현하기

```python
class BST:
    def __init__(self):
        self.root = None

    def insert(self, data):
        self.root = self._insert(self.root, data)

    def _insert(self, node, data):
        if node is None:
            return TreeNode(data)
        if data < node.data:
            node.left = self._insert(node.left, data)
        elif data > node.data:
            node.right = self._insert(node.right, data)
        return node

    def search(self, data):
        return self._search(self.root, data)

    def _search(self, node, data):
        if node is None:
            return False
        if data == node.data:
            return True
        elif data < node.data:
            return self._search(node.left, data)
        else:
            return self._search(node.right, data)

    def inorder(self):
        return inorder(self.root)

bst = BST()
for val in [8, 3, 10, 1, 6, 14]:
    bst.insert(val)

print(bst.inorder())       # [1, 3, 6, 8, 10, 14] — sorted result
print(bst.search(6))       # True
print(bst.search(7))       # False
```

### 단계 5: 트리 높이와 노드 수 계산하기

```python
def tree_height(node):
    if node is None:
        return -1
    return 1 + max(tree_height(node.left), tree_height(node.right))

def count_nodes(node):
    if node is None:
        return 0
    return 1 + count_nodes(node.left) + count_nodes(node.right)

print(f"height: {tree_height(bst.root)}")      # 2
print(f"node count: {count_nodes(bst.root)}")   # 6
```

## 이 코드에서 먼저 봐야 할 점

- 트리 알고리즘은 `node is None`이라는 base case를 중심으로 재귀가 전개됩니다.
- BST의 inorder 순회 결과가 정렬되는 이유는 왼쪽 < 부모 < 오른쪽 규칙 때문입니다.
- level-order 순회는 큐를 사용하며, 트리에서 BFS 패턴을 가장 명확하게 보여 줍니다.
- BST 탐색은 매 단계에서 절반을 버릴 수 있을 때 O(log n)에 가까워집니다.

트리는 구현 세부사항보다 사고방식이 중요합니다. “현재 노드를 처리하고, 왼쪽과 오른쪽 서브트리에 같은 규칙을 적용한다”라는 반복 패턴을 익히면 순회, 높이 계산, 탐색, 검증 문제들이 하나의 패밀리처럼 보이기 시작합니다.

실무에서는 BST의 평균 O(log n)만 기억하면 위험합니다. 입력이 이미 정렬되어 있거나 편향된 순서로 들어오면 트리는 한쪽으로 길게 늘어져 O(n)으로 퇴화합니다. 그래서 운영 시스템은 단순 BST보다 AVL, Red-Black Tree, B-Tree 계열처럼 균형을 유지하는 구조를 택합니다.

Python 코드에서는 재귀 깊이도 함께 봐야 합니다. 트리가 깊어질수록 `RecursionError` 가능성이 생기고, 순회 중 노드 객체 수가 많으면 메모리 사용량도 커집니다. 즉, 트리 선택은 “탐색이 빠르다”는 장점만이 아니라 균형 유지 비용, 재귀 한계, 저장 형태까지 묶어서 판단해야 합니다.

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 재귀 base case 누락 | 무한 재귀와 `RecursionError`로 이어집니다 | 항상 `node is None`을 먼저 처리합니다 |
| BST 중복 정책 미정의 | 예상과 다른 트리 구조가 생깁니다 | 중복을 무시할지, 개수를 셀지 정책을 정합니다 |
| 편향 트리를 BST로 착각 | 한쪽으로만 치우치면 O(n)으로 퇴화합니다 | 균형 트리 필요 여부를 구분합니다 |
| 순회 순서 혼동 | 알고리즘 결과가 달라집니다 | preorder(NLR), inorder(LNR), postorder(LRN)를 분명히 구분합니다 |
| 삭제 연산을 단순하게 봄 | 자식이 둘인 노드 처리가 특히 까다롭습니다 | 후계자(in-order successor) 패턴을 따로 연습합니다 |

## 실무에서 이렇게 쓰입니다

- 데이터베이스 인덱스는 B-Tree/B+Tree 계열을 사용합니다.
- 파일 시스템 디렉터리 구조는 전형적인 트리입니다.
- HTML/XML DOM은 문서 구조를 트리로 표현합니다.
- 파서와 컴파일러는 AST를 만들어 식과 문장을 처리합니다.
- 자동 완성은 Trie 같은 특화 트리 구조를 사용합니다.

## 실무에서는 이렇게 생각합니다

실무에서 BST를 처음부터 직접 구현할 일은 많지 않습니다. 대신 `sorted()`, `bisect`, 데이터베이스 인덱스, 라이브러리 내부 구조가 이미 그런 역할을 대신합니다. 그래도 트리를 이해해야 이런 도구가 어떤 가정 위에서 빠르게 동작하는지 설명할 수 있습니다.

또 하나 중요한 점은 트리가 재귀 사고를 훈련하는 최고의 재료라는 사실입니다. 트리 문제를 반복해서 풀다 보면, 복잡한 문제를 “현재 노드와 하위 문제”로 분해하는 감각이 자연스럽게 생깁니다.

## 체크리스트

- [ ] 트리의 루트, 리프, 깊이, 높이를 설명할 수 있다
- [ ] preorder, inorder, postorder, level-order 순회를 구현할 수 있다
- [ ] BST에서 삽입과 탐색을 구현할 수 있다
- [ ] BST의 inorder 순회가 왜 정렬 결과를 반환하는지 설명할 수 있다
- [ ] 트리 높이와 노드 수를 재귀로 계산할 수 있다

## 연습 문제

1. 주어진 이진 트리가 BST인지 검증하는 함수를 작성해 보세요. 힌트: inorder 결과가 정렬되어야 합니다.
2. 두 이진 트리가 구조적으로 같은지 확인하는 함수를 작성해 보세요.
3. BST에서 값을 삭제하는 함수를 구현해 보세요. 자식 수가 0, 1, 2인 경우를 모두 처리해야 합니다.

## 정리 및 다음 글 안내

트리는 계층 관계를 표현하는 가장 중요한 자료구조 중 하나이고, BST는 그 위에 정렬 규칙을 얹어 탐색 효율을 높인 구조입니다. 순회와 높이 계산처럼 많은 트리 연산은 재귀로 자연스럽게 풀립니다. 다음 글에서는 트리의 특수한 형태이면서 우선순위 처리에 강한 힙과 우선순위 큐를 봅니다.


## 타입 힌트 기반 이진 탐색 트리 구현

이진 트리의 가장 실용적인 형태인 이진 탐색 트리(BST)를 타입 힌트와 함께 구현합니다. BST는 왼쪽 자식 < 부모 < 오른쪽 자식이라는 불변식을 유지합니다.

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Iterator, Optional, TypeVar

T = TypeVar("T")


@dataclass
class TreeNode(Generic[T]):
    """이진 트리의 노드입니다."""
    value: T
    left: Optional[TreeNode[T]] = None
    right: Optional[TreeNode[T]] = None


class BST(Generic[T]):
    """이진 탐색 트리입니다. 중복 키는 무시합니다."""

    def __init__(self) -> None:
        self._root: Optional[TreeNode[T]] = None
        self._size: int = 0

    def insert(self, value: T) -> None:
        self._root = self._insert(self._root, value)

    def _insert(self, node: Optional[TreeNode[T]], value: T) -> TreeNode[T]:
        if node is None:
            self._size += 1
            return TreeNode(value=value)
        if value < node.value:  # type: ignore[operator]
            node.left = self._insert(node.left, value)
        elif value > node.value:  # type: ignore[operator]
            node.right = self._insert(node.right, value)
        return node

    def search(self, value: T) -> bool:
        return self._search(self._root, value)

    def _search(self, node: Optional[TreeNode[T]], value: T) -> bool:
        if node is None:
            return False
        if value == node.value:
            return True
        if value < node.value:  # type: ignore[operator]
            return self._search(node.left, value)
        return self._search(node.right, value)

    def inorder(self) -> Iterator[T]:
        """중위 순회: 정렬된 순서로 원소를 반환합니다."""
        yield from self._inorder(self._root)

    def _inorder(self, node: Optional[TreeNode[T]]) -> Iterator[T]:
        if node is not None:
            yield from self._inorder(node.left)
            yield node.value
            yield from self._inorder(node.right)

    def preorder(self) -> Iterator[T]:
        """전위 순회: 부모 → 왼쪽 → 오른쪽"""
        yield from self._preorder(self._root)

    def _preorder(self, node: Optional[TreeNode[T]]) -> Iterator[T]:
        if node is not None:
            yield node.value
            yield from self._preorder(node.left)
            yield from self._preorder(node.right)

    def height(self) -> int:
        return self._height(self._root)

    def _height(self, node: Optional[TreeNode[T]]) -> int:
        if node is None:
            return -1
        return 1 + max(self._height(node.left), self._height(node.right))

    def min_value(self) -> T:
        if self._root is None:
            raise ValueError("empty tree")
        node = self._root
        while node.left is not None:
            node = node.left
        return node.value

    def __len__(self) -> int:
        return self._size

    def __contains__(self, value: object) -> bool:
        return self.search(value)  # type: ignore[arg-type]

    def __repr__(self) -> str:
        return f"BST(size={self._size}, height={self.height()})"
```

### 설계 결정 네 가지

1. **재귀 삽입/검색**: 트리의 구조가 재귀적(노드 → 서브트리 → 서브트리)이므로, 재귀 구현이 자연스럽습니다. 반복문으로도 가능하지만 코드가 길어집니다.
2. **중위 순회가 정렬을 보장**: BST의 불변식 덕분에 중위 순회(left → root → right)는 항상 오름차순을 반환합니다. 이 성질이 BST의 핵심 가치입니다.
3. **height 계산**: 빈 트리는 높이 -1, 루트만 있으면 0입니다. 이 정의가 재귀 공식 `1 + max(left, right)`과 맞아떨어집니다.
4. **중복 무시**: 같은 값을 다시 넣으면 아무 일도 하지 않습니다. 중복을 허용하려면 카운터를 노드에 추가하는 변형이 필요합니다.

## 메모리 프로파일링: BST의 노드 오버헤드

```python
import sys
from typing import Any


def deep_getsizeof(obj: Any, seen: set[int] | None = None) -> int:
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)
    size = sys.getsizeof(obj)
    if hasattr(obj, "__dict__"):
        size += deep_getsizeof(obj.__dict__, seen)
        for v in obj.__dict__.values():
            size += deep_getsizeof(v, seen)
    if isinstance(obj, (list, tuple, set, frozenset)):
        size += sum(deep_getsizeof(item, seen) for item in obj)
    elif isinstance(obj, dict):
        size += sum(deep_getsizeof(k, seen) + deep_getsizeof(v, seen) for k, v in obj.items())
    return size


import random

n = 1_000
values = random.sample(range(n * 10), n)

bst = BST[int]()
for v in values:
    bst.insert(v)

sorted_list = sorted(values)

bst_size = deep_getsizeof(bst)
list_size = deep_getsizeof(sorted_list)

print(f"BST ({n} nodes):    {bst_size:>10} bytes")
print(f"sorted list ({n}): {list_size:>10} bytes")
print(f"BST overhead: {bst_size / list_size:.1f}x")
```

BST는 노드 객체마다 `__dict__` + left/right 포인터가 필요하므로 정렬된 list보다 3-5배 메모리를 씁니다. BST를 선택하는 이유는 메모리 효율이 아니라, O(log n) 삽입/검색/삭제를 동시에 제공한다는 사실입니다.

## 성능 벤치마크: BST vs sorted list 검색

```python
import bisect
import random
import timeit


def bench_bst_search(bst: BST[int], targets: list[int]) -> None:
    for t in targets:
        _ = t in bst


def bench_bisect_search(sorted_list: list[int], targets: list[int]) -> None:
    for t in targets:
        idx = bisect.bisect_left(sorted_list, t)
        _ = idx < len(sorted_list) and sorted_list[idx] == t


n = 10_000
values = random.sample(range(n * 10), n)
targets = random.sample(values, 1_000)

bst = BST[int]()
for v in values:
    bst.insert(v)
sorted_list = sorted(values)

trials = 10
t_bst = timeit.timeit(lambda: bench_bst_search(bst, targets), number=trials)
t_bisect = timeit.timeit(lambda: bench_bisect_search(sorted_list, targets), number=trials)

print(f"BST search (1k lookups, n=10k):    {t_bst:.4f}s")
print(f"bisect search (1k lookups, n=10k): {t_bisect:.4f}s")
```

순수 Python BST는 `bisect` + list보다 느린 경우가 많습니다. `bisect`는 C로 구현되어 있고, list의 연속 메모리 접근이 캐시 친화적이기 때문입니다. BST가 진짜 유리한 것은 "삽입과 삭제가 빈번한 동적 데이터"입니다. sorted list에 원소를 삽입하려면 O(n) 이동이 필요하지만, BST는 O(log n)에 삽입합니다.

## 순회 방식 비교: 재귀 vs 반복 vs BFS

```python
from collections import deque
from typing import Optional


def inorder_iterative(root: Optional[TreeNode[int]]) -> list[int]:
    """스택을 사용한 반복 중위 순회입니다."""
    result: list[int] = []
    stack: list[TreeNode[int]] = []
    current = root

    while current is not None or stack:
        while current is not None:
            stack.append(current)
            current = current.left
        current = stack.pop()
        result.append(current.value)
        current = current.right

    return result


def level_order(root: Optional[TreeNode[int]]) -> list[list[int]]:
    """BFS 레벨 순회입니다."""
    if root is None:
        return []
    result: list[list[int]] = []
    queue: deque[TreeNode[int]] = deque([root])

    while queue:
        level_size = len(queue)
        level: list[int] = []
        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.value)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)

    return result
```

재귀 중위 순회는 코드가 짧지만, 깊이가 깊은 트리에서 RecursionError 위험이 있습니다. 반복 버전은 명시적 스택을 사용해 이 제한을 피합니다. 레벨 순회는 큐를 사용해 같은 깊이의 노드를 한 번에 처리합니다.

### 균형 트리와 편향 트리

BST의 성능은 트리 높이에 의존합니다. 랜덤 데이터를 넣으면 평균 높이가 O(log n)이지만, 이미 정렬된 데이터를 순서대로 넣으면 한쪽으로만 자라는 편향 트리(skewed tree)가 되어 높이가 O(n)이 됩니다. 이 경우 검색도 O(n)으로 퇴화합니다.

```python
# 편향 트리 생성 예시
skewed = BST[int]()
for i in range(1, 11):
    skewed.insert(i)
print(f"height of skewed BST (10 nodes): {skewed.height()}")  # 9 (최악)

# 균형 트리 생성 예시
import random
balanced = BST[int]()
data = list(range(1, 11))
random.shuffle(data)
for i in data:
    balanced.insert(i)
print(f"height of shuffled BST (10 nodes): {balanced.height()}")  # 3~4
```

실무에서는 이 편향 문제를 해결하기 위해 AVL 트리나 Red-Black 트리 같은 자가 균형 트리를 사용합니다. Python 표준 라이브러리에는 이런 구조가 내장되어 있지 않지만, `sortedcontainers` 패키지가 B-tree 기반의 `SortedList`를 제공합니다.

## unittest로 BST 검증

```python
import unittest


class TestBST(unittest.TestCase):
    def setUp(self) -> None:
        self.bst: BST[int] = BST()
        for v in [50, 30, 70, 20, 40, 60, 80]:
            self.bst.insert(v)

    def test_search_existing(self) -> None:
        self.assertTrue(self.bst.search(30))
        self.assertTrue(self.bst.search(80))

    def test_search_missing(self) -> None:
        self.assertFalse(self.bst.search(25))
        self.assertFalse(self.bst.search(100))

    def test_inorder_sorted(self) -> None:
        self.assertEqual(list(self.bst.inorder()), [20, 30, 40, 50, 60, 70, 80])

    def test_height(self) -> None:
        self.assertEqual(self.bst.height(), 2)

    def test_min_value(self) -> None:
        self.assertEqual(self.bst.min_value(), 20)

    def test_contains(self) -> None:
        self.assertIn(50, self.bst)
        self.assertNotIn(99, self.bst)

    def test_duplicate_ignored(self) -> None:
        self.bst.insert(50)
        self.assertEqual(len(self.bst), 7)

    def test_empty_tree(self) -> None:
        empty: BST[int] = BST()
        self.assertEqual(empty.height(), -1)
        self.assertEqual(len(empty), 0)
        with self.assertRaises(ValueError):
            empty.min_value()


if __name__ == "__main__":
    unittest.main()
```

## 처음 질문으로 돌아가기

- **파일 시스템, DOM, 조직도는 왜 트리 구조로 모델링될까요?**
  - 이들은 모두 "하나의 루트에서 시작해 계층적으로 분기하는" 관계를 갖습니다. 순환이 없고, 모든 노드가 정확히 하나의 부모를 갖습니다. 이 특성이 트리의 정의와 정확히 일치하므로, 트리로 모델링하면 탐색·삽입·삭제 알고리즘을 바로 적용할 수 있습니다.
- **트리의 루트, 리프, 깊이, 높이는 각각 무엇을 뜻할까요?**
  - 루트는 부모가 없는 최상위 노드, 리프는 자식이 없는 말단 노드입니다. 깊이는 루트에서 해당 노드까지의 간선 수, 높이는 해당 노드에서 가장 먼 리프까지의 간선 수입니다. 전체 트리의 높이는 루트의 높이와 같습니다.
- **이진 트리 순회는 왜 재귀와 잘 맞을까요?**
  - 이진 트리는 "노드 + 왼쪽 서브트리 + 오른쪽 서브트리"라는 재귀적 구조를 갖습니다. 순회 로직도 "현재 노드 처리 + 왼쪽 재귀 + 오른쪽 재귀"로 자연스럽게 분해됩니다. 재귀 호출 스택이 트리 경로를 자동으로 추적해 주므로, 별도의 자료구조 없이 깊이 우선 탐색이 가능합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Structures with Python 101 (1/10): 자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [Data Structures with Python 101 (2/10): 배열과 리스트](./02-arrays-and-lists.md)
- [Data Structures with Python 101 (3/10): 스택과 큐](./03-stacks-and-queues.md)
- [Data Structures with Python 101 (4/10): 해시 테이블과 dict](./04-hash-tables-and-dict.md)
- [Data Structures with Python 101 (5/10): 연결 리스트](./05-linked-lists.md)
- **트리와 이진 트리 (현재 글)**
- 힙과 우선순위 큐 (예정)
- 그래프 표현 (예정)
- set과 집합 연산 (예정)
- 자료구조 선택 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Runestone Academy — Trees](https://runestone.academy/ns/books/published/pythonds3/Trees/toctree.html)
- [Python 공식 문서 — bisect](https://docs.python.org/3/library/bisect.html)
- [SQLite File Format — B-Tree Pages](https://www.sqlite.org/fileformat.html#b_tree_pages)
- [Real Python — Binary Trees in Python](https://realpython.com/binary-search-python/)
- [book-examples 저장소 — data-structures-python-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/data-structures-python-101/ko)

Tags: Python, 자료구조, Tree, Binary Tree, BST
