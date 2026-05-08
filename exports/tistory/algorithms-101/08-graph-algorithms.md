
# 그래프 알고리즘

> Algorithms 101 시리즈 (8/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 도로망, 소셜 네트워크, 의존성 그래프는 모두 다른 영역이지만 같은 알고리즘으로 풀 수 있는 이유는 무엇일까요?

> 그래프는 노드와 간선으로 관계를 표현하는 자료구조이며, 거의 모든 시스템이 그래프 위에서 추론됩니다. 핵심 알고리즘은 BFS(최단 거리·계층 탐색), DFS(연결성·위상 정렬), 다익스트라(가중치 최단 경로), MST(최소 비용 연결망)입니다. 이들 알고리즘은 그래프 표현에 따라 비용이 달라지므로, 인접 리스트 vs 인접 행렬의 트레이드오프를 함께 보아야 합니다. 그래프 알고리즘을 잡으면 추천·검색·라우팅·빌드 시스템까지 같은 어휘로 다룰 수 있습니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 그래프 표현(인접 리스트, 인접 행렬)의 트레이드오프
- BFS와 DFS의 사용 시나리오
- 다익스트라 최단 경로의 동작과 구현
- 최소 신장 트리(크루스칼·프림)의 사고

## 왜 중요한가

대부분의 실무 문제는 결국 그래프로 환원됩니다. 마이크로서비스의 호출 의존성, 빌드 도구의 태스크 그래프, 추천 시스템의 사용자-아이템 이분 그래프, 라우팅 시스템의 도로망까지 모두 그렇습니다. 그래프 알고리즘을 모르면 이런 시스템들의 핵심을 다룰 수 없습니다.

> 그래프는 시스템 사고의 공용 언어입니다.

## 개념 한눈에 보기

> 그래프는 V개의 노드와 E개의 간선으로 이루어집니다. 인접 리스트는 O(V+E) 메모리, 인접 행렬은 O(V²)입니다. BFS는 큐로 구현되어 가중치 없는 최단 거리를 O(V+E)에 구하고, DFS는 스택(재귀)으로 구현되어 연결성과 위상 정렬에 쓰입니다. 다익스트라는 우선순위 큐 + 그리디로 음이 아닌 가중치 최단 경로를 풀고, MST는 크루스칼(union-find)·프림(우선순위 큐)이 대표입니다.

```text
그래프 표현
    인접 리스트 : 메모리 O(V+E), 희소 그래프에 유리
    인접 행렬   : 메모리 O(V²),   조회 O(1), 밀집 그래프에 유리

핵심 탐색
    BFS  큐    가중치 없는 최단 거리, 계층 탐색
    DFS  스택  연결성, 사이클, 위상 정렬

가중치 그래프
    Dijkstra   음이 아닌 가중치 최단 경로  O((V+E) log V)
    MST        모든 노드를 잇는 최소 비용  Kruskal/Prim
```

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| 노드/간선 | 객체와 관계 |
| 인접 리스트 | 각 노드의 이웃 목록 |
| BFS/DFS | 너비/깊이 우선 탐색 |
| 다익스트라 | 음이 아닌 가중치 최단 경로 |
| MST | 모든 노드를 잇는 최소 비용 부분 그래프 |

## Before / After

**Before — 인접 행렬로 희소 그래프 표현, 메모리 낭비:**

```python
# V=10000, E=30000인 희소 그래프에 행렬 표현
adj = [[0] * 10000 for _ in range(10000)]   # 1억 칸, 대부분 0
```

**After — 인접 리스트:**

```python
from collections import defaultdict
adj = defaultdict(list)
adj[0].append(1)
adj[1].append(2)
# 메모리 O(V+E)
```

## 실습: 단계별로 따라하기

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

BFS는 가중치 없는 최단 거리를 자연스럽게 구합니다. 큐는 deque로 양쪽 O(1).

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
    return order if len(order) == n else None   # None이면 사이클

# A → B, A → C, B → D, C → D
print(topological_sort(4, [(0, 1), (0, 2), (1, 3), (2, 3)]))   # [0, 1, 2, 3]
```

빌드 시스템의 실행 순서, 학습 과목 선수 관계 등이 위상 정렬로 풀립니다.

### 3단계: 다익스트라 — 우선순위 큐 활용

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

음이 아닌 가중치라면 다익스트라가 표준입니다. 음의 가중치가 있으면 Bellman-Ford나 Johnson을 써야 합니다.

### 4단계: 크루스칼 MST — Union-Find 활용

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

가장 가벼운 간선부터 사이클을 만들지 않으면 추가합니다. 그리디 + Union-Find의 고전 조합.

### 5단계: 실전 — 도시 간 최소 연결 비용

```python
roads = [
    (0, 1, 10), (0, 2, 6), (0, 3, 5),
    (1, 3, 15), (2, 3, 4),
]
print("MST cost:", kruskal(4, roads))   # 19 (5 + 6 + 4 ... 등)
```

MST는 통신망 설계, 클러스터 거리 분석, 회로 배선 같은 실무 문제에 그대로 쓰입니다.

## 이 코드에서 주목할 점

- 그래프 표현 선택이 메모리·시간을 결정
- BFS는 큐, DFS는 스택(재귀) — 도구가 다르면 답이 바뀜
- 다익스트라의 핵심은 우선순위 큐와 "이미 확정된 거리" 검사
- Union-Find는 그래프·연결성 문제의 보편적 도구

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 인접 행렬을 희소 그래프에 사용 | OOM | 인접 리스트 사용 |
| 다익스트라에 음의 가중치 | 잘못된 결과 | Bellman-Ford로 전환 |
| BFS 거리에 weight 가정 | 잘못된 답 | 가중치 있으면 다익스트라 |
| Union-Find 경로 압축 누락 | O(n) per find | path compression + union by rank |
| 사이클 그래프에 위상 정렬 | None 반환 처리 누락 | 결과 길이로 사이클 탐지 |

## 실무에서는 이렇게 쓰입니다

- 빌드 시스템의 태스크 의존성 (위상 정렬)
- 마이크로서비스 호출 그래프 분석
- 지도 앱의 최단 경로 (다익스트라 + 휴리스틱 = A*)
- 추천 시스템의 사용자-아이템 그래프 임베딩
- 회로 배선·통신망 설계 (MST)

## 시니어 엔지니어는 이렇게 생각합니다

시니어는 새 문제를 만나면 "이건 그래프인가?"를 먼저 묻습니다. 노드와 간선을 어떻게 정의하느냐가 풀이의 90%이며, 한 번 그래프로 보이면 표준 알고리즘이 즉시 적용됩니다.

또한 시니어는 그래프 크기를 먼저 가늠합니다. V·E의 크기, 희소도, 가중치 분포를 보고 표현과 알고리즘을 선택합니다. 같은 문제도 V=10³와 V=10⁷에서 사용 가능한 알고리즘이 완전히 달라지기 때문입니다.

## 체크리스트

- [ ] 인접 리스트와 행렬의 트레이드오프를 안다
- [ ] BFS와 DFS의 사용처를 구분할 수 있는가
- [ ] 다익스트라의 동작을 한 줄로 설명할 수 있는가
- [ ] MST 알고리즘 두 가지를 적어도 하나는 구현할 수 있는가
- [ ] 새 문제를 그래프로 환원하는 감각이 있는가

## 연습 문제

1. 양방향 그래프에서 두 노드 사이의 모든 최단 경로 개수를 구하는 BFS 변형을 작성하세요. 같은 거리로 도달하는 경로 수를 누적합니다.

2. 사이클이 있을 수 있는 방향 그래프에서 위상 정렬이 가능한지 판정하고, 가능하면 한 가지 위상 순서를 출력하는 함수를 작성하세요.

3. 음이 아닌 가중치 그래프에서 시작 노드로부터의 최단 경로 트리를 다익스트라로 구성하고, 각 노드의 부모 포인터를 함께 출력하세요.

## 정리 및 다음 단계

그래프 알고리즘은 노드와 간선이라는 단순한 어휘로 거의 모든 시스템 문제를 표현할 수 있게 해줍니다. 표현·탐색·최단 경로·MST의 네 어휘만 갖춰도 실무의 많은 문제가 풀립니다. 더 깊이 들어가면 흐름 네트워크, 강한 연결 요소, 매칭 같은 고급 주제로 확장됩니다.

다음 글에서는 문자열 알고리즘 기초를 살펴봅니다. 단순 매칭의 비용, KMP의 실패 함수, Z 함수, 그리고 실무에서 가장 자주 쓰이는 정규식·트라이까지 다룹니다.

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
## 참고 자료

- [Python `heapq` documentation](https://docs.python.org/3/library/heapq.html)
- [Wikipedia — Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Sedgewick & Wayne — Algorithms 4ed, Chapter 4](https://algs4.cs.princeton.edu/40graphs/)
- [CLRS — Introduction to Algorithms, Chapters 22-24](https://mitpress.mit.edu/books/introduction-algorithms-third-edition)

Tags: Computer Science, 알고리즘, 그래프, BFS, 다익스트라, 최소 신장 트리

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
