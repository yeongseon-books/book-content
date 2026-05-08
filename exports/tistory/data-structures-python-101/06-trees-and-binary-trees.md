
# 트리와 이진 트리

> Data Structures with Python 101 시리즈 (6/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 파일 시스템, 조직도, DOM은 왜 트리 구조를 사용할까요?

> 트리는 계층적 관계를 자연스럽게 표현하는 자료구조입니다. 이진 탐색 트리(BST)는 정렬된 데이터에서 O(log n) 검색을 가능하게 합니다. 이 글에서는 트리의 개념, 이진 트리 구현, 순회 알고리즘, 이진 탐색 트리를 다룹니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 트리의 기본 용어와 구조
- 이진 트리의 Python 구현
- 전위·중위·후위·레벨 순회
- 이진 탐색 트리(BST)의 동작 원리

## 왜 중요한가

트리는 컴퓨터 과학에서 가장 중요한 자료구조 중 하나입니다. 파일 시스템, HTML DOM, 데이터베이스 인덱스(B-Tree), JSON 파싱 트리 등 어디에나 트리가 있습니다.

> 트리를 이해하면 재귀적 사고 능력이 크게 향상됩니다. 대부분의 트리 알고리즘은 재귀로 자연스럽게 표현됩니다.

이진 탐색 트리는 정렬된 데이터를 유지하면서 삽입, 삭제, 검색을 O(log n)에 수행합니다. 이는 list의 선형 검색 O(n)보다 월등히 빠릅니다.

## 핵심 개념 잡기

> 트리 = 루트에서 시작하여 자식 노드로 뻗어나가는 계층 구조

```
        [루트]
       /      \
    [자식]   [자식]
    /   \       \
 [잎]  [잎]    [잎]

이진 탐색 트리 (BST):
        [8]
       /   \
     [3]   [10]
    /   \      \
  [1]   [6]   [14]
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 루트(root) | 트리의 최상위 노드입니다 |
| 잎(leaf) | 자식이 없는 노드입니다 |
| 깊이(depth) | 루트에서 해당 노드까지의 거리입니다 |
| 높이(height) | 해당 노드에서 가장 먼 잎까지의 거리입니다 |
| 이진 탐색 트리(BST) | 왼쪽 자식 < 부모 < 오른쪽 자식 규칙을 따르는 트리입니다 |

## Before / After

정렬된 리스트에서 검색하는 방법과 BST에서 검색하는 방법을 비교합니다.

```python
# before: 정렬된 리스트에서 선형 검색 — O(n)
data = [1, 3, 6, 8, 10, 14]
for item in data:
    if item == 10:
        print("found")
        break
```

```python
# after: BST에서 검색 — O(log n)
# BST: 8 → 10 → found (2단계)
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

## 단계별 실습

### Step 1: 이진 트리 노드 정의

```python
class TreeNode:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

    def __repr__(self):
        return f"TreeNode({self.data})"
```

### Step 2: 트리 순회 구현

```python
def inorder(node):
    """중위 순회: 왼쪽 → 루트 → 오른쪽"""
    if node is None:
        return []
    return inorder(node.left) + [node.data] + inorder(node.right)

def preorder(node):
    """전위 순회: 루트 → 왼쪽 → 오른쪽"""
    if node is None:
        return []
    return [node.data] + preorder(node.left) + preorder(node.right)

def postorder(node):
    """후위 순회: 왼쪽 → 오른쪽 → 루트"""
    if node is None:
        return []
    return postorder(node.left) + postorder(node.right) + [node.data]

# 트리 구성:     1
#              /   \
#             2     3
#            / \
#           4   5
root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)
root.left.left = TreeNode(4)
root.left.right = TreeNode(5)

print(f"중위: {inorder(root)}")    # [4, 2, 5, 1, 3]
print(f"전위: {preorder(root)}")   # [1, 2, 4, 5, 3]
print(f"후위: {postorder(root)}")  # [4, 5, 2, 3, 1]
```

### Step 3: 레벨 순회 (BFS)

```python
from collections import deque

def level_order(root):
    """레벨 순회: 같은 깊이의 노드를 왼쪽에서 오른쪽으로"""
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

print(f"레벨: {level_order(root)}")  # [1, 2, 3, 4, 5]
```

### Step 4: 이진 탐색 트리 구현

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

print(bst.inorder())       # [1, 3, 6, 8, 10, 14] — 정렬 결과
print(bst.search(6))       # True
print(bst.search(7))       # False
```

### Step 5: 트리 높이와 노드 수 계산

```python
def tree_height(node):
    if node is None:
        return -1
    return 1 + max(tree_height(node.left), tree_height(node.right))

def count_nodes(node):
    if node is None:
        return 0
    return 1 + count_nodes(node.left) + count_nodes(node.right)

print(f"높이: {tree_height(bst.root)}")    # 2
print(f"노드 수: {count_nodes(bst.root)}") # 6
```

## 이 코드에서 주목할 점

- 트리 알고리즘은 재귀로 자연스럽게 표현됩니다 — base case는 node is None
- BST의 중위 순회는 정렬된 결과를 반환합니다
- 레벨 순회는 큐(deque)를 사용합니다 — BFS 패턴
- BST의 검색은 매 단계에서 반을 버리므로 O(log n)입니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 재귀 base case 누락 | 무한 재귀로 RecursionError 발생합니다 | node is None 체크를 항상 먼저 합니다 |
| BST에 중복 값 삽입 미처리 | 예상과 다른 트리 구조가 됩니다 | 중복 정책을 명확히 정합니다 (무시 또는 카운트) |
| 편향 트리 미인식 | BST가 O(n)으로 퇴화합니다 | 균형 트리(AVL, Red-Black)를 고려합니다 |
| 순회 순서 혼동 | 잘못된 결과가 나옵니다 | 전위(NLR), 중위(LNR), 후위(LRN)를 외웁니다 |
| 삭제 연산의 복잡성 과소평가 | 자식이 2개인 노드 삭제가 까다롭습니다 | 후계자(in-order successor) 패턴을 학습합니다 |

## 실무에서 이렇게 쓰입니다

- 데이터베이스 인덱스가 B-Tree/B+Tree로 구현됩니다
- 파일 시스템의 디렉터리 구조가 트리입니다
- HTML/XML DOM이 트리 구조입니다
- 표현식 파서가 AST(추상 구문 트리)를 생성합니다
- 자동 완성 기능이 Trie(접두사 트리)로 구현됩니다

## 현업 개발자는 이렇게 생각합니다

실무에서 BST를 직접 구현할 일은 드뭅니다. Python의 `sorted()`, `bisect` 모듈, 또는 데이터베이스의 인덱스가 대부분의 정렬·검색 요구를 처리합니다. 하지만 트리의 원리를 이해하면 이런 도구가 어떻게 동작하는지 파악할 수 있습니다.

재귀적 사고를 연습하기에 트리만한 자료구조가 없습니다. 트리 문제를 많이 풀수록 재귀를 자연스럽게 사용하게 됩니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **재귀 vs 반복** — 깊은 트리는 명시적 스택으로 안전성을 확보합니다.
- **순회 종류** — 전위·중위·후위·레벨 차이를 명확히 합니다.
- **불변식** — BST 불변식을 코드로 검증합니다.
- **표준 라이브러리** — 균형 트리는 sortedcontainers로 대체합니다.
- **응용** — 파일 시스템·DOM·식 구문 분석에서 응용을 본다.

## 체크리스트

- [ ] 트리의 루트, 잎, 깊이, 높이를 설명할 수 있다
- [ ] 전위, 중위, 후위, 레벨 순회를 구현할 수 있다
- [ ] BST에서 삽입과 검색을 구현할 수 있다
- [ ] BST의 중위 순회가 정렬된 결과를 반환하는 이유를 설명할 수 있다
- [ ] 트리의 높이와 노드 수를 재귀로 계산할 수 있다

## 연습 문제

1. 이진 트리가 BST인지 검증하는 함수를 작성하세요. (힌트: 중위 순회 결과가 정렬되어 있어야 합니다)
2. 두 이진 트리가 구조적으로 동일한지 확인하는 함수를 작성하세요.
3. BST에서 값을 삭제하는 함수를 구현하세요. (자식이 0, 1, 2개인 경우를 모두 처리)

## 정리 및 다음 글 안내

트리는 계층 구조를 표현하는 자료구조이고, BST는 정렬된 데이터를 O(log n)에 검색합니다. 트리 순회는 재귀로 자연스럽게 구현됩니다. 다음 글에서는 트리의 특수한 형태인 힙과 우선순위 큐를 다룹니다.

- [자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [배열과 리스트](./02-arrays-and-lists.md)
- [스택과 큐](./03-stacks-and-queues.md)
- [해시 테이블과 dict](./04-hash-tables-and-dict.md)
- [연결 리스트](./05-linked-lists.md)
- **트리와 이진 트리 (현재 글)**
- 힙과 우선순위 큐 (예정)
- 그래프 표현 (예정)
- set과 집합 연산 (예정)
- 자료구조 선택 기준 (예정)
## 참고 자료

- [Real Python — Binary Trees in Python](https://realpython.com/binary-search-python/)
- [GeeksforGeeks — Binary Search Tree](https://www.geeksforgeeks.org/binary-search-tree-data-structure/)
- [Visualgo — Binary Search Tree Visualization](https://visualgo.net/en/bst)
- [Problem Solving with Algorithms — Trees](https://runestone.academy/ns/books/published/pythonds3/Trees/toctree.html)

Tags: Python, 자료구조, Tree, Binary Tree, BST

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
