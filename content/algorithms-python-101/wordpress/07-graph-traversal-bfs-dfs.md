---
title: "바이브코딩을 위한 Python 알고리즘 (7/10): 그래프 탐색 — BFS와 DFS"
series: algorithms-python-101
episode: 7
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- Python
- 알고리즘
- BFS
- DFS
seo_description: "그래프 탐색 BFS와 DFS를 Python으로 구현합니다. AI에게 최단 경로와 연결 요소 문제를 요청할 때 올바른 탐색 방식을 선택하는 법을 배웁니다."
---

# 바이브코딩을 위한 Python 알고리즘 (7/10): 그래프 탐색 — BFS와 DFS

이 글은 바이브코딩을 위한 Python 알고리즘 시리즈의 7번째 글입니다.

"친구 추천 시스템 만들어줘", "폴더 구조 탐색해줘", "최단 경로 찾아줘"와 같은 요청을 AI에게 할 때, 내부적으로 그래프 탐색이 사용됩니다. AI가 BFS를 줄지 DFS를 줄지는 문제 설명에 따라 달라집니다. 둘의 차이를 모르면 잘못된 알고리즘을 받아도 눈치채지 못합니다.

네트워크, 지도, 의존성 트리, 추천 시스템은 모두 결국 노드와 연결 관계의 문제로 환원됩니다. BFS와 DFS는 이런 구조를 탐색하는 두 가지 기본 전략입니다. 둘의 차이를 분명히 이해하면 최단 경로, 사이클 검사, 연결 요소 문제를 훨씬 쉽게 다룰 수 있습니다.

BFS는 가까운 이웃부터 층별로 탐색하고, DFS는 한 경로를 가능한 깊게 내려간 뒤 되돌아옵니다. 가중치 없는 최단 경로에는 BFS, 경로 존재 여부나 사이클 탐지에는 DFS가 적합합니다.

> BFS는 가까운 이웃을 층별로 탐색하고, DFS는 한 경로를 가능한 깊게 내려간 뒤 되돌아옵니다.

---

## 이 글에서 다룰 문제

- 그래프의 기본 개념과 Python에서의 표현 방식은 무엇일까요?
- BFS는 어떤 원리로 동작하고 언제 써야 할까요?
- DFS는 어떤 원리로 동작하고 언제 써야 할까요?
- AI에게 그래프 탐색 문제를 어떻게 설명해야 올바른 알고리즘을 받을 수 있을까요?
- 방문 처리를 잊었을 때 어떤 문제가 생길까요?

소셜 네트워크, 지도, 웹 링크, 의존성 그래프는 모두 그래프로 모델링됩니다. BFS와 DFS를 구분하여 AI에게 요청하면, 문제에 맞는 정확한 탐색 코드를 받을 수 있습니다.

## Before / After

**Before — AI에게 탐색 방식을 명시하지 않고 요청:**

```python
# "최단 경로 찾아줘" → AI가 DFS를 줄 수도 있음
# DFS는 최단 경로를 보장하지 않음!
def find_path_dfs(graph, start, end, visited=None):
    if visited is None:
        visited = set()
    if start == end:
        return [start]
    visited.add(start)
    for neighbor in graph[start]:
        if neighbor not in visited:
            path = find_path_dfs(graph, neighbor, end, visited)
            if path:
                return [start] + path
    return None
# 경로는 찾지만 최단 경로가 아닐 수 있음
```

**After — BFS로 최단 경로를 요청하며 정확하게 명시:**

```python
from collections import deque

# "가중치 없는 그래프에서 BFS로 최단 경로 찾아줘"
def bfs_shortest_path(graph, start, end):
    queue = deque([[start]])
    visited = {start}
    while queue:
        path = queue.popleft()
        node = path[-1]
        if node == end:
            return path
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])
    return None
# BFS는 가중치 없는 그래프에서 최단 경로를 보장
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 최단 경로에 DFS 사용 | 최단 경로 보장 안 됨 | 가중치 없는 최단 경로 = BFS |
| 방문 처리(visited) 누락 | 무한 루프 또는 중복 방문 | AI 코드에서 visited set 확인 필수 |
| 사이클 있는 그래프에서 방문 처리 없이 탐색 | 무한 루프 | 방문 처리를 항상 포함해달라고 요청 |
| BFS에 list 대신 list로 큐 사용 | O(n) pop 때문에 성능 저하 | collections.deque 사용 확인 |
| 방향 그래프와 무방향 그래프 혼동 | 잘못된 탐색 결과 | "방향 그래프야" 또는 "무방향 그래프야"를 명시 |

## AI 협업 팁

그래프 탐색 AI 프롬프트 패턴:

1. **그래프 종류 명시**: "방향 그래프", "무방향 그래프", "가중치 있는/없는"
2. **탐색 목적 명시**: "최단 경로", "연결 여부 확인", "사이클 탐지"
3. **표현 방식 명시**: "인접 리스트로 표현된 그래프에서"

예시 프롬프트:
> "무방향 무가중치 그래프에서 BFS로 시작 노드에서 도착 노드까지 최단 경로를 반환하는 함수를 만들어줘. 그래프는 인접 리스트로 표현돼. 경로가 없으면 빈 리스트를 반환해줘."

BFS vs DFS 선택 기준을 AI에게 물어보기:
> "이 문제에서 BFS와 DFS 중 어떤 게 더 적합해? 이유도 설명해줘."

## 운영 체크리스트

- [ ] 최단 경로 문제에 BFS를 사용하고 있는가?
- [ ] 방문 처리(visited set)가 포함되어 있는가?
- [ ] BFS에서 큐로 collections.deque를 사용하는가?
- [ ] 그래프가 방향/무방향, 가중치 있음/없음인지 AI에게 명시했는가?
- [ ] 사이클이 있는 그래프에서 무한 루프 가능성을 확인했는가?

## 처음 질문으로 돌아가기

"최단 경로 찾아줘"라고 AI에게 요청할 때, "가중치 없는 그래프에서 BFS로"라고 명시하는 것이 핵심입니다. BFS와 DFS의 차이, 그리고 각각 언제 쓰는지를 알면 AI에게 정확한 알고리즘을 요청하고 받은 코드를 검증할 수 있습니다.

## 정리

BFS는 가중치 없는 최단 경로와 층별 탐색에, DFS는 경로 존재 확인, 사이클 탐지, 위상 정렬에 적합합니다. Python에서 BFS는 `collections.deque`, DFS는 재귀 또는 스택으로 구현합니다. 바이브코딩에서는 그래프 종류와 탐색 목적을 AI에게 명시하는 것이 올바른 코드를 받는 핵심입니다.

다음 글에서는 최단 경로 알고리즘(다익스트라)을 다룹니다. 가중치가 있는 그래프에서 BFS만으로는 부족할 때 어떤 알고리즘을 써야 하는지 배웁니다.

## 참고 자료

### 공식 문서
- [Python collections.deque](https://docs.python.org/3/library/collections.html#collections.deque)
- [Python defaultdict](https://docs.python.org/3/library/collections.html#collections.defaultdict)

### 관련 시리즈
- [바이브코딩을 위한 Python 알고리즘 (6/10): 동적 계획법 기초](./06-dynamic-programming-basics.md)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Python 알고리즘 (1/10): 알고리즘이란 무엇인가?
- 바이브코딩을 위한 Python 알고리즘 (2/10): 시간 복잡도와 Big-O
- 바이브코딩을 위한 Python 알고리즘 (3/10): 선형 탐색과 이진 탐색
- 바이브코딩을 위한 Python 알고리즘 (4/10): 정렬 알고리즘
- 바이브코딩을 위한 Python 알고리즘 (5/10): 재귀와 분할 정복
- 바이브코딩을 위한 Python 알고리즘 (6/10): 동적 계획법 기초
- **바이브코딩을 위한 Python 알고리즘 (7/10): 그래프 탐색 — BFS와 DFS (현재 글)**
- 바이브코딩을 위한 Python 알고리즘 (8/10): 최단 경로 기초
- 바이브코딩을 위한 Python 알고리즘 (9/10): 그리디 알고리즘
- 바이브코딩을 위한 Python 알고리즘 (10/10): 코딩 테스트 문제 접근법
<!-- toc:end -->

Tags: 바이브코딩, Python, 알고리즘, BFS, DFS
