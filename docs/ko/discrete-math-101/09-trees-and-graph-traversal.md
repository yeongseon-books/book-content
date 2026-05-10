---
series: discrete-math-101
episode: 9
title: 트리와 그래프 탐색
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
  - 이산수학
  - 트리
  - BFS
  - DFS
  - 신장 트리
seo_description: 트리의 정의, BFS와 DFS 탐색, 신장 트리와 최소 신장 트리(MST)의 개념을 코드와 함께 정리합니다.
last_reviewed: '2026-05-04'
---

# 트리와 그래프 탐색

> Discrete Math 101 시리즈 (9/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 그래프 위에서 "어디부터 어디까지 갈 수 있는가", "최소 비용으로 모두 연결하려면 어떻게 해야 하는가"를 어떻게 답할까요?

> 트리(tree)는 사이클이 없는 연결 그래프이며, 그래프 알고리즘에서 가장 자주 등장하는 부분 구조입니다. 그래프를 탐색하는 두 가지 기본 방법인 너비 우선 탐색(BFS)과 깊이 우선 탐색(DFS), 그리고 신장 트리와 최소 신장 트리(MST)의 개념을 코드와 함께 살펴봅니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 트리의 정의와 성질 (V-1 = E, 유일 경로)
- BFS — 큐 기반 너비 우선 탐색
- DFS — 스택/재귀 기반 깊이 우선 탐색
- 신장 트리와 최소 신장 트리(MST)의 직관

## 왜 중요한가

파일 시스템, DOM, 컴파일러 AST, 데이터베이스 인덱스 — 거의 모든 시스템에 트리가 숨어 있습니다. BFS와 DFS는 그래프 알고리즘의 출발점이며, 최단 경로·사이클 검사·위상 정렬·MST 등 수많은 문제의 기반입니다.

> 트리 = 가장 단순한 비자명 그래프. 탐색 = 그래프 알고리즘의 기본 동작.

## 개념 한눈에 보기

> 트리: 사이클 없는 연결 무방향 그래프. n개 정점이면 정확히 n-1개의 간선. 임의의 두 정점 사이에 경로가 정확히 하나.

```text
     트리                    BFS 순서             DFS 순서
       1                    1 → 2 → 3            1 → 2 → 4
      / \                   → 4 → 5 → 6          → 5 → 3 → 6
     2   3                  (레벨 단위)          (한 가지 끝까지)
    / \   \
   4   5   6
```

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| 트리(tree) | 사이클 없는 연결 그래프 |
| 루트(root) | 트리의 시작 정점 (선택적) |
| 리프(leaf) | 차수 1인 정점 |
| 신장 트리(spanning tree) | 모든 정점을 포함하는 부분 트리 |
| MST | 가중치 합이 최소인 신장 트리 |

## Before / After

**Before — 모든 노드를 개별적으로 확인:**

```python
# 친구의 친구를 손으로 검색 — 깊이마다 중복 코드
def friends_of_friends(person):
    result = set()
    for f in friends_of(person):
        for ff in friends_of(f):
            result.add(ff)
    return result
```

**After — BFS로 임의 거리 탐색:**

```python
from collections import deque


def reachable_within(graph, start, max_distance):
    """start로부터 거리 max_distance 이내의 모든 정점."""
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

## 실습: 단계별로 따라하기

### 1단계: 트리의 정의와 검증

```python
from collections import defaultdict


def is_tree(edges: list, n_nodes: int) -> bool:
    """무방향 그래프가 트리인지 검사 — 간선 수와 연결성 확인."""
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
print(f"트리인가: {is_tree(tree_edges, 6)}")
```

트리의 핵심 성질: n개 정점이면 정확히 n-1개의 간선이며, 임의의 간선을 제거하면 연결이 끊어집니다.

### 2단계: BFS — 너비 우선 탐색

```python
def bfs(graph: dict, start) -> dict:
    """start로부터 모든 정점까지의 최소 간선 수 (가중치 1 가정)."""
    distances = {start: 0}
    queue = deque([start])
    while queue:
        v = queue.popleft()
        for u in graph[v]:
            if u not in distances:
                distances[u] = distances[v] + 1
                queue.append(u)
    return distances


graph = {1: [2, 3], 2: [1, 4, 5], 3: [1, 6], 4: [2], 5: [2], 6: [3]}
print(f"1로부터 거리: {bfs(graph, 1)}")
```

BFS는 큐를 사용해 가까운 정점부터 방문합니다. 가중치가 모두 같다면 BFS가 최단 경로를 찾습니다.

### 3단계: DFS — 깊이 우선 탐색

```python
def dfs_recursive(graph: dict, start, visited=None) -> list:
    """재귀 DFS — 방문 순서를 반환."""
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
    """스택 기반 DFS — 깊이가 매우 큰 경우 안전."""
    visited, order, stack = set(), [], [start]
    while stack:
        v = stack.pop()
        if v in visited:
            continue
        visited.add(v); order.append(v)
        stack.extend(sorted(graph[v], reverse=True))
    return order


print(f"DFS 재귀: {dfs_recursive(graph, 1)}")
print(f"DFS 반복: {dfs_iterative(graph, 1)}")
```

DFS는 한 경로를 끝까지 탐색한 뒤 백트래킹합니다. 사이클 검사, 위상 정렬, 강한 연결 요소 검출 등에 사용됩니다.

### 4단계: 신장 트리와 BFS/DFS의 관계

```python
def spanning_tree_bfs(graph: dict, start) -> list:
    """BFS로 신장 트리 추출."""
    visited = {start}
    tree = []
    queue = deque([start])
    while queue:
        v = queue.popleft()
        for u in graph[v]:
            if u not in visited:
                visited.add(u)
                tree.append((v, u))
                queue.append(u)
    return tree


print(f"신장 트리(BFS): {spanning_tree_bfs(graph, 1)}")
```

BFS와 DFS는 모두 그래프의 신장 트리를 구성합니다. 신장 트리는 정점을 모두 포함하면서 사이클이 없는 부분 그래프입니다.

### 5단계: 최소 신장 트리(MST) — Kruskal

```python
def kruskal_mst(n_nodes: int, weighted_edges: list) -> list:
    """가중치 합이 최소인 신장 트리 — Union-Find 사용."""
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
print(f"MST: {kruskal_mst(4, edges)}")
```

Kruskal은 간선을 가중치 순으로 정렬하고, 사이클을 만들지 않는 간선만 선택합니다. 통신망 설계, 클러스터링, 회로 배선 등에 사용됩니다.

## 이 코드에서 주목할 점

- BFS와 DFS는 데이터 구조(큐 vs 스택)만 다를 뿐 골격은 같음
- 트리는 V-1개의 간선이라는 단순한 성질로 검증 가능
- BFS의 신장 트리는 최단 경로 트리(가중치 동일 시)
- MST는 그리디 알고리즘이 정답을 보장하는 드문 경우

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 방문 표시 누락 | 무한 루프 | 재귀 진입 즉시 visited에 추가 |
| 큐와 스택 혼동 | BFS인데 DFS처럼 동작 | deque의 popleft vs pop 확인 |
| 재귀 깊이 초과 | RecursionError | 큰 그래프는 반복 DFS |
| 가중치 무시한 BFS | 최단 경로 오답 | 가중치 있으면 Dijkstra |
| MST에 사이클 미검사 | 결과가 트리가 아님 | Union-Find로 사이클 차단 |

## 실무에서는 이렇게 쓰입니다

- 웹 크롤러의 페이지 탐색 (BFS, 깊이 제한)
- 컴파일러의 AST 순회 (DFS, post-order)
- 게임 AI의 상태 공간 탐색 (BFS·DFS·A*)
- 통신망의 최소 비용 설계 (MST)
- React의 가상 DOM diff (트리 비교)

## 시니어 엔지니어는 이렇게 생각합니다

시니어는 그래프 문제를 만나면 가장 먼저 "이게 BFS로 풀리는가, DFS로 풀리는가"를 구분합니다. 최단 경로·레벨 단위 처리는 BFS, 경로 탐색·위상 정렬·사이클 검사는 DFS입니다. 또한 메모리 한계를 의식해 큰 그래프에서는 반복 DFS와 명시적 스택을 사용합니다.

## 체크리스트

- [ ] 트리의 정의와 V-1 = E 성질을 안다
- [ ] BFS와 DFS의 차이를 데이터 구조로 설명할 수 있다
- [ ] BFS가 최단 경로를 찾는 조건을 안다
- [ ] 신장 트리와 MST의 차이를 이해했다
- [ ] Kruskal에서 Union-Find의 역할을 안다

## 연습 문제

1. 정점 5개의 트리에서 간선 수와 리프의 최소 개수를 각각 구하세요.

2. 미로(2D 격자)에서 출발점부터 도착점까지 최단 경로를 BFS로 구하는 코드를 작성하세요.

3. 6개 도시와 임의의 가중치를 가정하고, Kruskal로 최소 신장 트리를 손으로 구해보세요.

## 정리 및 다음 단계

트리는 사이클 없는 연결 그래프이며, BFS와 DFS는 그래프 위의 가장 기본적인 탐색 알고리즘입니다. MST는 가중치를 가진 그래프에서 최소 비용으로 모두 연결하는 부분 트리입니다.

다음 글에서는 지금까지 배운 이산수학의 모든 주제가 알고리즘 분석과 실무에서 어떻게 연결되는지 살펴봅니다.

<!-- toc:begin -->
- [이산수학이란 무엇인가?](./01-what-is-discrete-math.md)
- [명제와 논리](./02-propositions-and-logic.md)
- [집합과 함수](./03-sets-and-functions.md)
- [관계와 동치관계](./04-relations-and-equivalence.md)
- [증명 방법](./05-proof-techniques.md)
- [수열과 점화식](./06-sequences-and-recurrence.md)
- [조합과 경우의 수](./07-combinatorics.md)
- [그래프 이론 기초](./08-graph-theory-basics.md)
- **트리와 그래프 탐색 (현재 글)**
- 알고리즘과 이산수학의 연결 (예정)
<!-- toc:end -->

## 참고 자료

- [Discrete Mathematics and Its Applications — Kenneth Rosen, Chapter 11](https://www.mheducation.com/highered/product/discrete-mathematics-its-applications-rosen/M9781259676512.html)
- [Wikipedia — Tree (graph theory)](https://en.wikipedia.org/wiki/Tree_(graph_theory))
- [Wikipedia — Minimum Spanning Tree](https://en.wikipedia.org/wiki/Minimum_spanning_tree)
- [Algorithms — Sedgewick & Wayne, Chapter 4.3](https://algs4.cs.princeton.edu/43mst/)
