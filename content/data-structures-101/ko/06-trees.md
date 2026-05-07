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

<!-- a-grade-intro:begin -->

**핵심 질문**: 파일 시스템, HTML DOM, 조직도, 정규식 파서가 공통적으로 의지하는 자료구조는 무엇일까요?

> 트리는 한 노드에서 시작해 여러 자식 노드로 가지를 뻗어 가는 계층적 자료구조입니다. 사이클이 없고, 모든 노드가 정확히 하나의 부모를 가진다는 두 가지 규칙만으로 거의 모든 계층 구조를 표현할 수 있습니다. 이 글에서는 트리의 기본 용어, 표현 방법, 그리고 가장 자주 쓰이는 세 가지 순회 방식(전위·중위·후위)을 직접 구현해 봅니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 트리의 핵심 용어(루트, 잎, 깊이, 높이)
- 일반 트리와 이진 트리의 차이
- 깊이 우선 순회의 세 가지 방식(전위·중위·후위)
- 너비 우선 순회와의 비교

## 왜 중요한가

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

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| 루트(root) | 부모가 없는 유일한 노드 |
| 잎(leaf) | 자식이 없는 노드 |
| 깊이(depth) | 루트에서 해당 노드까지의 간선 수 |
| 높이(height) | 노드에서 가장 먼 잎까지의 간선 수 |
| 서브트리(subtree) | 어떤 노드와 그 자손으로 이루어진 트리 |

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

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 트리를 만나면 가장 먼저 "이 트리가 균형 잡혀 있는가"를 묻습니다. 균형 트리는 O(log n)을 보장하지만, 한 줄로 늘어진 트리는 사실상 연결 리스트이고 O(n)입니다. AVL·Red-Black·B-Tree 같은 균형 트리는 이 한계를 해결하기 위한 연구의 산물입니다.

또한 시니어는 깊은 재귀를 두려워합니다. 사용자 입력으로 깊이가 결정되는 트리(JSON 파싱 등)에서는 명시적 스택으로 변환해 안전성을 확보합니다. 알고리즘이 우아한 것과 운영 환경에서 안전한 것은 별개의 문제입니다.

## 체크리스트

- [ ] 루트, 잎, 깊이, 높이 같은 트리 용어를 정확히 사용할 수 있는가
- [ ] 일반 트리와 이진 트리의 차이를 설명할 수 있는가
- [ ] 전위·중위·후위 순회가 무엇이 다른지 알고 있는가
- [ ] DFS와 BFS의 차이가 자료구조 선택임을 이해했는가
- [ ] 균형 트리와 비균형 트리의 시간 복잡도 차이를 인지했는가

## 연습 문제

1. 위 이진 트리에서 "각 레벨의 평균값"을 출력하는 함수를 작성해 보세요. BFS와 dict의 조합을 사용합니다.

2. 어떤 트리가 "균형 잡혀 있다(balanced)"는 정의를 한 가지 만들고, 그 정의를 검증하는 함수를 작성해 보세요.

3. 일반 트리(자식 리스트 형태)에서 가장 깊은 잎의 깊이를 구하는 함수를 재귀로 작성해 보세요. 같은 함수를 명시적 스택으로도 작성해 비교해 봅니다.

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
