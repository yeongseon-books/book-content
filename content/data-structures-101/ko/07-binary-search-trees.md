---
series: data-structures-101
episode: 7
title: 이진 탐색 트리
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
  - 이진 탐색 트리
  - BST
  - 균형 트리
  - 검색
seo_description: 이진 탐색 트리의 동작 원리, 평균 O(log n)과 최악 O(n)의 차이, 그리고 균형 트리가 필요한 이유를 살펴봅니다.
last_reviewed: '2026-05-04'
---

# 이진 탐색 트리

> Data Structures 101 시리즈 (7/10)


## 이 글에서 다룰 문제

BST는 데이터베이스 인덱스, 파일 시스템 메타데이터, 메모리 할당기 등 정렬된 데이터의 빠른 검색이 필요한 곳에서 핵심 역할을 합니다. 균형 트리에 대한 직관 없이 데이터베이스 인덱스를 깊이 이해하기 어렵습니다.

> 정렬 + 검색 + 삽입 + 삭제 = O(log n)을 모두 만족하는 거의 유일한 자료구조 패밀리.

## 전체 흐름
> BST는 "정렬된 트리"입니다. 어떤 노드의 왼쪽 서브트리는 모두 그보다 작고, 오른쪽 서브트리는 모두 그보다 크다는 불변식을 유지합니다. 이 불변식 덕분에 매 단계마다 절반을 버릴 수 있어 평균 O(log n) 검색이 가능합니다.

```text
균형 BST (높이 2)              비균형 BST (높이 4)
        50                          10
       /  \                          \
      30   70                        20
     / \   / \                        \
    20 40 60 80                       30
                                       \
                                       40
                                        \
                                        50
검색 O(log n)                  검색 O(n)
```

## Before / After

**Before — 정렬 배열에 삽입:**

```python
import bisect

arr = []
for v in data:
    bisect.insort(arr, v)   # 검색 O(log n) + 이동 O(n) → 삽입 O(n)
```

**After — BST에 삽입:**

```python
root = None
for v in data:
    root = insert(root, v)   # 평균 O(log n)
```

## 단계별로 따라하기

### 1단계: BST 노드 정의와 삽입

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

비교 결과에 따라 왼쪽/오른쪽으로 내려가며 빈 자리를 찾아 삽입합니다.

### 2단계: BST 검색

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

매 단계에서 절반을 버립니다. 균형 트리라면 O(log n).

### 3단계: 중위 순회 = 정렬된 출력

```python
def inorder(node):
    if node is None:
        return
    inorder(node.left)
    print(node.key, end=" ")
    inorder(node.right)


inorder(root)   # 20 30 40 50 60 70 80
```

BST의 중위 순회는 항상 정렬된 결과를 줍니다. BST의 가장 우아한 성질입니다.

### 4단계: 삭제 (가장 까다로운 연산)

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
        # 자식이 0 또는 1개
        if root.left is None:
            return root.right
        if root.right is None:
            return root.left
        # 자식이 2개: 오른쪽 서브트리의 최솟값으로 대체
        successor = find_min(root.right)
        root.key = successor.key
        root.right = delete(root.right, successor.key)
    return root


root = delete(root, 30)
inorder(root)   # 20 40 50 60 70 80
```

삭제는 자식 수에 따라 세 가지 케이스로 나뉘며, 그중 자식이 둘인 경우가 가장 까다롭습니다.

### 5단계: 비균형 BST의 비극

```python
# 정렬된 입력으로 BST를 만들면 한쪽으로 기울어진다
import time

skewed = None
for v in range(10_000):
    skewed = insert(skewed, v)

start = time.perf_counter()
search(skewed, 9999)
print(f"기운 BST 검색: {(time.perf_counter() - start) * 1e6:.0f} µs")

# 셔플하면 균형이 자연스럽게 잡힌다
import random

values = list(range(10_000))
random.shuffle(values)

balanced = None
for v in values:
    balanced = insert(balanced, v)

start = time.perf_counter()
search(balanced, 9999)
print(f"균형 BST 검색: {(time.perf_counter() - start) * 1e6:.0f} µs")
```

정렬된 데이터를 그대로 넣으면 BST가 사실상 연결 리스트가 됩니다. 이 한계가 균형 트리(AVL, Red-Black)의 등장 배경입니다.

## 이 코드에서 주목할 점

- BST 불변식은 단순하지만 강력한 검색 성능을 만들어냅니다
- 삭제는 자식이 둘인 경우가 가장 까다로우며 후계자(successor)를 사용합니다
- 비균형 BST는 최악 O(n)이라 실무에서는 균형 트리를 사용합니다
- 중위 순회는 항상 정렬된 결과를 보장합니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| BST를 항상 O(log n)으로 가정 | 정렬 입력에서 O(n) | 균형 트리 사용 |
| 중복 키 처리 누락 | 무한 루프 또는 데이터 손실 | 중복 정책 명시 |
| 삭제에서 후계자 누락 | 트리 깨짐 | 자식 2개 케이스 정확히 처리 |
| dict 대신 BST 남용 | 더 느리고 복잡 | 정렬 순회가 필요 없으면 dict |
| 깊은 BST에서 재귀 사용 | RecursionError | 반복 또는 명시적 스택 |

## 실무에서는 이렇게 쓰입니다

- 데이터베이스 인덱스의 B-Tree/B+Tree는 BST의 디스크 친화적 일반화
- 자바의 `TreeMap`, C++의 `std::map`은 Red-Black 트리로 구현
- 파이썬에서는 `sortedcontainers.SortedDict`로 BST 의미를 사용
- 운영체제의 가상 메모리 관리, 프로세스 스케줄러도 균형 트리를 활용
- IP 라우팅 테이블의 longest prefix match는 트라이(Trie)라는 변형을 사용

## 체크리스트

- [ ] BST 불변식을 정확히 말할 수 있는가
- [ ] BST의 평균과 최악 시간 복잡도가 왜 다른지 설명할 수 있는가
- [ ] BST 삭제의 세 가지 케이스를 알고 있는가
- [ ] 균형 트리가 필요한 이유를 이해했는가
- [ ] BST와 dict 중 어느 것을 선택할지 기준을 갖고 있는가

## 정리 및 다음 단계

이진 탐색 트리는 단순한 불변식 하나로 검색·삽입·삭제 평균 O(log n)을 달성하는 자료구조입니다. 그러나 입력에 따라 균형이 무너지면 최악 O(n)이 되므로 실무에서는 AVL, Red-Black 같은 자기 균형 트리를 사용합니다. BST의 가장 우아한 성질은 중위 순회가 항상 정렬된 결과를 준다는 점입니다. 정렬된 데이터의 동적 관리가 필요한 모든 시스템의 기반이 됩니다.

다음 글에서는 "최댓값/최솟값에 빠르게 접근"하는 데 특화된 자료구조인 힙을 살펴봅니다. 우선순위 큐의 표준 구현이며, BST보다 단순하지만 더 좁은 용도에 최적화되어 있습니다.

<!-- toc:begin -->
- [자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [배열과 동적 배열](./02-arrays-and-dynamic-arrays.md)
- [연결 리스트](./03-linked-lists.md)
- [스택과 큐](./04-stacks-and-queues.md)
- [해시 테이블](./05-hash-tables.md)
- [트리](./06-trees.md)
- **이진 탐색 트리 (현재 글)**
- 힙 (예정)
- 그래프 (예정)
- 자료구조 선택 기준 (예정)
<!-- toc:end -->

## 참고 자료

- [Open Data Structures — Binary Search Trees](https://opendatastructures.org/ods-python/6_2_BinarySearchTree_Unbala.html)
- [Wikipedia — Binary Search Tree](https://en.wikipedia.org/wiki/Binary_search_tree)
- [Wikipedia — Red-Black Tree](https://en.wikipedia.org/wiki/Red%E2%80%93black_tree)
- [sortedcontainers documentation](https://grantjenks.com/docs/sortedcontainers/)

Tags: Computer Science, 자료구조, 이진 탐색 트리, BST, 균형 트리, 검색
