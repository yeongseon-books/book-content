---
series: algorithms-python-101
episode: 7
title: "Algorithms with Python 101 (7/10): 그래프 탐색 — BFS와 DFS"
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
  - Algorithms
  - Graphs
  - BFS
  - DFS
seo_description: 그래프 표현과 BFS, DFS의 핵심 활용법을 Python으로 익힙니다.
last_reviewed: '2026-05-12'
---

# Algorithms with Python 101 (7/10): 그래프 탐색 — BFS와 DFS

네트워크, 지도, 의존성 트리, 추천 시스템은 모두 결국 노드와 연결 관계의 문제로 환원됩니다. 배열과 리스트를 지나면 그래프 사고가 자주 등장하는 이유가 여기에 있습니다.

이 글은 Algorithms with Python 101 시리즈의 일곱 번째 글입니다. 여기서는 Python으로 그래프를 표현하고, BFS와 DFS를 실용적인 관점에서 구현해 보겠습니다.

BFS와 DFS는 그래프 탐색의 두 기초 전략입니다. 둘의 차이를 분명히 이해하면 최단 경로, 사이클 검사, 연결 요소 문제를 훨씬 쉽게 다룰 수 있습니다.

![Algorithms with Python 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-python-101/07/07-01-concept-overview.ko.png)
*Algorithms with Python 101 7장 흐름 개요*

## 이 글에서 다룰 문제

- 그래프의 기본 개념과 Python에서의 표현 방식은 무엇일까요?
- BFS는 어떤 원리로 동작하고 언제 써야 할까요?
- DFS는 어떤 원리로 동작하고 언제 써야 할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

> BFS는 가까운 이웃을 층별로 탐색하고, DFS는 한 경로를 가능한 깊게 내려간 뒤 되돌아옵니다.

## 개념 한눈에 보기

> 그래프는 노드(vertex)와 간선(edge)의 집합입니다

```text
Example graph:     BFS order:               DFS order:
  A—B               A (layer 0)             A → B → D → C → E → F
  |\ \              B, C (layer 1)
  | C  D            D, E, F (layer 2)
  |/ \
  E   F
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| Vertex (node) | 그래프를 이루는 개별 요소입니다 |
| Edge | 두 노드를 잇는 연결입니다 |
| Adjacency list | 각 노드와 이웃 노드 목록을 매핑하는 표현 방식입니다 |
| BFS (Breadth-First Search) | 큐를 사용해 가까운 노드부터 방문합니다 |
| DFS (Depth-First Search) | 스택 또는 재귀를 사용해 가능한 깊게 방문합니다 |

## BFS vs DFS 선택 기준

| 질문 | BFS | DFS |
|------|-----|-----|
| 최단 거리(홉 수)가 필요한가? | 적합 | 부적합 |
| 경로 존재 여부만 확인하나? | 가능 | 적합 |
| 사이클 탐지가 필요한가? | 가능 | 적합 |
| 위상 정렬이 필요한가? | 불가 | 적합 |
| 그래프가 매우 깊은가? | 안전 | 스택 주의 |

## 적용 전후 비교

두 노드가 연결되어 있는지 확인하는 두 가지 접근입니다.

```python
# before: ad-hoc 순회 — visited 없이 무한 루프 위험
def is_connected_wrong(graph, start, end):
    # visited 집합 없이 구현하면 사이클에서 무한 루프
    queue = [start]
    while queue:
        node = queue.pop(0)
        if node == end:
            return True
        queue.extend(graph[node])  # 무한 루프!
    return False
```

```python
# after: BFS — 체계적인 O(V+E) 순회
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

### 단계 1: 그래프 표현

```python
# dictionary를 사용하는 Adjacency list
graph: dict[str, list[str]] = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A", "E", "F"],
    "D": ["B"],
    "E": ["C"],
    "F": ["C"],
}

# 방향 그래프
directed_graph: dict[str, list[str]] = {
    "A": ["B", "C"],
    "B": ["D"],
    "C": ["E"],
    "D": [],
    "E": [],
}

# 가중 그래프
weighted_graph: dict[str, list[tuple[str, int]]] = {
    "A": [("B", 4), ("C", 2)],
    "B": [("A", 4), ("D", 3)],
    "C": [("A", 2), ("E", 1)],
    "D": [("B", 3)],
    "E": [("C", 1)],
}
```

### 단계 2: BFS 구현

```python
from collections import deque

def bfs(graph: dict[str, list[str]], start: str) -> list[str]:
    """BFS — O(V+E), uses a queue."""
    visited = {start}
    queue = deque([start])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)  # 큐에 넣을 때 방문 처리!
                queue.append(neighbor)

    return order

print(bfs(graph, "A"))  # ['A', 'B', 'C', 'D', 'E', 'F']
```

방문 처리를 `popleft()` 시점이 아닌 `append()` 시점에 해야 중복 방문을 막을 수 있습니다.

### 단계 3: DFS 구현 (재귀와 반복)

```python
def dfs_recursive(
    graph: dict[str, list[str]],
    node: str,
    visited: set[str] | None = None,
) -> list[str]:
    """DFS recursive — O(V+E)."""
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
    """DFS iterative — O(V+E), uses a stack."""
    visited: set[str] = set()
    stack = [start]
    order: list[str] = []

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

### 단계 4: BFS 최단 경로

```python
from collections import deque

def bfs_shortest_path(
    graph: dict[str, list[str]], start: str, end: str
) -> list[str] | None:
    """BFS shortest path — unweighted graph."""
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

### 단계 5: 연결 요소와 사이클 탐지

```python
def find_connected_components(
    graph: dict[str, list[str]],
) -> list[list[str]]:
    """Find all connected components."""
    visited: set[str] = set()
    components: list[list[str]] = []

    for node in graph:
        if node not in visited:
            component = bfs(graph, node)
            visited.update(component)
            components.append(component)

    return components

split_graph: dict[str, list[str]] = {
    "A": ["B"], "B": ["A"],
    "C": ["D"], "D": ["C"],
}
print(find_connected_components(split_graph))
# [['A', 'B'], ['C', 'D']]

def has_cycle(graph: dict[str, list[str]], start: str) -> bool:
    """무방향 그래프 사이클 탐지 — DFS + 부모 추적."""
    visited: set[str] = set()

    def _dfs(node: str, parent: str | None) -> bool:
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                if _dfs(neighbor, node):
                    return True
            elif neighbor != parent:  # 부모 제외하고 방문된 노드 = 사이클
                return True
        return False

    return _dfs(start, None)

print(has_cycle(graph, "A"))  # True
```

## 단계별 실행 추적 — BFS

`bfs(graph, "A")` 실행 추적:

```text
그래프: A-[B,C], B-[A,D], C-[A,E,F], D-[B], E-[C], F-[C]

초기: visited={'A'}, queue=deque(['A']), order=[]

Step 1: pop 'A'
  order=['A']
  이웃 B: not in visited → visited.add('B'), queue=['B']
  이웃 C: not in visited → visited.add('C'), queue=['B','C']

Step 2: pop 'B'
  order=['A','B']
  이웃 A: in visited → skip
  이웃 D: not in visited → visited.add('D'), queue=['C','D']

Step 3: pop 'C'
  order=['A','B','C']
  이웃 A: in visited → skip
  이웃 E: not in visited → queue=['D','E']
  이웃 F: not in visited → queue=['D','E','F']

Step 4: pop 'D' → order=['A','B','C','D']
Step 5: pop 'E' → order=['A','B','C','D','E']
Step 6: pop 'F' → order=['A','B','C','D','E','F']

결과: ['A', 'B', 'C', 'D', 'E', 'F'] (층별 탐색)
```

## 코딩 테스트 풀이 예시

**문제**: 2차원 격자에서 '1'로 이루어진 섬의 개수를 찾아라.

```python
from collections import deque

def num_islands(grid: list[list[str]]) -> int:
    """
    BFS로 섬의 개수를 셉니다.
    '1'=땅, '0'=물
    시간 복잡도: O(rows * cols)
    """
    if not grid:
        return 0

    rows, cols = len(grid), len(grid[0])
    visited = set()
    count = 0

    def bfs_island(r: int, c: int) -> None:
        queue = deque([(r, c)])
        visited.add((r, c))
        while queue:
            row, col = queue.popleft()
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = row + dr, col + dc
                if (0 <= nr < rows and 0 <= nc < cols
                        and grid[nr][nc] == "1"
                        and (nr, nc) not in visited):
                    visited.add((nr, nc))
                    queue.append((nr, nc))

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1" and (r, c) not in visited:
                bfs_island(r, c)
                count += 1

    return count


grid1 = [
    ["1", "1", "0", "0", "0"],
    ["1", "1", "0", "0", "0"],
    ["0", "0", "1", "0", "0"],
    ["0", "0", "0", "1", "1"],
]
print(num_islands(grid1))  # 3
```

**단계별 추적** (grid1에서 첫 번째 섬):

```text
(0,0)='1' → BFS 시작
  큐: [(0,0)]
  pop (0,0): 이웃 (0,1)='1', (1,0)='1' → 큐에 추가
  pop (0,1): 이웃 (0,2)='0' skip, (1,1)='1' → 큐에 추가
  pop (1,0): 이웃 (1,1) 이미 방문
  pop (1,1): 이웃 모두 방문 또는 물
  → 섬 1 완성, count=1
```

**문제**: 방향 그래프에서 위상 정렬을 구하라 (DFS 기반).

```python
def topological_sort(graph: dict[str, list[str]]) -> list[str]:
    """
    DFS 기반 위상 정렬.
    모든 노드에서 DFS 후 완료 시각 역순 = 위상 정렬 순서
    """
    visited: set[str] = set()
    result: list[str] = []

    def dfs(node: str) -> None:
        visited.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor)
        result.append(node)  # 완료 후 추가

    for node in graph:
        if node not in visited:
            dfs(node)

    return list(reversed(result))


dag = {
    "A": ["C"],
    "B": ["C", "D"],
    "C": ["E"],
    "D": ["F"],
    "E": [],
    "F": [],
}
print(topological_sort(dag))  # ['B', 'A', 'D', 'C', 'F', 'E'] (순서 중 하나)
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 방문 체크를 빼먹음 | 무한 루프에 빠집니다 | 노드를 큐/스택에 넣을 때 visited에 추가합니다 |
| BFS 큐로 리스트 사용 | `pop(0)`이 `O(n)`입니다 | `collections.deque`를 사용합니다 |
| DFS를 재귀로만 구현 | 큰 그래프에서 `RecursionError`가 날 수 있습니다 | 반복형 DFS도 익혀 둡니다 |
| 방향 그래프와 무방향 그래프를 혼동 | 탐색 결과와 해석이 달라집니다 | 그래프 종류를 먼저 명시합니다 |
| 끊어진 그래프를 하나의 시작점만 탐색 | 일부 노드를 놓칩니다 | 모든 미방문 노드에서 시작합니다 |

## 복잡도 비교표

| 알고리즘 | 자료구조 | 시간 복잡도 | 주 용도 |
|----------|----------|-------------|---------|
| BFS | 큐 | `O(V+E)` | 무가중치 최단 경로, 층별 탐색 |
| DFS 재귀 | 호출 스택 | `O(V+E)` | 사이클, 연결성, 위상 정렬 |
| DFS 반복 | 명시적 스택 | `O(V+E)` | 깊은 그래프에서 안전 |

## 실무에서는 이렇게 연결됩니다

- 소셜 네트워크는 BFS로 친구의 친구를 추천할 수 있습니다.
- 웹 크롤러는 페이지를 층별로 방문할 때 BFS를 활용합니다.
- 패키지 관리자는 DFS 기반 위상 정렬로 의존성을 처리합니다.
- 미로 탐색과 게임 AI는 그래프 순회를 경로 탐색의 기반으로 사용합니다.
- 네트워크 토폴로지 분석도 그래프 순회 위에 세워집니다.

## 현업에서는 이렇게 생각합니다

BFS와 DFS는 그래프 알고리즘의 벽돌입니다. 이 둘을 이해하면 다익스트라, 위상 정렬, 최소 신장 트리 같은 다음 단계 주제가 훨씬 자연스럽게 이어집니다.

실무에서는 NetworkX 같은 라이브러리를 쓸 수 있지만, 내부 동작을 이해해야 어떤 문제에 어떤 탐색이 맞는지 스스로 판단할 수 있습니다.

## 운영 체크리스트

- [ ] 인접 리스트로 그래프를 표현할 수 있습니다
- [ ] BFS와 DFS의 차이를 설명할 수 있습니다
- [ ] BFS로 최단 경로를 찾을 수 있습니다
- [ ] DFS로 사이클을 검출할 수 있습니다
- [ ] 무방향 그래프의 연결 요소를 찾을 수 있습니다

## 연습 문제

1. 2차원 격자(미로)에서 최단 경로를 찾는 BFS 함수를 작성해 보세요.
2. 방향 그래프에서 DFS 기반 위상 정렬을 구현해 보세요.
3. 주어진 그래프가 이분 그래프인지 BFS로 판별해 보세요.

## 정리와 다음 글

BFS는 노드를 층별로 탐색하고, 가중치 없는 그래프의 최단 경로를 보장합니다. DFS는 깊게 먼저 들어가므로 사이클 검출과 위상 정렬에 잘 맞습니다. 다음 글에서는 가중치가 있는 그래프의 최단 경로를 다익스트라 알고리즘으로 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [Algorithms with Python 101 (1/10): 알고리즘이란 무엇인가?](./01-what-are-algorithms.md)
- [Algorithms with Python 101 (2/10): 시간 복잡도와 Big-O](./02-time-complexity-and-big-o.md)
- [Algorithms with Python 101 (3/10): 선형 탐색과 이진 탐색](./03-linear-and-binary-search.md)
- [Algorithms with Python 101 (4/10): 정렬 알고리즘](./04-sorting-algorithms.md)
- [Algorithms with Python 101 (5/10): 재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- [Algorithms with Python 101 (6/10): 동적 계획법 기초](./06-dynamic-programming-basics.md)
- **Algorithms with Python 101 (7/10): 그래프 탐색 — BFS와 DFS (현재 글)**
- [Algorithms with Python 101 (8/10): 최단 경로 기초](./08-shortest-path-basics.md)
- [Algorithms with Python 101 (9/10): 그리디 알고리즘](./09-greedy-algorithms.md)
- [코딩 테스트 문제 접근법](./10-coding-test-strategies.md)

<!-- toc:end -->

## 참고 자료

- [Wikipedia — Breadth-First Search](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Wikipedia — Depth-First Search](https://en.wikipedia.org/wiki/Depth-first_search)
- [Real Python — Graphs in Python](https://realpython.com/python-graph/)
- [Visualgo — Graph Traversal](https://visualgo.net/en/dfsbfs)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-python-101/ko/07-graph-traversal-bfs-dfs)

Tags: Python, Algorithms, Graphs, BFS, DFS
