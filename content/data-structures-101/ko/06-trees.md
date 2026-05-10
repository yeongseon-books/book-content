---
series: data-structures-101
episode: 6
title: 트리
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
  - 트리
  - 계층 구조
  - 재귀
  - 순회
seo_description: 트리 자료구조의 기본 용어, 표현 방법, 그리고 전위·중위·후위 순회를 직접 구현하며 익힙니다.
last_reviewed: '2026-05-04'
---

# 트리

> Data Structures 101 시리즈 (6/10)


## 이 글에서 다룰 문제

트리는 거의 모든 계층 데이터의 기본 골격입니다. 데이터베이스 인덱스, 컴파일러의 추상 구문 트리(AST), 운영체제의 파일 시스템, JSON/XML 파싱 결과 등이 모두 트리입니다. 트리를 능숙하게 다루지 못하면 그래프·BST·힙 같은 더 정교한 자료구조도 다루기 어렵습니다.

> 트리는 "재귀가 가장 자연스러운 자료구조"입니다.

## 개념 한눈에 보기

> 트리는 노드와 간선으로 이루어진 그래프 중 사이클이 없고 연결되어 있는 것입니다. 이진 트리는 자식이 최대 둘인 트리이며, 알고리즘에서 가장 자주 사용됩니다.

```text
            A          ← 루트(root), 깊이 0
          /   \
         B     C       ← 깊이 1
        / \     \
       D   E     F     ← 깊이 2 (잎: leaf)

용어:
- A의 자식: B, C
- B의 부모: A
- B의 형제: C
- 잎(leaf): D, E, F
- 트리의 높이(height): 2
- 노드 수: 6
```

## Before / After

**Before — 평면 리스트로 계층 표현:**

```python
items = [
    ("/", None),
    ("home", "/"),
    ("docs", "/home"),
    ("a.txt", "/home/docs"),
]
# 부모 찾기, 자식 나열, 깊이 계산이 모두 번거로움
```

**After — 트리 노드로 계층 표현:**

```python
class Node:
    def __init__(self, name):
        self.name = name
        self.children = []

root = Node("/")
home = Node("home"); root.children.append(home)
docs = Node("docs"); home.children.append(docs)
docs.children.append(Node("a.txt"))
# 자식·자손 순회가 자연스러운 재귀로 표현됨
```

## 실습: 단계별로 따라하기

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

각 노드는 값과 자식 목록을 가집니다. 자식 수에 제한이 없으면 일반 트리입니다.

### 2단계: 이진 트리

```python
class BinaryNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


# 트리 만들기
#         1
#        / \
#       2   3
#      / \
#     4   5
root = BinaryNode(1,
                  BinaryNode(2, BinaryNode(4), BinaryNode(5)),
                  BinaryNode(3))
```

자식이 최대 둘이라 메모리 구조가 단순하고 알고리즘이 정형화됩니다.

### 3단계: 깊이 우선 순회 세 가지

```python
def preorder(node):
    """루트 → 왼쪽 → 오른쪽"""
    if node is None:
        return
    print(node.value, end=" ")
    preorder(node.left)
    preorder(node.right)


def inorder(node):
    """왼쪽 → 루트 → 오른쪽"""
    if node is None:
        return
    inorder(node.left)
    print(node.value, end=" ")
    inorder(node.right)


def postorder(node):
    """왼쪽 → 오른쪽 → 루트"""
    if node is None:
        return
    postorder(node.left)
    postorder(node.right)
    print(node.value, end=" ")


print("전위:", end=" "); preorder(root); print()
print("중위:", end=" "); inorder(root); print()
print("후위:", end=" "); postorder(root); print()
# 전위: 1 2 4 5 3
# 중위: 4 2 5 1 3
# 후위: 4 5 2 3 1
```

루트를 언제 처리하느냐에 따라 세 가지 순회가 만들어집니다. 표현식 평가는 후위, 트리 복제는 전위, BST 정렬 출력은 중위가 적합합니다.

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

같은 깊이의 노드를 먼저 모두 방문합니다. "최단 경로"나 "레벨별 처리"가 필요할 때 자연스럽습니다.

### 5단계: 트리의 깊이와 노드 수 계산

```python
def height(node):
    if node is None:
        return -1
    return 1 + max(height(node.left), height(node.right))


def count(node):
    if node is None:
        return 0
    return 1 + count(node.left) + count(node.right)


print(f"높이: {height(root)}")    # 2
print(f"노드 수: {count(root)}")   # 5
```

재귀가 트리에서 자연스러운 이유는 트리의 정의 자체가 재귀적이기 때문입니다("트리는 루트와 자식 트리들로 이루어진다").

## 이 코드에서 주목할 점

- 트리는 정의 자체가 재귀적이라 재귀 함수와 자연스럽게 맞물립니다
- 깊이 우선과 너비 우선의 차이는 자료구조(스택 vs 큐)의 차이입니다
- 이진 트리는 일반 트리보다 단순하지만 더 풍부한 알고리즘이 존재합니다
- 트리 깊이가 너무 크면 재귀 호출 스택이 터질 수 있습니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 자식 리스트와 left/right 혼동 | 일반 트리와 이진 트리 코드를 섞음 | 두 표현을 명확히 구분 |
| 빈 노드 분기 누락 | NoneType 에러 | 재귀 첫 줄에서 None 체크 |
| 깊이와 높이 혼동 | 알고리즘 분석 오류 | 깊이는 위에서, 높이는 아래에서 |
| 깊은 트리에서 재귀 사용 | RecursionError | 명시적 스택으로 변환 |
| BFS에 list 사용 | O(n) pop으로 느려짐 | `collections.deque` 사용 |

## 실무에서는 이렇게 쓰입니다

- 파일 시스템: 디렉터리 트리는 일반 트리의 대표 사례
- HTML/XML DOM: 브라우저는 문서를 트리로 파싱
- 컴파일러: 소스 코드 → 추상 구문 트리(AST) → 코드 생성
- 데이터베이스: B-Tree/B+Tree 인덱스로 정렬 데이터 검색 가속
- 의사결정 트리(Decision Tree): 머신러닝의 분류·회귀 모델

## 체크리스트

- [ ] 루트, 잎, 깊이, 높이 같은 트리 용어를 정확히 사용할 수 있는가
- [ ] 일반 트리와 이진 트리의 차이를 설명할 수 있는가
- [ ] 전위·중위·후위 순회가 무엇이 다른지 알고 있는가
- [ ] DFS와 BFS의 차이가 자료구조 선택임을 이해했는가
- [ ] 균형 트리와 비균형 트리의 시간 복잡도 차이를 인지했는가

## 정리 및 다음 단계

트리는 사이클이 없고 부모가 정확히 하나인 계층 자료구조이며, 재귀와 가장 자연스럽게 맞물리는 형태입니다. 깊이 우선 순회의 세 가지(전위·중위·후위)와 너비 우선 순회는 트리 알고리즘의 기본 도구이며, 자료구조(스택 vs 큐)의 선택만으로 동작이 달라집니다. 이진 트리는 일반 트리의 특수 형태이지만 더 풍부한 알고리즘이 존재합니다.

다음 글에서는 정렬된 이진 트리인 이진 탐색 트리(BST)를 살펴봅니다. 평균 O(log n) 검색을 제공하지만 균형이 깨지면 O(n)으로 떨어지는 미묘한 자료구조입니다.

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
