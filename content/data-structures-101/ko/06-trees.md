---
series: data-structures-101
episode: 6
title: 트리
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
  - 트리
  - 계층 구조
  - 재귀
  - 순회
seo_description: 계층적 데이터를 표현하는 트리의 핵심 용어와 순회 방식, 재귀적 특성 및 이진 트리의 구조를 상세히 다룹니다.
last_reviewed: '2026-05-12'
---

# 트리

이 글은 Data Structures 101 시리즈의 여섯 번째 글입니다.

## 이 글에서 다룰 문제

- 루트, 리프, 깊이, 높이 같은 트리 용어를 어떻게 정확히 구분할까요?
- 일반 트리와 이진 트리는 어떤 점이 다를까요?
- 전위·중위·후위 순회는 무엇이 다르고 어디에 쓰일까요?
- DFS와 BFS의 차이가 결국 스택과 큐의 차이라는 말은 왜 성립할까요?

파일 시스템, HTML DOM, 조직도, 정규식 파서는 서로 다른 분야처럼 보이지만 공통된 뼈대를 공유합니다. 바로 계층 구조를 표현하는 트리입니다.

> 트리는 하나의 시작 노드에서 여러 자식으로 뻗어나가는 계층 구조입니다. 사이클이 없고 각 노드는 부모를 하나만 가진다는 두 규칙만으로도 대부분의 계층 데이터를 표현할 수 있습니다. 그래서 트리는 재귀가 가장 자연스럽게 들어맞는 자료구조입니다.

## 왜 중요한가

트리는 데이터베이스 인덱스, 컴파일러의 AST, 운영체제 파일 시스템, JSON/XML 파서 결과처럼 거의 모든 계층형 데이터의 기본 골격입니다. 트리를 편하게 다루지 못하면 그래프, BST, 힙도 끝까지 자신 있게 읽기 어렵습니다.

> 트리는 재귀가 가장 자연스럽게 느껴지는 구조입니다.

## 핵심 한눈에 보기

> 트리는 연결되어 있고 사이클이 없는 그래프입니다. 그중 이진 트리는 각 노드가 자식을 최대 두 개까지만 가지는 특수한 형태이며, 알고리즘에서 가장 자주 등장합니다.

```text
            A          ← root, depth 0
          /   \
         B     C       ← depth 1
        / \     \
       D   E     F     ← depth 2 (leaves)

terms:
- A's children: B, C
- B's parent: A
- B's sibling: C
- leaves: D, E, F
- height of the tree: 2
- node count: 6
```

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| 루트 | 부모가 없는 유일한 노드 |
| 리프 | 자식이 없는 노드 |
| 깊이 | 루트에서 해당 노드까지의 간선 수 |
| 높이 | 해당 노드에서 가장 먼 리프까지의 간선 수 |
| 서브트리 | 어떤 노드와 그 자손 전체 |

## Before / After

**Before — representing hierarchy with a flat list:**

```python
items = [
    ("/", None),
    ("home", "/"),
    ("docs", "/home"),
    ("a.txt", "/home/docs"),
]
# Finding parents, listing children, computing depth — all painful
```

**After — representing hierarchy with tree nodes:**

```python
class Node:
    def __init__(self, name):
        self.name = name
        self.children = []

root = Node("/")
home = Node("home"); root.children.append(home)
docs = Node("docs"); home.children.append(docs)
docs.children.append(Node("a.txt"))
# Children and descendants traverse naturally with recursion
```

평면 리스트로도 관계를 표현할 수는 있지만, 부모 찾기·자식 나열·깊이 계산이 모두 불편합니다. 트리 구조를 쓰면 순회가 훨씬 자연스러워집니다.

## 단계별로 따라하기

### 1단계: 일반 트리 정의

```python
class TreeNode:
    def __init__(self, value):
        self.value = value
        self.children = []

    def add(self, child):
        self.children.append(child)
        return child


root = TreeNode("CEO")
cto = root.add(TreeNode("CTO"))
cfo = root.add(TreeNode("CFO"))
cto.add(TreeNode("Backend Lead"))
cto.add(TreeNode("Frontend Lead"))
cfo.add(TreeNode("Accountant"))
```

각 노드는 값과 자식 리스트를 가집니다. 자식 수에 제한이 없으므로 이것은 일반 트리입니다.

### 2단계: 이진 트리

```python
class BinaryNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


# Build the tree
#         1
#        / \
#       2   3
#      / \
#     4   5
root = BinaryNode(1,
                  BinaryNode(2, BinaryNode(4), BinaryNode(5)),
                  BinaryNode(3))
```

자식이 최대 두 개로 제한되면 메모리 구조가 단순해지고 알고리즘 패턴도 표준화됩니다.

### 3단계: 깊이 우선 순회 세 가지

```python
def preorder(node):
    """root -> left -> right"""
    if node is None:
        return
    print(node.value, end=" ")
    preorder(node.left)
    preorder(node.right)


def inorder(node):
    """left -> root -> right"""
    if node is None:
        return
    inorder(node.left)
    print(node.value, end=" ")
    inorder(node.right)


def postorder(node):
    """left -> right -> root"""
    if node is None:
        return
    postorder(node.left)
    postorder(node.right)
    print(node.value, end=" ")


print("preorder: ", end=""); preorder(root); print()
print("inorder:  ", end=""); inorder(root); print()
print("postorder:", end=""); postorder(root); print()
# preorder:  1 2 4 5 3
# inorder:   4 2 5 1 3
# postorder: 4 5 2 3 1
```

언제 루트를 방문하느냐가 순회를 구분합니다. 후위 순회는 계산 트리 평가에, 전위 순회는 복제나 직렬화에, 중위 순회는 BST 정렬 출력에 자주 쓰입니다.

### 4단계: 너비 우선 순회

```python
from collections import deque


def bfs(root):
    if root is None:
        return
    queue = deque([root])
    while queue:
        node = queue.popleft()
        print(node.value, end=" ")
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)


print("BFS:", end=" "); bfs(root); print()   # 1 2 3 4 5
```

같은 깊이의 노드를 먼저 모두 방문한 뒤 아래로 내려갑니다. 최단 경로나 레벨별 처리가 필요할 때 유용합니다.

### 5단계: 높이와 크기 계산

```python
def height(node):
    if node is None:
        return -1
    return 1 + max(height(node.left), height(node.right))


def count(node):
    if node is None:
        return 0
    return 1 + count(node.left) + count(node.right)


print(f"height: {height(root)}")    # 2
print(f"count:  {count(root)}")     # 5
```

트리는 정의 자체가 재귀적입니다. “트리는 루트와 여러 서브트리의 집합”이라는 문장을 그대로 코드로 옮길 수 있습니다.

## 이 코드에서 주목할 점

- 트리는 정의부터 재귀적이라 재귀 함수와 잘 맞습니다.
- DFS와 BFS의 차이는 결국 스택과 큐의 선택입니다.
- 이진 트리는 일반 트리보다 제약이 크지만 알고리즘은 더 풍부합니다.
- 너무 깊은 트리는 재귀 스택 한계를 쉽게 건드립니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| children 리스트와 left/right를 섞어 씀 | 일반 트리와 이진 트리 코드가 꼬임 | 표현 방식을 명확히 분리합니다 |
| 빈 노드 분기를 빼먹음 | `NoneType` 오류가 남 | 재귀 진입부에서 `None`을 먼저 처리합니다 |
| 깊이와 높이를 혼동함 | 분석이 틀어짐 | 깊이는 위에서, 높이는 아래에서 센다고 기억합니다 |
| 깊은 트리에 재귀만 사용함 | `RecursionError`가 발생함 | 명시적 스택으로 바꿉니다 |
| BFS에 list를 사용함 | `pop(0)`가 느려짐 | `collections.deque`를 사용합니다 |

## 실무에서는 이렇게 쓰입니다

- 파일 시스템은 일반 트리의 대표 사례입니다.
- 브라우저는 HTML과 XML을 DOM 트리로 파싱합니다.
- 컴파일러는 소스 코드를 AST로 바꾼 뒤 후속 단계를 진행합니다.
- 데이터베이스는 B-Tree, B+Tree 인덱스로 정렬된 키 탐색을 가속합니다.
- 의사결정 트리는 여러 머신러닝 분류기와 회귀기의 기반입니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 먼저 트리가 균형 잡혀 있는지를 봅니다. 균형이 잡힌 트리는 O(log n)을 기대할 수 있지만, 한쪽으로 무너진 트리는 사실상 연결 리스트가 되어 O(n)으로 떨어지기 때문입니다. AVL, Red-Black, B-Tree가 존재하는 이유도 여기에 있습니다.

또한 사용자 입력이 트리 깊이를 결정하는 상황에서는 재귀를 경계합니다. JSON 파싱처럼 입력이 깊어질 수 있는 경우에는 명시적 스택으로 바꿔 운영 안전성을 먼저 확보합니다.

## 체크리스트

- [ ] 루트, 리프, 깊이, 높이를 정확히 사용할 수 있습니다
- [ ] 일반 트리와 이진 트리의 차이를 설명할 수 있습니다
- [ ] 전위·중위·후위 순회의 차이를 이해했습니다
- [ ] DFS와 BFS를 자료구조 선택으로 설명할 수 있습니다
- [ ] 균형 트리와 비균형 트리의 시간 복잡도 차이를 알고 있습니다

## 연습 문제

1. 위 이진 트리의 각 레벨 평균값을 구하는 함수를 작성해 보세요. BFS와 dict를 조합하면 됩니다.

2. 트리의 “균형”을 직접 정의하고, 그 정의를 검사하는 함수를 구현해 보세요.

3. 일반 트리(children 리스트)에서 가장 깊은 리프의 깊이를 구하는 재귀 함수를 작성한 뒤, 같은 기능을 명시적 스택 버전으로 다시 구현해 비교해 보세요.

## 정리 및 다음 단계

트리는 사이클이 없고 각 노드가 부모를 하나만 가지는 계층 구조이며, 재귀와 가장 자연스럽게 맞물립니다. 전위·중위·후위 순회와 BFS는 트리 알고리즘의 기본 도구이고, DFS와 BFS를 바꾸는 것은 결국 스택과 큐를 바꾸는 일입니다. 이진 트리는 일반 트리의 특수 형태지만 훨씬 풍부한 알고리즘을 제공합니다.

다음 글에서는 정렬된 이진 트리인 이진 탐색 트리(BST)를 봅니다. 평균 O(log n) 탐색을 제공하지만 균형이 깨지면 O(n)으로 무너지는, 매우 중요한 구조입니다.

<!-- toc:begin -->
- [자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [배열과 동적 배열](./02-arrays-and-dynamic-arrays.md)
- [연결 리스트](./03-linked-lists.md)
- [스택과 큐](./04-stacks-and-queues.md)
- [해시 테이블](./05-hash-tables.md)
- **트리 (현재 글)**
- 이진 탐색 트리 (예정)
- 힙 (예정)
- 그래프 (예정)
- 자료구조 선택 기준 (예정)
<!-- toc:end -->

## 참고 자료

- [Open Data Structures — Binary Trees](https://opendatastructures.org/ods-python/6_Binary_Trees.html)
- [Wikipedia — Tree (data structure)](https://en.wikipedia.org/wiki/Tree_(data_structure))
- [Wikipedia — Tree Traversal](https://en.wikipedia.org/wiki/Tree_traversal)
- [Python `ast` module docs](https://docs.python.org/3/library/ast.html)

Tags: Computer Science, 자료구조, 트리, 계층 구조, 재귀, 순회
