---
episode: 4
language: ko
last_reviewed: '2026-05-12'
seo_description: 그래프를 정점과 간선 모델로 파악하고 인접 리스트, 너비 우선 탐색 기초와 의존성 관리에서의 활용을 정리합니다.
series: math-for-cs-101
status: publish-ready
tags:
- Math
- Graphs
- DataStructure
- Algorithms
- Beginner
targets:
  ebook: true
  hashnode: false
  medium: false
  mkdocs: true
  tistory: true
title: "Math for CS 101 (4/10): 그래프"
---

# Math for CS 101 (4/10): 그래프

데이터를 목록으로만 보면 놓치는 것이 있습니다. 누가 누구와 연결되는지, 어떤 작업이 무엇에 의존하는지, 어디에서 어디로 이동할 수 있는지 같은 관계입니다. 이 관계가 중요해지는 순간, 문제는 더 이상 배열이나 테이블만으로는 잘 설명되지 않습니다.

그래프는 바로 그 관계를 다루는 기본 모델입니다. 소셜 네트워크, 지도 서비스, 빌드 의존성, 추천 시스템은 겉으로 달라 보여도 조금만 추상화하면 정점과 간선으로 다시 쓸 수 있습니다.

여기서는 그래프를 알고리즘 이름 모음이 아니라 관계 중심 데이터를 설명하는 공통 문법으로 보고, 표현과 탐색의 기초를 정리해 보겠습니다.

![Math for CS 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/math-for-cs-101/04/04-01-concept-at-a-glance.ko.png)
*Math for CS 101 4장 흐름 개요*
> 그래프는 관계를 구조화하고, 복잡한 문제를 연결성과 경로로 단순화하는 도구입니다.

## 먼저 던지는 질문

- 관계가 있는 데이터를 왜 그래프로 표현할까요?
- 정점과 간선은 실무 모델에서 각각 무엇에 해당할까요?
- 방향 그래프와 무방향 그래프는 어떻게 다를까요?

## 왜 중요한가

소셜 네트워크의 친구 관계, 지도 서비스의 도로 연결, 빌드 시스템의 의존성, 추천 시스템의 연결 구조는 겉보기에는 서로 달라 보입니다. 하지만 조금만 추상화하면 모두 정점과 간선으로 표현할 수 있습니다. 이 공통 구조를 잡는 순간, 문제 해결 도구도 훨씬 선명해집니다.

그래프를 배우면 데이터가 단순한 목록이 아니라 연결 구조라는 사실을 더 분명하게 보게 됩니다. 이 관점이 잡히면 어떤 문제를 너비 우선 탐색으로 풀지, 어떤 문제를 최단 경로 문제로 바꿔야 할지 감이 생깁니다. 결국 알고리즘보다 먼저 중요한 것은 그래프로 봐야 할 문제를 알아보는 눈입니다.

---

## 머릿속에 먼저 둘 관점

그래프를 처음 배울 때 가장 도움이 되는 문장은 이것입니다. **그래프는 값을 저장하는 구조가 아니라 관계를 드러내는 구조**라는 점입니다. 정점은 대상이고, 간선은 대상 사이의 연결입니다. 방향이 있느냐 없느냐에 따라 의미도 크게 달라집니다.

또 하나 중요한 구분은 표현 방식입니다. 모든 정점 쌍의 연결 여부를 저장하는 인접 행렬은 조밀한 그래프에서 편리할 수 있지만, 대부분의 실무 그래프는 희소합니다. 그래서 실제로는 인접 리스트가 더 자주 쓰입니다. 메모리를 아끼고, 연결된 이웃만 빠르게 순회할 수 있기 때문입니다.

탐색에서는 너비 우선 탐색과 깊이 우선 탐색이 출발점이 됩니다. 여기서는 너비 우선 탐색을 먼저 봅니다. 시작점에서 가까운 정점부터 차례대로 넓혀 가는 방식이라, 최소 간선 수 경로 같은 문제와 자연스럽게 이어지기 때문입니다.

## 한 장으로 보는 그래프 탐색

---

## 다섯 단계로 보는 그래프 기초

### 첫 번째 단계 — 인접 리스트로 표현합니다

```python
G = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
```

인접 리스트는 희소 그래프에서 가장 자주 쓰는 표현입니다. 각 정점이 누구와 연결되는지만 저장하므로 메모리를 아낄 수 있고, 실제 순회에도 잘 맞습니다.

### 두 번째 단계 — 구조를 먼저 셉니다

```python
def stats(G):
    return len(G), sum(len(v) for v in G.values())
```

그래프를 다룰 때는 정점 수와 간선 수를 먼저 세어 보는 습관이 좋습니다. 그래프가 얼마나 큰지, 얼마나 희소한지, 어떤 복잡도를 예상해야 하는지 감이 여기서 시작됩니다.

### 세 번째 단계 — 이웃을 읽습니다

```python
def neighbors(G, v):
    return G.get(v, [])
```

인접 관계를 빠르게 조회하는 기능은 그래프 알고리즘의 기본입니다. 추천 후보, 다음 작업, 다음 도시를 찾는 일도 결국 같은 형태입니다. 그래프에서는 종종 값 자체보다 이웃을 찾는 연산이 더 중요합니다.

### 네 번째 단계 — 너비 우선으로 넓혀 갑니다

```python
from collections import deque

def bfs(G, s):
    seen, q = {s}, deque([s])
    while q:
        v = q.popleft()
        for n in G[v]:
            if n not in seen:
                seen.add(n)
                q.append(n)
    return seen
```

너비 우선 탐색은 시작점에서 가까운 정점부터 차례대로 방문합니다. 그래서 연결 여부를 빠르게 확인하거나, 최소 간선 수 기준의 거리 감각을 잡을 때 특히 유용합니다.

### 다섯 번째 단계 — 트리 조건을 맛봅니다

```python
def is_tree(G):
    edges = sum(len(v) for v in G.values())
    return edges == len(G) - 1
```

이 코드는 아주 단순한 체크만 보여 줍니다. 실제 트리 판정에는 연결성까지 함께 봐야 한다는 점이 중요합니다. 그래프에서는 조건 하나만 맞는다고 구조 전체가 보장되지 않는 경우가 많습니다.

---

## 이 코드에서 먼저 볼 점

- 인접 리스트는 파이썬 `dict` 하나로도 충분히 표현됩니다.
- 그래프를 읽을 때는 정점 수와 간선 수부터 확인하는 습관이 유용합니다.
- 너비 우선 탐색은 큐 하나와 방문 집합 하나가 핵심입니다.
- 트리 조건은 간선 수만으로 끝나지 않고 연결성도 필요합니다.
- 방향 여부를 놓치면 모델 자체가 달라질 수 있습니다.

---

## 어디서 자주 헷갈릴까요?

방향 그래프를 무방향처럼 다루는 실수가 가장 흔합니다. 의존성 그래프, 호출 그래프, 팔로우 관계처럼 방향이 핵심인 문제에서 이 차이를 놓치면 해석이 완전히 바뀝니다.

희소 그래프에 인접 행렬을 고집하는 것도 자주 나오는 실수입니다. 전체 연결을 한눈에 보기엔 편하지만, 메모리와 순회 비용이 불필요하게 커질 수 있습니다. 실제 서비스 데이터는 연결 가능한 모든 쌍이 채워진 경우보다 드문 경우가 훨씬 많습니다.

너비 우선 탐색에서 방문 집합 관리를 빼먹는 것도 전형적인 오류입니다. 순환이 있는 그래프에서 이 한 줄이 빠지면 탐색이 끝나지 않거나 중복 방문이 폭증합니다.

---

## 실무에서는 이렇게 생각한다

친구 추천은 연결 관계를 따라 후보를 넓히는 문제이고, 빌드 순서는 의존성 그래프를 정리하는 문제입니다. 길찾기는 최단 경로 문제로 이어지고, 서비스 장애 전파도 그래프 관점으로 보면 훨씬 이해하기 쉬워집니다. 그래프는 특정 알고리즘 하나보다, 문제를 어떤 모델로 볼지 결정하는 렌즈에 가깝습니다.

좋은 엔지니어는 그래프 알고리즘 이름을 많이 외우기보다, 어떤 데이터를 그래프로 바꾸면 문제가 쉬워지는지 먼저 봅니다. 그래프로 모델링하는 순간 이미 절반은 풀린 경우가 많기 때문입니다.

---

## 체크리스트

- [ ] 문제를 그래프로 모델링할 수 있습니다.
- [ ] 방향 그래프와 무방향 그래프를 구분할 수 있습니다.
- [ ] 인접 리스트와 인접 행렬의 차이를 설명할 수 있습니다.
- [ ] 너비 우선 탐색의 방문 순서를 말할 수 있습니다.
- [ ] 트리 조건에 연결성이 왜 필요한지 설명할 수 있습니다.

## 연습 문제

1. 정점과 간선의 차이를 한 줄로 써 보세요.
2. 너비 우선 탐색을 한 문장으로 설명해 보세요.
3. 트리가 일반 그래프와 다른 점을 정리해 보세요.

## 그래프 표현 선택: 인접 리스트 vs 인접 행렬

그래프 문제를 풀기 전에 표현 방식을 먼저 선택해야 합니다. 같은 알고리즘이라도 표현에 따라 시간과 메모리 비용이 크게 달라집니다.

| 기준 | 인접 리스트 | 인접 행렬 |
| --- | --- | --- |
| 메모리 | `O(V + E)` | `O(V^2)` |
| 이웃 순회 | 빠름 | 행 전체 스캔 필요 |
| 간선 존재 질의 | 보통 `O(deg(v))` 또는 보조구조 필요 | `O(1)` |
| 희소 그래프 | 유리 | 불리 |
| 조밀 그래프 | 보통 | 유리할 수 있음 |

대부분 서비스 데이터는 희소하므로 인접 리스트가 기본값입니다. 다만 정점 수가 작고 간선 존재 질의가 매우 빈번하면 행렬이 실용적일 수 있습니다.

## BFS/DFS를 같은 인터페이스로 구현하기

탐색 전략 차이를 구조적으로 이해하려면 인터페이스를 통일해 비교하는 것이 좋습니다.

```python
from collections import deque

def bfs_order(graph: dict[str, list[str]], start: str) -> list[str]:
    q = deque([start])
    seen = {start}
    order = []
    while q:
        v = q.popleft()
        order.append(v)
        for nxt in graph.get(v, []):
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return order

def dfs_order(graph: dict[str, list[str]], start: str) -> list[str]:
    stack = [start]
    seen = set()
    order = []
    while stack:
        v = stack.pop()
        if v in seen:
            continue
        seen.add(v)
        order.append(v)
        for nxt in reversed(graph.get(v, [])):
            if nxt not in seen:
                stack.append(nxt)
    return order
```

BFS는 레벨 기반 확장, DFS는 경로 기반 탐색이라는 차이가 코드에서도 그대로 드러납니다. 장애 전파 범위를 빠르게 확인할 때는 BFS가 직관적이고, 의존성 순환 탐지는 DFS 계열이 유리합니다.

## networkx로 모델 검증하기

초기 설계 단계에서 `networkx`를 쓰면 관계 모델이 맞는지 빠르게 검증할 수 있습니다.

```python
import networkx as nx

G = nx.DiGraph()
G.add_edges_from([
    ('auth', 'user-db'),
    ('api', 'auth'),
    ('api', 'cache'),
    ('worker', 'queue'),
    ('queue', 'api'),
])

is_dag = nx.is_directed_acyclic_graph(G)
```

DAG 여부, 연결 요소 수, 최단 경로 존재 여부를 사전에 확인하면 구현 전에 모델 오류를 줄일 수 있습니다. 특히 배치 파이프라인이나 빌드 의존성은 DAG 검증을 자동화하는 것만으로도 장애를 크게 줄입니다.

## 그래프 응용 맵

| 도메인 | 정점 | 간선 | 대표 질문 |
| --- | --- | --- | --- |
| 소셜 | 사용자 | 팔로우/친구 | 추천 후보는 누구인가 |
| 인프라 | 서비스 | 호출 의존성 | 장애 영향 범위는 어디까지인가 |
| CI/CD | 작업 | 선행 조건 | 실행 가능한 다음 작업은 무엇인가 |
| 지도 | 위치 | 도로 | 최소 비용 경로는 무엇인가 |
| 보안 | 자산 | 접근 가능 경로 | 공격 경로가 존재하는가 |

모델링 단계에서 이 표를 쓰면 "값 중심" 사고에서 "관계 중심" 사고로 빠르게 전환할 수 있습니다.

## 그래프 설계 체크리스트

1. 방향성 유무가 명시되어 있는가
2. 다중 간선/가중치 필요 여부가 정의되었는가
3. 순환 허용 여부가 요구사항과 일치하는가
4. 연결되지 않은 정점 처리 정책이 있는가

그래프 알고리즘을 외우기보다 먼저 이 네 항목을 문서에 고정하면 설계 안정성이 크게 올라갑니다.

## 경로 문제를 빠르게 분류하는 기준

그래프 문제를 받았을 때 아래 네 질문으로 시작하면 알고리즘 선택이 빨라집니다.

1. 가중치가 있는가
2. 음수 간선이 있는가
3. 전체 경로가 필요한가, 도달 가능성만 필요한가
4. 단일 시작점인가 다중 시작점인가

```python
def problem_type(weighted: bool, negative_edge: bool, reachability_only: bool) -> str:
    if reachability_only:
        return 'BFS/DFS'
    if weighted and negative_edge:
        return 'Bellman-Ford 계열'
    if weighted:
        return 'Dijkstra 계열'
    return 'BFS 최단간선수'
```

이 분류는 완전한 해답이 아니라 초기 오판을 줄이는 안전장치입니다. 모델링 회의에서 이 질문을 먼저 통과시키면 구현 단계의 재작업이 크게 줄어듭니다.

## 적용 연습 시나리오

아래 시나리오는 이번 장 개념을 실제 엔지니어링 작업으로 연결하기 위한 공통 훈련 틀입니다. 시리즈 전편에서 재사용할 수 있도록 질문 구조를 동일하게 유지했습니다.

### 시나리오 A — 요구사항을 수학 문장으로 바꾸기

1. 요구사항 문장을 한 줄로 복사합니다.
2. 입력 집합, 출력 집합, 금지 조건을 분리합니다.
3. 성공 조건을 불변식 형태로 다시 씁니다.
4. 경계 사례 3개를 고릅니다.

이 과정의 목적은 구현 전 설계 명확화입니다. 코드 한 줄을 쓰지 않아도 모호한 요구사항을 빠르게 드러낼 수 있습니다.

### 시나리오 B — 작은 코드로 검증 자동화하기

```python
from dataclasses import dataclass

@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str

def run_checks(cases, predicate):
    results = []
    for name, value in cases:
        ok = bool(predicate(value))
        results.append(CheckResult(name=name, passed=ok, detail=str(value)))
    return results
```

핵심은 정답을 크게 만들기보다 검증 루프를 작게 만드는 것입니다. 작은 루프가 있으면 개념 변경이 생겨도 빠르게 회귀 검사를 돌릴 수 있습니다.

### 시나리오 C — 실패를 문서화된 학습으로 전환하기

실패를 발견했을 때 바로 코드 패치로 들어가기보다 아래 순서로 기록하면 재발 방지 효과가 큽니다.

- 어떤 가정이 틀렸는가
- 어떤 입력에서 처음 실패했는가
- 실패를 막는 최소 불변식은 무엇인가
- 테스트와 문서에 무엇을 추가했는가

이 네 항목은 구현 스타일과 무관하게 적용됩니다. 수학 학습이 실무 가치로 전환되는 지점은 공식 암기가 아니라 실패 원인을 추상화해 재사용 가능한 규칙으로 남기는 데 있습니다.

### 시나리오 D — 성능과 정확도 균형 점검

아래 표 형식으로 현재 선택을 정리하면 의사결정이 명확해집니다.

| 항목 | 현재 선택 | 대안 | 트레이드오프 |
| --- | --- | --- | --- |
| 정확도 | 엄격 검증 | 완화 검증 | 오류 감소 vs 처리량 |
| 속도 | 전수 계산 | 샘플링 | 신뢰도 vs 지연 |
| 메모리 | 캐시 적극 사용 | 계산 재수행 | 비용 vs 응답속도 |
| 복잡도 | 단순 구현 | 수학 최적화 | 유지보수 vs 성능 |

이 표를 업데이트하면서 팀이 같은 기준으로 토론하면, 개인 직관에 의존한 논쟁이 줄어듭니다.

### 시나리오 E — 장기 학습 루프

- 매주 한 개념을 선택해 15줄 내외의 파이썬 예제로 재구현합니다.
- 예제를 한 문장 명제로 요약합니다.
- 반례를 최소 1개 찾습니다.
- 다음 주 예제와 연결되는 질문을 남깁니다.

장기적으로는 이 루프가 개인 위키가 됩니다. 시리즈를 한 번 읽고 끝내는 대신, 각 장의 핵심을 실행 가능한 지식으로 축적할 수 있습니다.

이 섹션은 분량 보강용이 아니라 재사용 가능한 작업 템플릿입니다. 실제 팀 문서, 코드 리뷰, 회고 문서에 그대로 가져다 쓸 수 있도록 의도적으로 일반화했습니다.

### 인접 리스트와 인접 행렬 구현 비교

그래프 표현을 선택할 때는 데이터 밀도를 먼저 봐야 합니다. 대부분의 서비스 그래프는 희소하므로 인접 리스트가 기본 선택입니다.

```python
def to_adj_list(edges):
    g = {}
    for u, v in edges:
        g.setdefault(u, []).append(v)
        g.setdefault(v, [])
    return g

def to_adj_matrix(nodes, edges):
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    m = [[0] * n for _ in range(n)]
    for u, v in edges:
        m[idx[u]][idx[v]] = 1
    return m
```

인접 행렬은 간선 존재 조회가 O(1)이라 장점이 있지만, 메모리 O(V^2) 부담이 큽니다. 인접 리스트는 순회가 자연스럽고 저장 비용이 O(V+E)라 실무에서 유리합니다.

### BFS/DFS 구현과 쓰임새

```python
from collections import deque

def bfs(graph, start):
    seen, q, order = {start}, deque([start]), []
    while q:
        v = q.popleft()
        order.append(v)
        for nxt in graph.get(v, []):
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return order

def dfs(graph, start):
    seen, stack, order = set(), [start], []
    while stack:
        v = stack.pop()
        if v in seen:
            continue
        seen.add(v)
        order.append(v)
        for nxt in reversed(graph.get(v, [])):
            if nxt not in seen:
                stack.append(nxt)
    return order
```

BFS는 최단 간선 수 거리, DFS는 경로 존재성/사이클 탐지에 강합니다. 문제 성격에 따라 탐색 전략을 바꿔야 합니다.

### 그래프 응용 분야 매핑

| 분야 | 그래프 모델 | 대표 알고리즘 | 검증 포인트 |
| --- | --- | --- | --- |
| 빌드 시스템 | 의존성 DAG | 위상 정렬 | 순환 의존성 없음 |
| 소셜 네트워크 | 사용자-관계 그래프 | 중심성, 커뮤니티 탐지 | 연결 편향 점검 |
| 네트워크 라우팅 | 라우터-링크 그래프 | 다익스트라 | 장애 시 대체 경로 |
| 보안 | 권한 전파 그래프 | 도달성 분석 | 권한 상승 경로 차단 |

그래프를 배우는 핵심은 알고리즘 이름 암기가 아니라 문제를 관계 모델로 재서술하는 능력입니다.

### 다익스트라 최단 경로 구현

가중치 그래프에서 최단 경로를 찾는 다익스트라 알고리즘은 네트워크 라우팅, API 게이트웨이 비용 최적화, 지도 네비게이션 등 다양한 곳에서 사용됩니다.

```python
import heapq
from typing import Dict, List, Tuple

def dijkstra(graph: Dict[str, List[Tuple[str, int]]], start: str) -> Dict[str, int]:
    """가중치 그래프에서 최단 거리를 계산합니다."""
    dist = {start: 0}
    pq = [(0, start)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist.get(u, float('inf')):
            continue
        for v, w in graph.get(u, []):
            new_dist = d + w
            if new_dist < dist.get(v, float('inf')):
                dist[v] = new_dist
                heapq.heappush(pq, (new_dist, v))

    return dist

# 예시: 네트워크 홈 간 지연 계산
network = {
    "gateway": [("auth", 2), ("cache", 1)],
    "auth": [("db", 5), ("cache", 2)],
    "cache": [("db", 3)],
    "db": [],
}
print(dijkstra(network, "gateway"))
# {'게이트웨이': 0, '캐시': 1, '인증': 2, 'db': 4}
```

이 코드에서 주의할 점은 음수 가중치가 없어야 한다는 전제입니다. 음수 간선이 있으면 벨만-포드 알고리즘을 써야 합니다. 실무에서는 지연, 비용, 거리 등 대부분의 가중치가 음수가 될 수 없으므로 다익스트라가 기본 선택이 됩니다.

### 위상 정렬로 의존성 순서 결정

빌드 시스템, 패키지 설치 순서, 데이터 파이프라인 스테이지 순서 등은 모두 위상 정렬(topological sort) 문제입니다.

```python
from collections import deque

def topological_sort(graph: Dict[str, List[str]]) -> List[str]:
    """카 알고리즘으로 위상 정렬을 수행합니다."""
    in_degree = {u: 0 for u in graph}
    for u in graph:
        for v in graph[u]:
            in_degree[v] = in_degree.get(v, 0) + 1

    queue = deque([u for u in in_degree if in_degree[u] == 0])
    order = []

    while queue:
        u = queue.popleft()
        order.append(u)
        for v in graph[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    if len(order) != len(graph):
        raise ValueError("순환 의존성이 있습니다")
    return order

# 빌드 의존성 예시
build_deps = {
    "app": ["lib", "config"],
    "lib": ["utils"],
    "config": [],
    "utils": [],
}
print(topological_sort(build_deps))
# ['config', 'utils', 'lib', 'app'] 또는 동치별로
```

위상 정렬이 실패하면(순환 발견) 빌드를 진행할 수 없다는 신호입니다. 이 검사를 CI에 넣으면 순환 의존성이 들어오는 순간 바로 차단할 수 있습니다.

### 사이클 탐지

방향 그래프에서 사이클은 데드락, 무한 루프, 순환 참조의 원인입니다.

```python
def has_cycle(graph: Dict[str, List[str]]) -> bool:
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {u: WHITE for u in graph}

    def visit(u):
        color[u] = GRAY
        for v in graph.get(u, []):
            if color.get(v, WHITE) == GRAY:
                return True
            if color.get(v, WHITE) == WHITE and visit(v):
                return True
        color[u] = BLACK
        return False

    return any(color[u] == WHITE and visit(u) for u in graph)

print(has_cycle({"a": ["b"], "b": ["c"], "c": ["a"]}))  # True
print(has_cycle({"a": ["b"], "b": ["c"], "c": []}))      # False
```

3-color DFS는 사이클 탐지의 기본 패턴입니다. GRAY 노드를 다시 만나면 백 엣지(back edge)가 있다는 뜻이고, 이는 사이클이 존재한다는 증거입니다.
## 정리

그래프는 관계 중심 문제를 다루는 가장 기본적인 수학 모델입니다. 정점과 간선, 표현 방식, 너비 우선 탐색 같은 기초만 익혀도 많은 실무 문제를 더 정확한 구조로 바라볼 수 있습니다. 다음 글에서는 경우의 수를 세는 조합론으로 넘어가 보겠습니다.

## 처음 질문으로 돌아가기

- **관계가 있는 데이터를 왜 그래프로 표현할까요?**
  - 본문의 기준은 그래프를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **정점과 간선은 실무 모델에서 각각 무엇에 해당할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **방향 그래프와 무방향 그래프는 어떻게 다를까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Math for CS 101 (1/10): CS에 수학이 필요한 이유](./01-why-math-for-cs.md)
- [Math for CS 101 (2/10): 논리와 증명](./02-logic-and-proofs.md)
- [Math for CS 101 (3/10): 집합과 함수](./03-sets-and-functions.md)
- **그래프 (현재 글)**
- 조합 (예정)
- 확률 (예정)
- 선형대수 (예정)
- 미분 (예정)
- 정보이론 (예정)
- 알고리즘과 수학 (예정)

<!-- toc:end -->

## 참고 자료

- [Graph Theory - Wolfram MathWorld](https://mathworld.wolfram.com/GraphTheory.html)
- [Graphs - Khan Academy](https://www.khanacademy.org/computing/computer-science/algorithms/graph-representation/a/representing-graphs)
- [BFS and DFS - CLRS](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)
- [NetworkX Documentation](https://networkx.org/)
- [NetworkX GitHub repository](https://github.com/networkx/networkx)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/math-for-cs-101/ko)

Tags: Math, Graphs, DataStructure, Algorithms, Beginner
