---
series: algorithms-101
episode: 8
title: 그래프 알고리즘
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - 알고리즘
  - 그래프
  - BFS
  - 다익스트라
  - 최소 신장 트리
seo_description: 그래프 표현, BFS와 DFS의 선택 기준, 다익스트라 최단 경로, 그리고 Kruskal·Prim 기반 MST를 정리합니다.
last_reviewed: '2026-05-12'
---

# 그래프 알고리즘

도로망, 소셜 네트워크, 의존성 그래프는 전혀 다른 문제처럼 보이는데 왜 같은 알고리즘으로 풀릴까요? 이 글은 Algorithms 101 시리즈의 여덟 번째 글입니다. 여기서는 그래프 표현, 순회, 최단 경로, 최소 신장 트리를 정리합니다.

## 이 글에서 다룰 문제

- 인접 리스트와 인접 행렬은 어떤 트레이드오프를 가질까요?
- BFS와 DFS는 각각 언제 써야 할까요?
- 다익스트라는 어떻게 동작하고 어떻게 구현할까요?
- Kruskal과 Prim은 최소 신장 트리를 어떻게 구할까요?

## 왜 중요한가

실무 문제는 결국 그래프로 환원되는 경우가 많습니다. 마이크로서비스 호출 의존성, 빌드 태스크 그래프, 추천 시스템의 사용자-아이템 이분 그래프, 라우팅 도로망이 모두 그 예입니다. 그래프 알고리즘을 모르면 이런 시스템의 핵심을 다루기 어렵습니다.

> 그래프는 시스템 사고의 공용 언어입니다.

## 한눈에 보는 개념

> 그래프는 V개의 노드와 E개의 간선으로 구성됩니다. 인접 리스트는 O(V+E) 메모리를 써서 희소 그래프에 적합하고, 인접 행렬은 O(V²) 메모리를 쓰지만 간선 조회가 O(1)이라 밀집 그래프에 적합합니다. BFS는 큐를 사용해 가중치 없는 최단 거리를 O(V+E)에 구합니다. DFS는 스택이나 재귀를 사용해 연결성, 사이클, 위상 정렬에 쓰입니다. 다익스트라는 음이 아닌 가중치 최단 경로를 푸는 그리디 + 우선순위 큐 알고리즘이고, MST의 대표는 Kruskal과 Prim입니다.

```text
Graph representations
    Adjacency list   memory O(V+E), good for sparse graphs
    Adjacency matrix memory O(V^2),  O(1) edge lookup, good for dense graphs

Core traversals
    BFS  queue   unweighted shortest paths, layered exploration
    DFS  stack   connectivity, cycles, topological sort

Weighted graphs
    Dijkstra   non-negative shortest paths   O((V+E) log V)
    MST        cheapest tree connecting all  Kruskal/Prim
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| 노드/간선 | 객체와 그 관계 |
| 인접 리스트 | 각 노드의 이웃 목록을 저장하는 표현 |
| BFS/DFS | 너비 우선 탐색 / 깊이 우선 탐색 |
| 다익스트라 | 음이 아닌 가중치 그래프의 최단 경로 알고리즘 |
| MST | 모든 노드를 최소 비용으로 연결하는 부분 그래프 |

## Before / After

**Before — 희소 그래프를 인접 행렬로 표현:**

```python
# V=10000, E=30000 sparse graph as a matrix
adj = [[0] * 10000 for _ in range(10000)]   # 100 million cells, mostly zero
```

**After — 인접 리스트 사용:**

```python
from collections import defaultdict
adj = defaultdict(list)
adj[0].append(1)
adj[1].append(2)
# memory O(V+E)
```

## 단계별로 따라가기

### 1단계: 인접 리스트와 BFS

```python
from collections import deque, defaultdict

def bfs(adj, start):
    visited = {start: 0}
    q = deque([start])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in visited:
                visited[v] = visited[u] + 1
                q.append(v)
    return visited

adj = defaultdict(list)
edges = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4)]
for a, b in edges:
    adj[a].append(b); adj[b].append(a)

print(bfs(adj, 0))   # {0: 0, 1: 1, 2: 1, 3: 2, 4: 3}
```

BFS는 가중치가 없는 그래프의 최단 거리를 자연스럽게 반환합니다. 큐는 양끝 O(1)을 보장하는 `deque`를 쓰는 것이 기본입니다.

### 2단계: DFS와 위상 정렬

```python
def topological_sort(n, edges):
    adj = defaultdict(list)
    indeg = [0] * n
    for u, v in edges:
        adj[u].append(v)
        indeg[v] += 1
    q = deque([i for i in range(n) if indeg[i] == 0])
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return order if len(order) == n else None   # None means a cycle exists

# A -> B, A -> C, B -> D, C -> D
print(topological_sort(4, [(0, 1), (0, 2), (1, 3), (2, 3)]))   # [0, 1, 2, 3]
```

빌드 시스템 실행 순서와 선수 과목 배치는 전형적인 위상 정렬 문제입니다.

### 3단계: 우선순위 큐 기반 다익스트라

```python
import heapq

def dijkstra(n, edges, start):
    adj = defaultdict(list)
    for u, v, w in edges:
        adj[u].append((v, w)); adj[v].append((u, w))
    dist = [float('inf')] * n
    dist[start] = 0
    pq = [(0, start)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist

edges = [(0, 1, 4), (0, 2, 1), (2, 1, 2), (1, 3, 1), (2, 3, 5)]
print(dijkstra(4, edges, 0))   # [0, 3, 1, 4]
```

가중치가 음수가 아니면 다익스트라가 표준 선택입니다. 음수 가중치가 보이면 Bellman-Ford나 Johnson을 떠올려야 합니다.

### 4단계: Union-Find를 쓰는 Kruskal MST

```python
class DSU:
    def __init__(self, n):
        self.p = list(range(n))
        self.r = [0] * n
    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.r[ra] < self.r[rb]:
            ra, rb = rb, ra
        self.p[rb] = ra
        if self.r[ra] == self.r[rb]:
            self.r[ra] += 1
        return True

def kruskal(n, edges):
    edges = sorted(edges, key=lambda e: e[2])
    dsu = DSU(n)
    total = 0
    for u, v, w in edges:
        if dsu.union(u, v):
            total += w
    return total

print(kruskal(4, [(0, 1, 1), (1, 2, 2), (0, 2, 4), (2, 3, 3)]))   # 6
```

가장 가벼운 간선부터 보되, 사이클을 만들지 않을 때만 채택합니다. 그리디와 Union-Find의 가장 고전적인 결합입니다.

### 5단계: 실전 예시 — 도시 연결 최소 비용

```python
roads = [
    (0, 1, 10), (0, 2, 6), (0, 3, 5),
    (1, 3, 15), (2, 3, 4),
]
print("MST cost:", kruskal(4, roads))   # 19 (e.g. 5 + 6 + 4 + ... )
```

MST는 네트워크 설계, 클러스터 거리 분석, 회로 배선처럼 "모두 연결하되 가장 싸게"라는 문제에 그대로 대응합니다.

## 이 글에서 먼저 가져갈 점

- 그래프 표현 선택이 메모리와 시간의 대부분을 결정합니다.
- BFS는 큐, DFS는 스택이라는 도구 차이가 결과 차이로 이어집니다.
- 다익스트라의 핵심은 우선순위 큐와 오래된 거리 무시 검사입니다.
- Union-Find는 연결성 문제의 보편 도구입니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 희소 그래프에 인접 행렬 사용 | OOM | 인접 리스트로 바꿉니다 |
| 음수 가중치에 다익스트라 적용 | 오답 | Bellman-Ford 등으로 전환합니다 |
| 가중치가 있는데 BFS 거리 사용 | 오답 | 가중치가 있으면 다익스트라를 씁니다 |
| Union-Find에 경로 압축 누락 | `find`가 느려짐 | path compression + union-by-rank를 넣습니다 |
| 사이클 그래프에 위상 정렬 적용 후 예외 처리 누락 | 잘못된 가정 | 결과 길이로 사이클을 확인합니다 |

## 실무에서는 이렇게 쓰입니다

- 빌드 시스템 태스크 의존성 분석
- 마이크로서비스 호출 그래프 진단
- 지도 앱 최단 경로 계산
- 추천 시스템의 그래프 임베딩
- 회로 배선과 네트워크 설계

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 먼저 "이 문제를 그래프로 볼 수 있는가"를 묻습니다. 무엇이 노드이고 무엇이 간선인지 정의하는 순간 풀이의 90%가 끝나는 경우가 많습니다. 프레이밍이 맞으면 표준 알고리즘을 바로 적용할 수 있습니다.

또한 처음부터 V와 E의 크기, 희소성, 가중치 분포를 추정합니다. 같은 문제라도 V=10^3과 V=10^7은 완전히 다른 표현과 도구를 요구하기 때문입니다.

## 체크리스트

- [ ] 인접 리스트와 인접 행렬의 트레이드오프를 설명할 수 있는가
- [ ] BFS와 DFS의 사용처를 구분할 수 있는가
- [ ] 다익스트라를 한 문장으로 설명할 수 있는가
- [ ] 최소 신장 트리 알고리즘을 하나 이상 구현할 수 있는가
- [ ] 새로운 문제를 그래프로 환원하는 감각이 있는가

## 연습 문제

1. 무방향 그래프에서 두 노드 사이의 서로 다른 최단 경로 개수를 세는 BFS 변형을 작성해 보세요.

2. 사이클이 있을 수도 있는 방향 그래프에 대해 위상 정렬 가능 여부를 판별하고, 가능하면 하나의 순서를 출력해 보세요.

3. 음이 아닌 가중치 그래프에서 다익스트라를 실행한 뒤, 시작점 기준 최단 경로 트리를 부모 포인터 형태로 출력해 보세요.

## 정리 및 다음 단계

그래프 알고리즘은 다양한 시스템 문제를 노드와 간선이라는 단순한 언어로 표현하게 해 줍니다. 표현, 순회, 최단 경로, MST만 익혀도 실무의 많은 문제를 다룰 수 있습니다. 그다음에는 flow, SCC, matching 같은 고급 주제로 자연스럽게 확장됩니다.

다음 글에서는 문자열 알고리즘 기초를 다룹니다. 단순 매칭의 비용, KMP의 실패 함수, 트라이, 그리고 정규식 비용 감각까지 연결해 보겠습니다.

<!-- toc:begin -->
- [알고리즘이란 무엇인가?](./01-what-is-an-algorithm.md)
- [시간 복잡도와 공간 복잡도](./02-time-and-space-complexity.md)
- [탐색 알고리즘](./03-search-algorithms.md)
- [정렬 알고리즘](./04-sorting-algorithms.md)
- [재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- [동적 계획법](./06-dynamic-programming.md)
- [그리디 알고리즘](./07-greedy-algorithms.md)
- **그래프 알고리즘 (현재 글)**
- 문자열 알고리즘 기초 (예정)
- 알고리즘 문제 풀이 전략 (예정)
<!-- toc:end -->

## 참고 자료

- [Python `heapq` documentation](https://docs.python.org/3/library/heapq.html)
- [Wikipedia — Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Sedgewick & Wayne — Algorithms 4ed, Chapter 4](https://algs4.cs.princeton.edu/40graphs/)
- [CLRS — Introduction to Algorithms, Chapters 22-24](https://mitpress.mit.edu/books/introduction-algorithms-third-edition)

Tags: Computer Science, 알고리즘, 그래프, BFS, 다익스트라, 최소 신장 트리
