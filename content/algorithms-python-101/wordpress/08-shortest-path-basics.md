---
title: "바이브코딩을 위한 Python 알고리즘 (8/10): 최단 경로 기초"
series: algorithms-python-101
episode: 8
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- Python
- 알고리즘
- 최단경로
- 다익스트라
seo_description: "다익스트라 알고리즘을 Python heapq로 구현합니다. AI에게 가중치 그래프 최단 경로를 요청할 때 올바른 알고리즘과 조건을 명시하는 법을 배웁니다."
---

# 바이브코딩을 위한 Python 알고리즘 (8/10): 최단 경로 기초

이 글은 바이브코딩을 위한 Python 알고리즘 시리즈의 8번째 글입니다.

"지도에서 최단 경로 찾아줘"라고 AI에게 요청할 때, 도로마다 거리(가중치)가 다르다면 BFS로는 충분하지 않습니다. BFS는 가중치 없는 그래프에서만 최단 경로를 보장합니다. 가중치가 있으면 다익스트라 알고리즘이 필요합니다.

경로 계획, 네트워크 지연 최소화, 물류 최적화는 모두 같은 질문으로 모입니다. 여기서 저기까지 가는 가장 비용이 적은 경로는 무엇인가. 간선 가중치가 중요해지는 순간 BFS만으로는 부족하고, 다음에 볼 후보 경로를 비용 기준으로 관리해야 하며, 그 지점에서 다익스트라와 우선순위 큐(힙)가 힘을 발휘합니다.

바이브코딩에서 "최단 경로 찾아줘"라고 AI에게 요청할 때, "가중치 있는 그래프에서 다익스트라로"라고 명시해야 올바른 코드를 받을 수 있습니다. 그리고 받은 코드에서 음수 가중치가 있는지 반드시 확인해야 합니다.

> 다익스트라 알고리즘은 음수 가중치가 없는 그래프에서, 하나의 시작점으로부터 모든 노드까지의 최단 경로를 구합니다.

---

## 이 글에서 다룰 문제

- 가중치 그래프의 최단 경로 문제는 어떻게 정의할까요?
- 다익스트라 알고리즘은 어떤 원리로 동작할까요?
- Python의 heapq로 우선순위 큐를 어떻게 구현할까요?
- 음수 가중치가 있을 때는 어떤 알고리즘을 써야 할까요?
- AI에게 최단 경로를 요청할 때 어떤 조건을 명시해야 할까요?

내비게이션, 네트워크 라우팅, 물류 최적화는 모두 가중치 그래프의 최단 경로 문제입니다. 다익스트라는 이 문제를 효율적으로 푸는 가장 기본적인 도구입니다. 바이브코딩에서 이 알고리즘을 이해하면, AI가 준 라우팅 코드를 제대로 검토할 수 있습니다.

## Before / After

**Before — 가중치 그래프에서 BFS로 최단 경로 요청:**

```python
from collections import deque

# 가중치를 무시하고 BFS 사용 — 틀린 결과!
def bfs_weighted(graph, start, end):
    queue = deque([[start]])
    visited = {start}
    while queue:
        path = queue.popleft()
        node = path[-1]
        if node == end:
            return path
        for neighbor, weight in graph[node]:  # 가중치 무시
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])
    return None
# 가중치 있는 그래프에서 최단 경로가 아닌 최소 홉 경로 반환
```

**After — 다익스트라로 가중치 최단 경로 요청:**

```python
import heapq

# "가중치 있는 그래프에서 다익스트라로 최단 거리 찾아줘"
def dijkstra(graph, start):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    heap = [(0, start)]

    while heap:
        cost, node = heapq.heappop(heap)
        if cost > distances[node]:
            continue
        for neighbor, weight in graph[node]:
            new_cost = cost + weight
            if new_cost < distances[neighbor]:
                distances[neighbor] = new_cost
                heapq.heappush(heap, (new_cost, neighbor))

    return distances
# O((V+E) log V) — 음수 가중치 없는 그래프에서 최단 거리 보장
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 가중치 그래프에 BFS 사용 | 최소 홉이지 최소 비용이 아님 | 가중치 있으면 다익스트라 요청 |
| 음수 가중치에 다익스트라 사용 | 틀린 결과 반환 | 음수 가중치 확인 후 벨만-포드 요청 |
| heapq 대신 list 큐 사용 | O(V²)로 느려짐 | heapq 사용 확인 |
| 이미 처리된 노드 재처리 | 무한 루프 가능 | "cost > distances[node]" 체크 포함 확인 |
| 경로 복원 코드 누락 | 거리만 알고 실제 경로를 모름 | "경로도 반환해줘"라고 AI에게 요청 |

## AI 협업 팁

최단 경로 AI 프롬프트 패턴:

1. **가중치 여부 명시**: "각 간선에 이동 비용이 있어"
2. **음수 가중치 여부**: "모든 가중치는 양수야" 또는 "음수 가중치 있어"
3. **반환 형식 명시**: "최단 거리만" 또는 "경로도 함께"

예시 프롬프트:
> "가중치 있는 방향 그래프에서 다익스트라로 시작 노드에서 모든 노드까지의 최단 거리를 구해줘. 그래프는 인접 리스트로 표현되고 모든 가중치는 양수야. 거리 딕셔너리를 반환해줘."

음수 가중치가 있을 때:
> "이 그래프에 음수 가중치가 있어. 다익스트라 대신 벨만-포드를 사용해줘."

## 운영 체크리스트

- [ ] 가중치가 있는 그래프에서 BFS 대신 다익스트라를 사용하는가?
- [ ] 음수 가중치가 없는지 확인하고 다익스트라를 사용하는가?
- [ ] heapq를 사용하여 우선순위 큐를 구현하는가?
- [ ] 이미 처리된 노드를 건너뛰는 로직이 있는가?
- [ ] 경로 복원이 필요한 경우 predecessor 딕셔너리를 추가했는가?

## 처음 질문으로 돌아가기

"최단 경로 찾아줘"라고 AI에게 요청할 때, 가중치가 있다면 "음수 가중치 없는 가중치 그래프에서 다익스트라로"라고 명시해야 합니다. 이 조건 하나가 BFS와 다익스트라를 구분하고, 올바른 최단 경로 코드를 받는 핵심입니다.

## 정리

가중치 없는 그래프의 최단 경로는 BFS, 양수 가중치 그래프는 다익스트라입니다. Python에서 다익스트라는 `heapq`로 구현하며, 음수 가중치가 있으면 벨만-포드를 사용합니다. 바이브코딩에서는 그래프의 가중치 조건을 AI에게 명시하는 것이 올바른 알고리즘을 받는 핵심입니다.

다음 글에서는 그리디 알고리즘을 다룹니다. 매 단계에서 지역 최적 선택을 하는 전략이 언제 전체 최적해를 보장하는지, 그리고 언제 실패하는지를 배웁니다.

## 참고 자료

### 공식 문서
- [Python heapq 모듈](https://docs.python.org/3/library/heapq.html)
- [Python collections.defaultdict](https://docs.python.org/3/library/collections.html#collections.defaultdict)

### 관련 시리즈
- [바이브코딩을 위한 Python 알고리즘 (7/10): 그래프 탐색 — BFS와 DFS](./07-graph-traversal-bfs-dfs.md)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Python 알고리즘 (1/10): 알고리즘이란 무엇인가?
- 바이브코딩을 위한 Python 알고리즘 (2/10): 시간 복잡도와 Big-O
- 바이브코딩을 위한 Python 알고리즘 (3/10): 선형 탐색과 이진 탐색
- 바이브코딩을 위한 Python 알고리즘 (4/10): 정렬 알고리즘
- 바이브코딩을 위한 Python 알고리즘 (5/10): 재귀와 분할 정복
- 바이브코딩을 위한 Python 알고리즘 (6/10): 동적 계획법 기초
- 바이브코딩을 위한 Python 알고리즘 (7/10): 그래프 탐색 — BFS와 DFS
- **바이브코딩을 위한 Python 알고리즘 (8/10): 최단 경로 기초 (현재 글)**
- 바이브코딩을 위한 Python 알고리즘 (9/10): 그리디 알고리즘
- 바이브코딩을 위한 Python 알고리즘 (10/10): 코딩 테스트 문제 접근법
<!-- toc:end -->

Tags: 바이브코딩, Python, 알고리즘, 최단경로, 다익스트라
