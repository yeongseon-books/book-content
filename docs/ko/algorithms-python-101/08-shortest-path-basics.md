---
series: algorithms-python-101
episode: 8
title: 최단 경로 기초
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Python
  - 알고리즘
  - 최단 경로
  - 다익스트라
  - heapq
seo_description: Python으로 다익스트라 알고리즘을 구현하고 최단 경로를 구합니다.
last_reviewed: '2026-05-04'
---

# 최단 경로 기초

> Algorithms with Python 101 시리즈 (8/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 가중 그래프에서 출발지부터 모든 노드까지의 최단 거리를 어떻게 구할까요?

> BFS는 가중치 없는 그래프에서만 최단 경로를 보장합니다. 간선에 가중치가 있으면 다익스트라 알고리즘이 필요합니다. 이 글에서는 다익스트라 알고리즘을 Python의 heapq로 구현합니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 가중 그래프에서 최단 경로 문제의 정의
- 다익스트라 알고리즘의 원리
- Python heapq를 활용한 구현
- 경로 추적과 음의 가중치 한계

## 왜 중요한가

내비게이션, 네트워크 라우팅, 물류 최적화 등 현실 세계의 경로 문제는 가중 그래프로 모델링됩니다. 다익스트라 알고리즘은 이런 문제를 효율적으로 해결하는 가장 기본적인 알고리즘입니다.

> 다익스트라 = 음이 아닌 가중치 그래프에서 단일 출발점 최단 경로를 구하는 알고리즘

다익스트라는 그리디 전략과 우선순위 큐를 결합하여 O((V+E) log V)에 동작합니다. 이 원리는 A* 알고리즘 등 고급 경로 탐색의 기반이 됩니다.

## 핵심 개념 잡기

> 최단 경로 = 출발 노드에서 도착 노드까지 간선 가중치의 합이 최소인 경로

```
가중 그래프:
A --4-- B --3-- D
|       |
2       1
|       |
C --5-- E

A→D 최단 경로: A→B→D (비용 7)
A→E 최단 경로: A→C→E 또는 A→B→E (비용 7 또는 5)
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| 가중 그래프(weighted graph) | 간선에 비용(가중치)이 부여된 그래프입니다 |
| 다익스트라(Dijkstra) | 음이 아닌 가중치에서 단일 출발점 최단 경로를 구합니다 |
| 우선순위 큐(priority queue) | 가장 작은 값을 먼저 꺼내는 자료구조입니다 |
| 완화(relaxation) | 더 짧은 경로를 발견하면 거리를 갱신하는 연산입니다 |
| 음의 가중치(negative weight) | 다익스트라에서 처리할 수 없는 음수 간선입니다 |

## Before / After

가중 그래프에서 최단 경로를 구하는 두 가지 방법을 비교합니다.

```python
# before: BFS — 가중치를 무시하여 잘못된 결과
def shortest(graph, start, end):
    from collections import deque
    queue = deque([(start, [start])])
    visited = {start}
    while queue:
        node, path = queue.popleft()
        if node == end:
            return path  # 간선 수 최소이지 비용 최소가 아님
        for neighbor, _ in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return None
```

```python
# after: 다익스트라 — 가중치 기반 최단 경로
import heapq

def shortest(graph, start, end):
    dist = {start: 0}
    heap = [(0, start, [start])]
    while heap:
        cost, node, path = heapq.heappop(heap)
        if node == end:
            return cost, path
        if cost > dist.get(node, float("inf")):
            continue
        for neighbor, weight in graph[node]:
            new_cost = cost + weight
            if new_cost < dist.get(neighbor, float("inf")):
                dist[neighbor] = new_cost
                heapq.heappush(heap, (new_cost, neighbor, path + [neighbor]))
    return None
```

## 단계별 실습

### Step 1: 가중 그래프 표현

```python
# 인접 리스트 — (이웃, 가중치) 튜플
graph: dict[str, list[tuple[str, int]]] = {
    "A": [("B", 4), ("C", 2)],
    "B": [("A", 4), ("D", 3), ("E", 1)],
    "C": [("A", 2), ("E", 5)],
    "D": [("B", 3)],
    "E": [("B", 1), ("C", 5)],
}

# 그래프 정보 출력
for node, neighbors in graph.items():
    edges = [f"{n}({w})" for n, w in neighbors]
    print(f"  {node} → {', '.join(edges)}")
```

### Step 2: 다익스트라 알고리즘 구현

```python
import heapq


def dijkstra(
    graph: dict[str, list[tuple[str, int]]], start: str
) -> dict[str, int]:
    """다익스트라 — O((V+E) log V)"""
    dist: dict[str, int] = {start: 0}
    heap: list[tuple[int, str]] = [(0, start)]

    while heap:
        cost, node = heapq.heappop(heap)
        if cost > dist.get(node, float("inf")):
            continue  # 이미 더 짧은 경로가 확정됨

        for neighbor, weight in graph[node]:
            new_cost = cost + weight
            if new_cost < dist.get(neighbor, float("inf")):
                dist[neighbor] = new_cost
                heapq.heappush(heap, (new_cost, neighbor))

    return dist

distances = dijkstra(graph, "A")
for node, d in sorted(distances.items()):
    print(f"  A → {node}: {d}")
# A → A: 0
# A → B: 4
# A → C: 2
# A → D: 7
# A → E: 5
```

### Step 3: 경로 추적

```python
import heapq


def dijkstra_with_path(
    graph: dict[str, list[tuple[str, int]]], start: str
) -> tuple[dict[str, int], dict[str, list[str]]]:
    """다익스트라 + 경로 추적"""
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
                prev[neighbor] = node
                heapq.heappush(heap, (new_cost, neighbor))

    # 경로 복원
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
    print(f"  A → {node}: 거리={distances[node]}, 경로={' → '.join(paths[node])}")
```

### Step 4: 격자 그래프에서 최단 경로

```python
import heapq


def grid_shortest_path(grid: list[list[int]]) -> int:
    """2차원 격자에서 좌상단→우하단 최소 비용 경로"""
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

### Step 5: 알고리즘 비교

```python
# BFS vs 다익스트라 적용 기준
comparison = [
    ("가중치 없는 그래프", "BFS — O(V+E)"),
    ("음이 아닌 가중치", "다익스트라 — O((V+E) log V)"),
    ("음의 가중치 허용", "벨만-포드 — O(V×E)"),
    ("모든 쌍 최단 경로", "플로이드-워셜 — O(V³)"),
]

print("최단 경로 알고리즘 선택 기준:")
for condition, algorithm in comparison:
    print(f"  {condition}: {algorithm}")
```

## 이 코드에서 주목할 점

- heapq는 최소 힙이므로 가장 작은 거리의 노드를 먼저 처리합니다
- `cost > dist.get(node, float("inf"))` 체크로 이미 확정된 노드를 건너뜁니다
- 경로 추적은 prev 딕셔너리로 역추적하여 복원합니다
- 격자 그래프도 다익스트라로 풀 수 있으며, 코딩 테스트에서 자주 출제됩니다

## 흔한 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|------------|----------|
| 음의 가중치에 다익스트라 사용 | 잘못된 결과를 반환합니다 | 벨만-포드 알고리즘을 사용합니다 |
| 확정된 노드 스킵 누락 | 중복 처리로 시간이 낭비됩니다 | 힙에서 꺼낸 후 거리를 비교합니다 |
| 리스트로 우선순위 큐 구현 | 삽입/삭제가 O(n)입니다 | heapq를 사용합니다 |
| 초기 거리를 0이 아닌 값으로 설정 | 출발 노드의 거리가 틀립니다 | 출발 노드의 거리를 0으로 초기화합니다 |
| 도달 불가능한 노드 미처리 | KeyError가 발생합니다 | dist.get(node, float("inf"))를 사용합니다 |

## 실무에서 이렇게 쓰입니다

- 내비게이션 앱이 다익스트라(또는 A*)로 최적 경로를 계산합니다
- 네트워크 라우팅 프로토콜(OSPF)이 다익스트라를 사용합니다
- 물류 시스템에서 배송 경로를 최적화합니다
- 게임에서 NPC의 이동 경로를 계산합니다
- SNS에서 사용자 간 최단 연결 관계를 분석합니다

## 현업 개발자는 이렇게 생각합니다

다익스트라를 직접 구현할 일은 드물지만, 최단 경로 문제를 인식하는 것이 중요합니다. "이 문제가 최단 경로 문제인가?"라는 질문을 할 수 있으면, 적절한 라이브러리나 알고리즘을 선택할 수 있습니다.

실무에서는 NetworkX의 shortest_path()나 Google Maps API 같은 도구를 사용합니다. 하지만 내부 동작을 이해하면 성능 문제를 진단하고 적절한 알고리즘을 선택하는 데 도움이 됩니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **가중치 부호** — 음수 가중치가 있으면 Dijkstra가 부적합합니다.
- **힙 구현** — Dijkstra는 heapq 기반이 사실상 표준입니다.
- **다대다 경로** — Floyd-Warshall은 작은 그래프에서만 실용적입니다.
- **정합성 테스트** — 골든 그래프로 회귀를 고정합니다.
- **실무 라이브러리** — networkx 등 검증된 구현을 우선 검토합니다.

## 체크리스트

- [ ] 다익스트라 알고리즘의 동작 원리를 설명할 수 있다
- [ ] heapq를 사용하여 다익스트라를 구현할 수 있다
- [ ] 최단 경로를 역추적할 수 있다
- [ ] 다익스트라의 한계(음의 가중치)를 설명할 수 있다
- [ ] 문제 유형에 따라 적절한 최단 경로 알고리즘을 선택할 수 있다

## 연습 문제

1. 가중 방향 그래프에서 특정 노드 쌍의 최단 경로와 비용을 출력하세요.
2. 격자에서 장애물(통과 불가 셀)이 있는 경우의 최단 경로를 구하세요.
3. 다익스트라를 사용하여 k번째 최단 경로를 구하는 함수를 작성하세요.

## 정리 및 다음 글 안내

다익스트라 알고리즘은 음이 아닌 가중치 그래프에서 최단 경로를 O((V+E) log V)에 구합니다. 핵심은 우선순위 큐로 가장 가까운 노드를 먼저 처리하는 것입니다. 다음 글에서는 "현재 최선의 선택"을 반복하는 그리디 알고리즘을 다룹니다.

<!-- toc:begin -->
- [알고리즘이란 무엇인가?](./01-what-are-algorithms.md)
- [시간 복잡도와 Big-O](./02-time-complexity-and-big-o.md)
- [선형 탐색과 이진 탐색](./03-linear-and-binary-search.md)
- [정렬 알고리즘](./04-sorting-algorithms.md)
- [재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- [동적 계획법 기초](./06-dynamic-programming-basics.md)
- [그래프 탐색 — BFS와 DFS](./07-graph-traversal-bfs-dfs.md)
- **최단 경로 기초 (현재 글)**
- 그리디 알고리즘 (예정)
- 코딩 테스트 문제 접근법 (예정)
<!-- toc:end -->

## 참고 자료

- [Wikipedia — Dijkstra's Algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Python 공식 문서 — heapq](https://docs.python.org/3/library/heapq.html)
- [Visualgo — Single-Source Shortest Path](https://visualgo.net/en/sssp)
- [Real Python — Priority Queue in Python](https://realpython.com/python-heapq-module/)
