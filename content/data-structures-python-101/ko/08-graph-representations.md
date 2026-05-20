---
series: data-structures-python-101
episode: 8
title: "Data Structures with Python 101 (8/10): 그래프 표현"
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
  - 자료구조
  - Graph
  - 그래프
  - BFS
seo_description: 그래프를 인접 리스트와 행렬로 구현하고 BFS와 DFS 순회 알고리즘의 원리, 다익스트라 최단 경로 전략을 익힙니다.
last_reviewed: '2026-05-15'
---

# Data Structures with Python 101 (8/10): 그래프 표현

이 글은 Data Structures with Python 101 시리즈의 여덟 번째 글입니다.

## 먼저 던지는 질문

- 소셜 네트워크, 지도, 의존성 관계는 코드에서 어떻게 표현할 수 있을까요?
- 인접 리스트와 인접 행렬은 각각 언제 유리할까요?
- BFS와 DFS는 무엇이 다르고 어디에 쓰일까요?

## 큰 그림

![Data Structures with Python 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-python-101/08/08-01-graph-representation-at-a-glance.ko.png)

*Data Structures with Python 101 8장 흐름 개요*

이 그림에서는 그래프 표현를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 그래프 표현의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 이 글이 중요한가

현실 세계의 대부분의 복잡한 관계는 그래프로 모델링할 수 있습니다. 친구 관계, 웹 링크, 도로망, 패키지 의존성, CI/CD 작업 흐름 모두 그래프 문제입니다. 그래서 그래프를 표현하고 순회하는 능력은 특정 문제 하나를 푸는 기술이 아니라, 관계형 시스템을 해석하는 기본 역량입니다.

> 그래프는 트리의 일반화입니다. 트리는 순환이 없는 연결 그래프라는 특수한 경우일 뿐입니다.

면접에서도 그래프는 중상급 난이도의 단골 주제입니다. 하지만 실제로 더 중요한 것은 “이 문제가 그래프 문제인가?”를 알아보는 능력입니다. 그래프로 모델링하는 순간 해결 전략이 BFS, DFS, 최단 경로, 위상 정렬 쪽으로 빠르게 정리되기 때문입니다.

## 핵심 개념 한눈에 보기

> 그래프 = 정점과 간선으로 관계를 표현하는 구조

```text
[Undirected Graph]        [Adjacency List]
  A --- B                  A: [B, C]
  |   / |                  B: [A, C, D]
  |  /  |                  C: [A, B]
  C --- D                  D: [B]
```

## 그래프 표현을 그림으로 보면

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 정점(vertex) | 그래프를 구성하는 노드입니다 |
| 간선(edge) | 두 정점 사이의 연결입니다 |
| 방향 그래프 | 간선에 방향이 있는 그래프입니다 |
| 가중치 그래프 | 간선마다 비용이나 거리 같은 값을 갖는 그래프입니다 |
| 인접 리스트 | 각 정점이 연결된 이웃 정점을 list로 저장하는 방식입니다 |

## Before / After

관계를 흩어진 변수로 관리하는 방식과 그래프로 구조화하는 방식을 비교해 보겠습니다.

```python
# before: relationships in individual variables — hard to extend
alice_friends = ["bob", "charlie"]
bob_friends = ["alice", "charlie", "diana"]
# adding a new user requires code changes
```

```python
# after: structured as a graph (adjacency list) — easy to extend
graph = {
    "alice": ["bob", "charlie"],
    "bob": ["alice", "charlie", "diana"],
    "charlie": ["alice", "bob"],
    "diana": ["bob"],
}
# new user: graph["eve"] = ["alice"]
```

이 차이는 단순한 코드 정리 이상의 의미가 있습니다. 그래프로 표현하는 순간, 탐색과 분석을 일반화할 수 있고 새로운 노드나 관계도 데이터만 바꿔 확장할 수 있습니다.

## 단계별 실습

### Step 1: Implement a graph with an adjacency list

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

### Step 2: Implement a graph with an adjacency matrix

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
        self.matrix[j][i] = weight  # undirected

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

### Step 3: Implement BFS

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

### Step 4: Implement DFS (recursive and iterative)

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

print(f"DFS recursive: {dfs_recursive(g, 'A')}")
print(f"DFS iterative: {dfs_iterative(g, 'A')}")
```

### Step 5: Weighted graph and shortest path

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

## 이 코드에서 먼저 봐야 할 점

- 인접 리스트는 희소 그래프에, 인접 행렬은 밀집 그래프에 더 잘 맞습니다.
- BFS는 큐를 쓰고 DFS는 스택이나 재귀를 씁니다. 구현 도구가 곧 탐색 전략입니다.
- BFS는 가중치 없는 그래프에서 최단 경로를 보장합니다.
- Dijkstra는 가중치 그래프에서 힙을 사용해 최단 경로를 계산합니다.

그래프 문제를 잘 풀려면 구현보다 먼저 관계를 구조로 보는 눈이 필요합니다. 값 하나를 처리하는 대신, 연결을 따라 움직이는 사고방식으로 전환해야 BFS·DFS·최단 경로가 한 흐름으로 이어집니다.

실무에서는 메모리와 장애 패턴을 같이 봐야 합니다. 인접 행렬은 간선 존재 확인이 단순하지만, 정점이 10만 개만 되어도 O(V²) 메모리 비용이 바로 문제가 됩니다. 반대로 인접 리스트는 희소 그래프에 효율적이지만, 특정 간선 존재 여부를 자주 검사하면 탐색 비용이 누적될 수 있습니다.

탐색 방식도 운영 특성과 연결됩니다. BFS는 최단 경로를 찾는 대신 큐가 빠르게 커질 수 있고, DFS는 메모리는 덜 쓰더라도 깊은 그래프에서 재귀 한계나 편향 탐색 문제가 생길 수 있습니다. 가중치가 있는 경로에 음수 간선이 섞이면 Dijkstra가 틀린 답을 낼 수 있다는 점도 반드시 기억해야 합니다.

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 방문 체크 없이 순회 | 순환이 있는 그래프에서 무한 루프가 날 수 있습니다 | `seen`/`visited` 집합을 둡니다 |
| 무방향 그래프에서 한 방향만 간선 추가 | 일부 경로를 절대 방문하지 못합니다 | `add_edge`에서 양방향을 모두 추가합니다 |
| 희소 그래프에 인접 행렬 사용 | O(V²) 메모리를 낭비합니다 | 기본 선택은 인접 리스트로 시작합니다 |
| DFS에 큐 사용 | 의도와 다르게 BFS가 됩니다 | DFS는 stack, BFS는 queue를 사용합니다 |
| Dijkstra에 음수 가중치 사용 | 결과가 보장되지 않습니다 | 음수 가중치가 있으면 Bellman-Ford를 검토합니다 |

## 실무에서 이렇게 쓰입니다

- 소셜 네트워크는 BFS 기반 친구 추천을 구현합니다.
- 패키지 매니저는 의존성 그래프를 정렬합니다.
- 내비게이션은 최단 경로 계산에 가중치 그래프를 사용합니다.
- 웹 크롤러는 BFS 방식으로 페이지를 넓게 방문할 수 있습니다.
- CI/CD 파이프라인은 작업 의존성을 DAG로 표현합니다.

## 실무에서는 이렇게 생각합니다

실무에서 그래프를 처음부터 구현하는 일은 드물고, NetworkX 같은 라이브러리나 Neo4j 같은 그래프 데이터베이스를 쓰는 일이 더 흔합니다. 그래도 BFS, DFS, 최단 경로의 내부 원리를 알아야 도구를 제대로 선택하고 병목을 설명할 수 있습니다.

결국 그래프 실력의 핵심은 구현보다 모델링입니다. “이 관계를 그래프로 볼 수 있는가?”를 먼저 알아차리면, 해결 전략은 그다음부터 훨씬 빠르게 정리됩니다.

## 체크리스트

- [ ] 인접 리스트와 인접 행렬의 차이를 설명할 수 있다
- [ ] BFS와 DFS를 구현할 수 있다
- [ ] 방향 그래프와 무방향 그래프를 구분할 수 있다
- [ ] 가중치 그래프에 Dijkstra를 적용할 수 있다
- [ ] 상황에 맞는 그래프 표현 방식을 선택할 수 있다

## 연습 문제

1. BFS를 사용해 두 노드 사이의 최단 경로(간선 수 기준)를 구하는 함수를 작성해 보세요.
2. DFS를 사용해 그래프의 연결 요소를 모두 찾는 함수를 작성해 보세요.
3. 방향 그래프에 사이클이 있는지 감지하는 함수를 작성해 보세요.

## 정리 및 다음 글 안내

그래프는 관계를 표현하는 범용 자료구조입니다. 인접 리스트와 인접 행렬로 표현할 수 있고, BFS와 DFS로 순회할 수 있으며, 가중치가 붙으면 최단 경로 문제로 확장됩니다. 다음 글에서는 중복 제거와 집합 연산에 강한 set을 살펴보겠습니다.

## 처음 질문으로 돌아가기

- **소셜 네트워크, 지도, 의존성 관계는 코드에서 어떻게 표현할 수 있을까요?**
  - 본문의 기준은 그래프 표현를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **인접 리스트와 인접 행렬은 각각 언제 유리할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **BFS와 DFS는 무엇이 다르고 어디에 쓰일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Structures with Python 101 (1/10): 자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [Data Structures with Python 101 (2/10): 배열과 리스트](./02-arrays-and-lists.md)
- [Data Structures with Python 101 (3/10): 스택과 큐](./03-stacks-and-queues.md)
- [Data Structures with Python 101 (4/10): 해시 테이블과 dict](./04-hash-tables-and-dict.md)
- [Data Structures with Python 101 (5/10): 연결 리스트](./05-linked-lists.md)
- [Data Structures with Python 101 (6/10): 트리와 이진 트리](./06-trees-and-binary-trees.md)
- [Data Structures with Python 101 (7/10): 힙과 우선순위 큐](./07-heaps-and-priority-queues.md)
- **그래프 표현 (현재 글)**
- set과 집합 연산 (예정)
- 자료구조 선택 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [NetworkX Documentation](https://networkx.org/documentation/stable/)
- [Python 공식 문서 — heapq](https://docs.python.org/3/library/heapq.html)
- [Runestone Academy — Graphs](https://runestone.academy/ns/books/published/pythonds3/Graphs/toctree.html)
- [Real Python — Graphs in Python](https://realpython.com/python-graph-algorithm/)

Tags: Python, 자료구조, Graph, 그래프, BFS
