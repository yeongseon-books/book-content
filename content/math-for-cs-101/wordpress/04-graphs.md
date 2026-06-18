---
series: math-for-cs-101
episode: 4
title: "바이브코딩을 위한 CS 수학 (4/10): 그래프"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - CS수학
  - 그래프이론
  - 알고리즘
  - 개발자수학
language: ko
---

# 바이브코딩을 위한 CS 수학 (4/10): 그래프

이 글은 **바이브코딩을 위한 CS 수학** 시리즈의 4편입니다. 그래프 이론이 의존성 관리, 소셜 네트워크, 경로 탐색에서 어떻게 활용되는지 바이브코딩 관점에서 살펴봅니다.

---

패키지 의존성, 소셜 네트워크 팔로우 관계, 도시 간 도로망 — 이 모두는 그래프 구조입니다. 바이브코딩으로 AI에게 "이 데이터의 관계를 분석해줘"라고 요청할 때, 그 분석의 기저에 그래프 탐색이 있다는 것을 알면 결과를 훨씬 정확하게 해석할 수 있습니다.

그래프는 노드(정점)와 엣지(간선)로 구성됩니다. 방향이 있으면 유향 그래프, 없으면 무향 그래프입니다. 이 단순한 구조로 현실의 복잡한 관계를 모델링할 수 있습니다.

> "그래프는 관계를 모델링하는 가장 강력한 수학 구조입니다. 의존성, 연결, 순서 — 모두 그래프입니다."

## 이 글에서 다룰 질문들

- BFS와 DFS는 언제 각각 더 유리할까요?
- 순환 의존성을 그래프로 어떻게 감지할까요?
- 위상 정렬은 빌드 시스템에서 어떻게 쓰일까요?
- 최단 경로 알고리즘은 어떤 상황에 적합할까요?
- 그래프를 코드에서 어떻게 표현할까요?

---

## 그래프 표현 방식

### Before: 관계를 리스트로 관리

```python
# 의존성을 단순 리스트로 관리
dependencies = [
    ("A", "B"),
    ("B", "C"),
    ("A", "C"),
]
# 순환 의존성 감지 불가, 탐색 어려움
```

### After: 인접 리스트로 그래프 표현

```python
from collections import defaultdict, deque

# 인접 리스트로 유향 그래프 표현
graph = defaultdict(list)
graph["A"].extend(["B", "C"])
graph["B"].append("C")

def bfs(start, graph):
    visited = set()
    queue = deque([start])
    order = []
    while queue:
        node = queue.popleft()
        if node not in visited:
            visited.add(node)
            order.append(node)
            queue.extend(graph[node])
    return order

print(bfs("A", graph))  # ['A', 'B', 'C']
```

---

## BFS vs DFS: 언제 무엇을?

| 알고리즘 | 탐색 방식 | 적합한 상황 | 공간 복잡도 |
| --- | --- | --- | --- |
| BFS | 넓이 우선 | 최단 경로, 레벨별 탐색 | O(V) — 큐 크기 |
| DFS | 깊이 우선 | 사이클 감지, 위상 정렬 | O(V) — 스택 깊이 |
| 위상 정렬 | DFS 응용 | 빌드 순서, 작업 스케줄링 | O(V+E) |

---

## 순환 의존성 감지

```python
def has_cycle(graph):
    """DFS로 유향 그래프의 사이클 감지"""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in graph}

    def dfs(node):
        color[node] = GRAY
        for neighbor in graph[node]:
            if color[neighbor] == GRAY:
                return True  # 사이클 발견
            if color[neighbor] == WHITE and dfs(neighbor):
                return True
        color[node] = BLACK
        return False

    return any(dfs(n) for n in graph if color[n] == WHITE)
```

패키지 의존성에 순환이 있으면 설치 순서를 결정할 수 없습니다. 빌드 시스템이 위상 정렬을 사용하는 이유입니다.

---

## AI 팁: 그래프 문제를 AI와 함께 풀기

1. **"이 관계 데이터를 그래프로 모델링해줘"** — 노드와 엣지를 명확히 정의합니다.
2. **"순환 의존성이 있는지 확인해줘"** — DFS 기반 사이클 감지를 요청합니다.
3. **"최단 경로를 찾아줘"** — 가중치 유무에 따라 BFS 또는 Dijkstra를 선택합니다.
4. **networkx 라이브러리**를 활용하면 그래프 알고리즘을 빠르게 적용할 수 있습니다.

---

## 실전 체크리스트

- [ ] 인접 리스트로 그래프를 표현할 수 있다
- [ ] BFS와 DFS를 직접 구현할 수 있다
- [ ] DFS로 순환 의존성을 감지할 수 있다
- [ ] 위상 정렬의 목적과 구현 방법을 설명할 수 있다
- [ ] 프로젝트 의존성을 그래프로 시각화한 경험이 있다

---

## 처음 질문으로 돌아가기

- **BFS와 DFS는 언제 각각 더 유리할까요?**
  BFS는 최단 경로나 레벨별 탐색에 유리하고, DFS는 사이클 감지나 위상 정렬에 적합합니다.

- **순환 의존성을 그래프로 어떻게 감지할까요?**
  DFS에서 현재 탐색 중인 노드(GRAY)를 다시 방문하면 사이클입니다.

- **위상 정렬은 빌드 시스템에서 어떻게 쓰일까요?**
  의존하는 패키지가 먼저 빌드되도록 순서를 결정합니다. 사이클이 있으면 위상 정렬이 불가능합니다.

---

## 정리

그래프는 관계를 모델링하는 핵심 구조입니다. 의존성 관리, 경로 탐색, 네트워크 분석 모두 그래프 알고리즘이 기반입니다. 다음 편에서는 조합론으로 경우의 수와 탐색 공간을 분석합니다.

---

## 참고 자료

- [networkx — Python 그래프 라이브러리](https://networkx.org/)
- [Introduction to Algorithms (CLRS) — Graph Algorithms](https://mitpress.mit.edu/books/introduction-algorithms-third-edition)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 CS 수학 (1/10): CS에 수학이 필요한 이유
- 바이브코딩을 위한 CS 수학 (2/10): 논리와 증명
- 바이브코딩을 위한 CS 수학 (3/10): 집합과 함수
- **바이브코딩을 위한 CS 수학 (4/10): 그래프 (현재 글)**
- 바이브코딩을 위한 CS 수학 (5/10): 조합
- 바이브코딩을 위한 CS 수학 (6/10): 확률
- 바이브코딩을 위한 CS 수학 (7/10): 선형대수
- 바이브코딩을 위한 CS 수학 (8/10): 미분
- 바이브코딩을 위한 CS 수학 (9/10): 정보이론
- 바이브코딩을 위한 CS 수학 (10/10): 알고리즘과 수학
<!-- toc:end -->

Tags: 바이브코딩, CS수학, 그래프이론, 알고리즘, 개발자수학
