---
series: algorithms-101
episode: 8
title: "Algorithms 101 (8/10): 그래프 알고리즘"
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
  - 알고리즘
  - 그래프
  - BFS
  - 다익스트라
  - 최소 신장 트리
seo_description: 그래프 표현, BFS와 DFS의 선택 기준, 다익스트라 최단 경로, 그리고 Kruskal·Prim 기반 MST를 정리합니다.
last_reviewed: '2026-05-12'
---

# Algorithms 101 (8/10): 그래프 알고리즘

이 글은 Algorithms 101 시리즈의 8번째 글입니다.

도로망, 소셜 네트워크, 의존성 그래프는 전혀 다른 문제처럼 보이는데 왜 같은 알고리즘으로 풀릴까요? 여기서는 그래프 표현, 순회, 최단 경로, 최소 신장 트리를 정리합니다.

![Algorithms 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-101/08/08-01-big-picture.ko.png)
*Algorithms 101 8장 흐름 개요*

## 먼저 던지는 질문

- 인접 리스트와 인접 행렬은 어떤 트레이드오프를 가질까요?
- BFS와 DFS는 각각 언제 써야 할까요?
- 다익스트라는 어떻게 동작하고 어떻게 구현할까요?

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

## 개선 전 / 개선 후

**Before — 희소 그래프를 인접 행렬로 표현:**

```python
# V=10000, E=30000 행렬로서의 희소 그래프
adj = [[0] * 10000 for _ in range(10000)]   # 100 million cells, mostly zero
```

**After — 인접 리스트 사용:**

```python
from collections import defaultdict
adj = defaultdict(list)
adj[0].append(1)
adj[1].append(2)
# 메모리 O(V+E)
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

## 실전 확장 워크북

이 절은 그래프 탐색/최단경로를 실제 문제 풀이와 운영 감각으로 연결하기 위한 보강 파트입니다. 개념을 암기하는 대신, 입력 크기·자료 구조·검증 순서를 함께 다루어 같은 유형의 문제를 반복적으로 안정적으로 풀 수 있게 만드는 데 목적이 있습니다. 핵심은 "정답 코드 한 번"이 아니라 "다음 문제에서도 재사용 가능한 판단 프레임"을 확보하는 것입니다.

### 1) 시간 복잡도와 입력 제약을 먼저 맞추기

| 입력 조건 | 우선 배제할 접근 | 현실적인 후보 | 확인 포인트 |
| --- | --- | --- | --- |
| n <= 10^3 | 없음(학습 목적 실험 가능) | 브루트포스, 정렬, 해시 | 구현 명확성 |
| n <= 10^5 | O(n^2) 대부분 배제 | O(n log n), O(n), BFS/DFS | 경계값 테스트 |
| n <= 10^6 이상 | O(n log n)도 부담 가능 | 단일 패스, 압축, 스트리밍 | 메모리 상한 |

복잡도 판단은 코드 스타일 논쟁보다 우선합니다. 같은 팀에서 코드 품질 기준이 달라도, 입력 제약과 차수를 맞추는 원칙은 공통으로 적용됩니다. 이 단계를 건너뛰면 구현이 아무리 깔끔해도 제출 실패나 운영 지연으로 이어집니다.

### 2) 단계별 추적 표로 경계 버그를 조기에 찾기

| 단계 | 관찰 값 | 기대 신호 | 실패 신호 |
| --- | --- | --- | --- |
| 초기화 | 포인터/상태/큐/테이블 | 문제 정의와 일치 | 초기값 누락 |
| 1회 반복 | 상태 전이 | 단조 증가 또는 감소 | 제자리 반복 |
| 종료 직전 | 반환 후보 | 문제 요구와 직접 연결 | 보조값 반환 |

경계 버그는 대부분 "한 줄"에서 발생하지만, 원인은 상태 전이 설계에 있습니다. 그래서 디버깅할 때는 출력값 하나만 보지 말고, 전이 로그를 함께 봐야 합니다. 특히 인덱스 기반 문제는 `lo, mid, hi`, DP 문제는 `state, transition`, 그래프 문제는 `queue size, visited count`를 같이 기록하면 원인 분리가 훨씬 빨라집니다.

### 3) Python 구현 앵커

```python
from collections import deque

def bfs_levels(graph, start):
    q = deque([start])
    dist = {start: 0}
    while q:
        u = q.popleft()
        for v in graph[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist
```

코드는 짧아도 충분합니다. 중요한 점은 구현 전에 불변식(invariant)을 문장으로 먼저 고정하는 것입니다. 예를 들어 "현재 단계가 끝나면 최소 비용이 보장된다" 같은 문장이 없으면, 코드가 돌아가도 왜 맞는지 설명할 수 없고, 변형 문제에서 무너지기 쉽습니다.

### 4) LeetCode 스타일 매핑

| 문제 | 핵심 패턴 | 첫 시도에서 자주 틀리는 지점 |
| --- | --- | --- |
| 200 Number of Islands | 제약을 통한 후보 축소 | 입력 조건을 늦게 반영 |
| 994 Rotting Oranges | 상태/포인터 유지 | 경계 인덱스 처리 |
| 743 Network Delay Time | 자료구조 선택 | 복잡도 목표 미달 |

문제 매핑의 목적은 정답 암기가 아닙니다. 같은 구조를 빠르게 인식하고, "왜 이 패턴을 쓰는가"를 재현하는 데 있습니다. 시리즈 전체를 관통하는 실력 차이는 여기서 발생합니다.

### 5) 비교 벤치마크를 읽는 기준

| 비교 항목 | A 접근 | B 접근 | 의사결정 기준 |
| --- | --- | --- | --- |
| 시간 | 평균적으로 빠름 | 최악 케이스 안정적 | 입력 분포가 고정인지 |
| 메모리 | 추가 배열 필요 | 제자리 처리 가능 | 메모리 제한 강도 |
| 구현 난이도 | 짧음 | 디버깅 난이도 높음 | 팀 유지보수 역량 |

벤치마크 숫자는 환경에 따라 달라집니다. 하지만 차수와 메모리 계층에서 발생하는 방향성은 반복됩니다. 그래서 한 번 측정한 결과를 절대값으로 외우기보다, 어떤 조건에서 우위가 바뀌는지(입력 크기, 정렬 여부, 중복 비율)를 함께 기록해야 다음 의사결정에 도움이 됩니다.

### 6) 제출/배포 전 점검 루틴

1. 문제 제약을 한 줄로 요약하고 불가능한 차수를 먼저 제거합니다.
2. 핵심 자료구조 선택 이유를 "삽입/조회/삭제 비용" 기준으로 적습니다.
3. 경계 입력 3종(빈값, 최소값, 중복/극단값) 테스트를 고정합니다.
4. 시간·공간 복잡도를 코드 옆에 기록하고, 실제 측정값을 짧게 남깁니다.
5. 같은 패턴의 변형 문제를 1개 더 풀어 일반화 여부를 확인합니다.

이 루틴을 꾸준히 적용하면 "이번 문제를 맞춤"에서 끝나지 않고 "같은 유형을 안정적으로 재현"하는 상태로 넘어갈 수 있습니다. 알고리즘 학습은 지식 축적이 아니라 판단 체계 구축이라는 점을 계속 기억하는 것이 중요합니다.

## 처음 질문으로 돌아가기

- **인접 리스트와 인접 행렬은 어떤 트레이드오프를 가질까요?**
  - 희소 그래프에서는 `defaultdict(list)` 기반 인접 리스트가 `O(V+E)` 메모리로 훨씬 유리하고, 인접 행렬은 `O(V^2)`를 쓰는 대신 간선 존재 여부를 O(1)에 확인할 수 있습니다. 본문이 `V=10000, E=30000` 예시를 든 이유가 바로 희소 그래프에서 행렬이 얼마나 낭비적인지 보여 주기 위해서였습니다.
- **BFS와 DFS는 각각 언제 써야 할까요?**
  - `bfs(adj, 0)`처럼 가중치 없는 최단 거리나 층별 탐색이 필요하면 BFS가 맞고, 연결성·사이클·위상 정렬처럼 깊이 구조를 따라가야 하면 DFS 계열 사고가 맞습니다. 본문에서도 큐를 쓰는 BFS와 위상 정렬 문제를 나눠 설명했습니다.
- **다익스트라는 어떻게 동작하고 어떻게 구현할까요?**
  - `heapq` 우선순위 큐에서 가장 짧은 거리 후보를 꺼내고, `if d > dist[u]: continue`로 오래된 항목을 버리며, 더 짧은 `nd`가 나오면 다시 push하는 방식입니다. 그래서 음이 아닌 가중치 그래프에서는 `dijkstra()`가 표준 답안이 됩니다.

<!-- toc:begin -->
## 시리즈 목차

- [Algorithms 101 (1/10): 알고리즘이란 무엇인가?](./01-what-is-an-algorithm.md)
- [Algorithms 101 (2/10): 시간 복잡도와 공간 복잡도](./02-time-and-space-complexity.md)
- [Algorithms 101 (3/10): 탐색 알고리즘](./03-search-algorithms.md)
- [Algorithms 101 (4/10): 정렬 알고리즘](./04-sorting-algorithms.md)
- [Algorithms 101 (5/10): 재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- [Algorithms 101 (6/10): 동적 계획법](./06-dynamic-programming.md)
- [Algorithms 101 (7/10): 그리디 알고리즘](./07-greedy-algorithms.md)
- **그래프 알고리즘 (현재 글)**
- 문자열 알고리즘 기초 (예정)
- 알고리즘 문제 풀이 전략 (예정)

<!-- toc:end -->

## 참고 자료

- [book-examples — algorithms-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-101/ko)
- [Python `heapq` documentation](https://docs.python.org/3/library/heapq.html)
- [Wikipedia — Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Sedgewick & Wayne — Algorithms 4ed, Chapter 4](https://algs4.cs.princeton.edu/40graphs/)
- [CLRS — Introduction to Algorithms, Chapters 22-24](https://mitpress.mit.edu/books/introduction-algorithms-third-edition)

Tags: Computer Science, 알고리즘, 그래프, BFS, 다익스트라, 최소 신장 트리
