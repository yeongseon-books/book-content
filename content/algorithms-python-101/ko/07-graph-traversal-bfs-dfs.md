---
series: algorithms-python-101
episode: 7
title: "Algorithms with Python 101 (7/10): 그래프 탐색 — BFS와 DFS"
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
  - Graphs
  - BFS
  - DFS
seo_description: 그래프 표현과 BFS, DFS의 핵심 활용법을 Python으로 익힙니다.
last_reviewed: '2026-05-12'
---

# Algorithms with Python 101 (7/10): 그래프 탐색 — BFS와 DFS

네트워크, 지도, 의존성 트리, 추천 시스템은 모두 결국 노드와 연결 관계의 문제로 환원됩니다. 배열과 리스트를 지나면 그래프 사고가 자주 등장하는 이유가 여기에 있습니다.

이 글은 Algorithms with Python 101 시리즈의 일곱 번째 글입니다. 여기서는 Python으로 그래프를 표현하고, BFS와 DFS를 실용적인 관점에서 구현해 보겠습니다.

BFS와 DFS는 그래프 탐색의 두 기초 전략입니다. 둘의 차이를 분명히 이해하면 최단 경로, 사이클 검사, 연결 요소 문제를 훨씬 쉽게 다룰 수 있습니다.


![Algorithms with Python 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-python-101/07/07-01-concept-overview.ko.png)
*Algorithms with Python 101 7장 흐름 개요*

## 먼저 던지는 질문

- 그래프의 기본 개념과 Python에서의 표현 방식은 무엇일까요?
- BFS는 어떤 원리로 동작하고 언제 써야 할까요?
- DFS는 어떤 원리로 동작하고 언제 써야 할까요?

## 왜 중요한가

소셜 네트워크, 지도, 웹 링크, 의존성 그래프는 모두 그래프로 모델링됩니다. BFS와 DFS는 이런 구조를 탐색하는 가장 기본적인 알고리즘입니다.

> BFS는 가까운 이웃을 층별로 탐색하고, DFS는 한 경로를 가능한 깊게 내려간 뒤 되돌아옵니다.

가중치가 없는 그래프의 최단 경로에는 BFS가 적합하고, 경로 존재 여부 확인, 사이클 탐지, 위상 정렬 같은 문제에는 DFS가 자주 사용됩니다.

## 개념 한눈에 보기

> 그래프는 노드(vertex)와 간선(edge)의 집합입니다

```text
Example graph:     BFS order:           DFS order:
  A—B               A (layer 0)         A → B → D → E → C → F
  |\ \              B, C (layer 1)
  | C  D            D, E, F (layer 2)
  |/ \
  E   F
```

## 핵심 개념

| 용어 | 설명 |
|------|------|
| Vertex (node) | 그래프를 이루는 개별 요소입니다 |
| Edge | 두 노드를 잇는 연결입니다 |
| Adjacency list | 각 노드와 이웃 노드 목록을 매핑하는 표현 방식입니다 |
| BFS (Breadth-First Search) | 큐를 사용해 가까운 노드부터 방문합니다 |
| DFS (Depth-First Search) | 스택 또는 재귀를 사용해 가능한 깊게 방문합니다 |

## Before / After

두 노드가 연결되어 있는지 확인하는 두 가지 접근입니다.

```python
# before: ad-hoc traversal — risk of infinite loop
def is_connected(graph, start, end):
    # Not systematic, may loop forever
    pass
```

```python
# after: BFS — systematic O(V+E) traversal
from collections import deque

def is_connected(graph, start, end):
    visited = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node == end:
            return True
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return False
```

## 단계별 실습

### Step 1: Representing Graphs

```python
# Adjacency list using a dictionary
graph: dict[str, list[str]] = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A", "E", "F"],
    "D": ["B"],
    "E": ["C"],
    "F": ["C"],
}

# Directed graph
directed_graph: dict[str, list[str]] = {
    "A": ["B", "C"],
    "B": ["D"],
    "C": ["E"],
    "D": [],
    "E": [],
}

# Weighted graph
weighted_graph: dict[str, list[tuple[str, int]]] = {
    "A": [("B", 4), ("C", 2)],
    "B": [("A", 4), ("D", 3)],
    "C": [("A", 2), ("E", 1)],
    "D": [("B", 3)],
    "E": [("C", 1)],
}
```

그래프는 보통 인접 리스트로 표현합니다. 노드 수가 많고 연결이 희소한 경우에 특히 효율적이며, BFS와 DFS 구현도 자연스럽습니다.

### Step 2: BFS Implementation

```python
from collections import deque

def bfs(graph: dict[str, list[str]], start: str) -> list[str]:
    """BFS — O(V+E), uses a queue."""
    visited = {start}
    queue = deque([start])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return order

print(bfs(graph, "A"))  # ['A', 'B', 'C', 'D', 'E', 'F']
```

BFS는 시작점에서 가까운 노드부터 한 층씩 넓혀 갑니다. 그래서 가중치가 없는 그래프의 최단 경로 문제에 특히 적합합니다.

### Step 3: DFS Implementation (Recursive and Iterative)

```python
def dfs_recursive(
    graph: dict[str, list[str]],
    node: str,
    visited: set[str] | None = None,
) -> list[str]:
    """DFS recursive — O(V+E)."""
    if visited is None:
        visited = set()
    visited.add(node)
    order = [node]
    for neighbor in graph[node]:
        if neighbor not in visited:
            order.extend(dfs_recursive(graph, neighbor, visited))
    return order

print(dfs_recursive(graph, "A"))  # ['A', 'B', 'D', 'C', 'E', 'F']

def dfs_iterative(graph: dict[str, list[str]], start: str) -> list[str]:
    """DFS iterative — O(V+E), uses a stack."""
    visited: set[str] = set()
    stack = [start]
    order: list[str] = []

    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        for neighbor in reversed(graph[node]):
            if neighbor not in visited:
                stack.append(neighbor)

    return order

print(dfs_iterative(graph, "A"))  # ['A', 'B', 'D', 'C', 'E', 'F']
```

DFS는 한 경로를 끝까지 따라가는 방식이라, 구조를 깊게 파고드는 문제에 잘 맞습니다. 재귀와 반복 모두 구현 가능하다는 점도 중요합니다.

### Step 4: BFS Shortest Path

```python
from collections import deque

def bfs_shortest_path(
    graph: dict[str, list[str]], start: str, end: str
) -> list[str] | None:
    """BFS shortest path — unweighted graph."""
    if start == end:
        return [start]

    visited = {start}
    queue: deque[list[str]] = deque([[start]])

    while queue:
        path = queue.popleft()
        node = path[-1]
        for neighbor in graph[node]:
            if neighbor == end:
                return path + [neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])

    return None

print(bfs_shortest_path(graph, "A", "F"))  # ['A', 'C', 'F']
print(bfs_shortest_path(graph, "D", "E"))  # ['D', 'B', 'A', 'C', 'E']
```

가중치가 없는 그래프에서는 BFS가 먼저 도착한 경로가 곧 최단 경로입니다. 이 성질이 BFS를 아주 실용적으로 만듭니다.

### Step 5: Connected Components and Cycle Detection

```python
def find_connected_components(
    graph: dict[str, list[str]],
) -> list[list[str]]:
    """Find all connected components."""
    visited: set[str] = set()
    components: list[list[str]] = []

    for node in graph:
        if node not in visited:
            component = bfs(graph, node)
            visited.update(component)
            components.append(component)

    return components

split_graph: dict[str, list[str]] = {
    "A": ["B"], "B": ["A"],
    "C": ["D"], "D": ["C"],
}
print(find_connected_components(split_graph))
# [['A', 'B'], ['C', 'D']]

def has_cycle(graph: dict[str, list[str]], start: str) -> bool:
    """Cycle detection in an undirected graph using DFS."""
    visited: set[str] = set()

    def _dfs(node: str, parent: str | None) -> bool:
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                if _dfs(neighbor, node):
                    return True
            elif neighbor != parent:
                return True
        return False

    return _dfs(start, None)

print(has_cycle(graph, "A"))  # True
```

그래프 문제는 단순 방문을 넘어서 연결 요소 분리, 사이클 검출 같은 응용으로 이어집니다. BFS와 DFS를 익히면 이 확장이 자연스럽게 보이기 시작합니다.

## 이 코드에서 먼저 봐야 할 점

- BFS는 큐(`deque`)를 쓰고, DFS는 스택 또는 재귀를 씁니다.
- BFS는 가중치 없는 그래프에서 최단 경로를 보장하지만, DFS는 그렇지 않습니다.
- `visited` 집합은 이미 방문한 노드를 기록해 무한 루프를 막습니다.
- 무방향 그래프의 사이클 검출에서는 부모 노드를 함께 추적해야 오탐을 막을 수 있습니다.

## 자주 하는 실수 5가지

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 방문 체크를 빼먹음 | 무한 루프에 빠집니다 | 노드를 처리하기 전에 `visited`를 확인합니다 |
| BFS 큐로 리스트 사용 | `pop(0)`이 `O(n)`입니다 | `collections.deque`를 사용합니다 |
| DFS를 재귀로만 구현 | 큰 그래프에서 `RecursionError`가 날 수 있습니다 | 반복형 DFS도 익혀 둡니다 |
| 방향 그래프와 무방향 그래프를 혼동 | 탐색 결과와 해석이 달라집니다 | 그래프 종류를 먼저 명시합니다 |
| 끊어진 그래프를 하나의 시작점만 탐색 | 일부 노드를 놓칩니다 | 모든 미방문 노드에서 시작합니다 |

## 실무에서는 이렇게 연결됩니다

- 소셜 네트워크는 BFS로 친구의 친구를 추천할 수 있습니다.
- 웹 크롤러는 페이지를 층별로 방문할 때 BFS를 활용합니다.
- 패키지 관리자는 DFS 기반 위상 정렬로 의존성을 처리합니다.
- 미로 탐색과 게임 AI는 그래프 순회를 경로 탐색의 기반으로 사용합니다.
- 네트워크 토폴로지 분석도 그래프 순회 위에 세워집니다.

## 현업에서는 이렇게 생각합니다

BFS와 DFS는 그래프 알고리즘의 벽돌입니다. 이 둘을 이해하면 다익스트라, 위상 정렬, 최소 신장 트리 같은 다음 단계 주제가 훨씬 자연스럽게 이어집니다.

실무에서는 NetworkX 같은 라이브러리를 쓸 수 있지만, 내부 동작을 이해해야 어떤 문제에 어떤 탐색이 맞는지 스스로 판단할 수 있습니다.

## BFS와 DFS를 고를 때 먼저 확인할 것

- 최단 단계 수가 필요하면 BFS부터 의심하는 편이 안전합니다. 무가중치 그래프에서는 도착 순서 자체가 답이 되기 때문입니다.
- 경로 존재 여부, 사이클, 위상 정렬처럼 구조를 깊게 파고들어야 하면 DFS가 더 자연스럽습니다.
- 입력 그래프가 매우 깊으면 재귀 DFS보다 반복형 DFS를 먼저 검토해야 합니다. 운영 코드에서는 재귀 깊이 제한이 장애 원인이 되기 쉽습니다.
- 탐색이 느리거나 메모리를 많이 쓰면, 자료구조 문제가 아닌 visited 처리 누락과 중복 방문부터 먼저 의심하는 편이 좋습니다.

## 체크리스트

- [ ] 인접 리스트로 그래프를 표현할 수 있습니다
- [ ] BFS와 DFS의 차이를 설명할 수 있습니다
- [ ] BFS로 최단 경로를 찾을 수 있습니다
- [ ] DFS로 사이클을 검출할 수 있습니다
- [ ] 무방향 그래프의 연결 요소를 찾을 수 있습니다

## 연습 문제

1. 2차원 격자(미로)에서 최단 경로를 찾는 BFS 함수를 작성해 보세요.
2. 방향 그래프에서 DFS 기반 위상 정렬을 구현해 보세요.
3. 주어진 그래프가 이분 그래프인지 BFS로 판별해 보세요.

## 정리와 다음 글

BFS는 노드를 층별로 탐색하고, 가중치 없는 그래프의 최단 경로를 보장합니다. DFS는 깊게 먼저 들어가므로 사이클 검출과 위상 정렬에 잘 맞습니다. 다음 글에서는 가중치가 있는 그래프의 최단 경로를 다익스트라 알고리즘으로 다룹니다.

## 심화 실전 노트: 그래프 탐색을 문제 유형으로 분해하기

### 구현 앵커: BFS 거리 배열과 DFS 진입/이탈 시간

```python
from collections import deque


def bfs_distance(graph: dict[int, list[int]], start: int) -> dict[int, int]:
    dist = {start: 0}
    q = deque([start])
    while q:
        node = q.popleft()
        for nxt in graph[node]:
            if nxt not in dist:
                dist[nxt] = dist[node] + 1
                q.append(nxt)
    return dist


def dfs_time(graph: dict[int, list[int]], start: int):
    visited = set()
    tin, tout = {}, {}
    clock = 0

    def go(node: int):
        nonlocal clock
        visited.add(node)
        clock += 1
        tin[node] = clock
        for nxt in graph[node]:
            if nxt not in visited:
                go(nxt)
        clock += 1
        tout[node] = clock

    go(start)
    return tin, tout
```

### 실행 추적: BFS 레이어

```text
start=1
layer0: [1]
layer1: [2,3]
layer2: [4,5,6]
```

레이어 정보가 필요한 문제(최단 단계 수, 감염 전파 일수)는 BFS가 기본 선택입니다.

### 복잡도 비교표

| 알고리즘 | 자료구조 | 시간 복잡도 | 주 용도 |
|----------|----------|-------------|---------|
| BFS | 큐 | `O(V+E)` | 무가중치 최단 경로 |
| DFS 재귀 | 호출 스택 | `O(V+E)` | 사이클, 연결성, 위상 정렬 기반 |
| DFS 반복 | 명시적 스택 | `O(V+E)` | 깊은 그래프에서 안전 |

### 인터뷰형 분해 질문

- 그래프가 방향/무방향 중 무엇인가
- 끊어진 그래프 가능성이 있는가
- 최단 "거리"가 필요한가, 단순 도달성만 필요한가
- 재귀 깊이가 입력에서 안전한가

### 증명 스케치: BFS 최단거리 보장

BFS는 큐를 통해 거리 `d` 노드를 모두 처리한 뒤 거리 `d+1` 노드로 이동합니다. 따라서 어떤 노드를 처음 방문하는 순간의 거리는 시작점에서 갈 수 있는 최소 간선 수와 일치합니다.

### 실수-수정 페어

| 실수 | 증상 | 수정 |
|------|------|------|
| 방문 처리를 pop 시점에만 수행 | 중복 enqueue 폭증 | enqueue 시점 방문 처리 |
| 무방향 그래프 사이클 탐지에서 부모 추적 누락 | 오탐 | `(node,parent)`로 DFS |
| 분리 그래프에서 단일 시작점만 탐색 | 일부 노드 미방문 | 전체 노드 루프 + 미방문 시작 |

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

## 케이스 스터디 확장: 입력 규모가 커질 때의 판단

### 시나리오 1: 제약 기반 의사결정 로그

문제를 처음 읽을 때 정답 코드보다 먼저 남겨야 하는 기록은 입력 크기, 허용 복잡도, 실패 가능성이 큰 경계 조건입니다. 이 기록이 있으면 구현 도중 방향이 흔들려도 빠르게 복구할 수 있습니다.

| 항목 | 기록 예시 | 확인 이유 |
|------|-----------|-----------|
| 입력 상한 | `N=200000` | 중첩 루프 배제 판단 |
| 목표 복잡도 | `O(n log n)` 이하 | 시간 초과 예방 |
| 경계 조건 | 빈 입력/중복/음수 | 런타임 오류 예방 |

```python
def decision_log(n_max: int) -> str:
    if n_max <= 5_000:
        return "O(n^2)까지 검토"
    if n_max <= 200_000:
        return "O(n log n) 중심"
    return "O(n) 우선"

print(decision_log(200_000))
```

작은 보조 함수를 두면 문제별 판단 근거를 팀 문서와 코드 리뷰에 같은 형태로 남길 수 있습니다. 코딩 테스트 연습에서도 같은 틀을 반복하면 풀이 속도와 정확도가 함께 올라갑니다.

### 시나리오 2: 제약 기반 의사결정 로그

문제를 처음 읽을 때 정답 코드보다 먼저 남겨야 하는 기록은 입력 크기, 허용 복잡도, 실패 가능성이 큰 경계 조건입니다. 이 기록이 있으면 구현 도중 방향이 흔들려도 빠르게 복구할 수 있습니다.

| 항목 | 기록 예시 | 확인 이유 |
|------|-----------|-----------|
| 입력 상한 | `N=200000` | 중첩 루프 배제 판단 |
| 목표 복잡도 | `O(n log n)` 이하 | 시간 초과 예방 |
| 경계 조건 | 빈 입력/중복/음수 | 런타임 오류 예방 |

```python
def decision_log(n_max: int) -> str:
    if n_max <= 5_000:
        return "O(n^2)까지 검토"
    if n_max <= 200_000:
        return "O(n log n) 중심"
    return "O(n) 우선"

print(decision_log(200_000))
```

작은 보조 함수를 두면 문제별 판단 근거를 팀 문서와 코드 리뷰에 같은 형태로 남길 수 있습니다. 코딩 테스트 연습에서도 같은 틀을 반복하면 풀이 속도와 정확도가 함께 올라갑니다.

### 시나리오 3: 제약 기반 의사결정 로그

문제를 처음 읽을 때 정답 코드보다 먼저 남겨야 하는 기록은 입력 크기, 허용 복잡도, 실패 가능성이 큰 경계 조건입니다. 이 기록이 있으면 구현 도중 방향이 흔들려도 빠르게 복구할 수 있습니다.

| 항목 | 기록 예시 | 확인 이유 |
|------|-----------|-----------|
| 입력 상한 | `N=200000` | 중첩 루프 배제 판단 |
| 목표 복잡도 | `O(n log n)` 이하 | 시간 초과 예방 |
| 경계 조건 | 빈 입력/중복/음수 | 런타임 오류 예방 |

```python
def decision_log(n_max: int) -> str:
    if n_max <= 5_000:
        return "O(n^2)까지 검토"
    if n_max <= 200_000:
        return "O(n log n) 중심"
    return "O(n) 우선"

print(decision_log(200_000))
```

작은 보조 함수를 두면 문제별 판단 근거를 팀 문서와 코드 리뷰에 같은 형태로 남길 수 있습니다. 코딩 테스트 연습에서도 같은 틀을 반복하면 풀이 속도와 정확도가 함께 올라갑니다.

### 시나리오 4: 제약 기반 의사결정 로그

문제를 처음 읽을 때 정답 코드보다 먼저 남겨야 하는 기록은 입력 크기, 허용 복잡도, 실패 가능성이 큰 경계 조건입니다. 이 기록이 있으면 구현 도중 방향이 흔들려도 빠르게 복구할 수 있습니다.

| 항목 | 기록 예시 | 확인 이유 |
|------|-----------|-----------|
| 입력 상한 | `N=200000` | 중첩 루프 배제 판단 |
| 목표 복잡도 | `O(n log n)` 이하 | 시간 초과 예방 |
| 경계 조건 | 빈 입력/중복/음수 | 런타임 오류 예방 |

```python
def decision_log(n_max: int) -> str:
    if n_max <= 5_000:
        return "O(n^2)까지 검토"
    if n_max <= 200_000:
        return "O(n log n) 중심"
    return "O(n) 우선"

print(decision_log(200_000))
```

작은 보조 함수를 두면 문제별 판단 근거를 팀 문서와 코드 리뷰에 같은 형태로 남길 수 있습니다. 코딩 테스트 연습에서도 같은 틀을 반복하면 풀이 속도와 정확도가 함께 올라갑니다.

### 시나리오 5: 제약 기반 의사결정 로그

문제를 처음 읽을 때 정답 코드보다 먼저 남겨야 하는 기록은 입력 크기, 허용 복잡도, 실패 가능성이 큰 경계 조건입니다. 이 기록이 있으면 구현 도중 방향이 흔들려도 빠르게 복구할 수 있습니다.

| 항목 | 기록 예시 | 확인 이유 |
|------|-----------|-----------|
| 입력 상한 | `N=200000` | 중첩 루프 배제 판단 |
| 목표 복잡도 | `O(n log n)` 이하 | 시간 초과 예방 |
| 경계 조건 | 빈 입력/중복/음수 | 런타임 오류 예방 |

```python
def decision_log(n_max: int) -> str:
    if n_max <= 5_000:
        return "O(n^2)까지 검토"
    if n_max <= 200_000:
        return "O(n log n) 중심"
    return "O(n) 우선"

print(decision_log(200_000))
```

작은 보조 함수를 두면 문제별 판단 근거를 팀 문서와 코드 리뷰에 같은 형태로 남길 수 있습니다. 코딩 테스트 연습에서도 같은 틀을 반복하면 풀이 속도와 정확도가 함께 올라갑니다.

## 처음 질문으로 돌아가기

- **그래프의 기본 개념과 Python에서의 표현 방식은 무엇일까요?**
  - 본문의 기준은 그래프 탐색 — BFS와 DFS를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **BFS는 어떤 원리로 동작하고 언제 써야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **DFS는 어떤 원리로 동작하고 언제 써야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Algorithms with Python 101 (1/10): 알고리즘이란 무엇인가?](./01-what-are-algorithms.md)
- [Algorithms with Python 101 (2/10): 시간 복잡도와 Big-O](./02-time-complexity-and-big-o.md)
- [Algorithms with Python 101 (3/10): 선형 탐색과 이진 탐색](./03-linear-and-binary-search.md)
- [Algorithms with Python 101 (4/10): 정렬 알고리즘](./04-sorting-algorithms.md)
- [Algorithms with Python 101 (5/10): 재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- [Algorithms with Python 101 (6/10): 동적 계획법 기초](./06-dynamic-programming-basics.md)
- **그래프 탐색 — BFS와 DFS (현재 글)**
- 최단 경로 기초 (예정)
- 그리디 알고리즘 (예정)
- 코딩 테스트 문제 접근법 (예정)

<!-- toc:end -->

## 참고 자료

- [Wikipedia — Breadth-First Search](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Wikipedia — Depth-First Search](https://en.wikipedia.org/wiki/Depth-first_search)
- [Real Python — Graphs in Python](https://realpython.com/python-graph/)
- [Visualgo — Graph Traversal](https://visualgo.net/en/dfsbfs)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-python-101/ko/07-graph-traversal-bfs-dfs)

Tags: Python, Algorithms, Graphs, BFS, DFS
