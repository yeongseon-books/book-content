---
series: discrete-math-101
episode: 9
title: "Discrete Math 101 (9/10): 트리와 그래프 탐색"
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
  - 이산수학
  - 트리
  - BFS
  - DFS
  - 신장 트리
seo_description: 트리, BFS, DFS, 신장 트리와 MST를 그래프 탐색의 기본 도구로 설명합니다.
last_reviewed: '2026-05-12'
---

# Discrete Math 101 (9/10): 트리와 그래프 탐색

이 글은 Discrete Math 101 시리즈의 9번째 글입니다.

## 먼저 던지는 질문

- 트리의 정의와 성질은 무엇일까요?
- BFS는 왜 최단 경로와 연결될까요?
- DFS는 어떤 문제에서 강할까요?

## 큰 그림

![Discrete Math 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/discrete-math-101/09/09-01-big-picture.ko.png)

*Discrete Math 101 9장 흐름 개요*

이 그림에서는 트리와 그래프 탐색를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 트리와 그래프 탐색의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

파일 시스템, DOM, 컴파일러 AST, 데이터베이스 인덱스처럼 많은 시스템 내부에는 트리가 숨어 있습니다. BFS와 DFS는 최단 경로, 사이클 검출, 위상 정렬, MST의 출발점입니다.

> 트리는 가장 단순한 비자명 그래프이고, 탐색은 그래프 알고리즘의 기본 동작입니다.

## 한눈에 보는 개념

> 트리는 연결된 무사이클 무방향 그래프입니다. 정점이 n개면 간선은 정확히 n-1개이고, 임의의 두 정점 사이 경로는 정확히 하나입니다.

```text
       tree                    BFS order            DFS order
        1                    1 → 2 → 3            1 → 2 → 4
       / \                   → 4 → 5 → 6          → 5 → 3 → 6
      2   3                  (level by level)     (one branch first)
     / \   \
    4   5   6
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| Tree | 연결된 사이클 없는 그래프 |
| Root | 선택된 시작 정점 |
| Leaf | 차수 1의 정점 |
| Spanning tree | 모든 정점을 포함하는 부분 트리 |
| MST | 총 가중치가 최소인 신장 트리 |

## Before / After

**Before — checking every node by hand:**

```python
# Friends-of-friends, written manually — duplicate code per depth
def friends_of_friends(person):
    result = set()
    for f in friends_of(person):
        for ff in friends_of(f):
            result.add(ff)
    return result
```

**After — BFS for arbitrary distance:**

```python
from collections import deque

def reachable_within(graph, start, max_distance):
    """All vertices within distance max_distance from start."""
    visited = {start: 0}
    queue = deque([start])
    while queue:
        v = queue.popleft()
        if visited[v] >= max_distance:
            continue
        for u in graph[v]:
            if u not in visited:
                visited[u] = visited[v] + 1
                queue.append(u)
    return visited
```

## 단계별로 따라가기

### 1단계: 트리 정의와 검증

```python
from collections import defaultdict

def is_tree(edges: list, n_nodes: int) -> bool:
    """Test whether an undirected graph is a tree — check edge count and connectivity."""
    if len(edges) != n_nodes - 1:
        return False
    adj = defaultdict(set)
    for u, v in edges:
        adj[u].add(v); adj[v].add(u)
    visited = set()
    stack = [next(iter(adj))]
    while stack:
        v = stack.pop()
        if v in visited:
            continue
        visited.add(v)
        stack.extend(adj[v] - visited)
    return len(visited) == n_nodes

tree_edges = [(1, 2), (1, 3), (2, 4), (2, 5), (3, 6)]
print(f"is tree: {is_tree(tree_edges, 6)}")
```

트리를 판정할 때 가장 실용적인 감각은 `V - 1 = E`와 연결성입니다. 이 두 조건이 함께 맞아떨어지면 트리라는 판단이 매우 쉬워집니다.

### 2단계: BFS — 너비 우선 탐색

```python
def bfs(graph: dict, start) -> dict:
    """Minimum number of edges from start to every vertex (assuming weight 1)."""
    distances = {start: 0}
    queue = deque([start])
    while queue:
        v = queue.popleft()
        for u in sorted(graph[v]):
            if u not in distances:
                distances[u] = distances[v] + 1
                queue.append(u)
    return distances

graph = {1: [2, 3], 2: [1, 4, 5], 3: [1, 6], 4: [2], 5: [2], 6: [3]}
print(f"distances from 1: {bfs(graph, 1)}")
```

BFS는 큐를 사용해 가까운 정점부터 탐색합니다. 모든 간선 가중치가 같다면 BFS가 최단 경로를 준다는 사실이 실무적으로 특히 중요합니다.

**예상 출력**

```text
distances from 1: {1: 0, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2}
```

- 정점 `2`, `3`은 시작점 `1`에서 한 간선 거리, `4`, `5`, `6`은 두 간선 거리여야 합니다.
- BFS에서 거리가 틀리면 보통 `visited` 표시를 늦게 하거나, 큐 대신 스택처럼 동작하게 만든 경우가 많습니다.

### 3단계: DFS — 깊이 우선 탐색

```python
def dfs_recursive(graph: dict, start, visited=None) -> list:
    """Recursive DFS — returns visit order."""
    if visited is None:
        visited = set()
    if start in visited:
        return []
    visited.add(start)
    order = [start]
    for u in sorted(graph[start]):
        order.extend(dfs_recursive(graph, u, visited))
    return order

def dfs_iterative(graph: dict, start) -> list:
    """Stack-based DFS — safe when depth is large."""
    visited, order, stack = set(), [], [start]
    while stack:
        v = stack.pop()
        if v in visited:
            continue
        visited.add(v); order.append(v)
        stack.extend(sorted(graph[v], reverse=True))
    return order

print(f"DFS recursive: {dfs_recursive(graph, 1)}")
print(f"DFS iterative: {dfs_iterative(graph, 1)}")
```

DFS는 한 갈래를 끝까지 따라간 뒤 되돌아옵니다. 그래서 사이클 검출, 위상 정렬, 강한 연결 요소처럼 구조를 깊게 파악하는 문제에 잘 맞습니다.

**예상 출력**

```text
DFS recursive: [1, 2, 4, 5, 3, 6]
DFS iterative: [1, 2, 4, 5, 3, 6]
```

- 이 예제는 이웃을 정렬했기 때문에 재귀 DFS와 반복 DFS의 방문 순서가 같게 고정됩니다.
- 다른 순서가 나왔다면 알고리즘이 틀렸다기보다 이웃 순서가 달라졌을 가능성이 큽니다. 검증용 예제에서는 항상 `sorted(...)`를 먼저 적용해 보세요.

### 4단계: BFS/DFS가 만드는 신장 트리

```python
def spanning_tree_bfs(graph: dict, start) -> list:
    """Extract a spanning tree via BFS."""
    visited = {start}
    tree = []
    queue = deque([start])
    while queue:
        v = queue.popleft()
        for u in sorted(graph[v]):
            if u not in visited:
                visited.add(u)
                tree.append((v, u))
                queue.append(u)
    return tree

print(f"spanning tree (BFS): {spanning_tree_bfs(graph, 1)}")
```

BFS와 DFS는 모두 그래프 전체를 덮는 신장 트리를 만들 수 있습니다. 즉, 탐색 과정 자체가 그래프의 뼈대를 하나 뽑아내는 작업이기도 합니다.

**예상 출력**

```text
spanning tree (BFS): [(1, 2), (1, 3), (2, 4), (2, 5), (3, 6)]
```

- BFS 신장 트리는 루트에서 가까운 정점부터 부모가 정해지므로, 같은 그래프를 쓰면 위 간선 집합이 나와야 합니다.
- 간선 수는 항상 `정점 수 - 1`개여야 합니다. 여기서는 6개 정점을 덮으므로 5개 간선이 맞습니다.

### 5단계: 최소 신장 트리(MST) — Kruskal

```python
def kruskal_mst(n_nodes: int, weighted_edges: list) -> list:
    """Spanning tree of minimum total weight — uses Union-Find."""
    parent = list(range(n_nodes))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        parent[ra] = rb
        return True

    mst = []
    for w, u, v in sorted(weighted_edges):
        if union(u, v):
            mst.append((u, v, w))
        if len(mst) == n_nodes - 1:
            break
    return mst

edges = [(1, 0, 1), (4, 0, 2), (2, 1, 2), (3, 1, 3), (5, 2, 3)]
mst = kruskal_mst(4, edges)
total_weight = sum(w for _, _, w in mst)
print(f"MST: {mst}")
print(f"total weight: {total_weight}")
```

Kruskal은 간선을 가중치 순으로 보되 사이클을 만드는 간선은 건너뜁니다. 통신망 설계, 배선, 클러스터링에서 자주 쓰이는 이유가 바로 이 단순함과 강력함에 있습니다.

**예상 출력**

```text
MST: [(0, 1, 1), (1, 2, 2), (1, 3, 3)]
total weight: 6
```

- 가중치가 가장 작은 간선부터 보되, `(0, 2, 4)`와 `(2, 3, 5)`는 이미 연결된 정점을 다시 잇거나 더 비싸므로 선택되지 않습니다.
- 결과 간선은 3개여야 하고, 총 가중치는 6이어야 합니다.
- 값이 다르면 Union-Find의 `find/union`이 사이클을 제대로 막고 있는지 먼저 확인해 보세요.

## 주목할 점

- BFS와 DFS는 골격은 같고 사용 자료구조만 다릅니다.
- 트리는 `V - 1 = E` 성질과 연결성으로 검증할 수 있습니다.
- BFS 신장 트리는 가중치가 동일할 때 최단 경로 트리이기도 합니다.
- MST는 그리디 알고리즘이 최적해를 보장하는 대표 사례입니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 방문 표시를 늦게 한다 | 무한 루프가 생긴다 | 진입 즉시 visited에 넣는다 |
| 큐와 스택을 헷갈린다 | BFS와 DFS가 뒤바뀐다 | `popleft`와 `pop`을 명확히 구분한다 |
| 재귀 DFS만 고집한다 | 깊은 그래프에서 스택 오버플로가 난다 | 큰 입력은 반복 DFS를 쓴다 |
| 가중치 그래프에도 BFS를 쓴다 | 최단 경로가 틀린다 | 가중치가 있으면 Dijkstra를 고려한다 |
| MST에서 사이클 검사를 뺀다 | 결과가 트리가 아니게 된다 | Union-Find로 차단한다 |

## 실무에서는 이렇게 사용합니다

- 웹 크롤러는 깊이 제한 BFS를 사용합니다.
- 컴파일러는 AST를 DFS 순회합니다.
- 게임 AI는 상태 공간을 BFS, DFS, A*로 탐색합니다.
- 최소 비용 네트워크 설계는 MST 문제입니다.
- React의 가상 DOM 비교도 트리 비교 문제로 볼 수 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 그래프 문제를 보면 가장 먼저 “BFS인가, DFS인가”를 결정합니다. 레벨별 탐색이나 무가중치 최단 경로는 BFS, 경로 구조 분석이나 사이클 검출은 DFS가 기본입니다. 또한 입력 크기가 크면 재귀 DFS 대신 명시적 스택을 사용하는 식으로 메모리 한계까지 함께 고려합니다.

## 체크리스트

- [ ] 트리의 정의와 `V-1 = E` 성질을 안다
- [ ] BFS와 DFS의 차이를 자료구조 기준으로 설명할 수 있다
- [ ] BFS가 최단 경로를 보장하는 조건을 안다
- [ ] 신장 트리와 MST의 차이를 이해한다
- [ ] Kruskal에서 Union-Find의 역할을 안다

## 연습 문제

1. 정점 5개인 트리에서 간선 수와 최소 리프 수를 구해 보세요.

2. 2차원 미로에서 시작점부터 목표점까지 최단 경로를 찾는 BFS를 작성해 보세요.

3. 도시 6개와 임의의 가중치를 두고 Kruskal로 MST를 손으로 계산해 보세요.

## 정리 및 다음 단계

트리는 연결된 무사이클 그래프이며, BFS와 DFS는 그래프 위를 움직이는 가장 기본적인 탐색입니다. MST는 가중 그래프를 최소 비용으로 연결하는 부분 트리입니다.

다음 글에서는 지금까지 배운 이산수학의 모든 주제가 알고리즘 분석과 실무 의사결정에 어떻게 연결되는지 묶어 보겠습니다.

## 처음 질문으로 돌아가기

- **트리의 정의와 성질은 무엇일까요?**
  - 본문의 기준은 트리와 그래프 탐색를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **BFS는 왜 최단 경로와 연결될까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **DFS는 어떤 문제에서 강할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Discrete Math 101 (1/10): 이산수학이란 무엇인가?](./01-what-is-discrete-math.md)
- [Discrete Math 101 (2/10): 명제와 논리](./02-propositions-and-logic.md)
- [Discrete Math 101 (3/10): 집합과 함수](./03-sets-and-functions.md)
- [Discrete Math 101 (4/10): 관계와 동치관계](./04-relations-and-equivalence.md)
- [Discrete Math 101 (5/10): 증명 방법](./05-proof-techniques.md)
- [Discrete Math 101 (6/10): 수열과 점화식](./06-sequences-and-recurrence.md)
- [Discrete Math 101 (7/10): 조합과 경우의 수](./07-combinatorics.md)
- [Discrete Math 101 (8/10): 그래프 이론 기초](./08-graph-theory-basics.md)
- **트리와 그래프 탐색 (현재 글)**
- 알고리즘과 이산수학의 연결 (예정)

<!-- toc:end -->

## 참고 자료

- [Discrete Mathematics and Its Applications — Kenneth Rosen, Chapter 11](https://www.mheducation.com/highered/product/discrete-mathematics-its-applications-rosen/M9781259676512.html)
- [Algorithms — Sedgewick & Wayne, Section 4.1 Undirected Graphs](https://algs4.cs.princeton.edu/41graph/)
- [Algorithms — Sedgewick & Wayne, Chapter 4.3](https://algs4.cs.princeton.edu/43mst/)
- [MIT Mathematics for Computer Science — Trees and Graph Traversal](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)

Tags: Computer Science, 이산수학, 트리, BFS, DFS, 신장 트리
