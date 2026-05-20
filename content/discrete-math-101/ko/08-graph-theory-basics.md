---
series: discrete-math-101
episode: 8
title: "Discrete Math 101 (8/10): 그래프 이론 기초"
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
  - 그래프 이론
  - 정점과 간선
  - 인접 리스트
  - 네트워크
seo_description: 그래프의 정의, 표현, 차수, 경로, 연결성과 특수 그래프를 실무 관점으로 설명합니다.
last_reviewed: '2026-05-12'
---

# Discrete Math 101 (8/10): 그래프 이론 기초

이 글은 Discrete Math 101 시리즈의 8번째 글입니다.

## 먼저 던지는 질문

- 그래프의 정의와 종류는 무엇일까요?
- 인접 리스트와 인접 행렬은 어떻게 다를까요?
- 차수, 경로, 사이클, 연결성은 왜 중요한가요?

## 큰 그림

![Discrete Math 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/discrete-math-101/08/08-01-graph-representations.ko.png)

*Discrete Math 101 8장 흐름 개요*

이 그림에서는 그래프 이론 기초를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 그래프 이론 기초의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

내비게이션의 최단 경로, 소셜 네트워크 추천, npm 의존성 해석, 컴파일러 데이터 흐름 분석은 모두 그래프 알고리즘 문제입니다. 그래프 이론을 모르고서는 이런 도구의 내부 동작을 구조적으로 이해하기 어렵습니다.

> 그래프는 관계가 있는 모든 것을 모델링하는 보편 언어입니다.

## 한눈에 보는 개념

> `G = (V, E)`에서 V는 정점 집합, E는 간선 집합입니다. 방향성, 가중치, 다중성 여부에 따라 여러 변형이 생깁니다.

### 같은 그래프를 세 가지 표현으로 보기

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| Vertex (node) | 그래프의 기본 단위 |
| Edge | 두 정점을 잇는 연결 |
| Degree | 정점에 닿는 간선 수 |
| Path | 간선을 따라 이어지는 정점열 |
| Cycle | 시작과 끝이 같은 경로 |

## Before / After

**Before — thinking only in flat data structures:**

```python
# Manage friendships as a list — slow lookup
friends = [("alice", "bob"), ("bob", "carol"), ("alice", "carol")]

def is_friend(a, b):
    return (a, b) in friends or (b, a) in friends
```

**After — modeled as a graph:**

```python
# Adjacency list — average O(1) lookup, plus a rich algorithm toolkit
from collections import defaultdict

graph = defaultdict(set)

def add_edge(g, a, b):
    g[a].add(b); g[b].add(a)

def is_adjacent(g, a, b):
    return b in g[a]
```

## 단계별로 따라가기

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
        return sorted(self.adj[v])

    def nodes(self):
        return sorted(self.adj.keys())

    def edges(self):
        seen = set()
        for u in self.adj:
            for v in self.adj[u]:
                e = (u, v) if self.directed else tuple(sorted((u, v)))
                seen.add(e)
        return sorted(seen)

g = Graph()
for u, v in [("A", "B"), ("B", "C"), ("A", "C"), ("C", "D")]:
    g.add_edge(u, v)

print(f"vertices: {g.nodes()}")
print(f"edges:    {g.edges()}")
```

그래프를 한 번 추상화해 두면 이후 알고리즘은 대부분 같은 인터페이스 위에서 작동합니다. 이 표현의 안정성이 실무에서는 매우 중요합니다.

**예상 출력**

```text
vertices: ['A', 'B', 'C', 'D']
edges:    [('A', 'B'), ('A', 'C'), ('B', 'C'), ('C', 'D')]
```

- 정점 집합은 `A, B, C, D` 네 개여야 합니다.
- 간선 집합은 네 개여야 하며, 무방향 그래프이므로 `('A', 'B')`와 `('B', 'A')`를 따로 세지 않습니다.
- 만약 `set(...)` 형태 그대로 출력했다면 순서가 달라질 수 있으니 비교 전에 `sorted(...)`로 정렬해서 확인하면 됩니다.

### 2단계: 인접 리스트 vs 인접 행렬

```python
def to_adjacency_matrix(g: Graph) -> tuple:
    nodes = sorted(g.nodes())
    n = len(nodes)
    idx = {v: i for i, v in enumerate(nodes)}
    M = [[0] * n for _ in range(n)]
    for u, v in g.edges():
        M[idx[u]][idx[v]] = 1
        if not g.directed:
            M[idx[v]][idx[u]] = 1
    return nodes, M

nodes, M = to_adjacency_matrix(g)
print(f"node order: {nodes}")
print(f"adjacency matrix:\n{M}")
```

| 표현 | 공간 | 간선 검사 | 이웃 순회 |
| --- | --- | --- | --- |
| 인접 리스트 | O(V + E) | O(deg) | O(deg) |
| 인접 행렬 | O(V²) | O(1) | O(V) |

희소 그래프는 리스트가, 밀집 그래프는 행렬이 유리합니다. 표현 선택이 메모리와 속도를 동시에 좌우합니다.

**예상 출력**

```text
node order: ['A', 'B', 'C', 'D']
adjacency matrix:
[[0, 1, 1, 0],
 [1, 0, 1, 0],
 [1, 1, 0, 1],
 [0, 0, 1, 0]]
```

- 행과 열의 순서는 반드시 `['A', 'B', 'C', 'D']`와 같은 순서를 공유해야 합니다.
- 예를 들어 `M[0][2] = 1`은 `A`와 `C`가 연결되었다는 뜻입니다.
- 정점 순서를 다르게 잡으면 행렬 값의 위치도 달라지므로, 결과를 비교할 때는 먼저 정점 순서를 함께 확인해야 합니다.

### 3단계: 차수와 핸드셰이킹 정리

```python
def degree(g: Graph, v) -> int:
    return len(g.adj[v])

total_degree = sum(degree(g, v) for v in g.nodes())
edge_count = len(g.edges())

# Handshake lemma: Σ deg(v) = 2|E|
print(f"sum of degrees = {total_degree}, 2|E| = {2 * edge_count}")
assert total_degree == 2 * edge_count
```

핸드셰이킹 정리는 모든 간선이 두 정점의 차수에 한 번씩 기여한다는 사실입니다. 여기서 홀수 차수 정점의 개수가 항상 짝수라는 중요한 따름정리도 나옵니다.

**예상 출력**

```text
sum of degrees = 8, 2|E| = 8
```

- `A=2`, `B=2`, `C=3`, `D=1`이므로 차수 합은 8입니다.
- 간선이 4개라면 `2|E| = 8`이어야 하므로 두 값이 일치해야 합니다.
- 값이 다르면 간선을 중복 집계했거나, 무방향 간선을 한쪽만 추가한 경우를 먼저 의심해 보세요.

### 4단계: 경로와 연결성

```python
from collections import deque

def has_path(g: Graph, start, target) -> bool:
    """Use BFS to test reachability — O(V + E)."""
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
    """Connected components (undirected only)."""
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
            queue.extend(sorted(g.adj[v] - comp))
        components.append(sorted(comp))
    return components

g_disconnected = Graph()
for u, v in [("A", "B"), ("B", "C"), ("C", "D"), ("X", "Y")]:
    g_disconnected.add_edge(u, v)

print(f"path A→D exists: {has_path(g, 'A', 'D')}")
print(f"connected components: {connected_components(g_disconnected)}")
```

그래프를 이해하는 핵심 질문은 결국 “어디까지 갈 수 있는가”입니다. 경로와 연결성은 이후 BFS, DFS, 최단 경로, 위상 정렬로 이어지는 출발점입니다.

**예상 출력**

```text
path A→D exists: True
connected components: [['A', 'B', 'C', 'D'], ['X', 'Y']]
```

- `A`에서 `D`까지는 `A → C → D` 같은 경로가 있으므로 `True`가 나와야 합니다.
- `g_disconnected`는 `{A, B, C, D}`와 `{X, Y}` 두 연결 요소로 나뉘어야 합니다.
- 연결 요소의 내부 순서가 달라지면 정렬이 빠졌을 가능성이 큽니다.

### 5단계: 특수 그래프

```python
from itertools import combinations

def is_complete(g: Graph) -> bool:
    """Complete graph K_n: every pair connected."""
    n = len(g.nodes())
    return len(g.edges()) == n * (n - 1) // 2

def is_bipartite(g: Graph) -> bool:
    """Bipartite: vertices split into two groups with no intra-group edges."""
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
print(f"K4 is complete: {is_complete(k4)}")

bipart = Graph()
for u, v in [("u1", "v1"), ("u1", "v2"), ("u2", "v1")]:
    bipart.add_edge(u, v)
print(f"bipartite: {is_bipartite(bipart)}")
```

DAG는 사이클이 없는 방향 그래프이고 위상 정렬이 적용됩니다. 이분 그래프는 배정 문제나 매칭 문제를 모델링할 때 핵심입니다.

**예상 출력**

```text
K4 is complete: True
bipartite: True
```

- `K4`는 네 정점의 모든 쌍이 연결되어 있으므로 완전 그래프입니다.
- `bipart`는 `{u1, u2}`와 `{v1, v2}`로 나눌 수 있으므로 이분 그래프입니다.
- 만약 `bipartite`가 `False`라면 같은 색을 가진 정점끼리 연결되었는지, 혹은 큐 기반 색칠 과정이 빠졌는지 점검해 보세요.

## 주목할 점

- 정점과 간선이라는 단순한 정의에서 매우 큰 표현력이 나옵니다.
- 인접 리스트와 인접 행렬은 공간과 조회 속도 사이의 교환 관계를 가집니다.
- 핸드셰이킹 정리는 모든 무방향 그래프의 기본 항등식입니다.
- 완전 그래프, 이분 그래프, DAG는 알고리즘 선택을 좌우하는 대표 분류입니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 방향 그래프와 무방향 그래프를 섞는다 | 간선을 한 번만 추가해 오류가 난다 | 무방향이면 양쪽 모두 넣는다 |
| 자기 루프를 잊는다 | 차수 계산이 어긋난다 | `(v, v)`의 기여를 따로 본다 |
| 다중 간선을 무시한다 | `set`과 `list` 의미가 달라진다 | 단순 그래프 가정 여부를 먼저 정한다 |
| 인접 행렬을 무조건 쓴다 | 희소 그래프에서 메모리를 낭비한다 | `E ≪ V²`이면 리스트를 우선 고려한다 |
| 사이클 검사를 건너뛴다 | DAG 전제 알고리즘이 깨진다 | 위상 정렬 전 비순환성을 확인한다 |

## 실무에서는 이렇게 사용합니다

- 소셜 네트워크는 공통 이웃과 그래프 임베딩으로 추천을 만듭니다.
- 내비게이션은 최단 경로 알고리즘 위에 서 있습니다.
- 패키지 매니저는 그래프 의존성을 정렬합니다.
- 데이터베이스 옵티마이저는 조인 그래프를 분석합니다.
- 추천 시스템은 그래프 신경망까지 활용합니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 새로운 도메인을 보면 먼저 “이걸 그래프로 모델링할 수 있는가”를 묻습니다. 그래프로 바꿀 수 있다면 이미 검증된 알고리즘 도구 상자가 바로 열리기 때문입니다. 또한 표현 선택을 가볍게 보지 않습니다. 인접 리스트와 행렬 중 무엇을 쓰는지가 메모리 사용량과 성능을 결정하기 때문입니다.

## 체크리스트

- [ ] 정점, 간선, 차수의 정의를 설명할 수 있다
- [ ] 인접 리스트와 인접 행렬의 차이를 안다
- [ ] 핸드셰이킹 정리를 적용할 수 있다
- [ ] BFS로 연결 요소를 찾을 수 있다
- [ ] 완전 그래프, 이분 그래프, DAG의 차이를 이해한다

## 연습 문제

1. 정점 6개인 무방향 그래프에서 가능한 최대 간선 수를 구하고 어떤 그래프가 그 값을 달성하는지 말해 보세요.

2. 자신의 소셜 네트워크를 인접 리스트로 표현하고, 자신이 속한 연결 요소의 크기를 계산해 보세요.

3. 핸드셰이킹 정리를 이용해 홀수 차수 정점의 수가 항상 짝수임을 증명해 보세요.

## 정리 및 다음 단계

그래프는 정점과 간선으로 관계를 표현하는 가장 일반적인 구조입니다. 표현 방식, 차수, 경로, 연결성, 특수 그래프 분류를 이해하면 이후의 그래프 알고리즘을 훨씬 수월하게 받아들일 수 있습니다.

다음 글에서는 그래프 위에서 실제로 움직이는 기본 알고리즘인 트리, BFS, DFS를 살펴보겠습니다.

## 처음 질문으로 돌아가기

- **그래프의 정의와 종류는 무엇일까요?**
  - 본문의 기준은 그래프 이론 기초를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **인접 리스트와 인접 행렬은 어떻게 다를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **차수, 경로, 사이클, 연결성은 왜 중요한가요?**
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
- **그래프 이론 기초 (현재 글)**
- 트리와 그래프 탐색 (예정)
- 알고리즘과 이산수학의 연결 (예정)

<!-- toc:end -->

## 참고 자료

- [Discrete Mathematics and Its Applications — Kenneth Rosen, Chapter 10](https://www.mheducation.com/highered/product/discrete-mathematics-its-applications-rosen/M9781259676512.html)
- [Algorithms — Sedgewick & Wayne, Chapter 4](https://algs4.cs.princeton.edu/40graphs/)
- [MIT Mathematics for Computer Science — Graphs and Trees](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
- [NetworkX Documentation — Graph types and representations](https://networkx.org/documentation/stable/reference/classes/index.html)

Tags: Computer Science, 이산수학, 그래프 이론, 정점과 간선, 인접 리스트, 네트워크
