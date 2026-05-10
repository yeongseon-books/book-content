---
series: discrete-math-101
episode: 8
title: 그래프 이론 기초
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
  - 그래프 이론
  - 정점과 간선
  - 인접 리스트
  - 네트워크
seo_description: 그래프의 정의, 표현 방법, 차수, 경로, 연결성 등 그래프 이론의 핵심 기초와 실무 응용을 다룹니다.
last_reviewed: '2026-05-04'
---

# 그래프 이론 기초

> Discrete Math 101 시리즈 (8/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 소셜 네트워크, 도로망, 인터넷, 의존성 — 이렇게 다양한 시스템을 하나의 수학 구조로 표현할 수 있을까요?

> 그래프(graph)는 정점(vertex)과 간선(edge)의 집합으로 구성된 가장 일반적인 관계 구조입니다. 단순한 정의에서 무한히 풍부한 응용이 나옵니다 — 라우팅, 추천, 의존성 해석, 회로 설계, 게임 AI까지. 이 글에서는 그래프의 정의, 표현 방법, 차수, 경로, 연결성, 그리고 특수 그래프(완전·이분·DAG)를 살펴봅니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 그래프의 정의와 종류 (무방향·방향·가중)
- 인접 리스트와 인접 행렬 표현
- 차수, 경로, 사이클, 연결성
- 완전 그래프, 이분 그래프, DAG

## 왜 중요한가

내비게이션의 최단 경로, 인스타그램의 팔로우 추천, npm의 의존성 해석, 컴파일러의 데이터 흐름 분석 — 이 모든 문제는 그래프 알고리즘으로 해결됩니다. 그래프 이론을 모르면 이런 도구의 내부를 이해할 수 없습니다.

> 그래프 = 관계가 있는 모든 것을 모델링하는 보편 언어

## 개념 한눈에 보기

> 그래프 G = (V, E). V는 정점, E는 간선. 방향성·가중치·중복 여부에 따라 다양한 변종이 존재.

```text
   무방향 그래프              방향 그래프 (DAG)
       A                          A
      / \                        / \
     B───C                      ↓   ↓
     │   │                      B → C
     D───E                          ↓
                                    D
   인접 리스트:              가중 그래프:
   A: [B, C]                  A ──5── B
   B: [A, D]                  │       │
   C: [A, E]                  3       2
                              │       │
                              C ──1── D
```

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| 정점(vertex/node) | 그래프의 기본 단위 |
| 간선(edge) | 두 정점을 연결 |
| 차수(degree) | 한 정점에 연결된 간선 수 |
| 경로(path) | 정점들을 잇는 간선 시퀀스 |
| 사이클(cycle) | 시작과 끝이 같은 경로 |

## Before / After

**Before — 데이터 구조로만 사고:**

```python
# 친구 관계를 리스트로 관리 — 검색 비효율
friends = [("alice", "bob"), ("bob", "carol"), ("alice", "carol")]


def is_friend(a, b):
    return (a, b) in friends or (b, a) in friends
```

**After — 그래프로 모델링:**

```python
# 인접 리스트 — O(1) 평균 조회, 풍부한 알고리즘 적용 가능
from collections import defaultdict

graph = defaultdict(set)


def add_edge(g, a, b):
    g[a].add(b); g[b].add(a)


def is_adjacent(g, a, b):
    return b in g[a]
```

## 실습: 단계별로 따라하기

### 1단계: 그래프 정의와 표현

```python
from collections import defaultdict


class Graph:
    def __init__(self, directed: bool = False):
        self.adj = defaultdict(set)
        self.directed = directed

    def add_node(self, v):
        _ = self.adj[v]

    def add_edge(self, u, v):
        self.adj[u].add(v)
        if not self.directed:
            self.adj[v].add(u)

    def neighbors(self, v):
        return self.adj[v]

    def nodes(self):
        return set(self.adj.keys())

    def edges(self):
        seen = set()
        for u in self.adj:
            for v in self.adj[u]:
                e = (u, v) if self.directed else tuple(sorted((u, v)))
                seen.add(e)
        return seen


g = Graph()
for u, v in [("A", "B"), ("B", "C"), ("A", "C"), ("C", "D")]:
    g.add_edge(u, v)

print(f"정점: {g.nodes()}")
print(f"간선: {g.edges()}")
```

### 2단계: 인접 리스트 vs 인접 행렬

```python
import numpy as np


def to_adjacency_matrix(g: Graph) -> tuple:
    nodes = sorted(g.nodes())
    n = len(nodes)
    idx = {v: i for i, v in enumerate(nodes)}
    M = np.zeros((n, n), dtype=int)
    for u, v in g.edges():
        M[idx[u]][idx[v]] = 1
        if not g.directed:
            M[idx[v]][idx[u]] = 1
    return nodes, M


nodes, M = to_adjacency_matrix(g)
print(f"노드 순서: {nodes}")
print(f"인접 행렬:\n{M}")
```

| 표현 | 공간 | 간선 검사 | 이웃 순회 |
| --- | --- | --- | --- |
| 인접 리스트 | O(V + E) | O(deg) | O(deg) |
| 인접 행렬 | O(V²) | O(1) | O(V) |

희소 그래프(간선이 적음)는 리스트, 밀집 그래프(간선이 많음)는 행렬이 유리합니다.

### 3단계: 차수와 핸드셰이킹 정리

```python
def degree(g: Graph, v) -> int:
    return len(g.adj[v])


total_degree = sum(degree(g, v) for v in g.nodes())
edge_count = len(g.edges())

# 핸드셰이킹 정리: Σ deg(v) = 2|E|
print(f"차수의 합 = {total_degree}, 2|E| = {2 * edge_count}")
assert total_degree == 2 * edge_count
```

핸드셰이킹 정리는 모든 간선이 두 정점에 기여한다는 직관입니다. 이로부터 "홀수 차수 정점은 짝수 개"라는 따름정리가 나옵니다.

### 4단계: 경로와 연결성

```python
from collections import deque


def has_path(g: Graph, start, target) -> bool:
    """BFS로 경로 존재 여부 확인 — O(V + E)"""
    visited = {start}
    queue = deque([start])
    while queue:
        v = queue.popleft()
        if v == target:
            return True
        for u in g.adj[v]:
            if u not in visited:
                visited.add(u); queue.append(u)
    return False


def connected_components(g: Graph) -> list:
    """연결 요소 (무방향 그래프 전용)"""
    visited = set()
    components = []
    for start in g.nodes():
        if start in visited:
            continue
        comp = set()
        queue = deque([start])
        while queue:
            v = queue.popleft()
            if v in comp:
                continue
            comp.add(v); visited.add(v)
            queue.extend(g.adj[v] - comp)
        components.append(comp)
    return components


print(f"A→D 경로 존재: {has_path(g, 'A', 'D')}")
print(f"연결 요소: {connected_components(g)}")
```

### 5단계: 특수 그래프

```python
from itertools import combinations


def is_complete(g: Graph) -> bool:
    """완전 그래프 K_n: 모든 쌍이 연결"""
    n = len(g.nodes())
    return len(g.edges()) == n * (n - 1) // 2


def is_bipartite(g: Graph) -> bool:
    """이분 그래프: 정점을 두 그룹으로 나눠 같은 그룹 내 간선 없음"""
    color = {}
    for start in g.nodes():
        if start in color:
            continue
        color[start] = 0
        queue = deque([start])
        while queue:
            v = queue.popleft()
            for u in g.adj[v]:
                if u not in color:
                    color[u] = 1 - color[v]
                    queue.append(u)
                elif color[u] == color[v]:
                    return False
    return True


k4 = Graph()
for u, v in combinations(["a", "b", "c", "d"], 2):
    k4.add_edge(u, v)
print(f"K4는 완전 그래프: {is_complete(k4)}")

bipart = Graph()
for u, v in [("u1", "v1"), ("u1", "v2"), ("u2", "v1")]:
    bipart.add_edge(u, v)
print(f"이분 그래프: {is_bipartite(bipart)}")
```

DAG(directed acyclic graph)는 사이클 없는 방향 그래프이며, 4장의 위상 정렬이 적용됩니다. 이분 그래프는 매칭 문제(예: 배정 문제)의 모델입니다.

## 이 코드에서 주목할 점

- 그래프는 정점·간선이라는 단순 정의에서 무한한 응용이 나옴
- 인접 리스트와 인접 행렬은 트레이드오프 관계
- 핸드셰이킹 정리는 모든 무방향 그래프의 기본 항등식
- 완전·이분·DAG는 알고리즘 설계의 표준 분류

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 무방향/방향 혼동 | 간선 한 번만 추가 | 무방향은 양쪽 모두 추가 |
| 자기 루프 처리 누락 | (v, v) 간선의 차수 +2 | 핸드셰이킹 정리 적용 시 주의 |
| 다중 간선 미처리 | set vs list 차이 | 단순 그래프 가정 시 set 사용 |
| 인접 행렬을 무조건 사용 | 희소 그래프에서 메모리 낭비 | E ≪ V²이면 리스트 |
| 사이클 검사 빠뜨림 | DAG 가정한 위상 정렬 무한 루프 | 사이클 검사 후 알고리즘 적용 |

## 실무에서는 이렇게 쓰입니다

- 소셜 네트워크의 친구 추천 (그래프 임베딩, 공통 이웃)
- 내비게이션의 최단 경로 (Dijkstra, A*)
- 패키지 매니저의 의존성 해석 (위상 정렬)
- 데이터베이스 쿼리 최적화 (조인 그래프)
- 추천 시스템의 그래프 신경망 (GNN)

## 시니어 엔지니어는 이렇게 생각합니다

시니어는 새로운 도메인을 만나면 "이게 그래프로 모델링되는가?"부터 묻습니다. 노드와 엣지로 표현되면 즉시 검증된 그래프 알고리즘 라이브러리를 적용할 수 있기 때문입니다. 또한 데이터 규모를 보고 인접 리스트와 인접 행렬을 신중히 선택합니다 — 이 선택이 메모리와 성능을 좌우합니다.

## 체크리스트

- [ ] 정점·간선·차수의 정의를 설명할 수 있는가
- [ ] 인접 리스트와 인접 행렬의 트레이드오프를 안다
- [ ] 핸드셰이킹 정리를 사용할 수 있는가
- [ ] 연결 요소를 BFS로 찾을 수 있는가
- [ ] 완전·이분·DAG의 차이를 이해했는가

## 연습 문제

1. 정점 6개의 무방향 그래프에서 가능한 최대 간선 수를 구하세요. 이는 어떤 그래프인가요?

2. 자신의 SNS 친구 관계를 인접 리스트로 표현하고, 자신을 포함한 연결 요소의 크기를 구하세요.

3. 핸드셰이킹 정리를 사용하여 "홀수 차수 정점의 개수는 항상 짝수"임을 증명하세요.

## 정리 및 다음 단계

그래프는 정점과 간선으로 관계를 표현하는 가장 일반적인 구조입니다. 표현 방법, 차수, 경로, 연결성, 특수 그래프의 분류는 모든 그래프 알고리즘의 출발점입니다.

다음 글에서는 그래프 위에서 가장 중요한 알고리즘 — 트리와 BFS·DFS 탐색 — 을 살펴봅니다.

<!-- toc:begin -->
- [이산수학이란 무엇인가?](./01-what-is-discrete-math.md)
- [명제와 논리](./02-propositions-and-logic.md)
- [집합과 함수](./03-sets-and-functions.md)
- [관계와 동치관계](./04-relations-and-equivalence.md)
- [증명 방법](./05-proof-techniques.md)
- [수열과 점화식](./06-sequences-and-recurrence.md)
- [조합과 경우의 수](./07-combinatorics.md)
- **그래프 이론 기초 (현재 글)**
- 트리와 그래프 탐색 (예정)
- 알고리즘과 이산수학의 연결 (예정)
<!-- toc:end -->

## 참고 자료

- [Discrete Mathematics and Its Applications — Kenneth Rosen, Chapter 10](https://www.mheducation.com/highered/product/discrete-mathematics-its-applications-rosen/M9781259676512.html)
- [Wikipedia — Graph Theory](https://en.wikipedia.org/wiki/Graph_theory)
- [NetworkX Documentation](https://networkx.org/documentation/stable/)
- [Algorithms — Sedgewick & Wayne, Chapter 4](https://algs4.cs.princeton.edu/40graphs/)

Tags: Computer Science, 이산수학, 그래프 이론, 정점과 간선, 인접 리스트, 네트워크
