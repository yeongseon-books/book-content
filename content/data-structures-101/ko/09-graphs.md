---
series: data-structures-101
episode: 9
title: 그래프
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
  - 자료구조
  - 그래프
  - 인접 리스트
  - 인접 행렬
  - 그래프 탐색
seo_description: 그래프의 표현 방법(인접 리스트/행렬), 방향성·가중치·연결성, 그리고 BFS/DFS 구현을 정리합니다.
last_reviewed: '2026-05-04'
---

# 그래프

> Data Structures 101 시리즈 (9/10)


## 이 글에서 다룰 문제

그래프는 컴퓨터과학에서 가장 일반적이고 강력한 자료구조입니다. SNS, 지도, 인터넷, 의존성 관리 도구, 추천 알고리즘이 모두 그래프 위에서 동작합니다. 그래프 탐색을 능숙하게 다루지 못하면 코딩 인터뷰의 절반 이상을 풀기 어렵습니다.

> 트리는 모든 관계 중 가장 단순한 형태일 뿐, 진짜 세계는 그래프로 표현됩니다.

## 개념 한눈에 보기

> 그래프 G = (V, E). V는 정점 집합, E는 간선 집합. 간선이 방향을 가지면 유향 그래프, 가중치가 있으면 가중 그래프입니다. 인접 리스트는 메모리 효율이 좋고, 인접 행렬은 두 정점 사이의 연결 확인이 O(1)입니다.

```text
무방향 그래프              유향 그래프
    A ─── B                 A ──→ B
    │     │                 │     ↓
    C ─── D                 C ←── D

인접 리스트                인접 행렬
A: [B, C]                    A B C D
B: [A, D]                  A 0 1 1 0
C: [A, D]                  B 1 0 0 1
D: [B, C]                  C 1 0 0 1
                           D 0 1 1 0
```

## Before / After

**Before — dict의 dict로 임시 표현:**

```python
graph = {"A": {"B": 1}, "B": {"A": 1, "C": 2}, ...}
# 표현은 되지만 일관된 인터페이스가 없어 알고리즘 작성이 번거로움
```

**After — 명확한 그래프 클래스:**

```python
class Graph:
    def __init__(self): self._adj = {}
    def add_edge(self, u, v, w=1): ...
    def neighbors(self, u): ...
# 모든 알고리즘이 같은 인터페이스로 동작
```

## 실습: 단계별로 따라하기

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


g = Graph()
for u, v in [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D"), ("D", "E")]:
    g.add_edge(u, v)

for node in g:
    print(node, g.neighbors(node))
```

dict + list로 인접 리스트를 표현합니다. 메모리는 O(V + E).

### 2단계: 인접 행렬로 그래프 표현

```python
class MatrixGraph:
    def __init__(self, n):
        self.n = n
        self.matrix = [[0] * n for _ in range(n)]

    def add_edge(self, u, v, weight=1):
        self.matrix[u][v] = weight
        self.matrix[v][u] = weight   # 무방향

    def has_edge(self, u, v):
        return self.matrix[u][v] != 0


g = MatrixGraph(5)
g.add_edge(0, 1); g.add_edge(0, 2); g.add_edge(1, 3); g.add_edge(2, 3); g.add_edge(3, 4)
print(g.has_edge(0, 1))   # True
print(g.has_edge(1, 2))   # False
```

행렬은 O(V^2) 메모리지만 두 정점 연결 확인이 O(1). 정점 수가 적고 간선이 빽빽한 그래프에 유리합니다.

### 3단계: BFS 탐색 (최단 경로 길이)

```python
from collections import deque


def bfs_shortest(g, start, target):
    visited = {start: 0}
    queue = deque([start])
    while queue:
        u = queue.popleft()
        if u == target:
            return visited[u]
        for v, _ in g.neighbors(u):
            if v not in visited:
                visited[v] = visited[u] + 1
                queue.append(v)
    return -1


print(bfs_shortest(g, "A", "E"))   # 3
```

BFS는 가까운 정점부터 방문하므로 비가중 그래프의 최단 경로를 자연스럽게 구합니다.

### 4단계: DFS 탐색 (재귀)

```python
def dfs(g, start, visited=None):
    if visited is None:
        visited = set()
    visited.add(start)
    print(start, end=" ")
    for v, _ in g.neighbors(start):
        if v not in visited:
            dfs(g, v, visited)


dfs(g, "A")   # 예: A B D C E
print()
```

DFS는 한 갈래를 끝까지 따라간 뒤 돌아오는 방식입니다. 사이클 검출, 위상 정렬, 연결 컴포넌트 탐색에 자주 쓰입니다.

### 5단계: 사이클 검출과 연결 컴포넌트

```python
def has_cycle(g, start, visited=None, parent=None):
    if visited is None:
        visited = set()
    visited.add(start)
    for v, _ in g.neighbors(start):
        if v not in visited:
            if has_cycle(g, v, visited, start):
                return True
        elif v != parent:
            return True
    return False


def connected_components(g):
    visited = set()
    components = []
    for node in g:
        if node not in visited:
            comp = set()
            stack = [node]
            while stack:
                u = stack.pop()
                if u in comp:
                    continue
                comp.add(u)
                for v, _ in g.neighbors(u):
                    stack.append(v)
            components.append(comp)
            visited.update(comp)
    return components


print(has_cycle(g, "A"))           # True (A-B-D-C-A)
print(connected_components(g))     # [{'A','B','C','D','E'}]
```

DFS의 응용입니다. 사이클은 SNS의 친구 관계 검증, 의존성 그래프 검증 등에 쓰이고, 연결 컴포넌트는 클러스터링·네트워크 분석에 쓰입니다.

## 이 코드에서 주목할 점

- 인접 리스트는 희소 그래프(간선 적음)에, 인접 행렬은 조밀 그래프에 적합합니다
- BFS와 DFS는 같은 코드에서 자료구조만 (큐 vs 스택) 바꾼 것입니다
- 무방향 그래프에서 사이클 검출은 부모를 추적해야 정확합니다
- 그래프는 트리의 일반화이며 거의 모든 관계 모델링의 기본 어휘입니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 방향성 표시 누락 | 알고리즘이 잘못된 결과 | 유향/무방향을 코드에 명시 |
| visited 누락 | 무한 루프 | 방문 표시는 큐/스택에 넣을 때 |
| 가중치 무시 | 다익스트라 등 가중 알고리즘에 비가중 BFS 적용 | 가중 시 다익스트라 사용 |
| 인접 행렬 남용 | V가 클 때 메모리 폭발 | 희소 그래프는 인접 리스트 |
| 깊은 그래프에 재귀 DFS | RecursionError | 명시적 스택으로 변환 |

## 실무에서는 이렇게 쓰입니다

- 소셜 네트워크: 친구 관계, 영향력 분석, 커뮤니티 탐지
- 지도/내비게이션: 도로망 위에서 다익스트라/A* 최단 경로
- 의존성 관리(npm, pip): 위상 정렬로 빌드 순서 결정
- 추천 시스템: 협업 필터링을 그래프 위 임베딩으로 표현
- 분산 시스템: 토폴로지·일관성·라우팅 알고리즘이 모두 그래프 기반

## 체크리스트

- [ ] 정점, 간선, 차수, 경로 같은 그래프 용어를 정확히 사용할 수 있는가
- [ ] 인접 리스트와 인접 행렬의 메모리·시간 트레이드오프를 알고 있는가
- [ ] 방향/무방향, 가중/비가중 그래프의 차이를 구분할 수 있는가
- [ ] BFS와 DFS의 구현 차이를 설명할 수 있는가
- [ ] 트리가 그래프의 특수한 경우임을 이해했는가

## 정리 및 다음 단계

그래프는 정점과 간선으로 임의의 관계를 표현하는 자료구조이며, 컴퓨터과학에서 가장 일반적이고 강력한 모델입니다. 인접 리스트와 인접 행렬의 트레이드오프를 이해하고, 방향성·가중치·연결성 같은 기본 속성을 정확히 다뤄야 합니다. BFS와 DFS는 모든 그래프 알고리즘의 기초이며, 자료구조의 선택만으로 두 알고리즘이 갈립니다.

다음 글에서는 시리즈의 마지막으로, 지금까지 배운 자료구조들을 어떤 상황에서 어떻게 선택할지에 대한 실전 가이드를 정리합니다.

<!-- toc:begin -->
- [자료구조란 무엇인가?](./01-what-are-data-structures.md)
- [배열과 동적 배열](./02-arrays-and-dynamic-arrays.md)
- [연결 리스트](./03-linked-lists.md)
- [스택과 큐](./04-stacks-and-queues.md)
- [해시 테이블](./05-hash-tables.md)
- [트리](./06-trees.md)
- [이진 탐색 트리](./07-binary-search-trees.md)
- [힙](./08-heaps.md)
- **그래프 (현재 글)**
- 자료구조 선택 기준 (예정)
<!-- toc:end -->

## 참고 자료

- [Open Data Structures — Graphs](https://opendatastructures.org/ods-python/12_Graphs.html)
- [NetworkX documentation](https://networkx.org/)
- [Wikipedia — Graph (abstract data type)](https://en.wikipedia.org/wiki/Graph_(abstract_data_type))
- [Sedgewick & Wayne — Algorithms 4ed, Graph chapters](https://algs4.cs.princeton.edu/40graphs/)

Tags: Computer Science, 자료구조, 그래프, 인접 리스트, 인접 행렬, 그래프 탐색
