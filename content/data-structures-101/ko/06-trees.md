---
series: data-structures-101
episode: 6
title: "Data Structures 101 (6/10): 트리"
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
  - 트리
  - 계층 구조
  - 재귀
  - 순회
seo_description: 계층적 데이터를 표현하는 트리의 핵심 용어와 순회 방식, 재귀적 특성 및 이진 트리의 구조를 상세히 다룹니다.
last_reviewed: '2026-05-12'
---

# Data Structures 101 (6/10): 트리

이 글은 Data Structures 101 시리즈의 여섯 번째 글입니다.

## 먼저 던지는 질문

- 루트, 리프, 깊이, 높이 같은 트리 용어를 어떻게 정확히 구분할까요?
- 일반 트리와 이진 트리는 어떤 점이 다를까요?
- 전위·중위·후위 순회는 무엇이 다르고 어디에 쓰일까요?

## 큰 그림

![Data Structures 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-101/06/06-01-big-picture.ko.png)

*Data Structures 101 6장 흐름 개요*

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

## 전후 비교

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


## 구현 관점 보강: 복잡도와 선택 기준

자료구조를 비교할 때는 평균 시간 복잡도만으로 결론을 내리면 정확도가 떨어집니다. 실제 시스템에서는 데이터 분포, 갱신 비율, 메모리 제약, 동시성 요구가 동시에 작동하기 때문입니다. 따라서 아래 표처럼 연산별 상한과 운영 조건을 함께 보는 기준이 필요합니다.

| 구조 | 조회 | 삽입 | 삭제 | 메모리 특성 | 적합한 상황 |
| --- | --- | --- | --- | --- | --- |
| 배열/동적 배열 | O(1) 인덱스, O(n) 탐색 | 끝 O(1) amortized, 중간 O(n) | 중간 O(n) | 연속 메모리, 캐시 효율 우수 | 읽기 중심, 랜덤 액세스 필요 |
| 연결 리스트 | O(n) | 노드 위치 확보 시 O(1) | 노드 위치 확보 시 O(1) | 포인터 오버헤드 큼 | 중간 삽입/삭제 빈번 |
| 해시 테이블 | 평균 O(1), 최악 O(n) | 평균 O(1) | 평균 O(1) | 버킷/재해시 비용 존재 | 키 기반 빠른 조회 |
| 균형 트리 | O(log n) | O(log n) | O(log n) | 포인터 구조, 정렬 유지 | 범위 질의, 순서 보존 |

구현 단계에서는 연산 정의를 코드 시그니처로 먼저 고정하는 방식이 안전합니다. 예를 들어 `insert`, `remove`, `contains`, `iterate`의 사전/사후 조건을 먼저 문서화하고, 그 뒤에 내부 저장 구조를 바꾸면 테스트 재사용성이 크게 올라갑니다. 같은 인터페이스에 배열 기반 구현과 링크 기반 구현을 각각 붙여 벤치마크하면, 개념 설명에서 보던 복잡도 표가 실제 지연 시간으로 어떻게 드러나는지 확인할 수 있습니다.

또한 사용 사례 비교는 데이터 흐름 단위로 해야 합니다. 예를 들어 이벤트 로그 파이프라인에서는 "대량 append + 배치 스캔" 패턴이 많아 동적 배열이 유리하지만, 작업 스케줄러에서는 "우선순위 갱신 + 최소값 추출"이 반복되어 힙이 더 적합합니다. 반대로 온라인 추천 시스템의 피처 저장소는 키 조회 비율이 매우 높아 해시 기반 구조가 기본 선택이 됩니다.

실습 팁으로는 동일한 입력 집합에 대해 최소 두 가지 구조를 구현하고, 다음 항목을 비교 기록하는 방식이 좋습니다: (1) 연산당 평균 지연 시간, (2) p95 지연 시간, (3) 메모리 사용량, (4) 구현 복잡도. 이 네 가지를 같이 보면 단순 Big-O 표기법이 놓치는 현실 제약까지 반영한 결정을 내릴 수 있습니다.

실무 적용 관점에서는 입력 데이터의 크기뿐 아니라 업데이트 패턴, 동시 접근, 메모리 상한을 함께 고려해 구조를 선택해야 안정적인 성능이 나옵니다.




## 실전 앵커: 구현과 복잡도 검증

개념을 정확히 이해하려면 설명 문장만 보는 것으로는 부족합니다. 손으로 구현하고, 연산 단위를 측정하고, 메모리 배치를 눈으로 그려 보는 과정이 함께 있어야 합니다. 아래 앵커는 이 시리즈 전체에서 공통으로 재사용할 수 있는 검증 틀입니다.

### 파이썬 미니 구현 묶음

```python
from collections import deque

# 1) 리스트: 끝 append/pop은 빠르고, 앞쪽 연산은 느립니다.
arr = []
arr.append(10)
arr.append(20)
arr.pop()

# 2) 스택: list로 LIFO 구현
stack = []
stack.append('A')
stack.append('B')
stack.pop()

# 3) 큐: deque로 FIFO 구현
queue = deque()
queue.append('job-1')
queue.append('job-2')
queue.popleft()

# 4) 트리 노드
class Node:
    def __init__(self, key, left=None, right=None):
        self.key = key
        self.left = left
        self.right = right

# 5) 그래프 인접 리스트와 너비 우선 탐색
graph = {
    'A': ['B', 'C'],
    'B': ['D'],
    'C': ['D'],
    'D': []
}

def bfs(start):
    seen = {start}
    q = deque([start])
    order = []
    while q:
        cur = q.popleft()
        order.append(cur)
        for nxt in graph[cur]:
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return order
```

### 연산 복잡도 비교표

| 구조 | 핵심 연산 | 평균 시간 | 최악 시간 | 메모리 관찰 포인트 |
| --- | --- | --- | --- | --- |
| 동적 배열 | 인덱스 조회 | O(1) | O(1) | 연속 메모리, 캐시 친화적 |
| 동적 배열 | 중간 삽입/삭제 | O(n) | O(n) | 이동 비용이 성능 병목 |
| 스택 | push/pop | O(1) | O(1) | 한쪽 끝 연산으로 단순 |
| 큐(덱) | enqueue/dequeue | O(1) | O(1) | 양 끝 연산이 안정적 |
| 트리(균형) | 탐색/삽입/삭제 | O(log n) | O(log n) | 높이 유지가 관건 |
| 그래프 | 순회(BFS/DFS) | O(V+E) | O(V+E) | 정점/간선 수에 비례 |

### 메모리 배치 그림

```text
동적 배열
[0][1][2][3][4]  (연속 주소)
  |  |  |  |
  +-- 인덱스로 즉시 접근

연결 리스트
[값|다음] -> [값|다음] -> [값|다음]
   ^ 포인터를 따라 이동

트리
        [8]
       /   \
     [3]   [10]
     / \
   [1] [6]

그래프(인접 리스트)
A: B, C
B: D
C: D
D: (없음)
```

### 문제 연결 지도

| 유형 | 대표 문제 | 이 글의 관점으로 보는 핵심 |
| --- | --- | --- |
| 배열/투포인터 | LeetCode 1, 88, 283 | 인덱스 이동과 덮어쓰기 비용 관리 |
| 스택 | LeetCode 20, 155, 739 | 상태를 되돌릴 때 LIFO가 자연스러운가 |
| 큐/BFS | LeetCode 102, 994, 542 | 레벨 단위 확산과 최단 거리 |
| 트리 | LeetCode 104, 226, 236 | 재귀와 반복 중 호출 깊이 제어 |
| 그래프 | LeetCode 200, 207, 417 | 방문 집합 설계와 순회 순서 |

실무에서 성능 이슈가 발생하면, 먼저 연산을 위 표의 행으로 대응시켜 병목을 분류한 뒤 구현을 교체하는 순서로 접근하는 편이 안전합니다.




### 운영에서 다시 확인할 기준

트리는 계층 구조를 표현할 때 매우 직관적이지만, 재귀 깊이와 균형 유지 전략을 함께 고려해야 실서비스에서 안정적으로 동작합니다. 탐색 경로가 길어지는 상황을 대비해 최대 깊이 경보를 두고, 입력 패턴 변화에 따라 구조가 치우치지 않는지 주기적으로 진단하는 것이 좋습니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.



### 운영에서 다시 확인할 기준

트리는 계층 구조를 표현할 때 매우 직관적이지만, 재귀 깊이와 균형 유지 전략을 함께 고려해야 실서비스에서 안정적으로 동작합니다. 탐색 경로가 길어지는 상황을 대비해 최대 깊이 경보를 두고, 입력 패턴 변화에 따라 구조가 치우치지 않는지 주기적으로 진단하는 것이 좋습니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.



### 운영에서 다시 확인할 기준

트리는 계층 구조를 표현할 때 매우 직관적이지만, 재귀 깊이와 균형 유지 전략을 함께 고려해야 실서비스에서 안정적으로 동작합니다. 탐색 경로가 길어지는 상황을 대비해 최대 깊이 경보를 두고, 입력 패턴 변화에 따라 구조가 치우치지 않는지 주기적으로 진단하는 것이 좋습니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.



### 운영에서 다시 확인할 기준

트리는 계층 구조를 표현할 때 매우 직관적이지만, 재귀 깊이와 균형 유지 전략을 함께 고려해야 실서비스에서 안정적으로 동작합니다. 탐색 경로가 길어지는 상황을 대비해 최대 깊이 경보를 두고, 입력 패턴 변화에 따라 구조가 치우치지 않는지 주기적으로 진단하는 것이 좋습니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.



### 운영에서 다시 확인할 기준

트리는 계층 구조를 표현할 때 매우 직관적이지만, 재귀 깊이와 균형 유지 전략을 함께 고려해야 실서비스에서 안정적으로 동작합니다. 탐색 경로가 길어지는 상황을 대비해 최대 깊이 경보를 두고, 입력 패턴 변화에 따라 구조가 치우치지 않는지 주기적으로 진단하는 것이 좋습니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.



### 운영에서 다시 확인할 기준

트리는 계층 구조를 표현할 때 매우 직관적이지만, 재귀 깊이와 균형 유지 전략을 함께 고려해야 실서비스에서 안정적으로 동작합니다. 탐색 경로가 길어지는 상황을 대비해 최대 깊이 경보를 두고, 입력 패턴 변화에 따라 구조가 치우치지 않는지 주기적으로 진단하는 것이 좋습니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.



### 운영에서 다시 확인할 기준

트리는 계층 구조를 표현할 때 매우 직관적이지만, 재귀 깊이와 균형 유지 전략을 함께 고려해야 실서비스에서 안정적으로 동작합니다. 탐색 경로가 길어지는 상황을 대비해 최대 깊이 경보를 두고, 입력 패턴 변화에 따라 구조가 치우치지 않는지 주기적으로 진단하는 것이 좋습니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.



### 운영에서 다시 확인할 기준

트리는 계층 구조를 표현할 때 매우 직관적이지만, 재귀 깊이와 균형 유지 전략을 함께 고려해야 실서비스에서 안정적으로 동작합니다. 탐색 경로가 길어지는 상황을 대비해 최대 깊이 경보를 두고, 입력 패턴 변화에 따라 구조가 치우치지 않는지 주기적으로 진단하는 것이 좋습니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.



### 운영에서 다시 확인할 기준

트리는 계층 구조를 표현할 때 매우 직관적이지만, 재귀 깊이와 균형 유지 전략을 함께 고려해야 실서비스에서 안정적으로 동작합니다. 탐색 경로가 길어지는 상황을 대비해 최대 깊이 경보를 두고, 입력 패턴 변화에 따라 구조가 치우치지 않는지 주기적으로 진단하는 것이 좋습니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.

## 처음 질문으로 돌아가기

- **루트, 리프, 깊이, 높이 같은 트리 용어를 어떻게 정확히 구분할까요?**
  - 본문의 기준은 트리를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **일반 트리와 이진 트리는 어떤 점이 다를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **전위·중위·후위 순회는 무엇이 다르고 어디에 쓰일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Structures 101 (1/10): 자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [Data Structures 101 (2/10): 배열과 동적 배열](./02-arrays-and-dynamic-arrays.md)
- [Data Structures 101 (3/10): 연결 리스트](./03-linked-lists.md)
- [Data Structures 101 (4/10): 스택과 큐](./04-stacks-and-queues.md)
- [Data Structures 101 (5/10): 해시 테이블](./05-hash-tables.md)
- **트리 (현재 글)**
- 이진 탐색 트리 (예정)
- 힙 (예정)
- 그래프 (예정)
- 자료구조 선택 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Data Structures 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/data-structures-101/ko)

- [Open Data Structures — Binary Trees](https://opendatastructures.org/ods-python/6_Binary_Trees.html)
- [Wikipedia — Tree (data structure)](https://en.wikipedia.org/wiki/Tree_(data_structure))
- [Wikipedia — Tree Traversal](https://en.wikipedia.org/wiki/Tree_traversal)
- [Python `ast` module docs](https://docs.python.org/3/library/ast.html)

Tags: Computer Science, 자료구조, 트리, 계층 구조, 재귀, 순회
