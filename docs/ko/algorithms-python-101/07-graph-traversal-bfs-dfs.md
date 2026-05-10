---
series: algorithms-python-101
episode: 7
title: 그래프 탐색 — BFS와 DFS
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
  - 알고리즘
  - 그래프
  - BFS
  - DFS
seo_description: Python으로 그래프를 표현하고 BFS와 DFS를 구현합니다.
last_reviewed: '2026-05-04'
---

# 그래프 탐색 — BFS와 DFS

> Algorithms with Python 101 시리즈 (7/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 네트워크에서 두 지점이 연결되어 있는지 어떻게 확인할까요?

> 그래프는 노드(정점)와 간선(엣지)으로 이루어진 자료구조이며, BFS와 DFS는 그래프의 모든 노드를 체계적으로 방문하는 두 가지 전략입니다. 이 글에서는 그래프를 Python으로 표현하고, BFS와 DFS를 구현합니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 그래프의 기본 개념과 Python 표현 방법
- BFS(너비 우선 탐색)의 원리와 구현
- DFS(깊이 우선 탐색)의 원리와 구현
- BFS와 DFS의 활용 차이

## 왜 중요한가

소셜 네트워크, 지도, 웹 페이지 링크, 의존성 관리 등 현실 세계의 수많은 관계가 그래프로 모델링됩니다. BFS와 DFS는 이 그래프를 탐색하는 가장 기본적인 알고리즘입니다.

> BFS = 가까운 노드부터 층별로 탐색, DFS = 한 경로를 끝까지 탐색한 후 되돌아감

BFS는 최단 경로 문제에, DFS는 경로 존재 여부, 사이클 탐지, 위상 정렬에 주로 사용됩니다.

## 핵심 개념 잡기

> 그래프 = 노드(정점)와 간선(엣지)의 집합

```
그래프 예시:      BFS 탐색 순서:        DFS 탐색 순서:
  A—B             A(0층)                A → B → D → E → C → F
  |\ \            B, C(1층)
  | C  D          D, E, F(2층)
  |/ \
  E   F
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 정점(vertex, node) | 그래프의 개별 요소입니다 |
| 간선(edge) | 두 정점을 연결하는 선입니다 |
| 인접 리스트(adjacency list) | 각 정점의 이웃 목록으로 그래프를 표현하는 방법입니다 |
| BFS(Breadth-First Search) | 큐를 사용하여 가까운 노드부터 탐색하는 방법입니다 |
| DFS(Depth-First Search) | 스택(또는 재귀)을 사용하여 깊이 우선으로 탐색하는 방법입니다 |

## Before / After

그래프에서 두 노드의 연결 여부를 확인하는 두 가지 방법을 비교합니다.

```python
# before: 모든 경로를 무작위 탐색 — 비효율적
def is_connected(graph, start, end):
    # 체계적이지 않아 무한 루프 위험
    pass
```

```python
# after: BFS로 체계적 탐색 — O(V+E)
from collections import deque

def is_connected(graph, start, end):
    visited = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node == end:
            return True
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return False
```

## 단계별 실습

### Step 1: 그래프 표현

```python
# 인접 리스트 — 딕셔너리로 표현
graph: dict[str, list[str]] = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A", "E", "F"],
    "D": ["B"],
    "E": ["C"],
    "F": ["C"],
}

# 방향 그래프 (간선에 방향이 있는 경우)
directed_graph: dict[str, list[str]] = {
    "A": ["B", "C"],
    "B": ["D"],
    "C": ["E"],
    "D": [],
    "E": [],
}

# 가중 그래프 (간선에 가중치가 있는 경우)
weighted_graph: dict[str, list[tuple[str, int]]] = {
    "A": [("B", 4), ("C", 2)],
    "B": [("A", 4), ("D", 3)],
    "C": [("A", 2), ("E", 1)],
    "D": [("B", 3)],
    "E": [("C", 1)],
}
```

### Step 2: BFS 구현

```python
from collections import deque


def bfs(graph: dict[str, list[str]], start: str) -> list[str]:
    """BFS — O(V+E), 큐 사용"""
    visited = {start}
    queue = deque([start])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return order

print(bfs(graph, "A"))  # ['A', 'B', 'C', 'D', 'E', 'F']
```

### Step 3: DFS 구현 (재귀와 반복)

```python
def dfs_recursive(
    graph: dict[str, list[str]],
    node: str,
    visited: set[str] | None = None,
) -> list[str]:
    """DFS 재귀 — O(V+E)"""
    if visited is None:
        visited = set()
    visited.add(node)
    order = [node]
    for neighbor in graph[node]:
        if neighbor not in visited:
            order.extend(dfs_recursive(graph, neighbor, visited))
    return order

print(dfs_recursive(graph, "A"))  # ['A', 'B', 'D', 'C', 'E', 'F']


def dfs_iterative(graph: dict[str, list[str]], start: str) -> list[str]:
    """DFS 반복 — O(V+E), 스택 사용"""
    visited = set()
    stack = [start]
    order = []

    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        for neighbor in reversed(graph[node]):
            if neighbor not in visited:
                stack.append(neighbor)

    return order

print(dfs_iterative(graph, "A"))  # ['A', 'B', 'D', 'C', 'E', 'F']
```

### Step 4: BFS로 최단 경로 찾기

```python
from collections import deque


def bfs_shortest_path(
    graph: dict[str, list[str]], start: str, end: str
) -> list[str] | None:
    """BFS 최단 경로 — 가중치 없는 그래프"""
    if start == end:
        return [start]

    visited = {start}
    queue: deque[list[str]] = deque([[start]])

    while queue:
        path = queue.popleft()
        node = path[-1]
        for neighbor in graph[node]:
            if neighbor == end:
                return path + [neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])

    return None

print(bfs_shortest_path(graph, "A", "F"))  # ['A', 'C', 'F']
print(bfs_shortest_path(graph, "D", "E"))  # ['D', 'B', 'A', 'C', 'E']
```

### Step 5: 연결 요소와 사이클 탐지

```python
def find_connected_components(
    graph: dict[str, list[str]],
) -> list[list[str]]:
    """모든 연결 요소 찾기"""
    visited: set[str] = set()
    components: list[list[str]] = []

    for node in graph:
        if node not in visited:
            component = bfs(graph, node)
            visited.update(component)
            components.append(component)

    return components

# 두 개의 연결 요소를 가진 그래프
split_graph: dict[str, list[str]] = {
    "A": ["B"], "B": ["A"],
    "C": ["D"], "D": ["C"],
}
print(find_connected_components(split_graph))
# [['A', 'B'], ['C', 'D']]


def has_cycle(graph: dict[str, list[str]], start: str) -> bool:
    """무방향 그래프의 사이클 탐지 — DFS"""
    visited: set[str] = set()

    def _dfs(node: str, parent: str | None) -> bool:
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                if _dfs(neighbor, node):
                    return True
            elif neighbor != parent:
                return True
        return False

    return _dfs(start, None)

print(has_cycle(graph, "A"))  # True (A-B-A 또는 A-C-A)
```

## 이 코드에서 주목할 점

- BFS는 큐(deque)를 사용하고, DFS는 스택(또는 재귀)을 사용합니다
- BFS는 최단 경로를 보장하지만 DFS는 보장하지 않습니다
- visited 집합으로 이미 방문한 노드를 추적하여 무한 루프를 방지합니다
- 사이클 탐지에서 부모 노드를 추적하여 거짓 양성을 방지합니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| visited 체크 누락 | 무한 루프에 빠집니다 | 방문 전에 항상 visited를 확인합니다 |
| BFS에서 리스트를 큐로 사용 | list.pop(0)은 O(n)입니다 | collections.deque를 사용합니다 |
| DFS 재귀 깊이 초과 | 큰 그래프에서 RecursionError입니다 | 반복 DFS를 사용합니다 |
| 방향/무방향 혼동 | 탐색 결과가 달라집니다 | 그래프 유형을 명확히 합니다 |
| 연결되지 않은 노드 누락 | 일부 노드를 탐색하지 못합니다 | 모든 노드에서 탐색을 시작합니다 |

## 실무에서 이렇게 쓰입니다

- 소셜 네트워크에서 "친구의 친구" 추천에 BFS를 사용합니다
- 웹 크롤러가 BFS로 페이지를 순회합니다
- 패키지 의존성 해결에 DFS 기반 위상 정렬을 사용합니다
- 미로 찾기, 게임 AI에서 경로 탐색을 합니다
- 네트워크 토폴로지 분석에 그래프 탐색을 활용합니다

## 현업 개발자는 이렇게 생각합니다

BFS와 DFS는 그래프 알고리즘의 기본 빌딩 블록입니다. 이 두 알고리즘을 제대로 이해하면 다익스트라, 위상 정렬, 최소 신장 트리 등 고급 알고리즘도 자연스럽게 이해됩니다.

실무에서는 NetworkX 같은 라이브러리를 사용하지만, BFS/DFS의 원리를 알아야 어떤 알고리즘을 선택할지 판단할 수 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **표현 선택** — 인접 리스트가 거의 모든 경우 우월합니다.
- **Visited 관리** — 재방문 방지는 정합성·성능 모두에 결정적입니다.
- **BFS 단축거리** — 가중치가 동일할 때만 BFS가 최단거리를 보장합니다.
- **재귀 DFS 위험** — 깊은 그래프는 명시적 스택을 씁니다.
- **관측** — 탐색 경로 로깅이 디버깅을 가장 빠르게 만듭니다.

## 체크리스트

- [ ] 인접 리스트로 그래프를 표현할 수 있다
- [ ] BFS와 DFS의 차이점을 설명할 수 있다
- [ ] BFS로 최단 경로를 구할 수 있다
- [ ] DFS로 사이클을 탐지할 수 있다
- [ ] 연결 요소를 구하는 알고리즘을 작성할 수 있다

## 연습 문제

1. BFS로 미로의 최단 경로를 찾는 함수를 작성하세요 (2차원 격자).
2. DFS로 방향 그래프의 위상 정렬을 구현하세요.
3. 주어진 그래프가 이분 그래프인지 BFS로 판별하세요.

## 정리 및 다음 글 안내

BFS는 가까운 노드부터 탐색하고 최단 경로를 보장합니다. DFS는 깊이 우선으로 탐색하며 사이클 탐지와 위상 정렬에 적합합니다. 다음 글에서는 가중 그래프에서 최단 경로를 구하는 다익스트라 알고리즘을 다룹니다.

<!-- toc:begin -->
- [알고리즘이란 무엇인가?](./01-what-are-algorithms.md)
- [시간 복잡도와 Big-O](./02-time-complexity-and-big-o.md)
- [선형 탐색과 이진 탐색](./03-linear-and-binary-search.md)
- [정렬 알고리즘](./04-sorting-algorithms.md)
- [재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- [동적 계획법 기초](./06-dynamic-programming-basics.md)
- **그래프 탐색 — BFS와 DFS (현재 글)**
- 최단 경로 기초 (예정)
- 그리디 알고리즘 (예정)
- 코딩 테스트 문제 접근법 (예정)
<!-- toc:end -->

## 참고 자료

- [Wikipedia — Breadth-First Search](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Wikipedia — Depth-First Search](https://en.wikipedia.org/wiki/Depth-first_search)
- [Real Python — Graphs in Python](https://realpython.com/python-graph/)
- [Visualgo — Graph Traversal](https://visualgo.net/en/dfsbfs)
