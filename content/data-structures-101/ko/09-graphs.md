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

이 글은 Data Structures 101 시리즈의 아홉 번째 글입니다.


![Data Structures 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/data-structures-101/09/09-01-graph-representations.ko.png)
*Data Structures 101 9장 흐름 개요*

## 먼저 던지는 질문

- 정점, 간선, 차수, 경로 같은 그래프 용어를 어떻게 정확히 쓸까요?
- 인접 리스트와 인접 행렬은 어떤 트레이드오프를 가질까요?
- 방향 그래프와 무방향 그래프, 가중치 그래프와 비가중치 그래프는 무엇이 다를까요?

## 왜 중요한가

그래프는 컴퓨터과학에서 가장 일반적이고 강력한 자료구조입니다. 소셜 네트워크, 지도, 인터넷, 의존성 관리자, 추천 알고리즘 모두 그래프 위에서 설명할 수 있습니다. 그래프 순회가 익숙하지 않으면 많은 코딩 문제와 시스템 문제를 다루기 어려워집니다.

> 트리는 가장 단순한 관계이고, 현실 세계는 대부분 그래프로 설명하는 편이 더 정확합니다.

## 핵심 한눈에 보기

> 그래프 `G = (V, E)`는 정점 집합 V와 간선 집합 E로 정의합니다. 간선에 방향이 있으면 방향 그래프, 가중치가 있으면 가중치 그래프입니다. 인접 리스트는 메모리 효율이 좋고, 인접 행렬은 두 정점 사이 간선 존재 여부를 O(1)에 확인할 수 있습니다.

### 그래프 표현 방식

## 핵심 용어

| 용어 | 의미 |
| --- | --- |
| 정점 | 그래프의 노드 |
| 간선 | 두 정점을 잇는 연결 |
| 차수 | 한 정점에 연결된 간선 수 |
| 경로 | 간선으로 이어진 정점들의 순서 |
| 사이클 | 시작점과 끝점이 같은 경로 |

## 전후 비교

**Before — ad-hoc dict-of-dict representation:**

```text
graph = {"A": {"B": 1}, "B": {"A": 1, "C": 2}, ...}
# It works, but with no consistent interface every algorithm becomes awkward
```

**After — an explicit Graph class:**

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

for node in service_graph:
    print(node, service_graph.neighbors(node))
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
matrix_graph.add_edge(0, 1); matrix_graph.add_edge(0, 2); matrix_graph.add_edge(1, 3); matrix_graph.add_edge(2, 3)
print(matrix_graph.has_edge(0, 1))   # True
print(matrix_graph.has_edge(1, 0))   # False
```

행렬은 O(V^2) 메모리를 쓰지만 “간선이 있는가?”를 O(1)에 답합니다. 정점 수가 작고 그래프가 조밀할 때 유리합니다.

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
print(f"hop count: {len(path) - 1}")

expected = [
    "api-gateway",
    "catalog-service",
    "inventory-service",
    "warehouse-db",
]
print(f"path matches expectation: {path == expected}")

# ['api-gateway', 'catalog-service', 'inventory-service', 'warehouse-db']
# hop count: 3
# 경로가 기대값과 일치: True
```

BFS는 가까운 정점을 먼저 방문하므로 비가중치 그래프에서 자연스럽게 최단 경로를 구합니다. 여기서 경로나 hop 수가 다르게 나오면 queue 순서를 깨뜨렸거나, `visited` 표시 시점이 늦었거나, 간선 방향을 잘못 넣었을 가능성이 큽니다.

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
# ['api-gateway', 'auth-service', 'user-db', 'catalog-service', 'inventory-service', 'warehouse-db', 'cache']
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
    ("ledger", "web"),
]:
    dependency_graph.add_edge(u, v)

cycle_found = has_cycle_directed(dependency_graph)
print(cycle_found)
print(f"topological traversal possible: {not cycle_found}")

# True
# 위상 순회 가능 여부: False
```

이 검증은 DFS가 실무에서 어떻게 쓰이는지 직접 보여 줍니다. 역방향 간선이 생기면 의존성 그래프를 위상 정렬할 수 없습니다. 여기서 `cycle_found`가 `False`로 나오면 방향 그래프를 무방향처럼 다뤘거나, 재귀 스택 추적을 빼먹었을 가능성이 큽니다.

## 이 코드에서 주목할 점

- 희소 그래프는 인접 리스트, 조밀 그래프는 인접 행렬이 잘 맞습니다.
- BFS와 DFS는 순회 뼈대가 비슷하고 queue냐 재귀/스택이냐가 동작을 가릅니다.
- 방향 그래프의 사이클 검출은 현재 재귀 스택을 함께 추적해야 정확합니다.
- 그래프는 트리의 일반화이자 관계 모델링의 기본 어휘입니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 방향 여부를 코드에 드러내지 않음 | 알고리즘 결과가 틀어짐 | directed/undirected를 명시합니다 |
| visited 집합을 빼먹음 | 무한 순회 발생 | enqueue/push 시점에 바로 표시합니다 |
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

시니어 엔지니어는 먼저 “이게 그래프 문제인가?”를 묻습니다. 정점, 간선, 관계라는 언어로 다시 표현할 수 있으면 BFS, DFS, 다익스트라, 위상 정렬 같은 검증된 해법을 곧바로 떠올릴 수 있기 때문입니다.

또한 NetworkX, igraph, Neo4j 같은 도구를 알고 적절할 때 사용합니다. 하지만 기본 알고리즘은 몸에 익혀 두어야, 라이브러리가 내부에서 무엇을 하는지 이해하고 성능·제약을 예측할 수 있습니다.

## 체크리스트

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


## 구현 관점 보강: 복잡도와 선택 기준

자료구조를 비교할 때는 평균 시간 복잡도만으로 결론을 내리면 정확도가 떨어집니다. 실제 시스템에서는 데이터 분포, 갱신 비율, 메모리 제약, 동시성 요구가 동시에 작동하기 때문입니다. 따라서 아래 표처럼 연산별 상한과 운영 조건을 함께 보는 기준이 필요합니다.

| 구조 | 조회 | 삽입 | 삭제 | 메모리 특성 | 적합한 상황 |
| --- | --- | --- | --- | --- | --- |
| 배열/동적 배열 | O(1) 인덱스, O(n) 탐색 | 끝 O(1) amortized, 중간 O(n) | 중간 O(n) | 연속 메모리, 캐시 효율 우수 | 읽기 중심, 랜덤 액세스 필요 |
| 연결 리스트 | O(n) | 노드 위치 확보 시 O(1) | 노드 위치 확보 시 O(1) | 포인터 오버헤드 큼 | 중간 삽입/삭제 빈번 |
| 해시 테이블 | 평균 O(1), 최악 O(n) | 평균 O(1) | 평균 O(1) | 버킷/재해시 비용 존재 | 키 기반 빠른 조회 |
| 균형 트리 | O(log n) | O(log n) | O(log n) | 포인터 구조, 정렬 유지 | 범위 질의, 순서 보존 |

구현 단계에서는 연산 정의를 코드 시그니처로 먼저 고정하는 방식이 안전합니다. 예를 들어 `insert`, `remove`, `contains`, `iterate`의 사전/사후 조건을 먼저 문서화하고, 그 뒤에 내부 저장 구조를 바꾸면 테스트 재사용성이 크게 올라갑니다. 같은 인터페이스에 배열 기반 구현과 링크 기반 구현을 각각 붙여 벤치마크하면, 개념 설명에서 보던 복잡도 표가 실제 지연 시간으로 어떻게 드러나는지 확인할 수 있습니다.

또한 사용 사례 비교는 데이터 흐름 단위로 해야 합니다. 예를 들어 이벤트 로그 파이프라인에서는 "대량 append + 배치 스캔" 패턴이 많아 동적 배열이 유리하지만, 작업 스케줄러에서는 "우선순위 갱신 + 최소값 추출"이 반복되어 힙이 더 적합합니다. 반대로 온라인 추천 시스템의 피처 저장소는 키 조회 비율이 매우 높아 해시 기반 구조가 기본 선택이 됩니다.

실습 팁으로는 동일한 입력 집합에 대해 최소 두 가지 구조를 구현하고, 다음 항목을 비교 기록하는 방식이 좋습니다: (1) 연산당 평균 지연 시간, (2) p95 지연 시간, (3) 메모리 사용량, (4) 구현 복잡도. 이 네 가지를 같이 보면 단순 Big-O 표기법이 놓치는 현실 제약까지 반영한 결정을 내릴 수 있습니다.

실무 적용 관점에서는 입력 데이터의 크기뿐 아니라 업데이트 패턴, 동시 접근, 메모리 상한을 함께 고려해 구조를 선택해야 안정적인 성능이 나옵니다.


## 실전 앵커: 구현과 복잡도 검증

개념을 정확히 이해하려면 설명 문장만 보는 것으로는 부족합니다. 손으로 구현하고, 연산 단위를 측정하고, 메모리 배치를 눈으로 그려 보는 과정이 함께 있어야 합니다. 아래 앵커는 이 시리즈 전체에서 공통으로 재사용할 수 있는 검증 틀입니다.

### 파이썬 미니 구현 묶음

```python
from collections import deque

# 1) 리스트: 끝 append/pop은 빠르고, 앞쪽 연산은 느립니다.
arr = []
arr.append(10)
arr.append(20)
arr.pop()

# 2) 스택: list로 LIFO 구현
stack = []
stack.append('A')
stack.append('B')
stack.pop()

# 3) 큐: deque로 FIFO 구현
queue = deque()
queue.append('job-1')
queue.append('job-2')
queue.popleft()

# 4) 트리 노드
class Node:
    def __init__(self, key, left=None, right=None):
        self.key = key
        self.left = left
        self.right = right

# 5) 그래프 인접 리스트와 너비 우선 탐색
graph = {
    'A': ['B', 'C'],
    'B': ['D'],
    'C': ['D'],
    'D': []
}

def bfs(start):
    seen = {start}
    q = deque([start])
    order = []
    while q:
        cur = q.popleft()
        order.append(cur)
        for nxt in graph[cur]:
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return order
```

### 연산 복잡도 비교표

| 구조 | 핵심 연산 | 평균 시간 | 최악 시간 | 메모리 관찰 포인트 |
| --- | --- | --- | --- | --- |
| 동적 배열 | 인덱스 조회 | O(1) | O(1) | 연속 메모리, 캐시 친화적 |
| 동적 배열 | 중간 삽입/삭제 | O(n) | O(n) | 이동 비용이 성능 병목 |
| 스택 | push/pop | O(1) | O(1) | 한쪽 끝 연산으로 단순 |
| 큐(덱) | enqueue/dequeue | O(1) | O(1) | 양 끝 연산이 안정적 |
| 트리(균형) | 탐색/삽입/삭제 | O(log n) | O(log n) | 높이 유지가 관건 |
| 그래프 | 순회(BFS/DFS) | O(V+E) | O(V+E) | 정점/간선 수에 비례 |

### 메모리 배치 그림

```text
동적 배열
[0][1][2][3][4]  (연속 주소)
  |  |  |  |
  +-- 인덱스로 즉시 접근

연결 리스트
[값|다음] -> [값|다음] -> [값|다음]
   ^ 포인터를 따라 이동

트리
        [8]
       /   \
     [3]   [10]
     / \
   [1] [6]

그래프(인접 리스트)
A: B, C
B: D
C: D
D: (없음)
```

### 문제 연결 지도

| 유형 | 대표 문제 | 이 글의 관점으로 보는 핵심 |
| --- | --- | --- |
| 배열/투포인터 | LeetCode 1, 88, 283 | 인덱스 이동과 덮어쓰기 비용 관리 |
| 스택 | LeetCode 20, 155, 739 | 상태를 되돌릴 때 LIFO가 자연스러운가 |
| 큐/BFS | LeetCode 102, 994, 542 | 레벨 단위 확산과 최단 거리 |
| 트리 | LeetCode 104, 226, 236 | 재귀와 반복 중 호출 깊이 제어 |
| 그래프 | LeetCode 200, 207, 417 | 방문 집합 설계와 순회 순서 |

실무에서 성능 이슈가 발생하면, 먼저 연산을 위 표의 행으로 대응시켜 병목을 분류한 뒤 구현을 교체하는 순서로 접근하는 편이 안전합니다.


### 운영에서 다시 확인할 기준

그래프 문제에서는 모델링이 절반입니다. 정점을 무엇으로 볼지, 간선 방향을 어떻게 정의할지에 따라 같은 데이터도 전혀 다른 문제로 바뀝니다. 구현 전에 노드, 간선, 가중치, 방문 조건을 문장으로 먼저 고정하면 코드 품질이 훨씬 안정됩니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

그래프 문제에서는 모델링이 절반입니다. 정점을 무엇으로 볼지, 간선 방향을 어떻게 정의할지에 따라 같은 데이터도 전혀 다른 문제로 바뀝니다. 구현 전에 노드, 간선, 가중치, 방문 조건을 문장으로 먼저 고정하면 코드 품질이 훨씬 안정됩니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

그래프 문제에서는 모델링이 절반입니다. 정점을 무엇으로 볼지, 간선 방향을 어떻게 정의할지에 따라 같은 데이터도 전혀 다른 문제로 바뀝니다. 구현 전에 노드, 간선, 가중치, 방문 조건을 문장으로 먼저 고정하면 코드 품질이 훨씬 안정됩니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

그래프 문제에서는 모델링이 절반입니다. 정점을 무엇으로 볼지, 간선 방향을 어떻게 정의할지에 따라 같은 데이터도 전혀 다른 문제로 바뀝니다. 구현 전에 노드, 간선, 가중치, 방문 조건을 문장으로 먼저 고정하면 코드 품질이 훨씬 안정됩니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

그래프 문제에서는 모델링이 절반입니다. 정점을 무엇으로 볼지, 간선 방향을 어떻게 정의할지에 따라 같은 데이터도 전혀 다른 문제로 바뀝니다. 구현 전에 노드, 간선, 가중치, 방문 조건을 문장으로 먼저 고정하면 코드 품질이 훨씬 안정됩니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.


### 운영에서 다시 확인할 기준

그래프 문제에서는 모델링이 절반입니다. 정점을 무엇으로 볼지, 간선 방향을 어떻게 정의할지에 따라 같은 데이터도 전혀 다른 문제로 바뀝니다. 구현 전에 노드, 간선, 가중치, 방문 조건을 문장으로 먼저 고정하면 코드 품질이 훨씬 안정됩니다.

검증 단계에서는 동일 입력 집합으로 최소 두 구현을 비교하고, 평균 지연 시간과 상위 백분위 지연 시간을 함께 기록해야 합니다. 또한 메모리 사용량과 코드 복잡도를 같이 보아야 실제 유지보수 비용까지 반영한 결정을 내릴 수 있습니다.

## 처음 질문으로 돌아가기

- **정점, 간선, 차수, 경로 같은 그래프 용어를 어떻게 정확히 쓸까요?**
  - 정점은 `api-gateway`, `auth-service` 같은 개체이고, 간선은 그 둘을 잇는 의존 관계입니다. 차수는 한 정점에 연결된 간선 수를 뜻하며, 경로는 본문 BFS 예제의 `api-gateway → catalog-service → inventory-service → warehouse-db`처럼 간선을 따라 이어진 방문 순서입니다.
- **인접 리스트와 인접 행렬은 어떤 트레이드오프를 가질까요?**
  - 인접 리스트는 dict와 list 조합으로 표현해 메모리를 O(V + E)만 쓰므로, 서비스 의존성처럼 희소한 그래프에 잘 맞습니다. 인접 행렬은 O(V^2) 메모리를 쓰는 대신 `has_edge(u, v)`를 O(1)에 답할 수 있어, 정점 수가 작고 간선이 빽빽한 경우에 유리합니다.
- **방향 그래프와 무방향 그래프, 가중치 그래프와 비가중치 그래프는 무엇이 다를까요?**
  - 방향 그래프는 `u → v`와 `v → u`를 다른 의미로 취급하므로, 본문 사이클 검출 예제처럼 의존성 루프를 정확히 잡아낼 수 있습니다. 가중치 그래프는 간선마다 비용이나 거리 값을 담아야 해서, 단순 hop 수를 보는 BFS 대신 다익스트라 같은 가중치 알고리즘이 필요해집니다.

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
- **그래프 (현재 글)**
- 자료구조 선택 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Data Structures 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/data-structures-101/ko)

- [Open Data Structures — Graphs](https://opendatastructures.org/ods-python/12_Graphs.html)
- [NetworkX documentation](https://networkx.org/)
- [Wikipedia — Graph (abstract data type)](https://en.wikipedia.org/wiki/Graph_(abstract_data_type))
- [Sedgewick & Wayne — Algorithms 4ed, Graph chapters](https://algs4.cs.princeton.edu/40graphs/)

Tags: Computer Science, 자료구조, 그래프, 인접 리스트, 인접 행렬, 그래프 탐색
