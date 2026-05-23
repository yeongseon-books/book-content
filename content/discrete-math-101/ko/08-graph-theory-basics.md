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


![Discrete Math 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/discrete-math-101/08/08-01-graph-representations.ko.png)
*Discrete Math 101 8장 흐름 개요*

## 먼저 던지는 질문

- 그래프의 정의와 종류는 무엇일까요?
- 인접 리스트와 인접 행렬은 어떻게 다를까요?
- 차수, 경로, 사이클, 연결성은 왜 중요한가요?

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

## 전후 비교

**Before — thinking only in flat data structures:**

```python
# 친구 관계를 list로 관리 — 조회가 느림
friends = [("alice", "bob"), ("bob", "carol"), ("alice", "carol")]

def is_friend(a, b):
    return (a, b) in friends or (b, a) in friends
```

**After — modeled as a graph:**

```python
# 인접 리스트 — 평균 O(1) 조회와 풍부한 알고리즘 활용
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

# 핸드셰이크 정리: Σ deg(v) = 2|E|
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

다음 글에서는 그래프 위에서 실제로 움직이는 기본 알고리즘인 트리, BFS, DFS를 봅니다.

## 실전 확장: 그래프 표현과 알고리즘 선택 기준

그래프 문제는 표현이 절반입니다. 인접 행렬과 인접 리스트 중 무엇을 고르는지에 따라 공간 복잡도와 구현 난도가 크게 달라집니다.

### 표현 비교

| 표현 | 공간 | 간선 존재 확인 | 순회 |
| --- | --- | --- | --- |
| 인접 행렬 | `O(V^2)` | `O(1)` | `O(V)` |
| 인접 리스트 | `O(V+E)` | 평균 `O(deg(v))` | `O(deg(v))` |

희소 그래프에서는 인접 리스트가 실용적입니다.

### BFS 구현 앵커

```python
from collections import deque

def bfs_order(graph: dict[int, list[int]], start: int) -> list[int]:
    seen = {start}
    q = deque([start])
    order = []
    while q:
        v = q.popleft()
        order.append(v)
        for nxt in graph.get(v, []):
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return order
```

### DFS 구현 앵커

```python
def dfs_order(graph: dict[int, list[int]], start: int) -> list[int]:
    seen = set()
    order = []

    def visit(v: int) -> None:
        seen.add(v)
        order.append(v)
        for nxt in graph.get(v, []):
            if nxt not in seen:
                visit(nxt)

    visit(start)
    return order
```

### 사이클 탐지(유향 그래프)

```python
def has_cycle_directed(graph: dict[int, list[int]]) -> bool:
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {v: WHITE for v in graph}

    def dfs(v: int) -> bool:
        color[v] = GRAY
        for nxt in graph.get(v, []):
            if color.get(nxt, WHITE) == GRAY:
                return True
            if color.get(nxt, WHITE) == WHITE and dfs(nxt):
                return True
        color[v] = BLACK
        return False

    return any(color[v] == WHITE and dfs(v) for v in graph)
```

색칠 기법은 재귀 스택에 다시 들어오는 간선을 찾는 방식입니다.

### 짧은 증명 앵커

무방향 그래프에서 `Σdeg(v)=2|E|`인 이유는 간선 하나가 양 끝 정점의 차수를 각각 1씩 증가시키기 때문입니다. 모든 간선을 합치면 정확히 두 번 세어집니다.

## 심화 워크숍: 그래프 알고리즘 적용 패턴

### 연결 요소 계산

무방향 그래프에서 연결 요소 개수는 네트워크 분리 상태를 측정하는 기본 지표입니다.

```python
def connected_components(graph: dict[int, list[int]]) -> list[set[int]]:
    seen = set()
    comps = []
    for s in graph:
        if s in seen:
            continue
        stack = [s]
        comp = set()
        seen.add(s)
        while stack:
            v = stack.pop()
            comp.add(v)
            for nxt in graph.get(v, []):
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        comps.append(comp)
    return comps
```

### 최단 경로가 필요한지 판단하기

요구사항이 "도달 가능 여부"면 DFS/BFS로 충분하지만 "최소 이동 횟수"면 BFS 또는 가중치가 있을 때 다익스트라가 필요합니다. 문제 문장에 있는 최적화 표현("최소", "가장 짧은")을 놓치지 않는 것이 중요합니다.

### 그래프 모델 검증 질문

- 고립 정점이 허용되는가
- 자기 루프를 허용하는가
- 다중 간선을 허용하는가
- 방향성은 필요한가

이 질문에 답하면 자료구조 선택이 자동으로 따라옵니다.

## 부록: 검증 가능한 실습 패턴 모음

아래 패턴은 각 장의 개념을 실습으로 고정하기 위한 공통 템플릿입니다. 핵심은 계산 결과를 맞히는 것보다, 어떤 정의를 적용했는지 문장으로 남기는 것입니다.

### 패턴 1: 정의를 먼저 쓰고 계산하기

1. 문제에서 사용하는 대상 집합을 명시합니다.
2. 관계 또는 함수를 기호로 정의합니다.
3. 계산을 수행하고, 결과가 정의를 만족하는지 다시 확인합니다.

이 순서를 지키면 중간에 식이 길어져도 논리의 출발점을 잃지 않습니다.

### 패턴 2: 반례를 의도적으로 만들기

정리나 가설을 세웠다면, 반례 후보를 최소 3개 만듭니다.

- 경계값 입력(0, 1, 최대값)
- 중복/충돌 입력
- 공집합 또는 단일 원소 입력

반례가 발견되면 결론을 버리는 것이 아니라, 가정과 정의를 수정합니다. 이 절차가 수학적 엄밀성과 엔지니어링 실용성을 동시에 만족시킵니다.

### 패턴 3: 표와 코드 출력을 함께 남기기

진리표, 집합 연산표, 점화식 전개표 중 하나를 반드시 포함합니다. 그리고 같은 내용을 계산하는 짧은 코드를 붙여 결과를 재현합니다.

```python
def verify_identity(left: set[int], right: set[int]) -> bool:
    return left == right
```

작은 검증 함수 하나라도 문서에 남기면 팀원 간 해석 차이를 줄일 수 있습니다.

### 패턴 4: 증명 구조를 고정하기

증명은 다음 네 문장 구조를 기본으로 씁니다.

- 가정: 무엇을 참이라고 두는가
- 전개: 어떤 정의/정리를 사용해 변형하는가
- 핵심 전환: 결론으로 넘어가는 결정적 단계는 무엇인가
- 결론: 원래 명제가 왜 성립하는가

이 구조는 직접 증명, 대우 증명, 귀류법, 귀납법 모두에 적용됩니다.

### 패턴 5: 알고리즘과 수학 근거 연결하기

알고리즘 설명에는 다음 항목을 최소로 넣습니다.

- 불변식 1개 이상
- 종료 조건 1개
- 복잡도 식 1개
- 반례 테스트 1개

이 네 항목이 있으면 코드가 바뀌어도 정확성 근거를 유지할 수 있습니다.

### 미니 문제 세트

1. 두 집합 `A`, `B`를 임의로 만들고 `A∩B`, `A∪B`, `A\B`를 계산한 뒤 포함관계를 설명하세요.
2. 명제식 `(P→Q) ∧ (Q→R) → (P→R)`의 진리표를 작성하고 항진명제 여부를 확인하세요.
3. 점화식 `T(n)=T(n-1)+n`의 닫힌형을 추측한 다음 귀납법으로 검증하세요.
4. 인접 리스트 그래프 하나를 만든 뒤 BFS/DFS 방문 순서를 비교하세요.
5. `nCk = nC(n-k)`를 식과 의미 해석(선택 vs 비선택) 두 방식으로 설명하세요.

### 마무리

각 장의 주제가 달라 보여도 훈련 루프는 같습니다. 정의를 선언하고, 계산을 수행하고, 반례로 검증하고, 증명 또는 불변식으로 고정하면 됩니다. 이 루프를 반복하면 새로운 문제에서도 같은 품질로 사고할 수 있습니다.


## 추가 심화: 오류 사례와 교정 로그

실무에서 이산수학 개념이 흔들리는 지점은 대부분 "정의 생략"에서 시작합니다. 아래는 자주 나오는 오류와 교정 방식입니다.

### 오류 사례 1: 조건 누락

- 증상: 코드가 특정 입력에서만 실패합니다.
- 원인: 명제식에서 한 항을 자연어로만 설명하고 코드에 반영하지 않았습니다.
- 교정: 조건을 변수화해 논리식으로 명시하고, 진리표의 위험 조합을 테스트로 고정합니다.

### 오류 사례 2: 집합 경계 불일치

- 증상: 제외되어야 할 원소가 결과에 섞입니다.
- 원인: 전체집합 `U`를 정의하지 않아 여집합 계산이 흔들립니다.
- 교정: `U`를 먼저 확정하고 `A^c = U \ A`를 코드와 문서에 동시에 기록합니다.

### 오류 사례 3: 그래프 방향성 오해

- 증상: 탐색 결과가 기대보다 과도하거나 부족합니다.
- 원인: 유향/무향 그래프를 혼동해 간선을 양방향으로 추가했습니다.
- 교정: 입력 스키마 단계에서 방향성을 필드로 분리하고, 예제 그래프를 최소 1개 유지합니다.

### 오류 사례 4: 점화식 기저 조건 누락

- 증상: 재귀가 종료되지 않거나 값이 어긋납니다.
- 원인: `n=0`, `n=1`에서의 정의를 생략했습니다.
- 교정: 기저 조건을 본문과 코드 첫 줄에 병기하고, 단위 테스트를 별도로 둡니다.

### 교정 루프

1. 정의를 다시 선언합니다.
2. 최소 반례를 구성합니다.
3. 식과 코드를 동시에 수정합니다.
4. 표/출력으로 재검증합니다.

이 루프를 문서화하면 팀 단위 품질이 안정됩니다.


## 보강 메모: 손으로 계산해 보는 검증 절차

아래 절차를 한 번 손으로 수행하면 개념이 빠르게 고정됩니다.

- 진리표 문제: 입력 조합을 빠짐없이 나열하고, 각 행의 결론을 식에 따라 계산합니다.
- 집합 문제: 원소를 실제로 써서 합집합/교집합/차집합을 구한 뒤 식과 일치하는지 확인합니다.
- 그래프 문제: 정점 방문 순서를 한 줄 로그로 기록해 BFS/DFS 차이를 비교합니다.
- 점화식 문제: `n=1..6`까지 값을 적어 패턴을 추측한 뒤 귀납법으로 검증합니다.

이 과정을 문서 마지막에 남기면 다음 글을 읽을 때도 같은 기준으로 사고를 이어갈 수 있습니다.


## 처음 질문으로 돌아가기

- **그래프의 정의와 종류는 무엇일까요?**
  - 그래프는 `G = (V, E)`로 쓰며, `V`는 정점 집합이고 `E`는 간선 집합입니다. 본문은 `Graph` 클래스와 `K4`, 이분 그래프 예시를 통해 무방향 그래프, 완전 그래프, 이분 그래프, DAG처럼 조건에 따라 여러 종류가 갈린다는 점을 정리했습니다.
- **인접 리스트와 인접 행렬은 어떻게 다를까요?**
  - 인접 리스트는 `O(V+E)` 공간으로 희소 그래프에 유리하고, 이웃 순회가 빠르지만 간선 존재 확인은 차수에 비례합니다. 반대로 본문의 `to_adjacency_matrix` 예시처럼 인접 행렬은 `O(V^2)` 공간을 쓰는 대신 두 정점의 연결 여부를 즉시 확인할 수 있어 밀집 그래프에서 강합니다.
- **차수, 경로, 사이클, 연결성은 왜 중요한가요?**
  - 차수는 `Σdeg(v)=2|E|` 같은 기본 항등식을 주고, 경로와 연결성은 `has_path`, `connected_components`처럼 어디까지 도달 가능한지 판단하게 해 줍니다. 또한 사이클 유무는 위상 정렬 가능 여부와 직결되므로, 그래프가 단순히 연결돼 있는지만 보는 것보다 훨씬 중요한 구조 정보입니다.

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

- [book-examples: discrete-math-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/discrete-math-101/ko)
- [Discrete Mathematics and Its Applications — Kenneth Rosen, Chapter 10](https://www.mheducation.com/highered/product/discrete-mathematics-its-applications-rosen/M9781259676512.html)
- [Algorithms — Sedgewick & Wayne, Chapter 4](https://algs4.cs.princeton.edu/40graphs/)
- [MIT Mathematics for Computer Science — Graphs and Trees](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)
- [NetworkX Documentation — Graph types and representations](https://networkx.org/documentation/stable/reference/classes/index.html)

Tags: Computer Science, 이산수학, 그래프 이론, 정점과 간선, 인접 리스트, 네트워크
