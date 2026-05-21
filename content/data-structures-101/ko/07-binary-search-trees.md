---
series: data-structures-101
episode: 7
title: "Data Structures 101 (7/10): 이진 탐색 트리"
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
  - 이진 탐색 트리
  - BST
  - 균형 트리
  - 검색
seo_description: BST의 불변식, 평균 O(log n), 균형 트리의 필요성을 설명합니다.
last_reviewed: '2026-05-12'
---

# Data Structures 101 (7/10): 이진 탐색 트리

이 글은 Data Structures 101 시리즈의 일곱 번째 글입니다.


![Data Structures 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-101/07/07-01-bst-balanced-vs-skewed.ko.png)
*Data Structures 101 7장 흐름 개요*

## 먼저 던지는 질문

- BST의 핵심 불변식은 무엇이며 검색·삽입·삭제는 어떻게 동작할까요?
- 평균 시간 복잡도와 최악 시간 복잡도가 왜 달라질까요?
- AVL, Red-Black, B-Tree 같은 균형 트리는 왜 필요할까요?

## 왜 중요한가

BST 계열은 데이터베이스 인덱스, 파일 시스템 메타데이터, 메모리 할당기, 정렬된 데이터 조회 시스템의 기초입니다. 균형 트리에 대한 감각이 없으면 데이터베이스 인덱스도 끝까지 깊게 이해하기 어렵습니다.

> 정렬과 검색, 삽입, 삭제를 모두 O(log n)에 가깝게 동시에 제공하는 성질은 거의 BST 계열만의 강점입니다.

## 핵심 한눈에 보기

> BST는 정렬된 트리입니다. 각 노드는 왼쪽 서브트리 전체가 더 작고, 오른쪽 서브트리 전체가 더 크다는 불변식을 유지합니다. 그래서 매 단계에서 절반을 버리며 내려갈 수 있고, 이것이 평균 O(log n)의 근거입니다.

### 균형 이진 탐색 트리와 편향 트리

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| BST 불변식 | `left.key < node.key < right.key` |
| 균형 | 좌우 높이 차이가 일정 한도 안에 있는 상태 |
| 회전(rotation) | 균형 회복을 위해 부모-자식 연결을 재배치하는 연산 |
| AVL 트리 | 각 노드의 좌우 높이 차이를 1 이하로 유지하는 BST |
| Red-Black 트리 | 색 규칙으로 균형을 보장하는 대표적인 실무형 BST |

## 전후 비교

**Before — inserting into a sorted array:**

```python
import bisect

arr = []
for v in data:
    bisect.insort(arr, v)   # search O(log n) + shift O(n) → insert O(n)
```

**After — inserting into a BST:**

```python
root = None
for v in data:
    root = insert(root, v)   # average O(log n)
```

정렬을 유지하면서 동적으로 데이터를 다뤄야 한다면 BST는 배열보다 훨씬 자연스러운 선택이 됩니다. 다만 이 강점은 균형이 유지된다는 전제 위에서만 성립합니다.

## 단계별로 따라하기

### 1단계: 노드 정의와 삽입

```python
class BSTNode:
    __slots__ = ("key", "left", "right")
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None

def insert(root, key):
    if root is None:
        return BSTNode(key)
    if key < root.key:
        root.left = insert(root.left, key)
    elif key > root.key:
        root.right = insert(root.right, key)
    return root

root = None
for v in [50, 30, 70, 20, 40, 60, 80]:
    root = insert(root, v)
```

비교 결과에 따라 왼쪽 또는 오른쪽으로 내려가 빈 자리를 찾습니다. BST 불변식은 이 단순한 분기 로직으로 유지됩니다.

### 2단계: 검색

```python
def search(root, key):
    while root is not None:
        if key == root.key:
            return True
        root = root.left if key < root.key else root.right
    return False

print(search(root, 40))   # True
print(search(root, 99))   # False
```

매 단계마다 남은 트리의 절반을 버립니다. 균형이 잡혀 있다면 이 과정은 O(log n)입니다.

### 3단계: 중위 순회는 항상 정렬된다

```python
def inorder(node):
    if node is None:
        return
    inorder(node.left)
    print(node.key, end=" ")
    inorder(node.right)

inorder(root)   # 20 30 40 50 60 70 80
```

BST의 가장 우아한 성질입니다. 정렬된 출력이 필요할 때 별도 정렬 없이 순회만으로 해결됩니다.

### 4단계: 삭제 — 가장 까다로운 연산

```python
def find_min(node):
    while node.left is not None:
        node = node.left
    return node

def delete(root, key):
    if root is None:
        return None
    if key < root.key:
        root.left = delete(root.left, key)
    elif key > root.key:
        root.right = delete(root.right, key)
    else:
        # 자식이 0개 또는 1개
        if root.left is None:
            return root.right
        if root.right is None:
            return root.left
        # 자식이 2개: in-order successor로 교체
        successor = find_min(root.right)
        root.key = successor.key
        root.right = delete(root.right, successor.key)
    return root

root = delete(root, 30)
inorder(root)   # 20 40 50 60 70 80
```

삭제는 자식 수에 따라 세 경우로 갈립니다. 특히 자식이 둘인 경우 중위 후속자(successor)를 이용하는 분기가 가장 중요합니다.

### 5단계: 균형이 무너지면 생기는 비극

```python
from random import Random

def build_bst(values):
    root = None
    for value in values:
        root = insert(root, value)
    return root

def tree_height(node):
    if node is None:
        return -1
    return 1 + max(tree_height(node.left), tree_height(node.right))

def search_steps(root, key):
    steps = 0
    while root is not None:
        steps += 1
        if key == root.key:
            return steps
        root = root.left if key < root.key else root.right
    return steps

values = list(range(31))
shuffled_values = values[:]
Random(42).shuffle(shuffled_values)

skewed = build_bst(values)
less_skewed = build_bst(shuffled_values)
target = values[-1]

skewed_height = tree_height(skewed)
less_skewed_height = tree_height(less_skewed)
skewed_steps = search_steps(skewed, target)
less_skewed_steps = search_steps(less_skewed, target)

print({
    "skewed_height": skewed_height,
    "shuffled_height": less_skewed_height,
    "skewed_steps": skewed_steps,
    "shuffled_steps": less_skewed_steps,
})

shape_check = (
    skewed_height == len(values) - 1
    and less_skewed_height < skewed_height
    and less_skewed_steps < skewed_steps
)
print(f"shape check passed: {shape_check}")

# Expected shape:
# {'skewed_height': 30, 'shuffled_height': <훨씬 더 작음>, 'skewed_steps': 31, 'shuffled_steps': <더 작음>}
# shape 검증 통과: True
```

정렬된 입력을 그대로 넣으면 BST는 사실상 연결 리스트로 퇴화합니다. 위 검증은 시간을 재는 대신 트리 높이와 탐색 단계 수를 직접 확인합니다. 기대한 격차가 보이지 않으면 셔플이 잘못되었거나, 균형화 로직이 섞였거나, 단계 수 계산이 틀렸을 가능성이 큽니다.

## 이 코드에서 주목할 점

- BST 불변식은 단순하지만 강력합니다.
- 삭제는 특히 자식 둘인 경우가 가장 까다롭습니다.
- 균형이 깨진 BST는 최악 O(n)이므로 실무에서는 균형 변종을 씁니다.
- 중위 순회가 정렬 결과를 준다는 점이 BST의 핵심 장점입니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| BST는 항상 O(log n)이라고 가정함 | 정렬 입력에서 O(n)으로 붕괴 | 균형 트리를 사용합니다 |
| 중복 키 정책을 정하지 않음 | 무한 루프나 데이터 손실 발생 | 중복 처리 규칙을 명시합니다 |
| 삭제에서 후속자 처리를 빼먹음 | 트리 불변식이 깨짐 | 자식 둘인 경우를 분리합니다 |
| dict 대신 무조건 BST를 고름 | 더 느리고 복잡해질 수 있음 | 정렬 순회가 필요할 때만 선택합니다 |
| 깊은 BST에 재귀만 사용함 | `RecursionError` 발생 가능 | 반복 또는 명시적 스택을 검토합니다 |

## 실무에서는 이렇게 쓰입니다

- 데이터베이스 인덱스의 B-tree, B+tree는 BST를 디스크 친화적으로 일반화한 구조입니다.
- Java의 `TreeMap`, C++의 `std::map`은 Red-Black 트리입니다.
- 파이썬에서는 보통 `sortedcontainers.SortedDict` 같은 라이브러리를 선택합니다.
- 운영체제의 가상 메모리 관리자와 스케줄러도 균형 트리 계열을 사용합니다.
- IP 라우팅 테이블은 longest-prefix 매칭을 위해 trie 같은 관련 구조를 씁니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 트리를 처음부터 직접 구현하지 않습니다. 표준 라이브러리나 검증된 라이브러리를 쓰는 편이 안전합니다. 하지만 그 라이브러리가 내부에서 무엇을 하는지는 정확히 이해하고 있어야, 한계를 예측하고 장애를 디버깅할 수 있습니다.

또한 먼저 “정렬 순서가 정말 필요한가”를 묻습니다. 정렬 순회나 범위 질의가 필요 없다면 dict가 거의 항상 더 단순하고 빠릅니다. BST는 정렬 의미를 얻기 위해 치르는 비용입니다.

## 체크리스트

- [ ] BST 불변식을 정확히 말할 수 있습니다
- [ ] 평균과 최악 시간 복잡도가 왜 갈리는지 설명할 수 있습니다
- [ ] BST 삭제의 세 가지 경우를 알고 있습니다
- [ ] 균형 트리가 왜 필요한지 이해했습니다
- [ ] BST와 dict 중 무엇을 고를지 기준을 가지고 있습니다

## 연습 문제

1. BST에서 k번째로 작은 값을 반환하는 메서드를 추가해 보세요. 먼저 O(n) 해법을 만들고, 각 노드에 서브트리 크기를 저장해 O(log n)으로 개선하는 버전도 시도해 보세요.

2. 두 BST가 같은 키 집합을 담고 있는지 판별하는 함수를 작성해 보세요. 트리 모양은 달라도 됩니다.

3. AVL의 네 가지 회전(LL, LR, RR, RL)을 직접 그려 보고, 각각이 어떤 상황에서 적용되는지 정리해 보세요.

## 정리 및 다음 단계

이진 탐색 트리는 단 하나의 불변식으로 평균 O(log n) 검색·삽입·삭제를 제공합니다. 하지만 입력에 따라 균형이 무너지면 최악 O(n)으로 떨어지므로, 실무에서는 AVL이나 Red-Black 같은 자기 균형 트리를 사용합니다. 중위 순회가 항상 정렬 결과를 준다는 성질은 정렬된 데이터를 동적으로 관리해야 하는 시스템의 핵심 기반이 됩니다.

다음 글에서는 최솟값 또는 최댓값을 빠르게 다루는 데 특화된 힙을 봅니다. BST보다 단순하지만 우선순위 처리에는 훨씬 직접적인 구조입니다.


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

이진 탐색 트리는 정렬성과 탐색 효율을 동시에 제공하지만, 입력 순서가 편향되면 사실상 연결 리스트처럼 동작할 수 있습니다. 따라서 균형 전략을 포함한 구현을 기본값으로 두고, 순회 결과와 높이 통계를 함께 기록해 편향을 빠르게 감지해야 합니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

이진 탐색 트리는 정렬성과 탐색 효율을 동시에 제공하지만, 입력 순서가 편향되면 사실상 연결 리스트처럼 동작할 수 있습니다. 따라서 균형 전략을 포함한 구현을 기본값으로 두고, 순회 결과와 높이 통계를 함께 기록해 편향을 빠르게 감지해야 합니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

이진 탐색 트리는 정렬성과 탐색 효율을 동시에 제공하지만, 입력 순서가 편향되면 사실상 연결 리스트처럼 동작할 수 있습니다. 따라서 균형 전략을 포함한 구현을 기본값으로 두고, 순회 결과와 높이 통계를 함께 기록해 편향을 빠르게 감지해야 합니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

이진 탐색 트리는 정렬성과 탐색 효율을 동시에 제공하지만, 입력 순서가 편향되면 사실상 연결 리스트처럼 동작할 수 있습니다. 따라서 균형 전략을 포함한 구현을 기본값으로 두고, 순회 결과와 높이 통계를 함께 기록해 편향을 빠르게 감지해야 합니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

이진 탐색 트리는 정렬성과 탐색 효율을 동시에 제공하지만, 입력 순서가 편향되면 사실상 연결 리스트처럼 동작할 수 있습니다. 따라서 균형 전략을 포함한 구현을 기본값으로 두고, 순회 결과와 높이 통계를 함께 기록해 편향을 빠르게 감지해야 합니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

이진 탐색 트리는 정렬성과 탐색 효율을 동시에 제공하지만, 입력 순서가 편향되면 사실상 연결 리스트처럼 동작할 수 있습니다. 따라서 균형 전략을 포함한 구현을 기본값으로 두고, 순회 결과와 높이 통계를 함께 기록해 편향을 빠르게 감지해야 합니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

이진 탐색 트리는 정렬성과 탐색 효율을 동시에 제공하지만, 입력 순서가 편향되면 사실상 연결 리스트처럼 동작할 수 있습니다. 따라서 균형 전략을 포함한 구현을 기본값으로 두고, 순회 결과와 높이 통계를 함께 기록해 편향을 빠르게 감지해야 합니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

이진 탐색 트리는 정렬성과 탐색 효율을 동시에 제공하지만, 입력 순서가 편향되면 사실상 연결 리스트처럼 동작할 수 있습니다. 따라서 균형 전략을 포함한 구현을 기본값으로 두고, 순회 결과와 높이 통계를 함께 기록해 편향을 빠르게 감지해야 합니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.

## 처음 질문으로 돌아가기

- **BST의 핵심 불변식은 무엇이며 검색·삽입·삭제는 어떻게 동작할까요?**
  - 본문의 기준은 이진 탐색 트리를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **평균 시간 복잡도와 최악 시간 복잡도가 왜 달라질까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **AVL, Red-Black, B-Tree 같은 균형 트리는 왜 필요할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Structures 101 (1/10): 자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [Data Structures 101 (2/10): 배열과 동적 배열](./02-arrays-and-dynamic-arrays.md)
- [Data Structures 101 (3/10): 연결 리스트](./03-linked-lists.md)
- [Data Structures 101 (4/10): 스택과 큐](./04-stacks-and-queues.md)
- [Data Structures 101 (5/10): 해시 테이블](./05-hash-tables.md)
- [Data Structures 101 (6/10): 트리](./06-trees.md)
- **이진 탐색 트리 (현재 글)**
- 힙 (예정)
- 그래프 (예정)
- 자료구조 선택 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Data Structures 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/data-structures-101/ko)

- [Open Data Structures — Binary Search Trees](https://opendatastructures.org/ods-python/6_2_BinarySearchTree_Unbala.html)
- [Wikipedia — Binary Search Tree](https://en.wikipedia.org/wiki/Binary_search_tree)
- [Wikipedia — Red-Black Tree](https://en.wikipedia.org/wiki/Red%E2%80%93black_tree)
- [sortedcontainers documentation](https://grantjenks.com/docs/sortedcontainers/)

Tags: Computer Science, 자료구조, 이진 탐색 트리, BST, 균형 트리, 검색
