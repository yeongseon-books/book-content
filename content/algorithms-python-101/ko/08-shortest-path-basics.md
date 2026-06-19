---
series: algorithms-python-101
episode: 8
title: "Algorithms with Python 101 (8/10): 최단 경로 기초"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - Algorithms
  - Shortest Path
  - Dijkstra
  - heapq
seo_description: 가중치 그래프 최단 경로를 찾는 다익스트라 알고리즘 원리를 파이썬으로 구현합니다. heapq 우선순위 큐 활용과 경로 복원 방법을 익힙니다.
last_reviewed: '2026-05-12'
---

# Algorithms with Python 101 (8/10): 최단 경로 기초

경로 계획, 네트워크 지연, 물류 최적화는 모두 결국 같은 질문으로 모입니다. 여기서 저기까지 가는 가장 싼 길은 무엇인가라는 질문입니다.

이 글은 Algorithms with Python 101 시리즈의 여덟 번째 글입니다. 여기서는 가중치 그래프의 최단 경로 문제를 정리하고, `heapq`를 사용해 Python으로 다익스트라 알고리즘을 구현해 보겠습니다.

간선 가중치가 중요해지는 순간 BFS만으로는 부족합니다. 다음에 볼 후보 경로를 우선순위로 관리해야 하고, 그 지점에서 다익스트라 알고리즘이 힘을 발휘합니다.

![Algorithms with Python 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-python-101/08/08-01-concept-overview.ko.png)
*Algorithms with Python 101 8장 흐름 개요*

## 이 글에서 다룰 문제

- 가중치 그래프의 최단 경로 문제는 어떻게 정의할까요?
- 다익스트라 알고리즘은 어떤 원리로 동작할까요?
- Python의 `heapq`로 우선순위 큐를 어떻게 구현할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

> 다익스트라 알고리즘은 음수 가중치가 없는 그래프에서, 하나의 시작점으로부터 모든 노드까지의 최단 경로를 구합니다.

## 개념 한눈에 보기

> 최단 경로 = 시작점에서 도착점까지 가는 경로 중 간선 가중치 합이 가장 작은 경로

```text
Weighted graph:
A --4-- B --3-- D
|       |
2       1
|       |
C --5-- E

A→D shortest path: A→B→D (cost 7)
A→E shortest path: A→B→E (cost 5)
A→C via BFS: A→C (hops 1, cost 2) — BFS와 동일
A→D via BFS: A→B→D (hops 2) — 하지만 A→C→E→B→D (hops 4)는 비용 더 쌈? No
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| Weighted graph | 각 간선에 비용(가중치)이 있는 그래프입니다 |
| Dijkstra's algorithm | 음수 가중치가 없는 단일 시작점 최단 경로 알고리즘입니다 |
| Priority queue | 가장 작은 값을 먼저 꺼내는 자료구조입니다 |
| Relaxation | 더 짧은 경로를 찾았을 때 거리 추정치를 갱신하는 과정입니다 |
| Negative weight | 다익스트라가 올바르게 처리하지 못하는 음수 비용 간선입니다 |

## 최단 경로 알고리즘 선택 가이드

| 조건 | 알고리즘 | 복잡도 |
|------|----------|--------|
| 무가중치 | BFS | `O(V+E)` |
| 비음수 가중치 | Dijkstra | `O((V+E) log V)` |
| 음수 가중치 포함 | Bellman-Ford | `O(VE)` |
| 모든 쌍 | Floyd-Warshall | `O(V^3)` |

## 적용 전후 비교

가중치 그래프에서 최단 경로를 찾는 두 가지 접근입니다.

```python
# before: BFS — 가중치를 무시해 잘못된 답을 냄
def shortest_wrong(graph, start, end):
    from collections import deque
    queue = deque([(start, [start])])
    visited = {start}
    while queue:
        node, path = queue.popleft()
        if node == end:
            return path  # 최소 홉 수, 최소 비용이 아님!
        for neighbor, _ in graph[node]:  # 가중치 무시
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return None
```

```python
# after: Dijkstra — 가중치를 고려한 최단 경로
import heapq

def shortest_dijkstra(graph, start, end):
    dist = {start: 0}
    heap = [(0, start)]
    while heap:
        cost, node = heapq.heappop(heap)
        if node == end:
            return cost
        if cost > dist.get(node, float("inf")):
            continue  # stale entry 건너뜀
        for neighbor, weight in graph[node]:
            new_cost = cost + weight
            if new_cost < dist.get(neighbor, float("inf")):
                dist[neighbor] = new_cost
                heapq.heappush(heap, (new_cost, neighbor))
    return float("inf")
```

## 단계별 실습

### 단계 1: 가중 그래프 표현하기

```python
graph: dict[str, list[tuple[str, int]]] = {
    "A": [("B", 4), ("C", 2)],
    "B": [("A", 4), ("D", 3), ("E", 1)],
    "C": [("A", 2), ("E", 5)],
    "D": [("B", 3)],
    "E": [("B", 1), ("C", 5)],
}

for node, neighbors in graph.items():
    edges = [f"{n}({w})" for n, w in neighbors]
    print(f"  {node} -> {', '.join(edges)}")
```

### 단계 2: Dijkstra 알고리즘

```python
import heapq

def dijkstra(
    graph: dict[str, list[tuple[str, int]]], start: str
) -> dict[str, int]:
    """Dijkstra's algorithm — O((V+E) log V)."""
    dist: dict[str, int] = {start: 0}
    heap: list[tuple[int, str]] = [(0, start)]

    while heap:
        cost, node = heapq.heappop(heap)
        if cost > dist.get(node, float("inf")):
            continue  # 이미 더 짧은 경로가 확정된 경우

        for neighbor, weight in graph[node]:
            new_cost = cost + weight
            if new_cost < dist.get(neighbor, float("inf")):
                dist[neighbor] = new_cost
                heapq.heappush(heap, (new_cost, neighbor))

    return dist

distances = dijkstra(graph, "A")
for node, d in sorted(distances.items()):
    print(f"  A -> {node}: {d}")
# A -> A: 0
# A -> B: 4
# A -> C: 2
# A -> D: 7
# A -> E: 5
```

### 단계 3: 경로 복원

```python
import heapq

def dijkstra_with_path(
    graph: dict[str, list[tuple[str, int]]], start: str
) -> tuple[dict[str, int], dict[str, list[str]]]:
    """Dijkstra with path reconstruction."""
    dist: dict[str, int] = {start: 0}
    prev: dict[str, str | None] = {start: None}
    heap: list[tuple[int, str]] = [(0, start)]

    while heap:
        cost, node = heapq.heappop(heap)
        if cost > dist.get(node, float("inf")):
            continue
        for neighbor, weight in graph[node]:
            new_cost = cost + weight
            if new_cost < dist.get(neighbor, float("inf")):
                dist[neighbor] = new_cost
                prev[neighbor] = node  # 거리 갱신 시점에만 prev 업데이트
                heapq.heappush(heap, (new_cost, neighbor))

    paths: dict[str, list[str]] = {}
    for node in dist:
        path: list[str] = []
        current: str | None = node
        while current is not None:
            path.append(current)
            current = prev.get(current)
        paths[node] = list(reversed(path))

    return dist, paths

distances, paths = dijkstra_with_path(graph, "A")
for node in sorted(paths):
    print(f"  A -> {node}: cost={distances[node]}, path={' -> '.join(paths[node])}")
```

### 단계 4: 그리드 최단 경로

```python
import heapq

def grid_shortest_path(grid: list[list[int]]) -> int:
    """격자에서 좌상단에서 우하단까지의 최소 비용 경로."""
    rows, cols = len(grid), len(grid[0])
    dist = [[float("inf")] * cols for _ in range(rows)]
    dist[0][0] = grid[0][0]
    heap: list[tuple[int, int, int]] = [(grid[0][0], 0, 0)]

    while heap:
        cost, r, c = heapq.heappop(heap)
        if r == rows - 1 and c == cols - 1:
            return cost
        if cost > dist[r][c]:
            continue
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                new_cost = cost + grid[nr][nc]
                if new_cost < dist[nr][nc]:
                    dist[nr][nc] = new_cost
                    heapq.heappush(heap, (new_cost, nr, nc))

    return dist[rows - 1][cols - 1]

grid = [
    [1, 3, 1],
    [1, 5, 1],
    [4, 2, 1],
]
print(grid_shortest_path(grid))  # 7 (1→1→1→1→2→1)
```

### 단계 5: heapq 기본 사용법

```python
import heapq

# 최소 힙 (Python 기본)
heap: list[int] = []
for x in [5, 1, 3, 7, 2]:
    heapq.heappush(heap, x)

while heap:
    print(heapq.heappop(heap), end=" ")  # 1 2 3 5 7

# 최대 힙 흉내내기 (음수 사용)
max_heap: list[int] = []
for x in [5, 1, 3, 7, 2]:
    heapq.heappush(max_heap, -x)

print(heapq.heappop(max_heap) * -1)  # 7
```

## 단계별 실행 추적 — 다익스트라

`dijkstra(graph, "A")` 실행 추적:

```text
그래프: A-[(B,4),(C,2)], B-[(A,4),(D,3),(E,1)], C-[(A,2),(E,5)], ...

초기: dist={A:0}, heap=[(0,A)]

Step 1: pop (0,A)
  이웃 B: 0+4=4 < inf → dist[B]=4, push (4,B)
  이웃 C: 0+2=2 < inf → dist[C]=2, push (2,C)
  heap=[(2,C),(4,B)]

Step 2: pop (2,C)  ← 가장 작은 것 먼저!
  이웃 A: 2+2=4 > dist[A]=0 → skip
  이웃 E: 2+5=7 < inf → dist[E]=7, push (7,E)
  heap=[(4,B),(7,E)]

Step 3: pop (4,B)
  이웃 A: 4+4=8 > 0 → skip
  이웃 D: 4+3=7 < inf → dist[D]=7, push (7,D)
  이웃 E: 4+1=5 < 7 → dist[E]=5 (갱신!), push (5,E)
  heap=[(5,E),(7,E),(7,D)]  ← 오래된 (7,E)는 stale

Step 4: pop (5,E)
  모든 이웃 갱신 불필요

Step 5: pop (7,E)  ← stale: 5 > dist[E]=5 → skip!

Step 6: pop (7,D)
  이웃 B: 7+3=10 > 4 → skip

최종: dist={A:0, B:4, C:2, D:7, E:5}
```

## 코딩 테스트 풀이 예시

**문제**: 장애물이 있는 격자에서 최단 경로를 구하라 (0=통로, 1=장애물).

```python
import heapq
from collections import deque

def shortest_path_grid(grid: list[list[int]]) -> int:
    """
    BFS로 격자 최단 경로 (무가중치).
    0=통로, 1=장애물
    도달 불가 시 -1 반환
    """
    rows, cols = len(grid), len(grid[0])
    if grid[0][0] == 1 or grid[rows-1][cols-1] == 1:
        return -1

    dist = [[-1] * cols for _ in range(rows)]
    dist[0][0] = 1
    queue = deque([(0, 0)])

    while queue:
        r, c = queue.popleft()
        if r == rows - 1 and c == cols - 1:
            return dist[r][c]
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = r + dr, c + dc
                if (0 <= nr < rows and 0 <= nc < cols
                        and grid[nr][nc] == 0
                        and dist[nr][nc] == -1):
                    dist[nr][nc] = dist[r][c] + 1
                    queue.append((nr, nc))

    return -1


grid = [
    [0, 0, 0],
    [1, 1, 0],
    [0, 0, 0],
]
print(shortest_path_grid(grid))  # 5
```

**문제**: K번째 최단 경로를 찾아라.

```python
import heapq
from collections import defaultdict

def kth_shortest_path(
    graph: dict[int, list[tuple[int, int]]], start: int, end: int, k: int
) -> int:
    """
    K번째 최단 경로 비용을 반환합니다.
    도달 불가 또는 k번째 없으면 -1 반환.
    시간 복잡도: O(k * E log V)
    """
    # 각 노드의 도착 횟수를 추적
    arrival_count: dict[int, int] = defaultdict(int)
    heap = [(0, start)]  # (비용, 노드)

    while heap:
        cost, node = heapq.heappop(heap)
        arrival_count[node] += 1

        if node == end and arrival_count[node] == k:
            return cost

        # k번 이상 도착했으면 더 탐색 불필요
        if arrival_count[node] > k:
            continue

        for neighbor, weight in graph.get(node, []):
            if arrival_count[neighbor] < k:
                heapq.heappush(heap, (cost + weight, neighbor))

    return -1


g = {
    1: [(2, 1), (3, 3)],
    2: [(3, 1), (4, 5)],
    3: [(4, 2)],
    4: [],
}
print(kth_shortest_path(g, 1, 4, 1))  # 5 (1→2→3→4)
print(kth_shortest_path(g, 1, 4, 2))  # 6 (1→3→4 via different path)
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 음수 가중치에 다익스트라 사용 | 잘못된 결과를 냅니다 | Bellman-Ford를 사용합니다 |
| stale entry 건너뛰기 체크 생략 | 중복 처리가 늘어 비효율적입니다 | 힙에서 꺼낸 비용과 dist를 비교합니다 |
| 우선순위 큐를 리스트로 흉내 냄 | 삽입과 삭제가 비효율적입니다 | `heapq`를 사용합니다 |
| 시작점 초기 거리를 잘못 둠 | 모든 경로 계산이 흔들립니다 | 시작점 거리를 0으로 둡니다 |
| `prev` 갱신을 무조건 수행 | 경로가 왜곡됩니다 | 거리 갱신 시점에만 `prev` 변경합니다 |

## 실무에서는 이렇게 연결됩니다

- 내비게이션 앱은 다익스트라나 A*로 운전 경로를 계산합니다.
- OSPF 같은 네트워크 라우팅 프로토콜도 다익스트라를 사용합니다.
- 물류 시스템은 창고와 배송 지점 사이의 최소 비용 경로를 계산합니다.
- 게임 엔진은 NPC 이동 경로를 찾습니다.
- 소셜 네트워크는 사용자 간 최소 연결 경로를 분석할 수 있습니다.

## 현업에서는 이렇게 생각합니다

실제로는 다익스트라를 매번 직접 구현하지 않아도 됩니다. 중요한 능력은 문제를 보고 "이건 최단 경로 문제다"라고 알아보는 일입니다. 그 순간 적절한 라이브러리와 알고리즘을 선택할 수 있기 때문입니다.

## 운영 체크리스트

- [ ] 다익스트라 알고리즘의 동작 원리를 설명할 수 있습니다
- [ ] Python의 `heapq`로 다익스트라를 구현할 수 있습니다
- [ ] 시작점에서 도착점까지 최단 경로를 복원할 수 있습니다
- [ ] 음수 가중치에서 다익스트라의 한계를 설명할 수 있습니다
- [ ] 문제 조건에 맞는 최단 경로 알고리즘을 고를 수 있습니다

## 연습 문제

1. 가중치가 있는 방향 그래프에서 특정 두 노드 사이의 최단 경로와 비용을 구해 보세요.
2. 장애물이 있는 격자에서 최단 경로를 구해 보세요.
3. 다익스트라를 이용해 k번째 최단 경로를 찾는 함수를 작성해 보세요.

## 정리와 다음 글

다익스트라는 음수 가중치가 없는 그래프에서 `O((V+E) log V)`로 최단 경로를 구합니다. 핵심은 우선순위 큐로 가장 가까운 미확정 노드를 먼저 처리하는 데 있습니다. 다음 글에서는 매 단계의 지역 최적 선택이 핵심인 그리디 알고리즘을 살펴봅니다.

<!-- toc:begin -->
## 시리즈 목차

- [Algorithms with Python 101 (1/10): 알고리즘이란 무엇인가?](./01-what-are-algorithms.md)
- [Algorithms with Python 101 (2/10): 시간 복잡도와 Big-O](./02-time-complexity-and-big-o.md)
- [Algorithms with Python 101 (3/10): 선형 탐색과 이진 탐색](./03-linear-and-binary-search.md)
- [Algorithms with Python 101 (4/10): 정렬 알고리즘](./04-sorting-algorithms.md)
- [Algorithms with Python 101 (5/10): 재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- [Algorithms with Python 101 (6/10): 동적 계획법 기초](./06-dynamic-programming-basics.md)
- [Algorithms with Python 101 (7/10): 그래프 탐색 — BFS와 DFS](./07-graph-traversal-bfs-dfs.md)
- **Algorithms with Python 101 (8/10): 최단 경로 기초 (현재 글)**
- [Algorithms with Python 101 (9/10): 그리디 알고리즘](./09-greedy-algorithms.md)
- [코딩 테스트 문제 접근법](./10-coding-test-strategies.md)

<!-- toc:end -->

## 참고 자료

- [Wikipedia — Dijkstra's Algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Python Documentation — heapq](https://docs.python.org/3/library/heapq.html)
- [Visualgo — Single-Source Shortest Path](https://visualgo.net/en/sssp)
- [Real Python — Priority Queue in Python](https://realpython.com/python-heapq-module/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-python-101/ko/08-shortest-path-basics)

Tags: Python, Algorithms, Shortest Path, Dijkstra, heapq
