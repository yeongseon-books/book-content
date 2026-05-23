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

## 먼저 던지는 질문

- 가중치 그래프의 최단 경로 문제는 어떻게 정의할까요?
- 다익스트라 알고리즘은 어떤 원리로 동작할까요?
- Python의 `heapq`로 우선순위 큐를 어떻게 구현할까요?

## 왜 중요한가

내비게이션, 네트워크 라우팅, 물류 최적화는 모두 가중치 그래프의 최단 경로 문제입니다. 다익스트라는 이 문제를 효율적으로 푸는 가장 기본적인 도구입니다.

> 다익스트라 알고리즘은 음수 가중치가 없는 그래프에서, 하나의 시작점으로부터 모든 노드까지의 최단 경로를 구합니다.

그리디 전략과 우선순위 큐를 결합해 `O((V+E) log V)`로 동작한다는 점이 핵심입니다. A* 같은 고급 알고리즘도 이 원리 위에 있습니다.

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
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| Weighted graph | 각 간선에 비용(가중치)이 있는 그래프입니다 |
| Dijkstra's algorithm | 음수 가중치가 없는 단일 시작점 최단 경로 알고리즘입니다 |
| Priority queue | 가장 작은 값을 먼저 꺼내는 자료구조입니다 |
| Relaxation | 더 짧은 경로를 찾았을 때 거리 추정치를 갱신하는 과정입니다 |
| Negative weight | 다익스트라가 올바르게 처리하지 못하는 음수 비용 간선입니다 |

## 적용 전후 비교
가중치 그래프에서 최단 경로를 찾는 두 가지 접근입니다.

```python
# before: BFS — 가중치를 무시해 잘못된 답을 냄
def shortest(graph, start, end):
    from collections import deque
    queue = deque([(start, [start])])
    visited = {start}
    while queue:
        node, path = queue.popleft()
        if node == end:
            return path  # minimum hops, NOT minimum cost
        for neighbor, _ in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return None
```

```python
# after: Dijkstra — 가중치를 고려한 최단 경로
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

가중치 그래프는 이웃 노드뿐 아니라 간선 비용까지 함께 저장해야 합니다. 그래서 인접 리스트의 값이 `(neighbor, weight)` 튜플 목록이 됩니다.

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
            continue

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

다익스트라는 현재까지 가장 짧다고 알려진 후보를 먼저 처리합니다. 그래서 우선순위 큐가 핵심이며, 이미 더 짧은 값이 기록된 노드는 건너뛰는 로직이 중요합니다.

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
                prev[neighbor] = node
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

거리만 구하는 것과 실제 경로를 복원하는 것은 다릅니다. `prev` 딕셔너리로 이전 노드를 기록해 두면 마지막에 경로를 되짚어 복원할 수 있습니다.

### 단계 4: 그리드 최단 경로
```python
import heapq

def grid_shortest_path(grid: list[list[int]]) -> int:
    """Minimum-cost path from top-left to bottom-right in a grid."""
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

격자 문제도 노드와 간선으로 해석하면 다익스트라의 전형적인 응용이 됩니다. 코딩 테스트에서 특히 자주 나오는 형태입니다.

### 단계 5: 알고리즘 비교
```python
comparison = [
    ("Unweighted graph", "BFS — O(V+E)"),
    ("Non-negative weights", "Dijkstra — O((V+E) log V)"),
    ("Negative weights allowed", "Bellman-Ford — O(V*E)"),
    ("All-pairs shortest path", "Floyd-Warshall — O(V^3)"),
]

print("Shortest-path algorithm selection guide:")
for condition, algorithm in comparison:
    print(f"  {condition}: {algorithm}")
```

최단 경로 문제는 조건에 따라 알고리즘 선택이 달라집니다. 가중치 유무, 음수 간선 존재, 모든 쌍 경로 필요 여부를 먼저 봐야 합니다.

## 이 코드에서 먼저 봐야 할 점

- `heapq`는 최소 힙이므로, 가장 짧은 거리 후보를 항상 먼저 처리할 수 있습니다.
- `cost > dist.get(node, float("inf"))` 검사는 이미 더 짧은 경로가 확정된 노드를 건너뜁니다.
- 경로 복원은 `prev` 딕셔너리를 사용해 도착점부터 거꾸로 추적합니다.
- 격자 최단 경로는 다익스트라가 실제 면접 문제로 자주 변형되는 사례입니다.

## 자주 하는 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 음수 가중치에 다익스트라 사용 | 잘못된 결과를 냅니다 | Bellman-Ford를 사용합니다 |
| 확정 노드 건너뛰기 체크 생략 | 중복 처리가 늘어 비효율적입니다 | 힙에서 꺼낸 비용과 기록된 거리를 비교합니다 |
| 우선순위 큐를 리스트로 흉내 냄 | 삽입과 삭제가 비효율적입니다 | `heapq`를 사용합니다 |
| 시작점 초기 거리를 잘못 둠 | 모든 경로 계산이 흔들립니다 | 시작점 거리를 0으로 둡니다 |
| 도달 불가 노드를 처리하지 않음 | 조회 시 `KeyError`가 날 수 있습니다 | `dist.get(node, float("inf"))`를 사용합니다 |

## 실무에서는 이렇게 연결됩니다

- 내비게이션 앱은 다익스트라나 A*로 운전 경로를 계산합니다.
- OSPF 같은 네트워크 라우팅 프로토콜도 다익스트라를 사용합니다.
- 물류 시스템은 창고와 배송 지점 사이의 최소 비용 경로를 계산합니다.
- 게임 엔진은 NPC 이동 경로를 찾습니다.
- 소셜 네트워크는 사용자 간 최소 연결 경로를 분석할 수 있습니다.

## 현업에서는 이렇게 생각합니다

실제로는 다익스트라를 매번 직접 구현하지 않아도 됩니다. 중요한 능력은 문제를 보고 "이건 최단 경로 문제다"라고 알아보는 일입니다. 그 순간 적절한 라이브러리와 알고리즘을 선택할 수 있기 때문입니다.

실무에서는 NetworkX나 지도 API를 사용할 수 있지만, 내부 원리를 이해해야 성능 문제와 알고리즘 선택을 제대로 설명할 수 있습니다.

## 다익스트라가 느리거나 틀릴 때 먼저 볼 것

- 간선에 음수 가중치가 섞였는지 먼저 확인해야 합니다. 이 조건 하나만 어겨도 결과가 틀릴 수 있습니다.
- 힙에서 꺼낸 오래된 후보를 건너뛰지 않으면 정답은 맞아도 처리량이 급격히 떨어집니다.
- 경로 복원이 이상하면 거리 배열보다 `prev` 갱신 시점이 더 자주 원인입니다. 더 짧은 비용을 찾았을 때만 이전 노드를 바꿔야 합니다.
- 실시간 길찾기처럼 그래프가 자주 바뀌는 시스템에서는 정확도만이 아니라 재계산 비용과 캐시 무효화 비용도 함께 봐야 합니다.

## 체크리스트

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

## 심화 실전 노트: 다익스트라 구현을 신뢰 가능한 형태로 고정하기

### 구현 앵커: stale entry 건너뛰기와 경로 복원 분리

```python
import heapq

def dijkstra_core(graph: dict[int, list[tuple[int, int]]], start: int):
    dist = {start: 0}
    prev = {start: None}
    pq = [(0, start)]

    while pq:
        cost, node = heapq.heappop(pq)
        if cost != dist.get(node, float("inf")):
            continue  # stale entry

        for nxt, w in graph[node]:
            nd = cost + w
            if nd < dist.get(nxt, float("inf")):
                dist[nxt] = nd
                prev[nxt] = node
                heapq.heappush(pq, (nd, nxt))

    return dist, prev

def restore_path(prev: dict[int, int | None], end: int):
    if end not in prev:
        return None
    path = []
    cur = end
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    return list(reversed(path))
```

### 실행 추적: 우선순위 큐 상태

```text
push (0,A)
pop  (0,A) -> B(4), C(2) 갱신
pop  (2,C) -> E(7) 갱신
pop  (4,B) -> E(5)로 재갱신, D(7) 갱신
pop  (5,E) ...
```

같은 노드가 여러 번 큐에 들어가는 것은 정상이며, 오래된 엔트리를 건너뛰는 조건이 성능 핵심입니다.

### 비교표: 최단 경로 알고리즘 선택

| 조건 | 알고리즘 | 복잡도 |
|------|----------|--------|
| 무가중치 | BFS | `O(V+E)` |
| 비음수 가중치 | Dijkstra | `O((V+E) log V)` |
| 음수 가중치 포함 | Bellman-Ford | `O(VE)` |
| 모든 쌍 | Floyd-Warshall | `O(V^3)` |

### 인터뷰형 분해 질문

- 음수 간선이 존재하는가
- 단일 시작점인가, 모든 쌍인가
- 경로 비용만 필요한가, 실제 경로도 필요한가
- 그래프가 희소한가 밀집한가

### 증명 스케치: 다익스트라의 안전성

비음수 가중치 조건에서, 우선순위 큐에서 가장 작은 거리로 꺼낸 노드 `u`보다 더 짧은 경로가 나중에 발견될 수 없습니다. 나중 경로는 최소한 비음수 간선을 추가로 거치므로 현재 비용보다 작아질 수 없기 때문입니다.

### 실수-수정 페어

| 실수 | 결과 | 수정 |
|------|------|------|
| 음수 간선인데 다익스트라 적용 | 오답 | 알고리즘 교체 |
| `prev` 갱신을 무조건 수행 | 경로 왜곡 | 거리 갱신 시점에만 `prev` 변경 |
| 도달 불가 노드 처리 누락 | 런타임 오류 | `inf`와 `None` 경로 명시 |

## 실전 검증 부록: 성능 측정과 반례 설계

알고리즘 학습에서 구현 자체보다 오래 남는 자산은 검증 습관입니다. 아래 체크는 주제와 무관하게 거의 모든 문제에서 공통으로 적용됩니다.

### 1) 마이크로 벤치마크 규칙

```python
import time

def benchmark(func, *args, repeat: int = 5) -> float:
    best = float("inf")
    for _ in range(repeat):
        start = time.perf_counter()
        func(*args)
        best = min(best, time.perf_counter() - start)
    return best
```

- 단일 실행 시간은 노이즈가 큽니다.
- 최소/중앙값 기준으로 비교하는 편이 안정적입니다.
- 입력 크기를 여러 단계로 늘려 증가 추세를 기록해야 합니다.

### 2) 반례 세트 템플릿

```text
A. 최소 입력: 빈 배열, 원소 1개
B. 중복 입력: 같은 값 다수
C. 정렬/역정렬 입력: 경계 인덱스 오류 탐지
D. 음수/0 포함 입력: 비교식 방향 오류 탐지
E. 해답 없음 케이스: 종료 조건 검증
```

테스트를 통과했는지보다, 어떤 종류의 실패를 막았는지 기록하는 편이 품질에 더 직접적입니다.

### 3) 복잡도-메모리 트레이드오프 표

| 개선 전략 | 시간 영향 | 공간 영향 | 적용 판단 |
|-----------|-----------|-----------|-----------|
| 캐시/메모이제이션 | 감소 | 증가 | 중복 계산이 명확할 때 |
| 정렬 후 탐색 | 대체로 감소 | 동일/약간 증가 | 질의가 여러 번일 때 |
| 해시 사용 | 평균 감소 | 증가 | 순서보다 조회가 중요할 때 |
| 힙 사용 | 상위/최소 유지에 유리 | 증가 | 우선순위 선택이 핵심일 때 |

### 4) 인터뷰 답변 스크립트

- "먼저 입력 제약을 보고 가능한 복잡도 상한을 정하겠습니다."
- "현재 접근의 시간/공간 복잡도를 계산해 보겠습니다."
- "경계 입력 다섯 가지로 검증 계획을 먼저 제시하겠습니다."
- "필요하면 정답 유지 조건을 짧게 증명하겠습니다."

이 스크립트를 반복하면 설명의 밀도가 올라가고, 구현 중 길을 잃는 빈도가 줄어듭니다.

## 처음 질문으로 돌아가기

- **가중치 그래프의 최단 경로 문제는 어떻게 정의할까요?**
  - 가중치 그래프의 최단 경로 문제는 시작점에서 도착점까지 가는 여러 경로 가운데 간선 가중치 합이 가장 작은 경로를 찾는 일입니다. 본문은 BFS가 최소 간선 수만 보장할 뿐이고, 비용이 붙는 순간 `("neighbor", weight)` 형태의 그래프와 다른 알고리즘이 필요하다는 점을 먼저 짚었습니다.
- **다익스트라 알고리즘은 어떤 원리로 동작할까요?**
  - 다익스트라는 현재까지 가장 짧다고 알려진 후보를 먼저 꺼내고, 더 짧은 경로를 찾으면 거리 추정치를 갱신하는 relaxation으로 진행합니다. `dijkstra()`의 `new_cost < dist.get(...)` 조건과 오래된 힙 항목을 건너뛰는 검사 덕분에 비음수 가중치 그래프에서 올바른 최단 거리를 구할 수 있습니다.
- **Python의 `heapq`로 우선순위 큐를 어떻게 구현할까요?**
  - `heapq`에서는 `(거리, 노드)` 또는 `(거리, 노드, 경로)` 튜플을 힙에 넣고, `heappop()`으로 가장 작은 거리 후보를 먼저 꺼내면 됩니다. `dijkstra_with_path()`와 `grid_shortest_path()` 예제는 거리 계산뿐 아니라 `prev`를 이용한 경로 복원과 격자 문제 확장까지 같은 우선순위 큐 패턴으로 처리했습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Algorithms with Python 101 (1/10): 알고리즘이란 무엇인가?](./01-what-are-algorithms.md)
- [Algorithms with Python 101 (2/10): 시간 복잡도와 Big-O](./02-time-complexity-and-big-o.md)
- [Algorithms with Python 101 (3/10): 선형 탐색과 이진 탐색](./03-linear-and-binary-search.md)
- [Algorithms with Python 101 (4/10): 정렬 알고리즘](./04-sorting-algorithms.md)
- [Algorithms with Python 101 (5/10): 재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- [Algorithms with Python 101 (6/10): 동적 계획법 기초](./06-dynamic-programming-basics.md)
- [Algorithms with Python 101 (7/10): 그래프 탐색 — BFS와 DFS](./07-graph-traversal-bfs-dfs.md)
- **최단 경로 기초 (현재 글)**
- 그리디 알고리즘 (예정)
- 코딩 테스트 문제 접근법 (예정)

<!-- toc:end -->

## 참고 자료

- [Wikipedia — Dijkstra's Algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Python Documentation — heapq](https://docs.python.org/3/library/heapq.html)
- [Visualgo — Single-Source Shortest Path](https://visualgo.net/en/sssp)
- [Real Python — Priority Queue in Python](https://realpython.com/python-heapq-module/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-python-101/ko/08-shortest-path-basics)

Tags: Python, Algorithms, Shortest Path, Dijkstra, heapq
