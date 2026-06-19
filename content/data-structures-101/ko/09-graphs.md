---
episode: 9
language: ko
last_reviewed: '2026-05-12'
seo_description: 그래프의 인접 리스트와 인접 행렬 표현 방식, BFS와 DFS의 동작 원리와 실무에서의 활용 사례를 정리합니다.
series: data-structures-101
status: publish-ready
tags:
- Computer Science
- 자료구조
- 그래프
- 인접 리스트
- 인접 행렬
- 그래프 탐색
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "Data Structures 101 (9/10): 그래프"
---

# Data Structures 101 (9/10): 그래프

> 그래프 `G = (V, E)`는 정점 집합 V와 간선 집합 E로 정의합니다. 간선에 방향이 있으면 방향 그래프, 가중치가 있으면 가중치 그래프입니다. 인접 리스트는 메모리 효율이 좋고, 인접 행렬은 두 정점 사이 간선 존재 여부를 O(1)에 확인할 수 있습니다.

이 글은 Data Structures 101 시리즈의 아홉 번째 글입니다.

![Data Structures 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-101/09/09-01-graph-representations.ko.png)
*Data Structures 101 9장 흐름 개요*

## 이 글에서 다룰 문제

- 정점, 간선, 차수, 경로 같은 그래프 용어를 어떻게 정확히 쓸까요?
- 인접 리스트와 인접 행렬은 어떤 트레이드오프를 가질까요?
- 방향 그래프와 무방향 그래프, 가중치 그래프와 비가중치 그래프는 무엇이 다를까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

그래프는 컴퓨터과학에서 가장 일반적이고 강력한 자료구조입니다. 소셜 네트워크, 지도, 인터넷, 의존성 관리자, 추천 알고리즘 모두 그래프 위에서 설명할 수 있습니다. 그래프 순회가 익숙하지 않으면 많은 코딩 문제와 시스템 문제를 다루기 어려워집니다.

> 트리는 가장 단순한 관계이고, 현실 세계는 대부분 그래프로 설명하는 편이 더 정확합니다.

## 핵심 한눈에 보기

| 용어 | 의미 |
| --- | --- |
| 정점 | 그래프의 노드 |
| 간선 | 두 정점을 잇는 연결 |
| 차수 | 한 정점에 연결된 간선 수 |
| 경로 | 간선으로 이어진 정점들의 순서 |
| 사이클 | 시작점과 끝점이 같은 경로 |

## 전후 비교

**Before — 일관성 없는 dict-of-dict 표현:**

```text
graph = {"A": {"B": 1}, "B": {"A": 1, "C": 2}, ...}
# 동작은 하지만 인터페이스가 없어 알고리즘마다 다르게 접근해야 함
```

**After — 명시적 Graph 클래스:**

```python
class Graph:
    def __init__(self): self._adj = {}
    def add_edge(self, u, v, w=1): ...
    def neighbors(self, u): ...
# 모든 알고리즘이 같은 인터페이스를 사용 가능
```

표현이 제각각이면 BFS, DFS, 최단 경로 같은 알고리즘을 재사용하기 어렵습니다. 그래프는 인터페이스를 먼저 정리하는 것만으로도 코드 품질이 크게 좋아집니다.

## 단계별로 따라하기

### 1단계: 인접 리스트로 그래프 표현

```python
class Graph:
    def __init__(self, directed=False):
        self._adj = {}
        self._directed = directed

    def add_node(self, u):
        self._adj.setdefault(u, [])

    def add_edge(self, u, v, weight=1):
        self.add_node(u); self.add_node(v)
        self._adj[u].append((v, weight))
        if not self._directed:
            self._adj[v].append((u, weight))

    def neighbors(self, u):
        return self._adj.get(u, [])

    def __iter__(self):
        return iter(self._adj)

service_graph = Graph(directed=True)
for u, v in [
    ("api-gateway", "auth-service"),
    ("api-gateway", "catalog-service"),
    ("auth-service", "user-db"),
    ("catalog-service", "inventory-service"),
    ("inventory-service", "warehouse-db"),
    ("inventory-service", "cache"),
    ("cache", "warehouse-db"),
]:
    service_graph.add_edge(u, v)
```

dict와 list를 조합한 가장 표준적인 표현입니다. 메모리 사용량은 O(V + E)라서 서비스 의존성처럼 희소한 실무 그래프에 특히 잘 맞습니다.

### 2단계: 인접 행렬로 표현

```python
class MatrixGraph:
    def __init__(self, n, directed=False):
        self.n = n
        self.directed = directed
        self.matrix = [[0] * n for _ in range(n)]

    def add_edge(self, u, v, weight=1):
        self.matrix[u][v] = weight
        if not self.directed:
            self.matrix[v][u] = weight

    def has_edge(self, u, v):
        return self.matrix[u][v] != 0

matrix_graph = MatrixGraph(4, directed=True)
matrix_graph.add_edge(0, 1); matrix_graph.add_edge(0, 2)
matrix_graph.add_edge(1, 3); matrix_graph.add_edge(2, 3)
print(matrix_graph.has_edge(0, 1))   # True
print(matrix_graph.has_edge(1, 0))   # False
```

행렬은 O(V^2) 메모리를 쓰지만 "간선이 있는가?"를 O(1)에 답합니다. 정점 수가 작고 그래프가 조밀할 때 유리합니다.

### 3단계: 너비 우선 탐색 - 최단 경로

```python
from collections import deque

def bfs_path(g, start, target):
    visited = {start}
    prev = {start: None}
    queue = deque([start])
    while queue:
        u = queue.popleft()
        if u == target:
            path = []
            while u is not None:
                path.append(u)
                u = prev[u]
            return list(reversed(path))
        for v, _ in g.neighbors(u):
            if v not in visited:
                visited.add(v)
                prev[v] = u
                queue.append(v)
    return []

path = bfs_path(service_graph, "api-gateway", "warehouse-db")
print(path)
# ['api-gateway', 'catalog-service', 'inventory-service', 'warehouse-db']
print(f"hop count: {len(path) - 1}")   # 3
```

BFS는 가까운 정점을 먼저 방문하므로 비가중치 그래프에서 자연스럽게 최단 경로를 구합니다.

### 4단계: 깊이 우선 탐색 - 재귀 기반 순회

```python
def dfs(g, start, visited=None, order=None):
    if visited is None:
        visited = set()
    if order is None:
        order = []
    visited.add(start)
    order.append(start)
    for v, _ in g.neighbors(start):
        if v not in visited:
            dfs(g, v, visited, order)
    return order

print(dfs(service_graph, "api-gateway"))
# ['api-gateway', 'auth-service', 'user-db', 'catalog-service',
#  'inventory-service', 'warehouse-db', 'cache']
```

DFS는 한 갈래를 끝까지 파고들었다가 되돌아옵니다. 사이클 검출, 위상 정렬, 연결 요소 탐색의 기본 도구입니다.

### 5단계: 의존성 그래프의 사이클 검출

```python
def has_cycle_directed(g):
    visited = set()
    active = set()

    def walk(node):
        visited.add(node)
        active.add(node)
        for neighbor, _ in g.neighbors(node):
            if neighbor not in visited and walk(neighbor):
                return True
            if neighbor in active:
                return True
        active.remove(node)
        return False

    return any(node not in visited and walk(node) for node in g)

dependency_graph = Graph(directed=True)
for u, v in [
    ("web", "auth"),
    ("auth", "payments"),
    ("payments", "ledger"),
    ("ledger", "web"),   # 순환 의존성!
]:
    dependency_graph.add_edge(u, v)

cycle_found = has_cycle_directed(dependency_graph)
print(cycle_found)                                   # True
print(f"topological traversal possible: {not cycle_found}")  # False
```

역방향 간선이 생기면 의존성 그래프를 위상 정렬할 수 없습니다. `active` 집합이 현재 재귀 스택을 추적하는 핵심입니다.

## 이 코드에서 주목할 점

- 희소 그래프는 인접 리스트, 조밀 그래프는 인접 행렬이 잘 맞습니다.
- BFS와 DFS는 순회 뼈대가 비슷하고 queue냐 재귀/스택이냐가 동작을 가릅니다.
- 방향 그래프의 사이클 검출은 현재 재귀 스택을 함께 추적해야 정확합니다.
- 그래프는 트리의 일반화이자 관계 모델링의 기본 어휘입니다.

## 인접 리스트 vs 인접 행렬 비교

| 항목 | 인접 리스트 | 인접 행렬 |
| --- | --- | --- |
| 메모리 | O(V + E) | O(V²) |
| 간선 존재 확인 | O(차수) | O(1) |
| 이웃 노드 순회 | O(차수) | O(V) |
| 희소 그래프 | 효율적 | 메모리 낭비 |
| 조밀 그래프 | 오버헤드 있음 | 효율적 |
| 가중치 표현 | (노드, 가중치) 튜플 | 행렬 값 |
| 적합한 상황 | 소셜 네트워크, 의존성 | 플로이드-워셜, 작은 조밀 그래프 |

## 디버깅 시나리오

### 시나리오 1: visited 표시 타이밍이 늦어서 노드를 중복 방문

**증상:** BFS가 같은 노드를 여러 번 방문하거나, 예상보다 많은 경로를 탐색합니다.

```python
# 버그: dequeue 후에 visited 표시
def bfs_buggy(g, start):
    queue = deque([start])
    visited = set()
    order = []
    while queue:
        u = queue.popleft()
        if u in visited:   # 이미 처리된 노드 체크
            continue
        visited.add(u)     # 너무 늦음: enqueue 시점이 아닌 dequeue 시점에 표시
        order.append(u)
        for v, _ in g.neighbors(u):
            queue.append(v)
    return order
```

**해결:** enqueue 시점에 바로 visited 표시합니다.

```python
def bfs_correct(g, start):
    visited = {start}          # enqueue 시점에 표시
    queue = deque([start])
    order = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v, _ in g.neighbors(u):
            if v not in visited:
                visited.add(v)    # 큐에 넣으면서 바로 표시
                queue.append(v)
    return order
```

### 시나리오 2: 무방향 그래프에서 방향 오류

**증상:** 무방향 그래프인데 한쪽 방향으로만 이동 가능합니다.

```python
# 버그: directed=True인데 무방향으로 쓰려 함
wrong_graph = Graph(directed=True)
wrong_graph.add_edge("A", "B")
print(list(wrong_graph.neighbors("B")))  # [] — B에서 A로 못 감

# 해결
undirected = Graph(directed=False)
undirected.add_edge("A", "B")
print(list(undirected.neighbors("B")))   # [('A', 1)] — 양방향
```

**원인:** `add_edge`가 반대 방향도 추가하지 않았습니다. `directed=False`를 명시하거나, 반대 간선을 수동으로 추가합니다.

### 시나리오 3: 큰 그래프에서 재귀 DFS가 RecursionError

**증상:** 노드가 수만 개인 그래프에서 DFS를 재귀로 실행하면 `RecursionError`가 납니다.

```python
import sys
# sys.setrecursionlimit(100000)  # 임시방편 — 메모리 위험

# 근본 해결: 명시적 스택을 사용한 반복 DFS
def dfs_iterative(g, start):
    visited = set()
    stack = [start]
    order = []
    while stack:
        u = stack.pop()
        if u in visited:
            continue
        visited.add(u)
        order.append(u)
        for v, _ in reversed(list(g.neighbors(u))):
            if v not in visited:
                stack.append(v)
    return order
```

**원인:** 파이썬의 기본 재귀 한도는 1000입니다. 깊이가 깊은 그래프는 반복 방식을 써야 합니다.

## 자주 하는 실수

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 방향 여부를 코드에 드러내지 않음 | 알고리즘 결과가 틀어짐 | directed/undirected를 명시합니다 |
| visited 집합을 빠뜨림 | 무한 순회 발생 | enqueue/push 시점에 바로 표시합니다 |
| 가중치를 무시하고 BFS를 사용함 | 잘못된 최단 경로가 나옴 | 가중치가 있으면 다익스트라를 고려합니다 |
| 큰 V에서 인접 행렬을 고름 | 메모리가 폭발함 | 희소 그래프에는 인접 리스트를 씁니다 |
| 깊은 그래프에 재귀 DFS만 사용함 | `RecursionError` 가능 | 명시적 스택으로 전환합니다 |

## 실무에서는 이렇게 쓰입니다

- 소셜 네트워크는 친구 관계, 영향력, 커뮤니티 탐지를 그래프로 모델링합니다.
- 지도와 내비게이션은 도로망 위에서 다익스트라와 A*를 실행합니다.
- npm, pip 같은 의존성 관리자는 위상 정렬로 빌드 순서를 결정합니다.
- 추천 시스템은 그래프 관계와 임베딩을 함께 사용합니다.
- 분산 시스템의 토폴로지, 라우팅, 일관성 분석도 그래프 알고리즘과 맞닿아 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 먼저 "이게 그래프 문제인가?"를 묻습니다. 정점, 간선, 관계라는 언어로 다시 표현할 수 있으면 BFS, DFS, 다익스트라, 위상 정렬 같은 검증된 해법을 곧바로 떠올릴 수 있기 때문입니다.

또한 NetworkX, igraph, Neo4j 같은 도구를 알고 적절할 때 사용합니다. 하지만 기본 알고리즘은 몸에 익혀 두어야, 라이브러리가 내부에서 무엇을 하는지 이해하고 성능·제약을 예측할 수 있습니다.

## 운영 체크리스트

- [ ] 정점, 간선, 차수, 경로를 정확히 설명할 수 있습니다
- [ ] 인접 리스트와 인접 행렬의 시간·메모리 차이를 알고 있습니다
- [ ] 방향/무방향, 가중치/비가중치를 구분할 수 있습니다
- [ ] BFS와 DFS의 구현 차이를 설명할 수 있습니다
- [ ] 트리가 그래프의 특수한 경우라는 점을 이해했습니다

## 연습 문제

1. `Graph`에 `bfs_path(start, target)` 메서드를 추가해 실제 경로를 반환하도록 만들어 보세요. 각 정점의 predecessor를 기록하면 됩니다.

2. 방향 그래프에 대해 위상 정렬을 두 방식 — DFS 후위 순서 역순, Kahn 알고리즘 — 으로 각각 구현해 보고 차이를 비교해 보세요.

3. `heapq`를 사용해 가중치 그래프에서 다익스트라 알고리즘을 구현해 보세요. 왜 음수 간선이 있으면 이 방식이 깨지는지도 설명해 보세요.

## 정리 및 다음 단계

그래프는 정점과 간선으로 임의의 관계를 표현하는 가장 일반적이고 강력한 모델입니다. 인접 리스트와 인접 행렬의 트레이드오프를 이해하고, 방향성·가중치·연결성을 정확히 다뤄야 합니다. BFS와 DFS는 모든 그래프 알고리즘의 출발점이며, 둘의 차이도 결국 자료구조 선택으로 귀결됩니다.

다음 글에서는 시리즈를 마무리하며, 지금까지 본 자료구조들을 어떤 상황에서 어떻게 선택할지 실전 관점으로 정리합니다.

## 처음 질문으로 돌아가기

- **정점, 간선, 차수, 경로 같은 그래프 용어를 어떻게 정확히 쓸까요?**
  - 정점은 노드, 간선은 두 노드를 잇는 연결, 차수는 한 정점의 간선 수, 경로는 간선으로 이어진 정점들의 순서입니다. 방향이 있으면 진입/진출 차수로 구분합니다.
- **인접 리스트와 인접 행렬은 어떤 트레이드오프를 가질까요?**
  - 인접 리스트는 O(V+E) 메모리로 희소 그래프에 효율적이고, 인접 행렬은 O(V²) 메모리를 쓰지만 간선 존재 여부를 O(1)에 확인합니다.
- **방향 그래프와 무방향 그래프, 가중치 그래프와 비가중치 그래프는 무엇이 다를까요?**
  - 방향 그래프는 간선에 방향이 있어 A→B와 B→A가 독립적이고, 무방향은 양방향입니다. 가중치는 간선에 비용·거리·용량을 부여하며, 최단 경로 알고리즘 선택에 영향을 줍니다.

<!-- toc:begin -->
## 시리즈 목차

- [Data Structures 101 (1/10): 자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [Data Structures 101 (2/10): 배열과 동적 배열](./02-arrays-and-dynamic-arrays.md)
- [Data Structures 101 (3/10): 연결 리스트](./03-linked-lists.md)
- [Data Structures 101 (4/10): 스택과 큐](./04-stacks-and-queues.md)
- [Data Structures 101 (5/10): 해시 테이블](./05-hash-tables.md)
- [Data Structures 101 (6/10): 트리](./06-trees.md)
- [Data Structures 101 (7/10): 이진 탐색 트리](./07-binary-search-trees.md)
- [Data Structures 101 (8/10): 힙](./08-heaps.md)
- **Data Structures 101 (9/10): 그래프 (현재 글)**
- [자료구조 선택 기준](./10-choosing-data-structures.md)

<!-- toc:end -->

## 참고 자료

- [Data Structures 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/data-structures-101/ko)

- [Open Data Structures — Graphs](https://opendatastructures.org/ods-python/12_Graphs.html)
- [NetworkX documentation](https://networkx.org/)
- [Wikipedia — Graph (abstract data type)](https://en.wikipedia.org/wiki/Graph_(abstract_data_type))
- [Sedgewick & Wayne — Algorithms 4ed, Graph chapters](https://algs4.cs.princeton.edu/40graphs/)

Tags: Computer Science, 자료구조, 그래프, 인접 리스트, 인접 행렬, 그래프 탐색
