---
series: data-structures-python-101
episode: 8
title: 그래프 표현
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
  - 자료구조
  - Graph
  - 그래프
  - BFS
seo_description: Python으로 그래프를 인접 리스트와 인접 행렬로 표현하고 탐색합니다.
last_reviewed: '2026-05-04'
---

# 그래프 표현

> Data Structures with Python 101 시리즈 (8/10)


## 이 글에서 다룰 문제

현실 세계의 관계는 대부분 그래프로 모델링됩니다. 소셜 네트워크의 친구 관계, 웹 페이지 링크, 도로망, 패키지 의존성 등이 모두 그래프입니다. 그래프를 표현하고 탐색하는 능력은 복잡한 문제를 해결하는 핵심 역량입니다.

> 그래프는 트리의 일반화입니다. 트리는 순환이 없는 연결 그래프의 특수한 경우입니다.

코딩 면접에서 그래프 문제는 중상급 난이도로 자주 출제됩니다. BFS, DFS를 자유자재로 구현할 수 있어야 합니다.

## 핵심 개념 잡기

> 그래프 = 노드(정점)들과 그것들을 연결하는 간선의 집합

```
[무방향 그래프]        [인접 리스트]
  A --- B              A: [B, C]
  |   / |              B: [A, C, D]
  |  /  |              C: [A, B]
  C --- D              D: [B]
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 정점(vertex) | 그래프의 노드입니다 |
| 간선(edge) | 두 정점을 연결하는 선입니다 |
| 방향 그래프 | 간선에 방향이 있는 그래프입니다 |
| 가중치 그래프 | 간선에 비용(가중치)이 있는 그래프입니다 |
| 인접 리스트 | 각 정점의 이웃을 리스트로 저장하는 표현 방식입니다 |

## Before / After

관계 데이터를 비구조적으로 관리하는 방법과 그래프로 구조화하는 방법을 비교합니다.

```python
# before: 관계를 개별 변수로 관리 — 확장 어려움
alice_friends = ["bob", "charlie"]
bob_friends = ["alice", "charlie", "diana"]
# 새 사용자 추가 시 코드 수정 필요
```

```python
# after: 그래프(인접 리스트)로 구조화 — 확장 용이
graph = {
    "alice": ["bob", "charlie"],
    "bob": ["alice", "charlie", "diana"],
    "charlie": ["alice", "bob"],
    "diana": ["bob"],
}
# 새 사용자: graph["eve"] = ["alice"]
```

## 단계별 실습

### Step 1: 인접 리스트로 그래프 구현

```python
from collections import defaultdict

class Graph:
    def __init__(self, directed=False):
        self.adj = defaultdict(list)
        self.directed = directed

    def add_edge(self, u, v):
        self.adj[u].append(v)
        if not self.directed:
            self.adj[v].append(u)

    def neighbors(self, node):
        return self.adj[node]

    def __str__(self):
        lines = []
        for node in sorted(self.adj):
            lines.append(f"{node}: {self.adj[node]}")
        return "\n".join(lines)

g = Graph()
g.add_edge("A", "B")
g.add_edge("A", "C")
g.add_edge("B", "C")
g.add_edge("B", "D")
print(g)
# A: ['B', 'C']
# B: ['A', 'C', 'D']
# C: ['A', 'B']
# D: ['B']
```

### Step 2: 인접 행렬로 그래프 구현

```python
class GraphMatrix:
    def __init__(self, vertices: list):
        self.vertices = vertices
        self.index = {v: i for i, v in enumerate(vertices)}
        n = len(vertices)
        self.matrix = [[0] * n for _ in range(n)]

    def add_edge(self, u, v, weight=1):
        i, j = self.index[u], self.index[v]
        self.matrix[i][j] = weight
        self.matrix[j][i] = weight  # 무방향

    def has_edge(self, u, v):
        i, j = self.index[u], self.index[v]
        return self.matrix[i][j] != 0

    def print_matrix(self):
        print("  ", " ".join(self.vertices))
        for i, v in enumerate(self.vertices):
            print(f"{v}:", self.matrix[i])

gm = GraphMatrix(["A", "B", "C", "D"])
gm.add_edge("A", "B")
gm.add_edge("A", "C")
gm.add_edge("B", "D")
gm.print_matrix()
```

### Step 3: BFS 구현

```python
from collections import deque

def bfs(graph, start):
    visited = []
    queue = deque([start])
    seen = {start}
    while queue:
        node = queue.popleft()
        visited.append(node)
        for neighbor in graph.neighbors(node):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return visited

g = Graph()
for u, v in [("A","B"), ("A","C"), ("B","D"), ("C","D"), ("D","E")]:
    g.add_edge(u, v)

print(f"BFS from A: {bfs(g, 'A')}")
# BFS from A: ['A', 'B', 'C', 'D', 'E']
```

### Step 4: DFS 구현 (재귀 + 반복)

```python
def dfs_recursive(graph, node, visited=None):
    if visited is None:
        visited = []
    visited.append(node)
    for neighbor in graph.neighbors(node):
        if neighbor not in visited:
            dfs_recursive(graph, neighbor, visited)
    return visited

def dfs_iterative(graph, start):
    visited = []
    stack = [start]
    seen = set()
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        visited.append(node)
        for neighbor in reversed(graph.neighbors(node)):
            if neighbor not in seen:
                stack.append(neighbor)
    return visited

print(f"DFS 재귀: {dfs_recursive(g, 'A')}")
print(f"DFS 반복: {dfs_iterative(g, 'A')}")
```

### Step 5: 가중치 그래프와 최단 경로

```python
import heapq
from collections import defaultdict

class WeightedGraph:
    def __init__(self):
        self.adj = defaultdict(list)

    def add_edge(self, u, v, weight):
        self.adj[u].append((v, weight))
        self.adj[v].append((u, weight))

def dijkstra(graph, start):
    dist = {start: 0}
    heap = [(0, start)]
    while heap:
        d, node = heapq.heappop(heap)
        if d > dist.get(node, float("inf")):
            continue
        for neighbor, weight in graph.adj[node]:
            new_dist = d + weight
            if new_dist < dist.get(neighbor, float("inf")):
                dist[neighbor] = new_dist
                heapq.heappush(heap, (new_dist, neighbor))
    return dist

wg = WeightedGraph()
wg.add_edge("A", "B", 4)
wg.add_edge("A", "C", 2)
wg.add_edge("B", "D", 3)
wg.add_edge("C", "D", 1)
wg.add_edge("D", "E", 5)

distances = dijkstra(wg, "A")
print(distances)  # {'A': 0, 'C': 2, 'B': 4, 'D': 3, 'E': 8}
```

## 이 코드에서 주목할 점

- 인접 리스트는 희소 그래프에 적합하고, 인접 행렬은 밀집 그래프에 적합합니다
- BFS는 큐(deque)를, DFS는 스택(list 또는 재귀)을 사용합니다
- BFS는 가중치 없는 그래프에서 최단 경로를 보장합니다
- Dijkstra는 가중치 그래프에서 최단 경로를 구하며 힙을 사용합니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 방문 체크 없이 탐색 | 순환 그래프에서 무한 루프에 빠집니다 | seen/visited 집합으로 방문을 체크합니다 |
| 무방향 그래프에서 한쪽만 간선 추가 | 탐색 시 일부 경로가 누락됩니다 | add_edge에서 양방향을 모두 추가합니다 |
| 인접 행렬을 희소 그래프에 사용 | 메모리가 O(V²)로 낭비됩니다 | 인접 리스트를 사용합니다 |
| DFS에서 스택 대신 큐 사용 | DFS가 아닌 BFS가 됩니다 | DFS는 스택(pop), BFS는 큐(popleft)입니다 |
| Dijkstra에 음수 가중치 사용 | 정확한 결과를 보장하지 않습니다 | 음수 가중치에는 Bellman-Ford를 사용합니다 |

## 실무에서 이렇게 쓰입니다

- 소셜 네트워크에서 친구 추천을 BFS로 구현합니다 (2촌 탐색)
- 패키지 매니저가 의존성 그래프를 위상 정렬합니다
- 네비게이션 앱이 Dijkstra로 최단 경로를 계산합니다
- 웹 크롤러가 BFS로 페이지를 방문합니다
- CI/CD 파이프라인이 작업 의존성을 DAG(방향 비순환 그래프)로 관리합니다

## 현업 개발자는 이렇게 생각합니다

실무에서 그래프를 직접 구현하는 경우는 드뭅니다. NetworkX 같은 라이브러리를 사용하거나, 그래프 데이터베이스(Neo4j)를 활용합니다. 하지만 BFS, DFS, 최단 경로의 원리를 이해하면 라이브러리를 더 효과적으로 사용할 수 있습니다.

문제를 그래프로 모델링하는 능력이 핵심입니다. "이 문제가 그래프 문제인가?"를 판단하는 것이 풀이보다 어려운 경우가 많습니다.

## 체크리스트

- [ ] 인접 리스트와 인접 행렬의 차이를 설명할 수 있다
- [ ] BFS와 DFS를 구현할 수 있다
- [ ] 방향 그래프와 무방향 그래프를 구분할 수 있다
- [ ] 가중치 그래프에서 Dijkstra를 적용할 수 있다
- [ ] 그래프 표현 방식을 상황에 맞게 선택할 수 있다

## 정리 및 다음 글 안내

그래프는 관계를 표현하는 범용 자료구조입니다. 인접 리스트와 인접 행렬로 표현하고, BFS와 DFS로 탐색합니다. 다음 글에서는 집합 연산을 효율적으로 수행하는 set을 다룹니다.

<!-- toc:begin -->
- [자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [배열과 리스트](./02-arrays-and-lists.md)
- [스택과 큐](./03-stacks-and-queues.md)
- [해시 테이블과 dict](./04-hash-tables-and-dict.md)
- [연결 리스트](./05-linked-lists.md)
- [트리와 이진 트리](./06-trees-and-binary-trees.md)
- [힙과 우선순위 큐](./07-heaps-and-priority-queues.md)
- **그래프 표현 (현재 글)**
- set과 집합 연산 (예정)
- 자료구조 선택 기준 (예정)
<!-- toc:end -->

## 참고 자료

- [Real Python — Graphs in Python](https://realpython.com/python-graph-algorithm/)
- [GeeksforGeeks — Graph Data Structure](https://www.geeksforgeeks.org/graph-data-structure-and-algorithms/)
- [Visualgo — Graph Traversal](https://visualgo.net/en/dfsbfs)
- [NetworkX Documentation](https://networkx.org/documentation/stable/)
