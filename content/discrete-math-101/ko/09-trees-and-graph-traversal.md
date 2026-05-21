---
series: discrete-math-101
episode: 9
title: "Discrete Math 101 (9/10): 트리와 그래프 탐색"
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
  - 트리
  - BFS
  - DFS
  - 신장 트리
seo_description: 트리, BFS, DFS, 신장 트리와 MST를 그래프 탐색의 기본 도구로 설명합니다.
last_reviewed: '2026-05-12'
---

# Discrete Math 101 (9/10): 트리와 그래프 탐색

이 글은 Discrete Math 101 시리즈의 9번째 글입니다.


![Discrete Math 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/discrete-math-101/09/09-01-big-picture.ko.png)
*Discrete Math 101 9장 흐름 개요*

## 먼저 던지는 질문

- 트리의 정의와 성질은 무엇일까요?
- BFS는 왜 최단 경로와 연결될까요?
- DFS는 어떤 문제에서 강할까요?

## 왜 중요한가

파일 시스템, DOM, 컴파일러 AST, 데이터베이스 인덱스처럼 많은 시스템 내부에는 트리가 숨어 있습니다. BFS와 DFS는 최단 경로, 사이클 검출, 위상 정렬, MST의 출발점입니다.

> 트리는 가장 단순한 비자명 그래프이고, 탐색은 그래프 알고리즘의 기본 동작입니다.

## 한눈에 보는 개념

> 트리는 연결된 무사이클 무방향 그래프입니다. 정점이 n개면 간선은 정확히 n-1개이고, 임의의 두 정점 사이 경로는 정확히 하나입니다.

```text
       tree                    BFS order            DFS order
        1                    1 → 2 → 3            1 → 2 → 4
       / \                   → 4 → 5 → 6          → 5 → 3 → 6
      2   3                  (level by level)     (one branch first)
     / \   \
    4   5   6
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| Tree | 연결된 사이클 없는 그래프 |
| Root | 선택된 시작 정점 |
| Leaf | 차수 1의 정점 |
| Spanning tree | 모든 정점을 포함하는 부분 트리 |
| MST | 총 가중치가 최소인 신장 트리 |

## 전후 비교

**Before — checking every node by hand:**

```python
# 친구의 친구를 수동으로 작성 — 깊이마다 중복 코드 발생
def friends_of_friends(person):
    result = set()
    for f in friends_of(person):
        for ff in friends_of(f):
            result.add(ff)
    return result
```

**After — BFS for arbitrary distance:**

```python
from collections import deque

def reachable_within(graph, start, max_distance):
    """All vertices within distance max_distance from start."""
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

## 단계별로 따라가기

### 1단계: 트리 정의와 검증

```python
from collections import defaultdict

def is_tree(edges: list, n_nodes: int) -> bool:
    """Test whether an undirected graph is a tree — check edge count and connectivity."""
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
print(f"is tree: {is_tree(tree_edges, 6)}")
```

트리를 판정할 때 가장 실용적인 감각은 `V - 1 = E`와 연결성입니다. 이 두 조건이 함께 맞아떨어지면 트리라는 판단이 매우 쉬워집니다.

### 2단계: BFS — 너비 우선 탐색

```python
def bfs(graph: dict, start) -> dict:
    """Minimum number of edges from start to every vertex (assuming weight 1)."""
    distances = {start: 0}
    queue = deque([start])
    while queue:
        v = queue.popleft()
        for u in sorted(graph[v]):
            if u not in distances:
                distances[u] = distances[v] + 1
                queue.append(u)
    return distances

graph = {1: [2, 3], 2: [1, 4, 5], 3: [1, 6], 4: [2], 5: [2], 6: [3]}
print(f"distances from 1: {bfs(graph, 1)}")
```

BFS는 큐를 사용해 가까운 정점부터 탐색합니다. 모든 간선 가중치가 같다면 BFS가 최단 경로를 준다는 사실이 실무적으로 특히 중요합니다.

**예상 출력**

```text
distances from 1: {1: 0, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2}
```

- 정점 `2`, `3`은 시작점 `1`에서 한 간선 거리, `4`, `5`, `6`은 두 간선 거리여야 합니다.
- BFS에서 거리가 틀리면 보통 `visited` 표시를 늦게 하거나, 큐 대신 스택처럼 동작하게 만든 경우가 많습니다.

### 3단계: DFS — 깊이 우선 탐색

```python
def dfs_recursive(graph: dict, start, visited=None) -> list:
    """Recursive DFS — returns visit order."""
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
    """Stack-based DFS — safe when depth is large."""
    visited, order, stack = set(), [], [start]
    while stack:
        v = stack.pop()
        if v in visited:
            continue
        visited.add(v); order.append(v)
        stack.extend(sorted(graph[v], reverse=True))
    return order

print(f"DFS recursive: {dfs_recursive(graph, 1)}")
print(f"DFS iterative: {dfs_iterative(graph, 1)}")
```

DFS는 한 갈래를 끝까지 따라간 뒤 되돌아옵니다. 그래서 사이클 검출, 위상 정렬, 강한 연결 요소처럼 구조를 깊게 파악하는 문제에 잘 맞습니다.

**예상 출력**

```text
DFS recursive: [1, 2, 4, 5, 3, 6]
DFS iterative: [1, 2, 4, 5, 3, 6]
```

- 이 예제는 이웃을 정렬했기 때문에 재귀 DFS와 반복 DFS의 방문 순서가 같게 고정됩니다.
- 다른 순서가 나왔다면 알고리즘이 틀렸다기보다 이웃 순서가 달라졌을 가능성이 큽니다. 검증용 예제에서는 항상 `sorted(...)`를 먼저 적용해 보세요.

### 4단계: BFS/DFS가 만드는 신장 트리

```python
def spanning_tree_bfs(graph: dict, start) -> list:
    """Extract a spanning tree via BFS."""
    visited = {start}
    tree = []
    queue = deque([start])
    while queue:
        v = queue.popleft()
        for u in sorted(graph[v]):
            if u not in visited:
                visited.add(u)
                tree.append((v, u))
                queue.append(u)
    return tree

print(f"spanning tree (BFS): {spanning_tree_bfs(graph, 1)}")
```

BFS와 DFS는 모두 그래프 전체를 덮는 신장 트리를 만들 수 있습니다. 즉, 탐색 과정 자체가 그래프의 뼈대를 하나 뽑아내는 작업이기도 합니다.

**예상 출력**

```text
spanning tree (BFS): [(1, 2), (1, 3), (2, 4), (2, 5), (3, 6)]
```

- BFS 신장 트리는 루트에서 가까운 정점부터 부모가 정해지므로, 같은 그래프를 쓰면 위 간선 집합이 나와야 합니다.
- 간선 수는 항상 `정점 수 - 1`개여야 합니다. 여기서는 6개 정점을 덮으므로 5개 간선이 맞습니다.

### 5단계: 최소 신장 트리(MST) — Kruskal

```python
def kruskal_mst(n_nodes: int, weighted_edges: list) -> list:
    """Spanning tree of minimum total weight — uses Union-Find."""
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
mst = kruskal_mst(4, edges)
total_weight = sum(w for _, _, w in mst)
print(f"MST: {mst}")
print(f"total weight: {total_weight}")
```

Kruskal은 간선을 가중치 순으로 보되 사이클을 만드는 간선은 건너뜁니다. 통신망 설계, 배선, 클러스터링에서 자주 쓰이는 이유가 바로 이 단순함과 강력함에 있습니다.

**예상 출력**

```text
MST: [(0, 1, 1), (1, 2, 2), (1, 3, 3)]
total weight: 6
```

- 가중치가 가장 작은 간선부터 보되, `(0, 2, 4)`와 `(2, 3, 5)`는 이미 연결된 정점을 다시 잇거나 더 비싸므로 선택되지 않습니다.
- 결과 간선은 3개여야 하고, 총 가중치는 6이어야 합니다.
- 값이 다르면 Union-Find의 `find/union`이 사이클을 제대로 막고 있는지 먼저 확인해 보세요.

## 주목할 점

- BFS와 DFS는 골격은 같고 사용 자료구조만 다릅니다.
- 트리는 `V - 1 = E` 성질과 연결성으로 검증할 수 있습니다.
- BFS 신장 트리는 가중치가 동일할 때 최단 경로 트리이기도 합니다.
- MST는 그리디 알고리즘이 최적해를 보장하는 대표 사례입니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 방문 표시를 늦게 한다 | 무한 루프가 생긴다 | 진입 즉시 visited에 넣는다 |
| 큐와 스택을 헷갈린다 | BFS와 DFS가 뒤바뀐다 | `popleft`와 `pop`을 명확히 구분한다 |
| 재귀 DFS만 고집한다 | 깊은 그래프에서 스택 오버플로가 난다 | 큰 입력은 반복 DFS를 쓴다 |
| 가중치 그래프에도 BFS를 쓴다 | 최단 경로가 틀린다 | 가중치가 있으면 Dijkstra를 고려한다 |
| MST에서 사이클 검사를 뺀다 | 결과가 트리가 아니게 된다 | Union-Find로 차단한다 |

## 실무에서는 이렇게 사용합니다

- 웹 크롤러는 깊이 제한 BFS를 사용합니다.
- 컴파일러는 AST를 DFS 순회합니다.
- 게임 AI는 상태 공간을 BFS, DFS, A*로 탐색합니다.
- 최소 비용 네트워크 설계는 MST 문제입니다.
- React의 가상 DOM 비교도 트리 비교 문제로 볼 수 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 그래프 문제를 보면 가장 먼저 “BFS인가, DFS인가”를 결정합니다. 레벨별 탐색이나 무가중치 최단 경로는 BFS, 경로 구조 분석이나 사이클 검출은 DFS가 기본입니다. 또한 입력 크기가 크면 재귀 DFS 대신 명시적 스택을 사용하는 식으로 메모리 한계까지 함께 고려합니다.

## 체크리스트

- [ ] 트리의 정의와 `V-1 = E` 성질을 안다
- [ ] BFS와 DFS의 차이를 자료구조 기준으로 설명할 수 있다
- [ ] BFS가 최단 경로를 보장하는 조건을 안다
- [ ] 신장 트리와 MST의 차이를 이해한다
- [ ] Kruskal에서 Union-Find의 역할을 안다

## 연습 문제

1. 정점 5개인 트리에서 간선 수와 최소 리프 수를 구해 보세요.

2. 2차원 미로에서 시작점부터 목표점까지 최단 경로를 찾는 BFS를 작성해 보세요.

3. 도시 6개와 임의의 가중치를 두고 Kruskal로 MST를 손으로 계산해 보세요.

## 정리 및 다음 단계

트리는 연결된 무사이클 그래프이며, BFS와 DFS는 그래프 위를 움직이는 가장 기본적인 탐색입니다. MST는 가중 그래프를 최소 비용으로 연결하는 부분 트리입니다.

다음 글에서는 지금까지 배운 이산수학의 모든 주제가 알고리즘 분석과 실무 의사결정에 어떻게 연결되는지 묶어 보겠습니다.

## 실전 확장: 트리 성질과 탐색 알고리즘 워크드 예시

트리는 "사이클이 없고 연결된 그래프"라는 정의 하나로 많은 성질이 따라옵니다. 특히 정점 수가 `n`이면 간선 수가 `n-1`이라는 사실은 구현 검증에 자주 쓰입니다.

### 트리 성질 확인 코드

```python
from collections import deque

def is_tree(n: int, edges: list[tuple[int, int]]) -> bool:
    if len(edges) != n - 1:
        return False
    g = {i: [] for i in range(n)}
    for a, b in edges:
        g[a].append(b)
        g[b].append(a)
    seen = {0}
    q = deque([0])
    while q:
        v = q.popleft()
        for nxt in g[v]:
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return len(seen) == n
```

간선 수와 연결성 검사를 함께 통과하면 트리로 판단할 수 있습니다.

### BFS 레벨 계산

```python
from collections import deque

def level_of_nodes(tree: dict[int, list[int]], root: int = 0) -> dict[int, int]:
    level = {root: 0}
    q = deque([root])
    while q:
        v = q.popleft()
        for nxt in tree.get(v, []):
            if nxt not in level:
                level[nxt] = level[v] + 1
                q.append(nxt)
    return level
```

레벨 정보는 최소 홉 거리, 조직도 깊이, 권한 상속 범위 계산에 바로 쓰입니다.

### DFS 기반 서브트리 크기

```python
def subtree_size(tree: dict[int, list[int]], root: int = 0) -> dict[int, int]:
    parent = {root: -1}
    order = [root]
    for v in order:
        for nxt in tree.get(v, []):
            if nxt != parent[v]:
                parent[nxt] = v
                order.append(nxt)
    size = {v: 1 for v in order}
    for v in reversed(order):
        p = parent[v]
        if p != -1:
            size[p] += size[v]
    return size
```

후위 순서 누적은 동적 계획법의 트리 버전으로 자주 등장합니다.

### 짧은 증명 앵커

명제: 트리에서 두 정점 사이의 단순 경로는 유일합니다.

증명: 두 개 이상의 서로 다른 단순 경로가 있다고 가정하면 그 둘을 합쳐 사이클이 생깁니다. 트리는 사이클이 없으므로 모순입니다. 따라서 경로는 유일합니다.

## 심화 워크숍: 트리 순회 패턴과 실무 매핑

### 전위/중위/후위 순회 용도

- 전위 순회: 구조 직렬화, 설정 트리 내보내기
- 중위 순회: 이진 탐색 트리 정렬 출력
- 후위 순회: 디렉터리 삭제처럼 자식 처리 후 부모 처리

```python
def preorder(tree: dict[int, tuple[int|None, int|None]], root: int|None, out: list[int]) -> None:
    if root is None:
        return
    out.append(root)
    l, r = tree[root]
    preorder(tree, l, out)
    preorder(tree, r, out)
```

### 최소 공통 조상 개념

두 노드의 최소 공통 조상은 계층형 권한 시스템, 조직도 질의, 파일 경로 분석에서 자주 사용됩니다. 기본 구현은 부모 포인터를 올려 맞추는 방식이며, 대규모 쿼리에서는 희소 테이블 기법을 사용합니다.

### 탐색 성능 체크포인트

- 인접 리스트 구성 비용을 선행 계산했는가
- 재귀 깊이 한계를 고려했는가
- 방문 배열 초기화 비용을 측정했는가
- 루트가 여러 개인 포리스트 입력을 처리하는가

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

## 심화: 오일러 경로와 해밀턴 경로 비교

트리 탐색을 넘어서면 그래프 전체를 한 번씩 방문하는 문제가 등장합니다. 대표적인 두 가지가 오일러 경로와 해밀턴 경로입니다.

오일러 경로는 모든 간선을 정확히 한 번씩 지나는 경로입니다. 존재 조건은 명확합니다. 무향 그래프에서 홀수 차수 정점이 0개이면 오일러 회로, 2개이면 오일러 경로가 존재합니다. 이 조건은 차수만 세면 O(V+E)에 판정할 수 있으므로 실무에서도 빠르게 확인 가능합니다.

해밀턴 경로는 모든 정점을 정확히 한 번씩 방문하는 경로입니다. 오일러와 달리 다항 시간 판정 알고리즘이 알려져 있지 않습니다. NP-완전 문제이기 때문입니다. 택배 경로 최적화, 회로 기판 드릴링 순서 등이 해밀턴 경로의 변형입니다.

```python
def has_euler_path(graph: dict[int, list[int]]) -> str:
    odd_degree = sum(1 for v in graph if len(graph[v]) % 2 != 0)
    if odd_degree == 0:
        return "오일러 회로 존재"
    elif odd_degree == 2:
        return "오일러 경로 존재"
    else:
        return "오일러 경로 없음"

# 예시
g = {0: [1, 2], 1: [0, 2, 3], 2: [0, 1, 3], 3: [1, 2]}
print(has_euler_path(g))  # 오일러 회로 존재
```

이 구분을 기억하면 "모든 간선을 방문"과 "모든 정점을 방문"이 계산 복잡도에서 얼마나 다른지 체감할 수 있습니다. 면접에서도 자주 등장하는 주제이므로 차수 조건을 즉시 떠올릴 수 있도록 연습해 두는 것이 좋습니다.


## 처음 질문으로 돌아가기

- **트리의 정의와 성질은 무엇일까요?**
  - 본문의 기준은 트리와 그래프 탐색를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **BFS는 왜 최단 경로와 연결될까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **DFS는 어떤 문제에서 강할까요?**
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
- [Discrete Math 101 (8/10): 그래프 이론 기초](./08-graph-theory-basics.md)
- **트리와 그래프 탐색 (현재 글)**
- 알고리즘과 이산수학의 연결 (예정)

<!-- toc:end -->

## 참고 자료

- [book-examples: discrete-math-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/discrete-math-101/ko)
- [Discrete Mathematics and Its Applications — Kenneth Rosen, Chapter 11](https://www.mheducation.com/highered/product/discrete-mathematics-its-applications-rosen/M9781259676512.html)
- [Algorithms — Sedgewick & Wayne, Section 4.1 Undirected Graphs](https://algs4.cs.princeton.edu/41graph/)
- [Algorithms — Sedgewick & Wayne, Chapter 4.3](https://algs4.cs.princeton.edu/43mst/)
- [MIT Mathematics for Computer Science — Trees and Graph Traversal](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf)

Tags: Computer Science, 이산수학, 트리, BFS, DFS, 신장 트리
